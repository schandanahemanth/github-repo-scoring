from __future__ import annotations

"""Score repositories with weighted log-scaled popularity and recency decay.

The algorithm combines stars, forks, and update recency using:
0.5 * log1p(stars) + 0.3 * log1p(forks) + 0.2 * exp(-days_since_update / 90)

Log scaling keeps very large repositories from dominating the ranking, while
the exponential decay term adds a freshness bonus for actively maintained code.
The default weights and decay window are configurable through application
settings so the ranking can be tuned without code changes.
"""

import math
from datetime import datetime, timezone

from app.config import Settings
from app.logger import logger
from app.models import Repository, ScoredRepository


def _as_utc(value: datetime) -> datetime:
    """Convert a datetime value to UTC while preserving the instant in time."""
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def days_since_update(pushed_at: datetime, now: datetime | None = None) -> float:
    """Calculate the elapsed days between now and the last repository push."""
    current_time = _as_utc(now or datetime.now(timezone.utc))
    pushed_at_utc = _as_utc(pushed_at)
    return (current_time - pushed_at_utc).total_seconds() / 86_400


def calculate_score(
    *,
    stars: int,
    forks: int,
    pushed_at: datetime,
    settings: Settings,
    now: datetime | None = None,
) -> float:
    """Compute the configured popularity score for a repository."""
    elapsed_days = days_since_update(pushed_at=pushed_at, now=now)
    score = round(
        settings.score_weight_stars * math.log1p(stars)
        + settings.score_weight_forks * math.log1p(forks)
        + settings.score_weight_recency
        * math.exp(-elapsed_days / settings.score_recency_decay_days),
        6,
    )
    logger.info(
        "Calculated repository score stars=%s forks=%s days_since_update=%.2f score=%.6f",
        stars,
        forks,
        elapsed_days,
        score,
    )
    return score


def score_repository(
    repository: Repository,
    settings: Settings,
    now: datetime | None = None,
) -> ScoredRepository:
    """Attach a computed popularity score to a repository model."""
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
        score=calculate_score(
            stars=repository.stars,
            forks=repository.forks,
            pushed_at=repository.pushed_at,
            settings=settings,
            now=now,
        ),
    )


def rank_repositories(
    repositories: list[Repository],
    settings: Settings,
    now: datetime | None = None,
) -> list[ScoredRepository]:
    """Score repositories and return them ordered by descending score."""
    logger.info("Ranking %s repositories using configured scoring weights", len(repositories))
    scored = [score_repository(repository, settings=settings, now=now) for repository in repositories]
    return sorted(scored, key=lambda repository: repository.score, reverse=True)
