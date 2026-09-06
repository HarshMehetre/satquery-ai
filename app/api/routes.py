from typing import Any

from fastapi import APIRouter, Depends

from app.executor.executor import Executor
from app.registry import create_production_registry
from app.schemas.query import QueryPlan
from app.schemas.result import ExecutionResult

router = APIRouter()


def get_executor() -> Executor:
    return Executor(
        registry=create_production_registry(),
    )


@router.post(
    "/query",
    response_model=dict[str, Any],
)
def execute_query(
    plan: QueryPlan,
    executor: Executor = Depends(get_executor),  # noqa: B008
) -> dict[str, Any]:
    result = executor.execute(plan)

    return serialize_execution_result(result)


def serialize_execution_result(
    result: ExecutionResult,
) -> dict[str, Any]:
    serialized_results: dict[str, Any] = {}

    for result_id, operation_result in result.results.items():
        data = operation_result.data

        if operation_result.data_type == "raster":
            data = {
                "type": "raster",
                "bands": data.bands,
                "metadata": data.metadata.model_dump(
                    mode="json",
                ),
            }

        elif operation_result.data_type == "vector":
            data = data.__geo_interface__

        serialized_results[result_id] = {
            "id": operation_result.id,
            "type": operation_result.type,
            "data_type": operation_result.data_type,
            "data": data,
            "metadata": operation_result.metadata,
            "confidence": operation_result.confidence,
        }

    return {
        "results": serialized_results,
        "evidence": [
            evidence.model_dump(mode="json")
            for evidence in result.evidence
        ],
        "metadata": result.metadata,
    }