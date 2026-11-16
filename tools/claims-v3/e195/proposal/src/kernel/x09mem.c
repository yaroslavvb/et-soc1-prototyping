/*-------------------------------------------------------------------------
 * x09mem: memory traffic with designed data (device kernel).
 *
 * Hart 0 of every participating minion moves 64 B lines between the cores and
 * DRAM until a cycle deadline, in one of five modes (x09mem_args.h):
 *
 *   X9_RD      flw.ps at a stride of 64 through the L1: one line read a load
 *              (the access of the public catalogue's flw_pat pattern).
 *   X9_WR      a tensor store of f0..f15 (16 rows x 32 B = 512 B = 8 lines),
 *              marching through the slice, eight stores then a wait (the
 *              access of the public catalogue's tstore_raw pattern).
 *   X9_RD_L1   the read loop with a stride of 0: every load hits one L1 line.
 *   X9_WR_SCP  the write loop into the minion's own scratchpad region.
 *   X9_WR_NST  the paced write loop with the tensor store replaced by a write
 *              of zero to the floating-point flags: nothing is stored.
 *
 * The data never changes during a launch: reads see what the host wrote into
 * the slices, writes store the minion's own 512 B image held in f0..f15. So
 * every arm of a direction runs the same instructions on the same addresses at
 * the same rate, and only the bits on the wires differ.
 *
 * Each timed loop is one asm statement, so its instructions are fixed by the
 * source and not by the compiler: in the write loops the image is loaded into
 * f0..f15 inside the same statement, so nothing can spill or restore those
 * registers between the load and the stores.
 *
 * Flat out (period 0): eight accesses per iteration, then the deadline check.
 * Paced (period > 0): one access, then the cycle counter is read until the
 * next slot opens, one slot every `period` cycles; a slot that is already open
 * when the access has been issued counts as late. With `phase` set, minion m's
 * slot grid starts (m * period) / 1024 cycles into the launch, so the 1,024
 * harts' accesses spread evenly over each period.
 *
 * Denominators: cycles (hpmcounter3), loop iterations and accesses, the
 * neighbourhood counters hpmcounter4 (thread-0 instructions retired) and
 * hpmcounter6 (L1 miss requests) before and after the loop, and on one hart the
 * memory shires' read and write request counters through the user-mode system
 * call of the open SDK (syscall.h, SYSCALL_PMC_MS_SAMPLE), before and after.
 *-------------------------------------------------------------------------*/

#include <stdbool.h>
#include <stdint.h>
#include "etsoc/isa/hart.h"
#include "etsoc/isa/syscall.h"
#include "x09mem_args.h"

int64_t entry_point(const struct X9Args* args);

/* The cycle counter is read four times in one aligned half line (the public erratum's workaround, as the public
 * catalogue does it); the last read is the value. */
#define CYC(r) ".p2align 4\n csrr " r ", hpmcounter3\n csrr " r ", hpmcounter3\n csrr " r ", hpmcounter3\n" \
               " csrr " r ", hpmcounter3\n"

static inline uint64_t cycles(void)
{
    uint64_t v;
    __asm__ __volatile__(CYC("%0") : "=r"(v));
    return v;
}

#define CSR_READ(name) ({ uint64_t _v; __asm__ __volatile__("csrr %0, " name : "=r"(_v)); _v; })

/* f0..f15 = the 512 B image at %[img]; all eight lanes enabled. */
#define LOAD_IMAGE                                                                                        \
    "mov.m.x m0, zero, 0xff\n"                                                                            \
    "flw.ps f0, 0(%[img])\n flw.ps f1, 32(%[img])\n flw.ps f2, 64(%[img])\n flw.ps f3, 96(%[img])\n"      \
    "flw.ps f4, 128(%[img])\n flw.ps f5, 160(%[img])\n flw.ps f6, 192(%[img])\n flw.ps f7, 224(%[img])\n"  \
    "flw.ps f8, 256(%[img])\n flw.ps f9, 288(%[img])\n flw.ps f10, 320(%[img])\n flw.ps f11, 352(%[img])\n" \
    "flw.ps f12, 384(%[img])\n flw.ps f13, 416(%[img])\n flw.ps f14, 448(%[img])\n flw.ps f15, 480(%[img])\n"
