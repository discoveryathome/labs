#!/usr/bin/env python3
"""Exhaust the preregistered alternating-parent insertion/deletion domain."""
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
PREDECESSOR = ROOT / "research/donor-60m-20261020"
sys.path.insert(0, str(PREDECESSOR))
from transfer import energy, neighborhood, verify_object, xor_check

SEED = "5df0b3ec35686ccb18f43aaee9f741e4"
BASE = "1e65ddd66191355ba5fd86b9788d6c02e9329a82"
INPUTS = [
    HERE / "sweep.py", HERE / "PREREGISTRATION.md",
    PREDECESSOR / "transfer.py", PREDECESSOR / "candidate-table.json",
    ROOT / "src/verify.py", ROOT / "scripts/independent_check.py",
    ROOT / "data/published.json", ROOT / "data/frontier.json",
    ROOT / "data/sources/manifest.json",
]


def alternate(bits):
    return "".join(str(int(b) ^ (i % 2)) for i, b in enumerate(bits))


def inputs():
    sources = json.loads((ROOT / "data/published.json").read_text())
    frontier = {r["N"]: r for r in json.loads((ROOT / "data/frontier.json").read_text())
                if r["bound"] is None}
    pending = {r["N"]: r["candidate_E"] for r in
               json.loads((PREDECESSOR / "candidate-table.json").read_text())}
    return sources, frontier, pending


def domain(sources, frontier):
    for index, source in enumerate(sources):
        for operation, change in (("delete", -1), ("insert", 1)):
            if source["N"] + change in frontier:
                yield index, operation, source["N"] + change


def self_check():
    trials = 0
    for n in range(2, 8):
        for bits in map("".join, itertools.product("01", repeat=n)):
            oriented = alternate(bits)
            assert alternate(oriented) == bits
            assert energy(oriented) == verify_object({"sequence": bits})["E"]
            for operation in ("delete", "insert"):
                edits = list(neighborhood(oriented, operation))
                assert len(edits) == (n if operation == "delete" else 2 * (n + 1))
                for position, bit, sequence in edits:
                    expected = list(oriented)
                    if operation == "delete":
                        del expected[position]
                    else:
                        expected.insert(position, bit)
                    assert sequence == "".join(expected)
                    obj = dict(sequence=sequence, N=len(sequence), E=energy(sequence))
                    verify_object(obj)
                    xor_check(obj)
                    trials += 1
    # Ensure the reference rejects a false energy, rather than only accepting controls.
    try:
        verify_object(dict(sequence="000", E=4))
    except ValueError:
        pass
    else:
        raise AssertionError("false energy was accepted")
    print(f"PASS: {trials} short edit trials, alternating invariance, and false-energy rejection")


def run(out, stop_at):
    sources, frontier, pending = inputs()
    jobs = list(domain(sources, frontier))
    expected = sum(sources[i]["N"] if op == "delete" else 2 * (sources[i]["N"] + 1)
                   for i, op, _ in jobs)
    out.mkdir(exist_ok=False)
    started = dt.datetime.now(dt.timezone.utc)
    metadata = dict(base=BASE, seed=SEED, started_at=started.isoformat(),
                    stop_at=stop_at.isoformat(), python=sys.version, platform=platform.platform(),
                    source_count=len(sources), eligible_targets=sorted(frontier),
                    reachable_targets=sorted({n for _, _, n in jobs}),
                    planned_groups=len(jobs), planned_trials=expected,
                    hashes={str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                            for p in INPUTS})
    (out / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")
    t0, c0 = time.monotonic(), time.process_time()
    total, groups, below_published, below_threshold = 0, 0, 0, 0
    best, candidates = {}, {}
    with (out / "groups.jsonl").open("x") as log:
        for index, operation, n in jobs:
            if dt.datetime.now(dt.timezone.utc) >= stop_at:
                break
            source = sources[index]
            oriented = alternate(source["sequence"])
            published_e = frontier[n]["E"]
            threshold = min(published_e, pending.get(n, published_e))
            histogram, digest = Counter(), hashlib.sha256()
            group_best = None
            new_candidates = []
            for position, bit, sequence in neighborhood(oriented, operation):
                e = energy(sequence)
                histogram[e] += 1
                digest.update(f"{position}:{bit}:{sequence}:{e}\n".encode())
                obj = dict(N=n, E=e, sequence=sequence, source_index=index,
                           source_N=source["N"], source_E=source["E"],
                           source=source["source"], by=source["by"],
                           orientation="alternating", operation=operation,
                           position=position, bit=bit)
                if group_best is None or e < group_best["E"]:
                    group_best = obj
                if e < threshold:
                    obj.update(verify_object(obj))
                    xor_check(obj)
                    new_candidates.append(obj)
            group_best.update(verify_object(group_best))
            xor_check(group_best)
            generated = sum(histogram.values())
            group_below_published = sum(v for e, v in histogram.items() if e < published_e)
            group_below_threshold = sum(v for e, v in histogram.items() if e < threshold)
            record = dict(source_index=index, operation=operation, N=n,
                          generated=generated, energy_histogram=dict(sorted(histogram.items())),
                          trials_sha256=digest.hexdigest(), best=group_best,
                          published_E=published_e, pending_E=pending.get(n), threshold_E=threshold,
                          below_published=group_below_published,
                          below_threshold=group_below_threshold)
            log.write(json.dumps(record, sort_keys=True) + "\n")
            log.flush()
            total += generated
            groups += 1
            below_published += group_below_published
            below_threshold += group_below_threshold
            if n not in best or group_best["E"] < best[n]["E"]:
                best[n] = dict(group_best, published_E=published_e,
                               pending_E=pending.get(n), threshold_E=threshold)
            for candidate in new_candidates:
                key = (n, candidate["canonical"])
                candidates.setdefault(key, dict(candidate, published_E=published_e,
                                                pending_E=pending.get(n), threshold_E=threshold))
    summary = dict(groups=groups, generated_sequences=total,
                   exhausted=groups == len(jobs), reached_lengths=len(best),
                   below_published=below_published, below_threshold=below_threshold,
                   candidate_orbits=len(candidates),
                   cpu_seconds=time.process_time() - c0, wall_seconds=time.monotonic() - t0,
                   finished_at=dt.datetime.now(dt.timezone.utc).isoformat())
    for name, obj in (("best", best), ("candidates", list(candidates.values())), ("summary", summary)):
        (out / f"{name}.json").write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, sort_keys=True), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-check", action="store_true")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--stop-at", default="2026-10-22T20:23:00Z")
    args = parser.parse_args()
    if args.self_check:
        self_check()
    elif args.output:
        deadline = dt.datetime.fromisoformat(args.stop_at.replace("Z", "+00:00"))
        if deadline.tzinfo is None:
            parser.error("--stop-at must include a timezone")
        run(args.output, deadline)
    else:
        parser.error("choose --self-check or --output")
