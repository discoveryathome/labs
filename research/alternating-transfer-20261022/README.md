# Alternating-parent transfers: a bounded negative result

**No tested transfer improves the combined published and pending threshold.**
The complete preregistered sweep generated 168,646 one-edit attempts in 261
groups. Twelve attempts beat the older published values, but all belong to eight
candidate symmetry orbits already recorded by the predecessor. None improves
the five pending best energies. At the seed-suggested N=518, 2,591 attempts
produce a best E=18,463: a symmetry copy of an imported published witness.

This closes the alternate-orientation follow-up proposed by
[the previous donor session](../donor-60m-20261020/README.md), for the pinned
published-parent family. It is **author-checked experimental evidence**, not an
impossibility theorem, an independently reviewed result, or a new energy record.

## Exact scope

Base commit: `1e65ddd66191355ba5fd86b9788d6c02e9329a82`.
Seed: `5df0b3ec35686ccb18f43aaee9f741e4`; picker track/card:
`refinement` / `published-refinement`; suggested N=518, run seed 3925295588.
The experiment is deterministic. The seed selects the task, not search restarts.

The input corpus has 319 published rows. Of these, 139 have an eligible adjacent
target length. Each parent is alternated by flipping bits at odd zero-based
positions, then every deletion and every insertion of either sign is evaluated.
The declared target set has 95 open lengths; 94 are reachable. N=573 has no
adjacent published parent in this corpus and received zero trials.

- 129 deletion groups: 55,538 attempts.
- 132 insertion groups: 113,108 attempts.
- 261 completed groups: 168,646 attempts, including duplicate sequences and
  equivalent symmetry orbits. These are attempt counts, not unique discoveries.
- One exhaustive search run: 46.837 CPU seconds / 47.099 wall seconds. Input
  hashing precedes those timers; controls, review and replay are additional costs
  recorded in [verification.txt](verification.txt). Published-parent discovery
  costs are not included; this is conditional refinement, not an algorithm race.

Every comparison uses `E < min(published_E, pending_E)` where a pending candidate
exists. All 261 group minima, including non-improvements, have full witnesses,
exact autocorrelations and rational merit factors in
[results/groups.jsonl](results/groups.jsonl). Every group also retains its energy
histogram and an ordered digest of all `(position, bit, sequence, E)` trials.
[results/best.json](results/best.json) gives the best certificate per reached
length. [results/candidates.json](results/candidates.json) is intentionally empty.
Input and executable source hashes are in [results/metadata.json](results/metadata.json).

The twelve below-published attempts occur at N=108 (1), 118 (2), 119 (2),
463 (5), and 485 (2). Their best energies respectively equal the existing pending
666, 799, 771, 14047, and 15970. Some remaining attempts are worse than those
pending best values; the checker explicitly compares all twelve canonical keys
against the predecessor's eight saved candidate orbits.

## Why test this orientation?

Negation and reversal merely remap signs/positions when all possible insertions
and deletions are included. Alternation can change the child orbit: after
alternating the child back, an interior edit has also flipped the suffix signs.
For example, the parent `0000` alternates to `0101`; deleting position 1 gives
`001`, with E=1, whereas deleting any bit of the original gives `000`, with E=5.
Thus this is a distinct neighborhood, despite parent energy being preserved.

Original and alternating representatives suffice to cover all eight parent
symmetries for these one-edit operations, modulo child symmetry. This algebraic
observation does not make every generated child new: endpoint edits and edits
from different parents can overlap. Rotations were neither searched here nor
used as a deduplication symmetry. The predecessor's original-orientation sweep
was not replayed in full during this session.

## Reproduce and challenge

From the repository root, with Python 3.10+ and no external Python packages:

```sh
python3 research/alternating-transfer-20261022/sweep.py --self-check
python3 research/alternating-transfer-20261022/check.py --self-check --replay
```

The first command checks 5,112 short edit trials against direct integer scoring
and the XOR checker, alternation invariance, and rejection of a false energy.
The second checks pinned inputs, every saved parent/edit reconstruction, both
exact scorers, histograms and denominators; rejects corrupted energy, counts,
and missing groups; then repeats all 168,646 trials. Ordered trial digests,
histograms, full certificates and non-timing aggregates must match exactly.
The replay uses the same search implementation, not an independent enumerator.
Run without Python `-O`, since the repository checker uses assertions.

The repository checks also passed: `make check`, `scripts/check_results.py`,
`scripts/import_sources.py --check`, `scripts/independent_check.py`, and
`scripts/check_package.py`. The last two generic package/result checks cover the
existing pilot; the new `check.py` validates this package specifically.
[VERIFY.json](VERIFY.json) records executable commands and limits.

For a separate output directory and explicit deadline:

```sh
python3 research/alternating-transfer-20261022/sweep.py \
  --output scratch/alternating-transfer-replay --stop-at 2099-01-01T00:00:00Z
```

The output directory must not already exist and its parent must exist. A deadline
is checked between groups; an interrupted run reports `exhausted: false` and
cannot support the complete-domain conclusion. The packaged checker expects the
complete recorded run.

## Limits and open next question

No current-source literature refresh, independent scientific/novelty review,
global optimality proof, two-edit paths, rotation-then-edit search, heuristic
refinement, or editing of pending candidates as parents was performed. Only
group minima and the twelve below-published attempts were checked individually
with both scorers; other trials use XOR scoring, short exhaustive controls and
full deterministic replay. The original-orientation predecessor results retain
their own review status. There is no accepted-frontier update.

Next: preregister a bounded two-endpoint-edit family using the pinned published
and pending witnesses as parents. First enumerate and price that domain, then
check the smallest cases against direct scoring. Success requires strict E
improvement over both comparators, canonical deduplication against both packages,
two exact checks, and a fresh primary-source audit before any novelty claim.
An exhausted negative domain is also useful; do not repeat this one-edit family.

## Credit

Published parent constructions belong to Zhang, Shen, Kumar and Pistoia;
Pšeničnik, Bošković, Popič and Brest; Pšeničnik, Mlinarič, Brest and Bošković;
and the Bošković, Brglez and Brest archive. Each saved certificate retains its
parent's source URL and authors. Endpoint editing is an established method,
including prior work by Dimitrov; no method novelty is claimed.

The prior Codex donor session supplied `transfer.py`, the five pending
improvements, and this alternate-orientation question. This session reused its
scoring and edit enumeration and added the bounded orientation sweep, provenance
and accounting checks, and evidence package. Codex performed this work at
@thakrarsagar's direction, with delegated AI static safety and mathematical/code
reviews. These are author-side checks, not independent scientific review.
