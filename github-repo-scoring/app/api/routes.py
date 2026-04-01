from __future__ import annotations

from fastapi import APIRouter, Depends

from app.clients.github_client import GitHubRepositoryClient
from app.core.config import Settings, get_settings
from app.models import Repository as RepositoryModel
from app.models import ScoredRepository as ScoredRepositoryModel
from app.schemas import (
    Repository,
    RepositoryListResponse,
    RepositoryQueryParams,
    ScoredRepository,
    ScoredRepositoryListResponse,
    ScoredRepositoryQueryParams,
)
from app.services.repository_service import RepositoryService

router = APIRouter()


def get_github_repository_client(
    settings: Settings = Depends(get_settings),
) -> GitHubRepositoryClient:
    """Create a GitHub repository client from the current application settings."""
    return GitHubRepositoryClient(settings=settings)


def get_repository_service(
    settings: Settings = Depends(get_settings),
    github_client: GitHubRepositoryClient = Depends(get_github_repository_client),
) -> RepositoryService:
    """Create the repository service used by the HTTP routes."""
    return RepositoryService(github_client=github_client, settings=settings)


def to_repository_schema(repository: RepositoryModel) -> Repository:
    """Convert an internal repository model into an API response schema."""
    return Repository(
        name=repository.name,
        full_name=repository.full_name,
        description=repository.description,
        language=repository.language,
        stars=repository.stars,
        forks=repository.forks,
        created_at=repository.created_at,
        pushed_at=repository.pushed_at,
        html_url=repository.html_url,
    )


def to_scored_repository_schema(repository: ScoredRepositoryModel) -> ScoredRepository:
    """Convert an internal scored repository model into an API response schema."""
    return ScoredRepository(
        name=repository.name,
        full_name=repository.full_name,
        description=repository.description,
        language=repository.language,
        stars=repository.stars,
        forks=repository.forks,
        created_at=repository.created_at,
        pushed_at=repository.pushed_at,
        html_url=repository.html_url,
        score=repository.score,
    )


@router.get("/health")
def health_check() -> dict[str, str]:
    """Return a simple health response for the running service."""
    return {"status": "ok"}


@router.get("/repositories", response_model=RepositoryListResponse)
def list_repositories(
    query: RepositoryQueryParams = Depends(),
    repository_service: RepositoryService = Depends(get_repository_service),
) -> RepositoryListResponse:
    """Fetch one filtered page of GitHub repositories and return normalized results."""
    result = repository_service.list_repositories(query)

    return RepositoryListResponse(
        page=result.page,
        per_page=result.per_page,
        total_count=result.total_count,
        has_next=result.has_next,
        items=[to_repository_schema(repository) for repository in result.items],
    )


@router.get("/repositories/scored", response_model=ScoredRepositoryListResponse)
def list_scored_repositories(
    query: ScoredRepositoryQueryParams = Depends(),
    repository_service: RepositoryService = Depends(get_repository_service),
) -> ScoredRepositoryListResponse:
    """Fetch filtered GitHub repositories, then score and rank them locally."""
    result = repository_service.list_scored_repositories(query)

    return ScoredRepositoryListResponse(
        page=result.page,
        per_page=result.per_page,
        total_count=result.total_count,
        has_next=result.has_next,
        items=[to_scored_repository_schema(repository) for repository in result.items],
    )
