# Module 6: Master Research Sources, Empirical Benchmarks & Citation Evidence Base

```text
================================================================================
MASTER EVIDENCE BASE: 2026 EMPIRICAL BENCHMARKS, VIDEO LABS & INDUSTRY STANDARDS
================================================================================
```

This document serves as the master evidence and citation catalog for the **Enterprise AI Infrastructure Decision Support System (TCO DSS)**. It maps real-world empirical lab benchmarks, secondary-market price trackings, driver/framework deprecation cliffs, and regulatory rulings directly into the system's physical inference equations (`specs/01`), financial algorithms (`specs/02`), seed catalogs (`specs/03`), Pydantic contracts (`specs/04`), and executive visualization components (`specs/05`).

---

## 1. Primary Empirical Video Benchmark Citations

### [YT-01] You Don't Need an Expensive GPU Anymore? Strata Changes Local AI
- **Creator / Channel:** Morgans Code (Oct 2026)
- **URL:** https://www.youtube.com/watch?v=v90_q8bIUlA
- **Core Findings & Calibrated Constants:**
  * **Desk, Shelf, Basement 3-Tier Architecture:** Partitions models into GPU VRAM (*Desk* = shared weights + hot experts), System RAM (*Shelf* = warm expert cache, $\ge 46\text{ GB}$ required, $64\text{ GB}$ optimal), and NVMe SSD (*Basement* = cold weights + 111 GB lookup table).
  * **Hardware Bus Scaling:** Moving an NVMe SSD from PCIe 3.0 to PCIe 4.0 increases offloaded generation speed by **+39.1%** ($6.9\text{ TPS} \rightarrow 9.6\text{ TPS}$).
  * **Host CPU Bottleneck:** On hybrid offloading, a 6-core CPU limits DeepSeek V4.1 Flash to **4–6 TPS**, while a 16-core CPU achieves **9–11 TPS**.
  * **Agent Turn Latency:** On an RTX 5070 (12 GB) + 64 GB DDR5 rig, a standard agentic turn ($2,700\text{ input} + 760\text{ output tokens}$) takes **15 seconds** on Qwen Flash Next vs. **~3 minutes** on DeepSeek V4.1 Flash 2-bit offload.
  * **Prefill Acceleration:** Strata achieves $2,800\text{ tok/s}$ prefill on 32K context (~12s wait) and sub-1-minute prefill on 128K context, outperforming unoptimized `llama.cpp` by $5.1\times$ ($2,320$ vs. $451\text{ tok/s}$).
- **Referenced In:** `specs/00_INDEX_AND_AGENT_ROUTER.md` (§1 Archetype 4), `specs/01_WORKLOAD_AND_PHYSICS_ENGINE.md` (§1.1, §2 Stage 1.5), `specs/03_CALIBRATED_2026_SEED_DATA.md` (§2 `rtx-5070-strata-64gb`), `specs/04_PYDANTIC_SCHEMAS_AND_CONTRACTS.md` (`DeploymentMode.TIERED_OFFLOAD_APPLIANCE`).

---

### [YT-02] The PC You Need For Every Size Of Local AI
- **Creator / Channel:** Locally (Nov 2026)
- **URL:** https://www.youtube.com/watch?v=3ZOKAeoEMB0
- **Core Findings & Calibrated Constants:**
  * **Quick-Fit Heuristic:** Quantifies memory sizing for 4-bit models: $\text{Max 4-Bit Params (B)} \approx \frac{\text{Advertised RAM} \times 0.67}{0.60}$.
  * **Artificial Analysis v5 Intelligence Ladder:** Traverses AA v5 scores from entry 16 GB ($20.1$) to 128 GB ($27.8$), 256 GB ($32.5$), and 1 TB+ ($46.0$).
  * **Budget Entry Pricing:** Profiles the RTX 5060 8 GB ($459 on Newegg) running 8B models at **62 TPS** in Ollama, and pairing with 32 GB system RAM to run Qwen 3.6-35B-A3B at **40 TPS**.
  * **Secondary Market Anchors:** Tracks secondary RTX 3090 24 GB pricing at **$1,778**, achieving **40 TPS** on Qwen 27B.
  * **MoE vs. Dense Bandwidth Math on 128 GB Unified Memory:** Dense Llama 70B ($P_{\text{active}} = 70\text{B}$) crawls at **5 TPS**, whereas MoE OpenAI gpt-oss-120B ($P_{\text{active}} = 5\text{B}$) runs at **46 TPS** ($9.2\times$ throughput ratio on identical hardware).
- **Referenced In:** `specs/01_WORKLOAD_AND_PHYSICS_ENGINE.md` (§2 Stage 1.1, §2 Stage 2.1), `specs/03_CALIBRATED_2026_SEED_DATA.md` (§1 AA v5 Staircase; §2 `rtx-5060-8gb`, `rtx-3090-24gb-used`, `mac-mini-m6-32gb`, `amd-strix-halo-128gb`).

---

### [YT-03] Qwen 3.8 vs 10 Tesla V100 GPUs
- **Creator / Channel:** MattMo (Oct 2026)
- **URL:** https://www.youtube.com/watch?v=sQenJEGBabM
- **Core Findings & Calibrated Constants:**
  * **Strict Power-of-Two Tensor Parallelism ($TP \in \{1, 2, 4, 8\}$):** Demonstrates that splitting attention heads across 10 GPUs introduces severe interconnect overhead and non-uniform tensor chunking compared to strict powers of two.
  * **MoE Interconnect Bypass:** Sparse MoE routing (`35B-A3B`) avoids PCIe/SXM2 bus saturation across multi-GPU rigs much more efficiently than dense 27B models.
- **Referenced In:** `specs/01_WORKLOAD_AND_PHYSICS_ENGINE.md` (§2 Stage 4.1 Strict Power-of-Two Rule), `specs/03_CALIBRATED_2026_SEED_DATA.md` (§2 `legacy-8x-v100-256gb`).

---

### [YT-04] The Cheapest 32GB Nvidia GPU You Can Buy for Local AI (Tesla V100)
- **Creator / Channel:** Lon.TV (Oct 2026)
- **URL:** https://www.youtube.com/watch?v=3P6m_QBIgAo
- **Core Findings & Calibrated Constants:**
  * **Secondary Hardware Pricing:** Tesla V100 32 GB HBM2 cards sell for **$500–$700** on secondary markets.
  * **Workstation Integration Friction:** Compute-only card requiring headless operation/secondary display GPU, custom 3D-printed high-RPM fan ducts, EPS 8-pin power adapters, and external OcuLink eGPU connections.
  * **Software Clock EOL Hard Wall:** NVIDIA R580 is the final driver series supporting Volta; CUDA 13 and `vLLM` v0.9+ drop Compute Capability 7.0 completely (disabling FlashAttention-2 and modern PagedAttention optimizations).
