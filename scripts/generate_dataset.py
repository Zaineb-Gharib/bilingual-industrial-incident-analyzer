"""Generate the original AI-assisted synthetic BIIA-80 v1 dataset and prompt examples."""

from __future__ import annotations

import csv
import hashlib
import json
import sys
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.domain.enums import (
    DatasetSplit,
    IncidentCategory,
)
from src.schemas.dataset import DatasetScenarioPair

DATA_PATH = ROOT / "data/incidents_v1.jsonl"
CSV_PATH = ROOT / "data/incidents_v1.csv"
MATRIX_PATH = ROOT / "data/scenario_matrix_v1.csv"
MANIFEST_PATH = ROOT / "data/dataset_manifest_v1.json"
EXAMPLES_PATH = ROOT / "prompts/examples_v1.json"


def scenario(
    category: str,
    code: str,
    source_en: str,
    source_zh: str,
    severity: str,
    system_en: str,
    system_zh: str,
    symptom_en: str,
    symptom_zh: str,
    certainty: str = "unknown",
    cause_en: str = "unknown",
    cause_zh: str = "未知",
) -> dict[str, str]:
    return {
        "category": category,
        "code": code,
        "source_en": source_en,
        "source_zh": source_zh,
        "severity": severity,
        "system_en": system_en,
        "system_zh": system_zh,
        "symptom_en": symptom_en,
        "symptom_zh": symptom_zh,
        "certainty": certainty,
        "cause_en": cause_en,
        "cause_zh": cause_zh,
    }


