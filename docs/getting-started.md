# Getting started on a new machine

> For the **results** rather than the machinery, read [findings/](findings/README.md): the findings from
> 18–24 September 2026, with a claim index that traces every number back to the experiment and the raw file
> it came from.

This page covers everything needed to pick the work up somewhere else: clone, connect to the lab, rebuild,
rerun, and republish. Claude Code's memory for this project lives outside the repo, on each machine, so this
page, [`AGENT.md`](../AGENT.md) (the entry point for an agent) and `CLAUDE.md` carry the context.

## Where things stand (2026-09-25)

The repository is the source of truth: every result, the experiment that produced it and the raw data are here,
and `docs/findings/` traces each claim to its file. If a session is lost, resume from this page.

- **The lab, 25 September (evening).** Four cards work, on three firmware releases: aifoundry2 and aifoundry3 (1.3.1)
  and, since 15:02 that day, aifoundry1's two cards (card 0 on 1.4.1, card 1 on 1.2.0). aifoundry1's cards had been
  refused because its driver module had an empty version string; the fix and the report are in
  `docs/reports/data/2026-09-25-aifoundry1/`. **aifoundry1's card 0 overheats: do not run sustained work on it.**
  aifoundry3's 0 W TDP is set at every boot by a service, not flashed. Between 16:14 and 16:27 the three hosts were
  brought to one configuration (performance power profile, chrony, core dumps, `et-who`, card locks, a login banner,
  `et-lab-manifest`); a full upgrade is installed and the reboot into kernel 7.0.0-34 is still pending. What that does
  to comparability, and every card's quirks: `docs/findings/14-card-behaviour.md`. The machines' shared tools:
  `docs/lab-access.md`.
