# Evaluation Plan

**Research question:** Which of zero-shot, few-shot, and one-cycle self-refinement produces the most accurate, consistent, grounded, and correctly structured results for bilingual industrial incident analysis without fine-tuning?  
**Status:** Method design only. No experiment has been run and no values in this document are project results.

---

# 1. Experimental Design

## 1.1 What Changes

Only the prompting strategy changes in the primary comparison:

- zero-shot;
- few-shot with one fixed development-only example bank;
- self-refinement with one initial and one combined review-and-correct semantic call.

## 1.2 What Stays Fixed

- evaluation task list and order policy;
- provider and model;
- model parameters, structured-output mode, and maximum tokens;
- schema and validation code;
- timeout/transport retry policy;
- optional syntax repair policy;
- prompt language modules and output schema;
- dataset, gold labels, and concept map;
- software commit and dependency environment.

## 1.3 Evaluation Tasks

The held-out evaluation contains 30 paired scenarios. Fifteen pairs request English output and fifteen request Chinese output. Both source languages are run for the same requested language within a pair. This produces 60 tasks balanced across four language paths.

Each strategy sees all 60 tasks. Strategy order should rotate deterministically per task, for example using a Latin-style rotation:

- task 1: zero, few, self;
- task 2: few, self, zero;
- task 3: self, zero, few;
- repeat.

This reduces the chance that one strategy always runs during a slower provider period.

## 1.4 Output Stages

Store these stages separately:

- raw first response;
- parsed first response if possible;
- validation issues;
- self-refinement initial response;
- self-refinement final response;
- optional syntax-repair response;
- final usable object;
- transport attempt history.

Primary strategy metrics use unassisted strategy outputs:

- zero-shot: first response;
- few-shot: first response;
- self-refinement: refined response.

Repair-assisted usability metrics are secondary.

## Explanation in Simple Words

A fair experiment changes the way the model is asked, while keeping the model, data, settings, and checks the same. It also saves failures instead of hiding them.

---

# 2. Metric Eligibility and Denominators

Before calculating a metric, define which records can be included:

- **All attempted tasks:** correct denominator for first-pass validity and failure rate.
- **Parsed schema-valid outputs:** correct denominator for category/severity accuracy.
- **Outputs with at least one returned evidence item:** one useful denominator for item-level grounding, accompanied by output-level coverage.
- **Matched scenario pairs with two eligible outputs:** correct denominator for bilingual consistency.
- **Manually reviewed outputs:** correct denominator for manual rubric and substantive hallucination.

Publish:

- numerator;
- denominator;
- percentage/value;
- number excluded;
- exclusion reason;
- metric source: automatic, manual, or optional judge;
- metric version.

Never calculate classification accuracy only on “nice-looking” successes without also showing validity/failure. A strategy that returns one correct category and 59 invalid objects is not a 100% successful system.

Recommended reporting contains two views:

1. **Conditional classification accuracy:** correct / schema-valid parsed outputs.
2. **End-to-end classification success:** correct and valid / all attempted tasks.

## Explanation in Simple Words

The denominator is the number underneath a fraction. Choosing it badly can make a weak system look strong. The report must say what was included and what failed.

---

# 3. Automatic Metrics

## 3.1 Category Accuracy

For eligible record i:

correct_category_i = 1 if predicted category equals gold category, otherwise 0.

category_accuracy = sum(correct_category_i) / N

Report conditional and end-to-end values, plus results by strategy, input language, output language, language path, and category.

## 3.2 Severity Accuracy

severity_accuracy = exact severity matches / eligible outputs

Also produce a confusion matrix with gold on rows and prediction on columns. Calculate macro recall by severity as a secondary measure if enough examples exist. Do not claim strong critical-severity conclusions from only a few examples.

## 3.3 Exact-Match Accuracy

Exact match is appropriate for:

- incident_category;
- severity;
- responsible_team;
- input_language;
- output_language;
- cause certainty.

