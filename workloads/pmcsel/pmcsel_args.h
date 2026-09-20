// Kernel arguments shared by the pmcsel device kernel (riscv64 gcc) and host (g++).
#pragma once
#include <stdint.h>

// The counter-configure syscall added by patches/0003-pmc-configure-syscall-353f20e.patch.
#define PS_SYSCALL_PMC_CONFIGURE 12
#define PS_TARGET(kind, fields) (((uint64_t)(kind) << 56) | (uint64_t)(fields))
#define PS_MAGIC 0x50534C31u  // "PSL1"

struct PsArgs {
  uint64_t results;  // device address of one PsResult
  uint64_t event;    // minion PMU event to put on hpmcounter6 (2 = retired instructions of thread 0)
  uint64_t iters;
};

struct PsResult {
  int64_t rc_core;       // configure mhpmevent6: 0 with the patched firmware, -1 (invalid id) without
  int64_t rc_bad;        // mhpmevent3 is refused: -1
  int64_t rc_sc;         // shire-cache bank 0 P0 qualifier := its boot value (a harmless write): 0
  uint64_t c6_before, c6_after;  // hpmcounter6 around the loop
  uint64_t c4_before, c4_after;  // hpmcounter4 (retired instructions, thread 0) around the same loop
  uint32_t magic;
  uint32_t pad;
};
