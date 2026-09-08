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
        },
    )


def test_osm_requires_feature_type() -> None:
    operation = Operation(
        id="osm",
        type="get_osm_features",
        inputs=[],
        parameters={},
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
        },
    )

    with pytest.raises(ValueError, match="does not require inputs"):
        OSMRetrievalOperation().validate(
            operation,
            create_context(),
        )


def test_osm_rejects_unresolved_aoi() -> None:
    context = ExecutionContext(
        aoi=AOI(
            type="bbox",
            value=[73.80, 18.45, 73.90, 18.55],
            resolved=False,
        )
    )

    with pytest.raises(ValueError, match="resolved AOI"):
        OSMRetrievalOperation().validate(
            create_operation(),
            context,
        )


def test_osm_validates_aoi_bbox_length() -> None:
    context = ExecutionContext(
        aoi=AOI(
            type="bbox",
            value=[73.80, 18.45, 73.90],
        )
    )

    with pytest.raises(ValueError, match="four values"):
        OSMRetrievalOperation().validate(
            create_operation(),
            context,
        )


def test_osm_validates_aoi_bbox_order() -> None:
    context = ExecutionContext(
        aoi=AOI(
            type="bbox",
            value=[73.90, 18.55, 73.80, 18.45],
        )
    )

    with pytest.raises(
        ValueError,
        match="west must be less than east",
    ):
        OSMRetrievalOperation().validate(
            create_operation(),
            context,
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


def test_major_road_filter_keeps_major_classes() -> None:
    features = gpd.GeoDataFrame(
        {
            "highway": [
                "primary",
                "secondary",
                "residential",
                "footway",
            ],
        },
        geometry=[
            LineString([(73.0, 18.0), (73.01, 18.01)]),
            LineString([(73.01, 18.0), (73.02, 18.01)]),
            LineString([(73.02, 18.0), (73.03, 18.01)]),
            LineString([(73.03, 18.0), (73.04, 18.01)]),
        ],
        crs="EPSG:4326",
    )

    handler = OSMRetrievalOperation()

    filtered = handler._filter_major_roads(features)

    assert len(filtered) == 2
    assert set(filtered["highway"]) == {
        "primary",
        "secondary",
    }


def test_major_road_filter_supports_list_values() -> None:
    features = gpd.GeoDataFrame(
        {
            "highway": [
                ["primary", "secondary"],
                ["residential"],
            ],
        },
        geometry=[
            LineString([(73.0, 18.0), (73.01, 18.01)]),
            LineString([(73.01, 18.0), (73.02, 18.01)]),
        ],
        crs="EPSG:4326",
    )

    handler = OSMRetrievalOperation()

    filtered = handler._filter_major_roads(features)

    assert len(filtered) == 1
    assert filtered.iloc[0]["highway"] == [
        "primary",
        "secondary",
    ]


def test_major_road_filter_rejects_missing_highway_column() -> None:
    features = gpd.GeoDataFrame(
        {
            "name": ["Road A"],
        },
        geometry=[
            LineString([(73.0, 18.0), (73.01, 18.01)]),
        ],
        crs="EPSG:4326",
    )

    handler = OSMRetrievalOperation()

    with pytest.raises(
        ValueError,
        match="highway",
    ):
        handler._filter_major_roads(features)