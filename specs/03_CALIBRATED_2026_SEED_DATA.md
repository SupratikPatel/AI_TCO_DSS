<!-- ===================================================================== -->
<!-- SPLIT FILE: specs/03_CALIBRATED_2026_SEED_DATA.md                     -->
<!-- PURPOSE: Module 3 (Pure Seed Data: AA v5 Ladder, Hardware, Models)    -->
<!-- ===================================================================== -->

# Module 3: 2026 Calibrated Hardware, Model, Intelligence & FinOps Seed Catalog

## 1. The Artificial Analysis v5 Intelligence Staircase (16GB to 1TB+ Rungs)

Doubling memory does not linearly buy a smarter model. The seed catalog classifies every memory tier into either an **Intelligence Leap Rung** or a **Bits, Context & Concurrency Rung**:

| Memory Rung | Top Model Unlocked | AA v5 Score (Opus 5.5 = `58.4`) | Rung Classification & What It Actually Buys | Key Hardware & OS Trap Notes |
|---|---|---|---|---|
| **16 GB** | `Qwen 3.8-27B` (3-bit PC) / `Gemma 4 12B` (Mac) | **20.1** (PC) / **14.5** (Mac) | **Entry Rung (~34% of Frontier).** | `RTX 5060 Ti 16GB` ($780) runs 27B 3-bit (`12.5 GB`) at 45 TPS (31 TPS @ 55K ctx). `16GB Mac Mini` ($899) has only ~12GB usable and drops to `Gemma 4 12B`. |
| **32 GB** | `Qwen 3.8-27B` (4-bit) | **20.1** *(Same Model)* | **4th Bit + 128K Agentic Context Floor.** | `Mac Mini M6 32GB` ($1,299) or `RTX 5090 32GB`. First viable single-agent coding rung. |
| **64 GB** | `Qwen 3.8-27B` (8-bit) | **20.1** *(Bits & Concurrency)* | **8-Bit + 256K Context + 10-Agent Concurrency.** | `Mac Mini M5 Pro 64GB` ($2,699) or `DGX Spark 64GB` ($4,999). Skip for 1 user; vital for **10 concurrent agents (~150 TPS combined)**. |
| **128 GB** | `GLM 5.3 Flash (320B-A18B)` / `Qwen Flash Next (125B)` | **27.8** *(+7.7 pt Leap)* | **First Major Open Intelligence Leap.** | `AMD Strix Halo` ($3,449, 47–54 TPS), `M5 Max Studio` ($5,099, 69 TPS), `DGX Spark 128GB` ($6,950). *Mac Trap:* Default 103GB usable blocks 111GB 4-bit `Flash Next` without `sysctl`. |
| **192 GB** | `Qwen 3-235B` (4-bit) / `MiniMax M2` | **28.5** *(Upgrade Trap)* | **Single-box 120–160GB models (~12 TPS).** | `AMD Gorgon Halo 192GB` ($6,799–$7,449). Pays $3,350 for +64GB (>$52/GB). `2× 128GB Strix Halo` ($6,898) give 256GB for $99 more. |
| **256 GB** | `DeepSeek V4.1 Flash (552B+196B)` (3-bit) | **32.5** *(+4.7 pt Leap)* | **Unlocks DeepSeek V4.1 Flash (~56% Frontier).** | `M5 Ultra 256GB` ($9,499, 26–35 TPS) or `2× DGX Sparks` ($13,900, 15s 32K prefill). *Mac Trap:* Default 206GB blocks 233.5GB 3-bit build without `sysctl`. |
| **512 GB** | `DeepSeek V4.1 Flash` (4-bit) / `GLM 5.3 753B` | **32.5** *(Fidelity Rung)* | **Restores 4-Bit Fidelity (98.5% agreement).** | **Arbitrage:** `2× 256GB M5 Studios` ($21,598) beat `1× 512GB M5 Studio` ($22,299) by $701 and double bandwidth. Or `512GB DDR4 EPYC + 1× RTX Pro 6000` (65 TPS). |
| **1 TB+** | `Kimi K3.1 Pro (2.8T MoE / 104B Active)` (2-bit) | **46.0** *(+13.5 pt Monster Leap)* | **Best Open Model in the World (~79% Frontier).** | `4× 256GB M5 Studios` ($37,996) or `8× DGX Sparks` ($55,600 @ 2.2 TPS). Beats 1TB dead-end models (`Mistral Large 4` = `26.0`, `Inkling` = `12.5`, `Nemotron 3 Ultra` = `11.8`). |

