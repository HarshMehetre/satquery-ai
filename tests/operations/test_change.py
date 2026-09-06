import numpy as np
import pytest

from app.executor.context import ExecutionContext
from app.operations.remote_sensing.change import TemporalDifferenceOperation
from app.schemas.operation import Operation
from app.schemas.query import AOI
from app.schemas.raster import RasterData, RasterMetadata
from app.schemas.result import OperationResult


def create_raster(
    data: np.ndarray,
    crs: str = "EPSG:4326",
    bands: list[str] | None = None,
) -> RasterData:
    if bands is None:
        bands = ["NDVI"]

    return RasterData(
        data=np.asarray(data, dtype=np.float32),
        bands=bands,
        metadata=RasterMetadata(
            crs=crs,
            width=data.shape[-1],
            height=data.shape[-2],
            count=data.shape[0],
            dtype="float32",
        ),
    )


def create_context(
    earlier: RasterData,
    later: RasterData,
) -> ExecutionContext:
    context = ExecutionContext(
        aoi=AOI(
            type="bbox",
            value=[73.80, 18.45, 73.90, 18.55],
        )
    )

    context.add_result(
        OperationResult(
            id="ndvi_2024",
            type="ndvi",
            data_type="raster",
            data=earlier,
        )
    )

    context.add_result(
        OperationResult(
            id="ndvi_2026",
            type="ndvi",
            data_type="raster",
            data=later,
        )
    )

    return context


def create_operation() -> Operation:
    return Operation(
        id="vegetation_change",
        type="temporal_difference",
        inputs=["ndvi_2024", "ndvi_2026"],
    )


def test_temporal_difference_requires_two_inputs() -> None:
    operation = Operation(
        id="vegetation_change",
        type="temporal_difference",
        inputs=["ndvi_2024"],
    )

    context = ExecutionContext(
        aoi=AOI(
            type="bbox",
            value=[73.80, 18.45, 73.90, 18.55],
        )
    )

    with pytest.raises(ValueError, match="exactly two inputs"):
        TemporalDifferenceOperation().validate(operation, context)


def test_temporal_difference_requires_raster_inputs() -> None:
    operation = create_operation()

    context = ExecutionContext(
        aoi=AOI(
            type="bbox",
            value=[73.80, 18.45, 73.90, 18.55],
        )
    )

    context.add_result(
        OperationResult(
            id="ndvi_2024",
            type="mock",
            data_type="scalar",
            data=1.0,
        )
    )

    context.add_result(
        OperationResult(
            id="ndvi_2026",
            type="mock",
            data_type="scalar",
            data=1.0,
        )
    )

    with pytest.raises(TypeError, match="raster inputs"):
        TemporalDifferenceOperation().execute(operation, context)


def test_temporal_difference_requires_raster_data() -> None:
    operation = create_operation()

    context = ExecutionContext(
        aoi=AOI(
            type="bbox",
            value=[73.80, 18.45, 73.90, 18.55],
        )
    )

    context.add_result(
        OperationResult(
            id="ndvi_2024",
            type="mock",
            data_type="raster",
            data=np.ones((1, 2, 2), dtype=np.float32),
        )
    )

    context.add_result(
        OperationResult(
            id="ndvi_2026",
            type="mock",
            data_type="raster",
            data=np.ones((1, 2, 2), dtype=np.float32),
        )
    )

    with pytest.raises(TypeError, match="RasterData inputs"):
        TemporalDifferenceOperation().execute(operation, context)


def test_temporal_difference_rejects_mismatched_dimensions() -> None:
    earlier = create_raster(
        np.array([[[0.8, 0.6], [0.4, 0.7]]])
    )

    later = create_raster(
        np.array([[[0.5, 0.7, 0.2], [0.6, 0.2, 0.4]]])
    )

    context = create_context(earlier, later)

    with pytest.raises(ValueError, match="identical dimensions"):
        TemporalDifferenceOperation().execute(
            create_operation(),
            context,
        )


def test_temporal_difference_rejects_mismatched_crs() -> None:
    earlier = create_raster(
        np.array([[[0.8, 0.6], [0.4, 0.7]]]),
        crs="EPSG:4326",
    )

    later = create_raster(
        np.array([[[0.5, 0.7], [0.6, 0.2]]]),
        crs="EPSG:32643",
    )

    context = create_context(earlier, later)

    with pytest.raises(ValueError, match="same CRS"):
        TemporalDifferenceOperation().execute(
            create_operation(),
            context,
        )


def test_temporal_difference_rejects_mismatched_bands() -> None:
    earlier = create_raster(
        np.array([[[0.8, 0.6], [0.4, 0.7]]]),
        bands=["NDVI"],
    )

    later = create_raster(
        np.array([[[0.5, 0.7], [0.6, 0.2]]]),
        bands=["EVI"],
    )

    context = create_context(earlier, later)

    with pytest.raises(ValueError, match="matching bands"):
        TemporalDifferenceOperation().execute(
            create_operation(),
            context,
        )


def test_temporal_difference_calculates_correct_values() -> None:
    earlier = create_raster(
        np.array(
            [[[0.8, 0.6], [0.4, 0.7]]],
            dtype=np.float32,
        )
    )

    later = create_raster(
        np.array(
            [[[0.5, 0.7], [0.6, 0.2]]],
            dtype=np.float32,
        )
    )

    context = create_context(earlier, later)

    result = TemporalDifferenceOperation().execute(
        create_operation(),
        context,
    )

    expected = np.array(
        [[[-0.3, 0.1], [0.2, -0.5]]],
        dtype=np.float32,
    )

    np.testing.assert_allclose(
        result.data.data,
        expected,
        rtol=1e-6,
        atol=1e-6,
    )


def test_temporal_difference_returns_raster_result() -> None:
    earlier = create_raster(
        np.array([[[0.8, 0.6], [0.4, 0.7]]])
    )

    later = create_raster(
        np.array([[[0.5, 0.7], [0.6, 0.2]]])
    )

    context = create_context(earlier, later)

    result = TemporalDifferenceOperation().execute(
        create_operation(),
        context,
    )

    assert result.id == "vegetation_change"
    assert result.type == "temporal_difference"
    assert result.data_type == "raster"

    assert isinstance(result.data, RasterData)
    assert result.data.bands == ["NDVI"]
    assert result.data.metadata.crs == "EPSG:4326"


def test_temporal_difference_metadata() -> None:
    earlier = create_raster(
        np.array([[[0.8, 0.6], [0.4, 0.7]]])
    )

    later = create_raster(
        np.array([[[0.5, 0.7], [0.6, 0.2]]])
    )

    context = create_context(earlier, later)

    result = TemporalDifferenceOperation().execute(
        create_operation(),
        context,
    )

    assert result.metadata["operation"] == "temporal_difference"
    assert result.metadata["formula"] == "later - earlier"
    assert result.metadata["earlier_input"] == "ndvi_2024"
    assert result.metadata["later_input"] == "ndvi_2026"