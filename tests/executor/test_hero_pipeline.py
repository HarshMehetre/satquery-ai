import geopandas as gpd
import numpy as np
from rasterio.transform import from_bounds
from shapely.geometry import LineString

from app.executor.executor import Executor
from app.schemas.query import AOI, DataInput, OutputSpec, QueryPlan
from app.schemas.raster import RasterData, RasterMetadata
from tests.operations.registry import create_mock_registry

BBOX = [73.0, 18.0, 73.1, 18.1]
WIDTH = 4
HEIGHT = 4


def create_test_raster(ndvi_values: np.ndarray) -> RasterData:
    transform = from_bounds(
        BBOX[0],
        BBOX[1],
        BBOX[2],
        BBOX[3],
        WIDTH,
        HEIGHT,
    )

    red = np.full(
        (HEIGHT, WIDTH),
        0.4,
        dtype=np.float32,
    )

    nir = (
        red * (1 + ndvi_values) / (1 - ndvi_values)
    ).astype(np.float32)

    data = np.stack([red, nir], axis=0)

    metadata = RasterMetadata(
        crs="EPSG:4326",
        transform=transform,
        resolution=(
            (BBOX[2] - BBOX[0]) / WIDTH,
            (BBOX[3] - BBOX[1]) / HEIGHT,
        ),
        bounds=(
            BBOX[0],
            BBOX[1],
            BBOX[2],
            BBOX[3],
        ),
        width=WIDTH,
        height=HEIGHT,
        count=2,
        dtype="float32",
    )

    return RasterData(
        data=data,
        bands=["B4", "B8"],
        metadata=metadata,
    )


def create_test_roads() -> gpd.GeoDataFrame:
    return gpd.GeoDataFrame(
        {"highway": ["primary"]},
        geometry=[
            LineString(
                [
                    (73.0, 18.05),
                    (73.1, 18.05),
                ]
            )
        ],
        crs="EPSG:4326",
    )


def create_hero_plan() -> QueryPlan:
    return QueryPlan(
        plan_id="hero_001",
        aoi=AOI(
            type="bbox",
            value=BBOX,
        ),
        inputs=[
            DataInput(
                id="s2_2024",
                source="sentinel-2",
                purpose="vegetation baseline",
            ),
            DataInput(
                id="s2_2026",
                source="sentinel-2",
                purpose="vegetation comparison",
            ),
            DataInput(
                id="roads",
                source="osm",
                purpose="major roads",
            ),
        ],
        operations=[
            {
            "id": "s2_2024",
            "type": "get_satellite_imagery",
            "parameters": {
                "bbox": BBOX,
                "start_date": "2024-01-01",
                "end_date": "2024-12-31",
                "max_cloud_coverage": 30,
                "width": WIDTH,
                "height": HEIGHT,
                },
            },
            {
            "id": "s2_2026",
            "type": "get_satellite_imagery",
            "parameters": {
                "bbox": BBOX,
                "start_date": "2026-01-01",
                "end_date": "2026-12-31",
                "max_cloud_coverage": 30,
                "width": WIDTH,
                "height": HEIGHT,
                },
            },
            {
            "id": "roads",
            "type": "get_osm_features",
            "parameters": {
                "bbox": BBOX,
                "feature_type": "roads",
                },
            },
            {
            "id": "ndvi_2024",
            "type": "calculate_ndvi",
            "inputs": ["s2_2024"],
            "parameters": {
                "red_band": "B4",
                "nir_band": "B8",
                },
            },
            {
            "id": "ndvi_2026",
            "type": "calculate_ndvi",
            "inputs": ["s2_2026"],
            "parameters": {
                "red_band": "B4",
                "nir_band": "B8",
                },
            },
            {
                "id": "vegetation_change",
                "type": "temporal_difference",
                "inputs": [
                    "ndvi_2024",
                    "ndvi_2026",
                ],
            },
            {
                "id": "vegetation_loss",
                "type": "vegetation_loss",
                "inputs": ["vegetation_change"],
                "parameters": {
                    "threshold": -0.1,
                },
            },
            {
                "id": "loss_polygons",
                "type": "raster_polygonize",
                "inputs": ["vegetation_loss"],
            },
            {
                "id": "loss_projected",
                "type": "project_to_crs",
                "inputs": ["loss_polygons"],
                "parameters": {
                    "target_crs": "EPSG:32643",
                },
            },
            {
                "id": "roads_projected",
                "type": "project_to_crs",
                "inputs": ["roads"],
                "parameters": {
                    "target_crs": "EPSG:32643",
                },
            },
            {
                "id": "road_buffer",
                "type": "buffer",
                "inputs": ["roads_projected"],
                "parameters": {
                    "distance_m": 3000,
                },
            },
            {
                "id": "final",
                "type": "intersection",
                "inputs": [
                    "loss_projected",
                    "road_buffer",
                ],
            },
            {
                "id": "area",
                "type": "area",
                "inputs": ["final"],
            },
        ],
        output=OutputSpec(
            type="statistics",
            include_geometry=True,
            include_statistics=True,
            include_evidence=True,
        ),
    )


