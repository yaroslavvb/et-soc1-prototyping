# Feasibility of running the ET-SoC-1 without its heatsink (30 September 2026)

The data behind [docs/reports/2026-09-30-esperanto-without-heatsink.html](../../2026-09-30-esperanto-without-heatsink.html),
the feasibility study the owner asked for on 29 September 2026 at 17:30 PDT: can a lab card run with its heatsink off so
that a temperature sensor can look straight at the chip, and what would work instead. Arithmetic on the record only: no
card was touched.

| File | What it is |
|---|---|
| `nohs_calc.py` | The feasibility model. Package geometry and heat capacities (A), the bare package's θJA in still air and with a fan (B), each card's idle power law and the SoC's share (C), steady state and the runaway condition θ·dP/dT < 1 with a Monte Carlo over the uncertain inputs (D), transients from a cold or hot start and the host-boot window (E), a lid thermocouple's error budget (F), and lateral decay lengths for each view of the chip (G). Every input names its source or is marked ASSUMED / ESTIMATE; seed 20260929. |
| `nohs_calc.out` | Its full printout: 5th / 50th / 95th percentiles unless a line says otherwise. The page takes every table from it. |
| `card0_guard.py`, `card0_guard.out` | aifoundry1 card 0's idle board and rail power at 300 MHz against its die mean, from the 21 read-only `guard.jsonl.gz` files under `docs/reports/data/` (12,035 samples at 60–64 °C): 17.97 W at 62 °C, rising 0.207 W/°C (rails 0.180). The model's card-0 law comes from here. |
| `make_page_data.py` | Writes `page.json`. It imports `nohs_calc.py` with its printout captured, stops if the printout no longer matches `nohs_calc.out`, parses the tables from it, and runs the one thing the model does not print: aifoundry2's junction temperature after a cold power-on, bare in still air, bare with a fan (the model's two-node transient with its input ranges) and with the heatsink (the Foster chain fitted on aifoundry2, `docs/findings/11-thermal-model.md`), at idle and under a random-data matmul on 1,024 minions, 400 draws each, seed 20260930. The ranked options table is written out in it. `--check` exits 1 if `page.json` is stale. |
| `page.json` | The page's data. |
| `lowclock_calc.py` | The envelope model for section 5 (added on the evening of 30 September, at the owner's request of about 15:45 PDT: how low can the clock go, 100 MHz, 10 MHz, and can a slow card run bare under a thermal camera). Board power and the bare package's outcome at 600–10 MHz under three voltage policies (voltages left, the firmware's floors, floors with the NoC lowered), built on the record's per-rail idle laws: the clock tree is shared across the three 600 MHz cards and leakage's voltage law is fixed by aifoundry2's 800 MHz idle and card 0's 300 MHz rails. It also gives the 90 % envelope, the floor no clock removes, the cooling each point needs (θ85), the window after the host boots, and imaging at each settable point (from `imaging_calc.json`). numpy only; seed 20260930, 2,000 accepted draws; about 2½ minutes. It checks its list of settable clocks against `external/et-platform/etsoc-hal/include/hwinc/hpdpll_modes_config.h` when that is present. |
| `lowclock_calc.out`, `lowclock_calc.json` | Its printout (sections A–I, every line labelled measured, source, outside, fitted, model, assumed or inference) and every table as JSON (`--json`). |
| `imaging_calc.py`, `.out`, `.json` | The imaging model: a layered spectral conduction model of die, paste, lid, heatsink, substrate and board (steady, lock-in and step responses), the lab's camera and the 34 on-die sensors' noise, and four patterns of work; the contrast each view gives, the camera's thresholds, the least clock and the lock-in time for each pattern, and the stock sensor's whole-degree readings simulated with and without a dither. Seed 20260930, 240 draws; about 8 minutes. It checks its grid and the heat-placement MAP measurement against `../2026-09-28-heat-placement/heat.json` and `val.json`. |
| `lc_plan_calc.py`, `lc_plan_calc.out` | The low-clock measurement plan's registered predictions for aifoundry3 (the idle step at 400–100 MHz, the leakage exponent from aifoundry2's idle reset, the lowest settable point, the bare card there by `nohs_calc.py`, which it imports, the schedule) and, in section K, the envelope model's predictions restated in the plan's terms. Seed 20260930; about 5 minutes; run after `lowclock_calc.py`. |
| `pll_modes.py`, `pll_modes.out` | The firmware facts decoded: every step-clock PLL mode with the 100 MHz reference (what `DM_CMD_SET_FREQUENCY` accepts: 100 MHz is the lowest), the per-shire PLL's range, the boot modes, the dividers' headroom below the tables, and each BL2 build's voltage range checks and safe state. Reads `external/et-platform` (found from its own path) with `git show` for each build. |
| `LOWCLOCK-FIRMWARE.md` | The firmware notes behind section 5, condensed from the working notes with their section numbers: every fact with its file and line in et-platform or the manuals. |
| `LOWCLOCK-PLAN.md` | The low-clock measurement plan (design only, not run; it needs the owner's go-ahead and the lab lead's consent): Stage 0 read-only, Stage A the clock steps heatsink on, Stage B the voltages at 100 MHz, the safety rules and exit paths, and the gated bare step. |
| `LOWCLOCK-OUTSIDE.md` | The outside research behind the page's sources [44]–[53], with its verbatim quotes (a copy of the working notes `~/claude/work/lowclock/outside.md`, paths written from `~`). |

## Rebuild

From the repository root (about 3 minutes for the model, 4 for the page data; `nice -n 19` on a shared machine):

```
V=docs/reports/data/2026-09-30-without-heatsink
python3 $V/nohs_calc.py > $V/nohs_calc.out
python3 $V/card0_guard.py > $V/card0_guard.out
python3 $V/imaging_calc.py --json $V/imaging_calc.json > $V/imaging_calc.out      # before lowclock_calc.py
python3 $V/lowclock_calc.py --json $V/lowclock_calc.json > $V/lowclock_calc.out   # before lc_plan_calc.py
python3 $V/lc_plan_calc.py > $V/lc_plan_calc.out
python3 $V/pll_modes.py > $V/pll_modes.out
python3 $V/make_page_data.py                                                       # about 4 minutes
NODE_PATH=$PWD/node_modules python3 scripts/build-report.py esperanto-without-heatsink $V/page.json docs/reports/2026-09-30-esperanto-without-heatsink.html
```

The page's sources are `docs/reports/sources/esperanto-without-heatsink.{body.html,script.js,meta.json}`.

## Notes

- The model was first run on 29 September; the copy here differs in two respects. The equilibrium Monte Carlo's lines now
  print their counts ("1 of 600"): they show that one aifoundry2 fan draw in 600 does reach a stable idle temperature
  (66 °C), which the first printout's rounding ("0%") hid. And three labels changed on 30 September, when the outside
  research was merged: section B's two cross-check notes now quote the vendor tables (AMD UG575 Table 10-1, Microchip
  UG0722 Table 9-1) instead of an unsourced "typical 8-12 / 4-7 C/W", and section F's heading calls the heatsink-base
  groove a variant of Intel's grooved-lid method rather than Intel's own. Every number is unchanged (same seed, same
  draws), and so is every line number.
