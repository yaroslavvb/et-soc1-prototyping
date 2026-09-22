// Kernel arguments shared by the nocbench device kernel (riscv64 gcc) and host (g++).
// Plain fixed-width C types only.
#pragma once
#include <stdint.h>

// Modes. Only hart 0 of a minion takes part: it is the only hart that may issue TensorSend/Recv.
#define NB_PINGPONG 1   // scheduled pairs: TensorSend then TensorRecv, and the partner the reverse (round trips)
#define NB_STREAM 2     // scheduled pairs: the initiator only sends, its partner only receives
#define NB_SHIFT 3      // every scheduled minion sends to `next` and receives from `prev` each step (rings)
#define NB_ALLREDUCE 4  // TensorReduce up the tree, then TensorBroadcast back down. levels <= 5: in every launched
                        // shire, its minions [0, 2^levels); levels > 5 (simulator only): minions [0, 2^levels)
#define NB_FCC 5        // scheduled pairs: credit ping-pong through the CREDINC ESRs and the FCC CSR
#define NB_FLAG 6       // scheduled pairs: flag ping-pong through global atomics in DRAM (the GPU way)
#define NB_BARRIER 7    // every scheduled minion runs `iters` barriers (per shire, or chip-wide)
#define NB_SPIN 8       // every scheduled minion runs an integer loop: power baseline
#define NB_HOTLINE 9    // every scheduled minion hammers ONE global atomic word, to measure who gets served.
                        // `hot_base` is a 2 KB-aligned DRAM region, so the line at offset s*64 is homed in
                        // shire s (PA[10:6]). `scope` picks the home: 0..31 that shire for everyone, 32 each
                        // minion's own shire (the uncontended baseline). `hot_window` non-zero runs every
                        // minion for that many cycles and records how many atomics each completed (the fair-
                        // share question); zero runs `iters` atomics each and records who finishes last.

// Scratchpad addressing (PRM 15.3, format 0): shire ID in bits [29:23], offset in [22:0]; 0x7F means self.
#define NB_SCP_ADDR(shire, offset) (0x80000000ull + ((uint64_t)((shire) & 0x7F) << 23) + (uint64_t)(offset))
#define NB_SCP_HOT_OFFSET 0x100000ull  // 1 MB into the scratchpad, clear of anything a kernel stages at its base
#define NB_STREAM_SPAN 0x400000ull  // 4 MB of DRAM walked by the host shire in modes 5 and 6
#define NB_SCP_SPAN 0x10000ull         // 64 KB walked by the owner's local loads: far past the 512 B of L1 per
                                       // hart, so every one of them reaches the shire cache

#define NB_MAGIC 0x4E4F4342u  // "NOCB"
#define NB_MINIONS 1024       // 32 compute shires x 32 minions; schedule rows are this wide
#define NB_IDLE 0xFFFFFFFFu   // schedule entry: not taking part in this round
#define NB_TIMEOUT 0xDEADC0DEu  // NbResult.value1 when a polled credit wait gave up

// Schedule entry (uint32, one per minion per round).
//   bits 12:0   partner minion (pairs), or `next` (NB_SHIFT)
//   bits 28:16  `prev` (NB_SHIFT)
//   bit 31      initiator: times the pair and sends first (pairs); sends before receiving (NB_SHIFT)
#define NB_ENTRY(partner, prev, first) \
  ((uint32_t)(partner) | ((uint32_t)(prev) << 16) | ((uint32_t)((first) ? 1u : 0u) << 31))
#define NB_PARTNER(e) ((e) & 0x1FFFu)
#define NB_PREV(e) (((e) >> 16) & 0x1FFFu)
#define NB_FIRST(e) ((e) >> 31)

// TensorRecv combine functions (PRM 9.4).
#define NB_FADD 0
#define NB_FMAX 2
#define NB_FMIN 3
#define NB_IADD 4
#define NB_IMAX 6
#define NB_IMIN 7
#define NB_MOVE 8

// NB_BARRIER scopes.
#define NB_SCOPE_SHIRE 0  // FLB + FCC inside each shire
#define NB_SCOPE_CHIP 1   // FLB in each shire, then one global atomic per shire, then FCC release

