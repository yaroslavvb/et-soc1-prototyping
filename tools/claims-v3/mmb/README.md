# V3-MMB: tensor matmul benchmark, private-tile L2 test, the E5 load step

PLAN3 section 2, V3-MMB (`docs/reports/data/2026-09-25-claims-v3/PLAN3.md`; 50 claims; items MMB-a to MMB-f, MMB-X1,
MMB-T). One pass on the local card:

    bash tools/claims-v3/mmb/block.sh <pass>            # passes 1-4 on each card, >= 10 min apart (queue line: "mmb <pass>")
    bash tools/claims-v3/mmb/block.sh 1 --smoke         # before the queue, once per card: about 45 s of card time
    V3_DRY=1 bash tools/claims-v3/mmb/block.sh <pass>   # no card: prints every device command, sleeps skipped
    V3_DEVICE=0 bash tools/claims-v3/mmb/block.sh <pass> # on aifoundry1: card 0 (or 1); lib.sh sets ET_DEVICES

Raw data go to `build/claims-v3/<card>/mmb/p<pass>/` (smoke: `mmb-smoke/p<pass>/`); `<card>` is aifoundry2,
aifoundry3, aifoundry1-c0 or aifoundry1-c1. The four cards run the same passes; what differs per card is in "Four cards"
below.

## What a pass does, in order

1. **Smoke checks** (every pass; about 15 s): the four launches of `make mmbench-check DEVICE=silicon`
   (`-m fp32`, `-m fp16`, `-m int8`, `-m fp32 -n 64 -i 2 -p`, all 32 shires) and `it_test_code_loading --mode=pcie`,
   each under `timeout 10`. Written to `smoke/`. They are MMB-b's smoke-test clause (decided on aifoundry3).
2. **E1** (about 2 min): the four mmbench workloads, one invocation each, in the pass's registered order
   (p1 fp32, fp16, int8, DRAM; p2 DRAM, int8, fp16, fp32; p3 int8, fp32, DRAM, fp16; p4 fp16, DRAM, fp32, int8; a pass
   number above 4 reuses these cyclically). Per workload: on a governor-free card (aifoundry2, aifoundry1-c0, -c1)
   `heat_to 76`; `start_sampler` (ettelem, 10 Hz,
   cap 90 s); `mmbench_power_v3.py run --only <workload> --seconds 6` (8 s idle, calibration launch, about 6 s of timed
   launches, 5 s gap; every launcher under `timeout 10`); `stop_sampler`; `mmbench_power_v3.py finish` (power.csv,
   results.json, drop flags); `scripts/mmbench-report-data.py` (the original report reducer, unchanged: `report.txt`).
   Written to `e1/<workload>/`.
3. **ridge-X1** (about 50 s): on a governor-free card `heat_to 76`; die temperature and clock before and after (`x1/clock.jsonl`,
   no sampler running then); per mode in the registered order (p1 fp32, fp16, int8; p2 int8, fp16, fp32; p3 fp16, int8,
   fp32; p4 fp32, int8, fp16): `mmbench_launcher -m <mode> -n 4 -p -i ITERS -r 3 -t 4` (private pools), 3 s, then
   `-n 16 -i ITERS/4 -r 3 -t 4` (shared control), 3 s; ITERS 280000 (fp32, fp16) or 250000 (int8). No sampler (cycle
   counters). Written to `x1/<private|shared>-<mode>.out` and `x1/rc.jsonl`.