- **Referenced In:** `specs/01_WORKLOAD_AND_PHYSICS_ENGINE.md` (§2 Stage 3.2 Clock 1 Software Clock), `specs/02_TCO_FINOPS_AND_EU_COMPLIANCE.md` (§2.2 Thermal Throttling, §2.5 Legacy Deprecation), `specs/03_CALIBRATED_2026_SEED_DATA.md` (§2 `legacy-8x-v100-256gb`).

---

### [YT-05] Every Way to Get 512GB of VRAM for Local AI
- **Creator / Channel:** RepoChad (Oct 2026)
- **URL:** https://www.youtube.com/watch?v=3gy34XTFEIQ
- **Core Findings & Calibrated Constants:**
  * **Attention Footprint Scaling (MLA vs. Standard GQA):** DeepSeek Multi-Head Latent Attention compresses KV cache to **~890 bytes/token** ($< 1\text{ GB}$ VRAM at 1M context), whereas standard GQA/MHA requires **120–163.8 KB/token** ($128\text{–}164\text{ GB}$ VRAM at 1M context).
  * **1,000,000-Token Prefill Latency Cliff:** 8× RTX Pro 6000 Blackwell ($8,700\text{ tok/s}$) reads 1M tokens in **~1.9 min**; 4× DGX Sparks ($4,000\text{ tok/s}$) takes **~4.2 min**; used Mac Studio M3 Ultra 512GB ($390\text{ tok/s}$) takes **~42.7 min**; 16× AMD MI50 ($56\text{ tok/s}$) takes **~5.0 hours**; dual EPYC DDR4 server + RTX 3090 ($35\text{ tok/s}$) takes **~7.9 hours**.
  * **Secondary Market Mac Arbitrage:** Used Mac Studio M3 Ultra 512GB trades at **$16,500** (shipping immediately) vs. new M5 Ultra 512GB at **$22,299** (10–12 week factory backlog).
  * **Server RAM Cost Inversion:** 64 GB DDR5 ECC server sticks sell for **~$2,400** ($43–$46/GB), while 64 GB DDR4 ECC sticks sell for **~$400** (enabling dual EPYC + 512 GB DDR4 complete servers for $2,999).
  * **Cloud API Electricity Parity:** Reading a 1M prompt on DeepSeek API costs **$0.15** off-peak, while local power for 16× MI50s (12.5 kWh @ $0.18/kWh) costs **$2.27** (local power alone is **15× more expensive than the API call**).
- **Referenced In:** `specs/01_WORKLOAD_AND_PHYSICS_ENGINE.md` (§2 Stage 1.3 MLA vs. GQA, §2 Stage 2.3 1M Prefill Cliff), `specs/02_TCO_FINOPS_AND_EU_COMPLIANCE.md` (§1 Baseline D.3 Electricity Parity), `specs/03_CALIBRATED_2026_SEED_DATA.md` (§2 `mac-studio-m3-ultra-512gb`, `epyc-ddr4-pro-6000`, `dgx-spark-128gb`, `legacy-16x-mi50-256gb`), `specs/04_PYDANTIC_SCHEMAS_AND_CONTRACTS.md` (`AttentionMechanism.MULTI_HEAD_LATENT`).

---

### [YT-06] Is 192GB Worth It for Local AI? (Or Two 128GB Boxes?)
- **Creator / Channel:** Lem. (Oct 2026)
- **URL:** https://www.youtube.com/watch?v=ZsSfQEqwsfM
- **Core Findings & Calibrated Constants:**
  * **AMD Gorgon Halo (495) vs. Strix Halo (395):** Both share the identical 256-bit bus and 40 CUs. LPDDR5X clock bumps memory bandwidth from $256\text{ GB/s}$ to $273\text{ GB/s}$ (+6.6%), yielding only a **5%–7% empirical TPS increase** (GPT-OSS 120B: $51.1 \rightarrow 54.2\text{ TPS}$).
  * **The 192 GB Upgrade Trap:** Framework 128 GB DIY kit costs **$3,449** vs. 192 GB kit at **$6,799** (assembled: **$7,449**). Upgrading costs **$3,350 for +64 GB = >$52/GB**.
  * **OS Memory Allocation Limits:** Windows caps Strix Halo at 96 GB and Gorgon Halo at 160 GB; Linux reaches 118 GB and 180 GB usable respectively.
  * **The "Slow Lane" Tradeoff:** 192 GB fits 140 GB models (Qwen 235B) in a single quiet box, but generation speed is physically capped at **~12 TPS**.
  * **Clustering Arbitrage:** 2× 128 GB Framework Mini PCs cost **$6,898** ($99 more than 1× 192 GB box) and deliver **256 GB aggregate memory** over Ethernet.
- **Referenced In:** `specs/01_WORKLOAD_AND_PHYSICS_ENGINE.md` (§2 Stage 1.1 AMD Windows/Linux split caps), `specs/03_CALIBRATED_2026_SEED_DATA.md` (§1 AA v5 Staircase 192GB rung; §2 `amd-gorgon-halo-192gb`).

---

### [YT-07] Why 64GB of RAM Now Matters More Than Your GPU for Local AI
- **Creator / Channel:** Lem. (Nov 2026)
- **URL:** https://www.youtube.com/watch?v=3_uVmNjZ1QY
- **Core Findings & Calibrated Constants:**
  * **Component Price Inversion:** A 64 GB DDR5 RAM kit retails at **$949**, exceeding an RTX 5070 12 GB (**$899**).
  * **Offload Tiering Speed:** With MoE expert RAM caching (*Shelf*), DeepSeek V4.1 Flash runs at **4.3–4.9 TPS**; streaming directly from NVMe (*Basement* only) drops speed to **1.8–2.2 TPS** (RAM caching provides a **$2.2\times$ speedup**).
  * **Unconstrained Reasoning Latency:** DeepSeek unconstrained thinking (up to 32,768 tokens) at 4.7 TPS blocks execution for **~1.93 hours** before emitting the first answer token.
  * **ISTA-DASLab 2-Bit Perplexity Degradation:** 2-bit quantization increases perplexity by **15.5%** on general text, **8.6%** on code, and **5.3%** on agent tasks (the smallest 2-bit quant is 53% worse on prose).
  * **Strata 5-Expert Fallback Mode:** On $\le 16\text{ GB}$ cards, Strata evaluates only **5 of 6 active experts**, degrading complex tool reasoning.
