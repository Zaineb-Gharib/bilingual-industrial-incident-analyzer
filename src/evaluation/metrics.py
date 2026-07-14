"""Pure metric formulas and aggregate records with explicit denominators."""

from __future__ import annotations

import json
import math
import statistics
import unicodedata
from collections import defaultdict
from collections.abc import Iterable
from typing import Any

from src.schemas.dataset import DatasetScenarioPair
from src.schemas.run_records import MetricRecord

REQUIRED_FIELDS = {
    "schema_version",
    "prompt_version",
    "input_language",
    "output_language",
    "incident_title",
    "incident_category",
    "severity",
    "affected_system",
    "main_symptoms",
    "suspected_cause",
    "recommended_immediate_actions",
    "recommended_long_term_actions",
    "responsible_team",
    "evidence",
    "uncertainty_explanation",
    "confidence",
    "warnings",
}


def safe_rate(numerator: float, denominator: float) -> float | None:
    return numerator / denominator if denominator else None


def precision_recall_f1(
    true_positive: int,
    false_positive: int,
    false_negative: int,
) -> tuple[float, float, float]:
    precision = safe_rate(true_positive, true_positive + false_positive) or 0.0
    recall = safe_rate(true_positive, true_positive + false_negative) or 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return precision, recall, f1


def required_field_completion(value: dict[str, Any] | None) -> float:
    if not value:
        return 0.0
    complete = 0
    for field_name in REQUIRED_FIELDS:
        if field_name not in value:
            continue
        field_value = value[field_name]
        if field_value is None:
            continue
        if isinstance(field_value, str) and not field_value.strip():
            continue
        if isinstance(field_value, list) and field_name != "warnings" and not field_value:
            continue
        complete += 1
    return complete / len(REQUIRED_FIELDS)


def aggregate_metrics(
    run_id: str,
    rows: list[dict[str, Any]],
    gold_records: Iterable[DatasetScenarioPair],
    group: dict[str, str] | None = None,
) -> list[MetricRecord]:
    gold = {record.scenario_id: record for record in gold_records}
    attempted = len(rows)
    parsed_rows: list[tuple[dict[str, Any], dict[str, Any]]] = []
    category_correct = 0
    severity_correct = 0
    team_correct = 0
    completion_sum = 0.0
    evidence_returned = 0
    evidence_grounded = 0
    outputs_with_grounded = 0
    symptom_tp = symptom_fp = symptom_fn = 0
    for row in rows:
        value = _parsed(row)
        completion_sum += required_field_completion(value)
        if not value:
            continue
        parsed_rows.append((row, value))
        record = gold.get(str(row.get("scenario_id")))
        if record:
            category_correct += value.get("incident_category") == record.category.value
            severity_correct += value.get("severity") == record.severity.value
            team_correct += value.get("responsible_team") == record.responsible_team.value
            tp, fp, fn = _symptom_counts(value, record)
            symptom_tp += tp
            symptom_fp += fp
            symptom_fn += fn
        evidence = value.get("evidence") or []
        returned = len(evidence)
        issues = _issues(row)
        invalid_quotes = sum(issue.get("code") == "EVIDENCE_NOT_IN_SOURCE" for issue in issues)
        grounded = max(0, returned - invalid_quotes)
        evidence_returned += returned
        evidence_grounded += grounded
        outputs_with_grounded += grounded > 0
    parsed_count = len(parsed_rows)
    first_pass = sum(bool(row.get("first_pass_json_valid")) for row in rows)
    final_valid = sum(bool(row.get("final_accepted_valid")) for row in rows)
    repair_used = sum(bool(row.get("repair_assisted_valid")) for row in rows)
    failures = attempted - final_valid
    latencies = [float(row.get("latency_ms") or 0.0) for row in rows]
    precision, recall, f1 = precision_recall_f1(symptom_tp, symptom_fp, symptom_fn)
    hallucinated_quotes = evidence_returned - evidence_grounded
    group = group or {}
    specs = [
        ("category_accuracy_conditional", category_correct, parsed_count),
        ("category_success_end_to_end", category_correct, attempted),
        ("severity_accuracy_conditional", severity_correct, parsed_count),
        ("severity_success_end_to_end", severity_correct, attempted),
        ("responsible_team_exact_match", team_correct, parsed_count),
        ("first_pass_json_validity_rate", first_pass, attempted),
        ("repair_assisted_validity_rate", final_valid, attempted),
        ("outputs_requiring_json_repair", repair_used, attempted),
        ("required_field_completion_rate", completion_sum, attempted),
        ("evidence_grounding_rate", evidence_grounded, evidence_returned),
        ("evidence_quote_hallucination_rate", hallucinated_quotes, evidence_returned),
        ("outputs_with_grounded_evidence_rate", outputs_with_grounded, attempted),
        ("failure_rate", failures, attempted),
        ("symptom_precision", symptom_tp, symptom_tp + symptom_fp),
        ("symptom_recall", symptom_tp, symptom_tp + symptom_fn),
        (
            "symptom_f1",
            f1 * (symptom_tp + symptom_fp + symptom_fn),
            symptom_tp + symptom_fp + symptom_fn,
        ),
        ("average_latency_ms", sum(latencies), len(latencies)),
    ]
    metrics = [
        MetricRecord(
            run_id=run_id,
            metric_name=name,
            numerator=float(numerator),
            denominator=float(denominator),
            value=safe_rate(float(numerator), float(denominator)),
            group=group,
        )
        for name, numerator, denominator in specs
    ]
    metrics.extend(
        [
            _latency_metric(run_id, "median_latency_ms", latencies, statistics.median, group),
            _latency_metric(run_id, "p95_latency_ms", latencies, _percentile_95, group),
        ]
    )
    consistency = bilingual_consistency(rows)
    metrics.append(
        MetricRecord(
            run_id=run_id,
            metric_name="bilingual_consistency_score",
            numerator=sum(consistency),
            denominator=len(consistency),
            value=safe_rate(sum(consistency), len(consistency)),
            exclusions=max(0, _potential_pair_count(rows) - len(consistency)),
            group=group,
        )
    )
    return metrics


