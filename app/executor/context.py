from typing import Any

from app.schemas.evidence import Evidence
from app.schemas.query import AOI, DataInput
from app.schemas.result import OperationResult


class ExecutionContext:
    """
    Runtime state shared by operations during query execution.
    """

    def __init__(
        self,
        aoi: AOI,
        inputs: list[DataInput] | None = None,
    ) -> None:
        self.aoi = aoi

        self.inputs: dict[str, DataInput] = {
            item.id: item
            for item in (inputs or [])
        }

        self.results: dict[str, OperationResult] = {}

        self.evidence: list[Evidence] = []

        self.metadata: dict[str, Any] = {}

    def add_result(
        self,
        result: OperationResult,
    ) -> None:
        """
        Store the result of an executed operation.
        """

        self.results[result.id] = result

    def get_result(
        self,
        result_id: str,
    ) -> OperationResult:
        """
        Retrieve a previous operation result.
        """

        if result_id not in self.results:
            raise KeyError(
                f"Operation result '{result_id}' does not exist."
            )

        return self.results[result_id]

    def add_evidence(
        self,
        evidence: Evidence,
    ) -> None:
        """
        Add provenance information to the execution context.
        """

        self.evidence.append(evidence)