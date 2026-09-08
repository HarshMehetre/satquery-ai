from app.config.settings import Settings
from app.planner.factory import create_planner
from app.planner.gemini import GeminiQueryPlanner
from app.planner.openai import OpenAIQueryPlanner
from app.registry import create_production_registry


def test_factory_creates_gemini_planner():
    settings = Settings(
        planner_provider="gemini",
        gemini_model="gemini-3.5-flash-lite",
    )

    planner = create_planner(
        registry=create_production_registry(),
        settings=settings,
    )

    assert isinstance(planner, GeminiQueryPlanner)
    assert planner.model == "gemini-3.5-flash-lite"


def test_factory_creates_openai_planner():
    settings = Settings(
        planner_provider="openai",
        openai_model="gpt-5.6-luna",
    )

    planner = create_planner(
        registry=create_production_registry(),
        settings=settings,
    )

    assert isinstance(planner, OpenAIQueryPlanner)
    assert planner.model == "gpt-5.6-luna"


def test_factory_rejects_unknown_provider():
    settings = Settings(
        planner_provider="unknown",
    )

    try:
        create_planner(
            registry=create_production_registry(),
            settings=settings,
        )
    except ValueError as exc:
        assert str(exc) == "Unsupported planner provider: unknown"
    else:
        raise AssertionError("Expected ValueError")