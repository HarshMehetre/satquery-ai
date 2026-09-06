import pytest

from app.executor.context import ExecutionContext
from app.schemas import (
    AOI,
    DataInput,
    Evidence,
    OperationResult,
)


def test_context_initialization():
    aoi = AOI(
        type="polygon",
        value="USER_AOI",
    )

    inputs = [
        DataInput(
            id="s2_2024",
            source="sentinel-2",
            purpose="vegetation",
        )
    ]

    context = ExecutionContext(
        aoi=aoi,
        inputs=inputs,
    )

    assert context.aoi == aoi
    assert "s2_2024" in context.inputs
    assert context.results == {}
    assert context.evidence == []


def test_add_and_get_result():
    aoi = AOI(
        type="polygon",
        value="USER_AOI",
    )

    context = ExecutionContext(aoi=aoi)

    result = OperationResult(
        id="ndvi_2024",
        type="calculate_ndvi",
        data_type="raster",
        data="mock_ndvi_raster",
    )

    context.add_result(result)

    retrieved = context.get_result("ndvi_2024")

    assert retrieved == result
    assert retrieved.data == "mock_ndvi_raster"


def test_missing_result_raises_error():
    aoi = AOI(
        type="polygon",
        value="USER_AOI",
    )

    context = ExecutionContext(aoi=aoi)

    with pytest.raises(KeyError):
        context.get_result("does_not_exist")


def test_add_evidence():
    aoi = AOI(
        type="polygon",
        value="USER_AOI",
    )

    context = ExecutionContext(aoi=aoi)

    evidence = Evidence(
        source="sentinel-2",
        source_type="satellite",
        operation="calculate_ndvi",
        description="NDVI calculated from Sentinel-2 imagery.",
    )

    context.add_evidence(evidence)

    assert len(context.evidence) == 1
    assert context.evidence[0] == evidence
    
def test_runtime_input() -> None:
    context = ExecutionContext(
        aoi=AOI(
            type="place",
            value="Pune",
        ),
    )

    context.add_runtime_input(
        "satellite_data",
        {"test": "raster"},
    )

    assert context.get_runtime_input(
        "satellite_data"
    ) == {"test": "raster"}

def test_missing_runtime_input_raises_error() -> None:
    context = ExecutionContext(
        aoi=AOI(
            type="place",
            value="Pune",
        )
    )

    with pytest.raises(KeyError):
        context.get_runtime_input("missing")