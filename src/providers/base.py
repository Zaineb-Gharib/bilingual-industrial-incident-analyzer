"""Protocol implemented by every LLM provider adapter."""

from typing import Protocol, runtime_checkable

from src.domain.models import LLMRequest, LLMResponse


@runtime_checkable
class LLMProvider(Protocol):
    name: str

    def complete(self, request: LLMRequest) -> LLMResponse:
        """Return provider-neutral text and metadata or raise a translated error."""
