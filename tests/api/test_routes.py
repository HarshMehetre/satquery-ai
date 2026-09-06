from fastapi.testclient import TestClient

from app.api.routes import get_executor
from app.executor.executor import Executor
from app.main import app
from app.schemas.operation import Operation
from app.schemas.query import AOI, OutputSpec, QueryPlan
from tests.operations.registry import create_mock_registry


def get_test_executor() -> Executor:
    return Executor(
        registry=create_mock_registry(),
    )


app.dependency_overrides[get_executor] = get_test_executor

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