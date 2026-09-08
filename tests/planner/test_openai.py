from unittest.mock import Mock

from app.planner.openai import OpenAIQueryPlanner
from app.registry import create_production_registry
from app.schemas.query import QueryPlan


def create_plan() -> QueryPlan:
    return QueryPlan.model_validate(
        {
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
    )


def test_openai_planner_returns_query_plan() -> None:
    expected_plan = create_plan()

    client = Mock()
    client.responses.parse.return_value.output_parsed = expected_plan

    registry = create_production_registry()

    planner = OpenAIQueryPlanner(
        registry=registry,
        client=client,
        model="test-model",
    )

    result = planner.plan("Show the area.")

    assert result is expected_plan

    client.responses.parse.assert_called_once()

    call_kwargs = client.responses.parse.call_args.kwargs

    assert call_kwargs["model"] == "test-model"
    assert call_kwargs["text_format"] is QueryPlan
    assert call_kwargs["input"] == "Show the area."


def test_openai_planner_includes_registry_catalog() -> None:
    expected_plan = create_plan()

    client = Mock()
    client.responses.parse.return_value.output_parsed = expected_plan

    registry = create_production_registry()

    planner = OpenAIQueryPlanner(
        registry=registry,
        client=client,
    )

    planner.plan("Find vegetation.")

    instructions = client.responses.parse.call_args.kwargs["instructions"]

    assert "get_satellite_imagery" in instructions
    assert "calculate_ndvi" in instructions
    assert "project_to_crs" in instructions
    assert "buffer" in instructions
    assert "intersection" in instructions
    assert "area" in instructions
    assert "get_osm_features" in instructions
    assert "temporal_difference" in instructions
    assert "vegetation_loss" in instructions
    assert "raster_polygonize" in instructions


def test_planner_catalog_matches_registry() -> None:
    registry = create_production_registry()

    client = Mock()

    planner = OpenAIQueryPlanner(
        registry=registry,
        client=client,
    )

    catalog = registry.get_catalog()

    assert catalog
    assert len(catalog) == len(registry.list_operations())

    client.responses.parse.return_value.output_parsed = create_plan()

    planner.plan("Find water bodies.")

    instructions = client.responses.parse.call_args.kwargs["instructions"]

    for operation in catalog:
        assert operation["type"] in instructions


def test_openai_planner_rejects_empty_query() -> None:
    client = Mock()
    registry = create_production_registry()

    planner = OpenAIQueryPlanner(
        registry=registry,
        client=client,
    )

    try:
        planner.plan("   ")
    except ValueError as exc:
        assert str(exc) == "Query must not be empty."
    else:
        raise AssertionError("Expected ValueError")

    client.responses.parse.assert_not_called()


def test_openai_planner_rejects_missing_structured_output() -> None:
    client = Mock()
    client.responses.parse.return_value.output_parsed = None

    registry = create_production_registry()

    planner = OpenAIQueryPlanner(
        registry=registry,
        client=client,
    )

    try:
        planner.plan("Find water bodies.")
    except ValueError as exc:
        assert str(exc) == "LLM did not return a valid QueryPlan."
    else:
        raise AssertionError("Expected ValueError")