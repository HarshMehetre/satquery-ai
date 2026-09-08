import geopandas as gpd

from app.executor.context import ExecutionContext
from app.operations.base import BaseOperation
from app.schemas.operation import Operation
from app.schemas.result import OperationResult


class IntersectionOperation(BaseOperation):
    """Compute the spatial intersection of two vector layers."""

    def validate(
        self,
        operation: Operation,
        context: ExecutionContext,
    ) -> None:
        if len(operation.inputs) != 2:
            raise ValueError(
                "IntersectionOperation requires exactly two inputs."
            )

    def execute(
        self,
        operation: Operation,
        context: ExecutionContext,
    ) -> OperationResult:
        self.validate(operation, context)

        first_id, second_id = operation.inputs

        first_result = context.get_input_result(first_id)
        second_result = context.get_input_result(second_id)

        if first_result.data_type != "vector":
            raise TypeError(
                "IntersectionOperation requires vector inputs."
            )

        if second_result.data_type != "vector":
            raise TypeError(
                "IntersectionOperation requires vector inputs."
            )

        if not isinstance(first_result.data, gpd.GeoDataFrame):
            raise TypeError(
                "IntersectionOperation requires GeoDataFrame inputs."
            )

        if not isinstance(second_result.data, gpd.GeoDataFrame):
            raise TypeError(
                "IntersectionOperation requires GeoDataFrame inputs."
            )

        first = first_result.data
        second = second_result.data

        if first.crs != second.crs:
            raise ValueError(
                "IntersectionOperation requires both inputs "
                "to use the same CRS."
            )

        intersection = gpd.overlay(
            first,
            second,
            how="intersection",
        )

        return OperationResult(
            id=operation.id,
            type=operation.type,
            data_type="vector",
            data=intersection,
            metadata={
                "operation": "intersection",
                "input_count": len(operation.inputs),
                "feature_count": len(intersection),
                "crs": str(intersection.crs)
                if intersection.crs
                else None,
            },
        )

    @staticmethod
    def _get_input_result(
        input_id: str,
        context: ExecutionContext,
    ) -> OperationResult:
        if input_id in context.results:
            return context.get_result(input_id)

        if input_id in context.runtime_inputs:
            return OperationResult(
                id=input_id,
                type="runtime_input",
                data_type="vector",
                data=context.get_runtime_input(input_id),
            )

        raise KeyError(
            f"Input '{input_id}' does not exist in execution context."
        )
        
    @classmethod
    def planner_metadata(cls) -> dict[str, object]:
        return {
            "description": "Calculate the spatial intersection of vector geometries.",
            "input_type": "vector",
            "output_type": "vector",
        }