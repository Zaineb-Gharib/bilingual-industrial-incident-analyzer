"""Pydantic contracts for paired bilingual synthetic incidents."""

from __future__ import annotations

import unicodedata
from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from src.domain.enums import (
    CauseCertainty,
    DatasetSplit,
    IncidentCategory,
    ResponsibleTeam,
    Severity,
)


class DatasetModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class BilingualConcept(DatasetModel):
    id: str = Field(min_length=2, max_length=100)
    en: str = Field(min_length=1, max_length=300)
    zh: str = Field(min_length=1, max_length=300)
    acceptable_en: list[str] = Field(default_factory=list)
    acceptable_zh: list[str] = Field(default_factory=list)


class AffectedSystem(DatasetModel):
    concept_id: str
    en: str
    zh: str


class GoldCause(DatasetModel):
    certainty: CauseCertainty
    en: str
    zh: str


class CreationMetadata(DatasetModel):
    author_id: str
    created_date: date
    reviewer_id: str | None = None
    review_date: date | None = None
    ai_assisted: bool = True


class DatasetScenarioPair(DatasetModel):
    dataset_version: Literal["1.0"]
    scenario_id: str = Field(pattern=r"^(DEV|EVAL)-[A-Z]{3}-\d{3}$")
    split: DatasetSplit
    category: IncidentCategory
    source_en: str = Field(min_length=10, max_length=4000)
    source_zh: str = Field(min_length=5, max_length=4000)
    translation_review_status: Literal["pending_manual_review", "approved", "single_reviewer"]
    translation_reviewer_notes: str
    severity: Severity
    affected_system: AffectedSystem
    symptom_concepts: list[BilingualConcept] = Field(min_length=1)
    suspected_cause: GoldCause
    immediate_action_concepts: list[BilingualConcept] = Field(min_length=1)
    long_term_action_concepts: list[BilingualConcept] = Field(min_length=1)
    responsible_team: ResponsibleTeam
    evidence_spans_en: list[str] = Field(min_length=1)
    evidence_spans_zh: list[str] = Field(min_length=1)
    safety_notes: str
    ambiguity_notes: str
    creation: CreationMetadata

    @model_validator(mode="after")
    def evidence_must_appear_in_matching_source(self) -> DatasetScenarioPair:
        source_en = unicodedata.normalize("NFC", self.source_en)
        source_zh = unicodedata.normalize("NFC", self.source_zh)
        for span in self.evidence_spans_en:
            if unicodedata.normalize("NFC", span) not in source_en:
                raise ValueError(f"English evidence is absent from source: {span}")
        for span in self.evidence_spans_zh:
            if unicodedata.normalize("NFC", span) not in source_zh:
                raise ValueError(f"Chinese evidence is absent from source: {span}")
        prefix = "DEV" if self.split == DatasetSplit.DEVELOPMENT else "EVAL"
        if not self.scenario_id.startswith(prefix):
            raise ValueError("scenario ID prefix must match the split")
        return self
