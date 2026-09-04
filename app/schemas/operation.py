from typing import Any

from pydantic import BaseModel, Field


class Operation(BaseModel):
    """
    A single executable operation in a SatQuery plan.
    """

    id: str = Field(
        ...,
        description="Unique identifier for this operation within the plan.",
    )

    type: str = Field(
        ...,
        description="Registered operation type.",
    )

    inputs: list[str] = Field(
        default_factory=list,
        description="IDs of input data or previous operation results.",
    )

    parameters: dict[str, Any] = Field(
        default_factory=dict,
        description="Operation-specific parameters.",
    )