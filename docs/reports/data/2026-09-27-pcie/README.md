# The host link and the launch path, on three cards (27 September 2026)

The chip diagram (et-soc1-chip-diagram) quoted the PCIe link only by its figure, Gen4 x8 at 15.75 GB/s per direction,
"not measured". On 27 September the owner asked for it to be measured. This directory is the record: the
predictions stated before the runs, every run's raw output, the reduction and the page's data.
Page: [`docs/reports/2026-09-27-et-soc1-pcie-link.html`](../../2026-09-27-et-soc1-pcie-link.html), built from
`docs/reports/sources/pcie-link.*`.

| File | What it is |
|---|---|
| `PREREG.md` | The predictions (P1-P13), the schedule, the statistic and the pass/fail rule, written at 14:19 PDT before any timed transfer (the pilots came after it). Its sha256 is `7695bf0ac9ffce27d527a81675c5cc19716692d7adbaf8823b10c34185166bb2`, also recorded in `pcie.json` (`meta.prereg_sha256`). |
| `raw/<card>/r<k>/` | One run of the schedule (`workloads/pciebench/run_pcie.sh`): `info.out`, `bw.out`, `lat.out`, `launch.out`, `conc.out`, `hostcopy.out` (lines `PCIE {json}`, the probe's output; `*.err` its stderr, the device layer's banner), `manifest.txt` (`et-lab-manifest`: host, kernel, CPU, driver, link, library hashes), `pre.json`/`post.json` (one telemetry sample of the card: die temperature, clocks, power; on aifoundry1 also `pre-card0.json`/`post-card0.json`, card 0's temperature, read and never used), `run.json` (times, exit codes, the hottest die, the binary's hash). Cards: `aifoundry2`, `aifoundry3`, `aifoundry1-c1` (`ET_DEVICES=1`). |
| `raw/<card>/r0/`, `raw/aifoundry2/pilot1/` | Pilots, after PREREG.md and before the schedule, left out of every figure. `pilot1` (aifoundry2, 14:21) ran the first probe: its fixed order of the four copy variants locked each variant onto one of the runtime's two polling modes, and its concurrency test showed two queued H2D commands at half the rate of one. The probe then gained the shuffled order, the copies after random gaps and the barrier (`/ser`) configurations; `r0` on each card (14:23-14:24) ran that probe. |
| `hosts.txt` | Read from sysfs and `/proc` on the three hosts at 15:03: each card's PCIe address, IOMMU group type (`DMA-FQ`: translated), negotiated and maximum link, and its root port's link; the host CPU and memory. |
| `schedule.log` | The driver's log (`workloads/pciebench/schedule.sh 1 5`, run from aifoundry2): five rounds 12 minutes apart, the card order rotated each round. |
| `pcie.json` | The reduction (`workloads/pciebench/reduce_pcie.py`), and the page's data: per card, every cell's mean over the runs with its 99% interval and the runs' own values; the predictions with their verdicts; the pooled 4 KB latency histograms. |
| `results.md` | The predictions against the results, as a table (the same reduction). |

## How it was run

The probe, `workloads/pciebench` (host program and empty kernel, runtime API only), was built on each host against
its own `/opt/et`, into a new build directory: `build/pciebench` in `~/claude/et-soc1-prototyping` on aifoundry2 and
in `~/nekko` on aifoundry3 and aifoundry1:

```
cmake -S workloads/pciebench -B build/pciebench -DCMAKE_PREFIX_PATH=/opt/et -Wno-dev && nice cmake --build build/pciebench -j4
```

