# Screenshot Manifest

Screenshots are captured from the real local Streamlit application with synthetic dataset
examples. All current captures use the deterministic demo provider and must visibly display
the demo label. The application commit, capture date, route, example/scenario ID, language
path, and strategy are recorded beside each image after capture.

No mockup, generated design, real credential, confidential identifier, or claimed live LLM
result is permitted in this folder.

## Verified captures

Capture date: 2026-07-14. Resolution: 1280×720 JPEG. Provider/model for every result:
deterministic `demo` / `demo-v1` (**not an LLM**).

| File | Route / state | Scenario or run | Path / strategy | Source commit |
|---|---|---|---|---|
| `01_home_demo.jpg` | Home and safety notice | — | — | `923e654` |
| `02_english_en_zero_shot_result_demo.jpg` | Analyze controls and accepted result | `DEV-DBF-001` | en→en / zero-shot | `923e654` |
| `03_english_en_zero_shot_evidence_warning_demo.jpg` | Analyze result summary | `DEV-DBF-001` | en→en / zero-shot | `923e654` |
| `04_validation_warning_and_evidence_demo.jpg` | Evidence, validation, uncertainty, download | `DEV-DBF-001` | en→en / zero-shot | `923e654` |
| `05_chinese_zh_few_shot_input_demo.jpg` | Chinese input and controls | `DEV-DEP-001` | zh→zh / few-shot | `ce4a0ac` |
| `06_chinese_zh_few_shot_result_demo.jpg` | Accepted Chinese result | `DEV-DEP-001` | zh→zh / few-shot | `ce4a0ac` |
| `07_cross_language_zh_en_self_refinement_demo.jpg` | Cross-language input | `DEV-DEP-001` | zh→en / self-refinement | `ce4a0ac` |
| `08_cross_language_self_refinement_result_demo.jpg` | Cross-language refined result and two-call count | `DEV-DEP-001` | zh→en / self-refinement | `ce4a0ac` |
| `09_cross_language_en_zh_result_demo.jpg` | Accepted cross-language result | `DEV-DBF-001` | en→zh / zero-shot | `ce4a0ac` |
| `10_strategy_comparison_demo.jpg` | Controlled three-strategy comparison | `EVAL-NET-003` | en→en / all strategies | `ce4a0ac` |
| `11_strategy_comparison_metrics_demo.jpg` | Comparison call, retry, latency, validation metrics | `EVAL-NET-003` | en→en / all strategies | `ce4a0ac` |
| `12_batch_prepared_request_estimate_demo.jpg` | Frozen development batch estimate | prepared run | all paths / all strategies | `ce4a0ac` |
| `13_batch_completed_artifacts_demo.jpg` | Completed batch and downloadable artifacts | `run-fd6f0e802fcb401ba6d9fa37ea52f3f6` | all paths / all strategies | `ce4a0ac` |
| `14_dashboard_heldout_metrics_demo.jpg` | Persisted held-out metric summary | `run-7343b258a9b64a77bc4716bd15d07445` | balanced paths / all strategies | `ce4a0ac` |
| `15_dashboard_chart_denominators_demo.jpg` | Metric chart and explicit denominators | `run-7343b258a9b64a77bc4716bd15d07445` | balanced paths / all strategies | `ce4a0ac` |
| `16_project_info_architecture_demo.jpg` | Architecture, strategies, and dataset facts | — | — | `ce4a0ac` |
| `17_limitations_privacy_safety_demo.jpg` | Claims, privacy, safety, and local reproduction | — | — | `ce4a0ac` |

The browser pass manually exercised en→en, en→zh, zh→en, and zh→zh; zero-shot,
few-shot, and self-refinement; the comparison page; development batch preparation and
completion; the persisted held-out dashboard; project information; and the UTF-8 JSON
download control. Exact JSON-byte encoding and CSV encoding are additionally covered by
automated tests.
