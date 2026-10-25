# Hamming-radius-3 balls around endpoint starts: a bounded negative result

**No sequence within three bit flips of any published or pending witness, or of any single
endpoint edit of one, beats both the accepted published energy and the best pending
candidate at any of the 95 audited open lengths.** All 15,366,696,575 sequences in the
preregistered domain were scored with exact integer arithmetic. No record candidate, no
frontier change.

Card `published-refinement` (track `refinement`), drawn by `scripts/pick.py` from seed
`a72912875cd29ad1572281452b7d0ff1` (suggested N=451, run seed 729616369, unused because the
family is fully enumerated). Base `1e65ddd66191355ba5fd86b9788d6c02e9329a82`. Budget 60 minutes,
started 07:54:39 UTC on 2026-10-25. The preregistration in [PREREGISTRATION.md](PREREGISTRATION.md)
was written before the full run.

## Why this family

[PR #6](https://github.com/discoveryathome/labs/pull/6) exhausted alternating-parent single
endpoint edits, and [PR #7](https://github.com/discoveryathome/labs/pull/7) exhausted exactly two
endpoint edits. PR #7 explicitly excluded interior edits. This session adds them: up to
three flips anywhere in the sequence, around every parent and every one-edit child.

## Domain

| Item | Count |
|---|---:|
| Parents: 319 published + 5 donor pending + 2 PR #7 pending | 326 |
| Starts (identity or one of 6 endpoint edits, kept at open lengths) | 964 |
| Open lengths covered | 95 of 95 |
| Sequences scored (radius <= 3, duplicates across starts counted) | 15,366,696,575 |
| Probe starts, run twice (timing, then verifier test), also in the denominator | 3 starts x 2 runs, 30,802,978 sequences |

Threshold per length = min(accepted published E, donor pending E, PR #7 pending E); see
[run/thresholds.json](run/thresholds.json). Hamming balls are invariant under all eight
energy-preserving symmetries, so one orientation per start covers its orbit. Rotation is not
used.

## Results

- **Below threshold: 0** at all 95 lengths ([results/below-threshold.json](results/below-threshold.json) is empty).
- **Best energy in the domain equals the threshold at every length.** It is reached only by
  the threshold witness itself, by other members of its symmetry orbit, or by equal-energy
  ties. Ties are not records.
- **Local optimality of the threshold witnesses.** 96 starts are a threshold witness
  unchanged (95 lengths). 91 of them are *strict* local minima within Hamming radius 3:
  every sequence 1, 2 or 3 flips away has higher energy. Among those 91, the smallest increase
  has median 152 and minimum 4. The other five have equal-energy neighbours and no lower ones:
  N=467 (2 flips), 497 (2 flips), 506 (1 flip), 517 (2 flips), 527 (1 flip).
- **Tie orbits.** The domain has 364 equal-to-threshold evaluations. Besides the threshold
  witnesses' own orbits, they fall in 3 symmetry-distinct orbits that are not in the pinned
  published or candidate sets. N=113 and N=527 match orbits already in
  the donor transfer results and PR #6/#7. **N=506 E=17301** is a symmetry-distinct tie with
  the published witness that appears in no earlier package. It was reached by 7 paths, for
  example flipping bit 360 of the published N=506 witness. It is a tie, not progress.
- **Suggested length N=451** (threshold 12625, published): 14 starts, 214,050,928 sequences,
  best E = 12625. That is the published orbit, reached as `prepend_1` of published N=450
  and as `delete_last` of published N=452. The published witness at N=451 is a strict
  radius-3 local minimum.

Per-length rows (threshold, best in domain, starts, sequences, ties): [results/per-length.json](results/per-length.json).
Per-start raw output (shell minima, ties, samples): [run/results.jsonl](run/results.jsonl).

## Evidence and controls (author-checked)

1. `ball.cpp --self-test`: every flip set of size <= 3 on 114 random sequences (N=3..40),
   338,352 in all, matches direct scoring.
2. Every start's energy is recomputed in C++ and compared with the Python value. The sequence
   count of every start equals sum C(N,i) for i <= 3. No accounting problems.
3. All 2,892 per-start shell minima and the first three strided samples per start (2,892),
   5,784 sequences in all, were rescored from scratch with **both** `src/verify.py` and
   `scripts/independent_check.py`. The
   other 8,676 strided samples were rescored with `scripts/independent_check.py`. All passed.
4. Two corruption controls (energy +4; one interior bit flipped) were rejected.
5. `make check` passed: 4 unit tests, `search --self-test`, 160 frontier rows and 221
   comparison witnesses. `python3 scripts/check_results.py` passed: 160 result certificates,
   0 distinct frontier improvements.

The full run took 5 min 05 s wall time (08:01:57 to 08:07:02 UTC) on 2 threads, built with
g++ 16.2.1 `-O3 -march=native` on Fedora under the desktop's shared 2-core cap. Timing is
indicative only.

## Replay

From an empty session folder `$S`:

```sh
git clone https://github.com/discoveryathome/labs "$S/repo"
git -C "$S/repo" checkout <this commit>
mkdir -p "$S/inputs" "$S/run"
git -C "$S/repo" fetch origin pull/7/head:pr7
git -C "$S/repo" show 7e015e8accc0cdbce48695dfb4c25a4d2f98d8e5:research/two-endpoint-20261022/results/candidates.json > "$S/inputs/pr7-candidates.json"
P="$S/repo/research/hamming-ball-20261025"
python3 "$P/build_starts.py" "$S"           # writes $S/run/starts.{tsv,json}, thresholds, known orbits
c++ -O3 -march=native -std=c++17 -pthread "$P/ball.cpp" -o "$S/run/ball"
"$S/run/ball" --self-test
"$S/run/ball" "$S/run/starts.tsv" 2 > "$S/run/results.jsonl"
python3 "$P/verify_results.py" "$S" "$S/out" # rescoring + summary
```

`run/starts.json` should hash to `83f2fd86…6ada0` and `run/results.jsonl` to `c4bba053…a4d954`
(full SHA-256 values in [HASHES.txt](HASHES.txt)). The results file is deterministic: no random
choices, and output is in start-id order.

## Not checked

- Independent review of this package and its code. Every check above is author-checked.
- No literature refresh. This is a negative result and claims no new record.
- Coverage of parents outside the pinned published rows and the 7 pending candidates. That
  includes the N=506 tie orbit found here, whose radius-3 ball was not separately searched.
- Radius >= 4, two-endpoint-edit starts combined with interior flips, and the equal-energy
  plateaus at N=467, 497, 506, 517 and 527 beyond one step.
- Global optimality. A failed finite search says nothing about sequences outside the domain.

## Open next questions

1. Do the equal-energy plateaus at N=467, 497, 506, 517 and 527 connect, through tie moves,
   to a point whose radius-3 ball beats the threshold? (Handoff below.)
2. Do PR #7's 4,808 two-endpoint paths, combined with radius-2 or radius-3 interior flips,
   reach below threshold? At the observed speed (about 5e7 sequences/s on 2 cores) radius 2
   is cheap and radius 3 costs on the order of 20–30 minutes.

## Credit

Published witness authors keep discovery credit for every parent (see `data/published.json`).
The donor session (`research/donor-60m-20261020/`) supplied the transfer code, the pending
candidates and the endpoint-transfer framing. PR #6 and PR #7 (thakrarsagar) supplied the
exhausted endpoint families this one extends, and the N=114 and N=464 pending parents.
Session donated by Cody Harris. Claude (Anthropic, Claude Code) designed, implemented and
checked this bounded experiment. No method novelty is claimed: exhaustive Hamming-ball
local search is standard.
