# rgm105: E105's copy of `tools/claims-v3/rgm`

`rgm` is E101's kernel and host, frozen with E101's record. This copy adds one thing: where `SP_GEMM`'s tiles live (`SpArgs.layout`, `SP_LAYOUT_*` in `sparsity_args.h`), and a `sparse25` generator. The partition, the op order, the cooperative loads and the tile contents are `rgm`'s; the host computes its reference on the packed pools and copies the bytes to each layout.

New arms in `--values <arm>:<gen>:<files>`: `gemmc<B>` B packed by column, `gemmv<B>` the vendor's strides (A and C at a pitch of 2,048 B, B at 2,112 B), `gemmh<B>` by column with 16 k tiles.

Build, on a box with the toolchain: `cmake -S tools/claims-v3/rgm105 -B build/e105 -DCMAKE_PREFIX_PATH=/opt/et -Wno-dev && cmake --build build/e105 -j2`. The registration is [`../kspeed/e105/E105.md`](../kspeed/e105/E105.md). Tile files stay in `tools/claims-v3/kinds/tiles`.
