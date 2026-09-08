from geopy.geocoders import Nominatim

from app.schemas.query import AOI


class AOIResolver:
    """Resolve planner-generated AOIs using trusted geographic data."""

    def __init__(self) -> None:
        self.geocoder = Nominatim(
            user_agent="satquery-ai",
            timeout=10,
        )

    def resolve(self, aoi: AOI) -> AOI:
        if aoi.resolved:
            return aoi

        if aoi.type in {"bbox", "polygon"}:
            return AOI(
                type=aoi.type,
                value=aoi.value,
                resolved=True,
            )

        if aoi.type == "place":
            return self._resolve_place(aoi)

        raise ValueError(f"Unsupported AOI type: '{aoi.type}'.")

    def _resolve_place(self, aoi: AOI) -> AOI:
        place_name = self._extract_place_name(aoi.value)

        if not place_name:
            raise ValueError("Place AOI must contain a place name.")

        location = self.geocoder.geocode(place_name)

        if location is None:
            raise ValueError(
                f"Could not resolve place AOI '{place_name}'."
            )

        bbox = self._location_bbox(location)

        return AOI(
            type="bbox",
            value=bbox,
            resolved=True,
        )

    @staticmethod
    def _extract_place_name(value: object) -> str | None:
        if isinstance(value, str):
            return value.strip() or None

        if isinstance(value, dict):
            name = value.get("name")
            if isinstance(name, str):
                return name.strip() or None

        return None

    @staticmethod
    def _location_bbox(location) -> list[float]:
        if not location.raw.get("boundingbox"):
            raise ValueError(
                f"Geocoder returned no bounding box for '{location.address}'."
            )

        south, north, west, east = (
            float(value)
            for value in location.raw["boundingbox"]
        )

        return [west, south, east, north]