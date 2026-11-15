// Kernel arguments shared by the x04clock device kernel (riscv64 gcc) and host (g++).
// Plain fixed-width C types only.
//
// x04clock: what an awake core costs per cycle, against a core that waits.
// Every arm runs on the worker minions (minion_mask, minions 1..31) of every launched shire. Minion 0, thread 0 of
// every launched shire is the shire's timekeeper in EVERY arm: it watches the cycle counter for the launch's window
// and, in the arms that wait, hands each waiting thread one fast credit (PRM ch. 11, CREDINC store) per period.
// A thread that returns from the kernel waits in the firmware's own post-launch credit barrier until the shire's
// last thread returns; shires left out of the launch stay in the firmware's idle park.
#pragma once
#include <stdint.h>

// What thread 0 of each worker does (args.arm):
#define X04_TK 0     // nothing: return at once (the hart then waits in the firmware's post-launch barrier)
#define X04_SPIN 1   // no-op sled: 512 `nop` per loop, cycle counter read between loops
#define X04_WAIT 2   // blocking credit wait (csrw fcc) for one credit per period, nothing else: duty 0
#define X04_DUTY 3   // per period: wait for the credit, then run the 64-slot no-op sled for duty_cycles
                     // (duty_cycles >= period: no credits, no waits: the same loop awake all the time)
#define X04_STALL 4  // a dependent chain of 64-bit `div` on zero operands
#define X04_MIX 5    // the no-op sled with one instruction of class `cls` in every `every` slots

// Instruction classes for X04_MIX (args.cls); sources f0..f7 hold zeros, results go to f8..f15, never read.
#define X04_CLS_FSGNJ_S 1   // fsgnj.s   scalar float sign-inject
#define X04_CLS_FADD_S 2    // fadd.s    scalar float add
#define X04_CLS_FADD_PS 3   // fadd.ps   8-lane float add
#define X04_CLS_FSGNJ_PS 4  // fsgnj.ps  8-lane float sign-inject
#define X04_CLS_COUNT 4

// What thread 1 of each worker does (args.t1):
#define X04_T1_OFF 0    // returns at once
#define X04_T1_SAME 1   // the same arm as thread 0
#define X04_T1_WAIT 2   // blocking credit wait, one credit per period

#define X04_MAGIC 0x58303443u  // "X04C"
#define X04_MAX_HARTS 2048
#define X04_SYNC_PER_SHIRE 1024  // bytes of the sync buffer per shire (see below)

// Result flags (X04Result.flags)
#define X04_F_LATE 1ull          // a waiting thread found the start already given: it skipped its waits (safe)
#define X04_F_HS_BAILOUT 2ull    // the timekeeper started without every waiting thread's report
#define X04_F_CTR_UNSYNCED 4ull  // a counter reader read without its own thread 1's done flag

struct X04Args {
  uint64_t arm;           // X04_TK .. X04_MIX
  uint64_t cls;           // X04_MIX: instruction class
  uint64_t every;         // X04_MIX: one class instruction every `every` slots (1, 2, 4, 8, 16, 32 or 64)
  uint64_t mask;          // m0 for the vector classes (0xff: all eight lanes)
  uint64_t t1;            // X04_T1_OFF / SAME / WAIT
  uint64_t shire_mask;    // shires that take part
  uint64_t minion_mask;   // worker minions of each shire (bit m = minion m); bit 0 is ignored (timekeeper)
  uint64_t window;        // cycles: how long every hart runs (spin arms) or periods * period (wait arms)
  uint64_t period;        // cycles between two credits (wait and duty arms)
  uint64_t duty_cycles;   // X04_DUTY: cycles of no-op sled after each credit
  uint64_t sources;       // 256 B of zeros in DRAM: f0..f7 and the integer sources
  uint64_t results;       // X04Result[X04_MAX_HARTS], indexed by hart (128 B each)
  uint64_t sync;          // X04_SYNC_PER_SHIRE bytes per shire: start handshake and counter-read flags
  uint64_t epoch;         // a value unique to this launch: a sync word holds it only if written in this launch
  uint64_t cluster;       // X04_MIX: 0 = class ops spread one in every `every` slots; 1 = all in a row at the body's start
  uint64_t hs_limit;      // timekeeper: cycles to wait for the waiting threads' reports before starting anyway
};

// Sync buffer, per shire (local atomics only, each word written by one hart):
//   bytes   0..511  ready word of each hart of the shire (index = hart & 63): epoch once its counter is empty
//   bytes 512..767  done word of each minion's thread 1 (index = minion): epoch once it has finished
//   bytes 768..775  go word: epoch once the timekeeper has started its periods

struct X04Result {
  uint64_t cycles;        // cycles the hart's timed part took
  uint64_t loops;         // sled loops completed (512 slots each; 64 in the duty arms); X04_STALL: loops of 64 divides
  uint64_t periods;       // credits consumed (wait and duty arms); the timekeeper: periods for which it sent credits
  uint64_t retired0;      // reader harts only (thread 0 of minions 0, 8, 16, 24): hpmcounter4 at the end
  uint64_t retired1;      //   hpmcounter5 at the end
  uint64_t icache_req;    //   hpmcounter7 at the end
  uint64_t icache_miss;   //   hpmcounter8 at the end
  uint64_t drained;       // wait and duty arms: credits found in the counter at the start (and taken)
  uint32_t hart;
  uint32_t magic;
  uint64_t awake;         // duty arms: cycles from each wake to the sled's exit, summed (the awake cycles)
  uint64_t flags;         // X04_F_*
  uint64_t hs_cycles;     // timekeeper: cycles it waited for the reports
  uint64_t pad[4];        // 128 B per hart: no two minions ever write one cache line
};
