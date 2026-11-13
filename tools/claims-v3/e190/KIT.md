# E190's run kit: one session runner for both arms in E189's form (one sampler, the stop lines live, the stop-path test, the gates), E136's rgm136 built on each box and read by its kernel's bytes and its host's behaviour, the reducer to the frozen scorer's form, the runbook from aifoundry2 to the scorer after the data commit, with no post (Q169; kitted, not run)

*Fri 13 Nov 2026 (week 46), PST, on aifoundry2, desk only (Q169, lane `kit-e190`). No card was claimed or opened: aifoundry2 has a card, so
every desk test that runs a built host, the runner or a stand-in session ran in a sandbox with no /dev/et* and an empty /run/lock. No device
command was sent, nothing was posted. The one other box reached was aifoundry1, over `ssh -o BatchMode=yes`, bounded, for ONE build of
rgm136 in a new folder of ours (`~/e190-q169-desk`): nothing built there was run. New files only, all under `tools/claims-v3/e190/`. The
registration [`E190.md`](E190.md) (commit `508d48d9`, its `tools/claims-v3/e190` subtree `4d4f7440...`; `SHA256SUMS-e190-registration`
`bfe58c58...`, 16 entries) and every file its list names stay as committed. **No E190 datum exists. Nothing here changes a forecast, a band,
a rule, a threshold, the order, the card time, the cap, a stop or the scorer.** Where E190.md leaves a reading to the kit, the reading is
stated in section 4 before any datum.*

## Results first (desk checks of code; nothing is measured)

