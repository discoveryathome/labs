# Independent verification

Use a fresh local clone or copy. No network, Python packages, GPU or upstream
executables are needed. Python 3.10+ is required for `int.bit_count`; C++17 and
make are needed only for solver tests and experiment replay.

```sh
make check
python3 scripts/import_sources.py --check
python3 scripts/independent_check.py
python3 scripts/check_results.py
python3 scripts/check_package.py
```

`src/verify.py` directly forms every C(k) with Python arbitrary-precision integers.
It accepts a JSON certificate containing `sequence` as an integer ±1 list, a
01 string (0 means −1), or a +- string. All declared exact fields are checked.
For example:

```sh
python3 src/verify.py --sequence +++++--++-+-+
python3 src/verify.py --file data/witnesses/99.json
python3 scripts/check_frontier.py --n 99
python3 scripts/independent_check.py --file data/witnesses/99.json
python3 scripts/compare_candidate.py data/witnesses/99.json
```

The first command must give N=13, E=6, F=169/12. A certificate with that sequence
and `"E":5` must exit nonzero. Empty inputs, nonbinary strings, bools and floats in
±1 arrays are rejected. N=1 gives E=0, F_exact="infinity", F_decimal=null.
F_decimal is presentation-only and never an acceptance threshold.

The standalone `independent_check.py` has no imports from the reference verifier
or search solver. It counts unequal bit pairs using XOR and popcount, obtains
`C(k)=(N-k)-2*mismatches`, and compares the integer energy and rational merit factor.
The exhaustive test enumerates all 131070 sequences for N=1–16 with this formulation,
compares every correlation with the reference for N≤9, and matches the published
optima. Randomized full-correlation comparisons extend through N=573.

`check_frontier.py` verifies raw input hashes, reconstructs each row's witness,
and checks that its energy is the minimum of all imported alternatives for N.
`import_sources.py --check` independently re-extracts the HTML/text tables (and
reads the extracted Packebusch–Mertens table, whose paper is cited by hash but not
stored) and compares the complete derived files byte for byte. Neither proves that a
construction is globally optimal nor that the bibliography is complete.

To test the protocol's per-row probe, use a recorded random seed to select three
rows and run the table's `check_row` command. The initialization did this and
stored the choices and results in `research/pilot/validation.txt`.

## Search reproducibility

```sh
python3 scripts/check_results.py --replay
python3 scripts/experiment.py --output scratch/new-run
```

Replay checks all 160 deterministic trajectories, excluding times. The sweep uses
2,000,000 neighbor evaluations per run, rounded down to a complete neighborhood.
Random starts and both methods share the same initial sequence for each (N,seed).
All four arms are interleaved in a fixed shuffled order. Published starts retain
the input construction in the best-so-far output; a tie from such a run is **not**
an independent rediscovery. Restarts and initial full scoring are not counted as
neighbor evaluations but their compute is included in CPU/wall timings.

The solver uses SplitMix64 with rejection sampling, fixed integer updates and
explicit budgets. Compiler-dependent timers vary; seeds, sequence, E and counters
must replay exactly. Source/config/frontier hashes and compiler/platform metadata
are recorded. Published paper computational costs are not included in pilot
runtime, so comparisons involving published starts are conditional refinement
experiments, not end-to-end algorithm comparisons.

Full replay may take several minutes under load. `check_results.py` without
`--replay` cheaply checks certificates, accounting, classifications, summary and
job coverage; timing values are recorded measurements, not mathematical certificates.

## Reviewing a new candidate

1. Save the full sequence, E, N, seed, code hash, command and compute budget.
2. Run both exact checkers; recompute the symmetry canonical representative.
3. Re-audit current primary sources for this N. Compare integer E, not rounded F.
4. Reject E ties as energy records, especially symmetry copies. A new inequivalent
   tie may be cataloguing work only.
5. Have another researcher replay the checks and record their identity, commit,
   command, output and limitations in `research/<name>/verifications/`.
6. The maintainer (@Mister-Meeseeks) reviews novelty, credit and scope before
   updating the frontier, after the independent replay in step 5.

Do not label the two checkers as two independent reviewers. All initialization
results are author-checked; an external person has not reviewed them.
