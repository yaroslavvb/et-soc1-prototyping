# E196's run kit: a lab port of the proposal's reference session that runs the passes on the lab's unchanged sparsity host and only the trains on the request's host, driven on aifoundry3 card 0 from aifoundry2, with its host-line reader tested on real card bytes, the runbook in E192's form with E193's records, and THE REAL-PATH DESK TEST with its audit of every dry branch (Q185; kitted, not run)

*Sun 15 Nov 2026 (week 46), PST, on aifoundry2, desk only (Q185, lane `kit-e196`). No card was claimed or opened (aifoundry2 has a card:
every desk test whose log is here ran in the round's CPU slot inside the no-device sandbox, and the real-path test ran each of its cases in
its own sandbox inside that one, with a private /dev holding regular files named /dev/et0_ops and /dev/et0_mgmt), no device
command was sent, no other box was reached, nothing was posted, no simulator ran. New files only, all under `tools/claims-v3/e196/`, on
the registration's local commit (reg-e196's patch applied to GitHub main `e8a85229`: E196.md, `reduce_e196.py`, `proposal/`, `desk/` and
`SHA256SUMS-e196-registration` as committed), every file of which stays as committed. **Before either landed, Q191's lane `fix-e196`
answered their verifier (verify-e196) on Sun 15 and Mon 16 Nov 2026, before any E196 datum** (section 16): the registration as fixed (redaction R1
of request.md's sizing table, dated notes 1-4; on GitHub main `d5beec9b`) has the tools/claims-v3/e196 subtree `6f692709...` and the
list `467ede78...`, 49 of 49 OK, and this kit's pins name them. This is the kit E196.md section 17.2 asks for. **No E196 datum exists, and the forecast stays sealed: no
forecast number is in any file here, and nothing here scores against it.** Nothing here changes an arm, a value, the order, a train, a
window, a threshold, a host assignment, a stop, the cap, a rest or the reduction. Where E196.md leaves a reading to the kit, it is stated in
section 4 before any datum.*

## Results first (desk checks of code; nothing is measured)

Python everywhere: `/usr/bin/python3` 3.12.3 on aifoundry2; cmake 3.28.3, riscv64-unknown-elf-gcc 15.1.0 and g++ 13.3.0 from this box's
/opt/et for the real builds in the runbook's desk test.

| check | result | log |
|---|---|---|
| **THE REAL-PATH DESK TEST**: `session_e196.sh`'s real path, DRY unset, exactly as step 9 launches it, and through it the port, against stand-ins for every device tool (the sampler behind the box copy of E128's guard, the lab's sparsity host, the request's x14_host, et-who, ps), some printing the runtime's line INSIDE their own lines; through the smoke, both trains, two passes and a stop by hand; every gate, stop, holder, the lock, a crash, a signal, the cut order, the refusals; the registered reduction and the checker on the real path's files; and the audit of every dry branch | **DESKTEST-REALPATH-E196 84 of 84 PASS** (Q191's fix-e196 logged run v3, Mon 16 Nov 01:05-01:59 PST, on the fixed kit's final bytes; kit-e196's logged run f2, 16:39:44-17:23:14 PST Sun 15 Nov, read 82 of 82 before the fix pass added case L2): P1-P18 every one PASS, 19 checks with P9's two (the smoke, T1, T2, passes 0 and 1: 89 lab-host and 54 request-host processes; 19 runtime lines dropped inside host lines, every such process's records written; the one unreadable run written as nothing; the registered `--readback-none-ok` exempted 63 runs, T1 12 units, 108 read-backs ok); L2 2 of 2 (the card lock taken in the gap after pass 0: the port's exit 75 read as a registered stop, session.rc 1, no device process after pass 0); the audit: 11 dry branches, each with a row, each row's cases passed | [`logs/desktest-realpath-e196.txt`](logs/desktest-realpath-e196.txt) |
| **THE REAL-BYTES TEST**: the host-line reader on the bytes the lab committed from cards | **REALBYTES-E196 16 of 16 PASS** (fix-e196's run v3, 2026-11-16 01:59:36 PST): 1a4bc1e3's split line reassembled (its first reader's broken head: the negative control); 32 committed stdout.txt files with a runtime line; 36 of the lab's own sparsity host's raw fp32 stdout files from aifoundry3 (153 lines) read exactly, with their own command lines; 16,287 of 16,287 splices at every byte offset; aifoundry3's real runtime text between lines (read) and inside a line (unreadable); E193's and E189's aifoundry3 lines; the E78 heater's real stdout with the registered heater command, and with a lost line (out of order); the request's host form as stand-ins | [`logs/realbytes-e196.txt`](logs/realbytes-e196.txt) |
| **the runbook** with a stand-in ssh and rsync on a stand-in box; **the box's builds REAL** (both hosts and the kernel with this desk's /opt/et) | **SELFTEST-RB-E196 23 of 23 PASS** (Q191's fix-e196 logged run v1, Mon 16 Nov 01:00:39-01:05:01 PST, on the fixed kit's bytes; kit-e196's logged run g2, 17:51:36-17:55:58 PST Sun 15 Nov, read 23 of 23 before the fix): the window rule, the lab-git lock (absent, nested), step 2 at every pin and its refusals (two lists short, an edited registered file, two shadows, a datum on a side branch), the sync, **E196-BUILT by the real builds** (both kernel ELFs `990807f4...`, both `.text` `8798e43c...`, 42 of 42 refusals), a second start, NO-THIRD-BUILD, the login link, a hang, a cut wait, no build today, the dry pass on the box (E196-DRY OK), the rest rule through step 9, **the rest read before step 7** (`rb/s09_rest_e196.sh`: refused 10 minutes after a session's end, open at 45), **the real `session_e196.sh` launched and waited on by its real name**, the same-day rule, two decoy names, the collection (COPY-BACK EXACT), the reduction before and after the data commit, a box file changed, **a gate stop collected into `docs/reports/gate-stops/`** and the same-day rule after it | [`logs/selftest-rb-e196.txt`](logs/selftest-rb-e196.txt) |
| **the rest rule**: E183's, E189's, E192's, E195's and E196's forms, a dry pass, a refusal, a cut session, energy.sh's folders, the newest of several, and the real-path test's own P and H1 logs | **SELFTEST-REST-E196 14 of 14 PASS** (fix-e196's run v1, 2026-11-16 01:59:35 PST, reading that lane's own real-path run's P and H1 logs) | [`logs/selftest-rest-e196.txt`](logs/selftest-rest-e196.txt) |
| the dry listing, every step with stand-ins | 14 steps listed, 0 exited non-zero, **0 box calls** (fix-e196's run v3, 2026-11-16 01:59:36 PST; a sample window on Mon 16 Nov) | [`logs/dry-listing-e196.txt`](logs/dry-listing-e196.txt) |
| `dmcmd_audit`, every file the session's chain runs (`preflight_e196.sh`) | **GO, 11 send sites, 0 disallowed, every one a READ**, no allow-list and no exception (fix-e196's run v3) | [`logs/dmcmd-audit-e196.txt`](logs/dmcmd-audit-e196.txt) |
| the port's dry listing against the registration | **E196-DRY OK: 255 device calls (237 cut), line for line the commands of desk/commands-e196.txt in the written orders**: 201 on the lab's host, 54 on the request's | the real-path test's case D and the runbook test's case DR |
| the reader's self-check and the checker on the registration's synthetic session (arbitrary test values, the registered reduction unchanged) | E196-LINES SELF-CHECK PASS (480 of 480); the reduction rc 0 (5 passes kept, 154 runs; fix-e196's run v3); CHECKS-E196 ran all six checks and the reported items (its readings are of the synthetic values, never a forecast) | [`logs/checks-e196.txt`](logs/checks-e196.txt) |
| the host change | the two hosts by sha256, the exact diff (724 removed, 291 added, the registration's diff body SAME), the options it adds, dmcmd_audit GO with 0 send sites on both hosts and the kernel, which host runs which arm, the predicted peak against the stops | [`desk/host-change-e196.txt`](desk/host-change-e196.txt) |

## Builds on (the stock-take's rule for lanes, MAP section 3)

1. **Checked:** E196.md (the registration, its freeze line, `6f692709...`); E192's kit (`a6fe5c20`: the reference session's family driven
   by a wrapper, the runbook's form, the real-path desk test and its stand-ins) and E193's (`45d45c12`: the first card command stamped as it
   starts, a gate stop's record, a crash read apart, the audit table of dry branches); E191's kit note 2 (`2d0fe517`: the host's line read
   from a source no runtime print can split, tested on real bytes); E192's data note 1 (`4e964246`: step 7's configuration read only once
   the rest has opened); k6 (`tools/claims-v3/q141k-runbook/k6/`); `tools/claims-v3/dmcmd_audit.py` and `dmcmd_table.json`; the go lines and
   card days of E192 and E193 (OUT/ready-e192, ready-e193, card-e192, card-e193); the round log's sections 104, 109, 110-120.
2. **Used, unchanged** (called, sourced or run by path; sha256 in [`SHA256SUMS-e196-kit`](SHA256SUMS-e196-kit) and
   [`SHA256SUMS-e196-shared`](SHA256SUMS-e196-shared)): the proposal's `stopwatch.py`, `make_x14.py`, `arms.json` and the host and kernel
   sources (the registration's list); `reduce_e196.py` (registered); the lab's `workloads/sparsity` (the unchanged host, its source
   `0f53a7d5...`); the lab's five E78 tiles (`tools/claims-v3/kinds/tiles/fp32`); **k6's runbook drivers** (`rb_common.sh`, its look
   `s05_look_k6.sh` and reads `s09_a3_reads_k6.sh`; v3.1's `rb_run.py` and `nopath_q142s.py`); **E183's desk-path gate**
   (`e183/rb/nopath_desk_e183.sh`, `nopath_spell_e183.py`); **E128's guard** (`e128/ettelem_guard.sh`); **Q136(w)'s `dmcmd_audit.py`** with
   the stock table; E193's rest rule's code, line for line.
3. **Not used:** any forecast number (sealed: E196.md section 0); any other card; any private page; a simulator.
4. **Tiers:** every file here is public tier and cites public pieces only.
5. **Readiness:** this kit gates nothing by itself: a verifier, a fix pass and a readiness check come next, then the session.

## 1. The session: a lab port of the reference session, and why

**Which, and why.** E196 runs **a lab port** of the proposal's reference session, not the proposal's runner as committed. E196.md
section 3 registers, on the post's words, that **the passes run on the lab's unchanged sparsity host and only the trains use the request's
host**; the proposal's `run_block.py` runs every arm on `x14_host` with `x14_host`'s arguments (`--label`, which the lab's host refuses:
reg-e196's finding 2), so it cannot run E196 as registered. The port changes only what that assignment needs and keeps every arm, order,
train, window, gap, approach, idle, burn-in, anchor, stop and the deadline by keeping the proposal's code: each port is the proposal's file
with marked changes, and its diff against the registered file is committed (`desk/port-diff-run_block-e196.txt`,
`desk/port-diff-run_session-e196.txt`).

[`run_block_e196.py`](run_block_e196.py) is `proposal/src/run_block.py` with:

| change | what | why |
|---|---|---|
| P1 | every pass run (two burn-ins, K.pi first and last, the 28 other arms), each train block's two K.pi anchors, every heater launch and the smoke's heater check on the lab's unchanged `sparsity_host` (`--lab-host`), with `desk/commands-e196.txt`'s commands (`lab_args`); the trains, the smoke's T1 processes and premise runs on `x14_host`, as before; `--heater` must be the lab's host | E196.md 3 |
| P2 | the smoke: the heater check, the four smoke arms on the lab's host, the same four on the request's host (with read-backs), two T1 processes; the gate reads both sets (the lab's set has no read-back: exempt from that one condition) | E196.md 6 |
| P3 | a lab-host launch written into `runs.jsonl` in the reduction's input form: its SPARSITY keys, `ops` = iters x minions, `"readback": "none"`, `"binary": "sparsity_host"`; a request-host launch carries `"binary": "x14_host"` | E196.md 7 |
| P4 | every host's stdout read by [`e196_lines.py`](e196_lines.py) (runtime lines dropped wherever they fell, every host line verified against its command); a process with any line it cannot read, or with launches out of order, writes NONE of its records (a mark names it; the smoke gate fails for it; a heater launch with it counts as failed) | CONTEXT section 116 |
| P5 | the order drawn on the host string `aifoundry3` and the pass (the registered order, `desk/order-e196-aifoundry3.txt`), not on this host's name; the session refuses any host not named aifoundry3, so on the box the two are the same string | E196.md 6 |
| P6 | **the kit's stop K1**: in the smoke, every run of both sets within 0.5 cycles of its expected count (544 with a row masked, 546 otherwise) | section 4; finding 1 below |

[`run_session_e196.sh`](run_session_e196.sh) is `proposal/src/run_session.sh` with: S1 the files (the port, `stops_e196.py`, the proposal's
`make_x14.py`, `arms.json` and `stopwatch.py` at their registered paths); S2 `LAB_H` required, the heater (`HEATER` must be it); **S3 the
opening configuration gate** (config-start.json must read `"tdp_w":0` and `"minion_mhz":600`, else "GATE-STOP" and exit 12 before the
sampler); **S4 the lab's live stops** ([`stops_e196.py`](stops_e196.py): board at or above 65 W on three samples in a row, a die reading at
or above 70 C, and the cap's end-stop) started beside `stopwatch.py` and checked with it before every block; S5 the one-card binary check
covers `LAB_H`; S6 the DRY listing names them. Everything else is the reference's line for line.

**The wrapper** ([`session_e196.sh`](session_e196.sh)), started detached by step 9, E192's form with E193's records:

| the wrapper's step | what | why |
|---|---|---|
| 1 | refusals before anything (exit 2, "no device opened"): the host's name aifoundry3 (hostname and Python's); USER the login; the registration's list at `467ede78...` and its six session files at their pins; the kit's list at the sha256 the runbook passes and its seven session files; the shared list; both hosts and E128's guard present and the box's sampler; today's build record (`build/BUILD-E196.txt`) and both hosts at its hashes, both kernels' `.text` `8798e43c...`; the preflight GO; exactly `/dev/et0_ops` and `/dev/et0_mgmt` | nothing runs that is not pinned; no device opened before these |
| 2 | **the first card command**, stamped as it starts (E193's reading): the free check (`et-who --check` exit 0, no other user's device process, a probe of the existing card lock, read-only, never created) | E196.md 10: the cap counts from it |
| 3 | **the cut order** from M, the minutes from the first card command to the earlier of the window's last end and the cap: M >= 53 every arm, passes 0-5 and 6 if it fits; 43-53 the passes that fit; 40-43 `DROP_ARMS=F.Ae,Z.b50,I.H.mFFFF`; M < 40 no session ("no device opened") | E196.md 6 |
| 4 | **DEADLINE** = the first card command + 58 minutes (or the last end - 2 minutes, if earlier): the port's own block-start rule; **the end-stop** at the cap - 60 s (or the last end - 60 s) through `stops_e196.py` | E196.md 10 |
| 5 | the port, `run_session_e196.sh build/e196/T<T0>/run 7`, with `H`, `LAB_H`, `HEATER`, `ETTELEM` (E128's guard), `SAMPLER=ettelem`, `GAP=30`, `TARGET=58`, `PREHEAT=59`, the lock, `LAB_TILES`, `TRAINS="T1 T2"`, `DEADLINE`, `STOPS_END_EPOCH` (and `DROP_ARMS` by the cut order), `ET_DEVICES` unset; a signal to the wrapper writes STOP and waits (never a kill); `run/SESSION_DONE` written when the port exited before its own | E196.md 6 and 9 |
| 6 | how it ended, in the wrapper's own words: "GATE-STOP:" when no train or pass block ran (no data); "session stopped: ...; the blocks done stand" after a registered stop; "session ended without a registered stop" for a crash; "trains complete: k of 2; passes complete: k of 7"; "session end (T0 <T0>)"; MANIFEST.sha256 last; session.rc (0 ended, 1 a registered stop after data, 2 a refusal, 3 a gate stop, 4 a crash) | E196.md 11; every rest rule and step 10 read them |

`--dry` runs the same refusals, then the port's DRY mode twice (the full plan and the cut order, six passes as the registration's dry check
ran the reference), read by [`drycheck_e196.py`](drycheck_e196.py): **255 device calls (237 cut), line for line the commands of
`desk/commands-e196.txt` in the written orders**: 201 on the lab's host, 54 on the request's; the registration's 251 (233) and the smoke's
second set of four.

## 2. The box: E196's root, the builds, the session directory, the tools

- **E196's root** is `build/claims-v3/aifoundry3/e196` under the box's tree (`~/aifoundry`). Step 5's rsync -R puts each of
  [`boxfiles-e196.txt`](boxfiles-e196.txt)'s 45 paths at its repository path there (the shared ones too: the audit and its table, E128's
  guard, the lab's unchanged sparsity workload's nine build files, the five lab tiles); nothing of another run's is written.
- **The builds** ([`build_e196.sh`](build_e196.sh), step 6): the lab's unchanged `workloads/sparsity` into `R/build/sparsity-lab`, the
  request's `proposal/src` into `R/build/x14`, never `build/sparsity` (which other kits use: E196.md 9); both kernels' `.text` must read
  `8798e43c...` (a gate: E196.md 11); the ELFs reported beside the desk's `990807f4...` and request.md's `abbdbe40...`, never judged; the hosts
  by their behaviour (42 refusals before anything: every registered command parses, `--label` is refused by the lab's host); make_x14.py's
  check and arms.json; the hashes in `R/build/BUILD-E196.txt`, which the session checks before anything opens.
- **The session's directory** is `build/e196/T<T0>/` under the tree (the dry pass's `build/e196/T<T0>-dry/`): `session.log`, the first card
  command, the hashes, the pins, the preflight, the port's output, `run/` (the port's OUT), MANIFEST.sha256, session.rc. Every rest rule of
  ours reads `build/e*/T*/session.log`.
- **The box's tools**, unchanged: `et-who --check`, the card lock `/run/lock/etsoc-shire0.lock`, coreutils' `timeout`, util-linux's `flock`,
  and **the sampler `build/ettelem/ettelem`, the box's own build**, through E128's guard (synced into E196's root; the guard refuses
  `--reset-ms` and every word but `config` and `sample`), which every aifoundry3 kit uses and the audit table lists as the reviewed variant.

## 3. The host change, audited ([`desk/host-change-e196.txt`](desk/host-change-e196.txt))

- **Both hosts by sha256:** the lab's unchanged host source `0f53a7d5...` (1,034 lines, unchanged since `27dce7f0`, 25 Sep 2026); the
  request's `x14_host` source `b91a2c76...` (590 lines). The kernel side (`sparsity.c`, `crt.S`, `sections.ld`, `kernel/CMakeLists.txt`,
  `sparsity_args.h`) is byte for byte the lab's. Binaries embed their build folder's kernel path, so their sha256 is each build's own: the
  box's are recorded by step 6 and checked by the session.
- **The exact diff** (`diff -u` of the lab's source against the request's): 724 lines removed, 291 added, 11 hunks; the same body as the
  registration's `desk/host-diff-e196-lab.txt`. **What it adds** (options only in the request's host): `--abba --label --label-b --launches
  --live-rows --live-rows-b --row-mask-b --values-b --zero-rows --zero-rows-b`: the A B B A train with a second row mask, the read-backs of
  C after the calibration launch and the last launch, labels; and the one-card rule and the 8 s launch budget. It removes the simulator's
  layer, every probe but the fp32 TensorFMA loop, fp16, int8, patterns and sweeps.
- **No device command beyond the table's reads and the runtime's launches:** both hosts make one device layer for the ops node only
  (`createPcieDeviceLayer(true, false)`) and the runtime's own create; neither holds a device-management command, an ioctl or a management
  node open (the one `_mgmt` in each is a comment); `dmcmd_audit` on both host sources and the kernel: GO, 0 send sites.
- **Which host runs which arm:** the lab's UNCHANGED host runs the heater check and every heater launch, the smoke's first set, each
  train block's two K.pi anchors and every pass run (every pass arm of arms.json, K.pi included: 201 device calls at six passes); the
  request's host runs the smoke's premise runs and two T1 processes and the 48 train processes (T1: T.Z.m1111 against I.Z.m000F; T2:
  T.Z.m5555 against I.Z.m00FF: 54 calls). The records say which (`"binary"`), and the real-path desk test checks every record.
- **The predicted peak against aifoundry3's stops** (registered, E196.md 9): the hottest load is random fp32 at full issue (I.R.full, and
  every heater launch); board about 54 W, die about 62 C (E178 54.06 W / 62 C; E192 53.32 W / 61 C with this heater); margins 11 W to the
  lab's 65 W stop, 26 W to stopwatch's 80 W, 16 W to the heater ceiling, about 8 C to the 70 C stops. The trains run on the zero tile.

## 4. The readings stated here before any datum (where E196.md leaves a choice to the kit)

- **The first card command** is the wrapper's free check, stamped as it starts (E193's reading); the cap (60 minutes) and the cut order's M
  count from it. A launch refused before it sent nothing ("no device opened": its card time is 0, every rest rule skips it).
