# E183's kit, dated note 6 (Fri 13 Nov 2026, before any E183 train datum): the post-block check kept to the train blocks (block v3, queue v3, session v3), step 10 v2 for every session version, the real-path desk test and the audit of every branch the dry path skips, step 5b (the first session's smoke and stop test moved aside), steps 8 v3 and 9 v3, step 2 v7; its verifier's findings answered before the land; no rule, forecast, threshold, plan, cap, stop or reading changes

*Beside [KIT.md](KIT.md) and its dated notes 1-5 (`45e514e3`, `1e74546a`, `e8e9f4e1`, `24b9b99e`, `9ae55d39`); it edits nothing there, nor
in [E183.md](E183.md) or its notes. Written on aifoundry2, desk only, by the lane `kit-e183n6` of Q173, begun at about 13:30 PST Fri 13 Nov
2026 by the clock, and changed before the land by the lane `fix-n6` of Q173 (from about 15:00 PST) to answer its verifier; its commit's
own time is git's. No card was claimed, no device command was sent, no lab box was reached, nothing was
posted; every run of a built binary, runner or stand-in box went through the round's CPU slot and a no-device sandbox (aifoundry2 has a card
of its own), and each desk test makes its own sandbox inside that one (no `/dev/et*`, a private PID namespace). It answers E183's first
session of that day (`card-e183f`, Q170: aifoundry3 card 0, T0 1794604458, 13:14:18 PST): **it stopped at its smoke gate by a defect of this
kit before any train block** (1.0 card-minute; every rule NOT RUN), and step 10 read a false RUN-GONE while the smoke ran. **No E183 datum is
in the lab** (`git log --all` on `docs/reports/data/*e183*`: nothing). E183.md's dated amendment A1, committed with this note, allows a
second session that day; the card lane's brief's dated note 5 carries both out. Read before the land by the verifier `verify-n6` (holds
with fixes: 2 minor findings and 4 nits, none blocking); the lane `fix-n6` answered each one in these files before the land (section 15).*

## Results first (desk only; nothing is measured)

| check | result | file |
|---|---|---|
| **the fix**: block v3 runs the post-block check on a train block only (the smoke's check is its registered gate); queue v3 and session v3 run block v3; harness v3 and preflight v3 pin and audit the new box files; session v3 also refuses unless `USER` is the login (section 6) | five box files, each v2 with its marked lines | `block_e183_v3.sh`, `queue_e183_v3.sh`, `session_e183_v3.sh`, `preflight_e183_v3.sh`, `harness_e183_v3.py` |
| **THE REAL-PATH DESK TEST**: the session's real path, V3_DRY unset, a real GCC -O2 train host on the recording mock, stand-ins for every device tool; the negative control (session v2: the box's KeyError at the desk); every branch the dry path skips | **DESKTEST-REALPATH-E183 PASS, 22 of 22** | [`logs/desktest-realpath-e183.txt`](logs/desktest-realpath-e183.txt) |
| **step 10 v2** against a stand-in box, each name form running, step 10 v1 the negative control | **SELFTEST-WAIT-E183 PASS, 15 of 15** | [`logs/selftest-wait-e183.txt`](logs/selftest-wait-e183.txt) |
| **step 5b, the aside**, against a stand-in box | **SELFTEST-ASIDE-E183 PASS, 13 of 13** | [`logs/selftest-aside-e183.txt`](logs/selftest-aside-e183.txt) |
| **steps 8 v3 and 9 v3** and the dry listing v7 against a stand-in box: step 9 v3's launch path (case L) and the two gates added before the land (G5, G6) included | **SELFTEST-RB-E183-V4 PASS, 11 of 11** | [`logs/selftest-rb-e183-v4.txt`](logs/selftest-rb-e183-v4.txt) |
| the dry listing v7 | 13 steps, 0 exiting non-zero, no call | [`logs/dry-listing-e183-v7.txt`](logs/dry-listing-e183-v7.txt) |
| re-runs on aifoundry2 of note 4's desk tests on these bytes: the runbook desk test v3, the rest rule test, the train check on real builds | as stated in the log | [`logs/reruns-note6-e183.txt`](logs/reruns-note6-e183.txt) |

## 1. What stopped the first session

`block_e183_v2.sh` (note 4) ends every real block that reaches its end with the post-block check: line 128 runs
`check_e183.py block <dir> --card <card> --root <tree>` and lines 129-132 read its last line as the block's status. `check_e183.py`'s
`block()` (line 154) takes the block's train from `e183_common.train_of_block`, which raises at line 69 for any block outside 18310-18315.
The smoke (18301) reaches that line; the stop-path test (18302) does not, since its own lines (v2's 105-115) end the block before it (the first session's `e183-stoptest/p18302` holds no `check.err`). So every real smoke ended
`fail post-block check crashed: KeyError: 'block 18301 is not a planned train block (18310-18315)'` with rc 1, after its own gate had read
SMOKE GO, and session v2's gate (`[ "$rc" -ne 0 ]`) stopped the session. Under V3_DRY lines 124-126 replace the check by
`dry run (runner rc 0)`, and every desk test of notes 1-5 ran the smoke only under V3_DRY or with a stand-in block, so none could see it.
Block v1 (`cc597bf2`, line 120) has the same line.

