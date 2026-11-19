# rgm136: E136's copy of `tools/claims-v3/e107/rgm107`, with a large GEMM

`rgm107` is E107's kernel and host (E105's `rgm105`, E101's `rgm`: gp-sdk's generated `libautogen/matmul_f32_1024_512_512` ported op for op, one block of
C (64 × 32 tiles) = A (64 × 32) × B (32 × 32), its partition, cooperative loads and TensorStore). This copy adds one thing and changes nothing else:

- **`SP_GEMM_LARGE`**, a flag in `SpArgs.layout` (bit 9), and `run_gemm_large` in the kernel: C (MB × NB blocks) = A (MB × KB blocks) × B (KB × NB blocks),
  every block the vendor's 64 × 32 × 32 tiles with B packed by column (E105's `SP_LAYOUT_BYCOL`). Every minion keeps the vendor's partition in every C block
  (two row tiles, one column tile) and the vendor's order inside an op, and runs each C tile's whole K, KB × 32 ops, as one accumulation (the first op
  starts it, the last closes int8's) before its one TensorStore. It walks the C blocks mb outer, nb inner. MB, NB and KB ride in `SpArgs.src`,
  `src_bytes` and `ntiles`, which `SP_GEMM` does not otherwise read, so the struct keeps its 256 bytes.
- The host's arm **`gemmL<MB>x<NB>x<KB>`**: it allocates MB × KB A blocks, KB × NB B blocks and MB × NB C blocks, fills them with rgm105's generators or
  the named tile files (unchanged), and checks 64 sampled C tiles spread over the C blocks against its own reference summed over the whole K (exact, or
  within 1e-4 of the sum of the absolute products). `gemmL4x8x8` is 4,096 × 4,096 × 4,096 in fp32 (192 MB with C); `gemmL2x2x2` 2,048 × 1,024 × 1,024
  (20 MB).

Build, on a box with the toolchain: `cmake -S tools/claims-v3/e136/rgm136 -B build/e136 -DCMAKE_PREFIX_PATH=/opt/et -Wno-dev && cmake --build build/e136 -j2`.
The registration is [`../E136.md`](../E136.md).
