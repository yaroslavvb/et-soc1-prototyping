/*-------------------------------------------------------------------------
 * Does shire-to-shire communication beat main memory? (see ../README.md)
 *
 *  OC_WRITE  every minion writes a known 1 KB pattern into its own shire's L2
 *            scratchpad, by tensor store (bypasses L1 and L2) or by plain
 *            vector stores (through L1), and checksums what it reads back.
 *  OC_READ   every minion checksums the pattern a different shire wrote. Run as
 *            a second launch, so this asks only whether the data landed.
 *  OC_RELAY  the experiment. K stages over a slab per shire. Each stage reads
 *            the previous stage's output and writes its own. The only thing that
 *            changes between the three media is where that intermediate lives:
 *            DRAM, the shire's own scratchpad, or the next shire's scratchpad.
 *
 * Timing uses the minion cycle counter (hpmcounter3). Each minion writes its
 * result to its own 64 B line, because the L1s are not coherent.
 *-------------------------------------------------------------------------*/

#include <stdbool.h>
#include <stdint.h>
#include "etsoc/isa/esr_defines.h"
#include "etsoc/isa/hart.h"
#include "onchip_args.h"

int64_t entry_point(const struct OcArgs* args);

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

// TensorLoad: `lines` 64 B lines from addr into the L1 scratchpad at line dst, bypassing the L1 cache.
static inline void t_load(uint64_t dst, uint64_t addr, uint64_t lines, uint64_t id)
{
    const uint64_t v = ((dst & 0x3F) << 53) | (addr & 0xFFFFFFFFFFC0ull) | ((lines - 1) & 0xF);
    register uint64_t x31 __asm__("x31") = 64ull | (id & 1);
    __asm__ __volatile__("csrw 0x83f, %1" : : "r"(x31), "r"(v) : "memory");
}

/* TensorLoadL2Scp: `lines` lines from addr into THIS shire's L2 scratchpad at scratchpad line dst,
   bypassing L1 and L2. The source may be DRAM or another shire's scratchpad, which is the whole point:
   it is a pull that no cache can make stale. TensorWait 2 + id. */
static inline void t_load_l2scp(uint64_t dst, uint64_t addr, uint64_t lines, uint64_t id)
{
    const uint64_t v = ((dst & 0x1FFFCull) << 46) | ((dst & 3) << 4) | (addr & 0xFFFFFFFFFFC0ull) | ((lines - 1) & 0xF);
    register uint64_t x31 __asm__("x31") = 64ull | (id & 1);
    __asm__ __volatile__("csrw 0x85f, %1" : : "r"(x31), "r"(v) : "memory");
}

/* TensorStore: `rows` rows of 32 B from f[start..start+rows-1] to addr, stride bytes apart, bypassing the
   L1 and L2 caches (PRM 9.4: a row is 16*SIZE+16 bytes, so SIZE = 1 gives the 32 B of one vector register). */
static inline void t_store(uint64_t start_reg, uint64_t rows, uint64_t addr, uint64_t stride)
{
    const uint64_t v = ((start_reg & 0x1F) << 57) | ((1ull & 0x3) << 55) | (addr & 0xFFFFFFFFFFF0ull) |
                       (((rows - 1) & 0xF) << 51);
    register uint64_t x31 __asm__("x31") = (stride & 0xFFFFFFFFFF0ull);
    __asm__ __volatile__("csrw 0x87f, %1" : : "r"(x31), "r"(v) : "memory");
}

static inline void t_wait(uint64_t id)
{
    __asm__ __volatile__("csrw 0x830, %0" : : "r"(id) : "memory", FREGS);
}

// Every lane of f0..f15 = 0.0f.
// Every lane of f0..f15 = the float whose bits are `bits`.
static inline void bcast16(uint32_t bits)
{
    const uint64_t z = bits;
    __asm__ __volatile__("mov.m.x m0, zero, 0xff\n"
                         "fbcx.ps f0, %0\n fbcx.ps f1, %0\n fbcx.ps f2, %0\n fbcx.ps f3, %0\n"
                         "fbcx.ps f4, %0\n fbcx.ps f5, %0\n fbcx.ps f6, %0\n fbcx.ps f7, %0\n"
                         "fbcx.ps f8, %0\n fbcx.ps f9, %0\n fbcx.ps f10, %0\n fbcx.ps f11, %0\n"
                         "fbcx.ps f12, %0\n fbcx.ps f13, %0\n fbcx.ps f14, %0\n fbcx.ps f15, %0\n"
                         : : "r"(z) : "memory", FREGS);
}

