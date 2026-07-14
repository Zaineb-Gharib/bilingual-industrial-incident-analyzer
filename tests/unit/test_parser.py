from src.validation.parser import parse_json_object


def test_direct_json_object_is_accepted() -> None:
    result = parse_json_object('{"a": 1}')
    assert result.value == {"a": 1}
    assert result.normalization_applied is False


def test_one_outer_fence_is_normalized() -> None:
    result = parse_json_object('```json\n{"a": 1}\n```')
    assert result.value == {"a": 1}
    assert result.normalization_applied is True


def test_prose_wrapped_json_is_rejected() -> None:
    result = parse_json_object('Here is the answer: {"a": 1}')
    assert result.error


def test_json_array_is_rejected() -> None:
    result = parse_json_object("[1, 2]")
    assert result.error


def test_multiple_json_objects_are_rejected() -> None:
    result = parse_json_object('{"a": 1}\n{"b": 2}')
    assert result.error
