"""Verbatim evidence grounding and conservative unsupported-detail warnings."""

from __future__ import annotations

import re
import unicodedata

from src.domain.enums import CauseCertainty, IssueSeverity
from src.domain.models import ValidationIssue
from src.schemas.incident import IncidentAnalysis

ALLOWED_EVIDENCE_FIELDS = {
    "incident_title",
    "incident_category",
    "severity",
    "affected_system",
    "main_symptoms",
    "suspected_cause",
    "responsible_team",
}


def normalize_nfc(text: str) -> str:
    return unicodedata.normalize("NFC", text)


def validate_grounding(
    analysis: IncidentAnalysis,
    source: str,
) -> tuple[list[ValidationIssue], int, int]:
    issues: list[ValidationIssue] = []
    source_nfc = normalize_nfc(source)
    grounded = 0
    for index, item in enumerate(analysis.evidence):
        if normalize_nfc(item.quote) in source_nfc:
            grounded += 1
        else:
            issues.append(
                ValidationIssue(
                    code="EVIDENCE_NOT_IN_SOURCE",
                    field_path=f"evidence.{index}.quote",
                    severity=IssueSeverity.ERROR,
                    message="Evidence quote is not an exact source substring.",
                    retryable=False,
                )
            )
        for field_name in item.supports_fields:
            if field_name not in ALLOWED_EVIDENCE_FIELDS:
                issues.append(
                    ValidationIssue(
                        code="EVIDENCE_UNSUPPORTED_FIELD_NAME",
                        field_path=f"evidence.{index}.supports_fields",
                        severity=IssueSeverity.WARNING,
                        message=f"Evidence references an unknown field: {field_name}",
                    )
                )
    if analysis.suspected_cause.certainty == CauseCertainty.EXPLICIT:
        statement = normalize_nfc(analysis.suspected_cause.statement).lower()
        if statement not in source_nfc.lower():
            issues.append(
                ValidationIssue(
                    code="CAUSE_SUPPORT_WEAK",
                    field_path="suspected_cause",
                    severity=IssueSeverity.WARNING,
                    message="The explicit cause wording is not directly present in the report.",
                )
            )
    issues.extend(_number_warnings(analysis, source_nfc))
    return issues, grounded, len(analysis.evidence)


def _number_warnings(analysis: IncidentAnalysis, source: str) -> list[ValidationIssue]:
    source_numbers = set(re.findall(r"\b\d+(?:\.\d+)?\b", source))
    narrative = " ".join(
        [
            analysis.incident_title,
            analysis.affected_system,
            *analysis.main_symptoms,
            analysis.suspected_cause.statement,
        ]
    )
    generated_numbers = set(re.findall(r"\b\d+(?:\.\d+)?\b", narrative))
    unexpected = sorted(generated_numbers - source_numbers)
    if not unexpected:
        return []
    return [
        ValidationIssue(
            code="UNSUPPORTED_DETAIL_SUSPECTED",
            field_path="narrative_fields",
            severity=IssueSeverity.WARNING,
            message="Generated numerical detail is absent from the report: "
            + ", ".join(unexpected),
        )
    ]