4. **pt X1, the E5 load step** (about 3 min): a governor-free card `heat_to 76`, aifoundry3 (pinned) sleeps 60 s; then the phases of
   `tools/ettelem/run_thermal.sh` with the same loads and flags: sampler (cap 240 s), idle0 20 s, 8 mmbench processes
   (`-m fp32 -n 16 -i 100000 -r 5 -t 120`, all shires), cool1 40 s, 4 memprobe processes (`--loop --table dram_seq.tbl
   --level 4 --stride 64 --lines 1024 --seconds 6`), cool2 22 s, end, sampler stopped 1 s later. Written to `thermal/`
   (`thermal-telemetry.jsonl.gz`, `thermal-phases.jsonl`, `thermal-loads.log` as run_thermal.sh writes them, plus each
   process's full output).
5. The card's idle state, at the start of the block (before any heating) and after the load step: `ettelem config`
   (one read-only query: power_state, minion MHz and mV, TDP, threshold) plus a 1 s die and clock reading, into
   `idle-state.jsonl` (four cards: aifoundry1-c0 idles at 300 MHz in a low_power state).
6. `passcheck.py` (no card): completeness and the drop rules; `block.json` says `ok`, or `fail` with the reasons (the
   queue then sets the attempt aside and re-runs the pass next time). It also runs the registered load-step reducer
   (`x1_reduce.py`) on the pass: a load step it cannot reduce (for example a telemetry sample whose SP-stats query
   failed, which ettelem leaves out) is a re-run reason now rather than a lost pass at reduction time. So is a load step
   whose matmul stop edge is outside 75-92 s after the idle0 mark, or whose DRAM phase ends after 174 s: the registered
   reducer reads the edges in fixed windows (15-35 s and 73-95 s; E5 stopped at 78.0 s) and bins only to 175 s, so such
   a pass would be reduced wrongly without an error (a slower launcher start-up on aifoundry3 would shift the stop edge).
   It reports each E1 launcher process's wall time (a note above 9.3 s). Telemetry is gzipped; the launcher's 8 MB
   `traceKernels_dev0_0.bin` is deleted.

`--smoke` runs every component once at its smallest: the same smoke checks, one 1 s heater launch (governor-free cards), E1
fp32-tensor-L2 with `--idle 2 --seconds 1 --gap 1`, one private and one shared int8 launch at a tenth of ITERS, and a
mini load step (2 s phases, one matmul process `-i 20000 -r 1`, one memprobe process `--seconds 1`). No heating in the
smoke block, so a clock drop there is a note, not a failure.

## Card minutes per pass

| | aifoundry2 | aifoundry3 | aifoundry1-c0, aifoundry1-c1 |
|---|---|---|---|
| idle-state records (start, end) | 0.1 | 0.1 | 0.1 |
| smoke checks | 0.3 | 0.3 | 0.3 |
| E1 (4 workloads) | 2 + heating (first heat from ~72 C about 0.5-1.5 min, later ones seconds) | 2 | 2 + heating: first heat from their idle (c0 ~65 C, c1 ~57 C on 25 Sep) to 76 C, about 1-3 min (aifoundry3 took 55 to 88 C in 150 two-second launches); later ones seconds |
| ridge-X1 | 0.9 (+ heat check) | 0.9 | 0.9 (+ heat check) |
| load step | 3 + heat check | 3 (+ 1 min sleep before it) | 3 + heat check |
| **pass** | **about 7-9 min** | **about 7 min wall, 6 of them on the card** | **about 8-11 min** (not yet measured on these cards) |
| smoke block | about 0.8 | about 0.7 | about 0.8 |

Four passes per card: about 28-36 min on aifoundry2, 28 on aifoundry3, 32-44 on each aifoundry1 card.

The plan's estimate was 42 and 25 minutes for 4 passes (10.5 and 6 per pass). Keep passes on a card >= 10 min apart
(PLAN3 2.13); the block does not wait by itself.

## What is dropped, and why

- Any launch (E1 timed launches, ridge-X1 launches) whose `implied_ghz` is outside 0.595-0.605 (registered).
- aifoundry2: any E1 launch with a telemetry sample inside it (or, for a launch shorter than the sampling interval, on
  either side of it) off `mhz.minion` 600, and any load-step pass with any sample off 600 (registered; below ~68 C the
  governor lifts the clock).
- aifoundry1's cards (not registered; "Four cards"): busy samples only, the same two rules over the samples inside
  launches; never idle brackets (aifoundry1-c0 idles at 300 MHz); a sample below 600 MHz in a process's first second
  is a ramp from the idle state, recorded, not dropped.
- An E1 workload's power values in a pass (MMB-c to MMB-f) are dropped if any of its timed launches was dropped (the
  mean power covers all of them). On aifoundry1's cards, a launch 0 dropped only for implied_ghz below the band (the
  ramp, before the power window) does not drop them.
- On aifoundry1's cards a ridge-X1 process whose launch 0 alone is below the band (a ramp from the idle state after the
  3 s gap) is still dropped launch by launch, but passcheck only notes it instead of re-running the pass: the other
  launches carry MMB-X1, as on every card.
- A pass with a registered drop, a missing component, or a failed E1 runner ends `fail` and is re-run by the queue;
  the reducer ignores the set-aside attempt (`p<k>.attempt-*`) but uses whatever a failed pass that was never re-run
  kept after the drop rules.
- Calibration launches are not items' data (as in the committed run, whose `runs.jsonl` has timed launches only): a
  28 ms calibration launch reads `implied_ghz` about 0.591 from the 0.43 ms launch overhead alone. They are reported.

