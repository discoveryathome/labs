#!/usr/bin/env python3
"""Weighted seeded picker. Advisory: a draw does not reserve work; check the Handoffs thread first."""
import argparse
import datetime
import json
from pathlib import Path
import re
import secrets

p=argparse.ArgumentParser()
p.add_argument("--seed",default=None)
a=p.parse_args()
seed=a.seed or secrets.token_hex(16)
if not re.fullmatch("[0-9a-fA-F]{32}",seed):
    p.error("seed must be 32 hexadecimal digits")
root=Path(__file__).resolve().parents[1]
catalog=json.loads((root/"discover/catalog.json").read_text())
draw=int(seed[:8],16)%100
for track in catalog["tracks"]:
    if draw<track["weight"]:break
    draw-=track["weight"]
task=track["tasks"][int(seed[8:16],16)%len(track["tasks"])]
now=datetime.datetime.now(datetime.timezone.utc)
messages=[json.loads(x) for x in (root/"discover/messages.jsonl").read_text().splitlines() if x.strip()]
closed={m.get("responds_to") for m in messages if m["kind"]=="done"}
claims=[m for m in messages if m["kind"]=="claim"
        and datetime.datetime.fromisoformat(m["expires"].replace("Z","+00:00"))>now
        and not any(d["kind"] in ("done","released") and d.get("task")==m.get("task")
                    and d["scope"]==m["scope"] and d["posted_at"]>m["posted_at"] for d in messages)]
handoffs=[m for m in messages if m["kind"]=="handoff" and m.get("id") not in closed
          and not any(c.get("responds_to")==m.get("id") for c in claims)]
rows=json.loads((root/"data/frontier.json").read_text())
targets=[r["N"] for r in rows if r["target"] and r["bound"] is None]
print(json.dumps(dict(seed=seed,track=track["id"],task=task["id"],
                     suggested_length=targets[int(seed[16:24],16)%len(targets)],
                     run_seed=int(seed[24:],16),
                     first_step=task["first_step"],live_claims=claims,open_handoffs=handoffs,
                     mode="open: pre-release contributions and expert-agent review; maintainer @Mister-Meeseeks",
                     coordination="Check the Handoffs thread (https://github.com/discoveryathome/labs/discussions/2) and these local-period messages before claiming"),indent=2))