def test_hero_pipeline_executes_end_to_end() -> None:
    vegetation_2024 = np.full(
        (HEIGHT, WIDTH),
        0.6,
        dtype=np.float32,
    )

    vegetation_2026 = vegetation_2024.copy()
    vegetation_2026[1:3, 1:3] = 0.3

    raster_2024 = create_test_raster(vegetation_2024)
    raster_2026 = create_test_raster(vegetation_2026)
    roads = create_test_roads()

    runtime_inputs = {
        "s2_2024": raster_2024,
        "s2_2026": raster_2026,
        "roads": roads,
    }

    executor = Executor(
        registry=create_mock_registry(),
    )

    result = executor.execute(
        create_hero_plan(),
        runtime_inputs=runtime_inputs,
    )

    expected_operation_ids = {
    "s2_2024",
    "s2_2026",
    "roads",
    "ndvi_2024",
    "ndvi_2026",
    "vegetation_change",
    "vegetation_loss",
    "loss_polygons",
    "loss_projected",
    "roads_projected",
    "road_buffer",
    "final",
    "area",
    }

    assert set(result.results) == expected_operation_ids

    ndvi_2024 = result.results["ndvi_2024"]
    ndvi_2026 = result.results["ndvi_2026"]

    assert ndvi_2024.data_type == "raster"
    assert ndvi_2026.data_type == "raster"

    change = result.results["vegetation_change"]

    assert change.data_type == "raster"
    assert change.data.data.shape == (1, HEIGHT, WIDTH)

    vegetation_loss = result.results["vegetation_loss"]

    assert vegetation_loss.data_type == "raster"
    assert vegetation_loss.data.data.shape == (1, HEIGHT, WIDTH)

    loss_polygons = result.results["loss_polygons"]

    assert loss_polygons.data_type == "vector"
    assert isinstance(
        loss_polygons.data,
        gpd.GeoDataFrame,
    )
    assert not loss_polygons.data.empty

    loss_projected = result.results["loss_projected"]
    roads_projected = result.results["roads_projected"]

    assert loss_projected.data_type == "vector"
    assert roads_projected.data_type == "vector"

    assert loss_projected.data.crs.to_epsg() == 32643
    assert roads_projected.data.crs.to_epsg() == 32643

    road_buffer = result.results["road_buffer"]

    assert road_buffer.data_type == "vector"
    assert not road_buffer.data.empty

    final = result.results["final"]

    assert final.data_type == "vector"
    assert not final.data.empty
    assert final.data.crs.to_epsg() == 32643

    area = result.results["area"]

    assert area.data_type == "scalar"
    assert isinstance(area.data, float)
    assert area.data > 0