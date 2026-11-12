# Calibration eligibility and one-user costs

Implemented 2026-11-10 for the author's continuation and bug report. Task scope: benchmark/domain contracts, catalog ingestion and evidence, resolver, performance/TCO engines, calibration service/report, ranking preset, scenario/accounting presentation, relevant tests/generated types, correction ledger and handoff. Existing staged work is preserved. No commit or push.

## Why the one-user result was about $300,000

The reproduced old Agentic coding / Cheapest result was a four-GPU RTX Pro 6000 deployment at **$308,347.20** over 60 months:

| Component | Five-year USD |
|---|---:|
| Hardware, purchased once | 71,456.00 |
| Operations staffing: 0.5 FTE | 214,053.98 |
| Electricity | 6,759.61 |
| Capital opportunity cost | 16,077.60 |

The implementation did not repeatedly buy the hardware. The enterprise staffing assumption dominated. Reducing users did not reduce the allocated operations FTE. Cheapest also meant a 50% cost weight, so more expensive candidates could win through quality and other criteria.

C-055 makes the Cheapest preset cost-only after hard filters; custom Expert weights can still override it. C-056 adds an explicit Normal/Expert cost-assumptions selector. Self-managed ownership uses purchase plus electricity at PUE 1, with no paid operations staff, NIM license, economic losses or resale deduction. Enterprise inputs are retained when switching modes. API charges/gateway assumptions and rental charges remain separate; this is not a claim that those services become free.

With one user, Agentic coding, Cheapest, self-managed and the existing workload defaults, the leading modeled option is **Mac Studio M5 Max 128 GB + Qwen 3.8 Flash Next INT2**, at **$6,143.30**: $5,693.03 purchase plus $450.27 electricity. The 256 GB M5 Ultra alternatives cost **$11,443.83**. These use existing catalog prices and formula/quality assumptions, including the INT2 candidate's quality fallback. They are not independently validated deployment benchmarks. No rule forces a Mac to win.

The default workload still has eight retained agents, five peak requests, 128,000 target context, minimum 20 effective TPS and maximum 15-second TTFT. Active users alone does not define all of those workload settings. The selected ranking now displays hardware, electricity and staffing directly.

## Evidence and matching

`BenchmarkRecord.context_tokens` remains as a legacy audit field. `prompt_tokens` is the measured prompt; `configured_context_tokens` is capacity and never substitutes for it. Scenario `performance_prompt_tokens` explicitly supplies the prompt used for measurement lookup; ordinary sizing capacity is not passed off as an actual prompt.

Matching requires model/hardware/precision, a prompt within the existing tolerance, and metric-specific matching execution conditions: node count, accelerator/host memory, runtime/version, model revision, exact quantization identity, KV precision, cache fraction/state, speculative mode, concurrency, protocol and residency. Speculative configuration is required when enabled; output length is required for generation metrics. The app's formula-only optimized-backend flag is not a physical measurement requirement. Hardware, concurrency, KV and cache settings are taken from the actual request rather than trusted from a mismatching override. Quality benchmarks retain their separate hardware-independent resolution behavior. See [U-01 matching policy](BENCHMARK_MATCHING_POLICY.md) and C-057 for the 2026-11-11 corrections, including workload-prompt TTFT selection and removal of duplicate backend penalties on measured prefill.

Incomplete evidence is loadable, preserved and excluded from measured lookup with reasons. Formula estimates remain labeled formula. RAM-shelf deployments have no VRAM-bandwidth performance fallback; absent comparable measurements, decode/effective performance and capacity are unavailable. No bandwidth/efficiency coefficient was tuned.

The [MacStories source](https://www.macstories.net/stories/m5-ultra-mac-studio-review-the-dream-mac-for-local-ai-agents/) identifies the 256 GB M5 Ultra, oMLX 0.7.0.dev2 and mixed oQ4e build. Five prompt-series rows are imported separately from the 108 TPS summary. The 130,522-token row is 60.6 TPS, with 512 output tokens, no cache reuse and MTP depth 3. The source's linked model revision is retained; fetching that linked Hugging Face revision returned 404 during this session, so its contents were not independently verified. KV precision and the app's optimized-backend flag are not established for those rows and remain unknown.

The [Strata maintainer documentation](https://github.com/Niko1221/Strata/blob/main/docs/DEEPSEEK41.md) supplies a separate typical 4.7 TPS RTX 5070 / 64 GB observation. Its prompt and exact runtime settings are not tied to that row. The 257 GB download includes Engram and the drafter. No PCIe/NVMe throughput or 70% multiplier was inferred as a measurement.

All six original decode records remain in the catalog with uncertainty reasons; an unchanged pre-correction copy is in `evidence/legacy_decode_observations.json`. Rounded summaries, primary rows and assumptions are not merged.

## Calibration interpretation

The report exports every comparison and exclusion, measured value, prompt, execution metadata, reason and numerical outcome. It separates comparable passes, numerical failures/known failures, and incomplete/unsupported evidence. Same-source prefill inputs are rejected as circular validation; hardware configuration, uncached processing and formula-supported execution must agree. Unknown precision/prompt values never receive fabricated defaults.

Current evidence yields **0 comparable decode rows / 12 exclusions** and **0 comparable prefill rows / 1 exclusion**, so both MAPE values are **n/a**. This is an evidence-coverage limitation, not an improvement to numerical accuracy. The three C-035/C-036 discrepancies are retained as strict xfail historical diagnostics under their original assumed conditions; synthetic regression tests exercise successful comparisons and numerical failures independently of eligibility exclusions.

Run `uv run ai-tco-calibrate` to regenerate `reports/calibration.csv`. Engine metadata is now 0.1.2. Source registry changes are reflected in the generated bibliography.

## Remaining work

**Status clarification (2026-11-11): the calibration task remains unfinished.** This review records completed safeguards and cost fixes, not validated numerical performance. The actionable backlog and completion criteria are in [UNFINISHED_TASKS.md](UNFINISHED_TASKS.md), U-01 through U-09. On resume, begin with U-01; do not conclude "everything done" from the passing software tests.

Obtain independent, fully specified resident, offload, multi-node and API measurements before treating predictions as validated. Calibrate exact quantization/speculative/runtime behavior only against comparable evidence. The catalog still has nine hardware entries, Macs at 64/128/256 GB and no priced 512 GB Mac. A shared Mac inference server requires a separate deployment mode and validated capacity; existing Macs remain one workstation per user.

Verification results and the next-session prompt are recorded in `progress.md`. Screenshot review compares the established Stitch-based layout and adds desktop/mobile self-managed captures; the cost selector uses short labels so its selected value stays readable on mobile.
