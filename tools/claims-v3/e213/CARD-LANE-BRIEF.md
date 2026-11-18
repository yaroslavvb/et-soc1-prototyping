# E213's card-lane brief: what the lane that runs an arm of E213, MM1-v3's blind matmul day (A: aifoundry3 card 0; B: aifoundry1 card 1), does, step by step, and what it never does (Q216; kitted, not run)

*Tue 17 Nov 2026 (week 47), PST, on aifoundry2, desk only (Q216, lane `kit-e213`), beside [KIT.md](KIT.md). E211's card-lane brief
(`tools/claims-v3/e211/CARD-LANE-BRIEF.md`, landed in `2b7f261f`, the brief E211 ran FULL by on aifoundry3 card 0) for arm A, and E206's
(`tools/claims-v3/e206/CARD-LANE-BRIEF.md`, landed in `906699ea`, the brief E206 arm B ran FULL by on aifoundry1 card 1) for arm B. The
registration is [E213.md](E213.md) (found by content: the commit that added it; its subtree `75778ad3...`; `SHA256SUMS-e213-registration`
`96e5d168...`, 27 entries: reg-e213's with Amendment A1, fix-e213's). No card was claimed or opened, no device command was sent, nothing was posted. No E213 datum exists. This
brief changes no forecast, band, rule, threshold, the order, the card time, the cap, a stop or the scorer. **Each arm is its own card lane**
(`card-e213a`, `card-e213b`: the never-run scanner subtracts those two folder names, so use exactly them) with its own booking, its own G and its
own RB_OUT; the two arms, on two boxes, may run at the same time (E213.md 6). **New against E211's and E206's briefs:** step 0's checks are a kit
script (`rb/s00_step0_e213.sh`: the arm's FREEZE LINE on GitHub main, the kit, THE SEALED-FORECAST CHECK, no datum of the arm, the clone clean);
arm B's freeze line is the registration commit (the orchestrator's answer 4); step 6n judges every hit against the arm's freeze line and writes the
scorer's labels; step 8 ends with THE SCRUB CHECK on the dry pass's own records (E209's lesson); the four families' identity gate per process.
**Amended by fix-e213 (Wed 18 Nov 2026, before any datum; verify-e213's findings and the orchestrator's answer 5):** arm A's smoke gains s04, the
family 'rgm211 gemmL''s own, with its own stop path (E213.md A1: row 9 and section 3); the queue rows follow Q216's card-lane text on QUEUE
CANCELLED (keep waiting); row 6 says what a failed rgm211 build costs arm B; the collection's scrub masks another login's et-who holder lines.*

## 1. What the go must carry (E213.md 6)

- **The owner's go**, on the round's reading: his standing words of Sun 15 Nov 2026 ("continue, all machines are up", 10:05:42 PST; "don't
  worry about discord post, just use the machines, nobody is using them", 10:22:36; "Feel free to use more cards in parallel, I don't need to
  reserve them", 17:21:16), "Try again" (received at or before 21:28:59) and "don't worry about hitting the limit, I will use a reset, feel free
  to run things overnight and in parallel" (at or before 21:51:09), his matmul focus of Mon 16 Nov 2026 (received at or before 09:48:24: "... just
  go as far as possible on the matte mold, on the FME, yeah, on the matmul operation"), his words relayed on the coordination thread (Mon 16 Nov
  2026, 11:01:08 PST: "feel free to use all the cards without restriction"; 23:15:25 PST: "There's no deadline; use the cards all night"), and
  Tue 17 Nov 2026: "Try again" (at or before 06:40:56 PST) and "Continue from where you left off" (twice, at or before 16:4x PST), with E213's
  registered items as its defaults, once E213 is registered, kitted, verified, landed and readiness-checked. Record them as dated departures in
  the data README: the registered items as their defaults; G = the booking on its day; the post waived; the package counter not read; the desk
  aifoundry2 with Python 3.12.3; the yvb3 session.
- **Arm A**: aifoundry3 card 0 at its pinned 600 MHz (a boot-time TDP of 0 latches the governor), reads only, nothing set; after the round's queue
  on aifoundry3 (the readiness lane's go lines name the queue helper's call); **46.3 card-minutes planned (E213.md A1: the smoke's four processes),
  no run after 60, cap 70**. Its freeze
  line, MM1-v3's land `b1493082` (pushed 20:52:46 PST Tue 17 Nov 2026), is on GitHub main.
- **Arm B**: aifoundry1 card 1 at 600 MHz as found, **ET_DEVICES=1 on every device process, card 1's lock, nothing on card 0 ever, one session of
  ours on aifoundry1 at a time** (either card; the model session's sweeps included); **32.5 card-minutes planned, no run after 42, cap 48**. **Its
  freeze line is the registration commit's push** (the orchestrator's answer 4, Tue 17 Nov 2026 21:27 PST: "ready-e213's go lines must require
  that commit on GitHub main before arm B's booking, and card-e213b must check it at step 0"): step 0's F1 line. **Conditional**: while a claim
  of the model session's stands on aifoundry1 the queue helper prints QUEUE CANCELLED (exit 4): **keep waiting in bounded chunks** - book nothing,
  make no ssh call to aifoundry1 while the claim stands - **at most until 20:29:00 PST Wed 18 Nov 2026, then SKIPPED** (Q216's card-lane text;
  fix-e213, verify-e213's finding 5: this brief said "return SKIPPED" at once).
- **The rest**: each arm's first card command (step 7's config read included) at least 40 minutes after the end of the last session on that box
  (arm A: ours on aifoundry3, E211's ended 13:39:35 PST Tue 17 Nov 2026; arm B: either card of aifoundry1, ours or the model session's, E212's
  a1c1-S3 ended 14:22:13 PST Tue 17 Nov 2026 by the orchestrator's release record, any later release counting). Read it by the clock from the
  last card lane's records BEFORE the booking; steps 7 and 9 read it on the box again.
- **The window**: G = this lane's booking of the arm's box that day; last start G + 1:30, last end G + 3:30, both rounded up to the minute,
  inside G's Pacific day; G at 20:29:00 PST or earlier. **Step 9 launches by the last start** (k6's `rb_need_start`; the cap and 5 minutes
  before the last end, E213_BUDGET_S arm A 4,500 s and arm B 3,180 s, would allow G + 2:15 and G + 2:37: the last start binds) and the runner keeps
  every run inside the last end.
- **The post**: none, by the standing waiver (record his words of 10:22:36). **The host's package counter**: not read.
- **The registration and the kit landed and on GitHub main** (registration first, then the kit), no datum of this arm in any ref (steps 0 and 2
  refuse).
- **A sealed forecast** (E213.md 0; the orchestrator's answer 2): a seal the model session posts before an arm books is recorded in
  `W/out/orch/sealed-e213.txt` only after it is registered in `tools/claims-v3/sealed-e213/e213-freeze-lines.md`, and the orchestrator holds that
  arm's booking meanwhile (`book.sh take <box> orch-hold-e213-seal`). Step 0's S1 line reads both: a sealed sha256 the record lists and the note
  at HEAD does not register stops the day before the box (tell the orchestrator; the note lands first). A seal posted after an arm booked is
  REPORTED as sealed during that arm's session.
- **THE QUIET DESK FLAG on aifoundry2** (the round's flag for a session on aifoundry2's own card): while it is up, run neither step 9
  (its file name holds `session_e213.sh`, which a text-matching session count on aifoundry2 would read) nor any desk test of this kit; wait in
  bounded chunks.

## 2. The steps, in order (paths under `tools/claims-v3/e213/`; `<arm>` is A or B, `<box>` aifoundry3 or aifoundry1)

Run from the lab clone (`cd $LAB`), ONE RB_OUT for this arm (a new directory outside the repo), the one `RB_LOCK` (the round's file of login
checks), for step 2 `RB_GITLOCK` (the lab-git lock), and for step 6n `E213_ROUND_OUT` (the round's OUT). Each step one plain call from a script
file. k6's drivers bound every remote call: a 15 s probe, then 60 s for a read, 600 s for a copy or one bounded wait (520 s), a detached launch
that returns at once, 5,400 s for a desk call. **A printed login link stops the step (11) and appends `<HH:MM:SS> <box> needs a check` to
`RB_LOCK`:** nothing is retried until it is cleared, and a session detached on the box keeps running. k6's exit codes: 0 done; 10 refused; 11 a
login link; 12 no answer; 13 past a bound; 14 a call failed; 15 a holder for 30 minutes; 16 a gate says stop; 17 call again. **E** is the end of
every path (below): it carries undesk and uncollect where they are due.

| # | the step | what to do with its exit |
|---|---|---|
| B | the queue (the readiness lane's go lines: wait in bounded chunks until QUEUE OVER; **while QUEUE BUSY or QUEUE CANCELLED keep waiting**, booking nothing and making no ssh call to that box while a claim stands, **at most until 20:29:00 PST Wed 18 Nov 2026, then SKIPPED**: Q216's card-lane text); **arm B: the registration commit on GitHub main** (the go lines read it; step 0 reads it again); `bash W/book.sh show`: a line `orch-hold-e213-seal` on the box means the orchestrator is registering a seal: wait (bounded), never book over it; then the rest by the clock (section 1), then THE DAY (G at 20:29:00 or earlier; later: wait in bounded chunks until 00:00:30 the next day); then `bash W/book.sh take <box> <lane>` | 0 BOOKED: G = this moment. 1: another lane (or the orchestrator's hold) holds it: make no ssh call to that box at all; wait (bounded) or stop (nothing else to undo) |
| 0 | `uptime` FIRST, OUTSIDE the span (THE LOAD RULE: above 8, wait in bounded chunks of at most 9 minutes until below 6, at most 60 minutes in all; past that, no box step that day: **E**); then `bash W/onelab.sh desk <lane>` (THE ONE-LAB RULE: steps 0, H and 2 never overlap another lane's collect span or a commit of ours; exit 3 at its 9-minute bound: call again, at most 6 calls, else **E**); E213's anchor lines (the land record, `OUT/q216-anchor-lines-e213.txt`, if the readiness lane names one); then **`E213_SEALED=W/out/orch/sealed-e213.txt bash rb/s00_step0_e213.sh <arm>`** (one call, read only, with the round's environment-only git rewrite set by the caller: S0 GitHub main and HEAD; **F1 the arm's freeze line an ancestor of GitHub main** (arm A `b1493082`; arm B the registration commit, found by content); F2 the kit commit; **S1 THE SEALED-FORECAST CHECK** (every sealed sha256 of the record registered in the note at HEAD; "0 of 0" with no record); S2 the seal note's commits; D0 no datum of this arm in any ref; G1 the clone clean) | `STEP0-E213 arm <arm>: 5 of 5 as stated` (exit 0): go on. Exit 1, any line NOT AS STATED: no box step that day: **E (with undesk)**; an S1 line NOT AS STATED is also told to the orchestrator (the seal's note lands first). Exit 2: a usage error (E213_SEALED unset): fix the call, then step 0 again |
| H | `bash W/hold.sh add <lane>` (THE QUIET HOLD, one owner a line, until the data commit); `git -C $LAB status --porcelain --untracked-files=all` reads 0 lines | not 0: **E (with undesk)** |
| 1 | `rb/s02_window_e213.sh <arm> <YYYY-MM-DD> <last start HH:MM> <last end HH:MM>` (today only; G + 1:30 and G + 3:30, rounded up) | "fits now: an E213 arm <arm> session ..."; "fits now: nothing": no box step: **E (with undesk)** |
| 2 | `uptime` (above 8: `undesk`, wait outside the span as in step 0, `desk` again, then this row again); then `RB_GITLOCK=<the lab-git lock> rb/s03_desk_e213.sh <arm>` (about 2 minutes: the registration's rules check and the scorer's stand-in self-test take most of it), **never inside the lab-git lock**; then `bash W/onelab.sh undesk <lane>` | 0: undesk, go on. A 16 naming **E213-arm-<arm>-has-data**: this arm already has a datum: **E (with undesk)**, told to the orchestrator. Anything else: no box step that day: **E (with undesk)**. Two exceptions, each bounded: a pull whose output shows the upstream did not answer: `undesk` at once, wait outside the span (chunks of at most 9 minutes; at most 3 tries in 30 minutes in all), `desk` again and run step 2 again, else **E**; a 16 naming HEAD-moved (a co-owner committed meanwhile): run step 2 again at once, at most 3 times, else **E (with undesk)** |
| 4 | the look, `../q141k-runbook/k6/s05_look_k6.sh <box>` (it writes the box-login file the scrub reads) | FREE; a holder: bounded polls (`--wait`), at most 30 minutes, else no session that day: **E** |
| 3 | the day's post: **none**, by the owner's standing waiver of Sun 15 Nov 2026 10:22:36 PST; record his words | |
| 5 | `rb/s07_sync_e213.sh <arm>` | 0 HARNESS OK on the box; 10: a session or runbook job of ours on the box; 16: uncommitted synced paths or a file off its sha256: **E** |
| 6 | `rb/s08_build_e213.sh <arm> start`, then `... wait` while it says 17 | 0: RB_OUT/e213-built-<arm>.txt (both kernels KERNEL OK; on arm B rgm136 at its whole ELF and "the hosts and /opt/et/lib/libdeviceLayer.a carry ET_DEVICES", else 16 and no session of arm B that day). **On arm B, rgm211's host is built here for s14 and k37-k40 (this desk cannot pass aifoundry1's ET_DEVICES gate, so this is its first real build): a failure to build or gate it fails the whole build (RGM-BUILD-FAILED, 16), and so arm B's whole session that day - not k37-k40 alone (E213.md A1 clause 6; fix-e213, verify-e213's finding 8): report it;** 16: start once more (two starts a Pacific day at most; a third: NO-THIRD-BUILD, no session that day: **E**); a 14 on wait: no reading, wait again |
| 6n | **THE NEVER-RUN SEARCH, REPEATED RIGHT BEFORE THE FIRST CARD COMMAND** (E213.md 4): `E213_ROUND_OUT=<the round's OUT> rb/s06n_neverrun_e213.sh <arm>` (well under a minute at the desk, 8 s an arm on the kit lane's run: the registration's scanner, unchanged, over the lab at HEAD and the round's card and data lane folders, E213's own folders subtracted, then the judgement against the arm's freeze line); run it when the rest is open or about to open, since step 7 needs its report under 30 minutes old | 0: its line `NEVER-RUN-E213 arm <arm>: <n> of <n> scored points never ran ...; ran before the freeze line (...), labelled: <none / ids>; ran after it (REPORTED, kept): <none / ids>` in RB_OUT (REPORTED, never a gate: a point labelled 'ran before' leaves every rule through the scorer's `--labels`, which step 13 passes from the data directory's `labels-e213.json`, and gets a dated note before the data commit, step 12); 14: a scan failed: run it again, at most 3 tries in all, else **E**; 10: no window for today (step 1 again, then 6n) or no `E213_ROUND_OUT` (set it to the round's OUT, then 6n again); after three 10s in a row, **E** |
| 7 | **STEP 7 ONLY ONCE THE REST HAS OPENED, WITHIN 30 MINUTES OF 6n**: `rb/s09_reads_e213.sh <arm>` (the 6n report's age and the rest rule on the box first, no card command; then the time stamped and the config read: arm A k6's step 7 unchanged; arm B E206's card-1 read through E213's guard with ET_DEVICES=1 and card 1's lock, its identity lines and card 0 clean); then 8 and 9 **without delay** | 10 with "the never-run report": run 6n again, then 7; 10 with "the rest has not run": wait in bounded chunks and run it again (6n again if its report passes 30 minutes), never around it; 0: the config read as found (arm A TDP 0 W / 65 C / 600 MHz; arm B TDP 65 W / 65 C / 600 MHz, minion_mv below 510, /dev/et1_mgmt and physical ID 1 alone) and et-who clean; 16 (not as found): no session that day, set nothing: **E**; 17 (et-who not clean): step 4 with `--wait`, then step 7 again |
| 8 | `rb/s10_dry_e213.sh <arm> start`, then `... wait` | 0: E213-DRY arm <arm> rc=0 runs=3 (the doubles on the box, no device) **and THE SCRUB CHECK on the dry pass's own records** (copied back read-only, scrubbed on a private copy at the desk by the collection's code: SCRUB-CHECK CLEAN); 16 with SCRUB-CHECK LEFT: the collection would refuse this box's records after the session: no session today, a kit note first: **E** |
| 9 | (the quiet-desk flag on aifoundry2 absent) `rb/s11_session_e213.sh <arm>` | 0 launched (its "rest:", "hung:" and "same-day:" lines in the runbook log; the T0 in RB_OUT/e213-T0-<arm>.txt); 10 refused (no never-run report from today: 6n and 7 first; the rest; a session or job of ours; **a HUNG marker**: a device process of ours did not end after its timeout's TERM: stop, report to the owner, no session that day; the same-day rule; no dry pass or build today): read why, never around it: **E** if the day cannot go on; 16: past the last start, or the cap would pass the last end: **E** |
| 10 | `rb/s20_wait_e213.sh <arm>`, again while it says 17 | 0: ended, MANIFEST-WRITTEN, the runner exited 0 (read its `STOP:` line if one is printed: a stop line, a holder, a kernel stop, an identity gate failure or two failed processes in a row end a session rc 0); **16 HUNG**: KILL NOTHING, reset nothing, keep the booking and the hold, collect what is written (step 11), write it up and escalate to the owner; **16 K1-STOPPED**: a launch did not finish (it may leave a hung hart): collect it, never reset, escalate; **16 CRASHED**: read runner.out read-only, report, then collect; **16 GATE-STOPPED**: no run, still collected as a gate stop's record; 14: gone without "session end" (RUN-GONE) or no runner.rc (read the box read-only first) |
| 11 | `bash W/onelab.sh collect <lane>` (exit 3 at its 9-minute bound: call again, at most 6 calls; the session's files wait on the box; after the sixth 3, **E**: nothing collected, the session's files left on the box untouched and reported, a later collection by a dated note); then `rb/s22_collect_e213.sh <arm>` (start it at least 10 minutes before the last end) | 0 COPY-BACK EXACT; 16 COPY-BACK NOT EXACT (a HUNG process may still be writing its files): commit nothing, read why: **E (with uncollect)**. **Every other exit** (10 refused, 11 a login link, 12 no answer, 13 past a bound, 14 a call failed): `uncollect` at once (nothing is committed yet), read why, wait OUTSIDE the span (chunks of at most 9 minutes; after a login link only once `RB_LOCK`'s check is cleared), then `collect` again and step 11 again: at most 3 tries in 60 minutes in all, else **E**, the session's files left on the box untouched and reported |
| 12 | `rb/s23_data_e213.sh <arm>` (the data directory `docs/reports/data/<day>-e213-blind-matmul-<aifoundry3 / aifoundry1-c1>/`, or a gate stop's record under `docs/reports/gate-stops/`; the scrub of every form of the box's home; the reducer; **step 6n's report, judgement and labels** copied in and listed in SHA256SUMS; the desk-path gate; the history check); the README in [DATA-README-FORM-e213.md](DATA-README-FORM-e213.md)'s form; **if step 6n labelled any point 'ran before', a dated note** (`README.md.dated-note-1.md`: the points, the files and dates the judgement found, and that the scorer's `--labels` takes them out of every rule; the frozen scorer is never changed); the public-text scan; `LAB_QUIET_HOLD_OWNER=<lane> bash W/commit_lab.sh "<subject>" "<body>" <the collected directory>` (new files only; on exit 5 or 6 run it again); **then** `bash W/onelab.sh uncollect <lane>`, `bash W/hold.sh remove <lane>`, `bash W/book.sh release <box> <lane>` | "COMMIT_LAB: pushed <sha>"; anything else after the retries: move the collected directory out of the lab clone at once into the lane's own folder (`OUT/<lane>/held/<the directory's name>`, a copy checked against its SHA256SUMS first, then removed from LAB by its literal path), so no untracked file in LAB blocks another card lane's step H; then **E (with uncollect)**, reported (a later lane commits the held directory by a dated note) |
| 13 | after the data commit only, never on a gate stop's record: `rb/s24_score_e213.sh <arm>` | step 6n's labels checked (LABELS-OK) and passed to the frozen scorer: RB_OUT/scores-e213-<arm>.json and .txt (this arm's rules; the other arm and the pooled HP1-HP5 NO DATA in this file: the scores lane scores the pooled rules once both arms are committed); read its words; a later lane commits them beside the data |
| E | **every path ends here**: `bash W/onelab.sh undesk <lane>` if inside steps 0-2; `bash W/onelab.sh uncollect <lane>` if between step 11's collect and the data commit's push; then `bash W/hold.sh remove <lane>` and `bash W/book.sh release <box> <lane>` (on a HUNG or K1 day: keep the booking and the hold until the owner or the orchestrator answers; release them then) | |

**Waits inside a span** (THE ONE-LAB RULE): every wait in this table is bounded (at most 9 minutes a call, with each row's total), and no wait
longer than one call happens inside a span: the load rule waits before `desk`; a step 2 or a step 11 that must wait leaves its span first
(`undesk`, `uncollect`) and enters it again before it is run again; past a row's bound the path ends at **E**. Inside the desk span a lane holds
only step 0's reads, H, step 1 and step 2 (k6's bounded drivers); inside the collect span, step 11 (its 600 s copy) and step 12 (commit_lab.sh's
own bounds: its lock wait of 1,200 s, five push tries).

**To stop the session by hand** (the operator's stop, a registered stop): `touch build/e213/T<T0>-<arm>/STOP` on the box (the host ends at its
next launch boundary; the runner reads the file before every start, so nothing further starts; a STOP file already there when the runner starts
is a refusal, no device opened, the file kept), or SIGTERM to the runner (`run_e213.py`), never to a host or the sampler. A STOP during the smoke
ends the smoke as a gate stop whose words name the stop. Never kill a process: the session ends its own processes and stops its sampler with
SIGTERM.

## 3. After a gate stop, a registered stop, a kernel stop, K1, HUNG or a crash

- **A gate stop** (no run: "refused, no device opened: ..." before any card command, or after the card opened: the start config, the card's
  identity gate, the sampler, the identity read, the smoke (an identity gate per process failing in it among them; on arm A's s04 only a failure
  that is the session's, below), the stop-path test) is **no session: no data**.
- **A family dropped by its smoke (arm A's s04, E213.md A1: its own stop path)**: s04 failed for its family alone - a GATE FAILED (no process
  started), a check of C wrong or missing, the walk check failed, a tensor error, a launch not ok, an exit not 0 but 124, the counter's mean
  outside 200-4,000, or the board's rise short on a live sampler. The session log reads "smoke s04: FAILED for its family alone (Amendment A1: its own stop path):
  ... the family 'rgm211 gemmL' is DROPPED", then "smoke gate passed: the runs start (Amendment A1: ...)"; the session goes on; a074, a078, a081
  and a085 are "not started" (NO DATA, no card time; queue.json's `families_dropped`). It is **not a gate stop and not a kernel stop**: the runs
  stand and are collected and committed as usual; the data README records the drop and s04's words; the frozen scorer reports it (the flag "A1:
  the family smoke of 'rgm211 gemmL' failed ...") and R0 does not count s04's own failure while none of the four ran. A failed s04 that is the
  session's - K1, a HUNG host, a launch timeout (rc 124), the host not shown on the arm's card, the sampler not live after it, or any stop raised
  during it - is a gate stop as at s01-s03. A failed gate or walk at s04 is a kit or build defect until shown otherwise: a dated note, and the readiness lane's look at the box's
  build before any later session of that family. Step 12 collects it as a gate stop's record under `docs/reports/gate-stops/`, never `docs/reports/data/`; commit it (new
  files only, its README in the gate-stop form); it is never scored. **That arm may be tried again with no amendment**: after a refusal that
  opened no device, **once more the same day**, once the look reads FREE again and inside the window (step 9 counts the tries: a third is
  refused); after a gate that came after the card opened, **not the same day** (step 9's same-day rule); a try on a later day needs that day's
  go, the rest, step 0 and step 6n again. A gate stop by a kit defect is the kit's to fix: a dated kit note and, if it touches the registration, a
  dated amendment to E213.md before any datum of that arm, verified and landed, then a later session.
- **A registered stop** (the board or die lines, a holder, two failed processes in a row, the card-time rule, the window's end, the operator's
  STOP or SIGTERM) after a run: the runs done stand and are scored as they stand (the registered subset if cut: the smoke, tie 1, pass 1 and tie
  2: arm A 92 runs, arm B 43); the data directory is committed; the missing runs are never re-run without a dated amendment.
- **A kernel stop** (plan-e213.json's kernel stops: an rgm211-host process ('rgm136 gemmLnc', 'rgm211 gemmLn', 'rgm211 gemmL') with a check of
  C wrong, a tensor error, the walk check failed, a launch timeout or a launch not ok; or an identity gate failure before any process):
  **nothing more that day on that arm**. The runs done stand and are collected and committed as above; the stop's words go in the README. A
  failed identity gate or walk check is a kit or build defect until shown otherwise: a dated note, and the readiness lane's look at the box's
  build before any later session.
- **K1** (a launch that did not finish) and **HUNG** (a device process still alive after its timeout's TERM): the session stops; the card may
  hold a hung hart: **never reset the card, no PMIC or power action, kill nothing** (the field manual's gates). Keep the booking and the hold,
  collect what was written (a HUNG process may keep writing its own files after the manifest: then the copy is not exact; commit nothing until a
  dated note decides), write it up, escalate to the owner and the lab admin. Step 9 refuses every later session of ours on that box while the
  HUNG line stands.
- **A crash** of the runner: named in its log ("CRASH: <type>: <message>"), its closing still run, runner.rc 1; step 10 says 16; report it,
  collect it (a crash with no run is a gate stop's record); never re-run around a crash without a dated note.
- **The runner gone without "session end"** (step 10's RUN-GONE): read the box read-only, collect what is there by a dated note's decision,
  report; the rest rule counts the session at its run's latest write.

## 4. Never

- No step 2 but `rb/s03_desk_e213.sh`, never inside the lab-git lock; no box step without step 0's and step 2's 0 that day; no step out of the
  order above; **never step 7 before the rest has opened, nor without a 6n report under 30 minutes old**; never steps 5, 6 or 8 while a session
  of ours runs (they refuse).
- **No booking of arm B before the registration commit is on GitHub main**; no booking over the orchestrator's `orch-hold-e213-seal`.
- No change to a forecast, a band, a rule, a threshold, the order, the card time, the cap or a stop except by a dated amendment before that arm's
  data (E213.md, Amendments); no run re-run after a stop without one; the scorer only as registered and only after the data commit.
- No device command but the kit's READs (dmcmd_audit_v2 GO): no set, no reset, no governor, TDP, threshold, clock, voltage, fan or firmware
  change; no statistics reset; no PMIC write; no PCIe recovery, no driver reload, no power cycle and nothing that risks one; **never kill a device
  process** (no SIGKILL, no `timeout -k`; a process that does not end after its TERM is reported at once and left).
- **On aifoundry1: nothing on card 0, ever** (ET_DEVICES=1 on every device process, card 1's lock), and **one session of ours on the box at a
  time** (either card). Never two sessions of ours on a box at once; never beside another user's holder or device process (the session's et-who
  and ps refuse).
- Never a lab user's login in any file (the collection's scrub masks ours; write `<login>`); no number from the owner's private pages or his
  A100 report in any lab file; no sealed forecast's number anywhere.
- Never touch another run's files on the box: E213 writes only `build/e213rgm/`, `build/e213/`, `build/e213-build-*` and the runbook's own
  `build/q141k/` entries, and step 5's synced files at their committed bytes; step 6n writes nothing on the box.
- Never write in another lane's folder, booking, hold line or onelab flag; never answer a lane by a message (the orchestrator answers through
  files under `W/out/orch/`).

## 5. Labels

Every figure here is **registered** (E213.md) or a **desk check of code** (KIT.md). Nothing here is measured, blind, held out or post hoc.

SPDX-License-Identifier: Apache-2.0
