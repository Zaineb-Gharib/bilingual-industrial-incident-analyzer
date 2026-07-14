"""Small deterministic EN/ZH language hints used before and after model calls."""

from __future__ import annotations

import re

from src.domain.enums import InputLanguage, OutputLanguage

_CJK = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff]")
_LATIN = re.compile(r"[A-Za-z]")


def language_counts(text: str) -> tuple[int, int]:
    return len(_CJK.findall(text)), len(_LATIN.findall(text))


def detect_input_language(text: str) -> InputLanguage:
    cjk, latin = language_counts(text)
    if cjk == 0 and latin == 0:
        return InputLanguage.UNKNOWN
    if cjk >= 2 and latin >= 8:
        ratio = min(cjk, latin) / max(cjk, latin)
        if ratio >= 0.18:
            return InputLanguage.MIXED
    if cjk >= 2 and cjk >= latin * 0.35:
        return InputLanguage.ZH
    if latin >= 3:
        return InputLanguage.EN
    return InputLanguage.UNKNOWN


def output_language_looks_wrong(text: str, requested: OutputLanguage) -> bool:
    cjk, latin = language_counts(text)
    if requested == OutputLanguage.ZH:
        return cjk < 2 and latin > 12
    return cjk > 12 and cjk > latin * 0.35
