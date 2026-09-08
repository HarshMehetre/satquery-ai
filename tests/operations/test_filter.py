import numpy as np
import pytest

from app.executor.context import ExecutionContext
from app.operations.remote_sensing.filter import VegetationLossOperation
from app.schemas.operation import Operation
from app.schemas.query import AOI
from app.schemas.raster import RasterData, RasterMetadata
from app.schemas.result import OperationResult


def create_raster(data: np.ndarray) -> RasterData:
    return RasterData(
        data=np.asarray(data, dtype=np.float32),
        bands=["NDVI_CHANGE"],
        metadata=RasterMetadata(
            crs="EPSG:4326",
            width=data.shape[-1],
            height=data.shape[-2],
            count=data.shape[0],
            dtype="float32",
        ),
    )


def create_context(raster: RasterData) -> ExecutionContext:
    context = ExecutionContext(
        aoi=AOI(
            type="bbox",
            value=[73.80, 18.45, 73.90, 18.55],
        )
    )

    context.add_result(
        OperationResult(
            id="vegetation_change",
            type="temporal_difference",
            data_type="raster",
            data=raster,
        )
    )

    return context


def create_operation(threshold: float = 0.0) -> Operation:
    return Operation(
        id="vegetation_loss",
        type="vegetation_loss",
        inputs=["vegetation_change"],
        parameters={
            "threshold": threshold,
        },
    )


def test_vegetation_loss_requires_one_input() -> None:
    operation = Operation(
        id="vegetation_loss",
        type="vegetation_loss",
        inputs=[],
        parameters={"threshold": 0.0},
    )

    context = ExecutionContext(
        aoi=AOI(
            type="bbox",
            value=[73.80, 18.45, 73.90, 18.55],
        )
    )

    with pytest.raises(ValueError, match="exactly one input"):
        VegetationLossOperation().validate(operation, context)


def test_vegetation_loss_requires_threshold() -> None:
    operation = Operation(
        id="vegetation_loss",
        type="vegetation_loss",
        inputs=["vegetation_change"],
    )

    context = ExecutionContext(
        aoi=AOI(
            type="bbox",
            value=[73.80, 18.45, 73.90, 18.55],
        )
    )

    with pytest.raises(ValueError, match="threshold"):
        VegetationLossOperation().validate(operation, context)


def test_vegetation_loss_requires_raster_input() -> None:
    operation = create_operation()

    context = ExecutionContext(
        aoi=AOI(
            type="bbox",
            value=[73.80, 18.45, 73.90, 18.55],
        )
    )

    context.add_result(
        OperationResult(
            id="vegetation_change",
            type="mock",
            data_type="scalar",
            data=-0.2,
        )
    )

    with pytest.raises(TypeError, match="raster input"):
        VegetationLossOperation().execute(operation, context)


def test_vegetation_loss_requires_raster_data() -> None:
    operation = create_operation()

    context = ExecutionContext(
        aoi=AOI(
            type="bbox",
            value=[73.80, 18.45, 73.90, 18.55],
        )
    )

    context.add_result(
        OperationResult(
            id="vegetation_change",
            type="mock",
            data_type="raster",
            data=np.zeros((1, 2, 2), dtype=np.float32),
        )
    )

    with pytest.raises(TypeError, match="RasterData input"):
        VegetationLossOperation().execute(operation, context)


def test_vegetation_loss_filters_decrease() -> None:
    change = np.array(
        [[[-0.3, 0.1], [0.2, -0.5]]],
        dtype=np.float32,
    )

    context = create_context(create_raster(change))

    result = VegetationLossOperation().execute(
        create_operation(threshold=0.0),
        context,
    )

    expected = np.array(
        [[[1, 0], [0, 1]]],
        dtype=np.uint8,
    )

    np.testing.assert_array_equal(
        result.data.data,
        expected,
    )


def test_vegetation_loss_supports_significant_loss_threshold() -> None:
    change = np.array(
        [[[-0.3, -0.1], [0.2, -0.5]]],
        dtype=np.float32,
    )

    context = create_context(create_raster(change))

    result = VegetationLossOperation().execute(
        create_operation(threshold=0.2),
        context,
    )

    expected = np.array(
        [[[1, 0], [0, 1]]],
        dtype=np.uint8,
    )

    np.testing.assert_array_equal(
        result.data.data,
        expected,
    )


def test_vegetation_loss_returns_binary_raster() -> None:
    change = np.array(
        [[[-0.3, 0.1], [0.2, -0.5]]],
        dtype=np.float32,
    )

    context = create_context(create_raster(change))

    result = VegetationLossOperation().execute(
        create_operation(),
        context,
    )

    assert result.data_type == "raster"
    assert isinstance(result.data, RasterData)
    assert result.data.bands == ["VEGETATION_LOSS"]
    assert result.data.data.dtype == np.uint8


def test_vegetation_loss_preserves_spatial_metadata() -> None:
    change = np.array(
        [[[-0.3, 0.1], [0.2, -0.5]]],
        dtype=np.float32,
    )

    context = create_context(create_raster(change))

    result = VegetationLossOperation().execute(
        create_operation(),
        context,
    )

    assert result.data.metadata.crs == "EPSG:4326"
    assert result.data.metadata.width == 2
    assert result.data.metadata.height == 2
    assert result.data.metadata.count == 1


def test_vegetation_loss_metadata() -> None:
    change = np.array(
        [[[-0.3, 0.1], [0.2, -0.5]]],
        dtype=np.float32,
    )

    context = create_context(create_raster(change))

    result = VegetationLossOperation().execute(
        create_operation(threshold=0.2),
        context,
    )

    assert result.metadata["operation"] == "vegetation_loss"
    assert result.metadata["input"] == "vegetation_change"
    assert result.metadata["threshold"] == 0.2
    assert result.metadata["condition"] == "change <= -threshold"