# Benchmark verification evidence review

Reviewed 2026-11-10. The supplied YouTube-assistant report is preserved in [evidence/inference_benchmark_verification.md](evidence/inference_benchmark_verification.md). It is a secondary extraction containing both claimed observations and hypotheses. Direct YouTube fetching was throttled; video timestamps were not independently verified.

## Primary-source corrections

[MacStories original benchmark](https://www.macstories.net/stories/m5-ultra-mac-studio-review-the-dream-mac-for-local-ai-agents/), accessed 2026-11-10: the M5 Ultra is 256 GB, while its M3 comparison is 512 GB. The long-context Flash-Next row is 60.6 TPS at 130,522 prompt tokens, with 512 output tokens, no cache reuse and MTP depth 3. It is a different request series from the 108 TPS summary. The article identifies mixed oQ4e quantization and oMLX. The report's 512 GB and exact 128,000 claims should not replace the catalog.

[Strata maintainer documentation](https://github.com/Niko1221/Strata/blob/main/docs/DEEPSEEK41.md), accessed 2026-11-10: the 257 GB set already includes 138 GB model files, 111 GB Engram and 8 GB drafter. It reports about 4.7 TPS on RTX 5070/64 GB RAM and separates prefill measurements. These are maintainer-reported results, not independently repeated measurements.

## Problems with the supplied derivations

- The midpoint of 4.3 and 4.9 is 4.6, not 4.7. A separately reported typical 4.7 must remain a distinct observation.
- The 65-75% bus-efficiency claim and assumed PCIe/NVMe bandwidths are not established by the timestamp table. Do not insert them into catalog inputs as measured facts.
- Multiplying our prediction by 0.70 to approach an observation is curve fitting, not independent validation. Our formula already includes an efficiency term; an additional factor needs a separate definition and evidence.
- The supplied 68 TPS derivation does not reproduce our engine's actual equation. The engine uses 672 / (16 * 2/8 * 1.05) * 0.425, before other multipliers; it does not divide 672 by 10 GB.
- The roofline puts bandwidth in the numerator of TPS. Total model size alone cannot identify the bottleneck: residency of active bytes, expert reuse, transfers, runtime, overlap and execution placement matter.
- Different GPUs, operating systems and host configurations are not a controlled experiment proving an operating-system cause.
- Do not generalize a fixed long-context slowdown from a couple of unmatched runs.

## Consequences for the three expected calibration failures

The existing tests still quantify differences against the current stored records; they do not establish matched-condition model error. The Mac comparisons lack adequate runtime, speculative-decoding and quantization matching, and the short-context value was assumed. The Strata decode context is also not established by an unrelated prefill test or a configured maximum.

Recommended correction sequence:

1. Preserve the current observations and their history, but identify incomplete or mismatched records as ineligible for strict calibration. Report exclusion reasons separately from numerical failures and successful comparisons.
2. Extend benchmark metadata and resolver matching to include actual hardware configuration, quantization identity, runtime/version, speculative mode, concurrency and measurement protocol. Separate actual prompt length from configured context capacity.
3. Import the original benchmark rows with their exact metadata. Keep source measurements, rounded video summaries and analyst assumptions distinguishable.
4. For offload deployments without comparable measurements or tier-specific inputs, report unavailable/uncertain performance rather than applying a VRAM-only model as if it were validated.
5. Validate a revised formula on independent observations. Do not tune it solely to make these three cases pass.

No production benchmark record, coefficient or xfail was changed in this evidence-review step. The raw report and this assessment are research evidence, not a new calibration dataset.

## Implementation follow-up (2026-11-10)

C-054 implements evidence eligibility, exact execution matching and preservation of excluded observations. See [calibration and cost review](CALIBRATION_AND_COST_REVIEW.md). The historical three formula discrepancies remain strict diagnostic xfails; the current report has no comparable observations, so MAPE is unavailable, not zero. Formula coefficients remain unchanged.
