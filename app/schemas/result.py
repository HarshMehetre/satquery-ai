from typing import Any, Literal

from pydantic import BaseModel, Field

from app.schemas.evidence import Evidence


class OperationResult(BaseModel):
    """
    Result produced by a single operation.
    """

    id: str

    type: str

    data_type: Literal[
        "raster",
        "vector",
        "table",
        "scalar",
        "json",
    ]

    data: Any

    metadata: dict[str, Any] = Field(
        default_factory=dict,
    )

    confidence: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
    )


class ExecutionResult(BaseModel):
    """
    Final result returned after executing a QueryPlan.
    """

    results: dict[str, OperationResult] = Field(
        default_factory=dict,
    )

    evidence: list[Evidence] = Field(
        default_factory=list,
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict,
    )