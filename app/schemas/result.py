from typing import Any, Literal

from pydantic import BaseModel, Field

from .evidence import Evidence


class OperationResult(BaseModel):
    id: str = Field(min_length=1)

    type: str = Field(min_length=1)

    data_type: Literal[
        "raster",
        "vector",
        "table",
        "scalar",
    ]

    data: Any

    metadata: dict[str, Any] = Field(
        default_factory=dict
    )

    confidence: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
    )


class ExecutionResult(BaseModel):
    results: dict[str, OperationResult] = Field(
        default_factory=dict
    )

    evidence: list[Evidence] = Field(
        default_factory=list
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict
    )