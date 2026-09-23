// Kernel arguments shared by the enercat device kernel (riscv64 gcc) and host (g++).
// Plain fixed-width C types only.
#pragma once
#include <stdint.h>

/* The energy catalogue: every hart runs one kind of operation flat out until a cycle deadline and reports
   how many it completed. The host measures board power meanwhile; energy per operation is what is left over
   idle, divided by the rate. Sources come from a small buffer the host fills, so the same pattern can run on
   zeros, on one constant, or on random data. */
#define EC_SPIN 1        // 8 independent addi: a core that is awake and doing the least it can
#define EC_IADD 2        // scalar add
#define EC_IMUL 3        // scalar mul
#define EC_IXOR 4        // scalar xor
#define EC_FADD_S 5      // scalar fadd.s
#define EC_FMUL_S 6      // scalar fmul.s
#define EC_FMADD_S 7     // scalar fmadd.s
#define EC_FADD_PS 8     // 8-lane fadd.ps
#define EC_FMUL_PS 9     // 8-lane fmul.ps
#define EC_FMADD_PS 10   // 8-lane fmadd.ps
#define EC_IADD_PI 11    // 8-lane integer fadd.pi
#define EC_IMUL_PI 12    // 8-lane integer fmul.pi
#define EC_FEXP_PS 13    // 8-lane transcendental fexp.ps
#define EC_FRCP_PS 14    // 8-lane reciprocal frcp.ps
#define EC_LD_L1 15      // flw.ps from a 256 B buffer that stays in the hart's L1
#define EC_ST_L1 16      // fsw.ps to the same
#define EC_ST_STREAM 17  // fsw.ps streaming over a per-hart slice of DRAM: the L1 write-back path
#define EC_TSTORE 18     // tensor store streaming over a per-hart slice (DRAM or scratchpad): bypasses L1 and L2
#define EC_TLOAD 19      // tensor load streaming over a per-hart slice (DRAM or scratchpad): bypasses L1
#define EC_FSQRT_PS 20   // 8-lane fsqrt.ps
#define EC_FDIV_PS 21    // 8-lane fdiv.ps

#define EC_MAGIC 0x454E4552u  // "ENER"
#define EC_MAX_HARTS 2048
#define EC_SCP_ADDR(shire, offset) (0x80000000ull + ((uint64_t)((shire) & 0x7F) << 23) + (uint64_t)(offset))
#define EC_SCP_LOCAL 0x7Fu

struct EcArgs {
  uint64_t mode;
  uint64_t shire_mask;
  uint64_t results;     // EcResult[EC_MAX_HARTS], indexed by hart
  uint64_t window;      // cycles each hart runs for
  uint64_t harts;       // 1: hart 0 of every minion; 2: both harts
  uint64_t sources;     // 256 B per hart of source operands (zeros, a constant, or random), in DRAM
  uint64_t slice;       // EC_ST_STREAM / EC_TSTORE / EC_TLOAD: per-hart slice base in DRAM
  uint64_t slice_bytes; // bytes per hart in that slice
  uint64_t scp;         // EC_TSTORE / EC_TLOAD: 1 = the slice is instead this shire's scratchpad, per-minion
  uint64_t scp_off;     //   at this offset plus minion * slice_bytes
};

// One cache line per hart.
struct EcResult {
  uint64_t cycles;   // cycles the timed loop actually took
  uint64_t iters;    // loop iterations completed; ops = iters * ops_per_iter (host knows the pattern)
  uint64_t bytes;    // bytes moved, for the memory patterns
  uint32_t hart;
  uint32_t magic;
  uint64_t pad[4];
};

#ifdef __cplusplus
static_assert(sizeof(EcArgs) == 10 * 8, "EcArgs layout must match on host and device");
static_assert(sizeof(EcResult) == 64, "EcResult must be one cache line");
#endif