For narrative strings, raw exact match is diagnostic only and should not be a headline metric.

## 3.4 Field-Level Precision, Recall, and F1

Use canonical gold concepts for symptoms and, as secondary analysis, action concepts.

For one field across records:

- TP: a predicted concept matches a gold concept.
- FP: a predicted concept has no gold match.
- FN: a gold concept is absent.

precision = TP / (TP + FP)  
recall = TP / (TP + FN)  
F1 = 2 × precision × recall / (precision + recall)

Primary field result: micro-F1, combining counts before calculation.  
Secondary result: macro-F1, averaging per-record F1 or per-concept F1 with the averaging choice stated.

Zero-denominator policy:

- If prediction and gold are both empty, record not_applicable rather than automatically perfect.
- If gold is non-empty and prediction empty, recall and F1 are 0.
- If prediction non-empty and gold empty, precision is 0; however version 1 should avoid required-empty symptom gold.

## 3.5 JSON Validity Rate

Define strict validity:

1. exactly one JSON object can be parsed under the documented fence policy;
2. object passes Pydantic;
3. extra fields are absent.

first_pass_json_validity = strict-valid primary first responses / attempted tasks

For self-refinement also report:

- initial_json_validity;
- refined_json_validity.

repair_assisted_validity = usable schema-valid outputs after one optional syntax repair / attempted tasks.

Never merge these into one unlabeled rate.

## 3.6 Required-Field Completion Rate

Define the required field set at schema version 1.0. A field is complete if:

- present;
- correct type;
- non-empty after trimming;
- list contains required minimum;
- unknown placeholder is allowed by that field and language.

Per record:

completion_i = complete_required_fields / total_required_fields

Report the macro average and per-field completion. Because schema-valid results should already be complete, this metric is especially useful on parsable but schema-invalid raw objects.

## 3.7 Evidence-Grounding Rate

Normalize source and quote with Unicode NFC only for comparison. Require the entire quote to appear as a substring. Do not translate or paraphrase evidence.

item_grounding_rate = grounded evidence items / all returned evidence items

output_grounding_coverage = outputs with at least one grounded evidence item / attempted tasks

fully_grounded_output_rate = outputs where every item is grounded and at least one item exists / attempted tasks

## 3.8 Hallucination Metrics

### Automatic Evidence-Quote Hallucination

evidence_quote_hallucination_rate = evidence items absent from source / all evidence items

This proves only that quotes were or were not copied from source.

### Manual Substantive Hallucination

Reviewers split narrative output into independently checkable factual claim units. Each unit is:

- supported;
- reasonable cautious recommendation, not a factual claim;
- unsupported;
- contradicted;
- unclear.

substantive_hallucination_rate = unsupported + contradicted factual units / all factual claim units

Report reviewer coverage and ambiguity. Do not calculate this automatically with simple keyword checks and call it truth.

## 3.9 Bilingual Consistency

For the same scenario and requested output language, compare the EN-source output with the ZH-source output.

Automatic weighted score:

- category agreement: 0 or 1, weight 0.30;
- severity agreement: 0 or 1, weight 0.20;
- team agreement: 0 or 1, weight 0.15;
- affected-system canonical concept agreement: 0 or 1, weight 0.15;
- symptom-concept F1 between the two outputs: 0 to 1, weight 0.20.

score = 0.30C + 0.20S + 0.15T + 0.15A + 0.20F

Report average across eligible pairs and number of pairs missing because one output failed. A high consistency score can mean the model is consistently wrong, so always pair it with gold accuracy.

Manual consistency for cause and actions:

- 0: meaning conflicts or one output invents major content;
- 1: mostly aligned with meaningful omissions/differences;
- 2: semantically aligned with only harmless wording differences.

## 3.10 Latency

Capture monotonic-clock latency:

- provider call latency per attempt;
- strategy semantic latency;
- total service latency including validation and allowed refinement/repair.

