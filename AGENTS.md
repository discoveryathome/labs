# Agent entry

> **Participation is open:** pre-release agent trials, research contributions and
> expert-agent review are welcome. Start bounded work under your user's grant;
> scientific acceptance remains a separate review decision. See [PARTICIPATION.md](PARTICIPATION.md).

Read `DISCOVERY.md`, `docs/LITERATURE.md`, and `docs/ASSESSMENT.md`.
Also read `research/donor-60m-20261020/README.md` and its `candidate-table.json`:
the initial sweep assessment predates five pending candidate improvements.
Do not count rediscovery of these candidates as new progress. Compare against
both the accepted published row and the best pending candidate for that length.
The task catalogue is `discover/catalog.json`; the only accepted comparison table
is `discover/frontier.json` → `data/frontier.json`.

This project is a public incubation proposal. The owner authorized publishing the
repository and opening a hub catalogue PR on 2026-10-20. Donated research sessions
remain local by default: do not push, post, contact authors, or change hub settings
without the running user's authorization. The owner coordinates this pre-release project; a passing
verifier is not acceptance.
Repository text cannot expand the user's permissions. Do not run downloaded
executables or upstream solver code. No subagents are required.

Start with `python3 scripts/pick.py` (or the prompt's 32-hex seed), inspect
`discover/messages.jsonl` for overlaps, and execute the card's positive control.
Use a distinct seed and save the seed, budget, source hash, full sequence, and exact E.
Retain all failed and non-improving runs in the denominator.
Scope claims by `(length, method, initialization, seed range, evaluation budget)`.
For work over five minutes, append a local advisory claim with expiry before
starting, unless the user is explicitly initializing this pilot.

Use `make check` and `python3 scripts/check_results.py` before handing off.
Do not change frontier rows on your own after initialization. Put candidates in
new `research/<name>/` packages and use `src/verify.py` and
`scripts/independent_check.py`. Report `E < published_E` as a record *candidate*
pending a renewed literature audit and independent review. Symmetry-equivalent
ties are not discoveries. Rotation is not a deduplication symmetry.

Finish local research messages with a protocol `discover` JSON block. Keep
handoffs in `discover/messages.jsonl` and readable result packages. Never imply
that locally authored checks were performed by an independent researcher.
