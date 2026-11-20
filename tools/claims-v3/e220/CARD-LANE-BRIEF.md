# E220's card-lane brief: MM1-v3.2's card-transfer blind day, arm A on aifoundry1 card 1 and arm B on aifoundry2 card 0 (Q233; kitted, not run)

*Fri 20 Nov 2026 (week 47), PST, on aifoundry2, desk only (Q233, lane `kit-e220`), beside [KIT.md](KIT.md). The registration is
[E220.md](E220.md), found by content (the commit that added it; its subtree `46dde0fd...`; `SHA256SUMS-e220-registration` `dc5d053f...`, 29
entries). No card was claimed or opened, no device command was sent, nothing was posted, no E220 datum exists. This brief changes no forecast,
band, rule, threshold, the order, the card time, the cap, a stop or the scorer.*

**fix-e220 (Fri 20 Nov 2026, before any E220 datum; verify-e220's findings; KIT.md section "fix-e220"):**

- **Step 6n reads dated note 1** (`tools/claims-v3/e220-notes/E220.md.dated-note-1.md`, landed with the registration; the orchestrator's ruling
  1). A point is labelled 'ran before' only by a session record on the arm's card. Desk copies in folders naming no card never count. The
  literal reading is REPORTED in the judgement, never a label. At the desk (11:25 PST) both arms read every point never run.
- **Row R reads E221's real release form**: a RELEASE line with no `ended HH:MM:SS` ends its session at the post's own time. It is never a
  comment, and with no day it is refused (16).
- **Step 13 prints every CX-E / CXP-E (and CX-T / CXP-T) verdict beside dated note 1's false rates**:
  `python3 -I -B tools/claims-v3/e220-notes/cx_null_e220_note1.py beside <the scorer's .json>`.
- **No SIGKILL toward a device process** (section 6 says exactly what is and is not sent).
- **Arm A's row E is by hand, in full, on every stop path** (below).

**Two card lanes, each its own booking, its own G and its own RB_OUT, named exactly `card-e220a` (arm A) and `card-e220b` (arm B):** the
registration's never-run scanner subtracts any path holding `-e220-` and the folders `W/out/card-e220*`, so any other name would be read as a
record of E220's own points. The data directories are `docs/reports/data/<day>-e220-blind-matmul-aifoundry1-c1/` (arm A) and
`docs/reports/data/<day>-e220-blind-matmul-aifoundry2/` (arm B).

- **Arm A**: aifoundry1 card 1 at 600 MHz as found, in E215 arm B's kit form as amended by E213's A2 and A3: **step 4 is fwgate's identity gate
  on the box's present boot** (`a2/rb/s05_look_e220a_a2.sh A`: one firmware-revisions READ on NEEDS-READ, both cards' locks held for it), **step 9
  launches only behind fwgate's guard on this boot** (`a2/rb/s11_session_e220a_a2.sh A`), **step 12 commits the read's folder**
  (`a2/rb/s23_data_e220a_a2.sh A`); **the G block runs last** (A3: E220's registered order already is: s03 at run 087, the 26 G runs after it);
  ET_DEVICES=1 on every device process, card 1's lock, **nothing on card 0**, one session at a time on aifoundry1; **THE REST RULE reads the
  model session's ~/claude/work/ee-*/ on aifoundry1** (no write there within the last 40 minutes, beside 40 minutes after the last session on
  either card). The k6 runbook (`../q141k-runbook/k6/`, unchanged) runs every box step from aifoundry2 over ssh.
- **Arm B**: aifoundry2 card 0 under its governor at 799 MHz (route c), in E216's kit form: THE DESK AND THE BOX ARE ONE MACHINE, every step a
  local script (`rb/*_e220b.sh`); **THE QUIET DESK FLAG** `W/locks/quiet-desk-aifoundry2` is raised only once arm A's card lane has passed its
  launch line (its `e220a-T0-A.txt` written after its booking) and is lowered on every path (step 11 after the copy-back, or `rb/end_e220b.sh`);
  **E216's copy-and-guard route for E212's release record, made a kit tool**: `rb/releases_e220b.py make` writes the round's release records
  in the rest rule's form and steps 7 and 9 run its guard.

