# E215's card-lane brief: what the lane that runs an arm of E215, MM1-v3.1's blind matmul day (A: aifoundry3 card 0; B: aifoundry1 card 1), does, step by step, and what it never does (Q224; kitted, not run)

*Thu 19 Nov 2026 (week 47), PST, on aifoundry2, desk only (Q224, lane `kit-e215`), beside [KIT.md](KIT.md). E213's card-lane brief
(`tools/claims-v3/e213/CARD-LANE-BRIEF.md`, landed in `6efdb002`: the brief E213 arm A ran FULL by on aifoundry3 card 0, data `c69a12aa`) for
both arms, with arm B in the form E213 arm B ran by on aifoundry1 card 1 (data `b0c727c5`): E213's **Amendment A2** (`tools/claims-v3/e213-a2/`,
landed `8b675547`: step 4 is fwgate's identity gate on the box's present boot, one firmware read on NEEDS-READ, fwgate's guard at step 9, the
read's folder committed at step 12) and **Amendment A3** (`tools/claims-v3/e213-a3/`, the same land: every gemmLnc point LAST - which E215's
registered order already is, so no order override is needed). The registration is [E215.md](E215.md) (found by content: the commit that added it;
its subtree `e89e512f...`; `SHA256SUMS-e215-registration` `99439f8f...`, 35 entries). No card was claimed or opened, no device command was sent,
nothing was posted. No E215 datum exists. This brief changes no forecast, band, rule, threshold, the order, the card time, the cap, a stop or the
scorer. **Each arm is its own card lane** (`card-e215a`, `card-e215b`: the never-run scanner subtracts those two folder names, so use exactly
them) with its own booking, its own G and its own RB_OUT; the two arms, on two boxes, may run at the same time (E215.md 6), **their desk spans
kept apart** (THE ONE-LAB RULE: rows 0-2 inside `onelab.sh desk`, never two lanes at once). **New against E213's brief:** arm B's steps 4, 9 and
12 are the A2 form's files in `a2/rb/`; the family smokes (every smoke but s01 and s11-s13 has its own stop path); **the gemmLnc family's smoke
runs inside the sequence, right before its block, at the session's end** (arm A s03, arm B s14); arm B's rgm211 gemmLn points (b009-b012, smoke
s15) run rgm211's ELF on card 1 for the first time, gated at its whole ELF; step 2 on arm B also re-chooses arm B's points (about ten minutes).
**fix-e215 (dated Thu 19 Nov 2026, before any E215 datum; verify-e215's finding 1):** step 2 prints the scorer's forecasts through
`rb/forecasts_print_e215.py`, which writes nothing (the scorer's own `--forecasts` mode writes over the registered `forecasts-e215.txt`),
compares the print with the committed bytes, and reads at its end that no registered file was written and E215's paths are clean again (row 2).*

## 1. What the go must carry (E215.md 6)

- **The owner's go**, on the round's reading: his standing words of Sun 15 Nov 2026 ("continue, all machines are up", 10:05:42 PST; "don't
  worry about discord post, just use the machines, nobody is using them", 10:22:36; "Feel free to use more cards in parallel, I don't need to
  reserve them", 17:21:16), "Try again" (received at or before 21:28:59) and "don't worry about hitting the limit, I will use a reset, feel free
  to run things overnight and in parallel" (at or before 21:51:09), his matmul focus of Mon 16 Nov 2026 (received at or before 09:48:24: "... just
  go as far as possible on the matte mold, on the FME, yeah, on the matmul operation"), his words relayed on the coordination thread (Mon 16 Nov
  2026, 11:01:08 PST: "feel free to use all the cards without restriction"; 23:15:25 PST: "There's no deadline; use the cards all night"), and
  Tue 17 Nov 2026: "Try again" (at or before 06:40:56 PST) and "Continue from where you left off" (twice, at or before 16:4x PST), with E215's
  registered items as its defaults, once E215 is registered, kitted, verified, landed and readiness-checked. Record them as dated departures in
  the data README: the registered items as their defaults; G = the booking on its day; the post waived; the package counter not read; the desk
  aifoundry2 with Python 3.12.3; the yvb3 session.
- **Arm A**: aifoundry3 card 0 at its pinned 600 MHz (a boot-time TDP of 0 latches the governor), reads only, nothing set; after the round's queue
  on aifoundry3 (the readiness lane's go lines name the queue helper's call, chain `e215a`); **119 runs and the gemmLnc smoke, 49.4 card-minutes
  planned, no run after 60, cap 70; stops 70 W on 3 samples / 70 C**. Its freeze line, MM1-v3.1's land `2c971828` (committed 23:09:13 PST Wed 18
  Nov 2026), is on GitHub main; E215's registration commit froze arm A's MM1-v2 column and every 'v3.1 with T7' forecast (REPORTED only).
- **Arm B**: aifoundry1 card 1 at 600 MHz as found, **ET_DEVICES=1 on every device process, card 1's lock, nothing on card 0 but the A2 form's one
  firmware read (fwgate's `--both-nodes-ok` query: card 0's management node opened within that one call, no command, runtime, workload or set),
  one session of ours on aifoundry1 at a time** (either card; the model session's sweeps included); **71 runs and the gemmLnc smoke, 28.0
  card-minutes planned, no run after 42, cap 48; stops 72 W on 3 samples / 80 C**. **Its freeze line is the registration commit's push** (E215.md
  section 0): the readiness lane's go lines require that commit on GitHub main before arm B's booking, and step 0's F1 line reads it.
  **Conditional**: while a claim of the model session's stands on aifoundry1 the queue helper prints QUEUE CANCELLED (exit 4): **keep waiting in
  bounded chunks** - book nothing, make no ssh call to aifoundry1 while the claim stands - at most until THE DAY's last booking time (20:29:00 PST),
  then SKIPPED for that day.
- **The rest**: each arm's first card command (step 7's config read included; on arm B also the A2 form's firmware read, which waits for the rest
  inside step 4) at least 40 minutes after the end of the last session on that box (arm A: ours on aifoundry3, E213 arm A's ended 07:19:59 PST Wed
  18 Nov 2026; the simulator runs on aifoundry3 since are not card sessions; arm B: either card of aifoundry1, ours or the model session's, E214
  a1c1-S4 ended 21:01:51 PST Wed 18 Nov 2026 by the orchestrator's release record, any later release counting). Read it by the clock from the last
  card lane's records BEFORE the booking; steps 7 and 9 (and arm B's step 4 before its read) read it on the box again.
