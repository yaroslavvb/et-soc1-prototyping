# Matmul energy benchmark, aifoundry2, 2026-09-18

Raw data behind `docs/reports/2026-09-18-et-soc1-matmul-efficiency.html`, from `make bench-power` in `~/nekko` on
aifoundry2. That runs `scripts/mmbench-power.py`, which drives `launchers/mmbench` and samples board power. The steps are in
`docs/getting-started.md`, section 4. The run writes three files:

- `power.csv`: board power samples.
- `runs.jsonl`: one record per launch.
- `results.json`: per-workload throughput and power.

Regenerate the report's numbers and power chart with
`scripts/mmbench-report-data.py docs/reports/data/2026-09-18-aifoundry2 --embed docs/reports/2026-09-18-et-soc1-matmul-efficiency.html`.
