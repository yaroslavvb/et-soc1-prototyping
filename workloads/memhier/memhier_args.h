// Kernel arguments shared by the memhier device kernel (riscv64 gcc) and host (g++).
// Plain fixed-width C types only.
#pragma once
#include <stdint.h>

#define MH_CHASE 1      // one hart follows a pointer chain: load-to-use latency
#define MH_STREAM_TL 2  // hart 0 of every minion streams 1 KB tensor loads: L2 / L3 / DRAM / L2-scratchpad bandwidth
#define MH_STREAM_L1 3  // both harts of every minion re-read a private 256 B buffer with 32 B vector loads: L1 bandwidth
#define MH_SPIN 4       // both harts run an integer loop that touches no memory: power of busy cores

#define MH_MAGIC 0x4D484945u  // "MHIE"
#define MH_MAX_HARTS 2048     // 32 compute shires x 64 harts
#define MH_SCP_LOCAL 0x7Fu    // scratchpad "shire" ID that means "my own shire" (PRM 15.3)

// Scratchpad region, Format 0 (PRM 15.3): 0x80000000 + (shire << 23) + offset. Each compute shire
// has 2.5 MB (et-common-libs system/layout.h); only the master shire's is used by the firmware.
#define MH_SCP_ADDR(shire, offset) (0x80000000ull + ((uint64_t)((shire) & 0x7F) << 23) + (uint64_t)(offset))
#define MH_SCP_BYTES_PER_SHIRE 0x280000ull

struct MhArgs {
  uint64_t mode;
  uint64_t shire_mask;  // shires the kernel was launched on
  uint64_t results;     // device address of MhResult[MH_MAX_HARTS], indexed by hart id

  // MH_CHASE: the hart `chaser_hart` walks p = *p from chain_base: warm_steps untimed, then steps timed.
  // If build_next != 0, the chain lives in a scratchpad and the chaser first writes it there:
  // line i at chain_base + 64*i points to line build_next[i] (uint32 indices in DRAM).
  uint64_t chaser_hart;
  uint64_t chain_base;
  uint64_t warm_steps;
  uint64_t steps;
  uint64_t build_next;
  uint64_t build_lines;

  // MH_STREAM_TL: participating minion m (0..n-1) reads bytes_per_minion (a multiple of 1 KB) starting
  // at stream_base + m * minion_stride, iters times. If scp_target is set, stream_base is an offset into
  // a scratchpad instead: the minion's own shire if scp_target == MH_SCP_LOCAL, otherwise the shire
  // (my shire + scp_target) % 32.
  uint64_t stream_base;
  uint64_t bytes_per_minion;
  uint64_t minion_stride;
  uint64_t scp_target;
  uint64_t iters;

  // MH_STREAM_L1: every hart reads l1_buffers + 256 * hart_index, 256 B, iters times.
  uint64_t l1_buffers;
};

// One cache line per hart.
struct MhResult {
  uint64_t cycles;  // minion cycles (hpmcounter3) of the timed part
  uint64_t value;   // chase: final pointer; spin: loop counter
  uint64_t bytes;   // bytes read in the timed part
  uint32_t hart;
  uint32_t magic;
  uint64_t pad[4];
};

#ifdef __cplusplus
static_assert(sizeof(MhArgs) == 15 * 8, "MhArgs layout must match on host and device");
static_assert(sizeof(MhResult) == 64, "MhResult must be one cache line");
#endif
