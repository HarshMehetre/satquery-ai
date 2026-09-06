from app.executor.context import ExecutionContext
from app.operations.gis.osm import OSMRetrievalOperation
from app.schemas.operation import Operation
from app.schemas.query import AOI


def main() -> None:
    bbox = [73.80, 18.45, 73.90, 18.55]

    operation = Operation(
        id="osm_roads",
        type="get_osm_features",
        parameters={
            "feature_type": "roads",
            "bbox": bbox,
        },
    )

    context = ExecutionContext(
        aoi=AOI(
            type="bbox",
            value=bbox,
        )
    )

    result = OSMRetrievalOperation().execute(
        operation,
        context,
    )

    gdf = result.data

    print("OSM retrieval successful")
    print(f"Feature count: {len(gdf)}")
    print(f"CRS: {gdf.crs}")
    print(f"Columns: {list(gdf.columns)}")
    print(f"Geometry types: {gdf.geometry.geom_type.unique().tolist()}")

    print("\nSample features:")
    print(gdf[["highway", "geometry"]].head())

    print("\nMetadata:")
    print(result.metadata)


if __name__ == "__main__":
    main()