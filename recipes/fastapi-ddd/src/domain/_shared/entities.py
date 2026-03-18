from datetime import UTC, datetime
from uuid import uuid4

from pydantic import BaseModel, Field


class Indexable(BaseModel):
    id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="Unique identifier for the entity (UUIDv4)",
        examples=["018f3b5e-9012-7000-8000-000000000000"],
        json_schema_extra={"format": "uuid"},
    )


class Creatable(BaseModel):
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Timestamp of creation",
        examples=[datetime.now(UTC)],
    )


class Updatable(BaseModel):
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Timestamp of the last update",
        examples=[datetime.now(UTC)],
    )
