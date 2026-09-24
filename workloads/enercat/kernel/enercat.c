/*-------------------------------------------------------------------------
 * The energy catalogue: one kind of operation, flat out, until a deadline.
 *
 * Every participating hart loads eight source operands from its own 256 B
 * buffer (the host fills it with zeros, one constant, or random data), then
 * runs the chosen pattern in blocks of 64 operations, checking the cycle
 * counter between blocks, and reports how many blocks it completed. Sources
 * are never overwritten and sinks are never read, so the values stay what the
 * host put there: the operand switching the unit sees is "the next pair of
 * operands", op after op, which is what a real stream of data looks like.
 *
 * The host measures board power while this runs; energy per operation is
 * what is left over idle, divided by the rate.
 *-------------------------------------------------------------------------*/

#include <stdbool.h>
#include <stdint.h>
#include "etsoc/isa/hart.h"
#include "enercat_args.h"
#include "../enercat_modes.h"

int64_t entry_point(const struct EcArgs* args);

#define VSINK "f8", "f9", "f10", "f11", "f12", "f13", "f14", "f15"
#define VSRC "f0", "f1", "f2", "f3", "f4", "f5", "f6", "f7"

static inline uint64_t cycles(void)
{
    uint64_t v;
    __asm__ __volatile__(".p2align 4\n csrr %0, hpmcounter3\n csrr %0, hpmcounter3\n"
                         " csrr %0, hpmcounter3\n csrr %0, hpmcounter3\n" : "=r"(v));
    return v;
}

// f0..f7 = the eight 32 B vectors of the source buffer; all eight lanes enabled.
static inline void load_vsrc(uint64_t buf)
{
    __asm__ __volatile__("mov.m.x m0, zero, 0xff\n"
                         "flw.ps f0, 0(%0)\n flw.ps f1, 32(%0)\n flw.ps f2, 64(%0)\n flw.ps f3, 96(%0)\n"
                         "flw.ps f4, 128(%0)\n flw.ps f5, 160(%0)\n flw.ps f6, 192(%0)\n flw.ps f7, 224(%0)\n"
                         : : "r"(buf) : "memory", VSRC);
}

/* Eight scalar ops on rotating source pairs. The results are early-clobber outputs GCC may not fold. */
#define IBLOCK(op)                                                                                        \
    do {                                                                                                  \
        uint64_t d0, d1, d2, d3, d4, d5, d6, d7;                                                          \
        __asm__ __volatile__(op " %0, %8, %9\n" op " %1, %10, %11\n" op " %2, %12, %13\n"                 \
                             op " %3, %14, %15\n" op " %4, %9, %10\n" op " %5, %11, %12\n"                \
                             op " %6, %13, %14\n" op " %7, %15, %8\n"                                     \
                             : "=&r"(d0), "=&r"(d1), "=&r"(d2), "=&r"(d3), "=&r"(d4), "=&r"(d5),         \
                               "=&r"(d6), "=&r"(d7)                                                       \
                             : "r"(s0), "r"(s1), "r"(s2), "r"(s3), "r"(s4), "r"(s5), "r"(s6), "r"(s7));   \
    } while (0)

#define FBLOCK(op)                                                                                        \
    do {                                                                                                  \
        float d0, d1, d2, d3, d4, d5, d6, d7;                                                             \
        __asm__ __volatile__(op " %0, %8, %9\n" op " %1, %10, %11\n" op " %2, %12, %13\n"                 \
                             op " %3, %14, %15\n" op " %4, %9, %10\n" op " %5, %11, %12\n"                \
                             op " %6, %13, %14\n" op " %7, %15, %8\n"                                     \
                             : "=&f"(d0), "=&f"(d1), "=&f"(d2), "=&f"(d3), "=&f"(d4), "=&f"(d5),         \
                               "=&f"(d6), "=&f"(d7)                                                       \
                             : "f"(g0), "f"(g1), "f"(g2), "f"(g3), "f"(g4), "f"(g5), "f"(g6), "f"(g7));   \
    } while (0)

#define FMABLOCK(op)                                                                                      \
    do {                                                                                                  \
        float d0, d1, d2, d3, d4, d5, d6, d7;                                                             \
        __asm__ __volatile__(op " %0, %8, %9, %10\n" op " %1, %10, %11, %12\n" op " %2, %12, %13, %14\n"  \
                             op " %3, %14, %15, %8\n" op " %4, %9, %10, %11\n" op " %5, %11, %12, %13\n"  \
                             op " %6, %13, %14, %15\n" op " %7, %15, %8, %9\n"                            \
                             : "=&f"(d0), "=&f"(d1), "=&f"(d2), "=&f"(d3), "=&f"(d4), "=&f"(d5),         \
                               "=&f"(d6), "=&f"(d7)                                                       \
                             : "f"(g0), "f"(g1), "f"(g2), "f"(g3), "f"(g4), "f"(g5), "f"(g6), "f"(g7));   \
    } while (0)

