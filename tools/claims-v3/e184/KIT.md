# E184's run kit: the staircase on aifoundry3 card 0 (870 quads, about 125 card-minutes, cap 135) and card 1's SRAM-rail test on aifoundry1 card 1 (about 18, cap 25), with the host-only change, the scorer for every registered rule and dated amendment A1 (Q153; kitted, not run)

*Sat 7 Nov 2026 (week 45), about 11:30-12:50 PST, on the Intel, desk only (Q153, lane `e184`): no card was claimed, no device command was
sent, no lab box or the mini was reached, nothing was posted or deployed. New files only. The registration [`E184.md`](E184.md) (`c6417611`,
11:27:45 PST) and every file [`SHA256SUMS-e184-registration`](SHA256SUMS-e184-registration) lists stay as committed (11 of 11 OK). No E184
datum exists: `git log --all` shows no `docs/reports/data/*e184*`. Card time waits on the owner's word and fresh network approvals, after a
verifier of this commit and a readiness critic.*

## Results first

- **Arm S, the staircase (aifoundry3 card 0, 600 MHz pinned).** [`block_e184s.sh`](block_e184s.sh) runs one pass in V3-CATFULL's form, as
  E180's v2 block does (lib.sh's look, D1's other-user test sourced unchanged from `e180/others_d1_e180.sh`, the card lock, the 10 Hz sampler
  through E128's guard with no `--reset-ms`, the runner, the post-block check, gzip, block_end). The runner [`run_e184.py`](run_e184.py)
  runs every quad of [`plan-e184.json`](plan-e184.json) in order: one host process under `timeout 10` (`--budget 9.5`), its schedule
  S + A B B A or B A A B, its images made by [`make_images_e184.py`](make_images_e184.py) and checked against the frozen list; D1's test
  and the stall check before every process; the live stops (board 65 W, `minshire[0]` 70 C) before and every 0.1 s during every process,
  a stop writing the `STOP` file the host reads before every launch. Pass 18413 reads its own two quads and pass 18412's A blocks from the
  telemetry and writes `cal.json` (M_op, M_s) by E184.md section 2.1's rule; parts P and C refuse without it.
- **Arm B, card 1's SRAM rail (aifoundry1 card 1, V3_DEVICE=1).** [`block_e184b.sh`](block_e184b.sh): the same block, card 1 only (never
  card 0), its telemetry through [`ettelem_guard_e184.sh`](ettelem_guard_e184.sh) (E128's allow-list plus `--reset-ms 1000` alone), the
  statistics reset in pass 18441 alone; the runner's bursts and holds with item and process marks; card 1's stops (66 W, any
  `minshire` 72 C).
- **The host-only change** ([`host_patch_e184.py`](host_patch_e184.py), built on the box by [`build_e184.sh`](build_e184.sh) into
  `build/enercat-e184`; nothing committed is edited): four insertions in a copy of `workloads/enercat/host/main.cpp` (committed sha256
  `3cad4adc…`, patched `7360e5e1…`, both pinned): `--schedule` (segments of launches, each with its own 2,048 x 256 B operand image copied
  before its first launch; an ENERCAT line per launch with `seg`, `label` and `image`) and `--stop-file`. The kernel is unchanged. **Its
  desk test, DESKTEST-HOST-E184 PASS** ([`logs/desktest-host-e184.txt`](logs/desktest-host-e184.txt)): the patched file compiles with
  `-Wall` and no warning against [`desk/stubs/`](desk/stubs) and links with a mock runtime ([`desk/mock_runtime_e184.cpp`](desk/mock_runtime_e184.cpp));
  run on the desk, a quad gives 18 launches in S A B B A order with the images' nonzero words in each copy (0, then 384 for 3 minions on 32
  shires); a stop file stops it before the first launch (exit 8); a wrong-size image is refused before any launch; the budget stops it
  (exit 9); without `--schedule` the catalogue's own loop is unchanged. The first compile against the real runtime is still the box's
  (step 6 below).
