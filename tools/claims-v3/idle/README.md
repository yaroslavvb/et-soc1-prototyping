# V3-IDLE: idle heat/cool cycles (PLAN3 §2 "V3-IDLE", suggested E44)

The idle law's shape on aifoundry3, the unsensed slope, the 73 C split and the leakage split
(items IDLE-0, a, b, c, d, e, f, k, L; 34 claims). Pre-registered predictions: `docs/reports/data/2026-09-25-claims-v3/PLAN3.md`
§2 V3-IDLE and `plan3.json` `experiments[V3-IDLE]` (`predictions`, `components_detail`: energy-manual EXP-EM1, dvfs
EXP-dvfs-4, horace-lowpower-X4).

## Running

```
bash tools/claims-v3/idle/block.sh <pass> [--smoke]     # from either tree (this repository or ~/nekko on aifoundry3)
V3_DRY=1 bash tools/claims-v3/idle/block.sh 1           # no device access: prints every device call
```

| pass | what | cooling | used by |
|---|---|---|---|
| 1-9 | a short cycle | 900 s | IDLE-0, a-f, k |
| 11-19 | an IDLE-LONG cycle (overnight, when the room is cool) | 5400 s aifoundry2, 2700 s aifoundry3 | IDLE-L; also a cycle for 0, a-f, k (first 900 s of its cooling) |
| any, `--smoke` | the pipeline check (exp `idle-smoke`) | 20 s, 2 bursts | nothing (checked by `reduce.py --check-pass`) |

Schedule lines: `idle 1`, `idle 2`, `idle 3` on each card, >= 30 min apart and on at least two different days (PLAN3
"cycles on at least two different days"). IDLE-LONG passes (`idle 11`, `idle 12`, `idle 13`) go in an overnight
schedule of their own, never interleaved. On aifoundry3 run `idle 1` before V3-CAT's hot passes: `tools/claims-v3/cat/block.sh`
takes its hold temperature from the highest reading in `$DATA_ROOT/idle/p*/telemetry.jsonl.gz` (PLAN3 day 3: "IDLE cycle 1 first").
Every kept cycle counts in the reduction, so decide beforehand which passes run and do not leave kept passes out afterwards.

## What one pass does, in order

1. Refuses to start (exit 3, no directory) when lib's `others_present` sees another user or another user's device
   process, when lib's `ours_running` sees a device process of this user (another session, a leftover), or when the
   `et_soc1` use count (`lsmod`) is not 0.
2. `block_begin` (one die reading), then `start_sampler` (`ettelem sample --every-ms 100`, `--seconds` = 900 + cooling
   + 90) for the whole cycle. Right after the start the use count is read 5 times; its maximum (normally 1: our
   sampler) is the intrusion baseline.
