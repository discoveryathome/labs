# Donor research trial: a useful pocket of accessible improvements

**The trial found five exact-checked constructions below the audited published
energies.** They remain record candidates pending independent novelty review.
The general-purpose search experiment was inconclusive; the successful route
was adding or removing one endpoint bit from recently published witnesses.

| N | Published E | Candidate E | Candidate F | Construction |
|---:|---:|---:|---:|---|
| 108 | 670 | 666 | 324/37 | Delete first bit of published N=109 |
| 118 | 807 | 799 | 6962/799 | Delete first bit of published N=119 |
| 119 | 787 | 771 | 14161/1542 | Delete last bit of published N=120 |
| 463 | 14439 | 14047 | 214369/28094 | Prepend −1 to published N=462 |
| 485 | 16106 | 15970 | 47045/6388 | Append −1 to published N=484 |

Full sequences, autocorrelations, exact merit factors, canonical symmetry keys,
parents and individual executable checks are in
[candidate-table.json](candidate-table.json) and [candidates/](candidates/).
[AUDIT.md](AUDIT.md) describes the renewed literature/benchmark audit and credits
the published parent constructions. No accepted frontier row was edited.

## What the session tested

The seeded catalogue draw selected `heldout-tabu`. An independently implemented
experimental search retained up to eight symmetry-distinct elite sequences,
used rank-biased selection, occasional crossover and perturbation, and restarted
on local stagnation. These are established ideas, not a new algorithm claim.
The original solver remained unchanged.

Forty calibration runs compared four variants with the baseline. The original
selection rule chose population tabu with a 4N stagnation threshold. That
configuration was frozen before 32 paired held-out trials at N=92,99,107,119,
with 50 million neighbor evaluations per run. It **won 14, tied 4 and lost 14**;
median paired energy reduction was zero. A calibration lead did not generalize.
N=99 looked better in this sample, but selecting that length afterwards would
require another held-out confirmation.

Sixteen 100-million-evaluation runs starting from the published records found
no improvement. The session then explicitly expanded to structured transfer:
all single-bit insertions/deletions and nonzero cyclic rotations of the pinned
published orientations into the 95 audited open lengths. This completed
**225,791 generated sequences in 396 source/operator groups**, using
**30.289413 CPU-seconds**. It found eight distinct improving symmetry orbits at
five lengths; only the best construction per length is counted as a frontier
improvement. Every best construction has the simpler endpoint representation
shown above.

The 16 closest distinct lengths then received bounded population-tabu refinement
from their best transformed starts. Full records and costs are in
[refinement/](refinement/). Retaining a candidate already found by transfer is
not an additional discovery. [analysis.json](analysis.json) gives the complete,
deduplicated totals, CPU denominator, held-out distributions and observed
candidate-length yield. An observed yield from one finite sweep is not a
sustainable arrival-rate estimate; independently accepted records remain zero.

The complete research denominator is **137 heuristic runs**, **6,809,992,812
single-bit neighbor evaluations**, the **225,791 transformation evaluations**,
and **1,499.706080 search CPU-seconds (25.00 CPU-minutes)**. This includes
calibration and unsuccessful searches, and corresponds to **12.00 distinct
candidate-length improvements per search CPU-hour** in this particular trial.
Engineering, literature audit, compilation, validation and replay are outside
that CPU denominator but inside the session time budget. There were no failed,
timed-out or omitted planned search jobs.

## Donor experience and launch recommendation

A working implementation and exact controls were available within the first
several minutes. Calibration completed at 11 minutes 34 seconds of charged time.
The held-out comparison delivered a useful negative result around minute 19;
the structured search produced the five candidates around minute 23.
This is tangible mathematical progress within a short session, rather than
merely making a weak internal baseline look better.

**Revise the initial blanket pessimism: LABS has demonstrated an accessible
structured-transfer direction.** It is a credible candidate for a small,
carefully scoped introductory project after independent review. Generic
random-start search still looks discouraging, and this one successful sweep
does not establish easy wins for many subsequent donors.

These five results have already been found. Before public donations, reviewers
should validate them and establish the appropriate new thresholds. Donors must
compare against the best pending candidates too; rediscovery against stale
published rows is not new progress. A fresh-agent follow-up should test another
transform family from those updated thresholds before promising a continuing
supply of low-hanging fruit.

Good next tasks are independent novelty review, two-edit paths, and testing
alternating-sign source orientations before insertion/deletion. Although
alternating signs preserve a sequence's energy, deleting an interior element
changes the alternating phase of the suffix; the resulting neighborhood is not
automatically covered by editing only the original orientation. This session
did not test that extension. The catalogue now routes more work toward
structured refinement and review and records the completed negative comparisons.

## Timing and limitations

The original 60-minute wall-clock trial began at 06:25:21 UTC on 20 October 2026
and was interrupted by the user. Calibration continued until 06:36:54.818652.
The user resumed at 13:04:13 UTC. We charged the entire first 693.818652 seconds,
including background execution, and allowed at most another 2906 seconds:
search deadline 13:37:39 and final deadline 13:52:39 UTC.
**This was a segmented 60-minute-budget trial, not an uninterrupted hour.**
`session.json`, `continuation.json` and the final receipt preserve the timeline.

The same agent built the pilot, giving it an orientation advantage over a new
donor. The first segment ran on a heavily loaded Apple M2; the second segment
had much less contention. Compare interleaved held-out results within their
phase, not raw speed across phases. All verification is author-performed, even
when using the separately implemented checker or a fresh local clone.

Original construction costs are inherited from the published authors. Endpoint
editing is an established method; this trial claims neither a novel operator
nor a general solver improvement. It establishes exact improvements over the
strongest same-length published witnesses identified in the bounded audit.
Global optimality, complete literature coverage and independent acceptance are
not established. No remote repository, push, hub listing or external post was made.

## Reproduce

From the repository root:

```sh
make check
c++ -O3 -std=c++17 -Wall -Wextra -pedantic research/donor-60m-20261020/search.cpp -o build/donor-search
./build/donor-search --self-test
python3 research/donor-60m-20261020/check.py
python3 research/donor-60m-20261020/check_candidate.py --n 119
```

`check.py` verifies every retained certificate using both integer implementations,
checks input/source hashes, job coverage, transformations, paired starts and the
saved analysis. `--replay sample` repeats eight predetermined search trajectories;
`--replay all` repeats every trajectory and all enumerated transfer groups.
Full replay can take tens of minutes. Historical run configurations have expired
deadlines; use these replay commands rather than rerunning the old phase harnesses.

`VERIFY.json` lists commands and bounds. `PREREGISTRATION.md`, `selection.json`
and `transfer-plan.json` separate calibration, held-out evaluation and exploratory
work. All unsuccessful runs remain in the logs. Mathematical witness authors
retain credit; Codex supplied the local transformation search, experimental
implementation, audit and author checks at the user's direction.
