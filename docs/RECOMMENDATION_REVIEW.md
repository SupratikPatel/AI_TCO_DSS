# Recommendation engine follow-up

Date: 2026-11-10

## Interpretation

Use case selects a benchmark and quality floor; it does not invent a task workload. Coding assistant and agentic coding share Terminal-Bench, with floors 40 and 55. Writing/email and RAG share AA with floors 14 and 18. Change requests/day, token lengths, context, users and targets in Expert mode to represent the actual work.

Popular assigns 40% weight to the OpenRouter model-usage snapshot dated 2026-11-06. It is not a survey of company adoption or hardware popularity. Missing popularity is treated as zero and noted. C-055 supersedes the earlier 50% cost-weighted Cheapest preset: it now uses cost-only weights after hard filters. Expert custom weights can override that preset. C-056 adds an explicit self-managed purchase-and-electricity comparison; see [calibration and cost review](CALIBRATION_AND_COST_REVIEW.md).

The earlier writing/email Best Fit result favored the $1.79M rental because speed and latency continued earning score beyond the required targets. By default, scoring now caps these two criteria at the targets. Raw measurements remain visible. Expert mode can restore rewards for excess performance. A 60-month total budget provides a hard affordability limit; CapEx alone cannot exclude expensive rentals.

## Historical reproduced default workload before C-054 through C-056

| Use case | Preset | Winner | 60-month USD | SAW |
|---|---|---|---:|---:|
| writing-email | cheapest | NVIDIA RTX Pro 6000 Blackwell (96GB) x 4 + DeepSeek V4.1 Flash INT4 | 308,347.20 | 0.992 |
| writing-email | best-fit | NVIDIA RTX Pro 6000 Blackwell (96GB) x 4 + DeepSeek V4.1 Flash INT4 | 308,347.20 | 0.996 |
| writing-email | most-capable | NVIDIA RTX Pro 6000 Blackwell (96GB) x 4 + DeepSeek V4.1 Flash INT4 | 308,347.20 | 0.997 |
| writing-email | popular | NVIDIA RTX Pro 6000 Blackwell (96GB) x 4 + DeepSeek V4.1 Flash INT4 | 308,347.20 | 0.997 |
| summarisation-rag | cheapest | NVIDIA RTX Pro 6000 Blackwell (96GB) x 4 + DeepSeek V4.1 Flash INT4 | 308,347.20 | 0.992 |
| summarisation-rag | best-fit | NVIDIA RTX Pro 6000 Blackwell (96GB) x 4 + DeepSeek V4.1 Flash INT4 | 308,347.20 | 0.996 |
| summarisation-rag | most-capable | NVIDIA RTX Pro 6000 Blackwell (96GB) x 4 + DeepSeek V4.1 Flash INT4 | 308,347.20 | 0.997 |
| summarisation-rag | popular | NVIDIA RTX Pro 6000 Blackwell (96GB) x 4 + DeepSeek V4.1 Flash INT4 | 308,347.20 | 0.997 |
| coding-assistant | cheapest | NVIDIA RTX Pro 6000 Blackwell (96GB) x 4 + DeepSeek V4.1 Flash INT4 | 308,347.20 | 0.989 |
| coding-assistant | best-fit | NVIDIA RTX Pro 6000 Blackwell (96GB) x 4 + DeepSeek V4.1 Flash INT4 | 308,347.20 | 0.995 |
| coding-assistant | most-capable | NVIDIA RTX Pro 6000 Blackwell (96GB) x 4 + DeepSeek V4.1 Flash INT4 | 308,347.20 | 0.997 |
| coding-assistant | popular | NVIDIA RTX Pro 6000 Blackwell (96GB) x 4 + DeepSeek V4.1 Flash INT4 | 308,347.20 | 0.997 |
| agentic-coding | cheapest | NVIDIA RTX Pro 6000 Blackwell (96GB) x 4 + DeepSeek V4.1 Flash INT4 | 308,347.20 | 0.990 |
| agentic-coding | best-fit | NVIDIA RTX Pro 6000 Blackwell (96GB) x 4 + DeepSeek V4.1 Flash INT4 | 308,347.20 | 0.995 |
| agentic-coding | most-capable | NVIDIA RTX Pro 6000 Blackwell (96GB) x 4 + DeepSeek V4.1 Flash INT4 | 308,347.20 | 0.997 |
| agentic-coding | popular | NVIDIA RTX Pro 6000 Blackwell (96GB) x 4 + DeepSeek V4.1 Flash INT4 | 308,347.20 | 0.997 |

Identical winners are possible and are not a reason to force diversity. They reflect the seed catalog, missing API performance evidence, shared benchmark mappings, constraints and weights. The app now exposes missing evidence and the lowest admissible cost. These are model outputs, not procurement recommendations.

## Remaining evidence work

Independent API/local benchmarks, offload and multi-node calibration, current hardware/networking quotes and precise custom-license representation remain unresolved. Existing calibration failures are retained. No empirical data was invented to make the tests or rankings look better.

Catalog fingerprints reject auditing a result against changed catalog data. This prevents mixing snapshots but is not a full archived catalog replay mechanism. The hybrid generator still selects one cheapest eligible local anchor; exhaustive routing optimization remains future work.

See [Revolut case study](REVOLUT_CASE_STUDY.md) for the primary-source analysis and comparison boundaries.

## Illustrative small-workload sensitivity check

This is an explicit assumption scenario, not measured enterprise demand: 5 users, 10 requests/user/day, 1,000 input tokens, 200 output tokens, one concurrent agent/request, 8,192 context, minimum 10 TPS, 0.05 operations FTE, $100,000 total budget, Writing/email and Cheapest. Other fields retain repository defaults. It changes several assumptions together and is not a causal attribution to any one field.

- NVIDIA DGX Spark (128GB) x 1 + GLM 5.3 Flash INT2: $31,596.39 over 60 months.
- NVIDIA DGX Spark (128GB) x 2 + GLM 5.3 Flash INT2: $41,787.38 over 60 months.
- NVIDIA GeForce RTX 5070 12GB + 64GB DDR5 (Strata offload) x 1 + Qwen 3.8-27B FP8: $24,694.51 over 60 months.
