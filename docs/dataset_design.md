# Dataset Design

**Dataset working name:** BIIA-80 v1  
**Planned size:** 40 bilingual scenario pairs = 80 language-specific reports  
**Purpose:** Development examples and held-out evaluation for the three prompting strategies  
**Status:** Design only; the complete dataset has not been created or reviewed

---

# 1. Dataset Goal and Unit

The dataset should test whether an LLM can structure short English and Simplified Chinese incident reports. The source-of-truth unit is a **scenario pair**: one fictional incident represented by meaning-equivalent English and Chinese reports with shared canonical labels. The evaluation loader expands each pair into two language-specific tasks.

Why this design:

- The model sees natural reports rather than literal translation fragments.
- Both language versions share one scenario identity.
- Bilingual consistency can be measured.
- Translations cannot accidentally enter different dataset splits.

The dataset must not be used to claim broad industrial performance. It is a small portfolio benchmark.

## Explanation in Simple Words

One fictional event is written in English and Chinese. The two versions stay together. This makes it possible to check whether changing the input language changes the model’s answer.

---

# 2. Scope and Balance

## 2.1 Category Allocation

| Category | Development pairs | Evaluation pairs | Total pairs | Expanded reports |
|---|---:|---:|---:|---:|
| server_failure | 1 | 3 | 4 | 8 |
| network_interruption | 1 | 3 | 4 | 8 |
| database_failure | 1 | 3 | 4 | 8 |
| deployment_failure | 1 | 3 | 4 | 8 |
| api_outage | 1 | 3 | 4 | 8 |
| storage_problem | 1 | 3 | 4 | 8 |
| data_pipeline_failure | 1 | 3 | 4 | 8 |
| hardware_malfunction | 1 | 3 | 4 | 8 |
| manufacturing_equipment_issue | 1 | 3 | 4 | 8 |
| security_alert | 1 | 3 | 4 | 8 |
| **Total** | **10** | **30** | **40** | **80** |

## 2.2 Recommended Variation

Across 40 pairs, deliberately vary:

- report length: approximately 20-90 English words and comparable Chinese meaning;
- severity: include low/medium/high and only a few carefully justified critical cases;
- cause information: explicit, suspected, and unknown;
- current state: ongoing, recovered, contained, and uncertain;
- impact: service unavailable, degraded, data gap, production pause, warning only;
- terminology: database/DB, server/node, pipeline/job, machine/equipment;
- evidence density: one to four useful spans;
- setting: web services, internal IT, data platforms, warehouse, workshop, production line;
- negation: “no defect confirmed,” “no maintenance scheduled”;
- time/numbers: some, but not every report;
- mixed-language product names, without turning the whole dataset mixed.

Avoid stereotyped patterns such as making every critical report Chinese or every hardware issue caused by overheating.

## Explanation in Simple Words

Each category gets the same number of examples. Reports should still differ in length, impact, certainty, and setting so the model cannot win by memorizing one pattern.

---

# 3. Authoritative Record Schema

Store one JSON object per line in data/incidents_v1.jsonl. Keep a generated CSV only for convenient inspection.

~~~json
{
  "dataset_version": "1.0",
  "scenario_id": "EV-API-002",
  "split": "evaluation",
  "category": "api_outage",
  "source_en": "English report",
  "source_zh": "中文报告",
  "translation_review_status": "approved",
  "translation_reviewer_notes": "Facts, negation and uncertainty align.",
  "severity": "high",
  "affected_system": {
    "concept_id": "supplier_status_api",
    "en": "supplier status API",
    "zh": "供应商状态API"
  },
  "symptom_concepts": [
    {
      "id": "http_503",
      "en": "HTTP 503 responses",
      "zh": "HTTP 503响应",
      "acceptable_en": ["503 response", "HTTP 503"],
      "acceptable_zh": ["503响应", "HTTP 503"]
    }
  ],
  "suspected_cause": {
    "certainty": "unknown",
    "en": "unknown",
    "zh": "未知"
  },
  "immediate_action_concepts": [
    {
      "id": "notify_application_team",
      "en": "notify the application team",
      "zh": "通知应用团队"
    }
  ],
  "long_term_action_concepts": [],
  "responsible_team": "application_engineering",
  "evidence_spans_en": ["exact English substring"],
  "evidence_spans_zh": ["中文原文片段"],
  "safety_notes": "No destructive or unauthorized action.",
  "ambiguity_notes": "Cause and scope are not stated.",
  "creation": {
    "author_id": "author-01",
    "created_date": "YYYY-MM-DD",
    "reviewer_id": "reviewer-01",
    "review_date": "YYYY-MM-DD"
  }
}
~~~

