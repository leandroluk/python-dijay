import os
from collections.abc import Callable

from pydantic import BaseModel, Field

from dijay import injectable


def _get_env_bool(key: str, default: bool) -> Callable[[], bool]:
    def wrapper() -> bool:
        return bool(os.getenv(key, str(default)).lower() == "true")

    return wrapper


@injectable()
class HttpConfig(BaseModel):
    path: str = Field(
        default_factory=lambda: os.getenv("HTTP_PATH", "/"),
        description="Path to the HTTP server",
    )
    host: str = Field(
        default_factory=lambda: os.getenv("HTTP_HOST", "127.0.0.1"),
        description="Host to the HTTP server",
    )
    port: int = Field(
        default_factory=lambda: int(os.getenv("HTTP_PORT", 8000)),
        description="Port to the HTTP server",
    )
    enable_reload: bool = Field(
        default_factory=_get_env_bool("HTTP_ENABLE_RELOAD", True),
        description="Enable reload",
    )
    enable_factory: bool = Field(
        default_factory=_get_env_bool("HTTP_ENABLE_FACTORY", False),
        description="Enable factory",
    )
    title: str = Field(
        default_factory=lambda: os.getenv("HTTP_TITLE", "Todo API"),
        description="Title",
    )
    version: str = Field(
        default_factory=lambda: os.getenv("HTTP_VERSION", "0.0.1"),
        description="Version",
    )
    description: str = Field(
        default_factory=lambda: os.getenv("HTTP_DESCRIPTION", "Todo API"),
        description="Description",
    )
