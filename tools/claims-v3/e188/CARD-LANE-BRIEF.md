# E188's card-lane brief: what the lane that runs E188 on aifoundry3 does, in order, and what it never does (Q165; kitted, not run)

*Thu 12 Nov 2026 (week 46), PST, on the Intel, desk only (Q165, lane `kit-e188`), beside [KIT.md](KIT.md); the registration is
[E188.md](E188.md) (`878b6f63`, git 12:53:42 PST). No card was claimed, no device command was sent, no lab box was reached, nothing was
posted. No E188 datum exists. This brief changes no rule, forecast, threshold, plan, cap or stop.*

## 1. What the go must carry

- **The owner's go** with a day and one window in PST (the last start and the last end), and **a fresh Tailscale approval for aifoundry3**.
  FULL needs 6,000 s before the last end at its launch (cap 100 card-minutes), plus about 25 minutes of box steps before it and 15 after;
  the fallback (PASSES) 2,400 s (cap 40).
- **E183 first on a shared day.** On any day E183 also runs, E188 runs after it (E188.md section 6): E183's collection (its step 11) ends
  before E188's look, one session of ours at a time.
- **The rest:** E188's launch at least 40 minutes after the end of our last real session on aifoundry3. Step 9 reads it on the box
  (`rb/rest_rule_e188.sh`: every session-log form our kits write, E183's `build/e183/session-t<T0>.log` and E185's and E186's
  `build/eNNN/T<T0>/session.log` among them) and refuses (10) before that; wait and run step 9 again, never around it.
- **The anchor lines** the go names: the kit's commit an ancestor of HEAD; the kit's list `SHA256SUMS-e188-kit` and step 2
  (`rb/s03_desk_e188.sh`, outside that list) unchanged since the kit's commit and at their stated sha256; the kit's list every entry OK; the
  registration's list `SHA256SUMS-e188-registration` (`b098561b...`, 20 of 20 OK); no E188 datum in any ref before step 1.

## 2. The steps, in order (paths under `tools/claims-v3/e188/`)

Run from the lab clone, each with this day's `RB_OUT` (a new directory outside the repo, E188's own: never E183's), the one `RB_LOCK` and,
for step 2, `RB_GITLOCK` (the lab-git lock). k6's drivers bound every remote call: a 15 s hard-killed probe, then 60 s for a read, 600 s for a
copy, a detached launch that returns at once. **A printed login link stops the step (11) and appends `<HH:MM:SS> aifoundry3 needs a check`
to `RB_LOCK`:** the Tailscale approval has lapsed; nothing is retried until a fresh approval, and a run detached on the box keeps running.

| # | the step | what to do with its exit |
|---|---|---|
| 0 | the anchor lines (section 1), by hand, in the lab clone, under the lab-git lock for any pull | any line not as stated: no box step that day |
| 1 | `rb/s02_window_e188.sh <day> <last start> <last end>` | first; today's day only |
| 2 | `rb/s03_desk_e188.sh` (read `~/git0/flush-util/load_guard --status` first: calm or warm only, never hot) | anything but 0 is no box step that day, whatever it names; one exception: a pull whose output shows the upstream did not answer (step 2 again once it answers) |
| 4 | the look, `../q141k-runbook/k6/s05_look_k6.sh aifoundry3`, BEFORE the post | FREE before the post; a holder: bounded polls (`--wait`), at most 30 minutes, else no card that day |
| 3 | the day's one post in `#community-lab` (the one-post rule), under the post's lock: `<ai> **Claude says:** using aifoundry3 for 2 h, until ~HH:MM PST [doc](<the kinds page>)` (FULL), `for 1 h` (PASSES); on a day E183 ran, a rewrite of the day's post from its current text, never a second post | the post's id and before/after text in the lane's result |
| 5 | `rb/s07_a3_sync_e188.sh` | 10: a session or runbook job of ours on the box (read it with its own step); 16: uncommitted synced paths |
| 6 | `rb/s08_a3_build_e188.sh start`, then `wait` while it says 17, or 14 with "no reading" | 0 with TRAIN-HOST-BUILT, TRAIN-CHANGE OK (the built host's behaviour) and HARNESS OK 79; 16 after a failed, overrun or lost build: start once more (the one re-run); a second failure names the fallback; NO-THIRD-BUILD; 14 on start: wait before any second start |
| 7 | `../q141k-runbook/k6/s09_a3_reads_k6.sh` | k6's |
| 8 | `rb/s10_a3_dry_e188.sh start`, then `wait` (or both with `--no-trains`) | 0 |
| 9 | `rb/s11_a3_session_e188.sh FULL yes` (or `PASSES no` in the fallback) | 0 launched (its rest line in the runbook log); 10 refused (the rest, a session or job of ours, no dry pass or build today): read why, never around it |
| 10 | `rb/s20_wait_e188.sh`, again while it says 17 | 0: the session ended with its manifest; 16: a gate stop, its manifest written (read the session log) |
| 11 | the release (` — released` appended to the day's post, every word kept), then `rb/s22_collect_e188.sh` | 0; 14 at the C-session gate: read the collector's output; 16: COPY-BACK not exact or the history check: nothing is scored |
| 12 | the data commit (`docs/reports/data/<day>-e188-one-number-r4-aifoundry3/`, after the public-text scan and the login scrub, through the lab's commit script) | |
| 13 | after the data commit only: `/usr/bin/python3 -I -B tools/claims-v3/e188/rb/check_arms_e188.py --data docs/reports/data/<day>-e188-one-number-r4-aifoundry3 --out $RB_OUT/arms/arm-ofm-e188 --kit-list-sha256 <the anchor line's>` | 0 ARMS READ; 16 ARMS NOT READ (recorded, never a stop: a reported arm). Its outputs stay outside the repo (the tier keeps the arms' readings private: the private Horace Hub quotes their printed lines; public records name the arms by their committed files only) |

**The fallback** (after step 6 names it, or the smoke's train gate fails inside FULL): step 6 `--no-trains` (HARNESS OK 76), step 7, step 8
`start --no-trains` and `wait --no-trains`, step 9 `PASSES no`, steps 10 and 11. Every train rule reads NOT SCORED; E188-LV is the reading.

## 3. Never

- No step 2 but `rb/s03_desk_e188.sh`; no box step without step 2's 0 that day; no step out of the order above; never step 6 while a session
  of ours runs (it refuses).
- **No string is grepped from a binary** to decide anything (E183's kit note 4's lesson): the train change is read from the host's
  behaviour by `train_check_e188.sh` (step 6, every block, the session's start).
- No device command but the kit's READs; no set, reset, governor, TDP, threshold or clock move; no statistics reset; no firmware query; no
  power cycle and nothing that risks one; nothing near card 0's 75 W alarm.
- Never another user's process or session; never a lab user's login in any file (the collection's scrub check stops a tree that holds one).
- Never touch E183's build records on the box (`build/e183-*`, `build/enercat-e183-cmake.log`, E183's jobs): E183's next day copies them
  first. Never move or remove E185's, E186's or E184's leftovers on the box without a dated note.
- Never a second post; never edit a post of another day.
- Never run october-forecast-model's reader before the data commit, inside the repo, or as a rule.

## 4. Labels

Every figure here is **registered** (E188.md) or a **desk check of code** (KIT.md section 6). Nothing here is measured, blind, held out or
post hoc.

SPDX-License-Identifier: Apache-2.0
