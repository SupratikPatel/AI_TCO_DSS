# U-02 benchmark evidence matrix

**Latest enterprise/router analysis, 2026-11-12:** read
[ENTERPRISE_SCALE_AND_ADAPTIVE_ROUTING_2026-11-12.md](ENTERPRISE_SCALE_AND_ADAPTIVE_ROUTING_2026-11-12.md)
for the author's 1050-user observation and two supplied posts. Reproduced no admission
at 1050 with enterprise defaults and the saved self-managed profile: last eligible
candidate has formula capacity 1010.5049 users, not a 1000-user input cap. The domain
and frontend accept 100000. The USD 100000 CapEx cap and missing API latency evidence
also constrain results; presets run after hard filters. Eight new scenarios and two
budget-only counterfactuals are saved separately. Revolut's shared fleet and Pi's
adaptive routing expose explicit replica/scheduler/router gaps beyond the existing
static Hybrid Split. Six primary responses are hashed; the report contains the
focused external-agent fetch request. No production changes or passed app/browser
reruns; capacity policy and strict calibration status remain unchanged. Continue the
latest 512 GB evidence review for core calibration. Preserve all staging/unrelated
files and logs; never commit or push.

**Latest 512 GB evidence checkpoint, 2026-11-12:** read
[M5_ULTRA_512GB_EVIDENCE_REVIEW_2026-11-12.md](M5_ULTRA_512GB_EVIDENCE_REVIEW_2026-11-12.md)
after the saved handoff/backlog. Official Apple specs and dated USD 22299 (1 TB) /
29799 (16 TB) offers now verify the 36-core CPU / 80-core GPU / 512 GB target.
Thirteen acquired oMLX records report 512 GB; Qwen Q6 at 131072 input reports
28.250 s TTFT / 102.3 TPS with fixed MTP depth 3. Apple supplies independent 512 GB
native-precision measurements. Four original quality logs reconcile 2647 questions.
A new archive preserves the input and 42 remote responses, including explicit blocked/
empty captures. C-070 through C-075 correct six report interpretations. Earlier
statements that no 512 GB measurements were acquired are historical and superseded.
Five simultaneous 128K requests, eight resident sessions and exact low-bit tool
validity remain missing in inspected evidence. No 512 GB catalog/shared-serving
implementation, production import, coefficient or capacity-policy change. Strict
coverage remains zero / 13 existing exclusions / MAPE n/a; no U task closed.
Reuse existing engine 0.1.4 verification and all archives. No benchmark machine;
preserve staging/unrelated files and logs; never commit or push.

**Latest v1.1 report checkpoint, 2026-11-12:** read
[YOUTUBE_EVIDENCE_REPORT_V11_REVIEW_2026-11-12.md](YOUTUBE_EVIDENCE_REPORT_V11_REVIEW_2026-11-12.md)
first after the saved handoff/backlog. A separate 34-file archive preserves the revised
input and 33 new primary remote files. Reconciled 60 Kapitsa coding responses,
12 cold prompt/TTFT records and 36 sweep requests; oMLX JSON is settings, not request
events. Added a conditional Heretik context-shape diagnostic (128K +16.5%, 256K
+51.4% overprediction after anchoring the baseline), not strict MAPE or fitting.
C-065 through C-069 correct M3-as-M5 attribution, loading-memory phase, unsupported
FP16 cache, forward-meter interpretation and integrated full-fill timing. No M5 Ultra
512 GB measurements or Max five-request / 128K logs acquired. Strict coverage remains
zero / 13 existing exclusions / MAPE n/a; no production data/code, coefficients,
capacity policy or task status changed. Reuse prior engine 0.1.4 verification and all
archives. No benchmark machine available; preserve staging/unrelated files, never
commit or push.

**Latest supplied-report review:** [YouTube-agent evidence review](YOUTUBE_EVIDENCE_REPORT_REVIEW_2026-11-12.md)
preserves the author's report and verifies new primary Mac, DGX and API sources
against pinned snapshots. C-061 through C-064 correct timing, memory, repetition
and KV-pool attribution. This adds qualified serving evidence, including confirmed
DGX concurrency; original strict admissions remain zero. No metadata was transferred
between runs or imported into production benchmarks.