## Deviations from the plan's commands, with reasons

1. **E1 sampler.** The plan runs `scripts/mmbench-power.py`, which starts `scripts/et-power-log.sh` (a loop of
   `dev_mngt_service` queries stopped with `killpg(SIGTERM)`, which can kill a query mid-request and poison the
   management node) and queries `dev_mngt_service` before and after. The card rules allow samplers only through
   lib.sh's `start_sampler`/`stop_sampler` and nothing else on the management node while one runs. So E1 uses a patched
   copy, `mmbench_power_v3.py`, and the ettelem sampler: `board_w` is `DM_CMD_GET_MODULE_POWER / 100`, the same reading
   et-power-log.sh prints (ettelem.cpp), at 10 Hz instead of ~8 Hz. Everything the original computes is copied
   unchanged, and `finish` writes the same `power.csv`, `runs.jsonl` and `results.json` (plus die temperatures, the
   clock during the launches and drop flags). `info.freqs` and the temperatures come from the telemetry in the original
   text format, so `mmbench-report-data.py` runs unchanged. The copy is split into `run` (card) and `finish` (no card),
   chdirs to `--root` explicitly, runs the launcher in the pass's `run/` directory (it writes an 8 MB trace dump
   there), and prints instead of running under `V3_DRY=1`. On the committed 18 Sep session laid out as a pass,
   `finish` reproduces the page's numbers exactly (9.511 T, 56.57 W, idle before 30.61/32.53/33.83/35.16 W).
2. **E1 heating on aifoundry2.** The plan: "heat to 76 C before a workload whose die reads < 70 C, start at <= 74 C".
   The card rules: power and memory-bound work starts on a die >= 76 C. The block runs `heat_to 76` before every
   workload and starts at once, so aifoundry2's E1 runs start at >= 76 C instead of 70-74 C (the 18 Sep run: 71 C).
3. **E1 report reducer**: `scripts/mmbench-report-data.py` from the tree root. On aifoundry2, `~/nekko/scripts/` holds
   older copies (its mmbench-power.py has no `idle_before_w`).
4. **Smoke tests**: the four launches of `make mmbench-check DEVICE=silicon` are run directly, not through make: the
   target depends on `all` (a cmake build), and on aifoundry2 the tree root has no gp-sdk build (it is in `~/nekko`), so
   make would start building. They and `it_test_code_loading` run at the start of every pass on both cards (the plan:
   once on aifoundry3 on day 0); they cost about 15 s.
5. **ridge-X1**: the commands as planned (flags checked against `launchers/mmbench/mmbench.cpp`: `-k -d -s -m -n -i -p
   -r -t`). Each process's output goes to its own `x1/<kind>-<mode>.out` instead of appending to `private.jsonl` and
   `shared.jsonl`. A non-zero launcher exit (a failed tolerance check: private fp32/fp16 records exceed
   `max_exact_iters` and report `approx` by design) is recorded, not a re-run: the cycle counts stand.
