# E192's run kit: the proposal's reference session run as committed on aifoundry3 card 0, the kit's gates through its stop file, the runbook from aifoundry2 in E189's form, a real-path desk test of the branches the dry pass skips (Q176; kitted, fixed before the land, not run)

*Sat 14 Nov 2026 (week 46), PST, on aifoundry2, desk only (Q176, lane `kit-e192`), on the registration's local commit `88c02bd2`
(E192.md, its tools/claims-v3/e192 subtree `c78351f9...`, `SHA256SUMS-e192-registration` `dd0a8963...`, 30 entries). **Fixed in place the
same evening, before the land, by lane `fix-e192`**, answering the verifier's findings (verify-e192: HOLDS WITH FIXES), on the same
registration re-applied unchanged on GitHub main `eee9fb7e` (the same subtree `c78351f9...`): what changed and why is section 12; every
log in `logs/` is that lane's re-run. No card was claimed or
opened (aifoundry2 has a card of its own: every desk run of a built host, a session, a stand-in box or anything that could open a device ran
inside the round's no-device sandbox, and each desk test makes its own sandbox inside it), no device command was sent, no lab box was
reached, nothing was posted. New files only, all under `tools/claims-v3/e192/`; E192.md, `proposal/` (the model session's request and
source, byte for byte) and `desk/` stay as committed. No E192 datum exists. **Nothing here changes an arm, a value, the order, a window, a
threshold, a stop, the reduction, the card time or the cap.** Where E192.md leaves a reading to the kit, it is stated in section 5 before
any datum. Python is `/usr/bin/python3` 3.12.3 (numpy 1.26.4) at the desk; the box's `python3` runs the reference session, as the proposal
wrote it.*

## Results first (desk checks of code; nothing is measured, nothing is forecast)

| check | result | log |
|---|---|---|
| **THE REAL-PATH DESK TEST**: `session_e192.sh`'s real path (DRY unset) against stand-ins for the sampler, the per-sensor sampler, E78's heater, the host, et-who, ps and the card lock, on a stand-in aifoundry3 tree, in a sandbox with two regular files named `/dev/et0_ops` and `/dev/et0_mgmt`: the dry path; the full real path through the smoke and two passes stopped by hand in the gap; the fallbacks; the holders at the start and between passes; the card lock busy; the three live stops; the heater check; the smoke gate and its negative control; the cap three ways; a dead gate; a signal; eight refusals; and fix-e192's cases (section 12): the node count with two cards, none and no `et0_mgmt` (nested sandboxes); `run_session.sh`'s own refusals run alone; its four exits before its EXIT trap after the probe (the wrapper's SESSION_DONE); the probe's lock taken; the per-sensor sampler off its pin and its chain NO-GO; the smoke gate's four other conditions and its arm order; the heater check with no board reading; a holder right after the sampler; a silent sampler; a crash in a block; a stop inside pass 0; another user's process between passes; no deadline | **DESKTEST-REALPATH-E192 108 of 108 PASS** (fix-e192's run; kit-e192's last run before the fix: 67 of 67) | [`logs/desktest-realpath-e192.txt`](logs/desktest-realpath-e192.txt) |
| **the runbook** (a stand-in ssh and rsync, a stand-in box; the box's build REAL: cmake with this desk's `/opt/et`, `check_elf.py`, the built host's `--list`): the window rule, the lab-git lock, step 2 at every pin, the history check and its shadows, an E192 datum in a ref, the sync, the build and its count, the login check, a hang, a cut wait, the dry pass, the rest rule through step 9, the real `session_e192.sh` launched and waited on (the name pattern on the real script), a decoy name, the collection, the reducer and the checker on the committed data, a changed box file | **SELFTEST-RB-E192 18 of 18 PASS** (fix-e192's run; RB_LOCK a copy of the round's lock file of checks: the login check appends one line to the copy, the rest kept; RB_GITLOCK a scratch lock); kit-e192's first run found **two defects of this kit's runbook that a dry listing cannot see** (section 6) | [`logs/selftest-rb-e192.txt`](logs/selftest-rb-e192.txt) |
| **the rest rule**: E183's, E189's, E190's and E192's forms, a cut session, a dry pass, a refusal, the log `session_e192.sh` wrote in the real-path test, and (fix-e192) energy.sh's folders in two trees and a dry one, and the wrapper's real logs of an early exit after the probe (the case B7: counted) and of a refusal at the node count (the case W1: skipped) | **SELFTEST-REST-E192 18 of 18 PASS** | [`logs/selftest-rest-e192.txt`](logs/selftest-rest-e192.txt) |
| the dry listing, every step with stand-ins | 13 steps, 0 exiting non-zero, **0 box calls** | [`logs/dry-listing-e192.txt`](logs/dry-listing-e192.txt) |
| `dmcmd_audit`, every file whose commands the day sends | **the plain chain GO** with the stock table (17 send sites, every one a READ, no allow-list, no exception); the per-sensor chain GO with E144's table (23 sites) and NO-GO with the stock table at command 74 alone (section 3) | [`logs/dmcmd-audit-e192.txt`](logs/dmcmd-audit-e192.txt) |
| the dry pass's reader, the section 7 checker, the history check | `drycheck_e192.py` E192-DRY OK on the reference session's DRY mode, two negative controls FAIL; `check_e192.py` on the registration's synthetic session (injected test values): 1 PASS, 2 PASS, 3 EQUAL, 4 PASS, 5 PASS, 6 PASS, 7 and 8 REPORTED, and with injected faults 1, 2 and 4 FAIL; the history check's names and NO-DATUM OK | [`logs/checks-e192.txt`](logs/checks-e192.txt) |

## Builds on (the stock-take's rule for lanes, MAP section 3)

1. **Checked:** E192.md (the registration, both freeze lines, `88c02bd2`); E189's kit (`b42dc95c`: the runbook's form, its rest rule, its
   history check, its runbook desk test); E183's kit notes 5 and 6 (`9ae55d39`, `977c63d1`: the desk on aifoundry2, the desk-path gate for a
   desk whose home has the box's shape, the real-path desk test and the dry-path audit, step 10's name-pattern defect); E190's step-10
   defect (round log sections 107 and 109: a gate that read every identity-passing session as stopped); the round log's section 104 lesson.
2. **Used, unchanged** (called, sourced or run by path; sha256 in [`SHA256SUMS-e192-kit`](SHA256SUMS-e192-kit) and
   [`SHA256SUMS-e192-shared`](SHA256SUMS-e192-shared)): the proposal's `run_session.sh`, `run_block.py`, `stopwatch.py`, `arms.txt`,
   `check_elf.py`, `reduce_intbits.py` and the host and kernel sources (the registration's list); **k6's runbook drivers**
   (`tools/claims-v3/q141k-runbook/k6/rb_common.sh`, its look `s05_look_k6.sh` and reads `s09_a3_reads_k6.sh`; v3.1's `rb_run.py` and
   `nopath_q142s.py`); **E183's desk-path gate** (`tools/claims-v3/e183/rb/nopath_desk_e183.sh`, `nopath_spell_e183.py`); **E178's login
   scrub** (`scrub_tree_e178.py`); **Q136(w)'s `dmcmd_audit.py`** with the stock table and **E144's table** (`e144/dmcmd_table_e144.json`);
   **E89's per-sensor sampler** (`e89/pvt_sample.py`); **E128's guard** (k6's step 7 reads the config through it); **E78's heater's source**
   (`workloads/sparsity/host/main.cpp`, for the audit).
3. **Not used:** any forecast number (the forecasts are sealed: E192.md section 0); any other card; anything of the archive or a private
   page; a refit; a simulator (none runs on the lab box).
4. **Tiers:** every file here is public tier and cites public pieces only; no NDA-tier check enters this kit.
5. **Readiness:** this kit gates nothing by itself: its verifier (verify-e192: HOLDS WITH FIXES) and its fix pass (fix-e192, section 12)
   came before the land; a readiness check comes next, then the owner's go.

## 1. The session: the proposal's reference session, as committed, driven with the box's tools

**Which, and why.** E192 runs the proposal's own `run_session.sh` (with `run_block.py` and `stopwatch.py`) **byte for byte at the
registration's sha256**, not a port into a lab block library. The proposal says its lab kit "is meant to run the same arms in the same order"
(BUILD.md); running the registered code unchanged guarantees every arm, value, order (the `random.Random("<hostname>|<pass>")` draw), window,
approach, burn-in, anchor, idle, stop and the 30 s gap with its holder check, with nothing re-implemented. The kit adds only what E192.md
section 17.2 asks of it, and it acts on the session only through the registered stop file `OUT/STOP` (E192.md 17.2: "the kit may add stops
that end a session early; it never changes an arm, a value, the order, a window, a threshold or the reduction").

**The wrapper** ([`session_e192.sh`](session_e192.sh)), started detached by step 9, does in order:
1. **refusals before anything** (exit 2, "no device opened"): the host's name is `aifoundry3` by `hostname` and by Python's
   `socket.gethostname()` (the registered order is drawn on it); `USER` is the login (E183 kit note 6's carried rule); no desk-test variable
   without `E192_DESKTEST=1`; the registration's list at `dd0a8963...` and its seven session files (`run_session.sh`, `run_block.py`,
   `stopwatch.py`, `arms.txt`, `check_elf.py`, `desk/arm-table-e192.jsonl`, `desk/order-e192-aifoundry3.txt`) at their sha256; the kit's list at
   the sha256 the runbook passes and its four session files (`session_e192.sh`, `gate_e192.py`, `preflight_e192.sh`, `drycheck_e192.py`); the
   host, the sampler and the heater present; `preflight_e192.sh`'s plain chain GO; **one card's nodes only, counted by name: exactly
   `/dev/et0_ops` and `/dev/et0_mgmt`** (E192.md section 3: "before opening anything the host counts the card nodes"; added by fix-e192:
   the probe had been the first card command before any node count, verify-e192's finding 2); the window's last end at least the cap away;
2. **the free check** (exit 3, "the card is not free ... no device opened"): `et-who --check` exit 0, no other user's device process, a probe
   of the existing card lock (read-only, never created) — the reference session makes the same check again before its sampler;
3. **the first card command, the per-sensor probe** (section 3): `flock -n <lock> timeout 10 python3 -B pvt_sample.py --probe` (three READ
   ticks); the session's card time and its cap count from it;
4. **the kit's gate** ([`gate_e192.py`](gate_e192.py)) beside the session (section 2), and the reference session itself:
   `run_session.sh build/e192/T<T0>/run 9` with `H`, `ETTELEM`, `HEATER`, `SAMPLER`, `PVT_SAMPLE`, `GAP=30`, `TARGET=58`, `PREHEAT=59`,
   `LOCK=/run/lock/etsoc-shire0.lock` set and `ET_DEVICES` unset; a gate watcher that dies while the session runs is a stop (the wrapper
   writes STOP: no gate, no session); a signal to the wrapper writes STOP and waits for the session's own end (never a kill); **when
   `run_session.sh` has exited without its own end marker** (it writes `run/SESSION_DONE` only in its EXIT trap, set after its refusals and
   its free check), **the wrapper writes `run/SESSION_DONE` itself**, one JSON line naming the wrapper and that exit (the reference's own
   marker is an empty file), and logs it, so the gate ends at once instead of at its end-stop (fix-e192, verify-e192's finding 1: about
   64 minutes and a false cap STOP before the fix);
5. **the kits' session log** `build/e192/T<T0>/session.log` ("session start", "sampler: ...", "passes complete: k of 9", "session end (T0
   <T0>)": every rest rule of ours reads it), then **MANIFEST.sha256 last** (every file under the session's directory), then `wrapper.rc`.

`--dry` runs the same refusals, then the reference session's own DRY mode (every device call printed, nothing opened: no et-who, no lock, no
probe, no sampler, no gate), read by [`drycheck_e192.py`](drycheck_e192.py): **328 device calls** (327 host runs and the smoke's heater
check), each under `timeout 10` with `--stop-file`, the smoke's three runs at 2 s, passes 0-8 at 36 runs each in exactly the order
`desk/order-e192-aifoundry3.txt` writes out, 20 marked idles and 8 lock releases with their gap. Its files go to `build/e192/T<T0>-dry/` and
every line is marked DRY, so every rest rule skips it.

**The box's tools** (found in the repository; none is built or changed by this kit):

| tool | where on aifoundry3 (k6's tree `~/aifoundry`) | which kit built it | its device commands |
|---|---|---|---|
| the sampler | `build/ettelem/ettelem` | the lab's `tools/ettelem/ettelem.cpp`, lib.sh's `ETTELEM` | the audit table's reviewed variant `ettelem` (by its build directory): `sample` sends six READs; no `--reset-ms` is ever passed |
| **E78's heater** | `build/sparsity/host/sparsity_host` | `workloads/sparsity` (the sparsity workload's build on aifoundry3, 18 Sep 2026, `docs/reports/data/2026-09-18-sparsity-aifoundry3/`; the runtime log-level fix of 25 Sep, `27dce7f0`, "in every host program"); lib.sh's `HEATER` on aifoundry3; E78's and E86-E106's blocks used it | `createPcieDeviceLayer(true, false)`: the ops node only, no device-management command (its source is in the audit, section 3); `--stop-file` is one of its options (main.cpp line 980) |
| **E89's per-sensor sampler** | synced by this kit into E192's root: `build/claims-v3/aifoundry3/e192/tools/claims-v3/e89/pvt_sample.py` | E89 (Q130), `tools/claims-v3/e89/pvt_sample.py` (`ac95a217`), the audit tables' reviewed raw client by sha256 `c4e4aed5...` | six READs a tick (33, 60, 27, 74 group 0, 32, 53); refuses every group of command 74 but 0 and 4; `--probe`: three ticks and a verdict |
| et-who | `/usr/local/bin/et-who` (`--check`: 0 free, 1 held, 2 failed; on all three hosts since 28 Sep, AGENT.md) | the lab's host setup | none: it reads /proc |

The heater's binary on aifoundry3 is not hashed in the repository (`tools/claims-v3/BUILD-HASHES-2026-10-27.md` hashes aifoundry1's), so step
6 reads it **by its behaviour**: its option parser, given the registered heater arguments, `--stop-file` and an unknown option, must stop at
the unknown option alone (exit 2) — every registered option is one it knows — and its sha256 on the box is recorded. Nothing is grepped from
any binary.

**Where the card day builds** (fix-e192, verify-e192's nit 9). The proposal's request.md section 8 says "Build in a folder of our own
(`~/claude/work/ee-1113-x01-intbits/`), never in the lab session's trees": that is the model session's rule for its own builds, in its relay
folder on aifoundry2, which the lab only reads. The lab's card-day build is the lab's own, by step 6 on aifoundry3, in **E192's own root**
`build/claims-v3/aifoundry3/e192/` (the build in its `build/intbits`), a folder no other run writes; the kit builds nothing in the relay
folder and writes nothing of another run's on the box (its sessions go to `build/e192/`).

## 2. The kit's gate (`gate_e192.py`): two stops, nothing else

- **THE SMOKE GATE** (E192.md 17.2: "a smoke gate that reads the smoke's INTBITS lines (the reference run_block.py reports a failed smoke run
  but does not stop on it)"). When the smoke block has recorded its three runs, each must have its device process's exit 0, at least 3
  INTBITS lines (2 s of 0.4 s launches), and on every line `"ok": true`, `"check_bad": 0` and 1,024 participants (the reducer's run gates
  and registered check 1's count); and the smoke's heater launch must itself have exited 0 (the reference reads its board level but not its
  exit: a heater that failed would pass the 70 W check on idle readings and leave every approach unable to preheat; found by this kit's first
  real-path run, section 6). Else STOP in the smoke's 10 s 'after' idle: no pass runs ("no pass: no data", E192.md section 11).
- **THE CAP** (E192.md section 10: 65 card-minutes from the first card command; "no pass starts that could end after it"; "never by killing a
  device process"). At each block's end, the next pass may start only if now + (the 30 s gap, for passes after 0) + D fits inside the cap,
  where D is the longest measured pass so far plus 60 s, or D0 = 400 s before any pass was measured (the proposal's 5.6 minutes a pass and
  about a minute). Else STOP (the reference session checks it after the gap, or pass 0 in its first idle). **30 s before the cap**, if the
  session still runs, STOP: the launch in flight finishes and the block ends at its next check.
- It opens nothing, sends nothing, and ends at the session's end (`run/SESSION_DONE`: the reference's own, or the wrapper's when
  `run_session.sh` exited before its EXIT trap, section 1) or at any STOP (its own or another's).

## 3. Device commands, and the sampler's choice

[`preflight_e192.sh`](preflight_e192.sh) runs `dmcmd_audit.py` with **no `--allow` and no `--except`** over every file whose commands the day
sends: the wrapper and the gate, `run_session.sh`, `run_block.py`, `stopwatch.py`, the host's source, E78's heater's source and E128's guard
(k6's step 7 config read). **The plain chain is GO with the stock table** (17 send sites: `ettelem sample` and `ettelem config`, every one a
READ; the host and the heater open the ops node only and send no management command).

**The per-sensor sampler.** E192.md section 4 prefers `SAMPLER=pvt` "where it answers on this card and the kit's audit reads its command as a
READ"; the plain sampler is the registered fallback. The stock table (`dmcmd_table.json`, et-platform `836a4ab`) leaves command 74
(`DM_CMD_GET_ASIC_PVT_SAMPLES`) **UNCLASSIFIED**: read with it, the per-sensor chain is NO-GO at that one command and nowhere else. **E144's
table** (`tools/claims-v3/e144/dmcmd_table_e144.json`, `13799873`: the stock table with that one entry changed) classifies command 74 group 0
**READ**, traced from the held patch source to the same PVT register reads `GET_MODULE_CURRENT_TEMPERATURE` makes, with the residual its
README states (aifoundry3's running build is not hashed; since 31 Oct its group 0 returns raw codes); E144, E176 and E181 ran `pvt_sample.py`
on this card under it. **The kit's reading:** the session takes `SAMPLER=pvt` only when (a) the per-sensor chain is GO with E144's table,
(b) `pvt_sample.py` on the box is at the reviewed sha256 `c4e4aed5...`, and (c) its probe answers with 34 sensors on every tick; else the
plain sampler, recorded in the session log and the data ("sampler: ettelem (the fallback: ...)"). **His go may name the plain sampler**
(step 9 `--plain-sampler`, `E192_SAMPLER=ettelem`: no probe is sent) if he reads only the stock table as the audit. **The go names the audit
table it accepts for command 74** (fix-e192, verify-e192's info 10, which accepts this reading): E144's, the default, under which the
session's first card command is the per-sensor probe and command 74 group 0 is sent; or the stock table alone, with `--plain-sampler`,
under which command 74 is never sent. The reducer reads the 34
codes when more than 90% of the samples carry them, else the whole-degree reading (registered; the registration's synthetic check ran both).

Never sent, by any file of the day: a statistics reset (`--reset-ms`, `--reset-once-file`), command 74's group 6 (the latch reset), the
firmware-revisions query, any `DM_CMD_SET_*`, any governor, TDP, threshold or clock set, any reset, power cycle, PCIe, driver, firmware or OTA
work, `dev_mngt_service`.

## 4. The runbook from aifoundry2 (each step a script; exit codes k6's: 0 done, 10 refused, 11 a login link, 12 no answer, 13 past a bound, 14 a call failed, 15 a holder 30 minutes, 16 a gate says stop, 17 call again)

Run from the lab clone, each with this day's `RB_OUT` (a new directory outside the repo, E192's own), `RB_LOCK` (the file a login check is
appended to) and, for step 2, `RB_GITLOCK` (the lab-git lock). Every remote call goes through k6's drivers, unchanged: a 15 s hard-killed probe,
then 60 s for a read, 600 s for a copy, one bounded wait, a detached launch that returns at once; **THE LOGIN CHECK: a printed login link stops
the step (11) and appends `<HH:MM:SS> aifoundry3 needs a check` to RB_LOCK, nothing retried.**

| # | step | file | what |
|---|---|---|---|
| 0 | (by hand) | | `uptime` on aifoundry2 (the load rule); the anchor lines of E192's land files at HEAD; no E192 datum in any ref |
| 1 | the window | [`rb/s02_window_e192.sh`](rb/s02_window_e192.sh) `<day> <last start> <last end>` | FIRST; today's day only; `RB_PLAN=e192` |
| 2 | the desk check | [`rb/s03_desk_e192.sh`](rb/s03_desk_e192.sh) | outside the kit's list (its sha256 in the land file and section 8); never inside the lab-git lock (it takes it itself for its pull: nested, 16); the registration found by its content; the paths clean; [`rb/check_history_e192.py`](rb/check_history_e192.py) `tree` (additions only since the registration and the kit; no shadow in the six folders the day's Python puts first) and `nodatum`; every list at its count and its own sha256; both freeze lines; the preflight; the desk tests' logs; HEAD unchanged |
| 4 | the look | `../q141k-runbook/k6/s05_look_k6.sh aifoundry3 [--wait]` | k6's, unchanged: et-who, who, uptime, the holder rule; records the box login for the collection |
| 3 | the post, or his waiver | (the card lane's) | after the look reads FREE; E192.md section 12 |
| 5 | the sync | [`rb/s07_a3_sync_e192.sh`](rb/s07_a3_sync_e192.sh) | refused beside a session or job of ours; [`boxfiles-e192.txt`](boxfiles-e192.txt)'s 35 paths, committed and at their pins, into **E192's own root** `build/claims-v3/aifoundry3/e192/` (the shared files too: nothing of another run's is written); the box's copies read at their pins |
| 6 | the build | [`rb/s08_a3_build_e192.sh`](rb/s08_a3_build_e192.sh) `start`, then `wait` while 17 | one detached job, [`build_e192.sh`](build_e192.sh): cmake with the box's `/opt/et`, `check_elf.py` "loops 16, bad 0", the host's `--list --json` and `--list` byte for byte the registration's table, the hashes recorded beside section 16's; **at most two build starts a Pacific day** (a third: NO-THIRD-BUILD, 16); then [`boxcheck_e192.sh`](boxcheck_e192.sh) (the host's name, one card node and the lock file, `et-who --check` answering, the sampler, the heater's parser, the per-sensor sampler's pin, every synced file's pin, today's build record, the plain chain GO); RB_OUT/e192-built.txt |
| 7 | the reads | `../q141k-runbook/k6/s09_a3_reads_k6.sh` | k6's, unchanged: the config (TDP 0 W / 65 C / 600 MHz, never set), et-who clean |
| 8 | the dry pass | [`rb/s10_a3_dry_e192.sh`](rb/s10_a3_dry_e192.sh) `start`, then `wait` | `session_e192.sh --dry` on the box: E192-DRY OK |
| 9 | the session | [`rb/s11_a3_session_e192.sh`](rb/s11_a3_session_e192.sh) `FULL [--plain-sampler]` | k6's guard; **THE REST RULE** ([`rb/rest_rule_e192.sh`](rb/rest_rule_e192.sh)) read on the box, refused before 40 minutes; today's dry pass and build; then `session_e192.sh` detached; the T0 in RB_OUT |
| 10 | the wait | [`rb/s20_wait_e192.sh`](rb/s20_wait_e192.sh), again while 17 | the session process as `session_e192(_v[0-9]+)?\.sh` (the real script's name, tested on it); its end read from its own T0's log; 0 ended (MANIFEST written; a STOP after passes shown); 16 stopped before any pass (still collected) |
| 11 | the release (or nothing under his waiver), then the collection | [`rb/s22_collect_e192.sh`](rb/s22_collect_e192.sh) | E183's desk-path gate's inputs first; one read-only copy back of the session and the build record with the box's manifest; **COPY EXACT** (and the session's own manifest) by [`collect_e192.py`](collect_e192.py); the desk-path gate on the copy; the data directory (our own box login masked; telemetry gzipped without name or time); the holder-line check; the desk-path gate again; E178's scrub; NO-DATUM |
| 12 | the data commit | (the card lane's, through the lab's commit script) | `docs/reports/data/<day>-e192-intbits-aifoundry3/`, README in section 9's form, after the public-text scan |
| 13 | after the data commit only | [`rb/s24_reduce_e192.sh`](rb/s24_reduce_e192.sh) `docs/reports/data/<day>-e192-intbits-aifoundry3` | the registered reducer at `715fddaa...`, unchanged, on the committed bytes (the telemetry unpacked and checked against the session's manifest), then [`check_e192.py`](check_e192.py) (E192.md section 7, its thresholds and no other); no scoring |

The dry listing ([`rb/list_steps_e192.sh`](rb/list_steps_e192.sh)) prints every step's exact commands and remote scripts, and calls nothing.
Its lines "`--- read, run on the Intel (...)`" are the shared runbook driver's own unchanged wording
(`tools/claims-v3/q141k-runbook/rb_common.sh` line 133, from when the desk was the Intel): on the card day every such call runs on the desk,
aifoundry2 since 13 Nov 2026 (fix-e192, verify-e192's nit 7; the driver is not edited).

**THE REST RULE** is E189's (b42dc95c) line for line but its words: no E192 session starts within 40 minutes of the end of our last real
session on the card, read from every session-log form of ours on the box (`build/eNNN/session.log`, `session-*.log`, `T<T0>/session.log`
— E185's, E186's, E188's, E189's, E190's `T<T0>-<arm>/` and E192's own — and `T<T0>/session-*.log`, plus energy.sh's folders); a session cut
mid-queue counts at its run's latest write; dry paths, DRY lines and blocks that opened no device are skipped. E192's own wrapper writes the
kits' form, so the next session of ours on aifoundry3 rests 40 minutes after E192 too.

## 5. The readings stated here before any datum (where E192.md leaves a choice to the kit)

1. **The session is the reference session as committed** (section 1); the kit's stops act through `OUT/STOP` only.
2. **The smoke gate's conditions** are section 2's: exit 0, at least 3 INTBITS lines, every line ok with `check_bad` 0 and 1,024
   participants, and the heater check's launch exit 0. No clock condition is added (the k6 read before the session checks 600 MHz; a clock
   off 600 in the data is registered check 2's to report).
3. **The cap**: from the first card command (the probe, or the sampler's start when no probe is sent); D0 = 400 s; the measured margin 60 s;
   the end-stop 30 s before the cap.
4. **The sampler**: section 3's rule; the go may name the plain sampler.
5. **The data directory**: the session's files as the box wrote them, the telemetry gzipped (no name, mtime 0; step 13 unpacks it and checks
   it against the session's own manifest), our own box login masked as `<box-login>` in every text file but the reference session's records,
   the box's cmake logs left on the box (they carry the box's absolute paths and nothing the data needs; `BUILD-E192.txt` carries the hashes).
6. **Card time** is reported from the first card command to the session's end (the wrapper's "passes complete" line).
7. **The heater check's 70 W boundary** (fix-e192, verify-e192's nit 5). E192.md sections 5, 9 and 11 word the smoke's heater check as
   "under 70 W" and "70 W or more", but the registered `run_block.py` stops only when the highest board reading is above 70 W
   (`top > a.heater_ceiling`): a reading of exactly 70.00 W passes. E192 registers the code (at its sha256), so the code's boundary is the
   rule; E192.md is not edited (its subtree `c78351f9...` and every pin stay).
8. **A `run/SESSION_DONE` the wrapper wrote** (section 1; fix-e192) is a kit marker in the reference session's folder, told apart from the
   reference's own by its bytes (one JSON line with `"by": "session_e192"` and run_session.sh's exit; the reference's is empty) and by the
   wrapper's log line; the data README names it when it is there.
9. **A launch refused before anything opened** ("no device opened": exit 2 at a refusal, or exit 3 at the wrapper's free check or at the
   probe's lock) sent no card command: its card time is 0 and every rest rule skips it. **Whether it may be launched again the same day is
   the go's to say** (verify-e192's finding 4; ready-e192's go lines). The kit's reading, for the go to confirm or refuse: it is not a
   session, and once the look reads FREE again it may be launched once more inside the same window. A launch that sent its probe is a
   session, even when `run_session.sh` then refuses at its own free check (the real-path case B7): the rest rule counts it from its
   "session end" line (the rest-rule test's R16 on B7's real log; R17 skips W1's real refusal).

## 6. THE REAL-PATH DESK TEST, and the audit of the branches the dry path skips

[`desk/desktest_realpath_e192.sh`](desk/desktest_realpath_e192.sh) and [`desk/realpath_e192.py`](desk/realpath_e192.py), with the stand-ins
[`desk/standin_e192.py`](desk/standin_e192.py) (each tool in its own output form, from a small card model: the heater and the host heat the
die model, the sampler reads it at 10 Hz; every call recorded with whether the card lock was held). Run inside W/nodev.sh; the test refuses if
any `/dev/et*` is a device, and re-executes itself with a private `/dev` holding two regular files named `/dev/et0_ops` and `/dev/et0_mgmt`
(fix-e192 added the second: the wrapper's node count now requires it), a private `/run/lock`, a private PID namespace and the host name
aifoundry3; the two-card, no-card and no-mgmt cases nest a sandbox of their own inside it (a fresh private `/dev` holding only the regular
files each names). Its first run (before the land) found three defects of the test's own
stand-ins and **one gap of the kit: the reference reads the heater check's board level but not the heater's exit** (a stand-in heater that
crashed passed the 70 W check on idle readings); the smoke gate now reads it (section 2), and the session's manifest no longer lists its
own temporary file. **The runbook desk test's first run found two defects of this kit's runbook that the dry listing (every step 0) could
not see:** step 6's build wrote cmake's log into `build/` before making it, in a fresh E192 root (on the card day every build would have
failed), and step 2 read the kit list's own sha256 from the previous call's output (it would have refused every day). Both are fixed and
both cases now pass on the real path. **The verifier's break runs** (verify-e192) found the two minor faults section 12 fixes; fix-e192 ported
its break cases and knobs into this test, added more, and ran it whole (108 of 108; first its new cases alone in a scratch copy of the test,
41 of 41, to find its own errors). Its cases:

| case | what it runs | asserted |
|---|---|---|
| 0 | the sandbox; the box copy's preflight | aifoundry3; only the two regular files; a private PID namespace; the plain chain GO, the per-sensor chain GO |
| D | `--dry` | 328 device calls in the registered order; the `-dry` directory and DRY lines; no stand-in called; the manifest exact |
| **P** | **the real path**, the per-sensor stand-in, 9 passes asked, a stop by hand in the gap after pass 1 | the probe under the card lock is the first card command; one sampler, `--seconds 6000 --every-ms 100`, stopped by SIGTERM once; the smoke gate GO on the three runs; the heater check ran (exit 0) below 70 W; passes 0 and 1 in the registered order for aifoundry3, every run 8 or more INTBITS lines, every launch ok; the approach on protocol; 75 host processes, each with the card lock held, `--window 240000000`, `--seconds` 2 or 4, `--stop-file`; the heater under the lock; the stop honoured after the gap (2 passes complete); the cap read before passes 0 and 1; session end, the manifest exact; et-who's readings; **the registered reducer and the section 7 checker read the real path's files** (stand-in numbers) |
| FB, FE | the real `pvt_sample.py` (it cannot open a card here); `E192_SAMPLER=ettelem` | the plain sampler, the fallback, `sample --seconds 6000 --every-ms 100`; the go's choice: no probe |
| H1-H3 | a holder; another user's device process; the lock held | exit 3, nothing opened |
| H4 | a holder after pass 0 | the session stops before pass 1 (exit 3); no device process after pass 0's end |
| L | the lock taken after the sampler started | the smoke's lock busy (exit 75), nothing run, the sampler stopped by SIGTERM |
| S1-S3 | the board above 80 W; the die at 76 C; the sampler quiet | stopwatch's or the block's stop; the host launches nothing after it; no device process after it |
| HC | the heater above 70 W | exit 9, no host run |
| G1, **N1** | a smoke run with `check_bad`; **the negative control: the reference session alone with the same smoke** | the kit's gate stops before any pass; **the reference alone runs into pass 0** (E192.md 17.2's reason for the gate) |
| G2a, G2b, G2d | the cap before pass 0 (D0); 30 s before the cap mid-pass; before pass 1 from a measured pass | each a STOP; the session inside its cap |
| G4, T | the gate killed; SIGTERM to the wrapper | the wrapper writes STOP; the run in flight finishes; session end; the manifest |
| R1-R8 | another host's name; USER; a desk-test variable; a registered file one byte longer; the kit list's sha256; the deadline; no lock file; a sampler word | each refused before anything (exit 2, no device opened) |
| *fix-e192:* R9 | no deadline variable | refused before anything |
| **W1, W2, F0, FM** | nested sandboxes: two cards (the per-sensor path; the plain sampler by the go); no card node; `/dev/et0_ops` without `/dev/et0_mgmt` | **the wrapper refuses at its node count (exit 2), before the free check and before any card command** (verify-e192's finding 2) |
| F0d, W1d, WXd, W5d, NLd | the reference session alone (as N1): no node; two cards with `ET_DEVICES` unset; `ET_DEVICES=x`; `ET_DEVICES=1` with no character node `/dev/et1_ops`; no lock file | each of its own refusals (exit 2), before its free check, nothing opened |
| **B7, B7e, B7p, B7l** | after the wrapper's free check and probe, at `run_session.sh`'s own free check: a holder; et-who failing; another user's device process; the card lock taken between its et-who and its lock probe | `run_session.sh` exits 3 before its EXIT trap; **the wrapper writes `run/SESSION_DONE`, the gate ends at it, the session ends at once** (no STOP; card time a few seconds; verify-e192's finding 1: before the fix each ran to the case's bound); step 10 reads 16; the manifest exact; the stand-in's lock holder ended after B7l |
| H5 | the card lock taken between the wrapper's own lock probe and its probe's `flock` (a stand-in `sha256sum`, first on PATH for this case only, has a holder take it) | exit 3, the probe never ran, no first card command |
| FP, FN | the per-sensor sampler off its reviewed sha256; the per-sensor chain NO-GO (the box copy of E144's table replaced by the stock table, then restored) | no probe, the plain sampler |
| B1-B4 | the smoke's heater launch exits 1; 1,023 participants; the smoke's first host process exits 1; 2 INTBITS lines a run | the kit's gate stops before any pass (exit 8); step 10 reads 16 |
| G5, G5b | the gate alone on a smoke written in another order; its control in the registered order | STOP; GO, no STOP, the gate ends at SESSION_DONE |
| HB | no board reading in any sample | the heater check's stale stop (exit 4), no host run |
| B8 | a holder right after the sampler starts | no block runs (exit 3), the sampler by SIGTERM, SESSION_DONE the reference's own |
| B9 | a sampler that never writes | the smoke's first reading stops (exit 4), no host run |
| B5 | a malformed INTBITS line in pass 0 (`run_block.py` raises) | the block ends (exit 1), the session stops, the sampler by SIGTERM, the manifest exact; no device process after; the rest rule counts the session |
| B11 | a stop by hand inside pass 0 | exit 8, 0 passes complete, step 10 reads 16 |
| B10 | another user's device process after pass 0 | the session stops before pass 1 (exit 3); step 10 reads it ended (0) |
| Z | | no process left; no network call; no `/dev/et*` but the test's two files |

**The audit: the branches skipped under DRY or a dry flag on the session's path, and the case that runs each, or why none can.** Read on
`session_e192.sh`, `run_session.sh`, `run_block.py` (its `--dry`), `stopwatch.py` and `gate_e192.py` (neither runs under DRY). Corrected by
fix-e192 (verify-e192's finding 3: kit-e192's table named cases for rows they did not run). Line numbers are the registered files'.

| where | under the dry path | on the real path | run by |
|---|---|---|---|
| `session_e192.sh`: the node count (fix-e192) | run (both paths) | exit 2 before anything | W1, W2, F0, FM (refused); every other case (passes) |
| `session_e192.sh`: the deadline check | not read | refuses a cap past the window's last end, or no deadline | R6, R9 |
| `session_e192.sh`: the free check (et-who, ps, the lock probe) | printed only | exit 3 before anything | P, H1, H2, H3 |
| `session_e192.sh`: the lock file | printed only | exit 2 before anything | R7 |
| `session_e192.sh`: the probe (the first card command) and the sampler's choice | printed only | `flock -n` + `timeout 10` + `pvt_sample.py --probe`; pvt or the fallback | P (pvt), FB (its probe fails), FE (the go's choice), FP (off its pin), FN (the chain NO-GO), H5 (the probe's lock taken: exit 3) |
| `session_e192.sh`: the gate watcher, the dead-gate stop, the signal trap, the summary lines | not run | | P, G1, G2a, G2b, G2d, G4, T |
| `session_e192.sh`: SESSION_DONE when `run_session.sh` exits before its EXIT trap (fix-e192) | not run | the wrapper writes it, the gate ends | B7, B7e, B7p, B7l (written); P, B8 and the rest (the reference's own: not written) |
| `run_session.sh` lines 52-68: the node count, `ET_DEVICES`, the lock file | skipped | behind the wrapper's own node count and lock-file check | run alone: F0d, W1d, WXd, W5d, NLd; through the wrapper: P (one card). **Not run: line 65** (a binary that ignores `ET_DEVICES` on a two-card host): it needs a character device at `/dev/et1_ops`, which the desk has not, and the wrapper refuses two cards first |
| `run_session.sh` lines 70-119: `free_before_sampler` | skipped | exit 3, nothing opened (after the wrapper's probe) | P (passes); B7 (held), B7e (et-who fails), B7p (another user's process), B7l (the lock) |
| `run_session.sh` lines 121-139: the sampler (pvt or ettelem), stopwatch, the EXIT trap | skipped | | P, FB, S3 (a quiet sampler still ended by SIGTERM), L, T, B8 |
| `run_session.sh` line 141: `free_with_sampler` | skipped | | P (our own holder line passes), B8 (a holder right after the sampler: exit 3) |
| `run_session.sh` lines 110-117 and 144: `locked_block` (the lock, 75) | skipped | | P (every host call with the lock held), L (75) |
| `run_session.sh` lines 147-160: the passes, STOP, the 30 s gap, the holder check | DRY lines only | | P (STOP after the gap), H4 (a holder), B10 (another user's process), G2d (the cap), B11 (STOP inside a pass) |
| `run_block.py` `reading()`: stale, missing, hot | returns the target | | S2 (hot), S3 (stale), B9 (no line), P |
| `run_block.py` `device()`: the process, the marks | prints the command | | P (every call), S1 (no process after STOP) |
| `run_block.py` `approach()`: heats, the wait, the quiet | a fixed record | | P (most launches on protocol) |
| `run_block.py` `run()`: INTBITS parsing, runs.jsonl | not reached | | P, G1, B5 (a malformed line: the block raises, exit 1) |
| `run_block.py` `idle()`: the real loop, the marks | prints | | P (the gate reads the marks) |
| `run_block.py` `heater_check()`: board_max, the 70 W ceiling | not reached | | P (below), HC (above: exit 9), HB (no board reading: exit 4), B1 (the heater's exit) |
| `stopwatch.py`: the board, die and staleness stops | not run | | S1, S2, S3. **Not run: its "no telemetry sample in the first 60 s"**: the block's own reading stops the smoke first in every arrangement (B9: a silent sampler stops at the smoke's first reading, about 10 s in) |
| `gate_e192.py`: the smoke gate | not run | | P (GO), G1 (`check_bad`, lines not ok), B1 (the heater's exit), B2 (participants), B3 (a host exit), B4 (fewer than 3 lines), G5 (the arm order, the gate alone), G5b (its control) |
| `gate_e192.py`: the cap | not run | | P, G2a (D0), G2b (the end-stop), G2d (a measured pass) |

## 7. Card-minutes and the cap (registered; unchanged)

About 52 card-minutes (55.5 with the eight 30 s gaps, E192.md section 10's desk check), **cap 65** from the first card command, enforced by
the gate (section 2) and never by killing a device process. The 40-minute rest before E192's first card command and after its end (the rest
rule, section 4). One session of ours at a time on aifoundry3 (k6's guard).

## 8. Files, the lists and step 2

| file | what |
|---|---|
| `session_e192.sh`, `gate_e192.py`, `preflight_e192.sh`, `drycheck_e192.py` | the session's wrapper, the kit's gate, the device-command preflight, the dry pass's reader (box) |
| `build_e192.sh`, `boxcheck_e192.sh`, `boxfiles-e192.txt` | the build on the box, the box's tools and pins, the sync list (box) |
| `collect_e192.py`, `check_e192.py` | the collection's desk half; the section 7 checker (desk) |
| `rb/rb_e192.sh`, `rb/s02...s24_*_e192.sh`, `rb/rest_rule_e192.sh`, `rb/check_history_e192.py`, `rb/list_steps_e192.sh` | the runbook |
| `rb/selftest_rb_e192.sh`, `rb/selftest_rest_e192.sh`, `desk/desktest_realpath_e192.sh`, `desk/realpath_e192.py`, `desk/standin_e192.py` | the desk tests |
| `KIT.md`, `CARD-LANE-BRIEF.md` | this file; the card lane's brief |
| `SHA256SUMS-e192-kit` | every kit file but itself and step 2 |
| `SHA256SUMS-e192-shared` | the six shared files the box receives, at their sha256 |
| `logs/*.txt` | the desk tests' logs (section 0) |

**Step 2 (`rb/s03_desk_e192.sh`) is outside `SHA256SUMS-e192-kit`** (a file cannot hold the sha256 of a list that holds its own): its own
sha256 and the list's are given in the land file's anchor lines.

## 9. The data commit's README (the card lane writes it; results first, registered against happened, departures dated)

`docs/reports/data/<day>-e192-intbits-aifoundry3/README.md`, in this order:
1. **Results first**: passes complete (of 9; pass 0 the warm-up), the sampler that ran and why, card-minutes (from the first card command),
   any STOP and its reason, the smoke gate's verdict; then, after step 13 only (its own commit), the reducer's prices and the section 7
   checks as `check_e192.py` printed them. **No forecast number and no score**: the model session scores its sealed forecasts privately.
2. **Registered against happened**, row by row (E192.md sections 3-10): the card and clock, the arms and order (the dry pass's E192-DRY
   line, the order the session ran), the windows, the approach, the passes, the smoke, the stops, the cap, the rest.
3. **Departures, dated**, each with its reason (e.g. the post waived by his words of that day; the plain sampler by his go).
4. **The day's records**: the build's hashes (beside E192.md section 16's), the box's manifest, COPY EXACT, the login masked, the scrub,
   `dmcmd_audit`'s verdicts, the commit of the data and of the records.

## 10. What the desk cannot show (for the verifier and the readiness critic)

1. **The real card**: the stand-ins answer in the tools' forms, never the card's; the rate, the power, the die and the per-sensor codes on
   aifoundry3 are unknown until the day.
2. **The box's own tools**: `pvt_sample.py --probe` on aifoundry3's running build, `et-who --check` there, the heater binary's parser and
   sha256 there, the box's `python3`, cmake and toolchain: read by steps 6-9 on the day, never here.
3. **The kernel built on aifoundry3** may differ as a file from section 16's (another toolchain); the gate is `check_elf.py` and the
   `--list` table, and the hashes are recorded, not judged.
4. **The cap's D0 and margin** are a reading (section 5); a pass much longer than measured passes before it is caught by the end-stop.
5. **Command 74's classification** rests on E144's table and its residual (section 3); the go may take the plain sampler instead.
6. **The rest rule reads only trees of ours** on aifoundry3. Its session-log loop reads the tree the runbook's prelude enters (k6's
   `~/aifoundry`, where every kit's `build/eNNN/` is); only its energy.sh loop reads three trees (`~/aifoundry`, `~/nekko`,
   `~/claude/et-soc1-prototyping`). Its desk test now has energy.sh cases in two of those trees and a dry one (R13-R15; fix-e192, the
   verifier's nit 6: kit-e192's wording said the whole rule read three trees).
7. **Our own live collector on aifoundry3** (the repository's `tools/lab/live/live-collector.py`; the box runs a copy, not read here) holds
   the management node a few milliseconds of each second while the card is free, by its documented duty cycle; a single `et-who --check`
   that catches it reads "held". At the wrapper's free check that refuses the launch with "no device opened" (exit 3, nothing sent; section
   5 item 9 for a second launch); at `run_session.sh`'s own check, after the probe, the session now ends at once (B7, with the wrapper's
   SESSION_DONE). The verifier's estimate is about 0.5% a check: from the duty cycle, not measured.
8. **A killed `run_session.sh`** (SIGKILL; nothing of ours sends one) would leave its sampler and stopwatch running: the wrapper now ends at
   once and writes SESSION_DONE (so stopwatch ends too), but the sampler runs to its own bound (`--seconds 6000`), reading only, and the next
   look shows it as our own holder. Not run at the desk.

## 11. Labels

Everything here is **registered** (E192.md, quoted) or a **desk check of code** (this kit's tests). Nothing is measured, blind, held out,
forecast or post hoc.

## 12. Fixed in place before the land (lane fix-e192, Sat 14 Nov 2026 evening, Q176)

The verifier (verify-e192, 17:00-17:55 PST: HOLDS WITH FIXES; the registration holds as it is) applied both land patches on GitHub main
`eee9fb7e` and broke the kit at the desk. Neither the registration nor any arm, value, order, window, threshold, stop, reduction, card time or
cap changed. The kit's files were changed in place (the kit had not landed), on the registration re-applied unchanged on `eee9fb7e`; the
kit's list, step 2's KITPIN and every log in `logs/` were made again.

| verifier's finding | what changed | tested by |
|---|---|---|
| 1 (minor): the wrapper waited on the gate whenever `run_session.sh` exited before its EXIT trap: about 64.5 minutes on the card day, a false cap STOP, a card time of about 3,870 s | `session_e192.sh`: after `run_session.sh` exits, `run/SESSION_DONE` written by the wrapper when absent (a JSON line naming itself; logged), so the gate ends at once (sections 1 and 5) | B7, B7e, B7p, B7l (each ends in about 2 s, card time 1-2 s, no STOP); B8 (the reference's own marker untouched) |
| 2 (minor): the per-sensor probe, the first card command, came before any card-node count | `session_e192.sh`: exactly `/dev/et0_ops` and `/dev/et0_mgmt`, by name, before anything opens a node (exit 2); both desk sandboxes now hold `/dev/et0_mgmt` as a regular file too | W1, W2, F0, FM (refused before et-who and the probe); every other case passes the count |
| 3 (low): branches the dry pass skips were left unrun, though the audit table and the subject said every one ran | the verifier's break cases and knobs ported (`desk/realpath_e192.py`, `desk/standin_e192.py`), more added (section 6), the audit table corrected, the two branches no desk case reaches named with why; the commit subject reworded | section 6 |
| 4 (low): our live collector can make one `et-who --check` read "held" | covered by fix 1 at `run_session.sh`'s check; section 5 item 9 states the kit's reading of a second launch for the go; section 10 item 7 | B7; the rest-rule test's R16 (B7's real log counted) and R17 (W1's real refusal skipped) |
| 5 (nit): the heater check's "under 70 W" against the code's `top > 70` | section 5 item 7 (the code is registered; E192.md not edited) | |
| 6 (nit): the rest rule's "three trees" | section 10 item 6 reworded; energy.sh cases | R13-R15 |
| 7 (nit): the dry listing's "run on the Intel" | section 4 (the shared driver's wording, unchanged) | |
| 8 (nit): a stray error line when no run was recorded | `session_e192.sh`: the launches counted only from a `runs.jsonl` that exists | no case's launch output holds the line (kit-e192's run: HC's and L's did); HC, L and the B7 family record no run |
| 9 (nit): request.md section 8's build folder | section 1 ("Where the card day builds") | |
| 10 (info): command 74's table | section 3: the go names the audit table it accepts; `CARD-LANE-BRIEF.md` section 1 | |

SPDX-License-Identifier: Apache-2.0
