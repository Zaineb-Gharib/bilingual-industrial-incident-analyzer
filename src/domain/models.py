"""Provider-neutral requests, outcomes, attempts, and validation issues."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from src.domain.enums import (
    AnalysisStage,
    FailureType,
    InputLanguage,
    IssueSeverity,
    OutputLanguage,
    PromptingStrategy,
    ValidationStatus,
)
from src.schemas.incident import IncidentAnalysis


class DomainModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class PromptMessage(DomainModel):
    role: str
    content: str


class PromptPackage(DomainModel):
    messages: list[PromptMessage]
    prompt_version: str = "1.0"
    template_name: str
    prompt_hash: str
    example_ids: list[str] = Field(default_factory=list)


class LLMRequest(DomainModel):
    messages: list[PromptMessage]
    model: str
    temperature: float = 0.0
    max_output_tokens: int = 1800
    request_json_object: bool = True
    metadata: dict[str, Any] = Field(default_factory=dict)


class LLMResponse(DomainModel):
    text: str
    provider: str
    requested_model: str
    resolved_model: str | None = None
    finish_reason: str | None = None
    provider_request_id: str | None = None
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    total_tokens: int | None = None
    latency_ms: float


class ValidationIssue(DomainModel):
    code: str
    field_path: str = ""
    severity: IssueSeverity
    message: str
    retryable: bool = False


class ValidationOutcome(DomainModel):
    status: ValidationStatus
    parsed: IncidentAnalysis | None = None
    issues: list[ValidationIssue] = Field(default_factory=list)
    json_valid: bool = False
    schema_valid: bool = False
    grounded_evidence_items: int = 0
    returned_evidence_items: int = 0
    normalization_applied: bool = False

    @property
    def accepted(self) -> bool:
        return self.status in {
            ValidationStatus.VALID,
            ValidationStatus.VALID_WITH_WARNINGS,
        }


class AnalysisRequest(DomainModel):
    incident_text: str
    output_language: OutputLanguage
    strategy: PromptingStrategy
    provider_name: str = "demo"
    model: str = "demo-v1"
    run_id: str | None = None
    task_id: str | None = None
    dataset_version: str | None = None
    scenario_id: str | None = None
    store_raw_override: bool = False
    allow_json_repair: bool = True


class AttemptRecord(DomainModel):
    attempt_id: str
    analysis_id: str
    stage: AnalysisStage
    transport_attempt: int
    started_at: datetime
    finished_at: datetime
    latency_ms: float
    provider: str
    model: str
    raw_response: str | None = None
    error_type: str | None = None
    error_message: str | None = None


class AnalysisOutcome(DomainModel):
    analysis_id: str
    correlation_id: str
    request: AnalysisRequest
    detected_input_language: InputLanguage
    prompt_version: str
    prompt_hash: str
    provider: str
    model: str
    validation: ValidationOutcome
    result: IncidentAnalysis | None = None
    initial_validation: ValidationOutcome | None = None
    initial_raw_response: str | None = None
    final_raw_response: str | None = None
    repair_raw_response: str | None = None
    first_pass_json_valid: bool = False
    repair_assisted_valid: bool = False
    final_accepted_valid: bool = False
    retry_count: int = 0
    semantic_call_count: int = 0
    total_latency_ms: float = 0.0
    failure_type: FailureType = FailureType.NONE
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class ProviderError(RuntimeError):
    """Base class for translated provider errors."""


class ProviderAuthenticationError(ProviderError):
    pass


class ProviderRateLimitError(ProviderError):
    def __init__(self, message: str, retry_after: float | None = None):
        super().__init__(message)
        self.retry_after = retry_after


class ProviderTimeoutError(ProviderError):
    pass


class ProviderTransientError(ProviderError):
    pass


class ProviderBadRequestError(ProviderError):
    pass


class ProviderUnsupportedResponseError(ProviderError):
    pass