SCENARIOS: list[dict[str, str]] = [
    scenario(
        "server_failure",
        "SRV",
        "At 09:10, the packaging line monitoring server stopped responding to health checks. Operators can still run the line locally, but the dashboard is unavailable. The cause is not yet known.",
        "09:10，包装线监控服务器停止响应健康检查。操作员仍可在本地运行生产线，但监控面板不可用。原因尚不清楚。",
        "high",
        "packaging line monitoring server",
        "包装线监控服务器",
        "health checks receive no response",
        "健康检查无响应",
    ),
    scenario(
        "server_failure",
        "SRV",
        "The authentication server restarted automatically after memory use rose for twenty minutes. Login service recovered, and the team suspects a memory leak but has not confirmed it.",
        "认证服务器在内存使用率上升二十分钟后自动重启。登录服务已经恢复，团队怀疑存在内存泄漏，但尚未确认。",
        "medium",
        "authentication server",
        "认证服务器",
        "automatic server restart",
        "服务器自动重启",
        "suspected",
        "memory leak",
        "内存泄漏",
    ),
    scenario(
        "server_failure",
        "SRV",
        "A compute node powered off after a power interruption, and all jobs on that node stopped. Other nodes remain available.",
        "电源中断后，一个计算节点关机，该节点上的所有作业停止。其他节点仍然可用。",
        "high",
        "compute node",
        "计算节点",
        "node powered off and jobs stopped",
        "节点关机且作业停止",
        "explicit",
        "power interruption",
        "电源中断",
    ),
    scenario(
        "server_failure",
        "SRV",
        "The backup server missed one scheduled health check and responded normally on the next check. No backup job impact has been reported.",
        "备份服务器错过了一次计划健康检查，并在下一次检查时正常响应。尚未报告备份作业受到影响。",
        "low",
        "backup server",
        "备份服务器",
        "one health check was missed",
        "错过一次健康检查",
    ),
    scenario(
        "network_interruption",
        "NET",
        "Sensors in workshop B lost connection to the gateway for six minutes after a switch reboot. Connections recovered automatically, and no sensor data was received during the interruption.",
        "交换机重启后，B车间的传感器与网关断开连接六分钟。连接已自动恢复，但中断期间未收到传感器数据。",
        "medium",
        "workshop B sensor network",
        "B车间传感器网络",
        "gateway connection and sensor data were interrupted",
        "网关连接和传感器数据中断",
        "explicit",
        "switch reboot",
        "交换机重启",
    ),
    scenario(
        "network_interruption",
        "NET",
        "The warehouse uplink became unavailable, leaving picking terminals offline. The network team is investigating and no recovery time is known.",
        "仓库上行链路不可用，导致拣货终端离线。网络团队正在调查，恢复时间未知。",
        "high",
        "warehouse uplink",
        "仓库上行链路",
        "picking terminals are offline",
        "拣货终端离线",
    ),
    scenario(
        "network_interruption",
        "NET",
        "Intermittent latency appeared on the office network after a routing configuration change. The change is suspected but has not been proven to be the cause.",
        "路由配置变更后，办公网络出现间歇性延迟。该变更被怀疑是原因，但尚未得到证实。",
        "medium",
        "office network",
        "办公网络",
        "intermittent latency",
        "间歇性延迟",
        "suspected",
        "routing configuration change",
        "路由配置变更",
    ),
    scenario(
        "network_interruption",
        "NET",
        "A redundant network link produced a warning while traffic continued over the second link. Users reported no service interruption.",
        "一条冗余网络链路发出警告，流量继续通过第二条链路传输。用户未报告服务中断。",
        "low",
        "redundant network link",
        "冗余网络链路",
        "link warning with traffic still flowing",
        "链路警告但流量仍在传输",
    ),
    scenario(
        "database_failure",
        "DBF",
        "The order service began returning database connection errors at 14:32. The database status page shows unavailable. No maintenance was scheduled, and the root cause is under investigation.",
        "14:32起，订单服务开始返回数据库连接错误。数据库状态页显示不可用。没有计划内维护，根本原因正在调查中。",
        "high",
        "order service database",
        "订单服务数据库",
        "connection errors and unavailable status",
        "连接错误且状态显示不可用",
    ),
    scenario(
        "database_failure",
        "DBF",
        "The reporting database replica fell twelve minutes behind because a long-running query consumed most resources. Primary transactions were unaffected.",
        "由于一个长时间运行的查询占用了大部分资源，报表数据库副本延迟了十二分钟。主库事务未受影响。",
        "medium",
        "reporting database replica",
        "报表数据库副本",
        "replication lag",
        "复制延迟",
        "explicit",
        "long-running query",
        "长时间运行的查询",
    ),
    scenario(
        "database_failure",
        "DBF",
        "The inventory database reported repeated page-read errors. Engineers suspect a storage fault, but the database remains online in degraded mode.",
        "库存数据库重复报告页面读取错误。工程师怀疑存在存储故障，但数据库仍以降级模式在线。",
        "high",
        "inventory database",
        "库存数据库",
        "repeated page-read errors",
        "重复的页面读取错误",
        "suspected",
        "storage fault",
        "存储故障",
    ),
    scenario(
        "database_failure",
        "DBF",
        "The development catalog database responded slowly for five minutes. No production user impact was observed.",
        "开发环境目录数据库响应缓慢五分钟。未观察到生产用户受到影响。",
        "low",
        "development catalog database",
        "开发环境目录数据库",
        "temporary slow responses",
        "短暂响应缓慢",
    ),
    scenario(
        "deployment_failure",
        "DEP",
        "Release 2.8 failed during the database migration step. The deployment system stopped the rollout and kept version 2.7 active. The log reports a migration checksum mismatch.",
        "2.8版本在数据库迁移步骤中失败。部署系统停止了发布，并保持2.7版本继续运行。日志显示迁移校验和不匹配。",
        "medium",
        "release deployment pipeline",
        "版本部署流水线",
        "migration step failed and rollout stopped",
        "迁移步骤失败且发布停止",
        "explicit",
        "migration checksum mismatch",
        "迁移校验和不匹配",
    ),
    scenario(
        "deployment_failure",
        "DEP",
        "A service deployment failed its health checks, so the platform kept the previous version active. The reason for the failed checks is unknown.",
        "一次服务部署未通过健康检查，因此平台保持旧版本继续运行。健康检查失败的原因未知。",
        "medium",
        "service deployment",
        "服务部署",
        "new version failed health checks",
        "新版本未通过健康检查",
    ),
    scenario(
        "deployment_failure",
        "DEP",
        "The production login rollout caused authentication errors across two services. The release team suspects an incorrect environment setting and paused the rollout.",
        "生产登录功能发布后，两个服务出现认证错误。发布团队怀疑环境设置不正确，并暂停了发布。",
        "high",
        "production login rollout",
        "生产登录功能发布",
        "authentication errors across services",
        "多个服务出现认证错误",
        "suspected",
        "incorrect environment setting",
        "环境设置不正确",
    ),
    scenario(
        "deployment_failure",
        "DEP",
        "A staging deployment emitted a deprecation warning but completed successfully. No test failure or user impact was reported.",
        "一次预发布环境部署发出弃用警告，但已成功完成。未报告测试失败或用户影响。",
        "low",
        "staging deployment",
        "预发布环境部署",
        "deprecation warning",
        "弃用警告",
    ),
    scenario(
        "api_outage",
        "API",
        "The supplier status API returned HTTP 503 responses for eighteen minutes. Requests are still failing and the cause is unknown.",
        "供应商状态API持续十八分钟返回HTTP 503响应。请求仍在失败，原因未知。",
        "high",
        "supplier status API",
        "供应商状态API",
        "HTTP 503 responses",
        "HTTP 503响应",
    ),
    scenario(
        "api_outage",
        "API",
        "The internal scheduling API failed intermittently and recovered without intervention. A gateway timeout is suspected but not confirmed.",
        "内部排程API间歇性失败，随后在无人干预的情况下恢复。怀疑是网关超时，但尚未确认。",
        "medium",
        "internal scheduling API",
        "内部排程API",
        "intermittent failures",
        "间歇性失败",
        "suspected",
        "gateway timeout",
        "网关超时",
    ),
    scenario(
        "api_outage",
        "API",
        "The payment API became unavailable after its certificate expired. Clients are receiving connection failures.",
        "支付API在证书过期后变得不可用。客户端正在收到连接失败。",
        "high",
        "payment API",
        "支付API",
        "connection failures and unavailability",
        "连接失败且API不可用",
        "explicit",
        "expired certificate",
        "证书过期",
    ),
    scenario(
        "api_outage",
        "API",
        "The sandbox API recorded three extra error responses during a test. The endpoint is currently available and no production traffic was involved.",
        "沙箱API在测试期间多记录了三个错误响应。该接口当前可用，且不涉及生产流量。",
        "low",
        "sandbox API",
        "沙箱API",
        "small increase in test errors",
        "测试错误小幅增加",
    ),
    scenario(
        "storage_problem",
        "STO",
        "The analytics volume reached 98 percent capacity and new jobs are being paused. Existing data remains readable.",
        "分析数据卷容量达到98%，新作业正在暂停。现有数据仍可读取。",
        "high",
        "analytics storage volume",
        "分析数据卷",
        "capacity reached 98 percent",
        "容量达到98%",
    ),
    scenario(
        "storage_problem",
        "STO",
        "The archive volume switched to read-only mode for nine minutes and then recovered. The cause has not been identified.",
        "归档数据卷进入只读模式九分钟后恢复。原因尚未确定。",
        "medium",
        "archive storage volume",
        "归档数据卷",
        "temporary read-only mode",
        "短暂进入只读模式",
    ),
    scenario(
        "storage_problem",
        "STO",
        "Object storage uploads are unavailable, while downloads continue to work. The storage team is investigating.",
        "对象存储上传不可用，但下载仍然正常。存储团队正在调查。",
        "high",
        "object storage upload service",
        "对象存储上传服务",
        "uploads unavailable",
        "上传不可用",
    ),
    scenario(
        "storage_problem",
        "STO",
        "A controller failure is causing data loss in progress on the test backup array. The array has been isolated by authorized storage staff.",
        "控制器故障正在导致测试备份阵列中的数据丢失。该阵列已由授权存储人员隔离。",
        "critical",
        "test backup storage array",
        "测试备份存储阵列",
        "data loss is in progress",
        "正在发生数据丢失",
        "explicit",
        "controller failure",
        "控制器故障",
    ),
    scenario(
        "data_pipeline_failure",
        "DPL",
        "The nightly ETL pipeline failed because the expected source partition was missing. No warehouse table was updated.",
        "夜间ETL流水线因缺少预期的源分区而失败。数据仓库表均未更新。",
        "medium",
        "nightly ETL pipeline",
        "夜间ETL流水线",
        "pipeline failed and tables were not updated",
        "流水线失败且表未更新",
        "explicit",
        "missing source partition",
        "缺少源分区",
    ),
    scenario(
        "data_pipeline_failure",
        "DPL",
        "The event stream is twenty minutes behind. Processing continues, but the reason for the lag is unknown.",
        "事件流延迟二十分钟。处理仍在继续，但延迟原因未知。",
        "medium",
        "event streaming pipeline",
        "事件流处理流水线",
        "processing lag",
        "处理延迟",
    ),
    scenario(
        "data_pipeline_failure",
        "DPL",
        "The production quality pipeline stopped after an input schema change. The data team suspects the new field format caused the parser failure.",
        "输入模式变更后，生产质量数据流水线停止。数据团队怀疑新的字段格式导致解析器失败。",
        "high",
        "production quality data pipeline",
        "生产质量数据流水线",
        "parser failure stopped processing",
        "解析器失败导致处理停止",
        "suspected",
        "new field format",
        "新的字段格式",
    ),
    scenario(
        "data_pipeline_failure",
        "DPL",
        "A development batch job started ten minutes late and completed normally. No downstream schedule was affected.",
        "一个开发批处理作业晚启动十分钟，但已正常完成。下游计划未受影响。",
        "low",
        "development batch job",
        "开发批处理作业",
        "late start",
        "启动延迟",
    ),
    scenario(
        "hardware_malfunction",
        "HWM",
        "One power supply in a rack server reported a warning while the redundant supply remained active. The server stayed online.",
        "机架服务器中的一个电源报告警告，冗余电源仍在工作。服务器保持在线。",
        "medium",
        "rack server power supply",
        "机架服务器电源",
        "power-supply warning",
        "电源警告",
    ),
    scenario(
        "hardware_malfunction",
        "HWM",
        "A controller temperature reading exceeded its warning threshold twice. The controller remains active while hardware support investigates.",
        "控制器温度读数两次超过警告阈值。控制器仍在运行，硬件支持团队正在调查。",
        "high",
        "industrial controller",
        "工业控制器",
        "temperature exceeded warning threshold",
        "温度超过警告阈值",
    ),
    scenario(
        "hardware_malfunction",
        "HWM",
        "A disk failure made one compute node unavailable. Workloads were moved by the approved platform process.",
        "磁盘故障导致一个计算节点不可用。工作负载已通过批准的平台流程迁移。",
        "high",
        "compute node disk",
        "计算节点磁盘",
        "disk failure and node unavailable",
        "磁盘故障且节点不可用",
        "explicit",
        "disk failure",
        "磁盘故障",
    ),
    scenario(
        "hardware_malfunction",
        "HWM",
        "A spare sensor module produced one invalid reading during bench testing. Later readings were normal.",
        "备用传感器模块在台架测试中产生了一次无效读数。后续读数正常。",
        "low",
        "spare sensor module",
        "备用传感器模块",
        "one invalid test reading",
        "一次无效测试读数",
    ),
    scenario(
        "manufacturing_equipment_issue",
        "MFG",
        "The press vibration reading rose above its warning threshold twice during the morning shift. No product defect has been confirmed. The operator paused the press and notified maintenance.",
        "早班期间，压力机振动读数两次超过警告阈值。尚未确认产品缺陷。操作员已暂停压力机并通知维修人员。",
        "high",
        "industrial press",
        "压力机",
        "vibration exceeded warning threshold",
        "振动超过警告阈值",
    ),
    scenario(
        "manufacturing_equipment_issue",
        "MFG",
        "The conveyor stopped because a guard sensor remained open. The operator kept the line stopped and called qualified maintenance.",
        "输送机因防护传感器保持开启状态而停止。操作员保持生产线停止，并联系了合格维修人员。",
        "high",
        "production conveyor",
        "生产输送机",
        "conveyor stopped",
        "输送机停止",
        "explicit",
        "open guard sensor",
        "防护传感器保持开启",
    ),
    scenario(
        "manufacturing_equipment_issue",
        "MFG",
        "Smoke was observed near the test furnace and the safety interlock stopped heating. The area was evacuated under the approved emergency procedure.",
        "测试炉附近观察到烟雾，安全联锁停止了加热。人员已按照批准的应急程序撤离该区域。",
        "critical",
        "test furnace",
        "测试炉",
        "smoke observed and heating stopped",
        "观察到烟雾且加热停止",
    ),
    scenario(
        "manufacturing_equipment_issue",
        "MFG",
        "The packaging labeler placed two labels slightly off center. Production continued after the samples were held for inspection.",
        "包装贴标机有两个标签位置略微偏离中心。样品被保留检查后，生产继续进行。",
        "low",
        "packaging labeler",
        "包装贴标机",
        "two labels were misaligned",
        "两个标签位置偏移",
    ),
    scenario(
        "security_alert",
        "SEC",
        "The identity system detected a spike in failed login attempts from test accounts. No successful unauthorized login has been confirmed.",
        "身份系统检测到测试账户的登录失败次数激增。尚未确认有未经授权的成功登录。",
        "medium",
        "identity monitoring system",
        "身份监控系统",
        "spike in failed login attempts",
        "登录失败次数激增",
    ),
    scenario(
        "security_alert",
        "SEC",
        "Endpoint protection detected a known malware signature in a training file and automatically isolated the test workstation. No execution was observed.",
        "终端防护在一个培训文件中检测到已知恶意软件特征，并自动隔离了测试工作站。未观察到文件执行。",
        "high",
        "test workstation endpoint protection",
        "测试工作站终端防护",
        "malware-signature alert and isolation",
        "恶意软件特征警报并隔离",
        "explicit",
        "known malware signature in a training file",
        "培训文件中的已知恶意软件特征",
    ),
    scenario(
        "security_alert",
        "SEC",
        "The audit system confirmed an unauthorized export of synthetic test files from the research workspace. Security operations contained the account and preserved logs.",
        "审计系统确认研究工作区中的合成测试文件被未经授权导出。安全运营团队已控制该账户并保留日志。",
        "critical",
        "research workspace audit system",
        "研究工作区审计系统",
        "confirmed unauthorized export",
        "确认未经授权的数据导出",
        "explicit",
        "unauthorized account activity",
        "未经授权的账户活动",
    ),
    scenario(
        "security_alert",
        "SEC",
        "A badge reader generated an access warning after an expired test badge was presented. The door remained locked and no access was gained.",
        "一个过期测试门禁卡被刷卡后，门禁读卡器产生访问警告。门保持锁定，未获得访问权限。",
        "low",
        "badge access reader",
        "门禁读卡器",
        "access warning with no entry",
        "访问警告但未进入",
    ),
]


