# fma_toggle: how many nets flip in the multiply-add unit, per data pattern

The ET-SoC-1 draws 38 W multiplying matrices of zeros and 66 W multiplying random ones, at the same speed
(docs/reports: horace-experiment). This bench asks the RTL why. It drives eight copies of core-et's
`txfma_top` (the 7-stage fused multiply-add unit, one per vector lane) with the exact micro-op stream of a
16x16x16 `TensorFMA32` and counts what switches.

> **Read this before quoting `nets`.** The headline figure of **21,331 toggles per random multiply-add**,
> published in `docs/reports/data/2026-09-21-horace-aifoundry2/toggles.json`, is **a count of RTL names
> under one version of Verilator, not a count of wires.** Re-run on the same RTL and the same card-dumped
> tiles it is 6,900–7,000 under Verilator 5.052, and about 900 once each physical net is counted once.
> [The settled count](#the-settled-count) has the ladder and the method. Every per-toggle energy fitted
> against `nets` carries whichever number it was fitted to.

What is modelled, from the RTL:

- **Order of operations** (PRM 9.4, `vpu_tensorfma.v`): for each B row k, for each A row i, two micro-ops
  (C columns 0-7, then 8-15), each `c = a*b + c` on 8 lanes. One micro-op per cycle, 512 per op, then a
  34-cycle gap (the card measures 546 cycles per op for every data pattern).
- **Zero gating** (`vpu_ctrl.v`, `ex_fma_gate_mask`): on an accumulate pass a lane gets no valid when its A
  or B operand word is zero. The unit's pipeline registers are enabled by the valid bit of their stage, so a
  gated lane clocks nothing and flips nothing. The first op of a launch is a multiply pass and is not gated.
- **Clock gate** (`vpu_lane.v`): the unit's clock runs while micro-ops arrive and for 7 cycles after.
- Results return to the C registers after 7 cycles, as in the chip, so later micro-ops see real accumulator
  values. Every result is checked against software (`+check`): 8,192 of 8,192 match for random data.

What is counted, per op and per minion:

| Counter | Meaning |
| --- | --- |
| `nets` | Toggles of every named net and register bit inside the eight units (Verilator toggle coverage, both edges, clocks excluded). **An RTL name, not a wire**, and version-dependent: see below |
| `by_block` | The same, by RTL file: the Booth/Wallace multiplier tree, the adder, the shifters, ... |
| `ff_clocked` | Register bits that received a clock edge with their enable high (`ff_acct.sv` replaces `libs/registers`) |
| `ff_present` | Register bits the unit's clock reached at all that cycle, enabled or not: the denominator of `ff_clocked`. 838 per lane in this RTL |
| `ff_toggles` | Register bits that changed |
| `bus` | Toggles of the operand words presented to the lanes (activity outside the unit: register-file reads, bypass) |
| `lane_valid` | Lane-cycles with a valid multiply-add, out of 4,096 |

Limits: RTL, not a netlist, so a "net" is a named signal (module ports are counted at each level of the
hierarchy, which for the compressor cells is a factor of two: see below); zero-delay simulation, so no
glitches; the Erbium-branch RTL is the same core lineage as the ET-SoC-1 but a later revision; only the
multiply-add units are simulated, not the scratchpad, the register file or the tensor state machine around
them.

## Building it

Verilator 5 is the only dependency, plus numpy for `tiles.py`.

**On a lab host (Ubuntu).** aifoundry2 already has one, built from source at `~/.local/verilator`
(5.042, which the Makefile's default `VERILATOR` points at):

```
make CORE_ET=../../external/core-et          # builds obj_dir/Vtb, about 1 minute
```

**On a Mac (verified on the Intel, 26 Oct 2026, macOS 15 / x86_64).** There is no Homebrew formula that
gives Verilator 5 here; conda-forge does, in user space, with no admin rights and nothing on the system
path:

```bash
# micromamba, ~10 MB, into ~/.local
curl -fsSL -o /tmp/mm.tar.bz2 https://micro.mamba.pm/api/micromamba/osx-64/latest   # osx-arm64 on Apple silicon
tar -xjf /tmp/mm.tar.bz2 -C /tmp bin/micromamba && install /tmp/bin/micromamba ~/.local/bin/

export MAMBA_ROOT_PREFIX=$HOME/.local/micromamba
micromamba create -y -n verilator -c conda-forge verilator numpy       # ~1.4 GB, 3 minutes
$MAMBA_ROOT_PREFIX/envs/verilator/bin/verilator --version              # Verilator 5.052
```

Two macOS-only wrinkles, both handled by the Makefile's `CXXOVERRIDE`:

- conda-forge's Verilator writes `CXX = x86_64-apple-darwin13.4.0-clang++` into the generated makefile.
  That wrapper ships in the env but is not on the path, and it wants the env's sysroot. Pass the system
  compiler instead.
- the archiver it calls (`x86_64-apple-darwin13.4.0-ar`) *is* needed and *is* only in the env, so the env's
  `bin` must be on `PATH` for the build.

```bash
export PATH="$HOME/.local/micromamba/envs/verilator/bin:$PATH"
make       CORE_ET=../../external/core-et VERILATOR=$HOME/.local/micromamba/envs/verilator/bin/verilator \
           CXXOVERRIDE=/usr/bin/clang++          # obj_dir/Vtb        ~3 min
make trace CORE_ET=../../external/core-et VERILATOR=$HOME/.local/micromamba/envs/verilator/bin/verilator \
           CXXOVERRIDE=/usr/bin/clang++          # obj_dir_trace/Vtrace
make settle_count CXX=/usr/bin/clang++           # the VCD counter
```

## Running it

```
python3 tiles.py randn /tmp/t.hex --iters-before 1000
./obj_dir/Vtb +tiles=/tmp/t.hex +ops=4 +warm=1 +check=8    # ACCT {...} line, CHK lines, final C
python3 toggles.py --out toggles.json --tiles-dir <dir of tiles dumped by sparsity_host --dump-tiles>
```

`toggles.py` runs each pattern at four points of a launch (accumulators at 0, 1e3, 1e5 and 4e5 ops) and
averages the last three.

## The settled count

`nets` counts an **RTL name**, once for every value the simulator's scheduler assigns it. Three things
inflate it above the number of wires that switch, and they are separable. Run the tracing build, which
carries the same stimulus and the same coverage counter and stops at the end of the trace window, so both
counters cover exactly the same cycles:

```bash
./obj_dir_trace/Vtrace +tiles=/tmp/t.hex +ops=4 +warm=1 +dump=/tmp/t.vcd +dump_uops=64 \
                       +verilator+coverage+file+/tmp/cov.dat
python3 scope_modules.py /tmp/t.vcd --rtl ../../external/core-et/rtl --extra ff_acct.sv tb.sv --out scopes.tsv
./settle_count /tmp/t.vcd --modmap scopes.tsv --out /tmp/settled.json
python3 recount.py --out recount.json --tiles-dir <tiles> --uops 64 --jobs 5   # all of it, per pattern
```

`settle_count` reads the VCD and counts four ways. `scope_modules.py` resolves each VCD scope (an
*instance* name) to the RTL module it instantiates, by reading the instantiation statements out of the
Verilog, so the split is comparable with the coverage counter's split by file.

| Count | What it is |
| --- | --- |
| `nets_vcd_raw` | every value change in the VCD, per RTL name — the coverage counter's unit, re-derived |
| `nets_settled` | changes between consecutive **settled** samples, at most one per bit per cycle, per RTL name |
| `nets_ids` | the same, once per VCD identifier: merges only the aliases Verilator itself collapsed |
| `nets_distinct` | the same, once per **distinct waveform**: two bits that change in exactly the same cycles are one net. The physical-net proxy |

The settled sample is the end of each negedge time step: the testbench drives operands at the negedge and
clocks registers at the posedge, so everything combinational has settled there. `settle_count` finds the
VCD's time unit from the first two timestamps rather than assuming one.

**What the four counts say** (random fp32 tiles the card ran, 21 Sep seed 1, accumulators at 1e3 ops;
`docs/reports/data/2026-10-26-toggle-recount/`):

| Per random multiply-add | |
| --- | --- |
| 21,331 | `nets`, as published 21 Sep — Verilator **5.042** on aifoundry2 (re-measured 26 Oct: 21,379) |
| 6,886 | `nets`, same bench, same tiles, Verilator **5.052** on the Intel |
| 7,280 | `nets_vcd_raw` |
| 6,978 | `nets_settled` |
| 3,900 | `nets_ids` |
| 904 | `nets_distinct` |

- **The 3.1x between the two Verilator versions is entirely inside two modules.** `txfma_csa` and
  `txfma_4_2_compressor` count 7.9x and 9.0x higher under 5.042; every other module agrees within 1%. Those
  two are the compressor cell and the full adder inside it, whose 64-wide carry chain 5.042 re-evaluated
  several times per cycle and counted each time. This is the defect the chip-diagram research named ("counts
  transient values while the model settles", `docs/reports/data/2026-09-27-chip-diagram/research/tensorfma32.json`,
  fact `tfma.lab`) — confirmed, and localised. Under 5.052 it is gone: `nets_settled` and `nets` differ by 0.2%.
- **The hierarchy counts each compressor net exactly twice.** `txfma_4_2_compressor` instantiates two
  `txfma_csa`, connected positionally, so its nine nets (`x0..x3`, `cin`, `cout`, `c`, `s`, `s0`) carry
  eighteen names and Verilator gives them nineteen VCD identifiers, of which only one pair is merged.
  `txfma_4_2_compressor_array` names six of them a third time. This is the "double counting of txfma_csa
  inside txfma_4_2_compressor" suspect — confirmed, and it is exact, not approximate.
- **`nets_distinct` lands near the gate-level figure.** 904 per multiply-add against the 1,244 physical
  toggles a zero-delay gate-level simulation of the chip's own netlist reports (`tfma.glitch`), 1,871 with
  gate delays. An identical-waveform merge is a lower bound on physical nets, so 904 < 1,244 is the right
  side to be on, and the two agree far better than 21,331 does with anything.

`ff_clocked` is disputed the same way: 602.5 register bits per multiply-add here against 1,586 of 1,851
flip-flops in the chip's netlist. Part of that is the denominator — **this RTL has 838 register bits per
lane** (`ff_present`), not 1,851, so the *fractions* are 72% and 86%, not 2.6x apart. The rest is a
difference between the designs, not between the counters.

## Files

| File | |
| --- | --- |
| `tb.sv` | the stimulus: 8 lanes of `txfma_top`, the TensorFMA32 micro-op order, lane gating, the clock gate. `+dump=<f>` opens a VCD window of `+dump_uops` cycles and ends the run there |
| `ff_acct.sv`, `acct.cpp` | drop-in `libs/registers` models that report clocked, present and changed bits |
| `tiles.py` | operand tiles for one pattern, or the raw tiles the card ran |
| `toggles.py` | the coverage counter, per pattern, into `toggles.json` |
| `settle_count.cpp` | the VCD counter: raw, settled, per identifier, per distinct waveform, by module |
| `scope_modules.py` | VCD scope (an instance path) to RTL module, from the Verilog's instantiations |
| `recount.py` | all five counts for every pattern, in `toggles.json`'s schema plus the new fields |
