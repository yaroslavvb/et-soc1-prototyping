# Resources: what existed before any measurement

Every finding in this directory rests either on one of these resources or on an experiment in
[03-experiments.md](03-experiments.md). Each entry says what the resource is authoritative for and, as
importantly, what it is **not** authoritative for. Cite them as **R1**...**R14**.

---

## R1 — Esperanto manuals (`external/et-man/`, gitignored clone)

PDFs plus a `txt/` directory of extracted text: *ET Programmer's Reference Manual* (PRM), *ET Preliminary
Datasheet Rev 1.0*, *ET-SoC Errata*, *ET Minion Overview*, *ET Introduction*, *ET-PCIe-Dev-Card-V3*.

- **Authoritative for:** the instruction set, CSR numbers and bit layouts, the TensorFMA32 pseudo-code
  (PRM §9.4, which is where the `if (a != 0 && b != 0)` zero-skip rule is written), errata, the shire and
  mesh topology, board-level regulators.
- **Not authoritative for:** anything about power in watts, anything about this particular card's firmware
  policy, and at least one known documentation bug (the fp16 zero-skip rule in the PRM does not match
  silicon; see [15-earlier-findings.md](15-earlier-findings.md)).
- **Used by:** E1, E11, E13, E22–E24 (the scratchpad address format; errata 4.1 and 4.2 for E23), E31–E32 (the
  datasheet's 8 × 6 mesh, via R14), A13, and the TensorFMA micro-op ordering in `rtl-sim/fma_toggle/tb.sv`.

## R2 — Open RTL of the core (`external/core-et/`, gitignored clone)

The Erbium branch at commit `b38a1a3`: the same Minion core lineage as the ET-SoC-1, in a later MCU-class
configuration. `external/core-et-main/` holds the `main` branch, a Verilator-first re-implementation.

- **Authoritative for:** the structure of the fused multiply-add unit (`rtl/shire/minion/vpu/txfma_7s/txfma_top.v`,
  seven pipeline stages), the zero-gating logic (`vpu_ctrl.v`, signal `ex_fma_gate_mask`), the lane clock gate
  (`vpu_lane.v`), the PMU counter carry bug (`rtl/shire/neigh/neigh_pmu.v`), the register primitives
  (`rtl/libs/registers/{ff,en_ff,rst_ff,rst_en_ff}.v`) that `rtl-sim/fma_toggle` replaces with instrumented copies,
  and the per-cycle compute peaks in `docs/Minion VPU Specification.pdf` (A19).
- **Not authoritative for:** timing of the taped-out A0 silicon, physical capacitance or energy. There is no
  cell library, netlist or power flow in the drop, so an RTL "net toggle" is a **named signal transition, not a
  charge**. Every joule in this work comes from measuring the card, never from the RTL.
- **Used by:** E2, E11, E13, E31–E32 (`axi_defines.vh`, `shirecache_mesh_master.sv`, via R14), A11 (the sleep and
  isolation ports), A19.

## R3 — Firmware source and installed tooling (`external/et-platform/`, `/opt/et`)

The firmware source, read at `353f20e` (the lab machines' `/opt/et` is built from that commit; `clone-upstream.sh`
checks out `836a4ab`, and `device-bootloaders/src/ServiceProcessorBL2/` is identical at both), plus the installed
runtime, `sys_emu` functional simulator, and `libDM.so` management library. **Which firmware the cards run is not
established:** their own trace strings match an older service-processor build, from before et-platform commit
`60b40c10f` (24 September 2024, "Dvfs fixes and refactoring", which reworked the governor), and both cards report release 1.3.1. Read every
statement below about the governor as a statement about the `353f20e` source.

- **Authoritative for:** the service processor's power and thermal policy. The two thresholds quoted
  throughout this work are read directly from the source:
  `TEMP_THRESHOLD_SW_MANAGED 65` and `POWER_THRESHOLD_SW_MANAGED 65` in
  `device-bootloaders/src/ServiceProcessorBL2/include/thermal_pwr_mgmt.h`, with the decision logic in
  `check_power_throttle_conditions()` of `services/thermal_pwr_mgmt.c` (thermal branch first, then power).
  The hardware catastrophic limits `TEMP_THRESHOLD_HW_CATASTROPHIC 75` and
  `POWER_THRESHOLD_HW_CATASTROPHIC 75` are in `include/bl2_pmic_controller.h`. **Observed, not explained:** in every
  session here the PMIC reading tracked the minion-shire reading within a degree, and both sat at 80–90 °C for
  hours with no catastrophic event, so that 75 °C limit must apply to a different sensor or not be armed on
  this card. Do not rely on it.
- **Not authoritative for:** what the card actually did on any given day. The governor's behaviour was
  measured in E10.
- **Used by:** E4, E21, the governor explanation in [14-card-behaviour.md](14-card-behaviour.md) and
  [16-dvfs-and-leakage.md](16-dvfs-and-leakage.md); `tools/ettelem` links against `libDM.so` from this install.

## R4 — Earlier reports in this repository (2026-09-18, before this line of work)

`docs/reports/2026-09-18-*.html`: matmul efficiency, memory hierarchy, on-chip communication, sparsity.
Their raw data is under `docs/reports/data/2026-09-18-*/`. The memory-hierarchy and on-chip communication sessions
were registered on 25 September as E33 and E34 in [03-experiments.md](03-experiments.md), with their claims in
[05-claims.md](05-claims.md).

- **Authoritative for:** the throughput and efficiency baselines quoted here (fp32 9.5 TFLOP/s, fp16 19.0,
  int8 71.8 TOP/s on `kernels/mmbench`), the mesh latencies, and the original sparsity result that the tensor
  unit's zero-skip saves energy but not cycles. That last one is the direct ancestor of everything in
  [10-data-dependent-power.md](10-data-dependent-power.md).
- **Caveat:** the sparsity work ran on **aifoundry3**, a different card from the one used throughout
  2026-09-19 onwards. Do not mix its absolute watts with this card's.

## R5 — The card and the lab

`aifoundry2`, one ET-SoC-1 PCIe card, 1,088 minion cores (1,024 usable for these workloads across 32 compute
shires), 32 GB LPDDR4X, in a desktop chassis. Reached over Tailscale SSH.

- **Authoritative for:** everything measured. Note that it is *one* card in *one* chassis: the thermal
  resistance in [11-thermal-model.md](11-thermal-model.md) is a property of this installation, not of the chip.
- **Etiquette (set by the repo owner, in `CLAUDE.md`):** ask which machine to use, check `uptime`/`who`/
  `lsmod | grep et_soc1` (third column is open handles) before touching a card, keep builds to `nice -j4`, and
  do not reset a card yourself (ping the lab admin). The original 10-second hold limit was **waived by the
  repo owner on 2026-09-21** for the long-run experiments (see Q13 in [02-requests.md](02-requests.md)); every
  other session kept each kernel process under 10 s. The telemetry sampler (`ettelem sample`) held the single-opener
  management node for whole sessions (up to 2.6 h in E27).

## R6 — Esperanto's own design argument (external, public)

- D. Ditzel et al., *Accelerating ML Recommendation with over a Thousand RISC-V/Tensor Processors on
  Esperanto's ET-SoC-1 Chip*, **Hot Chips 33** slides, 2021:
  <https://hc33.hotchips.org/assets/program/conference/day2/HC2021.Esperanto.Dave_Ditzel.presentation.v1submitted.pdf>
- Same title, **IEEE Micro 42(3)**, May/June 2022:
  <https://www.esperanto.ai/wp-content/uploads/2022/05/Dave-IEEE-Micro.pdf>

- **Authoritative for:** what Esperanto *intended*: the equation `Power = Cdynamic × Voltage² × Frequency +
  Leakage`, the target of 10 mW per core at 1 GHz and 0.425 V with 0.04 nF of switched capacitance, the
  voltage study (275 W at the highest voltage, 164 W at 0.75 V, 118 W at 0.67 V, about 20 W at 0.4 V, 8.5 W at
  the 0.3 V efficiency peak), and the chip facts (TSMC 7 nm, over 24 billion transistors, 570 mm², 89 mask
  layers, 1,088 minions, 256-bit LPDDR4x at 137 GB/s, operating range 300 MHz to 2 GHz).
- **Not authoritative for:** this card. The voltage curve is **modelled**, with cores re-synthesised at each
  voltage point, and the 20 W headline is a chip figure at an operating point this card's firmware never uses.
  Quotes and page context are transcribed in `docs/research/why-low-power.md`.

## R7 — NVIDIA A100 datasheet (external, public)

<https://www.nvidia.com/content/dam/en-zz/Solutions/Data-Center/a100/pdf/nvidia-a100-datasheet.pdf>

- **Authoritative for:** 400 W TDP (SXM4), 19.5 TFLOPS fp32, 312 TFLOPS fp16/bf16 tensor, 624 TOPS int8, HBM2 at
  1,555 GB/s (40 GB; the 80 GB HBM2e part is 1,935–2,039 GB/s), 1,410 MHz maximum boost clock. The transistor count
  (54.2 billion), die area (826 mm²) and process (TSMC 7 nm) are from the Ampere architecture whitepaper, p. 14.
- **Not authoritative for:** core voltage, which NVIDIA does not publish. **The 0.85 V used in
  [13-why-low-power.md](13-why-low-power.md) is an assumption**, and the sensitivity to it is stated there.

## R8 — Horace He, "Strangely, Matrix Multiplications on GPUs Run Faster When Given 'Predictable' Data!"

<https://www.thonking.ai/p/strangely-matrix-multiplications> (April 2024).

- **Authoritative for:** the A100 measurements this whole line of work reproduces: an 8192³ **bf16** matmul at
  257 TFLOPS on random data against 295 TFLOPS on zeros, with a 330 W power limit and 88 W idle, and the
  mechanism sentence, "A small amount of power is consumed whenever a transistor *switches states*."
- **Note on direction:** the post's finding is that **predictable data uses less power**. An earlier draft of
  our report had this reversed; it was corrected before publication.

## R9 — David Kanter's account of chip power management (external, a conversation)

A conversation of about 25 minutes with David Kanter (MLCommons) on 20 September 2026, in private notes. The notes
are not published: they were briefly public and were made private on 24 September 2026 (see
[04-artifacts.md](04-artifacts.md)). Only the technical content below is used here, and it is a paraphrase, not his
words.

- **Authoritative for:** how a mature design is *expected* to manage power, and as the reference class for
  normal: a DVFS loop driven by an internal activity-based power estimator on millisecond timescales
  (`P = C_switching × V² × f`, with V and f known and C the unknown), thermal sensors inside the same loop,
  cache data arrays behind leakage-suppression transistors un-suppressed about 10% at a time at a small wake-up
  latency, and leakage as typically 5–30% of a design's power, about 20% being common. Also the MLPerf context:
  inference is being normalised by **provisioned** power, not measured, because measurement is expensive in time
  and energy.
- **Not authoritative for:** this chip. He said so himself: this might not hold for Esperanto's part, only for
  designs from a more mature company. [16-dvfs-and-leakage.md](16-dvfs-and-leakage.md) checks each claim against
  the firmware, the RTL and the card.
- **Note:** the notes paraphrase a conversation; they are not a written source. Where they matter they are
  treated as a hypothesis to test, never as evidence.

## R10 — The other two lab machines

`aifoundry1` (two ET-SoC-1 cards) and `aifoundry3` (one), reached over Tailscale SSH the same way as R5. Note
that `/etc/hosts` on aifoundry2 carries stale LAN addresses for both; `~/.ssh/config` pins the Tailscale
addresses instead.

- **Authoritative for:** that these cards exist, their firmware and PMIC revisions, and — for aifoundry3 —
  everything measured in E20–E27, E29, E31 and E32 (E23 without power, E28 not at all).
- **Not authoritative for:** anything about aifoundry1's silicon before 25 September 2026. Its cards could not be
  opened until then (E21; fixed that day, 14-card-behaviour.md). Since then card 1 (firmware 1.2.0) runs the
  version-3 campaign; card 0 (firmware 1.4.1) overheats under load and is excluded.
- **Caveat that matters:** aifoundry3 is **not** a drop-in replacement for aifoundry2. It idles 25 °C cooler,
  its heatsink sheds heat faster, and its firmware holds it at 600 MHz because a boot service sets its TDP to 0 W at every boot (E21, corrected
  2026-09-25 in 14-card-behaviour.md).
  Absolute watts from the two cards are not comparable; switching power over idle is.
- **Used by:** E20–E27, E29, E31, E32. R4's sparsity work also ran on aifoundry3, which is why its absolute watts must not
  be mixed with aifoundry2's.

## R11 — Ivan's benchmark result (external, a Discord message)

A result reported in Discord: one global atomic counter in shire 0's scratchpad, all 32 shires hammering it,
about 60 million atomics a second in aggregate, the 31 non-owning shires splitting the work evenly, and
**shire 0 getting 6% of its fair share and finishing only after the other 31**.

- **Authoritative for:** nothing about this card by itself. It is one person's measurement of their own code,
  reported informally, and we do not have that code.
- **Useful for:** the question. It is the only claim anyone had made about many-to-one contention on a shire
  cache here, and it pointed at a line in `docs/research/counters-and-dram.md` that was an unverified reading
  of the SCspec with no experiment behind it.
- **What checking it produced:** the aggregate rate reproduces exactly (E22). The 6% does not: the atomic is
  shared to within half a percent (every shire between 0.998 and 1.004 of an even split), including with the host
  shire. What is starved is the host shire's
  **own** memory path, completely (E23). See [17-hot-line.md](17-hot-line.md).
- **Treated as:** a hypothesis to test, never as evidence. Where the two disagree, this work reports its own
  measurement and says plainly that Ivan's code was not run.

## R12 — The L2-mainline-starvation brief (a sibling analysis, external to this line of work)

<https://spacesheep.dev/@yaroslavvb/2026-09-22-et-soc1-l2-mainline-starvation>, written the same day from the
same repository state (`b36acd6`) and from R11.

- **Authoritative for:** nothing measured. It is an argument, not an experiment, and it says so.
- **Useful for:** two things this work took from it and checked. First, that the register-to-register path
  (`TensorSend`/`TensorRecv`) never touches the shire cache, so it is immune to the contention in
  [17-hot-line.md](17-hot-line.md). Second, the warning that a two-dimensional systolic array — every cell
  receiving from two partners — hangs a hart permanently, because the hardware keeps one ready flag per
  minion and not one per partner (`docs/et-soc1-notes.md`). That warning is why
  [18-on-chip-relay.md](18-on-chip-relay.md) is built at shire granularity on the scratchpad rather than as a
  mesh of TensorSend cells.
- **Where this work disagrees with it:** it repeats R11's 6% figure as measured fact and builds on it. E22
  did not reproduce that figure; see [17-hot-line.md](17-hot-line.md). The brief is kept, corrected in place with an
  Update box pointing to the hot-line report, and its source is now in the repository
  (`docs/reports/2026-09-22-et-soc1-l2-mainline-starvation.html`).

## R13 — The service processor's PMIC and PVT drivers (firmware source, read for E30)

`external/et-platform/device-bootloaders/src/ServiceProcessorBL2/driver/pmic_controller.c`,
`driver/pvt_controller.c`, `include/bl2_pvt_controller.h`, `include/pmic_hal.h`, `services/thermal_pwr_mgmt.c`
at commit `353f20e`.

- **Authoritative for:** what the meters are. The PMIC exposes PMBus statistics for three regulators (minion,
  NoC, SRAM) — v_out, a_out, w_out, v_in, a_in, w_in, deg_c, each as a current value, a minimum and maximum since
  reset, and a running average, 84 reads a pass — and set-point registers only for DDR, VDDQ, VDDQLP, PCIe logic,
  PCIe, Maxion and the L2/SRAM rail. The SP copies the PMIC's own running average of w_out (roughly first-order,
  τ ≈ 1.15–1.22 s as E27 measured it; the SP does no filtering) with its min and max, and forwards the input power. The Moortec PVT subsystem: 5 controllers × (8 temperature
  sensors, 2 × 16-channel voltage monitors, 8 process detectors); 35 temperature sensors live and 35 process detectors
  populated (one of each per minion shire plus one in the IO shire); 125 voltage
  points (3 per minion shire, 2 per memory shire, 3 IO shire, 2 PCIe shire, 2 external analog); the host gets
  averages, the DEBUG trace gets per-shire voltages, per-shire temperature is not exported, the process
  detectors are configured with measurement disabled and never read, the external analog inputs have a stub reader.
