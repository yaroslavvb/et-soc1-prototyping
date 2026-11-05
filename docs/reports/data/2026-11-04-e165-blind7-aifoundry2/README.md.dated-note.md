# Dated note beside README.md, Wed 4 Nov 2026 (week 45), about 18:30 PST: the committed check of C, where the board's blind error sits (post hoc), the dip range, the boot's zone, and which runbook ran (the fix pass after aifoundry2's verifier)

*Written beside [`README.md`](README.md) and not inside it. It records what the verifier of aifoundry2's card day (E165, E167, E168 and
E169; finished about 18:09 PST) found in this README and in the lane's own summary of it. Its verdict was "holds with fixes": the data,
the stops, the device commands, the order, the window, the post and the public-text scan all hold, and the registered scorer, re-run from
the committed data, reproduced `results.json` (10,682 leaf fields, 0 differ) and `score.txt` (85 lines, identical). Its items are wording
and records only. Desk only: no verdict, number, band, prediction, rule or frozen file changes, and no device command is involved. It
answers the same items as the README: the kinds page's
[section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open) item 6, and rank 2 of Q139's final
critic.*

## 1. Only the gzipped check of C for `s1` is committed

§ Files, the row for `ccheck-*.json`, reads: *"the check of C per session (`ccheck-s1.json` also gzipped)"*. The data commit
(`4c6665f0`) holds `ccheck-s1.json.gz`, `ccheck-smoke.json` and `ccheck-stoptest-board.json`; the plain `ccheck-s1.json` is not
committed. ([`collect_e165_bounded.sh`](../../../../tools/claims-v3/e165/collect_e165_bounded.sh) line 106 runs `gzip -n -k`, which
keeps both copies in the collection directory; only the gzipped one went into the commit.) So the row should read: *"the check of C per
session (`s1`'s committed gzipped only, as `ccheck-s1.json.gz`)"*.

To re-score from the committed files, decompress it first: the collector's scorer call passes `ccheck-s[0-9]*.json`. From the repo root,
with `<copy>` a copy of this directory:

```
gzip -dc <copy>/ccheck-s1.json.gz > <copy>/ccheck-s1.json
python3 -B tools/claims-v3/e165/score_e165.py <copy>/aifoundry2/s1 --ccheck <copy>/ccheck-s1.json --out <copy>/results.json > <copy>/score.txt
```

That is how the verifier re-scored it (about 3.5 minutes on one core), with the result above.

## 2. Where the board's blind error sits (post hoc)

§ What this does to predicting power and heat says of the pinned clock (E165-F2): *"no model of the bits predicts it: it is a session
term of the governor, not of the data."* That holds for the pinned clock, as written. It is not the board's account, and the lane's
summary of the day carried it over to the board. Split by tile with [`posthoc_board_split.py`](posthoc_board_split.py) (standard library;
it reads only `results.json`, and first reproduces the registered E165-R2 Bp and Bg lines exactly) →
[`posthoc-board-split.txt`](posthoc-board-split.txt). The error is measured minus M9's aifoundry2 part, recomputed per tile (the
registered primary).

| the pinned board: 40 tiles, 0.986 W rms | share of its squared error | rms without them |
|---|---|---|
| five class S tiles (single high B bits) over M9's part by +1.80 to +2.52 W: fp32 `b_onebit_b22_third` +2.52, `b_onebit_b20_pi` +2.04, `b_onebit_b20_full` +2.03, fp16 `b_onebit_b8_pi` +2.02, fp32 `b_onebit_b20_seventh` +1.80 | **57%** | 0.695 W over 35 |
| the six tiles with a single-pass clock dip (one pass at 752.0-780.0 MHz, the others at 800); their board errors −1.83 to +0.28 W | 22% | 0.947 W over 34 |
| both sets left out | | 0.540 W over 29 |

Class S's eight pinned tiles hold 61% in all; the other three read +0.46, −0.85 and −0.96 W (`fp16.b_onebit_b9_one`, at −0.96 W, is
also a dip tile). **The governed board** (12 tiles, 0.714 W rms) is a level and a spread: M9's part reads 0.425 W high on average at the
cap (10 of 12 tiles under it), with a 0.574 W spread about that level; the level is 35% of its mean squared error.

So, for the records, post hoc and labelled so (no rule was registered for this split): *"the pinned clock's residual is a session term
(one pass on each of six tiles dipped to 752-780 MHz); the pinned board's largest errors are five single-high-bit tiles 1.8-2.5 W over
M9 (class S, a data term: 57% of the squared error, 0.70 W rms without them), and the same six dips hold 22%; the governed board reads
0.43 W under M9 at the cap, with a 0.57 W spread about that level."* The README's peaks sentence (the board's peak samples over M9's 95%
upper peak on six single-bit tiles) is a reading of the peaks, separate from this one, and stands.

## 3. The dip range

The same paragraph gives the six dip passes as *"752-781 MHz"*. They ran at 752.0-780.0 MHz (`results.json` › `cells` ›
`burst_mhz_runs`), as the README's own list says (`fp32.exp_b_alt_lsb` 780 MHz, the highest). Read "752-780 MHz".

## 4. The card's identity, and the boot's zone

The README gives no boot time; the lane's summary gave it as "2026-10-26 15:13:03 PST". The runbook's step 14 (v1, 14:19-14:22 PST) read
aifoundry2's `uptime -s` as `2026-10-26 15:13:03`. That is **PDT, 14:13:03 PST**: `uptime -s` prints the boot in the local time of the
boot date, and daylight time ran until 1 Nov. The committed queue record agrees: [`aifoundry2/queue.jsonl`](aifoundry2/queue.jsonl) line 3
reads *"14:31:41 up 9 days, 18 min"* at the queue's start, a boot at about 14:13 PST on 26 Oct, and line 18 reads *"15:10:13 up 9 days,
57 min"* at its end, the same boot. That boot precedes E69's firmware read (2026-10-27 13:56:26 PDT), so the card ran BL2 0.22.0 by
host-boot continuity. v1's step 14 compared the boot with nothing; v2's step 14 (`16771f36`) refuses unless the boot precedes that read,
comparing instants, so the zone label never enters it, and the runbook's dated note records that the day's reading passes it. The card's
identity was never read with the firmware-revisions query.

## 5. Which runbook ran

Every runbook step for E165 ran Q141(k)'s v1 (`e962227a`): the look, the tree and its preflights, the dry pass (14:22:55-14:23:24 PST),
the launch (14:31:41), the waits, and the collection (`s22_collect.sh e165`, 15:23:23-15:40:27). v2 (`16771f36`) was committed at
15:34:42, during the collection's desk part, and its dated note says to use v2 for any later step; the collection ran on in v1. Nothing
would have read otherwise: v2's `s22_collect.sh` takes E165 by the same route (it changes only E167's, which probes all three boxes).
The collection's box-side part, the copies and the box's file hashes at nice 19 (about 15:23:24-15:23:32 PST), fell in E167's first
15-minute rest with no launch (15:14:18-15:29:18), not in a hold: aifoundry2's 5 s history, committed with E167
(`../2026-11-04-e167-heat-replicate-aifoundry2/history/`), reads host CPU 0.1-6.6% from 15:23:20 to 15:24:10 PST.

SPDX-License-Identifier: Apache-2.0
