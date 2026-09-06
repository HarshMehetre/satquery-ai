import numpy as np
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
        match="Missing required parameters",
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


def test_sentinel2_retrieval_populates_georeferencing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context = create_context()

    operation = create_operation()
    operation.parameters.update(
        {
            "width": 256,
            "height": 256,
        }
    )

    mock_data = np.zeros(
        (256, 256, 2),
        dtype=np.float32,
    )

    class MockRequest:
        @staticmethod
        def input_data(*args, **kwargs) -> object:
            return object()

        @staticmethod
        def output_response(*args, **kwargs) -> object:
            return object()

        def __init__(self, *args, **kwargs) -> None:
            pass

        def get_data(self) -> list[np.ndarray]:
            return [mock_data]

    monkeypatch.setattr(
        "app.operations.satellite.retrieve.SentinelHubRequest",
        MockRequest,
    )

    monkeypatch.setattr(
        "app.operations.satellite.retrieve.settings.sentinel_client_id",
        "test-client-id",
    )

    monkeypatch.setattr(
        "app.operations.satellite.retrieve.settings.sentinel_client_secret",
        "test-client-secret",
    )

    result = Sentinel2RetrievalOperation().execute(
        operation,
        context,
    )

    raster = result.data

    bbox = operation.parameters["bbox"]
    width = operation.parameters["width"]
    height = operation.parameters["height"]

    expected_x_resolution = (
        bbox[2] - bbox[0]
    ) / width

    expected_y_resolution = (
        bbox[3] - bbox[1]
    ) / height

    assert raster.data.shape == (
        2,
        height,
        width,
    )

    assert raster.bands == ["B4", "B8"]

    assert raster.metadata.crs == "EPSG:4326"

    assert raster.metadata.transform is not None

    assert raster.metadata.bounds == (
        bbox[0],
        bbox[1],
        bbox[2],
        bbox[3],
    )

    assert raster.metadata.resolution == (
        expected_x_resolution,
        expected_y_resolution,
    )

    transform = raster.metadata.transform

    assert transform.a == expected_x_resolution
    assert transform.e == -expected_y_resolution
    assert transform.c == bbox[0]
    assert transform.f == bbox[3]