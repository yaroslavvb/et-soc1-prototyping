# Experiments: the register

Every measurement in this directory has an ID here. An entry says what question it answers, exactly when and
where it ran, the command that produced it, where the **raw** data lives in this repository, and what it
cannot tell you. Cite as **E1**...**E19**.

All card work is on **aifoundry2**, one ET-SoC-1 PCIe card, firmware at et-platform `353f20e`. Unless an entry
says otherwise, the minion clock was a steady **600 MHz** at **516–518 mV** on the die, verified in every
telemetry sample of the session.

Rebuild every analysis, model, GIF and report from the raw data with a single script:

```
tools/ettelem/finish_horace.sh        # no card needed; ~10 min, mostly the RTL replays
```

---

## Standard protocol: the "strict start"

Used by E9, E12, E15 and E16, and the reason their numbers can be compared at all. Before every measured run:

1. If the mean minion-shire sensor is below the pre-heat temperature (84 °C), run 2-second bursts of
   random-data matmul until it reaches it.
2. Idle, card closed, until that sensor **first reads 80 °C** on the way down. Approached from above, the
   81 → 80 step is an edge, not a range, so the die is in the same state each time.
3. Launch the workload.

Runs go in shuffled blocks, one of each configuration per block, so any drift over a session spreads evenly
across configurations rather than landing on one. Telemetry is sampled at 10 Hz throughout by
`tools/ettelem/ettelem sample`, which holds the management node open for the whole session.

How well it worked, measured in E9: the thermal model puts the die at **80.96 °C ± 0.11 °C** at the 46 launch
instants, and idle power in the two seconds before launch at **36.29 W ± 0.06 W**.

---

## E1 — One memory access taken apart (2026-09-19)

**Question (Q4):** what does a single load cost, by stage and by power rail?
**Tool:** `workloads/memprobe` (device kernel with an op-program interpreter, host, `gen_ops.py`,
`analyze.py`, `run_power.py`).
**Raw data:** `docs/reports/data/2026-09-19-memprobe-aifoundry2/`.
**Method:** `evict_va` (CSR 0x89f) places a line at a chosen level, then one timed load; 1,500 addresses for
the L3 map, 19,000 loads at random phases for refresh; energy from the service processor's per-rail stats
trace during strided loops sized to each level.
**Findings:** [15-earlier-findings.md](15-earlier-findings.md).
**Caveats:** timing is load-to-use with one load in flight; the energy figures come from the 133 ms rail
averages, not from a per-access measurement.

## E2 — The `hpmcounter3` carry bug, reproduced in RTL (2026-09-20)

**Question (Q4, Q6):** why does the cycle counter read 128 short?
**Tool:** `rtl-sim/pmu_carry/` (Verilator 5.042 in `~/.local/verilator`, testbench `tb.sv` driving R2's
`shire/neigh/neigh_pmu.v` unmodified).
**Method:** assert count-up on counter 0 every cycle, read it every cycle, print every step that is not 1.
**Finding:** each counter is a 7-bit pre-counter plus a 57-bit post-counter; twelve counters share **one**
adder that folds pre-counter overflows into the post-counters round-robin, and a read ignores the pending
overflow bit. So after every wrap the value is 128 short until the adder comes round: 12 cycles in simulation,
11 on the card. `fixcyc()` in `workloads/memprobe/kernel/memprobe.c` corrects it.
**Caveat:** the Erbium RTL is a later revision than the taped-out silicon; the cycle counts differ by one.

## E3 — Device flame graphs (2026-09-20)

**Question (Q7):** can kernel time be attributed to regions on the device?
**Tool:** `workloads/traceprof` + `scripts/trace-flamegraph.py`.
**Raw data:** `docs/reports/data/2026-09-20-traceprof-aifoundry2/`.
**Caveat:** `fcvt.s.lu` traps (cause 0x1e) on this chip, so loop counters in floating-point code must be
32-bit; profile-region strings resolve as ELF file offsets, not virtual addresses.

## E4 — A counter-select syscall, in simulation only (2026-09-20)

**Question (Q7):** could a kernel choose its own PMU events?
**Artifacts:** `patches/0003-pmc-configure-syscall-353f20e.patch`, `scripts/build-minion-fw.sh`,
`workloads/pmcsel/`.
**Status:** built and verified in `sys_emu`. **Never run on the card**, because it needs a signed firmware
image (see Q7 in [02-requests.md](02-requests.md)). Treat any claim about per-event counters on silicon as
untested.

## E5 — Load step: power, temperature and the rails (2026-09-20, 21:09–21:12)

