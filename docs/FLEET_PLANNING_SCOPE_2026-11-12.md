# Fleet planning: bounded implementation scope

Scope decided 2026-11-12 from the new enterprise report and primary-source audit.
This extends U-07 with a pure, opt-in planning primitive, not a new recommendation
policy. Modify/create only `domain/fleet.py`, `engines/fleet.py`,
`tests/unit/test_fleet.py`, this scope, the evidence archive/review, correction
ledger and continuity documents. Existing catalog, scenario/API schemas, candidate
enumeration, ranking, costs and simultaneous-resident filters stay unchanged.

The primitive accepts caller-declared capacity of one **complete serving replica**,
including its GPUs per replica and a description/source identity for that capacity.
It separates fleet-wide simultaneous requests, retained sessions and required
aggregate **output** tokens/second. Employee seats are not a capacity input. The
caller must establish the workload/context/cache/placement match; a citation alone
does not validate supplied capacity. AgentX session trees cannot populate simultaneous
HTTP-request slots. Configured max sequences alone is not proven resident capacity.

For each known resource, compute an integer lower bound `ceil(demand / capacity)`.
Use the maximum of those independent bounds, then add an explicitly supplied spare
replica count and multiply by GPUs per complete replica. Replicas can be any integer;
they are not model-parallel node counts and are never rounded to powers of two.
Missing demand/capacity remains unknown. Zero capacity with positive demand has no
finite solution; zero demand needs zero active replicas for that resource.

The maximum of separate bounds is **necessary, not sufficient**. Joint memory use,
session affinity/placement, load balancing, prefill/decode contention, arrival bursts,
queueing and loaded latency may require more capacity. Linear output-capacity addition
is only an ideal-balance resource bound. No SLA, autoscaler or employee limit follows.
These are bounds conditional on the caller's declared capacities. An observed test
rate is not a proven physical ceiling; treating it as a planning ceiling is a separate
assumption and must be labeled. The worked source-based example does so explicitly.
No measured fleet curve or coefficient is invented and no benchmark is imported.
The primitive cannot reconstruct Revolut's unknown topology from 56 GPUs and TP8 advice.

The next larger phase needs explicit deployment/cost semantics, retained-state
placement and matched load/SLA evidence before recommendation integration. Shared M5
512 GB catalog/serving remains separate: verified advertised RAM/price does not supply
usable memory reservation, a matched prefill curve or five-request loaded performance.

Adaptive routing remains a separate phase. Required inputs include task classes,
capability/data policy, local load signal, classifier overhead/bypass, session affinity,
cache invalidation, retries/escalations, rate limits, task success and per-path costs.
Do not copy Jev's policy thresholds as measurements or attribute that package to Julien.
The existing static Hybrid Split and full local peak policy are unchanged.

Verification will cover rounding/boundaries, non-power-of-two replicas, unknown/zero
capacity, missing output demand, explicit spares, separate peak/retained constraints,
finite numeric validation and immutable deterministic results. Run focused purity/
contract checks and the required full Python suite after implementation. Reuse the
unchanged engine 0.1.4 UI/browser verification.
