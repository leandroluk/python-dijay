from dijay import injectable
from src.domain.todo import TodoEntity, TodoRepository

from ..error import FakeDatabaseError


@injectable(TodoRepository)
class FakeTodoRepository(TodoRepository):
    __data: dict[str, TodoEntity] = {}

    async def create(self, todo: TodoEntity) -> None:
        self.__data[todo.id] = todo

    async def update(self, todo: TodoEntity) -> None:
        if todo.id not in self.__data:
            raise FakeDatabaseError(f"Todo with id {todo.id} not found")
        self.__data[todo.id] = todo

    async def delete(self, id: str) -> None:
        if id not in self.__data:
            raise FakeDatabaseError(f"Todo with id {id} not found")
        del self.__data[id]

    async def find_all(self) -> list[TodoEntity]:
        return list(self.__data.values())

    async def find_by_id(self, id: str) -> TodoEntity | None:
        return self.__data.get(id)
