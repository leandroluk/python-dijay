from pydantic import BaseModel

from dijay import injectable
from src.application._shared import Usecase
from src.domain._shared import inherit_field
from src.domain.todo import TodoEntity, TodoRepository


class CreateTodoData(BaseModel):
    title: str = inherit_field(TodoEntity, "title")
    description: str | None = inherit_field(TodoEntity, "description")


@injectable()
class CreateTodoUsecase(Usecase[TodoEntity, CreateTodoData]):
    def __init__(self, todo_repository: TodoRepository):
        self.todo_repository = todo_repository

    async def execute(self, data: CreateTodoData) -> TodoEntity:
        todo = TodoEntity(
            title=data.title,
            description=data.description,
        )

        await self.todo_repository.create(todo)

        return todo
