# E191's kit, dated note 3 (Sun 15 Nov 2026, after E191's second session's data and scores and before any datum of a third session): the third session's runbook for E191.md's dated amendment A2 (a REPEAT, REPORTED, on Mon 16 Nov 2026 or a later day): step 2 v3, step 9 v3, step 11 v3 and step 13 v3 with the repeat reading, the dry listing v3, the runbook desk test v3 and the quick set v3; no rule, forecast, threshold, plan, cap, stop, box file or reading changes

*Beside [KIT.md](KIT.md) (`eb1ac923`) and [its dated note 2](KIT.md.dated-note-2.md) (`2d0fe517`); it edits nothing there, nor in
[E191.md](E191.md), its dated note 1, [A1](E191.md.dated-amendment-A1.md) or either earlier record. Written on aifoundry2, desk only, by the
lane `a2-e191`: begun in Q190 at about 17:26 PST Sun 15 Nov 2026, cut off at about 18:05 PST when the round's agents stopped at the
session's weekly usage limit (nothing in the work was at fault), and finished in Q191 from about 21:45 PST, by the clock; its commit's own
time is git's. **Written after E189's data commit `fa9098c4` (Sat 14 Nov 2026, 20:34:12 PST), after E191's second session's data commit
`7156ac15` (Sun 15 Nov 2026, 14:32:17 PST) with its data note 1 `aaf70691` (17:11:50 PST), and after the scores commit `f74c81e3` (17:37:11
PST: the frozen scorer's outputs on both records, committed beside them)**, so by E191's dated note 1 section 3 it registers only the kit's mechanics and gates made stricter
for safety, each named so in section 5; **nothing here changes a forecast, a band, a rule, a threshold, K, the order, the plan, the card time,
the cap, a registered stop line, a box file or the scorer**, and nothing here reads E189's or E191's measured numbers for any of them. It
carries out [E191.md's dated amendment A2](E191.md.dated-amendment-A2.md), committed with it; the card lane's brief's dated note 2
([`CARD-LANE-BRIEF.md.dated-note-2.md`](CARD-LANE-BRIEF.md.dated-note-2.md)) carries both out. No card was claimed, no device command was
sent, no lab box was reached, nothing was posted; every desk test that ran a runner, a stand-in session or a stand-in box ran in the round's
CPU slot and a sandbox with no `/dev/et*` and an empty `/run/lock` (the runbook test also in a private PID namespace), while THE QUIET DESK
FLAG for aifoundry2's card was absent. New files only, all under `tools/claims-v3/e191/`.*

## Results first (desk checks of code on committed records; nothing is measured)

Every test below ran on aifoundry2 (Linux, `/usr/bin/python3` 3.12.3, g++-13 13.3.0, bubblewrap) on Sun 15 Nov 2026 between 21:55 and 21:58
PST, in the lane's scratch clone at `b7af9be54992` (GitHub main then: the scores commit `f74c81e3` and E188's data note 1 on top of
`15cb0fcb`, where Q190's first runs had read 18 of 18 before B7v3 was added, 12 steps in the Sunday form the listing no longer allows, 8 of
8 and 13 of 13) with this note's files. **Q190's "rc 1" for the quick set** was the lane's
wrapper, not the quick set: its first run (18:03:56-18:04:15 PST at `15cb0fcb`) read 13 of 13, rc 0, and the wrapper then ended with a
`grep -c` of home paths in that log, which counts 0 lines and exits 1; the wrapper now exits with the quick set's own rc.

| check | result | log |
|---|---|---|
| **the runbook, v3** (`rb/selftest_rb_e191_v3.sh` under `rb/selftest_rb_e191_v3_ns.sh`, 21:55:30-21:57:25 PST): the third session's whole order on a stand-in aifoundry1 left as the second session left it (both earlier records committed in the scratch, their session directories on the stand-in box, its T0 file the second session's): A3, P1v3, P2v3/H6v3/H7v3, N1v3/N2v3, F2, S5v3, B6v3 (the build's own day), **B7v3 (a later day, A2-5: the stand-in box's build a day old; step 6's wait alone refused, 10; its start and its wait 0 with that day's records)**, G1v3/D3, G2v3, LL3a (THE LAST LAUNCH with v2's reference, the first session's T0, and with another: both refused), RS3 (the rest rule on the second session's own log), LA3 (the REAL session v2 stopping at its box check), LL3b, G4a3/G4b3 (the relaunch rule), C3v3/C5v3 (the second session's T0 and an `-s3` of another day refused), C2v3/C4v3, SC0v3/SC3v3/SC4v3 (the registered verdicts re-derived at `23484c4f...`; a changed byte in the second record refused), Z | **SELFTEST-RB-E191-V3 19 of 19 PASS** | [`logs/selftest-rb-e191-v3.txt`](logs/selftest-rb-e191-v3.txt) |
| the dry listing v3, every step of the third session with stand-ins (Mon 16 Nov 2026, a sample window; step 6's start listed) | **13 steps, 0 exiting non-zero, 0 box calls**; a sample day of Sun 15 Nov 2026 **REFUSED (2)**; the command lines pass note 1's item 4 (`desk/drylisting_check_e191_v2.py`: 2 device-opening lines, each with `ET_DEVICES=1`) | [`logs/dry-listing-e191-v3.txt`](logs/dry-listing-e191-v3.txt) |
| **the repeat reading's self-test** (`repeat_e191.py --selftest` on the frozen scorer's output for the committed second record, sha256 `23484c4f...`, byte for byte the record's committed `scores-e191.json` of `f74c81e3`): RS1 the record beside itself (60 differences, all zero), RS2 known moves read back exactly while the registered S1T stays the second session's, RS3 NO DATA in one configuration, RS4-RS5 inputs not of the scorer's form refused, RS6 no "verdict" key on the third session's side, RS7 the text's last line, RS8 the spreads | **REPEAT-E191 SELFTEST 8 of 8 PASS** | [`logs/repeat-selftest-e191.txt`](logs/repeat-selftest-e191.txt) |
| **the quick set v3** (`desk/checks_e191_v3.sh`, re-run after this note's text was final; its log names the run): every .py compiles and every .sh parses; `V3-FROM-V2 SAME` (7 and 5 exact replacements); step 2 v3's pinned lists, 14 of its 16 (note 3's and A2's pin this log), each at its count and bytes with every entry OK; the shared names; the second record's lists (257 of 257, 7 of 7); the registered verdicts re-derived (`23484c4f...`: FAIL, PASS, FAIL, FAIL); the repeat self-test (8 of 8); the preflight v2 GO (16 send sites, 0 disallowed); the dry listing v3's command lines; no new file shadows a module; the never-run check (a) in A2's form at `b7af9be5`: NEVER RAN (no E194 folder in the tree then) | **CHECKS-E191-V3 13 of 13 PASS** | [`logs/checks-e191-v3.txt`](logs/checks-e191-v3.txt) |

## 1. What refuses a third session in kit note 2's runbook

1. **Step 2 v2's never-run check (a)** runs `workloads/ledger/spp_never_ran.py` with only Q166's progs folder and E189's data folder left
   out. The second record names the instance (its README, its sparse-parity passes and smoke run), so at GitHub main `15cb0fcb` it reads
   **NAMED BEFORE** (23 files, inside E191's records; the lane's probe, 17:31-17:34 PST); with both E191 records left out it reads **NEVER
   RAN** (no other committed file names the instance's n, eta or m).
2. **Step 2 v2's never-run check (c)** allows E191 data in a ref only inside the first record: the second record refuses it.
3. **Step 9 v2's THE LAST LAUNCH** expects, when RB_OUT holds no T0, the box's last E191 launch to be the first session's T0 1794766494; the
   box's `build/q141k/e191.T0` now reads the second session's, 1794780355, so every fresh RB_OUT is refused (10).
4. **Steps 11 v2 and 13 v2** name the `...-c1-s2` directory, which exists.

## 2. The new files, one row each

| file | what it is | how it differs from v2 |
|---|---|---|
| `rb/s03_desk_e191_v3.sh` (**step 2 v3**) | the desk check before any box step | v2 with: **(a) in A2's form** (both earlier E191 records and E194's committed folders of the exact form `docs/reports/data/<day>-e194-blind-day-aifoundry2` left out, each named in the output and the runbook log); **(c) in A2's form** (E191 data in a ref only in the first record, no pass in it, and the second record, which must be there; anything else, an `-s3` of any day among it, refuses); HEAD descends from the second session's data commit (found by content); four more lists pinned (the second record's `SHA256SUMS`, 257, and `SHA256SUMS-note1`, 7; note 3's and A2's lists); note 3's desk-test logs as committed. In no list: the go's anchor lines give its sha256 |
| `rb/s11_a1_session_e191_v3.sh` (**step 9 v3**) | the launch of session v2 | v2 with seven exact replacements: the header, the step's name, **THE LAST LAUNCH's reference with no T0 in RB_OUT: the second session's T0 1794780355** and its words, the refusal's words (A2's third session is E191's last), the LAUNCHED line and the last line naming A2's third session |
| `rb/s22_collect_e191_v3.sh` (**step 11 v3**) | the copy-back and the data directory | v2 with five exact replacements: the header, the step's name, the directory `...-c1-s3` with **two gates made stricter for safety** (RB_OUT's T0 must not be the first's or the second's; no `...-c1-s3` of any day may exist), the refusal's words, the last line |
| `desk/v3from_v2_e191.py` | the generator of steps 9 v3 and 11 v3 | `--check` rebuilds both from the committed v2 files and compares byte for byte (`V3-FROM-V2 SAME`) |
| `rb/s24_score_e191_v3.sh` (**step 13 v3**) | the scorer and the repeat reading, after the data commit | v2's checks on the `-s3` directory, the frozen scorer on it (`scores-e191-s3.json`, REPORTED); **the registered verdicts re-derived**: the second record clean and its `SHA256SUMS` OK, the frozen scorer on it (`scores-e191-s2.json`) at `23484c4f...` byte for byte, else 16 and nothing set beside it; then `repeat_e191.py` (`repeat-e191-s3.json`, `repeat-e191-s3.txt`); exits 0 whatever the words |
| `repeat_e191.py` | the repeat reading (A2-1) | new (section 3) |
| `rb/list_steps_e191_v3.sh` | the dry listing v3 | v2's form in the third session's order, the sample day Mon 16 Nov 2026 by default; step 6's start listed (A2-5: that day's own build); a sample day before Mon 16 Nov 2026 refused (2) |
| `rb/selftest_rb_e191_v3.sh`, `rb/selftest_rb_e191_v3_ns.sh` | the runbook desk test v3 | v2's form (its stand-ins unchanged), the cases of the table above, B7v3 (a later day's build) among them |
| `desk/checks_e191_v3.sh` | the quick set v3 | compile and parse; `V3-FROM-V2 SAME`; step 2 v3's pinned lists (all but note 3's and A2's, which pin this check's log) at their counts and bytes with every entry OK; the names the new steps share; the second record's two lists; the registered verdicts re-derived (`23484c4f...`, FAIL, PASS, FAIL, FAIL); the repeat self-test; the preflight v2 GO; the dry listing v3's command lines; no new file shadowing a module; the never-run check (a) in A2's form at the tree |

