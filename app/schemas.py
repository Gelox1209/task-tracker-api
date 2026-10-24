"""Request/response shapes (what the API accepts and returns).

Keeping these separate from the DB models means you control exactly
what clients can send and see.
"""

from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

Title = Annotated[str, Field(min_length=1, max_length=200)]


class TaskConfig(BaseModel):
    model_config = ConfigDict(
        extra="forbid", str_strip_whitespace=True
    )  # forbid extra fields in input and strip whitespace from strings


class TaskListParams(TaskConfig):
    # Built in validation for limit and offset is handled by Pydantic's Field() with ge and le constraints,
    # so we don't need to manually check them in the endpoint.
    limit: int = Field(default=10, ge=1, le=100)
    offset: int = Field(default=0, ge=0)
    done: bool | None = None


class TaskCreate(TaskConfig):
    title: Title
    description: str | None = Field(default=None, max_length=1000)
    done: bool = Field(default=False)  # default value if not provided


class TaskRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None
    done: bool
    created_at: datetime


# When a subclass redefines a field, Pydantic replaces the whole field definition,
# be careful to include all the constraints you want.
class TaskUpdate(TaskCreate):
    title: Title = None
    done: bool = Field(default=None)