TEAM_BY_CATEGORY = {
    "server_failure": "platform_operations",
    "network_interruption": "network_operations",
    "database_failure": "database_operations",
    "deployment_failure": "release_engineering",
    "api_outage": "application_engineering",
    "storage_problem": "storage_operations",
    "data_pipeline_failure": "data_engineering",
    "hardware_malfunction": "hardware_support",
    "manufacturing_equipment_issue": "maintenance_engineering",
    "security_alert": "security_operations",
}

ACTION_BY_CATEGORY = {
    "server_failure": (
        "notify_platform_and_preserve_logs",
        "Notify platform operations and preserve server logs.",
        "通知平台运维并保留服务器日志。",
    ),
    "network_interruption": (
        "verify_network_and_preserve_logs",
        "Verify connectivity and preserve network logs.",
        "核实网络连接并保留网络日志。",
    ),
    "database_failure": (
        "notify_database_and_preserve_logs",
        "Notify database operations and preserve database and application logs.",
        "通知数据库运维并保留数据库和应用日志。",
    ),
    "deployment_failure": (
        "pause_release_and_review_logs",
        "Keep the rollout paused and review approved deployment logs.",
        "保持发布暂停并审查经批准的部署日志。",
    ),
    "api_outage": (
        "notify_application_and_verify_scope",
        "Notify the application owner and verify the outage scope.",
        "通知应用负责人并核实中断范围。",
    ),
    "storage_problem": (
        "notify_storage_and_protect_data",
        "Notify storage operations and protect evidence and data under approved procedures.",
        "通知存储运维，并按批准流程保护证据和数据。",
    ),
    "data_pipeline_failure": (
        "pause_downstream_and_preserve_logs",
        "Protect downstream data and preserve pipeline logs.",
        "保护下游数据并保留流水线日志。",
    ),
    "hardware_malfunction": (
        "qualified_hardware_review",
        "Request qualified hardware review and preserve readings.",
        "请求合格硬件人员审查并保留读数。",
    ),
    "manufacturing_equipment_issue": (
        "keep_safe_state_and_notify_maintenance",
        "Keep equipment in its current safe state and notify qualified maintenance.",
        "保持设备当前安全状态并通知合格维修人员。",
    ),
    "security_alert": (
        "notify_security_and_preserve_evidence",
        "Notify security operations and preserve evidence under the approved incident process.",
        "通知安全运营并按批准的事件流程保留证据。",
    ),
}


