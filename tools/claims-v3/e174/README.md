# E174's run kit: blind pool 8 on aifoundry1 card 0 under its own governor, in E170's form, checked at the desk, ready for the box steps after E172 (Q142(kg))

*Thu 5 Nov 2026 (week 45), PST, on the Intel, desk only: no card claimed, no device command sent, no lab box reached, nothing measured. It answers
the Q142(r)/(p)/(d) critic's `next` rank 2 for card 0 (E170's form, its admission and 66 W / 72 C stops), on the kinds page's
[section 11, item 6](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open), and the Q142 critic's fault 3. The rules are
registered in [`E174.md`](E174.md) (lab **`c8064454`**, 03:45:13 PST), the scorer and its self-test in **`99e5777e`** (03:54:39), this kit in the
commit that adds this README.*

## What it does to predicting power and heat

Nothing yet: it makes E174 runnable and scorable as registered. E174 then gives M10 carried's first blind power score on card 0 (21 new kinds:
fp32 4, fp16 5, int8 12; C0-W, C0-B), against M9 carried on the same bursts (C0-M1), and **term c2's second session**, blind (C0-H1 on the predicted
board; C0-HK at the measured board, 0.2415 against 0.1400 C per W). Before: E170 (pool 7, M9 carried) read the board 0.727 W rms, mean -0.090 W,
and the burst rise about 0.24 C per board W, from which M10 fitted c2 in sample.

## Ready, and what waits

| step | state |
|---|---|
| registration, frozen inputs (32), E170's admission on pool 8 (39 admitted, 25 left out by name), tiers, order, lines at the scored n (21), stops | **committed** (`c8064454`) |
| the scorer and its self-test | **committed** (`99e5777e`): [`selftest-score.txt`](selftest-score.txt), 22 of 22, E170's committed session reproduced (anchors, the primary on 39 tiles, W 0.7274 / -0.0896 W, F 3.9773 MHz, the rise 2.4566 C, M1 -0.1582 [-0.2423, -0.0944], E170's own lines; c2's 39 residuals at 0.3385 C), made-up sessions with known verdicts, every registered refusal |
| the run kit | **this commit**: [`make_protocol_e174.py`](make_protocol_e174.py) → `protocol*.json` ([`protocol.txt`](protocol.txt)); [`run_e174.py`](run_e174.py) (E170's runner ported, the watcher fix installed); [`queue_e174.py`](queue_e174.py) (E170's queue: the state gate, the stop tests first, the ramped smoke); [`make_harness_e174.py`](make_harness_e174.py) → [`harness-e174.json`](harness-e174.json) (110 files, 3 binaries) and [`check_e174.py`](check_e174.py); [`preflight_e174.sh`](preflight_e174.sh); [`box/`](box/) (look, check, launch, wait, and the step driver); [`collect_e174.sh`](collect_e174.sh) |
| device commands | **GO**: 33 send sites, all READ, 0 disallowed, E170's one reviewed exception (`run_hpl.py:622`, the residency query E170's guard refuses before the reader starts) ([`logs/dmcmd-audit.txt`](logs/dmcmd-audit.txt)); NO-GO on that line only without it ([`logs/dmcmd-audit-noexcept.txt`](logs/dmcmd-audit-noexcept.txt)) |
| the kit's self-test | [`logs/selftest-kit.txt`](logs/selftest-kit.txt): ALL PASS (the protocols against the order, the tiers and the hottest last, the admission at 60 W, the runner's refusals, the stop tests and the ramped smoke, the watcher installed, the harness, the state gate's helpers on E170's committed read, `launch_e174.sh`'s 15 refusal cases in a sandbox, `bash -n`) |
| the dry pass on the Intel | [`logs/drypass-intel.txt`](logs/drypass-intel.txt): the whole queue on the toy card: the state gate GO with nothing read (dry: no et-holders, uptime or ettelem read), stoptest-die exit 4 before any launch, stoptest-board exit 4 inside its launch, the ramped smoke rc 0 (no line under 590 MHz or over the stop), s1 24 runs rc 0, the watcher's record in `e174.json`; then `score_e174.py`: every P8 rule NOT SCORED at the dry twin's 6 tiles, E174-S PASS |
| the box steps, through the ported runbook | [`box/step_e174.sh`](box/step_e174.sh) over [`../q142kg-runbook/`](../q142kg-runbook/README.md): its desk test (28 of 28) and dry listing (16 of 16 steps, no call) |
| everything on the box | waits for **E172's end** on card 1, the owner's go, fresh lab approvals and the day's post |

## Card-minutes and the cap

