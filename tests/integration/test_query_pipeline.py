from __future__ import annotations

from typing import ClassVar

import geopandas as gpd
import numpy as np
from rasterio.transform import from_bounds
from shapely.geometry import LineString

from app.executor.executor import Executor
from app.planner.service import QueryService
from app.planner.validator import QueryPlanValidator
from app.registry.operations import create_production_registry
from app.schemas.operation import Operation
from app.schemas.query import (
    AOI,
    DataInput,
    OutputSpec,
    QueryPlan,
    TimeRange,
)
from app.schemas.raster import RasterData, RasterMetadata


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
                        "start_date": "2024-01-01",
                        "end_date": "2024-12-31",
                        "max_cloud_coverage": 30,
                        "width": 4,
                        "height": 4,
                    },
                ),
                Operation(
                    id="s2_2026_data",
                    type="get_satellite_imagery",
                    parameters={
                        "start_date": "2026-01-01",
                        "end_date": "2026-12-31",
                        "max_cloud_coverage": 30,
                        "width": 4,
                        "height": 4,
                    },
                ),
                Operation(
                    id="roads_data",
                    type="get_osm_features",
                    parameters={
                        "feature_type": "roads",
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
                        "direction": "decrease",
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


class StubSentinelHubRequest:
    """
    External Sentinel Hub request boundary used by the integration test.

    The production Sentinel-2 retrieval operation remains untouched.
    Only the external request/response is replaced.
    """

    responses: ClassVar[list[np.ndarray]] = []
    requests: ClassVar[list[dict]] = []

    @staticmethod
    def input_data(**kwargs):
        return {
            "type": "input_data",
            "kwargs": kwargs,
        }

    @staticmethod
    def output_response(*args, **kwargs):
        return {
            "type": "output_response",
            "args": args,
            "kwargs": kwargs,
        }

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.requests.append(kwargs)

    def get_data(self):
        if not self.responses:
            raise AssertionError(
                "StubSentinelHubRequest has no queued response."
            )

        return [self.responses.pop(0)]


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


def _create_sentinel_response(changed: bool = False) -> np.ndarray:
    """
    Create the H x W x bands response returned by Sentinel Hub.

    This mirrors the response shape expected by the production retrieval
    operation before it transposes the array into bands x height x width.
    """

    raster = _create_synthetic_raster(changed=changed)

    return np.transpose(
        raster.data,
        (1, 2, 0),
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


def test_query_service_executes_hero_query_end_to_end(monkeypatch):
    """
    Execute the complete production query pipeline.

    Application retrieval logic is real.
    Only external Sentinel Hub and OSM service calls are stubbed.
    """

    from app.config.settings import settings

    sentinel_responses = [
        _create_sentinel_response(changed=False),
        _create_sentinel_response(changed=True),
    ]

    StubSentinelHubRequest.responses = sentinel_responses.copy()
    StubSentinelHubRequest.requests = []

    monkeypatch.setattr(
        "app.operations.satellite.retrieve.SentinelHubRequest",
        StubSentinelHubRequest,
    )

    monkeypatch.setattr(
        settings,
        "sentinel_client_id",
        "test-client-id",
    )
    monkeypatch.setattr(
        settings,
        "sentinel_client_secret",
        "test-client-secret",
    )

    osm_calls = []

    def stub_features_from_bbox(**kwargs):
        osm_calls.append(kwargs)
        return _create_roads()

    monkeypatch.setattr(
        "app.operations.gis.osm.ox.features_from_bbox",
        stub_features_from_bbox,
    )

    planner = StubHeroPlanner()

    registry = create_production_registry()
    validator = QueryPlanValidator(registry)

    service = QueryService(
        planner=planner,
        validator=validator,
        executor=Executor(registry),
    )

    result = service.execute(
        "Find areas where vegetation decreased between 2024 and 2026 "
        "that are within 3 km of major roads.",
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

    evidence_operations = {
        item.operation for item in result.evidence
    }

    assert "get_satellite_imagery" in evidence_operations
    assert "get_osm_features" in evidence_operations
    assert "calculate_ndvi" in evidence_operations
    assert "temporal_difference" in evidence_operations
    assert "vegetation_loss" in evidence_operations
    assert "intersection" in evidence_operations
    assert "area" in evidence_operations

    # Verify that the real Sentinel-2 retrieval operation constructed
    # requests using the resolved AOI and requested temporal ranges.
    assert len(StubSentinelHubRequest.requests) == 2

    first_request = StubSentinelHubRequest.requests[0]
    second_request = StubSentinelHubRequest.requests[1]

    assert (
    first_request["bbox"].min_x,
    first_request["bbox"].min_y,
    first_request["bbox"].max_x,
    first_request["bbox"].max_y,
    ) == (
    73.0,
    18.0,
    73.1,
    18.1,
    )

    assert (
    second_request["bbox"].min_x,
    second_request["bbox"].min_y,
    second_request["bbox"].max_x,
    second_request["bbox"].max_y,
    ) == (
    73.0,
    18.0,
    73.1,
    18.1,
    )
    
    assert str(first_request["bbox"].crs) == "EPSG:4326"
    assert str(second_request["bbox"].crs) == "EPSG:4326"

    assert first_request["size"] == (4, 4)
    assert second_request["size"] == (4, 4)

    assert first_request["input_data"][0]["kwargs"]["time_interval"] == (
        "2024-01-01",
        "2024-12-31",
    )
    assert second_request["input_data"][0]["kwargs"]["time_interval"] == (
        "2026-01-01",
        "2026-12-31",
    )

    assert (
        first_request["input_data"][0]["kwargs"]["maxcc"]
        == 0.3
    )
    assert (
        second_request["input_data"][0]["kwargs"]["maxcc"]
        == 0.3
    )

    # Verify that the real OSM retrieval operation used the resolved AOI
    # and requested feature tags.
    assert len(osm_calls) == 1
    assert osm_calls[0]["bbox"] == (
        73.0,
        18.0,
        73.1,
        18.1,
    )
    assert osm_calls[0]["tags"] == {"highway": True}

    # The synthetic 2026 imagery contains a vegetation decrease in the
    # central 2x2 cells, so the deterministic loss operation must detect it.
    loss_mask = result.results["vegetation_loss"].data.data

    assert loss_mask.shape == (1, 4, 4)

    assert np.all(loss_mask[0, 1:3, 1:3])
    assert not np.any(loss_mask[0, 0, :])
    assert not np.any(loss_mask[0, 3, :])