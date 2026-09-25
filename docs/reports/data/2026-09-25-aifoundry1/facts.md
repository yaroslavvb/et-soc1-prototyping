# aifoundry1: what is broken (facts gathered 2026-09-25 13:01–13:15 PDT, read-only)

## Bottom line

aifoundry1's two cards are healthy at the PCIe and driver level. Every ET tool refuses them because the loaded
`et_soc1` kernel module has an **empty version string**. `/sys/module/et_soc1/version` contains only `"\n"`,
where aifoundry2 and aifoundry3 have `0.20.0`. The host library's driver check reads that file, finds no
`x.y.z`, and throws `Error unable to evaluate compatibility!` right after `open()`, before any command reaches
the card.

The empty version comes from a one-character Makefile typo, `$(ET_MODULE_VERSION=)`. It was introduced in
et-platform commit `09531e5c1` (2025-10-21, "Adding Makefile helpers") and fixed five days later in `78ed9b0d6`
(2025-10-26, "Fix version on dkms build"). That commit's message describes this exact failure: "When version
is empty, devicelayer fails to open the device as cannot check the compatibility of the driver."

aifoundry1's DKMS source `/usr/src/et-soc1-0.20.0` is a byte-exact snapshot of `09531e5c1`, copied on
2025-10-21 and 2025-10-24 and never refreshed. DKMS has rebuilt the broken module from it for every kernel
since. That includes `7.0.0-34`, the kernel that aifoundry1 will boot next, so a reboot will not fix it.
aifoundry2 and aifoundry3 build from the fixed tree.

The `srcversion` difference (`1383B256…` against `47D26A30…`) is a **symptom**, not the check. The source
bytes differ in two ways:

- the Makefile typo;
- a CentOS-9 `#if` change (`307e59c27`), which compiles to identical code on Ubuntu kernel 7.0.

So the only functional difference between aifoundry1's driver and the working ones is the empty version.
aifoundry1 already has the fixed driver source in `/usr/src/et-platform/et-driver`, byte-identical to what
aifoundry2 and aifoundry3 build. Re-pointing DKMS at it is a root-only fix of a few minutes (see below).

## Exact error text (verbatim, from our 2026-09-22 attempts on aifoundry1; transcript extract in `facts/aifoundry1/earlier-attempts-2026-09-22.txt`)

`ettelem sample` (build/ettelem/ettelem, links deviceLayer statically):
```
Opening device 0
FAIL: Exception message:Error unable to evaluate compatibility!
StackTrace:
	stack dump [1]  dbg::StackException::StackException(std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > const&) + 0x46
	stack dump [2]  build/ettelem/ettelem(+0x61805) [0x563c6a07f805]
	...
```
`/opt/et/bin/dev_mngt_service -m DM_CMD_GET_FIRMWARE_BOOT_STATUS` (2026-09-22 12:11:51 PDT):
```
command: DM_CMD_GET_FIRMWARE_BOOT_STATUS code 16
terminate called after throwing an instance of 'dev::Exception'
  what():  Exception message:Error unable to evaluate compatibility!
StackTrace:
2026/09/22 12:11:51 157256
***** FATAL SIGNAL RECEIVED *******
```
In the same 2026-09-22 command, `cat /sys/module/et_soc1/version` printed an **empty line** on aifoundry1 and
`0.20.0` on aifoundry3. The evidence was in hand then, but it was attributed to `srcversion`.

`tools/etcfg` works on both aifoundry1 cards, because it issues the raw `ETSOC1_IOCTL_GET_DEVICE_CONFIGURATION`
without deviceLayer. On 2026-09-22 it returned `tdp_w 65, minion_boot_freq_mhz 600, cm_shire_mask 0xffffffff`
for both `/dev/et0_mgmt` and `/dev/et1_mgmt`.

## Where the check is (et-platform `devicelayer/src/DevicePcie.cpp`, unchanged 353f20e..HEAD 836a4ab)

Excerpt saved in `facts/source/DevicePcie-check.txt`.

- L36: `constexpr auto kMinReqDriverVersion = "0.15.0";`
- L165–175 `getDeviceAttributeByName()`: reads `/sys/bus/pci/devices/<bdf>/<attr>`. If the file is missing it throws
  `Invalid attribute file path: '…'`, a different message.
