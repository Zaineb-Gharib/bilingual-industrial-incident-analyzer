# GitHub Publication Plan

**Status:** Planning only  
**Rule:** Do not publish until implementation, real testing, a frozen evaluation, and the gates below are complete.

---

# 1. Publication Goal

The repository should demonstrate:

- provider-neutral LLM engineering;
- bilingual structured extraction;
- Pydantic validation and grounding;
- prompt-strategy experimentation without fine-tuning;
- reproducible small-dataset evaluation;
- thoughtful failure, privacy, and safety design;
- beginner-friendly documentation and tests.

The public story is not “AI solves incidents.” It is “a carefully scoped prototype explores how prompting affects bilingual, grounded incident structuring.”

## Explanation in Simple Words

GitHub should show both engineering and honest research. The project is valuable because it checks the model and explains limits, not because it claims to replace incident responders.

---

# 2. Required Repository Contents

## Code and Configuration

- application entry and five Streamlit pages;
- source packages described in the repository structure;
- one reference provider adapter plus fake provider;
- versioned prompt files and development-only examples;
- schema, validators, storage, evaluation, and logging;
- scripts for dataset validation, evaluation, result export, and secret checking;
- pyproject.toml and requirements.txt;
- .env.example with names and blank/harmless values;
- .gitignore;
- license and changelog.

## Data and Results

- versioned synthetic paired dataset;
- dataset card/manifest/hash;
- example safe outputs;
- frozen run manifest;
- record-level results only if safe and licensing/privacy review allows;
- processed tables and generated charts;
- manual review rubric and coverage;
- explicit separation between demonstration fixtures and real measured results.

## Documentation

- README;
- install/config/demo instructions;
- architecture and diagrams;
- dataset method and leakage controls;
- evaluation formulas and repair policy;
- actual results after execution;
- limitations, ethics, privacy, and safety;
- tests and reproducibility;
- all planning documents, updated if the build differs.

## Visuals

- only real screenshots from the running app;
- only charts generated from archived results;
- alt text and concise captions;
- no key, private input, or misleading placeholder value.

## Explanation in Simple Words

A complete repository contains more than application code. It also contains the data rules, experiment record, tests, safety information, and real proof that the app runs.

---

# 3. Proposed README Outline

## Header

- Title: Bilingual Industrial Incident Analyzer.
- One-sentence description.
- Status: Research prototype.
- Badges only for real CI/test/license state.
- Prominent decision-support and sanitized-data notice.

## Demo

- One real screenshot.
- Short EN/ZH example.
- Link to additional screenshots.
- Optional short GIF only if it comes from the real app and remains readable.

## Features

- four language paths;
- structured Pydantic-validated JSON;
- exact source evidence;
- three prompt strategies;
- self-refinement trace;
- batch evaluation and dashboard;
- provider abstraction and offline fakes.

## How It Works

- small architecture diagram;
- report → prompt → provider → validation → storage → evaluation;
- concise layer explanation.

## Prompt Strategies in Simple Words

- zero-shot;
- few-shot;
- one-cycle self-refinement;
- research question.

## Quick Start

1. Clone.
2. Create/activate virtual environment.
3. Install.
4. Copy .env.example to .env.
5. Run fake/demo mode without a key.
6. Run Streamlit.

Then add a separate live-provider section with quota/privacy warning.

## Configuration

- variable table;
- provider/model selection;
- timeout/retry;
- raw storage default;
- key safety;
- no hard-coded current model claims without date/version.

## Dataset

- 40 paired scenarios / 80 language records;
- 10 categories;
- development/evaluation split;
- synthetic status;
- translation review;
- leakage controls;
- link to dataset card/manifest.

## Evaluation

- 60 held-out tasks;
- four balanced language paths;
- fixed comparison controls;
- primary and secondary metrics;
- manual review;
- repair-assisted metrics separate;
- exact run manifest.

## Actual Results

This section stays clearly marked “Pending implementation and evaluation” until a real run. Later include:

- table by strategy;
- best/worst findings;
- language/category breakdown;
- failure counts;
- latency/call count;
- manual review coverage;
- run/model/prompt/dataset versions;
- limitations and no exaggerated winner claim.

## Reproduction

- dataset validation command;
- offline test command;
- evaluation command;
- processed table/chart generation;
- expected file locations;
- non-determinism note.

