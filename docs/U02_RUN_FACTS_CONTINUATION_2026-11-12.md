# U-02 run-fact recovery — 2026-11-12

**Subsequent author-supplied evidence:** see the
[YouTube-agent report review](YOUTUBE_EVIDENCE_REPORT_REVIEW_2026-11-12.md).
It adds confirmed primary serving/production API evidence and four interpretation
corrections in a separate archive. The older acquisition and blockers below remain
preserved; do not repeat its downloads or treat its earlier API search as exhaustive.

Calibration remains unfinished. This continuation adds **34 newly acquired primary
files**, twelve audited Qwen 27B source rows and partial same-run offload counters.
It changes no production observations, coefficients, contracts, capacity policy or
recommendations. Strict application coverage remains zero decode / zero prefill,
13 existing exclusions, MAPE n/a. The earlier 35-file archive and six conditional
MLX diagnostics remain intact.

Scope: this report, `docs/evidence/public_benchmarks_2026-11-12/`, the evidence matrix,
`docs/evidence/api_measurement_search_2026-11-12/`, acquisition report, unfinished
backlog and session-continuity documents. These are
evidence/documentation changes; no application implementation or task completion
is claimed. Existing engine 0.1.4 verification remains applicable.

## Recovered independent prefill timing

The previously archived dataset inventory identifies raw files not acquired in the
prior session. The new [manifest](evidence/public_benchmarks_2026-11-12/manifest.json)
records URLs, resolved URLs, retrieval timestamps, byte lengths, HTTP statuses and
SHA-256 for all 34 new downloads. No earlier download or failed model-revision probe
was repeated. External source code is stored as `.txt` and was not executed.

