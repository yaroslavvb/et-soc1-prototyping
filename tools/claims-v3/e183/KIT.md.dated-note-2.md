# E183's kit, dated note 2 (Sun 8 Nov 2026, before any E183 datum): step 2 v3 runs the day-2 check before step 2 v2, so a committed change to E183's brief or to its M1 reader is seen, E183's three lists are pinned by their own bytes too, and october-forecast-model's M1 reader runs only behind the check's gate, after the data commit; no box file, rule, forecast, threshold, plan, cap, stop or order of box steps changes

*Beside [KIT.md](KIT.md) (`cc597bf2`) and [KIT.md.dated-note-1.md](KIT.md.dated-note-1.md) (`45e514e3`); it edits nothing there. Written
on the Intel, desk only (no card, no device command, no ssh to a lab box, no post in the lab's channel, no Modal), by the lane `fix-d2b`
of Q158b, begun at 07:46 PST Sun 8 Nov 2026 by the clock; its commit's own time is git's. It answers E183's side of the adversarial
verifier of the day-2 fixes (`verify-d2b`, Sun 8 Nov 2026 07:01-07:45 PST: **holds with fixes**, 0 critical, 0 major, 4 minor faults and 5
nits, none blocking): its fault 1 (no code read E183's M1 list before the reader) and fault 3 (no step read `SHA256SUMS-e183-brief`, so a
committed edit of the brief passed). E185's side is E185's kit note 3
([`../e185/KIT.md.dated-note-3.md`](../e185/KIT.md.dated-note-3.md)); fault 4 and the nits are in the brief's dated note
([`CARD-LANE-BRIEF.md.dated-note-1.md`](CARD-LANE-BRIEF.md.dated-note-1.md), the same in both kits). **No E183 datum exists**
(`git log --all` on `docs/reports/data/*e183*` and `*-e183-*`: nothing). **No box file changes:** the harness's 80 files, the 40 build
inputs, the session, the queue, the block, the stops and the device commands are the kit's as committed, and so is every step that
reaches the box.*

## Results first (desk only; nothing is measured)

| check | result | file |
|---|---|---|
| **the day-2 desk test** (E185's [`rb/selftest_day2_v1.sh`](../e185/rb/selftest_day2_v1.sh), one test for the day's check and both step 2s) | **SELFTEST-DAY2-V1 PASS, 25 of 25**; 0 calls to any box | [`../e185/rb/logs/selftest-day2-v1.txt`](../e185/rb/logs/selftest-day2-v1.txt) |
| **the dry listing v3** | 13 steps listed, 0 exiting non-zero, no ssh or rsync call; step 2 v3; the look before the day's post; the M1 gate after step 11 and the data commit | [`logs/dry-listing-e183-v3.txt`](logs/dry-listing-e183-v3.txt) |
| **device commands** | (a) the runbook as this note runs it, with E185's day-2 check: **GO, 11 send sites**, every one a READ, the same 11 as note 1's; (b) the day-2 note's new desk files: GO, 0 sites | [`logs/dmcmd-audit-note2-e183.txt`](logs/dmcmd-audit-note2-e183.txt) |
| **step 2 v3 and v2 for real** at this note's commit, on a scratch clone, with a window written that day | rc 0 each | the lane's own run (the records give its time) |

## Builds on

1. **Checked.** The prior-work inventory (Q145's stock-take, private scratch), read Sun 8 Nov 2026 at about 08:21 PST: public rows H24, H25
   and H28 (opaque pointers), as E185's kit notes read them; E183's KIT.md's own Checked rows stand.
2. **Used.** E183's kit note 1 (`45e514e3`): `rb/s03_desk_e183_v2.sh`, run unchanged inside step 2 v3, and `rb/list_steps_e183_v2.sh`, the
   form of the dry listing v3. E185's kit note 3: the day-2 check, [`../e185/rb/check_day2_v1.py`](../e185/rb/check_day2_v1.py), one for
   the whole day. E183's note M1 (`06286213`): its list `SHA256SUMS-e183-m1` (25, `c8bad971...`) and its reader's run line, which the gate
   runs. verify-d2b's cases H2f and H7, re-made.
3. **Not used.** Any change to a box file or a box step; any E183 datum (none exists); anything of the private tier.
4. **Tiers.** Public tier only. No private-tier check is used, so there is no sha256 line.
5. **Readiness.** This block is the note's own.

## The runbook as it now runs (note 1's section 8, with this note's changes)

| step | file | from this note |
|---|---|---|
| **0, before step 1** | **`/usr/bin/python3 -I -B tools/claims-v3/e185/rb/check_day2_v1.py tree --pull`** | **new:** the day-2 check by hand (the brief's dated note 1, section 1) |
| 1, the window | `rb/s02_window_e183.sh <day> <last start> <last end>` | unchanged |
| 2, the desk check | **`rb/s03_desk_e183_v3.sh`** | **new:** the day-2 check with its own pull, then step 2 v2 unchanged on the same tree, then HEAD unchanged |
| 3-11 | as note 1's section 8 (step 11 is `rb/s22_collect_e183_v2.sh`) | unchanged |
| **after the data commit** | **`/usr/bin/python3 -I -B tools/claims-v3/e185/rb/check_day2_v1.py m1 e183 --data <E183's data dir>`** | **new:** october-forecast-model's reader runs only behind the gate |

**Step 2 v2 is never run alone on E183's card day** (it runs inside v3), nor v1.

## Fault by fault

### verify-d2b's minor fault 3, E183's side: no step read E183's brief list

- **What it was.** `SHA256SUMS-e183-brief` (15 entries, its own sha256 `02c8b2b6...`) was read by no code, so E183's brief changed and
  committed passed E183's step 2 v2 and E185's step 2 v3 alike (H7).
- **What step 2 v3 does.** The day-2 check reads it at 15 and at its own bytes, its ten other entries a gate and its five M1 entries
  reported; and the history check sees any committed change on E183's paths. H7 now reads E183 v3 16 and E185 v4 16; v2 alone still 0.
- **verify-d2's nit 4, closed for the day:** E183's three lists (`SHA256SUMS-e183-registration` 20 `6defebd4...`, `-kit` 46
  `2e06e0cc...`, `-note1` 46 `24d0c583...`) are now checked at their own bytes too, beside v2's count pins, so a list rewritten with a file
  and its line, or a copied line, no longer passes (and the history check sees either).

### verify-d2b's minor fault 1, E183's side: nothing checked the M1 reader's bytes before the session

- **What it was.** No code read `SHA256SUMS-e183-m1`; the brief's `shasum -c` (25 of 25) passed a reader rewritten together with its line
  (H2f).
- **What the gate does** (`check_day2_v1.py m1 e183 --data <E183's data dir>`), **after E183's data commit**: the day-2 check (no pull);
  E183's seven M1 files (note M1, its json, reader, self-test and log, its list, and note M1's dated note 1) unchanged since `6860643c`;
  `SHA256SUMS-e183-m1` at 25 and at its own sha256 `c8bad97187caf6f3...`, 25 of 25 OK; the data directory committed and clean, the outputs
  not yet there. Only then does it run note M1's own run line (`/usr/bin/python3 -B tools/claims-v3/e183/arm_m1_read_e183.py --reduced
  <dir>/reduced-e183.json --scored <dir>/scored-e183.json --out <dir>/arm-m1-e183`), print its exit status, and check it wrote only its two
  outputs. A reader's refusal or non-zero exit is recorded, never a block. The outputs go in with a dated note beside the data README.
- **Its place moves**, from "after step 11's collection and before the data commit" (note M1; the brief's section 6) to after the data
  commit. The reading is unchanged.
- **Desk cases:** H2f, E183 v3 0 with the M1 change and the brief list's two M1 entries reported, and the gate 16, the reader not run; R4,
  the gate 0 on a stand-in data directory holding no reduction, the reader run and its rc 1 printed, nothing written.

## What does not change

KIT.md and note 1 and their files and lists; E183.md, its note 1 and its plans; note M1, its reader and its reading; the harness, the build
inputs and every step that reaches the box; the stops, the device commands, the budgets and the caps; the order with E185 (E183 only after
E185's step 14). The new files are new; v1's and v2's stay as committed.

## Files ([`SHA256SUMS-e183-kit-note2`](SHA256SUMS-e183-kit-note2), 15 entries)

This note; [CARD-LANE-BRIEF.md.dated-note-1.md](CARD-LANE-BRIEF.md.dated-note-1.md); [`rb/s03_desk_e183_v3.sh`](rb/s03_desk_e183_v3.sh)
and [`rb/list_steps_e183_v3.sh`](rb/list_steps_e183_v3.sh); the logs `logs/dry-listing-e183-v3.txt` and `logs/dmcmd-audit-note2-e183.txt`.
The list also pins E185's day-2 check, its desk test and the test's log, and the unchanged files step 2 v3 runs or names:
`rb/s03_desk_e183_v2.sh`, `rb/rb_e183.sh`, `rb/s02_window_e183.sh`, `rb/s22_collect_e183_v2.sh`, `SHA256SUMS-e183-brief` and the brief this
note's brief note corrects, `CARD-LANE-BRIEF.md`. It holds no file of note M1.

    bash tools/claims-v3/e183/rb/list_steps_e183_v3.sh <an empty scratch directory> > dry-listing-e183-v3.txt

## Labels

- **Registered:** every list, pin, step, gate, plan, cap and stop named here (E183.md with its note 1, KIT.md and its notes); this note's
  step 0, step 2 v3 and the M1 gate, before any datum.
- **Desk checks of code, not measurements:** every test result here.
- **Reported:** october-forecast-model's arms (note M1); their forecasts are blind for E183 (frozen before any datum).
- Nothing here is held out or post hoc.

SPDX-License-Identifier: Apache-2.0
