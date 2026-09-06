import geopandas as gpd

from app.executor.context import ExecutionContext
from app.operations.base import BaseOperation
from app.schemas.operation import Operation
from app.schemas.result import OperationResult


class BufferOperation(BaseOperation):
    """Create a buffer around vector geometries."""

    def validate(
        self,
        operation: Operation,
        context: ExecutionContext,
    ) -> None:
        if len(operation.inputs) != 1:
            raise ValueError(
                "BufferOperation requires exactly one input."
            )

        if "distance_m" not in operation.parameters:
            raise ValueError(
                "Missing required parameter: 'distance_m'."
            )

        distance_m = operation.parameters["distance_m"]

        if not isinstance(distance_m, (int, float)):
            raise TypeError(
                "Buffer distance must be a number."
            )

        if distance_m < 0:
            raise ValueError(
                "Buffer distance cannot be negative."
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
                "BufferOperation requires vector input."
            )

        if not isinstance(input_result.data, gpd.GeoDataFrame):
            raise TypeError(
                "BufferOperation requires a GeoDataFrame."
            )

        distance_m = float(operation.parameters["distance_m"])

        buffered = input_result.data.copy()
        buffered["geometry"] = buffered.geometry.buffer(distance_m)

        return OperationResult(
            id=operation.id,
            type=operation.type,
            data_type="vector",
            data=buffered,
            metadata={
                "operation": "buffer",
                "distance_m": distance_m,
                "feature_count": len(buffered),
                "crs": str(buffered.crs)
                if buffered.crs
                else None,
            },
        )