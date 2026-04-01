from __future__ import annotations

from fastapi import APIRouter, Depends

from app.config import Settings, get_settings
from app.github_client import GitHubRepositoryClient
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
from app.scoring import rank_repositories

router = APIRouter()


def get_github_repository_client(
    settings: Settings = Depends(get_settings),
) -> GitHubRepositoryClient:
    """Create a GitHub repository client from the current application settings."""
    return GitHubRepositoryClient(settings=settings)


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
    github_client: GitHubRepositoryClient = Depends(get_github_repository_client),
) -> RepositoryListResponse:
    """Fetch one filtered page of GitHub repositories and return normalized results."""
    repositories, total_count, has_next = github_client.search_repositories(
        language=query.language,
        created_after=query.created_after,
        sort_by=query.sort_by,
        order=query.order,
        page=query.page,
        per_page=query.per_page,
    )

    return RepositoryListResponse(
        page=query.page,
        per_page=query.per_page,
        total_count=total_count,
        has_next=has_next,
        items=[to_repository_schema(repository) for repository in repositories],
    )


@router.get("/repositories/scored", response_model=ScoredRepositoryListResponse)
def list_scored_repositories(
    query: ScoredRepositoryQueryParams = Depends(),
    settings: Settings = Depends(get_settings),
    github_client: GitHubRepositoryClient = Depends(get_github_repository_client),
) -> ScoredRepositoryListResponse:
    """Fetch filtered GitHub repositories, then score and rank them locally."""
    repositories, total_count, has_next = github_client.search_repositories(
        language=query.language,
        created_after=query.created_after,
        page=query.page,
        per_page=query.per_page,
    )
    ranked_repositories = rank_repositories(repositories, settings=settings)

    return ScoredRepositoryListResponse(
        page=query.page,
        per_page=query.per_page,
        total_count=total_count,
        has_next=has_next,
        items=[
            to_scored_repository_schema(repository)
            for repository in ranked_repositories
        ],
    )
