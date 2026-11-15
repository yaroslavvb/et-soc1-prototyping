# E190's kit, dated note 2, after E190's first card day and before any later E190 day: step 10 v3 (the wait no longer reads the identity gate's pass line as a gate stop), its two desk tests, step 2 v3 and the dry listing v3; the READING RULE retired (Q177, lane note2-e190; new files only)

*Sat 14 Nov 2026 (week 46), PST, on aifoundry2, desk only (Q177, lane `note2-e190`; written between 14:42 and 15:40 PST by the clock; its
commit's own time is git's). No card was claimed or opened, no device command was sent, no lab box was reached and nothing was posted: the
tests read text files through the real step scripts, with a stand-in ssh serving two stand-in boxes under a scratch directory, inside a
sandbox with no /dev/et* and an empty /run/lock, in a private PID namespace. It answers the one MAJOR desk-side finding of E190's
readiness check (`ready-e190`, Fri 13 Nov 2026, 15:10-15:58 PST): **step 10 v2 (`rb/s20_wait_e190_v2.sh`, line 38) reads every session
that passed its identity gate as GATE-STOPPED (exit 16), running or ended.** E190's first card day (Fri 13 Nov 2026, both arms, data
commit `a6fafba4`) met it on all five step-10 calls and read them by the go lines' READING RULE, stated before the launches (that data
directory's README, departure 3). The registration (`508d48d9`), the kit (`241726bd`) and note 1 (`bff31df2`) stay as committed: every
file of theirs is unchanged, and note 2 adds a `_v3` file beside each one it replaces. **Nothing here changes a forecast, a band, a rule,
a threshold, the order, the card time, the cap, a stop, the runner, the session, the scorer, or any datum or reading of E190's first day.**
It is written after that day's data and touches only how the runbook's wait reads a session log; the day's five step-10 readings stand as
its README records them, and step 10 v3 reproduces them (section 3).*

## Results first (desk checks of code; nothing is measured)

