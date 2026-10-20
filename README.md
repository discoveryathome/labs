# LABS: a local Discovery@Home pilot

Find sequences `s[i] ∈ {-1,+1}` minimizing the **aperiodic** energy
`E = Σ(k=1..N-1) (Σ(i=0..N-k-1) s[i]s[i+k])²`.
Merit factor `F=N²/(2E)` is a secondary presentation metric. Smaller integer E wins.

This is a local research proposal. No remote repository, pushes, hub application,
or donor launch is configured. **No maintainer has agreed to review submissions.**
See the [donor-session follow-up](research/donor-60m-20261020/README.md) for the
latest evidence: five exact-checked candidate improvements from endpoint edits,
pending independent novelty review. The [initial sweep assessment](docs/ASSESSMENT.md)
records the earlier unsuccessful baseline experiment.

The authoritative [frontier](discover/frontier.json) indexes
[160 lengths](data/frontier.json): N=2–66, sixteen recent medium-length cases,
N=450–527, and N=573. It selects the lowest verified energy among the imported
primary-source constructions, including the revised
[2025 memetic-tabu paper](https://arxiv.org/html/2504.00987v2),
[dual-step paper](https://arxiv.org/html/2409.07222v1) (journal publication in 2025),
and [2026 partition-search paper](https://arxiv.org/html/2607.09688v1).
These are literature records, not discoveries by this pilot. See
[the literature audit](docs/LITERATURE.md) for coverage and limitations.

## Reproduce offline

Python 3.10+ and a C++17 compiler with `make` are sufficient; there are no Python
dependencies, package installs, network requests, or GPU requirements for checking.
Run commands from this directory:

```sh
make check
python3 scripts/import_sources.py --check
python3 scripts/independent_check.py
python3 scripts/check_results.py
python3 scripts/check_frontier.py --n 451
python3 src/verify.py --file data/witnesses/451.json
```

The checks reproduce published scores, compare each row to every imported
alternative, enumerate every sequence for N=1–16, reject malformed and false
certificates, check symmetries, and compare incremental search arithmetic against
full recomputation. Typical certificate checks take seconds; allow two minutes on
a busy machine. They do not rerun historical optimality proofs.

```sh
# Deterministic replay of all experiment trajectories; timings will differ.
python3 scripts/check_results.py --replay
# A new run: refuses to overwrite existing experiment results.
python3 scripts/experiment.py --output scratch/my-run
# A bounded individual search with an explicit seed.
./build/search 99 123 2000000 tabu
# Draw a task and inspect local claims/handoffs.
python3 scripts/pick.py --seed 0123456789abcdef0123456789abcdef
```

See [independent verification instructions](docs/VERIFY.md),
[AGENTS.md](AGENTS.md), and [DISCOVERY.md](DISCOVERY.md) before contributing.
Original pilot code and documentation use MIT; third-party snapshots retain
their source licenses and attribution in [NOTICE](NOTICE).
