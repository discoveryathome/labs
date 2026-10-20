#!/usr/bin/env python3
"""Positive controls: fixed-work A/A, shared initial states and exact final scores."""
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from verify import verify_object

subprocess.run(["make","build"],cwd=ROOT,check=True,stdout=subprocess.DEVNULL)
for n in (13, 99, 451):
    outputs={}
    for method in ("hill","tabu"):
        cmd=[str(ROOT/"build/search"),str(n),"1729","20000",method]
        a,b=[json.loads(subprocess.check_output(cmd,text=True)) for _ in range(2)]
        verify_object(a);verify_object(b)
        for k in a:
            if k not in ("cpu_seconds","wall_seconds"):
                assert a[k]==b[k],k
        assert a["E"]<=a["initial_E"]
        outputs[method]=a
    assert outputs["hill"]["initial_E"]==outputs["tabu"]["initial_E"]
print("PASS: deterministic A/A and exact search checks")
