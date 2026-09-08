from abc import ABC, abstractmethod
from typing import Any

from app.executor.context import ExecutionContext
from app.schemas.operation import Operation
from app.schemas.result import OperationResult


class BaseOperation(ABC):
    """
    Base interface for all executable SatQuery operations.
    """
    
    @classmethod
    def planner_metadata(cls) -> dict[str, Any]:
        """Return metadata describing the operation to the query planner."""
        return {
            "type": cls.__name__,
            "description": cls.__doc__ or "",
        }

    @abstractmethod
    def validate(
        self,
        operation: Operation,
        context: ExecutionContext,
    ) -> None:
        """
        Validate whether the operation can execute
        in the current context.
        """

    @abstractmethod
    def execute(
        self,
        operation: Operation,
        context: ExecutionContext,
    ) -> OperationResult:
        """
        Execute the operation and return a structured result.
        """
