from app.operations.gis.area import AreaOperation
from app.operations.gis.buffer import BufferOperation
from app.operations.gis.intersection import IntersectionOperation
from app.operations.gis.osm import OSMRetrievalOperation
from app.operations.gis.project import ProjectToCRSOperation
from app.operations.satellite.retrieve import (
    Sentinel2RetrievalOperation,
)
from app.registry.operations import OperationRegistry
from tests.operations.mocks import (
    MockCombineOperation,
    MockRasterSourceOperation,
    MockSourceOperation,
    MockTransformOperation,
)


def create_mock_registry() -> OperationRegistry:
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
        Sentinel2RetrievalOperation,
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
        OSMRetrievalOperation,
    )

    return registry