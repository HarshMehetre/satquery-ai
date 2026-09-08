from unittest.mock import Mock

import pytest

from app.planner.aoi import AOIResolver
from app.planner.service import QueryService
from app.planner.validator import QueryPlanValidator
from app.schemas.query import AOI, OutputSpec, QueryPlan
from app.schemas.result import ExecutionResult
from tests.operations.registry import create_mock_registry


def test_query_service_resolves_aoi_before_validation() -> None:
    original_aoi = AOI(
        type="place",
        value={"name": "Mumbai"},
        resolved=False,
    )

    plan = QueryPlan(
        plan_id="mumbai_test",
        aoi=original_aoi,
        inputs=[],
        operations=[],
        output=OutputSpec(type="map"),
    )

    planner = Mock()
    planner.plan.return_value = plan

    resolver = Mock(spec=AOIResolver)
    resolver.resolve.return_value = AOI(
        type="bbox",
        value=[72.7, 18.8, 73.1, 19.3],
        resolved=True,
    )

    executor = Mock()
    executor.execute.return_value = ExecutionResult()

    service = QueryService(
        planner=planner,
        validator=QueryPlanValidator(create_mock_registry()),
        executor=executor,
        aoi_resolver=resolver,
    )

    result = service.execute("Find vegetation loss in Mumbai.")

    planner.plan.assert_called_once_with(
        "Find vegetation loss in Mumbai."
    )
    resolver.resolve.assert_called_once_with(original_aoi)
    executor.execute.assert_called_once()

    resolved_plan = executor.execute.call_args.args[0]

    assert resolved_plan.aoi.type == "bbox"
    assert resolved_plan.aoi.value == [72.7, 18.8, 73.1, 19.3]
    assert resolved_plan.aoi.resolved is True
    assert result == ExecutionResult()
    
def test_query_service_does_not_execute_when_aoi_resolution_fails() -> None:
    plan = QueryPlan(
        plan_id="mumbai_test",
        aoi=AOI(
            type="place",
            value={"name": "Mumbai"},
            resolved=False,
        ),
        inputs=[],
        operations=[],
        output=OutputSpec(type="map"),
    )

    planner = Mock()
    planner.plan.return_value = plan

    resolver = Mock(spec=AOIResolver)
    resolver.resolve.side_effect = ValueError(
        "Could not resolve place AOI 'Mumbai'."
    )

    executor = Mock()

    service = QueryService(
        planner=planner,
        validator=QueryPlanValidator(create_mock_registry()),
        executor=executor,
        aoi_resolver=resolver,
    )

    with pytest.raises(
        ValueError,
        match="Could not resolve place AOI",
    ):
        service.execute("Find vegetation loss in Mumbai.")

    executor.execute.assert_not_called()