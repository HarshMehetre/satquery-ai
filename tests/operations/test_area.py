import geopandas as gpd
import pytest
from shapely.geometry import box

from app.executor.context import ExecutionContext
from app.operations.gis.area import AreaOperation
from app.schemas.operation import Operation
from app.schemas.query import AOI
from app.schemas.result import OperationResult


def create_context() -> ExecutionContext:
    return ExecutionContext(
        aoi=AOI(
            type="bbox",
            value=[0, 0, 10, 10],
        )
    )


def create_operation(
    input_id: str = "intersection",
) -> Operation:
    return Operation(
        id="area",
        type="area",
        inputs=[input_id],
        parameters={},
    )


def add_vector_result(
    context: ExecutionContext,
    crs: str = "EPSG:32643",
) -> None:
    geometry = gpd.GeoDataFrame(
        {
            "class": ["affected", "affected"],
            "geometry": [
                box(0, 0, 100, 100),
                box(200, 200, 300, 300),
            ],
        },
        crs=crs,
    )

    context.add_result(
        OperationResult(
            id="intersection",
            type="intersection",
            data_type="vector",
            data=geometry,
        )
    )


def test_area_requires_exactly_one_input() -> None:
    operation = Operation(
        id="area",
        type="area",
        inputs=[],
        parameters={},
    )

    with pytest.raises(ValueError, match="exactly one input"):
        AreaOperation().validate(
            operation,
            create_context(),
        )


def test_area_requires_vector_input() -> None:
    context = create_context()

    context.add_result(
        OperationResult(
            id="raster",
            type="mock",
            data_type="raster",
            data="not-a-vector",
        )
    )

    operation = create_operation("raster")

    with pytest.raises(TypeError, match="vector input"):
        AreaOperation().execute(
            operation,
            context,
        )


def test_area_requires_geodataframe() -> None:
    context = create_context()

    context.add_result(
        OperationResult(
            id="intersection",
            type="mock",
            data_type="vector",
            data="not-a-geodataframe",
        )
    )

    operation = create_operation()

    with pytest.raises(TypeError, match="GeoDataFrame"):
        AreaOperation().execute(
            operation,
            context,
        )


def test_area_requires_crs() -> None:
    context = create_context()

    geometry = gpd.GeoDataFrame(
        geometry=[box(0, 0, 100, 100)],
    )

    context.add_result(
        OperationResult(
            id="intersection",
            type="mock",
            data_type="vector",
            data=geometry,
        )
    )

    operation = create_operation()

    with pytest.raises(ValueError, match="input CRS"):
        AreaOperation().execute(
            operation,
            context,
        )


def test_area_rejects_geographic_crs() -> None:
    context = create_context()

    add_vector_result(
        context,
        crs="EPSG:4326",
    )

    operation = create_operation()

    with pytest.raises(
        ValueError,
        match="projected CRS",
    ):
        AreaOperation().execute(
            operation,
            context,
        )


def test_area_calculates_total_area() -> None:
    context = create_context()
    add_vector_result(context)

    operation = create_operation()

    result = AreaOperation().execute(
        operation,
        context,
    )

    assert result.data_type == "scalar"

    # Two 100 m × 100 m polygons.
    assert result.data == pytest.approx(20_000.0)

    assert result.metadata["operation"] == "area"
    assert result.metadata["unit"] == "m²"
    assert result.metadata["feature_count"] == 2
    assert result.metadata["area_m2"] == pytest.approx(20_000.0)
    assert result.metadata["area_km2"] == pytest.approx(0.02)
    assert result.metadata["crs"] == "EPSG:32643"