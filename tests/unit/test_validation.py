from src.domain.enums import OutputLanguage, ValidationStatus
from src.schemas.incident import IncidentAnalysis
from src.validation.pipeline import validate_response


def test_valid_grounded_response_is_accepted(source_en: str, valid_json: str) -> None:
    result = validate_response(valid_json, source_en, OutputLanguage.EN)
    assert result.accepted
    assert result.grounded_evidence_items == 1


def test_hallucinated_quote_is_terminal(source_en: str, valid_analysis: IncidentAnalysis) -> None:
    payload = valid_analysis.model_dump()
    payload["evidence"][0]["quote"] = "This sentence was never in the report."
    result = validate_response(
        IncidentAnalysis.model_validate(payload).model_dump_json(), source_en, OutputLanguage.EN
    )
    assert result.status == ValidationStatus.INVALID_TERMINAL
    assert "EVIDENCE_NOT_IN_SOURCE" in {issue.code for issue in result.issues}


def test_declared_output_language_mismatch_is_terminal(source_en: str, valid_json: str) -> None:
    result = validate_response(valid_json, source_en, OutputLanguage.ZH)
    assert result.status == ValidationStatus.INVALID_TERMINAL
    assert "OUTPUT_LANGUAGE_MISMATCH" in {issue.code for issue in result.issues}


def test_bad_json_is_repairable(source_en: str) -> None:
    result = validate_response("not-json", source_en, OutputLanguage.EN)
    assert result.status == ValidationStatus.INVALID_REPAIRABLE
    assert result.json_valid is False
