from app.planner.planner import QueryPlanner
from app.schemas.query import AOI, OutputSpec, QueryPlan


class MockQueryPlanner(QueryPlanner):
    def plan(self, query: str) -> QueryPlan:
        return QueryPlan(
            plan_id="test_plan",
            aoi=AOI(
                type="bbox",
                value=[73.0, 18.0, 73.1, 18.1],
            ),
            operations=[],
            output=OutputSpec(
                type="statistics",
            ),
        )


def test_query_planner_returns_query_plan() -> None:
    planner = MockQueryPlanner()

    result = planner.plan("Find vegetation in this area")

    assert isinstance(result, QueryPlan)
    assert result.plan_id == "test_plan"
    assert result.aoi.type == "bbox"
    assert result.aoi.value == [73.0, 18.0, 73.1, 18.1]
    assert result.operations == []
    assert result.output.type == "statistics"