/*-------------------------------------------------------------------------
 * Fine-grained memory probes for ET-SoC-1 (see ../README.md).
 *
 *  MP_PROGRAM  one hart runs a list of ops written by the host: timed single loads,
 *              evicts to a chosen cache level, delays, fences and time stamps.
 *              The list is first copied into the shire's own L2 scratchpad and the
 *              results are recorded there too, so the only DRAM traffic during the
 *              timed part is the traffic the ops ask for.
 *  MP_LOOP     hart 0 of every minion loops over its own few addresses (a table from
 *              the host): load, wait for the data, evict the line to a chosen level.
 *              Board and rail power over this loop, minus idle, gives energy per access.
 *  MP_TLOOP    (only with MP_EXT, -DMEMPROBE_EXT=ON) hart 0 of the minions in minion_mask streams TensorLoads
 *              of a set stride from its own base (a scratchpad or an L2-resident buffer): bandwidth per shire.
 *              MP_EXT also adds the program ops OP_TTLOAD (one timed TensorLoad) and OP_TERR (tensor_error).
 *
 * Timing uses the minion cycle counter (hpmcounter3). The minion is in order, so an
 * instruction that uses the loaded register stalls until the data arrives, and the
 * cycle read after it sees the full load-to-use latency.
 *-------------------------------------------------------------------------*/

#include <stdint.h>
#include "etsoc/isa/hart.h"
#include "etsoc/isa/syscall.h"
#include "memprobe_args.h"

int64_t entry_point(const struct MpArgs* args);

// Cycle counter (hpmcounter3). On this card the carry into bit 7 lands 11 cycles late, so a value
// whose low 7 bits are 0-10 reads 128 short. fixcyc() puts the 128 back; with it, 4,000 raw back-to-back
// read pairs all differ by the same 10 cycles. Only one hart per minion reads the counter, so the
// two-hart read collision of RTLMIN-6496 cannot happen.
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

// Load one 64-bit word and wait for it: the addi cannot issue until the data is back.
static inline uint64_t load_wait(uint64_t a)
{
    uint64_t v;
    __asm__ __volatile__("ld %0, 0(%1)\n addi %0, %0, 1\n" : "=&r"(v) : "r"(a) : "memory");
    return v;
}

static inline uint64_t tload(uint64_t a, uint64_t* dt)
{
    uint64_t t0, t1, v;
    __asm__ __volatile__(RDCYC("%0") "ld %2, 0(%3)\n addi %2, %2, 1\n" RDCYC("%1")
                         : "=&r"(t0), "=&r"(t1), "=&r"(v) : "r"(a) : "memory");
    *dt = fixcyc(t1) - fixcyc(t0);
    return v;
}

// evict_va (etsoc/isa/cacheops.h) for one line: level 0 L1, 1 L2, 2 L3, 3 memory is where the line is
// left. The op is asynchronous: callers fence and wait before timing the next access.
static inline void evict_line(uint64_t a, uint64_t level)
{
    const uint64_t enc = ((level & 3) << 58) | (a & 0xFFFFFFFFFFC0ull);
    // x31 holds the stride, which is unused for one line.
    __asm__ __volatile__("li x31, 64\n csrw 0x89f, %0\n" : : "r"(enc) : "x31", "memory");
}

#ifdef MP_EXT
/* TensorLoad (PRM 9.3.1; the same encoding as workloads/sparsity and enercat): `lines` 64 B lines from addr,
   `stride` bytes apart, into L1 scratchpad lines dst.., with load id `id` (TensorWait id). No tensor_mask, not TenB.
   Only hart 0 of a minion may issue it. */
static inline void t_load(uint64_t dst, uint64_t addr, uint64_t lines, uint64_t stride, uint64_t id)
{
    const uint64_t v = ((dst & 0x3F) << 53) | (addr & 0xFFFFFFFFFFC0ull) | ((lines - 1) & 0xF);
    register uint64_t x31 __asm__("x31") = (stride & ~0x3Full) | (id & 1);
    __asm__ __volatile__("csrw 0x83f, %1" : : "r"(x31), "r"(v) : "memory");
}

