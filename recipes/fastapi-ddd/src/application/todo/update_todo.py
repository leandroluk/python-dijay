from pydantic import BaseModel, Field

from dijay import injectable
from src.application._shared import Usecase
from src.domain._shared import optional_field
from src.domain.todo import TodoEntity, TodoNotFoundError, TodoRepository


class UpdateTodoData(BaseModel):
    class Changes(BaseModel):
        title: str | None = optional_field(TodoEntity, "title")
        description: str | None = optional_field(TodoEntity, "description")
        done: bool | None = optional_field(TodoEntity, "done")

    id: str = TodoEntity.model_fields["id"]
    changes: Changes = Field(
        description="Changes to be applied to the todo",
        examples=[
            Changes(
                title="Buy milk",
                description="Buy milk",
                done=True,
            )
        ],
    )


@injectable()
class UpdateTodoUsecase(Usecase[TodoEntity, UpdateTodoData]):
    def __init__(self, todo_repository: TodoRepository):
        self.todo_repository = todo_repository

    async def execute(self, data: UpdateTodoData) -> TodoEntity:
        todo = await self.todo_repository.find_by_id(data.id)
        if not todo:
            raise TodoNotFoundError()

        update_data = data.changes.model_dump(exclude_unset=True)
        updated_todo = todo.model_copy(update=update_data)

        await self.todo_repository.save(updated_todo)
        return updated_todo