6. **pt X1**: `run_thermal.sh` is not called. Its load step is re-implemented in the block with the same phases,
   sleeps, loads and flags, for three reasons. The sampler goes through `start_sampler` (it waits for the first line,
   retries and drains; it is stopped by SIGTERM 1 s after the end mark, cap 240 s) instead of a bare `ettelem sample
   --seconds 185`. Every process runs through `hold10`. And the binaries are in two trees on aifoundry2: mmbench in
   `~/nekko/build`, memprobe and the table in this repository's `build/`. `run_thermal.sh` takes a single `BUILD` for
   both, and `BUILD=$HOME/nekko/build` (the plan's aifoundry3 form) would not find memprobe on aifoundry2. memprobe is
   lib.sh's `$MEMPROBE`: on aifoundry2 the fresh `build/memprobe-v3` (E5 used the 19 Sep `build/memprobe`), on
   aifoundry3 `build/memprobe`. The table is `build/memprobe-data/dram_seq.tbl` at the tree root on both. The launcher
   runs in the pass's `run/` directory. All MMBENCH lines of each process are kept (`mm-<i>.out`); `thermal-loads.log`
   gets the last line of each process, as `run_thermal.sh` writes it.
7. **x1_reduce.py** is the plan's `validate3/inv/pt-spatial-work/x1_reduce.py` (sha256 d95b227b…418f) copied here with
   three changes: `REPO` is derived from the file's location (the original pinned the aifoundry2 path); telemetry is
   read from `thermal-telemetry.jsonl` or its `.gz`; and it outputs one more field, `rest_matmul_mean`, the steady matmul
   remainder that P7 needs. On the committed E5 directory its output equals `x1_selfcheck_e5.json` field for field.
8. **Dry runs**: the block overrides lib.sh's dry `hold10` locally so that the dry line goes to the block's own stderr
   (fd 9) even from calls whose output is redirected to a file. lib.sh itself is unchanged.
9. **E1 process-time guard** (review, 25 Sep; not in the original). With `--seconds 6` and `--launch_seconds 1.5` the
   repeat rule gives 6 x 1.13 s (fp32), 8 x 0.85 s (fp16), 5 x ~1.46 s (int8) and 5 x ~1.48 s (DRAM: `int()` on iters
   makes 6 / (iters x per_iter) land just above 4) of launches in one process, 6.8-7.4 s before the launcher's own
   start-up, and the DRAM workload's start-up builds 256 MB of private tiles on the host. The committed 18 Sep run was
   12 s per workload and says nothing about this margin. The runner now times every launcher process (`procs` in
   `meta.json`, `launcher_processes` in `results.json`) and, if the calibration process's fixed cost (its wall time
   minus its launch) plus the planned launches would exceed 9 s, runs fewer launches (`repeat_planned` is kept). It
   never changes iters, the calibration or the windows. On a fake launcher with 0.3 s start-up the DRAM workload keeps
   its 5 launches (7.7 s); with 2.5 s it runs 4 (8.4 s) instead of being killed at 10 s. The smoke checks record their
   start times (`t0_ms`), so the `-m fp32 -n 64 -i 2 -p` check, which builds the same pools, shows that start-up cost on
   each card before the queue runs.
10. **Missing telemetry blocks** (review): ettelem leaves out a block (`mhz`, `temp_c`, `sp`, ...) whose query failed.
   `finish` and `reduce.py` treat such a sample as no reading for that block instead of crashing (the clock drop rule
   uses the samples that have a clock reading). `x1_reduce.py` is kept as registered; passcheck catches its failures.

## Reduction

    python3 tools/claims-v3/mmb/reduce.py --data <dir with one directory per card> --out verdicts.json

`<dir>/<card>/` is laid out like `DATA_ROOT` (`mmb/p<k>/`, optionally `mmb-smoke/p<k>/`); every card directory present
is read, and the four campaign cards are always expected (a missing one counts as a card without repeats in
`all_cards`). Runs on partial data. It
needs, in the tree: `tools/ettelem/summarize_power_session.py` (imported read-only by x1_reduce.py) and
`docs/reports/data/2026-09-22-dvfs-aifoundry2/dvfs.json` (the idle law, for P3). No scipy: the t distribution is
computed in the file. It was checked against the plan's critical values (t_0.995 at df 2, 3, 4, 5 and 9; t_0.99 at df 2, 3 and 4).

Output: `{"exp", "data", "need_kept_repeats", "cards", "passes", "idle_clock", "items": [...]}`. Each item has `item`,
`claims`, `prediction_registered` (verbatim), `per_card` (every card: values, n, 99% intervals, band checks, die
temperatures), `test` (what was computed), `outcome` (the registered outcome, from aifoundry2 and aifoundry3 only: PASS:
holds on both cards; FAIL; CARD-DIFFERENT; INSUFFICIENT: fewer than 3 kept passes on a card), `reading`, and
`all_cards` (see "Four cards"). Cross-card results are under `cross` (MMB-c ratios, MMB-d Welch tests). MMB-X1 and MMB-T carry a
summary item plus sub-items (`MMB-X1/a..c`, `MMB-T/P1..P10`), each decided on its own. The MMB-T sub-items carry
`claims_hint_unregistered`, a guess at which claims each P speaks to, for the page writer. The plan registers the
claims only for MMB-T as a whole.

### Readings of the registered text (the choices the plan leaves open)

- **MMB-a** cycles/op = `cycles_mean / ops_per_minion`, the definition of the E1 inventory reducer that produced the
  bands (`inv/matmul-sparse-testdrive-work/analyze_group.py`). With `cycles_max`, the page's own DRAM run reads
  16,185-16,239, outside 15,000-16,200; with `cycles_mean` it reads 15,212-15,565. `cycles_max`-based values are
  reported beside. aifoundry3's DRAM band is +-6% around the mean of aifoundry2's kept DRAM launches (so it needs >= 3
  aifoundry2 passes). Launch overhead (ridge-75), launch-to-launch spread (-31) and implied clock (-30) are reported
  as `info_*`, not decided: the registered prediction is the cycles/op band only.
