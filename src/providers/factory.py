"""Create configured adapters without leaking provider details into services."""

from src.config import Settings
from src.domain.models import ProviderBadRequestError
from src.providers.base import LLMProvider
from src.providers.demo import DemoProvider
from src.providers.openai_compatible import OpenAICompatibleProvider


def available_provider_names(settings: Settings) -> list[str]:
    providers = ["demo"]
    if settings.api_key:
        providers.append("openai_compatible")
    return providers


def create_provider(settings: Settings, provider_name: str | None = None) -> LLMProvider:
    name = (provider_name or settings.provider).lower()
    if name == "demo":
        return DemoProvider()
    if name == "openai_compatible":
        return OpenAICompatibleProvider(
            api_key=settings.api_key or "",
            timeout_seconds=settings.timeout_seconds,
            base_url=settings.base_url,
        )
    raise ProviderBadRequestError(f"Unsupported provider: {name}")
