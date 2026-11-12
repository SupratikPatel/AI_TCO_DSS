# Data Corrections Ledger

## Entries
| ID | Date | Area | Old value | New value | Sources | Decision |
|---|---|---|---|---|---|---|
| C-001 | 2026-11-06 | gpt-oss-120b architecture | dense | mixture-of-experts (117B total, 5.1B active) | HF-GPT-OSS-120B, OPENROUTER-MODELS | Use vendor model card; confirmed on 2026-11-07 (128 experts, 4 active, 36 layers) |
| C-002 | 2026-11-06 | Hetzner GEX63 monthly price | €1,197 | €999 (+ €999 one-time setup) | HETZNER-GEX63, IND-09 | Vendor price excl. VAT; re-checked on 2026-11-07 after the 15 June 2026 price change |
| C-003 | 2026-11-06 | Romania employer tax | 2.25 % statutory CAM vs ~4 % incl. benefits | 2.25 % | PWC-TAX-RO, SPEC-02 | Benefits are not a social tax (D-10); PwC confirms CAM 2.25 % on 2026-11-07 |
| C-004 | 2026-11-06 | Chart colours spec 05 §2.2 | non-Okabe-Ito hex values | Okabe-Ito mapping (table below) | OKABE-ITO-2008 | Colour-blind safe palette |
| C-005 | 2026-11-06 | Default currency | EUR | USD | requirements 12.1 | — |
| C-006 | 2026-11-06 | extra-high thinking multiplier | 4.9–8.0 | 4.94 | SPEC-01 §1.1 | Use the empirical task baseline |
| C-007 | 2026-11-06 | Contract changes vs spec 04 | see "Contract Deviations" | | requirements 7.7 | — |
| C-008 | 2026-11-06 | Package path | src/core/, src/ui/, src/agent/ | src/ai_tco_dss/{domain,catalog,engines,decision,services,ui} | requirements 1.6 | — |
| C-009 | 2026-11-06 | Rental GPU | RTX Pro 6000 (workstation) | RTX PRO 6000 Max-Q in GEX63/GEX430; sized with workstation item | HETZNER-GEX63 | assumption: same memory, equal performance |
| C-010 | 2026-11-07 | Poland employer tax | +12 % (spec 03) vs €85–96k total (spec 02) | 20.48 % (16.26 pension and disability + 1.67 accident + 2.45 Labour Fund + 0.10 FGSP) | PWC-TAX-PL, SPEC-02, SPEC-03 | Resolved: statutory employer rates; the 2026 cap of PLN 282,600 is ignored, like C-019 |
| C-011 | 2026-11-06 | Multi-node single-stream decode | — | Req 20.1 applied literally (no ×N) | design D-08 | known limitation, quantified by calibration |
| C-012 | 2026-11-06 | CSV export | two downloads per click | one ZIP with two CSVs | design D-11 | Streamlit limitation |
| C-013 | 2026-11-06 | Mac M5 Max OS reservation | spec 04 default 0.25 | 0.195 (128 GB → 103.04 GB) | YT-02, SPEC-01 | matches 16.6 reference; confirmed in Task 4 (no new source) |
| C-014 | 2026-11-07 | Hetzner GEX430 | not in spec | €3,599/month + €3,599 one-time setup, 4× RTX PRO 6000 Max-Q, 128 GB DDR5 ECC | HETZNER-GEX430 | added by requirements 10.6; setup fee verified on 2026-11-07 |
| C-015 | 2026-11-07 | Kimi K3.1 Pro license | "Open Weights" | Kimi K3.1-Pro License (MIT-style; separate agreement only for Model-as-a-Service businesses above USD 20M revenue; attribution above 100M MAU); stored as `MIT` | HF-KIMI-K3-1-PRO | Resolved: internal enterprise use is unrestricted. `LicenseType` has no custom open-weights member; `MIT` is the closest value (contract change proposal, `domain/` is outside the Task 4 scope) |
| C-016 | 2026-11-07 | Recruiting delay per staffing hub | 7.7 / 6.5 / 2.5 / 3.2 months (spec 03 §4) | 8 / 7 / 3 / 4 whole months (rounded up) | SPEC-03, requirements 13.2 | Req 13.2 stores whole months; rounding up is conservative; no web source found in Task 4, values stay `assumption` |
| C-017 | 2026-11-07 | Qwen 3.8 Flash Next | Apache 2.0; 125B total; 128K context; INT3 93 GB; AA v5 27.8 | Qwen Community License 1.0 (stored as `MIT`, see C-015); 180B stored parameters (125B MoE + 51B n-gram embedding + 4B MTP); 262,144 context; INT3 89.5 GB; AA v5 absent | HF-QWEN-3-8-FLASH-NEXT, UNSLOTH-GGUF, IND-01 | Model card and config.json; the license needs a separate agreement only for Model-as-a-Service / AI Work Assistant businesses, internal use is free. AA v5.0.1 lists no score, so the score stays absent (Req 10.8) |
| C-018 | 2026-11-07 | Baseline A subscription plan | Claude Max 20x, $200/seat/month (spec 02 §1) | Claude Ultra (10x Pro usage) $200, default plan `claude-ultra`; Claude Max (5x) $100 kept as second plan | CLAUDE-PLANS, SPEC-02 | Anthropic renamed its plans; same $200 price point for the default |
| C-019 | 2026-11-07 | Germany employer social tax | 21 % (spec 02 §2.5) | 21.3 % (9.3 pension + 1.3 unemployment + 7.3 health + 1.45 half of the 2.9 % average extra health contribution + 1.8 care + 0.15 insolvency; accident insurance excluded) | PWC-TAX-DE, SPEC-02 | Statutory sum. Open point for the author: the 2026 ceilings (EUR 101,400 pension, EUR 69,750 health) lower the effective rate to about 15.2 % at EUR 120,000 and 18.1 % at EUR 100,000 |
| C-020 | 2026-11-07 | Claude Opus 5.5 cache read price | $0.40 / 1M (10 %, spec 03 §3.3 and spec 02 §1) | $0.20 / 1M (5 % of input) | ANTHROPIC-PRICING | Vendor pricing page; Sonnet 5.5 cache read $0.10 (5 %) confirmed |
| C-021 | 2026-11-07 | Apple hardware specs | M5 Max 128GB 546 GB/s, 10 W / 140 W; M5 Ultra 15 W / 300 W; Mac mini M5 Pro 3 W / 65 W | M5 Max 614 GB/s (128 GB needs the 40-core GPU), 7 W / 200 W; M5 Ultra 1,200 GB/s, 9 W / 385 W; Mac mini M5 Pro 307 GB/s, 6 W / 145 W | APPLE-MAC-STUDIO-SPECS, APPLE-MAC-STUDIO-POWER, APPLE-MAC-MINI-SPECS, APPLE-MAC-MINI-POWER | Vendor pages; load = Apple's maximum power figure for its measurement configuration |
| C-022 | 2026-11-07 | RTX 5070 Strata appliance | 504 GB/s; prefill 3,600 tok/s at 32K (spec 03 §2) | 672 GB/s (192-bit GDDR7 at 28 Gbps); prefill 2,800 tok/s at 32K | GURU3D-RTX-5070, NVIDIA-RTX-5070-FAMILY, YT-01 | 504 GB/s is the RTX 4070 value; YT-01 (the cited source) reports 2,800 tok/s |
| C-023 | 2026-11-07 | GPU load power | RTX Pro 6000 350 W; DGX Spark 90 W | RTX Pro 6000 600 W (Workstation Edition max); DGX Spark 140 W (GB10 TDP, 240 W power supply) | NVIDIA-RTX-PRO-6000, NVIDIA-DGX-SPARK, YT-16 | Vendor maximum values; idle values stay spec 03 / YT-16 |
| C-024 | 2026-11-07 | DGX Spark memory architecture | ~118 GB usable (spec 03) | `memory_architecture = discrete`, usable 128 × 0.90 = 115.2 GB | NVIDIA-DGX-SPARK, SPEC-03 | `MemoryArchitecture` has no NVIDIA unified member; 2.8 GB below the spec value. Contract change proposal for a later task |
| C-025 | 2026-11-07 | AA Intelligence Index v5 scores | Opus 5.5 58.4, Sonnet 5.5 48.2, GPT-6.1 52.0, Kimi K3.1 Pro 46.0, DeepSeek V4.1 Flash 32.5, Gemma 4 12B 14.5, Qwen Flash Next 27.8, Gemini 3.1 Pro 49.5 | 59.1, 54.5, 54.6, 46.5, 32.6 (1017 revision); Gemma 4 12B, Qwen Flash Next, Qwen 3.6-35B-A3B, gpt-oss-120b and Gemini 3.1 Pro absent | IND-01 | AA v5.0.1 page data on 2026-11-07. Consequence: Gemma 4 12B, gpt-oss-120b and Gemini 3.1 Pro have no quality score at all and fail every Quality_Floor (Req 31.6) until a score is published |
| C-026 | 2026-11-07 | Gemini 3.1 Pro EU endpoint | Vertex AI EU (spec 03 §3.3) | `eu_pinned_endpoint = false`; only `gemini-3.1-pro-preview` exists, priced for the Vertex AI global endpoint only; $2 / $12 / cache $0.20 (≤ 200K) | GOOGLE-VERTEX-PRICING, GOOGLE-GEMINI-PRICING | Vertex AI lists no non-global price for this model |
| C-027 | 2026-11-07 | GLM 5.3 Flash | Apache 2.0; 128K context | MIT; 1,048,576 context; sparse attention with latent KV (kv_lora_rank 512) → `multi-head-latent` | HF-GLM-5-3-FLASH | Model card and config.json |
| C-028 | 2026-11-07 | Calibrated weight footprints | Qwen 3.8-27B INT3/INT4/INT8 12.5 / 16.7 / 29.5 GB; Qwen 3.6-35B-A3B INT4 17 GB; gpt-oss-120b INT4 66 GB; Gemma 4 12B 128K context | 13.1 / 17.6 / 29.0 GB; 22.4 GB; 63.0 GB; Gemma 4 12B 262,144 context | UNSLOTH-GGUF, HF-GEMMA-4-12B | One mapping for all models: INT2/INT3/INT4/INT8 = Unsloth UD-Q2_K_XL / UD-Q3_K_XL / UD-Q4_K_XL / Q8_0, which reproduces the 111.3 GB Flash Next INT4 reference of Req 16.6 |
| C-029 | 2026-11-07 | Terminal-Bench and SWE-bench versions | "Terminal Bench" without version (Opus 5.5 89.4, Qwen 3.8-27B 2.1 = 73.0) | `terminal_bench` = vendor-reported Terminal-Bench 2.x (2.1, or 2.0 for Qwen 3.6-35B-A3B); `swe_bench` = SWE-bench Pro; Opus 5.5 89.4 → absent | HF-QWEN-3-8-27B, HF-QWEN-3-6-35B-A3B, HF-GLM-5-3-FLASH, HF-DEEPSEEK-V4-1-FLASH, HF-QWEN-3-8-FLASH-NEXT | Frontier vendors and Kimi now report Terminal-Bench 4.0, which is not comparable with 2.x; API models and Kimi use the scaled AA fallback (Req 31.4). The version is in each record's note |
| C-030 | 2026-11-07 | Hetzner rental details | GEX430 512 GB RAM (assumption); region DE/FI | GEX430 128 GB DDR5 ECC; GEX63 128 GB DDR5; both only in Helsinki (FI, HEL1) | HETZNER-GEX63, HETZNER-GEX430, HETZNER-GPU-MATRIX | Vendor pages |
| C-031 | 2026-11-07 | Additional EU GPU providers (user request) | only Hetzner GEX63 / GEX430 | added `hetzner-gex131` (1× RTX PRO 6000, from €1,499 + €1,499 setup, FSN1/HEL1), `nebius-rtx-pro-6000-1x` ($1.80/GPU-h), `nebius-h100-8x` (8 × $4.50/GPU-h), `fireworks-h100-8x-eu` (8 × $8.00/GPU-h × 1.5 region-restricted, EU_FRANKFURT_1); monthly = hourly × 730 h. Not added: Deutsche Telekom Industrial AI Cloud (Munich, DGX B200 and RTX PRO servers, no public price list), OVHcloud (at most 4× H100 per instance; H100 valid node count is {8}), Scaleway (pricing page returned HTTP 403) | NEBIUS-PRICES, NEBIUS-REGIONS, FIREWORKS-PRICING, FIREWORKS-REGIONS, HETZNER-GPU-MATRIX, TELEKOM-IAC, OVHCLOUD-PRICES | Only offers that map to a catalog GPU and a valid node count become rentals. Fireworks is a US company with an EU-restricted deployment; its host RAM is an assumption |
| C-032 | 2026-11-07 | Hardware prices of spec 03 | EUR street prices | unchanged, tier `assumption` (SPEC-03) | SPEC-03, YT-06, YT-16 | Not web-verified: Apple's store shows only base-configuration prices; several spec 03 EUR figures equal the USD figures of their YouTube sources (Strix Halo 3,449; DGX Spark 6,950) |
| C-033 | 2026-11-07 | DGX Spark 4-node ring kit | €27,368 for 4 Sparks incl. ring kit (spec 03 §2) | no cabling kit recorded | SPEC-03 | The kit price is below 4 × €6,950 = €27,800, so the spec values contradict each other |
| C-034 | 2026-11-07 | Tiered-offload KV pool (Strata) | design.md Sizing_Engine step 6: subtract min(weights, usable VRAM) from the VRAM pool | the Shelf (N × `system_ram_offload_gb`) takes the weights first; weights on device = max(0, weights − Shelf); pool = usable VRAM − weights on device − runtime overhead | requirements 18.6, design.md § "Sizing_Engine", SPEC-01 Stage 1 §5 | With the design formula every model larger than the VRAM gets pool = −overhead and is always OOM, so the offload of Req 18.6 could never make a model fit. With the chosen rule a model is OOM exactly when it exceeds VRAM + Shelf − overhead; KV cache stays in VRAM |
| C-035 | 2026-11-07 | Decode formula: Qwen 3.8 Flash Next on M5 Ultra | Req 20.1 formula: 1,200 / (6 × 4/8 × 1.05) × 0.425 = 161.9 TPS at 8,192 tokens, × δ_ctx 0.60 = 97.1 TPS at 131,072 tokens | measured 108 TPS (short context) and 61 TPS (128K) stay Benchmark_Records and win (Project Rule 4); calibration APE 49.9 % and 59.3 % (> 30 %) | YT-21, SPEC-01 Stage 2 | Known calibration deviation. The measured speed equals η ≈ 0.28 instead of 0.425 (180B stored parameters with n-gram embedding and MTP head, C-017; MoE routing overhead on MLX). η_moe stays 0.425 because the Mac mini Qwen 3.6-35B-A3B record (YT-18) agrees within 5.1 %. Measured on the M5 Ultra 512 GB, stored on the 256 GB item (same chip and 1,200 GB/s) |
| C-036 | 2026-11-07 | Decode formula: DeepSeek V4.1 Flash INT2 on RTX 5070 Strata | Req 20.1 formula with the VRAM bandwidth: 672 / (16 × 2/8 × 1.05) × 0.425 = 68.0 TPS | measured 4.6 TPS (midpoint of 4.3–4.9 TPS with the DDR5 expert cache) stays the Benchmark_Record; calibration APE 1,378 % | YT-07, YT-01, SPEC-01 Stage 1 §5 | Known calibration deviation: on a tiered-offload appliance the offloaded experts stream from system RAM and NVMe over PCIe, not from the 672 GB/s VRAM. Req 20.1 has no offload-bandwidth term; requirement change proposal for a later task |
| C-037 | 2026-11-07 | Decode and prefill Benchmark_Records (Task 6) | no `data/benchmarks/decode.json` / `prefill.json` | 6 decode records and 1 prefill record from the spec 06 source summaries (tier `community`, note `single-source`). Where the summary does not state them, `context_tokens` = 8,192 ("short context") and `precision` = INT4 (4-bit; DeepSeek on Strata INT2, the 2-bit build of YT-01). The GB10 record (YT-16) is stored on `dgx-spark-128gb` (same 273 GB/s for 64 GB and 128 GB); the Strata prefill record (YT-01) is assumed to use Qwen 3.8 Flash Next | YT-01, YT-02, YT-06, YT-07, YT-16, YT-18, YT-21, specs/06 | Not stored yet: gpt-oss-120b on Strix Halo, 46 TPS (YT-02) and 51.1 TPS (YT-06), formula 40.6 TPS (APE 11.7 % / 20.5 %), because `tests/unit/test_mvp_catalog.py` (outside the Task 6 scope) deletes `gpt-oss-120b.json` from a data copy and any record for that model then fails the dangling-reference check; add them when that test is in scope. Not stored: multi-node results (4× and 2× DGX Spark prefill, 8× RTX PRO 6000 8,700 tok/s, 8× DGX Spark Kimi 2.2 TPS) because `BenchmarkRecord` has no node count, so multi-node decode (D-08, C-011) cannot be calibrated yet; speculative-decoding results (MTP 26.5–36.6 TPS, MLX DFlash 40–44 TPS) because it has no speculative-mode field; results for models or hardware outside the catalog (Olares One, GLM 5.3 744B, Llama); and spec 01 figures without a source id (M5 Max 29.8 TPS, M5 Ultra 56/50/35 TPS). The only prefill record measures the same YT-01 value that `base_prefill_tps_at_32k` of the Strata item already holds (C-022), so the prefill MAPE of 0.0 % carries no information until independent prefill records are added. Contract change proposal: `nodes` and `speculative_mode` on `BenchmarkRecord` |
| C-038 | 2026-11-07 | Active hours per month: TCO_Engine vs Workload_Profile | requirements 22.3: H_active ∈ [0, 730] (H_idle = 730 − H_active); requirements 23.1 and `WorkloadProfile.active_hours_per_month`: integer 1 to 744 | the TCO_Engine rejects 731 to 744 hours with `EngineInputError("active_hours_per_month")` (Req 22.12); the Baseline_Engine accepts 1 to 744 (Req 24.10) | requirements 22.3, 22.12, 23.1, 24.10 | The two ranges contradict each other for 731–744 h (a 31-day month has 744 h, `hours_per_month` is 730). Applied literally; a profile with more than 730 active hours gets no on-premise TCO. Requirement change proposal: H_idle = max(0, 730 − H_active) or a 744-hour month in Req 22.3 |
| C-039 | 2026-11-07 | `TcoInput` has no target context or backend factor (Task 7) | design.md TCO_Engine: aggregate-throughput records match the target context (Req 23.3); eviction wait_h = target_context / (prefill × β) / 3600 (Req 22.8) | target context = round(`sizing.m_kv_single_gb` × 10⁹ / `sizing.kv_per_token_bytes`) (the Sizing_Engine computes M_kv_single = kv_per_token × context / 10⁹); wait_h uses the Performance_Engine prefill rate without β | design.md § "TCO_Engine", § "Performance_Engine" | `TcoInput` carries no `SizingOptions` and `src/ai_tco_dss/domain/` is outside the Task 7 scope. β = 1.0 is the default (optimized backend); with `enable_optimized_backend = false` the eviction wait time is understated by the factor 1/0.035. Contract change proposal: `options: SizingOptions` on `TcoInput` |
| C-040 | 2026-11-07 | Gateway fee provenance in Baseline C (Task 7) | requirements 24.11: Value_Origin lists the source_ids of the prices and Reference_Data used | Baseline C lists the token-price source_ids only; the gateway fee source (`ASSUMPTION-MVP` in `baselines.json`) is missing | requirements 24.11, design.md § "Baseline_Engine" | `BaselineInput.gateway_fee_usd` and `ApiCostInput.gateway_fee_usd` are plain floats, and `src/ai_tco_dss/domain/` is outside the Task 7 scope. Contract change proposal: `gateway_fee: Money` on both inputs |
| C-041 | 2026-11-07 | Hybrid resale boundary | Req 25.5 omits resale, while Req 25.3 requires the 100% local hybrid to equal the resale-adjusted on-premise timeline | Subtract the same local resale value from both on-premise and hybrid timeline series when enabled | requirements 25.3, 25.5, 26.3 | Preserve the local=100% equality; standalone HybridCost.cost_60m remains gross (its input has no resale switch) |
| C-042 | 2026-11-08 | Hybrid hard-filter contract gap | CandidateEvaluation lacks endpoint/context facts and component evaluations | Add filter facts and component results; evaluate each component, with reduced local demand | requirements 27.4, 28.3/7; design Decision pipeline | Scope extends to domain/results.py and three generated result schemas; details below |
| C-043 | 2026-11-08 | Rental RAM total versus per-node sizing | Design copies total rental RAM into a field multiplied by nodes | Construct per-node RAM as rental total / GPU count; preserve catalog total | RentalSpec; design rental sizing; requirements 18, 27.3 | Full hardware inputs are part of the local cache key; details below |

