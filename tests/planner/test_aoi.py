from unittest.mock import Mock

import pytest

from app.planner.aoi import AOIResolver
from app.schemas.query import AOI


def test_place_is_resolved_to_bbox() -> None:
    resolver = AOIResolver()

    location = Mock()
    location.address = "Mumbai, Maharashtra, India"
    location.raw = {
        "boundingbox": [
            "18.8",
            "19.3",
            "72.7",
            "73.1",
        ]
    }

    resolver.geocoder.geocode = Mock(return_value=location)

    result = resolver.resolve(
        AOI(
            type="place",
            value="Mumbai",
            resolved=False,
        )
    )

    assert result.type == "bbox"
    assert result.value == [72.7, 18.8, 73.1, 19.3]
    assert result.resolved is True


def test_unresolved_place_without_name_is_rejected() -> None:
    resolver = AOIResolver()

    with pytest.raises(
        ValueError,
        match="Place AOI must contain a place name",
    ):
        resolver.resolve(
            AOI(
                type="place",
                value={},
                resolved=False,
            )
        )


def test_unknown_place_is_rejected() -> None:
    resolver = AOIResolver()
    resolver.geocoder.geocode = Mock(return_value=None)

    with pytest.raises(
        ValueError,
        match="Could not resolve place AOI",
    ):
        resolver.resolve(
            AOI(
                type="place",
                value="DefinitelyNotARealPlace",
                resolved=False,
            )
        )

def test_resolved_aoi_is_unchanged() -> None:
    aoi = AOI(
        type="bbox",
        value=[73.0, 18.0, 73.1, 18.1],
        resolved=True,
    )

    result = AOIResolver().resolve(aoi)

    assert result.resolved is True
    assert result.value == aoi.value


def test_bbox_can_be_resolved() -> None:
    aoi = AOI(
        type="bbox",
        value=[73.0, 18.0, 73.1, 18.1],
        resolved=False,
    )

    result = AOIResolver().resolve(aoi)

    assert result.resolved is True
    assert result.value == aoi.value


def test_polygon_can_be_resolved() -> None:
    polygon = {
        "type": "Polygon",
        "coordinates": [
            [
                [73.0, 18.0],
                [73.1, 18.0],
                [73.1, 18.1],
                [73.0, 18.1],
                [73.0, 18.0],
            ]
        ],
    }

    aoi = AOI(
        type="polygon",
        value=polygon,
        resolved=False,
    )

    result = AOIResolver().resolve(aoi)

    assert result.resolved is True
    assert result.value == polygon
