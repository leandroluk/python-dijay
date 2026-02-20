"""Lightweight async dependency injection container.

Quickstart::

    from dijay import injectable, resolve, SINGLETON

    @injectable(scope=SINGLETON)
    class Database: ...

    db = await resolve(Database)

For advanced usage (multiple containers, request scoping,
bootstrap/shutdown hooks), instantiate :class:`Container`
directly via :func:`instance`.
"""

from .container import Container
from .decorators import (
    injectable,
    instance,
    on_bootstrap,
    on_shutdown,
    register,
    resolve,
)
from .inject import Inject
from .module import DynamicModule, module
from .provider import REQUEST, SINGLETON, TRANSIENT, Provide

__all__ = [
    REQUEST,
    SINGLETON,
    TRANSIENT,
    Container,
    DynamicModule,
    Inject,
    Provide,
    injectable,
    instance,
    module,
    on_bootstrap,
    on_shutdown,
    register,
    resolve,
]
