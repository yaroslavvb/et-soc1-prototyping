/*-------------------------------------------------------------------------
 * On-chip communication probes for ET-SoC-1 (see ../README.md).
 *
 * Every probe runs on hart 0 of the minions the host schedules; hart 1 returns
 * at once. Pairs and rings come from a schedule of rounds in DRAM
 * (nocbench_args.h), so one launch can walk a whole shire-to-shire matrix.
 *
 *  NB_PINGPONG   TensorSend / TensorRecv round trips between two minions: the
 *                data goes from one hart's vector registers straight into the
 *                other's, with an optional combine (ADD, MAX, ...) on arrival.
 *  NB_STREAM     one-way TensorSend stream, one message per TensorRecv.
 *  NB_SHIFT      rings: each step every minion sends to `next` and receives
 *                from `prev`. Neighbours alternate send-first / receive-first,
 *                so the rendezvous never deadlocks.
 *  NB_ALLREDUCE  hardware reduction tree (TensorReduce) then broadcast tree
 *                (TensorBroadcast), over the first 2^levels minions of every
 *                launched shire (levels <= 5).
 *  NB_FCC        credit round trips: a store to the partner shire's CREDINC
 *                ESR, and a blocking write of the FCC CSR on the other side
 *                (or, with args->poll, a spin on FCCNB that can give up).
 *  NB_FLAG       flag round trips through global atomics on DRAM lines, which
 *                resolve in L3: what a GPU does between SMs.
 *  NB_BARRIER    FLB + FCC barrier in each shire, optionally chip-wide through
 *                one global atomic per shire.
 *  NB_SPIN       integer loop on the same harts: power baseline.
 *
 * The hardware keeps one "ready" flag per minion for TensorSend/Recv, not one
 * per partner (core-et dcache_reduce.v). A minion that could get readies from
 * two partners at once can lose one and stall for good, and a stalled hart
 * ignores the firmware's abort, so the host only builds schedules where that
 * cannot happen (the simulator tracks partners separately and never shows it).
 *
 * Timing uses the minion cycle counter (hpmcounter3). Every record is a 64 B
 * line of its own, because the L1s are not coherent.
 *-------------------------------------------------------------------------*/

#include <stdbool.h>
#include <stdint.h>
#include "etsoc/isa/esr_defines.h"
#include "etsoc/isa/hart.h"
#include "nocbench_args.h"

int64_t entry_point(const struct NbArgs* args);

#define NB_FLB 31  // fast local barrier used by the barriers (the firmware clears all FLBs before a launch)

// The tensor unit reads and writes f0-f31 behind the compiler's back.
#define FREGS                                                                                      \
    "f0", "f1", "f2", "f3", "f4", "f5", "f6", "f7", "f8", "f9", "f10", "f11", "f12", "f13", "f14", \
        "f15", "f16", "f17", "f18", "f19", "f20", "f21", "f22", "f23", "f24", "f25", "f26", "f27", \
        "f28", "f29", "f30", "f31"

// Four back-to-back reads: the firmware's workaround for RTLMIN-6496 (etsoc/drivers/pmu/pmu.h).
static inline uint64_t cycles(void)
{
    uint64_t v;
    __asm__ __volatile__(".p2align 4\n csrr %0, hpmcounter3\n csrr %0, hpmcounter3\n"
                         " csrr %0, hpmcounter3\n csrr %0, hpmcounter3\n" : "=r"(v));
    return v;
}

/* tensor_reduce CSR 0x800 (PRM 9.4): FREG 61:57, FUNCT 27:24, COUNT 22:16, minion or HEIGHT 15:3, op 1:0.
   The w_* helpers build the CSR value; t_op issues it. No "memory" clobber, so the timed loops keep
   everything in registers. */
static inline uint64_t w_send(uint64_t to, uint64_t count, uint64_t freg)
{
    return (freg << 57) | ((count & 0x7F) << 16) | ((to & 0x1FFF) << 3);
}

static inline uint64_t w_recv(uint64_t from, uint64_t count, uint64_t funct, uint64_t freg)
{
    return (freg << 57) | ((funct & 0xF) << 24) | ((count & 0x7F) << 16) | ((from & 0x1FFF) << 3) | 1;
}

