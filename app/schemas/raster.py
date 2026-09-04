from typing import Any

import numpy as np
from pydantic import BaseModel, Field, ConfigDict


class RasterMetadata(BaseModel):
    """Geospatial metadata associated with a raster."""

    crs: str | None = None
    transform: Any | None = None
    resolution: tuple[float, float] | None = None
    nodata: float | None = None
    bounds: tuple[float, float, float, float] | None = None
    width: int
    height: int
    count: int
    dtype: str

class RasterData(BaseModel):
    """In-memory multiband raster representation."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    data: np.ndarray
    bands: list[str] = Field(default_factory=list)
    metadata: RasterMetadata