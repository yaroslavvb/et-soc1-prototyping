# pciebench: the host link and the launch path

A standalone host program and two device kernels (et-testdrive style, runtime API only) that time what a program
gets over the ET-SoC-1's PCIe link: copy bandwidth from 4 KB to 256 MB in both directions, staged (the runtime's
bounce copy, the normal path) and DMA-only (the API's `cmaCopyFunction` replaced by a no-op: the same DMA without the
host copy), small-copy latency, empty-kernel launch latency, several transfers at once, and (since 28 September) the
first touch of each line after a host copy. Every result is a line `PCIE {json}`; each process stops starting new
work at `--budget` seconds (8.5 by default, at most 9.5).

```
cmake -S workloads/pciebench -B build/pciebench -DCMAKE_PREFIX_PATH=/opt/et -Wno-dev && nice cmake --build build/pciebench -j4
timeout 10 build/pciebench/host/pciebench_host --test info|bw|lat|launch|conc|touch|hostcopy [--budget 8.5] [--verify]
TREE=$PWD workloads/pciebench/run_pcie.sh <run>     # one run of every test (V3_DEVICE=1 on aifoundry1; V3_DRY=1: no device)
CARDS="aifoundry3 aifoundry1-c1" workloads/pciebench/schedule.sh 1 5    # runs on several cards, rounds 12 min apart
python3 workloads/pciebench/reduce_pcie.py <raw> --prereg <PREREG.md> --out pcie.json --md results.md
```

## The tests' options (hub rungs 34 and 35, 28 September)

- `--test conc`: with no option, the 27 September test (2 x 64 MB per stream, eight configurations, staged and
  DMA-only, three trials). `--mb N` sets the MB per command (1-128); `--elements E` sends each command as a list of E
  equal DMA elements (`memcpyHostToDevice`/`DeviceToHost` with a `MemcpyList`; 0, the default, is the plain call,
  which the runtime sends as one element up to 128 MB); `--copy dma|staged|both`; `--trials T`; `--cfgs a,b,...` runs
  only those configurations, in that order: the default eight and `2xh2d/ser`, `2xd2h/ser` (two streams, one command
  of each in flight); `--shuffle` draws a new configuration order each trial. Each line also carries `mb`,
  `cmds_per_leg` and `elements`.
- `--test touch`: the kernel `kernel/touch.c` (arguments and protocol in `touch_args.h`) times, on one hart, the
  first load of each of `--lines` lines (4,096) of a `--touch-mb` MB buffer (4) that the host has just written, in a
  launch without the L3 flush, and then the same lines again (an L2 hit); `--reps` (5) repetitions of seven launches
  on all 32 shires: a flush launch that times nothing, `dram_ref`, `l3_ref`, `h2d_warm` (after a write over lines the
  L3 holds), a flush launch, `h2d_cold` (after a write with the L3 empty), `l3_ref2`. No timed launch carries the
  flush: the firmware evicts each L3 slice after the pre-launch sync with no barrier after it, so a flushed timed
  launch could start while other slices were still evicting. Each arm's line gives the first- and second-touch cycles
  (`dt1`, `dt2`), `after_flush`, and how many first-touch values equal the last pattern written (`ok`), the one before
  it (`stale`) or neither (`other`). The kernel writes its timing slots in the scratchpad once before the clock starts.
- A conc trial that does not finish in 5 s aborts every stream the process uses, waits for the aborts, and only then
  reports the error, so no device buffer is freed under a transfer in flight.
- The `open` line carries `src`: the sha256 of `main.cpp`, `touch_args.h` and `kernel/touch.c` the binary was built
  from (CMake writes them into `Constants.h` at configure time and re-runs the configure when one changes).
  `tools/claims-v3/pcie2/block.sh` compares them with its tree before every pass.
- The experiment that uses both, with its predictions, is `tools/claims-v3/pcie2/` (its README).

## run_pcie.sh and schedule.sh

`run_pcie.sh` takes the card's lock for each device-opening process and releases it between them (since 28 September;
the runs of 27 September held it for the whole run, 12.8–14.9 s, longer than AGENT.md §5's 10 s). It takes the lock
with `flock -n` and never waits for it: if anyone holds it, or another user or device process appears (lib's
`others_present` and `ours_running`, and `et-who --check`, before every process), the run stops with exit 3 and moves
its partial output aside, so that a retry starts clean. The card's own samples before and after take the lock the same
way, with three tries each (ettelem fails to start about one time in three); a run with no reading in three tries
stops (exit 3), and a die at 90 °C or more stops it (exit 4). `V3_DRY=1` prints each device process instead of running
it, takes a lock file beside the output instead of the card's, and reads `PCIE_DRY_TEMP` (80) °C, with the first
`PCIE_DRY_NOTEL` samples empty. Start it detached over ssh (`setsid nohup … < /dev/null &`).

Fixed on 28 September, before its first run on a card since the lock change (dry-tested only): every telemetry sample
runs under `timeout 10` (it had 20); the run never reads card 0 (a sample with `ET_DEVICES=0` opened card 0's
management node against the owner's rule; the path is gone, and `run.json` says `"card0_read":false`); it refuses
aifoundry1's card 0 and, until the DV2 validation ends, aifoundry2 (`PCIE_ALLOW_AIFOUNDRY2=1`); on aifoundry1 it
refuses a probe or ettelem built without `ET_DEVICES` support (that name must be in the binary); a sample with no die
reading no longer counts as 0 °C; the gate stops at 90 °C, not above it; it no longer waits up to 20 s for a held lock
(`run.json` keeps `"lock_waits":0` for `reduce_pcie.py`); `PCIE_BIN` can name another probe. `schedule.sh` takes its
cards from `CARDS` (it used to fix the three and assume it ran on aifoundry2), runs a card on the local host locally
and the others over ssh, refuses aifoundry1's card 0 and, until the DV2 validation ends, aifoundry2, and gives each
run 300 s (a run's worst case is now under 3 minutes; the header of `run_pcie.sh` has the sum).

Files: `host/main.cpp` (the tests; its header explains staged and DMA-only), `kernel/empty.c` (the launch kernel),
`kernel/touch.c` and `touch_args.h` (the first-touch probe), `run_pcie.sh`, `schedule.sh`, `reduce_pcie.py`. The data,
the predictions and the page of 27 September: `docs/reports/data/2026-09-27-pcie/` and
`docs/reports/2026-09-27-et-soc1-pcie-link.html`.
