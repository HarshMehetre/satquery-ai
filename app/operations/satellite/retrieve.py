import numpy as np
from rasterio.transform import from_bounds
from sentinelhub import (
    CRS,
    BBox,
    DataCollection,
    MimeType,
    SentinelHubRequest,
    SHConfig,
)

from app.config.settings import settings
from app.executor.context import ExecutionContext
from app.operations.base import BaseOperation
from app.schemas.operation import Operation
from app.schemas.raster import RasterData, RasterMetadata
from app.schemas.result import OperationResult


class Sentinel2RetrievalOperation(BaseOperation):
    """Retrieve Sentinel-2 L2A imagery for an area and time range."""

    def validate(
        self,
        operation: Operation,
        context: ExecutionContext,
    ) -> None:
        if operation.inputs:
            raise ValueError(
                "Sentinel2RetrievalOperation does not require inputs."
            )

        required_parameters = {
            "bbox",
            "start_date",
            "end_date",
        }

        missing_parameters = (
            required_parameters - set(operation.parameters)
        )

        if missing_parameters:
            raise ValueError(
                "Missing required parameters: "
                f"{sorted(missing_parameters)}"
            )

        bbox = operation.parameters["bbox"]

        if len(bbox) != 4:
            raise ValueError(
                "bbox must contain four values: "
                "[west, south, east, north]."
            )

    def execute(
        self,
        operation: Operation,
        context: ExecutionContext,
    ) -> OperationResult:
        self.validate(operation, context)

        bbox = operation.parameters["bbox"]
        start_date = operation.parameters["start_date"]
        end_date = operation.parameters["end_date"]

        max_cloud_coverage = operation.parameters.get(
            "max_cloud_coverage",
            30,
        )

        width = operation.parameters.get("width", 256)
        height = operation.parameters.get("height", 256)

        if (
            settings.sentinel_client_id is None
            or settings.sentinel_client_secret is None
        ):
            raise RuntimeError(
                "Sentinel-2 credentials are not configured. "
                "Set SENTINEL_CLIENT_ID and SENTINEL_CLIENT_SECRET "
                "in the environment."
            )

        config = SHConfig()

        config.sh_client_id = settings.sentinel_client_id
        config.sh_client_secret = settings.sentinel_client_secret

        config.sh_token_url = (
            "https://identity.dataspace.copernicus.eu/"
            "auth/realms/CDSE/protocol/openid-connect/token"
        )

        config.sh_base_url = "https://sh.dataspace.copernicus.eu"

        data_collection = DataCollection.SENTINEL2_L2A.define_from(
            "s2l2a",
            service_url=config.sh_base_url,
        )

        request = SentinelHubRequest(
            data_folder=None,
            evalscript=self._build_evalscript(),
            input_data=[
                SentinelHubRequest.input_data(
                    data_collection=data_collection,
                    time_interval=(start_date, end_date),
                    maxcc=max_cloud_coverage / 100.0,
                )
            ],
            responses=[
                SentinelHubRequest.output_response(
                    "default",
                    MimeType.TIFF,
                )
            ],
            bbox=BBox(
                bbox=bbox,
                crs=CRS.WGS84,
            ),
            size=(width, height),
            config=config,
        )

        data = request.get_data()

        if not data:
            raise RuntimeError(
                "Sentinel-2 request returned no data."
            )

        raster_array = np.asarray(
            data[0],
            dtype=np.float32,
        )

        if raster_array.ndim != 3:
            raise ValueError(
                "Expected Sentinel-2 response with "
                "three dimensions: height, width, bands."
            )

        raster_array = np.transpose(
            raster_array,
            (2, 0, 1),
        )

        # Build the affine transform that maps raster pixels
        # to the requested geographic bounding box.
        transform = from_bounds(
            bbox[0],
            bbox[1],
            bbox[2],
            bbox[3],
            width,
            height,
        )

        metadata = RasterMetadata(
            crs="EPSG:4326",
            transform=transform,
            resolution=(
                (bbox[2] - bbox[0]) / width,
                (bbox[3] - bbox[1]) / height,
            ),
            bounds=(
                bbox[0],
                bbox[1],
                bbox[2],
                bbox[3],
            ),
            width=width,
            height=height,
            count=2,
            dtype=str(raster_array.dtype),
        )

        raster = RasterData(
            data=raster_array,
            bands=["B4", "B8"],
            metadata=metadata,
        )

        return OperationResult(
            id=operation.id,
            type=operation.type,
            data_type="raster",
            data=raster,
            metadata={
                "source": "sentinel-2",
                "collection": "sentinel-2-l2a",
                "start_date": start_date,
                "end_date": end_date,
                "max_cloud_coverage": max_cloud_coverage,
                "bands": ["B4", "B8"],
                "crs": "EPSG:4326",
                "bounds": list(bbox),
                "width": width,
                "height": height,
            },
        )

    @staticmethod
    def _build_evalscript() -> str:
        return """
        //VERSION=3
        function setup() {
            return {
                input: [{
                    bands: ["B04", "B08"],
                    units: "REFLECTANCE"
                }],
                output: {
                    bands: 2,
                    sampleType: "FLOAT32"
                }
            };
        }

        function evaluatePixel(sample) {
            return [
                sample.B04,
                sample.B08
            ];
        }
        """