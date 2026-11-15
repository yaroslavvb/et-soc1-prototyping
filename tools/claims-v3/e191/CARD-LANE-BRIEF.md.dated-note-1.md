# E191's card-lane brief, dated note 1: the second session of Sun 15 Nov 2026 (E191.md's dated amendment A1), step by step under the kit's dated note 2 (Q184; before any E191 pass datum)

*Sun 15 Nov 2026 (week 46), PST, on aifoundry2, desk only (Q184, lane `note2-e191`; fixed before the land by the lane `fix-n2e191` after
its verifier: kit note 2, section 14), beside [CARD-LANE-BRIEF.md](CARD-LANE-BRIEF.md)
(`eb1ac923`), which it edits nothing in. **Written after E189's data commit `fa9098c4` (Sat 14 Nov 2026, 20:34:12 PST)** and after E191's
first session (its record `1a4bc1e3`), before any E191 pass datum; limited to the kit's mechanics and stricter gates (E191's dated note 1,
section 3). It carries out [E191.md's dated amendment A1](E191.md.dated-amendment-A1.md) with [the kit's dated note 2](KIT.md.dated-note-2.md).
Everything in the brief not named here stands as written there (its sections 1, 3 and 4, THE EARLY STOP, every "never"). No card was
claimed or opened, no device command was sent, no lab box was reached, nothing was posted.*

## 1. What the day carries (A1-3)

- **The go:** his standing words of 10:05:42 PST ("continue, all machines are up") and 10:22:36 PST ("don't worry about discord post, just use
  the machines, nobody is using them"). **The post is waived by his words:** no claim, no release; record it in the result and the README as
  "the owner waived the post: his words, Sun 15 Nov 2026 10:22:36 PST". The host's package counter is not read (step 9 v2 without
  `--rapl-allowed`).
- **G2 = the moment this lane's `W/book.sh take aifoundry1 <lane>` prints BOOKED** (the booking's owner file records it). The window: last
  start G2+1:30, last end G2+3:30, each **rounded up** to the whole minute, inside 2026-11-15; **G2 at 20:29:00 PST or earlier, else no
  second session today** (release the booking and stop). Launch early (by about G2+1:20): step 11 starts no later than the last end less 10
  minutes.
- **The rest** has been open since 10:54:56 PST (the first session ended 10:14:56 PST); step 9 v2 reads it on the box.
- **A NEW RB_OUT**, absent or empty before step 1 (the first session's RB_OUT is never reused: step 9 v2 refuses an RB_OUT whose launch
  sent a card command).
- **The anchor lines** (kit note 2's LAND.md, with the landed commit): E191's registration, note 1, kit and note 2 commits ancestors of HEAD;
  the registration's list `e458fa82...` (11 of 11 OK), note 1's `45ebe831...` (3), the kit's `SHA256SUMS-e191-kit` (73) and note 2's
  `SHA256SUMS-e191-kit-note2` and A1's `SHA256SUMS-e191-a1` at their stated sha256 with every entry OK; step 2 v2 (`rb/s03_desk_e191_v2.sh`,
  outside every list) at its stated sha256; E191 data in a ref only in the first session's record (no pass in it).

## 2. The steps, in order (paths under `tools/claims-v3/e191/`; run from the lab clone's top)

Setup as the brief's section 2 (RB_OUT new, RB_LOCK, RB_GITLOCK, the GNU date shim, git reads over HTTPS by the environment rewrite; a
printed login link stops the step, 11, nothing retried).