One run on a card, `TREE=<tree> [V3_DEVICE=1] workloads/pciebench/run_pcie.sh <k>`, sources
`tools/claims-v3/lib.sh` (no other user or device process on the card, the telemetry helpers), takes the card's lock
(`flock -n /run/lock/etsoc-shire<N>.lock`) for the whole run, reads the die temperature and stops above 90 C, then
runs `info`, `bw --verify`, `lat`, `launch` and `conc`, one process each under `timeout 10` with `--budget 8.5`,
and `hostcopy` (no card). Each process stayed under 10 s (at most 2.1 s, `hosts.<card>.elapsed_s_max` in `pcie.json`),
but the lock was held for the whole run of six processes, 12.8–14.9 s (`run.json` `t1_ms` − `t0_ms`,
`hosts.<card>.run_times_ms`): longer than the lab's 10 s rule for holding a device, read here as applying to each
device-opening process. A later run can release the lock between the sub-tests. The schedule:

```
workloads/pciebench/schedule.sh 1 5          # from aifoundry2; aifoundry3 and aifoundry1 card 1 over ssh
```

Then, with the runs gathered into `raw/` (rsync of each host's `build/pcie-data/`):

```
python3 workloads/pciebench/reduce_pcie.py docs/reports/data/2026-09-27-pcie/raw \
    --prereg docs/reports/data/2026-09-27-pcie/PREREG.md \
    --out docs/reports/data/2026-09-27-pcie/pcie.json --md docs/reports/data/2026-09-27-pcie/results.md
python3 scripts/build-report.py pcie-link docs/reports/data/2026-09-27-pcie/pcie.json \
    docs/reports/2026-09-27-et-soc1-pcie-link.html
bash docs/reports/data/2026-09-24-report-review/tools/check_page.sh docs/reports/2026-09-27-et-soc1-pcie-link.html
```

## What each test measures

- **bw**: `memcpyHostToDevice` / `memcpyDeviceToHost` of 4 KB to 256 MB (x2 steps), each issued and waited for
  alone, both directions, *staged* (the runtime's default bounce copy) and *dma* (the API's `cmaCopyFunction`
  replaced by a no-op: the same DMA commands without the host copy; bytes not delivered). Repeats per size: 64 MB
  worth, at least 3 and at most 20, after one warm-up; the four variants shuffled in every repeat. `--verify` first
  sends 1 MB of random data there and back on the staged path and compares it.
- **lat**: an idle-stream `waitForStream`; 64 B and 4 KB round trips back to back (250 each variant, a fixed order);
  4 KB round trips after a random 0-1 ms spin (120 each variant, shuffled); 200 queued 4 KB copies, one wait (3 trials).
- **launch**: loading the empty kernel, the first launch, then per shire mask (32 shires, 1 shire) 150 launches
  each waited for and 3 batches of 100 queued launches (barrier on), twice.
- **conc**: 2 x 64 MB per stream, dma and staged, three trials: H2D alone, D2H alone, both on two streams, two H2D
  streams, two D2H streams (no barrier: both commands of a stream in flight), and `/ser` versions of the first three
  with the barrier on every copy (one command of a stream at a time).
- **hostcopy**: `memcpy` on the host over the same sizes: the ceiling of the staging copy.

The unit of replication is the run. A run's value for a cell is the median of its repeats (for `conc` the median of
its three trials); a card's value is the mean over its five runs with a 99% t-interval (t = 4.604).

## Hosts and what differs between them

All three links negotiated 16.0 GT/s x8 in every run (sysfs, recorded by `info` and `manifest.txt`); all three hosts
run the IOMMU in translated mode (`DMA-FQ`). The DMA limits are the same on all three: 128 MB per element, 8 elements
per command, a 2,057 MB bounce buffer. The hosts differ: aifoundry2 an i5-11600 (12 threads), aifoundry3 and
aifoundry1 an i7-11700K (16 threads); the runtime is the stock build on aifoundry2, a patched `-O3` build on
aifoundry3 and a fork on aifoundry1 (`docs/findings/14-card-behaviour.md`; `manifest.txt` has the hashes). The host's memcpy, measured by `hostcopy`,
sets the staged rate; the runtime build sets the per-command host overhead (the idle wait and the pipelined copies
differ by build).
