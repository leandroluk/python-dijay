from pydantic import BaseModel, Field

from src.domain._shared import optional_field
from src.domain.todo import TodoEntity


class UpdateTodoBodyDTO(BaseModel):
    title: str | None = optional_field(TodoEntity, "title")
    description: str | None = optional_field(TodoEntity, "description")
    done: bool | None = optional_field(TodoEntity, "done")


class UpdateTodoParamDTO(BaseModel):
    id: str = Field(description="The ID of the todo to update")
