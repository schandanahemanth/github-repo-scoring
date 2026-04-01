from app.core.config import Settings


def test_settings_use_defaults(monkeypatch) -> None:
    """
    Verify settings fall back to the expected default values.
    """
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    monkeypatch.delenv("GITHUB_API_VERSION", raising=False)
    monkeypatch.delenv("GITHUB_CACHE_TTL_SECONDS", raising=False)
    monkeypatch.delenv("SCORE_WEIGHT_STARS", raising=False)
    monkeypatch.delenv("SCORE_WEIGHT_FORKS", raising=False)
    monkeypatch.delenv("SCORE_WEIGHT_RECENCY", raising=False)
    monkeypatch.delenv("SCORE_RECENCY_DECAY_DAYS", raising=False)

    settings = Settings.from_env()

    assert settings.github_token is None
    assert settings.github_api_version == "2026-03-10"
    assert settings.github_cache_ttl_seconds == 300
    assert settings.score_weight_stars == 0.5
    assert settings.score_weight_forks == 0.3
    assert settings.score_weight_recency == 0.2
    assert settings.score_recency_decay_days == 90
