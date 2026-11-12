# U-02 public evidence acquisition — 2026-11-11

**2026-11-12 continuation:** [new run-fact recovery](U02_RUN_FACTS_CONTINUATION_2026-11-12.md)
adds a separate 34-file archive, twelve audited Qwen 27B llama-bench rows with
isolated cold-prefill timers, published harness history and partial same-run Strata
storage counters. Dynamic quantization and missing original run manifests still
prevent strict calibration. The MLX dtype/dirty-harness gap remains open. The
35-file archive and six conditional diagnostics described below are preserved.

New primary material is archived under
[`evidence/public_benchmarks_2026-11-11/`](evidence/public_benchmarks_2026-11-11/manifest.json).
The manifest records retrieval times, URLs, byte counts and SHA-256 hashes for 35
retrieved files. Archive-local `.gitattributes` disables text normalization; all 35
staged source blobs were checked against the raw-download hashes. External Python
source is retained as `.py.txt` for inspection and
was not executed. Only a safetensors header was retrieved; no model tensor payload,
inference run or paid API call was performed. Scope: this evidence archive/report,
the evidence matrix, correction ledger and continuity documents. The separate
author-approved U-05 policy change is documented in [the policy report](PEAK_CAPACITY_POLICY.md).

## Original evidence recovery

The Jundot model's [commit-history API](https://huggingface.co/api/models/Jundot/Qwen3.8-Flash-Next-oQ4e-mtp/commits/main)
returned only revision `2322c888c2c314d4eceddf0159dec5d821aa1e41`, dated 2026-10-29,
with a re-quantization title. This is a new history investigation, not a repeat of
the saved failing revision probe. It does not establish why the article-linked
revision is missing or recover its original tensors/settings. No current weights
were substituted for the MacStories run. Its KV/kernel facts remain missing.

The original pinned Strata DeepSeek document and the current upstream-head copy
are byte-identical in the archive. The separate benchmark protocol and Qwen result
directories add no run-specific facts to the original DeepSeek 4.7 TPS observation.
Its actual prompt/output, build/artifact, drafter/KV/cache/load and timing protocol
remain unresolved. No prompt was transferred from a different run.

## New resident evidence: a different Mac operator and model