Report mean, median, p95, standard deviation, minimum, maximum, and N. Self-refinement must show total and per-call latency. Timeouts should remain failures and may be shown at timeout limit in a separate failure table, not silently removed from the experience discussion.

## 3.11 Failure Rate

primary_failure_rate = tasks without a valid primary strategy output / attempted tasks

Break down mutually exclusive primary reasons:

- authentication/configuration;
- rate-limit exhausted;
- timeout exhausted;
- provider/server exhausted;
- invalid JSON;
- schema;
- grounding;
- safety;
- failed refinement;
- unexpected internal.

If several issues occur, define a deterministic precedence and retain all secondary issue codes.

## Explanation in Simple Words

Automatic metrics check things computers can judge reliably: exact labels, JSON shape, copied evidence, time, and failures. They cannot fully decide whether a long cause or action is sensible.

---

# 4. Practical Evaluation of Text Fields

## 4.1 Canonical Concept Matching

Gold data gives symptoms and actions stable IDs with acceptable EN/ZH phrases. Prediction text is:

1. NFC normalized;
2. English lowercased;
3. whitespace collapsed;
4. compared with versioned acceptable phrases.

Do not stem Chinese with an English tokenizer. Do not allow very broad one-character matches. Review false positives during development only, then freeze the concept map.

## 4.2 Affected System

Automatically map expected phrases to one canonical affected-system concept. If multiple systems appear, use the primary gold concept. Manual review checks specificity and unsupported qualifiers.

## 4.3 Suspected Cause

Automatic:

- certainty enum exact match;
- unknown versus non-unknown;
- optional gold cause concept phrase coverage.

Manual:

- whether the model preserved the report’s uncertainty;
- whether it introduced causal explanation not present;
- whether wording is clear in requested language.

## 4.4 Recommended Actions

Automatic concept coverage is secondary because several safe actions may be valid. Manual review is primary for:

- relevance;
- immediate versus long-term placement;
- safety;
- reversibility;
- authorization awareness;
- absence of unsupported operational detail.

An output is not penalized merely for safe wording different from gold.

## 4.5 Similarity Scores

Lexical similarity, embeddings, or ROUGE can be included as exploratory diagnostics. They must not be treated as correctness:

- copying gold wording can score high while containing a dangerous addition;
- a correct translation can use different words;
- longer answers may gain overlap unfairly.

## Explanation in Simple Words

Long text can be correct in many different ways. The plan uses small meaning labels for automatic checks and a human rubric for the important details.

---

# 5. Manual Review Rubric

## 5.1 Blinding

Export outputs in random order with strategy/model labels hidden. Show report, requested language, gold labels, and model output. A reviewer should not know which strategy produced the answer.

## 5.2 Scoring

| Dimension | 0 - Poor | 1 - Partial | 2 - Strong |
|---|---|---|---|
| Affected system | wrong or invented | vague/partly specific | correct, supported, appropriately specific |
| Main symptoms | mostly missing/invented | some correct plus omissions/extras | important symptoms covered without invention |
| Suspected cause | unsupported or overconfident | partly faithful but weak qualification | faithful and correctly qualified, including unknown |
| Immediate actions | unsafe or irrelevant | useful but generic/incomplete | safe, relevant, reversible, authorization-aware |
| Long-term actions | unsafe or irrelevant | partly useful | relevant and realistically scoped |
| Evidence | absent/invented | some valid but key claim unsupported | exact spans support important fields |
| Confidence/uncertainty | misleading certainty | generic caveat | explains specific missing/uncertain facts |
| Output language | wrong or hard to understand | understandable with terminology issues | clear and consistent requested language |

## 5.3 Safety Flags

Separately mark:

- destructive data/system operation;
- unapproved restart/failover/isolation;
- credential handling;
- deletion/concealment of evidence;
- physical repair or safety-control bypass;
- claim of confirmed security compromise without evidence;
- other dangerous advice.

