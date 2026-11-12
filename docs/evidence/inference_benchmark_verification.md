# Local LLM Inference Performance Verification & Bottleneck Analysis

This document provides a structured verification of empirical benchmark claims against theoretical inference-performance models, based directly on video evidence from two local-inference benchmarks:

1. **Video 1:** Apple M5 Ultra (512 GB) running Qwen 3.8 Flash Next  
   *Source:* [Which AI Models Can M5 Ultra Mac Studio Actually Run?](https://www.youtube.com/watch?v=PfSDw9IgdgM) by Forward Pass
2. **Video 2:** NVIDIA RTX 5070 (12 GB) + 64 GB RAM running DeepSeek V4.1 Flash (2-bit)  
   *Source:* [Why 64GB of RAM Now Matters More Than Your GPU for Local AI](https://www.youtube.com/watch?v=3_uVmNjZ1QY) by Lem

---

## Part 1: Apple Silicon M5 Ultra & Qwen 3.8 Flash Next

### 1.1 Overview & Notes Audit

* **Claimed in Notes:**
  * 108 output tokens/sec at 8,192 context tokens.
  * 61 output tokens/sec at 131,072 context tokens.
  * Model predicted: 161.9 tokens/sec and 97.1 tokens/sec, respectively.
* **Audit Verdict:** **Partially Inaccurate / Conflated Context.**
  * The **108 tok/s** figure is confirmed at `[00:03:00]`, but the video attributes this to an external benchmark from **MacStories**. Crucially, the video **does not state** that this was measured at an 8,192 context length.
  * The **61 tok/s** figure is confirmed at `[00:05:07]`, but the context is explicitly cited as **128K (128,000)** tokens, not $2^{17} = 131,072$ tokens.
  * Installed unified memory is **512 GB** (not 256 GB).

---

### 1.2 Timestamped Evidence Table: M5 Ultra

| Parameter / Question | Measured Fact / Video Evidence | Status / Citation |
| :--- | :--- | :--- |
| **Speed Measurement 1** | **~108 output tokens/second** (attributed to MacStories benchmark on M5 Ultra; compared to ~70 tok/s on M3 Ultra). | `[00:03:00]` |
| **Speed Measurement 2** | **~61 output tokens/second** (generation speed under extended context). | `[00:05:07]` |
| **Hardware Platform** | **Mac Studio**, Apple Silicon **M5 Ultra**, **80-core GPU**, **512 GB Unified Memory**, with theoretical bandwidth of **$1.2\text{ TB/s}$**. | `[00:00:08]`, `[00:00:38]` |
| **Model Name & Architecture** | **Qwen 3.8 Flash Next**; 125 billion total parameters; Mixture of Experts (MoE) with ~6 billion active parameters per token. | `[00:03:00]` |
| **Quantization Format** | **Not stated** for this specific MacStories run. (General 4-bit quantization discussion occurs at `[00:01:23]`, but exact quant format and file size are omitted). | Not stated |
| **Runtime / Backend** | **Not stated** (e.g., MLX, llama.cpp, or native Metal framework not identified). | Not stated |
| **Context Length (Baseline)** | **Not stated**. The 8,192 token figure in user notes is an ungrounded assumption. | Not stated |
| **Context Length (Degraded)** | Explicitly stated as **128,000 ("128K") context tokens** (introduced alongside a *"128,000 token prompt"*). Not 131,072. | `[00:05:02]`, `[00:05:07]` |
| **Metric Classification** | **Output / decode speed** (tokens generated per second). | `[00:03:00]`, `[00:05:07]` |
| **Concurrency & Scheduling** | **Not stated** (assumes single-stream sequential generation). | Not stated |
| **Caching / Speculative Decoding** | **Not stated**. | Not stated |

---

### 1.3 Discrepancy & Bottleneck Analysis (Predicted: 161.9 / 97.1 vs. Actual: 108 / 61)

#### Explicit Explanations in Video
1. **Rule of Bandwidth Ceiling vs. Runtime Reality:** At `[00:01:34]`, Rule 2 is introduced: theoretical speed cannot exceed memory bandwidth divided by active bytes read per token ($B_{\text{mem}} / W_{\text{active}}$). At `[00:02:26]`, the narrator observes that real-world inference engines achieve only a fraction of this roofline:
   > *"Real engines reach a third to a half of the ceiling, so expect around 26 [for GLM 5.3]."*
2. **Context Memory Degradation:** At `[00:05:07]`, the video explicitly attributes the reduction from 108 to 61 tokens/sec to the overhead of long-context generation (*"generation slows as the context grows"*).

#### Engineering Hypotheses
* **Non-Expert Overhead:** In MoE models like Qwen 3.8 Flash Next, decoding requires streaming not only the ~6B active expert weights, but also non-sparse base layers (embeddings, shared self-attention projections, RMSNorm, and routing gate logits). A formula dividing $1.2\text{ TB/s}$ solely by active MoE weights underestimates total bytes transferred per token.
* **Bus Saturation at Batch Size 1:** Achieving $1.2\text{ TB/s}$ on Apple Silicon requires fully saturating memory channels with parallel GPU compute. Autoregressive single-token decoding is memory-latency bound; Metal/MLX kernels typically operate at 65%–75% bus efficiency.
  $$\text{Expected TPS} \approx 161.9 \times 0.70 \approx 113.3\text{ tok/s} \quad (\approx 108\text{ observed})$$
* **KV-Cache Attention Bandwidth at 128K Context:** At 128,000 tokens, reading the Key-Value (KV) cache from unified memory requires significant memory bandwidth on every single token step, competing directly with weight streaming.

---

## Part 2: NVIDIA RTX 5070 & DeepSeek V4.1 Flash (2-bit)

### 2.1 Overview & Notes Audit

* **Claimed in Notes:**
  * 4.3–4.9 output tokens/sec on an RTX 5070 + 64 GB RAM system running "DeepSeek Flash at INT2".
  * Stored midpoint: 4.6 tokens/sec.
  * Context assumed: 8,192 tokens.
  * Theoretical GPU-bandwidth prediction: 68 tokens/sec.
* **Audit Verdict:** **Severe Modeling Category Error & Erroneous Context.**
  * The speed range of **4.3–4.9 tok/s** is confirmed at `[00:04:02]` for RAM-cached experts, with an overall typical steady-state average of **~4.7 tok/s** (`[00:05:15]`).
  * The **8,192-token context is completely ungrounded**. The video decode test was an informal query about a "side project" yielding a 500-token response. The number 8,000 appears strictly as the prompt length for a separate prefill benchmark (`[00:06:21]`) and Strata's default test harness setting (`[00:05:48]`).
  * The **68 tokens/sec theoretical prediction failed** because it erroneously assumed all weights reside in local GPU VRAM. The model is 257 GB; the RTX 5070 has only 12 GB VRAM. The true bottleneck is host system RAM and NVMe SSD streaming across the PCIe bus.

---

### 2.2 Timestamped Evidence Table: RTX 5070

| Parameter / Question | Measured Fact / Video Evidence | Status / Citation |
| :--- | :--- | :--- |
| **Speed Measurement (RAM Cache)** | **4.3–4.9 tokens/second** (active experts cached in 64 GB system RAM). Midpoint cited as **~4.7 tok/s**. | `[00:04:02]`, `[00:05:15]` |
| **Speed Measurement (SSD Streaming)** | **1.8–2.2 tokens/second** (reading un-cached experts directly from NVMe SSD). | `[00:04:12]` |
| **Prefill Speed** | **231 tokens/second** measured at an **8,000-token prompt**. | `[00:06:21]` |
| **Cross-Platform Baseline** | **8–10 tokens/second** achieved on an **RTX 3060 (12 GB) + 46 GB RAM running Linux**. | `[00:05:24]` |
| **Speculative Decoding Baseline** | **~40 tokens/second** achieved on an **RTX 4090 + 128 GB RAM** with speculative drafting enabled. | `[00:09:56]` |
| **Model Name & Parameters** | **DeepSeek V4.1 Flash**; 763 billion total parameters; MoE architecture with 384 experts per layer; activates 6 experts per token (or 5 in default fast mode). Includes a separate 111 GB "engram" lookup table. | `[00:00:07]`, `[00:03:01]`, `[00:03:33]` |
| **Quantization Format** | Stated strictly as **"two-bit"** files created by **ISTA D-Lab** (total footprint: 257 GB on disk). The explicit label "INT2" is **not stated**. | `[00:04:56]`, `[00:07:03]` |
| **GPU Model & VRAM** | NVIDIA GeForce **RTX 5070**, **12 GB VRAM**. | `[00:00:20]`, `[00:02:15]` |
| **CPU Specifications** | **Not stated**. | Not stated |
| **System RAM Capacity & Speed** | **64 GB** capacity. Channels, bus frequency, and DDR standard (e.g., DDR5 MT/s) are **not stated**. | `[00:00:21]`, `[00:04:02]` |
| **Storage Specifications** | **NVMe SSD**; minimum 257 GB free space required. PCIe generation and IOPS ratings are **not stated**. | `[00:06:57]`, `[00:07:05]` |
| **Operating System** | **Windows** (RTX 5070 test); **Linux** (RTX 3060 comparative test). | `[00:05:30]` |
| **Runtime / Backend** | **Strata** (open-source runtime, ported from **Project Maya**). | `[00:00:16]`, `[00:05:01]` |
| **Routing / Engine Settings** | Default "fast mode" activates 5 out of 6 experts per token for GPUs $\le$16 GB VRAM. Full quality mode routes all 6 experts. | `[00:08:08]` |
| **Prompt Length & Context** | Prompt length for the 4.3–4.9 tok/s run is **not stated** (informal test query). The 8,192 context in notes is **erroneous**. Context architecture limits: Strata default test = 8,000; native context = 1,000,000; thinking budget = up to 32,768. | `[00:01:38]`, `[00:05:48]`, `[00:08:34]` |
| **Metric Classification** | Single-request **decode / token generation speed** (output throughput). | `[00:04:08]` |
| **Operational State** | **Warm steady-state** with hot experts pinned in system RAM. | `[00:04:08]` |

---

### 2.3 Memory Tiering & Offload Architecture

The video demonstrates that 12 GB GPUs cannot run DeepSeek V4.1 Flash via standard VRAM offload. The Strata runtime implements a three-tier hierarchical memory model:

```
┌─────────────────────────────────────────────────────────────┐
│ 1. GPU VRAM (12 GB)                                         │
│    - Multi-Head Attention layers                            │
│    - Shared dense base layers & RMSNorm                     │
│    - Active KV-Cache buffers                                │
└──────────────────────────────┬──────────────────────────────┘
                               │ PCIe Bus (~20–26 GB/s)
┌──────────────────────────────▼──────────────────────────────┐
│ 2. System RAM (64 GB)                                       │
│    - Dynamic MoE Cache (frequently activated experts)       │
│    - Hit Rate yields: 4.3 – 4.9 tok/s                       │
└──────────────────────────────┬──────────────────────────────┘
                               │ NVMe Random Reads (~1.5–3.0 GB/s)
┌──────────────────────────────▼──────────────────────────────┐
│ 3. NVMe SSD Storage (257 GB total files + 111 GB engram)     │
│    - Inactive / cold experts                                │
│    - Cold Miss yields: 1.8 – 2.2 tok/s                      │
└─────────────────────────────────────────────────────────────┘
```

---

### 2.4 Explaining the 68 TPS vs. 4.6 TPS Discrepancy

#### Measured Facts
1. On identical hardware (RTX 5070 + 64 GB RAM), reading uncached experts from NVMe drops decode speed from **4.3–4.9 tok/s down to 1.8–2.2 tok/s**.
2. An older RTX 3060 (12 GB) under Linux achieved **8–10 tok/s**, beating the RTX 5070 under Windows due to operating system paging/IO scheduling efficiency.
3. The model on disk is 257 GB plus a 111 GB lookup table, whereas the RTX 5070 has only 12 GB of VRAM.

#### Creator's Stated Principles
* *"The RAM is the speed and the drive is the room."* (`[00:04:02]`)
* *"A slow disc slows every word."* (`[00:04:12]`)
* GPU compute and VRAM bandwidth are not the primary bottleneck in this configuration; host system memory capacity and drive latency dictate token throughput.

#### Mathematical Derivation of the Error
* **The Invalid Assumption:** The 68 tokens/sec model evaluated the roofline equation against the RTX 5070's internal GDDR7 bandwidth:
  $$B_{\text{VRAM}} \approx 672\text{ GB/s}$$
  Assuming $\approx 10\text{–}15\text{ billion}$ active parameters at 2 bits ($0.25\text{ bytes/param} \approx 2.5\text{–}3.75\text{ GB}$ of weights) plus dense layers:
  $$\text{Theoretical TPS}_{\text{invalid}} = \frac{672\text{ GB/s}}{\sim 10\text{ GB active data}} \approx 67.2\text{ tok/s}$$
* **The Reality (PCIe & Host RAM Bottleneck):** Because the weights do not reside in VRAM, active experts must cross the PCIe 4.0 x16 host interface on every token generation step. Real-world PCIe host-to-device transfer throughput tops out at $20\text{–}26\text{ GB/s}$:
  $$\text{Real Decode TPS}_{\text{RAM}} = \frac{B_{\text{PCIe}}}{W_{\text{active}}} \approx \frac{22\text{ GB/s}}{4.5\text{–}5.0\text{ GB}} \approx 4.4\text{–}4.8\text{ tok/s}$$
  This matches the measured **4.3–4.9 tok/s**.
* **SSD Miss Penalty:** When active experts are not present in the 64 GB RAM cache, random reads from the NVMe drive ($1.5\text{–}2.5\text{ GB/s}$) throttle decode performance down to:
  $$\text{Real Decode TPS}_{\text{SSD}} \approx \frac{2.0\text{ GB/s}}{\sim 1.0\text{ GB disk reads}} \approx 2.0\text{ tok/s}$$
  This matches the measured **1.8–2.2 tok/s**.

---

## Part 3: Comparative Summary & Modeling Guidance

### 3.1 Side-by-Side Architectural Comparison

| Dimension | Video 1: Apple M5 Ultra | Video 2: NVIDIA RTX 5070 + 64 GB RAM |
| :--- | :--- | :--- |
| **Model** | Qwen 3.8 Flash Next (125B total / ~6B active) | DeepSeek V4.1 Flash (763B total / 5–6 active experts) |
| **Quantization** | Unspecified 4-bit class | "Two-bit" (ISTA D-Lab, 257 GB on disk) |
| **Memory Architecture** | Unified Memory Architecture (UMA) | Segmented Heterogeneous: VRAM $\rightarrow$ System RAM $\rightarrow$ NVMe |
| **Total Addressable Memory** | 512 GB unified pool | 12 GB VRAM + 64 GB Host RAM + NVMe |
| **Primary Data Bus** | Unified Memory Bus ($1.2\text{ TB/s}$) | PCIe Bus ($20\text{–}26\text{ GB/s}$) & NVMe interface |
| **Decode Throughput** | **108 tok/s** (baseline) / **61 tok/s** (128K context) | **4.3–4.9 tok/s** (RAM cache) / **1.8–2.2 tok/s** (SSD) |
| **Model Fit Status** | Entire model resides in unified memory pool | Model exceeds total RAM + VRAM; requires storage paging |
| **Primary Bottleneck** | Metal bus saturation & long-context KV reads | PCIe host-to-device bandwidth & NVMe random access |

---

### 3.2 Analytical Takeaways for Performance Formula Calibration

1. **Gate by Memory Residency:** Never use GPU memory bandwidth ($B_{\text{VRAM}}$) in the denominator if total model footprint $M_{\text{total}} > VRAM$. The roofline must bind to the lowest tier holding active parameters:
   $$B_{\text{eff}} = \begin{cases} B_{\text{VRAM}}, & \text{if } M_{\text{total}} \le \text{VRAM} \\ B_{\text{PCIe}}, & \text{if } \text{VRAM} < M_{\text{active}} \le \text{RAM} \\ B_{\text{NVMe}}, & \text{if active weights stream from SSD} \end{cases}$$
2. **Account for Cache Hit Rates in Hybrid Offload:** For systems using dynamic MoE offloaders (such as Strata), decode latency is governed by the expert cache hit rate $h$:
   $$T_{\text{token}} = \frac{1}{\text{TPS}} = \frac{W_{\text{active, VRAM}}}{B_{\text{VRAM}}} + \frac{W_{\text{active, RAM}}}{B_{\text{PCIe}}} + \frac{(1 - h) \cdot W_{\text{active, SSD}}}{B_{\text{NVMe}}} + T_{\text{compute}}$$
3. **Context Length Adjustments:** Memory bandwidth available for model weights decays as context length increases due to KV-cache read volume. At 128,000 tokens on UMA systems, expect throughput drops of 40%–45% relative to short-prompt baselines.