def concept(concept_id: str, en: str, zh: str) -> dict[str, Any]:
    return {
        "id": concept_id,
        "en": en,
        "zh": zh,
        "acceptable_en": [en],
        "acceptable_zh": [zh],
    }


def first_sentence(text: str, punctuation: str) -> str:
    return text.split(punctuation, 1)[0].strip()


def build_records() -> list[DatasetScenarioPair]:
    category_indexes: Counter[str] = Counter()
    records = []
    for item in SCENARIOS:
        category_indexes[item["category"]] += 1
        index = category_indexes[item["category"]]
        split = "development" if index == 1 else "evaluation"
        prefix = "DEV" if split == "development" else "EVAL"
        scenario_id = f"{prefix}-{item['code']}-{index:03d}"
        action_id, action_en, action_zh = ACTION_BY_CATEGORY[item["category"]]
        long_id = f"review_{item['category']}_controls"
        record = DatasetScenarioPair.model_validate(
            {
                "dataset_version": "1.0",
                "scenario_id": scenario_id,
                "split": split,
                "category": item["category"],
                "source_en": item["source_en"],
                "source_zh": item["source_zh"],
                "translation_review_status": "pending_manual_review",
                "translation_reviewer_notes": "AI-assisted draft; requires bilingual human review.",
                "severity": item["severity"],
                "affected_system": {
                    "concept_id": f"{item['code'].lower()}_{index}_system",
                    "en": item["system_en"],
                    "zh": item["system_zh"],
                },
                "symptom_concepts": [
                    concept(
                        f"{item['code'].lower()}_{index}_symptom",
                        item["symptom_en"],
                        item["symptom_zh"],
                    )
                ],
                "suspected_cause": {
                    "certainty": item["certainty"],
                    "en": item["cause_en"],
                    "zh": item["cause_zh"],
                },
                "immediate_action_concepts": [concept(action_id, action_en, action_zh)],
                "long_term_action_concepts": [
                    concept(
                        long_id,
                        "Complete a human-led root-cause review and improve approved controls.",
                        "由人工完成根本原因审查并改进经批准的控制措施。",
                    )
                ],
                "responsible_team": TEAM_BY_CATEGORY[item["category"]],
                "evidence_spans_en": [first_sentence(item["source_en"], ".")],
                "evidence_spans_zh": [first_sentence(item["source_zh"], "。")],
                "safety_notes": "Recommendations must remain cautious, non-destructive, and authorization-aware.",
                "ambiguity_notes": (
                    "Cause is not confirmed."
                    if item["certainty"] != "explicit"
                    else "Only the stated cause is labeled; deeper root cause remains unknown."
                ),
                "creation": {
                    "author_id": "codex-ai-assisted-draft",
                    "created_date": date(2026, 7, 14),
                    "reviewer_id": None,
                    "review_date": None,
                    "ai_assisted": True,
                },
            }
        )
        records.append(record)
    return records


