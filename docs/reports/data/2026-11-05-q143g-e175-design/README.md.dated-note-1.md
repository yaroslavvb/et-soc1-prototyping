# E175's design, dated note 1: three corrections to this README, the lane's process disclosures, and which hash lists "pass" covers (Q143(g) fix pass)

*Written Thu 5 Nov 2026 (week 45), from about 14:55 PST, on the Intel, desk only: nothing measured, no card, no lab box. [`README.md`](README.md)
and every file of this directory (lab `b3f5e83c`) stay as committed. It answers three items from Q143(g)'s verifier, on the kinds page's
[section 11, item 6](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open):
- its records nits (section 1 below);
- its second fault, the lane's own process slips, which the lane disclosed (section 2);
- its carried item on hash lists (section 3).

Each correction was re-checked here from this directory's committed files. None changes a tile, a count, a prediction, the selection or the
pool.*

## 1. Corrections

1. **Results 2** says "The three zeros anchors and candidates in stream order, at the nine points of N = 9 ... 720 points", and the lane's
   result repeated it as "80 candidates plus the zeros anchors". **The zeros anchors were not counted on E175's bench.** The five count files
   `bench/counts-e175-{s1,a1}-c*.json` hold 80 tile rows, the 80 candidates, and none is a zeros anchor. The 720 points are those 80
   candidates' (80 × 9). The zeros anchors' points come from Q142(x)'s committed counts
   (`docs/reports/data/2026-11-05-q142x-pool8-freeze/bench/counts-x-s1-f03.json` and `counts-x-s1-i04.json`, as E175.md's predictions step 3
   says) and from pool 6's and pool 7's committed points: each anchor's `points_from` in
   `predict-candidates/predictions-pool8-aifoundry2.json` reads "given counts", `blind6:<type>.anchor6_zeros` and `blind7:<type>.anchor7_zeros`.
2. **Checks**, second bullet, names only the bench manifest's sha256 (`bench/manifest-bench.json`, `00c8225c…`, candidates 0-63). The A1 chunk
   (candidates 64-79) ran on **`bench/manifest-bench-a1.json`, sha256 `a98e78d2…`**. That is the `pool_manifest_sha256` its run record
   `bench/counts-e175-a1-c64-run.json` carries, and the file is committed here and listed in `SHA256SUMS`. The four registered chunks' run
   records carry `00c8225c…`.
3. **Disclosed**, second bullet, names the 12:27 PST preview of `plan` and `predict` on candidates 0-15, but not what followed it. As counts
   arrived, `plan`, `predict` and `select` also re-ran into the lane's scratch at K = 32, 48 and 64 candidates. The read at K = 64, the
   registered stream's end, is the one that led to dated note A1: 46 governed, 11 over 82 W, 7 pinned, from groups and peaks only. The
   committed outputs are the runs at K = 80. (The lane's own result states this; this README did not.)

## 2. The lane's process: three disclosures, as the lane's result states them

The verifier checked these from the lane's scratch. None touched a card, a box or an output, and every output re-made byte for byte at the
verifier's desk.
- One background waiter, at about 12:32 PST, ran inside `bash -c`. The session's rules for unattended shell calls forbid that form. It ended
  on its own, and later waits used a script file.
- One stderr capture of one call, at about 12:15 PST, was written to `/tmp` on the Intel, where the rules keep scratch in the session's own
  directory. It was removed at once.
- About 25 sub-second steps of the build, manifest, select and compare scripts called the system python directly, outside the round's local
  job slot. They were each under a second.

## 3. Which hash lists "pass" covers

The lists this README names pass, and still pass after this note's commit:
- the registration's 40;
- the predictor's 16 and 9;
- POOL8-SHA256SUMS's 209;
- this directory's 164;
- the pool's 28.

Elsewhere in the repo, three older lists still read a mismatch, as the last critic found and E175's verifier confirmed:
- `docs/reports/data/2026-11-01-e111-heat-steady/manifest.sha256` and `docs/reports/data/2026-11-02-q136a-int8-netlist-predictions/sha256.txt`
  each name a README that a later corrections commit edited (1-2 Nov);
- the mismatch of `docs/reports/data/2026-10-20-bitflip-ladder/gen-a1.sha256` comes from how its paths resolve, not from a changed file (the
  verifier's reading).

Their dated notes belong to the next records round. Where E175's records say the lists pass, they mean the named lists.

SPDX-License-Identifier: Apache-2.0
