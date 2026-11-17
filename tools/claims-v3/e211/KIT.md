# E211's run kit: the second kernel on aifoundry3 card 0 from aifoundry2, in E206's kit form (its arm A, which ran FULL on this card) as E207's kit ported it to one arm: one runner with one sampler and the stop lines live, the two kernels built on the box through their gates, THE IDENTITY GATE PER PROCESS, THE WALK CHECK and THE KERNEL STOPS, the smoke (one process of each arm family) and then the stop-path test, every run under a plain `timeout 10` and never killed; the never-run search repeated right before the first card command; rgm211 built on aifoundry3 and checked under the simulator there (Q204; kitted, not run)

*Tue 17 Nov 2026 (week 47), PST, on aifoundry2, desk only (Q204, lane `kit-e211`). No card was claimed or opened: aifoundry2 has a card, so every
desk test that runs a built host, the runner, a stand-in session or a stand-in reader ran inside the round's slots and its sandbox (no /dev/et*,
an empty /run/lock). No device command was sent, nothing was posted. One box was reached: **aifoundry3**, only while no lane booked it (`book.sh
show` read before every call), for: one read-only look (00:23 PST); the build of rgm136 and rgm211 in a folder of ours (00:25 PST); THE KERNEL
CHECK, eleven simulator runs one at a time (00:25-00:34 PST); and the kit's own `build_e211.sh` run there in a tree of ours (01:14 PST). Nothing
was written on aifoundry3 outside `~/claude/work/q204-kit-e211`, and no device was opened there (every host run sat in a sandbox with no device
node). New files only, all under `tools/claims-v3/e211/`, on top of E211's registration ([`E211.md`](E211.md), reg-e211's local commit applied as
a local commit; at the kit lane: its `tools/claims-v3/e211` subtree `c27487b7...`, `SHA256SUMS-e211-registration` `7c11c733...`, 37 entries), which
this kit changes in no byte. **No E211 datum exists. Nothing here changes a forecast, a band, a rule, a threshold, the order, the card time, the cap,
a stop or the scorer.** Where E211.md leaves a reading to the kit, the reading is stated in section 4 before any datum. E207's kit (Q199) was not
landed when this was written; its bytes were the starting point for the one-arm port and E206's landed kit (`906699ea`) is the authority every
behaviour below is checked against.*

*Fixed before the land (Q204's lane `fix-e211`, Tue 17 Nov 2026 from 02:59 PST, before any E211 datum), for verify-e211 (HOLDS WITH FIXES,
02:53 PST): the registration under this kit is now reg-e211's with E211.md's **Amendment A1** (its `tools/claims-v3/e211` subtree `fa109d01...`;
`SHA256SUMS-e211-registration` `477fb113...`, 38 entries; the forecasts unchanged, `forecast-e211.json` `90e8d1ae...`), and the kit is re-pinned
to it; THE DESK FINDING below is corrected; step 2 refuses while no E207 data folder is at HEAD; the brief's queue row lost its exception; the
runbook's desk test gained case E7; every desk test was re-run (section FIXED BEFORE THE LAND).*

