# Sparsity measurements, aifoundry3, 2026-09-18

Raw data behind `docs/reports/2026-09-18-et-soc1-sparsity.html`. The minion clock was 600 MHz in every sample of
`clock.csv` and `diverge/clock.csv`. `workloads/sparsity/run_lab.sh` makes the `*.jsonl` files, `clock.csv` and
`run_lab.log`:

```bash
ssh aifoundry3 'cd ~/nekko && bash workloads/sparsity/run_lab.sh build/sparsity/host/sparsity_host OUTDIR [GROUP...]'
```

| Files | `run_lab.sh` group | What it is |
|---|---|---|
| `fma-{fp32,fp16,int8}-elem.jsonl`, `fma-fp32-{col,row}.jsonl`, `fma-fp16-pair.jsonl` | fma | One minion repeats one 16x16 TensorFMA with a swept fraction of A zero (scattered, whole columns, whole rows, one of each fp16 pair) |
| `fma-fp32-elem-tenb.jsonl` | fma | The same with B streamed through TenB |
| `fma-fp32-bsparse{,90}.jsonl` | fma | Zeros in B instead of A (50% and 90%) |
| `fma-fp32-rowmask-0x{FFFF,00FF,000F,0001,0000}.jsonl` | fma | Dense A under a tensor_mask with 16, 8, 4, 1 and 0 rows enabled |
| `fma-fp32-elem-all.jsonl` | fma | Scattered zeros on all 1,024 minions |
| `tload-{dram,l2,scp}-{one,all}.jsonl` | tload | 16-line TensorLoads under masks of 16 down to 0 lines, on one minion and on all 1,024 |
| `gemv-{dense,masked,skip}.jsonl` | gemv | The 1024x4096 fp32 layer on all 1,024 minions, partial rows summed by the host ("compute only") |
| `gemv-tree-{dense,masked,skip}.jsonl` | gemv | The same layer summed on chip with TensorReduce (`--gemv-tree`) |
| `gemv-{skip,tree}-oneshire.jsonl` | gemv | The layer's first two output blocks on shire 0 alone |
| `diverge/diverge-{static,refill,scalar}-a{0,3,2,1.5,1.2}.jsonl` | diverge | Work items with Pareto-distributed lengths, three lane strategies, all 2,048 harts. `diverge/clock.csv` and `diverge/run_lab.log` are that run's logs |
| `clock.csv` | (all) | Minion clock (MHz) and board power (W), sampled by the script while it runs |
| `run_lab.log` | (all) | The script's output: each command and how many records passed their check |

Each line of a `*.jsonl` file is one `SPARSITY {json}` record, and `ok` says whether the host's exact check passed.
The `*.err` files (runtime log) were not kept. `wait_free` in `run_lab.sh` delays each command until no other process
holds the card.

The energy data comes from `workloads/sparsity/run_energy.py`, which runs each configuration for a few seconds while it
samples board power:

- `energy-a/`: `run_energy.py --host-bin build/sparsity/host/sparsity_host --out OUTDIR/energy-a`.
- `energy-b/`: the same with `--only gemv-skip-99,gemv-skip-90,gemv-skip-0,gemv-dense-90,fma-rowmask,fma-col50,fma-zero,fma-875,fma-50,fma-dense,spin`
  (the reverse order).

Each has `power.csv` (every power sample), `runs.jsonl` (the host's records) and `results.json` (per-configuration power,
throughput and energy). The energy runs predate the change to how the host times a layer (below), so the
`cycles_per_layer_*` fields in their layer records time each block's first minion only. The report uses their layer
rate (`per_s`) and power, which the change does not affect.

Superseded data, kept for provenance:

- `v1/`: the first layer sweeps timed each 16-output block by its first minion. With the tree that minion is the root and
  finishes last, so the tree numbers did not change on the rerun; without the tree they understated the layer. The
  first `tload-dram-one` used a 256 KB buffer, which a lone minion's shire kept in its 512 KB L2, so it measured L2,
  not DRAM. The current host uses the slowest minion of each block and a 64 MB DRAM buffer for a lone minion.
- `diverge-v1/`: an earlier divergence kernel with 4 FMA chains and a fixed split of items per hart.

Regenerate the report's numbers and chart data with
`python3 workloads/sparsity/analyze.py docs/reports/data/2026-09-18-sparsity-aifoundry3 --embed docs/reports/2026-09-18-et-soc1-sparsity.html`.
