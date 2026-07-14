"""Deterministic offline provider for tests and clearly labeled demonstrations."""

from __future__ import annotations

import re
import time
from collections.abc import Iterable

from src.domain.enums import (
    CauseCertainty,
    IncidentCategory,
    InputLanguage,
    OutputLanguage,
    ResponsibleTeam,
    Severity,
)
from src.domain.models import LLMRequest, LLMResponse
from src.schemas.incident import (
    Confidence,
    EvidenceItem,
    IncidentAnalysis,
    RecommendedAction,
    SuspectedCause,
)
from src.validation.language import detect_input_language


class DemoProvider:
    """A rule-based provider. It is not an LLM and its values are not research results."""

    name = "demo"

    def __init__(self, scripted: Iterable[str | Exception] | None = None):
        self._scripted = list(scripted or [])
        self.requests: list[LLMRequest] = []

    @property
    def call_count(self) -> int:
        return len(self.requests)

    def complete(self, request: LLMRequest) -> LLMResponse:
        started = time.perf_counter()
        self.requests.append(request)
        if self._scripted:
            value = self._scripted.pop(0)
            if isinstance(value, Exception):
                raise value
            text = value
        else:
            text = self._analyze(request)
        return LLMResponse(
            text=text,
            provider=self.name,
            requested_model=request.model,
            resolved_model="demo-rule-engine-v1",
            finish_reason="stop",
            provider_request_id=f"demo-{self.call_count:04d}",
            latency_ms=(time.perf_counter() - started) * 1000,
        )

    def _analyze(self, request: LLMRequest) -> str:
        report = str(request.metadata.get("incident_text", "")).strip()
        output_language = OutputLanguage(str(request.metadata.get("output_language", "en")))
        detected = InputLanguage(
            str(request.metadata.get("input_language", detect_input_language(report)))
        )
        category = self._category(report)
        severity = self._severity(report)
        team = self._team(category)
        title, system, symptom, immediate, long_term, unknown, demo_warning = self._phrases(
            category, output_language
        )
        cause_statement, certainty = self._cause(report, output_language)
        quote = self._evidence(report)
        analysis = IncidentAnalysis(
            input_language=detected,
            output_language=output_language,
            incident_title=title,
            incident_category=category,
            severity=severity,
            affected_system=system,
            main_symptoms=[symptom],
            suspected_cause=SuspectedCause(
                statement=cause_statement or unknown,
                certainty=certainty,
            ),
            recommended_immediate_actions=[
                RecommendedAction(
                    action=immediate,
                    rationale=(
                        "The report describes an incident requiring authorized review."
                        if output_language == OutputLanguage.EN
                        else "报告描述了需要授权人员审查的事件。"
                    ),
                    requires_authorization=True,
                )
            ],
            recommended_long_term_actions=[long_term],
            responsible_team=team,
            evidence=[
                EvidenceItem(
                    quote=quote,
                    supports_fields=["affected_system", "main_symptoms", "severity"],
                )
            ],
            uncertainty_explanation=(
                "The deterministic demo uses only visible keywords and cannot confirm root cause."
                if output_language == OutputLanguage.EN
                else "确定性演示仅使用可见关键词，无法确认根本原因。"
            ),
            confidence=Confidence(
                level="low",
                explanation=(
                    "Demo confidence is intentionally low because this is not an LLM result."
                    if output_language == OutputLanguage.EN
                    else "由于这不是LLM结果，演示置信度有意设为低。"
                ),
            ),
            warnings=[demo_warning],
        )
        return analysis.model_dump_json(indent=2)

    @staticmethod
    def _category(report: str) -> IncidentCategory:
        text = report.lower()
        rules = [
            (
                IncidentCategory.SECURITY_ALERT,
                ["security", "suspicious", "malware", "unauthorized", "安全", "可疑", "恶意"],
            ),
            (
                IncidentCategory.DEPLOYMENT_FAILURE,
                ["deployment", "release", "rollout", "migration step", "部署", "发布", "上线"],
            ),
            (IncidentCategory.API_OUTAGE, [" api ", "endpoint", "http 5", "接口", "api不可用"]),
            (
                IncidentCategory.DATABASE_FAILURE,
                ["database", " db ", "replica", "数据库", "连接错误"],
            ),
            (
                IncidentCategory.STORAGE_PROBLEM,
                ["storage", "disk space", "volume", "capacity", "存储", "磁盘空间", "容量"],
            ),
            (
                IncidentCategory.DATA_PIPELINE_FAILURE,
                ["pipeline", "etl", "batch job", "ingestion", "数据流水线", "数据管道", "作业"],
            ),
            (
                IncidentCategory.NETWORK_INTERRUPTION,
                [
                    "network",
                    "switch",
                    "gateway",
                    "connection",
                    "网络",
                    "交换机",
                    "网关",
                    "连接中断",
                ],
            ),
            (
                IncidentCategory.MANUFACTURING_EQUIPMENT_ISSUE,
                [
                    "press",
                    "conveyor",
                    "production line",
                    "vibration",
                    "压力机",
                    "输送机",
                    "生产线",
                    "振动",
                ],
            ),
            (
                IncidentCategory.HARDWARE_MALFUNCTION,
                [
                    "hardware",
                    "power supply",
                    "controller",
                    "sensor fault",
                    "硬件",
                    "电源",
                    "控制器",
                    "传感器故障",
                ],
            ),
            (IncidentCategory.SERVER_FAILURE, ["server", "host", "node", "服务器", "主机", "节点"]),
        ]
        padded = f" {text} "
        for category, keywords in rules:
            if any(keyword in padded for keyword in keywords):
                return category
        return IncidentCategory.OTHER

    @staticmethod
    def _severity(report: str) -> Severity:
        text = report.lower()
        if any(
            word in text
            for word in ["fire", "injury", "data loss in progress", "火灾", "受伤", "正在丢失数据"]
        ):
            return Severity.CRITICAL
        if any(
            word in text
            for word in [
                "unavailable",
                "stopped",
                "critical",
                "exceeded",
                "不可用",
                "停止",
                "严重",
                "超过",
            ]
        ):
            return Severity.HIGH
        if any(
            word in text
            for word in [
                "recovered",
                "degraded",
                "intermittent",
                "warning",
                "恢复",
                "降级",
                "间歇",
                "警告",
            ]
        ):
            return Severity.MEDIUM
        return Severity.UNKNOWN

    @staticmethod
    def _team(category: IncidentCategory) -> ResponsibleTeam:
        mapping = {
            IncidentCategory.SERVER_FAILURE: ResponsibleTeam.PLATFORM,
            IncidentCategory.NETWORK_INTERRUPTION: ResponsibleTeam.NETWORK,
            IncidentCategory.DATABASE_FAILURE: ResponsibleTeam.DATABASE,
            IncidentCategory.DEPLOYMENT_FAILURE: ResponsibleTeam.RELEASE,
            IncidentCategory.API_OUTAGE: ResponsibleTeam.APPLICATION,
            IncidentCategory.STORAGE_PROBLEM: ResponsibleTeam.STORAGE,
            IncidentCategory.DATA_PIPELINE_FAILURE: ResponsibleTeam.DATA,
            IncidentCategory.HARDWARE_MALFUNCTION: ResponsibleTeam.HARDWARE,
            IncidentCategory.MANUFACTURING_EQUIPMENT_ISSUE: ResponsibleTeam.MAINTENANCE,
            IncidentCategory.SECURITY_ALERT: ResponsibleTeam.SECURITY,
        }
        return mapping.get(category, ResponsibleTeam.INCIDENT)

    @staticmethod
    def _cause(report: str, output: OutputLanguage) -> tuple[str | None, CauseCertainty]:
        candidates = [
            ("migration checksum mismatch", "迁移校验和不匹配"),
            ("switch reboot", "交换机重启"),
            ("expired certificate", "证书过期"),
            ("disk failure", "磁盘故障"),
            ("power interruption", "电源中断"),
        ]
        lowered = report.lower()
        for english, chinese in candidates:
            if english in lowered or chinese in report:
                return (
                    english if output == OutputLanguage.EN else chinese
                ), CauseCertainty.EXPLICIT
        return None, CauseCertainty.UNKNOWN

    @staticmethod
    def _evidence(report: str) -> str:
        compact = report.strip()
        # Latin sentence endings require following whitespace, so a decimal such
        # as "2.8" is not cut into the meaningless evidence quote "2.". Chinese
        # sentence punctuation does not normally need a following space.
        pieces = re.split(r"(?<=[.!?])\s+|(?<=[。！？])", compact, maxsplit=1)
        quote = pieces[0] if pieces and pieces[0] else compact
        return quote[:1200]

    @staticmethod
    def _phrases(
        category: IncidentCategory,
        output: OutputLanguage,
    ) -> tuple[str, str, str, str, str, str, str]:
        labels_en = {
            IncidentCategory.SERVER_FAILURE: (
                "Server response failure",
                "reported server",
                "The server is not responding normally.",
            ),
            IncidentCategory.NETWORK_INTERRUPTION: (
                "Network connection interruption",
                "reported network connection",
                "Network connectivity was interrupted.",
            ),
            IncidentCategory.DATABASE_FAILURE: (
                "Database availability incident",
                "reported database",
                "Database access or availability failed.",
            ),
            IncidentCategory.DEPLOYMENT_FAILURE: (
                "Deployment failure",
                "reported deployment pipeline",
                "The deployment did not complete successfully.",
            ),
            IncidentCategory.API_OUTAGE: (
                "API availability incident",
                "reported API",
                "The API returned failures or was unavailable.",
            ),
            IncidentCategory.STORAGE_PROBLEM: (
                "Storage capacity incident",
                "reported storage system",
                "Storage capacity or access is abnormal.",
            ),
            IncidentCategory.DATA_PIPELINE_FAILURE: (
                "Data pipeline failure",
                "reported data pipeline",
                "The data-processing workflow failed.",
            ),
            IncidentCategory.HARDWARE_MALFUNCTION: (
                "Hardware malfunction",
                "reported hardware component",
                "The hardware reported abnormal behavior.",
            ),
            IncidentCategory.MANUFACTURING_EQUIPMENT_ISSUE: (
                "Manufacturing equipment warning",
                "reported manufacturing equipment",
                "The equipment reported abnormal operation.",
            ),
            IncidentCategory.SECURITY_ALERT: (
                "Security alert",
                "reported monitored system",
                "A suspicious security condition was reported.",
            ),
            IncidentCategory.OTHER: (
                "Technical incident",
                "reported system",
                "The report describes abnormal technical behavior.",
            ),
        }
        if output == OutputLanguage.EN:
            title, system, symptom = labels_en.get(category, labels_en[IncidentCategory.OTHER])
            return (
                title,
                system,
                symptom,
                "Notify the authorized owner, verify current impact, and preserve relevant evidence.",
                "Complete a human-led root-cause review and improve the approved monitoring or runbook.",
                "unknown",
                "Deterministic demo-provider output; not a real LLM result.",
            )
        labels_zh = {
            IncidentCategory.SERVER_FAILURE: (
                "服务器响应故障",
                "报告中的服务器",
                "服务器未正常响应。",
            ),
            IncidentCategory.NETWORK_INTERRUPTION: (
                "网络连接中断",
                "报告中的网络连接",
                "网络连接发生中断。",
            ),
            IncidentCategory.DATABASE_FAILURE: (
                "数据库可用性事件",
                "报告中的数据库",
                "数据库访问或可用性失败。",
            ),
            IncidentCategory.DEPLOYMENT_FAILURE: (
                "部署失败",
                "报告中的部署流水线",
                "部署未成功完成。",
            ),
            IncidentCategory.API_OUTAGE: ("API可用性事件", "报告中的API", "API返回失败或不可用。"),
            IncidentCategory.STORAGE_PROBLEM: (
                "存储问题",
                "报告中的存储系统",
                "存储容量或访问异常。",
            ),
            IncidentCategory.DATA_PIPELINE_FAILURE: (
                "数据流水线失败",
                "报告中的数据流水线",
                "数据处理流程失败。",
            ),
            IncidentCategory.HARDWARE_MALFUNCTION: (
                "硬件故障",
                "报告中的硬件组件",
                "硬件出现异常行为。",
            ),
            IncidentCategory.MANUFACTURING_EQUIPMENT_ISSUE: (
                "制造设备警告",
                "报告中的制造设备",
                "设备运行出现异常。",
            ),
            IncidentCategory.SECURITY_ALERT: (
                "安全警报",
                "报告中的受监控系统",
                "报告了可疑安全状况。",
            ),
            IncidentCategory.OTHER: ("技术事件", "报告中的系统", "报告描述了异常技术行为。"),
        }
        title, system, symptom = labels_zh.get(category, labels_zh[IncidentCategory.OTHER])
        return (
            title,
            system,
            symptom,
            "通知授权负责人，核实当前影响，并保留相关证据。",
            "由人工完成根本原因审查，并改进经批准的监控或运行手册。",
            "未知",
            "这是确定性演示提供程序的输出，不是真实LLM结果。",
        )
