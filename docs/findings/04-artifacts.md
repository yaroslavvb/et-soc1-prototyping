# Artifacts: what was published, and where it lives

Three kinds of artifact came out of this work: **published reports** (HTML, deployed to spacesheep.dev),
**repostable images**, and **tools** that can be re-run. Commits are listed at the end so any artifact can be
tied to the state of the tree that produced it. Cite as **A1**...**A15**.

Every report is assembled by `scripts/build-report.py <name> <data.json> <out.html>` from three sources in
`docs/reports/sources/`: `<name>.meta.json` (title, description), `<name>.body.html` (the prose) and
`<name>.script.js` (the charts, which read the embedded data as the constant `D`). **Editing the HTML directly
is always wrong** — it is regenerated.

---

## Published reports

| ID | Report | Built from | Space | Visibility (2026-09-22) |
|---|---|---|---|---|
| A1 | `docs/reports/2026-09-19-et-soc1-memory-anatomy.html` — one memory access by stage and rail | E1, E2 | [et-soc1-memory-anatomy](https://spacesheep.dev/@yaroslavvb/et-soc1-memory-anatomy) `2bf74fd1-fd7f-4e19-8e35-6168ae42657c` | private |
| A2 | `docs/reports/2026-09-20-et-soc1-limits-of-observability.html` — what can be seen, from board power to a flip-flop | R1, R2, R3, E2 | [et-soc1-limits-of-observability](https://spacesheep.dev/@yaroslavvb/et-soc1-limits-of-observability) `2ea37420-67b9-484e-9d4c-581e8a9f0323` | private |
| A3 | `docs/reports/2026-09-20-et-soc1-power-temperature.html` — every way to measure power and energy, and a load step through all of them | E5, E6 | [et-soc1-power-temperature](https://spacesheep.dev/@yaroslavvb/et-soc1-power-temperature) `acee5c6d-56c0-45e7-aa97-ce11af37bdd8` | public |
| A4 | `docs/reports/2026-09-20-horace-experiment.html` — the data-dependent power experiment, the flip model, the long runs, the structured matrices, the second card (**six versions**, see below) | E7–E17, E20 | [et-soc1-horace-experiment](https://spacesheep.dev/@yaroslavvb/et-soc1-horace-experiment) `da445a93-7be3-42c2-b9be-4992fa4a3b62` | public |
| A5 | `docs/reports/2026-09-21-why-low-power.html` — Esperanto's equation measured term by term against an A100 | E15, E10, R6, R7, R8 | [et-soc1-why-low-power](https://spacesheep.dev/@yaroslavvb/et-soc1-why-low-power) `baede20c-57d9-4e01-8157-2014670dd8cf` | public |

| A11 | `docs/reports/2026-09-22-dvfs-leakage.html` — six of David Kanter's claims about DVFS loops and leakage suppression, checked against the firmware, the RTL and the card | R9, R3, R2, E10, E18, E19, E20, E21 | [et-soc1-dvfs-leakage](https://spacesheep.dev/@yaroslavvb/et-soc1-dvfs-leakage) `171dcd4a-5b6d-49d3-aca0-db4980fabfa5` | **public** (the repo owner made it public on 2026-09-22 and asked that it stay so) |

| A13 | `docs/reports/2026-09-22-hot-line.html` — one contended global atomic: fair to the shire that hosts it, and fatal to that shire's own memory path | R11, R1, E22, E23 | [et-soc1-hot-line](https://spacesheep.dev/@yaroslavvb/et-soc1-hot-line) `ac439287-4503-42c7-88e7-b5d3e3b64b06` | private (default; it quotes a Discord message) |

| A14 | `docs/reports/2026-09-22-on-chip-relay.html` — handing a stage's output to a neighbouring shire instead of DRAM: 12× faster at a twelfth of the energy | R12, E24, E25 | [et-soc1-on-chip-relay](https://spacesheep.dev/@yaroslavvb/et-soc1-on-chip-relay) `8678d49d-3f0c-49be-b08a-5528de8ece3c` | private (default) |

| A15 | `docs/reports/2026-09-23-energy-manual.html` and `docs/energy-manual/*.md` — the energy manual: at rest, awake, per instruction, per byte, between shires, synchronisation, composition, two cards, method | E26 and every earlier E through its builder | [et-soc1-energy-manual](https://spacesheep.dev/@yaroslavvb/et-soc1-energy-manual) `cc3cb1d6-51cf-420b-a165-7d8629904d97` | private (default) |

Earlier reports in the same repository, from before this line of work (R4): matmul efficiency, memory
hierarchy (`4b6e0a37-808d-4fc9-8001-555125733c46`), on-chip communication
(`ab8e1b2b-de17-44f4-8645-006fa960e349`), sparsity (`5abf6014-8de0-4e82-8744-5676bac6453e`).

### A4's six versions

A4 was rewritten six times as the question got sharper. The file name never changed, so **only the latest is
on disk**; the earlier ones survive in git history and in the space's version list.

| Version | Commit | What changed |
|---|---|---|
| 1 | `df89c94` | E7: the effect exists, with a fitted temperature correction |
| 2 | `04746a3` | E8: every run started at 80 °C |
| 3 | `f2b8776` | E9–E11: strict control, heating per FLOP, the RTL activity model, the cool-die speed effect, the first GIFs |
| 4 | `07f7d04` | E12–E16: ten-minute runs, the flips-to-temperature model, structured matrices priced before they ran |
| 5 | `75bb061` | E17: fit and prediction separated, held-out validation |
| 6 | *(this commit)* | E20: the same experiment on aifoundry3; the model transfers up to one scale factor; equations rendered as SVG |

## A12 — Math rendered at build time

`scripts/tex2svg.js` turns the TeX in a report body into standalone SVG, called from
`scripts/build-report.py`: display math between `$$`, inline math between `\(` and `\)`, anything inside
`<pre>` or `<code>` left alone. It needs `npm install --no-save mathjax-full` once.

**Why not the usual runtime MathJax:** the first attempt loaded MathJax from `cdn.jsdelivr.net`, and the
publishing host blocks external scripts in viewers with a content-security policy — the deploy says so. Every
equation would have shown as raw TeX to every reader. Pre-rendering also means the files stay self-contained
and the math is identical in every browser. MathJax colours its SVG with `currentColor`, so dark mode works
with no extra rule.

## Repostable images

| ID | File | Public address | Content |
|---|---|---|---|
| A6 | `docs/reports/horace-heating.gif` (0.46 MB) | `https://da445a93-7be3-42c2-b9be-4992fa4a3b62.spacesheep.app/horace-heating.gif` | Five runs each of zeros, ones and random normal: die temperature over 7 s, each run launched at the same temperature. Raw sensor steps plus the recovered curve |
| A7 | `docs/reports/horace-heating-6.gif` (0.91 MB) | same host, `/horace-heating-6.gif` | The same for six kinds of matrix |
| A8 | `docs/reports/horace-long.gif` (0.29 MB) | same host, `/horace-long.gif` | Log time axis: how long each workload takes to drive the die from 80 to 90 °C |

Each has a `.png` poster beside it. They are generated by `tools/ettelem/make_heating_gif.py` and
`make_long_gif.py` with PIL, at 2× and downsampled, one global palette.

## Tools (all under `tools/ettelem/` unless noted)

| Tool | What it does |
|---|---|
| `ettelem` (C++, `tools/ettelem/ettelem.cpp`) | Telemetry client on `libDM.so`. `sample` emits JSON lines at up to 45 Hz: board power, the service processor's per-rail averages and voltages, die and PMIC temperatures, clocks. `config` reads the governor's static inputs: the flashed TDP, the software temperature threshold and the power state (E21). Also `loglevel` and `sptrace`. **Holds the management node open**, which is single-opener |
| `etcfg` (C, `tools/etcfg/etcfg.c`) | The driver's `ETSOC1_IOCTL_GET_DEVICE_CONFIGURATION` as JSON: TDP, boot clock, shire mask, cache sizes. Read-only, no management node, so it works on a machine whose `libDM.so` refuses the card (E21) |
| `compare_cards.py` | Two cards' strict sessions side by side, with the model's predicted switching power for each pattern. Fits nothing (E20) |
| `run_hotline_power.sh`, `analyze_hotline_power.py` | Board power and rails while one atomic line is contended, against the same work spread over 32 (E23) |
| `workloads/nocbench --test hotline` | Many-to-one contention on one global atomic word: per-shire shares in a common window, the host shire's own traffic, the requester and pacing sweeps (E22, E23) |
| `workloads/nocbench/run_hotline.sh`, `analyze_hotline.py` | The 42-configuration sweep and its analysis |
| `workloads/onchip` | `--test probe`: can one shire read what another wrote into its scratchpad, and by which write path (E24). `--test relay`: the same multi-stage computation with its intermediate in DRAM, in the shire's own scratchpad, or in the next shire's (E25). Every run verifies its own output |
| `workloads/onchip/run_onchip.sh`, `analyze_onchip.py` | The 88-configuration sweep and its analysis |
| `run_onchip_power.sh` | Board power per medium, one twelve-second burst each, sized so the card is busy 83% of the time |
| `workloads/enercat` | The instruction and byte energy catalogue: one pattern flat out on every hart, 56 configurations, `run_enercat.sh` and `analyze_enercat.py` (E26) |
| `build_energy_manual.py`, `render_energy_manual.py` | Assemble every table of the manual from its data file into one JSON, and render the markdown from it, so no number on the page is typed by hand |
| `build_cards_data.py` | Assembles the three-machine block and merges it into both reports' data (E20, E21) |
| `run_horace_strict.sh` | The strict-start protocol, shuffled blocks, 7 s runs (E9) |
| `run_horace_cold.sh` | Runs from a cool die, for the governor (E10) |
| `run_horace_long.sh` | Long runs with a temperature cap and a watchdog (E12, E16) |
| `run_ablation.sh` + `ablation.cfg` | Strict-start runs of arbitrary `sparsity_host` configurations (E15) |
| `run_vf_cold.sh` | A careful voltage/frequency comparison. **Written, never run** |
| `make_tiles.py` | Structured 16×16 operand pairs (E13) |
| `analyze_horace_strict.py`, `analyze_horace_long.py`, `analyze_horace_cold.py`, `analyze_ablation.py` | Per-run and per-pattern analysis |
| `flip_thermal_model.py` | Fits the flips → power → temperature model (E17) |
| `validate_flip_model.py` | Tests a **frozen** model on data it was not fitted to; fits nothing (E17) |
| `predict_heat.py` | Prices a custom workload from its operand tiles: flips, watts, heating curve, time to a cap, sustainable duty cycle |
| `compact_telemetry.py` | Shrinks a telemetry log ~70× for storage in the repo |
| `finish_horace.sh` | Rebuilds every analysis, the model, the validations, the GIFs and both reports from the stored raw data |
| `rtl-sim/fma_toggle/` | The Verilator bench that counts switching activity (E11, E13) |
| `rtl-sim/pmu_carry/` | The Verilator bench that reproduces the counter bug (E2) |
| `analyze_dvfs.py` | Classifies every governor transition against the firmware's thresholds and the kernel boundaries; assembles the DVFS brief's data (fits nothing) |
| `workloads/memprobe/gen_ops.py wakeup` | The array wake-up probe (E18) |
| `workloads/sparsity/host/main.cpp` | Extended in this work with `--values` (operand patterns, including `file:<path>` for custom tiles), `--dump-tiles`, `--stop-file` and fp16/int8 value fills |

## Commits

| Commit | Subject |
|---|---|
| `76085a3` | Take one ET-SoC-1 memory access apart, by stage and by power rail |
| `beb262c` | Survey the limits of observability on the ET-SoC-1 |
| `584b9a6` | Add observability tooling: flame graphs, PMU carry root cause, counter syscall |
| `df89c94` | Measure power and temperature; reproduce the Horace matmul experiment |
| `04746a3` | Rerun the Horace experiment with every run started at 80 °C |
| `f2b8776` | Horace experiment, third version: strict control, RTL flip model, thermal chain, GIF |
| `07f7d04` | Long runs, a flips-to-temperature model, structured matrices, and why the chip is low power |
| `75bb061` | Separate fit from prediction in the flips-to-temperature model |

## Publishing notes, learned the hard way

- Deploy with `npx --yes spacesheep deploy <file-or-dir> --space <uuid> -m "<message>"`. **Always pass
  `--space`** when updating, or the CLI creates a new space.
- A folder deploy (`index.html` plus assets, which is how A4 ships its GIFs) has **changed a space's
  visibility in both directions**. Run `npx spacesheep list` after every deploy and fix it with
  `npx spacesheep share <uuid> --visibility public|private`. The visibility column above is a snapshot, and
  visibility is the repo owner's call, not the deploy script's.
- **Delete any `.spacesheep.json` the CLI leaves behind, every time.** It pins a folder to a space, and
  `deploy` uses it when `--space` is absent. On 2026-09-22 a stale `docs/reports/.spacesheep.json` from the
  DVFS brief silently published the hot-line report **over** that brief. The recovery is to remove the pin
  file, redeploy the right HTML with an explicit `--space`, and check the published `<title>`. Safest habit:
  deploy a new report from a directory of its own, and always pass `--space` for an update.
- A new space is private and gets its slug from the file or folder name. Pass `--title`, `--slug`, `--emoji`
  and `--description` on the first deploy, or fix them on the next one; all four are kept on later updates.
