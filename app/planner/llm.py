from typing import Any

from app.planner.interface import QueryPlanner
from app.schemas.query import QueryPlan


class LLMQueryPlanner(QueryPlanner):
    """
    Query planner backed by an LLM.

    The LLM is responsible only for producing structured QueryPlan data.
    Validation and execution remain outside the planner.
    """

    def __init__(self, client: Any) -> None:
        self.client = client

    def plan(self, query: str) -> QueryPlan:
        if not query.strip():
            raise ValueError("Query must not be empty.")

        response = self.client.generate_structured(
            query=query,
            response_model=QueryPlan,
        )

        if isinstance(response, QueryPlan):
            return response

        return QueryPlan.model_validate(response)