static inline void t_wait(uint64_t id)
{
    __asm__ __volatile__("csrw 0x830, %0" : : "r"(id) : "memory");
}

static inline uint64_t tensor_error(void)
{
    uint64_t v;
    __asm__ __volatile__("csrr %0, 0x808" : "=r"(v));
    return v;
}
#endif

static void put_status(const struct MpArgs* args, uint64_t hart, uint64_t cyc, uint64_t count, uint64_t sink)
{
    volatile struct MpStatus* s = (volatile struct MpStatus*)args->status + hart;
    s->cycles = cyc;
    s->count = count;
    s->sink = sink;
    s->hart = (uint32_t)hart;
    s->magic = MP_MAGIC;
}

static void run_program(const struct MpArgs* args, uint64_t hart)
{
    volatile uint64_t* ops = (volatile uint64_t*)MP_SCP_ADDR(0x7F, MP_SCP_OPS_OFFSET);
    volatile uint32_t* res = (volatile uint32_t*)MP_SCP_ADDR(0x7F, MP_SCP_RES_OFFSET);
    const uint64_t n = args->n_ops < MP_MAX_OPS ? args->n_ops : MP_MAX_OPS;
    const volatile uint64_t* src = (const volatile uint64_t*)args->ops;
    for (uint64_t i = 0; i < 2 * n; i++)
        ops[i] = src[i];
    // The copy pulled the op list through L2/L3; push it out so it cannot collide with the probes.
    for (uint64_t i = 0; i < 2 * n; i += 8)
        evict_line((uint64_t)&src[i], 3);
    __asm__ __volatile__("fence" ::: "memory");

    uint64_t sink = 0, nres = 0, dt = 0;
    const uint64_t t_start = cycles();
    for (uint64_t i = 0; i < n; i++) {
        const uint64_t w = ops[2 * i], a = ops[2 * i + 1];
        const uint64_t code = w & 0xFF, arg = w >> 8;
        if (code == OP_END)
            break;
        switch (code) {
        case OP_LOAD:
            sink ^= load_wait(a);
            break;
        case OP_TLOAD2: {  // issue a load of addr and, one cycle later, a timed load of addr2 (from the next op)
            const uint64_t a2 = ops[2 * i + 3];
            uint64_t t0, t1, v1, v2;
            __asm__ __volatile__(RDCYC("%0") "ld %2, 0(%4)\n ld %3, 0(%5)\n addi %3, %3, 1\n" RDCYC("%1")
                                 "addi %2, %2, 1\n"
                                 : "=&r"(t0), "=&r"(t1), "=&r"(v1), "=&r"(v2) : "r"(a), "r"(a2) : "memory");
            sink ^= v1 ^ v2;
            i++;  // the next op only carried addr2
            if (nres < MP_MAX_RESULTS)
                res[nres++] = (uint32_t)(fixcyc(t1) - fixcyc(t0));
            break;
        }
        case OP_TLOAD:
            sink ^= tload(a, &dt);
            if (nres < MP_MAX_RESULTS)
                res[nres++] = (uint32_t)dt;
            break;
        case OP_EVICT:
            evict_line(a, arg);
            break;
        case OP_TEVICT: {
            const uint64_t t0 = cycles();
            evict_line(a, arg);
            __asm__ __volatile__("fence" ::: "memory");
            const uint64_t t1 = cycles();
            if (nres < MP_MAX_RESULTS)
                res[nres++] = (uint32_t)(t1 - t0);
            break;
        }
        case OP_FENCE:
            __asm__ __volatile__("fence" ::: "memory");
            break;
        case OP_TNOP: {
            uint64_t t0, t1;
            __asm__ __volatile__(RDCYC("%0") "addi %0, %0, 0\n" RDCYC("%1") : "=&r"(t0), "=&r"(t1));
            if (nres < MP_MAX_RESULTS)
                res[nres++] = (uint32_t)(fixcyc(t1) - fixcyc(t0));
            break;
        }
        case OP_RAW: {  // raw counter pairs, for studying the counter itself
            uint64_t t0, t1, c0, c1;
            __asm__ __volatile__(RDCYC("%0") "addi %0, %0, 0\n" RDCYC("%1") : "=&r"(t0), "=&r"(t1));
            if (arg == 1)  // the standard cycle CSR; it traps in U-mode on this firmware
                __asm__ __volatile__("csrr %0, cycle\n addi %0, %0, 0\n csrr %1, cycle\n" : "=&r"(c0), "=&r"(c1));
            else
                c0 = c1 = 0;
            if (nres + 4 <= MP_MAX_RESULTS) {
                res[nres++] = (uint32_t)t0;
                res[nres++] = (uint32_t)t1;
                res[nres++] = (uint32_t)c0;
                res[nres++] = (uint32_t)c1;
            }
            break;
        }
        case OP_TFENCE: {
            const uint64_t t0 = cycles();
            __asm__ __volatile__("fence" ::: "memory");
            const uint64_t t1 = cycles();
            if (nres < MP_MAX_RESULTS)
                res[nres++] = (uint32_t)(t1 - t0);
            break;
        }
        case OP_DELAY: {
            const uint64_t t0 = cycles();
            while (cycles() - t0 < arg) {
            }
            break;
        }
        case OP_STAMP:
            if (nres < MP_MAX_RESULTS)
                res[nres++] = (uint32_t)cycles();
            break;
        case OP_MSREAD:  // a memory shire's counter through the firmware (syscall 10): arg = ms | pmc << 8
            if (nres < MP_MAX_RESULTS)
                res[nres++] = (uint32_t)syscall(SYSCALL_PMC_MS_SAMPLE, arg & 0xFF, (arg >> 8) & 0xFF, 0);
            break;
        case OP_STORE:
            *(volatile uint64_t*)a = arg;
            break;
#ifdef MP_EXT
        case OP_TTLOAD: {  // one TensorLoad, timed from issue until TensorWait returns (the last line has landed)
            const uint64_t lines = (arg & 0xF) + 1, stride = (arg >> 8) ? (arg >> 8) : 64;
            const uint64_t t0 = cycles();
            t_load(0, a, lines, stride, 0);
            t_wait(0);
            const uint64_t t1 = cycles();
            if (nres < MP_MAX_RESULTS)
                res[nres++] = (uint32_t)(t1 - t0);
            break;
        }
        case OP_TERR:
            if (nres < MP_MAX_RESULTS)
                res[nres++] = (uint32_t)tensor_error();
            break;
#endif
        default:
            break;
        }
    }
    const uint64_t t_end = cycles();

    volatile uint32_t* out = (volatile uint32_t*)args->results;
    for (uint64_t i = 0; i < nres; i++)
        out[i] = res[i];
    __asm__ __volatile__("fence" ::: "memory");
    put_status(args, hart, t_end - t_start, nres, sink);
}