**About 28 card-minutes; the cap is 40, the slot 45 minutes** (E170's). 126 bursts at E170's measured 12.58 s a burst (its s1: 135 bursts in 28.30
min) is 26.4 min, plus the state reads, the two stop-path tests and the ramped smoke (E170: 0.91 min). **The registered subset**
(`protocol-subset.json`: passes 1, 2, 4 and 5, 84 bursts, about 18 min): `launch subset`, cap 25, a 30-minute slot.

## The order on the box and the window

- **After E172 has ended** on card 1: never two sessions of ours on aifoundry1. `launch_e174.sh` refuses (exit 3) while anything of ours holds either
  card's node or lock, runs a device process, or runs a queue or session (`queue_`, `session_`, `block_` or `run_eNNN`), and `queue_e174.py`'s state
  gate refuses a held node or lock again. E172's kit, committed by the k6 lane at `14fcb30d` after this one was written, runs `queue_e172.sh`,
  `session_e172.sh`, `block_e172.sh` and `run_e172.py`. That pattern matches all four, as does the runbook's `ours_live`.
- **The window** is the day's (the runbook's window file: no start after the last start, every run ends by the last end); the launch takes it as
  arguments and refuses (exit 6) outside it, reading the clock again just before it launches.
- **On the box, in the queue's order**: card 0's state gate (et-holders; the host's boot before E84's read; the module uptime's continuity with
  E84's identity read; `ettelem config` 65 W / 65 C at 600 MHz), the die and board stop-path tests, the ramped smoke (rest, `int8.anchor7_zeros`,
  `fp32.b_onebit_b20_one`), then the session (half A, then half B, the hottest kinds last). A NO-GO, a failed stop test or smoke: QUEUE-HALT, card 0
  idle. A safety stop or the alarm inside the session (exit 4) ends the session and the queue.

## The box steps, in order

First `export RB_OUT=<this card day's directory, outside the repo> RB_LOCK=<the round's lock file>` and, once,
`bash tools/claims-v3/q142kg-runbook/s02_window_q142kg.sh <day> <last start> <last end>`.

1. `bash tools/claims-v3/e174/box/step_e174.sh look`: the host's boot against E84's read, et-who (card 0's lines empty; nothing of ours on card 1),
   E172's end if its records are on the box, the logins, `/home`'s room, the three binaries against their pins, our device processes (none).
2. `... sync`: one `rsync -a -c -R` of E174's harness files into `aifoundry1:nekko/` (only after E172 has ended; only a clean, pushed tree).
3. `... check`: `check_e174.py` **HARNESS OK 110 + 3 binaries**; `preflight_e174.sh` **GO**; the tiles; pool 8's `SHA256SUMS` 89 OK; the box's dry
   pass (stoptest-die rc 4, smoke rc 0, 126 runs listed). Never during a session of ours on aifoundry1.
4. The day's one post (the card lanes, under the post's lock): aifoundry1's clause covers both cards.
5. `... launch` (or `... launch subset`): `ssh ... "bash -s -- '<deadline>' '<last start>' '<last end>' [subset]" < box/launch_e174.sh`, the times
   from the window file (the deadline is the last end less 5 minutes). Its refusals open nothing (exit 2, 3, 4, 5, 6, 9; IDENTITY-STOP is 16 at
   the step). It detaches `queue_e174.py` and prints `LAUNCHED e174 T0=...`.
6. `... wait`, repeated: 0 ended (read `queue.jsonl`'s `s1_end` rc and `s1/end.json`), 16 halted, 17 still running. Then the day's post.
7. `... pull`: a bounded copy of `aifoundry1:nekko/build/e174/` into `build/e174-raw/`.
8. `... collect`, at the desk: [`collect_e174.sh`](collect_e174.sh) (the harness check, the check of C on every session with a C log, **the C-log
   list**, E164's login scrub and its check, the data directory `docs/reports/data/<day>-e174-blind8-card0/`, `score_e174.py`), then **the C-log
   gate** and **the desk-path gate**. Then the public-text scan, then the data commit.

## Files

| file | runs where | what |
|---|---|---|
| [`E174.md`](E174.md), `e174_common.py`, `make_predictions_e174.py` → `frozen-sha256-e174.json`, `predictions-e174.json`, `.txt` | desk (the box imports `e174_common`) | the registration (`c8064454`) |
| `score_e174.py`, `selftest_score_e174.py` → `selftest-score.txt` | desk | the scorer and its self-test (`99e5777e`; the shared engine is `../e173/p8gov.py`) |
| `run_e174.py`, `queue_e174.py`, `check_e174.py`, `preflight_e174.sh`, `box/look_e174.sh`, `box/check_box_e174.sh`, `box/launch_e174.sh`, `box/wait_e174.sh` | box | the runner, the queue, the harness check, the audit, the box steps' scripts |
| `make_protocol_e174.py` → `protocol*.json`, `protocol.txt`; `make_harness_e174.py` → `harness-e174.json` | desk | the protocols, the hashes |
| `collect_e174.sh`, `box/step_e174.sh` | desk | the collector and the step driver |
| `selftest_kit_e174.py`, `drypass_intel_e174.sh`, `logs/` | desk | the kit's self-test, the dry pass, the audits |

## What this cannot say

The kit is ported and dry-run, not run: nothing here has opened card 0. If "the fix" reset or reflashed card 0, the module uptime shows it and E174
does not start (NO-GO on the day, card 0 idle): the running image could not be named without the firmware-revisions query, which is never sent.

SPDX-License-Identifier: Apache-2.0