- **The rest before step 7** (E192's data note 1, `4e964246`: E192's step 7 read came inside the 40 minutes): step 7's configuration read
  is a card command, so the kit holds it to the rest too: [`rb/s09_rest_e196.sh`](rb/s09_rest_e196.sh) sends the rest rule (the lines step 9
  sends; no card command) right before step 7: 0 the rest has opened, 10 not yet. Step 9 reads the rule again before the launch.
- **The cut order** (E196.md 6) is applied by the wrapper at the start, from M; within 43 <= M the port's own deadline decides which passes
  fit (it measures the first pass; a seventh only if it fits).
- **The end-stop** (`stops_e196.py --end-epoch`): STOP at the first card command + the cap - 60 s (or the window's last end - 60 s), so a
  block that overruns its estimate ends with the launch in flight, and the sampler's stop and the closing read fit inside the cap.
- **The opening configuration gate** (E196.md 6.2): `"tdp_w":0,` and `"minion_mhz":600,` in config-start.json (k6's strings), else
  GATE-STOP, exit 12, no sampler (no data); the threshold is reported, not gated (E196.md names TDP and the clock).
- **The lab's 65 W stop** reads "three samples in a row" as every telemetry sample with a board reading, a repeated meter value included
  (the stricter reading; stopwatch.py's 80 W counts distinct readings); "at or above".
- **The heater check's 70 W ceiling** sits above the lab's 65 W stop: on the card a heater at 65 W or more is stopped by the 65 W stop first
  (the real-path case HC); either ends the session before any smoke arm (E196.md 11's row).
- **THE KIT'S STOP K1** (E196.md 17.2: "the kit may add stops that end a session early"): in the smoke, each run of both sets within 0.5
  cycles of 544 (a row masked) or 546 (otherwise), else the smoke gate fails. E196.md section 14 counts on "a masked row takes 544 cycles,
  an unmasked op 546: a mask that did not act reads 546" to stand in for the passes' missing read-back; but the registered condition (within
  0.5 % of 544 or 546) is 2.72 cycles wide, wider than the 2-cycle step, so it cannot see a mask that did not act (the real-path case G2
  runs it: 546.015 on a masked arm passes the 0.5 % condition and fails K1). K1 adds the check where it can still stop the session, before
  any train or pass; the reduction's 0.5 % gate on the passes is registered and unchanged, and check 5 (0.05 cycles) reports any pass run
  off its count.
- **A host output the runner cannot read** (P4) writes no record of that process: a run of the lab's host then has no value (as a run the
  reduction sets aside), a train process gives no value (as an excluded one), a smoke run fails the gate. Never a wrong datum; never a
  partial run (a lost calibration line would move the reduction's window).
- **The same-day rule** (step 9; for the go to confirm or refuse): E196 runs once a Pacific day. A launch that ended with "no device opened"
  may be launched once more the same day (at most two such launches); a session that opened the card and ended at a gate (the opening
  configuration read, the smoke) is not tried again that day; a session with data never twice without a dated amendment.
- **A gate stop's record** (E193's form): a session with no train and no pass block (session.rc 2 or 3, a "GATE-STOP:" or "no device
  opened" line) is collected under `docs/reports/gate-stops/<day>-e196-zeroshare-T<T0>-aifoundry3/`, never under `docs/reports/data/`.
- **A crash** (the port exited non-zero with no stop recorded, e.g. a block killed from outside): "session ended without a registered
  stop", session.rc 4, step 10 MAIN-CRASHED; collected into the data directory; a dated note decides whether its blocks are reduced.
- **The data directory**: `docs/reports/data/<day>-e196-zeroshare-aifoundry3/` (session/, run/, facts-e196.json, SHA256SUMS), the
  telemetry gzipped with no name and mtime 0; step 13 unpacks it and checks it and the records against the box's manifest.
- **The scrub**: the box's home becomes `~`; the user of every holder line and our own login become `<login>`; no /home/ path and no login
  may be left; binary tiles copied as they are.
- **Check 6's carry-over** (E196.md 8.6): with the reduction's own launch reading (its dip rule; kept board samples in [start + 170 ms,
  end], at least 2) and its own exclusions of a process, per complete quad L2 - L3; per unit the SFFS process's value less the FSSF
  process's; mean over units, 95 % interval (t over units).
- **The sampler**: `ettelem sample --every-ms 100` through E128's guard (E196.md 5: never `--reset-ms`; the per-sensor sampler is not used).

## 5. The runbook from aifoundry2 ([`rb/`](rb/); the card lane's brief: [`CARD-LANE-BRIEF.md`](CARD-LANE-BRIEF.md))

Each step a script in E192's form through k6's drivers, unchanged (a 15 s hard-killed probe; 60 s for a read, 600 s for a copy, one bounded
wait, a detached launch; a printed login link stops the step with 11 and appends `<HH:MM:SS> aifoundry3 needs a check` to `RB_LOCK`, nothing
retried; exit codes 0, 10-17). One RB_OUT for the day.

| box step | file | what |
|---|---|---|
| B, 0, H | (by hand) | the booking (G); THE ONE-LAB RULE (`W/onelab.sh desk` around steps 0-2); `uptime` (THE LOAD RULE); GitHub main; the anchor lines; THE QUIET HOLD |
| 1, the window | [`rb/s02_window_e196.sh`](rb/s02_window_e196.sh) `<day> <last start> <last end>` | today only; the cap (3,600 s) before the last end |
| 2, the desk check | [`rb/s03_desk_e196.sh`](rb/s03_desk_e196.sh) (outside the kit's list) | the window; the pull under the lab-git lock (never nested: 16); the registration by its content and an ancestor of HEAD; the paths clean; the history check ([`rb/check_history_e196.py`](rb/check_history_e196.py)); every list at its count and its own bytes, every entry OK; the freeze line; no E196 datum in any ref; the preflight GO; the desk tests' logs; HEAD unchanged |
| 4, the look | `../q141k-runbook/k6/s05_look_k6.sh aifoundry3 [--wait]` | k6's, unchanged |
| 3, the post | (none) | his standing waiver |
| 5, the sync | [`rb/s07_a3_sync_e196.sh`](rb/s07_a3_sync_e196.sh) | the box read first (no session or job of ours; E196's root made); boxfiles-e196.txt's files, committed and at their pins, into E196's root; the box's copies at their pins |
| 6, the build | [`rb/s08_a3_build_e196.sh`](rb/s08_a3_build_e196.sh) `start`, `wait` | the detached job `build_e196.sh`; at most two starts a Pacific day; then [`boxcheck_e196.sh`](boxcheck_e196.sh) (the host's name, one card node and the lock file, et-who answering, the sampler, every pin, today's build record, the preflight); RB_OUT/e196-built.txt |
| 7, the reads | [`rb/s09_rest_e196.sh`](rb/s09_rest_e196.sh), then `../q141k-runbook/k6/s09_a3_reads_k6.sh` | **only once the rest has opened** (E192 data note 1): first the rest rule read on the box (the lines step 9 sends; no card command): 0 opened, 10 not yet (wait, run it again); then k6's reads, unchanged |
| 8, the dry pass | [`rb/s10_a3_dry_e196.sh`](rb/s10_a3_dry_e196.sh) `start`, `wait` | `session_e196.sh --dry` on the box: E196-DRY OK |
| 9, the session | [`rb/s11_a3_session_e196.sh`](rb/s11_a3_session_e196.sh) | the window and its cap, k6's guard, the same-day rule, **THE REST RULE** ([`rb/rest_rule_e196.sh`](rb/rest_rule_e196.sh): every session-log form of ours on the box), today's dry pass and build; then `session_e196.sh` detached |
| 10, the wait | [`rb/s20_wait_e196.sh`](rb/s20_wait_e196.sh), while 17 | the session found by its real script's name (the wrapper's own script name, `session_e196.sh` or a dated `_vN`, never the port's `run_session_e196.sh`); GATE-STOPPED and MAIN-CRASHED read only from the wrapper's own lines (16); the manifest |
| 11, the collection | [`rb/s22_collect_e196.sh`](rb/s22_collect_e196.sh) | E183 note 5's desk-path gate's inputs first; how it ended, read on the box; one read-only copy back; [`collect_e196.py`](collect_e196.py): COPY-BACK EXACT, the data directory or the gate stop's record, the scrub, facts, SHA256SUMS; the desk-path gate; the history check |
| 12, the commit | (the card lane's, through the lab's commit script) | the data directory with its README in [`DATA-README-FORM-e196.md`](DATA-README-FORM-e196.md)'s form, or the gate stop's record |
| 13, the reduction | [`rb/s24_reduce_e196.sh`](rb/s24_reduce_e196.sh) | after the data commit only: the committed records checked against the box's manifest and arms.json against the registered table; **the registered reduction, `reduce_e196.py OUT --readback-none-ok`, unchanged**; then [`check_e196.py`](check_e196.py) (E196.md 8) |

The dry listing: [`rb/list_steps_e196.sh`](rb/list_steps_e196.sh). Its lines "run on the Intel" are k6's `rb_local` wording, unchanged: they
mean the desk (aifoundry2).

## 6. Device commands

[`preflight_e196.sh`](preflight_e196.sh) runs `dmcmd_audit.py` with the stock table, **no `--allow` and no `--except`**, over every file whose
commands the day sends: the wrapper, the port and its block, the stops and the reader, the build, the proposal's stopwatch.py and
make_x14.py, both hosts' sources, the kernel, and E128's guard: **GO, 11 send sites, 0 disallowed, every one a READ** (E128's guard line 18,
`ettelem config`: GET_MODULE_STATIC_TDP_LEVEL, GET_MODULE_TEMPERATURE_THRESHOLDS, GET_MODULE_POWER_STATE, GET_ASIC_FREQUENCIES,
GET_ASIC_VOLTAGE; line 31, `ettelem sample`: GET_MODULE_POWER, GET_SP_STATS, GET_MODULE_CURRENT_TEMPERATURE, GET_ASIC_VOLTAGE,
GET_MODULE_VOLTAGE, GET_ASIC_FREQUENCIES), the port's two `"$ETTELEM"` calls noted as going through the guard (resolved by the wrapper's
`ETTELEM`; reg-e196's finding 5 answered). The hosts open the ops node only; the kernel sends nothing; `et-who --check` sends no device
command; k6's step 7 reads the configuration through the same guard. No set, no reset, no statistics reset, no firmware query, no PMIC
command.

## 7. THE REAL-PATH DESK TEST and the audit of every dry branch

[`desk/desktest_realpath_e196.sh`](desk/desktest_realpath_e196.sh) and [`desk/realpath_e196.py`](desk/realpath_e196.py) run **the
session's real path, DRY unset**, exactly as step 9 launches it (`session_e196.sh` with the runbook's variables, from a stand-in aifoundry3
tree holding boxfiles-e196.txt's files as the sync puts them), and through it the port as committed, against
[`desk/standin_e196.py`](desk/standin_e196.py)'s stand-ins at the tools' real paths: the box's sampler behind the box copy of E128's guard
(its `config` and its 10 Hz `sample`), **the lab's sparsity host** (its option parser, the node count, a calibration launch then launches of
about 0.5 s, SPARSITY lines in main.cpp's printf form, 544 or 546 cycles by the mask, the heater's load), **the request's x14_host** (its
parser and refusals, X14 and X14CHECK lines in its printf form, the A B B A kinds, the read-backs), et-who and ps; **some stand-ins print the
runtime's line "Opening device 0" INSIDE their own lines** (aifoundry1's form, 1a4bc1e3), one prints unknown text inside a line. Each case
in its own sandbox (a private /dev with regular files named /dev/et0_ops and /dev/et0_mgmt, a private /run/lock, a private PID namespace,
the host name aifoundry3), inside the no-device one, refusing to start if a character device /dev/et* is visible. The cases (in its log):

| case | what it runs | asserted |
|---|---|---|
| 0, ST | the sandbox; the box copy's preflight; `stops_e196.py` on synthetic telemetry | aifoundry3, two regular files, a private PID namespace; GO; the 65 W rule at exactly 65.0 (stop), a broken run of three (none), two samples (none), 69 C (none), 70 C (stop), the end-stop, SESSION_DONE, the first writer's STOP kept |
| D | `--dry` | 255 device calls (237 cut), line for line the registered commands; the -dry directory, every line DRY; no stand-in called; the manifest |
| **P** | **the real path**: the smoke, T1, T2, passes 0 and 1, a stop by hand in the gap after pass 1; every 7th process of each host splits a line with the runtime's text; F.B0's first run prints unknown text inside a line | the first card command and the cut order (M = 60); both configuration reads through the guard under the lock; one sampler stopped by SIGTERM; the heater check below 70 W and SMOKE-GATE PASS; both smoke sets (the lab's with readback none; the request's with 8 read-backs ok); T1 and T2: K.pi on the lab's host, 24 processes alternating SFFS and FSSF on the request's host, 14 launches each, 96 read-backs; passes 0 and 1 in the written order for aifoundry3, every run on the lab's host with `ops` = iters x minions and readback none; **the unreadable F.B0 run written as nothing, a mark naming it**; **every runtime line dropped and every such process's records written**; every host process under the card lock, `--stop-file` last; the stop honoured in the gap; the closing read; the manifest; step 10 reads RUN-ENDED; **the registered reduction (`--readback-none-ok`) reads the real path's files** (63 runs exempted, T1 12 units) and the checker reads them (108 read-backs); the rest rule counts the session |
| H1-H3 | a holder; another user's device process; the lock held | exit 3, nothing opened; the rest rule skips the refusal |
| H4 | a holder after T1 | the session stops before T2 (session.rc 1), no device process after T1 |
| CFG | the opening configuration at TDP 65 W | GATE-STOP (the port's exit 12), no sampler, no block; step 10 GATE-STOPPED |
| L | the lock taken after the sampler started | the smoke's lock busy, nothing run, GATE-STOP; the sampler by SIGTERM |
| L2 | the lock taken in the gap after pass 0, after data (added by Q191's lane `fix-e196`, verify-e196's finding 6) | pass 1's lock busy (the port's exit 75): "session stopped", session.rc 1, the trains and pass 0 stand; no device process after pass 0; the manifest; step 10 RUN-ENDED |
| HC, HF | the heater at 72 W; the heater check's launch failing | the 65 W stop first and the 70 W ceiling (exit 9), no smoke arm; the smoke gate failing at once |
| G1-G3 | a premise read-back not ok; a masked lab-host smoke run at 546 cycles; a tensor error | SMOKE-GATE FAIL, no train (G2: the registered 0.5 % condition passes it, K1 fails it) |
| U1, U2 | an unreadable lab-host smoke run; the runtime line inside a line of every host process | no record and the gate fails by name; every record read and the gate passes |
| S1-S3 | the board at 66 W in T1; the die toward 74 C; the sampler quiet | the lab's 65 W stop (before stopwatch's 80 W), no launch after it; a 70 C stop; a stale stop, the sampler by SIGTERM |
| X1 | the block killed from outside mid-train (no stop) | "session ended without a registered stop", session.rc 4, step 10 MAIN-CRASHED, the manifest |
| T | SIGTERM to the wrapper mid-train | STOP, the run in flight finishes, the blocks done stand, session end |
| M41, M45, M39 | the window's last end 41, 45, 39 minutes away | the cut order (the three arms dropped: the port's plan line); every arm and DEADLINE = the last end - 2 minutes; no session, no device opened |
| R1-R9, W1-W3 | another host's name; USER; a desk-test variable; a registered file changed; the kit list's sha256; no deadline; the build record not today; a host not the recorded build; a `.text` not 8798e43c...; two cards; none; no et0_mgmt | each refused before anything (exit 2, no device opened) |
| W10, Z | step 10's patterns read from its own file; the end | the wrapper found by its real name and never the port's; no process left, no network call, no /dev/et* but the two files |

