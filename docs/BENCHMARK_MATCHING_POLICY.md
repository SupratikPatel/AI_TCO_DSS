# U-01: metric-specific benchmark matching policy

Reviewed 2026-11-11. Scope: `domain/benchmark_conditions.py`, `engines/resolver.py`,
`engines/performance.py`, `services/calibration_report.py`, the TCO eviction-cost consumer,
their regression tests,
this policy, the correction ledger and continuity documents. No empirical observations,
catalog values or coefficients were changed. U-01 is a software/policy review;
independent calibration remains unfinished under U-02 through U-06.

## Definitions and evidence basis

Prompt processing, generation rate, first-token latency and aggregate serving throughput
have different denominators and timing boundaries. The primary
[llama-bench documentation](https://github.com/ggml-org/llama.cpp/blob/master/tools/llama-bench/README.md)
separates prompt processing, text generation and combined tests, and describes context
depth separately. [vLLM's metric definitions](https://github.com/vllm-project/vllm/blob/main/docs/design/metrics.md)
distinguish inter-token latency from per-request time per output token.
[NVIDIA's benchmark explanation](https://developer.nvidia.com/blog/benchmarking-llm-inference-at-scale-with-aiperf/)
distinguishes TTFT, inter-token latency and throughput across concurrent requests.
Accessed 2026-11-11. The policy below is an engineering decision for this application's
contracts, informed by those definitions; it is not an external standard or an accuracy claim.

Source import must establish the metric's definition before assigning `BenchmarkMetric`.
`DECODE_TPS` means a per-stream generation-phase rate, not whole-request output/time.
`PREFILL_TPS` means an isolated input-processing rate, not inverse end-to-end latency.
`TTFT_S` requires its client/server timing boundary. `AGGREGATE_TPS` is deployment-wide
throughput. Protocol strings must distinguish these boundaries, batching, cache handling,
kernel settings, placement and other material run settings. Exact string equality is a
conservative identity check; the software cannot verify the truth of a protocol description.
Unspecified material facts remain exclusion reasons rather than inferred defaults.

## Observation completeness versus matching versus calibration

These are separate decisions:

1. Is the observation interpretable, with the facts needed for its metric?
2. Does it match the requested execution/deployment?
3. Can the current formula represent those conditions, using independent evidence?

An offload observation can match a fully specified offload deployment while remaining
ineligible for the resident bandwidth formula. Similarly, an exactly matched concurrent
or speculative measurement can be used without claiming the formula models it accurately.
`BenchmarkConditions.missing_fields()` remains an inventory of all null contract fields;
it is no longer used as a universal eligibility rule. `evidence_gaps()` and
`matching_fields()` implement the metric-specific rule used by selection and calibration.

## Required and matching facts

All performance metrics require actual `prompt_tokens`, coarse precision and the following
execution facts on both observation and query. These facts must match exactly, apart from
the explicit prompt-length tolerance:

- Node count, accelerator/unified memory, host RAM and resident/offload placement.
- Runtime and version, model revision and exact quantization identity. A generic INT4
  bucket alone does not identify a mixed quantization build.
- KV precision, cache hit fraction and cache state.
- Speculative mode, concurrency and measurement protocol.

Additional rules:

| Field | Decode TPS | Prefill TPS | TTFT | Aggregate TPS |
|---|---|---|---|---|
| Output length | Required and exact | Not a matching field for isolated prefill | Not a matching field for first-token timing | Required and exact |
| Speculative configuration | Required and exact when mode is enabled | Same | Same | Same |
| Speculative configuration when mode is `none` | Not applicable | Not applicable | Not applicable | Not applicable |
| App `optimized_backend` boolean | Formula hint, not a matching field | Same | Same | Same |
| Actual runtime/kernel settings | Required in execution/protocol identity | Same | Same | Same |

Output length can affect the scheduler through other concurrent requests. For prefill or
TTFT under load, protocol identity must describe that workload; omitting this scalar does
not make otherwise undocumented load comparable. Enabled speculation still requires its
exact configuration. Cache, concurrency, KV and runtime facts were not made optional.
All explicit `uncertainty_reasons` continue to exclude an observation, including those
preserved on historical records. The observed value and metadata remain in the report.

The app backend switch currently selects a **formula-only TTFT multiplier** (1 or 0.035).
It does not configure or inspect an inference runtime. It is therefore not an independent
physical fact a third-party benchmark must report. Removing it from matching does not
equate different kernels: their actual settings must be part of the documented protocol.
The field stays in the contract for compatibility/audit; null remains null. Calibration
of raw decode/prefill does not require or fabricate this app flag.

Quality lookup remains separate and unchanged: it does not acquire hardware/runtime
matching requirements from this policy. Quantization-specific quality validity is U-05.

## Prompt, occupied context and configured capacity

- `BenchmarkRecord.prompt_tokens` is the actual measured input/context depth established
  by the protocol. `context_tokens` is a historical audit field. Neither legacy context
  nor configured capacity supplies a missing prompt.
- `configured_context_tokens` is a capacity setting, not occupied context. It need not
  equal the prompt and is not automatically mandatory. A known capacity smaller than
  the documented prompt is contradictory and excluded. Material allocation/kernel
  differences must still be identified in the protocol.
- `BenchmarkQuery.target_context` is a legacy field name: performance lookup uses it
  as the requested actual prompt/depth, within the configured tolerance (currently 25%).
  That tolerance is an assumption, not evidence that the speed curve is flat.
- `SizingOptions.performance_prompt_tokens` supplies the requested decode/prefill
  measurement point. The independent one-million-token prefill projection looks up
  that explicit point. It does not infer a million-token observation from capacity.
- Measured TTFT is selected against `workload.t_in_hat`, including harness/tokenizer
  input adjustments. A decode-context override cannot select a short-prompt TTFT for
  a much larger modeled request. With eviction risk, ordinary measured TTFT is not
  substituted: the current metadata cannot identify the additional rebuild event.
- The resident decode formula still applies `delta_ctx` to `target_context_length`.
  This remains the app's conservative target-context scenario estimate. Calibration
  explicitly evaluates at the observed prompt; configured maximum capacity never
  replaces that prompt. This does not validate estimates for every actual prompt below
  a capacity limit. Decode averages over growing output context also remain a model
  approximation; output length and protocol stay visible and exact for measured lookup.

The catalog-based prefill formula remains a hardware base rate. Applying that rate, or
one measured prefill point, to a different prompt or a million-token projection is an
approximation, not an independently validated latency curve. Cache-rate interpretation,
context scaling and feasible allocation for long-context runs need controlled evidence
under U-02/U-03. No fitted context or cache model was introduced in U-01.

## Concurrency and deployment policy

Measurement concurrency means simultaneous requests sharing the described hardware,
not the number of active users or retained agent states. The engine currently takes
the scenario's declared peak concurrent requests as the query's deployment load and
overrides contradictory metadata hints. It does not silently convert this to one,
divide measured latency by users, or treat aggregate TPS as single-stream decode.

Whether a scenario's peak is fleet-wide or per workstation needs an explicit workload
and allocation comparison in U-05, and validated shared serving in U-07. U-01 preserves
the conservative existing load assumption rather than guessing a per-machine peak.
Formula calibration continues to reject concurrency other than one: no concurrent
decode/prefill formula is established. Multi-node matching requires exact hardware/node
facts, but a match alone does not validate the existing scaling coefficient (C-011).

For RAM-shelf/offload deployments, resident GPU bandwidth is still not an acceptable
fallback. Matching measured performance is allowed; absent that evidence performance
stays unavailable. No transfer-bandwidth model or fitted offload coefficient was added.

## Formula calibration boundary

2026-11-11 follow-up (C-058): decode and aggregate query output lengths are taken
from the workload's generated-token volume (`out_think`, including thinking/tokenizer
effects), rounded to a token count. Contradictory metadata hints cannot override it.
Prefill/TTFT retain their metric-specific treatment of output length. Original
observations are unchanged; this is a query correction, not a new measurement.

Local formula comparisons additionally require an open-weights model, a prompt within
the catalog model limit and a configuration representable by the current sizing model.
An observed resident run that the sizing model calls OOM is exported as an explicit
model-support gap, not a measured failure or a successful throughput comparison.
Such evidence may expose a sizing error; exclusion does not resolve that discrepancy.
Engine metadata is 0.1.3 for these corrections and the preceding U-01 fixes.

The report retains the existing exclusions for uncertainty, missing required facts,
unknown hardware/model, nonpositive observations, offload, concurrent execution,
cached prompt processing, enabled speculation and quantization not represented by
the uniform-bit formula. Hardware memory/node configuration must agree with the catalog.
Prefill observations sourced from the same source as the formula's input remain excluded
as circular evidence. Different source IDs alone do not prove independence: U-02 must
check the underlying measurements and U-03 must separate fitting from validation.

The current prefill formula is a catalog base rate and does not consume the TTFT backend
multiplier. Measured prefill already includes the measured execution's speed, so derived
TTFT and TCO eviction wait now use that rate directly. Catalog/formula prefill retains the existing beta
assumption. Derived TTFT is still labeled formula, with measurement source provenance.

## Demonstrated errors and verification

- Before fixes, the new regression run produced 11 failures and 3 passes. It exposed
  unnecessary output/backend/config requirements, use of the wrong TTFT prompt,
  contradictory prompt/capacity acceptance and exclusion of otherwise complete synthetic
  calibration data solely for a missing app flag.
- A synthetic 1,000 TPS prefill observation with the app switch off yielded 685.714 s
  instead of 24 s for the test workload because beta was applied a second time.
  The correction removes that duplicate penalty; this is not a real benchmark result.
- Regression coverage also preserves missing physical-fact exclusions, generation output
  requirements, unsupported formula conditions, ordinary TTFT exclusion during eviction,
  capacity/prompt separation and the current catalog's zero independent coverage.
- A separate failing regression reproduced the same duplicate penalty in TCO eviction
  wait cost; that consumer was corrected as part of U-01 as well.
- Expanded focused post-fix checks: 220 passed, 13 evidence exclusions, 3 historical diagnostic
  expected failures. Final full Python: 819 passed, 13 skipped, 3 historical xfails, zero failures/errors, exit 0 (244.43 s). Ruff/format, strict mypy, catalog validation and API type drift pass. No schema/frontend changes; no browser or combined verifier rerun. The earlier full run exposed three continuity-document gates, corrected without changing their tests; the final full run passes them.

**Unchanged empirical result:** zero comparable decode/prefill observations, 12 decode
exclusions and one prefill exclusion; MAPE n/a. No observation was admitted to improve
the headline count. No coefficient was tuned. U-02 must recover primary run metadata
and produce the source-backed measured/inferred/missing evidence matrix. The exact
MacStories KV settings and model revision, and Strata's decode-specific prompt/build/
speculation/protocol, remain evidence gaps. U-03/U-04 cannot be marked complete from
this policy review or software tests.

C-058 final verification (engine 0.1.3): combined verifier native exit 0; 826 Python
passed, 13 skipped, 3 historical xfails; 31 frontend tests, 71 no-update browser
checks and 3 launcher checks. Numerical calibration coverage remains zero.