static inline uint64_t w_bcast(uint64_t height, uint64_t count, uint64_t funct)
{
    return ((funct & 0xF) << 24) | ((count & 0x7F) << 16) | ((height & 0xF) << 3) | 2;
}

static inline uint64_t w_reduce(uint64_t height, uint64_t count, uint64_t funct)
{
    return ((funct & 0xF) << 24) | ((count & 0x7F) << 16) | ((height & 0xF) << 3) | 3;
}

static inline void t_op(uint64_t v)
{
    __asm__ __volatile__("csrw 0x800, %0" : : "r"(v) : FREGS);
}

// n times: x, or x then y.
static void pulse1(uint64_t x, uint64_t n)
{
    for (uint64_t i = 0; i < n; ++i) {
        t_op(x);
    }
}

static void pulse2(uint64_t x, uint64_t y, uint64_t n)
{
    for (uint64_t i = 0; i < n; ++i) {
        t_op(x);
        t_op(y);
    }
}

// TensorWait 9: every earlier TensorSend/Recv/Reduce/Broadcast of this hart has completed.
static inline void t_wait(void)
{
    __asm__ __volatile__("csrwi 0x830, 9" : : : "memory", FREGS);
}

// Every lane of f0-f31 = v.
static inline void fill(uint32_t v)
{
    __asm__ __volatile__("mov.m.x m0, zero, 0xff\n"
                         "fbcx.ps f0, %0\n fbcx.ps f1, %0\n fbcx.ps f2, %0\n fbcx.ps f3, %0\n"
                         "fbcx.ps f4, %0\n fbcx.ps f5, %0\n fbcx.ps f6, %0\n fbcx.ps f7, %0\n"
                         "fbcx.ps f8, %0\n fbcx.ps f9, %0\n fbcx.ps f10, %0\n fbcx.ps f11, %0\n"
                         "fbcx.ps f12, %0\n fbcx.ps f13, %0\n fbcx.ps f14, %0\n fbcx.ps f15, %0\n"
                         "fbcx.ps f16, %0\n fbcx.ps f17, %0\n fbcx.ps f18, %0\n fbcx.ps f19, %0\n"
                         "fbcx.ps f20, %0\n fbcx.ps f21, %0\n fbcx.ps f22, %0\n fbcx.ps f23, %0\n"
                         "fbcx.ps f24, %0\n fbcx.ps f25, %0\n fbcx.ps f26, %0\n fbcx.ps f27, %0\n"
                         "fbcx.ps f28, %0\n fbcx.ps f29, %0\n fbcx.ps f30, %0\n fbcx.ps f31, %0\n"
                         : : "r"((uint64_t)v) : "memory", FREGS);
}

/* Lane 0 of f0 or f16, after a tensor op wrote it. Errata 1.29 type F: an fmv.x.w of the last register
   the tensor op wrote forces its write-back first. Which register that is depends on COUNT, so touch all. */
#define TOUCH_ALL                                                                                    \
    "fmv.x.w x0, f0\n fmv.x.w x0, f1\n fmv.x.w x0, f2\n fmv.x.w x0, f3\n fmv.x.w x0, f4\n"          \
    "fmv.x.w x0, f5\n fmv.x.w x0, f6\n fmv.x.w x0, f7\n fmv.x.w x0, f8\n fmv.x.w x0, f9\n"          \
    "fmv.x.w x0, f10\n fmv.x.w x0, f11\n fmv.x.w x0, f12\n fmv.x.w x0, f13\n fmv.x.w x0, f14\n"     \
    "fmv.x.w x0, f15\n fmv.x.w x0, f16\n fmv.x.w x0, f17\n fmv.x.w x0, f18\n fmv.x.w x0, f19\n"     \
    "fmv.x.w x0, f20\n fmv.x.w x0, f21\n fmv.x.w x0, f22\n fmv.x.w x0, f23\n fmv.x.w x0, f24\n"     \
    "fmv.x.w x0, f25\n fmv.x.w x0, f26\n fmv.x.w x0, f27\n fmv.x.w x0, f28\n fmv.x.w x0, f29\n"     \
    "fmv.x.w x0, f30\n fmv.x.w x0, f31\n"

static inline uint32_t lane0_f0(void)
{
    uint64_t v;
    __asm__ __volatile__(TOUCH_ALL "fmv.x.w %0, f0\n" : "=r"(v) : : "memory");
    return (uint32_t)v;
}

