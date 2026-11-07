<!-- ===================================================================== -->
<!-- SPLIT FILE: specs/01_WORKLOAD_AND_PHYSICS_ENGINE.md                   -->
<!-- PURPOSE: Module 1 (Workload Profiler) & Module 2 (4-Stage Physics)    -->
<!-- ===================================================================== -->

# Module 1 & Module 2: Enterprise Workload Profiler & 4-Stage Physical Inference Sizing Engine

## 1. Module 1: Enterprise Workload Profiler & Agentic Harness Mechanics

Ingests historical proxy logs (CSV/JSON from LiteLLM or Bifrost routing layers) or user slider overrides to establish deterministic token, context, and concurrency baselines.

### 1.1 Token Volume, Tokenizer Inflation, Thinking Effort & Verification Multipliers
1. **Base Request Tokens:** Prompt input tokens ($T_{\text{in}}$) and visible completion output tokens ($T_{\text{out}}$).
2. **Vendor Tokenizer Inflation Factor ($\tau_{\text{tokenizer}}$):**
   Token counts are not uniform across model families for identical text strings. Anthropic's tokenizer (`Claude 4.7+ / 5.5`) generates **~30% more tokens** for identical codebases or documents compared to OpenAI (`gpt-6.1` / `gpt-oss`) or `Qwen 3.8` tokenizers:
   $$\tau_{\text{tokenizer}} = \begin{cases} 1.30 & \text{if model family} == \text{"Claude"} \\ 1.00 & \text{otherwise} \end{cases}$$
3. **Thinking Effort Multiplier ($\mu_{\text{thinking}}$):**
   - Discrete presets: `none` ($1.0\times$), `low` ($1.5\times$), `medium` ($2.5\times$), `extra-high` ($4.9\times\text{–}8.0\times$).
   - *Empirical Task Baseline (`Qwen 3.8-27B` / `DeepSeek V4.1 Flash` Extra-High):* Generates ~`13,000` internal reasoning tokens + `3,300` visible output tokens per complex coding task ($\mu_{\text{thinking}} \approx 4.94\times$).
   - *Unconstrained Thinking Latency Wall:* `DeepSeek V4.1` unconstrained thinking can emit up to `32,768` reasoning tokens. On a slow 3-tier offloaded rig (`4.7 TPS`), unconstrained reasoning blocks the terminal for **~1.93 hours** before emitting the first visible answer token.
4. **Dual-Agent Verification Multiplier ($\nu_{\text{verify}}$):**
   - In the 6-Layer Agentic Harness architecture, enabling Layer 4 independent verification (`verifier.md` read-only evaluator agent) doubles total token consumption ($\nu_{\text{verify}} = 2.0\times$, else $1.0\times$).

### 1.2 Agentic Harness Scaffolding ($S_{\text{harness}}$), MCP Pruning & Mega-Sessions
1. **The 5.6× Harness Scaffolding Spread ($S_{\text{harness}}$):**
   Agentic coding tools inject hidden system instructions, repository maps, and tool schemas on every turn:
   - `claude-code`: `~33,000` scaffolding tokens/turn ($18.34/successful task baseline).
   - `codex`: `~13,000` tokens/turn (spiking to `~100,000` on fresh session init).
   - `opencode`: `~7,000` tokens/turn.
   - `deepseek-harness-dsh` (Creator Mode): `~4,200` tokens/turn ($3.28/successful task baseline—$5.6\times$ cheaper than `claude-code` at identical task pass rates).
   - `custom-lean`: User-configurable token count.
2. **Model Context Protocol (MCP) Code Mode Pruning Ratio ($r_{\text{mcp\_prune}}$):**
   - Standard harnesses re-send full JSON schemas for 50–500 MCP tools on every turn.
   - Enabling MCP Code Mode dynamically filters tool definitions, reducing scaffolding overhead by **58% to 92%** (default $r_{\text{mcp\_prune}} = 0.75$ when active, else $0.0$):
     $$S_{\text{effective}} = S_{\text{harness}} \times (1 - r_{\text{mcp\_prune}})$$
3. **Mega-Session Compounding Ratio ($\kappa_{\text{mega\_session}}$):**
   - Proportion of agentic sessions exceeding 80+ turns ($m_{\text{ratio}} \in [0.0, 1.0]$). Because full conversation history is re-sent and re-billed on every turn, 80+ turn mega-sessions account for ~91% of enterprise API spend:
     $$\kappa_{\text{mega\_session}} = 1.0 + (m_{\text{ratio}} \times 2.8)$$
