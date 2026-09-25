# Experiments: the register

Every measurement in this directory has an ID here. An entry says what question it answers, exactly when and
where it ran, the command that produced it, where the **raw** data lives in this repository, and what it
cannot tell you. Cite as **E1**...**E32**.

Card work up to E19 is on **aifoundry2**, one ET-SoC-1 PCIe card; from E20 each entry names its card (aifoundry2,
aifoundry3 or both). Firmware behaviour is read from the et-platform source at `353f20e`; the cards' own trace strings
match an older build (before et-platform commit `60b40c10f`, 24 Sep 2024; both cards report release 1.3.1), so which
commit the cards run is not established (R3). Unless an entry says otherwise, the minion clock was a steady
**600 MHz** at **516–518 mV** on aifoundry2 (521–523 mV on aifoundry3), verified in every telemetry sample of the
session. Times are the lab machines' local time (UTC−7), from the first and last recorded sample.

Each entry ends with the published report it fed; [04-artifacts.md](04-artifacts.md) has every report's space and
sources. Shorthand used below: a2 and a3 are aifoundry2 and aifoundry3; `mean [lo–hi]` is a mean with the full range
over every pass on both cards.

Rebuild the Horace line (E9–E17 and the E20 transfer): every analysis, the model, the GIFs and the Horace and
why-low-power pages, with one script. Every other entry gives its own command.

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
**Caveats:** timing is load-to-use with one load in flight; the energy figures come from the rails' running
averages, read every 133 ms, not from a per-access measurement. The energy manual re-measured the levels at a pinned
600 MHz on both cards (E29); quote those.
**Report:** [Anatomy of a memory access](https://spacesheep.dev/@yaroslavvb/et-soc1-memory-anatomy) (A1).

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
**Report:** [Anatomy of a memory access](https://spacesheep.dev/@yaroslavvb/et-soc1-memory-anatomy) (A1), section 8, and [Limits of observability](https://spacesheep.dev/@yaroslavvb/et-soc1-limits-of-observability) (A2).

## E3 — Device flame graphs (2026-09-20)

**Question (Q7):** can kernel time be attributed to regions on the device?
**Tool:** `workloads/traceprof` + `scripts/trace-flamegraph.py`.
**Raw data:** `docs/reports/data/2026-09-20-traceprof-aifoundry2/`.
**Caveat:** `fcvt.s.lu` traps (cause 0x1e) on this chip, so loop counters in floating-point code must be
32-bit; profile-region strings resolve as ELF file offsets, not virtual addresses.
**Report:** [Limits of observability](https://spacesheep.dev/@yaroslavvb/et-soc1-limits-of-observability) (A2).

## E4 — A counter-select syscall, in simulation only (2026-09-20)

**Question (Q7):** could a kernel choose its own PMU events?
**Artifacts:** `patches/0003-pmc-configure-syscall-353f20e.patch`, `scripts/build-minion-fw.sh`,
`workloads/pmcsel/`.
**Status:** built and verified in `sys_emu`. **Never run on the card**, because it needs a signed firmware
image (see Q7 in [02-requests.md](02-requests.md)). Treat any claim about per-event counters on silicon as
untested.
**Report:** [Limits of observability](https://spacesheep.dev/@yaroslavvb/et-soc1-limits-of-observability) (A2).

## E5 — Load step: power, temperature and the rails (2026-09-20, 21:09–21:12)

**Question (Q8):** how do board power, the three rail sensors and the die temperature respond to a load step?
**Tool:** `tools/ettelem/run_thermal.sh`; 10 Hz sampling.
**Raw data:** `docs/reports/data/2026-09-20-power-aifoundry2/thermal-telemetry.jsonl`, `thermal-phases.jsonl`,
reduced to `summary.json` (`thermal.series`, one sample a second).
**Findings:** the rail readings lag board power (the PMIC's running average, τ ≈ 1 s: 61% of a step after 1 s and
88% after 2 s, as E27 later measured); idle power depends on recent load; under load, board power rose about
**0.8 W per °C** (a least-squares line of board power against die temperature over the matmul: 0.80 W/°C from 5 s
after launch, 0.76–0.78 from 1–3 s; 0.40 W/°C on the minion rail). That is faster than the later idle law, whose
slope is 0.56–0.78 W/°C over the step's 75–87 °C (0.67 on average). The power-and-temperature report computes this
slope from `summary.json` `thermal.series`, and also quotes E7's fit (0.78 W/°C board, 0.38 minion rail, 22
uncontrolled runs at 79–90 °C, superseded). See [14-card-behaviour.md](14-card-behaviour.md).
**Report:** [Power and temperature](https://spacesheep.dev/@yaroslavvb/et-soc1-power-temperature) (A3).

## E6 — Per-shire on-die voltage map (2026-09-20)

**Question (Q8):** how far down can voltage be resolved?
**Method:** raise the service processor's log level to DEBUG (`DM_CMD_SET_DM_TRACE_CONFIG`), extract the SP
trace, parse one record per shire per pass.
**Raw data:** `docs/reports/data/2026-09-20-power-aifoundry2/per-shire-voltage-idle.json`.
**Caveat:** restore the log level afterwards (`ettelem loglevel info`).
**Report:** [Power and temperature](https://spacesheep.dev/@yaroslavvb/et-soc1-power-temperature) (A3), section 3 (the per-shire voltage map).

## E7 — Horace experiment, first version: uncontrolled (2026-09-20, 21:14–21:19)

**Question (Q9):** does operand data change matmul power on this chip?
**Raw data:** `docs/reports/data/2026-09-20-power-aifoundry2/horace-*`.
**Caveat:** three rounds back to back with the die drifting from 79 to 90 °C, so a fitted temperature term was
needed. **Superseded by E9.** Kept because it is the only session that reached 90 °C and 70 W under the
governor without being stopped.
**Report:** [The Horace experiment](https://spacesheep.dev/@yaroslavvb/et-soc1-horace-experiment) (A4), first version (superseded).

## E8 — Horace experiment, second version: each run started at 80 °C (2026-09-20, 21:34–21:44)

**Question (Q10):** same, with the die cooled to a common temperature first.
**Raw data:** `docs/reports/data/2026-09-20-power-aifoundry2/horace2-*`.
**Result:** 20 runs, 10 patterns, all started at exactly 80 °C; rounds agree within 1.1 W.
**Superseded by E9**, which has more repeats and a de-quantised temperature.
**Report:** [The Horace experiment](https://spacesheep.dev/@yaroslavvb/et-soc1-horace-experiment) (A4), second version (superseded).

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
**Report:** [The Horace experiment](https://spacesheep.dev/@yaroslavvb/et-soc1-horace-experiment) (A4).

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
**Report:** [The Horace experiment](https://spacesheep.dev/@yaroslavvb/et-soc1-horace-experiment) (A4), section 6; [Why is the ET-SoC-1 low power?](https://spacesheep.dev/@yaroslavvb/et-soc1-why-low-power) (A5); [The ET-SoC-1's DVFS loop](https://spacesheep.dev/@yaroslavvb/et-soc1-dvfs-leakage) (A11).

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
**Report:** [The Horace experiment](https://spacesheep.dev/@yaroslavvb/et-soc1-horace-experiment) (A4).

## E12 — Long runs: minutes instead of seconds (2026-09-21, 08:56–12:59)

**Question (Q12):** how does the die behave when a workload runs for minutes?
**Command:** `tools/ettelem/run_horace_long.sh build/horace_long tools/ettelem/horace_long.sched 80 84 90 900 18000 600`
**Protocol:** strict start, then **one process** per run for up to 600 s. The runner stops a run when the
sensor reads **90 °C**, when board power reaches 73 W, or when telemetry goes stale, by touching a file the
host polls between launches (`--stop-file`). 90 °C is inside what this card had already seen (93 °C, 70 W in
E7). **29 runs in 4 hours** — after a hot run the die needs up to seven minutes to return to 80 °C.
**Raw data:** `docs/reports/data/2026-09-21-horace-aifoundry2/long/` (+ `schedule.txt`).
**Findings:** [12-heat-management.md](12-heat-management.md).
**Caveat — a real confound:** during run 27 the card's cooling changed abruptly (under an unchanged workload,
42.7 W at 84 °C falling to 35.6 W as it cooled, the die fell from 84 to 72 °C in four minutes; most likely someone changed the airflow in the lab). **All fits stop at
13,950 s.** Runs 27 and 28 are in the charts but not in any fit.
**Report:** [The Horace experiment](https://spacesheep.dev/@yaroslavvb/et-soc1-horace-experiment) (A4), section 7.

## E13 — Switching activity of structured matrices (2026-09-21)

**Question (Q15):** what do structured operands do to the flip counts?
**Tool:** `tools/ettelem/make_tiles.py` generates 17 kinds of 16×16 operand pair (Hadamard, DCT, the cos and
sin halves of a DFT, butterfly factors and their dense kaleidoscope products, identity, permutation, diagonal,
tridiagonal, block-diagonal, upper-triangular, rank-1, circulant, 4-bit quantised, weights × ReLU activations,
and a matrix of −0.0), two seeds each; E11's bench then counts their activity.
**Raw data:** `structured_tiles/*.bin`, `structured_toggles.json`.
**Note:** `make_tiles.py` normalises negative zeros to +0.0 everywhere except the deliberate `negzero` kind,
because `x · 0` leaves −0.0 for negative x and the chip only gates the all-zero bit pattern.
**Report:** [The Horace experiment](https://spacesheep.dev/@yaroslavvb/et-soc1-horace-experiment) (A4), section 9.

## E14 — Predictions recorded before the matrices ran (2026-09-21, 13:08:33)

**Question (Q15):** is the model predictive, or only descriptive?
**Method:** E13's flip counts through the model of E17, giving power and a heating curve for each of the 17
kinds. **Written to disk at 13:08:33; the first of those matrices (butterfly) launched 36 s later, at 13:09:09.**
**Raw data:** `structured_predictions_before.json` (its `made_at` field is the timestamp).
**An earlier, weaker instance of the same idea:** `predictions_before.json`, recorded at 06:50:12 on 09-21 for
six patterns first run at 06:59, from a model fitted to the 09-20 data. That set was also used to *choose*
between model forms, so it is not a clean test of the final form; E14 is.
**Report:** [The Horace experiment](https://spacesheep.dev/@yaroslavvb/et-soc1-horace-experiment) (A4), section 9.

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
**Report:** [The Horace experiment](https://spacesheep.dev/@yaroslavvb/et-soc1-horace-experiment) (A4), section 9; [Why is the ET-SoC-1 low power?](https://spacesheep.dev/@yaroslavvb/et-soc1-why-low-power) (A5).

## E16 — Long runs of structured matrices (2026-09-21, 14:16–15:08)

**Question (Q15):** does the *heating* prediction hold, not just the power?
**Command:** `tools/ettelem/run_horace_long.sh build/horace_long2 build/horace_long2.sched 80 84 90 600 3600 120`
**Raw data:** `long2/` (+ `schedule.txt`). 8 runs: ones and random normal as references, then Hadamard,
kaleidoscope, ReLU, −0.0, the DFT pair and a block-diagonal matrix.
**Why it matters for provenance:** this session happened **after** the model was fitted and the predictions
recorded, on a different afternoon, with matrices that did not exist when the model was built.
**Report:** [The Horace experiment](https://spacesheep.dev/@yaroslavvb/et-soc1-horace-experiment) (A4), section 9.

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
**Report:** [The Horace experiment](https://spacesheep.dev/@yaroslavvb/et-soc1-horace-experiment) (A4), section 8.

## E18 — Wake-up probe: is any cache array power-gated when idle? (2026-09-22, 11:39)

**Question (Q20):** R9 says cache data arrays sit behind leakage-suppression transistors and pay a small
wake-up latency on first access. Does this card show one?
**Tool:** `workloads/memprobe`, new experiment `gen_ops.py wakeup`.
**Method:** place one line at a chosen level with `evict_va`, spin the minion on its cycle counter for a swept
idle interval (0 to 16.0 M cycles, i.e. up to 26.7 ms) without touching that line, then time a single load of it.
**One line per (repeat, level)**, so only the idle time varies; 20 repeats; one hart.
**Command:**
```
python3 workloads/memprobe/gen_ops.py wakeup --out W --reps 20 --seed 11 \
    --delays 0,1000,10000,100000,1000000,4000000,8000000,16000000
build/memprobe/host/memprobe_host --program W/wakeup.ops --out-dir W --budget 40
```
**Raw data:** `docs/reports/data/2026-09-22-dvfs-aifoundry2/wakeup/` (`wakeup.ops`, `wakeup.json` labels,
`wakeup.u32` results). Card held 4.9 s.
**Result:** the median paired difference between the longest and shortest idle is 0 cycles for L1 and L3, −11 for
L2 (a slow no-idle baseline, not the idle: 61 cycles with no idle, a normal 49.5-cycle hit at every idle from 1.7 µs),
+10.5 for DRAM (row closure: an 11-cycle activate, present in full after 1.7 µs of idle and flat out to 27 ms). No
wake-up anywhere.
**Caveats:** cannot detect a penalty below about ten cycles, and cannot test idle intervals beyond 27 ms, which
is the widest the delay op encodes. The minion keeps executing throughout, so only the array under test is
idle.
**Report:** [The ET-SoC-1's DVFS loop](https://spacesheep.dev/@yaroslavvb/et-soc1-dvfs-leakage) (A11).

## E19 — Idle power after 20 hours, as an out-of-sample check (2026-09-22, 11:44)

**Question (Q20):** how much does an entirely idle card leak, is there a deep idle state, and does the leakage
curve fitted on 21 September still hold on a different day?
**Method:** no workload for about 20.6 hours: E16's last launch ended at 15:06 on 21 September (its telemetry ran
to 15:08), and the idle sample began at 11:44:19 on 22 September. The only card use in between was E18's 4.9-second
single-hart probe, five minutes before the sample. `analyze_dvfs.py --since` computes the duration from those
timestamps (`dvfs.json` `idle_check.hours_idle`). Sampled `ettelem sample --seconds 60 --every-ms 200`, with no
workload during the sample.
**Raw data:** `docs/reports/data/2026-09-22-dvfs-aifoundry2/idle_20h.jsonl.gz` (300 samples).
**Result:** 31.79 ± 0.04 W at 73.0 °C, 600 MHz, 518 mV; minion rail 11.05 W, SRAM 2.00 W, mesh 3.64 W,
15.10 W on no rail sensor. The model of E17 predicts 31.78 W — error **+0.01 W**. No sign of a deep idle
state.
**Why it counts as a test:** the model was fitted on 21 September in a cooler room, on sessions whose idle
stretches were minutes, not hours. Nothing about today's measurement was in the fit.
**Report:** [The ET-SoC-1's DVFS loop](https://spacesheep.dev/@yaroslavvb/et-soc1-dvfs-leakage) (A11).

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
random data. The aifoundry2 idle law, fitted to idle readings from 64 to 88 °C and extrapolated 7–14 °C below that
range onto this card (which idled at 50–57 °C), predicts its idle power to **+0.73 W** out of 25 W.
**Caveats:** the two sessions are at different launch temperatures, so only *switching* power (board power
minus the idle power measured just before each run) is comparable, not absolute watts. The thermal network is
not comparable at all: aifoundry3 sheds heat visibly faster. The scale factor is one number fitted on this
card; the claim is that one number suffices, not that it was predicted.
**Report:** [The Horace experiment](https://spacesheep.dev/@yaroslavvb/et-soc1-horace-experiment) (A4), section 10; [The ET-SoC-1's DVFS loop](https://spacesheep.dev/@yaroslavvb/et-soc1-dvfs-leakage) (A11), section 7.

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
**Report:** [The ET-SoC-1's DVFS loop](https://spacesheep.dev/@yaroslavvb/et-soc1-dvfs-leakage) (A11).

## E22 — Many-to-one contention on one global atomic line (2026-09-22, both cards)

**When:** the recorded sweeps ran at 13:22 on both cards.

**Question (Q24):** does the shire that homes a contended atomic get less of it than the others?
**Method:** a new probe, `NB_HOTLINE` in `workloads/nocbench`. Every participating minion hammers one 4-byte
word with `amoaddg.w`; all of them meet at a chip-wide barrier first, then loop until a cycle deadline,
counting completions. A share is a shire's count over an even split. The home shire of a DRAM line is
`PA[10:6]`, so the probe allocates a 2 KB-aligned region and uses the line at offset *s*×64; scratchpad lines
use the PRM's format 0 (shire ID in bits [29:23]). Run on aifoundry2 and repeated on aifoundry3.
```
workloads/nocbench/run_hotline.sh DATA 6000000     # 42 configurations, each well under a second of card time
python3 workloads/nocbench/analyze_hotline.py DATA/sweep.jsonl DATA3/sweep.jsonl --power DATA/power.json --out hotline.json   # DATA3: aifoundry3
```
**Raw data:** `docs/reports/data/2026-09-22-hotline-aifoundry2/{sweep.jsonl,power.json,hotline.json}` and
`docs/reports/data/2026-09-22-hotline-aifoundry3/sweep.jsonl`.
**Result:** the atomic is **fair**. With 1,024 minions the host shire's share is 1.004 and the whole chip lies
within 0.998–1.004, standard deviation 0.001, on both cards and with the line homed in shire 0, 7, 15 or 31.
One contended line retires an atomic every **10.00 cycles** (about 60 M/s, matching the aggregate R11 quoted);
32 lines, one per shire, retire one every 0.31 cycles — 32× the work for the same instructions.
**Caveats:** with one minion per shire the bank is still saturated (600,061 atomics in 6,000,000 cycles, 10.0 cycles
each), but each shire has only one request queued, so the mesh round trip decides: shares spread 0.85–1.20, falling
step by step with hop distance from the home shire, with the host shire *highest*. That is latency, not arbitration.
A global atomic addressed through the self ID `0x7F` raises a kernel bus error, so the host shire's atomic cannot
take the local path at all — which is why this comes out fair.
**Report:** [One hot line stops a shire](https://spacesheep.dev/@yaroslavvb/et-soc1-hot-line) (A13).

## E23 — What a hot line costs the shire that hosts it (2026-09-22; power on aifoundry2, sweeps on both cards)

**When:** power runs 13:16–13:17 on aifoundry2, sweeps 13:22 on both cards; all committed in `e5715db` at 13:29.

**Question (Q24):** if the atomic is fair, what did Ivan measure?
**Method:** the same probe, with the host shire's 32 minions doing ordinary 64 B-strided loads over a private
slice of memory instead of joining the atomic, while the other shires hammer a line that lives in that shire
cache. Four combinations: the host reading its own scratchpad or DRAM, the hot line in that shire's scratchpad
or its L3 slice. The baseline is the identical loop with no other shire launched. Then two sweeps: how many
remote minions it takes, and how far they must be paced back. Power from
`tools/ettelem/run_hotline_power.sh` (three back-to-back launches per case, because the per-rail numbers are the
PMIC's running averages, τ ≈ 1 s), on aifoundry2 only, reduced by
`python3 tools/ettelem/analyze_hotline_power.py DATA --out DATA/power.json` (the `--power` input of E22's command).
**Raw data:** as E22, plus `docs/reports/data/2026-09-22-hotline-aifoundry2/{telemetry.jsonl.gz,runs.jsonl,marks.jsonl}`.
The 5, 40 and 100 ms window runs behind "identical for windows of 5, 10, 40 and 100 ms" are not in these files (every
sweep row has `window_cycles` 6,000,000); their counts exist only in `hotline.json` `context.window_independence`,
which `analyze_hotline.py` does not produce.
**Result:** the host shire completes **192–384 operations and then nothing**. The count is identical for
windows of 5, 10, 40 and 100 ms while the mesh retires six million atomics, so this is a stop, not a
slow-down: 0.01–0.05% of the uncontended rate. It does not matter whether the host is reading scratchpad or
DRAM, nor where the hot line lives. **The threshold is bank saturation and it is a cliff:** 20 remote
requesters leave the host at 98.9%, 24 take it to 0.02%, and 24 is where the measured cost reaches the
bank's 10.0 cycles per atomic. One other shire is enough. Pacing the remotes to one atomic per 10,000 cycles
returns the host to 54% and costs the hammering shires 4%. Energy: 23.6 nJ per contended atomic against
1.4 nJ spread over 32 lines, a factor of **17**, while 1,024 stalled minions cost only 1.4 W over idle (first run;
re-measured in E29: 19.8 [16.9–23.6] nJ against 1.16 [1.01–1.37] nJ, still 17×). aifoundry3 repeated the sweeps,
not the power runs. The stalled host's 384 and 192 operations and the 10.0 cycles per atomic repeat exactly, and the
host's count in the other rows agrees within 2% (exactly in 13 of the 42), except one: with the host reading its
scratchpad and the hot line in its L3 slice it gets 240 operations through against aifoundry2's 208.
**Mechanism, from the vendor:** Errata 4.1 (`RTLMIN-6207`) and 4.2 (`RTLMIN-6214`) in R1 describe exactly
this, rate the impact "Low" because "it would have to be a pretty consistent and repeating pattern", state
that `l3_yield_priority` does **not** fix the same-address case, and are both marked Postponed.
**Caveats:** `l3_yield` was **not** set — it is a shire-cache configuration register on a shared card. The errata
suggest it would not fully help: 4.1 covers the same-address case, and the case measured here is different
addresses, which the yield was built for, but 4.2 says the yield has no sub-bank granularity. Untested. Ivan's own
code was not run, so why his number was 6% rather than either of ours is not established; the reading offered is
that his shire 0 also did something local.
**Report:** [One hot line stops a shire](https://spacesheep.dev/@yaroslavvb/et-soc1-hot-line) (A13).

## E24 — Can one shire read what another wrote into its scratchpad? (2026-09-22, both cards)

**When:** the first rows of E25's sweeps, about 15:52 on aifoundry2 and 15:59 on aifoundry3 (the rows carry no
timestamps).

**Question (Q25):** the relay in E25 depends on a shire writing a compute result where another shire can read
it. Does that work, and by which write path?
**Method:** `workloads/onchip --test probe`. Every minion writes a 1 KB pattern that encodes its shire and
minion number into its own shire's L2 scratchpad, either with a tensor store (which bypasses the L1 and L2
caches) or with plain vector stores (which go through the L1). A second launch has every minion read and
check the block the shire one place away wrote.
**Raw data:** `docs/reports/data/2026-09-22-onchip-aifoundry2/sweep.jsonl` and
`docs/reports/data/2026-09-22-onchip-aifoundry3/sweep.jsonl`, group `probe` (two rows on each card).
**Result:** both paths work. 1,024 minions wrote, 1,024 read a different shire's block, **zero wrong words**
either way. Tensor store is the one E25 uses, because it bypasses the caches and so cannot leave a stale line
for the reader within a single launch.
**Also established, the hard way:** **offset 0 of a shire's scratchpad faults.** The buffers start 256 KB in.
And `amoaddg` to a scratchpad address through the self ID `0x7F` raises a kernel bus error (E22).
**Caveats:** the two launches are separated by a kernel boundary, at which the firmware evicts the L1 and L2,
so this shows the data lands — not that a plain-store write is visible across a barrier inside one launch.
E25 relies on tensor stores for exactly that reason.
**Report:** [Hand it to the next shire](https://spacesheep.dev/@yaroslavvb/et-soc1-on-chip-relay) (A14).

## E25 — A multi-stage relay: DRAM against the next shire's scratchpad (2026-09-22, both cards)

**When:** aifoundry2's sweep ended at 15:52 and its power bursts ran 15:57–15:58; aifoundry3's sweep ran at 15:59;
all committed in `24fc7bf` at 16:04.

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
python3 workloads/onchip/analyze_onchip.py DATA/sweep.jsonl DATA3/sweep.jsonl --power DATA --out onchip.json   # DATA3: aifoundry3
```
**Raw data:** `docs/reports/data/2026-09-22-onchip-aifoundry2/` (`sweep.jsonl`, `telemetry.jsonl.gz`,
`runs.jsonl`, `marks.jsonl`, `onchip.json`) and `docs/reports/data/2026-09-22-onchip-aifoundry3/sweep.jsonl`.
**Result:** at 1 MB per shire per stage, eight stages, 512 MB of traffic: DRAM **48.4 GB/s**, the next shire's
scratchpad **592.9 GB/s (12.3×)**, the shire's own **1,483.7 GB/s (30.7×)**. Energy per byte moved: 104.8,
8.9 and 4.25 pJ (first run; E29 re-measured them at 105.7, 8.6 and 3.99 pJ/B) — and all three draw within a watt of
each other over idle, so the on-chip routes get 12× and 30× more done for the same power. aifoundry3 gives 12.4× and
31.2×.
**The boundary:** the advantage is against DRAM, not against the hierarchy. Below the 32 MB L3 the DRAM route
runs at 280–410 GB/s and the hand-off buys 1.0–1.4×; at 32 MB per buffer it falls to 47.9 GB/s and stays
there out to 256 MB. **Arithmetic:** the lead holds to about four adds per element and then falls faster with each
quadrupling, from 12.2× at one add per element (this sweep's own run) to 1.5× at 256, which is 32 flops per byte
moved (read plus written). **Distance:** the ring runs in shire-ID order, and the next shire by ID is 1–10 mesh hops
away (3.5 on average) while s+16 is only 2.1; across the offsets tried (1.6–4.5 hops on average) the bandwidth stays
at 593–733 GB/s and does not follow the distance. Each hop still costs energy (E31–E32), which this sweep does not
see.
**How the hop is proved:** each shire starts its slab filled with its own number, and every element of every
run is checked against the value the slab must hold — for `hop`, the number of the shire `stages` places back
round the ring. Shire 0 ends holding 32 (= 24 + 8) rather than 8. A run whose data had not moved would fail.
**Caveats:** the arithmetic is one vector add, chosen to make the measurement about movement. A working set
larger than the 80 MB of scratchpad was not tried, which is the case where the hand-off would be the only
option rather than the faster one. The per-stage chip barrier is the simplest synchronisation, not the
cheapest. The `shires` sweep is confounded: fewer shires also means a smaller working set, which puts it back
inside the L3.
**Report:** [Hand it to the next shire](https://spacesheep.dev/@yaroslavvb/et-soc1-on-chip-relay) (A14).

## E26 — The instruction and byte energy catalogue (2026-09-23, 07:48–07:59, both cards at once)

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
**Report:** [The energy manual](https://spacesheep.dev/@yaroslavvb/et-soc1-energy-manual) (A15), first edition.
E27 superseded these tables, and the published manual prints E27's values (for example `fmadd.ps` on random data
55.9 pJ, the awake core 2.14 / 3.43 mW on one and two harts); quote those.

## E27 — The comprehensive instruction and memory catalogue, three passes on two cards (2026-09-23, 08:39–11:15)

**Question (Q28, Q30):** what does every instruction cost, how repeatable is it, how much of it is the card, and
what parts of a memory access can be separated — wire, line, row, leakage, rail?
**Method:** `workloads/enercat` generated from an instruction table (`gen_ops.py`: 174 mnemonics the assembler
accepts, 161 that execute; 13 trap in U-mode). `run_catalogue.py` runs 386 configurations — every instruction on
zeros and random operands, a constant on a subset, the awake core on one and two harts, the write and read paths
with the operand pattern filled into the slices, 1 KB scratchpad reads from a shire exactly 1–8 hops away, 64 B
scratchpad reads at three strides, L1 fills at three strides, four neighbourhoods reading, and DRAM row
patterns — **three times each in a different random order per pass**, 3 s bursts bracketed by 4.5 s of idle,
telemetry at 10 Hz. The same script ran on aifoundry2 and aifoundry3 at the same time: 9,264 launches per card,
2.6 hours each. `analyze_catalogue.py` gives each configuration the mean and standard error over passes, with the
leakage correction of E26; a straight-line fit of energy per byte against hop distance; the rail split of each
burst read from its last 0.6 s and corrected for the rails' one-second filter; and the SRAM rail's idle value
against die temperature.
```
python3 workloads/enercat/run_catalogue.py DATA --passes 3 --burst 3 --gap 4.5
python3 workloads/enercat/analyze_catalogue.py DATA_A2 DATA_A3 DATA_A2_ROWS --out catalogue.json
```
**Raw data:** `docs/reports/data/2026-09-23-catalogue-aifoundry2/` and `-aifoundry3/` (`runs.jsonl`, one line per
launch with pass and configuration; `telemetry.jsonl.gz`), reduced to
`docs/reports/data/2026-09-23-energy-manual/catalogue.json` (per-burst detail and per-configuration statistics).
**Result:** all 386 configurations at 600 MHz on every sample, no failed launches. Pass-to-pass standard error
**1.9% in the median, 6.1% at the 90th percentile** on aifoundry2 (1.2% and 3.6% on
aifoundry3). Cross-card ratio **0.950** in the median, 10th–90th percentile 0.906–0.987, over
all 386 configurations. On aifoundry2 the cheapest instruction is `fence` at 4.6 pJ and the dearest `amoaddg.d` at
1,486 pJ (4.5 and 1,393 pJ pooled over both cards). **Wires:** on aifoundry2, energy per byte against hop distance is a
straight line over 1–8 hops, 3.05 pJ/B + 0.750 pJ/B per hop on zeros and 7.90 + 1.812 on random data
(rms 0.39 and 1.09 pJ/B over 7 points; aifoundry3 0.643 and 1.675 per hop); the difference of the slopes, 1.06 pJ/B
per hop (**133 fJ per bit per hop**), is what random data adds over zeros on the wires: bits that change between
flits plus ones carried (E31–E32 separate the two). The 8-hop point, which only 16 shires can reach, pulls these fits
down: over 1–6 hops the same aifoundry2 data give 0.89 and 2.29 pJ/B per hop (174 fJ per bit; aifoundry3 2.09 and
155 fJ), in line with E31–E32. The energy manual keeps the 1–8-hop fit and notes the 1–6-hop one. The mesh rail on
its own gives 1.29 pJ/B per hop over 1–8 hops (1.51 over 1–6, in line with E31–E32's 1.50 on a loaded mesh). **Lines:** a 64 B fill from the
scratchpad into the L1 is 101 pJ on zeros and 205 on random data pooled over both cards (aifoundry2 211 and
aifoundry3 199 on random data; 1.6 and 3.2 pJ/B, about three quarters of the tensor load's 2.0 and 4.2 pJ/B for the
same bytes). **Rails:** scalar and vector arithmetic put 79–82% of their power on the minion rail and
about 18% on no metered rail (regulation); an own-scratchpad read 67% on the SRAM rail; a read six hops away 49% on
the mesh rail; a DRAM read 70% on no metered rail. **SRAM leakage:** the SRAM rail at idle rises from 1.60 W at
67 °C to 2.63 W at 82 °C on aifoundry2 (78 mW/°C at 80 °C, 22 mW/MB), 1.90 W at 51 °C on aifoundry3.
**Neighbourhoods:** the four quarters of a shire read its scratchpad at 3.8–4.2 pJ/B.
**Caveats:** the die drifted between 71 and 85 °C over the aifoundry2 session and the shuffled order is what keeps
that out of the tables; the leakage correction is the E26 one. The rail split assumes the rails' filter is first-order
with τ ≈ 1 s, measured on one step. The first-pass DRAM row configurations touched too little to leave the L3 and
measured the L3 instead (kept, labelled); E28 does the rows properly.
**Report:** [The energy manual](https://spacesheep.dev/@yaroslavvb/et-soc1-energy-manual) (A15), second edition.

## E28 — DRAM row hits against row misses, done with the L3 defeated (2026-09-23, 11:18–11:21, aifoundry2)

**Question (Q30):** does opening a DRAM row cost energy a programmer can see?
**Method:** 1 KB tensor loads from DRAM by 32 harts (minion 0 of every shire), each over its own 64 MB so the
touched set exceeds the 32 MB L3 whatever the pattern: sequential (each bank sees 32 columns of a row), row hit
(stride 8 KB: same bank and row, next column), row miss (a 248 KB jump after every 8 KB: a new row on every visit
to a bank). Three passes, zeros and random, as E27.
**Raw data:** `docs/reports/data/2026-09-23-catalogue-aifoundry2-rows/`, pooled into `catalogue.json` as `dramrow2/*`.
**Result:** 147 ± 8, 156 ± 5 and 153 ± 5 pJ/B on random data for sequential, row hit and row
miss; 115, 118 and 114 on zeros. **No difference within error.** Either the controller closes pages after each
access, so every access already includes an activation, or the activation is small next to the transfer; the
instruments cannot tell which. Rails: 68–70% of a DRAM read is on no metered rail (the DDR PHY and the chips).
**Caveats:** 32 harts give 14–17 GB/s, latency-bound, so the signal is 2–2.6 W over idle and the per-pass error
±4–8 pJ/B; a 20 pJ/B activation would have shown, a 5 pJ/B one would not.
**Report:** [The energy manual](https://spacesheep.dev/@yaroslavvb/et-soc1-energy-manual) (A15), second edition.

## E29 — Confidence bars: the reruns of the relay, the hot line, the rings and the levels (2026-09-23, 12:51–13:47)

**Question (Q31):** how much does every entry move when the workload is re-run, and when the card is changed?
**Method:** the catalogue already had three shuffled passes on two cards, so its entries got a `combined`
block (`workloads/enercat/analyze_catalogue.py`): mean over every pass on every card, the range those passes
spanned, and each card's mean ± pass-to-pass standard error. The four tables that rested on one session were
re-run: the relay by medium (`tools/ettelem/run_onchip_power.sh`), the hot-line atomics
(`run_hotline_power.sh`), and the nocbench rings with the memhier levels sampled by ettelem the manual's way
(`run_rings_levels_power.sh`, new), three passes each on both cards; on aifoundry2 every pass was preceded by
heating the die past 76 °C (`run_reruns_warm.sh`, `run_rl_warm_a2.sh`). Each pass is reduced on its own with
bracketing idle and the leakage correction and pooled by `tools/ettelem/analyze_reruns.py`, which drops a burst
if the minion clock left 600 MHz in it or if the sampler's own median latency exceeded 60 ms.
**Raw data:** `docs/reports/data/2026-09-23-reruns-aifoundry2-warm/`, `-aifoundry3/`; the discarded cool-card
attempt `-aifoundry2/`; pooled into `docs/reports/data/2026-09-23-energy-manual/reruns.json`.
**Result:** the catalogue's bars are ±5.6% in the median and ±11.5% at the 90th percentile (half the range), mostly
the 5% between the cards. The re-run tables, with `mean [lo–hi]` over every pass on both cards and each card's mean ±
pass-to-pass standard error. The rings are those of the energy manual §5: *pair* is messages between the two minions
of a pair in a neighbourhood, *shire* a ring of all 32 minions of a shire, *xshire1* each minion to the same minion of
the next shire ID (not necessarily a mesh neighbour).

| Entry | mean [lo–hi] | aifoundry2 | aifoundry3 | n |
|---|---|---|---|---|
| Relay through DRAM, pJ/B | **105.7** [99.5–111.0] | 102.1 ± 1.3 | 109.3 ± 1.5 | 8 |
| Relay to the next shire, pJ/B | **8.6** [7.8–9.2] | 9.1 ± 0.1 | 8.1 ± 0.1 | 8 |
| Relay in the own scratchpad, pJ/B | **3.99** [3.90–4.25] | 4.02 ± 0.08 | 3.97 ± 0.01 | 8 |
| Hot line, contended, nJ per atomic | **19.8** [16.9–23.6] | 20.8 ± 1.0 | 18.6 ± 1.1 | 7 |
| Hot line, spread over 32 lines, nJ per atomic | **1.16** [1.01–1.37] | 1.21 ± 0.08 | 1.09 ± 0.05 | 7 |
| L1, pJ/B | **0.77** [0.66–0.88] | 0.86 ± 0.01 | 0.68 ± 0.01 | 6 |
| L2, pJ/B | **2.51** [2.36–2.64] | 2.61 ± 0.02 | 2.40 ± 0.02 | 6 |
| L3, pJ/B | **10.5** [9.6–11.4] | 10.7 ± 0.3 | 10.3 ± 0.6 | 6 |
| DRAM, pJ/B | **122** [117–129] | 123 ± 4 | 121 ± 2 | 6 |
| Own scratchpad, pJ/B | **2.52** [2.39–2.64] | 2.40 ± 0.00 | 2.63 ± 0.01 | 6 |
| Remote scratchpad, pJ/B | **6.65** [5.31–7.48] | 6.17 ± 0.43 | 7.14 ± 0.27 | 6 |
| Ring, pair, pJ/B | **0.67** [0.61–0.73] | 0.63 ± 0.02 | 0.70 ± 0.02 | 6 |
| Ring, shire, pJ/B | **2.08** [1.93–2.16] | 2.05 ± 0.06 | 2.12 ± 0.03 | 6 |
| Ring, xshire1, pJ/B | **14.9** [14.2–15.4] | 15.4 ± 0.0 | 14.4 ± 0.1 | 6 |

**Three things the reruns taught:** (1) the first attempt (12:51–13:10, aifoundry2 at 65 °C) had the governor at
700–800 MHz inside 5–25% of the samples of most bursts and was discarded — bars must not hold a change of
operating point; (2) `run_energy.py`'s polling without the die temperature reads 10–50% high on 2 W signals on
a cooling card, so the rings and levels were re-sampled by ettelem and the 18 September runs are no longer
pooled; (3) rings between shires s and s+16 starve the service processor's own management path (sample latency,
six management commands, 22 → 150 ms; the board reading held for seconds) on aifoundry2, so that row is aifoundry3
only.
**Caveats:** the sampler failed to start in about one pass in three before the runners learnt to retry;
aifoundry3's hot-line pass 3 was cut short when the driver script was overwritten while running. Only
complete passes with telemetry are pooled.
**Report:** [The energy manual](https://spacesheep.dev/@yaroslavvb/et-soc1-energy-manual) (A15), third edition.

## E30 — The unmetered remainder attributed, and the DDR rail's droop as a DRAM-power meter (2026-09-23, analysis of E27 and E28)

**Question (Q32):** can anything reduce the share of power that is on no rail sensor?
**Method:** no new card time. The firmware's PMIC and PVT drivers were read for what the meters are
(`ServiceProcessorBL2/driver/pmic_controller.c`, `pvt_controller.c`, `services/thermal_pwr_mgmt.c`): the PMIC holds
PMBus statistics for three regulators only (minion, NoC, SRAM: v/a/w in and out, temperature; current, min, max,
average), the SP forwards the output-side power of each, and the other rails have set points and no telemetry. Then
E27's and E28's configurations were fitted, one mean per configuration: unmetered W = a·minion + b·SRAM + c·NoC +
d·(DRAM bytes/s), no intercept, per card; and `die_mv.ddr` (the memory shires' Moortec voltage monitor of the 0.8 V
DDR rail, in every ettelem sample) was regressed, with no intercept, on the off-rail DRAM watts and the rest of the
board's power over idle.
**Raw data:** `docs/reports/data/2026-09-23-catalogue-aifoundry2/`, `-aifoundry3/` and `-aifoundry2-rows/`
(`telemetry.jsonl.gz`), and `catalogue.json` (392 configurations on aifoundry2 including E28's rows, 386 on
aifoundry3); result in `docs/reports/data/2026-09-23-energy-manual/unmetered_fit.json`.
**Command:** the fit was first computed inline in the session, and `unmetered_fit.json` keeps those numbers. It was
later committed as a script, which recomputes both fits from the files above and compares them with that file:
```
python3 tools/ettelem/fit_unmetered.py        # add --out FIT.json to write the fit
```
It reproduces the attribution exactly (coefficients, standard errors, rms and n on both cards) and the droop
coefficient to within 3% (0.87 against 0.84 mV per off-rail DRAM watt; rms 0.37 against 0.36 mV). The inline run's
busy and idle windows for the droop were not recorded, so the script's own choice of windows accounts for the rest;
the droop fit uses only the aifoundry2 catalogue telemetry (n = 386). The script will not replace
`unmetered_fit.json` unless `--overwrite` is also given.
**Result:** aifoundry2: 0.196 ± 0.003 per minion-rail W, 0.050 ± 0.017 per SRAM W, 0.286 ± 0.021 per NoC W, 72.9 ±
1.6 pJ per DRAM byte, rms 0.35 W over 392 configuration means (1.1 W on the 17 DRAM configurations); aifoundry3:
0.177, 0.064, 0.264, 68.1 pJ/B, rms 0.30 W over 386 (1.3 W on its 11 DRAM configurations). So an instruction's
unmetered energy is the minion regulator's delivery loss (18–20%), a DRAM byte's is about 70 pJ in the PHY, the I/O
rail and the chips (twice that per useful byte through the L1 write-back path, which reads the line first), and the
NoC coefficient is too large for a regulator alone: the memory shires' logic, on an unmetered rail, works when the
mesh moves bytes to them. **The DDR rail droops 0.84 mV per off-rail DRAM watt** (0.025 mV per watt of anything
else, rms 0.36 mV over 386 configurations; 767 mV at idle against an 800 mV set point): 1 mV ≈ 1.2 W of DRAM,
refreshed every 133 ms, a meter for the largest unmetered consumer that was in every telemetry file all along. It
responds mostly to DRAM traffic, not only: heavy mesh and scratchpad traffic with no DRAM access droops it by 1–1.7
mV, which it would read as 0.8–1.8 W of DRAM, and its idle reading moves by about 1 mV between 71 and 77 °C. The
minion rail sags 0.068 mV per watt the cores draw.
**What it does not do:** none of the Moortec sensors measures current, so none meters the DDR, VDDQ, PCIe, IO or
Maxion rails; the droop is a calibrated proxy, not independent of the board meter; the idle 12–15 W stays unsplit,
and the fit's rms says nothing about it. The observability report's improvement ladder (A2, second edition) ranks
what would meter more.
**Caveats:** the fit's SRAM and NoC coefficients are collinear with the minion one in many configurations (their
standard errors say so); the droop of other rails leaks into the DDR monitor at 0.025 mV per board watt.
**Report:** [The energy manual](https://spacesheep.dev/@yaroslavvb/et-soc1-energy-manual) (A15), section 4.3 (`docs/energy-manual/04a-fine-grain.md`); [Limits of observability](https://spacesheep.dev/@yaroslavvb/et-soc1-limits-of-observability) (A2), section 4.

## E31 — Heat per millimetre, first run: hop distance against the bits on the links (2026-09-24, 13:23–14:16, both cards at once)

**Question (Q41):** what does moving a bit one millimetre across the mesh cost, and does it depend on transitions
or on the bits themselves?
**Method:** `workloads/enercat/run_wire.py <out> --set v1 --passes 3` on each card, 82 configurations × 3 passes in
a different shuffled order each pass, 3 s bursts bracketed by idle, `ettelem` at 10 Hz. Hart 0 of every minion
streams 1 KB tensor loads (two in flight) from the scratchpad of a shire exactly *d* hops away (*d* = 0, 1, 2, 3, 4,
6; at most two readers per target). Before each configuration every scratchpad is filled by
`--pattern tstore_raw`, which stores the host's bytes exactly (checked with `--dump-slice`): `bern:P` (each bit 1
with probability *P* ∈ {0, 0.1, 0.25, 0.5, 0.75, 0.9, 1}), `alt:N` (N-byte blocks alternately 0x00 and 0xFF, N = 16
to 256, at *d* = 0, 1, 3, 6), single-axis pairs (`--hop-axis x|y`, *d* = 1–4, *P* = 0 and ½) and E27's 'random'
image. Prefill and heater windows are logged in `marks.jsonl` and kept out of the idle brackets; on aifoundry2 a
heater was ready for a die below 69 °C and never ran. Reduced by `workloads/enercat/analyze_wire.py`: board power
over bracketing idle with the leakage correction, the mesh rail over the burst's last 0.6 s; bursts dropped if the
clock left 600 MHz or the sampler's median latency exceeded 60 ms; slopes per pass and card against *d*; the model
slope = s0 + a·2P(1−P) + b·P.
**Raw data:** `docs/reports/data/2026-09-24-wire-aifoundry2/`, `-aifoundry3/` (`telemetry.jsonl.gz`,
`runs.jsonl.gz` with every launch's reader>target map, `marks.jsonl`, `run.log`, the driver's error counters
before the run); analysis `docs/reports/data/2026-09-24-wire-energy/wire.json` (`model.v1`, `patterns`, `axes`,
`checks`).
**Result:** on the mesh rail a = 95 fJ per bit that differs from the previous flit, per hop; b = 131 per one
carried; s0 = 74 per bit whatever the data (on board power: a = 139, b = 197, s0 = 103). A random bit's data-dependent part is 113 fJ per
hop on the rail, 188 fJ with s0 (board: 168 and 271). Blocks of 16–128 B
cost the same and 256 B blocks 0.41 pJ/B per hop more on the rail (0.76 on board), consistent with four lanes
chosen by PA[7:6] and a flit of at least a 64 B line. x-only and y-only pairs agree to about 10%.
**Caveats:** the image repeats every 512 B and two readers of a target read the same bytes, so consecutive flits can
be exact copies and the difference rate is below 2P(1−P) by an unknown factor (E32 removes this); link sharing grows
with *d* (0% at one hop, 72% at six). On aifoundry2 the y-only pairs three hops apart starved the service
processor (telemetry reads of 0.8–1.6 s instead of 22 ms): all six such bursts are dropped, and the only y-only
three-hop point is aifoundry3's. The driver's error counters were the same before and after on both cards.
**Report:** [Heat per millimetre](https://spacesheep.dev/@yaroslavvb/et-soc1-heat-per-mm) (A17).

## E32 — Heat per millimetre, second run: unique lines and link-disjoint flows (2026-09-24, 14:30–14:59)

**Question (Q41):** the same, with the confounds of E31 removed, and what sharing a link costs.
**Method:** `run_wire.py --set v2`, chained after E31 by `tools/ettelem/chain_wire_v2.sh`, 44 configurations × 3
passes. `--pattern tstore_uniq` fills every 512 B block from its own random bytes (`uq:P`, *P* ∈ {0, ¼, ½, ¾, 1},
¾ the exact complement of ¼), and the two readers of a target read different regions (`--uniq-regions`);
`wsep/p{0,0.5}/hop{1..5}`: straight pairs chosen so that no two flows share a directed link and every target has
one reader (`--pairs`); `wfrz/hop{0,1,3,6}`: one random 64 B line everywhere (244 of 512 bits ones, no two flits
differ). Reduced as E31; the free-link numbers are fitted over *d* = 1–4, the same distances as the loaded set.
**Raw data:** `docs/reports/data/2026-09-24-wire2-aifoundry2/`, `-aifoundry3/`; analysis in the same `wire.json`
(`model.v2`, `disjoint_flows`, `complement_test`, `checks`, `sensitivity`), assembled with the literature and die
geometry by `tools/ettelem/build_wire_report.py` into `report.json`.
**Result:** a = 98 [92–103] and b = 129 [127–133] fJ per hop on the mesh rail, 151 and 192 on board power, rms 0.008
and 0.038 pJ/B per hop; the complement test gives 132 [125–138] fJ per one; the frozen line sits on the model. Per mm
(3.72 mm per hop): free links 24.6 + 11.7 = **36.2 fJ per random bit·mm** on the mesh rail and 32.7 + 14.0 = 46.7 on
board power; loaded mesh 30.6 + 19.8 = **50.4** and 46.1 + 26.8 = 72.9. Over the same one to four hops the loaded
mesh costs 119 against 91 fJ per bit per hop (data) and 76 against 43 (the rest) on the rail, with per-reader
bandwidth within 6%. Without the leakage correction the board coefficients are 4–9% higher; the rail's do not move.
**What went wrong first:** the first start failed on both cards. E31's samplers had been killed mid-request, and the
reply left in the management queue crashed every later opener with `std::bad_function_call`. One
`dev_mngt_service -m DM_CMD_GET_MODULE_POWER` call drained it; `ettelem sample` now exits cleanly on SIGTERM, and
the runners drain and retry on a failed start and restart a sampler that stalls. The restarted run completed 132
bursts per card with no sampler restart.
**Review:** before publication a workflow of six AI agents re-derived every number (two independent reductions,
three skeptics and a synthesis; `docs/reports/data/2026-09-24-wire-energy/review/`). The measurements reproduced within 1–3% on the rail and about 7%
on board power; its corrections to the interpretation are in the report and in
[20-heat-per-mm.md](20-heat-per-mm.md).
**Report:** [Heat per millimetre](https://spacesheep.dev/@yaroslavvb/et-soc1-heat-per-mm) (A17).

## A note on E10, re-analysed for Q20

The governor transitions in [16-dvfs-and-leakage.md](16-dvfs-and-leakage.md) are **not** a new experiment.
They are E10's telemetry re-read by `tools/ettelem/analyze_dvfs.py`, which classifies each of the 36 clock
changes against the firmware's two thresholds; the seven down-steps that neither threshold explains on the sampled
values are labelled unattributed. Nothing is fitted.

