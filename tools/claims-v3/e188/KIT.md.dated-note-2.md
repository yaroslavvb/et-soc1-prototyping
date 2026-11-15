# E188's kit, dated note 2 (Sun 15 Nov 2026, before any E188 datum): the kit run from aifoundry2 (Linux) as well as the Intel (macOS) - the lab-git lock by flock, GNU date for gdate, portable sed, the forecast check within a stated tolerance on its floats' last digits, step 11's desk-path gate for a desk whose home has the box account's shape, the real-path desk test and its dry-vs-real audit, step 10 tested on the real session script, step 2 v3, and the lab's top checked for a shadowing module (fix-port188); no rule, forecast, threshold, plan, cap, stop or reading changes

*Beside [KIT.md](KIT.md) (`726a6b64`) and its [dated note 1](KIT.md.dated-note-1.md) (`16b41cf2`); it edits nothing there, nor in
[E188.md](E188.md) or its dated amendments A1 and A2 and note 1. Written on aifoundry2, desk only, by the lane `port-e188` of Q182, begun
at 10:11 PST Sun 15 Nov 2026 by the clock; its commit's own time is git's. No card was claimed, no device command was sent, no lab box was
reached, nothing was posted. Every run of a built binary, runner or stand-in box went through the round's CPU slot and a no-device
sandbox (aifoundry2 has a card of its own), and the tests that need one make their own sandbox inside it (no `/dev/et*`, a private
PID namespace). **No E188 datum exists** (`git log --all` on `docs/reports/data/*e188*`: nothing). E188 was registered and kitted on
Thu 12 Nov 2026 and waits for the owner to name it in a go; the orchestrating session moved to aifoundry2 on Fri 13 Nov 2026 and the
Intel cannot be reached from there (E183's kit note 5 asked the same question for E183; E189's kit was ported the same way and named
E188's two open ports, `b42dc95c`). New files only, all under `tools/claims-v3/e188/`; every committed file stays as committed. Before
its land the lane `fix-port188` (Q182, from 12:09 PST) changed it in place on `verify-port188`'s findings (HOLDS WITH FIXES): a check of
the lab's top, a new file run by steps 2 v3 and 11 v2 (finding 1), and the wording items; section 14 has each finding and its answer. No
frozen number changed.*

## Results first (desk checks of code on aifoundry2; nothing is measured)

| check | result | log |
|---|---|---|
| **what fails on aifoundry2, reproduced**: step 2 v2 (as committed) for real on a scratch copy of the lab clone; the forecast's byte check under `/usr/bin/python3` 3.12.3; step 11's desk-path gate on E186's committed collection (E188's parent form); the macOS-only forms in the kit | step 2 v2 **16**, "the desk check failed: pull forecast": its pull "not started: [Errno 2] No such file or directory: '/usr/bin/lockf'" (rc 14) and `forecast_e188.py check` exit 1 (CHECK FAIL); step 11 v1's gate (k6's `rb_nopath`) **hits 71 files** ("this user's home"), note 2's gate 0; the forms in 8 files, every one a desk test, the dry pass, the stand-in cmake or step 2's pull | [`logs/port-aifoundry2-e188.txt`](logs/port-aifoundry2-e188.txt) |
| **the forecast check with a stated tolerance** (`forecast_tol_e188.py`) on this desk | **FORECAST-TOL-E188 PASS**: kinds-e188.json, the 6 new tiles and forecast-e188.txt byte-exact; every string, integer and boolean of forecast-e188.json exact; 16 of its 317 floats differ in their last digits, the largest at 0.0805 of its tolerance | the same; section 2 |
| **its self-test: how 3.9 and 3.12 differ, and that the tolerance cannot pass a real change** | **SELFTEST-FORECAST-TOL-E188 PASS (14 of 14)** (section 2) | [`logs/selftest-forecast-tol-e188.txt`](logs/selftest-forecast-tol-e188.txt) |
| **the runbook desk test v3**, ported (GNU date as `gdate` or `date`, `lockf` or `flock`, portable sed), on step 2 v3, step 11 v2, the dry listing v3, step 9 v2 and step 10 | **SELFTEST-RB-E188-V3 23 of 23 PASS**, the nested lab-git lock (N), the forecast's last digit pinned (F1), step 11 v2 against v1 on this desk's shape (C5) and its early check (C0), and the lab's top (T, T11) among them | [`logs/selftest-rb-e188-v3.txt`](logs/selftest-rb-e188-v3.txt) |
| **the lab's top** (fix-port188, on verify-port188's finding 1): the one folder the day's desk Python puts ahead of the standard library that the history check does not read; `rb/check_top_e188.py`, run by step 2 v3 and step 11 v2 and read by the brief right before step 1 | a `_strptime.py` committed there runs in step 1 and reads HISTORY OK, and the check and step 2 v3 refuse it (16); an untracked `json.py` there stops step 2 v3 (16) and step 11 v2 before any scoring (16), unread by either; it also reads `tools/claims-v3/e183/rb/`, the folder note 2's step 11 v2 brings into the day, where an untracked `re.py` reads HISTORY OK and stops step 2 v3 (16) (runbook cases T, T3, T11; its unit run 20 of 20); every other folder that Python puts first is one the history check reads for committed additions (section 14) | the runbook log; section 14 |
| **step 10 on the real session script's name** (E183's lesson) and its gate pattern against every line a passing session writes (E190's) | **SELFTEST-WAIT-E188 PASS (8 of 8)** | [`logs/selftest-wait-e188.txt`](logs/selftest-wait-e188.txt) |
| **THE REAL-PATH DESK TEST** (E183's lesson): `session_e188.sh` with `V3_DRY` unset, every binary a real build on the recording mock, stand-ins for every device tool | **DESKTEST-REALPATH-E188 PASS (18 of 18)**: both smoke gates ran and passed on a real smoke (never run under `V3_DRY`), the queue started and stopped at the operator's stop; step 10 reads that real passing session as ended (0) | [`logs/desktest-realpath-e188.txt`](logs/desktest-realpath-e188.txt) |
| E188's committed desk tests run again here, each read against what it prints on this desk | **RERUNS-NOTE2-E188 PASS (10 of 10)** (section 1) | [`logs/reruns-note2-e188.txt`](logs/reruns-note2-e188.txt) |
| the dry listing v3, both paths | **19 steps, 0 exited non-zero, 0 box calls** | [`logs/dry-listing-e188-v3.txt`](logs/dry-listing-e188-v3.txt) |

## 1. What fails on aifoundry2, and why (the port's record)

1. **Step 2's pull.** `rb/rb_e188.sh` (sourced by every step) runs the pull as `/usr/bin/lockf -k -t 600 <RB_GITLOCK> git pull --ff-only`.
   Linux has no `lockf`, so step 2 v1, and step 2 v2 that runs it, stop with 16 at once (the rest of the checks run first and report).
   This is E189's finding about E188 (`b42dc95c`, KIT.md: "E188's two open ports").
2. **The forecast's byte check.** Step 2 v1's `forecast_e188.py --root . check` re-makes forecast-e188.json in memory and compares its
   bytes. Under aifoundry2's `/usr/bin/python3` 3.12.3 16 floats come out with other last digits, so it reads CHECK FAIL (section 2).
3. **The desk tests' macOS forms.** `rb/selftest_rest_e188.sh`, `rb/selftest_rest_e188_v2.sh` and `dry_intel_e188.sh` refuse without `gdate`
   (Homebrew's name of GNU date); `rb/selftest_rb_e188.sh` and `_v2.sh` edit files with BSD sed's `sed -i ''` (GNU sed reads `''` as a file
   name), count `lockf` in the runbook log and grep the stand-in build's log for "Homebrew GCC": on aifoundry2 v2 reads 12 of 16 (P1,
   P2-P5, P6-P7, S1). `desk/desktest_train_check_e188.sh` mentions SDKROOT only to unset it, and runs as committed (50 of 50 here).
4. **Step 11's desk-path gate.** k6's `rb_nopath` runs v3.1's `nopath_q142s.py`, which forbids "this user's home". On aifoundry2 that home is
   `/home/<login>`, the prefix of every path aifoundry3 writes (the box account has the same name): on E186's committed collection, E188's
   parent form, it hits 71 files. So step 11 v1, collected from aifoundry2, would stop (16) after the copy-back and the scoring, before the
   data commit. port-e183 found this for E183 (its kit note 5, `9ae55d39`); E188's kit predates it.
5. **The scorer's self-test, last digits.** `selftest_score_e188.py` reads 18 of 20 under 3.12.3: its A1 (E186's scale `s` re-made from
   E186's committed anchors, compared to E186's scored `s` to the last bit: 1.0087332311048327 here, 1.008733231104833 committed) and A2
   (E182's train reduction re-made on two of E186's committed blocks, compared to trains-e186.json to the last bit) differ in their last
   digits. Run again with the built-in `sum()` as before 3.12 (a `sitecustomize.py` written at run time into a scratch directory on
   `PYTHONPATH`), it reads 20 of 20: the cause is 3.12's compensated summation, nothing else (`desk/reruns_note2_e188.sh`). This is a desk
   test, not a card-day step; on E188's day the collector and the scorer run under 3.12.3 here, and their printed figures may differ from a
   3.9 run's in the last digits. A verdict could move only for a statistic within such a step of its threshold. **Name the interpreter in
   the day's records** (step 2 v3 prints it).

Not ported, because nothing in them is macOS-only: every file the box runs (aifoundry3 is Linux; its `date` is GNU's), k6's `rb_common.sh`
and v3.1's `rb_run.py`, the collector, the scorer and the readers (the port record's grep, section 2, and E189's kit's grep of the same k6
files). `bench/bench_e188.sh` is the registration's bench on the mini, not a card day's file.

## 2. The forecast check within a stated tolerance ([`forecast_tol_e188.py`](forecast_tol_e188.py)), and why it cannot pass a real change

**How 3.9 and 3.12 differ on E188's forecast** (a desk read, shown by [`selftest_forecast_tol_e188.py`](selftest_forecast_tol_e188.py)'s F1
and F2): the forecast was frozen on the Intel's `/usr/bin/python3` 3.9.6 (macOS), where `forecast_e188.py check` reads CHECK PASS. Under
aifoundry2's 3.12.3 (glibc 2.39, numpy 1.26.4) 16 of forecast-e188.json's 317 floats differ, and nothing else does: kinds-e188.json, the 6
new tiles and forecast-e188.txt (every figure the registration prints, to its printed digits) are byte-exact. Two sources:
- **3.12's built-in `sum()` adds floats with compensated (Neumaier) summation**, where 3.9 adds them left to right. `m12_common.dot` and
  M10's feature chain sum floats. 7 values change by this alone: the three lines of PAIR's first tile (8.233099847174708 W committed,
  8.23309984717471 recomputed: 1 unit in the last place, 1.8e-15 W), PAIR's two train lines (a difference of two kinds' lines near 8.23 W,
  0.0013285762528241207 W committed: the same 1.8e-15 W is 8,192 units in the last place of so small a number) and PAIR's two powers from
  the measured noise. With `sum()` replaced by plain left-to-right addition under 3.12 (F2), all 7 become byte-exact.
