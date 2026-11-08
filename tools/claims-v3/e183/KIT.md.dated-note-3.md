# E183's kit, dated note 3 (Sun 8 Nov 2026, before any E183 datum): step 2 v4 runs the day-2 check v2 before step 2 v3 (v1's check on the perimeter of what the day's scorer and collectors load, and no untracked module in any of the day's directories), and october-forecast-model's M1 reader runs behind the check v2's gate; no box file, rule, forecast, threshold, plan, cap, stop or order of box steps changes

*Beside [KIT.md](KIT.md) (`cc597bf2`, git 21:53:34 PST Sat 7 Nov 2026), [KIT.md.dated-note-1.md](KIT.md.dated-note-1.md) (`45e514e3`, git
23:09:50 PST Sat 7 Nov) and [KIT.md.dated-note-2.md](KIT.md.dated-note-2.md) (`1e74546a`, git 08:37:53 PST Sun 8 Nov); it edits nothing
there. Written on the Intel, desk only (no card, no device command, no ssh to a lab box, no post in the lab's channel, no Modal), by the lane
`fix-fx` of Q158, begun at 11:31 PST Sun 8 Nov 2026 by the clock; its commit's own time is git's. It answers E183's side of the adversarial
verifier of the day-2 check (`verify-fx`, Sun 8 Nov 2026 10:42-11:3x PST: **holds with fixes**, 2 minor faults and 6 nits, none blocking):
its faults 1 and 2, which E183's day shares with E185's (one check for the whole day). E185's side and the check itself are E185's kit note
4 ([`../e185/KIT.md.dated-note-4.md`](../e185/KIT.md.dated-note-4.md)); nit 8 is in the brief's dated note 2
([`CARD-LANE-BRIEF.md.dated-note-2.md`](CARD-LANE-BRIEF.md.dated-note-2.md), the same in both kits). **No E183 datum exists** (`git log
--all` on `docs/reports/data/*e183*` and `*-e183-*`: nothing). **No box file changes:** the harness's 80 files, the 40 build inputs, the
session, the queue, the block, the stops and the device commands are the kit's as committed, and so is every step that reaches the box.*

## Results first (desk only; nothing is measured)

| check | result | file |
|---|---|---|
| **the day-2 desk test v2** (E185's [`rb/selftest_day2_v2.sh`](../e185/rb/selftest_day2_v2.sh), one test for the day's check and both step 2s) | **SELFTEST-DAY2-V2 PASS, 20 of 20**; 0 calls to any box | [`../e185/rb/logs/selftest-day2-v2.txt`](../e185/rb/logs/selftest-day2-v2.txt) |
| **the dry listing v4** | 13 steps listed, 0 exiting non-zero, no ssh or rsync call; step 2 v4; the look before the day's post; the M1 gate v2 after step 11 and the data commit | [`logs/dry-listing-e183-v4.txt`](logs/dry-listing-e183-v4.txt) |
| **device commands** | (a) the runbook as this note runs it, with E185's day-2 checks v2 and v1: **GO, 11 send sites**, every one a READ, the same 11 as note 2's; (b) the note's new desk files: GO, 0 sites | [`logs/dmcmd-audit-note3-e183.txt`](logs/dmcmd-audit-note3-e183.txt) |
| **step 2 v4 and v3 for real** at this note's commit, each with a window written that day | run by the lane first on a scratch clone holding this same commit, then on the lab clone after it | the lane's own runs (the records give each exit status and time) |

## Builds on

1. **Checked.** The prior-work inventory (Q145's stock-take, private scratch), read Sun 8 Nov 2026 at 11:58:12 PST: public rows H07, H08,
   H09, H24, H25 and H28 (opaque pointers), as E185's kit note 4 reads them; E183's KIT.md's own Checked rows stand.
2. **Used.** E183's kit note 2 (`1e74546a`): `rb/s03_desk_e183_v3.sh`, run unchanged inside step 2 v4, and `rb/list_steps_e183_v3.sh`, the
   form of the dry listing v4. E185's kit note 4: the day-2 check v2, [`../e185/rb/check_day2_v2.py`](../e185/rb/check_day2_v2.py), one for
   the whole day, and its desk test. E183's runbook desk test v2 (`rb/selftest_rb_e183_v2.sh`, note 1), whose case C1 runs step 11 v2 end
   to end on a synthetic session: the run-time trace of E185's note 4 read every Python process it started.
3. **Not used.** Any change to a box file or a box step; any E183 datum (none exists); anything of the private tier.
4. **Tiers.** Public tier only. No private-tier check is used, so there is no sha256 line.
5. **Readiness.** This block is the note's own.

## The runbook as it now runs (note 2's table, with this note's changes)

| step | file | from this note |
|---|---|---|
| **0, before step 1** | **`/usr/bin/python3 -I -B tools/claims-v3/e185/rb/check_day2_v2.py tree --pull`** | **new:** the day-2 check v2 by hand (the brief's dated note 2, section 1) |
| 1, the window | `rb/s02_window_e183.sh <day> <last start> <last end>` | unchanged |
| 2, the desk check | **`rb/s03_desk_e183_v4.sh`** | **new:** the day-2 check v2 with its own pull, then step 2 v3 unchanged on the same tree (the check v1, then step 2 v2), then HEAD unchanged |
| 3-11 | as note 1's section 8 (step 11 is `rb/s22_collect_e183_v2.sh`) | unchanged |
| **after the data commit** | **`/usr/bin/python3 -I -B tools/claims-v3/e185/rb/check_day2_v2.py m1 e183 --data <E183's data dir>`** | **new:** v1's M1 gate with the check v2's tree check |

**Step 2 v3 is never run alone on E183's card day** (it runs inside v4), nor v2 or v1.

## Fault by fault

### verify-fx's minor fault 1, E183's side

E183's own steps load nothing outside the check v1's perimeter: the run-time trace of step 11 v2 (the copy-back check, the collector v2,
its pins check, the reduction v2 and the scorer), of step 2's harness check and of E183's M1 reader found every lab file they open or import
inside it (E185's kit note 4, "What this lane found"). The fault is the day's all the same: E183's step 2 runs on the lab clone E185's
collection and score read, and the check v1 is one for the whole day. So step 2 v4 runs the check v2 first, whose perimeter adds the 12
lists the day's scorer opens, the closure list of the 168 files E185's scorer and collector load outside v1's perimeter, and kit note 2's and
E185's kit note 3's lists (47 lists; 6 directories and 592 named files outside them). Desk cases: L3 (M11's imported
`hpl/surface_hpl.py` edited and committed): E183's step 2 v3 alone passed it (its check v1 read 0), step 2 v4 reads 16.

### verify-fx's minor fault 2, E183's side

The check v2 refuses an untracked module in any of the day's 156 directories (E185's kit note 4); an untracked file under `e183/` (a core
directory) of any kind still stops step 2 by v1's status read. Desk case W: a lane's working note left untracked under `e183/` makes E183's
step 2 v4 read 16, naming it (the brief's dated note 2: "writes or commits").

### The M1 reader's gate v2

`check_day2_v2.py m1 e183 --data <E183's data dir>` is v1's gate with the check v2's tree check: E183's seven M1 files unchanged since
`6860643c`, `SHA256SUMS-e183-m1` at 25 and its own sha256 `c8bad97187caf6f3...`, the data directory committed and clean, then note M1's own
run line (`/usr/bin/python3 -B tools/claims-v3/e183/arm_m1_read_e183.py --reduced <dir>/reduced-e183.json --scored <dir>/scored-e183.json
--out <dir>/arm-m1-e183`), its exit status printed, and only its two outputs written. A reader's refusal or non-zero exit is recorded,
never a block. Desk case R4: the gate v2 0 on a stand-in data directory holding no reduction, the reader's rc 1 printed, nothing written.

## What does not change

KIT.md and notes 1 and 2 and their files and lists; E183.md, its note 1 and its plans; note M1, its reader and its reading; the harness, the
build inputs and every step that reaches the box; the stops, the device commands, the budgets and the caps; the order with E185 (E183 only
after E185's step 14). The new files are new; v1's, v2's and v3's stay as committed.

## Files ([`SHA256SUMS-e183-kit-note3`](SHA256SUMS-e183-kit-note3), 19 entries)

This note; [CARD-LANE-BRIEF.md.dated-note-2.md](CARD-LANE-BRIEF.md.dated-note-2.md); [`rb/s03_desk_e183_v4.sh`](rb/s03_desk_e183_v4.sh)
and [`rb/list_steps_e183_v4.sh`](rb/list_steps_e183_v4.sh); the logs `logs/dry-listing-e183-v4.txt` and `logs/dmcmd-audit-note3-e183.txt`.
The list also pins E185's day-2 check v2, its closure list, its desk test and the test's log, and the unchanged files step 2 v4 runs or
names: `rb/s03_desk_e183_v3.sh`, E185's `rb/check_day2_v1.py`, `rb/s03_desk_e183_v2.sh`, `rb/rb_e183.sh`, `rb/s02_window_e183.sh`,
`rb/s22_collect_e183_v2.sh`, `SHA256SUMS-e183-kit-note2`, `SHA256SUMS-e183-brief` and the brief this note's brief note corrects,
`CARD-LANE-BRIEF.md`. It holds no file of note M1.

    bash tools/claims-v3/e183/rb/list_steps_e183_v4.sh <an empty scratch directory> > dry-listing-e183-v4.txt

## Labels

- **Registered:** every list, pin, step, gate, plan, cap and stop named here (E183.md with its note 1, KIT.md and its notes); this note's
  step 0, step 2 v4 and the M1 gate v2, before any datum.
- **Desk checks of code, not measurements:** every test result here.
- **Reported:** october-forecast-model's arms (note M1); their forecasts are blind for E183 (frozen before any datum).
- Nothing here is held out or post hoc.

SPDX-License-Identifier: Apache-2.0
