import numpy as np

from app.schemas.raster import RasterData, RasterMetadata


def test_raster_metadata() -> None:
    metadata = RasterMetadata(
        crs="EPSG:4326",
        resolution=(0.0001, 0.0001),
        width=256,
        height=256,
        count=2,
        dtype="float32",
    )

    assert metadata.crs == "EPSG:4326"
    assert metadata.width == 256
    assert metadata.height == 256
    assert metadata.count == 2


def test_raster_data() -> None:
    data = np.zeros(
        (2, 256, 256),
        dtype=np.float32,
    )

    raster = RasterData(
        data=data,
        bands=["B4", "B8"],
        metadata=RasterMetadata(
            crs="EPSG:4326",
            width=256,
            height=256,
            count=2,
            dtype="float32",
        ),
    )

    assert raster.data.shape == (2, 256, 256)
    assert raster.bands == ["B4", "B8"]
    assert raster.metadata.crs == "EPSG:4326"