from collections.abc import Awaitable, Callable
from typing import Any

from dijay import injectable
from src.domain._shared import Database


@injectable(Database)
class FakeDatabase(Database):
    async def ping(self) -> None:
        pass

    async def connect(self) -> None:
        pass

    async def close(self) -> None:
        pass

    async def query[T](
        self,
        sql: str,
        params: list[Any] | None = None,
    ) -> list[T]:
        raise NotImplementedError

    async def exec(
        self,
        sql: str,
        params: list[Any] | None = None,
    ) -> Database.Result:
        raise NotImplementedError

    async def transaction[T](
        self,
        handler: Callable[[Database.Transaction], Awaitable[T]],
    ) -> T:
        raise NotImplementedError
