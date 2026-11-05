# Dated note beside README.md, Wed 4 Nov 2026 (week 45), about 17:4x PST: an in-place fix named, the boot time's zone, the largest miss split, and which runbook ran (E166's fix pass)

*Written beside [`README.md`](README.md) and not inside it. It records what the verifier of E166 and E163 found in this README (Wed 4 Nov
2026, about 17:17–17:27 PST). Its verdict was "holds with fixes": the data, the stops, the scorer (re-run byte for byte), the C check, the
order, the window, the post and the privacy all hold, and its items are wording and records only. Desk only: no verdict, number, band,
prediction, rule or frozen file changes, and no device command is involved. It answers the same items as the README: the kinds page's
[section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open) items 9, 8 and 6, and rank 3 of Q139's
final critic.*

## 1. One bullet was changed in place, in `4293d151`

The README was committed in `179549ce` (15:41:09 PST). Its fourth bullet was then changed in place in `4293d151` (16:54:31 PST, E163's data
commit, whose subject says so), before any verifier had read it. Elsewhere in this project a committed data README is corrected by a dated
note like this one. The bullet as first committed read:

> **Every dispatch's C is bit-exact:** 6,692 of 6,692 PASS against the RTL's arithmetic (Q139(k)'s `ccheck.py`, `--jobs 2`): the smoke's 48
> and the pass's 6,644 (fp32 4,130, int8 2,562; no ROUNDING, UNMODELLED or FAIL; no broken record), in the pass's 493 process launches.

It put the fp32 / int8 split on the pass's 6,644 dispatches. The split is of all 6,692: `ccheck/ccheck-all.json` › `summary.by_type` gives
fp32 4,130 and int8 2,562 PASS, 6,692 in all. The bullet now reads:

> **Every dispatch's C is bit-exact:** 6,692 of 6,692 PASS against the RTL's arithmetic (Q139(k)'s `ccheck.py`, `--jobs 2`; fp32 4,130,
> int8 2,562; no ROUNDING, UNMODELLED or FAIL; no broken record): the smoke's 48 and the pass's 6,644, the latter in the pass's 493 process
> launches.

Those two lines are the only change to this directory since `179549ce`. The first text stays in git history
(`git show 179549ce:docs/reports/data/2026-11-04-e166-heat-replicate-aifoundry3/README.md`).

## 2. The boot time is PDT

§ Registered before any data, the last bullet: *"Booted 26 Oct 15:18:24 PST"* should read **"Booted 26 Oct 15:18:24 PDT (14:18:24
PST)"**. `uptime -s` prints the boot in the zone in force on the boot date, and 26 Oct 2026 was still under daylight time, which ended on
1 Nov. The same look read "up 9 days, 0 min" at 14:18:26 PST on 4 Nov, which puts the boot at about 14:18 PST. The README's conclusion
stands: the host kept one boot all day, the boot the claim read (the last look, at 16:57:11 PST, read the same boot).

## 3. The largest single miss, split

§ What this does to predicting power and heat, **After**, ends: *"the bits-to-watts error of M8 on int8's whole-line class is the largest
single miss."* That puts the whole of the miss on M8's watts. The registered scorer splits each reading's error from the bits into M8's
watts and the heat path (`scored.json` › `readings.*`: `E_M8.plateau_err_C`, `A_plateau_err_C`, and their difference
`E_minus_A_plateau_C`):

| reading | from the bits, M8 (°C) | M8's watts part (°C) | given the measured watts, arm A (°C) |
|---|---|---|---|
| K_S | −0.248 | −0.481 | +0.233 |
| K_Q | −0.014 | −0.213 | +0.200 |
| **K_L** | **+0.869** | **+0.466** | **+0.403** (9.15% of its 4.409 °C rise) |
| K_O's window | +0.037 | −0.205 | +0.242 |
| K_OL's long window | +0.371 | −0.029 | +0.400 |

So the clause should read: *"the largest single miss from the bits is K_L's, int8's whole-line class: +0.87 °C, of which about +0.47 °C is
M8's watts and +0.40 °C remains given the measured watts."* M8's watts part is as large on K_S (−0.48 °C), where arm A's +0.23 °C offsets
part of it in the plateau. § What the two misses are, "RK3-a fails on the power path, mostly", and its K_L figures (+0.87 °C from the bits,
+0.40 °C given the watts) are right as written.

## 4. Which runbook ran

Every runbook step for E166 ran Q141(k)'s **v1** (`e962227a`): the look, the sync, the preflights, the reads, the dry pass and the launch
(14:18:20–14:20:56 PST), the waits, and the collection. v2 (`16771f36`) was committed at 15:34:42 PST, while E166's session was still
running, and its dated note says to use v2 for any later step or card day. The collection (`s22_collect.sh e166`, 15:35:29–15:35:55) was
the one E166 step after that commit, and it still ran v1. Nothing would have read otherwise. In that script v2 changes only E167's
collection route, and its shared helpers add only checks this collection did not reach (a lost dry job, state written on another day,
E170's queue on aifoundry1, the box a login link names). v2's guard against a plain E166 retry over an earlier smoke was never needed:
E166 was launched once, at 14:20:56, before v2 existed.

SPDX-License-Identifier: Apache-2.0
