from collections import Counter

from src.domain.enums import DatasetSplit
from src.evaluation.dataset_loader import (
    dataset_sha256,
    leakage_overlap_flags,
    load_dataset,
    load_few_shot_ids,
    validate_dataset,
)
from src.evaluation.task_builder import build_evaluation_tasks
from src.ui import ROOT


def test_dataset_contract_balance_and_hash() -> None:
    path = ROOT / "data/incidents_v1.jsonl"
    records = load_dataset(path)
    summary = validate_dataset(records, load_few_shot_ids(ROOT / "prompts/examples_v1.json"))
    assert summary["scenario_pairs"] == 40
    assert summary["pending_manual_review"] == 40
    assert (
        dataset_sha256(path) == "49a2a982cda5aea08fb74dc4556d0ce9215346996a1911f14d5b96e5bc3a2312"
    )


def test_evaluation_tasks_are_stable_and_balanced() -> None:
    records = load_dataset(ROOT / "data/incidents_v1.jsonl")
    first = build_evaluation_tasks(records, DatasetSplit.EVALUATION)
    second = build_evaluation_tasks(records, DatasetSplit.EVALUATION)
    assert [item.task_id for item in first] == [item.task_id for item in second]
    assert len(first) == 180
    assert Counter(item.source_language for item in first) == {"en": 90, "zh": 90}
    assert len({item.task_id for item in first}) == 180


def test_leakage_checker_flags_copied_cross_split_source() -> None:
    records = load_dataset(ROOT / "data/incidents_v1.jsonl")
    development = next(item for item in records if item.split == DatasetSplit.DEVELOPMENT)
    evaluation = next(item for item in records if item.split == DatasetSplit.EVALUATION)
    copied = evaluation.model_copy(update={"source_en": development.source_en})
    assert leakage_overlap_flags([development, copied])


def test_chinese_utf8_round_trip_jsonl_and_csv() -> None:
    records = load_dataset(ROOT / "data/incidents_v1.jsonl")
    assert any("\u4e00" <= character <= "\u9fff" for character in records[0].source_zh)
    csv_bytes = (ROOT / "data/incidents_v1.csv").read_bytes()
    assert csv_bytes.startswith(b"\xef\xbb\xbf")
    assert records[0].source_zh.encode("utf-8") in csv_bytes
