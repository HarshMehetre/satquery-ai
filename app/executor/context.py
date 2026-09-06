from typing import Any

from app.schemas.evidence import Evidence
from app.schemas.query import AOI, DataInput
from app.schemas.result import OperationResult


class ExecutionContext:
    def __init__(
        self,
        aoi: AOI,
        inputs: list[DataInput] | None = None,
        runtime_inputs: dict[str, Any] | None = None,
    ) -> None:
        self.aoi = aoi

        # Plan-level descriptions of external inputs.
        self.inputs: dict[str, DataInput] = {
            item.id: item
            for item in (inputs or [])
        }

        # Actual runtime data associated with external inputs.
        self.runtime_inputs: dict[str, Any] = runtime_inputs or {}

        # Results produced by operations during execution.
        self.results: dict[str, OperationResult] = {}

        self.evidence: list[Evidence] = []
        self.metadata: dict[str, Any] = {}

    def add_runtime_input(
        self,
        input_id: str,
        data: Any,
    ) -> None:
        self.runtime_inputs[input_id] = data

    def get_runtime_input(self, input_id: str) -> Any:
        if input_id not in self.runtime_inputs:
            raise KeyError(
                f"Runtime input '{input_id}' does not exist."
            )

        return self.runtime_inputs[input_id]

    def add_result(self, result: OperationResult) -> None:
        self.results[result.id] = result

    def get_result(self, result_id: str) -> OperationResult:
        if result_id not in self.results:
            raise KeyError(
                f"Operation result '{result_id}' does not exist."
            )

        return self.results[result_id]
    
    def get_input_result(self, input_id: str) -> OperationResult:
        """Resolve an operation result or runtime input by ID."""
        if input_id in self.results:
            return self.results[input_id]

        if input_id in self.runtime_inputs:
            runtime_data = self.runtime_inputs[input_id]

            if isinstance(runtime_data, OperationResult):
                return runtime_data

            raise TypeError(
                f"Runtime input '{input_id}' must be an OperationResult."
            )

        raise KeyError(
            f"Input '{input_id}' does not exist in execution context."
        )

    def add_evidence(self, evidence: Evidence) -> None:
        self.evidence.append(evidence)