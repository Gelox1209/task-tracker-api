"""Request/response shapes (what the API accepts and returns).

Keeping these separate from the DB models means you control exactly
what clients can send and see.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=1000)


class TaskRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None
    done: bool
    created_at: datetime


class TaskUpdate(BaseModel):
    # Fields are optional for partial updates. If a field is not provided, it won't be changed.
    title: str = Field(default=None, min_length=1, max_length=200)
    # str | none means the field can be a string or None, allowing for null values.
    description: str | None = Field(default=None, max_length=1000)
    done: bool = None