- **The runner's real path at the desk, DESKTEST-RUNNER-E184 4 of 4 PASS** ([`logs/desktest-runner-e184.txt`](logs/desktest-runner-e184.txt);
  kit v5's "real floor-path dry case"): `run_e184.py --desk` drives the desk host, with a thread writing a stand-in sampler file at 10 Hz: the
  smoke's four quads (72 launches, every segment as planned, the images equal to the frozen list); a live stop mid-pass (rc 5 after 12
  quads, `STOP` and `stop.json` written); arm B's six bursts with their marks; and the refusals (another arm's card, an unplanned pass, part P
  without `cal.json`). `--desk` skips D1's test (its et-holders call exists only on the boxes) and is refused on a lab box.
- **The scorer** ([`score_e184.py`](score_e184.py), on [`reduce_e184.py`](reduce_e184.py)'s files) reads every rule of E184.md section 5
  as A1 states them, with the registration's own statistics (e184_common.py; `power_e184.py`'s `delta_ratio`, run from that file's own
  text). **Its self-test, SELFTEST-SCORE-E184 14 of 14 PASS** ([`logs/selftest-score-e184.txt`](logs/selftest-score-e184.txt)): synthetic
  sessions written in the box's layout by [`fake_card_e184.py`](fake_card_e184.py) read as their truths (linear: N NULL, L LINEAR, J NONE
  SEEN, P LINEAR and METER EXCLUDED, C NONE SEEN, K inside; small steps at 0.8: L and P LOW; at E178's 0.29: P METER NOT EXCLUDED; a one-code
  step at 33.6 W: C SEEN at 33.64 W; a 0.10 W jump: J SEEN; card 1 two-phase: M SUPPORTED, T PASS; a normal rail, or ratios moving 0.12:
  M REFUTED; a 1.0 s SRAM filter: T OUTSIDE; missing arms and passes: NOT SCORED). **On committed card data:** the reset-window reader gives
  Q150's committed medians exactly on September's card-1 windows (idle 219 samples 0.6268 / 1.5917, busy 61 at 0.6305 / 1.5753), and A1's
  step-response reader gives E58's committed time constants on E58's card-1 bursts (SRAM 0.53 s against 0.525, minion 1.07 s against 1.08).
- **Dated amendment A1** ([`E184.md.dated-note-A1.md`](E184.md.dated-note-A1.md), this commit, before any datum): E184-T is read with E58's
  filter model ([`tau_a1_e184.py`](tau_a1_e184.py)), because the registered reader reads E58's committed SRAM bursts 0.1 s long (0.625 s
  against 0.525 s, [`a1_check_e184.py`](a1_check_e184.py), [`logs/a1-check-e184.txt`](logs/a1-check-e184.txt)); E184-T's verdicts are the
  SRAM rail's (B2 moves the minion and NoC rails 1.86 and 0.12 W); E184-G counts the plain passes; five readings stated. No forecast,
  band, threshold or arm-S rule changes.