- **Referenced In:** `specs/01_WORKLOAD_AND_PHYSICS_ENGINE.md` (§1.1 Thinking Latency Wall, §2 Stage 1.5, §2 Stage 3.1), `specs/02_TCO_FINOPS_AND_EU_COMPLIANCE.md` (§2.1 CapEx pricing), `specs/03_CALIBRATED_2026_SEED_DATA.md` (§3 Model Catalog `DeepSeek V4.1 Flash` 2-bit ISTA-DASLab).

---

### [YT-08] NEW DeepSeek Harness - Super Agent!
- **Creator / Channel:** Sam Witteveen (Nov 2026)
- **URL:** https://www.youtube.com/watch?v=OrcsMi2-IcM
- **Core Findings & Calibrated Constants:**
  * **Frontier Harness Evaluation (The 5.6× Cost Spread):** Across 30 identical tasks using Kimi K3, Codex scored 66.7%, Claude Code scored 63.3% at **$18.34/task**, and DeepSeek Harness (DSH Creator Mode) scored 63.3% at **$3.28/task** ($5.6\times$ cost differential holding model constant).
  * **Cordis Architecture:** Introduces spatiotemporal composability, cleanly detaching unneeded tools and state from context to prevent token bloat.
  * **Router Event Batching:** Router scales batch sizes from 1 to 2.8 under load (1 to 40 triggers/min), **dropping decision latency from 6.4s to 1.6s per decision**.
  * **Direct Worker PR Subscription Bypass:** Review comments bypass the central router once a PR is open, eliminating a **30% router token consumption spike**.
- **Referenced In:** `specs/01_WORKLOAD_AND_PHYSICS_ENGINE.md` (§1.2 The 5.6× Harness Scaffolding Spread), `specs/02_TCO_FINOPS_AND_EU_COMPLIANCE.md` (§1 Baseline B API cost calculation), `specs/03_CALIBRATED_2026_SEED_DATA.md` (§3 `deepseek-harness-dsh` preset), `specs/04_PYDANTIC_SCHEMAS_AND_CONTRACTS.md` (`HarnessType.DEEPSEEK_HARNESS_DSH`).

---

### [YT-09] Qwen Flash Next on the Olares One - Local LLM setup
- **Creator / Channel:** Luke's Dev Lab (Nov 2026)
- **URL:** https://www.youtube.com/watch?v=T-dygpUacgg
- **Core Findings & Calibrated Constants:**
  * **Olares One Appliance Architecture:** 3.5-liter headless appliance with an RTX 5090 Mobile (24 GB VRAM @ 900 GB/s) + 96 GB DDR5 RAM (**€3,200**).
  * **Qwen Flash Next Q4_K_XL Benchmarks:** Achieves **90 TPS** decode, $123\text{–}127\text{ tok/s}$ uncached prefill, and up to $1.1\text{M tok/s}$ cached prefill on Strata.
  * **Empirical Reasoning Accuracy:** Scores 15/15 on 128K context retrieval, **98% (47/48)** on progressive reasoning, and **100/100** on HumanEval Remix challenges.
  * **MCP Tool Loop Boundaries:** Zero-shot hands-off on Kanban and Blender MCP generation, but exhibits infinite test wait loops in complex Godot game development tasks without harness timeout guardrails.
- **Referenced In:** `specs/00_INDEX_AND_AGENT_ROUTER.md` (§1 Archetype 4), `specs/01_WORKLOAD_AND_PHYSICS_ENGINE.md` (§2 Stage 1.5, §2 Stage 2.2), `specs/03_CALIBRATED_2026_SEED_DATA.md` (§2 `olares-one-120gb`).

---

### [YT-10] Stop Upgrading Your AI Model (Build A Harness Instead)
- **Creator / Channel:** 100x Engineers (Oct 2026)
- **URL:** https://www.youtube.com/watch?v=QRFyNJnrHxM
- **Core Findings & Calibrated Constants:**
  * **6-Layer Harness Taxonomy:** Layer 1 (Deterministic Rubric), Layer 2 (Track Limits/Read-Only MCP), Layer 3 (Skills), Layer 4 (Independent Verifier), Layer 5 (Supervised Calibration), Layer 6 (Automation).
  * **Dual-Agent Verification Cost Multiplier ($\nu_{\text{verify}}$):** Adding an independent evaluator agent (`verifier.md`) with isolated context doubles token consumption ($\nu_{\text{verify}} = 2.0\times$).
  * **The `CONFIRMED` Protocol:** Evaluator agents must be explicitly authorized to emit `CONFIRMED` to prevent hallucinatory fault creation.
- **Referenced In:** `specs/01_WORKLOAD_AND_PHYSICS_ENGINE.md` (§1.1 Dual-Agent Verification Multiplier, §2 Stage 3.1), `specs/02_TCO_FINOPS_AND_EU_COMPLIANCE.md` (§1 Baseline B formula), `specs/04_PYDANTIC_SCHEMAS_AND_CONTRACTS.md` (`has_verification_agent_layer`).

---

### [YT-11] I Thought 2 TB of RAM Was Overkill… My AI Agents Disagree
- **Creator / Channel:** Alex Ziskind (Nov 2026)
- **URL:** https://www.youtube.com/watch?v=nwXEAVW0jFE
- **Core Findings & Calibrated Constants:**
  * **VRAM vs. System RAM Functional Split:** GPU VRAM governs instantaneous execution slots ($L_{\text{gpu}}$); System RAM governs parked agent workspace retention ($M_{\text{agent\_state}}$).
  * **The Conversational Eviction Tax:** Under 12 concurrent agents, **128 GB RAM** triggered 10 failures and 30 context evictions/rebuilds (**85 minutes** total). Doubling to **256 GB ECC DDR5 (6,400 MT/s)** allowed all 12 agents to finish in **59 minutes** (a **26-minute / 30.6% speedup** with zero context rebuilds; peak RAM: 150 GB). 16 agents finished in 78 minutes.
  * **Radeon R9700 32 GB Workstation ($1,850 / $2,000):** Runs 124B MoE (`Link 3.0 Flash`, 131K context) at **38 TPS** offloaded (5.5 GB on GPU, ~90 GB in RAM); sustains 8 concurrent agents at **7 TPS/agent** (vs. 8.5 TPS on an RTX Pro 6000).
  * **Future Architecture Reference:** AMD Halo Station (2027) configurations pairing **2 TB of DDR5 System RAM with 576 GB HBM3 GPU memory**.
