"""Safe loading and rendering of immutable prompt templates."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from src.domain.enums import OutputLanguage, PromptingStrategy
from src.domain.models import PromptMessage, PromptPackage, ValidationIssue
from src.schemas.incident import IncidentAnalysis


class PromptManager:
    """Render trusted system text separately from untrusted incident data."""

    PROMPT_VERSION = "1.0"

    def __init__(self, prompt_dir: Path):
        self.prompt_dir = prompt_dir
        self.shared = self._read("shared_system_v1.txt")
        self.output_modules = {
            OutputLanguage.EN: self._read("output_en_v1.txt"),
            OutputLanguage.ZH: self._read("output_zh_v1.txt"),
        }
        self.schema_json = json.dumps(
            IncidentAnalysis.model_json_schema(),
            ensure_ascii=False,
            separators=(",", ":"),
        )

    def _read(self, filename: str) -> str:
        return (self.prompt_dir / filename).read_text(encoding="utf-8")

    @staticmethod
    def _replace(template: str, values: dict[str, str]) -> str:
        rendered = template
        for key, value in values.items():
            rendered = rendered.replace("{{" + key + "}}", value)
        return rendered

    def _examples(self) -> tuple[str, list[str]]:
        path = self.prompt_dir / "examples_v1.json"
        if not path.exists():
            return "[]", []
        records: list[dict[str, Any]] = json.loads(path.read_text(encoding="utf-8"))
        return json.dumps(records, ensure_ascii=False, indent=2), [
            str(record["scenario_id"]) for record in records
        ]

    def render(
        self,
        strategy: PromptingStrategy,
        incident_text: str,
        output_language: OutputLanguage,
    ) -> PromptPackage:
        language_name = "English" if output_language == OutputLanguage.EN else "Simplified Chinese"
        template_map = {
            PromptingStrategy.ZERO_SHOT: "zero_shot_v1.txt",
            PromptingStrategy.FEW_SHOT: "few_shot_v1.txt",
            PromptingStrategy.SELF_REFINEMENT: "self_initial_v1.txt",
        }
        filename = template_map[strategy]
        examples_json, example_ids = self._examples()
        user = self._replace(
            self._read(filename),
            {
                "OUTPUT_LANGUAGE_NAME": language_name,
                "SCHEMA_JSON": self.schema_json,
                "INCIDENT_TEXT": incident_text,
                "FEW_SHOT_EXAMPLES": examples_json,
            },
        )
        system = self.shared + "\n" + self.output_modules[output_language]
        return self._package(
            system, user, filename, example_ids if strategy == PromptingStrategy.FEW_SHOT else []
        )

    def render_self_refinement(
        self,
        incident_text: str,
        output_language: OutputLanguage,
        initial_response: str,
        issues: list[ValidationIssue],
    ) -> PromptPackage:
        language_name = "English" if output_language == OutputLanguage.EN else "Simplified Chinese"
        warnings = json.dumps(
            [issue.model_dump(mode="json") for issue in issues],
            ensure_ascii=False,
        )
        user = self._replace(
            self._read("self_refine_v1.txt"),
            {
                "OUTPUT_LANGUAGE_NAME": language_name,
                "SCHEMA_JSON": self.schema_json,
                "INCIDENT_TEXT": incident_text,
                "INITIAL_RESPONSE": initial_response,
                "VALIDATION_WARNINGS": warnings,
            },
        )
        system = self.shared + "\n" + self.output_modules[output_language]
        return self._package(system, user, "self_refine_v1.txt", [])

    def render_json_repair(
        self,
        incident_text: str,
        output_language: OutputLanguage,
        malformed_response: str,
        issues: list[ValidationIssue],
    ) -> PromptPackage:
        language_name = "English" if output_language == OutputLanguage.EN else "Simplified Chinese"
        warnings = json.dumps(
            [issue.model_dump(mode="json") for issue in issues],
            ensure_ascii=False,
        )
        user = self._replace(
            self._read("json_repair_v1.txt"),
            {
                "OUTPUT_LANGUAGE_NAME": language_name,
                "SCHEMA_JSON": self.schema_json,
                "INCIDENT_TEXT": incident_text,
                "INITIAL_RESPONSE": malformed_response,
                "VALIDATION_WARNINGS": warnings,
            },
        )
        system = self.shared + "\n" + self.output_modules[output_language]
        return self._package(system, user, "json_repair_v1.txt", [])

    def _package(
        self,
        system: str,
        user: str,
        template_name: str,
        example_ids: list[str],
    ) -> PromptPackage:
        digest = hashlib.sha256((system + "\n" + user).encode("utf-8")).hexdigest()
        return PromptPackage(
            messages=[
                PromptMessage(role="system", content=system),
                PromptMessage(role="user", content=user),
            ],
            prompt_version=self.PROMPT_VERSION,
            template_name=template_name,
            prompt_hash=digest,
            example_ids=example_ids,
        )
