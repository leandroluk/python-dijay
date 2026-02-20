"""Global container instance and module-level shortcuts."""

from .container import Container

_global = Container()

injectable = _global.injectable
"""Shortcut for :meth:`Container.injectable` on the global container."""

register = _global.register
"""Shortcut for :meth:`Container.register` on the global container."""

resolve = _global.resolve
"""Shortcut for :meth:`Container.resolve` on the global container."""

on_bootstrap = _global.on_bootstrap
"""Shortcut for :meth:`Container.on_bootstrap` on the global container."""

on_shutdown = _global.on_shutdown
"""Shortcut for :meth:`Container.on_shutdown` on the global container."""


def instance() -> Container:
    """Create and return a new, independent :class:`Container`.

    Use this when you need isolation from the global container,
    for example in tests or multi-tenant scenarios.
    """
    return Container()
