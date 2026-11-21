# E222's card-lane brief: what the lane that runs E222, the MM1-v3.3 candidates' blind day on aifoundry3 card 0, does, step by step, and what it never does (Q236; kitted, not run)

*Fri 20 Nov 2026 (week 47), PST, on aifoundry2, desk only (Q236, lane `kit-e222`), beside [KIT.md](KIT.md). E218's card-lane brief
(`tools/claims-v3/e218/CARD-LANE-BRIEF.md`, kit `5582edfc`: the brief E218 ran FULL by on this card at 03:11-03:56 PST Fri 20 Nov 2026, 107 of
107 runs, data `b445b0f5`), itself E215 arm A's, for E222. The registration is [E222.md](E222.md) (found by content: the commit that added it; its
subtree `f8e6ec56...`; `SHA256SUMS-e222-registration` `de67150b...`, 30 entries). No card was claimed or opened, no device command was sent,
nothing was posted. No E222 datum exists. This brief changes no point, forecast, band, rule, threshold, the order, the card time, the cap, a stop or
the scorer. **The card lane is `card-e222`** (exactly that folder name under the round's OUT: the registration's never-run scanner never opens a
lane or data folder whose name holds `e222`, so any other name would read E222's own records as runs) with its own booking, its own G and its own
RB_OUT. **New against E218's brief:** E222's 70 points (T 32, L3b 10, Y3 10, G3 7, G3t 7, R 4) and its order (120 runs and 2 smoke processes:
pass 1 of 55, pass 2 of 40, the G block of 22 last, its smoke s03 at the kit's place 99); the card-time rule 70 card-minutes and the cap 80; step 0
reads the posted freeze line (F0: FROZEN.txt and the three forecast files) and the three candidates' lands (F1C); step 2 runs the frozen scorer's
two self-tests through `rb/scorer_check_e222.py` (written in RB_OUT only: the scorer's own `--selftest-*` modes write registered files), the sized
timeout and the no-kill audit; **step 6n judges by session records on this card (E220's dated note 1, the registration's reading), prints family R
(E218's own points, run here) as "RAN (exempt by family name: same-card repeats, REPORTED only)" and runs THE POSITIVE CONTROL** (R's exemption
lifted, all four must read RAN; else the day stops before step 7); step 13 calls the scorer in its registered form and leaves the cross-card rule
to the scores lane.*

## 1. What the go must carry (E222.md 6)

- **The owner's go**, on the round's reading: his standing words of Sun 15 Nov 2026 ("continue, all machines are up", 10:05:42 PST; "don't
  worry about discord post, just use the machines, nobody is using them", 10:22:36; "Feel free to use more cards in parallel, I don't need to
  reserve them", 17:21:16), "Try again" (received at or before 21:28:59) and "don't worry about hitting the limit, I will use a reset, feel free
  to run things overnight and in parallel" (at or before 21:51:09), his matmul focus of Mon 16 Nov 2026 (received at or before 09:48:24: "... just
  go as far as possible on the matte mold, on the FME, yeah, on the matmul operation"), his words relayed on the coordination thread (Mon 16 Nov
  2026, 11:01:08 PST: "feel free to use all the cards without restriction"; 23:15:25 PST: "There's no deadline; use the cards all night"; and since:
  "use all the cards without restriction, all night if needed"), and Tue 17 Nov 2026: "Try again" (at or before 06:40:56 PST) and "Continue from
  where you left off" (twice, at or before 16:4x PST), with E222's registered items as its defaults, once E222 is registered, kitted, verified,
  landed and readiness-checked. Record them as dated departures in the data README: the registered items as their defaults; G = the booking on its
  day; the post waived; the package counter not read; the desk aifoundry2 with Python 3.12.3; the yvb2 session (the card lane records its start).
- **The card**: aifoundry3 card 0 at its pinned 600 MHz (a boot-time TDP of 0 latches the governor), reads only, nothing set; after the round's
  queue on aifoundry3 (the readiness lane's go lines name the queue helper's call: `python3 W/out/orch/queue_state.py aifoundry3`); **120 runs and
  2 smoke processes (s01, s03), 50.7 card-minutes planned, no run after 70, cap 80; stops 70 W on 3 samples / 70 C**.
- **The freeze lines before the booking**: FROZEN.txt's post (`OUT/reg-e222/FROZEN.txt` `172ed079...`, written 13:50:25 PST Fri 20 Nov 2026,
  posted 13:51:12 PST as #1.30.1.2.1.1.1 and recorded in `W/out/orch/q236-frozen-posts.txt`, before any E220 or E222 datum: every forecast); on
  GitHub main, MM1-v3.2's land `4e386f75` and the three MM1-v3.3 candidates' lands (07:49 PST Fri 20 Nov 2026: posimb `badf08fa`, gemmlnc-af4
  `911651ee`, l3s `2a509f5a`: the code the forecasts read in place), then **the registration commit** (its push is E222's second freeze line: every
  forecast, the points, the rules, the plan and the scorer), then the kit's commit. Step 0's F0, F1, F1C, F1R and F2 lines read all of them.
- **The rest**: the first card command (step 7's config read included) at least 40 minutes after the end of the last session on aifoundry3 card 0
  (E218's ended 03:56:36 PST Fri 20 Nov 2026; any later session counts; the simulator runs on aifoundry3 are not card sessions). Read it by the
  clock from the last card lane's records BEFORE the booking; steps 7 and 9 read it on the box again.
- **The window**: G = this lane's booking of aifoundry3 that day; last start G + 1:30, last end G + 3:30, both rounded up to the minute, inside G's
  Pacific day; **G at 20:29:00 PST Fri 20 Nov 2026 or earlier (or a later day by a dated note), else from 00:00:30 PST the next day; the queue bound
  the go lines name (the round's brief: 08:00 PST Sat 21 Nov 2026)**. **Step 9 launches by the last start** (k6's `rb_need_start`; the cap and 5
  minutes before the last end, E222_BUDGET_S 5,100 s, would allow G + 2:05: the last start binds) and the runner keeps every run inside the last end.
- **The post**: none, by the standing waiver (record his words of 10:22:36). **The host's package counter**: not read.
- **The registration and the kit landed and on GitHub main** (registration first, then the kit), no E222 datum in any ref (steps 0 and 2 refuse).
- **A sealed forecast** (E222.md 0; the procedure is E218's, the orchestrator's answer 2 for E218: no answer for E222 names one yet, so the
  orchestrator confirms or changes it): if the model session posts a seal before `card-e222` books, the orchestrator holds aifoundry3 (E218's
  form: `book.sh take aifoundry3 orch-hold-e222-seal`), registers the seal in `tools/claims-v3/sealed-e222/e222-freeze-lines.md`, writes `W/out/orch/sealed-e222.txt`
  after that commit is on main, then releases. Step 0's S1 line reads both: a sealed sha256 the record lists and the note at HEAD does not register
  stops the day before the box (tell the orchestrator; the note lands first). **A later seal** goes in a NEW note (`e222-freeze-lines-2.md`) and its
  record line is a COMMENT: step 0 reads only `e222-freeze-lines.md` and every 64-hex on a non-comment line. A seal posted after the booking is
  REPORTED as sealed during the session.
- **THE QUIET DESK FLAG on aifoundry2** (the round's flag for a session on aifoundry2's own card): while it is up, run neither step 9 (its file
  name holds `session_e222.sh`, which a text-matching session count on aifoundry2 would read) nor any desk test of this kit; wait in bounded
  chunks.

## 2. The steps, in order (paths under `tools/claims-v3/e222/`)

Run from the lab clone (`cd $LAB`), ONE RB_OUT for E222 (a new directory outside the repo), the one `RB_LOCK` (the round's file of login checks),
for step 2 `RB_GITLOCK` (the lab-git lock), and for step 6n `E222_ROUND_OUT` (the round's OUT). Each step one plain call from a script file; the
numerical ones (steps 2 and 6n, and 12's reducer) inside the round's slot (`W/slot.sh`, THE CPU RULE: one slot job at a time, OMP_NUM_THREADS,
OPENBLAS_NUM_THREADS, MKL_NUM_THREADS and NUMEXPR_NUM_THREADS 1). k6's drivers bound every remote call: a 15 s probe, then 60 s for a read, 600 s
for a copy or one bounded wait (520 s), a detached launch that returns at once, 5,400 s for a desk call. **A printed login link stops the step (11)
and appends `<HH:MM:SS> aifoundry3 needs a check` to `RB_LOCK`:** nothing is retried until it is cleared, and a session detached on the box keeps
running. k6's exit codes: 0 done; 10 refused; 11 a login link; 12 no answer; 13 past a bound; 14 a call failed; 15 a holder for 30 minutes; 16 a
gate says stop; 17 call again. **E** is the end of every path (below): it carries undesk and uncollect where they are due.

| # | the step | what to do with its exit |
|---|---|---|
| B | the queue (the readiness lane's go lines: `python3 W/out/orch/queue_state.py aifoundry3`, waited in bounded chunks until QUEUE OVER; **while QUEUE BUSY or QUEUE CANCELLED keep waiting**, booking nothing and making no ssh call to aifoundry3 while a claim stands, at most until the queue bound, then SKIPPED); **FROZEN.txt's post recorded, MM1-v3.2's land, the candidates' lands, the registration commit and the kit commit on GitHub main** (the go lines read them; step 0 reads them again); `bash W/book.sh show`: a line `orch-hold-e222-seal` on aifoundry3 means the orchestrator is registering a seal: wait (bounded), never book over it; then the rest by the clock (section 1), then THE DAY (G at 20:29:00 PST or earlier; later: wait in bounded chunks until 00:00:30 PST the next day); then `bash W/book.sh take aifoundry3 card-e222` | 0 BOOKED: G = this moment. 1: another lane (or the orchestrator's hold) holds it: make no ssh call to aifoundry3 at all; wait (bounded) or stop (nothing else to undo) |
| 0 | `uptime` FIRST, OUTSIDE the span (THE LOAD RULE: above 8, wait in bounded chunks of at most 9 minutes until below 6, at most 60 minutes in all; past that, no box step that day: **E**); then `bash W/onelab.sh desk card-e222` (THE ONE-LAB RULE: steps 0, H and 2 never overlap another lane's collect span or a commit of ours; exit 3 at its 9-minute bound: call again, at most 6 calls, else **E**); E222's anchor lines (the land record, `W/out/q236-anchor-lines-e222.txt`, if the readiness lane names it); then **`E222_SEALED=W/out/orch/sealed-e222.txt E222_FROZEN_POSTS=W/out/orch/q236-frozen-posts.txt E222_FROZEN=W/out/reg-e222/FROZEN.txt bash rb/s00_step0_e222.sh A`** (one call, read only, with the round's environment-only git rewrite set by the caller: S0 GitHub main and HEAD (REPORTED); **F0 the posted freeze line** (the record's line names FROZEN.txt `172ed079` and the three forecast files, whose sha256 at HEAD are the posted ones; FROZEN.txt's bytes read); **F1 MM1-v3.2's land `4e386f75` and F1C the three candidates' lands ancestors of GitHub main; F1R the registration commit (found by content: subtree `f8e6ec56`) an ancestor**; F2 the kit commit; **S1 THE SEALED-FORECAST CHECK** (every sealed sha256 on a non-comment line of the record registered in `sealed-e222/e222-freeze-lines.md` at HEAD; "0 of 0" with no record); S2 the seal notes' commits (REPORTED); D0 no E222 datum in any ref; G1 the clone clean) | `STEP0-E222 arm A: 8 of 8 as stated` (exit 0): go on. Exit 1, any line NOT AS STATED: no box step that day: **E (with undesk)**; an S1 or F0 line NOT AS STATED is also told to the orchestrator (the seal's note lands first; a freeze line not as posted is the orchestrator's to answer). Exit 2: a usage error (E222_SEALED or E222_FROZEN_POSTS unset): fix the call, then step 0 again |
| H | `bash W/hold.sh add card-e222` (THE QUIET HOLD, one owner a line, until the data commit); `git -C $LAB status --porcelain --untracked-files=all` reads 0 lines | not 0: **E (with undesk)** |
| 1 | `rb/s02_window_e222.sh A <YYYY-MM-DD> <last start HH:MM> <last end HH:MM>` (today only; G + 1:30 and G + 3:30, rounded up) | "fits now: an E222 arm A session ..."; "fits now: nothing": no box step: **E (with undesk)** |
| 2 | `uptime` (above 8: `undesk`, wait outside the span as in step 0, `desk` again, then this row again); then `RB_GITLOCK=<the lab-git lock> bash W/slot.sh bash rb/s03_desk_e222.sh A` (a few minutes: the registration's forecast and rules checks take most of it), **never inside the lab-git lock**; step 2 writes only into RB_OUT and never rewrites a registered file (its checks are each script's `--check`, their scratch in RB_OUT through TMPDIR; the frozen scorer's two self-tests through `rb/scorer_check_e222.py` into RB_OUT, compared byte for byte with the committed files; at its end it reads that no file under E222's folder, tools/matmul/mm1, E218's and E220's folders or the seal note's folder is newer than its start marker and that E222's paths are clean again); then `bash W/onelab.sh undesk card-e222` | 0: undesk, go on. A 16 naming **wrote-in-lab** or **status-after** WITHOUT HEAD-moved: something wrote in the lab clone while step 2 ran: **E (with undesk)**, told to the orchestrator; with HEAD-moved beside it (a co-owner's commit wrote those files), the HEAD-moved exception below applies. A 16 naming **E222-has-data**: E222 already has a datum: **E (with undesk)**, told to the orchestrator. Anything else: no box step that day: **E (with undesk)**. Two exceptions, each bounded: a pull whose output shows the upstream did not answer: `undesk` at once, wait outside the span (chunks of at most 9 minutes; at most 3 tries in 30 minutes in all), `desk` again and run step 2 again, else **E**; a 16 naming HEAD-moved (a co-owner committed meanwhile): run step 2 again at once, at most 3 times, else **E (with undesk)** |
| 4 | the look, `../q141k-runbook/k6/s05_look_k6.sh aifoundry3` (it writes the box-login file the scrub reads; on aifoundry3 it gates on no boot: k6's identity-by-continuity rule is aifoundry1's alone) | FREE; a holder: bounded polls (`--wait`), at most 30 minutes, else no session that day: **E** |
| 3 | the day's post: **none**, by the owner's standing waiver of Sun 15 Nov 2026 10:22:36 PST; record his words | |
| 5 | `rb/s07_sync_e222.sh A` | 0 HARNESS OK on the box; 10: a session or runbook job of ours on the box; 16: uncommitted synced paths or a file off its sha256: **E** |
| 6 | `rb/s08_build_e222.sh A start`, then `... wait` while it says 17 | 0: RB_OUT/e222-built-A.txt (rgm136 KERNEL OK and rgm211's tree KERNEL OK, the hosts' twelve refusals in a sandbox, the record). **A failure to build or gate either tree fails the whole build (RGM-BUILD-FAILED, 16), and so the session that day** (both families need rgm136's ELF, the G block also rgm211's host); 16: start once more (two starts a Pacific day at most; a third: NO-THIRD-BUILD, no session that day: **E**); a 14 on wait: no reading, wait again |
| 6n | **THE NEVER-RUN SEARCH, REPEATED RIGHT BEFORE THE FIRST CARD COMMAND** (E222.md 4): `E222_ROUND_OUT=<the round's OUT> bash W/slot.sh bash rb/s06n_neverrun_e222.sh A` (about twenty seconds at the desk, single-threaded: the registration's scanner, unchanged, over the lab at HEAD, the round's card and data lane folders and MM1-v3.2's measured points, every folder whose name holds `e222` or `e220` never opened; then the judgement by session records on aifoundry3 card 0, family R exempt by name, and THE POSITIVE CONTROL); run it when the rest is open or about to open, since step 7 needs its report under 30 minutes old | 0: its line `NEVER-RUN-E222 arm A: <n> of 66 registered non-R points never ran on aifoundry3 card 0 by session records ...; ran before, labelled: <none / ids>; family R: ry01a RAN, ry01b RAN, rg01 RAN, rg01t RAN (exempt by family name: same-card repeats, REPORTED only); the positive control (R's exemption lifted, the same scan): 4 of 4 RAN; the literal reading (REPORTED, not a label): ...` in RB_OUT (REPORTED, never a gate: a point labelled 'ran before' leaves every rule through the scorer's `--labels`, which step 13 passes from the data directory's `labels-e222.json`, and gets a dated note before the data commit, step 12); **16 POSITIVE CONTROL FAILED: the scan cannot see this card's own sessions (E218's four points read never run with the exemption lifted): no card command today, E, and the orchestrator told** (its answer 1: a re-scan with a reader that does, a non-R point found run dropped by a rule stated with the drop); 14: a scan failed: run it again, at most 3 tries in all, else **E**; 10: no window for today (step 1 again, then 6n) or no `E222_ROUND_OUT` (set it to the round's OUT, then 6n again); after three 10s in a row, **E** |
| 7 | **STEP 7 ONLY ONCE THE REST HAS OPENED, WITHIN 30 MINUTES OF 6n**: `rb/s09_reads_e222.sh A` (the 6n report's age and the rest rule on the box first, no card command; then k6's step 7 unchanged: the time stamped and the config read); then 8 and 9 **without delay** | 10 with "the never-run report": run 6n again, then 7; 10 with "the rest has not run": wait in bounded chunks and run it again (6n again if its report passes 30 minutes), never around it; 0: the config read as found (TDP 0 W / 65 C / 600 MHz) and et-who clean; 16 (not as found): no session that day, set nothing: **E**; 17 (et-who not clean): step 4 with `--wait`, then step 7 again |
| 8 | `rb/s10_dry_e222.sh A start`, then `... wait` | 0: E222-DRY arm A rc=0 runs=3 (the doubles on the box, no device: s01, the stop-path test and t01, wn07t, wp04b) **and THE SCRUB CHECK on the dry pass's own records** (copied back read-only, scrubbed on a private copy at the desk by the collection's code: SCRUB-CHECK CLEAN); 16 with SCRUB-CHECK LEFT: the collection would refuse this box's records after the session: no session today, a kit note first: **E** |
| 9 | (the quiet-desk flag on aifoundry2 absent) `rb/s11_session_e222.sh A` | 0 launched (its "rest:", "hung:" and "same-day:" lines in the runbook log; the T0 in RB_OUT/e222-T0-A.txt); 10 refused (no never-run report from today: 6n and 7 first; the rest; a session or job of ours; **a HUNG marker**: a device process of ours did not end after its timeout's TERM: stop, report to the owner, no session that day; the same-day rule; no dry pass or build today): read why, never around it: **E** if the day cannot go on; 16: past the last start, or the cap would pass the last end: **E** |
| 10 | `rb/s20_wait_e222.sh A`, again while it says 17 | 0: ended, MANIFEST-WRITTEN, the runner exited 0 (read its `STOP:` line if one is printed: a stop line, a holder, a kernel stop, an identity gate failure or two failed processes in a row end a session rc 0; the G block dropped by s03 is no stop: read its "FAILED for its family alone" line); **16 HUNG**: KILL NOTHING, reset nothing, keep the booking and the hold, collect what is written (step 11), write it up and escalate to the owner; **16 K1-STOPPED**: a launch did not finish (it may leave a hung hart): collect it, never reset, escalate; **16 CRASHED**: read runner.out read-only, report, then collect; **16 GATE-STOPPED**: no run, still collected as a gate stop's record; 14: gone without "session end" (RUN-GONE) or no runner.rc (read the box read-only first) |
| 11 | `bash W/onelab.sh collect card-e222` (exit 3 at its 9-minute bound: call again, at most 6 calls; the session's files wait on the box; after the sixth 3, **E**: nothing collected, the session's files left on the box untouched and reported, a later collection by a dated note); then `rb/s22_collect_e222.sh A` (start it at least 10 minutes before the last end) | 0 COPY-BACK EXACT; 16 COPY-BACK NOT EXACT (a HUNG process may still be writing its files): commit nothing, read why: **E (with uncollect)**. **Every other exit** (10 refused, 11 a login link, 12 no answer, 13 past a bound, 14 a call failed): `uncollect` at once (nothing is committed yet), read why, wait OUTSIDE the span (chunks of at most 9 minutes; after a login link only once `RB_LOCK`'s check is cleared), then `collect` again and step 11 again: at most 3 tries in 60 minutes in all, else **E**, the session's files left on the box untouched and reported |
| 12 | `bash W/slot.sh bash rb/s23_data_e222.sh A`: the data directory `docs/reports/data/<day>-e222-blind-matmul-aifoundry3/`, or a gate stop's record under `docs/reports/gate-stops/`; the scrub of every form of the box's home, our login and another login's et-who holder lines; the reducer (s03 a smoke RUN at its place); **step 6n's report, judgement and labels** copied in and listed in SHA256SUMS; the desk-path gate; the history check; the README in [DATA-README-FORM-e222.md](DATA-README-FORM-e222.md)'s form; **if step 6n labelled any point 'ran before', a dated note** (`README.md.dated-note-1.md`: the points, the session records the judgement found, and that the scorer's `--labels` takes them out of every rule; the frozen scorer is never changed); the public-text scan; `LAB_QUIET_HOLD_OWNER=card-e222 bash W/commit_lab.sh "<subject>" "<body>" <the collected directory>` (new files only; on exit 5 or 6 run it again); **then** `bash W/onelab.sh uncollect card-e222`, `bash W/hold.sh remove card-e222`, `bash W/book.sh release aifoundry3 card-e222` | "COMMIT_LAB: pushed <sha>"; anything else after the retries: move the collected directory out of the lab clone at once into the lane's own folder (`OUT/card-e222/held/<the directory's name>`, a copy checked against its SHA256SUMS first, then removed from LAB by its literal path), so no untracked file in LAB blocks another card lane's step H; then **E (with uncollect)**, reported (a later lane commits the held directory by a dated note) |
| 13 | after the data commit only, never on a gate stop's record: `bash W/slot.sh bash rb/s24_score_e222.sh A` | step 6n's labels checked (LABELS-OK) and passed to the frozen scorer in its registered call (`score_e222.py --a <data-e222.json> --a-tag A --labels <labels-e222.json> --out RB_OUT/scores-A`): RB_OUT/scores-e222-A.json and .txt (R0, S6, T1-T3, E1-E4, H1-H10, HC-posimb, HC-AF4, HC-L3S, NH-posimb, NH-AF4, NH-L3S, SEL; CX "PENDING E220 DATA": the cross-card rule is the scores lane's, with E220's committed and verified data); read its words; a later lane commits them beside the data |
| E | **every path ends here**: `bash W/onelab.sh undesk card-e222` if inside steps 0-2; `bash W/onelab.sh uncollect card-e222` if between step 11's collect and the data commit's push; then `bash W/hold.sh remove card-e222` and `bash W/book.sh release aifoundry3 card-e222` (on a HUNG or K1 day: keep the booking and the hold until the owner or the orchestrator answers; release them then) | |

**Waits inside a span** (THE ONE-LAB RULE): every wait in this table is bounded (at most 9 minutes a call, with each row's total), and no wait
longer than one call happens inside a span: the load rule waits before `desk`; a step 2 or a step 11 that must wait leaves its span first
(`undesk`, `uncollect`) and enters it again before it is run again; past a row's bound the path ends at **E**. Inside the desk span the lane holds
only step 0's reads, H, step 1 and step 2 (k6's bounded drivers); inside the collect span, step 11 (its 600 s copy) and step 12 (commit_lab.sh's
own bounds: its lock wait of 1,200 s, five push tries).

**To stop the session by hand** (the operator's stop, a registered stop): `touch build/e222/T<T0>-A/STOP` on the box (the host ends at its next
launch boundary; the runner reads the file before every start, so nothing further starts; a STOP file already there when the runner starts is a
refusal, no device opened, the file kept), or SIGTERM to the runner (`run_e222.py`), never to a host or the sampler. A STOP during the smoke ends
the smoke as a gate stop whose words name the stop. Never kill a process: the session ends its own processes and stops its sampler with SIGTERM.

## 3. After a gate stop, the G block dropped by s03, a registered stop, a kernel stop, K1, HUNG or a crash

- **A gate stop** (no run: "refused, no device opened: ..." before any card command, or after the card opened: the start config, the card's
  identity gate, the sampler, the identity read, the session's smoke s01 (an identity gate failing in it among them), the stop-path test) is **no
  session: no data**. Step 12 collects it as a gate stop's record under `docs/reports/gate-stops/`, never `docs/reports/data/`; commit it (new
  files only, its README in the gate-stop form); it is never scored. **E222 may be tried again with no amendment**: after a refusal that opened no
  device, **once more the same day**, once the look reads FREE again and inside the window (step 9 counts the tries: a third is refused); after a
  gate that came after the card opened, **not the same day** (step 9's same-day rule); a try on a later day needs that day's go, the rest, step 0
  and step 6n again. A gate stop by a kit defect is the kit's to fix: a dated kit note and, if it touches the registration, a dated note to
  E222.md before any datum (after FROZEN.txt no point is added or re-chosen and no forecast is changed), verified and landed, then a later session.
- **The G block dropped by its smoke s03** (E222.md 3 and 6: s03 is the G block's own smoke and stop path): s03 failed for its family alone - a
  GATE FAILED (no process started), a check of C wrong or missing, the walk check failed, a tensor error, a launch not ok, an exit not 0 but 124,
  the counter's mean outside 200-4,000, or the board's rise short on a live sampler; or its not starting (the die gate's 300 s). The session log
  reads "smoke s03: FAILED for its family alone (its own stop path, E222.md 3): ... the family 'rgm136 gemmLnc' is DROPPED - k01, ..., wn07 never
  start (NO DATA); the session goes on"; the G runs are "not started" (NO DATA, no card time; queue.json's `families_dropped`). It is **not a gate
  stop and not a kernel stop**: the 98 runs before it stand and are collected and committed as usual; the data README records the drop and the
  smoke's words; the frozen scorer (score_e220.read_a at its pin) reports it (its flag "the G block's smoke s03 failed (...): the G block NO DATA;
  not an R0 failure, REPORTED") and R0 does not count the smoke's own failure while no gemmLnc point ran; HC-AF4 and the G groups of the no-harm
  rules read NO DATA. A failed s03 that is the session's - K1, a HUNG host, a launch timeout (rc 124), the host not shown on card 0, the sampler not
  live after it, or any stop raised during it - stops the session after the runs, which stand. A failed gate or walk at s03 is a kit or build
  defect until shown otherwise: a dated note, and the readiness lane's look at the box's build before any later session of the G block.
- **A registered stop** (the board or die lines, a holder, two failed processes in a row, the card-time rule, the window's end, the operator's
  STOP or SIGTERM) after a run: the runs done stand and are scored as they stand (the registered subset if cut: the opening smoke, tie 1, pass 1 and
  tie 2, every non-gemmLnc point once, the G block not reached: 57 runs, about 24.1 card-minutes); the data directory is committed; the missing runs
  are never re-run without a dated note. **A board stop in the G block** costs only the G runs after it: the block is last by registration.
- **A kernel stop** (a 'rgm136 gemmLnc' process with a check of C wrong, a tensor error, the walk check failed, a launch timeout or a launch not
  ok; or an identity gate failure before any run's process): **nothing more that day**. The runs done stand and are collected and committed as
  above; the stop's words go in the README. A failed identity gate or walk check is a kit or build defect until shown otherwise: a dated note, and
  the readiness lane's look at the box's build before any later session.
- **K1** (a launch that did not finish) and **HUNG** (a device process still alive after its timeout's TERM): the session stops; the card may hold
  a hung hart: **never reset the card, no PMIC or power action, kill nothing** (the field manual's gates). Keep the booking and the hold, collect
  what was written (a HUNG process may keep writing its own files after the manifest: then the copy is not exact; commit nothing until a dated note
  decides), write it up, escalate to the owner and the lab admin. Step 9 refuses every later session of ours on that box while the HUNG line
  stands.
- **A crash** of the runner: named in its log ("CRASH: <type>: <message>"), its closing still run, runner.rc 1; step 10 says 16; report it, collect
  it (a crash with no run is a gate stop's record); never re-run around a crash without a dated note.
- **The runner gone without "session end"** (step 10's RUN-GONE): read the box read-only, collect what is there by a dated note's decision,
  report; the rest rule counts the session at its run's latest write.

## 4. Never

- No step 2 but `rb/s03_desk_e222.sh`, never inside the lab-git lock; no box step without step 0's and step 2's 0 that day; no step out of the
  order above; **never step 7 before the rest has opened, nor without a 6n report under 30 minutes old**; never steps 5, 6 or 8 while a session of
  ours runs (they refuse); never a card command after step 6n's POSITIVE CONTROL FAILED.
- No booking before FROZEN.txt's post is recorded and MM1-v3.2's land, the candidates' lands, the registration commit and the kit commit are on
  GitHub main; no booking over the orchestrator's `orch-hold-e222-seal`; no card lane named anything but `card-e222`.
- No point added or re-chosen and no forecast changed (FROZEN.txt); no change to a band, a rule, a threshold, the order, the card time, the cap or
  a stop except by a dated note before E222's data; no run re-run after a stop without one; the scorer only as registered and only after the data
  commit.
- No device command but the kit's READs (dmcmd_audit_v2 GO): no set, no reset, no governor, TDP, threshold, clock, voltage, fan or firmware
  change; no statistics reset; no PMIC write; no PCIe recovery, no driver reload, no power cycle and nothing that risks one; **never kill a device
  process** (no SIGKILL, no `timeout -k`; a process that does not end after its TERM is reported at once and left).
- Never two sessions of ours on aifoundry3 at once; never beside another user's holder or device process (the session's et-who and ps refuse).
- Never a lab user's login in any file (the collection's scrub masks ours as `<login>` and another login's et-who holder lines as
  `<another-login>`); no number from the owner's private pages or his A100 report in any lab file; no sealed forecast's number anywhere.
- Never touch another run's files on the box: E222 writes only `build/e222rgm/`, `build/e222/`, `build/e222-build-*` and the runbook's own
  `build/q141k/` entries, and step 5's synced files at their committed bytes; step 6n writes nothing on the box.
- Never write in another lane's folder, booking, hold line or onelab flag; never answer a lane by a message (the orchestrator answers through
  files under `W/out/orch/`).

## 5. Labels

Every figure here is **registered** (E222.md) or a **desk check of code** (KIT.md). Nothing here is measured, blind, held out or post hoc.

SPDX-License-Identifier: Apache-2.0