- **Referenced In:** `specs/00_INDEX_AND_AGENT_ROUTER.md` (§1 Archetype 1, 4), `specs/01_WORKLOAD_AND_PHYSICS_ENGINE.md` (§1.4 Multi-Agent State Retention & Eviction Tax; §2 Stage 1.4), `specs/02_TCO_FINOPS_AND_EU_COMPLIANCE.md` (§2.2 Financial Cost of Conversational Eviction), `specs/03_CALIBRATED_2026_SEED_DATA.md` (§2 `radeon-r9700-32gb`, `threadripper-pro-256gb`, `amd-halo-station-2tb`; §4 Agent Headroom Table), `specs/04_PYDANTIC_SCHEMAS_AND_CONTRACTS.md` (`concurrent_agent_instances`, `system_ram_gb`, `context_eviction_risk`), `specs/05_VISUALIZATION_UX_AND_SYSTEM_DESIGN.md` (§3 View 1, View 3).

---

### [YT-12] I Built My Own Intelligent AI Gateway
- **Creator / Channel:** Techno Tim (Oct 2026)
- **URL:** https://www.youtube.com/watch?v=ukv-LIOI6_E
- **Core Findings & Calibrated Constants:**
  * **Heterogeneous Asymmetric 3-GPU Topology:** RTX 3090 24 GB (authority/heavy coding) + RTX 3060 12 GB (helper/terminal edits) + RTX 2000 Ada 16 GB (router/RAG embeddings).
  * **Disaggregated Vision Processing (iGPU):** Offloads the vision encoder to the Intel Core Ultra iGPU via OpenVINO, converting images to embeddings and feeding text-only weights to the RTX 3090 (freeing 4–6 GB VRAM on the primary GPU).
  * **Ultra-Low-Power NPU Offloading:** Runs Whisper Small (STT), Kokoro (TTS), and prompt injection screening on the Intel NPU via OpenVINO at near-zero power and latency.
- **Referenced In:** `specs/00_INDEX_AND_AGENT_ROUTER.md` (§1 Archetype 8), `specs/01_WORKLOAD_AND_PHYSICS_ENGINE.md` (§1.5 Disaggregated Modality Pipelines), `specs/02_TCO_FINOPS_AND_EU_COMPLIANCE.md` (§2.1 Scavenged Multi-GPU Workstation TCO), `specs/03_CALIBRATED_2026_SEED_DATA.md` (§2 `heterogeneous-scavenged-3gpu`), `specs/04_PYDANTIC_SCHEMAS_AND_CONTRACTS.md` (`DeploymentMode.HETEROGENEOUS_ROUTED_APPLIANCE`, `has_igpu_vision_offload`, `has_npu_audio_security_offload`), `specs/05_VISUALIZATION_UX_AND_SYSTEM_DESIGN.md` (§3 View 1, View 6).

---

### [YT-16] Can a NVIDIA AI Box Replace your $200 AI Subscription?
- **Creator / Channel:** Local Explained (Oct 2026)
- **URL:** https://www.youtube.com/watch?v=MOI8F2QL-J0
- **Core Findings & Calibrated Constants:**
  * **DGX Spark Hardware Profile:** Profiles NVIDIA GB10 Grace Blackwell unified architecture across 64 GB ($4,999) and 128 GB ($6,950) SKUs (273 GB/s unified memory bandwidth, 45W idle / 90W load).
  * **Hybrid Attention KV Footprint:** Verifies Qwen 3.8-27B maintaining dynamic KV cache across only 16 of its 64 layers ($r_{\text{kv\_active}} = 0.25$), consuming $17\text{ GB}$ KV cache for a total footprint of $34\text{ GB}$ at 250K context.
  * **Agent Scaffolding Drag:** Measures prompt bloat of `claude-code` (~33,000 tokens/turn) vs. `opencode` (~7,000 tokens/turn).
  * **Multi-Token Prediction Acceleration:** Demonstrates built-in MTP boosting DGX Spark decode from $11.6\text{ TPS}$ to $26.5\text{–}36.6\text{ TPS}$ with external draft models.
  * **Single-User Token Output Valuation:** Single-user hardware generating 11.6 TPS for 176 monthly working hours produces ~7.35M tokens/month, worth only **~$21.39/month** at OpenRouter market rates.
- **Referenced In:** `specs/01_WORKLOAD_AND_PHYSICS_ENGINE.md` (§1.1, §1.2, §2 Stage 1.3, §2 Stage 2.2), `specs/02_TCO_FINOPS_AND_EU_COMPLIANCE.md` (§1 Baseline D.1), `specs/03_CALIBRATED_2026_SEED_DATA.md` (§2 `dgx-spark-64gb`, `dgx-spark-128gb`).

---

### [YT-17] I Gave Local AI and the Cloud the Exact Same Job
- **Creator / Channel:** Alex Ziskind (Aug 2026)
- **URL:** https://www.youtube.com/watch?v=ujs0_cpAnaw
- **Core Findings & Calibrated Constants:**
  * **Thunderbolt 5 RDMA Mesh Topology:** Connects 4× 512 GB Mac Studio nodes into a 2 TB unified memory cluster using a 6-cable full-mesh Thunderbolt 5 RDMA configuration ($\alpha_{\text{scaling}} \approx 0.65$).
  * **Distributed Model Execution:** Evaluates Kimi K3 (2.8T MoE, 817 GB Q4 weights) across distributed Apple Silicon nodes.
  * **Power-of-Two Enforcement:** Snaps cluster node counts strictly to powers of two ($TP \in \{1, 2, 4, 8\}$) to prevent attention head splitting imbalances.
  * **Apple Silicon Prefill Latency Disparity:** Identifies the prefill bottleneck on unified memory (238 TPS prefill vs. 14.7 TPS decode), causing an identical agentic full-stack development task to take **4 hours on local hardware vs. 15 minutes on cloud APIs**.
