from app.executor.executor import Executor
from app.schemas.operation import Operation
from app.schemas.query import AOI, OutputSpec, QueryPlan
from tests.operations.registry import create_mock_registry


def test_executor_builds_evidence_for_executed_operation() -> None:
    plan = QueryPlan(
        plan_id="evidence_test",
        aoi=AOI(
            type="bbox",
            value=[73.0, 18.0, 73.1, 18.1],
        ),
        operations=[
            Operation(
                id="source",
                type="mock_raster_source",
                parameters={
                    "value": "test",
                },
            ),
        ],
        output=OutputSpec(
            type="statistics",
            include_geometry=False,
            include_statistics=True,
            include_evidence=True,
        ),
    )

    result = Executor(
        registry=create_mock_registry(),
    ).execute(plan)

    assert len(result.evidence) == 1

    evidence = result.evidence[0]

    assert evidence.operation == "mock_raster_source"
    assert evidence.parameters == {"value": "test"}
    assert evidence.source == "unknown"
    assert evidence.source_type == "operation"