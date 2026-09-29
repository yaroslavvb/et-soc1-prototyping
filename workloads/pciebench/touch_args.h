// The first-touch probe (pciebench --test touch, hub rung 34): arguments shared by the device kernel
// (kernel/touch.c, riscv64 gcc) and the host (host/main.cpp, g++). Plain fixed-width C types only.
//
// The host writes a buffer B over PCIe, then launches the kernel WITHOUT the L3 flush; one hart (hart 0: shire 0,
// minion 0, thread 0) loads word 0 of m lines of B, one at a time, and times each load with hpmcounter3: the first
// touch of each line after the copy. It then times the same lines again (the second touch, an L2 hit), checks every
// first-touch value against the pattern the host wrote last (and the one before it, to count stale lines), and copies
// the timings out. The line order is i_k = (a_mul * k + b_off) mod n_lines, a permutation when a_mul is odd and n_lines a
// power of two: consecutive loads land in different DRAM rows, and the 32 L3 homes (PA[10:6]) and 8 memory shires
// (PA[8:6]) are visited evenly. B is allocated aligned to its own size, so line offsets are physical address bits.
#pragma once
#include <stdint.h>

#define TOUCH_MAGIC 0x544F5543u        // "TOUC"
#define TOUCH_MAX_LINES 8192u          // lines timed per launch (the scratchpad holds 2 x 32 KB of timings)

// The local shire's L2 scratchpad (PRM 15.3 format 0; shire 0x7F = my own shire). The timings are recorded here while
// the probe runs, so the probe itself sends nothing over the mesh. Offset 0 of a scratchpad faults (docs/findings/
// 14-card-behaviour.md, "Traps"): the timings start 256 KB in.
#define TOUCH_SCP_ADDR(offset) (0x80000000ull + (0x7Full << 23) + (uint64_t)(offset))
#define TOUCH_SCP_OFFSET 0x40000ull

struct TouchArgs {
  uint64_t magic;        // TOUCH_MAGIC, or the kernel returns at once
  uint64_t buf;          // device address of B, aligned to its size
  uint64_t n_lines;      // lines in B: a power of two
  uint64_t m;            // lines timed, <= TOUCH_MAX_LINES and <= n_lines (0: return at once, for a flush launch)
  uint64_t a_mul;        // odd: the line sequence's multiplier
  uint64_t b_off;        // the line sequence's start
  uint64_t seed_expect;  // the pattern the host wrote last (touch_pat)
  uint64_t seed_prev;    // the pattern written before it (0: none)
  uint64_t out;          // device address of a TouchStatus followed by 2 x m u32: first-touch, then second-touch cycles
  uint64_t hart;         // the hart that times (0)
  uint64_t nonce;        // echoed in TouchStatus, so the host never reads an earlier launch's results
};

// One cache line.
struct TouchStatus {
  uint64_t magic;        // TOUCH_MAGIC once the kernel has written its results
  uint64_t cycles;       // the timed part, both passes
  uint64_t ok;           // first-touch values equal to touch_pat(seed_expect, i)
  uint64_t stale;        // equal to touch_pat(seed_prev, i) instead: the old data
  uint64_t other;        // neither
  uint64_t first_bad;    // k of the first line that was not ok (~0: none)
  uint64_t sink;         // xor of the second-touch values, so no load is optimised away
  uint64_t nonce;        // TouchArgs.nonce
};

// The value of word w of line i under pattern seed (w = 0 is the word the kernel checks). splitmix64's finaliser.
static inline uint64_t touch_pat_word(uint64_t seed, uint64_t i, uint64_t w)
{
  uint64_t z = seed ^ (i * 0x9E3779B97F4A7C15ull) ^ (w * 0xD1B54A32D192ED03ull);
  z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9ull;
  z = (z ^ (z >> 27)) * 0x94D049BB133111EBull;
  return z ^ (z >> 31);
}
static inline uint64_t touch_pat(uint64_t seed, uint64_t i) { return touch_pat_word(seed, i, 0); }

// The k-th line of the sequence.
static inline uint64_t touch_line(uint64_t a_mul, uint64_t b_off, uint64_t n_lines, uint64_t k)
{
  return (a_mul * k + b_off) & (n_lines - 1);
}

#ifdef __cplusplus
static_assert(sizeof(TouchArgs) == 11 * 8, "TouchArgs layout must match on host and device");
static_assert(sizeof(TouchStatus) == 64, "TouchStatus must be one cache line");
#endif
