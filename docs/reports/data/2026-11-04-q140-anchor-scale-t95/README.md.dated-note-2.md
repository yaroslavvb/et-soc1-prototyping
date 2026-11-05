# Dated note 2 on the paired-anchor card scale at 95% (Wed 4 Nov 2026, week 45, about 17:2x PST, Q141(r)'s fix pass)

*Written beside [`README.md`](README.md) and [the first dated note](README.md.dated-note.md), and not inside either: both stay as
committed (`a7fbb2ac`, `efaaa726`). Post hoc, unregistered and desk only. Nothing registered, frozen or measured changes, and rank 4's
rule for pool 7 (Q140(x), `75802201`) is untouched. It answers the records' verifier (Wed 4 Nov 2026, about 16:42–17:15 PST), which
read the first note's method. Like that note, it changes no prediction of power or heat: it says how robust one card pair's interval
is to how it is computed.*

**The result.** The first note's **±3.7%** for int8 (3.06 Welch degrees of freedom) assumes that its two anchors are independent: it
gives each anchor's ratio its own variance and adds them, though both anchors ran in the same passes. Read at the level of the pass,
which keeps any correlation between anchors inside a pass, int8's scale is **±3.85% at 95% at 2.25 Welch degrees of freedom**, and
the floats' **±0.21% at 4.96**. The correction stands either way: both readings are under the README's old low end (4.07%) and over
the doubled ±3% the README corrected.

| Scale, card 1 over aifoundry3 | Reading | Scale | Relative s.e. | Welch df | t (0.975) | 95% half-width |
|---|---|---|---|---|---|---|
| int8 (2 anchors) | each anchor's own variance, anchors independent (the first note) | 0.9580 | 1.18% | 3.06 | 3.15 | 3.71% |
| int8 (2 anchors) | pass level: one index per pass (this note) | 0.9580 | 0.99% | 2.25 | 3.881 | **3.85%** |
| floats (4 anchors) | each anchor's own variance, anchors independent (the first note) | 0.9619 | 0.10% | 7.36 | 2.34 | 0.24% |
| floats (4 anchors) | pass level: one index per pass (this note) | 0.9619 | 0.08% | 4.96 | 2.577 | **0.21%** |

The two int8 anchors' D correlate **+0.71** across aifoundry3's 4 passes and **−0.40** across card 1's 3: the independent reading
understates the spread on one card and overstates it on the other, and with 3 and 4 passes neither correlation is measured well.
Since the pass-level reading has fewer degrees of freedom, its t is larger, and it comes out slightly wider for int8 and slightly
narrower for the floats. The scale itself is the same in both readings: the pass-level index's mean is the mean of the anchors'
ratios when every anchor has a D in every pass, as here (aifoundry3's passes 15310–15313; card 1's 15710, 15712 and 15713, its
pass 15711 having no D).

**How it was made.** [`anchor_pass_level.py`](anchor_pass_level.py), new code: in each pass, each anchor's mean D over its non-failed
runs is divided by that anchor's mean D on aifoundry3, and the family's anchors are averaged, giving one index per pass; the scale is
card 1's mean index over aifoundry3's, its relative variance adds the two cards' (the delta method on a ratio of two means), and its
degrees of freedom are Welch's, on 3 passes against 4. It reads only E153's and E157's committed
[`runs.csv`](../2026-11-03-e153-blind6-aifoundry3/runs.csv) ([card 1's](../2026-11-03-e157-blind6-card1/runs.csv)) and takes the t
quantile from this directory's [`anchor_scale_t95.py`](anchor_scale_t95.py); standard library only:

    python3 -I -B anchor_pass_level.py <lab clone> anchor-pass-level.json > anchor-pass-level.txt

Its output is [`anchor-pass-level.json`](anchor-pass-level.json) and [`anchor-pass-level.txt`](anchor-pass-level.txt). The records'
verifier computed the same pass-level variant with code of its own, and every figure in the table agrees with it to the digits shown.
No verifier has read this script.

**Where the records carry it.** Q140's "How to read ±" in [`05-claims.md`](../../../findings/05-claims.md), in a fourth dated clause,
every earlier word kept.

SPDX-License-Identifier: Apache-2.0
