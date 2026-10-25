#!/usr/bin/env python3
"""Rescore the Hamming-ball results from scratch with both repository checkers and summarize.

Usage: verify_results.py SESSION_DIR OUT_DIR
Every per-start shell minimum gets both checkers; strided samples get the independent
XOR checker, and the first three per start also get src/verify.py. Any below-threshold hit
gets both checkers plus a canonical-orbit comparison against all known witnesses.
"""
import json, sys
from collections import defaultdict
from math import comb
from multiprocessing import Pool
from pathlib import Path

S, OUT = Path(sys.argv[1]), Path(sys.argv[2])
ROOT = S / "repo"
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "scripts")]
from verify import verify_object, canonical, parse_sequence
from independent_check import check as xor_check

starts = {s["id"]: s for s in json.loads((S / "run/starts.json").read_text())}
known = {int(k): set(v) for k, v in json.loads((S / "run/known-canonical.json").read_text()).items()}
RES = Path(sys.argv[3]) if len(sys.argv) > 3 else S / "run/results.jsonl"
results = [json.loads(l) for l in RES.read_text().splitlines() if l.strip()]


def apply(bits, flips):
    b = list(bits)
    for i in flips:
        b[i] = "1" if b[i] == "0" else "0"
    return "".join(b)


def both(job):
    seq, e = job
    obj = dict(N=len(seq), E=e, sequence=seq)
    verify_object(obj)
    xor_check(obj)
    return 1


def xor_only(job):
    seq, e = job
    xor_check(dict(N=len(seq), E=e, sequence=seq))
    return 1


both_jobs, xor_jobs, below, problems = [], [], [], []
per_length = defaultdict(lambda: dict(best=None, starts=0, evaluated=0, ties=0, tie_orbits=set()))
total_eval = 0
for r in results:
    st = starts[r["id"]]
    n, bits = st["N"], st["bits"]
    want = sum(comb(n, i) for i in range(r["radius"] + 1))
    if not (r["evaluated"] == r["expected"] == want and r["E_start"] == st["E"] and r["T"] == st["T"]):
        problems.append(("accounting", r["id"]))
    total_eval += r["evaluated"]
    L = per_length[n]
    L["starts"] += 1; L["evaluated"] += r["evaluated"]; L["ties"] += r["ties"]
    cands = [(st["E"], [], "start")] + [(r[k]["E"], r[k]["flips"], k) for k in ("min1", "min2", "min3") if r[k]]
    for e, flips, k in cands:
        if k != "start":
            both_jobs.append((apply(bits, flips), e))
        if L["best"] is None or e < L["best"]["E"]:
            L["best"] = dict(E=e, start=r["id"], flips=flips, op=st["op"], parent_kind=st["parent_kind"],
                             parent_N=st["parent_N"])
    for z, h in enumerate(r["samples"]):
        (both_jobs if z < 3 else xor_jobs).append((apply(bits, h["flips"]), h["E"]))
    for h in r["below_hits"]:
        seq = apply(bits, h["flips"])
        both_jobs.append((seq, h["E"]))
        key = canonical(parse_sequence(seq))
        below.append(dict(N=n, E=h["E"], T=st["T"], start=r["id"], flips=h["flips"], sequence=seq,
                          canonical=key, known=key in known.get(n, set())))
    if r["below"] > len(r["below_hits"]):
        problems.append(("below-cap-hit", r["id"]))
    for h in r["tie_hits"]:
        L["tie_orbits"].add(canonical(parse_sequence(apply(bits, h["flips"]))))

with Pool(2) as pool:
    n_both = sum(pool.map(both, both_jobs, chunksize=16))
    n_xor = sum(pool.map(xor_only, xor_jobs, chunksize=64))

# Corruption controls: the checkers must reject a wrong energy and a one-bit change.
controls = 0
seq0, e0 = both_jobs[0]
for bad in [(seq0, e0 + 4), (apply(seq0, [len(seq0) // 2]), e0)]:
    try:
        both(bad)
    except (AssertionError, ValueError):
        controls += 1
assert controls == 2, "corruption control not rejected"

rows = []
for n in sorted(per_length):
    L = per_length[n]
    T = starts[next(i for i in starts if starts[i]["N"] == n)]["T"]
    new_tie_orbits = sorted(L["tie_orbits"] - known.get(n, set()))
    rows.append(dict(N=n, threshold_E=T, best_E_in_domain=L["best"]["E"], gap=L["best"]["E"] - T,
                     best=L["best"], starts=L["starts"], evaluated=L["evaluated"], ties=L["ties"],
                     tie_orbits_recorded=len(L["tie_orbits"]),
                     tie_orbits_not_previously_known=len(new_tie_orbits)))

summary = dict(
    results=len(results), starts=len(starts), evaluated=total_eval,
    accounting_problems=problems, corruption_controls_rejected=controls,
    rescored_both_checkers=n_both, rescored_independent_only=n_xor,
    below_threshold=len(below), below_threshold_new_orbits=sum(not b["known"] for b in below),
    lengths=len(rows), lengths_tied=sum(r["gap"] == 0 for r in rows),
    lengths_below=sum(r["gap"] < 0 for r in rows),
    suggested_N451=[r for r in rows if r["N"] == 451],
)
OUT.mkdir(parents=True, exist_ok=True)
(OUT / "summary.json").write_text(json.dumps(summary, indent=1) + "\n")
(OUT / "per-length.json").write_text(json.dumps(rows, indent=1) + "\n")
(OUT / "below-threshold.json").write_text(json.dumps(below, indent=1) + "\n")
print(json.dumps(summary, indent=1))