Required invariants:

- scenario_id is unique and stable.
- split is development or evaluation.
- category and severity use allowed enum values.
- both source strings are non-empty UTF-8.
- both translations have exactly the same split and scenario ID because they are one record.
- every evidence span is an exact substring of its matching source after Unicode NFC.
- certainty unknown uses unknown/未知 and does not smuggle a guessed cause into labels.
- gold actions are concepts, not copy-ready commands.
- development records are the only allowed few-shot sources.

## Explanation in Simple Words

The JSONL record stores both reports and all labels together. Rules called invariants are facts that must always be true, such as evidence being copied from the correct report.

---

# 4. Labeling Guide

## 4.1 Category

Choose the primary incident type described by the report:

- **server_failure:** a server/node/host is stopped, unresponsive, or unavailable.
- **network_interruption:** connectivity, routing, gateway, DNS, or link interruption is primary.
- **database_failure:** database availability, connection, replication, or database operation is primary.
- **deployment_failure:** rollout, release, build-to-deploy, migration during deployment, or rollback is primary.
- **api_outage:** an API endpoint/service interface is unavailable or returning failure responses.
- **storage_problem:** capacity, volume, disk space, storage mount, or object storage is primary.
- **data_pipeline_failure:** ingestion, ETL, scheduled job, stream, or data-processing workflow is primary.
- **hardware_malfunction:** general computing/electronic hardware such as disk, power supply, controller, or sensor hardware.
- **manufacturing_equipment_issue:** production machinery/process equipment behavior is primary.
- **security_alert:** suspicious or policy-triggering activity is primary; an alert does not prove compromise.

If two categories appear, label the incident’s central failure and record the secondary aspect in ambiguity_notes. The evaluation data should avoid cases where two labels are equally defensible unless the ambiguity is intentional and documented.

## 4.2 Severity

Use only stated impact and reasonable direct implications:

- **critical:** explicit immediate human safety danger, confirmed destructive loss in progress, confirmed major compromise, or broad essential production outage without workaround.
- **high:** major system unavailability or credible production/safety risk requiring urgent expert response.
- **medium:** limited, temporary, recovered, contained, or degraded disruption with no stated immediate safety danger.
- **low:** warning/minor issue with little stated operational impact.
- **unknown:** insufficient impact information.

Do not make every unavailable service critical. Do not downgrade manufacturing warnings merely because no defect is yet confirmed.

## 4.3 Affected System

Label the most specific system explicitly supported:

- Good: “order service database.”
- Too broad: “IT system.”
- Unsupported: “primary PostgreSQL cluster” when neither primary nor PostgreSQL appears.

Give it a canonical concept ID and bilingual labels.

## 4.4 Symptoms

Break observable behavior into separate concepts:

- no response to health checks;
- dashboard unavailable;
- database connection errors;
- vibration over threshold;
- telemetry missing.

Do not put causes or recommended actions in symptoms.

## 4.5 Suspected Cause and Certainty

- **explicit:** the report directly connects a cause to the incident.
- **suspected:** the report uses wording such as “may be,” “suspected,” or “possibly.”
- **unknown:** no cause is stated.

An event sequence is not always causation. “After deployment” is a timing clue; only label it explicit if the report says the deployment caused or triggered the failure.

## 4.6 Recommended Action Concepts

Labels represent acceptable goals, not exact wording. Immediate concepts can include:

- notify the authorized owner;
- verify current status/impact;
- preserve logs/readings/evidence;
- follow an approved runbook;
- keep equipment safely paused;
- check approved failover/rollback options;
- check backup status before any restoration.

Long-term concepts can include:

- complete root-cause review;
- improve monitoring/alerting;
- review resilience/failover;
- add pre-deployment validation;
- review preventive maintenance;
- improve data buffering/reprocessing controls.

Never label a command, forced restart, deletion, bypass, unapproved isolation, or physical repair instruction.

## 4.7 Responsible Team

Use the team most likely to coordinate first, based on the affected system:

- platform_operations
- network_operations
- database_operations
- release_engineering
- application_engineering
- storage_operations
- data_engineering
- hardware_support
- maintenance_engineering
- security_operations
- incident_management
- unknown

