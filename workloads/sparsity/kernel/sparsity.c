/*-------------------------------------------------------------------------
 * Sparse-compute probes for ET-SoC-1 (see ../README.md).
 *
 *  SP_FMA      Hart 0 of each minion repeats one TensorFMA (16x16 tiles) with A,
 *              and optionally B, resident in the L1 scratchpad. The host puts
 *              zeros in A or B, so the cycles per op show whether the tensor
 *              unit's zero skipping (PRM 9.4 pseudo-code) saves time.
 *  SP_TLOAD    Hart 0 streams 16-line TensorLoads under a fixed tensor_mask: do
 *              masked-off lines cost memory bandwidth?
 *  SP_GEMV     A batch-1 layer y = W x (1024 x 4096, fp32). Each shire keeps its
 *              share of W in its L2 scratchpad. Per 16-element slice of x a
 *              minion loads only the W^T lines whose x is nonzero, then does one
 *              one-row TensorFMA, and 16 minions sum their partial rows with a
 *              TensorReduce tree that stays inside the shire.
 *  SP_DIVERGE  Work items that each need k iterations of 4 independent FMA chains,
 *              on the 8 SIMD lanes of each hart: in static groups of 8 (like a
 *              GPU warp), with a lane refilled as soon as its item finishes, or
 *              one item at a time on one lane.
 *  SP_SPIN     Integer loop: power baseline.
 *
 * Timing uses the minion cycle counter (hpmcounter3). Each hart writes its own
 * 64 B result line, because the L1s are not coherent.
 *-------------------------------------------------------------------------*/

#include <stdbool.h>
#include <stdint.h>
#include "etsoc/isa/esr_defines.h"
#include "etsoc/isa/hart.h"
#include "etsoc/isa/tensors.h"
#include "sparsity_args.h"

int64_t entry_point(const struct SpArgs* args);

// The tensor unit reads and writes f0-f31 behind the compiler's back.
#define SP_POLL_LIMIT (1ull << 26)  // barrier poll reads before giving up (about 0.1-0.3 s)

#define FREGS                                                                                      \
    "f0", "f1", "f2", "f3", "f4", "f5", "f6", "f7", "f8", "f9", "f10", "f11", "f12", "f13", "f14", \
        "f15", "f16", "f17", "f18", "f19", "f20", "f21", "f22", "f23", "f24", "f25", "f26", "f27", \
        "f28", "f29", "f30", "f31"

/* Errata 1.29 type F: after a tensor op writes the vector registers, an fmv.x.w of the last register it wrote
   must come before any other instruction reads them. Which register that is depends on the op, so touch all. */
#define TOUCH_ALL                                                                                    \
    "fmv.x.w x0, f0\n fmv.x.w x0, f1\n fmv.x.w x0, f2\n fmv.x.w x0, f3\n fmv.x.w x0, f4\n"          \
    "fmv.x.w x0, f5\n fmv.x.w x0, f6\n fmv.x.w x0, f7\n fmv.x.w x0, f8\n fmv.x.w x0, f9\n"          \
    "fmv.x.w x0, f10\n fmv.x.w x0, f11\n fmv.x.w x0, f12\n fmv.x.w x0, f13\n fmv.x.w x0, f14\n"     \
    "fmv.x.w x0, f15\n fmv.x.w x0, f16\n fmv.x.w x0, f17\n fmv.x.w x0, f18\n fmv.x.w x0, f19\n"     \
    "fmv.x.w x0, f20\n fmv.x.w x0, f21\n fmv.x.w x0, f22\n fmv.x.w x0, f23\n fmv.x.w x0, f24\n"     \
    "fmv.x.w x0, f25\n fmv.x.w x0, f26\n fmv.x.w x0, f27\n fmv.x.w x0, f28\n fmv.x.w x0, f29\n"     \
    "fmv.x.w x0, f30\n fmv.x.w x0, f31\n"

/* Errata 1.29 types B and C (vector moves, packed-integer and FP ops): a register must not be read within
   8 instructions of being written unless a taken branch comes between. TAKEN is that branch. */
#define TAKEN "j 91f\n91:\n"

// Four back-to-back reads: the firmware's workaround for RTLMIN-6496 (etsoc/drivers/pmu/pmu.h).
static inline uint64_t cycles(void)
{
    uint64_t v;
    __asm__ __volatile__(".p2align 4\n csrr %0, hpmcounter3\n csrr %0, hpmcounter3\n"
                         " csrr %0, hpmcounter3\n csrr %0, hpmcounter3\n" : "=r"(v));
    return v;
}