| C-044 | 2026-11-09 | Low-utilization financial inference | Requirement 23.6 predicts fixed costs are likely to exceed API costs below 55% utilization | Neutral low-utilization caution plus actual matched-horizon cost comparison; show utilization as a percentage | Req 23.6; engines/tco.py; tests/unit/test_tco_accounting.py; author screenshot/fix request | Author-approved wording correction: default 4.7% utilization still yields modeled local TCO $308,347.20 versus Baseline C $325,669.51; thresholds and numerical formulas unchanged. See spec 09 follow-up notice. |

| C-045 | 2026-11-10 | Requested context | only 128K floor checked | reject model limits below requested context | project review reproduction | Author-authorized correctness fix |
| C-046 | 2026-11-10 | Wait-time cost | candidate omitted reference API latency | candidate and timeline use same reference latency; backend options reach eviction formula | project review reproduction | Restores parity and backend factor |
| C-047 | 2026-11-10 | Active monthly hours | TCO rejected 731-744 | accept 1-744; idle hours = max(0, configured month - active) | C-038 | Resolves mismatch without negative idle energy |
| C-048 | 2026-11-10 | Performance preference | unbounded speed/latency reward | default scores saturate at user targets; Expert can reward excess | author request | Preference policy, not empirical calibration; raw metrics retained |
| C-049 | 2026-11-10 | Hybrid anchor | cheapest memory-feasible local candidate | cheapest local passing constraints at routed demand | C-042 | Still one illustrative local anchor, not exhaustive optimization |
| C-050 | 2026-11-10 | Derived latency origin | measured prefill implies measured TTFT | formula TTFT retains source IDs with formula origin | project review | Direct TTFT measurements still win |