// Eight vector ops, sources f0..f7 rotating, sinks f8..f15.
#define VBLOCK(op)                                                                                        \
    __asm__ __volatile__(op " f8, f0, f1\n" op " f9, f2, f3\n" op " f10, f4, f5\n" op " f11, f6, f7\n"    \
                         op " f12, f1, f2\n" op " f13, f3, f4\n" op " f14, f5, f6\n" op " f15, f7, f0\n"   \
                         : : : VSINK)
#define VMABLOCK(op)                                                                                      \
    __asm__ __volatile__(op " f8, f0, f1, f2\n" op " f9, f2, f3, f4\n" op " f10, f4, f5, f6\n"            \
                         op " f11, f6, f7, f0\n" op " f12, f1, f2, f3\n" op " f13, f3, f4, f5\n"          \
                         op " f14, f5, f6, f7\n" op " f15, f7, f0, f1\n"                                  \
                         : : : VSINK)
#define V1BLOCK(op)                                                                                       \
    __asm__ __volatile__(op " f8, f0\n" op " f9, f1\n" op " f10, f2\n" op " f11, f3\n"                    \
                         op " f12, f4\n" op " f13, f5\n" op " f14, f6\n" op " f15, f7\n"                   \
                         : : : VSINK)

// Variadic, because the generated blocks carry commas of their own.
#define RUN(...)                                                                                          \
    do {                                                                                                  \
        const uint64_t t0 = cycles(), deadline = t0 + a->window;                                          \
        do {                                                                                              \
            __VA_ARGS__; __VA_ARGS__; __VA_ARGS__; __VA_ARGS__;                                           \
            __VA_ARGS__; __VA_ARGS__; __VA_ARGS__; __VA_ARGS__;                                           \
            ++iters;                                                                                      \
        } while (cycles() < deadline);                                                                    \
        cyc = cycles() - t0;                                                                              \
    } while (0)

static inline void t_load(uint64_t dst, uint64_t addr, uint64_t lines, uint64_t id)
{
    const uint64_t v = ((dst & 0x3F) << 53) | (addr & 0xFFFFFFFFFFC0ull) | ((lines - 1) & 0xF);
    register uint64_t x31 __asm__("x31") = 64ull | (id & 1);
    __asm__ __volatile__("csrw 0x83f, %1" : : "r"(x31), "r"(v) : "memory");
}

static inline void t_store(uint64_t start_reg, uint64_t rows, uint64_t addr, uint64_t stride)
{
    const uint64_t v = ((start_reg & 0x1F) << 57) | ((1ull & 0x3) << 55) | (addr & 0xFFFFFFFFFFF0ull) |
                       (((rows - 1) & 0xF) << 51);
    register uint64_t x31 __asm__("x31") = (stride & 0xFFFFFFFFFF0ull);
    __asm__ __volatile__("csrw 0x87f, %1" : : "r"(x31), "r"(v) : "memory");
}

static inline void t_wait(uint64_t id)
{
    __asm__ __volatile__("csrw 0x830, %0" : : "r"(id) : "memory");
}