static inline uint32_t lane0_f16(void)
{
    uint64_t v;
    __asm__ __volatile__(TOUCH_ALL "fmv.x.w %0, f16\n" : "=r"(v) : : "memory");
    return (uint32_t)v;
}

/* Fast credit counters (PRM 11): a store to CREDINC0 (COUNTER0) or CREDINC1 (COUNTER1) of a shire adds a
   credit to thread 0 of every minion in the mask; writing the FCC CSR takes one, blocking until there is one. */
static inline void credit(uint64_t shire, uint64_t counter, uint32_t minion_mask)
{
    volatile uint64_t* const p = (volatile uint64_t*)ESR_SHIRE(shire, FCC_CREDINC_0) + counter;
    *p = minion_mask;
}

static inline void credit_wait(uint64_t counter)
{
    __asm__ __volatile__("csrw 0x821, %0" : : "r"(counter) : "memory");
}

/* Take one credit. With poll, first spin on FCCNB (CSR 0xCC0: COUNTER0 in bits 15:0, COUNTER1 in 31:16),
   which does not block, and give up after `limit` reads: a blocked FCC wait cannot be interrupted, so a
   credit that never arrives would otherwise hold the hart until the card is reset. */
static inline bool take_credit(uint64_t counter, uint64_t poll, uint64_t limit)
{
    if (poll) {
        const uint64_t shift = counter ? 16 : 0;
        for (uint64_t n = 0;; ++n) {
            uint64_t v;
            __asm__ __volatile__("csrr %0, 0xcc0" : "=r"(v) : : "memory");
            if ((v >> shift) & 0xFFFF) {
                break;
            }
            if (n >= limit) {
                return false;
            }
        }
    }
    credit_wait(counter);
    return true;
}

// FLBarrier (PRM 10.1.1): returns 1 on the hart that arrives last, and the counter resets.
static inline uint64_t flb_join(uint64_t barrier, uint64_t match)
{
    uint64_t last;
    __asm__ __volatile__("csrrw %0, 0x820, %1" : "=r"(last) : "r"((match << 5) | barrier) : "memory");
    return last;
}

// Global atomics resolve in L3 / memory, visible to every shire (PRM 7).
static inline uint32_t amoadd_g(volatile uint32_t* p, uint32_t v)
{
    uint32_t old;
    __asm__ __volatile__("amoaddg.w %0, %1, (%2)" : "=r"(old) : "r"(v), "r"(p) : "memory");
    return old;
}

static inline uint32_t amoor_g(volatile uint32_t* p, uint32_t v)
{
    uint32_t old;
    __asm__ __volatile__("amoorg.w %0, %1, (%2)" : "=r"(old) : "r"(v), "r"(p) : "memory");
    return old;
}

static inline void amoswap_g(volatile uint32_t* p, uint32_t v)
{
    uint32_t old;
    __asm__ __volatile__("amoswapg.w %0, %1, (%2)" : "=r"(old) : "r"(v), "r"(p) : "memory");
    (void)old;
}

// n credit round trips with the hart 0 of minion mask pm in shire ps. False if a polled wait gave up.
static bool credit_pingpong(bool first, uint64_t ps, uint32_t pm, uint64_t n, uint64_t poll, uint64_t limit)
{
    if (first) {
        for (uint64_t i = 0; i < n; ++i) {
            credit(ps, 0, pm);
            if (!take_credit(0, poll, limit)) {
                return false;
            }
        }
    } else {
        for (uint64_t i = 0; i < n; ++i) {
            if (!take_credit(0, poll, limit)) {
                return false;
            }
            credit(ps, 0, pm);
        }
    }
    return true;
}

// Flag round trips from..to: the initiator stores i in the partner's flag and waits for i in its own.
static void flag_pingpong(bool first, volatile uint32_t* mine, volatile uint32_t* theirs, uint32_t from, uint32_t to)
{
    for (uint32_t i = from; i <= to; ++i) {
        if (first) {
            amoswap_g(theirs, i);
            while (amoor_g(mine, 0) != i) {
            }
        } else {
            while (amoor_g(mine, 0) != i) {
            }
            amoswap_g(theirs, i);
        }
    }
}