---

## 2. Calibrated 2026 Hardware Seed Catalog

| ID | Hardware Name | Deployment Mode | Advertised / Usable Memory | Bandwidth | Prefill Speed (32K / 1M) | Power (Idle/Load) | 2026 Price | Software Clock & Notes |
|---|---|---|---|---|---|---|---|---|
| `rtx-5060-8gb` | RTX 5060 8GB + 32GB DDR5 PC | `tiered-offload-appliance` | 8 GB VRAM (~7.2 GB) + 32 GB RAM | 288 GB/s | 2,100 tok/s | 12W / 140W | €850 | 5.0 yrs. Runs 8B @ 62 TPS; `35B-A3B` @ 40 TPS via RAM offload. |
| `rtx-5060-ti-16gb` | RTX 5060 Ti 16GB Desktop | `per-seat-workstation` | 16 GB GDDR7 (~14.4 GB) | 448 GB/s | 3,200 tok/s | 15W / 180W | €1,150 | 5.0 yrs. Runs `Qwen 27B` 3-bit (`12.5GB`) @ 45 TPS (31 TPS @ 55K ctx). |
| `rtx-3090-24gb-used` | Used RTX 3090 24GB Desktop | `per-seat-workstation` | 24 GB GDDR6X (~21.6 GB) | 936 GB/s | 3,800 tok/s | 25W / 350W | €1,778 | 3.0 yrs. Runs 27B @ 40 TPS; caps standard 27B INT4 context at ~120K. |
| `rtx-5070-strata-64gb` | RTX 5070 (12GB) + 64GB DDR5 (`Strata`) | `tiered-offload-appliance` | 12 GB VRAM + 64 GB DDR5 | 504 GB/s | 3,600 tok/s | 20W / 250W | €1,848 | 5.0 yrs. Runs 111GB `Flash Next` @ 94 TPS; `DeepSeek V4.1` @ 4.7 TPS. |
| `radeon-r9700-32gb` | AMD Radeon R9700 32GB Workstation | `tiered-offload-appliance` | 32 GB GDDR6 (~28.8 GB) + 256 GB RAM | 680 GB/s | 3,400 tok/s | 25W / 300W | €1,850 | 3.5 yrs. Runs 124B MoE @ 38 TPS offloaded; 8 agents @ 7 TPS/agent. |
| `heterogeneous-scavenged-3gpu` | Scavenged 3-GPU + iGPU/NPU Rig | `heterogeneous-routed` | 52 GB VRAM (24G+12G+16G) + 128G RAM | 936 GB/s max | 4,500 tok/s | 65W / 750W | €3,600 | 4.0 yrs. RTX 3090 (Authority) + 3060 (Worker) + 2000 Ada (Router) + Core Ultra iGPU. |
| `olares-one-120gb` | Olares One Compact Appliance | `tiered-offload-appliance` | 24 GB GDDR7 + 96 GB DDR5 | 900 GB/s | 4,200 tok/s | 25W / 280W | €3,200 | 5.0 yrs. 3.5L box; runs `Flash Next` @ 90 TPS decode, 127 TPS prefill. |
| `wici-one-wireless` | WiCi One Wireless eGPU (5060Ti / 5090) | `wireless-egpu-appliance` | 16 GB / 32 GB + 4TB NVMe | 448 / 1,792 GB/s | 3,200 / 9,500 tok/s | 25W / 450W | €2,599 / €9,999 | 5.0 yrs. Wi-Fi 7 virtual GPU; runs 748B GGUF DeepSeek via `InferSSD` @ ~8 TPS. |
| `mac-mini-m6-16gb` | Mac Mini (M6 Base 16GB) | `per-seat-workstation` | 16 GB (~12 GB usable) | 153 GB/s | 650 tok/s | 2.6W / 35W | €899 | 5.0 yrs. 12GB usable wall forces fallback to `Gemma 4 12B`. |
| `mac-mini-m6-32gb` | Mac Mini (M6 24GB $\rightarrow$ 32GB SKU) | `per-seat-workstation` | 32 GB (~24 GB / 28 GB tuned) | 170 GB/s | 720 tok/s | 2.6W / 40W | €1,299 | 5.0 yrs. Unlocks 170 GB/s bus + 128K agentic context floor on `Qwen 27B`. |
| `mac-mini-m5-pro-64gb` | Mac Mini (M5 Pro 64GB) | `per-seat-workstation` | 64 GB (~48 GB / 58 GB tuned) | 307 GB/s | 1,200 tok/s | 3W / 65W | €2,699 | 5.0 yrs. 531 prefill units/core; supports 10 concurrent 27B agents (~150 TPS). |
| `mac-studio-m5-max-128gb`| Mac Studio (M5 Max 128GB) | `per-seat-workstation` | 128 GB (~103 GB / 115 GB tuned)| 546 GB/s | 1,650 tok/s | 10W / 140W | €5,099 | 5.0 yrs. $2\times$ M3 Ultra reading speed. Needs `sysctl` for 111GB `Flash Next` (69 TPS). |
| `amd-strix-halo-128gb` | AMD Strix Halo Mini PC (128GB) | `per-seat-workstation` | 128 GB (96 GB Win / 118 GB Linux)| 256 GB/s | 148 tok/s (1M: 1.9h)| 15W / 150W | €3,449 | 2.5 yrs. Runs `Flash Next` @ 47–54 TPS; `gpt-oss-120B` @ 46 TPS vs 70B dense @ 5 TPS. |
| `amd-gorgon-halo-192gb` | AMD Gorgon Halo Mini PC (192GB) | `per-seat-workstation` | 192 GB (160 GB Win / 180 GB Linux)| 273 GB/s | 165 tok/s | 15W / 150W | €6,799 | 2.5 yrs. $52/GB upgrade trap; `2× 128GB Strix` (€6,898) give 256GB. |
| `mac-studio-m5-ultra-256gb`| Mac Studio (M5 Ultra 256GB) | `per-seat-workstation` | 256 GB (~206 GB / 240 GB tuned)| 1,200 GB/s | 2,700 tok/s | 15W / 300W | €9,499 | 5.0 yrs. 11s 20-page prefill; 26–35 TPS on `DeepSeek V4.1` 3-bit (with `sysctl`). |
| `mac-studio-m3-ultra-512gb`| Used Mac Studio (M3 Ultra 512GB) | `per-seat-workstation` | 512 GB (~384 GB / 480 GB tuned)| 800 GB/s | 390 tok/s (1M: 42.7m)| 20W / 280W | €16,500 | 3.0 yrs. High RAM, but legacy 151 units/core prefill takes 42.7 min on 1M tokens. |
| `mac-studio-m5-ultra-512gb`| Mac Studio (M5 Ultra 512GB) | `per-seat-workstation` | 512 GB (~384 GB / 480 GB tuned)| 1,200 GB/s | 2,700 tok/s | 18W / 300W | €22,299 | 5.0 yrs. €701 pricier than `2× 256GB Studios` (€21,598) which double bandwidth to 2.4 TB/s. |
| `dgx-spark-64gb` | NVIDIA DGX Spark (64GB) | `per-seat-workstation` | 64 GB (~58 GB usable) | 273 GB/s | 2,000 tok/s | 42W / 90W | €4,999 | 5.0 yrs. Runs `Qwen 27B` + 250K context (34GB) at 11.6–36.6 TPS. |
| `dgx-spark-128gb` | NVIDIA DGX Spark (128GB) | `centralized-server` | 128 GB (~118 GB usable) | 273 GB/s | 2,000 tok/s (4x: 4,000)| 45W / 90W | €6,950 | 5.0 yrs. 4× Sparks (€27,368 w/ ring kit) prefill 1M tokens in 4.2m; 8× run Kimi K3.1 @ 2.2 TPS. |
| `threadripper-pro-256gb` | Threadripper Pro + 256GB DDR5 + 1× Pro 6000 | `centralized-server` | 96 GB VRAM + 256 GB ECC DDR5 | 1,800 GB/s (VRAM) | 5,500 tok/s | 95W / 580W | €21,800 | 5.0 yrs. Zero-eviction multi-agent workstation (16+ agents without context loss). |
| `epyc-ddr4-pro-6000` | Dual EPYC + 512GB DDR4 + 1× Pro 6000 | `tiered-offload-appliance` | 96 GB VRAM + 512 GB DDR4 | 1,800 GB/s | 5,500 tok/s | 180W / 650W | €20,500 | 4.5 yrs. DDR4 arbitrage (€399/64GB vs €1,200+ DDR5); runs `DeepSeek V4.1` @ 65 TPS. |
| `rtx-pro-6000-96gb` | NVIDIA RTX Pro 6000 Blackwell (96GB) | `centralized-server` | 96 GB ECC (~86.4 GB usable) | 1,800 GB/s | 5,500 tok/s (8x: 8,700)| 30W / 350W | €16,000 | 5.0 yrs. 4× cards (€64k) serve 32 users @ 900+ TPS; 8× prefill 1M tokens in 1.9m. |
| `h100-80gb-sxm` | NVIDIA H100 SXM (80GB) | `centralized-server` | 80 GB HBM3 (~72 GB usable) | 3,350 GB/s | 18,000 tok/s | 70W / 700W | €32,000 | 5.0 yrs. Reaches 5,900 tok/s on `gpt-oss-120b` (SemiAnalysis InferenceX). |
| `amd-halo-station-2tb` | AMD Halo Station (2027 Ref Architecture) | `centralized-server` | 576 GB HBM3 + 2,048 GB DDR5 | 4,200 GB/s (HBM3) | 22,000 tok/s | 120W / 1,200W | €48,000 | 5.0 yrs. 2TB system RAM for 64+ concurrent multi-agent fleets with zero eviction. |
| `hetzner-scaleway-eu-gpu` | Dedicated EU Cloud GPU (Hetzner / Scaleway)| `cloud-rental` | 80 GB – 96 GB Dedicated | 1,800–3,350 GB/s| 5,500+ tok/s | Included | €1,197–€2,093/mo | Zero CapEx / Zero MLOps hardware maintenance; 100% EU sovereign data centers. |
| `legacy-8x-v100-256gb` | Used 8× Tesla V100 Rack (256GB) | `centralized-server` | 256 GB HBM2 (~230 GB usable) | 900 GB/s | 2,200 tok/s | 400W / 2,800W | €5,800 | **0.5 yrs (Expired):** R580 final driver; dropped in CUDA 13 & vLLM v0.9+; €1,900/yr power. |
| `legacy-16x-mi50-256gb` | Used 16× AMD MI50 Rig (256GB) | `centralized-server` | 256 GB HBM2 (~230 GB usable) | 1,000 GB/s | 56 tok/s (1M: 5.0h) | 300W / 2,400W | €13,500 | **0.5 yrs (Expired):** Mainline ROCm dropped; 1M prefill costs €2.27 in electricity vs $0.15 API. |

