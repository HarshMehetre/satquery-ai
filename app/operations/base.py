from abc import ABC, abstractmethod

from app.executor.context import ExecutionContext
from app.schemas.operation import Operation
from app.schemas.result import OperationResult


class BaseOperation(ABC):
    """
    Base interface for all executable SatQuery operations.
    """

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
