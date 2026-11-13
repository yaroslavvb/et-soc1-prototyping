# The card lane's brief, dated note 5 (Fri 13 Nov 2026, before any E183 train datum; Q173): E183's second session that day, by E183.md's dated amendment A1 and the kit's dated note 6: the steps in order, the aside before the sync, no build, step 8 v3, step 9 v3, step 10 v2, and the steps never run alone

*Beside `CARD-LANE-BRIEF.md` (E183's copy, `6860643c`) and its dated notes 1 (`1e74546a`), 2 (`e8e9f4e1`), 3 (`24b9b99e`) and 4
(`9ae55d39`), which it edits nothing of. It is E183's alone. Written on aifoundry2, desk only, by the lane `kit-e183n6` of Q173 (Fri 13
Nov 2026, PST by the clock; its commit's own time is git's), and changed before the land by the lane `fix-n6` of Q173 to answer the
verifier `verify-n6` (the kit's note 6, section 15). It answers E183's first session of that day (aifoundry3 card 0, T0 13:14:18
PST): it stopped at its smoke gate by a kit defect before any train block (1.0 card-minute), and step 10 read a false RUN-GONE while the
smoke ran. The code is the kit's dated note 6 ([`KIT.md.dated-note-6.md`](KIT.md.dated-note-6.md)); the second session is allowed by
[`E183.md.dated-amendment-A1.md`](E183.md.dated-amendment-A1.md). **It adds no rule, forecast, threshold, plan, cap or stop.** No card
was claimed, no device command was sent, no lab box was reached, nothing was posted.*

## 1. What the go for the second session names

- **Amendment A1's window: day 2026-11-13, last start 21:00, last end 22:30 PST**, in **a new RB_OUT** (never the first session's), and
  the owner's go for the day (his words that morning; the day's post and its release waived).
- **The new RB_OUT**, named by the go, outside the first session's (`card-e183f`'s `rb/`), and read **absent or empty before step 1**:
  `[ ! -e "$RB_OUT" ] || [ -z "$(ls -A "$RB_OUT")" ]` exits 0, else stop and report. Step 9 v3 also refuses (10), at the desk before any
  call, an RB_OUT that already holds a session's T0 (`t0-e183.txt`): one RB_OUT, one session.
- **The anchor lines** (never written here, since this note is in the lists they name): note 4's lines 1-6 and note 5's lines 1-5, still
  true; then note 6's: the commit that added note 6 and amendment A1 is an ancestor of the lab clone's HEAD; `SHA256SUMS-e183-kit-note6`'s
  and `SHA256SUMS-e183-a1`'s own sha256, each list's entries all OK from the lab's top; the own sha256 of `rb/s03_desk_e183_v7.sh` (in
  neither list); and the git modes of note 6's files.
- **The first session's read-only desk copy** (the card lane `card-e183f`'s `rb/box-session-e183/` with its
  `box-session-e183.box-manifest.txt`): step 5b reads it.
- **At least 40 minutes after our last real session on aifoundry3**: the first session ended 13:15:19 PST, so step 9's rest gate opened at
  13:55:19 PST.

## 2. The order

