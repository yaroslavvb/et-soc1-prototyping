# Local patches to upstream repos

`scripts/provision-vm.sh` applies `et-platform-*.patch` to `external/et-platform`
before building. It skips any patch that is already applied.

| Patch | Why |
|---|---|
| `et-platform-0001-thirdparty-full-clone.patch` | `ThirdParty()` clones g3log, easy_profiler, and cereal with `GIT_SHALLOW TRUE` but pins them to `git describe` refs (e.g. `v2.1.0-66-gcc0e154`). Once upstream moves past that commit, as easy_profiler did on 2026-08-05, a depth-1 clone no longer contains it and the build fails with `fatal: invalid reference`. A full clone fixes this. Worth sending upstream, either this change or pinning full SHAs. |
| `et-platform-0002-gpsdk-sysemu-preload-firmware.patch` | gp-sdk's `GenericLauncher` never gives sysemu the firmware ELFs to preload: SP BL2, and the master, machine, and worker minion images. With `--device_type=sysemu`, every gp-sdk launcher (`hello_world_launcher`, `saxpy_launcher`, ...) boots the Service Processor on empty memory and spins forever on "Trapping to the same address", which also produces a GB-sized `sysemu.log0`. The runtime's own tests avoid this because `esperanto-tools-libs/tests/common/TestUtils.h` sets the paths. The patch sets them the same way, from the installed `EsperantoBootLoader` and `EsperantoDeviceMinionRuntime` CMake packages. |

`lab-gp-sdk-06605ab.patch` is **not** applied by `provision-vm.sh`: it targets an older gp-sdk, for lab
machines whose `/opt/et` predates current upstream. aifoundry2's install is et-platform `353f20e` (2025-12-30).
`scripts/deploy-lab-gpsdk.sh <host>` handles it. It exports gp-sdk at `06605ab`, the last version before gp-sdk
required the Erbium components that install lacks, applies this patch, installs the result where the Makefile
expects gp-sdk on the host, and builds.

| Patch | Why |
|---|---|
| `lab-gp-sdk-06605ab.patch` | Four fixes. (1) The `0002` firmware preload above. (2) dnnLibrary and FFTW become optional; only libautogen's matmul and the FFT example use them. (3) `-Wl,--emit-relocs` on kernel links. Without it the runtime cannot relocate the entry-point table, and every kernel faults at PC `0x40` with an instruction access fault. Upstream restored the flag in `7e3b4c2`. (4) `riscv_helpers.cmake` uses the keyword `target_link_libraries` form, so it doesn't clash with `kernels/CMakeLists.txt`. |