| C-051 | 2026-11-10 | MacStories benchmark hardware attribution | C-035 and supplied video-assistant report attribute M5 measurements to 512 GB | original article identifies M5 Ultra 256 GB and M3 Ultra 512 GB; earlier assistant attribution is corrected | https://www.macstories.net/stories/m5-ultra-mac-studio-review-the-dream-mac-for-local-ai-agents/ | Evidence review only; do not reinterpret the original benchmark as a 512 GB test. See docs/BENCHMARK_VERIFICATION_REVIEW.md |
| C-052 | 2026-11-10 | Long-context measurement and comparability | stored 61 TPS at 131072; supplied report says exactly 128000 | original row reports 60.6 TPS at 130522 input tokens with MTP depth 3, distinct from the 108 TPS summary series | MacStories original benchmark; C-051 source | Runtime/protocol matching required before replacing calibration data; coefficients and xfails unchanged |
| C-053 | 2026-11-10 | Supplied Strata storage interpretation | report adds 111 GB Engram to a 257 GB total | maintainer documents 257 GB including model, Engram and drafter | https://github.com/Niko1221/Strata/blob/main/docs/DEEPSEEK41.md | Correct supplied-report interpretation; generic bus estimates remain hypotheses |
| C-054 | 2026-11-10 | Benchmark matching and calibration eligibility | Generic precision and assumed context could select measurements across runtime/speculation/deployment conditions; six decode rows were treated as calibration | Actual prompt and configured capacity separated; exact execution conditions required; incomplete observations retained and exported with reasons; offload has no VRAM-only performance fallback | C-035 through C-037, C-051 through C-053; MACSTORIES-M5-2026; STRATA-DEEPSEEK41; docs/CALIBRATION_AND_COST_REVIEW.md | Import five MacStories prompt-series observations and separate Strata 4.7 TPS observation; preserve all six legacy decode observations and three historical numerical xfails. No coefficient tuning. |
| C-055 | 2026-11-10 | Cheapest preset | 50% cost weight could select $308347 instead of a qualifying $221568 option for one user | Cost-only weights (1,0,0,0,0,0); hard filters still apply; Expert custom weights remain explicit overrides | Reproduced repository scenario; author bug report | Cheapest now means lowest modeled admissible 60-month cost for default preset weights, in SAW and TOPSIS. No favored hardware rule. |
| C-056 | 2026-11-10 | Small self-managed ownership cost assumptions | Half an operations FTE plus economic costs applied to a one-user comparison without a visible Normal-mode choice | Explicit enterprise/self-managed cost model; self-managed owned hardware counts purchase once and power, PUE 1, no staffing/NIM/economic losses/resale | Author confirmed self-managed comparison; engine trace of one-user scenario | Enterprise inputs remain intact; default enterprise API behavior retained. Self-managed rental still incurs rental charges; API prices and gateway assumptions remain separate. Workload/quality filters do not change. |