- L252 `openWhenReady(path)`, which runs for every `/dev/etN_mgmt` and `/dev/etN_ops` open:
  1. `open(path, O_RDWR|O_NONBLOCK)`.
  2. `ioctl ETSOC1_IOCTL_GET_PCIBUS_DEVICE_NAME` returns, for example, `0000:01:00.0`.
  3. L270: `curVersion = getDeviceAttributeByName(devName, "driver/module/version")`, which resolves to
     `/sys/module/et_soc1/version`.
  4. L274 `std::regex_search(curVersion, "(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)")`:
     - a MAJOR other than 0 gives `Driver version is incompatible (MAJOR: …)!`;
     - a version older than 0.15.0 gives `Driver version is incompatible (x < 0.15.0)!`;
     - **no x.y.z match** gives L294 `throw Exception("Error unable to evaluate compatibility!")`.
  5. Only after that, `ETSOC1_IOCTL_GET_DEVICE_STATE` must return Ready or PendingCommands.
- The code is in `libdeviceLayer.a`, which is **statically linked** into each tool: `dev_mngt_service`,
  `et-powertop`, our `ettelem` and `sparsity_host`, and the runtime users. **It is not in `libDM.so`**:
  `grep -c 'evaluate compatibility'` gives 0 for `/opt/et/lib/libDM.so` and `libetrt.so`, and 1 for
  `libdeviceLayer.a`, `ettelem` and `sparsity_host`.

The Makefile typo, shown with a make evaluation of the two versions of the lines
(`facts/source/mkdemo/`):
```
aifoundry1  (09531e5c1):  ET_MODULE_VERSION=$(shell cat VERSION)
                          CFLAGS_MODULE+=-DET_MODULE_VERSION=\"$(ET_MODULE_VERSION=)\"     -> -DET_MODULE_VERSION=\"\"
aifoundry2/3 (78ed9b0d6+): ET_MODULE_VERSION := $(or $(shell cat VERSION 2>/dev/null), $(shell cat $(src)/VERSION 2>/dev/null), unknown)
                          CFLAGS_MODULE+=-DET_MODULE_VERSION=\"$(ET_MODULE_VERSION)\"      -> -DET_MODULE_VERSION=\"0.20.0\"
```
`MODULE_VERSION("")` gives `modinfo` the value `version:` (empty) and `/sys/module/et_soc1/version` the value `\n`,
1 byte. Both were observed on aifoundry1.

## Side-by-side

