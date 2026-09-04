from typing import Any, Literal

from pydantic import BaseModel, Field


class Evidence(BaseModel):
    source: str = Field(min_length=1)

    source_type: Literal[
        "satellite",
        "osm",
        "model",
        "gis",
    ]

    acquisition_date: str | None = None

    operation: str = Field(min_length=1)

    parameters: dict[str, Any] = Field(
        default_factory=dict
    )

    description: str = Field(min_length=1)