static inline void set_tensor_mask(uint64_t m)
{
    __asm__ __volatile__("csrw 0x805, %0" : : "r"(m) : "memory");
}

static inline uint64_t tensor_error(void)
{
    uint64_t v;
    __asm__ __volatile__("csrr %0, 0x808" : "=r"(v));
    return v;
}

static inline void t_fma(uint64_t v)
{
    __asm__ __volatile__("csrw 0x801, %0" : : "r"(v) : "memory", FREGS);
}

static inline void t_reduce(uint64_t v)
{
    __asm__ __volatile__("csrw 0x800, %0" : : "r"(v) : "memory", FREGS);
}

static inline void t_wait(uint64_t id)
{
    __asm__ __volatile__("csrw 0x830, %0" : : "r"(id) : "memory", FREGS);
}

/* TensorLoad (PRM 9.3.1, et-common-libs tensor_load): `lines` 64 B lines from addr, 64 B apart, into L1
   scratchpad lines dst.., with load id `id` (TensorWait id). mask = 1: only lines whose tensor_mask bit is set. */
static inline void t_load(uint64_t dst, uint64_t addr, uint64_t lines, uint64_t id, uint64_t mask, uint64_t tenb)
{
    const uint64_t v = (mask << 63) | ((dst & 0x3F) << 53) | (tenb << 52) | (addr & 0xFFFFFFFFFFC0ull) |
                       ((lines - 1) & 0xF);
    register uint64_t x31 __asm__("x31") = 64ull | (id & 1);
    __asm__ __volatile__("csrw 0x83f, %1" : : "r"(x31), "r"(v) : "memory");
}

/* TensorLoadL2Scp (et-common-libs et_tensor_load_l2scp): `lines` lines from addr into this shire's L2
   scratchpad starting at scratchpad line dst, bypassing L1 and L2. TensorWait 2 + id. */
static inline void t_load_l2scp(uint64_t dst, uint64_t addr, uint64_t lines, uint64_t id)
{
    const uint64_t v = ((dst & 0x1FFFCull) << 46) | ((dst & 3) << 4) | (addr & 0xFFFFFFFFFFC0ull) | ((lines - 1) & 0xF);
    register uint64_t x31 __asm__("x31") = 64ull | (id & 1);
    __asm__ __volatile__("csrw 0x85f, %1" : : "r"(x31), "r"(v) : "memory");
}

/* tensor_fma control word (PRM 9.4): MSK 63, BCOLS 56:55, AROWS 54:51, ACOLS 50:47, AOFFSET 46:43,
   TenC-to-RF 23 (int8), TENB 20, BSTART 17:12, ASTART 9:4, type 3:1, MUL 0. */
static inline uint64_t fma_word(uint64_t type, uint64_t arows, uint64_t astart, uint64_t tenb, uint64_t bstart,
                                uint64_t msk)
{
    return (msk << 63) | (3ull << 55) | ((arows - 1) << 51) | (15ull << 47) | (tenb << 20) | ((bstart & 0x3F) << 12) |
           ((astart & 0x3F) << 4) | ((type & 7) << 1);
}

/* Fast local barrier over the 32 hart 0s of this shire: FLB 30 counts arrivals, and the last one gives every
   minion a credit on counter 1 of thread 0 (the PRM 10/11 pattern, as in gp-sdk's shire barrier). Waiters poll
   FCCNB (counter 1 in bits 31:16) instead of blocking on the FCC CSR, and give up after `limit` reads, so a
   minion that never arrives fails the run instead of hanging the card. Returns false on a timeout. */
static bool shire_barrier(uint64_t shire, uint64_t limit)
{
    uint64_t last;
    __asm__ __volatile__("csrrw %0, 0x820, %1" : "=r"(last) : "r"((31ull << 5) | 30) : "memory");
    if (last) {
        *((volatile uint64_t*)ESR_SHIRE(shire, FCC_CREDINC_0) + 1) = 0xFFFFFFFFull;
    }
    for (uint64_t i = 0; i < limit; ++i) {
        uint64_t v;
        __asm__ __volatile__("csrr %0, 0xcc0" : "=r"(v) : : "memory");
        if ((v >> 16) & 0xFFFF) {
            __asm__ __volatile__("csrw 0x821, %0" : : "r"(1ull) : "memory");  // take the credit (there is one)
            return true;
        }
    }
    return false;
}

