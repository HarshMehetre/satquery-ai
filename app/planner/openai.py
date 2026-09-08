from openai import OpenAI

from app.planner.interface import QueryPlanner
from app.registry.operations import OperationRegistry
from app.schemas.query import QueryPlan

PLANNER_SYSTEM_PROMPT = """
You are the planning engine for SatQuery-AI.

Your job is to convert a user's natural-language geospatial query
into a structured QueryPlan.

Rules:

1. Only produce a QueryPlan.
2. Never execute operations.
3. Never generate Python code.
4. Never invent satellite observations, measurements, distances,
   areas, dates, or GIS results.
5. Use ONLY operations from the supplied operation catalog.
6. Operation inputs must reference declared data inputs or previous
   operation IDs.
7. Use deterministic operations whenever possible.
8. Preserve temporal requirements explicitly.
9. Every operation must have a unique ID.
10. The executor performs all actual calculations and data retrieval.

AVAILABLE OPERATIONS:
"""


class OpenAIQueryPlanner(QueryPlanner):
    """Convert natural-language queries into validated QueryPlans."""

    def __init__(
        self,
        registry: OperationRegistry,
        client: OpenAI | None = None,
        model: str = "gpt-5.6-luna",
    ) -> None:
        self.registry = registry
        self.client = client
        self.model = model

    def _build_system_prompt(self) -> str:
        catalog = self.registry.get_catalog()

        return (
            f"{PLANNER_SYSTEM_PROMPT}\n"
            f"{catalog}\n"
        )

    def plan(self, query: str) -> QueryPlan:
        if not query.strip():
            raise ValueError("Query must not be empty.")

        client = self.client or OpenAI()

        response = client.responses.parse(
            model=self.model,
            instructions=self._build_system_prompt(),
            input=query,
            text_format=QueryPlan,
        )

        if response.output_parsed is None:
            raise ValueError("LLM did not return a valid QueryPlan.")

        return response.output_parsed