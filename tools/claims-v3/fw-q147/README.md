# fw-q147: the counter-configure firmware patch, a desk study (Q147 item 6)

*Thu 5 Nov 2026 (week 45), about 23:00-23:50 PST, desk only: no card, no device command, no lab box. It answers item 6 of the
owner's answers of Thu 5 Nov 2026 (Q147): "feel free to use patched firmware if it helps, make sure to follow Roman's guidelines
to avoid breaking the card". The patch is [`patches/0003-pmc-configure-syscall-353f20e.patch`](../../../patches/0003-pmc-configure-syscall-353f20e.patch)
(E4, 20 Sep 2026). Public facts only: the lab's committed data and records, and public source at pinned commits.*

## Results first

1. **It does not help the open problems.** For the anatomy's op rate, the power viruses' issue rate (E179), the governor model,
   the card-to-card gap and class S, the counters it unlocks would either re-count what the stock firmware's counters and the
   launch records already give, or cannot see the quantity at all (joules, volts, bit toggles, the service processor's governor).
   No frozen or planned prediction would change (table below). Its real use is memory-path observability, which is not this
   blog's core, and even there two stock syscalls give the first numbers with no firmware change.
2. **Loading it risks a power cycle and the card, so it waits for the owner's word.** The minion firmware lives in each card's
   SPI flash image. Putting the patch on a card is a firmware update that rewrites the card's other flash bank and runs the PMIC
   firmware-update path, then a card reset to boot it, and the same again to undo it. At BL2 0.22.0 a card reset goes through the
   PMIC and may power-cycle the card ([`AGENT.md`](../../../AGENT.md), the owner's rule 1 of 2 Nov 2026), and the lab's rules
   forbid firmware work and card resets outright. A minion image that fails to load stops the service processor before the
   host can reach the card, and no independent recovery path exists on the lab's cards. By the maintainer's guidelines,
   firmware changes stay with him.
3. **Verdict: not worth doing; not attempted.** Nothing in this study touched a card. If the owner still wants it, the decision
   and the work are his and the firmware maintainer's (below).
4. **A name to keep apart:** "Roman's patch 0003" in [`../e89/E89.md`](../e89/E89.md) (line 27) is the firmware maintainer's
   per-sensor temperature patch for the service processor (command 74, aifoundry3's thermal build of 7 Oct 2026). The lab's
   `patches/0003-pmc-configure-…` is a different patch, to the minion firmware, and is on no card.

## Builds on

- **Checked:** the private prior-work inventory, read Thu 5 Nov 2026 at about 23:00 PST: public rows L02, L03, L06, P02, P03,
  P05, P11, P12, P27, H09, H23, H28 (opaque pointers).
- **Used:** E4's patch and `workloads/pmcsel` (`584b9a66`); the lab's counter map
  [`docs/research/counters-and-dram.md`](../../../docs/research/counters-and-dram.md) (20 Sep, research only); E2's carry erratum
  (`rtl-sim/pmu_carry/`); E3's `traceprof` (retired-instruction counts read on silicon); the energy catalogue's issue rates, as the
  anatomy's dated note carries them (`538c98ce`); the anatomy's op rate (`538c98ce`); E171's and E172's reductions (pool 8);
  E69's, E72's and E118's change records; the firmware identity reads of E69, E79, E82 (A1) and E84 (A1);
  [`docs/findings/14-card-behaviour.md`](../../../docs/findings/14-card-behaviour.md)'s hosts table; `tools/lab/et-reset`; et-platform
  `836a4ab60` and `353f20e` (`external/et-platform`); core-et `b38a1a3` (`external/core-et`).
- **Not used:** sys_emu as a counter source (it models only the cycle and retired-instruction events: `workloads/pmcsel/README.md`);
  the RTL toggle bench (it counts toggles, not the card's events); ETASP (not applicable).
- **Tiers:** public only; nothing from a private tier is used or cited.

## 1. What the patch adds, and what the stock firmware already gives

**The patch** adds U-mode syscall 12 (`SYSCALL_PMC_CONFIGURE`) to the Machine Minion's M-mode handler, passed through by the
Worker Minion. A kernel can choose the events of `hpmcounter4`-`hpmcounter8` for its own hart (`mhpmevent3` is refused: the
firmware's cycle time stamp), and write the performance-monitor qualifiers and control word of any shire-cache bank (shire 0-32,
bank 0-3) or memory shire (0-7). It was built and checked only in sys_emu (E4). The five files it touches or relies on, and the
default counter setup, are byte-identical at et-platform `353f20e` and `836a4ab60` (same git blobs), so it applies unchanged to
the public source of the BL2 0.22.0 line.

**What it would let a kernel count** (public lists: `et-common-libs/include/etsoc/drivers/pmu/pmu.h:129-182` at `836a4ab60`; the
PRM's Tables 1-3 and 1-4; core-et `rtl/inc/pmu_types.vh`): TensorFMA instructions; fp32, fp16a32 and integer TensorFMA ops and int8
ops; cycles the TensorFMA waits on TenB; tensor loads and stores; D-cache accesses and misses per thread; L2 miss requests, their
rejections and evictions; TRANS, SHORT and MASK ops; TensorReduce and TensorQuant instructions; neighbourhood ET-Link, cooperative
load/store, I-cache and page-walk traffic; shire-cache hits and misses by operation class and the occupancy modes (mean miss
latency by Little's law); memory-shire qualified reads and writes. The hardware sums counters 3-6 over the 8 minions of a
neighbourhood (one copy for even harts, one for odd), so even a per-hart choice reads out as a neighbourhood sum
([`counters-and-dram.md`](../../../docs/research/counters-and-dram.md) § 1.1).

**In the open RTL the tensor-op events are control events:** core-et `rtl/shire/minion/vpu/vpu_ctrl.v:1681-1699` raises the
TensorFMA op events from the pipeline's qualified valid and the op type, and `TFMA_INST` from the instruction start; the zero gate
acts on the lanes below that. So there an op count is the same for every kind of number. (core-et is a later configuration of the
design, not the taped-out RTL.)

**The stock firmware, no patch** (`836a4ab60` = `353f20e` here): `device-minion-runtime/src/MachineMinion/src/main.c:50-112` sets,
once at boot, `hpmcounter3` = cycles (free-running), `hpmcounter4`/`5` = retired instructions of thread 0 / thread 1,
`hpmcounter6` = L2 miss requests, `hpmcounter7`/`8` = I-cache requests and I-cache misses to L2; each shire-cache bank's P0 = all
L2 reads and P1 = all writes; each memory shire's P0/P1 = all mesh reads / writes. U-mode reads `hpmcounter3-8`
(`mcounteren`, `MachineMinion/src/main.c:145`; `scounteren`, `WorkerMinion/src/main.c:69`); `hpmcounter4-8` are zeroed before every
launch (`MachineMinion/src/syscall.c:283-306`); syscalls 9 and 10 sample any shire-cache bank and any memory shire
(`WorkerMinion/src/syscall.c:69-73`). The firmware declares an MM-to-compute "PMC configure" message but nothing sends or handles
it (`et-common-libs/include/transports/mm_cm_iface/message_types.h:85, 116`), so no host or trace path chooses events. On silicon,
E3's `traceprof` read cycle stamps and retired-instruction counts summed by the hardware over a neighbourhood
([`workloads/traceprof/README.md`](../../../workloads/traceprof/README.md) lines 21-22).

## 2. Does it help? The five problems

| problem | what the counters would measure | change to a prediction | the route that exists now |
|---|---|---|---|
| **The anatomy's op rate** | TensorFMA instructions or ops per neighbourhood inside each launch | **none.** E171's fp32 random rate is 1.1171e9 steps a second from the launch records against 1.1253e9 from 546.001 cycles a step alone (the anatomy, `538c98ce`, [README](../../../docs/reports/data/2026-11-05-q145a-anatomy-top-lines/README.md) lines 67-69; post hoc); the 0.73% gap is the launch gaps (fp32 randn's duty 0.9928, [`e171.json`](../../../docs/reports/data/2026-11-05-e171-blind8-aifoundry3/e171.json)). Counters are zeroed before every launch, so they cannot see gaps, and inside a launch they would re-count what the cycle counter says. | the stock cycle counter and the launch records, as the anatomy does |
| **The viruses' issue rate (E179)** | issues a hart-cycle | **none beyond the stock counters.** The rate matters (the catalogue's two-hart random rows run 0.30-0.45 issues a hart-cycle; `fmadd.ps` 0.3649, 0.730 a minion-cycle, one hart 0.5814; measured 26 Sep, from the anatomy's [dated note](../../../docs/reports/data/2026-11-05-q145a-anatomy-top-lines/NOTE-2026-11-05-fmadd-ps-public-facts.md), `538c98ce`, lines 43-50), but `hpmcounter4`/`5` over `hpmcounter3`, or the kernel's own loop count over device cycles, measure it with the stock firmware, as the catalogue did for 150 instructions. | stock `hpmcounter3-5` in E179's own kernel (a change to the published kernel, so it belongs in E179's registration), read with `HPM_SAFE_READ` (Errata 1.23) and the carry fix (E2) |
| **The governor model** | nothing the governor uses | **none.** Its misses are the service processor's idle reset, a heartbeat landing between kernels (E100: 39 of 39 heartbeats in a gap fell, 0 of 234 inside kernels); E173's pinned clock 7.01 MHz rms, 0.07 MHz over the 17 tiles with no dipped pass (blind; the split post hoc; 05-claims.md line 4112); E175's governed clock 4.49 MHz rms (blind). Minion counters see neither the service processor nor the gaps. | the committed SP rings, Q132(g)'s lattice, one kernel per burst (E100's N arm), a counted dip term |
| **The card-to-card gap** (card 1's minion rail about 1.1x aifoundry3's after V²) | events, not joules or volts | **none.** The work per op is already equal: on all 71 items the two cards share in pool 8, the cycles a step are identical (546.001 fp32 and fp16, 318.0 int8) and the op rate of card 1 over aifoundry3 has median 0.9998 (0.9984-1.0009). After each session's own V² (0.914), card 1's minion-rail switching power is 1.103x aifoundry3's on 46 float items and 1.081x on 19 int8 items, the board 1.056x and 1.044x ([`posthoc-card-check.json`](posthoc-card-check.json); post hoc). The excess is energy per op; whether it is the rail meter, the silicon or the voltage reading, no counter can tell. | a calibrated meter or reference load on both cards (the owner's word), same-protocol re-runs, the public PMIC firmware's meter facts |
| **Class S and the register file** | op counts and stalls per kind | **none.** Op events do not depend on the data (open RTL); register-file switching is not an event; a stall would show as more cycles per op, and the stock cycle counter reads 546.001 / 318.0 for every kind on both 600 MHz cards (above). Class S stays M10's largest miss: 0.273 / 0.238 W rms on aifoundry3 / card 1 (blind, E171 / E172). | the measured per-position price lists as a registered term; Ditzel 2026's register-file caveat beside the bench |

**Where it would help, outside these five:** the memory path and the large-GEMM L3 map (G4's 30.2 MHz rms clock miss on E168,
blind, 05-claims.md line 3332; the stride steps): shire-cache hits and misses per bank, mean miss latency, D-cache misses. Even there the stock syscalls 9 and 10
already give each bank's reads and writes and each memory shire's mesh traffic, which is the cheaper first step.

## 3. What each card runs now (committed reads)

| card | release / BL1 / BL2 | PMIC | minions | read |
|---|---|---|---|---|
| aifoundry3 card 0 | 1.4.0 / 0.22.0 / 0.22.0 | 1.5.0 | 0.25.1 | E79, 31 Oct 2026 ([README](../../../docs/reports/data/2026-10-31-e79-fp16-int8-bit-prices/README.md) lines 617-629): the non-public thermal build first flashed on 7 Oct, which answers command 74 (E89) |
| aifoundry2 card 0 | 1.4.0 / 0.22.0 / 0.22.0 | 1.5.0 | 0.25.1 | E69, 27 Oct ([`../knob/CHANGE-RECORD.md`](../knob/CHANGE-RECORD.md)); its 10 Oct thermal-v2 update |
| aifoundry1 card 0 | 1.4.0 / 0.22.0 / 0.22.0 | 1.6.1 | 0.25.1 | E84 A1, 31 Oct; carried by module-uptime continuity since (E118; E174's gate, 5 Nov) |
| aifoundry1 card 1 | 1.4.0 / 0.22.0 / 0.22.0 | 1.3.0 | 0.25.1 | E82 A1, 31 Oct |

The host installs differ (aifoundry2 the stock `353f20e` build; aifoundry3 `353f20e` with a patched `libetrt.so`; aifoundry1 a local
fork build: [`14-card-behaviour.md`](../../../docs/findings/14-card-behaviour.md)), and only PMIC firmware 1.7.0 is public. The
cards' minions report 0.25.1, while the public `device-minion-runtime` declares 0.25.0 at both `353f20e` and `836a4ab60`
(`CMakeLists.txt:5`). So the exact source of the running minion images is not in the lab's hands, and a build of the patch from
public source would be a different minion build from the one each card runs.

## 4. The firmware maintainer's guidelines, and what loading the patch would take

**The guidelines.** The ET-SoC-1 firmware field manual (private; it is not in this repository) with its gates G0-G4 and its
change-record template, as E69, E72 and E118 used them ([`../knob/CHANGE-RECORD.md`](../knob/CHANGE-RECORD.md),
[`../lq6/CHANGE-RECORD.md`](../lq6/CHANGE-RECORD.md), [`../e118/CHANGE-RECORD.md`](../e118/CHANGE-RECORD.md)); and his posted guidance as
E118's record paraphrases it: no deviation from the manual's gates; firmware changes stay with him, because firmware failures can
brick a box; a wedged card or host is recovered by a host soft reboot and then an AC-outlet cycle through the lab's power switch,
which once left a host stuck until someone went to the lab. The lab's own rules ([`AGENT.md`](../../../AGENT.md)): never touch a
card's firmware (no OTA, no flashing), never reset a card; agents never run `et-reset` ([`tools/lab/et-reset`](../../lab/et-reset)
header).

**The path, from public source** (et-platform `836a4ab60`, `device-bootloaders/src/ServiceProcessorBL2/`):
1. **Build** the minion runtime with the patch, then wrap the images into **the card's own** flash image, keeping its per-card
   data and, on aifoundry3, the thermal service-processor build that answers command 74. The per-card images and the wrapping
   tools are the maintainer's.
2. **Update** (`services/firmware_update.c`): the service processor proceeds even if aborting the Master Minion's work fails
   (`:1083-1087`), writes the whole other flash partition (`:712-724`), rewrites its configuration region (`:752`), **calls the PMIC
   firmware update** (`:784`), and only then swaps the boot priority (`:793`).
3. **Reset** to boot it: `DM_CMD_RESET_ETSOC`, which at BL2 0.22.0 resets the card through its PMIC and may power-cycle it; then
   PCIe re-enumeration and a driver re-initialisation (on aifoundry1 the driver serves both cards).
4. **Check** identity, PMIC state, configuration, clocks and health; the firmware-revisions query is itself a PMIC command.
5. **Restore** the stock minions: a second update and a second reset.

**If the image does not boot.** BL2 loads and authenticates the three minion images at boot and, if one fails, logs "Waiting for
SOC RESET!!!" and spins (`common/main.c:431-432`, `:64-70`), before it launches the host command handler (`:445`) and before it
enables the PCIe link (`:478`); the same if the Master Minion threads fail to start (`:462-463`). The host then cannot reach the card
to update it again. BL1 also spins on its own failures (`ServiceProcessorBL1/src/bl1_main.c:354-361`), and the fallback to the other
bank is not in the public tree. No PMIC console, probe or programmer is established for the lab's cards (E72's and E118's records),
so recovery is the reboot and outlet cycle above, or someone at the lab.

**Signatures.** BL2 checks each image's signature and hash unless VaultIP is disabled or an OTP bit says to ignore signatures
(`services/firmware_loader.c:304-325, 621, 664-667`). Three cards are recorded as running the maintainer's rebuilt images since
7-10 Oct (aifoundry3, E89; aifoundry2, E69; aifoundry1 card 0, E118's record), and card 1's BL2 moved from 0.18.0 to 0.22.0 by
31 Oct (E82 A1). So E4's "needs a signed image" is not the barrier it looked on 20 Sep; the update path is.

**Other users of the shared cards.** The cards are shared with other people, CI runners (aifoundry1, aifoundry2) and a demo
(aifoundry3); an update needs one exclusive owner across all of them and the monitors. On aifoundry1 a driver or PCIe action takes
both cards, and a host reboot or outlet cycle ends every session on the host. aifoundry3's boot service sets its 0 W TDP (the 600
MHz pin) at boot and does not re-check after a reset (`tools/lab/et-reset` header). Every later run's firmware identity and its
command table would change.

**The patch's own hazards, found here.** (a) It never restores the boot defaults: the firmware zeroes `hpmcounter4-8` before each
launch but sets their events only at boot, so one kernel's choice persists into every later kernel on those harts, other users'
included, and, through the neighbourhood sums, into what neighbouring harts read. (b) Its shire-cache and memory-shire writes pass
raw control words, interrupt-enable bits included (bits 3, 7 and 20:
`etsoc-hal/include/etsoc_hal/inc/etsoc_shire_cache_esr.h:3163, 3107, 3023`), which the stock firmware never sets, for any shire,
and the Master Minion samples those same counters for the management statistics. A version for a card would restore the defaults
at kernel return, mask the interrupt bits and limit the writes to the caller's own shire.

**The gates, at the desk:** G0 (authorization) FAIL: no authorization for a firmware update or a reset, and the owner's rule of
2 Nov stands. G1 (recovery before risk) FAIL: no independent recovery path, and the lab holds no card's flash or PMIC backup. G2
(candidate provenance) FAIL: the running minions' source and the per-card images are not the lab's. G3 UNKNOWN. G4 not reached.
**NO-GO**, before value is weighed.

## 5. What to do instead

- **E179:** take the issue rate from the stock counters in its own kernel, or from its loop count over device cycles.
- **The anatomy:** keep the rate from the launch records and the cycle counter.
- **The governor:** the counted dip term, and one kernel per burst.
- **The card gap:** state it as energy per op at equal work per op (section 2).
- **Class S:** the per-position price term.
- **If the patch is ever wanted:** the owner's explicit word for one named card and window (lifting the no-power-cycle rule for
  it), the maintainer's own authorization and execution, an independent recovery path proved first, the patch fixed (section 4),
  and a filled change record committed with the data. Desk estimate: 60-90 minutes of exclusive time per card, the restore
  included, with the host's other users out during the resets. Not proposed.

## Files

- `README.md`: this note.
- [`posthoc_card_check.py`](posthoc_card_check.py): the post hoc check of section 2's card row (committed files only):
  `python3 -I tools/claims-v3/fw-q147/posthoc_card_check.py . tools/claims-v3/fw-q147/posthoc-card-check.json`.
- [`posthoc-card-check.json`](posthoc-card-check.json): its output.
