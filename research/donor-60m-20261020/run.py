#!/usr/bin/env python3
"""Sequential, bounded, fully logged donor experiment. Run from repository root."""
import datetime as dt
import hashlib
import json
from pathlib import Path
import platform
import resource
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "scripts")]
from verify import verify_object
from independent_check import check as xor_check


def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def run(config_path):
    config = json.loads(config_path.read_text())
    out = HERE / config["name"]
    out.mkdir(exist_ok=False)
    hashes = {str(p.relative_to(ROOT)): digest(p) for p in [
        HERE / "search.cpp", HERE / "run.py", ROOT / "src/search.cpp",
        ROOT / "src/verify.py", ROOT / "scripts/independent_check.py",
        ROOT / "data/frontier.json", ROOT / "build/donor-search",
        ROOT / "build/search", config_path]}
    metadata = dict(config=config, hashes=hashes, platform=platform.platform(),
                    python=sys.version, start=dt.datetime.now(dt.timezone.utc).isoformat(),
                    compiler=subprocess.check_output(["c++", "--version"], text=True))
    (out / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")
    frontier = {x["N"]: x for x in json.loads((ROOT / "data/frontier.json").read_text())}
    deadline = dt.datetime.fromisoformat(config["stop_at"].replace("Z", "+00:00"))
    started = time.monotonic()
    child0 = resource.getrusage(resource.RUSAGE_CHILDREN)
    with (out / "runs.jsonl").open("x") as f:
        for index, job in enumerate(config["jobs"]):
            left = (deadline - dt.datetime.now(dt.timezone.utc)).total_seconds()
            if left < 2:
                print("Phase deadline reached; unstarted jobs are recorded in summary.", flush=True)
                break
            n = job["N"]
            args = [str(ROOT / "build" / ("search" if job["method"] == "tabu" else "donor-search")),
                    str(n), str(job["seed"]), str(job["budget"]), job["method"]]
            if job["method"] != "tabu":
                args += [str(job["stagnation"])]
            if job["start"] == "published":
                args += [json.loads((ROOT / frontier[n]["object"]).read_text())["sequence"]]
            t0 = time.monotonic()
            before = resource.getrusage(resource.RUSAGE_CHILDREN)
            record = dict(job=job, index=index, argv=args,
                          started_at=dt.datetime.now(dt.timezone.utc).isoformat())
            try:
                p = subprocess.run(args, capture_output=True, text=True,
                                   timeout=min(config["timeout_seconds"], left - 1), cwd=ROOT)
                record.update(returncode=p.returncode, stderr=p.stderr)
                if p.returncode:
                    record.update(status="failed", stdout=p.stdout)
                else:
                    result = json.loads(p.stdout)
                    checked = verify_object(result)
                    xor_check(result)
                    record.update(status="ok", result=result, verified=checked,
                                  reference_E=frontier[n]["E"],
                                  gap=result["E"] - frontier[n]["E"])
            except subprocess.TimeoutExpired as e:
                record.update(status="timeout", stdout=str(e.stdout), stderr=str(e.stderr))
            except Exception as e:
                record.update(status="error", error=repr(e))
            after = resource.getrusage(resource.RUSAGE_CHILDREN)
            record["elapsed_wall_seconds"] = time.monotonic() - t0
            record["child_cpu_seconds"] = (after.ru_utime + after.ru_stime
                                            - before.ru_utime - before.ru_stime)
            f.write(json.dumps(record) + "\n")
            f.flush()
            score = record.get("result", {}).get("E")
            print(f'{index+1}/{len(config["jobs"])} N={n} {job["method"]} '
                  f'{job.get("stagnation","")} {job["start"]} seed={job["seed"]} '
                  f'{record["status"]} E={score} published={frontier[n]["E"]}', flush=True)
    records = [json.loads(x) for x in (out / "runs.jsonl").read_text().splitlines()]
    child1 = resource.getrusage(resource.RUSAGE_CHILDREN)
    summary = dict(completed=len(records), planned=len(config["jobs"]),
                   statuses={s: sum(x["status"] == s for x in records)
                             for s in ["ok", "failed", "timeout", "error"]},
                   candidates=sum(x.get("gap", 0) < 0 for x in records),
                   total_child_cpu_seconds=child1.ru_utime+child1.ru_stime-child0.ru_utime-child0.ru_stime,
                   wall_seconds=time.monotonic()-started,
                   finish=dt.datetime.now(dt.timezone.utc).isoformat(),
                   unstarted_jobs=config["jobs"][len(records):])
    (out / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary), flush=True)


if __name__ == "__main__":
    run(Path(sys.argv[1]).resolve())
