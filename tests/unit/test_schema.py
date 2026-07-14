import pytest
from pydantic import ValidationError

from src.schemas.incident import IncidentAnalysis, SuspectedCause


def test_schema_forbids_extra_fields(valid_analysis: IncidentAnalysis) -> None:
    payload = valid_analysis.model_dump()
    payload["invented"] = True
    with pytest.raises(ValidationError):
        IncidentAnalysis.model_validate(payload)


def test_unknown_cause_cannot_hide_specific_claim() -> None:
    with pytest.raises(ValidationError):
        SuspectedCause(statement="probably a cable", certainty="unknown")


def test_round_trip_strict_schema(valid_analysis: IncidentAnalysis) -> None:
    restored = IncidentAnalysis.model_validate_json(valid_analysis.model_dump_json())
    assert restored == valid_analysis
    assert restored.schema_version == "1.0"


@pytest.mark.parametrize(
    ("field", "value"),
    [("incident_category", "unsupported"), ("severity", "catastrophic"), ("evidence", [])],
)
def test_controlled_values_and_nonempty_evidence(
    valid_analysis: IncidentAnalysis, field: str, value: object
) -> None:
    payload = valid_analysis.model_dump()
    payload[field] = value
    with pytest.raises(ValidationError):
        IncidentAnalysis.model_validate(payload)


def test_missing_required_field_is_rejected(valid_analysis: IncidentAnalysis) -> None:
    payload = valid_analysis.model_dump()
    del payload["affected_system"]
    with pytest.raises(ValidationError):
        IncidentAnalysis.model_validate(payload)
