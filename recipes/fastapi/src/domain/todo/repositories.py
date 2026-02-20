from abc import ABC, abstractmethod

from .entities import TodoEntity


class TodoRepository(ABC):
    @abstractmethod
    async def create(self, todo: TodoEntity) -> None:
        raise NotImplementedError

    @abstractmethod
    async def update(self, todo: TodoEntity) -> None:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, id: str) -> None:
        raise NotImplementedError

    @abstractmethod
    async def find_all(self) -> list[TodoEntity]:
        raise NotImplementedError

    @abstractmethod
    async def find_by_id(self, id: str) -> TodoEntity | None:
        raise NotImplementedError