static void run_loop(const struct MpArgs* args, uint64_t m, uint64_t hart)
{
    uint64_t addr[MP_LOOP_MAX_ADDRS];
    const uint64_t k = args->n_addrs < MP_LOOP_MAX_ADDRS ? args->n_addrs : MP_LOOP_MAX_ADDRS;
    const volatile uint64_t* table = (const volatile uint64_t*)args->table + m * args->n_addrs;
    for (uint64_t j = 0; j < k; j++)
        addr[j] = table[j];
    const uint64_t level = args->level;

    uint64_t sink = 0;
    if (args->stride) {
        const uint64_t base = addr[0], stride = args->stride, n = args->n_lines;
        const uint64_t t0 = cycles();
        for (uint64_t it = 0; it < args->iters; it++) {
            // Unrolled by 4 (n is a multiple of 4): the same instructions for every pattern, so power
            // differences between patterns come from the memory level alone. Each addi waits for its data.
            uint64_t a = base, j = n, v;
#define MP_STEP "ld %0, 0(%1)\n add %1, %1, %4\n addi %0, %0, 1\n xor %2, %2, %0\n"
            __asm__ __volatile__("1: " MP_STEP MP_STEP MP_STEP MP_STEP " addi %3, %3, -4\n bnez %3, 1b\n"
                                 : "=&r"(v), "+r"(a), "+r"(sink), "+r"(j) : "r"(stride) : "memory");
#undef MP_STEP
        }
        const uint64_t t1 = cycles();
        put_status(args, hart, t1 - t0, args->iters * n, sink);
        return;
    }
    const uint64_t t0 = cycles();
    for (uint64_t it = 0; it < args->iters; it++) {
        for (uint64_t j = 0; j < k; j++) {
            sink ^= load_wait(addr[j]);
            if (level < 4)
                evict_line(addr[j], level);
        }
    }
    const uint64_t t1 = cycles();
    put_status(args, hart, t1 - t0, args->iters * k, sink);
}

