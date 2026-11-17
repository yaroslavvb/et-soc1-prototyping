# E211's card-lane brief: what the lane that runs E211, the second kernel, on aifoundry3 card 0 does, step by step, and what it never does (Q204; kitted, not run)

*Tue 17 Nov 2026 (week 47), PST, on aifoundry2, desk only (Q204, lane `kit-e211`), beside [KIT.md](KIT.md). E206's card-lane brief
(`tools/claims-v3/e206/CARD-LANE-BRIEF.md`, landed in `906699ea`, the brief E206 arm A ran FULL by on this card), as E207's kit ported it to one
arm (Q199, not landed when this was written), for E211. The registration is [E211.md](E211.md) (found by content: the commit that added it; its
subtree `fa109d01...`; `SHA256SUMS-e211-registration` `477fb113...`, 38 entries: reg-e211's with Amendment A1, made by Q204's fix-e211 before any
datum and before the land; at the kit lane `c27487b7...` and `7c11c733...`, 37). No card was claimed or opened, no device command was sent,
nothing was posted. No E211 datum exists. This brief changes no forecast, band, rule, threshold, the order, the card time, the cap, a stop or the
scorer. **New against E206's brief:** E207's step 6n (the never-run search repeated right before the first card command, E211.md section 4) and
step 7's refusal without a fresh 6n report; the queue (after E207's data commit and E210); THE IDENTITY GATE PER PROCESS, THE WALK CHECK and THE
KERNEL STOPS inside the session (KIT.md 4); the two kernels' build; the 35-minute cap (the registered last start G + 1:30 binds the launch).*

## 1. What the go must carry (E211.md 8)

- **The owner's go**, on the round's reading: his standing words of Sun 15 Nov 2026 ("continue, all machines are up", 10:05:42 PST; "don't
  worry about discord post, just use the machines, nobody is using them", 10:22:36; "Feel free to use more cards in parallel, I don't need to
  reserve them ..., feel free to use more in parallel", 17:21:16), "Try again" (received at or before 21:28:59) and "don't worry about hitting
  the limit, I will use a reset, feel free to run things overnight and in parallel" (at or before 21:51:09), his matmul focus of Mon 16 Nov 2026
  (received at or before 09:48:24: "... just go as far as possible on the matte mold, on the FME, yeah, on the matmul operation"; through the
  model session's coordination post #2.6.2 at 11:01:08, "feel free to use all the cards without restriction"; and through its #10.13.1 at
  23:15:25, "There's no deadline; use the cards all night"), with E211's registered items as its defaults, once E211 is registered, kitted,
  verified, landed and readiness-checked. Record them as dated departures in the data README: the registered items as their defaults; G = the
  booking on its day; the post waived; the package counter not read; the desk aifoundry2 with Python 3.12.3; the yvb3 session.
- **The card**: aifoundry3 card 0 at its pinned 600 MHz (a boot-time TDP of 0 latches the governor), reads only, nothing set; **after the
  round's queue on aifoundry3** (the queue helper `python3 W/out/orch/queue_state.py aifoundry3 e207 e210` reads QUEUE OVER; QUEUE CANCELLED
  (exit 4) is SKIPPED, no booking) **and after E207's data commit on GitHub main** (E211.md 8: E211 books no card, on any box, before it: its
  twins 2x3x2, 3x3x4 and 6x6x6 fp32 are E207 blind points). **No exception** (fix-e211, E211.md A1 clause 4): if E207's chain stops short
  of its card day, E211 does not book until the orchestrator's dated ruling and a dated amendment of E211 (for example one swapping those three
  twins) are landed; step 2 refuses while no `docs/reports/data/*e207*` folder is at HEAD. 20.4 card-minutes planned, no run after 30, cap 35.
