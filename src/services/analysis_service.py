"""Main analysis orchestration with bounded transport retries and one refinement."""

from __future__ import annotations

import random
import time
from collections.abc import Callable
from datetime import UTC, datetime

from src.config import Settings
from src.domain.enums import (
    AnalysisStage,
    FailureType,
    IssueSeverity,
    PromptingStrategy,
    ValidationStatus,
)
from src.domain.models import (
    AnalysisOutcome,
    AnalysisRequest,
    AttemptRecord,
    LLMRequest,
    LLMResponse,
    PromptPackage,
    ProviderAuthenticationError,
    ProviderBadRequestError,
    ProviderError,
    ProviderRateLimitError,
    ProviderTimeoutError,
    ProviderTransientError,
    ValidationIssue,
    ValidationOutcome,
)
from src.observability.logging import redact
from src.prompts.manager import PromptManager
from src.providers.base import LLMProvider
from src.storage.repositories import AnalysisRepository
from src.utils.ids import random_id
from src.utils.text import InputValidationError, validate_incident_text
from src.validation.language import detect_input_language
from src.validation.pipeline import validate_response


class CallExhaustedError(RuntimeError):
    def __init__(self, original: ProviderError, retries: int):
        super().__init__(str(original))
        self.original = original
        self.retries = retries