Any serious safety flag requires reviewer notes regardless of rubric total.

## 5.4 Claim Units

Example source: “The API returned 503 errors for ten minutes. Cause unknown.”

Output claim units:

1. API returned 503 errors - supported.
2. Outage lasted ten minutes - supported.
3. Database overload caused it - unsupported.
4. Notify application owner - cautious recommendation, not factual claim.

Substantive hallucination = 1 unsupported factual unit / 3 factual units = 33.3% for this fictional example.

## 5.5 Review Coverage and Agreement

Best plan:

- manually review all 180 primary outputs if feasible;
- otherwise review a stratified sample with equal strategy/language/category coverage;
- have a second reviewer independently score at least 20%;
- report exact agreement and weighted Cohen’s kappa for ordinal rubric scores if the sample supports it;
- resolve disagreements for a separate adjudicated analysis while preserving original scores.

If only one reviewer exists, state that clearly and do not report inter-rater reliability.

## Explanation in Simple Words

Human reviewers check the parts that formulas cannot understand well. Blinding hides the strategy name so reviewers are less likely to favor one method.

---

# 6. Optional LLM-as-a-Judge

An optional judge can apply the same rubric to report, gold, and prediction. It must be secondary.

Controls:

- use a separate prompt and version;
- hide strategy names;
- rotate output order if comparing two outputs;
- use temperature zero when available;
- save raw judge response;
- validate judge JSON;
- compare judge scores with human scores on a subset;
- report model/provider/date.

Risks:

- preference for writing style or verbosity;
- shared blind spots with the tested model;
- bias across English and Chinese;
- sensitivity to prompt order;
- inconsistent outputs;
- hidden model updates;
- circularity if the same model judges itself.

Never use a judge for deterministic JSON parsing or evidence containment.

## Explanation in Simple Words

Another LLM can help review many outputs, but it can also be wrong. It is an extra opinion, not the answer key.

---

# 7. Fair Comparison Procedure

## Before the Run

- [ ] Validate dataset/hash.
- [ ] Freeze prompts/example IDs/schema/concept map.
- [ ] Select provider/model and current pricing/privacy notes.
- [ ] Set temperature, max tokens, timeout, retries, structured-output mode.
- [ ] Create stable tasks and rotated strategy order.
- [ ] Record software commit and dependency snapshot.
- [ ] Estimate base call count and cost.
- [ ] Run complete fake-provider rehearsal.
- [ ] Define primary/secondary metrics before seeing results.

## During the Run

- [ ] Do not edit prompts/data/config.
- [ ] Save every attempt immediately.
- [ ] Preserve rate limits/timeouts/failures.
- [ ] Pause safely if quota or provider state changes.
- [ ] Resume only from matching manifest.
- [ ] Do not manually rerun a strategy because its output looks bad.

## After the Run

- [ ] Reconcile attempted/completed/failed counts.
- [ ] Calculate automatic metrics from immutable records.
- [ ] Export blinded manual-review queue.
- [ ] Complete and import review with rubric version.
- [ ] Generate processed tables and charts from code.
- [ ] Interpret differences with dataset-size caution.
- [ ] Archive manifest/raw/processed/report with commit.

## Explanation in Simple Words

The procedure freezes the rules before seeing the answers. This prevents quietly changing prompts or rerunning only bad examples until the preferred strategy wins.

---

# 8. Fictional Demonstration Calculations

The following numbers are invented only to show arithmetic.

## Example A - Accuracy

Suppose 50 outputs are schema-valid and 42 categories are correct:

42 / 50 = 0.84 = 84% conditional category accuracy.

If there were 60 attempted tasks:

42 / 60 = 0.70 = 70% end-to-end correct-and-valid category success.

## Example B - Field F1

Suppose symptom concepts across records produce:

- TP = 70
- FP = 10
- FN = 20

Precision = 70 / 80 = 0.875.  
Recall = 70 / 90 = 0.778.  
F1 = 2 × 0.875 × 0.778 / (0.875 + 0.778) = approximately 0.824.

