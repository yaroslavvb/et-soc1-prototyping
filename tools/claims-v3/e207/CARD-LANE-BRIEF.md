# E207's card-lane brief: what the lane that runs E207, the blind matmul day, on aifoundry3 card 0 does, step by step, and what it never does (Q199; kitted, not run)

*Mon 16 Nov 2026 (week 47), PST, on aifoundry2, desk only (Q199, lane `kit-e207`), beside [KIT.md](KIT.md). E206's card-lane brief
(`tools/claims-v3/e206/CARD-LANE-BRIEF.md`, landed in `906699ea`, the brief E206 arm A ran FULL by on this card) for E207's one arm. The
registration is [E207.md](E207.md) (found by content: the commit that added it; its subtree `d2089226...` with amendment A1 (fix-e207; before it,
`ac8854b4...`); `SHA256SUMS-e207-registration` `b97becf2...`, 24 entries). No card was claimed or opened, no device command was sent, nothing was posted. No E207 datum exists. This brief
changes no forecast, band, rule, threshold, the order, the card time, the cap, a stop or the scorer. **New against E206's brief:** step 6n (the
never-run search repeated right before the first card command, E207.md section 4), step 7's refusal without a fresh 6n report, the binding last
start (the 70-minute cap leaves the registered G + 1:30 as the launch bound), one arm.*

*Fixed by Q199's lane `fix-e207` (Tue 17 Nov 2026, before any E207 datum; KIT.md section 9, E207.md amendment A1): step 6n counts only card
runs (another experiment's desk doubles are DESK-ONLY, dismissed; the model session's `~/claude/work/ee-*/` folders are not read) and dates every
record against MM1-v1's freeze (21:14:57 PST Mon 16 Nov 2026: only a record before it is "ran before"); rows 6n, 11, 12 and 13 below say what to
do with each of its words, with a failed collect, with a failed data commit, and with the after-score tool's registered verdicts; section 2 says
how to read a smoke gate that coincides with the operator's STOP file.*

## 1. What the go must carry (E207.md 6)