**Question (Q8):** how do board power, the three rail sensors and the die temperature respond to a load step?
**Tool:** `tools/ettelem/run_thermal.sh`; 10 Hz sampling.
**Raw data:** `docs/reports/data/2026-09-20-power-aifoundry2/thermal-telemetry.jsonl`, `thermal-phases.jsonl`.
**Findings:** rail averages lag board power by about 2 s; idle power depends on recent load; leakage slope
**0.78 W/°C** on the board (0.38 on the minion rail) under load. See
[14-card-behaviour.md](14-card-behaviour.md).

## E6 — Per-shire on-die voltage map (2026-09-20)

**Question (Q8):** how far down can voltage be resolved?
**Method:** raise the service processor's log level to DEBUG (`DM_CMD_SET_DM_TRACE_CONFIG`), extract the SP
trace, parse one record per shire per pass.
**Raw data:** `docs/reports/data/2026-09-20-power-aifoundry2/per-shire-voltage-idle.json`.
**Caveat:** restore the log level afterwards (`ettelem loglevel info`).

## E7 — Horace experiment, first version: uncontrolled (2026-09-20, 21:14–21:19)

**Question (Q9):** does operand data change matmul power on this chip?
**Raw data:** `docs/reports/data/2026-09-20-power-aifoundry2/horace-*`.
**Caveat:** three rounds back to back with the die drifting from 79 to 90 °C, so a fitted temperature term was
needed. **Superseded by E9.** Kept because it is the only session that reached 90 °C and 70 W under the
governor without being stopped.

## E8 — Horace experiment, second version: each run started at 80 °C (2026-09-20, 21:34–21:44)

**Question (Q10):** same, with the die cooled to a common temperature first.
**Raw data:** `docs/reports/data/2026-09-20-power-aifoundry2/horace2-*`.
**Result:** 20 runs, 10 patterns, all started at exactly 80 °C; rounds agree within 1.1 W.
**Superseded by E9**, which has more repeats and a de-quantised temperature.

## E9 — Horace experiment, third version: strict, 14 patterns (2026-09-21, 06:55–07:52)

**Question (Q11):** the definitive data-dependent power measurement.
**Command:**
```
tools/ettelem/run_horace_strict.sh build/horace3 80 84 4 5 2 7 \
  "zeros ones pi sparse50 uniform randn" \
  "signs pow2 mant a_randn_b_ones a_ones_b_randn ternary sparse75 checker"
```
**Protocol:** the strict start above; 4 burn-in cycles, then 5 shuffled blocks of the 6 main patterns, with the
8 extra patterns in the first 2 blocks; 7 s per run; random patterns get new random tiles each block (seed =
block + 1). **46 measured runs.**
**Raw data:** `docs/reports/data/2026-09-21-horace-aifoundry2/strict/` — `runs.jsonl` (one line per kernel
launch), `starts.jsonl` (one per run: pattern, seed, reading at launch, seconds spent approaching),
`telemetry.jsonl.gz` (10 Hz, compacted), `tiles/<pattern>.<seed>.bin` (**the exact operand tiles the card
ran**, 2 × 1,024 bytes).
**Analysis:** `tools/ettelem/analyze_horace_strict.py` → `horace3.json`, `horace3.txt`.
**Findings:** [10-data-dependent-power.md](10-data-dependent-power.md).

## E10 — Cool-start runs: the clock governor (2026-09-21, 06:45–06:54)

**Question (Q11):** what does the firmware's governor do when the die starts below its 65 °C threshold?
**Command:** `tools/ettelem/run_horace_cold.sh build/horace_cold 63 300 zeros randn ones randn zeros ones`
**Raw data:** `docs/reports/data/2026-09-21-horace-aifoundry2/cold1/`, `cold2/`.
**Precondition:** the card had idled overnight to 62 °C. This cannot be recreated on demand; the die needs
hours to get below 65 °C.
**Findings:** the governor and the speed effect, in [14-card-behaviour.md](14-card-behaviour.md).
**Caveats:** 7 runs, start temperatures differ by up to 2 °C, and the governor changes the operating point
within seconds. This is a demonstration, not a controlled experiment. `tools/ettelem/run_vf_cold.sh` is
written for a careful version and **has never been run**.

## E11 — Switching activity of the multiply-add unit, card tiles (2026-09-21)

