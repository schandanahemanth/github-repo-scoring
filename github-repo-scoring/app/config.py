from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    github_token: str | None = None
    score_weight_stars: float = 0.5
    score_weight_forks: float = 0.3
    score_weight_recency: float = 0.2
    score_recency_decay_days: int = 90

    @classmethod
    def from_env(cls) -> "Settings":
        defaults = cls()
        return cls(
            github_token=os.getenv("GITHUB_TOKEN", defaults.github_token or "") or None,
            score_weight_stars=float(os.getenv("SCORE_WEIGHT_STARS", str(defaults.score_weight_stars))),
            score_weight_forks=float(os.getenv("SCORE_WEIGHT_FORKS", str(defaults.score_weight_forks))),
            score_weight_recency=float(os.getenv("SCORE_WEIGHT_RECENCY", str(defaults.score_weight_recency))),
            score_recency_decay_days=int(os.getenv("SCORE_RECENCY_DECAY_DAYS", str(defaults.score_recency_decay_days))),
        )


def get_settings() -> Settings:
    return Settings.from_env()