- **Useful for:** E30 and the observability report's §4 and improvement ladder.
- **Treated as:** the truth about this firmware; not exercised beyond the reads ettelem already makes.


## R14 — Wire-energy literature and the die's geometry (external, public; read for Q41)

Collected on 2026-09-24 by a research workflow of seven AI agents (four researchers, two adversarial verifiers, one
synthesis); `docs/reports/data/2026-09-24-wire-energy/research/SYNTHESIS.md` quotes every source with its URL and
page.

- **Dally's figure:** "Communication (~100fJ/b-mm on-chip)", AHA retreat keynote 2023, slide 8; the same
  100 fJ/bit-mm in Dally, Turakhia and Han, CACM 2020. Neither states a node, a voltage or a data activity.
- **Figures with conditions:** Keckler, Dally et al., IEEE Micro 2011, Table 1 (40 nm, 0.9 V: 310 pJ for 256
  bits over 10 mm, 121 fJ/bit·mm on random data); Dally's 10 nm projection (174 pJ per 256 bits over 10 mm,
  68 fJ/bit·mm); Dally et al., VLSI Symposium 2018 (20–40 fJ/bit-mm, 16 nm, about 200 fF/mm); Ho's 2003
  thesis (measured, 0.18 µm, 1.8 V).
- **The die:** 570 mm² (Hot Chips 33 slide 20; IEEE Micro 42(3), 2022, p. 37); the tile pitch measured in
  pixels on the published die plot (IEEE Micro 2022, Fig. 7) scaled to that area: 3.73 mm in x, 3.70 mm in y,
  3.72 mm per hop (3.64–3.74 over three readings of what the area covers). The mesh is 8 × 6 stops (ET
  Preliminary Datasheet Rev 1.0, ch. 4).
- **The link:** 512 bits per beat at the mesh master port (`core-et` `axi_defines.vh:43`), four lanes chosen
  by PA[7:6] (`shirecache_mesh_master.sv`); the NoC at 400 MHz and 0.485 V from telemetry.
- **Authoritative for:** what the literature's per-mm numbers mean and the millimetres per hop.
- **Not authoritative for:** the wire's own capacitance on this chip (no layout is public), or how many
  millimetres of metal a hop really crosses; the pitch is centre to centre.
- **Treated as:** external inputs of kind `X`; the pitch is an estimate (kind `A`) with its range carried into
  every per-mm bar.
