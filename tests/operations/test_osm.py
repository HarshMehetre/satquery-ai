import geopandas as gpd
import osmnx as ox
import pytest
from shapely.geometry import LineString

from app.executor.context import ExecutionContext
from app.operations.gis.osm import OSMRetrievalOperation
from app.schemas.operation import Operation
from app.schemas.query import AOI


def create_context() -> ExecutionContext:
    return ExecutionContext(
        aoi=AOI(
            type="bbox",
            value=[73.80, 18.45, 73.90, 18.55],
        )
    )


def create_operation(
    feature_type: str = "roads",
) -> Operation:
    return Operation(
        id="osm",
        type="get_osm_features",
        inputs=[],
        parameters={
            "feature_type": feature_type,
            "bbox": [73.80, 18.45, 73.90, 18.55],
        },
    )


def test_osm_requires_feature_type() -> None:
    operation = Operation(
        id="osm",
        type="get_osm_features",
        inputs=[],
        parameters={
            "bbox": [73.80, 18.45, 73.90, 18.55],
        },
    )

    with pytest.raises(ValueError, match="feature_type"):
        OSMRetrievalOperation().validate(
            operation,
            create_context(),
        )


def test_osm_rejects_unsupported_feature_type() -> None:
    operation = create_operation("airports")

    with pytest.raises(ValueError, match="Unsupported"):
        OSMRetrievalOperation().validate(
            operation,
            create_context(),
        )


def test_osm_rejects_operation_inputs() -> None:
    operation = Operation(
        id="osm",
        type="get_osm_features",
        inputs=["previous"],
        parameters={
            "feature_type": "roads",
            "bbox": [73.80, 18.45, 73.90, 18.55],
        },
    )

    with pytest.raises(ValueError, match="does not require inputs"):
        OSMRetrievalOperation().validate(
            operation,
            create_context(),
        )


def test_osm_validates_bbox_length() -> None:
    operation = Operation(
        id="osm",
        type="get_osm_features",
        inputs=[],
        parameters={
            "feature_type": "roads",
            "bbox": [73.80, 18.45, 73.90],
        },
    )

    with pytest.raises(ValueError, match="four values"):
        OSMRetrievalOperation().validate(
            operation,
            create_context(),
        )


def test_osm_validates_bbox_order() -> None:
    operation = Operation(
        id="osm",
        type="get_osm_features",
        inputs=[],
        parameters={
            "feature_type": "roads",
            "bbox": [73.90, 18.55, 73.80, 18.45],
        },
    )

    with pytest.raises(ValueError, match="Invalid bbox"):
        OSMRetrievalOperation().validate(
            operation,
            create_context(),
        )


def test_osm_retrieval(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    expected = gpd.GeoDataFrame(
        {
            "highway": ["primary"],
            "geometry": [
                LineString(
                    [
                        (73.80, 18.45),
                        (73.90, 18.55),
                    ]
                )
            ],
        },
        crs="EPSG:4326",
    )

    def mock_features_from_bbox(*, bbox, tags):
        assert bbox == (73.80, 18.45, 73.90, 18.55)
        assert tags == {"highway": True}
        return expected

    monkeypatch.setattr(
        ox,
        "features_from_bbox",
        mock_features_from_bbox,
    )

    result = OSMRetrievalOperation().execute(
        create_operation(),
        create_context(),
    )

    assert result.data_type == "vector"
    assert isinstance(result.data, gpd.GeoDataFrame)
    assert len(result.data) == 1
    assert result.metadata["source"] == "openstreetmap"
    assert result.metadata["feature_type"] == "roads"
    assert result.metadata["feature_count"] == 1