**Question (Q11):** how many transistor-level events does each data pattern cause?
**Tool:** `rtl-sim/fma_toggle/` — eight copies of R2's `txfma_top` (the 7-stage fused multiply-add unit, one
per vector lane) under Verilator, driven with the micro-op stream of a 16×16×16 `TensorFMA32`: for each row of
B, for each row of A, two micro-ops of eight `c = a·b + c`, 512 micro-ops per op, with R2's zero gating and
lane clock gate modelled.
**Input:** the tiles E9 dumped, so the simulation replays *exactly* what the card computed.
**Command:** `python3 rtl-sim/fma_toggle/toggles.py --tiles-dir <tiles> --patterns ... --out toggles.json`
**Raw data:** `docs/reports/data/2026-09-21-horace-aifoundry2/toggles.json`.
**Correctness check:** every result is compared against software; 8,192 of 8,192 multiply-adds of two
random-data ops match bit for bit.
**Counts, per op and per minion:** `ff_clocked` (register bits that saw a clock edge with enable high),
`nets` (toggles of every named net, both edges, clocks excluded), `by_block` (the same split by RTL file),
`bus` (operand words presented to the lanes), `lane_valid` (of 4,096).
**Caveats:** RTL, not a netlist; zero-delay, so **no glitches**; only the multiply-add units, not the
scratchpad, register file or tensor state machine around them; a "net" is a named signal counted at each level
of hierarchy.

## E12 — Long runs: minutes instead of seconds (2026-09-21, 08:56–12:59)

**Question (Q12):** how does the die behave when a workload runs for minutes?
**Command:** `tools/ettelem/run_horace_long.sh build/horace_long tools/ettelem/horace_long.sched 80 84 90 900 18000 600`
**Protocol:** strict start, then **one process** per run for up to 600 s. The runner stops a run when the
sensor reads **90 °C**, when board power reaches 73 W, or when telemetry goes stale, by touching a file the
host polls between launches (`--stop-file`). 90 °C is inside what this card had already seen (93 °C, 70 W in
E7). **29 runs in 4 hours** — after a hot run the die needs up to six minutes to return to 80 °C.
**Raw data:** `docs/reports/data/2026-09-21-horace-aifoundry2/long/` (+ `schedule.txt`).
**Findings:** [12-heat-management.md](12-heat-management.md).
**Caveat — a real confound:** during run 27 the card's cooling changed abruptly (under a constant 42 W the die
fell from 84 to 72 °C in four minutes; most likely someone changed the airflow in the lab). **All fits stop at
13,950 s.** Runs 27 and 28 are in the charts but not in any fit.

## E13 — Switching activity of structured matrices (2026-09-21)

**Question (Q15):** what do structured operands do to the flip counts?
**Tool:** `tools/ettelem/make_tiles.py` generates 17 kinds of 16×16 operand pair (Hadamard, DCT, the cos and
sin halves of a DFT, butterfly factors and their dense kaleidoscope products, identity, permutation, diagonal,
tridiagonal, block-diagonal, upper-triangular, rank-1, circulant, 4-bit quantised, weights × ReLU activations,
and a matrix of −0.0), two seeds each; E11's bench then counts their activity.
**Raw data:** `structured_tiles/*.bin`, `structured_toggles.json`.
**Note:** `make_tiles.py` normalises negative zeros to +0.0 everywhere except the deliberate `negzero` kind,
because `x · 0` leaves −0.0 for negative x and the chip only gates the all-zero bit pattern.

## E14 — Predictions recorded before the matrices ran (2026-09-21, 13:08:33)

**Question (Q15):** is the model predictive, or only descriptive?
**Method:** E13's flip counts through the model of E17, giving power and a heating curve for each of the 17
kinds. **Written to disk at 13:08:33; the first of those matrices ran on the card at 13:16.**
**Raw data:** `structured_predictions_before.json` (its `made_at` field is the timestamp).
**An earlier, weaker instance of the same idea:** `predictions_before.json`, recorded at 06:50:12 on 09-21 for
six patterns first run at 06:59, from a model fitted to the 09-20 data. That set was also used to *choose*
between model forms, so it is not a clean test of the final form; E14 is.

## E15 — Ablations and structured matrices, 7 s each (2026-09-21, 13:08–14:14)

**Question (Q14, Q15):** where do the watts go, and do the structured predictions hold?
**Command:** `tools/ettelem/run_ablation.sh build/ablation1 tools/ettelem/ablation.cfg 2 7`
**Configurations (30, each run twice, shuffled):** an integer spin loop on all cores and on a quarter of them;
fp32, fp16 and int8 TensorFMA on zeros, ones and random data; random fp32 on 256, 512, 768 and 1,024 minions;
TensorLoad streaming from L2 and from DRAM; and 14 structured matrices from E13.
**Raw data:** `ablation/` (+ `configs.txt` listing every configuration).
**Analysis:** `analyze_ablation.py` → `ablation.json`, `ablation.txt`.
**Findings:** [13-why-low-power.md](13-why-low-power.md) and the validation table in
[10-data-dependent-power.md](10-data-dependent-power.md).

