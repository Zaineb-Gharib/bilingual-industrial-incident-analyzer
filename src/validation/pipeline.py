"""End-to-end deterministic validation of one raw provider response."""

from __future__ import annotations

from src.domain.enums import IssueSeverity, OutputLanguage, ValidationStatus
from src.domain.models import ValidationIssue, ValidationOutcome
from src.validation.grounding import validate_grounding
from src.validation.language import output_language_looks_wrong
from src.validation.parser import parse_json_object
from src.validation.safety import validate_safety
from src.validation.schema_validator import validate_incident_schema


def validate_response(
    raw_response: str,
    source_report: str,
    requested_output_language: OutputLanguage,
) -> ValidationOutcome:
    parsed_json = parse_json_object(raw_response)
    if parsed_json.error:
        return ValidationOutcome(
            status=ValidationStatus.INVALID_REPAIRABLE,
            issues=[
                ValidationIssue(
                    code="INVALID_JSON",
                    severity=IssueSeverity.ERROR,
                    message=parsed_json.error,
                    retryable=True,
                )
            ],
            normalization_applied=parsed_json.normalization_applied,
        )
    analysis, schema_issues = validate_incident_schema(parsed_json.value or {})
    if analysis is None:
        return ValidationOutcome(
            status=ValidationStatus.INVALID_REPAIRABLE,
            issues=schema_issues,
            json_valid=True,
            normalization_applied=parsed_json.normalization_applied,
        )
    issues: list[ValidationIssue] = []
    if analysis.output_language != requested_output_language:
        issues.append(
            ValidationIssue(
                code="OUTPUT_LANGUAGE_MISMATCH",
                field_path="output_language",
                severity=IssueSeverity.ERROR,
                message="Declared output language differs from the user request.",
                retryable=False,
            )
        )
    narrative = " ".join(
        [
            analysis.incident_title,
            analysis.affected_system,
            *analysis.main_symptoms,
            analysis.suspected_cause.statement,
            analysis.uncertainty_explanation,
        ]
    )
    if output_language_looks_wrong(narrative, requested_output_language):
        issues.append(
            ValidationIssue(
                code="OUTPUT_LANGUAGE_CONTENT_MISMATCH",
                field_path="narrative_fields",
                severity=IssueSeverity.WARNING,
                message="Narrative text may not use the requested language consistently.",
            )
        )
    grounding_issues, grounded, returned = validate_grounding(analysis, source_report)
    issues.extend(grounding_issues)
    issues.extend(validate_safety(analysis, source_report))
    errors = [issue for issue in issues if issue.severity == IssueSeverity.ERROR]
    if errors:
        status = ValidationStatus.INVALID_TERMINAL
    elif issues:
        status = ValidationStatus.VALID_WITH_WARNINGS
    else:
        status = ValidationStatus.VALID
    return ValidationOutcome(
        status=status,
        parsed=analysis,
        issues=issues,
        json_valid=True,
        schema_valid=True,
        grounded_evidence_items=grounded,
        returned_evidence_items=returned,
        normalization_applied=parsed_json.normalization_applied,
    )
