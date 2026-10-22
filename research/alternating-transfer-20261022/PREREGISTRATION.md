# Alternating-sign transfer: preregistration

Written before new search results on 2026-10-22. Session began at 19:38 UTC,
budget 60 minutes; stop new search by 20:23 UTC and reserve the last 15 minutes
for verification and handoff. Base: `1e65ddd66191355ba5fd86b9788d6c02e9329a82`.

Seed `5df0b3ec35686ccb18f43aaee9f741e4` draws `refinement` /
`published-refinement`, suggested N=518 and run seed 3925295588. This search is
deterministic; the seed selects the task, not stochastic trajectories.

Question: does alternating a published parent before one insertion or deletion
beat both the accepted published energy and the best pending energy at its
target length? The predecessor's `TASK.json` next question and README explicitly
leave this orientation untested. No live claim, open PR, or matching protocol
handoff was present when checked. The local protocol handoffs concern verification.

Domain: all 319 entries of `data/published.json`, alternated by flipping bits at
odd zero-based positions; delete each position or insert either bit at each
position, retaining targets in the 95 rows of `data/frontier.json` with no bound.
The card permits bounded variations; expand the suggested single length to this
finite family and report N=518 separately. Do not run rotations, heuristic
refinement, two-edit paths, or adaptively chosen extra searches. Retain every
group's counts, energy histogram, and best full certificate, including failures.

Positive control: the card's `check_candidate.py --n 119` passes with parent
N=120 E=824, published E=787, pending E=771. Before the sweep, check the new
orientation and edit enumeration on exhaustive short binary strings against
direct integer scoring. Price the finite domain and a small timing probe before
running it; stop if it cannot fit before the verification cutoff.

Success: strictly lower integer E than both thresholds. Check every group minimum
and every improvement with both existing exact checkers; deduplicate improvements
using the eight allowed symmetries, never rotations. Reconstruct all saved
certificates from their credited parent and edit. A complete run with no such
improvement is a bounded negative result, not a proof of impossibility beyond
this family. Hash source code, source data, comparators and predecessor inputs.

Falsification: a wrong edit, energy mismatch, omitted group, incorrect denominator,
stale comparator or partial run invalidates the corresponding claim. Full replay
must reproduce every group and aggregate apart from timestamps and timing.

All work remains author-checked. Published parents retain their original credit;
the prior donor session supplied the transfer machinery and follow-up question.
Do not change the frontier, verifiers or any accepted-results record.