- **Referenced In:** `specs/00_INDEX_AND_AGENT_ROUTER.md` (§1 Archetype 2), `specs/01_WORKLOAD_AND_PHYSICS_ENGINE.md` (§2 Stage 2.3, §2 Stage 4.1, §2 Stage 4.2), `specs/02_TCO_FINOPS_AND_EU_COMPLIANCE.md` (§2.4 Wait-Time Penalty).

---

### [YT-18] Don't Buy a Mac Mini For Local AI (Do This)
- **Creator / Channel:** Kai (Sep 2026)
- **URL:** https://www.youtube.com/watch?v=IRyiP_U7RuA
- **Core Findings & Calibrated Constants:**
  * **Apple Unified Memory Pricing Law:** Quantifies Apple's flat **$25/GB** memory upgrade pricing, creating steep price cliffs across product lines.
  * **Default macOS Allocation Wall:** Out-of-the-box macOS reserves ~25% memory for system overhead, leaving only ~19 GB usable on a 24 GB machine.
  * **Hardware Product-Line Cliff:** Highlights the $2,400 expenditure gap required to step up from a 64 GB Mac Mini ($2,699) to a 128 GB Mac Studio ($5,099).
  * **2026 Component Street Markups:** Tracks HBM/GDDR7 supply constraints pushing retail RTX 5090 street prices past $4,000.
  * **The 94% Prefill Trap:** Measures unoptimized default inference backends spending 94% of total turn latency in prefill (49s wait on an 8K prompt, dropping to 1.7s when swapping to an optimized backend like `vLLM` or `gmlx`).
  * **MoE vs. Dense Bandwidth Math:** Proves sparse MoE Qwen 3.6-35B-A3B ($P_{\text{active}} = 3\text{B}$) achieves **78.8 TPS** on an M5 Pro, while dense Qwen 3.8-27B ($P_{\text{active}} = 27\text{B}$) is limited to **14.7 TPS** ($5.36\times$ ratio).
- **Referenced In:** `specs/01_WORKLOAD_AND_PHYSICS_ENGINE.md` (§2 Stage 1.1, §2 Stage 2.1, §2 Stage 2.3), `specs/03_CALIBRATED_2026_SEED_DATA.md` (§2 `mac-mini-m6-16gb`, `mac-mini-m6-32gb`, `mac-mini-m5-pro-64gb`).

---

### [YT-19] Every Size Local AI In 24 Minutes
- **Creator / Channel:** Tina Huang (Sep 2026)
- **URL:** https://www.youtube.com/watch?v=rPGJhrunbxo
- **Core Findings & Calibrated Constants:**
  * **Quick-Fit Sizing Rule Formulation:** Establishes the parameter capacity rule for quantized models: $\text{Max 4-Bit Parameters (B)} \approx \frac{\text{Advertised RAM} \times 0.75}{0.60}$.
  * **Multi-Tier Capacity vs. Bandwidth Mapping:** Maps operational trade-offs across MacBook Pro (32 GB), Mac Studio (64 GB), AMD Ryzen AI Halo (128 GB advertised / 96 GB usable on Windows), discrete RTX 4090 (24 GB), and 8× H100 SXM clusters (640 GB).
- **Referenced In:** `specs/01_WORKLOAD_AND_PHYSICS_ENGINE.md` (§2 Stage 1.1), `specs/03_CALIBRATED_2026_SEED_DATA.md` (§1, §2).

---

### [YT-20] Every Way to Get 256 GB of VRAM for Local AI
- **Creator / Channel:** RepoChad (Oct 2026)
- **URL:** https://www.youtube.com/watch?v=h8dxm7UEStQ
- **Core Findings & Calibrated Constants:**
  * **The Three Lifecycle Clocks:** Defines the evaluation framework for Software Clock (framework and driver EOL), Model Clock (point-release weight growth), and Money Clock (true annualized useful cost including power and resale).
  * **Legacy Architecture Deprecation:** Details the obsolescence of legacy 8× Tesla V100 and AMD MI50 rigs due to exclusion from CUDA 13, modern `vLLM` (v0.9+), and FlashAttention-2, alongside a $1,900/year electricity penalty.
  * **macOS Memory Limit Override:** Documents terminal override commands (`sudo sysctl iogpu.wired_limit_mb=...`) to expand unified memory allocation to 90%–94% usable RAM.
  * **Enterprise Concurrency Density:** Demonstrates 4× RTX Pro 6000 Blackwell workstations serving 32 concurrent developers at **900+ aggregate TPS**, reducing local cost to ~$1.00 per 1M tokens.
  * **Model Bloat Velocity:** Tracks architecture growth from DeepSeek V4 (151 GB) to DeepSeek V4.1 Flash (510 GB + 196B Engram SSD lookup table).
- **Referenced In:** `specs/01_WORKLOAD_AND_PHYSICS_ENGINE.md` (§2 Stage 1.1, §2 Stage 1.4, §2 Stage 3.2), `specs/02_TCO_FINOPS_AND_EU_COMPLIANCE.md` (§2.2), `specs/03_CALIBRATED_2026_SEED_DATA.md` (§2 `rtx-pro-6000-96gb`, `cluster-8x-pro-6000`).

---

### [YT-21] Which AI Models Can M5 Ultra Mac Studio Actually Run?
- **Creator / Channel:** Forward Pass (Oct 2026)
- **URL:** https://www.youtube.com/watch?v=PfSDw9IgdgM
- **Core Findings & Calibrated Constants:**
  * **M5 Ultra Hardware Profile:** Evaluates M5 Ultra 512 GB (1.2 TB/s unified memory bandwidth, neural accelerators sustaining 2,700 TPS prefill at 32K context).
  * **MoE Dual-Parameter Law Formulation:** Compares memory traffic per token: GLM 5.3 (744B-A40B) reads ~20 GB weights/token achieving **25–26 TPS**, whereas dense Llama 405B reads ~200 GB weights/token achieving only **~4 TPS**.
  * **Context Degradation Curve:** Measures attention throughput tapering on large contexts, showing Qwen Flash Next dropping from **108 TPS** at short context to **61 TPS** at 128K context ($\delta_{\text{ctx}} = 0.565$).
- **Referenced In:** `specs/01_WORKLOAD_AND_PHYSICS_ENGINE.md` (§2 Stage 2.1, §2 Stage 2.2), `specs/03_CALIBRATED_2026_SEED_DATA.md` (§2 `mac-studio-m5-ultra-256gb`, `mac-studio-m5-ultra-512gb`).

---

