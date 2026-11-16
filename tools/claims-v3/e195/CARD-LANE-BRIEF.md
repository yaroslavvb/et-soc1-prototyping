# E195's card lane brief: aifoundry3 card 0, one session, run from aifoundry2 (Q185, lane kit-e195; fixed in Q191, lane fix-e195; kitted, not run)

*Sun 15 Nov 2026 (week 46), PST. For the card lane that runs E195 after its verifier, its fix pass and a readiness check, on the owner's
go. The go lines a readiness lane writes are the authority on the day; this brief is the kit's own account of the order, the gates and the
stops. Every path is under `tools/claims-v3/e195/` unless named. Nothing here changes an arm, a value, the order, a window, a threshold, a
stop, the cap, the rests or the reduction (E195.md, registered). Fixed before any E195 datum (Q191, lane fix-e195, Sun 15 Nov 2026):
row E now ends every stop path with the one-lab calls (verify-e195's finding 2), and G2 states where the cap counts from (finding 3,
KIT.md section 4's dated reading).*

## 1. What the go must carry (E195.md 13)

- **G1, the run:** E195 on aifoundry3 card 0, 600 MHz as found (pinned by its zero TDP), reads only (dmcmd_audit GO), nothing set; one
  session of ours on aifoundry3 at a time. His standing words of Sun 15 Nov 2026 10:22:36 PST ("don't worry about discord post, just use the
  machines, nobody is using them") are read by the lab as the go for an idle card's registered run once kitted, verified and readiness-checked
  (E195.md 13); a go of his that changes a registered item is a dated departure.
- **G2, the size:** the smoke 901 and passes 910-917 (910 the warm-up); about 43 card-minutes, **cap 45** from the session's first card
  command, its holder check (KIT.md section 4's dated reading, Q191: E195.md 6's clock window, "the session's launch plus 45 minutes",
  and request.md 10's sizing, the session's smoke, passes and two config reads). Step 7's single config read is a card command for the
  rests (G3) and is **reported apart**: the data README gives its time and the minutes from it to the session's last card command.
  The shorter variant (910-915) only by a dated amendment before the session.
- **G3, the rests:** at least 40 minutes between the previous session of ours on aifoundry3 card 0 (its last card command) and E195's
  FIRST CARD COMMAND OF ANY KIND (step 7's config read counts), and 40 minutes after E195 before the next session of ours there.
- **G4, the window (E195.md 6):** from G, last start G+1:30, last end G+3:00, inside one Pacific day. Under his standing go, G is the time
  the go lines define (as E191's second session took its booking's time).
- **G5, the post:** none, by his standing waiver (Sun 15 Nov 2026 10:22:36 PST); he can ask for one.
- **G6, the memory shires' counters: NOT READ** (KIT.md section 4: every x9_ item runs `--no-ms`, the registered fallback, because the
  worker firmware's source at the card's running build could not be established: C6 reads NO DATA and every write price carries E195.md
  section 4's label). The go may instead carry a dated amendment, before any datum, that restores the default (the counters read) on the
  version-matched public source's evidence; the kit does not run that variant as it stands.

## 2. The steps (one RB_OUT; k6's exit codes: 0 done; 10 refused; 11 a login link; 12 no answer; 13 past a bound; 14 a call failed; 15 a
holder for 30 minutes; 16 a gate says stop; 17 call again)

Setup (the go lines name the round's paths; none is written here): `W` the round's workflow folder, `LAB` the shared lab clone; a new,
empty `RB_OUT` under the lane's own folder (E195's own, never another run's); `RB_LOCK` the round's lock file of checks (a login check
appends one line to it); `RB_GITLOCK` the round's lab-git lock; `cd $LAB`; every step one plain call from a script file (no `bash -c`, no
background `&`). Inside slot.sh a lock wait uses `-E 76`, never 75. nodev.sh is not needed: no step runs a built binary on aifoundry2
(step 2's dry listing runs the kit's runner in its own dry mode, Python only).

| step | what | expected |
|---|---|---|
| B | `bash $W/book.sh take aifoundry3 <lane>` | 0 BOOKED (G = this moment under the standing go); 1: make no ssh call to aifoundry3 at all; stop |
| 0 | `uptime` (the load rule: wait while the 1-minute load is above 8, until below 6); `bash $W/onelab.sh desk <lane>` (THE ONE-LAB RULE: waits for no other lane's collect span and no commit of ours); the anchor lines of the land files at LAB's HEAD | 0; `onelab` 3 = call again; an anchor line off, or any other failure once `desk` has run: E |
| H | `bash $W/hold.sh add <lane>`; `git -C $LAB status --porcelain --untracked-files=all` reads 0 lines | else E |
| 1 | `bash rb/s02_window_e195.sh <today> <G+1:30> <G+3:00>` | 0 "fits now: E195 (its 45 card-minutes)"; "fits now: nothing", or any other exit: E |
| 2 | `bash $W/slot.sh bash rb/s03_desk_e195.sh` (never inside the lab-git lock); then `bash $W/onelab.sh undesk <lane>` | 0 "desk check: ... PORT CHECK PASS; DRYLISTING-E195 PASS; no E195 datum in any ref; the preflight GO; the kit's desk tests' logs"; any 16 or 10, or any other exit: E |
| 4 | `bash ../q141k-runbook/k6/s05_look_k6.sh aifoundry3` | 0 FREE (it records the box login for step 11); 17 HELD: again with `--wait`, 30 minutes at most; 15: E |
| 3 | the post: waived (his words, Sun 15 Nov 2026 10:22:36 PST): record them | |
| 5 | `bash rb/s07_a3_sync_e195.sh` | 0 "synced ... HARNESS OK"; 10 a session or job of ours on the box: read why; 16 uncommitted paths or a pin off |
| 6 | `bash rb/s08_a3_build_e195.sh start`, then `... wait` again while 17 (a 14 "no reading": wait again) | 0 "built today on aifoundry3 ... pins and tools read OK"; 16: start once more (two starts a Pacific day at most; a third is NO-THIRD-BUILD: no session that day) |
| 7 | **`bash rb/s09_a3_reads_e195.sh` ONLY ONCE THE REST HAS OPENED** (40 minutes after our previous session's end on aifoundry3); it reads the rest on the box first and sends no config read before it | 10 "the rest has not run": call again after it; 0 "config TDP 0 W / 65 C / 600 MHz, et-who clean" (k6's step 7, unchanged); then 8 and 9 without delay |
| 8 | `bash rb/s10_a3_dry_e195.sh start`, then `... wait` (about 3 minutes) | 0 "E195-DRY OK: 288 device calls" |
| 9 | `bash rb/s11_a3_session_e195.sh FULL` | 0 "e195 launched (T0 ...)"; 10: read the refusal (the rest, a stop file left, today's session that opened the card, the dry pass or the build not today) |
| 10 | `bash rb/s20_wait_e195.sh`, again while 17 (about 45 minutes) | 0 RUN-ENDED (the queue end line, passes complete k of 8); 16 GATE-STOPPED or MAIN-CRASHED: still collected; 14 RUN-GONE: read the box's logs, read-only |
| C | `bash $W/onelab.sh collect <lane>` | 0; 3 = call again |
| 11 | `bash rb/s22_collect_e195.sh` | 0 "E195 COLLECTED: ... (it is docs/reports/data/<day>-e195-x09-dramtoggle-aifoundry3/)" or a gate stop's record under docs/reports/gate-stops/; any other exit: report it (the box's files stay, read-only), then E |
| 12 | the README in DATA-README-FORM-e195.md's form, the public-text scan, then `LAB_QUIET_HOLD_OWNER=<lane> bash $W/commit_lab.sh "<subject>" "<body>" <the data directory>` (from a script file; on exit 5 or 6 run it again); then `bash $W/onelab.sh uncollect <lane>` | "COMMIT_LAB: pushed <sha>"; a commit that never pushes, or a scan that finds what may not be published: report it (the data stays in RB_OUT), then E |
| E | **every stop path ends here, and so does the normal end** (Q191, verify-e195's finding 2): `bash $W/onelab.sh undesk <lane>` and `bash $W/onelab.sh uncollect <lane>` (THE ONE-LAB RULE on every stop path: a stop inside steps 0-2 leaves this lane's desk flag, a stop between C and the data commit's push its collect flag; each call removes only this lane's own flag and is harmless when there is none, so E runs both); then `bash $W/hold.sh remove <lane>` (after H); `bash $W/book.sh release aifoundry3 <lane>` | each 0 |
| 13 | after the data commit only: `bash rb/s24_reduce_e195.sh docs/reports/data/<day>-e195-x09-dramtoggle-aifoundry3` | 0 "reduced (...)": RB_OUT/x09-e195.json and .txt, leftover-e195.json and .txt, committed by the records lane in a dated note; no score |

The dry listing of every step: `bash rb/list_steps_e195.sh <an empty scratch dir>` (13 steps, 0 box calls).

## 3. When it stops

- **Every stop path ends at row E** (the one-lab calls, then the hold and the booking), from step 0 on: a stop inside steps 0-2
  ends this lane's desk span, a stop between C and the data commit's push ends its collect span (THE ONE-LAB RULE).
- **A refusal or a gate before any pass** (step 10's GATE-STOPPED): step 11 collects it as a gate stop's record (never a datum, never
  reduced). A launch that opened no device ("no device opened" on its refusal or gate line, no start config read) is not a session: it may
  be launched ONCE more from the same RB_OUT inside the same window once the look reads FREE again (step 9 allows it and writes
  RB_OUT/e195-relaunch.txt; the go confirms it). A gate after the start config read (the config not as found, the smoke's gates) ends the
  day for E195: no second session that day (step 9 refuses it).
- **The smoke's gates** (E195.md 5): the registered smoke_gate_x09.py and the kit's peak gate (the smoke's highest board reading below
  65 W and its highest die reading below 65 C): a failure is "no pass that day: no data".
- **A live stop** (the board at or above 70 W on three samples in a row on the live telemetry: watch_x09.py; the die at or above 70 C:
  the runner; a stale sampler: the runner; a holder; a failed pass): the queue ends; the main passes that ended ok are reduced as they
  stand (910 the warm-up); a pass cut short is committed and reported, not reduced (E195.md 7, 12). Step 10 reads RUN-ENDED (0).
- **A pass that ended without a registered stop** (a traceback in the runner: "ended without a registered stop", session.rc 4): step 10
  reads MAIN-CRASHED (16); report it, kill nothing, collect it; a dated note decides whether its passes are reduced.
- **A stuck sampler** (one that ignored SIGTERM for 30 s): never killed; it ends at its own --seconds bound (the pass's estimate plus
  900 s, about 46 minutes); the session stops after that pass and skips its closing config read; the lane reports it; the next session
  of ours on aifoundry3 waits until it has ended (k6's look reads it as our own holder).
- **A stop file** the session or the watcher wrote (build/x09-STOP in E195's root) stays after the session: the session and step 9 refuse
  while it exists; a dated note moves it aside before another E195 session.
- **By hand, during the session:** `touch <E195's root>/build/x09-STOP` (every host launches nothing more, no further pass starts) and,
  to end the pass in flight at its next item, also the running pass's `STOP` (`build/claims-v3/aifoundry3/x09-T<T0>/p<pass>/STOP`); or
  send the session SIGTERM (it writes both itself and closes). Never a kill of any process of the session.
- **A launch that does not finish** (a hung hart): stop, keep the records, report to the owner and the lab admin; a card reset is never
  this run's to make.

## 4. Never

- No firmware, OTA, flash, PMIC write, card reset, PCIe recovery, driver reload, governor, TDP, threshold or clock set, power cycle or
  anything that risks one; no statistics reset (`--reset-ms`); never the firmware-revisions query in this kit (it needs none).
- No SIGKILL, and no signal at all, to a device process (the sampler, the host, the heater): every one ends by itself; plain `timeout 10`
  (no `-k`) is the runner's own backstop.
- Never two sessions of ours on aifoundry3; never a session during a runbook job; never on aifoundry2's own card (no step touches it).
- Never write outside E195's root (`build/claims-v3/aifoundry3/e195`), `build/e195/` and the runbook's `build/q141k/` entries on the box.
- No E195 file edited after the land: a change is a dated note or amendment, before the data it touches.
- No forecast number, no score: the model session scores its sealed forecast privately after the data commit.
- Nothing in any public file beyond the public tier (the round's tier rules), no lab user's login, no credentials or access paths; the
  collection masks our own box login and refuses any other account's.

SPDX-License-Identifier: Apache-2.0