- **`math.erf` differs between the two builds.** The other 9 are power values, `0.5 (1 + erf(.))` or a sum of two (`candidates_m12.norm_cdf`),
  each at most 8 units in the last place (1.1e-16) under the old summation; two of them (PAIR's powers from the registered noise) carry
  both sources and differ natively by 5,804 units, 8.1e-14, the largest difference of the 16 (the native rows: F1's log). Under the
  old summation every other float of the file is byte-identical, so `erf` receives the committed arguments: the difference arises inside
  it (`erf` is not correctly rounded, and the near-cancellation `1 + erf(x)` for `erf(x)` near -0.85 turns one unit of `erf`'s last place
  into up to 8 of the result).

**The check** (step 2 v3's forecast check; it writes nothing and never re-freezes):
1. **the pins:** the registration's list `SHA256SUMS-e188-registration` at its 20 entries and its own sha256 (`b098561b...`, as step 2 pins it),
   and in it, at their listed sha256, the five files the check rests on (`forecast_e188.py`, forecast-e188.json, forecast-e188.txt,
   kinds-e188.json, `bench/counts-e188.json`). **The committed forecast's bytes stay the pinned truth**, and the scorer reads those bytes;
2. **the recomputation:** `forecast_e188.py` imported unchanged, `stage()` and `forecast()` run in memory, as its own `check` runs them
   (`forecast()` asserts its own exact checks: the bench's reference rows, E186's kinds to the last bit, AALL as E186's R4);
3. **exact:** kinds-e188.json's bytes, the new tiles' bytes, forecast-e188.txt's bytes, and in forecast-e188.json every key, list length,
   string (each input's sha256 in `inputs_sha256` among them), integer, boolean and null;
4. **within the tolerance:** each float of forecast-e188.json, **|committed - recomputed| <= 1e-12 x max(1, |committed|, |recomputed|)**
   (a line near 8 W may move by 8e-12 W, a value at or below 1 by 1e-12). On aifoundry2 the largest difference is 0.0805 of its
   tolerance (PAIR's power from the registered noise, 8.1e-14); a margin of 12. On 3.9 the bytes are exact and the check says so.

**Why it cannot pass a real change** (each claim a case of the self-test, 14 of 14):
- a change of the committed forecast fails the pins: a byte changed, the list one line short, or the file and its list line rewritten
  together, each refused by name (F5); in step 2 v3 the registration's list is also read by v1's loop at its pin (the runbook test's F1: a
  last-digit edit of a forecast line with its list line rewritten stops step 2 v3 at both);
- a change of an input file fails the exact sha256 strings (every one of the file's 200 strings, integers and booleans alone changed: an
  exact difference, every time, F3c), and a change of any figure the registration prints fails forecast-e188.txt's bytes;
- **the float comparison by itself:** every float alone moved by twice its tolerance is caught, every time (F3b, 317 of 317); every watt
  figure moved by 5e-6 W, half of the last place the .txt prints (1e-5 W), is outside by at least 5.7e5 times its tolerance (F3d, 182
  figures); an input changed in memory (its file's bytes, so its sha256, unchanged), recomputed through `forecast()`: B05's F tile's adder
  count x (1 + 1e-9) and x (1 + 1e-6), E182's measured train se x (1 + 1e-9) and the registered train half-width x (1 + 1e-9) are each
  outside; the comparison still sees that count changed by 1e-10 relative (its resolution there, about 1e4 below the registration's printed
  1e-5 W on an 8 W line); the fp32 rate and M12's `gamma_B` x (1 + 1e-9) stop `forecast()` itself at its exact check against E186's frozen
  kinds (F4).

So the tolerance admits only changes below 1e-12 absolute (1e-12 relative above 1) in a float of forecast-e188.json: what an
interpreter's arithmetic does to the last digits and, for the smallest floats, somewhat more (B05's M10 train line, -1.4e-5 W, may move
in its eighth significant digit, about 3e8 units in its last place; a zero may become 1e-12), still seven orders below the 1e-5 W the
registration prints; never a change of the committed forecast, of an input, of a printed figure, or of anything a rule reads at the
registration's precision; and no reading of E188 uses the recomputed numbers at all. (Reworded before the land by fix-port188,
verify-port188's nit 4: this paragraph said the tolerance "admits only what an interpreter's arithmetic can do to the last digits".)

## 3. The lab-git lock: [`rb/rb_e188_n2.sh`](rb/rb_e188_n2.sh)

The file note 2's steps source in place of `rb/rb_e188.sh`, which it sources unchanged (and k6's `rb_common.sh` with it). One change, E189's
way (`b42dc95c`): `e188_pull` takes the lab-git lock with `/usr/bin/lockf -k -t 600` where it exists (the Intel: rb_e188.sh's own words),
else `/usr/bin/flock -w 600 -E 75` (Linux; the round's commit helper on aifoundry2 takes the same lock with `flock`). Both exit 75 when the
600 s pass, so a step 2 run inside that lock still waits, exits 75 and stops with 16 naming its pull: **never run step 2 inside the
lab-git lock**. The desk test's short wait for its nested case (`RB_GITLOCK_T`) is read only with `RB_DESKTEST=1`; a card day sets neither.
The dry listing names the command this desk would run ("run on the desk"). Runbook case N: a step 2 v3 inside the lock (outer `flock -n`)
stops with 16 naming its pull, the lock tool's exit 75 in the runbook log.

## 4. Step 2 v3: [`rb/s03_desk_e188_v3.sh`](rb/s03_desk_e188_v3.sh)

Step 2 v1's code, line for line (runbook case D2: 7 lines out and 25 in, comments aside, every one of them note 2's), with:
1. `rb/rb_e188_n2.sh` sourced (the pull's lock as section 3); its name in the runbook's log `s03_desk_v3_e188`;
2. the forecast check `forecast_tol_e188.py` (section 2), never the byte check;
3. v1's loop over the lists reads four more, each at its count and its own sha256, every entry OK (a gate, no override): note 1's two
   (`SHA256SUMS-e188-a1` 2, `SHA256SUMS-e188-kit-note1` 10, as step 2 v2 pinned them), **the registration's dated amendment A2's**
   (`SHA256SUMS-e188-a2` 1, pinned by no step before) and **this note's** (`SHA256SUMS-e188-kit-note2`, 23; step 2 v3 is outside it: a
   file cannot hold its own list's sha256, so the go's anchor lines carry step 2 v3's sha256 beside the list's);
4. note 1's three desk tests' logs (step 2 v2's) and note 2's six test logs (its seventh log, the port's record, has no PASS line), as
   committed, each with its PASS line once;
5. the desk's `/usr/bin/python3` read and named in the step's last line;
6. (fix-port188) right after the history check, [`rb/check_top_e188.py`](rb/check_top_e188.py): the lab's top, and E183's rb/ folder that
   step 11 v2 brings into the day, hold no module or package named as one the system python finds, no byte-code a module's name imports
   and no `.pth` file, else 16 naming `top` (section 14).

Everything else is v1's: the window written today for E188 first (10 before any call), `RB_GITLOCK` required, the ancestry from
`878b6f63`, the paths clean, the history check, v1's twenty lists and the kit's 106 at their pins, a list it does not pin reported (never a
gate), the harness rebuilt, the items, the build inputs, the plan, the statistics, v1's eight desk tests' logs as committed, HEAD unchanged
across all of it (16), E188 data in any ref reported. On aifoundry2 the pull may meet GitHub's ssh port failing (E183's kit note 5, section
4.3): the card lane may set, for step 2 only and in the environment, never in a git config file,
`GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=url.https://github.com/.insteadOf GIT_CONFIG_VALUE_0=git@github.com:`.

## 5. Step 11 v2: [`rb/s22_collect_e188_v2.sh`](rb/s22_collect_e188_v2.sh)

Step 11 v1's code, line for line (D2: 5 lines out and 11 in; 3 and 6 before fix-port188 added the lab's top's check after the history
check, before any scoring, with its line in the summary, and -I on the reading of a failed pairing: section 14), with E183's desk-path gate
in place of k6's: it sources `rb/rb_e188_n2.sh` and
E183's `rb/nopath_desk_e183.sh` (unchanged, by path; E183 ran it on its real collection from aifoundry2 on Fri 13 Nov 2026), with
`E183_BOX`, the name that file reads, set to E188's box (aifoundry3); right after the window and the end gate, **before any copy**,
`nopath_desk_ready` (HOME is this account's home from the account database, else 10; no entry of that home named as aifoundry3's tree,
`aifoundry`, else 16); and at the end `nopath_desk "$OUT"` in place of `rb_nopath "$OUT"`. On a desk whose home is not under `/home/` (the
Intel) `nopath_desk` is `rb_nopath`, unchanged. On aifoundry2 it forbids each entry of the home by name, leaves aifoundry3's tree out, and
reads every path written from the home with `.`, `..` or `//` that leaves that tree as a hit (`rb/nopath_spell_e183.py`); E183's kit note 5,
sections 2-3 and 11, has the gate's whole reading and its 37-case test. On E186's committed collection it reads 0 hits where k6's reads 71
(the port record). Runbook case C5, on a session staged on the stand-in box whose scored output names aifoundry3's own tree under the
desk's home: step 11 v1 stops at k6's gate (16), step 11 v2 collects it (0), and a desk path beside it stops step 11 v2 (16); case C0: HOME
set but empty is refused (10) before any copy.

## 6. Step 10 on the real session script ([`rb/selftest_wait_e188.sh`](rb/selftest_wait_e188.sh)), unchanged

Step 10 (`rb/s20_wait_e188.sh`) looks for the session's process with `pgrep -u "$(id -u)" -f "session_$RUN\.sh"`, `RUN=e188`. Unlike E183's
(whose session v2's name its step 10 v1 never matched), E188 has one session script, `session_e188.sh`, and step 9 v2 launches it by that
name (`setsid nohup bash tools/claims-v3/e188/session_e188.sh`). The test runs step 10 whole against a stand-in box in a private PID
namespace with the real `pgrep`, on **the real `session_e188.sh`** launched with step 9 v2's own words and held at its harness check by a
stand-in `python3`: the real `pgrep` lists exactly `bash tools/claims-v3/e188/session_e188.sh`; step 10 reads RUN-RUNNING (17) while it
runs, RUN-ENDED with MANIFEST-WRITTEN and GATE-STOPPED (16) once it stops at that check, RUN-GONE (14) for a session killed with SIGKILL
before its end, and RUN-GONE (14) when only other names run (`session_e1880.sh`, `session_e186.sh`, `queue_e188.sh`, `block_e188.sh`).
**E190's lesson** (its step 10 v2 read every session that passed its identity gate as a gate stop): step 10's GATE-STOPPED pattern,
`smoke gate failed|stop-path test failed|no device opened`, matches every stop line of `session_e188.sh` (its 10 `stop_now` messages and its
2 gate lines) and none of its 12 other lines; no other file the session runs (51 text files `harness-e188.json` names) prints any of its
three phrases (a desk read of code, W5); and on the real-path test's real passing session step 10 reads RUN-ENDED (0), no GATE-STOPPED
(case P5 there). The line "the train smoke's gate failed ... the queue runs PASSES" is the registered fallback's, not a gate stop, and the
pattern does not read it as one. Seen beside (no change): after RUN-GONE the remote loop also prints a RUN-RUNNING line; the desk reads
RUN-GONE first (14).

## 7. The real-path desk test ([`desk/desktest_realpath_e188.sh`](desk/desktest_realpath_e188.sh)) and the dry-vs-real audit

**The lesson** (E183's kit note 6, `977c63d1`): a check that runs only on the real path is never exercised by a desk test that runs the dry
path. E188's kit (Thu 12 Nov) predates it: its dry pass runs every block under `V3_DRY`, where the session skips its config reads and **its
smoke gate**, lib.sh takes no card lock and starts no sampler, and both runners print instead of launching. This test runs
`session_e188.sh`'s real path, `V3_DRY` unset, in its own sandbox (no `/dev/et*`, the sandbox's own card lock file, a private PID
namespace, the hostname aifoundry3), against stand-ins for every device tool (E183's forms: the telemetry reader, the holder readers,
logging `timeout` and `flock`, refusing `ssh`, `scp` and `rsync`; `USER` the login, as the ssh login sets it on the box). Every binary the
session runs is a real g++-13 build on the recording mock runtime: E78's host (also the heater), the C-logging host, and the train host
by `build_host_e188.sh`'s real path with the kit's stand-in cmake; the tree's `harness-e188.json` pins the four stand-in binaries.

**The mock in a card's time** ([`desk/mock_rt_e188_clock.cpp`](desk/mock_rt_e188_clock.cpp), desk only, never on a box). The test's first
run, on the committed mock (`desk/mock_rt_e188.cpp`: a fixed 40 ms a launch, each launch's C computed inside the launch, 546 cycles an op
for every type), stopped the session at **"smoke gate failed (stop test rc 0, smoke rc 0, gate 1): no block runs"**: the host's own clock
reading (the longest kernel's cycles over the launch's wall time) read 0.06-3.1 GHz, outside the gate's 0.595-0.605, and int8's cycles
per op read 546 where the gate wants 318. That is the mock, not the kit: a card at its pinned 600 MHz passes the same gate (E186's smoke on
aifoundry3). The 600 MHz mock records the card's cycles per op for each type (the gate's own table: fp32 and fp16 546, int8 318), makes
each launch last its cycles at 600 MHz, and computes each launch's C after the host has timed it; the train host is built with no C stored
(`MOCK_C_SKIP`), since the engine's C at a train's iters takes seconds a tile and no step of the session reads it (the collector's check of
C does, at step 11; `desktest_host_e188.sh` checks the train host's C on the plain mock). Case P6 shows the gate's clock check still bites:
P's smoke with every launch's clock moved 1% off 600 MHz reads FAIL on the clock.

**The cases** (18 of 18): 0a-0c the sandbox; the three builds (TRAIN-CHANGE OK read from the train host's behaviour, no device call); HARNESS
OK 79 with the binaries and 72 without; the preflight GO. **P1-P4 the real path:** harness with the binaries, the train host's behaviour, the
preflight, the start config read under the card lock and `timeout 10` through E128's guard, the stop-path test 18802 (die, board and watch
each exit 6 on a live sample), the smoke 18801 (its 13 kinds items and 2 B05 processes, 28 train launch records, every launch through the C
wrapper), **both smoke gates on the real smoke: SMOKE-GATE (kinds) PASS and SMOKE-GATE (train) PASS**, "smoke gate passed: queue starts (plan
FULL)", the queue's "STOP: stopping before p18820" (the operator's stop written before the launch), the closing config read, et-who at both
ends, "session end", LAST_T0, blocks.txt naming both blocks, MANIFEST.sha256 over the session's files and both blocks' (every line reads
back); the real calls counted (2 locked config reads, 2 block locks, D1's holder read twice a block, 2 samplers at 10 Hz, 15 host runs
under `timeout 10`, each reaching the mock device layer). **P5** step 10 on that real passing session (section 6). **P6** the clock check
bites. **A1-A10** the branches the dry path skips: D1's other-user rule (another user's holder: 3, no device call); the card lock held (3);
a live board stop at 65 W (the in-run watcher's STOP, the block fails, no host run); the sampler stalls (the runner's stale check, the
block fails); a changed C-logging host (the session 9 "no device opened", the block's preflight 2; the harness without the binaries
passes); the session's start gate past its latest start (8); lib.sh's skip of a block already done (0, no device call); D1 and `USER`
(below). **Z** nothing left running, no network call, no `/dev/et*`.

**The dry-vs-real audit** (every `V3_DRY`, `--dry` and dry-only variable on the session's path; "RP" is this test):

| where | under the dry path | on the real path | run now by |
|---|---|---|---|
| `session_e188.sh`: its directory and `LAST_T0` | `T<T0>-dry`, no LAST_T0 | `T<T0>`, LAST_T0, which steps 10 and 11 read | RP P3; the wait test W1-W3 |
| `session_e188.sh`: `cfg()` | writes `{"dry":true}` | the config read under the card lock and `timeout 10` through E128's guard | RP P1, P4 |
| `session_e188.sh`: the smoke gate | "DRY: the smoke gate needs a real smoke; not run" | `smoke_gate_e188.py --part kinds` and `--part train` on the real smoke | **RP P1, P2, P6** |
| `session_e188.sh`: the data root | `build/claims-v3-dry/` | `build/claims-v3/aifoundry3/`, with its earlier-block refusal | RP P, A9 |
| `block_e188.sh`: D1 (`others_present`) | lib.sh's stub: nobody | `sudo -n et-holders` lines on card 0 not of `$USER`, and `ps` | RP A1, A10 |
| `block_e188.sh`: `check_e188.py` with the binaries | skipped (the `--desk` form) | every binary and the train host against their pins | RP 0c, A6; runbook S1 |
| `block_e188.sh`: the card lock file's presence; `blocks.txt`; `et-lab-manifest` | not read; not written; not run | read; appended (E188_T0 set); run (no device) | RP P3, A2 |
| `block_e188.sh`: `card_config`, the sampler | stubs | the guard's `config` under `timeout 10`; the 10 Hz sampler started and stopped by SIGTERM | RP P4, A4 |
| lib.sh: `block_begin`'s card lock, `die_c` | no lock; 80 C | `flock -n 9`; the guard's `sample` | RP P4, A2 |
| `run_e188.py`, `run_e78.py`: the launches, the approach, the stops, the in-run watcher, the stale check | printed, not run | the host through the C wrapper under `timeout 10`; the stops on live samples | RP P (the smoke, with no heat), A3, A4; the stop-path test in P |
| `run_e188t.py`: the train processes, their records, stops and watcher | printed | the train host through the wrapper | RP P2 (the smoke's two processes) |
| the queue's blocks on the real path: the kinds passes (E78's approach: heat to 59 C, launch at 58 C) and the trains (anchors, 76 processes) | printed | the same block and runner code as the smoke, with the heater's approach | **not run at the desk** (a stand-in die cannot follow a heater); `run_e78.py`'s approach is unchanged since E78 and ran on aifoundry3 in E78's, E178's, E182's and E186's sessions |
| step 9's launch tail | the listing prints the remote script | the launch, T0, `e188-T0.txt` | runbook L (v2's case, kept) |

**The host's real bytes** (the round's lesson after E191's smoke on aifoundry1, where a runtime line split the host's JSON line; verify-port188's
finding 8): this test feeds the runners the mock's output only. The real evidence for the two `SPARSITY {` parsers on aifoundry3 is
E186's FULL session (section 14, finding 8); no raw stdout from that box is committed, so no desk test can feed it.

**D1 and `USER`, carried (case A10; E183's kit note 6, section 6).** `block_e188.sh`'s D1 keeps the holder lines whose user is not `$USER`
inside a command substitution under lib.sh's `set -u`: with `USER` unset it reads no holder at all and goes on (to its block-number check,
2, in the test), where with `USER` set another user's holder line exits 3. On aifoundry3 the session inherits `USER` from the ssh login that
launches it (step 9), as E183's sessions did; E188 has no gate for it, and none is added here (a box file would mean a new harness, check,
preflight, sync and dry pass: the kit's note 1, section 4). **A carried gap, reported:** E188's readiness check decides whether the card
lane's brief reads `USER` in step 9's output or a later note gates it.

## 8. The runbook from aifoundry2

KIT.md section 3 and note 1, with three rows replaced and step 1 preceded by a read (fix-port188):

| step | file | from this note |
|---|---|---|
| 1, the window | `rb/s02_window_e188.sh`, unchanged, right after the brief's read of `rb/check_top_e188.py` (fix-port188; section 14) | the read: TOP OK, else no step that day |
| 2, the desk check | **`rb/s03_desk_e188_v3.sh`** with `RB_GITLOCK` set (the lab-git lock the desk's commit helper takes), never inside that lock | anything but 0: no box step that day (16 naming HEAD-moved: a co-owner committed meanwhile, run it again; 16 naming `top`: the lab's top or E183's rb/ holds a shadowing module, byte-code or a `.pth` file) |
| 10, the wait | `rb/s20_wait_e188.sh`, unchanged, again while it says 17 | 0 ended with its manifest (read the printed lines); 16 a gate stop, still collected; 14 RUN-GONE or MANIFEST-ABSENT: read the box (read-only) first; 10 RUN-UNKNOWN |
| 11, the collection | **`rb/s22_collect_e188_v2.sh`** | as step 11 v1, and 10 or 16 from the desk-path gate's early check before any copy; 16 at the lab's top or E183's rb/ after the history check (nothing scored) |

Every other step is KIT.md's and note 1's (step 9 is note 1's v2). The desk tests that want `gdate` run through
[`desk/gnudate_e188.sh`](desk/gnudate_e188.sh). The dry listing is [`rb/list_steps_e188_v3.sh`](rb/list_steps_e188_v3.sh); its lines "run on
the Intel" (k6's `rb_local` words, unchanged) mean the desk. **Never on E188's day from aifoundry2:** step 2 v1 or v2 (they stop at the pull),
step 11 v1 (it stops at its desk-path gate after the scoring), or the runbook desk test v1 or v2 as the day's evidence. What the day also
needs (the owner's go naming E188, the post or its waiver, the window, the bookings, the hold, the anchor lines with this note's) is the
card lane's and its go lines', not this note's ([`CARD-LANE-BRIEF.md.dated-note-2.md`](CARD-LANE-BRIEF.md.dated-note-2.md)).

## 9. What does not change

E188.md, its dated amendments A1 and A2 and its dated note 1, and every rule, forecast, threshold, power figure, plan, cap, stop and
reading. KIT.md and note 1 and every file of theirs; the brief and its note 1. Every box file, the harness (77 files), the box steps but 2
and 11, the build, the session, the queue, the block, the runners, the smoke gate, the rest rule, the collector, the reductions, the
scorer, the reported arms' reader and its gate (`arm_read_e188.py`, `rb/check_arms_e188.py`). Every new file is new; nothing committed is modified, renamed or removed. Three new
Python files: `forecast_tol_e188.py` (a reader, standard library only beside what `forecast_e188.py` imports), its self-test and
`rb/check_top_e188.py` (a reader of the lab's top and E183's rb/, standard library only; fix-port188); one new C++ file, the 600 MHz mock, desk only.

## 10. Open items

1. **E188 runs only on the owner's go naming it.** Its box steps have been rehearsed against stand-ins only; the train host's first
   compile is on the box (step 6).
2. **D1 and `USER`** (section 7): carried, reported.
3. **The queue's blocks on the real path** (the kinds passes' heater approach, the trains' anchors and 76 processes) did not run at the
   desk (section 7's audit).
4. **The readers under 3.12.3** (section 1, item 5): name the interpreter in the day's records.
5. **The lab's top** (E189's fix-fix189 found it in E189's check; verify-port188 confirmed it for E188's by test, its finding 1):
   answered before the land by `rb/check_top_e188.py` (the top and E183's rb/), run by steps 2 v3 and 11 v2 and read by the brief right
   before step 1, and -I on step 11's reading of a failed pairing (section 14). Every other folder the day's desk Python puts first is one
   the history check reads for committed additions (section 14; untracked files there: item 9). What stays: a module put at the top after the brief's read would run in step 1's window script before step 2 v3 stops the
   day.
6. **The desk's home must not hold an entry named `aifoundry`** (aifoundry3's tree): step 11 v2 refuses (16) before any copy if it does.
7. **verify-port188 read this note (HOLDS WITH FIXES), and fix-port188 answered its findings in place (section 14).** No verifier has
   read fix-port188's changes before the land; E188's readiness check reads them (the top's check, cases T (with T3) and T11, the brief's
   read before step 1, the wording).
8. **The host's real bytes on aifoundry3** (verify-port188's finding 8): the evidence is E186's FULL session, not a desk test; the
   readiness check weighs it (section 14).
9. **An untracked module in a folder outside the core ones** (beside a file a list names, in a folder the day's Python puts first) is read
   by neither the history check's rule 3 (committed additions) nor its rule 4 (uncommitted files on E188's paths); fix-port188 found it
   while reading the folders for finding 1 (section 14). `rb/check_top_e188.py` reads one such folder, E183's rb/ (note 2's step 11 v2 runs
   `nopath_spell_e183.py` there); the others (`e178`, `e164`, `kinds`, `p8-600`, `ccheck`, `e119`, `rtl-sim/fma_toggle_v2`, the data
   folders), which the committed kit already brought into the day, are carried, for the readiness check: the round reads the lab clone
   clean (`git status --porcelain` empty) before each land, and step 2 v3 reads E188's paths clean; a read of `git status --porcelain --untracked-files=all`
   on those folders before step 1 would close it.

## 11. Labels

- **Registered, before any datum:** step 2 v3's pins and its forecast check's tolerance, step 11 v2's gate, the lab's top's check, the
  runbook's rows.
- **Desk checks of code, not measurements:** every test result here; the forecast's last digits under 3.12 (a desk reading of an
  interpreter's arithmetic); the clock and cycle figures of the mock; the folders the day's desk Python puts first (fix-port188's
  coverage reading, a desk reading of code). E186's record counts (section 14) are read from its committed data.
- **Reported:** the arms of `ofm-e188.json` (unchanged, unread). Nothing here is measured, blind, held out or post hoc.

## 12. Files ([`SHA256SUMS-e188-kit-note2`](SHA256SUMS-e188-kit-note2), 23 entries)

This note and the brief's dated note 2; `forecast_tol_e188.py`, `selftest_forecast_tol_e188.py`; `desk/gnudate_e188.sh`,
`desk/desktest_realpath_e188.sh`, `desk/mock_rt_e188_clock.cpp`, `desk/reruns_note2_e188.sh`; `rb/rb_e188_n2.sh`, `rb/s22_collect_e188_v2.sh`,
`rb/list_steps_e188_v3.sh`, `rb/selftest_rb_e188_v3.sh`, `rb/selftest_wait_e188.sh`, `rb/check_top_e188.py`; the seven logs; and E183's two files step 11 v2 sources
or runs, unchanged (`tools/claims-v3/e183/rb/nopath_desk_e183.sh`, `tools/claims-v3/e183/rb/nopath_spell_e183.py`). Step 2 v3 is outside it
(section 4). The unchanged files the new steps source or run beside those (`rb/rb_e188.sh`, k6's `rb_common.sh`, v3.1's `rb_run.py` and
`nopath_q142s.py`, E178's `scrub_tree_e178.py`, steps 9 v2 and 10) are pinned by the kit's list and note 1's, which step 2 v3 reads.

    /usr/bin/python3 -B tools/claims-v3/e188/forecast_tol_e188.py --root .
    /usr/bin/python3 -B tools/claims-v3/e188/selftest_forecast_tol_e188.py <scratch dir>
    bash tools/claims-v3/e188/rb/selftest_rb_e188_v3.sh <scratch dir>          (in a no-device sandbox: case L launches the real session)
    bash tools/claims-v3/e188/rb/selftest_wait_e188.sh <scratch dir>
    bash tools/claims-v3/e188/desk/desktest_realpath_e188.sh <scratch dir>
    bash tools/claims-v3/e188/desk/reruns_note2_e188.sh <scratch dir>          (in a no-device sandbox)
    bash tools/claims-v3/e188/rb/list_steps_e188_v3.sh <an empty scratch dir>
    /usr/bin/python3 -I -B tools/claims-v3/e188/rb/check_top_e188.py          (from the lab's top)

## 13. Builds on (the stock-take's rule for lanes, MAP section 3)

1. **Checked:** as KIT.md's block; pieces newer than it cited by commit: E188's kit note 1 (`16b41cf2`) and amendment A2 (`f9632ee3`);
   E183's kit notes 5 and 6 (`9ae55d39`, `977c63d1`); E189's kit (`b42dc95c`) and its history check's rule 4 after fix-fix189 (the
   folders the day's Python puts first); E190's kit note 2 (its step 10 v3); verify-port188's findings (Q182, section 14).
2. **Used**, each unchanged and by path: E188's kit and note 1 (step 2 v1's code, the base of v3; step 11 v1's, the base of v2; the dry
   listing v2, the base of v3; the runbook desk test v2, the base of v3; `forecast_e188.py`, imported; `desk/mock_rt_e188.cpp`, the base of
   the 600 MHz mock); E183's `rb/nopath_desk_e183.sh` and `rb/nopath_spell_e183.py`; E183's real-path test's and step-10 test's forms; E189's
   lock port; k6's runbook drivers; E188's history check's rule 3 (its shadow test, the same in `rb/check_top_e188.py`). *Check against the
   same operation:* step 2 v3 against v1 and step 11 v2 against v1, line counts (D2).
3. **Not used:** anything of the card, the box, the reported arms' model or the private tier.
4. **Tiers:** every file here is public tier and cites public pieces only.
5. **Readiness:** this block is the note's. A verifier checks it.

## 14. Answered before the land (fix-port188, Q182, Sun 15 Nov 2026, from 12:09 PST)

`verify-port188` (11:35-12:08 PST) read this note at GitHub main `fe08ed67` plus the port's patch and found it HOLDS WITH FIXES: nothing
it found blocked the land. The lane `fix-port188` changed the note in place, in a copy of the port's scratch clone, before any land.
Every change is to note 2's own new files, plus one new file (`rb/check_top_e188.py`); the registration's, the kit's and note 1's files
are untouched, and no frozen number changed.

| # | verify-port188's finding | answer |
|---|---|---|
| 1 | low (carried, confirmed by its test): a module added at the lab's top passes the history check (HISTORY OK) and runs in step 1's window script (`_strptime.py`) and in step 11 v2's `python3 -B -c` (`json.py`) | **fixed:** `rb/check_top_e188.py` (below; it also reads E183's rb/, the folder note 2 brings into the day), run by step 2 v3 after the history check (16 naming `top`) and by step 11 v2 after the history check, before any scoring (16, nothing scored); the brief reads it right before step 1; step 11 v2's `-c` runs with -I. Runbook desk test cases T and T11 |
| 2 | low: the brief's post record cites only the Fri 13 and Sat 14 Nov waivers | **fixed:** the brief's section 3 cites the owner's standing waiver of Sun 15 Nov 2026 10:22:36 PST and the departure's words; the behaviour is unchanged |
| 3 | nit: `forecast_tol_e188.py`'s docstring said "about 1e-11 relative, a million times below" the printed 1e-5 W | **fixed:** 1e-10 relative (F4; at 1e-11 the largest difference is 0.271 of the tolerance), about 1e4 below |
| 4 | nit: section 2 said the tolerance admits only what an interpreter's arithmetic can do to the last digits | **fixed:** "only changes below 1e-12 absolute (1e-12 relative above 1)", with the smallest floats named |
| 5 | nit: the land record (LAND.md, not a file of the repository) said every E188 file is 100644 | **fixed there:** every note-2 file is 100644 (29 earlier E188 files are 100755) |
| 6 | nit: the brief said the go's anchor lines gain four; the land record carries six | **fixed:** the brief's section 2 lists six, numbered in the land record's order |
| 7 | nit: the commit message said math.erf makes the other 9 differences, at most 8 units in the last place; F5's docstring said "one byte changed" | **fixed:** the message and `forecast_tol_e188.py`'s docstring say that with `sum()` as before 3.12 each of the 9 is at most 8 units, and that natively PAIR's two powers from the registered noise, which carry both sources, differ by 5,804; F5's docstring says "appended" |
| 8 | info: the round's real-bytes lesson (after E191's smoke on aifoundry1) is not carried into the real-path test | **answered for the readiness check** (below); no box file changes |

**The lab's top (finding 1): which folders the day's desk Python puts ahead of the standard library, and which the history check reads**
(fix-port188's coverage reading, a desk reading of code; step 2 v3's seven readers traced to their final `sys.path`, the rest read from
the code):
- **Four processes put the lab's top first:** step 1's window script on stdin (`time.strptime` imports `_strptime`); the collector's two
  scripts on stdin (`collect_e188.sh`, inside step 11: `reduce_footing`'s and `ccsessions_e188`'s standard-library imports, after the folder
  each inserts); step 11's reading of a failed pairing (`python3 -B -c`; -I from this note on). The history check reads additions on
  E188's paths only, and the top is on none of them.
- **Every other folder they put first is one the history check reads for committed additions** under its rule 3: the core directories
  (e188, e186, m12, e182, the k6/v3.1 runbook) in full and, for their own files and packages, the folders of the files E188's lists and
  harness name: `tools/claims-v3/e183/rb` (step 11 v2's `nopath_spell_e183.py`; the kit list names `rest_rule_e183.sh` there), `e178`,
  `e164`, `kinds` and `kinds/blind5`, `p8-600`, `ccheck`, `e119`, `rtl-sim/fma_toggle_v2`, and the nine data folders the forecast's chain
  inserts (M9's and its recount rule's, M10's, the footing's, and the model folders of Q133, Q137, Q138, Q139 and E147). Its rule 4 reads
  uncommitted files on E188's paths only: the core directories in full, but in those other folders only the named files themselves, so an
  untracked module beside them (say `tools/claims-v3/e183/rb/re.py`, which `nopath_spell_e183.py` would import) is read by neither rule
  (read so in the lane: HISTORY OK with it, HISTORY REFUSED with the same file in `e188/rb/`). Of those folders only E183's rb/ comes into the
  day with note 2 (step 11 v2), so `rb/check_top_e188.py` reads it too; the rest, the committed kit's, are carried (section 10, item 9).
- **[`rb/check_top_e188.py`](rb/check_top_e188.py)** lists the top and E183's rb/ as they are on disk (committed or not, ignored or not:
  Python reads the disk) and refuses a module file or regular package there named as a module the system python finds (the history check's
  rule 3, the same test), byte-code a module's name would import (a sourceless `.pyc` or `.pyo`; at the top also any `__pycache__`) and any
  `.pth` file. On the lab clone today it reads TOP OK (no module at the top; in E183's rb/ only `nopath_spell_e183.py`). Its unit run in the
  lane refused, each alone, at the top `_strptime.py`, `json.py`, an extension module named `json`, a package `numpy/`, a sourceless
  `re.pyc`, a `__pycache__` folder, a `.pth` file, `test.py` and `statistics.pyw`, and in E183's rb/ `re.py`, a sourceless `gzip.pyc`, a
  package `posixpath/`, a `.pth` file and the folder missing; it passed `notes.py`, `e188_common.py` (the stdin scripts put E188's folder
  first), `tools/__init__.py` and a namespace folder at the top, and a `__pycache__` in E183's rb/ (20 of 20). The runbook desk test's case T: a
  `_strptime.py` committed at the top (a working copy of the standard library's, which writes a marker when imported) runs in step 1 (rc 0,
  the marker written) and reads HISTORY OK, and the check alone and step 2 v3 refuse it (16); an untracked `json.py` there stops step 2 v3
  (16), unread by any of its processes; an untracked `re.py` in E183's rb/ reads HISTORY OK and stops step 2 v3 (16). Case T11: step 11 v2 on a staged session with that `json.py` copies back, reads HISTORY OK and stops
  (16) at the check, before the collector, the module unread.
- **What stays:** a module put at the top between the brief's read and step 1 would still run in step 1's window script; step 2 v3 then
  stops the day (16) before any box step, and step 11 v2 reads the top again before the collector.

**The host's real bytes (finding 8), for the readiness check.** The two `SPARSITY {` parsers the day's runners use (`kinds/run_e78.py`
line 290, unchanged since 31 Oct 2026; `run_e188t.py` line 136, the same two lines as E186's `run_e186t.py`) read the host's stdout in
memory: no raw stdout from aifoundry3 is committed, so no desk test can feed them its real bytes. The real evidence is E186's FULL session
on aifoundry3 card 0 (Mon 9 Nov 2026, `docs/reports/data/2026-11-09-e186-one-number-r3-aifoundry3/`): the same lines parsed 9,968 train
records (10 blocks' `train.jsonl`) and 466 kinds-pass records (22 `runs.jsonl` files), and every one of its 12 blocks reads status ok. A
runtime line printed inside a `SPARSITY {` line makes `json.loads` raise: the runner, and with it the block (at the smoke, the day), fails.
One printed just before a record's start, with no line end between, would drop that record: the runner logs each process's launch count
and the scorer's pairing check reads a train with unpaired records as NOT SCORED. Neither turns a record into another number. These
parsers are box files and do not meet the round's lesson (a result read from a source no runtime print can split); changing them means a
new harness (the kit's note 1, section 4), so the readiness check weighs that with E186's evidence.

SPDX-License-Identifier: Apache-2.0