def write_jsonl(records: list[DatasetScenarioPair]) -> str:
    payload = "\n".join(record.model_dump_json() for record in records) + "\n"
    DATA_PATH.write_text(payload, encoding="utf-8")
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def write_csv(records: list[DatasetScenarioPair]) -> None:
    fieldnames = [
        "dataset_version",
        "scenario_id",
        "split",
        "category",
        "severity",
        "source_en",
        "source_zh",
        "affected_system_en",
        "affected_system_zh",
        "responsible_team",
        "cause_certainty",
        "cause_en",
        "cause_zh",
        "evidence_spans_en",
        "evidence_spans_zh",
        "translation_review_status",
    ]
    with CSV_PATH.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for record in records:
            writer.writerow(
                {
                    "dataset_version": record.dataset_version,
                    "scenario_id": record.scenario_id,
                    "split": record.split.value,
                    "category": record.category.value,
                    "severity": record.severity.value,
                    "source_en": record.source_en,
                    "source_zh": record.source_zh,
                    "affected_system_en": record.affected_system.en,
                    "affected_system_zh": record.affected_system.zh,
                    "responsible_team": record.responsible_team.value,
                    "cause_certainty": record.suspected_cause.certainty.value,
                    "cause_en": record.suspected_cause.en,
                    "cause_zh": record.suspected_cause.zh,
                    "evidence_spans_en": json.dumps(record.evidence_spans_en, ensure_ascii=False),
                    "evidence_spans_zh": json.dumps(record.evidence_spans_zh, ensure_ascii=False),
                    "translation_review_status": record.translation_review_status,
                }
            )


