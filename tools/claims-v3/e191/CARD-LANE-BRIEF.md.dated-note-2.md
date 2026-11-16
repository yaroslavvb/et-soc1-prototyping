# E191's card-lane brief, dated note 2: the third session (E191.md's dated amendment A2, a REPEAT), step by step under the kit's dated note 3, on Mon 16 Nov 2026 or a later day (Q190-Q191; after the second session's data and scores, before any datum of a third)

*Sun 15 Nov 2026 (week 46), PST, on aifoundry2, desk only (lane `a2-e191`: begun in Q190, cut off at about 18:05 PST when the round's agents
stopped at the session's weekly usage limit, finished in Q191), beside [CARD-LANE-BRIEF.md](CARD-LANE-BRIEF.md) and
[its dated note 1](CARD-LANE-BRIEF.md.dated-note-1.md), which it edits nothing in. **Written after E189's data commit `fa9098c4` (Sat 14 Nov
2026, 20:34:12 PST), after E191's second session's data commit `7156ac15` (Sun 15 Nov 2026, 14:32:17 PST) and after the scores commit
`f74c81e3` (17:37:11 PST)**, before any datum of a third session; limited to the kit's mechanics and stricter gates (E191's dated note 1, section 3). It carries out
[E191.md's dated amendment A2](E191.md.dated-amendment-A2.md) with [the kit's dated note 3](KIT.md.dated-note-3.md). Everything in the brief
and its note 1 not named here stands as written there (THE EARLY STOP, THE RELAUNCH RULE, every "never"), except note 1's "never a third E191
session today", which A2 supersedes for this one repeat. No card was claimed or opened, no device command was sent, no lab box was reached,
nothing was posted.*

## 1. What the day carries (A2-4, A2-5)

