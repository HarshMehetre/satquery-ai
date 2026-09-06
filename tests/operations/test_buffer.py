import geopandas as gpd
import pytest
from shapely.geometry import LineString

from app.executor.context import ExecutionContext
from app.operations.gis.buffer import BufferOperation
from app.schemas.operation import Operation
from app.schemas.query import AOI
from app.schemas.result import OperationResult


def create_context() -> ExecutionContext:
    return ExecutionContext(
        aoi=AOI(
            type="bbox",
            value=[73.80, 18.45, 73.90, 18.55],
        )
    )


def create_operation(
    input_id: str = "roads",
    distance_m: int = 3000,
) -> Operation:
    return Operation(
        id="road_buffer",
        type="buffer",
        inputs=[input_id],
        parameters={
            "distance_m": distance_m,
        },
    )


def add_road_result(context: ExecutionContext) -> None:
    roads = gpd.GeoDataFrame(
        {
            "highway": ["primary"],
            "geometry": [
                LineString(
                    [
                        (0, 0),
                        (100, 0),
                    ]
                )
            ],
        },
        crs="EPSG:32643",
    )

    context.add_result(
        OperationResult(
            id="roads",
            type="project_to_crs",
            data_type="vector",
            data=roads,
        )
    )


def test_buffer_requires_exactly_one_input() -> None:
    operation = Operation(
        id="road_buffer",
        type="buffer",
        inputs=[],
        parameters={"distance_m": 3000},
    )

    with pytest.raises(ValueError, match="exactly one input"):
        BufferOperation().validate(
            operation,
            create_context(),
        )


def test_buffer_requires_distance() -> None:
    operation = Operation(
        id="road_buffer",
        type="buffer",
        inputs=["roads"],
        parameters={},
    )

    with pytest.raises(ValueError, match="distance_m"):
        BufferOperation().validate(
            operation,
            create_context(),
        )


def test_buffer_rejects_negative_distance() -> None:
    operation = create_operation(distance_m=-100)

    with pytest.raises(ValueError, match="cannot be negative"):
        BufferOperation().validate(
            operation,
            create_context(),
        )


def test_buffer_rejects_non_numeric_distance() -> None:
    operation = Operation(
        id="road_buffer",
        type="buffer",
        inputs=["roads"],
        parameters={
            "distance_m": "3000",
        },
    )

    with pytest.raises(TypeError, match="must be a number"):
        BufferOperation().validate(
            operation,
            create_context(),
        )


def test_buffer_requires_vector_input() -> None:
    context = create_context()

    context.add_result(
        OperationResult(
            id="raster",
            type="mock",
            data_type="raster",
            data="not-a-vector",
        )
    )

    operation = create_operation(input_id="raster")

    with pytest.raises(TypeError, match="vector input"):
        BufferOperation().execute(
            operation,
            context,
        )


def test_buffer_requires_geodataframe() -> None:
    context = create_context()

    context.add_result(
        OperationResult(
            id="roads",
            type="mock",
            data_type="vector",
            data="not-a-geodataframe",
        )
    )

    operation = create_operation()

    with pytest.raises(TypeError, match="GeoDataFrame"):
        BufferOperation().execute(
            operation,
            context,
        )


def test_buffer_creates_buffer_geometry() -> None:
    context = create_context()
    add_road_result(context)

    operation = create_operation(distance_m=3000)

    result = BufferOperation().execute(
        operation,
        context,
    )

    assert result.data_type == "vector"
    assert isinstance(result.data, gpd.GeoDataFrame)

    assert len(result.data) == 1
    assert result.data.crs.to_epsg() == 32643

    geometry = result.data.geometry.iloc[0]

    assert geometry.geom_type == "Polygon"
    assert geometry.area > 0

    assert result.metadata["operation"] == "buffer"
    assert result.metadata["distance_m"] == 3000.0
    assert result.metadata["feature_count"] == 1
    assert result.metadata["crs"] == str(result.data.crs)