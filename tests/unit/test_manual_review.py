import csv

from src.evaluation.manual_review import REVIEW_COLUMNS, export_blinded_review_template


def test_manual_review_export_is_bom_utf8_and_unscored(tmp_path) -> None:
    path = tmp_path / "review.csv"
    rows = [
        {
            "analysis_id": "analysis-1",
            "scenario_id": "EVAL-SRV-001",
            "raw_input": "服务器停止响应。",
            "parsed_response": '{"title":"事件"}',
        }
    ]
    export_blinded_review_template(rows, {"EVAL-SRV-001": {"category": "server_failure"}}, path)
    assert path.read_bytes().startswith(b"\xef\xbb\xbf")
    with path.open(encoding="utf-8-sig", newline="") as handle:
        exported = list(csv.DictReader(handle))
    assert list(exported[0]) == REVIEW_COLUMNS
    assert exported[0]["source_report"] == "服务器停止响应。"
    assert exported[0]["reviewer_id"] == ""
    assert exported[0]["dangerous_advice"] == ""
