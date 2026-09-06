import geopandas as gpd

from app.executor.context import ExecutionContext
from app.operations.base import BaseOperation
from app.schemas.operation import Operation
from app.schemas.result import OperationResult


class ProjectToCRSOperation(BaseOperation):
    """Project vector data into a target coordinate reference system."""

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
                "ProjectToCRSOperation requires a 'target_crs' parameter."
            )

    def execute(
        self,
        operation: Operation,
        context: ExecutionContext,
    ) -> OperationResult:
        self.validate(operation, context)

        input_id = operation.inputs[0]

        if input_id in context.results:
            input_result = context.get_result(input_id)
            data = input_result.data

        elif input_id in context.runtime_inputs:
            data = context.get_runtime_input(input_id)

        else:
            raise KeyError(
                f"Input '{input_id}' does not exist in execution context."
            )

        if not isinstance(data, gpd.GeoDataFrame):
            raise TypeError(
                "ProjectToCRSOperation requires a vector input "
                "as a GeoDataFrame."
            )

        target_crs = operation.parameters["target_crs"]

        projected = data.to_crs(target_crs)

        return OperationResult(
            id=operation.id,
            type=operation.type,
            data_type="vector",
            data=projected,
            metadata={
                "source_crs": str(data.crs),
                "target_crs": str(projected.crs),
                "feature_count": len(projected),
            },
        )