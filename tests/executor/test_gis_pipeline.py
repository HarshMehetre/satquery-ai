import geopandas as gpd
import osmnx as ox
from shapely.geometry import LineString

from app.executor.executor import Executor
from app.operations.gis.buffer import BufferOperation
from app.operations.gis.osm import OSMRetrievalOperation
from app.operations.gis.project import ProjectToCRSOperation
from app.registry.operations import OperationRegistry
from app.schemas.operation import Operation
from app.schemas.query import AOI, DataInput, OutputSpec, QueryPlan


def create_registry() -> OperationRegistry:
    registry = OperationRegistry()

    registry.register(
        "get_osm_features",
        OSMRetrievalOperation,
    )
    registry.register(
        "project_to_crs",
        ProjectToCRSOperation,
    )
    registry.register(
        "buffer",
        BufferOperation,
    )

    return registry


def test_osm_project_buffer_pipeline(
    monkeypatch,
) -> None:
    roads = gpd.GeoDataFrame(
        {
            "highway": ["primary", "secondary"],
            "geometry": [
                LineString(
                    [
                        (73.80, 18.45),
                        (73.85, 18.50),
                    ]
                ),
                LineString(
                    [
                        (73.85, 18.50),
                        (73.90, 18.55),
                    ]
                ),
            ],
        },
        crs="EPSG:4326",
    )

    def mock_features_from_bbox(*, bbox, tags):
        assert bbox == (73.80, 18.45, 73.90, 18.55)
        assert tags == {"highway": True}
        return roads

    monkeypatch.setattr(
        ox,
        "features_from_bbox",
        mock_features_from_bbox,
    )

    plan = QueryPlan(
        plan_id="gis_pipeline_test",
        aoi=AOI(
            type="bbox",
            value=[73.80, 18.45, 73.90, 18.55],
        ),
        inputs=[
            DataInput(
                id="roads",
                source="openstreetmap",
                purpose="major roads",
            )
        ],
        operations=[
            Operation(
                id="roads",
                type="get_osm_features",
                parameters={
                    "feature_type": "roads",
                    "bbox": [73.80, 18.45, 73.90, 18.55],
                },
            ),
            Operation(
                id="projected_roads",
                type="project_to_crs",
                inputs=["roads"],
                parameters={
                    "target_crs": "EPSG:32643",
                },
            ),
            Operation(
                id="road_buffer",
                type="buffer",
                inputs=["projected_roads"],
                parameters={
                    "distance_m": 3000,
                },
            ),
        ],
        output=OutputSpec(
            type="map",
            include_geometry=True,
            include_statistics=True,
            include_evidence=True,
        ),
    )

    result = Executor(
        registry=create_registry(),
    ).execute(plan)

    assert set(result.results) == {
        "roads",
        "projected_roads",
        "road_buffer",
    }

    osm_result = result.results["roads"]
    projected_result = result.results["projected_roads"]
    buffer_result = result.results["road_buffer"]

    assert osm_result.data_type == "vector"
    assert projected_result.data_type == "vector"
    assert buffer_result.data_type == "vector"

    assert isinstance(
        osm_result.data,
        gpd.GeoDataFrame,
    )
    assert isinstance(
        projected_result.data,
        gpd.GeoDataFrame,
    )
    assert isinstance(
        buffer_result.data,
        gpd.GeoDataFrame,
    )

    assert osm_result.data.crs.to_epsg() == 4326
    assert projected_result.data.crs.to_epsg() == 32643
    assert buffer_result.data.crs.to_epsg() == 32643

    assert len(osm_result.data) == 2
    assert len(projected_result.data) == 2
    assert len(buffer_result.data) == 2

    assert all(
        geometry.geom_type == "Polygon"
        for geometry in buffer_result.data.geometry
    )

    assert all(
        geometry.area > 0
        for geometry in buffer_result.data.geometry
    )

    assert (
        buffer_result.metadata["distance_m"]
        == 3000.0
    )