/* Barrier of every minion in part_masks. Arrivals meet in the shire's FLB; the last one in the shire
   either releases the shire (NB_SCOPE_SHIRE) or adds one to a global counter, and the last shire to arrive
   releases every shire with one CREDINC store each. Everybody waits on credit counter 1.
   `gen` numbers the chip-wide barriers, so the counter never needs a reset. */
static bool barrier(const struct NbArgs* a, uint64_t shire, uint64_t scope, uint64_t gen)
{
    const volatile uint32_t* masks = (const volatile uint32_t*)a->part_masks;
    const uint32_t mine = masks[shire];
    if (flb_join(NB_FLB, (uint64_t)__builtin_popcount(mine) - 1)) {
        if (scope == NB_SCOPE_SHIRE) {
            credit(shire, 1, mine);
        } else if (amoadd_g((volatile uint32_t*)a->counter, 1) + 1 == (uint32_t)((gen + 1) * a->part_shires)) {
            for (uint64_t s = 0; s < 32; ++s) {
                const uint32_t m = masks[s];
                if (m) {
                    credit(s, 1, m);
                }
            }
        }
    }
    return take_credit(1, a->poll, a->poll_limit);
}

// Allreduce on the tree: up with TensorReduce (levels 0..top), down with TensorBroadcast (top..0).
static inline void tree(uint64_t top, uint64_t count, uint64_t funct)
{
    for (uint64_t h = 0; h <= top; ++h) {
        t_op(w_reduce(h, count, funct));
    }
    for (uint64_t h = top + 1; h-- > 0;) {
        t_op(w_bcast(h, count, NB_MOVE));
    }
}

struct Rec {
    uint64_t cycles;
    uint32_t value0, value1;
};

static struct Rec run_round(const struct NbArgs* a, uint64_t round, uint64_t me, uint32_t e)
{
    struct Rec r = { 0, 0, 0 };
    const uint64_t p = NB_PARTNER(e);
    const bool first = NB_FIRST(e) != 0;
    const uint64_t n = a->warmup + a->iters;
    const uint64_t count = a->count, funct = a->funct;
    uint64_t t0 = 0;

    switch (a->mode) {
    case NB_PINGPONG:
    case NB_STREAM:
    case NB_SHIFT: {
        // Two CSR values per step: x then y. Pairs send and receive in f0..; rings receive into f16..
        const uint64_t mode = a->mode, w = a->warmup, iters = a->iters;
        const uint64_t prev = mode == NB_SHIFT ? NB_PREV(e) : p;
        const uint64_t freg_in = mode == NB_SHIFT ? 16 : 0;
        const uint64_t snd = w_send(p, count, 0), rcv = w_recv(prev, count, funct, freg_in);
        const uint64_t x = first ? snd : rcv, y = first ? rcv : snd;
        fill(NB_PATTERN(me));
        if (mode == NB_STREAM) {
            pulse1(x, w);
        } else {
            pulse2(x, y, w);
        }
        t_wait();
        r.value0 = lane0_f0();
        t0 = cycles();
        if (mode == NB_STREAM) {
            pulse1(x, iters);
        } else {
            pulse2(x, y, iters);
        }
        t_wait();
        r.cycles = cycles() - t0;
        r.value1 = mode == NB_SHIFT ? lane0_f16() : lane0_f0();
        break;
    }

    case NB_FCC: {
        const uint64_t ps = p >> 5, w = a->warmup, iters = a->iters;
        const uint32_t pm = 1u << (p & 31);
        const uint64_t poll = a->poll, limit = a->poll_limit;
        if (!credit_pingpong(first, ps, pm, w, poll, limit)) {
            r.value1 = NB_TIMEOUT;
            break;
        }
        t0 = cycles();
        if (!credit_pingpong(first, ps, pm, iters, poll, limit)) {
            r.value1 = NB_TIMEOUT;
            break;
        }
        r.cycles = cycles() - t0;
        break;
    }

    case NB_FLAG: {
        volatile uint32_t* const flags = (volatile uint32_t*)a->flags;
        volatile uint32_t* const mine = flags + (round * NB_MINIONS + me) * 16;
        volatile uint32_t* const theirs = flags + (round * NB_MINIONS + p) * 16;
        const uint32_t w = (uint32_t)a->warmup, last = (uint32_t)n;
        flag_pingpong(first, mine, theirs, 1, w);
        t0 = cycles();
        flag_pingpong(first, mine, theirs, w + 1, last);
        r.cycles = cycles() - t0;
        r.value1 = amoor_g(mine, 0);
        break;
    }

    case NB_BARRIER: {
        const uint64_t shire = me >> 5, w = a->warmup, scope = a->scope;
        uint64_t i = 0;
        for (; i < w && barrier(a, shire, scope, i); ++i) {
        }
        t0 = cycles();
        for (; i < n && barrier(a, shire, scope, i); ++i) {
        }
        r.cycles = cycles() - t0;
        if (i < n) {
            r.value1 = NB_TIMEOUT;
        }
        break;
    }

    case NB_SPIN:
        t0 = cycles();
        for (uint64_t i = 0; i < a->iters; ++i) {
            __asm__ __volatile__("addi t0, t0, 1\n addi t1, t1, 1\n addi t2, t2, 1\n addi t3, t3, 1\n"
                                 : : : "t0", "t1", "t2", "t3");
        }
        r.cycles = cycles() - t0;
        break;

    default:
        break;
    }
    return r;
}

