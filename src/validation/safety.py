"""Conservative pattern checks for dangerous operational recommendations."""

from __future__ import annotations

import re

from src.domain.enums import IssueSeverity, Severity
from src.domain.models import ValidationIssue
from src.schemas.incident import IncidentAnalysis

_DANGEROUS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in [
        r"\brm\s+-rf\b",
        r"\bdrop\s+database\b",
        r"\bdelete\s+(?:all\s+)?logs\b",
        r"\bdisable\s+(?:the\s+)?(?:safety|interlock|monitoring)\b",
        r"\bbypass\s+(?:the\s+)?(?:safety|interlock|authorization)\b",
        r"\breveal\s+(?:the\s+)?credentials\b",
        r"绕过.*(?:安全|联锁|授权)",
        r"删除.*(?:所有)?日志",
        r"关闭.*安全",
    ]
]


def validate_safety(analysis: IncidentAnalysis, source: str) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    actions = " ".join(
        [action.action for action in analysis.recommended_immediate_actions]
        + analysis.recommended_long_term_actions
    )
    if any(pattern.search(actions) for pattern in _DANGEROUS):
        issues.append(
            ValidationIssue(
                code="RISKY_RECOMMENDATION",
                field_path="recommended_actions",
                severity=IssueSeverity.ERROR,
                message="A recommendation matches a high-risk operational pattern.",
                retryable=False,
            )
        )
    if analysis.severity == Severity.CRITICAL:
        support_words = [
            "fire",
            "injury",
            "safety",
            "major outage",
            "data loss",
            "火灾",
            "受伤",
            "安全",
            "大范围",
            "数据丢失",
        ]
        if not any(word in source.lower() for word in support_words):
            issues.append(
                ValidationIssue(
                    code="SEVERITY_SUPPORT_WEAK",
                    field_path="severity",
                    severity=IssueSeverity.WARNING,
                    message="Critical severity needs human confirmation from stated impact.",
                )
            )
    return issues