| C-057 | 2026-11-11 | Metric-specific matching and measured prefill accounting (U-01) | Universal field completeness required app backend/output/drafter facts even when inapplicable; measured prefill received beta twice in latency/eviction cost; TTFT matched decode context | Require physical execution facts by metric; output length for generation, drafter config only when enabled; app beta applies only to formula prefill; TTFT matches effective workload prompt and excludes unobserved eviction rebuilds; reject prompt beyond documented capacity | docs/BENCHMARK_MATCHING_POLICY.md; primary llama-bench/vLLM/NVIDIA metric definitions linked there (accessed 2026-11-11); synthetic regressions in tests/unit/test_matching_policy.py | No empirical values or coefficients changed; 13 observations remain excluded and calibration unfinished. Unknown KV/runtime facts remain unknown. No contract/schema change. |

| C-058 | 2026-11-11 | Throughput run matching and calibration applicability | Decode/aggregate used output-length metadata hints even when workload output differed; calibration could predict for a model OOM or attempt API-only local sizing | Override query output length with modeled generated tokens including thinking/tokenizer effects; explicitly exclude local formula requests for API models, prompts beyond model limit and configurations the current sizing model cannot represent | tests/unit/test_calibration_followup.py: seven failing regressions before correction; U-01 policy follow-up | No empirical data or coefficients changed. Sizing exclusions describe a model limitation, not measured failure. Engine version 0.1.3; schema/API types regenerated. Independent calibration remains unfinished. |

| C-059 | 2026-11-11 | New Strata evidence: requested versus actual output | Head-to-head README says decode = 256 tokens | Six RTX 5070 Strata raw rows contain 94–132 generated tokens; preserve each actual count separately from the request setting | Niko1221/Strata at c1ff07f1a1817594811c960039571c6e268fe89a, bench/results/2026-10-06-llamacpp-0.6.0/README.md and 5070/raw/strata-setup.jsonl; archived with hashes under docs/evidence/public_benchmarks_2026-11-11 (accessed 2026-11-11) | Evidence-only contradiction; this Qwen/speculative dataset does not fill the original DeepSeek run metadata or validate an offload formula. No production observation changed. |
| C-060 | 2026-11-11 | Author-approved simultaneous peak capacity (U-05) | Monthly-only users-served filter admitted a three-slot Max INT3 configuration for five peak requests | Separate peak_capacity hard filter requires sized resident slots >= full requested peak for each local deployment/component; rentals choose a peak-fitting precision when available | Author selected Require simultaneous capacity; seven new failing regressions in tests/unit/test_peak_capacity.py; docs/PEAK_CAPACITY_POLICY.md | Extends historical Req 28.1 under explicit author instruction. Preserve monthly capacity, costs, workload defaults and unknown loaded latency. No queueing, seat pooling or fractional hybrid peak inferred. Engine 0.1.4; affected schema/API metadata regenerated. |

