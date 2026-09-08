import numpy as np

from app.executor.context import ExecutionContext
from app.operations.base import BaseOperation
from app.schemas.operation import Operation
from app.schemas.raster import RasterData, RasterMetadata
from app.schemas.result import OperationResult


class TemporalDifferenceOperation(BaseOperation):
    """Calculate the temporal difference between two raster layers."""

    def validate(
        self,
        operation: Operation,
        context: ExecutionContext,
    ) -> None:
        if len(operation.inputs) != 2:
            raise ValueError(
                "TemporalDifferenceOperation requires exactly two inputs."
            )

    def execute(
        self,
        operation: Operation,
        context: ExecutionContext,
    ) -> OperationResult:
        self.validate(operation, context)

        earlier_id, later_id = operation.inputs

        earlier_result = context.get_input_result(earlier_id)
        later_result = context.get_input_result(later_id)

        if earlier_result.data_type != "raster":
            raise TypeError(
                "TemporalDifferenceOperation requires raster inputs."
            )

        if later_result.data_type != "raster":
            raise TypeError(
                "TemporalDifferenceOperation requires raster inputs."
            )

        if not isinstance(earlier_result.data, RasterData):
            raise TypeError(
                "TemporalDifferenceOperation requires RasterData inputs."
            )

        if not isinstance(later_result.data, RasterData):
            raise TypeError(
                "TemporalDifferenceOperation requires RasterData inputs."
            )

        earlier = earlier_result.data
        later = later_result.data

        if earlier.data.shape != later.data.shape:
            raise ValueError(
                "TemporalDifferenceOperation requires rasters "
                "with identical dimensions."
            )

        if earlier.metadata.crs != later.metadata.crs:
            raise ValueError(
                "TemporalDifferenceOperation requires rasters "
                "with the same CRS."
            )

        if earlier.bands != later.bands:
            raise ValueError(
                "TemporalDifferenceOperation requires matching bands."
            )

        difference = later.data - earlier.data

        difference = np.asarray(
            difference,
            dtype=np.float32,
        )

        metadata = RasterMetadata(
            crs=later.metadata.crs,
            transform=later.metadata.transform,
            resolution=later.metadata.resolution,
            nodata=later.metadata.nodata,
            bounds=later.metadata.bounds,
            width=later.metadata.width,
            height=later.metadata.height,
            count=later.metadata.count,
            dtype=str(difference.dtype),
        )

        raster = RasterData(
            data=difference,
            bands=later.bands.copy(),
            metadata=metadata,
        )

        return OperationResult(
            id=operation.id,
            type=operation.type,
            data_type="raster",
            data=raster,
            metadata={
                "operation": "temporal_difference",
                "formula": "later - earlier",
                "earlier_input": earlier_id,
                "later_input": later_id,
            },
        )
        
    @classmethod
    def planner_metadata(cls) -> dict[str, object]:
        return {
            "description": "Calculate the difference between two temporal raster results.",
            "input_type": "raster",
            "output_type": "raster",
    }