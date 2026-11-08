# E184 arm B's README, dated note 1 (Sun 8 Nov 2026; after the data verifier): E184-M's registered bootstrap resamples each sample's two ratios apart; resampled by sample, f's interval is about 0.0001 narrower at each end, and the verdict, which turns on the levels' span, is unchanged; two records lines

*Written on the Intel from about 03:40 PST on Sun 8 Nov 2026, desk only, after the data verifier of E184's two arms (Sun 8 Nov 2026,
02:40-03:09 PST: holds with fixes, 0 critical, 0 major, 3 minor and 4 nits). **Arm B holds as committed:** every kit reader re-ran on this
directory byte for byte, and the verifier's own code gave every registered figure. [`README.md`](README.md) and
[`SHA256SUMS-arm-b`](SHA256SUMS-arm-b) (lab `8bf74b26`, 00:43:41 PST) stay as committed, with every file of arm B's collection. **No
number, rule, verdict or gate reading changes:** E184-T PASS and E184-M NOT RESOLVED, as committed. The note answers the verifier's one
nit in arm B's scoring (section 1, fault 6) and its records lines that touch arm B (section 2, fault 7). Arm S's faults are in
[`README-arm-s.md.dated-note-1.md`](README-arm-s.md.dated-note-1.md), and the figures here are that note's
[`posthoc_note1_e184.py`](posthoc_note1_e184.py)'s output, [`posthoc-note1-e184.json`](posthoc-note1-e184.json) > B6, pinned with both
notes in [`SHA256SUMS-note1`](SHA256SUMS-note1).*

## 1. E184-M's f interval: the registered bootstrap breaks each sample's pairing (fault 6, nit)

E184-M's scorer (`score_e184.score_b`, which score v3 calls unchanged) draws its bootstrap of f = (min/max + 1) / 2 in a particular way.
It resamples the pooled min/avg list and the pooled max/avg list **with independent indexes**, so a draw pairs one sample's min/avg with
another sample's max/avg. The two lists are paired by sample. In
[`reduced-e184b-v4.json`](reduced-e184b-v4.json) > passes > 18441 > levels, each level's `min_over_avg_all` and `max_over_avg_all` come from
one list of (min/avg, max/avg) pairs. There are 483 pooled samples in the 10 scored levels. Resampling samples keeps each pair together:

| bootstrap of f | draws, seed | 95% interval |
|---|---|---|
| **registered** (independent indexes), re-made here | 2,000, 18404 (the scorer's) | **[0.706996, 0.709585]**, equal to `scored-e184-v3.json` > arm_B > E184-M > f_ci95 |
| paired (samples resampled) | 2,000, 18404 | [0.707052, 0.709545] |
| registered | 20,000, 20261108 | [0.707039, 0.709603] |
| paired | 20,000, 20261108 | [0.707089, 0.709500] |

The paired interval is about 0.0001 narrower at each end. The verifier's own paired run, with 4,000 draws, gave [0.707181, 0.709510].
Both intervals lie inside E184-M's band for f, 0.65-0.75, and f itself is 0.708189 either way. **The verdict does not move.** NOT RESOLVED
comes from the levels' min/avg medians, which span 0.081146 against the registered 0.06, and no bootstrap of f enters that (E184.md section
5.3). A future scorer resamples samples.

## 2. Records lines (fault 7)

- **8bf74b26's time.** Git gives 00:43:41 PST for the commit (author and committer), and the push ended at 00:43:43 (the card lane's
  commit record). Records that give 00:43:58 are wrong.
- **E184.md's labels.** In E184.md, **E184-T** is the SRAM rail's step response: tau inside 0.44-0.64 s, forecast 0.54 s, and today PASS at
  0.515 s rise and 0.520 s fall. The forecast that card 1's SRAM rail reads about 30% low (f 0.698, the rail about 1.43 times its reading)
  is **E184-M**'s, H-MIX. A record that puts that forecast under E184-T uses the wrong label; this README and the scored files use
  E184.md's.

## What does not change

README.md, SHA256SUMS-arm-b (80 of 80 OK) and every file of `8bf74b26`; arm S's files (`f8d94224`). E184-T PASS (SRAM rise 0.515 s
[0.472, 0.558], fall 0.520 s [0.489, 0.551]); E184-M NOT RESOLVED (f 0.708189 [0.706996, 0.709585], the levels' min/avg span 0.081146);
the reported E184-X, E184-R and E184-G and the control rails, as committed.

## Labels

- **Registered, blind:** E184-T's and E184-M's verdicts and figures, as committed.
- **Post hoc** (written after the data; deciding nothing): the paired bootstrap and the 20,000-draw re-runs.

SPDX-License-Identifier: Apache-2.0
