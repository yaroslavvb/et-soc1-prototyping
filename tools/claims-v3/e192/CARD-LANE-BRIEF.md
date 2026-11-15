# E192's card-lane brief: what the lane that runs E192 on aifoundry3 does, in order, and what it never does (Q176; kitted, not run)

*Sat 14 Nov 2026 (week 46), PST, on aifoundry2, desk only (Q176, lane `kit-e192`), beside [KIT.md](KIT.md). The registration is
[E192.md](E192.md) (both freeze lines in its section 0). No card was claimed or opened, no device command was sent, no other box was reached,
nothing was posted. No E192 datum exists. This brief changes no arm, value, order, window, threshold, stop, reduction, card time or cap.
Changed in place the same evening, before the land, by lane `fix-e192` (KIT.md section 12): section 1 now asks the go to name the audit table
it accepts and whether a launch refused before anything opened may be launched again that day; section 3 says what a session is.*

## 1. What the go must carry (E192.md section 12)

- **The owner's go** naming E192 on **aifoundry3 card 0, at 600 MHz as found, reads only**; **about 52 card-minutes, cap 65** (from the
  session's first card command); **the 40-minute rest** before E192's first card command and after its end; and **the day's post** in the
  lab's channel, or **his waiver of it for that day** (his waiver of Fri 13 Nov 2026 covered that day only). Optionally: the plain sampler
  (`--plain-sampler`, if he reads only the stock audit table; KIT.md section 3).
- **The audit table the go accepts for command 74** (the per-sensor sampler's): E144's, the default (the first card command is the
  per-sensor probe, and command 74 group 0 is sent when it answers), or the stock table alone (then `--plain-sampler`: command 74 is never
  sent). KIT.md section 3.
- **Whether a launch refused before anything opened may be launched again that day.** A launch that ends "no device opened" (exit 2, or 3 at
  the wrapper's free check or at the probe's lock) sent no card command: card time 0, skipped by every rest rule. The kit's reading, for the
  go to confirm or refuse: it is not a session, and once the look reads FREE again it may be launched once more inside the same window
  (KIT.md section 5 item 9). Our own live collector on the box can make a single `et-who --check` read "held" (KIT.md section 10 item 7).
- **Both freeze lines in HEAD before any datum**: `fa385703ee5b385a2bb54834644d5e34a999ddbb2fd8a2eeeb2ead83ae9cc461` and
  `49bec965bf6921ba40aa1eb22bd364a41062893ff3b8109be14116ee44e49b74`, each on one line of `tools/claims-v3/e192/E192.md` at the landed
  registration (step 2 checks both, and that no E192 datum is in any ref).
- **The anchor lines** of E192's land files: the registration's and the kit's commits ancestors of HEAD; the registration's subtree
  `c78351f9...` and list `dd0a8963...` (30 of 30 OK); the kit's list `SHA256SUMS-e192-kit` and step 2 (`rb/s03_desk_e192.sh`, outside
  that list) at their stated sha256, every entry OK.
- **The window from the go at G**, inside one Pacific day: alone on aifoundry3 that day, last start G+1:30 and last end G+3:30; after another
  session of ours there that day, its end plus the 40-minute rest before E192's first card command (step 9 reads the rest on the box and
  refuses before it). The session needs its 65 card-minutes (3,900 s) before the last end at its launch, after about 40 minutes of box steps;
  about 15 minutes of collection follow.
- **Order on aifoundry3**: after the session(s) of ours already there that day, with the rest between; never two of ours there at once.

## 2. The steps, in order (paths under `tools/claims-v3/e192/`)

Run from the lab clone, each with this day's `RB_OUT` (a new directory outside the repo, E192's own: never another run's), the one `RB_LOCK`
and, for step 2, `RB_GITLOCK` (the lab-git lock). k6's drivers bound every remote call. **A printed login link stops the step (11) and
appends `<HH:MM:SS> aifoundry3 needs a check` to `RB_LOCK`:** nothing is retried until the check is cleared; a session detached on the box
keeps running.

