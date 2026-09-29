/*-------------------------------------------------------------------------
 * pciebench's first-touch probe (hub rung 34; ../touch_args.h has the arguments and the protocol).
 *
 * One hart (args->hart, 0: shire 0, minion 0, thread 0) loads word 0 of m lines of the buffer the host has just
 * written over PCIe, one load at a time, and times each with hpmcounter3. Launched without the L3 flush, that first
 * touch shows where the host's write left the line: an L3 hit (110 + 12 x hops to its home, E36) or DRAM (another
 * ~91 + 12 x hops past the home). It then times the same lines again (the L2, a reference for the timer), checks the
 * first-touch values against the host's pattern, and copies the timings out. Every other hart returns at once.
 *
 * The timings are kept in the shire's own scratchpad while it runs, so between two timed loads the probe sends nothing
 * over the mesh. No double, no division, no cycle CSR, no global atomic, no tensor op (docs/findings/
 * 14-card-behaviour.md, "Traps"): only loads of the host's buffer, local scratchpad stores and, at the end, plain
 * stores to the host's output buffer.
 *-------------------------------------------------------------------------*/
#include <stdint.h>
#include "etsoc/isa/hart.h"
#include "touch_args.h"

int64_t entry_point(const struct TouchArgs* args);

// Cycle counter (hpmcounter3). On these cards the carry into bit 7 lands 11 cycles late, so a value whose low 7 bits
// are 0-10 reads 128 short; fixcyc() puts the 128 back (workloads/memprobe, E2). Only one hart of the minion reads it.
#define RDCYC(v) "csrr " v ", hpmcounter3\n"

static inline uint64_t fixcyc(uint64_t v)
{
    return v + ((uint64_t)((v & 0x7F) < 11) << 7);
}

static inline uint64_t cycles(void)
{
    uint64_t v;
    __asm__ __volatile__(RDCYC("%0") : "=r"(v));
    return fixcyc(v);
}

// One timed load (memprobe's tload): the addi cannot issue until the data is back, and the second counter read
// follows it, so dt is the load-to-use latency plus the counter's own ~10 cycles.
static inline uint64_t tload(uint64_t a, uint32_t* dt)
{
    uint64_t t0, t1, v;
    __asm__ __volatile__(RDCYC("%0") "ld %2, 0(%3)\n addi %2, %2, 1\n" RDCYC("%1")
                         : "=&r"(t0), "=&r"(t1), "=&r"(v) : "r"(a) : "memory");
    *dt = (uint32_t)(fixcyc(t1) - fixcyc(t0));
    return v - 1;
}

int64_t entry_point(const struct TouchArgs* args)
{
    if (get_hart_id() != args->hart)
        return 0;
    const uint64_t n = args->n_lines, m = args->m;
    if (args->magic != TOUCH_MAGIC || args->buf == 0 || args->out == 0 || n == 0 || (n & (n - 1)) != 0 ||
        m > TOUCH_MAX_LINES || m > n || (args->a_mul & 1) == 0)
        return 0;
    if (m == 0)
        return 0;   // a launch that exists only for its L3 flush

    volatile uint32_t* d1 = (volatile uint32_t*)TOUCH_SCP_ADDR(TOUCH_SCP_OFFSET);
    volatile uint32_t* d2 = d1 + TOUCH_MAX_LINES;
    const uint64_t buf = args->buf, a = args->a_mul, b = args->b_off;
    const uint64_t se = args->seed_expect, sp = args->seed_prev;
    uint64_t ok = 0, stale = 0, other = 0, first_bad = ~0ull, sink = 0;
    uint32_t dt;

    // Write the timing slots once before the clock starts, so that a store inside the timed loop never opens a
    // scratchpad line for the first time (a new line every 16 slots) just before the next timed load.
    for (uint64_t k = 0; k < m; k++) {
        d1[k] = 0;
        d2[k] = 0;
    }
    __asm__ __volatile__("fence" ::: "memory");
    const uint64_t t0 = cycles();
    // The first touch of each line: nothing but the timed load reaches past the shire between two of them.
    for (uint64_t k = 0; k < m; k++) {
        const uint64_t i = touch_line(a, b, n, k);
        const uint64_t v = tload(buf + (i << 6), &dt);
        d1[k] = dt;
        if (v == touch_pat(se, i))
            ok++;
        else {
            if (sp != 0 && v == touch_pat(sp, i))
                stale++;
            else
                other++;
            if (first_bad == ~0ull)
                first_bad = k;
        }
    }
    // The second touch of the same lines, in the same order: at the host's default m = 4,096 lines (256 KB), at most
    // two lines per set of the 512 KB 4-way L2, so these are L2 hits, the timer's reference.
    for (uint64_t k = 0; k < m; k++) {
        const uint64_t i = touch_line(a, b, n, k);
        sink ^= tload(buf + (i << 6), &dt);
        d2[k] = dt;
    }
    const uint64_t t1 = cycles();

    volatile uint32_t* o = (volatile uint32_t*)(args->out + sizeof(struct TouchStatus));
    for (uint64_t k = 0; k < m; k++) {
        o[k] = d1[k];
        o[m + k] = d2[k];
    }
    volatile struct TouchStatus* s = (volatile struct TouchStatus*)args->out;
    s->cycles = t1 - t0;
    s->ok = ok;
    s->stale = stale;
    s->other = other;
    s->first_bad = first_bad;
    s->sink = sink;
    s->nonce = args->nonce;
    __asm__ __volatile__("fence" ::: "memory");
    s->magic = TOUCH_MAGIC;
    __asm__ __volatile__("fence" ::: "memory");
    return 0;
}
