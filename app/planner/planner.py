from abc import ABC, abstractmethod

from app.schemas.query import QueryPlan


class QueryPlanner(ABC):
    """Interface for converting natural-language queries into QueryPlans."""

    @abstractmethod
    def plan(self, query: str) -> QueryPlan:
        """Convert a natural-language query into an executable QueryPlan."""
        raise NotImplementedError