4. **128K Minimum Agentic Context Floor:**
   - Flag any local hardware/model pairing whose maximum usable context window falls below `128,000` tokens (`meets_128k_agentic_context_floor = False`), as multi-file coding agents rapidly exhaust smaller windows.

### 1.3 Multi-Agent State Retention vs. The Conversational Eviction Tax
In multi-agent engineering workflows, developers run fleets of concurrent agents (e.g., 8–16 simultaneous autonomous coding loops). Memory management bifurcates into two distinct physical domains:
1. **The VRAM vs. System RAM Functional Split:**
   - **GPU VRAM** governs **Instantaneous Execution Concurrency** (the number of active inference streams generating tokens in parallel at that exact millisecond).
   - **System RAM (DDR4/DDR5)** governs **Agent Context Retention & Workspace Capacity** (parking idle conversation histories, repository AST maps, tool execution logs, and KV caches between active turns without evicting them).
2. **State Retention Memory Demand ($M_{\text{agent\_state}}$):**
   $$M_{\text{agent\_state}} = N_{\text{agents}} \times \left(M_{\text{kv\_single}} + M_{\text{repo\_workspace}}\right)$$
   *(where $M_{\text{repo\_workspace}} \approx 2.5\text{–}6.0\text{ GB}$ per agent session for indexing local git trees, terminal buffers, and environment state).*
3. **The Conversational Eviction Tax ($\kappa_{\text{eviction}}$):**
   - If total system memory cannot hold all concurrent agent workspaces ($M_{\text{agent\_state}} > M_{\text{system\_ram\_usable}}$), the host OS or inference server is forced to evict conversation history to disk or discard it entirely.
   - Every eviction forces a **Cold Context Re-Prefill** on the subsequent turn, burning massive GPU cycles and locking execution lanes:
   - *Empirical 12-Agent Benchmark (128 GB vs. 256 GB RAM):*
     - On **128 GB RAM**, running 12 concurrent coding agents triggered **30 context evictions**, causing **10 of 12 agents to fail or timeout** and stretching total execution time to **85 minutes**.
     - Upgrading to **256 GB ECC DDR5 (6,400 MT/s)** allowed all **12 agents to complete successfully in 59 minutes** (a **26-minute / 30.6% wall-clock reduction** with zero context rebuilds; peak RAM usage reached **150 GB**).
     - At **256 GB RAM**, concurrency scaled cleanly to **16 simultaneous active agents** with 100% completion rates.

### 1.4 API Gateway Serialization & Memory Overhead
- **Python Gateways (`LiteLLM`):** Introduce **100–500 ms** P99 JSON serialization and logging latency under high multi-agent concurrency.
- **Compiled Rust/Go Gateways (`Bifrost`):** Reduce gateway overhead to **11 µs – 840 µs**.
- **Gateway Memory Scaling:** Proxy gateway RAM scales proportionally with $\text{Peak Concurrent Streams} \times \text{Context Length P99}$.

---

## 2. Module 2: 4-Stage Physical Hardware & Inference Sizing Engine

Hardware must not be evaluated by raw TFLOPS. Every hardware-model pairing must pass sequentially through four physical bottleneck stages:
**Stage 1 (Usable Memory, Attention KV & Offload) $\rightarrow$ Stage 2 (MoE Bandwidth & Prefill Compute) $\rightarrow$ Stage 3 (Quantization Fidelity & Lifecycle Clocks) $\rightarrow$ Stage 4 (Multi-Node Topology & Disaggregation)**.

### Stage 1: Memory Architecture, OS Split Traps, Attention Formats & 3-Tier Offload

