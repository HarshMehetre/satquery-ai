from app.registry import OperationRegistry
from app.schemas.query import QueryPlan


class QueryPlanValidator:
    """Validate a QueryPlan against the available operation registry."""

    def __init__(self, registry: OperationRegistry) -> None:
        self.registry = registry

    def validate(self, plan: QueryPlan) -> None:
        self._validate_aoi(plan)
        self._validate_operation_types(plan)
        self._validate_operation_ids(plan)
        self._validate_inputs(plan)

    def _validate_aoi(self, plan: QueryPlan) -> None:
        if not plan.aoi.resolved:
            raise ValueError(
                "AOI must be resolved before query execution."
            )

    def _validate_operation_types(self, plan: QueryPlan) -> None:
        registered_operations = set(self.registry.list_operations())

        for operation in plan.operations:
            if operation.type not in registered_operations:
                raise ValueError(
                    f"Unknown operation type '{operation.type}' "
                    f"for operation '{operation.id}'."
                )

    def _validate_operation_ids(self, plan: QueryPlan) -> None:
        operation_ids = [operation.id for operation in plan.operations]

        if len(operation_ids) != len(set(operation_ids)):
            raise ValueError("Operation IDs must be unique.")

    def _validate_inputs(self, plan: QueryPlan) -> None:
        operation_ids = {operation.id for operation in plan.operations}
        declared_inputs = {input_data.id for input_data in plan.inputs}

        for operation in plan.operations:
            for input_id in operation.inputs:
                if input_id not in operation_ids and input_id not in declared_inputs:
                    raise ValueError(
                        f"Input '{input_id}' required by operation "
                        f"'{operation.id}' is not declared or produced."
                    )