from pathlib import Path

from src.config import Settings


def test_safe_summary_never_contains_key(tmp_path: Path) -> None:
    settings = Settings.from_env(tmp_path, {"LLM_API_KEY": "super-secret-value"})
    summary = settings.safe_summary()
    assert "super-secret-value" not in str(summary)
    assert summary["api_key_configured"] is True


def test_environment_override_is_applied(tmp_path: Path) -> None:
    settings = Settings.from_env(
        tmp_path,
        {"LLM_PROVIDER": "demo", "LLM_MODEL": "chosen", "LLM_MAX_RETRIES": "4"},
    )
    assert settings.provider == "demo"
    assert settings.model == "chosen"
    assert settings.max_retries == 4
