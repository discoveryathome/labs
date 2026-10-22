# Bounded primary-source audit — 22 October 2026

**Both candidates reproduce exactly and improve the audited same-length published witnesses. No superseding verified witness was identified in this bounded search. This is not a novelty determination, global-optimality proof, or scientific acceptance.** The accepted frontier and pinned source data were not changed.

Audit scope: base `1e65ddd66191355ba5fd86b9788d6c02e9329a82`; source checks on 2026-10-22, 20:26–20:32 UTC, within the parent session's 60-minute donation. Reviewed `docs/LITERATURE.md`, the previous donor's `AUDIT.md`, `audit-queries.json`, and candidate package. Exact retrieval timestamps, hashes, source encodings, queries, and failures are in [source-audit.json](source-audit.json).

| N | Published E | Candidate E | Exact candidate F | Credited published parent | Ordered bit operations |
|---:|---:|---:|---|---|---|
| 114 | 777 | 761 | 6498/761 | Zhang, Shen, Kumar and Pistoia: N=112, E=728 | prepend 1; prepend 0 |
| 464 | 14436 | 14396 | 26912/3599 | Pšeničnik, Bošković, Popić and Brest: N=462, E=13811 | prepend 0 twice |

## Objective and source decoding

The objective is the **aperiodic** energy
`C(k)=sum(i=0..N-k-1) s[i]*s[i+k]`,
`E=sum(k=1..N-1) C(k)^2`, with `s[i] in {-1,+1}`;
`F=N^2/(2E)`. There is no cyclic wraparound, zero-lag term, or double counting of negative lags. Bit 0 represents −1 and bit 1 represents +1. These definitions agree with the two papers. PSL is a different objective: the N=464 candidate has PSL=24, whereas its published N=464 comparator has PSL=22.

[Zhang et al., v2, Table 2](https://arxiv.org/html/2504.00987v2) explicitly pads hexadecimal encodings **on the right**. Its N=112 parent is `A0496A493FAECCC8AFC3D50E738F`, already 112 bits. Its N=114 comparator is `B6C3648DB19C8C387A9EAA8578000`: decode 116 bits and remove exactly two trailing padding zeros. The decoded sequences match published rows 196 and 197 (zero-based), with E=728 and E=777.

[Pšeničnik et al., v1, Table 3 and its preceding encoding paragraph](https://arxiv.org/html/2607.09688v1) specify **left** padding. The N=462 parent requires removal of two leading zeros from its 464-bit hexadecimal representation; the N=464 comparator requires no trimming. They match published rows 294 and 296, with E=13811 and E=14436. Keeping the parent's two formerly padding zeros as actual −1 spins gives exactly the N=464 candidate. Length is therefore essential when interpreting this shared hexadecimal string.

Fresh, locally authored direct integer sums and an XOR/popcount calculation independently reproduced all six energies: both parents, both published comparators, and both candidates. Replaying the ordered operations reproduced the package's complete bitstrings and SHA-256 values. This arithmetic cross-check is not independent researcher review and does not re-audit every search trial.

## Provenance and prior work

The N=464 path passes through N=463, E=14047, **bit-for-bit identical** to [the previous donor candidate](../donor-60m-20261020/candidates/463.json). Credit that package for the earlier endpoint improvement, and the published authors for the difficult parent construction. The N=114 path passes through N=113, E=736 before its second prepend. The prior donor package has no N=114 or N=464 candidate.

Endpoint insertion/deletion and their composition are established methods: [Dimitrov, 2206.12070v1, Table III, PDF p. 9](https://arxiv.org/pdf/2206.12070) lists both prepend signs, both append signs and deletions; Table XI explicitly chains three appends to reach N=464. Its N=464 merit factor is 7.13467656416, below both modern comparators. No method novelty is claimed.

The new package's `results/summary.json` reports **4,808 generated paths, four paths below the published-plus-pending threshold, and two candidate orbits**. Four is the qualifying-path count, not the total trial denominator.

## Current primary sources and benchmarks

- Live abstract histories still identify [2504.00987v2](https://arxiv.org/abs/2504.00987) and [2607.09688v1](https://arxiv.org/abs/2607.09688). Their freshly fetched HTML is byte-identical to the pinned files.
- [Dual-step, 2409.07222v1](https://arxiv.org/html/2409.07222v1) remains v1. Its N=464 row has rounded F=7.2617 and the imported exact E=14824, weaker than E=14436. The fetched full-page hash differs from the pinned snapshot, but the complete `<article>...</article>` is byte-identical; site-wrapper changes do not change the benchmark.
- The authors' [laboratory page](https://labraj.feri.um.si/dejavnosti/raziskovalna-dejavnost/binarna-zaporedja-z-nizkimi-avtokorelacijami/) still directs merit-factor data to [borkob/git_labs](https://github.com/borkob/git_labs) and PSL data to [J-Brest/LABS](https://github.com/J-Brest/LABS). Default-branch heads remain `1aa1234...` and `4232311...`, respectively, unchanged since the prior audit. Current recursive trees were not truncated; no newer same-length witness was identified. Kumar's [publication list](https://nirajkumar92.github.io/publications.html) points to the same Zhang arXiv entry.
- The laboratory's newer [PSL preprint v2](https://www.preprints.org/manuscript/202605.0907) is a PSL-focused result, not evidence of a better E at either target length. The page identifies v2, posted 28 July 2026.
- [Endless Exam's published index](https://github.com/ricolalemon/endless-exam/blob/9fc1ece969c0d9dec056f78ac4e83dbcf2c90a9e/bench/results/published/index.csv) is unchanged: 85 LABS rows across five instance IDs, corresponding to N=240,280,281,357,375, with no target-length overlap.
- The earlier audit's [PCE/NISQ paper](https://arxiv.org/html/2506.17391v2) remains v2 and reports exact simulations through N=45; the [direct-PUBO paper](https://arxiv.org/html/2510.24237v1) remains v1 and benchmarks N=5..99. Neither supplied a replacement witness for N=114 or N=464.

## Limits and failures

Searches covered the exact candidate length/energy pairs, current LABS merit-factor records, named papers and author repositories. No stronger verified same-length result was found; search-index absence does not exclude unpublished, unindexed, private, other-branch, or other-repository results. Repository checks cover the returned default heads and trees, not every fork, branch or discussion. The dual-step journal version and the prior ROADEF abstract were not separately reacquired in this short audit.

The context HTML converter failed for all three main paper URLs because `turndown` was missing. Direct public HTTPS retrieval succeeded. Optional local extractors `bs4` and `pdftotext` were unavailable; standard-library HTML parsing and the web tool's PDF text were used instead. Direct retrieval of the PSL preprint returned HTTP 403; its content was accessible through the web tool, so no direct body hash is claimed for that page. No downloaded code was executed, no full papers were saved or redistributed, and nothing was posted.
