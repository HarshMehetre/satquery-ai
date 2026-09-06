from typing import Any

import geopandas as gpd
import numpy as np
from rasterio.features import shapes
from shapely.geometry import shape

from app.executor.context import ExecutionContext
from app.operations.base import BaseOperation
from app.schemas.operation import Operation
from app.schemas.raster import RasterData
from app.schemas.result import OperationResult


class RasterPolygonizeOperation(BaseOperation):
    """Convert a raster mask into vector polygons."""

    def validate(
        self,
        operation: Operation,
        context: ExecutionContext,
    ) -> None:
        if len(operation.inputs) != 1:
            raise ValueError(
                "RasterPolygonizeOperation requires exactly one input."
            )

    def execute(
        self,
        operation: Operation,
        context: ExecutionContext,
    ) -> OperationResult:
        self.validate(operation, context)

        input_id = operation.inputs[0]
        input_result = context.get_input_result(input_id)

        if input_result.data_type != "raster":
            raise TypeError(
                "RasterPolygonizeOperation requires raster input."
            )

        if not isinstance(input_result.data, RasterData):
            raise TypeError(
                "RasterPolygonizeOperation requires RasterData input."
            )

        raster = input_result.data

        if raster.data.ndim != 3:
            raise ValueError(
                "RasterPolygonizeOperation requires a 3D raster array."
            )

        if raster.data.shape[0] != 1:
            raise ValueError(
                "RasterPolygonizeOperation requires a single-band raster."
            )

        if raster.metadata.transform is None:
            raise ValueError(
                "RasterPolygonizeOperation requires raster transform metadata."
            )

        mask = raster.data[0]

        valid_mask = mask != raster.metadata.nodata

        polygon_records: list[dict[str, Any]] = []

        for geometry, value in shapes(
            mask.astype(np.uint8),
            mask=valid_mask,
            transform=raster.metadata.transform,
        ):
            if value != 1:
                continue

            polygon_records.append(
                {
                    "class": "vegetation_loss",
                    "value": int(value),
                    "geometry": shape(geometry),
                }
            )

        if polygon_records:
            polygons = gpd.GeoDataFrame(
                polygon_records,
                crs=raster.metadata.crs,
            )
        else:
            polygons = gpd.GeoDataFrame(
                {
                    "class": [],
                    "value": [],
                    "geometry": [],
                },
                geometry="geometry",
                crs=raster.metadata.crs,
            )

        return OperationResult(
            id=operation.id,
            type=operation.type,
            data_type="vector",
            data=polygons,
            metadata={
                "operation": "raster_polygonize",
                "input": input_id,
                "feature_count": len(polygons),
                "crs": str(polygons.crs)
                if polygons.crs
                else None,
            },
        )