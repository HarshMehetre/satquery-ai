from typing import Any, Literal

from pydantic import BaseModel, Field

from .operation import Operation


class AOI(BaseModel):
    type: Literal["bbox", "polygon", "place"]
    value: Any


class TimeRange(BaseModel):
    start: str
    end: str


class DataInput(BaseModel):
    id: str = Field(min_length=1)
    source: Literal[
        "sentinel-2",
        "sentinel-1",
        "osm",
    ]
    purpose: str = Field(min_length=1)
    time_range: TimeRange | None = None


class OutputSpec(BaseModel):
    type: Literal[
        "map",
        "geojson",
        "raster",
        "statistics",
    ] = "map"

    include_geometry: bool = True
    include_statistics: bool = True
    include_evidence: bool = True


class QueryPlan(BaseModel):
    plan_id: str = Field(min_length=1)
    aoi: AOI
    inputs: list[DataInput] = Field(default_factory=list)
    operations: list[Operation] = Field(default_factory=list)
    output: OutputSpec = Field(default_factory=OutputSpec)