| C-061 | 2026-11-12 | Supplied YouTube-agent Strata Mac timing/protocol | Report labels needle rates isolated prefill and short/story baseline uncached | Primary MAC.md describes a first-token timing boundary, leaves the engine version unrecorded and does not establish the decode cache protocol | Strata c1ff07f1a1817594811c960039571c6e268fe89a docs/MAC.md; archived under docs/evidence/user_report_review_2026-11-12 (accessed 2026-11-12) | Preserve reported rates as qualified evidence; isolated-prefill and cache fields remain unknown. No catalog observations or coefficients changed. |
| C-062 | 2026-11-12 | Supplied Strata concurrent memory labels | Report labels 8.3 / 12.0 / 14.0 / 16.0 GB as KV/state memory | Source identifies total engine memory; per-sequence running state/KV is separately 0.65 GB at configured 36864 context | Same pinned MAC.md as C-061, Several requests at once | Do not calibrate KV bytes or infer occupied prompt length from engine totals. Capacity policy unchanged. |
| C-063 | 2026-11-12 | Supplied MacStories repetition/output metadata | Report combines long-context series with median-of-three metadata and later calls generated output count unknown | Primary identifies one run per size and exactly 512 generated tokens for that series; three-run medians describe a separate session | MacStories original article, Charts 1 to 4 and separate quantization session; archived macstories-response.html under user_report_review_2026-11-12 (accessed 2026-11-12) | Existing production rows already preserve 512 actual tokens; retain their artifact/KV exclusions and historical discrepancies. No rewrite needed. |
| C-064 | 2026-11-12 | Supplied DGX long-context pool attribution | Report assigns five and six concurrent long-prompt tests to the 31.15 GB FP8 KV pool | Pinned source assigns five-request 652 s last-TTFT test to earlier 27 GB pool and six-request 790 s test to 31.15 GB pool | devopsfortunato/Qwen3.8-Flash-Next-FP4-Local-DGX-Spark 6aab1a5589dfd0cd93cb0ffc8d50392cfaffa9b6 README.md; archived under user_report_review_2026-11-12 (accessed 2026-11-12) | Store as separate runs; do not transplant current recipe settings to historical measurements. No performance coefficient or simultaneous-capacity rule changed. |
| C-065 | 2026-11-12 | Supplied v1.1 MacStories hardware/workload attribution | 103.9 / 97.3 / 96.6 / 89.1 TPS assigned to M5 Ultra four-quant comparison | These are M3 Ultra code results; M5 Ultra prose is 111.6 / 100.0 / 95.2 / 86.8 and code is 142.9 / 132.6 / 122.8 / 119.0 TPS in Q4/Q5/Q6/Q8 order | Previously archived MacStories article, four-precision chart; docs/YOUTUBE_EVIDENCE_REPORT_V11_REVIEW_2026-11-12.md (accessed 2026-11-12) | Keep M3 only as historical attribution context. Preserve MTP depth three, SSD embedding placement for Q6/Q8 and Q4 retest distinction. No M5 512 GB validation or production import. |
| C-066 | 2026-11-12 | Supplied v1.1 MacStories memory phase | 134 / 153 / 101 / 130 GB called generic build peak memory | Those are M5 loading peaks; sampled answering process peaks are 155 / 179 / 156 / 187 GB in Q4/Q5/Q6/Q8 order | Same archived primary as C-065, memory chart/test details | Retain phase and process-footprint boundary; neither figure is KV-only. Q5 memory uses a later pass, not its timed performance session. |
| C-067 | 2026-11-12 | Supplied v1.1 oMLX live cache dtype | FP16 KV assigned to t9sos5mz and b0zessb6 | Live cache tensor dtype is not established by the archived settings; TurboQuant is disabled | omlx.ai benchmark records t9sos5mz and b0zessb6; raw HTML/settings under docs/evidence/user_report_v11_review_2026-11-12 (accessed 2026-11-12) | Keep dtype unknown. Model settings/caps do not supply actual request token counts or event logs. Preserve enabled MTP and artifact identity. |
| C-068 | 2026-11-12 | Supplied v1.1 Sushi timing and occupied context | Reciprocal 17.34-17.88 ms/forward presented as roughly 55.9-57.7 TPS at 131072 context | These are forward-meter timings and derived reciprocals; neither measured end-to-end decode nor occupied 128K depth is established by that row | beamivalice/sushi 404e8b386b8ece983806cf190a780d6001b68072 docs/perf-baselines.md, separate forward-meter and llmprobe rows (accessed 2026-11-12) | Do not turn a configured ctx or forward kernel timer into a long-context generation observation. Preserve other measured llmprobe rows separately. |
| C-069 | 2026-11-12 | Supplied v1.1 Heretik full-context fill timing | Approximately 28-minute one-shot 262K fill grouped with measured isolated pp512 rates | Source obtains 28 minutes by integrating its incremental depth curve; no recorded one-shot full-fill timer supplied | heretik.io/qwen38-flash-next-262k-macbook, archived heretik.html (accessed 2026-11-12) | Label full-fill duration as estimate. Seven pp512/tg128 depth points remain source measurements with one trial each. No coefficient fitting. |
| C-070 | 2026-11-12 | Supplied 512 GB report's MacStories speculation | Existing M5 Ultra 256 GB 60.6 / 74.7 TPS ladder labelled MTP OFF | Archived source specifies multi-token prediction depth 3 | Previously archived MacStories article, Test details; docs/M5_ULTRA_512GB_EVIDENCE_REVIEW_2026-11-12.md | Keep the source conditions and 256 GB hardware. No reuse as a non-speculative or 512 GB observation. |
| C-071 | 2026-11-12 | Supplied 512 GB report's cross-run memory attribution | Qwen Q6 memory partly borrowed from a 256 GB run (150.5 GB); DeepSeek footprint stated roughly 292-406 GB | Qwen 512 GB record 2zvzoy8b: selected peak 150.3, resource active 149.81, footprint 154.96 GB; DeepSeek selected peaks 404.1-411.8 and resource footprints 411.99-418.92 GB across acquired records | Permanent omlx.ai records archived under m5_512gb_report_review_2026-11-12 (accessed 2026-11-12) | Keep selected metrics, session resource summaries, memory phases and machines distinct. Do not transplant memory from a matched model name. |
| C-072 | 2026-11-12 | Supplied 512 GB report's exact gpt-oss context | Leaderboard shorthand 195k converted to 195000 actual tokens | Permanent odblvo21 record reports Context 200000 | omlx.ai/benchmarks/performance/odblvo21 (accessed 2026-11-12) | Preserve reported context separately from the recipe's max_context_window 128000. Actual runtime enforcement and token events remain unresolved. |
| C-073 | 2026-11-12 | Supplied 512 GB report's HumanEval causal/sampling claim | Higher output cap said to recover 9.7-15.2 points; both compared runs described as deterministic | Acquired 132/164 and 148/164 logs are distinct settings/artifact labels/runtimes; earlier 32 failures include 24 stop and 8 length; later settings force_sampling true | oMLX qvlxvz1i and 6b3p2k87 pages plus original gzip question logs (accessed 2026-11-12) | Recount flags without executing code. Score difference is not an isolated causal effect of output cap; exact tool-workload validity remains open. |
| C-074 | 2026-11-12 | Supplied 512 GB report's Sushi quality denominator | Score 94/100 described as success on 100 multi-step tool calls | Archived Sushi README reports score 94 from 182/194 points; score 90 from 174/194 points for 4bpw | Previously archived beamivalice/sushi 404e8b386b8ece983806cf190a780d6001b68072 README.md | Preserve published scores/points; do not infer a 100-call sample, success rate, confidence interval or DSS quality-floor equivalence. |
| C-075 | 2026-11-12 | Supplied 512 GB report's Apple TTFT transcription | Qwen 65536-input two-M5 tensor-parallel TTFT 29.0 s | Source table's 65K tab gives 29.4 s | Apple ML Research mlx-distributed-inference, embedded source table2; archived apple/mlx-distributed.html (accessed 2026-11-12) | Preserve both input-size tabs and node/parallelization identities. No transplant to single-node Flash-Next or concurrent serving. |
| C-076 | 2026-11-12 | New enterprise report's GLM serving metrics | Sustained p50/p90 TTFT 0.90/1.83 vs 17.57/44.82 s; generation 11.9 vs 4.5 TPS; burst output 359.7 vs 100.3 TPS | Retrieved Backboard source: sustained p50 3.24 vs 357.50 s, p90 61.20 vs 504.90 s, median generation 15.8 vs 7.7 TPS; burst output 165.5 vs 63.5 TPS | backboard.io/blog/glm-5-3-inference-throughput-vllm; new enterprise_report_review_2026-11-12 archive (accessed 2026-11-12) | Preserve differing admission/completion populations and preliminary internal status; correct review, retain original report, no production import. |
| C-077 | 2026-11-12 | New enterprise report's H100 AgentX values and concurrency | November 1 source; c16 p90 TTFT 1.21 s, interactivity 47.6, output 87.1 TPS/GPU; c treated as simultaneous sessions/requests | Retrieved November 6 source: c16 1.41 s, 71.6 TPS/user, 90.7 output TPS/GPU; all-eight-GPU table independently rounded to 726 TPS; concurrency is live session trees, not simultaneous HTTP requests | backboard.io/blog/qwen-flash-next-h100-full-precision (accessed 2026-11-12) | Preserve total-token/output, GPU/node and session/request denominators. Do not use these trees as resident request slots or isolate engine effects from BF16/FP8 differences. |
| C-078 | 2026-11-12 | New enterprise report's Petronella hardware and precision | 61/349/583 TPS attributed to four H200; fast GB300 peer path called NVFP4; input/rate divisions presented as TTFT | Primary tables attribute 61/349/583 to four RTX PRO 6000 Blackwell Max-Q; fast GB300 path uses MXFP4 experts and RTX cold-expert peer; reconstructed TTFT remains estimated | petronellatech.com/ai/llm-benchmarks/models/deepseek-v4-1-flash/; saved web-tool excerpts; direct HTTP 403 preserved (accessed 2026-11-12) | Do not transplant hardware, quantization or latency metadata. Raw internal source paths remain acquisition leads. |
| C-079 | 2026-11-12 | New enterprise report's Pi routing API/configuration | registerVirtualModel resolve(context) described as per-turn dispatch; typesafe-system-one called classifier.provider | Pinned Pi docs use route(request, ctx) per request, including continuations/retries; Jev classifier.provider is typesafe, adapter API is typesafe-system-one | Archived Pi 841dc6050b5f0014733ee40436f8ad7cf80c93fe docs; npm @caph42/pi-jev-router 2.0.0, verified SHA-512, gitHead 75ad5b71940624ba29baf39ad0e7c51319db598e | Distinguish dispatch from classification boundaries, public package from Julien's unknown extension, policy fixtures from production measurement. No acquired source executed. |
| C-080 | 2026-11-12 | New enterprise report's low-bit tool-safety inference | Divergence/token agreement said to prove a minimum safe universal tool-calling floor | Publisher artifact recommendations and token proxies do not establish a universal task-success/schema-validity threshold or uniform INT2/INT3 quality | Previously archived Unsloth v3.0/v3.1/Qwen guides, ISTA card and original oMLX quality logs; ENTERPRISE_REPORT_REVIEW_2026-11-12.md | Preserve artifact-specific evidence and unknown workload transfer; C-074 already corrects repeated Sushi 94/100-scenarios error. No quality coefficient or score imported. |
| C-081 | 2026-11-12 | New enterprise report's Gemini 3.1 Pro capacity | 2M input context | Official Vertex model page lists 1,048,576 input tokens and global-only availability for gemini-3.1-pro-preview | cloud.google.com/vertex-ai/generative-ai/docs/models/gemini/3-1-pro; archived response (accessed 2026-11-12) | Correct evidence interpretation; existing catalog already has 1,048,576/global-only, so no catalog mutation. US/4K/batch third-party timing cannot fill EU/32K/128K streaming gaps. |
| C-082 | 2026-11-12 | New enterprise report's Revolut fact/guidance and cost boundary | Exact NVFP4 artifact, deployed >90% cache fraction, zero quality loss and invoice exclusions described as established facts | Slide verifies Together Dedicated Inference, 56 B200, reported +76% RPS and 14.26 to 1.68 s; talk provides FP4/TP/cache guidance, not run-linked artifact/cache/quality manifests or complete cost exclusions | Reused conference transcript plus newly downloaded and visually inspected afternoon-revolut.webp (accessed 2026-11-12) | Preserve source-reported results without inventing topology or cost boundary; spoken approximate RPS endpoints and slide percentage are not one exact reconciled ratio. |
| C-083 | 2026-11-12 | New enterprise report's OpenAI long-context multiplier wording | $2/$10 becomes $4/$15 described as a 2x jump | Official gpt-6.1-sol page specifies 2x input/cache and 1.5x output above 272K input for the full request; regional processing adds 10% where available | developers.openai.com/api/docs/models/gpt-6.1-sol; archived response (accessed 2026-11-12) | Retain exact model/processing identity and separate published price rules from absent matched API performance. No current model substituted or production price changed. |

## Contract Deviations (spec 04 → domain contracts)

2026-11-12 U-07 bounded extension: `domain/fleet.py` adds `ReplicaCapacity`,
`FleetSizingInput` and `FleetSizingResult` for an opt-in resource-bound planner.
These are separate from existing recommendation/scenario contracts and exported
API schemas. The [scope](../docs/FLEET_PLANNING_SCOPE_2026-11-12.md) requires explicit
spares, separate request/retained/output constraints and visible unknowns. No current
peak policy, candidate, coefficient, catalog value or endpoint was changed.

