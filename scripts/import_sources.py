#!/usr/bin/env python3
"""Rebuild certificates from pinned, offline primary-source snapshots and extracted tables."""
import hashlib
import argparse
import json
import sys
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from verify import score
from html_tables import Tables


def build(check=False):
    def emit(path, obj):
        content = json.dumps(obj, indent=2, ensure_ascii=False)+"\n"
        if check:
            assert path.read_text() == content, f"derived artifact differs: {path}"
        else:
            path.write_text(content)
    sources = json.loads((ROOT / "data/sources/manifest.json").read_text())
    urls = {}
    for item in sources:
        p = ROOT / item["path"]
        # "stored": false entries are cited by URL and hash only; their factual
        # data is read from the extracted file that names them in "extracted_from".
        if item.get("stored", True):
            assert hashlib.sha256(p.read_bytes()).hexdigest() == item["sha256"], p
        urls[p.name] = item["url"]
    cited = {item["path"]: item for item in sources}
    records = []

    def add(n, sequence, name, by, date, energy=None, f=None, optimum=False):
        result = score(sequence)
        assert result["N"] == n, (name, n, result["N"])
        if energy is not None:
            assert result["E"] == energy, (name, n, result["E"], energy)
        if f is not None:
            # Published decimal tables are rounded (some entries truncated).
            tolerance = Decimal(10) ** -len(f.split(".")[-1])
            actual = Decimal(n*n) / Decimal(2*result["E"])
            assert abs(actual - Decimal(f)) <= tolerance, (name, n, actual, f)
        records.append(dict(N=n, sequence=sequence, E=result["E"],
                            F_exact=result["F_exact"], canonical=result["canonical"],
                            source=urls[name], source_file="data/sources/"+name,
                            by=by, updated=date, optimum=optimum))

    add(2, "01", "optimal.html", "Elementary parity bound", "2016-04-01", 1, optimum=True)
    # Factual table rows extracted from arXiv:1512.02475; the paper is not stored.
    optimal = json.loads((ROOT/"data/sources/optimal-table.json").read_text())
    assert optimal["source"]["sha256"] == cited["data/sources/optimal.html"]["sha256"]
    assert optimal["columns"] == ["N", "E", "FN", "sequences", "skew"]
    seen = set()
    for r in optimal["rows"]:
        if len(r) < 4 or not r[0].isdigit():
            continue
        n = int(r[0])
        if n in seen:
            continue
        seen.add(n)
        s = "".join(("1" if i % 2 == 0 else "0") * int(c, 36)
                    for i, c in enumerate(r[3]))
        add(n, s, "optimal.html", "Packebusch and Mertens", "2016-04-01",
            int(r[1]), optimum=True)
    for line in (ROOT/"data/sources/2018-skew.txt").read_text().splitlines()[1:]:
        r = line.split()
        if len(r) == 4:
            add(int(r[0]), r[3], "2018-skew.txt", "Bošković, Brglez and Brest archive",
                "2018-01-01", int(r[2]), r[1])
    tables = Tables((ROOT/"data/sources/memetic2025.html").read_text()).tables
    table = next(t for t in tables if t and t[0][:3] == ["N", "Old E", "New E"])
    n = energy = None
    for r in table[1:]:
        if len(r) != 7:
            continue
        if r[0]:
            n, energy = int(r[0]), int(r[2])
        width = (n+3)//4*4
        bits = format(int(r[5], 16), f"0{width}b")
        assert len(bits) == width and set(bits[n:]) <= {"0"}
        add(n, bits[:n], "memetic2025.html", "Zhang, Shen, Kumar and Pistoia",
            "2025-08-14", energy)
    for name, date, by in [
        ("dual-step.html", "2024-09-11", "Pšeničnik, Mlinarič, Brest and Bošković"),
        ("2026.html", "2026-07-14", "Pšeničnik, Bošković, Popič and Brest"),
    ]:
        tables = Tables((ROOT/"data/sources"/name).read_text()).tables
        table = next(t for t in tables if len(t) > 30 and t[0][0] == "L")
        for r in table:
            if len(r) != 4 or not r[0].isdigit():
                continue
            n = int(r[0])
            bits = format(int(r[3].replace("allowbreak", "").replace(" ", ""), 16), f"0{n}b")
            assert len(bits) == n
            add(n, bits, name, by, date, f=r[2])

    # The 2018 archive is reproduced, but is not asserted current outside audited cases.
    eligible = {r["N"] for r in records if r["source_file"].split("/")[-1] != "2018-skew.txt"}
    frontier = []
    for n in sorted(eligible):
        choices = [r for r in records if r["N"] == n]
        best = min(choices, key=lambda r: (r["E"], not r["optimum"]))
        row = {k: best[k] for k in ("N", "E", "F_exact", "source", "by", "updated")}
        row.update(object=f"data/witnesses/{n}.json",
                   status="proven-optimal (literature)" if n <= 66 else "best-verified-published",
                   bound=best["E"] if n <= 66 else None,
                   audited_on="2026-10-20",
                   target=n in (92, 99, 107, 119, 450, 451, 518, 573))
        frontier.append(row)
        p = ROOT/row["object"]
        p.parent.mkdir(exist_ok=True)
        emit(p, best)
    emit(ROOT/"data/published.json", records)
    emit(ROOT/"data/frontier.json", frontier)
    print(f"Imported {len(records)} witnesses; {len(frontier)} frontier lengths")


if __name__ == "__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--check",action="store_true")
    build(p.parse_args().check)
