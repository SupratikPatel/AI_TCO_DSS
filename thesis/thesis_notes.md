# Thesis working notes: decision support for the total cost of AI inference

**Status:** Research and writing notes, not a completed thesis. Project facts below describe the repository state documented on 2026-11-09. Research questions and chapter structure are proposed wording for the author's review. Numerical examples are scenario-dependent estimates, not independently validated predictions or procurement advice. Catalog references and academic literature are maintained separately in `references.bib` and `literature.bib`.

## 1 Introduction

### Problem and motivation

Organizations considering language-model inference must compare alternatives that differ simultaneously in capital expenditure, recurring expenses, technical capacity, model capability and contractual constraints. A cloud API, a dedicated GPU rental, an owned installation and a hybrid arrangement have different cost structures. A comparison based only on GPU purchase price or an API token price can omit personnel, electricity, memory capacity, workload variation and endpoint requirements. The project specification frames the problem as a decision-support task rather than an automatic procurement decision [@SPEC-02].

The proposed artifact is the AI TCO Decision Support System (DSS), a scenario-driven application that compares candidate deployments against feasibility constraints and ranks the candidates that remain. It makes formulas, input provenance, assumptions and result exports available for inspection. The value of this artifact is its ability to make assumptions and trade-offs explicit; its outputs should not be interpreted as guaranteed costs, legal determinations or empirical performance measurements.

### Proposed research questions

- How can a scenario-based DSS combine inference sizing, cost estimation and hard constraints to compare AI deployment alternatives?
- How do workload assumptions, infrastructure costs, feasibility thresholds and decision weights affect the candidates and ranking produced by the model?
- How can formula traces, data provenance and exportable results make the recommendation more inspectable?

These questions are candidate formulations, not claims about an approved thesis proposal. Design science provides a possible framing for the creation and evaluation of an information-systems artifact [@Hevner2004]. The final methodology, contribution and scope require agreement with the thesis supervisor.

### Intended contribution and boundaries

The implementation connects a catalog and reproducible scenario inputs to workload, sizing, performance, financial and multicriteria decision models. It supplies a web interface and a structured audit trail. Its contribution is a demonstrable decision process and a reusable implementation; evidence of better organizational decisions would require a separate user study or field evaluation. It does not establish that its seed prices, performance assumptions or quality benchmarks predict outcomes for a particular organization.

## 2 Background

### Inference workload and memory

Inference capacity depends on model weights, precision, runtime overhead, context length and concurrent requests. An autoregressive service also stores attention key and value state; this cache can grow with request length and concurrency. PagedAttention research discusses the memory-management challenges of serving variable-length requests and presents a particular allocation approach [@Kwon2023PagedAttention]. That paper motivates attention to memory management but does not validate this DSS's sizing equations or imply that the DSS models vLLM's allocator in detail.

The project's workload and physics specification defines inputs such as users, requests, context, prompt scaffolding and thinking effort [@SPEC-01]. The implementation distinguishes memory feasibility from performance: a pairing that fits is not automatically fast enough, and missing empirical data must not be presented as a measured result. Quantization changes memory needs and can affect model fidelity; catalog-specific agreement data and its provenance should be examined rather than assumed to generalize [@IND-03].

### Total cost and alternatives

The project models owned infrastructure through upfront capital costs and recurring components such as energy and personnel, with optional resale and additional scenario-controlled items. API alternatives depend on workload, token prices and selected endpoint assumptions. Dedicated rentals and hybrid deployments use different cost structures [@SPEC-02]. Energy and staffing inputs are catalog snapshots rather than universal tariffs or salaries [@IND-05; @IND-06].

The timeline is an undiscounted cumulative-cost comparison. It should not be called net present value or a discounted cash-flow analysis. A computed crossing is an integer month in this model, not proof that an investment will break even under real demand.

### Multi-criteria decision analysis

Hard filters encode mandatory conditions before preference scoring. The implemented weighted sum (SAW) and TOPSIS methods then compare admissible alternatives on cost, quality, effective throughput, latency, risk and popularity. TOPSIS is grounded in the multiple-attribute decision literature [@HwangYoon1981]. Normalization, missing-data treatment, weights and the candidate set affect results; a rank is conditional on these modeling choices. Rankings should be accompanied by sensitivity analysis and explanations rather than represented as objective proof of a uniquely best architecture.

## 3 Requirements

The active requirements are in `.kiro/specs/ai-tco-dss-mvp/requirements.md`; the web migration decision in `specs/09_WEB_FRONTEND_MIGRATION.md` supersedes older delivery-specific Streamlit directions. The following is a synthesis, not a replacement for those requirements.

