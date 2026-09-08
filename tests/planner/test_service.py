from app.executor.executor import Executor
from app.planner.planner import QueryPlanner
from app.planner.service import QueryService
from app.planner.validator import QueryPlanValidator
from app.schemas.operation import Operation
from app.schemas.query import AOI, OutputSpec, QueryPlan
from tests.operations.registry import create_mock_registry


class SimpleMockPlanner(QueryPlanner):
    def plan(self, query: str) -> QueryPlan:
        return QueryPlan(
            plan_id="service_test",
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
            ),
        )


def test_query_service_plans_validates_and_executes() -> None:
    registry = create_mock_registry()

    service = QueryService(
        planner=SimpleMockPlanner(),
        validator=QueryPlanValidator(registry),
        executor=Executor(registry),
    )

    result = service.execute("test query")

    assert "source" in result.results
    assert len(result.evidence) == 1
    assert result.evidence[0].operation == "mock_raster_source"