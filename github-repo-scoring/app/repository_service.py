from __future__ import annotations

from dataclasses import dataclass

from app.config import Settings
from app.github_client import GitHubRepositoryClient
from app.logger import logger
from app.models import Repository, ScoredRepository
from app.schemas import RepositoryQueryParams, ScoredRepositoryQueryParams
from app.scoring import rank_repositories


@dataclass(frozen=True)
class RepositorySearchResult:
    items: list[Repository]
    total_count: int
    has_next: bool
    page: int
    per_page: int


@dataclass(frozen=True)
class ScoredRepositorySearchResult:
    items: list[ScoredRepository]
    total_count: int
    has_next: bool
    page: int
    per_page: int


class RepositoryService:
    """Coordinate repository fetching and scoring for the API layer."""

    def __init__(
        self, github_client: GitHubRepositoryClient, settings: Settings
    ) -> None:
        """Initialize the service with the GitHub client and current settings."""
        self.github_client = github_client
        self.settings = settings

    def list_repositories(self, query: RepositoryQueryParams) -> RepositorySearchResult:
        """Fetch one page of raw repositories using the provided filters and sort options."""
        logger.info(
            "Listing repositories language=%s created_after=%s sort_by=%s page=%s per_page=%s",
            query.language,
            query.created_after,
            query.sort_by,
            query.page,
            query.per_page,
        )
        repositories, total_count, has_next = self.github_client.search_repositories(
            language=query.language,
            created_after=query.created_after,
            sort_by=query.sort_by,
            order=query.order,
            page=query.page,
            per_page=query.per_page,
        )
        return RepositorySearchResult(
            items=repositories,
            total_count=total_count,
            has_next=has_next,
            page=query.page,
            per_page=query.per_page,
        )

    def list_scored_repositories(
        self,
        query: ScoredRepositoryQueryParams,
    ) -> ScoredRepositorySearchResult:
        """Fetch filtered repositories, then apply local scoring and ranking."""
        logger.info(
            "Listing scored repositories language=%s created_after=%s page=%s per_page=%s",
            query.language,
            query.created_after,
            query.page,
            query.per_page,
        )
        repositories, total_count, has_next = self.github_client.search_repositories(
            language=query.language,
            created_after=query.created_after,
            page=query.page,
            per_page=query.per_page,
        )
        ranked_repositories = rank_repositories(repositories, settings=self.settings)
        return ScoredRepositorySearchResult(
            items=ranked_repositories,
            total_count=total_count,
            has_next=has_next,
            page=query.page,
            per_page=query.per_page,
        )
