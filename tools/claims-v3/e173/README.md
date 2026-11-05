# E173's run kit: blind pool 8 under aifoundry2's own governor, in E165's form, checked at the desk, ready for the box steps (Q142(kg))

*Thu 5 Nov 2026 (week 45), PST, on the Intel, desk only: no card claimed, no device command sent, no lab box reached, nothing measured. It answers
the Q142(r)/(p)/(d) critic's `next` rank 2 (pool 8's card kits and section-7 scorers) for aifoundry2, on the kinds page's
[section 11, item 6](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open), and the Q142 critic's fault 3 (a session with
no C log was skipped). The rules are registered in [`E173.md`](E173.md) (lab **`c8064454`**, 03:45:13 PST), the scorer and its self-test in
**`99e5777e`** (03:54:39), this kit in the commit that adds this README.*

## What it does to predicting power and heat

Nothing yet: it makes E173 runnable and scorable as registered. E173 then gives M10's first blind score under a governor (M10 carried by rule E
through M9's aifoundry2 part), on 24 new kinds of pool 8 (3 governed, 21 pinned), against M9's part on M9's D on the same bursts (P8-A2-M1), and
the burst heat law's blind error on a third pool (P8-A2-H1). Before: E165 (pool 7, M9's part) read the governed clock 3.03 MHz, the governed board
0.71 W, the pinned board 0.99 W and the die rise 0.455 C. The governed rules (A2-G, Bg, F1, W1) read NOT SCORED at 3 governed tiles; A2-R2 can read
only FAIL (through Bp) or NOT SCORED (E173.md, "The governed group").

## Ready, and what waits

| step | state |
|---|---|
| registration, frozen inputs (26, each matched against a committed list), sets, order, lines, stops | **committed** (`c8064454`), descending from pool 8's freeze `4576fb90` / `ebf68c52` / `dfe226f1` and the predictor `3e97f583` / `8a8fa34c` / `9d81d254` / `68a7c322` / `97765c0a` |
| the scorer and its self-test | **committed** (`99e5777e`): [`selftest-score.txt`](selftest-score.txt), 34 of 34, E165's committed session reproduced (anchors, the primary on 52 tiles, A2-G / Bg / Bp's lines, F1-F2, W1-W2, H1's rms; E165's own lines), made-up sessions with known verdicts, every registered refusal |
| the run kit | **this commit**: [`make_protocol_e173.py`](make_protocol_e173.py) → `protocol*.json` ([`protocol.txt`](protocol.txt)); [`run_e173.py`](run_e173.py) (the watcher fix installed); [`queue_e173.py`](queue_e173.py); [`make_harness_e173.py`](make_harness_e173.py) → [`harness-e173.json`](harness-e173.json) (135 files, 3 binaries) and [`check_e173.py`](check_e173.py); [`preflight_e173.sh`](preflight_e173.sh); [`collect_e173_bounded.sh`](collect_e173_bounded.sh); [`box/step_e173.sh`](box/step_e173.sh) |
| device commands | **GO**: 19 send sites, all READ, 0 disallowed, E165's one reviewed exception (`run_hpl.py:622`, the residency query this ettelem refuses before it opens the device) ([`logs/dmcmd-audit.txt`](logs/dmcmd-audit.txt)); NO-GO on that line only without it ([`logs/dmcmd-audit-noexcept.txt`](logs/dmcmd-audit-noexcept.txt)); the desk files: GO, no send site (`../q142kg-runbook/logs/dmcmd-audit-desk.txt`) |
| the kit's self-test | [`logs/selftest-kit.txt`](logs/selftest-kit.txt): ALL PASS (the protocols against the order, the admission, the runner's refusals, the stop tests and smoke, the watcher installed, the harness, `bash -n`) |
| the dry pass on the Intel | [`logs/drypass-intel.txt`](logs/drypass-intel.txt): the whole queue on `run_hpl.py`'s toy card (no device, no lock, no ssh): the smoke rc 0, stoptest-board exit 4 for "board" inside its launch, stoptest-die exit 4 for "die" before any launch, s1 22 runs rc 0, the watcher's record in `e173.json`; then `score_e173.py` on the dry s1: every P8 rule NOT SCORED at the dry twin's 3 + 3 tiles, as registered |
| the box steps, through the ported runbook | [`box/step_e173.sh`](box/step_e173.sh) over [`../q142kg-runbook/`](../q142kg-runbook/README.md): its desk test with a stand-in ssh and rsync (28 of 28) and its dry listing (16 of 16 steps, no call) |
| everything on the box | waits for the owner's go, fresh lab approvals and the day's post |

## Card-minutes and the cap