Functional requirements include loading a provenance-bearing catalog, accepting a workload and financial scenario, calculating memory fit and cost projections, applying feasibility filters, ranking candidates, presenting independent simulators and exposing an audit trail. The audit must identify the selected candidate, show available formula traces and value origins, and allow JSON and CSV exports. The application must distinguish infeasible alternatives, missing benchmark data, invalid inputs and calculation failures.

Quality requirements include deterministic calculations for the same inputs, input validation, transparent sources, responsive light and dark layouts, keyboard-accessible controls and tests across the API and browser. USD is the calculation currency; EUR is a display conversion. An explicit FX override can alter USD values derived from EUR catalog inputs, whereas changing display currency alone must not alter the decision calculation [@ECB-FX].

Normal mode retains the selected use case, user count and preset while ignoring Expert-only values. Expert mode exposes additional scenario settings and ranking weights. A ranking weight cannot make an infeasible candidate pass a hard filter. These distinctions are important to both the requirements and the evaluation design.

## 4 Design

### Architecture and data flow

The active architecture separates the React/TypeScript frontend from a FastAPI adapter and Python services. The Python domain contracts, catalog repository, calculation engines and decision layer remain the computational authority. The web client presents typed results, handles interaction and formats display values; it does not implement the financial or ranking algorithms. The Streamlit adapter was retired in Task 13; pure chart and formatting helpers remain for regression coverage.

A scenario flows from the UI through validation to the service layer. The service constructs candidate evaluations, applies hard filters, ranks feasible candidates and returns a `ScenarioResult` containing the recommendation, baselines, optional timeline, FX metadata, source registry and warnings. Separate memory and TCO simulator requests retain their own inputs and results. The shared KPI ribbon describes rank one, not the independently selected simulator candidate.

Catalog values use sourced wrappers with source identifiers, tiers and access dates. The generated `references.bib` reflects `data/sources.json`; a catalog source being present does not, by itself, establish the accuracy or continuing validity of every associated number. Assumptions are identified as assumptions [@ASSUMPTION-MVP; @ASSUMPTION-WORKLOAD-DEFAULT].

### Decision workflow and auditability

The candidate generator considers available deployment combinations and computes relevant facts. Filtering reports measured or calculated values and required thresholds; scoring applies only after filtering. SAW uses normalized criteria and weights; TOPSIS uses distances to ideal and anti-ideal points. Their rankings should be interpreted with the precise normalization and missing-value behavior implemented in the repository, not merely from the method names [@HwangYoon1981].

The audit drawer shares candidate selection with the ranking. It exposes existing engine traces and performance origins, source references and the active FX metadata. Hybrid components are shown separately; rental accounting is distinguished from the retained local calculation. JSON export contains the current service result in USD. The CSV ZIP contains ranking data and the scenario's 60-month timeline in the active display currency. The timeline anchor is identified and can differ from a non-on-premise winner; simulator results are independent. Export is disabled for pending or failed current calculations to avoid presenting an earlier result as current.

## 5 Implementation

### Core services and models

The repository uses immutable Pydantic domain contracts, a JSON-backed catalog repository, pure calculation engines and service orchestration. Workload calculations feed sizing and performance; the financial engines construct owned, rental, API, baseline and hybrid comparisons. The measured-first resolver chooses an applicable benchmark when one exists; otherwise the performance model reports a formula-derived value. The source of each available performance value is visible in the result.

Candidate enumeration and filtering are implemented in the decision layer. Hybrid feasibility uses explicit component facts and recalculates local demand at the local share (ledger C-042). Rental host RAM is treated as a server total and converted to a per-node sizing input (C-043). These are implementation decisions to describe precisely in the final thesis, including why a weighted average alone cannot establish component feasibility.

### Interface and export

The web application uses React, TypeScript and Vite, with a FastAPI boundary over the Python services. Ranking, memory and 60-month TCO are separate views with a common KPI ribbon. The interface supports Normal and Expert scenarios, light and dark themes, accessible tables and explicit warning text. Charts retain documented palette and line-style meanings from ledger C-004; color is not the only status indicator.

The selected-candidate audit uses the existing result's traces and provenance. Deployment-specific cost traces are supplied for API, rental and hybrid candidates, while on-premise traces are retained from the engines. CSV conversion uses the result's FX rate, and JSON retains the full USD result. A prior independent TCO projection retains the FX rate from its successful request even if later scenario inputs change.

### Reproducibility

Python dependencies are managed through the repository's `uv` environment and frontend dependencies through npm. `scripts/verify.py` runs Python linting, formatting, type checking, catalog validation and tests. The combined verifier also runs frontend, Chromium and launcher checks; production cutover was completed in Task 13. The exact dependency versions and commands should be taken from the checked-in project files at the time of final submission.