## E16 — Long runs of structured matrices (2026-09-21, 14:16–15:08)

**Question (Q15):** does the *heating* prediction hold, not just the power?
**Command:** `tools/ettelem/run_horace_long.sh build/horace_long2 build/horace_long2.sched 80 84 90 600 3600 120`
**Raw data:** `long2/` (+ `schedule.txt`). 8 runs: ones and random normal as references, then Hadamard,
kaleidoscope, ReLU, −0.0, the DFT pair and a block-diagonal matrix.
**Why it matters for provenance:** this session happened **after** the model was fitted and the predictions
recorded, on a different afternoon, with matrices that did not exist when the model was built.

## E17 — The flips-to-temperature model, and its out-of-sample tests (offline, 2026-09-21 and 09-22)

**Question (Q12, Q16):** turn flip counts into a temperature prediction, and find out how much of that is fit
rather than prediction. **No card time**: this runs on the saved telemetry.

**Fit** (`tools/ettelem/flip_thermal_model.py`):
```
python3 tools/ettelem/flip_thermal_model.py <data>/long@13950 <data>/strict \
  --leak-only <data>/cold1 <data>/cold2 --anchor 62:26.7 --toggles <data>/toggles_all.json --out model.json
```
Leakage is fitted to the **idle** samples of all four sessions (no launch within 4.5 s), then the flip energies
to the **busy** samples with leakage held fixed, then the thermal network to the sensor reading driven by
measured board power. `--anchor 62:26.7` pins the slowest stage with the one overnight idle equilibrium.
**Output:** `model.json`, `model.txt`.

**Out-of-sample tests** (`tools/ettelem/validate_flip_model.py`, fits nothing):
- **Time split** — every parameter refitted on the first 7,400 s of E12 plus E9 (`model_firsthalf.json`), then
  the 12 later runs predicted: `validation_timesplit.json`.
- **Different session** — that same first-half model, and separately the published model, applied to E16:
  `validation_afternoon_firsthalf.json`, `validation_afternoon.json`.
- In both, the thermal state at each launch is estimated **causally**, by an observer that has seen the
  telemetry up to that launch only; from launch on, nothing measured enters the simulation.

**Findings and numbers:** [11-thermal-model.md](11-thermal-model.md).

## E18 — Wake-up probe: is any cache array power-gated when idle? (2026-09-22, 11:39)

**Question (Q20):** R9 says cache data arrays sit behind leakage-suppression transistors and pay a small
wake-up latency on first access. Does this card show one?
**Tool:** `workloads/memprobe`, new experiment `gen_ops.py wakeup`.
**Method:** place one line at a chosen level with `evict_va`, spin the minion on its cycle counter for a swept
idle interval (0 to 16.7 M cycles, i.e. up to 27 ms) without touching that line, then time a single load of it.
**One line per (repeat, level)**, so only the idle time varies; 20 repeats; one hart.
**Command:**
```
python3 workloads/memprobe/gen_ops.py wakeup --out W --reps 20 --seed 11 \
    --delays 0,1000,10000,100000,1000000,4000000,8000000,16000000
build/memprobe/host/memprobe_host --program W/wakeup.ops --out-dir W --budget 40
```
**Raw data:** `docs/reports/data/2026-09-22-dvfs-aifoundry2/wakeup/` (`wakeup.ops`, `wakeup.json` labels,
`wakeup.u32` results). Card held 4.9 s.
**Result:** paired difference between the longest and shortest idle is 0 cycles for L1 and L3, −11 for L2
(noise), +10 for DRAM (row closure). No wake-up anywhere.
**Caveats:** cannot detect a penalty below about ten cycles, and cannot test idle intervals beyond 27 ms, which
is the widest the delay op encodes. The minion keeps executing throughout, so only the array under test is
idle.

## E19 — Idle power after 20 hours, as an out-of-sample check (2026-09-22, 11:44)

