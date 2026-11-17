# E209's run kit: E208's registered kit, unchanged, for E209's one session on aifoundry2 card 0 under its governor, run from aifoundry2 itself - one runner with one sampler and this card's stop lines live, the card's lock held with et-who empty, the config read and its identity gate first, the stop-path test, the smoke, 62 runs each under a plain `timeout 10` and never killed (a host alive past its TERM is a LEFTOVER, reported and left); the clock read in every sample, never set; THE QUIET DESK FLAG, THE REST RULE before any card command, THE REBOOT GATE, THE ONE-LAB RULE; the never-run search repeated right before the first card command; the collection with E208's data checker and a scrub; the reducer and the frozen scorer after the data commit (Q202; kitted, not run)

*Tue 17 Nov 2026 (week 47), PST, on aifoundry2, desk only (Q202, lane `kit-e209`: begun 02:55 PST, cut by the account's weekly usage limit at
about 03:40 PST, resumed at 06:52 PST from its own log and folder, round Q202c). No card was claimed or opened: aifoundry2 has a card, so every
desk test that runs a built host, the runner, a stand-in session or a stand-in reader ran inside the round's slots and its sandbox (no /dev/et*
device node, an empty /run/lock). No device command was sent, nothing was posted, no simulator was run, no other box was reached. New files only,
all under `tools/claims-v3/e209/`. The registration [`E209.md`](E209.md) (found by content: the commit that added it, its `tools/claims-v3/e209`
subtree `afaa6053...`: reg-e209's `95479783...` with fix-e209's amendment A1; `SHA256SUMS-e209-registration` `c7da26be...`, 22 entries) and every
file its list names stay as committed. **No E209 datum exists. Nothing here changes a forecast, a band, a rule, a threshold, the points, the
order, the card time, the cap, a stop or the scorer.** Where E209.md leaves a reading to the kit, the reading is stated in section 4 before any
datum. **Before the land, Q202c's lane `fix-e209` answered the adversarial verifier's findings (verify-e209, 07:38-08:15 PST) in the
registration (E209.md A1) and here: section 11.***

