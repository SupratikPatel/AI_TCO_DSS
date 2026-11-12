# Primary Benchmark Evidence Report: Apple Mac Studio M5 Ultra (512 GB Unified Memory)

**Generated:** November 12, 2026  
**Companion Structured Data:** `m5_ultra_512gb_benchmark_evidence.json`  
**Scope & Verification Policy:** Strict primary-source verification of Apple's Mac Studio with **M5 Ultra and 512 GB unified memory**, auditing the lead video ([`6UjDw-2s4ik`](https://www.youtube.com/watch?v=6UjDw-2s4ik)) and related YouTube videos, extracting verified 512 GB M5 Ultra runs from [`oMLX` Community Telemetry](https://omlx.ai/benchmarks/performance), [Apple Machine Learning Research](https://machinelearning.apple.com/research/mlx-distributed-inference), and [`r/MacStudio`](https://www.reddit.com/r/MacStudio/comments/1xrxm5f/m5_ultra_512gb_benchmarks/), and documenting low-bit `Qwen3.8-Flash-Next` quality evaluations. Results from **M5 Ultra 256 GB**, **M3 Ultra 512 GB**, and **M5 Max 128 GB** are strictly segregated and never substituted for M5 Ultra 512 GB.

---

## 1. Official Apple Hardware Verification (`M5 Ultra + 512 GB`)

