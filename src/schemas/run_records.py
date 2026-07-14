"""Versioned batch, metric, and manual-review records."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from src.domain.enums import OutputLanguage, PromptingStrategy


class RunModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class EvaluationTask(RunModel):
    task_id: str
    scenario_id: str
    dataset_version: str
    split: str
    source_language: Literal["en", "zh"]
    output_language: OutputLanguage
    strategy: PromptingStrategy
    incident_text: str


class RunManifest(RunModel):
    run_id: str
    dataset_version: str
    dataset_hash: str
    prompt_version: str
    schema_version: str
    provider: str
    model: str
    temperature: float
    timeout_seconds: float
    transport_retries: int
    syntax_repair_enabled: bool
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    task_ids: list[str]
    notes: str = ""


class MetricRecord(RunModel):
    run_id: str
    metric_name: str
    value: float | None
    numerator: float | None
    denominator: float
    exclusions: int = 0
    source: Literal["automatic", "manual", "optional_llm_judge"] = "automatic"
    metric_version: str = "1.0"
    group: dict[str, str] = Field(default_factory=dict)


class ManualReviewRecord(RunModel):
    output_id: str
    reviewer_id: str
    rubric_version: str = "1.0"
    affected_system: int = Field(ge=0, le=2)
    symptoms: int = Field(ge=0, le=2)
    suspected_cause: int = Field(ge=0, le=2)
    immediate_actions: int = Field(ge=0, le=2)
    long_term_actions: int = Field(ge=0, le=2)
    evidence: int = Field(ge=0, le=2)
    uncertainty: int = Field(ge=0, le=2)
    output_language_quality: int = Field(ge=0, le=2)
    factual_claim_units: int = Field(ge=0)
    unsupported_claim_units: int = Field(ge=0)
    dangerous_advice: bool = False
    notes: str = ""
    reviewed_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    def as_metric_payload(self) -> dict[str, Any]:
        dimensions = [
            self.affected_system,
            self.symptoms,
            self.suspected_cause,
            self.immediate_actions,
            self.long_term_actions,
            self.evidence,
            self.uncertainty,
            self.output_language_quality,
        ]
        return {
            "rubric_average": sum(dimensions) / len(dimensions),
            "substantive_hallucination_rate": (
                self.unsupported_claim_units / self.factual_claim_units
                if self.factual_claim_units
                else None
            ),
            "dangerous_advice": self.dangerous_advice,
        }