[tristanbes/m5-ultra-llm-bench](https://huggingface.co/datasets/tristanbes/m5-ultra-llm-bench/tree/cb78e33292442f8f6f430dd3a3b9acdef4fe9707)
is pinned at `cb78e33292442f8f6f430dd3a3b9acdef4fe9707` and licensed CC BY 4.0.
Its 192 long-context rows retain successes, warnings and failures. The six selected
rows below are Qwen 3.8 27B, MLX, source KV label `f16`, three trials each, on an
80-core M5 Ultra with 256 GB. They use random input and 128 generated tokens;
they do not measure the Flash-Next INT2/INT3 recommendation. All six retain the
source model revision, runtime versions, individual samples and environment fields.

| Fact | Source-backed status | Admission consequence |
|---|---|---|
| Model | `mlx-community/Qwen3.8-27B-4bit`, revision `10c35caafbb80f7dc6a7a432cdd11af10a6d4818`; pinned config and tensor index acquired | Distinct from the missing Jundot artifact |
| Quantization | Config reports affine 4-bit/group 64, without per-module overrides | Keep this identity; do not relabel GGUF dynamic quants as uniform INT4 |
| Hardware/runtime | Source reports 256 GB/80 GPU cores; mlx-lm 0.32.2, MLX 0.32.4 | Source-reported, not independently replicated |
| Cache/speculation/load | Archived runner and versioned upstream call path create fresh request caches, one serial stream, no draft model | Code-supported inference about this protocol, not an observed scheduler trace |
| KV dtype | Rows say `f16`; checkpoint config says BF16 and its first-shard header contains BF16 scales/norms | Unquantized 16-bit cache is plausible; an actual FP16/BF16 cache trace was not captured. Do not silently promote the source label to a verified dtype |
| Harness identity | Rows report `1025283-dirty`; acquired dataset snapshot is later | Exact historical dirty worktree is unavailable |
| Prefill denominator | Upstream timer includes first-token forward/sampling | Not isolated input-processing TPS; no prefill admission |
| Generation denominator | Upstream starts timer after first token, reports 128 tokens across 127 intervals | Preserve native rate; show a separately derived 127/128 count normalization |

The checkpoint header is metadata, not a captured live cache. It does not by itself
prove a wrong source KV label. Its bytes are retained with the HTTP range in the
manifest so the uncertainty can be investigated without downloading the weights.
The exact historical harness and live cache dtype remain strict-admission blockers.

## U-03 conditional numerical diagnostic

[`resident_diagnostics.json`](evidence/public_benchmarks_2026-11-11/resident_diagnostics.json)
retains each complete source row, raw samples, source line number, exact formula
trace, inputs, engine parameters and catalog fingerprint. Predictions use the
unchanged resident formula with measured lookup disabled, uniform INT4 and the
source's 16-bit KV label. FP16 and BF16 have the same current byte/formula treatment.
This is a conditional diagnostic, **not an admitted calibration dataset**.

| Prompt tokens | Source generation TPS | Derived interval TPS | Formula TPS | Diagnostic absolute error, % |
|---:|---:|---:|---:|---:|
| 512 | 54.83 | 54.40 | 59.26 | 8.93 |
| 4,096 | 54.01 | 53.59 | 59.26 | 10.58 |
| 16,384 | 51.13 | 50.73 | 56.00 | 10.39 |
| 32,768 | 48.59 | 48.21 | 52.74 | 9.40 |
| 65,536 | 43.50 | 43.16 | 44.15 | 2.29 |
| 131,072 | 37.00 | 36.71 | 35.56 | 3.15 |

Derived interval TPS = native generation TPS × 127/128. The JSON also retains errors
against the native rates and standard deviations of transformed samples. These are
three within-machine repetitions, not six independent machines. Selection followed
source inspection; there is no blind holdout, coefficient fit or population confidence
claim. The diagnostic mean error is 7.46%, conditional on the stated representation.
It must not replace the application's strict MAPE of n/a or support Flash-Next quality,
INT2 performance, shared Mac serving or loaded latency claims.

To reproduce a row using the saved JSON and current catalog, load its `sizing_options`
and `workload_profile` into `SizingOptions`/`WorkloadProfile`, select the indicated
Mac/Qwen 27B catalog entries, and call `compute_workload`, `size_deployment`, then
`compute_performance` with an empty `BenchmarkSet` and `use_measured=False`.
Compare `decode_tps.value` to `formula_decode_tps`; derive the interval TPS/error
using the expression above. Parameters and catalog SHA-256 must match the saved
values. No `BenchmarkRecord` was fabricated to bypass strict eligibility.

## U-04: new offload logs, still no validated transfer model

The [upstream Strata head-to-head archive](https://github.com/Niko1221/Strata/tree/c1ff07f1a1817594811c960039571c6e268fe89a/bench/results/2026-10-06-llamacpp-0.6.0)
contains actual per-request JSONL and a saved RTX 5070 configuration. It measures
Qwen Flash-Next IQ3_XXS with speculation, not the original DeepSeek observation.
The saved rows have actual prompts of 4,052/32,056 tokens, output counts, server
timings and draft statistics. These facts belong only to those rows.

The README's headline says decode = 256 tokens; the six archived Strata rows contain
94–132 output tokens. The 256-token request setting must not replace actual output
counts (C-059). The archive reports one hardware round with limited repetitions;
it supplies no simultaneous per-tier bytes, transfer overlap and execution traces.
Its document pin is not an engine binary hash. Those gaps and mixed quantization/
enabled speculation preclude resident calibration and a validated tier-aware model.
Offload performance remains unavailable absent a matching measured path.

The other [Mac recipe's primary results](https://github.com/sethforprivacy/Qwen3.8-Flash-Next-M5-Ultra-oMLX/blob/050233efcd0a765de9963ab21a01df0723a50530/docs/RESULTS.md)
are also archived. Their oQ6e/MTP/lookup experiments and summary timing method are
different conditions; no table cell was promoted into a production observation.

## Exact remaining acquisition

1. Recover original MacStories artifact hashes and saved runtime/KV configuration.
2. For the new Qwen 27B candidate series, obtain the original dirty harness snapshot,
   commands and live cache dtype; keep the native and derived timing metrics distinct.
3. For independent prefill, acquire an isolated timer or raw event timings that
   separate prompt processing from first-token forward/sampling.
4. For offload, acquire the same-run placement/residency, active bytes per tier,
   transfer time/overlap, CPU/GPU work and uncached prompt/generation timings with
   exact binaries/artifacts. No advertised-bandwidth efficiency factor is inferred.
5. For U-05, measure exact INT2/INT3 artifacts under the approved simultaneous peak,
   including quality/tool validity, client TTFT and per-request rates. Capacity policy
   is now specified; memory capacity alone does not validate latency.
6. For U-06, endpoint/region/model revision, cache, prompt/output, offered load and
   client event timings remain missing. No paid experiments or credentials were used.

**Strict coverage remains 0 comparable decode / 0 comparable prefill, 13 existing
exclusions, MAPE n/a.** This acquisition adds inspectable primary data and conditional
diagnostics; U-02/U-03/U-04 and the empirical parts of U-05/U-06 remain open.
