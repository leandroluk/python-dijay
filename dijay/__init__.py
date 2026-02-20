"""Lightweight async dependency injection container.


Quickstart::


    from antigravity import inject, resolve, SINGLETON


    @inject(scope=SINGLETON)

    class Database:

        ...


    db = await resolve(Database)


For advanced usage (multiple containers, request scoping, bootstrap/shutdown hooks),

instantiate :class:`Container` directly via :func:`instance`.
"""

from .container import (
    REQUEST,
    SINGLETON,
    TRANSIENT,
    Container,
    Inject,
    injectable,
    instance,
    resolve,
)

__all__ = [
    Container,
    injectable,
    resolve,
    instance,
    Inject,
    SINGLETON,
    TRANSIENT,
    REQUEST,
]
