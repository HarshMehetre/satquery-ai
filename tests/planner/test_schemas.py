from app.schemas.query import QueryPlan


def test_valid_query_plan():
    plan = QueryPlan(
        plan_id="test_001",
        aoi={
            "type": "bbox",
            "value": [73.7, 18.4, 73.9, 18.6],
        },
        inputs=[
            {
                "id": "s2_2026",
                "source": "sentinel-2",
                "purpose": "vegetation_analysis",
                "time_range": {
                    "start": "2026-01-01",
                    "end": "2026-12-31",
                },
            }
        ],
        operations=[
            {
                "id": "ndvi",
                "type": "calculate_ndvi",
                "inputs": ["s2_2026"],
            }
        ],
    )

    assert plan.plan_id == "test_001"
    assert plan.operations[0].type == "calculate_ndvi"