3. **Heat.** 2 s random-data fma bursts on all 1024 minions, each under `hold10`:
   `$HEATER --test fma --type fp32 --pattern none --values randn --shires 0xffffffff --per-shire 32 --seconds 2 --seed 1`
   (lib's HEATER: `build/sparsity_t2/host/sparsity_host` on aifoundry2, `build/sparsity/host/sparsity_host` on aifoundry3),
   until the die reads >= the target (aifoundry2 88 C; aifoundry3 90 C, which it never reaches, so it heats to its
   plateau), at most 150 bursts or 900 s. Before each burst the die is read from the running sampler's newest line
   (`$SAMPLER_OUT.raw`, at most 3 s old), and the card is checked: another user (`others_present`) or any device
   process but our sampler, of any user, stops the cycle (exit 3), so the heater never lands on someone else's run.
4. **Cool.** No launch for the cooling time. Every 10 s the block checks that the sampler is alive, that no device process
   other than our sampler runs (any user, by lib's `DEV_COMM`), and that the use count is not above the baseline. An
   intrusion stops the cycle (mark `abort`, `block_end fail`, exit 3: the queue sets the pass aside and retries it after
   10 min), because another kernel spoils the idle samples. A login without a device process is only marked (`login`).
5. SIGTERM the sampler (`stop_sampler`), wait 2 s (block_end's die reading starts ettelem again, which often fails right
   after an instance), gzip the telemetry and the heater's output, `reduce.py --check-pass` (stdlib only),
   `block_end ok|fail` with a one-line note (bursts, Tmax, cooling samples, largest sample gap, off-600 count, bins,
   warnings such as a failed heater burst).

block.sh wraps lib's `die_c` (local helper, lib.sh unchanged): lib's `block_end` writes the reading unquoted into
block.json, so a failed reading would leave invalid JSON (`"die_c_end":,`); the wrapper writes `null`. After an
intrusion (exit 3) the wrapper does not open the card at all, because the other process may be a sampler of its own and
the management node has one opener. reduce.py also reads a block.json with an empty value (older blocks, other writers).

Files in `$DATA_ROOT/idle/p<N>/`: `telemetry.jsonl.gz`, `launches.jsonl` (host times around every heater process and its
rc), `heat.jsonl` (the die reading before every burst), `marks.jsonl` (`cycle_start`, `heat_end` with die/reason/bursts,
`cool_start`, `cool_end`, `abort`, `login`), `cycle.json` (parameters), `heater.out.gz`, `check.json`, `block.json`,
`code.sha256`. About 1 MB per short pass, 3-4 MB per long pass (gzipped 10 Hz telemetry).

## Card minutes per pass

| | aifoundry2 | aifoundry3 |
|---|---|---|
| short pass | ~17-20 (begin, sampler and end ~1; heating from a ~74 C rest to 88 C ~1-3; idle 15) | ~22 (150 bursts ~6.5; idle 15; ~0.5) |
| 3 short passes | ~55 (plan: 66) | ~66 (plan: 80) |
| long pass | ~93 | ~52 |
| smoke | ~30 s | ~30 s |

The heating time on aifoundry2 is estimated from the committed runs (randn from 81 C reached 88 C in 10-210 s,
2026-09-21-horace-aifoundry2/long). On aifoundry3 the burst cap (150 back-to-back bursts of ~2.6 s) ends the heating before the
900 s cap.

## What is dropped, and why

- A pass whose `block.json` is not `ok` (intrusion, heater failing 3 times in a row, sampler failure, failed check),
  a dry run, or one without `cool_start`/`cool_end` marks. A single failed heater burst is only a warning in the note and
  check.json: rule A drops every launch window, so it does not touch the idle samples (the queue does not retry a failed
  block, so failing the pass for it would lose the cycle). Kept and dropped passes are listed in `verdicts.json` `passes`.
- Samples from 1 s before to 6 s after any heater launch (rule A), and every sample outside the cooling window.
- aifoundry2 samples with `mhz.minion != 600` (registered sample-level rule; the count is in the block note as `off600` and in
  `passes[].counts`). aifoundry3 is pinned at 600 MHz; its off-600 samples are counted, not dropped (none expected).
- Whole-degree bins with fewer than 20 samples in a cycle.
- Not dropped: a pass that found the die already at its target (e.g. right after another experiment's heavy block) makes no
  burst; its cooling starts at `cool_start` and it is kept.
- For IDLE-k: aifoundry2 cycles whose highest reading is below 86 C, and samples within 20 s of the last burst.
- For IDLE-L: flip_thermal_model.py step 2a's own rule (no launch within 4.5 s, the first 20 s of the pass, off-600 samples).

## Deviations from the plan's commands, with reasons

1. **One cycle per block** instead of `idle_cycles.sh ... 3 900` (three cycles under one 90-min sampler): each block stays under
   ~22 min so the queue can interleave experiments, and each cycle is a separately started block (the unit of replication).
2. **Die reading during heating from the running sampler's output**, not a second `ettelem sample --seconds 1` per burst as in
   `heat()` of run_reruns_warm.sh: lib.sh forbids a second opener of the management node while the sampler runs. As a result the
   bursts are back to back (~88% duty against heat()'s ~60%), so 150 bursts take ~6.5 min rather than ~9 min, and aifoundry3's
   plateau is that of a near-continuous heater (which is what IDLE-0 asks for). The plateau is logged per cycle (Tmax).
3. **Heating caps**: 150 bursts or 900 s, whichever comes first (EXP-EM1 details: "at most 150 ... until minshire >= target or 15 min").
4. **aifoundry3 target 90 C** (EXP-EM1 command: heat to the plateau), not X4's 62 C: the merged plan's IDLE-LONG only extends the
   cooling, and a 62 C stop could end the heating before the plateau that IDLE-0 logs.
5. **Other-user check**: the plan's "skip the cycle if the et_soc1 use count != 1 (only our sampler)" is checked before the block
   (count must be 0: the sampler is not yet running) and every 10 s of the idle against the sampler's own count; instead of
   skipping, the block exits 3 and the queue retries the pass later.
6. **Heater binary**: lib's HEATER (sparsity_t2 on aifoundry2, as the EXP-EM1/dvfs-4 commands and run_reruns_warm.sh; sparsity on
   aifoundry3, which has no sparsity_t2). X4's command names build/sparsity on aifoundry2. Both binaries are built from
   workloads/sparsity and carry the same option set (checked with `strings`); nothing of sparsity_t2 is needed on aifoundry3.
7. **Launch times** are host timestamps around each heater process, so the exclusion window [start - 1 s, end + 6 s] also covers
   the process's start-up and tear-down.
8. **IDLE-LONG as pass numbers 11-19** of the same experiment; a long pass is a complete cycle and also serves items 0, a-f and k
   with its first 900 s of cooling (the plan: "extend each cycle's cooling"). A long block (~93 min on aifoundry2) is longer than
   the ~35 min block limit: a cooling curve cannot be split into blocks without other experiments' kernels in between, so these
   passes run overnight from their own schedule.
9. **Sampler length**: `--seconds` 900 + cooling + 90 per block (the plan: 5400 for its three-cycle script); stopped with SIGTERM.

## The reduction (reduce.py), and the readings the plan left open

```
python3 tools/claims-v3/idle/reduce.py --data <dir with aifoundry2/ and aifoundry3/ laid out like DATA_ROOT> --out verdicts.json
python3 tools/claims-v3/idle/reduce.py --check-pass $DATA_ROOT/idle/p1      # stdlib only; what block.sh runs
```
The full reduction needs numpy (not scipy); `--check-pass` needs only the standard library, so the card hosts need no numpy.
It runs on partial data (one card, fewer passes) and says INSUFFICIENT where a card has fewer than 3 kept cycles.
Constants are the published ones: the law 12.6349 + 23.2568 e^((T-80)/36) (2026-09-21-horace-aifoundry2/model.json), the
aifoundry2 SRAM law -0.3226 + 2.8091 e^((T-80)/36) (2026-09-23-energy-manual/catalogue.json), the 22 Sep split
11.05 / 2.00 / 3.64 / 15.10 W, the busy power 63.9 W, the flip_thermal_model.py T_L grid 16-80 C.

Common: bins are whole degrees of `temp_c.minshire[0]` (n >= 20 per cycle); a cycle's offset is the unweighted mean of its bins'
(bin mean - law), as on the pages ("the mean of its temperature bins"); slopes are unweighted least squares over bin means;
unsensed = board_w - (sp.minion_w + sp.sram_w + sp.noc_w)[avg]; intervals are two-sided 99% t over cycle-level values; a
band test means the whole interval lies inside the band.

| item | card | outcome rule as implemented |
|---|---|---|
| IDLE-0 | a3 | every cycle's highest reading inside 60-66 C |
| IDLE-a | a3 | the registered decision: offset interval (bins 51..Tmax) inside [0.3, 0.9] W and residual-slope interval inside [-0.05, 0.05] W/C. The prediction's "every bin" check is reported (per-bin intervals), not decisive |
| IDLE-b | a2 | "in every bin" + "99% t over 3 cycles": every bin visited by >= 3 kept cycles has its interval over cycles inside [-0.53, +0.07] W; the cycle offset is reported |
| IDLE-c | a2 | the registered decision: the upper end of the unsensed-slope interval (bins 74-88 C) < 0.15 W/C; the metered-rail slope over 75-80 C is reported against 0.51 +- 0.07 |
| IDLE-d | a2 | cycles with a 73 C bin: minion, SRAM, mesh and unsensed intervals each inside the 22 Sep value +- 0.2 W |
| IDLE-e | a3 | SRAM slope interval (bins 51..Tmax) inside [0.017, 0.077] W/C, and in every bin visited by >= 3 cycles the lower end of the excess over the aifoundry2 SRAM law >= 0.8 W |
| IDLE-f | both | condition "Tmax >= 70 C" read as ">= 3 aifoundry3 cycles with a 70 C idle bin"; then a3's unsensed interval at 70 C inside [12.9, 13.9] W. Otherwise the outcome is CARD-DIFFERENT with `condition_met: false` (values stay per card, each at its own temperature) |
| IDLE-k | a2 | cycles from >= 86 C; samples >= 20 s after the last burst within the first 900 s of cooling; flip_thermal_model.py step 2a fit per cycle; each cycle's best T_L inside 30-48 C, its shares A80/63.9 over the T_L values within 0.005 W rms of the best inside 0.31-0.47, and the interval of the cycle residual over 70-85 C bins inside [-0.4, 0.0] W. `decision`: Kanter's 30% established only if every cycle's lowest share > 0.30 |
| IDLE-L | both | long passes; flip_thermal_model.py step 2a exactly; a2 intervals of best T_L inside [30, 45], A80 inside [19, 29], A80/T_L inside [0.62, 0.68]; a3 slope at 56 C inside [0.22, 0.38] and offset (rule-A bins of the whole cooling) inside [0.3, 1.1]. `leakage_split` identified only if A80's interval is narrower than +-3 W |

Outcomes: PASS (holds on each registered card), FAIL, CARD-DIFFERENT (holds on one registered card and fails on the other: IDLE-L;
and IDLE-f when its condition is not met), INSUFFICIENT (a registered card has fewer than 3 kept cycles for the item; for the
per-bin tests of IDLE-b and IDLE-e also when no bin was visited by >= 3 kept cycles, since no bin then has the needed repeats;
IDLE-e still FAILs on its slope alone). `verdicts.json` also lists every pass with its UTC date and
`info_days_of_kept_cycles_utc` per card, for PLAN3's "cycles on at least two different days" (reported, not a reduction rule).

## Known risks (for the owner, before any data)

- **Edge bins.** The reading is whole degrees, so the highest and lowest bin of a cycle hold only part of a degree of true
  temperature; on aifoundry2 (0.6 W/C) their means sit up to ~0.2-0.3 W off the law. The synthetic test (truth: a flat -0.10 W)
  fails IDLE-b's "every bin" test in its edge bins (70, 75, 76, 87 C). The registered rule has no edge-bin exclusion, so none is
  applied; an amendment (for example, drop each cycle's first and last bin) would have to be made before the first run.
- aifoundry2 cools from 88 C to only ~76 C in 15 min on a warm day (the committed gaps: 89 -> 81 C in ~6 min), so IDLE-d (73 C
  bin) is INSUFFICIENT unless a cycle runs on a cool evening or IDLE-LONG runs.
- IDLE-k and IDLE-L on aifoundry2 are expected to be unidentified: the T_L profile is flat over the short cooling range (plan:
  "Expect it to be inconclusive"), so IDLE-k FAILs on the share band and Kanter's 30% is not established.
- The intrusion poll runs every 10 s: a foreign process that opens and closes the card between two polls is not seen.

## Tests done

- `bash -n`; `V3_DRY=1` of passes 1 and 11 and `--smoke` on aifoundry2, and of passes 2 and 12 and `--smoke` with a `hostname`
  shim for aifoundry3 (which exercises the aifoundry3 branch: HEATER build/sparsity, target 90, 150-burst cap, 2700 s cooling).
- A fake tree (scratchpad `validate3/drv/idle/faketree`: lib.sh with a fake dev_mngt_service, a fake ettelem streaming
  synthetic JSON and honouring SIGTERM, a fake 2 s heater, `lsmod`/`who` shims) ran the non-dry paths: a full short cycle
  (40 s cooling), the smoke, an abort on a foreign `*_host` process during the idle, an abort on a rise of the use count, the
  refusal to start on a held card, and the "already done" guard.
- reduce.py on synthetic data with a known truth (`gen_synth.py`: all-pass, a3 offset 1.2 W, partial, cool day) and on the
  committed aifoundry2 cooling gaps of 2026-09-21-horace-aifoundry2/long and long2 (`legacy_to_passes.py`).
- Review (scratchpad `validate3/drv/idle/review`): `gen_review.py` cases `allfail` (every item's truth outside its band:
  all 9 items FAIL, IDLE-f with its condition met), `truepass`, `mixed` (aifoundry3 short of long passes: IDLE-L
  INSUFFICIENT) and `lib_badjson` (a block.json with `"die_c_end":,` is read, a failed pass is dropped); the writer's five
  synthetic sets give the same outcomes as before; IDLE-b/IDLE-e with no bin in 3 cycles give INSUFFICIENT. A fake tree
  (`review/faketree`, run only through the guarded `review/run_fake.sh`) ran a full cycle, the smoke (~30 s wall), an intrusion
  during the idle and one during heating (exit 3, block.json valid with `die_c_end` null, no ettelem start after the abort),
  and the refusal to start while a device process of this user runs.
- Real card, by accident (25 Sep 09:51:57-09:54:46, aifoundry2, the reviewer's mistake: a fake-tree test ran the real
  block from the repository): 62 heater bursts under `timeout 10` (rc 0, 2.67 s per burst cycle, die 59 -> 84 C, clock 700/800
  MHz below ~68 C), live die readings from the sampler 49-121 ms old, sampler stopped by SIGTERM through the EXIT trap. The
  data were moved to `build/claims-v3/reviewer-tests/` by another session and are not a pass.