- **The rest**: the first card command (step 7's config read included) at least 40 minutes after the end of our previous session on aifoundry3,
  whatever its form (the model session's folders `~/claude/work/ee-*/` count too). Read it by the clock from the last card lane's records
  BEFORE the booking (E210's or E207's, whichever ran last there); steps 7 and 9 read it on the box again.
- **The window**: G = this lane's booking of aifoundry3 that day; last start G + 1:30, last end G + 3:30, both rounded up to the minute, inside
  G's Pacific day; G at 20:29:00 PST or earlier. **Step 9 launches by the last start** (k6's `rb_need_start`; the 35-minute cap and 5 minutes
  before the last end, E211_BUDGET_S 2,400 s, would allow G + 2:50: the last start binds) and the runner keeps every run inside the last end.
- **The post**: none, by the standing waiver (record his words of 10:22:36). **The host's package counter**: not read.
- **The registration and the kit landed and in HEAD** (registration first, then the kit), no E211 datum in any ref (step 2 refuses).
- **A sealed forecast** (E211.md 0): if the round's record of sealed forecasts (`W/out/orch/sealed-e211.txt`) lists a sealed sha256 for E211 that
  `tools/claims-v3/sealed-e211/e211-freeze-lines.md` at HEAD does not register, do not book: tell the orchestrator (the note lands first, under
  the desk-commit rule). A sha256 posted after the first datum is REPORTED as post-data.
- **THE QUIET DESK FLAG on aifoundry2**: while the round's quiet-desk flag for aifoundry2 is up (a session on aifoundry2's own card), run neither
  step 9 (its file name holds `session_e211.sh`, which a text-matching session count on aifoundry2 would read) nor any desk test of this kit; wait
  in bounded chunks.
- **Before the card** (E211.md 8): the kit built rgm211 on aifoundry3 (its `.text` 82c79807... and loadable identity 1351a569..., the pins) and
  ran THE KERNEL CHECK under the simulator there (`logs/simcheck-e211.txt`: SIMCHECK-E211 7 of 7 AS STATED, a gemmLn process on rgm136's ELF seen to
  fail its walk check). If a readiness lane finds that record missing or NOT RUN, it re-runs the check before the card.

## 2. The steps, in order (paths under `tools/claims-v3/e211/`)

