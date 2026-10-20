#!/usr/bin/env python3
"""Offline exact checks, provenance, coverage and optional deterministic replay."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "scripts")]
from verify import verify_object
from independent_check import check as xor_check
from analyze import analyze
from transfer import energy, neighborhood
from check_candidate import main as check_candidate


def require(condition, message):
    if not condition:
        raise ValueError(message)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--replay", choices=["sample", "all"])
    args = parser.parse_args()
    manifest = HERE/"SOURCES.json"
    if manifest.exists():
        for entry in json.loads(manifest.read_text())["files"]:
            require(hashlib.sha256((ROOT/entry["path"]).read_bytes()).hexdigest()==entry["sha256"],
                    f"package source/result hash: {entry['path']}")
    frontier = {x["N"]: x for x in json.loads((ROOT / "data/frontier.json").read_text())}
    count, replayed = 0, 0
    selection = json.loads((HERE / "selection.json").read_text())["selected"]
    require((selection["method"], selection["stagnation"]) == ("population", 4), "selection changed")
    for phase in ["calibration", "heldout", "warm"]:
        directory = HERE / phase
        require((directory / "summary.json").exists(), f"incomplete phase {phase}")
        metadata = json.loads((directory / "metadata.json").read_text())
        config = json.loads((HERE / f"{phase}.json").read_text())
        require(config == metadata["config"], f"{phase} config changed")
        for name, expected in metadata["hashes"].items():
            # Compiler-produced bytes are platform specific. Source and inputs
            # must match; rebuild locally for replay.
            if name.startswith("build/"):
                continue
            require(hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == expected,
                    f"hash mismatch: {name}")
        rows = [json.loads(x) for x in (directory / "runs.jsonl").read_text().splitlines()]
        summary = json.loads((directory / "summary.json").read_text())
        require(summary["completed"] == len(rows), f"{phase} count")
        require(summary["planned"] == len(config["jobs"]), f"{phase} planned count")
        require(summary["unstarted_jobs"] == config["jobs"][len(rows):], f"{phase} unstarted")
        for index, row in enumerate(rows):
            job = config["jobs"][index]
            require(row["job"] == job and row["index"] == index, f"{phase} job order")
            expected_args=[str(job["N"]),str(job["seed"]),str(job["budget"]),job["method"]]
            if job["method"]!="tabu":
                expected_args.append(str(job["stagnation"]))
            if job["start"]=="published":
                expected_args.append(json.loads((ROOT/frontier[job["N"]]["object"]).read_text())["sequence"])
            require(row["argv"][1:]==expected_args, f"{phase} actual arguments")
            require(job["seed"] in range(3849692671,3849692675) if phase == "calibration"
                    else job["seed"] in range(3849692701,3849692709), "seed scope")
            if row["status"] != "ok":
                continue
            r = row["result"]
            computed = verify_object(r)
            xor_check(r)
            require(computed == row["verified"], "saved verification differs")
            for key in ("N", "seed", "budget", "method", "start"):
                require(r[key] == job[key], f"job/result mismatch {key}")
            require(r["evaluations"] == job["budget"] // job["N"] * job["N"], "budget")
            require(row["reference_E"] == frontier[r["N"]]["E"], "reference")
            require(row["gap"] == r["E"] - frontier[r["N"]]["E"], "gap")
            if phase != "calibration" and r["method"] != "tabu":
                require(r["stagnation"] == selection["stagnation"], "unfrozen parameter")
            if phase == "warm":
                require(r["initial_E"] == frontier[r["N"]]["E"], "warm input score")
            count += 1
            if args.replay == "all" or (args.replay == "sample" and index < 2):
                argv = [str(ROOT / "build" / Path(row["argv"][0]).name), *row["argv"][1:]]
                replay = json.loads(subprocess.check_output(argv, text=True, timeout=300, cwd=ROOT))
                strip = lambda obj: {k: v for k, v in obj.items()
                                     if k not in ("cpu_seconds", "wall_seconds")}
                require(strip(replay) == strip(r), f"trajectory mismatch: {phase}/{index}")
                replayed += 1
    for r in [json.loads((HERE / "smoke.json").read_text()),
              *json.loads((HERE / "controls.json").read_text())["runs"]]:
        verify_object(r)
        xor_check(r)
        count += 1
    published = json.loads((ROOT / "data/published.json").read_text())
    known = {(r["N"],r["canonical"]) for r in published}
    transfer_dir = HERE / "transfer"
    require((transfer_dir / "summary.json").exists(), "transfer incomplete")
    for name, expected in json.loads((transfer_dir / "metadata.json").read_text())["hashes"].items():
        require(hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == expected,
                f"transfer hash: {name}")
    groups = [json.loads(x) for x in (transfer_dir / "groups.jsonl").read_text().splitlines()]
    expected_groups = [(i,op) for i,r in enumerate(published)
                       for op,d in [("delete",-1),("insert",1),("rotate",0)]
                       if r["N"]+d in frontier and frontier[r["N"]+d]["bound"] is None]
    summary = json.loads((transfer_dir / "summary.json").read_text())
    require([(r["source_index"],r["operation"]) for r in groups]
            == expected_groups[:len(groups)], "transfer coverage/order")
    require(summary["exhausted"] == (len(groups)==len(expected_groups)), "transfer coverage flag")
    require(summary["generated_sequences"] == sum(r["generated"] for r in groups), "transfer count")
    for i,r in enumerate(groups):
        source = published[r["source_index"]]
        neighbors = neighborhood(source["sequence"],r["operation"])
        if args.replay == "all":
            values = [(energy(s),j,b,s) for j,b,s in neighbors]
            minimum = min(values,key=lambda x:x[0])
            require((r["E"],r["position"],r["bit"],r["sequence"]) == minimum, "transfer minimum")
        else:
            reconstructed = next(s for j,b,s in neighbors if j==r["position"] and b==r["bit"])
            require(reconstructed == r["sequence"], "transform reconstruction")
        verify_object(r);xor_check(r);count+=1
        require(r["reference_E"] == frontier[r["N"]]["E"], "transfer comparison")
    best = json.loads((transfer_dir / "best.json").read_text())
    for pool in best.values():
        for r in pool:
            verify_object(r);xor_check(r);count+=1
            require((r["N"],r["canonical"]) not in known, "published orbit retained")
    refine_dir = HERE / "refinement"
    metadata = json.loads((refine_dir / "metadata.json").read_text())
    for name, expected in metadata["hashes"].items():
        require(hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == expected,
                f"refinement hash: {name}")
    rows = [json.loads(x) for x in (refine_dir / "runs.jsonl").read_text().splitlines()]
    summary = json.loads((refine_dir / "summary.json").read_text())
    require(summary["completed"] == len(rows), "refinement completed")
    require(summary["unstarted_jobs"] == metadata["jobs"][len(rows):], "refinement unstarted")
    expected_initials = sorted([pool[0] for pool in best.values() if pool],
                               key=lambda r:(r["E"]/r["reference_E"],r["N"]))[:16]
    require([j["initial"] for j in metadata["jobs"]] == expected_initials, "refinement selection")
    for i,row in enumerate(rows):
        require(row["index"]==i and row["job"]==metadata["jobs"][i], "refinement job")
        if row["status"] != "ok":
            continue
        r,job=row["result"],row["job"]
        require(row["argv"][1:]==[str(job["initial"]["N"]),str(job["seed"]),
                str(job["budget"]),"population","4",job["initial"]["sequence"]],
                "refinement actual arguments")
        require(r["initial_E"]==job["initial"]["E"], "refinement input")
        require(r["seed"]==job["seed"] and r["budget"]==job["budget"], "refinement parameters")
        require(r["method"]=="population" and r["stagnation"]==4, "refinement method")
        require(r["evaluations"]==job["budget"]//r["N"]*r["N"], "refinement budget")
        require(row["reference_E"]==frontier[r["N"]]["E"], "refinement frontier")
        require(row["gap"]==r["E"]-frontier[r["N"]]["E"], "refinement gap")
        require(verify_object(r)==row["verified"], "refinement certificate");xor_check(r);count+=1
        if args.replay=="all" or (args.replay=="sample" and i<2):
            argv=[str(ROOT/"build/donor-search"),*row["argv"][1:]]
            actual=json.loads(subprocess.check_output(argv,text=True,timeout=300,cwd=ROOT))
            strip=lambda obj:{k:v for k,v in obj.items() if k not in ("cpu_seconds","wall_seconds")}
            require(strip(actual)==strip(r), "refinement trajectory")
            replayed+=1
    stats = analyze()
    require(all(p["same_initial_E"] for p in stats["pairs"]), "paired starts differ")
    for n in stats["candidate_lengths"]:
        check_candidate(n)
    for r in json.loads((HERE/"audit-files.json").read_text())["files"]:
        require(hashlib.sha256((HERE/r["path"]).read_bytes()).hexdigest()==r["sha256"],
                f"audit hash: {r['path']}")
    saved = HERE / "analysis.json"
    if saved.exists():
        require(json.loads(saved.read_text()) == stats, "analysis is stale")
    print(f"PASS: {count} exact certificates, source/input hashes, job coverage, paired starts; "
          f"{replayed} deterministic trajectory replays")


if __name__ == "__main__":
    main()
