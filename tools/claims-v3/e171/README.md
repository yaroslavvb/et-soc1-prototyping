# E171's run kit: blind pool 8 on aifoundry3 card 0 at 600 MHz, M10 primary, every session's C checked (Q142(k6); registered, not yet run)

*Thu 5 Nov 2026 (week 45), PST, on the Intel, desk only (Q142(k6)): no card was claimed, no device command was sent, no ssh to a lab box
was made. The registration is [`E171.md`](E171.md), committed first with E172's and nothing else (`4441083f`, 03:38:53 PST); the scorer
followed (`tools/claims-v3/p8-600/`, `a518aa11`, 03:55:27). It answers item 6 of the kinds page's
[section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open) (with items 8 and 9) and the Q142(r)/(p)/(d)
critic's `next` rank 2 for aifoundry3. This README is the kit's: what it holds, what was checked at the desk, the card-minutes and the
cap, the order on the box, and **the box steps that wait for the approvals and his go**. Nothing here changes a rule of E171.md.*

## What it does to predicting power and heat

It makes pool 8's blind test of M10 runnable and scorable on aifoundry3 as registered: M10's power and 4.5 s heat for 31 new kinds,
against M9, with the session's own scale against its a-priori arm, the held-out check anchors and the re-runs' level or gain. No frozen
prediction changes: every model number is Q142(x)'s (`4576fb90`). The before is M10's held-out error (floats 0.185 W; pool 7's kinds 0.205 W
on this card); the after is what the card measures.

## The freeze, in order (each before any E171 data)

| step | commit, time (PST) | what |
|---|---|---|
| 1 | `4441083f`, 03:38:53 | [`E171.md`](E171.md) (and E172's), alone |
| 2 | `a518aa11`, 03:55:27 | the P8 scorer, the C-session check and their self-test ([`../p8-600/`](../p8-600/README.md)) |
| 3 | this commit | the run kit, `plan-e171.json`, `harness-e171.json`, the device-command audits, the watcher test, the Intel dry pass, this README |

## Checked at the desk

- **The scorer** (step 2's self-test, all six parts PASS): it reproduces E163's 13 committed rule readings, intervals and verdicts with
  E163's registered seeds; its C-session check lists E163's 7 C-logged sessions and finds each checked to the end; it scores a synthetic
  session to every designed answer and refuses as registered (exit 4, 5 and 9).
- **The items and orders** (`e171_common.py --verify`): 64 pool tiles against their sha256, the five frozen pool files, a kinds pass of 84
  runs holding exactly the 64 tiles, a SHORT pass of 75 without the nine priority-2 kinds, the ten smoke items. `make_plan_e171.py` derives
  the smoke from the frozen predictions by E171.md's rule and refuses if it differs from the kit's list.
- **The watcher** ([`selftest_watcher_e171.py`](selftest_watcher_e171.py) → [`logs/selftest-watcher.txt`](logs/selftest-watcher.txt), K1-K5
  PASS): the run_hpl race's moments forced on the kinds watcher. A replaced file is read as the new file at once (never an old line at an old
  offset); an unread stop line in a replaced file is not read as current; a partial newest line gives the previous complete one; the
  watcher thread fires the board stop within 0.5 s, before and across a replacement. `watcher_q142s.py` and both amendments are pinned in
  the harness and scanned by the audit (0 send sites).
- **The device commands** ([`dmcmd-audit.txt`](dmcmd-audit.txt), [`dmcmd-audit-noexcept.txt`](dmcmd-audit-noexcept.txt),
  [`dmcmd-audit-desk.txt`](dmcmd-audit-desk.txt)): `dmcmd_audit.py` unchanged on the session's file set **GO, 32 send sites, 0 disallowed**,
  every command READ, with E153's one reviewed exception (`lib.sh:154`; NO-GO without it, exactly there, as E163's); the desk files (the
  reducer, the collector, the plan and harness makers, the dry pass, the watcher test and the scorer's three files) send nothing (GO, 0
  sites). The statistics reset is never sent. The box's patched host source is scanned on the box by the preflight, as E163's was.
- **A V3_DRY dry pass on the Intel** (`dry_intel_e171.sh` → [`logs/dry-intel.txt`](logs/dry-intel.txt); a scratch copy of the tree, stub
  binaries that refuse if executed, `hostname` shimmed to aifoundry3, GNU `date`, and stand-in `ssh`, `rsync` and `scp` that log and refuse;
  no device opened): `check_e171.py` HARNESS OK, the preflight GO, `e171_common.py --verify` 0 problems; a kinds pass (86 launches through
  the C wrapper), a SHORT pass (77), the smoke (10); the queue's budget, deadline and plan rules; the session's three start gates (exit 8,
  no device opened); **no network call**. **DRY-INTEL PASS.**
- The public-text scan over every file (the lab's fixed list and the lane's; the privacy table is absent on the Intel).

## Card-minutes and the cap

| plan (`E171_PLAN`) | sequence | expected | cap (the budget rule) | the day's post says |
|---|---|---|---|---|
| **FULL** (default) | 17110, 17111, 17112, then 17113 if it fits | **about 60-62** (four passes; 45-46 with three) | **70** (4,200 s, 60 s reserve) | `for 1.5 h` |
| TWO (the registered subset for a short window) | 17110, 17111 | about 31 | 38 | `for 1 h` |
| SHORT | 17120, 17121 (75-run passes) | about 28 | 30 | `for 1 h` |