| | step | file |
|---|---|---|
| 0 | the day-2 check v2, by hand, under the lab clone's commit lock (GitHub reads over HTTPS by the environment rewrite); then the anchor lines | `/usr/bin/python3 -I -B tools/claims-v3/e185/rb/check_day2_v2.py tree --pull` |
| 1 | the window, FIRST, in a new RB_OUT (absent or empty: section 1) | `rb/s02_window_e183.sh 2026-11-13 21:00 22:30` |
| 2 | the desk check | **`rb/s03_desk_e183_v7.sh`** (step 2 v6, then note 6's and A1's lists, the harness v3, note 6's four desk tests' logs) |
| 4 | the look | `../q141k-runbook/k6/s05_look_k6.sh aifoundry3` |
| 3 | the post | **waived** (the owner's words, Fri 13 Nov 2026 about 11:30 PST): record it in the result and the data README |
| 5a | the read-only copy of the box's build records into this RB_OUT | `rb/s06_a3_records_e183.sh` (today's: the day's one build) |
| **5b** | **the aside: the first session's smoke and stop-path test moved aside on the box** | **`rb/s06b_a3_aside_e183.sh <card-e183f's rb/box-session-e183>`** (its manifest beside it) |
| 5 | the sync (it carries note 6's files) | `rb/s07_a3_sync_e183.sh` |
| 6 | the build | **NOT RUN**: the day's one good build (13:13 PST, TRAIN-HOST-BUILT) stands; a start would refuse (10); NO-THIRD-BUILD binds |
| 7 | the reads | `../q141k-runbook/k6/s09_a3_reads_k6.sh` |
| 8 | the dry pass of note 6's files | **`rb/s10_a3_dry_e183_v3.sh start`**, then `wait` (job `a3-dry-e183-v3`) |
| 9 | the session | **`rb/s11_a3_session_e183_v3.sh FULL`** (`SHORT` only when the window cannot fit FULL) |
| 10 | the wait | **`rb/s20_wait_e183_v2.sh`**, again while it says 17 |
| 11 | the collection (the release is waived) | `rb/s22_collect_e183_v3.sh` |
| after the data commit | october-forecast-model's reader behind the gate | `/usr/bin/python3 -I -B tools/claims-v3/e185/rb/check_day2_v2.py m1 e183 --data <E183's data dir>` |

The dry listing of this table: `rb/list_steps_e183_v7.sh`.

## 3. Never run on the second session

Notes 3 and 4's lists, and also: **step 2 v6** alone (`rb/s03_desk_e183_v6.sh`, which runs unchanged inside step 2 v7); **step 6** in any
version (`rb/s08_a3_build_e183_v2.sh start`, `rb/s08_a3_build_e183.sh`); **step 8 v2** (`rb/s10_a3_dry_e183_v2.sh`: block v2); **step 9
v2** (`rb/s11_a3_session_e183_v2.sh`: session v2, whose smoke ends at the post-block check's KeyError); **step 10 v1**
(`rb/s20_wait_e183.sh`: it reads any session after v1 as gone); and **note 4's box files as a session's** (`block_e183_v2.sh`,
`queue_e183_v2.sh`, `session_e183_v2.sh`, `preflight_e183_v2.sh`).

## 4. Readings on the day

- **Step 5b** prints the desk copy's reading first (`the desk's copy is exact: 11 files of .../e183-smoke/p18301 and 8 of
  .../e183-stoptest/p18302 ...`), then one of: `ASIDE-DONE` (0: moved to `build/claims-v3/aifoundry3/e183-aside-2026-11-13-t1794604458/`);
  `ASIDE-ALREADY` (0: a second run, nothing moved); `REFUSED` (10: a session or a runbook job of ours runs there: wait, then again);
  `ASIDE-DIFFERS`, `ASIDE-MISSING` or `ASIDE-EXISTS` (16: nothing moved; the box no longer holds what the copy holds: stop and report, never
  move anything by hand); `ASIDE-FAILED` (16: a `mkdir` or a rename failed on the box, or the list under the aside name is not the copy's
  after the move; its form `ASIDE-FAILED: mv .../p18302 (after .../p18301 moved to ...)` is a partial move, `p18301` moved and `p18302`
  not): **stop and report**, and move nothing by hand before a dated note says how; a run of step 5b after it reads `ASIDE-MISSING` (16),
  and step 9 v3 refuses while `p18302` sits in the data root, so no session starts. It writes `RB_OUT/aside-e183.txt`. A 16 before any call
  names the desk copy (it is not exact against its own manifest): stop and report.
- **Step 9 v3** refuses (10) while any entry sits in `build/claims-v3/aifoundry3/e183`, `e183-smoke` or `e183-stoptest` on the box (step 5b
  first), and without today's dry pass v3 (step 8 v3; the morning's `a3-dry-e183` does not count). Its rest line goes into the runbook's log.
  It also refuses (10) at the desk, before any call, when RB_OUT already holds `t0-e183.txt` (`this RB_OUT already holds a session's T0
  ...: one RB_OUT, one session`), and on the box while `build/e183/STOP` or `build/claims-v3/STOP` exists (`REFUSED: <file> exists on the
  box (an operator's stop ...)`: queue v3 reads both before every item, so a stale one would end the session after its smoke with no train):
  stop and report, and remove no stop file by hand before a dated note says whose it is.
- **The launch**, as the runbook test v4's case L shows it on a stand-in box: `LAUNCHED e183 T0=<T0> <date> <time> PST (plan FULL; gates:
  ...)`, then step 9's line `e183 launched on aifoundry3, T0 <T0> (plan FULL)`, and `RB_OUT/t0-e183.txt` holds that T0; the first line of
  the box's `build/e183/session-t<T0>.log` reads `<date> <time> PST session start (T0 <T0> = <time> PST), kit note 6; plan FULL`. A first
  line without `kit note 6` is not session v3: stop and report.
- **Session v3** stops before any device (8, `USER is '...', not this login ...: no device opened`) if `USER` is not the login: D1's
  other-user rule reads it. Over ssh it is set; a 16 at step 10 naming this line means the launch's environment lost it.
- **Step 10 v2** matches E183's session and queue in every version: `RUN-RUNNING` (17) while it runs, `RUN-ENDED` (0) at `session end (T0
  ...)`, `GATE-STOPPED` (16) after a gate line. A `RUN-GONE` (14) now means what it says: no session process and no end; read the box's log
  read-only before anything else.
- **The smoke's block** reads `ok smoke: no post-block check (...); its gate is check_e183.py smoke, run by the session next` in its
  block.json; the gate's own line follows in the session log (`SMOKE GO: ...` or `SMOKE NO-GO: ...`), and only the gate decides.
- **The collection (step 11 v3)** copies `e183`, `e183-smoke` and `e183-stoptest` whole: after step 5b they hold the second session's alone;
  the first session's stay under the aside name, never collected by step 11.
- Everything else as notes 1-4 say.

SPDX-License-Identifier: Apache-2.0
