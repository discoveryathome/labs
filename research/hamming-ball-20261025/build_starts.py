#!/usr/bin/env python3
"""Build the preregistered start list: identity or one endpoint edit of every published
and pending parent, kept when the start length is an audited open length."""
import hashlib, json, sys
from collections import Counter
from pathlib import Path

S = Path(sys.argv[1]); ROOT = S / "repo"
sys.path.insert(0, str(ROOT / "src"))
from verify import canonical, parse_sequence

OPS = ("identity", "delete_first", "delete_last", "prepend_0", "prepend_1", "append_0", "append_1")
SUGGESTED_N = 451

def edit(bits, op):
    if op == "identity": return bits
    if op == "delete_first": return bits[1:]
    if op == "delete_last": return bits[:-1]
    if op.startswith("prepend_"): return op[-1] + bits
    if op.startswith("append_"): return bits + op[-1]
    raise ValueError(op)

def energy(bits):
    n, x = len(bits), int(bits, 2)
    return sum((n-k-2*((x^(x>>k))&((1<<(n-k))-1)).bit_count())**2 for k in range(1, n))

published = json.loads((ROOT/"data/published.json").read_text())
frontier = {r["N"]: r for r in json.loads((ROOT/"data/frontier.json").read_text()) if r["bound"] is None}
donor = json.loads((ROOT/"research/donor-60m-20261020/candidate-table.json").read_text())
pr7 = json.loads((S/"inputs/pr7-candidates.json").read_text())

parents = [dict(kind="published", ref=f"data/published.json#{i}", N=p["N"], bits=p["sequence"], E=p["E"])
           for i, p in enumerate(published)]
for r in donor:
    o = json.loads((ROOT/r["object"]).read_text())
    parents.append(dict(kind="pending-donor", ref=r["object"], N=o["N"], bits=o["sequence"], E=o["E"]))
for i, c in enumerate(pr7):
    parents.append(dict(kind="pending-pr7", ref=f"pr7:research/two-endpoint-20261022/results/candidates.json#{i}",
                        N=c["N"], bits=c["sequence"], E=c["E"]))
for p in parents:
    assert len(p["bits"]) == p["N"] and energy(p["bits"]) == p["E"], p["ref"]

threshold = {n: r["E"] for n, r in frontier.items()}
for r in donor: threshold[r["N"]] = min(threshold[r["N"]], r["candidate_E"])
for c in pr7: threshold[c["N"]] = min(threshold[c["N"]], c["E"])

known = {}
for p in parents:
    known.setdefault(p["N"], set()).add(canonical(parse_sequence(p["bits"])))

starts, ops = [], Counter()
for pi, p in enumerate(parents):
    for op in OPS:
        b = edit(p["bits"], op); n = len(b)
        if n not in threshold: continue
        e = energy(b)
        starts.append(dict(id=len(starts), N=n, bits=b, E=e, T=threshold[n], gap=e-threshold[n],
                           radius=3, parent=pi, parent_kind=p["kind"],
                           parent_ref=p["ref"], parent_N=p["N"], parent_E=p["E"], op=op))
        ops[op] += 1

with open(S/"run/starts.tsv", "w") as f:
    for s in starts:
        f.write(f'{s["id"]}\t{s["N"]}\t{s["radius"]}\t{s["T"]}\t{s["E"]}\t{s["bits"]}\n')
(S/"run/starts.json").write_text(json.dumps(starts, indent=0) + "\n")
(S/"run/thresholds.json").write_text(json.dumps({str(k): v for k, v in sorted(threshold.items())}, indent=1) + "\n")
(S/"run/known-canonical.json").write_text(json.dumps({str(k): sorted(v) for k, v in sorted(known.items())}) + "\n")

def ball(n, r):
    from math import comb
    return sum(comb(n, i) for i in range(r+1))
cost = sum(s["N"]**3/2 if s["radius"] == 2 else s["N"]**4/6 for s in starts)
gaps = sorted(s["gap"] for s in starts)
covered = sorted({s["N"] for s in starts})
print(json.dumps(dict(parents=len(parents), parent_kinds=Counter(p["kind"] for p in parents),
    starts=len(starts), ops=ops, lengths_covered=len(covered), open_lengths=len(threshold),
    missing=sorted(set(threshold)-set(covered)),
    sequences=sum(ball(s["N"], s["radius"]) for s in starts),
    radius3_starts=sum(s["radius"] == 3 for s in starts),
    inner_ops_estimate=f"{cost:.3g}",
    gap_min=gaps[0], gap_p10=gaps[len(gaps)//10], gap_median=gaps[len(gaps)//2],
    starts_gap_le_50=sum(g <= 50 for g in gaps), starts_gap_le_0=sum(g <= 0 for g in gaps),
    closest=[(s["N"], s["op"], s["parent_kind"], s["gap"]) for s in sorted(starts, key=lambda s: s["gap"])[:12]],
    sha256={str(p.relative_to(S)): hashlib.sha256(p.read_bytes()).hexdigest() for p in
            [ROOT/"data/published.json", ROOT/"data/frontier.json",
             ROOT/"research/donor-60m-20261020/candidate-table.json", S/"inputs/pr7-candidates.json",
             S/"mine/build_starts.py"]}), indent=1, default=str))
