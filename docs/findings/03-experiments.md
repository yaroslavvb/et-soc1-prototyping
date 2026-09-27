# Experiments: the register

Every measurement in this directory has an ID here. An entry says what question it answers, exactly when and where it
ran, the command that produced it, where the **raw** data lives in this repository, and what it cannot tell you. Cite
as **E1**...**E49**. E33 and E34 are the 18 September memory-hierarchy and on-chip communication sessions,
registered on 25 September; they are numbered last so that no other number moves. E35–E47 are version 3 of the claims
check (25–26 September, three cards; E47 was registered and not run), E48 the gathers and scatters run on the
same three cards after each card's campaign blocks (26 September), and E49 a card-free test of the runtime's log-level race.

Card work up to E19, and E33–E34, is on **aifoundry2**, one ET-SoC-1 PCIe card; from E20 each entry names its card
(aifoundry2, aifoundry3 or both; E35–E46 and E48 also aifoundry1's card 1). Firmware behaviour is read from the et-platform
source at `353f20e`; the cards' own trace strings match an older build (before et-platform commit `60b40c10f`, 24 Sep
2024; both cards report release 1.3.1), so which commit the cards run is not established (R3). Unless an entry says
otherwise, the minion clock was a steady **600 MHz** at **516–518 mV** on aifoundry2 (521–523 mV on aifoundry3),
verified in every telemetry sample of the session. Times are the lab machines' local time (UTC−7), from the first and
last recorded sample.

