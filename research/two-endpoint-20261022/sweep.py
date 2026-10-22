#!/usr/bin/env python3
"""Exhaust exactly two ordered endpoint edits; score every retained path twice."""
import argparse
from collections import Counter
import datetime as dt
import hashlib
import itertools
import json
from pathlib import Path
import platform
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PREVIOUS = ROOT / "research/donor-60m-20261020"
sys.path.insert(0, str(PREVIOUS))
from transfer import energy, verify_object, xor_check
from verify import canonical, parse_sequence, orbit

OPS = ("delete_first", "delete_last", "prepend_0", "prepend_1", "append_0", "append_1")
SEED = "93610b14cdb3c9d4f2373623b04b0933"
BASE = "1e65ddd66191355ba5fd86b9788d6c02e9329a82"


def edit(bits, operation):
    if operation == "delete_first":
        return bits[1:]
    if operation == "delete_last":
        return bits[:-1]
    if operation.startswith("prepend_") and operation[-1] in "01":
        return operation[-1] + bits
    if operation.startswith("append_") and operation[-1] in "01":
        return bits + operation[-1]
    raise ValueError(operation)


def paths(bits):
    for first in OPS:
        intermediate = edit(bits, first)
        if not intermediate:
            continue
        for second in OPS:
            child = edit(intermediate, second)
            if child:
                yield first, second, child


def inputs():
    published = json.loads((ROOT / "data/published.json").read_text())
    table = json.loads((PREVIOUS / "candidate-table.json").read_text())
    parents = [dict(s, parent_kind="published", parent_object="data/published.json",
                    parent_row=i) for i, s in enumerate(published)]
    for row in table:
        obj = json.loads((ROOT / row["object"]).read_text())
        parents.append(dict(obj, parent_kind="pending", parent_object=row["object"],
                            parent_row=None, by=published[obj["source_index"]]["by"]))
    frontier = {r["N"]: r for r in json.loads((ROOT / "data/frontier.json").read_text())
                if r["bound"] is None}
    pending = {r["N"]: r["candidate_E"] for r in table}
    files = [HERE / "sweep.py", HERE / "PREREGISTRATION.md", PREVIOUS / "transfer.py",
             PREVIOUS / "candidate-table.json", ROOT / "data/published.json",
             ROOT / "data/frontier.json", ROOT / "data/sources/manifest.json",
             ROOT / "src/verify.py", ROOT / "scripts/independent_check.py"]
    files += [ROOT / r["object"] for r in table]
    return parents, frontier, pending, files


def plan(parents, frontier):
    counts, contributing = Counter(), set()
    for index, parent in enumerate(parents):
        for _, _, child in paths(parent["sequence"]):
            if len(child) in frontier:
                counts[len(child)] += 1
                contributing.add(index)
    return dict(parent_rows=len(parents), contributing_parents=len(contributing),
                eligible_targets=sorted(frontier), reachable_targets=sorted(counts),
                trials_by_length=dict(sorted(counts.items())), planned_trials=sum(counts.values()))


def self_check():
    count = 0
    for n in range(3, 7):
        for bits in map("".join, itertools.product("01", repeat=n)):
            children = list(paths(bits))
            assert len(children) == 36
            keys = {canonical(parse_sequence(child)) for _, _, child in children}
            for first, second, child in children:
                expected = list(bits)
                for op in (first, second):
                    if op == "delete_first": expected.pop(0)
                    elif op == "delete_last": expected.pop()
                    elif op.startswith("prepend_"): expected.insert(0, op[-1])
                    else: expected.append(op[-1])
                assert child == "".join(expected)
                obj = dict(N=len(child), E=energy(child), sequence=child)
                verify_object(obj)
                xor_check(obj)
                count += 1
            for oriented in orbit(parse_sequence(bits)):
                text = "".join("1" if x == 1 else "0" for x in oriented)
                assert {canonical(parse_sequence(c)) for _, _, c in paths(text)} == keys
    try:
        edit("010", "rotate")
    except ValueError:
        pass
    else:
        raise AssertionError("unsupported operation accepted")
    print(f"PASS: {count} short ordered paths; direct/XOR scores, list-edit reconstruction and all-eight-parent-symmetry closure")


