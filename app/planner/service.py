from app.executor.executor import Executor
from app.planner.aoi import AOIResolver
from app.planner.planner import QueryPlanner
from app.planner.validator import QueryPlanValidator
from app.schemas.result import ExecutionResult


class QueryService:
    """Orchestrate planning, AOI resolution, validation, and execution."""

    def __init__(
        self,
        planner: QueryPlanner,
        validator: QueryPlanValidator,
        executor: Executor,
        aoi_resolver: AOIResolver | None = None,
    ) -> None:
        self.planner = planner
        self.validator = validator
        self.executor = executor
        self.aoi_resolver = aoi_resolver or AOIResolver()

    def execute(
        self,
        query: str,
        runtime_inputs=None,
    ) -> ExecutionResult:
        plan = self.planner.plan(query)

        plan.aoi = self.aoi_resolver.resolve(plan.aoi)

        self.validator.validate(plan)

        return self.executor.execute(
            plan,
            runtime_inputs=runtime_inputs,
        )