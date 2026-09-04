import pytest

from app.executor.executor import Executor
from app.schemas.operation import Operation
from app.schemas.query import (
    AOI,
    DataInput,
    OutputSpec,
    QueryPlan,
)
from tests.operations.registry import create_mock_registry


def create_plan() -> QueryPlan:
    return QueryPlan(
        plan_id="test_plan",
        aoi=AOI(
            type="place",
            value="Pune",
        ),
        inputs=[
            DataInput(
                id="satellite_data",
                source="mock-satellite",
                purpose="test imagery",
            )
        ],
        operations=[
            Operation(
                id="source",
                type="mock_source",
                inputs=["satellite_data"],
            ),
            Operation(
                id="transform",
                type="mock_transform",
                inputs=["source"],
            ),
            Operation(
                id="combine",
                type="mock_combine",
                inputs=["source", "transform"],
            ),
        ],
        output=OutputSpec(
            type="statistics",
        ),
    )


def test_executor_runs_operation_chain() -> None:
    registry = create_mock_registry()
    executor = Executor(registry)

    result = executor.execute(create_plan())

    assert set(result.results) == {
        "source",
        "transform",
        "combine",
    }

    assert result.results["source"].type == "mock_source"
    assert result.results["transform"].type == "mock_transform"
    assert result.results["combine"].type == "mock_combine"


def test_executor_respects_dependencies() -> None:
    registry = create_mock_registry()
    executor = Executor(registry)

    plan = create_plan()

    result = executor.execute(plan)

    transform_result = result.results["transform"]
    combine_result = result.results["combine"]

    assert transform_result.data["transformed"] == (
        result.results["source"].data
    )

    assert "source" in combine_result.data
    assert "transform" in combine_result.data


def test_executor_rejects_missing_input() -> None:
    registry = create_mock_registry()
    executor = Executor(registry)

    plan = create_plan()

    plan.operations[0].inputs = ["missing_input"]

    with pytest.raises(KeyError):
        executor.execute(plan)


def test_executor_rejects_unknown_operation() -> None:
    registry = create_mock_registry()
    executor = Executor(registry)

    plan = create_plan()

    plan.operations[0].type = "does_not_exist"

    with pytest.raises(KeyError):
        executor.execute(plan)
        
def test_executor_returns_complete_execution_result() -> None:
    registry = create_mock_registry()
    executor = Executor(registry)

    result = executor.execute(create_plan())

    assert result.results
    assert isinstance(result.results, dict)
    assert isinstance(result.evidence, list)
    assert isinstance(result.metadata, dict)
    
def test_executor_rejects_circular_dependencies() -> None:
    registry = create_mock_registry()
    executor = Executor(registry)

    plan = create_plan()

    plan.operations[0].inputs = ["combine"]

    with pytest.raises(ValueError, match="Circular dependency"):
        executor.execute(plan)
        
def test_executor_rejects_duplicate_operation_ids() -> None:
    registry = create_mock_registry()
    executor = Executor(registry)

    plan = create_plan()

    plan.operations.append(
        Operation(
            id="source",
            type="mock_source",
            inputs=["satellite_data"],
        )
    )

    with pytest.raises(
        ValueError,
        match="Duplicate operation ID",
    ):
        executor.execute(plan)