| # | the step | what to do with its exit |
|---|---|---|
| 0 | by hand: `uptime` on aifoundry2 (the 1-minute load below 8, else wait); E192's anchor lines at HEAD; no E192 datum in any ref | any line not as stated: no box step that day |
| 1 | `rb/s02_window_e192.sh <day> <last start> <last end>` | first; today's day only |
| 2 | `rb/s03_desk_e192.sh` with `RB_GITLOCK` set; **never inside the lab-git lock** (it takes it itself for its pull; nested it stops with 16) | anything but 0: no box step that day; one exception: a pull whose output shows the upstream did not answer (step 2 again once it answers) |
| 4 | the look, `../q141k-runbook/k6/s05_look_k6.sh aifoundry3` | FREE; a holder: bounded polls (`--wait`), at most 30 minutes, else no card that day |
| 3 | the day's post after the look reads FREE, or his waiver recorded | the post's id and text in the lane's result, or the waiver's words and time |
| 5 | `rb/s07_a3_sync_e192.sh` | 10: a session or runbook job of ours on the box; 16: uncommitted synced paths or a file off its pin |
| 6 | `rb/s08_a3_build_e192.sh start`, then `wait` while it says 17 (after a 14, "no reading": wait again) | 0: RB_OUT/e192-built.txt (the hashes; the box's tools and pins OK); 16: the build failed: start once more (one re-run a day); a third start: NO-THIRD-BUILD, no session that day |
| 7 | `../q141k-runbook/k6/s09_a3_reads_k6.sh` | k6's (TDP 0 W / 65 C / 600 MHz; et-who clean) |
| 8 | `rb/s10_a3_dry_e192.sh start`, then `wait` | 0 (E192-DRY OK) |
| 9 | `rb/s11_a3_session_e192.sh FULL` (add `--plain-sampler` only if his go names it) | 0 launched (its rest line in the runbook log); 10 refused (the rest, a session or job of ours, no dry pass or build today): read why, never around it |
| 10 | `rb/s20_wait_e192.sh`, again while it says 17 | 0: ended, its manifest written (a STOP after passes is shown: the passes done are reduced as they stand); 16: stopped before any pass (a refusal, the card not free, the smoke or a gate): still collect |
| 11 | the release of the day's post (or nothing under his waiver), then `rb/s22_collect_e192.sh` | 0 COLLECTED; 16: COPY NOT EXACT, the desk-path gate, the holder-line check, the scrub: commit nothing, read why |
| 12 | the data commit: `docs/reports/data/<day>-e192-intbits-aifoundry3/` (after the public-text scan, through the lab's commit script, new files only), with the README in KIT.md section 9's form | |
| 13 | after the data commit only: `rb/s24_reduce_e192.sh docs/reports/data/<day>-e192-intbits-aifoundry3` | the reducer's output and the section 7 checks in RB_OUT, committed by the records lane; a failed check is reported as FAILED, never a datum removed for it |

## 3. Never

- No step 2 but `rb/s03_desk_e192.sh`, and never inside the lab-git lock; no box step without step 2's 0 that day; no step out of order; never
  step 5, 6 or 8 while a session of ours runs (they refuse).
- No device command but the kit's READs (`preflight_e192.sh`: the plain chain GO); **no set, reset, governor, TDP, threshold or clock move;
  no statistics reset; never the firmware-revisions query; no power cycle and nothing that risks one;** never kill a device process (the
  kit stops through `OUT/STOP`, and the launch in flight finishes).
- No arm, value, order, window, pass, smoke, threshold, stop or reduction but the registered: the reference session runs as committed; no
  re-drawn order; no second session that day without a dated amendment first (a session is a launch that sent its first card command, the
  probe or the sampler; a launch refused with "no device opened" is the go's to allow again, section 1).
- **No forecast number and no score in any lab file**: the forecasts are sealed by their two freeze lines; the model session scores them.
- Never another user's process or file; never a lab user's login in any committed file (our own box login is masked by step 11).
- Never touch another run's files on the box: E192's files live in its own root (`build/claims-v3/aifoundry3/e192/`) and its sessions in
  `build/e192/`; never two sessions of ours on aifoundry3 at once.
- Never run the reducer before the data commit, nor on a data directory that is not committed and clean.
- No simulator on any lab box; no host compute beside the run.

## 4. Labels

Every figure here is **registered** (E192.md) or a **desk check of code** (KIT.md). Nothing here is measured, blind, held out or post hoc.

SPDX-License-Identifier: Apache-2.0
