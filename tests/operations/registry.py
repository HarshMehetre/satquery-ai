from app.registry.operations import OperationRegistry
from tests.operations.mocks import (
    MockCombineOperation,
    MockSourceOperation,
    MockTransformOperation,
)


def create_mock_registry() -> OperationRegistry:
    registry = OperationRegistry()

    registry.register(
        "mock_source",
        MockSourceOperation,
    )

    registry.register(
        "mock_transform",
        MockTransformOperation,
    )

    registry.register(
        "mock_combine",
        MockCombineOperation,
    )

    return registry