import geopandas as gpd

from app.executor.context import ExecutionContext
from app.operations.base import BaseOperation
from app.schemas.operation import Operation
from app.schemas.result import OperationResult


class ProjectToCRSOperation(BaseOperation):
    """Reproject vector geometries into a target coordinate reference system."""

    def validate(
        self,
        operation: Operation,
        context: ExecutionContext,
    ) -> None:
        if len(operation.inputs) != 1:
            raise ValueError(
                "ProjectToCRSOperation requires exactly one input."
            )

        if "target_crs" not in operation.parameters:
            raise ValueError(
                "Missing required parameter: 'target_crs'."
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
                "ProjectToCRSOperation requires vector input."
            )

        if not isinstance(input_result.data, gpd.GeoDataFrame):
            raise TypeError(
                "ProjectToCRSOperation requires a GeoDataFrame."
            )

        target_crs = operation.parameters["target_crs"]

        projected = input_result.data.to_crs(target_crs)

        return OperationResult(
            id=operation.id,
            type=operation.type,
            data_type="vector",
            data=projected,
            metadata={
                "source_crs": str(input_result.data.crs)
                if input_result.data.crs
                else None,
                "target_crs": str(projected.crs),
                "feature_count": len(projected),
            },
        )