def run(out, deadline):
    parents, frontier, pending, files = inputs()
    planned = plan(parents, frontier)
    out.mkdir(exist_ok=False)
    metadata = dict(base=BASE, seed=SEED, started_at=dt.datetime.now(dt.timezone.utc).isoformat(),
                    stop_at=deadline.isoformat(), python=sys.version, platform=platform.platform(),
                    plan=planned, operations=OPS,
                    hashes={str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in files})
    (out / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")
    started, cpu = time.monotonic(), time.process_time()
    counts, best, candidates = Counter(), {}, {}
    below_published = below_threshold = total = 0
    completed_parents = 0
    with (out / "trials.jsonl").open("x") as log:
        for index, parent in enumerate(parents):
            if dt.datetime.now(dt.timezone.utc) >= deadline:
                break
            for first, second, child in paths(parent["sequence"]):
                n = len(child)
                if n not in frontier:
                    continue
                e = energy(child)
                obj = dict(N=n, E=e, sequence=child)
                exact = verify_object(obj)
                xor_check(obj)
                threshold = min(frontier[n]["E"], pending.get(n, frontier[n]["E"]))
                record = dict(parent=index, operations=[first, second], N=n, E=e,
                              sequence_sha256=hashlib.sha256(child.encode()).hexdigest(),
                              published_E=frontier[n]["E"], pending_E=pending.get(n), threshold_E=threshold)
                log.write(json.dumps(record, sort_keys=True) + "\n")
                total += 1
                counts[n] += 1
                below_published += e < frontier[n]["E"]
                below_threshold += e < threshold
                certificate = dict(record, sequence=child, F_exact=exact["F_exact"],
                                   canonical=exact["canonical"], parent_kind=parent["parent_kind"],
                                   parent_object=parent["parent_object"], parent_row=parent["parent_row"],
                                   parent_N=parent["N"], parent_E=parent["E"],
                                   source=parent["source"], by=parent["by"])
                if n not in best or e < best[n]["E"]:
                    best[n] = certificate
                if e < threshold:
                    candidates.setdefault((n, exact["canonical"]), dict(certificate, **{
                        k: exact[k] for k in ("autocorrelations", "PSL", "canonical_sha256")}))
            log.flush()
            completed_parents += 1
    summary = dict(generated_paths=total, completed_parent_rows=completed_parents,
                   exhausted=completed_parents == len(parents), reached_lengths=len(counts),
                   trials_by_length=dict(sorted(counts.items())), below_published=below_published,
                   below_threshold=below_threshold, candidate_orbits=len(candidates),
                   cpu_seconds=time.process_time() - cpu, wall_seconds=time.monotonic() - started,
                   finished_at=dt.datetime.now(dt.timezone.utc).isoformat())
    for name, obj in (("summary", summary), ("best", best), ("candidates", list(candidates.values()))):
        (out / f"{name}.json").write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: v for k, v in summary.items() if k != "trials_by_length"}, sort_keys=True), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-check", action="store_true")
    parser.add_argument("--plan", action="store_true")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--stop-at")
    args = parser.parse_args()
    if args.self_check:
        self_check()
    elif args.plan:
        p, f, _, _ = inputs()
        print(json.dumps(plan(p, f), sort_keys=True))
    elif args.output and args.stop_at:
        deadline = dt.datetime.fromisoformat(args.stop_at.replace("Z", "+00:00"))
        if deadline.tzinfo is None:
            parser.error("--stop-at must include a timezone")
        run(args.output, deadline)
    else:
        parser.error("choose --self-check, --plan, or --output with --stop-at")