Task 9 scope extension authorized by the 2026-11-08 implementation request:
`domain/results.py` and the generated `schemas/{Recommendation,ScenarioResult,TcoProjection}.json`
are included to resolve C-042. Existing fields and constructors remain compatible.

- **C-042 (2026-11-08): hybrid filter evidence.** Old: `CandidateEvaluation` carried only
  weighted metrics, with no endpoint/context facts; `FilterInput` has no catalog. New:
  `model_max_context_tokens`, `api_has_eu_endpoint` and `components` (local and API
  evaluations) travel with each result. All nine rules inspect applicable components;
  failures identify every offending component. The local component is recomputed with
  `TcoInput.demand_share = local_offload_ratio`, keeping utilization, flags and traces
  consistent. Sources: requirements 27.4, 28.3/7 and design Decision pipeline.
- **C-043 (2026-11-08): rental host RAM units.** Old design wording copied the rental's
  total server RAM into a hardware field which sizing multiplies by node count. New:
  divide rental RAM by GPU count when constructing the per-node sizing input, preserving
  the rental total in the sizing result. Cache keys include the complete hardware input
  and demand share, preventing reuse across distinct host-memory configurations. Sources:
  `RentalSpec.system_ram_total_installed_gb`, design rental sizing and requirements 18/27.3.
  No catalog value changed; direct oracle tests cover all six rentals and every model.
"absent" means the field is not in spec 04; "removed" means the domain contract has no such field. All numeric catalog fields are additionally wrapped in `Sourced[T]` / `Money` (design D-01), and spec 04 `Dict`/`List` fields become tuples (D-03).

