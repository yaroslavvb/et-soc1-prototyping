# Matmul energy benchmark, aifoundry2, 2026-09-18

Raw data behind `docs/reports/2026-09-18-et-soc1-matmul-efficiency.html`, from `make bench-power` in `~/nekko` on
aifoundry2. That runs `scripts/mmbench-power.py`, which drives `launchers/mmbench` and samples board power. The steps are in
`docs/getting-started.md`, section 4. The run writes three files:

- `power.csv`: board power samples.
- `runs.jsonl`: one record per launch.
- `results.json`: per-workload throughput and power.

Regenerate the report's numbers and power chart with
`scripts/mmbench-report-data.py docs/reports/data/2026-09-18-aifoundry2 --embed docs/reports/2026-09-18-et-soc1-matmul-efficiency.html`.

The report's "Per W above idle" column subtracts the idle just before each workload (30.61, 32.53, 33.83 and 35.16 W
for fp32, fp16, int8 and the DRAM run; `idle_before()` in `scripts/mmbench-power.py`, recomputed from `power.csv`
and `runs.jsonl` by `scripts/mmbench-report-data.py`), not `results.json`'s single `idle_w` of 30.61 W. The die warmed
over the session and leaked more, so `results.json`'s `gflops_per_w_above_idle` is superseded for fp16, int8 and
DRAM. Runs made with the current `scripts/mmbench-power.py` also store `idle_before_w`.

Run without `--embed`, the script prints both figures for each workload: "idle before … above it" is the report's
column (366.3, 711.2, 2,571.4 and 37.9 GFLOP/s per W, the int8 one in GOP/s), and "above first idle" is
`results.json`'s `gflops_per_w_above_idle` (366.3, 663.7, 2,305.2 and 24.3).
