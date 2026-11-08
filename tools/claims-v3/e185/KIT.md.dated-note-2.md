# E185's kit, dated note 2 (Sun 8 Nov 2026, before any E185 datum): step 2 v3 pins E185's five lists at their counts and their own bytes (8, 13, 21, 5 and 28) with no override, and runs again just before step 14; october-forecast-model's note M1's list is read and reported, never a gate; the day-2 brief; lines for the records; no box file, rule, forecast, plan, cap, stop or order of box steps changes

*Beside [KIT.md](KIT.md) (`460c352f`) and [KIT.md.dated-note-1.md](KIT.md.dated-note-1.md) (`ad2ed873`, 22:45:02 PST Sat 7 Nov 2026); it
edits nothing there. Written on the Intel, desk only (no card, no device command, no ssh to a lab box, no post in the lab's channel, no
Modal), by the lane `fix-d2` of Q157, first written between 06:20 and 06:50 PST Sun 8 Nov 2026 by the clock; its commit's own time is
git's. It answers the adversarial verifier of E183's notes 1, E185's A1 and kit note 1, and the two october-forecast-model notes M1
(`verify-d2`, Sun 8 Nov 2026 05:22-06:08 PST: **holds with fixes**, 0 critical, 0 major, 3 minor faults and 6 nits): its minor fault 2
(critic-q155's nit 2, confirmed), its minor fault 3 on E185's side, and its nits 7, 8 and 9. E183's side of fault 3 and its fault 1 and
nits 4-6 are answered in E183's kit ([`../e183/CARD-LANE-BRIEF.md`](../e183/CARD-LANE-BRIEF.md) and
[`../e183/E183.md.dated-note-M1.md.dated-note-1.md`](../e183/E183.md.dated-note-M1.md.dated-note-1.md)). **No E185 datum exists**
(`git log --all` on `docs/reports/data/*e185*` and `*-e185-*`: nothing). **No box file changes:** `frozen-e185.sha256`'s 30 entries, the
runner, the session, the block, the smoke gate, the stops and the device commands are the kit's as committed, and so is every step that
reaches the box. The kit's audit (GO, 38 send sites) and the runbook's (GO, 11) stand.*

## Results first (desk only; nothing is measured)

| check | result | file |
|---|---|---|
| **step 2 v3's desk test**, on a shared, sparse scratch clone of the lab with a local upstream (step 2 reads only git and the lab's files; stand-in ssh and rsync refuse any call) | **SELFTEST-RB-E185-V3 PASS, 11 of 11** (A3, K, P0, P1, P2, P3, P4, P5, M1, W, Z); 0 calls to any box | [`rb/logs/selftest-rb-v3.txt`](rb/logs/selftest-rb-v3.txt) |
| **the dry listing v3** | every step exits 0, no ssh or rsync call, the look listed before the day's post, step 2 v3 listed twice (step 2, and again just before step 14) | [`rb/logs/dry-listing-v3.txt`](rb/logs/dry-listing-v3.txt) |
| **device commands**, the runbook as it now runs (kit note 1's, with step 2 v3 in v2's place) | **GO, 11 send sites** with E128's guard, every one a READ; bare, NO-GO at exactly step 9's guard call; **both bodies byte for byte kit note 1's** (`rb/logs/dmcmd-audit-v2.txt`, `-bare-v2.txt`): step 2 v3 sends no device command | [`rb/logs/dmcmd-audit-v3.txt`](rb/logs/dmcmd-audit-v3.txt), [`rb/logs/dmcmd-audit-bare-v3.txt`](rb/logs/dmcmd-audit-bare-v3.txt) |
| **step 2 v3 for real**, on a scratch clone holding this note's final files, with its own window written that day | rc 0; the five lists at their pins and bytes, the kit note 2's list at 16, note M1 "present, its list 21 of 21 at its pinned bytes" | the lane's own run (the records give its time) |

## Builds on

1. **Checked.** The prior-work inventory (Q145's stock-take, private scratch), read Sun 8 Nov 2026 at about 06:30 PST: public rows H24, H25
   and H28 (opaque pointers), as KIT.md and its note 1 read them.
2. **Used.**
   - **E185's kit note 1** (`ad2ed873`): `rb/s03_desk_e185_v2.sh`, the form of step 2 v3, line for line but the changes marked v3;
     `rb/list_steps_e185_v2.sh`, the form of the dry listing v3; `rb/selftest_rb_e185_v2.sh`'s case K, the form of this test's K.
   - **E183's kit note 1** (`45e514e3`): `rb/s03_desk_e183_v2.sh`, the form of a step 2 whose every list sits at a pinned count with no
     override, and `rb/selftest_rb_e183_v2.sh`'s cases P1-P2, the form of a step-2 case on a scratch repository with an upstream.
   - **verify-d2's case** (its throwaway branch: the kit note 1's list cut to 27 lines, v2 rc 0), re-made here as P1; its P5 and P6
     classes (a list's bytes changed with its count kept, against E183's collector), re-made here against E185's lists as P5 and P4.
   - **E185's note M1** (`2f6a4440`): its list `SHA256SUMS-e185-m1` (21) and its reader's run line, which the brief names.
   - *The same operation, earlier:* on the intact tree v2 and v3 read alike (P0: both 0); v3 differs from v2 only where a list is off its
     pin (P1, P3, P4, P5), and v2's committed desk test stands for every other step (its log, `rb/logs/selftest-rb-v2.txt`).
