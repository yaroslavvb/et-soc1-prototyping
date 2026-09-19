// Kernel-argument layout shared by the device kernel (riscv64 gcc) and the host
// launcher (host g++).  Keep it plain fixed-width C types.
#pragma once
#include <stdint.h>

#define HELLO_MAGIC 0x48454C4Cu  // "HELL" (little-endian "LLEH")

// One record per hart, exactly one 64-byte cache line.  Minion L1 data caches
// are not coherent and write back whole lines, so two harts on different
// minions must never write into the same line (see docs/et-soc1-notes.md).
struct HelloRecord {
  uint32_t magic;        // HELLO_MAGIC once written
  uint32_t hart_id;      // csr hartid: shire*64 + minion*2 + thread
  int32_t rel_tid;       // get_relative_thread_id(): 0..num_threads-1
  uint32_t num_threads;  // get_num_threads()
  uint32_t shire_id;     // hart_id >> 6
  uint32_t minion_id;    // global minion index, hart_id >> 1
  uint32_t thread_id;    // hart within the minion, 0 or 1
  uint32_t pad[9];
};

struct HelloArgs {
  uint64_t num_records;  // capacity of `records`
  uint64_t records;      // device address of HelloRecord[num_records]
};

#ifdef __cplusplus
static_assert(sizeof(HelloRecord) == 64, "HelloRecord must be one cache line");
static_assert(sizeof(HelloArgs) == 16, "HelloArgs layout must match on host and device");
#endif
