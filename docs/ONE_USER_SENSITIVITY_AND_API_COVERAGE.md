# One-user sensitivity and API coverage

Historical engine 0.1.3 report, preserved unchanged below. The author subsequently
required simultaneous resident capacity; [engine 0.1.4 policy/results](PEAK_CAPACITY_POLICY.md)
supersede the admission counts and unconstrained peak behavior in this report.
The original saved JSON remains intact. Quality, loaded latency and API evidence
limits below still apply.

2026-11-11 continuation of U-05/U-06. These are outputs of engine 0.1.3 using the
existing catalog, not new benchmark measurements. No quantization-specific quality
score, performance coefficient, price or workload default was changed.

The [machine-readable report](evidence/one_user_sensitivity_2026-11-11.json) contains
all 11 exact scenario inputs, engine parameters, catalog fingerprint, winners, Mac Flash-Next INT2/3/4
results and API results, including origins and rejection reasons. Reloading each
stored input reproduces its winner, exact USD cost and admissible count.

## Workload being compared

Baseline: one active user, Self-managed, Cheapest, Agentic coding, eight retained
agents, five peak requests, 128,000 target context, minimum 20 effective TPS and
maximum 15 s TTFT. Other workload/cost assumptions remain the original defaults.
For this model the input includes 15,000 average user tokens plus 33,000 harness
tokens; output includes the default thinking multiplier. This is a substantial
agent workload, not five people or a single empty-context chat.

## Baseline Mac / Flash-Next results

All speed and latency entries below are **formula estimates**. Missing means the
model does not fit according to the sizing engine and performance is unavailable.
Dollar amounts are modeled 60-month purchase-plus-power totals.

| Mac | Precision | Effective TPS | TTFT, s | KV slots at target context | Outcome |
|---|---|---:|---:|---:|---|
| Mini 64 GB | INT2 | unavailable | unavailable | 0 | Rejected: memory/context/capacity/performance |
| Mini 64 GB | INT3 | unavailable | unavailable | 0 | Rejected: memory/context/capacity/performance |
| Mini 64 GB | INT4 | unavailable | unavailable | 0 | Rejected: memory/context/capacity/performance |
| Max 128 GB | INT2 | 72.17 | 14.55 | 6 | Admitted, rank 1, $6,143.30 |
| Max 128 GB | INT3 | 53.07 | 14.55 | 3 | Admitted, rank 2, $6,143.30; peak-load gap below |
| Max 128 GB | INT4 | unavailable | unavailable | 0 | Rejected: memory/context/capacity/performance |
| Ultra 256 GB | INT2 | 133.78 | 8.89 | 36 | Admitted, rank 10, $11,443.83 |
| Ultra 256 GB | INT3 | 99.72 | 8.89 | 33 | Admitted, rank 11, $11,443.83 |
| Ultra 256 GB | INT4 | 79.49 | 8.89 | 27 | Admitted, rank 12, $11,443.83 |

INT2 does not win because its quality was measured to be better, or because this
comparison purchases cheaper hardware than INT3. The cost-only preset sees equal
hardware/power totals for those two Max configurations and uses deterministic ties.
Their quality is the same model-level second-choice SWE score, 62.5, with a fallback
note. That is not a measurement of either exact quantized artifact. The catalog's
INT3 token-agreement value (81.6%) is a separate risk input; INT2 has no corresponding
agreement value. Neither an absent risk observation nor a model-level quality score
establishes INT2 agent/tool reliability. Quantization-specific evidence is still needed.

## Explicit scenario changes

Each row changes only the indicated baseline field. The last row removes two
performance constraints as a diagnostic; it is not an equivalent-service comparison.

