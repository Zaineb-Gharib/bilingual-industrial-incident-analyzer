"""Typed, environment-based configuration with safe defaults."""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path


def _load_dotenv(path: Path) -> None:
    """Load simple KEY=VALUE lines without overriding real environment variables."""
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            os.environ.setdefault(key, value)


def _bool(value: str | None, default: bool) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    """Application settings. The API key is deliberately excluded from repr."""

    provider: str = "demo"
    model: str = "demo-v1"
    api_key: str | None = field(default=None, repr=False)
    base_url: str | None = None
    timeout_seconds: float = 30.0
    max_retries: int = 2
    temperature: float = 0.0
    max_output_tokens: int = 1800
    store_raw_inputs: bool = False
    database_path: Path = Path("data/local/app.db")
    log_level: str = "INFO"
    prompt_dir: Path = Path("prompts")
    dataset_path: Path = Path("data/incidents_v1.jsonl")

    @classmethod
    def from_env(
        cls,
        root: Path | None = None,
        overrides: Mapping[str, str] | None = None,
    ) -> Settings:
        root = (root or Path.cwd()).resolve()
        _load_dotenv(root / ".env")
        env = dict(os.environ)
        if overrides:
            env.update(overrides)
        key = env.get("LLM_API_KEY", "").strip() or None
        base_url = env.get("LLM_BASE_URL", "").strip() or None
        return cls(
            provider=env.get("LLM_PROVIDER", "demo").strip().lower(),
            model=env.get("LLM_MODEL", "demo-v1").strip(),
            api_key=key,
            base_url=base_url,
            timeout_seconds=float(env.get("LLM_TIMEOUT_SECONDS", "30")),
            max_retries=max(0, int(env.get("LLM_MAX_RETRIES", "2"))),
            temperature=float(env.get("LLM_TEMPERATURE", "0")),
            max_output_tokens=max(256, int(env.get("LLM_MAX_OUTPUT_TOKENS", "1800"))),
            store_raw_inputs=_bool(env.get("APP_STORE_RAW_INPUTS"), False),
            database_path=root / env.get("APP_DATABASE_PATH", "data/local/app.db"),
            log_level=env.get("LOG_LEVEL", "INFO").upper(),
            prompt_dir=root / "prompts",
            dataset_path=root / "data/incidents_v1.jsonl",
        )

    @property
    def live_provider_ready(self) -> bool:
        return self.provider == "openai_compatible" and bool(self.api_key and self.model)

    def safe_summary(self) -> dict[str, object]:
        """Return display/log values without the API key."""
        return {
            "provider": self.provider,
            "model": self.model,
            "base_url_configured": bool(self.base_url),
            "api_key_configured": bool(self.api_key),
            "timeout_seconds": self.timeout_seconds,
            "max_retries": self.max_retries,
            "temperature": self.temperature,
            "max_output_tokens": self.max_output_tokens,
            "store_raw_inputs": self.store_raw_inputs,
            "database_path": str(self.database_path),
            "log_level": self.log_level,
        }