#### 1. Usable Memory Ceiling ($M_{\text{usable}}$) & Operating System Allocation Traps
Advertised RAM/VRAM is never 100% available for model weights and KV cache:
- **Apple Silicon Unified Memory (`macOS`):** Reserves ~20%–25% for OS/display by default (`sysctl` wired limit). Enabling `apply_mac_wired_memory_override = True` (`sudo sysctl iogpu.wired_limit_mb=...`) raises usable memory to **90%–94%**:
  - *16GB Mac Trap:* Default `~12 GB` usable blocks `Qwen 3.8-27B` 3-bit (`12.5 GB`), forcing fallback to `Gemma 4 12B` (`7.5 GB`), whereas a 16GB discrete PC GPU (`RTX 5060 Ti`, `~14.4 GB` usable) fits 27B 3-bit cleanly.
  - *128GB Mac Trap:* Default `~103 GB` usable blocks `Qwen 3.8 Flash Next 125B` 4-bit (`111 GB`), silently forcing a downgrade to the 3-bit build (`93 GB`) unless the `sysctl` override (`~115 GB` usable) is applied.
  - *256GB Mac Trap:* Default `~206 GB` usable fits `GLM 5.3 Flash` 4-bit (`199.7 GB`, AA v5 `27.8`), but blocks `DeepSeek V4.1 Flash` 3-bit (`233.5 GB`, AA v5 `32.5`) unless the `sysctl` override (`~240 GB` usable) is applied.
  - *4× 256GB Mac Cluster Trap:* Default `~825 GB` aggregate usable fits the `711 GB` 2-bit `Kimi K3.1 Pro` build, but requires `sysctl` overrides across all 4 nodes (`~960 GB` usable) to load the higher-fidelity `861 GB` 2-bit build.
- **AMD Strix / Gorgon Halo Unified Memory:**
  - *Strix Halo (128GB):* Capped at `96 GB` usable on Windows; `118 GB` usable on Linux.
  - *Gorgon Halo (192GB):* Capped at `160 GB` usable on Windows; `180 GB` usable on Linux.
- **Discrete NVIDIA / AMD Workstation GPUs:** Host OS runs on system RAM; usable VRAM is governed by `gpu_memory_utilization` (default `0.90` on `vLLM` / `ROCm`).
- **Quick Fit UI Badge Heuristic:**
  $$\text{Max 4-Bit Parameters (Billions)} \approx \frac{\text{Advertised Memory (GB)} \times (1 - r_{\text{os\_reserved}})}{0.60}$$

#### 2. Model Weights Memory ($M_{\text{weights}}$)
Determined by **Total Parameters ($P_{\text{total}}$)** for both Dense and Sparse MoE models (unless overridden by an exact calibrated footprint in `calibrated_weights_gb`):
$$M_{\text{weights}} = P_{\text{total}} \times \left(\frac{\text{Weight Precision Bits}}{8}\right) \times 1.05$$

#### 3. Attention Architecture Footprint at Scale (MLA vs. Standard GQA vs. Hybrid)
The attention mechanism dictates whether 128K–1M context windows are physically possible:
- **Multi-Head Latent Attention (`multi-head-latent` — `DeepSeek V4 / V4.1 Flash`):** Compresses KV projections into a low-rank latent vector requiring only **~890 bytes/token**. At `1,000,000` tokens, the entire KV cache consumes **$< 0.9\text{ GB}$ of RAM/VRAM**.
- **Standard GQA / MHA (`standard-mha-gqa` — `Llama`, `Mistral`, `MiniMax`):** Requires **~120 KB to 163.8 KB/token** at FP16 (~41 KB/token at INT4). At `1,000,000` tokens, standard GQA consumes **41 GB (INT4) to 129 GB (FP16)** for a single user.
- **Hybrid Sparse Layered Attention (`hybrid-sparse` — `Qwen 3.8-27B`):** Maintains growing KV caches on only 16 of its 64 layers ($r_{\text{kv\_active}} = 0.25$). At `250,000` context, $M_{\text{kv}} \approx 17\text{ GB}$ + $16.7\text{ GB}$ (4-bit weights) = **~34 GB total** (or **~46 GB** in 8-bit at 256K context).
- **General Formula (when not using MLA latent override):**
  $$M_{\text{kv\_per\_token}} = 2 \times \left(n_{\text{layers}} \times r_{\text{kv\_active}}\right) \times n_{\text{kv\_heads}} \times d_{\text{head}} \times \left(\frac{\text{KV Precision Bits}}{8}\right) \times \phi_{\text{format}}$$
  $$M_{\text{kv\_single}} = M_{\text{kv\_per\_token}} \times \text{Target Context Length}$$
  *(where $\phi_{\text{format}} = 1.0$ for `GGUF`/`vLLM` and $1.08$ for `MLX` at extreme contexts).*

