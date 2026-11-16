# E202's card-lane brief: what the lane that runs E202 on aifoundry3 card 0 does, step by step, and what it never does (Q193; kitted, not run)

*Mon 16 Nov 2026 (week 47), PST, on aifoundry2, desk only (Q193, lane `kit-e202`), beside [KIT.md](KIT.md). The registration is
[E202.md](E202.md) (its subtree `d95a19d9...`, list `SHA256SUMS-e202-registration` `3ff8830f...`, 12 entries), on the program commit
(`workloads/mnistmlp`, its subtree `fb102551...`). No card was claimed or opened, no device command was sent, no box but one read-only
look at aifoundry3's tools was reached, nothing was posted. No E202 datum exists. This brief changes no forecast, band, rule, threshold,
K, the order, the R rule, the card time, the cap, a stop or the scorer.* *Fixed before the land by Q193's lane `fix-e202` (Mon 16 Nov
2026, verify-e202's findings; KIT.md section 12): the ledger v3 note is required at step 2; the booking and the readiness read the rest by
the clock and on E201's and E204's logs; step 9 refuses on a HUNG marker; step 10 reads the runner's exit; a crash is named.*

## 1. What the go must carry (E202.md 10 and 11)

- **The owner's go** for E202 on **aifoundry3 card 0 at its pinned 600 MHz, reads only, nothing set**: on the round's reading, his
  standing words of Sun 15 Nov 2026 (10:05:42 "continue, all machines are up"; 10:22:36 "don't worry about discord post, just use the
  machines, nobody is using them"; 17:21:16 on using more cards in parallel) and his "Try again" of 21:2x, with E202's registered items as
  its defaults, once it is registered, kitted, verified and readiness-checked. **About 17-29 card-minutes, cap 35** from the session's
  first card command (no burst starts after 33); **after E201** on the same card and the **40-minute rest** (E202's first card command,
  step 7's read included, at least 40 minutes after the end of our previous session on aifoundry3, whatever its form; the next session of
  ours there at least 40 minutes after E202's end); **one session**; **the window**: G = this lane's booking of aifoundry3 that day; last
  start G + 1:30, last end G + 3:30, both rounded up to the minute, inside G's Pacific day; G at 20:29:00 PST or earlier; **the post**:
  none, by the standing waiver (record his words of 10:22:36); **the host's package counter**: not read.
- **The program and the registration landed and in HEAD before the session** (the program first: `OUT/fix-mnist/land`, then
  `OUT/reg-e202/land`, then this kit's land), no `docs/reports/data/*e202*` path in any ref (step 2 refuses otherwise).
- **Ledger v3** (E202.md 4.4): ledger v3 landed (`50795847`, Mon 16 Nov 2026 06:26:27 PST) after the registration's freeze, so E202's v3
  note ([`E202-ledger-v3-note.md`](E202-ledger-v3-note.md), with `v3note_e202.py` and its two outputs, in the kit's list) is frozen with
  this kit, before any datum, REPORTED beside v2 (the verdicts stay v2's). **Step 2 requires it** once ledger v3 is in HEAD (its four files
  in HEAD and `v3note_e202.py --check` PASS, else 16): the go confirms step 2's line "ledger v3 in HEAD yes, E202's v3 note in HEAD yes".
- **"After E201"** (E202.md 10; verify-e202's note 11): never beside E201 (one session of ours per box: the booking), after it when both
  run. If E201 does not run first (its chain skipped or stopped), E202 still waits for the box's last session of ours and its 40-minute
  rest, and its README says so in its departures. **Mon 16 Nov 2026 (fix-e202, resumed in Q198):** the owner's matmul focus (his
  words received at or before 09:48:24 PST) paused E201 and E204 and kept E202: E202 runs on aifoundry3 without E201, after the box's
  last session of ours (by the round's records at this writing, E197's sitting 1, session end 06:10:45 PST) and its 40-minute rest,
  and a departure line in its README says that E201 did not run first.
- **The rest, by the clock, before the booking** (verify-e202's finding 6): book aifoundry3 only once 40 minutes have passed since the end
  of our last session there, read from that lane's own records (its result, its data README or its session log's "session end"), not
  only from the rest rule; the rest rule at steps 7 and 9 reads the box again (with fix-e202's activity floor). **The readiness check
  (ready-e202)** runs `rb/rest_rule_e202.sh` on E201's and on E204's committed session logs (as `rb/selftest_rest_e202.sh`'s cases do: the
  log at its path in a stand-in tree, its last line and its file time 10 minutes ago) and reads REFUSED for each, before it reads ready.
  With E201 and E204 paused (above), it does the same with the committed session log of the box's last session of ours (E197 sitting
  1's, in its data commit, at this writing) and with any later one's.
- **The kit's readings the go confirms or refuses** (KIT.md section 4): the cap counted from the session's own first card command, step
  7's read reported apart; the clock line counting every live sample; the stale line; each smoke process its own arm; K1 (a launch that did
  not finish ends the session); the closing config read only while et-who reads the card free; the same-day rule; the gate stop's record
  under `docs/reports/gate-stops/`; and fix-e202's (items 21-25 and the changes to 7, 9, 14 and 18): an unreadable et-who is a holder; a
  crash is named and exits 1; K1 also on a host that died or left no record; the closing read not sent while our sampler runs; the host's
  timeout cap on the R rule (a smaller R only, none at the forecast); etcfg read as the two config reads; the HUNG-marker refusal.

## 2. The steps, in order (paths under `tools/claims-v3/e202/`)

Run from the lab clone (`cd $LAB`), ONE RB_OUT (a new directory outside the repo, E202's own), the one `RB_LOCK` (the round's file of
login checks) and, for step 2, `RB_GITLOCK` (the lab-git lock). Each step one plain call from a script file. k6's drivers bound every
remote call: a 15 s hard-killed probe, then 60 s for a read, 600 s for a copy, one bounded wait (520 s), a detached launch that returns at
once. **A printed login link stops the step (11) and appends `<HH:MM:SS> aifoundry3 needs a check` to `RB_LOCK`:** nothing is retried
until it is cleared, and a session detached on the box keeps running. k6's exit codes: 0 done; 10 refused; 11 a login link; 12 no answer;
13 past a bound; 14 a call failed; 15 a holder for 30 minutes; 16 a gate says stop; 17 call again. **E** is the end of every path (below).

| # | the step | what to do with its exit |
|---|---|---|
| B | first the rest by the clock (section 1: 40 minutes since our last session on aifoundry3 ended, from that lane's records); then `bash W/book.sh take aifoundry3 <lane>` | 0 BOOKED: G = this moment. 1: another lane holds it: make no ssh call to aifoundry3 at all; stop (nothing else to undo) |
| 0 | `bash W/onelab.sh desk <lane>` (THE ONE-LAB RULE: steps 0, H and 2 never overlap another lane's collect span or a commit of ours); `uptime` (THE LOAD RULE: above 8, wait in bounded chunks until below 6); GitHub main read; E202's anchor lines (the land files) | any line not as stated: no box step that day: **E** (with undesk) |
| H | `bash W/hold.sh add <lane>` (THE QUIET HOLD, until the data commit); `git -C $LAB status --porcelain --untracked-files=all` reads 0 lines | not 0: **E** (with undesk) |
| 1 | `rb/s02_window_e202.sh <YYYY-MM-DD> <last start HH:MM> <last end HH:MM>` (today only; G + 1:30 and G + 3:30, rounded up) | "fits now: E202 (its 35 card-minutes)"; "fits now: nothing": no box step: **E** (with undesk) |
| 2 | `uptime`; then `rb/s03_desk_e202.sh` with `RB_GITLOCK`, **never inside the lab-git lock**; then `bash W/onelab.sh undesk <lane>` | 0: undesk, go on (its line reads "ledger v3 in HEAD yes, E202's v3 note in HEAD yes (V3NOTE CHECK PASS)": section 1). Anything else: no box step that day: **E** (with undesk); "ledger-v3-note" among its reasons: the note is not in HEAD or does not re-make itself, tell the orchestrator; one exception: a pull whose output shows the upstream did not answer (step 2 again once it answers) |
| 4 | the look, `../q141k-runbook/k6/s05_look_k6.sh aifoundry3` (it writes the box-login file step 11's scrub reads) | FREE; a holder: bounded polls (`--wait`), at most 30 minutes, else no session that day: **E** |
| 3 | the day's post: **none**, by the owner's standing waiver of Sun 15 Nov 2026 10:22:36 PST; record his words | |
| 5 | `rb/s07_a3_sync_e202.sh` | 10: a session or runbook job of ours on the box; 16: uncommitted synced paths or a file off its sha256: **E** |
| 6 | `rb/s08_a3_build_e202.sh start`, then `wait` while it says 17 (the build, the MNIST fetch by sha256, the weights and expected outputs, the host's checks: a few minutes) | 0: RB_OUT/e202-built.txt (E202-BUILT: the .text `ace7bcb0...`, 18 of 18 files at their pins, HOST-BEHAVIOUR OK 20 of 20; the box's harness 33, GO, self-check); 16: start once more (two starts a Pacific day at most; a third: NO-THIRD-BUILD, no session that day: **E**); a 14 on wait: no reading, wait again |
| 7 | **STEP 7 ONLY ONCE THE REST HAS OPENED** (after E201, our previous session on aifoundry3): `rb/s09_a3_reads_e202.sh` (the rest rule read on the box first, no card command; then the time stamped and k6's step 7 unchanged); then 8 and 9 **without delay** | 10 with "the rest has not run": wait in bounded chunks and run it again, never around it; 0: the config read TDP 0 W / 65 C / 600 MHz and et-who clean; 16 (not as found): no session that day, set nothing: **E**; 17 (et-who not clean): step 4 with `--wait`, then step 7 again |
| 8 | `rb/s10_a3_dry_e202.sh start`, then `wait` | 0 (E202-DRY rc=0 bursts=4: the doubles on the box, no device) |
| 9 | `rb/s11_a3_session_e202.sh` | 0 launched (its "rest:", "hung:" and "same-day:" lines in the runbook log; the T0 in RB_OUT/e202-T0.txt); 10 refused (the rest, a session or job of ours, **a HUNG marker** (fix-e202: a device process of ours that did not end after its timeout's TERM: stop, report to the owner, no session that day), the same-day rule, no dry pass or build today): read why, never around it: **E** if the day cannot go on; 16: past the last start, or the cap would pass the last end: **E** |
| 10 | `rb/s20_wait_e202.sh`, again while it says 17 | 0: ended, MANIFEST-WRITTEN, **the runner exited 0**; 16 GATE-STOPPED (no burst: "GATE-STOP:" or "refused, no device opened:" in its own log; still collected, as a gate stop's record); **16 "the runner exited <rc> after the session's end and stopped at no gate"** (fix-e202: a crash, its "CRASH: <type>: <message>" line named as CRASHED): read runner.out read-only, report it, then collect; **14 runner.rc not written** 10 s after the end: wait once more, then read the box read-only; 14: gone without "session end" (read the box read-only first) |
| 11 | `bash W/onelab.sh collect <lane>`; then `rb/s22_collect_e202.sh` (start it at least 10 minutes before the last end) | 0 COLLECTED into `docs/reports/data/<day>-e202-mnist-int8-aifoundry3/`, or for a gate stop (or a crash with no burst: "a crash's record", fix-e202) into `docs/reports/gate-stops/<day>-e202-mnist-int8-T<T0>-aifoundry3/` (RB_OUT/e202-data-dir.txt names it); 16: COPY-BACK NOT EXACT, the scrub, the desk-path gate or the history check: commit nothing, read why: **E** (with uncollect) |
| 12 | the commit: README.md in [DATA-README-FORM-e202.md](DATA-README-FORM-e202.md)'s form (or its gate-stop form); the public-text scan; `LAB_QUIET_HOLD_OWNER=<lane> bash W/commit_lab.sh "<subject>" "<body>" <the collected directory>` (new files only; on exit 5 or 6 run it again); then `bash W/onelab.sh uncollect <lane>` | "COMMIT_LAB: pushed <sha>"; anything else after the retries: **E** (with uncollect), the collected files kept in the lab clone untracked, reported |
| 13 | after the data commit only, never on a gate stop's record: `rb/s24_score_e202.sh` | the frozen scorer: RB_OUT/scores-e202.json and its printed words (E202-S1, S1T, S2, S2T, S3: PASS, FAIL or NO DATA); then the ledger v3 note's REPORTED readings, RB_OUT/v3-scores-e202.json (fix-e202: S2T-v3, never a verdict); the records lane commits both beside the data |
| E | **every path ends here**: `bash W/onelab.sh undesk <lane>` if inside steps 0-2; `bash W/onelab.sh uncollect <lane>` if between step 11's collect and the push; then `bash W/hold.sh remove <lane>` and `bash W/book.sh release aifoundry3 <lane>` | |

**To stop the session by hand** (the operator's stop, a registered stop): `touch build/e202/T<T0>/STOP` on the box (the runner reads it
before every start and between processes; the process in flight finishes), or SIGTERM to the runner (`run_e202.py`), never to a host or
the sampler. Never kill a process: the session ends its own processes and stops its sampler with SIGTERM.

## 3. After a gate stop, a registered stop, or a crash

- **A gate stop** (no burst: "refused, no device opened: ..." before any card command, or "GATE-STOP: ..." after the card opened: the start
  config, the sampler, the stop-path test, a stop or K1 in the smoke, no pair passing the smoke) is **no session: no data** (E202.md 7.2).
  Step 11 still collects it, into its **gate stop's record** under `docs/reports/gate-stops/`, never `docs/reports/data/` (step 2 reads
  every `docs/reports/data/*e202*` path as an E202 datum). Commit the record (new files only, its README in the gate-stop form); it is
  never scored. **E202 may be tried again with no amendment** (no burst ran): after a launch that opened no device, **once more the same
  day**, after the look reads FREE again and inside the window (step 9 counts them: a third is refused); after a gate that came after the
  card opened, **not the same day** (step 9 refuses: the kit's same-day rule); a try on a later day needs that day's go and the rest. **A gate
  stop by a kit defect** (E191's first session's kind) is the kit's to fix: a dated kit note and a dated amendment to E202.md before any
  burst datum, verified and landed, then a later session, as E191's note 2 and amendment A1 did. **Every smoke failing at once** (E202.md 8.2:
  UA = 1's polarity) is no data; the UA = 0 fallback is a new program commit and a dated amendment, never improvised.
- **A registered stop** (65 W, 70 C, a second sample off 600 MHz, a line older than 1 s, a holder, the cap, the operator's STOP or SIGTERM)
  after a burst ran: the bursts done stand and are scored as they stand (E202.md 9); the data directory is committed; the missing bursts
  are never re-run without a dated amendment.
- **K1, a launch that did not finish** (the host's "kernel did not finish", or `timeout 10`'s rc 124): the session stops; it may leave a
  hung hart: **never reset the card, no PMIC or power action** (the field manual's gates). Keep the booking and the hold, collect what was
  written, write it up, escalate to the owner and the lab admin.
- **A crash** (fix-e202): the runner's own crash is named in its log ("CRASH: <type>: <message>", before the closing, which still runs),
  in queue.json and in its exit (runner.rc 1): step 10 says 16 ("the runner exited 1 ... (CRASHED ...)"); report it, collect it (step 11
  names a crash with no burst a crash's record, under `docs/reports/gate-stops/`; with bursts, the data stand as they stand and the README
  names the crash); a crash is never re-run around without a dated note. **The runner gone without "session end"** (step 10's RUN-GONE):
  read the box read-only, collect what is there by a dated note's decision, report; the rest rule counts the session at its run's latest
  write.

## 4. Never

- No step 2 but `rb/s03_desk_e202.sh`, and never inside the lab-git lock; no box step without step 2's 0 that day; no step out of the order
  above; never step 7 before the rest has opened; never steps 5, 6 or 8 while a session of ours runs (they refuse).
- **No change to a forecast, a band, a rule, a threshold, K, the order, the R rule, the card time, the cap or a stop** except by a dated
  amendment before the data (E202.md, Amendments); no burst re-run after a stop without one; the scorer only as registered (its sha256 in
  the registration's list) and only after the data commit.
- No device command but the kit's READs (dmcmd_audit_v2 GO): no set, no reset, no governor, TDP, threshold, clock, voltage, fan or firmware
  change; no statistics reset; no PMIC write; no power cycle and nothing that risks one; never kill a device process (no SIGKILL, no
  `timeout -k`).
- Never two sessions of ours on aifoundry3 at once; never beside another user's process or holder (the session's et-who and ps before
  every host process refuse); never on a card but card 0 (the runner refuses unless exactly `/dev/et0_mgmt` and `/dev/et0_ops` exist).
- Never a lab user's login in any file (the collection's scrub masks our box login and refuses any /home/ path left); no number from the
  owner's private checkpoint or his A100 report in any lab file (E202.md 11: the side-by-side stays on his private pages).
- Never touch another run's files on the box: E202 writes only `build/e202mnist/`, `build/e202files/`, `build/e202/`,
  `build/e202-build-*` and the runbook's own `build/q141k/` entries, and step 5's synced files at their committed bytes.

## 5. Labels

Every figure here is **registered** (E202.md) or a **desk check of code** (KIT.md). Nothing here is measured, blind, held out or post hoc.

SPDX-License-Identifier: Apache-2.0