## 6 Evaluation

### Evidence available at this snapshot

The Task 12 project record reports 728 Python tests passed, three calibration cases expected-failed, and three failures caused by the two thesis files that were missing at that snapshot. It also reports 59 Chromium checks and 28 frontend tests passing, together with frontend typecheck, lint, build, generated-type drift and a separately run launcher check. This is a historical verification snapshot; rerun the suite and record its actual result before using it as current evidence.

Browser checks cover both themes at desktop, tablet and mobile CSS widths, the audit selector, downloads, empty/error states, stale-response handling and keyboard interactions. Python checks compare API payloads with service outputs and exercise export round trips. These checks support claims about implemented behavior and regression coverage; they do not demonstrate external validity of the cost and performance estimates or user effectiveness.

Under the documented default scenario, the Task 9/11 project record reports 36 admissible and 637 rejected candidates, with an on-premise RTX Pro 6000 configuration and DeepSeek V4.1 Flash INT4 ranked first by SAW. The score and ordering are outputs of the repository's scenario, catalog and model assumptions, not a recommendation applicable to every enterprise. Catalog figures and source pages change over time [@NVIDIA-RTX-PRO-6000; @HF-DEEPSEEK-V4-1-FLASH]. Reproduce the scenario from the saved input and result before citing numeric outputs.

### Evaluation still needed

1. Define a reproducible scenario matrix varying user demand, concurrency, context, electricity, staffing, rates and deployment constraints. Report the full input and catalog snapshot.
2. Compare measured and predicted decode, prefill and end-to-end latency under matched model, precision, hardware, context and runtime conditions. Report sample size, source quality, errors and exclusions; avoid equating a software test pass with predictive accuracy.
3. Examine rank sensitivity to weights, missing data and normalization, and check whether small plausible changes alter feasibility or the preferred deployment.
4. Validate economic assumptions with representative procurement, operations and workload data, including uncertainty ranges and omitted costs.
5. If the research question concerns decision quality or usability, conduct a separately designed and approved evaluation with intended users; record task outcomes and limitations without claiming findings before the study is run.

## 7 Limitations

The corrections ledger is the primary source for known deviations. In particular, C-035 and C-036 record large decode prediction errors for specific hardware/model cases; three calibration cases are expected failures. C-037 records assumed context and precision for some benchmark records and identifies a circular prefill calibration case. These findings limit claims of predictive performance. Benchmark values from video summaries have not all been independently remeasured.

Some catalog numbers are assumptions rather than verified current prices, and source quality varies. Missing quality scores can exclude candidates under quality floors (C-025). The ledger records simplified license representations for some models, so an application's compliance result is not a substitute for reviewing current license terms, data-processing contracts, residency and organizational policy (C-015/C-017). An endpoint's modeled location alone cannot prove legal compliance.

Other model limitations include simplified multi-node decode scaling (C-011), incomplete multi-node cabling costs (C-033), the active-hours contract mismatch (C-038), and the target-context/eviction calculation contract gap (C-039). The timeline uses the documented resale treatment (C-041). Salary, utilization and demand estimates are scenario inputs, not observations of a particular enterprise. Some independent sources are vendor or community material and must be distinguished from peer-reviewed research.

The current implementation does not establish a discounted NPV, a statistical confidence interval, a production SLA, a comprehensive lifecycle assessment or a causal estimate of savings. Test results show conformance to specified behavior, not correctness of all underlying assumptions. The default workload is explicitly a placeholder awaiting organizational data [@ASSUMPTION-WORKLOAD-DEFAULT].

## 8 Future work

Task 13 completed production serving, concurrency/performance checks, CI and retirement of the legacy Streamlit adapter. Post-MVP changes are documented in PROJECT_REVIEW.md and the corrections ledger.

Subsequent research can improve calibration with independent measurements; resolve the ledger's contract and data issues; model uncertainty, price changes and time-varying demand; evaluate discounting as a separately specified extension; broaden the catalog with verified provenance; and study ranking stability. Legal, security, operations and sustainability assessments require additional evidence and should not be inferred from the current numeric score.

For the thesis, confirm the research questions and institution's required structure, establish a versioned evaluation dataset and scenario protocol, document citation access dates where appropriate, and distinguish design intentions from executed experiments. Validate every external source and historical claim again before final submission.

## Update log

- 2026-11-09: Created a sourced working draft from repository progress, active specifications, the corrections ledger and the generated catalog bibliography. Added separately linked academic literature. Research questions and future evaluation activities remain proposals for author review; historical test counts are labeled as a snapshot.