| # | the step | what to do with its exit |
|---|---|---|
| B | `bash W/book.sh take aifoundry1 <lane>`: **its time is G2** | 1: another lane holds the box: stop |
| 0 | THE LOAD RULE; `check_day2_v2.py tree --pull` under the lab-git lock (`-E 76` inside slot.sh); the anchor lines as kit note 2's LAND.md states them | any line not as stated: no box step today |
| H | `bash W/hold.sh add <lane>` | as the brief |
| 1 | `rb/s02_window_e191.sh 2026-11-15 <last start> <last end>` from G2 (section 1) | first; a new RB_OUT |
| 2 | **`rb/s03_desk_e191_v2.sh`** with `RB_GITLOCK`, under slot.sh, THE LOAD RULE first, never inside the lab-git lock (v1's step 2 now stops at its never-run check (c): never run it) | anything but 0: no box step today |
| 4 | the look, `rb/s05_look_e191.sh` | FREE on both cards; HELD: `--wait` (30 minutes in all); 16: no launch |
| 3 | the post: **waived** (section 1) | record it |
| 5 | **`rb/s07_a1_sync_e191_v2.sh`** | 0 with "HARNESS OK and HARNESS-V2 OK on the box"; 10: a session or job of ours on the box; 16: uncommitted synced paths or a file off its sha256 |
| 6 | **NO start.** `rb/s08_a1_build_e191.sh wait` alone (A1-4: the first session's build of today stands; the wait re-reads it into this RB_OUT) | 0 with RB_OUT/e191-built.txt "ledger,spp" and the records, harness, preflight and self-checks read on the box; a start would be refused ("both programs were built today", 10): never run it |
| 7 | `rb/s09_a1_reads_e191.sh` | as the brief (its one re-run after the look reads FREE again) |
| 8 | **`rb/s10_a1_dry_e191_v2.sh start`**, then `wait` | 0 with `E191-DRY-V2 rc=0 passes=n dry-check=1 identity-lines=2 note2=1 runtime-dropped=n` (n at least 1) |
| 9- | before step 9 v2: step 10 v2's pattern (`ours_live "session_${RUN}*.sh"`, RUN=e191) matches step 9 v2's launch line (`setsid nohup bash tools/claims-v3/e191/session_e191_v2.sh`) | a mismatch: stop and report |
| 9 | **`rb/s11_a1_session_e191_v2.sh FULL`** | 0 launched (its "last launch:" and rest lines in the runbook log; "session v2, kit note 2" in the LAUNCHED line); 10 refused (the rest, a session or job of ours, no a1-dry-e191-v2 today, an RB_OUT whose launch sent a card command, a second refused launch, or THE LAST LAUNCH: the box's last E191 launch is not the one this RB_OUT recorded): read why, never around it; 16 IDENTITY-STOP: no launch; **14 (a call failed): the launch may have gone out with its answer lost: run no step 9 again before the box is read, read-only (`build/q141k/e191.T0` and that T0's `session.log`), and reported** |
| 10 | **`rb/s20_wait_e191_v2.sh`**, again while it says 17 | as the brief's step 10 (0, 16 GATE-STOPPED, 16 BOUND-SEEN: report at once, kill nothing, keep the booking), plus: NOTE2-SESSION must read yes (a 10 "not kit note 2's": stop and report); **a GATE-STOPPED whose log reads "no device opened" (no card command): THE RELAUNCH RULE below** |
| 11 | **`rb/s22_collect_e191_v2.sh`** (no release: no post) | 0 COLLECTED into `docs/reports/data/2026-11-15-e191-blind-day-aifoundry1-c1-s2/`; 10: not a kit note 2 session, or the directory exists; 16: COPY-BACK not exact, the scrub, the desk-path gate or the history check: commit nothing |
| 12 | the README (section 3), `rb/readme_check_e191.py <the -s2 directory>` (README-CHECK-E191 OK), the public-text scan, then `LAB_QUIET_HOLD_OWNER=<lane> bash W/commit_lab.sh "<subject>" "<body>" docs/reports/data/2026-11-15-e191-blind-day-aifoundry1-c1-s2` | "COMMIT_LAB: pushed <sha>"; on 5 or 6 run it again |
| 13 | after the data commit only: **`rb/s24_score_e191_v2.sh`** | READ the four rules' words (it exits 0 whatever they say); a records lane commits scores-e191.json |
| E | `bash W/hold.sh remove <lane>`; `bash W/book.sh release aifoundry1 <lane>` | on every stop path too (a BOUND: keep the booking until the orchestrator says) |

**THE RELAUNCH RULE** (kit note 2, section 7): a launch whose session log reads "no device opened" (`queue.json` `t_first_ms` null, no
"config start" line: no card command, card time 0) is not a session. Run the look (step 4) again and, when it reads FREE, run step 9 v2
**once more from the same RB_OUT**, inside the same window (its own gates again: the last start, the cap before the last end, the rest,
today's a1-dry-e191-v2 and build): it prints "relaunch: ..." and writes RB_OUT/e191-relaunch.txt. A second refused launch ends the day
(step 9 v2 refuses it, 10). Report the refused launch's T0 and its "no device opened" line in the result and the README (dated); it is not
collected (step 11 v2 collects the T0 in RB_OUT's e191-T0.txt, the last launch). A session that sent a card command and then stopped at a
gate (the identity gate, the stop-path test, the smoke) is the day's second and last session: collect it, commit it, no third.
**THE LAST LAUNCH** (kit note 2, section 7): step 9 v2 also refuses (10) while the box's last E191 launch (`build/q141k/e191.T0`) is not
the last launch this RB_OUT recorded (its `e191-T0.txt`, or with none the first session's T0 1794766494): a launch went out whose ssh call
was lost. Read the box, read-only, and report; never write RB_OUT's files by hand to get past it.

**THE EARLY STOP** is the brief's, with runner v2's process: a SIGTERM only to the process whose command line runs
`tools/claims-v3/e191/run_e191_v2.py session --t0 <T0>` (never `session_e191_v2.sh`, never the process group), or the stop file
`nekko/build/e191/T<T0>/STOP` written by the brief's one bounded ssh call.

## 3. The data README for the second session (step 12)

From `rb/data-readme-form-e191.md` (unchanged), with these differences:
- **the directory** is `docs/reports/data/2026-11-15-e191-blind-day-aifoundry1-c1-s2/`; the title names E191, aifoundry1 card 1, the day and
  **"the second session (E191.md's dated amendment A1)"**, and the paragraph names kit note 2's land commit beside the registration, note 1
  and the kit;
- **What ran** adds, for every host process, the reader's record: the runtime lines dropped (smoke.json's and run.json's `host_line`) and
  any host's line that was not read, by its pass, with its reason;
- **Departures and notes** name: A1 (the second session, its window from G2, the build rule: no start, today's build re-read); his two
  standing words with their times and the post waived; the first session's record (`1a4bc1e3`), used by no rule; any refused launch (its T0
  and line) under the relaunch rule;
- **the Files table** names each pass's **`stdout.txt`** (the host's standard output, raw: the runtime line inside the ledger host's line)
  beside `host-raw.json` (the reassembled line, which the frozen scorer reads), `host.json` (the adapter's fields; sparse parity's verified
  line) and the rest of the form's row; the checker reads basenames, so it passes either way: name it in words all the same.

## 4. Never (in addition to the brief's section 3)

- Never v1's step 2, 5, 8, 9, 10, 11 or 13 in this session; never step 6's start; never runner v1 or session v1.
- Never a third E191 session today (a launch that opened no device is not a session; see the relaunch rule); never into the first
  session's directory, and never an edit of the first session's record.
- Never read the first session's readings for any gate, forecast or rule (A1-2).

## 5. Labels

Every figure here is **registered** (E191.md, its note 1, A1) or a **desk check of code** (KIT.md, kit note 2). Nothing here is measured,
blind, held out or post hoc.

SPDX-License-Identifier: Apache-2.0
