#!/usr/bin/env python3
"""Render the measured launch assessment from archived experiment output."""
import argparse
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser()
p.add_argument("--check",action="store_true")
a=p.parse_args()
summary=json.loads((ROOT/"research/pilot/results/summary.json").read_text())
runs=[json.loads(x) for x in (ROOT/"research/pilot/results/runs.jsonl").read_text().splitlines()]
frontier={r["N"]:r for r in json.loads((ROOT/"data/frontier.json").read_text())}
wins=ties=losses=0
lines=["| N | Published E | Published F | Best random hill E | Best random tabu E | Best published-start E |",
       "|---:|---:|---:|---:|---:|---:|"]
for n in sorted({r["N"] for r in runs}):
    subset=[r for r in runs if r["N"]==n]
    def best(method,start):
        return min(r["E"] for r in subset if r["method"]==method and r["start"]==start)
    for seed in sorted({r["seed"] for r in subset}):
        e={r["method"]:r["E"] for r in subset if r["seed"]==seed and r["start"]=="random"}
        d=e["tabu"]-e["hill"];wins+=d<0;ties+=d==0;losses+=d>0
    ref=frontier[n]["E"]
    warm=min(r["E"] for r in subset if r["start"]=="published")
    lines.append(f"| {n} | {ref} | {n*n/(2*ref):.6f} | {best('hill','random')} | {best('tabu','random')} | {warm} |")
table="\n".join(lines)
cpu=summary["cpu_seconds"]
text=f"""# Launch-readiness assessment — 2026-10-20

> **Current participation:** pre-release contributions and expert-agent review are open;
> @Mister-Meeseeks maintains the project, which is listed on the Discovery@Home hub and
> open to donated sessions since 2026-10-22. Any closed-intake or missing-coordinator
> statement below records an earlier stage (2026-10-20); see [the current policy](../PARTICIPATION.md).
> Scientific results and review requirements remain in force; independent review of the
> five pending candidates is still wanted.

**Recommendation: retain LABS as a local incubation project. Do not launch short
CPU donations with a promise of mathematical records.** Short sessions can
productively audit sources, verify candidates, and run disciplined algorithm
ablations. Competitive record hunting needs a stronger search engine or a
specific structural idea, followed by a larger pilot.

## Measured outcome

The archived sweep contains **{summary['runs']} runs**, five seeds at each of eight
lengths and four arms (hill/tabu × random/published start), at a budget of two
million neighbor evaluations per run. It executed
**{summary['neighbor_evaluations']:,} neighbor evaluations**, consuming
**{cpu:.6f} process CPU-seconds** ({cpu/3600:.6f} CPU-hours),
**{summary['solver_wall_seconds']:.6f} summed solver wall-seconds**, and
**{summary['harness_wall_seconds']:.6f} harness wall-seconds**.

**Genuine published-frontier improvements: {summary['distinct_frontier_improvements']}.
Observed search yield: {summary['frontier_improvements_per_cpu_hour']:.1f} improvements per CPU-hour.**
There are no new published-record candidates to submit.

{table}

The full per-arm distributions, CPU times and distinct symmetry-orbit counts are
in `research/pilot/results/summary.json`; every run and full sequence is in
`runs.jsonl`. The table shows minima over five seeds, not expected performance.

## Three different meanings of improvement

* **Published records:** zero strict E improvements. All 80 published-start runs
  retained the input record. They are warm-start ties, not independent discoveries.
* **Internal baseline:** all 80 random-start runs reduced their initial E. Tabu
  beat hill in **{wins} of {wins+ties+losses} paired random-start runs**,
  tied {ties} and lost {losses}. This is fixed-neighborhood-budget evidence
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

This is only {cpu/60:.2f} CPU-minutes of new search. Zero hits is an empirical
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
"""
path=ROOT/"docs/ASSESSMENT.md"
if a.check:
    assert path.read_text()==text
    print("PASS: assessment agrees with archived results")
else:
    path.write_text(text)
    print("Wrote docs/ASSESSMENT.md")
