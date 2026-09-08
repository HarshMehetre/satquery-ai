from app.planner.gemini import GeminiQueryPlanner
from app.planner.validator import QueryPlanValidator
from app.registry import create_production_registry

HERO_QUERY = (
    "Find areas where vegetation decreased between 2024 and 2026 "
    "that are within 3 km of major roads."
)


def main() -> None:
    registry = create_production_registry()

    planner = GeminiQueryPlanner(
        registry=registry,
        model="gemini-3.5-flash-lite",
    )

    validator = QueryPlanValidator(registry)

    print("Generating QueryPlan with Gemini...")
    plan = planner.plan(HERO_QUERY)

    print("\nGenerated QueryPlan:")
    print(plan.model_dump_json(indent=2))

    print("\nValidating QueryPlan...")
    validator.validate(plan)

    print("\n✓ QueryPlan validation passed")


if __name__ == "__main__":
    main()