## 1. What the go carries (E220.md 6)

The owner's standing words as E220.md 6 records them, with E220's registered items as defaults, once E220 is registered, kitted, verified,
landed and readiness-checked; the readiness lane's go lines name the anchor lines of the kit's land (step 2's own sha256 for each arm among
them), the round's records (`W/out/orch/sealed-e220.txt`, the release records), the other lane's launch marker path, and the queue.
**What runs beside E220 (the round's words):** Q234 freezes MM1-v3.3 candidates; the orchestrator holds both arms' bookings until its freeze
lines are posted, at most until 11:30 PST; **E221, the model session's sixth sweep, holds claims on aifoundry1**: arm A books nothing and makes
no ssh call to aifoundry1 while a claim stands (row B: QUEUE OVER first). Every seal the model session posts for E220 is registered in
`tools/claims-v3/sealed-e220/e220-freeze-lines.md` before either arm books (a later one in `e220-freeze-lines-2.md`, its record line a
COMMENT): each arm's step 0 reads both (arm A `rb/s00_step0_e220a.sh` S1, arm B `rb/s00_sealed_e220b.sh`).

## 2. THE ONE-LAB RULE and the two arms' order

- **Desk spans kept apart**: arm A's rows 0, H, 1, 2 inside `bash W/onelab.sh desk card-e220a` ... `undesk`; arm B's rows D+ ... D- inside
  `bash W/onelab.sh desk card-e220b` ... `undesk`. `onelab.sh desk` waits for another lane's span (bounded, 9 minutes a call): **run arm A's
  rows 0-2 first** when both lanes are ready at once (arm A's launch gates arm B's flag; arm B's step 2 holds its span for its scorer check).
- **Collect spans**: each arm's step 11 inside `bash W/onelab.sh collect <lane>` ... `uncollect` (arm B's step 11 refuses outside it).
- **Every stop path carries undesk (inside steps 0-2) and uncollect (between collect and the data commit's push)**: row E of each table.
  Arm B's `rb/end_e220b.sh` does both, lowers the flag if it is the lane's, removes the hold line and releases the booking; arm A's row E is
  the same four calls by hand (`onelab.sh undesk|uncollect`, `hold.sh remove`, `book.sh release aifoundry1 card-e220a`).
- **The order across the arms**: arm A's B, 0-2, 4-9 (its launch writes `RB_OUT/e220a-T0-A.txt`); arm B's O row waits for that marker
  (written after arm A's booking), then Q raises the flag. A booking of a card lane of ours that RB_LAUNCHED does not name is waited for; an
  orchestrator's hold (`orch-*`) is reported, never waited for.
- THE CPU RULE: every numerical step (each arm's 2, 6n, 11, 12-13) inside `W/slot.sh` with OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
  MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1, one slot job of a lane at a time; aifoundry2's 1-minute load under 6 through arm B's session (arm B's
  steps 7 and 9 gate on it: 17 while it is 6 or more, nothing sent).
- Every step is one plain call from a script file (no `bash -c`, no background `&`); every wait bounded (at most 9 minutes a call).

## 3. Arm A (card-e220a): aifoundry1 card 1, the k6 runbook with A2's steps 4, 9 and 12

Run from the lab clone (`cd $LAB`), ONE RB_OUT for the arm (a new directory outside the repo: `$W/out/card-e220a/rb-e220a`, so that arm B's
THE ORDER reads arm A's launch marker at `$W/out/card-e220a/rb-e220a/e220a-T0-A.txt`), the one `RB_LOCK` (the round's file of login
checks), `RB_GITLOCK` (the lab-git lock) for step 2, `E220A_ROUND_OUT` (the round's OUT) for step 6n. k6's exit codes: 0 done; 10 refused; 11
a login link (appends `<HH:MM:SS> aifoundry1 needs a check` to RB_LOCK; nothing retried until cleared); 12 no answer; 13 past a bound; 14 a
call failed; 15 a holder for 30 minutes; 16 a gate says stop; 17 call again. The dry listing: `a2/logs/dry-listing-a2-A.txt` (A2's steps in
place) beside `logs/dry-listing-e220a-A.txt` (the kit's own files).

| # | the step | what to do with its exit |
|---|---|---|
| B | the queue for aifoundry1 (the go lines' chain: wait in bounded chunks until QUEUE OVER; while QUEUE BUSY or CANCELLED - E221's claim - book nothing and make no ssh call to aifoundry1); `bash W/book.sh show` (an `orch-hold-*` line: wait, never book over it); then `bash W/book.sh take aifoundry1 card-e220a` | 0 BOOKED: G = this moment; 1: wait (bounded) or stop |
| 0 | `uptime` first, outside the span (THE LOAD RULE: above 8 wait in chunks of at most 9 minutes until below 6, at most 60 minutes); `bash W/onelab.sh desk card-e220a`; the land's anchor lines (step 2's own sha256 among them); then `E220A_SEALED=W/out/orch/sealed-e220.txt bash rb/s00_step0_e220a.sh A` (S0 GitHub main and HEAD; F1 MM1-v3.2's land an ancestor; F1R the registration commit (subtree 46dde0fd) in HEAD; **S1 THE SEALED-FORECAST CHECK**; D0 no arm A datum; G1 the lab clone clean) | "STEP0-E220 arm A: 6 of 6 as stated"; anything NOT AS STATED: no step that day, **E (with undesk)**, tell the orchestrator |
| H | `bash W/hold.sh add card-e220a`; `git -C $LAB status --porcelain --untracked-files=all` reads 0 lines | not 0: **E (with undesk)** |
| 1 | `bash rb/s02_window_e220a.sh A <YYYY-MM-DD> <last start HH:MM> <last end HH:MM>` (today, from G) | "fits now"; "fits now: nothing": **E (with undesk)** |
| 2 | FIRST `sha256sum rb/s03_desk_e220a.sh` equals the land record's step-2 anchor line (step 2 sits outside the kit's list); then `RB_GITLOCK=<the lab-git lock> bash W/slot.sh bash rb/s03_desk_e220a.sh A`, never inside the lab-git lock. **It runs no registered maker**: the registration's checks in their `--check` form, the frozen scorer's two self-tests through `rb/scorer_check_e220.py` into RB_OUT only (byte-compared with the committed outputs), the timeout table's check, the preflight, the logs; at its end it reads that no file of E220's folders or MM1's was written; then `bash W/onelab.sh undesk card-e220a` | 0: undesk, go on; 16: read RB_OUT's words, **E (with undesk)** |
| 4 | **A2: `bash a2/rb/s05_look_e220a_a2.sh A`** (the A2 form's pins at the desk, k6's holder rule with `--wait` - k6's continuity identity is NOT read: aifoundry1 booted after E82's firmware read -, A2's box files synced and checked, fwgate's look; on NEEDS-READ, in one bounded call, THE REST RULE first, both cards free by `et-who --check`, then ONE `fwgate.py read --box aifoundry1 --card 1 --both-nodes-ok`, EQUAL or the day ends) | 0 (EQUAL or CONTINUITY: the look file `A2-LOOK-A`); 16: no read and no launch on this boot, report, **E**; 10 with the rest's words: wait, call again |
| 3 | the post: none, by the owner's standing waiver (E220.md 6 records his words) | |
| 5 | `bash rb/s07_sync_e220a.sh A` | 0 HARNESS OK on the box; 10 or 16: read why, **E** |
| 6 | `bash rb/s08_build_e220a.sh A start`, then `... wait` while 17 | 0: RB_OUT/e220a-built-A.txt (both kernels KERNEL OK at their WHOLE ELF and "the hosts and /opt/et/lib/libdeviceLayer.a carry ET_DEVICES"); 16: start once more (two starts a Pacific day at most; a third: NO-THIRD-BUILD, no session that day: **E**) |
| 6n | `E220A_ROUND_OUT=<the round's OUT> bash W/slot.sh bash rb/s06n_neverrun_e220a.sh A` (the registration's scanner and report at their pins through `desk/neverrun_card_e220.py --arm A`; E220's own folders subtracted) | 0: its `NEVER-RUN-E220 arm A: ... by dated note 1's reading ...` line (REPORTED, never a gate: a point with a SESSION RECORD ON aifoundry1 card 1 among its hits is labelled 'ran before' in `labels-e220-A.json`, which step 13 passes to the scorer, and goes in a dated note before the data commit; the literal reading's count is REPORTED on the same line and in `judge-e220-A.json` > `literal_reading_REPORTED`, never a label: at the desk it read 52 desk-only points of 84) |
| - | WAIT until THE REST has opened: 40 minutes after the last session on aifoundry1 (either card, ours or the model session's) AND no write under the model session's `~/claude/work/ee-*/` on aifoundry1 within the last 40 minutes; 6n again if its report passes 30 minutes | |
| 7 | **STEP 7's config read ONLY ONCE THE REST HAS OPENED, within 30 minutes of 6n**: `bash rb/s09_reads_e220a.sh A` (the report's age and the rest rule on the box first, no card command; then the card-1 read through `ettelem_guard_e220a.sh` with ET_DEVICES=1 under `flock -n /run/lock/etsoc-shire1.lock timeout 10`) | 0: TDP 65 W / 65 C / 600 MHz, minion_mv below 510, /dev/et1_mgmt and physical ID 1 alone, et-who clean on both cards; 10 "the rest has not run": wait in bounded chunks, again (never around it); 16: no session that day, set nothing, **E**; 17: the look again |
| 8 | `bash rb/s10_dry_e220a.sh A start`, then `... wait` | 0: E220-DRY arm A rc=0 and THE SCRUB CHECK on the dry pass's own records CLEAN; 16: no session today, **E** |
| 9 | **A2: `bash a2/rb/s11_session_e220a_a2.sh A`** (the kit's step 9 but for the guard: A2's pins on the box, then `fwgate.py guard --box aifoundry1 --card 1 --extra <the read's folder>`) | 0 launched: **its T0 in RB_OUT/e220a-T0-A.txt (arm B's flag waits for this marker)**; 16 IDENTITY-STOP: nothing launched, report, **E**; 10: read why (HUNG marker, same-day rule, no 6n today), **E** if the day cannot go on |
| 10 | `bash rb/s20_wait_e220a.sh A` while 17 | 0 ended; 16 HUNG: KILL NOTHING, reset nothing, keep the booking and the hold, collect (11), escalate; 16 K1 or CRASHED: collect, report; 14: read the box read-only |
| 11 | `bash W/onelab.sh collect card-e220a`; then `bash rb/s22_collect_e220a.sh A` (at least 10 minutes before the last end) | 0 COPY-BACK EXACT; 16 NOT EXACT: commit nothing, **E (with uncollect)**; any other exit: `uncollect` at once, wait outside the span, again (at most 3 tries in 60 minutes) |
| 12 | **A2: `bash W/slot.sh bash a2/rb/s23_data_e220a_a2.sh A`** (the kit's step 12, then the read's folder as `fwgate/`): the data directory `docs/reports/data/<day>-e220-blind-matmul-aifoundry1-c1/` (or a gate stop's record under `docs/reports/gate-stops/`), the scrub, the reducer, step 6n's report, judgement and labels, the README in [DATA-README-FORM-e220a.md](DATA-README-FORM-e220a.md)'s form; the public-text scan; `LAB_QUIET_HOLD_OWNER=card-e220a bash W/commit_lab.sh ...`; then `bash W/onelab.sh uncollect card-e220a`, `bash W/hold.sh remove card-e220a`, `bash W/book.sh release aifoundry1 card-e220a` | "COMMIT_LAB: pushed <sha>"; a failure after its retries: move the directory out of LAB (checked against SHA256SUMS), **E (with uncollect)** |
| 13 | after the data commit only: `bash W/slot.sh bash rb/s24_score_e220a.sh A`; then (dated note 1, F3) `python3 -I -B tools/claims-v3/e220-notes/cx_null_e220_note1.py beside RB_OUT/scores-e220-A.json` and its lines in the lane's result beside every CX verdict | LABELS-OK, then the frozen scorer: RB_OUT/scores-e220-A.json and .txt (arm A's R0, S6, T1-T3, E1-E4, H1-H10, CX-T, CX-E; arm B's and the pooled rules NO DATA there); `CX-BESIDE-E220-NOTE1: ...` |
| E | every path ends here: `undesk` if inside 0-2; `uncollect` if between 11's collect and the push; then `hold.sh remove card-e220a` and `book.sh release aifoundry1 card-e220a` (on a HUNG or K1 day keep both until the owner or the orchestrator answers). **fix-e220 (verify-e220's F5): arm A has no end script, so these calls are by hand; before the lane returns, `bash W/onelab.sh show` must list no `desk-card-e220a` and no `collect-card-e220a` flag (a missed undesk blocks arm B's collect and every desk commit of the round)** | |

## 4. Arm B (card-e220b): aifoundry2 card 0, E216's runbook form

    W=<the round's workflow folder>; LAB=<the shared lab clone>; LANE=card-e220b
    mkdir $W/out/$LANE/rb-e220b and $W/out/$LANE/box-e220b      (new and empty: arm B's own RB_OUT and box root)
    python3 -I -B tools/claims-v3/e220/rb/releases_e220b.py make $W/out/orch $W/out/$LANE/releases-<HHMMSS>   (row R: prints RB_RELEASES=...)
    export RB_OUT=$W/out/$LANE/rb-e220b E220B_ROOT=$W/out/$LANE/box-e220b RB_QUIET=$W/locks/quiet-desk-aifoundry2 RB_LANE=$LANE
           RB_RELEASES=<the line row R printed> RB_ROUND_OUT=$W/out RB_W=$W RB_GITLOCK=$W/locks/lab-git.lock RB_SEALED=$W/out/orch/sealed-e220.txt
           RB_LAUNCHED=card-e220a=$W/out/card-e220a/rb-e220a/e220a-T0-A.txt      (arm A's RB_OUT as section 3 names it; the ready
           lane confirms the path from card-e220a's go lines; a booking of a card lane of ours not named here is waited for)
    NEVER set RB_DESKTEST, RB_FWGATE, RB_GITHUB, RB_HOME_WORK, RB_NOW, RB_DATA_LAB, RB_BOOKS, RB_LOAD, RB_E220B_KITPIN, E220B_DESKTEST,
    MMS_FAKE_*, E220B_FAKE_* or E220B_SI_*: they are the desk tests' (each step refuses the RB_ ones outside a desk test).

**THE ORDER: R, B, D+, 0, H, 1, 2, D-; O, Q; 5, 4, 6, 8, 6n; once the rest has opened and within 30 minutes of 6n, 7 and 9 back to back; 10,
4', C+, 11 (with Q-), 12, C-, 13, E.** Step 7 sends the day's first card command only when fwgate's look reads NEEDS-READ (one
firmware-revisions READ); on CONTINUITY step 9's own config read is the first. Exit codes: 0 done; 10 refused; 13 past a bound; 14 a call
failed; 15 a holder; 16 a gate says stop; 17 call again.

| step | call | expected | any other exit |
|---|---|---|---|
| R | `python3 -I -B rb/releases_e220b.py make $W/out/orch <a new folder>` (every `W/out/orch/*releases*.txt` copied in the rest rule's form: E212's S3 re-run line as E216's copy wrote it, a `#` line with a day and an end followed by its rule-form line, **E221's real release form - `RELEASE aifoundry2 card 0: E221 a2c0-Sk ended (runner rc 0, ...)` with no `ended HH:MM:SS` - followed by a rule-form line whose end is the post's own time (fix-e220, verify-e220's F2), never a comment whatever other words it holds**, a claim or proposal kept as a comment) | `RELEASES-E220B: MADE <n> records ...` and the RB_RELEASES line | 16 UNCLASSIFIED: a line naming aifoundry2 card 0 the tool cannot read: nothing written; a person reads the line; no session until it is read |
| B | `python3 $W/out/orch/queue_state.py aifoundry2` (QUEUE OVER), then `bash $W/book.sh take aifoundry2 $LANE` | BOOKED; G = this moment | BUSY or CANCELLED: wait (bounded) |
| D+ | `bash $W/onelab.sh desk $LANE` (right before step 0; arm A's rows 0-2 first when both are ready) | in its desk span | 3: call again |
| 0 | `uptime` (THE LOAD RULE); GitHub main read; the land's anchor lines (step 2's own sha256 among them); then **S1** `RB_SEALED=$W/out/orch/sealed-e220.txt bash rb/s00_sealed_e220b.sh` | "SEALED-E220: sealed k of k registered" | 10 (a seal NOT REGISTERED, or a record that cannot be read): D-, E, tell the orchestrator |
| H | `bash $W/hold.sh add $LANE`; `git -C $LAB status --porcelain --untracked-files=all` | 0 lines | D-, E |
| 1 | `bash rb/s02_window_e220b.sh <G epoch>` | "the window written to RB_OUT/window.env" | 10: D-, E |
| 2 | FIRST `sha256sum rb/s03_desk_e220b.sh` equals the land record's step-2 anchor line; then `bash $W/slot.sh bash rb/s03_desk_e220b.sh` (never inside the lab-git lock; outside a desk test it refuses unless D+ holds the span). **It runs no registered maker**: the frozen scorer's two self-tests through `rb/scorer_check_e220.py` into RB_OUT/scorer-check-B/ only | "STEP2 PASS (HEAD <sha>)" | a different sha256: not run, D-, E; 10: D-, E (RB_OUT/step2.txt) |
| D- | `bash $W/onelab.sh undesk $LANE` (right after step 2, and on every stop path from D+ to here) | left its desk span | |
| O | `bash rb/quiet_e220b.sh others --wait` while 17 (**THE ORDER: card-e220a's launch marker written after its booking**) | "THE ORDER: every other card lane of ours ... has passed its launch step" | 17: again in bounded chunks, at most until the window's last start less 40 minutes, then E |
| Q | `bash rb/quiet_e220b.sh raise $LANE`, then `bash rb/quiet_e220b.sh count --wait` (THE P2 COUNT 0) | raised (`card-e220b <time>`); P2 0 | raise 10 (another's flag up): wait, never overwrite; 17: O again |
| 3 | the post: waived | | |
| 5 | `bash rb/s07_sync_e220b.sh` | SYNCED at the harness's sha256 | 10: read why; 14: again |
| 4 | `bash rb/s05_look_e220b.sh [--wait]` | 0 FREE; the reboot gate CONTINUITY or NEEDS-READ | 17 or 15: again with --wait; 16: no session on this boot, Q-, E |
| 6 | `bash rb/s08_build_e220b.sh start`, then `... wait` while 17 (E208's build_mms.sh, then E220's build_e220b.sh: rgm211's host) | "MMS-BUILT and E220-BUILT" | 16: start once more (two a day); an E220-BUILD-FAILED: family G cannot run today: tell the orchestrator, never run around it |
| 8 | `bash rb/s10_dry_e220b.sh start`, then `... wait` while 17 | "DRY PASS" (103 of 103 runs in the registered order, 106 processes gated OK, the 17 G processes on rgm211's host's double, every host call under its sized plain timeout) | 16: no session that day |
| 6n | `bash $W/slot.sh bash rb/s06n_neverrun_e220b.sh` | its `NEVER-RUN-E220 arm B: ... by dated note 1's reading ...` line (REPORTED; a point with a session record on aifoundry2 card 0 among its hits is labelled; the labels in RB_OUT/ranbefore-e220b.json reach the scorer at step 13; the literal reading REPORTED beside, never a label: at the desk 42 of 74, 41 desk-only and xy03b) | 14: again |
| - | WAIT until the rest has opened (40 minutes after the last session on aifoundry2 card 0 ended; E216's ended 17:23:32 PST Thu 19 Nov 2026; any later one counts) | | |
| 7 | `bash rb/s09_reads_e220b.sh` (THE RELEASE-RECORDS GUARD first: the round's records unchanged since row R, else 16) | "the first card command stamped ...: step 9 within 120 s" | 17 REST NOT OPEN or THE CPU RULE's load: wait, again (nothing sent); 16 (the guard, fwgate DIFFERENT or UNREADABLE, a rest source unreadable): no session on this boot, Q-, E (a changed record: row R again, then 7) |
| 9 | `bash rb/s11_session_e220b.sh` AT ONCE (the guard again) | "STARTED <T0>-a2c0-E220" | 10 "more than 120 s": step 7 again; 16 IDENTITY-STOP: report; 17: again within the stamp's 120 s |
| 10 | `bash rb/s20_wait_e220b.sh` while 17 | 0 ENDED, runner rc 0 | 16: read its words (a gate stop, a KERNEL STOP, an IDENTITY GATE STOP, a LEFTOVER, GONE); 14: again |
| 4' | `bash rb/s05_look_e220b.sh` once the session has ended | 0 FREE | 15: read who holds it; kill nothing |
| C+ | `bash $W/onelab.sh collect $LANE` | in its collect span | 3: again |
| 11 | `bash $W/slot.sh bash rb/s22_collect_e220b.sh` | "DATA DIR docs/reports/data/<day>-e220-blind-matmul-aifoundry2 written; THE QUIET DESK FLAG lowered after the copy-back" | 14 NOT EXACT: read why; 16 THE SCRUB: nothing in LAB, Q-, C-, E |
| Q- | done by step 11 after the copy-back; on every stop path after Q (`bash rb/quiet_e220b.sh lower $LANE`) | lowered | 10: not ours: leave it |
| 12 | the README's dated notes; the public-text scan; `LAB_QUIET_HOLD_OWNER=$LANE bash $W/commit_lab.sh ...`; then hold remove and booking release | "COMMIT_LAB: pushed <sha>" | after the retries: move the directory out of LAB, E with uncollect |
| C- | `bash $W/onelab.sh uncollect $LANE` (right after the push, and on every stop path from C+ to here) | | |
| 13 | `bash $W/slot.sh bash rb/s24_score_e220b.sh` (after the data commit only) | the manifest read (1 line by THE MASK), the reducer rc 0, LABELS-OK when labels name points, the frozen scorer (`score_e220.py --b`), then `post_e220b.py after` (REPORTED: points with no route-c reading by family, the session's stop); then (dated note 1, F3) `python3 -I -B tools/claims-v3/e220-notes/cx_null_e220_note1.py beside RB_OUT/score/scores-e220.json`, its lines beside every CX verdict in the lane's result | 10: not committed or a label names nothing; 14: read why |
| E | `bash rb/end_e220b.sh` on every path's end: the flag lowered if the lane's, the desk or collect span left, the hold removed, the booking released | "E: ..." | 17: a session of ours still runs or a leftover stands: nothing released |

## 5. Stops (each ends with E; nothing is ever killed)

- **Arm A** (E220.md 3 and 6): the board above 72 W on 3 samples in a row, the die 80 C; the die gate min(63, rest + 3) C; the drop line 69 W;
  the rule 60 minutes, the cap 70. **Arm B**: the board above 70 W on 3 samples, the die 70 C, the latch 70 C once risen; the die gate 55 C for
  at most 180 s; the drop line 67 W; the rule 60, the cap 70.
- **THE KERNEL STOP** (a G process's walk check, its check of C, a tensor error, a launch timeout) and **THE IDENTITY GATE STOP** (a process's ELF
  not its family's) end the session; nothing further starts. Arm A's gemmLnc smoke s03 has its own stop path (a failure drops the family alone);
  on arm B a failed s03 is a KERNEL STOP at run 087 and the G block never starts. An s03 failure while no gemmLnc point ran is never counted in
  R0 (E220.md 3); on arm B the frozen scorer reads s03 as no registered point (it is not among its flags) and step 13's readings REPORT the stop.
- **THE PLAIN TIMEOUT**: `timeout 10` on every host but xf04's (`timeout 13`, both arms: `desk/timeouts-e220.json`), never `-k`. A host past its
  TERM is a LEFTOVER (arm B) or HUNG (arm A): KILL NOTHING, keep the booking, the hold and the flag, report.
- To stop by hand: arm A `touch build/e220a/T<T0>-A/STOP` on aifoundry1; arm B the box root's `src/stop_mms.sh a2c0 <sid>`. Never a signal to
  a host or the sampler.

## 6. Never

- **No SIGKILL toward a device process** (fix-e220, verify-e220's F4; `logs/nokill-e220.txt`: 0 lines that could send one).
  - No file of the kit, A2's or E208's runner sends one, and every device process runs under its plain `timeout 10` or `13` (SIGTERM only).
  - The one SIGKILL in the code the kit runs is k6's `q141k-runbook/v3.1/rb_run.py` `kill_tree()`. Past a call's bound, or on a login link,
    it sends TERM and then KILL to that call's own local process tree on the desk: aifoundry2's ssh client, rsync, git or desk Python, for
    arm A only.
  - Arm A runs no device process on aifoundry2, and arm B's runbook does not use rb_run.py.
- No `kill -9` or `timeout -k` of ours, no reset, no PCIe recovery, no driver reload, no power cycle, no firmware write, no OTA, no flash,
  no PMIC write, no governor, TDP, threshold or clock set, no statistics reset (each arm's guard refuses `sample --reset-ms`): dmcmd_audit_v2 GO
  on both arms' files with no allowance.
- On aifoundry1: nothing on card 0 (but the A2 form's one READ, both locks held), one session at a time, nothing while E221's claim stands.
- On aifoundry2: no `sys_emu`; while THE QUIET DESK FLAG stands no device-named process and no `session_eNNN*.sh` or `queue_eNNN*` of ours
  starts, and no desk test of this kit runs.
- Never step 2 inside the lab-git lock; never a registered maker in step 2; never edit, pull or commit in LAB by hand (commit_lab.sh only).
- No post anywhere but the orchestrator's; public text carries no login, home path, credential or NDA name.

## 7. What the go should know (none blocks)

1. **Arm A's real build cannot run at the desk** (this desk's device layer carries no ET_DEVICES): the build's desk test reads its refusal at
   the ET_DEVICES gate, and the real-path and runbook desk tests run the later steps on a stand-in record beside the real ELFs and hosts.
   aifoundry1's own build read the ET_DEVICES reading for E215 arm B and E213 arm B; a failure there is a dated note, never a way around.
2. **Arm B's s03 in the frozen scorer**: s03 is a smoke row (D1), not a registered point of arm B, so the scorer's arm B reader does not read
   its run; a failed s03 stops the session (THE KERNEL STOP) and leaves the G block NO DATA, REPORTED by `post_e220b.py after` (desk-tested).
3. **The real-path desk test of arm B runs at the real pace** (its MAIN case is the whole 103-run schedule): its log names each case's time.
4. **The release records**: E221's record writes every line as a `#` comment, which the rest rule skips; row R's copy adds a rule-form line for
   any such line that names aifoundry2 card 0 with its day and its end. **fix-e220:** E221's real release line names no end time
   (`#15.9.1 2026-11-20 10:55:47 PST: RELEASE aifoundry2 card 0: E221 a2c0-S1 ended (runner rc 0, ...)`). The kit's copy read it as UNCLASSIFIED
   (16) and would have stopped arm B at row R; with a no-end word in it, the line would have become a comment and the rest opened early. Row R
   now ends such a session at the post's own time: the rest then counts from 10:55:47 for a2c0-S1, opening 11:35:47 (desk, 11:01 PST).
5. **DECIDED (fix-e220): dated note 1 is the reading; the kit's step 6n applies it (the labels are a session record's on the card; the literal
   reading REPORTED). The original item follows, as kit-e220 wrote it.** STEP 6n MAY LABEL MANY POINTS (THE ORCHESTRATOR DECIDES BEFORE EITHER CARD LANE BOOKS). Since 07:38:29 PST E221's data lane holds a copy
   of its registration tree in `W/out/data-e221/work/reg-tree/` (no card named) whose config list and scan record name E220's shape tokens;
   by the registered literal reading each such token counts as run on every card, so step 6n labels those points 'ran before' and they leave
   every rule (the kit's final desk run: arm B 42 of 74; arm A in `logs/neverrun-desk-e220a.txt`). The judgement REPORTS which labelled points
   have desk files only among their counted hits. A card lane never edits a label by hand and never moves another lane's files: the
   orchestrator decides (a dated note before any datum, or the data lane's copy moved out of the lanes' folders) before step 6n is run.
