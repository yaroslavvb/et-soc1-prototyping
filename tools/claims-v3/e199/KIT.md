# E199's run kit: E192's reference session run as committed on aifoundry1 card 1 (ET_DEVICES=1, card 1's lock), the identity gates and the watch, card 1's live stops, the runbook from aifoundry2 in E191's form, the real-path, real-bytes, real-build, rest-rule and runbook desk tests (Q191; kitted, not run)

*Sun 15 Nov 2026 (week 46), PST, on aifoundry2, desk only (Q191, lane `kit-e199`, resuming Q190's lane cut at about 18:05 PST by the
account's weekly limit), on E199's registration (as fixed before the land, below: its local commit re-made with `git am` on GitHub main
`72514ce5`, its tools/claims-v3/e199 subtree `070b4e2d...`, `SHA256SUMS-e199-registration` `4d05fe0a...`, 17 entries, every one OK;
first written on `b7af9be5` at subtree `d8fb41e1...`, list `4bf52246...`). No card was claimed or opened, no device command was sent, nothing was posted. The one look at aifoundry1 (21:5x PST, while no lane
booked it) was read-only: `uptime -s` 2026-10-26 15:02:04, bubblewrap 0.9.0 present, et-who "No process holds an ET-SoC-1 device node or
card lock.", the four nodes and both lock files, `ls` of our own build folders (`~/nekko/build/ettelem`, `build/sparsity/host`,
`build/claims-v3/aifoundry1-c1`, `build/e190`, `build/e191`; no `build/e199`). Every desk run of a stand-in, a runner, a built host or a
session ran inside the round's CPU slot and its no-device sandbox, each test making its own private `/dev` inside it. New files only, all
under `tools/claims-v3/e199/`; E199.md and the registration's files stay as committed. No E199 datum exists. **Nothing here changes an arm,
a value, the order rule, a window of the reducer, a threshold, a rule, the reduction, the card time or the cap** (E199.md section 15); the
kit adds stops that end a session early, before its first launch or through the registered stop file. Python is `/usr/bin/python3` 3.12.3
(numpy 1.26.4) at the desk; the box's `python3` runs the reference session, as E192's did.*

*Fixed before the land, Mon 16 Nov 2026 (week 46), PST (Q191, lane `fix-e199`, desk only on aifoundry2: no card claimed, no lab box
reached, nothing posted), after verify-e199 read this kit HOLDS WITH FIXES. The registration under it was fixed first: freeze line 1 is
now `deb4a7d1...` (the forecast's rule words corrected, every price unchanged), freeze line 2 is the model session's sealed card-1 forecast
`1c5d8fa3...` (posted 01:28:51 PST, before the land), and a price is decided at 4 measured passes. Here: every pin on the registration
moved (section 13); step 2 checks freeze line 2 on one line and prints it (F2); the identity gate (a) refuses a runtime line naming
another device (F5); the runbook test refuses to start from 23:20 Pacific (F6) and its WN case shows the wait's pattern matches the real
name only (F9); a desk test never waits inside its sandbox for the quiet-desk flag (F7); the brief names step 1's stop path (F8); the
card-time estimate is about 60 (F4). Every desk test was re-run on the final bytes. Nothing in the kit changes an arm, a value, the order
rule, a window of the reducer, a threshold, the reduction or the cap.*

## Results first (desk checks of code; nothing is measured, nothing is forecast)

| check | result | log |
|---|---|---|
| **THE REAL-PATH DESK TEST** (`desk/desktest_realpath_e199.sh`, `desk/realpath_e199.py`, stand-ins `desk/standin_e199.py`): `session_e199.sh`'s real path in a private `/dev` holding aifoundry1's four node names (each a bind of `/dev/null`: character nodes that are no card), card 1's and card 0's lock files, a private PID namespace, the host name aifoundry1: the dry path; the real path through THE IDENTITY GATE (a) and (b), the smoke and TWO PASSES with a stop by hand in the gap (THE STOP PATH); the plain sampler; holders on either card; the identity gate both ways; THE WATCH; card 1's live stops; the smoke gate, the cap, the gate's death, a signal; aifoundry1's runtime line inside a host's line; run_session.sh's own refusals (its line 65 among them, which E192's kit could not run) | **DESKTEST-REALPATH-E199 78 of 78 PASS** | [`logs/desktest-realpath-e199.txt`](logs/desktest-realpath-e199.txt) |
| **THE REAL-BYTES TEST** (`desk/realbytes_e199.py`): every reader of a device program's output fed the bytes the lab committed from aifoundry1 card 1 (1a4bc1e3: the runtime line inside the ledger host's JSON line; 7156ac15) and from E192's aifoundry3 session (a6e17e83): run_block.py's reader on 3,255 real INTBITS records, the runtime line at every byte offset, the REAL run_block.py end to end, the gate's watch on real stderr, the identity gate (a) on real config reads, the telemetry readers | **REALBYTES-E199 11 of 11 PASS (RB3: 662 offsets: 2 read exactly, 7 lost, 653 raise, 0 wrong)** | [`logs/realbytes-e199.txt`](logs/realbytes-e199.txt) |
| **the real build** (`desk/realbuild_e199.sh`): build_e199.sh on this desk's /opt/et (aifoundry1's "() 15.1.0" toolchain): check_elf, E192's loop_order 16 of 16, the arm table byte for byte, the hashes beside E192's | **REALBUILD-E199 5 of 5 PASS (the selection fails here as it must: this desk's /opt/et has no ET_DEVICES; the kernel's .text equals both E192 builds' `aafdba4b...`, its ELF E192's desk build's: reported)** | [`logs/realbuild-e199.txt`](logs/realbuild-e199.txt) |
| **the runbook** (`rb/selftest_rb_e199.sh`: a fake ssh and rsync, a stand-in aifoundry1, a scratch repository; the box's build REAL; the REAL session_e199.sh launched by step 9 and waited on by step 10's pattern) | **SELFTEST-RB-E199 21 of 21 PASS** | [`logs/selftest-rb-e199.txt`](logs/selftest-rb-e199.txt) |
| **the rest rule** (`rb/selftest_rest_e199.sh`): E190 arm B's and E191's two sessions' logs AS COMMITTED (times shifted), E199's own wrapper's real logs from the real-path test, cut sessions, every tree of ours, energy.sh folders, dry markers | **SELFTEST-REST-E199 16 of 16 PASS** | [`logs/selftest-rest-e199.txt`](logs/selftest-rest-e199.txt) |
| **the audit of every branch the dry pass skips** (`desk/dryaudit_e199.py`, reading the committed logs) | **DRY-AUDIT-E199 37 of 37 COVERED (3 items named as not reachable at the desk)** | [`logs/dry-audit-e199.txt`](logs/dry-audit-e199.txt) |
| the dry listing, every step with stand-ins (`rb/list_steps_e199.sh`) | **13 steps, 0 exiting non-zero, 0 box calls** | [`logs/dry-listing-e199.txt`](logs/dry-listing-e199.txt) |
| `dmcmd_audit` (`preflight_e199.sh`), every file whose commands the day sends | **the plain chain GO with the stock table (11 send sites, every one a READ, no allow-list, no exception); the per-sensor chain GO with E144's table (17 sites), NO-GO with the stock table at command 74 alone** | [`logs/dmcmd-audit-e199.txt`](logs/dmcmd-audit-e199.txt) |
| the identity module's self-check (since fix-e199 also a runtime line naming device 0 refused), the quick set (every .py compiles, every .sh parses), the history check's names | **CHECKS-E199 13 of 13 PASS; the identity module's self-check PASS** | [`logs/checks-e199.txt`](logs/checks-e199.txt) |

## Builds on (the stock-take's rule for lanes, MAP section 3)

1. **Checked:** E199.md (the registration, `reg-e199`'s local commit re-made here); E192's kit as landed (`a6fe5c20`: its wrapper, gate, runbook,
   desk tests) and E192's card day (`card-e192`, Q179: RAN FULL, 9 of 9 passes, 59.52 card-minutes, no relaunch; its smoke gate, cap and
   rest worked as kitted); E191's kit with its dated note 2 (`2d0fe517`: aifoundry1 card 1, ET_DEVICES=1 for every device process, card 1's
   lock, THE IDENTITY GATE before the first launch and THE WATCH on every host, the reboot gate, the runtime line and the parser that no
   runtime print can split) and E191's two card-1 sessions (`1a4bc1e3`, `7156ac15`); E190's arm B on card 1 and its dated note 1 (its
   session-log form `build/e190/T<T0>-B/`); k6's runbook; the round's lessons (section 116: a host's stdout on a real box can carry runtime
   lines inside its own output; feed every parser the real committed bytes).