Run from the lab clone (`cd $LAB`), ONE RB_OUT for E211's day (a new directory outside the repo), the one `RB_LOCK` (the round's file of login
checks), for step 2 `RB_GITLOCK` (the lab-git lock), and for step 6n `E211_ROUND_OUT` (the round's OUT). Each step one plain call from a script
file. k6's drivers bound every remote call: a 15 s probe, then 60 s for a read, 600 s for a copy or one bounded wait (520 s), a detached launch
that returns at once, 5,400 s for a desk call. **A printed login link stops the step (11) and appends `<HH:MM:SS> aifoundry3 needs a check` to
`RB_LOCK`:** nothing is retried until it is cleared, and a session detached on the box keeps running. k6's exit codes: 0 done; 10 refused; 11 a
login link; 12 no answer; 13 past a bound; 14 a call failed; 15 a holder for 30 minutes; 16 a gate says stop; 17 call again. **E** is the end of
every path (below): it carries undesk and uncollect where they are due.

| # | the step | what to do with its exit |
|---|---|---|
| B | the queue (`python3 W/out/orch/queue_state.py aifoundry3 e207 e210`: QUEUE OVER; QUEUE CANCELLED is SKIPPED, no booking) AND E207's data commit on GitHub main (no exception: an E207 chain that stopped short is not E207's data commit; that needs the orchestrator's dated ruling and a dated amendment of E211 first, and step 2 refuses without it), then the rest by the clock (section 1), then THE DAY (G at 20:29:00 or earlier; later: wait in bounded chunks until 00:00:30 the next day); then `bash W/book.sh take aifoundry3 <lane>` | 0 BOOKED: G = this moment. 1: another lane holds it: make no ssh call to aifoundry3 at all; wait (bounded) or stop (nothing else to undo) |
| 0 | `uptime` FIRST, OUTSIDE the span (THE LOAD RULE: above 8, wait in bounded chunks of at most 9 minutes until below 6, at most 60 minutes in all; past that, no box step that day: **E**); then `bash W/onelab.sh desk <lane>` (THE ONE-LAB RULE: steps 0, H and 2 never overlap another lane's collect span or a commit of ours; exit 3 at its 9-minute bound: call again, at most 6 calls, else **E**); GitHub main read; E211's anchor lines (the land record, `OUT/q204-anchor-lines-e211.txt`); the sealed-forecast check (section 1) | any line not as stated: no box step that day: **E (with undesk)** |
| H | `bash W/hold.sh add <lane>` (THE QUIET HOLD, one owner a line, until the data commit); `git -C $LAB status --porcelain --untracked-files=all` reads 0 lines | not 0: **E (with undesk)** |
| 1 | `rb/s02_window_e211.sh A <YYYY-MM-DD> <last start HH:MM> <last end HH:MM>` (today only; G + 1:30 and G + 3:30, rounded up) | "fits now: an E211 session ..."; "fits now: nothing": no box step: **E (with undesk)** |
| 2 | `uptime` (above 8: `undesk`, wait outside the span as in step 0, `desk` again, then this row again); then `RB_GITLOCK=<the lab-git lock> rb/s03_desk_e211.sh A`, **never inside the lab-git lock**; then `bash W/onelab.sh undesk <lane>` | 0: undesk, go on. A 16 whose failure list holds **E207-data** (no `docs/reports/data/*e207*` folder at HEAD: fix-e211, A1 clause 4): E207's data commit is not on GitHub main, so this lane should not have booked: **E (with undesk)**, told to the orchestrator. Anything else: no box step that day: **E (with undesk)**. Two exceptions, each bounded: a pull whose output shows the upstream did not answer: `undesk` at once, wait outside the span (chunks of at most 9 minutes; at most 3 tries in 30 minutes in all), `desk` again and run step 2 again, else **E**; a 16 naming HEAD-moved (a co-owner committed meanwhile): run step 2 again at once, at most 3 times, else **E (with undesk)** |
| 4 | the look, `../q141k-runbook/k6/s05_look_k6.sh aifoundry3` (it writes the box-login file step 12's scrub reads) | FREE; a holder: bounded polls (`--wait`), at most 30 minutes, else no session that day: **E** |
| 3 | the day's post: **none**, by the owner's standing waiver of Sun 15 Nov 2026 10:22:36 PST; record his words | |
| 5 | `rb/s07_sync_e211.sh A` | 0 HARNESS OK on the box; 10: a session or runbook job of ours on the box; 16: uncommitted synced paths or a file off its sha256: **E** |
| 6 | `rb/s08_build_e211.sh A start`, then `... wait` while it says 17 | 0: RB_OUT/e211-built-A.txt (both kernels KERNEL OK, the hosts' twelve refusals); 16: start once more (two starts a Pacific day at most; a third: NO-THIRD-BUILD, no session that day: **E**); a 14 on wait: no reading, wait again |
| 6n | **THE NEVER-RUN SEARCH, REPEATED RIGHT BEFORE THE FIRST CARD COMMAND** (E211.md 4): `E211_ROUND_OUT=<the round's OUT> rb/s06n_neverrun_e211.sh A` (a couple of minutes at the desk and a bounded read on aifoundry3; E211's own folders, its two design lanes and the model session's folders left out by name: run E211's desk tests only from folders named `<role>-e211[<suffix>]`); run it when the rest is open or about to open, since step 7 needs its report under 30 minutes old | 0: its last line `NEVER-RUN-E211 rgm211 on a card before E211: <none / keys>; ...` (REPORTED, never a gate: rgm211 found on a card before E211 gets a dated note before the data commit, step 12, and a word to the orchestrator; E207's twins found are expected); 14: a scan failed: run it again, at most 3 tries in all, then `... A --desk-only` (aifoundry3 NOT SEARCHED, a stated gap); 10: no window for today (step 1 again, then 6n) or no `E211_ROUND_OUT` (set it to the round's OUT, then 6n again); after three 10s in a row, **E** |
| 7 | **STEP 7 ONLY ONCE THE REST HAS OPENED, WITHIN 30 MINUTES OF 6n**: `rb/s09_reads_e211.sh A` (the 6n report's age and the rest rule on the box first, no card command; then the time stamped and k6's config read); then 8 and 9 **without delay** | 10 with "the never-run report": run 6n again, then 7; 10 with "the rest has not run": wait in bounded chunks and run it again (6n again if its report passes 30 minutes), never around it; 0: the config read as found and et-who clean; 16 (not as found): no session that day, set nothing: **E**; 17 (et-who not clean): step 4 with `--wait`, then step 7 again |
| 8 | `rb/s10_dry_e211.sh A start`, then `... wait` | 0 (E211-DRY arm A rc=0 runs=3: the doubles on the box, no device) |
| 9 | (the quiet-desk flag on aifoundry2 absent) `rb/s11_session_e211.sh A` | 0 launched (its "rest:", "hung:" and "same-day:" lines in the runbook log; the T0 in RB_OUT/e211-T0-A.txt); 10 refused (no never-run report from today: 6n and 7 first; the rest; a session or job of ours; **a HUNG marker**: a device process of ours did not end after its timeout's TERM: stop, report to the owner, no session that day; the same-day rule; no dry pass or build today): read why, never around it: **E** if the day cannot go on; 16: past the last start, or the cap would pass the last end: **E** |
| 10 | `rb/s20_wait_e211.sh A`, again while it says 17 | 0: ended, MANIFEST-WRITTEN, the runner exited 0 (read its `STOP:` line if one is printed: a stop line, a holder, a kernel stop, an identity gate failure or two failed gemmL processes end a session rc 0); **16 HUNG**: KILL NOTHING, reset nothing, keep the booking and the hold, collect what is written (step 11), write it up and escalate to the owner; **16 K1-STOPPED**: a launch did not finish (it may leave a hung hart): collect it, never reset, escalate; **16 CRASHED**: read runner.out read-only, report, then collect; **16 GATE-STOPPED**: no run, still collected as a gate stop's record; 14: gone without "session end" or no runner.rc (read the box read-only first) |
| 11 | `bash W/onelab.sh collect <lane>` (exit 3 at its 9-minute bound: call again, at most 6 calls; the session's files wait on the box; after the sixth 3, **E**: nothing collected, the session's files left on the box untouched and reported, a later collection by a dated note); then `rb/s22_collect_e211.sh A` (start it at least 10 minutes before the last end) | 0 COPY-BACK EXACT; 16 COPY-BACK NOT EXACT (a HUNG process may still be writing its files): commit nothing, read why: **E (with uncollect)**. **Every other exit** (10 refused, 11 a login link, 12 no answer, 13 past a bound, 14 a call failed): `uncollect` at once (nothing is committed yet), read why, wait OUTSIDE the span (chunks of at most 9 minutes; after a login link only once `RB_LOCK`'s check is cleared), then `collect` again and step 11 again: at most 3 tries in 60 minutes in all, else **E**, the session's files left on the box untouched and reported |
| 12 | `rb/s23_data_e211.sh A` (the data directory, or a gate stop's record, the scrub, the reducer, **step 6n's report** copied in as `neverrun-e211-card.txt` and `neverrun-e211-card.json` and listed in SHA256SUMS, the desk-path gate, the history check); the README in [DATA-README-FORM-e211.md](DATA-README-FORM-e211.md)'s form; **if rgm211 was found on a card before E211, a dated note** (`README.md.dated-note-1.md`: the keys, where the scan found them, and what that does to the blindness of those points; a later scores lane applies it: the frozen scorer is never changed); the public-text scan; `LAB_QUIET_HOLD_OWNER=<lane> bash W/commit_lab.sh "<subject>" "<body>" <the collected directory>` (new files only; on exit 5 or 6 run it again); then `bash W/onelab.sh uncollect <lane>`, `bash W/hold.sh remove <lane>`, `bash W/book.sh release aifoundry3 <lane>` | "COMMIT_LAB: pushed <sha>"; anything else after the retries: move the collected directory out of the lab clone at once into the lane's own folder (`OUT/<lane>/held/<the directory's name>`, a copy checked against its SHA256SUMS first, then removed from LAB by its literal path), so no untracked file in LAB blocks another card lane's step H; then **E (with uncollect)**, reported (a later lane commits the held directory by a dated note) |
| 13 | after the data commit only, never on a gate stop's record: `rb/s24_score_e211.sh A` | the frozen scorer: RB_OUT/scores-e211-A.json and .txt (R0, S6, T4, T1-T3, E1-E4, W1, W2, H1-H6 (H7 NOT REGISTERED), SR, CT, CE; the reported readings; E211.md's Amendment A1: its line says whether A1 APPLIES and on which ratios W1, W2 and H1-H3 were scored, the other reading REPORTED in the JSON, and on an R0 FAIL every other rule carries R0's label); read its words; a later lane commits them beside the data |
| E | **every path ends here**: `bash W/onelab.sh undesk <lane>` if inside steps 0-2; `bash W/onelab.sh uncollect <lane>` if between step 11's collect and the data commit's push; then `bash W/hold.sh remove <lane>` and `bash W/book.sh release aifoundry3 <lane>` (on a HUNG or K1 day: keep the booking and the hold until the owner or the orchestrator answers; release them then) | |

**Waits inside a span** (THE ONE-LAB RULE): every wait in this table is bounded (at most 9 minutes a call, with each row's total), and no wait
longer than one call happens inside a span: the load rule waits before `desk`; a step 2 or a step 11 that must wait leaves its span first
(`undesk`, `uncollect`) and enters it again before it is run again; past a row's bound the path ends at **E**. Inside the desk span a lane holds
only step 0's reads, H, step 1 and step 2 (k6's bounded drivers); inside the collect span, step 11 (its 600 s copy) and step 12 (commit_lab.sh's
own bounds: its lock wait of 1,200 s, five push tries).

**To stop the session by hand** (the operator's stop, a registered stop): `touch build/e211/T<T0>-A/STOP` on the box (the host ends at its next
launch boundary; the runner reads the file before every start, so nothing further starts; a STOP file already there when the runner starts is a
refusal, no device opened, the file kept), or SIGTERM to the runner (`run_e211.py`), never to a host or the sampler. A STOP during the smoke ends
the smoke as a gate stop whose words name the stop ("smoke gate failed: a stop during the smoke's s0N: the operator's STOP file ..."), not the
cut process's board rise (verify-e207's finding V4, answered in this kit). Never kill a process: the
session ends its own processes and stops its sampler with SIGTERM.

## 3. After a gate stop, a registered stop, a kernel stop, K1, HUNG or a crash

- **A gate stop** (no run: "refused, no device opened: ..." before any card command, or after the card opened: the start config, the card's
  identity gate, the sampler, the identity read, the smoke (an identity gate per process failing in it among them), the stop-path test) is **no
  session: no data**. Step 12 collects it as a gate stop's record under `docs/reports/gate-stops/`, never `docs/reports/data/`; commit it (new
  files only, its README in the gate-stop form); it is never scored. **E211 may be tried again with no amendment**: after a refusal that opened no
  device, **once more the same day**, once the look reads FREE again and inside the window (step 9 counts the tries: a third is refused); after a
  gate that came after the card opened, **not the same day** (step 9's same-day rule); a try on a later day needs that day's go, the rest and
  step 6n again. A gate stop by a kit defect is the kit's to fix: a dated kit note and, if it touches the registration, a dated amendment to
  E211.md before any datum, verified and landed, then a later session.
- **A registered stop** (the board or die lines, a holder, two failed gemmL processes, the card-time rule, the window's end, the operator's STOP
  or SIGTERM) after a run: the runs done stand and are scored as they stand (the registered subset if cut: the smoke, family X and family W, 35
  processes; family C is then NO DATA); the data directory is committed; the missing runs are never re-run without a dated amendment.
- **A kernel stop** (plan-e211.json > stops > kernel_stops: a gemmLn or gemmLnc process with a check of C wrong, a tensor error, the walk check
  failed, a launch timeout or a launch not ok; or an identity gate failure before any process): **nothing more that day**. The runs done stand
  and are collected and committed as above; the stop's words go in the README; a walk check that failed on the card is the registration's R0
  FAIL (it labels every other verdict). A failed identity gate or walk check is a kit or build defect until shown otherwise: a dated note, and the
  readiness lane's look at the box's build before any later session.
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

- No step 2 but `rb/s03_desk_e211.sh`, never inside the lab-git lock; no box step without step 2's 0 that day; no step out of the order above;
  **never step 7 before the rest has opened, nor without a 6n report under 30 minutes old**; never steps 5, 6 or 8 while a session of ours runs
  (they refuse).
- No booking before E207's data commit, with no exception for an E207 chain that stopped short (A1 clause 4); never beside E207's or E210's
  session on aifoundry3.
- No change to a forecast, a band, a rule, a threshold, the order, the card time, the cap or a stop except by a dated amendment before the data
  (E211.md, Amendments); no run re-run after a stop without one; the scorer only as registered and only after the data commit.
- No device command but the kit's READs (dmcmd_audit_v2 GO): no set, no reset, no governor, TDP, threshold, clock, voltage, fan or firmware
  change; no statistics reset; no PMIC write; no power cycle and nothing that risks one; **never kill a device process** (no SIGKILL, no
  `timeout -k`; a process that does not end after its TERM is reported at once and left).
- Never two sessions of ours on aifoundry3 at once; never beside another user's holder or device process (the session's et-who and ps refuse).
- Never a lab user's login in any file (the collection's scrub masks ours; write `<login>`); no number from the owner's private pages or his
  A100 report in any lab file; no sealed forecast's number anywhere.
- Never touch another run's files on the box: E211 writes only `build/e211rgm/`, `build/e211/`, `build/e211-build-*` and the runbook's own
  `build/q141k/` entries, and step 5's synced files at their committed bytes; step 6n writes nothing on the box. The kit lane's own aifoundry3
  folder (`~/claude/work/q204-kit-e211`: its build, simulator runs and box-build tree) is not the session's and is never read by it.
- Never write in another lane's folder, booking, hold line or onelab flag; never answer a lane by a message (the orchestrator answers through
  files under `W/out/orch/`).

## 5. Labels

Every figure here is **registered** (E211.md) or a **desk check of code** (KIT.md). Nothing here is measured, blind, held out or post hoc.

SPDX-License-Identifier: Apache-2.0
