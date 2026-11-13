# E190's card-lane brief: what the lane that runs E190 on aifoundry2's card 0 (arm A) and aifoundry1's card 1 (arm B) does, in order, and what it never does (Q169; kitted, not run)

*Fri 13 Nov 2026 (week 46), PST, on aifoundry2, desk only (Q169, lane `kit-e190`), beside [KIT.md](KIT.md). The registration is
[E190.md](E190.md) (commit `508d48d9`). No card was claimed or opened, no device command was sent, nothing was posted; the one other box
reached was aifoundry1, for a build in a new folder of ours (nothing built there was run). No E190 datum exists. This brief changes no
forecast, band, rule, threshold, order, card time, cap, stop or the scorer.*

## 1. What the go must carry

- **The owner's go** naming E190 for the day: his words of Fri 13 Nov 2026 about 11:30 PST ("Feel free to use all four cards, and you
  don't need to post on Discord", CONTEXT section 102) allow card time on both cards today, each run registered, kitted, verified and
  readiness-checked first; a readiness lane (ready-e190) gives the go lines. Reads only; about 33 card-minutes on arm A and 25 on arm B
  (plan-e190.txt), cap 40 an arm.
- **NO POST AND NO RELEASE.** The owner waived the day's Discord post (his words, Fri 13 Nov 2026 about 11:30 PST). The lane records "the
  owner waived the day's post: his words, Fri 13 Nov 2026 ~11:30 PST" in its result and in the data README; every other etiquette check
  stays (et-who, who, uptime and ps before each session; the card's lock held for the session; `timeout 10` a process).
- **The window from the go**, inside one Pacific day: one window serves both arms (step 1); an arm's launch needs 2,700 s before the last
  end (its 40-minute cap, the closing and a margin) after about 20 minutes of box steps (the look, the sync or the tree's merge, the
  build, the dry pass); about 10 minutes of copy-back and collection follow.
- **The two arms may run at the same time**, on their two boxes. **Never two of our sessions on aifoundry1 at once**: E191 (registered,
  `300d76e4`) also needs card 1; k6's guard refuses a launch beside any session of ours on the box, and the kit's rest rule makes arm B
  wait 40 minutes after any session of ours on aifoundry1 (E191's among them).
- **The anchor lines** ([`ANCHOR-LINES`](#7-the-anchor-lines) below, and OUT/kit-e190/ANCHOR-LINES.md): the registration's and the kit's
  commits ancestors of HEAD; the registration's list `bfe58c58...` (16 of 16 OK); the kit's list `SHA256SUMS-e190-kit` and step 2
  (`rb/s03_desk_e190.sh`, outside that list) unchanged since the kit's commit and at their stated sha256, every entry OK; no E190 datum in
  any ref before step 1.

## 2. THE QUIET HOLD (the round's rule, for this lane)

THE QUIET HOLD is one file for the whole round, `W/locks/lab-quiet-hold`; while it exists no lane writes to the lab clone except the card
lane named on its first line, which commits its data with `LAB_QUIET_HOLD_OWNER` set to that line (`commit_lab.sh` refuses everyone else
with 76). For E190:
- the hold is created before step 2 and removed only after E190's data commit (and the M-records the round asks for), by the round's
  orchestrator or, if the round's brief says so, by this lane itself with its own name on the first line;
- **if another card lane already holds it** (its first line names another lane: E183's or E189's day on aifoundry3), E190's lane neither
  removes nor overwrites it: it waits, in bounded calls, until that lane removes it, then creates its own; or the orchestrator runs both
  under one hold whose owner commits both data directories. Two holds cannot exist at once, and a data commit under someone else's hold is
  refused (76): plan the day so that E190's data commit happens under E190's own hold;
- step 2 pulls the lab clone under the lab-git lock (never inside it); the hold does not stop that pull, it stops writes.

## 3. The steps, in order (paths under `tools/claims-v3/e190/`)

Run from the lab clone on aifoundry2, each with this day's `RB_OUT` (a new directory outside the repo, E190's own), the one `RB_LOCK` and, for
step 2, `RB_GITLOCK` (the lab-git lock, `W/locks/lab-git.lock`). k6's drivers bound every remote call: a 15 s hard-killed probe, then 60 s for
a read, 600 s for a copy, one bounded wait, a detached launch that returns at once. Both boxes are reached by `ssh -o BatchMode=yes`
(aifoundry2 reaches itself the same way). **A printed login link stops the step (11) and appends `<HH:MM:SS> <box> needs a check` to
`RB_LOCK`:** nothing is retried until a fresh approval; a session detached on the box keeps running.

| # | the step | what to do with its exit |
|---|---|---|
| 0 | by hand: `uptime` (aifoundry2 has no load_guard), the anchor lines (section 7) | any line not as stated: no box step that day |
| 1 | `rb/s02_window_e190.sh <day> <last start> <last end>` | first; today's day only |
| 2 | `rb/s03_desk_e190.sh` with `RB_GITLOCK` set; **never inside the lab-git lock** (it takes it itself for its pull; nested, it stops with 16) | anything but 0: no box step that day, whatever it names; one exception: a pull whose upstream did not answer (step 2 again once it answers) |
| 4 | per arm, the look: `../q141k-runbook/k6/s05_look_k6.sh aifoundry2` (arm A) and `... aifoundry1` (arm B; E172's look reads the host's identity by continuity: booted before E82's firmware read) | FREE; a holder: bounded polls (`--wait`), at most 30 minutes, else no session of that arm today. It records our own login on the box in RB_OUT for the scrub |
| 3 | **no post** (waived) | |
| 5 | `rb/s07_sync_e190.sh A` (aifoundry2's tree is a git checkout that merges GitHub main by itself: nothing is copied; 17 until it holds the kit commit; `A pull` pulls it, fast-forward only, if E190's paths there are clean) and `rb/s07_sync_e190.sh B` (the rsync into aifoundry1's `~/nekko`) | 0: HARNESS OK on the box; 17 (arm A): call again; 10: a session or job of ours there; 16: a file off its sha256 |
| 6 | per arm `rb/s08_build_e190.sh <A\|B> start`, then `wait` while it says 17 (after a 14, "no reading": wait again) | 0: RB_OUT/e190-built-<arm>.txt; the kernel at the pin `aace138c...`, the host's four refusals, the record, the harness, the preflight GO; 16: start once more (one re-run a day); a third start: NO-THIRD-BUILD, no session of that arm today |
| 8 | per arm `rb/s10_dry_e190.sh <A\|B> start`, then `wait` | 0 |
| 9 | per arm `rb/s11_session_e190.sh <A\|B>` | 0 launched (its rest line in the runbook log); 10 refused (the rest rule, a session or job of ours, no dry pass or build today, the identity): read why, never around it |
| 10 | per arm `rb/s20_wait_e190.sh <A\|B>`, again while it says 17 | 0: ended with its manifest; 16: a gate stop (the box or build check, the lock, a holder, the start config, the sampler, the stop-path test, the smoke), its manifest written: still collect it |
| 11 | per arm `rb/s22_collect_e190.sh <A\|B>` (no release: no post was made) | 0: COPY-BACK EXACT; 16: not exact: copy again into a new RB_OUT/e190-raw/<arm> |
| 12 | `rb/s23_data_e190.sh` once every arm that ran today is copied back | 0 COLLECTED: `docs/reports/data/<day>-e190-large-gemm/` (aifoundry2/, aifoundry1-c1/, data-e190.json, reduce-e190.txt, SHA256SUMS), the scrub (the box home and our own box login), the desk-path gate, HISTORY OK |
| 12b | the data commit: that directory, after the public-text scan, through `commit_lab.sh` (new files only) with `LAB_QUIET_HOLD_OWNER` set to the hold's first line, with a README in the lab's form written by the card lane (results first: per arm and format, the measured seconds, J over idle and J with the card at rest of one 8,192^3 GEMM, each beside its frozen point; registered vs happened; departures dated; "the owner waived the day's post") | then THE QUIET HOLD removed (section 2) |
| 13 | after the data commit only: `rb/s24_score_e190.sh` | R0, S1-S8 and the headline in RB_OUT/scores-e190.json; a FAIL is reported as FAIL; a cell with no run is NO DATA, never a failed prediction |

## 4. What the session does on each box (run_e190.py, detached by session_e190.sh)

The box and the build (the host name, build/e190rgm's kernel at the pin and its host at today's record, the arm's telemetry reader at its pin,
the tiles, the harness, the preflight GO), the card's lock (`flock -n`, held to the end), the holders (counts only), the start config through
the guard (arm A 65 W / 65 C; arm B 65 W / 65 C / 600 MHz: else no launch), ONE sampler (10 Hz) feeding the stop lines live (arm A board above
85 W on 3 samples in a row, arm B above 75 W; the shires' mean or hottest sensor at or above 80 C on one sample; a trip touches the hosts'
stop file, so a running host ends at its next launch boundary, and nothing further starts), the stop-path test, the smoke (30 s at rest;
fp32, fp16, int8 for 2 s each, checks of C and the cycles-an-op tie), then P1, S1, P2, S2, P3, S3, P4, S4, S5, S6 (gates 55/57 C on arm A,
min(63, rest + 3) / min(64, rest + 4) on arm B, 300 s at most; 10 s at rest; one 6 s process, or twelve; 4 s read), no run after 35
card-minutes, the closing config by 40, "session end", MANIFEST.sha256 last.

## 5. Never

- No step 2 but `rb/s03_desk_e190.sh`, and never inside the lab-git lock; no box step without step 2's 0 that day; no step out of the order
  above; never step 5, 6 or 8 while a session of ours runs on that box (they refuse).
- No device command but the kit's READs (dmcmd_audit GO, 22 send sites): no set, reset, governor, TDP, threshold or clock move; no
  statistics reset; no firmware query; no residency read; no power cycle and nothing that risks one; never kill a device process.
- Not aifoundry1's card 0 (its 75 W PMIC alarm trips on fp32 random, E84) and not aifoundry3 (E183's and E189's day).
- No run beyond the registered order; no change to `--seconds 6 --budget 7.5`, the twelve processes, the gates or the stops.
- Never another user's process or session; never a lab user's login in any file (the collection's scrub replaces our own and refuses any
  /home/ path or login left).
- Never two sessions of ours on aifoundry1 at once; never a session of ours beside a dry pass or a build on the same box.
- No post and no release today (waived); never edit a post of another day.
- Never run the scorer before the data commit, nor on a data directory that is not committed and clean.

## 6. Labels

Every figure here is **registered** (E190.md) or a **desk check of code** (KIT.md). Nothing here is measured, blind, held out or post hoc.

## 7. The anchor lines

The kit's lane writes them with the landed commit (OUT/kit-e190/ANCHOR-LINES.md): the registration `508d48d9...` and the kit commit ancestors
of HEAD; the registration's list `SHA256SUMS-e190-registration` `bfe58c58...`, 16 entries, every one OK; the kit's list `SHA256SUMS-e190-kit`
at its count and sha256, every entry OK; step 2 (`rb/s03_desk_e190.sh`) at its sha256; no `docs/reports/data/*e190*` path in any ref.

SPDX-License-Identifier: Apache-2.0
