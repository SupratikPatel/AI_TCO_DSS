---
license: apache-2.0
pretty_name: Smarty Pants Mac Benchmarks
tags:
- mlx
- apple-silicon
- benchmark
- quantization
configs:
- config_name: results
  data_files: results.json
---

# Smarty Pants Mac Benchmarks

Speed and quality for open models on real Apple Silicon Macs, made with our open [model factory](https://github.com/Howcanio/smarty-pants/tree/main/scripts/model-factory). Each section is one model on one Mac. The **bold** row is the base version; the rows marked ↳ are versions we built or tested to make it faster, smaller or smarter, measured the same way on the same Mac.

A version counts as **better** only if it is faster or smaller *and* its answers stay as good, or if its answers get better at the same speed. Everything else is listed anyway, so you can see what did not work.

## Summary

| Model | Mac | Base speed | Best version | Its speed | Its quality |
|---|---|---|---|---|---|
| Qwen3.5-4B (Smarty) | Apple M5 Pro (Mac mini) | 99.7 tok/s, quality 86.5% | base is still best |  |  |
| Qwen3.5-4B (Smarty), GSM8K math | Apple M5 Pro, 64 GB (Mac mini) | 99.7 tok/s, quality 89.0% | base is still best |  |  |
| Qwen3.5-4B (Smarty), draft-ahead decoding | Apple M5 Pro, 64 GB (Mac mini) | 95.9 tok/s, quality 89.0% | base is still best |  |  |
| Qwen 3.8 27B | Apple M5 Pro (Mac mini) | 35.7 tok/s, quality 90.9% | base is still best |  |  |
| Qwen 3.8 27B, draft-ahead decoding | Apple M5 Pro, 64 GB (Mac mini) | 17.8 tok/s, quality 91.5% | Standard 4-bit + guess 4 words ahead (test only, off in the app) | 32.2 tok/s | 91.5% |
| Qwen 3.8 27B, smaller tuned build | Apple M5 Pro, 64 GB (Mac mini) | 17.7 tok/s, quality 94.8% | AtomicChat 3.80-bit DWQ (tuned to copy the full model) | 20.4 tok/s | 94.6% |
| Arete 27B (NousResearch) | Apple M5 Pro, 64 GB (Mac mini) | 35.5 tok/s, quality 89.9% | base is still best |  |  |
| Qwen3.6-35B-A3B | Apple M5 Pro, 64 GB (Mac mini) | 157.8 tok/s, quality 86.3% | base is still best |  |  |
| Axion 1.0 35B | Apple M5 Pro, 64 GB (Mac mini) | 74.7 tok/s, quality 92.3% | only one build tested |  |  |
| gpt-oss-20b | Apple M5 Pro, 64 GB (Mac mini) | 106.1 tok/s, quality 66.6% | no clear win (a trade-off is listed) |  |  |
| Qwen3.6-35B-A3B | Apple M3 Max, 36 GB (MacBook Pro) | 61.4 tok/s, quality – | only one build tested |  |  |
| Qwen3 Reranker 0.6B | Apple M5 Pro, 64 GB (Mac mini) | 135.4 pairs/s, quality 0.682 / 0.748 | no clear win (a trade-off is listed) |  |  |
| Qwen3.5-0.8B | Apple M5 Pro (Mac mini) | 120.0 tok/s, quality 7% | Qwen3.5-0.8B + MIT CSAIL's p50c weight edit (reproduced) | 120.0 tok/s | 33% |

Quality means something different per test, so compare it only within one section.

## Results

### Qwen3.5-4B (Smarty) on Apple M5 Pro (Mac mini)

Measured 2026-10-22.

| Version | Speed (tok/s) | vs base | Peak memory | Quality (top-1 match vs 8-bit) | Perplexity | Checks | Verdict |
|---|---|---|---|---|---|---|---|
| **Standard 4-bit (what we serve)** | 99.7 |  | 4.13 GB | 86.5% | 14.60 | 10/10 | base |
| ↳ MXFP4 (4-bit float) | about 104 | +4% | – | – | about 15.2 | – | no gain: 4% faster but 4% worse quality |
| ↳ 4-bit, finer groups (g32) | about 91 | -9% | – | – | 14.54 | – | slower: slightly better quality, 9% slower |
| ↳ Mixed 3/6-bit | 13-20% faster |  | 9-13% less | – | +31-36% | – | worse: too lossy |
| ↳ 3-bit | 13-20% faster |  | 9-13% less | – | +31-36% | 9/10 | worse: too lossy, 1 wrong answer |
| ↳ Standard 4-bit + 8-bit attention memory | same |  | – | – | – | – | no gain: no difference on short chats |
| ↳ 8-bit copy (quality yardstick, not served) | 57.0 | -43% | – | 100.0% | – | – | reference: more bits, slower |

How it was measured: Speed: output tokens per second on a short chat (median of 3 after a warm-up). Memory: peak during a 4,096-token prompt. Quality: how often the version picks the same next word as a near-lossless 8-bit copy (top-1 match), plus 10 short questions with one right answer.

Takeaway: the standard 4-bit build is still the best tradeoff. Speed tracks how many bits each weight uses, and below 4 bits quality drops sharply. Next to try: DWQ 3-bit.

_Entered from the factory report as posted on the day; the full result files are on the Mac mini. Rows marked 'about' will be exact after the next run._

### Qwen3.5-4B (Smarty), GSM8K math on Apple M5 Pro, 64 GB (Mac mini)

Measured 2026-11-05.

| Version | Speed (tok/s) | vs base | Peak memory | Quality (GSM8K, 500 problems right) | Paired vs base | Verdict |
|---|---|---|---|---|---|---|
| **Standard 4-bit (what we serve)** | 99.7 |  | 4.13 GB | 89.0% |  | base |
| ↳ DWQ 3-bit (tuned to copy the full model) | 120.1 | +20% | 3.62 GB | 83.6% | +14 / -41 (p < 0.001) | worse: faster and smaller, but 2.5 to 8.3 points fewer right |
| ↳ DWQ 4-bit (tuned to copy the full model) | 100.4 | +1% | 4.13 GB | 88.4% | +20 / -23 (p = 0.76) | no gain: same speed, no real difference in right answers |

How it was measured: 500 GSM8K grade-school math problems (openai/gsm8k test, seed 0), the same for every version, served the way Smarty Pants serves Smarty: thinking off, greedy, up to 1,024 tokens. DWQ builds: mlx-lm DWQ, 1,024 samples, group size 64. A version is better only with more right answers at McNemar p < 0.05; faster counts only if the 95% interval of the accuracy change stays above -2 points. Script: scripts/model-factory/benchcheck.py.

Takeaway: neither DWQ build beats the one we serve. 3-bit DWQ is about 20% faster and 13% smaller but gets about 5 points fewer right; 4-bit DWQ is no different. The served build stays. We keep negative results on the page.

### Qwen3.5-4B (Smarty), draft-ahead decoding on Apple M5 Pro, 64 GB (Mac mini)

Measured 2026-11-05.

| Version | Speed (tok/s) | vs base | Peak memory | Quality (GSM8K, 500 problems right) | Paired vs base | Verdict |
|---|---|---|---|---|---|---|
| **Standard 4-bit (what we serve)** | 95.9 |  | 2.90 GB | 89.0% |  | base |
| ↳ Standard 4-bit + guess 4 words ahead | 105.2 | +10% | 3.43 GB | 88.8% | +4 / -5 (p = 1.0) | no gain: 10% faster, same right answers, but 18% more memory |
| ↳ Standard 4-bit + guess 2 words ahead | 93.2 | -3% | 3.43 GB | 88.2% | +4 / -8 (p = 0.39) | slower: 3% slower and 18% more memory |

How it was measured: draft-ahead (speculative) decoding: a small guesser model, mlx-community/Qwen3.5-0.8B-MLX-4bit, proposes 2 or 4 words and Smarty checks them in one pass. Same 500 GSM8K problems and served settings as above (thinking off, greedy, up to 1,024 tokens); the standard build was timed again in the same sitting. Guesses accepted: 85% (2 at a time), 76% (4 at a time).

Takeaway: no win yet. Guessing 4 ahead is 10% faster with the same right answers, but it needs 18% more memory, and our rule allows at most 5% more. Guessing 2 ahead is slower.

### Qwen 3.8 27B on Apple M5 Pro (Mac mini)

Measured 2026-11-02.

| Version | Speed (tok/s) | vs base | Peak memory | Quality (top-1 match vs 8-bit) | Perplexity | Checks | Verdict |
|---|---|---|---|---|---|---|---|
| **Standard 4-bit (mlx-community)** | 35.7 |  | 18.26 GB | 90.9% | 7.95 | 10/10 | base |
| ↳ Mixed 3/6-bit | slower |  | – | – | – | – | worse: slower and lower quality |
| ↳ Standard 4-bit + 8-bit attention memory | same |  | – | – | – | – | no gain: no difference on short chats |
| ↳ 8-bit copy (quality yardstick, not served) | – |  | – | 100.0% | 7.67 | – | reference: quality yardstick |

How it was measured: Speed: output tokens per second on a short chat (median of 3 after a warm-up). Memory: peak during a 4,096-token prompt. Quality: how often the version picks the same next word as a near-lossless 8-bit copy (top-1 match), plus 10 short questions with one right answer. mlx 0.32.4.

Takeaway: the standard 4-bit build runs well on a 32 GB+ Mac; neither tested change helped.

_Entered from the factory report as posted on the day; the full result files are on the Mac mini. Rows marked 'about' will be exact after the next run._

### Qwen 3.8 27B, draft-ahead decoding on Apple M5 Pro, 64 GB (Mac mini)

Measured 2026-11-06. Important: this gain was measured greedy with thinking off. When our Mac app served it live at its default settings (temperature 0.6, thinking on), we did not see the speed-up, so the app has draft-ahead turned off again while we find out why. Do not expect this speed from Smarty Pants today.

| Version | Speed (tok/s) | vs base | Peak memory | Quality (GSM8K, 200 problems right) | Paired vs base | Verdict |
|---|---|---|---|---|---|---|
| **Standard 4-bit (mlx-community)** | 17.8 |  | 15.80 GB | 91.5% |  | base |
| ↳ Standard 4-bit + guess 4 words ahead (test only, off in the app) | 32.2 | +81% | 16.31 GB | 91.5% | +1 / -1 (p = 1.0) | faster: 81% faster, same right answers, 3% more memory (in this test setup; not yet in the live app) |

How it was measured: draft-ahead (speculative) decoding: the small mlx-community/Qwen3.5-0.8B-MLX-4bit guesses 4 words at a time and Qwen 3.8 27B checks them in one pass; 76% of guesses were kept. 200 GSM8K problems, the same for both, measured with mlx-lm in Python, greedy, thinking off, up to 1,024 tokens. The standard build was timed again in the same sitting, with serving paused (this sitting's standard speed is lower than the 35.7 tok/s chat test above, which used a different prompt and length).

Takeaway: draft-ahead made Qwen 3.8 27B 81% faster with the same right answers and only 3% more memory, the first speed-up to beat a standard build on this page.

### Qwen 3.8 27B, smaller tuned build on Apple M5 Pro, 64 GB (Mac mini)

Measured 2026-11-08.

| Version | Speed (tok/s) | vs base | Peak memory | Quality (GSM8K, all 1,319 problems right) | Paired vs base | Verdict |
|---|---|---|---|---|---|---|
| **Standard 4-bit (mlx-community, revision 10c35ca)** | 17.7 |  | 15.88 GB | 94.8% |  | base |
| ↳ AtomicChat 3.80-bit DWQ (tuned to copy the full model) | 20.4 | +15% | 13.52 GB | 94.6% | +22 / -25 (p = 0.77) | faster: 15% faster and 15% less memory, answers as good (-1.2 to +0.8 points) |

How it was measured: the full GSM8K test (1,319 problems), the same for both, served the way Smarty Pants serves it: thinking off, greedy, up to 1,024 tokens. Better needs answers as good (95% interval of the accuracy change above -2 points) plus at least 10% faster or 10% less memory. In the Mac app's own code, at temperature 0.6 with thinking on, the smaller build also ran faster: 20.3 vs 17.6 tok/s.

Takeaway: the smaller tuned build gives the same answers (94.6% vs 94.8%, no real difference) while running 15% faster on 15% less memory, so it fits more Macs.

Credit: the 3.80-bits-per-weight DWQ build is by AtomicChat ([AtomicChat/Qwen3.8-27B-MLX-AD-3.80bpw-DWQ-13.7GB](https://huggingface.co/AtomicChat/Qwen3.8-27B-MLX-AD-3.80bpw-DWQ-13.7GB), revision 9fa7ab0); we tested it.

### Arete 27B (NousResearch) on Apple M5 Pro, 64 GB (Mac mini)

Measured 2026-11-09.

| Version | Speed (tok/s) | vs base | Peak memory | Quality (top-1 match vs 8-bit) | Perplexity | Checks | Verdict |
|---|---|---|---|---|---|---|---|
| **4-bit (Duckets MLX build)** | 35.5 |  | 18.26 GB | 89.9% | 8.34 | 10/10 | base |
| ↳ 8-bit copy (quality yardstick, not served) | 11.6 | -67% | 30.87 GB | 100.0% | 8.06 | 9/10 | reference: quality yardstick |

How it was measured: Speed: output tokens per second on a short chat (median of 3 after a warm-up). Memory: peak during a 4,096-token prompt. Quality: how often the version picks the same next word as a near-lossless 8-bit copy (top-1 match), plus 10 short questions with one right answer. The yardstick is a community 8-bit copy (pjain001/arete-27b-8bit-mlx); bf16 did not fit the Mac's free disk. Also checked on 300 GSM8K math problems (thinking off, greedy, up to 1,024 tokens): the 4-bit build got 94.3% right.

Takeaway: the 4-bit build passes: 10/10 checks, 94.3% on GSM8K (in line with Qwen 3.8 27B, which it is fine-tuned from), 35.5 tok/s and an 18.3 GB peak. That fits 32 GB+ Macs comfortably and 24 GB Macs only tightly.

Credit: Arete 27B is by NousResearch (Apache-2.0); the 4-bit MLX build is by Duckets ([Duckets/Arete-27B-MLX-4bit](https://huggingface.co/Duckets/Arete-27B-MLX-4bit), revision bd3f716).

### Qwen3.6-35B-A3B on Apple M5 Pro, 64 GB (Mac mini)

Measured 2026-11-07. Our own 4-bit build timed 34% faster than the community build, but that is unconfirmed: it has the same bits and memory, and the community build was timed right after a long download. We will rerun it before relying on it.

| Version | Speed (tok/s) | vs base | Peak memory | Quality (top-1 match vs 6-bit) | Perplexity | Checks | Verdict |
|---|---|---|---|---|---|---|---|
| **Standard 4-bit (mlx-community)** | 157.8 |  | 21.49 GB | 86.3% | 11.83 | 10/10 | base |
| ↳ 4-bit, our own build | 210.7 | +34% | 21.49 GB | 86.2% | 11.80 | 10/10 | unconfirmed: timed 34% faster with the same quality; needs a repeat run |
| ↳ Mixed 3/4-bit | 118.0 | -25% | 17.89 GB | 76.2% | 13.43 | 10/10 | worse: 17% less memory, but 25% slower and perplexity +13.5% |
| ↳ 6-bit copy (quality yardstick, not served) | 119.6 | -24% | 30.15 GB | 100.0% | 11.14 | 10/10 | reference: quality yardstick |

How it was measured: Speed: output tokens per second on a short chat (median of 3 after a warm-up). Memory: peak during a 4,096-token prompt. Quality: how often the version picks the same next word as a 6-bit copy (the quality yardstick here) (top-1 match), plus 10 short questions with one right answer. mlx 0.32.4, mlx-lm 0.32.2.

Takeaway: the standard 4-bit build passes all 10 checks at about 158 tok/s and 21.5 GB, so it fits Macs with 48 GB or more. Mixed 3/4-bit saves memory but loses too much quality.

### Axion 1.0 35B on Apple M5 Pro, 64 GB (Mac mini)

Measured 2026-11-11.

| Version | Speed (tok/s) | vs base | Peak memory | Quality (GSM8K, 300 problems right) | Paired vs base | Verdict |
|---|---|---|---|---|---|---|
| **UD 4-bit (NapYang MLX build)** | 74.7 |  | 21.09 GB | 92.3% |  | base |

How it was measured: 300 GSM8K math problems, thinking off, greedy, up to 2,048 tokens. Single build tested (no yardstick copy).

Takeaway: passes: 92.3% right at 74.7 tok/s and a 21.1 GB peak, so it fits Macs with 32 GB or more. For comparison on the same test: Qwen 3.8 27B 94.6% (all 1,319 problems), Arete 27B 94.3% at 35.5 tok/s.

Credit: Axion 1.0 35B is by Axion1-0 (Apache-2.0); the UD 4-bit MLX build is by NapYang ([NapYang/Axion-1.0-35B-UD-MLX-4bit-fp16](https://huggingface.co/NapYang/Axion-1.0-35B-UD-MLX-4bit-fp16), revision be0c767).

### gpt-oss-20b on Apple M5 Pro, 64 GB (Mac mini)

Measured 2026-11-08. The yardstick is not a true 8-bit copy: the converter kept OpenAI's own 4-bit expert weights, so it came out at 4.6 bits per weight. Quality here means closeness to a near-original copy, not to a higher-precision one.

| Version | Speed (tok/s) | vs base | Peak memory | Quality (top-1 match vs yardstick) | Perplexity | Checks | Verdict |
|---|---|---|---|---|---|---|---|
| **MXFP4-Q4 (mlx-community)** | 106.1 |  | 12.12 GB | 66.6% | 30.92 | 7/10 | base |
| ↳ OptiQ 4-bit (mlx-community) | 99.3 | -6% | 12.57 GB | 85.8% | 28.68 | 9/10 | trade-off: much closer to the original and 2 more checks right, 6% slower, 0.45 GB more |
| ↳ Our convert (yardstick, 4.6 bits/weight, not served) | 85.7 | -19% | 12.99 GB | 100.0% | 28.10 | 8/10 | reference: quality yardstick |

How it was measured: Speed: output tokens per second on a short chat (median of 3 after a warm-up). Memory: peak during a 4,096-token prompt. Quality: how often the version picks the same next word as our yardstick copy (top-1 match), plus 10 short questions with one right answer. mlx 0.32.4, mlx-lm 0.32.2.

Takeaway: both community 4-bit builds run at about 100 tok/s and peak at 12-13 GB, so they fit 24 GB Macs. OptiQ is a trade-off rather than a win: much closer to the original (top-1 85.8% vs 66.6%, 9/10 checks vs 7/10) for 6% less speed. A math accuracy test comes next.

### Qwen3.6-35B-A3B on Apple M3 Max, 36 GB (MacBook Pro)

Measured 2026-09-08.

| Version | Speed (tok/s) | vs base | Peak memory | Quality | Perplexity | Checks | Verdict |
|---|---|---|---|---|---|---|---|
| **Standard 4-bit (mlx-community)** | 61.4 |  | 21.52 GB | – | – | – | base |

How it was measured: speed only: one request at a time, 500 to 4,096-token prompts, 128 tokens out, mlx-vlm 0.7.0. With 8 requests at once the Mac produced 193 tok/s in total. No quality test yet.

### Qwen3 Reranker 0.6B on Apple M5 Pro, 64 GB (Mac mini)

Measured 2026-11-09.

| Version | Speed (pairs/s, batch 8) | vs base | Peak memory | Quality (NDCG@10 / MRR@10) | Same top pick as bf16 | Verdict |
|---|---|---|---|---|---|---|
| **bf16 (official Qwen release)** | 135.4 |  | 3.08 GB | 0.682 / 0.748 |  | base |
| ↳ mxfp8 (mlx-community) | 151.8 | +12% | 2.50 GB | 0.677 / 0.745 | 84.7% | trade-off: 0.6 GB less memory; faster at batch 8 but slower at batch 1 and 32 |
| ↳ 8-bit, our own build (group 64, not released) | 84.3 | -38% | 2.52 GB | 0.684 / 0.753 | 96.0% | trade-off: 0.6 GB less memory, closest to bf16, but slower |

How it was measured: reranking 150 queries (3,000 query-document pairs) from mteb/askubuntudupquestions-reranking; score = probability of "yes" after Qwen's reranker prompt. Speed is pairs per second at batch size 8 over a short window, so treat it as rough (batch 1: bf16 68.8, mxfp8 51.9, ours 48.4; batch 32: 138.2, 95.1, 93.6).

Takeaway: a trade-off, not a win. On a 0.6B model the 8-bit builds save only about 0.6 GB and are not faster overall; ranking quality differences are within noise. The bf16 build is the one we serve. Our 8-bit build agrees with bf16 on the top pick far more often than the mxfp8 build (96% vs 85%).

### Qwen3.5-0.8B on Apple M5 Pro (Mac mini)

Measured 2026-11-04.

| Version | Speed (tok/s) | vs base | Peak memory | Quality (MATH-500, 30 problems) | Finished | Verdict |
|---|---|---|---|---|---|---|
| **Qwen3.5-0.8B, original** | 120.0 |  | 2.22 GB | 7% | 7% | base |
| ↳ Qwen3.5-0.8B + MIT CSAIL's p50c weight edit (reproduced) | 120.0 | same | 2.19 GB | 33% | 60% | better: finished 60% of answers (was 7%), ended in a loop 3% (was 87%) |

How it was measured: 30 MATH-500 math problems (seeded random pick), thinking on, up to 32,768 tokens, MIT's sampling settings, 1 answer per problem, graded with math-verify 0.9.0 by MIT's rule. Runs on MLX in bfloat16 rather than vLLM, so single answers are not comparable one to one with MIT's.

Takeaway: the edit changes 0.016% of the weights. On our Mac it cut loops from 87% to 3% and raised correct answers from 7% to 33%, with no change in speed or memory. Problem by problem, the edited model got 8 right that the original missed and lost none (sign test p ≈ 0.008). MIT reports 7.9% to 48.1% on all 500 problems with 4 answers each.

Credit: this is a reproduction of MIT CSAIL's published edit (Takehi, Teoh, Zhang and Khattab, [weight-space programming](https://rikiyat.github.io/blog/weight-space-programming), edit and evaluation code from [RikiyaT/lm_understand-logs](https://github.com/RikiyaT/lm_understand-logs)). Smarty Pants did not make this edit; we rebuilt it bit for bit, hash-checked it and measured it on a Mac.

## Use these models without a Mac

Smarty Pants serves models from Macs like these at `https://smartypants.network/v1` (OpenAI-compatible). Smarty (`smartypants/smarty`) is the Qwen3.5-4B standard 4-bit above; see https://smartypants.network for which models are open and their prices.

## Data

`results.json` holds every number on this page, one entry per section, rebuilt by `scripts/model-factory/benchmarks.py` after each factory run. No prompts, answers or machine identifiers are included.