---

## 3. Calibrated 2026 Model Seed Catalog

### 3.1 Dense Open-Weights Models
- **`Gemma 4 12B`:**
  - *Architecture:* 12B total / 12B active, dense standard GQA. License: Apache 2.0.
  - *Weights:* INT4 = `~7.5 GB`. Max context: 128K.
  - *Scores:* AA v5 Score = `14.5`. Primary function: Entry-level fallback for 16GB macOS devices blocked by OS wired memory caps.
- **`Qwen 3.8-27B`:**
  - *Architecture:* 27B total / 27B active, 64 layers (16 active growing KV layers $\rightarrow r_{\text{kv\_active}} = 0.25$). License: Apache 2.0.
  - *Weights:* INT3 = `12.5 GB`, INT4 = `16.7 GB`, INT8 = `29.5 GB`. Max context: 256K.
  - *Scores:* AA v5 Score = `20.1`, Terminal Bench 2.1 = `73.0`.
  - *Cloud Rates:* OpenRouter = `$0.09/1M in, $1.875–$2.91/1M out` (~`$3.53` per benchmark task).
- **`Llama 3.3-70B`:**
  - *Architecture:* 70B total / 70B active, dense standard GQA. License: Meta Llama 3 Community.
  - *Weights:* FP8 = `70 GB`, FP16 = `140 GB`. Max context: 128K. AA v5 Score = `24.2`.
