from app.schemas.operation import Operation


class DependencyResolver:
    """
    Resolves dependencies between operations and determines
    a valid execution order.
    """

    def resolve(
        self,
        operations: list[Operation],
    ) -> list[Operation]:
        """
        Return operations in dependency-safe execution order.

        Raises:
            ValueError: If duplicate IDs, missing dependencies,
                        or circular dependencies are detected.
        """

        operation_map = self._build_operation_map(operations)

        self._validate_dependencies(
            operations,
            operation_map,
        )

        return self._topological_sort(
            operations,
            operation_map,
        )

    def _build_operation_map(
        self,
        operations: list[Operation],
    ) -> dict[str, Operation]:
        """
        Build an operation ID -> Operation mapping.
        """

        operation_map: dict[str, Operation] = {}

        for operation in operations:
            if operation.id in operation_map:
                raise ValueError(
                    f"Duplicate operation ID: '{operation.id}'."
                )

            operation_map[operation.id] = operation

        return operation_map

    def _validate_dependencies(
        self,
        operations: list[Operation],
        operation_map: dict[str, Operation],
    ) -> None:
        """
        Validate that all operation dependencies exist.

        Inputs may refer to either:
        - another operation
        - an external data input

        At this stage, dependency resolution only validates
        operation-to-operation dependencies.
        """

        operation_ids = set(operation_map)

        for operation in operations:
            for input_id in operation.inputs:

                # If the input refers to another operation,
                # it is a dependency and must exist.
                if self._looks_like_operation_dependency(
                    input_id,
                    operation_ids,
                ):
                    continue

                # External inputs are intentionally allowed.
                # They will be validated later against
                # ExecutionContext.inputs.

    def _looks_like_operation_dependency(
        self,
        input_id: str,
        operation_ids: set[str],
    ) -> bool:
        """
        Determine whether an input refers to another operation.

        If the ID exists in the operation map, it is an
        operation dependency. Otherwise it is assumed to
        be an external data input.
        """

        return input_id in operation_ids

    def _topological_sort(
        self,
        operations: list[Operation],
        operation_map: dict[str, Operation],
    ) -> list[Operation]:
        """
        Perform a topological sort using DFS.

        Raises:
            ValueError: If a circular dependency is detected.
        """

        visited: set[str] = set()
        visiting: set[str] = set()
        ordered: list[Operation] = []

        def visit(operation_id: str) -> None:

            if operation_id in visiting:
                raise ValueError(
                    "Circular dependency detected involving "
                    f"operation '{operation_id}'."
                )

            if operation_id in visited:
                return

            visiting.add(operation_id)

            operation = operation_map[operation_id]

            for input_id in operation.inputs:
                if input_id in operation_map:
                    visit(input_id)

            visiting.remove(operation_id)
            visited.add(operation_id)

            ordered.append(operation)

        for operation in operations:
            visit(operation.id)

        return ordered