Each entry ends with the published report it fed; [04-artifacts.md](04-artifacts.md) has every report's space and
sources. Shorthand used below: a2 and a3 are aifoundry2 and aifoundry3, a1c1 is aifoundry1's card 1; `mean [lo–hi]` is
a mean with the full range over every pass on both cards (in E35–E46, a mean with its 99% interval).

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
**Tool:** `workloads/memprobe` (device kernel with an op-program interpreter, host, `gen_ops.py`, `run_power.py`,
`analyze_power.py`, `analyze.py`, `build_report.py`).
**Raw data:** `docs/reports/data/2026-09-19-memprobe-aifoundry2/`. The rail trace is kept as `power/sp_stats.csv`
(the merged trace `analyze_power.py --csv` writes), not as the service processor's `.bin` dumps.
**Rebuild from the committed data** (no card):
```
D=docs/reports/data/2026-09-19-memprobe-aifoundry2
python3 workloads/memprobe/analyze_power.py $D/power --json $D/power/summary.json   # reads power/sp_stats.csv
python3 workloads/memprobe/analyze.py --data $D --out $D/summary.json
python3 workloads/memprobe/build_report.py $D/summary.json docs/reports/data/2026-09-23-energy-manual/manual.json \
    docs/reports/2026-09-19-et-soc1-memory-anatomy.html
```
**Method:** `evict_va` (CSR 0x89f) places a line at a chosen level, then one timed load; 1,500 addresses for
the L3 map, 19,000 loads at random phases for refresh; energy from the service processor's per-rail stats
trace during strided loops sized to each level. `l3map.u32` holds 8,192 consecutive lines as L3 hits, a larger
check of the L3 model (8,124 within ±4 cycles of 110 + 12·hops, 60 more 5–6 cycles above it, 8 counter glitches);
the page does not use it.
**Findings:** [15-earlier-findings.md](15-earlier-findings.md).
**Caveats:** timing is load-to-use with one load in flight; the energy figures come from the rails' running
averages, copied once per service-processor pass (133 ms on aifoundry2 with nothing polling, 156 ms under ettelem at
10 Hz: E41), not from a per-access measurement. The energy manual re-measured the levels at a pinned
600 MHz on both cards (E29); quote those.
**Report:** [Anatomy of a memory access](https://spacesheep.dev/@yaroslavvb/et-soc1-memory-anatomy) (A1).

## E2 — The `hpmcounter3` carry bug, reproduced in RTL (2026-09-20)

**Question (Q4, Q6):** why does the cycle counter read 128 short?
**Tool:** `rtl-sim/pmu_carry/` (Verilator 5.042 in `~/.local/verilator`, testbench `tb.sv` driving R2's
`shire/neigh/neigh_pmu.v` unmodified).
**Method:** assert count-up on counter 0 every cycle, read it every cycle, print every step that is not 1.
**Finding:** each counter is a 7-bit pre-counter plus a 57-bit post-counter; twelve counters share **one**
adder that folds pre-counter overflows into the post-counters round-robin, and a read ignores the pending
overflow bit. So after every wrap the value is 128 short until the adder comes round: a 12-cycle window in
simulation; on the card it covered at least 0–10 in one launch and 0–9 in the other (19 September), and in E35 no
single window fitted every pair in most launches on any of three cards (MEM-R1). `fixcyc()` in `workloads/memprobe/kernel/memprobe.c` corrects it.
**Caveat:** the Erbium RTL is a later revision than the taped-out silicon; the cycle counts differ by one.
**Report:** [Anatomy of a memory access](https://spacesheep.dev/@yaroslavvb/et-soc1-memory-anatomy) (A1), section 8, and [Limits of observability](https://spacesheep.dev/@yaroslavvb/et-soc1-limits-of-observability) (A2).

## E3 — Device flame graphs (2026-09-20)

**Question (Q7):** can kernel time be attributed to regions on the device?
**Tool:** `workloads/traceprof` + `scripts/trace-flamegraph.py`.
**Command** (from `build/traceprof-data`, after building `workloads/traceprof`):
```
timeout 10 ../traceprof/host/traceprof_host --shires 0x1 --reps 4 --out events.jsonl
python3 ../../scripts/trace-flamegraph.py events.jsonl --svg flame.svg --folded flame.folded \
    --title "traceprof on aifoundry2: 32 harts of shire 0, cycles"
```
**Raw data:** `docs/reports/data/2026-09-20-traceprof-aifoundry2/`: 512 events from 32 harts, spanning 1,572,824
cycles (2.6 ms at 600 MHz) of kernel time. The second command, run on the committed `events.jsonl`, reproduces
`flame.svg` and `flame.folded` byte for byte.
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
**Raw data:** `docs/reports/data/2026-09-20-power-aifoundry2/thermal-telemetry.jsonl`, `thermal-phases.jsonl`, and
`raw/thermal-loads.log` (recovered on 25 September from aifoundry2's build tree: one line per load process, 8
`MMBENCH` and 4 `MEMPROBE`, which `run_thermal.sh` cut at 200 and 160 characters, so the per-launch times are not in
it). Reduced to `summary.json` (`thermal.series`, one sample a second; `thermal.gaps`, the dips between load
processes, from the 10 Hz stream; `thermal.loads`) by
```
python3 tools/ettelem/summarize_power_session.py docs/reports/data/2026-09-20-power-aifoundry2 \
    --out docs/reports/data/2026-09-20-power-aifoundry2/summary.json
```
which reproduces the committed series exactly.
**Findings:** the rail readings lag board power (the PMIC's running average: E27's catalogue later measured a step
at 55–57% after 1 s and 83–84% after 2 s, τ ≈ 1.15–1.22 s, `catalogue.json` `rail_filter`); idle power depends on
recent load; under load, board power rose about **0.8 W per °C** (a least-squares line of board power against die
temperature over the matmul: 0.76, 0.80, 0.82 and 0.89 W/°C for fits starting 1, 5, 10 and 20 s after launch; 0.77,
0.79, 0.80 and 0.84 without the seconds that hold a launch gap; 0.40 W/°C on the minion rail). A least-squares line
through the later idle law over the seconds of the 5 s fit gives 0.69 W/°C (the law's own slope runs from 0.56 to
0.78 W/°C over the step's 75–87 °C). The DRAM-bound load moves the minion rail by only 0.4 W, with the die 1 °C warmer. The DDR
domain's on-die reading falls about 0.2 mV per °C at idle (768 mV at 72 °C, 766 mV at 81 °C); the DRAM load reads
3 mV below that trend at 82 °C, and the matmul's 765 mV at 84–87 °C is what the trend predicts. The
power-and-temperature report computes all of these from `summary.json`, and also quotes E7's fit (0.78 W/°C board,
0.38 minion rail, 22 run averages from 30 uncontrolled runs at 79–90 °C, superseded). See
[14-card-behaviour.md](14-card-behaviour.md).
**Report:** [Power and temperature](https://spacesheep.dev/@yaroslavvb/et-soc1-power-temperature) (A3).

## E6 — Per-shire on-die voltage map (2026-09-20)

**Question (Q8):** how far down can voltage be resolved?
**Method:** raise the service processor's log level to DEBUG (`DM_CMD_SET_DM_TRACE_CONFIG`), extract the SP
trace, parse one record per shire per pass.
**Raw data:** `docs/reports/data/2026-09-20-power-aifoundry2/per-shire-voltage-idle.json`, and the SP trace dumps it
came from, recovered on 25 September from aifoundry2's build tree: `raw/sp1.bin`, `sp2.bin`, `sp3.bin` (checksums in
`raw/README.md`).
```
python3 tools/ettelem/parse_sptrace_voltage.py docs/reports/data/2026-09-20-power-aifoundry2/raw/sp1.bin \
    > per-shire-voltage-idle.json
```
reproduces the committed map byte for byte; `sp2.bin` and `sp3.bin` hold later passes, 0.3 s apart, whose current
readings differ from it in 6 and 7 of the 102 cells, by 1 mV, with every low and high the same (`summary.json`
`voltage_repeat`).
**Caveat:** restore the log level afterwards (`ettelem loglevel info`).
**Report:** [Power and temperature](https://spacesheep.dev/@yaroslavvb/et-soc1-power-temperature) (A3), section 3 (the per-shire voltage map).

## E7 — Horace experiment, first version: uncontrolled (2026-09-20, 21:14–21:19)

**Question (Q9):** does operand data change matmul power on this chip?
**Raw data:** `docs/reports/data/2026-09-20-power-aifoundry2/horace-*`.
**Caveat:** three rounds back to back with the die drifting from 79 to 90 °C, so a fitted temperature term was
needed. Round 2 (the third; rounds count from 0) was degenerate: `run_horace.sh` rotated the patterns with the
multiplier 2·round + 1, which is 5 in round 2, so that round alternated onebit and ones five times each, and `summary.json` keeps 22 run averages from the
30 runs (`run_horace.sh` now uses the multipliers 1, 3, 7, 9, all coprime to 10). The committed
`horace-telemetry.jsonl` is thinned to 2 Hz by `compact_telemetry.py`, while the rows (30 samples each) were computed
at 10 Hz, so they can be approximated from the repository but not reproduced exactly. **Superseded by E9.** Kept
because it is the only session that reached 90 °C and 70 W under the governor without being stopped.
**Report:** [The Horace experiment](https://spacesheep.dev/@yaroslavvb/et-soc1-horace-experiment) (A4), first version (superseded).

## E8 — Horace experiment, second version: each run started at 80 °C (2026-09-20, 21:34–21:44)

**Question (Q10):** same, with the die cooled to a common temperature first.
**Raw data:** `docs/reports/data/2026-09-20-power-aifoundry2/horace2-*`.
**Result:** 20 runs, 10 patterns, all started at exactly 80 °C; rounds agree within 1.1 W.
**Caveat:** as in E7, the committed `horace2-telemetry.jsonl` is thinned to 2 Hz while the rows were computed at 10 Hz.
**Superseded by E9**, which has more repeats and a de-quantised temperature.
**Report:** [The Horace experiment](https://spacesheep.dev/@yaroslavvb/et-soc1-horace-experiment) (A4), second version (superseded).

## E9 — Horace experiment, third version: strict, 14 patterns (2026-09-21, 06:55–07:52)

**Question (Q11):** the definitive data-dependent power measurement.
**Command** (the two builds, on the lab machine, serve every Horace session E9–E20):
```
cmake -S workloads/sparsity -B build/sparsity -DCMAKE_PREFIX_PATH=/opt/et -Wno-dev && cmake --build build/sparsity -j4
cmake -S tools/ettelem -B build/ettelem -DCMAKE_PREFIX_PATH=/opt/et -Wno-dev && cmake --build build/ettelem
tools/ettelem/run_horace_strict.sh build/horace3 80 84 4 5 2 7 \
  "zeros ones pi sparse50 uniform randn" \
  "signs pow2 mant a_randn_b_ones a_ones_b_randn ternary sparse75 checker"
```
Then, off the card (`tools/ettelem/finish_horace.sh` runs the last two from the committed data; the RTL replay of
E11 is skipped while `toggles.json` exists):
```
python3 tools/ettelem/analyze_horace_strict.py build/horace3 --toggles toggles.json --out horace3.json
python3 tools/ettelem/make_heating_gif.py horace3.json horace-heating.gif --poster horace-heating.png --steps
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
**Command:** `python3 tools/ettelem/make_tiles.py --all build/structured_tiles` (then E11's bench on those tiles;
`finish_horace.sh` runs it when `structured_toggles.json` is missing).
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
recorded, in a separate session that afternoon, with matrices that did not exist when the model was built.
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
`wakeup.u32` results). Card held 4.9 s. Reduced by `tools/ettelem/analyze_dvfs.py --wakeup` (the full command is
under E19). Since 25 September it uses the stored latencies as they are: `memprobe.c` already corrects the cycle
counter's late carry, and the analysis had corrected 7 of the 800 loads a second time.
**Result:** the median paired difference between the longest and shortest idle is 0 cycles for L1 and L3, −11 for
L2 (a slow no-idle baseline, not the idle: 61 cycles with no idle, a normal 49.5-cycle hit at every idle from 1.7 µs),
+10.5 for DRAM (row closure: an 11-cycle activate, present in full after 1.7 µs of idle and flat out to 27 ms; of
the 20 paired DRAM differences at 27 ms, 13 are +9 to +14 cycles, six are within 6 cycles of zero and one is an
outlier, −51). No wake-up anywhere.
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
**Command** (the DVFS report's data and page, from the repo root; no card). The three steps go together: the second
adds the three-machine block (`cards`) that the page's sections 3 and 6 need, `analyze_dvfs.py` keeps an existing
`cards` block when it rewrites the file, and `build-report.py` refuses to build the page without one.
```
D=docs/reports/data; H=$D/2026-09-21-horace-aifoundry2; A3=$D/2026-09-22-horace-aifoundry3; C=$D/2026-09-22-cards
python3 tools/ettelem/analyze_dvfs.py --cold $H/cold1 $H/cold2 --wakeup $D/2026-09-22-dvfs-aifoundry2/wakeup \
    --idle $D/2026-09-22-dvfs-aifoundry2/idle_20h.jsonl.gz --since $H/long2/runs.jsonl.gz \
    --model $H/model.json --ablation $H/ablation.json --sptrace $C/sptrace-aifoundry3.bin \
    --out $D/2026-09-22-dvfs-aifoundry2/dvfs.json
python3 tools/ettelem/build_cards_data.py --cards $A3/cards.json --transfer $A3/transfer.json \
    --leak $A3/leakage_crosscard.json --config $C/config.json --driver $C/driver_config.json \
    --sptrace $C/sptrace-aifoundry3.bin --out $C/cards-report.json \
    --merge $D/2026-09-22-dvfs-aifoundry2/dvfs.json
python3 scripts/build-report.py dvfs-leakage $D/2026-09-22-dvfs-aifoundry2/dvfs.json docs/reports/2026-09-22-dvfs-leakage.html
```
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
```
Then, from the repo root with no card (`tools/ettelem/finish_horace.sh` runs all four):
```
D=docs/reports/data/2026-09-21-horace-aifoundry2; A3=docs/reports/data/2026-09-22-horace-aifoundry3
python3 tools/ettelem/analyze_horace_strict.py $A3 --toggles $D/toggles.json --out $A3/horace3.json
python3 tools/ettelem/compare_cards.py --card aifoundry2=$D/horace3.json --card aifoundry3=$A3/horace3.json \
    --model $D/model.json --toggles $D/toggles.json --out $A3/cards.json
python3 tools/ettelem/transfer_cards.py --cards $A3/cards.json --session $A3 --model $D/model.json \
    --transfer $A3/transfer.json --leak $A3/leakage_crosscard.json
python3 tools/ettelem/build_cards_data.py ...   # the three-machine block, merged into both reports' data (E19's command)
```
`transfer_cards.py` (added 25 September) reproduces the committed `transfer.json` and `leakage_crosscard.json` byte for
byte in their first-published fields, which until then no committed script produced, and adds `worst_rms`,
`worst_single`, `mean_offset_W_by_sample` and a `model_rule` block.
**Raw data:** `docs/reports/data/2026-09-22-horace-aifoundry3/` (`runs.jsonl`, `starts.jsonl`,
`telemetry.jsonl.gz`, `tiles/`, and the derived `horace3.json`, `cards.json`, `transfer.json`,
`leakage_crosscard.json`).
**Result:** the same ordering and nearly the same magnitudes as E9 — zeros 1.89 W over idle against 1.96,
random normal 24.86 against 27.11. The aifoundry2 model applied unchanged is off by 1.38 W rms, and it overestimates
every pattern, by 3 to 10% (8% by least squares); after one scale factor of **0.924** the residual is **0.20 W rms**
over a 1.9–25 W range. Calibrating that factor on one operand pattern's runs and predicting the other seven patterns
gives 0.36 W rms in the median and 0.93 W rms at worst (calibrated on zeros; the largest single error is 1.53 W),
and 0.27 W rms calibrated on random normal. The aifoundry2 idle law, fitted to idle readings from 64 to 88 °C and
extrapolated 7–14 °C below that range onto this card (which idled at 50–57 °C), predicts its idle power to
**+0.73 W** out of 25 W, the mean of the four temperature bins (the 50 °C bin is 22 samples of pre-session idle;
+0.68 W weighted by samples; with the model's own idle rule, +0.69 W over 55–57 °C).
**Caveats:** the two sessions are at different launch temperatures, so only *switching* power (board power
minus the idle power measured just before each run) is comparable, not absolute watts. The thermal network is
aifoundry2's alone: this session did not measure aifoundry3's cooling over minutes, so whether the network transfers
was not tested. The scale factor is one number fitted on this
card; the claim is that one number suffices, not that it was predicted.
**Report:** [The Horace experiment](https://spacesheep.dev/@yaroslavvb/et-soc1-horace-experiment) (A4), section 10; [The ET-SoC-1's DVFS loop](https://spacesheep.dev/@yaroslavvb/et-soc1-dvfs-leakage) (A11), section 6.

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
**Corrections (2026-09-25):** the `srcversion` difference was not the cause. The module had an empty version
string (a Makefile typo in its DKMS source), which the device layer's driver check reads; rebuilding the module
from the fixed source brought both cards back on 25 September. And aifoundry3's zero TDP is not flashed: a boot
service (`et-board-clock-guard.service`) sets it, with the 600/400 MHz clocks, at every boot. Both are in
[14-card-behaviour.md](14-card-behaviour.md).
**Caveats:** none left open from the two questions above.
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
python3 workloads/nocbench/analyze_hotline.py DATA/sweep.jsonl DATA3/sweep.jsonl --power DATA/power.json \
    --context DATA/context.json --barrier docs/reports/data/2026-09-18-nocbench-aifoundry2/barrier-chip1.jsonl \
    --out DATA/hotline.json                        # DATA3: aifoundry3
python3 tools/ettelem/analyze_reruns.py docs/reports/data/2026-09-23-reruns-aifoundry2-warm \
    docs/reports/data/2026-09-23-reruns-aifoundry3 --out reruns.json   # the pooled energies (E29)
```
`context.json` (committed 25 September) holds only what no raw file has: the errata text, quoted by hand, and the
window table (below). `--barrier` reads the chip barrier from the 18 September nocbench run (4,995 cycles with one
minion per shire); the uncontended round trip (216.2 cycles) and the bank's 10.0 cycles per atomic are computed from
the sweep. Until then `hotline.json`'s `context` block had no producer.
**Raw data:** `docs/reports/data/2026-09-22-hotline-aifoundry2/{sweep.jsonl,power.json,context.json,hotline.json}` and
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
PMIC's running averages, τ ≈ 1.2 s), on aifoundry2 only, reduced by
`python3 tools/ettelem/analyze_hotline_power.py DATA --out DATA/power.json` (the `--power` input of E22's command).
**Raw data:** as E22, plus `docs/reports/data/2026-09-22-hotline-aifoundry2/{telemetry.jsonl.gz,runs.jsonl,marks.jsonl}`.
The 5, 40 and 100 ms window runs behind "identical for windows of 5, 10, 40 and 100 ms" are not in these files (every
sweep row has `window_cycles` 6,000,000); their counts exist only in the hand-kept `context.json`, which
`analyze_hotline.py --context` copies into `hotline.json` `context.window_independence`.
**Result:** the host shire completes **192–384 operations and then nothing**. The count is identical for
windows of 5, 10, 40 and 100 ms while the mesh retires six million atomics, so this is a stop, not a
slow-down: 0.01–0.05% of the uncontended rate. It does not matter whether the host is reading scratchpad or
DRAM, nor where the hot line lives. **The threshold is bank saturation and it is a cliff:** 20 remote
requesters leave the host at 98.9%, 24 take it to 0.02%, and 24 is where the measured cost reaches the
bank's 10.0 cycles per atomic. One other shire is enough. Pacing the remotes to one atomic per 10,000 cycles
returns the host to 54% and costs the hammering shires 4%. Energy: 23.6 nJ per contended atomic against
1.4 nJ spread over 32 lines, a factor of **17**, while 1,024 stalled minions cost only 1.4 W over idle (first run;
re-measured in E29: 19.8 [16.9–23.6] nJ against 1.16 [1.01–1.37] nJ, still 17×, and about 1.2 W over idle for the
stalled chip, 1.19 [1.01–1.41] W, `reruns.json` `hotline_over_idle_w`). aifoundry3 repeated the sweeps, not the
power runs. The stalled host's 384 and 192 operations and the 10.0 cycles per atomic repeat exactly. In the 40
configurations that have a host shire, its count matches exactly in 15 and agrees within 2% in all but one: with the
host reading its scratchpad and the hot line in its L3 slice it gets 240 operations through against aifoundry2's 208.
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
Since 25 September `analyze_onchip.py` also writes the mesh layout (`layout`, `empty`, imported from
`workloads/nocbench/analyze.py`), the ring order (`ring`), the headline configuration as repeated in each sweep group
on each card (`repeats`), and per ring offset each card's bandwidth and
stage time (`distance[].by_card`) and the longest hand-off (`distance[].longest`); every earlier key is unchanged.
**Raw data:** `docs/reports/data/2026-09-22-onchip-aifoundry2/` (`sweep.jsonl`, `telemetry.jsonl.gz`,
`runs.jsonl`, `marks.jsonl`, `onchip.json`) and `docs/reports/data/2026-09-22-onchip-aifoundry3/sweep.jsonl`.
**Result:** at 1 MB per shire per stage, eight stages, 512 MB of traffic: DRAM **48.4 GB/s**, the next shire's
scratchpad **592.9 GB/s (12.3×)**, the shire's own **1,483.7 GB/s (30.7×)**. Energy per byte moved: 104.8,
8.9 and 4.25 pJ (first run; E29 re-measured them at 105.7, 8.6 and 3.99 pJ/B) — and all three draw within a watt of
each other over idle, so the on-chip routes get 12× and 30× more done for about the same power. aifoundry3 gives 12.4× and
31.2×.
**The boundary:** the advantage is against DRAM, not against the hierarchy. Below the 32 MB L3 the DRAM route
runs at 280–410 GB/s and the hand-off buys 1.0–1.4×; at 32 MB per buffer it falls to 47.9 GB/s and stays
there out to 256 MB. **Arithmetic:** the lead holds to about four adds per element and then falls faster with each
quadrupling, from 12.2× at one add per element (this sweep's own run) to 1.5× at 256, which is 32 flops per byte
moved (read plus written). **Distance:** the ring runs in shire-ID order, and the next shire by ID is 1–10 mesh hops
away (3.5 on average) while s+16 is only 2.1; across the five offsets tried (1.6–4.5 hops on average) the bandwidth
runs 593–733 GB/s, not with the mean distance but with the longest hand-off in the ring (10 to 6 hops, r = −0.99 on
both cards, against −0.32 and −0.30 for the mean): the stage time grows about 3,200–3,300 cycles per hop of the
longest hand-off, and the ID-order ring used for the headline is the slowest. Five offsets are a correlation, not a
controlled test. Each hop also costs energy (E31–E32), which this sweep does not see.
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
**What it establishes:** an 8-lane vector op on zeros costs what a scalar one does (lanes computing on zeros add
nothing); a random-data `fmadd.ps` lane costs 6.5 pJ over the awake core, against 6.0 pJ per multiply-add in the
tensor unit, so the two datapaths cost nearly the same. In E27's figures, of the 1.2 pJ per multiply-add the tensor
unit saves, about half is instruction issue and half datapath (the operands differ as well: uniform in [0.5, 2) for
the vector unit, normal for the tensor unit); a DRAM write by tensor store
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
burst read from its last 0.6 s and corrected for the rails' filter (divided by 0.94, see below); and the SRAM rail's idle value
against die temperature.
```
python3 workloads/enercat/run_catalogue.py DATA --passes 3 --burst 3 --gap 4.5
python3 workloads/enercat/analyze_catalogue.py DATA_A2 DATA_A3 DATA_A2_ROWS --out catalogue.json
```
**Raw data:** `docs/reports/data/2026-09-23-catalogue-aifoundry2/` and `-aifoundry3/` (`runs.jsonl`, one line per
launch with pass and configuration; `telemetry.jsonl.gz`), reduced to
`docs/reports/data/2026-09-23-energy-manual/catalogue.json` (per-burst detail and per-configuration statistics). Since
26 September that file holds E46's catalogue on three cards, and this entry's is `catalogue-23sep.json` beside it
(byte-identical to `catalogue.json` at `299fac8`).
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
67 °C to 2.63 W at 82 °C on aifoundry2 (78 mW/°C at 80 °C; the whole rail 19.4 mW/MB at 80 °C), 1.90 W at 51 °C on
aifoundry3.
**Neighbourhoods:** the four quarters of a shire read its scratchpad at 3.8–4.2 pJ/B.
**The rails' filter** (`catalogue.json` `rail_filter`, added 25 September): over the bursts with more than 8 W on the
minion rail and at least 4 s of idle either side, the rail has fallen 57% of the step 1 s after the board's
step-down and 84% after 2 s on aifoundry2 (τ 1.15 s, 242 bursts), 55% and 83% on aifoundry3 (τ 1.22 s, 229).
**The sampler** (`sampler_median_ms`, `sampler_max_ms` per burst and per configuration, added 25 September): on
aifoundry2 the tensor loads and row walks from DRAM slow it to a median of 23–206 ms per sample over a burst (683 ms
for the longest single sample); every other burst, and every aifoundry3 burst, stays at 21–22 ms. The catalogue keeps those
bursts: 3 of aifoundry2's 1,176 are over the 60 ms rule the later analyses drop by, and dropping them would move its
DRAM term in E30 from 72.9 to 71.8 pJ/B, under one standard error.
**Caveats:** the die drifted between 71 and 85 °C over the aifoundry2 session and the shuffled order is what keeps
that out of the tables; the leakage correction is the E26 one. The rail split takes each rail's last 0.6 s of a
3 s burst and divides by 0.94, the part of a step the PMIC's average is taken to have reached; the measured fall is
0.91–0.92 at 2.6 s and 0.94 at 3.0 s, so the correction is kept as published, and each 1% of rail scale moves the
fitted minion delivery loss of E30 by about 1.2 points. In the three slowest-sampler bursts the rail readings are
stale (the NoC rail reads up to 0.6 W low). The first-pass DRAM row configurations touched too little to leave the L3
and measured the L3 instead (kept, labelled); E28 does the rows properly.
**Report:** [The energy manual](https://spacesheep.dev/@yaroslavvb/et-soc1-energy-manual) (A15), second edition.

## E28 — DRAM row hits against row misses, done with the L3 defeated (2026-09-23, 11:18–11:21, aifoundry2)

**Question (Q30):** does opening a DRAM row cost energy a programmer can see?
**Method:** 1 KB tensor loads from DRAM by 32 harts (minion 0 of every shire), each over its own 64 MB so the
touched set exceeds the 32 MB L3 whatever the pattern: sequential (each bank sees 32 columns of a row), row hit
(stride 8 KB: same bank and row, next column), row miss (a 248 KB jump after every 8 KB: a new row on every visit
to a bank). Three passes, zeros and random, as E27.
**Raw data:** `docs/reports/data/2026-09-23-catalogue-aifoundry2-rows/`, pooled into `catalogue.json` as `dramrow2/*`.
**Result:** 147 ± 8, 156 ± 5 and 153 ± 5 pJ/B on random data for sequential, row hit and row
miss; 115, 118 and 114 on zeros. **No difference within error.** The controller runs an open-page policy: a row
stays open until a refresh (every 2,325 cycles at 600 MHz, 3.88 µs as measured in E1; the controller is programmed
for 3.87 µs) or an access to another row of its bank closes it (E1, and
[Anatomy of a memory access](https://spacesheep.dev/@yaroslavvb/et-soc1-memory-anatomy#how-long-a-row-stays-open)).
Each hart here comes back to its row only every 1,200–1,400 cycles or so, with 31 other streams in between, and a
refresh falls every 2,325 cycles. So either every pattern paid an activation, or an activation is small next to the
transfer; the instruments cannot tell which, and for a programmer it makes no difference. These 32-hart loads cost
14–21% more per byte than E27's tensor loads at 76 GB/s, the two cards' mean (26–30% more on zeros; 13–20% and 22–26%
against aifoundry2's own tensor loads): use them to compare patterns, and E27's to price DRAM. Rails: on random data 67–71% of a DRAM row read is on no metered rail (73–75% on zeros).
**Caveats:** 32 harts give 14–17 GB/s, latency-bound, so the signal is 2.2–2.6 W over idle on random data (1.6–1.9 W
on zeros) and the per-pass error ±4–8 pJ/B; a 20 pJ/B activation would have shown, a 5 pJ/B one would not.
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
if the minion clock left 600 MHz in it or if the sampler's own median latency exceeded 60 ms. The first hot-line
session enters the pool from its `power.json`; since 25 September the script also pools the hot line's watts over
idle (`hotline_over_idle_w`: the stalled chip at 1.19 [1.01–1.41] W, n = 7).
```
python3 tools/ettelem/analyze_reruns.py docs/reports/data/2026-09-23-reruns-aifoundry2-warm \
    docs/reports/data/2026-09-23-reruns-aifoundry3 --out docs/reports/data/2026-09-23-energy-manual/reruns.json
```
**Raw data:** `docs/reports/data/2026-09-23-reruns-aifoundry2-warm/`, `-aifoundry3/`; the discarded cool-card
attempt `-aifoundry2/`; pooled into `docs/reports/data/2026-09-23-energy-manual/reruns.json`. Since 26 September that
file takes the relay, the rings and the levels from the version-3 passes (`analyze_reruns.py --v3-rl`, E43), and this
entry's values are in it as committed at `299fac8` (`git show 299fac8:<path>`).
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
pooled; (3) rings between shires s and s+16 starve the service processor's own management path on aifoundry2 (sample
latency, six management commands, 22 → 76–146 ms, the median in each of three passes; the board value changed
1.4–2.4 times a second, against 5–6 in the other rings) while aifoundry3 stayed at 22 ms; on aifoundry2 that ring's
energy read 33–45% low over three passes (39% on their mean) against aifoundry3's, so that row is aifoundry3 only.
(Superseded, 26 Sep: in E43 the same ring starved the sampler on all three cards in every pass, aifoundry3 included,
so the aifoundry3-only row is not supported either; see E43.)
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
aifoundry3); result in `docs/reports/data/2026-09-23-energy-manual/unmetered_fit.json`. Since 26 September that file
is the same fit over E46's catalogue on three cards (the droop on aifoundry2's: 0.86 mV per off-rail DRAM watt, 0.034
per other watt, minion IR drop 0.053 mV/W), and this entry's numbers are in it as committed at `299fac8`.
**Command:**
```
python3 tools/ettelem/fit_unmetered.py --out docs/reports/data/2026-09-23-energy-manual/unmetered_fit.json --overwrite
```
The fit was first computed inline in the session, and until 25 September `unmetered_fit.json` kept those numbers:
the script reproduced the attribution exactly (coefficients, standard errors, rms and n on both cards) but not the
droop block, whose inline busy and idle windows were not recorded (0.84 against the script's 0.87 mV per off-rail
DRAM watt). On 25 September the file was regenerated by the script, so every number below has a producer; the
attribution is unchanged to floating-point rounding, the droop numbers are the script's, and the file gains each configuration's row
(`<card>.per_config`, `ddr_droop.per_config`) and a comparison refit that counts the line read before each store
through the L1 (`l1_line_read_refit`, not the published fit). The droop fit uses only the aifoundry2 catalogue
telemetry (n = 386). The script will not replace an existing file unless `--overwrite` is given.
**Result:** aifoundry2: 0.196 ± 0.003 per minion-rail W, 0.050 ± 0.017 per SRAM W, 0.286 ± 0.021 per NoC W, 72.9 ±
1.6 pJ per DRAM byte, rms 0.35 W over 392 configuration means (1.1 W on the 17 DRAM configurations); aifoundry3:
0.177, 0.064, 0.264, 68.1 pJ/B, rms 0.30 W over 386 (1.3 W on its 11 DRAM configurations). So an instruction's
unmetered energy is the minion regulator's delivery loss (18–20%), a DRAM byte's is about 70 pJ in the PHY, the I/O
rail and the chips (twice that per useful byte through the L1 write-back path, which reads the line first), and the
NoC coefficient is too large for a regulator alone: the memory shires' logic, on an unmetered rail, works when the
mesh moves bytes to them. The DRAM residual is about a quarter of those configurations' unmetered power, and it has a
pattern: stores through the L1 sit 1.3–2.7 W above the fit, because their line reads are not counted as bytes;
random data sits above, zeros and constants below. **The DDR rail droops 0.87 mV per off-rail DRAM watt** (0.029 mV
per watt of anything else, rms 0.37 mV over 386 configurations; 767 mV at idle against an 800 mV set point):
1 mV ≈ 1.2 W of DRAM, refreshed once per service-processor pass (133–156 ms on aifoundry2, depending on the poller: E41), a meter for the largest unmetered consumer that was in
every telemetry file all along. It responds mostly to DRAM traffic, not only: heavy mesh and scratchpad traffic with
no DRAM access droops it by up to about 2 mV (2.2 mV for L3 reads through the mesh), which it would read as up to
about 2 W of DRAM, and its idle reading moves by about 1 mV between 71 and 77 °C. The minion rail sags 0.070 mV per
watt the cores draw.
**What it does not do:** none of the Moortec sensors measures current, so none meters the DDR, VDDQ, PCIe, IO or
Maxion rails; the droop is a calibrated proxy, not independent of the board meter; the idle 12–16 W (12–13 W on
aifoundry3 at 51–56 °C, 14–16 W on aifoundry2 at 66–82 °C) stays unsplit, and the fit's rms says nothing about it.
The observability report's improvement ladder (A2, second edition) ranks what would meter more.
**Caveats:** the fit's SRAM and NoC coefficients are collinear with the minion one in many configurations (their
standard errors say so); the minion delivery loss (18–20%) holds only as far as the rails' meters can be trusted:
it moves about 1.2 points for each 1% of rail scale, which the fit cannot pin (E27, the rails' filter); the droop of
other rails leaks into the DDR monitor at 0.029 mV per board watt.
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
geometry by `tools/ettelem/build_wire_report.py` into `report.json`. E31 and E32 are reduced together, from the
repository root (the first command reproduces the committed `wire.json` byte for byte; `build-report.py` needs
`npm ci` once, for mathjax-full):
```
python3 workloads/enercat/analyze_wire.py docs/reports/data/2026-09-24-wire{,2}-aifoundry{2,3} \
    --out docs/reports/data/2026-09-24-wire-energy/wire.json --pitch-x-mm 3.73 --pitch-y-mm 3.70
python3 tools/ettelem/build_wire_report.py --wire docs/reports/data/2026-09-24-wire-energy/wire.json \
    --out docs/reports/data/2026-09-24-wire-energy/report.json
python3 scripts/build-report.py heat-per-mm docs/reports/data/2026-09-24-wire-energy/report.json \
    docs/reports/2026-09-24-heat-per-mm.html
```
`build_wire_report.py` also reads the energy manual's `manual.json`, the die geometry's `research/geometry/pitch.json`,
the logical mesh map of `workloads/nocbench/analyze.py` and the raw runs' reader>target maps; since 25 September it
resolves those paths from its own location, so it runs from any directory, and stops if one is missing (before, run
outside the repository root, it silently dropped a section).
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
three skeptics and a synthesis; `docs/reports/data/2026-09-24-wire-energy/review/`). The measurements reproduced
within 1–3% on the rail's coefficients (6% on the free-link fixed part: Method B 45.6 against 43.1 fJ per bit per
hop) and about 7% on board power; its corrections to the interpretation are in the report and in
[20-heat-per-mm.md](20-heat-per-mm.md). The review's `indep/fits.txt` was regenerated on 25 September with the
default health filter, as its sibling `fits_leak.txt` had been: only the four lines of its C4 axis block changed,
because the file first committed was the `--keep-bad` output.
**Report:** [Heat per millimetre](https://spacesheep.dev/@yaroslavvb/et-soc1-heat-per-mm) (A17).

## E33 — The memory hierarchy: latency, bandwidth and scratchpad distance (2026-09-18, 17:44–17:52, aifoundry2)

**Question:** what does each level of the memory hierarchy cost in time, and how far away is another shire's
scratchpad? Registered on 25 September for a session that ran before this register began (resource R4).
**Tool:** `workloads/memhier` (a pointer chase over working sets from 256 B to 256 MB, from four shires and from hart
1; the same chase in every shire's scratchpad; streaming TensorLoads for bandwidth; `run_energy.py` for board power).
**Command** (on the lab machine; each probe is its own `timeout 10` process):
```
ssh aifoundry2 'cd ~/nekko && bash workloads/memhier/run_lab.sh build/memhier/host/memhier_host build/memhier-data'
python3 workloads/memhier/analyze.py docs/reports/data/2026-09-18-memhier-aifoundry2 \
    --embed docs/reports/2026-09-18-et-soc1-memory-hierarchy.html
```
**Raw data:** `docs/reports/data/2026-09-18-memhier-aifoundry2/` (the chase files, `dvfs-poll-during-spin.txt`, and
`energy/`, `energy2/`: two runs of an earlier `run_energy.py` that recorded neither clock nor voltage); its README
names the group of `run_lab.sh` behind each file.
**Result** (the page's embedded `memhier-data`): load-to-use latency 5.25 cycles in the L1, 36 in the L2 read buffer,
47 in the L2 and the local scratchpad; the L3 159–169 cycles and DRAM 287–297 cycles (479–495 ns) in the chases that
ran at 600 MHz, DRAM 352–368 cycles in those the governor ran at 800 MHz (`plateaus`). DRAM fits 86.3 cycles plus
344.8 ns, the L3 72.2 cycles plus 61.4 ns plus 20 ns per mesh hop (`fits`); another shire's scratchpad
65.95 cycles plus 56.48 ns plus 20.00 ns per hop (`scp_model`). Bandwidth, from the launches at 600 MHz only
(`scripts/ridge-points.py`, `memhier_levels()`): L1 6.2 TB/s, L2 2.45, own scratchpad 2.46, L3 0.98, another shire's
scratchpad 0.96, DRAM 76 GB/s; the 23 September reruns reproduce them within 0.3% on both cards.
**Caveats:** the governor was free to move the clock (the page splits the chases by the clock they ran at); the energies
per byte of this session are superseded by the energy manual's §4 (E29, a pinned 600 MHz, both cards). One energy run
crashed the host runtime during the DRAM stream, and a full chip reset restored the card.
**Report:** [Memory hierarchy](https://spacesheep.dev/@yaroslavvb/et-soc1-memory-hierarchy).

## E34 — On-chip communication: messages, reductions, barriers and their energy (2026-09-18, 19:14–19:28, aifoundry2)

**Question:** what does it cost to move data between minions and shires by TensorSend, credits, reductions and
barriers? Registered on 25 September, like E33 (resource R4).
**Tool:** `workloads/nocbench` (round trips between minion pairs and all 496 shire pairs, combine on receive,
credits, flags through memory, reduction trees of 2–1,024 minions, shire and chip barriers, loaded pairs;
`run_energy.py` for rings of 1 KB messages at different distances, with board power).
**Command** (on the lab machine):
```
ssh aifoundry2 'cd ~/nekko && bash workloads/nocbench/run_lab.sh build/nocbench/host/nocbench_host OUTDIR'
python3 workloads/nocbench/run_energy.py --host-bin build/nocbench/host/nocbench_host --out OUTDIR/energy-a
python3 workloads/nocbench/run_energy.py --host-bin build/nocbench/host/nocbench_host --out OUTDIR/energy-b \
    --only xshire1-c4,shire-c4,xshire6,xshire4,xshire2,xshire8,xshire16,xshire1,shire,neigh,pair,spin
python3 workloads/nocbench/analyze.py docs/reports/data/2026-09-18-nocbench-aifoundry2 \
    --memhier docs/reports/data/2026-09-18-memhier-aifoundry2 --search \
    --embed docs/reports/2026-09-18-et-soc1-on-chip-communication.html
```
`analyze.py` also embeds the energy manual's 23 September re-runs of these rings (`--reruns`, by default
`docs/reports/data/2026-09-23-energy-manual/reruns.json`) and, with `--search`, records every restart of the layout
search.
**Raw data:** `docs/reports/data/2026-09-18-nocbench-aifoundry2/` (its README maps each file to its `run_lab.sh`
group; `first-energy-run/` is an earlier version, not used).
**Result** (the page's embedded `nocbench-data`): a TensorSend round trip is 68 cycles on a fast-network pair and 114
elsewhere in a shire (`primitives`); between shires 150 + 12.02 cycles per mesh hop, worst residual 1.1 cycles
(`matrices["matrix-pingpong"]`), and with 1 KB messages 12.0 cycles per hop up to 5 hops and 36.0 beyond
(`matrices["matrix-pingpong-c32"].knee`). The layout search recovers marty1885's shire map from the latencies in 12 of
12 restarts (`matrices["matrix-pingpong"].search.restarts`). A shire barrier is 237 cycles, a 32-minion allreduce 432,
a 1,024-minion allreduce of 32 B 1,368 cycles (2.28 µs); the chip barrier is 4,995 cycles with one minion per shire
and 5,018 with all 1,024 (`barrier-chip{1,32}.jsonl`). Energy: the re-measured rings of 23 September (E29) give
0.67 pJ/B on pairs, 2.1 in a neighbourhood or a shire ring, and 9.3 + 1.7 pJ/B per mean hop across the mesh
(r² 0.95, the two cards pooled, which mixes a card difference: 7.6 + 2.3 on aifoundry2 and 10.2 + 1.3 on aifoundry3,
the slope known to about ±50%; `reruns.mesh_fit` at `299fac8`; E43 re-measured the rings on three cards); the
18 September runs gave 0.8, 2.3 and 10.0 + 1.9 and are superseded.
**Caveats:** one card, at 600 MHz throughout (`clock.csv`); the 18 September energies read 2–20% (median 10%) above
the reruns.
**Report:** [On-chip communication](https://spacesheep.dev/@yaroslavvb/et-soc1-on-chip-communication).

## Version 3 of the claims check: what E35–E47 share

E35–E46 are version 3 of the claims check (Q45, Q50), run unattended on three cards from 2026-09-25 17:23 to 09-26 06:53
(the first block's `t0_ms` and the last one's `t1_ms`). What the entries share is stated here once. `V3` below is
`docs/reports/data/2026-09-25-claims-v3/`; a1c1 is aifoundry1's card 1.

- **Pre-registered.** `V3/PLAN3.md` §2 (commit `d4e162f`, before any card run) gives each experiment its items: the
  page claims it tests, a prediction and a decision rule. Amendments A1–A5 (`V3/AMENDMENTS.md`), each committed before
  the data it touches, change how rules are applied, never a band after the data. The code is
  `tools/claims-v3/<exp>/` (`block.sh`, `reduce.py`, and a README that lists where it departs from PLAN3's command
  lines); every block records the sha256 of the code it ran (`code.sha256`).
- **Cards.** aifoundry2 and aifoundry3, the registered pair (firmware 1.3.1; aifoundry3 held at 600 MHz by its
  boot-time 0 W TDP), and a1c1 (firmware 1.2.0), added by amendment A2 after the machine fixes of 25 September.
  aifoundry1's card 0 was excluded for safety before any campaign data (A4: 98–102 °C in its smoke blocks, 115–117 °C
  with nothing running after the last). All three idled at 600 MHz, at 518, 523 and 499 mV on a2, a3 and a1c1
  (`V3/results/idle.json`, `idle_clocks.<card>.minion_mv_median_at_used`).
- **Blocks.** Each card ran `tools/claims-v3/queue.sh tools/claims-v3/schedule-<card>.txt`, which runs
  `tools/claims-v3/<exp>/block.sh <pass>` for each line. A block starts only when no one else uses the card (on
  aifoundry1 a login alone no longer blocks: A3), holds the card's lock, runs every device process under `timeout 10`,
  and writes `V3/raw/<card>/<exp>/p<N>/` with a `block.json` (`t0_ms`, `t1_ms`, `die_c_start`, `die_c_end`, `status`,
  `note`). 197 blocks ran: 65 on a2, 67 on a3 and 65 on a1c1. Three failed, all on aifoundry3 (E35, E38, E43); each was
  run again, and the failed attempt is kept as `p<N>.attempt-<epoch>` and not used. `queue-state.jsonl` beside each
  card's data logs every block's return code, the gather/scatter blocks that followed (E48) included.
- **The unit and the outcomes.** The unit is a pass: an independently started block, or the blocks that make one.
  Intervals are 99% t on pass-level values. Each item has a **registered** outcome over aifoundry2 and aifoundry3,
  exactly as PLAN3 defines it: PASS (holds on both), CARD-DIFFERENT (holds on one; the page gives per-card values), FAIL
  (the prediction failed; the page drops or qualifies the claim and takes the measured values), INSUFFICIENT (fewer
  than three kept passes on a card, or a missing input). Each item also has an **all-cards** outcome over the three
  cards (A2, A4); REPORTED means the item names other cards and is shown, not tested, on this one. Decisions use this
  campaign's passes only: committed runs are printed beside them, never pooled.
- **Reduction.** From aifoundry2's checkout, `tools/claims-v3/collect.sh <dir>` copies the three cards' data and
  `tools/claims-v3/reduce_all.sh <dir> <out>` runs every `reduce.py`, writing `<exp>.json` and `<exp>.log`: committed
  as `V3/results/`. Each item carries `outcome` (registered), `all_cards`, `per_card` and `reading`;
  `V3/results/pagemap.json` (and `.md`) maps every page claim to the items that decide it.
- **Not run.** V3-COOL (aifoundry2 only, from a cool die; PLAN3's suggested E46) was not scheduled, so its claims keep
  their one-card labels; E46 is used for catfull, the full-catalogue re-run that Q50 added. V3-LONG (E47) needed a
  waiver of the 10 s rule, which the owner did not give.
- **Comparability.** The host changes of 16:14–16:27 on 25 September precede every block, and aifoundry3's idle die
  sat at 55–57 °C instead of 53–54 °C after them (A5); host-side timings are not comparable with the earlier sessions
  ([14-card-behaviour.md](14-card-behaviour.md), "Host changes of 25 September"). The version-3 passes run before
  those fixes (25 September, 10:00–16:19) are not used (A2) and are not in this directory.

## E35 — The memory anatomy, the cycle-counter window and the wake-up probe on three cards (2026-09-25 23:20 – 09-26 06:51, three cards)

**Question:** do the memory-anatomy page (61 claims on aifoundry2 alone, mostly one launch), the hub's cycle-counter
tile and E18's no-power-gating result hold on every card, pass after pass? 80 claims, 15 items.
**Method:** `tools/claims-v3/mem/block.sh <pass>`: the `workloads/memprobe` op programs with the registered seeds
(timer phases, ladder, decomp, l3map, msmap, bits, refresh, pagetimeout), each its own `timeout 10` process in `shuf`
order under the 10 Hz sampler, ladder and decomp again from requesters 7, 24, 31, and in passes 1–3 the wake-up probe
(idle 0 to 16M cycles); a2 and a1c1 heat to 76 °C first. Five passes per card. Decision: the 99% t interval of the
pass values inside each registered band on each card (one-sided for fractions; every pass for deterministic items);
MEM-W holds if no level shifts ≥ 5 cycles in ≥ 18 of 20 lines after 16M cycles in 3 of 3 probes. A2.mem: a1c1 is
judged on clock readings inside kernels only (the busy rule), a2 on every sample, a3 is pinned.
**Raw data:** `V3/raw/<card>/mem/p<N>/` (`<prog>.u32` and labels, `req{7,24,31}/`, `wake/`, `telemetry.jsonl.gz`,
`memprobe.log`, `drop.json`, `binary.sha256`); a3's failed first pass 3 (refresh returned nothing) is
`p3.attempt-1790423247`; a3's extra pass 6 is kept but unused. Reduced to `V3/results/mem.json` (`mem.passes.json`).
**Result:** five passes and three probes kept per card, every sample at 600 MHz. Registered and all cards alike: PASS
MEM-P1, P2, P3, P9, X2, W; CARD-DIFFERENT P4, P7 (a3 fails); FAIL P5, P6, P8, P10, R1–R3. L3 hits: slope 11.99
[11.96–12.02] cycles per hop and intercept 110.5–110.6 on every card
(`[item=MEM-P1].per_card.<card>.tests.P1_l3_slope`). DRAM within ±3 cycles of the 19 September model for 97.0%, 92.9%,
94.4% of lines (a2, a3, a1c1; `MEM-P2`). Ladder medians L2 49, L3 170.6–171.2, DRAM 303.0–304.6 cycles, the DRAM
intervals wider than the 303–315 band (`MEM-P8`). Row conflict +36.9 [35.4–38.4], +37.4 [31.3–43.5], +36.5
[35.2–37.8] cycles (`MEM-P4`). Refresh every 2,325.4 cycles on every card, but closed − open is 5.3–6.6 cycles (10–13
predicted) and only 0.26–0.36 of pairs with no refresh between hit the open row (≥ 0.98 predicted; `MEM-P5`,
`MEM-P6`). The counter's raw differences are only 10, 138 and −118 in all 30 t_raw and t_rawodd launches, but no
single short window fits in 8, 15 and 13 of 15 launches (`MEM-R1`). No cache level wakes up after 16M idle cycles on
any card; L2 reads 60–61 cycles without idle, 49–50 after (`MEM-W`).
**Caveats:** the missed P5b and P6 bands came from the one-card analysis of 19 September; all three cards miss them
alike, so the pages take the measured values. a3 ran its own build (kernel ELF `180eb2ac…`; a2 and a1c1 `55c6dbab…`).
Passes started at 74–86 °C on a2, 54–66 °C on a3, 58–67 °C on a1c1. a3 gave no informative counter-window readout.
**Report:** [Anatomy of a memory access](https://spacesheep.dev/@yaroslavvb/et-soc1-memory-anatomy) (A1); [The ET-SoC-1's DVFS loop](https://spacesheep.dev/@yaroslavvb/et-soc1-dvfs-leakage) (A11); [Limits of observability](https://spacesheep.dev/@yaroslavvb/et-soc1-limits-of-observability) (A2).

## E36 — Latency, cycle-count and bandwidth sweeps, repeated on three cards (2026-09-25 17:28 – 09-26 06:53, three cards)

**Question:** do the memory-hierarchy and on-chip-communication numbers (one aifoundry2 session, E33–E34), the
sparse-compute cycle counts and layer times (one aifoundry3 run) and the hot-line and relay sweeps (one launch per
card, E22–E25) repeat, pass after pass, on every card?
**Method:** `tools/claims-v3/lat/block.sh <pass>`: nine units in an order shuffled per pass, the same on every card
(memhier chases and scratchpad sweep, nocbench, the sparsity groups and extras, enercat's lone-minion DRAM streams,
`sgemm_host`, 77 hot-line and 119 relay processes), every process under `timeout 10`, the 10 Hz sampler in every unit.
a2 and a1c1 ran each pass as two half blocks (11–32) heated to 76 °C before every unit, a3 as whole blocks (1–3); each
card added two divergence-only blocks (4, 5). Launches off 600 MHz are dropped (a2: the registered rule; a1c1:
A2.lat's idle-aware rule; a3 is pinned). Deterministic items must hold in every kept pass, magnitudes by 99% t on pass
means; N3 by a shire-block bootstrap, S5 over five short blocks, R by a permutation test; either card can decide FAIL.
**Raw data:** `V3/raw/<card>/lat/p<N>/` (`order.json`, `idle.jsonl`, per unit the host printouts, `launches.jsonl`,
`telemetry.jsonl.gz`; a2's also hold V3-COOL's warm controls, `c6/`, reduced by nothing); `V3/results/lat.json`.
**Result:** registered PASS LAT-M1, M2, M3, S1; FAIL N1–N4, S2–S5, G, R3, H; INSUFFICIENT R. All cards: the same on
every item. Every item kept 3 passes per card (R on a3: 2), none dropped for its clock, and the cards agree within a
cycle on all but the chip barrier, so most FAILs are a band every card missed alike (paths under
`.items[item=LAT-…]`): shire barrier 232.5–232.7 cycles (predicted 237 ± 1), 32-minion allreduce 444.1–444.3 (432 ±
2), 1,024-minion allreduce 1,392.6–1,393.4 (1,368 ± 10), credits 140.2 + 14.42 per hop (148 + 12.2) (N1, N4, N2
`credit_fit`); 4-line lone-minion loads 41.9 and 42.95 cycles (43–49) (S2); all-minion L2 at 20,000 loads 256.5 (259.3
± 1.5), so the cold-start reading goes (S3); seed 3 at 99% 2.598 µs (1.9–2.5) (S4); 18 September's lane efficiencies
not reproduced, though "from α = 2" stands, a2 +0.0155 [0.0128–0.0182] T/s (S5); sgemm n = 64 on one shire
0.54–0.56 ms (0.31), 0 mismatches (G); a lone enercat minion 0.907 B per cycle, not 1.40 (R3); 31 one-per-shire
requesters leave the hot line's host at 100% (≤ 1% predicted) (H `sub.P5_pollers`); the flag round trip's slope bound,
+9.2 on a2, lies between keep (< +6) and drop (≥ +12.02) (N3 `bootstrap99`).
**Caveats:** five of a3's 917 LAT host processes exited abnormally (exit 139 four times in the relay units of passes 2
and 3, once 134; the campaign's binaries predate E49's fix), which cost LAT-R its third a3 pass. Two probes moved with
the pass on every card alike (16-line lone-minion DRAM 1,132.5 cycles in pass 1, 748–751 after; 2,000-load L2 351–353
falling to 262–269), so their pass means carry 99% intervals hundreds of cycles wide.
**Report:** [Sparse compute](https://spacesheep.dev/@yaroslavvb/et-soc1-sparse-compute); [On-chip communication](https://spacesheep.dev/@yaroslavvb/et-soc1-on-chip-communication); [One hot line stops a shire](https://spacesheep.dev/@yaroslavvb/et-soc1-hot-line) (A13); [Memory hierarchy](https://spacesheep.dev/@yaroslavvb/et-soc1-memory-hierarchy); [Ridge points](https://spacesheep.dev/@yaroslavvb/et-soc1-ridge-points) (A19); [Hand it to the next shire](https://spacesheep.dev/@yaroslavvb/et-soc1-on-chip-relay) (A14); [Test drive](https://spacesheep.dev/@yaroslavvb/et-soc1-testdrive); [Limits of observability](https://spacesheep.dev/@yaroslavvb/et-soc1-limits-of-observability) (A2); [L2 mainline starvation brief](https://spacesheep.dev/@yaroslavvb/2026-09-22-et-soc1-l2-mainline-starvation).

## E37 — The matmul benchmark on three cards: rate, exactness, watts, private tiles and the load step (2026-09-26, 00:19–06:36, three cards)

**Question:** the matmul page's lede (9.5 / 19.0 / 71.8 T(FL)OP/s, exact, 57–62 W), the ridge page's cause for int8's
7.3 B per minion-cycle and the power-and-temperature page's busy slope and load step each rested on one aifoundry2
run.
**Method:** `tools/claims-v3/mmb/block.sh <pass>`, four passes per card, all kept: smoke checks; the four 6 s mmbench
workloads (fp32, fp16, int8 from the L2, fp32 from DRAM) in each pass's registered order, sampled by ettelem at 10 Hz
through a patched `mmbench_power_v3.py`; private-tile launches (`-n 4 -p`) against the shared `-n 16` control, cycle
counters only; and the E5 load step (eight fp32 matmul processes, then four memprobe DRAM streams) with
`run_thermal.sh`'s phases. a2 and a1c1 heat to 76 °C before each part. Launches off 0.595–0.605 GHz are dropped; on a2
any sample off 600 MHz, on a1c1 busy samples only (A2.mmb). Cycles, rate and exactness must hold in every launch;
watts, per-W, the A100 lead, the rise and the load step's P1–P10 by 99% t over pass values against registered bands.
**Raw data:** `V3/raw/<card>/mmb/p1`–`p4/` (`e1/<workload>/` telemetry, `runs.jsonl`, `results.json`; `x1/`;
`thermal/`; `smoke/`; `passcheck.json`); reduced to `V3/results/mmb.json` (`.log`).
**Result:** registered PASS on MMB-a to -f and MMB-X1; MMB-T FAIL (P1 FAIL; P3, P4 minion rail, P5 DRAM, P7
CARD-DIFFERENT; the rest PASS). All cards: PASS MMB-a, -b, -X1; CARD-DIFFERENT MMB-f (a1c1's fp16 and DRAM rise) and
MMB-T; MMB-c, -d, -e REPORTED. Every kept launch on every card: fp32 and fp16 529.001 cycles per op,
int8 280.35–280.37, 9.5105–9.5119 / 19.018–19.022 / 71.766–71.775 T(FL)OP/s per pass, all exact (`.items[item=MMB-a]`,
`[item=MMB-b]`). Board watts over idle, int8 (`[item=MMB-c].per_card.<card>["int8-tensor-L2"]`): a2 27.9 [26.6–29.3]
at an 80 °C die, a3 26.3 [26.0–26.6] at 62 °C, a1c1 33.1 [32.6–33.5] at 76 °C; a3/a2 0.94–0.95 in all four workloads
(`.cross`). Per W, a3 is 1.17 × a2 in each L2 mode (Welch p ≤ 1.2 × 10⁻⁴, `[item=MMB-d].cross`), a1c1 0.82–0.85 × a2;
the A100's int8 lead is 1.33, 1.13 and 1.63 (`[item=MMB-e]…a100_lead`). Private int8 tiles take 511.94 cycles per op
(4.00 B per minion-cycle) on all three cards against 280.47–280.48 (7.30 B) shared (`[item=MMB-X1/c]`). Load step:
busy slope a2 1.02 [0.67–1.36] W/°C (0.7–0.9 predicted), a3 0.61 [0.49–0.74] (0.3–0.6), a1c1 1.13 [1.05–1.22]
(`[item=MMB-T/P1]`); 600 MHz in every sample; PMIC average within 0.2 W of the board on every card (`MMB-T/P8`).
**Caveats:** each card's watts are at its own die temperature and idle (33.3, 26.0, 41.8 W before the workloads): the
per-W gap is the card at its operating temperature, not a card property. a2's load steps in passes 3 and 4 ran hotter
(busy 86.9–97.0 and 85.6–95.3 °C against 80.6–89.0, `MMB-T/P1.per_card.aifoundry2.busy_T_range`) and split its P3–P5
values into two pairs, which is why those intervals include 0. Private fp32/fp16 launches fail the result check by
design; their cycle counts stand. The busy-minus-idle slope (a2 0.20 [0.08–0.32] W/°C) is reported, not decided.
**Report:** [Power and temperature](https://spacesheep.dev/@yaroslavvb/et-soc1-power-temperature) (A3); [Matmul efficiency](https://spacesheep.dev/@yaroslavvb/et-soc1-matmul-efficiency); [Ridge points](https://spacesheep.dev/@yaroslavvb/et-soc1-ridge-points) (A19); [The Horace experiment](https://spacesheep.dev/@yaroslavvb/et-soc1-horace-experiment) (A4); [Limits of observability](https://spacesheep.dev/@yaroslavvb/et-soc1-limits-of-observability) (A2); [Sparse compute](https://spacesheep.dev/@yaroslavvb/et-soc1-sparse-compute).

## E38 — Tensor-unit energy by operands, precision, structure and active minions (2026-09-25 19:04 – 09-26 04:37, three cards)

**Question:** the why-low-power figures (pJ per MAC by precision, the integer loop, power linear in active minions),
the Horace page's negative zero, bit-field ladder and structured matrices, and the energy manual's fp16 and int8 rows
rested on aifoundry2 alone, two runs in one session (E15). Do they hold on each card, run by run?
**Method:** `tools/claims-v3/abla/block.sh <pass>`, passes 1–4 per card: the 23 configurations of `abl_a.cfg` in
shuffled order, each a separate 7 s `sparsity_host` process after its own strict start (a2 and a1c1 heat to 84 °C and
launch at 80 °C; a3 heats to 62 °C and launches at 57 °C, A5). Switching = early power − leakage × the rise since
launch − pre-launch idle (0.81 W/°C on a2 and a1c1, 0.55 on a3), after the registered dropout rule. Rule: per card 19
sub-tests at alpha 0.01/19 (differences exclude 0 with the predicted sign and the point inside its tolerance;
equivalences inside ±1.0 W); ABL-R descriptive, decided on a3 (leave-one-out rms ≤ 0.6 W); EM4c exact. A2.abla tests
T1, T5's fp32/int8 ratio, the EM4 rider, T7 and EM4c on a1c1 and reports the rest.
**Raw data:** `V3/raw/<card>/abla/p1`–`p4/` (runs, starts, telemetry, checks); a3's first p1 (25 Sep 19:04–19:39) hit
its time cap after 7 of 23 runs (`p1.attempt-1790421750`), re-run 26 Sep 04:22–04:37; reduced to
`V3/results/abla.json` (runs in `abla.runs.json`).
**Result:** 92 runs kept per card, every sample at 600 MHz. Registered: PASS T2, T3, T5, T5-EM4, T8, EM4c, EM4d;
CARD-DIFFERENT T1, T6, T7; FAIL T4, ABL-R; all cards the same. Corrected intervals, 4 runs, a2 / a3 / a1c1: pJ per MAC
over idle, int8 random 0.313 [0.297–0.330] / 0.262 [0.238–0.287] / 0.309 [0.261–0.357], fp16 random 2.661 / 2.410 /
2.70, fp32/int8 18.9 / 20.5 / 19.6 (`[item=ABL-T5]`); ones − zeros 8.52 / 8.09 / 9.00 W, random − zeros 25.33 / 23.91
/ 26.66 W (`[item=ABL-T8]`); −0.0 over +0.0 +8.36 / +8.05 / +8.85 W, −0.0 − ones −0.15 [−0.80–0.50] / −0.04
[−1.14–1.06] / −0.14 [−1.44–1.15] W (`[item=ABL-T1]`); integer loop over idle 1.51 [0.58–2.44] / 0.40 [−0.07–0.86] /
0.73 [−0.68–2.14] W (`[item=ABL-T6]`); switching per minion at 1,024 over 256 minions 1.094 / 1.239 [1.104–1.390] /
1.246 [1.013–1.532] against [0.98, 1.10] (`[item=ABL-T7]`); a3's Hadamard, butterfly and kaleidoscope 0.59–1.17 W
below 0.924 × the flip model, its DFT pair 1.67 [1.45–1.90] W above (predicted 2.7 ± 1.0); refit leave-one-out rms
1.01 / 0.91 / 0.97 W (`[item=ABL-R].per_card.<card>.refit_switching`); 1,320 timed launches per card at 546.00 (fp32,
fp16) and 318.00 (int8); a2's nine EM4 patterns within 2% of 21 Sep.
**Caveats:** corrected intervals use t = 16.05 at 4 runs (5.84 at plain 99%), so T1's equivalence and a2's T4
equivalences fail on width, points within 0.51 W of zero; on a3 all three non-DFT intervals lie below zero. a3
launches 23 °C cooler, so its lower values are the card at its temperature (E40 could not separate the two). a1c1
takes a2's leakage slope, its own unmeasured, and idled at 50.15 W before launch (a2 36.34, a3 25.78).
**Report:** [The Horace experiment](https://spacesheep.dev/@yaroslavvb/et-soc1-horace-experiment) (A4); [Why is the ET-SoC-1 low power?](https://spacesheep.dev/@yaroslavvb/et-soc1-why-low-power) (A5); [The energy manual](https://spacesheep.dev/@yaroslavvb/et-soc1-energy-manual) (A15); [The ET-SoC-1's DVFS loop](https://spacesheep.dev/@yaroslavvb/et-soc1-dvfs-leakage) (A11); [Limits of observability](https://spacesheep.dev/@yaroslavvb/et-soc1-limits-of-observability) (A2); [Ridge points](https://spacesheep.dev/@yaroslavvb/et-soc1-ridge-points) (A19).

## E39 — Sparse-compute energy and TenB streaming, strict start (2026-09-25 21:39 – 09-26 05:07, three cards)

**Question:** the sparse-compute page's "power saved 86%" and energy per layer rested on aifoundry3, two runs of one
session without temperature correction; the matmul page's "the difference is the kernel" (B streamed through TenB
against B in the L1) was never a controlled comparison.
**Method:** `tools/claims-v3/ablb/block.sh <pass>`, passes 1–3 per card: the 18 configurations of `v3-energy.cfg`
(run_energy.py's 11, gemv-dense-0, and int8 ones, int8 random and fp16 random with B in the L1 and with `--b-stream`)
in shuffled order, each a separate 5 s run after the strict start of E38 (a3 heats to 59 °C and launches at 57 °C,
A5). Metric: board power over pre-launch idle (no dropout rule registered). Rule: cycles per op inside fixed bands in
every timed launch (2a); per-block values or within-block paired differences, 99% t with df 2, on each card (2b, 2c,
3ab, 3c, 3d, 3f, 3g); the energy per layer stated per card, PASS only if every band is met, never CARD-DIFFERENT (3e).
A2.ablb tests 2a, 2b, 3ab, 3d, 3f and 3g on a1c1 and reports 2c, 3c and 3e.
**Raw data:** `V3/raw/<card>/ablb/p1`–`p3/` (as E38; no failed block); reduced to `V3/results/ablb.json`.
**Result:** 54 runs kept per card, every sample at 600 MHz. Registered: PASS 2a, 2b, 2c, 3c, 3d, 3f; CARD-DIFFERENT
3g; FAIL 3ab, 3e. All cards the same, except 3d CARD-DIFFERENT (a1c1's interval leaves 0.7–1.5). Values a2 / a3 /
a1c1, 99%, 3 blocks: every timed launch at 546.00 (fp16, B in L1), 318.00 (int8, L1), 529.00 (fp16, TenB) and
270.00 cycles (int8, TenB, never measured before), identical on the cards to 0.0002 cycle (`[item=ABLB-2a]`); TenB −
L1, int8 random +6.55 [5.97–7.14] / +6.04 [3.65–8.43] / +7.53 [6.77–8.29] W, int8 ones +2.72 / +2.40 / +2.67 W
(`[item=ABLB-2b]`); int8 random in L1 over idle 9.90 / 8.22 / 9.62 W (`[item=ABLB-2c]`); dense 17.51 / 15.53 /
17.30 W, zeros 2.47 / 1.03 / 1.39 W, saving 0.859 [0.786–0.932] / 0.934 [0.895–0.972] / 0.920 [0.910–0.930], none
inside 0.80–0.92 (`[item=ABLB-3ab]`); slope of power on the useful-slot fraction 14.97 [14.80–15.15] / 14.50
[12.99–16.00] / 15.78 [15.33–16.24] W, rms 0.28 / 0.18 / 0.32 W (`[item=ABLB-3c]`); row mask against half zeros 1.10 /
1.07 / 1.15 (`[item=ABLB-3d]`); µJ per layer over idle at skip-0 / 90 / 99%: a2 67.5 / 18.6 / 5.9 at 81.4 °C, a3 55.5
/ 11.9 / 3.3 at 58.4 °C (predicted 70 / 19 / 7), a1c1 75.4 / 16.2 / 4.5 at 80.3 °C (`[item=ABLB-3e]`); gating alone
(gemv-dense-0 − dense-90) +1.66 [0.65–2.68] / +1.59 [1.05–2.14] / +1.75 [0.72–2.78] W (`[item=ABLB-3f]`); fma on zeros
over the integer loop +0.87 [−0.87–2.62] / +0.69 [0.08–1.29] / +0.67 [0.04–1.31] W (`[item=ABLB-3g]`).
**Caveats:** three blocks give df 2 (t = 9.925); int8 ones' TenB cost and the gating alone miss their predicted bands
(+3 to +8, +0.3 to +1.5 W), though the rule tests only the sign. "The difference is the kernel" is undecided: the
reducer ran without V3-MMB's values (`[item=ABLB-2b].kernel_clause`). a3 runs 23 °C cooler than a2 and a1c1, so its
values are that card at that temperature. a1c1 idled at 50.17 W before launch (a2 36.38, a3 25.77).
**Report:** [Sparse compute](https://spacesheep.dev/@yaroslavvb/et-soc1-sparse-compute); [Matmul efficiency](https://spacesheep.dev/@yaroslavvb/et-soc1-matmul-efficiency); [The Horace experiment](https://spacesheep.dev/@yaroslavvb/et-soc1-horace-experiment) (A4); [Limits of observability](https://spacesheep.dev/@yaroslavvb/et-soc1-limits-of-observability) (A2).

## E40 — The card or its temperature? Switching power at two launch temperatures on each card (2026-09-25 21:46 – 09-26 06:03, three cards)

**Question:** three pages put aifoundry3's 0.92–0.95 switching scale down to the card, but every comparison changed
the card and the launch temperature together (81 against 56 °C). Does each card's switching move with temperature?
**Method:** `tools/claims-v3/x5/block.sh <pass>`: a hot and then a cool arm, each one block of the ablation runner
(`tools/claims-v3/abla/ablrun.sh`) on `x5.cfg` (fp32 zeros, ones, uniform and randn, fp16 randn; 7 s on 1,024 minions,
the same tiles in both arms of a pass), each arm with its own 10 Hz sampler. Launch / preheat: a2 and a1c1 83 / 86 °C
hot, 76 / 79 °C cool; a3 65 / 68 °C hot, 57 / 62 °C cool (A5; registered 55 / 60). Three passes per card. Decision:
per card and pattern (fp32 uniform, fp32 randn), the Welch 99.75% interval (Bonferroni over 4) of hot − cool
switching; "card property" if all four lie inside ±0.5 W, "temperature effect" if a3's two exclude 0 upwards with
points ≥ +0.4 W, otherwise "not separated". A2.x5: all_cards tests the card hypothesis on every card (busy clock
rule).
**Raw data:** `V3/raw/<card>/x5/p<N>/` (`hi<b>/`, `lo<b>/` session directories as in E38: `runs.jsonl`,
`starts.jsonl`, `telemetry.jsonl.gz`; `block.json`); per-run values in `V3/results/x5.runs.json`, reduced to
`V3/results/x5.json`.
**Result:** all 30 runs kept on every card, every idle and busy sample at 600 MHz. Registered: FAIL, verdict "not
separated"; all cards: FAIL (the card hypothesis fails on every card). Hot − cool, fp32 randn: a2 +1.20 W [+0.26,
+2.15], a3 +1.97 [+1.47, +2.46], a1c1 −6.36 [−49.36, +36.63]; fp32 uniform −7.04 [−69.54, +55.47], −7.29 [−18.48,
+3.90], −6.92 [−42.04, +28.20] (99.75%, 3 against 3 runs;
`[item=X5].per_card.<card>.tests.<pattern>.ci_hot_minus_cool`). fp32 randn switching, hot / cool: a2 27.68
[26.98–28.38] / 26.48 [26.23–26.73] W, a3 26.72 [26.25–27.20] / 24.75 [24.50–25.01] (99%, `.switching_by_arm`), at
measured launches of 83.3 / 76.7 °C (a2), 65.0 / 57.6 (a3), 83.0 / 76.0 (a1c1). The temperature-effect reading
(reported) holds for fp32 randn on a2 and a3, for uniform on no card.
**Caveats:** the runner's fixed order puts fp32 uniform first in every arm; in the hot arm it follows the preheat
bursts directly, and its idle bracket reads high (a2 48.9 and 50.6 W in passes 1–2 against 38.2–38.9 W for the arm's
later runs; a3 37.3–38.9 against 29.0–34.1 W), and its hot − cool reads −7.04 W on a2 and −7.29 W on a3: the uniform
test decides nothing (`V3/results/x5.runs.json`, `runs.<card>[config=fp32_uniform, arm=hi].p_before`). a1c1's brackets
read 45.9–69.3 W and rise after heated runs (mean 57.05 W, `[item=X5].all_cards.idle_clock.aifoundry1-c1.idle_w`), so
its switching scatters (fp32 zeros −10.8 to +1.6 W). a2's pass 3 began on a 99 °C die (block.json). a3's cool arm
launched at 57.6 °C and was reduced at 55.9 °C as registered (A5).
**Report:** [The Horace experiment](https://spacesheep.dev/@yaroslavvb/et-soc1-horace-experiment) (A4); [The energy manual](https://spacesheep.dev/@yaroslavvb/et-soc1-energy-manual) (A15); [Why is the ET-SoC-1 low power?](https://spacesheep.dev/@yaroslavvb/et-soc1-why-low-power) (A5).

## E41 — The meter chain on three cards: the SP's pass, reset windows, peak-hold, voltage maps, governor readouts (2026-09-25 21:56 – 09-26 04:37, three cards)

**Question:** "133 ms", quoted on 15 pages, was one aifoundry2 session with no sampler; the spatial brief's voltage
map and peak-hold figures were one capture per card; `--reset-ms` had never run; the governor readouts were one
session.
**Method:** `tools/claims-v3/tel/block.sh <pass>`, three passes per card at least 30 min apart, all kept: governor
readouts at INFO level (`sptrace` around five 2 s zeros launches, `etcfg`, `ettelem config`); seven arms in a shuffled
order (quiet; a power poll about every 16 ms; one per 0.1 s; ettelem at 100, 50 and 25 ms; a voltage-query loop), each
followed by an SP stats extract; a reset segment (`ettelem sample --reset-ms 1000` over three 3 s bursts); a DEBUG
block (per-shire voltage captures, three 14 s peak-hold windows). a2 and a1c1 heat to 76 °C first. On aifoundry1 a
pass takes the whole host (A2.tel). Rules: registered bands in 3 of 3 passes; P3, P4 and TEL-S by 99% t on paired pass
differences.
**Raw data:** `V3/raw/<card>/tel/p1`–`p3/` (`trace/merged.spst.gz`, `e10`/`e20`/`e40.jsonl.gz`, `pwr.csv.gz`,
`l10.csv.gz`, `volt.log.gz`, `reset.jsonl.gz`, `gov/`, `dbg/`, `marks.jsonl`); reduced to `V3/results/tel.json`
(`.log`).
**Result:** registered PASS P1–P4, P6; CARD-DIFFERENT TEL-S, TEL-G; FAIL P5, P7, TEL-R; INSUFFICIENT TEL-Q; all cards
the same except P6, CARD-DIFFERENT. In `.items[item=…].per_card.<card>`: the quiet SP pass is 133.2 ms in every a2
pass (`TEL-P1`), 134.8 on a1c1, 224.1–224.5 on a3 (`TEL-P5`, ≥ 230 predicted); on a2 ettelem at 10 Hz adds 26.6 ms
(one-sided 99% lower bound 21.6, `TEL-P3`), the voltage loop 12.4 [8.4–16.4], a single-command poll 0.8. The board
value refreshes, for the 0.1 s poll / ettelem 10 Hz / 20 Hz, every 126–134.5 / 155.5–157 / 186.5–187 ms on a2, 223–224
/ 262.5–264 / 319.5–322 on a3, 133.5–139 / 156.5–158.5 / 188–188.5 on a1c1; P_H − P_L is 39.8 [36.5–43.1] ms on a3 and
includes 0 on a2 and a1c1 (`TEL-S`…`H_minus_L_t99`). `--reset-ms` windows work on every a2 and a3 pass (flat to
0.47–0.66 W after a burst) and fail once on a1c1; the resets restart the rail average, median f(1 s) 0.93 on every
card against 0.45–0.68 predicted (`TEL-P7`…`median_f1`). The peak-hold high ends load windows 2 or 3 °C above the SP
maximum, pass medians disagreeing on every card (`TEL-R`). a3 reads TDP 0 W, 65 °C, `max_power` every pass, but its
trace held no throttle or idle event (≥ 5 predicted); a2 65 W, `managed_power`, no governor line (`TEL-G`…`passes[]`).
a3's idle voltage pattern has a plane (p = 0.001) and moves 1.6 mV sd under load (≤ 0.5 predicted); a2 and a1c1 have
two complete idle captures.
**Caveats:** the idle voltage pattern's pass-to-pass correlation is exactly 1.0 for every pair computed, which the
reducer does not explain. At 25 ms ettelem stretches the SP pass to 307–317 ms (a2, a1c1) and 582 ms (a3;
`passes.<card>[].sp.E40`). a1c1's P1–P5, TEL-G and the TEL-S bands are reported, not tested; three P7 bursts miss the
catalogue rule (a3 2, a1c1 1).
**Report:** [Limits of observability](https://spacesheep.dev/@yaroslavvb/et-soc1-limits-of-observability) (A2); [Power and temperature](https://spacesheep.dev/@yaroslavvb/et-soc1-power-temperature) (A3); [The ET-SoC-1's DVFS loop](https://spacesheep.dev/@yaroslavvb/et-soc1-dvfs-leakage) (A11); [Spatial temperature brief](https://spacesheep.dev/@yaroslavvb/et-soc1-spatial-temperature-brief); [Anatomy of a memory access](https://spacesheep.dev/@yaroslavvb/et-soc1-memory-anatomy) (A1); one claim each on A4, A15, A17, Matmul efficiency, Sparse compute and On-chip communication.

## E42 — Heat per millimetre, third run: the board split, the four-hop step and link-disjoint flows (2026-09-25 18:08 – 09-26 06:46, three cards)

**Question:** the heat-per-mm page's mesh-rail results were proven on both cards, but the board-power split into data
and fixed parts, the four-hop step on board power and the link-disjoint contrast were within noise at E31–E32's three
passes, and the byte-for-byte fill check rested on one card (16 claims).
**Method:** `tools/claims-v3/wire/block.sh <pass>`, six passes per card, all kept: E32's `run_wire.py --set v2` loop
on 28 configurations (`wu/p0`, `wu/p0.5`, `wu/p1`, `wsep/p0`, `wsep/p0.5`), shuffled per pass; per configuration a
`tstore_uniq` prefill, 5 s idle, a 3 s burst of 1 KB tensor loads from the scratchpad *d* hops away, 4 s idle,
`ettelem` at 10 Hz. a2 and a1c1 start each pass at ≥ 76 °C and heat for 2 s below 69 °C; a3 runs no heater. Pass 1
adds WIRE-FILL's 12 `--dump-slice` launches. Reduced by verbatim copies of the registered scripts
(`tools/claims-v3/wire/registered/`): an item passes when the 99% interval (df 5) excludes the null on both cards and
both means lie in the registered range; P10, P14 and P16 are equivalence tests; P13 is descriptive. A2.wire: a1c1
drops a burst only for a busy sample off 600 MHz.
**Raw data:** `V3/raw/<card>/wire/p<N>/` (`telemetry.jsonl.gz`, `runs.jsonl`, `marks.jsonl`, `idle_state.jsonl`,
`pass_check.json`; `dump/` in pass 1); reduced to `V3/results/wire.json` (`.log`).
**Result:** registered (a2 + a3): 21 PASS (P1–P5b, P6a, P7a–P7d, P10–P12, P14a–P16, WIRE-FILL); CARD-DIFFERENT P7e,
P7f, P8, P9 (fail on a3); FAIL P6b; P13 descriptive. All cards: 16 PASS; P1, P7b, P14b, P15b, P16 also CARD-DIFFERENT
(a1c1). Per card, mean [99%], 6 passes (`.items[item=WIRE-P1-16/<P>].per_card.<card>.mean`, `.lo99`, `.hi99`): a
random bit per mm on free links, mesh rail (P11a), a2 36.1 [35.2–37.0], a3 35.8 [35.1–36.5], a1c1 38.1 [26.3–49.9] fJ;
board (P11b) 46.7 [40.3–53.1], 44.4 [41.9–46.9], 51.1 [47.8–54.5] fJ. Sharing a link, mesh rail, per bit per hop: data
(P1) 31.7, 35.1, 44.9 fJ; fixed (P2) 33.8 [31.4–36.2], 33.0 [31.6–34.4], 42.3 [40.9–43.6] fJ. All ones over random per
hop, mesh rail (P6a): +9.6 [8.1–11.0]%, +8.1 [0.5–15.8]%, +12.3 [0.2–24.4]%; at one hop all ones cost 35.2, 35.7 and
36.7% less (P12). Four hops sit above the line through 1, 2, 3 and 6 hops by 6.5, 8.0, 7.9% (random, P7a) and 14.5,
15.2, 15.4% (all ones, P7c); link-disjoint flows at four hops are 0.1, 0.6 and 0.4% off their line (P14a). WIRE-FILL:
12 of 12 launches matched on each card (`.items[item=WIRE-FILL].per_card.<card>.matched`).
**Caveats:** most card differences come from one pass per card, which the rule keeps: a3's pass 4 (P8 −0.16 hop
against 0.56–0.60 in its other passes, P9 −0.25 against 1.11–1.18) and a1c1's pass 6 (P16 −47.6% against 0.1–2.9%,
P11a 23.5 against 40.9–41.3 fJ/mm; `.per_card.<card>.vals`). No burst was dropped (every sample at 600 MHz, implied
clock 0.5988–0.5997 GHz); one a3 burst did not launch (pass 6, `wu/p0.5/hop3`, exit 139). Dies: a2 72–90 °C, a3
55–60 °C, a1c1 60–75 °C with 26–27 heater launches per pass; the leakage correction is aifoundry2's idle law on every
card. WIRE-FILL checks the store kernel on a DRAM slice, not the scratchpad image.
**Report:** [Heat per millimetre](https://spacesheep.dev/@yaroslavvb/et-soc1-heat-per-mm) (A17).

## E43 — Rings, levels and the relay, with spin brackets and controlled scratchpad contents (2026-09-25 18:15 – 09-26 06:19, three cards)

**Question:** E29's L1, L2 and own-scratchpad energies and its per-hop ring slope differed between the cards, and
nothing said whether the scratchpad's contents caused it; "rings draw less than spinning", the small-message costs and
the leaving-the-shire step were within noise (30 claims).
**Method:** `tools/claims-v3/rl/block.sh <pass>`, six passes per card, all kept: half A, nocbench spin, the eleven
rings of E29 (reversed on even passes), spin; half B, memhier spin, L2 and own scratchpad in ABBA order after a
scratchpad prefill (zeros on odd passes, random on even), L1, L3, DRAM, remote scratchpad, spin; then the relay by
DRAM, next shire and own scratchpad. 10 Hz sampling; a2 and a1c1 heated to ≥ 76 °C before each part. 99% t on pass
values, Welch 99% between cards. Registered: a card difference only if Welch excludes 0, else pooled; RL-b decided on
a2, RL-c on a3; a ring draws "less than spinning" only if spin − ring > 0 on both cards; RL-h's bands 1.7–2.3 (zeros)
and 3.7–4.7 (random) pJ/B. A2.rl: a1c1 counts busy samples for its 600 MHz rules.
**Raw data:** `V3/raw/<card>/rl/p<N>/` (`A/`, `B/`, `relay/` with `telemetry.jsonl.gz`, `runs.jsonl`, `marks.jsonl`;
`state.jsonl`, `quality-windows.json`); a3's first pass 4 (an xshire4 launch exited 139) kept aside as
`p4.attempt-1790422676`; reduced to `V3/results/rl.json` (`.log`).
**Result:** registered: 18 of 30 parts PASS (RL-a to RL-d, RL-g, RL-h, X3 (a) pair and the five 1 KB cross-shire
rings, X3 (e) inside-shire rings); CARD-DIFFERENT X3 (a) shire-c4 and xshire1-c4, both (d) spin bands, (e) scp-remote;
FAIL RL-f and X3 (a) neigh and shire; INSUFFICIENT X3 (a) xshire16 and the three X4 rows. All cards: relay DRAM and
RL-h CARD-DIFFERENT (a1c1), RL-f INSUFFICIENT, the rest the same. Per card, mean [99%], 6 passes
(`.items[item=<id>, part=<part>].per_card.<card>.mean`, `.ci99`): ring slope a2 1.78 [1.31–2.25], a3 1.73 [0.48–2.97],
a1c1 1.74 [0.95–2.53] pJ/B per hop, pooled 1.753 (predicted a2 2.3, a3 1.3); relay DRAM ÷ next shire 12.9, 13.0, 13.1×
(pooled 12.97; predicted 11.2, 13.5); relay through DRAM 111.3, 107.5, 129.9 pJ/B; L1 level 0.77, 0.75, 0.72 pJ/B,
pooled 0.759 (predicted a2 − a3 +0.18). Own scratchpad after zeros 2.11 [1.81–2.41], 2.10 [1.84–2.36], 2.55
[2.22–2.87] and after random 4.13, 4.04, 5.03 pJ/B (3 passes each), a3 − a2 at equal contents −0.012 and −0.084: the
E29 card difference is the contents (RL-h). Small messages cost more (shire-c4 − shire 1.51, 1.34, 1.47 pJ/B); a2's
leaving-the-shire step 5.17 [3.35–6.99] pJ/B. Spin − ring: pair 0.45, 0.32, 0.42 W; cross-shire rings 0.38–1.18 W.
**Caveats:** the s ↔ s+16 ring starved the sampler on every card in every pass (median 63–141 ms; aifoundry3 had
stayed at 22 ms in E29), so its 18 bursts were dropped (`dropped_bursts`). RL-g's scratchpad parts mix the two
contents and pass through their width; RL-h is the test (the prefill covers 87.5% of the bytes read). RL-f and RL-X4
were reduced without the catfull low edge and the V3-ABL-A FLOP side (`low_edge_source`, `flop_source` null). Dies at
block start and end: a2 71–77 °C, a3 55–59 °C, a1c1 60–66 °C, all idling at 600 MHz, with aifoundry2's leakage law on
every card.
**Report:** [On-chip communication](https://spacesheep.dev/@yaroslavvb/et-soc1-on-chip-communication); [Memory hierarchy](https://spacesheep.dev/@yaroslavvb/et-soc1-memory-hierarchy); [The energy manual](https://spacesheep.dev/@yaroslavvb/et-soc1-energy-manual) (A15); [Ridge points](https://spacesheep.dev/@yaroslavvb/et-soc1-ridge-points) (A19); [Hand it to the next shire](https://spacesheep.dev/@yaroslavvb/et-soc1-on-chip-relay) (A14).

## E44 — Idle heat/cool cycles: the idle law on three cards (2026-09-25 20:55 – 09-26 05:25, three cards)

**Question:** the idle law (12.6 W + 23.3 W·e^((T−80)/36)) was fitted on aifoundry2 alone with its leakage split
unidentified, and aifoundry3's shape and SRAM rail rested on single-bin readings. Does the law hold on each card, what
does the unsensed remainder do with temperature, and is busy leakage above Kanter's 30%? (PLAN3 V3-IDLE, 34 claims.)
**Method:** `tools/claims-v3/idle/block.sh <pass>`, one cycle per block: 2 s random-data fma bursts on 1,024 minions,
back to back, to 88 °C (a2, a1c1) or 90 °C (a3), at most 150 bursts, then 900 s with no launch, `ettelem` at 10 Hz.
Three cycles per card, all kept; the overnight IDLE-LONG passes were never scheduled. Whole-degree bins (n ≥ 20),
samples 1 s before to 6 s after a launch dropped, unsensed = board − the three rails, 99% t over cycles. Each band is
one card's (IDLE-0, a, e, f a3's; b, c, d, k a2's), so a1c1 is reported, not tested (A2.idle); A1 drops each cycle's
edge bins from IDLE-b.
**Raw data:** `V3/raw/<card>/idle/p{1,2,3}/` (`telemetry.jsonl.gz`, `heat.jsonl`, `launches.jsonl`, `marks.jsonl`,
`cycle.json`, `check.json`); reduced to `V3/results/idle.json` (`.log`).
**Result:** registered and all cards: PASS IDLE-c, e, f; FAIL IDLE-0, a, b, k; INSUFFICIENT IDLE-d, L. Every cooling
sample was at 600 MHz (`.idle_clocks`). IDLE-0: a3's die peaked at 90 °C in 3 of 3 cycles (after 126, 131 and 150
bursts), not the predicted 60–66 °C plateau (`.items[item=IDLE-0].per_card.aifoundry3.tmax_per_cycle`). IDLE-a: a3 −
the aifoundry2 law over 55–84 °C +1.01 [0.95–1.07] W (predicted +0.3 to +0.9), residual slope 0.036 [0.031–0.041]
W/°C; a1c1 +10.07 [9.73–10.40] W, slope 0.237 [0.228–0.246] (`.items[item=IDLE-a].per_card.<card>.offset_W`,
`.resid_slope_W_per_C`). IDLE-b: a2 sits on its own law, +0.04 [−0.15–0.22] W, not −0.23 ± 0.3
(`.items[item=IDLE-b].per_card.aifoundry2.info_cycle_offset_W`). IDLE-c: a2's unsensed slope over 74–88 °C 0.100
[0.056–0.145] W/°C, the rails' 0.525 [0.498–0.551] over 75–80 °C; a1c1 0.162 [0.081–0.244] and 0.767 [0.758–0.776]
(`.items[item=IDLE-c].per_card.<card>`). IDLE-e: a3's SRAM rail 0.066 [0.062–0.069] W/°C, at least 0.93 W above
aifoundry2's SRAM law in every bin 55–84 °C; a1c1 0.051 [0.046–0.057] (`.sram_slope_W_per_C`). IDLE-f: unsensed at
70 °C a3 13.69 [13.56–13.83] W, a1c1 17.46 [17.31–17.62], a2 14.81 (one cycle) (`.unsensed_70C_W`). IDLE-k: a2's T_L
profile is flat (best 32, 32, 16 °C; busy shares 0.17–0.80 within 0.005 W rms), so Kanter's 30% is not established
(`.items[item=IDLE-k].per_card.aifoundry2`).
**Caveats:** a2 cooled only to 67–77 °C in 15 minutes, so IDLE-d had a 73 °C bin in two cycles and stays open; IDLE-L
had no long pass. a1c1 (firmware 1.2.0) idles 10 W above the law, 42.71 [42.62–42.80] W at 73 °C against a2's 31.73:
per card, not a residual. All nine cycles ran in one night, not on two days as PLAN3 suggested (not a rule).
**Report:** [The energy manual](https://spacesheep.dev/@yaroslavvb/et-soc1-energy-manual) (A15); [The ET-SoC-1's DVFS loop](https://spacesheep.dev/@yaroslavvb/et-soc1-dvfs-leakage) (A11); [The Horace experiment](https://spacesheep.dev/@yaroslavvb/et-soc1-horace-experiment) (A4); [Why is the ET-SoC-1 low power?](https://spacesheep.dev/@yaroslavvb/et-soc1-why-low-power) (A5); [Limits of observability](https://spacesheep.dev/@yaroslavvb/et-soc1-limits-of-observability) (A2); [Anatomy of a memory access](https://spacesheep.dev/@yaroslavvb/et-soc1-memory-anatomy) (A1); [Power and temperature](https://spacesheep.dev/@yaroslavvb/et-soc1-power-temperature) (A3).

## E45 — The catalogue's temperature panel and the DRAM-row rows (2026-09-25 17:23 – 09-26 05:58, three cards)

**Question:** is the catalogue's 5% card gap (E27: aifoundry3 / aifoundry2 0.950) the card or its temperature; do
E28's DRAM-row rows, aifoundry2's only, hold elsewhere; are the store-over-load, L1-fill and fence/nop rankings real?
(V3-CAT, 14 claims.)
**Method:** `tools/claims-v3/cat/block.sh <pass>`, one pass per block through
`tools/claims-v3/cat/run_catalogue_t10.py`. Arm A, a 30-configuration panel at `--burst 3 --gap 4.5`: on a2 and a1c1
four warm passes (≤ 82 °C after heating to ≥ 76 °C) and four held at 88 °C (up to 5 heater launches before each
configuration); on a3 three cool passes (no heater) and three held at 89 °C (V3-IDLE's 90 °C less 1). Arm B, 23
configurations (dramrow2, tload/dram, tstore/dram, tload/scp, l1fill stride 32 and 64, fence, nop): three passes on a2
and a1c1, six on a3. Every block `ok`, every burst kept. Rules, Welch 99% on pass values: CAT-a, β = (hot − cool)/ΔT
of the panel's median log ratio, "card" if it excludes 0.21 %/°C, "temperature" if it excludes 0 only; CAT-b, cool a3
/ warm a2 in 0.951 ± 0.015 excluding 1; CAT-c, ANOVA p > 0.01 over seq/rowhit/rowmiss and rows − tload/dram excluding
0; CAT-e, tstore − tload in +3.2 ± 3 pJ/B on a3; CAT-f, fill / tensor load in 0.75 ± 0.10 excluding 1. a1c1 reports
CAT-b and e.
**Raw data:** `V3/raw/<card>/cat/p<N>/` (`runs.jsonl.gz`, `telemetry.jsonl.gz`, `marks.jsonl.gz`, `pass.json`,
`check.json`), `V3/raw/aifoundry3/cat/hold_c.json`; reduced to `V3/results/cat.json` (`.log`).
**Result:** registered FAIL CAT-a, b, e; CARD-DIFFERENT CAT-c, f (hold on a3 and a1c1, fail on a2); all cards the
same. CAT-a: a hotter die costs more, β a2 +0.484 [0.068–0.901] %/°C over ΔT 14.4 °C, a3 +0.301 [0.178–0.424] over
10.6 °C (both "temperature"), a1c1 +0.354 [−0.105–0.814] over 6.2 °C
(`.items[item=CAT-a].per_card.<card>.beta_pct_per_c`). CAT-b: cool a3 (58.8–60.4 °C busy) / warm a2 (76.2–76.6 °C)
0.985 [0.977–0.993], against 0.951 predicted and 0.953 on 23 Sep; a1c1 / a2, both warm, 0.999 [0.984–1.014]
(`.items[item=CAT-b].per_card.ratio`). CAT-c: the three row patterns are indistinguishable (ANOVA p 0.056–0.95) and
cost more than a DRAM tensor load, zeros +21.7 [11.6–31.8], +27.1 [22.9–31.4], +24.9 [9.9–40.0] pJ/B on a2, a3, a1c1,
random +21.4 [−26.2–69.0], +24.7 [13.8–35.5], +22.1 [14.9–29.3]
(`.items[item=CAT-c].per_card.<card>.<set>.rows_minus_tload`). CAT-e: tstore − tload includes 0 on every card (a3
+7.32 [−1.94–16.58] pJ/B). CAT-f: a2 0.77 [≈0.43–1.11], a3 0.80 [≈0.66–0.94], a1c1 0.83 [≈0.69–0.97]
(`.items[item=CAT-f].per_card.<card>.ratio_ci99_approx`). fence − nop, registered as within noise, is not: −0.82 to
−1.00 pJ/op on zeros, every interval excluding 0
(`.items[item=CAT-f].per_card.<card>.fence_vs_nop_expected_within_noise`).
**Caveats:** the hot holds fell short on a3 and a1c1 (busy 69.6–71.1 °C and 70.6–74.9 °C after 150 heater launches per
pass), shrinking ΔT; a2's ran at 87.9–96.4 °C. Stride-256 was not run (energy-manual-102 untested).
**Report:** [The energy manual](https://spacesheep.dev/@yaroslavvb/et-soc1-energy-manual) (A15); [Limits of observability](https://spacesheep.dev/@yaroslavvb/et-soc1-limits-of-observability) (A2).

## E46 — The energy manual's full catalogue, three passes on three cards (2026-09-25 17:28 – 09-26 04:58, three cards)

**Question:** does E27's catalogue reproduce configuration by configuration, is aifoundry3 still about 5% cheaper than
aifoundry2, and where does a third card fall? Not in PLAN3: after the machine fixes of 25 September the owner asked
for every measurement to be re-run on every card (Q50), and amendment A2.catfull fixed the rules before any of its
data.
**Method:** `tools/claims-v3/catfull/block.sh <KS>`, pass K, part S. A pass is `workloads/enercat/run_catalogue.py`'s
392 configurations (its two `dramrow/stride256K` ones left out, E28's `dramrow2` rows in) in the order
`random.Random(40<K>)` gives, cut into three parts of 130–131; each part is one block through
`tools/claims-v3/cat/run_catalogue_t10.py` with E27's timing (`--passes 1 --burst 3 --gap 4.5 --seed 40<K><S>`). a2
and a1c1 are heated to ≥ 76 °C before each part; a3 is not; no heater runs inside a part. Nine blocks per card, all
`ok`. Drops: on a2 and a1c1 a busy sample off 600 MHz or an implied clock outside 0.595–0.605 GHz, idle brackets never
tested; on a3 no clock rule. Items: CF-GAP, Welch 99% of a3 − a2 on each pass's median log ratio to a2's means, PASS
if wholly below 1 (a1c1 reported); CF-COVER, ≥ 3 complete passes with every configuration kept; CF-REP, the
pass-to-pass error, reported.
**Raw data:** `V3/raw/<card>/catfull/p<KS>/` (`runs.jsonl.gz`, `telemetry.jsonl.gz`, `marks.jsonl.gz`, `plan.json`,
`pass.json`, `preheat.jsonl`, `check.json`); reduced to `V3/results/catfull.json` (`.log`), with every configuration's
per-card and pooled values (`.configs`).
**Result:** registered PASS CF-GAP and CF-COVER, CF-REP reported; all cards: CF-COVER PASS, CF-GAP and CF-REP
reported. Every card kept all 1,176 bursts (392 × 3), none dropped or missing, every sample at 600 MHz
(`.items[item=CF-COVER].per_card.<card>`, `.idle_clock`). CF-GAP: a3 / a2 = 0.976 [0.961–0.990] over the pass-level
medians (3 v 3), against 0.950 on 23 Sep; a1c1 / a2 0.967 [0.950–0.985]
(`.items[item=CF-GAP].per_card.<card>.vs_aifoundry2`). Over the 392 configurations the median ratio to a2 is 0.972 on
a3 (10–90%: 0.916–1.004) and 0.962 on a1c1 (0.902–1.141) (`.ratios.per_card`). CF-REP, median / 90th-percentile
pass-to-pass standard error: a2 2.1% / 5.7%, a3 1.4% / 3.6%, a1c1 1.5% / 4.1% (23 Sep: 1.9% / 6.1% and 1.2% / 3.6%;
`.items[item=CF-REP].per_card.<card>`). Configuration by configuration the new values are 0.999 of 23 Sep's on a2
(10–90%: 0.932–1.095) and 1.023 on a3 (0.967–1.091) (`.vs_committed_23sep`).
**Caveats:** each card ran at its own temperature (busy dies 70.6–86.2 °C on a2, 57.2–58.8 °C on a3, 59.9–62.2 °C on
a1c1, block notes), and E45 finds the catalogue moving 0.3–0.5% per °C, so the card ratios mix card and temperature.
Idle between bursts, all at 600 MHz, was 32.7 W on a2, 25.8 on a3 and 34.4 on a1c1
(`.idle_clock.<card>.idle_w_by_mhz`); energies are over each card's own idle.
**Report:** [The energy manual](https://spacesheep.dev/@yaroslavvb/et-soc1-energy-manual) (A15), its catalogue; not in `V3/results/pagemap.json`, which maps PLAN3's items only.

## E47 — Minutes-long runs to a temperature cap on both cards (registered, not run)

**Question:** do the Horace long runs' times to the cap ("19–26 s / 107–167 s / never") and the equal flip power of
ones on 1,024 minions and random data on 384 hold on both cards? They rest on one aifoundry2 session (E12).
**Method, as registered:** PLAN3 §2 "V3-LONG" (horace-lowpower X3): `tools/ettelem/run_horace_long.sh` with three runs
per pattern per card (ones and zeros on 1,024 minions, random data on 384 and on 1,024), each up to ten minutes; item
LONG decides on the log time ratio, 99% Welch, per card.
**Not run.** Each run holds a card for minutes, against the lab's 10 s rule. PLAN3 made the experiment conditional on
the owner's waiver, and the owner's decision D1 kept the rule (`V3/README.md`, "Owner decisions"). No block, schedule
line or data exists; the seven claims of item LONG stay labelled one card, one session.
**Report:** [The Horace experiment](https://spacesheep.dev/@yaroslavvb/et-soc1-horace-experiment) (A4) keeps that label.

## E48 — Gathers, scatters and packed atomics on three cards (2026-09-26, 03:19–09:22, three cards)

**Question:** how fast, and at what energy, do the vector unit's indexed memory instructions run (gathers and scatters
of bytes, halves and words, their L1-bypassing `l` and global `g` forms, the 32-byte-block forms `fg32`/`fsc32`, and
the packed atomics `famoadd{l,g}.pi`) from each level of memory, against scalar atomics and a gather-add-scatter
update on the same address streams? Does the design's model of them hold, and are they exact on silicon (erratum
1.3)? The owner's Q52, run after each card's campaign queue had ended.
**Method:** `tools/claims-v3/gs/block.sh <KS>` (pass K = 1–3; S = 0 check, 1 energy, 2 rate), queued by
`tools/claims-v3/queue.sh tools/claims-v3/schedule-gs-<card>.txt`, on `workloads/enercat` built with `-DENERCAT_GS=ON`
into `build/enercat_gs` (the configurations in `workloads/enercat/gs_catalogue.py`, the analysis
`workloads/enercat/analyze_gs.py`). The C block runs one verify launch per configuration (159, the semantic probe
among them) and checks every gathered element, the table after scatters, every counter after atomics and the lane
order of the returned values; the E blocks run 101 configurations at 1,024 minions with E27's timing (`--burst 3 --gap
4.5`) under the 10 Hz sampler; the R blocks 57 at one minion, 32 in one shire and 32 spread. a2 and a1c1 were heated
to ≥ 76 °C before each E and R block and held above 74 °C between R configurations; a3 is pinned and was not heated.
"Random" is one random word on each of the 64 lines of a 4 KB tile, the tiles visited in a scrambled order, not
uniform addresses over the table. The items, drop rules and ranges were fixed in `tools/claims-v3/gs/README.md`
before any card ran it (`bde52e0`): unit the pass, 99% t over three passes per card, PASS inside the range on every
card, FAIL wholly outside.
**Raw data:** `V3/raw/<card>/gs/p<KS>/` (`block.json`, `check.json`, `plan.json`, `pass.json`, `configs.json`,
`code.sha256`, `run.log`, `runs.jsonl.gz`, and for E and R `telemetry.jsonl.gz`, `preheat.jsonl`); seven blocks per
card: a2 03:19–04:43, a3 04:50–06:13, a1c1 06:57–09:22. Reduced by `python3 tools/claims-v3/gs/reduce.py --data V3/raw
--out V3/results/gs.json --gs-out V3/results/gs-full.json` (`reduce_all.sh` writes `gs.json` and `gs.log`);
`gs-full.json` holds every configuration per card and pooled (`.combined`; `.combined_catalogue` over a2 and a3 only).
**Result:** GS-L1, GS-MH, GS-DRAM and GS-CHECK PASS on every card, GS-UC FAILS on every card; the rest is reported
(`V3/results/gs.log`). Rates are the same on the three cards to 0.02% (median ratio 1.000 over 157 configurations);
energies per element are a3 / a2 0.965 (10–90%: 0.937–0.994) and a1c1 / a2 1.085 (0.933–1.148) (`GS-CARD`). Word
gathers at 1,024 minions, pooled over the cards (`.items[item=GS-RATE].pooled`): from L1 (512 B per hart) 452 G
elements/s at 12.8 pJ each, 10.89 cycles per instruction per minion on every card (range 7–12, `GS-L1`); from L2
(4 KB per hart) and from the own scratchpad (16 KB) 27.4 G/s at 355 and 368 pJ, 1.15× the two-miss-handler bound of
23.9 G/s, with the second hart adding nothing (h2 / h1 1.000–1.001; `GS-MH`); from a scratchpad two hops away
10.2 G/s at 903 pJ; from DRAM (256 KB per hart) 1.19 G/s at 9.8 nJ, 76.4 GB/s of lines on every card (57–95 GB/s
registered, `GS-DRAM`). Word scatters: L1 452 G/s at 14.7 pJ, L2 23.5 G/s at 732 pJ, DRAM 0.42 G/s at 23.8 nJ. The
L1-bypassing gather `fgwl.ps` with both harts of one minion runs 1.03× one hart's rate, not the 1.6–2.4× that strict
per-thread order predicted (`GS-UC`). All 159 verify launches passed on every card, and all 2,937 timed launches per
card ended with `gsc_progress` 0 on every hart (`GS-CHECK`). When every lane of a scatter writes one word, lane 7 wins,
every time on every card (`GS-CONFLICT`, as predicted). Updates (`GS-ADD`, pooled): gather + `fadd.ps` + scatter
139 G/s at 0.036 nJ in L1, 18.2 G/s at 0.80–0.85 nJ in L2 or the scratchpad, 0.42 G/s at 22 nJ in DRAM; packed
atomics 12.7 G/s at 0.39 nJ on a shire table and 2.8 G/s at 1.7 nJ on a chip table; scalar `amoaddl.w` 12.8 G/s at
0.27 nJ, `amoaddg.w` 2.8 G/s at 1.1 nJ (the energy manual's spread global atomics: 1.9 G/s at 1.16 nJ).
**Caveats:** on a2 and a1c1 each energy block dropped the burst of the word gather from 64 KB per hart (its launches'
implied clock 0.594–0.597 GHz, just outside the 0.595–0.605 rule), so that configuration has values on a3 only;
every other configuration kept three passes on every card. Each card ran at its own temperature, so the card
ratios mix card and temperature, as in E46. The timed launches cannot see erratum 1.3's skipped elements; only the
verify launches can. A FAIL says the design's model is wrong, not the measured values. aifoundry3's queue was the
first card run of the g3log fix (E49): 641 host processes, no crash.
**Validation across machines:** every tested item was decided per card, on three cards in three machines (aifoundry2,
aifoundry3 and aifoundry1's card 1), each from its own three passes: GS-L1, GS-MH, GS-DRAM and GS-CHECK passed on each,
GS-UC failed on each (`V3/results/gs.json`, `.items[item=<GS-…>].outcomes`).
**Gap:** the word gather from 64 KB per hart (`gs/E/fgw.ps/dram-64K/rand/random/h2/mff/n1024`) lost every energy burst
on a2 and a1c1, three of three passes each: in each burst one launch's implied clock read 0.594 GHz (0.5941–0.5945),
just under the pre-registered 0.595–0.605 GHz band, while the telemetry read 600 MHz (`gs-full.json`,
`.cards.<card>.dropped`). The rule was not relaxed: that row's energy (9.2 nJ per element) is a3's alone, and every
page that shows it says so; its rate equals the 256 KB (DRAM) row's.
**Report:** since 27 September, [the energy manual](https://spacesheep.dev/@yaroslavvb/et-soc1-energy-manual) (A15):
§3.1's last table (the L1 rows: bold pooled over a2 and a3, `.combined_catalogue`'s rule, with a1c1 in the per-card
column), §4.3 (patterns, masks, element sizes, lane conflicts, scaling), a new §4.4 "Irregular access: gathers and
scatters by level" and six rows of §6 (the packed and scalar atomics, scatter-add), all pooled over the three cards; [the
memory hierarchy](https://spacesheep.dev/@yaroslavvb/et-soc1-memory-hierarchy) (a section "Irregular access", two charts,
rules for kernels, and the spec sheet's random-element column); [influence functions](https://spacesheep.dev/@yaroslavvb/et-soc1-influence-functions)
(S3 measured, K3, K6, §6); and [the hub](https://spacesheep.dev/@yaroslavvb/et-soc1-limits-of-observability)'s chart
of events (eight gathered, scattered and atomic events). Chain: `tools/ettelem/build_energy_manual.py` pools
`gs-full.json`'s pass values into `manual.json` `gs` (the rows from `tools/ettelem/gs_levels.py`);
`render_catalogue.py` and `render_energy_manual.py` write 03a, 04, 04a and 06; `workloads/memhier/analyze.py --embed`
embeds it (`--manual`, by default the manual's `manual.json`); `sync_hub_data.py` and
`docs/reports/data/2026-09-25-influence-on-et/make_analysis.py` read it. No page claim of E48 is in
`V3/results/pagemap.json` (written before E48), so the hub's scoreboard does not count it.

## E49 — The runtime's log-level race, reproduced without a card (2026-09-25, 23:12, aifoundry2's CPU)

**Question:** is aifoundry3's host crash about 1.08 s into 1 launch in 100 (14-card-behaviour.md, "Traps") the
g3log level-map race that four core dumps point to, and does registering the levels first remove it?
**Method:** `tools/g3log-race/race.cpp` against the lab's `/opt/et/lib/libg3log.so`: per trial, reset g3log's
levels, then release 4 waiting threads that each make the first `g3::logLevel()` call for `VERBOSE_MID`, as
libetrt's thread-pool workers do; count the trials after which the map does not hold exactly one more level.
Three runs of 20,000 trials without registration, three with the level registered first; no card is opened.
**Result:** 1,087, 1,358 and 1,412 of 20,000 trials corrupted the map without registration; 0 of 60,000 with it.
Every `workloads/*/host/main.cpp` now calls `registerRuntimeLogLevels()` first in `main`.
**Caveats:** the test shows the mechanism and the fix, not the crash rate on aifoundry3, which depends on its
`-O3` runtime's timing. Binaries built before the fix, the version-3 campaign's among them, keep the crash; the
gather/scatter host (E48) is the first card program built with it.
**On the card (26 Sep):** aifoundry3's E48 queue ran that fixed build for 641 host processes (3,096 launches,
04:48–06:13) with no crash and no core dump, where the unfixed binaries' rate of about 1 in 100 predicts 6.4
(Poisson chance of none: 0.2%). aifoundry2's and aifoundry3's other host builds were rebuilt with the fix once
their queues had ended.

## A note on E10, re-analysed for Q20

The governor transitions in [16-dvfs-and-leakage.md](16-dvfs-and-leakage.md) are **not** a new experiment.
They are E10's telemetry re-read by `tools/ettelem/analyze_dvfs.py`, which classifies each of the 36 clock
changes against the firmware's two thresholds; the seven down-steps that neither threshold explains on the sampled
values are labelled unattributed. Nothing is fitted.

