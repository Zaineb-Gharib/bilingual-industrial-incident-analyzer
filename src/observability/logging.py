"""Structured logging with conservative secret redaction."""

from __future__ import annotations

import json
import logging
import re
from datetime import UTC, datetime
from typing import Any

_SECRET_PATTERNS = [
    re.compile(r"(?<![A-Za-z0-9])sk-[A-Za-z0-9_-]{12,}"),
    re.compile(r"(?i)(api[_-]?key\s*[=:]\s*)\S+"),
    re.compile(r"(?i)(authorization\s*[=:]\s*bearer\s+)\S+"),
]


def redact(value: str) -> str:
    result = value
    for pattern in _SECRET_PATTERNS:
        if pattern.groups:
            result = pattern.sub(r"\1[REDACTED]", result)
        else:
            result = pattern.sub("[REDACTED]", result)
    return result


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": redact(record.getMessage()),
        }
        if hasattr(record, "correlation_id"):
            payload["correlation_id"] = record.correlation_id
        return json.dumps(payload, ensure_ascii=False)


def configure_logging(level: str = "INFO") -> None:
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level)
