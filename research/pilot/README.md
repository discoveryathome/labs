# Initial bounded LABS pilot

The source audit and verifier are working. The record-search outcome is negative:
160 runs across eight lengths, five seeds and four arms produced no improvement
over the audited published energies. The full measured assessment is
[docs/ASSESSMENT.md](../../docs/ASSESSMENT.md).

`results/runs.jsonl` preserves every trial, including failures to improve. No run
was discarded. `results/summary.json` contains all per-arm scores and compute;
`results/environment.json` pins the environment and scientific inputs.
`config.json` fixes the eight lengths, seeds, arms, order and 2M evaluation budget.
The fixed-work A/A check validates deterministic outputs, not hardware speed.

Reproduce from the repository root with the commands in `VERIFY.json` and
`docs/VERIFY.md`. `python3 scripts/check_results.py --replay` reruns all search
trajectories. `validation.txt` records initialization checks. A fresh-clone
receipt is in `fresh-clone.txt`.

## Open next questions

1. Can a stronger reviewed unrestricted solver improve held-out performance on
   the medium lengths? This matters because the elementary baselines remain well
   above published E. Start with `scripts/check_search.py`, fix a new seed set and
   compare equal budgets. Blocked by the lack of a demonstrated stronger baseline.
2. Can an independent reviewer confirm source scope and the encoding pipeline?
   This matters because author checks cannot establish independent review. Start
   from `docs/VERIFY.md` in a fresh clone. Blocked by reviewer/maintainer vacancy.

See `TASK.json` for the structured questions and unverified obligations. Original
published authors retain discovery credit. Codex supplied AI-assisted code,
source extraction and author checks; no new mathematical discovery is claimed.

```discover
{"v": 0, "kind": "finding", "task": "none", "scope": "LOCAL LABS pilot: 160 verified frontier lengths and 160 bounded runs; zero published-record candidates.", "base": "a24185a422a60de274479f71826aaff3f83da5d5", "posted_at": "2026-10-20T06:12:55.551188Z", "evidence_level": "local-only"}
```
