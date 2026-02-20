from pydantic import Field
from src.domain._shared import Creatable, Indexable, Updatable


class TodoEntity(Indexable, Updatable, Creatable):
    title: str = Field(
        description="Todo's title",
        examples=["Todo"],
        min_length=3,
        max_length=100,
    )
    description: str = Field(
        description="Todo's description",
        examples=["Todo description"],
        min_length=3,
        max_length=100,
    )
    done: bool = Field(
        description="Todo's status",
        default=False,
        examples=[False],
    )