- **MMB-b** throughput: every kept timed launch's own `tflops` inside the band ("deterministic", read as MMB-a's "every
  launch"). Exactness: every kept timed launch `check == "exact"`, `bad_minions == 0`, `launch_errors == 0`. The smoke
  clause decides on aifoundry3 only, as registered: every `mmbench-check` and `it_test_code_loading` record from every pass
  and any smoke block has rc 0 and exact launches, with at least one of each; aifoundry2's are reported. A record with
  rc 127 (the binary is not on the card) means the test did not run: it is listed, not counted as a failure, and without
  a run of each test the clause (and so MMB-b on aifoundry3) is INSUFFICIENT.
- **MMB-c** (review, 25 Sep: the registered watt bands now decide, as registered; the first draft only reported them):
  a card holds if, for every workload, the 99% t interval of its pass values excludes 0 (the decision column) and the
  pass mean is inside its registered band: aifoundry2 fp32 23-29, fp16 24-30, int8 25-31, DRAM 6-10 W; aifoundry3
  0.92 x the aifoundry2 mean +-3 W, and the a3/a2 ratio of pass means in 0.85-1.0 (both are aifoundry3's prediction,
  since it is stated relative to aifoundry2). Holds on one card only is CARD-DIFFERENT (common rule). aifoundry3 needs
  aifoundry2's >= 3 passes for its band. Without the bands a measured 35 W above idle would have passed "26 +-3 W".
