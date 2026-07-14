"""Map Pydantic errors to stable application issue records."""

from __future__ import annotations

from typing import Any

from pydantic import ValidationError

from src.domain.enums import IssueSeverity
from src.domain.models import ValidationIssue
from src.schemas.incident import IncidentAnalysis


def validate_incident_schema(
    value: dict[str, Any],
) -> tuple[IncidentAnalysis | None, list[ValidationIssue]]:
    try:
        return IncidentAnalysis.model_validate(value), []
    except ValidationError as exc:
        issues = []
        for error in exc.errors(include_url=False):
            location = ".".join(str(part) for part in error["loc"])
            error_type = str(error["type"])
            if error_type in {"missing"}:
                code = "SCHEMA_MISSING_FIELD"
            elif "literal" in error_type or "enum" in error_type:
                code = "UNSUPPORTED_ENUM"
            elif "extra" in error_type:
                code = "SCHEMA_EXTRA_FIELD"
            else:
                code = "SCHEMA_TYPE_ERROR"
            issues.append(
                ValidationIssue(
                    code=code,
                    field_path=location,
                    severity=IssueSeverity.ERROR,
                    message=str(error["msg"]),
                    retryable=True,
                )
            )
        return None, issues
