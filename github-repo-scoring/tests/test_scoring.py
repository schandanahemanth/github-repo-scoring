from datetime import datetime, timedelta, timezone

from app.core.config import Settings
from app.models import Repository
from app.services.scoring import calculate_score


def test_scoring_uses_agreed_formula() -> None:
    """
    Verify scoring matches the agreed weighted popularity formula.
    """
    settings = Settings()
    now = datetime(2026, 3, 31, tzinfo=timezone.utc)

    score = calculate_score(
        stars=99,
        forks=24,
        pushed_at=now - timedelta(days=45),
        settings=settings,
        now=now,
    )

    assert score == 3.389554


def test_calculate_score_can_be_used_to_rank_internal_repository_models() -> None:
    """
    Verify internal repository models can be scored successfully.
    """
    settings = Settings()
    now = datetime(2026, 3, 31, tzinfo=timezone.utc)
    repository = Repository(
        name="repo-scoring",
        full_name="octocat/repo-scoring",
        description="test repository",
        language="Python",
        stars=150,
        forks=40,
        created_at=datetime(2025, 1, 1, tzinfo=timezone.utc),
        pushed_at=now - timedelta(days=10),
        html_url="https://github.com/octocat/repo-scoring",
    )

    score = calculate_score(
        stars=repository.stars,
        forks=repository.forks,
        pushed_at=repository.pushed_at,
        settings=settings,
        now=now,
    )

    assert score > 0