This is a routing label, not a statement of fault.

## 4.8 Evidence

Evidence spans:

- must be copied exactly from source;
- should be short enough to locate;
- collectively support the central symptoms, system, cause/certainty, or severity;
- should not be entire reports unless the report is extremely short;
- remain source-language text.

## Explanation in Simple Words

The labeling guide tells human authors how to choose the “correct” answers. It keeps labels consistent and stops a labeler from inventing facts that are not in the report.

---

# 5. Creation Workflow

## Step 1 - Matrix

Create a 40-row plan with ID, category, split, desired severity, cause certainty, setting, length band, and special feature such as negation or recovery.

## Step 2 - First-Language Draft

Write reports from scratch. Do not adapt a company’s real report. Keep details internally consistent and avoid real names/IPs/customers.

## Step 3 - Independent Gold Labels

Label from the report and rubric before any LLM is run. If a field is unknown, keep it unknown rather than revising the report solely to make evaluation easier.

## Step 4 - Translation

Translate meaning, factual details, uncertainty, negation, units, and impact. Natural word order is more important than literal word order.

## Step 5 - Evidence Selection

Select exact spans independently from each source text. Run automated containment immediately.

## Step 6 - Bilingual Review

The reviewer checks:

- same systems and components;
- same number/time/unit facts;
- same cause certainty;
- same outage/recovery status;
- same negative claims;
- similar tone, without adding urgency;
- natural terminology.

## Step 7 - Adjudication

Record disagreements. If category/severity changes, re-check both sources and all labels. Never silently erase the original note.

## Step 8 - Freeze

Sort by stable scenario_id; validate; generate manifest/hash/counts; tag version 1.0. Changes after freeze require a new version and reason.

## Explanation in Simple Words

The workflow separates writing, labeling, translating, and reviewing. That reduces the chance that one mistake quietly affects every part of a record.

---

# 6. Translation Quality

Preferred review is a second bilingual person. If unavailable:

1. The author translates.
2. After a delay, the author performs a blind comparison.
3. A translation tool or model may produce a back-translation as a clue only.
4. The author documents single-reviewer limitations.
5. At least the primary public examples receive external bilingual review before release if possible.

Do not use automatic translation output as unquestioned ground truth. Check domain terms such as:

- deployment: 部署/发布 depending on context;
- pipeline: 流水线 for data/software pipeline, not manufacturing production line unless intended;
- gateway: 网关;
- outage/unavailable: 中断/不可用 with the same scope;
- suspected: 疑似/可能, not confirmed wording;
- press: 压力机, not journalistic press.

## Explanation in Simple Words

A translation can be grammatical but still change the technical meaning. Review focuses on facts and uncertainty, not just whether the sentence sounds smooth.

---

# 7. Leakage Prevention

## Split Rule

Assign split at scenario-pair level. No translation, paraphrase, or near duplicate may cross the boundary.

## Few-Shot Rule

The prompt bank references only development IDs. Add an automated test that loads the dataset and fails if any example ID is evaluation.

## Similarity Audit

- Normalize English case/whitespace and Chinese Unicode/whitespace.
- Compare word/character shingles.
- Flag shared long phrases.
- Manually review same-category pairs with high overlap.
- Keep recurring necessary terminology, but rewrite incident facts and structure.

## Experiment Freeze

Prompt authors may inspect development labels. Before the primary experiment:

- freeze prompt v1;
- freeze example IDs;
- freeze dataset hash;
- create manifest;
- avoid prompt edits based on evaluation outcomes.

If a genuine bug requires a change, mark the previous run invalid/exploratory and create a new prompt or dataset version.

## Explanation in Simple Words

Leakage happens when the model sees answers from the exam while it is still practicing. Keeping similar English and Chinese reports in one split and checking example IDs protects the held-out evaluation.

---

# 8. Evaluation Task Expansion

The evaluation set has 30 pairs. To control cost while covering all four paths:

1. Deterministically assign 15 pairs to requested English output.
2. Assign the other 15 to requested Chinese output.
3. For each pair, run both source_en and source_zh using the same requested output.

Result:

| Input | Output | Planned task count |
|---|---|---:|
| English | English | 15 |
| Chinese | English | 15 |
| English | Chinese | 15 |
| Chinese | Chinese | 15 |
| **Total** |  | **60** |