| check | result | log |
|---|---|---|
| **step 10 v3's text** against v2 and the kit's v1 (case D) | outside its comment lines v3 differs from v2 in exactly two lines: `rb_init s20_wait_v3` (the step's name in RB_OUT's log) and the GATE-STOPPED pattern without `\|the card.s identity: \|the identity read \(`; that pattern is the kit's v1 pattern (`rb/s20_wait_e190.sh` line 37) byte for byte | [`logs/selftest-wait-e190-v3.txt`](logs/selftest-wait-e190-v3.txt) |
| **ready-e190's W1-W4**, on the real path's own session logs as note 1 committed them (`logs/realpath-e190-v2.txt`: RA1, RB2, RB1) | **v3 0 / 17 / 16 / 0** (W1 arm A ended; W2 arm A running; W3 arm B's identity gate on card 0's config; W4 arm B ended); v2 16 / 16 / 16 / 16, as ready-e190 found | the same |
| v2's other readings, kept (W5-W9) | RUN-GONE 14; MANIFEST-ABSENT 14; RUN-UNKNOWN 10 (the box's T0 not RB_OUT's; not written today); a stand-in under the v1 name `session_e190.sh` not counted, 14: **v3 = v2 in each** | the same |
| **the 12 real-path sessions** of that log, each ended with a manifest (X1-X12) | v3 16 for exactly the **8** the runner itself ended rc 16 (the gates), 0 for its **4** rc-0 sessions; v2 16 for all 12 | the same |
| | **SELFTEST-WAIT-E190-V3 23 of 23 PASS** | the same |
| **card-e190's five step-10 calls** on E190's committed card-day logs (R1-R5: each arm's `session.log` cut at that call's time from the README's departure 3; the session running where it ran; the committed `MANIFEST.sha256`, 212 lines, where it had ended) | **v3 17, 17, 0, 17, 0** (A running, B running, A ended, B running, B ended); v2 16 on all five, as card-e190 met; v3 prints the same session lines as v2 (35, 33, 40, 40, 40) and no GATE-STOPPED | [`logs/realread-wait-e190-v3.txt`](logs/realread-wait-e190-v3.txt) |
| each arm cut just after its start config line, the session running (R6, R7) | v3 17 (v2 16) | the same |
| **a real gate-stop line written as a test input** at its place in an arm's real log, then the runner's closing lines (G1-G11), and G1's input before its session end with the session running (G12) | **v3 16 in all 12** (v2 16) | the same |
| a stop tripped in the runs (T1 the identity stop, I7's words; T2 a board line, S1's: the runner itself ends rc 0) | v3 0, ended, with the `STOP:` line among the lines it prints (v2 16) | the same |
| the patterns over every line, by `grep -E` (P1-P3) | both card-day logs (100 lines): v3 0 hits, v2 2 (each arm's start config line); the 12 real-path sessions: v3 exactly the 8 rc-16 ones, v2 all 12; the gate lines of G1-G11: v3 11 of 11; the STOP lines of T1-T2: v3 0 of 4 | the same |
| | **REALREAD-WAIT-E190-V3 25 of 25 PASS** | the same |
| the dry listing v3 (`rb/list_steps_e190_v3.sh`, note 1's sample window) | **23 steps, 0 exited non-zero, 0 box calls** | [`logs/dry-listing-e190-v3.txt`](logs/dry-listing-e190-v3.txt) |

Beside the committed tests, a desk read of the round's own records: R1-R5's step 10 v2 output reproduced card-e190's five captured calls of
Fri 13 Nov 2026 line for line (the same 35, 33, 40, 40 and 40 session lines, the same RUN-, MANIFEST- and GATE-STOPPED lines, the box's date
and the loop's seconds aside), and step 10 v3 on the same inputs drops only the GATE-STOPPED line. Those captures are kept with the round's
records, not in this repository.

## 1. The fault

Line 38 of step 10 v2 prints `GATE-STOPPED` when the session log matches

`stop-path test failed|smoke gate failed|no device opened|the gate, no launch|would not start|the card.s identity: |the identity read \(`

Note 1 added the last two alternatives for its two new gates, but `the card.s identity: ` is also in the line every session prints when its
identity gate PASSES (`run_e190_v2.py` line 779: `config start: {...} (read, nothing set); the card's identity: PCIe target /dev/et0_mgmt,
physical device ID 0`, and on arm B `/dev/et1_mgmt, physical device ID 1, minion_mv <n> below 510`). The pattern is read whether the session
has ended or not, and step 10 reads `GATE-STOPPED` (16) before `RUN-ENDED` (0) and before "still runs" (17), so every session that got past
its start config was a "gate stop", at every call. The second alternative, `the identity read \(`, matches only the identity read's failure
line (line 794); the pass line (796) reads `the identity read: et-who ...`. Both failure lines it was meant for (777 and 794) end
`: the gate, no launch`, which the pattern already held. No desk test of note 1 gave step 10 v2 a session that passed its identity gate (the
runbook test's real session stopped at its box check; its WV/WG log had no identity line); ready-e190's dry-vs-real audit found it.

## 2. What v3 changes, and why its pattern still catches every gate stop

`rb/s20_wait_e190_v3.sh` is v2 with its header comment rewritten, its step name `s20_wait_v3`, and line 38's pattern without the two
alternatives (its line 44): `stop-path test failed|smoke gate failed|no device opened|the gate, no launch|would not start`, the kit's own
pattern again. Everything else is v2's in v2's order: the T0 file read today, the session counted by its own script name
`session_e190_v2.sh` (E190's `ours_live`), the bounded remote loop, the session lines printed (identity among them), RUN-ENDED with the
manifest's count, RUN-RUNNING, and on the desk RUN-UNKNOWN (10), a failed call (14), RUN-GONE (14), MANIFEST-ABSENT (14), GATE-STOPPED (16),
ended (0), else 17.

The runner (`run_e190_v2.py`, note 1's) ends a session at a gate in eleven places; each prints one line, and each line holds one of the five
phrases (a desk read of code: no other line the runner writes to the session log holds any of them, and none of the reasons it fills
into its other lines does):

| the gate | `run_e190_v2.py` line | the phrase that catches it | the cases |
|---|---|---|---|
| the box or the build not the registered one | 740 | `no device opened` | X5 (RA5), X6 (RB0), X11 (RB5); G6 |
| no card lock on the box | 746 | `no device opened` | G7 (the runner's words) |
| the card's lock cannot be opened | 751 | `no device opened` | G8 (the runner's words) |
| the card's lock is held | 756 | `no device opened` | X2 (RA2); G4 |
| a holder or a device process | 762 | `no device opened` | X4 (RA4); G5 |
| the start config not the registered one | 768 | `the gate, no launch` | G9 (the runner's words) |
| the start config's identity (note 1) | 777 | `the gate, no launch` | W3 and X8 (RB2); G1 (made by `e190_note1.config_identity` from aifoundry2's committed start config read and its stderr, read as arm B) |
| the sampler would not start | 783 | `would not start` | G10 (the runner's words) |
| the stop-path test failed | 787 | `stop-path test failed` | G11 (the runner's words) |
| the identity read (note 1) | 794 | `the gate, no launch` | X9 (RB3); G2 |
| the smoke gate (the host's card among its checks) | 800 | `smoke gate failed` | X10 (RB4); G3 |

Six of the eleven lines are the real path's own (the runner without `--dry`, as note 1's real-path test committed them); the other five no
real-path session printed, so they are written in the runner's words from its source.

## 3. What step 10 v3 reads (for every later E190 day)

| exit | it means | then |
|---|---|---|
| 0 | the session ended and its `MANIFEST.sha256` is written | step 11 v2. **Read the printed lines first**: a session whose runs were ended by a stop line, two failed processes or the identity stop also ends rc 0 in the runner (S1-S3 and S5, H2 and I7 in `logs/selftest-run-e190-v2.txt`) and is 0 here, with its `STOP: ...: nothing further started` line among the lines printed; an identity stop is handled as `CARD-LANE-BRIEF.md.dated-note-1.md` section 5 says (report it with `identity.json`; never re-run around it that day) |
| 16 | a gate stop: one of the eleven lines above, ended or still closing | step 11 v2 still collects it; never re-run around a gate that day |
| 17 | the session still runs | call step 10 v3 again |
| 14 | RUN-GONE (no session process and no session end), MANIFEST-ABSENT, or the call failed | as the kit: read the box (read-only) first |
| 10 | RUN-UNKNOWN (the box's T0 not written today, or not this RB_OUT's) | as the kit |

v2's 16 on a session whose runs were stopped was the defect, not a reading: v2 read every session that passed its identity gate as 16,
including all four rc-0 sessions of the real-path test and both of E190's real sessions.

**The READING RULE is retired.** On Fri 13 Nov 2026 the card lane read step 10 v2 by the rule ready-e190's go lines stated before the
launches ("RUN-RUNNING" means call again; "RUN-ENDED" with "MANIFEST-WRITTEN" means ended, and a gate stop only if a printed session line
holds one of five phrases). Step 10 v3 is that rule made code: its pattern is those five phrases, and on E190's five real calls the two read
the same (R1-R5: running, running, ended, running, ended). For every later E190 day **step 10 is v3**, read by its exit as above; never
step 10 v2 or v1, and never the READING RULE in its place.

## 4. Step 2 v3 and the pins

Step 2 v2 pins note 1's list (`SHA256SUMS-e190-kit-note1`, 38 entries) by count and bytes, and that list names step 10 v2; a step 10 v3 read
under step 2 v2 alone would be reported, never gated. So note 2 adds its own list, **`SHA256SUMS-e190-kit-note2`** (8 entries: every file of
this note but the list itself and step 2 v3), and **step 2 v3** (`rb/s03_desk_e190_v3.sh`, outside the list), which runs step 2 v2 unchanged
and then, on the same HEAD (the one step 2 v2's last line names): note 2's commit found by its content (the commit that added
`KIT.md.dated-note-2.md`) an ancestor of HEAD; note 2's list at its pinned count and its own pinned sha256 (`NOTE2PIN`), every entry OK;
note 2's two desk tests' logs and the dry listing v3's last line as committed; HEAD unchanged to the end. Its exits are k6's (0, 10, 16;
step 2 v2's own pass through), and like v2 it is never run inside the lab-git lock. By its code step 2 v2 alone also passes on a HEAD that
holds note 2 (it reports note 2's list as one it does not pin, and the history check reads note 2's files as additions under
`tools/claims-v3/e190`); the land record reads both steps for real.

The anchor lines a later E190 day's step 0 carries gain note 2's: its commit an ancestor of HEAD; `SHA256SUMS-e190-kit-note2` at its 8
entries, its own sha256 and every entry OK; step 2 v3 at its own sha256 with its `NOTE2PIN` line. Their values are in the land record (a
note cannot hold its own list's sha256). Note 1's anchor lines stand beside them, except the line that read "no E190 datum in any ref":
E190's first day's data (`a6fafba4`) and any dated notes beside it are in the history now, and step 2 v2 reports them ("commits naming E190
data").

## 5. The runbook for a later E190 day

`CARD-LANE-BRIEF.md.dated-note-1.md` stays the card lane's brief, with two rows of its section 1 replaced:

| # | the step | what to do with its exit |
|---|---|---|
| 2 | **`rb/s03_desk_e190_v3.sh`** with `RB_GITLOCK` set, never inside the lab-git lock | anything but 0: no box step that day (a 16 naming HEAD-moved: a co-owner committed meanwhile, run it again) |
| 10 | per arm **`rb/s20_wait_e190_v3.sh <A\|B>`**, again while it says 17 | section 3 above |

Steps 1, 12 and 13 stay the kit's; steps 5, 6, 8, 9 and 11 stay note 1's v2; step 4 is k6's look; `rb/s25_report_e190_n1.sh` follows step
13. The lines its section 5 names are read in step 10 v3's output the same way. `rb/list_steps_e190_v3.sh` prints every step's commands
(the dry listing v3, 23 steps). **Never on a later E190 day:** step 2 v2 or v1 alone, step 10 v2 or v1, or any step the brief's section 7
already rules out. What a later day also needs (its go, the post or its waiver, the window, the bookings, the hold, the quiet desk, a new
RB_OUT and data directory) is the card lane's and its go lines', not this note's.

## 6. The files (all new, under tools/claims-v3/e190/)

| file | what | replaces, for a later E190 day |
|---|---|---|
| `rb/s20_wait_e190_v3.sh` | step 10 v3 | `rb/s20_wait_e190_v2.sh` (and the kit's v1) |
| `rb/s03_desk_e190_v3.sh` (outside the list) | step 2 v3: step 2 v2, then note 2's commit, list and logs | `rb/s03_desk_e190_v2.sh` as the step to run |
| `rb/list_steps_e190_v3.sh` | the dry listing v3 (steps 2 and 10 as v3; the post lines read "the owner's call for that day") | `rb/list_steps_e190_v2.sh` |
| `rb/selftest_wait_e190_v3.py`, `rb/selftest_wait_e190_v3.sh` | the desk tests: `desk` (W1-W9, X1-X12, D) and `real` (R1-R7, G1-G12, T1-T2, P1-P3), each ending with Z (every stand-in call to a stand-in box; no stand-in left running) | (added) |
| `logs/selftest-wait-e190-v3.txt`, `logs/realread-wait-e190-v3.txt`, `logs/dry-listing-e190-v3.txt` | their logs | |
| this note | | |
| `SHA256SUMS-e190-kit-note2` | every file above but itself and step 2 v3 | |

## 7. What the tests do not show

The stand-in boxes run on the desk, so the remote script ran with this desk's bash, pgrep and date, as on arm A's box (the same machine) but
not on aifoundry1's; the stand-in session is a script that only sleeps, counted by the same `ours_live` by its name (on Fri 13 Nov 2026 that
same count, v2's, which v3 keeps, saw the real sessions run on both boxes: card-e190's three RUNNING calls); and the remote loop's bound was
6 s (`RB_WAIT_LOOP_S=6`; the card day's is 520 s), so a call on a running session read RUNNING after one 15 s sleep. Step 10 v3 has not yet
run against a real box: its first call is a later E190 day's. Step 2 v3 has no committed desk test of its own; the land record reads it for
real at the land commit.

## 8. Labels

Registered: nothing new; the rules, stops and plan named are E190.md's. **Desk checks of code:** every test result above. **Desk reads of
committed records:** E190's card-day session logs, manifests, start config read and README (`a6fafba4`), note 1's real-path and runner test
logs (`bff31df2`). A desk read of the round's own records: the comparison with card-e190's captures. Nothing here is measured, blind or held
out; no forecast, band or scored number is touched, and no E190 datum is read for a value. Python: `/usr/bin/python3` 3.12.3.

## Compute

On aifoundry2 through the round's local slots (`slot.sh`, nice 10), inside the sandbox (W/nodev.sh) and the test's own private PID
namespace, one job at a time: the `desk` test about 2 minutes, the `real` test about 4 minutes, the dry listing about a second. No other box.

SPDX-License-Identifier: Apache-2.0
