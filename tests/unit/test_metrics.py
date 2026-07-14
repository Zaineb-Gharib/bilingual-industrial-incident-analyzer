from src.domain.enums import OutputLanguage, PromptingStrategy
from src.domain.models import AnalysisRequest
from src.evaluation.dataset_loader import load_dataset
from src.evaluation.metrics import (
    aggregate_metrics,
    precision_recall_f1,
    required_field_completion,
    safe_rate,
)
from src.services.factory import build_analysis_service
from src.ui import ROOT


def test_safe_rate_has_explicit_zero_denominator() -> None:
    assert safe_rate(1, 0) is None
    assert safe_rate(2, 4) == 0.5


def test_precision_recall_f1_formula() -> None:
    precision, recall, f1 = precision_recall_f1(2, 1, 2)
    assert precision == 2 / 3
    assert recall == 1 / 2
    assert round(f1, 6) == 0.571429


def test_required_field_completion_empty_is_zero() -> None:
    assert required_field_completion({}) == 0.0


def test_aggregate_metric_denominators_from_one_real_demo_row(settings) -> None:
    record = load_dataset(ROOT / "data/incidents_v1.jsonl")[0]
    service = build_analysis_service(settings, "demo")
    outcome = service.analyze(
        AnalysisRequest(
            incident_text=record.source_en,
            output_language=OutputLanguage.EN,
            strategy=PromptingStrategy.ZERO_SHOT,
            scenario_id=record.scenario_id,
            provider_name="demo",
            model="demo-v1",
        )
    )
    rows = service.repository.list_analyses()
    metrics = {item.metric_name: item for item in aggregate_metrics("run", rows, [record])}
    assert outcome.final_accepted_valid
    assert metrics["first_pass_json_validity_rate"].numerator == 1
    assert metrics["first_pass_json_validity_rate"].denominator == 1
    assert metrics["evidence_grounding_rate"].value == 1.0