Each task is run for three strategies. Self-refinement adds one initial call per task. The planned base semantic call count is 240, excluding transport retries and optional repair. This is a budget estimate, not an executed result.

Task IDs should include dataset version, scenario ID, source language, output language, and strategy. Never use a random UUID as the only identifier because resume logic needs stable identity.

## Explanation in Simple Words

Each held-out event is tested from both languages, but uses one chosen output language. Across all events, the four possible language directions appear equally often without doubling the experiment.

---

# 9. Reproducibility and Dataset Card

The manifest should include:

- dataset name/version;
- SHA-256 of JSONL;
- record/pair counts;
- counts by split/category/severity/certainty;
- author/reviewer method;
- translation review counts;
- creation date;
- license and source statement;
- schema version;
- validation script version/commit;
- known limitations;
- generation command for the CSV.

The dataset card should say:

- All reports are fictional/synthetic unless a later version explicitly documents permission.
- The data is intended for research/demo use.
- It does not certify operational safety.
- Labels contain subjective choices.
- Chinese is Simplified Chinese.
- Dataset size is small.
- Security-alert examples do not imply confirmed compromise.

Use deterministic ordering and UTF-8 with newline termination. For spreadsheet convenience, a CSV export may use UTF-8 with BOM, but JSONL remains canonical and its encoding policy must be documented.

## Explanation in Simple Words

The dataset card is a label for the dataset itself. It tells future users where the examples came from, how many there are, how they were checked, and what they should not be used to prove.

---

# 10. Sample Records and Coverage

Five complete paired sample records are provided in project_specification.md Section 6:

1. DS-SRV-001 - server failure with unknown cause.
2. DS-NET-001 - recovered network interruption after a switch reboot.
3. DS-DB-001 - database unavailable with cause under investigation.
4. DS-DEP-001 - deployment failure with checksum mismatch.
5. DS-MFG-001 - manufacturing press vibration warning.

Together they demonstrate:

- English/Chinese paired source text;
- exact evidence in each language;
- explicit and unknown causes;
- medium and high severity;
- safe action concepts;
- translation and ambiguity notes.

Before using them in the real dataset, assign final IDs/splits, conduct bilingual review, replace draft version with 1.0, and ensure any development sample is never used as an evaluation task.

## Explanation in Simple Words

The sample records show exactly what a finished data record looks like. They are still drafts and need the same review as the rest of the dataset.

---

# 11. Safety and Misleading Recommendation Controls

- Gold actions should be goals, not operational commands.
- Use “authorized,” “approved runbook,” and “qualified personnel” where the context is risky.
- Do not imply that a model action is mandatory.
- Do not provide physical repair procedures.
- Do not advise deleting logs, wiping systems, disabling monitoring, bypassing interlocks, or hiding a security event.
- For unknown cause, actions should focus on evidence and triage, not a guessed repair.
- For recovered incidents, include verification and data-gap assessment rather than pretending the incident is over.
- A security alert remains an alert unless evidence confirms an event.

Each record should contain safety_notes to help manual reviewers understand the dangerous inference to avoid.

## Explanation in Simple Words

The correct label must not teach unsafe behavior. It describes a safe direction, such as contacting the right team or following an approved procedure.

---

# 12. Dataset Validation Checklist

- [ ] Exactly 40 unique scenario IDs.
- [ ] Exactly 10 development and 30 evaluation pairs.
- [ ] Exactly four pairs per category.
- [ ] Both EN and ZH sources in every pair.
- [ ] Every enum is allowed.
- [ ] Every evidence span appears in the matching source.
- [ ] No empty gold concept labels.
- [ ] Unknown cause is not contradicted by a cause statement.
- [ ] Translation review status is recorded.
- [ ] No real personal/confidential identifier.
- [ ] No dangerous command in action concepts.
- [ ] Few-shot IDs are development-only.
- [ ] Similarity/leakage flags are adjudicated.
- [ ] UTF-8/NFC checks pass.
- [ ] JSONL is deterministic and valid line by line.
- [ ] CSV is regenerated, not hand-edited.
- [ ] Manifest counts equal source counts.
- [ ] SHA-256 and schema version recorded.
- [ ] Dataset card states synthetic nature and limits.
- [ ] Dataset v1 is frozen before the primary run.

## Explanation in Simple Words

This checklist is the final gate before the dataset becomes an exam. A failed item means the dataset should not be used for the main results yet.
