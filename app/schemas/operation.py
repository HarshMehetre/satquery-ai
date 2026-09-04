from typing import Any

from pydantic import BaseModel, Field


class Operation(BaseModel):
    id: str = Field(min_length=1)
    type: str = Field(min_length=1)
    inputs: list[str] = Field(default_factory=list)
    parameters: dict[str, Any] = Field(default_factory=dict)