3. **Not used.** Any change to a box file or a box step; aifoundry1 or aifoundry2; any E185 datum (none exists); anything of the
   private tier.
4. **Tiers.** Public tier only. No private-tier check is used, so there is no sha256 line.
5. **Readiness.** This block is the note's own.

## The runbook as it now runs (kit note 1's table, with this note's changes)

| step | file | from this note |
|---|---|---|
| 1, the window | `rb/s02_window_e185.sh <day> <last start> <last end>` | unchanged |
| 2, the desk check | **`rb/s03_desk_e185_v3.sh`** | v2's checks, with E185's five lists at their pinned counts and their own bytes and the kit note 2's list at its count, HEAD descending from kit note 1 too, and note M1's list reported |
| 3, the look, FIRST | `rb/s05_look_e185.sh aifoundry3 [--wait]` | unchanged |
| 4, the day's post | (the card lane's, not scripted) | after the look |
| 5-7, sync, preflight, reads | `rb/s07_a3_sync_e185.sh`, `rb/s08_a3_preflight_e185.sh`, `rb/s09_a3_reads_e185.sh` | unchanged |
| 8, the dry pass | `rb/s10_a3_dry_e185.sh start`, then `wait` | unchanged (the brief's "no reading" line) |
| 9, the host's start window | `rb/s12_a3_host_e185.sh start` | unchanged |
| 10, the launch | `rb/s11_a3_launch_e185_v2.sh [--later-try] [--under-an-hour] [--after-noon]` | unchanged (kit note 1's v2) |
| 11, the wait | `rb/s20_wait_e185.sh` | unchanged |
| 12, the host's end window | `rb/s12_a3_host_e185.sh end` | unchanged |
| 13, the release | (not scripted) | |
| **before 14** | **`rb/s03_desk_e185_v3.sh` again**, with the same `RB_OUT` | **new: step 14 runs only on its 0** |
| 14, the collection | `rb/s22_collect_e185_v2.sh` | unchanged (kit note 1's v2) |

**v1's and v2's step 2 (`s03_desk_e185.sh`, `s03_desk_e185_v2.sh`) are never run on E185's card day,** nor v1's steps 10 and 14. Step 2 v3
sources the kit's `rb_common_e185.sh` unchanged, with the same exit codes (KIT.md). The day's order with E183 is
[CARD-LANE-BRIEF.md](CARD-LANE-BRIEF.md), this note's brief.

## Fault by fault

### verify-d2's minor fault 2 (critic-q155's nit 2): E185's lists were read without their pins

- **What v2 did.** Step 2 v2 checked E185's five lists only as "every entry OK" (`n == w`, the list's own line count), so a list a later
  commit cut short would pass, where M11's seventeen lists and the footing law's two sat at pinned counts, and E182's, E184's and E183's
  step 2s pinned every list. `verify-d2` showed it on a throwaway branch: the kit note 1's list cut to 27 lines and committed, step 2 v2 rc
  0, where E183's step 2 v2 refused the same cut of its own list (16). Step 14 v2 reads its eight lists by shasum's exit status alone, hours
  after step 2.
- **What v3 does** ([`rb/s03_desk_e185_v3.sh`](rb/s03_desk_e185_v3.sh)):
  - **E185's five lists**, each OK in full, at its pinned count and at its own committed sha256, with no override:

    | list | entries | its own sha256 (committed once, never modified) |
    |---|---:|---|
    | `SHA256SUMS-e185-registration` (`98fe28b7`) | 8 | `dd772a17...` |
    | `SHA256SUMS-e185-kit` (`460c352f`) | 13 | `79fdc928...` |
    | `rb/SHA256SUMS-rb-e185` (`460c352f`) | 21 | `2f5371e8...` |
    | `SHA256SUMS-e185-a1` (`df4e6763`) | 5 | `8757f508...` |
    | `SHA256SUMS-e185-kit-note1` (`ad2ed873`) | 28 | `0eeedd7c...` |

    The byte pins go one step past the counts the fault asked for: they close, for E185's own lists, the class `verify-d2`'s nit 4 found in
    E183's count-only pins (a list rewritten with a file and its line together, P5; a line replaced by a copy of another, P4), which a
    count cannot see. E183's lists stay as its kit note 1 pins them (the nit's own fix is "the next E18x kit"; no action for day 2).
  - **This note's own list**, `SHA256SUMS-e185-kit-note2`, at its count, 16. It lists step 2 v3, so step 2 v3 cannot pin its bytes.
  - HEAD also descends from E185's kit note 1 (`ad2ed873`). Everything else is v2's, line for line.
- **Step 14's lists, read at their pins on the tree step 14 runs on.** `verify-d2` offered two fixes: a step 14 v3 with the same pins, or
  step 2 v3's pin check again just before step 14. This note takes the second. Step 2 v3 reads all eight of step 14 v2's lists at their
  pins (E185's five at their counts and bytes; M11's `SHA256SUMS-score-m11-v5`, `-score-m11-v4` and `-a10` at 4, 5 and 4), and it reaches
  no box. Step 14 v2 and the collector v2, which copy from the box, stay as committed and as tested by kit note 1. So **the card lane runs
  step 2 v3 again after the release, and step 14 only on its 0** (the brief, section 2). A 16 there that names a list means step 14 does
  not run, E185's files stay on the box read-only, and a dated note decides first. A 16 naming only `pull` is the network's: run it again.
  E185 is launched before noon, so its step 14 falls on the day its window was written, which step 2 v3 checks.
- **Desk cases** ([`rb/logs/selftest-rb-v3.txt`](rb/logs/selftest-rb-v3.txt)):
  - P0: the intact clone, v3 0 naming every pin, and v2 0;
  - P1: `verify-d2`'s case, the kit note 1's list at 27: v3 16, "SHA256SUMS-e185-kit-note1(27 OK of 27; pinned 28; ...)"; v2 0;
  - P2: each other list one line short, one at a time, the kit note 2's among them: v3 16 each, the list named with its count and pin;
  - P3: the registration's list with a line repeated (9 lines, every one OK): v3 16; v2 0;
  - P4: A1's list with its last line replaced by a copy of its first (5 lines, every one OK, a file no longer pinned): v3 16 on the list's
    own bytes; v2 0;
  - P5: `a1-e185.txt` rewritten together with its line in A1's list (5 lines, every one OK): v3 16 on the list's own bytes; v2 0;
  - W: step 2 v3 twice in a row, as the card day runs it: 0 and 0, the paths clean after, nothing appended to the lock file, no call;
  - K: no window, and a window from another day: 10 before any call each time.

### verify-d2's minor fault 3, E185's side: note M1's list was read by no step

- **What it was.** `SHA256SUMS-e185-m1` (21 entries: the note, its json, its reader, its self-test and log, and 16 files already pinned
  elsewhere) sat outside E185's five lists and both collectors, and the reader pins only its json, so nothing checked the reader's own bytes
  before day 2's run.
- **What step 2 v3 does.** It reads the list at its count (21) and its own committed sha256 (`52a6c162...`) and **reports** it, never as a
  gate: "present, its list 21 of 21 at its pinned bytes (read beside, by its reader, after step 14)", or "present, but its list is off its
  pin (...): the M1 arm is not read on this day", the same line in the runbook's log. The M1 arm is a reported arm that E185.md never
  provided for, and its note changes no rule, plan, stop or order; a gate on its list would let a reported arm stop E185, so step 2 v3
  reports it instead. The kit note 2's own list (16) holds no M1 file for the same reason. *Desk case M1:* the list cut to 20, v3 0 with the
  miss named and logged; the note itself removed, v3 0, "absent (not read)".
- **Before the reader** (the brief, section 6): `shasum -a 256 -c tools/claims-v3/e185/SHA256SUMS-e185-m1` must read 21 of 21 OK, else the
  reader is not run and the data README records the refusal. The list holds the reader's own bytes, so this checks the reader too.

### verify-d2's nit 9: the M1 note's "step 22", and a missing room

- E185's M1 note (M1-4) places its reader "after step 22's score". In E185's own numbering that step is **step 14** (`rb/s22_collect_e185_v2.sh`,
  named after its file). The brief names it so: after E185's step 14 and before the data commit.
