// Kernel arguments shared by the onchip device kernel (riscv64 gcc) and host (g++).
// Plain fixed-width C types only.
#pragma once
#include <stdint.h>

// Does shire-to-shire communication beat main memory? Two probes and one experiment.
#define OC_WRITE 1   // every minion writes a known 1 KB pattern into its own shire's L2 scratchpad
#define OC_READ 2    // every minion reads the pattern another shire wrote, and checksums it
#define OC_RELAY 3   // K stages over a slab per shire: each stage reads the previous stage's output and
                     // writes its own. `medium` decides where the intermediate lives.

// Where the intermediate data of OC_RELAY lives between stages.
#define OC_MEM_DRAM 0  // the standard approach: write it to DRAM, read it back next stage
#define OC_MEM_SCP 1   // keep it in the shire's own L2 scratchpad; no data ever crosses a shire
#define OC_MEM_HOP 2   // hand it to the next shire: read the neighbour's scratchpad, write your own

// Two buffers, alternating by stage. A minion's chunk is far larger than the 512 B of L1 it gets, so by the
// time a stage reads a buffer again the lines it left behind two stages ago are long evicted; the run's
// checksum is checked against the analytic answer, which would fail if that were not so.
#define OC_BUFFERS 2

#define OC_MAGIC 0x4F4E4348u  // "ONCH"
#define OC_MAX_MINIONS 1024
#define OC_SCP_LOCAL 0x7Fu

// Scratchpad region, Format 0 (PRM 15.3): 0x80000000 + (shire << 23) + offset; 0x7F means the local shire.
// Each compute shire has 2.5 MB (et-common-libs system/layout.h).
#define OC_SCP_ADDR(shire, offset) (0x80000000ull + ((uint64_t)((shire) & 0x7F) << 23) + (uint64_t)(offset))
#define OC_SCP_BYTES 0x280000ull

// The probes write one 1 KB block per minion, 32 KB per shire, starting here.
#define OC_PROBE_OFF 0x100000ull
#define OC_PROBE_BLOCK 1024ull
// A value that depends on the shire, the minion and the position, so a wrong source is obvious.
#define OC_PAT(shire, minion, k) (0x5A000000u | ((uint32_t)(shire) << 19) | ((uint32_t)(minion) << 14) | (uint32_t)(k))

struct OcArgs {
  uint64_t mode;
  uint64_t shire_mask;
  uint64_t results;  // OcResult[OC_MAX_MINIONS], indexed by minion
  uint64_t shift;    // OC_READ: read the scratchpad of shire (mine + shift) % 32
  uint64_t method;   // OC_WRITE: 0 tensor_store from the vector registers, 1 plain vector stores

  // OC_RELAY
  uint64_t medium;        // OC_MEM_DRAM | OC_MEM_SCP | OC_MEM_HOP
  uint64_t dram_a;        // two DRAM slabs, stage_bytes per shire in each
  uint64_t dram_b;
  uint64_t scp_a;         // two scratchpad offsets, stage_bytes per shire in each
  uint64_t scp_b;
  uint64_t stage_bytes;   // bytes per shire per stage (split over the shire's 32 minions)
  uint64_t stages;        // how many stages to run
  uint64_t counter;       // DRAM line for the chip-wide barrier's global atomic (host zeroes it)
  uint64_t work;          // multiply-adds applied to each element per stage: the arithmetic-intensity knob
  uint64_t hop_dist;      // OC_MEM_HOP: how many shires round the ring a slab moves per stage
  uint64_t poll_limit;    // barrier give-up count, so a lost credit fails the run and not the card
};

// One cache line per minion.
struct OcResult {
  uint64_t cycles;
  uint64_t checksum;
  uint64_t bytes;
  uint32_t minion;
  uint32_t errors;
  uint32_t magic;
  uint32_t pad0;
  uint64_t pad[3];
};

#ifdef __cplusplus
static_assert(sizeof(OcArgs) == 16 * 8, "OcArgs layout must match on host and device");
static_assert(sizeof(OcResult) == 64, "OcResult must be one cache line");
#endif
