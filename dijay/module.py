import inspect
from collections.abc import Callable
from typing import Any, TypedDict, cast

from .container import Container
from .provider import SINGLETON, Provide


class DynamicModule(TypedDict, total=False):
    """Structure returned by static methods (e.g. ``for_root``) to
    configure dynamic modules.
    """

    module: Any
    providers: list[Any]
    imports: list[Any]
    exports: list[Any]
    globals: bool


class module:  # noqa: N801
    """Decorator that marks a class as a Module.

    Modules organize providers and can be imported by other modules.

    Args:
        providers: Providers to register within this module.
        imports: Imported modules that export providers.
        exports: Providers to export to importing modules.
        globals: If ``True``, exports are available globally.
    """

    def __init__(
        self,
        providers: list[Any] | None = None,
        imports: list[Any] | None = None,
        exports: list[Any] | None = None,
        globals: bool = False,
    ):
        self.metadata = {
            "providers": providers or [],
            "imports": imports or [],
            "exports": exports or [],
            "globals": globals,
        }

    def __call__(self, cls: Any) -> Any:
        cls.__module_metadata__ = self.metadata
        return cls

    @staticmethod
    def on_bootstrap(
        fn: Callable[..., Any] | Container | None = None,
        /,
        container: Container | None = None,
    ) -> Any:
        """Decorator to register a bootstrap hook.

        Can be used with or without a container::

            @module.on_bootstrap
            def boot(): ...

            @module.on_bootstrap(container=c)
            def boot(): ...
        """
        from .container import Container
        from .decorators import on_bootstrap as _global_on_bootstrap

        def _make_decorator(
            _container: Container | None,
        ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
            def decorator(f: Callable[..., Any]) -> Callable[..., Any]:
                if _container is not None:
                    return _container.on_bootstrap(f)
                return cast(Callable[..., Any], _global_on_bootstrap(f))

            return decorator

        if isinstance(fn, Container):
            return _make_decorator(fn)
        if container is not None:
            return _make_decorator(container)
        if callable(fn):
            return _make_decorator(None)(fn)
        return _make_decorator(None)

    @staticmethod
    def on_shutdown(
        fn: Callable[..., Any] | Container | None = None,
        /,
        container: Container | None = None,
    ) -> Any:
        """Decorator to register a shutdown hook.

        Can be used with or without a container::

            @module.on_shutdown
            def shut(): ...

            @module.on_shutdown(container=c)
            def shut(): ...
        """
        from .container import Container
        from .decorators import on_shutdown as _global_on_shutdown

        def _make_decorator(
            _container: Container | None,
        ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
            def decorator(f: Callable[..., Any]) -> Callable[..., Any]:
                if _container is not None:
                    return _container.on_shutdown(f)
                return cast(Callable[..., Any], _global_on_shutdown(f))

            return decorator

        if isinstance(fn, Container):
            return _make_decorator(fn)
        if container is not None:
            return _make_decorator(container)
        if callable(fn):
            return _make_decorator(None)(fn)
        return _make_decorator(None)


def _is_dynamic_module(obj: Any) -> bool:
    return isinstance(obj, dict) and "module" in obj


def _register_provider(container: Container, provider: Any) -> None:
    """Register a single provider entry into the container.

    Handles three cases:

    - ``Provide`` dataclass with ``use_value``, ``use_class``
      or ``use_factory``.
    - Class decorated with ``@injectable(token)`` carrying
      ``__dijay_token__`` metadata.
    - Plain class (registered as its own token).
    """
    if isinstance(provider, Provide):
        if provider.use_value is not None:
            val = provider.use_value
            container.register(
                provider.token,
                lambda v=val: v,
                scope=provider.scope,
            )
        elif provider.use_factory is not None:
            container.register(
                provider.token,
                provider.use_factory,
                scope=provider.scope,
            )
        elif provider.use_class is not None:
            container.register(
                provider.token,
                provider.use_class,
                scope=provider.scope,
            )
        return

    token = getattr(provider, "__dijay_token__", provider)
    scope = getattr(provider, "__dijay_scope__", SINGLETON)

    if inspect.isclass(provider):
        container.register(token, provider, scope=scope)


def _resolve_module(container: Container, mod: Any) -> None:
    """Recursively resolve a module hierarchy and register
    all providers.
    """
    if _is_dynamic_module(mod):
        for imp in mod.get("imports", []):
            _resolve_module(container, imp)
        for provider in mod.get("providers", []):
            _register_provider(container, provider)
        mod = mod["module"]

    if not hasattr(mod, "__module_metadata__"):
        return

    metadata = mod.__module_metadata__

    for imp in metadata["imports"]:
        _resolve_module(container, imp)

    for provider in metadata["providers"]:
        _register_provider(container, provider)
