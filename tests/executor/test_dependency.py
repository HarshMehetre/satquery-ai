import pytest

from app.executor.dependency import DependencyResolver
from app.schemas.operation import Operation


def test_resolves_simple_dependency_chain():
    operations = [
        Operation(
            id="final",
            type="intersection",
            inputs=["vegetation_loss"],
        ),
        Operation(
            id="vegetation_loss",
            type="filter",
            inputs=["vegetation_change"],
        ),
        Operation(
            id="vegetation_change",
            type="temporal_difference",
            inputs=["ndvi_2024", "ndvi_2026"],
        ),
        Operation(
            id="ndvi_2024",
            type="calculate_ndvi",
            inputs=["s2_2024"],
        ),
        Operation(
            id="ndvi_2026",
            type="calculate_ndvi",
            inputs=["s2_2026"],
        ),
    ]

    resolver = DependencyResolver()

    ordered = resolver.resolve(operations)

    order = [operation.id for operation in ordered]

    assert order.index("ndvi_2024") < order.index(
        "vegetation_change"
    )

    assert order.index("ndvi_2026") < order.index(
        "vegetation_change"
    )

    assert order.index("vegetation_change") < order.index(
        "vegetation_loss"
    )

    assert order.index("vegetation_loss") < order.index(
        "final"
    )


def test_resolves_multiple_dependencies():
    operations = [
        Operation(
            id="final",
            type="intersection",
            inputs=[
                "vegetation_loss",
                "road_buffer",
            ],
        ),
        Operation(
            id="vegetation_loss",
            type="filter",
            inputs=["vegetation_change"],
        ),
        Operation(
            id="vegetation_change",
            type="temporal_difference",
            inputs=[
                "ndvi_2024",
                "ndvi_2026",
            ],
        ),
        Operation(
            id="ndvi_2024",
            type="calculate_ndvi",
            inputs=["s2_2024"],
        ),
        Operation(
            id="ndvi_2026",
            type="calculate_ndvi",
            inputs=["s2_2026"],
        ),
        Operation(
            id="road_buffer",
            type="buffer",
            inputs=["roads"],
        ),
    ]

    resolver = DependencyResolver()

    ordered = resolver.resolve(operations)

    order = [operation.id for operation in ordered]

    assert order.index("vegetation_loss") < order.index(
        "final"
    )

    assert order.index("road_buffer") < order.index(
        "final"
    )


def test_duplicate_operation_ids_fail():
    operations = [
        Operation(
            id="duplicate",
            type="mock",
        ),
        Operation(
            id="duplicate",
            type="mock",
        ),
    ]

    resolver = DependencyResolver()

    with pytest.raises(ValueError, match="Duplicate operation ID"):
        resolver.resolve(operations)


def test_circular_dependency_fails():
    operations = [
        Operation(
            id="operation_a",
            type="mock",
            inputs=["operation_b"],
        ),
        Operation(
            id="operation_b",
            type="mock",
            inputs=["operation_a"],
        ),
    ]

    resolver = DependencyResolver()

    with pytest.raises(
        ValueError,
        match="Circular dependency",
    ):
        resolver.resolve(operations)


def test_external_inputs_are_allowed():
    operations = [
        Operation(
            id="ndvi",
            type="calculate_ndvi",
            inputs=["s2_2024"],
        ),
    ]

    resolver = DependencyResolver()

    ordered = resolver.resolve(operations)

    assert len(ordered) == 1
    assert ordered[0].id == "ndvi"