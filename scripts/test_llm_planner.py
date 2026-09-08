from app.planner.openai import OpenAIQueryPlanner
from app.planner.validator import QueryPlanValidator
from app.registry import create_production_registry

HERO_QUERY = (
    "Find areas where vegetation decreased between 2024 and 2026 "
    "that are within 3 km of major roads."
)


def main() -> None:
    registry = create_production_registry()

    planner = OpenAIQueryPlanner(
        registry=registry,
    )

    validator = QueryPlanValidator(registry)

    print("Generating QueryPlan...")
    plan = planner.plan(HERO_QUERY)

    print("\nGenerated QueryPlan:")
    print(plan.model_dump_json(indent=2))

    print("\nValidating QueryPlan...")
    validator.validate(plan)

    print("✓ QueryPlan validation passed")


if __name__ == "__main__":
    main()