| | **aifoundry1** | aifoundry2 | aifoundry3 |
|---|---|---|---|
| OS / kernel running | Ubuntu 24.04.3, `7.0.0-31-generic` | same | same |
| Booted | 2026-09-18 15:43:48 (root on ZFS) | 2026-09-18 15:43:18 | 2026-09-18 15:43:18 |
| Kernel at next boot (installed 09-24 by unattended upgrade) | `7.0.0-34-generic` | same | same |
| Loaded module | `et_soc1`, refcnt **0** | `et_soc1`, refcnt 2 (our queue) | `et_soc1`, refcnt 1 (our sampler) |
| **`/sys/module/et_soc1/version`** | **`""` (1 byte, `\n`)** | `0.20.0` | `0.20.0` |
| `srcversion` | `1383B256EB24A0A53F04CC7` | `47D26A305A0428B29FB7FC4` | `47D26A305A0428B29FB7FC4` |
| vermagic | `7.0.0-31-generic SMP preempt mod_unload modversions` | same | same |
| `.ko` file | `/lib/modules/7.0.0-31-generic/updates/dkms/et-soc1.ko.zst` | same path | same path |
| `.ko` size / mtime | 53734 B, 2026-09-05 06:49:16 | 53714 B, 2026-09-05 06:51:32 | 53714 B, 2026-09-06 06:16:42 |
| `.ko` sha256 (first 16) | `0174afe4cfa1cde6` | `7244d5047faf9a9c` | `39229cb3851c67f1` (signatures differ per host) |
| Signed by | `aifoundry1 Secure Boot Module Signature key` | aifoundry2 … | aifoundry3 … |
| Module taint / kernel taint | OE / 12289 (P+O+E; P is probably ZFS) | OE / 12288 | OE / 12288 |
| Compiler | gcc 13.3.0-6ubuntu2~24.04.1 | same | same |
| How installed | **DKMS**, `et-soc1/0.20.0` for 20 kernels, **plus** an older `esperanto/0.20.0` DKMS package for 23 kernels | DKMS `et-soc1/0.20.0` (7.0.0-31, -34) | DKMS `et-soc1/0.20.0` (6.17.0-40, 7.0.0-31, -34) |
| DKMS source dir | `/usr/src/et-soc1-0.20.0`, dir 2025-10-21 19:40, files 2025-10-24 15:34 | `/usr/src/et-soc1-0.20.0`, 2026-03-12 16:50 | `/usr/src/et-soc1-0.20.0`, 2026-03-25 16:45 |
| **Source = et-platform commit** | **`09531e5c1` (2025-10-21), exact match on `et-soc1-pcie.c`, `et_pci_dev.h`, `Makefile`** | `61bcfc0a9` (2025-10-28) = 353f20e = HEAD | same as aifoundry2 (all sources identical) |
| Makefile version line | `…\"$(ET_MODULE_VERSION=)\"` (typo) | fixed | fixed |
| et_soc1 for next kernel 7.0.0-34 | version `""`, srcversion `1383B256…` (**still broken after reboot**) | `0.20.0`, `47D26A30…` | `0.20.0`, `47D26A30…` |
| Fixed driver source already on disk | **yes**: `/usr/src/et-platform/et-driver` (353f20e) is byte-identical to aifoundry2's DKMS source | — | — |
| How the module gets loaded at boot | not by `modules-load.d` (no entry) or udev (module has no aliases); loaded at **15:47:30**, 3m42s after boot, by something a user cannot see | `/etc/modules-load.d/et_soc1.conf` (loaded at boot +7 s) | probably `etsoc1-demo.service` `ExecStartPre=/usr/sbin/modprobe et_soc1` (loaded at boot +15 s) |
| Other ET module on disk | `esperanto.ko` (version `0.20.0`, srcversion `AD480A2EE8A4E95E7AE6414`, PCI driver name "Esperanto", Sep 2025 source), not loaded | none | none |
| udev rules | `50-et.rules` (`KERNEL=="et-soc1*", MODE="0666"`) + `50-esperanto.rules` | `50-et.rules` | `50-et.rules` |
| `/usr/src/et-platform` HEAD | `353f20e982f4…` | same | same |
| `/opt/et` runtime (cmake) | runtime 0.19.0, deviceLayer 4.1.0, deviceManagement 0.21.0, DMApp 1.22.0, linuxDriver 1.0.0 | same | same |
| `libDM.so` | sha `28712bc70aa08685`, 2181888 B, 2026-01-03 | **identical** | **identical** |
| `dev_mngt_service` | sha `a3d4c722d9505aa9`, 2026-01-03 | **identical** | **identical** |
| `libdeviceLayer.a` | 818426 B, **2026-05-01** (rebuilt) | 811500 B, 2026-01-03 | 811500 B, 2026-01-03 |
| `libetrt.so` | 12470496 B, **2026-05-10** (rebuilt, plus many `it_*`/`pcie_*` test binaries from May 2026) | 12470496 B, 2026-01-03 | **1599400 B, 2026-07-23** (patched build with an "event-id guard", backups `*.pre-event-id-guard.*`) |
| PCIe devices | **2**: `01:00.0` and `02:00.0`, `[1e0a:eb01]`, class 1200 | 1: `02:00.0` | 1: `02:00.0` |
| Driver bound | `ET` (et_soc1) on both | `ET` | `ET` |
| Link | Gen4 16 GT/s x8 on both (upstream 01.0 max x16, 01.1 x8) | 16 GT/s x8 | 16 GT/s x8 |
| BARs | BAR0 32G pref 64-bit, BAR2 16K, BAR4 4M (both cards) | same | same |
| PCI state | D0, enabled, BusMaster+, `>TAbort+` (same on 2 and 3) | same | same |
| AER counters (user-readable) | all zero | all zero | all zero |
| Device nodes | `/dev/et0_{mgmt,ops}` 10:263/264, `/dev/et1_{mgmt,ops}` 10:265/266, `crw-rw-rw- root:root`, created 15:47:31–32 | `/dev/et0_{mgmt,ops}` 0666 | `/dev/et0_{mgmt,ops}` 0666 |
| Driver err_stats | et0: PmicCeEvent 1, others 0; et1: all 0; no UCE | MinionCe 23, SpCe 5, no UCE | SpCe 3, no UCE |
| mgmt VQ msgs since boot | et0: SQ0 **0**, CQ0 1 (one async event); et1: 0 / 0 | SQ0 3.25 M | SQ0 1.63 M |
| ops VQ msgs since boot | 0 on both cards | SQ0 379 k | SQ0 241 k |
| ET IRQs since boot (`/proc/interrupts`) | mgmt0_irq1 = 1, all other ET vectors 0 | active | active |
| Kernel log readable | no (`dmesg`: "Operation not permitted"; journal: not in adm/systemd-journal) | no | no |
| `/var/log/kern.log` size | **279 MB**, growing ~850 B/s (17 KB in 20 s); `/var/log/dmesg` 148 MB | 0.19 MB | 0.08 MB |
| Other users / services on the box | **another user** logged in since 09-18 (tmux, running `claude`); GitHub Actions runner `nekkoai-hf-hackathon.aifoundry1-et-soc1` (root) active | another user has 10 processes; runner `aifoundry-org-hf-hackathon.aifoundry2-et-soc1` active | runner disabled; `etsoc1-demo`, `etsoc1-chatbot`, `et-board-clock-guard` services |

