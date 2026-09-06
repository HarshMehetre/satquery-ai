from pathlib import Path

from app.executor.context import ExecutionContext
from app.operations.satellite.retrieve import Sentinel2RetrievalOperation
from app.schemas.operation import Operation
from app.schemas.query import AOI


def main() -> None:
    context = ExecutionContext(
        aoi=AOI(
            type="bbox",
            value=[73.80, 18.45, 73.90, 18.55],
        )
    )

    operation = Operation(
        id="sentinel2_test",
        type="get_satellite_imagery",
        inputs=[],
        parameters={
            "bbox": [73.80, 18.45, 73.90, 18.55],
            "start_date": "2026-01-01",
            "end_date": "2026-01-31",
            "max_cloud_coverage": 30,
            "width": 256,
            "height": 256,
        },
    )

    result = Sentinel2RetrievalOperation().execute(
        operation,
        context,
    )

    raster = result.data

    print("Sentinel-2 retrieval successful")
    print(f"Shape: {raster.data.shape}")
    print(f"Bands: {raster.bands}")
    print(f"CRS: {raster.metadata.crs}")
    print(f"Width: {raster.metadata.width}")
    print(f"Height: {raster.metadata.height}")
    print(f"Dtype: {raster.metadata.dtype}")

    output_dir = Path("outputs")
    output_dir.mkdir(exist_ok=True)

    print(f"\nOutput directory: {output_dir.resolve()}")


if __name__ == "__main__":
    main()