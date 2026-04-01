from datetime import datetime, timezone

from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.api.routes import get_repository_service
from app.main import app
from app.models import Repository, ScoredRepository


class StubRepositoryService:
    """Provide predictable repository results for route tests."""

    def list_repositories(self, query):
        return type(
            "RepositoryResult",
            (),
            {
                "items": [
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
                "total_count": 42,
                "has_next": True,
                "page": query.page,
                "per_page": query.per_page,
            },
        )()

    def list_scored_repositories(self, query):
        return type(
            "ScoredRepositoryResult",
            (),
            {
                "items": [
                    ScoredRepository(
                        name="repo-scoring",
                        full_name="octocat/repo-scoring",
                        description="Repository scoring service",
                        language="Python",
                        stars=120,
                        forks=32,
                        created_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
                        pushed_at=datetime(2026, 3, 30, tzinfo=timezone.utc),
                        html_url="https://github.com/octocat/repo-scoring",
                        score=3.4021,
                    )
                ],
                "total_count": 42,
                "has_next": True,
                "page": query.page,
                "per_page": query.per_page,
            },
        )()


class UnauthorizedRepositoryService:
    """Raise an authentication error to simulate a rejected upstream request."""

    def list_repositories(self, query):
        raise HTTPException(status_code=401, detail="GitHub API authentication failed.")

    def list_scored_repositories(self, query):
        raise HTTPException(status_code=401, detail="GitHub API authentication failed.")


class ForbiddenRepositoryService:
    """Raise a forbidden error to simulate rate limiting or denied access."""

    def list_repositories(self, query):
        raise HTTPException(
            status_code=403,
            detail="GitHub API rate limit exceeded or access forbidden.",
        )

    def list_scored_repositories(self, query):
        raise HTTPException(
            status_code=403,
            detail="GitHub API rate limit exceeded or access forbidden.",
        )


def test_health_endpoint_returns_ok() -> None:
    """Verify the health endpoint reports the service as available."""
    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_list_repositories_returns_normalized_paginated_results() -> None:
    """Verify the repositories endpoint returns mapped GitHub search results."""
    app.dependency_overrides[get_repository_service] = StubRepositoryService

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
    app.dependency_overrides[get_repository_service] = StubRepositoryService

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


def test_list_repositories_propagates_401_from_github_client() -> None:
    """Verify the raw repositories endpoint surfaces GitHub auth failures."""
    app.dependency_overrides[get_repository_service] = UnauthorizedRepositoryService

    with TestClient(app) as client:
        response = client.get("/repositories")

    app.dependency_overrides.clear()

    assert response.status_code == 401
    assert response.json() == {"detail": "GitHub API authentication failed."}


def test_list_repositories_propagates_403_from_github_client() -> None:
    """Verify the raw repositories endpoint surfaces GitHub forbidden failures."""
    app.dependency_overrides[get_repository_service] = ForbiddenRepositoryService

    with TestClient(app) as client:
        response = client.get("/repositories")

    app.dependency_overrides.clear()

    assert response.status_code == 403
    assert response.json() == {
        "detail": "GitHub API rate limit exceeded or access forbidden."
    }


def test_list_scored_repositories_propagates_401_from_github_client() -> None:
    """Verify the scored repositories endpoint surfaces GitHub auth failures."""
    app.dependency_overrides[get_repository_service] = UnauthorizedRepositoryService

    with TestClient(app) as client:
        response = client.get("/repositories/scored")

    app.dependency_overrides.clear()

    assert response.status_code == 401
    assert response.json() == {"detail": "GitHub API authentication failed."}


def test_list_scored_repositories_propagates_403_from_github_client() -> None:
    """Verify the scored repositories endpoint surfaces GitHub forbidden failures."""
    app.dependency_overrides[get_repository_service] = ForbiddenRepositoryService

    with TestClient(app) as client:
        response = client.get("/repositories/scored")

    app.dependency_overrides.clear()

    assert response.status_code == 403
    assert response.json() == {
        "detail": "GitHub API rate limit exceeded or access forbidden."
    }
