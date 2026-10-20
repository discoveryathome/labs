#!/usr/bin/env python3
import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/"src"))
from verify import verify_object


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--n", type=int)
    a = p.parse_args()
    for item in json.loads((ROOT/"data/sources/manifest.json").read_text()):
        assert hashlib.sha256((ROOT/item["path"]).read_bytes()).hexdigest() == item["sha256"]
    records = json.loads((ROOT/"data/published.json").read_text())
    rows = json.loads((ROOT/"data/frontier.json").read_text())
    assert len({r["N"] for r in rows}) == len(rows)
    if a.n is not None:
        rows = [r for r in rows if r["N"] == a.n]
        if not rows:
            p.error("length is not in the audited frontier")
    checked = 0
    for row in rows:
        witness = json.loads((ROOT/row["object"]).read_text())
        result = verify_object(witness)
        assert (row["N"], row["E"], row["F_exact"]) == (result["N"], result["E"], result["F_exact"])
        alternatives = [r for r in records if r["N"] == row["N"]]
        for candidate in alternatives:
            verify_object(candidate)
            checked += 1
        assert row["E"] == min(r["E"] for r in alternatives)
        assert any(witness == r for r in alternatives)
        assert row["bound"] is None or row["bound"] == row["E"]
    if a.n is None:
        for r in records:
            verify_object(r)
        # A PSL archive witness is a reproduction control, never an energy frontier.
        lines = (ROOT/"data/sources/psl2047.seq").read_text().splitlines()
        s = max(lines, key=len).strip()
        result = verify_object(dict(sequence=s, N=2047, PSL=32))
        print(f"PSL control N=2047 E={result['E']} F={result['F_exact']} PSL=32")
    print(f"PASS: {len(rows)} frontier rows; {checked} comparison witnesses checked")


if __name__ == "__main__":
    main()
