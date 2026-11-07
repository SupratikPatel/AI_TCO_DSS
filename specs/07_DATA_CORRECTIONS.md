# Data Corrections Ledger

## Entries
| ID | Date | Area | Old value | New value | Sources | Decision |
|---|---|---|---|---|---|---|
| C-001 | 2026-11-06 | gpt-oss-120b architecture | dense | mixture-of-experts (117B total, 5.1B active) | OPENAI-GPT-OSS-CARD, HF-GPT-OSS-120B | Use vendor model card |
| C-002 | 2026-11-06 | Hetzner GEX63 monthly price | €1,197 | €999 (+ €999 one-time setup) | HETZNER-GEX63 | Vendor price excl. VAT |
| C-003 | 2026-11-06 | Romania employer tax | 2.25 % statutory CAM vs ~4 % incl. benefits | 2.25 % | RO-ANAF-CAM, SPEC-02 | Benefits are not a social tax (D-10) |
| C-004 | 2026-11-06 | Chart colours spec 05 §2.2 | non-Okabe-Ito hex values | Okabe-Ito mapping (table below) | OKABE-ITO-2008 | Colour-blind safe palette |
| C-005 | 2026-11-06 | Default currency | EUR | USD | requirements 12.1 | — |
| C-006 | 2026-11-06 | extra-high thinking multiplier | 4.9–8.0 | 4.94 | SPEC-01 §1.1 | Use the empirical task baseline |
| C-007 | 2026-11-06 | Contract changes vs spec 04 | see "Contract Deviations" | | requirements 7.7 | — |
| C-008 | 2026-11-06 | Package path | src/core/, src/ui/, src/agent/ | src/ai_tco_dss/{domain,catalog,engines,decision,services,ui} | requirements 1.6 | — |
| C-009 | 2026-11-06 | Rental GPU | RTX Pro 6000 (workstation) | RTX PRO 6000 Max-Q in GEX63/GEX430; sized with workstation item | HETZNER-GEX63 | assumption: same memory, equal performance |
| C-010 | 2026-11-06 | Poland employer tax | +12 % (spec 03) vs €85–96k total (spec 02) | to verify in Task 4 | SPEC-02, SPEC-03 | open |
| C-011 | 2026-11-06 | Multi-node single-stream decode | — | Req 20.1 applied literally (no ×N) | design D-08 | known limitation, quantified by calibration |
| C-012 | 2026-11-06 | CSV export | two downloads per click | one ZIP with two CSVs | design D-11 | Streamlit limitation |
| C-013 | 2026-11-06 | Mac M5 Max OS reservation | spec 04 default 0.25 | 0.195 (128 GB → ~103 GB) | YT-02, SPEC-01 | matches 16.6 reference |
| C-014 | 2026-11-06 | Hetzner GEX430 | not in spec | €3,599/month + setup fee | HETZNER-GEX430 | added by requirements 10.6 |
| C-015 | 2026-11-06 | Kimi K3.1 Pro license | "Open Weights" | to verify in Task 4 | SPEC-03 | open |

## Contract Deviations (spec 04 → domain contracts)
| Contract | Field / member | Old | New | Sources | Date |
|---|---|---|---|---|---|

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
| Quality floors | 14 / 18 / 40 / 55 | see design "Quality floors" | 31.3 |
| Preset weights | see design "Presets" | | 32.1 |
| Risk weights and constants | w = 0.5/0.5, cap 5 yrs, rental 0.20, API 0.40, missing agreement 0.95 | | 29.4 |
| AA ratio default | 2.0 | used when < 2 models have both scores | 31.4 |
| Calibration tolerances | 30 % decode, 50 % prefill | | 42.2 |
| FX rate (until verified) | 1.1165 USD/EUR | ECB early Nov 2026 | 12.2 |