**Latest acquisition, 2026-11-12:** [run-fact continuation](U02_RUN_FACTS_CONTINUATION_2026-11-12.md)
and [full row/raw audit](evidence/public_benchmarks_2026-11-12/run_evidence_audit.json).
Twelve Qwen 27B llama-bench rows now have independent isolated-prefill raw samples,
actual K/V formats, runtime build and generation-at-depth timers. They use dynamic
UD-Q4_K_M, outside the current uniform-bit calibration model; original dirty harness
and run-linked artifact hashes remain missing. Three new Strata operator reports
add partial residency, traffic and wait evidence, with metric/output caveats and
no validated transfer/compute-overlap model. None supplies missing facts for the
13 production observations below; all remain excluded. The original MLX live dtype
and dirty-worktree gaps remain unresolved. No new strict MAPE or coefficients.

Status: evidence audit started 2026-11-11; usable independent calibration evidence
has **not** been acquired. No catalog observations, conditions or coefficients changed.
Apply [the U-01 policy](BENCHMARK_MATCHING_POLICY.md), keeping measurement lookup
eligibility separate from formula applicability. No numbers below were measured by this project.

Continuation: [new public-source acquisition and conditional diagnostics](U02_PUBLIC_EVIDENCE_ACQUISITION.md)
archives a separate repeated Mac dataset, pinned configurations/source and Strata
raw logs with hashes. None resolves the original MacStories/DeepSeek unknowns.
Six Qwen 27B resident rows have conditional numerical diagnostics; they are not
admitted strict observations. See that report for exact remaining evidence, and
[the peak-capacity policy](PEAK_CAPACITY_POLICY.md) for the author's separate U-05 choice.

## Catalog observations

Values and historical identifiers are preserved from `data/benchmarks/decode.json`,
`prefill.json` and [the unchanged legacy copy](evidence/legacy_decode_observations.json).
`S` means source-reported; `A` means a historical assumption, not established by the run;
`?` means unknown. A reported result is not an independent replication.

| Observation / source | Reported TPS | Actual prompt | Established/inferred facts | Decision |
|---|---:|---:|---|---|
| Qwen 27B / Mac mini 64 GB / YT-18 | 14.7 | ? | A: INT4, legacy 8192 context | Exclude: L |
| Qwen A3B / Mac mini 64 GB / YT-18 | 78.8 | ? | A: INT4, legacy 8192 context | Exclude: L |
| Flash-Next / M5 Ultra / YT-21 | 108 | ? | A: INT4, legacy 8192 context; summary series | Exclude: L |
| Flash-Next / M5 Ultra / YT-21 | 61 | ? | Legacy 131072 context; rounded summary | Exclude: L |
| DeepSeek / Strata / YT-07 | 4.6 | ? | Historical range midpoint, assumed INT2/8192 | Exclude: L |
| Qwen 27B / DGX Spark / YT-16 | 11.6 | ? | A: INT4, legacy 8192 context | Exclude: L |
| Flash-Next / M5 Ultra / MacStories | 90.7 | 3578 | S: M below | Exclude: M |
| Flash-Next / M5 Ultra / MacStories | 87.8 | 15867 | S: M below | Exclude: M |
| Flash-Next / M5 Ultra / MacStories | 83.8 | 65005 | S: M below | Exclude: M |
| Flash-Next / M5 Ultra / MacStories | 60.6 | 130522 | S: M below | Exclude: M |
| Flash-Next / M5 Ultra / MacStories | 74.7 | 261597 | S: M below | Exclude: M |
| DeepSeek / RTX 5070 / Strata maintainer | 4.7 | ? | S: S below | Exclude: S |
| Flash-Next / Strata prefill / YT-01 | 2800 | ? | A: INT4, legacy 32768; source also formula input | Exclude: P |

### L — historical video observations

