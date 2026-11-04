# E163's run kit: blind pool 7 on aifoundry3 card 0, M9 primary, with rank 14's C-checked re-runs (Q141(a); registered, not yet run)

*Wed 4 Nov 2026 (week 45), PST, on the Intel, desk only (Q141(a), the card half's desk preparation): no card was claimed, no device
command was sent, no ssh to a lab box was made. The registration is [`E163.md`](E163.md), committed first and alone in `64dff136`
(09:33:22 PST); it answers item 6 of the kinds page's
[section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open) and Q140's final critic's `card_half[0]`
with its `desk_next` 1 and 7. This README is the kit's: what it holds, what was checked at the desk, the card-minutes and the cap, the
order on the box, and **the box steps that wait for the approvals and his go**. Nothing here changes a rule of E163.md.*

## What it does to predicting power and heat

It makes rank 1's blind test scorable on aifoundry3: M9's power for 48 new kinds against M6 (resolved below zero or not), M8 and M7,
its bias, its bands' coverage, its 4.5 s heat, per class (S, E, L, H, U, R), and rank 9's real tiles; it gives rank 4's paired-anchor
scale its reference half; and it tests whether 22 earlier file-tile rows (pool 5's 10, E152's 6, E151's 6) reproduce with their C
checked (rank 14). **No frozen prediction changes**: every model number is Q140(x)'s (`75802201`), the reference errors are M9's own
(`1f244140`), and the freeze only copies them (`predictions-e163.json`). The before is M9's nested error on aifoundry3's rows, 0.200 /
0.168 / 0.169 W (fp32 / fp16 / int8), out of kind; the after is what the card measures.

## The freeze, in order (each before any E163 data)

| step | commit, time (PST) | what |
|---|---|---|
| 1 | `64dff136`, 09:33:22 | [`E163.md`](E163.md), the registration, alone |
| 2 | `442474d5`, 09:38:32 | `ref_errors_e163.py` → `ref-errors-m9.json` (M9's nested errors from `rows-m9.json`, every pool equal to `m9.json`'s; `--recompute` through `fit_m9.run_family` equal row by row: `logs/ref-errors-recompute.txt`); `rerun_ref_e163.py` → `rerun-ref.json`, `rerun-ref/` (the 16 + 6 re-run picks and their earlier values; E152 re-reduced on the footing); `make_predictions_e163.py` → `predictions-e163.json`, `planned-intervals.txt`; `score_e163.py`; `selftest_e163.py` → `selftest-parent-e153.txt`, `selftest.txt` |
| 3 | this commit | the run kit, `harness-e163.json`, the device-command audits, the Intel dry pass, this README |

| file | sha256 |
|---|---|
| `E163.md` | `517e6cc330ce7cf5838a947846d5b986d8b23c609dd6493f8313ae506810e28c` |
| `predictions-e163.json` | `b4e4d3cef730f750ed9d2289a3c97d9ae6a7a7fc4656e259e13d90f79b6e8b4b` |
| `rerun-ref.json` | `13ebe905b74cf32d176c22da8c134cd93dee1754f082abe9456e33423d90ced1` |
| `ref-errors-m9.json` | `d9e3a2f3d0cc0ed70eee5e3cd5ed389052a74914d0b972b80c43e8e11ab56b73` |
| `score_e163.py` | `da92a03de17ba157c0d952607ba65c3d47c05e85f7b3c2b319d8be5a06d9e561` |
| `harness-e163.json` | `8ed3461f468f59a93e90da1dc88aa697f6ca17332eb3aa3779f41366e9eda1e8` (142 files: 14 reused card files equal to E153's registered values, 9 E163 card files, 3 registration files, 3 of E151's, 109 pool files and tiles, E153's 4 box binaries) |

## Checked at the desk

- **The scorer against its parent** (`selftest-parent-e153.txt`): `score_e163.py` configured as E153's registration (M8 primary, pool 6, K1,
  the card-scale rules) on E153's committed reduction, its seven arms, its C check and raw passes gives E153's committed `scored.json`
  exactly: **SELFTEST-PARENT PASS, 9,853 fields, 0 differ**, all 23 registered verdicts (P1 FAIL, M2 WORSE, K1 PASS, …).
- **The scorer on E163's freeze** (`selftest.txt`): 40 simulated sessions a world; the C-check plumbing; the E151 block's path end to end
  (E151's own committed blocks, renumbered to 16351-16359, score as an exact repeat: KE-D and KE-W PASS, largest difference 0.0 W); a
  results page renders; `score_rank4.py` reads the output (all nine anchors, per-pass values) and scores a self-pair PASS.
- **M9's reference errors** reproduce `m9.json`'s pools to 1e-9 W, and `fit_m9.run_family` re-run unchanged gives them row by row (0.0 W).
- **The device commands** (`dmcmd-audit.txt`, `dmcmd-audit-noexcept.txt`, `dmcmd-audit-desk.txt`): `dmcmd_audit.py` unchanged on the
  session's file set **GO, 32 send sites, 0 disallowed**, every command READ, with E153's one reviewed exception (`lib.sh:154`, the
  conditional `--reset-ms` forward no E163 call uses; NO-GO without it, as E153's); the findings equal E153's audit bar the names; the
  desk files and the patched host source (`5bd029ca…`, as `build_host_ccheck.sh` makes it, E153's) send nothing (GO, 0 sites). The
  statistics reset is never sent.
- **A V3_DRY dry pass on the Intel** (`dry_intel_e163.sh` → [`logs/dry-intel.txt`](logs/dry-intel.txt); a scratch copy of the tree,
  stub binaries that refuse if executed, `hostname` shimmed to aifoundry3 and GNU `date`; no device opened, no ssh): `check_e163.py`
  HARNESS OK (138 files; binaries not checked in a dry run), the preflight GO, `e163_common.py --verify` 0 problems; one kinds pass
  (99 launches through the C wrapper: 97 runs and 2 burn-ins), one SHORT pass (79), one E151 block (34 trains runs, E151's stops 45 W /
  68 °C), the smoke (12); the queue's budget rule (two 3 s stubs, then "budget: stopping"), its deadline rule, its plan check; the
  session's three start gates (exit 8, no device opened). **DRY-INTEL PASS.**
- The public-text scan over every file (the lab's fixed list and the brief's; the privacy table is absent on the Intel).

## Card-minutes and the cap

| plan (`E163_PLAN`) | sequence | expected | cap (the budget rule) | the day's post says |
|---|---|---|---|---|
| **FULL** (default) | 16310, 16311, 16312, the E151 block 16350-16352, then 16313 only if it fits | **about 56-59** | **70** (4,200 s, 60 s reserve) | `for 1.5 h` |
| TWO (the registered subset for a short window) | 16310, 16311 | about 31-33 | 38 | `for 1 h` |
| SHORT | 16320, 16321 (77-run passes: the four priority-2 tests and the 16 re-runs dropped) | about 25-27 | 30 | `for 1 h` |

From E153's measured session: the stop-path test and the smoke about 70 s; a 97-run kinds pass about 892-947 s (E153's 703-746 s for 78
launches-runs, scaled to 99); an E151 block about 182 s (E151's start to start). At E153's speed the fourth pass does not fit after the
E151 block (about 4,240-4,460 s against 4,140), so FULL is in practice three passes and the block. Q140's critic estimated "49-64 with
the 16 in-pass re-runs; about 10 more for an E151 block; a 70-minute cap".

## The order on aifoundry3

**After E166** (E166's room gate needs a rested card; E163's kinds protocol heats to 59 °C before every launch, so it needs no rest), at
once, in the same reservation if the window allows. If only a short window is free, E163 runs instead of E166 (Q140's critic, subset
(a)), FULL if 75 minutes are free, else TWO. Never with another session of ours on aifoundry3. Rank 4 is scored after E164 (aifoundry1
card 1) by `tools/claims-v3/kinds/blind7/score_rank4.py --a3 <E163's scored.json> --c1 <E164's> --pair E163/E164`.

## The box steps that wait for the approvals and his go

Everything above is done. These remain, in order, and each is a read or a dry run until the session starts:

1. **Fresh network approvals** of the lab boxes' access checks for aifoundry3 (every ssh `-o BatchMode=yes -o ConnectTimeout=10`; a printed login link stops the lane),
   and his go with the round's time gates.
2. **The day's one post** in `#community-lab` (section 15's rule: the clauses held now plus
   `using aifoundry3 for 1.5 h, until ~HH:MM PST [doc](<https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers>)`, rewritten with
   EXPECT_TEXT under the Discord lock; the release later drops the clause or appends " — released").
3. **Look first** on aifoundry3: `et-who`, `who`, `uptime`; no process holds a device node or card 0's lock (an idle login does not block,
   D1); E166's session ended and its lock is free.
4. **Sync the tree the harness expects**: aifoundry3's `~/aifoundry` (the binaries tree E153 ran from). From the Intel, after
   `git -C ~/git/et-soc1-prototyping pull --ff-only`: `rsync -a -c --exclude __pycache__` these paths to the same paths under
   `aifoundry3:aifoundry/`: `tools/claims-v3/e163/`, `tools/claims-v3/kinds/blind7/`, `tools/claims-v3/kinds/blind5/`,
   `tools/claims-v3/kinds/e130/`, `tools/claims-v3/e152/`, `tools/claims-v3/e151/`, `tools/claims-v3/ccheck/`, `tools/claims-v3/dmcmd_audit.py`,
   `tools/claims-v3/dmcmd_table.json` (the reused card code, `lib.sh`, `kinds/e78_common.py`, `run_e78.py`, `reduce_e78.py`, `kinds.json`,
   `e128/ettelem_guard.sh` and `workloads/sparsity/host/main.cpp`, must already be there unchanged: the check below says so).
5. **Pool 7's hashes on the box**: `(cd tools/claims-v3/kinds/blind7 && sha256sum -c SHA256SUMS)` → 91 OK.
6. **The C-logging host present**: `build/ccheck/b/host/sparsity_host` (E153's, `99ed75fb…`), with the kernel `build/sparsity/kernel/sparsity.elf`
   (`d521e432…`), the heater `build/sparsity/host/sparsity_host` (`20e760c2…`) and `build/ettelem/ettelem` (`16037641…`):
   `python3 tools/claims-v3/e163/check_e163.py` → `HARNESS OK: 142 files`. If a binary differs or is missing, stop: rebuilding the C-logging
   host (`tools/claims-v3/ccheck/build_host_ccheck.sh`, no device) changes its hash, and a dated amendment beside E163.md must register the
   new one before the claim.
7. **The preflight on the box**: `bash tools/claims-v3/e163/preflight_e163.sh` → GO (it scans the patched host source
   `build/ccheck/src/host/main.cpp` there too); `python3 tools/claims-v3/e163/e163_common.py --verify` → 0 problems.
8. **A V3_DRY pass on the box** (no device): `V3_DRY=1 bash tools/claims-v3/e163/block_e163.sh 16310` (99 launches through the wrapper),
   `… 16350` (34), `… 16301 --smoke` (12); and the session's start gate refusing (exit 8) with a past `E163_LATEST_START`.
9. **`et-lab-manifest`** read and kept (aifoundry3 runs a non-public thermal firmware build first flashed on 7 Oct 2026; the device-command
   classes rest on et-platform `836a4ab`'s handlers, and the smoke gate fails if the config or telemetry comes back in another form), and
   **`et-who`** clean once more.
10. **The session**, detached, from a script file run by `ssh aifoundry3 'bash -s' < file`, from `~/aifoundry`:
    `E163_T0=$(date +%s) E163_PLAN=FULL E163_LATEST_START='<the round's last start>' E163_DEADLINE='<the round's last end>' setsid nohup bash tools/claims-v3/e163/session_e163.sh > build/e163/session.out 2>&1 < /dev/null &`.
    The session runs the check, the preflight, the stop-path test (16302) and the smoke (16301) with its gate before any pass; any
    failure opens no further device. Waits are bounded remote waits (`timeout 540` inside a script), never a long local sleep.
11. **Release and collect**: on `queue: … done`, the post's release (section 15); copy `build/claims-v3/aifoundry3/{e163,e163-smoke,e163-stoptest}`
    and `build/e163/` (as `logs/`) to the Intel; `PY=/usr/bin/python3 nice -n 10 bash tools/claims-v3/e163/collect_e163.sh <copy> [<Q141(t)'s
    arm as {tile: D_w}>]` → `build/e163-out/<date>-e163-blind7-aifoundry3/`, the data directory `docs/reports/data/<date>-e163-blind7-aifoundry3/`.

## Files

`E163.md` (the registration); `predictions-e163.json`, `planned-intervals.txt`, `make_predictions_e163.py` (the freeze); `ref_errors_e163.py`,
`ref-errors-m9.json`, `logs/ref-errors-recompute.txt` (M9's reference errors); `rerun_ref_e163.py`, `rerun-ref.json`, `rerun-ref/` (rank 14's
picks and earlier values); `score_e163.py`, `selftest_e163.py`, `selftest-parent-e153.txt`, `selftest.txt` (the scorer and its self-tests);
`e163_common.py`, `run_e163.py`, `block_e163.sh`, `queue_e163.sh`, `session_e163.sh`, `check_e163.py`, `preflight_e163.sh`,
`smoke_gate_e163.py` (the box); `reduce_e163.py`, `collect_e163.sh` (the desk); `make_harness_e163.py`, `harness-e163.json`;
`dmcmd-audit.txt`, `dmcmd-audit-noexcept.txt`, `dmcmd-audit-desk.txt`; `dry_intel_e163.sh`, `logs/dry-intel.txt`; this README.

SPDX-License-Identifier: Apache-2.0