#### 4. Leftover KV-Cache Pool & Multi-Agent Concurrency ($U_{\text{max}}$)
Model weights load once into memory; remaining usable memory forms the shared KV-cache pool across concurrent streams:
$$M_{\text{kv\_pool}} = M_{\text{usable}} - M_{\text{weights}} - M_{\text{runtime\_overhead}}$$
$$U_{\text{max}} = \left\lfloor \frac{M_{\text{kv\_pool}}}{M_{\text{kv\_single}}} \right\rfloor$$
- **The 64GB Multi-Agent Concurrency Arbitrage:** While a 64GB box runs the same `Qwen 3.8-27B` model (`20.1` AA v5 score) as a 32GB box for a single user, its surplus `~30 GB` KV pool unlocks up to **10 simultaneous agent sessions clocking ~150 TPS combined throughput**.
- **Hard OOM Guardrail:** If $M_{\text{kv\_pool}} \le 0$ or $U_{\text{max}} < 1$, flag `is_feasible = False` (`OOM`) and recommend the next memory rung, `sysctl` override, or power-of-two node count.

#### 5. The "Desk, Shelf, Basement" 3-Tier Offload Engine (`Strata`, `Engram`, `InferSSD`)
For systems where $M_{\text{weights}} > M_{\text{VRAM}}$, the engine models 3-tier hierarchical memory execution:
- **Desk (GPU VRAM):** Holds active attention buffers, shared dense layers, and hot routed experts.
- **Shelf (System RAM — DDR4/DDR5):** Holds warm MoE experts (requires $\ge 46\text{ GB}$, ideally $\ge 64\text{ GB}$). Caching experts in system RAM provides a **$2.2\times$ decode speedup** over direct NVMe streaming (`4.7 TPS` vs. `2.1 TPS`).
- **Basement (NVMe SSD):** Holds static lookup tables (`196 GB Engram` table in `DeepSeek V4.1 Flash`; `257 GB` ISTA-DASLab 2-bit tables) or cold MoE experts (`InferSSD` on `WiCi One`).
- **Host Bus & CPU Core Scaling Multipliers on Offloaded Rigs:**
  - *PCIe Generation:* Upgrading from PCIe 3.0 to PCIe 4.0 increases offloaded decode speed by **~39%** (`6.9 TPS` $\rightarrow$ `9.6 TPS`).
  - *CPU Core Count:* On `Strata` hybrid offload, a 6-core CPU limits `DeepSeek V4.1 Flash` to **4–6 TPS**, whereas a 16-core CPU reaches **9–11 TPS**.
  - *Radeon 32GB Workstation Offload (`R9700`):* An AMD Radeon R9700 (32GB VRAM) paired with 256GB System RAM runs a 124B MoE (`Link 3.0 Flash`, 131K context) keeping **5.5 GB** in VRAM and **~90 GB** on the Shelf, sustaining **38 TPS** on single streams and **~7 TPS per agent across 8 concurrent agents** (nearly matching the 8.5 TPS/agent of an RTX Pro 6000 96GB).
  - *Strata Default Context Warning:* Flag that `Strata` defaults to an `8,192` context window (smaller than `claude-code` or `codex` system prompts) and must be manually reconfigured.

---

### Stage 2: Memory Bandwidth (Decode) vs. Compute (Prefill) & The MoE Law

#### 1. The MoE Dual-Parameter Law
- **Total Parameters ($P_{\text{total}}$)** govern **Storage Capacity ($M_{\text{weights}}$)**.
- **Active Parameters ($P_{\text{active}}$)** govern **Memory Bandwidth Traffic per Token ($M_{\text{active\_weights}}$)** and dictate generation speed:
  $$M_{\text{active\_weights}} = P_{\text{active}} \times \left(\frac{\text{Weight Precision Bits}}{8}\right) \times 1.05$$
