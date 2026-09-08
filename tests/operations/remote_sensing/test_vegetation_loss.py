import numpy as np
import pytest
from rasterio.transform import from_bounds

from app.executor.context import ExecutionContext
from app.operations.remote_sensing.filter import VegetationLossOperation
from app.schemas.operation import Operation
from app.schemas.query import AOI
from app.schemas.raster import RasterData, RasterMetadata
from app.schemas.result import OperationResult


def create_change_result(data: np.ndarray) -> OperationResult:
    height, width = data.shape[-2:]

    raster = RasterData(
        data=data.astype(np.float32),
        bands=["NDVI"],
        metadata=RasterMetadata(
            crs="EPSG:4326",
            transform=from_bounds(73.0, 18.0, 73.1, 18.1, width, height),
            width=width,
            height=height,
            count=data.shape[0],
            dtype="float32",
        ),
    )

    return OperationResult(
        id="vegetation_change",
        type="temporal_difference",
        data_type="raster",
        data=raster,
    )


def create_context(result: OperationResult) -> ExecutionContext:
    context = ExecutionContext(
        aoi=AOI(
            type="bbox",
            value=[73.0, 18.0, 73.1, 18.1],
            resolved=True,
        )
    )
    context.add_result(result)
    return context


def test_detects_only_negative_change_for_decrease():
    change = np.array(
        [[
            [0.0, -0.05, -0.1, -0.2],
            [0.1, 0.0, -0.3, 0.2],
        ]]
    )

    context = create_context(create_change_result(change))

    operation = Operation(
        id="vegetation_loss",
        type="vegetation_loss",
        inputs=["vegetation_change"],
        parameters={
            "threshold": 0.1,
            "direction": "decrease",
        },
    )

    result = VegetationLossOperation().execute(operation, context)

    expected = np.array(
        [[
            [0, 0, 1, 1],
            [0, 0, 1, 0],
        ]],
        dtype=np.uint8,
    )

    np.testing.assert_array_equal(result.data.data, expected)


def test_detects_only_positive_change_for_increase():
    change = np.array(
        [[
            [0.0, 0.05, 0.1, 0.2],
            [-0.1, 0.0, 0.3, -0.2],
        ]]
    )

    context = create_context(create_change_result(change))

    operation = Operation(
        id="vegetation_loss",
        type="vegetation_loss",
        inputs=["vegetation_change"],
        parameters={
            "threshold": 0.1,
            "direction": "increase",
        },
    )

    result = VegetationLossOperation().execute(operation, context)

    expected = np.array(
        [[
            [0, 0, 1, 1],
            [0, 0, 1, 0],
        ]],
        dtype=np.uint8,
    )

    np.testing.assert_array_equal(result.data.data, expected)


def test_rejects_invalid_direction():
    context = create_context(
        create_change_result(np.zeros((1, 2, 2)))
    )

    operation = Operation(
        id="vegetation_loss",
        type="vegetation_loss",
        inputs=["vegetation_change"],
        parameters={
            "threshold": 0.1,
            "direction": "sideways",
        },
    )

    with pytest.raises(
        ValueError,
        match="direction must be either 'decrease' or 'increase'",
    ):
        VegetationLossOperation().validate(operation, context)