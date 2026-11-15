/*-------------------------------------------------------------------------
 * x04clock: what an awake core costs per cycle, against a core that waits.
 *
 * Minion 0, thread 0 of every launched shire is the timekeeper in every arm:
 * it reads the cycle counter for the launch's window and, once per period,
 * stores one credit for the waiting threads into the shire's CREDINC
 * registers (PRM ch. 11) when the arm waits on credits. Workers are the
 * minions of minion_mask (1..31).
 *
 * A worker's thread blocks on the fast credit counter (csrw fcc) in the wait
 * and duty arms: a user-mode hart cannot execute wfi (PRM 1.2). Every wait
 * has its partner in its own shire, and nothing can leave a thread blocked:
 *  - start handshake: each waiting thread first empties its counter (the
 *    SDK's init_fcc), then writes its ready word; the timekeeper starts its
 *    periods only when every waiting thread of its shire has reported (or
 *    after hs_limit cycles), and then writes the go word;
 *  - a waiting thread that reads the go word already written has missed the
 *    start: it skips its waits and flags itself (the launch is not counted);
 *  - the timekeeper sends three spare credits at the end and waits 4,096
 *    cycles, so nothing is in flight when it returns.
 * The sync words are written with the shire's local atomics and carry the
 * launch's epoch, so a word left from an earlier launch never counts.
 *
 * Sources are zeros (host buffer), results go to f8..f15 and are never read,
 * sources are never rewritten.
 *-------------------------------------------------------------------------*/

#include <stdbool.h>
#include <stdint.h>
#include "etsoc/isa/hart.h"
#include "etsoc/isa/esr_defines.h"
#include "etsoc/isa/fcc.h"
#include "etsoc/isa/atomic.h"
#include "x04_args.h"

int64_t entry_point(const struct X04Args* a);

#define VSINK "f8", "f9", "f10", "f11", "f12", "f13", "f14", "f15"
#define VSRC "f0", "f1", "f2", "f3", "f4", "f5", "f6", "f7"
#define X04_MIX_CASE(cls, every, cluster) ((cluster) * 10000 + (cls) * 100 + (every))

/* The cycle counter, read four times on an aligned group (the safe read for two threads of one minion). */
static inline uint64_t cycles(void)
{
    uint64_t v;
    __asm__ __volatile__(".p2align 4\n csrr %0, hpmcounter3\n csrr %0, hpmcounter3\n"
                         " csrr %0, hpmcounter3\n csrr %0, hpmcounter3\n" : "=r"(v));
    return v;
}

