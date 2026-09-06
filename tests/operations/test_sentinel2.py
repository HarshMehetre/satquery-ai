import pytest

from app.executor.context import ExecutionContext
from app.operations.satellite.retrieve import (
    Sentinel2RetrievalOperation,
)
from app.schemas.operation import Operation
from app.schemas.query import AOI


def create_context() -> ExecutionContext:
    return ExecutionContext(
        aoi=AOI(
            type="bbox",
            value=[73.0, 18.0, 73.1, 18.1],
        )
    )


def create_operation() -> Operation:
    return Operation(
        id="sentinel_2",
        type="get_satellite_imagery",
        inputs=[],
        parameters={
            "bbox": [73.0, 18.0, 73.1, 18.1],
            "start_date": "2026-01-01",
            "end_date": "2026-01-31",
        },
    )


def test_sentinel2_requires_no_inputs() -> None:
    context = create_context()

    operation = create_operation()

    Sentinel2RetrievalOperation().validate(
        operation,
        context,
    )


def test_sentinel2_rejects_inputs() -> None:
    context = create_context()

    operation = create_operation()
    operation.inputs = ["unexpected_input"]

    with pytest.raises(
        ValueError,
        match="does not require inputs",
    ):
        Sentinel2RetrievalOperation().validate(
            operation,
            context,
        )


def test_sentinel2_requires_bbox() -> None:
    context = create_context()

    operation = create_operation()
    operation.parameters.pop("bbox")

    with pytest.raises(
        ValueError,
        match="Missing Sentinel-2 parameters",
    ):
        Sentinel2RetrievalOperation().validate(
            operation,
            context,
        )


def test_sentinel2_validates_bbox_length() -> None:
    context = create_context()

    operation = create_operation()
    operation.parameters["bbox"] = [73.0, 18.0]

    with pytest.raises(
        ValueError,
        match="four values",
    ):
        Sentinel2RetrievalOperation().validate(
            operation,
            context,
        )


def test_sentinel2_evalscript_contains_required_bands() -> None:
    evalscript = (
        Sentinel2RetrievalOperation._build_evalscript()
    )

    assert "B04" in evalscript
    assert "B08" in evalscript
    assert "REFLECTANCE" in evalscript