## Example C - Evidence

Suppose a strategy returns 100 evidence quotes and 96 are exact substrings:

- item grounding rate = 96 / 100 = 96%;
- evidence-quote hallucination rate = 4 / 100 = 4%.

This does not prove that all narrative claims are grounded.

## Example D - Bilingual Consistency

Suppose one paired output has category=1, severity=1, team=0, system=1, symptom F1=0.75:

0.30(1) + 0.20(1) + 0.15(0) + 0.15(1) + 0.20(0.75) = 0.80.

The pair’s consistency score is 0.80. It may still be wrong against gold.

## Example E - Latency

For fictional latencies 2.0, 3.0, and 7.0 seconds:

mean = 12 / 3 = 4.0 seconds; median = 3.0 seconds.

The slow 7-second output shows why median and p95 should accompany mean in real results.

## Explanation in Simple Words

These examples teach how to calculate the metrics. They are not measurements of this project and must never be copied into a results section.

---

# 9. Analysis and Statistical Caution

The dataset is small. Recommended analysis:

- paired per-task metric differences between strategies;
- 95% bootstrap confidence intervals over scenario pairs as optional descriptive uncertainty;
- McNemar’s test for paired binary correctness only if assumptions/sample size are reasonable;
- Wilcoxon signed-rank for paired ordinal/manual scores as exploratory;
- effect size and raw difference over “winner” language.

Do not make many uncorrected significance tests across every subgroup. Subgroup values with only three category pairs per language assignment are descriptive. Report exact counts.

If repeated stochastic runs are affordable, repeat the entire manifest two or three times and treat run as another source of variability. Do not repeat only selected examples.

## Explanation in Simple Words

Small data can show interesting patterns, but tiny differences may be luck. The report should say “on this dataset” and show uncertainty instead of claiming universal superiority.

---

# 10. Results Tables and Charts

Required processed tables:

- overall primary metrics by strategy;
- assisted usability metrics by strategy;
- metrics by input language;
- metrics by language path;
- category and severity accuracy by category;
- failure taxonomy;
- self-refinement initial versus final;
- manual rubric dimensions;
- latency/call counts;
- bilingual consistency paired records.

Required charts:

- grouped bars for core metrics by strategy;
- category-strategy heatmap;
- severity confusion matrix per strategy or selectable;
- first-pass versus final validity;
- latency box/violin plot;
- failure reason stacked bars;
- EN/ZH input comparison;
- self-refinement issue fixed/introduced summary.

Every chart caption should identify:

- run ID/manifest;
- metric definition/version;
- denominator;
- whether value is automatic/manual/judge;
- whether error bars are present and what they mean.

## Explanation in Simple Words

Tables provide exact values and charts make patterns easier to see. Captions prevent a picture from losing important details such as how many examples were counted.

---

# 11. Evaluation Acceptance Checklist

- [ ] Research question and primary metrics were defined before results.
- [ ] All three strategies used the same frozen conditions.
- [ ] Few-shot examples are development-only.
- [ ] Self-refinement used exactly one correction cycle.
- [ ] Syntax repair is reported separately.
- [ ] All four language paths have equal task counts.
- [ ] Failed tasks remain in validity/failure denominators.
- [ ] Conditional and end-to-end classification views are both available.
- [ ] Evidence grounding is not called total hallucination.
- [ ] Manual review is blinded and versioned.
- [ ] Optional judge results are labeled optional.
- [ ] Numerator/denominator/exclusions appear with metrics.
- [ ] Latency includes mean, median, and p95.
- [ ] Raw outputs and manifest are archived.
- [ ] Fictional examples are not included as real results.
- [ ] Conclusions say “on this dataset” and state limitations.

## Explanation in Simple Words

The acceptance checklist protects the experiment from common mistakes. If an item fails, fix the method or clearly mark the run exploratory before publishing.
