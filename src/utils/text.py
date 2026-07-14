"""Unicode-safe input helpers."""

from __future__ import annotations

import hashlib
import unicodedata

MIN_INPUT_CHARS = 10
MAX_INPUT_CHARS = 4000


class InputValidationError(ValueError):
    pass


def validate_incident_text(text: str) -> str:
    trimmed = text.strip()
    if not trimmed:
        raise InputValidationError("Incident report must not be empty.")
    if len(trimmed) < MIN_INPUT_CHARS:
        raise InputValidationError(
            f"Incident report must contain at least {MIN_INPUT_CHARS} characters."
        )
    if len(trimmed) > MAX_INPUT_CHARS:
        raise InputValidationError(
            f"Incident report exceeds the {MAX_INPUT_CHARS}-character limit."
        )
    return trimmed


def nfc(text: str) -> str:
    return unicodedata.normalize("NFC", text)


def text_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()