- **The window**: G = this lane's booking of the arm's box that day; last start G + 1:30, last end G + 3:30, both rounded up to the minute,
  inside G's Pacific day; G at 20:29:00 PST or earlier. **Step 9 launches by the last start** (k6's `rb_need_start`; the cap and 5 minutes
  before the last end, E215_BUDGET_S arm A 4,500 s and arm B 3,180 s, would allow G + 2:15 and G + 2:37: the last start binds) and the runner keeps
  every run inside the last end.
- **The post**: none, by the standing waiver (record his words of 10:22:36). **The host's package counter**: not read.
- **The registration and the kit landed and on GitHub main** (registration first, then the kit), no datum of this arm in any ref (steps 0 and 2
  refuse).
- **A sealed forecast** (E215.md 0): a seal the model session posts before an arm books is recorded in `W/out/orch/sealed-e215.txt` only after it
  is registered in `tools/claims-v3/sealed-e215/e215-freeze-lines.md`, and the orchestrator holds that arm's booking meanwhile (`book.sh take
  <box> orch-hold-e215-seal`). Step 0's S1 line reads both: a sealed sha256 the record lists and the note at HEAD does not register stops the day
  before the box (tell the orchestrator; the note lands first). **A later seal** (E213's lesson) goes in a NEW note
  (`e215-freeze-lines-2.md`) and its record line is a COMMENT: step 0 reads only `e215-freeze-lines.md` and every 64-hex on a non-comment line.
  A seal posted after an arm booked is REPORTED as sealed during that arm's session.
- **THE QUIET DESK FLAG on aifoundry2** (the round's flag for a session on aifoundry2's own card): while it is up, run neither step 9 (its file
  name holds `session_e215.sh`, which a text-matching session count on aifoundry2 would read) nor any desk test of this kit; wait in bounded
  chunks.

## 2. The steps, in order (paths under `tools/claims-v3/e215/`; `<arm>` is A or B, `<box>` aifoundry3 or aifoundry1)

Run from the lab clone (`cd $LAB`), ONE RB_OUT for this arm (a new directory outside the repo), the one `RB_LOCK` (the round's file of login
checks), for step 2 `RB_GITLOCK` (the lab-git lock), and for step 6n `E215_ROUND_OUT` (the round's OUT). Each step one plain call from a script
file; the numerical ones (steps 2 and 6n, and 12's reducer) inside the round's slot (`W/slot.sh`, THE CPU RULE: one slot job at a time,
OMP_NUM_THREADS, OPENBLAS_NUM_THREADS, MKL_NUM_THREADS and NUMEXPR_NUM_THREADS 1). k6's drivers bound every remote call: a 15 s probe, then 60 s
for a read, 600 s for a copy or one bounded wait (520 s), a detached launch that returns at once, 5,400 s for a desk call. **A printed login link
stops the step (11) and appends `<HH:MM:SS> <box> needs a check` to `RB_LOCK`:** nothing is retried until it is cleared, and a session detached on
the box keeps running. k6's exit codes: 0 done; 10 refused; 11 a login link; 12 no answer; 13 past a bound; 14 a call failed; 15 a holder for 30
minutes; 16 a gate says stop; 17 call again. **E** is the end of every path (below): it carries undesk and uncollect where they are due.

| # | the step | what to do with its exit |
|---|---|---|
| B | the queue (the readiness lane's go lines: wait in bounded chunks until QUEUE OVER; **while QUEUE BUSY or QUEUE CANCELLED keep waiting**, booking nothing and making no ssh call to that box while a claim stands, at most until 20:29:00 PST of the day, then SKIPPED); **arm B: the registration commit on GitHub main** (the go lines read it; step 0 reads it again); `bash W/book.sh show`: a line `orch-hold-e215-seal` on the box means the orchestrator is registering a seal: wait (bounded), never book over it; then the rest by the clock (section 1), then THE DAY (G at 20:29:00 or earlier; later: wait in bounded chunks until 00:00:30 the next day); then `bash W/book.sh take <box> <lane>` | 0 BOOKED: G = this moment. 1: another lane (or the orchestrator's hold) holds it: make no ssh call to that box at all; wait (bounded) or stop (nothing else to undo) |
| 0 | `uptime` FIRST, OUTSIDE the span (THE LOAD RULE: above 8, wait in bounded chunks of at most 9 minutes until below 6, at most 60 minutes in all; past that, no box step that day: **E**); then `bash W/onelab.sh desk <lane>` (THE ONE-LAB RULE: steps 0, H and 2 never overlap another lane's collect span or a commit of ours, and **the other arm's desk span**: the two E215 lanes' rows 0-2 never run at once; exit 3 at its 9-minute bound: call again, at most 6 calls, else **E**); E215's anchor lines (the land record, `OUT/q224-anchor-lines-e215.txt`, if the readiness lane names one); then **`E215_SEALED=W/out/orch/sealed-e215.txt bash rb/s00_step0_e215.sh <arm>`** (one call, read only, with the round's environment-only git rewrite set by the caller: S0 GitHub main and HEAD; **F1 the arm's freeze line an ancestor of GitHub main** (arm A `2c971828`; arm B the registration commit, found by content: subtree `e89e512f`); F2 the kit commit; **S1 THE SEALED-FORECAST CHECK** (every sealed sha256 on a non-comment line of the record registered in `sealed-e215/e215-freeze-lines.md` at HEAD; "0 of 0" with no record); S2 the seal notes' commits; D0 no datum of this arm in any ref; G1 the clone clean) | `STEP0-E215 arm <arm>: 5 of 5 as stated` (exit 0): go on. Exit 1, any line NOT AS STATED: no box step that day: **E (with undesk)**; an S1 line NOT AS STATED is also told to the orchestrator (the seal's note lands first). Exit 2: a usage error (E215_SEALED unset): fix the call, then step 0 again |
| H | `bash W/hold.sh add <lane>` (THE QUIET HOLD, one owner a line, until the data commit); `git -C $LAB status --porcelain --untracked-files=all` reads 0 lines | not 0: **E (with undesk)** |
| 1 | `rb/s02_window_e215.sh <arm> <YYYY-MM-DD> <last start HH:MM> <last end HH:MM>` (today only; G + 1:30 and G + 3:30, rounded up) | "fits now: an E215 arm <arm> session ..."; "fits now: nothing": no box step: **E (with undesk)** |
| 2 | `uptime` (above 8: `undesk`, wait outside the span as in step 0, `desk` again, then this row again); then `RB_GITLOCK=<the lab-git lock> bash W/slot.sh bash rb/s03_desk_e215.sh <arm>` (arm A about 4 minutes: the registration's forecast and rules checks and the scorer's stand-in self-test take most of it; **arm B about 14 minutes: also `desk/choose_e215b.py --check`, which re-chooses arm B's 30 points from the registration's scan**), **never inside the lab-git lock**; step 2 writes only into RB_OUT and never rewrites a registered file (its checks are each script's `--check`; the scorer's forecasts print is `rb/forecasts_print_e215.py`, print only, compared with the committed bytes; at its end it reads that no file of E215's registered folders is newer than its start marker and that E215's paths are clean again: fix-e215); then `bash W/onelab.sh undesk <lane>` | 0: undesk, go on. A 16 naming **wrote-in-lab** or **status-after** WITHOUT HEAD-moved: something wrote in the lab clone while step 2 ran: **E (with undesk)**, told to the orchestrator; with HEAD-moved beside it (a co-owner's commit wrote those files), the HEAD-moved exception below applies. A 16 naming **E215-arm-<arm>-has-data**: this arm already has a datum: **E (with undesk)**, told to the orchestrator. Anything else: no box step that day: **E (with undesk)**. Two exceptions, each bounded: a pull whose output shows the upstream did not answer: `undesk` at once, wait outside the span (chunks of at most 9 minutes; at most 3 tries in 30 minutes in all), `desk` again and run step 2 again, else **E**; a 16 naming HEAD-moved (a co-owner committed meanwhile): run step 2 again at once, at most 3 times, else **E (with undesk)** |
| 4 | **arm A:** the look, `../q141k-runbook/k6/s05_look_k6.sh aifoundry3` (it writes the box-login file the scrub reads). **arm B (the A2 form): `a2/rb/s05_look_e215_a2.sh B`**: the window, the A2 form's pins at the desk, k6's holder rule with `--wait` (k6's continuity identity is NOT read: it stops every boot of aifoundry1 after E82's firmware read), the A2 form's box files synced and checked, fwgate's look; on NEEDS-READ, in one bounded call, THE REST RULE first, both cards free by `et-who --check`, then ONE `fwgate.py read --box aifoundry1 --card 1 --both-nodes-ok` (the owner's rulings, verbatim: 15:07:01 PST Sun 15 Nov 2026, "Firmware revisions query was a false positive. It should have never been forbidden. Reading operations and firmware are always allowed." and 15:09:49 PST, "I don't want to modify firmware, but commands which read firmware should be fine."); the read's folder copied back exact and its scrub checked; this boot's ledger and attempt-log lines brought back as evidence (never a gate). **On aifoundry1's present boot (16:46:32 PST Tue 17 Nov 2026, E213 arm B's) fwgate counts only committed records and EQUAL reads of today, so the look reads NEEDS-READ and step 4 makes the boot's second read (fwgate allows it: the first, E213 arm B's of 15:13:25 PST Wed 18 Nov, ended EQUAL); the evidence then reads fwgate's ledger with two calls of this boot ("NOT one EQUAL call on this boot: read the lines"): expected, REPORTED in the README, never a gate (KIT.md 5)** | arm A: FREE; a holder: bounded polls (`--wait`), at most 30 minutes, else no session that day: **E**. arm B: 0 (`A2-LOOK-B: CONTINUITY ...` or `A2-LOOK-B: EQUAL <record> ...` in RB_OUT/e215-a2-look-B.txt); 10 (the rest not open before the read: wait in bounded chunks and run step 4 again); 17 held (call again, bounded) and 15 held 30 minutes in all (no session today: **E**); **16: no session on this boot (DIFFERENT, UNREADABLE, a cut-off read, a busy lock, a missing lock file, an attempt of this boot that did not end EQUAL: never a second read on the boot, by fwgate, the kit or any lane): E**, reported |
| 3 | the day's post: **none**, by the owner's standing waiver of Sun 15 Nov 2026 10:22:36 PST; record his words | |
| 5 | `rb/s07_sync_e215.sh <arm>` | 0 HARNESS OK on the box; 10: a session or runbook job of ours on the box; 16: uncommitted synced paths or a file off its sha256: **E** |
| 6 | `rb/s08_build_e215.sh <arm> start`, then `... wait` while it says 17 | 0: RB_OUT/e215-built-<arm>.txt (both kernels KERNEL OK; **on arm B both kernels at their whole ELF** and "the hosts and /opt/et/lib/libdeviceLayer.a carry ET_DEVICES", else 16 and no session of arm B that day). **On arm B, rgm211's host and ELF are built here for b009-b013 and smokes s14 and s15 (rgm211's ELF runs on card 1 for the first time): a failure to build or gate either kernel fails the whole build (RGM-BUILD-FAILED, 16), and so arm B's whole session that day; E213 arm B's real build on aifoundry1 read both whole ELFs the pins (b0c727c5 session/kernel-rgm*.txt): report a failure, a dated note decides;** 16: start once more (two starts a Pacific day at most; a third: NO-THIRD-BUILD, no session that day: **E**); a 14 on wait: no reading, wait again |
| 6n | **THE NEVER-RUN SEARCH, REPEATED RIGHT BEFORE THE FIRST CARD COMMAND** (E215.md 4): `E215_ROUND_OUT=<the round's OUT> bash W/slot.sh bash rb/s06n_neverrun_e215.sh <arm>` (about a minute at the desk, single-threaded: the registration's scanner, unchanged, over the lab at HEAD, the round's card and data lane folders and MM1-v3.1's measured points, E215's own folders subtracted; then the judgement of each point by its own reading - literal P, C, R the shape token; post hoc L the configuration; post hoc S the kind - against the arm's freeze line); run it when the rest is open or about to open, since step 7 needs its report under 30 minutes old | 0: its line `NEVER-RUN-E215 arm <arm>: <n> of <n> scored points never ran ...; ran before the freeze line (...), labelled: <none / ids>; ran after it (REPORTED, kept): <none / ids>` in RB_OUT (REPORTED, never a gate: a point labelled 'ran before' leaves every rule through the scorer's `--labels`, which step 13 passes from the data directory's `labels-e215.json`, and gets a dated note before the data commit, step 12); 14: a scan failed: run it again, at most 3 tries in all, else **E**; 10: no window for today (step 1 again, then 6n) or no `E215_ROUND_OUT` (set it to the round's OUT, then 6n again); after three 10s in a row, **E** |
| 7 | **STEP 7 ONLY ONCE THE REST HAS OPENED, WITHIN 30 MINUTES OF 6n**: `rb/s09_reads_e215.sh <arm>` (the 6n report's age and the rest rule on the box first, no card command; then the time stamped and the config read: arm A k6's step 7 unchanged; arm B the card-1 read through E215's guard with ET_DEVICES=1 and card 1's lock, its identity lines and card 0 clean); then 8 and 9 **without delay** | 10 with "the never-run report": run 6n again, then 7; 10 with "the rest has not run": wait in bounded chunks and run it again (6n again if its report passes 30 minutes), never around it; 0: the config read as found (arm A TDP 0 W / 65 C / 600 MHz; arm B TDP 65 W / 65 C / 600 MHz, minion_mv below 510, /dev/et1_mgmt and physical ID 1 alone) and et-who clean; 16 (not as found): no session that day, set nothing: **E**; 17 (et-who not clean): step 4 with `--wait` (arm B: k6's holder rule as in step 4), then step 7 again |
| 8 | `rb/s10_dry_e215.sh <arm> start`, then `... wait` | 0: E215-DRY arm <arm> rc=0 runs=3 (the doubles on the box, no device: the opening smoke, the stop-path test and three runs) **and THE SCRUB CHECK on the dry pass's own records** (copied back read-only, scrubbed on a private copy at the desk by the collection's code: SCRUB-CHECK CLEAN); 16 with SCRUB-CHECK LEFT: the collection would refuse this box's records after the session: no session today, a kit note first: **E** |
| 9 | (the quiet-desk flag on aifoundry2 absent) **arm A: `rb/s11_session_e215.sh A`; arm B (the A2 form): `a2/rb/s11_session_e215_a2.sh B`** (the kit's step 9 line for line but for the guard: the A2 form's pins on the box, then `fwgate.py guard --box aifoundry1 --card 1 --extra <the read's folder>`, "identity: ... ok" or IDENTITY-STOP and nothing launched; it requires step 4's look file from today) | 0 launched (its "rest:", "hung:" and "same-day:" lines in the runbook log; the T0 in RB_OUT/e215-T0-<arm>.txt); 10 refused (no never-run report from today: 6n and 7 first; the rest; a session or job of ours; **a HUNG marker**: a device process of ours did not end after its timeout's TERM: stop, report to the owner, no session that day; the same-day rule; no dry pass or build today; arm B: no A2 look file from today): read why, never around it: **E** if the day cannot go on; 16: past the last start, the cap would pass the last end, or (arm B) IDENTITY-STOP: **E** |
| 10 | `rb/s20_wait_e215.sh <arm>`, again while it says 17 | 0: ended, MANIFEST-WRITTEN, the runner exited 0 (read its `STOP:` line if one is printed: a stop line, a holder, a kernel stop, an identity gate failure or two failed processes in a row end a session rc 0; a family dropped by its smoke is no stop: read its "FAILED for its family alone" lines); **16 HUNG**: KILL NOTHING, reset nothing, keep the booking and the hold, collect what is written (step 11), write it up and escalate to the owner; **16 K1-STOPPED**: a launch did not finish (it may leave a hung hart): collect it, never reset, escalate; **16 CRASHED**: read runner.out read-only, report, then collect; **16 GATE-STOPPED**: no run, still collected as a gate stop's record; 14: gone without "session end" (RUN-GONE) or no runner.rc (read the box read-only first) |
| 11 | `bash W/onelab.sh collect <lane>` (exit 3 at its 9-minute bound: call again, at most 6 calls; the session's files wait on the box; after the sixth 3, **E**: nothing collected, the session's files left on the box untouched and reported, a later collection by a dated note); then `rb/s22_collect_e215.sh <arm>` (start it at least 10 minutes before the last end) | 0 COPY-BACK EXACT; 16 COPY-BACK NOT EXACT (a HUNG process may still be writing its files): commit nothing, read why: **E (with uncollect)**. **Every other exit** (10 refused, 11 a login link, 12 no answer, 13 past a bound, 14 a call failed): `uncollect` at once (nothing is committed yet), read why, wait OUTSIDE the span (chunks of at most 9 minutes; after a login link only once `RB_LOCK`'s check is cleared), then `collect` again and step 11 again: at most 3 tries in 60 minutes in all, else **E**, the session's files left on the box untouched and reported |
| 12 | **arm A: `bash W/slot.sh bash rb/s23_data_e215.sh A`; arm B (the A2 form): `bash W/slot.sh bash a2/rb/s23_data_e215_a2.sh B`** (the kit's step 12 as a child, unchanged, then the firmware read's folder - when step 4 read - into the data directory as `fwgate/` after the kit's scrub, with step 4's evidence of the one call beside it; SHA256SUMS made again): the data directory `docs/reports/data/<day>-e215-blind-matmul-<aifoundry3 / aifoundry1-c1>/`, or a gate stop's record under `docs/reports/gate-stops/`; the scrub of every form of the box's home, our login and another login's et-who holder lines; the reducer (the gemmLnc smoke a smoke RUN at its place); **step 6n's report, judgement and labels** copied in and listed in SHA256SUMS; the desk-path gate; the history check; the README in [DATA-README-FORM-e215.md](DATA-README-FORM-e215.md)'s form; **if step 6n labelled any point 'ran before', a dated note** (`README.md.dated-note-1.md`: the points, the files and dates the judgement found, and that the scorer's `--labels` takes them out of every rule; the frozen scorer is never changed); the public-text scan; `LAB_QUIET_HOLD_OWNER=<lane> bash W/commit_lab.sh "<subject>" "<body>" <the collected directory>` (new files only; on exit 5 or 6 run it again); **then** `bash W/onelab.sh uncollect <lane>`, `bash W/hold.sh remove <lane>`, `bash W/book.sh release <box> <lane>` | "COMMIT_LAB: pushed <sha>"; anything else after the retries: move the collected directory out of the lab clone at once into the lane's own folder (`OUT/<lane>/held/<the directory's name>`, a copy checked against its SHA256SUMS first, then removed from LAB by its literal path), so no untracked file in LAB blocks another card lane's step H; then **E (with uncollect)**, reported (a later lane commits the held directory by a dated note) |
| 13 | after the data commit only, never on a gate stop's record: `bash W/slot.sh bash rb/s24_score_e215.sh <arm>` | step 6n's labels checked (LABELS-OK) and passed to the frozen scorer: RB_OUT/scores-e215-<arm>.json and .txt (this arm's rules per group, registered P/C/R and post hoc L/S reported apart; the other arm and the pooled HP1-HP5 NO DATA in this file: the scores lane scores the pooled rules once both arms are committed); read its words; a later lane commits them beside the data |
| E | **every path ends here**: `bash W/onelab.sh undesk <lane>` if inside steps 0-2; `bash W/onelab.sh uncollect <lane>` if between step 11's collect and the data commit's push; then `bash W/hold.sh remove <lane>` and `bash W/book.sh release <box> <lane>` (on a HUNG or K1 day: keep the booking and the hold until the owner or the orchestrator answers; release them then) | |

**Waits inside a span** (THE ONE-LAB RULE): every wait in this table is bounded (at most 9 minutes a call, with each row's total), and no wait
longer than one call happens inside a span: the load rule waits before `desk`; a step 2 or a step 11 that must wait leaves its span first
(`undesk`, `uncollect`) and enters it again before it is run again; past a row's bound the path ends at **E**. Inside the desk span a lane holds
only step 0's reads, H, step 1 and step 2 (k6's bounded drivers); inside the collect span, step 11 (its 600 s copy) and step 12 (commit_lab.sh's
own bounds: its lock wait of 1,200 s, five push tries). **The other E215 arm's desk span is another lane's span**: `onelab.sh desk` waits for it
(arm B's step 2 holds its span about 14 minutes; start arm A's rows 0-2 first when both lanes are ready at once).

**To stop the session by hand** (the operator's stop, a registered stop): `touch build/e215/T<T0>-<arm>/STOP` on the box (the host ends at its
next launch boundary; the runner reads the file before every start, so nothing further starts; a STOP file already there when the runner starts
is a refusal, no device opened, the file kept), or SIGTERM to the runner (`run_e215.py`), never to a host or the sampler. A STOP during the smoke
ends the smoke as a gate stop whose words name the stop. Never kill a process: the session ends its own processes and stops its sampler with
SIGTERM.

## 3. After a gate stop, a dropped family, a registered stop, a kernel stop, K1, HUNG or a crash

- **A gate stop** (no run: "refused, no device opened: ..." before any card command, or after the card opened: the start config, the card's
  identity gate, the sampler, the identity read, the session's smoke s01 or s11-s13 (an identity gate per process failing in it among them), a
  family smoke's failure that is the session's (below), the stop-path test) is **no session: no data**. Step 12 collects it as a gate stop's
  record under `docs/reports/gate-stops/`, never `docs/reports/data/`; commit it (new files only, its README in the gate-stop form); it is never
  scored. **That arm may be tried again with no amendment**: after a refusal that opened no device, **once more the same day**, once the look reads
  FREE again and inside the window (step 9 counts the tries: a third is refused); after a gate that came after the card opened, **not the same
  day** (step 9's same-day rule); a try on a later day needs that day's go, the rest, step 0 and step 6n again (and on arm B its step 4 on that
  boot). A gate stop by a kit defect is the kit's to fix: a dated kit note and, if it touches the registration, a dated amendment to E215.md before
  any datum of that arm, verified and landed, then a later session.
- **A family dropped by its smoke** (E215.md 3, E213's Amendment A1 form; arm A: s02 'rgm211 gemmLn' (a021, a022, a023, a025), s04 'rgm211 gemmL'
  (a027), s03 'rgm136 gemmLnc' (a024, a026, a031, a032); arm B: s15 'rgm211 gemmLn' (b009, b010, b011, b012), s14 'rgm136 gemmLnc' (b013)): the
  smoke failed for its family alone - a GATE FAILED (no process started), a check of C wrong or missing, the walk check failed, a tensor error, a
  launch not ok, an exit not 0 but 124, the counter's mean outside 200-4,000, or the board's rise short on a live sampler; for the gemmLnc smoke
  inside the sequence also its not starting (the die gate's 300 s). The session log reads "smoke <id>: FAILED for its family alone (its own stop
  path, E215.md 3): ... the family '<loop>' is DROPPED - <points> never start (NO DATA); the session goes on"; the family's runs are "not
  started" (NO DATA, no card time; queue.json's `families_dropped`). It is **not a gate stop and not a kernel stop**: the runs stand and are
  collected and committed as usual; the data README records the drop and the smoke's words; the frozen scorer reports it (the flag "the family
  smoke of '<loop>' failed ...") and R0 does not count the smoke's own failure while none of its family ran. A failed family smoke that is the
  session's - K1, a HUNG host, a launch timeout (rc 124), the host not shown on the arm's card, the sampler not live after it, or any stop raised
  during it - stops the session (in the opening smoke: a gate stop; at the gemmLnc block: a stop after the runs, which stand). A failed gate or
  walk at a family smoke is a kit or build defect until shown otherwise: a dated note, and the readiness lane's look at the box's build before any
  later session of that family. **On arm B a drop of 'rgm211 gemmLn' at s15 is rgm211's ELF's first process on card 1 failing: report it at once.**
- **A registered stop** (the board or die lines, a holder, two failed processes in a row, the card-time rule, the window's end, the operator's
  STOP or SIGTERM) after a run: the runs done stand and are scored as they stand (the registered subset if cut: the opening smoke, tie 1, pass 1
  and tie 2, every point once but the gemmLnc block: arm A 82 runs, about 34.1 card-minutes; arm B 43, about 17.2); the data directory is
  committed; the missing runs are never re-run without a dated amendment. **A board stop in the gemmLnc block** (E213 arm B's day: k37 tripped 72 W
  x3 at run 079) costs only the gemmLnc runs after it: the block is last by registration.
- **A kernel stop** (an rgm211-host process ('rgm136 gemmLnc', 'rgm211 gemmLn', 'rgm211 gemmL') with a check of C wrong, a tensor error, the walk
  check failed, a launch timeout or a launch not ok; or an identity gate failure before any run's process): **nothing more that day on that arm**.
  The runs done stand and are collected and committed as above; the stop's words go in the README. A failed identity gate or walk check is a kit or
  build defect until shown otherwise: a dated note, and the readiness lane's look at the box's build before any later session.
- **K1** (a launch that did not finish) and **HUNG** (a device process still alive after its timeout's TERM): the session stops; the card may
  hold a hung hart: **never reset the card, no PMIC or power action, kill nothing** (the field manual's gates). Keep the booking and the hold,
  collect what was written (a HUNG process may keep writing its own files after the manifest: then the copy is not exact; commit nothing until a
  dated note decides), write it up, escalate to the owner and the lab admin. Step 9 refuses every later session of ours on that box while the
  HUNG line stands.
- **A crash** of the runner: named in its log ("CRASH: <type>: <message>"), its closing still run, runner.rc 1; step 10 says 16; report it,
  collect it (a crash with no run is a gate stop's record); never re-run around a crash without a dated note.
- **The runner gone without "session end"** (step 10's RUN-GONE): read the box read-only, collect what is there by a dated note's decision,
  report; the rest rule counts the session at its run's latest write.
- **Arm B's firmware gate** (step 4, the A2 form): anything but EQUAL or CONTINUITY ends arm B's day on that boot, and no lane reads the firmware
  again on that boot; the read's folder and the evidence are committed with the data (step 12) when a session ran, or reported in the lane's
  result when none did.

## 4. Never

- No step 2 but `rb/s03_desk_e215.sh`, never inside the lab-git lock; no box step without step 0's and step 2's 0 that day; no step out of the
  order above; **never step 7 before the rest has opened, nor without a 6n report under 30 minutes old**; never steps 5, 6 or 8 while a session
  of ours runs (they refuse).
- **No booking of arm B before the registration commit is on GitHub main**; no booking over the orchestrator's `orch-hold-e215-seal`.
- No change to a forecast, a band, a rule, a threshold, the order, the card time, the cap or a stop except by a dated amendment before that arm's
  data (E215.md, Amendments); no run re-run after a stop without one; the scorer only as registered and only after the data commit.
- No device command but the kit's READs (dmcmd_audit_v2 GO) and, on arm B, the A2 form's one firmware read (a READ: fwgate's audit GO, its one
  send site the revisions query): no set, no reset, no governor, TDP, threshold, clock, voltage, fan or firmware change; no statistics reset; no
  PMIC write; no PCIe recovery, no driver reload, no power cycle and nothing that risks one; **never kill a device process** (no SIGKILL, no
  `timeout -k`; a process that does not end after its TERM is reported at once and left).
- **On aifoundry1: nothing on card 0** but the A2 form's one read (ET_DEVICES=1 on every other device process, card 1's lock), and **one session
  of ours on the box at a time** (either card). Never two sessions of ours on a box at once; never beside another user's holder or device process
  (the session's et-who and ps refuse).
- Never a lab user's login in any file (the collection's scrub masks ours as `<login>` and another login's et-who holder lines as
  `<another-login>`); no number from the owner's private pages or his A100 report in any lab file; no sealed forecast's number anywhere.
- Never touch another run's files on the box: E215 writes only `build/e215rgm/`, `build/e215/` (the A2 form's read folder and attempt log among
  them), `build/e215-build-*` and the runbook's own `build/q141k/` entries, and step 5's (and the A2 form's step 4's) synced files at their
  committed bytes; step 6n writes nothing on the box.
- Never write in another lane's folder, booking, hold line or onelab flag; never answer a lane by a message (the orchestrator answers through
  files under `W/out/orch/`).

## 5. Labels

Every figure here is **registered** (E215.md) or a **desk check of code** (KIT.md). Nothing here is measured, blind, held out or post hoc.

SPDX-License-Identifier: Apache-2.0