### 1.1 Official Apple Configuration & Specification Sources
* **Apple US Store (512 GB / 1 TB CTO):** [Buy Mac Studio, M5 Ultra Chip, 36-core CPU, 80-core GPU, 512GB memory, 1TB storage](https://www.apple.com/shop/buy-mac/mac-studio/m5-ultra-chip-36-core-cpu-80-core-gpu-512gb-memory-1tb-storage)
* **Apple US Store (512 GB / 16 TB CTO):** [Buy Mac Studio, M5 Ultra Chip, 36-core CPU, 80-core GPU, 512GB memory, 16TB storage](https://www.apple.com/shop/buy-mac/mac-studio/m5-ultra-chip-36-core-cpu-80-core-gpu-512gb-memory-16tb-storage)
* **Apple Newsroom Launch Release (Aug 25, 2026):** [Apple introduces new Mac Studio with M5 Max and M5 Ultra](https://www.apple.com/newsroom/2026/08/apple-introduces-new-mac-studio-with-m5-max-and-m5-ultra/)
* **Apple Product Page:** [Mac Studio — Apple](https://www.apple.com/mac-studio/)
* **Independent Store Audit (Nov 4, 2026):** [VDF.AI — Mac Studio M5 Ultra for Local LLMs: Price, Fit and Speed](https://vdf.ai/blog/mac-studio-m5-ultra-local-llm/)

### 1.2 Verified Hardware Architecture & Dated Pricing Table (Checked Nov 4–12, 2026)

| Specification Field | Verified Value (M5 Ultra 512 GB Tier) | Source / Notes |
| :--- | :--- | :--- |
| **SoC & Die Layout** | **Apple M5 Ultra** (4-die UltraFusion package joining two dual-die M5 Max packages) | [Apple Newsroom](https://www.apple.com/newsroom/2026/08/apple-introduces-new-mac-studio-with-m5-max-and-m5-ultra/) |
| **CPU Cores** | **36-core CPU** (`12` super cores + `24` performance cores; `0` efficiency cores) | Required for 512 GB; 30C/64G binned chip caps at 256 GB ([Apple Store](https://www.apple.com/shop/buy-mac/mac-studio/m5-ultra-chip-36-core-cpu-80-core-gpu-512gb-memory-1tb-storage)) |
| **GPU Cores & AI Units** | **80-core GPU** with a dedicated **Neural Accelerator** (matrix-multiply unit) in every GPU core + **32-core Neural Engine** | [Apple Newsroom](https://www.apple.com/newsroom/2026/08/apple-introduces-new-mac-studio-with-m5-max-and-m5-ultra/) |
| **Unified Memory** | **512 GB** unified memory | Default macOS GPU wired limit is ~75–80% (`384.0–409.6 GB`), raisable via `sudo sysctl iogpu.wired_limit_mb=<MB>` to `~472–500 GB` |
| **Memory Bandwidth** | **1.2 TB/s** (`1,228.8 GB/s` theoretical; +50% over M3 Ultra `819.2 GB/s`) | Measured on 80c M5 Ultra: **`1,039 GB/s`** GPU microbenchmark / **`583.6 GB/s`** CPU STREAM Triad ([Alex Ziskind `c_58D7ixOQI` @ `07:12–07:58`](https://www.youtube.com/watch?v=c_58D7ixOQI)) |
| **SSD Capacity & Prices (US Store)** | **1 TB (Included):** `$22,299.00` (`$1,858.25/mo` × 12 mo)<br>**2 TB (+`$500`):** `$22,799.00`<br>**4 TB (+`$1,500`):** `$23,799.00`<br>**8 TB (+`$3,500`):** `$25,799.00`<br>**16 TB (+`$7,500`):** `$29,799.00` | [Apple Store 1 TB](https://www.apple.com/shop/buy-mac/mac-studio/m5-ultra-chip-36-core-cpu-80-core-gpu-512gb-memory-1tb-storage) / [Apple Store 16 TB](https://www.apple.com/shop/buy-mac/mac-studio/m5-ultra-chip-36-core-cpu-80-core-gpu-512gb-memory-16tb-storage). Memory upgrade alone is **`+$15,500`** over 96 GB (`$6,799`) and **`+$11,500`** (`~$44.92/GB`) over 256 GB (`$10,799`) on the same 36C/80G chip. |
| **Release & Delivery Dates** | Announced **Aug 25, 2026**; 96/256 GB shipped **Sep 22, 2026**; 512 GB orderable **Oct 28, 2026**; first customer units delivered **Nov 9, 2026** | Confirmed by [Apple Newsroom](https://www.apple.com/newsroom/2026/08/apple-introduces-new-mac-studio-with-m5-max-and-m5-ultra/), [VDF.AI](https://vdf.ai/blog/mac-studio-m5-ultra-local-llm/), and Nov 9 customer deliveries on [`r/MacStudio`](https://www.reddit.com/r/MacStudio/comments/1xrjynp/mac_studio_m5u_36c_80g_512gb_4tb_arrived_5_days/) |
| **Power & Interconnect** | **480 W** max continuous rating (`385 W` max system load; `~300 W` measured in 65K single-node MLX inference); **6× Thunderbolt 5** (`120 Gb/s`, RDMA via `rdma_ctl enable` in macOS Recovery) | [Apple ML Research](https://machinelearning.apple.com/research/mlx-distributed-inference) / [VDF.AI](https://vdf.ai/blog/mac-studio-m5-ultra-local-llm/) |

---

## 2. Audit of Lead YouTube Video (`6UjDw-2s4ik`) and Related Videos

**Critical Finding:** Neither [`6UjDw-2s4ik`](https://www.youtube.com/watch?v=6UjDw-2s4ik) (published Nov 5, 2026) nor its sister TCO videos ([`PlOI37B3Ntg`](https://www.youtube.com/watch?v=PlOI37B3Ntg), [`WXr7597eHrQ`](https://www.youtube.com/watch?v=WXr7597eHrQ), [`GiACVxCWJtU`](https://www.youtube.com/watch?v=GiACVxCWJtU), published Oct 29–30, 2026) possessed a physical 512 GB M5 Ultra unit, because customer deliveries did not begin until **November 9, 2026**. As [`WXr7597eHrQ`](https://www.youtube.com/watch?v=WXr7597eHrQ) explicitly states at `00:26`: *"we don't have one... so this trip is built from the people who have tested the M5 Ultra so far: reviewers, owners, and Apple's own numbers."*

### 2.1 Traceability Audit of Every Figure in `https://www.youtube.com/watch?v=6UjDw-2s4ik`

| Timestamp in `6UjDw-2s4ik` | Quoted Figure / Claim | True Hardware & Primary Source | Classification |
| :--- | :--- | :--- | :--- |
| `01:44`, `04:26–05:15` | `$22,299` (36C CPU, 80C GPU, 512 GB RAM, 1 TB SSD); `+$15,500` over 96 GB; `+$11,500` (`~$45/GB`) over 256 GB | **M5 Ultra 512 GB** — [Apple US Store](https://www.apple.com/shop/buy-mac/mac-studio/m5-ultra-chip-36-core-cpu-80-core-gpu-512gb-memory-1tb-storage) | **Verified Spec** |
| `06:24–06:43`, `11:14` | Default GPU cap `~384 GB`; terminal command raises cap up to `~500 GB` (leaving ~6–12 GB for macOS) | **macOS Unified Memory Setting** (`sudo sysctl iogpu.wired_limit_mb=N`) | **Verified OS Setting** |
| `06:50–07:15`, `11:08–11:50` | 4-bit sizes: `GLM-5.3` = `418 GB` (fits 512 GB), `DeepSeek-V4.1-Flash` = `432 GB` (fits 512 GB), `Muse Spark Open` = `533 GB` (needs 2× Studio), `Kimi K3.1 Pro` = `1,561 GB` (needs 4× 512 GB Studio = `$89,196` + 6× `$69` TB5 cables = `$89,610`) | **Hugging Face Checkpoint Sizes** — Verified in [VDF.AI](https://vdf.ai/blog/mac-studio-m5-ultra-local-llm/) (note: `mlx-community` 4-bit `GLM-5.3` is `418.3 GB`; Unsloth `UD-IQ4_XS` GGUF is `365.3 GB`; `DeepSeek-V4.1-Flash-1017` `oQ3e` is `381.2 GB`) | **Model Footprint Fact** |
| `08:06–10:55` | **Terminal Bench 4.0** (Claude Code harness): `Claude Opus 5.5` = `64.85%` (`66.4%` Moonshot table / `63.6%` AA); `GLM-5.3` = `41.82%`; `Kimi K3.1 Pro` (2.8T/A104B native 4-bit) = `65.7%` (Moonshot) / `67.2%` (Artificial Analysis) | **Cloud / Full-Weight Server Runs** — Terminal Bench 4.0 Leaderboard & Artificial Analysis | **Quality Benchmark (Server Weights)** |
| `13:30–13:38` | "`oMLX` developer shipped a build claiming **44% faster prefill** for `DeepSeek V4.1 Flash` on an M5 Ultra" | **M5 Ultra (256 GB)** — [oMLX v0.7.4.dev1 Release Notes (#5031)](https://github.com/jundot/omlx/releases): `DeepSeek-V4.1-Flash oQ2e-mtp` 32K prompt prefill rose from `2,631` to **`3,779 tok/s` (+44%)**, and 256K prompt from `2,604` to **`3,718 tok/s` (+43%)** | **Verified Secondary Citation** |
| `14:01–14:15` | Apple ran `Muse Spark Open` (816B total / 42B active, NVFP4) across **4× M5 Ultra machines** and recorded **`36.73 tok/s`** | **4× M5 Ultra 512 GB Cluster (Tensor Parallel, 8,192 ctx, 128 gen)** — [Apple ML Research (Oct 15, 2026)](https://machinelearning.apple.com/research/mlx-distributed-inference) | **Verified Primary Measurement (4× 512 GB Cluster)** |
| `14:16–14:30` | Scaling `36.73 tok/s` by active parameters (`42B` vs `104B`) yields **`~15 tok/s`** for `Kimi K3.1 Pro` on 4× M5 Ultra 512 GB | **Creator Estimate** (`36.73 × 42 / 104 = 14.83 tok/s`) | **Estimate (Unmeasured)** |
| `14:31–15:48` | Alex Ziskind ran `Kimi K3` on **4× 512 GB M3 Ultra** Mac Studios and measured **`14.7 tok/s`** decode and **`238 tok/s`** prefill (`~2 min` TTFT on 30K Claude Code prompt; `4 hours` app build vs `15 min` cloud) | **4× M3 Ultra 512 GB Cluster** (NOT M5 Ultra) — [Alex Ziskind `ujs0_cpAnaw`](https://www.youtube.com/watch?v=ujs0_cpAnaw) | **M3 Ultra 512 GB Measurement (Not M5 Ultra)** |
| `15:54–16:25` | Spicy Neuron (6 months on **512 GB M3 Ultra** behind Claude Code) reported 1 concurrent user limit; Ziskind tested **256 GB M5 Ultra** with multiple users and throughput peaked at 4 users and fell off at 8 | **M3 Ultra 512 GB** & **M5 Ultra 256 GB** — [Alex Ziskind `_yrw6c5gw3E` @ `15:15–16:30`](https://www.youtube.com/watch?v=_yrw6c5gw3E) | **M3U 512 GB & M5U 256 GB Measurements** |
| `18:21–18:28` | `DeepSeek-V4.1-Flash` model family gets **`53 tok/s`** on an M5 Ultra (measured by Ziskind) | **M5 Ultra 256 GB (80c)** running `DeepSeek-V4-Flash` 284B 4-bit in MLX — [Alex Ziskind `c_58D7ixOQI` @ `08:18`](https://www.youtube.com/watch?v=c_58D7ixOQI) & [`_yrw6c5gw3E` @ `07:14`](https://www.youtube.com/watch?v=_yrw6c5gw3E) | **M5 Ultra 256 GB Measurement** |

---

## 3. Verified Primary Benchmark Evidence on M5 Ultra 512 GB

### 3.1 Concise Summary Table of Verified M5 Ultra 512 GB Runs

| Run ID | Source & Date | Hardware Verified | Model & Exact Quantization | Runtime & Settings | Actual Input / Output Tokens | Prefill (`PP tok/s`) | TTFT (`s`) | Decode (`TG tok/s`) | Peak Memory / Power |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`M5U512-OMLX-01`** | [oMLX Leaderboard Page 2](https://omlx.ai/benchmarks/performance?cursor=WyJwZXJmb3JtYW5jZTpoaWRlX3NwZWNwcmVmaWxsPTEiLCIyMDI2LTExLTEyIDA4OjI5OjUxIiw2MTQ5NTAsMiwyLDEwXQ%3D%3D&hide_specprefill=1) (`2026-11-12`, rows #13–16) | **M5 Ultra (80c) · 512 GB** (`✓` telemetry) | `Qwen3.8-Flash-Next-oQ6e-mtp` (`6bit` mixed MLX OptiQ) | `oMLX`, Lightning MTP ON, `b=1`, uncached | `1,024` / `128`<br>`8,192` / `128`<br>`32,768` / `128`<br>**`131,072` / `128`** | `2,521`<br>`4,903`<br>`4,847`<br>**`4,640`** | `~0.41` (est)<br>`~1.67` (est)<br>`~6.76` (est)<br>**`~28.25` (est)** | `128.7`<br>`113.2`<br>`144.9`<br>**`102.3`** | `~157.15 GB` footprint (`~150.5 GB` active @ 128k per matched `oQ6e` run) |
| **`M5U512-OMLX-02`** | [oMLX `3u2u1f9j` (128k)](https://omlx.ai/benchmarks/performance/3u2u1f9j) & [`odblvo21` (195k)](https://omlx.ai/benchmarks/performance/odblvo21) (`2026-11-12`) | **M5 Ultra (80c) · 512.00 GB** (`macOS 27.2`) | `gpt-oss-120b-MLX-8bit` (`8bit` MLX) | `oMLX v0.7.4.dev1`, MTP OFF, FP16 KV, `temp=1`, `b=1`, Python code | **`131,072` / `128`**<br>`195,000` / `128` | **`1,839`**<br>`1,533` | **`71.288`**<br>`130.446` | **`50.4`**<br>`42.4` | **`121.62 GB`** active (`133.72 GB` wired / `512.00 GB` RAM) @ 128k;<br>`124.50 GB` active @ 195k |
| **`M5U512-OMLX-03`** | [oMLX Leaderboard Page 2](https://omlx.ai/benchmarks/performance?cursor=WyJwZXJmb3JtYW5jZTpoaWRlX3NwZWNwcmVmaWxsPTEiLCIyMDI2LTExLTA5IDE2OjQxOjQzIiw2MTAxNjIsMiwyLDEwXQ%3D%3D&hide_specprefill=1) (`2026-11-09`, rows #13–18, 20) | **M5 Ultra (80c) · 512 GB** (`✓` telemetry) | `DeepSeek-V4.1-Flash-oQ4e-mtp` (`oQ4e` 4-bit, fully in RAM) | `oMLX`, Lightning MTP ON, `b=1`, uncached | `1,024` (cold) / `128`<br>`1,024` (warm) / `128`<br>`4,096` / `128`<br>`8,192` / `128`<br>`16,384` / `128`<br>`32,768` / `128`<br>`65,536` / `128` | `293.5`<br>`932.7`<br>`1,308`<br>`1,239`<br>`1,291`<br>`1,300`<br>`1,280` | `~3.49` (est)<br>`~1.10` (est)<br>`~3.13` (est)<br>`~6.61` (est)<br>`~12.69` (est)<br>`~25.21` (est)<br>`~51.20` (est) | `29.5`<br>`66.1`<br>`67.5`<br>`69.4`<br>`79.2`<br>`81.9`<br>`82.0` | `~292–406 GB` footprint (requires 512 GB tier without SSD offload) |
| **`M5U512-APPLE-04A`** | [Apple ML Research](https://machinelearning.apple.com/research/mlx-distributed-inference) (`2026-10-15`) | **1× M5 Ultra (80c) · 512 GB** (and 2×/4× TB5 RDMA cluster) | `Qwen/Qwen3.8-27B` (Dense 27B, native `BF16`) | `mlx_lm.benchmark` (`MLX v0.30.1+`, `macOS 26.2+`), MTP OFF, `-b 1` | `8,192` / `128`<br>(`65,536` / `128` also run) | `~1,998` (8K, 1×) | **`4.1`** (1×, 8K)<br>`4.1` (2× Pipe, 8K)<br>`3.1` (2× TP, 8K)<br>`1.7` (4× TP, 8K)<br>`24.5` (2× Pipe, 65K)<br>`29.0` (2× TP, 65K) | **`19.69`** (1×)<br>`19.44` (2× Pipe)<br>`33.27` (2× TP)<br>`50.89` (4× TP) | Up to **`68 GB`** RAM & **`~300 W`** peak power at 65,536 ctx |
| **`M5U512-APPLE-04B`** | [Apple ML Research](https://machinelearning.apple.com/research/mlx-distributed-inference) (`2026-10-15`) | **1× M5 Ultra (80c) · 512 GB** (and 2×/4× TB5 RDMA cluster) | `mistralai/Mistral-Medium-3.5-128B` (Dense 128B, native `FP8`) | `mlx_lm.benchmark` (`MLX v0.30.1+`, `macOS 26.2+`), MTP OFF, `-b 1` | `8,192` / `128`<br>`65,536` / `128` | `~333` (8K, 1×)<br>`~240` (65K, 1×) | **`24.6`** (1×, 8K)<br>`24.5` (2× Pipe, 8K)<br>`14.4` (2× TP, 8K)<br>`7.5` (4× TP, 8K)<br>**`~273`** (1×, 65K)<br>**`~154`** (2× TP, 65K) | **`7.70`** (1×)<br>`7.70` (2× Pipe)<br>`13.69` (2× TP)<br>`23.37` (4× TP) | Up to **`158 GB`** RAM & **`~300 W`** peak power at 65,536 ctx |
| **`M5U512-APPLE-04C`** | [Apple ML Research](https://machinelearning.apple.com/research/mlx-distributed-inference) (`2026-10-15`) | **2× & 4× M5 Ultra (80c) · 512 GB** RDMA cluster | `meta-models/Muse-Spark-Open-816B-A42B-NVFP4` (`493 GB` weights) | `mlx.launch --backend jaccl` (`MLX_METAL_FAST_SYNCH=1`), `-b 1` | `8,192` / `128`<br>`65,536` / `128` | `~1,706` (8K, 4× TP)<br>`~1,614` (65K, 4× TP 2-cable) | **OOM on 1× 512 GB**<br>`8.4` (2× Pipe, 8K)<br>`8.2` (2× TP, 8K)<br>`4.8` (4× TP, 8K)<br>**`40.6`** (4× TP, 65K, 2 cables)<br>**`50.5`** (4× TP, 65K, 1 cable) | **OOM on 1×**<br>`15.74` (2× Pipe)<br>`24.99` (2× TP)<br>**`36.73`** (4× TP) | `493 GB` weights + buffers exceed 1× 512 GB; fits 2× or 4× 512 GB |
| **`M5U512-REDDIT-05`** | [Reddit `r/MacStudio` (`1xrxm5f`)](https://www.reddit.com/r/MacStudio/comments/1xrxm5f/m5_ultra_512gb_benchmarks/) (`2026-11-09`) | **M5 Ultra 512 GB** (X operator screenshots) | `DeepSeek` language model (`Q6` / high precision) & second 1M-ctx model | `vllm` (per thread comments), uncached fresh prompt, `c=1` | `16,384` and **`262,144` (`256K`)** | `~2,184` (est @ 256K) | **`~120.0`** (`~2 min` at fresh 256K context, no prefix cache) | `UNKNOWN` (inside image attachment) | `UNKNOWN` (inside image attachment) |

---

## 4. Assessment of Priority Workloads (`3A`, `3B`, `3C`) and Non-Substitutable Reference Runs

### 4.1 Workload 3A: Single Request at ~131,072 Actual Input Tokens
* **Measured on M5 Ultra 512 GB:**
  1. **`Qwen3.8-Flash-Next-oQ6e-mtp` (6-bit, Lightning MTP ON):** At **`128k` (`131,072` actual input tokens, `128` generated tokens)** on `M5 Ultra (80c) · 512 GB`, [`oMLX` leaderboard row #14](https://omlx.ai/benchmarks/performance?cursor=WyJwZXJmb3JtYW5jZTpoaWRlX3NwZWNwcmVmaWxsPTEiLCIyMDI2LTExLTEyIDA4OjI5OjUxIiw2MTQ5NTAsMiwyLDEwXQ%3D%3D&hide_specprefill=1) recorded **`PP = 4,640 tok/s`** and **`TG = 102.3 tok/s`** (implied TTFT **`~28.25 s`**).
  2. **`gpt-oss-120b-MLX-8bit` (8-bit, MTP OFF):** At **`128k` (`131,072` actual input tokens, `128` generated tokens)** on `M5 Ultra (80c) · 512.00 GB` ([`oMLX 3u2u1f9j`](https://omlx.ai/benchmarks/performance/3u2u1f9j)), `oMLX v0.7.4.dev1` recorded **`PP = 1,839 tok/s`**, **`TTFT = 71.288 s` (`71,288 ms`)**, **`TG = 50.4 tok/s`**, and **`Peak MLX Active = 121.62 GB`** (`133.72 GB` system wired peak out of `512.00 GB`).
* **Comparison on M5 Ultra 80c 256 GB (Same 36C/80G Die & 1.2 TB/s Bandwidth, Strictly Segregated as 256 GB):**
  * Because the 256 GB 80-core M5 Ultra has the exact same 36-core CPU, 80-core GPU, and 1.2 TB/s memory bandwidth as the 512 GB M5 Ultra, models under ~210 GB that fit in 256 GB execute on identical silicon:
    * **`Qwen3.8-Flash-Next-oQ4e-mtp` (4-bit, Lightning MTP ON, INT8 Activation Prefill ON)** on `M5 Ultra (80c) · 256 GB` ([`oMLX 9aa0q4b3`](https://omlx.ai/benchmarks/performance/9aa0q4b3), `2026-11-11`): At **`128k` (`131,072` input, `128` output)**, **`PP = 5,992 tok/s`**, **`TTFT = 21.873 s` (`21,873 ms`)**, **`TG = 95.5 tok/s`**, **`Peak mem = 109.3 GB`** (`117.27 GB` wired peak). Full sweep (`1k / 4k / 8k / 16k / 32k / 64k / 128k / 195k`): `PP = 587.0 / 1,726 / 3,617 / 5,767 / 6,494 / 6,209 / 5,992 / 5,395 tok/s`; `TG = 61.7 / 79.0 / 63.8 / 95.2 / 87.0 / 68.3 / 95.5 / 89.6 tok/s`.
    * **`Qwen3.8-Flash-Next-oQ6e-mtp` (6-bit, Lightning MTP ON, INT8 Activation Prefill ON)** on `M5 Ultra (80c) · 256 GB` ([`oMLX u6ocbrlv`](https://omlx.ai/benchmarks/performance/u6ocbrlv), `2026-11-07`): At **`128k`**, **`PP = 4,984 tok/s`**, **`TG = 106.7 tok/s`**, **`Peak mem = 150.5 GB`**.
    * **`Qwen3.8-Flash-Next-oQ4e` (4-bit, MTP OFF, 512 generated tokens)** on `M5 Ultra (80c) · 256 GB` ([MacStories Review](https://www.macstories.net/stories/m5-ultra-mac-studio-review-the-dream-mac-for-local-ai-agents/), `oMLX v0.7.0.dev2`, single run per context size with **512 generated tokens**, prior to Oct/Nov INT8 prefill patches): At **`128K`**, **`TTFT = 49.2 s`**, **`TG = 60.6 tok/s`**; at **`256K`**, **`TTFT = 101.5 s`**, **`TG = 74.7 tok/s`**.
    * **`DeepSeek-V4.1-Flash-1017-Abliterated` (`oQ2.5e-mtp`, Engram SSD offload ON, CED + INT8 prefill ON)** on `1× M5 Ultra (64c) · 256 GB` vs `2× M5 Ultra (64c) · 256 GB` Dual-TB5 RDMA ([Reddit `u/lgrimani` `1xo8k9j`](https://www.reddit.com/r/MacStudio/comments/1xo8k9j/dual_m5u_256gb_dual_tb5_omlx_074dev1_dsv41/), `oMLX v0.7.4.dev1`, `128` generated tokens): At **`pp131073/tg128` (`131,073` actual input tokens)**:
      * **1× M5 Ultra 256 GB:** `TTFT = 67.046 s` (`67,045.7 ms`), `PP = 1,955.0 tok/s`, `TG = 81.3 tok/s` (`TPOT = 12.39 ms`), `E2E = 68.625 s`, `Peak MLX = 210.72 GB`.
      * **2× M5 Ultra 256 GB (Dual RDMA Tensor Parallel):** `PP = 3,494 tok/s`, `TG = 60.0 tok/s`, `E2E = 39.65 s`.

### 4.2 Workload 3B: Five Simultaneous Requests Each at ~131,072 Actual Input Tokens
* **Status on M5 Ultra 512 GB:** **`UNKNOWN` (Unmeasured across all public sources as of November 12, 2026).**
* **Why 512 GB Capacity Alone Does Not Establish 5× 131K Performance:**
  * While `Qwen3.8-Flash-Next` at 2-bit (`66.4–78.9 GB`), 3-bit (`75.8–90.0 GB`), or 4-bit (`93.7–111.5 GB`) plus five `131,072`-token KV caches (`~27 KB/tok × 655,360 tokens ≈ 17.7 GB` in FP16) easily fits inside 512 GB unified memory (`<140 GB` total footprint), **prefill is compute-bound on the 80 GPU cores** and **batched decode is memory-bandwidth-bound on the same 1.2 TB/s bus as the 96 GB and 256 GB M5 Ultra**.
* **Closest Measured Multi-Stream / Long-Context Benchmarks (Strictly Segregated by Hardware):**
  1. **M3 Ultra 512 GB (8 Concurrent Streams at 81K and 160K Context — [oMLX v0.7.3 Release Notes](https://github.com/jundot/omlx/releases)):**
     * `8 Lightning MTP streams at 81K context` (`Qwen3.8-Flash-Next oQ4e`): Peak memory **`161.1 GiB`** (down from `248.0 GiB` after in-place KV cache batch update fixes `#4916/#4936/#4954/#4971`), aggregate decode **`241.1 tok/s`** (`~30.1 tok/s` per stream). Per-request TTFT: `UNKNOWN`.
     * `8 agent conversations from 160K context` (`MTP off`): Peak memory **`153.0 GiB`** (down from `185.3 GiB`), aggregate output **`42.4 tok/s`** (`~5.3 tok/s` per stream). Per-request TTFT: `UNKNOWN`.
  2. **M5 Ultra (12 Concurrent Requests on `DeepSeek-V4.1-Flash` — [oMLX v0.7.3 Release Notes](https://github.com/jundot/omlx/releases)):**
     * `12 concurrent requests` (context length unstated): Aggregate decode rose from `56.3` to **`125.7 tok/s`** (`~10.48 tok/s` per stream) after fused decode kernel fix `#4989`.
  3. **M5 Ultra 80c 256 GB (1, 4, and 8 Concurrent Users — [Alex Ziskind `_yrw6c5gw3E` @ `15:15–16:30`](https://www.youtube.com/watch?v=_yrw6c5gw3E)):**
     * `DeepSeek-V4-Flash` (short prompt): Peaks at **4 concurrent users (`66 tok/s` aggregate)** and drops at **8 concurrent users (`46 tok/s` aggregate)**.
     * `DeepSeek-V4-Flash` (**8 concurrent users, each with 8,000 tokens of chat history**): Each user waited **`>60 seconds` TTFT**, then generated at **`~5 tok/s` per user** (`~11 tok/s` effective aggregate throughput across the test window, vs `24 s` TTFT and `25 tok/s` aggregate on 2× DGX Spark).
     * `Qwen3.8-Flash-Next` (8 concurrent users, short prompt): **`66 tok/s` aggregate** (`llama.cpp`) / **`70 tok/s` aggregate** (`oMLX`) vs **`120 tok/s` aggregate** on 2× DGX Spark.
  4. **M5 Ultra 256 GB Continuous Batching at `pp1024/tg128` (`oMLX v0.7.3 / v0.7.4.dev1`):**
     * `Qwen3.8-Flash-Next-oQ4e-mtp` ([`9aa0q4b3`](https://omlx.ai/benchmarks/performance/9aa0q4b3), 80c): `1× = 61.7 tok/s`, `2× = 108.7 tok/s` (`1.76×`), `4× = 213.2 tok/s` (`3.46×`).
     * `Qwen3.8-Flash-Next-oQ6e-mtp` ([`u6ocbrlv`](https://omlx.ai/benchmarks/performance/u6ocbrlv), 80c): `1× = 148.6 tok/s`, `2× = 304.5 tok/s` (`2.05×`), `4× = 715.2 tok/s` (`4.81×`).
     * `DeepSeek-V4.1-Flash-1017-oQ2e-mtp` ([`7hdr933y`](https://omlx.ai/benchmarks/performance/7hdr933y), 80c): `1× = 62.3 tok/s`, `2× = 74.4 tok/s` (`1.19×`), `4× = 91.5 tok/s` (`1.47×`), `8× = 162.9 tok/s` (`2.61×`).
     * `DeepSeek-V4.1-Flash-1017-Abliterated oQ2.5e-mtp` ([Reddit `u/lgrimani` `1xo8k9j`](https://www.reddit.com/r/MacStudio/comments/1xo8k9j/dual_m5u_256gb_dual_tb5_omlx_074dev1_dsv41/), 64c):
       * `2× batch` (`pp1024/tg128`): `TTFT = 2.897 s`, `PP = 449.1 tok/s` (`224.6 tok/s/req`), `Aggregate TG = 118.2 tok/s`, `E2E = 6.726 s` (vs `29.0 tok/s` aggregate / `11.02 s` E2E on 2× M5U RDMA).
       * `4× batch` (`pp1024/tg128`): `TTFT = 5.705 s`, `PP = 397.1 tok/s` (`99.3 tok/s/req`), `Aggregate TG = 220.0 tok/s`, `E2E = 12.643 s` (vs `28.5 tok/s` aggregate / `20.17 s` E2E on 2× M5U RDMA).

### 4.3 Workload 3C: Eight Retained Agent Sessions
* **On M5 Ultra 512 GB:** **`UNKNOWN` (Unmeasured).**
* **On M3 Ultra 512 GB (Reference Only):** Verified in [oMLX v0.7.3 Release Notes](https://github.com/jundot/omlx/releases) (`8 Lightning MTP streams at 81K` on `Qwen3.8-Flash-Next oQ4e` = `161.1 GiB` resident peak, `241.1 tok/s` aggregate decode; `8 agent conversations from 160K` with `MTP off` = `153.0 GiB` resident peak, `42.4 tok/s` aggregate output).

---

## 5. Quality & Reliability of Exact Low-Bit `Qwen3.8-Flash-Next` Artifacts

### 5.1 ISTA-DASLab `Qwen3.8-Flash-Next-GSQ-RCO-GGUF` (Mixed Per-Tensor Precision + Fixed `IQ4_NL` N-Gram Table)
**Source:** [ISTA-DASLab/Qwen3.8-Flash-Next-GSQ-RCO-GGUF Model Card](https://huggingface.co/ISTA-DASLab/Qwen3.8-Flash-Next-GSQ-RCO-GGUF)  
*Architecture Note:* Every variant ships as two GGUF shards. Shard 2 (`per_layer_token_embd`, 51.2B parameters) is held at fixed `IQ4_NL` (`4.50 bpw`, `28.8 GB`) across all builds and can be memory-mapped on SSD (`-lm mmap --lazy-mode on`) or kept in RAM. Shard 1 holds the transformer weights quantized via GSQ + RCO per-tensor optimization.

| Exact Artifact Identifier | Transformer Avg `bpw` | Shard 1 (Weights) | Shard 2 (N-Gram `IQ4_NL`) | Total Download | 5-Task Zero-Shot Avg (`%`) | `AIME25` (`%`) | `GPQA-Diamond` (`%`) | `LiveCodeBench v6` (`%`) | 3-Task Avg (`%`) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `Qwen/Qwen3.8-Flash-Next` (`BF16` Base) | `16.00` | `354.0 GB` | (included) | `354.0 GB` | `76.94` | `100.00` | `91.92` | **`87.43`** | **`93.12`** |
| `ISTA-DASLab/Qwen3.8-Flash-Next-GSQ-RCO-GGUF:Q2_0` | `2.40` | `37.6 GB` | `28.8 GB` | `66.4 GB` | `78.00` | `96.67` | `89.39` | **`81.14`** (`-6.29 pp`) | **`89.07`** |
| `ISTA-DASLab/Qwen3.8-Flash-Next-GSQ-RCO-GGUF:IQ2_XS` | `2.50` | `39.2 GB` | `28.8 GB` | `68.0 GB` | `77.16` | `96.67` | `87.37` | **`83.43`** (`-4.00 pp`) | **`89.16`** |
| `ISTA-DASLab/Qwen3.8-Flash-Next-GSQ-RCO-GGUF:IQ3_XXS` | `3.00` | `47.0 GB` | `28.8 GB` | `75.8 GB` | `77.23` | `100.00` | `91.41` | **`86.29`** (`-1.14 pp`) | **`92.57`** |
| `ISTA-DASLab/Qwen3.8-Flash-Next-GSQ-RCO-GGUF:IQ3_S` | `3.50` | `54.8 GB` | `28.8 GB` | `83.6 GB` | `UNKNOWN` | `100.00` | `92.93` | **`86.86`** (`-0.57 pp`) | **`93.26`** |

### 5.2 oMLX Community Intelligence Benchmarks (With Downloadable `.json.gz` Question Logs)

| Exact Artifact & Repo | Benchmark & Version | Sample / Total | Pass Count & Score | Hardware & Runtime | Thinking & Sampling Settings | Documented Failure Breakdown & Raw Log Link |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `ISTA-DASLab/Qwen3.8-Flash-Next-GSQ-RCO-Q2_0` | **MMLU-Pro** | `1,000` / `12,032` (`seed=42`, stratified) | **`714 / 1,000` (`71.4%`)** | M5 Max (40c) 64 GB, `oMLX v0.7.2` (`14.6m`) | Deterministic, `temp=1`, `top_p=0.95`, `top_k=20`, **Thinking: No**, `mtp=false`, `batch=4` | `286` failures; worst in **engineering (`44/81 = 54.3%`)**, **law (`57/92 = 62.0%`)**, **physics (`71/108 = 65.7%`)**; best in CS (`31/34 = 91.2%`). ([oMLX `mkzszvig`](https://omlx.ai/benchmarks/intelligence/mkzszvig)) |
| `ISTA-DASLab/Qwen3.8-Flash-Next-GSQ-RCO-Q2_0` | **GSM8K** | `1,319` / `1,319` (Full) | **`1,238 / 1,319` (`93.9%`)** | M5 Max (40c) 64 GB, `oMLX v0.7.2` (`12.1m`) | Deterministic, `temp=1`, `top_p=0.95`, `top_k=20`, **Thinking: No**, `mtp=false`, `batch=4` | `81` failed math problems; downloadable 250 KB `.json.gz` log. ([oMLX `ybmeme01`](https://omlx.ai/benchmarks/intelligence/ybmeme01)) |
| `Jundot/Qwen3.8-Flash-Next-oQ4e-mtp` (4-bit) | **HumanEval** | `164` / `164` (Full) | **`132 / 164` (`80.5%`)** | **M5 Ultra (64c) 256 GB**, `oMLX v0.7.0` (`18.5m`) | Deterministic, **Thinking: Yes**, `force_sampling=false`, `mtp=false`, `batch=4` | `32` failed coding tasks when thinking tokens were unconstrained without an explicit high `max_tokens` ceiling. ([oMLX `qvlxvz1i`](https://omlx.ai/benchmarks/intelligence/qvlxvz1i)) |
| `Qwen3.8-Flash-Next-oQ4e-MTP-128k` (4-bit) | **HumanEval** | `164` / `164` (Full) | **`148 / 164` (`90.2%`)** (`93.3–95.7%` in [`yjfg8r9i`](https://omlx.ai/benchmarks/intelligence/yjfg8r9i)/[`yywmmv20`](https://omlx.ai/benchmarks/intelligence/yywmmv20)) | M5 Max (40c) 128 GB, `oMLX v0.6.4` (`1.4h`) | Deterministic, **Thinking: Yes**, `max_tokens=32768`, `max_context=131072`, `mtp=true`, `batch=8` | `16` failed coding tasks; raising `max_tokens` to `32,768` recovered +9.7 to +15.2 pp over `qvlxvz1i`. ([oMLX `6b3p2k87`](https://omlx.ai/benchmarks/intelligence/6b3p2k87)) |
| `Qwen3.8-Flash-Next-oQ6e-mtp` (6-bit) | **ARC-C** | `100` / `1,172` (`seed=42`) | **`96 / 100` (`96.0%`)** | **M5 Ultra (64c) 256 GB**, `oMLX v0.7.1rc1` (`1.8m`) | Deterministic, `batch=4` | `4` failed questions. ([oMLX `m92jl8y8`](https://omlx.ai/benchmarks/intelligence/m92jl8y8)) |

### 5.3 Unsloth Dynamic v3.0 / v3.1 GGUF Quality, Agentic Benchmarks & Tool-Call Failure Analysis
**Sources:** [Unsloth Qwen3.8-Flash-Next Guide](https://unsloth.ai/docs/models/qwen3.8-next), [Unsloth Dynamic 3.1 GGUFs](https://unsloth.ai/docs/basics/dynamic-3.0-ggufs/dynamic-3.1-ggufs), and [Unsloth Dynamic 3.0 GGUFs](https://unsloth.ai/docs/basics/dynamic-3.0-ggufs)

* **Evaluation Harness & Settings (`26.2B` total evaluation tokens):**
  * **`DeepSWE v1.1` (`18.1B` tokens):** `113` tasks × `3` passes minimum, `mini-swe-agent` (Pier's default `mini.yaml` with native bash tool calls), `500` step limit, `30 s` command timeout, `512K` context window (`256K` non-YaRN), `65,536` max tokens per reply, `temperature=1.0`, `top_p=0.95`, `preserve_thinking=True`, `reasoning_effort=50` (`xhigh`).
  * **`Terminal-Bench 2.1` (`5.2B` tokens):** `82` validated tasks (7 oracle-unsolvable tasks excluded out of 89) × `3` attempts per task, `mini-swe-agent 2.4.6` with native tool calls, `150` step limit, `temperature=1.0`, `top_p=0.95`, `512K` context, `65,536` max tokens per reply, `reasoning_effort=50`.
  * **`Divergence-300 @32`:** `300` unseen held-out prompts from `Terminal-Bench 2.1`, `DeepSWE`, `Harbor`, `MathArena 2025-26`, and long-document prompts, comparing 32-token greedy argmax trajectories against `BF16`.

| Unsloth Artifact (`unsloth/Qwen3.8-Flash-Next-GGUF`) | File Size (`GB`, incl. `28.8 GB` `IQ4_NL` N-Gram Shard) | Top-1 Token Agreement (`%`) | Mean KLD | `99.9%` KLD | Agentic Coding & Tool-Calling Notes |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`UD-IQ1_S`** (Dynamic v3.1) | `72.5 GB` (`66.4 GB` in v3.1) | `77.325%` | `0.396070` | `7.2126` | Scores **`54.0%` on `DeepSWE v1.1`** (vs `58.7%` BF16) and **`68.3%` on `Terminal-Bench 2.1`** in v3.1, but Unsloth warns `<UD-Q2_K_XL` drops to `<8–10%` on `Divergence-300 @32`. |
| **`UD-IQ1_M`** | `74.5 GB` (`68.0 GB` in v3.1) | `79.691%` | `0.314739` | `6.1965` | Requires thinking mode ON and `presence_penalty >= 1.5` to prevent infinite loops. |
| **`UD-Q2_K_XL`** | `78.9 GB` (`79.6 GB` in v3.1) | `82.715%` | `0.224607` | `4.9121` | **Minimum recommended Unsloth threshold for agentic tool use** (`~25%` exact 32-token trajectory match on `Divergence-300 @32`). |
| **`UD-IQ3_XXS`** | `82.0 GB` (`83.6 GB` in v3.1) | `85.414%` | `0.165120` | `4.0375` | Matches `91 GB` RAM tier with MTP head (`+1.91–2.79 GB`). |
| **`UD-Q3_K_XL`** | `90.0 GB` (`89.5 GB` in v3.1) | `88.315%` | `0.106504` | `3.0538` | Strong 3-bit operating point for 128 GB+ unified memory. |
| **`UD-IQ4_XS`** | `93.7 GB` | `89.554%` | `0.083630` | `2.3677` | Fits 128 GB M5 Max with 262K context (`106 GB` wired peak in Heretik run). |
| **`UD-Q4_K_XL`** | `111.3 GB` | `92.255%` | `0.046893` | `1.5468` | Standard 4-bit reference (`92.3%` top-1 agreement, `0.0469` mean KLD). |
| **`UD-Q5_K_XL`** | `158.3 GB` | `93.680%` | `0.030415` | `1.0036` | Near-lossless (`103 tok/s` on M5 Ultra 256 GB in Strata). |
| **`UD-Q6_K_XL`** | `169.2 GB` | `94.089%` | `UNKNOWN` | `UNKNOWN` | Highest GGUF precision before `Q8_0` (`192 GB`) and `BF16` (`354 GB`). |

* **Sushi Engine `Tool-eval-bench 3.0` (100 Multi-Step Agentic Tool Calls — [Sushi GitHub](https://github.com/beamivalice/sushi)):**
  * `Qwen3.8-Flash-Next-Sushi-STQ-2.75bpw` (`44.9 GiB` weights): **`94 / 100` (`94.0%`)**
  * `Qwen3.8-Flash-Next-Sushi-4bpw` (`63.9 GiB` weights): **`90 / 100` (`90.0%`)**

---

## 6. Unresolved Gaps & Contradictions

1. **Five Simultaneous Requests at ~131,072 Actual Input Tokens on M5 Ultra 512 GB (Workload 3B):** Remains **unmeasured (`UNKNOWN`)** across all public sources as of November 12, 2026. The closest empirical proofs are `oMLX v0.7.3`'s 8-stream tests at `81K` (`241.1 tok/s` aggregate, MTP ON) and `160K` (`42.4 tok/s` aggregate, MTP OFF) on **M3 Ultra 512 GB**, and Alex Ziskind's 8-user test at `8K` history on **M5 Ultra 256 GB** (`>60 s` TTFT, `~5 tok/s` per user).
2. **Low-Bit (2-bit / 3-bit) `Qwen3.8-Flash-Next` on M5 Ultra 512 GB:** Because 512 GB M5 Ultra buyers purchase the tier specifically to hold 300B–750B models (`DeepSeek-V4.1-Flash oQ4e`, `GLM-5.3`) or higher-bit builds (`Qwen3.8-Flash-Next oQ6e-mtp` / `oQ8e-mtp`), no 512 GB M5 Ultra owner has uploaded a 2-bit or 3-bit `Qwen3.8-Flash-Next` run to `oMLX` yet (only `oQ6e-mtp` has been uploaded on M5 Ultra 512 GB).
3. **Single-Node vs Dual-Node RDMA Contradiction on `oMLX` vs Apple `mlx_lm.benchmark`:** Apple's Oct 15 post ([`mlx-distributed-inference`](https://machinelearning.apple.com/research/mlx-distributed-inference)) showed `1.69×–1.78×` decode scaling on dense models (`Qwen3.8-27B` and `Mistral-Medium-3.5-128B`) using `mlx.launch --backend jaccl` at `b=1`, whereas independent operator [`u/lgrimani`](https://www.reddit.com/r/MacStudio/comments/1xo8k9j/dual_m5u_256gb_dual_tb5_omlx_074dev1_dsv41/) found that on sparse MoE `DeepSeek-V4.1-Flash-1017` (`oQ2.5e-mtp`) in `oMLX v0.7.4.dev1`, **1× M5 Ultra beat 2× M5 Ultra RDMA on decode at every context length from 1K to 200K** (`81.3` vs `60.0 tok/s` at 128K) and on 2×/4× continuous batching (`220.0` vs `28.5 tok/s` at `4×`), because `oMLX`'s custom single-node `CED`/`INT8` and fused MoE kernels were not natively active on the tensor-parallel path.
