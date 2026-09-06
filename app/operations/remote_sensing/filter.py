import numpy as np

from app.executor.context import ExecutionContext
from app.operations.base import BaseOperation
from app.schemas.operation import Operation
from app.schemas.raster import RasterData, RasterMetadata
from app.schemas.result import OperationResult


class VegetationLossOperation(BaseOperation):
    """Extract vegetation-loss pixels from a temporal change raster."""

    def validate(
        self,
        operation: Operation,
        context: ExecutionContext,
    ) -> None:
        if len(operation.inputs) != 1:
            raise ValueError(
                "VegetationLossOperation requires exactly one input."
            )

        if "threshold" not in operation.parameters:
            raise ValueError(
                "Missing required parameter: 'threshold'."
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
                "VegetationLossOperation requires raster input."
            )

        if not isinstance(input_result.data, RasterData):
            raise TypeError(
                "VegetationLossOperation requires RasterData input."
            )

        input_raster = input_result.data
        threshold = float(operation.parameters["threshold"])

        loss_mask = input_raster.data <= threshold

        loss_mask = loss_mask.astype(np.uint8)

        metadata = RasterMetadata(
            crs=input_raster.metadata.crs,
            transform=input_raster.metadata.transform,
            resolution=input_raster.metadata.resolution,
            nodata=0,
            bounds=input_raster.metadata.bounds,
            width=input_raster.metadata.width,
            height=input_raster.metadata.height,
            count=input_raster.metadata.count,
            dtype=str(loss_mask.dtype),
        )

        raster = RasterData(
            data=loss_mask,
            bands=["VEGETATION_LOSS"],
            metadata=metadata,
        )

        return OperationResult(
            id=operation.id,
            type=operation.type,
            data_type="raster",
            data=raster,
            metadata={
                "operation": "vegetation_loss",
                "input": input_id,
                "threshold": threshold,
                "condition": "change <= threshold",
            },
        )