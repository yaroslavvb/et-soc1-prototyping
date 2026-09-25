# Horace experiment and low-power ablations (aifoundry2, 2026-09-21)

Data behind `docs/reports/2026-09-20-horace-experiment.html` and `docs/reports/2026-09-21-why-low-power.html`. Rebuild the
analyses, the model, the GIFs and both reports with `tools/ettelem/finish_horace.sh`.

| Path | What |
| --- | --- |
| `strict/runs.jsonl` | One line per kernel launch (`sparsity_host`), tagged with its block. Block -9 is a pre-heat burst, -1 burn-in |
| `strict/starts.jsonl` | One line per measured run: pattern, seed, the reading at launch, seconds spent heating and cooling to it |
| `strict/telemetry.jsonl.gz` | 10 Hz `ettelem sample`, cut down to the fields the analysis reads (`tools/ettelem/compact_telemetry.py`) |
| `strict/tiles/<pattern>.<seed>.bin` | The A and B operand tiles the card ran (2 x 1,024 bytes), replayed by `rtl-sim/fma_toggle` |
| `toggles.json` | Switching activity of the multiply-add units per pattern (`rtl-sim/fma_toggle/toggles.py`) |
| `predictions_before.json` | Power predicted for six new patterns before they were first run, from the 20 September data |
| `horace3.json`, `horace3.txt` | `tools/ettelem/analyze_horace_strict.py`: per run and per pattern results, thermal network, power model, chain |
| `cold1/`, `cold2/`, `cold*.json` | Cool-start runs (`run_horace_cold.sh`) and their analysis: clock, FLOPS, power per run |
| `long/`, `long.json` | Runs of up to ten minutes with a 90 °C cap (`run_horace_long.sh`, schedule in `long/schedule.txt`) and their per-run summary. The card's cooling changed abruptly 13,950 s into the session; fits stop there |
| `long2/`, `long2.json` | Long validation runs of the structured matrices (tested causally in `validation_afternoon*.json`; `model2.json` and `model2.txt` are a superseded non-causal evaluation, no longer produced and read by no page) |
| `model_firsthalf.json`, `validation_timesplit.*`, `validation_afternoon*.*` | Out-of-sample tests (`tools/ettelem/validate_flip_model.py`): every parameter refitted on the first 7,400 s of the long session and frozen, the later runs and the afternoon session predicted with the launch state estimated from earlier telemetry only |
| `model.json`, `model.txt` | The flips-to-temperature model (`tools/ettelem/flip_thermal_model.py`): leakage, flip energies, thermal network, per-run predictions |
| `structured_tiles/`, `structured_toggles.json`, `structured_predictions_before.json` | Structured 16x16 operand pairs (`make_tiles.py`), their RTL activity, and the predictions recorded before they ran |
| `ablation/`, `ablation.json`, `vf.json` | Strict 7 s runs of the low-power ablations and the structured matrices (`run_ablation.sh`, `ablation/configs.txt`); the 600 and 800 MHz operating points from the cool starts (`vf.json`, written by `tools/ettelem/build_vf.py`, whose `rules` field states each window) |
| `toggles_all.json` | `toggles.json` and `structured_toggles.json` merged, for the model |
| `report.json`, `lowpower-report.json` | What the two reports embed (`tools/ettelem/build_horace_report_data.py`, `build_lowpower_report_data.py`) |
| (in `docs/reports/data/2026-09-22-horace-aifoundry3/`) `horace3.json`, `cards.json`, `transfer.json`, `leakage_crosscard.json` | The second card's strict session and how the model transfers to it: `analyze_horace_strict.py`, `compare_cards.py` and `tools/ettelem/transfer_cards.py`, which `finish_horace.sh` runs before merging the three-machine block (`build_cards_data.py`) |

Protocol of the strict run: `tools/ettelem/run_horace_strict.sh build/horace3 80 84 4 5 2 7 "<main>" "<extra>"`: heat
to 84 °C with random-data bursts if below, idle until the mean minion-shire sensor first reads 80 °C, run one pattern
for 7 s. Four burn-in cycles, then five shuffled blocks of the six main patterns; the eight extra patterns run in the
first two blocks only. Random patterns use seed = block + 1.
