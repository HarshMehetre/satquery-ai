from app.executor.context import ExecutionContext
from app.operations.base import BaseOperation
from app.schemas.operation import Operation
from app.schemas.result import OperationResult


class MockSourceOperation(BaseOperation):
    """Mock operation that reads an external input."""

    def validate(
        self,
        operation: Operation,
        context: ExecutionContext,
    ) -> None:
        if len(operation.inputs) != 1:
            raise ValueError(
                "MockSourceOperation requires exactly one input."
            )

        input_id = operation.inputs[0]

        if input_id not in context.inputs:
            raise KeyError(
                f"External input '{input_id}' does not exist."
            )

    def execute(
        self,
        operation: Operation,
        context: ExecutionContext,
    ) -> OperationResult:
        self.validate(operation, context)

        input_id = operation.inputs[0]
        data_input = context.inputs[input_id]

        return OperationResult(
            id=operation.id,
            type=operation.type,
            data_type="json",
            data={
                "source": data_input.source,
                "purpose": data_input.purpose,
            },
        )


class MockTransformOperation(BaseOperation):
    """Mock operation that transforms a previous operation result."""

    def validate(
        self,
        operation: Operation,
        context: ExecutionContext,
    ) -> None:
        if len(operation.inputs) != 1:
            raise ValueError(
                "MockTransformOperation requires exactly one input."
            )

        input_id = operation.inputs[0]

        if input_id not in context.results:
            raise KeyError(
                f"Operation result '{input_id}' does not exist."
            )

    def execute(
        self,
        operation: Operation,
        context: ExecutionContext,
    ) -> OperationResult:
        self.validate(operation, context)

        input_id = operation.inputs[0]
        previous_result = context.get_result(input_id)

        return OperationResult(
            id=operation.id,
            type=operation.type,
            data_type="json",
            data={
                "transformed": previous_result.data,
            },
        )


class MockCombineOperation(BaseOperation):
    """Mock operation that combines multiple previous results."""

    def validate(
        self,
        operation: Operation,
        context: ExecutionContext,
    ) -> None:
        if len(operation.inputs) < 2:
            raise ValueError(
                "MockCombineOperation requires at least two inputs."
            )

        for input_id in operation.inputs:
            if input_id not in context.results:
                raise KeyError(
                    f"Operation result '{input_id}' does not exist."
                )

    def execute(
        self,
        operation: Operation,
        context: ExecutionContext,
    ) -> OperationResult:
        self.validate(operation, context)

        combined_data = {
            input_id: context.get_result(input_id).data
            for input_id in operation.inputs
        }

        return OperationResult(
            id=operation.id,
            type=operation.type,
            data_type="json",
            data=combined_data,
        )