### [YT-22] Don't Buy a Mac Studio M5 Ultra For Local AI (Do This)
- **Creator / Channel:** Devsplainers (Sep 2026)
- **URL:** https://www.youtube.com/watch?v=TdnshBitkzo
- **Core Findings & Calibrated Constants:**
  * **Opportunity Cost of Capital:** Incorporates a 4.5% annual capital opportunity rate into workstation CapEx projections.
  * **Resale Value Divergence:** Highlights the financial gap between official Apple trade-in (~10% after 3 years) and peer-to-peer secondary market value retention (60%–65%).
  * **Distributed MLX / Exo Stability Limits:** Documents packet drop rates and cluster disconnects under high-throughput agentic tool-calling on Thunderbolt 5 RDMA meshes.
  * **Sub-2-Bit Quantization Breakdown:** Identifies reliability failure modes where 1.5-bit to 2-bit quantization causes agentic loops to produce malformed tool call syntax.
  * **Work Schedule Economics:** Analyzes the cost divergence between interactive workday coding (developer actively waiting on responses) and unattended overnight background batch loops.
- **Referenced In:** `specs/00_INDEX_AND_AGENT_ROUTER.md` (§1), `specs/01_WORKLOAD_AND_PHYSICS_ENGINE.md` (§1.1, §2 Stage 3.1, §2 Stage 4.2), `specs/02_TCO_FINOPS_AND_EU_COMPLIANCE.md` (§2.1, §2.2).

---

## 2. Industry Technical Standards, Empirical Whitepapers & Regulatory References

| Ref ID | Organization / Author | Publication / Standard | Core Calibrated Constants & Findings | Primary Spec Sections |
|---|---|---|---|---|
| **[IND-01]** | **Artificial Analysis** | *LLM Quality & Price Index v5 (2026)* | Normalized Intelligence Ladder: Claude Opus 5.5 (`58.4`), Kimi K3.1 Pro (`46.0`), DeepSeek V4.1 Flash (`32.5`), GLM 5.3 Flash (`27.8`), Qwen 3.8-27B (`20.1`), Gemma 4 12B (`14.5`). Negative reference: Mistral Large 4 (`26.0`), Inkling (`12.5`), Nemotron 3 Ultra (`11.8`). | `01_WORKLOAD_AND_PHYSICS_ENGINE.md` (§2 Stage 1.1), `03_CALIBRATED_2026_SEED_DATA.md` (§1, §3), `05_VISUALIZATION_UX_AND_SYSTEM_DESIGN.md` (View 1, 4) |
| **[IND-02]** | **SemiAnalysis** | *InferenceX Throughput & Hardware Scaling Benchmarks* | H100 SXM prefill ceiling up to 18,000 tok/s ($5,900\text{ tok/s}$ on `gpt-oss-120b`). RTX Pro 6000 Blackwell 1.8 TB/s bus and 8-card scaling ($8,700\text{ tok/s}$ at 32K context). | `01_WORKLOAD_AND_PHYSICS_ENGINE.md` (§2 Stage 2.3), `03_CALIBRATED_2026_SEED_DATA.md` (§2 `h100-80gb-sxm`, `rtx-pro-6000-96gb`) |
| **[IND-03]** | **Unsloth AI** | *Quantization Token-Agreement Benchmarks* | Empirical token agreement vs. full precision: DeepSeek V4.1 4-bit (98.5%), DeepSeek V4.1 3-bit (95.1%), Kimi K3 2-bit (90.4% / 84.1%), Qwen Flash Next 3-bit (81.6%). Sub-90% agreement triggers an agent schema break warning. | `01_WORKLOAD_AND_PHYSICS_ENGINE.md` (§2 Stage 3.1), `03_CALIBRATED_2026_SEED_DATA.md` (§3 Model Catalog), `04_PYDANTIC_SCHEMAS_AND_CONTRACTS.md` (`token_agreement_rate`) |
| **[IND-04]** | **Bifrost Project** | *Compiled Proxy Gateway Benchmark vs. LiteLLM* | Python gateway serialization latency ($100\text{–}500\text{ ms}$ P99) vs. compiled Rust/Go Bifrost gateway ($11\text{–}840\ \mu\text{s}$). Proxy gateway RAM scales as $\text{Peak Streams} \times \text{Context P99}$. | `01_WORKLOAD_AND_PHYSICS_ENGINE.md` (§1.3), `04_PYDANTIC_SCHEMAS_AND_CONTRACTS.md` (`GatewayType`) |
| **[IND-05]** | **BDEW (Bundesverband der Energie- und Wasserwirtschaft)** | *German Electricity Price Analysis (2026)* | SME Industrial electricity: **€0.172 / kWh**. Commercial office electricity: **€0.280 / kWh**. Data center cooling PUE (1.15 to 1.50) adds $1,000–$2,000/kW/year. | `02_TCO_FINOPS_AND_EU_COMPLIANCE.md` (§2.2), `03_CALIBRATED_2026_SEED_DATA.md` (§5), `04_PYDANTIC_SCHEMAS_AND_CONTRACTS.md` (`ElectricityTariffTier`) |
| **[IND-06]** | **Eurostat & National Labor Codes** | *Cross-Border Intra-EU IT Compensation & Social Taxes (2026)* | Munich HQ Senior MLOps: €120,000 base + 21% employer social contribution (*Lohnnebenkosten*) = **€145,200/yr (€12,100/mo)**. Romania EU Branch: €75,000 base + 2.25% CAM (~4% with perks) = **€78,000/yr (€6,500/mo)**. Net **46.3% personnel OpEx savings** under 100% GDPR sovereignty. | `02_TCO_FINOPS_AND_EU_COMPLIANCE.md` (§2.4), `03_CALIBRATED_2026_SEED_DATA.md` (§5), `04_PYDANTIC_SCHEMAS_AND_CONTRACTS.md` (`EuEngineeringHub`), `05_VISUALIZATION_UX_AND_SYSTEM_DESIGN.md` (View 5) |
| **[IND-07]** | **NVIDIA Corporation** | *NVIDIA AI Enterprise Software Licensing Policy* | Mandatory NIM software license for enterprise-supported workstations: **$4,500 (€4,150) per GPU/year** ($18,000/yr for a 4-card RTX Pro 6000 node). | `01_WORKLOAD_AND_PHYSICS_ENGINE.md` (§2 Stage 3.2 Clock 3), `02_TCO_FINOPS_AND_EU_COMPLIANCE.md` (§2.5), `04_PYDANTIC_SCHEMAS_AND_CONTRACTS.md` (`enable_nvidia_nim_licensing`) |
| **[IND-08]** | **Meta Platforms** | *Llama 4 Community License Agreement* | Explicit territorial restriction prohibiting commercial use for companies whose principal place of business is in the European Union. | `02_TCO_FINOPS_AND_EU_COMPLIANCE.md` (§1 Baseline C.3), `03_CALIBRATED_2026_SEED_DATA.md` (§3 Model Catalog), `04_PYDANTIC_SCHEMAS_AND_CONTRACTS.md` (`LicenseType.LLAMA_4_EU_RESTRICTED`) |
| **[IND-09]** | **Hetzner Online / Scaleway** | *Dedicated EU Cloud Bare-Metal Server Listings* | Hetzner dedicated GPU bare-metal: **€1,197/mo**. Scaleway dedicated GPU server: **€2,093/mo**. Baseline comparison against purchased hardware amortization (~€505/mo CapEx). | `02_TCO_FINOPS_AND_EU_COMPLIANCE.md` (§1 Baseline C.2), `03_CALIBRATED_2026_SEED_DATA.md` (§2 `hetzner-scaleway-eu-gpu`), `05_VISUALIZATION_UX_AND_SYSTEM_DESIGN.md` (View 2) |
| **[IND-10]** | **Devox / Spheron Whitepapers** | *Enterprise Self-Hosting GPU Utilization Viability Studies* | **70% GPU Utilization Rule:** Self-hosted inference clusters only achieve net savings over PAYG cloud APIs when sustained utilization exceeds 70% ($\ge 8,000$ conversations/day or monthly API spend $> \$50,000/\text{mo}$). | `02_TCO_FINOPS_AND_EU_COMPLIANCE.md` (§2.3), `04_PYDANTIC_SCHEMAS_AND_CONTRACTS.md` (`meets_70_percent_utilization_threshold`), `05_VISUALIZATION_UX_AND_SYSTEM_DESIGN.md` (View 2) |

