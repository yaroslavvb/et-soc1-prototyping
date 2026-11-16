// Kernel arguments shared by the regfile device kernel (riscv64 gcc) and host (g++). Plain fixed-width C types only.
//
// regfile: the integer register file's reads and writes. Every participating hart runs one loop form (a fixed
// stream of 128 32-bit integer instructions, no load, no store, no branch inside the body; make_images.py lists the
// forms) until a cycle deadline. Before the loop the hart loads the registers the form names from the kind's
// register image (32 x 64-bit values, by register number); after it, it stores them back so the host can check them.
#pragma once
#include <stdint.h>

#define RF_PER_ITER 128              // body instructions per loop iteration (plus 3: addi, csrr, bltu)
#define RF_MAGIC 0x52464c45u         // "RFLE"
#define RF_MAX_HARTS 2048

struct RfArgs {
  uint64_t form;          // loop form (RF_FORM_* in regfile_bodies.inc)
  uint64_t shire_mask;
  uint64_t minion_mask;   // bit m: minion m of every shire takes part (0 means all 32)
  uint64_t harts;         // 1: hart 0 of every minion (the default: one instruction stream per pipeline); 2: both
  uint64_t window;        // cycles each hart runs for
  uint64_t results;       // RfResult[RF_MAX_HARTS], indexed by hart
  uint64_t image;         // device address of the kind's register image: uint64_t[32]
};

// Six cache lines per hart.
struct RfResult {
  uint64_t cycles;        // cycles the timed loop took (hpmcounter3)
  uint64_t iters;         // loop iterations completed; body instructions = iters * RF_PER_ITER
  uint64_t ret0, ret1;    // hpmcounter4 (thread-0 instructions retired, neighbourhood sum) before and after the loop
  uint64_t icr0, icr1;    // hpmcounter7 (neighbourhood instruction-cache requests) before and after
  uint64_t icm0, icm1;    // hpmcounter8 (neighbourhood instruction-cache misses to L2) before and after
  uint64_t l1m0, l1m1;    // hpmcounter6 (L1 data misses to L2, neighbourhood sum) before and after
  uint64_t ra, gp;        // x1 and x3 during the loop (the loop's own instructions name them in a field)
  uint64_t deadline;      // the loop's deadline (cycle counter value)
  uint32_t hart;
  uint32_t magic;
  uint64_t pad[2];
  uint64_t regs[32];      // the form's named registers after the loop (others 0)
};

#ifdef __cplusplus
static_assert(sizeof(RfArgs) == 7 * 8, "RfArgs layout must match on host and device");
static_assert(sizeof(RfResult) == 384, "RfResult must be six cache lines");
#endif