- **Running now: version 3 of the claims check.** Pre-registered in `docs/reports/data/2026-09-25-claims-v3/`
  (`PLAN3.md`, and `AMENDMENTS.md` A1–A5, each written before the data it touches), with its code in `tools/claims-v3/`.
  Its queues run unattended on aifoundry1's card 1, aifoundry2 and aifoundry3 (`queue.sh` with
  `schedule-<card>.txt`), and their blocks hold the cards and the card locks. **Do not start card work on those
  machines without asking**, and while a queue runs do not rebuild the binaries it uses or run
  `scripts/deploy-lab*.sh` against its host (both write into `~/nekko`, which the blocks use; [`AGENT.md`](../AGENT.md)
  §7); a queue stops at the next block boundary when `build/claims-v3/STOP` exists in its tree (the owner's call).
  Next on the cards, after the campaign: gathers and scatters (E48, `tools/claims-v3/gs/`). The pages are revised
  with the campaign's results in a later pass; until then their sources stay as they are.
- **New pages, 25 September:** [Influence functions on the ET-SoC-1](https://spacesheep.dev/@yaroslavvb/et-soc1-influence-functions)
  (exploratory, no card run; `docs/reports/data/2026-09-25-influence-on-et/`),
  [What is broken on aifoundry1](https://spacesheep.dev/@yaroslavvb/aifoundry1-troubleshooting) and its
  [fix log](https://spacesheep.dev/@yaroslavvb/aifoundry1-fix), and a report on the lab's problems for the lab lead,
  which is private and not in the repository.
- **The repository pass of 25 September:** [`AGENT.md`](../AGENT.md) (the map and the rules for an agent starting
  from a clone), [`reports/MIRROR.md`](reports/MIRROR.md) (every published page with its space, file and
  visibility) and `scripts/check-mirror.py` (live equals repo). Lessons that had lived only in per-machine memory
  moved into `findings/14-card-behaviour.md`, `lab-access.md`, this page and `findings/04-artifacts.md`.
- **Reports (all public on spacesheep.dev; the hub is the observability report):**
  [Limits of observability](https://spacesheep.dev/@yaroslavvb/et-soc1-limits-of-observability) (second edition:
  the meter chain, the unmetered remainder attributed, the improvement ladder, the index of every measurement
  report) · [The energy manual](https://spacesheep.dev/@yaroslavvb/et-soc1-energy-manual) (third edition: every
  entry with a confidence bar from repeated passes on two cards) · [DVFS and leakage](https://spacesheep.dev/@yaroslavvb/et-soc1-dvfs-leakage)
  · [Spatial temperature brief](https://spacesheep.dev/@yaroslavvb/et-soc1-spatial-temperature-brief) · [Horace](https://spacesheep.dev/@yaroslavvb/et-soc1-horace-experiment)
  · [Why low power](https://spacesheep.dev/@yaroslavvb/et-soc1-why-low-power) · [Hot line](https://spacesheep.dev/@yaroslavvb/et-soc1-hot-line)
  · [On-chip relay](https://spacesheep.dev/@yaroslavvb/et-soc1-on-chip-relay) · [Heat per millimetre](https://spacesheep.dev/@yaroslavvb/et-soc1-heat-per-mm)
  (the mesh's wire energy per bit·mm against Dally's ~100 fJ/b-mm) · and the 18–20 September reports below.
  Every space the hub links is public (Q40). Every page, its space uuid, its repo file and its visibility are in
  [`reports/MIRROR.md`](reports/MIRROR.md), and `python3 scripts/check-mirror.py` checks that each live page equals
  its file. Deploy with `spacesheep deploy <dir> --space <uuid>` from a directory of its own holding `index.html`
  (the Horace experiment always as its folder with the GIFs), and delete `.spacesheep.json` afterwards (MIRROR.md,
  "Deploying one page"; the history is in `docs/findings/04-artifacts.md`).
- **The energy manual** (`docs/energy-manual/*.md`, page `docs/reports/2026-09-23-energy-manual.html`) is built
  by `tools/ettelem/build_energy_manual.py` → `manual.json` → `render_energy_manual.py` (sections 1–8),
  `render_catalogue.py` (3a, 4a) and `scripts/build-report.py energy-manual`. Its data: the catalogue
  (`workloads/enercat/run_catalogue.py`, 386 configurations × 3 shuffled passes on aifoundry2 and aifoundry3,
  `docs/reports/data/2026-09-23-catalogue-*`, reduced by `workloads/enercat/analyze_catalogue.py`), the reruns of
  the relay, hot line, rings and levels (`tools/ettelem/run_reruns_warm.sh`, `run_rings_levels_power.sh`,
  `docs/reports/data/2026-09-23-reruns-*`, pooled by `tools/ettelem/analyze_reruns.py`), and the unmetered-power
  attribution (`docs/reports/data/2026-09-23-energy-manual/unmetered_fit.json`, written by
  `tools/ettelem/fit_unmetered.py --overwrite`; until 25 September the droop block was the first, inline fit's,
  0.84 mV/W, and it is now the script's 0.87; the fit is described in `docs/energy-manual/04a-fine-grain.md` and in
  E30 of `docs/findings/03-experiments.md`). `docs/findings/04-artifacts.md` (A16) gives the whole rebuild in order.
- **What the bars taught us:** pass-to-pass scatter on one card is 1–2%; the two cards differ by 5% with one
  scale; small signals carry the widest bars because a 1–5 W signal rides on a 30 W idle that drifts: ±17% on
  the hot line, ±4–16% on the levels and rings, ±5.5% on the DRAM relay. On aifoundry2 every power burst needs a
  die above 68 °C or the governor moves the clock mid-burst (the firmware threshold is 65 °C, but on ettelem's
  mean die reading the clock still stepped up at readings up to 67 °C in E10); the cool-card reruns of
  23 September, at 64–66 °C, were discarded for that reason.
- **The unmetered power** (board minus the three metered rails: 15 W of 32 W idle) fits as 18–20% delivery loss on
  the minion rail, 5% on SRAM, 26–29% on the mesh and 68–73 pJ per DRAM byte off-rail, rms 0.30–0.35 W over
  about 390 configuration means (1.1–1.3 W on the DRAM ones); the idle 15 W is not split. The memory shires' Moortec voltage monitor (`die_mv.ddr`) droops 0.87 mV per off-rail DRAM watt and
  serves as a DRAM-activity meter (traffic with no DRAM access moves it too, by up to about 2 mV). What would meter more is the observability report's improvement ladder.
- **Heat per millimetre** (`docs/findings/20-heat-per-mm.md`, page `docs/reports/2026-09-24-heat-per-mm.html`):
  `workloads/enercat/run_wire.py` (two runs, E31 and E32, both cards, `docs/reports/data/2026-09-24-wire*-aifoundry*`)
  → `workloads/enercat/analyze_wire.py` → `wire.json` → `tools/ettelem/build_wire_report.py` → `report.json` →
  `scripts/build-report.py heat-per-mm`. A random bit costs 36 fJ per mm on the mesh rail with free links, 50 on a
  loaded mesh (47 and 73 on board power); ones carried cost energy, not just bit changes. An adversarial review
  by a workflow of six AI agents checked it before publication (`docs/reports/data/2026-09-24-wire-energy/review/`).
- **New traps (24 September):** a sampler killed mid-request poisons the management queue until one
  `dev_mngt_service` call drains it; loads between shires in the same column three hops apart starve the meter on
  aifoundry2; a memory pattern with no buffer writes to physical address 0 and nothing reports it. All three are in
  `docs/findings/14-card-behaviour.md`, "Traps".
- **The review of 24 September:** every page of the published set was checked for consistency, cross-links,
  suspicious claims and readability by a workflow of AI agents (the record is in `docs/findings/04-artifacts.md`,
  "The 24 September review"). The notes of the conversation with David Kanter are now private and
  unlinked; the two briefs of 22 September are imported into `docs/reports/`; deploy the Horace experiment only as
  its folder with the GIFs.
- **The validation of 25 September:** every card-free analysis was rerun (nearly all reproduce byte for byte), every
  number with no producer script got one, the claims were rechecked against the data, repeated explanations were cut
  to one canonical page each, and the pages gained interactive charts built on a shared chart toolkit
  (`docs/reports/sources/chartkit.js`). The L2 mainline-starvation brief is now a pointer page. The raw SP trace dumps
  and load log of 20 September were recovered and committed. The page checker had missed errors thrown while a page
  loads; it is fixed. The record is `docs/findings/04-artifacts.md`, "The 25 September validation", and
  `docs/reports/data/2026-09-24-report-review/`.
- **Next:** the ladder's first undone rungs — deconvolving the rails' filter (τ ≈ 1.15–1.22 s, measured), calibrating the per-shire
  IR-drop map from the SP DEBUG trace into a spatial current map, and a PCIe riser with shunts for millisecond
  board power. The earlier "next" items below (a real GEMM, prefetching, Discord) still stand.

## Earlier work (18–21 September), and where it stood

- **Goal.** Roman Shaposhnik (AI Foundry / AINekko) invited us to prototype a workload on the ET-SoC-1, first
  on the `sys_emu` simulator and then on the real cards in their lab. He would like the experience shared on the
  AI Foundry Discord. The long-term workload has not been picked yet.
- **Done:**
  - The local simulator environment: Lima VM, `make run-hello`. See the [README](../README.md).
  - The hello worlds, on the simulator and on a card.
  - `workloads/sgemm` on aifoundry3: scalar fp32, 127 GFLOP/s.
  - The tensor-unit matmul energy benchmark on aifoundry2 (`kernels/mmbench`). Results:
    - fp32: 9.5 TFLOP/s, 168 GFLOP/s per W, 3.4× the A100's fp32 CUDA-core efficiency by spec sheet on the
      benchmark's ±1/±2 operands (about 2.9× on random data at 80 °C; not its tensor cores, see
      [findings/13-why-low-power.md](findings/13-why-low-power.md)).
    - fp16: 19.0 TFLOP/s, 321 GFLOP/s per W.
    - int8: 71.8 TOP/s, 1,162 GOP/s per W.
  - The report is [docs/reports/2026-09-18-et-soc1-matmul-efficiency.html](reports/2026-09-18-et-soc1-matmul-efficiency.html),
    published at https://spacesheep.dev/@yaroslavvb/et-soc1-matmul-efficiency. Its raw data is in
    `docs/reports/data/2026-09-18-aifoundry2/`.
  - The memory hierarchy on aifoundry2 (`workloads/memhier`): each level's latency, bandwidth and energy per byte.
    Report: [docs/reports/2026-09-18-et-soc1-memory-hierarchy.html](reports/2026-09-18-et-soc1-memory-hierarchy.html).
  - On-chip communication on aifoundry2 (`workloads/nocbench`): the 6x6 shire mesh, TensorSend/Recv, reduction trees,
    credits and barriers. Report: [docs/reports/2026-09-18-et-soc1-on-chip-communication.html](reports/2026-09-18-et-soc1-on-chip-communication.html).
  - Sparsity on aifoundry3 (`workloads/sparsity`): tensor-unit zero-skip saves energy but no cycles, masked TensorLoads
    save time except when the whole chip saturates DRAM, and a batch-1 sparse layer runs in 7.5 us dense and 2.1 us at
    99% zeros. The report also ranks scenarios where the chip could beat an A100. Report:
    [docs/reports/2026-09-18-et-soc1-sparsity.html](reports/2026-09-18-et-soc1-sparsity.html), published at
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
  - Power and temperature (2026-09-20, `tools/ettelem`): board power under load rose about 0.8 W per °C in the load
    step (E5; the first, uncontrolled Horace session fitted 0.78, E7; an idle card's leakage slope is 0.65 W/°C at
    80 °C, E17), and the card idles 5 W higher
    after a load than before it, so baselines must be taken at the same die temperature. Reports:
    [power and temperature](reports/2026-09-20-et-soc1-power-temperature.html) and the
    [Horace experiment](reports/2026-09-20-horace-experiment.html) (20–22 September: data-dependent matmul power with every
    run launched from the same die temperature, zeros 38 W, ones 47 W, random 63 W; heating per FLOP; a power model from RTL toggle
    counts, `rtl-sim/fma_toggle`; ten-minute runs; a model from flip rates to die temperature, `tools/ettelem/flip_thermal_model.py`;
    structured matrices priced before they ran; `tools/ettelem/predict_heat.py` for custom workloads; and the same experiment
    on aifoundry3) and
    [why the chip is low power](reports/2026-09-21-why-low-power.html) (C V² f + leakage measured term by term, against an A100).
  - On this card in this chassis, nothing but zeros can run at full load for long: from 80 °C, random fp32 data reaches 90 °C in
    about 20 s and ones in about two minutes, because leakage (23 W at 80 °C, +0.65 W per °C) feeds back through 1.5 °C per W of
    thermal resistance. Sustained switching power above about 3 W has no equilibrium. Runs longer than a few seconds need a
    temperature cap: `tools/ettelem/run_horace_long.sh` stops a run at 90 °C through the host's `--stop-file`. Never edit a runner
    script while it is running; bash reads it as it goes.
  - The clock governor is thermal first: above 65 °C the card sits at 600 MHz and 0.52 V whatever the power, below it a busy card
    steps up through 700 MHz (0.57 V) to 800 MHz (0.62 V). A card that has idled overnight (62 °C, 27 W) therefore behaves differently from one in use (72 to
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
gh repo clone yaroslavvb/et-soc1-prototyping nekko      # public repo
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
3. Run `ssh aifoundry2 true`. Tailscale SSH is in check mode: it prints a `login.tailscale.com` URL that a person
   must approve in a browser signed in to the tailnet, while the `ssh` waits. One approval lasts about 12 hours.
   An agent cannot approve it: it hands the URL to a person. If the URL answers 404, sign out of
   login.tailscale.com and back in, then `ssh` again ([lab-access.md](lab-access.md), "How access works").
4. From aifoundry2 to the other two, give each machine's full tailnet name as its `HostName` in `~/.ssh/config`:
   aifoundry2 resolves the short names over the LAN first ([lab-access.md](lab-access.md)).

`/opt/et/bin` is on PATH in login shells on every machine since 25 September; nothing to add to `.bashrc`.

| Machine | Cards | Notes |
|---|---|---|
| `aifoundry1` | 2 (`/dev/et0_*`, `/dev/et1_*`) | Working since 2026-09-25 15:02 (the driver's empty version string was fixed). Card 0 (firmware 1.4.1) **overheats: do not run sustained work on it**; it idles at 300 MHz. Card 1 (firmware 1.2.0) is fine and idles at 600 MHz, 33–35 W. Select a card with `ET_DEVICES=<n>` (this host only; `V3_DEVICE=<n>` in `tools/claims-v3`). Its `/opt/et` is a fork build; the disk is nearly full. |
| `aifoundry2` | 1 | The main card for this work, and the git checkout (`~/claude/et-soc1-prototyping`). Firmware 1.3.1. Minion clock 600 MHz when the die is above 65 °C (up to 800 MHz below), 32 GB LPDDR4X, idle board power 27 W cold, 31 to 36 W after load. |
| `aifoundry3` | 1 | Firmware 1.3.1, held at 600 MHz by a 0 W TDP that a boot service sets at every boot (not flashed). The die idles at 55–57 °C since the host changes of 25 Sep (51–54 °C before). Compare switching power over idle, not absolute watts. Its `libetrt.so` is a patched `-O3` build, and about one host launch in 100 crashes at 1.08 s: repeat it. |

See [findings/14-card-behaviour.md](findings/14-card-behaviour.md) for how the four cards and three hosts differ.

All three are x86_64 Ubuntu 24.04 with RISC-V GCC 15.1 and `sys_emu` in `/opt/et`, but not the same runtime:
aifoundry2 has et-platform `353f20e` (Dec 2025, runtime 0.19.0), aifoundry3 the same with a patched `libetrt.so`, and
aifoundry1 a fork build whose device layer takes `ET_DEVICES` (§9). All are older than the gp-sdk that upstream
documents; see section 4. Admin work on the machines (accounts, drivers, resets) is for the lab admin;
[docs/lab-access.md](lab-access.md) covers accounts for other people.

**Etiquette.** The cards are shared, and these are the user's rules, also in `CLAUDE.md`:

- Ask which machine to use (on aifoundry1, which card), and stay off machines other sessions are using.
- Look before touching a card: `et-who` lists every user's holders of the device nodes and the card locks (or
  `fuser -v /dev/et*`); also `who` and `uptime`. The old check, the use count in `lsmod | grep et_soc1`, cannot tell
  which of aifoundry1's two cards is held. Hold the card's lock for your run:
  `flock -n /run/lock/etsoc-shire<N>.lock <command>`.
- Never hold a device for more than 10 s. Use `timeout 10`.
- Stop tools and samplers with Ctrl-C or a plain `kill`, never `kill -9`: it poisons the card's management queue
  for the next user ([findings/14-card-behaviour.md](findings/14-card-behaviour.md), "Traps").
- Keep disk and memory use small, and build with `nice` and `-j4`.
- Others use the cards too: CI runners on aifoundry1 and aifoundry2 and a demo service on aifoundry3 can take a card
  at any time, and the version-3 campaign's queues hold the cards for hours ("Where things stand").

Why: the management node is single-opener, so one careless sampler blocks everyone; heat carries over from one run
to the next, so someone else's run changes your die temperature and your power readings; and a hung card needs a
power cycle that only the lab admin can do.

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
- **Power.** `scripts/et-power-log.sh` samples board power from the service processor about 8 times a second (a new
  reading about every 133 ms on aifoundry2; aifoundry3's changes only about every 250 ms).
  `scripts/mmbench-power.py` averages it over each workload's launch windows.
- **Output.** `build/mmbench-power/`: `power.csv`, `runs.jsonl` and `results.json`.

On the simulator, run `scripts/vm make mmbench-check` on the laptop, or `make mmbench-check` on a lab machine. It
uses one shire and takes about 40 s per mode. The simulator's timings are meaningless because `sys_emu` is
functional only, so measure speed on a card.

## 5. Updating the report

```bash
rsync -a aifoundry2:nekko/build/mmbench-power/ docs/reports/data/<date>-aifoundry2/
scripts/mmbench-report-data.py docs/reports/data/<date>-aifoundry2 \
    --manual docs/reports/data/2026-09-23-energy-manual/manual.json \
    --embed docs/reports/2026-09-18-et-soc1-matmul-efficiency.html --ladder docs/report/index.html
scripts/paste-chartkit.py docs/reports/2026-09-18-et-soc1-matmul-efficiency.html docs/report/index.html
```

This prints the table numbers, % of peak and A100 ratios, and refreshes the power chart. The prose and tables
in the HTML are hand-written, so edit them to match. To publish, use the spacesheep CLI. Sign in once per machine
with `spacesheep login`, which asks a person to approve it in the browser. **Check the CLI's version**
(`spacesheep --version`): the pages up to 25 September were deployed with spacesheep CLI 1.5.1, a GitHub build,
while npm's latest was 1.2.1. On the evening of 25 September npm's latest became 1.9.1 (`npm install -g spacesheep`),
and aifoundry2's CLI (Node 24 in `~/.local/node`) was updated to it; `scripts/check-mirror.py` reads the pages back
the same with 1.5.1 and 1.9.1. Avoid an older one, such as a stale `npx` cache. The key lives in
`~/.config/spacesheep/`: never copy it into the repository.

```bash
D=$(mktemp -d); cp docs/reports/2026-09-18-et-soc1-matmul-efficiency.html "$D/index.html"
spacesheep deploy "$D" --space 590752c1-17a8-4f5d-97ef-bcf33fd6a3e7 -m "<what changed>"; rm -rf "$D"
spacesheep list | grep et-soc1                 # the visibility column must still say public (Q40)
python3 scripts/check-mirror.py --only et-soc1-matmul-efficiency   # live equals repo
```

Always pass `--space`. Without it the CLI creates a new space. Deploy from a directory of its own: the CLI writes a
`.spacesheep.json` pin file into the deployed directory (gitignored), and a stale one once published a page over
another. The older test-drive write-up in `docs/report/` is space `16732875-c03e-434d-a643-7a432586c7f7`. Every
page's space, file and deploy form: [`reports/MIRROR.md`](reports/MIRROR.md).

## 6. What is already on the lab machines

- **aifoundry2** (`~yaroslavvb`):
  - `~/claude/et-soc1-prototyping`: **the git checkout** the work is done in. The version-3
    campaign runs from here, with its raw data in `build/claims-v3/aifoundry2/`.
  - `~/nekko`: the gp-sdk deploy tree (`scripts/deploy-lab-gpsdk.sh`; `MMBENCH_DIR` in `tools/claims-v3/lib.sh`),
    built. The 18 Sep runs are in `build/mmbench-power`, `build/memhier` (chases), `build/memhier-energy*` and
    `build/nocbench-data`. The outputs the reports use are committed under `docs/reports/data/`.
  - `~/et-testdrive`: built.
  - `~/et-hello`: scratch from the first session, superseded by `~/nekko`. Safe to delete.
- **aifoundry3:** `~/nekko` (deployed for E20 onward; the campaign runs from it) and the `workloads/sgemm` build.
  See [workloads/sgemm/README.md](../workloads/sgemm/README.md).
- **aifoundry1:** `~/nekko` since 25 September (the campaign on card 1 runs from it; `ettelem` is built there
  against the host's own `/opt/et`, so it honours `ET_DEVICES`).

The `~/nekko` trees on aifoundry1 and aifoundry3 are **rsynced copies without git**: edit in the checkout on
aifoundry2 (or a clone), then rsync the changed files. Their `.venv` or `pylib/` numpy fallbacks are no longer needed
(the system numpy is installed everywhere since 25 September). Home directories are local to each machine.

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

**Gotchas from the long runs (22–25 September):**

- **Start long runs detached:** `ssh host 'cd <tree> && setsid nohup <cmd> > <log> 2>&1 < /dev/null &'`. A plain
  `nohup` keeps the `ssh` session open, and the agent harness's command timeout then kills it. The hosts are on
  Wi-Fi, so a dropped connection must not take a run with it.
- **Polling with `pgrep -f <script>` over `ssh` matches itself,** because the `ssh` command line that runs `pgrep`
  names the script too. Match on something only the target has, or check the log.
- **Copying scripts:** an `scp` over a running script corrupts it (bash reads by offset), and an `scp` to a new
  path drops the executable bit. Copy to a temporary name and `mv` it into place, then `chmod +x`.
- **rsync keeps the source's modification times,** so `make` or `cmake --build` on the lab host may not rebuild
  after a sync. Use `cmake --build <dir> --clean-first`.
- **A code-only agent must not reach a card.** On 25 September an agent told to write code only ran a real block:
  a `cd` inside a backgrounded `&&` chain did not apply. Test block scripts with `V3_DRY=1` (no device access at all),
  from an absolute path, and check `et-who` afterwards.
- **The three hosts' compilers generate the same code,** but the ELF files differ in their `.comment` section, so
  compare `.text` hashes, not file md5s ([findings/14-card-behaviour.md](findings/14-card-behaviour.md), "Traps").

## 8. Reproducing each report

Each report is one HTML file in `docs/reports/`, with its raw measurements in `docs/reports/data/`. Reports from
18–19 September are hand-written HTML whose charts read JSON an analysis script embeds; on 2026-09-18 each script
regenerated its committed page byte for byte from the committed data. Later reports are assembled by
`scripts/build-report.py` from `docs/reports/sources/` (see `docs/findings/04-artifacts.md`), and several compute
every number from their data. The GPU and A100 columns come from the sourced notes in `docs/reports/sources/`, not
from our measurements.

**Build prerequisites.** Python 3 with numpy, and node: `scripts/build-report.py` renders TeX to SVG with
mathjax-full, which `package.json` pins to 3.2.1; run `npm ci` once at the repo root (in a git worktree without its own
`node_modules`, set `NODE_PATH` to a checkout's). **Charts.** Every page's charts use the shared toolkit
`docs/reports/sources/chartkit.js` (the global `CK`). `build-report.py` inlines it into the source-built pages at
`__CHARTKIT__`, with its CSS in `report.template.html` between `chartkit:css:begin` and `chartkit:css:end`. The
standalone pages (the 18–19 September reports, the test drive, the spatial brief) carry a copy between
`<!-- chartkit:begin -->` and `<!-- chartkit:end -->`: after editing `chartkit.js` or that CSS, or after an
`--embed` run, refresh them with `scripts/paste-chartkit.py PAGE` (`--check` reports a stale copy); the memory-anatomy
page gets it from its template. Edit a standalone page's prose in the HTML, outside those markers.

| Report | Code | Measure (on a lab machine) | Raw data | Regenerate the page |
|---|---|---|---|---|
| Matmul efficiency, and the test drive's ladder | `kernels/mmbench`, `launchers/mmbench` | section 4 | `docs/reports/data/2026-09-18-aifoundry2` | `python3 scripts/mmbench-report-data.py DATA --manual docs/reports/data/2026-09-23-energy-manual/manual.json --embed HTML --ladder docs/report/index.html` |
| Memory hierarchy | `workloads/memhier` | `workloads/memhier/README.md`: the chases, then `run_energy.py` | `docs/reports/data/2026-09-18-memhier-aifoundry2` | `python3 workloads/memhier/analyze.py DATA --embed HTML` |
| On-chip communication | `workloads/nocbench` | `run_lab.sh`, then `run_energy.py` twice, the second time with `--only` in reverse order | `docs/reports/data/2026-09-18-nocbench-aifoundry2` | `python3 workloads/nocbench/analyze.py DATA --memhier docs/reports/data/2026-09-18-memhier-aifoundry2 --search --embed HTML` |
| Memory anatomy | `workloads/memprobe` | `gen_ops.py` programs, `run_power.py` (`workloads/memprobe/README.md`) | `docs/reports/data/2026-09-19-memprobe-aifoundry2` | `python3 workloads/memprobe/analyze_power.py DATA/power --json DATA/power/summary.json`, `python3 workloads/memprobe/analyze.py --data DATA --out DATA/summary.json`, then `python3 workloads/memprobe/build_report.py DATA/summary.json docs/reports/data/2026-09-23-energy-manual/manual.json HTML` (E1) |
| Power and temperature, spatial brief | `tools/ettelem/run_thermal.sh`, `run_horace.sh` | E5–E8 in `docs/findings/03-experiments.md` | `docs/reports/data/2026-09-20-power-aifoundry2` (with `raw/`: the SP trace dumps and the load log) | `python3 tools/ettelem/summarize_power_session.py DATA --out DATA/summary.json`, then `scripts/build-report.py power-temperature DATA/summary.json HTML`; the brief's constants from `python3 tools/ettelem/host_temp_fields.py` (`--check PAGE`) |
| Horace experiment, why low power | `tools/ettelem` (`run_horace_*.sh`, `run_ablation.sh`) | the commands of E9–E17 and E20 in `docs/findings/03-experiments.md` | `docs/reports/data/2026-09-21-horace-aifoundry2`, `2026-09-22-horace-aifoundry3` | `tools/ettelem/finish_horace.sh` |
| DVFS and leakage | `tools/ettelem/analyze_dvfs.py` | E10, E18, E19 in `docs/findings/03-experiments.md` | `docs/reports/data/2026-09-22-dvfs-aifoundry2` (the wake-up probe, the 20-hour idle), `2026-09-21-horace-aifoundry2` (`cold1`, `cold2`, `long2`, `model.json`, `ablation.json`), `2026-09-22-horace-aifoundry3` (`cards.json`, `transfer.json`, `leakage_crosscard.json`), `2026-09-22-cards` | three steps, in order (E19 gives them in full): `analyze_dvfs.py … --out dvfs.json`; `build_cards_data.py … --merge dvfs.json`, which adds the three-machine block that sections 3 and 6 need (`analyze_dvfs.py` keeps it on a later rerun, and `build-report.py` refuses to build without it); `scripts/build-report.py dvfs-leakage dvfs.json HTML` |
| Hot line, on-chip relay, heat per mm | `workloads/nocbench`, `workloads/onchip`, `workloads/enercat/run_wire.py` | the commands of E22–E25 and E31–E32 in `docs/findings/03-experiments.md` | `docs/reports/data/2026-09-22-hotline-*` (with the hand-kept `context.json`), `-onchip-*`, `2026-09-24-wire*` | the same entries (the hot line's `analyze_hotline.py` takes `--context` and `--barrier`), then `scripts/build-report.py` (the exact final commands are in [`reports/MIRROR.md`](reports/MIRROR.md), "How each page is built") |
| Energy manual, catalogue | `workloads/enercat` | `run_catalogue.py DATA --passes 3` on each card (2.6 h each; keep the die warm on aifoundry2) | `docs/reports/data/2026-09-23-catalogue-aifoundry2`, `-aifoundry3`, `-aifoundry2-rows` | `analyze_catalogue.py A2 A3 A2_ROWS --out catalogue.json`, `fit_unmetered.py --out unmetered_fit.json --overwrite`, then `tools/ettelem/build_energy_manual.py`, `render_energy_manual.py`, `render_catalogue.py`, `scripts/build-report.py energy-manual manual.json HTML` (`docs/findings/04-artifacts.md`, A16, gives the full order) |
| Energy manual, reruns | `tools/ettelem/run_reruns_warm.sh`, `run_rings_levels_power.sh` | 3 passes each of relay, hot line, rings, levels per card; preheat aifoundry2 | `docs/reports/data/2026-09-23-reruns-aifoundry2-warm`, `-aifoundry3` | `tools/ettelem/analyze_reruns.py DIRS --out reruns.json` (bursts off 600 MHz dropped) |
| Limits of observability | `docs/reports/sources/limits-of-observability.*` | reads the firmware and the catalogue; no card time | `docs/reports/data/2026-09-23-energy-manual/` (`unmetered_fit.json`, `catalogue.json`, `manual.json`, `reruns.json` and the rerun directories it names), `docs/reports/data/2026-09-22-dvfs-aifoundry2/dvfs.json`, `2026-09-24-wire-energy/report.json`, `2026-09-21-horace-aifoundry2/model.json` and `report.json` | `python3 tools/ettelem/sync_hub_data.py` (writes the data file's computed blocks; `--check` exits 1 if they are stale; rerun it after regenerating any of those files), then `scripts/build-report.py limits-of-observability docs/reports/sources/limits-of-observability.data.json HTML` |
| Sparsity | `workloads/sparsity` | `run_lab.sh`, then `run_energy.py` twice, the second time with `--only` in reverse order (`workloads/sparsity/README.md`) | `docs/reports/data/2026-09-18-sparsity-aifoundry3` | `python3 workloads/sparsity/analyze.py DATA --later docs/reports/data/2026-09-22-horace-aifoundry3/horace3.json --embed HTML` |
| Ridge points | `scripts/ridge-points.py` | nothing: derived from the four 2026-09-18 reports | their four data directories, and the energy manual's `manual.json` | `python3 scripts/ridge-points.py --embed HTML` (`docs/findings/04-artifacts.md`, A19, gives the input chain) |

- **Measuring.** Build on the machine with `scripts/deploy-lab.sh aifoundry2 workloads/<name>`, or
  `scripts/deploy-lab-gpsdk.sh` for `kernels/`. Follow the etiquette above, then copy the outputs back into a new
  dated directory under `docs/reports/data/`. The runs print JSON lines that the analysis scripts read.
  Workloads also run on the simulator with `--sysemu` (small sizes), which checks correctness but not speed.
- **Analysis.** You need Python 3. The on-chip communication analysis also needs numpy. It prints every number
  the page quotes, including the one-hop ring and the mesh-time decomposition.
- **Publishing.** Every space the hub links is public (Q40). Update one in place with its uuid from
  [`reports/MIRROR.md`](reports/MIRROR.md), which also gives each page's final build command. You can use the CLI
  (section 5) or the spacesheep MCP: `stage_begin`, then `curl -X PUT` the file, then `deploy` with the uuid.
  Afterwards run `spacesheep list`, compare the visibility with MIRROR.md, and run `python3 scripts/check-mirror.py`.
- **What will differ.** Another card can have a different shire map if a different shire is fused off. It can
  also run at another clock: the governor moves between 600 and 800 MHz (three points: 600, 700, 800), and time on the mesh is fixed in ns. And
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
| `/opt/et` on aifoundry2 | et-platform `353f20e` (Dec 2025): runtime 0.19.0, GCC 15.1 | installed by the lab |
| `/opt/et` on aifoundry3 | the same, except `libetrt.so`: a patched Release `-O3` build of `836a4ab` (2026-07-23) | installed by the lab |
| `/opt/et` on aifoundry1 | a build of an et-platform fork (May 2026): its runtime and device layer differ, and the device layer honours `ET_DEVICES=<n>`; `libDM.so`, `dev_mngt_service`, `et-powertop` and GCC 15.1 as on the others | installed by the lab |
| Card firmware | 1.3.1 on aifoundry2 and aifoundry3 (a build of about mid-May 2024); 1.4.1 and 1.2.0 on aifoundry1's cards 0 and 1 | flashed by the lab; read with `dev_mngt_service -m DM_CMD_GET_MODULE_FIRMWARE_REVISIONS` (`docs/reports/data/2026-09-25-claims-v3/firmware.md` for aifoundry2 and aifoundry3, `AMENDMENTS.md` A2 there for aifoundry1) |

`UPSTREAM_LATEST=1 scripts/clone-upstream.sh` and `TOOLCHAIN_REF=et scripts/provision-vm.sh` build the branch tips
instead of the pins.
