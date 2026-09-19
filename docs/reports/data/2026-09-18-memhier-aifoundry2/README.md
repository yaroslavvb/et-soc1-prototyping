# Memory-hierarchy measurements, aifoundry2, 2026-09-18

Raw data behind `docs/reports/2026-09-18-et-soc1-memory-hierarchy.html`. Every file comes from
`workloads/memhier/run_lab.sh`, run on aifoundry2 with `ssh aifoundry2 'cd ~/nekko && bash
workloads/memhier/run_lab.sh build/memhier/host/memhier_host OUTDIR'`. The group that makes each file:

| File | Group | What it is |
|---|---|---|
| `chase-dram.jsonl`, `chase-dram-sweep-from24.jsonl` | chase | Pointer-chase latency, 256 B to 256 MB, from shire 0 and shire 24 |
| `chase-dram-thread1.jsonl` | chase | The same from hart 1, up to 4 KB |
| `chase-dram-from{7,24,31,0-repeat}.jsonl` | chase | 4 MB (L3) and 256 MB (DRAM) chains from four shires |
| `chase-dram-placement.jsonl`, `chase-dram-offsets.jsonl` | chase | Repeated L3 and DRAM chains in fresh DRAM regions |
| `chase-scp-local.jsonl` | scp | Chains in the shire's own L2 scratchpad |
| `chase-scp-map{,-from7,-from24,-from31}.jsonl` | scp | A 64 KB chain in each of the 32 shires' scratchpads, from shires 0, 7, 24 and 31 |
| `dvfs-poll-during-spin.txt` | dvfs | Clock, minion voltage and board power every ~250 ms around a 2 s spin |
| `energy/`, `energy2/` | energy | Two runs of `workloads/memhier/run_energy.py`: bandwidth and board power per level |

Each line of the chase files is one `MEMHIER {json}` record with the chase's parameters, its cycles per load, its wall
time and epoch timestamps. `ok` says whether the final pointer matched a host-side walk of the chain. Regenerate the
report's numbers and chart data with
`python3 workloads/memhier/analyze.py docs/reports/data/2026-09-18-memhier-aifoundry2 --embed docs/reports/2026-09-18-et-soc1-memory-hierarchy.html`.
