#!/usr/bin/env python3
"""Check this package's accounting, parent provenance and exact certificates."""
import argparse
from collections import Counter
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "scripts")]
from verify import verify_object
from independent_check import check as xor_check


def validate(records, best, candidates, summary, sources, frontier, pending):
    expected = [(i, op, s["N"] + delta)
                for i, s in enumerate(sources)
                for op, delta in (("delete", -1), ("insert", 1))
                if s["N"] + delta in frontier]
    assert [(r["source_index"], r["operation"], r["N"]) for r in records] == expected

    def certificate(obj):
        source = sources[obj["source_index"]]
        assert obj["orientation"] == "alternating"
        assert (obj["source_N"], obj["source_E"], obj["source"], obj["by"]) == (
            source["N"], source["E"], source["source"], source["by"])
        bits = [str(1 - int(b)) if i % 2 else b for i, b in enumerate(source["sequence"])]
        j = obj["position"]
        if obj["operation"] == "delete":
            assert type(j) is int and 0 <= j < len(bits) and obj["bit"] is None
            del bits[j]
        else:
            assert obj["operation"] == "insert"
            assert type(j) is int and 0 <= j <= len(bits) and obj["bit"] in ("0", "1")
            bits.insert(j, obj["bit"])
        assert "".join(bits) == obj["sequence"]
        verify_object(obj)
        xor_check(obj)

    totals = Counter()
    per_length = {}
    for r in records:
        n, s = r["N"], sources[r["source_index"]]
        expected_count = s["N"] if r["operation"] == "delete" else 2 * (s["N"] + 1)
        histogram = {int(e): count for e, count in r["energy_histogram"].items()}
        assert all(e >= 0 and type(c) is int and c > 0 for e, c in histogram.items())
        assert sum(histogram.values()) == r["generated"] == expected_count
        threshold = min(frontier[n]["E"], pending.get(n, frontier[n]["E"]))
        assert (r["published_E"], r["pending_E"], r["threshold_E"]) == (
            frontier[n]["E"], pending.get(n), threshold)
        assert r["below_published"] == sum(c for e, c in histogram.items() if e < frontier[n]["E"])
        assert r["below_threshold"] == sum(c for e, c in histogram.items() if e < threshold)
        obj = r["best"]
        assert (obj["source_index"], obj["operation"], obj["N"]) == (r["source_index"], r["operation"], n)
        certificate(obj)
        assert obj["E"] == min(histogram)
        totals.update({k: r[k] for k in ("generated", "below_published", "below_threshold")})
        if str(n) not in per_length or obj["E"] < per_length[str(n)]["E"]:
            per_length[str(n)] = dict(obj, published_E=r["published_E"],
                                      pending_E=r["pending_E"], threshold_E=threshold)
    assert best == per_length
    keys = set()
    for obj in candidates:
        certificate(obj)
        n = obj["N"]
        threshold = min(frontier[n]["E"], pending.get(n, frontier[n]["E"]))
        assert (obj["published_E"], obj["pending_E"], obj["threshold_E"]) == (
            frontier[n]["E"], pending.get(n), threshold)
        assert obj["E"] < threshold
        key = (n, obj["canonical"])
        assert key not in keys
        keys.add(key)
    assert {r["N"] for r in records if r["below_threshold"]} == {r["N"] for r in candidates}
    assert summary["exhausted"] is True
    assert summary["groups"] == len(expected)
    assert summary["generated_sequences"] == totals["generated"]
    assert summary["reached_lengths"] == len(best)
    assert summary["below_published"] == totals["below_published"]
    assert summary["below_threshold"] == totals["below_threshold"]
    assert summary["candidate_orbits"] == len(candidates)
    return expected, totals


