# Heat placement: development, calibration and the frozen validation (E52, Q60)

The owner's request of 27 September 2026 (11:09 PDT, [02-requests.md](../../../findings/02-requests.md), Q60) asked two
things of the chip's heat and its clock governor: **Q1**, does the governor act when the *average* die temperature
passes its limit or when *one* sensor does; **Q2**, can the same heat-intensive work run longer before the throttle in
some parts of the chip than in others. Theories and predictions first, every iteration on one card, then a test on
another card with no iteration after it, and a summary of which theories survived.

This directory holds everything: the design and its critique, the development rounds on aifoundry3, card 1's
calibration and validation on aifoundry1, aifoundry2's same-day attempts, the reductions, the verdicts (`val.json`)
and the page's data. The tools are
[`tools/claims-v3/hp/`](../../../../tools/claims-v3/hp) (its `README.md` has the rules, the pass numbering and the 40
departures from the design); the frozen predictions are its [`prereg/PREREG.md`](../../../../tools/claims-v3/hp/prereg/PREREG.md).
The page is `docs/reports/2026-09-28-et-soc1-heat-placement.html` ("Where the work sits"), built from `heat.json` here.

**Status (28 September, 08:00 PDT): done.** Development (R1–R3, aifoundry3) and card 1's calibration (V0); the
predictions frozen at 22:50 PDT on 27 September (PREREG.md SHA-256
`a1bdc4e42c88c875f53afe112141df95bfac13370243650cf99b6b93c53ff890`); the validation on aifoundry1's card 1 in three
sessions, 27 Sep 23:45 – 28 Sep 07:49:40 (its queue log's "queue ends"); its blocks collected here and reduced once,
under the lock, into `val.json`. **Verdicts:** PLACE-tS (Tier S) **PASS**, L = 0.715 [0.546, 0.883], the perimeter
2.04 times as long as the interior in 5 of 5 blocks; PLACE-t (Tier L, primary) **INSUFFICIENT**, L = 0.198 [−0.423,
0.819], with 7 of its 10 runs (10 of all 15 Tier L runs) cut off by the 150 s cap before the mean read 66 °C; H11
(transfer) INSUFFICIENT; by DESIGN2's frozen table no theory survived on card 1 and none was refuted (H3 and H4 have
no entry: PLACE-t was registered SIGN+, the prediction of H2). The page opens with the summary.

The development and calibration data chose the parameters and the predictions and test nothing; only the validation
blocks (`p9*` under `raw/aifoundry1-c1/hp/`) test. Only signs transfer between cards, never magnitudes.

## Files

