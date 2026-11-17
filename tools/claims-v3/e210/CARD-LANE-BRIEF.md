# E210's card-lane brief: what the lane that runs E210, the switch test, on aifoundry3 card 0 does, step by step, and what it never does (Q202; kitted, not run)

*Tue 17 Nov 2026 (week 47), PST, on aifoundry2, desk only (Q202, lane `kit-e210`), beside [KIT.md](KIT.md). E206's card-lane brief
(`tools/claims-v3/e206/CARD-LANE-BRIEF.md`, landed in `906699ea`, the brief E206 arm A ran FULL by on this card) as kit-e207 ported it for E207
on the same card (its local commit `4bd6e38c`, under verification when this was written), for E210's one arm. The registration is
[E210.md](E210.md) (found by content: the commit that added it; its subtree `adef3701...`; `SHA256SUMS-e210-registration` `4219474f...`, 523
entries). No card was claimed or opened, no device command was sent, nothing was posted. No E210 datum exists. This brief changes no forecast,
band, rule, threshold, the order, the card time, the cap, a stop or the scorer. **New against E207's brief:** E210's opening (60 s at rest, the
smoke of random@S1, zeros@S1 and random@S2, THE PROBE of maxalte@S2, then the stop-path test); 171 runs; no run after 85 card-minutes, the
session ends at 95; step 12n (the never-run search again, after the copy-back and before the data commit: E210.md 4); the brief gaps
verify-e207 found in E207's brief, answered here (rows 6n, 11 and 12).*

## 1. What the go must carry (E210.md 6)

- **The owner's go**, on the round's reading: his standing words of Sun 15 Nov 2026 ("continue, all machines are up", 10:05:42 PST; "don't
  worry about discord post, just use the machines, nobody is using them", 10:22:36; "Feel free to use more cards in parallel, I don't need to
  reserve them", 17:21:16), "Try again" (received at or before 21:28:59) and "don't worry about hitting the limit, I will use a reset, feel free
  to run things overnight and in parallel" (at or before 21:51:09), his matmul focus of Mon 16 Nov 2026 (received at or before 09:48:24: "... just
  go as far as possible on the matte mold, on the FME, yeah, on the matmul operation") and his words relayed by the model session's coordination
  post #10.13.1 (23:15:25 PST Mon 16 Nov: "There's no deadline; use the cards all night"), with E210's registered items as its defaults, once
  E210 is registered, kitted, verified, landed and readiness-checked. Record them as dated departures in the data README: the registered items
  as their defaults; G = the booking on its day; the post waived; the package counter not read; the desk aifoundry2 with Python 3.12.3; the yvb3
  session.
- **The card**: aifoundry3 card 0 at its pinned 600 MHz (a boot-time TDP of 0 latches the governor), reads only, nothing set; **after E207 on
  this card** (the queue helper `python3 W/out/orch/queue_state.py aifoundry3 e207` reads QUEUE OVER: E207's card day done or its chain stopped;
  QUEUE CANCELLED (exit 4) is SKIPPED, no booking); about 73 card-minutes planned (171 runs at 26 s at S1 and 22.5 s at S2, and about 4 minutes
  of opening), **no run starts after 85 card-minutes; the session ends at 95** after the run in progress (the round's cap is 100).
- **The rest**: the first card command (step 7's config read included) at least 40 minutes after the end of our previous session on aifoundry3,
  whatever its form (E207's, on the card day; the model session's folders `~/claude/work/ee-*/` count too, by their files' times only). Read it
  by the clock from the last card lane's records BEFORE the booking; steps 7 and 9 read it on the box again.
- **The window**: G = this lane's booking of aifoundry3 that day; last start G + 1:30, last end G + 3:30, both rounded up to the minute, inside
  G's Pacific day; G at 20:29:00 PST or earlier. **Step 9 launches by the last start** (k6's `rb_need_start`; the 95-minute cap and 5 minutes
  before the last end, E210_BUDGET_S 6,000 s, would allow G + 1:50: the last start binds) and the runner keeps every run inside the last end.
- **The post**: none, by the standing waiver (record his words of 10:22:36). **The host's package counter**: not read.
- **The registration and the kit landed and in HEAD** (registration first, then the kit), no E210 datum in any ref (step 2 refuses).
- **A sealed forecast** (E210.md 0): a sealed sha256 the model session posts for E210's cases **before E210's first card command** is a freeze
  line of E210, registered in a dated note outside the pinned folder (`tools/claims-v3/sealed-e210/e210-freeze-lines.md`), committed before that
  first card command; its sha256 only is quoted, no lab rule scores it. If the round's record (`W/out/orch/sealed-e210.txt`, which the
  orchestrator keeps) lists, on a line that is not a comment, a sealed sha256 for E210 that `tools/claims-v3/sealed-e210/e210-freeze-lines.md` at
  HEAD does not register, **do not book**: tell the orchestrator in the result (the note lands first, under the desk-commit rule). A record line
  this lane's checks read must point only at files those checks read (the round's E206 lesson of Mon 16 Nov 2026, 23:35 PST). A sha256
  posted after the first card command is recorded as not a blind freeze.
- **THE QUIET DESK FLAG on aifoundry2**: while the round's quiet-desk flag for aifoundry2 is up (a session on aifoundry2's own card: card-e209
  or the model session), run neither step 9 (its file name holds `session_e210.sh`, which a text-matching session count on aifoundry2 would
  read) nor any desk test of this kit; wait in bounded chunks.