## 2. What the post-block check is for, and the fix chosen

**What it is for.** `check_e183.py`'s docstring: "the post-block check: the anchors' bursts by ... `bursts_of` (E180's), and the train's
processes (13 launches each, every one ok, each launch's kind and image by the registered schedule); writes `<dir>/check.json` and prints
`<status> <note>`". Its record names the block's train, its anchors and its planned processes; the reduction v2 reports it beside, never as
a verdict (`reduce_e183_v2.py` line 17), and only for the train blocks it reduces. E183.md registers no post-block check at all: section 7
registers the smoke's **gate** (every burst at 600 MHz within 3% of the others' rate, both train processes 13 launches ok by the schedule),
and the kit's `check_e183.py smoke` is that gate, which the session runs right after the smoke's block. The check came from E180's block,
whose post-block check read any block's bursts; E183's port gave it a train's lines and kept calling it on the smoke.

**What it should do on the smoke and the stop-path test:** nothing. The smoke is read by its registered gate, which passed on the first
session; the stop-path test is read by its own lines (both stops must fire), which passed. Neither has a train.

**The fix: block v3 calls the post-block check on a train block only** (`block_e183_v3.sh`, its lines 141-147). On the smoke it runs no
check and writes the runner's status with the note
`smoke: no post-block check (check_e183.py block reads a train block only, note 6); its gate is check_e183.py smoke, run by the session next`;
a runner exit other than 0 still reads as v2 reads it (5 a stop, 4 the sampler, 7 no records, any other a failure). On a train block every
line is v2's. **Not chosen:** a v2 of the check with lines for the smoke and the stop-path test. Block v2 calls `check_e183.py` by its path,
so any fix needs a block v3 anyway; a check v2 would add Python and repeat the smoke's gate inside the block, where the registration names
only the gate. **Also new,** so that a session runs one block version and no real path sets a variable the dry pass alone may set:
`queue_e183_v3.sh` (queue v2 with block v3 as its default block; `E183_BLOCK` stays the dry pass's stub-test variable),
`session_e183_v3.sh` (session v2 with block v3, queue v3, the harness v3, the preflight v3, and the `USER` gate of section 6),
`preflight_e183_v3.sh` (v2's audited set with the four new box files) and `harness_e183_v3.py` with `harness-e183-v3.json` (made by
`make_harness_e183_v3.py`: note 4's harness file and check at their sha256, v2's check run unchanged, then note 6's five box files at
their pins: `HARNESS OK: 92 files`, 132 with the binaries). Block v3's preflight runs the harness v3. No rule, threshold, plan, cap or stop
changes, and no reading: the check reads a train block exactly as before.

## 3. The second defect: step 10 (`rb/s20_wait_e183_v2.sh`)

Step 10 v1 (`rb/s20_wait_e183.sh`, unchanged since `cc597bf2`) looks for the session's process with `pgrep -f "session_e183\.sh"`, which no
later session version matches; on Fri 13 Nov 2026, while session v2 ran its smoke, it read `RUN-GONE` (14) at 13:14:30, and only after the
session had ended did it read `RUN-ENDED` and `GATE-STOPPED` (16). **Step 10 v2** matches E183's session and its queue in every version,
`(session|queue)_e183(_v[0-9]+)?\.sh`; whether the session has ended is still read only from its own T0's log. Its desk test
([`rb/selftest_wait_e183.sh`](rb/selftest_wait_e183.sh)) runs the step whole against a stand-in box whose `pgrep` is the real one, in a
private PID namespace holding only the test's stand-in "sessions": W0 v1 with session v2 running reads RUN-GONE (14: the day's false
reading); W1-W7 v2 with each form running alone (session v2, v1, v3, v10; queue v1, v2, v3) reads RUN-RUNNING (17); W8 with only other
names running (another run's session, `session_e1830.sh`, a block) and W9 with nothing running read RUN-GONE (14); W10 after the session's
end RUN-ENDED (0); W11 after a gate line GATE-STOPPED (16); W12 the dry listing shows the new pattern and calls nothing; W13 v2 is v1 with
two lines changed. No desk test of the kit had run step 10 before.

## 4. THE REAL-PATH DESK TEST ([`desk/desktest_realpath_e183.sh`](desk/desktest_realpath_e183.sh))

**The lesson** (both E183 days lost to it): a check that runs only on the real path is never exercised by a desk test that runs the dry
path. This test runs **session v3's real path, V3_DRY unset**, at the desk:
- **the train host is a real build**: `build_host_e183_v2.sh` on its real path, with the kit's stand-in cmake (`rb/fake_cmake_gcc_e183.sh`,
  unchanged) compiling the patched `main.cpp` by g++-13 at -O2 against E184's desk stubs, with a `Constants.h` naming the stand-in tree's
  kernel (as the box's configure names its build tree's), linked with `desk/mock_runtime_e183_v2.cpp`: each launch sleeps 400 ms (the
  0.4 s window at 600 MHz), and every device-layer and runtime call is appended to a record, so the record counts the host processes that
  reached the device layer;
- **the device tools are stand-ins**: the telemetry reader `build/ettelem/ettelem` answers E128's guard's two words (`config` with the box's
  config line; `sample --seconds --every-ms` with 10 Hz lines in the box's form: board 30 W, `minshire[0]` 50 C, 600 MHz); the holder
  readers (`et-who`, and `sudo -n /usr/local/sbin/et-holders`, which D1's rule calls) answer "No process holds ..." and name the test's own
  card lock as its own; the card lock is the sandbox's own `/run/lock/etsoc-shire0.lock`; `timeout` and `flock` are the system's, behind
  stand-ins that log each call; ssh, scp and rsync refuse;
- **the sandbox**: the test re-executes itself in bubblewrap (a private `/dev` with no `/dev/et*`, a private `/run/lock`, a private PID
  namespace, the hostname aifoundry3) and refuses if any `/dev/et*` is visible;
- **one train block**: the operator's stop (`build/e183/STOP`) is written by the holder stand-in once block 18310 has begun, so the queue
  runs that block whole (its 4 anchors and 52 processes) and stops before 18311.

| case | what it shows | result |
|---|---|---|
| 0 | the sandbox; build v2's real path (BUILD OK, TRAIN-CHANGE OK, no device call); harness v3 with the binaries; preflight v3 GO | PASS |
| **N1** | **the negative control**: session v2 on the real path stops as aifoundry3 did: stop test rc 0, the smoke's gate SMOKE GO, block v2's check.err ending `KeyError: 'block 18301 is not a planned train block (18310-18315)'`, the smoke's block.json `fail` with that note, the gate line `smoke gate failed (stop test rc 0, smoke rc 1, gate 0): no train block runs`, no queue; the stop test has no check.err | PASS |
| N2 | the same smoke under V3_DRY: block v2 reads rc 0 (`dry run (runner rc 0)`) | PASS |
| W | without an aside: block v3's stop-path test rewrites the earlier `p18302` in place (V3_FORCE), and its smoke moves the earlier `p18301` to `p18301.attempt-<epoch>` inside `e183-smoke/` | PASS |
| **P1** | **session v3's real path**: `kit note 6`; `HARNESS OK: 132 files`; dmcmd_audit GO; the config read; stop test rc 0; smoke rc 0; SMOKE GO; `smoke gate passed: queue starts (plan FULL)`; `p18310 rc=0`; `STOP: stopping before p18311`; `done, 1 items`; `session end (T0 ...)` | PASS |
| P2 | block 18310's post-block check on the real path: `ok`, 52 of 52 processes good, 4 anchors, no train fault, 0 samples off 600 MHz; 676 train launch records | PASS |
| P3 | the smoke's block.json `ok` with note 6's note, no check.err, no check.json; the stop test fired both stops (board and die) | PASS |
| P4 | the real calls: 2 config reads under the card lock (`flock -n ... timeout 10 ... ettelem_guard.sh config`), 3 block locks, D1's holder read before every block, burst and process, 3 samplers at 10 Hz, 62 host runs under `timeout 10`, 62 device-layer opens (the smoke's 4 bursts and 2 processes, the block's 4 anchors and 52 processes); no dry log | PASS |
| A1 | D1's other-user rule: another user's holder line on card 0: block v3 exits 3 before anything, no device call | PASS |
| A2 | the card lock held by another process: block v3 exits 3 at lib.sh's lock | PASS |
| A3 | a live stop before the first burst (the board at 66 W): the block reads `stop`, `stop.json`, exit 5, no host run | PASS |
| A3b | a live stop during a launch (the board crosses 65 W inside the first anchor burst): the in-run watcher SIGTERMs the host, exit 5 | PASS |
| A4 | the sampler stalls: the runner exits 4 at its next check, the block reads `fail` ("the sampler stopped writing"), one anchor ran | PASS |
| A5 | the runner's own check of the registration's list: one registered file changed: the real runner exits 2 before any host run; under `--dry` it reads 0 | PASS |
| A6-A7 | the harness with the binaries: a changed host binary stops session v3 (9, `harness check failed: no device opened`) and block v3's preflight (2); without the binaries (the dry form) it passes | PASS |
| A8 | session v3's start gate on the real path (a past latest start): 8, the real log, no device opened | PASS |
| A9 | lib.sh's skip of a train block whose block.json exists (18310 again): `already done`, exit 0, no device call | PASS |
| A10 | D1 without `USER` (section 6): another user's holder passes (the runner's `--check-others` exits 0, against 3 with `USER` set); session v3's `USER` gate stops first (8, no device opened) | PASS |
| A11 | lib.sh's `ours_running`: a device process of ours left running (a stand-in named `ettelem`): block v3 exits 3 | PASS |
| Z | no process of the test left; no network call; no `/dev/et*` through the run | PASS |

## 5. The audit: every branch the dry path skips on the session's path, and the test that now runs it

Read on note 6's files (`session_e183_v3.sh`, `queue_e183_v3.sh`, `block_e183_v3.sh`) and on the files they run unchanged (`lib.sh`,
`others_d1_e180.sh`, `run_e183.py`, `check_e183.py`, `harness_e183_v2.py`/`_v3.py`, `preflight_e183_v3.sh`, `ettelem_guard.sh`,
`train_check_e183.sh`), by every `V3_DRY`, `--dry`/`a.dry`, `V3_FORCE` and dry-pass-only variable. "RP" is the real-path desk test.

| where | under the dry path | on the real path | run now by |
|---|---|---|---|
| session v3 line 53 | the log is `session-dry-t<T0>.log` | `session-t<T0>.log`, which steps 10 and 11 read | RP P1, P4, A8 |
| session v3 line 56 (`cfg`) | writes `{"dry":true}` | the config read under the card lock and `timeout 10`, through E128's guard | RP P1, P4 |
| session v3 line 72, block v3 line 74 | the harness without the binaries | with the binaries (BUILD-E183.json, the host, the kernel, the 38-file tree) | RP 0c, P1, A6, A7 |
| session v3 lines 89-94 (the gate, `check_e183.py smoke`) | not run | `check_e183.py smoke` | RP P1, N1 |
| session v3 line 99 | `queue-dry-t<T0>.out` | `queue-t<T0>.out` | RP P1 |
| session v3 line 71, the `USER` gate (new) | the same in both | refuses unless `USER` is the login | RP A10 |
| queue v3 lines 37-39 (`E183_SEQ`, `E183_BUDGET_S`, `E183_GAP_S`, `E183_RESERVE_S`, `E183_BLOCK`) | the dry pass's stub test sets them | their defaults: FULL's six blocks, 3,900 s, a 10 s gap, a 60 s reserve, block v3; the STOP file | RP P1 (the defaults; STOP) |
| block v3 line 59 (`E183_PROCESSES`) | the dry pass's short form | every process of the block | RP P2 (52 of 52) |
| block v3 lines 47-48 and 116 (`others_present`, `ours_running`) | lib.sh's stubs: nobody, nothing | D1's rule; our own device processes by `ps` | RP A1, A10, A11, P |
| block v3 lines 98-101 (`V3_FORCE`, the attempt rename) | the dry data root | the real data root, where an earlier smoke or stop test sits | RP W; step 5b (section 7); step 9 v3's data-root gate (section 8) |
| block v3 lines 130-134 | the runner with `--dry` | the runner launches the host | RP N1, P |
| block v3 lines 137-154 | `dry run (runner rc N)` | the post-block check (train blocks), the smoke's note, the stop, sampler and records exits | RP N1 (v2), P2, P3, A3, A3b, A4 |
| lib.sh line 181 | the dry data root | a train block whose block.json exists is skipped (`already done`, 0) | RP A9; step 9 v3's data-root gate |
| lib.sh line 184 | no card lock | `flock -n` on `/run/lock/etsoc-shire0.lock` | RP P4, A2 |
| lib.sh lines 204-214 | the dry data root; stubs of `hold10`, `die_c`, `clock_mhz`, `heat_to`, `drain_mgmt`, the sampler, `others_present`, `ours_running` | the real data root; `die_c` and `clock_mhz` through the guard; the 10 Hz sampler started and stopped by SIGTERM; D1; `ps` (`hold10` is not used by E183; `heat_to` only where the governor is free, not aifoundry3; block v3 refuses `drain_mgmt`) | RP P, P4, A1, A4, A11 |
| `others_d1_e180.sh` line 13 | D1 not defined | D1: other users' device processes by `ps`, and `sudo -n et-holders` lines on card 0 not of `$USER` | RP A1, A10, P4 |
| `run_e183.py` line 72 | the stop-path test returns 5 unread | both stops read on live samples, the watcher on a child | RP P3, N1 |
| `run_e183.py` line 164 | the registration's list not checked | refused (2) on any change | RP A5 |
| `run_e183.py` line 193 | sleeps printed | real leads and gaps | RP P (block 18310: 329 s) |
| `run_e183.py` line 199 | D1 never asked | D1 before every burst and process | RP P4, A10 |
| `run_e183.py` line 211 | no stall | the sampler's file must grow within 6 s | RP A4 |
| `run_e183.py` line 224 | no stop reading | the stops before every burst and process, and the in-run watcher | RP A3, A3b |
| `run_e183.py` lines 291, 313 | the host printed, not run | the host under `timeout 10`, its ENERCAT records, the marks | RP P, N1 |
| `check_e183.py block` and `smoke` | neither run | the post-block check (train blocks) and the smoke's gate | RP P1-P3, N1 |
| `rb/s11_a3_session_e183_v3.sh` lines 64-79 (step 9 v3's launch tail: the T0 file, `setsid nohup ... session_e183_v3.sh`, `LAUNCHED`, `t0-e183.txt`) | the listing prints the remote script and exits (line 73) | the launch | the runbook test v4's case L (verify-n6's case, carried into it before the land) |

Nothing else on the session's path branches on a dry flag: `preflight_e183_v3.sh`, `ettelem_guard.sh` and `train_check_e183.sh` run the
same in both, and the runbook's own `RB_DRY` is the listing mode, which every step's desk test runs beside its real form (sections 3, 7, 8).
The last row was the one real-path stretch no committed test ran when the verifier read this note (its finding 1): its case L ran it, and
it is now case L of `rb/selftest_rb_e183_v4.sh`.

## 6. `USER`, found by the real-path test

D1's other-user rule (`others_d1_e180.sh`, E180's, unchanged) keeps the holder lines whose user is not `$USER`, inside a command
substitution, under lib.sh's `set -u`. With `USER` unset that substitution fails, the holder list reads empty, and **another user's holder
line on card 0 passes** (fail open). The real-path test's own sandbox had no `USER` at first (this lane's shell on aifoundry2 has none; `LOGNAME` is set): every D1
call printed `USER: unbound variable` and its case A1 ran a block it should have refused. On aifoundry3 the session inherits `USER` from the
ssh login that launches it (step 9), and the first session's log holds no such line, so D1 read correctly there. KIT.md's open item 7 named
the dependence; nothing guarded it. **Session v3 now refuses (8, no device opened) unless `USER` is the login** (`id -un`), after its time
gates and before its harness; the test sets `USER` as the box's login does, and case A10 shows both the fail-open read and the gate.

**The same dependence outside E183** (the verifier's finding 2, added before the land): D1's rule is also sourced by E180's and E184's
blocks and runners, and the lab's stock `others_present` (`lib.sh` line 64, the rule a host with one card reads) keeps the logins that are
not `$USER` inside a command substitution under `set -u` in the same way: in the verifier's desk probe another user's login blocked the
start with `USER` set and read "would start" without it. Session v3's gate guards E183's sessions only. The verifier read E190's runner as
taking the login from its working directory and reaching its box over ssh, so E190's arm A is not exposed. **Carried forward:** any later
kit that sources either rule (E184's arms S and B among them) gets session v3's `USER` gate, or one like it, before its card day. Nothing
in E180's, E184's or the lab's files changes here.

## 7. Step 5b, NEW: the aside ([`rb/s06b_a3_aside_e183.sh`](rb/s06b_a3_aside_e183.sh))

**Why.** On aifoundry3 the first session left `build/claims-v3/aifoundry3/e183-smoke/p18301` and `e183-stoptest/p18302`, each with its
block.json. Block v2 and v3 move an earlier smoke to `p18301.attempt-<epoch>` inside `e183-smoke/`, write a new stop-path test into an earlier
`p18302` in place (V3_FORCE), and lib.sh skips a train block whose block.json exists; step 11 copies the three directories whole (RP case W).

**What.** At the desk, before any call: the first session's read-only copy (the card lane's, at the box's paths) against the box's own
manifest of it: every file listed under the two directories is in the copy at its sha256, and nothing else is there; the manifest names one
session log, whose T0 and Pacific day name the aside. Else 16, no call. Then ONE call on the box (k6's probe first; k6 has no class for a
rename, so it runs under the read class's 60 s bound): refused (10) while a runbook job or a card session of ours runs; the two directories
must be plain directories of ours holding only regular files and directories, whose files by sha256 are exactly the copy's (else
`ASIDE-DIFFERS`, 16, nothing moved); the aside name must not exist (`ASIDE-EXISTS`, 16); then `mkdir` of the aside's two parents and two
renames (`mv -T`, one file system) to `build/claims-v3/aifoundry3/e183-aside-<day>-t<T0>/{e183-smoke/p18301,e183-stoptest/p18302}`, outside
the three directories step 11 copies, and the list read again there (`ASIDE-DONE`). Again after the move: `ASIDE-ALREADY` (0). **Nothing is
removed, written into or copied on the box.** It writes `RB_OUT/aside-e183.txt`.

**Desk cases** ([`rb/selftest_aside_e183.sh`](rb/selftest_aside_e183.sh), a stand-in box with made-up bytes under the real names, 11 + 8
files): A1 ASIDE-DONE, every file at its sha256 under the aside, the box's file count and bytes unchanged, one remote call; A2 again:
ASIDE-ALREADY; A3 one byte different on the box, A4 one more file, A5 a symbolic link: ASIDE-DIFFERS (16), nothing moved; A6 the copy
differs from its manifest and A7 a file the manifest does not list: 16 before any call; A8 a session of ours running: REFUSED (10); A9 the
aside name taken: ASIDE-EXISTS (16); A10 a login link at the probe: 11, the lock file appended, no call; A11 no copy: 10; A12 the dry
listing carries the copy's list, no call; Z another run's files untouched.

## 8. Steps 8 v3 and 9 v3

**Step 8 v3** ([`rb/s10_a3_dry_e183_v3.sh`](rb/s10_a3_dry_e183_v3.sh)) is step 8 v2 with block v3 and session v3's start gate, and its
own job name, `a3-dry-e183-v3`, so that step 9 v3 reads a dry pass of note 6's files made today, never the first session's `a3-dry-e183`.
**Step 9 v3** ([`rb/s11_a3_session_e183_v3.sh`](rb/s11_a3_session_e183_v3.sh)) is step 9 v2 launching session v3, reading today's
`a3-dry-e183-v3`, and refusing (10) while any entry sits in `build/claims-v3/aifoundry3/e183`, `e183-smoke` or `e183-stoptest` (step 5b
first). **Two gates added before the land** (the lane `fix-n6`, for the verifier's findings 3 and 5): at the desk, before any call, it
refuses (10) an RB_OUT that already holds `t0-e183.txt` (one RB_OUT, one session: the first session's RB_OUT holds its T0, and step 11
collects the session whose T0 is written there); and on the box it refuses (10) while `build/e183/STOP` or `build/claims-v3/STOP` exists
(queue v3 reads both before every item, so a stale one would end the session after its smoke with no train). The rest rule, k6's guard,
today's good build and the window's gates are v2's. Its desk test ([`rb/selftest_rb_e183_v4.sh`](rb/selftest_rb_e183_v4.sh)) runs, on a
stand-in box made ready by the window, step 5, step 5a and step 6 v2: V the dry listing v7 in its order; D step 8 v3 (job `a3-dry-e183-v3`
rc 0: block v3's dry 18310, smoke and stop test, session v3's start gate 8; no `a3-dry-e183`); G1 step 9 v3 refused while the first
session's two directories sit in the data root; G2 refused with only step 8 v2's job today; G3 every note 6 gate passing, refused at the
build's gate (the build's job made yesterday's for the case); G4 the rest rule (10 minutes after a session of ours): refused; G5 an
operator's stop left on the box, `build/e183/STOP` and then `build/claims-v3/STOP`, every other gate passing and the rest line read:
refused, naming the file; **L** (the verifier's case, carried into the test before the land) the launch path whole, every gate passing
and the launch's `USER` not the login: `LAUNCHED` with a T0, written to RB_OUT's `t0-e183.txt`; on the stand-in box the session log reads
`kit note 6; plan FULL`, the `USER` gate's line ending `no device opened`, and `session end (T0 ...)`; step 10 v2 then reads `RUN-ENDED`
and `GATE-STOPPED` (16); one session log more and no device record; G6 step 9 v3 again from that RB_OUT: refused at the desk, no call.
Only L launches, and its session stops before any device; a session's real path is section 4's. The test's negative control (a lane
record, not committed): the same test with step 9 v3 as it stood before the land fails 8 of 11, G5 launching with `build/e183/STOP` present
(its stand-in session opened no device: D1 read the holders as unreadable and stopped it) and G6 reaching the box, and L by their cascade.

## 9. Step 2 v7 ([`rb/s03_desk_e183_v7.sh`](rb/s03_desk_e183_v7.sh)) and the dry listing v7 ([`rb/list_steps_e183_v7.sh`](rb/list_steps_e183_v7.sh))

Step 2 v7 runs step 2 v6 unchanged (step 2 v5 inside it reports note 6's and A1's lists as unknown: never a gate there), then on the same
HEAD: this note's list `SHA256SUMS-e183-kit-note6` and amendment A1's `SHA256SUMS-e183-a1`, each at its pinned count and its own pinned
sha256 with every entry OK; the harness v3 (`make_harness_e183_v3.py --check`: CHECK PASS; `harness_e183_v3.py`: HARNESS OK); this note's
four desk tests' logs as committed (the runbook test v4's, with its launch path, added before the land); HEAD unchanged; else 16. It is in neither list (a file cannot hold the sha256 of a list that holds its
own); the go's anchor lines give its sha256. Step 0 and step 2 v7 were run for real in the lane's scratch clone at its local commit; their
readings are in the land's record, since step 2 v7 pins this note's list. The dry listing v7 lists the second session's order (section 10).

## 10. The runbook for the second session (E183.md's dated amendment A1)

| step | file | from this note |
|---|---|---|
| 0 | `check_day2_v2.py tree --pull`, then the anchor lines | unchanged, with note 6's lines |
| 1 | `rb/s02_window_e183.sh 2026-11-13 21:00 22:30`, in a new RB_OUT, absent or empty before this step (the brief's note 5, section 1) | unchanged; step 9 v3 refuses an RB_OUT that holds a T0 |
| 2 | **`rb/s03_desk_e183_v7.sh`** | **new** |
| 4, then 3 | the look; the post waived | unchanged |
| 5a | `rb/s06_a3_records_e183.sh` (the new RB_OUT: today's build records) | unchanged |
| **5b** | **`rb/s06b_a3_aside_e183.sh <the first session's read-only copy>`** | **new** |
| 5 | `rb/s07_a3_sync_e183.sh` (it carries note 6's files) | unchanged |
| 6 | **not run** (the day's one good build stands; NO-THIRD-BUILD) | - |
| 7 | `../q141k-runbook/k6/s09_a3_reads_k6.sh` | unchanged |
| 8 | **`rb/s10_a3_dry_e183_v3.sh start`**, then `wait` | **new** |
| 9 | **`rb/s11_a3_session_e183_v3.sh FULL`** | **new** (its two gates added before the land included) |
| 10 | **`rb/s20_wait_e183_v2.sh`**, again while it says 17 | **new** |
| 11 | `rb/s22_collect_e183_v3.sh` (the release waived) | unchanged (note 5's) |

**Never run on that session:** step 2 v6 alone; step 6 in any version; step 8 v2; step 9 v2; step 10 v1; note 4's box files as a
session's (block, queue, session and preflight v2); and everything notes 3, 4 and 5 name. The brief's dated note 5 carries the table.

## 11. What does not change

E183.md and its notes 1, M1 (with its dated note 1) and M2, and every rule, forecast, threshold, power figure, plan, cap and stop; E183.md's
dated amendment A1 changes none of them. KIT.md and notes 1-5 and their files; the brief and its notes 1-4. The runner, the checks
(`check_e183.py`), `e183_common.py`, the train host's patch, its build (v2), the train check, the reduction, the scorer, the collector and
the copy check; the device commands (every one a READ). Every new file is new; nothing committed is modified, renamed or removed. Two new
Python files (`harness_e183_v3.py`, `make_harness_e183_v3.py`, standard library only), whose names shadow no module.

## 12. Labels

- **Registered, before any train datum:** block v3's post-block check on train blocks only, session v3's `USER` gate, step 5b, step 8 v3's
  job name, step 9 v3's gates (the two added before the land among them), step 10 v2's pattern, step 2 v7's pins and its four logs.
- **Desk checks of code, not measurements:** every test result here (`/usr/bin/python3` 3.12.3 on aifoundry2).
- **Reported:** october-forecast-model's arms (notes M1 and M2), unchanged and unread.
- Nothing here is held out or post hoc, and nothing is measured.

## 13. Files ([`SHA256SUMS-e183-kit-note6`](SHA256SUMS-e183-kit-note6), 47 entries)

This note and the brief's dated note 5; the box files `block_e183_v3.sh`, `queue_e183_v3.sh`, `session_e183_v3.sh`, `preflight_e183_v3.sh`,
`harness_e183_v3.py`, `harness-e183-v3.json`, `make_harness_e183_v3.py`; the runbook's `rb/s06b_a3_aside_e183.sh`, `rb/s10_a3_dry_e183_v3.sh`,
`rb/s11_a3_session_e183_v3.sh`, `rb/s20_wait_e183_v2.sh`, `rb/list_steps_e183_v7.sh`; the desk tests `desk/desktest_realpath_e183.sh`,
`rb/selftest_wait_e183.sh`, `rb/selftest_aside_e183.sh`, `rb/selftest_rb_e183_v4.sh`; the six logs. It also pins the unchanged files the new
steps and tests run, source or name: `block_e183_v2.sh`, `queue_e183_v2.sh`, `session_e183_v2.sh`, `preflight_e183_v2.sh`,
`harness_e183_v2.py`, `harness-e183-v2.json`, `check_e183.py`, `e183_common.py`, `run_e183.py`, `build_host_e183_v2.sh`,
`train_check_e183.sh`, `desk/mock_runtime_e183_v2.cpp`, `rb/fake_cmake_gcc_e183.sh`, `rb/rb_e183.sh`, `rb/s10_a3_dry_e183_v2.sh`,
`rb/s11_a3_session_e183_v2.sh`, `rb/s20_wait_e183.sh`, `rb/s03_desk_e183_v6.sh`, `SHA256SUMS-e183-kit-note5`, the lab's `lib.sh`,
E180's `others_d1_e180.sh`, E128's `ettelem_guard.sh` and k6's `rb_common.sh`. Step 2 v7 is outside it (section 9).

    bash tools/claims-v3/e183/desk/desktest_realpath_e183.sh <scratch dir>     # inside a no-device sandbox; about 13 minutes
    bash tools/claims-v3/e183/rb/selftest_wait_e183.sh <scratch dir>
    bash tools/claims-v3/e183/rb/selftest_aside_e183.sh <scratch dir>
    bash tools/claims-v3/e183/rb/selftest_rb_e183_v4.sh <scratch dir>
    bash tools/claims-v3/e183/rb/list_steps_e183_v7.sh <an empty scratch dir>

## 14. Open items

1. **The land** before the second session's step 0 (the verifier has read this note and amendment A1, and its findings are answered in
   section 15); then the readiness check with the go's anchor lines, which carry the land's commit and these files' sha256 as landed.
2. **The second session's train blocks are the first on any card:** the real-path test ran block 18310 against the recording mock and
   stand-in telemetry, never the card; the box's own toolchain built today's host (13:13 PST, BUILD OK), and every box step stays as
   rehearsed against stand-ins.
3. Step 5b reads the card lane's desk copy of the first session (outside the repo); it was rehearsed on a stand-in box built from that
   copy's own files (19 of 19 exact, ASIDE-DONE, then ASIDE-ALREADY), a lane record, not a committed log.
4. D1's dependence on `USER` is guarded by session v3 only; `others_d1_e180.sh` (E180's) is unchanged, and the lab's stock
   `others_present` has the same dependence (section 6): any later kit that sources either rule carries the gate before its card day.
5. **The smoke gate's code and the plan's text differ** (found by the verifier; older than this note): `check_e183.py` line 34
   (`EXPECTED_SMOKE_LAUNCHES = (2, 3)`, `cc597bf2`) takes 2 or 3 launches in a 1 s burst, where the registered plan's gate text
   (`plan-e183.json`, `c98a7287`) says 1 to 3. The code is the stricter, so it fails safe: a burst of one launch would read SMOKE NO-GO and
   stop the session before any train. Not changed today; a later dated note may align the two.

## 15. Its verifier's findings, answered before the land (the lane `fix-n6` of Q173)

The verifier `verify-n6` applied this note's commit to GitHub main by `git am` (the same tree), re-ran every desk test here and its own
adversarial tests on the real path, and read **holds with fixes**: 2 minor findings and 4 nits, none blocking. The note and amendment A1
were not landed, so each answer is in these files as landed; nothing committed before them changes.

| # | finding | answer | where |
|---|---|---|---|
| 1 | minor: step 9 v3's launch tail (the T0 file, `setsid nohup ... session_e183_v3.sh`, `LAUNCHED`, `t0-e183.txt`) was run by no committed desk test: the runbook test v4's cases all ended at a refusal | the verifier's case L carried into the runbook test v4 (the launch path whole on a stand-in box, the session stopping at its `USER` gate before any device; step 10 v2 reading `RUN-ENDED` and `GATE-STOPPED`); step 2 v7 now checks that test's log beside the other three | section 8; `rb/selftest_rb_e183_v4.sh`; `rb/s03_desk_e183_v7.sh`; the audit's last row (section 5) |
| 2 | minor, outside this kit: D1's fail-open without `USER` is shared by E180's and E184's blocks and runners, and the lab's stock `others_present` fails open the same way | recorded, and carried forward to any later kit that sources either rule; nothing in E183's files needed | section 6; open item 4 |
| 3 | nit: "a new RB_OUT" (A1-3, the brief's note 5) was enforced by nothing | step 9 v3 refuses (10), before any call, an RB_OUT that already holds a T0 (case G6); the brief and the dry listing name the check before step 1 (RB_OUT absent or empty); A1-3 says how it is enforced | section 8; `rb/s11_a3_session_e183_v3.sh`; `rb/list_steps_e183_v7.sh`; the brief's note 5, section 1; A1-3 |
| 4 | nit: the brief's readings omitted step 5b's `ASIDE-FAILED` (16), whose second form is a partial move | the brief's section 4 names it: stop and report, nothing moved by hand before a dated note | the brief's note 5, section 4 |
| 5 | nit: no step read the box for a stale `build/e183/STOP` or `build/claims-v3/STOP`, which would end the session after its smoke with no train | step 9 v3 refuses (10) on the box while either exists (case G5); the brief names the reading | section 8; `rb/s11_a3_session_e183_v3.sh`; the brief's note 5, section 4 |
| 6 | nit, older than this note: the smoke gate's code takes 2 or 3 launches a burst where the plan's text says 1 to 3 | recorded; not changed today (the code is the stricter) | open item 5 |

Re-run on these files as landed (desk checks of code, `/usr/bin/python3` 3.12.3 on aifoundry2, each inside the round's CPU slot and a
no-device sandbox): the four desk tests of the results table, the dry listing v7 and note 4's three tests; the six logs in `logs/` are
those runs'. Step 0, the anchor lines and step 2 v7 were run for real on the land's local commit; their readings are in the land's record.

SPDX-License-Identifier: Apache-2.0
