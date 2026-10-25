# Preregistration: exhaustive Hamming-radius-3 balls around endpoint starts

Written 2026-10-25 08:02 UTC, before the full run. Base `1e65ddd66191355ba5fd86b9788d6c02e9329a82`.
Card `published-refinement` (track `refinement`), drawn by the repository picker from seed
`a72912875cd29ad1572281452b7d0ff1`; suggested length N=451, run seed 729616369 (unused:
the family is fully enumerated, with no random choices). Budget 60 minutes from 07:54:39 UTC.
Search stops by 08:39:40 UTC.

## Question

Can up to three interior or endpoint bit flips, applied to a published or pending witness or
to one endpoint edit of it, beat **both** the accepted published energy and the best pending
candidate at an audited open length? PR #6 and PR #7 exhausted endpoint-only families and
explicitly excluded interior edits; this family adds them.

## Domain (fixed before running)

- Parents: the 319 pinned rows of `data/published.json`, the 5 donor candidates
  (`research/donor-60m-20261020/candidate-table.json`) and the 2 PR #7 candidates
  (`research/two-endpoint-20261022/results/candidates.json` at `7e015e8`): 326 parents.
- Starts: each parent unchanged, or after one of delete_first, delete_last, prepend_0,
  prepend_1, append_0, append_1. A start is kept when its length is one of the 95 audited open
  lengths: **964 starts, all 95 lengths covered**.
- Ball: every sequence within Hamming distance <= 3 of each start, including the start:
  **15,366,696,575 scored sequences**. Duplicate sequences reached from different starts are
  counted again in the denominator.
- Threshold per length: min(accepted published E, donor pending E, PR #7 pending E).
- Hamming balls are invariant under all eight energy-preserving symmetries, so one orientation
  per start suffices. Rotation is not used.

The radius was raised from 2 (with radius 3 only at N=451) to 3 everywhere after timing three
probe starts (N=110 and N=460 at radius 2, N=451 at radius 3: 0.67 s). The probes are counted
in the denominator. No results from the full domain had been seen when the radius was set.

## Pricing and expectation

Start gaps above threshold: minimum 0 (226 starts already tie, mostly published witnesses
unchanged), median 184. The donor session already ran population tabu from the published
records and from 16 transformed starts. Those runs very likely covered most radius-1 and
radius-2 moves from the closest starts. **The expected outcome is a bounded negative result:
no sequence in the domain beats both thresholds.** A positive result needs a full witness with
integer E strictly below the threshold, scored by both repository checkers and deduplicated
under the eight symmetries against all known witnesses. Ties do not count.

## Method and checks

`ball.cpp` scores each sequence by exact integer incremental updates of the aperiodic
autocorrelations (pair corrections at shift |i-j|). Controls:
1. A built-in self-test checks every flip set of size <= 3 on 114 random sequences
   (N=3..40) against direct scoring.
2. Every start's E is recomputed and compared with the Python-computed input.
3. Every per-start, per-shell minimum and about 12 strided samples per start are rescored
   from scratch with `src/verify.py` and `scripts/independent_check.py`.
4. Any sequence below threshold gets both checkers and a canonical-orbit comparison.
