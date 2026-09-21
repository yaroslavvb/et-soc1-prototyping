# Horace experiment, third version (aifoundry2, 2026-09-21)

Data behind `docs/reports/2026-09-20-horace-experiment.html`. Rebuild everything below from the raw runs with
`tools/ettelem/finish_horace.sh <strict-run-dir> <cold-run-dir>...`.

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
| `report.json` | What the report embeds (`tools/ettelem/build_horace_report_data.py`) |

Protocol of the strict run: `tools/ettelem/run_horace_strict.sh build/horace3 80 84 4 5 2 7 "<main>" "<extra>"`: heat
to 84 C with random-data bursts if below, idle until the mean minion-shire sensor first reads 80 C, run one pattern
for 7 s. Four burn-in cycles, then five shuffled blocks of the six main patterns; the eight extra patterns run in the
first two blocks only. Random patterns use seed = block + 1.