// Every lane of f0..f15 = its own value, so a block that came from the wrong place is obvious.
static inline void fill16(uint32_t base)
{
    __asm__ __volatile__("mov.m.x m0, zero, 0xff" : : : "memory");
#define F(n) __asm__ __volatile__("fbcx.ps f" #n ", %0" : : "r"((uint64_t)(base + (n))) : FREGS)
    F(0); F(1); F(2); F(3); F(4); F(5); F(6); F(7);
    F(8); F(9); F(10); F(11); F(12); F(13); F(14); F(15);
#undef F
}

/* Wait for one credit on counter 1 of this hart, by polling FCCNB (CSR 0xCC0, counter 1 in bits 31:16)
   rather than blocking on the FCC CSR: a credit that never arrives then fails the run instead of holding
   the hart until the card is reset. */
static bool take_credit1(uint64_t limit)
{
    for (uint64_t i = 0; i < limit; ++i) {
        uint64_t v;
        __asm__ __volatile__("csrr %0, 0xcc0" : "=r"(v) : : "memory");
        if ((v >> 16) & 0xFFFF) {
            __asm__ __volatile__("csrw 0x821, %0" : : "r"(1ull) : "memory");
            return true;
        }
    }
    return false;
}

static inline uint32_t amoadd_g(volatile uint32_t* p, uint32_t v)
{
    uint32_t old;
    __asm__ __volatile__("amoaddg.w %0, %1, (%2)" : "=r"(old) : "r"(v), "r"(p) : "memory");
    return old;
}

/* Chip-wide barrier, the shape workloads/nocbench measures at about 5,000 cycles: the 32 minions of a shire
   meet in its fast local barrier, the last one adds one to a counter, and the one shire that sees the final
   count releases every shire with one credit store each. Exactly one global atomic per shire per barrier and
   nobody spins on it, which matters: 24 minions polling one line is enough to stop that line's home shire
   getting any memory of its own (docs/findings/17-hot-line.md). */
static bool chip_barrier(const struct OcArgs* a, uint64_t shires, uint64_t gen)
{
    uint64_t last;
    __asm__ __volatile__("csrrw %0, 0x820, %1" : "=r"(last) : "r"((31ull << 5) | 29) : "memory");
    if (last) {
        const uint32_t seen = amoadd_g((volatile uint32_t*)a->counter, 1) + 1;
        if (seen == (uint32_t)((gen + 1) * shires)) {
            for (uint64_t s = 0; s < 32; ++s) {
                if ((a->shire_mask >> s) & 1) {
                    *((volatile uint64_t*)ESR_SHIRE(s, FCC_CREDINC_0) + 1) = 0xFFFFFFFFull;
                }
            }
        }
    }
    return take_credit1(a->poll_limit);
}

static void put(const struct OcArgs* a, uint64_t minion, uint64_t cyc, uint64_t sum, uint64_t bytes,
                uint32_t errors)
{
    volatile struct OcResult* r = (volatile struct OcResult*)a->results + minion;
    r->cycles = cyc;
    r->checksum = sum;
    r->bytes = bytes;
    r->minion = (uint32_t)minion;
    r->errors = errors;
    r->magic = OC_MAGIC;
}

// Sum of the 256 uint32 of a 1 KB block, read with plain loads.
static uint64_t checksum1k(uint64_t addr)
{
    const volatile uint32_t* p = (const volatile uint32_t*)addr;
    uint64_t s = 0;
    for (uint64_t i = 0; i < OC_PROBE_BLOCK / 4; ++i) {
        s += p[i];
    }
    return s;
}


/* Load 16 vector registers (512 B) from addr, add 1.0 to every lane `work` times, and tensor-store them to
   dst. The store bypasses the L1 and L2 caches, so what the next shire reads cannot be a stale line. */