- The reader stops with a TypeError (rc 1), where it should refuse, on a score whose start gate carries no `room_c`. That is latent: a
  scored E185 passed its start gate, whose mark carries the room. The reader stays as committed and pinned (its list's 21); the brief says a
  reader's refusal or any non-zero exit never blocks the data commit, and the README records it with the output. A later reader refuses a
  missing room.

### verify-d2's nit 8: the scorer v5's report prints A1's records rules without their words

`scored-m11.md` prints "E185-C on F", "on B" and "on Rl" with no word that the F line governs (A1-2), and A10's pooled HM-CAL and
HM-CAL-I8 verdicts (in `verify-d2`'s stand-in case, "HM-CAL BETTER; HM-CAL-I8 BETTER") with nothing saying they are E181's (A1-3). The scorer is unchanged by design. **The brief (section 7) and E185's data
README carry A1-2's and A1-3's words**: E185-C's consequence from its F line only; the pooled HM-CAL and HM-CAL-I8 verdicts are E181's,
never E185's.

### verify-d2's nit 7: A1-1's timeline, two lines for the records

A1-1's table stands as committed, and its disclosure holds; the records add two lines beside it (`verify-d2` read them from the round's
local slot log, the e185 lane's scratch files and git, and this note re-read the slot log and the statement file's time):
1. Sat 7 Nov 2026, 20:03:59-20:04:05 PST: the e185 lane's first job, a layout read of the training sessions (E144's, E154's and E166's
   committed passes: their holds, rests, windows and Pref), with no arm and no E181 file read. A1-1's table leaves it out.