**Question (Q20):** how much does an entirely idle card leak, is there a deep idle state, and does the leakage
curve fitted on 21 September still hold on a different day?
**Method:** the card had been untouched for 20.4 h. Sampled `ettelem sample --seconds 60 --every-ms 200`, with
no workload at any point.
**Raw data:** `docs/reports/data/2026-09-22-dvfs-aifoundry2/idle_20h.jsonl.gz` (300 samples).
**Result:** 31.79 ± 0.04 W at 73.0 °C, 600 MHz, 518 mV; minion rail 11.05 W, SRAM 2.00 W, mesh 3.64 W,
15.10 W on no rail sensor. The model of E17 predicts 31.78 W — error **+0.01 W**. No sign of a deep idle
state.
**Why it counts as a test:** the model was fitted on 21 September in a cooler room, on sessions whose idle
stretches were minutes, not hours. Nothing about today's measurement was in the fit.

## E20 — The strict protocol on a second card (aifoundry3, 2026-09-22, 12:12–12:25)

**Question (Q21, Q22):** does the data-dependent power effect reproduce on a different card, and does the
flip model fitted on aifoundry2 predict it without refitting?
**Method:** `run_horace_strict.sh` exactly as in E9, with the launch temperature set to 55 °C instead of 80 °C
because that card idles at 51 °C and cannot be held at 80 °C between runs. 2 burn-in runs, 3 blocks of the six
main patterns plus one block of the two extras, shuffled, 7 s each, each launched when the sensor first reads
55 °C after a pre-heat to 60 °C. 20 recorded runs, launch temperature 55.77 ± 0.18 °C.
```
ssh aifoundry3 'cd ~/nekko && tools/ettelem/run_horace_strict.sh build/strict3 55 60 2 3 1 7 \
    "zeros ones pi sparse50 uniform randn" "signs mant"'
python3 tools/ettelem/analyze_horace_strict.py DATA/2026-09-22-horace-aifoundry3 \
    --toggles DATA/2026-09-21-horace-aifoundry2/toggles.json --out .../horace3.json
python3 tools/ettelem/compare_cards.py --card aifoundry2=... --card aifoundry3=... \
    --model DATA/2026-09-21-horace-aifoundry2/model.json --toggles ... --out .../cards.json
```
**Raw data:** `docs/reports/data/2026-09-22-horace-aifoundry3/` (`runs.jsonl`, `starts.jsonl`,
`telemetry.jsonl.gz`, `tiles/`, and the derived `horace3.json`, `cards.json`, `transfer.json`,
`leakage_crosscard.json`).
**Result:** the same ordering and nearly the same magnitudes as E9 — zeros 1.89 W over idle against 1.96,
random normal 24.86 against 27.11. The aifoundry2 model applied unchanged is off by 1.38 W rms; after one
scale factor of **0.924** the residual is **0.20 W rms** over a 1.9–25 W range. Calibrating that factor on a
single run and predicting the other seven gives 0.36 W rms in the median, 0.27 W if the calibration run is
random data. The aifoundry2 idle law extrapolated 25 °C below its fitted range predicts this card's idle power
to **+0.73 W** out of 25 W.
**Caveats:** the two sessions are at different launch temperatures, so only *switching* power (board power
minus the idle power measured just before each run) is comparable, not absolute watts. The thermal network is
not comparable at all: aifoundry3 sheds heat visibly faster. The scale factor is one number fitted on this
card; the claim is that one number suffices, not that it was predicted.

## E21 — The governor's inputs on all three machines (2026-09-22, 12:42–12:47)

**Question (Q21, Q22):** aifoundry3 never leaves 600 MHz while aifoundry2 reaches 800. Why?
**Method:** two read-only queries, added for this. `tools/etcfg` issues the driver's
`ETSOC1_IOCTL_GET_DEVICE_CONFIGURATION`; `ettelem config` asks the service processor for
`DM_CMD_GET_MODULE_STATIC_TDP_LEVEL`, `..._TEMPERATURE_THRESHOLDS` and `..._POWER_STATE`. The card's own log
buffer was then read with `ettelem sptrace`. Neither tool writes anything to a card.
**Raw data:** `docs/reports/data/2026-09-22-cards/` (`config.json`, `driver_config.json`,
`sptrace-aifoundry2.bin`, `sptrace-aifoundry3.bin`, `cards-report.json`, `cool2.log`).
**Result:** the service processor reports a static TDP of **65 W on aifoundry2 and 0 W on aifoundry3**, with
identical firmware. In `check_power_throttle_conditions()` (R3) the step-down test is
`avg_soc_pwr_mW > tdp_level_mW` and the step-up test is `<`, so at a TDP of zero the loop can only ever
throttle down. aifoundry3's own trace buffer holds 26 throttle-down events and 0 throttle-up events in one
8 KB window, each printing `tdp level: 0`. A second, independent path agrees: `get_power_state()` returns
`MAX_POWER` whenever power exceeds the TDP level, and aifoundry3 reports `max_power` at 23 W while aifoundry2
reports `managed_power`. **The driver's ioctl reports 65 W on all three machines**, so the host-visible TDP is
not the number the governor uses.
**Also established:** aifoundry1 holds two cards, both on the PCIe bus (`1e0a:eb01` at 01:00.0 and 02:00.0)
with device nodes present, but its kernel module's `srcversion` is `1383B256EB24A0A53F04CC7` against
`47D26A305A0428B29FB7FC4` on the other two, with the same `libDM.so`; the library refuses the card with
`Error unable to evaluate compatibility!` and `dev_mngt_service` is inactive. Not fixed: it is a shared
machine's kernel driver.
**Caveats:** why aifoundry3's flashed TDP is zero, and whether it was ever different, is not established.
Whether the 0 W is in flash or set at boot was not traced further than `g_pmic_power_reg.module_tdp_level`.

