# UI Wireframes

**Framework:** Streamlit  
**Status:** Planning wireframes, not screenshots  
**Important:** These boxes are layout sketches. Public screenshots must later be captured from the real running application.

---

# 1. Design Principles

- Start with the user’s task, not model settings.
- Keep the safety/privacy warning visible but concise.
- Display evidence and uncertainty near the conclusion.
- Use icons plus text; never rely only on red/green.
- Keep raw/provider metadata in expanders.
- Preserve readable Chinese wrapping and UTF-8 downloads.
- Thin pages call services; the UI does not parse JSON or implement retry logic.
- If a result is invalid, do not beautify it into appearing valid.

## Explanation in Simple Words

The screen should make the result easy to read without hiding risks. Advanced details are available, but a beginner does not need to understand them before running a safe example.

---

# 2. Global Shell

~~~text
┌─────────────────────────────────────────────────────────────────────────────┐
│ Bilingual Industrial Incident Analyzer                                     │
│ Research prototype: structures EN/ZH incident reports with source evidence │
├──────────────────────┬──────────────────────────────────────────────────────┤
│ NAVIGATION           │ ⚠ Use fictional or sanitized reports only.          │
│ ○ Single Analysis    │ This tool does not confirm root cause or authorize   │
│ ○ Compare Strategies │ operational action. Human review is required.        │
│ ○ Batch Evaluation   │                                                      │
│ ○ Results Dashboard  │ [CURRENT PAGE CONTENT]                               │
│ ○ Project Info       │                                                      │
│                      │                                                      │
│ CONFIGURATION        │                                                      │
│ Provider: configured │                                                      │
│ Model: model-name    │                                                      │
│ Prompt: v1           │                                                      │
│ Schema: 1.0          │                                                      │
│ Mode: FAKE / LIVE    │                                                      │
└──────────────────────┴──────────────────────────────────────────────────────┘
~~~

Global behavior:

- In live mode, show a quota/cost notice without displaying a key.
- If configuration is invalid, show a safe sidebar status and disable call buttons.
- On every page, place a short footer with project status, commit if known, and decision-support notice.

## Explanation in Simple Words

The left side shows where the user is and which model setup is active. The top warning reminds users not to paste private company information.

---

# 3. Single Incident Analysis

## 3.1 Empty State

~~~text
┌─────────────────────────────────────────────────────────────────────────────┐
│ Single Incident Analysis                                                    │
│ Paste a short English or Chinese incident report.                           │
│                                                                             │
│ Incident report                                                   0 / 4000  │
│ ┌─────────────────────────────────────────────────────────────────────────┐ │
│ │ Example: The order API began returning 503 errors...                    │ │
│ │                                                                         │ │
│ └─────────────────────────────────────────────────────────────────────────┘ │
│ Detected language: shown after typing (English / Chinese / Mixed / Unknown) │
│                                                                             │
│ Output language:  (●) English  ( ) 简体中文                                 │
│ Prompt strategy: [ Zero-shot ▼ ]                                           │
│ Privacy: [✓] Do not store raw ad hoc report                                │
│                                                                             │
│ [ Analyze incident ]                                                        │
│                                                                             │
│ What you will receive: category, severity, system, symptoms, cautious       │
│ actions, exact evidence, and uncertainty.                                   │
└─────────────────────────────────────────────────────────────────────────────┘
~~~

Validation behavior:

- Empty or shorter-than-minimum: inline hint; button disabled.
- Over 4,000 characters: show exact excess count and no API call.
- Likely prompt-injection phrases: informational warning only; the report remains analyzable under the untrusted-data policy.

## 3.2 Loading State

~~~text
┌─────────────────────────────────────────────────────────────────────────────┐
│ ⏳ Analyzing with zero-shot…                                                 │
│ Step: calling configured model                                              │
│ Do not submit again. The request has correlation ID ABC123.                 │
└─────────────────────────────────────────────────────────────────────────────┘
~~~

Do not simulate percent completion for one provider call. A spinner and named stage are more honest.

## 3.3 Valid Result