## 2. The steps, in order (paths under `tools/claims-v3/e210/`)

Run from the lab clone (`cd $LAB`), ONE RB_OUT for E210's day (a new directory outside the repo), the one `RB_LOCK` (the round's file of login
checks), for step 2 `RB_GITLOCK` (the lab-git lock), and for steps 6n and 12n `E210_ROUND_OUT` (the round's OUT). Each step one plain call from a
script file. k6's drivers bound every remote call: a 15 s probe, then 60 s for a read, 600 s for a copy or one bounded wait (520 s), a detached
launch that returns at once, 5,400 s for a desk call. **A printed login link stops the step (11) and appends `<HH:MM:SS> aifoundry3 needs a
check` to `RB_LOCK`:** nothing is retried until it is cleared, and a session detached on the box keeps running. k6's exit codes: 0 done; 10
refused; 11 a login link; 12 no answer; 13 past a bound; 14 a call failed; 15 a holder for 30 minutes; 16 a gate says stop; 17 call again. **E**
is the end of every path (below): it carries undesk and uncollect where they are due.

| # | the step | what to do with its exit |
|---|---|---|
| B | the queue (`python3 W/out/orch/queue_state.py aifoundry3 e207`: QUEUE OVER; QUEUE CANCELLED is SKIPPED, no booking), then the rest by the clock (section 1), then THE DAY (G at 20:29:00 or earlier; later: wait in bounded chunks until 00:00:30 the next day); then `bash W/book.sh take aifoundry3 <lane>` | 0 BOOKED: G = this moment. 1: another lane holds it: make no ssh call to aifoundry3 at all; wait (bounded) or stop (nothing else to undo) |
| 0 | `uptime` FIRST, OUTSIDE the span (THE LOAD RULE: above 8, wait in bounded chunks of at most 9 minutes until below 6, at most 60 minutes in all; past that, no box step that day: **E**); then `bash W/onelab.sh desk <lane>` (THE ONE-LAB RULE: steps 0, H and 2 never overlap another lane's collect span or a commit of ours; exit 3 at its 9-minute bound: call again, at most 6 calls, else **E**); GitHub main read; E210's anchor lines (the land record, `OUT/q202-anchor-lines-e210.txt`); the sealed-forecast check (section 1) | any line not as stated: no box step that day: **E (with undesk)** |
| H | `bash W/hold.sh add <lane>` (THE QUIET HOLD, one owner a line, until the data commit); `git -C $LAB status --porcelain --untracked-files=all` reads 0 lines | not 0: **E (with undesk)** |
| 1 | `rb/s02_window_e210.sh A <YYYY-MM-DD> <last start HH:MM> <last end HH:MM>` (today only; G + 1:30 and G + 3:30, rounded up) | "fits now: an E210 session ..."; "fits now: nothing": no box step: **E (with undesk)** |
| 2 | `uptime` (above 8: `undesk`, wait outside the span as in step 0, `desk` again, then this row again); then `RB_GITLOCK=<the lab-git lock> rb/s03_desk_e210.sh A`, **never inside the lab-git lock**; then `bash W/onelab.sh undesk <lane>` | 0: undesk, go on. Anything else: no box step that day: **E (with undesk)**. Two exceptions, each bounded: a pull whose output shows the upstream did not answer: `undesk` at once, wait outside the span (chunks of at most 9 minutes; at most 3 tries in 30 minutes in all), `desk` again and run step 2 again, else **E**; a 16 naming HEAD-moved (a co-owner committed meanwhile): run step 2 again at once, at most 3 times, else **E (with undesk)** |
| 4 | the look, `../q141k-runbook/k6/s05_look_k6.sh aifoundry3` (it writes the box-login file step 12's scrub reads) | FREE; a holder: bounded polls (`--wait`), at most 30 minutes, else no session that day: **E** |
| 3 | the day's post: **none**, by the owner's standing waiver of Sun 15 Nov 2026 10:22:36 PST; record his words | |
| 5 | `rb/s07_sync_e210.sh A` (518 files: E210's box files, the registration's frozen points and forecasts and its list, the 493 tiles, rgm136's sources) | 0 HARNESS OK on the box; 10: a session or runbook job of ours on the box; 16: uncommitted synced paths or a file off its sha256: **E** |
| 6 | `rb/s08_build_e210.sh A start`, then `... wait` while it says 17 | 0: RB_OUT/e210-built-A.txt (KERNEL OK); 16: start once more (two starts a Pacific day at most; a third: NO-THIRD-BUILD, no session that day: **E**); a 14 on wait: no reading, wait again |
| 6n | **THE NEVER-RUN SEARCH, REPEATED RIGHT BEFORE THE FIRST CARD COMMAND** (E210.md 4; the kit's reading, KIT.md 4.17): `E210_ROUND_OUT=<the round's OUT> rb/s06n_neverrun_e210.sh A` (about a minute at the desk and a bounded read on aifoundry3; left out by the scanner's own `--exclude`: E210's own folders (in the lab `tools/claims-v3/e210`; in OUT every folder named `<role>-e210[<suffix>]`, so run E210's desk tests only from such folders; on the box `build/e210`, `build/e210rgm` and the synced `tools/claims-v3/e210`) and the model session's folders `~/claude/work/ee-*/`); run it when the rest is open or about to open, since step 7 needs its report under 30 minutes old | 0: its last line `NEVER-RUN <n> of 9 patterns (A1)[; RAN BEFORE: <patterns> (see named-by.json)]; by named tile files in launch records: <k> of 9 named[ (<patterns>)]; anywhere (the registered condition ii): <k2> of 9 named[ (<patterns>)]; generators not the host's in launch records: none \| <gens> in <f> file(s); elsewhere (never a run): none \| <gens> in <f> file(s); the registered rule as first written: <m> of 9 (6n; aifoundry3 ...)` (REPORTED, never a gate: E210.md 4 keeps every pattern in E210; the README says which). **The verdict is A1's (E210.md amendment A1 item 1): both conditions count a GEMM string only inside a host launch record**; the registered rule as first written reads all nine as run when any GEMM string anywhere names a generator rgm136 does not draw, and a pattern as run when any string anywhere names a law-passing tile file. **Read the listed files** (`neverrun-e210-card.txt`, `named-by.json` › `A1_item_1`): at fix-e210's desk read (Tue 17 Nov 2026 07:12-07:15 PST, aifoundry3 not read) A1 read 9 of 9; the generator `noise` sat in 27 files, every one E211's host-refusal checks (never a run), and E212's planned arms named `fld_sign.bin` (the signs law) and `den4.bin` (highmant8's structure) in plans only. **If E212 has run those tiles since, their launch records count**: say which patterns, by whose run and when, in the README. Copy the last line and say all three verdicts in the README; 14: a scan failed: run it again, at most 3 tries in all, then `... A --desk-only` (aifoundry3 NOT SEARCHED, a stated gap); 10: no window (step 1 first) or `E210_ROUND_OUT` unset or inside the repo: set it to the round's OUT and run 6n again |
| 7 | **STEP 7 ONLY ONCE THE REST HAS OPENED, WITHIN 30 MINUTES OF 6n**: `rb/s09_reads_e210.sh A` (the 6n report's age and the rest rule on the box first, no card command; then the time stamped and k6's config read); then 8 and 9 **without delay** | 10 with "the never-run report": run 6n again, then 7; 10 with "the rest has not run": wait in bounded chunks and run it again (6n again if its report passes 30 minutes), never around it; 0: the config read as found and et-who clean; 16 (not as found): no session that day, set nothing: **E**; 17 (et-who not clean): step 4 with `--wait`, then step 7 again |
| 8 | `rb/s10_dry_e210.sh A start`, then `... wait` | 0 (E210-DRY arm A rc=0 runs=3: the doubles on the box, no device; the probe IN; every tile file of runs 004 and 007 read from the box tree) |
| 9 | (the quiet-desk flag on aifoundry2 absent) `rb/s11_session_e210.sh A` | 0 launched (its "rest:", "hung:" and "same-day:" lines in the runbook log; the T0 in RB_OUT/e210-T0-A.txt); 10 refused (no never-run report from today: 6n and 7 first; the rest; a session or job of ours; **a HUNG marker**: a device process of ours did not end after its timeout's TERM: stop, report to the owner, no session that day; the same-day rule; no dry pass or build today): read why, never around it: **E** if the day cannot go on; 16: past the last start, or the cap would pass the last end: **E** |
| 10 | `rb/s20_wait_e210.sh A`, again while it says 17 (about 73 card-minutes planned; at most 95) | 0: ended, MANIFEST-WRITTEN, the runner exited 0 (read its `STOP:` line if one is printed: a stop line, a holder or two failed processes end a session rc 0; read the probe's line: `the probe maxalte@S2: IN` or `OUT ... maxalte@S2 leaves the session`, a registered rule, never a stop); **16 HUNG**: KILL NOTHING, reset nothing, keep the booking and the hold, collect what is written (step 11), write it up and escalate to the owner; **16 K1-STOPPED**: a launch did not finish (it may leave a hung hart): collect it, never reset, escalate; **16 CRASHED**: read runner.out read-only, report, then collect; **16 GATE-STOPPED**: no run, still collected as a gate stop's record; 14: gone without "session end" or no runner.rc (read the box read-only first) |
| 11 | `bash W/onelab.sh collect <lane>` (exit 3 at its 9-minute bound: call again, at most 6 calls; after the sixth: nothing has entered the span, so no uncollect: **E**, the session's files left on the box untouched and reported); then `rb/s22_collect_e210.sh A` (start it at least 10 minutes before the last end) | 0 COPY-BACK EXACT; 16 COPY-BACK NOT EXACT (a HUNG process may still be writing its files): commit nothing, read why: **E (with uncollect)**. **Every other exit** (10 refused, 11 a login link, 12 no answer, 13 past a bound, 14 a call failed): `uncollect` at once (nothing is committed yet), read why, wait OUTSIDE the span (chunks of at most 9 minutes; after a login link only once `RB_LOCK`'s check is cleared), then `collect` again and step 11 again: at most 3 tries in 60 minutes in all, else **E**, the session's files left on the box untouched and reported |
| 12n | **THE NEVER-RUN SEARCH AGAIN, BEFORE THE DATA COMMIT** (E210.md 4: "repeats this search before its data commit"): `E210_ROUND_OUT=<the round's OUT> rb/s06n_neverrun_e210.sh A --late` (the desk's three roots, no box call; about a minute; inside the collect span: it reads only) | 0: its line in RB_OUT/e210-neverrun-late.txt (REPORTED); 14: run it again, at most 3 tries, else **E (with uncollect)**; 10: no copy-back today (step 11 first) |
| 12 | `rb/s23_data_e210.sh A` (it refuses without step 12n's report written after the copy-back; the data directory `docs/reports/data/<day>-e210-switch-test-aifoundry3/`, or a gate stop's record, the scrub, the reducer, **both never-run reports** copied in as `neverrun-e210-card.*`, `neverrun-e210-late.*`, `named-by-card.json`, `named-by-late.json` and listed in SHA256SUMS, the desk-path gate, the history check); the README in [DATA-README-FORM-e210.md](DATA-README-FORM-e210.md)'s form (it says which patterns, if any, either report found run before, and that by E210.md 4 they stay in E210: no rule changes, the frozen scorer is never changed); the public-text scan; `LAB_QUIET_HOLD_OWNER=<lane> bash W/commit_lab.sh "<subject>" "<body>" <the collected directory>` (new files only; on exit 5 or 6 run it again); then `bash W/onelab.sh uncollect <lane>`, `bash W/hold.sh remove <lane>`, `bash W/book.sh release aifoundry3 <lane>` | "COMMIT_LAB: pushed <sha>"; anything else after the retries: move the collected directory out of the lab clone by its literal path into RB_OUT (`mv` to `RB_OUT/uncommitted-<the directory's name>`, so the lab clone is clean for every other card lane's step H), then **E (with uncollect)**, reported |
| 13 | after the data commit only, never on a gate stop's record: `rb/s24_score_e210.sh A` | the frozen scorer as registered (`score_e210.py DATA.json --out SCORED.json --txt SCORED.txt`): RB_OUT/scores-e210-A.json and .txt (R0, B5, B10 reported, H1-H4; per case its dW, SE, T and each route's error; as re-frozen by E210.md A1: R0 FAIL on a printed check not exact or approx, a process that printed none REPORTED by name in `R0` › `missing_REPORTED`; a run whose clock or power reading is missing, None or not finite set aside by Q, never a crash; beside each of H1-H4 the REPORTED pattern-level line H1p-H4p); read its words; the README names every process in `missing_REPORTED`, every run in data-e210.json's `runs_without_a_sample_inside` and each BETTER beside its pattern-level line; a later lane commits them beside the data |
| E | **every path ends here**: `bash W/onelab.sh undesk <lane>` if inside steps 0-2; `bash W/onelab.sh uncollect <lane>` if between step 11's collect and the data commit's push; then `bash W/hold.sh remove <lane>` and `bash W/book.sh release aifoundry3 <lane>` (on a HUNG or K1 day: keep the booking and the hold until the owner or the orchestrator answers; release them then) | |

**Waits inside a span** (THE ONE-LAB RULE): every wait in this table is bounded (at most 9 minutes a call, with each row's total), and no wait
longer than one call happens inside a span: the load rule waits before `desk`; a step 2 or a step 11 that must wait leaves its span first
(`undesk`, `uncollect`) and enters it again before it is run again; past a row's bound the path ends at **E**. Inside the desk span a lane holds
only step 0's reads, H, step 1 and step 2 (k6's bounded drivers); inside the collect span, step 11 (its 600 s copy), step 12n (desk reads) and
step 12 (commit_lab.sh's own bounds: its lock wait of 1,200 s, five push tries).

**To stop the session by hand** (the operator's stop, a registered stop): `touch build/e210/T<T0>-A/STOP` on the box (the host ends at its next
launch boundary; the runner reads the file before every start, so nothing further starts; a STOP file already there when the runner starts is a
refusal, no device opened, the file kept; a STOP during the opening is named in the smoke gate's words), or SIGTERM to the runner
(`run_e210.py`), never to a host or the sampler. Never kill a process: the session ends its own processes and stops its sampler with SIGTERM.

## 3. After the probe, a gate stop, a registered stop, K1, HUNG or a crash

- **The probe** (E210.md 6): maxalte@S2's one 2 s process, under the die gate, read from its start to the end of its 4 s tail. IN: maxalte@S2
  runs as registered. OUT (a board sample above 64 W, or the die at 63 C or more, or no reading, or a probe process that ended badly): **maxalte
  leaves the session** - its six runs are not started, its case is NO DATA - a registered rule, logged, **not a stop**: the session goes on.
  Never re-run the probe or maxalte's runs that day; the README reports the probe's readings (never scored).
- **A gate stop** (no run: "refused, no device opened: ..." before any card command, or after the card opened: the start config, the identity
  gate, the sampler, the identity read, the smoke, a stop line during the probe, the stop-path test) is **no session: no data**. Step 12 collects
  it as a gate stop's record under `docs/reports/gate-stops/`, never `docs/reports/data/`; commit it (new files only, its README in the gate-stop
  form); it is never scored. **E210 may be tried again with no amendment**: after a refusal that opened no device, **once more the same day**,
  once the look reads FREE again and inside the window (step 9 counts the tries: a third is refused); after a gate that came after the card
  opened, **not the same day** (step 9's same-day rule); a try on a later day needs that day's go, the rest and step 6n again. A gate stop by a
  kit defect is the kit's to fix: a dated kit note and, if it touches the registration, a dated amendment to E210.md before any datum, verified
  and landed, then a later session.
- **A registered stop** (the board or die lines, a holder, two failed processes, the card-time rule, the window's end, the operator's STOP or
  SIGTERM) after a run: the runs done stand and are scored as they stand (the registered subset if cut: the opening and passes 1-4, every kind
  twice at both shapes, about 55 card-minutes); the data directory is committed; the missing runs are never re-run without a dated amendment.
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

- No step 2 but `rb/s03_desk_e210.sh`, never inside the lab-git lock; no box step without step 2's 0 that day; no step out of the order above;
  **never step 7 before the rest has opened, nor without a 6n report under 30 minutes old**; never steps 5, 6 or 8 while a session of ours runs
  (they refuse); never step 12 without step 12n's report from after the copy-back (it refuses).
- No change to a forecast, a band, a rule, a threshold, the order, the card time, the cap, the probe or a stop except by a dated amendment
  before the data (E210.md, Amendments); no run re-run after a stop without one; the scorer only as registered and only after the data commit.
- No device command but the kit's READs (dmcmd_audit_v2 GO): no set, no reset, no governor, TDP, threshold, clock, voltage, fan or firmware
  change; no statistics reset; no PMIC write; no power cycle and nothing that risks one; **never kill a device process** (no SIGKILL, no
  `timeout -k`; a process that does not end after its TERM is reported at once and left).
- Never two sessions of ours on aifoundry3 at once; never beside another user's holder or device process (the session's et-who and ps refuse).
- Never a lab user's login in any file (the collection's scrub masks ours; write `<login>`); no number from the owner's private pages or his
  A100 report in any lab file; no sealed forecast's number anywhere; never read the model session's uncommitted session folders (steps 6n and
  12n leave `~/claude/work/ee-*/` out).
- Never touch another run's files on the box: E210 writes only `build/e210rgm/`, `build/e210/`, `build/e210-build-*` and the runbook's own
  `build/q141k/` entries, and step 5's synced files at their committed bytes; steps 6n and 12n write nothing on the box.
- Never write in another lane's folder, booking, hold line or onelab flag; never answer a lane by a message (the orchestrator answers through
  files under `W/out/orch/`).

## 5. Labels

Every figure here is **registered** (E210.md) or a **desk check of code** (KIT.md). Nothing here is measured, blind, held out or post hoc.

SPDX-License-Identifier: Apache-2.0
