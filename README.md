# nekko: ET-SoC-1 prototyping

A workspace for prototyping on AINekko / AI Foundry's **ET platform**, the open-sourced Esperanto
**ET-SoC-1**: 1088 RISC-V minion cores with custom vector and tensor units. Work runs on the
`sys_emu` simulator first, then on real cards in the AI Foundry lab.

**An agent, or a person picking up the work? Start with [AGENT.md](AGENT.md)**: the map, the rules, and where to find
the current state. Page changes waiting for the next pass are listed in [docs/reports/TODO.md](docs/reports/TODO.md).

**Looking for results rather than code? Start with [docs/findings/](docs/findings/README.md).** It is a
self-contained write-up of everything measured on the card: what a workload's data does to power and
temperature, the model that predicts it, why the chip is low power against an A100, and — for every number —
which experiment produced it and which raw file holds the evidence. The published reports are indexed on the
public hub, [Limits of observability](https://spacesheep.dev/@yaroslavvb/et-soc1-limits-of-observability#reports);
[`docs/reports/MIRROR.md`](docs/reports/MIRROR.md) records every published page, its space uuid, its visibility and the
committed file it mirrors (`python3 scripts/check-mirror.py` compares them); `docs/findings/04-artifacts.md` records
the code and data.

**New machine? Start with [docs/getting-started.md](docs/getting-started.md).** It covers the current status,
cloning, connecting to the lab machines over Tailscale, the hello worlds, rerunning the benchmark, and
republishing the reports. Its section 8 shows how to regenerate every report from the raw data committed here, and
section 9 lists the pinned upstream versions.

## The published pages

Every page of the measurement set, with the code that measured it and its raw data. Since 26 September the pages also
carry version 3 of the claims check, every claim re-tested on three cards (`tools/claims-v3/`,
`docs/reports/data/2026-09-25-claims-v3/`). [`docs/reports/MIRROR.md`](docs/reports/MIRROR.md) gives each page's space,
visibility and build command (and lists the lab-machine pages), [getting-started §8](docs/getting-started.md#8-reproducing-each-report)
how to measure and regenerate it, and [`docs/findings/04-artifacts.md`](docs/findings/04-artifacts.md) its history and
tools. The hub's survey sources (seven AI research agents, Claude subagents run by the author, each covering one layer
of the manuals, firmware, RTL and tools, with each key claim checked by two further AI agents) are in
`docs/reports/sources/2026-09-20-limits-of-observability/`. Add a row here with each new page.

| Page · file | Code | Raw data |
|---|---|---|
| [The ET-SoC-1, interactively](https://spacesheep.dev/@yaroslavvb/et-soc1-chip-diagram) · `docs/reports/2026-09-27-et-soc1-chip-diagram.html` | `docs/reports/data/2026-09-27-chip-diagram/build_facts.py` | `docs/reports/data/2026-09-27-chip-diagram/` |
| [Anatomy of a memory access, interactively](https://spacesheep.dev/@yaroslavvb/et-soc1-memory-levels) · `docs/reports/2026-09-28-et-soc1-memory-levels.html` | `docs/reports/data/2026-09-28-memory-levels/build_facts.py` | `docs/reports/data/2026-09-28-memory-levels/` |
| [Where the work sits: placement and the thermal trip](https://spacesheep.dev/@yaroslavvb/et-soc1-heat-placement) · `docs/reports/2026-09-28-et-soc1-heat-placement.html` | `tools/claims-v3/hp/`, `docs/reports/data/2026-09-28-heat-placement/build_heat_data.py` | `docs/reports/data/2026-09-28-heat-placement/` |
| [The effect of overheating](https://spacesheep.dev/@yaroslavvb/et-soc1-effect-of-overheating) · `docs/reports/2026-09-28-effect-of-overheating.html` | `tools/claims-v3/oh/`, `docs/reports/data/2026-09-28-overheating/build_overheat_data.py` (and `scripts/` there) | `docs/reports/data/2026-09-28-overheating/` |
| [The PCIe link and the launch path](https://spacesheep.dev/@yaroslavvb/et-soc1-pcie-link) · `docs/reports/2026-09-27-et-soc1-pcie-link.html` | `workloads/pciebench/` | `docs/reports/data/2026-09-27-pcie/` |
| [Limits of observability · ET-SoC-1 reports hub](https://spacesheep.dev/@yaroslavvb/et-soc1-limits-of-observability) · `docs/reports/2026-09-20-et-soc1-limits-of-observability.html` | `tools/ettelem/sync_hub_data.py`, `workloads/traceprof/`, `rtl-sim/pmu_carry/`, `workloads/pmcsel/` | `docs/reports/sources/limits-of-observability.data.json`, `docs/reports/sources/2026-09-20-limits-of-observability/` |
| [The energy manual](https://spacesheep.dev/@yaroslavvb/et-soc1-energy-manual) · `docs/reports/2026-09-23-energy-manual.html` | `workloads/enercat/`, `tools/ettelem/build_energy_manual.py` | `docs/reports/data/2026-09-23-energy-manual/`, `docs/energy-manual/` |
| [Heat per millimetre](https://spacesheep.dev/@yaroslavvb/et-soc1-heat-per-mm) · `docs/reports/2026-09-24-heat-per-mm.html` | `workloads/enercat/run_wire.py`, `tools/ettelem/build_wire_report.py` | `docs/reports/data/2026-09-24-wire-energy/` |
| [The DVFS loop and its leakage](https://spacesheep.dev/@yaroslavvb/et-soc1-dvfs-leakage) · `docs/reports/2026-09-22-dvfs-leakage.html` | `tools/ettelem/analyze_dvfs.py`, `tools/etcfg/` | `docs/reports/data/2026-09-22-dvfs-aifoundry2/` |
| [Power and temperature telemetry](https://spacesheep.dev/@yaroslavvb/et-soc1-power-temperature) · `docs/reports/2026-09-20-et-soc1-power-temperature.html` | `tools/ettelem/run_thermal.sh`, `tools/ettelem/summarize_power_session.py` | `docs/reports/data/2026-09-20-power-aifoundry2/` |
| [The Horace experiment](https://spacesheep.dev/@yaroslavvb/et-soc1-horace-experiment) · `docs/reports/2026-09-20-horace-experiment.html` | `tools/ettelem/finish_horace.sh`, `rtl-sim/fma_toggle/`, `tools/ettelem/predict_heat.py` | `docs/reports/data/2026-09-21-horace-aifoundry2/`, `docs/reports/data/2026-09-22-horace-aifoundry3/` |
| [Why is it low power?](https://spacesheep.dev/@yaroslavvb/et-soc1-why-low-power) · `docs/reports/2026-09-21-why-low-power.html` | `tools/ettelem/run_ablation.sh`, `docs/research/why-low-power.md` | `docs/reports/data/2026-09-21-horace-aifoundry2/` |
| [One hot line stops a shire](https://spacesheep.dev/@yaroslavvb/et-soc1-hot-line) · `docs/reports/2026-09-22-hot-line.html` | `workloads/nocbench/`, `tools/ettelem/run_hotline_power.sh` | `docs/reports/data/2026-09-22-hotline-aifoundry2/`, `docs/reports/data/2026-09-22-hotline-aifoundry3/` |
| [Hand it to the next shire: on-chip relay vs DRAM](https://spacesheep.dev/@yaroslavvb/et-soc1-on-chip-relay) · `docs/reports/2026-09-22-on-chip-relay.html` | `workloads/onchip/`, `tools/ettelem/run_onchip_power.sh` | `docs/reports/data/2026-09-22-onchip-aifoundry2/`, `docs/reports/data/2026-09-22-onchip-aifoundry3/` |
| [Anatomy of a memory access](https://spacesheep.dev/@yaroslavvb/et-soc1-memory-anatomy) · `docs/reports/2026-09-19-et-soc1-memory-anatomy.html` | `workloads/memprobe/`, `docs/research/` | `docs/reports/data/2026-09-19-memprobe-aifoundry2/`, `docs/reports/data/2026-09-26-memprobe-3cards/` |
| [Memory hierarchy](https://spacesheep.dev/@yaroslavvb/et-soc1-memory-hierarchy) · `docs/reports/2026-09-18-et-soc1-memory-hierarchy.html` | `workloads/memhier/` | `docs/reports/data/2026-09-18-memhier-aifoundry2/` |
| [On-chip communication](https://spacesheep.dev/@yaroslavvb/et-soc1-on-chip-communication) · `docs/reports/2026-09-18-et-soc1-on-chip-communication.html` | `workloads/nocbench/` | `docs/reports/data/2026-09-18-nocbench-aifoundry2/` |
| [Matmul efficiency](https://spacesheep.dev/@yaroslavvb/et-soc1-matmul-efficiency) · `docs/reports/2026-09-18-et-soc1-matmul-efficiency.html` | `kernels/mmbench/`, `launchers/mmbench/`, `scripts/mmbench-report-data.py` | `docs/reports/data/2026-09-18-aifoundry2/` |
| [Sparse compute](https://spacesheep.dev/@yaroslavvb/et-soc1-sparse-compute) · `docs/reports/2026-09-18-et-soc1-sparsity.html` | `workloads/sparsity/` | `docs/reports/data/2026-09-18-sparsity-aifoundry3/` |
| [Ridge points](https://spacesheep.dev/@yaroslavvb/et-soc1-ridge-points) · `docs/reports/2026-09-18-et-soc1-ridge-points.html` | `scripts/ridge-points.py` | the four 18 September directories and `manual.json` |
| [Test drive](https://spacesheep.dev/@yaroslavvb/et-soc1-testdrive) · `docs/report/index.html` | `workloads/sgemm/`, `kernels/mmbench/`, `scripts/mmbench-report-data.py` | `docs/reports/data/2026-09-18-aifoundry2/` |
| [Spatial temperature: a brief](https://spacesheep.dev/@yaroslavvb/et-soc1-spatial-temperature-brief) · `docs/reports/2026-09-22-et-soc1-spatial-temperature-brief.html` | by hand; its two constants: `tools/ettelem/host_temp_fields.py` | `docs/reports/data/2026-09-20-power-aifoundry2/` |
| [L2 mainline starvation: a brief](https://spacesheep.dev/@yaroslavvb/2026-09-22-et-soc1-l2-mainline-starvation) · `docs/reports/2026-09-22-et-soc1-l2-mainline-starvation.html` | by hand (a pointer page) | – |
| [Influence functions on the ET-SoC-1](https://spacesheep.dev/@yaroslavvb/et-soc1-influence-functions) · `docs/reports/2026-09-25-influence-on-et.html` | `docs/reports/data/2026-09-25-influence-on-et/make_analysis.py` | `docs/reports/data/2026-09-25-influence-on-et/` |
| [Sparse parity on the ET-SoC-1](https://spacesheep.dev/@yaroslavvb/et-soc1-sparse-parity) (not yet deployed) · `docs/reports/2026-09-29-sparse-parity.html` | `workloads/sparseparity/`, `docs/reports/data/2026-09-29-sparse-parity/make_page_data.py` | `workloads/sparseparity/data/2026-09-29-aifoundry3-{card,card-m4,m5-energy}/`, `workloads/sparseparity/cpu/data/2026-09-29-aifoundry3-r/`, `workloads/sparseparity/proto/data/2026-09-28-aifoundry1/` |

## Also in the repository

- `docs/et-soc1-notes.md` is a condensed guide: architecture, programming model, the memory-coherency trap,
  the FOSDEM "zero to matmul" optimisation ladder, silicon errata, and simulator flags.
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
2. Clones et-platform, et-man, core-et (erbium), et-testdrive and etTopoScan into `external/`.
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

On a lab machine with a card and the et-platform stack installed (aifoundry3 as written: aifoundry2's card is out of
service since 2 October 2026, and on aifoundry1 a program needs `ET_DEVICES=<N>` and card N's lock,
[`docs/lab-start/START.md`](docs/lab-start/START.md), rule 3). Never deploy while a `tools/claims-v3` queue runs on
the host ([AGENT.md](AGENT.md) §7).

```bash
scripts/deploy-lab-gpsdk.sh aifoundry3        # from a clone: sources, the lab's patched gp-sdk, a nice -j4 build
ssh aifoundry3                                # then, in ~/nekko on the host:
et-who                                        # nobody on the card? (and ask first: AGENT.md §5)
flock -n /run/lock/etsoc-shire0.lock timeout 10 make run-hello DEVICE=silicon
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
