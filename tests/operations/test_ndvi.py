import pytest

from app.executor.context import ExecutionContext
from app.operations.remote_sensing.ndvi import NDVIOperation
from app.schemas.operation import Operation
from app.schemas.query import AOI, DataInput
import numpy as np


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


def test_ndvi_requires_one_input() -> None:
    context = create_context()

    operation = Operation(
        id="ndvi",
        type="calculate_ndvi",
        inputs=[],
        parameters={
            "red_band": "B4",
            "nir_band": "B8",
        },
    )

    with pytest.raises(
        ValueError,
        match="exactly one input",
    ):
        NDVIOperation().validate(operation, context)


def test_ndvi_requires_existing_input() -> None:
    context = create_context()

    operation = Operation(
        id="ndvi",
        type="calculate_ndvi",
        inputs=["missing"],
        parameters={
            "red_band": "B4",
            "nir_band": "B8",
        },
    )

    with pytest.raises(KeyError):
        NDVIOperation().validate(operation, context)


def test_ndvi_requires_band_parameters() -> None:
    context = create_context()

    operation = Operation(
        id="ndvi",
        type="calculate_ndvi",
        inputs=["satellite_data"],
        parameters={},
    )

    with pytest.raises(
        ValueError,
        match="Missing NDVI parameters",
    ):
        NDVIOperation().validate(operation, context)
        
def create_raster_context() -> ExecutionContext:
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
    
def test_ndvi_calculation() -> None:
    context = create_raster_context()

    operation = Operation(
        id="ndvi",
        type="calculate_ndvi",
        inputs=["satellite_data"],
        parameters={
            "red_band": "B4",
            "nir_band": "B8",
        },
    )

    source_data = {
        "B4": np.array(
            [[0.2, 0.4]],
            dtype=np.float32,
        ),
        "B8": np.array(
            [[0.6, 0.8]],
            dtype=np.float32,
        ),
    }

    # context.inputs["satellite_data"].purpose = source_data

    # For this test, directly test the calculation layer.
    result = NDVIOperation()._calculate(
        operation=operation,
        source_data=source_data,
        red_band="B4",
        nir_band="B8",
    )

    expected = np.array(
        [[0.5, 0.33333334]],
        dtype=np.float32,
    )

    np.testing.assert_allclose(
        result.data,
        expected,
        rtol=1e-5,
        atol=1e-5,
    )
    
def test_ndvi_handles_zero_denominator() -> None:
    operation = Operation(
        id="ndvi",
        type="calculate_ndvi",
        inputs=["satellite_data"],
        parameters={
            "red_band": "B4",
            "nir_band": "B8",
        },
    )

    source_data = {
        "B4": np.array(
            [[0.0, 0.2]],
            dtype=np.float32,
        ),
        "B8": np.array(
            [[0.0, 0.2]],
            dtype=np.float32,
        ),
    }

    result = NDVIOperation()._calculate(
        operation=operation,
        source_data=source_data,
        red_band="B4",
        nir_band="B8",
    )

    assert result.data[0, 0] == 0.0
    assert result.data[0, 1] == 0.0
    
def test_ndvi_rejects_shape_mismatch() -> None:
    operation = Operation(
        id="ndvi",
        type="calculate_ndvi",
        inputs=["satellite_data"],
        parameters={
            "red_band": "B4",
            "nir_band": "B8",
        },
    )

    source_data = {
        "B4": np.zeros((2, 2), dtype=np.float32),
        "B8": np.zeros((4, 4), dtype=np.float32),
    }

    with pytest.raises(
        ValueError,
        match="identical shapes",
    ):
        NDVIOperation()._calculate(
            operation=operation,
            source_data=source_data,
            red_band="B4",
            nir_band="B8",
        )
        
def test_ndvi_rejects_missing_band() -> None:
    operation = Operation(
        id="ndvi",
        type="calculate_ndvi",
        inputs=["satellite_data"],
        parameters={
            "red_band": "B4",
            "nir_band": "B8",
        },
    )

    source_data = {
        "B4": np.zeros((2, 2), dtype=np.float32),
    }

    with pytest.raises(
        KeyError,
        match="NIR band",
    ):
        NDVIOperation()._calculate(
            operation=operation,
            source_data=source_data,
            red_band="B4",
            nir_band="B8",
        )