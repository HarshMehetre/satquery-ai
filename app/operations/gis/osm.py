from typing import ClassVar

import geopandas as gpd
import osmnx as ox

from app.executor.context import ExecutionContext
from app.operations.base import BaseOperation
from app.schemas.operation import Operation
from app.schemas.result import OperationResult


class OSMRetrievalOperation(BaseOperation):
    """Retrieve OpenStreetMap features for an area."""

    FEATURE_TAGS: ClassVar[dict[str, dict[str, bool]]] = {
        "roads": {"highway": True},
        "buildings": {"building": True},
        "waterways": {"waterway": True},
    }

    MAJOR_ROAD_CLASSES: ClassVar[set[str]] = {
        "motorway",
        "motorway_link",
        "trunk",
        "trunk_link",
        "primary",
        "primary_link",
        "secondary",
        "secondary_link",
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

        required_parameters = {
            "feature_type",
        }

        missing_parameters = (
            required_parameters - set(operation.parameters)
        )

        if missing_parameters:
            raise ValueError(
                "Missing required parameters: "
                f"{sorted(missing_parameters)}"
            )

        self._get_aoi_bbox(context)

        feature_type = operation.parameters["feature_type"]

        if feature_type not in self.FEATURE_TAGS:
            raise ValueError(
                f"Unsupported feature_type '{feature_type}'. "
                f"Supported types: {sorted(self.FEATURE_TAGS)}"
            )

    def execute(
        self,
        operation: Operation,
        context: ExecutionContext,
    ) -> OperationResult:
        self.validate(operation, context)

        bbox = self._get_aoi_bbox(context)
        feature_type = operation.parameters["feature_type"]

        features = ox.features_from_bbox(
            bbox=tuple(bbox),
            tags=self.FEATURE_TAGS[feature_type],
        )

        if features.empty:
            raise RuntimeError(
                f"No OSM features found for feature_type "
                f"'{feature_type}'."
            )

        features = features.reset_index()

        if feature_type == "roads":
            features = self._filter_major_roads(features)

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
            },
        )

    @staticmethod
    def _get_aoi_bbox(context: ExecutionContext) -> list[float]:
        """Return the authoritative bbox from the resolved AOI."""

        if not context.aoi.resolved:
            raise ValueError(
                "OSM retrieval requires a resolved AOI."
            )

        if context.aoi.type != "bbox":
            raise ValueError(
                "OSM retrieval requires a resolved bbox AOI."
            )

        bbox = context.aoi.value

        if not isinstance(bbox, (list, tuple)) or len(bbox) != 4:
            raise ValueError(
                "Resolved AOI bbox must contain four values: "
                "[west, south, east, north]."
            )

        west, south, east, north = bbox

        if west >= east or south >= north:
            raise ValueError(
                "Invalid resolved AOI bbox: west must be less "
                "than east and south must be less than north."
            )

        return list(bbox)

    def _filter_major_roads(
        self,
        features: gpd.GeoDataFrame,
    ) -> gpd.GeoDataFrame:
        if "highway" not in features.columns:
            raise ValueError(
                "OSM road data does not contain a 'highway' column."
            )

        major_roads = features[
            features["highway"].apply(
                self._is_major_road
            )
        ].copy()

        if major_roads.empty:
            raise RuntimeError(
                "No major roads found in the requested area."
            )

        return major_roads

    def _is_major_road(self, value: object) -> bool:
        if isinstance(value, list):
            return any(
                road_class in self.MAJOR_ROAD_CLASSES
                for road_class in value
            )

        return value in self.MAJOR_ROAD_CLASSES

    @classmethod
    def planner_metadata(cls) -> dict[str, object]:
        return {
            "description": (
                "Retrieve OpenStreetMap features within "
                "the resolved AOI."
            ),
            "parameters": {
                "feature_type": "OSM feature category.",
            },
            "input_type": "aoi",
            "output_type": "vector",
            "spatial_extent": (
                "Uses the resolved AOI exclusively; "
                "operation parameters must not define a bbox."
            ),
        }