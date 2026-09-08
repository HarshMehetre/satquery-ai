from app.planner.interface import QueryPlanner
from app.schemas.operation import Operation
from app.schemas.query import AOI, OutputSpec, QueryPlan

HERO_QUERY = (
    "Find areas where vegetation decreased between 2024 and 2026 "
    "that are within 3 km of major roads."
)


class MockQueryPlanner(QueryPlanner):
    """Deterministic planner used for testing the planning pipeline."""

    def plan(self, query: str) -> QueryPlan:
        if query != HERO_QUERY:
            raise ValueError(
                f"Unsupported mock query: '{query}'."
            )

        return QueryPlan(
            plan_id="hero_vegetation_loss",
            aoi=AOI(
                type="bbox",
                value=[73.0, 18.0, 73.1, 18.1],
            ),
            operations=[
                Operation(
                    id="s2_2024",
                    type="get_satellite_imagery",
                    parameters={
                        "bbox": [73.0, 18.0, 73.1, 18.1],
                        "start_date": "2024-01-01",
                        "end_date": "2024-12-31",
                        "max_cloud_coverage": 30,
                        "width": 4,
                        "height": 4,
                    },
                ),
                Operation(
                    id="s2_2026",
                    type="get_satellite_imagery",
                    parameters={
                        "bbox": [73.0, 18.0, 73.1, 18.1],
                        "start_date": "2026-01-01",
                        "end_date": "2026-12-31",
                        "max_cloud_coverage": 30,
                        "width": 4,
                        "height": 4,
                    },
                ),
                Operation(
                    id="roads",
                    type="get_osm_features",
                    parameters={
                        "bbox": [73.0, 18.0, 73.1, 18.1],
                        "feature_type": "roads",
                    },
                ),
                Operation(
                    id="ndvi_2024",
                    type="calculate_ndvi",
                    inputs=["s2_2024"],
                    parameters={
                        "red_band": "B4",
                        "nir_band": "B8",
                    },
                ),
                Operation(
                    id="ndvi_2026",
                    type="calculate_ndvi",
                    inputs=["s2_2026"],
                    parameters={
                        "red_band": "B4",
                        "nir_band": "B8",
                    },
                ),
                Operation(
                    id="vegetation_change",
                    type="temporal_difference",
                    inputs=["ndvi_2024", "ndvi_2026"],
                ),
                Operation(
                    id="vegetation_loss",
                    type="vegetation_loss",
                    inputs=["vegetation_change"],
                    parameters={
                        "threshold": -0.1,
                    },
                ),
                Operation(
                    id="loss_polygons",
                    type="raster_polygonize",
                    inputs=["vegetation_loss"],
                ),
                Operation(
                    id="loss_projected",
                    type="project_to_crs",
                    inputs=["loss_polygons"],
                    parameters={
                        "target_crs": "EPSG:32643",
                    },
                ),
                Operation(
                    id="roads_projected",
                    type="project_to_crs",
                    inputs=["roads"],
                    parameters={
                        "target_crs": "EPSG:32643",
                    },
                ),
                Operation(
                    id="road_buffer",
                    type="buffer",
                    inputs=["roads_projected"],
                    parameters={
                        "distance_m": 3000,
                    },
                ),
                Operation(
                    id="final",
                    type="intersection",
                    inputs=["loss_projected", "road_buffer"],
                ),
                Operation(
                    id="area",
                    type="area",
                    inputs=["final"],
                ),
            ],
            output=OutputSpec(
                type="map",
                include_geometry=True,
                include_statistics=True,
                include_evidence=True,
            ),
        )