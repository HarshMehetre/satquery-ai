from app.schemas.evidence import Evidence
from app.schemas.operation import Operation
from app.schemas.result import OperationResult


class EvidenceBuilder:
    """Build provenance evidence from executed operations and results."""

    def build(
        self,
        operation: Operation,
        result: OperationResult,
    ) -> Evidence:
        metadata = result.metadata

        return Evidence(
            source=metadata.get("source", "unknown"),
            source_type=metadata.get(
                "source_type",
                "operation",
            ),
            acquisition_date=metadata.get(
                "acquisition_date",
            ),
            operation=operation.type,
            parameters=operation.parameters,
            description=metadata.get(
                "description",
            ),
        )