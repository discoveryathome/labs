# Launch-readiness assessment — 2026-10-20

> **Current participation:** pre-release contributions and expert-agent review are open.
> Any closed-intake or missing-coordinator statement below records an earlier stage;
> see [the current policy](../PARTICIPATION.md). Scientific results and review requirements remain in force.

**Recommendation: retain LABS as a local incubation project. Do not launch short
CPU donations with a promise of mathematical records.** Short sessions can
productively audit sources, verify candidates, and run disciplined algorithm
ablations. Competitive record hunting needs a stronger search engine or a
specific structural idea, followed by a larger pilot.

## Measured outcome

The archived sweep contains **160 runs**, five seeds at each of eight
lengths and four arms (hill/tabu × random/published start), at a budget of two
million neighbor evaluations per run. It executed
**319,982,780 neighbor evaluations**, consuming
**167.109534 process CPU-seconds** (0.046419 CPU-hours),
**231.140608 summed solver wall-seconds**, and
**233.429558 harness wall-seconds**.

**Genuine published-frontier improvements: 0.
Observed search yield: 0.0 improvements per CPU-hour.**
There are no new published-record candidates to submit.

| N | Published E | Published F | Best random hill E | Best random tabu E | Best published-start E |
|---:|---:|---:|---:|---:|---:|
| 92 | 490 | 8.636735 | 746 | 738 | 490 |
| 99 | 553 | 8.861664 | 913 | 849 | 553 |
| 107 | 645 | 8.875194 | 1121 | 1069 | 645 |
| 119 | 787 | 8.996823 | 1363 | 1307 | 787 |
| 450 | 13009 | 7.783073 | 23169 | 21617 | 13009 |
| 451 | 12625 | 8.055485 | 21673 | 20781 | 12625 |
| 518 | 18463 | 7.266533 | 30975 | 28639 | 18463 |
| 573 | 22558 | 7.277440 | 38098 | 35102 | 22558 |

The full per-arm distributions, CPU times and distinct symmetry-orbit counts are
in `research/pilot/results/summary.json`; every run and full sequence is in
`runs.jsonl`. The table shows minima over five seeds, not expected performance.

## Three different meanings of improvement

* **Published records:** zero strict E improvements. All 80 published-start runs
  retained the input record. They are warm-start ties, not independent discoveries.
* **Internal baseline:** all 80 random-start runs reduced their initial E. Tabu
  beat hill in **39 of 40 paired random-start runs**,
  tied 0 and lost 1. This is fixed-neighborhood-budget evidence
  against our elementary hill baseline.
* **New search algorithm:** none claimed. Tabu is an established method, and this
  implementation was not compared head-to-head with the published GPU memetic
  or self-avoiding-walk solvers. We make no scaling or state-of-the-art claim.

The benchmark uses a single solver process at a time on an Apple M2, C++17,
`-O3`, with deterministic SplitMix64 randomness. The environment file records
compiler, platform and input hashes. Machine load was high (recorded at sweep
start and observed during the run); CPU frequencies and scheduling varied.
Wall times are not dedicated-machine throughput measurements. Fixed evaluation
budgets and paired starting states support score comparisons; hardware speed
comparisons would require controlled interleaved timing and A/A calibration.
The included A/A check confirms deterministic outputs, not a timing speedup.

The denominator above includes search initialization and restarts, but excludes
literature research, engineering, certificate checks, build time and replay.
Published-start arms also inherit the historical cost of discovering their
inputs. They must not be advertised as finding those records in seconds.

This is only 2.79 CPU-minutes of new search. Zero hits is an empirical
observation, not a proof that improvements are impossible or an estimate of a
stable rare-event rate. Runs sharing methods, witnesses and lengths are not
independent samples of all future donated work. The study does not justify
extrapolating an expected time to a new record.

## Readiness and productive next work

The pilot provides a cheap exact verifier, a separately implemented XOR checker,
319 reproduced published witnesses, a 160-length table with per-row checks,
exhaustive controls through N=16, deterministic search, symmetry deduplication,
a seeded catalogue, full negative-result logs and replay instructions.
All evidence remains author-checked. Historical optimality labels and source
completeness have the limitations stated in `docs/LITERATURE.md`.

The most credible short-session work is a bounded change with a reusable outcome:
audit a newer record source; review an encoding or checker invariant; implement
and test an incremental evaluator; compare restart/tenure variants on held-out
medium-length cases; or test a specified structured transformation followed by
unrestricted refinement. Failed experiments should be retained with their scope
and compute so they are not repeated blindly.

For a second research pilot, preregister held-out seeds and equal-compute
comparisons with a reviewed stronger baseline, then test whether near-frontier
hit rates improve before allocating more record-search compute. Stop a direction
after ten sessions with neither held-out algorithm gains nor a competitive
candidate; reopen it for a new structural idea, source update, or faster engine.
This is a proposed decision rule, not evidence that ten sessions suffice to
estimate a rare discovery rate.

**Launch remains closed:** no maintainer has consented, review capacity is
unknown, and there is no shared coordination service. Local files conform to the
Discovery@Home protocol; conformance is not a stage assessment or endorsement.
Before opening donations, designate a willing maintainer, confirm credit/license
terms, establish shared claims/handoffs, and independently review the verifier
and frontier. Review capacity sets intake; compute alone does not.
