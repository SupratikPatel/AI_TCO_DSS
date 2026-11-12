# Enterprise report: verified evidence and bounded fleet implementation

Reviewed 2026-11-12. The supplied `C:/Users/supra/Downloads/evidence_report.md`
is [preserved unchanged](evidence/enterprise_report_review_2026-11-12/evidence_report.md):
46,724 bytes, SHA-256 `2e82d5087bbb2b14d08c58d079a1f32da9db7368a439c9b7c7ec5115dfa46361`.
The three named companion JSON files are absent beside the report. Its claimed
companion hashes are not verified artifacts. No companion logs/screenshots were
identified in the supplied files; unrelated Downloads content was not acquired.

The new material strengthens qualified shared-serving evidence and establishes a
published router's implementation identity. It does **not** resolve Revolut's replica
layout, Julien's exact router, the M5 five-request/128K workload, exact uniform
INT2/INT3 tool quality or matched EU API performance. Strict production coverage
remains **zero comparable observations / 13 existing exclusions / MAPE n/a**.

## What the new primary evidence resolves

The [conference tuning slide](evidence/enterprise_report_review_2026-11-12/revolut-tuning-slide.webp)
was downloaded and visually inspected. It confirms the 56-B200 fleet, reported 76%
higher RPS and 88% lower TTFT (14.26 to 1.68 seconds), and the footnote **Together
AI Dedicated Model Inference**. The [archived conference transcript](evidence/enterprise_routing_analysis_2026-11-12/revolut-talk.html)
separately reports approximately 2,000 engineers, FP4 guidance, TP4/TP8 KV tradeoffs,
cache-hit guidance and interactive speeds. Reuse the saved scale diagnostics; none
of this establishes seven replicas or a GPU-per-employee capacity rule.

The source's approximate spoken RPS endpoints (around three to over seven) and
76% slide summary are separate reported observations; they do not arithmetically
reconcile as one exact endpoint ratio. The transcript/slide do not establish the
report's exact NVFP4 artifact, deployed cache-hit fraction, zero-loss quality result,
or full accounting boundary for $0.30/M tokens. Keep guidance and reported economics
distinct from measured run metadata. Rental invoices and exclusions of staffing or
exception-API spend remain unverified. The list-price calculation is $367,511.20
for 56 × 730 × $8.99, conditional on those rates/hours, not Revolut's invoice.

