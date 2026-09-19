# On-chip communication measurements, aifoundry2, 2026-09-18

Raw data behind `docs/reports/2026-09-18-et-soc1-on-chip-communication.html`. The minion clock was 600 MHz
throughout, according to `clock.csv`. `workloads/nocbench/run_lab.sh` makes the `*.jsonl` files and `clock.csv`:

```bash
ssh aifoundry2 'cd ~/nekko && bash workloads/nocbench/run_lab.sh build/nocbench/host/nocbench_host OUTDIR'
```

| Files | `run_lab.sh` group | What it is |
|---|---|---|
| `classes-{pingpong,fcc,flag}.jsonl` | classes | Round trips from minion 0.0 to 17 partners: fast-network pairs, the rest of its neighbourhood and shire, and shires 1-10 hops away |
| `counts-pingpong.jsonl`, `counts-stream.jsonl` | counts, stream | Round trip and one-way time per message, from 1 to 127 registers (32 B to 4 KB) |
| `functs-{iadd,imax,fadd,fmax}.jsonl` | functs | The same round trip with a combine on receive |
| `matrix-pingpong{,-m31,-c32}.jsonl` | matrix | All 496 shire pairs, minion 0 (or 31) of each, with 32 B (or 1 KB) messages |
| `intra-pingpong{,-s24}.jsonl` | matrix | All 496 minion pairs inside shire 0 (or 24) |
| `fcc-inshire-{block,poll}.jsonl`, `matrix-{fcc,flag}.jsonl` | sync | Credits with blocking and polled waits, and the shire matrices for credits and memory flags |
| `allreduce{,-all}-c{1,8,32}.jsonl` | allreduce | Trees of 2-32 minions, in shire 0 alone and in all 32 shires at once |
| `xallreduce-c{1,32}.jsonl` | xallreduce | Trees of 64-1024 minions, across shires |
| `barrier-{shire,chip}{1,32}.jsonl` | barrier | Shire and chip-wide barriers |
| `isolated-pairs.jsonl`, `loaded-pairs.jsonl` | loaded | 16 cross-shire pairs, one at a time and all at once |
| `clock.csv` | (all) | Minion clock and board power, sampled by the script while it runs |
| `device-info.txt` | | The runtime's device report, printed by every run |

The energy data comes from `workloads/nocbench/run_energy.py`, which runs rings of 1 KB messages at different distances
while it samples board power:

- `energy-a/`: `run_energy.py --host-bin build/nocbench/host/nocbench_host --out OUTDIR/energy-a`.
- `energy-b/`: the same with `--only xshire1-c4,shire-c4,xshire6,xshire4,xshire2,xshire8,xshire16,xshire1,shire,neigh,pair,spin`
  (the reverse order).
- `first-energy-run/`: an earlier version of the script, with a single idle baseline and fewer configurations.
  The card was cooling during it, so the report does not use it. It is kept for provenance.

Each line of a `*.jsonl` file is one `NOCBENCH {json}` record. A `launch` record starts each kernel launch, and
`pair`, `allreduce`, `barrier` or `throughput` records follow it. `ok` says whether the data check passed. Regenerate
the report's numbers and chart data with
`python3 workloads/nocbench/analyze.py docs/reports/data/2026-09-18-nocbench-aifoundry2 --memhier docs/reports/data/2026-09-18-memhier-aifoundry2 --search --embed docs/reports/2026-09-18-et-soc1-on-chip-communication.html`.