def write_matrix(records: list[DatasetScenarioPair]) -> None:
    with MATRIX_PATH.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "scenario_id",
                "split",
                "category",
                "severity",
                "cause_certainty",
                "translation_review_status",
            ],
        )
        writer.writeheader()
        for record in records:
            writer.writerow(
                {
                    "scenario_id": record.scenario_id,
                    "split": record.split.value,
                    "category": record.category.value,
                    "severity": record.severity.value,
                    "cause_certainty": record.suspected_cause.certainty.value,
                    "translation_review_status": record.translation_review_status,
                }
            )


TITLE_EN = {
    category.value: category.value.replace("_", " ").title() for category in IncidentCategory
}
TITLE_ZH = {
    "server_failure": "服务器故障",
    "network_interruption": "网络中断",
    "database_failure": "数据库故障",
    "deployment_failure": "部署失败",
    "api_outage": "API中断",
    "storage_problem": "存储问题",
    "data_pipeline_failure": "数据流水线失败",
    "hardware_malfunction": "硬件故障",
    "manufacturing_equipment_issue": "制造设备问题",
    "security_alert": "安全警报",
}


def example_for(
    record: DatasetScenarioPair,
    input_language: str,
    output_language: str,
) -> dict[str, Any]:
    source = record.source_en if input_language == "en" else record.source_zh
    use_en = output_language == "en"
    unknown = "unknown" if use_en else "未知"
    action = record.immediate_action_concepts[0]
    long_action = record.long_term_action_concepts[0]
    output = {
        "schema_version": "1.0",
        "prompt_version": "1.0",
        "input_language": input_language,
        "output_language": output_language,
        "incident_title": TITLE_EN[record.category.value]
        if use_en
        else TITLE_ZH[record.category.value],
        "incident_category": record.category.value,
        "severity": record.severity.value,
        "affected_system": record.affected_system.en if use_en else record.affected_system.zh,
        "main_symptoms": [
            record.symptom_concepts[0].en if use_en else record.symptom_concepts[0].zh
        ],
        "suspected_cause": {
            "statement": (record.suspected_cause.en if use_en else record.suspected_cause.zh)
            or unknown,
            "certainty": record.suspected_cause.certainty.value,
        },
        "recommended_immediate_actions": [
            {
                "action": action.en if use_en else action.zh,
                "rationale": (
                    "This is a cautious, authorized triage step."
                    if use_en
                    else "这是谨慎且需要授权的初步处置步骤。"
                ),
                "requires_authorization": True,
            }
        ],
        "recommended_long_term_actions": [long_action.en if use_en else long_action.zh],
        "responsible_team": record.responsible_team.value,
        "evidence": [
            {
                "quote": (
                    record.evidence_spans_en[0]
                    if input_language == "en"
                    else record.evidence_spans_zh[0]
                ),
                "supports_fields": ["affected_system", "main_symptoms", "severity"],
            }
        ],
        "uncertainty_explanation": (
            "Only information stated in the report is included."
            if use_en
            else "仅包含报告中明确陈述的信息。"
        ),
        "confidence": {
            "level": "medium",
            "explanation": (
                "Key symptoms are explicit; missing details remain unknown."
                if use_en
                else "主要症状明确，缺失信息保持未知。"
            ),
        },
        "warnings": [],
    }
    return {
        "scenario_id": record.scenario_id,
        "input_language": input_language,
        "output_language": output_language,
        "incident_report": source,
        "expected_output": output,
    }