struct Out {
    uint64_t cycles, count, aux, aux2;
};

/* ---------------------------------------------------------------- SP_FMA */

static void run_fma(const struct SpArgs* a, uint64_t minion, struct Out* o)
{
    const uint64_t type = a->type, iters = a->iters, stream = a->b_stream, msk = a->use_mask;
    t_load(0, a->a_tile, 16, 0, 0, 0);  // A -> L1 scratchpad lines 0-15
    if (!stream) {
        t_load(16, a->b_tile, 16, 1, 0, 0);  // B -> lines 16-31
    }
    t_wait(0);
    t_wait(1);
    if (msk) {
        set_tensor_mask(a->mask);
    }
    const uint64_t base = fma_word(type, 16, 0, stream, 16, msk);
    const uint64_t last_extra = type == SP_INT8 ? (1ull << 23) : 0;  // int8 accumulates in TenC; copy it out at the end
    const uint64_t t0 = cycles();
    for (uint64_t i = 0; i < iters; ++i) {
        if (stream) {
            t_load(0, a->b_tile, 16, 1, 0, 1);  // TensorLoadB into TenB, paired with the next TensorFMA
        }
        t_fma(base | (i == 0 ? 1 : 0) | (i + 1 == iters ? last_extra : 0));
    }
    t_wait(7);
    o->cycles = cycles() - t0;
    o->count = iters;

    // C (16 x 16, 32-bit) is in f0..f31: row i in f[2i], f[2i+1].
    const uint64_t c = a->out + minion * SP_TILE_BYTES;
    __asm__ __volatile__(TOUCH_ALL "mov.m.x m0, zero, 0xff\n"
                         "fsw.ps f0, 0(%0)\n    fsw.ps f1, 32(%0)\n   fsw.ps f2, 64(%0)\n   fsw.ps f3, 96(%0)\n"
                         "fsw.ps f4, 128(%0)\n  fsw.ps f5, 160(%0)\n  fsw.ps f6, 192(%0)\n  fsw.ps f7, 224(%0)\n"
                         "fsw.ps f8, 256(%0)\n  fsw.ps f9, 288(%0)\n  fsw.ps f10, 320(%0)\n fsw.ps f11, 352(%0)\n"
                         "fsw.ps f12, 384(%0)\n fsw.ps f13, 416(%0)\n fsw.ps f14, 448(%0)\n fsw.ps f15, 480(%0)\n"
                         "fsw.ps f16, 512(%0)\n fsw.ps f17, 544(%0)\n fsw.ps f18, 576(%0)\n fsw.ps f19, 608(%0)\n"
                         "fsw.ps f20, 640(%0)\n fsw.ps f21, 672(%0)\n fsw.ps f22, 704(%0)\n fsw.ps f23, 736(%0)\n"
                         "fsw.ps f24, 768(%0)\n fsw.ps f25, 800(%0)\n fsw.ps f26, 832(%0)\n fsw.ps f27, 864(%0)\n"
                         "fsw.ps f28, 896(%0)\n fsw.ps f29, 928(%0)\n fsw.ps f30, 960(%0)\n fsw.ps f31, 992(%0)\n"
                         : : "r"(c) : "memory");
}

/* ---------------------------------------------------------------- SP_TLOAD */

static void run_tload(const struct SpArgs* a, uint64_t minion, struct Out* o)
{
    // Scratchpad addresses (0x8000_0000-0xFFFF_FFFF) are per shire: index them by minion-in-shire.
    const uint64_t idx = (a->src >> 31) == 1 ? (minion & 31) : minion;
    const uint64_t base = a->src + idx * a->src_bytes, span = a->src_bytes, iters = a->iters, msk = a->use_mask;
    if (msk) {
        set_tensor_mask(a->mask);
    }
    uint64_t off = 0;
    const uint64_t t0 = cycles();
    for (uint64_t i = 0; i < iters; ++i) {
        const uint64_t id = i & 1;
        if (i >= 2) {
            t_wait(id);  // two loads in flight
        }
        t_load(id * 16, base + off, 16, id, msk, 0);
        off += 1024;
        if (off >= span) {
            off = 0;
        }
    }
    t_wait(0);
    t_wait(1);
    o->cycles = cycles() - t0;
    o->count = iters;
}

/* ---------------------------------------------------------------- SP_GEMV */

