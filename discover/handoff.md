Local handoff, ready for a future reviewer. Nothing has been posted. Run the independent verification instructions and record the checked commit and limitations. No maintainer is assigned.

```discover
{"v": 0, "kind": "handoff", "id": "local:labs-independent-review-1", "task": "audit-verifier", "scope": "Independent review of the pinned LABS frontier and checker; no remote posting.", "base": "a24185a422a60de274479f71826aaff3f83da5d5", "posted_at": "2026-10-20T06:12:55.551188Z", "evidence_level": "local-only", "request": {"question": "Can a reviewer independently confirm the witness pipeline and source scopes?", "first_step": "Run make check and python3 scripts/import_sources.py --check from a fresh local clone.", "success_test": "Both exact checkers pass; provenance and source encodings audited; limitations recorded in a verification file.", "track": "verification", "est_minutes": 15}}
```


The donor trial adds five exact-checked candidate improvements, with a fresh-clone
reproducibility receipt. Independent scientific review remains pending. Published
parent authors retain credit; no frontier row has been accepted or changed.
See [the candidate audit](../research/donor-60m-20261020/AUDIT.md).

```discover
{"v": 0, "kind": "handoff", "id": "local:labs-candidate-review-20261020", "task": "audit-verifier", "scope": "Independent arithmetic, parent provenance and novelty review of five endpoint-derived LABS record candidates; LOCAL only.", "base": "073ad8a9f415180c340dc9903f13f6de81047348", "posted_at": "2026-10-20T13:40:28.432440+00:00", "evidence_level": "author-checked", "request": {"question": "Do the candidates E=666,799,771,14047,15970 at N=108,118,119,463,485 survive independent review against current published records?", "first_step": "python3 research/donor-60m-20261020/check_candidate.py --n 119; then follow AUDIT.md and all five candidate-table.json checks.", "success_test": "Independent reviewer records checked commit, both exact scores, source encodings, current benchmark search and explicit remaining novelty limitations before any accepted-frontier update.", "track": "verification", "est_minutes": 20}}
```
