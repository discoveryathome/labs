#!/usr/bin/env python3
"""Exhaust bounded one-edit neighborhoods of pinned published witnesses."""
import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "scripts")]
from verify import verify_object, canonical, parse_sequence
from independent_check import check as xor_check


def energy(bits):
    n, x = len(bits), int(bits, 2)
    return sum((n-k-2*((x^(x>>k))&((1<<(n-k))-1)).bit_count())**2
               for k in range(1, n))


def neighborhood(bits, operation):
    n = len(bits)
    if operation == "delete":
        for j in range(n):
            yield j, None, bits[:j]+bits[j+1:]
    elif operation == "insert":
        for j in range(n+1):
            for b in "01":
                yield j, b, bits[:j]+b+bits[j:]
    elif operation == "rotate":
        for j in range(1,n):
            yield j, None, bits[j:]+bits[:j]
    else:
        raise ValueError(operation)


def run(out, stop_at):
    out.mkdir(exist_ok=False)
    frontier = {r["N"]: r for r in json.loads((ROOT / "data/frontier.json").read_text())
                if r["bound"] is None}
    sources = json.loads((ROOT / "data/published.json").read_text())
    known = {(r["N"], r["canonical"]) for r in sources}
    deadline = dt.datetime.fromisoformat(stop_at.replace("Z","+00:00"))
    metadata = dict(
        started_at=dt.datetime.now(dt.timezone.utc).isoformat(),
        stop_at=stop_at, targets=sorted(frontier), source_count=len(sources),
        scope="All one-bit insertions/deletions and nonzero cyclic rotations from pinned published witnesses, restricted to audited open target lengths.",
        hashes={str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in [Path(__file__), ROOT / "data/frontier.json", ROOT / "data/published.json"]})
    (out / "metadata.json").write_text(json.dumps(metadata, indent=2)+"\n")
    t0,c0 = time.monotonic(),time.process_time()
    best, counts, groups, candidates = {}, 0, 0, []
    exhausted = True
    with (out / "groups.jsonl").open("x") as log:
        for index, source in enumerate(sources):
            for operation, change in [("delete",-1),("insert",1),("rotate",0)]:
                n=source["N"]+change
                if n not in frontier:
                    continue
                if dt.datetime.now(dt.timezone.utc)>=deadline:
                    exhausted=False
                    break
                group_best=None
                for position,bit,sequence in neighborhood(source["sequence"],operation):
                    e=energy(sequence)
                    counts+=1
                    result=dict(N=n,E=e,sequence=sequence,source_index=index,
                                source_N=source["N"],source_E=source["E"],
                                source=source["source"],operation=operation,position=position,bit=bit)
                    if group_best is None or e<group_best["E"]:
                        group_best=result
                    pool=best.setdefault(n,[])
                    if len(pool)<2 or e<=pool[-1]["E"]:
                        key=canonical(parse_sequence(sequence))
                        if (n,key) not in known and all(x["canonical"]!=key for x in pool):
                            result["canonical"]=key
                            pool.append(result)
                            pool.sort(key=lambda x:(x["E"],x["canonical"]))
                            del pool[2:]
                    if e<frontier[n]["E"]:
                        verify_object(result);xor_check(result)
                        candidates.append(result)
                verify_object(group_best);xor_check(group_best)
                groups+=1
                group_best["generated"]=source["N"] if operation=="delete" else (
                    2*(source["N"]+1) if operation=="insert" else source["N"]-1)
                group_best["reference_E"]=frontier[n]["E"]
                log.write(json.dumps(group_best)+"\n");log.flush()
            if not exhausted:
                break
    # Deduplicate candidate certificates under all eight allowed symmetries.
    unique={}
    for r in candidates:
        key=canonical(parse_sequence(r["sequence"]))
        r["canonical"]=key
        unique[(r["N"],key)]=r
    for n,pool in best.items():
        for r in pool:
            verify_object(r);xor_check(r)
            r["reference_E"]=frontier[n]["E"]
            r["gap"]=r["E"]-frontier[n]["E"]
    summary=dict(groups=groups,generated_sequences=counts,exhausted=exhausted,
                 candidate_orbits=len(unique),cpu_seconds=time.process_time()-c0,
                 wall_seconds=time.monotonic()-t0,
                 finished_at=dt.datetime.now(dt.timezone.utc).isoformat())
    (out/"best.json").write_text(json.dumps(best,indent=2)+"\n")
    (out/"candidates.json").write_text(json.dumps(list(unique.values()),indent=2)+"\n")
    (out/"summary.json").write_text(json.dumps(summary,indent=2)+"\n")
    print(json.dumps(summary),flush=True)


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--stop-at",required=True)
    a=p.parse_args()
    run(a.output,a.stop_at)