static inline void zero_c_row(void)
{
    __asm__ __volatile__("mov.m.x m0, zero, 0xff\n fbcx.ps f0, zero\n fbcx.ps f1, zero\n" TAKEN : : : "memory", "f0", "f1");
}

static void run_gemv(const struct SpArgs* a, uint64_t shire, uint64_t minion, struct Out* o)
{
    const uint64_t j = minion & 31;          // minion in shire
    const uint64_t block = shire * 2 + (j >> 4);
    const uint64_t r = j & 15;               // K range: x[256 r, 256 r + 256)
    const uint64_t flags = a->gemv_flags, reps = a->iters;
    const uint64_t slab_line = j * SP_GEMV_SLAB_LINES;  // this minion's W^T lines in the shire's L2 scratchpad

    // Stage the W^T slab (16 KB) from DRAM into the local L2 scratchpad, 16 lines per TensorLoadL2Scp.
    const uint64_t wsrc = a->w + minion * SP_GEMV_SLAB_LINES * 64;
    for (uint64_t t = 0; t < SP_GEMV_SLAB_LINES / 16; ++t) {
        const uint64_t id = t & 1;
        if (t >= 2) {
            t_wait(2 + id);
        }
        t_load_l2scp(slab_line + 16 * t, wsrc + t * 1024, 16, id);
    }
    t_wait(2);
    t_wait(3);

    // Which of the 16 slices to compute, and their masks (the host precomputes the bitmask of x != 0).
    const volatile uint16_t* xm = (const volatile uint16_t*)a->xmask + r * SP_GEMV_SLICES;
    uint16_t mask[SP_GEMV_SLICES];
    uint8_t list[SP_GEMV_SLICES];
    uint64_t n = 0, lines = 0;
    for (uint64_t t = 0; t < SP_GEMV_SLICES; ++t) {
        const uint16_t m = (flags & SP_GEMV_MASKED_LOADS) ? xm[t] : 0xFFFF;
        if ((flags & SP_GEMV_SKIP_EMPTY) && xm[t] == 0) {
            continue;
        }
        mask[n] = m;
        list[n++] = (uint8_t)t;
        lines += (uint64_t)__builtin_popcount(m);
    }
    const uint64_t msk = (flags & SP_GEMV_MASKED_LOADS) ? 1 : 0;
    const uint64_t scp = SP_SCP_LOCAL((uint64_t)slab_line * 64);
    const uint64_t xline = a->x + r * 256 * 4;  // this minion's 256 x values = 16 lines
    // One-row TensorFMA: A = x slice (1 x 16) in L1 scratchpad line 32 + t, B = 16 W^T lines in buffer 0 or 1.
    const uint64_t fma0 = fma_word(SP_FP32, 1, 0, 0, 0, 0);
    // Tree reduce over the 16 minions of this block: minion r receives at levels below ctz(r), sends at ctz(r).
    const uint64_t top = r ? (uint64_t)__builtin_ctzll(r) : 3;

    const bool tree = (flags & SP_GEMV_TREE) != 0;
    uint64_t total = 0, done = 0;
    for (uint64_t rep = 0; rep < reps; ++rep) {
        if (!shire_barrier(shire, SP_POLL_LIMIT)) {
            break;
        }
        const uint64_t t0 = cycles();
        zero_c_row();
        t_load(32, xline, 16, 1, 0, 0);  // all 16 x slices of this minion -> lines 32-47
        if (n) {
            if (msk) {
                set_tensor_mask(mask[0]);
            }
            t_load(0, scp + (uint64_t)list[0] * 1024, 16, 0, msk, 0);
        }
        t_wait(1);
        for (uint64_t i = 0; i < n; ++i) {
            const uint64_t buf = i & 1;
            t_wait(buf);  // W^T lines of slice i are in; its tensor_mask is no longer needed
            if (i + 1 < n) {
                t_wait(7);  // the TensorFMA that last read the other buffer (slice i-1) is done
                if (msk) {
                    set_tensor_mask(mask[i + 1]);
                }
                t_load((buf ^ 1) * 16, scp + (uint64_t)list[i + 1] * 1024, 16, buf ^ 1, msk, 0);
            }
            t_fma(fma0 | ((32 + (uint64_t)list[i]) << 4) | ((buf * 16) << 12));
        }
        t_wait(7);
        if (tree) {
            // Sum the 16 partial rows (f0, f1) of the block with TensorReduce FADD, COUNT 2, levels 0..top;
            // the block's minion 0 ends with y.
            for (uint64_t h = 0; h <= top; ++h) {
                t_reduce((0ull << 24) | (2ull << 16) | (h << 3) | 3);
            }
            t_wait(9);
            if (r == 0) {
                float* y = (float*)a->out + block * 16;
                __asm__ __volatile__(TOUCH_ALL "mov.m.x m0, zero, 0xff\n fsw.ps f0, 0(%0)\n fsw.ps f1, 32(%0)\n"
                                     : : "r"(y) : "memory");
            }
        } else {
            // No on-chip reduction: every minion writes its partial row to its own line, and the host adds them.
            float* p = (float*)a->out + minion * 16;
            __asm__ __volatile__(TOUCH_ALL "mov.m.x m0, zero, 0xff\n fsw.ps f0, 0(%0)\n fsw.ps f1, 32(%0)\n"
                                 : : "r"(p) : "memory");
        }
        total += cycles() - t0;
        ++done;
    }
    o->cycles = total;
    o->count = done;  // < reps when a barrier timed out
    o->aux = n;
    o->aux2 = lines;
}

