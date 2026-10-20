#!/usr/bin/env python3
"""A second exact checker using XOR/popcount; imports no pilot scoring/search code."""
import argparse
from fractions import Fraction
import json
from pathlib import Path


def check(obj):
    s=obj["sequence"]
    if not isinstance(s,str) or not s or set(s)-{"0","1"}:
        raise ValueError("expected nonempty 01 string")
    n=len(s)
    x=int(s,2)
    energy=0
    correlations=[]
    for k in range(1,n):
        # Equal bits contribute +1; unequal bits contribute -1.
        mismatches=((x^(x>>k))&((1<<(n-k))-1)).bit_count()
        c=n-k-2*mismatches
        correlations.append(c)
        energy+=c*c
    assert obj["N"]==n and obj["E"]==energy
    if "F_exact" in obj:
        assert obj["F_exact"]==(str(Fraction(n*n,2*energy)) if energy else "infinity")
    if "autocorrelations" in obj:
        assert obj["autocorrelations"]==correlations


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--file",type=Path)
    a=p.parse_args()
    root=Path(__file__).resolve().parents[1]
    if a.file:
        check(json.loads(a.file.read_text()));print("PASS: independent certificate check")
    else:
        objects=json.loads((root/"data/published.json").read_text())
        runfile=root/"research/pilot/results/runs.jsonl"
        if runfile.exists():
            objects += [json.loads(x) for x in runfile.read_text().splitlines()]
        for obj in objects:
            check(obj)
        print(f"PASS: independent XOR/popcount checked {len(objects)} certificates")