- **MMB-d**: per L2 mode, two-sided Welch on pass values of board GFLOP/s per W, alpha 0.01/3. A mode holds if the
  difference is significant with mean(a3)/mean(a2) >= 1.08 (the prediction's ">= 8%"). PASS needs all three modes.
- **MMB-e** (review, 25 Sep: the registered lead bands now decide): one-sided 99% t (t_0.99,n-1) upper bound of int8
  board GOP/s per W below 1560 = "the A100 wins" on that card; a card holds if the A100 wins there and the lead
  1560 / pass mean is inside the card's registered band (aifoundry2 1.25-1.45, aifoundry3 1.00-1.25). The decision
  column's consequence is reported on its own (`consequence`): if aifoundry3's interval includes 1560, the page drops
  "the A100 wins int8 efficiency" as a general statement.
- **MMB-f**: the rise is mean(last 1 s) - mean(first 1 s) of mean_w's own window: after the 1 s settle, samples inside
  launches. The committed data show the board reading at its plateau within the first second, then climbing slowly:
  +1.3 W from 1-2 s to 5-6 s for fp32 and int8, about 0 on DRAM. L2 holds if the 99% interval is above 0 and, on
  aifoundry2, the mean is in 0.5-2.0 W; no band is registered for aifoundry3, so there only the sign counts (the common
  rule). DRAM "~0" holds if the 99% interval lies inside +-0.5 W, the lower edge of the L2 band. This is an equivalence
  reading like the plan's other "~" tests; "interval includes 0" failed on a consistent 0.07 W offset in the test data.
- **MMB-X1**: cycles/op = `cycles_max / ops_per_minion` (the plan's reduction line); B/minion-cycle = 2048 / cycles.
  Sub-items a (shared 528.5-529.5 / 279.4-281.4), b (private fp32/fp16 529-545; a consequence line if any card has a
  launch above 560) and c (private int8 480-560; "refutes" if every launch on both cards is <= 330, "cause open" if all
  are in 330-480).
- **MMB-T** (per pass by x1_reduce.py, then over kept passes):
  - P1: the interval excludes 0 and the mean is in the band.
  - P2 (share = minion slope / board slope): the mean is in the band. The decision column names no interval test for P2.
  - P3: the interval excludes 0 and the mean is in the band; on aifoundry2 also |mean of (measured - idle-law
    difference)| <= 0.7 W.
  - P4: the remainder interval excludes 0 and the mean is in 3-7 W; minion rail: the upper end of the two-sided 99%
    interval < 1.0 W.
  - P5: DRAM, the interval excludes 0 and the mean is in 2-5 mV; matmul, |mean| <= 1 mV.
  - P6: the interval excludes 0; the band is reported only.
  - P7, every pass: start overshoot = tau-0 start max minus the top of the matmul remainder range, >= 10 W; stop dip =
    the lower of the idle0 and cool1 remainders minus the tau-0 stop-window min, >= 2 W; filtered with the card's tau,
    everything within [that idle level - 1, matmul top + 1].
  - P8: the 99% interval of the per-pass steady medians lies inside +-0.5 W.
  - P9: every kept pass reads 600 MHz only (dropped aifoundry2 passes are listed).
  - P10: the aifoundry2 mean is in 4-8 C; aifoundry3 is reported.
  - A sign disagreement between the cards' intervals gives CARD-DIFFERENT. pt-spatial-22's busy-minus-idle slope is
    reported (`busy_minus_idle_slope_a2_not_decided`), not decided.
- Summary items (MMB-X1, MMB-T): INSUFFICIENT if any sub-item is, PASS if all pass, FAIL if any fails, else
  CARD-DIFFERENT.

## Four cards (amendment of 25 Sep 2026, before any aifoundry1 data)

The owner asked for every measurement on every card after the machine fixes of 25 Sep, so the campaign runs V3-MMB on
aifoundry2, aifoundry3, aifoundry1-c0 and aifoundry1-c1 (four passes each). aifoundry1's two cards are not in the
registration: nothing registered changes for aifoundry2 and aifoundry3 (their rules, code paths and outcomes are the
same; checked on every earlier test set), and the choices below for aifoundry1's cards are made before any of their
data. The amendment text is in `AMENDMENTS.md` (V3-MMB).

**The cards.** aifoundry1-c0: firmware 1.4.1, TDP 65 W, threshold 65 C, idles in a `low_power` state at 300 MHz / 398 mV
(18.8 W board) between kernels. aifoundry1-c1: firmware 1.2.0, TDP 65 W, threshold 65 C, idles at 600 MHz / 499 mV
(32.9 W). Both governors are free (lib.sh `GOV_FREE=1`); aifoundry2 and aifoundry3 run firmware 1.3.1.

**Block (per-card parameters).** Every `$CARD = aifoundry2` test became `GOV_FREE` (heater, heating, the busy clock
rule) and the aifoundry3 branch became "pinned" (the 60 s sleep before the load step). aifoundry1's cards take
aifoundry2's values: heat to `HEAT_C=76` C before each E1 workload, before ridge-X1 and before the load step (same
software threshold, 65 C, and TDP, 65 W, so the same margin above the threshold keeps the governor off 700/800 MHz); the
heater is lib.sh's `$HEATER` (aifoundry1: `build/sparsity`, like aifoundry3's tree); memprobe `build/memprobe`; mmbench
from `~/nekko`. Sampler caps, phases, loads and flags are the same on every card. `order.json` records `gov_free`,
`device` (V3_DEVICE) and `heat_c`; `idle-state.jsonl` records the idle state at the block's start and end. The block
has no et_soc1 use-count check (it relies on lib.sh's `others_present` and per-card `ours_running`), so the other card's
queue on aifoundry1 does not stop it. `it_test_code_loading` loads `/opt/et/lib/libetrt.so` through its rpath, the
library every benchmark uses (checked with `ldd` on aifoundry2), so `ET_DEVICES` restricts it as it restricts them.

**Clock rules (cardrules.py, shared by finish, passcheck and reduce).**
- aifoundry2: the registered rules, unchanged (an E1 launch with a sample off 600 MHz inside it, or on either side of a
  launch shorter than the sampling interval; a load step with any sample off 600 MHz).
- aifoundry3: no telemetry clock rule (pinned), unchanged.
- aifoundry1's cards, the busy rule: only busy samples count (inside a launch's window, from the MMBENCH / MEMPROBE
  lines' `t_start_ms`/`t_end_ms`); idle brackets never drop anything, so aifoundry1-c0's 300 MHz idle does not drop its
  bursts. A busy sample below 600 MHz in the first second after a process's first launch starts is the clock rising from
  the idle state (the firmware may report it a management pass late): recorded as `ramp`, not a drop. Any other busy
  sample off 600 (a lift to 700/800 on a cool die, a step down later in a burst) drops the E1 launch or the load-step
  pass. implied_ghz outside 0.595-0.605 drops a launch on every card (registered).
- E1 power values on aifoundry1's cards: kept if every timed launch is kept, or if the only dropped launch is launch 0,
  dropped only for implied_ghz below 0.595 (the clock rose from the idle state inside the registered 1 s settle, before
  the power window starts); per-W values then use the kept launches' throughput. passcheck re-runs a pass when a
  workload's power values are dropped, a ridge-X1 launch other than a lone launch 0 below the band is off 0.595-0.605,
  or a load step fails the busy rule; ramp and idle clocks are notes.
- The idle clock is recorded everywhere: `results.json` `idle_mhz_minion` (the 8 s idle) and per workload
  `idle_before_mhz_minion`; passcheck's `components.thermal.clock` (each phase's idle and busy clocks); `idle-state.jsonl`.

