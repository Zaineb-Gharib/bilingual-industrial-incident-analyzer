"""Strict Pydantic v2 contract for LLM incident-analysis output."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from src.domain.enums import (
    CauseCertainty,
    IncidentCategory,
    InputLanguage,
    OutputLanguage,
    ResponsibleTeam,
    Severity,
)


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class SuspectedCause(StrictModel):
    statement: str = Field(min_length=1, max_length=500)
    certainty: CauseCertainty

    @model_validator(mode="after")
    def unknown_must_stay_unknown(self) -> SuspectedCause:
        if self.certainty == CauseCertainty.UNKNOWN:
            allowed = {"unknown", "未知", "不明"}
            if self.statement.strip().lower() not in allowed:
                raise ValueError("an unknown cause must use a language-appropriate unknown value")
        return self


class RecommendedAction(StrictModel):
    action: str = Field(min_length=1, max_length=500)
    rationale: str = Field(min_length=1, max_length=500)
    requires_authorization: bool = True


class EvidenceItem(StrictModel):
    quote: str = Field(min_length=1, max_length=1200)
    supports_fields: list[str] = Field(min_length=1, max_length=8)

    @field_validator("supports_fields")
    @classmethod
    def evidence_field_names_must_be_nonempty(cls, values: list[str]) -> list[str]:
        if any(not value.strip() for value in values):
            raise ValueError("evidence field names must not be blank")
        return values


class Confidence(StrictModel):
    level: Literal["high", "medium", "low"]
    explanation: str = Field(min_length=1, max_length=700)


class IncidentAnalysis(StrictModel):
    schema_version: Literal["1.0"] = "1.0"
    prompt_version: Literal["1.0"] = "1.0"
    input_language: InputLanguage
    output_language: OutputLanguage
    incident_title: str = Field(min_length=1, max_length=200)
    incident_category: IncidentCategory
    severity: Severity
    affected_system: str = Field(min_length=1, max_length=300)
    main_symptoms: list[str] = Field(min_length=1, max_length=10)
    suspected_cause: SuspectedCause
    recommended_immediate_actions: list[RecommendedAction] = Field(min_length=1, max_length=5)
    recommended_long_term_actions: list[str] = Field(min_length=1, max_length=5)
    responsible_team: ResponsibleTeam
    evidence: list[EvidenceItem] = Field(min_length=1, max_length=10)
    uncertainty_explanation: str = Field(min_length=1, max_length=700)
    confidence: Confidence
    warnings: list[str] = Field(default_factory=list, max_length=10)

    @field_validator("main_symptoms", "recommended_long_term_actions", "warnings")
    @classmethod
    def list_items_must_not_be_blank(cls, values: list[str]) -> list[str]:
        if any(not value.strip() for value in values):
            raise ValueError("list items must not be blank")
        return values
