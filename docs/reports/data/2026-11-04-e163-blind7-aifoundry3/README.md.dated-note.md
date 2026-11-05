# Dated note beside README.md, Wed 4 Nov 2026 (week 45), about 17:4x PST: the session's excess over M9 as registered, the card-scale labels, and which runbook ran (E163's fix pass)

*Written beside [`README.md`](README.md) and not inside it: the README stays as committed in `4293d151` (16:54:31 PST). It records what
the verifier of E166 and E163 found in this README (Wed 4 Nov 2026, about 17:17–17:27 PST). Its verdict was "holds with fixes": the data, the
stops, the scorers (re-run byte for byte), the order, the window, the post and the privacy all hold, and its items are wording and
records only. Desk only: no verdict, number, band, prediction, rule or frozen file changes, no device command is involved, and nothing in
this note was registered. It answers the same items as the README: the kinds page's
[section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open) item 6, Q140's final critic's ranks 1, 4,
9, 7 and 11.*

## 1. The excess over M9: what is registered, and what is not

The README reads the session's excess over M9 as more than its rules test, in three places:

- § Results, "What carries the misses", the B1 and B2 bullet: *"So the excess is a level of the whole board reading on this day, which M9
  does not model, more than a per-kind error."*
- § What it does to predicting power and heat, **After**: *"fp32's rose from 0.330 to 0.389 W, carried by the single high bits and the
  session's level."*
- the same section, **What it says to change**: *"a day-to-day level term (this session read +0.15 W on the floats, and every re-run tile
  read high), which a refit cannot take from the bits alone"*.

**What is registered.** B1 and B2 read FAIL LOW: the session reads +0.151 W above M9 on the 26 float kinds and +0.051 W on the 22 int8
kinds, outside M9's nested errors. By format the bias is reported, not ruled on: +0.205 W on fp32, +0.049 W on fp16, +0.051 W on int8
(`scored.json` › `primary.primary.reported.M9.power`). K14-D fails, and every one of the 16 re-run tiles reads higher than in its earlier
session, by +0.013 to +0.278 W ([`results.md`](results.md); [`scored.json`](scored.json) › `verdicts`, `primary.K14`).

**What is not.** No registered rule tests a level of the board, a day term, or a level against a gain.
- D is read over the session's own zeros, so a level common to the whole board reading cancels in D. What B1, B2 and K14-D see is an excess
  in D itself.
- A gain reads as well as a level does. The card scale, a reported item (E163.md § Reported), is 1.0056 [1.0031, 1.0104] on the floats and
  1.0112 [1.0022, 1.0218] on int8 (`scored.json` › `primary.CS`).
- Post hoc, the committed per-tile rows do not separate the two (§ 3).
- Day against session is not tested. Every re-run reference is another day's session on this card: ten tiles from E141 (Mon 2 Nov), six
  from E152 (Tue 3 Nov) (`scored.json` › `primary.K14.by_source`).

**The three passages, as they should read:**
- *"So the session reads above M9 on every format (B1/B2 FAIL LOW, every re-run tile higher than before). This is a session-wide level or
  gain, not separated here (the reported card scale is 1.0056 floats, 1.0112 int8): a post hoc reading, not a registered one."*
- *"fp32's rose from 0.330 to 0.389 W, carried by the single high bits and the session-wide excess over M9."*
- *"What it says to change: the session read above M9 on every format, and every re-run tile read high. No rule scored here says whether
  that is a level or a gain in D, or whether it belongs to the day, the session or the card. The registered test of a scale between
  sessions is rank 4's pair rule on E163 and E164 (Q140(x)'s `score_rank4.py`: a card's scale from its random anchors, against the pool's
  median ratio), which E164's lane scored after this README was written (`5eecc457`, 17:28:54 PST)."* The README's second item, the
  single-high-bit counts (from 0.54 to 0.38 W rms at 27 points, reported), stands as written.

## 2. The card-scale labels in `results.md`

[`results.md`](results.md) § "Card scale (reported)" prints **PASS** for the floats and **FAIL** for int8. Those words are the readings of
E153's old CS0 line (the scale within 1% of 1). For E163 the card scale is reported only (E163.md § Reported: "the card scale on this card
(…: M9's scale of 1 on its own card, reported, no longer a rule)"), and `scored.json` › `primary.CS` gives each entry
`"verdict": "REPORTED"` beside its `"reading"`. Neither label is a rule or a verdict.

## 3. How the post hoc check was made

[`posthoc_level_gain.py`](posthoc_level_gain.py) reads only `scored.json` beside it: each tile's M9 prediction and its measured D on the
registered primary. For each family it fits the error (measured − M9) against M9's predicted D by ordinary least squares, over every scored
tile except class S (the single high B bits, the largest per-kind miss) and the zero anchors. It uses the standard library only:

    python3 -I -B posthoc_level_gain.py scored.json > posthoc-level-gain.txt

The output, [`posthoc-level-gain.txt`](posthoc-level-gain.txt) (± one standard error):

| family | tiles | M9's D (W) | both terms: level, gain | a level alone | a gain alone |
|---|---|---|---|---|---|
| floats | 24 | 9.26–24.72 | −0.100 ± 0.118 W, +1.09 ± 0.59% of D | +0.110 ± 0.031 W | +0.60% of D |
| int8 | 26 | 2.58–7.38 | −0.090 ± 0.188 W, +2.27 ± 2.96% of D | +0.052 ± 0.034 W | +0.88% of D |

A level alone describes the rows, and so does a gain alone; fitted together, neither term is resolved. The verifier's own fit on the floats
gave the same figures. This is a reading, not a rule, and it changes no verdict.

## 4. Which runbook ran the card day

The box steps ran Q141(k)'s runbook **v1** (`e962227a`) throughout, the sync in § Registered before any data included. v2 (`16771f36`,
15:34:42 PST) says in its dated note: for any later step or card day, use v2. After that commit, E163's look and launch (15:35:52–15:35:59),
its wait (15:41:34–15:50:20) and the last look (16:57:11) still ran on v1's scripts, and the lane's other bounded calls used v1's
`rb_common.sh`. No gate would have read otherwise. v2 adds two checks to that launch, and both pass on the day's record:
- FULL's 4,200 s from the launch at 15:35:59 end at 16:45:59, before the round's last end at 19:00 PST.
- E166's log offset was written that day, at E166's launch (14:20:50–14:20:56).

D1 (§ Registered against what happened) holds for v2 as well: both versions' `s22_collect.sh e163` copy into the absolute
`$RB_REPO/build/e163-raw` (v1 line 55, v2 line 59), and `reduce_e78.py` records the pass directories as given (line 428).

SPDX-License-Identifier: Apache-2.0
