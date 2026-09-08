from app.operations.base import BaseOperation
from app.operations.gis.area import AreaOperation
from app.operations.gis.buffer import BufferOperation
from app.operations.gis.intersection import IntersectionOperation
from app.operations.gis.osm import OSMRetrievalOperation
from app.operations.gis.project import ProjectToCRSOperation
from app.operations.remote_sensing.change import TemporalDifferenceOperation
from app.operations.remote_sensing.filter import VegetationLossOperation
from app.operations.remote_sensing.ndvi import NDVIOperation
from app.operations.remote_sensing.polygonize import RasterPolygonizeOperation
from app.operations.satellite.retrieve import Sentinel2RetrievalOperation


class OperationRegistry:
    """
    Registry mapping operation names to their implementation classes.
    """

    def __init__(self) -> None:
        self._operations: dict[str, type[BaseOperation]] = {}

    def register(
        self,
        name: str,
        operation_class: type[BaseOperation],
    ) -> None:
        """
        Register an operation implementation.
        """

        if name in self._operations:
            raise ValueError(
                f"Operation '{name}' is already registered."
            )

        self._operations[name] = operation_class

    def get(
        self,
        name: str,
    ) -> type[BaseOperation]:
        """
        Retrieve an operation implementation by name.
        """

        if name not in self._operations:
            raise KeyError(
                f"Operation '{name}' is not registered."
            )

        return self._operations[name]

    def contains(
        self,
        name: str,
    ) -> bool:
        """
        Check whether an operation is registered.
        """

        return name in self._operations

    def list_operations(
        self,
    ) -> list[str]:
        """
        Return all registered operation names.
        """

        return list(self._operations.keys())
    
    def get_catalog(self) -> list[dict[str, object]]:
        """Return planner-facing metadata for all registered operations."""
        return [
            {
            "type": operation_type,
            **operation_class.planner_metadata(),
            }
            for operation_type, operation_class in self._operations.items()
        ]


def create_production_registry() -> OperationRegistry:
    """Create a registry containing all implemented production operations."""

    registry = OperationRegistry()

    registry.register(
        "get_satellite_imagery",
        Sentinel2RetrievalOperation,
    )
    registry.register(
        "calculate_ndvi",
        NDVIOperation,
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

    return registry