Twenty-four files are Qwen 27B llama-bench raw logs, pinned to the same
[dataset revision](https://huggingface.co/datasets/tristanbes/m5-ultra-llm-bench/tree/cb78e33292442f8f6f430dd3a3b9acdef4fe9707).
They cover six prompt depths and two KV formats (`f16`, `q8_0`). Each pair contains
one cold-prefill record and two separate depth records: 2,048-token prefill at depth,
and 128-token decode at depth. All 36 records retain three nanosecond samples.

The raw build is `9125a2ebe` / b11896. Logs record Metal/BLAS, GPU layers 99, CPU-MoE
layers 0, batch/microbatch 2,048, flash attention on and the actual K/V type. Hardware
capacity and artifact repository/revision still come from the source summary, not
the raw timer. The runner records `1025283-dirty`; no original binary/artifact hashes
were recovered.

The newly archived [b11896 timer source](https://github.com/ggml-org/llama.cpp/blob/b11896/tools/llama-bench/llama-bench.cpp)
clears sequence memory before repetitions and prepares/restores depth before the
timed region. `test_prompt` processes random token IDs and synchronizes; `test_gen`
processes and synchronizes one random token at a time. Cold prefill has `n_gen=0`
and `n_depth=0`, so its timer contains no generated-token sampling. This resolves
the isolated-prefill timing-definition gap **for these llama-bench runs**. It does
not resolve the separate MLX first-token-inclusive timer or measure serving TTFT.
Code supports this interpretation; the original binary was not independently rebuilt.

| Prompt/depth | Cold prefill, f16 TPS | Cold prefill, q8_0 TPS | Decode at depth, f16 TPS | Decode at depth, q8_0 TPS |
|---:|---:|---:|---:|---:|
| 512 | 1,127.10 | 1,125.64 | 48.61 | 47.25 |
| 4,096 | 1,322.95 | 1,318.82 | 47.95 | 45.87 |
| 16,384 | 1,234.34 | 1,225.02 | 45.35 | 43.86 |
| 32,768 | 1,125.24 | 1,114.64 | 42.40 | 40.93 |
| 65,536 | 930.72 | 942.54 | 37.09 | 36.01 |
| 131,072 | 717.52 | 718.79 | 30.15 | 28.96 |

The [machine-readable audit](evidence/public_benchmarks_2026-11-12/run_evidence_audit.json)
contains each full source row, original line number, raw file/record, samples and
admission reasons. Every raw mean exactly equals its source-summary metric.
Recomputed sample rates use `tokens * 1e9 / nanoseconds`; means use unrounded rates.
The upstream `%g` sample output has six significant digits, while `avg_ts` has six
decimal places. Those distinct rounding rules were checked, not treated as a data
discrepancy. No 127/128 MLX normalization applies to these llama-bench samples.

Recheck the archive and derived rates from the repository root without inference:

```python
import hashlib, json, statistics
from pathlib import Path

root = Path("docs/evidence/public_benchmarks_2026-11-12")
manifest = json.loads((root / "manifest.json").read_text())
for item in manifest["files"]:
    data = (root / item["path"]).read_bytes()
    assert len(data) == item["bytes"]
    assert hashlib.sha256(data).hexdigest() == item["sha256"]
audit = json.loads((root / "run_evidence_audit.json").read_text())
for row in audit["raw_resident_rows"]:
    for raw in row["raw"]:
        records = [json.loads(s) for s in (root / raw["path"]).read_text().splitlines()]
        assert records == raw["records"]
        for record in records:
            tokens = record["n_gen"] or record["n_prompt"]
            rates = [tokens * 1e9 / ns for ns in record["samples_ns"]]
            assert [float(format(r, ".6g")) for r in rates] == record["samples_ts"]
            assert abs(statistics.mean(rates) - record["avg_ts"]) <= 0.00000051
```

**Admission decision:** these are independent isolated-prefill observations, but
`UD-Q4_K_M` is a dynamic GGUF quantization, not the formula's uniform INT4. Original
dirty-worktree and run-linked artifact hashes are also absent. No application query
establishes an exact protocol match for measured lookup. Do not manufacture uniform
`BenchmarkRecord` conditions or include these rows in strict MAPE. An independent
timer alone does not establish formula comparability. No coefficients were fitted.

## Historical harness recovery result

The new [dataset history API response](https://huggingface.co/api/datasets/tristanbes/m5-ultra-llm-bench/commits/main)
contains four published commits. Neither identifies the `1025283` base. Two earlier
published `bench.py` snapshots were acquired. The 2026-10-27 snapshot is byte-identical
to the already archived 2026-10-30 runner; the 2026-10-23 snapshot is an earlier,
smaller implementation. Published snapshots do not recover uncommitted changes or
prove the runner used for the long-context measurements. The new history investigation
therefore leaves the original MLX dirty harness and live FP16/BF16 cache dtype open.
No repeated Jundot revision probe or substitute weights were used.

## Offload: useful same-run component inputs, incomplete model validation

New source-operator reports and their complete available comments are archived from
[Strata #3942](https://github.com/Niko1221/Strata/issues/3942),
[#4074](https://github.com/Niko1221/Strata/issues/4074) and
[#4170](https://github.com/Niko1221/Strata/issues/4170).
Their facts belong to their own runs, not the original RTX 5070 / 4.7 TPS observation.

| Source | Acquired evidence | Remaining barrier |
|---|---|---|
| #3942, RTX 5090 D v2 | Prompt counts, cold client TTFT, setup flags, 0.1.49 package, reported store size | Prefill/TTFT columns alone do not establish independent isolated prefill; actual drafter state questioned by author; no raw request timing bundle |
| #4074, three V100s | Source build, hardware, startup placement, store residency and approximate CPU-lane share | Headline rates explicitly use generated tokens / whole wall time; cannot relabel them pure generation TPS. Exact prompts, live KV/drafter state and raw traces missing |
| #4170 opening report, RTX 5090 | Same-run disk counter windows, repeated/fresh prompt separation, startup residency, build and launch settings | Summary counters, not per-layer timing/overlap or exact prompt/artifact/output manifests |
| #4170 direct-run comment, RTX 5070 Ti | One greedy 256-token input, three interleaved repetitions per setting, per-token bytes/misses/store wait, physical drive-slot change | Raw input IDs, complete run logs, live KV/speculation state, exact binary/pack hashes and overlap traces absent |

The [RTX 5070 Ti operator's direct-run comparison](https://github.com/Niko1221/Strata/issues/4170#issuecomment-6515508984)
uses a source build at `dfbd8342`, 16 GB VRAM, 64 GB RAM, a 24 GB store and five
active experts. Moving the same SN850P drive from PCIe 3.0 x4 to 4.0 x4 reportedly
changes median decode from 6.91 to 9.55 TPS and store wait from 87.3 to 45.4 ms/token,
at 260.7 MB read/token in both conditions. These are reported medians, not retained
individual runs or a blind validation set.

An inspectable **component diagnostic**, using the operator's separate drive test:

| Drive link | Drive-test MB/s | Ideal transfer ms/token: 260.7 / rate × 1,000 | Reported store-wait ms/token |
|---|---:|---:|---:|
| PCIe 3.0 x4 | 3,265 | 79.85 | 87.3 |
| PCIe 4.0 x4 | 7,100–7,212 | 36.15–36.72 | 45.4 |

This calculation is not an end-to-end prediction or a proven bandwidth bound: a
drive microbenchmark does not prove the application's sustained service rate, and
wait can overlap compute. It uses no invented efficiency factor. It shows why bytes,
service time and overlap must be measured together; peak VRAM/NVMe bandwidth alone
cannot supply missing CPU/GPU critical-path time. The opening RTX 5090 report instead
describes low disk queue depth; its counters cannot be transplanted to this machine.

The [later six-run follow-up](https://github.com/Niko1221/Strata/issues/4170#issuecomment-6518623523)
reports two output hashes: baseline round 2 and split round 3 differ from the other
four runs. That caveat belongs to the later batch; it does not prove the earlier
reported identical-output batch was false. Preserve this variability rather than
assuming matched outputs across all experiments. Raw hash values/IDs are absent.

**Admission/model decision:** retain these component facts as external evidence.
They are not a validated offload model, strict observations, evidence for the original
DeepSeek row, or support for the Flash-Next INT2/INT3 recommendation. Production
offload performance stays unavailable without a matching measured path. U-04 is open.

## U-06: additional public API search

The [supplemental seven-response archive](evidence/api_measurement_search_2026-11-12/manifest.json)
records one successful primary report retrieval and six HTTP 404 responses. Search
rendering exposed [Sonnet](https://www.llmverifications.com/models/claude-sonnet-5-5)
and [Gemini](https://www.llmverifications.com/models/gemini-3-1-pro-preview) summaries
claiming streamed measurements. Direct HTTP retrieval of both model pages, the linked
methodology/downloads pages, and the linked Opus/GPT Sol pages returned 404. The
rendered/direct-response discrepancy is unresolved; no downloadable request events
or complete endpoint/region/cache/load protocol were acquired. Search summaries are
not a replacement for raw records. No performance values were imported from them.

The independently accessible
[HolmesGPT 2026-10-21 report](https://holmesgpt.dev/latest/development/evaluations/history/results_20261021_072130/)
includes all four model families with reasoning-effort labels, task results, costs
and whole-task latency summaries. It evaluates Kubernetes/cloud troubleshooting.
Those elapsed task times do not establish per-request first-token latency, generation
intervals or the DSS workload's cache/concurrency/region conditions. This is evidence
of a different agent workload, not missing TTFT/decode data that can be filled by
dividing task duration or treating every task as one request. U-06 remains open;
missing comparable evidence still does not mean measured API failure.

## Concrete measurement handoff

**The author confirmed that no benchmark machine is available.** No original
operator worktree, comparable API event bundle or paid-run authorization was
established. No inference/paid API run was performed. The next useful work requires:

1. **MLX resident:** original dirty worktree plus command/environment and live K/V
   tensor dtype; otherwise a new clearly identified controlled run, retaining model
   and binary hashes, random input IDs/seed, empty-cache procedure, isolated prefill
   boundaries, generation intervals and every trial/failure. Do not backfill old rows.
2. **Offload:** obtain #4170's original direct-run bundles or independently record
   exact input/output IDs and hashes, actual KV/drafter state, per-token demand/read
   bytes, CPU/GPU work, residency and transfer/compute overlap for each repetition.
   Keep drive microbenchmarks separate. Fix fitting/held-out prompts and hardware
   conditions before evaluating a candidate model; summary medians are insufficient.
3. **One-user winner:** use the saved engine 0.1.4 baseline, exact INT2/INT3 artifacts,
   five simultaneous requests at target context and eight retained agents. Record
   per-request client TTFT, inter-token/whole-request rates, actual prompt/output
   lengths, cache state and agent/tool correctness. Memory fit is already implemented;
   quantization-specific quality and loaded latency remain unvalidated.
4. **APIs:** original request/stream event logs with endpoint, region, model revision,
   cache behavior, actual token counts, offered load and client timing boundaries for
   all four alternatives. Credentials or model-card marketing do not supply measurements.

U-02/U-03/U-04 and the empirical portions of U-05/U-06 remain open. U-07/U-08 remain
separate scopes. Reuse saved software verification; do not rerun application/browser
suites for this evidence-only continuation.

## Verification and saved state

[Integrity proof](evidence/public_benchmarks_2026-11-12/integrity_verification.json)
records successful SHA-256/length verification of 34 primary files and seven API
responses, exact source-row/raw-record reconciliation, and all 108 sample-rate
checks. All 33 session-continuity checks passed after checkpoint updates. Application,
numerical and browser suites were not rerun; no application changes justify them.
Relevant evidence/docs are staged for review alongside preserved earlier staging.
No commit or push. No empirical U task was marked complete.
