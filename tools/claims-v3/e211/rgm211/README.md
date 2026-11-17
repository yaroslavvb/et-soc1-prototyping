# rgm211: E211's second kernel - a copy of `tools/claims-v3/e136/rgm136` with its C-block walk swapped

Made by `tools/claims-v3/e211/make_rgm211.py` from rgm136 as committed (rgm136 itself is never edited; `../rgm211.diff` is the whole difference). Two arms beside rgm136's `gemmL<MB>x<NB>x<KB>`: `gemmLn<MB>x<NB>x<KB>` walks the C blocks nb outer, mb inner (`SP_GEMM_NB_OUTER`, `run_gemm_large_nm`, which writes the walk tag `SP_WALK_TAG_NM` to every hart's `aux` after its timed section), and `gemmLnc<MB>x<NB>x<KB>` is gemmL with every minion loading for itself (coop 0, rgm136's own compiled branch; E211 runs it on rgm136's ELF). The host checks the walk tag on every large-GEMM launch (a gemmLn launch needs the tag on every hart, a gemmL or gemmLnc launch 0) and refuses a malformed arm, type, per-shire count, gen or tile file before it opens the device. Nothing else differs from rgm136. E211's registration (`../E211.md`) gives the build commands and the identities.

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
