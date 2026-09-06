from typing import ClassVar

import geopandas as gpd
import osmnx as ox

from app.executor.context import ExecutionContext
from app.operations.base import BaseOperation
from app.schemas.operation import Operation
from app.schemas.result import OperationResult


class OSMRetrievalOperation(BaseOperation):
    """Retrieve OpenStreetMap vector features for an area."""

    FEATURE_TAGS: ClassVar[dict[str, dict[str, bool]]] = {
        "roads": {"highway": True},
        "buildings": {"building": True},
        "waterways": {"waterway": True},
    }

    def validate(
        self,
        operation: Operation,
        context: ExecutionContext,
    ) -> None:
        if operation.inputs:
            raise ValueError(
                "OSMRetrievalOperation does not require inputs."
            )

        if "feature_type" not in operation.parameters:
            raise ValueError(
                "Missing required parameter: 'feature_type'."
            )

        feature_type = operation.parameters["feature_type"]

        if feature_type not in self.FEATURE_TAGS:
            raise ValueError(
                "Unsupported OSM feature_type. "
                "Supported values: roads, buildings, waterways."
            )

        self._resolve_bbox(operation, context)

    def execute(
        self,
        operation: Operation,
        context: ExecutionContext,
    ) -> OperationResult:
        self.validate(operation, context)

        feature_type = operation.parameters["feature_type"]
        bbox = self._resolve_bbox(operation, context)

        features = ox.features_from_bbox(
            bbox=bbox,
            tags=self.FEATURE_TAGS[feature_type],
        )

        if not isinstance(features, gpd.GeoDataFrame):
            raise TypeError(
                "OSM retrieval must return a GeoDataFrame."
            )

        return OperationResult(
            id=operation.id,
            type=operation.type,
            data_type="vector",
            data=features,
            metadata={
                "source": "openstreetmap",
                "feature_type": feature_type,
                "feature_count": len(features),
                "bbox": list(bbox),
                "crs": str(features.crs) if features.crs else None,
            },
        )

    @staticmethod
    def _resolve_bbox(
        operation: Operation,
        context: ExecutionContext,
    ) -> tuple[float, float, float, float]:
        if "bbox" in operation.parameters:
            bbox = operation.parameters["bbox"]
        elif context.aoi.type == "bbox":
            bbox = context.aoi.value
        else:
            raise ValueError(
                "OSM retrieval requires a bbox parameter "
                "or a bbox-type AOI."
            )

        if len(bbox) != 4:
            raise ValueError(
                "bbox must contain four values: "
                "[west, south, east, north]."
            )

        west, south, east, north = map(float, bbox)

        if west >= east or south >= north:
            raise ValueError(
                "Invalid bbox. Expected west < east and south < north."
            )

        return west, south, east, north