from __future__ import annotations

import asyncio
import inspect
from collections.abc import Callable
from typing import (
    Annotated,
    Any,
    Self,
    Union,
    cast,
    get_args,
    get_origin,
    get_type_hints,
)

from .inject import Inject
from .provider import REQUEST, SINGLETON


class Container:
    """Async dependency injection container.

    Supports three lifetime scopes — ``singleton``, ``transient``, and
    ``request`` — and resolves dependencies automatically by inspecting
    type hints.

    Typical usage::

        container = Container()

        @container.injectable(scope=SINGLETON)
        class DatabaseConnection: ...

        async with container:
            db = await container.resolve(DatabaseConnection)
    """

    def __init__(self) -> None:
        """Initialise an empty container with no registered providers."""
        self._registry: dict[Any, dict[str, Any]] = {}
        self._singletons: dict[Any, Any] = {}
        self._request_store: dict[str, dict[Any, Any]] = {}
        self._bootstrap_hooks: list[Callable[..., Any]] = []
        self._shutdown_hooks: list[Callable[..., Any]] = []
        self._bootstrap_methods: dict[Any, list[str]] = {}
        self._shutdown_methods: dict[Any, list[str]] = {}
        self._resolving: set[Any] = set()

    def injectable(
        self,
        token: Any | None = None,
        scope: str = SINGLETON,
    ) -> Callable[[Any], Any]:
        """Decorator that registers a class or factory as a provider.

        Args:
            token: Token under which the provider is registered.
                   Defaults to the class itself or factory return type.
            scope: Lifetime scope (``SINGLETON``, ``TRANSIENT``,
                   or ``REQUEST``).

        Returns:
            The original class or function, unchanged.

        Example::

            @container.injectable(scope=TRANSIENT)
            class EmailSender: ...
        """

        def decorator(provider: Any) -> Any:
            target_token = token or (
                provider
                if inspect.isclass(provider)
                else get_type_hints(provider).get("return", provider)
            )
            self._registry[target_token] = {
                "provider": provider,
                "scope": scope,
                "is_class": inspect.isclass(provider),
            }

            if inspect.isclass(provider):
                for name, value in inspect.getmembers(provider):
                    if getattr(value, "__dijay_bootstrap__", False):
                        self._bootstrap_methods.setdefault(target_token, []).append(
                            name
                        )
                    if getattr(value, "__dijay_shutdown__", False):
                        self._shutdown_methods.setdefault(target_token, []).append(name)

            provider.__dijay_token__ = target_token
            provider.__dijay_scope__ = scope
            return provider

        return decorator

    def register(
        self,
        token: Any,
        provider: Any,
        scope: str = SINGLETON,
    ) -> None:
        """Explicitly bind a provider to a token.

        Unlike :meth:`injectable`, ``register`` lets you bind any
        existing class or callable to a token at runtime.

        Args:
            token:    The type or key to resolve.
            provider: A class or callable to instantiate/call.
            scope:    Lifetime scope (defaults to ``SINGLETON``).

        Example::

            container.register(Database, FakeDatabase)
        """
        self._registry[token] = {
            "provider": provider,
            "scope": scope,
            "is_class": inspect.isclass(provider),
        }

        if inspect.isclass(provider):
            for name, value in inspect.getmembers(provider):
                if getattr(value, "__dijay_bootstrap__", False):
                    self._bootstrap_methods.setdefault(token, []).append(name)
                if getattr(value, "__dijay_shutdown__", False):
                    self._shutdown_methods.setdefault(token, []).append(name)

    def on_bootstrap(self, fn: Callable[..., Any]) -> Callable[..., Any]:
        """Register a hook to run during :meth:`bootstrap`.

        Args:
            fn: Async or sync callable whose parameters will be
                injected.

        Returns:
            The original callable, unchanged.
        """
        self._bootstrap_hooks.append(fn)
        setattr(fn, "__dijay_bootstrap__", True)
        return fn

    def on_shutdown(self, fn: Callable[..., Any]) -> Callable[..., Any]:
        """Register a hook to run during :meth:`shutdown`.

        Args:
            fn: Async or sync callable whose parameters will be
                injected.

        Returns:
            The original callable, unchanged.
        """
        self._shutdown_hooks.append(fn)
        setattr(fn, "__dijay_shutdown__", True)
        return fn

    async def bootstrap(self) -> None:
        """Execute all registered bootstrap hooks in order."""
        for hook in self._bootstrap_hooks:
            # Skip if it's a method that will be called via _bootstrap_methods.
            # We detect methods by checking if they belong to a class.
            if (
                inspect.isroutine(hook)
                and "." in hook.__qualname__
                and "<locals>" not in hook.__qualname__
            ):
                continue
            await self.call(hook)

        for token, methods in self._bootstrap_methods.items():
            instance_obj = await self.resolve(token)
            for method_name in methods:
                await self.call(getattr(instance_obj, method_name))

    async def shutdown(self) -> None:
        """Execute all shutdown hooks and clear internal caches."""
        for hook in self._shutdown_hooks:
            if (
                inspect.isroutine(hook)
                and "." in hook.__qualname__
                and "<locals>" not in hook.__qualname__
            ):
                continue
            await self.call(hook)

        for token, methods in self._shutdown_methods.items():
            # Only shutdown singletons that were actually created
            if token in self._singletons:
                instance_obj = self._singletons[token]
                for method_name in methods:
                    await self.call(getattr(instance_obj, method_name))

        self._singletons.clear()
        self._request_store.clear()

    async def __aenter__(self) -> Self:
        """Start the container and run bootstrap hooks."""
        await self.bootstrap()
        return self

    async def __aexit__(self, *args: Any) -> None:
        """Shut down the container and run cleanup hooks."""
        await self.shutdown()

    async def resolve[T](self, token: type[T] | Any, id: str | None = None) -> T:
        """Resolve a dependency by token, respecting its scope.

        Args:
            token: The type or key to resolve.
            id:    Optional request identifier for ``REQUEST``
                   scoped dependencies.

        Returns:
            A fully constructed instance of type ``T``.

        Raises:
            RuntimeError: On circular dependency or unregistered
                          token.
        """
        if token in self._resolving:
            raise RuntimeError(f"Circular dependency: {token}")

        self._resolving.add(token)
        try:
            config = self._registry.get(token)
            if not config:
                if inspect.isclass(token):
                    return cast(T, await self.call(token, id=id))
                raise RuntimeError(f"Token {token} não registrado.")

            scope = config["scope"]
            if scope == SINGLETON and token in self._singletons:
                return cast(T, self._singletons[token])

            if scope == REQUEST and id and token in self._request_store.get(id, {}):
                return cast(T, self._request_store[id][token])

            instance_obj = await self.call(config["provider"], id=id)

            if scope == SINGLETON:
                self._singletons[token] = instance_obj
            elif scope == REQUEST and id:
                self._request_store.setdefault(id, {})[token] = instance_obj

            return cast(T, instance_obj)
        finally:
            self._resolving.remove(token)

    async def call(
        self,
        target: Callable[..., Any],
        id: str | None = None,
        **kwargs: Any,
    ) -> Any:
        """Invoke a callable with dependencies resolved and injected.

        Args:
            target: The class or callable to invoke.
            id:     Request identifier for ``REQUEST`` scoped deps.
            **kwargs: Pre-supplied arguments that bypass resolution.

        Returns:
            The return value of ``target``, awaited if coroutine.
        """
        func = target.__init__ if inspect.isclass(target) else target
        hints = get_type_hints(func, include_extras=True)

        for name, hint in hints.items():
            if name == "return" or name in kwargs:
                continue

            token = self._extract_token(hint)
            if token is Any:
                continue

            origin = get_origin(hint)
            args = get_args(hint)
            is_opt = origin is Union and type(None) in args

            try:
                kwargs[name] = await self.resolve(token, id=id)
            except RuntimeError:
                if not is_opt:
                    raise
                kwargs[name] = None

        res = target(**kwargs)
        return await res if asyncio.iscoroutine(res) else res

    def _extract_token(self, hint: Any) -> Any:
        """Extract the injection token from a type hint."""
        if get_origin(hint) is Annotated:
            for arg in get_args(hint)[1:]:
                if isinstance(arg, Inject):
                    return arg.token
            return get_args(hint)[0]
        return hint

    @classmethod
    def from_module(cls, mod: Any) -> Container:
        """Create a container from a module hierarchy."""
        from .module import _resolve_module

        c = cls()
        _resolve_module(c, mod)
        return c