class AnalysisService:
    """Coordinate prompts, provider calls, validation, refinement, repair, and storage."""

    def __init__(
        self,
        settings: Settings,
        provider: LLMProvider,
        prompt_manager: PromptManager,
        repository: AnalysisRepository | None = None,
        sleeper: Callable[[float], None] = time.sleep,
        jitter: Callable[[float, float], float] = random.uniform,
    ):
        self.settings = settings
        self.provider = provider
        self.prompt_manager = prompt_manager
        self.repository = repository
        self.sleeper = sleeper
        self.jitter = jitter

    def analyze(self, request: AnalysisRequest) -> AnalysisOutcome:
        started = time.perf_counter()
        analysis_id = random_id("analysis")
        correlation_id = random_id("corr")
        try:
            incident_text = validate_incident_text(request.incident_text)
        except InputValidationError as exc:
            validation = ValidationOutcome(
                status=ValidationStatus.INVALID_TERMINAL,
                issues=[
                    ValidationIssue(
                        code="INPUT_INVALID",
                        severity=IssueSeverity.ERROR,
                        message=str(exc),
                    )
                ],
            )
            outcome = AnalysisOutcome(
                analysis_id=analysis_id,
                correlation_id=correlation_id,
                request=request,
                detected_input_language=detect_input_language(request.incident_text),
                prompt_version=self.prompt_manager.PROMPT_VERSION,
                prompt_hash="",
                provider=request.provider_name,
                model=request.model,
                validation=validation,
                failure_type=FailureType.INPUT,
                total_latency_ms=(time.perf_counter() - started) * 1000,
            )
            self._save_outcome(outcome)
            return outcome

        detected = detect_input_language(incident_text)
        prompt = self.prompt_manager.render(
            request.strategy,
            incident_text,
            request.output_language,
        )
        semantic_calls = 0
        retries = 0
        initial_validation: ValidationOutcome | None = None
        initial_raw: str | None = None
        final_raw: str | None = None
        repair_raw: str | None = None
        validation = ValidationOutcome(status=ValidationStatus.INVALID_TERMINAL)
        result = None
        first_pass_valid = False
        repair_assisted_valid = False
        failure_type = FailureType.NONE
        provider_name = request.provider_name
        model_name = request.model

        try:
            if request.strategy == PromptingStrategy.SELF_REFINEMENT:
                initial_response, used_retries = self._call_with_retry(
                    analysis_id,
                    AnalysisStage.SELF_INITIAL,
                    prompt,
                    request,
                    incident_text,
                    detected.value,
                )
                semantic_calls += 1
                retries += used_retries
                provider_name = initial_response.provider
                model_name = initial_response.resolved_model or initial_response.requested_model
                initial_raw = initial_response.text
                initial_validation = validate_response(
                    initial_raw,
                    incident_text,
                    request.output_language,
                )
                first_pass_valid = initial_validation.json_valid and initial_validation.schema_valid
                refine_prompt = self.prompt_manager.render_self_refinement(
                    incident_text,
                    request.output_language,
                    initial_raw,
                    initial_validation.issues,
                )
                refined_response, used_retries = self._call_with_retry(
                    analysis_id,
                    AnalysisStage.SELF_REFINED,
                    refine_prompt,
                    request,
                    incident_text,
                    detected.value,
                )
                semantic_calls += 1
                retries += used_retries
                final_raw = refined_response.text
                validation = validate_response(
                    final_raw,
                    incident_text,
                    request.output_language,
                )
                # For self-refinement, the refined response is the strategy output.
                # Its pre-repair validity is the comparable first-pass measurement;
                # the initial draft remains separately attributed above.
                first_pass_valid = validation.json_valid and validation.schema_valid
            else:
                response, used_retries = self._call_with_retry(
                    analysis_id,
                    AnalysisStage.PRIMARY,
                    prompt,
                    request,
                    incident_text,
                    detected.value,
                )
                semantic_calls += 1
                retries += used_retries
                provider_name = response.provider
                model_name = response.resolved_model or response.requested_model
                final_raw = response.text
                validation = validate_response(
                    final_raw,
                    incident_text,
                    request.output_language,
                )
                first_pass_valid = validation.json_valid and validation.schema_valid

            if (
                not validation.accepted
                and validation.status == ValidationStatus.INVALID_REPAIRABLE
                and request.allow_json_repair
                and final_raw is not None
            ):
                if initial_validation is None:
                    initial_validation = validation
                repair_prompt = self.prompt_manager.render_json_repair(
                    incident_text,
                    request.output_language,
                    final_raw,
                    validation.issues,
                )
                repair_response, used_retries = self._call_with_retry(
                    analysis_id,
                    AnalysisStage.JSON_REPAIR,
                    repair_prompt,
                    request,
                    incident_text,
                    detected.value,
                )
                semantic_calls += 1
                retries += used_retries
                repair_raw = repair_response.text
                repaired_validation = validate_response(
                    repair_raw,
                    incident_text,
                    request.output_language,
                )
                if repaired_validation.accepted:
                    validation = repaired_validation
                    repair_assisted_valid = True

            result = validation.parsed if validation.accepted else None
            if not validation.accepted:
                failure_type = self._validation_failure(validation, request.strategy)
        except CallExhaustedError as exc:
            retries += exc.retries
            failure_type, code = self._provider_failure(exc.original)
            validation = ValidationOutcome(
                status=ValidationStatus.INVALID_TERMINAL,
                issues=[
                    ValidationIssue(
                        code=code,
                        severity=IssueSeverity.ERROR,
                        message=redact(str(exc.original))[:500],
                    )
                ],
            )

        outcome = AnalysisOutcome(
            analysis_id=analysis_id,
            correlation_id=correlation_id,
            request=request.model_copy(update={"incident_text": incident_text}),
            detected_input_language=detected,
            prompt_version=prompt.prompt_version,
            prompt_hash=prompt.prompt_hash,
            provider=provider_name,
            model=model_name,
            validation=validation,
            result=result,
            initial_validation=initial_validation,
            initial_raw_response=initial_raw,
            final_raw_response=final_raw,
            repair_raw_response=repair_raw,
            first_pass_json_valid=first_pass_valid,
            repair_assisted_valid=repair_assisted_valid,
            final_accepted_valid=validation.accepted,
            retry_count=retries,
            semantic_call_count=semantic_calls,
            total_latency_ms=(time.perf_counter() - started) * 1000,
            failure_type=failure_type,
        )
        self._save_outcome(outcome)
        return outcome

    def _call_with_retry(
        self,
        analysis_id: str,
        stage: AnalysisStage,
        prompt: PromptPackage,
        request: AnalysisRequest,
        incident_text: str,
        input_language: str,
    ) -> tuple[LLMResponse, int]:
        transport_attempt = 0
        while True:
            transport_attempt += 1
            started_at = datetime.now(UTC)
            call_started = time.perf_counter()
            raw_response: str | None = None
            error: ProviderError | None = None
            try:
                llm_request = LLMRequest(
                    messages=prompt.messages,
                    model=request.model,
                    temperature=self.settings.temperature,
                    max_output_tokens=self.settings.max_output_tokens,
                    metadata={
                        "incident_text": incident_text,
                        "output_language": request.output_language.value,
                        "input_language": input_language,
                        "strategy": request.strategy.value,
                        "stage": stage.value,
                    },
                )
                response = self.provider.complete(llm_request)
                raw_response = response.text
            except ProviderError as exc:
                error = exc
            finished_at = datetime.now(UTC)
            latency_ms = (time.perf_counter() - call_started) * 1000
            attempt = AttemptRecord(
                attempt_id=random_id("attempt"),
                analysis_id=analysis_id,
                stage=stage,
                transport_attempt=transport_attempt,
                started_at=started_at,
                finished_at=finished_at,
                latency_ms=latency_ms,
                provider=self.provider.name,
                model=request.model,
                raw_response=raw_response,
                error_type=type(error).__name__ if error else None,
                error_message=redact(str(error))[:500] if error else None,
            )
            if self.repository:
                self.repository.save_attempt(attempt)
            if error is None:
                return response, transport_attempt - 1
            retryable = isinstance(
                error,
                (ProviderRateLimitError, ProviderTimeoutError, ProviderTransientError),
            )
            retries_used = transport_attempt - 1
            if not retryable or retries_used >= self.settings.max_retries:
                raise CallExhaustedError(error, retries_used)
            delay = 2 ** (transport_attempt - 1) + self.jitter(0, 0.2)
            if isinstance(error, ProviderRateLimitError) and error.retry_after is not None:
                delay = max(delay, error.retry_after)
            self.sleeper(delay)

    @staticmethod
    def _provider_failure(error: ProviderError) -> tuple[FailureType, str]:
        if isinstance(error, ProviderAuthenticationError):
            return FailureType.AUTHENTICATION, "AUTHENTICATION_FAILED"
        if isinstance(error, ProviderRateLimitError):
            return FailureType.RATE_LIMIT, "RATE_LIMIT_EXHAUSTED"
        if isinstance(error, ProviderTimeoutError):
            return FailureType.TIMEOUT, "TIMEOUT_EXHAUSTED"
        if isinstance(error, ProviderBadRequestError):
            return FailureType.PROVIDER, "PROVIDER_BAD_REQUEST"
        return FailureType.PROVIDER, "PROVIDER_UNAVAILABLE"

    @staticmethod
    def _validation_failure(
        validation: ValidationOutcome,
        strategy: PromptingStrategy,
    ) -> FailureType:
        codes = {issue.code for issue in validation.issues}
        if "INVALID_JSON" in codes:
            return FailureType.INVALID_JSON
        if any(code.startswith("SCHEMA_") or code == "UNSUPPORTED_ENUM" for code in codes):
            return FailureType.SCHEMA
        if "RISKY_RECOMMENDATION" in codes:
            return FailureType.SAFETY
        if any(code.startswith("EVIDENCE_") for code in codes):
            return FailureType.GROUNDING
        if strategy == PromptingStrategy.SELF_REFINEMENT:
            return FailureType.REFINEMENT
        return FailureType.INTERNAL

    def _save_outcome(self, outcome: AnalysisOutcome) -> None:
        if not self.repository:
            return
        store_raw = self.settings.store_raw_inputs or outcome.request.store_raw_override
        self.repository.save_outcome(
            outcome,
            raw_input=outcome.request.incident_text if store_raw else None,
        )
