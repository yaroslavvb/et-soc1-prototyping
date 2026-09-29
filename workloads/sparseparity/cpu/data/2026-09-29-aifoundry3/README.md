# CPU baselines for sparse parity, aifoundry3's host, 29 September 2026 (M0): the first run, superseded

**Superseded** by [`../2026-09-29-aifoundry3-r/`](../2026-09-29-aifoundry3-r/README.md), the run after the reviews
(R2): five repetitions per point, B1 with 8 instances per register, the meet in the middle with the random halving,
the CPU's own two-stage screens at every showcase size, and CPU energy stated as an assumption rather than a bound
(the package limits read 4,095 W). The files here are kept as the record of the first run; the "energy bound" in
`tables.md` is not a bound.

These were host CPU runs only. No card was opened, and `et-who` showed no holder before or after any run (each
run's `card_holder_after` field). The host is an i7-11700K, 8 cores and 16 threads with AVX-512 VPOPCNTQ
([`lscpu.txt`](lscpu.txt), [`manifest.txt`](manifest.txt)). Every run was niced to 19 and used at most 6 threads,
pinned as `OMP_PLACES={0},{1},…` with `OMP_PROC_BIND=close`. The `smt2` runs put 2 threads on core 0's two
hyperthreads (cpus 0 and 8).

| File | What |
|---|---|
| `bench.jsonl`, `bench.log`, `code.sha256` | The full ladder, 01:19–01:33 PDT, run as `nice -n 19 python3 workloads/sparseparity/tools/bench_cpu.py --bin ~/nekko/build/sparseparity-cpu --out <dir> --maxt 6 --spbits ~/nekko/build/sparseparity-cpu/spbits` (spbits is `proto/spbits.c`). It covers vexh at 1/2/4/6 threads and smt2, B1, the two-stage screens, the correctness runs, spbits, and the meet in the middle with its first, uncalibrated cost model (r = 17–20). One JSON object per run: the program's output plus `label`, `place`, `cpus`, `mhz_mean`, `process_s` and `card_holder_after`. |
| `mitm2/` | The meet in the middle again (`--only mitm`, 01:35–01:47), after its cost model was recalibrated from the first run's r sweep and its buckets narrowed. It holds 10 seeds at L1 and L2 and r sweeps 12–22 on both. `spbase` sha256 is `509ee96b…`; the vexh code is the same as in the first run's `29ce9a93…`. |
| `l2.ref.merge.json` | The reference run on the planner's 32 × 32-minion L2 work list, merged by `planner.py merge`: coverage complete, both checksums equal to the closed forms, the secret found, all 8,192 reported candidates rescored correctly. |
| `l5s.0.ref.merge.json` | The same for slice 0 of 64 of L5's two-stage stage 1 (m1 = 1,280, τ₁ = 144); partial by design. |
| `tables.md` | Generated: `python3 workloads/sparseparity/tools/table_cpu.py <this dir> <this dir>/mitm2`. |
| `sptest-aifoundry3.log`, `sptest-aifoundry2.log` | `tools/sptest.py --threads 2 --spbits …` with the final code on both hosts: 99 checks, all pass. |

The current table is in [`../../../README.md`](../../../README.md), "CPU baselines".
