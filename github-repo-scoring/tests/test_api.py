from datetime import datetime, timezone

from fastapi.testclient import TestClient

from app.main import app
from app.models import Repository
from app.routes import get_github_repository_client


class StubGitHubRepositoryClient:
    """Provide predictable repository search results for route tests."""

    def search_repositories(self, **kwargs):
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


def test_health_endpoint_returns_ok() -> None:
    """Verify the health endpoint reports the service as available."""
    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_list_repositories_returns_normalized_paginated_results() -> None:
    """Verify the repositories endpoint returns mapped GitHub search results."""
    app.dependency_overrides[get_github_repository_client] = StubGitHubRepositoryClient

    with TestClient(app) as client:
        response = client.get(
            "/repositories",
            params={"language": "Python", "created_after": "2024-01-01"},
        )

    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {
        "page": 1,
        "per_page": 30,
        "total_count": 42,
        "has_next": True,
        "items": [
            {
                "name": "repo-scoring",
                "full_name": "octocat/repo-scoring",
                "description": "Repository scoring service",
                "language": "Python",
                "stars": 120,
                "forks": 32,
                "created_at": "2024-01-01T00:00:00Z",
                "pushed_at": "2026-03-30T00:00:00Z",
                "html_url": "https://github.com/octocat/repo-scoring",
            }
        ],
    }


def test_list_scored_repositories_returns_ranked_results() -> None:
    """Verify the scored endpoint returns repositories ordered by computed score."""
    app.dependency_overrides[get_github_repository_client] = StubGitHubRepositoryClient

    with TestClient(app) as client:
        response = client.get(
            "/repositories/scored",
            params={"language": "Python", "created_after": "2024-01-01"},
        )

    app.dependency_overrides.clear()

    assert response.status_code == 200
    payload = response.json()
    assert payload["page"] == 1
    assert payload["per_page"] == 30
    assert payload["total_count"] == 42
    assert payload["has_next"] is True
    assert len(payload["items"]) == 1
    assert payload["items"][0]["name"] == "repo-scoring"
    assert payload["items"][0]["score"] > 0
