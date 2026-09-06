import geopandas as gpd
import pytest
from shapely.geometry import box

from app.executor.context import ExecutionContext
from app.operations.gis.intersection import IntersectionOperation
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
    first_id: str = "vegetation_loss",
    second_id: str = "road_buffer",
) -> Operation:
    return Operation(
        id="intersection",
        type="intersection",
        inputs=[first_id, second_id],
        parameters={},
    )


def add_vector_results(
    context: ExecutionContext,
) -> None:
    vegetation = gpd.GeoDataFrame(
        {
            "class": ["vegetation_loss"],
            "geometry": [
                box(0, 0, 10, 10),
            ],
        },
        crs="EPSG:32643",
    )

    road_buffer = gpd.GeoDataFrame(
        {
            "class": ["road_buffer"],
            "geometry": [
                box(5, -5, 15, 5),
            ],
        },
        crs="EPSG:32643",
    )

    context.add_result(
        OperationResult(
            id="vegetation_loss",
            type="mock",
            data_type="vector",
            data=vegetation,
        )
    )

    context.add_result(
        OperationResult(
            id="road_buffer",
            type="mock",
            data_type="vector",
            data=road_buffer,
        )
    )


def test_intersection_requires_two_inputs() -> None:
    operation = Operation(
        id="intersection",
        type="intersection",
        inputs=["vegetation_loss"],
        parameters={},
    )

    with pytest.raises(ValueError, match="exactly two inputs"):
        IntersectionOperation().validate(
            operation,
            create_context(),
        )


def test_intersection_rejects_non_vector_first_input() -> None:
    context = create_context()

    context.add_result(
        OperationResult(
            id="raster",
            type="mock",
            data_type="raster",
            data="not-a-vector",
        )
    )

    context.add_result(
        OperationResult(
            id="vector",
            type="mock",
            data_type="vector",
            data=gpd.GeoDataFrame(
                geometry=[],
                crs="EPSG:32643",
            ),
        )
    )

    operation = create_operation(
        first_id="raster",
        second_id="vector",
    )

    with pytest.raises(TypeError, match="vector inputs"):
        IntersectionOperation().execute(
            operation,
            context,
        )


def test_intersection_rejects_non_vector_second_input() -> None:
    context = create_context()

    context.add_result(
        OperationResult(
            id="vector",
            type="mock",
            data_type="vector",
            data=gpd.GeoDataFrame(
                geometry=[],
                crs="EPSG:32643",
            ),
        )
    )

    context.add_result(
        OperationResult(
            id="raster",
            type="mock",
            data_type="raster",
            data="not-a-vector",
        )
    )

    operation = create_operation(
        first_id="vector",
        second_id="raster",
    )

    with pytest.raises(TypeError, match="vector inputs"):
        IntersectionOperation().execute(
            operation,
            context,
        )


def test_intersection_rejects_non_geodataframe() -> None:
    context = create_context()

    context.add_result(
        OperationResult(
            id="first",
            type="mock",
            data_type="vector",
            data="not-a-geodataframe",
        )
    )

    context.add_result(
        OperationResult(
            id="second",
            type="mock",
            data_type="vector",
            data=gpd.GeoDataFrame(
                geometry=[],
                crs="EPSG:32643",
            ),
        )
    )

    operation = create_operation(
        first_id="first",
        second_id="second",
    )

    with pytest.raises(TypeError, match="GeoDataFrame inputs"):
        IntersectionOperation().execute(
            operation,
            context,
        )


def test_intersection_rejects_mismatched_crs() -> None:
    context = create_context()

    first = gpd.GeoDataFrame(
        geometry=[box(0, 0, 10, 10)],
        crs="EPSG:32643",
    )

    second = gpd.GeoDataFrame(
        geometry=[box(5, -5, 15, 5)],
        crs="EPSG:4326",
    )

    context.add_result(
        OperationResult(
            id="first",
            type="mock",
            data_type="vector",
            data=first,
        )
    )

    context.add_result(
        OperationResult(
            id="second",
            type="mock",
            data_type="vector",
            data=second,
        )
    )

    operation = create_operation(
        first_id="first",
        second_id="second",
    )

    with pytest.raises(ValueError, match="same CRS"):
        IntersectionOperation().execute(
            operation,
            context,
        )


def test_intersection_creates_intersected_geometry() -> None:
    context = create_context()
    add_vector_results(context)

    operation = create_operation()

    result = IntersectionOperation().execute(
        operation,
        context,
    )

    assert result.data_type == "vector"
    assert isinstance(result.data, gpd.GeoDataFrame)

    assert len(result.data) == 1
    assert result.data.crs.to_epsg() == 32643

    geometry = result.data.geometry.iloc[0]

    assert geometry.geom_type == "Polygon"
    assert geometry.area == pytest.approx(25.0)

    assert result.metadata["operation"] == "intersection"
    assert result.metadata["input_count"] == 2
    assert result.metadata["feature_count"] == 1
    assert result.metadata["crs"] == str(result.data.crs)