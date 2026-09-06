import geopandas as gpd
import pytest
from shapely.geometry import LineString

from app.executor.context import ExecutionContext
from app.operations.gis.project import ProjectToCRSOperation
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
    target_crs: str = "EPSG:32643",
) -> Operation:
    return Operation(
        id="projected_roads",
        type="project_to_crs",
        inputs=[input_id],
        parameters={
            "target_crs": target_crs,
        },
    )


def add_road_result(context: ExecutionContext) -> None:
    roads = gpd.GeoDataFrame(
        {
            "highway": ["primary"],
            "geometry": [
                LineString(
                    [
                        (73.80, 18.45),
                        (73.90, 18.55),
                    ]
                )
            ],
        },
        crs="EPSG:4326",
    )

    context.add_result(
        OperationResult(
            id="roads",
            type="get_osm_features",
            data_type="vector",
            data=roads,
        )
    )


def test_project_requires_exactly_one_input() -> None:
    operation = Operation(
        id="projected_roads",
        type="project_to_crs",
        inputs=[],
        parameters={"target_crs": "EPSG:32643"},
    )

    with pytest.raises(ValueError, match="exactly one input"):
        ProjectToCRSOperation().validate(
            operation,
            create_context(),
        )


def test_project_requires_target_crs() -> None:
    operation = Operation(
        id="projected_roads",
        type="project_to_crs",
        inputs=["roads"],
        parameters={},
    )

    with pytest.raises(ValueError, match="target_crs"):
        ProjectToCRSOperation().validate(
            operation,
            create_context(),
        )


def test_project_requires_vector_input() -> None:
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
        ProjectToCRSOperation().execute(
            operation,
            context,
        )


def test_project_reprojects_geometry() -> None:
    context = create_context()
    add_road_result(context)

    operation = create_operation()

    result = ProjectToCRSOperation().execute(
        operation,
        context,
    )

    assert result.data_type == "vector"
    assert isinstance(result.data, gpd.GeoDataFrame)
    assert result.data.crs.to_epsg() == 32643
    assert result.metadata["source_crs"] == "EPSG:4326"
    assert result.metadata["target_crs"] == "EPSG:32643"
    assert result.metadata["feature_count"] == 1

    geometry = result.data.geometry.iloc[0]

    assert geometry.length > 0
    assert geometry.length != 0.1