static void put(volatile struct NbResult* slot, const struct Rec* r, uint64_t iters, uint32_t partner,
                uint64_t me, uint64_t round)
{
    slot->cycles = r->cycles;
    slot->iters = iters;
    slot->value0 = r->value0;
    slot->value1 = r->value1;
    slot->partner = partner;
    slot->minion = (uint32_t)me;
    slot->round = (uint32_t)round;
    slot->magic = NB_MAGIC;
}

int64_t entry_point(const struct NbArgs* args)
{
    const uint64_t t_entry = cycles();
    const uint64_t hart = get_hart_id();
    const uint64_t shire = hart >> 6;
    if ((hart & 1) || shire >= 32 || !((args->shire_mask >> shire) & 1)) {
        return 0;
    }
    const uint64_t me = hart >> 1;  // minion ID: TensorSend's TARGET, and hart 0's mhartid / 2
    volatile struct NbResult* const results = (volatile struct NbResult*)args->results;
    uint64_t slot = ((const volatile uint32_t*)args->slot_base)[me];

    if (args->mode == NB_ALLREDUCE) {
        // Up to 5 levels the tree stays inside a shire, so every launched shire runs its own.
        const uint64_t levels = args->levels;
        const uint64_t local = levels <= 5 ? (me & 31) : me;
        if (local >> levels) {
            return 0;
        }
        // Minion m receives at levels below ctz(m) and sends at ctz(m); the root (m = 0) receives at every level.
        const uint64_t top = local ? (uint64_t)__builtin_ctzll(local) : levels - 1;
        struct Rec r = { 0, 0, 0 };
        fill((uint32_t)local + 1);
        tree(top, args->count, NB_IADD);  // checked: every minion ends with the sum over all
        t_wait();
        r.value0 = lane0_f0();
        const uint64_t t0 = cycles();
        for (uint64_t i = 0; i < args->iters; ++i) {
            tree(top, args->count, args->funct);  // IMAX or MOVE keep the sum, so it is checked again at the end
        }
        t_wait();
        r.cycles = cycles() - t0;
        r.value1 = lane0_f0();
        put(results + slot, &r, args->iters, 0, me, 0);
    } else {
        if (!((((const volatile uint32_t*)args->part_masks)[shire] >> (me & 31)) & 1)) {
            return 0;
        }
        const volatile uint32_t* const sched = (const volatile uint32_t*)args->schedule;
        for (uint64_t round = 0; round < args->rounds; ++round) {
            if (args->round_barrier && !barrier(args, shire, NB_SCOPE_CHIP, round)) {
                break;  // a credit never came: stop here, the host sees the missing records
            }
            const uint32_t e = sched[round * NB_MINIONS + me];
            if (e == NB_IDLE) {
                continue;
            }
            const struct Rec r = run_round(args, round, me, e);
            put(results + slot++, &r, args->iters, NB_PARTNER(e), me, round);
            if (r.value1 == NB_TIMEOUT) {
                break;
            }
        }
    }

    volatile struct NbResult* const clock = (volatile struct NbResult*)args->clocks + me;
    clock->t_entry = t_entry;
    clock->t_exit = cycles();
    clock->minion = (uint32_t)me;
    clock->magic = NB_MAGIC;
    return 0;
}
