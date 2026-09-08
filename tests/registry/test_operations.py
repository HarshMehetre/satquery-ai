from app.registry import create_production_registry


def test_production_registry_exposes_planner_catalog() -> None:
    registry = create_production_registry()

    catalog = registry.get_catalog()

    operation_types = {item["type"] for item in catalog}

    assert operation_types == {
        "get_satellite_imagery",
        "calculate_ndvi",
        "project_to_crs",
        "buffer",
        "intersection",
        "area",
        "get_osm_features",
        "temporal_difference",
        "vegetation_loss",
        "raster_polygonize",
    }


def test_ndvi_catalog_contains_parameter_metadata() -> None:
    registry = create_production_registry()

    catalog = registry.get_catalog()

    ndvi = next(
        item for item in catalog
        if item["type"] == "calculate_ndvi"
    )

    assert ndvi["description"]
    assert ndvi["parameters"] == {
        "red_band": "Red band name.",
        "nir_band": "Near-infrared band name.",
    }
    assert ndvi["input_type"] == "raster"
    assert ndvi["output_type"] == "raster"