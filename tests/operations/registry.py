from app.operations.gis.area import AreaOperation
from app.operations.gis.buffer import BufferOperation
from app.operations.gis.intersection import IntersectionOperation
from app.operations.gis.project import ProjectToCRSOperation
from app.operations.remote_sensing.change import TemporalDifferenceOperation
from app.operations.remote_sensing.filter import VegetationLossOperation
from app.operations.remote_sensing.ndvi import NDVIOperation
from app.operations.remote_sensing.polygonize import RasterPolygonizeOperation
from app.registry.operations import OperationRegistry
from tests.operations.mocks import (
    MockCombineOperation,
    MockOSMRetrievalOperation,
    MockRasterSourceOperation,
    MockSentinel2RetrievalOperation,
    MockSourceOperation,
    MockTransformOperation,
)


def create_mock_registry(
    osm_retrieval_operation=MockOSMRetrievalOperation,
) -> OperationRegistry:
    registry = OperationRegistry()

    registry.register(
        "mock_source",
        MockSourceOperation,
    )

    registry.register(
        "mock_transform",
        MockTransformOperation,
    )

    registry.register(
        "mock_combine",
        MockCombineOperation,
    )
    
    registry.register(
        "mock_raster_source",
        MockRasterSourceOperation,
    )
    
    registry.register(
        "get_satellite_imagery",
        MockSentinel2RetrievalOperation,
    )
    
    registry.register(
        "project_to_crs",
        ProjectToCRSOperation,
    )
    
    registry.register(
        "buffer",
        BufferOperation,
    )

    registry.register(
        "intersection",
        IntersectionOperation,
    )
    
    registry.register(
        "area",
        AreaOperation,
    )
    
    registry.register(
        "get_osm_features",
        osm_retrieval_operation,
    )
    
    registry.register(
        "temporal_difference",
        TemporalDifferenceOperation,
    )
    
    registry.register(
        "vegetation_loss",
        VegetationLossOperation,
    )

    registry.register(
        "raster_polygonize",
        RasterPolygonizeOperation,
    )
    
    registry.register(
        "calculate_ndvi",
        NDVIOperation,
    )

    return registry