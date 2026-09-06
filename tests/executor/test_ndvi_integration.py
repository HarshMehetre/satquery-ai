import numpy as np

from app.executor.executor import Executor
from app.operations.remote_sensing.ndvi import NDVIOperation
from app.registry.operations import OperationRegistry
from app.schemas.operation import Operation
from app.schemas.query import AOI, OutputSpec, QueryPlan
from app.schemas.raster import RasterData
from tests.operations.mocks import MockRasterSourceOperation


def create_registry() -> OperationRegistry:
    registry = OperationRegistry()

    registry.register(
        "mock_raster_source",
        MockRasterSourceOperation,
    )

    registry.register(
        "calculate_ndvi",
        NDVIOperation,
    )

    return registry


def test_executor_runs_ndvi_pipeline() -> None:
    registry = create_registry()
    executor = Executor(registry)

    plan = QueryPlan(
        plan_id="ndvi_integration_001",
        aoi=AOI(
            type="place",
            value="Pune",
        ),
        inputs=[],
        operations=[
            Operation(
                id="imagery",
                type="mock_raster_source",
                inputs=[],
            ),
            Operation(
                id="ndvi",
                type="calculate_ndvi",
                inputs=["imagery"],
                parameters={
                    "red_band": "B4",
                    "nir_band": "B8",
                },
            ),
        ],
        output=OutputSpec(
            type="raster",
            include_geometry=False,
            include_statistics=True,
            include_evidence=True,
        ),
    )

    result = executor.execute(plan)

    assert "imagery" in result.results
    assert "ndvi" in result.results

    ndvi_result = result.results["ndvi"]

    assert ndvi_result.data_type == "raster"
    assert isinstance(ndvi_result.data, RasterData)

    assert ndvi_result.data.bands == ["NDVI"]
    assert ndvi_result.data.data.shape == (1, 2, 2)

    expected = np.array(
        [
            [0.5, 0.33333334],
            [0.4, 0.2857143],
        ],
        dtype=np.float32,
    )

    np.testing.assert_allclose(
        ndvi_result.data.data[0],
        expected,
        rtol=1e-5,
        atol=1e-5,
    )