# E175's run kit: aifoundry2's governed line under its own governor, in E173's form with the v3 drivers, checked at the desk, ready for the box steps (Q143(g))

*Thu 5 Nov 2026 (week 45), PST, on the Intel, desk only: no card claimed, no device command sent, no lab box reached, nothing measured. It answers
the earlier critics' rank "aifoundry2's governed line" on the kinds page's
[section 11, item 6](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open). The rules are registered in
[`E175.md`](E175.md) (lab **`c50ff493`**, 12:16:51 PST); the tiles, their selection and their frozen predictions in **`b3f5e83c`** (13:04:23 PST;
[`docs/reports/data/2026-11-05-q143g-e175-design/`](../../../docs/reports/data/2026-11-05-q143g-e175-design/README.md)); this kit in the commit that
adds this README. Nothing of the pool-8 card day (E171-E174), which ran meanwhile, was read.*

## What it does to predicting power and heat

Nothing yet: it makes E175 runnable and scorable as registered. E175 then gives M10 carried (rule E, through M9's aifoundry2 part) its first blind
score under the governor on enough governed tiles: 16 new kinds predicted at 727.9-793.8 MHz, four to a stratum, against rank 2's governed lines
(E175-A2-G, Bg) and Q140(l)'s held-out figures (F1, W1); 8 new pinned kinds beside (Bp, F2, W2), so rank 2 (E175-A2-R2) can read PASS on blind kinds
for the first time; M10 against M9's part on the board (M1); the burst heat law on a fourth pool (H1). Before: the governed clock's only blind score
is M9's part on pool 7 (E165: 3.03 MHz rms, 12 tiles); pool 8 left G, Bg, F1 and W1 NOT SCORED.

## Ready, and what waits

| step | state |
|---|---|
| the registration, the design's rule, the power at the planned n | **committed** (`c50ff493`): [`E175.md`](E175.md), [`make_e175_pool.py`](make_e175_pool.py), [`bench_e175.py`](bench_e175.py), [`design_power_e175.py`](design_power_e175.py) → [`design-power-e175.txt`](design-power-e175.txt), [`SHA256SUMS-e175-registration`](SHA256SUMS-e175-registration) (40) |
| dated note A1 (the stream continued for the pinned set only) | **committed** (`0e56a875`, 12:54:59 PST, before any candidate past 63 existed): [`E175.md.dated-note-A1.md`](E175.md.dated-note-A1.md), [`make_e175_pool_a1.py`](make_e175_pool_a1.py), [`SHA256SUMS-e175-a1`](SHA256SUMS-e175-a1): the registered 64 candidates gave 16 governed and 7 pinned; candidate 65 completed the pinned set |
| the tiles, the counts, the selection, the pool and its frozen predictions | **committed** (`b3f5e83c`): [`pool/`](pool/) (27 tiles), [`frozen/predictions-pool8-aifoundry2.json`](frozen/predictions-pool8-aifoundry2.json) (the frozen predictor's own output), the design directory's `SHA256SUMS` |
| the kit | **this commit**: [`make_predictions_e175.py`](make_predictions_e175.py) → [`predictions-e175.json`](predictions-e175.json), [`frozen-sha256-e175.json`](frozen-sha256-e175.json) (33 files, 25 of them matched against the committed list that names them, the others committed clean with their last commit), [`predictions-e175.txt`](predictions-e175.txt); [`make_protocol_e175.py`](make_protocol_e175.py) → `protocol*.json` ([`protocol.txt`](protocol.txt)); [`run_e175.py`](run_e175.py) (the watcher fix installed); [`queue_e175.py`](queue_e175.py); [`make_harness_e175.py`](make_harness_e175.py) → [`harness-e175.json`](harness-e175.json) (103 files, the 27 pool tiles among them, and the box's 3 binaries) and [`check_e175.py`](check_e175.py); [`preflight_e175.sh`](preflight_e175.sh); [`collect_e175_bounded.sh`](collect_e175_bounded.sh); [`box/step_e175_v3.sh`](box/step_e175_v3.sh) |
| the scorer and its self-test | **this commit**: [`score_e175.py`](score_e175.py) (E173's `p8gov.py` imported unchanged), [`selftest_score_e175.py`](selftest_score_e175.py) → [`selftest-score.txt`](selftest-score.txt): 37 of 37: E165's committed session reproduced where the rules overlap (the anchors, M9's part on 52 tiles field for field, G's, Bg's and Bp's lines and R2's form, F1-F2, W1-W2 and H1's rms, E165's own lines and paired interval); made-up sessions with known verdicts (R2 PASS; a governed clock level and a pinned board level FAIL; M1 BETTER and WORSE; GS reads a designed slope; 7 governed tiles NOT SCORED); every registered refusal |
| device commands | **GO**: 19 send sites, all READ, 0 disallowed, with E165's and E173's one reviewed exception (`run_hpl.py:622`, the residency query this ettelem refuses at its argument check before it opens the device) ([`logs/dmcmd-audit.txt`](logs/dmcmd-audit.txt)); NO-GO on that line only without the reviewed exception ([`logs/dmcmd-audit-noexcept.txt`](logs/dmcmd-audit-noexcept.txt)); the desk files GO, no send site ([`logs/dmcmd-audit-desk.txt`](logs/dmcmd-audit-desk.txt)) |
| the kit's self-test | [`logs/selftest-kit.txt`](logs/selftest-kit.txt): ALL PASS (the protocols against the order, the five passes of 29, the admission and the 16 / 8 sets, the runner's refusals, the stop tests and smoke, the watcher installed, the harness, `bash -n`) |
| the dry pass on the Intel, with a stand-in ssh and rsync | [`logs/drypass-intel.txt`](logs/drypass-intel.txt): the whole queue on `run_hpl.py`'s toy card (no device, no lock), with a logging stand-in ssh and rsync first on PATH: the smoke rc 0, stoptest-board exit 4 for "board" 14 ms after the third live line over 30 W, stoptest-die exit 4 for "die" before any launch, s1 22 runs rc 0, the watcher's record in `e175.json`; then `score_e175.py` on the dry s1: every governed and pinned rule NOT SCORED at the dry twin's 3 + 3 tiles, as registered; **0 stand-in calls** |
| the box steps | [`box/step_e175_v3.sh`](box/step_e175_v3.sh) over the q142kg runbook's `rb_common_v3.sh`: its desk test with a stand-in ssh and rsync, [`selftest_steps_e175.sh`](selftest_steps_e175.sh) → [`logs/selftest-steps.txt`](logs/selftest-steps.txt) (34 of 34), and its dry listing ([`logs/dry-listing.txt`](logs/dry-listing.txt), 8 of 8 steps, no call) |
| everything on the box | waits for E173 to end (plus 10 minutes), a readiness critic, the day's post and the window |

## Card-minutes and the cap

**About 38 card-minutes; the cap is 42, the slot 48 minutes.** 145 bursts in 5 passes of 29: per pass 17 governed bursts (the 16 kept and
E80's fp16 randn) at E165's measured 16.2 s and 12 pinned (the three zeros anchors, the 8 kept and E80's int8 full) at 13.5 s is 7.3 min, so 36.5
min for the five, plus the smoke and the two stop tests (E165: 0.97 min). `run_e119.py` starts a run only if its planned time fits the cap, so a slow
day cuts pass 5's tail, never a run in flight. **The registered subset** (`protocol-subset.json`: passes 1-3, 87 bursts, about 22 min): `launch
subset`, cap 25, a 31-minute slot. On aifoundry2, E175 runs after E173 (at least 10 minutes after its queue ends) and before or without E177, never
beside either.

## The box steps, in order

Each runs on the Intel from the top of the lab clone through the q142kg runbook (a 15 s probe; every call bounded; a login link kills the call and
appends `<HH:MM:SS> aifoundry2 needs a check` to `$RB_LOCK`). First `export RB_OUT=<a new directory for this session, outside the repo> RB_LOCK=<the
round's lock file>` and, once, `bash tools/claims-v3/q142kg-runbook/s02_window_q142kg.sh <day> <last start> <last end>` with the go's window (E175.md:
if the go names none, `2026-11-05 21:00 22:00`).

1. `bash tools/claims-v3/e175/box/step_e175_v3.sh look`: et-who, who, uptime, the identity by host-boot continuity (before E69's firmware read of
   2026-10-27 13:56:26 PDT), the holder rule (an idle login does not block; E173's queue, if still running, holds the card: ours_live counts it). 0
   free; 16 the identity stop; 17 held.
2. `... tree`: `git pull --ff-only`; `git merge-base --is-ancestor $RB_BASE HEAD` (default `c50ff493`, the registration; the kit's own bytes are
   checked by the harness); `tools/claims-v3` clean; then `check_e175.py` **HARNESS OK 103 + 3 binaries**, `e175_common.py` **27 tiles** OK, the
   pool's SHA256SUMS **28** OK, `preflight_e175.sh` **GO**, `run_e175.py --list` **145** runs.
3. `... dry start`, then `... dry wait` (repeated until 0): the box's dry pass (the toy card, a few minutes), a detached job; it refuses while a
   session of ours runs (E173's queue counts).
4. The day's one post (the card lane, under the post's lock): aifoundry2's clause, before the first launch.
5. `... launch` (or `... launch subset`): inside the window (no start after the last start; the slot must end by the last end), with v3.1's guard
   on the box (no dry pass running, no session of ours, the identity), today's dry pass ended rc 0, and **E175.md's gate**: no `queue_e173.py`
   running, and E173's `build/e173/runs/status.json`, if written today, reads ended or halted and is at least 600 s old. It writes the slot file and
   detaches `queue_e175.py --cap 42` (the subset: `--cap 25 --protocol protocol-subset.json`). The queue runs the smoke, the DMA rule and both
   stop-path tests itself, and halts with QUEUE-HALT and no session if any fails.
6. `... wait`, repeated: one bounded wait; 0 ended, 16 a gate stopped it, 17 still running. Then the day's post drops the clause (or appends
   " — released" if it is the last one held).
7. `... collect`, at the desk: [`collect_e175_bounded.sh`](collect_e175_bounded.sh) (the harness check, its own probe, every remote call under
   600 s, the box's file hashes, Q139(k)'s check of C on every session with a C log, the C-log list, E111's login scrub, the data directory
   `docs/reports/data/<day>-e175-governed-aifoundry2/`, `score_e175.py`), then **the C-log gate with v3's list** (`cclist_q142kg_v3.py`, then v3.1's
   `ccdone_q142s.py`) and **the desk-path gate** (`nopath_q142s.py`). Then the public-text scan, then the data commit.

## The stops and the governor

As [`E175.md`](E175.md): one die reading at or above 76 °C, or the board above 85 W on three live samples in a row, ends the session (exit 4); a
burst runs only if its frozen estimate is at most 82 W (every kept tile's larger 95% upper peak is at most 81.53 W); after a run whose highest
board sample reached 82 W, nothing at or above that run's estimate runs (E159's lock, the same tile included: with 16 governed tiles predicted at
upper peaks up to 81.53 W, a session may lose tiles to it, and every rule then reads at its scored n). No governor, TDP, threshold or clock set; the
`ettelem config` reads at the start and end expect 65 W / 65 °C.

## Device commands sent

As [`E175.md`](E175.md) § Device commands sent (E173's table): `ettelem sample` and `config` reads (the PMIC voltage reads among them, which the owner
allows), `ettelem sptrace`'s trace copy, the residency read this build refuses before it opens the device, the drain only if a sampler fails twice;
no statistics reset, no firmware-revisions query, no governor, TDP, threshold or clock set, nothing that writes.

## Files

| file | runs where | what |
|---|---|---|
| [`E175.md`](E175.md), `make_e175_pool.py`, `bench_e175.py`, `design_power_e175.py` → `design-power-e175.{txt,json}`, `SHA256SUMS-e175-registration` | desk (the bench driver on the mini) | the registration (`c50ff493`) |
| `pool/`, `frozen/` | desk and box | the tiles and their frozen predictions (`b3f5e83c`) |
| `e175_common.py`, `make_predictions_e175.py` → `frozen-sha256-e175.json`, `predictions-e175.json`, `.txt` | desk (the box imports `e175_common`) | the sets, order, lines, references, admission and rules |
| `score_e175.py`, `selftest_score_e175.py` → `selftest-score.txt` | desk | the scorer (E173's `p8gov.py` imported) and its self-test |
| `run_e175.py`, `queue_e175.py`, `check_e175.py`, `preflight_e175.sh` | box | the runner (E165's chain, the watcher installed), the queue, the harness check, the audit |
| `make_protocol_e175.py` → `protocol.json`, `protocol-subset.json`, `protocol-dry.json`, `protocol-stoptest-{board,die}[-dry].json`, `protocol.txt` | desk | the protocols, each with its order entries |
| `make_harness_e175.py` → `harness-e175.json` | desk | the hashes the box and the collector check |
| `collect_e175_bounded.sh`, `box/step_e175_v3.sh`, `selftest_steps_e175.sh` | desk | the collector, the box steps, their desk test |
| `selftest_kit_e175.py`, `drypass_intel_e175.sh`, `logs/` | desk | the kit's self-test, the dry pass, the audits, the dry listing |
| [`SHA256SUMS-e175-kit`](SHA256SUMS-e175-kit) | desk | the sha256 of every file of this commit |

The Intel's batch rule: every generator, self-test, audit and dry pass here ran as a short job through the round's local slot at nice 10; a few
inline reads of committed JSON files, each under a second, ran outside it. The bench counts ran on the mini. No lab box was used.

## What this cannot say

The kit is ported and dry-run, not run: nothing here has opened aifoundry2's card. The box steps read what the desk cannot: the binaries, the
host's boot, the holders, E173's end.

SPDX-License-Identifier: Apache-2.0
