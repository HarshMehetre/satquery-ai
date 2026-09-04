from abc import ABC, abstractmethod

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
        context,
    ) -> None:
        """
        Validate whether the operation can be executed
        in the current execution context.

        Should raise an exception if validation fails.
        """
        pass

    @abstractmethod
    def execute(
        self,
        operation: Operation,
        context,
    ) -> OperationResult:
        """
        Execute the operation and return a structured result.
        """
        pass