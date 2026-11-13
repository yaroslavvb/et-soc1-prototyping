# E189's card-lane brief: what the lane that runs E189 on aifoundry3 does, in order, and what it never does (Q167; kitted, not run)

*Thu 12 Nov 2026 (week 46), PST, on the Intel, desk only (Q167, lane `kit-e189`), beside [KIT.md](KIT.md); fixed before landing on Fri 13
Nov 2026 on aifoundry2 (Q168, lane `fix-e189b`: the registration's new pins, the end bound, the desk on either machine; KIT.md section 10).
The registration is [E189.md](E189.md), as re-made before any datum. No card was claimed or opened, no device command was sent, no other
box was reached, nothing was posted. No E189 datum exists. This brief changes no forecast, band, rule, threshold, K, order, cap or stop.*

## 1. What the go must carry (E189.md section 13)

- **The owner's go** naming E189 on aifoundry3 card 0, at 600 MHz as found, reads only; about 95 card-minutes (cap 110); **a fresh Tailscale
  approval for aifoundry3**; whether a read of the host's package counter is allowed (default no: step 9 then runs without
  `--rapl-allowed`, and the host's share stays assumed and labelled so).
- **The window from the go at G**, inside one Pacific day and at least 30 minutes before the approval lapses: alone, last start G+1:30 and last
  end G+3:30, the day's ONE post 'for 2 h'; after E183 the same day, last start G+3:00 and last end G+5:00, the post 'for 4 h'. The session
  needs its 110 card-minutes (6,600 s) before the last end at its launch, after about 30 minutes of box steps; about 15 minutes of collection
  follow.
- **E183 first on a shared day**, and E189's first card command at least 40 minutes after E183's session end (or after that run's latest file
  write, if it ended without 'session end'). Step 9 reads it on the box (`rb/rest_rule_e189.sh`: every session-log form of ours, a cut
  session counted at its run's latest write) and refuses (10) before that: wait and run step 9 again, never around it.
- **The anchor lines** the go names (E189's LAND.md gives them with the landed commits): the registration's and the kit's commits ancestors of
  HEAD; the registration's subtree `993e549a...` and list `bf1b1bbb...` (10 of 10 OK); the kit's list `SHA256SUMS-e189-kit` and step 2
  (`rb/s03_desk_e189.sh`, outside that list) unchanged since the kit's commit and at their stated sha256, every entry OK; no E189 datum in any
  ref before step 1.
- **E188 waits** for this day's verdict; it runs only on a later go that names it.

## 2. The steps, in order (paths under `tools/claims-v3/e189/`)

Run from the lab clone, each with this day's `RB_OUT` (a new directory outside the repo, E189's own: never E183's), the one `RB_LOCK` and, for
step 2, `RB_GITLOCK` (the lab-git lock). k6's drivers bound every remote call: a 15 s hard-killed probe, then 60 s for a read, 600 s for a
copy, one bounded wait, a detached launch that returns at once. **A printed login link stops the step (11) and appends `<HH:MM:SS>
aifoundry3 needs a check` to `RB_LOCK`:** the approval has lapsed; nothing is retried until a fresh one, and a session detached on the box
keeps running.

| # | the step | what to do with its exit |
|---|---|---|
| 0 | by hand, in the lab clone: `~/git0/flush-util/load_guard --status` (calm or warm only; that is the Intel's tool: from aifoundry2, which has none, read `uptime` instead), then under the lab-git lock `/usr/bin/python3 -I -B tools/claims-v3/e185/rb/check_day2_v2.py tree --pull`, then E189's anchor lines (and E183's, on a shared day, before E183) | any line not as stated: no box step that day |
| 1 | `rb/s02_window_e189.sh <day> <last start> <last end>` | first; today's day only |
| 2 | `rb/s03_desk_e189.sh` with `RB_GITLOCK` set, read load_guard first; **never inside the lab-git lock** (it takes it itself for its pull, with `lockf` on the Intel or `flock` on Linux; nested, it stops with 16) | anything but 0: no box step that day, whatever it names; one exception: a pull whose output shows the upstream did not answer (step 2 again once it answers) |
| 4 | the look, `../q141k-runbook/k6/s05_look_k6.sh aifoundry3`, BEFORE the post | FREE before the post; a holder: bounded polls (`--wait`), at most 30 minutes, else no card that day |
| 3 | the day's ONE post in `#community-lab` (the one-post rule), under the post's lock: `<ai> **Claude says:** using aifoundry3 for 2 h, until ~HH:MM PST [doc](<the kinds page>)` alone, 'for 4 h' after E183; on a day E183 ran, a rewrite of the day's post from its current text, never a second post | the post's id and before/after text in the lane's result |
| 5 | `rb/s07_a3_sync_e189.sh` | 10: a session or runbook job of ours on the box; 16: uncommitted synced paths or a file off its sha256 |
| 6 | `rb/s08_a3_build_e189.sh start`, then `wait` while it says 17 (and after a 14, "no reading": wait again) | 0: RB_OUT/e189-built.txt names what built (LEDGER-BUILT and SPP-BUILT by the kernels' hashes and the hosts' behaviour); 16 when neither built: start once more (one re-run a day); a program still not built is SKIPPED (no data); a third start: NO-THIRD-BUILD |
| 7 | `../q141k-runbook/k6/s09_a3_reads_k6.sh` | k6's (TDP 0 W / 65 C / 600 MHz; et-who clean) |
| 8 | `rb/s10_a3_dry_e189.sh start`, then `wait` | 0 |
| 9 | `rb/s11_a3_session_e189.sh FULL` (add `--rapl-allowed` only if his go allows the package counter) | 0 launched (its rest line in the runbook log); 10 refused (the rest, a session or job of ours, no dry pass or build today): read why, never around it |
| 10 | `rb/s20_wait_e189.sh`, again while it says 17 | 0: ended with its manifest; 16: a gate stop (the lock, a holder, the start config, the stop-path test, the smoke), its manifest written: release, then collect |
| 11 | the release (` — released` appended to the day's post, every word kept), then `rb/s22_collect_e189.sh` | 0 COLLECTED; 16: COPY-BACK not exact, the scrub, the desk-path gate or the history check: commit nothing, read why |
| 12 | the data commit: `docs/reports/data/<day>-e189-blind-day-aifoundry3/` (after the public-text scan, through the lab's commit script, new files only), with a README in the lab's form written by the card lane (results first, registered vs happened, departures dated) | |
| 13 | after the data commit only: `rb/s24_score_e189.sh` | the four rules' words (PASS, FAIL or NOT DECIDED) and each configuration's errors in RB_OUT/scores-e189.json; a FAIL is reported as FAIL; a configuration with fewer than 2 good passes is NO DATA, never a failed prediction |

## 3. Never

- No step 2 but `rb/s03_desk_e189.sh`, and never inside the lab-git lock; no box step without step 2's 0 that day; no step out of the order
  above; never step 5, 6 or 8 while a session of ours runs (they refuse).
- **No string is grepped from a binary** to decide anything: the hosts are read by their behaviour (`hostcheck_e189.py`), the kernels by
  their hashes.
- No device command but the kit's READs (dmcmd_audit GO); no set, reset, governor, TDP, threshold or clock move; no statistics reset; no
  firmware query; no power cycle and nothing that risks one; nothing near card 0's 75 W alarm; never kill a device process.
- No pass, smoke or anchor beyond the registered session (the counters arm is DROPPED: KIT.md section 5); no re-drawn order; no K but the
  registered; no `--reset-ms`; the host's package counter only on his go, and only as our own user.
- Never another user's process or session; never a lab user's login in any file (the collection's scrub refuses any /home/ path left).
- Never touch E183's build records or another run's files on the box; never two sessions of ours on aifoundry3 at once.
- Never a second post; never edit a post of another day.
- Never run the scorer before the data commit, nor on a data directory that is not committed and clean.

## 4. Labels

Every figure here is **registered** (E189.md) or a **desk check of code** (KIT.md). Nothing here is measured, blind, held out or post hoc.

SPDX-License-Identifier: Apache-2.0
