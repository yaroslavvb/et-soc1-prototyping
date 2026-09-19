# nekko: ET-SoC-1 prototyping

A workspace for prototyping on AINekko / AI Foundry's **ET platform**, the open-sourced Esperanto
**ET-SoC-1**: 1088 RISC-V minion cores with custom vector and tensor units. Work runs on the
`sys_emu` simulator first, then on real cards in the AI Foundry lab.

**New machine? Start with [docs/getting-started.md](docs/getting-started.md).** It covers the current status,
cloning, connecting to the lab machines over Tailscale, the hello worlds, rerunning the benchmark, and
republishing the reports.

- `docs/et-soc1-notes.md` is a condensed guide: architecture, programming model, the memory-coherency trap,
  the FOSDEM "zero to matmul" optimization ladder, silicon errata, and simulator flags.
- `docs/report/` is the first shareable write-up, published at https://spacesheep.dev/@yaroslavvb/et-soc1-testdrive.
  Edit `index.html`, then run `npx --yes spacesheep deploy docs/report --space 16732875-c03e-434d-a643-7a432586c7f7`
  to update the same space. Without `--space` the CLI creates a new one, and its `.spacesheep.json` pin files are gitignored.
- `docs/reports/2026-09-18-et-soc1-matmul-efficiency.html` measures tensor-unit matmul speed and energy efficiency
  on aifoundry2's card against the A100 (`kernels/mmbench`, `launchers/mmbench`, `make bench-power`). Its raw data is in `docs/reports/data/`.
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
