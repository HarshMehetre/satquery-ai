import pytest

from app.planner.validator import QueryPlanValidator
from app.schemas.operation import Operation
from app.schemas.query import AOI, OutputSpec, QueryPlan
from tests.operations.registry import create_mock_registry


def create_plan(
    operations: list[Operation],
    inputs=None,
) -> QueryPlan:
    return QueryPlan(
        plan_id="validator_test",
        aoi=AOI(
            type="bbox",
            value=[73.0, 18.0, 73.1, 18.1],
        ),
        inputs=inputs or [],
        operations=operations,
        output=OutputSpec(
            type="statistics",
        ),
    )


def test_valid_plan_passes_validation() -> None:
    validator = QueryPlanValidator(
        registry=create_mock_registry(),
    )

    plan = create_plan(
        operations=[
            Operation(
                id="source",
                type="mock_source",
            ),
            Operation(
                id="transform",
                type="mock_transform",
                inputs=["source"],
            ),
        ],
    )

    validator.validate(plan)


def test_unknown_operation_type_is_rejected() -> None:
    validator = QueryPlanValidator(
        registry=create_mock_registry(),
    )

    plan = create_plan(
        operations=[
            Operation(
                id="unknown",
                type="does_not_exist",
            ),
        ],
    )

    with pytest.raises(
        ValueError,
        match="Unknown operation type",
    ):
        validator.validate(plan)


def test_duplicate_operation_ids_are_rejected() -> None:
    validator = QueryPlanValidator(
        registry=create_mock_registry(),
    )

    plan = create_plan(
        operations=[
            Operation(
                id="duplicate",
                type="mock_source",
            ),
            Operation(
                id="duplicate",
                type="mock_source",
            ),
        ],
    )

    with pytest.raises(
        ValueError,
        match="Operation IDs must be unique",
    ):
        validator.validate(plan)


def test_undeclared_input_is_rejected() -> None:
    validator = QueryPlanValidator(
        registry=create_mock_registry(),
    )

    plan = create_plan(
        operations=[
            Operation(
                id="transform",
                type="mock_transform",
                inputs=["missing"],
            ),
        ],
    )

    with pytest.raises(
        ValueError,
        match="is not declared or produced",
    ):
        validator.validate(plan)
        
def test_rejects_unresolved_aoi():
    validator = QueryPlanValidator(
        registry=create_mock_registry(),
    )

    plan = QueryPlan(
        plan_id="test",
        aoi={
            "type": "place",
            "value": "Mumbai",
            "resolved": False,
        },
        inputs=[],
        operations=[],
        output={
            "type": "map",
        },
    )

    with pytest.raises(
        ValueError,
        match="AOI must be resolved before query execution.",
    ):
        validator.validate(plan)
        
def test_resolved_aoi_is_accepted():
    validator = QueryPlanValidator(
        registry=create_mock_registry(),
    )

    plan = QueryPlan(
        plan_id="test",
        aoi={
            "type": "bbox",
            "value": [73.0, 18.0, 73.1, 18.1],
            "resolved": True,
        },
        inputs=[],
        operations=[],
        output={
            "type": "map",
        },
    )

    validator.validate(plan)