def write_examples(records: list[DatasetScenarioPair]) -> list[str]:
    dev = {
        record.category.value: record
        for record in records
        if record.split == DatasetSplit.DEVELOPMENT
    }
    examples = [
        example_for(dev["server_failure"], "en", "en"),
        example_for(dev["database_failure"], "zh", "zh"),
        example_for(dev["deployment_failure"], "en", "zh"),
        example_for(dev["manufacturing_equipment_issue"], "zh", "en"),
    ]
    EXAMPLES_PATH.write_text(
        json.dumps(examples, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return [example["scenario_id"] for example in examples]


def write_manifest(
    records: list[DatasetScenarioPair],
    dataset_hash: str,
    example_ids: list[str],
) -> None:
    manifest = {
        "dataset_name": "BIIA-80",
        "dataset_version": "1.0",
        "sha256": dataset_hash,
        "scenario_pairs": len(records),
        "language_specific_reports": len(records) * 2,
        "split_counts": Counter(record.split.value for record in records),
        "category_counts": Counter(record.category.value for record in records),
        "severity_counts": Counter(record.severity.value for record in records),
        "translation_review_counts": Counter(
            record.translation_review_status for record in records
        ),
        "few_shot_example_ids": example_ids,
        "provenance": "Original fictional incidents generated with Codex assistance.",
        "human_review_status": "pending_manual_review",
        "encoding": "UTF-8 JSONL; UTF-8 with BOM CSV inspection copy",
        "created_date": "2026-07-14",
    }
    MANIFEST_PATH.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, default=dict) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    records = build_records()
    dataset_hash = write_jsonl(records)
    write_csv(records)
    write_matrix(records)
    example_ids = write_examples(records)
    write_manifest(records, dataset_hash, example_ids)
    print(
        json.dumps(
            {
                "scenario_pairs": len(records),
                "language_specific_reports": len(records) * 2,
                "sha256": dataset_hash,
                "manual_review_status": "pending_manual_review",
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
