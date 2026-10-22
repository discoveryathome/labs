#!/usr/bin/env python3
"""Reconstruct every path using deques, independently of the search enumerator."""
import argparse
from collections import Counter, deque
import copy
import hashlib
import itertools
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PREVIOUS = ROOT / "research/donor-60m-20261020"
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "scripts")]
from verify import verify_object
from independent_check import check as xor_check

# Deliberately separate from sweep.edit and sweep.paths: use deque operations.
OPERATIONS = (("delete_first", "left", None), ("delete_last", "right", None),
              ("prepend_0", "left", "0"), ("prepend_1", "left", "1"),
              ("append_0", "right", "0"), ("append_1", "right", "1"))


def children(sequence):
    for first, second in itertools.product(OPERATIONS, repeat=2):
        bits = deque(sequence)
        for _, side, value in (first, second):
            if value is None:
                if side == "left": bits.popleft()
                else: bits.pop()
            elif side == "left": bits.appendleft(value)
            else: bits.append(value)
            if not bits:
                break
        else:
            yield [first[0], second[0]], "".join(bits)


def load_parents():
    published = json.loads((ROOT / "data/published.json").read_text())
    table = json.loads((PREVIOUS / "candidate-table.json").read_text())
    parents = [dict(s, parent_kind="published", parent_object="data/published.json",
                    parent_row=i) for i, s in enumerate(published)]
    for row in table:
        obj = json.loads((ROOT / row["object"]).read_text())
        assert (obj["N"], obj["E"]) == (row["N"], row["candidate_E"])
        source = published[obj["source_index"]]
        bits = deque(source["sequence"])
        op = obj["endpoint_identity"]["operation"]
        if op == "delete_first": bits.popleft()
        elif op == "delete_last": bits.pop()
        elif op.startswith("prepend_"): bits.appendleft(op[-1])
        elif op.startswith("append_"): bits.append(op[-1])
        else: raise ValueError(op)
        ancestor = verify_object(dict(sequence="".join(bits)))
        assert (ancestor["E"], ancestor["canonical"]) == (obj["E"], obj["canonical"])
        parents.append(dict(obj, parent_kind="pending", parent_object=row["object"],
                            parent_row=None, by=source["by"]))
    for parent in parents:
        verify_object(parent)
        xor_check(parent)
    frontier = {r["N"]: r for r in json.loads((ROOT / "data/frontier.json").read_text()) if r["bound"] is None}
    pending = {r["N"]: r["candidate_E"] for r in table}
    return parents, frontier, pending


def reconstruct(parents, frontier, pending):
    records, best, candidates = [], {}, {}
    counts, groups, contributing = Counter(), set(), set()
    for index, parent in enumerate(parents):
        for operations, sequence in children(parent["sequence"]):
            n = len(sequence)
            if n not in frontier:
                continue
            exact = verify_object(dict(sequence=sequence))
            e = exact["E"]
            xor_check(dict(sequence=sequence, **exact))
            threshold = min(frontier[n]["E"], pending.get(n, frontier[n]["E"]))
            record = dict(parent=index, operations=operations, N=n, E=e,
                          sequence_sha256=hashlib.sha256(sequence.encode()).hexdigest(),
                          published_E=frontier[n]["E"], pending_E=pending.get(n), threshold_E=threshold)
            records.append(record)
            counts[str(n)] += 1
            groups.add((index, n))
            contributing.add(index)
            certificate = dict(record, sequence=sequence, F_exact=exact["F_exact"],
                               canonical=exact["canonical"], parent_kind=parent["parent_kind"],
                               parent_object=parent["parent_object"], parent_row=parent["parent_row"],
                               parent_N=parent["N"], parent_E=parent["E"],
                               source=parent["source"], by=parent["by"])
            if str(n) not in best or e < best[str(n)]["E"]:
                best[str(n)] = certificate
            if e < threshold:
                candidates.setdefault((n, exact["canonical"]), dict(certificate, **{
                    k: exact[k] for k in ("autocorrelations", "PSL", "canonical_sha256")}))
    plan = dict(parent_rows=len(parents), contributing_parents=len(contributing),
                eligible_targets=sorted(frontier), reachable_targets=sorted(map(int, counts)),
                trials_by_length=dict(counts), planned_trials=len(records))
    summary = dict(generated_paths=len(records), completed_parent_rows=len(parents),
                   exhausted=True, reached_lengths=len(counts), trials_by_length=dict(counts),
                   below_published=sum(r["E"] < r["published_E"] for r in records),
                   below_threshold=sum(r["E"] < r["threshold_E"] for r in records),
                   candidate_orbits=len(candidates))
    return records, best, list(candidates.values()), plan, summary, len(groups)


