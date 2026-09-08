import geopandas as gpd
import numpy as np
from fastapi.testclient import TestClient
from rasterio.transform import from_bounds
from shapely.geometry import LineString

from app.api.routes import get_executor, get_query_service
from app.config.settings import settings
from app.executor.executor import Executor
from app.main import app
from app.planner.gemini import GeminiQueryPlanner
from app.planner.mock import MockQueryPlanner
from app.planner.openai import OpenAIQueryPlanner
from app.planner.service import QueryService
from app.planner.validator import QueryPlanValidator
from app.schemas.operation import Operation
from app.schemas.query import AOI, OutputSpec, QueryPlan
from app.schemas.raster import RasterData, RasterMetadata
from tests.operations.registry import create_mock_registry


def test_production_query_service_uses_configured_planner() -> None:
    service = get_query_service()

    if settings.planner_provider == "gemini":
        assert isinstance(service.planner, GeminiQueryPlanner)
    elif settings.planner_provider == "openai":
        assert isinstance(service.planner, OpenAIQueryPlanner)
    else:
        raise AssertionError(
            f"Unsupported planner provider: {settings.planner_provider}"
        )


def get_test_executor() -> Executor:
    return Executor(
        registry=create_mock_registry(),
    )


app.dependency_overrides[get_executor] = get_test_executor


def create_hero_runtime_inputs() -> dict:
    transform = from_bounds(
        73.0,
        18.0,
        73.1,
        18.1,
        4,
        4,
    )
    raster_2024 = RasterData(
        data=np.full(
            (2, 4, 4),
            0.6,
            dtype=np.float32,
        ),
        bands=["B4", "B8"],
        metadata=RasterMetadata(
            crs="EPSG:4326",
            transform=transform,
            resolution=None,
            nodata=None,
            bounds=(73.0, 18.0, 73.1, 18.1),
            width=4,
            height=4,
            count=2,
            dtype="float32",
        ),
    )

    raster_2026_data = np.full(
        (2, 4, 4),
        0.6,
        dtype=np.float32,
    )

    raster_2026_data[:, 1:3, 1:3] = 0.3

    raster_2026 = RasterData(
        data=raster_2026_data,
        bands=["B4", "B8"],
        metadata=RasterMetadata(
            crs="EPSG:4326",
            transform=transform,
            resolution=None,
            nodata=None,
            bounds=(73.0, 18.0, 73.1, 18.1),
            width=4,
            height=4,
            count=2,
            dtype="float32",
        ),
    )

    roads = gpd.GeoDataFrame(
        {"highway": ["primary"]},
        geometry=[
            LineString(
                [
                    (73.02, 18.02),
                    (73.08, 18.08),
                ],
            ),
        ],
        crs="EPSG:4326",
    )

    return {
        "s2_2024": raster_2024,
        "s2_2026": raster_2026,
        "roads": roads,
    }


class MockQueryService(QueryService):
    def execute(
        self,
        query: str,
        runtime_inputs=None,
    ):
        return super().execute(
            query,
            runtime_inputs=create_hero_runtime_inputs(),
        )


def get_test_query_service() -> QueryService:
    registry = create_mock_registry()

    return MockQueryService(
        planner=MockQueryPlanner(),
        validator=QueryPlanValidator(registry),
        executor=Executor(registry),
    )


app.dependency_overrides[get_query_service] = get_test_query_service

client = TestClient(app)


def test_query_endpoint_executes_plan() -> None:
    plan = QueryPlan(
        plan_id="api_test",
        aoi=AOI(
            type="bbox",
            value=[73.0, 18.0, 73.1, 18.1],
        ),
        operations=[
            Operation(
                id="source",
                type="mock_raster_source",
            ),
        ],
        output=OutputSpec(
            type="statistics",
            include_geometry=False,
            include_statistics=True,
            include_evidence=True,
        ),
    )

    response = client.post(
        "/query",
        json=plan.model_dump(mode="json"),
    )

    assert response.status_code == 200

    body = response.json()

    assert "results" in body
    assert "evidence" in body
    assert "metadata" in body

    assert set(body["results"]) == {"source"}

    assert body["results"]["source"]["data_type"] == "raster"

    assert len(body["evidence"]) == 1
    assert body["evidence"][0]["operation"] == "mock_raster_source"


def test_natural_query_endpoint_executes_hero_query() -> None:
    response = client.post(
        "/query/natural",
        json={
            "query": (
                "Find areas where vegetation decreased between "
                "2024 and 2026 that are within 3 km of major roads."
            )
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert "results" in body
    assert "evidence" in body
    assert "metadata" in body

    assert set(body["results"]) == {
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

    assert len(body["evidence"]) == 13