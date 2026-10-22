# Two ordered endpoint edits

Written before scoring the new search domain. Session started
2026-10-22 20:17:32 UTC; budget 60 minutes; stop new work by 21:02:32 UTC and
reserve the final 15 minutes for verification and handoff.

Base: `1e65ddd66191355ba5fd86b9788d6c02e9329a82`.
OS-generated seed: `93610b14cdb3c9d4f2373623b04b0933`.
Repository picker: `refinement` / `published-refinement`, suggested N=119,
run seed 2957707571. The enumeration itself is deterministic.

Take the open [handoff](https://github.com/discoveryathome/labs/discussions/2#discussioncomment-19131784)
from [PR #6](https://github.com/discoveryathome/labs/pull/6), which completed the
alternating-parent single-edit extension. No other live claim or PR covers this
two-edit domain. That predecessor remains unmerged, and this new PR starts from
main. Its scientific results keep their existing author-checked status.

Question: can exactly two ordered endpoint operations from a published or pending
parent produce E below both same-length comparison thresholds?

Domain: the 319 rows in `data/published.json`, followed by the five full pending
certificates listed in `research/donor-60m-20261020/candidate-table.json` in file
order. The six operations, in order, are delete-first, delete-last, prepend-0,
prepend-1, append-0, append-1. Apply every ordered pair of operations, retaining
only final lengths in the 95 unbounded rows of `data/frontier.json`. Intermediate
lengths need not be frontier lengths. Invalid empty intermediates are skipped.
Retain repeated paths, undo paths and symmetry copies in the denominator; never
use rotations for deduplication. Original parent orientations suffice because
endpoint edits commute with negation, reversal and alternation up to operation
remapping and child symmetry; verify this claim on exhaustive small examples.

This follows the handoff's bounded family rather than only the suggested N=119;
report N=119 separately. No interior edits, search on new results as parents,
heuristic refinement, rotation-then-edit or adaptive expansion. Price the exact
domain and a longest-parent timing control before the full sweep. A budget
overrun means report partial coverage, never silently drop attempts.

Positive control: `check_candidate.py --n 119` passed with parent N=120 E=824,
published E=787 and pending E=771. Before new search, test operation composition
and symmetry closure on short binary inputs. Score every retained attempt with
both existing exact checker implementations if the timing probe permits.

Success requires strict E below `min(published_E, pending_E)` when a pending
candidate exists, canonical orbit deduplication, full parent reconstruction and
both exact checks. Before reporting a record candidate, refresh relevant primary
sources and compare against existing candidate orbits. Otherwise report the
finite negative result. No accepted frontier, verifier or solver changes.

Save all attempted paths and E, full best/candidate sequences, exact input/source
hashes and aggregate coverage. Replay must reproduce non-timing outputs exactly.
Falsifiers include missing paths, a wrong parent/edit, score mismatch, stale
threshold, incorrect count or false exhaustion claim. Invalidated claims must be
corrected and the verification evidence retained.

Credit the published witness authors, the original donor transfer implementation
and pending candidates, and the alternate-orientation session's handoff. AI
checks do not constitute independent scientific review or acceptance.