## E22 — Many-to-one contention on one global atomic line (2026-09-22, 13:05–13:50)

**Question (Q24):** does the shire that homes a contended atomic get less of it than the others?
**Method:** a new probe, `NB_HOTLINE` in `workloads/nocbench`. Every participating minion hammers one 4-byte
word with `amoaddg.w`; all of them meet at a chip-wide barrier first, then loop until a cycle deadline,
counting completions. A share is a shire's count over an even split. The home shire of a DRAM line is
`PA[10:6]`, so the probe allocates a 2 KB-aligned region and uses the line at offset *s*×64; scratchpad lines
use the PRM's format 0 (shire ID in bits [29:23]). Run on aifoundry2 and repeated on aifoundry3.
```
workloads/nocbench/run_hotline.sh DATA 6000000     # 42 configurations, each well under a second of card time
python3 workloads/nocbench/analyze_hotline.py DATA/sweep.jsonl --power DATA/power.json --out hotline.json
```
**Raw data:** `docs/reports/data/2026-09-22-hotline-aifoundry2/{sweep.jsonl,power.json,hotline.json}` and
`docs/reports/data/2026-09-22-hotline-aifoundry3/sweep.jsonl`.
**Result:** the atomic is **fair**. With 1,024 minions the host shire's share is 1.004 and the whole chip lies
within 0.998–1.004, standard deviation 0.001, on both cards and with the line homed in shire 0, 7, 15 or 31.
One contended line retires an atomic every **10.00 cycles** (about 60 M/s, matching the aggregate R11 quoted);
32 lines, one per shire, retire one every 0.31 cycles — 32× the work for the same instructions.
**Caveats:** with one minion per shire the bank is not saturated and shares spread 0.85–1.20, with the host
shire *highest*; that is latency, not arbitration. A global atomic addressed through the self ID `0x7F`
raises a kernel bus error, so the host shire's atomic cannot take the local path at all — which is why this
comes out fair.

## E23 — What a hot line costs the shire that hosts it (2026-09-22, 13:50–14:20)

**Question (Q24):** if the atomic is fair, what did Ivan measure?
**Method:** the same probe, with the host shire's 32 minions doing ordinary 64 B-strided loads over a private
slice of memory instead of joining the atomic, while the other shires hammer a line that lives in that shire
cache. Four combinations: the host reading its own scratchpad or DRAM, the hot line in that shire's scratchpad
or its L3 slice. The baseline is the identical loop with no other shire launched. Then two sweeps: how many
remote minions it takes, and how far they must be paced back. Power from
`tools/ettelem/run_hotline_power.sh` (three back-to-back launches per case, because the per-rail numbers are
~2 s moving averages).
**Raw data:** as E22, plus `docs/reports/data/2026-09-22-hotline-aifoundry2/{telemetry.jsonl,runs.jsonl,marks.jsonl}`.
**Result:** the host shire completes **192–384 operations and then nothing**. The count is identical for
windows of 5, 10, 40 and 100 ms while the mesh retires six million atomics, so this is a stop, not a
slow-down: 0.01–0.05% of the uncontended rate. It does not matter whether the host is reading scratchpad or
DRAM, nor where the hot line lives. **The threshold is bank saturation and it is a cliff:** 20 remote
requesters leave the host at 98.9%, 24 take it to 0.02%, and 24 is where the measured cost reaches the
bank's 10.0 cycles per atomic. One other shire is enough. Pacing the remotes to one atomic per 10,000 cycles
returns the host to 54% and costs the hammering shires 4%. Energy: 23.6 nJ per contended atomic against
1.4 nJ spread over 32 lines, a factor of **17**, while 1,024 stalled minions cost only 1.4 W over idle.
aifoundry3 reproduces every number to the individual operation.
**Mechanism, from the vendor:** Errata 4.1 (`RTLMIN-6207`) and 4.2 (`RTLMIN-6214`) in R1 describe exactly
this, rate the impact "Low" because "it would have to be a pretty consistent and repeating pattern", state
that `l3_yield_priority` does **not** fix the same-address case, and are both marked Postponed.
**Caveats:** `l3_yield` was **not** set — it is a shire-cache configuration register on a shared card and the
erratum says it would not help here. Ivan's own code was not run, so why his number was 6% rather than either
of ours is not established; the reading offered is that his shire 0 also did something local.

