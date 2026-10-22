# Research contract

The question is constructive: for each specified N, exhibit a ±1 sequence with
lower aperiodic energy than the best verified published construction for that N.
The certificate is the full sequence. All authoritative arithmetic is integer;
F is stored as a reduced rational and displayed as a decimal only for convenience.
N=1 has zero energy and infinite F and is a control, not a record-search target.

Progress has three distinct meanings:

1. **Record candidate:** strictly lower E than the current published frontier,
   with full witness, renewed source audit, symmetry check, and independent review.
2. **Algorithm evidence:** better distributions of E or time-to-target on held-out
   seeds, fixed budgets and inputs, against strong comparators. A few wins against
   our elementary baseline do not establish a state-of-the-art algorithm.
3. **Infrastructure or internal baseline:** a verified replication, corrected
   record table, better local starting point, or trustworthy measurement.

The first is the primary scientific objective. Publication is not guaranteed by
beating a row: novelty, provenance, credit and venue review still matter.

## Frontier and bottleneck

`discover/frontier.json` is authoritative. Its table has executable per-row
checks and credits the published authors. The [literature audit](docs/LITERATURE.md)
describes the exact and heuristic boundaries. We have verified the constructions,
not independently proved their optimality or exhaustively established that no
newer publication exists.

Primary targets are N=92,99,107,119,450,451,518,573. They are credible research
directions because recent publications actually improved these regions and
demonstrated weaknesses of skew-only search. They are **not demonstrated easy
opportunities for laptop sessions**. The medium lengths allow unrestricted-search
experiments cheaply; the longer lengths test the transfer of published structure
and perturbation/refinement. N≤66 is for controls; an alleged improvement there is
first a checker/encoding investigation.

The [follow-up donor session](research/donor-60m-20261020/README.md) found a
narrower accessible direction: endpoint edits of recent published witnesses
produced exact-checked improvements at N=108,118,119,463,485. These are pending
record candidates, not independently accepted records. This supports structured
transfer tasks, while repeatable success beyond those already found remains
untested. Always compare new submissions against the pending candidate table too.

The bottleneck is generating candidates competitive with heavily optimized,
often GPU-based prior work. Verification is cheap. Default baseline restarts
are unlikely to match that prior compute investment.

## Implemented methods and symmetries

`src/search.cpp` implements random-restart steepest single-bit descent and tabu
search with aspiration, random tenure, random tie breaking and stagnation restarts.
Published-start searches kick the incumbent at restarts. These are independently
implemented baselines, not reproductions of published GPU algorithms.
The full neighborhood costs O(N²), with O(N) evaluation per proposed bit flip.
The delta formula is
`dC(k)=-2*s[j]*( [j>=k]*s[j-k] + [j+k<N]*s[j+k] )`;
`dE=Σ(2*C(k)*dC(k)+dC(k)²)`.

Complementation, reversal and alternating sign multiplication generate an orbit
of at most eight sequences. Canonicalization takes the lexicographically least
01 encoding of the entire orbit. Small symmetric orbits can have fewer than eight
members. Sequences are deduplicated when collecting results; search trajectories
are not claimed to avoid every repeated state. Cyclic rotation can change
aperiodic E and is a search operator, not an equivalence. Skew symmetry is a
restriction, not a valid reduction of the unrestricted optimization problem.

## Priorities and coordination

`discover/catalog.json` contains four tracks summing to 100: source audit 15,
verification 25, algorithm measurement 10, and structured refinement 50.
`discover/priority-log.md` explains and dates the weights. The seeded local picker
prints active claims and unresolved handoffs; it does not lock work. Separate
checkouts do not share live state, so this incubation pilot is not ready for a swarm.

Do not repeat completed verification merely to generate a contribution.
Existing checks on each card explain what remains. A source audit must compare
current versions and the actual objective. Peak sidelobe level, periodic energy,
skew-only optima and finite-length merit factor are different claims.
No branch-and-bound run or scaling fit from small N proves a new long-length optimum.

## Verification, review and credit

See `docs/VERIFY.md`. Packages need `TASK.json`, `VERIFY.json`, source and input
hashes, commands, all run logs, candidates, limitations and a bounded next step.
Record candidates require both checkers, source refresh, and an independent
reviewer before a maintainer can update the frontier. An independent implementation
run by the author remains **author-checked**.

No person has agreed to maintain this project and review capacity is unknown.
The manifest's `UNASSIGNED` slot is an explicit vacancy, not an appointed person.
Review and donor intake are paused. The owner has authorized publication and a
hub catalogue nomination; this does not appoint a scientific maintainer or certify
readiness. The empty manifest `hubs` array permits nomination without claiming
maintainer consent to a donor launcher. See `docs/PUBLICATION.md`.
Before launch, name a consenting maintainer and their reviews/week,
confirm licensing/credit, and establish shared coordination. Review capacity will
limit intake even if exact checking is automated.

Original code and documentation use MIT as a local default. Published witnesses
retain attribution to their discoverers; contributors are credited in result
packages and `CONTRIBUTORS.md`, including AI assistance. No authorship or
publication promise is made. Changes to the verifier or frontier deserve the most
care because every subsequent donor depends on them.
