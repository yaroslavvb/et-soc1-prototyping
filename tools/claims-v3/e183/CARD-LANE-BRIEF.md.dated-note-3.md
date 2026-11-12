# The card lane's brief, dated note 3 (Thu 12 Nov 2026, before any E183 datum; Q164): E183's next day, by its kit's dated note 4: the steps in order, the ones never run alone, and what the go names

*Beside `CARD-LANE-BRIEF.md` (E183's copy, `6860643c`) and its dated notes 1 (`1e74546a`) and 2 (`e8e9f4e1`), which it edits nothing of.
It is E183's alone: E185's copy of the brief is not touched, and day 2 (E185, then E183) is over: E185 ran on Thu 12 Nov 2026 and E183 took
its registered SKIP, its train host's two builds read "the host lacks the train change" by a defect of the kit's check. Written on the
Intel, desk only, by the lane `kit-e183n` of Q164, begun at 08:14 PST Thu 12 Nov 2026 by the clock; its commit's own time is git's. The code
is E183's kit note 4 ([`KIT.md.dated-note-4.md`](KIT.md.dated-note-4.md)). **It adds no rule, forecast, threshold, plan, cap or stop**; the
rest rule of note 4 is a gate of the runbook. Notes 1 and 2's lines on the day-2 check v2, the M1 gate and the lab clone kept still stand.
Read before the land by a verifier (`verify-kit183`) and changed by the lane `fix-kit183`: note 4's section 12 lists what changed.*

## 1. What the go for E183's next day names

- **His go and a fresh Tailscale approval for aifoundry3**, with the day and one window in PST (last start, last end) that holds FULL's
  3,900 s before the last end at the launch, about 25 minutes of box steps before it (step 5a's copy among them) and about 15 minutes of
  collection after. E183 has no cool-hour plan: any hour.
- **A day with a Pacific date of Fri 13 Nov 2026 or later.** aifoundry3's `build/e183-build-attempts.txt` holds two `a3-build-e183 started`
  lines dated 2026-11-12 (Thursday's two builds); step 6 v2 counts a day's starts by the Pacific date and refuses a third (NO-THIRD-BUILD,
  16: E183.md section 7's SKIP "at a third start"), after the look and the day's post. A go later on Thu 12 Nov 2026 could only end there.
- **The anchor lines**, given in the go (never written here, since this note is in the list they name): the commit that added note 4 is an
  ancestor of the lab clone's HEAD; `SHA256SUMS-e183-kit-note4`'s own sha256, its 44 entries each OK from the lab's top; the own sha256 of
  `rb/s03_desk_e183_v5.sh` (outside that list); and note 3's lines, still true.
- **At least 40 minutes after our last real session on aifoundry3.** Step 9 v2 reads it from every session log of ours on the box and
  refuses (10) under 40 minutes; nothing else waits on it.
- **The day's one post**, under the one-post rule: `for 1.5 h` for FULL (`for 1 h` for SHORT), released at the end with every word kept.
- E183 may share a day with another run of ours on aifoundry3 (E188 or E187 when they are kitted): one session of ours at a time, each run's
  collection before the next run's look. E183 FULL first is a preference, not a plan: E183.md section 7 lets E183 "go first or follow any
  run", and the other run's own go and window decide.

## 2. The order (note 4's section 7)

| | step | file |
|---|---|---|
| 0 | the day-2 check v2, by hand, under the lab clone's commit lock | `/usr/bin/python3 -I -B tools/claims-v3/e185/rb/check_day2_v2.py tree --pull` |
| 1 | the window, FIRST | `rb/s02_window_e183.sh <day> <last start> <last end>` |
| 2 | the desk check | **`rb/s03_desk_e183_v5.sh`** |
| 4 | the look, BEFORE the post | `../q141k-runbook/k6/s05_look_k6.sh aifoundry3` |
| 3 | the post | the card lane's, under the post's lock |
| **5a** | **the read-only copy of Thursday's build records** | **`rb/s06_a3_records_e183.sh`** |
| 5 | the sync | `rb/s07_a3_sync_e183.sh` |
| 6 | the build | **`rb/s08_a3_build_e183_v2.sh start`**, then `wait` while it says 17 or 14 |
| 7 | the reads | `../q141k-runbook/k6/s09_a3_reads_k6.sh` |
| 8 | the dry pass | **`rb/s10_a3_dry_e183_v2.sh start`**, then `wait` |
| 9 | the session | **`rb/s11_a3_session_e183_v2.sh FULL`** (`SHORT` only when the window cannot fit FULL) |
| 10 | the wait | `rb/s20_wait_e183.sh`, again while it says 17 |
| 11 | the release, then the collection | `rb/s22_collect_e183_v2.sh` |
| after the data commit | october-forecast-model's reader behind the gate | `/usr/bin/python3 -I -B tools/claims-v3/e185/rb/check_day2_v2.py m1 e183 --data <E183's data dir>` |

**Never run alone on that day:** E183's step 2 v4, v3, v2 or v1; step 6 v1 (`rb/s08_a3_build_e183.sh`); step 8 v1
(`rb/s10_a3_dry_e183.sh`); step 9 v1 (`rb/s11_a3_session_e183.sh`); step 11 v1 (`rb/s22_collect_e183.sh`); and v1's box files as a session's
(`build_host_e183.sh`, `block_e183.sh`, `queue_e183.sh`, `session_e183.sh`). Step 6 v1 and block v1 grep the host for the train change, which
a GCC build fails; step 9 v1 has no rest rule.

## 3. Readings on the day

- **Step 5a before any build.** Step 6 v2's start refuses (10) until step 5a has written `RECORDS-COPIED` in this day's `RB_OUT`. Step 5a
  prints the box's compiler line from Thursday's cmake log: put it in the day's records. COPIED WITH GAPS (records the box's own rsync
  names missing; 0 files when none is left) is not a stop; a 14 is (run step 5a again, never step 6 first). Step 5a runs once a day: in an
  RB_OUT that already holds `RECORDS-COPIED` it refuses (16) and calls nothing, which on the same day means the copy is done (go on to
  step 5); a new day takes a new RB_OUT.
- **No tidy of aifoundry3 moves or removes E183's build records** (`build/e183-build-logs/`, the attempts file, the cmake log, the inputs
  and tree checks, the build job's four files) before a copy of them is on the desk: step 5a's `RECORDS-COPIED` on E183's next day, or a
  tidy lane's own read-only copy first.
- **Step 6 v2's build** prints `TRAIN-CHANGE OK: ...` in its job's log before `BUILD OK`; `TRAIN-CHANGE MISSING` means the host refused the
  patch's options (a failed build: the re-run rule, then the fallback, as v1's). After TRAIN-HOST-INPUTS-DIFFER, step 5 once more.
- **Step 9 v2's rest line** (`rest: <m> minutes since E<run>'s session end ...`, or `REFUSED: <m> minutes since ...`) goes into the runbook's
  log and the day's records; under 40 minutes, wait and run step 9 v2 again (the window allowing).
- **Step 2 v5 reports** lists it does not know and notes M1's and M2's lists (never a gate). Its 16 names a gate list, the harness v2 or a
  log: a dated note first.
- Everything else as notes 1 and 2 say: a 14 with "no reading (rc 14)" and no JOB-DONE or JOB-LOST is a cut call (wait again); one session
  of ours at a time; the window is never rewritten; nothing but the card lane writes or commits in the lab clone from step 2 to E183's data
  commit.

SPDX-License-Identifier: Apache-2.0
