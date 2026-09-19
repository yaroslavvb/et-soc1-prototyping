/*-------------------------------------------------------------------------
 * Memory-hierarchy probes for ET-SoC-1 (see ../README.md).
 *
 *  MH_CHASE      one hart follows a random pointer chain, p = *p, so each load
 *                waits for the previous one: load-to-use latency of whatever level
 *                the chain's working set lives in (L1, L2, L3, DRAM or L2 scratchpad).
 *  MH_STREAM_TL  hart 0 of every minion streams 1 KB TensorLoads into its L1
 *                scratchpad, two in flight. They bypass the L1 cache, so this gives
 *                the bandwidth of L2, L3, DRAM or the L2 scratchpad.
 *  MH_STREAM_L1  both harts re-read a private 256 B buffer with 32 B vector loads.
 *                It fits in the 512 B of L1 that each hart gets, so this is L1 bandwidth.
 *  MH_SPIN       both harts run an integer loop that touches no data: busy-core power.
 *
 * Timing uses the minion cycle counter (hpmcounter3). Each hart writes its result
 * to its own 64 B line, so the non-coherent L1s never share a line.
 *-------------------------------------------------------------------------*/

#include <stdbool.h>
#include <stdint.h>
#include "etsoc/isa/hart.h"
#include "etsoc/isa/tensors.h"
#include "memhier_args.h"

int64_t entry_point(const struct MhArgs* args);

// Four back-to-back reads: the firmware's workaround for RTLMIN-6496 (etsoc/drivers/pmu/pmu.h).
static inline uint64_t cycles(void)
{
    uint64_t v;
    __asm__ __volatile__(".p2align 4\n csrr %0, hpmcounter3\n csrr %0, hpmcounter3\n"
                         " csrr %0, hpmcounter3\n csrr %0, hpmcounter3\n" : "=r"(v));
    return v;
}

// n dependent loads (n is a multiple of 8).
static inline uint64_t chase(uint64_t p, uint64_t n)
{
    for (uint64_t i = 0; i < n; i += 8) {
        __asm__ __volatile__("ld %0, 0(%0)\n ld %0, 0(%0)\n ld %0, 0(%0)\n ld %0, 0(%0)\n"
                             "ld %0, 0(%0)\n ld %0, 0(%0)\n ld %0, 0(%0)\n ld %0, 0(%0)\n"
                             : "+r"(p) : : "memory");
    }
    return p;
}

static void put_result(const struct MhArgs* args, uint64_t hart, uint64_t cyc, uint64_t value, uint64_t bytes)
{
    volatile struct MhResult* r = (volatile struct MhResult*)args->results + hart;
    r->cycles = cyc;
    r->value = value;
    r->bytes = bytes;
    r->hart = (uint32_t)hart;
    r->magic = MH_MAGIC;
}

int64_t entry_point(const struct MhArgs* args)
{
    const uint64_t hart = get_hart_id();
    const uint64_t shire = hart >> 6;
    const uint64_t mask = args->shire_mask;
    if (shire >= 32 || !((mask >> shire) & 1))
        return 0;
    const uint64_t minion_in_shire = (hart >> 1) & 31;
    const uint64_t thread = hart & 1;
    // Participating minions are numbered 0..n-1 across the shires in mask.
    const uint64_t m = (uint64_t)__builtin_popcountll(mask & ((1ull << shire) - 1)) * 32 + minion_in_shire;

    if (args->mode == MH_CHASE) {
        if (hart != args->chaser_hart)
            return 0;
        if (args->build_next) {  // chain in a scratchpad: write it first
            const uint32_t* next = (const uint32_t*)args->build_next;
            volatile uint64_t* base = (volatile uint64_t*)args->chain_base;
            for (uint64_t i = 0; i < args->build_lines; i++)
                base[i * 8] = args->chain_base + (uint64_t)next[i] * 64;
            __asm__ __volatile__("fence" ::: "memory");
        }
        uint64_t p = chase(args->chain_base, args->warm_steps);
        const uint64_t t0 = cycles();
        p = chase(p, args->steps);
        const uint64_t t1 = cycles();
        put_result(args, hart, t1 - t0, p, 0);
        return 0;
    }

    if (args->mode == MH_STREAM_TL) {
        if (thread != 0)  // tensor loads are hart-0 only
            return 0;
        uint64_t base;
        if (args->scp_target) {
            const uint64_t target = args->scp_target == MH_SCP_LOCAL ? MH_SCP_LOCAL : (shire + args->scp_target) % 32;
            base = MH_SCP_ADDR(target, args->stream_base + minion_in_shire * args->minion_stride);
        } else {
            base = args->stream_base + m * args->minion_stride;
        }
        const uint64_t chunks = args->bytes_per_minion / 1024;
        uint64_t k = 0;
        const uint64_t t0 = cycles();
        for (uint64_t it = 0; it < args->iters; it++) {
            for (uint64_t c = 0; c < chunks; c++, k++) {
                const uint64_t id = k & 1;
                if (k >= 2)
                    tensor_wait((long)id);  // the load issued two steps ago into the same buffer
                tensor_load(false, false, id * 16, 0, 0, base + c * 1024, 0, 15, 64, id);
            }
        }
        tensor_wait(TENSOR_LOAD_WAIT_0);
        tensor_wait(TENSOR_LOAD_WAIT_1);
        const uint64_t t1 = cycles();
        put_result(args, hart, t1 - t0, 0, args->iters * chunks * 1024);
        return 0;
    }

    if (args->mode == MH_STREAM_L1) {
        const uint64_t buf = args->l1_buffers + (m * 2 + thread) * 256;
        __asm__ __volatile__("mov.m.x m0, zero, 0xff");  // vector loads use all 8 lanes
        uint64_t t0 = 0;
        for (uint64_t it = 0; it <= args->iters; it++) {  // pass 0 warms the lines into L1
            if (it == 1)
                t0 = cycles();
            __asm__ __volatile__("flw.ps f0, 0(%0)\n   flw.ps f1, 32(%0)\n  flw.ps f2, 64(%0)\n  flw.ps f3, 96(%0)\n"
                                 "flw.ps f4, 128(%0)\n flw.ps f5, 160(%0)\n flw.ps f6, 192(%0)\n flw.ps f7, 224(%0)\n"
                                 : : "r"(buf) : "f0", "f1", "f2", "f3", "f4", "f5", "f6", "f7", "memory");
        }
        const uint64_t t1 = cycles();
        put_result(args, hart, t1 - t0, 0, args->iters * 256);
        return 0;
    }

    if (args->mode == MH_SPIN) {
        uint64_t x = 0;
        const uint64_t t0 = cycles();
        for (uint64_t it = 0; it < args->iters; it++)
            __asm__ __volatile__("addi %0, %0, 1\n addi %0, %0, 1\n addi %0, %0, 1\n addi %0, %0, 1\n" : "+r"(x));
        const uint64_t t1 = cycles();
        put_result(args, hart, t1 - t0, x, 0);
        return 0;
    }
    return 0;
}