| Change | Admitted candidates | Global modeled winner | Five-year USD |
|---|---:|---|---:|
| Baseline | 47 | Max 128 / Flash-Next INT2 | 6,143.30 |
| Context 64K | 55 | Max 128 / Qwen 27B INT3 | 6,143.30 |
| Context 256K | 38 | Max 128 / Flash-Next INT2 | 6,143.30 |
| Peak 1 request | 47 | Max 128 / Flash-Next INT2 | 6,143.30 |
| Peak 2 requests | 47 | Max 128 / Flash-Next INT2 | 6,143.30 |
| Peak 10 requests | 47 | Max 128 / Flash-Next INT2 | 6,143.30 |
| One retained agent | 48 | Max 128 / Qwen 27B INT3 | 6,143.30 |
| Sixteen retained agents | 43 | DGX Spark / Flash-Next INT2 | 8,330.83 |
| Maximum TTFT 5 s | 30 | RTX Pro 6000 x1 / Qwen 27B FP8 | 19,272.25 |
| Maximum TTFT 30 s | 47 | Max 128 / Flash-Next INT2 | 6,143.30 |
| Both performance filters unset | 120 | Mini 64 / Qwen 27B INT3 | 3,345.78 |

Sixteen retained agents trigger eviction risk on the Max: its Flash-Next TTFT
estimate rises to 92.12 s, failing the unchanged 15 s limit. The Ultra remains
admitted; the cheaper qualifying global option happens to be DGX Spark. At a 5 s
limit all nine Mac/Flash-Next configurations fail; no preference forces a Mac to win.

## Unresolved peak-load boundary

Peak changes above do not establish performance invariance in real serving. The
resident formula is a single-stream estimate; the current hard filter named
`users_served` checks monthly utilization, not peak-memory occupancy or queueing
latency. The aggregate batching fallback also uses modeled maximum KV slots, not
measured serving behavior at each requested peak.

Consequently the baseline Max INT3 is admitted despite three KV slots and five
requested peak requests. At 256K, the Max INT2/INT3 estimates have three/one slots,
while the peak remains five. Some requests would need queueing or another execution
policy; that policy and its latency are not modeled. The report exposes this gap.
It does not silently lower concurrency, add an unsupported queueing coefficient or
call those configurations validated for the requested peak SLA. U-05 remains open
for workload/allocation policy and matched load measurements. Shared serving is U-07.

## API evidence coverage

All four API models have missing decode, TTFT and effective-TPS evidence in the
catalog. Baseline rejected results distinguish this as `not available`, rather than
an observed rate below 20 TPS or an observed latency above 15 s.

| Model | Default performance decision | Other baseline rejection |
|---|---|---|
| Claude Opus 5.5 | Missing TPS and TTFT | None |
| Claude Sonnet 5.5 | Missing TPS and TTFT | None |
| GPT 6.1 | Missing TPS and TTFT | None |
| Gemini 3.1 Pro | Missing TPS and TTFT | No EU-pinned endpoint; quality unavailable |

Removing both performance filters admits GPT, Sonnet and Opus at ranks 82/83/84
with modeled totals $39,097.52 / $41,826.78 / $53,653.56. Gemini still fails the
other requirements. These prices alone cannot establish performance-equivalent
value. The local winner in the baseline is not proof that it outperforms APIs
excluded for absent evidence. U-06's coverage/boundary audit is delivered; comparable
API performance still requires endpoint/region/model-version, prompt/output, cache,
load and client timing records. No paid API calls were made.

## Reproduce a saved scenario

From the repository's Python environment:

```python
import json
from pathlib import Path
from ai_tco_dss.domain import RecommendRequest
from ai_tco_dss.services import recommend
from ai_tco_dss.settings import load_engine_parameters

report = json.loads(Path(
    "docs/evidence/one_user_sensitivity_2026-11-11.json"
).read_text(encoding="utf-8"))
assert load_engine_parameters().model_dump(mode="json") == report["engine_parameters"]
for case in report["cases"]:
    result = recommend(RecommendRequest.model_validate({"scenario": case["scenario"]}))
    winner = result.ranked[0].evaluation
    assert len(result.ranked) == case["admissible_count"]
    assert winner.candidate_id == case["winner"]["candidate_id"]
    assert winner.cost_60m == case["winner"]["cost_60m_usd"]
```

This checks determinism against the recorded catalog/engine snapshot. It does not
validate physical performance, quantized quality, offload behavior or API SLAs.
