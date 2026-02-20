from pydantic import BaseModel, Field

from dijay import injectable
from src.application._shared import Usecase
from src.domain.todo import TodoEntity, TodoRepository


class ListTodoResult(BaseModel):
    items: list[TodoEntity] = Field(
        default_factory=list,
        description="List of todos",
    )


@injectable()
class ListTodoUsecase(Usecase[ListTodoResult]):
    def __init__(self, todo_repository: TodoRepository):
        self.todo_repository = todo_repository

    async def execute(self) -> ListTodoResult:
        items = await self.todo_repository.find_all()
        return ListTodoResult(
            items=items,
        )