- **The day:** Mon 16 Nov 2026, or a later Pacific day (Sunday's windows closed before A2 could land).
- **The go:** his standing words of Sun 15 Nov 2026, 10:05:42 PST ("continue, all machines are up"), 10:22:36 PST ("don't worry about discord
  post, just use the machines, nobody is using them") and 17:21:16 PST (use more cards in parallel), and his "Try again" after the round's
  stop (received at or before 21:28:59 PST that day), beside the report of his words posted for him at 19:34:12 PST ("The aifoundry cards are
  all free right now ...; feel free to use them"); on a later day the same words, unless he says otherwise. **The post is waived by his words:** no claim, no release; record it in the result and the README as "the owner waived the
  post: his words, Sun 15 Nov 2026 10:22:36 PST". The host's package counter is not read (step 9 v3 without `--rapl-allowed`).
- **G3 = the moment this lane's `W/book.sh take aifoundry1 <lane>` prints BOOKED** (the booking's owner file records it). The window: last
  start G3+1:30, last end G3+3:30, each **rounded up** to the whole minute, inside that Pacific day; **G3 at 20:29:00 PST or earlier, else no
  third session that day** (release the booking and stop; a later day takes a new booking). Launch early (by about G3+1:20).
- **The rest:** open since 15:01:46 PST Sun 15 Nov 2026 (the second session ended 14:21:46 PST) unless another session of ours ran on
  aifoundry1 since (E198, E199): then 40 minutes after its end. Step 9 v3 reads it on the box. **Run step 7 only after the rest has opened** (its config read is a
  card command: E192's lesson).
- **The build:** the third session's day builds its own: that day's first start, then the wait (A2-5: Sunday's build records are not that
  day's, so step 6's wait alone refuses with 10, "no build job was started today").
- **A NEW RB_OUT**, absent or empty before step 1 (no earlier session's RB_OUT is ever reused: step 9 v3 refuses an RB_OUT whose launch sent a
  card command, and THE LAST LAUNCH refuses an RB_OUT that does not know the box's last launch).
- **The anchor lines** (kit note 3's LAND.md, with the landed commit): E191's registration, note 1, kit, note 2 with A1, the second session's
  data commit and its data note 1, and A2's land commit, ancestors of HEAD; every list step 2 v3 pins at its stated sha256 with every entry
  OK; step 2 v3 (`rb/s03_desk_e191_v3.sh`, outside every list) at its stated sha256; E191 data in a ref only in the first record (no pass in
  it) and the second.
- **THE EXCLUSION RULE** (A2-6): E194's committed step 2, and the step 2 v2 of E194's amendment A1, leave out E191's `-c1` and `-c1-s2`
  folders only and refuse once `-c1-s3` is in their tree. Before the data commit, read whether E194's card lane has passed its step 2 (or landed a note naming `-c1-s3`) and say which in
  the result; the orchestrator orders the two days. The third session's data commit itself follows the kit as written.

## 2. The steps, in order (paths under `tools/claims-v3/e191/`; run from the lab clone's top)

Setup as the brief's section 2 (RB_OUT new, RB_LOCK, RB_GITLOCK, the GNU date shim, git reads over HTTPS by the environment rewrite; a
printed login link stops the step, 11, nothing retried).

| # | the step | what to do with its exit |
|---|---|---|
| B | `bash W/book.sh take aifoundry1 <lane>`: **its time is G3** | 1: another lane holds the box: stop |
| 0 | THE LOAD RULE; `check_day2_v2.py tree --pull` under the lab-git lock; the anchor lines as kit note 3's LAND.md states them | any line not as stated: no box step today |
| H | `bash W/hold.sh add <lane>` | as the brief |
| 1 | `rb/s02_window_e191.sh <day> <last start> <last end>` from G3 (section 1) | first; a new RB_OUT |
| 2 | **`rb/s03_desk_e191_v3.sh`** with `RB_GITLOCK`, under slot.sh, THE LOAD RULE first, never inside the lab-git lock (v2's step 2 now stops at its never-run checks: never run it) | anything but 0: no box step today; a `never-ran(a)` naming a folder: read it, report it, no session before a dated note |
| 4 | the look, `rb/s05_look_e191.sh` | FREE on both cards; HELD: `--wait` (30 minutes in all); 16: no launch |
| 3 | the post: **waived** (section 1) | record it |
| 5 | `rb/s07_a1_sync_e191_v2.sh` | 0 with "HARNESS OK and HARNESS-V2 OK on the box"; 10: a session or job of ours on the box; 16: uncommitted synced paths or a file off its sha256 |
| 6 | `rb/s08_a1_build_e191.sh start`, then `wait` (again while it says 17) | start: 0 with "E191-BUILDS-TODAY 0" and the job started; wait: 0 with RB_OUT/e191-built.txt "ledger,spp" (or what that day built: the other SKIPPED); 16 neither built: one more start that day only if this was its first; "both programs were built today" (10): that day's build exists, run the wait alone |
| 7 | `rb/s09_a1_reads_e191.sh`, after the rest has opened | as the brief (its one re-run after the look reads FREE again) |
| 8 | `rb/s10_a1_dry_e191_v2.sh start`, then `wait` | 0 with `E191-DRY-V2 rc=0 passes=6 dry-check=1 identity-lines=2 note2=1 runtime-dropped=n` (n at least 1) |
| 9- | before step 9 v3: step 10 v2's pattern (`ours_live "session_${RUN}*.sh"`, RUN=e191) matches step 9 v3's launch line (`setsid nohup bash tools/claims-v3/e191/session_e191_v2.sh`) | a mismatch: stop and report |
| 9 | **`rb/s11_a1_session_e191_v3.sh FULL`** | 0 launched ("last launch: ... the second session's T0", the rest line, "A2's third session, a REPEAT" in the LAUNCHED line); 10 refused (the rest, a session or job of ours, no a1-dry-e191-v2 today, an RB_OUT whose launch sent a card command, a second refused launch, or THE LAST LAUNCH: the box's last E191 launch is not the one this RB_OUT knows, with none the second session's 1794780355): read why, never around it; 16 IDENTITY-STOP: no launch; **14: the launch may have gone out with its answer lost: run no step 9 again before the box is read, read-only (`build/q141k/e191.T0` and that T0's `session.log`), and reported** |
| 10 | `rb/s20_wait_e191_v2.sh`, again while it says 17 | as the brief's note 1 (0; 16 GATE-STOPPED; 16 BOUND-SEEN: report at once, kill nothing, keep the booking; NOTE2-SESSION must read yes); **a GATE-STOPPED whose log reads "no device opened": THE RELAUNCH RULE** |
| 11 | **`rb/s22_collect_e191_v3.sh`** (no release: no post) | 0 COLLECTED into `docs/reports/data/<day>-e191-blind-day-aifoundry1-c1-s3/`; 10: an earlier session's T0, an `-s3` already there, not a kit note 2 session, or the directory exists; 16: COPY-BACK not exact, the scrub, the desk-path gate or the history check: commit nothing |
| 12 | the README (section 3), `rb/readme_check_e191.py <the -s3 directory>` (README-CHECK-E191 OK), the public-text scan, then `LAB_QUIET_HOLD_OWNER=<lane> bash W/commit_lab.sh "<subject>" "<body>" docs/reports/data/<day>-e191-blind-day-aifoundry1-c1-s3` | "COMMIT_LAB: pushed <sha>"; on 5 or 6 run it again |
| 13 | after the data commit only: **`rb/s24_score_e191_v3.sh`** | READ its "scored:" and "repeat:" lines (it exits 0 whatever they say; the words are REPORTED, never verdicts); 16 when the second record's re-derived output is not `23484c4f...`: report it, set nothing beside the verdicts; a records lane commits the three outputs beside the `-s3` data |
| E | `bash W/hold.sh remove <lane>`; `bash W/book.sh release aifoundry1 <lane>` | on every stop path too (a BOUND: keep the booking until the orchestrator says) |

**THE RELAUNCH RULE** (kit note 2, section 7), unchanged: a launch whose session log reads "no device opened" is not a session; after the
look reads FREE again, step 9 v3 once more from the same RB_OUT inside the same window; a second refused launch ends the day. A session that
sent a card command and then stopped at a gate is the third and last E191 session: collect it, commit it, no fourth.

**THE EARLY STOP** is the brief's, with runner v2's process: a SIGTERM only to the process whose command line runs
`tools/claims-v3/e191/run_e191_v2.py session --t0 <T0>` (never `session_e191_v2.sh`, never the process group), or the stop file
`nekko/build/e191/T<T0>/STOP` written by the brief's one bounded ssh call.

## 3. The data README for the third session (step 12)

From `rb/data-readme-form-e191.md` (unchanged), with the brief's note 1 section 3 differences, and these:
- **the directory** is `docs/reports/data/<day>-e191-blind-day-aifoundry1-c1-s3/`; the title names E191, aifoundry1 card 1, the day and
  **"the third session (E191.md's dated amendment A2), a REPEAT: its scorer output REPORTED beside the registered verdicts, which are the
  second session's"**; the paragraph names A2's and kit note 3's land commit beside the registration, note 1, the kit and note 2;
- **Registered against happened** adds A2's rows (the window from G3, the build rule, the rest since the last session of ours on aifoundry1,
  the one third session);
- **Departures and notes** name: A2 (the third session as a repeat, its window from G3, the build rule); his standing words with their times
  and the post waived; both earlier records, used by no gate of this session; any refused launch (its T0 and line) under the relaunch rule;
  "not blind to the second session's data" (A2's own label), and the frozen forecasts blind to every E191 datum;
- **Next** names step 13 v3's three outputs (`scores-e191-s3.json`, REPORTED; `scores-e191-s2.json` at the registered bytes;
  `repeat-e191-s3.json` and `.txt`) and says that **E191's verdicts are the second session's and stand**;
- **the means of the passes table are desk arithmetic, not verdicts,** as in the second record; no forecast is set beside them in the README.

## 4. Never (in addition to the brief's section 3 and note 1's section 4)

- Never v1's or v2's step 2, 9, 11 or 13 in this session; never a third build start in a day; never runner v1 or session v1.
- Never a fourth E191 session; never into the first or second session's directory, and never an edit of either record.
- Never call the third session's words verdicts, never pool its passes with the second session's, never read either earlier session's readings
  for any gate of this one.

## 5. Labels

Every figure here is **registered** (E191.md, its note 1, A1, A2) or a **desk check of code** (KIT.md, kit notes 2 and 3). Nothing here is
measured, blind, held out or post hoc. Not blind to the second session's data (A2's label).

SPDX-License-Identifier: Apache-2.0
