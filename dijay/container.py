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

SINGLETON = "singleton"
"""Scope that creates a single instance shared across all resolutions."""

TRANSIENT = "transient"
"""Scope that creates a new instance on every resolution."""

REQUEST = "request"
"""Scope that creates one instance per request ID, shared within the same request."""


class Inject:
    """Marker used in ``Annotated`` type hints to specify a custom injection token.

    When a parameter is annotated with ``Annotated[SomeType, Inject(token)]``,
    the container resolves ``token`` instead of ``SomeType``.

    Example::

        async def handler(
            svc: Annotated[MyService, Inject("my_service_token")]
        ) -> None: ...
    """

    def __init__(self, token: Any) -> None:
        """
        Args:
            token: The token (class, string, or any hashable) that the container
                   should resolve for the annotated parameter.
        """
        self.token = token


class Container:
    """Async dependency injection container.

    Supports three lifetime scopes — ``singleton``, ``transient``, and ``request`` —
    and resolves dependencies automatically by inspecting type hints.

    Typical usage::

        container = Container()

        @container.inject(scope=SINGLETON)
        class DatabaseConnection:
            ...

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
        self._resolving: set[Any] = set()

    def injectable(
        self,
        token: Any | None = None,
        scope: str = SINGLETON,
    ) -> Callable[[Any], Any]:
        """Decorator that registers a class or factory function as a provider.

        Args:
            token: The token under which the provider is registered. Defaults to
                   the decorated class itself, or the return type annotation of a
                   factory function when ``token`` is ``None``.
            scope: Lifetime scope of the resolved instance. One of ``SINGLETON``
                   (default), ``TRANSIENT``, or ``REQUEST``.

        Returns:
            The original class or function, unchanged, so the decorator is
            transparent to the rest of the codebase.

        Example::

            @container.inject(scope=TRANSIENT)
            class EmailSender:
                ...
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
            return provider

        return decorator

    def on_bootstrap(self, fn: Callable[..., Any]) -> Callable[..., Any]:
        """Register a hook to run when the container starts up.

        Hooks are executed in registration order during :meth:`bootstrap`.
        All dependencies of the hook function are resolved automatically.

        Args:
            fn: An async or sync callable whose parameters will be injected.

        Returns:
            The original callable, unchanged.
        """
        self._bootstrap_hooks.append(fn)
        return fn

    def on_shutdown(self, fn: Callable[..., Any]) -> Callable[..., Any]:
        """Register a hook to run when the container shuts down.

        Hooks are executed in registration order during :meth:`shutdown`,
        before the singleton and request caches are cleared.

        Args:
            fn: An async or sync callable whose parameters will be injected.

        Returns:
            The original callable, unchanged.
        """
        self._shutdown_hooks.append(fn)
        return fn

    async def bootstrap(self) -> None:
        """Execute all registered bootstrap hooks in order.

        Called automatically by :meth:`__aenter__` when using the container
        as an async context manager.
        """
        for hook in self._bootstrap_hooks:
            await self.call(hook)

    async def shutdown(self) -> None:
        """Execute all registered shutdown hooks and clear internal caches.

        Called automatically by :meth:`__aexit__` when the ``async with`` block exits.
        After all hooks run, singleton and request-scoped instances are discarded.
        """
        for hook in self._shutdown_hooks:
            await self.call(hook)
        self._singletons.clear()
        self._request_store.clear()

    async def __aenter__(self) -> Self:
        """Start the container and run bootstrap hooks.

        Returns:
            The container itself, allowing ``async with container as c:`` syntax.
        """
        await self.bootstrap()
        return self

    async def __aexit__(self, *args: Any) -> None:
        """Shut down the container and run cleanup hooks."""
        await self.shutdown()

    async def resolve[T](self, token: type[T] | Any, id: str | None = None) -> T:
        """Resolve a dependency by token, respecting its registered scope.

        - **Singleton**: the same instance is returned on every call.
        - **Transient**: a new instance is created on every call.
        - **Request**: one instance per ``id``; a new one is created when ``id``
          changes or is ``None``.

        Unregistered classes are instantiated directly with their own
        dependencies resolved recursively.

        Args:
            token: The type or key to resolve.
            id:    An optional request identifier used for ``REQUEST``-scoped
                   dependencies.

        Returns:
            A fully constructed instance of type ``T``.

        Raises:
            RuntimeError: If a circular dependency is detected or the token is
                          not registered and cannot be auto-resolved.
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
        self, target: Callable[..., Any], id: str | None = None, **kwargs: Any
    ) -> Any:
        """Invoke a callable with its dependencies resolved and injected.

        Inspects the type hints of ``target`` (or ``target.__init__`` for classes),
        resolves each parameter from the container, and calls the target.
        Parameters already present in ``kwargs`` are not overridden.

        Optional parameters (``X | None``) that cannot be resolved are silently
        set to ``None`` instead of raising an error.

        Args:
            target: The class or callable to invoke.
            id:     Request identifier forwarded to :meth:`resolve` for
                    ``REQUEST``-scoped dependencies.
            **kwargs: Pre-supplied arguments that bypass resolution.

        Returns:
            The return value of ``target(**kwargs)``, awaited if it is a coroutine.
        """
        func = target.__init__ if inspect.isclass(target) else target
        hints = get_type_hints(func, include_extras=True)

        for name, hint in hints.items():
            if name == "return" or name in kwargs:
                continue

            token = self._extract_token(hint)
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
        """Extract the injection token from a type hint.

        If the hint is ``Annotated[T, Inject(token), ...]``, the first
        :class:`Inject` metadata value is returned as the token.
        If the hint is plain ``Annotated[T, ...]`` with no :class:`Inject`,
        the inner type ``T`` is returned.
        For all other hints, the hint itself is returned unchanged.

        Args:
            hint: A type annotation, possibly wrapped in ``Annotated``.

        Returns:
            The resolved token to pass to :meth:`resolve`.
        """
        if get_origin(hint) is Annotated:
            for arg in get_args(hint)[1:]:
                if isinstance(arg, Inject):
                    return arg.token
            return get_args(hint)[0]
        return hint


_global = Container()

injectable = _global.injectable
"""Shortcut for :meth:`Container.injectable` on the global container."""

resolve = _global.resolve
"""Shortcut for :meth:`Container.resolve` on the global container."""

on_bootstrap = _global.on_bootstrap
"""Shortcut for :meth:`Container.on_bootstrap` on the global container."""

on_shutdown = _global.on_shutdown
"""Shortcut for :meth:`Container.on_shutdown` on the global container."""


def instance() -> Container:
    """Create and return a new, independent :class:`Container` instance.

    Use this when you need a container that is isolated from the global one,
    for example in tests or multi-tenant scenarios.

    Returns:
        A fresh :class:`Container` with no registrations.
    """
    return Container()
