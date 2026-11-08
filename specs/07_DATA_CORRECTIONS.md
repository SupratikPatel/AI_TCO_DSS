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

## Contract Deviations (spec 04 → domain contracts)
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
| Benchmark context when not stated | 8,192 tokens | the source summaries say "short context"; matches the Req 9.4 window 6,144–10,240 at a 8,192 target (C-037) | 9.2, 9.4 |
| Benchmark precision when not stated | INT4 | 4-bit is the default build of the source videos (C-037) | 9.4 |
| β_backend | 1.0 optimized, 0.035 unoptimized | spec 01 Stage 2 §3 (49 s → 1.7 s on an 8K prompt) | 21.2 |
| FX rate | 1.1165 USD/EUR | ECB reference rate of 2026-11-06, verified on 2026-11-07 (tier `official`) | 12.2 |
| Eviction N_agents | `concurrent_agent_instances` of the Workload_Profile (default 8) | spec 02 §2.4 divides the wait cost by the number of agents sharing the machine | 22.8 |
| Missing cabling kit | 0 USD when the hardware item has no kit for the node count | no MVP hardware item has a cabling kit (C-033) | 22.1 |
| Measured aggregate TPS for per-seat workstations | record value × active users | a record measures one machine; per-seat deployments have one machine per user | 23.3 |
| Wait-time penalty without local TTFT | 0 USD plus a warning | H_local_wait cannot be computed | 22.7 |

| Single-stream break-even operating assumption | 8760 hours/year, 100% single-stream load | Hypothetical output market-value comparison, not a forecast of workload utilization | 26.8 |
