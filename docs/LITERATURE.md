# Frontier audit — 2026-10-20

The audit searched both requested repositories, arXiv versions, recent
2025–2026 publications, and references in the recent record papers. Source
snapshots and SHA-256 hashes are in `data/sources/manifest.json`. The Packebusch &
Mertens paper is not redistributed (arXiv non-exclusive license): its manifest entry
keeps the URL, access date and hash with `"stored": false`, and its tables are kept as
extracted factual data in `data/sources/optimal-table.json` (extracted 2026-10-22). Repository
heads: `borkob/git_labs@1aa123407636e48630174e0bf122037e369c1d68` and
`J-Brest/LABS@4232311cb4f3626ab008336f6069cd5af5e3915b`.
No search can certify that every unpublished or unindexed construction is absent.
“Best verified published” means the strongest witness found in this audit for
that row, not an optimality theorem.

| Source | What it establishes | Treatment |
|---|---|---|
| [Packebusch & Mertens, 2016](https://arxiv.org/html/1512.02475) | Unrestricted optimal sequences through 66; skew-symmetric optima through odd 119 | Import unrestricted witnesses, mark proof status as literature-reported; do not extend unrestricted proof status to 119 |
| [Bošković–Brglez–Brest archive](https://github.com/borkob/git_labs) | Historical energy witnesses and solvers, including 2018 skew results | Recompute the 2018 witness file; treat it as historical, not automatically current |
| [Zhang et al., 2504.00987v2](https://arxiv.org/html/2504.00987v2) | Sixteen improved lengths 92–120; non-skew improvements at 99,107,109,113,119 | Use revised v2, not the twelve-length v1 abstract; verify all 17 witnesses, including two inequivalent N=92 sequences |
| [Pšeničnik et al., dual-step](https://arxiv.org/html/2409.07222v1), [2025 journal version](https://doi.org/10.1016/j.dsp.2025.105316) | Improved constructions across 450–527, with a tie at 518 | Verify all 78 preprint witnesses; compare with 2026 values rather than treating 2025 as final |
| [Pšeničnik et al., 2026](https://arxiv.org/html/2607.09688v1) | Partition-guided, GPU-parallel self-avoiding walks followed by unrestricted refinement | Verify the 35 witnesses actually listed in Table 3 and take per-length minima with the earlier paper |
| [J-Brest/LABS](https://github.com/J-Brest/LABS) and [2026 PSL paper](https://www.preprints.org/manuscript/202605.0907) | Peak sidelobe records, including long Legendre-based sequences | Separate objective; verify N=2047 PSL=32, E=433843, F=4190209/867686 as a control, not an energy record |
| [Dimitrov, journal 2025](https://www.sciencedirect.com/science/article/abs/pii/S1051200424004184), [author preprint](https://arxiv.org/abs/2106.03377) | Efficient skew flip calculations and long sequences with F>5 | Algorithm direction; not a stronger finite-length witness for the selected targets |
| [Cadavid et al., November 2025](https://arxiv.org/abs/2511.04553) | Quantum-enhanced memetic search scaling experiments at N=27–37 | Algorithm evidence on small instances; does not replace the target-length record table |

The exact boundary N=66 is also stated in the revised 2025 memetic paper. No
later unrestricted exact result was identified in this audit. The pilot checks
small optima exhaustively through N=16; it does not rerun the historical
branch-and-bound proofs.

## Scope and encoding findings

The 2026 abstract describes an interval through 527 and a result at 573. Its
Table 3 contains **35 total rows**, 34 in 450–518 and one at 573; the pilot uses
the actual table rather than inventing missing improved rows. The 2025 table
supplies the other cases through 527. ArXiv's 2026 HTML displays a June date
despite a July identifier; the versioned URL and content hash, not that rendered
date, identify the evidence. `updated` dates identify source releases approximately;
`audited_on` is the unambiguous local audit date.

The 2025 memetic table pads bits at the **right** to a multiple of four;
the dual-step and 2026 tables use **left** hexadecimal padding. Leading sequence
zeros must be preserved to obtain N bits (notably N=484). One dual-step HTML
witness contains the rendering token `allowbreak`; the importer removes that
literal token and whitespace, then requires exact length and verified score.
All 319 imported witnesses pass their reported energy or displayed merit-factor
precision checks. The importer is deterministic and can be rechecked offline.

The table combines 65 unrestricted exact control lengths, 16 medium-length
records, 78 long-length records, and N=573: **160 rows**. Historical 2018 rows
outside these cases are replicated but not asserted current. There is no claimed
global all-N database.

## Claims checked

| Claim from the research brief | Status |
|---|---|
| Minimizing E is equivalent to maximizing F at fixed N and E>0 | Confirmed algebraically; N=1 handled separately |
| A full sequence admits cheap exact verification | Confirmed by direct integer and independent XOR implementations |
| Every improvement can be a publishable mathematical record | Potentially; actual novelty and publication require refreshed comparisons and review |
| Earlier repository records remain strongest | Not assumed; contradicted for the updated medium and long regions |
| Proven skew optima settle unrestricted odd lengths | False; recent non-skew constructions explicitly beat several such values |

Searches also surfaced a [2021 inverse-filtering paper](https://www.sciencedirect.com/org/science/article/pii/S1546221821001326)
claiming unusually high F at N=231 and 237. Those witnesses were not independently
reproduced here, so those lengths are excluded from the audited frontier and are
an unresolved source-verification lead. Periodic-correlation and PSL-only results
are likewise not promoted into the energy frontier.

## Target rationale

N=92,99,107,119 give lower-cost unrestricted-search experiments in a region where
recent work found improvements over mature benchmarks. N=450,451 tests neighboring
length transfers; N=518 was tied in the 2025 work and improved in 2026; N=573
tests a longer structured construction. Recent progress supports research interest,
but does not imply high improvement probability in short CPU sessions.

A future algorithm claim should compare against published implementations after
code review and authorization, with equal compute and held-out seeds. This pilot
compares **construction scores** against the strongest imported published witnesses;
it does not claim to replicate GPU runtimes or outperform those algorithms.
