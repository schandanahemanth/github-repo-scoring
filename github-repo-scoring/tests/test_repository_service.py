from datetime import date, datetime, timezone

from app.core.cache import InMemoryTTLCache
from app.core.config import Settings
from app.models import Repository
from app.schemas import RepositoryQueryParams, ScoredRepositoryQueryParams
from app.services.repository_service import RepositoryService


class StubGitHubRepositoryClient:
    """Track repository search calls and return predictable data for service tests."""

    def __init__(self) -> None:
        self.call_count = 0

    def search_repositories(self, **kwargs):
        self.call_count += 1
        return (
            [
                Repository(
                    name="repo-scoring",
                    full_name="octocat/repo-scoring",
                    description="Repository scoring service",
                    language="Python",
                    stars=120,
                    forks=32,
                    created_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
                    pushed_at=datetime(2026, 3, 30, tzinfo=timezone.utc),
                    html_url="https://github.com/octocat/repo-scoring",
                )
            ],
            42,
            True,
        )


def test_list_repositories_uses_cached_github_results() -> None:
    """Verify repeated raw repository searches reuse cached GitHub responses."""
    github_client = StubGitHubRepositoryClient()
    cache = InMemoryTTLCache()
    service = RepositoryService(
        github_client=github_client,
        settings=Settings(github_cache_ttl_seconds=300),
        cache=cache,
    )
    query = RepositoryQueryParams(language="Python", created_after=date(2024, 1, 1))

    first_result = service.list_repositories(query)
    second_result = service.list_repositories(query)

    assert github_client.call_count == 1
    assert first_result.total_count == second_result.total_count == 42


def test_list_scored_repositories_reuses_cached_github_results() -> None:
    """Verify scored repository searches reuse cached raw GitHub responses."""
    github_client = StubGitHubRepositoryClient()
    cache = InMemoryTTLCache()
    service = RepositoryService(
        github_client=github_client,
        settings=Settings(github_cache_ttl_seconds=300),
        cache=cache,
    )
    query = ScoredRepositoryQueryParams(language="Python", created_after=date(2024, 1, 1))

    first_result = service.list_scored_repositories(query)
    second_result = service.list_scored_repositories(query)

    assert github_client.call_count == 1
    assert len(first_result.items) == len(second_result.items) == 1
    assert first_result.items[0].score == second_result.items[0].score


def test_cache_expires_after_ttl() -> None:
    """Verify cached GitHub search results expire once the TTL elapses."""
    current_time = 1_000.0

    def time_provider() -> float:
        return current_time

    github_client = StubGitHubRepositoryClient()
    cache = InMemoryTTLCache(time_provider=time_provider)
    service = RepositoryService(
        github_client=github_client,
        settings=Settings(github_cache_ttl_seconds=60),
        cache=cache,
    )
    query = RepositoryQueryParams(language="Python", created_after=date(2024, 1, 1))

    service.list_repositories(query)
    current_time += 61
    service.list_repositories(query)

    assert github_client.call_count == 2