/* ---------------------------------------------------------------- SP_DIVERGE */

/* Each item needs k iterations of s = s*1 + 1 on 8 independent chains (8 FMAs per lane per iteration), so every
   chain ends at s = k exactly and the host checks each item. Lane state: f1-f8; remaining iterations: f9 (int32);
   constants f10 (0) and f11 (1.0f). m0 is the set of lanes still running. The loop orders its instructions so every
   vector register is read at least 8 instructions after it is written (errata 1.29 types B and C). */

static inline void div_consts(void)
{
    __asm__ __volatile__("mov.m.x m0, zero, 0xff\n"
                         "fbcx.ps f10, zero\n"
                         "lui t0, 0x3f800\n fbcx.ps f11, t0\n"  // 1.0f
                         TAKEN
                         : : : "t0", "memory", "f10", "f11");
}

// m0 = lanes whose counter is > 0; returns how many.
static inline uint64_t div_active(void)
{
    uint64_t n;
    __asm__ __volatile__("mov.m.x m0, zero, 0xff\n"
                         "fltm.pi m0, f10, f9\n"
                         "maskpopc %0, m0\n"
                         : "=r"(n) : : "memory");
    return n;
}

// With m0 set and at least `stop` lanes running: iterate while at least `stop` lanes are still running.
// Returns the iterations run; afterwards m0 again holds the running lanes.
static inline uint64_t div_run(uint64_t stop)
{
    uint64_t it = 0, n;
    __asm__ __volatile__("1:\n"
                         " faddi.pi f9, f9, -1\n"
                         " fmadd.ps f1, f1, f11, f11\n fmadd.ps f2, f2, f11, f11\n"
                         " fmadd.ps f3, f3, f11, f11\n fmadd.ps f4, f4, f11, f11\n"
                         " fmadd.ps f5, f5, f11, f11\n fmadd.ps f6, f6, f11, f11\n"
                         " fmadd.ps f7, f7, f11, f11\n fmadd.ps f8, f8, f11, f11\n"
                         " mov.m.x m0, zero, 0xff\n"
                         " fltm.pi m0, f10, f9\n"
                         " maskpopc %1, m0\n"
                         " addi %0, %0, 1\n"
                         " bgeu %1, %2, 1b\n"
                         : "+r"(it), "=&r"(n)
                         : "r"(stop)
                         : "memory", "f1", "f2", "f3", "f4", "f5", "f6", "f7", "f8", "f9");
    return it;
}

// Lane buffer: states f1-f8 and counter f9, 9 x 8 words (stays in this hart's L1).
struct LaneBuf {
    uint32_t v[9][8];
} __attribute__((aligned(64)));

static inline void div_save(struct LaneBuf* b)
{
    __asm__ __volatile__("mov.m.x m0, zero, 0xff\n"
                         "fsw.ps f1, 0(%0)\n fsw.ps f2, 32(%0)\n fsw.ps f3, 64(%0)\n fsw.ps f4, 96(%0)\n"
                         "fsw.ps f5, 128(%0)\n fsw.ps f6, 160(%0)\n fsw.ps f7, 192(%0)\n fsw.ps f8, 224(%0)\n"
                         "fsw.ps f9, 256(%0)\n"
                         : : "r"(b) : "memory");
}