#define FREGS "f0", "f1", "f2", "f3", "f4", "f5", "f6", "f7", "f8", "f9", "f10", "f11", "f12", "f13", "f14", "f15"

/* One tensor store of 16 rows x 32 B from f0..f15 to the 512 B block at %[p]: the control word is the block's
 * address or'ed with %[cst] (cols 1, rows - 1 = 15: the open SDK's tensor_store encoding), the row stride (32) in
 * x31. Then the pointer steps 512 and wraps at %[end]. */
#define STORE_STEP                                                                                        \
    "or %[t], %[p], %[cst]\n csrw 0x87f, %[t]\n"                                                          \
    "addi %[p], %[p], 512\n bltu %[p], %[end], 2f\n mv %[p], %[base]\n2:\n"
/* The same step with the tensor store replaced by a write of zero to the floating-point flags (fflags, unused by
 * this kernel): the control that stores nothing. */
#define NOSTORE_STEP                                                                                      \
    "or %[t], %[p], %[cst]\n csrw fflags, zero\n"                                                         \
    "addi %[p], %[p], 512\n bltu %[p], %[end], 2f\n mv %[p], %[base]\n2:\n"
/* One 32 B load at %[p] (into f8, never read), then the pointer steps %[st] and wraps at %[end]. */
#define LOAD_STEP                                                                                         \
    "flw.ps f8, 0(%[p])\n add %[p], %[p], %[st]\n bltu %[p], %[end], 2f\n mv %[p], %[base]\n2:\n"

/* The memory shires' request counters: pmc 1 = reads, 2 = writes, 0 = cycles (the firmware's default setup). */
static void sample_ms(uint64_t* rd, uint64_t* wr, uint64_t* cyc, uint64_t* bad)
{
    uint64_t r = 0, w = 0;
    for (uint64_t ms = 0; ms < X9_MS_COUNT; ++ms) {
        const int64_t a = syscall(SYSCALL_PMC_MS_SAMPLE, ms, 1, 0);
        const int64_t b = syscall(SYSCALL_PMC_MS_SAMPLE, ms, 2, 0);
        if (a < 0) { ++*bad; } else { r += (uint64_t)a; }
        if (b < 0) { ++*bad; } else { w += (uint64_t)b; }
    }
    const int64_t c = syscall(SYSCALL_PMC_MS_SAMPLE, 0, 0, 0);
    if (c < 0) { ++*bad; }
    *rd = r;
    *wr = w;
    *cyc = c < 0 ? 0 : (uint64_t)c;
}

