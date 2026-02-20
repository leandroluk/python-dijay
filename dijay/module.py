import inspect
from collections.abc import Callable
from typing import Any, TypedDict

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


def module(
    providers: list[Any] = [],
    imports: list[Any] = [],
    exports: list[Any] = [],
    globals: bool = False,
) -> Callable[[Any], Any]:
    """Decorator that marks a class as a Module.

    Modules organize providers and can be imported by other modules.

    Args:
        providers: Providers to register within this module.
        imports: Imported modules that export providers.
        exports: Providers to export to importing modules.
        globals: If ``True``, exports are available globally.
    """

    def decorator(cls: Any) -> Any:
        cls.__module_metadata__ = {
            "providers": providers,
            "imports": imports,
            "exports": exports,
            "globals": globals,
        }
        return cls

    return decorator


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
