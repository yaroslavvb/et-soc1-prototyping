# nekko: ET-SoC-1 prototyping

This workspace is for prototyping workloads on AINekko/AI Foundry's ET platform (the Esperanto ET-SoC-1:
1088 RV64 "minion" cores with vector and tensor extensions). They run first on the `sys_emu` simulator,
then on real cards in the AI Foundry lab.

**Read [`AGENT.md`](AGENT.md) first.** It maps the repository, the machines and the cards, the rules, the measurement
framework and the publishing path, and ends with a first-hour checklist. Read `docs/et-soc1-notes.md` before writing
kernels. `docs/getting-started.md` has the current status ("Where things stand"), next steps, and how to resume on a
new machine.

**This repository is the ground truth: the knowledge base and the tool collection.** Every result, the experiment
behind it, its raw data and the tool that produced it are here, and `docs/findings/README.md` is the index
(claims → experiment → file). Claude Code's memory is per-machine and invisible elsewhere, so every lesson goes into
the repository (AGENT.md, "Where new lessons go"), and `docs/getting-started.md` is kept current when the state of the
work changes. Every published page is a committed file listed in `docs/reports/MIRROR.md`; after a deploy, check that
the live page equals the file (`python3 scripts/check-mirror.py`). Never mirror a private page, and never put anything
security-sensitive in this public repository (access paths, keys, other people's accounts or files).
Before measuring anything, read `docs/findings/README.md`, `docs/findings/14-card-behaviour.md` (the cards and the
traps) and `docs/findings/19-observability-and-the-unmetered.md` (what the meters can and cannot see); record new
work in `docs/findings/02-requests.md`, `03-experiments.md`, `04-artifacts.md` and `05-claims.md`, and commit the data
under `docs/reports/data/<date>-<name>-<host>/`.

## Where am I?

| You are on | ET tooling | Build and run |
|---|---|---|
| A Mac (the original setup, for simulator work) | in the Lima VM `et` (Ubuntu 24.04 arm64); the repo is mounted at the same path | **prefix commands with `scripts/vm`**, e.g. `scripts/vm make run-hello` |
| Another Ubuntu 24.04 box without cards | `scripts/clone-upstream.sh && scripts/provision-vm.sh` build the same `/opt/et` natively (never run `provision-vm.sh` on a lab machine: its `/opt/et` is the lab's) | run directly |
| A lab machine, `aifoundry1`, `aifoundry2` or `aifoundry3` (x86_64 Ubuntu 24.04, where the card work runs; the git checkout is `~/claude/et-soc1-prototyping` on aifoundry2) | the lab's own, older `/opt/et` (below) | run directly: `scripts/vm` does not apply |

## The simulator environment (Mac + Lima, or a provisioned Ubuntu)
- `/opt/et` (inside the VM) holds the ET RISC-V GCC 15.2 toolchain and the et-platform install: runtime,
  `sys_emu`, firmware, gp-sdk. The et-platform build dir is `~/build/et-platform` in the VM.
- `external/` has the upstream clones (gitignored): `et-platform`, `et-man` (manuals as PDFs), and `core-et`
  (erbium branch, micro-architecture docs). `patches/` holds local fixes to et-platform, which
  `scripts/provision-vm.sh` applies.
- Rebuilding after changes to et-platform sources: `scripts/vm scripts/provision-vm.sh platform`.

## Layout and workflow
- `kernels/<name>/`: device code (RISC-V, U-mode). Register it with `add_kernel(<name> <srcs>)` in
  `kernels/CMakeLists.txt`. It is built inside gp-sdk's device project via `CUSTOM_KERNELS_SRC_DIR`.
- `launchers/<name>/`: host programs built on gp-sdk's `GenericLauncher`. Register with `add_launcher(...)`.
  Put the shared kernel-argument struct in `kernels/<name>/<name>_args.h`, using fixed-width types only.
- `make` builds both into `build/`, and `make run-hello` runs the example. Launchers take
  `--device_type=sysemu|silicon`, so the same binary targets the simulator or a card.
- Extra simulator flags go through `SIM_PARAMS="..."` (the launcher's `--simulator_params`). Run output
  goes to `build/run/`: `sysemu.log0`, UART logs, and `traceKernels_dev0_0.bin`. `make trace` prints the kernel's `et_printf` lines.

## Lab machines (real ET-SoC-1 cards)
- The machines are `ssh aifoundry1|2|3` (Tailscale SSH in check mode, user `yaroslavvb`: a person must approve the
  login URL it prints; an agent hands it over and waits). See `docs/lab-access.md`.
- Four cards: aifoundry2 and aifoundry3 have one each, aifoundry1 two (select one with `ET_DEVICES=<n>` there).
  **aifoundry1's card 0 overheats: no sustained work on it.** aifoundry3 is pinned at 600 MHz by a boot service.
  Their differences: `docs/findings/14-card-behaviour.md`.
- The hosts' `/opt/et` is **older** than the simulator's: GCC 15.1, no gp-sdk launchers and no Erbium bits, and not
  the same runtime on every host (aifoundry2 stock `353f20e`, aifoundry3 a patched `libetrt.so`, aifoundry1 a fork
  build).
- Workloads that must run there live in `workloads/<name>/`. They are standalone, in the et-testdrive style, using only the runtime API
  and `et-common-libs`, and they build against either install. `scripts/deploy-lab.sh <host> workloads/<name>` copies the sources
  and builds them on the machine. The kernel is built there too, with the lab toolchain.
- gp-sdk kernels and launchers (`kernels/`, `launchers/`) also run there. `scripts/deploy-lab-gpsdk.sh <host>` installs gp-sdk
  pinned to `06605ab` plus `patches/lab-gp-sdk-06605ab.patch` at `~/nekko/external/et-platform/gp-sdk` and builds with `nice -j4`.
  Then run `make mmbench-check DEVICE=silicon` and `make bench-power` in `~/nekko`. Without the patch, kernels fault at PC 0x40.
- Measurements that must be repeatable go through `tools/claims-v3/` (`lib.sh` enforces the rules below; see AGENT.md).
  Its queues may be running: check `docs/getting-started.md`, "Where things stand", and `et-who` before any card work.
  While they run, never rebuild a build directory their blocks use (`lib.sh` lists them) and never run
  `scripts/deploy-lab*.sh` against that host: both write into `~/nekko`, which the blocks use on every host (AGENT.md §7).
- **Etiquette. The cards are shared, and the user set these rules:**
  - Ask which machine to use, and stay off machines other sessions are using.
  - Check for other users before touching a card: `et-who` (who holds each card's nodes and lock), `who`, `uptime`,
    `ps`. Hold the card's lock for the run: `flock -n /run/lock/etsoc-shire<N>.lock <cmd>`.
  - Never hold a device for more than 10 s. Wrap runs in `timeout 10`; the sgemm host also stops launching after `--budget`.
  - Keep disk and memory use small: sources only, `nice -j4` builds.
  - Stop samplers and tools with a plain `kill` or Ctrl-C, never `kill -9`, and never reset a card yourself: ask
    the lab admin.
  - An agent that only writes code must not reach a card: test block scripts with `V3_DRY=1`.

## Rules of thumb for ET kernels
- L1D$ is **not coherent** and writes back whole 64 B lines. Harts on different minions must not write to the
  same line. Use per-hart 64 B-aligned ownership, `…l`/`…g` stores, or explicit evicts. The firmware evicts L1/L2 after a kernel.
- Validate FP/vector code with `SIM_PARAMS="-vpurf_check -mem_check"`. A0 silicon has the VPU register-file
  hazard (errata 1.29), and this GCC does not insert workarounds.
- `sys_emu` is functional only, so there are no performance numbers from it. Test on a small `--shire_mask` first because it is slow.
- Only hart 0 of a minion may issue tensor ops, except `TensorLoadL2Scp`/`TensorWait`. There is no hardware fdiv/fsqrt, and no 64-bit
  integer-to-float conversion (`fcvt.s.lu` traps with cause 30): use 32-bit counters in floating-point loops.
- A `double` anywhere in a kernel traps too, and so do `fsin`, `frsq` and reading `cycle` in U-mode. Offset 0 of a
  shire's scratchpad faults, and a global atomic through a scratchpad address is a bus error. Never spin on one
  global atomic from many shires (it stops the home shire's memory path): use a credit-release barrier. The full
  list is in `docs/findings/14-card-behaviour.md`, "Traps".
