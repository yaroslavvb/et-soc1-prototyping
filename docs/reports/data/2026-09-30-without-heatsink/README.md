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

## Rebuild

From the repository root (about 3 minutes for the model, 4 for the page data; `nice -n 19` on a shared machine):

```
V=docs/reports/data/2026-09-30-without-heatsink
python3 $V/nohs_calc.py > $V/nohs_calc.out
python3 $V/card0_guard.py > $V/card0_guard.out
python3 $V/make_page_data.py
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
