# E184's kit, dated note 4 (Sun 8 Nov 2026, week 45, written from 03:24 PST by the clock): step 11 v4 collects a session its smoke gate stopped - the session's own files first, then the pass directories that session's log says it made; step 2 v4 pins nine lists; written after both arms' data, it changes no rule, reader, forecast, band, plan, cap or stop

*Written on the Intel in Q156 (lane `fix-e184`), desk only: no card claimed, no device command sent, no lab box reached (every ssh and
rsync of the tests below is a stand-in that serves a local directory), nothing posted or deployed. New files only: the kit (`65f844be`) and
kit notes 1 (`eab0c70e`), 2 (`571511d0`) and 3 (`f9dcddac`) stay as committed, with every file their lists name (registration 11 of 11,
kit 44 of 44, A2 6 of 6, kit note 1 45 of 45, A3 3 of 3, kit note 2 20 of 20, A4 1 of 1, kit note 3 18 of 18 OK). It answers the data
verifier of E184's two arms (`verify-e184`, Sun 8 Nov 2026, 02:40-03:09 PST: holds with fixes, 3 minor and 4 nits), its **fault 3**: step 11
v3 cannot collect a session its smoke gate stopped. **It is written after E184's data** (arm B `8bf74b26`, 00:43:41 PST; arm S `f8d94224`,
02:36:34 PST). It changes only which directories step 11 copies, and in what order; the collector, the reducer, the scorer, every rule and
every reading are kit note 3's and A4's, unchanged. **No box file changes:** the harness's 59 files (`harness-e184-v2.json`) are kit note
1's, byte for byte.*

## Results first

| what was wrong | the fix | file | its test |
|---|---|---|---|
| Step 11 v3's first copy names the arm's three pass directories, `e184`, `e184-smoke` and `e184-stoptest`, and only the queue makes `e184`. On Sun 8 Nov arm S's smoke gate stopped its session (T0 1794133299, A3-1), so at 02:26:36 PST rsync exited 23 and the step stopped (14) before the session's own files, the collector and the gates. Those files are still on aifoundry3. | **Step 11 v4.** The session's own files (the box's `build/e184/`) come first, and this T0's log is checked there (v3's words, the same 14). Then the copy takes the pass directories **this T0's own log says the session made**. That is all three (v3's copy, unchanged) unless the log holds the session's gate-stop line: `smoke gate failed (stop test rc N, smoke rc N, gate N): no pass runs` gives `e184-smoke` and `e184-stoptest`; `stop-path test failed: no smoke, no pass` gives `e184-stoptest` alone. | `rb/s22_collect_e184_v4.sh` | desk test v4: **CG** (0; the copy holds the two directories and the session's files; the scored arm reads its session gate, every rule NOT SCORED); **CGv** (step 11 v3 on the same box: 14 at its first copy, the fault); **CGx** (another session's `e184` left on the box: not copied); **CGs** (a failed stop-path test: `e184-stoptest` alone); **CM** (a session that ran its queue, its `e184` missing on the box: 14 at the copy, as v3) |
| step 2 v3 pins eight lists, and this note adds one | **step 2 v4** pins nine: 11, 44, 6, 45, 3, 20, 1, 18 and this note's **10** | `rb/s03_desk_e184_v4.sh` | desk test v4 **K** (no window: 10, no call); the dry listing v4 |

**Everything else reads as before.** The desk test v4 runs v3's 38 cases with the v4 steps (C1-C8, C1b, C2, C2n, C2p, C2e, P1 and D1 through
step 11 v4; C2ev keeps step 11 v2), and each reads as in v3's committed log. The only differences are dates, T0 numbers, the scratch
repository's file count and the v4 names. With the five new cases: **SELFTEST-RB-E184-V4 PASS, 43 of 43**. The runbook's device-command
audit v4 is byte for byte v3's: GO, 23 send sites. Step 11 v4 sends no device command: it makes two rsync copies, then runs the desk collector.