int64_t entry_point(const struct EcArgs* a)
{
    const uint64_t hart = get_hart_id();
    const uint64_t shire = hart >> 6;
    if (shire >= 32 || !((a->shire_mask >> shire) & 1)) {
        return 0;
    }
    const uint64_t thread = hart & 1;
    const uint64_t minion_in_shire = (hart >> 1) & 31;
    const uint64_t mode = a->mode;
    const bool tensor = mode == EC_TSTORE || mode == EC_TSTORE_RAW || mode == EC_TSTORE_UNIQ || mode == EC_TLOAD || mode == EC_TLOAD_PAT;
    if (thread && (a->harts < 2 || tensor)) {
        return 0;
    }
    if (a->minion_mask && !((a->minion_mask >> minion_in_shire) & 1)) {
        return 0;
    }
    const uint64_t src = a->sources + hart * 256;
    const volatile uint64_t* sw = (const volatile uint64_t*)src;
    const uint64_t s0 = sw[0], s1 = sw[4], s2 = sw[8], s3 = sw[12], s4 = sw[16], s5 = sw[20], s6 = sw[24], s7 = sw[28];
    const volatile float* sf = (const volatile float*)src;
    const float g0 = sf[0], g1 = sf[8], g2 = sf[16], g3 = sf[24], g4 = sf[32], g5 = sf[40], g6 = sf[48], g7 = sf[56];
    uint64_t iters = 0, cyc = 0, bytes = 0;
    // Base of this hart's slice for the memory patterns: DRAM, own scratchpad, or a target shire's scratchpad.
    uint64_t slice_base = a->slice + hart * a->slice_bytes;
    if (a->scp == 0 && mode == EC_TLOAD_PAT && a->minion_mask) {
        // With a minion mask the host allocates one slice per PARTICIPANT, so index by rank among them:
        // shires below mine in the mask times minions per shire in the mask, plus minions below mine.
        const uint64_t per_shire = (uint64_t)__builtin_popcountll(a->minion_mask & 0xFFFFFFFFull);
        const uint64_t shires_below = (uint64_t)__builtin_popcountll(a->shire_mask & ((1ull << shire) - 1));
        const uint64_t minions_below = (uint64_t)__builtin_popcountll(a->minion_mask & ((1ull << minion_in_shire) - 1));
        slice_base = a->slice + (shires_below * per_shire + minions_below) * a->slice_bytes;
    }
    if (a->scp == 0 && (mode == EC_TLOAD_PAT || mode == EC_FLW_PAT)) {
        // Spread minions over the eight DRAM banks (PA[12:10]) so a per-hart stride that stays in one bank
        // does not put every hart in the same one. The host allocates 8 KB of slack per hart for this.
        slice_base += ((hart >> 1) & 7) * 1024;
    }
    if (a->scp == 1) {
        slice_base = EC_SCP_ADDR(EC_SCP_LOCAL, a->scp_off + minion_in_shire * a->slice_bytes);
    } else if (a->scp == 2) {
        const uint32_t tv = ((const volatile uint32_t*)a->targets)[shire];
        const uint64_t tgt = tv & 0xFFFFu, region = tv >> 16;   // region 1: the second reader's copy (EC_TSTORE_UNIQ)
        slice_base = EC_SCP_ADDR(tgt, a->scp_off + (region * 32 + minion_in_shire) * a->slice_bytes);
    }

    switch (mode) {
#include "enercat_ops.inc"

    case EC_TLOAD_PAT: {
        // `access_bytes` per tensor load (1 or 16 lines), `stride` apart, wrapping every `region` bytes.
        const uint64_t lines = a->access_bytes / 64;
        const uint64_t period = a->jump_every ? a->jump_every * a->stride + a->jump_bytes : a->stride;
        const uint64_t n = a->jump_every ? a->region / period * a->jump_every : a->region / a->stride;
        uint64_t p = slice_base, k = 0, q = 0;
        const uint64_t t0 = cycles(), deadline = t0 + a->window;
        do {
            for (int b = 0; b < 8; ++b, ++q) {
                const uint64_t id = q & 1;
                if (q >= 2) {
                    t_wait(id);
                }
                t_load(id * 16, p, lines, id);
                p += a->stride;
                if (a->jump_every && (k + 1) % a->jump_every == 0) {
                    p += a->jump_bytes;
                }
                if (++k == n) { k = 0; p = slice_base; }
            }
            ++iters;
        } while (cycles() < deadline);
        t_wait(0);
        t_wait(1);
        cyc = cycles() - t0;
        bytes = iters * 8 * a->access_bytes;
        break;
    }

    case EC_FLW_PAT: {
        // 32 B vector loads through the L1, `stride` apart: a stride of 64 misses on every line and uses
        // half of it, which is how the per-line fill cost is separated from the per-byte cost.
        __asm__ __volatile__("mov.m.x m0, zero, 0xff" : : : "memory");
        const uint64_t n = a->region / a->stride;
        uint64_t p = slice_base, k = 0;
        const uint64_t t0 = cycles(), deadline = t0 + a->window;
        do {
            for (int b = 0; b < 8; ++b) {
                __asm__ __volatile__("flw.ps f8, 0(%0)" : : "r"(p) : "memory", "f8");
                p += a->stride;
                if (++k == n) { k = 0; p = slice_base; }
            }
            ++iters;
        } while (cycles() < deadline);
        cyc = cycles() - t0;
        bytes = iters * 8 * 32;
        break;
    }
    case EC_SPIN:
        RUN(__asm__ __volatile__("addi t0, t0, 1\n addi t1, t1, 1\n addi t2, t2, 1\n addi t3, t3, 1\n"
                                 "addi t4, t4, 1\n addi t5, t5, 1\n addi t6, t6, 1\n addi t0, t0, 1\n"
                                 : : : "t0", "t1", "t2", "t3", "t4", "t5", "t6"));
        break;
    case EC_IADD: RUN(IBLOCK("add")); break;
    case EC_IMUL: RUN(IBLOCK("mul")); break;
    case EC_IXOR: RUN(IBLOCK("xor")); break;
    case EC_FADD_S: RUN(FBLOCK("fadd.s")); break;
    case EC_FMUL_S: RUN(FBLOCK("fmul.s")); break;
    case EC_FMADD_S: RUN(FMABLOCK("fmadd.s")); break;
    case EC_FADD_PS: load_vsrc(src); RUN(VBLOCK("fadd.ps")); break;
    case EC_FMUL_PS: load_vsrc(src); RUN(VBLOCK("fmul.ps")); break;
    case EC_FMADD_PS: load_vsrc(src); RUN(VMABLOCK("fmadd.ps")); break;
    case EC_IADD_PI: load_vsrc(src); RUN(VBLOCK("fadd.pi")); break;
    case EC_IMUL_PI: load_vsrc(src); RUN(VBLOCK("fmul.pi")); break;
    case EC_FEXP_PS: load_vsrc(src); RUN(V1BLOCK("fexp.ps")); break;
    case EC_FRCP_PS: load_vsrc(src); RUN(V1BLOCK("frcp.ps")); break;
    case EC_FSQRT_PS: load_vsrc(src); RUN(V1BLOCK("fsqrt.ps")); break;
    case EC_FDIV_PS: load_vsrc(src); RUN(VBLOCK("fdiv.ps")); break;

    case EC_LD_L1:
        load_vsrc(src);  // also warms the 256 B into the L1
        RUN(__asm__ __volatile__("flw.ps f8, 0(%0)\n flw.ps f9, 32(%0)\n flw.ps f10, 64(%0)\n flw.ps f11, 96(%0)\n"
                                 "flw.ps f12, 128(%0)\n flw.ps f13, 160(%0)\n flw.ps f14, 192(%0)\n flw.ps f15, 224(%0)\n"
                                 : : "r"(src) : "memory", VSINK));
        bytes = iters * 8 * 256;
        break;
    case EC_ST_L1:
        load_vsrc(src);
        RUN(__asm__ __volatile__("fsw.ps f0, 0(%0)\n fsw.ps f1, 32(%0)\n fsw.ps f2, 64(%0)\n fsw.ps f3, 96(%0)\n"
                                 "fsw.ps f4, 128(%0)\n fsw.ps f5, 160(%0)\n fsw.ps f6, 192(%0)\n fsw.ps f7, 224(%0)\n"
                                 : : "r"(src) : "memory"));
        bytes = iters * 8 * 256;
        break;

    case EC_ST_STREAM: {
        // 32 B vector stores marching through this hart's slice; the L1 write-back path to wherever the
        // slice's total footprint lands (with 2,048 harts x slice_bytes past the L3, that is DRAM).
        load_vsrc(src);
        const uint64_t base = a->slice + hart * a->slice_bytes, n = a->slice_bytes / 256;
        uint64_t p = base, k = 0;
        const uint64_t t0 = cycles(), deadline = t0 + a->window;
        do {
            for (int b = 0; b < 8; ++b) {
                __asm__ __volatile__("fsw.ps f0, 0(%0)\n fsw.ps f1, 32(%0)\n fsw.ps f2, 64(%0)\n fsw.ps f3, 96(%0)\n"
                                     "fsw.ps f4, 128(%0)\n fsw.ps f5, 160(%0)\n fsw.ps f6, 192(%0)\n fsw.ps f7, 224(%0)\n"
                                     : : "r"(p) : "memory");
                p += 256;
                if (++k == n) { k = 0; p = base; }
            }
            ++iters;
        } while (cycles() < deadline);
        cyc = cycles() - t0;
        bytes = iters * 8 * 256;
        break;
    }

    case EC_TSTORE: {
        // 16 rows x 32 B from f0..f15 per tensor store, marching through the slice; bypasses L1 and L2.
        load_vsrc(src);
        __asm__ __volatile__("fadd.ps f8, f0, f0\n fadd.ps f9, f1, f1\n fadd.ps f10, f2, f2\n fadd.ps f11, f3, f3\n"
                             "fadd.ps f12, f4, f4\n fadd.ps f13, f5, f5\n fadd.ps f14, f6, f6\n fadd.ps f15, f7, f7\n"
                             : : : VSINK);
        const uint64_t base = slice_base;
        const uint64_t n = a->slice_bytes / 512;
        uint64_t p = base, k = 0;
        const uint64_t t0 = cycles(), deadline = t0 + a->window;
        do {
            for (int b = 0; b < 8; ++b) {
                t_store(0, 16, p, 32);
                p += 512;
                if (++k == n) { k = 0; p = base; }
            }
            t_wait(8);
            ++iters;
        } while (cycles() < deadline);
        cyc = cycles() - t0;
        bytes = iters * 8 * 512;
        break;
    }

    case EC_TSTORE_RAW: {
        // The same store loop as EC_TSTORE, but f8..f15 come from the next 256 B of sources instead of being
        // doubles of f0..f7: the 512 B written per tensor store is the host's image, byte for byte.
        load_vsrc(src);
        __asm__ __volatile__("flw.ps f8, 0(%0)\n flw.ps f9, 32(%0)\n flw.ps f10, 64(%0)\n flw.ps f11, 96(%0)\n"
                             "flw.ps f12, 128(%0)\n flw.ps f13, 160(%0)\n flw.ps f14, 192(%0)\n flw.ps f15, 224(%0)\n"
                             : : "r"(src + 256) : "memory", VSINK);
        const uint64_t base = slice_base;
        const uint64_t n = a->slice_bytes / 512;
        uint64_t p = base, k = 0;
        const uint64_t t0 = cycles(), deadline = t0 + a->window;
        do {
            for (int b = 0; b < 8; ++b) {
                t_store(0, 16, p, 32);
                p += 512;
                if (++k == n) { k = 0; p = base; }
            }
            t_wait(8);
            ++iters;
        } while (cycles() < deadline);
        cyc = cycles() - t0;
        bytes = iters * 8 * 512;
        break;
    }

    case EC_TSTORE_UNIQ: {
        // Fill both regions of this minion block by block, each block from its own 512 B of the DRAM buffer; wait for
        // every store before reloading its registers, since a tensor store reads f0..f15 after it is issued.
        const uint64_t g = shire * 32 + minion_in_shire;
        const uint64_t blocks = a->slice_bytes / 512;
        const uint64_t t0 = cycles();
        for (uint64_t r = 0; r < 2; ++r) {
            const uint64_t dst = a->scp ? EC_SCP_ADDR(EC_SCP_LOCAL, a->scp_off + (r * 32 + minion_in_shire) * a->slice_bytes)
                                        : a->slice + (g * 2 + r) * a->slice_bytes;
            const uint64_t srcb = a->sources + (g * 2 + r) * a->slice_bytes;
            for (uint64_t k = 0; k < blocks; ++k) {
                load_vsrc(srcb + k * 512);
                __asm__ __volatile__("flw.ps f8, 0(%0)\n flw.ps f9, 32(%0)\n flw.ps f10, 64(%0)\n flw.ps f11, 96(%0)\n"
                                     "flw.ps f12, 128(%0)\n flw.ps f13, 160(%0)\n flw.ps f14, 192(%0)\n flw.ps f15, 224(%0)\n"
                                     : : "r"(srcb + k * 512 + 256) : "memory", VSINK);
                t_store(0, 16, dst + k * 512, 32);
                t_wait(8);
            }
        }
        cyc = cycles() - t0;
        iters = 1;
        bytes = 2 * a->slice_bytes;
        break;
    }

    case EC_TLOAD: {
        // 1 KB tensor loads into the L1 scratchpad, two in flight, marching through the slice.
        const uint64_t base = slice_base;
        const uint64_t n = a->slice_bytes / 1024;
        uint64_t p = base, k = 0, q = 0;
        const uint64_t t0 = cycles(), deadline = t0 + a->window;
        do {
            for (int b = 0; b < 8; ++b, ++q) {
                const uint64_t id = q & 1;
                if (q >= 2) {
                    t_wait(id);
                }
                t_load(id * 16, p, 16, id);
                p += 1024;
                if (++k == n) { k = 0; p = base; }
            }
            ++iters;
        } while (cycles() < deadline);
        t_wait(0);
        t_wait(1);
        cyc = cycles() - t0;
        bytes = iters * 8 * 1024;
        break;
    }
    default:
        return 0;
    }

    volatile struct EcResult* r = (volatile struct EcResult*)a->results + hart;
    r->cycles = cyc;
    r->iters = iters;
    r->bytes = bytes;
    r->hart = (uint32_t)hart;
    r->magic = EC_MAGIC;
    return 0;
}
