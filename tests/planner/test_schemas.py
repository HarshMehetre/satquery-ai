from app.schemas import (
    AOI,
    DataInput,
    Operation,
    OutputSpec,
    QueryPlan,
    TimeRange,
)


def test_query_plan_creation():
    plan = QueryPlan(
        plan_id="hero_001",

        aoi=AOI(
            type="polygon",
            value="USER_AOI",
        ),

        inputs=[
            DataInput(
                id="s2_2024",
                source="sentinel-2",
                purpose="vegetation",
                time_range=TimeRange(
                    start="2024-01-01",
                    end="2024-12-31",
                ),
            ),
            DataInput(
                id="s2_2026",
                source="sentinel-2",
                purpose="vegetation",
                time_range=TimeRange(
                    start="2026-01-01",
                    end="2026-12-31",
                ),
            ),
            DataInput(
                id="roads",
                source="osm",
                purpose="major_roads",
            ),
        ],

        operations=[
            Operation(
                id="ndvi_2024",
                type="calculate_ndvi",
                inputs=["s2_2024"],
            ),
            Operation(
                id="ndvi_2026",
                type="calculate_ndvi",
                inputs=["s2_2026"],
            ),
            Operation(
                id="vegetation_change",
                type="temporal_difference",
                inputs=[
                    "ndvi_2024",
                    "ndvi_2026",
                ],
            ),
            Operation(
                id="road_buffer",
                type="buffer",
                inputs=["roads"],
                parameters={
                    "distance_m": 3000,
                },
            ),
            Operation(
                id="final",
                type="intersection",
                inputs=[
                    "vegetation_change",
                    "road_buffer",
                ],
            ),
        ],

        output=OutputSpec(
            type="map",
            include_geometry=True,
            include_statistics=True,
            include_evidence=True,
        ),
    )

    assert plan.plan_id == "hero_001"
    assert len(plan.inputs) == 3
    assert len(plan.operations) == 5
    assert plan.output.type == "map"