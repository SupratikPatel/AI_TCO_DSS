# Supplied evidence report v1.1: new M5 evidence and corrections

Reviewed 2026-11-12. Input: the author's Downloads file
`ai_deployment_benchmark_evidence_report (1).md`, preserved byte-for-byte as
[submitted_report_v1.1.md](evidence/user_report_v11_review_2026-11-12/submitted_report_v1.1.md).
This is a delta review of the [first supplied report](YOUTUBE_EVIDENCE_REPORT_REVIEW_2026-11-12.md).
It reuses earlier source archives and decisions rather than repeating their acquisition.
M5 Macs remain the only Mac deployment options. Historical M3 results are retained only
to correct attribution; they do not validate M5 performance.

The revision adds useful evidence: raw Kapitsa responses, a non-speculative M5 Max
depth sweep, oMLX model settings/resource summaries and Sushi performance/quality
summaries. It also misattributes M3 Ultra code results to M5 Ultra. **There are still
no M5 Ultra 512 GB measurements in these reports.** No price/configuration for that
target was verified here, and no catalog option or shared-serving implementation was added.

## Archive and reproducibility

[manifest.json](evidence/user_report_v11_review_2026-11-12/manifest.json) records the
input and 33 new remote files, with URLs, retrieval times, sizes and SHA-256 hashes.
All 34 hashes/sizes reconcile; the submitted copy matches the original input.
[review_audit.json](evidence/user_report_v11_review_2026-11-12/review_audit.json) retains
derived counts, timing checks, settings, engine parameters and context-shape results.
[derive_review.py](evidence/user_report_v11_review_2026-11-12/derive_review.py)
reproduces that audit offline from the workspace root with `uv run python`.
It executes only project/local derivation code. Archived external harnesses and shell
scripts remain `.py.txt` / `.sh.txt` and were not executed.

Pinned acquisition heads: Kapitsa `5ca196fba4b052ca143cf911639e93c31b8e2a8a`,
Sushi `404e8b386b8ece983806cf190a780d6001b68072`, mlx-serve
`f87552989b62bef91c981abeb5425e46e83568df`. These are archive identities, not a claim
that each historical experiment used its repository's acquisition head.

## New run evidence