- **The owner's go**, on the round's reading: his standing words of Sun 15 Nov 2026 ("continue, all machines are up", 10:05:42 PST; "don't
  worry about discord post, just use the machines, nobody is using them", 10:22:36; "Feel free to use more cards in parallel, I don't need to
  reserve them ..., feel free to use more in parallel", 17:21:16), "Try again" (received at or before 21:28:59) and "don't worry about hitting
  the limit, I will use a reset, feel free to run things overnight and in parallel" (at or before 21:51:09), and his matmul focus of Mon 16
  Nov 2026 (received at or before 09:48:24: "... just go as far as possible on the matte mold, on the FME, yeah, on the matmul operation";
  and, through the model session's coordination post #2.6.2 at 11:01:08, "feel free to use all the cards without restriction"), with E207's
  registered items as its defaults, once E207 is registered, kitted, verified, landed and readiness-checked. Record them as dated departures in
  the data README: the registered items as their defaults; G = the booking on its day; the post waived; the package counter not read; the desk
  aifoundry2 with Python 3.12.3; the yvb3 session.
- **The card**: aifoundry3 card 0 at its pinned 600 MHz (a boot-time TDP of 0 latches the governor), reads only, nothing set; **after the
  round's queue on aifoundry3** (the queue helper `python3 W/out/orch/queue_state.py aifoundry3 <the experiments before E207: e202 e206a>`
  reads QUEUE OVER; QUEUE CANCELLED (exit 4) is SKIPPED, no booking); 40.6 card-minutes planned, no run after 60, cap 70.
- **The rest**: the first card command (step 7's config read included) at least 40 minutes after the end of our previous session on aifoundry3,
  whatever its form (the model session's folders `~/claude/work/ee-*/` count too). Read it by the clock from the last card lane's records
  BEFORE the booking (E206 arm A's session there ended 18:22:16 PST Mon 16 Nov 2026: E207's rest opened 19:02:16 PST); steps 7 and 9 read it on
  the box again.
- **The window**: G = this lane's booking of aifoundry3 that day; last start G + 1:30, last end G + 3:30, both rounded up to the minute, inside
  G's Pacific day; G at 20:29:00 PST or earlier. **Step 9 launches by the last start** (k6's `rb_need_start`; the 70-minute cap and 5 minutes
  before the last end, E207_BUDGET_S 4,500 s, would allow G + 2:15: the last start binds) and the runner keeps every run inside the last end.
- **The post**: none, by the standing waiver (record his words of 10:22:36). **The host's package counter**: not read.
- **The registration and the kit landed and in HEAD** (registration first, then the kit), no E207 datum in any ref (step 2 refuses).
- **A sealed forecast** (E207.md 0): if the round's record of sealed forecasts (`W/out/orch/sealed-e207.txt`, if the orchestrator keeps one)
  lists a sealed sha256 for E207 that `tools/claims-v3/sealed-e207/e207-freeze-lines.md` at HEAD does not register, do not book: tell the
  orchestrator (the note lands first, under the desk-commit rule). A sha256 posted after the data commit is REPORTED as post-data.
- **THE QUIET DESK FLAG on aifoundry2**: while the round's quiet-desk flag for aifoundry2 is up (a session on aifoundry2's own card), run neither step 9
  (its file name holds `session_e207.sh`, which a text-matching session count on aifoundry2 would read) nor any desk test of this kit; wait in
  bounded chunks.

## 2. The steps, in order (paths under `tools/claims-v3/e207/`)

Run from the lab clone (`cd $LAB`), ONE RB_OUT for E207's day (a new directory outside the repo), the one `RB_LOCK` (the round's file of login
checks), for step 2 `RB_GITLOCK` (the lab-git lock), and for step 6n `E207_ROUND_OUT` (the round's OUT). Each step one plain call from a script
file. k6's drivers bound every remote call: a 15 s probe, then 60 s for a read, 600 s for a copy or one bounded wait (520 s), a detached launch
that returns at once, 5,400 s for a desk call. **A printed login link stops the step (11) and appends `<HH:MM:SS> aifoundry3 needs a check` to
`RB_LOCK`:** nothing is retried until it is cleared, and a session detached on the box keeps running. k6's exit codes: 0 done; 10 refused; 11 a
login link; 12 no answer; 13 past a bound; 14 a call failed; 15 a holder for 30 minutes; 16 a gate says stop; 17 call again. **E** is the end of
every path (below): it carries undesk and uncollect where they are due.

| # | the step | what to do with its exit |
|---|---|---|
| B | the queue (`python3 W/out/orch/queue_state.py aifoundry3 <the experiments before E207>`: QUEUE OVER; QUEUE CANCELLED is SKIPPED, no booking), then the rest by the clock (section 1), then THE DAY (G at 20:29:00 or earlier; later: wait in bounded chunks until 00:00:30 the next day); then `bash W/book.sh take aifoundry3 <lane>` | 0 BOOKED: G = this moment. 1: another lane holds it: make no ssh call to aifoundry3 at all; wait (bounded) or stop (nothing else to undo) |
| 0 | `uptime` FIRST, OUTSIDE the span (THE LOAD RULE: above 8, wait in bounded chunks of at most 9 minutes until below 6, at most 60 minutes in all; past that, no box step that day: **E**); then `bash W/onelab.sh desk <lane>` (THE ONE-LAB RULE: steps 0, H and 2 never overlap another lane's collect span or a commit of ours; exit 3 at its 9-minute bound: call again, at most 6 calls, else **E**); GitHub main read; E207's anchor lines (the land record, `OUT/q199-anchor-lines-e207.txt`); the sealed-forecast check (section 1) | any line not as stated: no box step that day: **E (with undesk)** |
| H | `bash W/hold.sh add <lane>` (THE QUIET HOLD, one owner a line, until the data commit); `git -C $LAB status --porcelain --untracked-files=all` reads 0 lines | not 0: **E (with undesk)** |
| 1 | `rb/s02_window_e207.sh A <YYYY-MM-DD> <last start HH:MM> <last end HH:MM>` (today only; G + 1:30 and G + 3:30, rounded up) | "fits now: an E207 session ..."; "fits now: nothing": no box step: **E (with undesk)** |
| 2 | `uptime` (above 8: `undesk`, wait outside the span as in step 0, `desk` again, then this row again); then `RB_GITLOCK=<the lab-git lock> rb/s03_desk_e207.sh A`, **never inside the lab-git lock**; then `bash W/onelab.sh undesk <lane>` | 0: undesk, go on. Anything else: no box step that day: **E (with undesk)**. Two exceptions, each bounded: a pull whose output shows the upstream did not answer: `undesk` at once, wait outside the span (chunks of at most 9 minutes; at most 3 tries in 30 minutes in all), `desk` again and run step 2 again, else **E**; a 16 naming HEAD-moved (a co-owner committed meanwhile): run step 2 again at once, at most 3 times, else **E (with undesk)** |
| 4 | the look, `../q141k-runbook/k6/s05_look_k6.sh aifoundry3` (it writes the box-login file step 12's scrub reads) | FREE; a holder: bounded polls (`--wait`), at most 30 minutes, else no session that day: **E** |
| 3 | the day's post: **none**, by the owner's standing waiver of Sun 15 Nov 2026 10:22:36 PST; record his words | |
| 5 | `rb/s07_sync_e207.sh A` | 0 HARNESS OK on the box; 10: a session or runbook job of ours on the box; 16: uncommitted synced paths or a file off its sha256: **E** |
| 6 | `rb/s08_build_e207.sh A start`, then `... wait` while it says 17 | 0: RB_OUT/e207-built-A.txt (KERNEL OK); 16: start once more (two starts a Pacific day at most; a third: NO-THIRD-BUILD, no session that day: **E**); a 14 on wait: no reading, wait again |
| 6n | **THE NEVER-RUN SEARCH, REPEATED RIGHT BEFORE THE FIRST CARD COMMAND** (E207.md 4 and A1): `E207_ROUND_OUT=<the round's OUT> rb/s06n_neverrun_e207.sh A` (a minute or two at the desk and a bounded read on aifoundry3). It counts a record only where it is a card run: the lab's data directories, the card and data lanes' folders in OUT, `~/claude/work` but the model session's `ee-*` folders (never read), aifoundry3's run folders; E207's own folders are subtracted (on the box build/e207; in OUT every folder named `<role>-e207[<suffix>]`; `tools/claims-v3/e207`); a record in any other folder (another experiment's desk test, a kit's log) is DESK-ONLY, dismissed and listed. Run it when the rest is open or about to open, since step 7 needs its report under 30 minutes old | 0: its last line `NEVER-RUN <n> of 53 points, <m> of 47 cases[; RAN BEFORE: <ids>][; CASE RAN BEFORE: <cases>][; TO DATE: <ids or cases>][; AFTER THE FREEZE (REPORTED, kept): <ids>][; DESK-ONLY (dismissed): <ids>]`, REPORTED, never a gate: go on. **RAN BEFORE** (a record dated before 21:14:57 PST Mon 16 Nov 2026) and **TO DATE** (found in a card run that no path, commit or file time dates) are labelled in step 12's dated note; **AFTER THE FREEZE** stays in every rule (record it in the README); **DESK-ONLY** is dismissed (record it in the README). 14: a scan failed: run it again, at most 3 tries in all, then `... A --desk-only` (aifoundry3 NOT SEARCHED, a stated gap). **10**: either no window today in this RB_OUT (steps 0-2 were not run in it today: the day starts again from step 0, in this RB_OUT) or `E207_ROUND_OUT` unset or not a folder (set it to the round's OUT, `W/out`, and run 6n again) |
| 7 | **STEP 7 ONLY ONCE THE REST HAS OPENED, WITHIN 30 MINUTES OF 6n**: `rb/s09_reads_e207.sh A` (the 6n report's age and the rest rule on the box first, no card command; then the time stamped and k6's config read); then 8 and 9 **without delay** | 10 with "the never-run report": run 6n again, then 7; 10 with "the rest has not run": wait in bounded chunks and run it again (6n again if its report passes 30 minutes), never around it; 0: the config read as found and et-who clean; 16 (not as found): no session that day, set nothing: **E**; 17 (et-who not clean): step 4 with `--wait`, then step 7 again |
| 8 | `rb/s10_dry_e207.sh A start`, then `... wait` | 0 (E207-DRY arm A rc=0 runs=3: the doubles on the box, no device) |
| 9 | (the quiet-desk flag on aifoundry2 absent) `rb/s11_session_e207.sh A` | 0 launched (its "rest:", "hung:" and "same-day:" lines in the runbook log; the T0 in RB_OUT/e207-T0-A.txt); 10 refused (no never-run report from today: 6n and 7 first; the rest; a session or job of ours; **a HUNG marker**: a device process of ours did not end after its timeout's TERM: stop, report to the owner, no session that day; the same-day rule; no dry pass or build today): read why, never around it: **E** if the day cannot go on; 16: past the last start, or the cap would pass the last end: **E** |
| 10 | `rb/s20_wait_e207.sh A`, again while it says 17 | 0: ended, MANIFEST-WRITTEN, the runner exited 0 (read its `STOP:` line if one is printed: a stop line, a holder or two failed processes end a session rc 0); **16 HUNG**: KILL NOTHING, reset nothing, keep the booking and the hold, collect what is written (step 11), write it up and escalate to the owner; **16 K1-STOPPED**: a launch did not finish (it may leave a hung hart): collect it, never reset, escalate; **16 CRASHED**: read runner.out read-only, report, then collect; **16 GATE-STOPPED**: no run, still collected as a gate stop's record; 14: gone without "session end" or no runner.rc (read the box read-only first) |
| 11 | `bash W/onelab.sh collect <lane>` (exit 3 at its 9-minute bound: call again, at most 6 calls; the session's files wait on the box; **after the sixth exit 3**: collect nothing, go to **E** (no uncollect is due: the span was never entered), leave the session's files on the box untouched and report them for a later collection by a dated note's decision); then `rb/s22_collect_e207.sh A` (start it at least 10 minutes before the last end) | 0 COPY-BACK EXACT; 16 COPY-BACK NOT EXACT (a HUNG process may still be writing its files): commit nothing, read why: **E (with uncollect)**. **Every other exit** (10 refused, 11 a login link, 12 no answer, 13 past a bound, 14 a call failed): `uncollect` at once (nothing is committed yet), read why, wait OUTSIDE the span (chunks of at most 9 minutes; after a login link only once `RB_LOCK`'s check is cleared), then `collect` again and step 11 again: at most 3 tries in 60 minutes in all, else **E**, the session's files left on the box untouched and reported |
| 12 | `rb/s23_data_e207.sh A` (the data directory, or a gate stop's record, the scrub, the reducer, **step 6n's report** copied in as `neverrun-e207-card.txt` and `neverrun-e207-card.json` and listed in SHA256SUMS, the desk-path gate, the history check); the README in [DATA-README-FORM-e207.md](DATA-README-FORM-e207.md)'s form; **if 6n's line names any RAN BEFORE, CASE RAN BEFORE or TO DATE, a dated note** (`README.md.dated-note-1.md`: each point and case, every path 6n dated and why, from 6n's `ranbefore-e207-card.json`; for each TO DATE one, its session's own start read from its data README, runbook log or session folder: after 21:14:57 PST Mon 16 Nov 2026 it is AFTER THE FREEZE and stays, else, or unreadable, it is labelled; by E207.md A1 items 2-3 a labelled point leaves every rule and its case the time rules, a labelled case the time rules only) **and, only if a TO DATE one is dated after the freeze, the final labels** `ranbefore-e207-labels.json` (`{"points": [...], "cases": [...], "why": {...}}`; without it the after-score tool takes 6n's proposal); the frozen scorer is never changed; **the README states 6n's line and the count of runs whose reducer detail carries `checks_missing` above 0** (E207.md A1 item 7; 0 expected); the public-text scan; `LAB_QUIET_HOLD_OWNER=<lane> bash W/commit_lab.sh "<subject>" "<body>" <the collected directory>` (new files only; on exit 5 or 6 run it again); then `bash W/onelab.sh uncollect <lane>`, `bash W/hold.sh remove <lane>`, `bash W/book.sh release aifoundry3 <lane>` | "COMMIT_LAB: pushed <sha>"; anything else after the retries: **move the collected directory out of the lab clone** into this lane's own folder (`mv $LAB/<the collected directory> OUT/<lane>/uncommitted/`, which leaves `git status` of LAB clean, so no other card lane's step H is blocked), then **E (with uncollect)**, reported with its new path; the session's files stay on the box as well |
| 13 | after the data commit only, never on a gate stop's record: `rb/s24_score_e207.sh A` | the frozen scorer: RB_OUT/scores-e207-A.json and .txt (R0, T1-T3, E1-E4, S6, H1-H4; the reported readings), then the after-score tool (E207.md A1): RB_OUT/postscore-e207-A.json and .txt, **THE REGISTERED VERDICTS** (the scorer's cells with any labelled point or case left out; with no label, the scorer's own), the family-level check beside H1-H4 and the checks read (REPORTED); read both; a later lane commits them beside the data. "THE AFTER-SCORE TOOL FAILED": the scorer's outputs stand; say so; the scores lane runs it |
| E | **every path ends here**: `bash W/onelab.sh undesk <lane>` if inside steps 0-2; `bash W/onelab.sh uncollect <lane>` if between step 11's collect and the data commit's push; then `bash W/hold.sh remove <lane>` and `bash W/book.sh release aifoundry3 <lane>` (on a HUNG or K1 day: keep the booking and the hold until the owner or the orchestrator answers; release them then) | |

**Waits inside a span** (THE ONE-LAB RULE): every wait in this table is bounded (at most 9 minutes a call, with each row's total), and no wait
longer than one call happens inside a span: the load rule waits before `desk`; a step 2 or a step 11 that must wait leaves its span first
(`undesk`, `uncollect`) and enters it again before it is run again; past a row's bound the path ends at **E**. Inside the desk span a lane holds
only step 0's reads, H, step 1 and step 2 (k6's bounded drivers); inside the collect span, step 11 (its 600 s copy) and step 12 (commit_lab.sh's
own bounds: its lock wait of 1,200 s, five push tries).

**To stop the session by hand** (the operator's stop, a registered stop): `touch build/e207/T<T0>-A/STOP` on the box (the host ends at its next
launch boundary; the runner reads the file before every start, so nothing further starts; a STOP file already there when the runner starts is a
refusal, no device opened, the file kept), or SIGTERM to the runner (`run_e207.py`), never to a host or the sampler. Never kill a process: the
session ends its own processes and stops its sampler with SIGTERM.

**A smoke gate and the STOP file** (fix-e207, verify-e207's finding 10): a STOP touched during the smoke ends the smoke's running host at its
next launch boundary, and the runner then reads that short host as a failed smoke ("smoke gate failed: b0x: ... the board's rise None W ..."),
so the session log names the smoke, not the STOP file, and step 10 reads GATE-STOPPED (16). Before writing it up, read
`build/e207/T<T0>-A/STOP` on the box (read-only: present or not, and its time): if it is there and its time precedes the smoke's failure line,
record the stop as the operator's (a registered stop) in the gate stop's README; it stays a gate stop's record either way (no point ran).

## 3. After a gate stop, a registered stop, K1, HUNG or a crash

- **A gate stop** (no run: "refused, no device opened: ..." before any card command, or after the card opened: the start config, the identity
  gate, the sampler, the identity read, the smoke, the stop-path test) is **no session: no data**. Step 12 collects it as a gate stop's record
  under `docs/reports/gate-stops/`, never `docs/reports/data/`; commit it (new files only, its README in the gate-stop form); it is never
  scored. **E207 may be tried again with no amendment**: after a refusal that opened no device, **once more the same day**, once the look reads
  FREE again and inside the window (step 9 counts the tries: a third is refused); after a gate that came after the card opened, **not the same
  day** (step 9's same-day rule); a try on a later day needs that day's go, the rest and step 6n again. A gate stop by a kit defect is the kit's
  to fix: a dated kit note and, if it touches the registration, a dated amendment to E207.md before any datum, verified and landed, then a later
  session.
- **A registered stop** (the board or die lines, a holder, two failed processes, the card-time rule, the window's end, the operator's STOP or
  SIGTERM) after a run: the runs done stand and are scored as they stand (the registered subset if cut: the smoke, tie 1, pass 1 and tie 2,
  runs 1-55); the data directory is committed; the missing runs are never re-run without a dated amendment.
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

- No step 2 but `rb/s03_desk_e207.sh`, never inside the lab-git lock; no box step without step 2's 0 that day; no step out of the order above;
  **never step 7 before the rest has opened, nor without a 6n report under 30 minutes old**; never steps 5, 6 or 8 while a session of ours runs
  (they refuse).
- No change to a forecast, a band, a rule, a threshold, the order, the card time, the cap or a stop except by a dated amendment before the data
  (E207.md, Amendments); no run re-run after a stop without one; the scorer only as registered and only after the data commit.
- No device command but the kit's READs (dmcmd_audit_v2 GO): no set, no reset, no governor, TDP, threshold, clock, voltage, fan or firmware
  change; no statistics reset; no PMIC write; no power cycle and nothing that risks one; **never kill a device process** (no SIGKILL, no
  `timeout -k`; a process that does not end after its TERM is reported at once and left).
- Never two sessions of ours on aifoundry3 at once; never beside another user's holder or device process (the session's et-who and ps refuse).
- Never a lab user's login in any file (the collection's scrub masks ours; write `<login>`); no number from the owner's private pages or his
  A100 report in any lab file; no sealed forecast's number anywhere.
- Never touch another run's files on the box: E207 writes only `build/e207rgm/`, `build/e207/`, `build/e207-build-*` and the runbook's own
  `build/q141k/` entries, and step 5's synced files at their committed bytes; step 6n writes nothing on the box.
- Never write in another lane's folder, booking, hold line or onelab flag; never answer a lane by a message (the orchestrator answers through
  files under `W/out/orch/`).

## 5. Labels

Every figure here is **registered** (E207.md) or a **desk check of code** (KIT.md). Nothing here is measured, blind, held out or post hoc.

SPDX-License-Identifier: Apache-2.0