static inline void relay_block(uint64_t addr, uint64_t dst, uint64_t work)
{
    __asm__ __volatile__(
        "flw.ps f0, 0(%0)\n   flw.ps f1, 32(%0)\n  flw.ps f2, 64(%0)\n  flw.ps f3, 96(%0)\n"
        "flw.ps f4, 128(%0)\n flw.ps f5, 160(%0)\n flw.ps f6, 192(%0)\n flw.ps f7, 224(%0)\n"
        "flw.ps f8, 256(%0)\n flw.ps f9, 288(%0)\n flw.ps f10, 320(%0)\n flw.ps f11, 352(%0)\n"
        "flw.ps f12, 384(%0)\n flw.ps f13, 416(%0)\n flw.ps f14, 448(%0)\n flw.ps f15, 480(%0)\n"
        : : "r"(addr) : "memory", FREGS);
    for (uint64_t w = 0; w < work; ++w) {
        __asm__ __volatile__(
            "fadd.ps f0, f0, f16\n fadd.ps f1, f1, f16\n fadd.ps f2, f2, f16\n fadd.ps f3, f3, f16\n"
            "fadd.ps f4, f4, f16\n fadd.ps f5, f5, f16\n fadd.ps f6, f6, f16\n fadd.ps f7, f7, f16\n"
            "fadd.ps f8, f8, f16\n fadd.ps f9, f9, f16\n fadd.ps f10, f10, f16\n fadd.ps f11, f11, f16\n"
            "fadd.ps f12, f12, f16\n fadd.ps f13, f13, f16\n fadd.ps f14, f14, f16\n fadd.ps f15, f15, f16\n"
            : : : FREGS);
    }
    t_store(0, 16, dst, 32);
}

// The k-th participating shire, counting from 0.
static inline uint64_t nth_shire(uint64_t mask, uint64_t k)
{
    for (uint64_t s = 0; s < 32; ++s) {
        if ((mask >> s) & 1) {
            if (k-- == 0) {
                return s;
            }
        }
    }
    return 0;
}

/* The participating shire `back` places before s round the ring. The ring is over the shires in the mask,
   not over all 32, so a partial launch still hands each slab to a shire that is actually running. */
static inline uint64_t ring_prev(uint64_t mask, uint64_t s, uint64_t back)
{
    const uint64_t n = (uint64_t)__builtin_popcountll(mask);
    const uint64_t idx = (uint64_t)__builtin_popcountll(mask & ((1ull << s) - 1));
    return nth_shire(mask, (idx + n - (back % n)) % n);
}

// Base address of buffer b of shire s, for this medium. OC_MEM_HOP reads the shire before it in the ring.
static inline uint64_t buf_addr(const struct OcArgs* a, uint64_t medium, uint64_t s, uint64_t b, bool read)
{
    const uint64_t off = (b & 1) ? a->scp_b : a->scp_a;
    if (medium == OC_MEM_DRAM) {
        return ((b & 1) ? a->dram_b : a->dram_a) + s * a->stage_bytes;
    }
    if (medium == OC_MEM_SCP) {
        return OC_SCP_ADDR(OC_SCP_LOCAL, off);
    }
    return read ? OC_SCP_ADDR(ring_prev(a->shire_mask, s, a->hop_dist ? a->hop_dist : 1), off)
                : OC_SCP_ADDR(OC_SCP_LOCAL, off);
}