**x1_reduce.py**: a card without a measured rail filter (aifoundry1's) is filtered with aifoundry2's tau (1.148 s); the
filtered clause of P7 is then reported, not decided, on those cards. `valid` stays the registered a2-only rule; the
callers apply the busy rule to aifoundry1's cards.

**Reducer: `all_cards`.** Each item keeps its registered `outcome` (aifoundry2 and aifoundry3, exactly as before) and
adds `all_cards`: PASS if it holds on every card on which it is tested, CARD-DIFFERENT if on some (or the tested cards'
99% intervals disagree in sign, as registered), FAIL if on none, INSUFFICIENT if any tested card has fewer than 3 kept
repeats (a missing card has none; `outcome_over_cards_with_repeats` gives the rest), REPORTED if the item is registered
for aifoundry2 or aifoundry3 only. The registered cards enter with their registered per-card holds. A band given for
aifoundry2 or aifoundry3 only is reported on aifoundry1's cards; a clause registered for each card (or for both cards
without naming one) is tested on them unchanged:

| item | aifoundry1's cards |
|---|---|
| MMB-a | tested: every kept L2 launch in its band (fp32/fp16 528.5-529.5, int8 279.4-281.4); DRAM reported (its band is aifoundry2's, aifoundry3's is relative to it) with where it falls in each |
| MMB-b | tested: throughput bands and exactness; the smoke clause (registered for aifoundry3) reported |
| MMB-c | reported (watt bands per registered card): above-idle W, board W, idle-before W and its clock, the ratio to aifoundry2, where it falls in each band |
| MMB-d | reported (a comparison of aifoundry3 with aifoundry2): per-W values, ratio to aifoundry2, a Welch test against it as information |
| MMB-e | reported (lead bands per registered card): lead, one-sided bound, A100 wins or not; `all_cards.consequence` says whether "the A100 wins int8 efficiency" holds on every card |
| MMB-f | tested as aifoundry3 (no band registered for them): L2 rise 99% interval above 0; DRAM "~0" (interval inside +-0.5 W) |
| MMB-X1 a, b, c | tested unchanged; the consequences (any card above 560; <= 330 or 330-480 on every card) over all cards |
| MMB-T P1, P2, P3, P10 | reported (bands per registered card) |
| MMB-T P4 (remainder 3-7 W, minion < 1 W), P5 (DRAM 2-5 mV, matmul +-1 mV), P6 (interval excludes 0), P8 | tested unchanged |
| MMB-T P7 | the tau = 0 overshoot (>= 10 W) and dip (>= 2 W) tested; the filtered clause (each card's own tau) reported with aifoundry2's tau |
| MMB-T P9 | tested unchanged: 600 MHz in every sample of every kept pass, idle samples included |

Items over an idle bracket (MMB-c; MMB-T P3, P4, P5, P6, P7, P9) carry each card's idle clock in `all_cards.idle_clock`,
and the reading names any card whose idle brackets are not at 600 MHz; `doc["idle_clock"]` has the full table (E1 idle
and idle-before windows, the load step's idle0 / idle-after / all idle samples, the block's power_state, ridge-X1's
readings). Expected before the data: if aifoundry1-c0 idles at 300 MHz in these blocks, P9 does not hold there, and P4
(minion rail over the cool1 baseline), P6 (droop from idle0) and MMB-c's above-idle watts include the step from the
low-power idle state to the 600 MHz burst, so a CARD-DIFFERENT there is read as the idle state, not the DRAM, droop or
matmul physics. The summary items (MMB-X1, MMB-T) combine their sub-items' `all_cards` outcomes as the registered summary
does, leaving REPORTED ones out.

**Risks for aifoundry1's cards.** (1) Firmware 1.4.1 has a 300 MHz operating point; if its thermal branch steps a hot
die (> 65 C) below 600 MHz during bursts, heating to 76 C would put c0's bursts off 600 and every pass would be re-run:
check the first real pass's passcheck on c0 before letting its queue continue. (2) The wake from `low_power` can take
longer than the 1 s ramp allowance: in the 25 Sep ~16:40 clock test on c0 (two 2 s fp32 launches 1 s apart), the first
launch after the low-power idle drew no extra power and the clock reached 600 MHz only at its end, about 2.3 s in; the
second launch ran at 600 MHz (49.4 W), and the card then idled at 600 MHz (26 W). Inside a block the smoke launches and
the heater wake the card first, so this matters only if c0 goes back to `low_power` during the block's idle gaps (E1's
8 s idle and 5 s gaps, ridge-X1's 3 s gaps, the load step's 20 s idle0 and 40 s cool1). If it does, and the wake takes
longer than 1 s: (a) E1's calibration launch absorbs the wake. It runs slow, so the timed launches get fewer iterations
or fewer repeats and the power window is shorter (down to about half: `meta.json` `timed_workloads` and `cal.jsonl` show
it), and MMB-f's rise is then taken over that shorter window. (b) An E1 launch 0 that still has busy samples below 600 MHz after its first second
drops that workload's power values. (c) The load step's first matmul and DRAM processes have busy samples below 600 MHz
after the ramp second, so the pass is dropped. (d) A ridge-X1 process with launches after launch 0 below the band re-runs
the pass. The rule is not widened after seeing the data (samples at 300 MHz inside the power window or the load step's
edges are not 600 MHz data). c0's affected items then read INSUFFICIENT, and the idle-state records say why. Check the
smoke block's and the first pass's `passcheck.err` on c0 before letting its queue continue. (3) The two cards of
aifoundry1 share a chassis: one card's heating may warm the other; each block records its own die temperatures.

