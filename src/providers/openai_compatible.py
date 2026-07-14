"""Optional real adapter implemented with the supported OpenAI Python SDK."""

from __future__ import annotations

import time

from src.domain.models import (
    LLMRequest,
    LLMResponse,
    ProviderAuthenticationError,
    ProviderBadRequestError,
    ProviderRateLimitError,
    ProviderTimeoutError,
    ProviderTransientError,
    ProviderUnsupportedResponseError,
)


class OpenAICompatibleProvider:
    """Chat-Completions adapter isolated from application services."""

    name = "openai_compatible"

    def __init__(
        self,
        api_key: str,
        timeout_seconds: float,
        base_url: str | None = None,
    ):
        if not api_key:
            raise ProviderAuthenticationError("A local LLM_API_KEY is required.")
        try:
            import openai
        except ImportError as exc:
            raise ProviderBadRequestError(
                "The openai package is not installed. Install project requirements."
            ) from exc
        self._openai = openai
        kwargs: dict[str, object] = {
            "api_key": api_key,
            "timeout": timeout_seconds,
            "max_retries": 0,
        }
        if base_url:
            kwargs["base_url"] = base_url
        self._client = openai.OpenAI(**kwargs)

    def complete(self, request: LLMRequest) -> LLMResponse:
        started = time.perf_counter()
        try:
            response = self._client.chat.completions.create(
                model=request.model,
                messages=[message.model_dump() for message in request.messages],
                temperature=request.temperature,
                max_completion_tokens=request.max_output_tokens,
                response_format={"type": "json_object"} if request.request_json_object else None,
            )
        except Exception as exc:
            self._translate_error(exc)
            raise AssertionError("unreachable") from exc
        if not response.choices:
            raise ProviderUnsupportedResponseError("The provider returned no completion choices.")
        message = response.choices[0].message
        text = message.content or ""
        if not text.strip():
            raise ProviderUnsupportedResponseError("The provider returned an empty response.")
        usage = response.usage
        return LLMResponse(
            text=text,
            provider=self.name,
            requested_model=request.model,
            resolved_model=getattr(response, "model", None),
            finish_reason=response.choices[0].finish_reason,
            provider_request_id=getattr(response, "_request_id", None)
            or getattr(response, "id", None),
            prompt_tokens=getattr(usage, "prompt_tokens", None) if usage else None,
            completion_tokens=getattr(usage, "completion_tokens", None) if usage else None,
            total_tokens=getattr(usage, "total_tokens", None) if usage else None,
            latency_ms=(time.perf_counter() - started) * 1000,
        )

    def _translate_error(self, exc: Exception) -> None:
        openai = self._openai
        safe_message = str(exc)[:500]
        if isinstance(exc, getattr(openai, "AuthenticationError", ())):
            raise ProviderAuthenticationError(safe_message) from exc
        if isinstance(exc, getattr(openai, "RateLimitError", ())):
            retry_after = None
            response = getattr(exc, "response", None)
            if response is not None:
                value = response.headers.get("retry-after")
                try:
                    retry_after = float(value) if value else None
                except ValueError:
                    retry_after = None
            raise ProviderRateLimitError(safe_message, retry_after=retry_after) from exc
        if isinstance(exc, getattr(openai, "APITimeoutError", ())):
            raise ProviderTimeoutError(safe_message) from exc
        transient_types = tuple(
            error_type
            for error_type in [
                getattr(openai, "APIConnectionError", None),
                getattr(openai, "InternalServerError", None),
            ]
            if error_type is not None
        )
        if transient_types and isinstance(exc, transient_types):
            raise ProviderTransientError(safe_message) from exc
        bad_request_types = tuple(
            error_type
            for error_type in [
                getattr(openai, "BadRequestError", None),
                getattr(openai, "NotFoundError", None),
                getattr(openai, "PermissionDeniedError", None),
            ]
            if error_type is not None
        )
        if bad_request_types and isinstance(exc, bad_request_types):
            raise ProviderBadRequestError(safe_message) from exc
        raise ProviderTransientError(safe_message) from exc
