from __future__ import annotations

from fastapi import FastAPI

from app.routes import router
from app.logger import logger

app = FastAPI(
    title="GitHub Repository Scoring Service",
    version="0.1.0",
)

app.include_router(router)


@app.on_event("startup")
def startup() -> None:
    logger.info("Starting GitHub Repository Scoring Service")
