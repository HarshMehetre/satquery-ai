import pytest

from app.operations.base import BaseOperation
from app.schemas.operation import Operation
from app.schemas.result import OperationResult


class MockOperation(BaseOperation):

    def validate(
        self,
        operation: Operation,
        context,
    ) -> None:
        if operation.type != "mock":
            raise ValueError("Invalid operation type.")

    def execute(
        self,
        operation: Operation,
        context,
    ) -> OperationResult:
        return OperationResult(
            id=operation.id,
            type=operation.type,
            data_type="scalar",
            data=42,
        )


def test_mock_operation_validation():
    operation = Operation(
        id="test_001",
        type="mock",
    )

    mock = MockOperation()

    mock.validate(operation, None)


def test_mock_operation_execution():
    operation = Operation(
        id="test_001",
        type="mock",
    )

    mock = MockOperation()

    result = mock.execute(operation, None)

    assert result.id == "test_001"
    assert result.type == "mock"
    assert result.data_type == "scalar"
    assert result.data == 42


def test_base_operation_is_abstract():
    with pytest.raises(TypeError):
        BaseOperation()