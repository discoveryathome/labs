# Candidate novelty audit, 20 October 2026

The five best candidates beat every same-length witness in the pilot's imported
corpus. Both exact checkers pass. A renewed primary-source and benchmark search
found no superseding construction at these lengths. **They remain candidates:
no independent researcher has reviewed the arithmetic, provenance or novelty.**
Search absence does not establish that an unpublished or poorly indexed result
does not exist. The accepted frontier has not been changed.

| N | Audited published E | Candidate E | Published parent | Endpoint edit |
|---:|---:|---:|---|---|
| 108 | 670 | 666 | Zhang et al., N=109, E=658 | Remove first bit |
| 118 | 807 | 799 | Zhang et al., N=119, E=787 | Remove first bit |
| 119 | 787 | 771 | Zhang et al., N=120, E=824 | Remove last bit |
| 463 | 14439 | 14047 | Pšeničnik et al., N=462, E=13811 | Prepend −1 |
| 485 | 16106 | 15970 | Pšeničnik et al., N=484, E=15646 | Append −1 |

The small cases compare to [Zhang et al. v2](https://arxiv.org/html/2504.00987v2).
N=463 compares to [Pšeničnik et al. 2026](https://arxiv.org/html/2607.09688v1).
N=485 compares to the [dual-step table](https://arxiv.org/html/2409.07222v1);
the 2026 table does not include an N=485 row. Parent witnesses for both long
candidates come from the 2026 paper. The scientific credit for the difficult
parent constructions belongs to those authors.

## Sources rechecked

* The live arXiv abstract pages still identify 2504.00987v2 and 2607.09688v1.
  Downloaded HTML for these versions and the dual-step table is byte-identical
  to the imported snapshots. `audit/source-refresh.json` records hashes and
  retrieval times.
* GitHub API checks returned the same heads for
  [borkob/git_labs](https://github.com/borkob/git_labs)
  (`1aa123407636e48630174e0bf122037e369c1d68`) and
  [J-Brest/LABS](https://github.com/J-Brest/LABS)
  (`4232311cb4f3626ab008336f6069cd5af5e3915b`).
  The latter's PSL objective remains distinct.
* The October 2026 [Endless Exam benchmark](https://github.com/ricolalemon/endless-exam)
  at `9fc1ece969c0d9dec056f78ac4e83dbcf2c90a9e` was checked as an additional
  contemporary benchmark. Its published LABS outcomes and five reference
  witnesses concern N=240,280,281,357,375, which do not overlap these candidates.
  The five reference witnesses were independently rescored locally. The raw
  index, reference files, README and MIT license are retained under `audit/`.
* [Dimitrov's 2022 paper](https://arxiv.org/pdf/2206.12070) already uses endpoint
  insertion/deletion operators and chains them. This session does **not** claim
  a new transformation method. Its listed N=463 and N=485 merit factors are
  weaker than the 2025–2026 comparators. No N=108 or N=118 record row was found
  in that PDF's text.
* The January 2026 [NISQ paper](https://arxiv.org/html/2506.17391v2) studies exact
  small cases through N=45 and a hardware demonstration at N=120; no replacement
  witness for our five lengths was identified.
  The [direct-PUBO preprint](https://arxiv.org/html/2510.24237v1), associated with
  a 2026 journal publication, benchmarks N=5..99.
  The [ROADEF 2026 abstract](https://roadef2026.sciencesconf.org/685082) discusses
  finite interaction range and exact formulations, without a competing witness
  for these lengths.

Searches included recent LABS/merit-factor records and exact length/energy pairs
108/666, 118/799, 119/771, 463/14047 and 485/15970. They yielded no stronger
verified same-length witness. This is a bounded audit, not an exhaustive
bibliographic guarantee. No authors were contacted, and nothing was posted.

## Independent review target

Run `check_candidate.py --n N` for each of the five lengths. It reconstructs the
edit from the credited parent, verifies both parent and candidate with direct
integer and XOR arithmetic, recomputes the published comparator, and checks every
imported same-length alternative. Challenge the source encodings and check for
records outside this corpus before proposing an accepted-frontier update.

The endpoint energy identities give an additional short check. For a parent
`s[0..L-1]` with autocorrelations `C(k)`, deleting its last element gives
`E' = E + L - 3 - 2*s[L-1]*Σ(k=1..L-2) C(k)*s[L-1-k]`.
Appending `x ∈ {−1,+1}` gives
`E' = E + L + 2*x*Σ(k=1..L-1) C(k)*s[L-k]`.
Reversal gives the corresponding first-element formulas.
