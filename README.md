# nekko: ET-SoC-1 prototyping

A workspace for prototyping on AINekko / AI Foundry's **ET platform**, the open-sourced Esperanto
**ET-SoC-1**: 1088 RISC-V minion cores with custom vector and tensor units. Work runs on the
`sys_emu` simulator first, then on real cards in the AI Foundry lab.

**Looking for results rather than code? Start with [docs/findings/](docs/findings/README.md).** It is a
self-contained write-up of everything measured on the card: what a workload's data does to power and
temperature, the model that predicts it, why the chip is low power against an A100, and — for every number —
which experiment produced it and which raw file holds the evidence. The published reports are indexed on the
public hub, [Limits of observability](https://spacesheep.dev/@yaroslavvb/et-soc1-limits-of-observability#reports);
`docs/findings/04-artifacts.md` records every space, its uuid and its visibility.

**New machine? Start with [docs/getting-started.md](docs/getting-started.md).** It covers the current status,
cloning, connecting to the lab machines over Tailscale, the hello worlds, rerunning the benchmark, and
republishing the reports. Its section 8 shows how to regenerate every report from the raw data committed here, and
section 9 lists the pinned upstream versions.

- `docs/et-soc1-notes.md` is a condensed guide: architecture, programming model, the memory-coherency trap,
  the FOSDEM "zero to matmul" optimisation ladder, silicon errata, and simulator flags.
- `docs/report/` is the first shareable write-up, published at https://spacesheep.dev/@yaroslavvb/et-soc1-testdrive.
  Edit `index.html`, then run `npx --yes spacesheep deploy docs/report --space 16732875-c03e-434d-a643-7a432586c7f7`
  to update the same space. Without `--space` the CLI creates a new one, and its `.spacesheep.json` pin files are gitignored.
- `docs/reports/2026-09-18-et-soc1-matmul-efficiency.html` measures tensor-unit matmul speed and energy efficiency
  on aifoundry2's card against the A100 (`kernels/mmbench`, `launchers/mmbench`, `make bench-power`). Its raw data is in `docs/reports/data/`.
- `docs/reports/2026-09-18-et-soc1-memory-hierarchy.html` measures each memory level's size, latency, bandwidth and energy per
  byte on the same card, next to published A100 numbers (`workloads/memhier`; public space
  https://spacesheep.dev/@yaroslavvb/et-soc1-memory-hierarchy, uuid `4b6e0a37-808d-4fc9-8001-555125733c46`).
- `docs/reports/2026-09-18-et-soc1-on-chip-communication.html` maps the 32 shires on the 6x6 mesh and measures the chip's
  message passing on the same card, next to how GPUs communicate between cores: TensorSend/Recv by distance and size,
  hardware reduction trees, credit counters, barriers, and energy per byte. It uses `workloads/nocbench`, and is a public
  space at https://spacesheep.dev/@yaroslavvb/et-soc1-on-chip-communication, uuid `ab8e1b2b-de17-44f4-8645-006fa960e349`.
- `docs/reports/2026-09-18-et-soc1-sparsity.html` measures what aifoundry3's card does with zeros (tensor-unit zero-skip,
  masked TensorLoads, a batch-1 sparse layer, divergent work items) and lists the scenarios where the chip could beat an
  A100, with the benchmark that would settle each. It uses `workloads/sparsity`, and is a public space at
  https://spacesheep.dev/@yaroslavvb/et-soc1-sparse-compute, uuid `5abf6014-8de0-4e82-8744-5676bac6453e`.
- `docs/reports/2026-09-19-et-soc1-memory-anatomy.html` takes single memory accesses apart on aifoundry2's card: latency
  by stage (L2, L3 home shire, mesh hops, memory shire, DRAM row state, refresh; the L3 model holds to ±4 cycles for 1,498 of
  1,500 lines), and energy per load by power rail (minion cores, SRAM, NoC, DDR side). It uses `workloads/memprobe`;
  `docs/research/` holds the survey of counters, DRAM mapping and power telemetry it builds on. Its energies per byte are
  superseded by the energy manual's (below). Public space https://spacesheep.dev/@yaroslavvb/et-soc1-memory-anatomy,
  uuid `2bf74fd1-fd7f-4e19-8e35-6168ae42657c`.
- `docs/reports/2026-09-20-et-soc1-limits-of-observability.html` is the ladder of what can be observed on the chip, from board
  power down to a flip-flop per cycle in the RTL, with what each step would take. Its sources (a survey by seven AI research agents,
  Claude subagents run by the author, each covering one layer of the manuals, firmware, RTL and tools, with each key claim then
  checked by two further AI agents) are in `docs/reports/sources/2026-09-20-limits-of-observability/`;
  `tools/ettelem/sync_hub_data.py` writes the data file's computed blocks from the analyses (`--check` reports a stale
  file), then `scripts/build-report.py limits-of-observability docs/reports/sources/limits-of-observability.data.json <out>`
  assembles the page.
  **Second edition (2026-09-23): the hub for every measurement report**, with the power meter chain, the unmetered remainder
  attributed by regression, the Moortec PVT sensors and the DDR-rail droop meter, and a 20-rung improvement ladder.
  Public space https://spacesheep.dev/@yaroslavvb/et-soc1-limits-of-observability, uuid `2ea37420-67b9-484e-9d4c-581e8a9f0323`.
