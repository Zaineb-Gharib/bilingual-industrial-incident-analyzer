from dataclasses import replace

from src.domain.enums import OutputLanguage, PromptingStrategy
from src.domain.models import (
    AnalysisRequest,
    ProviderAuthenticationError,
    ProviderRateLimitError,
    ProviderTimeoutError,
)
from src.prompts.manager import PromptManager
from src.providers.demo import DemoProvider
from src.services.analysis_service import AnalysisService
from src.storage.repositories import in_memory_repository


def request(
    source: str, strategy: PromptingStrategy = PromptingStrategy.ZERO_SHOT
) -> AnalysisRequest:
    return AnalysisRequest(
        incident_text=source,
        output_language=OutputLanguage.EN,
        strategy=strategy,
        provider_name="demo",
        model="demo-v1",
    )


def test_transport_retry_is_bounded_and_recorded(settings, source_en, valid_json) -> None:
    waits: list[float] = []
    provider = DemoProvider([ProviderTimeoutError("temporary"), valid_json])
    service = AnalysisService(
        replace(settings, max_retries=1),
        provider,
        PromptManager(settings.prompt_dir),
        in_memory_repository(),
        sleeper=waits.append,
        jitter=lambda _a, _b: 0,
    )
    outcome = service.analyze(request(source_en))
    assert outcome.final_accepted_valid
    assert outcome.retry_count == 1
    assert provider.call_count == 2
    assert waits == [1]


def test_json_repair_is_single_and_attributed(settings, source_en, valid_json) -> None:
    provider = DemoProvider(["not-json", valid_json])
    service = AnalysisService(
        settings,
        provider,
        PromptManager(settings.prompt_dir),
        in_memory_repository(),
    )
    outcome = service.analyze(request(source_en))
    assert outcome.final_accepted_valid
    assert outcome.repair_assisted_valid
    assert outcome.first_pass_json_valid is False
    assert outcome.semantic_call_count == 2


def test_self_refinement_makes_exactly_two_semantic_calls(settings, source_en, valid_json) -> None:
    provider = DemoProvider([valid_json, valid_json])
    service = AnalysisService(
        settings,
        provider,
        PromptManager(settings.prompt_dir),
        in_memory_repository(),
    )
    outcome = service.analyze(request(source_en, PromptingStrategy.SELF_REFINEMENT))
    assert outcome.final_accepted_valid
    assert outcome.semantic_call_count == 2
    assert provider.call_count == 2


def test_refined_response_defines_self_refinement_first_pass(
    settings, source_en, valid_json
) -> None:
    provider = DemoProvider(["invalid initial draft", valid_json])
    service = AnalysisService(
        settings,
        provider,
        PromptManager(settings.prompt_dir),
        in_memory_repository(),
    )
    outcome = service.analyze(request(source_en, PromptingStrategy.SELF_REFINEMENT))
    assert outcome.initial_validation is not None
    assert outcome.initial_validation.json_valid is False
    assert outcome.first_pass_json_valid is True
    assert outcome.repair_assisted_valid is False


def test_invalid_input_never_calls_provider(settings) -> None:
    provider = DemoProvider()
    service = AnalysisService(
        settings,
        provider,
        PromptManager(settings.prompt_dir),
        in_memory_repository(),
    )
    outcome = service.analyze(request("short"))
    assert outcome.final_accepted_valid is False
    assert provider.call_count == 0
    assert outcome.failure_type.value == "input"


def test_overlong_input_never_calls_provider(settings) -> None:
    provider = DemoProvider()
    service = AnalysisService(
        settings,
        provider,
        PromptManager(settings.prompt_dir),
        in_memory_repository(),
    )
    outcome = service.analyze(request("x" * 4001))
    assert outcome.failure_type.value == "input"
    assert provider.call_count == 0


def test_authentication_failure_is_not_retried(settings, source_en) -> None:
    provider = DemoProvider([ProviderAuthenticationError("invalid credential")])
    service = AnalysisService(
        settings,
        provider,
        PromptManager(settings.prompt_dir),
        in_memory_repository(),
    )
    outcome = service.analyze(request(source_en))
    assert outcome.failure_type.value == "authentication"
    assert provider.call_count == 1


def test_rate_limit_exhaustion_is_bounded(settings, source_en) -> None:
    provider = DemoProvider([ProviderRateLimitError("slow"), ProviderRateLimitError("still slow")])
    service = AnalysisService(
        replace(settings, max_retries=1),
        provider,
        PromptManager(settings.prompt_dir),
        in_memory_repository(),
        sleeper=lambda _value: None,
        jitter=lambda _a, _b: 0,
    )
    outcome = service.analyze(request(source_en))
    assert outcome.failure_type.value == "rate_limit"
    assert outcome.retry_count == 1
    assert provider.call_count == 2


def test_failed_refinement_is_not_replaced_by_initial(
    settings, source_en, valid_json, valid_analysis
) -> None:
    payload = valid_analysis.model_dump()
    payload["evidence"][0]["quote"] = "invented evidence"
    invalid_refined = valid_analysis.model_validate(payload).model_dump_json()
    provider = DemoProvider([valid_json, invalid_refined])
    service = AnalysisService(
        settings,
        provider,
        PromptManager(settings.prompt_dir),
        in_memory_repository(),
    )
    outcome = service.analyze(request(source_en, PromptingStrategy.SELF_REFINEMENT))
    assert outcome.result is None
    assert outcome.final_accepted_valid is False
    assert outcome.failure_type.value == "grounding"
    assert outcome.initial_raw_response == valid_json


def test_user_input_not_stored_by_default(settings, source_en) -> None:
    repository = in_memory_repository()
    service = AnalysisService(
        settings,
        DemoProvider(),
        PromptManager(settings.prompt_dir),
        repository,
    )
    service.analyze(request(source_en))
    assert repository.list_analyses()[0]["raw_input"] is None
