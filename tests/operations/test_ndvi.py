import numpy as np
import pytest

from app.executor.context import ExecutionContext
from app.operations.remote_sensing.ndvi import NDVIOperation
from app.schemas.operation import Operation
from app.schemas.query import AOI, DataInput
from app.schemas.raster import RasterData, RasterMetadata


def create_context() -> ExecutionContext:
    return ExecutionContext(
        aoi=AOI(
            type="place",
            value="Pune",
        ),
        inputs=[
            DataInput(
                id="satellite_data",
                source="mock-satellite",
                purpose="test imagery",
            )
        ],
    )


def create_raster(
    red: np.ndarray,
    nir: np.ndarray,
) -> RasterData:
    data = np.stack([red, nir])

    return RasterData(
        data=data,
        bands=["B4", "B8"],
        metadata=RasterMetadata(
            crs="EPSG:4326",
            width=red.shape[1],
            height=red.shape[0],
            count=2,
            dtype="float32",
        ),
    )


def test_ndvi_requires_one_input() -> None:
    context = create_context()

    operation = Operation(
        id="ndvi",
        type="calculate_ndvi",
        inputs=[],
        parameters={
            "red_band": "B4",
            "nir_band": "B8",
        },
    )

    with pytest.raises(
        ValueError,
        match="exactly one input",
    ):
        NDVIOperation().validate(operation, context)


def test_ndvi_requires_existing_input() -> None:
    context = create_context()

    operation = Operation(
        id="ndvi",
        type="calculate_ndvi",
        inputs=["missing"],
        parameters={
            "red_band": "B4",
            "nir_band": "B8",
        },
    )

    with pytest.raises(KeyError):
        NDVIOperation().validate(operation, context)


def test_ndvi_requires_band_parameters() -> None:
    context = create_context()

    operation = Operation(
        id="ndvi",
        type="calculate_ndvi",
        inputs=["satellite_data"],
        parameters={},
    )

    with pytest.raises(
        ValueError,
        match="Missing NDVI parameters",
    ):
        NDVIOperation().validate(operation, context)


def test_ndvi_calculation() -> None:
    operation = Operation(
        id="ndvi",
        type="calculate_ndvi",
        inputs=["satellite_data"],
        parameters={
            "red_band": "B4",
            "nir_band": "B8",
        },
    )

    red = np.array(
        [[0.2, 0.4]],
        dtype=np.float32,
    )

    nir = np.array(
        [[0.6, 0.8]],
        dtype=np.float32,
    )

    raster = create_raster(red, nir)

    result = NDVIOperation()._calculate(
        operation=operation,
        source_data=raster,
        red_band="B4",
        nir_band="B8",
    )

    expected = np.array(
        [[0.5, 0.33333334]],
        dtype=np.float32,
    )

    assert isinstance(result.data, RasterData)
    assert result.data.bands == ["NDVI"]
    assert result.data.data.shape == (1, 1, 2)

    np.testing.assert_allclose(
        result.data.data[0],
        expected,
        rtol=1e-5,
        atol=1e-5,
    )


def test_ndvi_handles_zero_denominator() -> None:
    operation = Operation(
        id="ndvi",
        type="calculate_ndvi",
        inputs=["satellite_data"],
        parameters={
            "red_band": "B4",
            "nir_band": "B8",
        },
    )

    red = np.array(
        [[0.0, 0.2]],
        dtype=np.float32,
    )

    nir = np.array(
        [[0.0, 0.2]],
        dtype=np.float32,
    )

    raster = create_raster(red, nir)

    result = NDVIOperation()._calculate(
        operation=operation,
        source_data=raster,
        red_band="B4",
        nir_band="B8",
    )

    assert result.data.data[0, 0, 0] == 0.0
    assert result.data.data[0, 0, 1] == 0.0


def test_ndvi_rejects_missing_red_band() -> None:
    operation = Operation(
        id="ndvi",
        type="calculate_ndvi",
        inputs=["satellite_data"],
        parameters={
            "red_band": "B4",
            "nir_band": "B8",
        },
    )

    raster = RasterData(
        data=np.zeros(
            (1, 2, 2),
            dtype=np.float32,
        ),
        bands=["B8"],
        metadata=RasterMetadata(
            crs="EPSG:4326",
            width=2,
            height=2,
            count=1,
            dtype="float32",
        ),
    )

    with pytest.raises(
        KeyError,
        match="Red band",
    ):
        NDVIOperation()._calculate(
            operation=operation,
            source_data=raster,
            red_band="B4",
            nir_band="B8",
        )


def test_ndvi_rejects_missing_nir_band() -> None:
    operation = Operation(
        id="ndvi",
        type="calculate_ndvi",
        inputs=["satellite_data"],
        parameters={
            "red_band": "B4",
            "nir_band": "B8",
        },
    )

    raster = RasterData(
        data=np.zeros(
            (1, 2, 2),
            dtype=np.float32,
        ),
        bands=["B4"],
        metadata=RasterMetadata(
            crs="EPSG:4326",
            width=2,
            height=2,
            count=1,
            dtype="float32",
        ),
    )

    with pytest.raises(
        KeyError,
        match="NIR band",
    ):
        NDVIOperation()._calculate(
            operation=operation,
            source_data=raster,
            red_band="B4",
            nir_band="B8",
        )


def test_ndvi_preserves_raster_metadata() -> None:
    operation = Operation(
        id="ndvi",
        type="calculate_ndvi",
        inputs=["satellite_data"],
        parameters={
            "red_band": "B4",
            "nir_band": "B8",
        },
    )

    red = np.ones(
        (2, 2),
        dtype=np.float32,
    )

    nir = np.ones(
        (2, 2),
        dtype=np.float32,
    )

    raster = RasterData(
        data=np.stack([red, nir]),
        bands=["B4", "B8"],
        metadata=RasterMetadata(
            crs="EPSG:32643",
            resolution=(10.0, 10.0),
            bounds=(73.0, 18.0, 73.1, 18.1),
            nodata=-9999.0,
            width=2,
            height=2,
            count=2,
            dtype="float32",
        ),
    )

    result = NDVIOperation()._calculate(
        operation=operation,
        source_data=raster,
        red_band="B4",
        nir_band="B8",
    )

    metadata = result.data.metadata

    assert metadata.crs == raster.metadata.crs
    assert metadata.resolution == raster.metadata.resolution
    assert metadata.bounds == raster.metadata.bounds
    assert metadata.nodata == raster.metadata.nodata
    assert metadata.width == raster.metadata.width
    assert metadata.height == raster.metadata.height
    assert metadata.count == 1
    
def test_ndvi_uses_runtime_raster_input() -> None:
    context = create_context()

    red = np.array(
        [[0.2, 0.4]],
        dtype=np.float32,
    )

    nir = np.array(
        [[0.6, 0.8]],
        dtype=np.float32,
    )

    raster = create_raster(red, nir)

    context.add_runtime_input(
        "satellite_data",
        raster,
    )

    operation = Operation(
        id="ndvi",
        type="calculate_ndvi",
        inputs=["satellite_data"],
        parameters={
            "red_band": "B4",
            "nir_band": "B8",
        },
    )

    result = NDVIOperation().execute(
        operation,
        context,
    )

    assert isinstance(result.data, RasterData)

    expected = np.array(
        [[0.5, 0.33333334]],
        dtype=np.float32,
    )

    np.testing.assert_allclose(
        result.data.data[0],
        expected,
        rtol=1e-5,
        atol=1e-5,
    )