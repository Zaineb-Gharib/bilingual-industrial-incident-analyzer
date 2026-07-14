from src.domain.enums import InputLanguage, OutputLanguage
from src.validation.language import detect_input_language, output_language_looks_wrong


def test_detects_english_chinese_and_mixed() -> None:
    assert detect_input_language("The server stopped responding.") == InputLanguage.EN
    assert detect_input_language("服务器停止响应。") == InputLanguage.ZH
    assert detect_input_language("服务器 server stopped 响应") == InputLanguage.MIXED


def test_output_language_hint_flags_obvious_mismatch() -> None:
    assert output_language_looks_wrong("这是一段完全中文的分析内容。", OutputLanguage.EN)
