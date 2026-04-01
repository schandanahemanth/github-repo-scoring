from __future__ import annotations

from dataclasses import dataclass

from app.clients.github_client import GitHubRepositoryClient
from app.core.cache import InMemoryTTLCache
from app.core.config import Settings
from app.core.logger import logger
from app.models import Repository, ScoredRepository
from app.schemas import RepositoryQueryParams, ScoredRepositoryQueryParams
from app.services.scoring import rank_repositories


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


GitHubSearchCacheValue = tuple[list[Repository], int, bool]


class RepositoryService:
    """Coordinate repository fetching and scoring for the API layer."""

    def __init__(
        self,
        github_client: GitHubRepositoryClient,
        settings: Settings,
        cache: InMemoryTTLCache[tuple, GitHubSearchCacheValue] | None = None,
    ) -> None:
        """Initialize the service with the GitHub client and current settings."""
        self.github_client = github_client
        self.settings = settings
        self.cache = cache

    def _build_cache_key(
        self,
        *,
        language: str | None,
        created_after,
        sort_by,
        order,
        page: int,
        per_page: int,
    ) -> tuple:
        """Build a stable cache key from the GitHub search parameters."""
        return (
            language,
            created_after.isoformat() if created_after else None,
            sort_by.value if sort_by else None,
            order.value if sort_by and order else None,
            page,
            per_page,
        )

    def _search_repositories(
        self,
        *,
        language: str | None,
        created_after,
        sort_by=None,
        order=None,
        page: int,
        per_page: int,
    ) -> GitHubSearchCacheValue:
        """Fetch repositories with cache lookups around the GitHub client."""
        cache_key = self._build_cache_key(
            language=language,
            created_after=created_after,
            sort_by=sort_by,
            order=order,
            page=page,
            per_page=per_page,
        )
        if self.cache is not None:
            cached_value = self.cache.get(cache_key)
            if cached_value is not None:
                logger.info("Returning cached GitHub search results for key=%s", cache_key)
                return cached_value

        repositories, total_count, has_next = self.github_client.search_repositories(
            language=language,
            created_after=created_after,
            sort_by=sort_by,
            order=order,
            page=page,
            per_page=per_page,
        )
        result = (repositories, total_count, has_next)
        if self.cache is not None:
            self.cache.set(
                cache_key,
                result,
                ttl_seconds=self.settings.github_cache_ttl_seconds,
            )
        return result

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
        repositories, total_count, has_next = self._search_repositories(
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
        repositories, total_count, has_next = self._search_repositories(
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
