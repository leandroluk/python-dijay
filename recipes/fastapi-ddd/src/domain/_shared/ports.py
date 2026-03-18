from abc import ABC, abstractmethod
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class DatabaseResult:
    rows_affected: int
    last_insert_id: str | int | None = None


class DatabaseTransaction(ABC):
    @abstractmethod
    async def query[T](self, sql: str, params: list[Any] | None = None) -> list[T]:
        raise NotImplementedError

    @abstractmethod
    async def exec(self, sql: str, params: list[Any] | None = None) -> DatabaseResult:
        raise NotImplementedError


class Database(ABC):
    @abstractmethod
    async def ping(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def connect(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def close(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def query[T](
        self,
        sql: str,
        params: list[Any] | None = None,
    ) -> list[T]:
        raise NotImplementedError

    @abstractmethod
    async def exec(self, sql: str, params: list[Any] | None = None) -> DatabaseResult:
        raise NotImplementedError

    @abstractmethod
    async def transaction[T](
        self, handler: Callable[[DatabaseTransaction], Awaitable[T]]
    ) -> T:
        raise NotImplementedError
