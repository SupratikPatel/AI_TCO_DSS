# Review of the supplied YouTube-agent benchmark report

Reviewed 2026-11-12. The supplied report contains useful new primary-source leads
and several recoverable numerical results. It advances the public-evidence work;
it does not complete strict calibration or validate the current one-user winner.

The input is preserved byte-for-byte in
[the review archive](evidence/user_report_review_2026-11-12/ai_deployment_benchmark_evidence_report.md).
Its [manifest](evidence/user_report_review_2026-11-12/manifest.json) records the input
hash and 23 newly acquired remote files, with retrieval metadata and hashes. GitHub
and dataset files are pinned to revisions. These 24 files are separate from the
earlier archives. The source file in Downloads was not edited. External Python was
archived as `.py.txt` and was not executed; no inference or paid API calls occurred.

Scope: this review/archive, correction ledger, evidence matrix and continuity docs.
No production observations, catalog values, coefficients, schemas or code changed.
Engine 0.1.4 and simultaneous resident capacity remain settled. Existing software
verification is reused; empirical U-02 through U-06 remain open.

## What the primary sources establish

### M5 Max: genuine low-bit measurements, incomplete execution identity

Pinned [Strata MAC.md](https://github.com/Niko1221/Strata/blob/c1ff07f1a1817594811c960039571c6e268fe89a/docs/MAC.md)
confirms these source-reported single-request rates over 200 generated tokens:

| Artifact family | No-MTP short / story TPS | MTP short / story TPS, suffix off |
|---|---:|---:|
| Q2_0 | 87.4 / 87.3 | 114.0 / 107.9 |
| IQ3_XXS | 78.7 / 78.6 | 103.5 / 96.9 |
| IQ3_S, first table | 74.5 / 74.3 | 98.2 / 94.1 |
| IQ3_S, separate table | 75.4 / 74.8 | 101.9 / 94.7 |
| UD-Q4_K_XL | 60.7 / 59.7 | 94.0 / 73.7 |

Keep the two IQ3_S tables separate; no repetition statistics establish an average
across them. The primary explicitly leaves the engine version unrecorded. Prompt
counts for these short/story decode runs, live KV dtype, run-linked artifact hashes
and complete cache/protocol identity are unresolved. Its approximate 4K/32K needle
rates are described using a first-token boundary, so isolated prefill is unproven.
The source does not establish exact 4,096/32,768 occupied tokens merely by writing K.

It also reports one-to-four simultaneous requests at configured context 36,864,
150 generated tokens each, using IQ3_S with MTP. This is useful concurrency evidence,
but does not establish five requests with 128K occupied context on the Max. The
8.3/12.0/14.0/16.0 GB figures describe engine memory, not a KV-only pool.

The n-gram table stays on SSD even when GPU-mapped model weights are resident.
Preserve that placement when comparing with a generic resident formula. Q2_0,
IQ3_S and NVIDIA FP4 are distinct artifacts; generic INT2/INT3/INT4 labels do not
make them interchangeable with catalog candidates. The new quality comparisons
against Q8_0 provide artifact-specific agreement/KL evidence, not an agent-task
accuracy score or proof that the application's quality floor is met.

### DGX Spark: measured serving evidence with explicit latency limits

[Fortunato's pinned recipe](https://github.com/devopsfortunato/Qwen3.8-Flash-Next-FP4-Local-DGX-Spark/blob/6aab1a5589dfd0cd93cb0ffc8d50392cfaffa9b6/README.md)
confirms two distinct long-prompt experiments:

| Requests | Actual input tokens each | Output tokens each | KV pool | Last first token |
|---:|---:|---:|---:|---:|
| 5 | 246,388–253,222 | 3,000 | **27 GB** | 652 s |
| 6 | 252,700–253,222 | 3,000 | **31.15 GB** | 790 s |

Both reportedly decoded together without preemption. Prompt processing was serial,
which explains the long last-request TTFT. Capacity and loaded latency are separate
observations. These are NVIDIA FP4/vLLM conditions, not the app's modeled INT2 Mac.
Historical speed tables in this changing recipe must retain their own engine/image
and settings; the latest README configuration cannot identify every earlier run.

[TensorFold's pinned recipe](https://github.com/MiaAI-Lab/Qwen3.8-Flash-Next-Single-DGX-Spark-TensorFold/blob/20e15e41f2f514a0d287710f4665ee1b5009ba41/README.md)
confirms five-stream prose/code figures and a separate cold-prefill ladder. The
short-prompt five-stream table reports 35.0 TPS per request / 156.1 aggregate for
prose and 48.0 / 217.6 for code. Preserve the published columns; absent individual
records, do not infer their aggregation by multiplying the representative per-request
figure. The README identifies a sparkDash timer and warns that the separately supplied
`tools/bench_streams.py` uses different prompts/settings. Do not assign that script's
repetition count to the sparkDash table. Configured 262,144 per slot is not evidence
that these decode requests each occupied 262K. The 199,730-token needle's 100.7 s is
a first-token/prefill duration; dividing the two produces an estimate, not an
independent isolated-prefill observation.

[Surogate's pinned benchmarks](https://github.com/invergent-ai/surogate/blob/c7df4bafb41129da88ab5ba82fa84037be7b5ee7/surogate/serve/BENCHMARKS.md)
confirm low-bit Flash-Next serving results, including different MTP builds. The
eight-agent warm TTFT of 1.88/2.53 s belongs to **Surogate3.7-35B-A3B NVFP4**, not
Flash-Next. Warm turns reuse cached conversation state. Its public harness can
write per-turn JSONL, but this review acquired the harness and summary, not the
original per-turn logs. The supplied report separates these models in its detailed
section; preserve that distinction when extracting its combined headline row.

### Mac mini: three different workloads, not interchangeable samples

The [pinned SmartyPants dataset](https://huggingface.co/datasets/smartypantsnet/mac-benchmarks/tree/7f03fc28d323f5043a0b40e07d69d43833e56372)
confirms Qwen 27B baseline rates of 35.7 TPS for short chat, 17.8 TPS for the
200-problem GSM8K comparison and 17.7 TPS for full GSM8K. These use different
prompts/output lengths. Its `results.json` is a structured summary; the source
states that full result files remain on the operator's Mac. Memory measured during
a 4,096-token prompt does not identify the short-chat speed prompt. Exact per-request
counts, timing samples, live cache state and complete runtime identities were not
recovered. The linked Reddit subseries was not independently verified here.

### API performance: useful production evidence, no matched workload yet

[Requesty's primary report](https://www.requesty.ai/blog/gpt-vs-claude-vs-gemini-api-price-latency)
confirms these production-streaming statistics for September 7–November 9, 2026:

| Model | Median TTFT | P95 TTFT | Reported output TPS |
|---|---:|---:|---:|
| Sonnet 5.5 | 2.786 s | 20.158 s | 200 |
| Opus 5.5 | 3.712 s | 16.036 s | 140 |
| GPT-6.1 Sol | 4.041 s | 18.276 s | 71 |

This improves U-06's external evidence coverage. Request mixes and cache rates
differ; model-level medians do not identify one fixed endpoint/region/revision,
prompt/output count and offered load. The separate coding-task results use another
protocol. Do not combine medians into a claimed measured whole-request latency.
OpenRouter ranges and the report's Gemini 3.1 Pro preview figures were not independently
snapshotted in this review; retain them as leads. No matched API lookup was added.

## Corrections to the supplied report

| Ledger | Submitted interpretation | Primary-source correction |
|---|---|---|
| C-061 | Strata Mac needle rates are isolated prefill; decode baseline is uncached | First-token boundary is described; uncached decode protocol and engine version are not established. Keep those fields unknown |
| C-062 | 8.3–16.0 GB is KV/state memory | These are total engine figures; source separately reports 0.65 GB per-sequence state/KV at configured 36,864 |
| C-063 | MacStories prompt series is a median of three; output count unknown | Original article identifies single runs per size and exactly 512 generated tokens; three-run medians belong to another session |
| C-064 | Fortunato five/six long-context experiments share the 31.15 GB pool | Five-request experiment belongs to earlier 27 GB pool, six-request experiment to 31.15 GB |

The [MacStories primary article](https://www.macstories.net/stories/m5-ultra-mac-studio-review-the-dream-mac-for-local-ai-agents/)
was rechecked because the supplied report contradicted its saved protocol. The
existing five production observations already preserve its actual prompts/output
counts; they need no rewrite. KV/runtime-artifact blockers remain unresolved.

Video timestamps are useful leads, but the supplied Markdown contains no captured
transcripts, screenshots or original video logs for independent checking. Its
references to a structured JSON record are not accompanied by a JSON block/file.
The alleged Tom's Hardware comparison links to secondary retellings; its primary
run was not identified here. These are verification limits, not proof that the
videos or claims are false. Hardware attribution changes such as the claimed
M4 Pro correction remain unverified until original video evidence is recovered.

The separate DeepSeek Mac traffic measurements were made while an idle 60 GB Qwen
server shared that machine's cache. Their 48/111 MB-per-token values cannot supply
RTX 5070 traffic inputs. Pack recipes and current defaults also cannot retroactively
establish the original 4.7 TPS run's build, prompt, KV or drafter state.

## What remains and what can now be used

Use the verified primary tables as qualified deployment/serving evidence and retain
their errors, workload differences and missing fields. They demonstrate that runtime,
quantization, cache reuse and load materially affect performance. They narrow the
next acquisition to original raw logs and commands rather than more headline rates.

The [machine-readable review](evidence/user_report_review_2026-11-12/review_audit.json)
assesses all twelve headline rows, retains corrected run facts and separates confirmed
primary data from unverified video/secondary claims. No strict formula observation
was admitted. The resident rows lack necessary run identity or use unsupported exact
quantization/speculation; concurrency/agent/API evidence validates different aspects
and conditions. Strict comparable coverage remains zero, 13 existing exclusions,
MAPE n/a. This does not erase the useful new serving evidence.

Highest-value remaining items are the original M5 Max commands/build, cache/KV and
actual prompt logs; original DGX request/stream logs; the SmartyPants full operator
results; API request events with conditions; and original timestamped video captures.
The author has no benchmark machine, so no controlled local run is scheduled. U-05's
five-request / 128K Max case and exact-artifact tool quality remain unvalidated.

The [integrity record](evidence/user_report_review_2026-11-12/integrity_verification.json)
confirms all 24 archive hashes/lengths, unchanged original input, twelve reviewed
rows, eleven primary-text checks and three dataset-condition checks. All 33
session-continuity checks pass after these documentation/ledger updates. No numerical
or browser suites were repeated. Relevant files are staged alongside preserved
earlier work; no commit or push.