## What happens when a tool opens an aifoundry1 card

The sequence is from the code above, and matches the counters.

1. `open("/dev/et0_mgmt")` succeeds: the nodes are 0666 and the driver is bound.
2. `ioctl(GET_PCIBUS_DEVICE_NAME)` succeeds.
3. The tool reads `/sys/bus/pci/devices/0000:01:00.0/driver/module/version` and gets `"\n"`. The regex does not
   match, so the tool throws `Error unable to evaluate compatibility!`. `dev_mngt_service` does not catch it and
   aborts with `terminate called … FATAL SIGNAL RECEIVED`.
4. No command is ever queued to the card. The mgmt SQ0 counter on both cards is still **0** after our
   2026-09-22 attempts in this boot.

So the cards' firmware state has never been tested by any of our attempts: whether they would report Ready,
and which firmware they run, are **unknown** until the version is fixed. The driver side is known to work:
- PCIe link up;
- BARs mapped;
- MSI vectors allocated;
- DIR discovery completed, since both `etN_mgmt` and `etN_ops` nodes exist;
- `GET_DEVICE_CONFIGURATION` answers with sane values.

## Fresh read-only attempt: NOT made

On 2026-09-25 13:01, `who` on aifoundry1 showed `another user` on pts/2 and pts/3 (tmux since 09-18 17:23, a `claude`
process running) as well as yaroslavvb. Per the rules, no `/dev/et*` node was opened. aifoundry2 and aifoundry3
were not opened either, because our queues hold them. Everything above comes from sysfs, modinfo, file reads,
`/proc/interrupts` and the 2026-09-22 logs.

## Fix (for Roman or anyone with root on aifoundry1; do it when no one is using the cards; refcnt is 0 now)

Option A reuses the source the other two machines use, and gives an identical module (srcversion `47D26A30…`):
```
sudo dkms remove et-soc1/0.20.0 --all
sudo mv /usr/src/et-soc1-0.20.0 /usr/src/et-soc1-0.20.0.broken-09531e5c1
sudo mkdir /usr/src/et-soc1-0.20.0
sudo git -C /usr/src/et-platform archive 353f20e et-driver | sudo tar -x --strip-components=1 -C /usr/src/et-soc1-0.20.0
sudo dkms install et-soc1/0.20.0 -k 7.0.0-31-generic
sudo dkms install et-soc1/0.20.0 -k 7.0.0-34-generic
sudo modprobe -r et_soc1 && sudo modprobe et_soc1
cat /sys/module/et_soc1/version /sys/module/et_soc1/srcversion   # expect 0.20.0 / 47D26A305A0428B29FB7FC4
/opt/et/bin/dev_mngt_service -m DM_CMD_GET_ASIC_CHIP_REVISION -n 0 -u 5000   # then -n 1
```
Option B is the minimal fix: in `/usr/src/et-soc1-0.20.0/Makefile`, replace lines 4–5 with the two lines of
`78ed9b0d6`, then run `dkms build/install --force` for both kernels and reload the module as above. srcversion
would then stay different from aifoundry2/3's, but the version would read `0.20.0`.

Optional:
- Add `/etc/modules-load.d/et_soc1.conf` (`et_soc1`) as on aifoundry2, so the module loads at boot.
- Remove the stale `esperanto` DKMS package, a Sep 2025 driver that is not loaded but is rebuilt for every
  kernel.

## Corrections to our own notes

(`docs/findings/14-card-behaviour.md`, `03-experiments.md` E21, `05-claims.md`, the dvfs report, and the memory
note)

- "srcversion mismatch" is not the cause: nothing checks `srcversion`. The cause is the **empty module
  version**, and its origin is the Makefile typo in et-platform `09531e5c1`.