// Errata 1.29 type A: after a vector load, an fmv.x.w of the loaded register before anything else reads it.
static inline void div_restore(const struct LaneBuf* b)
{
    __asm__ __volatile__("mov.m.x m0, zero, 0xff\n"
                         "flw.ps f1, 0(%0)\n flw.ps f2, 32(%0)\n flw.ps f3, 64(%0)\n flw.ps f4, 96(%0)\n"
                         "flw.ps f5, 128(%0)\n flw.ps f6, 160(%0)\n flw.ps f7, 192(%0)\n flw.ps f8, 224(%0)\n"
                         "flw.ps f9, 256(%0)\n"
                         "fmv.x.w x0, f1\n fmv.x.w x0, f2\n fmv.x.w x0, f3\n fmv.x.w x0, f4\n fmv.x.w x0, f5\n"
                         "fmv.x.w x0, f6\n fmv.x.w x0, f7\n fmv.x.w x0, f8\n fmv.x.w x0, f9\n"
                         "nop\n"
                         : : "r"(b) : "memory", "f1", "f2", "f3", "f4", "f5", "f6", "f7", "f8", "f9");
}

static inline void lane_clear(struct LaneBuf* b, uint64_t l, uint32_t k)
{
    for (int c = 0; c < SP_DIV_CHAINS; ++c) {
        b->v[c][l] = 0;
    }
    b->v[8][l] = k;
}

// The work queue: the first item of the next chunk, or >= n when the queue is empty.
static inline uint64_t grab(const struct SpArgs* a)
{
    uint32_t old;
    __asm__ __volatile__("amoaddg.w %0, %1, (%2)" : "=r"(old) : "r"((uint32_t)SP_DIV_CHUNK), "r"(a->counter) : "memory");
    return old;
}

// A hart's view of the queue: the part of its current chunk not handed out yet.
struct Queue {
    uint64_t next, end;
    bool empty;
    uint64_t chunks;
};

// The next item index, or -1 when the queue has run out.
static inline int64_t take(const struct SpArgs* a, struct Queue* q)
{
    if (q->next == q->end) {
        if (q->empty) {
            return -1;
        }
        const uint64_t c = grab(a);
        if (c >= a->n_items) {
            q->empty = true;
            return -1;
        }
        q->next = c;
        q->end = c + SP_DIV_CHUNK;
        ++q->chunks;
    }
    return (int64_t)q->next++;
}

