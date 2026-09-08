import pytest

from app.planner.mock import HERO_QUERY, MockQueryPlanner
from app.schemas.query import QueryPlan


def test_mock_planner_returns_hero_query_plan() -> None:
    planner = MockQueryPlanner()

    plan = planner.plan(HERO_QUERY)

    assert isinstance(plan, QueryPlan)
    assert plan.plan_id == "hero_vegetation_loss"

    assert plan.aoi.type == "bbox"
    assert plan.aoi.value == [73.0, 18.0, 73.1, 18.1]

    operation_types = [operation.type for operation in plan.operations]

    assert operation_types == [
        "get_satellite_imagery",
        "get_satellite_imagery",
        "get_osm_features",
        "calculate_ndvi",
        "calculate_ndvi",
        "temporal_difference",
        "vegetation_loss",
        "raster_polygonize",
        "project_to_crs",
        "project_to_crs",
        "buffer",
        "intersection",
        "area",
    ]


def test_mock_planner_preserves_hero_query_parameters() -> None:
    planner = MockQueryPlanner()

    plan = planner.plan(HERO_QUERY)

    operations = {
        operation.id: operation
        for operation in plan.operations
    }

    assert operations["s2_2024"].parameters["start_date"] == "2024-01-01"
    assert operations["s2_2026"].parameters["start_date"] == "2026-01-01"

    assert operations["roads"].parameters["feature_type"] == "roads"

    assert operations["vegetation_loss"].parameters["threshold"] == -0.1

    assert operations["loss_projected"].parameters["target_crs"] == "EPSG:32643"
    assert operations["roads_projected"].parameters["target_crs"] == "EPSG:32643"

    assert operations["road_buffer"].parameters["distance_m"] == 3000


def test_mock_planner_preserves_operation_dependencies() -> None:
    planner = MockQueryPlanner()

    plan = planner.plan(HERO_QUERY)

    operations = {
        operation.id: operation
        for operation in plan.operations
    }

    assert operations["ndvi_2024"].inputs == ["s2_2024"]
    assert operations["ndvi_2026"].inputs == ["s2_2026"]

    assert operations["vegetation_change"].inputs == [
        "ndvi_2024",
        "ndvi_2026",
    ]

    assert operations["vegetation_loss"].inputs == [
        "vegetation_change",
    ]

    assert operations["loss_polygons"].inputs == [
        "vegetation_loss",
    ]

    assert operations["road_buffer"].inputs == [
        "roads_projected",
    ]

    assert operations["final"].inputs == [
        "loss_projected",
        "road_buffer",
    ]

    assert operations["area"].inputs == ["final"]


def test_mock_planner_rejects_unsupported_query() -> None:
    planner = MockQueryPlanner()

    with pytest.raises(
        ValueError,
        match="Unsupported mock query",
    ):
        planner.plan("Find buildings near roads")