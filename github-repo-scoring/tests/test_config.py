from app.config import Settings


def test_settings_use_defaults(monkeypatch) -> None:
    """
    Verify settings fall back to the expected default values.
    """
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    monkeypatch.delenv("SCORE_WEIGHT_STARS", raising=False)
    monkeypatch.delenv("SCORE_WEIGHT_FORKS", raising=False)
    monkeypatch.delenv("SCORE_WEIGHT_RECENCY", raising=False)
    monkeypatch.delenv("SCORE_RECENCY_DECAY_DAYS", raising=False)

    settings = Settings.from_env()

    assert settings.github_token is None
    assert settings.score_weight_stars == 0.5
    assert settings.score_weight_forks == 0.3
    assert settings.score_weight_recency == 0.2
    assert settings.score_recency_decay_days == 90
