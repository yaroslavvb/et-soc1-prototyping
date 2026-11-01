# sp109: E109's copy of `workloads/sparsity`

`workloads/sparsity` (the binary E78's frame runs) with one change on each side, so a TensorFMA's shape and row mask can travel in the `--values` string that
`run_e78.py` passes, unchanged:

- **Kernel** (`kernel/sparsity.c`): `run_fma` reads the op's A rows and A columns (K, in 32-bit words) from `SpArgs.shape`, the slot that was `pad0`
  (bits 4:0 and 12:8; 0 means 16), once, before the timed loop; `fma_word` takes the A columns. With `shape` 0 the control word is the original's.
- **Host** (`host/main.cpp`): `--values` may begin `shape=<R>x<K>[m<hex>]:`: R A rows, K A columns, and an optional row mask (as `--row-mask`). The rest is
  the ordinary `--values`. Without the prefix nothing changes. Each launch record adds `arows` and `acols`.

Build, on a box with the toolchain: `cmake -S tools/claims-v3/e109/sp109 -B build/e109 -DCMAKE_PREFIX_PATH=/opt/et -Wno-dev && cmake --build build/e109 -j2`.
The registration is [`../E109.md`](../E109.md); the sys_emu check is [`../desk/sysemu-check.txt`](../desk/sysemu-check.txt). Tile files stay in
`tools/claims-v3/kinds/tiles` and `tools/claims-v3/kinds/e93/tiles`.
