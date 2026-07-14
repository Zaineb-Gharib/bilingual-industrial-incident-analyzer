import json

from src.domain.enums import OutputLanguage, PromptingStrategy
from src.domain.models import AnalysisRequest
from src.prompts.manager import PromptManager
from src.providers.demo import DemoProvider
from src.services.analysis_service import AnalysisService


def test_download_payload_is_utf8_not_ascii_escaped(settings) -> None:
    source = "数据库不可用，连接在09:14停止。"
    service = AnalysisService(settings, DemoProvider(), PromptManager(settings.prompt_dir))
    outcome = service.analyze(
        AnalysisRequest(
            incident_text=source,
            output_language=OutputLanguage.ZH,
            strategy=PromptingStrategy.ZERO_SHOT,
        )
    )
    encoded = json.dumps(outcome.model_dump(mode="json"), ensure_ascii=False, indent=2).encode(
        "utf-8"
    )
    decoded = encoded.decode("utf-8")
    assert "数据" in decoded
    assert "\\u6570\\u636e" not in decoded
