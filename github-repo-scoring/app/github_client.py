from __future__ import annotations

from datetime import date
from datetime import datetime

import httpx

from app.config import Settings
from app.logger import logger
from app.models import Repository
from app.schemas import RepositorySortBy, SortOrder

GITHUB_SEARCH_REPOSITORIES_URL = "https://api.github.com/search/repositories"


def build_search_query(
    *,
    language: str | None = None,
    created_after: date | None = None,
) -> str:
    """Build the GitHub repository search query from supported filters."""
    qualifiers: list[str] = []

    if language:
        qualifiers.append(f"language:{language}")
    if created_after:
        qualifiers.append(f"created:>={created_after.isoformat()}")

    return " ".join(qualifiers)


def build_search_params(
    *,
    language: str | None = None,
    created_after: date | None = None,
    sort_by: RepositorySortBy | None = None,
    order: SortOrder = SortOrder.desc,
    page: int = 1,
    per_page: int = 50,
) -> dict[str, str | int]:
    """Build GitHub request parameters for repository search and pagination."""
    params: dict[str, str | int] = {
        "q": build_search_query(language=language, created_after=created_after),
        "page": page,
        "per_page": per_page,
    }

    if sort_by is not None:
        params["sort"] = sort_by.value
        params["order"] = order.value

    return params


def build_headers(settings: Settings) -> dict[str, str]:
    """Build request headers for GitHub API calls, including optional auth."""
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2026-03-10",
    }
    if settings.github_token:
        headers["Authorization"] = f"Bearer {settings.github_token}"
    return headers


def parse_github_datetime(value: str | datetime) -> datetime:
    """Parse an ISO 8601 GitHub timestamp into a timezone-aware datetime."""
    if isinstance(value, datetime):
        return value
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def map_github_repository(item: dict) -> Repository:
    """Map a GitHub repository payload into the internal repository model."""
    return Repository(
        name=item["name"],
        full_name=item["full_name"],
        description=item.get("description"),
        language=item.get("language"),
        stars=item.get("stargazers_count", 0),
        forks=item.get("forks_count", 0),
        created_at=parse_github_datetime(item["created_at"]),
        pushed_at=parse_github_datetime(item["pushed_at"]),
        html_url=item["html_url"],
    )


class GitHubRepositoryClient:
    def __init__(
        self,
        settings: Settings,
        http_client: httpx.Client | None = None,
    ) -> None:
        """Initialize the GitHub client with settings and an optional HTTP client."""
        self.settings = settings
        self.http_client = http_client or httpx.Client(timeout=10.0)

    def search_repositories(
        self,
        *,
        language: str | None = None,
        created_after: date | None = None,
        sort_by: RepositorySortBy | None = None,
        order: SortOrder = SortOrder.desc,
        page: int = 1,
        per_page: int = 30,
    ) -> tuple[list[Repository], int, bool]:
        """Fetch one page of repositories from GitHub and normalize the response."""
        params = build_search_params(
            language=language,
            created_after=created_after,
            sort_by=sort_by,
            order=order,
            page=page,
            per_page=per_page,
        )
        logger.info("Searching GitHub repositories with params=%s", params)
        response = self.http_client.get(
            GITHUB_SEARCH_REPOSITORIES_URL,
            params=params,
            headers=build_headers(self.settings),
        )
        response.raise_for_status()

        payload = response.json()
        total_count = payload.get("total_count", 0)
        items = [map_github_repository(item) for item in payload.get("items", [])]
        has_next = page * per_page < total_count
        logger.info(
            "Received %s repositories from GitHub total_count=%s has_next=%s",
            len(items),
            total_count,
            has_next,
        )
        return items, total_count, has_next
