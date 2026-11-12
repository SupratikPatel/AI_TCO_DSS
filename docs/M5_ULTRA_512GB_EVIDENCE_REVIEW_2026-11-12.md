# M5 Ultra 512 GB: supplied-report verification

Reviewed 2026-11-12. The author's
`m5_ultra_512gb_benchmark_evidence_report.md` is preserved byte-for-byte under
[the new archive](evidence/m5_512gb_report_review_2026-11-12/m5_ultra_512gb_benchmark_evidence_report.md).
This advances the [previous review](YOUTUBE_EVIDENCE_REPORT_V11_REVIEW_2026-11-12.md):
**the M5 Ultra 512 GB configuration, two US prices, and source-reported 512 GB
performance are now verified.** Earlier checkpoints saying no 512 GB measurements
were acquired describe the earlier evidence state and are superseded by this review.

It does not establish five simultaneous 128K requests or eight resident agent
sessions on that machine. No 512 GB catalog entry/shared-serving implementation,
production benchmark import, coefficient change or capacity-policy change was made.
U-02 through U-06 and the remaining U-07 implementation stay open.

## Hardware and price evidence

[Apple technical specifications](https://www.apple.com/mac-studio/specs/) confirm
512 GB with the 36-core CPU / 80-core GPU M5 Ultra and nominal 1.2 TB/s bandwidth.
The archived US Store Product/Offer JSON-LD gives **USD 22,299 for 512 GB / 1 TB**
and **USD 29,799 for 512 GB / 16 TB**, retrieved 2026-11-12. These are the exact
configuration titles and USD offers, not an inferred memory-upgrade calculation.
Sources: [1 TB configuration](https://www.apple.com/shop/buy-mac/mac-studio/m5-ultra-chip-36-core-cpu-80-core-gpu-512gb-memory-1tb-storage),
[16 TB configuration](https://www.apple.com/shop/buy-mac/mac-studio/m5-ultra-chip-36-core-cpu-80-core-gpu-512gb-memory-16tb-storage).
No German quote, tax conversion, intermediate-SSD configured price or delivery
guarantee was verified here. Do not manufacture these from the US offers.

The [launch announcement](https://www.apple.com/newsroom/2026/08/apple-introduces-new-mac-studio-with-m5-max-and-m5-ultra/)
specifies September 22 general availability and **late October** for 512 GB.
It does not establish the report's exact October 28 order/November 9 first-delivery
dates, four-die package claim or exact 1228.8 GB/s figure. Those remain unverified.
Consumer-delivery timing alone cannot prove a reviewer lacked an earlier unit.

## Actual 512 GB source results

The two supplied leaderboard pages were followed to permanent records. Sixteen
performance pages were archived and parsed: **13 report 512 GB**, and three report
256 GB and remain separate references. oMLX hardware/resource fields are uploaded
community evidence, not this project's inspection of physical hardware.

| Model and permanent record | Reported input/context | Reported TTFT | Reported TG rate | Conditions and memory |
|---|---:|---:|---:|---|
| [Qwen3.8-Flash-Next-oQ6e-mtp](https://omlx.ai/benchmarks/performance/2zvzoy8b) | 131072 | **28.250 s** | **102.3 tok/s** | M5 Ultra 80c / 512 GB, oMLX 0.7.3, fixed MTP depth 3. Selected peak 150.3 GB; resource MLX active 149.81 GB / process footprint 154.96 GB. |
| [gpt-oss-120b-MLX-8bit](https://omlx.ai/benchmarks/performance/3u2u1f9j) | 131072 | **71.288 s** | **50.4 tok/s** | 80c / 512 GB, oMLX 0.7.4.dev1, MTP false. Resource MLX active 121.62 GB / process footprint 128.52 GB. |
| [Same gpt-oss session, longer input](https://omlx.ai/benchmarks/performance/odblvo21) | **200000** | **130.446 s** | **42.4 tok/s** | Display shorthand is `195k`; it is not 195000 actual tokens. Resource MLX active 124.50 GB. |
| [DeepSeek-V4.1-Flash-oQ4e-mtp](https://omlx.ai/benchmarks/performance/hu57yay1) | 65536 | **51.214 s** | **82.0 tok/s** | 80c / 512 GB, oMLX 0.7.3, MTP true. Selected peak 411.8 GB; active 410.79 GB / footprint 418.92 GB. Exact mixed quantization and live dtype not established by the model name. |

Qwen's source also reports 128.7 / 113.2 / 144.9 TPS at 1024 / 8192 / 32768 input,
and batching 1/2/4/8 gives aggregate **128.7 / 133.2 / 173.4 / 206.5 TPS** at
the short benchmark point. Those are useful batching results, not five long-context
requests. The audit retains all permanent IDs and metrics.

The report's Qwen 28.25-second TTFT, originally marked estimated from PP, can now
be cited directly from the permanent record. Other PP rates remain source labels;
the pages do not supply isolated server timers or request-event logs, so they must
not be imported as proven isolated prefill. Do not derive new TTFT observations
from rounded PP values where a direct timer is missing.

All performance-page raw JSON blocks are **model settings**. They do not establish
actual generated-token counts, per-token timestamps, cache hit fractions or exact
weight revisions/hashes. The report's uniform 128-output-token assertion is not
independently recovered from those records. Disabled TurboQuant does not establish
FP16 KV (reuse C-067). The gpt-oss recipe says `max_context_window: 128000` while
the result fields report 131072 and 200000: retain both and investigate their
semantics, rather than treating the recipe cap as a verified runtime allocation.

DeepSeek's two 1K records belong to different result/session groups. Their different
rates do not independently establish the report's cold/warm cache classification.
Similarly, `moe_expert_offload_enabled: false` is narrower than proving every
embedding/ngram table fully resident; no unrecorded placement was filled in.

## Apple single-node and distributed results

Apple's [MLX distributed-inference post](https://machinelearning.apple.com/research/mlx-distributed-inference)
explicitly identifies 512 GB machines and supplies `-p 8192 -g 128 -b 1` examples.
Its source contains both tabs of the tables, even though a text-only view initially
shows the 8K tab. Both tabs were parsed as data without executing page code.

| Single M5 Ultra 512 GB | TTFT, 8192 input | Decode, 8192 input | TTFT, 65536 input | Decode, 65536 input |
|---|---:|---:|---:|---:|
| Qwen3.8 27B, BF16 | 4.1 s | 19.69 TPS | **43.7 s** | **17.87 TPS** |
| Mistral Medium 3.5 128B, FP8 | 24.6 s | 7.70 TPS | **273.0 s** | **6.16 TPS** |

These are useful native-precision resident measurements for different models, not
Qwen Flash-Next low-bit results. Exact historical runtime/weight/cache manifests
are still absent. Dividing input count by TTFT gives an estimate, not an isolated
prefill measurement. Muse Spark Open's 36.73 TPS is a **four-machine** 8K result;
its one-machine case does not fit. Clustering and batch concurrency are distinct.
The full parsed tables are retained in the audit; no model or node count was
silently transferred to another observation.

## Low-bit quality evidence now recovered

The ISTA model card was pinned to revision
`ed59f92082b1e93c0e96d60a8b11aab089b52f09`. It confirms a fixed IQ4_NL n-gram
shard plus mixed transformer quantization. Its LiveCodeBench v6 summary is
**81.14 / 83.43 / 86.29 / 86.86** for Q2_0 / IQ2_XS / IQ3_XXS / IQ3_S, versus
87.43 BF16. These publisher results support artifact-specific quality discussion;
they are not uniform INT2/INT3 quality or measurements of the DSS's agent workload.
Source: [pinned card](https://huggingface.co/ISTA-DASLab/Qwen3.8-Flash-Next-GSQ-RCO-GGUF/blob/ed59f92082b1e93c0e96d60a8b11aab089b52f09/README.md).

Four oMLX downloadable gzip question logs were acquired and reconciled:

| Record / artifact label | Questions | Published correct flags recounted | Failures |
|---|---:|---:|---:|
| [GSQ-RCO-Q2_0, MMLU-Pro](https://omlx.ai/benchmarks/intelligence/mkzszvig) | 1000 | 714 (71.4%) | 286 |
| [GSQ-RCO-Q2_0, GSM8K](https://omlx.ai/benchmarks/intelligence/ybmeme01) | 1319 | 1238 (93.9%) | 81 |
| [oQ4e, HumanEval](https://omlx.ai/benchmarks/intelligence/qvlxvz1i) | 164 | 132 (80.5%) | 32 |
| [oQ4e-MTP-128k, HumanEval](https://omlx.ai/benchmarks/intelligence/6b3p2k87) | 164 | 148 (90.2%) | 16 |

All **2647 unique within-run question IDs** and pass/failure totals reconcile. This
recounts publisher grading flags; it is not independent regrading. Generated code
and suggested shell commands were not executed. Logs omit question text, and the
later HumanEval log also omits completion counts/finish reasons. Do not turn task
duration into a decode or TTFT observation.

The earlier HumanEval run's 32 failures comprise **24 `stop` and eight `length`**
finishes. The later run changes sampling, MTP, batch size, runtime and artifact label
as well as output cap. The score difference is not a controlled experiment proving
that a larger token cap alone caused recovery. The Q2_0 repository label in the
quality uploads does not establish byte identity with the separately pinned GGUF.

Unsloth's [model guide](https://unsloth.ai/docs/models/qwen3.8-next),
[Dynamic v3.0](https://unsloth.ai/docs/basics/dynamic-3.0-ggufs) and
[Dynamic v3.1](https://unsloth.ai/docs/basics/dynamic-3.0-ggufs/dynamic-3.1-ggufs)
primary guides were also archived. They confirm the published
KLD/agreement table, 1-bit DeepSWE/Terminal-Bench headline results and explicit
warnings about low-bit tool calling. Preserve Dynamic v3.0 versus v3.1 distinctions;
do not merge a quality row from one pack revision with another size/runtime result.
Q6's source KLD values, missing in the supplied table, are mean **0.027091** and
99.9th percentile **0.8416**. The previously archived Sushi source reports a score
of 94 from 182/194 points, not proof of 94 successes among 100 tool calls.

## Corrections, access limits and remaining work

C-070 through C-075 in [the ledger](../specs/07_DATA_CORRECTIONS.md) correct the
report's MacStories MTP mode, cross-run memory, gpt-oss context, HumanEval causal
claim, Sushi sample interpretation and a transcribed Apple TTFT. The supplied file
was not edited. The earlier MacStories 60.6 / 74.7 TPS ladder used **MTP depth 3**,
not MTP off; reusing an earlier source does not warrant changing its conditions.
Apple's Qwen 65K two-node tensor-parallel TTFT is **29.4 s**, not the report's 29.0 s.

YouTube watch HTML/oEmbed confirm the lead video's identity and description, but
the caption endpoint returned HTTP 200 with **zero bytes**. Exact quoted timestamps
and the claim about what physical unit the creator had remain unverified here.
The Reddit thread says it reposts someone else's X screenshots. Web text supports
the existence of an approximate two-minute claim, while direct JSON and image
requests returned 403. That does not recover a primary operator/run bundle or
prove model/precision/timer details. Keep it a secondary lead; do not treat a failed
fetch as measured inference failure. The referenced companion JSON was not supplied.

The five-request / 131072-input workload, eight retained sessions and exact low-bit
tool reliability remain **not found in the inspected 512 GB evidence**. This is a
bounded search result, not proof that no such measurement exists anywhere. Original
run-linked artifact/build, KV/cache state, request counts and timing traces are the
next acquisition targets. No benchmark machine is available. Existing independent
offload/API gaps remain open; M3 purchase options stay out of scope.

## Saved audit and checks

[manifest.json](evidence/m5_512gb_report_review_2026-11-12/manifest.json) hashes the
input and 42 remote responses, including the empty/blocked responses explicitly.
[derive_audit.py](evidence/m5_512gb_report_review_2026-11-12/derive_audit.py) reproduces
the offline [audit](evidence/m5_512gb_report_review_2026-11-12/review_audit.json):
43 source/input sizes and hashes, 16 performance records, both Apple table contexts,
two offers and 2647 quality records. Prior source archives were reused, not replaced.

Strict calibration remains zero comparable observations / 13 existing exclusions /
MAPE n/a. New qualified evidence is materially stronger; no strict import is justified
by filling missing facts. This review changes evidence/continuity documents only.
Reuse the engine 0.1.4 combined verification; do not rerun application/browser suites.
Preserve staged/unrelated work and logs. Never commit or push.

Verification: all 43 archived sizes/hashes match, the input matches the Downloads
original byte-for-byte, local review links resolve, and all 33 session-continuity
checks pass after shortening the resume prompt to its existing 50-line limit.
No application/frontend/browser tests were repeated; no inference or paid calls ran.
