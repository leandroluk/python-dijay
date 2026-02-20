from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

SINGLETON = "singleton"
"""Scope that creates a single instance shared across all resolutions."""

TRANSIENT = "transient"
"""Scope that creates a new instance on every resolution."""

REQUEST = "request"
"""Scope that creates one instance per request ID, shared within the same request."""


@dataclass
class Provide:
    """Custom provider registration for modules.

    Allows defining providers with specific tokens, values, factories,
    or class overrides.

    Example::

        @module(providers=[
            Provide("DB_URL", use_value="postgresql://..."),
            Provide(Cache, use_class=RedisCache),
            Provide(Client, use_factory=create_http_client),
        ])
        class AppModule: ...

    Args:
        token: The token to bind (e.g. interface, string).
        use_class: A class to instantiate and bind to the token.
        use_value: A value to bind directly.
        use_factory: A callable to invoke to create the dependency.
        scope: Lifetime scope (defaults to ``SINGLETON``).
    """

    token: Any
    use_class: Any = None
    use_value: Any = None
    use_factory: Callable[..., Any] | None = None
    scope: str = SINGLETON