Original primary links in the source registry:
[YT-18](https://www.youtube.com/watch?v=IRyiP_U7RuA),
[YT-21](https://www.youtube.com/watch?v=PfSDw9IgdgM),
[YT-07](https://www.youtube.com/watch?v=3_uVmNjZ1QY),
[YT-16](https://www.youtube.com/watch?v=MOI8F2QL-J0),
[YT-01](https://www.youtube.com/watch?v=v90_q8bIUlA).
These links identify provenance, not fresh verification of their contents.
Direct fetching was throttled in the saved review. The
[secondary extraction](evidence/inference_benchmark_verification.md) does not establish
complete run metadata. Actual prompt, exact artifacts, KV/runtime settings, speculation,
concurrency, cache and timing protocol remain unestablished. Preserve the historical
diagnostic discrepancies; do not relabel their assumptions as measurements.

### M — MacStories prompt series

[Primary article](https://www.macstories.net/stories/m5-ultra-mac-studio-review-the-dream-mac-for-local-ai-agents/),
rechecked 2026-11-11. Source reports: 256 GB M5 Ultra, oMLX 0.7.0.dev2,
mixed oQ4e Flash-Next, MTP depth 3, thinking off, temperature 0, seed 42,
512 output tokens, unique prefixes/no cache reuse, one run per size. This series
is separate from the 108 TPS summary. Single-stream execution is inferred from
individual request descriptions, not independently observed scheduler traces.
KV precision and full saved kernel/runtime configuration are not established.
The linked model revision is identified but its contents remain unavailable.
Lookup therefore remains excluded; mixed quantization and enabled speculation also
remain outside the current formula-calibration boundary.

### S — Strata maintainer observation

[Primary document pinned at the latest document-changing commit retrieved on 2026-11-11](https://github.com/Niko1221/Strata/blob/de9c0448b2290c6c681eda16ff39759a1dc63ea1/docs/DEEPSEEK41.md).
It reports RTX 5070 12 GB, host RAM 64 GB, NVMe 3.6 GB/s, typical decode 4.7 TPS.
The separate 4K/8K prefill figures do not establish the decode prompt.
The documented model family, download recipe and current defaults are contextual
facts, not proof of the build, exact artifact, drafter state, KV, concurrency,
output length or timing protocol used for this row. CPU/SSD offload is described;
per-run residency/transfer traces remain missing. Exclude from lookup and from
the resident formula. Do not infer a bus-efficiency coefficient from this result.
The document commit is not an engine-build pin.

### P — prefill observation

Protocol and actual prompt are unknown. The same source feeds the hardware prefill
input, so this cannot independently validate that input. Do not transfer a prompt
or build from unrelated Strata tests to this historical row.

## Model-revision investigation

[Saved unauthenticated HTTP probes](evidence/benchmark_metadata_probe_2026-11-11.json)
distinguish the repository from the exact revision. The repository landing page and
[metadata API](https://huggingface.co/api/models/Jundot/Qwen3.8-Flash-Next-oQ4e-mtp)
returned 200. The
[article-linked revision API](https://huggingface.co/api/models/Jundot/Qwen3.8-Flash-Next-oQ4e-mtp/revision/2615fc0e976e65c2f3b55daca3a948f1cdc5b9f8)
returned 404. The current revision is saved only as a distinct identifier; it does
not repair the historical link. Cause of the missing revision is unestablished.
No claim is made that the original model's tensors, quantization manifest or
configuration were inspected. Runtime defaults from another version would not
establish the settings used in the original benchmark either.

## Concrete acquisition requirements

The public sources checked here do not provide a complete comparable row. Further
recovery requires the original operators' saved manifests/logs or controlled runs:

| Gap | Required acquisition | Prohibited substitution |
|---|---|---|
| Mac model revision/KV/kernel facts | Original file hashes, model/quantization manifest, exact oMLX build and saved execution settings | Current model revision or runtime defaults |
| Resident calibration | Fixed model/hardware/quantization/KV; speculation off for the current formula; one concurrent stream; isolated uncached prefill and generation measurements at recorded prompt depths | Fitting MTP mixed-quantized results as uniform INT4 |
| Strata decode metadata | Exact engine/build and artifact hashes; actual decode prompt/output, KV, drafter configuration, cache and concurrency; generation timing boundary | Prompt from a separate prefill result |
| Offload model inputs | Per-tier residency/placement, bytes transferred, measured transfer rates/overlap and CPU/GPU work during the same run | Advertised NVMe/VRAM bandwidth as end-to-end execution rate |
| Statistical validation | Raw timings, repetitions and variation; separate fitting and held-out conditions across prompt/deployment settings | Counting exclusions as accuracy improvement |
| Prefill independence | A new independently recorded run, with no shared source observation supplying the formula's base rate | A different source ID for the same underlying measurement |

For controlled runs, archive hardware/memory/OS/driver configuration, artifact hashes,
runtime commit and command, cache reset procedure, per-request prompt/generated token
counts and timings, repetitions and failures. Report serving TTFT separately from
isolated input-processing throughput. Keep baseline single-stream tests separate from
concurrency/speculative/offload extensions. The current application does not execute
such inference benchmarks itself; no hardware access or paid API experiment is assumed.

**Coverage remains 0 comparable decode / 0 comparable prefill.** U-02 remains open for
usable evidence acquisition; U-03/U-04 remain empirically unresolved. This matrix is an
acquisition checklist and evidence audit, not numerical calibration.