/* The other counters, each with the same four-read safe form. */
#define SAFE_HPM(name)                                                                                  \
    static inline uint64_t read_##name(void)                                                            \
    {                                                                                                   \
        uint64_t v;                                                                                     \
        __asm__ __volatile__(".p2align 4\n csrr %0, " #name "\n csrr %0, " #name "\n"                   \
                             " csrr %0, " #name "\n csrr %0, " #name "\n" : "=r"(v));                   \
        return v;                                                                                       \
    }
SAFE_HPM(hpmcounter4)
SAFE_HPM(hpmcounter5)
SAFE_HPM(hpmcounter7)
SAFE_HPM(hpmcounter8)

/* A short pause between two polls of a sync word: a chain of dependent multiplies, so that a polling thread
   leaves the issue slot to the other thread of its minion. */
static inline void pause(void)
{
    uint64_t x = 3;
    __asm__ __volatile__(".rept 16\n mul %0, %0, %0\n.endr\n" : "+r"(x));
}

static inline volatile uint64_t* sync_word(const struct X04Args* a, uint64_t shire, uint64_t byte)
{
    return (volatile uint64_t*)(a->sync + shire * X04_SYNC_PER_SHIRE + byte);
}
static inline uint64_t sync_read(volatile uint64_t* p) { return atomic_or_local_64(p, 0); }
static inline void sync_write(volatile uint64_t* p, uint64_t v)
{
    __asm__ __volatile__("fence" ::: "memory");
    (void)atomic_exchange_local_64(p, v);
}

/* f0..f7 = eight 32 B vectors of zeros; then m0 = the arm's lane mask. */
static inline void load_vsrc(uint64_t buf, uint64_t mask)
{
    __asm__ __volatile__("mov.m.x m0, zero, 0xff\n"
                         "flw.ps f0, 0(%0)\n flw.ps f1, 32(%0)\n flw.ps f2, 64(%0)\n flw.ps f3, 96(%0)\n"
                         "flw.ps f4, 128(%0)\n flw.ps f5, 160(%0)\n flw.ps f6, 192(%0)\n flw.ps f7, 224(%0)\n"
                         : : "r"(buf) : "memory", VSRC);
    __asm__ __volatile__("mov.m.x m0, %0, 0" : : "r"(mask & 0xff));
}

/* One loop = one 512-slot body, then a cycle-counter check. RVC is off so every slot is four bytes. */
#define RUN_SLED(BODY)                                                                                  \
    do {                                                                                                \
        const uint64_t t0 = cycles(), deadline = t0 + a->window;                                        \
        do {                                                                                            \
            __asm__ __volatile__(".option push\n.option norvc\n" BODY ".option pop\n" : : : VSINK);     \
            ++loops;                                                                                    \
        } while (cycles() < deadline);                                                                  \
        cyc = cycles() - t0;                                                                            \
    } while (0)

#define NOP_SLED_512 ".rept 512\naddi x0, x0, 0\n.endr\n"
#define NOP_SLED_64 ".rept 64\naddi x0, x0, 0\n.endr\n"

/* Empty this thread's counter, report ready, and say whether the start was already given (then: do not wait). */
static bool ready_and_check_late(const struct X04Args* a, uint64_t shire, uint64_t hart, uint64_t* drained)
{
    *drained = read_fcc(FCC_0);
    init_fcc(FCC_0);
    sync_write(sync_word(a, shire, (hart & 63) * 8), a->epoch);
    return sync_read(sync_word(a, shire, 768)) == a->epoch;
}

int64_t entry_point(const struct X04Args* a)
{
    const uint64_t hart = get_hart_id();
    const uint64_t shire = hart >> 6;
    if (shire >= 32 || !((a->shire_mask >> shire) & 1)) {
        return 0;
    }
    const uint64_t thread = hart & 1;
    const uint64_t minion = (hart >> 1) & 31;
    const uint32_t workers = (uint32_t)(a->minion_mask & 0xFFFFFFFEull);
    const bool duty_waits = a->arm == X04_DUTY && a->duty_cycles < a->period;
    const bool t0_credit = a->arm == X04_WAIT || duty_waits;
    const bool t1_credit = a->t1 == X04_T1_WAIT || (a->t1 == X04_T1_SAME && t0_credit);
    const uint64_t periods = a->period ? a->window / a->period : 0;
    uint64_t loops = 0, cyc = 0, taken = 0, drained = 0, awake = 0, flags = 0, hs_cycles = 0;

    if (minion == 0) {
        if (thread) {
            return 0;
        }
        /* The timekeeper: the same loop in every arm; it stores credits only when an arm waits on them. */
        const bool credits = (t0_credit || t1_credit) && workers;
        if (credits) {
            /* Start handshake: every waiting thread of this shire has emptied its counter. */
            const uint64_t h0 = cycles(), give_up = h0 + a->hs_limit;
            for (uint64_t m = 1; m < 32; ++m) {
                if (!((workers >> m) & 1)) {
                    continue;
                }
                for (uint64_t t = 0; t < 2; ++t) {
                    if ((t == 0 && !t0_credit) || (t == 1 && !t1_credit)) {
                        continue;
                    }
                    volatile uint64_t* w = sync_word(a, shire, (m * 2 + t) * 8);
                    while (sync_read(w) != a->epoch) {
                        if (cycles() > give_up) {
                            flags |= X04_F_HS_BAILOUT;
                            break;
                        }
                        pause();
                    }
                }
            }
            sync_write(sync_word(a, shire, 768), a->epoch);
            hs_cycles = cycles() - h0;
        }
        const uint64_t t0 = cycles();
        for (uint64_t k = 1; k <= periods; ++k) {
            const uint64_t target = t0 + k * a->period;
            while (cycles() < target) {
            }
            if (credits) {
                if (t0_credit) {
                    SEND_FCC(THIS_SHIRE, THREAD_0, FCC_0, workers);
                }
                if (t1_credit) {
                    SEND_FCC(THIS_SHIRE, THREAD_1, FCC_0, workers);
                }
                ++taken;
            }
        }
        cyc = cycles() - t0;
        if (credits) {
            /* three spare credits, then let them land (the firmware empties the counters after the kernel) */
            for (int s = 0; s < 3; ++s) {
                if (t0_credit) {
                    SEND_FCC(THIS_SHIRE, THREAD_0, FCC_0, workers);
                }
                if (t1_credit) {
                    SEND_FCC(THIS_SHIRE, THREAD_1, FCC_0, workers);
                }
            }
            const uint64_t settle = cycles() + 4096;
            while (cycles() < settle) {
            }
        }
    } else {
        if (!((workers >> minion) & 1)) {
            return 0;
        }
        uint64_t arm = a->arm;
        if (thread) {
            if (a->t1 == X04_T1_OFF) {
                return 0;
            }
            if (a->t1 == X04_T1_WAIT) {
                arm = X04_WAIT;
            }
        }
        const volatile uint64_t* sw = (const volatile uint64_t*)a->sources;
        switch (arm) {
        case X04_TK:
            return 0;

        case X04_SPIN:
            RUN_SLED(NOP_SLED_512);
            break;

        case X04_WAIT: {
            if (ready_and_check_late(a, shire, hart, &drained)) {
                flags |= X04_F_LATE;
                break;
            }
            const uint64_t t0 = cycles();
            for (uint64_t k = 0; k < periods; ++k) {
                wait_fcc(FCC_0);
                ++taken;
            }
            cyc = cycles() - t0;
            break;
        }

        case X04_DUTY: {
            /* One 64-slot body and one cycle check per loop at every duty, the top (no waits) included. */
            if (duty_waits && ready_and_check_late(a, shire, hart, &drained)) {
                flags |= X04_F_LATE;
                break;
            }
            const uint64_t span = duty_waits ? a->duty_cycles : a->period;
            const uint64_t t0 = cycles();
            for (uint64_t k = 0; k < periods; ++k) {
                if (duty_waits) {
                    wait_fcc(FCC_0);
                    ++taken;
                }
                const uint64_t w0 = cycles(), deadline = w0 + span;
                uint64_t c;
                do {
                    __asm__ __volatile__(".option push\n.option norvc\n" NOP_SLED_64 ".option pop\n");
                    ++loops;
                    c = cycles();
                } while (c < deadline);
                awake += c - w0;
            }
            cyc = cycles() - t0;
            break;
        }

        case X04_STALL: {
            uint64_t x = sw[0];
            const uint64_t z = sw[1];
            const uint64_t t0 = cycles(), deadline = t0 + a->window;
            do {
                __asm__ __volatile__(".rept 64\ndiv %0, %0, %1\n.endr\n" : "+r"(x) : "r"(z));
                ++loops;
            } while (cycles() < deadline);
            cyc = cycles() - t0;
            break;
        }

        case X04_MIX: {
            load_vsrc(a->sources, a->mask);
            switch (X04_MIX_CASE(a->cls, a->every, a->cluster)) {
#include "x04_blocks.inc"
            default:
                return 0;
            }
            __asm__ __volatile__("mov.m.x m0, zero, 0xff");
            break;
        }

        default:
            return 0;
        }
    }

    volatile struct X04Result* r = (volatile struct X04Result*)a->results + hart;
    if (thread == 1 && (minion & 7) == 0) {
        /* tell this minion's counter reader (thread 0) that this thread has finished */
        sync_write(sync_word(a, shire, 512 + minion * 8), a->epoch);
    }
    if (thread == 0 && (minion & 7) == 0) {
        /* One reader per neighbourhood, thread 0, after its own thread 1 has finished (erratum 1.23). */
        const bool t1_runs = minion != 0 && a->t1 != X04_T1_OFF && a->arm != X04_TK && ((workers >> minion) & 1);
        if (t1_runs) {
            uint64_t n = 0;
            while (sync_read(sync_word(a, shire, 512 + minion * 8)) != a->epoch) {
                if (++n > 200000) {
                    flags |= X04_F_CTR_UNSYNCED;
                    break;
                }
                pause();
            }
        }
        r->retired0 = read_hpmcounter4();
        r->retired1 = read_hpmcounter5();
        r->icache_req = read_hpmcounter7();
        r->icache_miss = read_hpmcounter8();
    }
    r->cycles = cyc;
    r->loops = loops;
    r->periods = taken;
    r->drained = drained;
    r->awake = awake;
    r->flags = flags;
    r->hs_cycles = hs_cycles;
    r->hart = (uint32_t)hart;
    r->magic = X04_MAGIC;
    return 0;
}
