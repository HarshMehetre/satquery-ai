from fastapi import FastAPI

from app.api.routes import router

app = FastAPI(
    title="SatQuery-AI",
    description="Natural-language geospatial query execution API.",
    version="0.1.0",
)

app.include_router(router)