- **`GPT-OSS 120B` (Dense build):**
  - *Architecture:* 120B total / 120B active dense. License: Apache 2.0.
  - *Weights:* INT4 = `66 GB`. Requires >64GB system memory. AA v5 Score = `26.5`.
- **`Llama 3.1-405B`:**
  - *Architecture:* 405B total / 405B active dense. License: Meta Llama 3 Community.
  - *Weights:* INT4 = `200 GB`, FP8 = `405 GB`. Generation speed: ~4 TPS on M5 Ultra (`1,200 GB/s`). AA v5 Score = `30.2`.

### 3.2 Sparse Mixture-of-Experts (MoE) Open-Weights Models
- **`Qwen 3.6-35B-A3B`:**
  - *Architecture:* 35B total / 3B active. License: Apache 2.0.
  - *Weights:* INT4 = `17 GB`. Generation speed: **78.8 TPS** on Apple Pro chip (vs. 14.7 TPS on dense 27B).
- **`Qwen 3.8 Flash Next (125B–176B / A6B)`:**
  - *Architecture:* 125B total / 6B active. License: Apache 2.0.
  - *Weights & Agreement:* INT3 (`93 GB`, 81.6% token agreement), INT4 (`111 GB`, 97.8% agreement). Max context: 128K.
  - *Scores & Speed:* AA v5 Score = `27.8`. 90–108 TPS short context, 61 TPS @ 128K on M5 Ultra; 94 TPS on RTX 5070 Strata hybrid.
