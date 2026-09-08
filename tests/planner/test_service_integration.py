
from app.executor.executor import Executor
from app.planner.service import QueryService
from app.registry import create_production_registry
from app.schemas.query import QueryPlan
from app.schemas.result import OperationResult


def create_plan() -> QueryPlan:
    return QueryPlan.model_validate(
        {
            "plan_id": "integration_test",
            "aoi": {
                "type": "bbox",
                "value": [73.0, 18.0, 73.1, 18.1],
            },
            "inputs": [],
            "operations": [
                {
                    "id": "source",
                    "type": "mock_source",
                    "inputs": [],
                    "parameters": {},
                }
            ],
            "output": {
                "type": "statistics",
                "include_geometry": False,
                "include_statistics": True,
                "include_evidence": True,
            },
        }
    )


class MockPlanner:
    def __init__(self, plan: QueryPlan) -> None:
        self.plan_result = plan

    def plan(self, query: str) -> QueryPlan:
        return self.plan_result


class MockValidator:
    def __init__(self) -> None:
        self.called = False

    def validate(self, plan: QueryPlan) -> None:
        self.called = True


def test_query_service_runs_planner_validator_and_executor():
    plan = create_plan()

    planner = MockPlanner(plan)
    validator = MockValidator()

    registry = create_production_registry()
    registry.register("mock_source", MockSourceOperation)

    executor = Executor(registry)

    service = QueryService(
        planner=planner,
        validator=validator,
        executor=executor,
    )

    result = service.execute("Show me the result.")

    assert validator.called
    assert isinstance(result.results["source"], OperationResult)
    assert result.results["source"].id == "source"


class MockSourceOperation:
    def validate(self, operation, context) -> None:
        pass

    def execute(self, operation, context) -> OperationResult:
        return OperationResult(
            id=operation.id,
            type=operation.type,
            data_type="scalar",
            data=42,
        )