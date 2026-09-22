# nekko: ET-SoC-1 prototyping

A workspace for prototyping on AINekko / AI Foundry's **ET platform**, the open-sourced Esperanto
**ET-SoC-1**: 1088 RISC-V minion cores with custom vector and tensor units. Work runs on the
`sys_emu` simulator first, then on real cards in the AI Foundry lab.

**Looking for results rather than code? Start with [docs/findings/](docs/findings/README.md).** It is a
self-contained write-up of everything measured on the card: what a workload's data does to power and
temperature, the model that predicts it, why the chip is low power against an A100, and — for every number —
which experiment produced it and which raw file holds the evidence.

**New machine? Start with [docs/getting-started.md](docs/getting-started.md).** It covers the current status,
cloning, connecting to the lab machines over Tailscale, the hello worlds, rerunning the benchmark, and
republishing the reports. Its section 8 shows how to regenerate every report from the raw data committed here, and
section 9 lists the pinned upstream versions.

- `docs/et-soc1-notes.md` is a condensed guide: architecture, programming model, the memory-coherency trap,
  the FOSDEM "zero to matmul" optimization ladder, silicon errata, and simulator flags.
- `docs/report/` is the first shareable write-up, published at https://spacesheep.dev/@yaroslavvb/et-soc1-testdrive.
  Edit `index.html`, then run `npx --yes spacesheep deploy docs/report --space 16732875-c03e-434d-a643-7a432586c7f7`
  to update the same space. Without `--space` the CLI creates a new one, and its `.spacesheep.json` pin files are gitignored.
- `docs/reports/2026-09-18-et-soc1-matmul-efficiency.html` measures tensor-unit matmul speed and energy efficiency
  on aifoundry2's card against the A100 (`kernels/mmbench`, `launchers/mmbench`, `make bench-power`). Its raw data is in `docs/reports/data/`.
- `docs/reports/2026-09-18-et-soc1-memory-hierarchy.html` measures each memory level's size, latency, bandwidth and energy per
  byte on the same card, next to published A100 numbers (`workloads/memhier`; private space
  https://spacesheep.dev/@yaroslavvb/et-soc1-memory-hierarchy, uuid `4b6e0a37-808d-4fc9-8001-555125733c46`).
- `docs/reports/2026-09-18-et-soc1-on-chip-communication.html` maps the 32 shires on the 6x6 mesh and measures the chip's
  message passing on the same card, next to how GPUs communicate between cores: TensorSend/Recv by distance and size,
  hardware reduction trees, credit counters, barriers, and energy per byte. It uses `workloads/nocbench`, and is a private
  space at https://spacesheep.dev/@yaroslavvb/et-soc1-on-chip-communication, uuid `ab8e1b2b-de17-44f4-8645-006fa960e349`.
- `docs/reports/2026-09-18-et-soc1-sparsity.html` measures what aifoundry3's card does with zeros (tensor-unit zero-skip,
  masked TensorLoads, a batch-1 sparse layer, divergent work items) and lists the scenarios where the chip could beat an
  A100, with the benchmark that would settle each. It uses `workloads/sparsity`, and is a private space at
  https://spacesheep.dev/@yaroslavvb/et-soc1-sparse-compute, uuid `5abf6014-8de0-4e82-8744-5676bac6453e`.
- `docs/reports/2026-09-19-et-soc1-memory-anatomy.html` takes single memory accesses apart on aifoundry2's card: latency
  by stage (L2, L3 home shire, mesh hops, memory shire, DRAM row state, refresh) to within ±3 cycles, and energy per load
  by power rail (minion cores, SRAM, NoC, DDR side). It uses `workloads/memprobe`; `docs/research/` holds the survey of
  counters, DRAM mapping and power telemetry it builds on. Private space https://spacesheep.dev/@yaroslavvb/et-soc1-memory-anatomy,
  uuid `2bf74fd1-fd7f-4e19-8e35-6168ae42657c`.
- `docs/reports/2026-09-20-et-soc1-limits-of-observability.html` is the ladder of what can be observed on the chip, from board
  power down to a flip-flop per cycle in the RTL, with what each step would take. Its sources (a seven-layer survey of the manuals,
  firmware, RTL and tools, with two-reviewer verification of the key claims) are in `docs/reports/sources/2026-09-20-limits-of-observability/`;
  `scripts/build-observability-report.py` assembles the page. Private space https://spacesheep.dev/@yaroslavvb/et-soc1-limits-of-observability, uuid `2ea37420-67b9-484e-9d4c-581e8a9f0323`.
