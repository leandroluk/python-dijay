from pydantic import BaseModel

from dijay import injectable
from src.application._shared import Usecase
from src.domain._shared import inherit_field
from src.domain.todo import TodoEntity, TodoNotFoundError, TodoRepository


class GetTodoByIdData(BaseModel):
    id: str = inherit_field(TodoEntity, "id")


@injectable()
class GetTodoByIdUsecase(Usecase[TodoEntity, GetTodoByIdData]):
    def __init__(self, todo_repository: TodoRepository):
        self.todo_repository = todo_repository

    async def execute(self, data: GetTodoByIdData) -> TodoEntity:
        todo = await self.todo_repository.find_by_id(data.id)
        if not todo:
            raise TodoNotFoundError()

        return todo
