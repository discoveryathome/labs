# Two endpoint edits: two provisional energy improvements

**The complete 4,808-path sweep found two distinct sequences below the pinned
published and pending thresholds.** Both have full exact certificates and were
reconstructed by a separately written enumerator. They remain **author-checked
record candidates**, pending independent source, arithmetic and novelty review.
The accepted frontier is unchanged.

- **N=114: E=761**, versus published E=777; exact F=`6498/761`.
  Start with Zhang, Shen, Kumar and Pistoia's N=112, E=728 witness, prepend
  `1`, then prepend `0` (final prefix `01`).
- **N=464: E=14396**, versus published E=14436; exact F=`26912/3599`.
  Start with Pšeničnik, Bošković, Popič and Brest's N=462, E=13811 witness,
  then prepend `0` twice. Two other ordered paths yield the same symmetry orbit.

Bits use `0 = -1` and `1 = +1`. Neither target has a better entry in the five-row
pending table. Four attempted paths produce these two orbits; these counts must
not be confused with four discoveries. [results/candidates.json](results/candidates.json)
contains the full sequences, all correlations, exact rational F, canonical keys,
parent identities and ordered edits. [AUDIT.md](AUDIT.md) records the bounded
current-source audit and its limitations; it is not a proof of global novelty.
The bounded refresh found no stronger verified same-length witness. N=464's
PSL is 24 versus the published comparator's 22: the improvement is in energy,
the stated objective, and is not a PSL improvement.

## What is new, and what belongs to predecessors

