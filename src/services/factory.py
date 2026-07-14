"""Construct application services for Streamlit, scripts, and tests."""

from __future__ import annotations

from src.config import Settings
from src.prompts.manager import PromptManager
from src.providers.factory import create_provider
from src.services.analysis_service import AnalysisService
from src.storage.repositories import AnalysisRepository


def build_analysis_service(
    settings: Settings,
    provider_name: str | None = None,
) -> AnalysisService:
    provider = create_provider(settings, provider_name)
    repository = AnalysisRepository(settings.database_path)
    prompts = PromptManager(settings.prompt_dir)
    return AnalysisService(settings, provider, prompts, repository)
