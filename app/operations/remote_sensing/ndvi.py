from typing import Any

import numpy as np

from app.executor.context import ExecutionContext
from app.operations.base import BaseOperation
from app.schemas.operation import Operation
from app.schemas.result import OperationResult


class NDVIOperation(BaseOperation):
    """Calculate NDVI from red and NIR raster bands."""

    def validate(
        self,
        operation: Operation,
        context: ExecutionContext,
    ) -> None:
        if len(operation.inputs) != 1:
            raise ValueError(
                "NDVIOperation requires exactly one input."
            )

        input_id = operation.inputs[0]

        if input_id not in context.inputs and input_id not in context.results:
            raise KeyError(
                f"Input '{input_id}' does not exist."
            )

        required_parameters = {"red_band", "nir_band"}

        missing_parameters = required_parameters - set(
            operation.parameters
        )

        if missing_parameters:
            raise ValueError(
                "Missing NDVI parameters: "
                f"{sorted(missing_parameters)}"
            )

    def execute(
        self,
        operation: Operation,
        context: ExecutionContext,
    ) -> OperationResult:
        self.validate(operation, context)

        input_id = operation.inputs[0]

        if input_id in context.results:
            source_data: Any = context.get_result(input_id).data
        else:
            source_data = context.inputs[input_id]

        red_band = operation.parameters["red_band"]
        nir_band = operation.parameters["nir_band"]

        return self._calculate(
            operation=operation,
            source_data=source_data,
            red_band=red_band,
            nir_band=nir_band,
        )

    def _calculate(
        self,
        operation: Operation,
        source_data: Any,
        red_band: str,
        nir_band: str,
    ) -> OperationResult:
        if not isinstance(source_data, dict):
            raise TypeError(
                "NDVI input data must be a dictionary containing bands."
            )

        if red_band not in source_data:
            raise KeyError(
                f"Red band '{red_band}' not found in input data."
            )

        if nir_band not in source_data:
            raise KeyError(
                f"NIR band '{nir_band}' not found in input data."
            )

        red = np.asarray(
            source_data[red_band],
            dtype=np.float32,
        )

        nir = np.asarray(
            source_data[nir_band],
            dtype=np.float32,
        )

        if red.shape != nir.shape:
            raise ValueError(
                "Red and NIR bands must have identical shapes."
            )

        denominator = nir + red

        ndvi = np.divide(
            nir - red,
            denominator,
            out=np.zeros_like(nir, dtype=np.float32),
            where=denominator != 0,
        )

        return OperationResult(
            id=operation.id,
            type=operation.type,
            data_type="raster",
            data=ndvi,
            metadata={
                "red_band": red_band,
                "nir_band": nir_band,
                "formula": "(NIR - Red) / (NIR + Red)",
            },
        )