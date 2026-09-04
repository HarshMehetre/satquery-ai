from typing import Any

from pydantic import BaseModel, Field


class Evidence(BaseModel):
    """
    Provenance information describing how a result was produced.
    """

    source: str

    source_type: str

    acquisition_date: str | None = None

    operation: str

    parameters: dict[str, Any] = Field(
        default_factory=dict,
    )

    description: str | None = None