# E206's card-lane brief: what the lane that runs an arm of E206 (A: aifoundry3 card 0; B: aifoundry1 card 1) does, step by step, and what it never does (Q198; kitted, not run)

*Mon 16 Nov 2026 (week 47), PST, on aifoundry2, desk only (Q198, lanes `kit-e206` and `fix-e206`), beside [KIT.md](KIT.md). The
registration is [E206.md](E206.md) with its amendment A1 (found by content: the commit that added it; its subtree `114c094b...`;
`SHA256SUMS-e206-registration` `d9fb06e4...`, 25 entries). No card was claimed or opened, no device command was sent, nothing was posted. No
E206 datum exists. This brief changes no forecast, band, rule, threshold, the order, the card time, the cap, a stop or the scorer. Each arm is
its own card lane (card-e206a, card-e206b) with its own booking, its own G and its own RB_OUT; the two arms, on two boxes, may run at the same
time (E206.md 6). **Fixed before the land (fix-e206, for the verifier's finding 8):** no wait inside a onelab span is unbounded (section 2,
"Waits inside a span"), and the operator's STOP file now stops the session as written (the runner reads it before every start).*

## 1. What the go must carry (E206.md 6)

- **The owner's go**, on the round's reading: his standing words of Sun 15 Nov 2026 ("continue, all machines are up", 10:05:42 PST; "don't
  worry about discord post, just use the machines, nobody is using them", 10:22:36; "Feel free to use more cards in parallel, I don't need to
  reserve them ..., feel free to use more in parallel", 17:21:16), "Try again" (received at or before 21:28:59) and "don't worry about hitting
  the limit, I will use a reset, feel free to run things overnight and in parallel" (at or before 21:51:09), and his matmul focus of Mon 16 Nov
  2026 (received at or before 09:48:24: "... just go as far as possible on the matte mold, on the FME, yeah, on the matmul operation"), with
  E206's registered items as its defaults, once E206 is registered, kitted, verified and readiness-checked. Record them as dated departures
  in the data README: the registered items as their defaults; G = the booking on its day; the post waived; the package counter not read; the
  desk aifoundry2 with Python 3.12.3; the yvb3 session.
- **Arm A**: aifoundry3 card 0 at its pinned 600 MHz (a boot-time TDP of 0 latches the governor), reads only, nothing set; **after E202's
  card day there** (the queue helper `python3 W/out/orch/queue_state.py aifoundry3 e202` reads QUEUE OVER); about 92.6 card-minutes, no run
  after 112, cap 120.
- **Arm B**: aifoundry1 card 1 at 600 MHz as found, ET_DEVICES=1 on every device process, card 1's lock, nothing on card 0 ever, one session
  of ours on aifoundry1 (either card, the model session's sweeps included: same login); about 87.6 card-minutes, no run after 112, cap 120.
  **Conditional**: while `W/out/orch/claim-aifoundry1.txt` exists the queue helper prints QUEUE CANCELLED (exit 4): return SKIPPED (cancelled
  by the orchestrator), book nothing, make no ssh call to aifoundry1.
- **The rest**: each arm's first card command (step 7's config read included) at least 40 minutes after the end of our previous session on
  that box, whatever its form (on aifoundry1, either card; the model session's folders `~/claude/work/ee-*/` count too). Read it by the
  clock from the last card lane's records BEFORE the booking; steps 7 and 9 read it on the box again.
- **The window**: G = this lane's booking of the arm's box that day; last start G + 1:30, last end G + 3:30, both rounded up to the minute,
  inside G's Pacific day; G at 20:29:00 PST or earlier. Step 9 needs 7,500 s before the last end, so the launch comes by G + 1:25.
- **The post**: none, by the standing waiver (record his words of 10:22:36). **The host's package counter**: not read.
- **The registration and the kit landed and in HEAD** (registration first, then the kit), no datum of this arm in any ref (step 2 refuses).
- **A sealed forecast** (E206.md 0): if `W/out/orch/sealed-e206.txt` lists a sealed sha256 for E206 that `tools/claims-v3/sealed-e206/
  e206-freeze-lines.md` at HEAD does not register, do not book: tell the orchestrator (the note lands first, under the desk-commit rule).
- **THE QUIET DESK FLAG on aifoundry2**: while the round's quiet-desk flag for aifoundry2 is up (a session on aifoundry2's own card), run neither step 9 (its file name holds
  `session_e206.sh`, which a text-matching session count on aifoundry2 would read) nor any desk test of this kit; wait in bounded chunks.

## 2. The steps, in order (paths under `tools/claims-v3/e206/`; `<arm>` is A or B, `<box>` aifoundry3 or aifoundry1)

Run from the lab clone (`cd $LAB`), ONE RB_OUT for this arm (a new directory outside the repo), the one `RB_LOCK` (the round's file of login
checks) and, for step 2, `RB_GITLOCK` (the lab-git lock). Each step one plain call from a script file. k6's drivers bound every remote call: a
15 s probe, then 60 s for a read, 600 s for a copy, one bounded wait (520 s), a detached launch that returns at once. **A printed login link
stops the step (11) and appends `<HH:MM:SS> <box> needs a check` to `RB_LOCK`:** nothing is retried until it is cleared, and a session
detached on the box keeps running. k6's exit codes: 0 done; 10 refused; 11 a login link; 12 no answer; 13 past a bound; 14 a call failed; 15 a
holder for 30 minutes; 16 a gate says stop; 17 call again. **E** is the end of every path (below): it carries undesk and uncollect where they
are due.

| # | the step | what to do with its exit |
|---|---|---|
| B | the queue (`python3 W/out/orch/queue_state.py <box> <the round's experiments>`: QUEUE OVER; QUEUE CANCELLED is SKIPPED, no booking), then the rest by the clock (section 1), then THE DAY (G at 20:29:00 or earlier); then `bash W/book.sh take <box> <lane>` | 0 BOOKED: G = this moment. 1: another lane holds it: make no ssh call to that box at all; wait (bounded) or stop (nothing else to undo) |
| 0 | `uptime` FIRST, OUTSIDE the span (THE LOAD RULE: above 8, wait in bounded chunks of at most 9 minutes until below 6, at most 60 minutes in all; past that, no box step that day: **E**); then `bash W/onelab.sh desk <lane>` (THE ONE-LAB RULE: steps 0, H and 2 never overlap another lane's collect span or a commit of ours; exit 3 at its 9-minute bound: call again, at most 6 calls, else **E**); GitHub main read; E206's anchor lines (the land record, `OUT/q198-anchor-lines-e206.txt`); the sealed-forecast check (section 1) | any line not as stated: no box step that day: **E (with undesk)** |
| H | `bash W/hold.sh add <lane>` (THE QUIET HOLD, one owner a line, until the data commit); `git -C $LAB status --porcelain --untracked-files=all` reads 0 lines | not 0: **E (with undesk)** |
| 1 | `rb/s02_window_e206.sh <arm> <YYYY-MM-DD> <last start HH:MM> <last end HH:MM>` (today only; G + 1:30 and G + 3:30, rounded up) | "fits now: an E206 session of arm <arm>"; "fits now: nothing": no box step: **E (with undesk)** |
| 2 | `uptime` (above 8: `undesk`, wait outside the span as in step 0, `desk` again, then this row again); then `RB_GITLOCK=<the lab-git lock> rb/s03_desk_e206.sh <arm>`, **never inside the lab-git lock**; then `bash W/onelab.sh undesk <lane>` | 0: undesk, go on. Anything else: no box step that day: **E (with undesk)**. Two exceptions, each bounded: a pull whose output shows the upstream did not answer: `undesk` at once, wait outside the span (chunks of at most 9 minutes; at most 3 tries in 30 minutes in all), `desk` again and run step 2 again, else **E**; a 16 naming HEAD-moved (a co-owner committed meanwhile): run step 2 again at once, at most 3 times, else **E (with undesk)** |
| 4 | the look, `../q141k-runbook/k6/s05_look_k6.sh <box>` (it writes the box-login file step 12's scrub reads) | FREE; a holder: bounded polls (`--wait`), at most 30 minutes, else no session that day: **E** |
| 3 | the day's post: **none**, by the owner's standing waiver of Sun 15 Nov 2026 10:22:36 PST; record his words | |
| 5 | `rb/s07_sync_e206.sh <arm>` | 0 HARNESS OK on the box; 10: a session or runbook job of ours on the box; 16: uncommitted synced paths or a file off its sha256: **E** |
| 6 | `rb/s08_build_e206.sh <arm> start`, then `... wait` while it says 17 | 0: RB_OUT/e206-built-<arm>.txt (KERNEL OK; on arm B "the host and /opt/et/lib/libdeviceLayer.a carry ET_DEVICES", else 16 and no session of arm B that day); 16: start once more (two starts a Pacific day at most; a third: NO-THIRD-BUILD, no session that day: **E**); a 14 on wait: no reading, wait again |
| 7 | **STEP 7 ONLY ONCE THE REST HAS OPENED**: `rb/s09_reads_e206.sh <arm>` (the rest rule on the box first, no card command; then the time stamped and the config read); then 8 and 9 **without delay** | 10 with "the rest has not run": wait in bounded chunks and run it again, never around it; 0: the config read as found and et-who clean; 16 (not as found, or arm B's read not card 1's): no session that day, set nothing: **E**; 17 (et-who not clean): step 4 with `--wait`, then step 7 again |
| 8 | `rb/s10_dry_e206.sh <arm> start`, then `... wait` | 0 (E206-DRY rc=0 runs=3: the doubles on the box, no device) |
| 9 | (the quiet-desk flag on aifoundry2 absent) `rb/s11_session_e206.sh <arm>` | 0 launched (its "rest:", "hung:" and "same-day:" lines in the runbook log; the T0 in RB_OUT/e206-T0-<arm>.txt); 10 refused (the rest; a session or job of ours; **a HUNG marker**: a device process of ours did not end after its timeout's TERM: stop, report to the owner, no session that day; the same-day rule; no dry pass or build today): read why, never around it: **E** if the day cannot go on; 16: past the last start, the cap would pass the last end, or aifoundry1's IDENTITY-STOP: **E** |
| 10 | `rb/s20_wait_e206.sh <arm>`, again while it says 17 | 0: ended, MANIFEST-WRITTEN, the runner exited 0 (read its `STOP:` line if one is printed: a stop line, a holder or two failed processes end a session rc 0); **16 HUNG**: KILL NOTHING, reset nothing, keep the booking and the hold, collect what is written (step 11), write it up and escalate to the owner; **16 K1-STOPPED**: a launch did not finish (it may leave a hung hart): collect it, never reset, escalate; **16 CRASHED**: read runner.out read-only, report, then collect; **16 GATE-STOPPED**: no run, still collected as a gate stop's record; 14: gone without "session end" or no runner.rc (read the box read-only first) |
| 11 | `bash W/onelab.sh collect <lane>` (exit 3 at its 9-minute bound: call again, at most 6 calls; the session's files wait on the box); then `rb/s22_collect_e206.sh <arm>` (start it at least 10 minutes before the last end) | 0 COPY-BACK EXACT; 16 COPY-BACK NOT EXACT (a HUNG process may still be writing its files): commit nothing, read why: **E (with uncollect)**. **Every other exit** (10 refused, 11 a login link, 12 no answer, 13 past a bound, 14 a call failed): `uncollect` at once (nothing is committed yet), read why, wait OUTSIDE the span (chunks of at most 9 minutes; after a login link only once `RB_LOCK`'s check is cleared), then `collect` again and step 11 again: at most 3 tries in 60 minutes in all, else **E**, the session's files left on the box untouched and reported |
| 12 | `rb/s23_data_e206.sh <arm>` (the data directory, or a gate stop's record, the scrub, the reducer, SHA256SUMS, the desk-path gate, the history check); the README in [DATA-README-FORM-e206.md](DATA-README-FORM-e206.md)'s form; the never-run search re-run (`desk/neverrun_e206.py`, REPORTED: which points the model session ran first); the public-text scan; `LAB_QUIET_HOLD_OWNER=<lane> bash W/commit_lab.sh "<subject>" "<body>" <the collected directory>` (new files only; on exit 5 or 6 run it again); then `bash W/onelab.sh uncollect <lane>`, `bash W/hold.sh remove <lane>`, `bash W/book.sh release <box> <lane>` | "COMMIT_LAB: pushed <sha>"; anything else after the retries: **E (with uncollect)**, the collected files kept in the lab clone untracked, reported |
| 13 | after the data commit only, never on a gate stop's record: `rb/s24_score_e206.sh <arm>` | the frozen scorer: RB_OUT/scores-e206-<arm>.json and .txt (R0, C1, S1-S4, S6 per model and arm; the summaries; the readings); read its words; a later lane commits them beside the data |
| E | **every path ends here**: `bash W/onelab.sh undesk <lane>` if inside steps 0-2; `bash W/onelab.sh uncollect <lane>` if between step 11's collect and the data commit's push; then `bash W/hold.sh remove <lane>` and `bash W/book.sh release <box> <lane>` (on a HUNG or K1 day: keep the booking and the hold until the owner or the orchestrator answers; release them then) | |

**Waits inside a span** (THE ONE-LAB RULE; fixed before the land for the verifier's finding 8): every wait in this table is bounded (at most 9
minutes a call, with each row's total), and no wait longer than one call happens inside a span: the load rule waits before `desk`; a step 2 or
a step 11 that must wait leaves its span first (`undesk`, `uncollect`) and enters it again before it is run again; past a row's bound the path
ends at **E**. Inside the desk span a lane holds only step 0's reads, H, step 1 and step 2 (k6's bounded drivers); inside the collect span, step
11 (its 600 s copy) and step 12 (commit_lab.sh's own bounds: its lock wait of 1,200 s, five push tries).

**To stop the session by hand** (the operator's stop, a registered stop): `touch build/e206/T<T0>-<arm>/STOP` on the box (the host ends at its
next launch boundary; the runner reads the file before every start, so nothing further starts: fixed before the land, the verifier's finding
1; a STOP file already there when the runner starts is a refusal, no device opened, the file kept), or SIGTERM to the runner (`run_e206.py`),
never to a host or the sampler. Never kill a process: the session ends its own processes and stops its sampler with SIGTERM.

## 3. After a gate stop, a registered stop, K1, HUNG or a crash

- **A gate stop** (no run: "refused, no device opened: ..." before any card command, or after the card opened: the start config, the
  identity gate, the sampler, the identity read, the smoke, the stop-path test) is **no session: no data**. Step 12 collects it as a gate stop's
  record under `docs/reports/gate-stops/`, never `docs/reports/data/`; commit it (new files only, its README in the gate-stop form); it is never
  scored. **The arm may be tried again with no amendment**: after a refusal that opened no device, **once more the same day**, once the look
  reads FREE again and inside the window (step 9 counts the tries: a third is refused); after a gate that came after the card opened, **not the
  same day** (step 9's same-day rule); a try on a later day needs that day's go and the rest. A gate stop by a kit defect is the kit's to fix:
  a dated kit note and, if it touches the registration, a dated amendment to E206.md before any datum, verified and landed, then a later
  session.
- **A registered stop** (the board or die lines, a holder, two failed processes, the card-time rule, the window's end, the operator's STOP or
  SIGTERM) after a run: the runs done stand and are scored as they stand; the data directory is committed; the missing runs are never re-run
  without a dated amendment.
- **K1** (a launch that did not finish) and **HUNG** (a device process still alive after its timeout's TERM): the session stops; the card may
  hold a hung hart: **never reset the card, no PMIC or power action, kill nothing** (the field manual's gates). Keep the booking and the
  hold, collect what was written (a HUNG process may keep writing its own files after the manifest: then the copy is not exact; commit
  nothing until a dated note decides), write it up, escalate to the owner and the lab admin. Step 9 refuses every later session of ours on
  that box while the HUNG line stands.
- **A crash** of the runner: named in its log ("CRASH: <type>: <message>"), its closing still run, runner.rc 1; step 10 says 16; report it,
  collect it (a crash with no run is a gate stop's record); never re-run around a crash without a dated note.
- **The runner gone without "session end"** (step 10's RUN-GONE): read the box read-only, collect what is there by a dated note's decision,
  report; the rest rule counts the session at its run's latest write.

## 4. Never

- No step 2 but `rb/s03_desk_e206.sh`, never inside the lab-git lock; no box step without step 2's 0 that day; no step out of the order above;
  **never step 7 before the rest has opened**; never steps 5, 6 or 8 while a session of ours runs (they refuse).
- No change to a forecast, a band, a rule, a threshold, the order, the card time, the cap or a stop except by a dated amendment before the
  data (E206.md, Amendments); no run re-run after a stop without one; the scorer only as registered and only after the data commit.
- No device command but the kit's READs (dmcmd_audit_v2 GO): no set, no reset, no governor, TDP, threshold, clock, voltage, fan or firmware
  change; no statistics reset; no PMIC write; no power cycle and nothing that risks one; **never kill a device process** (no SIGKILL, no
  `timeout -k`; a process that does not end after its TERM is reported at once and left).
- Never two sessions of ours on a box at once (on aifoundry1, either card); never beside another user's holder or device process (the
  session's et-who and ps refuse); **arm B never on card 0** (ET_DEVICES=1, card 1's lock, the identity gate, read and watch; an IDENTITY-STOP
  or any card-0 line: stop, never re-run that day).
- Never a lab user's login in any file (the collection's scrub masks ours; write `<login>`); no number from the owner's private pages or his
  A100 report in any lab file; no sealed forecast's number anywhere.
- Never touch another run's files on a box: E206 writes only `build/e206rgm/`, `build/e206/`, `build/e206-build-*` and the runbook's own
  `build/q141k/` entries, and step 5's synced files at their committed bytes.
- Never write in another lane's folder, booking, hold line or onelab flag; never answer a lane by a message (the orchestrator answers through
  files under `W/out/orch/`).

## 5. Labels

Every figure here is **registered** (E206.md) or a **desk check of code** (KIT.md). Nothing here is measured, blind, held out or post hoc.

SPDX-License-Identifier: Apache-2.0