| Path | What |
|---|---|
| `raw/aifoundry3/hp/p<pass>/` | every development block (R0 801/901, R1a 1701, R1b 1601–1603, R1c 1101–1103 and 1201–1203, R2 2301 and 2204–2206, R3 3101–3103 and 3201–3203): `block.json`, `plan.json` (the block's own parameters), `runs.jsonl` (each run's record), `launches.jsonl`, `marks.jsonl`, `tel-<run>.jsonl.gz` (10 Hz telemetry), `heater-<run>[-pre].out.gz`, `blockcheck.json`, `code.sha256`, `binaries.json`, `manifest.txt` (`et-lab-manifest`), `mgmt.log.gz`; the probe (801) also `probe.json`, `p0.bin`/`p1.bin` (the service processor's trace ring before and after) |
| `raw/aifoundry1-c1/hp/p<pass>/` | card 1's R0 probe and smoke (801, 901), its calibration V0 (5501, 5502; 5503 ended at once, "skipped", because the edge had settled), and the validation blocks 9101–9105 (Tier S) and 9201–9205 (Tier L), each with `prereg-lock.json` and `guard.jsonl.gz` (the card-0 guard's samples); `p9101.guard-stop-27sep` is session 1's stopped first attempt at 9101 (status fail: departure 39), kept and never reduced; `session-widle.json` the idle-power guard's baseline |
| `val.json` | the verdicts: `reduce.py --val` on `raw/aifoundry1-c1` under the lock (reproduced byte for byte; SHA-256 `a026c507…`) |
| `raw/aifoundry2/hp/a2/p1`, `p2` | aifoundry2's two same-day attempts (A2, its own frozen PREREG-A2, `tools/claims-v3/hp/a2/`) |
| `reductions/` | `dev-r1c.json`, `dev-r2.json`, `dev-r3.json` (`reduce.py --dev` after each round; dev-r3 is the development record), `p1-r1b.json`, `p1-after-edit.json`, `p1-r1c.json` (the P1 decisions; the middle one is the bug of departure 35, kept as evidence), `dl8_check.py` (D-L8 on block 2301), `v0.json` (card 1's settled edge, `hplib.py v0final`), `bin-c1.json` (card 1's binaries, `block.sh --binhash`), `reg.json` (P3, the registration), `prereg-val.out` (what `prereg.py --val` printed at the freeze) |
| `logs/` | the queue logs of every development, calibration and validation queue (`queue-hp-aifoundry1-c1-val1.log`, `-val1b.log`, `-val2.log`), the session-2 waiter's log (`hp-val2-waiter.log`; its `who` field, other people's logins, removed by `collect_val.sh`), and aifoundry2's two attempt logs |
| `plan/` | `DESIGN.md` (12:00), `CRITIQUE.md` (12:22) and `DESIGN2.md` (13:22 PDT, 27 Sep: the design the tools implement), `plan-after-r2.txt` (the plan from R2 to the verdicts, 20:25), and `notes/` (the research notes and scripts DESIGN2 cites: `firmware.md`, `observability.md`, `feasibility.md`, `derive_feasibility.*`, `design2_sets.*`, `idle_curves.*`) |
| `build_heat_data.py` | writes `heat.json`, the page's data, from the files above, `tools/claims-v3/hp/` (PREREG, placements, README, the reducer's own observables) and the DVFS page's `dv2.json` and `reductions/dv2-dev.json` (with G1-T's count rule from `tools/claims-v3/dv2/reduce_dv2.py`); reads `val.json` when it exists; `--check` exits 1 if `heat.json` is stale |
| `heat.json` | the page's data (generated) |
| `collect_val.sh` | adds card 1's validation blocks to `raw/aifoundry1-c1/hp/` (the verdict step) |