---

## 3. Master Cross-Reference Correlation Matrix

| Citation Key | Topic / Technology Covered | Primary Metric / Finding | Exact Spec Module & Section |
|---|---|---|---|
| **[YT-01]** | Strata 3-Tier Offload Engine | PCIe 3.0 vs. 4.0 (6.9 $\rightarrow$ 9.6 TPS); 6-core vs. 16-core CPU bottleneck; 15s vs. 3m agent turn | `specs/01` (§1.1, §2 Stage 1.5), `specs/03` (§2) |
| **[YT-02]** | Parameter Capacity & Intelligence Ladder | $(M_{\text{RAM}} \times 0.67)/0.60$; sub-$500 RTX 5060; RTX 3090 $1,778; 70B dense (5 TPS) vs. 120B MoE (46 TPS) | `specs/01` (§2 Stage 1.1, Stage 2.1), `specs/03` (§1, §2) |
| **[YT-03]** | Multi-GPU Tensor Parallelism | Power-of-two tensor parallelism ($TP \in \{1, 2, 4, 8\}$); MoE interconnect bypass | `specs/01` (§2 Stage 4.1), `specs/03` (§2) |
| **[YT-04]** | Volta V100 Secondary Hardware & EOL | $500–$700 card cost; R580 final driver; CUDA 13 & vLLM 0.9+ Compute Capability 7.0 EOL | `specs/01` (§2 Stage 3.2 Clock 1), `specs/02` (§2.2), `specs/03` (§2) |
| **[YT-05]** | 512 GB Architectures & Attention Scaling | DeepSeek MLA (890 B/tok, <1GB @ 1M ctx) vs. GQA (129GB @ 1M ctx); 1M prefill cliff (1.9m vs. 42.7m vs. 7.9h); 15× power cost penalty | `specs/01` (§2 Stage 1.3, Stage 2.3), `specs/02` (§1 Baseline D), `specs/03` (§2) |
| **[YT-06]** | AMD Gorgon Halo (192 GB) | +6.6% bandwidth yields only 5%–7% TPS gain; $3,350 for +64 GB upgrade trap; Windows/Linux VRAM caps | `specs/01` (§2 Stage 1.1), `specs/03` (§1, §2) |
| **[YT-07]** | DDR5 RAM Pricing & 2-Bit Quantization | 64 GB DDR5 ($949) > RTX 5070 ($899); RAM shelf gives 2.2× speedup; 32k thinking tokens @ 4.7 TPS = 1.93h wait; 2-bit perplexity hit | `specs/01` (§1.1, §2 Stage 1.5, Stage 3.1), `specs/02` (§2.1), `specs/03` (§3) |
| **[YT-08]** | Agent Scaffolding & DeepSeek Harness | 5.6× cost spread (Claude Code $18.34 vs. DSH $3.28); Cordis composability; router batching drops latency 6.4s to 1.6s | `specs/01` (§1.2), `specs/02` (§1 Baseline B), `specs/03` (§3), `specs/04` |
| **[YT-09]** | Olares One Compact Appliance | RTX 5090M (24 GB) + 96 GB DDR5 (€3,200); Flash Next @ 90 TPS; 98% reasoning; HumanEval Remix 100/100 | `specs/00` (§1 Archetype 4), `specs/01` (§2 Stage 1.5, Stage 2.2), `specs/03` (§2) |
| **[YT-10]** | 6-Layer Harness & Dual-Agent Verifiers | Layer 4 independent verifier introduces 2.0× token burn multiplier ($\nu_{\text{verify}}$); `CONFIRMED` rule | `specs/01` (§1.1, Stage 3.1), `specs/02` (§1 Baseline B), `specs/04` |
| **[YT-11]** | Multi-Agent State Retention & Evictions | VRAM = concurrency slots; System RAM = agent workspace retention; Conversational Eviction Tax (128 GB = 30 rebuilds & 85m; 256 GB = 0 rebuilds & 59m); R9700 32 GB @ 38 TPS | `specs/00` (§1), `specs/01` (§1.4, Stage 1.4), `specs/02` (§2.2), `specs/03` (§2, §4), `specs/04`, `specs/05` |
| **[YT-12]** | Scavenged Heterogeneous 3-GPU Gateway | RTX 3090 (authority) + 3060 (helper) + Ada 2000 (router); OpenVINO iGPU vision offload; Intel NPU audio/security offload | `specs/00` (§1 Archetype 8), `specs/01` (§1.5), `specs/02` (§2.1), `specs/03` (§2), `specs/04`, `specs/05` |
| **[YT-16]** | DGX Spark & Token Production Valuation | GB10 Grace Blackwell 64 GB/128 GB @ 273 GB/s; Qwen 27B hybrid KV (17 GB @ 250K ctx); MTP boosts decode to 26.5–36.6 TPS; 7.35M tok/mo = ~$21.39/mo value | `specs/01` (§1.1, §1.2, Stage 1.3, Stage 2.2), `specs/02` (§1 Baseline D.1), `specs/03` (§2) |
| **[YT-17]** | Thunderbolt 5 Mesh & Local vs. Cloud Gap | 4-node 2 TB Mac Studio cluster via 6 TB5 cables ($\alpha_{\text{scaling}} \approx 0.65$); Kimi K3 2.8T MoE; 4h local vs. 15m cloud task | `specs/00` (§1 Archetype 2), `specs/01` (§2 Stage 2.3, Stage 4.1, Stage 4.2), `specs/02` (§2.4) |
| **[YT-18]** | Apple Unified Memory Pricing & Prefill Trap | Apple flat $25/GB upgrade cliff; 25% system reservation; $2,400 gap Mini to Studio; 94% prefill trap (49s wait on 8K $\rightarrow$ 1.7s); MoE 35B-A3B (78.8 TPS) vs. 27B dense (14.7 TPS) | `specs/01` (§2 Stage 1.1, Stage 2.1, Stage 2.3), `specs/03` (§2) |
| **[YT-19]** | Quantized Sizing Rule & Platform Mapping | $\text{Max 4-Bit Params (B)} \approx \frac{\text{Advertised RAM} \times 0.75}{0.60}$; platform trade-offs from 32 GB laptop to 640 GB H100 cluster | `specs/01` (§2 Stage 1.1), `specs/03` (§1, §2) |
| **[YT-20]** | The Three Lifecycle Clocks & 4× Pro 6000 | Software, Model, and Money Clocks; Volta/MI50 EOL; macOS `sysctl` 90%–94% override; 4× Pro 6000 serves 32 users @ 900+ TPS (~$1.00/1M tokens); DeepSeek V4 $\rightarrow$ V4.1 bloat | `specs/01` (§2 Stage 1.1, Stage 1.4, Stage 3.2), `specs/02` (§2.2), `specs/03` (§2) |
| **[YT-21]** | M5 Ultra Profile & MoE Dual-Parameter Law | M5 Ultra 512 GB (1.2 TB/s, 2,700 tok/s prefill); GLM 5.3 (25–26 TPS) vs. Llama 405B (~4 TPS); Context degradation curve ($\delta_{\text{ctx}} = 0.565$ at 128K context) | `specs/01` (§2 Stage 2.1, Stage 2.2), `specs/03` (§2) |
| **[YT-22]** | Workstation CapEx Opportunity Cost & MLX Mesh | 4.5% annual capital opportunity cost; Apple trade-in (~10%) vs. P2P resale (60%–65%); TB5 mesh packet drops; sub-2-bit JSON syntax failure; interactive vs. unattended batch | `specs/00` (§1), `specs/01` (§1.1, Stage 3.1, Stage 4.2), `specs/02` (§2.1, §2.2) |
| **[IND-01]** | Artificial Analysis v5 Benchmark Index | Normalized open-weights vs. frontier scores: Opus 5.5 (`58.4`), Kimi K3.1 (`46.0`), DeepSeek V4.1 (`32.5`), GLM 5.3 (`27.8`), Qwen 27B (`20.1`) | `specs/01` (§2 Stage 1.1), `specs/03` (§1, §3), `specs/05` (View 1, 4) |
| **[IND-02]** | SemiAnalysis InferenceX Benchmarks | H100 SXM prefill ($18,000\text{ tok/s}$); RTX Pro 6000 Blackwell 1.8 TB/s bus and 8-card scaling ($8,700\text{ tok/s}$) | `specs/01` (§2 Stage 2.3), `specs/03` (§2) |
| **[IND-03]** | Unsloth Token-Agreement Empirical Data | DeepSeek V4.1 4-bit (98.5%), 3-bit (95.1%), Kimi K3 2-bit (90.4% / 84.1%), Qwen Flash Next 3-bit (81.6%) | `specs/01` (§2 Stage 3.1), `specs/03` (§3), `specs/04` |
| **[IND-04]** | Bifrost Compiled Proxy Performance | Python gateway serialization ($100\text{–}500\text{ ms}$) vs. compiled Rust/Go Bifrost ($11\text{–}840\ \mu\text{s}$) | `specs/01` (§1.3), `specs/04` |
| **[IND-05]** | BDEW German Energy Tariff Analysis | SME Industrial electricity (€0.172/kWh) vs. commercial office (€0.280/kWh); Cooling PUE multipliers | `specs/02` (§2.2), `specs/03` (§5), `specs/04` |
| **[IND-06]** | Intra-EU Cross-Border Compensation | Munich HQ Senior MLOps (€145.2k/yr total) vs. Romania EU Branch (€78.0k/yr total); 46.3% personnel savings under 100% GDPR sovereignty | `specs/02` (§2.4), `specs/03` (§5), `specs/04`, `specs/05` (View 5) |
| **[IND-07]** | NVIDIA AI Enterprise Licensing Policy | Mandatory NIM container license on enterprise workstations: $4,500 (€4,150) per GPU/yr ($18,000/yr for 4-GPU node) | `specs/01` (§2 Stage 3.2 Clock 3), `specs/02` (§2.5), `specs/04` |
| **[IND-08]** | Meta Llama 4 Community License | Explicit territorial restriction prohibiting commercial use for entities domiciled in the EU | `specs/02` (§1 Baseline C.3), `specs/03` (§3), `specs/04` |
| **[IND-09]** | Hetzner & Scaleway Dedicated Cloud Servers | Dedicated EU bare-metal GPU rental: Hetzner €1,197/mo, Scaleway €2,093/mo vs. €505/mo hardware amortization | `specs/02` (§1 Baseline C.2), `specs/03` (§2), `specs/05` (View 2) |
| **[IND-10]** | Enterprise GPU Utilization Thresholds | 70% GPU Utilization Rule: self-hosting on-prem clusters only saves money when sustained utilization exceeds 70% | `specs/02` (§2.3), `specs/04`, `specs/05` (View 2) |