2. The arms statement's last write is 20:08:37 PST, its appended freeze record; "written at 20:03" is the time in its own header.

Both come before the E181 stage (20:08:43), so A1-1's account of the switch to the two-pass reading, after both E181 held-out readings were
printed, stands as written.

### Found here: the dry listing's labels

`rb/list_steps_e185_v2.sh` (and v1's) print the day's post as "step 6" and the release as "step 21", an older numbering; KIT.md and kit
note 1 call them steps 4 and 13. The dry listing v3 prints 4 and 13. A records nit; no step changes.

## What the card day reads from this note

- Step 2 is v3, run as step 2 and again just before step 14 (step 14 only on its 0).
- The day's order with E183, the "no reading" line, the post, the readers' places and the README's words: [CARD-LANE-BRIEF.md](CARD-LANE-BRIEF.md).
- E185's own `RB_OUT`, and the day's one `RB_LOCK`.

## What does not change

KIT.md, kit note 1 and their files and lists; the box list (`frozen-e185.sha256`); the session, runner, block, smoke gate, stops, device
commands, budget and cap; every step that reaches the box; E185.md and A1; note M1 and its reader; M11's scorer v5; E181's data. The rest
gate's 40 minutes, A7-4's noon and hour, and the 6,300 s window gate are step 10 v2's, as committed. The v3 files are new; v1's and v2's
stay as committed.

## Files ([`SHA256SUMS-e185-kit-note2`](SHA256SUMS-e185-kit-note2), 16 entries)

This note; [CARD-LANE-BRIEF.md](CARD-LANE-BRIEF.md); [`rb/s03_desk_e185_v3.sh`](rb/s03_desk_e185_v3.sh),
[`rb/list_steps_e185_v3.sh`](rb/list_steps_e185_v3.sh) and [`rb/selftest_rb_e185_v3.sh`](rb/selftest_rb_e185_v3.sh); the logs
`rb/logs/selftest-rb-v3.txt`, `dry-listing-v3.txt`, `dmcmd-audit-v3.txt` and `dmcmd-audit-bare-v3.txt`. The list also pins the unchanged
files step 2 v3 sources and the steps the brief names beside it: `rb/rb_common_e185.sh`, `rb/s02_window_e185.sh`, `rb/s03_desk_e185_v2.sh`,
`rb/s10_a3_dry_e185.sh`, `rb/s11_a3_launch_e185_v2.sh`, `rb/s20_wait_e185.sh` and `rb/s22_collect_e185_v2.sh`, each at the sha256 kit note
1's or the runbook's list names it with. It holds no file of note M1.

    bash tools/claims-v3/e185/rb/selftest_rb_e185_v3.sh <a scratch directory outside the repo> > selftest-rb-v3.txt
    bash tools/claims-v3/e185/rb/list_steps_e185_v3.sh <an empty scratch directory> > dry-listing-v3.txt

## Labels

- **Registered:** every list, pin, step, gate, plan, cap and stop named here (E185.md with A1, M11's A7-4, KIT.md and its notes); this
  note's step 2 v3 and its re-run before step 14, before any datum.
- **Desk checks of code, not measurements:** every test result here.
- **Post hoc:** the two timeline lines for A1-1 (the round's slot log and the scratch files' times, read after A1).
- **Reported:** october-forecast-model's arm (note M1); its forecasts are blind for E185 (frozen before any datum).
- Nothing here is held out.

## Compute

The Intel, through the round's local slot, one job at a time at nice 10: a development run of the desk test (06:27:02-06:29:19 PST, 137 s),
the audits (06:30:25), the public-text pre-scans (06:39-06:40), then the committed runs of the desk test (06:41:08-06:43:30, 142 s), the dry listing and the
audits (06:43:30-06:43:35), and step 2 v3 for real on a scratch clone of the final files. The scratch clones are shared and sparse (about 250 MB each) and are removed after use. No lab box, no remote host, no
card.

SPDX-License-Identifier: Apache-2.0
