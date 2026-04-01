from datetime import date, datetime, timezone

import httpx

from app.config import Settings
from app.github_client import (
    GITHUB_SEARCH_REPOSITORIES_URL,
    GitHubRepositoryClient,
    build_headers,
    build_search_params,
    build_search_query,
    map_github_repository,
)
from app.schemas import RepositorySortBy, SortOrder


def test_build_search_query_with_language_and_created_after() -> None:
    """Verify supported filters are translated into the GitHub query string."""
    query = build_search_query(
        language="Python",
        created_after=date(2024, 1, 1),
    )

    assert query == "language:Python created:>=2024-01-01"


def test_build_search_params_includes_sort_only_when_requested() -> None:
    """Verify GitHub params include pagination and optional sort fields."""
    params = build_search_params(
        language="Python",
        created_after=date(2024, 1, 1),
        sort_by=RepositorySortBy.stars,
        order=SortOrder.desc,
        page=2,
        per_page=50,
    )

    assert params == {
        "q": "language:Python created:>=2024-01-01",
        "sort": "stars",
        "order": "desc",
        "page": 2,
        "per_page": 50,
    }


def test_build_headers_includes_github_token_when_present() -> None:
    """Verify authenticated GitHub requests include the configured token."""
    settings = Settings(github_token="test-token")

    headers = build_headers(settings)

    assert headers["Authorization"] == "Bearer test-token"
    assert headers["Accept"] == "application/vnd.github+json"
    assert headers["X-GitHub-Api-Version"] == "2026-03-10"


def test_map_github_repository_normalizes_response_fields() -> None:
    """Verify a GitHub payload is mapped into the internal repository model."""
    repository = map_github_repository(
        {
            "name": "repo-scoring",
            "full_name": "octocat/repo-scoring",
            "description": "Repository scoring service",
            "language": "Python",
            "stargazers_count": 120,
            "forks_count": 32,
            "created_at": datetime(2024, 1, 1, tzinfo=timezone.utc),
            "pushed_at": datetime(2026, 3, 30, tzinfo=timezone.utc),
            "html_url": "https://github.com/octocat/repo-scoring",
        }
    )

    assert repository.name == "repo-scoring"
    assert repository.stars == 120
    assert repository.forks == 32


def test_search_repositories_maps_upstream_response() -> None:
    """Verify the client fetches, maps, and paginates GitHub search results."""

    def handler(request: httpx.Request) -> httpx.Response:
        assert str(request.url) == (
            "https://api.github.com/search/repositories"
            "?q=language%3APython+created%3A%3E%3D2024-01-01&page=1&per_page=30"
        )
        return httpx.Response(
            status_code=200,
            json={
                "total_count": 42,
                "items": [
                    {
                        "name": "repo-scoring",
                        "full_name": "octocat/repo-scoring",
                        "description": "Repository scoring service",
                        "language": "Python",
                        "stargazers_count": 120,
                        "forks_count": 32,
                        "created_at": "2024-01-01T00:00:00Z",
                        "pushed_at": "2026-03-30T00:00:00Z",
                        "html_url": "https://github.com/octocat/repo-scoring",
                    }
                ],
            },
        )

    transport = httpx.MockTransport(handler)
    http_client = httpx.Client(transport=transport)
    client = GitHubRepositoryClient(
        settings=Settings(),
        http_client=http_client,
    )

    repositories, total_count, has_next = client.search_repositories(
        language="Python",
        created_after=date(2024, 1, 1),
    )

    assert len(repositories) == 1
    assert repositories[0].full_name == "octocat/repo-scoring"
    assert total_count == 42
    assert has_next is True