| Contract | Field / member | Old | New | Sources | Date |
|---|---|---|---|---|---|
| ElectricityTariffTier | CUSTOM | custom | removed | requirements 13.1 (exactly three tariffs); design.md "Enumerations" | 2026-11-07 |
| WorkloadProfile | working_days_per_month | absent | 22 (1–31) | requirements 14.2; design.md "Scenario contracts" | 2026-11-07 |
| EnterpriseFinancials | currency | EUR | USD | requirements 12.1; ledger C-005 | 2026-11-07 |
| EnterpriseFinancials | max_capex_budget | 100000.0 | removed (renamed max_capex_budget_usd) | requirements 28.6; design.md "Scenario contracts" | 2026-11-07 |
| EnterpriseFinancials | max_capex_budget_usd | absent | 100000.0, optional | requirements 28.6; design.md "Scenario contracts" | 2026-11-07 |
| EnterpriseFinancials | electricity_cost_per_kwh | 0.172 | removed (from electricity.json via electricity_tariff_tier) | requirements 13.1; design.md "Scenario contracts" | 2026-11-07 |
| EnterpriseFinancials | devops_annual_base_salary_eur | 75000.0 | removed (from staffing_hubs.json) | requirements 13.2; design.md "Scenario contracts" | 2026-11-07 |
| EnterpriseFinancials | employer_social_tax_multiplier | 0.04 | removed (from staffing_hubs.json) | requirements 13.2; design.md "Scenario contracts" | 2026-11-07 |
| EnterpriseFinancials | datacenter_infrastructure_multiplier | 1.0 | removed (moved to HardwareSpec.datacenter_multiplier) | design.md "Scenario contracts" | 2026-11-07 |
| EnterpriseFinancials | nvidia_nim_license_per_gpu_yr_eur | 4150.0 | removed (renamed nvidia_nim_license_per_gpu_yr_usd) | requirements 12.1; design.md "Scenario contracts" | 2026-11-07 |
| EnterpriseFinancials | nvidia_nim_license_per_gpu_yr_usd | absent | 4500.0 | design.md "Scenario contracts" | 2026-11-07 |
| EnterpriseFinancials | developer_hourly_opportunity_cost | 65.0 (EUR) | 72.57 (USD, 65 × 1.1165 rounded) | requirements 12.1; design.md "Scenario contracts" | 2026-11-07 |
| EnterpriseFinancials | include_resale_value | absent | False | requirements 26.4 | 2026-11-07 |
| EnterpriseFinancials | subscription_plan_id | absent | None (None → baselines.json default plan) | design.md "Scenario contracts" | 2026-11-07 |
| EnterpriseFinancials | cooling_pue | range [1.0, 2.0] | range [1.0, 3.0] (default unchanged) | requirements 22.3 | 2026-11-07 |
| EnterpriseFinancials | devops_fte_allocation | range [0, 5] | range [0, 10] (default unchanged) | requirements 22.4 | 2026-11-07 |
| SizingOptions | gpu_memory_utilization | absent | 0.90 | requirements 16.4; design.md "Scenario contracts" | 2026-11-07 |
| SizingOptions | runtime_overhead_gb | absent | 2.0 | requirements 17.5; design.md "Scenario contracts" | 2026-11-07 |
| SizingOptions | repo_workspace_gb | absent | 4.0 (2.5–6.0) | requirements 17.7; design.md "Scenario contracts" | 2026-11-07 |
| SizingOptions | runtime_format | absent | auto | requirements 17.4; design.md "Scenario contracts" | 2026-11-07 |
| HardwareSpec | memory_architecture | absent | required | requirements 16.1–16.4; design.md "Catalog contracts" | 2026-11-07 |
| HardwareSpec | gpus_per_unit | absent | required | requirements 22.5 (NIM per GPU); design.md "Catalog contracts" | 2026-11-07 |
| HardwareSpec | datacenter_multiplier | absent | required (moved from EnterpriseFinancials) | design.md "Catalog contracts" | 2026-11-07 |
| HardwareSpec | cabling_kits | absent | empty tuple | design.md "Catalog contracts" | 2026-11-07 |
| HardwareSpec | valid_node_counts | [1, 2, 4, 8] | required, per item | requirements 10.5 | 2026-11-07 |
| HardwareSpec | os_reserved_memory_ratio | 0.25 | None (unified memory only; Mac M5 Max 0.195, ledger C-013) | requirements 16.1; ledger C-013 | 2026-11-07 |
| HardwareSpec | system_ram_offload_gb | 0.0 | None | design.md "Catalog contracts" | 2026-11-07 |
| HardwareSpec | system_ram_total_installed_gb | 64.0 | None | design.md "Catalog contracts" | 2026-11-07 |
| HardwareSpec | base_prefill_tps_at_32k | required | None (optional, Req 21.7 path) | requirements 21.7 | 2026-11-07 |
| HardwareSpec | msrp_eur | required | removed (renamed msrp, optional Money) | requirements 12.3; design D-01 | 2026-11-07 |
| HardwareSpec | msrp | absent | None | design.md "Catalog contracts" | 2026-11-07 |
| HardwareSpec | street_price_eur | required | removed (renamed street_price, Money) | requirements 12.3; design D-01 | 2026-11-07 |
| HardwareSpec | street_price | absent | required | design.md "Catalog contracts" | 2026-11-07 |
| HardwareSpec | nvme_ssd_offload_gb | 0.0 | removed | design.md "Catalog contracts" (not used by any MVP formula) | 2026-11-07 |
| HardwareSpec | gpu_cores | None | removed | design.md "Catalog contracts" (not used by any MVP formula) | 2026-11-07 |
| HardwareSpec | per_core_prefill_score | None | removed | design.md "Catalog contracts" (not used by any MVP formula) | 2026-11-07 |
| HardwareSpec | host_cpu_cores | None | removed | design.md "Catalog contracts" (not used by any MVP formula) | 2026-11-07 |
| HardwareSpec | has_igpu_vision_offload | False | removed | design.md "Catalog contracts" (not used by any MVP formula) | 2026-11-07 |
| HardwareSpec | has_npu_audio_security_offload | False | removed | design.md "Catalog contracts" (not used by any MVP formula) | 2026-11-07 |
| HardwareSpec | monthly_cloud_rental_eur | None | removed (rentals are RentalSpec items in rentals.json) | requirements 10.6; design.md "Catalog contracts" | 2026-11-07 |
| ModelSpec | aa_v5_score | required | removed (Benchmark_Record aa_index_v5 in quality.json) | design D-06 | 2026-11-07 |
| ModelSpec | terminal_bench_score | None | removed (Benchmark_Record terminal_bench) | design D-06 | 2026-11-07 |
| ModelSpec | tokenizer_inflation_factor | 1.0 | removed (τ = 1.30 for family Claude, EngineParameters) | requirements 15.2; design.md "Workload_Engine" | 2026-11-07 |
| ModelSpec | calibrated_weights_gb | None | empty tuple of PrecisionValue | design D-03 | 2026-11-07 |
| ModelSpec | token_agreement_rates | None | empty tuple of PrecisionValue | design D-03 | 2026-11-07 |
| ModelSpec | active_kv_layer_ratio | 1.0 | None (engine uses 1.0 for standard-mha-gqa) | requirements 17.3 | 2026-11-07 |
| ModelSpec | ssd_streaming_lookup_gb | 0.0 | removed | design.md "Catalog contracts" (not used by any MVP formula) | 2026-11-07 |
| ModelSpec | openrouter_output_price_per_1m | None | removed (renamed open_weights_output_price_per_1m, Money) | requirements 24.6; design.md "Catalog contracts" | 2026-11-07 |
| ModelSpec | open_weights_output_price_per_1m | absent | None | design.md "Catalog contracts" | 2026-11-07 |
| ModelSpec | avg_benchmark_task_cost_usd | None | removed | design.md "Catalog contracts" (not used by any MVP formula) | 2026-11-07 |
| ModelSpec | api_input_price_per_1m | None | removed (api_prices.input_per_1m) | design.md "Catalog contracts" | 2026-11-07 |
| ModelSpec | api_output_price_per_1m | None | removed (api_prices.output_per_1m) | design.md "Catalog contracts" | 2026-11-07 |
| ModelSpec | api_cache_read_multiplier | 0.1 | removed (api_prices.cache_read_per_1m as an absolute price) | requirements 24.4; design.md "Catalog contracts" | 2026-11-07 |
| ModelSpec | api_prices | absent | None (required for commercial-api) | design.md "Catalog contracts" | 2026-11-07 |
| ModelSpec | eu_compliant | True | removed (eu_pinned_endpoint) | requirements 28.1; design.md "Catalog contracts" | 2026-11-07 |
| ModelSpec | eu_pinned_endpoint | absent | None (commercial-api only) | requirements 28.1; design.md "Catalog contracts" | 2026-11-07 |
| ModelSpec | api_decode_tps | absent | None | design.md "Performance_Engine" (API candidates) | 2026-11-07 |
| ModelSpec | api_ttft_s | absent | None | design.md "Performance_Engine" (API candidates) | 2026-11-07 |
| HardwareSizingResult | max_retained_agent_instances | required | removed (agent state reported as agent_state_memory_required_gb) | design.md "Result contracts" | 2026-11-07 |
| HardwareSizingResult | ttft_seconds | required | removed (renamed PerformanceResult.ttft_s, Metric) | design.md "Result contracts" | 2026-11-07 |
| SizingResult | precision | absent | required | design.md "Result contracts" | 2026-11-07 |
| SizingResult | requested_nodes | absent | required | requirements 18.2 | 2026-11-07 |
| SizingResult | alpha_scaling | absent | required | requirements 18.4 | 2026-11-07 |
| SizingResult | usable_memory_gb | absent | required | requirements 16.1–16.4 | 2026-11-07 |
| SizingResult | usable_memory_default_gb | absent | required | requirements 16.5 | 2026-11-07 |
| SizingResult | usable_system_ram_gb | absent | required, nullable | requirements 17.11 | 2026-11-07 |
| SizingResult | weights | absent | required Metric | requirements 17.1, 17.2 | 2026-11-07 |
| SizingResult | kv_per_token_bytes | absent | required | requirements 17.3 | 2026-11-07 |
| SizingResult | m_kv_single_gb | absent | required | requirements 17.5 | 2026-11-07 |
| SizingResult | kv_pool_gb | absent | required | requirements 17.5 | 2026-11-07 |
| SizingResult | max_usable_context | absent | required | requirements 19.1 | 2026-11-07 |
| SizingResult | traces | absent | required | requirements 36.1 | 2026-11-07 |
| PerformanceResult | prefill_tps | absent | required Metric, nullable | requirements 21.1 | 2026-11-07 |
| PerformanceResult | ttft_s | absent | required Metric, nullable (was ttft_seconds) | requirements 21.2 | 2026-11-07 |
| PerformanceResult | traces | absent | required | requirements 36.1 | 2026-11-07 |
| TcoProjectionResult | hardware_id | required | removed (TcoProjection.candidate carries the ids) | design.md "Result contracts" | 2026-11-07 |
| TcoProjectionResult | nodes_count | required | removed (renamed TcoResult.units) | requirements 22.1, 22.2 | 2026-11-07 |
| TcoProjectionResult | capex_total | required | removed (renamed TcoResult.capex, Metric) | design.md "Result contracts" | 2026-11-07 |
| TcoProjectionResult | sustained_gpu_utilization | required | removed (renamed TcoResult.utilization, nullable) | requirements 23.1, 23.3 | 2026-11-07 |
| TcoProjectionResult | monthly_on_prem_opex | required | removed (renamed TcoResult.monthly_opex) | requirements 22.13 | 2026-11-07 |
| TcoProjectionResult | monthly_eviction_loss_eur | 0.0 | removed (eviction_loss entry of TcoResult.monthly_opex, USD) | requirements 22.8, 12.1 | 2026-11-07 |
| TcoProjectionResult | monthly_cloud_baselines | required | removed (BaselineResult.a_monthly, b_monthly, c_monthly) | requirements 24 | 2026-11-07 |
| TcoProjectionResult | three_clocks_scorecard | required | removed (lifecycle clocks enter the risk criterion) | requirements 29.4 | 2026-11-07 |
| TcoProjectionResult | timeline_60_months | required | removed (renamed TimelineResult.points, exactly 60) | requirements 26.1 | 2026-11-07 |
| TcoProjectionResult | single_stream_break_even_years | None | None, now a Metric | requirements 26.8 | 2026-11-07 |
| TcoResult | units | absent | required | requirements 22.1, 22.2 | 2026-11-07 |
| TcoResult | gpu_count | absent | required | requirements 22.5 | 2026-11-07 |
| TcoResult | capex | absent | required Metric | requirements 22.1 | 2026-11-07 |
| TcoResult | monthly_opex | absent | required | requirements 22.13 | 2026-11-07 |
| TcoResult | monthly_opex_total | absent | required | requirements 22.13 | 2026-11-07 |
| TcoResult | aggregate_tps | absent | required Metric, nullable | requirements 23.2, 23.4 | 2026-11-07 |
| TcoResult | capacity_tokens_month | absent | required, nullable | requirements 23.1 | 2026-11-07 |
| TcoResult | utilization | absent | required, nullable | requirements 23.1, 23.3 | 2026-11-07 |
| TcoResult | capacity_insufficient | absent | required | requirements 23.3, 23.7 | 2026-11-07 |
| TcoResult | resale_retention_3yr | absent | required | requirements 22.9 | 2026-11-07 |
| TcoResult | cost_60m | absent | required | requirements 27.1 | 2026-11-07 |
| TcoResult | warnings | absent | required | requirements 23.6 | 2026-11-07 |
| TcoResult | traces | absent | required | requirements 36.1 | 2026-11-07 |
| BaselineResult | reference_model_id | absent | required | requirements 24.4 | 2026-11-07 |
| BaselineResult | a_monthly | absent | required Metric | requirements 24.1 | 2026-11-07 |
| BaselineResult | b_monthly | absent | required Metric | requirements 24.4 | 2026-11-07 |
| BaselineResult | c_monthly | absent | required Metric | requirements 24.5 | 2026-11-07 |
| BaselineResult | currency | absent | USD | requirements 24.11 | 2026-11-07 |
| TimelineResult | anchor_candidate_id | absent | required | design D-09 | 2026-11-07 |
| TimelineResult | rental_id | absent | required | requirements 25.1 | 2026-11-07 |
| TimelineResult | hybrid_api_model_id | absent | required | requirements 25.2 | 2026-11-07 |
| TimelineResult | points | absent | required, exactly 60 (was timeline_60_months) | requirements 26.1 | 2026-11-07 |
| TimelineResult | include_resale | absent | required | requirements 26.4 | 2026-11-07 |
| MonthlyTcoPoint | baseline_d_openrouter_value_cumulative | required float | required, nullable (Baseline D may be unavailable) | requirements 24.6; design.md "Result contracts" | 2026-11-07 |

