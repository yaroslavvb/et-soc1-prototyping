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
// Fine-grained memory patterns: `access_bytes` per access, `stride` apart, wrapping every `region` bytes of
// the hart's slice, the slice in DRAM (scp 0), the shire's own scratchpad (1) or the scratchpad of the shire
// `targets[shire]` (2); with scp = 2 the target entry's bits 31:16 pick the region r (see EC_TSTORE_UNIQ). EC_TLOAD_PAT uses tensor loads (bypass the L1); EC_FLW_PAT 32 B vector loads
// through the L1, so a stride of 64 touches every line once and uses half of it.
#define EC_TLOAD_PAT 22
#define EC_FLW_PAT 23
// Tensor store of f0..f15 loaded straight from 512 B of sources (this hart's 256 B block and the next hart's),
// so the image stored is exactly the host's bytes. EC_TSTORE stores f0..f7 and their doubles, which is fine
// for "zeros / const / random" but not for controlled bit patterns on the wires.
#define EC_TSTORE_RAW 24
// Unique fill: every 512 B block of a minion's scratchpad region is loaded from its own 512 B of a big DRAM buffer
// (`sources` points at it: minion g, region r, block k at sources + ((g*2 + r)*slice_bytes) + k*512), and two
// regions are filled per minion (r = 0, 1), so the two readers of a target can read different bytes. With scp = 0
// it fills DRAM slices instead (slice + (g*2 + r)*slice_bytes), which the host can read back to check the image.
#define EC_TSTORE_UNIQ 25
// Generated instruction cases start at 100 (enercat_modes.h).

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
  uint64_t scp_off;     //   at this offset plus minion * slice_bytes; 2 = the scratchpad of targets[shire]
  uint64_t targets;     // uint32_t[32] in DRAM: the shire each shire reads from when scp == 2
  uint64_t minion_mask; // bit m: minion m of every shire takes part (0 means all 32)
  uint64_t stride;      // EC_TLOAD_PAT / EC_FLW_PAT: bytes between consecutive accesses
  uint64_t access_bytes;// EC_TLOAD_PAT: 64 (one line) or 1024 (16 lines) per tensor load
  uint64_t region;      // EC_TLOAD_PAT / EC_FLW_PAT: bytes per hart to wrap within
  uint64_t jump_every;  // EC_TLOAD_PAT: after this many accesses, add jump_bytes to the pointer (0: never).
  uint64_t jump_bytes;  //   With stride 1 KB, jump_every 8 and jump_bytes 248 KB, every DRAM bank sees a new
                        //   row on every visit; without the jump it sees 32 columns of one row.
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
static_assert(sizeof(EcArgs) == 17 * 8, "EcArgs layout must match on host and device");
static_assert(sizeof(EcResult) == 64, "EcResult must be one cache line");
#endif
