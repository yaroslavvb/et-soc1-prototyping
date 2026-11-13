// Kernel arguments shared by the ledger programs' device kernel (riscv64 gcc) and host (g++).
// Plain fixed-width C types only. SPDX-License-Identifier: Apache-2.0
#pragma once
#include <stdint.h>

/* Three plain programs for the ledger's blind day (the November checkpoint's plan, step 3; Q166). Every
   participating hart works on its own data, whole cache lines only (the minions' L1 data caches are not coherent
   and write back whole lines), and writes one 64 B record:
     LG_COPY    copy `bytes` from src to dst, `reps` passes; `width` 32 = flw.ps/fsw.ps (32 B a move, eight
                moves of each per 256 B), 8 = ld/sd (eight of each per 64 B line)
     LG_SHA256  SHA-256 of one message of reps x bytes bytes: this participant's own `bytes`-byte block at src,
                repeated `reps` times (one message is a serial chain of compressions, so each hart hashes its own)
     LG_SORT    a bottom-up merge sort of this participant's `bytes` (a power of two) 32-bit keys, `reps` times:
                each time the input is copied from src into the work area, then sorted there (two buffers of
                `bytes` keys each, ping-pong); the merge's branch follows the data
   Participants are numbered over the shire mask, the minion mask and the harts per minion (entry_point() in
   kernel/ledger.c computes the number inline; the host's participant() is the same). */
#define LG_COPY 1
#define LG_SHA256 2
#define LG_SORT 3

#define LG_MAGIC 0x4C454447u  // "LEDG"
#define LG_MAX_HARTS 2048

struct LgArgs {
  uint64_t prog;         // LG_COPY / LG_SHA256 / LG_SORT
  uint64_t shire_mask;   // bit s: shire s takes part (shires 0-31)
  uint64_t minion_mask;  // bit m: minion m of every taking shire takes part (0: all 32)
  uint64_t harts;        // 1: hart 0 of every minion; 2: both harts
  uint64_t results;      // LgResult[LG_MAX_HARTS] in DRAM, by hart id
  uint64_t src;          // copy: source; sha256: the blocks, `bytes` per participant; sort: input keys, `bytes` per participant
  uint64_t dst;          // copy: destination; sort: work area, 2 x `bytes` keys per participant; sha256: unused
  uint64_t bytes;        // copy: bytes per participant (multiple of 256); sha256: block bytes (multiple of 64); sort: keys
  uint64_t reps;         // copy: passes; sha256: repeats of the block in the message; sort: sorts
  uint64_t width;        // copy: 32 (vector) or 8 (scalar)
};

// One cache line per hart.
struct LgResult {
  uint64_t cycles;     // hpmcounter3 over this hart's work; hart 0 of each minion only (erratum 1.23), 0 on hart 1
  uint64_t units;      // copy: bytes copied; sha256: compressions; sort: sorts completed
  uint32_t hart;       // get_hart_id()
  uint32_t magic;      // LG_MAGIC once the record is written
  uint32_t word[8];    // sha256: the digest's eight words H0..H7; sort: [0] out-of-order neighbours in the result,
                       // [1] xor of the result's keys, [2] their sum mod 2^32, [3] 1 if the result is in the second
                       // buffer; copy: unused
  uint64_t participant;
};

#ifdef __cplusplus
static_assert(sizeof(LgArgs) == 10 * 8, "LgArgs layout must match on host and device");
static_assert(sizeof(LgResult) == 64, "LgResult must be one cache line");
#endif
