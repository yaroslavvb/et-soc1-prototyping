# Resources: what existed before any measurement

Every finding in this directory rests either on one of these resources or on an experiment in
[03-experiments.md](03-experiments.md). Each entry says what the resource is authoritative for and, as
importantly, what it is **not** authoritative for. Cite them as **R1**...**R10**.

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
- **Used by:** E1, E11, E13, and the TensorFMA micro-op ordering in `rtl-sim/fma_toggle/tb.sv`.

## R2 — Open RTL of the core (`external/core-et/`, gitignored clone)

The Erbium branch at commit `b38a1a3`: the same Minion core lineage as the ET-SoC-1, in a later MCU-class
configuration. `external/core-et-main/` holds the `main` branch, a Verilator-first re-implementation.

- **Authoritative for:** the structure of the fused multiply-add unit (`shire/minion/vpu/txfma_7s/txfma_top.v`,
  seven pipeline stages), the zero-gating logic (`vpu_ctrl.v`, signal `ex_fma_gate_mask`), the lane clock gate
  (`vpu_lane.v`), the PMU counter carry bug (`shire/neigh/neigh_pmu.v`), and the register primitives
  (`libs/registers/{ff,en_ff,rst_ff,rst_en_ff}.v`) that `rtl-sim/fma_toggle` replaces with instrumented copies.
- **Not authoritative for:** timing of the taped-out A0 silicon, physical capacitance or energy. There is no
  cell library, netlist or power flow in the drop, so an RTL "net toggle" is a **named signal transition, not a
  charge**. Every joule in this work comes from measuring the card, never from the RTL.
- **Used by:** E2, E11, E13.

## R3 — Firmware source and installed tooling (`external/et-platform/` at `353f20e`, `/opt/et`)

The commit that matches the firmware running on aifoundry2's card, plus the installed runtime, `sys_emu`
functional simulator, and `libDM.so` management library.

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
- **Used by:** the governor explanation in [14-card-behaviour.md](14-card-behaviour.md); `tools/ettelem`
  links against `libDM.so` from this install.

## R4 — Earlier reports in this repository (2026-09-18, before this line of work)

`docs/reports/2026-09-18-*.html`: matmul efficiency, memory hierarchy, on-chip communication, sparsity.
Their raw data is under `docs/reports/data/2026-09-18-*/`.

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
  other session in this work kept to it.

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

- **Authoritative for:** 54.2 billion transistors, 826 mm², TSMC 7 nm, 400 W TDP (SXM4), 19.5 TFLOPS fp32,
  312 TFLOPS fp16 tensor, 624 TOPS int8, HBM2e at 1,555 GB/s, 1,410 MHz maximum boost clock.
- **Not authoritative for:** core voltage, which NVIDIA does not publish. **The 0.85 V used in
  [13-why-low-power.md](13-why-low-power.md) is an assumption**, and the sensitivity to it is stated there.

## R8 — Horace He, "Strangely, Matrix Multiplications on GPUs Run Faster When Given 'Predictable' Data!"

<https://www.thonking.ai/p/strangely-matrix-multiplications> (April 2024).

- **Authoritative for:** the A100 measurements this whole line of work reproduces: an 8192³ matmul at
  257 TFLOPS on random data against 295 TFLOPS on zeros, with a 330 W power limit and 88 W idle, and the
  mechanism sentence, "A small amount of power is consumed whenever a transistor *switches states*."
- **Note on direction:** the post's finding is that **predictable data uses less power**. An earlier draft of
  our report had this reversed; it was corrected before publication.

## R9 — David Kanter's account of chip power management (external, a conversation)

Notes from a ~25-minute conversation with David Kanter, founder of MLPerf / MLCommons, on 20 September 2026,
written up as a research brief: <https://spacesheep.dev/@yaroslavvb/david-kanter-power-brief>.

- **Authoritative for:** how a mature design is *expected* to manage power, and as the reference class for
  "normal": a DVFS loop driven by an internal activity-based power estimator on millisecond timescales
  (`P = C_switching × V² × f`, with V and f known and C the unknown), thermal sensors inside the same loop,
  cache data arrays behind leakage-suppression transistors un-suppressed ~10% at a time at a small wake-up
  latency, and leakage as "typically 5–30%, ~20% common". Also the MLPerf context: inference is being
  normalised by **provisioned** power, not measured, because measurement is expensive in time and energy.
- **Not authoritative for:** this chip. He said so himself — "maybe not on Esperanto's part, but on anything
  from a more mature company". [16-dvfs-and-leakage.md](16-dvfs-and-leakage.md) checks each claim against the
  firmware, the RTL and the card.
- **Note:** the notes are a paraphrase of a conversation, not a written source. Where they matter they are
  treated as a hypothesis to test, never as evidence.

## R10 — The other two lab machines

`aifoundry1` (two ET-SoC-1 cards) and `aifoundry3` (one), reached over Tailscale SSH the same way as R5. Note
that `/etc/hosts` on aifoundry2 carries stale LAN addresses for both; `~/.ssh/config` pins the Tailscale
addresses instead.

- **Authoritative for:** that these cards exist, their firmware and PMIC revisions, and — for aifoundry3 —
  everything measured in E20 and E21.
- **Not authoritative for:** anything about aifoundry1's silicon. Its cards cannot be opened (E21), so no
  measurement of any kind was taken from them.
- **Caveat that matters:** aifoundry3 is **not** a drop-in replacement for aifoundry2. It idles 25 °C cooler,
  its heatsink sheds heat faster, and its firmware pins it at 600 MHz because its flashed TDP is 0 W (E21).
  Absolute watts from the two cards are not comparable; switching power over idle is.
- **Used by:** E20, E21. R4's sparsity work also ran on aifoundry3, which is why its absolute watts must not
  be mixed with aifoundry2's.