## 3. The repeat reading (`repeat_e191.py`)

It reads two outputs of the frozen scorer, unchanged (the second record's and the third's), and writes one JSON and one text. For each
configuration and each session: the passes scored; S1's, S1T's and S2T's errors and S2's ratio and band, as the frozen scorer computed them;
each error's sample standard deviation over the session's passes (S1's equals the scorer's own `e_j_over_pass_sd`: RS8); the measured means
(J over idle, J with the card at rest, t_k, T0). Then the third session minus the second: each error in percentage points, each measured mean as
a ratio, S1's and S1T's differences over sqrt(sd2^2/n2 + sd3^2/n3), and whether each configuration meets each rule in both. A configuration
with NO DATA in either session has no difference. The rules carry the second session's words as `registered_verdict` and the third session's
as `word` (REPORTED); no key on the third session's side names a verdict (RS6). The arms v2.1 and v2c are carried the same way. Standard
library only; it refuses (2) an input that is not the scorer's day output (RS4, RS5).

## 4. The runbook for the third session (E191.md's dated amendment A2)

Run from the lab clone, each step with a **new RB_OUT** (absent or empty before step 1; no earlier session's RB_OUT is ever reused), the one
`RB_LOCK` and, for step 2 v3, `RB_GITLOCK`. Exit codes are k6's.

| step | file | from this note |
|---|---|---|
| B | `W/book.sh take aifoundry1 <lane>`: its time is A2's **G3** | (the card lane's) |
| 0 | THE LOAD RULE; `check_day2_v2.py tree --pull` under the lab-git lock; the anchor lines of this note's land | unchanged, with this note's lines |
| H | `W/hold.sh add <lane>` | unchanged |
| 1 | `rb/s02_window_e191.sh <day> <G3+1:30> <G3+3:30>` (each rounded up; G3 at 20:29:00 or earlier that day) | unchanged; a new RB_OUT |
| 2 | **`rb/s03_desk_e191_v3.sh`** | **new** |
| 4, then 3 | the look; the post waived (his words, 10:22:36 PST) | unchanged |
| 5 | `rb/s07_a1_sync_e191_v2.sh` | kit note 2's |
| 6 | `rb/s08_a1_build_e191.sh start`, then `wait`: the third session's day builds its own (A2-5: Sunday's build is not that day's) | unchanged (B7v3) |
| 7 | `rb/s09_a1_reads_e191.sh`, **only after the rest has opened** | unchanged (its one re-run rule) |
| 8 | `rb/s10_a1_dry_e191_v2.sh start`, then `wait` | kit note 2's |
| 9 | **`rb/s11_a1_session_e191_v3.sh FULL`** | **new**: THE LAST LAUNCH's reference the second session's T0 |
| 10 | `rb/s20_wait_e191_v2.sh`, again while it says 17 | kit note 2's |
| 11 | **`rb/s22_collect_e191_v3.sh`** (no release: no post) | **new**: `docs/reports/data/<day>-e191-blind-day-aifoundry1-c1-s3/` |
| 12 | the README from `rb/data-readme-form-e191.md` for the `-s3` directory (the brief's note 2 names the differences), `rb/readme_check_e191.py`, the scan, the data commit | the form unchanged |
| 13 | **`rb/s24_score_e191_v3.sh`** | **new**: the repeat reading |
| E | `W/hold.sh remove <lane>`; `W/book.sh release aifoundry1 <lane>` | unchanged |

**Never run in the third session:** v1's or v2's step 2, 9, 11 or 13; runner v1 or session v1; a third build start the same day.

## 5. The readings stated here before any datum of a third session (each kit mechanics, or a gate made stricter for safety, named so)

- **The never-run check (a) in A2's form (kit mechanics):** it reads the record as it now stands: the registered sessions' folders (E189's,
  E191's two, E194's of its exact form) left out, and a run of the instance anywhere else refuses.
- **The never-run check (c) in A2's form (kit mechanics):** it reads the second record as what it is, a committed session; an `-s3` path
  before the third session refuses.
- **THE LAST LAUNCH's reference (kit mechanics):** the second session's T0, the box's last E191 launch; any other T0 still refuses.
- **Step 11 v3's two refusals (gates made stricter for safety):** never an earlier session's T0, never a second `-s3` directory.
- **Step 13 v3's re-derivation of the registered verdicts (a gate made stricter for safety):** the repeat is set only beside the verdicts
  at their committed bytes.
- **The repeat reading (A2-1's form; REPORTED):** its numbers decide nothing.
- **A2-5's build rule (kit mechanics, KIT.md 4 read as written):** a build stands only on its own day; on the third session's day step 6's
  start, then its wait (B7v3).
- Everything else is KIT.md section 4 and kit note 2, unchanged.

## 6. What does not change

E191.md, its dated note 1, A1 and every registered file, list and anchor; KIT.md and kit note 2 and every file of their lists (73 and 71
entries); the brief and its note 1; both earlier records. Every box file (harness v2's 49 files: runner v2, common v2, session v2, the doubles,
the preflights, the identity module, the guard, the build); the adapter, the reader, THE STOP LINES, the identity gate, the holder rule, the
30 s bound, the sampler's freshness, the early stop, the box check, THE KERNEL GATE, the rest rule, the collector, the reducer, the scorer, the
cap and the window rule; every device command (each a READ). Every new file is new; nothing committed is modified, renamed or removed. The new
Python files (`repeat_e191.py`, `desk/v3from_v2_e191.py`) shadow no module (the quick set).

## 7. What the desk cannot show

1. **The third session's own day:** the card, its die at the start, the real hosts' lines (kit note 2 section 11 stands; the second session
   read every one of its 31 host lines with one runtime line dropped each).
2. **A folder of E194's data in another form than its step 11's** (`<day>-e194-blind-day-aifoundry2`), or any other file that names the
   instance, would make step 2 v3 refuse (16): the safe direction; a dated note then names it.
3. **E194's own check against the `-s3` folder** (A2-6): E194's committed step 2 and the step 2 v2 of E194's amendment A1 leave out E191's
   `-c1` and `-c1-s2` only; this note cannot change E194's files; the order of the two days, or E194's own note, answers it.

## 8. Labels

- **Registered, after the second session's data and before any datum of a third session:** the files of section 2 and the readings of
  section 5. Not blind to the second session's data.
- **Desk checks of code, not measurements:** every test result here (`/usr/bin/python3` 3.12.3 on aifoundry2); the committed records the
  tests read (both earlier records, the frozen scorer's output on the second) are **desk reads of committed records**.
- Nothing here is measured, blind, held out or post hoc.

## 9. Files ([`SHA256SUMS-e191-kit-note3`](SHA256SUMS-e191-kit-note3))

This note, A2, the brief's dated note 2; the new runbook files `rb/s11_a1_session_e191_v3.sh`, `rb/s22_collect_e191_v3.sh`,
`rb/s24_score_e191_v3.sh`, `rb/list_steps_e191_v3.sh`, `rb/selftest_rb_e191_v3.sh`, `rb/selftest_rb_e191_v3_ns.sh`; `repeat_e191.py`,
`desk/v3from_v2_e191.py`, `desk/checks_e191_v3.sh`; the four logs (`logs/selftest-rb-e191-v3.txt`, `logs/dry-listing-e191-v3.txt`,
`logs/repeat-selftest-e191.txt`, `logs/checks-e191-v3.txt`). It also pins the unchanged files the
new ones run, source, import or read: `rb/rb_e191.sh`, `rb/rest_rule_e191.sh`, `rb/s02_window_e191.sh`, `rb/s05_look_e191.sh`,
`rb/s07_a1_sync_e191_v2.sh`, `rb/s08_a1_build_e191.sh`, `rb/s09_a1_reads_e191.sh`, `rb/s10_a1_dry_e191_v2.sh`, `rb/s11_a1_session_e191_v2.sh`,
`rb/s20_wait_e191_v2.sh`, `rb/s22_collect_e191_v2.sh`, `rb/s24_score_e191_v2.sh`, `rb/list_steps_e191_v2.sh`, `rb/selftest_rb_e191_v2.sh`,
`rb/check_history_e191.py`, `rb/readme_check_e191.py`, `rb/data-readme-form-e191.md`, `rb/fake_cmake_e191.sh`, `collect_e191.py`,
`score_e191.py`, `run_e191_v2.py`, `session_e191_v2.sh`, `e191_common_v2.py`, `desk/drylisting_check_e191.py`,
`desk/drylisting_check_e191_v2.py`, `SHA256SUMS-e191-kit-note2`, `SHA256SUMS-e191-a1`, k6's `rb_common.sh`, and the second record's
`SHA256SUMS` and `SHA256SUMS-note1`. Step 2 v3 (`rb/s03_desk_e191_v3.sh`) is outside it, and so is A2's list (`SHA256SUMS-e191-a2`: A2,
E191.md and its registration list, note 1 and its list, A1 and its list, this note, the brief's note 2, and the second record's README, its
data notes 1 and 2, its three lists and the frozen scorer's committed output on it, `scores-e191.json` and `scores-e191.txt`: 17).

    /usr/bin/python3 -I -B tools/claims-v3/e191/repeat_e191.py --selftest <the frozen scorer's output on the second record>
    bash tools/claims-v3/e191/rb/selftest_rb_e191_v3_ns.sh <an empty scratch dir>      # inside a no-device sandbox; about 2 minutes
    bash tools/claims-v3/e191/rb/list_steps_e191_v3.sh <an empty scratch dir> [<day, 2026-11-16 or later> <last start> <last end>]
    /usr/bin/python3 -I -B tools/claims-v3/e191/desk/v3from_v2_e191.py --check
    bash tools/claims-v3/e191/desk/checks_e191_v3.sh                                   # about 4 minutes (the never-run check reads the tree)

SPDX-License-Identifier: Apache-2.0
