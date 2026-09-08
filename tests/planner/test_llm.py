from app.planner.llm import LLMQueryPlanner
from app.schemas.query import QueryPlan


class MockStructuredLLM:
    def __init__(self, response: dict) -> None:
        self.response = response
        self.calls: list[dict] = []

    def generate_structured(self, *, query: str, response_model: type) -> dict:
        self.calls.append(
            {
                "query": query,
                "response_model": response_model,
            }
        )
        return self.response


def create_plan_data() -> dict:
    return {
        "plan_id": "test_plan",
        "aoi": {
            "type": "bbox",
            "value": [73.0, 18.0, 73.1, 18.1],
        },
        "inputs": [],
        "operations": [],
        "output": {
            "type": "map",
            "include_geometry": True,
            "include_statistics": True,
            "include_evidence": True,
        },
    }


def test_llm_planner_returns_query_plan() -> None:
    llm = MockStructuredLLM(create_plan_data())
    planner = LLMQueryPlanner(client=llm)

    result = planner.plan("Show the area.")

    assert isinstance(result, QueryPlan)
    assert result.plan_id == "test_plan"
    assert llm.calls[0]["query"] == "Show the area."
    assert llm.calls[0]["response_model"] is QueryPlan


def test_llm_planner_accepts_existing_query_plan() -> None:
    plan = QueryPlan.model_validate(create_plan_data())

    class ExistingPlanLLM:
        def generate_structured(self, *, query: str, response_model: type) -> QueryPlan:
            return plan

    planner = LLMQueryPlanner(client=ExistingPlanLLM())

    result = planner.plan("Show the area.")

    assert result is plan


def test_llm_planner_rejects_empty_query() -> None:
    llm = MockStructuredLLM(create_plan_data())
    planner = LLMQueryPlanner(client=llm)

    try:
        planner.plan("   ")
    except ValueError as exc:
        assert str(exc) == "Query must not be empty."
    else:
        raise AssertionError("Expected ValueError")