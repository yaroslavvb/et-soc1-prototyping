# rgm107: E107's copy of `tools/claims-v3/rgm105`

`rgm105` is E105's kernel and host (E101's `rgm` plus `SpArgs.layout`), frozen with E105's record. This copy adds two things to `SP_GEMM` and changes nothing else: the partition, the op order, the cooperative loads, the layouts, the tile contents and the host's check are `rgm105`'s.

- **`SpArgs.repeats`** (the slot that was `pad0`, so the struct keeps its 256 bytes): the passes over each block before the walk moves to the next. The same ops on the same addresses into the same C, so a block's first pass meets its tiles cold and the other `repeats - 1` meet them where the first left them. 0 or 1 is E101's and E105's loop.
- **`SP_GEMM_C_SHARED`**, a flag in `SpArgs.layout` (bit 8): every block stores its C into the first block's C, so C holds 2 MB of the L3 however many blocks the walk has. The host then allocates one C block and checks the last block's C there.

New arm names in `--values <arm>:<gen>:<files>`: any gemm arm may end in `r<R>` and then `s`, for example `gemmc16r4` (16 blocks, each 4 times), `gemmc8s` (8 blocks, C shared), `gemmc16r4s`. `gemmc16` is E105's cold walk, unchanged.

Build, on a box with the toolchain: `cmake -S tools/claims-v3/e107/rgm107 -B build/e107 -DCMAKE_PREFIX_PATH=/opt/et -Wno-dev && cmake --build build/e107 -j2`. The registration is [`../E107.md`](../E107.md). Tile files stay in `tools/claims-v3/kinds/tiles`.