## Testing

- fake-provider default;
- test categories;
- live_api marker opt-in;
- latest real CI status only.

## Privacy, Safety, Ethics, and Limitations

- no confidential reports;
- provider privacy terms;
- hallucinated root causes;
- unsafe advice risk;
- human review;
- synthetic data and bilingual bias;
- prompt injection;
- decision-support disclaimer.

## Repository Structure

Use a shortened tree and link to documentation for details.

## Roadmap

Only genuine planned improvements, not promises.

## License and Contact

- selected license;
- dataset licensing statement;
- portfolio author/contact;
- acknowledgments without suggesting endorsement.

## Explanation in Simple Words

The README first helps a recruiter understand the project, then helps a developer run it, and finally explains how the experiment and limits work.

---

# 4. Screenshot Checklist

All screenshots must be captured from the real app on a known commit using fictional reports.

| Screenshot | Required content | Privacy/accuracy check |
|---|---|---|
| Home/project info | title, goal, workflow, warning | no “production-ready” claim |
| EN analysis | English source/result/evidence | synthetic example ID recorded |
| ZH analysis | Chinese source/result/evidence | glyphs render cleanly |
| Cross-language | EN→ZH or ZH→EN; source evidence unchanged | no translated evidence presented as quote |
| Strategy comparison | common settings and three outputs | real live/fake status labeled |
| Validation warning | deliberately invalid fixture or genuine failed output | clearly label test fixture if fake mode |
| Batch evaluation | manifest/progress or completed counts | counts match archived run |
| Dashboard | headline metrics with denominators | actual run only |
| Charts | one or more readable plots | generated from processed results |
| Project information | limitations/ethics/future work | warning visible |

For each image, store a small manifest entry:

- filename;
- commit;
- app mode;
- scenario/run ID;
- capture date;
- crop/redaction note;
- alt text.

Do not use design wireframes as implementation screenshots. Do not type invented results into the UI to make a dashboard look complete.

## Explanation in Simple Words

A screenshot is evidence of the real application. Recording the commit and example makes it possible to reproduce and trust the image.

---

# 5. Secret and Privacy Review

## Files That Must Be Ignored

- .env and variants except .env.example;
- local SQLite databases and journal files;
- local/private/raw report folders;
- Python caches and virtual environments;
- IDE settings where not intentionally shared;
- test coverage output;
- provider SDK caches;
- unreviewed raw evaluation exports if they contain sensitive metadata.

## Checks Before First Push

- scan working tree and staged content;
- scan Git history for common key formats and high-entropy strings;
- search for api_key, authorization, bearer, secret, password;
- inspect notebooks, screenshots, logs, fixtures, and shell history copied into docs;
- confirm .env.example has no plausible secret;
- confirm errors/log examples do not include request headers;
- inspect Git remote and repository visibility.

If a real secret was ever committed, deleting the line is not enough. Revoke/rotate the secret and clean history using an appropriate reviewed process before publication.

## Data Privacy

- Publish only synthetic dataset reports.
- Review record-level provider metadata for account/project identifiers.
- Hash or remove provider request IDs if they create an unnecessary disclosure.
- Do not publish ad hoc user inputs.
- State provider privacy considerations based on current official terms at implementation time.

## Explanation in Simple Words

Secrets can hide in logs, screenshots, history, and test files. A final search of only the current .env file is not enough.

---

# 6. Licensing and Attribution

Deferred implementation decision:

- MIT is short/permissive.
- Apache-2.0 adds an explicit patent grant.

This is not legal advice. Before choosing:

- confirm provider SDK licenses;
- confirm copied snippets/assets have compatible terms;
- state that the synthetic dataset is original;
- choose a dataset license or apply repository license explicitly;
- attribute third-party icons/fonts/templates;
- do not include proprietary incident content.

The README should distinguish code license, dataset license, and third-party dependencies if they differ.

## Explanation in Simple Words

A license tells other people what they may do with the code and data. The author must also respect the licenses of anything reused.

---

# 7. Results Publication Rules

Before adding any metric:

1. Identify archived run ID and manifest hash.
2. Confirm prompt/schema/dataset/model/version.
3. Generate the value from code, not manual spreadsheet editing.
4. Include numerator/denominator and failure count.
5. Label metric as automatic/manual/optional judge.
6. State whether syntax repair is included.
7. State evaluation size and synthetic-data limitation.
8. Link to the exact processed table or reproduction command.