| EnterpriseFinancials | max_tco_budget_usd | absent | optional 60-month USD budget | C-048; author request | 2026-11-10 |
| DecisionOptions | reward_excess_performance | absent | false by default, Expert override | C-048 | 2026-11-10 |
| TcoInput | options | absent | default SizingOptions, service supplies actual options | C-046 | 2026-11-10 |
| RankingInput | tps_target | absent | optional score saturation target | C-048 | 2026-11-10 |
| RankingInput | ttft_target | absent | optional score saturation target | C-048 | 2026-11-10 |
| ScenarioResult | catalog_fingerprint | absent | optional SHA-256 snapshot identifier | review provenance fix | 2026-11-10 |
| ScenarioResult | engine_version | absent | 0.1.2 | review reproducibility fix; C-054-C-056 | 2026-11-10 |

| EnterpriseFinancials | cost_model | absent | enterprise (default) or self-managed | C-056; author confirmation | 2026-11-10 |
| SizingOptions | benchmark_conditions | absent | optional exact deployment execution conditions, unknown by default | C-054 | 2026-11-10 |
| SizingOptions | performance_prompt_tokens | absent | optional actual prompt for measured lookup, independent of target context capacity | C-054 | 2026-11-10 |
| BenchmarkRecord | prompt_tokens | absent | optional actual measured prompt; never inferred from legacy context | C-054 | 2026-11-10 |
| BenchmarkRecord | configured_context_tokens | absent | optional configured capacity, separate from measured prompt | C-054 | 2026-11-10 |
| BenchmarkRecord | conditions | absent | optional BenchmarkConditions; missing facts stay null | C-054 | 2026-11-10 |
| BenchmarkRecord | uncertainty_reasons | absent | immutable explicit reasons excluding uncertain observations | C-054 | 2026-11-10 |

## Okabe-Ito Archetype Mapping
| Archetype (spec 05 §2.2) | Original hex | Okabe-Ito hex | Line style / fill |
|---|---|---|---|
| Sovereign Per-Seat Workstation | `#06B6D4` | `#56B4E9` sky blue | solid, 3 px |
| Sovereign Centralized Server / PD-Disagg | `#3B82F6` | `#0072B2` blue | solid, 4 px |
| Heterogeneous Modality / Scavenged Rig | `#6366F1` | `#F0E442` yellow | solid, 3 px, black marker outline |
| Dedicated EU Cloud GPU | `#10B981` | `#009E73` bluish green | dash-dot, 2.5 px |
| Baseline C (EU-pinned API) | `#F59E0B` | `#E69F00` orange | solid, 3 px |
| Baseline B / D (global API / OpenRouter value) | `#8B5CF6` | `#000000` black | dotted, 2 px (D adds diamond markers) |
| Baseline A (consumer subscription) | `#F43F5E` | `#CC79A7` reddish purple | dashed, 2 px + `[NON-COMPLIANT / BLOCKED]` when ineligible |
| OOM / Thermal / Eviction Warning | `#EF4444` | `#D55E00` vermillion | diagonal hatch `pattern_shape="/"` |
| Hybrid Split (not in §2.2) | — | `#E69F00` orange | dash, 2.5 px |

Within one figure, every pair of archetypes differs in colour or style (Hybrid shares orange with Baseline C but uses dash, not solid).

## Calibration Known Deviations

Historical unmatched-condition diagnostics, retained as three strict xfails. These are not comparable calibration errors (C-054). The current eligibility report excludes the source observations with explicit reasons.
| Entry ID | metric | model_id | hardware_id | source_id | Reason |
|---|---|---|---|---|---|
| C-035 | decode_tps | qwen-3-8-flash-next | mac-studio-m5-ultra-256gb | YT-21 | formula 161.9 / 97.1 TPS vs measured 108 / 61 TPS at 8,192 / 131,072 tokens (APE 49.9 % / 59.3 %); η_moe 0.425 overestimates this MoE on MLX |
| C-036 | decode_tps | deepseek-v4-1-flash | rtx-5070-strata-64gb | YT-07 | formula 68.0 TPS uses the VRAM bandwidth; offloaded experts stream from system RAM (measured 4.6 TPS, APE 1,378 %) |

## Assumptions
| Name | Value | Rationale | Used by (requirement) |
|---|---|---|---|
| Working_Days_Per_Month | 22 | typical working month | 14.1, 14.4 |
| Requests_Per_User_Per_Day | 40 | dummy until PowerBI data | 14.1 |
| Utilization definition | demanded output tokens ÷ capacity tokens | design D-07 | 23.1 |
| Capacity fallback | n = min(U_max, 64 × nodes), E(n) = 1/(1 + 0.03(n−1)), cap = nodes × prefill_32k | saturating batching | 23.4 |
| Resale curve | linear to r_resale_3yr at 36 months, floor 0 | simple straight-line | 22.9 |
| include_resale_value | false | conservative TCO | 26.4 |
| Context-match tolerance | 0.25 | ±25 % context still comparable | 9.5 |
| η_engine | 0.70 dense, 0.425 MoE | midpoints of spec 01 ranges | 20.2 |
| γ_spec | 1.0 / 1.425 / 1.80 / 2.75 | midpoints of spec 01 ranges | 20.3 |
| δ_ctx breakpoints | (8K 1.00), (32K 0.89), (128K 0.60), (256K 0.50), (1M 0.40) | fitted to spec 01 examples | 20.6 |
| Runtime overhead | 2.0 GB | engine + CUDA/MLX context | 17.5 |
| M_repo_workspace | 4.0 GB | midpoint of 2.5–6.0 GB | 17.7 |
| Eviction events / month | 30 | spec 01 12-agent benchmark | 22.8 |
| Eviction compute price | 0.30 USD / 1M tokens | open-weights input price level | 22.8 |
| Capital opportunity rate | 0.045 | risk-free rate (spec 02) | 22.6 |
| Gateway fee | 500 USD / month | enterprise gateway/SLA estimate | 24.5 |
| Reference API model | claude-sonnet-5-5 | typical agentic coding default | 24.4 |
| Quality floors | 14 / 18 / 40 / 55 | see design "Quality floors"; the 14.0 floor was set for Gemma 4 12B (14.5), which has no AA v5 score since C-025 | 31.3 |
| Preset weights | see design "Presets" | | 32.1 |
| Default subscription plan | claude-ultra (200 USD / seat / month) | $200 plan of spec 02 Baseline A under its current name (C-018) | 24.1 |
| Rental hours per month | 730 | hourly GPU prices × 730 h = monthly rental price (Nebius, Fireworks; equals `hours_per_month`) | 25.1 |
| Fireworks host RAM | 1600 GB | not published; equal to the Nebius 8× H100 VM (C-031) | 25.1 |
| Popularity value | billion tokens on OpenRouter on the snapshot date | raw value of the Popularity_Snapshot | 32.6 |
| Risk weights and constants | w = 0.5/0.5, cap 5 yrs, rental 0.20, API 0.40, missing agreement 0.95 | | 29.4 |
| AA ratio default | 2.0 | used when < 2 models have both scores | 31.4 |
| Calibration tolerances | 30 % decode, 50 % prefill | | 42.2 |
| Historical benchmark context when not stated (superseded by C-054) | 8,192 tokens; never used as actual prompt | the source summaries say "short context"; matches the Req 9.4 window 6,144–10,240 at a 8,192 target (C-037) | 9.2, 9.4 |
| Historical benchmark precision when not stated (superseded by C-054) | INT4 bucket; insufficient for matching | 4-bit is the default build of the source videos (C-037) | 9.4 |
| β_backend | 1.0 optimized, 0.035 unoptimized | spec 01 Stage 2 §3 (49 s → 1.7 s on an 8K prompt) | 21.2 |
| FX rate | 1.1165 USD/EUR | ECB reference rate of 2026-11-06, verified on 2026-11-07 (tier `official`) | 12.2 |
| Eviction N_agents | `concurrent_agent_instances` of the Workload_Profile (default 8) | spec 02 §2.4 divides the wait cost by the number of agents sharing the machine | 22.8 |
| Missing cabling kit | 0 USD when the hardware item has no kit for the node count | no MVP hardware item has a cabling kit (C-033) | 22.1 |
| Measured aggregate TPS for per-seat workstations | record value × active users | a record measures one machine; per-seat deployments have one machine per user | 23.3 |
| Wait-time penalty without local TTFT | 0 USD plus a warning | H_local_wait cannot be computed | 22.7 |

| Single-stream break-even operating assumption | 8760 hours/year, 100% single-stream load | Hypothetical output market-value comparison, not a forecast of workload utilization | 26.8 |
