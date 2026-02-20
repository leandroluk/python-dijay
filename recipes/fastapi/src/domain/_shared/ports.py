from abc import ABC, abstractmethod
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any


class Database(ABC):
    @dataclass(frozen=True)
    class Result:
        rows_affected: int
        last_insert_id: str | int | None = None

    class Transaction(ABC):
        @abstractmethod
        async def query[T](
            self,
            sql: str,
            params: list[Any] | None = None,
        ) -> list[T]:
            raise NotImplementedError

        @abstractmethod
        async def exec(
            self,
            sql: str,
            params: list[Any] | None = None,
        ) -> Database.Result:
            raise NotImplementedError

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
    async def exec(
        self,
        sql: str,
        params: list[Any] | None = None,
    ) -> Database.Result:
        raise NotImplementedError

    @abstractmethod
    async def transaction[T](
        self,
        handler: Callable[[Database.Transaction], Awaitable[T]],
    ) -> T:
        raise NotImplementedError
