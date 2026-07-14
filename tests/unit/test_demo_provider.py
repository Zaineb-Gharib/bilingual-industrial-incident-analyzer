from src.domain.enums import OutputLanguage, PromptingStrategy
from src.domain.models import LLMRequest
from src.prompts.manager import PromptManager
from src.providers.demo import DemoProvider
from src.schemas.incident import IncidentAnalysis


def test_demo_provider_is_explicitly_labeled(settings) -> None:
    prompt = PromptManager(settings.prompt_dir).render(
        PromptingStrategy.ZERO_SHOT,
        "The server stopped responding.",
        OutputLanguage.EN,
    )
    response = DemoProvider().complete(
        LLMRequest(
            messages=prompt.messages,
            model="demo-v1",
            metadata={
                "incident_text": "The server stopped responding.",
                "input_language": "en",
                "output_language": "en",
            },
        )
    )
    parsed = IncidentAnalysis.model_validate_json(response.text)
    assert response.provider == "demo"
    assert "not a real LLM result" in parsed.warnings[0]


def test_demo_provider_preserves_exact_evidence(settings) -> None:
    source = "The network gateway is unavailable. Engineers observed packet loss."
    prompt = PromptManager(settings.prompt_dir).render(
        PromptingStrategy.ZERO_SHOT, source, OutputLanguage.EN
    )
    response = DemoProvider().complete(
        LLMRequest(
            messages=prompt.messages,
            model="demo-v1",
            metadata={"incident_text": source, "input_language": "en", "output_language": "en"},
        )
    )
    evidence = IncidentAnalysis.model_validate_json(response.text).evidence[0].quote
    assert evidence in source