def main(replay, self_check):
    manifest = json.loads((HERE / "SOURCES.json").read_text())
    for item in manifest["files"]:
        assert hashlib.sha256((ROOT / item["path"]).read_bytes()).hexdigest() == item["sha256"], item["path"]
    result = HERE / "results"
    read = lambda name: json.loads((result / f"{name}.json").read_text())
    metadata, best, candidates, summary = map(read, ("metadata", "best", "candidates", "summary"))
    for path, expected_hash in metadata["hashes"].items():
        assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == expected_hash, path
    sources = json.loads((ROOT / "data/published.json").read_text())
    frontier = {r["N"]: r for r in json.loads((ROOT / "data/frontier.json").read_text()) if r["bound"] is None}
    pending = {r["N"]: r["candidate_E"] for r in
               json.loads((ROOT / "research/donor-60m-20261020/candidate-table.json").read_text())}
    records = [json.loads(line) for line in (result / "groups.jsonl").read_text().splitlines()]
    expected, totals = validate(records, best, candidates, summary, sources, frontier, pending)
    assert metadata["planned_groups"] == len(expected)
    assert metadata["planned_trials"] == totals["generated"]
    assert metadata["source_count"] == len(sources)
    assert metadata["eligible_targets"] == sorted(frontier)
    assert metadata["reachable_targets"] == sorted({n for _, _, n in expected})
    print(f"PASS: {len(records)} groups; {totals['generated']} trials; parent reconstruction, both exact checkers, accounting and pinned inputs")
    # Reconstruct every below-published attempt, including inferior pending ties.
    sys.path.insert(0, str(ROOT / "research/donor-60m-20261020"))
    from transfer import energy, neighborhood
    predecessor = json.loads((ROOT / "research/donor-60m-20261020/transfer/candidates.json").read_text())
    known = {(r["N"], r["canonical"]) for r in predecessor}
    overlaps = []
    for r in records:
        if not r["below_published"]:
            continue
        bits = sources[r["source_index"]]["sequence"]
        oriented = "".join(str(1 - int(b)) if i % 2 else b for i, b in enumerate(bits))
        for _, _, sequence in neighborhood(oriented, r["operation"]):
            e = energy(sequence)
            if e < r["published_E"]:
                obj = dict(N=r["N"], E=e, sequence=sequence)
                exact = verify_object(obj)
                xor_check(obj)
                overlaps.append((r["N"], exact["canonical"]))
    assert len(overlaps) == summary["below_published"]
    assert all(key in known for key in overlaps)
    assert any(s["N"] == 518 and s["canonical"] == best["518"]["canonical"] for s in sources)
    print(f"PASS: all {len(overlaps)} below-published attempts are in {len(set(overlaps))} predecessor candidate orbits; N=518 best is a published symmetry tie")
    if self_check:
        bad_energy = copy.deepcopy(records)
        bad_energy[0]["best"]["E"] += 4
        bad_count = copy.deepcopy(records)
        bad_count[0]["generated"] += 1
        for broken in (bad_energy, bad_count, records[:-1]):
            try:
                validate(broken, best, candidates, summary, sources, frontier, pending)
            except (AssertionError, ValueError):
                continue
            raise AssertionError("corrupted evidence accepted")
        print("PASS: false energy, incorrect denominator and missing group rejected")
    if replay:
        with tempfile.TemporaryDirectory(prefix="alternating-replay-", dir=ROOT.parent) as temp:
            out = Path(temp) / "results"
            subprocess.run([sys.executable, str(HERE / "sweep.py"), "--output", str(out),
                            "--stop-at", "2099-01-01T00:00:00Z"], check=True, timeout=600)
            for name in ("groups.jsonl", "best.json", "candidates.json"):
                assert (out / name).read_bytes() == (result / name).read_bytes(), name
            actual = json.loads((out / "summary.json").read_text())
            for key in summary.keys() - {"cpu_seconds", "wall_seconds", "finished_at"}:
                assert actual[key] == summary[key], key
        print("PASS: full replay matches every ordered trial digest, histogram, certificate and non-timing aggregate")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--replay", action="store_true")
    parser.add_argument("--self-check", action="store_true")
    args = parser.parse_args()
    main(args.replay, args.self_check)