- **Empirical MoE vs. Dense Benchmarks:**
  - *Apple M5 Pro (`307 GB/s`):* Dense `Qwen 3.8-27B` ($P_{\text{active}} = 27\text{B}$) runs at **14.7 TPS**, whereas sparse `Qwen 3.6-35B-A3B` ($P_{\text{total}} = 35\text{B}, P_{\text{active}} = 3\text{B}$) runs at **78.8 TPS** ($5.36\times$ faster).
  - *AMD Strix Halo (`256 GB/s`):* Dense `Llama 70B` ($P_{\text{active}} = 70\text{B}$) crawls at **5 TPS**, whereas MoE `OpenAI gpt-oss-120B` ($P_{\text{active}} = 5\text{B}$) runs at **46 TPS** ($9.2\times$ faster).
  - *Apple M5 Ultra (`1,200 GB/s`):* `GLM 5.3 744B-A40B` (~20GB read/token $\rightarrow$ **25–26 TPS**) runs $6\times$ faster than dense `Llama 405B` (~200GB read/token $\rightarrow$ **~4 TPS**).
  - *Kimi K3.1 Pro Bandwidth Wall ($P_{\text{total}} = 2.8\text{T}, P_{\text{active}} = 104\text{B}$):* Reads ~52 GB per token at 4-bit. A `273 GB/s` DGX Spark is physically capped at ~5.2 TPS ceiling, and an **8× DGX Spark cluster ($55,600)** achieves **2.2 TPS** in practice ($14\times$ slower than Moonshot's **31 TPS** API). Naive SSD streaming without RAM expert caching drops to **9.4 seconds/token (0.11 TPS)** (47 minutes for a 300-word reply).

#### 2. Decode Token Generation Speed ($\text{TPS}_{\text{decode}}$)
$$\text{TPS}_{\text{decode}} = \frac{\text{Memory Bandwidth (GB/s)}}{M_{\text{active\_weights}}\text{ (GB)}} \times \eta_{\text{engine}} \times \gamma_{\text{spec}} \times \delta_{\text{ctx}} \times \alpha_{\text{scaling}}$$
- $\eta_{\text{engine}}$: Software memory bus ceiling efficiency (`0.65–0.75` for dense models on `MLX`/`vLLM`; `0.35–0.50` for sparse MoE routing).
- $\gamma_{\text{spec}}$: Speculative Decoding / Multi-Token Prediction (MTP) multiplier:
  - `1.0`: Standard single-token autoregressive decoding (`11.6 TPS` on DGX Spark; `29.8 TPS` on M5 Max in `Qwen 27B`).
  - `1.35 – 1.50`: Apple Silicon `MLX + MTP / DFlash` (boosts M5 Max on `Qwen 27B` from **29 TPS in GGUF to 40–44 TPS in MLX**).
  - `1.40 – 2.20`: NVIDIA built-in MTP (`15.0–26.5 TPS` on DGX Spark via `vLLM`/Ollama).
  - `2.40 – 3.10`: External speculative draft model (`up to 36.6 TPS` on DGX Spark; boosts mixed GPU rigs from **18 TPS to 44–70 TPS**).
- $\delta_{\text{ctx}}$: **Context-Depth Attention Degradation Factor**:
  - Decode speed drops by **~40% to 53%** as context fills from 8K to 256K:
    - `M5 Max (Qwen 3.8-27B 4-bit)`: **30 TPS** at 8K $\rightarrow$ **14 TPS** at 256K ($\delta_{\text{ctx}} = 0.47$).
    - `M5 Ultra (Qwen 3.8-27B 4-bit)`: **56 TPS** at 8K $\rightarrow$ **50 TPS** at 32K $\rightarrow$ **35 TPS** at 128K ($\delta_{\text{ctx}} = 0.625$).
    - `M5 Ultra (Qwen Flash Next)`: **108 TPS** short $\rightarrow$ **61 TPS** at 128K ($\delta_{\text{ctx}} = 0.565$).

#### 3. Prompt Prefill Latency (TTFT), The M4 $\rightarrow$ M5 Compute Jump & The 1M-Token Prefill Cliff
Prefill processes input + scaffolding tokens in parallel and is **GPU compute-bound**, not memory-bandwidth bound:
- **Apple Silicon GPU Core Prefill Law & The Used M3 Ultra Trap:**
  - Within an Apple chip generation, per-core GPU prefill speed is constant across Base, Pro, Max, and Ultra, scaling linearly with GPU core count (8 cores on M1 Base to 80 cores on M5 Ultra).
  - Per-core prefill compute jumped **$3.5\times$ in the M5 generation**: from **151 units/core on M4 (and M1–M3)** to **531 units/core on M5/M6**.
  - *Procurement Consequence:* An **M5 Max (~21,000 prefill score)** reads prompts **$2\times$ faster than a used M3 Ultra (~10,000 prefill score)**, and an **M5 Pro** matches an **M3 Ultra** in reading speed.
- **The 94% Prefill Trap & Backend Multiplier ($\beta_{\text{backend}}$):**
  - Default unoptimized servers spend up to 94% of total response time in prefill (49s wait on an 8K prompt, dragging a 57 TPS model down to **3 TPS effective speed**; 80s wait on 32K Mac Studio). Switching to an optimized backend (`vLLM`, `SGLang`, `mlx-lm`, `gmlx`) drops 8K prefill from **49s to 1.7s** (and 32K Mac Studio prefill from **80s to 18s**; $\beta_{\text{backend}} = 1.0$ optimized vs. $0.035$ unoptimized).
- **Calibrated Cold Prefill Wait Times across Prompt Sizes:**
  - *20-Page Document (`Qwen 27B`):* **11s** (`M5 Ultra`) | **21s** (`M5 Max`) | **40s** (`M3 Ultra`) | **71s** (`M6 Base`) | **6 min** (`M2 Base`).
  - *32K Token Prompt:* **15–17s** (`2× DGX Sparks`) | **18–80s** (`M5 Ultra`) | **2.2 min** (`M5 Max`) | **4.2 min** (`M3 Ultra`) | **29 min** (`M4 Base`).
  - *128K Token Codebase Dump (`Qwen 27B`):* **10 min** (`M5 Ultra`) | **40 min** (`M3 Ultra`) | **2.3 hours** (`M4 Pro`).
  - *1,000,000-Token Prompt Prefill Cliff (`DeepSeek V4.1` / Long-Context):*
    - **8× RTX Pro 6000 Blackwell (`8,700 tok/s` prefill):** **~1.9 minutes** (`102 TPS` decode).
    - **4× DGX Spark Cluster (`4,000 tok/s` prefill):** **~4.2 minutes** (`66–117 TPS` decode).
    - **Used Mac Studio M3 Ultra 512GB (`390 tok/s` prefill):** **~42.7 minutes**.
    - **2× AMD Strix Halo Mini PCs (`148 tok/s` prefill):** **~1.9 hours**.
    - **16× AMD MI50 HBM Rig (`56 tok/s` prefill):** **~5.0 hours**.
    - **Dual EPYC DDR4 Server + RTX 3090 (`35 tok/s` prefill):** **~7.9 hours**.
- **End-to-End Effective TPS Equation (including Eviction Re-Prefill Penalty):**
  $$\text{TTFT (seconds)} = \frac{\left(T_{\text{in}} + S_{\text{effective}}\right) \times \tau_{\text{tokenizer}} \times (1 - r_{\text{cache}})}{\text{Prefill TPS}_{\text{hardware}} \times \beta_{\text{backend}} \times \psi_{\text{cached\_ctx}}} + \left(\text{Eviction Flag} \times \text{TTFT}_{\text{rebuild}}\right)$$
  $$\text{TPS}_{\text{effective}} = \frac{T_{\text{out}} \times \mu_{\text{thinking}}}{\text{TTFT} + \left(\frac{T_{\text{out}} \times \mu_{\text{thinking}}}{\text{TPS}_{\text{decode}}}\right)}$$

---

### Stage 3: Quantization Fidelity, 6-Layer Harnesses & Hardware Lifecycle Clocks

#### 1. Empirical Quantization Token-Agreement Fidelity (`token_agreement_rate`)
Evaluates quantization compression using Unsloth empirical token-agreement benchmarks against full precision:
- **4-Bit (`DeepSeek V4.1 Flash`, 298GB):** **98.5% agreement** (~1 word variation per 67 tokens). Full agentic reliability.
- **3-Bit (`DeepSeek V4.1 Flash`, 233.5GB):** **95.1% agreement** (~1 word variation per 20 tokens).
- **2-Bit (`Kimi K3 / K3.1 Pro`, 861GB Unsloth):** **90.4% agreement** (~1 word variation per 10 tokens).
- **2-Bit (`Kimi K3 / K3.1 Pro`, 711GB Unsloth / ISTA-DASLab):** **84.1% agreement** (~1 word variation per 6 tokens). Introduces a **15.5% general perplexity penalty**, **8.6% coding degradation**, and **5.3% agent task failure rate**.
- **3-Bit (`Qwen 3.8 Flash Next`, 93GB):** **81.6% agreement** (~1 word variation per 5 tokens).
- **Fallback Expert Routing Degradation:** On $\le 16\text{ GB}$ GPUs, hybrid engines like `Strata` drop routing from 6 to **5 active experts**, degrading complex reasoning. Flag any configuration with `token_agreement_rate < 0.90` with an agentic schema-break warning.

#### 2. The Three Hardware Lifecycle Clocks
1. **Clock 1 — The Software Clock (`software_support_years`):**
   - *Active Flagship (4–5+ yrs):* NVIDIA Blackwell (`RTX 5090`, `RTX Pro 5000/6000`, `DGX Spark GB10`), Hopper (`H100`/`H200`), Apple Silicon (`M5/M6` via `MLX`).
   - *Medium (2–3 yrs):* AMD Strix/Gorgon Halo, AMD RDNA3/RDNA4 workstations (ROCm upstreaming cadence), and older Apple `M1–M3`.
   - *Expired / Legacy (0–1 yr):* Used **Tesla V100 32GB** ($500–$700/card) and **AMD MI50** ($600/card). NVIDIA's **R580 driver branch is Volta's final stop**; `CUDA 13+` and `vLLM v0.9+ / v0.20` drop Compute Capability 7.0 (no FlashAttention-2, no modern PagedAttention), and mainline `ROCm` dropped the MI50.
2. **Clock 2 — The Model Clock (`model_fit_horizon`):**
   - Models bloat across point releases (`DeepSeek V4 Flash` = `151 GB` $\rightarrow$ `V4.1 Flash` = `298 GB` 4-bit + `196 GB Engram`, stranding 256GB machines at 4-bit and forcing 3-bit down-quantization).
3. **Clock 3 — The Money Clock (`annualized_useful_cost_eur`):**
   $$\text{Annualized Useful Cost} = \frac{\text{CapEx} \times (1 - r_{\text{resale}}) + (\text{Annual Software License} + \text{Annual Energy OpEx}) \times Y_{\text{useful}}}{Y_{\text{useful}}}$$

---

### Stage 4: Multi-Node Topologies, Disaggregation & Heterogeneous Routing

1. **Strict Power-of-Two Tensor Parallelism ($TP \in \{1, 2, 4, 8\}$):**
   - Tensor parallelism must divide attention heads evenly. Non-power-of-two node counts (3, 5, 6, 7, 10) are rejected or penalized ($\alpha_{\text{penalty}} \ge 0.35$) and automatically snapped to $\{1, 2, 4, 8\}$.
2. **Interconnect Scaling Efficiency ($\alpha_{\text{scaling}}$) & Cabling:**
   - `NVLink / NVSwitch` (H100/H200): $\alpha = 0.90$.
   - `PCIe Gen5` (4×–8× RTX Pro 6000): $\alpha = 0.75$.
   - `DGX Spark 4-Node Ring Cable` ($568 kit): Unifies 4× 128GB Sparks into a 512GB pool ($\alpha = 0.72$) without an external switch.
   - `Thunderbolt 5 RDMA Full Mesh` (120–128 Gbps across Mac Studios): $\alpha = 0.65$. Requires $\frac{N(N-1)}{2}$ direct cables (1 cable for 2 nodes, 6 cables for 4 nodes) and macOS recovery-mode RDMA enablement.
3. **Disaggregated Prefill-Decode Clusters (`disaggregated-pd`):**
   - Connects **2× DGX Sparks** (compute-dense prefill nodes) to **1× RTX Pro 6000 Blackwell** (1.8 TB/s decode node) over 200 Gbps RoCE, eliminating head-of-line prefill blocking in multi-user environments.
4. **Heterogeneous Modality & Semantic Routing Topologies (`heterogeneous-routed`):**
   - Combines multiple asymmetric GPUs with specialized host silicon:
     - **Authority Reasoning Tier:** RTX 3090 24GB or RTX 5090 32GB hosting heavy reasoning and complex coding models (`Qwen 3.8-27B`, `Flash Next`).
     - **Helper & Fast Worker Tier:** RTX 3060 12GB or RTX 4060 16GB dedicated to minor file edits, tool parameter extraction, and fast linting.
     - **Semantic Router & Vector Embedding:** RTX 2000 Ada (16GB ECC) hosting semantic intent classifiers and local vector embeddings.
     - **iGPU Vision Offload:** Routes visual document and screenshot understanding to Intel/AMD integrated graphics (via OpenVINO / ROCm), saving 4–6 GB of discrete VRAM for pure text generation.
     - **NPU Security & Audio Offload:** Pushes real-time audio transcription (Whisper) and prompt injection/jailbreak classification to the host NPU at <5W power draw.