**The audit** ([`desk/dry-branches-e196.tsv`](desk/dry-branches-e196.tsv)): every line of `session_e196.sh` that branches on DRY (4),
of `run_session_e196.sh` on `${DRY:-}` (1) and of `run_block_e196.py` on `a.dry` (6): what the dry path does there, what the real path does,
and the cases that run the real branch; the test reads the files' own lines and fails if one has no row, a row's text differs, or a named
case did not pass in the same run. No dry branch on the session's path is left unrun.

## 8. The real-bytes test (the lesson of E191's first session)

[`desk/realbytes_e196.py`](desk/realbytes_e196.py) feeds the kit's host-line reader ([`e196_lines.py`](e196_lines.py), the one place the
runner reads a host's stdout) **the bytes the lab committed from cards**: E191's split smoke stdout (1a4bc1e3: the ledger host's line with
"Opening device 1" inside it, reassembled to its PASS line, while E191's first reader takes the broken head: the negative control) and every
committed stdout.txt with a runtime line (E191's two sessions); **the lab's own sparsity host's raw stdout from aifoundry3** (the claims
check's `fma-fp32-*` files: every SPARSITY line read as json.loads reads it, and with each file's own command line); the runtime line at
every byte offset of each file's first line, and two at once; **aifoundry3's real runtime text** (E192's stderr.txt, E193's
device-stderr.txt; E192's data directory holds no raw host stdout, its runs.jsonl being the reference runner's parsed records, so its
stderr.txt is what it gives) between the host's lines (read, counted as other text) and inside a host line (unreadable: fails safe); E193's X04 lines
and E189's ledger lines from aifoundry3; **the E78 heater's own real stdout** (a timed process, all 1,024 minions) with the kit's registered
heater command, and with its calibration line or a middle line lost (out of order: none written) or against another command's values
(unreadable); and the request's host form, which no card has ever printed, as stand-in lines in its printf form for the four train
commands and the four premise runs (every split read the same; a wrong label, a wrong mask, a missing key, a launch out of order, a lost
calibration line and unknown text each unreadable).

## 9. What the checker reads after the reduction (`check_e196.py`)

E196.md section 8's six checks with its readings (the ties against the published references and their half-widths; the MSK null's
interval; the held ladder's middle-step ratio; the read-backs' count, 108 at the full plan; cycles per op at 0.05; the trains' anchor drift
and the carry-over), and the "also reported" items (samples off 600 MHz, runs set aside and why, passes kept, dips, off-protocol runs,
`readback_gate` against the session's unchanged-host runs, unreadable host outputs, runtime lines dropped). A failed check removes no datum.
On the registration's own synthetic session in E196's form (arbitrary test values, the registered reduction unchanged) it ran end to end
(`logs/checks-e196.txt`); its readings there are of the synthetic values, never a forecast.

## 10. Card-minutes, the cap and the rest (registered; unchanged)

About 49 card-minutes (46-53) with six passes, a seventh adding about 6; the smoke's second set adds about 0.25 (E196.md 10). **Cap 60**
from the first card command: the port's DEADLINE (58 minutes) for block starts and the end-stop (59 minutes) for a block in flight; never
by killing a device process. The 40-minute rest before E196's first card command and after its end (the rest rule, step 9; E197's rest rule
reads E196's session log the same way). One session of ours at a time on aifoundry3.

## 11. Files, the lists and step 2

| file | what |
|---|---|
| `session_e196.sh` | the session's wrapper on the box (section 1) |
| `run_session_e196.sh`, `run_block_e196.py` | the lab port of the proposal's `run_session.sh` and `run_block.py` (section 1; their diffs in `desk/port-diff-*-e196.txt`) |
| `stops_e196.py` | the lab's live stops on aifoundry3 and the end-stop |
| `e196_lines.py` | the host-line reader (runtime lines dropped, every host line verified) |
| `preflight_e196.sh` | dmcmd_audit on the session's files |
| `drycheck_e196.py` | the dry listing's reader, line for line against the registered commands and orders |
| `build_e196.sh`, `boxcheck_e196.sh`, `boxfiles-e196.txt` | the builds on the box, the box's tools and pins, the sync list (45 paths) |
| `collect_e196.py`, `check_e196.py` | the collection's desk half; the section 8 checker |
| `rb/` | the runbook's steps, the rest rule, the history check, the dry listing, the runbook's and the rest rule's desk tests |
| `desk/desktest_realpath_e196.sh`, `desk/realpath_e196.py`, `desk/standin_e196.py`, `desk/dry-branches-e196.tsv` | the real-path desk test, its stand-ins and its audit table |
| `desk/realbytes_e196.py` | the real-bytes test |
| `desk/host-change-e196.txt`, `desk/port-diff-run_block-e196.txt`, `desk/port-diff-run_session-e196.txt` | the host change, audited; the port's diffs |
| `KIT.md`, `CARD-LANE-BRIEF.md`, `DATA-README-FORM-e196.md` | this file; the card lane's brief; the data README's form |
| `SHA256SUMS-e196-kit` | every kit file but itself and step 2 |
| `SHA256SUMS-e196-shared` | the 17 shared files the box receives (the audit and its table, E128's guard, the lab's sparsity workload's nine build files, the five lab tiles), at their sha256 |
| `logs/*.txt` | the desk tests' logs (local paths and the login masked) |

**Step 2 (`rb/s03_desk_e196.sh`) is outside `SHA256SUMS-e196-kit`** (a file cannot hold the sha256 of a list that holds its own): its own
sha256 and the list's are given in the land file's anchor lines.

## 12. reg-e196's findings and open items, answered

| reg-e196 | what | here |
|---|---|---|
| finding 1 (medium) | the unchanged host breaks reduce_x14.py's read-back gate | the registered `reduce_e196.py --readback-none-ok`, run unchanged by step 13; the port writes `"readback": "none"` on every lab-host launch and on no other (P3; the real-path case P checks every record; P16 runs the reduction on the real path's files) |
| finding 2 (medium) | the reference runner cannot run E196's passes | the lab port (section 1) |
| finding 3 (low) | no read-back on the pass runs | registered (E196.md 14); the kit adds K1 (section 4), because the cycle gate it relied on is wider than the step |
| finding 4 (low) | host binaries' sha256 per build | step 6 records the box's; the session checks both hosts against today's record; the gate is both kernels' `.text` |
| finding 5 (low) | `"$ETTELEM"` unresolved in the proposal's run_session.sh | the kit's audit resolves it to E128's guard: GO, every site a READ (section 6) |
| open: both builds on aifoundry3, .text checked | | `build_e196.sh` (section 2), run for real in the runbook's desk test |
| open: the runner and a real-path test with split lines | | sections 1, 7 and 8 |
| open: the lab's choices to read | | stated in E196.md and section 4; for the verifier |

## 13. What the desk cannot show (for the verifier and the readiness critic)

1. **The hosts on the card**: the desk ran the real built hosts only to their refusals before the device layer; their launches, their
   SPARSITY and X14 lines and the runtime's prints on aifoundry3 meet the card first in the smoke (the smoke gate and K1 read them).
2. **The box's builds**: step 6 there, against aifoundry3's own /opt/et (its riscv gcc reports another version string): the ELFs will differ
   as files; the gate is both kernels' `.text`, which the lab's three toolchains have generated identically (E196.md 14), not yet read there.
3. **The box's sampler, holder check and runtime**: the real `build/ettelem/ettelem`, `et-who` and the runtime meet the port first on the
   day (step 7 reads the configuration through the same guard before).
4. **Another user's device process**: the ps rule for other users cannot be made at the desk (no other user's process can be started).
5. **The collection and the reduction** ran on stand-in sessions (the real-path test's and the runbook test's), not on a card's.
6. **Our own live collector on aifoundry3** holds the management node a few milliseconds of each second while the card is free; a single
   `et-who --check` that catches it reads "held" (the wrapper's free check then refuses with "no device opened"; the same-day rule allows
   one more launch); the opening configuration read or the sampler's start could meet it as a busy node (E192's and E193's readiness
   estimate about 0.4-0.5 % an open, not measured): a gate stop after the card opened, so no second try that day.
