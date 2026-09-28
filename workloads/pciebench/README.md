# pciebench: the host link and the launch path

A standalone host program and an empty device kernel (et-testdrive style, runtime API only) that time what a program
gets over the ET-SoC-1's PCIe link: copy bandwidth from 4 KB to 256 MB in both directions, staged (the runtime's
bounce copy, the normal path) and DMA-only (the API's `cmaCopyFunction` replaced by a no-op: the same DMA without the
host copy), small-copy latency, empty-kernel launch latency, and several transfers at once. Every result is a line
`PCIE {json}`; each process stops starting new work at `--budget` seconds (8.5 by default, at most 9.5).

```
cmake -S workloads/pciebench -B build/pciebench -DCMAKE_PREFIX_PATH=/opt/et -Wno-dev && nice cmake --build build/pciebench -j4
timeout 10 build/pciebench/host/pciebench_host --test info|bw|lat|launch|conc|hostcopy [--budget 8.5] [--verify]
TREE=$PWD workloads/pciebench/run_pcie.sh <run>     # one run of every test under the card's lock (V3_DEVICE=1 on aifoundry1)
workloads/pciebench/schedule.sh 1 5                 # the 27 September schedule, from aifoundry2 over the three cards
python3 workloads/pciebench/reduce_pcie.py <raw> --prereg <PREREG.md> --out pcie.json --md results.md
```

Files: `host/main.cpp` (the tests; its header explains staged and DMA-only), `kernel/empty.c` (the kernel),
`run_pcie.sh`, `schedule.sh`, `reduce_pcie.py`. The data, the predictions and the page:
`docs/reports/data/2026-09-27-pcie/` and `docs/reports/2026-09-27-et-soc1-pcie-link.html`.