- **`DeepSeek V4 Flash (284B-A13B)`:**
  - *Architecture:* 284B total / 13B active. License: MIT.
  - *Weights:* INT4 = `151–162 GB`. Max context: 1,000,000 tokens. AA v5 Score = `27.4`.
- **`GLM 5.3 Flash (320B-A18B)`:**
  - *Architecture:* 320B total / 18B active. License: Apache 2.0.
  - *Weights:* INT4 = `178–199.7 GB`. Max context: 128K.
  - *Scores & Cloud:* AA v5 Score = `27.8`. Cloud API = `$0.092–$0.50/1M out` (~20× cheaper to rent than dense 27B).
- **`Qwen 3.5-397B-A17B`:**
  - *Architecture:* 397B total / 17B active. License: Apache 2.0.
  - *Weights:* INT4 = `224 GB`. Cloud API = `$3.20–$3.50/1M out`.
- **`DeepSeek V4.1 Flash (552B-A16B + 196B SSD Engram)`:**
  - *Architecture:* 552B core weights / ~16B active per token + 196GB static Engram lookup table on NVMe SSD (`748B` combined). Multi-Head Latent Attention (MLA: <0.9 GB KV cache @ 1M context). License: MIT.
  - *Weights & Agreement:* Unsloth 3-bit non-Engram = `233.5 GB` (95.1% agreement); 4-bit non-Engram = `298 GB` (98.5% agreement); full official = `510 GB`.
  - *Scores & Cloud:* AA v5 Score = `32.5`. API rates: `$0.60/1M out (off-peak)`, `$1.20/1M out (peak)` (~`$0.60` per benchmark task).
- **`GLM 5.3 Full (744B/753B-A40B)`:**
  - *Architecture:* 753B total / 40B active. License: Apache 2.0.
  - *Weights:* INT3 = `343 GB`, INT4 = `420 GB`. AA v5 Score = `31.7`. Generation speed: ~25–26 TPS on 512GB M5 Ultra.
- **`Kimi K3.1 Pro (2.8T MoE / 104B Active)`:**
  - *Architecture:* 2,800B total / 104B active (~52 GB read per token at 4-bit). License: Open Weights.
  - *Weights & Agreement:* Unsloth 2-bit build = `711 GB` (84.1% agreement); higher-fidelity 2-bit build = `861 GB` (90.4% agreement); FP8 = `1.56 TB`.
  - *Scores & Cloud:* AA v5 Score = `46.0` (highest open-weights index score in the world). Moonshot Cloud API: `$10.00/1M out` at **31 TPS** (vs. **2.2 TPS** on 8× DGX Sparks).
- **Underperforming Reference Giants (Negative Benchmarks):**
  - `Mistral Large 4 (>1TB MoE)`: AA v5 Score = `26.0` (scores below 125B models).
  - `Inkling (~1T MoE)`: AA v5 Score = `12.5`.
  - `Nemotron 3 Ultra (550B)`: AA v5 Score = `11.8`.