~~~text
┌─────────────────────────────────────────────────────────────────────────────┐
│ ✓ Valid with 1 warning                       Result ID: analysis-…           │
├───────────────────────────────┬─────────────────────────────────────────────┤
│ Incident title                │ Order database unavailable                  │
│ Category                      │ Database failure                            │
│ Severity                      │ HIGH · urgent expert review                 │
│ Affected system               │ Order service database                      │
│ Responsible team              │ Database operations                         │
├───────────────────────────────┴─────────────────────────────────────────────┤
│ Main symptoms                                                               │
│ • Database connection errors                                                │
│ • Database status page reports unavailable                                  │
│                                                                             │
│ Suspected cause                                                             │
│ Unknown · The source says investigation is still in progress.               │
├─────────────────────────────────────────────────────────────────────────────┤
│ Recommended immediate actions                                               │
│ 1. Notify the authorized database team.                                     │
│    Why: the database is reported unavailable. Authorization required: Yes   │
│ 2. Preserve application and database logs.                                  │
│                                                                             │
│ Recommended long-term actions                                               │
│ • Complete a root-cause review after recovery.                              │
├─────────────────────────────────────────────────────────────────────────────┤
│ Source evidence                                                             │
│ “returning database connection errors” → symptoms                           │
│ “database status page shows unavailable” → severity/system                  │
│ “root cause is under investigation” → cause uncertainty                     │
├─────────────────────────────────────────────────────────────────────────────┤
│ Confidence: MEDIUM                                                          │
│ The report clearly states symptoms but does not state a cause.               │
│                                                                             │
│ ⚠ Warning: Severity requires human confirmation from actual impact.         │
│                                                                             │
│ [ Download UTF-8 JSON ]  [ Analyze another ]                                │
│ ▸ Technical details (model, prompt hash, latency, validation, raw response) │
└─────────────────────────────────────────────────────────────────────────────┘
~~~

Evidence is always shown in original source language. Cross-language narrative does not translate evidence.

## 3.4 Invalid Result

~~~text
┌─────────────────────────────────────────────────────────────────────────────┐
│ ✕ Result not accepted                                                       │
│ The model returned one evidence quote that is not present in the report.     │
│                                                                             │
│ Error code: EVIDENCE_NOT_IN_SOURCE                                          │
│ What to do: Retry once, choose another strategy, or inspect diagnostic data.│
│ No grounded result is available for download.                               │
│                                                                             │
│ [ Try again ] [ Compare strategies ]                                        │
│ ▸ Invalid diagnostic output (clearly labeled; raw text only)                │
└─────────────────────────────────────────────────────────────────────────────┘
~~~

Do not show a large green severity/category header above an invalid result.

## 3.5 Self-Refinement Details

~~~text
┌─────────────────────────────────────────────────────────────────────────────┐
│ Self-refinement trace                                                       │
│ Initial: ✕ 2 validation issues · 2.4 s                                      │
│ Final:   ✓ valid with warning · 2.8 s                                       │
│ Total semantic latency: 5.2 s · Semantic calls: 2                           │
│                                                                             │
│ Changed fields                                                              │
│ • suspected_cause: overconfident → unknown                                  │
│ • evidence[1]: invalid quote removed/replaced with exact source quote        │
│                                                                             │
│ ▸ Initial answer   ▸ Validator warnings   ▸ Final answer                    │
└─────────────────────────────────────────────────────────────────────────────┘
~~~

## Explanation in Simple Words

The single page gathers one report and shows a structured answer. An invalid answer is displayed as a failure, while self-refinement shows both the first and corrected versions.

---

# 4. Prompt Strategy Comparison

## 4.1 Input

Reuse the report box and output-language controls. Model settings are locked for all three strategies. Display: “This action may make four semantic calls: zero-shot 1, few-shot 1, self-refinement 2, before transport retries/optional repair.”

## 4.2 Summary

~~~text
┌─────────────────────────────────────────────────────────────────────────────┐
│ Prompt Strategy Comparison                                                  │
│ Same report · Same model/settings · Requested output: English               │
├──────────────────┬───────────────┬───────────────┬───────────────────────────┤
│ Metric           │ Zero-shot     │ Few-shot      │ Self-refinement           │
├──────────────────┼───────────────┼───────────────┼───────────────────────────┤
│ Primary validity │ ✓ Valid       │ ✕ Invalid     │ ✓ Valid                   │
│ Final usability  │ ✓             │ ✓ after repair│ ✓                         │
│ Latency          │ 2.1 s         │ 2.7 s         │ 5.4 s total               │
│ Completion       │ 100%          │ 92% first     │ 100%                      │
│ Grounded quotes  │ 3 / 3         │ 2 / 3         │ 3 / 3                     │
│ Warnings         │ 1             │ 2             │ 0                         │
│ Semantic calls   │ 1             │ 1             │ 2                         │
└──────────────────┴───────────────┴───────────────┴───────────────────────────┘
│ These example values are UI placeholders until a real run exists.           │
└─────────────────────────────────────────────────────────────────────────────┘
~~~

Implementation must populate the table from real current responses. During development, use visibly labeled fake fixtures. Never reuse the placeholder numbers above in public results.

## 4.3 Output Tabs

