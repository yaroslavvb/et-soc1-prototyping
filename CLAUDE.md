# nekko: ET-SoC-1 prototyping

This workspace is for prototyping workloads on AINekko/AI Foundry's ET platform (the Esperanto ET-SoC-1:
1088 RV64 "minion" cores with vector and tensor extensions). They run first on the `sys_emu` simulator,
then on real cards in the AI Foundry lab. Read `docs/et-soc1-notes.md` before writing kernels.

## Environment
- The host is macOS/arm64. All ET tooling runs in the Lima VM `et` (Ubuntu 24.04 arm64). The repo is mounted
  at the same path in the VM, so **prefix build and run commands with `scripts/vm`**, e.g. `scripts/vm make run-hello`.
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
- The machines are `ssh aifoundry1|2|3` (Tailscale SSH, user `yaroslavvb`). They are x86_64 with an **older `/opt/et`**: no gp-sdk
  launchers and no Erbium bits. See `docs/lab-access.md`.
- Workloads that must run there live in `workloads/<name>/`. They are standalone, in the et-testdrive style, using only the runtime API
  and `et-common-libs`, and they build against either install. `scripts/deploy-lab.sh <host> workloads/<name>` copies the sources
  and builds them on the machine. The kernel is built there too, with the lab toolchain.
- **Etiquette. The cards are shared, and the user set these rules:**
  - Ask which machine to use, and stay off machines other sessions are using.
  - Check `uptime`/`ps` for other users before touching a card.
  - Never hold a device for more than 10 s. Wrap runs in `timeout 10`; the sgemm host also stops launching after `--budget`.
  - Keep disk and memory use small: sources only, `nice -j4` builds.

## Rules of thumb for ET kernels
- L1D$ is **not coherent** and writes back whole 64 B lines. Harts on different minions must not write to the
  same line. Use per-hart 64 B-aligned ownership, `…l`/`…g` stores, or explicit evicts. The firmware evicts L1/L2 after a kernel.
- Validate FP/vector code with `SIM_PARAMS="-vpurf_check -mem_check"`. A0 silicon has the VPU register-file
  hazard (errata 1.29), and this GCC does not insert workarounds.
- `sys_emu` is functional only, so there are no performance numbers from it. Test on a small `--shire_mask` first because it is slow.
- Only hart 0 of a minion may issue tensor ops, except `TensorLoadL2Scp`/`TensorWait`. There is no hardware fdiv/fsqrt.