## Files

- `block.sh`: one pass (or `--smoke`).
- `mmbench_power_v3.py`: the patched E1 runner (`run` / `finish`).
- `passcheck.py`: the end-of-block check (exit 4 means re-run).
- `cardrules.py`: the per-card clock rules (four cards), used by `finish`, `passcheck.py` and `reduce.py`.
- `x1_reduce.py`: the load-step reducer (copy, see deviation 7).
- `reduce.py`: the verdicts (holds the plan's N8 `mmb_pool` and `ridge_x1`).

Tests (off the card) are in the session scratchpad, `validate3/drv/mmb/` (the review's in `validate3/drv/mmb/rev/`:
`make_fail.py` builds 4+4 passes whose registered predictions must fail: int8 at 282 cycles/op, aifoundry2 fp32 at 33 W
above idle, equal per-W on the two cards, a 3 W within-run rise, private int8 at 300 cycles/op, PMIC average 1 W off.
It reduces to MMB-a, -b, -c, -d, -f, MMB-X1/c and MMB-T/P8 FAIL, and MMB-e CARD-DIFFERENT on aifoundry3's lead of 1.31,
which the first draft's rule passed. `fake_launcher.py` tests the process-time guard without a card). `make_synth.py synth` builds 4+4 modelled
passes: the real `finish` and `mmbench-report-data.py` run on every workload, and the data inject a 700 MHz sample in
an aifoundry2 E1 launch and an 800 MHz sample in an aifoundry2 load step. `make_synth.py legacy` lays out the committed
18 Sep E1 session and 20 Sep E5 load step as aifoundry2 pass 1. The variants cover one card only, a short aifoundry3,
and private int8 at 300/300, 300/510 and 400/420 cycles/op.

Four-card tests (25 Sep) are in `validate3/fourcards/mmb/`: `make_synth4.py` builds four cases (every card seeded on its
own, so aifoundry2's and aifoundry3's data are identical across cases): `pass4` (all four cards hold every tested
item: all_cards PASS), `c0differs` (aifoundry1-c0 idles at 300 MHz with lower idle power, ramps at every process start,
has a busy 700 MHz sample in one E1 workload and one load step, and private int8 at 400 cycles/op: its bursts are kept,
the two real busy drops re-run, all_cards CARD-DIFFERENT on MMB-X1/c, P4, P6 and P9 with the idle clock named),
`missing` (no aifoundry1-c1: all_cards INSUFFICIENT) and `c1short` (two passes: INSUFFICIENT). The registered outcomes
and every aifoundry2/aifoundry3 value are identical across the four cases and, on the eight earlier test sets, identical
to the reducer before the change (`cmp_registered.py`); `finish` re-run on earlier synthetic E1 directories keeps every
field. Dry runs of passes 1-4 and the smoke block for all four card ids (aifoundry1 through a hostname shim with
V3_DEVICE=0/1) are in `fourcards/mmb/dry/`.