~~~text
┌─────────────────────────────────────────────────────────────────────────────┐
│ [ Zero-shot ] [ Few-shot ] [ Self-refinement ] [ Field differences ]        │
│                                                                             │
│ Selected strategy full structured output…                                  │
│ Evidence… Warnings… Technical details…                                     │
└─────────────────────────────────────────────────────────────────────────────┘
~~~

Field differences should use a table:

| Field | Zero-shot | Few-shot | Self-refinement | Agreement |
|---|---|---|---|---|
| category | database_failure | database_failure | database_failure | 3/3 |
| severity | high | medium | high | 2/3 |

For narrative fields, display text side by side and call similarity “comparison aid,” not accuracy.

## Explanation in Simple Words

The comparison page sends the same report through all three methods. It compares shape, evidence, time, and differences, but it does not assume that two agreeing models are correct.

---

# 5. Batch Evaluation

## 5.1 Pre-Run Manifest

~~~text
┌─────────────────────────────────────────────────────────────────────────────┐
│ Batch Evaluation                                                            │
│ Dataset: BIIA-80 v1 · Evaluation: 30 pairs / 60 tasks                       │
│ Dataset hash: abcd… · Prompt: v1 · Schema: 1.0                              │
│ Model: configured-model · Temperature: 0 · Strategy order: rotated          │
│                                                                             │
│ Language paths: EN→EN 15 · ZH→EN 15 · EN→ZH 15 · ZH→ZH 15                 │
│ Planned strategy outputs: 180                                               │
│ Planned base semantic calls: 240                                            │
│ Actual calls may be higher because of bounded retries/repair.                │
│                                                                             │
│ [ ] I understand that live evaluation may consume API quota.                │
│ [ Create frozen manifest ]  [ Start run ]                                   │
└─────────────────────────────────────────────────────────────────────────────┘
~~~

The Start button is disabled until the manifest is saved and confirmation is checked in live mode.

## 5.2 Running/Resume

~~~text
┌─────────────────────────────────────────────────────────────────────────────┐
│ Run: run-2026…                                   Status: RUNNING             │
│ [█████████████████░░░░░░░░░░░░░░] 96 / 180 strategy outputs                │
│ Complete 92 · Failed 4 · Pending 84 · Transport attempts 102                │
│ Current: EV-STO-003 / Chinese input / English output / few-shot              │
│                                                                             │
│ [ Stop after current task ]                                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│ Recent failures                                                             │
│ Task       Strategy       Code                         Retry state           │
│ …          zero-shot      INVALID_JSON                 terminal primary      │
│ …          self-refine    TIMEOUT_EXHAUSTED             terminal              │
└─────────────────────────────────────────────────────────────────────────────┘
~~~

After refresh, show Resume only when the current configuration matches the frozen manifest.

## 5.3 Complete

~~~text
┌─────────────────────────────────────────────────────────────────────────────┐
│ ✓ Batch complete                                                            │
│ Attempted 180 · Primary valid  [real count] · Failed [real count]           │
│ Manual review remaining: [real count]                                       │
│                                                                             │
│ [ Open dashboard ] [ Export record JSONL ] [ Export CSV ] [ Review queue ] │
│ ▸ Manifest and reproducibility details                                      │
└─────────────────────────────────────────────────────────────────────────────┘
~~~

## Explanation in Simple Words

The batch page tells the researcher how much work and possible API use is planned. It saves every result so a stopped run can continue safely.

---

# 6. Results Dashboard

## 6.1 Filters and Metric Cards

~~~text
┌─────────────────────────────────────────────────────────────────────────────┐
│ Results Dashboard                                                           │
│ Run [run-… ▼] Strategy [All ▼] Input [All ▼] Output [All ▼] Category [All]│
│ Metric source [Automatic ▼]                                                 │
├──────────────────┬──────────────────┬──────────────────┬────────────────────┤
│ Category accuracy│ Severity accuracy│ JSON validity    │ Evidence grounding │
│ [value]          │ [value]          │ [value]          │ [value]            │
│ n/N shown        │ n/N shown        │ first-pass       │ exact quotes       │
├──────────────────┴──────────────────┴──────────────────┴────────────────────┤
│ Failure rate     │ Bilingual consistency │ Median / p95 latency              │
│ [value and n/N]  │ [value, eligible pairs]│ [seconds]                        │
└─────────────────────────────────────────────────────────────────────────────┘
~~~

No reviewed manual data:

~~~text
Manual hallucination rate: Not available
Reason: manual review has not been completed for the selected run.
~~~

Do not display 0%.

## 6.2 Charts