| Evidence | Established facts | Use and remaining limits |
|---|---|---|
| [Heretik M5 Max 128 GB depth sweep](https://heretik.io/qwen38-flash-next-262k-macbook/) | `llama-bench 213df585b`, UD-IQ4_XS, no MTP, `-p 512 -n 128 -d 0,4096,16384,32768,65536,131072,262144 -r 1`; reported FP16 KV. Decode falls from 33.0 to 17.0 at 128K and 10.9 at 256K. | Seven single-run source points, not repeated raw timing samples. Mixed GGUF and mmap n-gram table do not establish a uniform resident INT4 observation. Incremental pp512 at occupied depth is not a cold full-context fill. |
| [oMLX four benchmark records](https://omlx.ai/benchmarks/performance/t9sos5mz) | Archived all four linked records, including settings and resource summaries. `t9sos5mz` reports oQ2.5e-mtp 73.4 TPS at 128K and aggregate 655.6 TPS at batch eight / 1K. | MTP-enabled, artifact-specific observations. Embedded JSON is model settings, not per-request event logs. No actual output count/live KV dtype established by that JSON. Batch eight at 1K cannot validate five occupied 128K contexts. |
| [Kapitsa November 4 Flash-Next](https://github.com/nace-ai/kapitsa/blob/5ca196fba4b052ca143cf911639e93c31b8e2a8a/bench/results/2026-11-04-m5-max-flash-next/README.md) | Three runs, each five sampled and five greedy coding answers: 30 actual 512-token responses. Run medians reconcile to 108.47 sampled and 113.94 greedy TPS. Six cold prompt timings and 36 sweep requests reconcile; all sweep outputs are 192 tokens. | Recoverable clean harness `af7d79580a176ffef45d1aaa72cc0b888f214453`, MTP depth two, one slot / configured 32768. Mixed 4/6/8-bit weights, SSD-mapped 32 GB n-gram table. Headline decode uses a middle window; prefill is prompt/TTFT. Not strict resident uniform-bit calibration. |
| [Kapitsa October 25 Qwen 27B MLX-LM](https://github.com/nace-ai/kapitsa/blob/5ca196fba4b052ca143cf911639e93c31b8e2a8a/bench/results/2026-10-25-m5-max/README.md) | Three saved runs, another 30 actual 512-token responses and six cold prompt timings. Per-run sampled medians 29.27 / 30.96 / 31.02 TPS; greedy 27.73 / 29.69 / 31.47. Runtime/version and command saved. | Harness recorded dirty at `cd20dcc690ac499a3433c60b1c7c0662e550ca6a`; filenames/weight bytes do not resolve model revision or exact quantization. Live cache dtype remains unknown. Native isolated-prefill timings are null. |
| [Sushi source tables](https://github.com/beamivalice/sushi/blob/404e8b386b8ece983806cf190a780d6001b68072/README.md) | Primary README confirms STQ 2.75bpw 138.2 TPS and 4bpw 122.0 TPS at the 128K rung, plus tool-eval scores 94 (182/194) and 90 (174/194). Also reports 2bpw score 88 (170/194). | Useful quantization-specific quality leads, with different thinking settings across some models. These are published summaries, not this project's validation of its exact INT2/INT3 artifact, quality floor or five-request SLA. Memory table excludes SSD prompt cache/n-gram table and includes buffers/state, not KV alone. |
| [mlx-serve M5 Ultra 256 GB Qwen 27B A/B](https://github.com/ddalcu/mlx-serve/blob/f87552989b62bef91c981abeb5425e46e83568df/docs/performance.md) | Two boots per arm at 8K/32K/64K/128K, `--no-mtp --max-concurrent 1`. Stock 128K: 947.8 / 949.8 TPS; int8-Q/K arm: 1080.4 / 1084.6. Acquired inspection script reads server `timings.prompt_ms`. | Independent isolated-prefill lead, not KV quantization. Lossy int8 Q/K is a distinct kernel setting. Summary lacks exact historical artifact/build and request bundle; current script is not proven identical to that experiment. PLD is separately default-on, so `--no-mtp` alone does not establish all speculative decoding is disabled. |

The two Kapitsa cells total **60 coding responses, 12 cold prefill records and 36
sweep requests**. The audit checks response medians and the identity
`prefill_tps = prompt_tokens / ttft_s`; it does not reconstruct unrecorded token-event
timestamps. For Flash-Next the archived clean harness excludes the first 16 and last
four tokens of decode. It uses character-proportional token allocation when chunks
contain multiple tokens (`rate_method: chars`). Full-generation and whole-request
rates are separately recorded; they must not be substituted silently. October's
dirty harness cannot be reconstructed from November's clean source.

The November README expressly says only Kapitsa was rerun. Other Flash-Next engine
cells retain their October 18 date, different sessions and power modes. They are not
an interleaved November head-to-head. `machine.json` was captured after the runs;
its `binary_sha256` is null and the source note says the historical binary was not
kept. A source commit is recovered; a verified exact executable is not.

For oMLX, [6ll10w10](https://omlx.ai/benchmarks/performance/6ll10w10) explicitly enables
TurboQuant KV at four bits and adaptive maximum MTP depth six. It also enables
thinking and forced sampling. In contrast, `t9sos5mz` and `b0zessb6` disable
TurboQuant but do not declare the live cache tensor dtype in their raw settings or
an explicit MTP depth there. `max_tokens` and `max_context_window` are caps, not
actual generated/occupied counts. In `t9sos5mz`, selected benchmark peak 83.2 GB,
session process footprint peak 94.04 GB and MLX active peak 82.76 GB are distinct
metrics. They are not interchangeable KV estimates.

## Conditional context-shape diagnostic

There is now an independent source curve against which to inspect the existing
`delta_ctx` shape without inventing a uniform quantization. Divide each Heretik
decode rate by its observed 33.0 TPS zero-depth baseline, and compare with the
unchanged local helper's normalized factor. This cancels the modeled amplitude;
it does not validate bandwidth, active-weight bytes or engine efficiency.

| Occupied depth | Source TPS | Observed fraction of baseline | Existing delta factor | Baseline-anchored TPS | Overprediction |
|---|---:|---:|---:|---:|---:|
| 0 | 33.0 | 1.000 | 1.000 | 33.00 | anchor |
| 4096 | 30.7 | 0.930 | 1.000 | 33.00 | 7.5% |
| 16384 | 27.9 | 0.845 | 0.945 | 31.19 | 11.8% |
| 32768 | 24.8 | 0.752 | 0.890 | 29.37 | 18.4% |
| 65536 | 23.0 | 0.697 | 0.745 | 24.59 | 6.9% |
| 131072 | 17.0 | 0.515 | 0.600 | 19.80 | 16.5% |
| 262144 | 10.9 | 0.330 | 0.500 | 16.50 | 51.4% |

This source loses more speed at long depth than the current generic curve predicts
when anchored this way. That is a diagnostic discrepancy, not a strict calibration
failure assigned to a deployment: one trial per depth, mixed quantization, mmap,
system memory pressure and the selected source/backend remain confounders.
The baseline/source were selected after inspection, so this is not blind held-out
validation. There is no strict MAPE, fitting or coefficient change.

## Demonstrated report corrections

C-065 through C-069 in [the ledger](../specs/07_DATA_CORRECTIONS.md) preserve old and
corrected interpretations. The submitted report itself remains unchanged.

- **Hardware/workload attribution:** the reported 103.9 / 97.3 / 96.6 / 89.1 TPS
  are MacStories **M3 Ultra code** results, not M5 Ultra results. Correct M5 Ultra
  prose: **111.6 / 100.0 / 95.2 / 86.8**; code: **142.9 / 132.6 / 122.8 / 119.0**,
  in oQ4e/oQ5e/oQ6e/oQ8e order. MTP depth three; Q6/Q8 embedding tables on SSD.
  Q4 is a later nine-prose / three-code retest, the others three-run medians.
- **Memory phase:** 134 / 153 / 101 / 130 GB are M5 loading peaks. Sampled
  answering process peaks are **155 / 179 / 156 / 187 GB**. Neither is weights-only
  or KV-only memory. The later Q5 memory pass is not its timed performance session.
  Both corrections use the already archived [MacStories article](https://www.macstories.net/stories/m5-ultra-mac-studio-review-the-dream-mac-for-local-ai-agents/).
- **oMLX cache precision:** disabling TurboQuant is insufficient evidence for the
  claimed FP16 live dtype; keep that field unknown for `t9sos5mz`/`b0zessb6`.
- **Sushi rate/context:** 17.34–17.88 ms/forward reciprocals are derived forward-meter
  rates, not measured end-to-end decode TPS at 128K occupied context. The nearby
  `ctx 131072` setting does not establish that the forward meter occupied that depth.
- **Heretik full fill:** approximately 28 minutes is obtained by integrating the
  measured incremental curve, not a recorded one-shot 262K cold-prefill timer.

## Inherited findings and remaining acquisition

The revision has 13 headline rows. Rows 1–3 are the new Heretik/oMLX/Sushi-Kapitsa
groups examined above; the supplemental mlx-serve lead is also examined. Rows 4–13
reuse the first review's primary Strata, Fortunato, TensorFold, Surogate, MacStories,
Mac-mini and API assessments, with the new MacStories corrections here. No new video
transcript/capture files or companion JSON file accompanied this revision, so its
claimed verified video extraction is not independently established by the input.
MTPLX's additional numerical ladders and the 350K Reddit narrative are retained as
unverified new leads, not asserted as independently checked measurements here.

The earlier TensorFold boundary still applies despite v1.1 section D's renewed
grouping: five configured 262K slots and five short-prompt requests do not establish
five simultaneously occupied 262K contexts. The Surogate eight-agent TTFT for a
different model cannot be assigned to Flash-Next. Reuse those archived sources;
do not reacquire or merge distinct runs to fill missing metadata.

Next useful acquisition is exact run-linked packs/configuration and live cache
dtype for non-MTP resident measurements; original request events/server isolated
timers for new leads; and exact INT2/INT3 tool-eval runs under the requested workload.
No benchmark machine is available. Exact M5 Max five-request / 128K loaded latency,
M5 Ultra 512 GB results, validated offload and workload-matched API events remain
missing. Shared serving/catalog extension stays U-07, separately scoped.

Strict coverage remains **zero comparable observations / 13 existing exclusions /
MAPE n/a**. The 13 headline report groups are not those 13 production observations.
U-02 through U-06 remain open. No production code/data, coefficients, default workload
or simultaneous-capacity policy changed. Reuse the passed engine 0.1.4 combined
verification; only new evidence integrity/continuity checks are required. Preserve
all prior staging, unrelated files, source archives and logs. Never commit or push.

Verification: 34 archived input/source hashes and lengths passed; submitted bytes
equal the Downloads original; local review links resolve; `git diff --check` passed.
The changed-document continuity suite passed all 33 tests. No application/frontend/
browser suite was rerun and no inference, paid API call or weight download occurred.
