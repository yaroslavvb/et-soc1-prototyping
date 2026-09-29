// Kernel arguments shared by the memprobe device kernel (riscv64 gcc) and host (g++).
// Plain fixed-width C types only.
#pragma once
#include <stdint.h>

#define MP_PROGRAM 1  // one hart runs an op list (below) and records one u32 per timed op
#define MP_LOOP 2     // hart 0 of every minion in shire_mask loops: load + evict over its own few addresses (power)
#define MP_LOOP_MAX_ADDRS 16

// Ops for MP_PROGRAM. Each op is two u64 words: {code | arg << 8, addr}.
#define OP_END 0
#define OP_LOAD 1     // load addr and wait for the data (untimed)
#define OP_TLOAD 2    // same, timed: records the cycles from issue to data
#define OP_EVICT 3    // evict_va(addr) to level arg (0 L1, 1 L2, 2 L3, 3 memory)
#define OP_TEVICT 4   // same plus a fence, timed
#define OP_FENCE 5
#define OP_DELAY 6    // spin until arg cycles have passed
#define OP_STAMP 7    // records the low 32 bits of the cycle counter
#define OP_STORE 8    // store 64 bits to addr (makes the line dirty)
#define OP_TFENCE 9   // timed fence
#define OP_TNOP 10    // timed nothing: the overhead to subtract from OP_TLOAD
#define OP_MSREAD 13  // records a memory shire counter (syscall 10): arg = ms | pmc << 8, pmc 0 cycles, 1 reads, 2 writes
#define OP_TLOAD2 12  // load addr, then at once a timed load of the next op's addr: the time until the second arrives
#define OP_RAW 11     // four results: two raw back-to-back hpmcounter3 reads, then two `cycle` reads if arg == 1

#ifdef MP_EXT
// Extension (build with -DMEMPROBE_EXT=ON, e.g. into build/memprobe2; tools/claims-v3/memp2). Without MP_EXT the
// header, kernel and host compile exactly as before, so a default build of build/memprobe is unchanged.
#define MP_TLOOP 3    // hart 0 of every minion in minion_mask (per shire) of shire_mask streams TensorLoads (bandwidth)
#define OP_TTLOAD 14  // timed TensorLoad into L1 scratchpad lines 0..: arg bits 3:0 = lines - 1, bits 55:8 = stride
                      // in bytes (0 = 64); records the cycles from issue to TensorWait's return (hart 0 of a minion only)
#define OP_TERR 15    // records the tensor_error CSR (0x808): nonzero after a faulted tensor op (it may still hold an
                      // earlier kernel's bits: record it before the first tensor op too, count only bits added after)
#endif

#define MP_MAGIC 0x4D50524Fu  // "MPRO"
#define MP_MAX_HARTS 2048

// Local L2 scratchpad (PRM 15.3 Format 0; shire 0x7F = my own shire). The op list is copied here
// before the timed part, and results are recorded here, so the probe itself never touches DRAM.
#define MP_SCP_ADDR(shire, offset) (0x80000000ull + ((uint64_t)((shire) & 0x7F) << 23) + (uint64_t)(offset))
#define MP_SCP_OPS_OFFSET 0x0ull
#define MP_SCP_OPS_BYTES 0x180000ull  // 1.5 MB: 98,304 ops
#define MP_SCP_RES_OFFSET 0x180000ull
#define MP_SCP_RES_BYTES 0x100000ull  // 1 MB: 262,144 results
#define MP_MAX_OPS (MP_SCP_OPS_BYTES / 16)
#define MP_MAX_RESULTS (MP_SCP_RES_BYTES / 4)

struct MpArgs {
  uint64_t mode;
  uint64_t shire_mask;  // shires the kernel was launched on
  uint64_t status;      // device address of MpStatus[MP_MAX_HARTS]

  // MP_PROGRAM
  uint64_t hart;     // the hart that runs the program
  uint64_t ops;      // DRAM address of the op list (n_ops x 16 B)
  uint64_t n_ops;
  uint64_t results;  // DRAM address for the u32 results

  // MP_LOOP: minion m (0..n-1 over shire_mask) loops `iters` times over its n_addrs addresses
  // table[m * n_addrs + j]: load (wait for the data), then evict the line to `level`.
  uint64_t table;    // DRAM address of n_minions x n_addrs u64 addresses
  uint64_t n_addrs;  // 1..MP_LOOP_MAX_ADDRS
  uint64_t level;    // evict level after each load; 4 = no evict (L1 hits)
  uint64_t iters;
  // Strided mode, if stride != 0: minion m cycles through table[m * n_addrs] + j * stride, j < n_lines.
  // A cyclic walk over more lines than a cache holds misses it every time (LRU), with no evicts.
  uint64_t stride;
  uint64_t n_lines;
#ifdef MP_EXT
  // MP_TLOOP: minion m (hart 0, minion bit set in minion_mask) streams `iters` TensorLoads of tl_lines lines,
  // `stride` bytes apart inside each load, starting at table[m] (an absolute address, one per minion of every shire
  // in shire_mask), the next load tl_step bytes further on, wrapping every tl_span bytes. Two loads in flight.
  uint64_t minion_mask;  // minions (0..31) of each shire that stream
  uint64_t tl_lines;     // 1..16
  uint64_t tl_step;
  uint64_t tl_span;
  uint64_t tl_flags;     // MP_TL_WARM: scalar-load every line of the span before the timed part (the arena source)
  // The status line's sink carries tensor_error: (its value before the first tensor op << 32) | its value at the end;
  // an error is a bit set at the end that was not set before (an earlier kernel may have left the CSR set).
#endif
};
#ifdef MP_EXT
#define MP_TL_WARM 1ull
#endif

// One cache line per hart.
struct MpStatus {
  uint64_t cycles;   // minion cycles of the timed part
  uint64_t count;    // results recorded (PROGRAM) or loads done (LOOP)
  uint64_t sink;     // xor of loaded values, so the loads cannot be optimized away
  uint32_t hart;
  uint32_t magic;
  uint64_t pad[4];
};

#ifdef __cplusplus
#ifdef MP_EXT
static_assert(sizeof(MpArgs) == 18 * 8, "MpArgs layout must match on host and device");
#else
static_assert(sizeof(MpArgs) == 13 * 8, "MpArgs layout must match on host and device");
#endif
static_assert(sizeof(MpStatus) == 64, "MpStatus must be one cache line");
#endif
