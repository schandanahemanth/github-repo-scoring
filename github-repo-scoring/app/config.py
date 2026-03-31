from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    github_token: str | None
    score_weight_stars: float
    score_weight_forks: float
    score_weight_recency: float
    score_recency_decay_days: int

    @classmethod
    def from_env(cls) -> "Settings":
        github_token = os.getenv("GITHUB_TOKEN") or None
        return cls(
            github_token=github_token,
            score_weight_stars=float(os.getenv("SCORE_WEIGHT_STARS", "0.5")),
            score_weight_forks=float(os.getenv("SCORE_WEIGHT_FORKS", "0.3")),
            score_weight_recency=float(os.getenv("SCORE_WEIGHT_RECENCY", "0.2")),
            score_recency_decay_days=int(os.getenv("SCORE_RECENCY_DECAY_DAYS", "90")),
        )


def get_settings() -> Settings:
    return Settings.from_env()