def aggregate_all_groups(
    run_id: str,
    rows: list[dict[str, Any]],
    gold_records: Iterable[DatasetScenarioPair],
) -> list[MetricRecord]:
    gold_list = list(gold_records)
    metrics = aggregate_metrics(run_id, rows, gold_list)
    group_fields = ["strategy", "input_language", "output_language"]
    for field in group_fields:
        values = sorted({str(row.get(field)) for row in rows if row.get(field) is not None})
        for value in values:
            subset = [row for row in rows if str(row.get(field)) == value]
            metrics.extend(aggregate_metrics(run_id, subset, gold_list, {field: value}))
    paths = sorted(
        {
            f"{row.get('input_language')}->{row.get('output_language')}"
            for row in rows
            if row.get("input_language") and row.get("output_language")
        }
    )
    for path in paths:
        source, target = path.split("->")
        subset = [
            row
            for row in rows
            if row.get("input_language") == source and row.get("output_language") == target
        ]
        metrics.extend(aggregate_metrics(run_id, subset, gold_list, {"language_path": path}))
    gold_by_id = {record.scenario_id: record for record in gold_list}
    categories = sorted({record.category.value for record in gold_list})
    for category in categories:
        subset = [
            row
            for row in rows
            if row.get("scenario_id") in gold_by_id
            and gold_by_id[str(row["scenario_id"])].category.value == category
        ]
        if subset:
            metrics.extend(aggregate_metrics(run_id, subset, gold_list, {"category": category}))
    return metrics


def bilingual_consistency(rows: list[dict[str, Any]]) -> list[float]:
    groups: dict[tuple[str, str, str], dict[str, dict[str, Any]]] = defaultdict(dict)
    for row in rows:
        value = _parsed(row)
        if not value or not row.get("final_accepted_valid"):
            continue
        key = (
            str(row.get("scenario_id")),
            str(row.get("strategy")),
            str(row.get("output_language")),
        )
        groups[key][str(row.get("input_language"))] = value
    scores = []
    for pair in groups.values():
        if not {"en", "zh"} <= pair.keys():
            continue
        left, right = pair["en"], pair["zh"]
        category = float(left.get("incident_category") == right.get("incident_category"))
        severity = float(left.get("severity") == right.get("severity"))
        team = float(left.get("responsible_team") == right.get("responsible_team"))
        system = float(
            _norm(left.get("affected_system", "")) == _norm(right.get("affected_system", ""))
        )
        symptom = _text_list_f1(left.get("main_symptoms", []), right.get("main_symptoms", []))
        scores.append(
            0.30 * category + 0.20 * severity + 0.15 * team + 0.15 * system + 0.20 * symptom
        )
    return scores


def _symptom_counts(
    predicted: dict[str, Any],
    gold: DatasetScenarioPair,
) -> tuple[int, int, int]:
    output_language = predicted.get("output_language", "en")
    expected = {
        _norm(concept.en if output_language == "en" else concept.zh)
        for concept in gold.symptom_concepts
    }
    found: set[str] = set()
    extra = 0
    for symptom in predicted.get("main_symptoms", []):
        normalized = _norm(str(symptom))
        matches = {
            concept for concept in expected if concept in normalized or normalized in concept
        }
        if matches:
            found.update(matches)
        else:
            extra += 1
    return len(found), extra, len(expected - found)


def _text_list_f1(left: list[str], right: list[str]) -> float:
    left_set = {_norm(item) for item in left}
    right_set = {_norm(item) for item in right}
    tp = len(left_set & right_set)
    _, _, f1 = precision_recall_f1(tp, len(left_set - right_set), len(right_set - left_set))
    return f1


def _norm(value: str) -> str:
    return " ".join(unicodedata.normalize("NFC", value).lower().split())


def _parsed(row: dict[str, Any]) -> dict[str, Any] | None:
    value = row.get("parsed_response")
    if isinstance(value, dict):
        return value
    if isinstance(value, str) and value:
        try:
            loaded = json.loads(value)
            return loaded if isinstance(loaded, dict) else None
        except json.JSONDecodeError:
            return None
    return None


def _issues(row: dict[str, Any]) -> list[dict[str, Any]]:
    value = row.get("validation_issues")
    if isinstance(value, list):
        return value
    if isinstance(value, str) and value:
        try:
            loaded = json.loads(value)
            return loaded if isinstance(loaded, list) else []
        except json.JSONDecodeError:
            return []
    return []


def _latency_metric(
    run_id: str,
    name: str,
    values: list[float],
    function: Any,
    group: dict[str, str],
) -> MetricRecord:
    value = float(function(values)) if values else None
    return MetricRecord(
        run_id=run_id,
        metric_name=name,
        numerator=value,
        denominator=len(values),
        value=value,
        group=group,
    )


def _percentile_95(values: list[float]) -> float:
    ordered = sorted(values)
    if not ordered:
        return math.nan
    index = max(0, math.ceil(0.95 * len(ordered)) - 1)
    return ordered[index]


def _potential_pair_count(rows: list[dict[str, Any]]) -> int:
    return len(
        {(row.get("scenario_id"), row.get("strategy"), row.get("output_language")) for row in rows}
    )