## Builds on (the stock-take's rule for lanes, MAP section 3)

1. **Checked:** the stock-take's INVENTORY.md, read Sun 8 Nov 2026 at 03:33 PST (row H28, the kits' meter and stops; kit note 3's block
   also named H27). The ids are opaque pointers into a private inventory. Newer pieces are cited by commit.
2. **Used** (each unchanged, called or sourced by path; their sha256 in kit note 3's, kit note 2's or kit note 1's list):
   - **Kit note 3's runbook files** (`f9dcddac`): `rb/s22_collect_e184_v3.sh`, `rb/s03_desk_e184_v3.sh`, `rb/list_steps_e184_v3.sh`,
     `rb/selftest_rb_e184_v3.sh` and `audit_rb_e184_v3.sh`. Each v4 file is its predecessor with the stated changes (counted, exact
     replacements; each file's header lists them). Also `collect_e184_v3.sh`, which step 11 v4 calls unchanged. *Check:* v3's 38 desk
     cases re-run under the v4 steps and read as v3's committed log (`logs/selftest-rb-e184-v3.txt`).
   - **The session's own gate-stop lines,** as `session_e184s_v2.sh` and `session_e184b_v2.sh` write them (kit note 1; their lines 68 and
     78), unchanged. *Check:* arm S's session log of Sun 8 Nov, as step 10's wait printed it from the box, holds `smoke gate failed (stop
     test rc 0, smoke rc 0, gate 1): no pass runs` (`docs/reports/data/2026-11-08-e184-sensor-validation/README-arm-s.md`, box step 10).
     That is step 11 v4's pattern.
   - **`fake_card_e184_v2.py --smoke-fail`** (kit note 1), unchanged: the gate-stopped synthetic sessions. **k6's runbook drivers**
     through `rb/rb_e184.sh`, unchanged.
3. **Not used:** rsync's `--ignore-missing-args`, the verifier's example. Beside a gate-stopped session it would copy another session's
   `e184` from the box. And it would let a session that ran its queue pass the copy with its `e184` missing. The log-driven copy does
   neither (CGx, CM).
4. **Tiers:** every file here is public tier and cites public pieces only. No NDA-tier check enters this note.
5. **Readiness:** this block is the note's. A verifier checks it against INVENTORY.md and the cited commits.

## 1. Step 11 v4

`rb/s22_collect_e184_v4.sh S|B` is v3 with two changes.
1. **The order.** The box's `build/e184/` (the operand images left out) is copied to `build/e184-raw/<card>/logs/` first, and the step stops
   (14, v3's words) unless the copy holds `session-<arm>-t<T0>.log` for the T0 step 9 recorded. v3 made the same check after both copies.
2. **The pass directories.** They are read from that log: three, as v3, by default. With `stop-path test failed: no smoke, no pass` the copy
   is `e184-stoptest`. With `smoke gate failed (stop test rc N, smoke rc N, gate N): no pass runs` it is `e184-smoke` and `e184-stoptest`.
   The step says which. The patterns are the session file's own words, anchored at the line's end.

Then come v3's stop-path no-launch check, the collector (`collect_e184_v3.sh`: reduce v4 with A4, score v3), its success line, the
desk-path gate and the login check, last, all unchanged. A gate-stopped session's log has no "smoke gate passed" line, so the reducer's
session gate reads every rule of the arm NOT SCORED. That is A3-1's "E184 arm S not run", never a verdict; the step says so. A session that
ran its queue is copied exactly as v3 copies it, and a missing pass directory still stops the copy (CM).

**Limits, stated.** Like v3, the copy takes what the named directories hold on the box. A gate-stopped session's `e184-smoke` and
`e184-stoptest` are its own only if no earlier session's pass directories sit there. On Sun 8 Nov they were that session's alone: arm S's
first session on aifoundry3. And `lib.sh` (its line 181) skips a pass that already holds `block.json` unless V3_FORCE is set. So, as
README-arm-s.md and the verifier say, any later arm S session first needs that day's `e184-smoke/p18401` and `e184-stoptest/p18402` moved
aside on the box. That is a box step, for a later dated note.

## 2. Step 2 v4

`rb/s03_desk_e184_v4.sh` is v3 with `SHA256SUMS-e184-kit-note4:10` added to its pinned lists, so it checks nine. Like v3, it refuses (10)
unless step 1 wrote this RB_OUT's window today.

## 3. The runbook as it now runs (it governs E184's steps)

Kit note 3 section 3's table, with **steps 2 and 11 in v4**. Every other step, file and rule is kit note 3's (and kit note 2's).

| KIT.md box step | file |
|---|---|
| 1, his go and the window | `rb/s02_window_e184.sh <day> <last start> <last end>` (one `RB_OUT` per arm), **first** |
| 2, the desk check | **`rb/s03_desk_e184_v4.sh`**: the nine lists at their pins (11, 44, 6, 45, 3, 20, 1, 18, 10); it refuses (10) without step 1's window of today |
| 4, look first; 3, then the day's one post | as kit note 3 |
| 5-10, 10b | as kit note 3 (`s07`, `s08`, `s09_reads_e184_v2`, `s10`, `s11`, `s20`, then `s09_reads_e184_v2 ... after`) |
| 11, release, then collect | the post's release; then **`rb/s22_collect_e184_v4.sh S|B`**: the session's own files, then the pass directories its log names, then `collect_e184_v3.sh` (reduce v4 with A4, score v3); then the data directory `docs/reports/data/<day>-e184-sensor-validation/` and a data verifier |

**Arm S's session of Sun 8 Nov (T0 1794133299), whose own files are still on aifoundry3** in our tree's `build/e184/` (README-arm-s.md lists
them), can be collected by this note's steps on that same day. It uses the day's arm-S RB_OUT, which holds `t0-S.txt`, the look's own-login
record and the window step 1 wrote at 00:01:55 PST. The steps are step 2 v4, then step 11 v4. Neither reads a card or sends a device
command. It needs aifoundry3's Tailscale approval of that night (to about 09:30 PST) and runs only on the Pacific date of the window (step
2's check).

Its output directory, `build/e184-out/2026-11-08-e184-sensor-validation/`, also holds arm B's collection. So the collector re-reduces arm B
from its kept copy with its kept T0, and scores both arms. The verifier's desk check S4 found arm B's reduced file the same byte for byte
and its scored section equal. The lane that commits it adds its files beside `f8d94224`'s under names that do not collide with arm B's
committed `scored-e184-v3.*` and `reduced-e184b-v4.json`. It adds them with their own hash list and a dated note beside `README-arm-s.md`,
after a data verifier, and never edits a committed file.

## 4. The runbook's desk test v4

`rb/selftest_rb_e184_v4.sh <scratch dir>` (its header lists the cases): v3's 38 cases with the v4 steps, then five new ones, each staged on
the stand-in aifoundry3 from `fake_card_e184_v2.py --smoke-fail` (seed 11) as the box leaves a gate-stopped session (no `e184`; the stop-path
test's no runs file; the session's logs and config reads):

| case | staged | step 11 | reads |
|---|---|---|---|
| CG | the log's `smoke gate failed (...): no pass runs`; `e184-smoke`, `e184-stoptest` | v4 | **0**; the copy holds `e184-smoke`, `e184-stoptest` and the session's log; the scored arm S: gate false, its reasons name the missing "smoke gate passed" line, every rule NOT SCORED |
| CGv | the same | **v3** | **14** at its first copy ("the copy back exited non-zero"); the session's files not copied: Sun 8 Nov's fault |
| CGx | CG plus another session's `e184` on the box | v4 | **0**; that `e184` is not copied; the same scores as CG |
| CGs | the log's `stop-path test failed: no smoke, no pass`; `e184-stoptest` alone | v4 | **0**; the copy holds `e184-stoptest` and the log; every rule NOT SCORED |
| CM | a session that ran its queue (`smoke gate passed`), its `e184` removed from the box | v4 | **14** at the copy, as v3 |

## 5. The checks (each run by this lane; the logs are this commit's)

| check | result | log |
|---|---|---|
| the runbook's desk test v4 | **SELFTEST-RB-E184-V4 PASS, 43 of 43** (103 s; v3's 38 as in its committed log, and CG, CGv, CGx, CGs, CM) | `logs/selftest-rb-e184-v4.txt` |
| the runbook's dry listing v4 | 0 exited non-zero, no ssh or rsync; step 2 v4 listed once, step 11 v4 once an arm (the session's files first, then the pass copy) | `logs/dry-listing-e184-v4.txt` |
| dmcmd_audit | runbook v4 **GO, 23 sites**, byte for byte kit note 3's log (the four v4 files send nothing) | `logs/dmcmd-audit-rb-v4.txt` |
| the hash lists, the harness, the plan | the eight lists at step 2 v3's pins; the box list CHECK PASS; HARNESS OK 59; the plan IDENTICAL; no committed E184 file changed since `f9dcddac`; two commits name E184 data (`8bf74b26`, `f8d94224`), which this note follows | `logs/reruns-note4.txt` |

Step 2 v4 is run for real on the committed tree after this commit: it needs E184's paths clean and this note's list committed.

## 6. Kit note 4's files (their sha256 in [`SHA256SUMS-e184-kit-note4`](SHA256SUMS-e184-kit-note4), 10)

| file | what | from |
|---|---|---|
| `KIT.md.dated-note-4.md` | this note | |
| `rb/s22_collect_e184_v4.sh` | step 11 v4: the session's own files first, then the pass directories its log names | `rb/s22_collect_e184_v3.sh` |
| `rb/s03_desk_e184_v4.sh` | step 2 v4: nine lists pinned | `rb/s03_desk_e184_v3.sh` |
| `rb/list_steps_e184_v4.sh`, `rb/selftest_rb_e184_v4.sh` | the dry listing and the runbook's desk test | v3's |
| `audit_rb_e184_v4.sh` | the runbook's device-command audit | v3's |
| `logs/` (4 files) | the checks above | |

## 7. Open items (for the verifier, the readiness critic and the records)

1. **No verifier has read this note.** It came from the data verifier's fault 3, and was written after the data.
2. **Arm S's session files on aifoundry3** are collected only if a lane runs section 3's two steps on Sun 8 Nov while the approval lasts.
   Otherwise they wait on the box; a collection on a later day needs a window written that day, and a dated note naming the departure.
3. Kit note 3's limits stand: A3-1's censoring of E184-P's high side above a gain of about 1.6; the one-shire calibration effect; the
   rail rarely separates the meter from the power (A2-3).
4. **Before any re-run of arm S,** as dated notes first (the data verifier's fault 2; `README-arm-s.md.dated-note-1.md` gives the figures):
   - the smoke gate read with A2-5's refresh rule (a box-file change: `check_e184_v2.py` is a harness file), or the dip risk accepted in
     words at its rate;
   - that day's `e184-smoke/p18401` and `e184-stoptest/p18402` moved aside on the box;
   - his go, with a window that fits 8,100 s.

## Labels

- **Registered:** nothing new. The pins, the plan, the caps and the stops are unchanged.
- **Desk checks of code, not measurements:** every test result here.
- **Written after the data:** this note and its code (both arms' data were committed before it). It changes no reading: arm S has no rule
  with a reading (A3-1), and arm B's files are as committed.

## Compute

All on the Intel, desk only, through the round's local slot (`slot.sh`), one job at a time at nice 10, one core: the runbook's desk test v4
(103 s), the dry listing, the audit and the re-runs (5 s). No lab box, card, mini or network call.

SPDX-License-Identifier: Apache-2.0
