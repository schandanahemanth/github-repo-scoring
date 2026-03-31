from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Repository:
    name: str
    full_name: str
    description: str | None
    language: str | None
    stars: int
    forks: int
    created_at: datetime
    pushed_at: datetime
    html_url: str


@dataclass(frozen=True)
class ScoredRepository:
    name: str
    full_name: str
    description: str | None
    language: str | None
    stars: int
    forks: int
    created_at: datetime
    pushed_at: datetime
    html_url: str
    score: float
