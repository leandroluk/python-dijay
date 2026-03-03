"""Global container instance and module-level shortcuts."""

from .container import Container

_global = Container()

injectable = _global.injectable
"""Shortcut for :meth:`Container.injectable` on the global container."""

register = _global.register
"""Shortcut for :meth:`Container.register` on the global container."""

resolve = _global.resolve
"""Shortcut for :meth:`Container.resolve` on the global container."""


def on_bootstrap(fn=None, /, container=None):
    """Register a bootstrap hook on the given container (or global).

    Can be used as::

        @on_bootstrap
        def boot(): ...

        @on_bootstrap(container=c)
        def boot(): ...
    """
    _container = fn if isinstance(fn, Container) else (container or _global)

    def _decorator(f):
        return _container.on_bootstrap(f)

    if callable(fn) and not isinstance(fn, Container):
        return _decorator(fn)
    return _decorator


def on_shutdown(fn=None, /, container=None):
    """Register a shutdown hook on the given container (or global).

    Can be used as::

        @on_shutdown
        def shut(): ...

        @on_shutdown(container=c)
        def shut(): ...
    """
    _container = fn if isinstance(fn, Container) else (container or _global)

    def _decorator(f):
        return _container.on_shutdown(f)

    if callable(fn) and not isinstance(fn, Container):
        return _decorator(fn)
    return _decorator


def instance() -> Container:
    """Create and return a new, independent :class:`Container`.

    Use this when you need isolation from the global container,
    for example in tests or multi-tenant scenarios.
    """
    return Container()
