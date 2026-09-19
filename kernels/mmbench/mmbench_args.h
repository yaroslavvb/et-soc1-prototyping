// Kernel-argument layout shared by the mmbench device kernel (riscv64 gcc) and
// its host launcher (host g++).  Keep it plain fixed-width C types.
#pragma once
#include <stdint.h>

// Values are the TensorFMA "type" field (sw-sysemu insns/tensors.cpp).
#define MMBENCH_FP32 0u  // TensorFMA32:    C fp32  += A fp32  x B fp32,  K = 16 per op
#define MMBENCH_FP16 1u  // TensorFMA16A32: C fp32  += A fp16  x B fp16,  K = 32 per op
#define MMBENCH_INT8 3u  // TensorIMA8A32:  C int32 += A int8  x B int8,  K = 64 per op

#define MMBENCH_MAGIC 0x4D4D424Eu  // "MMBN"

// Every A and B tile is 16 cache lines of 64 B, in the layout tensor_load expects:
//  - A tile (16 x K): line i is row i, K elements packed from byte 0.
//  - B tile (K x 16): line p holds, for output column j = 0..15, the E consecutive
//    k-elements B[p*E + e][j] (e = 0..E-1) at bytes (j*E + e)*sizeof(elem), where
//    E = 4 / sizeof(elem) is 1 for fp32, 2 for fp16 and 4 for int8.
// One op multiplies one A tile by one B tile: 16 * 16 * K multiply-adds.
#define MMBENCH_TILE_BYTES 1024u

struct MmBenchArgs {
  uint64_t a_tiles;        // device address of the A tile pool
  uint64_t b_tiles;        // device address of the B tile pool (same count as A)
  uint64_t c_out;          // device address of one C tile (16x16 x 32-bit) per minion
  uint64_t stats_out;      // device address of one MmBenchStats per minion
  uint64_t iters;          // passes over the minion's tiles; ops per minion = iters * ntiles
  uint32_t ntiles;         // tile pairs each minion cycles through (>= 1)
  uint32_t private_pools;  // 0: all minions share tiles [0, ntiles), each starting at a
                           //    different tile; 1: minion m owns tiles [m*ntiles, (m+1)*ntiles)
  uint32_t mode;           // MMBENCH_FP32 / MMBENCH_FP16 / MMBENCH_INT8
  uint32_t num_minions;    // number of C tiles / stats slots, indexed by global minion id
};

// One cache line per minion, so minions never share an L1-written line.
struct MmBenchStats {
  uint64_t cycles;   // minion cycles (hpmcounter3) from the first load to the last FMA
  uint64_t ops;      // TensorFMA ops issued
  uint32_t hart_id;
  uint32_t magic;    // MMBENCH_MAGIC once written
  uint32_t pad[10];
};

#ifdef __cplusplus
static_assert(sizeof(MmBenchArgs) == 56, "MmBenchArgs layout must match on host and device");
static_assert(sizeof(MmBenchStats) == 64, "MmBenchStats must be one cache line");
#endif