- Observability tooling that came out of that survey, none of which changes a card:
  - `workloads/traceprof` + `scripts/trace-flamegraph.py`: a device flame graph in minion cycles from a kernel's profile regions.
  - `rtl-sim/pmu_carry`: the original PMU RTL under Verilator; it reproduces and explains the late bit-7 carry of `hpmcounter3`.
  - `rtl-sim/fma_toggle`: eight copies of the fused multiply-add RTL replaying a TensorFMA32 on the card's own operands; counts
    register bits clocked and nets toggled per data pattern (the Horace experiment's power model).
  - `patches/0003-pmc-configure-syscall-353f20e.patch`, `scripts/build-minion-fw.sh`, `workloads/pmcsel`: a firmware syscall
    that lets a kernel choose counter events, built and verified in `sys_emu`. A card would need a signed image to run it.
- `docs/reports/2026-09-20-et-soc1-power-temperature.html` lists every way to measure power, energy and temperature on the card,
  and shows a load step through all of them: leakage of 0.8 W per °C, idle power that depends on recent load, rail averages that
  lag by 2 s, and a 34-shire on-die voltage map. It uses `tools/ettelem`, a telemetry client on the management library
  (`tools/ettelem/run_thermal.sh`). Private space https://spacesheep.dev/@yaroslavvb/et-soc1-power-temperature, uuid `acee5c6d-56c0-45e7-aa97-ce11af37bdd8`.
- `docs/reports/2026-09-20-horace-experiment.html` reproduces Horace He's "predictable data" matmul result on this chip and takes
  it apart (fourth version, 21 September). Same clock and FLOPs for every operand pattern, but 38 W on zeros, 47 W on ones and
  63 W on random values, with every run launched from the same die temperature (`tools/ettelem/run_horace_strict.sh`); heating per
  FLOP; a power model from RTL switching activity of the multiply-add unit (`rtl-sim/fma_toggle`, 0.5 W out of sample); the speed
  effect from a cool die (`run_horace_cold.sh`); ten-minute runs with a 90 °C cap (`run_horace_long.sh`: random data gets from 80 to
  90 °C in 19 to 26 s, ones in about two minutes, zeros never); a three-line model from flip rates to temperature
  (`tools/ettelem/flip_thermal_model.py`: leakage 23 W at 80 °C, thermal stages out to 2,500 s; on held-out runs the time to 90 °C is predicted to 9% in the median and 23% at worst,
  and ten-minute end temperatures come out 3 to 5 °C hot: `tools/ettelem/validate_flip_model.py`);
  and structured matrices (Hadamard, DCT, butterfly, kaleidoscope, ...: `tools/ettelem/make_tiles.py`) whose power was predicted to
  0.9 W before they ran. `tools/ettelem/predict_heat.py --model .../model.json --tiles my.bin` prices a custom workload: flips,
  watts, heating curve, time to a cap, sustainable duty cycle. GIFs: `docs/reports/horace-heating.gif`, `horace-heating-6.gif`,
  `horace-long.gif`. `tools/ettelem/finish_horace.sh` rebuilds everything from `docs/reports/data/2026-09-21-horace-aifoundry2/`.
  Public space (the user's choice) https://spacesheep.dev/@yaroslavvb/et-soc1-horace-experiment, uuid
  `da445a93-7be3-42c2-b9be-4992fa4a3b62`, deployed as a folder (`index.html` plus the GIFs), so the GIFs have public addresses such as
  https://da445a93-7be3-42c2-b9be-4992fa4a3b62.spacesheep.app/horace-heating.gif. A folder deploy can leave the space private;
  put it back with `spacesheep share <uuid> --visibility public` and check `spacesheep list` after every deploy.
- `docs/reports/2026-09-21-why-low-power.html` asks why the chip draws so little next to an A100, using Esperanto's own equation
  (power = C V² f + leakage) and ablations on the card (`tools/ettelem/run_ablation.sh`, `ablation.cfg`, `analyze_ablation.py`):
  an integer loop on all cores costs 1.5 W, int8 multiply-adds 0.32 pJ against 6.0 pJ for fp32, power is linear in active cores,
  the 0.62 V / 800 MHz point costs 2× the switching power of 0.52 V / 600 MHz, leakage is 23 W at 80 °C, and per FLOP of dense
  matmul an A100 is five times better. Notes and sources in `docs/research/why-low-power.md`. Private space
  https://spacesheep.dev/@yaroslavvb/et-soc1-why-low-power, uuid `baede20c-57d9-4e01-8157-2014670dd8cf`.
  Both are assembled by `scripts/build-report.py` from `docs/reports/sources/`. After any `spacesheep deploy` of the other spaces,
  re-check that the space is still private: deploys have reset visibility to public more than once.
- `docs/reports/2026-09-22-dvfs-leakage.html` checks six claims by David Kanter (MLPerf) about DVFS loops and
  leakage suppression against this chip: the governor reads a measured PMIC wattage rather than estimating power
  from activity counters, its ±5% guardband macros are dead code so it hunts (36 transitions analysed,
  `tools/ettelem/analyze_dvfs.py`), the per-minion sleep transistors in the RTL are tied off and no firmware
  drives them, a wake-up probe finds no array power gating (`gen_ops.py wakeup`), and leakage is 36% of a busy
  card against his 5-30%. Private space https://spacesheep.dev/@yaroslavvb/et-soc1-dvfs-leakage, uuid
  `171dcd4a-5b6d-49d3-aca0-db4980fabfa5`.
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
