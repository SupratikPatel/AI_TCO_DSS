# Revolut inference case study: implications for AI TCO DSS

Reviewed 2026-11-10. This is a sourced case analysis, not a calibrated dataset or a verified procurement quotation. No catalog or engine constants were changed from this account.

## What the post establishes

The [LinkedIn post by Andrei Devo](https://www.linkedin.com/posts/andevo_revolut-rents-56-nvidia-b200-gpus-164k-share-7524084235712925696-YJ6v/) describes a large GLM coding deployment and estimates GPU rental costs at $164,000-$198,000 per month. Treat that price range as the poster's estimate: the post does not supply a provider quote, contract, invoice or complete cost breakdown. Its description of GLM 5.1 also needs the later model-version distinction below.

## Primary account

David Abitbol's [organizer-published talk/transcript](https://ai.engineer/nyc/2026/talks/revolut), October 13, 2026, and [session video](https://www.youtube.com/watch?v=Ok6QdZHCcI8) report:

- About 2,000 engineers use a deployment of 56 B200 GPUs serving GLM 5.3; the earlier rollout used GLM 5.1.
- He reports roughly $0.30 per million blended tokens and an invoice about one-tenth of prior Anthropic/OpenAI spending.
- Targets include first-token latency below three seconds and about 200 tokens per second.
- Tuning a fixed GPU fleet reduced latency as demand grew. Discussed controls include 256K context, FP4, tensor parallelism, cache reuse, speculative decoding and prefill/decode separation.
- Other models remain available for exceptional or visual tasks.
- The reported 60% coding-time and 70% lead-time improvements are internal rollout observations. The presentation does not isolate the causal effect of self-hosting.

These are company-reported observations, not independently reproduced measurements. The transcript contains recognition errors. It does not establish the LinkedIn rental price or complete TCO.

## Arithmetic on the post's estimate

These are calculations from the post's assumptions, not additional observed Revolut costs:

| Calculation | Result |
|---|---:|
| Monthly rental divided by 2,000 engineers | $82-$99 per engineer per month |
| Monthly rental divided by 56 GPUs and 730 hours | Approximately $4.01-$4.84 per GPU-hour |
| Flat rental multiplied by 60 months | $9.84M-$11.88M |

The last row excludes staffing, other model calls, operational overhead, growth, contract changes and discounting. It is a constant-price extrapolation, not a forecast. A large total can coexist with a reasonable per-user amount at enterprise scale. Neither number establishes savings without a comparable alternative delivering the same workload and service level.

## Implications for this project

The following are design conclusions for AI TCO DSS, not claims made by Revolut:

1. **Ask for workload before recommending hardware.** Users, requests, token lengths, concurrency, context and latency requirements determine what constitutes a suitable deployment. A writing/email choice should not silently inherit a coding-agent workload and then reward surplus throughput.
2. **Separate sufficient performance from maximum performance.** Once a candidate meets a task's service requirements, additional speed may have limited value. Show when a higher ranking is buying excess capacity and how much it costs relative to a cheaper feasible alternative.
3. **Measure the service, not just weight fit.** Memory feasibility does not prove adequate concurrent capacity or acceptable queueing latency. Quantization, cache behavior, runtime and deployment topology must accompany benchmark observations.
4. **Compare matched alternatives.** Evaluate total recurring costs, one-time costs, effective utilization and per-user costs for the same demand. Preserve the difference between rental, owned hardware and API billing.
5. **Represent routing explicitly.** A local/API split is an assumption about which work can use each component. Capability requirements and each component's feasibility matter; a weighted average of scores cannot establish either.
6. **Show uncertainty and evidence coverage.** Do not insert the post's GPU price, productivity percentages or fleet throughput into generic calibration constants. The available account lacks the complete workload, serving configuration, cost boundary and measurement distribution required for that use.

## What would be needed to reproduce the case

A defensible scenario would require the actual contract price and cost inclusions, utilization and demand traces, input/output/cache token mix, peak concurrency, context distribution, model/quantization/runtime versions, measured latency percentiles, routing shares and operational staffing. The matched API alternative must use the same task mix and service targets. Productivity benefits should remain a separate scenario assumption unless a study supports a causal estimate.

This case is useful as motivation for workload-driven sizing and cost transparency. It cannot validate the current catalog's RTX, H100, model quality or performance estimates.

## Bibliography keys

Both sources are registered in `data/sources.json` and exported to `thesis/references.bib`:

- `REVOLUT-AIE-2026`: primary conference talk/transcript, accessed 2026-11-10.
- `REVOLUT-LINKEDIN-DEVO`: the supplied LinkedIn post, accessed 2026-11-10.

Pandoc citations: [@REVOLUT-AIE-2026] and [@REVOLUT-LINKEDIN-DEVO]. The talk supports company-reported deployment claims; the post is cited for its commentary and unverified rental estimate.

## Enterprise-scale follow-up, 2026-11-12

The author's 1050-user empty recommendation was reproduced under saved DSS profiles.
See [enterprise scale and adaptive routing](ENTERPRISE_SCALE_AND_ADAPTIVE_ROUTING_2026-11-12.md)
for the modeled capacity/budget boundary, eight new diagnostic scenarios, two budget
counterfactuals, current fleet/replica limitations and the separately sourced Pi
virtual-model example. This does not change the primary-account caveats or convert
Revolut's deployment into a calibrated observation.
