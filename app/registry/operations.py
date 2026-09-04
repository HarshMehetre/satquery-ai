from typing import Type

from app.operations.base import BaseOperation


class OperationRegistry:
    """
    Registry mapping operation names to their implementation classes.
    """

    def __init__(self) -> None:
        self._operations: dict[str, Type[BaseOperation]] = {}

    def register(
        self,
        name: str,
        operation_class: Type[BaseOperation],
    ) -> None:
        """
        Register an operation implementation.
        """

        if name in self._operations:
            raise ValueError(
                f"Operation '{name}' is already registered."
            )

        self._operations[name] = operation_class

    def get(
        self,
        name: str,
    ) -> Type[BaseOperation]:
        """
        Retrieve an operation implementation by name.
        """

        if name not in self._operations:
            raise KeyError(
                f"Operation '{name}' is not registered."
            )

        return self._operations[name]

    def contains(
        self,
        name: str,
    ) -> bool:
        """
        Check whether an operation is registered.
        """

        return name in self._operations

    def list_operations(self) -> list[str]:
        """
        Return all registered operation names.
        """

        return list(self._operations.keys())