New [Backboard primary summaries](https://backboard.io/blog/glm-5-3-inference-throughput-vllm)
confirm an eight-B200 BF16 GLM test, 32 workflows and a 30-minute admission window
followed by draining. Sustained output is 370.0 vs 74.9 tok/s, but the report's
latencies are contradicted: source p50 is **3.24 vs 357.50 s**, p90 **61.20 vs
504.90 s**, and median generation **15.8 vs 7.7 tok/s**. Engines completed different
admitted workloads. Burst output is 165.5 vs 63.5 tok/s, with p50 TTFT 1.63 vs
16.40 s. These preliminary internal summaries omit a complete prompt manifest,
variance and serving settings. They support qualified capacity discussion, not
strict import or universal paired latency ratios. All four source tables are saved.

The [H100 AgentX summary](https://backboard.io/blog/qwen-flash-next-h100-full-precision)
is dated November 6, not November 1. At 16 live session trees, Backboard reports
p90 TTFT **1.41 s**, p90 interactivity **71.6 tok/s/user**, and output **90.7
tok/s/GPU**. Its separately rounded all-eight-GPU table reports 726 output tok/s;
multiplying the rounded GPU value gives 725.6. Preserve both. Total-token throughput
includes a different denominator and cannot replace output throughput. AgentX
concurrency means **live session trees**, not simultaneous HTTP requests. The
comparison uses BF16 versus FP8, and does not isolate engine effects. The audit
retains all five levels and both denominator conventions.

The [single-RTX-PRO-6000 Qwen 27B source](https://backboard.io/blog/qwen3-8-27b-vllm-sglang-inference)
does confirm the report's 299/322 ms/13.275 s short-input TTFT and approximately
63.4/64.4/71.2 s long-input values. Its 37,969,920 matching outputs concern one
kernel-change comparison with its parent, not that many independent successful
tool tasks. The Qwen 35B article supplies relative ratios, not absolute capacity.

The [Petronella DeepSeek page](https://petronellatech.com/ai/llm-benchmarks/models/deepseek-v4-1-flash/)
attributes **61 / 349 / 583 tok/s** to **four RTX PRO 6000 Blackwell Max-Q**, not
four H200s. Its fast GB300 + RTX peer path uses **MXFP4 experts**, not the report's
uniform NVFP4 attribution. The [Qwen page](https://petronellatech.com/ai/llm-benchmarks/models/qwen3-8-flash-next/)
confirms the cited GB300 and TP2/TP4/TP8 Spark rates. These are model-parallel pools,
not independent replicas. Prompt/rate divisions remain estimates, not TTFT samples.
Direct HTTP returned 403 for both pages; web-tool primary-page excerpts are saved
separately with that limitation. Named internal source paths are leads, not acquired
raw logs. In particular, the new evidence does not verify the report's H200 identity,
GB300 931.7-at-32 claim or reconstructed TTFTs under concurrent long prompts.

## Router identity and remaining adaptive-routing scope

The npm registry identifies **@caph42/pi-jev-router 2.0.0**, gitHead
`75ad5b71940624ba29baf39ad0e7c51319db598e`. The 39,716-byte package was archived;
its npm SHA-512 integrity matches. README, manifest and TypeScript source were
inspected without installation or execution. The published thresholds, local
classification deadline, guarded write handoff and fallback behavior are supported.
They are policy defaults, not evidence of classifier accuracy or savings.

The [previously pinned Pi documentation](evidence/enterprise_routing_analysis_2026-11-12/pi-virtual-models.md)
uses **`route(request, ctx)` before every request**, including continuations/retries;
the supplied report's `resolve(context)` signature is wrong. In Jev configuration,
`classifier.provider` defaults to `typesafe`; `typesafe-system-one` is an adapter API,
not the provider ID. Classifier re-evaluation at user/compaction boundaries is
distinct from per-request route dispatch. No local GPU congestion-bypass measurement
is supplied by this package. Its fixtures explicitly do not measure production
latency, classifier accuracy, task quality or cost.

Julien's [pinned SynthTraces README](evidence/enterprise_report_review_2026-11-12/synthtraces-README.md)
at `e5f8ec99d8140bcf650b61d9401af996c0c70789` describes a local simulated **user**
and remote coding **agent**. It is not his personal adaptive-router implementation
or an evaluated local/cloud/hybrid policy. The earlier archive already contains his
public LinkedIn post; this report's crawler restriction does not erase that capture.
Keep exact extension identity and measured routing benefits unknown.

## M5, low-bit quality and APIs

Reuse the [512 GB review](M5_ULTRA_512GB_EVIDENCE_REVIEW_2026-11-12.md), permanent
oMLX result 2zvzoy8b and original 2,647-question logs. The new report repeats
unsupported cold-cache/128-output and cross-run memory interpretations (C-071),
and repeats Sushi **94/100 scenarios** despite C-074: the archived score is 94
from **182/194 points**. Do not treat a token-agreement proxy or publisher operating
recommendation as a proven universal minimum safe tool-calling precision. Exact
pack revisions, runtime and workload matter; none supplies uniform INT2/INT3 validity
for the current DSS winner.

Newly archived oMLX 0.7.3 release notes do report an M5 Ultra DeepSeek **12-request
aggregate decode** improvement, 56.3 to 125.7 tok/s. The summary does not identify
the memory configuration or context for that row. It is different from five fully
occupied 128K requests and eight retained sessions. The source explicitly identifies
the quoted eight-long-conversation rows as **M3 Ultra**, retained as history only.
Absence in inspected sources is not proof no public measurement exists anywhere.

[Official OpenAI documentation](https://developers.openai.com/api/docs/models/gpt-6.1-sol)
confirms Sol's $2 input / $10 output / $0.10 cached input per million tokens. Above
272K actual input, the full request uses 2× input/cache and **1.5× output**; the
report's wording that $4/$15 is a uniform 2× jump is wrong. Regional processing adds
10% where available. [Anthropic's official prices](https://platform.claude.com/docs/en/about-claude/pricing)
confirm the cited Sonnet/Opus base and cache-read rates. None is an API latency log.
[Google's model documentation](https://cloud.google.com/vertex-ai/generative-ai/docs/models/gemini/3-1-pro)
lists **1,048,576** input tokens and global-only availability for 3.1 Pro Preview,
contradicting the report's 2M claim. No model or endpoint was silently substituted.
Unverified successor-model, lifecycle, benchmark and provider-specific EU claims
remain unimported. US/4K/batch/edge third-party summaries do not establish streaming
32K/128K EU client TTFT, decode, retries or task success. U-06 remains open.

## Implemented extension and verification

The [explicit fleet scope](FLEET_PLANNING_SCOPE_2026-11-12.md) adds an opt-in
`plan_fleet(FleetSizingInput)` primitive in `engines/fleet.py` with immutable domain
contracts. It takes per-complete-replica request/retention/output capacity, separates
the three demands, rounds independent replica counts upwards, adds caller-declared
spares and multiplies by GPUs per replica. Unknown constraints remain visible and
positive demand with zero capacity has no finite result. It returns **necessary
resource lower bounds**, never a sufficient fleet/SLA verdict. It neither infers
employee demand nor equates AgentX trees to resident request slots.

Two saved executable offline examples show a wholly synthetic case (three active
replicas plus one spare, eight GPUs each) and a partially documented GLM capacity
case. The latter's hypothetical demand yields a three-replica output bound while
request/retained capacity stays unknown; it is not a 24-GPU deployment recommendation.
The observed 370 TPS is explicitly treated as a hypothetical planning ceiling,
not evidence that the hardware cannot serve faster. These are conditional bounds.
Joint placement, scaling, queueing, task success and loaded latency remain unvalidated.
Candidate/ranking/API/UI integration and adaptive scheduling remain future phases.
No catalog values, coefficients, current filters or existing engine 0.1.4 decisions
were changed. No new calibration observations were imported.

The initial new tests failed on the absent module. Two further regressions reproduced
decimal ceiling inflation and finite-ratio overflow before correction using exact
decimal-ratio arithmetic. Focused fleet/purity checks: **30 passed**; new source/test
Ruff/format and strict mypy pass. Full Python result and final continuity verification
are recorded in the final checkpoint below. Existing browser/launcher proof is reused
because their implementation and recommendation path are unchanged.

[manifest.json](evidence/enterprise_report_review_2026-11-12/manifest.json) verifies
24 new source/input/excerpt/member hashes and ten reused archive files. It distinguishes
403 bodies, web-tool excerpts and decoded npm members. The offline
[derivation](evidence/enterprise_report_review_2026-11-12/derive_audit.py) reproduces
the [audit](evidence/enterprise_report_review_2026-11-12/review_audit.json), source-table
checks, npm integrity and fleet examples. C-076 onward records new contradictions;
prior C-071/C-074 are reused. No inference, paid calls, weights, commit or push.

Final verification: full Python **858 passed, 13 skipped, 3 historical xfails**, native
exit 0 in 252.33 seconds; logs `.enterprise-report-python.log` and
`.enterprise-report-python-exit.json`. Ruff/format pass for all `src`, `tests`,
`scripts` and this session's acquisition/derivation scripts; strict mypy passes for
all 47 source files. A root-wide Ruff probe also found pre-existing issues in older
evidence derivation scripts; those archived files were preserved. There is no claim
of a new all-green combined verifier. Current browser/launcher/type proof is reused.

All 33 session-continuity checks pass after the handoff/prompt updates. The root-wide
Ruff result is 41 pre-existing findings, all outside this session's changed files.
