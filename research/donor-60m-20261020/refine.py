#!/usr/bin/env python3
"""Refine the preregistered best neighboring-length transformations."""
import datetime as dt
import hashlib
import json
from pathlib import Path
import resource
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "scripts")]
from verify import verify_object
from independent_check import check as xor_check


def main():
    plan = json.loads((HERE / "transfer-plan.json").read_text())
    best = json.loads((HERE / "transfer/best.json").read_text())
    chosen = sorted([pool[0] for pool in best.values() if pool],
                    key=lambda r:(r["E"]/r["reference_E"],r["N"]))[:16]
    deadline=dt.datetime.fromisoformat(plan["stop_at"].replace("Z","+00:00"))
    out=HERE/"refinement";out.mkdir(exist_ok=False)
    hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
            for p in [Path(__file__),HERE/"search.cpp",HERE/"transfer/best.json",
                      HERE/"transfer-plan.json",ROOT/"data/frontier.json"]}
    jobs=[dict(initial=r,seed=3849692801+i,budget=100000000,method="population",stagnation=4)
          for i,r in enumerate(chosen)]
    (out/"metadata.json").write_text(json.dumps(dict(jobs=jobs,hashes=hashes,
        initialization="derived edit, not the original published witness",
        solver_start_label="The legacy C++ 'published' field means supplied input; the exact derived input is in each job."),
        indent=2)+"\n")
    t0=time.monotonic();c0=resource.getrusage(resource.RUSAGE_CHILDREN)
    with (out/"runs.jsonl").open("x") as f:
        for i,job in enumerate(jobs):
            left=(deadline-dt.datetime.now(dt.timezone.utc)).total_seconds()
            if left<2:break
            initial=job["initial"];n=initial["N"]
            argv=[str(ROOT/"build/donor-search"),str(n),str(job["seed"]),
                  str(job["budget"]),job["method"],str(job["stagnation"]),initial["sequence"]]
            record=dict(index=i,job=job,argv=argv,
                        started_at=dt.datetime.now(dt.timezone.utc).isoformat())
            w=time.monotonic();c=resource.getrusage(resource.RUSAGE_CHILDREN)
            try:
                process=subprocess.run(argv,capture_output=True,text=True,timeout=min(left-1,300),cwd=ROOT)
                record.update(returncode=process.returncode,stderr=process.stderr)
                if process.returncode:
                    record.update(status="failed",stdout=process.stdout)
                else:
                    result=json.loads(process.stdout)
                    checked=verify_object(result);xor_check(result)
                    if result["initial_E"]!=initial["E"]:raise ValueError("initial score")
                    record.update(status="ok",result=result,verified=checked,
                                  reference_E=initial["reference_E"],gap=result["E"]-initial["reference_E"])
            except subprocess.TimeoutExpired as e:
                record.update(status="timeout",stdout=str(e.stdout),stderr=str(e.stderr))
            except Exception as e:
                record.update(status="error",error=repr(e))
            after=resource.getrusage(resource.RUSAGE_CHILDREN)
            record["child_cpu_seconds"]=after.ru_utime+after.ru_stime-c.ru_utime-c.ru_stime
            record["elapsed_wall_seconds"]=time.monotonic()-w
            f.write(json.dumps(record)+"\n");f.flush()
            print(i+1,len(jobs),n,record["status"],record.get("result",{}).get("E"),
                  "reference",initial["reference_E"],flush=True)
    rows=[json.loads(x) for x in (out/"runs.jsonl").read_text().splitlines()]
    c1=resource.getrusage(resource.RUSAGE_CHILDREN)
    summary=dict(completed=len(rows),planned=len(jobs),
                 candidates=sum(r.get("gap",0)<0 for r in rows),
                 child_cpu_seconds=c1.ru_utime+c1.ru_stime-c0.ru_utime-c0.ru_stime,
                 wall_seconds=time.monotonic()-t0,unstarted_jobs=jobs[len(rows):],
                 finished_at=dt.datetime.now(dt.timezone.utc).isoformat())
    (out/"summary.json").write_text(json.dumps(summary,indent=2)+"\n")
    print(json.dumps(summary),flush=True)


if __name__=="__main__":
    main()
