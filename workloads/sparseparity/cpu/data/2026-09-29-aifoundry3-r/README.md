# CPU baselines for sparse parity after the reviews, aifoundry3's host, 29 September 2026

These were host CPU runs only. No card was opened, and `et-who` showed no holder before or after any run (each
run's `card_holder_after` field). The host is an i7-11700K, 8 cores and 16 threads with AVX-512 VPOPCNTQ
([`lscpu.txt`](lscpu.txt), [`manifest.txt`](manifest.txt)). Every run was niced to 19 and used at most 6 threads,
pinned as `OMP_PLACES={0},{1},…` with `OMP_PROC_BIND=close`; the `smt2` runs put 2 threads on core 0's two
hyperthreads. It replaces [`../2026-09-29-aifoundry3/`](../2026-09-29-aifoundry3/README.md), the first run, after
review R2: five repetitions per timed point (median and range), B1 with 8 instances per register, the meet in the
middle with a random halving of the features and its full expected time, and the CPU's own two-stage screens at two
m1 for each showcase size.

| File | What |
|---|---|
| `bench.jsonl`, `bench.log`, `code.sha256` | The ladder, run as `nice -n 19 python3 workloads/sparseparity/tools/bench_cpu.py --bin build/sparseparity-f-cpu --out <dir> --maxt 6 --spbits build/sparseparity-cpu/spbits` in `~/nekko`, 03:52–04:07 PDT. One JSON object per run: the program's output plus `label`, `place`, `cpus`, `mhz_mean`, `process_s` and `card_holder_after`. |
| `powercap.txt` | The package power limits (`constraint_0/1_power_limit_uw` = 4,095,000,000 µW: PL1 = PL2 = 4,095 W, lifted), the energy counter's permissions (root only) and `perf_event_paranoid` (2): why CPU energy is an assumption here, not a measurement and not a bound. |
| `l2.ref.merge.json`, `l5s.0.ref.merge.json` | The reference run on the planner's 32 × 32-minion L2 work list, and on slice 0 of 64 of L5's two-stage stage 1, merged by `planner.py merge`. |
| `tables.md` | Generated: `python3 workloads/sparseparity/tools/table_cpu.py <this dir>`. |

The summary table and what it says are in [`../../README.md`](../../README.md), "CPU baselines".