Allowed wording:

- “On the 60-task held-out synthetic evaluation…”
- “Few-shot produced a higher observed first-pass JSON validity than zero-shot in run X…”
- “The difference is descriptive because the dataset is small.”

Avoid:

- “The model accurately diagnoses industrial incidents.”
- “Self-refinement is proven best.”
- “Safe recommendations” without manual safety evidence and limits.
- “Hallucination-free.”

## Explanation in Simple Words

Real numbers still need context. The repository should say which small dataset and run produced them and avoid turning one experiment into a universal promise.

---

# 8. GitHub Metadata and Portfolio Polish

Recommended repository name:

bilingual-industrial-incident-analyzer

Suggested description:

“Provider-neutral Streamlit research prototype for validated EN/ZH industrial incident structuring and prompt-strategy evaluation.”

Possible topics:

- llm
- prompt-engineering
- bilingual-nlp
- structured-output
- pydantic
- streamlit
- evaluation
- industrial-ai
- python

Use:

- a clean social preview based on the real app or a simple title graphic that contains no metric;
- issue templates only if the author plans to maintain them;
- a small contributing guide if accepting contributions;
- CI for offline tests, lint, and dataset validation;
- Dependabot or similar only if the maintenance burden is acceptable.

Do not add badges that are not connected to real checks.

## Explanation in Simple Words

Names, topics, and a concise description help recruiters find and understand the repository. Badges and previews must reflect real project state.

---

# 9. Release Sequence

## Stage A - Private Local Build

- Implement and test in fake mode.
- Create/review dataset.
- Freeze experiment inputs.
- Run controlled live evaluation.

## Stage B - Private Repository Review

- Push only after secret scan.
- Run CI.
- Review rendering, links, data, results, and screenshots.
- Ask a second person to follow quick start if possible.

## Stage C - Public Candidate

- Prepare v1.0.0-rc notes.
- Clean-clone verification.
- Confirm current provider documentation links.
- Check CV wording against actual state.

## Stage D - Public v1.0.0

- Change visibility/publish.
- Verify signed-out view.
- Tag release.
- Save release commit and archive in CV records.

## Stage E - Maintenance

- Record model/provider changes.
- Keep old result manifests.
- Do not silently replace old results after prompt/data changes.
- Update limitations when new evidence appears.

## Explanation in Simple Words

Publication happens in stages so mistakes can be caught while the repository is still private. Old results stay connected to the old version that created them.

---

# 10. Final Publication Gate

## Security

- [ ] No API key or secret in current tree/history.
- [ ] .env is ignored; .env.example is harmless.
- [ ] No private input/database/log.
- [ ] Screenshots contain no sensitive data.
- [ ] Provider request metadata is reviewed.

## Correctness

- [ ] Offline tests and dataset validation pass.
- [ ] Clean clone works.
- [ ] All five pages load.
- [ ] Live evaluation uses frozen manifest.
- [ ] Counts and metrics reconcile.
- [ ] Charts regenerate from processed data.

## Research Integrity

- [ ] No fabricated result or screenshot.
- [ ] Demonstration fixtures are labeled.
- [ ] First-pass and repaired metrics are separate.
- [ ] Failure counts and denominators are visible.
- [ ] Manual/judge provenance is visible.
- [ ] Conclusions are limited to this dataset/run.

## Documentation

- [ ] README follows outline.
- [ ] Installation/config/demo commands are current.
- [ ] Architecture diagrams render and have text alternatives.
- [ ] Dataset/evaluation/limitations/ethics are documented.
- [ ] License and attribution are present.
- [ ] Placeholder CV/results values are removed or still clearly pending.

## Portfolio Quality

- [ ] Real screenshots are clear and reproducible.
- [ ] Social preview and repository description are accurate.
- [ ] Topics are relevant.
- [ ] CV entry matches actual completion state.
- [ ] Repository is visibly different from a security code-generation project.

Publication is approved only when every required item is checked or a documented exception is visible in the README.

## Explanation in Simple Words

The gate is the last “stop and check” moment. Publishing should wait if secrets, broken instructions, missing tests, or invented results remain.