Left out of the raw copies on purpose: `who.txt`, `et-who.txt` and `ps.txt` (logins and other users' processes, which
never go into this public repository). `mgmt.log` is gzipped (`gzip -n -9`); the reducer reads the `.gz` files. The
design's citations `W/…` name the heat worktree (`et-soc1-heat`, branch `heat-placement` at `0cfc742`), whose files are
the same as this repository's at that commit; `TPM:N` is line N of et-platform's
`cafe03fc3^:…/services/thermal_pwr_mgmt.c` (the 1.3.1 cards' closest source), and `FW18` is `da192816a` (BL2 0.18.0).
`dl8_check.py` names the tools by a path relative to this repository (it had the worktree's absolute path).

## What ran, where and when (27–28 September 2026, PDT)

| Time | Card | Passes | What |
|---|---|---|---|
| 11:09 | — | — | the owner's request; research notes, `DESIGN.md`, `CRITIQUE.md`, then the owner's decisions O1–O3 (chains up to 150 s; the service processor's log level may be set to WARNING on a card whose probe is ALIVE; aifoundry2 tried today) and `DESIGN2.md` (13:22); no card touched |
| afternoon | — | — | the tools (`tools/claims-v3/hp/`), their dry-run simulator and synthetic self-test (`selftest/`), and PREREG-A2 frozen before aifoundry2's attempt (`a2/PREREG-A2.md`, SHA-256 `a1eb1832…`) |
| 16:50–16:51 | aifoundry2 | A2 attempt 1 | rest 67 °C: WARM (the governor sits in its thermal loop at 600 MHz), probe SILENT; TRIG-A, TRIG-B and H12 NOT OBSERVABLE (the pre-registered branch); one documentation launch |
| 16:52–16:53 | aifoundry3 | R0 801, 901; R1a 1701 | probe SILENT (predicted: its zero TDP latches the governor), smoke ok; the one-shot trace test is not applicable (it runs only on a STUCK probe) |
| 16:58–17:31 | aifoundry3 | R1b 1601–1603 | scouting: UNI32@16 chains from 60 °C took a median 104.9 s, over the 40–100 s aim (D-L16: raise S_L to 61); three half-power runs (CEN8, W8b) from 63 °C never reached 66 °C (D-L8: raise S_L8 to 64); Tier S from 64 °C crossed in about 1 s |
| 17:41–17:50 | — | P1 | `p1-r1b.json`; the re-run after the params edit (`p1-after-edit.json`) moved the edges from the edited file, not the ones the blocks recorded: the reducer was fixed before P1 ran again (departure 35) |
| 18:02–19:02 | aifoundry3 | R1c 1201, 1101, 1202, 1102, 1203, 1103 | three Tier L blocks (INT16@32, PER16@32, UNI32@16, chains from 61 °C) and three Tier S blocks (one 7 s launch from 64 °C; also B4NE, B4SW for MAP), interleaved |
| 18:52 | aifoundry2 | A2 attempt 2 | re-check: rest 66 °C, WARM again; no third attempt ran |
| 20:12 | — | P1 | `p1-r1c.json`, `dev-r1c.json`: D-S keeps Tier S (no censored INT16/PER16 run); S_L 61, S_L8 64 |
| 20:18–20:36 | aifoundry3 | R2 2301 | the L8 block from 64 °C: five of six half-power placements never reached 66 °C in 150 s; UNI32@16 (512 minions) did, in 21.3 s. `dl8_check.py`: DROP L8 and G8 (params-r2 `types` [S, L16]) |
| 20:24–20:25 | aifoundry1 card 1 | R0 801, 901 | probe SILENT (predicted: its clock never leaves 600 MHz), smoke ok |
| 20:37–21:08 | aifoundry3 | R2b 2204–2206 | three more Tier L blocks, the design's fallback after the drop (`dev-r2.json`) |
| 21:12–22:11 | aifoundry3 | R3 3201, 3101, 3202, 3102, 3203, 3103 | three Tier L and three Tier S blocks under the final parameters (`params-r3`) and code (`dev-r3.json`) |
| 22:13–22:49 | aifoundry1 card 1 | V0 5501, 5502, 5503 | calibration on ALL24 (768 minions) chains, never a tested workload: from 61 °C a median 11.7 s, under half of aifoundry3's 27.0 s (T_cal, its R3 calibration chains), so the edge dropped to 60 °C: median 17.2 s, inside 0.5–2 × T_cal, settled; 5503 ended at once |
| 22:50 | — | P3, PREREG | `reg.json` (P3 with card 1's V0 chains for its scatter), then `prereg.py --val`: PREREG.md, `prereg.json`, `params-val-aifoundry1-c1.json`, the lock |
| 23:45 → 28 Sep 07:49 | aifoundry1 card 1 | validation 9201, 9101–9105, 9202–9205 | see "The validation" below |
| 28 Sep 07:50–08:00 | — | verdicts | the blocks copied read-only and collected (`collect_val.sh`); `reduce.py --val` → `val.json`; the page rebuilt |

Development's result (`reductions/dev-r3.json`, item `PLACE-t`): over nine Tier L blocks the perimeter placement took
longer than the interior one to bring the mean from 61 to 66 °C in nine of nine blocks, L = ln(t66 perimeter / t66
interior) 0.479 [0.409, 0.550] (99%), 1.62 times as long; power, perimeter less interior, −0.21 [−0.38, −0.05] W at
about 14 W each (inside the ±0.5 W equivalence band); work equal to 0.002%. Tier S: 0.581 [0.454, 0.708] over six
blocks. The page gives the rest, each number from `heat.json`.

## The freeze

`prereg.py --val` wrote `tools/claims-v3/hp/prereg/PREREG.md` at 22:50:43 PDT on 27 September; its SHA-256 is
`a1bdc4e42c88c875f53afe112141df95bfac13370243650cf99b6b93c53ff890` (also in `PREREG.sha256`, and recorded outside the
tree when it was frozen). Its lock holds the SHA-256 of `prereg.json` (every item, prediction, band, beta, primary and
n_val), `params-val-aifoundry1-c1.json`, `block.sh`, `hplib.sh`, `hplib.py`, `probe.sh`, `reduce.py`,
`sptrace_events.py`, `placements.json`, `ettelem-hp/ettelem.cpp`, `run_queue.sh`, `tools/claims-v3/lib.sh` and
`queue.sh`, `tools/ettelem/ettelem.cpp` and `flip_thermal_model.py`, and card 1's four binaries (the heater, its
kernel, the sampler and `ettelem-hp`). Every validation block checked all of it before touching the card, and
`reduce.py --val` checks it again. **Edit none of these files** (they are the heat-placement lock; the DV2 lock,
`tools/claims-v3/dv2v/LOCK.sha256`, shares `lib.sh` and `queue.sh`).

Registered for card 1 (P3, mechanically from development): **PLACE-t** (Tier L, SIGN+, the perimeter lasts longer,
n_val 5 blocks, primary) and **PLACE-tS** (Tier S, SIGN+, n_val 5), each with POWER (±0.5 W) and WORK (±1%)
equivalence on its pair; Tier S POWER for pairs with INT16@32 waived (departure 37); H11, transfer, is FAIL if a
registered SIGN item fails. Reported, not tested: PLACE-kappa, PLACE-kappa-S (the κ gate, 0.90, passed too rarely:
departure 38), CONC (development did not support its fixed SIGN+), MAP (card 1 could not resolve it at 5 blocks), and
every L8 and G8 item (MEM, EDGE, PLACE8-t, LIN, GRAD-EW, GRAD-NS: dropped by D-L8). TRIG-A on card 1 is waived
(departure 19), TRIG-B was not registered (every probe SILENT), and aifoundry2's clock items were NOT OBSERVABLE.

## Departures

The tools' README lists 40 departures from `DESIGN2.md`, each with its reason. Most were fixed before any data or
while development ran (seeds, pass numbers, the trace-ring parser, the statistics' edge cases, the guards). Fixes
found in development came after development data: 29 (blockcheck reads each block's own round and parameters) and 35
(P1 and P3 read each block's own parameters). Four decisions came after development data: 36 (S_L8 only while L8 or
G8 is kept), 37 (Tier S POWER waived for INT16@32 pairs) and 38 (the κ gate stays 0.90), all before any validation
data; and 39 (every validation session starts with a Tier S block), after the first validation session's safety stop,
with no locked file changed. One was recorded after the validation, from its review: 40 (the block-void rule reads
τ_c over the measured runs only), the reading the locked `reduce.py` applied from the freeze, and the one that
reproduces the development record.

## The validation (aifoundry1 card 1)

Schedules `tools/claims-v3/schedule-hp-aifoundry1-c1-val1.txt`, `-val1b.txt`, `-val2.txt`; every block started with
`HP_PREREG_SHA256=a1bdc4e4…` through `run_queue.sh`. Session 1 (27 Sep 23:45) ran 9201 (Tier L, ok); 9101 (Tier S)
then stopped at its first measured run on the card-1 idle-power guard (a 2.30 W rise over the session's first run, which
had started 4 °C lower: departure 39); the aborted directory is kept as `p9101.guard-stop-27sep` and never reduced.
Session 1b (00:27–01:52, 28 Sep) re-ran 9101, 13.8 min after the stop (under the 15 min between queue entries the
design asks; departure 39), then 9202, 9102, 9203. Session 2 (05:52–07:49, at least 4 h later) ran
9103, 9204, 9104, 9205, 9105. The reducer uses each type's first five usable blocks in pass order; no spare blocks were
queued. None was void or incomplete, so all ten were used, and no measured run was void. The three Tier S blocks of
session 2 (9103, 9104, 9105) missed the edge on their first calibration run (void); 9103 ran a second one, 9104 and
9105 did not, which leaves those two without a κ network (κ is reported only, never tested).

What the verdicts rest on (`heat.json`, `val_blocks.summary`; the page's section 8 has the block table):

- **Tier S** (one 7 s launch from 64 °C): every run crossed; the perimeter took 2.18–3.03 s and the interior
  1.14–1.41 s, longer in 5 of 5 blocks. PLACE-tS PASS; WORK PASS; POWER waived (departure 37: on aifoundry3 the
  interior crossed in under a second, so its power window was empty; on card 1 it was not, and the waived value,
  −0.27 [−0.42, −0.13] W, is reported).
- **Tier L** (chains of 2 s launches from 60 °C, capped at 150 s): 10 of the 15 measured runs, 7 of PLACE-t's 10,
  never read 66 °C within the cap (INT16@32 3 of 5, PER16@32 4 of 5, UNI32@16 3 of 5; by session 2 of 3, 2 of 6, 6 of 6). A cut-off run counts
  as 150 s (DESIGN2 §2.2), so blocks 9202, 9204 and 9205, with both runs cut off, give L = 0; 9201 (perimeter over
  150 s, interior 110.2 s) and 9203 (142.6 against 72.1 s) went the predicted way. PLACE-t INSUFFICIENT, POWER
  INSUFFICIENT (−0.20 [−0.71, 0.32] W), WORK PASS.
- **Card 1's calibration chains** (768 minions, in the Tier L blocks) took 17.6–27.3 s (median 22.8 s) against
  17.2–20.5 s at V0 from the same 60 °C edge: they took longer during the validation than when its edge was set, and
  in session 2 every Tier L run was cut off (reported; not tested as the cause of the cut-offs).

## How to reproduce (from the repository root; no card)

```bash
V=docs/reports/data/2026-09-28-heat-placement
python3 tools/claims-v3/hp/reduce.py --data $V/raw/aifoundry3 --card aifoundry3 --dev --out /tmp/dev.json      # = $V/reductions/dev-r3.json, byte for byte
python3 tools/claims-v3/hp/reduce.py --data $V/raw/aifoundry3 --card aifoundry3 --p3 \
    --cal-card1 $V/raw/aifoundry1-c1 --out /tmp/reg.json                                                    # = $V/reductions/reg.json, byte for byte
python3 $V/reductions/dl8_check.py $V/raw/aifoundry3 2301                                                  # D-L8: DROP
sha256sum tools/claims-v3/hp/prereg/PREREG.md                                                              # a1bdc4e4…
python3 tools/claims-v3/hp/reduce.py --data $V/raw/aifoundry1-c1 --card aifoundry1-c1 --val \
    --prereg tools/claims-v3/hp/prereg/prereg.json --out /tmp/val.json                                    # = $V/val.json, byte for byte
python3 $V/build_heat_data.py                                                                              # heat.json (--check: is it current?)
python3 scripts/build-report.py heat-placement $V/heat.json docs/reports/2026-09-28-et-soc1-heat-placement.html
```

`python3 tools/claims-v3/hp/selftest/run_selftest.py` runs the synthetic chain (development → P1 → V0 → P3 → PREREG →
validation → verdicts) with no card (65 checks, about a minute; give it a scratch directory as its argument); `V3_DRY=1` runs any block against the simulator (the tools' README).

## The verdict step (done 28 September, 07:50–08:00 PDT)

Only after card 1's queue log on aifoundry1 (`~/nekko/build/claims-v3/queue-hp-aifoundry1-c1-val2.log`) says
`queue ends`; nothing below touches a card.

1. Copy the data read-only: `rsync -a aifoundry1:nekko/build/claims-v3/aifoundry1-c1/hp/ SRC/` and the validation
   queue logs (`queue-hp-aifoundry1-c1-val1.log`, `-val1b.log`, `-val2.log`, and `hp-val2-waiter.log` if present) into
   `LOGS/`.
2. `bash $V/collect_val.sh SRC LOGS`: adds the `p9…` directories and the logs here, without `who.txt`, `et-who.txt`
   or `ps.txt`.
3. `sha256sum tools/claims-v3/hp/prereg/PREREG.md` must print `a1bdc4e4…`, then
   `python3 tools/claims-v3/hp/reduce.py --data $V/raw/aifoundry1-c1 --card aifoundry1-c1 --val --prereg tools/claims-v3/hp/prereg/prereg.json --out $V/val.json`.
   It checks the lock and every block's `prereg-lock.json`, binaries and code hash, and refuses on any difference;
   never pass `--amendment`. Its words are final: PASS, FAIL or INSUFFICIENT per registered item, and H11.
4. `python3 $V/build_heat_data.py` (it reads `val.json` and card 1's validation blocks through the reducer's own
   functions), rebuild the page, `check_page.sh` it (light and `DARK=1`, 1280 and 390 px). The page's verdict
   section, KPI, status line, charts and "Which theories survived" fill in from the data with no source edit.
5. Record the verdicts in `docs/findings/03-experiments.md` (E52's "Validation"), `05-claims.md` (the heat-placement
   rows: validated values labelled with the card), and this README's status.

It ran as written: the lab copy was taken with `rsync -a` after "queue ends" (07:49:40) and checked equal to the lab's
files (`rsync -c --dry-run`); `reduce.py --val` ran once from this repository and once from the heat worktree
(`et-soc1-heat`, whose `tools/claims-v3/hp/` is identical), and both outputs were the same byte for byte. No analysis
choice changed and `--amendment` was never passed. `HP_PREREG_SHA256` (the hash recorded outside the tree at the
freeze) is read by the validation blocks (`block.sh`, through `hplib.py vallock`) and by `run_queue.sh`, not by
`reduce.py --val`: its anchors are `PREREG.md` against `PREREG.sha256`, the locked files, and each block's
`prereg-lock.json` (the PREREG hash the block ran under, checked when it ran against the recorded value). A reduction
with the variable set to anything gives the same `val.json`.