- "`libDM.so` refuses the card": the check is in deviceLayer (`DevicePcie.cpp` `openWhenReady`), which is
  statically linked into each tool. `libDM.so` is identical on all three machines.
- "`dev_mngt_service` is inactive": there is no such systemd unit on any of the three machines.
  `dev_mngt_service` is a CLI, so `systemctl is-active` prints `inactive` for any made-up name. The statement
  should be dropped.
- "not ours to fix" still holds (it needs root), but the fix is small and mechanical, and the fixed source is
  already on the machine.

## Side findings (outside the question; relevant to our lab notes)

- **aifoundry3's 0 W TDP is not a flashed value; root sets it at every boot.** The unit
  `/etc/systemd/system/et-board-clock-guard.service` was installed 2026-07-23 and is enabled and active. It
  runs `/usr/local/sbin/configure-et-board-clock` with `ET_BOARD_TDP_W=0`, `ET_MINION_FREQUENCY_MHZ=600` and
  `ET_NOC_FREQUENCY_MHZ=400`. The script sends
  `dev_mngt_service -m DM_CMD_SET_MODULE_STATIC_TDP_LEVEL -l 0`, then `DM_CMD_SET_FREQUENCY -f 600,400`.
  - Its stated reason: "aifoundry3's ET-SoC1 becomes unreliable when firmware DVFS raises the minion clock
    above its 600 MHz minimum … Keep the board at the supported 600/400 MHz point by setting a zero-watt
    software TDP ceiling."
  - This boot's marker `/run/et-board-clock-guard.ok` reads
    `56c9e0bf-1bf0-4c9c-969e-cf52d66bf565 600 400 0`, which is the current boot_id.
  - This contradicts "the reason is a flashed zero" in 14-card-behaviour.md / E21. Saved in
    `facts/aifoundry3/clock-guard*.txt`.
- **aifoundry3 runs a different `libetrt.so`** from aifoundry2: 1.6 MB, 2026-07-23, an "event-id guard" build
  that probably matches upstream `06dfe1302` "runtime: allocate unique event IDs across wraparound". Our
  `sparsity_host` links `/opt/et/lib/libetrt.so` dynamically, so `*_host` runs on the two cards do not use the
  same runtime binary.
- **aifoundry1's kernel log is being flooded**: `kern.log` is 279 MB and grows about 850 B/s, against well
  under 1 MB on the other two. The ET IRQ lines are silent, so it is probably not the cards, but the source
  cannot be seen without `adm`.
- **All three machines will boot 7.0.0-34 at their next reboot** (installed 2026-09-24). DKMS has built
  et_soc1 for it everywhere, and on aifoundry1 that build is broken the same way.

## Unknowns

- Who or what loads et_soc1 on aifoundry1 at boot +3m42s. It is not modules-load.d or udev. Candidates: the
  root GitHub Actions runner job, a cron `@reboot`, or a person. None of these is visible to a user.
- The firmware and PMIC versions and the device state of aifoundry1's cards, which cannot be read until the
  version is fixed.
- The source of aifoundry1's kernel-log flood.

## Files

Everything is under `/tmp/claude-1019/-home-yaroslavvb-claude/ed6d06d5-de26-4323-94f1-0dc808eafbda/scratchpad/aif1/`:

- `collect.sh`: the read-only collector, which was run on all three hosts. It never opens `/dev/et*`.
- `facts/aifoundry{1,2,3}/collect.txt`: raw output from each host.
- `facts/aifoundry{1,2,3}/usr-src-et-soc1.sha256`, `opt-et-hashes.txt`: source and binary hashes.
- `facts/aifoundry1/`:
  - `earlier-attempts-2026-09-22.txt`: verbatim tool outputs from E21;
  - `modinfo-extra.txt`: module version for both kernels, the Makefile, and the esperanto module;
  - `usr-src-et-platform-et-driver.txt`: the fixed source already on the host;
  - `log-growth-and-irqs.txt`;
  - `load-origin.txt`;
  - `ps-users.txt`.
- `facts/aifoundry3/clock-guard.txt`, `clock-guard-scripts.txt`.
- `facts/next-kernel-module-versions.txt`.
- `facts/source/`:
  - `DevicePcie-check.txt`;
  - `et-platform-09531e5c1-introduces-typo.patch`;
  - `et-platform-78ed9b0d6-fix-version-on-dkms-build.patch`;
  - `driver-commit-hashes.txt`: the hash match of each host's driver source to a commit;
  - `mkdemo/`: the Makefile typo reproduction.