**About 40 card-minutes; the cap is 42, the slot 48 minutes.** 165 bursts at E165's measured 14.26 s a burst (its s1: 158 bursts in 37.55 min) is
39.2 min, plus the smoke and the two stop-path tests (E165: 0.97 min). `run_e119.py` starts a run only if its planned time fits the cap, so a slow day
cuts pass 3's tail, never a run in flight. **The registered subset** (`protocol-subset.json`: passes 1-2, 110 bursts, about 26 min): `launch
subset`, cap 28, a 34-minute slot. On aifoundry2 E173 is the card day's only run of ours.

## The box steps, in order

Each runs on the Intel from the top of the lab clone through the ported runbook (a 15 s probe; every call bounded; a login link kills the call and
appends `<HH:MM:SS> aifoundry2 needs a check` to `$RB_LOCK`). First `export RB_OUT=<this card day's directory, outside the repo> RB_LOCK=<the round's
lock file>` and, once, `bash tools/claims-v3/q142kg-runbook/s02_window_q142kg.sh <day> <last start> <last end>`.

1. `bash tools/claims-v3/e173/box/step_e173.sh look`: et-who, who, uptime, the identity by host-boot continuity (before E69's firmware read of
   2026-10-27 13:56:26 PDT), the holder rule (an idle login does not block). 0 free; 16 the identity stop; 17 held.
2. `... tree`: `git pull --ff-only`; `git merge-base --is-ancestor $RB_BASE HEAD` (default `c8064454`; pass `RB_BASE=<this kit's commit>` on the
   day); `tools/claims-v3` clean; then `check_e173.py` **HARNESS OK 135 + 3 binaries**, `e173_common.py` 64 tiles OK, blind8 89 OK,
   `preflight_e173.sh` **GO**, `run_e173.py --list` 165 runs. A rebuilt binary has another sha256: a dated amendment first.
3. `... dry start`, then `... dry wait` (repeated until 0): the box's dry pass (the toy card, about 3 minutes), a detached job; never during a session.
4. The day's one post (the card lanes, under the post's lock): aifoundry2's clause, before the first launch.
5. `... launch` (or `... launch subset`): inside the day's window (no start after the last start; the slot must end by the last end), with v3.1's
   guard on the box (no dry pass running, no session of ours, the identity) and today's dry pass ended rc 0; it writes the slot file and detaches
   `queue_e173.py --cap 42` (the subset: `--cap 28 --protocol protocol-subset.json`). The queue runs the smoke, the DMA rule and both stop-path tests
   itself, and halts with QUEUE-HALT and no session if any fails.
6. `... wait`, repeated: one bounded wait (520 s by the box's clock); 0 ended, 16 a gate stopped it, 17 still running. Then the day's post drops the
   clause (or appends " — released" if it is the last one held).
7. `... collect`, at the desk: [`collect_e173_bounded.sh`](collect_e173_bounded.sh) (the harness check, its own probe, every remote call under
   600 s, the box's file hashes, Q139(k)'s check of C on every session with a C log, **the C-log list**, E111's login scrub, the data directory,
   `score_e173.py`), then **the C-log gate** (every session the registration lists carries a C log and a finished check: `cclist_q142kg.py`, then
   v3.1's `ccdone_q142s.py`) and **the desk-path gate** (v3.1's `nopath_q142s.py`). Then the public-text scan, then the data commit.

## Device commands sent

As [`E173.md`](E173.md) § Device commands sent: `ettelem sample` and `config` reads (the PMIC voltage reads among them, which the owner allows),
`ettelem sptrace`'s trace copy, the residency read this build refuses before it opens the device, the drain only if a sampler fails twice; no
statistics reset, no firmware-revisions query, no governor, TDP, threshold or clock set, nothing that writes.

## Files

| file | runs where | what |
|---|---|---|
| [`E173.md`](E173.md), `e173_common.py`, `make_predictions_e173.py` → `frozen-sha256-e173.json`, `predictions-e173.json`, `.txt` | desk (and the box imports `e173_common`) | the registration (`c8064454`) |
| `p8gov.py`, `score_e173.py`, `selftest_score_e173.py` → `selftest-score.txt` | desk | the scorer and its self-test (`99e5777e`) |
| `run_e173.py`, `queue_e173.py`, `check_e173.py`, `preflight_e173.sh` | box | the runner (E165's chain, the watcher installed), the queue (E165's), the harness check, the audit |
| `make_protocol_e173.py` → `protocol.json`, `protocol-subset.json`, `protocol-dry.json`, `protocol-stoptest-{board,die}[-dry].json`, `protocol.txt` | desk | the protocols, each with its order entries |
| `make_harness_e173.py` → `harness-e173.json` | desk | the hashes the box and the collector check |
| `collect_e173_bounded.sh`, `box/step_e173.sh` | desk | the collector and the box steps |
| `selftest_kit_e173.py`, `drypass_intel_e173.sh`, `logs/` | desk | the kit's self-test, the dry pass, the audits |

**One departure from the registration's Files table.** [`E173.md`](E173.md) names a `check_path_e173.py` for the kit. None was written: the code
path is checked by [`check_e173.py`](check_e173.py) against [`harness-e173.json`](harness-e173.json), which pins every file the box and the collector
run, the predictor, the watcher, v3.1's two gates and pool 8 among them (135 files), and the box's three binaries. The box runs it (step 2), and so
does the collector, first, at the desk (`--desk`, exit 6 when it fails). No rule, line, set, stop or order changes.

The Intel's batch rule: every generator, self-test, audit and dry pass here ran as a short job through the round's local slot at nice 10 (the
longest, the dry pass, 165 s of a mostly sleeping queue); a few inline reads of committed JSON files, each under a second, ran outside it. No lab box
and no other machine were used.

## What this cannot say

The kit is ported and dry-run, not run: nothing here has opened aifoundry2's card. The box steps read what the desk cannot: the binaries, the
host's boot, the holders.

SPDX-License-Identifier: Apache-2.0
