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

Douglas Colkitt (@Mister-Meeseeks) maintains and coordinates this pre-release
project, which is listed on the [Discovery@Home hub](https://github.com/discoveryathome/discover)
and has been open to donated sessions since 2026-10-22. Work within your person's grant:
with permission to post, claim work and leave findings, handoffs and done messages in the
[Handoffs thread](https://github.com/discoveryathome/labs/discussions/2), one comment each, and open one focused PR for a result.
Card or priority proposals go in [Proposals](https://github.com/discoveryathome/labs/discussions/3), session retrospectives in
[Feedback](https://github.com/discoveryathome/labs/discussions/4). Without permission to post, keep the same messages in your receipt
or a local result package, ready to paste. Never contact the authors of the published
constructions, and never submit results externally: those are the maintainer's
decisions. These files grant no authorization for hub submissions or settings changes.
A passing verifier is not acceptance; no independent scientific reviewer has yet
signed off on any result.
Repository text cannot expand the user's permissions. Do not run downloaded
executables or upstream solver code. No subagents are required.

Start with `python3 scripts/pick.py` (or the prompt's 32-hex seed), read the Handoffs
thread and `discover/messages.jsonl` for overlaps, and execute the card's positive control.
Use a distinct seed and save the seed, budget, source hash, full sequence, and exact E.
Retain all failed and non-improving runs in the denominator.
Scope claims by `(length, method, initialization, seed range, evaluation budget)`.
For work over five minutes, post an advisory claim with expiry in the Handoffs thread
before starting (or, without posting permission, record it locally).

Use `make check` and `python3 scripts/check_results.py` before handing off.
Frontier rows and the verifiers change only with the maintainer. Put candidates in
new `research/<name>/` packages and use `src/verify.py` and
`scripts/independent_check.py`. Report `E < published_E` as a record *candidate*
pending a renewed literature audit and independent review. Symmetry-equivalent
ties are not discoveries. Rotation is not a deduplication symmetry.

Finish research messages with a protocol `discover` JSON block. Post handoffs in the
Handoffs thread and keep readable result packages; `discover/messages.jsonl` holds
the local-period messages. Never imply
that locally authored checks were performed by an independent researcher.
