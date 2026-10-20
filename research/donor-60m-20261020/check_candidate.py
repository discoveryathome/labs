#!/usr/bin/env python3
"""Reconstruct one candidate directly from its credited published parent."""
import argparse
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path[:0]=[str(ROOT/"src"),str(ROOT/"scripts")]
from verify import verify_object, score
from independent_check import check


def main(n):
    candidate=json.loads((HERE/f"candidates/{n}.json").read_text())
    source=json.loads((ROOT/"data/published.json").read_text())[candidate["source_index"]]
    verify_object(source);check(source)
    b=source["sequence"];op=candidate["endpoint_identity"]["operation"]
    if op=="delete_first": derived=b[1:]
    elif op=="delete_last": derived=b[:-1]
    elif op.startswith("prepend_"): derived=op[-1]+b
    elif op.startswith("append_"): derived=b+op[-1]
    else: raise ValueError("unsupported endpoint operation")
    exact=verify_object(candidate);check(candidate)
    constructed=score(derived)
    if (constructed["canonical"],constructed["E"])!=(exact["canonical"],exact["E"]):
        raise ValueError("parent reconstruction failed")
    row=next(r for r in json.loads((ROOT/"data/frontier.json").read_text()) if r["N"]==n)
    reference=json.loads((ROOT/row["object"]).read_text())
    verify_object(reference);check(reference)
    if candidate["reference_E"]!=reference["E"] or exact["E"]>=reference["E"]:
        raise ValueError("not a strict improvement over the pinned comparator")
    published=json.loads((ROOT/"data/published.json").read_text())
    if exact["E"]>=min(r["E"] for r in published if r["N"]==n):
        raise ValueError("does not beat every imported construction")
    print(f"PASS N={n}: parent N={source['N']} E={source['E']} via {op}; "
          f"published E={reference['E']} -> candidate E={exact['E']}; "
          f"F={exact['F_exact']}. Independent novelty review remains pending.")


if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--n",type=int,required=True)
    main(p.parse_args().n)