**His words** (Mon 16 Nov 2026, received at or before 09:48:24 PST; a voice transcription in which "matte mold" is the matmul and "FME" the
tensor unit's multiply-add): "I want you to focus on the matte mold most of all, so I want to have a model which predicts matte mold energy and
number of transistor switches and clock cycles. From based on what I know about the size of a matrix and which operations are contained. See
check how well the timing simulation for the matte mold matches reality and the energy. So I basically I don't care about going deep onto other
operations for now, just go as far as possible on the matte mold, on the FME, yeah, on the matmul operation."

## Results first (desk checks of code and desk reads of committed records; nothing is measured)

| check | result | log |
|---|---|---|
| **the REAL path** (`desk/realpath_e209.py`): runbook step 9's launch exactly as the card day makes it - the box root's `start_e209.sh`, then `session_e209.sh`, then E208's runner `run_mms.py` UNCHANGED on its real path (no --dry) - in a box root made by `make_box_e209.py sync`, each case in a sandbox of its own (two regular files at /dev/et0_ops and /dev/et0_mgmt, a private /run/lock, the host name aifoundry2), stand-ins for every device tool (the reader behind E208's REAL guard, the host, et-who; E208's doubles inside them), the REAL kernel ELF at E136's pin; at the real pace | **DESKTEST-REALPATH-E209 22 of 22 PASS (22 cases)**: MAIN (the box check, the card's lock, the config and identity gates, the stop-path test, the identity read, the 60 s opening rest, the smoke, A1, N1, e29, e30, e14 in the registered order with E209's names, the operator's STOP as run 006 begins, the closing config read, the clock in every sample, E208's reducer unchanged and the frozen scorer reading the session: R0 PASS); STEP (the governor steps e30's clock down inside its busy window: the scorer FLAGS it); the three stop lines (BOARD above 85 W on 3 samples; DIE the shires' mean at 80 C; LATCH a risen latch at 80 C; LATCHHI a latch high from before the session trips nothing); RUNTIME (a runtime line splitting the check record: no check read, never a wrong value; R0 FAIL); HANG (a host deaf to SIGTERM: a LEFTOVER, the card's lock held until it ends by itself, NO SIGKILL); QUIET (a sampler gone quiet: stopped by SIGTERM and started again); HOLDER, BUSYLOCK, NOLOCK, WRONGCFG (each gate: no launch); TWOFAIL; R-REAL (a real reboot-gate record taken with no desk switch: the session unmarked; t_first_ms null at the card-lock gate); and start_e209.sh's seven refusals | [`logs/realpath-e209.txt`](logs/realpath-e209.txt) |
| **the DRY audit** (`desk/dryaudit_e209.py`): every line of E208's runner that reads the dry flag, the real path there and the real-path cases that ran it | **DRY-AUDIT-E209 29 of 29 COVERED** | [`logs/dryaudit-e209.txt`](logs/dryaudit-e209.txt) |
| **the host-output parsers on real committed bytes** (`desk/realbytes_e209.py`): E208's `parse_sparsity`, `last_json` and `parse_ident` (unchanged) on E208's three sessions on this card (every host stdout and stderr, the config reads), E206 arm A's 244 host stdouts and raw config, E191's runtime line spliced at every offset of a committed launch line of this card | **REALBYTES-E209 28 of 28 PASS** | [`logs/realbytes-e209.txt`](logs/realbytes-e209.txt) |
| **the runbook** (`desk/selftest_rb_e209.py`): the window; THE QUIET DESK FLAG on every path; THE P2 COUNT by each process's own script name; THE REST RULE (committed sessions, release records of E208 and E212, the box root's running, cut and never-reached sessions, a dry pass); step 7 and THE REBOOT GATE with the lab's fwgate in its desk mode (one read EQUAL, the guard, a DIFFERENT answer, CONTINUITY, a boot after the read, a missing or changed record, the rest not open, no 6n, past the last start, one session a day, no flag); STEP 2 AT EVERY PIN in a scratch repository with a stand-in kit commit; the launch, THE WAIT by the real script name, THE COLLECTION (a desk session refused outside a desk test, THE SCRUB both ways, COPY-BACK EXACT, E208's checker, the data directory and README); E on every stop path with the round's own helpers; and fix-e209's cases: P15 (step 2 itself changed in a later commit: HISTORY FAIL commit by commit), P16 and S3b (step 2 and step 11 outside a desk test without their one-lab span: refused), E5-E7 (E after a leftover: a device-named process alive or an unresolved leftover in queue.json keeps the flag, the hold line and the booking; a resolved one releases them) | **SELFTEST-RB-E209 72 of 72 PASS** (with a stand-in kit commit: P4-P6 and P14 run only then) | [`logs/selftest-rb-e209.txt`](logs/selftest-rb-e209.txt) |
| **step 13's label check and readings** (`rb/post_e209.py --selftest`; E209.md A1; the frozen scorer's own stand-in day A and variants, scored by it): labels of step 6n's form, a typo, a case spelled in capitals, empty, not a list, not JSON, and the scorer echoing a bad label; E208's 27 anchor runs (18.355041 W, counted apart); the day offset; H4n equal to H4 at offset 0 and H4's seed; a +2% day level taken back out; the points with no window view, no run, a set-aside run, a capped run and a labelled point | **SELFTEST-POST-E209 18 of 18 PASS** | [`logs/selftest-post-e209.txt`](logs/selftest-post-e209.txt) |
| **the build** (`desk/desktest_build_e209.sh`): the box root synced, E208's `build_mms.sh` unchanged against this box's /opt/et | **DESKTEST-BUILD-E209 PASS: kernel aace138caf8071cc7679134211045a89fb09b65cc9a170bfe33409fd36b4fda0 (pin EQUAL); the host's four refusals before it opens a device; the record of today** | [`logs/desktest-build-e209.txt`](logs/desktest-build-e209.txt) |
| **the dry pass** (the box root's `src/dry_e209.sh 0.02`: E208's runner in its --dry mode with E208's doubles, E209's schedule; et-who a stand-in inside the sandbox) | **DRY PASS a2c0 E209 (runner rc 0; 0 runs not clean); device calls 70 (config 2, sampler 1, host 67); runs ran 62 of 62 (2 null); the registered order kept; 45 point ids (e01-e45); card-minutes (unscaled) 32.23; stop None** | [`logs/drypass-e209.txt`](logs/drypass-e209.txt) |
| **the dry listing** (`rb/list_steps_e209.sh`: every step in the brief's order with its script in full; nothing run) | **dry listing: 24 steps listed, 0 run, 0 box calls** (step 2 printed with its kit pin not yet set: the listing sits in the list that pin names) | [`logs/dry-listing-e209.txt`](logs/dry-listing-e209.txt) |
| **dmcmd_audit_v2** (`preflight_e209.sh`: every file the day runs, builds or sends a command from; no --allow) | **dmcmd_audit: GO (12 send site(s), 0 disallowed; allow-list: none)** | [`logs/dmcmd-audit-e209.txt`](logs/dmcmd-audit-e209.txt) |
| **the registration's checks and the box harness** (as step 2 runs them) | points_e209.py --check: POINTS CHECK PASS; rules_e209.py --check: RULES CHECK PASS; plan_e209.py --check: PLAN CHECK PASS; desk/kernel_e209.py --check: PASS; score_e209.py --forecasts rc 0: byte for byte forecasts-e209.txt; make_box_e209.py check: harness: 72 files (E208's 48, E209's box files 4 and its list, the real tiles, fwgate) CHECK PASS; sha256sum -c SHA256SUMS-e209-registration: 22 of 22 OK; MM1-v2's folder list: 114 of 114 OK; MM1-v1's: 77 of 77 OK; E208's src/ list: 48 of 48 OK; E208's registration list: 57 of 57 OK; no kill word outside the words that forbid them | [`logs/checks-e209.txt`](logs/checks-e209.txt) |

## 1. The kit: E208's registered kit, unchanged, for E209's one session (E209.md 6: "the kit lane ports it and lists every change")

**THE BOX ROOT** (`make_box_e209.py`; its every file in `harness-e209.json`, 72 files, each at its sha256): a folder of the card lane's own on
aifoundry2 (never inside the lab clone, never a model session's `ee-*` folder), E208's kit layout (`tools/claims-v3/e208/proposal/src/README.md`):

| what | files | from |
|---|---|---|
| E208's registered kit, every file UNCHANGED at its committed sha256 | 48 (`src/run_mms.py` `5dae80e0...`, `src/mms_common.py` `c3fc7883...` and `src/reduce_mms.py` `b9e32618...` (both pinned by E209.md), `src/mms_ident.py`, `src/fake_card_mms.py`, `src/guard_ettelem.sh`, `src/build_mms.sh`, `src/preflight_mms.sh`, `src/check_mms.py`, `src/status_mms.sh`, `src/stop_mms.sh`, the rgm136 and ettelem sources, the device-command table, the tiles, ...) | `tools/claims-v3/e208/proposal/src/` at its `SRC-SHA256SUMS` (`543e9298...`, 48 lines) |
| E209's four box files | `src/sched/a2c0-E209.json`, `src/session_e209.sh`, `src/start_e209.sh`, `src/dry_e209.sh` | `box/` here |
| the box's src/ list | `src/SRC-SHA256SUMS` (what E208's `check_mms.py --box` reads: E208's 48 lines and the four box files) | `box/SRC-SHA256SUMS-e209` |
| E206's real tiles, at the paths E209's schedule names (relative to the root) | 12 (`tools/claims-v3/kinds/real2/tiles/<fmt>/<name>.bin`, each at `points-e209.json` > `tiles_sha256`) | the lab's committed tiles |
| the reboot gate and its records, unchanged | `fwgate/fwgate.py` (`4d529a57...`) and 6 records | `tools/claims-v3/fwgate/` |

**EVERY CHANGE FROM E208'S KIT** (for the verifier; nothing else differs):
1. **The schedule.** `src/sched/a2c0-E209.json` is the registered `sched-e209.json` (`ec8713a7...`) with ONE key changed, `"kit"` from `"E209
   (E208's kit form)"` to `"1116-mmsweep"`, the word E208's schedule reader (`mms_common.load_sched`, unchanged) requires; every run, the order,
   the forms, the timing (rule 45, cap 55, the 60 s opening rest, the die gate's 180 s), the process (6 s, budget 7.5 s, timeout 10) and the
   smoke are the registration's bytes (`make_box_e209.py check` re-makes it and compares it JSON-equal but for that key). Its file sha256
   `e3d35d5e...`.
2. **The start.** `src/start_e209.sh` in place of E208's `start_mms.sh` (unchanged beside it, never called): one session (E209), the same box
   lock taken first and handed to the session (fd 9, `MMS_BOX_LOCK_FD`), the same last-end bounds (more than 10 minutes, less than 4 hours
   away), the same build-record and harness refusals, and three refusals more: THE FIRST CARD COMMAND's age (step 7's stamp in the past and at
   most 120 s back); THE REBOOT GATE's folder (step 7's `first/<FIRST>` holding one fwgate read record of THIS boot, written today, verdict EQUAL,
   or fwgate's CONTINUITY line; a desk test's record only with `E209_DESKTEST=1`, which marks the session DESKTEST); THE QUIET DESK FLAG up and
   the card lane's (its first word). Step 7's folder is copied into the session's `first/` (committed with the data).
3. **The session wrapper.** `src/session_e209.sh` in place of `session_mms.sh`: runs `src/run_mms.py session --card a2c0 --sched
   src/sched/a2c0-E209.json --t0 <T0> --out sessions/<T0>-a2c0-E209 --deadline-epoch <the window's last end>`, then writes `runner.rc`.
4. **The dry pass.** `src/dry_e209.sh` in place of `dry_mms.sh`: E208's runner in its --dry mode on E209's schedule; DRY PASS also requires E209's
   62 runs in the registered order with E209's point ids and the manifest.
5. **The box's src/ list** gains the four box files; **the real tiles** sit at the schedule's paths under the root; **fwgate** sits beside `src/`.

E208's runner, its two modules, its doubles, its guard, its build, its status and stop scripts and its reducer are E208's bytes, run unchanged:
the box check, the build at the kernel pin, the card's lock held with et-who empty but for the session's own lock line, the config read and
its identity gate as the session's first card command, one sampler at 10 Hz for the session with the stop lines live on every sample, the
stop-path test and the identity read, the 60 s opening rest, the smoke, each run's die gate and holder reads, each host watched every 0.1 s
(E209.md 6).

## 2. The session, as E208's runner runs it with E209's schedule and this card's lines

| | |
|---|---|
| the card's lines (`mms_common.CARDS["a2c0"]`, E208's; the same lines as this card's own in E194's and E200's kits, **which read E189's 65 W / 70 C lines first, for their own programs, and these beside them**: E209 runs these alone, as E208 did on this card three times, E209.md 6; verify-e209's finding 1 asks the orchestrator to confirm them before ready-e209) | the config gate TDP 65 W, threshold 65 C, minion 600 MHz, power state 3; the stops: the board strictly above 85 W on 3 samples in a row, the shires' mean at or above 80 C, the hottest-sensor latch at or above 80 C once it has risen above its first reading; the die gate a run starts under 55 C, waited at most 180 s |
| the schedule (E209's registered) | the smoke (`1x1x4` fp32 zeros, fp16 ones, int8 random, 2 s each), then 62 runs: A1, N1, pass 1 (45 points, A2-A4), pass 2 (10 points reversed), A5, N2; a burst = 10 s at rest, one process of 6 s (a 7.5 s budget) under a plain `timeout 10`, 5 s at rest; sus3 (e39, e43) = 20 s, three processes, 20 s; a null = the same windows with no process |
| the card time | no run starts after 45 card-minutes from the session's config read; the session ends at 55; the deadline is the window's last end; 28.7 card-minutes planned |
| a stop | touches the hosts' `--stop-file` (a host ends at its next launch boundary); a device process alive past its timeout's TERM is a LEFTOVER: the session ends at once, makes no closing read, holds the card's lock until no device process of ours is left (at most 10 minutes); nothing is ever killed |

## 3. The runbook ([`rb/`](rb/); the card lane's brief: [`CARD-LANE-BRIEF.md`](CARD-LANE-BRIEF.md))

Every step is a local script on aifoundry2 (no ssh), sourcing `rb/rb_e209.sh`, with k6's exit codes and bounded waits (at most 520 s a call):

| step | script | what |
|---|---|---|
| 1 | `rb/s02_window_e209.sh <G>` | THE WINDOW: last start G + 1:30, last end G + 3:30 rounded up, G at 20:29:00 or earlier; `window.env` |
| 2 | `rb/s03_desk_e209.sh` (outside the kit's list; its sha256 compared with the land's anchor before it runs) | THE DESK CHECK: outside a desk test, THE ONE-LAB RULE's desk span held (fix-e209); HEAD = GitHub's main (a fast-forward under the lab-git lock when due); the paths clean; the registration and the kit by content; THE HISTORY CHECK (`rb/check_history_e209.py`: additions only under the folder since the registration, net and commit by commit); six lists at their pinned counts and own sha256 (E209's registration and kit, MM1-v2's and MM1-v1's folders, E208's registration and src/); the registration's checks and `score_e209.py --forecasts` byte for byte; `make_box_e209.py check`; `preflight_e209.sh` GO; the kit's desk-test logs; THE FREEZE LINE; the round's sealed record registered (the E206 lesson); no E209 datum in any ref |
| Q | `rb/quiet_e209.sh raise|lower|check <lane>`, `count [--wait]` | THE QUIET DESK FLAG (one line `<lane> <time>`, never another's overwritten or removed) and THE P2 COUNT |
| 4 | `rb/s05_look_e209.sh` | THE LOOK: fwgate's look (no device), et-who, the device processes, CI jobs, the card's lock, the box root's lock |
| 5 | `rb/s07_sync_e209.sh` | THE SYNC: `make_box_e209.py sync <root>`, every file read back at its sha256 |
| 6 | `rb/s08_build_e209.sh start|wait` | THE BUILD: E208's `build_mms.sh` from the root under a plain `timeout 900` (two starts a day at most) |
| 8 | `rb/s10_dry_e209.sh start|wait` | THE DRY PASS: the root's `dry_e209.sh 0.02` |
| 6n | `rb/s06n_neverrun_e209.sh` | THE NEVER-RUN SEARCH REPEATED (`desk/neverrun_card_e209.py`: the registration's scanner and report from copies; every counted record dated against MM1-v2's freeze); REPORTED; its labels to step 13 |
| 7 | `rb/s09_reads_e209.sh` | THE READS: the window, the flag, the build and dry pass of today, the P2 count, 6n under 30 minutes old, one session a day, THE REST RULE (`rb/rest_rule_e209.py`) BEFORE anything reaches the card, et-who free; then fwgate's look, its one read when NEEDS-READ, its guard; the stamp |
| 9 | `rb/s11_session_e209.sh` | THE SESSION: within 120 s of the stamp, the rest and fwgate's guard again, the P2 count, then the root's `start_e209.sh` |
| 10 | `rb/s20_wait_e209.sh` | THE WAIT: the session by its real script name and E208's `status_mms.sh`; a LEFTOVER reported, nothing killed |
| 11 | `rb/s22_collect_e209.sh` | outside a desk test, THE ONE-LAB RULE's collect span held (fix-e209); THE COLLECTION (`collect_e209.py`): the box-tree gate, COPY-BACK EXACT, E208's data checker unchanged (C0-C8, REPORTED), THE SCRUB, the data directory with README (`DATA-README-FORM-e209.md`) and SHA256SUMS; the flag lowered |
| 13 | `rb/s24_score_e209.sh` | after the data commit: E208's reducer unchanged on the committed session; the labels checked (`rb/post_e209.py labels`: an entry naming no point or time case refused, 10); `score_e209.py` (frozen) with step 6n's labels; then `rb/post_e209.py after` (E209.md A1, REPORTED: the points NO DATA named, reading (f)'s day offset, H4n on H4's line); outputs in RB_OUT only |
| E | `rb/end_e209.sh` | THE END OF EVERY PATH: the flag, the desk or collect span, the hold line, the booking, each only if the lane's; nothing under a running session, nor while a device-named process of ours is alive or a session's `queue.json` records an unresolved leftover (17: everything kept; fix-e209) |
| - | `rb/list_steps_e209.sh` | THE DRY LISTING (nothing run) |

## 4. The readings stated here before any datum (where E209.md leaves a choice to the kit)

1. **The card time is counted from the session's own config read** (E208's runner, unchanged: `t_first`). When step 7 sends fwgate's one
   firmware read (its look NEEDS-READ), that read is the day's first card command and precedes the config read by at most 120 s (step 9's bound);
   then the card time from the first card command is the runner's count plus at most 2 minutes. The collection's facts carry step 7's stamp and
   mode beside the runner's figures, so the difference is on record.
2. **A session that never reached the card is not a session on the card.** E208's runner writes `t_first_ms` null in `queue.json` when it ended
   at a gate before its first card command (the box lock, the box check, the card's lock, a holder). THE REST RULE lists such a session and never
   counts it, wherever it is read (the box root, the lab's data, any tree), and the box root is never read twice; "one session a day" counts only
   sessions that reached the card (a `config start:` line). A second session the same day follows one that never reached the card, in a new
   RB_OUT (the runbook test's S1-S5; the real-path case R-REAL).
3. **A gate stop after the session reached the card** (the config or identity gate, the identity read, the stop-path test, the smoke gate) is
   collected and committed as the day's record and never reduced; a second session needs a dated amendment beside E209.md (step 2 refuses while
   an E209 data path exists in any ref).
4. **The clock in every sample:** the sampler's `mhz.minion` in every telemetry line (E208's guard and reader; the real-path test asserts it on
   every sample of MAIN, and E208's checker's C4 counts it); **a step inside a busy window** is flagged by the frozen scorer (STEP, E209.md 7):
   the real-path case STEP steps e30's clock down to 600 MHz 2 s into its process and the scorer flags e30; the same run unstepped in MAIN
   carries no flag.
5. **THE QUIET DESK FLAG** (`W/locks/quiet-desk-aifoundry2`, one line `<lane> <time>`, the round's form) is raised by the card lane right
   before the look and lowered by step 11 after the copy-back, and by `rb/end_e209.sh` on every stop path after it; another's flag is never
   overwritten or removed (the model session's form is respected); `start_e209.sh` refuses unless the flag is up and the card lane's.
6. **The wait's session-name pattern** is the real script name `session_e209.sh`, read as each process's own script (an interpreter's first
   non-option argument), never a command string's text; the same pattern (`session_e[0-9]*.sh`, `queue_e[0-9]*`) counts THE P2 COUNT.
7. **No SIGKILL anywhere:** E208's runner sends SIGTERM only (a plain `timeout 10` on every device process, never `-k`; its own SIGTERM to a
   timeout wrapper that outlived its bound) and leaves a device process alive past its TERM as a LEFTOVER; no E209 file sends or arranges a
   kill (`logs/checks-e209.txt` lists every kill word of the kit's code: none outside the words that forbid them); the real-path cases read every
   record of each case for a kill word and every process for rc 137 or -9.
8. **Step 7 only once the rest has opened:** step 7 reads THE REST RULE before fwgate's look and before any card command; refused, it sends
   nothing (the runbook test's G10); step 9 reads the rest again.
9. **The release records:** E208's and E212's (`RB_RELEASES` names both, joined by ':'); every line naming aifoundry2 card 0 counts.
10. **The dry pass's pace:** 32.23 card-minutes (32.22 in the kit lane's run) at the doubles' pace (unscaled) against the registered plan's 28.7 at E208's measured pace on
   this card; the rule (45) and the cap (55) hold either. Not a forecast of the card's time.
11. **Step 6n is REPORTED, never a gate;** a point found run on this card before MM1-v2's freeze goes into a dated note before the data commit and
   into `ranbefore-e209.json`, which step 13 passes to the frozen scorer (`--labels`) when it names a point.
12. **The sealed record** (step 2, check 10): a sha256 the round's record lists on a line that is not a comment must be registered in
   `tools/claims-v3/sealed-e209/e209-freeze-lines.md` at HEAD before the booking (the E206 lesson); none was posted when this kit was written.
13. **The data directory's name** is `docs/reports/data/<day>-e209-blind-matmul-aifoundry2/` (the day of the session's T0); its README holds no
    forecast number and no score.
14. **The labels are checked before the scorer reads them** (fix-e209; E209.md A1 item 3): step 13 runs `rb/post_e209.py labels` on
    `RB_OUT/ranbefore-e209.json` and refuses (10) when an entry names no point or time case of `points-e209.json`; the card lane corrects the
    dated note and the file, never the scorer.
15. **The points the scorer leaves out unnamed are named** (fix-e209; E209.md A1 item 2): step 13's `rb/post_e209.py after` lists every point
    with no kept run, with kept runs but no time reading (no window view: the governor held 700 MHz through the window) and with a time
    reading but no energy reading; each is NO DATA, and the scores' commit names them in its note.
16. **The day offset and H4n** (fix-e209; E209.md A1 item 1): the same call prints reading (f)'s day offset (the day's kept anchor runs over
    E208's 27 on this card, in W over idle, op time and clock) and H4n (H4 on J over idle divided by 1 + the W offset; REPORTED only) on H4's
    line; H1-H4 are decided as registered.
17. **E keeps everything after a LEFTOVER** (fix-e209; verify-e209's finding 7): `rb/end_e209.sh` refuses (17), releasing nothing, while a
    device-named process of ours is alive or a box-root session's `queue.json` records an unresolved leftover; the orchestrator clears the
    flag, the hold line and the booking once it is resolved.
18. **THE ONE-LAB RULE in the steps** (fix-e209; verify-e209's finding 8): outside a desk test, step 2 refuses (10) unless `onelab.sh show`
    lists the lane's desk span and step 11 unless it lists its collect span; in a desk test (the land and readiness lanes' step-2 runs) each
    only reports it.

## 5. THE REAL-PATH DESK TEST and the audit of every dry branch

A dry pass never runs the branches its flag skips (the round's lessons of Fri 13 Nov and Sun 15 Nov 2026), so E209's session was run on its REAL
path at the desk: `desk/realpath_e209.py` makes a box root with `make_box_e209.py sync`, puts the REAL kernel ELF (E136's pin) and stand-ins at
the built host's and reader's paths (`desk/standin_e209.py`: E208's doubles, unchanged, with the die, the latch, a clock step, a runtime line and
a host deaf to SIGTERM as desk knobs), and launches `start_e209.sh` exactly as step 9 does, each case in a sandbox of its own inside W/nodev.sh.
`desk/dryaudit_e209.py` then lists every line of `run_mms.py` that reads the dry flag (28 lines, and E209's one desk switch: 29 entries), the real path there
and the cases that ran it, each PASS in the committed log: **DRY-AUDIT-E209 29 of 29 COVERED**. E209's runbook has no dry mode (each step is a local script; the dry
listing prints it and runs nothing). The runner's box check's refusal side is not run by a real-path case (its pass side is, in every case that
reaches the card): the build desk test and step 2 check the same pins.

## 6. Device commands

`preflight_e209.sh` (dmcmd_audit_v2 with its table v2, no --allow, no exception) over E208's runner, modules, guard, status, stop, build and
preflight scripts and the host's source, E209's box scripts, the collector, every runbook step but step 2 (which calls it) and fwgate:
**dmcmd_audit: GO (12 send site(s), 0 disallowed; allow-list: none)**: `ettelem config` and `ettelem sample` through E208's guard (TDP, thresholds, power state, frequencies, voltages; power, temperatures,
SP statistics, voltages: every one a READ) and fwgate's one firmware-revisions read (a READ by the owner's rulings). E208's runner also runs
E208's own preflight (`src/preflight_mms.sh --audit-only`, the checker v1 and its table, unchanged) in its box check before its first device
access. ("Reads only" is exact on the management node; every runtime creation also sends the ops node's abort to every submission queue of every
card the device layer enumerates - harmless on a card held alone, and aifoundry2 has one card.) **The host's package counter is not read.**

## 7. The parsers and the real bytes

Every parser on E209's path that reads a device tool's output was fed the lab's committed bytes of that tool (`desk/realbytes_e209.py`): E208's
`parse_sparsity` read every SPARSITY line of E208's three sessions on this card (1658, 1662 and 1666 lines over 99 host stdouts each), each run
record's launch count equal to the parser's on its committed bytes; `parse_ident` read exactly /dev/et0_ops and physical device ID 0 on every
host stderr and /dev/et0_mgmt, ID 0 on every config read; E206 arm A's 244 host stdouts (3914 lines) and its raw config; E191's runtime line
spliced at every offset of a committed launch line of this card: the record read whole or dropped, never a wrong value; a check record split by
the runtime line reads no check (a failed process: the scorer's R0 then FAILS). **REALBYTES-E209 28 of 28 PASS**. The collection runs E208's data lane's checker
unchanged (it read E208's three sessions on this card: ALL PASS); the runbook test runs it on a stand-in session stopped after A1, where its
verdicts are REPORTED as read: C0, C4, C6, C7, C8 PASS; C1 and C2 FAIL (a stopped session: 1 of 62 runs), C5 FAIL (a stop is recorded), and C3
FAIL on one line only, the sampler's stderr holding no device block (the desk's stand-in sampler prints none; the real reader prints its node
and physical device ID, as every committed E208 session on this card shows).

## 8. What the desk cannot show

1. **The host on this card:** the desk ran the built host only to its four refusals; E208 ran the same host source and kernel bytes on this card in
   three sessions. The host's own sha256 depends on the box root's path (it keeps its kernel's default path), so the gate is the kernel ELF's
   bytes and the build record of the day, as in E208.
2. **The governor's clock** on E209's points: read in every sample and every launch, never set; MM1-v2's clock forecast is the day's test.
3. **Our own live collector** may hold the management node for a moment at the free checks (step 7 re-reads up to three times for a reader of
   ours; E208's runner re-reads once after 5 s).
4. **fwgate's one read** happens only if its look reads NEEDS-READ; anything but EQUAL stops E209 on this boot.
5. **The card time at the card's pace:** the plan's 28.7 card-minutes is E208's measured pace; the desk's dry pass is the doubles' pace.

## 9. Files (all new, under tools/claims-v3/e209/; every one but step 2 and the list itself in `SHA256SUMS-e209-kit`)

| file | what |
|---|---|
| `KIT.md`, `CARD-LANE-BRIEF.md` | this file; the card lane's brief |
| `make_box_e209.py`, `harness-e209.json` | the box root: make, check, sync |
| `box/a2c0-E209.json`, `box/start_e209.sh`, `box/session_e209.sh`, `box/dry_e209.sh`, `box/SRC-SHA256SUMS-e209` | E209's four box files and the box's src/ list |
| `preflight_e209.sh` | dmcmd_audit_v2 on the day's files |
| `collect_e209.py`, `DATA-README-FORM-e209.md` | the collection and the data README's form |
| `rb/rb_e209.sh`, `rb/s02_window_e209.sh`, `rb/s03_desk_e209.sh` (step 2, outside the list; pinned by the land's anchor), `rb/check_history_e209.py`, `rb/quiet_e209.sh`, `rb/s05_look_e209.sh`, `rb/s07_sync_e209.sh`, `rb/s08_build_e209.sh`, `rb/s10_dry_e209.sh`, `rb/s06n_neverrun_e209.sh`, `rb/s09_reads_e209.sh`, `rb/rest_rule_e209.py`, `rb/s11_session_e209.sh`, `rb/s20_wait_e209.sh`, `rb/s22_collect_e209.sh`, `rb/s24_score_e209.sh`, `rb/end_e209.sh`, `rb/list_steps_e209.sh` | the runbook |
| `desk/neverrun_card_e209.py` | step 6n's scanner (the registration's from copies, dated against the freeze) |
| `desk/realpath_e209.py`, `desk/standin_e209.py`, `desk/dryaudit_e209.py`, `desk/realbytes_e209.py`, `desk/selftest_rb_e209.py`, `desk/desktest_build_e209.sh` | the desk tests |
| `rb/post_e209.py` | step 13's label check before the scorer and its readings after it (E209.md A1; fix-e209), with its self-test |
| `logs/realpath-e209.txt`, `logs/dryaudit-e209.txt`, `logs/realbytes-e209.txt`, `logs/selftest-rb-e209.txt`, `logs/desktest-build-e209.txt`, `logs/drypass-e209.txt`, `logs/dry-listing-e209.txt`, `logs/dmcmd-audit-e209.txt`, `logs/checks-e209.txt`, `logs/selftest-post-e209.txt` | their logs, as run (fix-e209 re-ran every one on the fixed kit) |
| `SHA256SUMS-e209-kit` | the kit's list (47 files; step 2 pins its count and its own sha256) |

## 10. Labels, and compute

Every figure here is a desk check of code or a desk read of committed records; nothing is measured, nothing is forecast anew. The desk ran under
`/usr/bin/python3` 3.12.3 on aifoundry2 (Ubuntu 24.04, 12 cores), every test that runs a built host, the runner or a stand-in inside the round's
CPU slots (`W/slot.sh`, nice 10) and its no-device sandbox (`W/nodev.sh`; bubblewrap 0.9.0), each only while THE QUIET DESK FLAG was absent.
**The resume:** the lane's first attempt (02:55-03:40 PST) wrote most of these files and ran the build, the parsers, the real path (18 of 19:
its no-kill check read the runner's own words "never kill -9" as a kill) and the runbook test (40 of 44: a test's DIFFERENT answer that changed
nothing, a rest rule that counted a session that never reached the card, and the collection's misread of the checker's table); the resumed
lane fixed each, added the latch cases, the real record case, step 2's pins and history check, the preflight, the DRY audit and the dry listing,
and re-ran every test above.

## 11. fix-e209: the adversarial verifier's findings, answered before the land (Q202c, Tue 17 Nov 2026 PST, desk only)

verify-e209 (07:38-08:15 PST) held the registration and this kit WITH FIXES, none blocking. Q202c's lane `fix-e209` answered each before the
land, on a scratch clone of GitHub main at `030ffa42` with both land patches applied: the registration in E209.md's amendment A1 (its subtree
is now `afaa6053...`), the kit here. **No forecast, point, band, tie, threshold, test, decision rule, plan, stop, order, card time or cap
changed, and neither the scorer nor E208's kit nor any box file changed** (`harness-e209.json` and `box/` are the kit lane's bytes).

| # | finding (verify-e209) | what was done | the desk proof (this commit's logs) |
|---|---|---|---|
| 1, medium | the stop lines need the orchestrator's word; "the same as E194's and E200's" left out that those kits read E189's 65 W / 70 C lines first | the clause in section 2's table; the lines unchanged (E209.md 6, E208's on this card) | for the orchestrator before ready-e209 |
| 2, medium | MM1-v2 against MM1-v1 (H1-H4) is weak | none needed: E209.md sections 7 and 8 state it with the power table | - |
| 3, low | the power simulation leaves out a day-level offset common to every case | E209.md A1 item 1: reading (f)'s day offset printed on H4's line with H4n (REPORTED only); `rb/post_e209.py after`, run by step 13 | fix-e209's own simulation (4,000 days a scenario; E209.md A1): at a -0.93% day offset H4's power falls from 0.46 to 0.31 and the midpoint names MM1-v1 7.3% of the time; the self-test's D1-D5 and T1 |
| 4, low | nothing step 2 checks pins step 2 itself | (a) `rb/check_history_e209.py` also reads the commits since the registration one by one: a commit that modifies or deletes a file of the folder fails, step 2 among them; (b) the brief's steps 0 and 2: step 2's sha256 is compared with the kit's land record before it runs (a step 2 edited to skip (a) is caught only so) | the runbook test's P15 (step 2 changed in a later commit: HISTORY FAIL commit by commit); P8 still refuses a changed registration list |
| 5, low | the frozen scorer echoes labels that name no point or case | E209.md A1 item 3; step 13 runs `rb/post_e209.py labels` before the scorer and refuses (10) on a label that names nothing | the self-test's L1-L7 (L7: the scorer given `e1` echoes it and scores e01) |
| 6, low | a point whose only run has no window view leaves every rule unnamed | E209.md A1 item 2 (NO DATA); step 13's `post_e209.py after` names it, beside every point with no kept run and every point with time but no energy | the self-test's N1-N5 (N1 is verify-e209's attack S3) |
| 7, low | E releases the flag, the hold line and the booking after a LEFTOVER | `rb/end_e209.sh` refuses (17), releasing nothing, while a device-named process of ours is alive or a box-root session's `queue.json` records an unresolved leftover | the runbook test's E5-E7; E1-E4 as before |
| 8, low (optional) | no step script checks the lane's one-lab span | outside a desk test step 2 refuses without the desk span and step 11 without the collect span; in a desk test each reports it (the land and readiness lanes run step 2 in its desk mode) | the runbook test's P16 and S3b, S3 with the span; the pass side outside a desk test is the card lane's own step 2 (a desk test never reads GitHub) |
| 9, low (REPORTED) | the never-run other-card list is out of date and noisy | the brief's 6n row names the other-card runs (E207 on aifoundry3 today, E212's aifoundry1 sessions, E206) and the scanner's two quirks; the scanner unchanged, no rule changes | - |
| 10, nit | logs older than the kit commit; two loose sentences of E209.md | every log re-run on the fixed kit (below); E209.md A1 item 4 corrects T2's second basis and the watts sentence | this commit's logs/ |

**The files** (the land is still new files only, all under `tools/claims-v3/e209/`): **new** `rb/post_e209.py` and `logs/selftest-post-e209.txt`;
**edited before the land** `KIT.md`, `CARD-LANE-BRIEF.md`, `rb/end_e209.sh`, `rb/check_history_e209.py` (the registration's subtree
`afaa6053...` and the check commit by commit), `rb/s03_desk_e209.sh` (the registration list's pin `c7da26be...`, the desk span, the history
check's words, the new log among the logs it reads, its kit pin set at this commit), `rb/s22_collect_e209.sh` (the collect span),
`rb/s24_score_e209.sh` (the label check and the readings), `rb/list_steps_e209.sh` (step 13'), `preflight_e209.sh` (`rb/post_e209.py` audited),
`desk/selftest_rb_e209.py` (P15, P16, S3b, E5-E7; the new log among its stand-in logs) and every log; **unchanged** every other file of the kit
lane's 47 (the box root's harness and files, the collector and its README form, the window, flag, look, sync, build, dry-pass, never-run,
reads, rest, session and wait steps, and the real-path, stand-in, DRY-audit, parser and build tests).

**The logs** (finding 10): fix-e209 made every log in `logs/` on aifoundry2 at the registration's local commit `cb14eae3` with the kit's files
in the working tree, before this commit, as the kit lane made its own: the build, then the runbook test, the real path, the parsers, the dry
pass, the DRY audit, the dry listing, the preflight, the checks and the post self-test, one at a time, each in the round's slot and (where it
runs a host, the runner or a stand-in) the no-device sandbox, only while THE QUIET DESK FLAG was absent. Two say what they are in their own
terms: the dry listing prints step 2 with its kit pin not yet set (`0:unset-until-the-kit-commit`), because the listing sits in the list that
pin names; and the runbook log ran step 2 with a stand-in kit commit (72 rows; at the committed kit, P4-P6 and P14 do not run). The runs at the
committed kit (step 2 at its own pins, the dry listing with the pin set) are recorded in the land record, outside this tree.

SPDX-License-Identifier: Apache-2.0
