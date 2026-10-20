#!/usr/bin/env python3
"""Recompute descriptive statistics; never relabel a baseline win as a record."""
import collections
import json
from pathlib import Path
import statistics

HERE = Path(__file__).resolve().parent


def analyze():
    phases = {}
    all_runs = []
    for phase in ["calibration", "heldout", "warm", "refinement"]:
        path = HERE / phase / "runs.jsonl"
        if not path.exists():
            continue
        rows = [json.loads(x) for x in path.read_text().splitlines()]
        all_runs += rows
        ok = [r for r in rows if r["status"] == "ok"]
        phases[phase] = dict(
            completed=len(rows), successful=len(ok),
            failures=len(rows) - len(ok),
            candidates=sum(r["gap"] < 0 for r in ok),
            evaluations=sum(r["result"]["evaluations"] for r in ok),
            solver_cpu_seconds=sum(r["result"]["cpu_seconds"] for r in ok),
            child_cpu_seconds=sum(r["child_cpu_seconds"] for r in rows),
            harness_run_wall_seconds=sum(r["elapsed_wall_seconds"] for r in rows),
            distinct_output_orbits=len({r["verified"]["canonical"] for r in ok}),
        )
    heldout = []
    path = HERE / "heldout/runs.jsonl"
    if path.exists():
        heldout = [json.loads(x) for x in path.read_text().splitlines()]
    paired = collections.defaultdict(dict)
    for r in heldout:
        if r["status"] == "ok":
            paired[(r["job"]["N"], r["job"]["seed"])][r["job"]["method"]] = r
    pairs = []
    for (n, seed), group in sorted(paired.items()):
        if set(group) != {"tabu", "population"}:
            continue
        base, new = group["tabu"], group["population"]
        b, a = base["result"], new["result"]
        pairs.append(dict(N=n, seed=seed, baseline_E=b["E"], new_E=a["E"],
                          reference_E=new["reference_E"],
                          delta_E=a["E"]-b["E"],
                          relative_reduction=(b["E"]-a["E"])/b["E"],
                          same_initial_E=a["initial_E"] == b["initial_E"],
                          baseline_cpu_seconds=b["cpu_seconds"],
                          new_cpu_seconds=a["cpu_seconds"]))
    by_length = []
    for n in sorted({p["N"] for p in pairs}):
        ps = [p for p in pairs if p["N"] == n]
        by_length.append(dict(
            N=n, pairs=len(ps), reference_E=ps[0]["reference_E"],
            baseline_median_E=statistics.median(p["baseline_E"] for p in ps),
            new_median_E=statistics.median(p["new_E"] for p in ps),
            baseline_best_E=min(p["baseline_E"] for p in ps),
            new_best_E=min(p["new_E"] for p in ps),
            wins=sum(p["delta_E"] < 0 for p in ps),
            ties=sum(p["delta_E"] == 0 for p in ps),
            losses=sum(p["delta_E"] > 0 for p in ps)))
    totals = dict(
        pairs=len(pairs),
        wins=sum(p["delta_E"] < 0 for p in pairs),
        ties=sum(p["delta_E"] == 0 for p in pairs),
        losses=sum(p["delta_E"] > 0 for p in pairs),
        median_paired_relative_reduction=statistics.median(
            p["relative_reduction"] for p in pairs) if pairs else None,
        baseline_cpu_seconds=sum(p["baseline_cpu_seconds"] for p in pairs),
        new_cpu_seconds=sum(p["new_cpu_seconds"] for p in pairs),
        unmatched_successful_runs=sum(len(g) for g in paired.values()
                                      if set(g) != {"tabu", "population"}))
    smoke = json.loads((HERE / "smoke.json").read_text())
    controls = json.loads((HERE / "controls.json").read_text())["runs"]
    research_cpu = sum(p["solver_cpu_seconds"] for p in phases.values()) + smoke["cpu_seconds"]
    transfer_path = HERE / "transfer/summary.json"
    transfer = json.loads(transfer_path.read_text()) if transfer_path.exists() else None
    if transfer:
        research_cpu += transfer["cpu_seconds"]
    candidates = {}
    for row in all_runs:
        if row["status"] == "ok" and row["gap"] < 0:
            r = row["result"]
            candidates[(r["N"], row["verified"]["canonical"])] = r["E"]
    if transfer:
        for r in json.loads((HERE / "transfer/candidates.json").read_text()):
            candidates[(r["N"], r["canonical"])] = r["E"]
    candidate_lengths = sorted({n for n,_ in candidates})
    record_candidates = len(candidate_lengths)
    return dict(
        phases=phases, heldout_totals=totals, by_length=by_length, pairs=pairs,
        research_runs=sum(p["completed"] for p in phases.values())+1,
        research_neighbor_evaluations=sum(p["evaluations"] for p in phases.values())+smoke["evaluations"],
        research_search_cpu_seconds=research_cpu,
        transfer=transfer,
        control_solver_cpu_seconds=sum(r["cpu_seconds"] for r in controls),
        candidate_lengths=candidate_lengths,
        published_record_candidate_lengths=record_candidates,
        candidate_orbits=len(candidates),
        independently_accepted_records=0,
        observed_candidate_lengths_per_research_cpu_hour=record_candidates/(research_cpu/3600),
        denominator_notes=[
            "Includes calibration, held-out, warm, smoke, structured transformation and refinement searches.",
            "Controls, compilation, source research, implementation, verification and replay are separate.",
            "Child CPU time is also recorded to retain failed-run costs.",
            "Warm-start ties inherit the published witness and are not discoveries.",
            "Refinement retaining an already found candidate is deduplicated, not another discovery.",
            "Candidate-length yield is not an accepted-record rate or a sustainable rate estimate.",
            "Descriptive paired comparison, not a claim against published SOTA algorithms.",
        ])


if __name__ == "__main__":
    print(json.dumps(analyze(), indent=2))
