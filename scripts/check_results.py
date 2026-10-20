#!/usr/bin/env python3
"""Check all result certificates; optionally replay deterministic search trajectories."""
import argparse
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from verify import verify_object
from experiment import summarize, digest

p=argparse.ArgumentParser()
p.add_argument("--directory",type=Path,default=ROOT/"research/pilot/results")
p.add_argument("--replay",action="store_true")
a=p.parse_args()
meta=json.loads((a.directory/"environment.json").read_text())
assert digest(ROOT/"src/search.cpp")==meta["source_sha256"]
assert digest(ROOT/"data/frontier.json")==meta["frontier_sha256"]
results=[json.loads(x) for x in (a.directory/"runs.jsonl").read_text().splitlines()]
rows={r["N"]:r for r in json.loads((ROOT/"data/frontier.json").read_text())}
expected={(n,s,m,t) for n in meta["config"]["lengths"] for s in meta["config"]["seeds"]
          for m,t in meta["config"]["arms"]}
assert len(results)==len(expected)
assert {(r["N"],r["seed"],r["method"],r["start"]) for r in results}==expected
if a.replay:
    subprocess.run(["make","build"],cwd=ROOT,check=True)
for r in results:
    verify_object(r)
    assert r["reference_E"]==rows[r["N"]]["E"]
    assert r["gap_E"]==r["E"]-r["reference_E"]
    assert r["budget"]==meta["config"]["evaluations"]
    assert r["evaluations"]==r["budget"]//r["N"]*r["N"]
    assert r["iterations"]*r["N"]==r["evaluations"]
    assert r["E"]<=r["initial_E"]
    assert r["cpu_seconds"]>0 and r["wall_seconds"]>0
    want=("published-record-candidate" if r["gap_E"]<0 else
          "record-tie" if r["gap_E"]==0 else "internal-baseline")
    assert r["classification"]==want
    if a.replay:
        cmd=[str(ROOT/"build/search"),str(r["N"]),str(r["seed"]),str(r["budget"]),r["method"]]
        if r["start"]=="published":
            cmd.append(json.loads((ROOT/rows[r["N"]]["object"]).read_text())["sequence"])
        again=json.loads(subprocess.check_output(cmd,text=True,timeout=60))
        for k in ("N","seed","budget","method","start","initial_E","E","evaluations",
                  "iterations","restarts","incumbent_improvements","sequence"):
            assert again[k]==r[k],(k,r["N"],r["seed"])
summary=json.loads((a.directory/"summary.json").read_text())
for k,v in summarize(results).items():
    assert summary[k]==v,k
print(f"PASS: {len(results)} result certificates; "
      f"{summary['distinct_frontier_improvements']} distinct frontier improvements"
      + ("; all trajectories replayed" if a.replay else ""))
