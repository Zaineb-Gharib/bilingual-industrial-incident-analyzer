from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

import pytest

from src.config import Settings
from src.domain.enums import CauseCertainty, OutputLanguage
from src.schemas.incident import (
    Confidence,
    EvidenceItem,
    IncidentAnalysis,
    RecommendedAction,
    SuspectedCause,
)

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def source_en() -> str:
    return "Database access stopped at 09:14 after a migration checksum mismatch."


@pytest.fixture
def valid_analysis(source_en: str) -> IncidentAnalysis:
    return IncidentAnalysis(
        input_language="en",
        output_language=OutputLanguage.EN,
        incident_title="Database access incident",
        incident_category="database_failure",
        severity="high",
        affected_system="database",
        main_symptoms=["Database access stopped."],
        suspected_cause=SuspectedCause(
            statement="migration checksum mismatch",
            certainty=CauseCertainty.EXPLICIT,
        ),
        recommended_immediate_actions=[
            RecommendedAction(
                action="Notify the authorized database owner.",
                rationale="The report states that access stopped.",
                requires_authorization=True,
            )
        ],
        recommended_long_term_actions=["Review the migration validation procedure."],
        responsible_team="database_operations",
        evidence=[
            EvidenceItem(
                quote=source_en,
                supports_fields=["affected_system", "main_symptoms", "suspected_cause"],
            )
        ],
        uncertainty_explanation="The report does not prove every contributing factor.",
        confidence=Confidence(level="medium", explanation="The stated cause is explicit."),
        warnings=[],
    )


@pytest.fixture
def valid_json(valid_analysis: IncidentAnalysis) -> str:
    return valid_analysis.model_dump_json()


@pytest.fixture
def settings(tmp_path: Path) -> Settings:
    base = Settings.from_env(ROOT)
    return replace(
        base,
        provider="demo",
        model="demo-v1",
        database_path=tmp_path / "test.db",
        max_retries=2,
    )


def as_row(**overrides: object) -> dict[str, object]:
    row: dict[str, object] = {
        "analysis_id": "analysis-1",
        "scenario_id": "EVAL-SRV-001",
        "strategy": "zero_shot",
        "input_language": "en",
        "output_language": "en",
        "parsed_response": json.dumps({}),
        "validation_issues": "[]",
        "first_pass_json_valid": 1,
        "repair_assisted_valid": 0,
        "final_accepted_valid": 1,
        "latency_ms": 10.0,
    }
    row.update(overrides)
    return row
