# pciebench: the host link and the launch path

A standalone host program and an empty device kernel (et-testdrive style, runtime API only) that time what a program
gets over the ET-SoC-1's PCIe link: copy bandwidth from 4 KB to 256 MB in both directions, staged (the runtime's
bounce copy, the normal path) and DMA-only (the API's `cmaCopyFunction` replaced by a no-op: the same DMA without the
host copy), small-copy latency, empty-kernel launch latency, and several transfers at once. Every result is a line
`PCIE {json}`; each process stops starting new work at `--budget` seconds (8.5 by default, at most 9.5).

```
cmake -S workloads/pciebench -B build/pciebench -DCMAKE_PREFIX_PATH=/opt/et -Wno-dev && nice cmake --build build/pciebench -j4
timeout 10 build/pciebench/host/pciebench_host --test info|bw|lat|launch|conc|hostcopy [--budget 8.5] [--verify]
TREE=$PWD workloads/pciebench/run_pcie.sh <run>     # one run of every test (V3_DEVICE=1 on aifoundry1; V3_DRY=1: no device)
workloads/pciebench/schedule.sh 1 5                 # the 27 September schedule, from aifoundry2 over the three cards
python3 workloads/pciebench/reduce_pcie.py <raw> --prereg <PREREG.md> --out pcie.json --md results.md
```

`run_pcie.sh` takes the card's lock for each device-opening process and releases it between them (since 28 September;
the runs of 27 September held it for the whole run, 12.8–14.9 s, longer than AGENT.md §5's 10 s): it checks for other
users again before each process, waits up to `PCIE_LOCK_WAIT` seconds (20) for the lock, and stops with exit 3 if the
lock stays held, moving the partial run aside so that a retry starts clean. The card's own temperature samples before
and after take the lock the same way, and a run whose sample could not stops the same way, since the 90 °C gates need
it. A run that had to wait for the lock between sub-tests is kept and flagged (`lock_waits` in its `run.json`;
`reduce_pcie.py` lists it in `hosts.<card>.lock_waited_runs` and in the results). `V3_DRY=1` prints each device process
instead of running it, and takes a lock file beside the output instead of the card's.

Files: `host/main.cpp` (the tests; its header explains staged and DMA-only), `kernel/empty.c` (the kernel),
`run_pcie.sh`, `schedule.sh`, `reduce_pcie.py`. The data, the predictions and the page:
`docs/reports/data/2026-09-27-pcie/` and `docs/reports/2026-09-27-et-soc1-pcie-link.html`.
