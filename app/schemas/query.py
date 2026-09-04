from typing import Any, Literal

from pydantic import BaseModel, Field

from app.schemas.operation import Operation


class AOI(BaseModel):
    """
    Area of Interest.

    The value is intentionally flexible because an AOI may eventually
    be represented as a bounding box, polygon, place name, etc.
    """

    type: Literal["bbox", "polygon", "place"]

    value: Any


class TimeRange(BaseModel):
    """
    Temporal range for a data request.
    """

    start: str
    end: str


class DataInput(BaseModel):
    """
    External data source required by a query plan.
    """

    id: str = Field(
        ...,
        description="Unique identifier for this input.",
    )

    source: str = Field(
        ...,
        description="Data source, e.g. sentinel-2, sentinel-1, osm.",
    )

    purpose: str = Field(
        ...,
        description="Why this dataset is required.",
    )

    time_range: TimeRange | None = None


class OutputSpec(BaseModel):
    """
    Defines what the user expects from query execution.
    """

    type: Literal[
        "map",
        "geojson",
        "raster",
        "statistics",
    ]

    include_geometry: bool = True
    include_statistics: bool = True
    include_evidence: bool = True


class QueryPlan(BaseModel):
    """
    Complete structured representation of a user's geospatial query.
    """

    plan_id: str

    aoi: AOI

    inputs: list[DataInput] = Field(
        default_factory=list,
    )

    operations: list[Operation] = Field(
        default_factory=list,
    )

    output: OutputSpec