struct NbArgs {
  uint64_t mode;
  uint64_t shire_mask;  // shires the kernel was launched on
  uint64_t results;     // NbResult[]: minion m writes its k-th record (k-th round it takes part in) at slot_base[m] + k
  uint64_t slot_base;   // uint32_t[NB_MINIONS]
  uint64_t clocks;      // NbResult[NB_MINIONS]: t_entry / t_exit of every minion that took part
  uint64_t schedule;    // uint32_t[rounds][NB_MINIONS] (NB_ENTRY), in DRAM
  uint64_t rounds;
  uint64_t round_barrier;  // 1: chip-wide barrier between rounds, so only one round's pairs run at a time
  uint64_t part_masks;     // uint32_t[32]: minions of each shire that appear in any round (for barriers)
  uint64_t part_shires;    // number of shires with a nonzero part mask
  uint64_t counter;        // DRAM line for the chip-wide barrier's global atomic counter (host zeroes it)
  uint64_t flags;          // NB_FLAG: DRAM, one 64 B line per (round, minion) (host zeroes them)
  uint64_t iters;          // timed iterations (round trips, messages, steps, allreduces, barriers, spins)
  uint64_t warmup;         // untimed iterations first, which also line the partners up
  uint64_t count;          // vector registers per message, 1..127 (past f31 it wraps to f0)
  uint64_t funct;          // TensorRecv / TensorReduce combine function (NB_MOVE, NB_IADD, ...)
  uint64_t levels;         // NB_ALLREDUCE: tree levels (minions [0, 2^levels) take part), 1..10
  uint64_t scope;          // NB_BARRIER: NB_SCOPE_SHIRE or NB_SCOPE_CHIP
  uint64_t poll;           // 1: wait for credits by polling FCCNB and give up after poll_limit reads, instead of
  uint64_t poll_limit;     //    the blocking FCC CSR (a credit that never comes then fails the run, not the card)
  uint64_t hot_base;       // NB_HOTLINE: 2 KB-aligned DRAM region, 32 lines of 64 B (host zeroes it)
  uint64_t hot_window;     // NB_HOTLINE: cycles of the timed window; 0 means run `iters` atomics instead
  uint64_t hot_pace;       // NB_HOTLINE: cycles a remote waits between atomics (the errata's workaround)
  uint64_t hot_stream;     // NB_HOTLINE modes 5 and 6: DRAM buffer the host shire streams (host zeroes it)
  uint64_t hot_scp;        // NB_HOTLINE: 0 DRAM; 1 the home shire's L2 scratchpad, addressed by its explicit
                           //   shire ID by everyone; 2 the same word, but the home shire's own minions reach it
                           //   through the self ID 0x7F (a bus error for a global atomic: that path does not
                           //   take one); 3 the home shire's minions instead stream ordinary loads over their
                           //   own scratchpad through 0x7F while the rest hammer the atomic, which is the
                           //   neighbourhood-against-mesh pairing of Errata 4.1 (RTLMIN-6207); 4 the same
                           //   but the hammered word is a DRAM line homed in that shire instead, so the two
                           //   sides share the shire cache without sharing an address; 5 and 6 are 3 and 4
                           //   with the host shire streaming ordinary DRAM instead of its scratchpad, which
                           //   is what a shire that is computing actually does
};

// One 64 B line per record, so the non-coherent L1s never share a line.
struct NbResult {
  uint64_t cycles;   // hpmcounter3 cycles of the timed section
  uint64_t t_entry;  // hpmcounter3 at kernel entry and exit, for the clock estimate
  uint64_t t_exit;
  uint64_t iters;
  uint32_t value0;   // f0 lane 0 after the warm-up (NB_ALLREDUCE: after the checked allreduce;
                     //   NB_HOTLINE: the counter value this minion's FIRST timed atomic returned)
  uint32_t value1;   // f0 lane 0 at the end (NB_SHIFT: f16 lane 0); NB_TIMEOUT if a credit wait gave up;
                     //   NB_HOTLINE: the value its LAST timed atomic returned, i.e. its finishing position
  uint32_t partner;
  uint32_t minion;
  uint32_t round;
  uint32_t magic;
  uint32_t pad[2];
};

#ifdef __cplusplus
static_assert(sizeof(NbArgs) == 25 * 8, "NbArgs layout must match on host and device");
static_assert(sizeof(NbResult) == 64, "NbResult must be one cache line");
#endif

// f-register fill value of a minion, so the receiver can tell whose data arrived.
#define NB_PATTERN(minion) (0x5A000000u | ((uint32_t)(minion) << 4) | 0x9u)
