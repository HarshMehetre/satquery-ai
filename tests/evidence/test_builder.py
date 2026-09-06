from app.evidence.builder import EvidenceBuilder
from app.schemas.operation import Operation
from app.schemas.result import OperationResult


def test_build_evidence_from_operation_result() -> None:
    operation = Operation(
        id="s2_2024",
        type="get_satellite_imagery",
        parameters={
            "bbox": [73.0, 18.0, 73.1, 18.1],
            "start_date": "2024-01-01",
            "end_date": "2024-12-31",
        },
    )

    result = OperationResult(
        id="s2_2024",
        type="get_satellite_imagery",
        data_type="raster",
        data=None,
        metadata={
            "source": "sentinel-2",
            "source_type": "satellite",
            "acquisition_date": "2024-06-15",
            "description": "Sentinel-2 L2A imagery",
        },
    )

    evidence = EvidenceBuilder().build(
        operation,
        result,
    )

    assert evidence.source == "sentinel-2"
    assert evidence.source_type == "satellite"
    assert evidence.acquisition_date == "2024-06-15"
    assert evidence.operation == "get_satellite_imagery"
    assert evidence.parameters == operation.parameters
    assert evidence.description == "Sentinel-2 L2A imagery"


def test_build_evidence_uses_defaults_when_metadata_is_missing() -> None:
    operation = Operation(
        id="ndvi_2024",
        type="calculate_ndvi",
    )

    result = OperationResult(
        id="ndvi_2024",
        type="calculate_ndvi",
        data_type="raster",
        data=None,
    )

    evidence = EvidenceBuilder().build(
        operation,
        result,
    )

    assert evidence.source == "unknown"
    assert evidence.source_type == "operation"
    assert evidence.acquisition_date is None
    assert evidence.operation == "calculate_ndvi"
    assert evidence.parameters == {}
    assert evidence.description is None