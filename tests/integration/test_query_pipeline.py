from __future__ import annotations

import geopandas as gpd
import numpy as np
from rasterio.transform import from_bounds
from shapely.geometry import LineString

from app.executor.executor import Executor
from app.planner.service import QueryService
from app.planner.validator import QueryPlanValidator
from app.schemas.operation import Operation
from app.schemas.query import (
    AOI,
    DataInput,
    OutputSpec,
    QueryPlan,
    TimeRange,
)
from app.schemas.raster import RasterData, RasterMetadata
from tests.operations.registry import create_mock_registry


class StubHeroPlanner:
    """Deterministic planner used to exercise the production query pipeline."""

    def plan(self, query: str) -> QueryPlan:
        assert query == (
            "Find areas where vegetation decreased between 2024 and 2026 "
            "that are within 3 km of major roads."
        )

        return QueryPlan(
            plan_id="hero-query",
            aoi=AOI(
                type="bbox",
                value=[73.0, 18.0, 73.1, 18.1],
                resolved=True,
            ),
            inputs=[
                DataInput(
                    id="s2_2024",
                    source="sentinel-2",
                    purpose="2024 satellite imagery",
                    time_range=TimeRange(
                        start="2024-01-01",
                        end="2024-12-31",
                    ),
                ),
                DataInput(
                    id="s2_2026",
                    source="sentinel-2",
                    purpose="2026 satellite imagery",
                    time_range=TimeRange(
                        start="2026-01-01",
                        end="2026-12-31",
                    ),
                ),
                DataInput(
                    id="roads",
                    source="osm",
                    purpose="major roads",
                ),
            ],
            operations=[
                Operation(
                    id="s2_2024_data",
                    type="get_satellite_imagery",
                    parameters={
                        "input_id": "s2_2024",
                    },
                ),
                Operation(
                    id="s2_2026_data",
                    type="get_satellite_imagery",
                    parameters={
                        "input_id": "s2_2026",
                    },
                ),
                Operation(
                    id="roads_data",
                    type="get_osm_features",
                    parameters={
                        "input_id": "roads",
                    },
                ),
                Operation(
                    id="ndvi_2024",
                    type="calculate_ndvi",
                    inputs=["s2_2024_data"],
                    parameters={
                        "red_band": "B4",
                        "nir_band": "B8",
                    },
                ),
                Operation(
                    id="ndvi_2026",
                    type="calculate_ndvi",
                    inputs=["s2_2026_data"],
                    parameters={
                        "red_band": "B4",
                        "nir_band": "B8",
                    },
                ),
                Operation(
                    id="vegetation_change",
                    type="temporal_difference",
                    inputs=["ndvi_2024", "ndvi_2026"],
                    parameters={
                        "direction": "decrease",
                    },
                ),
                Operation(
                    id="vegetation_loss",
                    type="vegetation_loss",
                    inputs=["vegetation_change"],
                    parameters={
                        "threshold": 0.1,
                    },
                ),
                Operation(
                    id="loss_polygons",
                    type="raster_polygonize",
                    inputs=["vegetation_loss"],
                ),
                Operation(
                    id="loss_projected",
                    type="project_to_crs",
                    inputs=["loss_polygons"],
                    parameters={
                        "target_crs": "EPSG:32643",
                    },
                ),
                Operation(
                    id="roads_projected",
                    type="project_to_crs",
                    inputs=["roads_data"],
                    parameters={
                        "target_crs": "EPSG:32643",
                    },
                ),
                Operation(
                    id="road_buffer",
                    type="buffer",
                    inputs=["roads_projected"],
                    parameters={
                        "distance_m": 3000,
                    },
                ),
                Operation(
                    id="final",
                    type="intersection",
                    inputs=["loss_projected", "road_buffer"],
                ),
                Operation(
                    id="area",
                    type="area",
                    inputs=["final"],
                ),
            ],
            output=OutputSpec(
                type="map",
                include_geometry=True,
                include_statistics=True,
                include_evidence=True,
            ),
        )


def _create_synthetic_raster(changed: bool = False) -> RasterData:
    """Create synthetic Sentinel-2 B4/B8 imagery."""
    

    red = np.full((4, 4), 0.2, dtype=np.float32)
    nir = np.full((4, 4), 0.8, dtype=np.float32)

    if changed:
        red[1:3, 1:3] = 0.5
        nir[1:3, 1:3] = 0.25
        
    transform = from_bounds(
        73.0,
        18.0,
        73.1,
        18.1,
        4,
        4,
    )

    metadata = RasterMetadata(
    crs="EPSG:4326",
    transform=transform,
    resolution=(0.025, 0.025),
    bounds=(73.0, 18.0, 73.1, 18.1),
    width=4,
    height=4,
    count=2,
    dtype="float32",
    )

    return RasterData(
        data=np.stack([red, nir]),
        bands=["B4", "B8"],
        metadata=metadata,
    )


def _create_roads() -> gpd.GeoDataFrame:
    """Create synthetic major-road geometry crossing the AOI."""

    return gpd.GeoDataFrame(
        {
            "highway": ["primary"],
            "geometry": [
                LineString(
                    [
                        (73.0, 18.05),
                        (73.1, 18.05),
                    ]
                )
            ],
        },
        crs="EPSG:4326",
    )


def test_query_service_executes_hero_query_end_to_end():
    planner = StubHeroPlanner()

    registry = create_mock_registry()
    validator = QueryPlanValidator(registry)

    service = QueryService(
        planner=planner,
        validator=validator,
        executor=Executor(registry),
    )

    result = service.execute(
        "Find areas where vegetation decreased between 2024 and 2026 "
        "that are within 3 km of major roads.",
        runtime_inputs={
            "s2_2024_data": _create_synthetic_raster(),
            "s2_2026_data": _create_synthetic_raster(changed=True),
            "roads_data": _create_roads(),
        },
    )

    expected_operations = {
        "s2_2024_data",
        "s2_2026_data",
        "roads_data",
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

    assert expected_operations.issubset(result.results.keys())

    assert result.results["s2_2024_data"].data_type == "raster"
    assert result.results["s2_2026_data"].data_type == "raster"
    assert result.results["roads_data"].data_type == "vector"

    assert result.results["ndvi_2024"].data_type == "raster"
    assert result.results["ndvi_2026"].data_type == "raster"
    assert result.results["vegetation_change"].data_type == "raster"
    assert result.results["vegetation_loss"].data_type == "raster"

    assert result.results["loss_polygons"].data_type == "vector"
    assert result.results["vegetation_loss"].data.metadata.crs == "EPSG:4326"
    assert str(result.results["loss_polygons"].data.crs) == "EPSG:4326"
    assert result.results["loss_projected"].data_type == "vector"
    assert result.results["roads_projected"].data_type == "vector"
    assert result.results["road_buffer"].data_type == "vector"
    assert result.results["final"].data_type == "vector"

    assert result.results["area"].data_type == "scalar"

    assert result.evidence

    evidence_operations = {item.operation for item in result.evidence}

    assert "get_satellite_imagery" in evidence_operations
    assert "get_osm_features" in evidence_operations
    assert "calculate_ndvi" in evidence_operations
    assert "temporal_difference" in evidence_operations
    assert "vegetation_loss" in evidence_operations
    assert "intersection" in evidence_operations
    assert "area" in evidence_operations