static void run_diverge(const struct SpArgs* a, struct Out* o)
{
    const volatile uint32_t* items = (const volatile uint32_t*)a->items;
    volatile uint32_t* out = (volatile uint32_t*)a->out;
    const uint64_t n = a->n_items;
    uint64_t useful = 0, iters = 0, refills = 0, chunks = 0;
    struct LaneBuf lb;
    div_consts();
    const uint64_t t0 = cycles();

    if (a->variant == SP_DIV_STATIC) {
        for (uint64_t c = grab(a); c < n; c = grab(a)) {
            ++chunks;
            for (uint64_t g = c; g < c + SP_DIV_CHUNK; g += 8) {
                for (uint64_t l = 0; l < 8; ++l) {
                    const uint32_t k = items[g + l];
                    useful += k;
                    lane_clear(&lb, l, k);
                }
                div_restore(&lb);
                if (div_active()) {
                    iters += div_run(1);
                }
                div_save(&lb);
                for (uint64_t l = 0; l < 8; ++l) {
                    out[g + l] = lb.v[0][l];
                }
            }
        }
    } else if (a->variant == SP_DIV_REFILL) {
        struct Queue q = { 0, 0, false, 0 };
        int64_t lane_item[8];
        for (uint64_t l = 0; l < 8; ++l) {
            lane_item[l] = take(a, &q);
            const uint32_t k = lane_item[l] >= 0 ? items[lane_item[l]] : 0;
            useful += k;
            lane_clear(&lb, l, k);
        }
        div_restore(&lb);
        uint64_t active = div_active();
        while (active) {
            // Run while every lane is busy; once the queue is empty, run the remaining lanes dry.
            const bool more = !(q.empty && q.next == q.end);
            iters += div_run(more ? 8 : 1);
            active = div_active();
            if (active == 8 || !more) {
                continue;
            }
            // Some lanes finished: record their items and hand them the next ones.
            div_save(&lb);
            bool changed = false;
            for (uint64_t l = 0; l < 8; ++l) {
                if (lb.v[8][l] != 0) {
                    continue;
                }
                if (lane_item[l] >= 0) {
                    out[lane_item[l]] = lb.v[0][l];
                }
                lane_item[l] = take(a, &q);
                if (lane_item[l] >= 0) {
                    const uint32_t k = items[lane_item[l]];
                    useful += k;
                    lane_clear(&lb, l, k);
                    changed = true;
                }
            }
            ++refills;
            if (changed) {
                div_restore(&lb);
            }
            active = div_active();
        }
        div_save(&lb);
        for (uint64_t l = 0; l < 8; ++l) {
            if (lane_item[l] >= 0) {
                out[lane_item[l]] = lb.v[0][l];
            }
        }
        chunks = q.chunks;
    } else {  // SP_DIV_SCALAR: one item at a time, 8 chains on lane 0 with scalar fmadd.s
        for (uint64_t c = grab(a); c < n; c = grab(a)) {
            ++chunks;
            for (uint64_t i = c; i < c + SP_DIV_CHUNK; ++i) {
                uint64_t k = items[i];
                uint32_t res;
                useful += k;
                iters += k;
                __asm__ __volatile__("fmv.w.x f1, zero\n fmv.w.x f2, zero\n fmv.w.x f3, zero\n fmv.w.x f4, zero\n"
                                     "fmv.w.x f5, zero\n fmv.w.x f6, zero\n fmv.w.x f7, zero\n fmv.w.x f8, zero\n"
                                     TAKEN "beqz %1, 2f\n"
                                     "1: fmadd.s f1, f1, f11, f11\n fmadd.s f2, f2, f11, f11\n"
                                     " fmadd.s f3, f3, f11, f11\n fmadd.s f4, f4, f11, f11\n"
                                     " fmadd.s f5, f5, f11, f11\n fmadd.s f6, f6, f11, f11\n"
                                     " fmadd.s f7, f7, f11, f11\n fmadd.s f8, f8, f11, f11\n"
                                     " addi %1, %1, -1\n bnez %1, 1b\n"
                                     "2: j 3f\n3: fmv.x.w %0, f1\n"
                                     : "=r"(res), "+r"(k)
                                     : : "memory", "f1", "f2", "f3", "f4", "f5", "f6", "f7", "f8");
                out[i] = res;
            }
        }
    }
    o->cycles = cycles() - t0;
    o->count = useful;
    o->aux = iters;
    o->aux2 = refills | (chunks << 32);
}

/* ---------------------------------------------------------------- entry */

int64_t entry_point(const struct SpArgs* args)
{
    const uint64_t t_entry = cycles();
    const uint64_t hart = get_hart_id();
    const uint64_t shire = hart >> 6;
    const uint64_t minion = hart >> 1;
    const uint64_t thread = hart & 1;
    if (shire >= 32 || !((args->shire_mask >> shire) & 1) || (minion & 31) >= args->per_shire) {
        return 0;
    }
    const uint64_t mode = args->mode;
    if (thread && !(mode == SP_DIVERGE && args->harts == 2)) {
        return 0;  // tensor ops only from hart 0; SP_DIVERGE can use both harts
    }
    struct Out o = { 0, 0, 0, 0 };
    switch (mode) {
    case SP_FMA:
        run_fma(args, minion, &o);
        break;
    case SP_TLOAD:
        run_tload(args, minion, &o);
        break;
    case SP_GEMV:
        run_gemv(args, shire, minion, &o);
        break;
    case SP_DIVERGE:
        run_diverge(args, &o);
        break;
    case SP_SPIN: {
        const uint64_t t0 = cycles();
        for (uint64_t i = 0; i < args->iters; ++i) {
            __asm__ __volatile__("addi t0, t0, 1\n addi t1, t1, 1\n addi t2, t2, 1\n addi t3, t3, 1\n"
                                 : : : "t0", "t1", "t2", "t3");
        }
        o.cycles = cycles() - t0;
        o.count = args->iters;
        break;
    }
    default:
        break;
    }
    volatile struct SpResult* r = (volatile struct SpResult*)args->results + hart;
    r->cycles = o.cycles;
    r->count = o.count;
    r->aux = o.aux;
    r->aux2 = o.aux2;
    r->t_entry = t_entry;
    r->t_exit = cycles();
    r->hart = (uint32_t)hart;
    r->tensor_error = (uint32_t)tensor_error();
    r->magic = SP_MAGIC;
    return 0;
}
