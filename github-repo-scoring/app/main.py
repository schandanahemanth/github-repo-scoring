from __future__ import annotations

from fastapi import FastAPI

from app.routes import router


app = FastAPI(
    title="GitHub Repository Scoring Service",
    version="0.1.0",
)

app.include_router(router)