## E24 — Can one shire read what another wrote into its scratchpad? (2026-09-22, 15:10)

**Question (Q25):** the relay in E25 depends on a shire writing a compute result where another shire can read
it. Does that work, and by which write path?
**Method:** `workloads/onchip --test probe`. Every minion writes a 1 KB pattern that encodes its shire and
minion number into its own shire's L2 scratchpad, either with a tensor store (which bypasses the L1 and L2
caches) or with plain vector stores (which go through the L1). A second launch has every minion read and
check the block the shire one place away wrote.
**Raw data:** `docs/reports/data/2026-09-22-onchip-aifoundry2/sweep.jsonl`, group `probe`.
**Result:** both paths work. 1,024 minions wrote, 1,024 read a different shire's block, **zero wrong words**
either way. Tensor store is the one E25 uses, because it bypasses the caches and so cannot leave a stale line
for the reader within a single launch.
**Also established, the hard way:** **offset 0 of a shire's scratchpad faults.** The buffers start 256 KB in.
And `amoaddg` to a scratchpad address through the self ID `0x7F` raises a kernel bus error (E22).
**Caveats:** the two launches are separated by a kernel boundary, at which the firmware evicts the L1 and L2,
so this shows the data lands — not that a plain-store write is visible across a barrier inside one launch.
E25 relies on tensor stores for exactly that reason.

## E25 — A multi-stage relay: DRAM against the shire next door (2026-09-22, 15:30–16:40)

**Question (Q25, Q26):** is there a computation where shire-to-shire communication beats writing the
intermediate to main memory?
**Method:** `workloads/onchip --test relay`. A slab of fp32 per shire; a stage reads every element, adds 1.0
and writes it out; the next stage reads what the last wrote; a chip-wide barrier between stages. The same
kernel, the same barriers and the same arithmetic run three ways, differing only in where a stage's output
goes: `dram` (write to DRAM, read back), `scp` (the shire's own L2 scratchpad), `hop` (where the next shire
in the ring will read it). Inputs are plain vector loads, outputs are tensor stores. Sweeps over arithmetic
per element, working-set size, stages, shires and hop distance; power from
`tools/ettelem/run_onchip_power.sh`, one twelve-second burst per medium.
```
workloads/onchip/run_onchip.sh DATA                 # 88 configurations
tools/ettelem/run_onchip_power.sh DATA 12
python3 workloads/onchip/analyze_onchip.py DATA/sweep.jsonl --power DATA --out onchip.json
```
**Raw data:** `docs/reports/data/2026-09-22-onchip-aifoundry2/` (`sweep.jsonl`, `telemetry.jsonl`,
`runs.jsonl`, `marks.jsonl`, `onchip.json`) and `docs/reports/data/2026-09-22-onchip-aifoundry3/sweep.jsonl`.
**Result:** at 1 MB per shire per stage, eight stages, 512 MB of traffic: DRAM **48.4 GB/s**, the next shire's
scratchpad **592.9 GB/s (12.3×)**, the shire's own **1,483.7 GB/s (30.7×)**. Energy per byte moved: 104.8,
8.9 and 4.3 pJ — and all three draw within a watt of each other over idle, so the on-chip routes get 12× and
30× more done for the same power. aifoundry3 gives 12.4× and 31.2×.
**The boundary:** the advantage is against DRAM, not against the hierarchy. Below the 32 MB L3 the DRAM route
runs at 280–410 GB/s and the hand-off buys 1.0–1.4×; at 32 MB per buffer it falls to 47.9 GB/s and stays
there out to 256 MB. **Arithmetic:** the lead halves for every quadrupling of work, from 12.3× at one add per
element to 1.5× at 256. **Distance:** handing the slab 16 shires away is no slower than next door
(593 to 734 GB/s), so placement is free.
**How the hop is proved:** each shire starts its slab filled with its own number, and every element of every
run is checked against the value the slab must hold — for `hop`, the number of the shire `stages` places back
round the ring. Shire 0 ends holding 32 (= 24 + 8) rather than 8. A run whose data had not moved would fail.
**Caveats:** the arithmetic is one vector add, chosen to make the measurement about movement. A working set
larger than the 80 MB of scratchpad was not tried, which is the case where the hand-off would be the only
option rather than the faster one. The per-stage chip barrier is the simplest synchronisation, not the
cheapest. The `shires` sweep is confounded: fewer shires also means a smaller working set, which puts it back
inside the L3.

