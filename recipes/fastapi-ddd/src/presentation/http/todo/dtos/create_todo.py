from pydantic import BaseModel

from src.domain._shared import inherit_field
from src.domain.todo import TodoEntity


class CreateTodoBodyDTO(BaseModel):
    title: str = inherit_field(TodoEntity, "title")
    description: str | None = inherit_field(TodoEntity, "description")
