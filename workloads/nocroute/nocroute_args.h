// Kernel arguments shared by the nocroute device kernel (riscv64 gcc) and host (g++). Plain fixed-width C types only.
// EXPERIMENT nocr (tools/claims-v3/nocr/README.md): hub rung 31 (mesh stops, by timing counter reads) and rung 32
// (the mesh's routing order, by link contention).
#pragma once
#include <stdint.h>

#define NR_MESH 1   // R31: hart 0 of minion 0 of each caller shire runs the call list in its own time slot
#define NR_FILL 2   // every minion (hart 0) of every shire in the mask tensor-stores the pattern over its read slice
#define NR_READ 3   // R32: hart 0 of every minion of each reader shire streams 1 KB tensor loads from map[shire]'s scratchpad
#define NR_WRITE 4  // R32w: hart 0 of every minion of each writer shire streams 512 B tensor stores into map[shire]'s scratchpad

// R31 call-list entry (one u64): kind | id << 8 | a << 16 | b << 24. id NR_SELF means the caller's own shire.
#define NR_CALL_SC 1   // syscall(SYSCALL_PMC_SC_SAMPLE, shire id 0..32, bank a 0..3, pmc b in {0, 3, 7})
#define NR_CALL_MS 2   // syscall(SYSCALL_PMC_MS_SAMPLE, memory shire id 0..7, pmc a in {0, 7}, 0)
#define NR_CALL_NOP 3  // timed nothing: the two counter reads' own cost
#define NR_SELF 0xFF
#define NR_BAD 0xFFFFFFFFu  // recorded instead of a time for an entry the kernel refused (it never makes that call)
// What each call touches: the COMPILED firmware, not pmu.c's C text. The ESR pointers in pmu.h are not volatile, so
// the compiler merges the stop's and the start's read-modify-writes. objdump of sample_sc_pmcs / sample_ms_pmcs in
// MachineMinion.elf (identical code in all three lab hosts' /opt/et copies and in build/fw-build):
//   SC pmc 0: ld ctl; sd ctl (stop); ld cycle counter; sd ctl (start): 2 loads and 2 stores to the ESRs of the
//             target shire's cache bank;
//   SC pmc 3 (PMU_SC_ALL): ld ctl; sd ctl|0x20011: 1 load and 1 store (the stop is merged away), returns -1;
//   SC pmc 7: matches no case, so no ESR access at all: the syscall's own cost (the null call), returns -1;
//   MS pmc 0: the same 2 loads and 2 stores to the memory shire's DDRC ESRs; MS pmc 7: no access (null).
// So pmc 0 - pmc 3 and pmc 3 - null are each one load plus one store. The cards run flashed minion firmware 0.22.0
// and 0.23.0, built from the same pmu.c / pmu.h (et-common-libs 0.22.0 and 0.23.0 equal HEAD but for the licence
// header) with an unknown compiler; reduce.py checks that the two differences agree before using either.
// The kernel refuses shire 33 (the spare), shire ids above 32, banks above 3, memory shires above 7 and any other pmc.

#define NR_MAX_CALLS 8192   // and n_calls must be a multiple of 8: each caller's results fill whole 64 B lines
#define NR_NONE 0xFFFFu    // map entry: this shire takes no part
#define NR_SCP_SIZE 0x280000ull                  // 2.5 MB scratchpad per shire
#define NR_READ_OFF (256ull * 1024)              // R32 read region: minion m's slice at +m * slice_bytes (offset 0 faults)
#define NR_SLICE_MAX (32ull * 1024)
#define NR_WRITE_OFF (NR_READ_OFF + 32 * NR_SLICE_MAX)  // R32w write region, above the read region (1.25 MB)
#define NR_MESH_CALLS (NR_WRITE_OFF + 32 * NR_SLICE_MAX)  // R31, local: the call list (64 KB), at 2.25 MB
#define NR_MESH_RES (NR_MESH_CALLS + 8 * NR_MAX_CALLS)   // R31, local: the results (64 KB), ends at 2.375 MB

#define NR_MAGIC 0x4E4F4352u  // "NOCR"
#define NR_MAX_HARTS 2048

// Format 0 scratchpad address (PRM 15.3); shire 0x7F is the local shire.
#define NR_SCP_ADDR(shire, offset) (0x80000000ull + ((uint64_t)((shire) & 0x7F) << 23) + (uint64_t)(offset))

struct NrArgs {
  uint64_t mode;
  uint64_t shire_mask;   // shires the kernel was launched on
  uint64_t status;       // NrResult[NR_MAX_HARTS] in DRAM, indexed by hart
  uint64_t window;       // READ/WRITE: cycles each hart streams for; MESH: cycles per caller slot
  uint64_t map;          // READ/WRITE: uint32_t[32] in DRAM, the partner shire of each shire (NR_NONE: none)
  uint64_t pattern;      // FILL/WRITE: 512 B in DRAM loaded into f0..f15 (the bytes every tensor store writes)
  uint64_t slice_bytes;  // READ/WRITE/FILL: bytes per minion (a multiple of 1 KB, at most NR_SLICE_MAX)
  uint64_t calls;        // MESH: u64[n_calls] in DRAM
  uint64_t n_calls;      // MESH: at most NR_MAX_CALLS
  uint64_t out;          // MESH: u32[32][n_calls][2] in DRAM, 64 B-aligned: per caller slot, per call {cycles, low 32 bits of a0}
  uint64_t gap;          // MESH: idle cycles after each call, outside the timed part
  uint64_t lead;         // MESH: cycles from kernel entry to slot 0 (every caller copies its list meanwhile)
  uint64_t caller_mask;  // MESH: the shires that call (a subset of shire_mask); slot = rank of the shire in it
  uint64_t minion_mask;  // READ/WRITE/FILL: minions that take part (0 = all 32)
};

// One cache line per hart.
struct NrResult {
  uint64_t cycles;   // READ/WRITE/FILL: cycles of the timed loop; MESH: cycles of the caller's program
  uint64_t bytes;    // READ/WRITE/FILL: bytes moved; MESH: calls made
  uint64_t iters;    // READ/WRITE: loop iterations; MESH: entries refused
  uint64_t t_begin;  // MESH: cycles from kernel entry to the first call (the slot start)
  uint64_t partner;  // READ/WRITE: the shire it streamed from or to; MESH: the slot
  uint64_t err;      // nonzero: the kernel refused this hart's work (1 bad partner, 2 bad slice, 3 slot overrun,
                     // 4 MESH n_calls not a multiple of 8 in 8..NR_MAX_CALLS, or out not 64 B-aligned)
  uint32_t hart;
  uint32_t magic;
  uint64_t pad;
};

#ifdef __cplusplus
static_assert(sizeof(NrArgs) == 14 * 8, "NrArgs layout must match on host and device");
static_assert(sizeof(NrResult) == 64, "NrResult must be one cache line");
#endif