| check | result | log |
|---|---|---|
| **the runner on the doubles** (`selftest_run_e190.py`): every gate before any device (the start config of each arm, a failed config read, the lock held, et-who holders, device processes of another user, of ours and a CI job, a dead sampler, a stop-path test that cannot trip, a smoke check of C wrong, a smoke crash), each stop line on live samples (arm A's board line above 85 W on 3 samples; arm B's die line at 80 C on the shires' mean; the die line on the hottest sensor alone; no trip at 85.0 W nor on 2 samples above; arm B's 75 W line), the die gate held, the card-time rule, a hung host (`timeout 10`, rc 124), two failed processes in a run, THE ORDER (the whole plan: the 18 runs in the registered order, 1 and 12 processes, every argv the registered one), the refusals without `--dry` and the REAL runner on the desk stopping at its box check; and END TO END on both arms (the whole plan, the doubles' leakage off): the reducer, then the frozen scorer | **SELFTEST-RUN-E190 25 of 25 PASS**; end to end: 36 runs reduced, every run's t_gemm the injected seconds within 1.2e-6 (relative), its J over idle the injected watts x seconds within 0.40% (0.34% with the watts 25% over); the scorer read R0, S1-S6 PASS, S7 THE SAME SCALED, S8 STRICT at the points, and S1 PASS, S2 FAIL, S3 FAIL with the watts 25% over | [`logs/selftest-run-e190.txt`](logs/selftest-run-e190.txt) |
| **the build on this desk's real toolchain** (`desk/desktest_build_e190.sh`; GCC 15.1.0 for the kernel, g++ 13.3.0, cmake 3.28.3) | **DESKTEST-BUILD-E190 4 of 4 PASS**: the kernel ELF at the registration's pin `aace138c...` (its .text `61315bf6...`), the host's four refusals before any device, the record; a changed source refused before the build; a changed kernel refused at the pin; the runner's box check passes the kernel and host and stops at the reader's pin only | [`logs/desktest-build-e190.txt`](logs/desktest-build-e190.txt) |
| **the runbook** (`rb/selftest_rb_e190.sh`: a fake ssh and rsync, two stand-in boxes, the real build): the window rule, the lab-git lock (absent and nested), step 2 at every pin, the history check and a shadow, the look, E190's ours_live (a command string that names session_e190.sh is not a session; a session_e190.sh run as a script is), step 5 on the git tree (17, then `pull`) and the rsync, a login link (11 and the lock line), a hang (13), a cut wait (14), NO-THIRD-BUILD, the negative control through the runbook, the real build of both arms, the box's dry passes, the rest rule through step 9, the REAL session stopping at its box check, the wait, the copy-back, the data directory, a copy not exact | **SELFTEST-RB-E190 29 of 29 PASS**; on its way it found E190's own fault for arm A (item 18 of section 4: k6's text-matched ours_live counted the desk's own commands on aifoundry2) and the kit fixed it before the commit (case OL) | [`logs/selftest-rb-e190.txt`](logs/selftest-rb-e190.txt) |
| the dry listing, every step for both arms with stand-ins | **22 steps, 0 exiting non-zero, 0 box calls** | [`logs/dry-listing-e190.txt`](logs/dry-listing-e190.txt) |
| `dmcmd_audit` on the session's files (`preflight_e190.sh`: the runner, its common module, the wrapper, the build, the harness check, E190's guard, the host's source) | **GO, 22 send sites, 0 disallowed, every one a READ**, no allow-list, no exception: each reader resolved to its reviewed variant (aifoundry2 `build/ettelem-hpl` = ettelem-dv2; aifoundry1 `build/ettelem` = ettelem) | [`logs/dmcmd-audit-e190.txt`](logs/dmcmd-audit-e190.txt) |
| the common module's self-check, the harness, the registration's checks | E190-COMMON SELF-CHECK PASS; harness-e190.json CHECK PASS and HARNESS OK (25 files); forecast_e190 --check PASS; plan_e190 --check PASS; the scorer's stub self-test PASS | [`logs/checks-e190.txt`](logs/checks-e190.txt) |
| **aifoundry1's build** (Fri 13 Nov 2026 12:36 PST, `~/e190-q169-desk`, builds only, nothing run) | the kernel ELF byte-identical to the pin (`aace138c...`, .text `61315bf6...`: the same RISC-V GCC 15.1.0); the host built against aifoundry1's own runtime (its `libetrt.so` `d2412f17...`, aifoundry2's `f5d1bfb1...`: the two boxes' runtimes differ, as E136 and E137 found), host compiler g++ 13.3.0 | [`logs/a1-build-e190.txt`](logs/a1-build-e190.txt) |

## 1. The kit, in E189's form

- **The runner** ([`run_e190.py`](run_e190.py), [`session_e190.sh`](session_e190.sh), [`e190_common.py`](e190_common.py)): one arm's whole session
  on its box. Before anything opens: the host name is the arm's, build/e190rgm's kernel at the pin and its host at the sha256 the box's build
  recorded today, the arm's telemetry reader at its pin, the three tiles at kinds.json's sha256, the harness (HARNESS OK) and the preflight
  (dmcmd_audit GO). Then the card's lock (`flock -n`, held to the end), the holders (counts only), THE FIRST CARD COMMAND `ettelem config`
  through [`ettelem_guard_e190.sh`](ettelem_guard_e190.sh) under `timeout 10` (the card time counts from it), ONE sampler (10 Hz) for the
  session whose every line feeds THE STOP LINES as it arrives, the stop-path test, the smoke, the registered order, the closing config,
  "session end", MANIFEST.sha256 last. Nothing is set.
- **The build** ([`build_e190.sh`](build_e190.sh)): E136's rgm136 unchanged, into **build/e190rgm** (a new folder of ours) on each box;
  the kernel by its bytes (the registration's pin), the host by its behaviour (four refusals main.cpp makes before its device Session),
  build/e190rgm/BUILD-e190.json. Its desk test runs the real toolchain here.
- **The doubles** ([`fake_card_e190.py`](fake_card_e190.py)): config, et-who, a toy card's sampler driven by the launches the host double
  announces at their start, and the host (its SPARSITY lines on a virtual clock at the forecast's points, so the reducer reads the injected
  seconds at any time scale).
- **The reducer** ([`reduce_e190.py`](reduce_e190.py)): each arm's session into the frozen scorer's data form (score_e190.py's docstring)
  and a table. **The collection** ([`collect_e190.py`](collect_e190.py)): COPY-BACK EXACT, the data directory, the scrub of the box's home
  and of our own box login, the reducer, SHA256SUMS. **The harness** ([`check_e190.py`](check_e190.py), `harness-e190.json`) and **the
  preflight** ([`preflight_e190.sh`](preflight_e190.sh)).
- **The runbook** ([`rb/`](rb/)), from aifoundry2 through k6's drivers, unchanged: the window; step 2 (the pull under the lab-git lock,
  every list pinned by count and bytes, the history check, the harness, the registration's checks, the preflight, the desk tests' logs);
  per arm the look (k6's), the sync, the build, the dry pass, the session, the wait, the copy-back; the data directory; the scorer after the
  data commit. **No post and no release** (waived: section 4, item 16). [`CARD-LANE-BRIEF.md`](CARD-LANE-BRIEF.md) is the card lane's brief,
  with THE QUIET HOLD's note.

## 2. Card-minutes and the cap (registered; unchanged)

About 33 card-minutes on arm A and 25 on arm B (plan-e190.txt), cap 40 an arm: no run starts once the arm's card time passes 35 minutes; at 40
minutes the session ends; a started run is cut only by a stop.

## 3. The order on each box

| step | file | what |
|---|---|---|
| 0 | (by hand) | `uptime`; the anchor lines; THE QUIET HOLD (CARD-LANE-BRIEF.md section 2) |
| 1 | `rb/s02_window_e190.sh <day> <last start> <last end>` | first; today's day only; one window for both arms |
| 2 | `rb/s03_desk_e190.sh` | the window; the pull under the lab-git lock; ancestry (the registration's subtree, the kit found by its content); the paths clean; HISTORY OK; the two lists at their pins; the harness; the common self-check; forecast and plan --check; the stub self-test; the preflight; the desk tests' logs |
| 4 | `../q141k-runbook/k6/s05_look_k6.sh aifoundry2` / `aifoundry1` | k6's, unchanged (et-who, who, uptime, ps counts; aifoundry1's identity by continuity); our login recorded for the scrub |
| 5 | `rb/s07_sync_e190.sh A [pull]` / `B` | arm A: the git tree holds the kit commit (17 until it does; `pull`: fast-forward only), HARNESS OK there; arm B: the rsync into `~/nekko`, HARNESS OK there |
| 6 | `rb/s08_build_e190.sh <A\|B> start`, then `wait` | the detached build, NO-THIRD-BUILD, the record, the harness, the preflight and the self-check on the box |
| 8 | `rb/s10_dry_e190.sh <A\|B> start`, then `wait` | the runner on the box with its doubles, no device |
| 9 | `rb/s11_session_e190.sh <A\|B>` | k6's guard and identity, THE REST RULE, today's dry pass and build, then `session_e190.sh` detached |
| 10 | `rb/s20_wait_e190.sh <A\|B>` | the T0 the runbook launched; the manifest written; a gate stop is 16 and still collected |
| 11 | `rb/s22_collect_e190.sh <A\|B>` | one read-only copy back, COPY-BACK EXACT |
| 12 | `rb/s23_data_e190.sh` | the data directory `docs/reports/data/<day>-e190-large-gemm/`, the scrub, the reducer, SHA256SUMS, the desk-path gate, the history check; then the data commit (the card lane's, through `commit_lab.sh`, under its quiet hold) |
| 13 | `rb/s24_score_e190.sh` | after the data commit only: score_e190.py (registered, unchanged) on the committed data-e190.json |

## 4. The readings stated here before any datum (where E190.md leaves a choice to the kit)

1. **The stop lines as the watcher reads them** (E190.md 8: "the keys run_hpl.py's watcher reads"): `board_cap_w` 85 W (arm A) / 75 W
   (arm B) on `cap_consecutive` 3 samples in a row, the board strictly above the line, a sample with no board reading starting the count
   again; `abs_stop_c` 80 C on one sample of the shires' mean OR the hottest shire sensor. E190.md 3 words the die line on the shires' mean;
   the hottest sensor reads at or above the mean, so the line as the watcher reads it trips no later and possibly earlier: stricter, never
   looser. A trip touches the hosts' `--stop-file` at once: the running host ends its loop at its next launch boundary (about 0.5 s; this
   host's own path, proven on silicon by E146's stoptest-board), never killed; nothing further starts; the run's 4 s read and the closing
   follow.
2. **The stop-path test** ("the stop tests on live samples first"): E189's form, on the session's live sampler, with test thresholds every
   sample crosses (0 W on 3 samples; 0 C), each test line touching its own file (never the hosts' stop file) and refusing a start; no launch
   is spent on it.
3. **The start config**: arm A 65 W / 65 C (E136's runner ended a session unless both read back 65); **arm B also 600 MHz**: its line
   (61.5 W predicted peak under 70 W) is reckoned at 600 MHz, so a card found off it voids the premise: no launch. Read again at the end.
4. **The smoke**: one process a format with `--seconds 2 --budget 3.5` (E146's smoke form; E190.md says "one 2 s process"), not die-gated (E146's
   smoke); its gate: rc 0, every launch ok, the check of C exact or approx, the check record's cycles an op within 50-250% of the frozen point
   at the arm's clock (E146's queue read the same record). Any failure ends the session at the gate.
5. **Arm B's rest die**: the median of the shires' mean over the smoke's 30 s rest reading.
6. **The tail**: 4 s read after a run's last process (E136's and E146's `tail_s`); the reducer does not use it.
7. **Card time** counts from the start config read. The 35-minute rule is read before a run and again after its die gate (whose wait stops
   at the rule); a run whose planned length would pass the 40-minute cap less 60 s of closing, or come within 90 s of the window's last end,
   does not start (with the rule at 35 minutes it never binds: the longest run is about 2.2 minutes).
8. **A failed process** (rc not 0, `timeout 10`'s 124 among them) is flagged in its run; two in one run stop the session (E64's runner's rule).
9. **The holders**: et-who and ps before the session and before each run; before each later process of a sustained run, ps only (et-who takes
   up to 20 s and would open gaps the plan does not have). Arm A: any holder line of another login, another user's device process, a CI job,
   another device process of ours. Arm B: a holder of card 1's nodes or lock of another login, any line of ours on card 0 (never two of our
   sessions on aifoundry1), a CI job, another device process of ours; another login on card 0 does not block (k6's rule there). Counts only.
10. **The reducer's readings**: a counted launch also has `ok` and `wall_s` >= 0.1 s (E119's clock_x floor; every E190 launch is about 0.4 s
    or more); a sustained run's last 40 s holds the counted launches wholly inside [the last process's end - 40 s, its end]; die_start is the
    mean of the shires' mean over the last 5 s of rest; the smoke's cycles an op is each format's check record's; arm A's x600 comes from
    every launch of the counted form at 590-610 MHz and at or above 790 MHz; a run with no counted launch keeps t_gemm null with its reason.
11. **The readers**: arm A E136's sampler `build/ettelem-hpl/ettelem` (`77a46171...`, the reader of every anchor burst the forecast uses);
    arm B the lab's `build/ettelem/ettelem` on aifoundry1 (`8008f96f...`, E157's, E164's and E172's pin on card 1); one guard, `config` and
    `sample` only.
12. **THE REST RULE** (E190.md registers none; the kit's): no E190 session starts within 40 minutes of our last real session on that box
    (E189's rule, every session-log form; on aifoundry1 either card), so that "the card at rest" the forecast prices is a rested card.
13. **Arm A's tree** (`~/claude/et-soc1-prototyping`) is a git checkout that merges GitHub main by itself: nothing is copied into it (an
    untracked copy of a file the next merge brings would stop that merge); step 5 waits for the kit commit there, or pulls it fast-forward.
14. **The build** goes into `build/e190rgm` on each box; the kernel ELF must be the registration's pin on both boxes (shown on both desks
    today); the host is read by its behaviour, its bytes carrying its build path.
15. **The scrub**: the box's home becomes "~" and our own box login "<login>" in every text and .gz file; any /home/ path or the login left
    refuses the collection.
16. **No post, no release**: the owner waived the day's Discord post (his words, Fri 13 Nov 2026 about 11:30 PST); the card lane records it.
17. **The A100 report's figures** are in no file of this kit (E190.md: its date only).
18. **E190's ours_live** (`rb/rb_e190.sh`; found by this kit's runbook desk test, its first runs' cases C and C2): on aifoundry2 the desk
    and arm A's box are one machine, reached by ssh to itself, so the desk's own commands are not ancestors of the box's read. k6's
    ours_live matches a process's whole command text: step 9's own name (`s11_session_e190.sh` holds `session_e190.sh`) and any shell
    whose command string names a session file would read as "a card session of ours" and refuse arm A's launch, its build, its dry pass and
    its copy-back. E190's prelude keeps k6's whole (`rb_common.sh` unchanged) and then redefines ours_live to read each process's OWN
    script (the first word after its interpreter and options; a shell's `-c` string never counts), with k6's names; the wait and the
    copy-back count `session_e190.sh` the same way. The card lane on aifoundry2 should still not run a command whose words start a file
    named `session_eNNN.sh` beside a step that reaches the box.

## 5. Files

| file | what |
|---|---|
| `e190_common.py` | the arms, the build's pins, the stop lines, the gates, the order with its cells, the argv, the counted launch; its self-check |
| `run_e190.py`, `session_e190.sh` | the runner (both arms) and its detached wrapper |
| `ettelem_guard_e190.sh` | the only way the runner reads a card: `config`, `sample --seconds --every-ms` |
| `build_e190.sh` | the box build and its record |
| `check_e190.py`, `harness-e190.json` | every file a box runs or reads, at its sha256 (25) |
| `preflight_e190.sh` | dmcmd_audit on the session's files |
| `fake_card_e190.py` | the doubles |
| `reduce_e190.py` | the scorer's data form from the sessions |
| `collect_e190.py` | COPY-BACK EXACT; the data directory, the scrub, the reducer, SHA256SUMS |
| `selftest_run_e190.py` | the runner's desk test, end to end through the frozen scorer |
| `desk/desktest_build_e190.sh` | the build's desk test on the real toolchain |
| `rb/` | the runbook's steps, its common file, the rest rule, the history check, the dry listing, its desk test |
| `CARD-LANE-BRIEF.md` | the card lane's brief (THE QUIET HOLD's note among it) |
| `logs/` | every check above |
| `SHA256SUMS-e190-kit` | the kit's files (step 2 aside), its logs |

## 6. Device commands

`dmcmd_audit.py` on the session's files: **GO, 22 send sites, 0 disallowed, every one a READ**, with no allow-list and no exception:
`ettelem config` (GET_MODULE_STATIC_TDP_LEVEL, GET_MODULE_TEMPERATURE_THRESHOLDS, GET_MODULE_POWER_STATE, GET_ASIC_FREQUENCIES, GET_ASIC_VOLTAGE)
and `ettelem sample` (GET_MODULE_POWER, GET_SP_STATS, GET_MODULE_CURRENT_TEMPERATURE, GET_ASIC_VOLTAGE, GET_MODULE_VOLTAGE, GET_ASIC_FREQUENCIES),
each through the guard, which refuses `--reset-ms` and every other word before the device opens. The host opens the ops node only. No set, no
reset, no statistics reset, no firmware query, no residency read, no drain (`dev_mngt_service` is never run), no power cycle.

## 7. What the desk cannot show

1. **The card path at this size has never run**: A, B and C of 512 + 256 MB in fp32 and the runtime's 256 MB allocations and DMAs; the
   smoke is their first check, on each card.
2. **The runner has met only its doubles** (the desk, and each box's dry pass on the day): the live sampler, the card lock, et-who and the
   real host meet it first in the session. The stop-file path on silicon is E146's (the same host).
3. **aifoundry1's host has never run**: built here today and not run (the round's rule); the box's build step reads its refusals on the day.
4. **The process times are desk estimates** (plan-e190.txt): 12 processes of about 7.9 s in fp32 under `timeout 10`; a process cut by
   `timeout 10` is flagged and loses its check, never a device held past 10 s.
5. **Arm A's tree merges GitHub main by itself** (its reflog: a fast-forward to each new commit within minutes); step 5 waits or pulls.
6. Card time waits on the owner's go for the day (section 102's words) and a readiness lane's go lines.

## 8. Labels

Every figure quoted from E190.md and its files (the forecasts, the order, the caps, the stops, the pins) is **registered**. The desk tests'
results are **desk checks of code**, not measurements; the end-to-end joules and the scorer's words come from the doubles (the frozen
forecast's points driven through a toy card): not a measurement and not a reading of E190. The aifoundry1 build's hashes are a desk build's.
Nothing here is **blind** or **held out**, and no E190 datum exists.

## Compute

On aifoundry2 through the round's local slots (`slot.sh`, nice 10), one job at a time, each that runs a built host, the runner or a stand-in
session inside the sandbox: the runner's desk test (about 15 minutes), three real builds of rgm136 for the build's desk test and two for the
runbook's, the dry listing. On aifoundry1: one cmake build of rgm136 (seconds), nothing run.

SPDX-License-Identifier: Apache-2.0
