// Kernel arguments shared by the intbits device kernel (riscv64 gcc) and host (g++).
// Plain fixed-width C types only.
//
// intbits: scalar integer bit-flip and carry ladders. Every participating hart runs one fixed stream of
// register-to-register integer instructions (no load, no store) until a cycle deadline. A "pair" stream
// alternates two instructions of the same opcode,
//     op x5, x6, x7      (A: sources a0, b0)
//     op x5, x28, x29    (B: sources a1, b1)
// so the bits that change between neighbouring instructions are set by the host's choice of a0, b0, a1, b1:
// on the two operand ports popcount(a0^a1) and popcount(b0^b1), on the result popcount(r0^r1).
#pragma once
#include <stdint.h>

// Stream forms (IbArgs.form)
#define IB_NOP 1        // 32-bit nop (addi x0, x0, 0), the no-op sled
#define IB_SAME 2       // one instruction repeated: op x5, x6, x7
#define IB_PAIR 3       // A, B alternating, both writing x5
#define IB_SPLIT 4      // A writes x5, B writes x30: each destination keeps one value

// Opcodes (IbArgs.op)
#define IB_ADD 0
#define IB_XOR 1
#define IB_SUB 2
#define IB_AND 3
#define IB_OR 4
#define IB_NOPS 5

#define IB_PER_ITER 256   // instructions in one loop body (128 A/B pairs), all 32-bit encodings
#define IB_MAGIC 0x49424954u  // "IBIT"
#define IB_MAX_HARTS 2048

struct IbArgs {
  uint64_t form;
  uint64_t op;
  uint64_t shire_mask;
  uint64_t minion_mask;  // bit m: minion m of every shire takes part (0 means all 32)
  uint64_t harts;        // 1: hart 0 of every minion (the default: one instruction stream per pipeline); 2: both
  uint64_t window;       // cycles each hart runs for
  uint64_t results;      // IbResult[IB_MAX_HARTS], indexed by hart
  uint64_t a0, b0, a1, b1;  // the four source values (the same on every hart)
};

// Two cache lines per hart.
struct IbResult {
  uint64_t cycles;       // cycles the timed loop took (hpmcounter3)
  uint64_t iters;        // loop iterations completed; instructions in the bodies = iters * IB_PER_ITER
  uint64_t ret0, ret1;   // hpmcounter4 (thread-0 instructions retired, neighbourhood sum) before and after the loop
  uint64_t icr0, icr1;   // hpmcounter7 (neighbourhood instruction-cache requests) before and after
  uint64_t icm0, icm1;   // hpmcounter8 (neighbourhood instruction-cache misses to L2) before and after
  uint64_t l1m0, l1m1;   // hpmcounter6 (L1 data misses to L2, neighbourhood sum) before and after
  uint64_t res_x5;       // x5 after one A,B pair run once more after the loop (the check)
  uint64_t res_x30;      // x30 after the same (form IB_SPLIT only)
  uint32_t hart;
  uint32_t magic;
  uint64_t pad[3];
};

#ifdef __cplusplus
static_assert(sizeof(IbArgs) == 11 * 8, "IbArgs layout must match on host and device");
static_assert(sizeof(IbResult) == 128, "IbResult must be two cache lines");
#endif
