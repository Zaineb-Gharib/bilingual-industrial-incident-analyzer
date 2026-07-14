"""Load, validate, hash, and inspect the paired JSONL dataset."""

from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from pathlib import Path

from src.domain.enums import DatasetSplit
from src.schemas.dataset import DatasetScenarioPair


class DatasetValidationError(ValueError):
    pass


def load_dataset(path: Path) -> list[DatasetScenarioPair]:
    records = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            records.append(DatasetScenarioPair.model_validate_json(line))
        except Exception as exc:
            raise DatasetValidationError(
                f"Invalid JSONL record at line {line_number}: {exc}"
            ) from exc
    return records


def dataset_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_dataset(
    records: list[DatasetScenarioPair],
    few_shot_example_ids: list[str] | None = None,
) -> dict[str, object]:
    errors: list[str] = []
    ids = [record.scenario_id for record in records]
    if len(records) != 40:
        errors.append(f"expected 40 scenario pairs, found {len(records)}")
    if len(ids) != len(set(ids)):
        errors.append("scenario IDs are not unique")
    split_counts = Counter(record.split.value for record in records)
    if split_counts != {"development": 10, "evaluation": 30}:
        errors.append(f"unexpected split counts: {dict(split_counts)}")
    category_counts = Counter(record.category.value for record in records)
    if set(category_counts.values()) != {4} or len(category_counts) != 10:
        errors.append(f"categories are not balanced at four pairs each: {dict(category_counts)}")
    pending = sum(record.translation_review_status == "pending_manual_review" for record in records)
    dev_ids = {record.scenario_id for record in records if record.split == DatasetSplit.DEVELOPMENT}
    for example_id in few_shot_example_ids or []:
        if example_id not in dev_ids:
            errors.append(f"few-shot example is not development-only: {example_id}")
    overlap_flags = leakage_overlap_flags(records)
    if errors:
        raise DatasetValidationError("; ".join(errors))
    return {
        "scenario_pairs": len(records),
        "language_specific_reports": len(records) * 2,
        "split_counts": dict(split_counts),
        "category_counts": dict(category_counts),
        "pending_manual_review": pending,
        "overlap_flags_for_manual_review": overlap_flags,
    }


def leakage_overlap_flags(
    records: list[DatasetScenarioPair],
    threshold: float = 0.72,
) -> list[dict[str, object]]:
    development = [record for record in records if record.split == DatasetSplit.DEVELOPMENT]
    evaluation = [record for record in records if record.split == DatasetSplit.EVALUATION]
    flags = []
    for dev in development:
        for test in evaluation:
            score = _jaccard(_english_shingles(dev.source_en), _english_shingles(test.source_en))
            if score >= threshold:
                flags.append(
                    {
                        "development_id": dev.scenario_id,
                        "evaluation_id": test.scenario_id,
                        "english_shingle_jaccard": round(score, 3),
                    }
                )
    return flags


def _english_shingles(text: str, size: int = 5) -> set[str]:
    words = re.findall(r"[a-z0-9]+", text.lower())
    return {" ".join(words[index : index + size]) for index in range(len(words) - size + 1)}


def _jaccard(left: set[str], right: set[str]) -> float:
    if not left or not right:
        return 0.0
    return len(left & right) / len(left | right)


def load_few_shot_ids(path: Path) -> list[str]:
    examples = json.loads(path.read_text(encoding="utf-8"))
    return [str(example["scenario_id"]) for example in examples]
