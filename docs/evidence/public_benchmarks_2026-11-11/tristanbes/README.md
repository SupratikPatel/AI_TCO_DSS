---
license: cc-by-4.0
pretty_name: M5 Ultra LLM speed (MLX vs llama.cpp)
tags:
- benchmark
- apple-silicon
- mlx
- llama.cpp
- gguf
configs:
- config_name: default
  data_files: results.jsonl
---

# M5 Ultra LLM speed: MLX vs llama.cpp

Measured token speeds for popular open models on a **Mac Studio M5 Ultra**, running each model in both MLX and llama.cpp. Every speed here was measured (TTFT and GB × decode are derived from them), and every model file is pinned to a commit so you can rerun it.

## Hardware

- Apple M5 Ultra, 36-core CPU: 12 super cores and 24 performance cores (`sysctl`: `hw.perflevel0` "Super", 12 logical CPUs; `hw.perflevel1` "Performance", 24).
- 80-core GPU.
- 256 GB unified memory.
- Memory bandwidth 1.2 TB/s: Apple's stated peak from its [tech specs](https://support.apple.com/en-us/128107), not a figure measured here.

## Results

Tokens per second, mean ± standard deviation of 3 trials. Prefill is reading a 512- or 4096-token prompt; decode is generating 128 tokens with that prompt already in the KV cache (the "Decode depth" column gives the depth actually used). Decode 4096 also gives the median of the 3 trials ("med"). GB is the weight size on disk.

| Model | Runtime | Quant | GB | Prefill 512 | Prefill 4096 | Decode 512 | Decode 4096 | Decode depth | GB × decode ¹ |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| Humanizer 12B | MLX ³ | 8-bit (own conversion of jialinyyzz/humanizer) | 12.7 | 2,679 | 3,431 | 67.4 | 64.4 | 512 / 4096 | 853 GB/s |
| Humanizer 12B | llama.cpp -ub 2048 | Q8_0 | 12.7 | 2,835 ± 3 | 2,984 ± 16 | 63.5 ± 0.3 | 59.7 ± 1.7 (med 60.1) | 512 / 4096 | 804 GB/s |
| Qwen3.8 27B | MLX ³ | 4-bit | 16.1 | 1,499 | 1,866 | 54.7 | 53.6 | 512 / 4096 | 878 GB/s |
| Qwen3.8 27B | llama.cpp -ub 2048 | UD-Q4_K_M | 16.5 | 1,120 ± 2 | 1,300 ± 3 | 47.7 ± 0.1 | 46.9 ± 0.4 (med 47.1) | 512 / 4096 | 786 GB/s |
| gpt-oss 20B | MLX ³ | MXFP4-Q8 | 12.1 | 7,009 | 11,190 | 172.7 | 168.5 | 512 / 4096 | 2,086 GB/s |
| gpt-oss 20B | llama.cpp -ub 2048 | MXFP4 | 12.1 | 6,597 ± 27 | 7,203 ± 25 | 201.8 ± 3.4 | 193.3 ± 9.1 (med 198.3) | 512 / 4096 | 2,444 GB/s |
| Qwen3.6 35B-A3B | MLX ³ | 4-bit | 20.4 | 5,584 | 9,725 | 145.8 | 144.3 | 512 / 4096 | 2,975 GB/s |
| Qwen3.6 35B-A3B | llama.cpp -ub 2048 | UD-Q4_K_M | 22.1 | 4,877 ± 12 | 6,073 ± 18 | 136.1 ± 2.3 | 131.7 ± 5.3 (med 132.0) | 512 / 4096 | 3,012 GB/s |
| Gemma 4 31B | MLX ³ | 4-bit | 18.4 | 1,224 | 1,406 | 43.8 | 39.3 | 512 / 4096 | 807 GB/s |
| Gemma 4 31B | llama.cpp -ub 2048 | Q4_K_M | 18.3 | 1,084 ± 2 | 1,171 ± 2 | 43.0 ± 0.1 | 39.6 ± 0.5 (med 39.7) | 512 / 4096 | 789 GB/s |
| Devstral Small 2 24B | MLX ³ | 4-bit | 15.1 | 1,746 | 2,086 | 62.9 | 60.1 | 512 / 4096 | 950 GB/s |
| Devstral Small 2 24B | llama.cpp -ub 2048 | Q4_K_M | 14.3 | 1,491 ± 5 | 1,613 ± 4 | 59.8 ± 0.4 | 56.8 ± 0.8 (med 57.3) | 512 / 4096 | 858 GB/s |
| Flint 40B-A2.5B | MLX | int4 (official) | 22.6 | 5,368 ± 57 | 9,095 ± 101 | 137.9 ± 2.9 | 140.9 ± 2.6 (med 141.5) | 512 / 4096 | 3,112 GB/s |
| Flint 40B-A2.5B | llama.cpp -ub 2048 | UD-Q4_K_XL | 25.1 | 4,678 ± 36 | 6,692 ± 33 | 117.7 ± 1.1 | 111.2 ± 6.1 (med 114.0) | 512 / 4096 | 2,949 GB/s |
| Nanbeige4.3 33B | MLX | 4-bit | 18.6 | 1,249 ± 2 | 1,502 ± 13 | 51.4 ± 0.1 | 49.0 ± 0.1 (med 49.0) | 512 / 4096 | 958 GB/s |
| Nanbeige4.3 33B | llama.cpp -ub 2048 | Q4_K_M | 20.8 | 1,143 ± 2 | 1,119 ± 5 | 44.8 ± 0.3 | 42.0 ± 0.4 (med 41.8) | 512 / 4096 | 931 GB/s |
| Mistral-Large-4-1T-A52B | llama.cpp -ub 2048 | UD-IQ1_S | 233.0 | 355 ± 0 | 224 ± 1 | 21.5 ± 0.0 | 20.0 ± 0.0 (med 20.0) | 512 / 4096 | 5,005 GB/s |