**His words** (Mon 16 Nov 2026, received at or before 09:48:24 PST; a voice transcription in which "matte mold" is the matmul and "FME" the
tensor unit's multiply-add): "I want you to focus on the matte mold most of all, so I want to have a model which predicts matte mold energy and
number of transistor switches and clock cycles. From based on what I know about the size of a matrix and which operations are contained. See
check how well the timing simulation for the matte mold matches reality and the energy. So I basically I don't care about going deep onto other
operations for now, just go as far as possible on the matte mold, on the FME, yeah, on the matmul operation."

## Results first (desk checks of code, desk reads of committed records, and desk runs on aifoundry3's host CPU; nothing is measured on a card)

| check | result | log |
|---|---|---|
| **the build on aifoundry3** (a folder of ours, nice 10, -j2; the box's riscv gcc "(g1b306039a) 15.1.0") | **rgm211: `.text` `82c7980716a0...` and loadable identity `1351a569e4a2...`, both equal to the registration's pins** (whole ELF `70c066e8...`, not the desk build's `00402801...`: the string in `.comment`, a section the card never loads); rgm136: `.text` `61315bf6...`, identity `649d4079...` (E206's pins); THE IDENTITY GATE per arm family both ways: gemmL, gemmLn and gemmLnc OK on their own ELFs, the three other pairings FAILED (6 of 6 as stated) | [`logs/a3-build-e211.txt`](logs/a3-build-e211.txt) |
| **THE KERNEL CHECK under sys_emu on aifoundry3** (shire mask 0x1, 32 minions; the host with --sysemu in a sandbox with no device node, prlimit 4 GB, nice 19, a plain timeout 1500; one run at a time) | **SIMCHECK-E211 7 of 7 AS STATED**: gemmLn2x2x1 fp32 and int8, gemmLn1x2x1 and gemmLn2x1x1 (family X), gemmLnc2x2x1 (rgm211's host on rgm136's ELF), gemmL2x2x1 (rgm136's host), each rc 0, its check of C approx (fp32) or exact (int8) over 8,192 words, the walk nm (tag on 32 of 32 harts) or mn (tag on none), walk_ok true, walk_launches_bad 0; **gemmLn on rgm136's ELF: rc 1, walk_ok false, walk_launches_bad 1** (the wrong ELF refused by the walk tag); 34-36 s and under 200 MB each | [`logs/simcheck-e211.txt`](logs/simcheck-e211.txt), `logs/simcheck/` |
| **the kit's own build script on aifoundry3** (`build_e211.sh`, in a tree of ours holding the harness's files) | **RGM-BUILT rc=0: both kernels KERNEL OK by the loadable identity (rgm136 ELF ff2723b8..., rgm211 ELF 70c066e8..., the same as the first build), 12 of 12 host refusals before the device stage in the box's sandbox, HARNESS OK, both self-checks PASS, dmcmd_audit: GO (11 send site(s), 0 disallowed; allow-list: none) on the box (01:14:43-01:14:50 PST)** | [`logs/a3-boxbuild-e211.txt`](logs/a3-boxbuild-e211.txt) |
| **the runner on the doubles** (`selftest_run_e211.py`): the short path with the identity gate and read; the smoke (s01 gemmL, s02 gemmLn, s03 gemmLnc, each gated, each at MM1's counter-mean forecast, the walk on s02 and s03) and THEN the stop-path test; every config gate, holder, sampler fault and stop line of E206's; the STOP file, a deaf sampler, card 1's runtime line, HUNG with nothing killed; **E211's own: the identity gate refusing the smoke's s02 (the smoke gate) and run 006 (STOP; through the reducer and the frozen scorer R0 FAIL), the walk check failing in the smoke and in run 004 (THE KERNEL STOPS; R0 FAIL), a check wrong, a launch timeout (rc 124) and a tensor error in gemmLn and gemmLnc runs (THE KERNEL STOPS), a gemmL crash only flagged, two gemmL failures in a row (runs 011 and 012) stopping, family C's six runs on their hosts and ELFs**; THE ORDER (38 runs, every key, argv and gate the registered); END TO END twice through the reducer and the FROZEN scorer | **SELFTEST-RUN-E211 60 of 60 PASS** | [`logs/selftest-run-e211.txt`](logs/selftest-run-e211.txt) |
| **the REAL path** (`desk/realpath_e211.py`, `desk/realpath_e211.sh`): run_e211.py WITHOUT --dry under aifoundry3's hostname (a private UTS namespace) and a private PID namespace, stand-ins for the reader behind the REAL guard, et-who, the two hosts, the lock and the nodes; **the two REAL kernel ELFs from the REAL build_e211.sh**, so the identity gate per process reads real ELFs: the box check (both kernel gates, harness, preflight), the lock, et-who and ps, the card's identity gate and read, the smoke, the stop-path test, three runs; a host hung past its TERM under the real `timeout 10` (left, ending by itself); rgm211's `.text` changed (refused); ET_DEVICES; the other card three ways; runtime lines; a sampler death; the STOP file; **rgm136's real ELF copied over rgm211's after the smoke: run 004's gate FAILED, no process, the session stopped**; the gate in process on the real ELFs both ways; the walk check on the real path | **REALPATH-E211 16 of 16 PASS** | [`logs/realpath-e211.txt`](logs/realpath-e211.txt) |
| **the parsers on real committed bytes** (`desk/realbytes_e211.py`): E206 arm A's 244 committed rgm136 stdouts on this card; its 241 runs through reduce_e211's per-run readings against E206's committed data-e206.json field for field; E190's 174 stdouts and 12 card-1 bursts; runtime lines spliced at every byte offset, single and nested; the split stdouts; the config line; the identity forms; **and rgm211's host's own real bytes (the kit's simulator stdouts): every record read against its own command line, the walk read by family (the wrong-ELF case NOT OK), runtime lines spliced into rgm211's records at every offset with the walk read the same** | **REALBYTES-E211 10 of 10 PASS** | [`logs/realbytes-e211.txt`](logs/realbytes-e211.txt) |
| **the build on this desk's real toolchain** (`desk/desktest_build_e211.sh`; riscv gcc "() 15.1.0", g++ 13.3.0, cmake 3.28.3): both kernels through their gates, the hosts' twelve refusals in the build's sandbox, other boxes refused, changed sources refused, aifoundry3's `.comment` form, a changed `.rodata` or `.text` byte, the wrong kernel each way, the runner's box check, the guard | **DESKTEST-BUILD-E211 10 of 10 PASS** | [`logs/desktest-build-e211.txt`](logs/desktest-build-e211.txt) |
| **the runbook** (`rb/selftest_rb_e211.sh`: a fake ssh and rsync, a stand-in aifoundry3, the real builds): the window rule, the lab-git lock, step 2 at every pin, the history check and a shadow, an E211 datum refusing step 2, **no E207 data folder at HEAD refusing step 2 (case E7, fix-e211)**, the look, ours_live, the sync, a login link, a hang, NO-THIRD-BUILD, **the real build of both kernels on the stand-in box**, **step 6n on stand-in roots (rgm211 found on a card in the lab's data and in another kit's box folder; E211's own folders, its design lane and the model session's left out by name; a simulator record named apart; the --desk-only form)**, step 7 refusing without a fresh 6n report or before the rest, the dry pass, THE HUNG MARKER, THE SAME-DAY RULE, the last start, the REAL session stopping at its box check, step 10's readings, the copy-back, the gate stop's record, a copy not exact, a session through step 12's data directory and step 13's frozen scorer | **SELFTEST-RB-E211 29 of 29 PASS** (fix-e211's re-run, with case E7; the test now runs itself in a private PID namespace) | [`logs/selftest-rb-e211.txt`](logs/selftest-rb-e211.txt) |
| the dry listing, every step with stand-ins | **dry listing: 15 steps listed, 0 exited non-zero, 0 box calls** | [`logs/dry-listing-e211.txt`](logs/dry-listing-e211.txt) |
| `dmcmd_audit_v2` on the session's files (`preflight_e211.sh`: the runner, its two modules, the wrapper, the build, the harness check, the guard, the registration's identity gate, both hosts' sources) | **dmcmd_audit: GO (11 send site(s), 0 disallowed; allow-list: none)**, every one a READ, no allow-list, no exception | [`logs/dmcmd-audit-e211.txt`](logs/dmcmd-audit-e211.txt) |
| the quick set | the two modules' self-checks, the harness re-made and at its sha256, the registration's seven checks and its scorer's stand-in self-test (byte-identical), its list, the preflight, the two aifoundry3 records, bash -n and a parse of every file; no call in the kit's code sends a kill (the lines naming one are prose, listed) | [`logs/checks-e211.txt`](logs/checks-e211.txt) |

## THE DESK FINDING: the simulator's step count is neither walk-blind nor ELF-blind (REPORTED; it changes no rule)

THE KERNEL CHECK's step counts (sys_emu steps: not time, and not instruction counts, as corrected below), mask 0x1, fp32, steps a minion an op
(`logs/simcheck-e211.txt`):

| ELF | its walk at 2x2x1 | at the controls' shapes 1x2x1 / 2x1x1 (one op stream) | the other walk in the same ELF | the non-cooperative branch |
|---|---:|---:|---:|---:|
| rgm136 (E136's) | 47.742 (gemmL, mn) | 48.047 / 48.219 | (none: it ignores the walk bit) | 40.566 (gemmLnc) |
| rgm211 (E211's) | 32.762 (gemmLn, nm) | 33.180 / 33.047 | 41.695 (gemmL's mn walk, simulator only) | 36.500 (simulator only) |

*Corrected by fix-e211 before any datum (verify-e211: the kit lane's text said "about 31% fewer instructions an op"; E211.md section 6 said
the count was walk-blind; both were wrong, and steps are not instructions. The simulator check's own log, `logs/simcheck-e211.txt`, is a
record kept as it was written, with the kit lane's first wording in its FINDING paragraph; this section corrects that wording).* E211.md section 6 said the instruction count is walk-blind ("the two
walks run the same loop body"). That holds for the source, not for the two compiled ELFs: the link-time inlining of both walks into
`entry_point` allocates registers differently. **The instruction counts are the static ones**, read from the desk builds' disassembly by
verify-e211: the steady-state cooperative loop runs **36 instructions an op in rgm136's gemmL** (2 of them stack loads, on the path from the
wait to the A and B loads), **35 in rgm211's own copy of gemmL's walk** (1 stack load) and **31 in rgm211's gemmLn** (none); after the wait the
FMA is the 6th, 6th and 9th instruction and the A load the 28th, 27th and 24th. **The table's sys_emu steps are not instruction counts**: they run
+10.6, +5.6 and +0.6 steps an op over the static counts, about 5 steps for each stack load, so the 31% that the steps' ratio (32.762 / 47.742)
suggests is not the instruction ratio (31 / 36, 14% fewer). The registration compares gemmLn on rgm211's ELF with gemmL on rgm136's ELF, so
**its controls x01 and x02 are not one instruction stream**. Whether the card's cycles follow these at 900-1,500 cycles an op, most of them
waiting on the tensor unit and the memory, is not known from the simulator, which is not timing; verify-e211's desk estimate of the code-path
offset at x01 is about -0.4% (instructions alone) to -1.5% (with the stack loads' latency), against T4's 1% bound. **The answer is in the
registration, E211.md Amendment A1 (made by fix-e211 before any datum):** T4 is unchanged; when T4 fails with both controls on one side and
within 0.005 of each other (their mean offset within 0.03), W1, W2 and H1-H3 are scored on the control-corrected ratios, the raw ones REPORTED
beside; the scorer also labels the timing simulation's column and reports the measured cycles over these steps for each point's own ELF and
walk. The kit's code is unchanged for it (the scorer reads the controls from the data the reducer already writes).

## FIXED BEFORE THE LAND (Q204's lane fix-e211, Tue 17 Nov 2026, before any E211 datum)

verify-e211 read the registration and this kit as HOLDS WITH FIXES (02:53 PST). fix-e211 answered its findings in a scratch clone of GitHub main
`f155c8ca` with both land patches applied (02:59 PST); the account's usage limit cut the lane at about 03:30 PST, and it resumed from its own
folder at 06:48 PST. The registration's part is E211.md's **Amendment A1**; nothing here or there changes a forecast, the points, the order, the
plan, the card time, the cap, a stop, a pin, a build or the harness (`harness-e211.json`, 41 files, unchanged).

| verify-e211's finding | the answer |
|---|---|
| (high) x01 and x02 compare two compiled loops (36 and 31 instructions an op), so T4 can fail on the code path alone | E211.md A1 clause 1: when T4 fails with both controls on one side of 0, within 0.005 of each other and their mean within 0.03, W1, W2 and H1-H3 are scored on the control-corrected ratios, the raw reading REPORTED beside (the registration's rules and scorer; the kit's code is unchanged: the scorer reads the controls from the data the reducer already writes) |
| (medium) the instruction-count text wrong both ways | THE DESK FINDING above corrected, its table header too; E211.md section 6; both commit messages; the simulator check's record `logs/simcheck-e211.txt` kept as written |
| (medium) the timing simulation's column is rgm136's law at rgm211's points | E211.md A1 clause 3: the scorer labels the column and reports beside it the measured wall cycles an op over the kit's sys_emu steps an op for the point's own ELF and walk (REPORTED) |
| (medium) this brief loosened the E207 gate, and no code enforced it | [`CARD-LANE-BRIEF.md`](CARD-LANE-BRIEF.md) row B lost "(or E207's chain stopped short of its card day)", and its section 1 and rows 2 and 13 say what to do; **step 2 refuses (16, the word E207-data) while no `docs/reports/data/*e207*` folder is at HEAD**; the runbook's desk test gained case E7 and a stand-in E207 data commit under every other case |
| (low) no Builds on section | E211.md section 12, with A1's own line |
| (low) stale wording | E211.md's header and sections 0 and 4 dated at the freeze; both commit messages |
| (low) R0's label not applied by the scorer | E211.md A1 clause 2: the scorer attaches it to every other rule |
| (low) the identity gate's objcopy to `/dev/stdout` inside the desk sandbox | not changed: it fails safe, and no user can unlink aifoundry3's `/dev/stdout` |
| (low) rgm211's host lets `-1`, `+2`, `' 2'` and MB 4096 reach the device stage | not changed: the registered order cannot produce them, and a change would re-make the host and the aifoundry3 records |
| (info) F1's "exactly"; the runbook test's benign "not uptodate" git lines | E211.md A1 clause 5; not changed |

**The pins.** The registration under this kit is reg-e211's with A1: its folder's tree `fa109d01...`, its list `SHA256SUMS-e211-registration`
`477fb113...`, 38 entries (the 37 registered at 00:14 PST and `power-a1-e211.json`). `rb/rb_e211.sh` and `rb/check_history_e211.py` pin the
tree; step 2's REGPIN pins the list, and its KITPIN this kit's list, re-made last.

**Found on the re-runs and fixed (the tests' own constants and their desk, never the kit's code):** the runbook test's case P2 expected the
37-entry list's "36 OK of 36" (`SELFTEST-RB-E211 28 of 29 FAIL` at the provisional kit commit); it now reads the count from the list. Its next run read 16 of 29: the
stand-in box is this desk, so ours_live (steps 5, 6, 10 and 11, case OL) read the desk's real process table, where another lane's desk test was
then running eleven `bash src/session_e209.sh` processes of the same account; the test now runs itself once in a private PID namespace (nested
bubblewrap, as `desk/realpath_e211.sh` does), where it sees only its own processes. Step 2's header and PASS line now read the registration
list's count from REGPIN.

**Every desk test re-run for real** (aifoundry2, `/usr/bin/python3` 3.12.3, one slot job at a time inside W/nodev.sh, the quiet-desk flag
absent; the logs in `logs/`): at the provisional kit commit, 06:55:03-07:14:21 PST: **SELFTEST-RUN-E211 60 of 60 PASS**, **REALPATH-E211 16 of 16 PASS**, **REALBYTES-E211 10 of 10 PASS**, **DESKTEST-BUILD-E211 10 of 10 PASS**; after the two test
fixes, 07:22:49-07:27:46 PST: **SELFTEST-RB-E211 29 of 29 PASS** (case E7 among them), **dry listing: 15 steps listed, 0 exited non-zero, 0 box calls**, **dmcmd_audit: GO (11 send site(s), 0 disallowed; allow-list: none)** (every send site a READ), and the quick set (both modules'
self-checks, the harness re-made CHECK PASS and HARNESS OK 41 files, the registration's seven checks, the scorer's stand-in self-test
byte-identical, the registration's list 38 of 38, `bash -n` and a parse of every file, no call that sends a kill). Not re-run: anything on
aifoundry3 (the build and THE KERNEL CHECK are the kit lane's records; aifoundry3 has been booked for E207's sealed-forecast hold since 03:02
PST, so this lane made no ssh call there).

## 1. The kit

- **The runner** ([`run_e211.py`](run_e211.py), [`session_e211.sh`](session_e211.sh), [`e211_common.py`](e211_common.py),
  [`e211_ident.py`](e211_ident.py)): the session on aifoundry3 card 0, E206's runner for its arm A (as E207's kit ported it), every behaviour
  E206's but: **THE TWO KERNELS AND HOSTS** (each process runs its point's own host and ELF: gemmL rgm136's host and ELF; gemmLn rgm211's;
  gemmLnc rgm211's host on rgm136's ELF); **THE IDENTITY GATE PER PROCESS** (`gate_of`: before every process the registration's own gate,
  `ident_e211.gate`, on the process's `--kernel` by its arm family; the words recorded with the process; a GATE FAILED starts no process and stops
  the session; in `--dry` the gate reads the ELF's path, and the real gate on real ELFs is the real-path test's); **THE WALK CHECK** (every
  rgm211-host process's records: walk nm for gemmLn, mn for gemmLnc, walk_ok true on every launch, the check line's walk_launches_bad 0);
  **THE KERNEL STOPS** (a gemmLn or gemmLnc process with a check of C wrong, a tensor error, the walk check failed, a launch timeout (K1 or rc
  124), a launch not ok, or an exit not 0 stops the session: nothing more that day); the smoke s01-s03 against MM1's counter-mean forecast
  (forecast-e211.json, R0's band); the order (38 runs); the card-time rule (no run after 30 card-minutes, the session ends at 35). Before
  anything opens: the host name aifoundry3, build/e211rgm's record today's BUILT by build_e211.sh on this box, both kernels through THE KERNEL
  GATE again, both hosts at the sha256 the build recorded, the reader at its pin, the two tiles at their manifest's sha256, the harness (HARNESS
  OK) and the preflight (dmcmd_audit_v2 GO). Then the card's lock (`flock -n`, held to the end), the holders (counts only), THE FIRST CARD
  COMMAND `ettelem config` through [`ettelem_guard_e211.sh`](ettelem_guard_e211.sh) under a plain `timeout 10` with its stderr kept (the start
  config and the card's identity gate; the card time counts from it), ONE sampler (10 Hz) whose every line feeds THE STOP LINES as it arrives,
  THE IDENTITY READ, the smoke and then the stop-path test, the registered order, the closing config, "session end", MANIFEST.sha256 last.
  Nothing is set. Every start first reads the operator's STOP file; never two samplers at once.
- **No SIGKILL anywhere** (W/out/orch/kill-rule.txt; AGENT.md "never kill -9"): every device process is under a plain `timeout 10`; the runner
  waits for it with a bound and, past `timeout`'s TERM by HANG_GRACE_S (4 s), writes "<time> HUNG: ..." in the session log, touches the stop
  file, starts nothing further, sends no further card command (no closing config read), closes the session and LEAVES the process (exit 8).
  et-who, the harness check and the preflight are waited on with a bound and left past it. The sampler is stopped by SIGTERM only. The build runs
  under a plain `timeout`. The one kill in the whole path is k6's bounded runner's (rb_run.py, unchanged, every kit's): past a call's bound it
  ends THE DESK'S OWN ssh client, rsync or collector; never a process on a box.
- **The build** ([`build_e211.sh`](build_e211.sh), [`check_e211.py`](check_e211.py)): E136's rgm136 unchanged into **build/e211rgm/rgm136** and
  E211's rgm211 into **build/e211rgm/rgm211** (new folders of ours) on aifoundry3; each kernel through THE KERNEL GATE (`check_e211.py --kernel
  rgm136|rgm211`: the registration's `ident_e211.gate` for the family that kernel serves alone: the `.text` always the pin, and the whole ELF the
  desk build's or its loadable identity the pin); the hosts by their behaviour: rgm136's four refusals and rgm211's eight (the four, and four of
  validateArm's early refusals), **each run inside a bubblewrap sandbox with no device node and each required to end before the device stage**
  (the runtime's "[RUNTIME]" line never printed: a refusal that did not refuse cannot reach a card); build/e211rgm/BUILD-e211.json.
- **The doubles** ([`fake_card_e211.py`](fake_card_e211.py)): E206's config, et-who, toy sampler and host, the host double now in two forms
  (`--as rgm136`: E136's records; `--as rgm211`: with the walk fields, the tag written only when a gemmLn arm runs an ELF from rgm211's build
  folder), driven by E211's frozen forecasts (MM1's seconds and watts; family C's C1 for gemmLnc); modes for every failure the tests need, among
  them a host that IGNORES its TERM, walk_ok false, a tensor error, and any mode limited to named points.
- **The reducer** ([`reduce_e211.py`](reduce_e211.py)): each run by E206's readings (reduce_e206's reduce_run, line for line, plus the counted
  launches' walk fields), written in the frozen scorer's form (score_e211.py's docstring: `{"arms": {"A": {"smoke": {"runs"}, "runs"}}}`, each
  RUN with its point, pair, walk and gate words; a process the gate refused kept as a run with its gate words and no check, so R0 reads it).
  **The collection** ([`collect_e211.py`](collect_e211.py)): COPY-BACK EXACT, the data directory (or a gate stop's record), the scrub, the
  reducer, step 6n's report, SHA256SUMS. **The harness** ([`check_e211.py`](check_e211.py), `harness-e211.json`, 41 files files) and **the
  preflight** ([`preflight_e211.sh`](preflight_e211.sh)).
- **The runbook** ([`rb/`](rb/)), from aifoundry2 through k6's drivers, unchanged: the window; step 2 (the pull under the lab-git lock, both
  lists pinned by count and bytes, the history check, the harness, the registration's checks and the scorer's self-test, the preflight, the desk
  tests' logs and the simulator check's; outside the kit's list); the look (k6's); the sync; the build; **step 6n, the never-run search
  repeated**; **step 7, only once the rest has opened and within 30 minutes of 6n**; the dry pass; the session; the wait; the copy-back; the data
  directory; the scorer after the data commit. **No post and no release** (waived). [`CARD-LANE-BRIEF.md`](CARD-LANE-BRIEF.md) is the card
  lane's brief, with THE ONE-LAB RULE and THE QUIET HOLD in its step table; [`DATA-README-FORM-e211.md`](DATA-README-FORM-e211.md) is the data
  README's form.

## 2. Card-minutes and the cap (registered; unchanged)

20.4 card-minutes planned (the smoke and 38 runs at E206 arm A's measured 21.96 s a run on this card, and 300 s of reads and gates;
plan-e211.txt); no run starts once the card time passes 30 minutes; at 35 the session ends after the run in progress; a started run is cut only
by a stop. The registered subset if cut: the smoke, family X and family W (35 processes); family C is then NO DATA.

## 3. The order on the box

The card lane's full table, with the queue, the booking, THE ONE-LAB RULE (desk / undesk around steps 0-2, collect / uncollect around step 11 to
the data commit's push), THE QUIET HOLD and the end of every path, is [`CARD-LANE-BRIEF.md`](CARD-LANE-BRIEF.md) section 2. The kit's steps:

| step | file | what |
|---|---|---|
| 1 | `rb/s02_window_e211.sh A <day> <last start> <last end>` | first; today only; the window (G = the booking) in its own RB_OUT |
| 2 | `rb/s03_desk_e211.sh A` (outside the kit's list) | the window; the pull under the lab-git lock; the registration and the kit found by content, ancestors of HEAD; the paths clean; HISTORY OK; both lists at their pins; the harness; both self-checks; the registration's checks (make_rgm211, kernel, ident, points, forecast, rules, plan) and the scorer's stand-in self-test byte-identical; the preflight; the desk tests' logs and the simulator check's; no E211 datum in any ref; **E207's data at HEAD** (fix-e211: a `docs/reports/data/*e207*` folder, else 16 with the word E207-data) |
| 4 | `../q141k-runbook/k6/s05_look_k6.sh aifoundry3` | k6's, unchanged (et-who, who, uptime, the holder rule); our login recorded for the scrub |
| 5 | `rb/s07_sync_e211.sh A` | the rsync into `~/aifoundry`; HARNESS OK on the box |
| 6 | `rb/s08_build_e211.sh A start`, then `wait` | the detached build of both kernels, NO-THIRD-BUILD, the record (both KERNEL OK), the harness, the preflight and both self-checks on the box |
| 6n | `E211_ROUND_OUT=<the round's OUT> rb/s06n_neverrun_e211.sh A [--desk-only]` | THE NEVER-RUN SEARCH, REPEATED right before the first card command (section 4 item 17); its NEVER-RUN-E211 line in RB_OUT |
| 7 | `rb/s09_reads_e211.sh A` | 6n's report under 30 minutes old, then THE REST RULE on the box, no card command (10 while either fails); then k6's step 7 unchanged (TDP 0 W / 65 C / 600 MHz, et-who clean) |
| 8 | `rb/s10_dry_e211.sh A start`, then `wait` | the runner on the box with its doubles, no device |
| 9 | `rb/s11_session_e211.sh A` | the last start (k6's), the cap before the last end, today's 6n report, k6's guard, THE REST RULE, THE HUNG MARKER, THE SAME-DAY RULE, today's dry pass and build, then `session_e211.sh` detached |
| 10 | `rb/s20_wait_e211.sh A` | the T0 the runbook launched; HUNG, K1, CRASHED and a gate stop are 16; ended (runner rc 0) 0; running 17 |
| 11 | `rb/s22_collect_e211.sh A` | one read-only copy back, COPY-BACK EXACT |
| 12 | `rb/s23_data_e211.sh A` | the data directory `docs/reports/data/<day>-e211-second-kernel-aifoundry3/` (or a gate stop's record under `docs/reports/gate-stops/`), the scrub, the reducer, step 6n's report, SHA256SUMS, the desk-path gate, the history check; then the card lane's README (and a dated note if rgm211 was found on a card before E211) and data commit |
| 13 | `rb/s24_score_e211.sh A` | after the data commit only: score_e211.py (registered with E211.md's Amendment A1, unchanged since) on the committed data-e211.json; its printed words end with A1's line (APPLIES or NOT APPLIED, and the basis of W1, W2, H1-H3) and, on an R0 FAIL, the R0 label line |

## 4. The readings stated here before any datum (where E211.md leaves a choice to the kit)

1. **THE DIE LINE'S "HOTTEST SENSOR" IS A LATCH** (E206.md amendment A1 item 1, which plan-e211.json adopts in words): the line trips on the
   shires' mean (`minshire[0]`) at or above 70 C, or on the latch (`minshire[2]`) only when it has risen during the session above the lowest
   value it read since the session's first sample and reads at or above 70 C. On aifoundry3 card 0 the latch read 87 C in every committed sample
   of E189, E195, E196, E197 and E206 arm A. `e211_common.Stops`, E206's line for line.
2. **The other stop lines** (plan-e211.json > stops): the board strictly above 70 W on 3 samples in a row that carry a board reading (a sample
   with none neither counts nor breaks the row: E206.md A1 item 2, adopted). A trip touches the host's `--stop-file` at once: the running host
   ends its loop at its next launch boundary (about 0.5 s; both hosts' own path, rgm136's proven on silicon by E146, rgm211's the same code),
   never killed; nothing further starts; the run's 4 s read and the closing follow. **The line** (65 W): no point's planning peak passes it
   (the self-check reads plan-e211.json: family C's C2 at 63.98 W, REPORTED, the highest).
3. **The smoke, then the stop-path test** (plan-e211.json "smoke"): 30 s at rest (the rest die: the median of the shires' mean over it; the die
   gate is formed from it), then one process each of s01 (gemmL2x2x2, rgm136), s02 (gemmLn2x2x2, rgm211) and s03 (gemmLnc2x2x2, rgm211's host on
   rgm136's ELF), **"one checked short process" read as E206's smoke form, `--seconds 2 --budget 3.5`**; each gated by its family first; each
   must exit 0 with every launch ok, its check of C exact or approx, **the walk check (s02 nm, s03 mn) and no kernel stop**, its cycles an op
   (the CHECK record's `cycles_per_op`, the counter's mean, as E190's and E206's smoke read it) within 50-250% of MM1's counter-mean forecast
   (forecast-e211.json > points > s0N > MM1 > cycles_per_op_mean: 788.1, 789.2 and 788.1, the number the frozen scorer's R0 reads), the board at
   least 2 W over the rest during its launches (at least 3 samples), and the host on card 0 (the watch); THEN the stop-path test on live samples.
   Any failure: the smoke gate failed, no run (a gate stop). **The reducer hands R0 the median over the smoke process's counted launches** (the
   scorer's RUN form) and keeps the check record's reading beside it (`check_cycles_per_op`). **Every arm family's first process on the card is
   short**: the smoke's three, before any 6 s run (the round's "every family's first run is short", read by arm family; families X, W and C of
   the order start only after the smoke passed).
4. **The start config** (plan-e211.json): TDP 0 W / 65 C / 600 MHz, read as found, nothing set; read again at the end (never after a HUNG, nor
   while the sampler would not stop).
5. **The card's identity**: `/dev/et0_mgmt`, physical device ID 0 on the config read's stderr; no minion_mv bound (a one-card box). The identity
   read with the sampler running; the host watch at every process (both hosts); a host naming or holding another card stops the session at once
   (in the smoke: the smoke gate). The box itself is told by its hostname (the box check, the guard and the build refuse every box but
   aifoundry3).
6. **The holders** (E206 arm A's): any holder line of another login, another user's device process, a CI job, any other device process of ours.
   **An unreadable et-who is a holder** (E202's fix). Counts only.
7. **The die gate**: min(60, rest die + 4) C, on a live sample (under 2 s old) only, waiting at most 300 s and never past the card-time rule or
   a stop; else that run is NO DATA.
8. **A run**: the die gate, the holders again (et-who and ps), 10 s at rest (p_rest = the median board W of its last 5 s), **the identity gate of
   its process**, ONE host process `timeout 10 <its host> <the point's registered host_args> --kernel <its ELF> --stop-file <STOP>`, a 4 s read.
   A live sampler before the process, else the run ends there flagged and the sampler is restarted (SIGTERM to a stale one); a stale sampler that
   will not stop on SIGTERM is left running, never killed, and the session stops.
9. **Failures, by arm family.** **gemmLn and gemmLnc (rgm211's host, a kernel never run on a card): THE KERNEL STOPS** (plan-e211.json lists
   "any check of C wrong, tensor_error, walk check failed (walk_ok false), launch timeout or identity gate failure in a gemmLn or gemmLnc process";
   **the kit reads a launch timeout as K1 or `timeout 10`'s rc 124, and adds a launch not ok and an exit not 0**, both of which on rgm211's host
   mean one of the listed causes or an unlisted fault: a reading stricter than the words, never looser): nothing more that day. **gemmL
   (rgm136, run FULL by E206 arm A on this card): E206's rules**: a failed process (rc not 0, rc 124 among them) is flagged; **two failed
   processes in a row stop the session**. **An identity gate failure before ANY process**, whatever its family, starts no process and stops the
   session (plan-e211.json names gemmLn and gemmLnc; the kit gates gemmL's twins too, since a wrong ELF there would be run as data). **K1** stops
   the session at once; **HUNG**: exit 8. A crash of the runner is named and exits 1, its closing run.
10. **Card time** counts from the start config read (the session's own first card command; step 7's read is reported apart). A run starts only
    if the card time is under 30 minutes and its longest length (28 s once its gate has passed) fits the 35-minute cap less 60 s of closing and
    ends 90 s before the window's last end.
11. **The reader**: aifoundry3's `build/ettelem/ettelem` (`16037641...`, E206's and E207's kits' read there), through one guard, `config` and
    `sample` only, ET_DEVICES unset, any other box refused.
12. **THE REST RULE** (E211.md 8): the first card command at least 40 minutes after our previous session on aifoundry3 ended. E206's rule (every
    session-log form of ours, the activity floor, the model session's folders `~/claude/work/ee-*/`), its floor now leaving out E211's own
    folders, so E206's, E207's and E210's count. Steps 7 and 9 read it on the box, step 7 BEFORE its config read.
13. **THE HUNG MARKER and THE SAME-DAY RULE** (E202's): step 9 refuses while any session log of ours on the box holds a HUNG line; an E211
    session that opened the card earlier that day refuses another; after sessions that opened no device, a third try refuses.
14. **The window**: step 9 launches only before the registered last start G + 1:30 (k6's `rb_need_start`) and with 2,400 s (the 35-minute cap
    and 5 minutes) before the last end (G + 3:30); the last start binds; the runner itself keeps every run inside the last end.
15. **The data directory**: `docs/reports/data/<day>-e211-second-kernel-aifoundry3/` with `session/`, `data-e211.json`, `reduce-e211.txt`, step
    6n's report (`neverrun-e211-card.txt`, `neverrun-e211-card.json`), SHA256SUMS and the README; a session in which no run started is a gate
    stop's record under `docs/reports/gate-stops/<day>-e211-second-kernel-T<T0>-aifoundry3/` (E202's form), never scored. Step 2 refuses on any
    E211 datum.
16. **The scrub**: the box's home becomes "~" and our own box login "<login>" in every text and .gz file; any /home/ path or the login left
    refuses the collection.
17. **THE NEVER-RUN SEARCH, REPEATED** (E211.md section 4: "The card lane re-checks the never-run list right before its first card command"):
    step 6n runs E206's scanner, unchanged (`95b290c0...`), over the registration's roots and aifoundry3's box tree: at the desk the lab clone at
    HEAD (but `tools/claims-v3/e211` and `tools/claims-v3/sealed-e211`, E211's own committed folders: plans, desk-test logs and the simulator
    check's record, never a run before E211), the round's lane folders (named by `E211_ROUND_OUT`; but every `<role>-e211[<suffix>]` folder and
    E211's two design lanes `mm-kernel2` and `critic-kernel2`, whose files the registration named plans, never runs) and HOME/claude/work (but
    the model session's `ee-*` folders: the round's rule since 23:18 PST Mon 16 Nov 2026); on aifoundry3 every folder of `~/aifoundry/build` but
    `e211` and `e211rgm` (E211's own), every folder of `~/claude/work` but `ee-*`, and `~/claude/et-soc1-prototyping/build`. **Folders are left
    out by name, whole** (simpler than E207's subtraction of counts; a folder left out is listed in the report). The scanner's own split of a
    record into a card record or a simulator record is read as it is: the kit's simulator check on aifoundry3 (`~/claude/work/q204-kit-e211`,
    records with "ghz" 0) is named apart, never a card run. **The judgement is the registration's** (desk/neverrun_e211.py's): rgm211's arms
    gemmLn and gemmLnc with a card record outside the folders left out ("rgm211 on a card before E211: none", or the keys and paths), and where
    each gemmL twin ran (E206 arm A's four twins in sample, E207's three expected once E207 has run). REPORTED, never a gate: rgm211 found on a
    card before E211 goes into a dated note before the data commit and to the orchestrator; the frozen scorer is never changed. Each call writes
    a new folder (`neverrun-<time>-<pid>`), so a report never reads an earlier call's scans. Step 7 refuses unless 6n ended within the last 30
    minutes. NOT SEARCHED, as registered: aifoundry1's own folders.
18. **The host's records** are read from a source no runtime print can split (e211_common's docstring); the runtime lines are removed pass after
    pass until none is left; **a runtime line naming another card than card 0** is an identity trip; card 0's own line is dropped and counted.
    **rgm211's host's walk fields** ride inside each record (`walk`, `walk_tagged`, `walk_ok`; the check line's `walk`, `walk_launches_bad`): a
    record is read whole or not at all, so a runtime line cannot split a walk field from its record (RB-SIM splices into rgm211's real records).
19. **No post, no release** (waived: the owner's words of Sun 15 Nov 2026, 10:22:36 PST). **The host's package counter is not read.**
20. **The sealed forecasts** (E211.md 0): a sealed sha256 the model session posts for E211's points before the first datum is registered in
    `tools/claims-v3/sealed-e211/e211-freeze-lines.md` before the card day; the card lane checks the round's record of them
    (`W/out/orch/sealed-e211.txt`) at its step 0.
21. **THE OPERATOR'S STOP FILE** (CARD-LANE-BRIEF 2): `touch build/e211/T<T0>-A/STOP` on the box is a registered stop: the running host ends at
    its next launch boundary (it reads the same file), and the runner reads the file before every start; a STOP file already in the session's
    folder when the runner starts is a refusal before any device, and the file is kept.
22. **The reducer's readings** (E211.md 7, the scorer's docstring): counted launches launch >= 0, ok, wall_s >= 0.1 s, a pass, the kernel clock in
    590-610 MHz; t_gemm = sum of wall / sum of passes; cycles a GEMM the median of cycles_max / passes; cycles an op the median of the host's
    cycles_per_op; p_work the median board W inside the counted launches; p_rest the median of the 5 s before the process; die_start the mean of
    the shires' mean then; mhz_min and mhz_max the lowest and the highest minion clock inside the counted launches; **walk: the walk and walk_ok of
    every counted launch and the last check line's walk_launches_bad (rgm211's host; null for rgm136's)**; **gate: the words the runner recorded**.
    Each run keyed by its point and by **its pair as the registered order gives it at its place n** (family C's twin runs, w01m at n 37 and w06m
    at n 40, belong to c01 and c02, the C block's pairs, not to their points' W pairs: the scorer's family C ratio reads the C block's own runs).
    E206 arm A's 241 committed runs reduce to E206's committed readings field for field (RB-E206R).
23. **The box build's host checks run in a sandbox** (a reading the kit adds to E206's build form): bubblewrap with a private /dev and an empty
    /run/lock, each check required to end before the device stage; a box without bubblewrap refuses the build (aifoundry3 has `/usr/bin/bwrap`:
    the look of 00:23 PST, and the kit's build ran there at 01:14 PST).

## 5. What E207's verifier found in the kit form this kit inherits, and what this kit does (verify-e207, HOLDS WITH FIXES, read 01:5x PST)

E207's kit (the one-arm port this kit started from) was verified while this kit was written. Each finding that touches the kit form, and its
answer here (the findings on E207's own registration are E207's):

| verify-e207's finding | here |
|---|---|
| (major) step 6n counted other experiments' desk-test doubles in the lane folders as runs | E211's step 6n judges only rgm211's arms (gemmLn, gemmLnc), which no other experiment's doubles print; E211's own lanes, its two design lanes and the model session's folders are left out by name, whole; the twins' records are REPORTED with their paths (a lane folder's record reads "a card, not known which"), never a gate |
| (medium) the "ran before" exclusion has no mechanism | rgm211 found on a card before E211 is REPORTED, a dated note and a word to the orchestrator; the frozen scorer is never changed; no rule is dropped by the kit |
| (medium) 6n read the model session's uncommitted session folders | E211's step 6n leaves out every `ee-*` folder, at the desk and on aifoundry3 |
| (minor) the runbook test's SD case failed between 00:00 and 00:45 PST | the stand-in log's last write is dated inside today at every hour (fix-e207's form); the rest rule reads its "session end" line |
| (minor) R0 could not see a run with no check of C | E211's frozen scorer reads a missing check as "missing" (R0 FAIL); the reducer writes `checks: []` for such a run, and for a process the gate refused |
| (minor) the brief's rows 11, 6n and 12; a STOP during the smoke named the cut process's board rise | rows 6n, 11 and 12 say what follows each bound (row 12 moves a failed collection out of LAB, so no untracked file blocks another lane's step H); a stop during the smoke is named first ("a stop during the smoke's s0N: ..."; desk case SS) |
| (note) the scorer crashed on a null smoke cycles an op | E211's frozen scorer reads it as outside the band (R0 FAIL), no crash |
| (note) 6n's lab scan read E207's own folder | E211's step 6n leaves out `tools/claims-v3/e211` and `sealed-e211` |

## 6. Files

| file | what |
|---|---|
| `e211_common.py` | the arm, the two builds' pins, the arm families' hosts and kernels, the walk check's reading and the kernel stops, the tiles, the frozen forecast's reading, the stop lines and the latch reading, the gate, the order, the argv, the counted launch, the host-records and config parsers; its self-check |
| `e211_ident.py` | the identity reads, the host watch, the board's rise, the sampler's freshness (E206's module, arm A); its self-check |
| `run_e211.py`, `session_e211.sh` | the runner (the identity gate per process, the walk check, the kernel stops) and its detached wrapper |
| `ettelem_guard_e211.sh` | the only way the runner reads a card: `config`, `sample --seconds --every-ms` |
| `build_e211.sh` | the box build of both kernels and its record |
| `check_e211.py`, `harness-e211.json` | every file a box runs or reads, at its sha256 (41 files); THE KERNEL GATE per kernel |
| `preflight_e211.sh` | dmcmd_audit_v2 on the session's files |
| `fake_card_e211.py` | the doubles (two host forms) |
| `reduce_e211.py` | the scorer's data form from a session |
| `collect_e211.py` | COPY-BACK EXACT; the data directory or the gate stop's record, the scrub, the reducer, step 6n's report, SHA256SUMS |
| `selftest_run_e211.py` | the runner's desk test, end to end through the frozen scorer |
| `desk/realpath_e211.py`, `desk/realpath_e211.sh` | the real-path desk test (real ELFs, the real gate per process) |
| `desk/realbytes_e211.py` | the parsers on real committed bytes and on rgm211's host's real simulator bytes |
| `desk/desktest_build_e211.sh` | the build's desk test on the real toolchain, with the kernel gate's cases |
| `desk/neverrun_card_e211.py` | step 6n's scans and judgement |
| `rb/` | the runbook's steps, its common file, the rest rule, the history check, the dry listing, its desk test |
| `CARD-LANE-BRIEF.md`, `DATA-README-FORM-e211.md` | the card lane's brief; the data README's form |
| `logs/` | every check above; `logs/simcheck/` the simulator stdouts (the home path written "~") with their command lines; `logs/a3-build-e211.txt`, `logs/a3-boxbuild-e211.txt` the aifoundry3 builds |
| `SHA256SUMS-e211-kit` | the kit's files (step 2, `rb/s03_desk_e211.sh`, aside: it pins this list), its logs |

## 7. Device commands

`preflight_e211.sh` (dmcmd_audit_v2, its table v2): **dmcmd_audit: GO (11 send site(s), 0 disallowed; allow-list: none)**, with no allow-list and no exception: `ettelem config` (GET_MODULE_STATIC_TDP_LEVEL,
GET_MODULE_TEMPERATURE_THRESHOLDS, GET_MODULE_POWER_STATE, GET_ASIC_FREQUENCIES, GET_ASIC_VOLTAGE) and `ettelem sample` (GET_MODULE_POWER,
GET_SP_STATS, GET_MODULE_CURRENT_TEMPERATURE, GET_ASIC_VOLTAGE, GET_MODULE_VOLTAGE, GET_ASIC_FREQUENCIES), each through the guard, which refuses
`--reset-ms` and every other word before the device opens. Both hosts open the ops node only (their sources are in the audit). Step 7 sends k6's
config read through E128's guard (the same five READs). No set, no reset, no statistics reset, no firmware query, no residency read, no drain
(`dev_mngt_service` is never run), no power cycle. The identity reads send nothing to a card: et-who stats the nodes, /proc is read for our own
processes only, and the identity gate per process reads ELF files.

## 8. What the desk cannot show

1. **rgm211 has never run on a card**, and the runner has met only its doubles and stand-ins: the live sampler, the card lock, et-who and the
   real hosts meet it first in the session. rgm211's host ran on aifoundry3's CPU under sys_emu only (seven cases as stated, four diagnostics),
   at shire mask 0x1 and small shapes; its full-chip launches (1,024 minions, 6 s processes) and its stop-file path on silicon are first seen in
   the smoke (rgm136's: E146).
2. **The simulator is not timing** (mm-timing, Q198): THE KERNEL CHECK shows rgm211 computes C right, writes its walk tag and is refused on the
   wrong ELF; it says nothing of cycles or watts. Its step counts are THE DESK FINDING above (REPORTED).
3. **The never-run search was not run on the real roots by this lane** (it is step 6n's, right before the first card command, when E207's twins
   will have run); its tool ran on stand-in roots in the runbook's desk test. This lane's own folders hold E211's arms by the thousand (the
   doubles' records): the search leaves them out by name.
4. **The latch reading** rests on committed telemetry; the session's own first samples show the latch it starts from.
5. Card time waits on the queue (E207's data commit, E210), the rest, the day, the booking and a readiness lane's go lines (CARD-LANE-BRIEF.md).

## 9. Labels

Every figure quoted from E211.md and its files (the forecasts, the order, the caps, the stops, the gates, the pins) is **registered**. The desk
tests' results are **desk checks of code**, not measurements; the end-to-end joules and the scorer's words come from the doubles (E211's frozen
forecasts driven through a toy card): not a measurement and not a reading of E211. The committed reads the kit cites (the latches, the identity
blocks, E190's and E206's outputs) are **desk reads of committed records**. The aifoundry3 build's identities and the simulator check's records
are **desk runs on aifoundry3's host CPU** (no device opened); the simulator's step counts are **not time**. Nothing here is **blind** or **held
out**, and no E211 datum exists. Python: `/usr/bin/python3` 3.12.3 at the desk, `/usr/bin/python3` 3.12.3 on aifoundry3.

## Compute

On aifoundry2 through the round's local slots (`slot.sh`, nice 10), one job at a time, each that runs a built host, the runner or a stand-in inside
the sandbox (W/nodev.sh; the real-path test in private UTS and PID namespaces): the runner's desk test, the real-path test (two real builds), the
build's test (four real builds), the runbook's test (one real build on its stand-in box), the real-bytes test, the dry listing; the final pass
ran once, one slot job inside the sandbox, 2026-11-17 01:47:13 PST to 2026-11-17 02:04:48 PST (final_tests.sh f2). **fix-e211's re-runs** (the same box and slots, each one slot job inside W/nodev.sh, the quiet-desk flag absent): every desk test, 06:55:03 to 07:14:21 PST (its f09_kittests.sh t2), and the runbook test, the dry listing, the preflight and the quick set again, 07:22:49 to 07:27:46 PST (f18_rbtests.sh t4). On aifoundry3, each only while no lane booked it: the build of both kernels (seconds, -j2, nice 10), eleven simulator runs (34-36 s each,
one at a time, nice 19, under 200 MB), the kit's own build script (seconds), a read-only look.

SPDX-License-Identifier: Apache-2.0
