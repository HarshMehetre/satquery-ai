import numpy as np
import pytest
from rasterio.transform import from_origin

from app.executor.context import ExecutionContext
from app.operations.remote_sensing.polygonize import RasterPolygonizeOperation
from app.schemas.operation import Operation
from app.schemas.query import AOI
from app.schemas.raster import RasterData, RasterMetadata
from app.schemas.result import OperationResult


def create_raster(
    data: np.ndarray,
    transform=None,
    crs: str = "EPSG:32643",
) -> RasterData:
    if transform is None:
        transform = from_origin(
            500000,
            2000,
            10,
            10,
        )

    return RasterData(
        data=np.asarray(data, dtype=np.uint8),
        bands=["VEGETATION_LOSS"],
        metadata=RasterMetadata(
            crs=crs,
            transform=transform,
            width=data.shape[-1],
            height=data.shape[-2],
            count=data.shape[0],
            dtype="uint8",
            nodata=0,
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
            id="vegetation_loss",
            type="vegetation_loss",
            data_type="raster",
            data=raster,
        )
    )

    return context


def create_operation() -> Operation:
    return Operation(
        id="vegetation_loss_polygons",
        type="raster_polygonize",
        inputs=["vegetation_loss"],
    )


def test_polygonize_requires_one_input() -> None:
    operation = Operation(
        id="vegetation_loss_polygons",
        type="raster_polygonize",
    )

    context = ExecutionContext(
        aoi=AOI(
            type="bbox",
            value=[73.80, 18.45, 73.90, 18.55],
        )
    )

    with pytest.raises(ValueError, match="exactly one input"):
        RasterPolygonizeOperation().validate(operation, context)


def test_polygonize_requires_raster_input() -> None:
    operation = create_operation()

    context = ExecutionContext(
        aoi=AOI(
            type="bbox",
            value=[73.80, 18.45, 73.90, 18.55],
        )
    )

    context.add_result(
        OperationResult(
            id="vegetation_loss",
            type="mock",
            data_type="scalar",
            data=1,
        )
    )

    with pytest.raises(TypeError, match="raster input"):
        RasterPolygonizeOperation().execute(operation, context)


def test_polygonize_requires_raster_data() -> None:
    operation = create_operation()

    context = ExecutionContext(
        aoi=AOI(
            type="bbox",
            value=[73.80, 18.45, 73.90, 18.55],
        )
    )

    context.add_result(
        OperationResult(
            id="vegetation_loss",
            type="mock",
            data_type="raster",
            data=np.ones((1, 2, 2), dtype=np.uint8),
        )
    )

    with pytest.raises(TypeError, match="RasterData input"):
        RasterPolygonizeOperation().execute(operation, context)


def test_polygonize_requires_single_band() -> None:
    raster = create_raster(
        np.ones((2, 2, 2), dtype=np.uint8),
    )

    context = create_context(raster)

    with pytest.raises(ValueError, match="single-band"):
        RasterPolygonizeOperation().execute(
            create_operation(),
            context,
        )


def test_polygonize_requires_transform() -> None:
    raster = RasterData(
        data=np.ones((1, 2, 2), dtype=np.uint8),
        bands=["VEGETATION_LOSS"],
        metadata=RasterMetadata(
            crs="EPSG:32643",
            transform=None,
            width=2,
            height=2,
            count=1,
            dtype="uint8",
            nodata=0,
        ),
    )

    context = create_context(raster)

    with pytest.raises(ValueError, match="transform metadata"):
        RasterPolygonizeOperation().execute(
            create_operation(),
            context,
        )


def test_polygonize_extracts_loss_polygons() -> None:
    data = np.array(
        [
            [
                [1, 1, 0],
                [1, 1, 0],
                [0, 0, 0],
            ]
        ],
        dtype=np.uint8,
    )

    raster = create_raster(data)
    context = create_context(raster)

    result = RasterPolygonizeOperation().execute(
        create_operation(),
        context,
    )

    polygons = result.data

    assert result.data_type == "vector"
    assert len(polygons) == 1
    assert polygons.geometry.iloc[0].geom_type == "Polygon"
    assert polygons["class"].iloc[0] == "vegetation_loss"
    assert polygons["value"].iloc[0] == 1


def test_polygonize_preserves_crs() -> None:
    data = np.array(
        [[[1, 0], [0, 1]]],
        dtype=np.uint8,
    )

    raster = create_raster(data, crs="EPSG:32643")
    context = create_context(raster)

    result = RasterPolygonizeOperation().execute(
        create_operation(),
        context,
    )

    assert result.data.crs.to_string() == "EPSG:32643"


def test_polygonize_preserves_spatial_scale() -> None:
    data = np.array(
        [
            [
                [1, 1],
                [1, 1],
            ]
        ],
        dtype=np.uint8,
    )

    raster = create_raster(
        data,
        transform=from_origin(
            500000,
            2000,
            10,
            10,
        ),
    )

    context = create_context(raster)

    result = RasterPolygonizeOperation().execute(
        create_operation(),
        context,
    )

    polygons = result.data

    # Four 10 m × 10 m pixels form one 20 m × 20 m polygon.
    assert polygons.geometry.iloc[0].area == pytest.approx(400.0)


def test_polygonize_ignores_non_loss_pixels() -> None:
    data = np.array(
        [
            [
                [0, 0],
                [0, 0],
            ]
        ],
        dtype=np.uint8,
    )

    raster = create_raster(data)
    context = create_context(raster)

    result = RasterPolygonizeOperation().execute(
        create_operation(),
        context,
    )

    assert len(result.data) == 0


def test_polygonize_metadata() -> None:
    data = np.array(
        [
            [
                [1, 1],
                [0, 0],
            ]
        ],
        dtype=np.uint8,
    )

    raster = create_raster(data)
    context = create_context(raster)

    result = RasterPolygonizeOperation().execute(
        create_operation(),
        context,
    )

    assert result.metadata["operation"] == "raster_polygonize"
    assert result.metadata["input"] == "vegetation_loss"
    assert result.metadata["feature_count"] == 1
    assert result.metadata["crs"] == "EPSG:32643"