- **Device commands: `dmcmd_audit.py` GO for each arm.** Arm S ([`logs/dmcmd-audit-s.txt`](logs/dmcmd-audit-s.txt)): GO, 32 send sites,
  0 disallowed, no allow-list, every one a READ; E153's reviewed exception at `lib.sh:154` (start_sampler's forwarded arguments), as E180's
  kit has it: block_e184s.sh passes no `--reset-ms`, and E128's guard refuses one. Arm B ([`logs/dmcmd-audit-b.txt`](logs/dmcmd-audit-b.txt)):
  GO, 34 send sites, 0 disallowed, the allow-list STATS_RESET alone (`lib.sh:154`, `block_e184b.sh:81`: pass 18441's `--reset-ms 1000`). The
  desk files ([`logs/dmcmd-audit-desk.txt`](logs/dmcmd-audit-desk.txt), [`audit_desk_e184.sh`](audit_desk_e184.sh)): GO with five reviewed
  exceptions, the dry pass's two lines that run E184's guard against its own stub reader. The enercat host, patched or not, opens the card
  through the runtime only. **No stock READ returns the regulators' phase-shedding setting** (E184.md section 3).
- **The Intel dry pass, DRY-INTEL-E184 PASS** ([`logs/dry-intel-e184.txt`](logs/dry-intel-e184.txt), [`dry_intel_e184.sh`](dry_intel_e184.sh)):
  with stub binaries that refuse if run and stand-in ssh, rsync and scp that log and refuse: the harness; both preflights GO; the box build
  under V3_DRY (the patch gives the pinned file); the guards (arm S calls E128's, arm B E184's, nobody calls the reader directly; E184's guard
  passes `config`, `sample` and `sample --reset-ms 1000` and refuses `--reset-ms 500`, `loglevel` and `sptrace` with 97); all 18 passes of
  both arms through their blocks with the planned number of host processes (870 quads; 36, 36, 6, 16, 16 processes in arm B), the
  calibration's `cal.json` from stand-in bases, one reset sampler start (18441) and no stub executed; the refusals; the queue's budget and
  deadline rules; the sessions' start gates; a whole dry session of each arm; **no network call**.
- **The harness:** [`harness-e184.json`](harness-e184.json), 58 files (E184's 16 box files, lib.sh, E180's D1 test, E128's guard, the
  audit and its table, and the committed `workloads/enercat` file by file) and the pinned patched source. `check_e184.py harness`: HARNESS
  OK ([`logs/harness-check.txt`](logs/harness-check.txt)).
- **The interpreter** (kit v5's lesson): the registration's outputs and the reducer's and scorer's are byte for byte the same under
  `/usr/bin/python3` 3.9 and `python3` 3.13 ([`logs/interp-check-e184.txt`](logs/interp-check-e184.txt)); the desk commands name
  `/usr/bin/python3`.

## Builds on (the stock-take's rule for lanes, MAP section 3)

1. **Checked:** the stock-take's INVENTORY.md, read Sat 7 Nov 2026 about 11:30 PST. Public rows read: P01, P03, P08, P09, P11, L06, L08,
   L11, L23, H22, H24, H27, H28 (E184.md's block). The row ids are opaque pointers into a private inventory.
2. **Used** (each unchanged, called or sourced by path, its sha256 in `harness-e184.json` or [`SHA256SUMS-e184-kit`](SHA256SUMS-e184-kit)):
   - **E180's kit** (`tools/claims-v3/e180/`, v2 and v3): the block, session, queue, preflight, harness and dry-pass forms; its D1 test
     `others_d1_e180.sh`, sourced unchanged. *Check:* E180 ran this form on aifoundry3 on 6 Nov (42.0 card-minutes, every command a read).
   - **E128's telemetry guard** and **lib.sh** (unchanged): the sampler and the config reads.
   - **Q136(w)'s `dmcmd_audit.py` and `dmcmd_table.json`**: the audits.
   - **The energy catalogue's host** (`workloads/enercat`, copied and patched in a build tree, never edited): the quads' and bursts' launches.
   - **E58's filter model** (`tools/claims-v3/tau/taulib.py`, `tools/ettelem/deconv.py`): A1's reader, ported to pure Python and checked
     on E58's committed bursts. **Q150's reset-window reader** (`reset_minmax_bylevel.py`, `707cd2c5`): E184-M's, line for line, checked
     on September's committed windows.
   - **E164's and E171's stops** (as E172 and E180 ran them): 66 W / 72 C on card 1, 65 W / 70 C on aifoundry3.
3. **Not used:** E180's v3 runbook drivers (k6's `rb_common.sh`): not ported here (open item 1); E178's C check (the catalogue's host keeps
   no C log); the catalogue's prefill (no E184 configuration needs one).
4. **Tiers:** every file here is public tier and cites public pieces only. No NDA-tier check enters this kit.
5. **Readiness:** this block is the kit's. A verifier checks it against INVENTORY.md and the cited commits.

## Kit v5's lessons, item by item

| lesson | here |
|---|---|
| one copy of each C log | no C log exists (the catalogue's host keeps none); the collection copies each pass's gzipped files once and unpacks nothing into the data directory |
| s02 before s03 | the box steps below put the window (step 1) before the desk check (step 2) |
| the commit message scanned | this commit's message went through the public-text scan with the files; the data commit's must too (step 11) |
| a real floor-path dry case | the runner's real path runs at the desk on the patched host against a mock runtime (DESKTEST-RUNNER), and the reducer and scorer read full synthetic sessions in the box's layout |
| one window file per runbook | each arm's card day keeps its own `RB_OUT` (and so its own window file) and one shared `RB_LOCK` |
| the readers' interpreter pinned | every desk command names `/usr/bin/python3`; every output is the same under 3.13 (INTERP-E184 SAME) |

## Card-minutes and the caps

| arm | card | items | expected | cap (the queue's budget from T0) | the day's post |
|---|---|---|---|---|---|
| S | aifoundry3 card 0 | 870 quads in 11 passes | **about 125** | **135** (8,100 s, 60 s reserve) | `using aifoundry3 for 2.5 h, until ~HH:MM PST` |
| B | aifoundry1 card 1 | 113 processes in 7 passes | **about 18** | **25** (1,500 s) | `using aifoundry1 card 1 for 1 h, until ~HH:MM PST` |

A pass in flight is never cut; the queue projects each pass by the plan's estimate times the largest measured-to-planned ratio so far, plus
60 s. In arm S the scan's two passes come last, so a budget stop cuts them first. Box steps add about 30 minutes of wall time to arm S
(the build included) and 20 to arm B.

## The order on the boxes

The arms are independent: the same day on the two boxes, in either order or together, one session of ours per card, never two of ours on
aifoundry1 and never card 0. An idle login does not block (D1, the owner's ruling of 1 November 2026). The day's one post names every card
held, by section 15's rule.

## The box steps that wait for the approvals and his go (from the lab clone, after `git pull --ff-only`)

The k6 runbook drivers are not ported for E184 (open item 1), so each step is given as its command; each remote command runs from a script
file through `ssh -o BatchMode=yes -o ConnectTimeout=10 <box> 'bash -s' < <file>`, bounded, and a printed login link stops the step and is
appended to `RB_LOCK`. The trees: aifoundry3 `~/aifoundry`, aifoundry1 `~/nekko`.

1. **His go, the approvals and the window:** the day, the last start and the last end, in PST, written to this arm's `RB_OUT`.
2. **The desk check:** HEAD descends from this commit; E184's paths clean; `sha256sum -c` of `SHA256SUMS-e184-registration` and
   `SHA256SUMS-e184-kit`; `check_e184.py harness`; `plan_e184.py --check`, `make_images_e184.py --check`; no E184 data in any ref.
3. **The day's one post** (the card lane's, under the post's lock).
4. **Look first:** `et-who`, `who`, `uptime` on the box; FREE or wait (bounded, 30 minutes).
5. **Sync:** one `rsync -a -c -R` of every file `harness-e184.json` names (and `tools/claims-v3/e184/`) to the box's tree; uncommitted changes
   refuse.
6. **The build and the checks on the box:** `bash tools/claims-v3/e184/build_e184.sh` (the first compile of the patched host against the real
   runtime: if it fails, that arm does not run that day; the fix is a dated amendment), then `check_e184.py harness --binaries` and
   `preflight_e184.sh S` (or `B`): HARNESS OK and GO, else stop.
7. **Reads:** `et-lab-manifest`; the config through the arm's guard (aifoundry3: 0 W / 65 C / 600 MHz; card 1: its own); et-who clean.
8. **A V3_DRY pass on the box:** `V3_DRY=1 E184_DRY_BASES=16:30.4,24:33.1,32:35.6 bash tools/claims-v3/e184/session_e184s.sh` (or
   `V3_DEVICE=1 … session_e184b.sh`) with the day's gates: it writes the dry log only (the real session removes the dry `cal.json` at its
   start).
9. **The session:** `E184_T0=$(date +%s) E184_LATEST_START='<last start>' E184_DEADLINE='<last end>' setsid nohup bash
   tools/claims-v3/e184/session_e184s.sh > build/e184/session-S.out 2>&1 < /dev/null &` (arm B: `session_e184b.sh`, `session-B.out`), from
   a script file, only after steps 5-8 read clean today. The session runs the harness with the binaries, the preflight, the stop-path test,
   the smoke and its gate before any pass.
10. **Wait** with bounded polls of `build/e184/session-<arm>.log` (`timeout 540` inside a script, repeated).
11. **Release, then collect:** the post's release; then copy back `build/claims-v3/<card>/e184*` (aifoundry3 or aifoundry1-c1), `build/e184/`
    (the session and queue logs, `cal.json`, `dmcmd-preflight-<arm>.txt`, the configs) into a scratch `build/e184-raw/` on the Intel; reduce and
    score with `/usr/bin/python3 -B tools/claims-v3/e184/reduce_e184.py <raw> --arm S|B` and `score_e184.py`; E164's login scrub in
    `--check` form; the public-text scan of the files and of the commit message; the data directory
    `docs/reports/data/<day>-e184-sensor-validation/`; then a data verifier.

## Files, and what each builds on

| file | what | builds on |
|---|---|---|
| `run_e184.py` | the runner: quads, the calibration, bursts and holds, the live stops, the stop-path test | `e180/run_e180_v2.py` |
| `block_e184s.sh`, `block_e184b.sh` | one pass of each arm on its card | `e180/block_e180_v2.sh` |
| `session_e184s.sh`, `session_e184b.sh`, `queue_e184.sh` | the sessions with their gates; the queue with its budget | E180's |
| `preflight_e184.sh`, `audit_desk_e184.sh` | the device-command audits | E180's preflight |
| `ettelem_guard_e184.sh` | arm B's telemetry guard | `e128/ettelem_guard.sh` |
| `host_patch_e184.py`, `build_e184.sh` | the host-only change and its box build | `e180/build_e180.sh` |
| `check_e184.py`, `make_harness_e184.py`, `harness-e184.json` | the harness, post-block and smoke checks | E180's |
| `reduce_e184.py`, `tau_a1_e184.py`, `score_e184.py` | the reduction, A1's reader, the rules | e184_common.py; E58's taulib; Q150's reader |
| `fake_card_e184.py`, `selftest_score_e184.py` | synthetic sessions; the scorer's self-test | |
| `a1_check_e184.py`, `E184.md.dated-note-A1.md` | amendment A1 and its check | E58 |
| `desk/` (`desktest_host_e184.sh`, `desktest_runner_e184.py`, `mock_runtime_e184.cpp`, `stubs/`) | the host's and the runner's desk tests | |
| `dry_intel_e184.sh`, `interp_check_e184.sh` | the Intel dry pass; the interpreter check | E180's dry pass |
| `logs/` | every check above | |
| `SHA256SUMS-e184-kit` | the kit's files and logs | |

## Open items (for the verifier, the readiness critic and the records)

1. **The runbook.** E180's v3 runbook steps (on k6's `rb_common.sh`: the bounded remote calls, the login-link stop, the holder rule, the
   detached dry and build jobs, the desk-path gate) are not ported for E184's two boxes; the box steps above are their commands. A kit note
   should port them, with their desk test against a fake ssh, before the readiness critic reads E184 READY.
2. **The box build is new.** The patched host has compiled only against desk stubs; step 6 is its first compile against the real runtime.
3. **No verifier has read the registration or this kit.** Card time only on his go and fresh approvals.
4. **Arm B's B3** is read against September's aifoundry3 rows only (no same-day partner), as E184.md registers it.

## Compute

All on the Intel, desk only, through the round's local slot (`slot.sh`), one job at a time at nice 10, one core: the registration's
inputs, plan, images list and power (about 2 minutes); the scorer's self-test (2.5 minutes); the A1 check, the desk tests, the dry pass and
the interpreter check (each under 2 minutes). The host's desk compile with `clang++` and the audits ran outside the slot, each under a
minute. No Verilator bench was needed, so the mini was not used; no lab box, card or network call.

SPDX-License-Identifier: Apache-2.0