2. **Used, unchanged** (called, sourced, imported or run by path; sha256 in [`SHA256SUMS-e199-kit`](SHA256SUMS-e199-kit) and
   [`SHA256SUMS-e199-shared`](SHA256SUMS-e199-shared), E192's own in its lists): E192's `proposal/src/` (run_session.sh `9c0a6bb4...`,
   run_block.py `38106da5...`, stopwatch.py `fc19cb7e...`, the host and kernel sources, check_elf.py, arms.txt, reduce_intbits.py
   `715fddaa...`), E192's `desk/arm-table-e192.*` and `desk/loop_order_e192.py`, E192's `check_e192.py` (at E192's kit pin `ceb99e7c...`),
   E199's registered `order-e199-aifoundry1.txt`, `prefilter_e199.py`, `score_e199.py`; **E191's identity module** `e191_ident.py`
   (`3fabb603...`, imported: config_identity, etwho_identity, etwho_unreadable, proc_nodes, sampler_identity, parse_ident, descendants);
   **k6's runbook driver** `rb_common.sh` (its prelude with aifoundry1's tree `~/nekko`, its guard `rb_guard_text` with aifoundry1's REBOOT
   GATE, its desk-path gate `rb_nopath`, its jobs, its exit codes) and v3.1's runner; E191's ours_live (copied into `rb/rb_e199.sh` as E191's
   `rb_e191.sh` appends it to k6's prelude); E191's look, reads and rest rule (ported, `rb/s05_look_e199.sh`, `rb/s09_a1_reads_e199.sh`,
   `rb/rest_rule_e199.sh`); Q136(w)'s `dmcmd_audit.py` with the stock table and E144's table; E89's `pvt_sample.py` (`c4e4aed5...`); E151's
   rail filter (through `prefilter_e199.py`); E178's login scrub; E78's heater's source (for the audit).
3. **Not used:** any number of a sealed forecast; card 0 (no command, node or lock of it anywhere in the day's chain); E183's desk-path gate
   (section 4: it refuses on a desk whose home holds an entry named as the box's tree, and aifoundry2's home holds `nekko`); a simulator.
4. **Tiers:** every file here is public tier and cites public pieces only.
5. **Readiness:** this kit gates nothing by itself: its verifier, a fix pass if needed, its land and a readiness check come first.

## 1. The session: E192's reference session as committed, card 1's

[`session_e199.sh`](session_e199.sh) is E192's wrapper made card 1's (E192's stays as landed). It runs E192's `run_session.sh`
**byte for byte at E192's registration's sha256**, with run_block.py and stopwatch.py, from E199's own root on the box, and adds only what
E199.md sections 3, 7 and 15 ask, each before the first launch or through the registered stop file. In order:

1. **refusals before anything** (exit 2, "no device opened"): the host's name `aifoundry1` by `hostname` and by Python's
   `socket.gethostname()` (the registered order is drawn on it); `USER` the login; E192's registration list at `dd0a8963...` and its six
   session files; E199's registration list at `4d05fe0a...` and its order file; the kit's list at the sha256 the runbook passes and its six
   session files (`session_e199.sh`, `gate_e199.py`, `ident_e199.py`, `ettelem_guard_e199.sh`, `preflight_e199.sh`, `drycheck_e199.py`); the
   shared list and its six files (E191's identity module at E191's kit pin); the host, the reader, the heater and the per-sensor sampler
   present; **the reader at E191's pin `8008f96f...`** (E157's, E164's, E172's, E190 arm B's and E191's reader on card 1); **THE SELECTION:
   the host, the reader and the heater each carry `ET_DEVICES`** (run_session.sh's own `grep -aqw` on a two-card host, made here first,
   so that run_session.sh never refuses after a card command was sent); the plain chain GO (`preflight_e199.sh`); **aifoundry1's two cards'
   nodes only, counted by name** (exactly `/dev/et0_ops /dev/et1_ops` and `/dev/et0_mgmt /dev/et1_mgmt`) and **card 1's lock file**
   `/run/lock/etsoc-shire1.lock` (never created); the window's last end at least the cap away;
2. **the free check** (exit 3, "no device opened"): `et-who --check` exit 0 (no holder on EITHER card: E191's look's rule; its holder
   lines counted by card, never named, in `etwho-before.txt`), no other user's device process, a probe of card 1's lock;
3. **THE FIRST CARD COMMAND: the start config read** (`flock -n` card 1's lock, `timeout 10`, `ettelem config` through
   [`ettelem_guard_e199.sh`](ettelem_guard_e199.sh): aifoundry1 and `ET_DEVICES=1` only, the one word `config`), its stderr kept, read by
   **THE IDENTITY GATE (a)** ([`ident_e199.py`](ident_e199.py) on E191's `e191_ident`): every `PCIe target` line names `/dev/et1_mgmt`,
   every `Physical device ID` reads 1, the JSON reads TDP 65 W, 65 C, 600 MHz and `minion_mv` in (450, 510) — the JSON read once
   aifoundry1's runtime lines (`Opening device <n>` with its newline, wherever it fell) are dropped. One more read, 3 s later, only when no
   config came back at all (E191's step-7 note: our own live collector can hold the management node for a moment). Failing: "stopped before
   any pass completed: the identity gate (a)", exit 16, no launch; it is a session (a card command was sent) and the rest rule counts it;
4. **the per-sensor probe** (`flock -n` card 1's lock, `timeout 10`, `pvt_sample.py --probe`, its card read from `ET_DEVICES=1`): SAMPLER=pvt
   when the per-sensor chain is GO and every probe tick answers with 34 sensors; else the plain sampler (E192.md section 4's fallback);
   the go may name the plain sampler (`E199_SAMPLER=ettelem`: no probe);
5. **THE KIT'S GATE** ([`gate_e199.py`](gate_e199.py), section 2) beside E192's `run_session.sh`, which runs with `ET_DEVICES=1` exported,
   `LOCK=/run/lock/etsoc-shire1.lock`, `H`, `ETTELEM`, `HEATER`, `SAMPLER`, `PVT_SAMPLE`, `GAP=30`, `TARGET=58`, `PREHEAT=59`; a gate that
   dies mid-session is a STOP; a signal to the wrapper writes STOP and waits; **`run/SESSION_DONE` written by the wrapper when
   run_session.sh exits before its EXIT trap** (E192's fix);
6. **the end config read** (its stderr kept; recorded, not a gate), the kits' session log `build/e199/T<T0>/session.log` ("session start",
   "identity (a): ...", "identity (b): ...", "passes complete: k of 9", "session end (T0 <T0>)"), **MANIFEST.sha256 last**, then `wrapper.rc`.

`--dry` runs the same refusals, then the reference session's DRY mode, read by [`drycheck_e199.py`](drycheck_e199.py): 328 device calls in
the order `order-e199-aifoundry1.txt` writes out, 20 marked idles, 8 lock releases; every line DRY, its folder `-dry`.

**Where it runs on aifoundry1.** k6's tree there is `~/nekko` (no git). E199's root is `~/nekko/build/claims-v3/aifoundry1-c1/e199/`
(lib.sh's card-1 data root, a folder of ours): the synced files at their repository paths and the build (`build/intbits`); the sessions in
`~/nekko/build/e199/`. The box's tools: the reader `~/nekko/build/ettelem/ettelem`, E78's heater `~/nekko/build/sparsity/host/sparsity_host`
(lib.sh's HEATER on aifoundry1; E157 ran it as E78's heater on card 1 on 3 Nov 2026 at sha256 `e0fbecce...`, reported beside today's).

**No private /dev on the box** (the lane's question, answered at the desk). A bubblewrap `/dev` holding only card 1's nodes would hide
card 0 from the session, but `et-who` reads the holders through its privileged helper, and bubblewrap always sets the
no-new-privileges flag: measured on aifoundry2 (the lab's same et-who), `et-who --check` inside the round's sandbox exits 2 (the helper
refuses to run under that flag), so every holder check of run_session.sh would fail and the session would refuse. Card 0 is kept
out by the selection instead (ET_DEVICES=1 in every process, the binaries' selection checked, card 1's lock), and watched: THE IDENTITY
GATE (a) and (b) and THE WATCH stop a session that names or holds card 0. The private `/dev` is the desk's (every desk test).

## 2. The kit's gate (`gate_e199.py`): E192's two stops and card 1's three

It opens no device and sends no command; it reads the session's files, et-who's answer and `/proc` of the session's own processes, and acts
only through `OUT/STOP` (run_block.py checks it before every device process; the host before every 0.4 s launch).

- **THE SMOKE GATE** (E192's, word for word in effect): each smoke run exit 0, at least 3 INTBITS lines, every line ok, `check_bad` 0, 1,024
  participants; the heater check's launch exit 0; the smoke's arms in order; and **each of the smoke's four device processes (the heater
  check and three runs) printed the device layer's identity block naming card 1** (every device process prints one; E192's committed
  stderr holds 706 blocks for 706 device processes). Else STOP before any pass.
- **THE CAP** (E192's): 65 card-minutes from the first card command (here the start config read); the next pass only if it can end inside
  it (D the longest measured pass + 60 s, else D0 400 s); 30 s before the cap, STOP.
- **CARD 1'S LIVE STOP LINES** (E199.md section 7): `board_w` at or above 65 W, or `temp_c.minshire[0]` at or above 70 C, on any sample.
  On card 1 the 65 W line acts before stopwatch's 80 W rule and before the smoke heater check's 70 W ceiling (the desk test's HC: a 66 W
  heater check stops at the 65 W line).
- **THE IDENTITY GATE (b)** (E191's dated note 1, item 3(b)): with the sampler running (its first sample written) and before the smoke's
  first launch, `et-who` (rc 0 and readable, else UNREADABLE), every holder line of our login on card 1, at least one on `/dev/et1_mgmt`,
  none on card 0, none of another login on either card, and the sampler's own open files holding `/dev/et1_mgmt` and nothing of card 0.
  Failing; not decided within 8 s of the first sample (the smoke's first launch comes at least 20 s after the sampler starts:
  run_session.sh's 10 s, then the smoke's 10 s idle); or decided only after a device process had started: STOP before any launch.
- **THE WATCH** (E191's item 3(c), from outside): every 0.1 s, the new text of `OUT/stderr.txt` (an identity block naming another card) and
  the open files and mappings of every process under the wrapper (a card 0 node, or card 0's lock file): STOP; the process in flight ends
  by its own budget, never killed.

## 3. Device commands (`dmcmd_audit` GO)

[`preflight_e199.sh`](preflight_e199.sh) runs `dmcmd_audit.py` with no `--allow` and no `--except` over the wrapper, the gate, the identity
modules, the guard, E192's run_session.sh, run_block.py and stopwatch.py, the host's source and E78's heater's source: **the plain chain GO
with the stock table** (every send site a READ: `ettelem config` and `ettelem sample`; the host and the heater open the ops node only). **The
per-sensor chain GO with E144's table** (command 74 group 0 READ) and NO-GO with the stock table at command 74 alone, as for E192. **At card
1's firmware build:** the table classifies et-platform `836a4ab` (BL2 0.22.0), "the version all four lab cards report since 27-31 Oct 2026";
card 1's running build is E82's read of record (2026-10-31 13:45:24 PDT), carried by continuity while aifoundry1 has not booted since: THE
REBOOT GATE (k6's guard at step 9; E199's look at step 4; aifoundry1 booted 2026-10-26 15:02:04, read today). A later boot stops E199 (16): a
firmware read compared with the record, under the owner's ruling of Sun 15 Nov 2026 15:07:01 PST, would then come first, by a dated
amendment (not kitted: not needed while the box has not rebooted). Never sent by any file of the day: a statistics reset, command 74's group
6, any set, any governor, TDP, threshold or clock move, any reset, power cycle, PCIe, driver, firmware or OTA work; nothing to card 0.

## 4. The runbook from aifoundry2, in E191's form (exit codes k6's: 0 done, 10 refused, 11 a login link, 12 no answer, 13 past a bound, 14 a call failed, 15 a holder 30 minutes, 16 a gate says stop, 17 call again)

Run from the lab clone with this day's `RB_OUT` (a new directory outside the repo), `RB_LOCK` and, for step 2, `RB_GITLOCK`. Every remote
call goes through k6's drivers unchanged (a 15 s probe; bounded reads, copies and waits; detached launches; THE LOGIN CHECK). **THE WINDOW:
G = the card lane's booking of aifoundry1 on its day; last start ceil(G+1:30), last end ceil(G+3:30), inside the Pacific day, the last start at
most the last end less 70 minutes** (E199.md section 10; after another session of ours on aifoundry1 that day, its end plus the rest).

| # | step | file | what |
|---|---|---|---|
| B | the booking | (the card lane's) `bash W/book.sh take aifoundry1 <lane>` | G is its time |
| | **THE ONE-LAB RULE** | `bash W/onelab.sh desk <lane>` | right before step 0 |
| 0 | (by hand) | | the load rule; E199's anchor lines; no E199 datum in any ref |
| H | the hold | `bash W/hold.sh add <lane>` | LAB's status 0 lines |
| 1 | the window | [`rb/s02_window_e199.sh`](rb/s02_window_e199.sh) `<day> <last start> <last end>` | FIRST; today's day only; RB_PLAN=e199 |
| 2 | the desk check | [`rb/s03_desk_e199.sh`](rb/s03_desk_e199.sh) | OUTSIDE the kit's list; never inside the lab-git lock; the four lists at their pins (E199's 17, E192's 30, E192's kit 35, E199's kit); the shared list; THE HISTORY CHECK ([`rb/check_history_e199.py`](rb/check_history_e199.py)); the two freeze lines, each on one line (line 2, the sealed card-1 forecast, printed); **THE SEALED CARD-1 NOTE** at `tools/claims-v3/sealed-card1/e199-freeze-lines.md` when it exists (tracked, clean, added after the registration and never edited: its sha256 printed as freeze lines); no E199 datum; the preflight; the desk tests' logs |
| | **THE ONE-LAB RULE** | `bash W/onelab.sh undesk <lane>` | right after step 2, and on every stop path before it |
| 4 | the look | [`rb/s05_look_e199.sh`](rb/s05_look_e199.sh) `[--wait]` | E191's: BOTH CARDS (et-who as counts by card; ps; our sessions and jobs), THE REBOOT GATE (booted before E82's read), the box login recorded |
| 3 | the post | (waived) | the owner's standing words of Sun 15 Nov 2026 10:22:36 PST; never a post |
| 5 | the sync | [`rb/s07_a1_sync_e199.sh`](rb/s07_a1_sync_e199.sh) | refused beside a session or job of ours; [`boxfiles-e199.txt`](boxfiles-e199.txt)'s 39 paths into E199's root; the box's copies at their pins |
| 6 | the build | [`rb/s08_a1_build_e199.sh`](rb/s08_a1_build_e199.sh) `start`, then `wait` while 17 | [`build_e199.sh`](build_e199.sh) (cmake with the box's /opt/et; check_elf "loops 16, bad 0"; E192's loop_order 16 of 16; the arm table byte for byte; ET_DEVICES in the host and /opt/et's device layer; the hashes beside E192's, reported); at most two starts a day; then [`boxcheck_e199.sh`](boxcheck_e199.sh) (aifoundry1, the four nodes and card 1's lock file, et-who answering, the reader at E191's pin, ET_DEVICES in the host, reader and heater, the heater's parser, the pins, today's build record, the plain chain GO) |
| 7 | the reads | [`rb/s09_a1_reads_e199.sh`](rb/s09_a1_reads_e199.sh) | **the rest rule first (refused before the rest opens: the config read is a card command)**, then E191's reads with ET_DEVICES=1 and card 1's lock through E199's guard, read by the identity gate (a)'s form; both cards free |
| 8 | the dry pass | [`rb/s10_a1_dry_e199.sh`](rb/s10_a1_dry_e199.sh) `start`, then `wait` | `session_e199.sh --dry` on the box: E199-DRY OK |
| 9- | (by hand) | | step 10's pattern (`ours_live 'session_e199.sh'`) against step 9's launch line: the same name |
| 9 | the session | [`rb/s11_a1_session_e199.sh`](rb/s11_a1_session_e199.sh) `FULL [--plain-sampler]` | k6's guard (no dry pass, no session of ours on aifoundry1, THE REBOOT GATE); THE REST RULE ([`rb/rest_rule_e199.sh`](rb/rest_rule_e199.sh): every session-log form of ours on aifoundry1, either card, every tree: E190 arm B's `T<T0>-B/`, E191's `T<T0>/`, E199's own); today's dry pass and build; then `session_e199.sh` detached |
| 10 | the wait | [`rb/s20_wait_e199.sh`](rb/s20_wait_e199.sh), again while 17 | the session found by E191's ours_live as `session_e199.sh` or `session_e199_v<n>.sh` (its own script; never a longer name, a grep or a dry pass); 0 ended; 16 stopped before any pass (still collected) |
| | **THE ONE-LAB RULE** | `bash W/onelab.sh collect <lane>` | right before step 11 |
| 11 | the collection | [`rb/s22_collect_e199.sh`](rb/s22_collect_e199.sh) | one read-only copy back; **COPY EXACT** ([`collect_e199.py`](collect_e199.py)); **k6's desk-path gate** (`rb_nopath`, E191's step-11 form) on the copy; the data directory (our box login masked; telemetry gzipped; the identity lines in `facts-e199.json`); the holder-line check; the desk-path gate again; E178's scrub; NO-DATUM |
| 12 | the data commit | (the card lane's) | `docs/reports/data/<day>-e199-intbits-aifoundry1-c1/`, README from [`rb/data-readme-form-e199.md`](rb/data-readme-form-e199.md), the public-text scan, `commit_lab.sh` |
| | **THE ONE-LAB RULE** | `bash W/onelab.sh uncollect <lane>` | right after the data commit's push, and on every stop path between collect and the push |
| 13 | after the data commit only | [`rb/s24_score_e199.sh`](rb/s24_score_e199.sh) `docs/reports/data/<day>-e199-intbits-aifoundry1-c1` | E151's rail filter (`prefilter_e199.py`), E192's reducer (`715fddaa...`), E192's section 7 checker (`check_e192.py`, unchanged at E192's kit pin) on card 1's data, **THE TRANSPORT SCORER** (`score_e199.py`: E199-T1, E199-T2, the families), the unfiltered reduction beside it |
| E | the end | (the card lane's) `bash W/hold.sh remove <lane>`; `bash W/book.sh release aifoundry1 <lane>` | on every stop path too |

The dry listing ([`rb/list_steps_e199.sh`](rb/list_steps_e199.sh)) prints every step's commands and remote scripts and calls nothing. Its
"run on the Intel" lines are k6's driver's unchanged wording; on the card day those calls run on aifoundry2.

**Why k6's desk-path gate and not E183's** (step 11): E183's gate (E192's step 11) refuses on a desk whose home holds an entry named as the
box's tree; k6's tree for aifoundry1 is `nekko`, and aifoundry2's home holds `~/nekko`, so it would refuse every E199 collection there.
E191's collections of Sun 15 Nov 2026 ran k6's `rb_nopath` on aifoundry2; E199's does the same.

*Re-run by fix-e199 on the final bytes, Mon 16 Nov 2026 PST, each in the round's CPU slot and its no-device sandbox, with THE QUIET
DESK FLAG absent: the real path 78 of 78 (02:08:53-02:30:49); the real bytes 11 of 11 (RB3 as above; RB6 now also reads card 1's real
config read carrying E170's real runtime line, `Opening device 0`, refused by that line alone); the real build 5 of 5; the runbook 21 of
21 (02:09:42-02:14:45; WN read RUN-GONE in 2 s); the rest rule 16 of 16; the dry audit, the dry listing, dmcmd_audit and the quick set
re-made with the kit's list. Beside them (desk checks of code by fix-e199, outputs not committed): verify-e199's mutant B1, the wait's
pattern widened to `session_e199*.sh`, now FAILS WN (RUN-RUNNING, 17, after 45 s; 20 of 21), and the three NOT RUN paths (a start at
a shimmed 23:30; the quiet-desk flag at the runbook test's start; the flag at the real-path wrapper) each exit 5 before any sandbox.*

## 5. The readings stated here before any datum (where E199.md leaves a choice to the kit)

1. **The session is E192's reference session as committed**; the kit's stops act before the first launch or through `OUT/STOP` only.
2. **The first card command is the start config read** (THE IDENTITY GATE (a)); the cap (65 card-minutes) and the card time count from it.
3. **One more config read** only when no config came back at all; a read that names another card, or reads another config, fails at once.
4. **THE IDENTITY GATE (b) is one et-who read**, as E191 ran it. Our own live collector on aifoundry1 reads both cards a few milliseconds
   a second; a read that catches it on card 0 fails the gate (a session ended before any launch). The duty cycle makes that rare (about
   0.5% a read: the verifier's estimate for E192 from the collector's documented cycle, not measured on aifoundry1).
5. **The smoke gate's card-1 condition** counts identity blocks in `stderr.txt` (one a device process; four in the smoke).
6. **Card 1's 65 W line binds before the heater check's 70 W ceiling** (both registered; the stricter acts first).
7. **A launch refused before anything opened** ("no device opened": exit 2, or 3 at the free check or at the config read's lock) sent no card
   command: not a session, skipped by every rest rule; whether it may be launched again that day is the go's to say (E192's G4 form).
8. **A session ended by the identity gate (a)** sent a card command: it is a session (the rest rule counts it), with no data.
9. **The sealed card-1 forecasts** (the round's CONTEXT section 122): E199's, posted by the model session at 01:28:51 PST Mon 16 Nov 2026
   before the land, is E199.md's freeze line 2 (registered by fix-e199): step 2 checks it on one line, as it checks freeze line 1, and
   prints it; the card lane's wait for it is over. A sha256 posted after the land enters only by a dated note at
   `tools/claims-v3/sealed-card1/e199-freeze-lines.md`, outside the pinned subtree, committed under the desk-commit rule before E199's
   card day; step 2 prints it as the later note's line; the history and no-datum checks accept it.
10. **The desk's own variables** (`E199_DESKTEST=1` with `E199_CAP_S`, `E199_D0_S`, `E199_PVT_SAMPLE`, `E199_PVT_SHA256`,
    `E199_READER_SHA256`, `E199_B_DEADLINE_S`; `RB_DESKTEST=1` with `E199_DESK_BUDGET_S`, `E199_SELECTION_REPORT_ONLY`) are refused or
    ignored without their flag; the card day sets none (a real ssh passes none).

## 6. The desk tests, and the audit of the branches the dry pass skips

**THE REAL-PATH DESK TEST** runs `session_e199.sh`'s real path case by case against the stand-ins (each in its tool's own output form: the
reader's `config` prints aifoundry1's runtime line then the JSON and the identity block on stderr; the sampler holds `/dev/et1_mgmt`; the
host prints the runtime line, the identity block and INTBITS lines while holding `/dev/et1_ops`; et-who lists every open stand-in node as
et-holders does). Its cases: 0 (the sandbox; the box copy's preflight and identity self-check; the guard refusing a missing ET_DEVICES,
ET_DEVICES=0 and any word but config), D (the dry path), **P (the real path: the identity gates, the smoke, two passes, the stop by hand,
75 host processes each under card 1's lock with ET_DEVICES=1, every launch a record with the runtime line first, the end read, E199's
pipeline reading the files, the rest rule refusing right after)**, FE, H1, H1b, H2, H3, IA1-IA5, IB1-IB3, W1-W3, LS1, LS2, S3, HC, G1,
G2a, G4, T, RT1, B7, R1-R8, N1-N5, Z. [`desk/dryaudit_e199.py`](desk/dryaudit_e199.py) names every branch the dry pass skips (the
wrapper's, the gate's, run_session.sh's, run_block.py's, stopwatch.py's, the identity module's, steps 7, 9 and 10's) with the cases that ran
it, reads their PASS lines in the committed logs, and lists apart what no desk case reaches (stopwatch's 80 W rule, which card 1's 65 W
line pre-empts; a SIGKILLed run_session.sh; the box's own tools).

**THE REAL-BYTES TEST**, **the real build**, **the rest rule** and **the runbook** are described in their files' headers; their results are
in the table above.

**THE QUIET DESK FLAG in the desk tests** (since fix-e199, verify-e199 F7): the real-path and runbook tests take the flag's path
(`E199_QUIET_FLAG`) and end NOT RUN (exit 5) when it exists at the start or before any case: they never wait inside their sandbox, where a
paused run counted as a sandbox in flight and held a card lane's pre-launch check. A caller waits for the flag, if at all, outside any
sandbox. The runbook test also refuses to start from 23:20 Pacific (F6): its desk window is today's last minutes. Its WN case (F9) now
runs a decoy `session_e1990.sh` that outlives the wait's 40 s bound and asks RUN-GONE within one loop (under 17 s), so a pattern that
matched the decoy would read 17 after 40 s: the pattern matches the real name only.

## 7. Card-minutes and the cap (registered; unchanged)

About 60 card-minutes (E199.md section 8 since fix-e199: E192's own session took 59.52, measured on aifoundry3, against its estimate of 52;
plan the booking and the rests on 60-65; the cap may cut the last pass), **cap 65** from the first card command, enforced by the gate,
never by killing a device process. The 40-minute rests on aifoundry1, either card (the rest rule, steps 7 and 9). One session of ours on
aifoundry1 at a time (k6's guard, the look, the booking).

## 8. Files, the lists and step 2

| file | what |
|---|---|
| `session_e199.sh`, `gate_e199.py`, `ident_e199.py`, `ettelem_guard_e199.sh`, `preflight_e199.sh`, `drycheck_e199.py` | the session's wrapper, the kit's gate, the identity module, the config read's guard, the device-command preflight, the dry pass's reader (box) |
| `build_e199.sh`, `boxcheck_e199.sh`, `boxfiles-e199.txt` | the build on the box, the box's tools and pins, the sync list (box) |
| `collect_e199.py` | the collection's desk half |
| `rb/rb_e199.sh`, `rb/s02...s24_*_e199.sh`, `rb/rest_rule_e199.sh`, `rb/check_history_e199.py`, `rb/list_steps_e199.sh`, `rb/data-readme-form-e199.md` | the runbook |
| `desk/*`, `rb/selftest_*_e199.sh` | the desk tests |
| `KIT.md`, `CARD-LANE-BRIEF.md` | this file; the card lane's brief |
| `SHA256SUMS-e199-kit` | every kit file but itself and step 2 |
| `SHA256SUMS-e199-shared` | the six shared files the box receives |
| `logs/*.txt` | the desk tests' logs |

**Step 2 (`rb/s03_desk_e199.sh`) is outside `SHA256SUMS-e199-kit`**: its own sha256 and the list's are in the land file's anchor lines.

## 9. The data commit's README

The card lane fills [`rb/data-readme-form-e199.md`](rb/data-readme-form-e199.md): results first (passes, the sampler, the identity
lines, card-minutes, any STOP, the smoke gate, the peaks), registered against happened, departures dated, the day's records. **No forecast
number of any sealed forecast and no score in it**: step 13's outputs are committed by a records lane after the data commit.

## 10. What the desk cannot show

1. **The real card**: the stand-ins answer in the tools' forms, never card 1's; its rate, power, die, approach timing and per-sensor codes
   are unknown until the day (E199.md section 13).
2. **The box's own tools**: the reader's and the heater's selection (`ET_DEVICES` in their bytes), the heater's parser, `pvt_sample.py
   --probe` on card 1's running build, aifoundry1's device layer, its `python3`: read by steps 6-9 on the day.
3. **This desk's /opt/et carries no ET_DEVICES** (E191's real-build log; the real-build test's RB1): the build's selection check cannot pass
   here; the desk's builds report it (`E199_SELECTION_REPORT_ONLY`, desk only), and aifoundry1's build must pass it (E191's card-1 builds did).
4. **The kernel built on aifoundry1** may differ as a file from E192's; check_elf and loop_order are the gate, the hashes reported.
5. **The live collector** on aifoundry1 (section 5 item 4).
6. **A runtime line inside an INTBITS line**: the intbits host prints nothing before it opens the card, so aifoundry1's runtime line comes
   first, on its own line (read on the real path and on the real bytes); should one ever fall inside a line, the block raises (no wrong
   record) or that one launch line is lost (the REAL-BYTES test's RB3 counts both). Not seen in any committed card-1 output.

## 11. Labels

Everything here is **registered** (E199.md, E192.md, quoted) or a **desk check of code** (this kit's tests). The look at aifoundry1 and
the et-who-in-a-sandbox reading on aifoundry2 are **measured** desk facts. Nothing is forecast, blind, held out or post hoc.

## 12. The registration's kit requirements, each met or not

| requirement (E199.md section 15; reg-e199's gaps for the kit) | how | tested by |
|---|---|---|
| E192's session as committed with ET_DEVICES=1 and card 1's lock | `session_e199.sh` (section 1) | real path P (P2-P17), N3-N5 |
| the runbook in E191's form: the window; step 2 pinning E199's and E192's lists; the look on both cards; the sync to a folder of ours; the build with check_elf, loop_order and the --list against E192's table, the kernel's hashes beside E192's; k6's reads with ET_DEVICES=1, the config read after the rest opens; the dry pass; the detached launch; the wait on the real script's name; the collection; the data README; the pipeline and the scorer with check_e192.py after the data commit | section 4 | the runbook test (A-Z), the dry listing, the real build |
| THE IDENTITY GATE (a) and (b) before the first launch; the hostname check; card 1's live stop lines; the reboot gate | sections 1-2; k6's guard and the look | IA1-IA5, IB1-IB3, P2, P6, R1, LS1, LS2, HC, RG |
| `dmcmd_audit` GO for the session's chain at card 1's firmware build, the sampler's choice included | section 3 | `logs/dmcmd-audit-e199.txt` |
| a real-path desk test (stand-ins for every device tool, et-who, the lock, the sampler and the host, in a private /dev, through the smoke, the stop path and at least two passes) with an audit of every branch the dry pass skips | section 6 | the real-path log; the dry audit |
| the real-bytes test of every reader of a host's standard output on aifoundry1's committed bytes and on E192's committed aifoundry3 output | the real-bytes test | RB0-RB7 |
| the identity gate tested both ways (card 1's forms pass; card 0's, a missing ET_DEVICES and a second card's holder refused) | ident_e199's self-check; the real path; the real bytes | 0e-0g, P2, P6, IA1, IA2, IB1-IB3, W1-W3, H1b, N3, RB5, RB6 |
| THE ONE-LAB RULE helper around steps 0, H and 2, and around the collection to the data commit's push | section 4's table; CARD-LANE-BRIEF.md | the dry listing prints them |
| run_block.py's INTBITS reader on aifoundry1's committed bytes | the real-bytes test | RB0-RB4, RT1, P12 |
| the per-sensor sampler's ET_DEVICES check | ET_DEVICES=1 exported (pvt_sample.py's `--card` default); identity (b) reads the sampler's own open nodes | P3, P6, IB3 |
| card 1's build, loop checks and kernel .text beside E192's | `build_e199.sh` | the real build (RB1, RB2); the runbook's B |
| the reboot gate | k6's guard; E199's look | the runbook's RG |
| a firmware read after a later boot of aifoundry1 | **NOT KITTED**: aifoundry1 has not booted since 2026-10-26; a later boot stops E199 (16) until a dated amendment adds the read | |

## 13. Fixes before the land (Mon 16 Nov 2026, Q191 lane `fix-e199`: verify-e199's findings)

verify-e199 read the registration and this kit at their land patches: HOLDS WITH FIXES, three minor findings and six nits, none
blocking the land or making the card day unsafe. The registration's answers are E199.md section 17; the kit's:

| # | finding | done in the kit |
|---|---|---|
| F1, F3, F4 | the registration's (the forecast's rule words; decided at 4 passes; the card-time estimate) | every pin on the fixed registration moved (below); the card time here and in the brief and the README form |
| F2 | step 2 printed sealed lines only from the later note | step 2 checks E199.md's freeze line 2 (`1c5d8fa3...`) on one line, as it checks line 1, and prints it beside the later note's line; the runbook test's P1 and SN1 read both |
| F5 | the identity gate (a) dropped `Opening device <n>` lines without reading n | a runtime line naming another device than 1 is refused (`ident_e199.py`); its self-check refuses `Opening device 0` with card 1's JSON and block; the real-bytes test's RB6 feeds card 1's real read with E170's real runtime line (`Opening device 0`) and reads it refused by that line alone |
| F6 | the runbook test read 11 of 21 when started at 23:57 | it refuses to start from 23:20 Pacific: NOT RUN (exit 5), never a FAIL |
| F7 | a real-path run paused by the quiet-desk flag held card-e194's pre-launch check for 9 minutes | the real-path and runbook tests end NOT RUN when the flag exists at the start or before any case; no test waits inside its sandbox (section 6) |
| F8 | the brief's step 1 row named no stop path; `onelab.sh` has no staleness check | step 1's row names `onelab.sh undesk`, then E (the hold removed, the booking released); a stale flag of a killed lane is the orchestrator's to clear (the round's helper, not this kit's) |
| F9 | the WN case could not see an over-wide wait pattern | the decoy outlives the wait's 40 s bound and RUN-GONE must come within one loop (section 6) |

**The re-pin list (verify-e199's map, every item done):** the registration subtree `070b4e2d...` in `rb/rb_e199.sh` (E199_REG_SUBTREE),
`rb/check_history_e199.py` (REG_SUBTREE) and step 2's comment; the registration list `4d05fe0a...` (17) in `session_e199.sh` (REG199_SHA),
`rb/rb_e199.sh` (E199_REG_LIST_SHA), step 2 (REGPIN), `boxcheck_e199.sh` and `boxfiles-e199.txt`; freeze line 1 `deb4a7d1...` in step 2
(F1) and E199.md; then every desk test re-run and its log re-made, `SHA256SUMS-e199-kit` and step 2's KITPIN, and the land file's anchor
lines. `selftest-e199.json` (the registration's) holds the new forecast's sha256.

SPDX-License-Identifier: Apache-2.0
