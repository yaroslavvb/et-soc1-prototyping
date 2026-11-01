# rgm: a matmul that streams, for E101 (Q132)

A copy of `workloads/sparsity` (kernel, host, args) with two new kernel modes and one new host path, so that the kinds of numbers can run in a real matmul. `workloads/sparsity` and `kernels/mmbench` are not edited. The registration, the design and what stays different from a production GEMM: [`../kinds/E101.md`](../kinds/E101.md).

- **`SP_STREAM`**: `kernels/mmbench`'s inner loop, op for op, in this kernel: A and B both loaded per op from a tile pool.
- **`SP_GEMM`**: the structure of gp-sdk's generated `libautogen/matmul_f32_1024_512_512` (`MatmulCmd_compute.cc`): its partition, its cooperative loads, its order of load, load, store, wait, FMA, a TensorStore per output tile, in any of the three types, with packed tiles and a loop inside the launch.
- **Host:** `--test fma --values <arm>:<gen>:<files>` (the grammar is at the top of the new block in `host/main.cpp`). A run's `iters` in its `SPARSITY` records is the ops per minion, and the last record, `"test":"check"`, is the host's comparison of C with its own reference. Every other test and `--values file:` run as in `workloads/sparsity`.
- **`tiles/*/e37.bin`**: E37's own ±1 / ±2 fill as kinds tiles (`make_e37_tiles.py`).
- **`sim-check.txt`**: the arms in the simulator.

Build on a box, no device node, from a tree holding this directory: `cmake -S tools/claims-v3/rgm -B build/e101 -DCMAKE_PREFIX_PATH=/opt/et -Wno-dev && cmake --build build/e101 -j2`.
