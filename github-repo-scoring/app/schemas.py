from __future__ import annotations

from datetime import date, datetime
from enum import Enum

from pydantic import BaseModel, Field


class RepositorySortBy(str, Enum):
    stars = "stars"
    forks = "forks"
    updated = "updated"


class SortOrder(str, Enum):
    asc = "asc"
    desc = "desc"


class RepositoryQueryParams(BaseModel):
    language: str | None = Field(default=None, min_length=1)
    created_after: date | None = None
    sort_by: RepositorySortBy | None = None
    order: SortOrder = SortOrder.desc
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=30, ge=1, le=100)


class ScoredRepositoryQueryParams(BaseModel):
    language: str | None = Field(default=None, min_length=1)
    created_after: date | None = None
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=30, ge=1, le=100)


class Repository(BaseModel):
    name: str
    full_name: str
    description: str | None = None
    language: str | None = None
    stars: int = Field(ge=0)
    forks: int = Field(ge=0)
    created_at: datetime
    pushed_at: datetime
    html_url: str


class ScoredRepository(Repository):
    score: float


class RepositoryListResponse(BaseModel):
    page: int = Field(ge=1)
    per_page: int = Field(ge=1, le=100)
    total_count: int = Field(ge=0)
    has_next: bool
    items: list[Repository]


class ScoredRepositoryListResponse(BaseModel):
    page: int = Field(ge=1)
    per_page: int = Field(ge=1, le=100)
    total_count: int = Field(ge=0)
    has_next: bool
    items: list[ScoredRepository]
