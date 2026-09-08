from app.config.settings import Settings
from app.planner.gemini import GeminiQueryPlanner
from app.planner.interface import QueryPlanner
from app.planner.openai import OpenAIQueryPlanner
from app.registry.operations import OperationRegistry


def create_planner(
    registry: OperationRegistry,
    settings: Settings,
) -> QueryPlanner:
    """Create the configured query planner."""
    if settings.planner_provider == "gemini":
        return GeminiQueryPlanner(
            registry=registry,
            model=settings.gemini_model,
        )

    if settings.planner_provider == "openai":
        return OpenAIQueryPlanner(
            registry=registry,
            model=settings.openai_model,
        )

    raise ValueError(
        f"Unsupported planner provider: {settings.planner_provider}"
    )