int64_t entry_point(const struct OcArgs* args)
{
    const uint64_t hart = get_hart_id();
    const uint64_t shire = hart >> 6;
    if ((hart & 1) || shire >= 32 || !((args->shire_mask >> shire) & 1)) {
        return 0;  // tensor ops are hart 0 only
    }
    const uint64_t j = (hart >> 1) & 31;  // minion in shire
    const uint64_t minion = shire * 32 + j;
    const uint64_t off = OC_PROBE_OFF + j * OC_PROBE_BLOCK;

    if (args->mode == OC_WRITE) {
        const uint64_t dst = OC_SCP_ADDR(OC_SCP_LOCAL, off);
        const uint32_t base = OC_PAT(shire, j, 0);
        const uint64_t t0 = cycles();
        if (args->method == 0) {
            // Two tensor stores of 16 rows x 32 B, which bypass the L1 and L2 caches.
            fill16(base);
            t_store(0, 16, dst, 32);
            fill16(base + 16);
            t_store(0, 16, dst + 512, 32);
            t_wait(8);  // TENSOR_STORE_WAIT
        } else {
            // Plain vector stores, which go through the L1 write-back cache.
            volatile uint32_t* p = (volatile uint32_t*)dst;
            for (uint64_t k = 0; k < OC_PROBE_BLOCK / 4; ++k) {
                p[k] = base + (uint32_t)(k / 8);
            }
            __asm__ __volatile__("fence" ::: "memory");
        }
        const uint64_t t1 = cycles();
        put(args, minion, t1 - t0, checksum1k(dst), OC_PROBE_BLOCK, 0);
        return 0;
    }

    if (args->mode == OC_READ) {
        const uint64_t src_shire = (shire + args->shift) % 32;
        const uint64_t src = OC_SCP_ADDR(src_shire, off);
        uint32_t errors = 0;
        const volatile uint32_t* p = (const volatile uint32_t*)src;
        const uint32_t base = OC_PAT(src_shire, j, 0);
        const uint64_t t0 = cycles();
        uint64_t s = 0;
        for (uint64_t k = 0; k < OC_PROBE_BLOCK / 4; ++k) {
            const uint32_t v = p[k];
            s += v;
            if (v != base + (uint32_t)(k / 8)) {
                ++errors;
            }
        }
        const uint64_t t1 = cycles();
        put(args, minion, t1 - t0, s, OC_PROBE_BLOCK, errors);
        return 0;
    }


    if (args->mode == OC_RELAY) {
        const uint64_t medium = args->medium, work = args->work, stages = args->stages;
        const uint64_t chunk = args->stage_bytes / 32;        // bytes this minion owns
        const uint64_t blocks = chunk / 512;                  // 16 vector registers per block
        const uint64_t shires = (uint64_t)__builtin_popcountll(args->shire_mask);
        // f16 = 1.0f in every lane, the value each pass adds.
        __asm__ __volatile__("mov.m.x m0, zero, 0xff" : : : "memory");
        __asm__ __volatile__("fbcx.ps f16, %0" : : "r"((uint64_t)0x3F800000u) : FREGS);

        if (args->shift == 1) { put(args, minion, chunk, blocks, shires, 100); return 0; }
        // Stage -1, untimed: fill buffer 0 with a known pattern so all three media start the same way.
        {
            // A shire-dependent starting value, so the final contents say which shire the data came from.
            const float f0v = (float)(uint32_t)shire;
            uint32_t bits;
            __builtin_memcpy(&bits, &f0v, 4);
            const uint64_t dst = buf_addr(args, medium, shire, 0, false) + j * chunk;
            bcast16(bits);
            for (uint64_t b = 0; b < blocks; ++b) {
                t_store(0, 16, dst + b * 512, 32);
            }
            t_wait(8);
        }
        if (args->shift == 2) { put(args, minion, 0, 0, 0, 101); return 0; }
        if (!chip_barrier(args, shires, 0)) {
            put(args, minion, 0, 0, 0, 1);
            return 0;
        }

        if (args->shift == 3) { put(args, minion, 0, 0, 0, 102); return 0; }
        const uint64_t t0 = cycles();
        for (uint64_t k = 0; k < stages; ++k) {
            const uint64_t src = buf_addr(args, medium, shire, k, true) + j * chunk;
            const uint64_t dst = buf_addr(args, medium, shire, k + 1, false) + j * chunk;
            for (uint64_t b = 0; b < blocks; ++b) {
                relay_block(src + b * 512, dst + b * 512, work);
            }
            t_wait(8);
            if (!chip_barrier(args, shires, k + 1)) {
                put(args, minion, cycles() - t0, 0, 0, 2);
                return 0;
            }
        }
        const uint64_t t1 = cycles();

        // Every element should now be stages * work. Sum what is actually there.
        const uint64_t fin = buf_addr(args, medium, shire, stages, false) + j * chunk;
        const volatile uint32_t* p = (const volatile uint32_t*)fin;
        // Compare bit patterns and sum as integers: this core traps on 64-bit integer-to-float conversion
        // (docs/et-soc1-notes.md), so no double ever appears in a kernel.
        /* Where the data should have come from. With OC_MEM_HOP every stage moves a slab one shire round
           the ring, so after K stages shire s holds what shire (s - K) mod 32 started with; if it did not
           actually cross, this check fails. */
        const uint64_t hd = args->hop_dist ? args->hop_dist : 1;
        const uint64_t from = (medium == OC_MEM_HOP) ? ring_prev(args->shire_mask, shire, stages * hd) : shire;
        const float wf = (float)(uint32_t)(from + stages * work);
        uint32_t want;
        __builtin_memcpy(&want, &wf, 4);
        uint64_t bad = 0, sum = 0;
        for (uint64_t i = 0; i < chunk / 4; ++i) {
            const uint32_t v = p[i];
            sum += v;
            if (v != want) {
                ++bad;
            }
        }
        put(args, minion, t1 - t0, sum, stages * chunk * 2, (uint32_t)bad);
        return 0;
    }

    return 0;
}
