#!/usr/bin/env python3
"""Validate the result package's pinned live inputs without invoking git."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
package=json.loads((ROOT/"research/pilot/SOURCES.json").read_text())
for item in package["files"]:
    data=(ROOT/item["path"]).read_bytes()
    assert hashlib.sha256(data).hexdigest()==item["sha256"],item["path"]
    blob=b"blob "+str(len(data)).encode()+b"\0"+data
    assert hashlib.sha1(blob).hexdigest()==item["git_blob"],item["path"]
meta=json.loads((ROOT/"research/pilot/results/environment.json").read_text())
config=(ROOT/"research/pilot/config.json").read_bytes()
assert hashlib.sha256(config).hexdigest()==meta["config_sha256"]
assert json.loads(config)==meta["config"]
print(f"PASS: {len(package['files'])} pinned package inputs and config")