int64_t entry_point(const struct X9Args* a)
{
    const uint64_t hart = get_hart_id();
    const uint64_t shire = hart >> 6;
    if (shire >= 32 || !((a->shire_mask >> shire) & 1)) {
        return 0;
    }
    const uint64_t thread = hart & 1;
    const uint64_t minion_in_shire = (hart >> 1) & 31;
    if (thread) {
        return 0;   // hart 0 of each minion only: only hart 0 may issue tensor stores, and the reads match it
    }
    if (a->minion_mask && !((a->minion_mask >> minion_in_shire) & 1)) {
        return 0;
    }
    const uint64_t mode = a->mode;
    if (mode != X9_RD && mode != X9_WR && mode != X9_RD_L1 && mode != X9_WR_SCP && mode != X9_WR_NST) {
        return 0;
    }
    if (mode == X9_WR_NST && a->period == 0) {
        return 0;   // the no-store control exists only paced (flat out it would be the store loop)
    }
    const uint64_t minion = hart >> 1;   // 0..1023 over the chip
    const bool reporter = a->ms_counters && hart == 0;
    const bool reads = mode == X9_RD || mode == X9_RD_L1;

    uint64_t base = a->slice + hart * a->slice_bytes;
    if (a->bank_spread) {
        base += (minion & 7) * 1024;   // spread the harts over the eight DRAM banks, as flw_pat does
    }
    uint64_t region = a->region;
    if (mode == X9_WR_SCP || mode == X9_WR_NST) {   // NST stores nothing: its pointer only walks the same region
        base = X9_SCP_ADDR(X9_SCP_LOCAL, a->scp_off + minion_in_shire * a->scp_bytes);
        region = a->scp_bytes;
    }
    const uint64_t step = reads ? a->stride : 512;
    const uint64_t end = base + (step ? region / step * step : region);   // the pointer wraps here
    const uint64_t img = a->images + minion * 512;
    const uint64_t cst = (1ull << 55) | (15ull << 51);
    const uint64_t period = a->period;

    uint64_t iters = 0, acc = 0, spins = 0, late = 0, cyc = 0, p = base, t = 0, now = 0;
    uint64_t rd0 = 0, wr0 = 0, cy0 = 0, rd1 = 0, wr1 = 0, cy1 = 0, bad = 0;
    if (reporter) {
        sample_ms(&rd0, &wr0, &cy0, &bad);
    }
    const uint64_t ret0 = CSR_READ("hpmcounter4"), l1m0 = CSR_READ("hpmcounter6");
    const uint64_t t0 = cycles(), deadline = t0 + a->window;
    // Paced loops: the slot grid starts at g0. With the phase set, minion m waits (m * period) / 1024 cycles first,
    // outside the timed loop and its poll count.
    uint64_t g0 = t0;
    if (period && a->phase) {
        g0 = t0 + (minion * period) / 1024;
        while (cycles() < g0) {
        }
    }

    if (reads && period == 0) {
        __asm__ __volatile__("mov.m.x m0, zero, 0xff\n"
                             "1:\n" LOAD_STEP LOAD_STEP LOAD_STEP LOAD_STEP LOAD_STEP LOAD_STEP LOAD_STEP LOAD_STEP
                             "addi %[it], %[it], 1\n" CYC("%[now]") "bltu %[now], %[dl], 1b\n"
                             : [p] "+&r"(p), [it] "+&r"(iters), [now] "=&r"(now)
                             : [st] "r"(step), [end] "r"(end), [base] "r"(base), [dl] "r"(deadline)
                             : "memory", "f8");
        acc = iters * 8;
    } else if (reads) {
        __asm__ __volatile__("mov.m.x m0, zero, 0xff\n"
                             "mv %[nx], %[t0]\n"
                             "1:\n" LOAD_STEP
                             "addi %[acc], %[acc], 1\n add %[nx], %[nx], %[per]\n" CYC("%[now]")
                             "bltu %[now], %[nx], 4f\n addi %[late], %[late], 1\n j 5f\n"
                             "4:\n addi %[sp], %[sp], 1\n" CYC("%[now]") "bltu %[now], %[nx], 4b\n"
                             "5:\n bltu %[now], %[dl], 1b\n"
                             : [p] "+&r"(p), [acc] "+&r"(acc), [late] "+&r"(late), [sp] "+&r"(spins),
                               [now] "=&r"(now), [nx] "=&r"(t)
                             : [st] "r"(step), [end] "r"(end), [base] "r"(base), [dl] "r"(deadline),
                               [per] "r"(period), [t0] "r"(g0)
                             : "memory", "f8");
        iters = acc;
    } else if (period == 0) {
        __asm__ __volatile__(LOAD_IMAGE
                             "li x31, 32\n"
                             "1:\n" STORE_STEP STORE_STEP STORE_STEP STORE_STEP STORE_STEP STORE_STEP STORE_STEP
                             STORE_STEP
                             "li %[t], 8\n csrw 0x830, %[t]\n"
                             "addi %[it], %[it], 1\n" CYC("%[now]") "bltu %[now], %[dl], 1b\n"
                             : [p] "+&r"(p), [it] "+&r"(iters), [now] "=&r"(now), [t] "=&r"(t)
                             : [img] "r"(img), [cst] "r"(cst), [end] "r"(end), [base] "r"(base), [dl] "r"(deadline)
                             : "memory", "x31", FREGS);
        acc = iters * 8;
    } else if (mode != X9_WR_NST) {
        uint64_t nx = 0;
        __asm__ __volatile__(LOAD_IMAGE
                             "li x31, 32\n"
                             "mv %[nx], %[t0]\n"
                             ".p2align 4\n"   /* the loop starts aligned: its padding is the no-store loop's */
                             "1:\n" STORE_STEP
                             "addi %[acc], %[acc], 1\n andi %[t], %[acc], 7\n bnez %[t], 3f\n"
                             "li %[t], 8\n csrw 0x830, %[t]\n"
                             "3:\n add %[nx], %[nx], %[per]\n" CYC("%[now]")
                             "bltu %[now], %[nx], 4f\n addi %[late], %[late], 1\n j 5f\n"
                             "4:\n addi %[sp], %[sp], 1\n" CYC("%[now]") "bltu %[now], %[nx], 4b\n"
                             "5:\n bltu %[now], %[dl], 1b\n"
                             : [p] "+&r"(p), [acc] "+&r"(acc), [late] "+&r"(late), [sp] "+&r"(spins),
                               [now] "=&r"(now), [t] "=&r"(t), [nx] "=&r"(nx)
                             : [img] "r"(img), [cst] "r"(cst), [end] "r"(end), [base] "r"(base), [dl] "r"(deadline),
                               [per] "r"(period), [t0] "r"(g0)
                             : "memory", "x31", FREGS);
        iters = acc;
    } else {
        // the paced write loop instruction for instruction, the tensor store replaced (NOSTORE_STEP)
        uint64_t nx = 0;
        __asm__ __volatile__(LOAD_IMAGE
                             "li x31, 32\n"
                             "mv %[nx], %[t0]\n"
                             ".p2align 4\n"
                             "1:\n" NOSTORE_STEP
                             "addi %[acc], %[acc], 1\n andi %[t], %[acc], 7\n bnez %[t], 3f\n"
                             "li %[t], 8\n csrw 0x830, %[t]\n"
                             "3:\n add %[nx], %[nx], %[per]\n" CYC("%[now]")
                             "bltu %[now], %[nx], 4f\n addi %[late], %[late], 1\n j 5f\n"
                             "4:\n addi %[sp], %[sp], 1\n" CYC("%[now]") "bltu %[now], %[nx], 4b\n"
                             "5:\n bltu %[now], %[dl], 1b\n"
                             : [p] "+&r"(p), [acc] "+&r"(acc), [late] "+&r"(late), [sp] "+&r"(spins),
                               [now] "=&r"(now), [t] "=&r"(t), [nx] "=&r"(nx)
                             : [img] "r"(img), [cst] "r"(cst), [end] "r"(end), [base] "r"(base), [dl] "r"(deadline),
                               [per] "r"(period), [t0] "r"(g0)
                             : "memory", "x31", FREGS);
        iters = acc;
    }
    if (!reads) {
        __asm__ __volatile__("csrw 0x830, %0" : : "r"(8ull) : "memory");   // every store done before the end
    }
    cyc = cycles() - t0;

    const uint64_t ret1 = CSR_READ("hpmcounter4"), l1m1 = CSR_READ("hpmcounter6");
    if (reporter) {
        sample_ms(&rd1, &wr1, &cy1, &bad);
    }

    volatile struct X9Result* r = (volatile struct X9Result*)a->results + hart;
    r->cycles = cyc;
    r->iters = iters;
    r->accesses = acc;
    r->lines = (mode == X9_RD_L1 || mode == X9_WR_SCP || mode == X9_WR_NST) ? 0 : (reads ? acc : acc * 8);
    r->ret0 = ret0;
    r->ret1 = ret1;
    r->l1m0 = l1m0;
    r->l1m1 = l1m1;
    r->ms_rd = rd1 - rd0;
    r->ms_wr = wr1 - wr0;
    r->ms_cyc = cy1 - cy0;
    r->ms_bad = bad;
    r->spins = spins;
    r->late = late;
    r->hart = (uint32_t)hart;
    r->magic = X9_MAGIC;
    r->pad = reporter ? 1 : 0;   // 1: this record carries the memory shires' counters
    return 0;
}