## E26 — The instruction and byte energy catalogue (2026-09-23, 09:40–10:05, both cards at once)

**Question (Q27):** what does each kind of instruction cost, and each byte written, at every level — the
two things no earlier session measured.
**Method:** `workloads/enercat`. Every hart of every minion runs one pattern flat out until a cycle deadline
and reports its count; 56 configurations (13 instructions × zeros / constant / random operands, the awake
core on one and two harts, L1 hits, tensor loads and stores to DRAM and to the shire's own scratchpad, the
L1 write-back path), each a 5 s burst of 0.4 s launches bracketed by 6 s of idle. Board power at 10 Hz
throughout. Energy per event = (burst power − mean of the two bracketing idles − the extra leakage of the
warmer burst) × burst time / events. The same script ran on aifoundry2 and aifoundry3 within the same hour.
```
workloads/enercat/run_enercat.sh DATA 5
python3 workloads/enercat/analyze_enercat.py DATA_A2 DATA_A3 --out enercat.json
python3 tools/ettelem/build_energy_manual.py --out manual.json     # assembles every table from its file
python3 tools/ettelem/render_energy_manual.py manual.json docs/energy-manual/
```
**Raw data:** `docs/reports/data/2026-09-23-enercat-aifoundry2/` and `-aifoundry3/` (`runs.jsonl`, one
line per launch; `telemetry.jsonl.gz`), reduced to `docs/reports/data/2026-09-23-energy-manual/enercat.json`;
every other table of the manual is assembled in `manual.json` from the files E26's builder names.
**Result (aifoundry2, 600 MHz, both harts, pJ per instruction above idle, zeros / constant / random):**
add 6.6 / 6.9 / 9.6; fadd.s 23.2 / 23.5 / 26.1; fmadd.s 27.4 / 27.2 / 31.3; fadd.ps 24.0 / 23.9 / 43.3;
fmadd.ps 27.8 / 28.3 / **59.4** (7.4 per lane); fadd.pi 13.0 / 13.3 / 20.5; fexp.ps 105 / 104 / 167. An
awake minion is 2.0 mW on one hart, 3.2 on two. **Bytes (pJ/B, zeros / random):** L1 load 0.36 / 0.54, L1
store 0.47 / 0.78, own-scratchpad tensor load 2.0 / 4.2, tensor store 4.4 / 8.0, DRAM tensor load 94 / 134,
tensor store 87 / 140, `fsw.ps` through the L1 to DRAM 247 / 345. **Cross-card:** 56 entries, aifoundry3 /
aifoundry2 median 0.949, range 0.87–1.01.
**What it establishes:** an 8-lane vector op on zeros costs what a scalar one does (idle lanes are free); a
random-data `fmadd.ps` lane costs 6.5 pJ over the awake core, against 6.0 pJ per multiply-add in the tensor
unit, so the two datapaths cost the same and the tensor unit saves only issue; a DRAM write by tensor store
costs a read, and the L1 write-back path 2.5× that; DRAM is data-dependent too (94 → 134 pJ/B).
**Caveats:** the die drifted from 74 to 87 °C over the aifoundry2 session; the leakage correction was
0.7 W in the median and 1.8 W at most, and the sensor's whole-degree steps make it ±0.3 W. `fdiv.ps` and
`fsqrt.ps` trap and are absent. Everything is at 600 MHz. The memory-hierarchy reads of 18 September, which
the manual also uses, were taken with the governor free to move the clock.

## A note on E10, re-analysed for Q20

The governor transitions in [16-dvfs-and-leakage.md](16-dvfs-and-leakage.md) are **not** a new experiment.
They are E10's telemetry re-read by `tools/ettelem/analyze_dvfs.py`, which classifies each of the 36 clock
changes against the firmware's two thresholds and the kernel boundaries. Nothing is fitted.