def validate(actual, expected):
    records, best, candidates, metadata, summary = actual
    expected_records, expected_best, expected_candidates, plan, totals, _ = expected
    assert records == expected_records, "ordered trial coverage, scores or provenance differ"
    assert best == expected_best, "best certificates differ"
    assert candidates == expected_candidates, "candidate certificates differ"
    assert metadata["plan"] == plan, "planned coverage differs"
    assert metadata["operations"] == [op[0] for op in OPERATIONS]
    for key, value in totals.items():
        assert summary[key] == value, key
    assert summary["exhausted"] is True


def main(self_check):
    metadata = json.loads((HERE / "results/metadata.json").read_text())
    for path, expected_hash in metadata["hashes"].items():
        assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == expected_hash, path
    manifest = json.loads((HERE / "SOURCES.json").read_text())
    for item in manifest["files"]:
        assert hashlib.sha256((ROOT / item["path"]).read_bytes()).hexdigest() == item["sha256"], item["path"]
    parents, frontier, pending = load_parents()
    expected = reconstruct(parents, frontier, pending)
    read = lambda name: json.loads((HERE / f"results/{name}.json").read_text())
    records = [json.loads(line) for line in (HERE / "results/trials.jsonl").read_text().splitlines()]
    actual = (records, read("best"), read("candidates"), metadata, read("summary"))
    validate(actual, expected)
    print(f"PASS: independent deque replay of {len(records)} paths / {expected[-1]} parent-length groups; every correlation and E checked by both implementations")
    print(f"PASS: {len(parents)} parent certificates and five pending-parent ancestor reconstructions; thresholds, exact witnesses, ordered coverage and hashes")
    known = json.loads((PREVIOUS / "transfer/candidates.json").read_text())
    published = json.loads((ROOT / "data/published.json").read_text())
    known_keys = {(r["N"], r["canonical"]) for r in known + published}
    for candidate in actual[2]:
        assert (candidate["N"], candidate["canonical"]) not in known_keys
    print(f"PASS: {len(actual[2])} improving orbits differ from every pinned published and predecessor candidate orbit")
    previous_best = json.loads((PREVIOUS / "transfer/best.json").read_text())
    for candidate in actual[2]:
        first = candidate["operations"][0]
        assert first.startswith("prepend_")
        intermediate = first[-1] + parents[candidate["parent"]]["sequence"]
        exact = verify_object(dict(sequence=intermediate))
        xor_check(dict(sequence=intermediate, **exact))
        assert any(r["canonical"] == exact["canonical"]
                   for r in previous_best[str(exact["N"])])
        print(f"PASS: N={candidate['N']} chains through predecessor N={exact['N']} E={exact['E']} orbit")
    predecessors = json.loads((HERE / "PREDECESSORS.json").read_text())
    prior_rows = predecessors["alternating_package"]["files"][0]["selected_rows"]
    assert predecessors["alternating_package"]["files"][1]["value"] == []
    for candidate in actual[2]:
        previous = next(r for r in prior_rows if r["N"] == candidate["N"])
        assert candidate["E"] < previous["E"]
        assert candidate["canonical_sha256"] != previous["canonical_sha256"]
    print("PASS: both candidates also beat the recorded PR #6 results at its pinned head")
    if self_check:
        corruptions = []
        for field, value in (("E", records[0]["E"] + 4), ("parent", -1),
                             ("operations", ["prepend_0", "prepend_1"])):
            broken = copy.deepcopy(actual)
            broken[0][0][field] = value
            corruptions.append(broken)
        broken = copy.deepcopy(actual)
        broken[0].pop()
        corruptions.append(broken)
        broken = copy.deepcopy(actual)
        broken[0].append(copy.deepcopy(broken[0][0]))
        corruptions.append(broken)
        broken = copy.deepcopy(actual)
        broken[4]["exhausted"] = False
        corruptions.append(broken)
        broken = copy.deepcopy(actual)
        broken[2].pop()
        corruptions.append(broken)
        for broken in corruptions:
            try:
                validate(broken, expected)
            except AssertionError:
                continue
            raise AssertionError("corrupted artifact accepted")
        print(f"PASS: {len(corruptions)} corruption controls (score, parent, operation order, missing/duplicate trial, incomplete run, missing candidate)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-check", action="store_true")
    main(parser.parse_args().self_check)
