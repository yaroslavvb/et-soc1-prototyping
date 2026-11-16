// Kernel arguments shared by the x09mem device kernel (riscv64 gcc) and its host (g++).
// Plain fixed-width C types only, in the style of the public lab repo's workloads/enercat.
#pragma once
#include <stdint.h>

/* Memory traffic with designed data. Hart 0 of every participating minion streams 64 B lines to or from its own
   slice of DRAM, flat out or paced by the cycle counter, while the host's power logger runs:

     X9_RD      32 B vector loads through the L1 at a stride of 64: every load misses and brings one line from
                DRAM (the loop of the public catalogue's flw_pat pattern). The host fills the slices with the image.
     X9_WR      tensor stores of 16 rows x 32 B from f0..f15 (512 B = 8 lines) marching through the slice; the
                store bypasses the L1 and the L2 (the loop of the public catalogue's tstore_raw pattern). f0..f15
                hold the minion's own 512 B image for the whole launch.
     X9_RD_L1   the paced read loop with a stride of 0: every load hits the same L1 line (no memory traffic), the
                equal-issue control of a paced read.
     X9_WR_SCP  the paced write loop into the minion's own region of its shire's scratchpad (no DRAM traffic), the
                equal-issue control of a paced write that still stores.
     X9_WR_NST  the paced write loop with the tensor store replaced by a write of the floating-point flags (zero):
                the same instructions and slots, and nothing is stored anywhere (the control with no store).

   period == 0: flat out (8 accesses per loop iteration, the deadline checked once per iteration).
   period  > 0: one access per `period` cycles: the hart issues the access, then reads the cycle counter until the
                next slot opens. With `phase` set, hart 0 of minion m (0..1023 over the chip) starts its slot grid
                (m * period) / 1024 cycles after the launch's start, so the 1,024 harts' accesses are spread evenly over
                each period instead of all issuing at once. */
#define X9_RD 1
#define X9_WR 2
#define X9_RD_L1 3
#define X9_WR_SCP 4
#define X9_WR_NST 5

#define X9_MAGIC 0x58394D45u  // "X9ME"
#define X9_MAX_HARTS 2048
#define X9_MS_COUNT 8         // memory shires whose read and write counters the reporting hart samples
#define X9_SCP_ADDR(shire, offset) (0x80000000ull + ((uint64_t)((shire) & 0x7F) << 23) + (uint64_t)(offset))
#define X9_SCP_LOCAL 0x7Fu

struct X9Args {
  uint64_t mode;         // X9_RD, X9_WR, X9_RD_L1, X9_WR_SCP, X9_WR_NST
  uint64_t shire_mask;   // bit s: shire s takes part
  uint64_t minion_mask;  // bit m: minion m of every shire takes part (0 means all 32)
  uint64_t results;      // X9Result[X9_MAX_HARTS], indexed by hart
  uint64_t window;       // cycles each hart runs for
  uint64_t period;       // 0: flat out; else cycles between accesses
  uint64_t images;       // X9_WR, X9_WR_SCP, X9_WR_NST: 512 B per minion (minion index = hart / 2), into f0..f15
  uint64_t slice;        // X9_RD, X9_RD_L1, X9_WR: base of the per-hart DRAM slices
  uint64_t slice_bytes;  // bytes between consecutive harts' slices (indexed by hart id, as the catalogue does)
  uint64_t region;       // bytes each hart sweeps in its slice before wrapping
  uint64_t stride;       // X9_RD / X9_RD_L1: bytes between loads (64 or 0); writes always step 512
  uint64_t bank_spread;  // 1: offset each slice by ((hart / 2) % 8) KB, as the catalogue's flw_pat does
  uint64_t scp_off;      // X9_WR_SCP: offset of minion 0's region in the shire's scratchpad
  uint64_t scp_bytes;    // X9_WR_SCP: bytes per minion region in the scratchpad
  uint64_t ms_counters;  // 1: shire 0, minion 0, hart 0 samples the memory shires' read and write counters
  uint64_t phase;        // paced loops: 1 spreads the harts' slot grids over one period (see above), 0 starts all at t0
};

// One record per hart, two cache lines.
struct X9Result {
  uint64_t cycles;        // cycles the timed loop took
  uint64_t iters;         // loop iterations (flat out: 8 accesses each; paced: 1 access each)
  uint64_t accesses;      // loads or tensor stores issued
  uint64_t lines;         // 64 B lines moved (reads: one a load; writes: eight a store)
  uint64_t ret0, ret1;    // hpmcounter4 before and after the loop (thread-0 instructions, neighbourhood sum)
  uint64_t l1m0, l1m1;    // hpmcounter6 before and after (L1 miss requests, neighbourhood sum)
  uint64_t ms_rd;         // reporting hart only: the memory shires' read counters, summed, after minus before
  uint64_t ms_wr;         //   and their write counters
  uint64_t ms_cyc;        //   and memory shire 0's cycle counter, after minus before
  uint64_t ms_bad;        //   number of counter samples that returned a negative value (an error)
  uint64_t spins;         // paced loops: cycle-counter polls while waiting for a slot (the phase wait excluded)
  uint64_t late;          // paced loops: slots that opened before the previous access was issued
  uint32_t hart;
  uint32_t magic;
  uint64_t pad;           // 1 on the record that carries the memory shires' counters
};

#ifdef __cplusplus
static_assert(sizeof(X9Args) == 16 * 8, "X9Args layout must match on host and device");
static_assert(sizeof(X9Result) == 128, "X9Result must be two cache lines");
#endif
