from src.observability.logging import redact


def test_redaction_hides_key_but_preserves_task_id() -> None:
    fake_key = "sk-" + "abcdefghijklmnopqrstuvwxyz123"
    assert redact(f"token {fake_key}") == "token [REDACTED]"
    task_id = "task-72661ebc76a18256c4fe"
    assert redact(task_id) == task_id


def test_redaction_hides_authorization_value() -> None:
    assert "private-value" not in redact("Authorization: Bearer private-value")
