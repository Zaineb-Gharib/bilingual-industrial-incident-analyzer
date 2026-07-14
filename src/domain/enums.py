"""Controlled values used throughout the application and evaluation."""

from enum import StrEnum


class InputLanguage(StrEnum):
    EN = "en"
    ZH = "zh"
    MIXED = "mixed"
    UNKNOWN = "unknown"


class OutputLanguage(StrEnum):
    EN = "en"
    ZH = "zh"


class IncidentCategory(StrEnum):
    SERVER_FAILURE = "server_failure"
    NETWORK_INTERRUPTION = "network_interruption"
    DATABASE_FAILURE = "database_failure"
    DEPLOYMENT_FAILURE = "deployment_failure"
    API_OUTAGE = "api_outage"
    STORAGE_PROBLEM = "storage_problem"
    DATA_PIPELINE_FAILURE = "data_pipeline_failure"
    HARDWARE_MALFUNCTION = "hardware_malfunction"
    MANUFACTURING_EQUIPMENT_ISSUE = "manufacturing_equipment_issue"
    SECURITY_ALERT = "security_alert"
    OTHER = "other"
    UNKNOWN = "unknown"


class Severity(StrEnum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNKNOWN = "unknown"


class CauseCertainty(StrEnum):
    EXPLICIT = "explicit"
    SUSPECTED = "suspected"
    UNKNOWN = "unknown"


class ResponsibleTeam(StrEnum):
    PLATFORM = "platform_operations"
    NETWORK = "network_operations"
    DATABASE = "database_operations"
    RELEASE = "release_engineering"
    APPLICATION = "application_engineering"
    STORAGE = "storage_operations"
    DATA = "data_engineering"
    HARDWARE = "hardware_support"
    MAINTENANCE = "maintenance_engineering"
    SECURITY = "security_operations"
    INCIDENT = "incident_management"
    UNKNOWN = "unknown"


class PromptingStrategy(StrEnum):
    ZERO_SHOT = "zero_shot"
    FEW_SHOT = "few_shot"
    SELF_REFINEMENT = "self_refinement"


class ValidationStatus(StrEnum):
    VALID = "valid"
    VALID_WITH_WARNINGS = "valid_with_warnings"
    INVALID_REPAIRABLE = "invalid_repairable"
    INVALID_TERMINAL = "invalid_terminal"


class IssueSeverity(StrEnum):
    WARNING = "warning"
    ERROR = "error"


class FailureType(StrEnum):
    NONE = "none"
    INPUT = "input"
    AUTHENTICATION = "authentication"
    RATE_LIMIT = "rate_limit"
    TIMEOUT = "timeout"
    PROVIDER = "provider"
    INVALID_JSON = "invalid_json"
    SCHEMA = "schema"
    GROUNDING = "grounding"
    SAFETY = "safety"
    REFINEMENT = "refinement"
    ENCODING = "encoding"
    INTERNAL = "internal"


class AnalysisStage(StrEnum):
    PRIMARY = "primary"
    SELF_INITIAL = "self_initial"
    SELF_REFINED = "self_refined"
    JSON_REPAIR = "json_repair"


class DatasetSplit(StrEnum):
    DEVELOPMENT = "development"
    EVALUATION = "evaluation"