- Observability tooling that came out of that survey, none of which changes a card:
  - `workloads/traceprof` + `scripts/trace-flamegraph.py`: a device flame graph in minion cycles from a kernel's profile regions.
  - `rtl-sim/pmu_carry`: the original PMU RTL under Verilator; it reproduces and explains the late bit-7 carry of `hpmcounter3`.
  - `rtl-sim/fma_toggle`: eight copies of the fused multiply-add RTL replaying a TensorFMA32 on the card's own operands; counts
    register bits clocked and nets toggled per data pattern (the Horace experiment's power model).
  - `patches/0003-pmc-configure-syscall-353f20e.patch`, `scripts/build-minion-fw.sh`, `workloads/pmcsel`: a firmware syscall
    that lets a kernel choose counter events, built and verified in `sys_emu`. A card would need a signed image to run it.
- `docs/reports/2026-09-20-et-soc1-power-temperature.html` lists every way to measure power, energy and temperature on the card,
  and shows a load step through all of them: power that rises with die temperature (about 0.8 W per °C under load; the later
  idle law gives 0.65 W per °C at 80 °C), idle power that depends on recent load, rail readings that lag (the PMIC's running average, τ ≈ 1.2 s), and a 34-shire
  on-die voltage map. It uses `tools/ettelem`, a telemetry client on the management library
  (`tools/ettelem/run_thermal.sh`). Public space https://spacesheep.dev/@yaroslavvb/et-soc1-power-temperature, uuid `acee5c6d-56c0-45e7-aa97-ce11af37bdd8`.
- `docs/reports/2026-09-20-horace-experiment.html` reproduces Horace He's "predictable data" matmul result on this chip and takes
  it apart (20–22 September; section 10 repeats it on aifoundry3's card). Same clock and FLOPs for every operand
  pattern, but 38 W on zeros, 47 W on ones and 63 W on random values, with every run launched from the same die temperature (`tools/ettelem/run_horace_strict.sh`); heating per
  FLOP; a power model from RTL switching activity of the multiply-add unit (`rtl-sim/fma_toggle`, 0.50 W rms leaving one pattern
  out); the speed
  effect from a cool die (`run_horace_cold.sh`); ten-minute runs with a 90 °C cap (`run_horace_long.sh`: random data gets from 80 to
  90 °C in 19 to 26 s, ones in about two minutes, zeros never); a three-line model from flip rates to temperature
  (`tools/ettelem/flip_thermal_model.py`: leakage 23 W at 80 °C, thermal stages out to 2,500 s; on the later runs of the same session, which it was not fitted to, the time to 90 °C is
  predicted to 9% in the median and 23% at worst; on a different afternoon with new matrices, 7% and 65% (the DFT pair, whose
  power it put 2.8 W low); ten-minute end temperatures come out 3 to 5 °C hot: `tools/ettelem/validate_flip_model.py`);
  and structured matrices (Hadamard, DCT, butterfly, kaleidoscope, ...: `tools/ettelem/make_tiles.py`) whose power was predicted to
  0.92 W rms before they ran. `tools/ettelem/predict_heat.py --model .../model.json --tiles my.bin` prices a custom workload: flips,
  watts, heating curve, time to a cap, sustainable duty cycle. GIFs: `docs/reports/horace-heating.gif`, `horace-heating-6.gif`,
  `horace-long.gif`. `tools/ettelem/finish_horace.sh` rebuilds the Horace analyses, model, GIFs and pages from
  `docs/reports/data/2026-09-21-horace-aifoundry2/`.
  Public space (the user's choice) https://spacesheep.dev/@yaroslavvb/et-soc1-horace-experiment, uuid
  `da445a93-7be3-42c2-b9be-4992fa4a3b62`, deployed as a folder (`index.html` plus the GIFs), so the GIFs have public addresses such as
  https://da445a93-7be3-42c2-b9be-4992fa4a3b62.spacesheep.app/horace-heating.gif. Always deploy it as that folder: a
  single-file deploy drops the GIFs. A folder deploy can leave the space private; put it back with
  `spacesheep share <uuid> --visibility public` and check `spacesheep list` after every deploy.
  Section 10 repeats the whole experiment on aifoundry3's card: the flip model fitted here, applied to that card
  unchanged, is off by a flat 8%, and one scale factor of 0.92 brings it to 0.20 W rms over a 1.9-25 W range
  (`tools/ettelem/compare_cards.py`, `build_cards_data.py`; raw data
  `docs/reports/data/2026-09-22-horace-aifoundry3/`).
- `docs/reports/2026-09-21-why-low-power.html` asks why the chip draws so little next to an A100, using Esperanto's own equation
  (power = C V² f + leakage) and ablations on the card (`tools/ettelem/run_ablation.sh`, `ablation.cfg`, `analyze_ablation.py`):
  an integer loop on all cores costs 1.5 W, int8 multiply-adds 0.32 pJ against 6.0 pJ for fp32, power is linear in active cores,
  the 0.62 V / 800 MHz point costs 2× the switching power of 0.52 V / 600 MHz, and leakage is 23 W at 80 °C. Per FLOP of dense
  matmul the A100's bf16 tensor cores are 5.4× more efficient than this card's fp32 and 2.6× more than its fp16; against the
  A100's fp32 CUDA-core datasheet figure (19.5 TFLOPS at 400 W) this card is about 2.9× better on random data and 3.4× on
  the matmul benchmark's ±1/±2 operands. Notes and sources in
  `docs/research/why-low-power.md`. Public space
  https://spacesheep.dev/@yaroslavvb/et-soc1-why-low-power, uuid `baede20c-57d9-4e01-8157-2014670dd8cf`.
  Both are assembled by `scripts/build-report.py` from `docs/reports/sources/`. TeX between `$$` or `\( \)` in a
  report body is rendered to standalone SVG at build time by `scripts/tex2svg.js` (mathjax-full, pinned to 3.2.1 in
  `package.json`: run `npm ci` once at the repo root): the publishing host blocks external scripts, so a runtime MathJax from a CDN leaves every
  equation as raw TeX. After any `spacesheep deploy`, re-check that the space is still public: folder deploys have
  changed visibility in both directions (`docs/findings/04-artifacts.md`, "Publishing notes").
- `docs/reports/2026-09-22-dvfs-leakage.html` checks six claims about DVFS loops and leakage suppression, from a
  conversation with David Kanter (MLCommons) on 20 September 2026 (private notes), against this chip: the governor
  reads a measured PMIC wattage rather than estimating power from activity counters, and from a cool die it hunts
  across the 65 °C threshold, which has no dead band (36 transitions analysed, `tools/ettelem/analyze_dvfs.py`); the
  open (Erbium) RTL's per-minion sleep controls are tied off and no firmware drives them; a wake-up probe finds no
  array power gating (`gen_ops.py wakeup`); and leakage is 36% of a busy card against his 5–30%. The governor was
  read at et-platform `353f20e`; the cards' own trace strings match an older firmware build. It now also covers the three lab machines: aifoundry3's service processor reports a
  static TDP of **0 W** (the driver reports 65 W on every machine), which makes the governor's step-up test
  unreachable and holds that card at 600 MHz for as long as its flashed TDP stays at zero, and aifoundry1's two cards cannot be opened because its
  kernel module's `srcversion` does not match its `libDM.so`. Public space (the user's choice)
  https://spacesheep.dev/@yaroslavvb/et-soc1-dvfs-leakage, uuid `171dcd4a-5b6d-49d3-aca0-db4980fabfa5`.
  Read a card's governor inputs with `tools/etcfg` (driver ioctl) and `build/ettelem/ettelem config`
  (service processor); both are read-only.
- `docs/reports/2026-09-22-hot-line.html` follows up a Discord claim that the shire hosting a contended global
  atomic gets 6% of its fair share. It does not: the atomic is shared to within half a percent. What that
  shire loses is its **own** memory path, which stops dead - 384 operations and then nothing, identical at 5, 10,
  40 and 100 ms windows, while the mesh retires six million atomics. The threshold is a cliff at 24 remote
  requesters, under one shire's worth, and it is exactly where the shire cache reaches its 10-cycles-per-atomic
  floor. ET-SoC Errata 4.1 (RTLMIN-6207) and 4.2 (RTLMIN-6214) describe it, rate the impact "Low", say
  `l3_yield_priority` does not fix the same-address case, and are both Postponed. Pacing the remotes to one
  atomic per 10,000 cycles gives the host shire back half its bandwidth for 4% of theirs. New probe
  `workloads/nocbench --test hotline` plus `run_hotline.sh`/`analyze_hotline.py`; power from
  `tools/ettelem/run_hotline_power.sh`. The sweeps reproduce on aifoundry3: the stalled host's 384 and 192
  operations exactly, the host's count in the other rows within 2% except one (240 operations against 208). Public space
  https://spacesheep.dev/@yaroslavvb/et-soc1-hot-line, uuid `ac439287-4503-42c7-88e7-b5d3e3b64b06`.
- `docs/reports/2026-09-22-on-chip-relay.html` answers whether on-chip communication can beat main memory for a
  real computation. A chain of stages that hands each stage's output to the next shire's scratchpad (the next
  shire ID, 3.5 mesh hops away on average) instead of writing it to DRAM runs **12.3× faster and uses 12× less
  energy per byte, on the same watts**; keeping it in the shire's own scratchpad is 30.7×. Both reproduce on aifoundry3. The boundary is sharp:
  below the 32 MB L3 the DRAM route runs at 280-410 GB/s and the hand-off buys nothing, and at 32 MB per
  buffer DRAM falls to 48 GB/s and stays there out to 256 MB. The lead holds to about four adds per element and
  then shrinks with each quadrupling of the arithmetic: 4.1× at 8 flops per byte moved, 1.5× at 32. Which shire
  receives the slab moved the bandwidth by up to a quarter over the five ring offsets tried (593-733 GB/s), falling
  with the longest hand-off in the ring, not the mean distance; each hop also costs about 1.5–2.2 pJ per byte (heat
  per millimetre). New workload `workloads/onchip` (`--test probe` and `--test relay`) with `run_onchip.sh`,
  `analyze_onchip.py` and `tools/ettelem/run_onchip_power.sh`. Public space
  https://spacesheep.dev/@yaroslavvb/et-soc1-on-chip-relay, uuid `8678d49d-3f0c-49be-b08a-5528de8ece3c`.
- `docs/energy-manual/` is **the energy manual**: what every kind of operation on the card costs in joules, arranged
  so a workload's energy can be built from parts - the card at rest (12.6 W fixed plus leakage e-folding every
  36 °C), an awake minion (2 mW), every instruction on zeros/constant/random data (integer add 6 pJ on zeros and 9 on
  random, float add 23, 8-lane FMA 27 on zeros and 56 on random), bytes at every level (L1 0.5 pJ/B, own scratchpad 2-8, DRAM 90-140,
  the L1 write-back path to DRAM 250-350), bytes between shires, synchronisation, worked compositions, and the
  second card at 0.95× the first over 56 entries. Measured by the new `workloads/enercat` (`run_enercat.sh`,
  `analyze_enercat.py`); every table is assembled from its data file by `tools/ettelem/build_energy_manual.py`
  and the pages rendered by `render_energy_manual.py`, so no number is typed by hand. The second edition
  (`workloads/enercat/run_catalogue.py`) measures every one of the 161 instructions the silicon executes in U-mode
  three times in shuffled order on both working cards (pass-to-pass error 1.9% median, second card 0.95× over 386
  configurations), and separates a memory access into its parts: one mesh hop is 0.75 pJ/B on zeros and 1.81 on
  random data fitted over 1–8 hops (2.3 over 1–6 hops, in line with heat per millimetre; the difference is bits that
  change between flits plus ones carried), a 64 B line fill into the L1 is about 100-205 pJ (zeros to random data), the DRAM row
  pattern makes no difference, the SRAM rail leaks 1.6 W at 67 °C rising to 2.6 W at 82 °C, and each class of
  operation is split across the minion, SRAM and mesh rails. The third edition puts a confidence bar on every
  entry - mean [lo-hi] over the three passes on two cards, and three warm reruns per card of the relay, the hot
  line, the rings and the levels (`tools/ettelem/run_reruns_warm.sh`, `run_rings_levels_power.sh`,
  `analyze_reruns.py`; bursts in which aifoundry2's governor moved the clock, or in which the workload starved the
  service processor that reads the meter, are dropped) - and attributes what a workload adds on no rail sensor (`tools/ettelem/fit_unmetered.py`,
  which writes the fit; the idle 15 W is not split): 18-20% delivery loss on the minion rail, 5% on SRAM, 26-29% on the mesh,
  about 70 pJ per DRAM byte off-rail, plus a
  DRAM-activity meter from the memory shires' Moortec voltage monitor (0.87 mV per off-rail DRAM watt).
  Published, public, at https://spacesheep.dev/@yaroslavvb/et-soc1-energy-manual, uuid `cc3cb1d6-51cf-420b-a165-7d8629904d97`.
- `docs/reports/2026-09-24-heat-per-mm.html` ("Heat per millimetre") measures what moving a bit one millimetre across
  the mesh costs, against Dally's "~100 fJ/b-mm": a random bit costs 36 fJ per mm on the mesh rail with free links and
  50 on a loaded mesh (47 and 73 on board power), and ones carried cost energy, not only bits that change between
  flits (`workloads/enercat/run_wire.py`, `analyze_wire.py`, `tools/ettelem/build_wire_report.py`; checked before
  publication by a workflow of six AI agents, `docs/reports/data/2026-09-24-wire-energy/review/`). Public space
  https://spacesheep.dev/@yaroslavvb/et-soc1-heat-per-mm, uuid `5602ff62-878f-4db6-b703-02061000d9ce`.
- Two briefs of 22 September, hand-written HTML imported from their published pages:
  `docs/reports/2026-09-22-et-soc1-spatial-temperature-brief.html` (the die's 35 temperature sensors, how the firmware
  reduces them to one number, and what a spatial heat map would need; https://spacesheep.dev/@yaroslavvb/et-soc1-spatial-temperature-brief)
  and `docs/reports/2026-09-22-et-soc1-l2-mainline-starvation.html` (an analysis of a contention result reported in
  Discord, written before the hot-line report re-measured it; since 25 September a pointer page to the hot-line
  report and On-chip communication, with the brief as corrected on 24 September kept in git at `49dd0c8`;
  https://spacesheep.dev/@yaroslavvb/2026-09-22-et-soc1-l2-mainline-starvation). Both are public.
- `docs/reports/2026-09-18-et-soc1-ridge-points.html` ("Ridge points") works out, from the chip's specs and the
  measurements above, how many FLOPs per byte a kernel needs from each level of memory before compute rather than
  bandwidth sets its speed. `scripts/ridge-points.py` regenerates its numbers from the reports' raw data; no card runs.
  It is published at https://spacesheep.dev/@yaroslavvb/et-soc1-ridge-points, uuid `dd341b0b-a52e-4e23-b8b3-101a83119133`.
- `docs/lab-access.md` covers logging in to the lab machines (`aifoundry1`-`3`) and creating accounts for new people.
- `workloads/` holds standalone workloads that run on both the simulator and the lab cards. The first one is `workloads/sgemm`:
  fp32 matmul, verified on aifoundry3's card at 127 GFLOP/s with scalar code. `scripts/deploy-lab.sh` builds a workload on a lab machine.
- `kernels/` holds device kernels and `launchers/` holds host programs. `kernels/hello` + `launchers/hello` is the
  hello world: all 2048 harts check in, and the host verifies them.
- `scripts/`:
  - `create-vm.sh`: one-shot setup on macOS.
  - `provision-vm.sh`: toolchain and et-platform build on any Ubuntu 24.04 machine.
  - `vm`: runs a command inside the VM.
  - `add-lab-user.sh`: creates an account on every lab machine.
  - `deploy-lab-gpsdk.sh`: builds `kernels/` and `launchers/` on a lab machine, against gp-sdk pinned and patched for its older `/opt/et`.
  - `et-power-log.sh`, `mmbench-power.py`, `mmbench-report-data.py`: board-power sampling, the benchmark runner, and the report numbers.
  - `build-report.py`: assembles a report from `docs/reports/sources/` and its data; `paste-chartkit.py`: copies the shared
    chart toolkit (`docs/reports/sources/chartkit.js` and its CSS) into the standalone report pages (`--check` reports drift).
- `patches/` holds local fixes to et-platform: a broken third-party fetch, gp-sdk launchers that can't boot sysemu, and
  `lab-gp-sdk-06605ab.patch` for the lab machines. See `patches/README.md`. `external/` holds the upstream clones and is gitignored.

## Setup (macOS, Apple Silicon)

```bash
scripts/create-vm.sh
```

This does four things:
1. Installs [Lima](https://lima-vm.io) and creates the VM `et`: Ubuntu 24.04 arm64, 16 vCPU, 48 GB RAM, with this repo mounted at the same path.
2. Clones et-platform, et-man, and core-et (erbium) into `external/`.
3. Builds the ET RISC-V toolchain from source into `/opt/et`, since the prebuilt release is x86-only.
4. Builds et-platform (firmware, `sys_emu`, runtime, gp-sdk) into `/opt/et`.

On an M5 Max this took about 15 minutes. Most of that is the 7-minute toolchain build. On a native Ubuntu 24.04 x86 or arm64 box, run `scripts/clone-upstream.sh && scripts/provision-vm.sh`.

The VM keeps running in the background. Stop it with `limactl stop et`. `scripts/vm` restarts it on demand.

## Run

Each run on the simulator takes about 40 s. Almost all of that is the simulated firmware booting 33 shires.

```bash
scripts/vm make run-hello
```

This builds `kernels/hello` and `launchers/hello`, then runs the kernel on the simulator. Expected output:
`hello: 2048/2048 harts reported in from 32 shires ... PASS`.

```bash
scripts/vm make trace
```

This prints the kernel's `et_printf` output from the device trace.

```bash
scripts/vm make upstream-test
```

This runs et-platform's README/CI hello world, `it_test_code_loading`. Expected: 3 tests PASSED.

```bash
scripts/vm make upstream-hello
```

This runs gp-sdk's `hello_world_launcher` with `print.elf`. It prints `HELLO WORLD!!!!` and needs patch 0002.

```bash
scripts/vm make run-hello SIM_PARAMS="-vpurf_warn"
```

This adds the simulator's A0-errata checker to a run.

On a lab machine with a card and the et-platform stack installed:

```bash
make run-hello DEVICE=silicon
```

## Adding a prototype

1. Put the kernel in `kernels/foo/foo.cc` and add `add_kernel(foo foo/foo.cc)` to `kernels/CMakeLists.txt`.
2. Put the host side in `launchers/foo/foo.cpp` and add `add_launcher(foo_launcher foo/foo.cpp)` to `launchers/CMakeLists.txt`.
3. Share the argument struct via `kernels/foo/foo_args.h`, and add a `run-foo` target to the `Makefile`.

## Upstream

- https://github.com/aifoundry-org/et-platform: firmware, runtime, simulator, gp-sdk
- https://github.com/aifoundry-org/et-man: Programmer's Reference Manual, datasheet, errata
- https://github.com/openhwfoundation/core-et/tree/erbium: RTL and micro-architecture docs
- https://github.com/aifoundry-org/riscv-gnu-toolchain: GCC port (branch `et`)
- FOSDEM 2026, "Zero to matmul with the ET-SoC-1": https://archive.fosdem.org/2026/events/attachments/T3PSFN-zero_to_matmul_with_the_et-soc-1/slides/267107/zerotomat_asnyquu.pdf
