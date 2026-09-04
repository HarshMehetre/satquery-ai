import pytest

from app.executor.context import ExecutionContext
from app.schemas.operation import Operation
from app.schemas.query import AOI, DataInput
from tests.operations.mocks import (
    MockCombineOperation,
    MockSourceOperation,
    MockTransformOperation,
)


def create_context() -> ExecutionContext:
    return ExecutionContext(
        aoi=AOI(
            type="place",
            value="Pune",
        ),
        inputs=[
            DataInput(
                id="satellite_data",
                source="mock-satellite",
                purpose="test imagery",
            )
        ],
    )


def test_mock_source_operation() -> None:
    context = create_context()

    operation = Operation(
        id="source",
        type="mock_source",
        inputs=["satellite_data"],
    )

    handler = MockSourceOperation()

    handler.validate(operation, context)
    result = handler.execute(operation, context)

    assert result.id == "source"
    assert result.type == "mock_source"
    assert result.data_type == "json"
    assert result.data["source"] == "mock-satellite"


def test_mock_source_requires_valid_external_input() -> None:
    context = create_context()

    operation = Operation(
        id="source",
        type="mock_source",
        inputs=["missing_input"],
    )

    handler = MockSourceOperation()

    with pytest.raises(KeyError):
        handler.validate(operation, context)


def test_mock_transform_operation() -> None:
    context = create_context()

    source_operation = Operation(
        id="source",
        type="mock_source",
        inputs=["satellite_data"],
    )

    source_result = MockSourceOperation().execute(
        source_operation,
        context,
    )

    context.add_result(source_result)

    transform_operation = Operation(
        id="transform",
        type="mock_transform",
        inputs=["source"],
    )

    handler = MockTransformOperation()

    result = handler.execute(
        transform_operation,
        context,
    )

    assert result.id == "transform"
    assert result.data["transformed"] == source_result.data


def test_mock_combine_operation() -> None:
    context = create_context()

    source_result = MockSourceOperation().execute(
        Operation(
            id="source",
            type="mock_source",
            inputs=["satellite_data"],
        ),
        context,
    )

    context.add_result(source_result)

    transformed_result = MockTransformOperation().execute(
        Operation(
            id="transform",
            type="mock_transform",
            inputs=["source"],
        ),
        context,
    )

    context.add_result(transformed_result)

    combine_operation = Operation(
        id="combine",
        type="mock_combine",
        inputs=["source", "transform"],
    )

    result = MockCombineOperation().execute(
        combine_operation,
        context,
    )

    assert result.id == "combine"
    assert "source" in result.data
    assert "transform" in result.data