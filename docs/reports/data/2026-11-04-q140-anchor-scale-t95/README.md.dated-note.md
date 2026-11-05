# Dated note on the paired-anchor card scale at 95% (Wed 4 Nov 2026, week 45, Q141(r))

*Written beside [`README.md`](README.md) and not inside it, after Q140's final critic (Q140(f), Wed 4 Nov 2026, from about 08:10
PST), whose fault 1 it records; the README stays as committed in `a7fbb2ac`. Post hoc and desk only. Nothing registered, frozen or
measured changes, and rank 4's rule for pool 7 (Q140(x), `75802201`) is untouched. It answers rank 4 of Q139's final critic (the
paired-anchor card scale) under the kinds page's
[section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open) item 6. It changes no prediction of
power or heat: it says how wide one card pair's measured scale is.*

**The correction.** The README gives int8's 95% half-width as **4.1–6.1%**, between two cases for pool 6's anchor error: a copy of
E78's (2.14 degrees of freedom) or an independent error of the same size (4.28). Neither case is needed. Pool 6's random anchors have
committed passes of their own, one run a pass, in E153's and E157's primary `runs.csv`. With each anchor's own passes, on both
cards, int8's scale (the mean of its two anchors' ratios, card 1 over aifoundry3) is 0.9580 with a relative standard error of 1.18%,
**±3.7% at 95% at 3.06 Welch degrees of freedom**; the floats' (the mean of four) is 0.9619, 0.10%, **±0.24% at 7.36**. So the
README's ±4.1–6.1% is too wide; the doubled ±3% of the clause it corrected is still too narrow for int8.

| Scale, card 1 over aifoundry3 | Anchors, with their own passes | Ratio | Relative s.e. | Welch df | 95% half-width |
|---|---|---|---|---|---|
| int8 | `int8.full` (E78's; 4 passes on aifoundry3, 3 on card 1), `int8.anchor6_full` (pool 6's; 4 and 3) | 0.9580 | 1.18% | 3.06 | **3.71%** |
| floats | `fp32.randn`, `fp32.anchor6_randn`, `fp16.randn`, `fp16.anchor6_randn` (4 and 3 passes each) | 0.9619 | 0.10% | 7.36 | **0.24%** |

The point against pool 6's median does not move: int8 −1.04%, floats −0.15% (README, Results), and rank 4's registered selftest
gives the same int8 anchor scale, 0.9580 ± 0.0113 from the passes
([`selftest-rank4.txt`](../../../../tools/claims-v3/kinds/blind7/selftest-rank4.txt) line 7). M8's and M9's fitted prices, a
jackknife over 66–370 kinds a family, are untouched: doubling their ± one standard error does give a 95% interval.

**How it was made.** [`anchor_t95_measured.py`](anchor_t95_measured.py) is Q140's final critic's post hoc script, committed here
unchanged. It reads only committed files: E153's and E157's
[`runs.csv`](../2026-11-03-e153-blind6-aifoundry3/runs.csv) ([card 1's](../2026-11-03-e157-blind6-card1/runs.csv)), each pass's mean
D over its non-failed runs, and the t quantile from this directory's [`anchor_scale_t95.py`](anchor_scale_t95.py) (`ablcore.py`'s,
verbatim). It uses the standard library only:

    python3 -I -B anchor_t95_measured.py <lab clone> anchor-t95-measured.json > anchor-t95-measured.txt

Q141(r) re-ran it on the lab clone at `4c6665f0`, after the critic, and its JSON is byte for byte the critic's:
[`anchor-t95-measured.json`](anchor-t95-measured.json), [`anchor-t95-measured.txt`](anchor-t95-measured.txt). No verifier has
read the script.

**Where the records carry it.** Q140's "How to read ±" in [`05-claims.md`](../../../findings/05-claims.md) and the Q140 row of
[`02-requests.md`](../../../findings/02-requests.md), each in a third dated clause, every earlier word kept.