From E163's measured session on this card (its 99-launch kinds passes took 1,001-1,025 s) scaled to 86 launches: 870-890 s a pass; the
stop-path test and the smoke about 62 s. The queue's first estimate is 900 s a kinds pass, then the longest measured; at that speed the
fourth pass fits (it ends near T0+3,650 s against 4,140 s) and a fifth would not.

## The order on aifoundry3

E171 alone on aifoundry3 (nothing else of ours there on the card day). It starts with `et-who` clean; an idle login does not block (D1).

## The box steps that wait for the approvals and his go

Everything above is done. These remain, in order, each a read or a dry run until the session starts. Every remote call is
`ssh -o BatchMode=yes -o ConnectTimeout=10 aifoundry3 'bash -s' < <script file>` or an rsync with
`-e 'ssh -o BatchMode=yes -o ConnectTimeout=10'`, from the lab clone after `git pull --ff-only`; the runbook's steps
([`../q141k-runbook/k6/`](../q141k-runbook/k6/README.md)) wrap each one with the 15 s probe, the bounds and the login-link stop.

1. **Fresh network approvals** for aifoundry3 and his go with the round's time gates (a printed login link stops the step).
2. **The day's one post** in `#community-lab` (section 15's rule: the clauses held now plus `using aifoundry3 for 1.5 h, until ~HH:MM PST
   [doc](<https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers>)`, rewritten with EXPECT_TEXT under the post's lock).
3. **Look first** on aifoundry3: `et-who`, `who`, `uptime`; no process holds a device node or card 0's lock.
4. **Sync** into `~/aifoundry` (the binaries tree E163 ran from): `rsync -a -c -R --exclude __pycache__ -e 'ssh -o BatchMode=yes -o
   ConnectTimeout=10' tools/claims-v3/e171/ tools/claims-v3/kinds/blind8/ tools/claims-v3/hpl/watcher_q142s.py
   tools/claims-v3/hpl/run_hpl.py.dated-note.md tools/claims-v3/hpl/run_hpl.py.dated-note-2.md aifoundry3:aifoundry/` (the reused card
   code, the ccheck files, the guard and the host source must already be there unchanged: the check below says so).
5. **Pool 8's hashes on the box**: `(cd tools/claims-v3/kinds/blind8 && sha256sum -c SHA256SUMS)` → 89 OK.
6. **The harness and the C-logging host**: `python3 -B tools/claims-v3/e171/check_e171.py` → `HARNESS OK: 101 files` (E163's four binaries
   among them). If a binary differs, stop: a dated amendment beside E171.md registers the new one before the claim.
7. **The preflight on the box**: `bash tools/claims-v3/e171/preflight_e171.sh` → GO; `python3 -B tools/claims-v3/e171/e171_common.py --verify`
   → 0 problems.
8. **A V3_DRY pass on the box** (no device): `V3_DRY=1 bash tools/claims-v3/e171/block_e171.sh 17110` (86 launches through the wrapper),
   `… 17101 --smoke` (10); the session's start gate refusing (exit 8) with a past `E171_LATEST_START`.
9. **`et-lab-manifest`** read and kept, and **`et-who`** clean once more.
10. **The session**, detached, from a script file, in `~/aifoundry`:
    `E171_T0=$(date +%s) E171_PLAN=FULL E171_LATEST_START='<the round's last start>' E171_DEADLINE='<the round's last end>' setsid nohup bash
    tools/claims-v3/e171/session_e171.sh > build/e171/session.out 2>&1 < /dev/null &`. It runs the check, the preflight, the stop-path test
    (17102) and the smoke (17101) with its gate before any pass; any failure opens no further device.
11. **Release and collect**: on `queue: … done`, the post's release; copy `build/claims-v3/aifoundry3/{e171,e171-smoke,e171-stoptest}` and
    `build/e171/` (as `logs/`) into **`build/e171-raw`** (repo-relative: the reducer records the pass directories as given); then
    `PY=/usr/bin/python3 nice -n 10 bash tools/claims-v3/e171/collect_e171.sh build/e171-raw` → `build/e171-out/<day>-e171-blind8-aifoundry3/`;
    the C-session gate (`python3 -B tools/claims-v3/p8-600/ccsessions_p8.py --run E171 --raw build/e171-raw --ccheck <out>/ccheck/ccheck-all.json`,
    exit 0 or nothing is scored as registered), the login check of `logs/` and the desk-path gate; then the data directory
    `docs/reports/data/<day>-e171-blind8-aifoundry3/`. KA pooled reads after E172 is collected:
    `score_p8_600.py ka-pooled <E171 scored.json> <E172 scored.json>`.

## Files

`E171.md` (the registration); `plan-e171.json`, `make_plan_e171.py` (the plan in machine form); `e171_common.py`, `run_e171.py`,
`block_e171.sh`, `queue_e171.sh`, `session_e171.sh`, `check_e171.py`, `preflight_e171.sh`, `smoke_gate_e171.py` (the box); `reduce_e171.py`,
`collect_e171.sh` (the desk); `make_harness_e171.py`, `harness-e171.json`; `dmcmd-audit.txt`, `dmcmd-audit-noexcept.txt`,
`dmcmd-audit-desk.txt`; `selftest_watcher_e171.py`, `logs/selftest-watcher.txt`; `dry_intel_e171.sh`, `logs/dry-intel.txt`; this README.
The scorer is `../p8-600/`.

## Compute

The Intel, every Python and dry run through the round's local slot, one at a time, at nice 10: the plan maker, the item check, the watcher
test (once in development, once committed), the harness maker, the dry pass (about a minute) and the three audits. No lab box, no mini job.

SPDX-License-Identifier: Apache-2.0
