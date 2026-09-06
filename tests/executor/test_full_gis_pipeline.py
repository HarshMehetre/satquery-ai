import geopandas as gpd
from pyproj import Transformer
from shapely.geometry import box

from app.executor.executor import Executor
from app.schemas.operation import Operation
from app.schemas.query import AOI, DataInput, OutputSpec, QueryPlan
from app.schemas.result import OperationResult
from tests.operations.registry import create_mock_registry


def create_vegetation_loss_gdf() -> gpd.GeoDataFrame:
    """Create deterministic vegetation-loss polygons near the mock roads."""
    transformer = Transformer.from_crs(
        "EPSG:4326",
        "EPSG:32643",
        always_xy=True,
    )

    x1, y1 = transformer.transform(73.805, 18.455)
    x2, y2 = transformer.transform(73.825, 18.475)

    return gpd.GeoDataFrame(
        {
            "class": ["vegetation_loss", "vegetation_loss"],
            "geometry": [
                box(x1 - 250, y1 - 250, x1 + 250, y1 + 250),
                box(x2 - 250, y2 - 250, x2 + 250, y2 + 250),
            ],
        },
        crs="EPSG:32643",
    )


def test_full_gis_pipeline(monkeypatch) -> None:
    registry = create_mock_registry()

    osm_operation = Operation(
        id="osm_roads",
        type="get_osm_features",
        parameters={
            "feature_type": "roads",
            "bbox": [73.80, 18.45, 73.90, 18.55],
        },
    )

    project_operation = Operation(
        id="projected_roads",
        type="project_to_crs",
        inputs=["osm_roads"],
        parameters={
            "target_crs": "EPSG:32643",
        },
    )

    buffer_operation = Operation(
        id="road_buffer",
        type="buffer",
        inputs=["projected_roads"],
        parameters={
            "distance_m": 3000,
        },
    )

    intersection_operation = Operation(
        id="affected_near_roads",
        type="intersection",
        inputs=["road_buffer", "vegetation_loss"],
    )

    area_operation = Operation(
        id="affected_area",
        type="area",
        inputs=["affected_near_roads"],
    )

    plan = QueryPlan(
        plan_id="full_gis_pipeline",
        aoi=AOI(
            type="bbox",
            value=[73.80, 18.45, 73.90, 18.55],
        ),
        inputs=[
            DataInput(
                id="vegetation_loss",
                source="runtime",
                purpose="vegetation loss polygons",
            )
        ],
        operations=[
            osm_operation,
            project_operation,
            buffer_operation,
            intersection_operation,
            area_operation,
        ],
        output=OutputSpec(
            type="statistics",
            include_geometry=True,
            include_statistics=True,
            include_evidence=True,
        ),
    )

    vegetation_loss = create_vegetation_loss_gdf()

    def mock_features_from_bbox(*args, **kwargs):
        return gpd.GeoDataFrame(
            {
                "highway": ["primary", "secondary"],
                "geometry": [
                    box(73.80, 18.45, 73.81, 18.46),
                    box(73.82, 18.47, 73.83, 18.48),
                ],
            },
            crs="EPSG:4326",
        )

    import app.operations.gis.osm as osm_module

    monkeypatch.setattr(
        osm_module.ox,
        "features_from_bbox",
        mock_features_from_bbox,
    )

    executor = Executor(registry)

    result = executor.execute(
        plan,
        runtime_inputs={
            "vegetation_loss": OperationResult(
                id="vegetation_loss",
                type="runtime_input",
                data_type="vector",
                data=vegetation_loss,
            )
        },
    )

    assert set(result.results) == {
        "osm_roads",
        "projected_roads",
        "road_buffer",
        "affected_near_roads",
        "affected_area",
    }

    projected_roads = result.results["projected_roads"].data
    road_buffer = result.results["road_buffer"].data
    intersection = result.results["affected_near_roads"].data
    area = result.results["affected_area"]

    assert projected_roads.crs.to_string() == "EPSG:32643"
    assert road_buffer.crs.to_string() == "EPSG:32643"

    assert len(projected_roads) == 2
    assert len(road_buffer) == 2

    assert all(
        geometry.geom_type == "Polygon"
        for geometry in road_buffer.geometry
    )

    assert intersection.crs.to_string() == "EPSG:32643"
    assert len(intersection) > 0

    assert area.data_type == "scalar"
    assert area.data > 0
    assert area.metadata["unit"] == "m²"
    assert area.metadata["area_m2"] == area.data
    assert area.metadata["area_km2"] > 0
