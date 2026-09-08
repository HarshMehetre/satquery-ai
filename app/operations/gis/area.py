import geopandas as gpd

from app.executor.context import ExecutionContext
from app.operations.base import BaseOperation
from app.schemas.operation import Operation
from app.schemas.result import OperationResult


class AreaOperation(BaseOperation):
    """Calculate the total area of vector geometries."""

    def validate(
        self,
        operation: Operation,
        context: ExecutionContext,
    ) -> None:
        if len(operation.inputs) != 1:
            raise ValueError(
                "AreaOperation requires exactly one input."
            )

    def execute(
        self,
        operation: Operation,
        context: ExecutionContext,
    ) -> OperationResult:
        self.validate(operation, context)

        input_id = operation.inputs[0]
        input_result = context.get_result(input_id)

        if input_result.data_type != "vector":
            raise TypeError(
                "AreaOperation requires vector input."
            )

        if not isinstance(input_result.data, gpd.GeoDataFrame):
            raise TypeError(
                "AreaOperation requires a GeoDataFrame."
            )

        gdf = input_result.data

        if gdf.crs is None:
            raise ValueError(
                "AreaOperation requires an input CRS."
            )

        if gdf.crs.is_geographic:
            raise ValueError(
                "AreaOperation requires a projected CRS "
                "with metric units."
            )

        total_area_m2 = float(gdf.geometry.area.sum())

        return OperationResult(
            id=operation.id,
            type=operation.type,
            data_type="scalar",
            data=total_area_m2,
            metadata={
                "operation": "area",
                "unit": "m²",
                "feature_count": len(gdf),
                "crs": str(gdf.crs),
                "area_m2": total_area_m2,
                "area_km2": total_area_m2 / 1_000_000,
            },
        )
        
    @classmethod
    def planner_metadata(cls) -> dict[str, object]:
        return {
            "description": "Calculate the area of vector geometries.",
            "input_type": "vector",
            "output_type": "table",
        }