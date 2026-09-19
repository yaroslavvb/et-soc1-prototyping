// Kernel arguments shared by the device kernel (riscv64 gcc) and the host (g++).
#pragma once
#include <stdint.h>

struct SgemmArgs {
  uint64_t a;           // device address of A[n][n], row-major fp32
  uint64_t b;           // device address of B[n][n]
  uint64_t c;           // device address of C[n][n] (output)
  uint64_t shire_mask;  // shires the kernel was launched on (to number the harts)
  uint32_t n;           // matrix size, multiple of 16
  uint32_t pad;
};