¹ Weight size on disk × decode tok/s at the 512-token prompt. For a dense model it approximates the weight bandwidth used (M5 Ultra: 1.2 TB/s, Apple's stated peak). For MoE models (Flint 40B-A2.5B, Qwen3.6 35B-A3B, gpt-oss 20B, Mistral-Large-4-1T-A52B) each token reads only the active experts, so it is not a physical bandwidth, only a size-normalised figure.

³ v1 MLX rows (2026-10-23, mlx-lm 0.32.2): mean of 3 trials, no standard deviation or per-trial values stored. Decode is measured right after the prompt (depth = prompt length), like the other MLX rows. GB was measured on 2026-10-26 from the same files.

Other settings, left out of the table (same models, tok/s, mean of 3 trials): **llama-bench defaults (-ub 512), decode depth 0**: Humanizer 12B p512 prefill 2,817, decode 64.0, Humanizer 12B p4096 prefill 2,677, decode 64.0, Qwen3.8 27B p512 prefill 1,119, decode 48.2, Qwen3.8 27B p4096 prefill 1,101, decode 48.2, gpt-oss 20B p512 prefill 6,493, decode 200.0, gpt-oss 20B p4096 prefill 6,174, decode 200.0, Qwen3.6 35B-A3B p512 prefill 4,889, decode 134.5, Qwen3.6 35B-A3B p4096 prefill 4,646, decode 134.5, Gemma 4 31B p512 prefill 1,069, decode 43.2, Gemma 4 31B p4096 prefill 1,015, decode 43.2, Devstral Small 2 24B p512 prefill 1,469, decode 59.7, Devstral Small 2 24B p4096 prefill 1,411, decode 59.7, Flint 40B-A2.5B p512 prefill 4,682, decode 118.9, Flint 40B-A2.5B p4096 prefill 4,452, decode 118.9, Nanbeige4.3 33B p512 prefill 1,132, decode 44.7, Nanbeige4.3 33B p4096 prefill 1,049, decode 44.7; **superseded by rerun 2026-10-26 15:31 CET (same settings)**: Flint 40B-A2.5B p512 prefill 4,717, decode 118.9, Flint 40B-A2.5B p4096 prefill 6,705, decode 113.3; **mlx_lm.benchmark --prefill-step-size 512 (default 2048)**: Flint 40B-A2.5B p4096 prefill 5,956, decode 139.3, Nanbeige4.3 33B p4096 prefill 1,356, decode 49.1.

![Decode tok/s at a 4096-token context, MLX vs llama.cpp](charts/1_hero_decode_4k.png)

*MLX generates faster on 6 of 8 models, but llama.cpp wins gpt-oss 20B*

![Prefill tok/s for a 4096-token prompt](charts/2_prefill_4k.png)

*Prompt processing: MLX is 1.15–1.6× faster on all 8 models*

![Decode adjusted for weight size](charts/3_fair_size_adjusted.png)

*Adjusted for file size, MLX's decode lead shrinks to 11% or less*

![Summary table](charts/4_summary_table.png)

*M5 Ultra: MLX vs llama.cpp on 8 local models*

![Headline result, square format](charts/5_hero_square.png)

*MLX decodes faster on 6 of 8 models; llama.cpp wins gpt-oss 20B*

**All llama.cpp rows use the matched settings (2026-10-26).** The MLX rows of Flint 40B-A2.5B and Nanbeige4.3 33B are from the same day. The MLX rows of the six other models are v1 runs from 2026-10-23 (mlx-lm 0.32.2, same `mlx_lm.benchmark` settings, no standard deviation stored). The earlier llama.cpp runs with llama-bench's defaults are kept in the footnote.

## Mistral Large 4 ("Le Chonk"), 1T parameters

Measured on 2026-10-30, the day after the weights were released. Mistral Large 4 is a 1-trillion-parameter MoE (128 experts, 4 active + 1 shared, ~52B active parameters per token, MLA attention).

- **Quant:** [unsloth UD-IQ1_S](https://huggingface.co/unsloth/Mistral-Large-4-1T-A52B-GGUF) (233 GB, ~1.8 bits per weight on average), revision `1eb4373`. It is the only published quant that fits in 256 GB: the smallest MLX build (mlx-community 2-bit) is 338 GB, so there is no MLX row. Expect a quality loss compared with the full model; this section measures speed only.
- **Runtime:** llama.cpp b12015 (`a34de8618`); Mistral Large 4 support landed in [#31376](https://github.com/ggml-org/llama.cpp/pull/31376) (b11999). An earlier run on b11999 gave the same decode speed (21.7 / 20.2 tok/s) and 4% lower prefill at 512 tokens (339 tok/s); its rows are in `runs/2026-10-30/b11999-mistral-large-4-rows.jsonl`.
- **Memory:** the GPU wired limit was raised to 240 GiB (`iogpu.wired_limit_mb=245760`). Wired memory peaked at 245.8 GB; swap stayed at 0.7 GB; no thermal warning.

Its llama-bench row is in the results table above. Speculative decoding with the DSpark draft shipped by unsloth (`dspark-Mistral-Large-4-1T-A52B-Q8_0.gguf`, 2.2 GB), measured on `llama-server` with `tools/spec_ab.py`: decode tok/s from the server's own timings, 512 generated tokens (`ignore_eos`), 3 trials per line after a warm-up, `--spec-type draft-dspark --spec-draft-n-max 3`, reasoning effort "low", same server settings (`-c 8192 -np 1 -fa on`) with and without the draft:

| Prompt | Temperature | Baseline | DSpark (3 drafted tokens) | Speed-up | Draft acceptance |
|---|---:|---:|---:|---:|---:|
| code | 0 | 21.6 ± 0.0 | 29.4 ± 0.3 | ×1.36 | 58% |
| prose | 0 | 21.6 ± 0.0 | 27.0 ± 0.1 | ×1.25 | 50% |
| json | 0 | 21.6 ± 0.1 | 35.9 ± 0.1 | ×1.66 | 77% |
| code | 1 | 21.6 ± 0.0 | 31.4 ± 2.4 | ×1.45 | 63% |
| prose | 1 | 21.6 ± 0.0 | 26.3 ± 1.2 | ×1.22 | 48% |
| json | 1 | 21.6 ± 0.0 | 34.9 ± 1.8 | ×1.61 | 74% |

The speed-up depends on how predictable the text is: ×1.6 on JSON, ×1.25 on prose. Unsloth's "about 2×" was not reached here. Rows: `results_spec.jsonl`.

![Mistral Large 4 on a Mac Studio M5 Ultra](charts/10_le_chonk.png)

![Generation speed vs total parameters, every model measured on this Mac](charts/11_le_chonk_scale.png)

*Quants differ (1-bit for the 1T model, 4-bit / 8-bit / MXFP4 for the others), so this shows what runs, not a like-for-like comparison.*

## Quantizations

Matched as closely as the published files allow. They are not identical formats:

| Model | MLX | GGUF (llama.cpp) |
|---|---|---|
| Humanizer 12B | 8-bit affine, group 64 (own conversion) | Q8_0 |
| Qwen3.8 27B | 4-bit affine, group 64 | UD-Q4_K_M (Unsloth dynamic) |
| gpt-oss 20B | MXFP4-Q8 (MXFP4 experts, 8-bit attention) | MXFP4 |
| Qwen3.6 35B-A3B | 4-bit affine, group 64 (8-bit gates) | UD-Q4_K_M (Unsloth dynamic) |
| Gemma 4 31B | 4-bit affine, group 64 | Q4_K_M |
| Devstral Small 2 24B | 4-bit affine, group 64 | Q4_K_M |
| Flint 40B-A2.5B | int4, group 64 (official) | UD-Q4_K_XL (Unsloth dynamic) |
| Nanbeige4.3 33B | 4-bit affine, group 64 | Q4_K_M |

File sizes differ by model, and decode reads the weights once per token, so a larger file decodes slower. Decode at the 512-token prompt (MLX vs llama.cpp, tok/s), and the gap left after adjusting for size ("GB × decode" column):

- Humanizer 12B (dense): same size; MLX +6% (67.4 vs 63.5).
- Qwen3.8 27B (dense): GGUF 2.5% larger; MLX +15% (54.7 vs 47.7), +12% after size adjustment.
- gpt-oss 20B (MoE): same size; llama.cpp +17% (201.8 vs 172.7).
- Qwen3.6 35B-A3B (MoE): GGUF 8.5% larger; MLX +7% (145.8 vs 136.1), a tie after size adjustment: size explains it.
- Gemma 4 31B (dense): same size; near tie, MLX +2% (43.8 vs 43.0), and a tie at depth 4096 (39.3 vs 39.6).
- Devstral Small 2 24B (dense): GGUF 5% smaller, yet MLX +5% (62.9 vs 59.8), +11% after size adjustment.
- Flint 40B-A2.5B (MoE): GGUF 11% larger; MLX +17% (137.9 vs 117.7), +6% after size adjustment.
- Nanbeige4.3 33B (dense): GGUF 12% larger; MLX +15% (51.4 vs 44.8), +3% after size adjustment: size explains most of it.

For the MoE models the size adjustment is only a normalisation, not a bandwidth: each token reads only the active experts (footnote ¹).

## Long context

Same 8 models (tier 0) at contexts from 512 to 128k tokens, with an f16 and an 8-bit KV cache. Tokens per second, mean of 3 trials. The rows, with standard deviations and every trial, are in `results_long.jsonl`.

**Decode** (tok/s, 128 tokens generated with the context already in the KV cache):

| Model | Runtime | KV cache | GB | 512 | 4k | 16k | 32k | 64k | 128k |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| Humanizer 12B | MLX | f16 | 12.7 | 67.9 | 64.3 | 64.4 | 63.1 | 61.7 | 56.8 |
| Humanizer 12B | MLX | 8-bit, g64 | 12.7 | not supported ⁴ | not supported ⁴ | not supported ⁴ | not supported ⁴ | not supported ⁴ | not supported ⁴ |
| Humanizer 12B | llama.cpp | f16 | 12.7 | 64.4 | 60.6 | 58.6 | 55.5 | 49.6 | 40.8 |
| Humanizer 12B | llama.cpp | q8_0 | 12.7 | 56.8 | 52.0 | 50.9 | 48.7 | 41.7 | 32.4 |
| Qwen3.8 27B | MLX | f16 | 16.1 | 54.8 | 54.0 | 51.1 | 48.6 | 43.5 | 37.0 |
| Qwen3.8 27B | MLX | 8-bit, g64 | 16.1 | 54.5 | 53.2 | 49.0 | 44.9 | 37.8 | 28.4 |
| Qwen3.8 27B | llama.cpp | f16 | 16.5 | 48.6 | 47.9 | 45.4 | 42.4 | 37.1 | 30.2 |
| Qwen3.8 27B | llama.cpp | q8_0 | 16.5 | 47.3 | 45.9 | 43.9 | 40.9 | 36.0 | 29.0 |
| gpt-oss 20B | MLX | f16 | 12.1 | 185.4 | 179.9 | 161.3 | 146.4 | 121.4 | 94.7 |
| gpt-oss 20B | MLX | 8-bit, g64 | 12.1 | not supported ⁴ | not supported ⁴ | not supported ⁴ | not supported ⁴ | not supported ⁴ | not supported ⁴ |
| gpt-oss 20B | llama.cpp | f16 | 12.1 | 209.7 | 200.3 | 172.2 | 154.3 | 121.7 | 84.9 |
| gpt-oss 20B | llama.cpp | q8_0 | 12.1 | 192.5 | 179.3 | 169.2 | 150.5 | 123.7 | 89.2 |
| Qwen3.6 35B-A3B | MLX | f16 | 20.4 | 160.1 | 151.6 | 146.4 | 140.9 | 125.0 | 107.4 |
| Qwen3.6 35B-A3B | MLX | 8-bit, g64 | 20.4 | 151.8 | 147.8 | 139.9 | 125.4 | 105.0 | 77.7 |
| Qwen3.6 35B-A3B | llama.cpp | f16 | 22.1 | 143.5 | 141.2 | 133.0 | 120.4 | 105.4 | 84.6 |
| Qwen3.6 35B-A3B | llama.cpp | q8_0 | 22.1 | 135.3 | 134.7 | 125.0 | 115.9 | 99.7 | 79.2 |
| Gemma 4 31B | MLX | f16 | 18.4 | 45.2 | 40.4 | 33.6 | 27.1 | 19.8 | 12.6 |
| Gemma 4 31B | MLX | 8-bit, g64 | 18.4 | not supported ⁴ | not supported ⁴ | not supported ⁴ | not supported ⁴ | not supported ⁴ | not supported ⁴ |
| Gemma 4 31B | llama.cpp | f16 | 18.3 | 43.8 | 41.1 | 38.0 | 34.6 | 29.1 | 21.9 |
| Gemma 4 31B | llama.cpp | q8_0 | 18.3 | 39.7 | 38.0 | 35.0 | 31.0 | 25.2 | 18.1 |
| Devstral Small 2 24B | MLX | f16 | 15.1 | 64.8 | 61.9 | 53.5 | 47.4 | 37.4 | 26.2 |
| Devstral Small 2 24B | MLX | 8-bit, g64 | 15.1 | 60.9 | 58.8 | 52.6 | 46.8 | 37.4 | 27.0 |
| Devstral Small 2 24B | llama.cpp | f16 | 14.3 | 60.4 | 58.1 | 49.7 | 43.3 | 34.1 | 23.0 |
| Devstral Small 2 24B | llama.cpp | q8_0 | 14.3 | 56.4 | 54.9 | 50.5 | 45.1 | 36.9 | 27.1 |
| Flint 40B-A2.5B | MLX | f16 | 22.6 | 146.4 | 132.4 | 135.0 | 120.6 | 114.3 | 92.0 |
| Flint 40B-A2.5B | MLX | 8-bit, g64 | 22.6 | not supported ⁴ | not supported ⁴ | not supported ⁴ | not supported ⁴ | not supported ⁴ | not supported ⁴ |
| Flint 40B-A2.5B | llama.cpp | f16 | 25.1 | 120.4 | 118.1 | 106.2 | 100.5 | 87.6 | 67.4 |
| Flint 40B-A2.5B | llama.cpp | q8_0 | 25.1 | 104.4 | 100.7 | 98.8 | 92.7 | 82.6 | 66.2 |
| Nanbeige4.3 33B | MLX | f16 | 18.6 | 52.2 | 49.9 | 43.5 | 37.7 | 29.5 | 21.5 |
| Nanbeige4.3 33B | MLX | 8-bit, g64 | 18.6 | 48.9 | 46.7 | 40.0 | 33.4 | 25.7 | 17.0 |
| Nanbeige4.3 33B | llama.cpp | f16 | 20.8 | 45.6 | 43.1 | 35.8 | 30.4 | 22.9 | 15.1 |
| Nanbeige4.3 33B | llama.cpp | q8_0 | 20.8 | 42.4 | 41.0 | 35.9 | 30.8 | 24.0 | 16.2 |

**Prefill** (tok/s, reading a prompt of the context length from an empty cache):

| Model | Runtime | KV cache | GB | 512 | 4k | 16k | 32k | 64k | 128k |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| Humanizer 12B | MLX | f16 | 12.7 | 2,710 | 3,430 | 3,349 | 3,064 | 2,673 | 2,071 |
| Humanizer 12B | MLX | 8-bit, g64 | 12.7 | not supported ⁴ | not supported ⁴ | not supported ⁴ | not supported ⁴ | not supported ⁴ | not supported ⁴ |
| Humanizer 12B | llama.cpp | f16 | 12.7 | 2,861 | 3,051 | 2,741 | 2,405 | 1,894 | 1,327 |
| Humanizer 12B | llama.cpp | q8_0 | 12.7 | 2,825 | 3,017 | 2,710 | 2,375 | 1,874 | 1,312 |
| Qwen3.8 27B | MLX | f16 | 16.1 | 1,508 | 1,908 | 1,838 | 1,716 | 1,510 | 1,220 |
| Qwen3.8 27B | MLX | 8-bit, g64 | 16.1 | 1,507 | 1,849 | 1,706 | 1,504 | 1,137 | 733 |
| Qwen3.8 27B | llama.cpp | f16 | 16.5 | 1,127 | 1,323 | 1,234 | 1,125 | 931 | 718 |
| Qwen3.8 27B | llama.cpp | q8_0 | 16.5 | 1,126 | 1,319 | 1,225 | 1,115 | 943 | 719 |
| gpt-oss 20B | MLX | f16 | 12.1 | 7,315 | 11,768 | 10,639 | 9,109 | 7,270 | 5,092 |
| gpt-oss 20B | MLX | 8-bit, g64 | 12.1 | not supported ⁴ | not supported ⁴ | not supported ⁴ | not supported ⁴ | not supported ⁴ | not supported ⁴ |
| gpt-oss 20B | llama.cpp | f16 | 12.1 | 6,569 | 7,242 | 6,005 | 4,681 | 3,346 | 2,105 |
| gpt-oss 20B | llama.cpp | q8_0 | 12.1 | 6,527 | 7,224 | 5,961 | 4,769 | 3,394 | 2,150 |
| Qwen3.6 35B-A3B | MLX | f16 | 20.4 | 5,742 | 9,732 | 9,077 | 7,893 | 6,096 | 4,137 |
| Qwen3.6 35B-A3B | MLX | 8-bit, g64 | 20.4 | 5,768 | 9,449 | 8,049 | 6,379 | 4,138 | 2,361 |
| Qwen3.6 35B-A3B | llama.cpp | f16 | 22.1 | 4,902 | 6,170 | 5,423 | 4,604 | 3,425 | 2,300 |
| Qwen3.6 35B-A3B | llama.cpp | q8_0 | 22.1 | 4,877 | 6,095 | 5,363 | 4,550 | 3,491 | 2,373 |
| Gemma 4 31B | MLX | f16 | 18.4 | 1,276 | 1,470 | 1,373 | 1,257 | 1,068 | 828 |
| Gemma 4 31B | MLX | 8-bit, g64 | 18.4 | not supported ⁴ | not supported ⁴ | not supported ⁴ | not supported ⁴ | not supported ⁴ | not supported ⁴ |
| Gemma 4 31B | llama.cpp | f16 | 18.3 | 1,094 | 1,192 | 1,065 | 928 | 729 | 511 |
| Gemma 4 31B | llama.cpp | q8_0 | 18.3 | 1,083 | 1,173 | 1,054 | 928 | 737 | 519 |
| Devstral Small 2 24B | MLX | f16 | 15.1 | 1,804 | 2,188 | 1,985 | 1,816 | 1,503 | 1,109 |
| Devstral Small 2 24B | MLX | 8-bit, g64 | 15.1 | 1,784 | 1,953 | 1,539 | 1,178 | 732 | 413 |
| Devstral Small 2 24B | llama.cpp | f16 | 14.3 | 1,491 | 1,639 | 1,413 | 1,189 | 905 | 615 |
| Devstral Small 2 24B | llama.cpp | q8_0 | 14.3 | 1,488 | 1,636 | 1,416 | 1,194 | 908 | 613 |
| Flint 40B-A2.5B | MLX | f16 | 22.6 | 5,586 | 9,144 | 8,499 | 7,366 | 5,786 | 4,015 |
| Flint 40B-A2.5B | MLX | 8-bit, g64 | 22.6 | not supported ⁴ | not supported ⁴ | not supported ⁴ | not supported ⁴ | not supported ⁴ | not supported ⁴ |
| Flint 40B-A2.5B | llama.cpp | f16 | 25.1 | 4,745 | 6,846 | 5,606 | 4,460 | 3,158 | 1,984 |
| Flint 40B-A2.5B | llama.cpp | q8_0 | 25.1 | 4,680 | 6,714 | 5,492 | 4,413 | 3,132 | 1,984 |
| Nanbeige4.3 33B | MLX | f16 | 18.6 | 1,275 | 1,545 | 1,392 | 1,179 | 916 | 630 |
| Nanbeige4.3 33B | MLX | 8-bit, g64 | 18.6 | 1,262 | 1,336 | 935 | 655 | 381 | 203 |
| Nanbeige4.3 33B | llama.cpp | f16 | 20.8 | 1,157 | 1,155 | 929 | 736 | 519 | 321 |
| Nanbeige4.3 33B | llama.cpp | q8_0 | 20.8 | 1,112 | 1,145 | 923 | 734 | 519 | 325 |

⁴ not supported (mlx-lm 0.32.2: RotatingKVCache quantization not implemented). These models use sliding-window attention, whose rotating KV cache mlx-lm cannot quantize; the run stops with `NotImplementedError: RotatingKVCache Quantization NYI`. The failed rows stay in `results_long.jsonl` (`error` field) and count in no figure.

GB is the weight size on disk. k = 1024 tokens (128k = 131072).

![Decode tok/s as the context grows](charts/6_long_decode.png)

*At 128K, MLX decodes faster on 7 of 8 models; Gemma 4 is the exception*

![Prefill tok/s as the context grows](charts/7_long_prefill.png)

*Prefill: MLX's lead grows with context, 1.6–2.4× faster at 128K*

![Long-context results table](charts/8_long_table.png)

*Long context on M5 Ultra: speed at 4K, 32K and 128K tokens*

![Effect of a q8_0 KV cache on llama.cpp at 128K](charts/9_kv_q8_effect.png)

*llama.cpp q8_0 KV cache at 128K: 9–34% less memory, same prefill*

### Method (long context)

- **llama.cpp** (llama-bench, same build as the main table): per context N two passes — cold prefill `-p N -n 0`, and work at depth `-p 2048 -n 128 -d N` (decode tok/s with N tokens already in the KV cache, plus a 2048-token prefill on top of the context); `-ngl 99 -fa on -b 2048 -ub 2048 -r 3`; KV cache f16 and q8_0 (`-ctk/-ctv`). The prefill table shows the cold prefill; the 2048-token prefill at depth is in `results_long.jsonl` (`prefill_at_depth_tps`). The raw llama-bench output of every pass is in `runs/2026-10-26/` and `runs/2026-10-27/` (home directory paths replaced by `~`).
- **MLX**: `mlx_lm.benchmark -p N -g 128 -n 3` (decode follows the N-token prompt = decode at depth N), plus `tools/mlx_depth.py` with an 8-bit KV cache (`--kv-bits 8 --kv-group-size 64`).
- **MLX 8-bit KV rows**: measured with `tools/mlx_depth.py` (mlx_lm's `stream_generate` with `kv_bits=8`, `kv_group_size=64`), not with `mlx_lm.benchmark`, so MLX f16 vs MLX 8-bit is not a strict like-for-like comparison. mlx-lm 0.32.2 cannot quantize sliding-window (rotating) KV caches, so Humanizer 12B, gpt-oss 20B, Gemma 4 31B and Flint 40B-A2.5B have no MLX 8-bit rows (footnote ⁴).
- 60 s idle cooldown between passes; contexts 512, 4096, 16384, 32768, 65536, 131072; 8 models, tier 0.
- Run started 2026-10-26 18:30 CET, finished 2026-10-27 08:57 CET.
- TTFT (`ttft_s`) in the llama.cpp rows is an estimate (N / prefill tok/s), not a measurement; `ttft_method` says how each row got it.

## Method

- **MLX**: `mlx_lm.benchmark -p {512,4096} -g 128 -n 3` (default `--prefill-step-size 2048`). Decode runs right after the prompt, so it is measured at depth 512 or 4096. Each row also stores the median, the standard deviation and every trial.
- **llama.cpp**, matched settings: `llama-bench -ngl 99 -fa on -ctk f16 -ctv f16 -b 2048 -ub 2048 -r 3`, Metal, in two passes:
  - prefill: `-p 512,4096 -n 0`. `-ub 2048` matches MLX's prefill step of 2048 tokens.
  - decode: `-p 0 -n 128 -d 0,512,4096`. Each prompt length gets its decode at depth = prompt length, like MLX. Depth 0 is stored as `decode_tps_depth0`.
- llama-bench's defaults (`-ub 512`, decode at depth 0) against MLX's defaults are in the footnote under the table, along with MLX at `--prefill-step-size 512`.
- Flint and Nanbeige were first run by `runs/matched-20261026/run_matched.sh`; its commands, log and raw outputs are published there (`run_matched.sh`, `runs.log`, the raw llama-bench / mlx_lm `*.out` files). The six other models and a rerun of Flint were measured by `bench.py` with the same llama-bench settings (15:21–15:33 CET); the Flint rerun replaces the first matched Flint rows, which stay in the footnote. That rerun's console log (exact llama-bench commands, cooldowns, mean per point) is `runs/matched-20261026/rerun-1521.log`. llama-bench's raw JSONL was not saved for it; the per-trial values of its 14 rows are in `results.jsonl` (`samples_prefill`, `samples_decode`). Home directory paths in the published logs are replaced by `~`.
- Tool versions: llama.cpp 9125a2ebe (b11896) built from source for every llama.cpp row in the table; mlx-lm git 4cfc647 for Flint (support not yet in a release), mlx-lm 0.32.2 for the other MLX rows; mlx 0.32.4.
- A run that failed (`error`) or during which the Mac started to swap (`warning`) stays in `results.jsonl` / `results_long.jsonl` for the record, but counts in no table figure. Rows with a `setting` field were run with non-matched settings; they stay in the file and appear only in the footnote.
- Long-context runs (`bench.py --profile long`) are in `results_long.jsonl` and in the [Long context](#long-context) section, with their own method.

### Sanity check

llama-bench on Llama-2-7B Q4_0 (`ggml-org/Llama-2-7B-GGUF`, rev 8bf9812c) on this Mac at b11896: pp512 5057.44 ± 10.01, tg128 178.92 ± 0.70 tok/s. The M5 Ultra 80-core entry in llama.cpp discussion #4167 (commit c1d0e7a) gives 4944.66 / 179.10. The machine performs as expected.

## Caveats

- `mlx_lm.benchmark`'s `prompt_tps` is timed up to the first generated token, so it includes that token's forward pass and sampling. Its `generation_tps` counts 128 tokens over the time of 127, about +0.8%.
- Both tools use random-token prompts. On MoE models this may route experts differently from real text.
- TTFT (`ttft_s`) is estimated as prompt tokens / prefill tok/s unless `ttft_method` says it was measured.
- 3 trials per point (llama-bench's default is 5).
- llama-bench decode at depth 4096: the first of the 3 repetitions is the slowest on every model of the 15:21 rerun (e.g. Flint 104.1 vs 115.5 / 114.0; gpt-oss 182.8 vs 198.8 / 198.3), which widens the standard deviation. It is not background load: the machine was otherwise idle, swap 0. The median is shown next to the mean for that column.
- Short runs with a fixed 128-token output. They show raw engine speed, not what a long chat feels like, which also depends on the prompt cache and the app.

### Environment

Mac Studio M5 Ultra on AC power. Swap stayed at 0 throughout and macOS recorded no thermal or performance warning. During the first matched pass (Flint and Nanbeige, `run_matched.sh`) the machine was not idle: other user processes were present at times (browser, a Go build and lint, desktop apps), and the Aikido endpoint network-filter proxy was running at 0 to 2.4% CPU, sampled before each run. The 15:21–15:33 CET rerun (the six other models and Flint) ran with the machine otherwise idle: swap 0, no thermal warning, only desktop apps at ≤63% of one core, sampled every 30 s. Model, runtime versions, macOS version, the `bench.py` commit and the date are in every row of `results.jsonl`.

## Reproduce

Build llama.cpp from source at b11803 or later (Flint needs it; b11896 was used), rather than `brew install llama.cpp`.

```bash
git clone https://github.com/ggml-org/llama.cpp && cd llama.cpp
git checkout b11896 && cmake -B build && cmake --build build --target llama-bench -j
export LLAMA_BENCH=$PWD/build/bin/llama-bench
brew install uv
uv run bench.py            # downloads the pinned files into ~/hf-bench, appends to results.jsonl
uv run bench.py --only gemma
uv run bench.py --profile long --tier 3 --only gpt-oss-120b   # long context, appends to results_long.jsonl
```

Add a model by appending to `models.json` (MLX repo and GGUF file, each with its commit).

## Columns of results.jsonl

`model`, `weights` (repo), `revision`, `file`, `quant`, `runtime`, `runtime_version`, `prompt_tokens`, `prefill_tps`, `decode_tps`, `peak_memory_gb`, `generated_tokens`, `trials`, `date`, `chip`, `gpu_cores`, `memory_gb`, `macos`.

Rows written by bench.py v2 (`schema: 2`) also have `kv_type`, `n_ubatch` (llama.cpp), `depth` and `decode_depth` (both = tokens in the KV cache when the measured decode starts), `decode_tps_depth0` (llama.cpp), `size_gb` (weight bytes on disk / 1e9), `size_x_decode_gbps` (= `size_gb` × `decode_tps`), `*_median`, `*_std`, `samples_*`, `ttft_s` with `ttft_method`, thermal, swap and wired-memory state (in `pass_a` / `pass_b` for llama.cpp), `bench_commit`, and `error` or `warning` when a run went wrong. Rows ingested from raw files have `raw_source` and `measured_with`. The v1 MLX rows also have `size_gb` and `size_x_decode_gbps`, added later (`size_source`). A `setting` field marks a run with non-matched settings. `results_custom.jsonl` holds runs with other settings (each labelled in `setting`).

`peak_memory_gb` means two things. For MLX it is the peak reported by mlx-lm (v1 rows: mean over the trials; v2 rows: max). For llama.cpp (v2 rows only) it is the sampled RSS of llama-bench, mmap'd pages included (`peak_memory_method`).

Corrections and requests for models are welcome in the Community tab.