7. **The stand-ins' names**: the desk tests place shell stand-ins at the hosts' and the sampler's real paths; each execs Python at once, so
   for its first milliseconds its process name is the real tool's. Every desk test waited for THE QUIET DESK FLAG to be absent (no card
   session of ours on aifoundry2's own card) before it started; the residual is that window inside a test.

## 14. Findings for the verifier (desk checks of code)

| # | severity | what | here |
|---|---|---|---|
| 1 | medium | **E196.md section 14's stand-in for the passes' missing read-back does not hold as a gate.** It says every pass run's cycles per op are gated and that "a mask that did not act reads 546"; but the registered tolerance (within 0.5 % of 544 or 546) is 2.72 cycles at 544, wider than the 2-cycle step, so a masked run at 546.0 passes it (the real-path case G2 runs this). The premise runs check the mask on the request's host only; a fault on the lab host's mask path would not be seen | the kit's stop K1 in the smoke (0.5 cycles, both hosts' sets: section 4) catches it before any train or pass; check 5 (0.05 cycles) reports any pass run off its count; the reduction's 0.5 % gate is registered and unchanged. For the verifier: is K1 within 17.2's "stops that end a session early", and is a dated note to E196.md 14 wanted? |
| 2 | low | The smoke's heater ceiling (70 W) sits above the lab's 65 W stop, so with the lab's stops running it cannot be the first to act (case HC: the 65 W stop writes STOP, then the ceiling ends the block with exit 9) | both end the session before any smoke arm, as E196.md 11 says; the data README names which stop acted |
| 3 | low | The port draws the order on "aifoundry3" (P5), where the proposal draws on the host's name | on aifoundry3 the two strings are equal and the session refuses any other host; the registered order (desk/order-e196-aifoundry3.txt) is what both give; drycheck checks the listing against it |
| 4 | note | The dry listing has 255 device calls, not section 16's 251: the smoke's registered second set (four runs on the lab's host) | 237 with the cut order (233 + 4) |
| 5 | note | No card has printed an X14 line: the request's host's lines are tested only as stand-ins in its printf form (RB7, the real-path stand-ins) | the smoke reads the first real ones (the premise runs and two T1 processes) under its gate and K1 before any train |
| 6 | note | The rest rule reads E195's session log as `build/e195/T<T0>/session.log`, the form E195's kit (in progress, read from its lane's clone) writes | the rule reads every `build/e*/T*/session.log`; the rest-rule test's R7 and R8 use E195's form |
| 7 | note | The same-day rule, the relaunch after "no device opened", the unreadable-output rule and the end-stop are the kit's readings | section 4; for the go to confirm or refuse |

## 15. Labels, and compute

Every figure quoted from E196.md (the arms, the cap, the stops, the rests, the pins) is **registered**. The desk tests' results are **desk
checks of code**, not measurements; every watt and degree in them is a stand-in's arbitrary test value, not a forecast and not a measurement.
Nothing here is blind, held out or post hoc; no E196 datum exists. Compute: on aifoundry2 through the round's CPU slot at nice 10, every
logged desk test inside the no-device sandbox (the five fast logs, the dry listing, the preflight, the real-bytes test, the checks and the
rest rule's test, from their run g4 at 17:56:10-17:56:12 PST, after the rest read before step 7 was added and with step 2's pin at 46
entries; their earlier run f2 at 17:03, in the CPU slot only and before step 2's pin was written, read the same but for the new step); the
real builds in the runbook's desk test with `-j4`; the real-path desk test at real timing (43.5 minutes of wall time for the logged run f2, 16:39:44-17:23:14 PST, its P case 18 minutes; the development run d1 the same; a quick subset q1 of 32 checks before it, never a logged result); the runbook test 4.4 minutes (g2; the earlier f2, 22 cases, the same), its real builds about 20 s; no simulator, no other box, no card. **Q191's fix pass** (lane `fix-e196`) ran every logged desk test again on the fixed kit's bytes, one CPU-slot job at a time, each inside the no-device sandbox with the quiet-desk flag absent: the fast tests (run v3, 2026-11-16 01:59:36 PST), the real-path test (run v3, Mon 16 Nov 01:05-01:59 PST, with case L2; a development run of L2 alone before it, never a logged result), the runbook test (run v1, Mon 16 Nov 01:00-01:05 PST; it refuses to start after 22:30 Pacific, so it ran after midnight) and the rest rule's test (run v1, 2026-11-16 01:59:35 PST); section 16.

## 16. Q191's fix pass (lane `fix-e196`): verify-e196's findings answered before the land

*Sun 15 Nov 2026 from 23:04 PST to Mon 16 Nov 2026, on aifoundry2, desk only, before any E196 datum, on GitHub main `d5beec9b` (Q188's
guards: new files only, none under a path E196 reads). The registration's verifier, verify-e196, read DOES NOT HOLD for one reason, the
seal; every other check it made held. Each finding is answered here or in E196.md, and every desk test whose log step 2 reads ran again
on the fixed kit's bytes (the table above). Nothing here changes an arm, a value, the order, a train, a window, a threshold, a host
assignment, a stop, the cap, a rest or the reduction.*

| # | verify-e196's finding | the answer |
|---|---|---|
| 1 | medium: the seal. request.md's lines 233-249 (section 5's table, its column "expected (top-down)") and 251 were committed byte for byte | E196.md's redaction R1 (its section 0): the 54 numbers of those lines withheld under a dated header at line 232, the received file registered by its sha256 `88ddd2b4...`, the withheld lines by theirs; the registration's list re-made (`467ede78...`, 49 entries) and its subtree (`6f692709...`); every pin of them here moved (`session_e196.sh`, `boxcheck_e196.sh`, `rb/rb_e196.sh`, `rb/s03_desk_e196.sh`, `rb/check_history_e196.py`, the brief and this file); the kit's list, step 2's KITPIN and the logs re-made |
| 2 | minor: E196.md 14 said the pass runs' cycle gate catches a mask that did not act | E196.md's dated note 1: the gate is 2.72 cycles wide; K1 (section 4) and the checker's check 5 stand in; no rule, gate or datum changes |
| 3 | nit: the heater labelled as quoted | E196.md's dated note 2: the lab's choice, and why (the passes' frame on the unchanged host; E78 and E192 on this card; the lab host refuses the request's heater arguments) |
| 4 | nit: "E189's and E193's form" for the window | E196.md's dated note 3: E193's form; the window stays G + 1:30 / G + 3:00 (the brief's step 1 already named G + 3:00) |
| 5 | nit: "no firmware-revisions query" read as a rule | E196.md's dated note 4: by E196's choice, after the owner's rulings that reads are allowed; its device commands unchanged |
| 6 | nit: no desk test of the wrapper's ending after data when a later block finds the card lock busy (exit 75) | the real-path test's new case L2 (section 7's table): the lock taken in the gap after pass 0; L2 and L2b PASS |
| 7 | nit: the brief's steps 1 and 2 did not name the undesk on their failure paths | the brief's two rows: `W/onelab.sh undesk <lane>`, then E |
| 8 | note, for ready-e196 | no kit change: ready-e196 re-reads E195's landed session-log form before E196's day; Q188's guards add files only (step 2 reads HISTORY OK on `d5beec9b`); the card lane writes Monday's go basis into the data README's go placeholder |

SPDX-License-Identifier: Apache-2.0
