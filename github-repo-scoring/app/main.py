from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import router
from app.core.logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Run application startup logic using FastAPI's lifespan interface."""
    logger.info("Starting GitHub Repository Scoring Service")
    yield


app = FastAPI(
    title="GitHub Repository Scoring Service",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(router)
