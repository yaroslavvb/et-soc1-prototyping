# Getting started on a new machine

> For the **results** rather than the machinery, read [findings/](findings/README.md): the findings from
> 19-22 September 2026, with a claim index that traces every number back to the experiment and the raw file
> it came from.

This page covers everything needed to pick the work up somewhere else: clone, connect to the lab, rebuild,
rerun, and republish. Claude Code's memory for this project lives outside the repo, on each machine, so this
page and `CLAUDE.md` carry the context.

## Where things stand (2026-09-24)

The repository is the source of truth: every result, the experiment that produced it and the raw data are here,
and `docs/findings/` traces each claim to its file. If a session is lost, resume from this page.

- **Reports (all public on spacesheep.dev; the hub is the observability report):**
  [Limits of observability](https://spacesheep.dev/@yaroslavvb/et-soc1-limits-of-observability) (second edition:
  the meter chain, the unmetered remainder attributed, the improvement ladder, the index of every measurement
  report) · [The energy manual](https://spacesheep.dev/@yaroslavvb/et-soc1-energy-manual) (third edition: every
  entry with a confidence bar from repeated passes on two cards) · [DVFS and leakage](https://spacesheep.dev/@yaroslavvb/et-soc1-dvfs-leakage)
  · [Spatial temperature brief](https://spacesheep.dev/@yaroslavvb/et-soc1-spatial-temperature-brief) · [Horace](https://spacesheep.dev/@yaroslavvb/et-soc1-horace-experiment)
  · [Why low power](https://spacesheep.dev/@yaroslavvb/et-soc1-why-low-power) · [Hot line](https://spacesheep.dev/@yaroslavvb/et-soc1-hot-line)
  · [On-chip relay](https://spacesheep.dev/@yaroslavvb/et-soc1-on-chip-relay) · [Heat per millimetre](https://spacesheep.dev/@yaroslavvb/et-soc1-heat-per-mm)
  (the mesh's wire energy per bit·mm against Dally's ~100 fJ/b-mm) · and the 18–20 September reports below.
  Space uuids are in `docs/findings/04-artifacts.md`; deploy with `npx --yes spacesheep deploy <dir> --space <uuid>`
  from a private directory holding `index.html`, and delete `.spacesheep.json` afterwards (see `04-artifacts.md`).
- **The energy manual** (`docs/energy-manual/*.md`, page `docs/reports/2026-09-23-energy-manual.html`) is built
  by `tools/ettelem/build_energy_manual.py` → `manual.json` → `render_energy_manual.py` (sections 1–8),
  `render_catalogue.py` (3a, 4a) and `scripts/build-report.py energy-manual`. Its data: the catalogue
  (`workloads/enercat/run_catalogue.py`, 386 configurations × 3 shuffled passes on aifoundry2 and aifoundry3,
  `docs/reports/data/2026-09-23-catalogue-*`, reduced by `workloads/enercat/analyze_catalogue.py`), the reruns of
  the relay, hot line, rings and levels (`tools/ettelem/run_reruns_warm.sh`, `run_rings_levels_power.sh`,
  `docs/reports/data/2026-09-23-reruns-*`, pooled by `tools/ettelem/analyze_reruns.py`), and the unmetered-power
  attribution (`docs/reports/data/2026-09-23-energy-manual/unmetered_fit.json`, computed inline; the fit is
  described in `docs/energy-manual/04a-fine-grain.md`).
- **What the bars taught us:** pass-to-pass scatter on one card is 1–2%; the two cards differ by 5% with one
  scale; small signals (the awake core, the hot line, the DRAM relay) carry ±20–30% because a 1–5 W signal rides
  on a 30 W idle that drifts. On aifoundry2 every power burst needs a die above 68 °C or the governor moves the
  clock mid-burst; the cool-card reruns of 23 September were discarded for that reason.
- **The unmetered power** (board minus the three metered rails: 15 W of 32 W idle) fits as 18–20% delivery loss on
  the minion rail, 5% on SRAM, 26–29% on the mesh and 68–73 pJ per DRAM byte off-rail, rms 0.3 W over 390
  bursts; the memory shires' Moortec voltage monitor (`die_mv.ddr`) droops 0.84 mV per off-rail DRAM watt and
  serves as a DRAM-activity meter. What would meter more is the observability report's improvement ladder.
- **Heat per millimetre** (`docs/findings/20-heat-per-mm.md`, page `docs/reports/2026-09-24-heat-per-mm.html`):
  `workloads/enercat/run_wire.py` (two runs, E31 and E32, both cards, `docs/reports/data/2026-09-24-wire*-aifoundry*`)
  → `workloads/enercat/analyze_wire.py` → `wire.json` → `tools/ettelem/build_wire_report.py` → `report.json` →
  `scripts/build-report.py heat-per-mm`. A random bit costs 36 fJ per mm on the mesh rail with free links, 50 on a
  loaded mesh (47 and 73 on board power); ones carried cost energy, not just bit changes. An adversarial review
  checked it before publication (`docs/reports/data/2026-09-24-wire-energy/review/`).
- **New traps (24 September):** a sampler killed mid-request poisons the management queue until one
  `dev_mngt_service` call drains it; loads between shires in the same column three hops apart starve the meter on
  aifoundry2; a memory pattern with no buffer writes to physical address 0 and nothing reports it. All three are in
  `docs/findings/14-card-behaviour.md`, "Traps".
- **Next:** the ladder's first undone rungs — deconvolving the rails' 1 s filter, calibrating the per-shire
  IR-drop map from the SP DEBUG trace into a spatial current map, and a PCIe riser with shunts for millisecond
  board power. The earlier "next" items below (a real GEMM, prefetching, Discord) still stand.

## Where things stood on 2026-09-18

- **Goal.** Roman Shaposhnik (AI Foundry / AINekko) invited us to prototype a workload on the ET-SoC-1, first
  on the `sys_emu` simulator and then on the real cards in their lab. He would like the experience shared on the
  AI Foundry Discord. The long-term workload has not been picked yet.
- **Done:**
  - The local simulator environment: Lima VM, `make run-hello`. See the [README](../README.md).
  - The hello worlds, on the simulator and on a card.
  - `workloads/sgemm` on aifoundry3: scalar fp32, 127 GFLOP/s.
  - The tensor-unit matmul energy benchmark on aifoundry2 (`kernels/mmbench`). Results:
    - fp32: 9.5 TFLOP/s, 168 GFLOP/s per W, 3.4× the A100's fp32 efficiency by spec sheet.
    - fp16: 19.0 TFLOP/s, 321 GFLOP/s per W.
    - int8: 71.8 TOP/s, 1,162 GOP/s per W.
  - The report is [docs/reports/2026-09-18-et-soc1-matmul-efficiency.html](reports/2026-09-18-et-soc1-matmul-efficiency.html),
    published privately at https://spacesheep.dev/@yaroslavvb/et-soc1-matmul-efficiency. Its raw data is in
    `docs/reports/data/2026-09-18-aifoundry2/`.
  - The memory hierarchy on aifoundry2 (`workloads/memhier`): each level's latency, bandwidth and energy per byte.
    Report: [docs/reports/2026-09-18-et-soc1-memory-hierarchy.html](reports/2026-09-18-et-soc1-memory-hierarchy.html).
  - On-chip communication on aifoundry2 (`workloads/nocbench`): the 6x6 shire mesh, TensorSend/Recv, reduction trees,
    credits and barriers. Report: [docs/reports/2026-09-18-et-soc1-on-chip-communication.html](reports/2026-09-18-et-soc1-on-chip-communication.html).
  - Sparsity on aifoundry3 (`workloads/sparsity`): tensor-unit zero-skip saves energy but no cycles, masked TensorLoads
    save time except when the whole chip saturates DRAM, and a batch-1 sparse layer runs in 7.5 us dense and 2.1 us at
    99% zeros. The report also ranks scenarios where the chip could beat an A100. Report:
    [docs/reports/2026-09-18-et-soc1-sparsity.html](reports/2026-09-18-et-soc1-sparsity.html), published privately at
    https://spacesheep.dev/@yaroslavvb/et-soc1-sparse-compute.
  - One memory access taken apart on aifoundry2 (`workloads/memprobe`): L3 = 110 + 12/hop, DRAM adds 91 + 12/hop to the
    memory shire, rows/banks/refresh, and energy per load by rail. Report:
    [docs/reports/2026-09-19-et-soc1-memory-anatomy.html](reports/2026-09-19-et-soc1-memory-anatomy.html).
  - The observability survey: what the card, the simulator and the RTL each let you see, and the firmware-signing caveat on
    making more visible. Report: [docs/reports/2026-09-20-et-soc1-limits-of-observability.html](reports/2026-09-20-et-soc1-limits-of-observability.html).
  - Tooling from the survey (2026-09-20): device flame graphs (`workloads/traceprof`, `scripts/trace-flamegraph.py`); the
    `hpmcounter3` late carry root-caused in the original RTL under Verilator (`rtl-sim/pmu_carry`; Verilator 5.042 is built in
    `~/.local/verilator` on aifoundry2, with `libfl-dev` and `help2man` unpacked under `~/.local/debs`); and a counter-configure
    syscall for the minion firmware, verified in `sys_emu` (`patches/0003`, `scripts/build-minion-fw.sh`, `workloads/pmcsel`).
    No firmware was flashed: the boot chain checks signatures and the open tree has no signing key, so that waits for a
    signed build or word from the lab on how the card is provisioned.
  - Power and temperature (2026-09-20, `tools/ettelem`): the card leaks about 0.8 W per °C under load and idles 5 W higher after a
    load than before it, so baselines must be taken at the same die temperature. Reports:
    [power and temperature](reports/2026-09-20-et-soc1-power-temperature.html) and the
    [Horace experiment](reports/2026-09-20-horace-experiment.html) (fourth version, 2026-09-21: data-dependent matmul power with every
    run launched from the same die temperature, zeros 38 W, ones 47 W, random 63 W; heating per FLOP; a power model from RTL toggle
    counts, `rtl-sim/fma_toggle`; ten-minute runs; a model from flip rates to die temperature, `tools/ettelem/flip_thermal_model.py`;
    structured matrices priced before they ran; `tools/ettelem/predict_heat.py` for custom workloads) and
    [why the chip is low power](reports/2026-09-21-why-low-power.html) (C V² f + leakage measured term by term, against an A100).
  - On this card in this chassis, nothing but zeros can run at full load for long: from 80 °C, random fp32 data reaches 90 °C in
    about 20 s and ones in about two minutes, because leakage (23 W at 80 °C, +0.65 W per °C) feeds back through 1.5 °C per W of
    thermal resistance. Sustained switching power above about 3 W has no equilibrium. Runs longer than a few seconds need a
    temperature cap: `tools/ettelem/run_horace_long.sh` stops a run at 90 °C through the host's `--stop-file`. Never edit a runner
    script while it is running; bash reads it as it goes.
  - The clock governor is thermal first: above 65 °C the card sits at 600 MHz and 0.52 V whatever the power, below it a busy card
    goes to 800 MHz and 0.62 V. A card that has idled overnight (62 °C, 27 W) therefore behaves differently from one in use (72 to
    80 °C, 31 to 36 W). Check `mhz` in `ettelem sample` before comparing anything.
  - Ridge points, derived from the above with no new runs: the FLOPs per byte a kernel needs from each memory level
    to be compute-bound (fp32 on the tensor unit: 4 from its own shire, 10 from L3 or another shire, 130 from DRAM).
    Report: [docs/reports/2026-09-18-et-soc1-ridge-points.html](reports/2026-09-18-et-soc1-ridge-points.html),
    published at https://spacesheep.dev/@yaroslavvb/et-soc1-ridge-points.
  - Summaries of all of these are in [et-soc1-notes.md](et-soc1-notes.md).
- **Next:**
  - A real GEMM, tiling through the L2 scratchpad with cooperative tensor loads. FOSDEM reached 10.25 TFLOP/s this way.
  - Hart 1 prefetching with `TensorLoadL2Scp`.
  - A vector-unit fp32 baseline.
  - Posting the results on Discord.
  - From the sparsity report: run the batch-1 layer on an A100 for a measured comparison, and try the spiking
    microcircuit (PD14), where the chip's 2.3 us hardware allreduce could beat a GPU's per-step kernel launches.

## 1. Clone

```bash
gh repo clone yaroslavvb/et-soc1-prototyping nekko      # private repo
cd nekko
scripts/clone-upstream.sh
```

`clone-upstream.sh` puts et-platform, et-man (the manuals), core-et and et-testdrive in `external/`. Keep
et-platform's full history, because `scripts/deploy-lab-gpsdk.sh` exports an older gp-sdk from it.

For the local simulator, run `scripts/create-vm.sh` on a Mac. On Ubuntu 24.04, run `scripts/provision-vm.sh`.
The [README](../README.md) has the details. The lab machines don't need any of this: they already have the ET stack.

## 2. Connect to the lab machines

The lab machines are on AI Foundry's Tailscale tailnet. We are a member as `yaroslavvb@gmail.com`, through the
invite Roman sent. On the new machine:

1. Install Tailscale, sign in with that account, and check that the machines show up:
   `tailscale status | grep aifoundry`.
2. Logins use Tailscale SSH, so there are no keys or passwords. Our account is `yaroslavvb` on every machine.
   If your local username is different, add this to `~/.ssh/config`:

   ```
   Host aifoundry1 aifoundry2 aifoundry3
       User yaroslavvb
   ```
3. Run `ssh aifoundry2 true`. If Tailscale prints a URL, open it to confirm it's you. Tailscale repeats this
   check every so often.
4. On the machine, put the ET tools on your PATH: `echo 'export PATH=/opt/et/bin:$PATH' >> ~/.bashrc`.

| Machine | Cards | Notes |
|---|---|---|
| `aifoundry1` | 2 (`/dev/et0_*`, `/dev/et1_*`) | |
| `aifoundry2` | 1 | This session's benchmark. Minion clock 600 MHz when the die is above 65 °C (up to 800 MHz below), 32 GB LPDDR4X, idle board power 27 W cold, 31 to 36 W after load. |
| `aifoundry3` | 1 | `workloads/sgemm` |

All three are x86_64 Ubuntu 24.04. Their `/opt/et` is et-platform `353f20e` from Dec 2025: runtime 0.19.0,
RISC-V GCC 15.1 and `sys_emu`. That is older than the gp-sdk that upstream documents; see section 4.
`ssh root@aifoundryN` also works, but use it only for admin, such as `scripts/add-lab-user.sh`.
[docs/lab-access.md](lab-access.md) covers accounts for other people and sudo.

**Etiquette.** The cards are shared, and these are the user's rules, also in `CLAUDE.md`:

- Ask which machine to use.
- Look before touching a card: `uptime`, `who`, `ps`, and `lsmod | grep et_soc1`. Its third column is the number
  of open handles and should be 0.
- Never hold a device for more than 10 s. Use `timeout 10`.
- Keep disk and memory use small, and build with `nice` and `-j4`.

Only one process at a time can open a card's management node (`/dev/et0_mgmt`). While someone runs `et-powertop`,
`dev_mngt_service`, et-testdrive and the power logger all fail with "Device or resource busy".

**Lab norms from the AI Foundry Discord** (#community-lab, read on 2026-09-18):

- People claim a machine by posting "using aifoundry2" there, and "released" when they are done.
- **Don't reset a card yourself.** On 2026-07-17 the lab admin, Afonso Oliveira, asked people not to reset the
  ET-SoC-1 cards, because a software reset can hang one. If a card hangs, ping him and he will power-cycle it. We
  reset aifoundry2 twice on 2026-09-18 with `dev_mngt_service -m DM_CMD_RESET_ETSOC -n 0`, both times with the user's
  approval and before we had seen his request. It worked both times, but ask him first.
- You can tell a card is wedged when every launch fails with `KernelLaunchCmIfaceMulticastFailed`, or with "Couldn't use
  the HPSQ. Perhaps the Master Minion is hanged?".

## 3. Hello world

On a lab machine, with nothing to build:

```bash
/opt/et/bin/it_test_code_loading                           # simulator: 3 tests pass in about 110 s
timeout 10 /opt/et/bin/it_test_code_loading --mode=pcie    # the card: 3 tests pass in under 1 s
```

marty1885's et-testdrive, from the laptop:

```bash
rsync -a --exclude .git --exclude build external/et-testdrive/ aifoundry2:et-testdrive/
ssh aifoundry2 'cd et-testdrive && cmake -B build -DCMAKE_PREFIX_PATH=/opt/et -Wno-dev > /dev/null &&
  nice cmake --build build -j4 > /dev/null && timeout 10 build/host/hello_host build/kernel/hello.elf | tail -3'
```

It should print "Hello World from hart N" from all 64 harts of shire 0. Add `-DET_SYSEMU=ON` to the first
`cmake` for a simulator build.

## 4. The matmul energy benchmark

gp-sdk kernels (`kernels/`, `launchers/`) need gp-sdk pinned to `06605ab` plus
`patches/lab-gp-sdk-06605ab.patch` on the lab machines. `patches/README.md` explains why. Without the patch, every
kernel faults at PC `0x40`. The deploy script sets this up:

```bash
scripts/deploy-lab-gpsdk.sh aifoundry2       # from the laptop: sources, patched gp-sdk, nice -j4 build (~10 s)
ssh aifoundry2
cd ~/nekko
make mmbench-check DEVICE=silicon            # exact-result check of every mode, about 1 s of card time
make bench-power                             # about 1 min; every launcher is capped at 10 s on the card
```

- **The kernel.** Hart 0 of each of the 1,024 minions runs back-to-back `tensor_fma` ops: 16×16×K tiles in fp32,
  fp16→fp32 or int8→int32. A is double-buffered in the L1 scratchpad, and B streams through TenB.
- **Checking.** The host checks every minion's result exactly against its own computation.
- **Power.** `scripts/et-power-log.sh` samples board power from the service processor about 7 times a second.
  `scripts/mmbench-power.py` averages it over each workload's launch windows.
- **Output.** `build/mmbench-power/`: `power.csv`, `runs.jsonl` and `results.json`.

On the simulator, run `scripts/vm make mmbench-check` on the laptop, or `make mmbench-check` on a lab machine. It
uses one shire and takes about 40 s per mode. The simulator's timings are meaningless because `sys_emu` is
functional only, so measure speed on a card.

## 5. Updating the report

```bash
rsync -a aifoundry2:nekko/build/mmbench-power/ docs/reports/data/<date>-aifoundry2/
scripts/mmbench-report-data.py docs/reports/data/<date>-aifoundry2 \
    --embed docs/reports/2026-09-18-et-soc1-matmul-efficiency.html
```

This prints the table numbers, % of peak and A100 ratios, and refreshes the power chart. The prose and tables
in the HTML are hand-written, so edit them to match. To publish, use the spacesheep CLI. Sign in once per machine
with `npx --yes spacesheep login`, which asks you to approve it in the browser.

```bash
npx --yes spacesheep deploy docs/reports/2026-09-18-et-soc1-matmul-efficiency.html \
    --space 590752c1-17a8-4f5d-97ef-bcf33fd6a3e7 -m "<what changed>"
npx --yes spacesheep share 590752c1-17a8-4f5d-97ef-bcf33fd6a3e7 --visibility private
npx --yes spacesheep list | grep et-soc1      # confirm the visibility column says private
```

Always pass `--space`. Without it the CLI creates a new space. The `.spacesheep.json` files it writes are
gitignored, so a fresh clone has nothing that pins the space. The older test-drive write-up in `docs/report/`
is space `16732875-c03e-434d-a643-7a432586c7f7`.

## 6. What is already on the lab machines

- **aifoundry2** (`~yaroslavvb`):
  - `~/nekko`: the deployed copy, built. The 18 Sep runs are in `build/mmbench-power`, `build/memhier` (chases),
    `build/memhier-energy*` and `build/nocbench-data`. The outputs the reports use are committed under `docs/reports/data/`.
  - `~/et-testdrive`: built.
  - `~/et-hello`: scratch from the first session, superseded by `~/nekko`. Safe to delete.
- **aifoundry3:** the `workloads/sgemm` build. See [workloads/sgemm/README.md](../workloads/sgemm/README.md).
- **aifoundry1:** the account only.

Home directories are local to each machine.

## 7. Gotchas from the first session

- **gp-sdk versus the lab install.** Three problems, all fixed by `patches/lab-gp-sdk-06605ab.patch`:
  - The Erbium components are missing.
  - The simulator runs without firmware and writes GBs of log.
  - Kernels fault at PC `0x40` without `--emit-relocs`.
- **`pkill -f <pattern>` over `ssh` kills your own session,** because the remote command line contains the
  pattern. Kill by PID instead.
- **The Mac has no `timeout` by default.** Run capped commands on the lab machine.
- **Board power creeps up as the chip warms,** by about 3 W over 12 s. Compare runs of the same length.
- **A hung transfer outlives the kernel abort.** If a TensorSend, TensorRecv or blocking credit wait (`csrw fcc`)
  never completes, the stalled hart ignores the firmware's abort. The card then refuses launches until it is
  power-cycled. Every wait must have a partner that answers it. When credits cross shires, poll `fccnb` with a
  bailout first, as `workloads/nocbench` does.
- **TensorSend has one "ready" bit per minion.** A minion must never have two partners that could both be ready at
  once. Change partners only across a barrier. `sys_emu` tracks each partner separately, so a schedule that passes
  on the simulator can still hang silicon. See `docs/et-soc1-notes.md`, "On-chip communication".

## 8. Reproducing each report

Each report is one HTML file in `docs/reports/`, with its raw measurements in `docs/reports/data/`. The charts read
JSON that an analysis script embeds in the page. The prose and tables are written by hand from the script's
printout. On 2026-09-18, each script regenerated its committed page byte for byte from the committed data. The
GPU and A100 columns come from the sourced notes in `docs/reports/sources/`, not from our measurements.

| Report | Code | Measure (on a lab machine) | Raw data | Regenerate the page |
|---|---|---|---|---|
| Matmul efficiency | `kernels/mmbench`, `launchers/mmbench` | section 4 | `docs/reports/data/2026-09-18-aifoundry2` | `scripts/mmbench-report-data.py DATA --embed HTML` |
| Memory hierarchy | `workloads/memhier` | `workloads/memhier/README.md`: the chases, then `run_energy.py` | `docs/reports/data/2026-09-18-memhier-aifoundry2` | `python3 workloads/memhier/analyze.py DATA --embed HTML` |
| On-chip communication | `workloads/nocbench` | `run_lab.sh`, then `run_energy.py` twice, the second time with `--only` in reverse order | `docs/reports/data/2026-09-18-nocbench-aifoundry2` | `python3 workloads/nocbench/analyze.py DATA --memhier docs/reports/data/2026-09-18-memhier-aifoundry2 --search --embed HTML` |
| Energy manual, catalogue | `workloads/enercat` | `run_catalogue.py DATA --passes 3` on each card (1.5 h each; keep the die warm on aifoundry2) | `docs/reports/data/2026-09-23-catalogue-aifoundry2`, `-aifoundry3`, `-aifoundry2-rows` | `analyze_catalogue.py A2 A3 --out catalogue.json`, then `tools/ettelem/build_energy_manual.py`, `render_energy_manual.py`, `render_catalogue.py`, `scripts/build-report.py energy-manual manual.json HTML` |
| Energy manual, reruns | `tools/ettelem/run_reruns_warm.sh`, `run_rings_levels_power.sh` | 3 passes each of relay, hot line, rings, levels per card; preheat aifoundry2 | `docs/reports/data/2026-09-23-reruns-aifoundry2-warm`, `-aifoundry3` | `tools/ettelem/analyze_reruns.py DIRS --out reruns.json` (bursts off 600 MHz dropped) |
| Limits of observability | `docs/reports/sources/limits-of-observability.*` | reads the firmware and the catalogue; no card time | `docs/reports/data/2026-09-23-energy-manual/unmetered_fit.json` | `scripts/build-report.py limits-of-observability docs/reports/sources/limits-of-observability.data.json HTML` |
| Sparsity | `workloads/sparsity` | `run_lab.sh`, then `run_energy.py` twice, the second time with `--only` in reverse order (`workloads/sparsity/README.md`) | `docs/reports/data/2026-09-18-sparsity-aifoundry3` | `python3 workloads/sparsity/analyze.py DATA --embed HTML` |
| Ridge points | `scripts/ridge-points.py` | nothing: derived from the four 2026-09-18 reports | their four data directories | `python3 scripts/ridge-points.py --embed HTML` |

- **Measuring.** Build on the machine with `scripts/deploy-lab.sh aifoundry2 workloads/<name>`, or
  `scripts/deploy-lab-gpsdk.sh` for `kernels/`. Follow the etiquette above, then copy the outputs back into a new
  dated directory under `docs/reports/data/`. The runs print JSON lines that the analysis scripts read.
  Workloads also run on the simulator with `--sysemu` (small sizes), which checks correctness but not speed.
- **Analysis.** You need Python 3. The on-chip communication analysis also needs numpy. It prints every number
  the page quotes, including the one-hop ring and the mesh-time decomposition.
- **Publishing.** The spaces are private. Update one in place with its uuid, which is in the README. You can use the
  CLI (section 5) or the spacesheep MCP: `stage_begin`, then `curl -X PUT` the file, then `deploy` with the uuid.
  Afterwards check that the visibility is still private.
- **What will differ.** Another card can have a different shire map if a different shire is fused off. It can
  also run at another clock: the governor moves between 600 and 850 MHz, and time on the mesh is fixed in ns. And
  it can idle at a different power, depending on its temperature and on other users. All of our runs are timestamped,
  and those at 600 MHz say so in the data.

## 9. Upstream versions

| Component | Version used | Pinned in |
|---|---|---|
| et-platform: firmware, runtime, `sys_emu`, gp-sdk | `836a4ab` plus `patches/et-platform-*.patch` | `scripts/clone-upstream.sh`; built by `scripts/provision-vm.sh` |
| RISC-V GCC 15.2 (aifoundry-org/riscv-gnu-toolchain, branch `et`) | `b4f9cd5` | `scripts/provision-vm.sh` (`TOOLCHAIN_REF`) |
| et-man: PRM, datasheet, errata | `5fe80a3` | `scripts/clone-upstream.sh` |
| core-et, branch erbium: RTL and design docs | `b38a1a3` | `scripts/clone-upstream.sh` |
| et-testdrive | `c2035c5` | `scripts/clone-upstream.sh` |
| etTopoScan | `ee3e9f2` | `scripts/clone-upstream.sh` |
| gp-sdk on the lab machines | `06605ab` plus `patches/lab-gp-sdk-06605ab.patch` | `scripts/deploy-lab-gpsdk.sh` |
| `/opt/et` on aifoundry1-3 | et-platform `353f20e` (Dec 2025): runtime 0.19.0, GCC 15.1 | installed by the lab |

`UPSTREAM_LATEST=1 scripts/clone-upstream.sh` and `TOOLCHAIN_REF=et scripts/provision-vm.sh` build the branch tips
instead of the pins.