This takes the [two-edit handoff](https://github.com/discoveryathome/labs/discussions/2#discussioncomment-19131784)
from [PR #6](https://github.com/discoveryathome/labs/pull/6), pinned at
`752a17026f40d1adc860c76d2cb090973d07ed6b`. That unmerged package completed the
alternating-parent single-edit extension and found no new record candidate.
Its best E at these lengths was 785 and 14436, respectively. The present package
is based directly on main and has no runtime dependency on PR #6.

The useful intermediate sequences already existed in the original donor's
`transfer/best.json`: the N=114 construction passes through an **N=113, E=736
tie in a different orbit from the imported published witness**. The N=464
construction passes through the existing **N=463, E=14047 pending candidate**.
We extend those known intermediate orbits by one further endpoint insertion;
we do not claim their discovery. This illustrates why keeping useful ties and
pending witnesses as future parents can matter.

All eight old candidate orbits, not only the five best-length entries, were
checked for overlap. [PREDECESSORS.json](PREDECESSORS.json) pins the prior packages,
remote artifact hashes and relevant comparisons. Endpoint editing/chaining is
established work, including Dimitrov's; no method novelty is claimed.

## Preregistered scope and accounting

Base: `1e65ddd66191355ba5fd86b9788d6c02e9329a82`.
Seed: `93610b14cdb3c9d4f2373623b04b0933`, generated from OS randomness.
The repository picker drew `refinement` / `published-refinement`, suggested
N=119 and run seed 2957707571. The search itself is deterministic.

The [preregistration](PREREGISTRATION.md) follows the handoff's complete bounded
family instead of only N=119. Input order is 319 published rows followed by five
pending candidates. Apply exactly two ordered operations from: delete-first,
delete-last, prepend-0, prepend-1, append-0, append-1. Only the final length is
filtered, using the 95 rows with `bound is None`; the intermediate need not be
an eligible frontier length. All paths, duplicates and undo operations remain
in the denominator. Parent orientations do not need expansion for this
endpoint-only family: negation, reversal and alternation remap the operation
alphabet to itself, up to child symmetry. Short exhaustive controls test this.

- 324 parent rows considered, 148 contributing and 176 with zero eligible paths.
- 395 `(parent identity, final length)` groups, reaching all 95 eligible lengths.
- Length change -2: 126 groups / 504 paths; change 0: 140 / 2240;
  change +2: 129 / 2064. Total: **4808 paths**.
- 56 paths beat the older published values, but only four beat
  `min(published_E, pending_E)`, yielding the two candidate orbits above.
- **N=119:** 68 paths; best E=771, a tie with the existing pending candidate.
  The seeded length produced no new improvement.

All 4,808 path IDs, ordered edits, exact energies, sequence digests and thresholds
are in [results/trials.jsonl](results/trials.jsonl); none is dropped for poor
performance. [results/best.json](results/best.json) retains a full minimum witness
per length. One complete search run used 58.420 CPU seconds / 58.566 wall seconds,
including both scorers for every retained path. Input loading, domain planning,
controls and replay are additional costs. Published-parent discovery costs are
not included: this is a conditional construction experiment, not an algorithm race.

No interior edits, stochastic search, heuristic refinement, rotation-then-edit,
or adaptive search on newly found results was performed. Rotation is not used
for deduplication. No accepted data or existing verifier/solver is modified.

## Reproduce and challenge

From the repository root, Python 3.10+ without `-O`, no external Python packages:

```sh
python3 research/two-endpoint-20261022/sweep.py --self-check
python3 research/two-endpoint-20261022/check.py --self-check
```

The first command tests 4,320 short paths, list-based operation reconstruction,
direct/XOR scoring and coverage under all eight parent symmetries. The second
rebuilds **every retained path with deques**, without importing the search
enumerator, checks every correlation and energy with both existing scorers,
validates all 324 parent certificates and the five pending-parent ancestor chains,
and compares all trial records, coverage, minima, candidates and hashes.
It rejects changed energy, parent identity or operation order, missing/duplicate
trials, an incomplete run, and a missing candidate.

The two scoring implementations and the two enumerators are author-run checks,
not independent scientific reviewers. Direct scoring forms aperiodic correlations
with integer sums; the other checker uses XOR/popcount. Full replay is a
verification pass, not an extra search sample. [VERIFY.json](VERIFY.json) lists
commands and [verification.txt](verification.txt) records executed checks.

To repeat the original string-based sweep in a new directory whose parent exists:

```sh
python3 research/two-endpoint-20261022/sweep.py \
  --output scratch/two-endpoint-replay --stop-at 2099-01-01T00:00:00Z
```

The output must not exist. A deadline is checked between parent rows;
`exhausted: false` cannot support a complete-domain claim. The packaged checker
expects the full recorded domain. [SOURCES.json](SOURCES.json) and the run metadata
pin the code and inputs. The generic repository checks also passed, but their
pilot package/results checks do not substitute for this new checker.

## Open next questions and limits

First, have another researcher verify these two certificates, their original
source encodings, the intermediate-orbit provenance, and the current source audit
before proposing any accepted-frontier change. Current-source search cannot
exclude unpublished or poorly indexed results. Neither global optimality nor
independent scientific acceptance is established here.

A later distinct experiment could preregister endpoint extensions of retained
non-record ties and pending candidates, using these two energies as additional
provisional thresholds. Price and freeze that domain first; do not rescore this
completed family and count the same candidates again. No such extension was run
in this session. Full predecessor sweeps were not replayed.

## Credit

The N=114 parent belongs to Zhang, Shen, Kumar and Pistoia; the N=464 parent to
Pšeničnik, Bošković, Popič and Brest. Other tested parents retain the credit in
`data/published.json`, including Pšeničnik, Mlinarič, Brest and Bošković and the
Bošković, Brglez and Brest archive. Every saved minimum and candidate records
its parent's author/source. The original donor session supplied the transfer
machinery, intermediate tie and pending candidate; the alternate-orientation
session supplied the explicit handoff. Established endpoint methods, including
Dimitrov's work, retain their credit.

Codex performed this implementation, bounded experiment and author checks at
@thakrarsagar's direction, with delegated AI domain, code and primary-source
reviews. This is AI assistance, not independent human or scientific signoff.
