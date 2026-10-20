#!/usr/bin/env python3
"""Classify a candidate against the audited published frontier without changing it."""
import argparse
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from verify import verify_object

p=argparse.ArgumentParser()
p.add_argument("certificate",type=Path)
a=p.parse_args()
r=verify_object(json.loads(a.certificate.read_text()))
rows={x["N"]:x for x in json.loads((ROOT/"data/frontier.json").read_text())}
if r["N"] not in rows:
    p.error("No audited row for this length; first establish a current published comparator")
row=rows[r["N"]]
reference=verify_object(json.loads((ROOT/row["object"]).read_text()))
if r["E"]<reference["E"]:
    status="published-record-candidate; refresh sources and obtain independent review"
elif r["E"]==reference["E"]:
    status="energy tie; not an energy record"
else:
    status="above published frontier; internal-baseline result only"
known=[x for x in json.loads((ROOT/"data/published.json").read_text()) if x["N"]==r["N"]]
duplicate=any(verify_object(x)["canonical"]==r["canonical"] for x in known)
print(json.dumps(dict(N=r["N"],E=r["E"],F_exact=r["F_exact"],
                     published_E=reference["E"],gap_E=r["E"]-reference["E"],
                     known_symmetry_orbit=duplicate,status=status),indent=2))