~~~text
┌─────────────────────────────────────┬───────────────────────────────────────┐
│ Core metrics by strategy            │ Category accuracy heatmap             │
│ [grouped bar chart]                 │ [categories × strategies]             │
├─────────────────────────────────────┼───────────────────────────────────────┤
│ Latency distribution                │ Failure reasons                       │
│ [box/violin plot]                   │ [stacked bars with counts]             │
├─────────────────────────────────────┴───────────────────────────────────────┤
│ Severity confusion matrix · selectable strategy                            │
│ [matrix]                                                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│ Metric detail table                                                        │
│ metric · numerator · denominator · exclusions · source · version           │
│ [ Download filtered table ]                                                 │
└─────────────────────────────────────────────────────────────────────────────┘
~~~

Chart requirements:

- tooltips contain n/N;
- rate axes use consistent 0-100% scale when comparing;
- missing data is blank/annotated, never zero-filled;
- strategy colors are consistent and accessible;
- captions mention run ID and metric source.

## Explanation in Simple Words

The dashboard shows both a quick summary and exact supporting counts. Filters help find language or category weaknesses. Missing manual review is shown as missing, not as perfect performance.

---

# 7. Project Information

~~~text
┌─────────────────────────────────────────────────────────────────────────────┐
│ About This Project                                                          │
│                                                                             │
│ Goal                                                                        │
│ Convert short EN/ZH reports into validated structured data and compare      │
│ three prompting methods without fine-tuning.                                │
│                                                                             │
│ [ How it works diagram ]                                                    │
│                                                                             │
│ Prompt strategies                                                          │
│ Zero-shot: instructions without examples                                    │
│ Few-shot: instructions plus a few development examples                      │
│ Self-refinement: initial answer plus one review-and-correct cycle            │
│                                                                             │
│ ▾ Dataset and evaluation                                                    │
│ ▾ Limitations                                                               │
│ ▾ Privacy, ethics, and safety                                               │
│ ▾ Future work                                                               │
│                                                                             │
│ ⚠ Research and decision-support only. Human review is required.             │
└─────────────────────────────────────────────────────────────────────────────┘
~~~

Link to repository documentation after publication. Before publication, avoid broken GitHub links.

## Explanation in Simple Words

The information page teaches a visitor what the project does and what its results do not prove. It is important for recruiters and first-time users.

---

# 8. Responsive and Accessibility Notes

- On wide screens, comparison may use three columns; on narrow screens, use tabs.
- Tables should allow horizontal scrolling rather than tiny text.
- Evidence and Chinese text should wrap naturally.
- Use semantic headings in order.
- Every input has a visible label and help text.
- Status is icon plus word: ✓ Valid, ⚠ Warning, ✕ Invalid.
- Charts have titles, captions, tooltips, and downloadable tables.
- Color contrast should meet WCAG AA where controllable.
- Avoid flag icons; languages are not countries.
- Do not use all caps for Chinese labels.
- Keyboard focus and button order should follow visual order.

## Explanation in Simple Words

Responsive design keeps the app usable on smaller screens. Accessibility rules help people who use keyboards, screen readers, or cannot rely on color.

---

# 9. UI State Matrix

| Page | State | Required behavior |
|---|---|---|
| Single | empty | guidance and disabled submit |
| Single | invalid input | inline error, zero provider calls |
| Single | loading | spinner, current stage, double-submit guard |
| Single | valid | structured fields, evidence, warning, download |
| Single | invalid output | clear failure, diagnostic expander |
| Single | provider error | safe retry/config guidance |
| Compare | ready | call estimate and locked common settings |
| Compare | partial failures | keep successful tabs and show failures |
| Batch | no manifest | preview and confirmation |
| Batch | running | progress, recent failures, stop-after-current |
| Batch | interrupted | matching-manifest resume |
| Batch | complete | exports, dashboard, review queue |
| Dashboard | no run | informative empty state |
| Dashboard | filtered empty | explain no eligible records |
| Dashboard | partial manual review | show reviewed N and missing state |
| Info | normal | project explanation and safety limits |

## Explanation in Simple Words

Screens need designs for errors and empty data, not only success. The state matrix tells the coding agent what the user should see in each situation.

---

# 10. Screenshot Plan for Later

Capture from the real running app:

- [ ] Project/home information.
- [ ] English input and English output.
- [ ] Chinese input and Chinese output.
- [ ] One cross-language analysis.
- [ ] Three-strategy comparison.
- [ ] Invalid evidence warning.
- [ ] Batch manifest and completed run.
- [ ] Results dashboard overview.
- [ ] One readable chart.
- [ ] Limitations/safety information.

Each screenshot must use synthetic data, display no key, record its commit/example/run, and avoid fabricated values.

## Explanation in Simple Words

These wireframes are not screenshots. Real screenshots come later, after the application is built and the shown results genuinely exist.
