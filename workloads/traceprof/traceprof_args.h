// Kernel arguments shared by the traceprof device kernel (riscv64 gcc) and host (g++).
#pragma once
#include <stdint.h>

struct TpArgs {
  uint64_t shire_mask;  // shires the kernel was launched on
  uint64_t arena;       // DRAM scratch: 64 KB per participating minion
  uint64_t reps;        // repeats of each phase
};

#ifdef __cplusplus
static_assert(sizeof(TpArgs) == 3 * 8, "TpArgs layout must match on host and device");
#endif
