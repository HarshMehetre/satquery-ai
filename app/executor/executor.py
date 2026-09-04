from app.executor.context import ExecutionContext
from app.executor.dependency import DependencyResolver
from app.registry.operations import OperationRegistry
from app.schemas.query import QueryPlan
from app.schemas.result import ExecutionResult
from app.schemas.operation import Operation


class Executor:
    def __init__(
        self,
        registry: OperationRegistry,
        dependency_resolver: DependencyResolver | None = None,
    ) -> None:
        self.registry = registry
        self.dependency_resolver = (
            dependency_resolver or DependencyResolver()
        )

    def execute(self, plan: QueryPlan) -> ExecutionResult:
        context = ExecutionContext(
            aoi=plan.aoi,
            inputs=plan.inputs,
        )

        ordered_operations = self.dependency_resolver.resolve(
            plan.operations
        )

        for operation in ordered_operations:
            self._validate_inputs(operation, context)

            operation_class = self.registry.get(operation.type)
            handler = operation_class()

            handler.validate(operation, context)

            result = handler.execute(
                operation,
                context,
            )

            context.add_result(result)

        return ExecutionResult(
            results=context.results,
            evidence=context.evidence,
            metadata=context.metadata,
        )

    def _validate_inputs(
        self,
        operation,
        context: ExecutionContext,
    ) -> None:
        for input_id in operation.inputs:
            if (
                input_id not in context.inputs
                and input_id not in context.results
            ):
                raise KeyError(
                    f"Input '{input_id}' required by operation "
                    f"'{operation.id}' does not exist."
                )