#ifdef MP_EXT
// Bandwidth of a TensorLoad stream (tools/claims-v3/memp2, R43): no evicts, two loads in flight, the same loop for
// every stride, source and neighbourhood count. The sink word of the status line carries tensor_error before the
// first tensor op (high 32 bits) and at the end (low 32 bits). MP_TL_WARM (the arena source): every line of the span
// is first loaded by scalar loads, so the stream reads L2-resident lines whether or not the L2 keeps the lines a
// TensorLoad fetched (R36).
static void run_tloop(const struct MpArgs* args, uint64_t m, uint64_t hart)
{
    const uint64_t base = ((const volatile uint64_t*)args->table)[m];
    const uint64_t lines = args->tl_lines, stride = args->stride, step = args->tl_step, span = args->tl_span;
    const uint64_t iters = args->iters;
    const uint64_t err0 = tensor_error();
    if (args->tl_flags & MP_TL_WARM) {
        for (uint64_t o = 0; o < span; o += 64)
            (void)load_wait(base + o);
        __asm__ __volatile__("fence" ::: "memory");
    }
    uint64_t off = 0;
    const uint64_t t0 = cycles();
    for (uint64_t i = 0; i < iters; ++i) {
        const uint64_t id = i & 1;
        if (i >= 2)
            t_wait(id);
        t_load(id * 16, base + off, lines, stride, id);
        off += step;
        if (off >= span)
            off = 0;
    }
    t_wait(0);
    t_wait(1);
    const uint64_t t1 = cycles();
    put_status(args, hart, t1 - t0, iters, ((err0 & 0xFFFFFFFFull) << 32) | (tensor_error() & 0xFFFFFFFFull));
}
#endif

int64_t entry_point(const struct MpArgs* args)
{
    const uint64_t hart = get_hart_id();
    const uint64_t shire = hart >> 6;
    const uint64_t mask = args->shire_mask;
    if (shire >= 32 || !((mask >> shire) & 1))
        return 0;

    if (args->mode == MP_PROGRAM) {
        if (hart == args->hart)
            run_program(args, hart);
        return 0;
    }
    if (args->mode == MP_LOOP) {
        if (hart & 1)
            return 0;
        const uint64_t m = (uint64_t)__builtin_popcountll(mask & ((1ull << shire) - 1)) * 32 + ((hart >> 1) & 31);
        run_loop(args, m, hart);
        return 0;
    }
#ifdef MP_EXT
    if (args->mode == MP_TLOOP) {
        const uint64_t mis = (hart >> 1) & 31;
        if ((hart & 1) || !((args->minion_mask >> mis) & 1))
            return 0;
        const uint64_t m = (uint64_t)__builtin_popcountll(mask & ((1ull << shire) - 1)) * 32 + mis;
        run_tloop(args, m, hart);
        return 0;
    }
#endif
    return 0;
}