### 3.3 Commercial Frontier Cloud APIs (2026 Calibrated Rates)
- **`Claude Opus 5.5` (Vertex AI EU / AWS Bedrock EU / Direct):**
  - *Scores:* AA v5 Score = `58.4`, Terminal Bench = `89.4`.
  - *Pricing (Global):* `$4.00/1M input, $20.00/1M output`. Cache read = `$0.40/1M` (10%).
  - *Pricing (EU Endpoint):* **+10% Residency Surcharge** $\rightarrow$ `$4.40/1M input, $22.00/1M output`.
- **`Claude Sonnet 5.5` (Vertex AI EU / Direct):**
  - *Scores:* AA v5 Score = `48.2`.
  - *Pricing (Global):* `$2.00/1M input, $10.00/1M output`. Cache read = `$0.10/1M` (5%). EU Endpoint = `$2.20 / $11.00`.
- **`Claude Haiku 5.5`:**
  - *Pricing:* `$0.10/1M input, $0.50/1M output` ($\le 100\text{K}$ context); `$0.50 / $2.50` ($> 100\text{K}$).
- **`GPT-6.1 / 5.6 Soul` (Azure EU / OpenAI Global):**
  - *Scores:* AA v5 Score = `52.0`.
  - *Pricing:* `$2.00/1M input, $10.00/1M output` ($2\times$ input surcharge past 272K context).
- **`Gemini 3.1 Pro` (Vertex AI EU):**
  - *Scores:* AA v5 Score = `49.5`.
  - *Pricing:* `$2.00/1M input, $12.00/1M output` ($\le 200\text{K}$); `$4.00 / $18.00` ($> 200\text{K}$).
- **`Gemini 3.8 Flash`:**
  - *Pricing:* `$0.75/1M input, $3.75/1M output` (introductory promotional rate through Dec 31, 2026; **scheduled price increase to `$1.50 / $7.50` on Jan 1, 2027**).

---

## 4. Intra-EU Engineering Compensation & FinOps Seed Table

| Region / Hub Key | Location Profile | Base MLOps Salary (2026) | Employer Social Tax Rate ($\tau$) | Total Annual Employer Cost | Monthly Employer Cost (1.0 / 0.5 FTE) | Recruiting Delay |
|---|---|---|---|---|---|---|
| `de-munich-hq` | Munich, Germany (HQ) | €120,000 | +21.0% (Lohnnebenkosten) | **€145,200** | €12,100 / €6,050 | 7.7 months |
| `de-berlin-hamburg`| Berlin / Hamburg, Germany | €100,000 | +21.0% (Lohnnebenkosten) | **€121,000** | €10,083 / €5,042 | 6.5 months |
| `ro-cluj-bucharest`| Cluj-Napoca / Bucharest, Romania | €75,000 | +2.25% CAM (~4% w/ benefits)| **€78,000** | **€6,500 / €3,250** | 2.5 months |
| `pl-warsaw-krakow` | Warsaw / Krakow, Poland | €82,000 | +12.0% statutory employer | **€91,840** | €7,653 / €3,827 | 3.2 months |

### Electricity Tariffs Seed
- `de-industrial-bdew`: **€0.172 / kWh** (German SME industrial grid tariff, 2026 BDEW average).
- `de-office`: **€0.280 / kWh** (Standard commercial office building tariff).
- `eu-nordic`: **€0.095 / kWh** (Renewable green hydro/nuclear datacenter tariff in Sweden/Finland).

---

## 5. Multi-Agent Concurrency & Eviction Calibration Benchmarks

| Metric / Parameter | 128 GB System RAM Configuration | 256 GB ECC DDR5 Configuration | Impact & Architectural Takeaway |
|---|---|---|---|
| **Max Concurrent Coding Agents** | 12 agents attempted | 12 agents (scaled to 16 agents) | 256 GB unlocks true multi-agent parallelism. |
| **Agent Completion Rate** | **16.7%** (2 passed, 10 failed/timed out)| **100%** (12 of 12 passed) | RAM starvation causes agent cascade failures. |
| **Conversational Evictions to Disk**| **30 evictions** | **0 evictions** | Zero evictions preserves local git & tool context. |
| **Total Task Execution Time** | **85 minutes** | **59 minutes** | **26-minute speedup (-30.6%)** with 256 GB RAM. |
| **Peak System RAM Measured** | 128 GB (Hard OOM boundary) | 150 GB (Room for 16+ agents) | 128 GB is a bottleneck for >6 coding agents. |