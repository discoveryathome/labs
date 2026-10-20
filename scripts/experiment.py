#!/usr/bin/env python3
"""Bounded interleaved experiment; saves certificates and exact comparison scores."""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import platform
import random
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/"src"))
from verify import verify_object


def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def run(config, output):
    config_bytes = config.read_bytes()
    cfg = json.loads(config_bytes)
    subprocess.run(["make", "build"], cwd=ROOT, check=True)
    rows = {r["N"]: r for r in json.loads((ROOT/"data/frontier.json").read_text())}
    jobs = [(n, seed, method, start) for n in cfg["lengths"]
            for seed in cfg["seeds"] for method, start in cfg["arms"]]
    random.Random(cfg["order_seed"]).shuffle(jobs)
    output.mkdir(parents=True, exist_ok=True)
    if (output/"runs.jsonl").exists():
        raise ValueError("output already contains runs; choose a fresh directory")
    metadata = dict(config=cfg, config_sha256=hashlib.sha256(config_bytes).hexdigest(),
                    started_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    platform=platform.platform(), machine=platform.machine(),
                    python=sys.version, cpu_count=os.cpu_count(),
                    load_average_start=os.getloadavg() if hasattr(os, "getloadavg") else None,
                    compiler=subprocess.check_output(["c++","--version"], text=True).splitlines()[0],
                    compiler_flags="-O3 -std=c++17 -Wall -Wextra -pedantic",
                    source_sha256=digest(ROOT/"src/search.cpp"),
                    binary_sha256=digest(ROOT/"build/search"),
                    frontier_sha256=digest(ROOT/"data/frontier.json"))
    (output/"environment.json").write_text(json.dumps(metadata, indent=2)+"\n")
    results = []
    t0=time.perf_counter()
    with (output/"runs.jsonl").open("w") as f:
        for index,(n, seed, method, start) in enumerate(jobs):
            cmd = [str(ROOT/"build/search"), str(n), str(seed),
                   str(cfg["evaluations"]), method]
            if start == "published":
                cmd.append(json.loads((ROOT/rows[n]["object"]).read_text())["sequence"])
            r = json.loads(subprocess.check_output(cmd, text=True, timeout=cfg["run_timeout_seconds"]))
            result = verify_object(r)
            r.update(canonical=result["canonical"], canonical_sha256=result["canonical_sha256"],
                     F_exact=result["F_exact"], reference_E=rows[n]["E"],
                     gap_E=r["E"]-rows[n]["E"],
                     classification=("published-record-candidate" if r["E"]<rows[n]["E"]
                                     else "record-tie" if r["E"]==rows[n]["E"]
                                     else "internal-baseline"))
            f.write(json.dumps(r, sort_keys=True)+"\n");f.flush();results.append(r)
            print(f"{index+1}/{len(jobs)} N={n} {method}/{start} E={r['E']} "
                  f"reference={r['reference_E']} CPU={r['cpu_seconds']:.3f}s", flush=True)
    summary = summarize(results)
    summary["harness_wall_seconds"]=time.perf_counter()-t0
    (output/"summary.json").write_text(json.dumps(summary,indent=2)+"\n")


def summarize(results):
    # Count a new energy per length once; repeated seeds and symmetry copies aren't discoveries.
    unique = {(r["N"],r["E"]) for r in results if r["E"]<r["reference_E"]}
    cpu = sum(r["cpu_seconds"] for r in results)
    arms=[]
    for n,method,start in sorted({(r["N"],r["method"],r["start"]) for r in results}):
        runs=[r for r in results if (r["N"],r["method"],r["start"])==(n,method,start)]
        energies=sorted(r["E"] for r in runs)
        arms.append(dict(N=n,method=method,start=start,runs=len(runs),
                         best_E=min(energies),median_E=energies[len(energies)//2],
                         reference_E=runs[0]["reference_E"],
                         improved_initial=sum(r["E"]<r["initial_E"] for r in runs),
                         record_beating_runs=sum(r["E"]<r["reference_E"] for r in runs),
                         distinct_orbits=len({r["canonical"] for r in runs}),
                         cpu_seconds=sum(r["cpu_seconds"] for r in runs)))
    return dict(runs=len(results),neighbor_evaluations=sum(r["evaluations"] for r in results),
                cpu_seconds=cpu,solver_wall_seconds=sum(r["wall_seconds"] for r in results),
                distinct_frontier_improvements=len(unique),
                frontier_improvements_per_cpu_hour=len(unique)*3600/cpu if cpu else None,
                arms=arms)


if __name__ == "__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--config",type=Path,default=ROOT/"research/pilot/config.json")
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    run(a.config,a.output)