- The with-heatsink trajectory under load adds the fitted model's 1.85 W for the tensor state machines of 1,024 minions
  and 27.2 W of switching for random-normal operands (`11-thermal-model.md`, `12-heat-management.md` line 20) to the
  board power, since the Foster chain was fitted on board power. The bare trajectories add 23 W on the die, the share
  of that load the model puts on the SoC.
- Line references inside nohs_calc.py/.out are to commit 70447ec.
- Before publication (30 September) the page went through a citation check of its outside sources and a review. In
  `page.json` only two strings changed: option 2's "what it measures" and the prerequisite line (which now cite the
  full camera plan). Every model number, and the trajectories, are unchanged; `--check` confirms it.
- The 30–90 s from power-on to the first telemetry reading is an assumption: the hosts' boot time is not recorded.
- Outside research (vendor θJA tables, bare-processor runs, the runaway criterion, IR-window coolers and lock-in
  thermography, the case-temperature thermocouple method, heatsink refitting and delidding, IR window materials and
  coolants, Esperanto's public figures) is cited on the page as [1]–[43], listed under "Outside sources" with what each
  gives. `page.json` carries the vendor θJA ranges as `bare.vendor_still` and `bare.vendor_fan`. The page's option 3 is
  Intel's grooved-lid thermocouple, since AMD advises against any thermocouple between package and heatsink; the
  model's section F error budget, drawn up for a heatsink-base groove, is used for it as an upper estimate.
- Section 5 (30 September, evening). `make_page_data.py` now also writes a `lowclock` block: it reads `lowclock_calc.json`,
  `imaging_calc.json` and `lc_plan_calc.out` and stops if a JSON no longer matches its printout; it recomputes nothing.
  Every other block of `page.json` is unchanged from the published version except the options table, whose options 1
  and 6 were reworded to take in the low-clock findings. The imaging model was run once in the work directory and once
  here: the JSON is byte-identical and the printout differs only in the path on its last line. The firmware notes and
  the plan are copies of working files (`~/claude/work/lowclock/fw.md`, `plan.md`). Outside sources [44]–[53] are cited
  on the page; the outside research behind them, with verbatim quotes, is `LOWCLOCK-OUTSIDE.md`.
- Section 5 after review (30 September, late evening). Three reviews (physics and numbers, source fidelity, the owner's
  reading) were checked one by one; the real findings changed the models as follows, and every section-5 number on the
  page moved with them (the other blocks of `page.json` are unchanged, apart from the wording of options 1 and 6 of the
  ranked table, which now carry the stock sensor's dither and the bare look's odds):
  - `lc_plan_calc.py` F: the blower's board-to-air resistance in the power-on model is drawn from `nohs_calc.py`'s own
    formulas at 3–6 m/s (1.14–2.31 °C/W) instead of an assumed 0.5–1.5; the blower's power-on share falls from 80 % to
    44 %, below the plan's 80 % gate.
  - `lowclock_calc.py` F2: the window now adds the plan's 20–60 s to set the low point after the host boots, and runs
    to the plan's stops (75 °C watcher, 80 °C relay) as well as 85 °C; the board node's off-die heat now falls with the
    regulator loss a lower point removes and rises with a workload's off-die share. F2 also settles the transient
    model's two-node network, which counts the board's heating by the off-die power, beside section F's θ draw.
  - `lowclock_calc.py` C: anchor (i) now includes the SRAM rail's recorded 704 → 830 mV step at 800 MHz (E51), which
    gives the SRAM's leakage law an anchor; about 2.5 % of the prior draws pass both anchors (the candidate pool is
    80 × the draws). The regulator-loss coefficients are E46's per rail (NoC 0.29, SRAM 0.03–0.04; card 1's SRAM 0.54).
  - Both models: the per-shire switching power is drawn 0.60–0.76 W (was 0.55–0.75, below aifoundry2's runs), and the
    floor voltage is 398 mV in both.
  - `imaging_calc.py`: an IR-window cooler's window and oil-film transmission (assumed 0.85–0.95 × 0.6–0.95); the camera
    thresholds printed; the stock I/O sensor's whole-degree readings simulated with and without a slow dither of the
    chip's power (a separate random stream, so the rest of the model is unchanged).
  - The race between `DM_CMD_SET_FREQUENCY` and the governor was checked at et-platform HEAD `836a4ab`: still present,
    reachable (the command's task has the higher priority) and wider than one comparison (`LOWCLOCK-PLAN.md` §2.2).
- Below 300 MHz nothing in section 5 has been seen on a card: the settable clocks, the voltage floors, the governor's
  behaviour and the race between `DM_CMD_SET_FREQUENCY` and the governor's loop are read from firmware source; the
  powers, settling and imaging times are model numbers. Any clock, voltage or governor write needs the owner's approval.
