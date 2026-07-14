"""Run all three strategies under the same configured conditions."""

from __future__ import annotations

from src.domain.enums import PromptingStrategy
from src.domain.models import AnalysisOutcome, AnalysisRequest
from src.services.analysis_service import AnalysisService


class ComparisonService:
    def __init__(self, analysis_service: AnalysisService):
        self.analysis_service = analysis_service

    def compare(self, base_request: AnalysisRequest) -> dict[PromptingStrategy, AnalysisOutcome]:
        outcomes: dict[PromptingStrategy, AnalysisOutcome] = {}
        for strategy in PromptingStrategy:
            request = base_request.model_copy(update={"strategy": strategy})
            outcomes[strategy] = self.analysis_service.analyze(request)
        return outcomes
