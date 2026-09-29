/*-------------------------------------------------------------------------
 * Noisy sparse parity on the ET-SoC-1: the exhaustive correlation scan (see ../sparseparity_args.h for the
 * tiling, and docs/research/sparse-parity/DESIGN.md for the design).
 *
 *  SPP_SCALAR  Bit-packed XOR + software popcount (no multiply, no popcount instruction on this core). One hart
 *              per minion, or both with SPP_F_TWOHART (rows 0-7 / 8-15 of every tile, so each dump line has one
 *              writer). The correctness reference on the card.
 *  SPP_TENSOR  The scan as an int8 GEMM on +-1 bytes (the T2 split). Per minion:
 *              - hart 0 copies its share of X_B into the shire's L2 scratchpad with TensorLoadL2Scp, meets the
 *                other minions at a shire barrier, then issues only tensor ops (TensorLoad of A from the staging
 *                buffer, TensorLoad of B into TenB, TensorIMA8A32) and runs the epilogue. It reads the scratchpad
 *                (X_B and the staged A) through the local alias 0x7F, the path whose own-shire rate was measured;
 *              - hart 1 generates each row tile's A operand (16 rows x 64*S samples, +1 = 0x01, -1 = 0xFF) in its
 *                own vector registers and writes it to the staging buffer with stores that bypass its L1: fswg.ps
 *                into the scratchpad (explicit shire address), or fswl.ps into DRAM lines held in the shire's L2;
 *              - the two harts signal through two L2 lines per minion (amoswapl.d / amoorl.d), with a
 *                multiply-chain pause between polls (erratum 1.28: a thread issuing uncached ops back to back can
 *                starve the other thread). A hart that gives up (a poll limit or the barrier) writes the abort
 *                word to its own line, so the other hart stops at once instead of polling out its own limit.
 *              Each output tile's epilogue masks the staircase and padding, adds sum(c) and sum(c^2), and takes
 *              the lane maxima; when a tile could hold a new best (or tie it), its S ops are recomputed and
 *              scanned in scalar code for the exact position (rare: a few dozen times per hart). The hart's
 *              record flags a tie: another of its candidates with c equal to its best c.
 *
 * No early exit: every launch scans its whole work list. Every hart writes one 64 B record; nothing a minion
 * writes during the scan is read by another minion. Only hart 0 reads hpmcounter3 (erratum 1.23).
 * sys_emu cannot check errata 1.29 type F (its VPURF checker ignores tensor writes to f registers): the TOUCH_ALL
 * after every t_wait(7) that precedes a vector read handles it by construction.
 *-------------------------------------------------------------------------*/

#include <stdbool.h>
#include <stdint.h>
#include "etsoc/isa/esr_defines.h"
#include "etsoc/isa/hart.h"
#include "sparseparity_args.h"

int64_t entry_point(const struct SppArgs* args);

#define INLINE static inline __attribute__((always_inline))
/* Each hart's U-mode stack is 4,160 B (et-common-libs system/layout.h KERNEL_UMODE_STACK_SIZE), hart 1's directly
   below hart 0's, and sys_emu's memory checker stops a hart that writes past its own. The per-hart paths are kept
   out of entry_point's frame (NOINLINE) so that only the running path's locals are on the stack: hart 0's deepest
   chain (entry_point with its T0, run_t0, a tile loop, rescans) is about 2.3 KB. */
#define NOINLINE static __attribute__((noinline))

#define FREGS                                                                                      \
    "f0", "f1", "f2", "f3", "f4", "f5", "f6", "f7", "f8", "f9", "f10", "f11", "f12", "f13", "f14", \
        "f15", "f16", "f17", "f18", "f19", "f20", "f21", "f22", "f23", "f24", "f25", "f26", "f27", \
        "f28", "f29", "f30", "f31"

/* Errata 1.29 type F: after a tensor op writes the vector registers, an fmv.x.w must come before any other VPU
   instruction reads them. Touch all 32 (which register is last depends on the op). */
#define TOUCH_ALL                                                                                    \
    "fmv.x.w x0, f0\n fmv.x.w x0, f1\n fmv.x.w x0, f2\n fmv.x.w x0, f3\n fmv.x.w x0, f4\n"          \
    "fmv.x.w x0, f5\n fmv.x.w x0, f6\n fmv.x.w x0, f7\n fmv.x.w x0, f8\n fmv.x.w x0, f9\n"          \
    "fmv.x.w x0, f10\n fmv.x.w x0, f11\n fmv.x.w x0, f12\n fmv.x.w x0, f13\n fmv.x.w x0, f14\n"     \
    "fmv.x.w x0, f15\n fmv.x.w x0, f16\n fmv.x.w x0, f17\n fmv.x.w x0, f18\n fmv.x.w x0, f19\n"     \
    "fmv.x.w x0, f20\n fmv.x.w x0, f21\n fmv.x.w x0, f22\n fmv.x.w x0, f23\n fmv.x.w x0, f24\n"     \
    "fmv.x.w x0, f25\n fmv.x.w x0, f26\n fmv.x.w x0, f27\n fmv.x.w x0, f28\n fmv.x.w x0, f29\n"     \
    "fmv.x.w x0, f30\n fmv.x.w x0, f31\n"

/* Before a call to a function whose asm clobbers the f registers (a tile loop, rescans): that function's prologue
   saves the callee-saved f8, f9, f18..f27 with fsw (reads) and its epilogue restores them with flw (type A writes),
   so a second call would read registers the first one loaded, with no fmv.x.w between (sys_emu's VPURF checker
   flags it; the values are dead either way). TOUCH_ALL before each such call resolves every pending load. */
#define CALL_GUARD() __asm__ __volatile__(TOUCH_ALL : : : "memory")

/* Errata 1.29 types B and C (packed-integer, move and FP ops): a register must not be read within 8 instructions
   of being written unless a taken branch comes between. TAKEN is that branch. */
#define TAKEN "j 91f\n91:\n"

// All 32 vector registers (the 16 x 16 int32 output tile: row i in f[2i], f[2i+1]) to 1 KB at %0.
#define STORE_ALL                                                                                  \
    "fsw.ps f0, 0(%0)\n    fsw.ps f1, 32(%0)\n   fsw.ps f2, 64(%0)\n   fsw.ps f3, 96(%0)\n"          \
    "fsw.ps f4, 128(%0)\n  fsw.ps f5, 160(%0)\n  fsw.ps f6, 192(%0)\n  fsw.ps f7, 224(%0)\n"         \
    "fsw.ps f8, 256(%0)\n  fsw.ps f9, 288(%0)\n  fsw.ps f10, 320(%0)\n fsw.ps f11, 352(%0)\n"        \
    "fsw.ps f12, 384(%0)\n fsw.ps f13, 416(%0)\n fsw.ps f14, 448(%0)\n fsw.ps f15, 480(%0)\n"       \
    "fsw.ps f16, 512(%0)\n fsw.ps f17, 544(%0)\n fsw.ps f18, 576(%0)\n fsw.ps f19, 608(%0)\n"       \
    "fsw.ps f20, 640(%0)\n fsw.ps f21, 672(%0)\n fsw.ps f22, 704(%0)\n fsw.ps f23, 736(%0)\n"       \
    "fsw.ps f24, 768(%0)\n fsw.ps f25, 800(%0)\n fsw.ps f26, 832(%0)\n fsw.ps f27, 864(%0)\n"       \
    "fsw.ps f28, 896(%0)\n fsw.ps f29, 928(%0)\n fsw.ps f30, 960(%0)\n fsw.ps f31, 992(%0)\n"

/* ---------------------------------------------------------------- counters, CSRs, tensor ops */

// hpmcounter3 reads 128 short when its low 7 bits are 0-10 (the late carry; workloads/memprobe): put it back.
INLINE uint64_t cycles(void)
{
    uint64_t v;
    __asm__ __volatile__("csrr %0, hpmcounter3" : "=r"(v));
    return v + ((uint64_t)((v & 0x7F) < 11) << 7);
}

INLINE uint64_t tensor_error(void)
{
    uint64_t v;
    __asm__ __volatile__("csrr %0, 0x808" : "=r"(v));
    return v;
}

INLINE void t_fma(uint64_t v)
{
    __asm__ __volatile__("csrw 0x801, %0" : : "r"(v) : "memory", FREGS);
}

INLINE void t_wait(uint64_t id)
{
    __asm__ __volatile__("csrw 0x830, %0" : : "r"(id) : "memory", FREGS);
}

/* TensorLoad (PRM 9.3.1): 16 lines of 64 B from addr (64 B apart) into L1 scratchpad lines dst.., load id `id`
   (TensorWait id); tenb = 1: stream into TenB for the next TensorFMA instead. */
INLINE void t_load(uint64_t dst, uint64_t addr, uint64_t id, uint64_t tenb)
{
    const uint64_t v = ((dst & 0x3F) << 53) | (tenb << 52) | (addr & 0xFFFFFFFFFFC0ull) | 15u;
    register uint64_t x31 __asm__("x31") = 64ull | (id & 1);
    __asm__ __volatile__("csrw 0x83f, %1" : : "r"(x31), "r"(v) : "memory");
}

/* TensorLoadL2Scp: 16 lines from addr into this shire's L2 scratchpad starting at scratchpad line dst, bypassing
   L1 and L2. TensorWait 2 + id. */
INLINE void t_load_l2scp(uint64_t dst, uint64_t addr, uint64_t id)
{
    const uint64_t v = ((dst & 0x1FFFCull) << 46) | ((dst & 3) << 4) | (addr & 0xFFFFFFFFFFC0ull) | 15u;
    register uint64_t x31 __asm__("x31") = 64ull | (id & 1);
    __asm__ __volatile__("csrw 0x85f, %1" : : "r"(x31), "r"(v) : "memory");
}

/* TensorIMA8A32 control word (PRM 9.4): 16 A rows x 64 int8 (ACOLS 15 words) x 16 B columns, signed A and B
   (UA = UB = 0), B streamed through TenB, A from L1 scratchpad line astart. MUL (bit 0) starts C at A*B; DST (bit
   23) writes C to f0..f31 instead of TenC. */
INLINE uint64_t ima8_word(uint64_t astart, bool first, bool last)
{
    return (3ull << 55) | (15ull << 51) | (15ull << 47) | ((uint64_t)last << 23) | (1ull << 20) |
           ((astart & 0x3F) << 4) | (3ull << 1) | (uint64_t)first;
}

/* ---------------------------------------------------------------- L2 lines between the two harts */

INLINE uint64_t l2_read(uint64_t addr)
{
    uint64_t v;
    __asm__ __volatile__("amoorl.d %0, zero, (%1)" : "=r"(v) : "r"(addr) : "memory");
    return v;
}

INLINE void l2_write(uint64_t addr, uint64_t v)
{
    uint64_t old;
    __asm__ __volatile__("fence\n amoswapl.d %0, %1, (%2)" : "=r"(old) : "r"(v), "r"(addr) : "memory");
    (void)old;
}

/* A pause that keeps the issue slot free for the other hart: a chain of dependent multiplies (the multiplier
   takes about 8 cycles per op). About 70-330 cycles. */
INLINE void pause(uint64_t i)
{
    uint64_t x = 3;
    const uint64_t n = 8 + (i & 31);
    for (uint64_t j = 0; j < n; ++j) {
        __asm__ __volatile__("mul %0, %0, %0" : "+r"(x));
    }
}

// Waits until the line at addr holds this launch's epoch and a count >= target: returns 1. Returns -1 at once if
// the line holds the abort word (the other hart gave up), 0 after `limit` polls. Adds the polls to *polls.
INLINE int wait_count(uint64_t addr, uint64_t epoch, uint64_t target, uint64_t limit, uint64_t* polls)
{
    for (uint64_t i = 0; i < limit; ++i) {
        const uint64_t v = l2_read(addr);
        if ((v >> 32) == epoch) {
            const uint64_t cnt = v & 0xFFFFFFFFull;
            if (cnt == SPP_SYNC_ABORT) {
                *polls += i;
                return -1;
            }
            if (cnt >= target) {
                *polls += i;
                return 1;
            }
        }
        pause(i);
    }
    *polls += limit;
    return 0;
}

// Gives up: the abort word on this hart's own line, so the other hart stops waiting for it.
INLINE void signal_abort(uint64_t addr, uint64_t epoch)
{
    l2_write(addr, (epoch << 32) | SPP_SYNC_ABORT);
}

/* Fast local barrier over the hart 0s of minions 0..P-1 of this shire: FLB 30 counts arrivals and the last one
   gives each of them a credit on FCC counter 1 of thread 0 (as in workloads/sparsity). Waiters poll FCCNB and
   give up after `limit` reads, so a minion that never arrives fails the run instead of hanging the card. */
INLINE bool shire_barrier(uint64_t shire, uint64_t P, uint64_t limit)
{
    uint64_t last;
    __asm__ __volatile__("csrrw %0, 0x820, %1" : "=r"(last) : "r"(((P - 1) << 5) | 30) : "memory");
    if (last) {
        *((volatile uint64_t*)ESR_SHIRE(shire, FCC_CREDINC_0) + 1) = P >= 32 ? 0xFFFFFFFFull : ((1ull << P) - 1);
    }
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

/* ---------------------------------------------------------------- colex subsets */

INLINE int64_t sub_max(const uint64_t* r, uint64_t k1)
{
    return k1 ? (int64_t)r[k1 - 1] : -1;
}

// The next (k1)-subset in colex order.
INLINE void sub_next(uint64_t* r, uint64_t k1)
{
    for (uint64_t e = 0; e < k1; ++e) {
        if (e + 1 == k1 || r[e] + 1 < r[e + 1]) {
            ++r[e];
            for (uint64_t f = 0; f < e; ++f) {
                r[f] = f;
            }
            return;
        }
    }
}

// Popcount without a multiply (libgcc's __popcountdi2 uses the 1/8-rate mul).
INLINE uint64_t pc64(uint64_t x)
{
    x = x - ((x >> 1) & 0x5555555555555555ull);
    x = (x & 0x3333333333333333ull) + ((x >> 2) & 0x3333333333333333ull);
    x = (x + (x >> 4)) & 0x0F0F0F0F0F0F0F0Full;
    x += x >> 8;
    x += x >> 16;
    x += x >> 32;
    return x & 0x7F;
}

struct Acc {
    int64_t sum;
    uint64_t sq, count, best_rank;
    int32_t best;
    uint32_t tie;  // another candidate had c == best
};

// Every candidate with c >= the running best passes through here (the tensor epilogue rescans every tile whose
// maximum reaches the running best), so `tie` is exact: set when a second candidate reaches the best c.
INLINE void consider(struct Acc* a, int32_t c, uint64_t rank)
{
    if (c > a->best) {
        a->best = c;
        a->best_rank = rank;
        a->tie = 0;
    } else if (c == a->best) {
        a->tie = 1;
        if (rank < a->best_rank) {
            a->best_rank = rank;
        }
    }
}

/* ---------------------------------------------------------------- SPP_SCALAR */

NOINLINE void run_scalar(const struct SppArgs* a, uint64_t g, uint64_t thread, struct Acc* acc, uint64_t* rows_out)
{
    const uint64_t n = a->n, k1 = a->k - 1, m = a->m, S = a->S, nJ = a->nJ, nrows = a->nrows;
    const bool two = (a->flags & SPP_F_TWOHART) != 0, dump = (a->flags & SPP_F_DUMP) != 0;
    const uint64_t* X = (const uint64_t*)a->xbits;
    const uint64_t* Y = (const uint64_t*)a->ybits;
    const uint64_t* CK = (const uint64_t*)a->binom_k;
    const struct SppMinion* mp = (const struct SppMinion*)a->minions + g;
    const struct SppBlock* blocks = (const struct SppBlock*)a->blocks;
    uint64_t P[SPP_SMAX];
    uint64_t seq = mp->dump_base, rows = 0;
    for (uint32_t b = 0; b < mp->nblocks; ++b) {
        const struct SppBlock* blk = blocks + mp->first_block + b;
        uint64_t r[SPP_KMAX];
        for (uint64_t e = 0; e < k1; ++e) {
            r[e] = blk->sub[e];
        }
        uint64_t rank = 16ull * blk->tile0;
        for (uint32_t t = 0; t < blk->ntiles; ++t) {
            const uint64_t J0 = (uint64_t)(sub_max(r, k1) + 1) >> 4;
            for (uint64_t i = 0; i < 16; ++i, ++rank) {
                const bool mine = !two || ((i < 8) == (thread == 0));
                const bool valid = rank < nrows;
                if (mine && valid) {
                    const int64_t p = sub_max(r, k1);
                    for (uint64_t w = 0; w < S; ++w) {
                        uint64_t v = Y[w];
                        for (uint64_t e = 0; e < k1; ++e) {
                            v ^= X[r[e] * S + w];
                        }
                        P[w] = v;
                    }
                    ++rows;
                    for (uint64_t J = J0; J < nJ; ++J) {
                        volatile int32_t* line = dump ? (volatile int32_t*)(a->dump + (seq + J - J0) * SPP_TILE_BYTES + i * 64) : 0;
                        for (uint64_t jj = 0; jj < 16; ++jj) {
                            const uint64_t j = 16 * J + jj;
                            int32_t c = INT32_MIN;
                            if ((int64_t)j > p && j < n) {
                                const uint64_t* xj = X + j * S;
                                uint64_t pc = 0;
                                for (uint64_t w = 0; w < S; ++w) {
                                    pc += pc64(P[w] ^ xj[w]);
                                }
                                c = (int32_t)m - 2 * (int32_t)pc;
                                acc->sum += c;
                                acc->sq += (uint64_t)((int64_t)c * c);
                                ++acc->count;
                                consider(acc, c, rank + CK[j]);
                            }
                            if (dump) {
                                line[jj] = c;
                            }
                        }
                    }
                } else if (mine && dump) {
                    for (uint64_t J = J0; J < nJ; ++J) {
                        volatile int32_t* line = (volatile int32_t*)(a->dump + (seq + J - J0) * SPP_TILE_BYTES + i * 64);
                        for (uint64_t jj = 0; jj < 16; ++jj) {
                            line[jj] = INT32_MIN;
                        }
                    }
                }
                if (valid) {
                    sub_next(r, k1);
                }
            }
            seq += nJ - J0;
        }
    }
    *rows_out = rows;
}

/* ---------------------------------------------------------------- SPP_TENSOR, hart 1: the row operand */

static const uint32_t kLaneShift[8] __attribute__((aligned(32))) = { 0, 4, 8, 12, 16, 20, 24, 28 };

/* Constant vector registers of hart 1: f8 = per-lane shifts 0, 4, .., 28; f9 = 0x00204081 (spreads a nibble's
   bits to bits 0, 8, 16, 24); f10 = 0x01010101; f11 = 0xFE; f13 = 0.
   They stay live across C code between gen_consts() and the last EXPAND8 without being declared to the compiler
   (as in M1): the generators must call nothing that touches the f registers. Today they call wait_count,
   sub_next, l2_write, zero_line and, in run_gen_inc, a compiler-generated memset (a byte loop): none uses an f
   register (checked in the disassembly, 29 September). A call to anything that uses FP would corrupt the rows
   silently: reload with gen_consts() after it (review of M4, finding 10). */
INLINE void gen_consts(void)
{
    __asm__ __volatile__("mov.m.x m0, zero, 0xff\n"
                         "flw.ps f8, 0(%0)\n"
                         "li t0, 0x00204081\n fbcx.ps f9, t0\n"
                         "li t0, 0x01010101\n fbcx.ps f10, t0\n"
                         "li t0, 0xFE\n fbcx.ps f11, t0\n"
                         "fbci.pi f13, 0\n"
                         "fmv.x.w x0, f8\n"
                         TAKEN
                         : : "r"(kLaneShift) : "t0", "memory", "f8", "f9", "f10", "f11", "f13");
}

/* Expands eight 32-bit words of sign bits into 8 x 32 bytes of +1 (bit 0) / -1 (bit 1) and stores them at
   dst, dst+32, .., dst+224, bypassing this hart's L1: with fswg.ps into the scratchpad, through the shire's own
   explicit address (never the 0x7F alias: a global atomic through it is a bus error, and a global store through
   it is untested), or with fswl.ps into a DRAM line held in the shire's L2. (sys_emu's memory checker treats an
   fswl.ps to a scratchpad line as never visible to a later TensorLoad; a global store, a TensorLoadL2Scp or an
   evict is.) Byte 4l+b of a 32-byte chunk is bit 4l+b of its word. Eight independent chains, nine instructions
   per round, so every vector register is read at least eight instructions after it was written (errata 1.29
   types B and C). */
#define EXPAND8(STORE)                                                                                       \
    uint64_t a1, a2, a3, a4, a5, a6, a7;                                                                     \
    __asm__ __volatile__(                                                                                    \
        "fbcx.ps f0, %[w0]\n fbcx.ps f1, %[w1]\n fbcx.ps f2, %[w2]\n fbcx.ps f3, %[w3]\n"                    \
        "fbcx.ps f4, %[w4]\n fbcx.ps f5, %[w5]\n fbcx.ps f6, %[w6]\n fbcx.ps f7, %[w7]\n"                    \
        "addi %[a1], %[d], 32\n"                                                                             \
        "fsrl.pi f0, f0, f8\n fsrl.pi f1, f1, f8\n fsrl.pi f2, f2, f8\n fsrl.pi f3, f3, f8\n"                \
        "fsrl.pi f4, f4, f8\n fsrl.pi f5, f5, f8\n fsrl.pi f6, f6, f8\n fsrl.pi f7, f7, f8\n"                \
        "addi %[a2], %[d], 64\n"                                                                             \
        "fandi.pi f0, f0, 15\n fandi.pi f1, f1, 15\n fandi.pi f2, f2, 15\n fandi.pi f3, f3, 15\n"            \
        "fandi.pi f4, f4, 15\n fandi.pi f5, f5, 15\n fandi.pi f6, f6, 15\n fandi.pi f7, f7, 15\n"            \
        "addi %[a3], %[d], 96\n"                                                                             \
        "fmul.pi f0, f0, f9\n fmul.pi f1, f1, f9\n fmul.pi f2, f2, f9\n fmul.pi f3, f3, f9\n"                \
        "fmul.pi f4, f4, f9\n fmul.pi f5, f5, f9\n fmul.pi f6, f6, f9\n fmul.pi f7, f7, f9\n"                \
        "addi %[a4], %[d], 128\n"                                                                            \
        "fand.pi f0, f0, f10\n fand.pi f1, f1, f10\n fand.pi f2, f2, f10\n fand.pi f3, f3, f10\n"            \
        "fand.pi f4, f4, f10\n fand.pi f5, f5, f10\n fand.pi f6, f6, f10\n fand.pi f7, f7, f10\n"            \
        "addi %[a5], %[d], 160\n"                                                                            \
        "fmul.pi f0, f0, f11\n fmul.pi f1, f1, f11\n fmul.pi f2, f2, f11\n fmul.pi f3, f3, f11\n"            \
        "fmul.pi f4, f4, f11\n fmul.pi f5, f5, f11\n fmul.pi f6, f6, f11\n fmul.pi f7, f7, f11\n"            \
        "addi %[a6], %[d], 192\n"                                                                            \
        "fxor.pi f0, f0, f10\n fxor.pi f1, f1, f10\n fxor.pi f2, f2, f10\n fxor.pi f3, f3, f10\n"            \
        "fxor.pi f4, f4, f10\n fxor.pi f5, f5, f10\n fxor.pi f6, f6, f10\n fxor.pi f7, f7, f10\n"            \
        "addi %[a7], %[d], 224\n"                                                                            \
        STORE " f0, (%[d])\n " STORE " f1, (%[a1])\n " STORE " f2, (%[a2])\n " STORE " f3, (%[a3])\n"        \
        STORE " f4, (%[a4])\n " STORE " f5, (%[a5])\n " STORE " f6, (%[a6])\n " STORE " f7, (%[a7])\n"       \
        : [a1] "=&r"(a1), [a2] "=&r"(a2), [a3] "=&r"(a3), [a4] "=&r"(a4), [a5] "=&r"(a5), [a6] "=&r"(a6),     \
          [a7] "=&r"(a7)                                                                                     \
        : [d] "r"(dst), [w0] "r"(w0), [w1] "r"(w1), [w2] "r"(w2), [w3] "r"(w3), [w4] "r"(w4), [w5] "r"(w5),   \
          [w6] "r"(w6), [w7] "r"(w7)                                                                         \
        : "memory", "f0", "f1", "f2", "f3", "f4", "f5", "f6", "f7")

INLINE void expand8_g(uint64_t dst, uint32_t w0, uint32_t w1, uint32_t w2, uint32_t w3, uint32_t w4, uint32_t w5,
                      uint32_t w6, uint32_t w7)
{
    EXPAND8("fswg.ps");
}

INLINE void expand8_l(uint64_t dst, uint32_t w0, uint32_t w1, uint32_t w2, uint32_t w3, uint32_t w4, uint32_t w5,
                      uint32_t w6, uint32_t w7)
{
    EXPAND8("fswl.ps");
}

// One 64-byte line of zero bytes (a padding row's slice) at dst (f13 = 0).
INLINE void zero_line(uint64_t dst, bool global)
{
    const uint64_t d2 = dst + 32;
    if (global) {
        __asm__ __volatile__("fswg.ps f13, (%0)\n fswg.ps f13, (%1)\n" : : "r"(dst), "r"(d2) : "memory");
    } else {
        __asm__ __volatile__("fswl.ps f13, (%0)\n fswl.ps f13, (%1)\n" : : "r"(dst), "r"(d2) : "memory");
    }
}

// The staging buffers of minion slot g (minion mi of `shire`): DRAM, or this shire's scratchpad by its explicit
// shire address (which the global stores need; TensorLoad reads the same physical lines).
INLINE uint64_t stage_base(const struct SppArgs* a, uint64_t shire, uint64_t mi, uint64_t g)
{
    return a->stage_global ? a->stage + g * a->stage_stride
                           : 0x80000000ull + (shire << 23) + a->stage + mi * a->stage_stride;
}

NOINLINE void run_gen(const struct SppArgs* a, uint64_t shire, uint64_t mi, uint64_t g, uint32_t* err,
                      uint64_t* tiles_out, uint64_t* polls_out)
{
    const uint64_t k1 = a->k - 1, S = a->S, nrows = a->nrows, nbuf = a->nbuf, epoch = a->epoch;
    const uint64_t* X = (const uint64_t*)a->xbits;
    const uint64_t* Y = (const uint64_t*)a->ybits;
    const struct SppMinion* mp = (const struct SppMinion*)a->minions + g;
    const struct SppBlock* blocks = (const struct SppBlock*)a->blocks;
    const uint64_t sbytes = 16 * S * 64;
    const uint64_t stage0 = stage_base(a, shire, mi, g);
    const bool global = !a->stage_global;  // scratchpad staging: global stores
    const uint64_t gen_line = a->sync + g * SPP_SYNC_BYTES, rel_line = gen_line + 64;
    const uint64_t* rp[16][SPP_KMAX - 1];
    uint64_t q = 0, polls = 0;
    gen_consts();
    for (uint32_t b = 0; b < mp->nblocks; ++b) {
        const struct SppBlock* blk = blocks + mp->first_block + b;
        uint64_t r[SPP_KMAX];
        for (uint64_t e = 0; e < k1; ++e) {
            r[e] = blk->sub[e];
        }
        uint64_t rank = 16ull * blk->tile0;
        for (uint32_t t = 0; t < blk->ntiles; ++t, ++q) {
            if (q >= nbuf) {
                const int w = wait_count(rel_line, epoch, q - nbuf + 1, a->poll_limit, &polls);
                if (w <= 0) {
                    if (w == 0) {
                        *err |= SPP_ERR_POLL;
                        signal_abort(gen_line, epoch);  // hart 0 stops waiting for rows
                    } else {
                        *err |= SPP_ERR_ABORTED;
                    }
                    goto out;
                }
            }
            const uint64_t dst = stage0 + (nbuf == 2 ? (q & 1) : 0) * sbytes;
            uint64_t nvalid = 0;
            for (uint64_t i = 0; i < 16; ++i, ++rank) {
                if (rank < nrows) {
                    for (uint64_t e = 0; e < k1; ++e) {
                        rp[i][e] = X + r[e] * S;
                    }
                    sub_next(r, k1);
                    ++nvalid;
                } else {
                    for (uint64_t e = 0; e < k1; ++e) {
                        rp[i][e] = X;  // any column: the row is zeroed below
                    }
                }
            }
            // Word q' = s*32 + 2i + h of the tile (row i, samples 64s + 32h ..) goes to dst + 32 q'.
            for (uint64_t i = 0; i < 16; i += 4) {
                for (uint64_t s = 0; s < S; ++s) {
                    uint64_t p[4];
                    for (uint64_t rr = 0; rr < 4; ++rr) {
                        uint64_t v = Y[s];
                        for (uint64_t e = 0; e < k1; ++e) {
                            v ^= rp[i + rr][e][s];
                        }
                        p[rr] = v;
                    }
                    const uint64_t d = dst + (s * 32 + 2 * i) * 32;
                    if (global) {
                        expand8_g(d, (uint32_t)p[0], (uint32_t)(p[0] >> 32), (uint32_t)p[1], (uint32_t)(p[1] >> 32),
                                  (uint32_t)p[2], (uint32_t)(p[2] >> 32), (uint32_t)p[3], (uint32_t)(p[3] >> 32));
                    } else {
                        expand8_l(d, (uint32_t)p[0], (uint32_t)(p[0] >> 32), (uint32_t)p[1], (uint32_t)(p[1] >> 32),
                                  (uint32_t)p[2], (uint32_t)(p[2] >> 32), (uint32_t)p[3], (uint32_t)(p[3] >> 32));
                    }
                }
            }
            for (uint64_t i = nvalid; i < 16; ++i) {
                for (uint64_t s = 0; s < S; ++s) {
                    zero_line(dst + (s * 32 + 2 * i) * 32, global);
                }
            }
            l2_write(gen_line, (epoch << 32) | (q + 1));  // fence, then the count
        }
    }
out:
    *tiles_out = q;
    *polls_out = polls;
}

/* SPP_F_GEN_NOSTORE (a timing probe): the same expansion, stored with plain fsw.ps into a 256 B buffer that stays in
   this hart's L1, so the global staging stores are the only work left out. Caveat (review of M4, finding 9): the
   256 B are 4 of the 8 L1 lines a hart has in scratchpad mode, shared with the slice-major X lines and the stack,
   so dirty write-backs of the buffer may count as generation time: incremental minus nostore can understate what
   the staged stores cost. */
INLINE void expand8_c(uint64_t dst, uint32_t w0, uint32_t w1, uint32_t w2, uint32_t w3, uint32_t w4, uint32_t w5,
                      uint32_t w6, uint32_t w7)
{
    EXPAND8("fsw.ps");
}

// Four rows' words (row i: samples 64s.. of rows i..i+3) expanded and stored at d (see EXPAND8).
INLINE void emit4(uint64_t d, uint64_t p0, uint64_t p1, uint64_t p2, uint64_t p3, uint64_t mode)
{
    if (mode == 0) {
        expand8_g(d, (uint32_t)p0, (uint32_t)(p0 >> 32), (uint32_t)p1, (uint32_t)(p1 >> 32), (uint32_t)p2,
                  (uint32_t)(p2 >> 32), (uint32_t)p3, (uint32_t)(p3 >> 32));
    } else if (mode == 1) {
        expand8_l(d, (uint32_t)p0, (uint32_t)(p0 >> 32), (uint32_t)p1, (uint32_t)(p1 >> 32), (uint32_t)p2,
                  (uint32_t)(p2 >> 32), (uint32_t)p3, (uint32_t)(p3 >> 32));
    } else {
        expand8_c(d, (uint32_t)p0, (uint32_t)(p0 >> 32), (uint32_t)p1, (uint32_t)(p1 >> 32), (uint32_t)p2,
                  (uint32_t)(p2 >> 32), (uint32_t)p3, (uint32_t)(p3 >> 32));
    }
}

/* A run of consecutive rows of one row tile that share their prefix R \ {r0}: in colex order r0 (the smallest
   element) varies fastest, so rows row0 .. row0+len-1 have r0 = off, off+1, .. and the same r1 .. r_{k-2}. */
struct GenRun {
    uint32_t row0, len;
    uint64_t off;
    uint16_t pre[SPP_KMAX - 2];
};

/* SPP_F_GEN_INC (k >= 2): the row operand from the slice-major X. Per slice s, each run's prefix word
   y[s] ^ x_{r1}[s] ^ .. is computed once and each row's word is prefix ^ x_{r0}[s], read from xt + s*n + r0: the 16
   rows of a tile read 2-3 consecutive lines. The staging layout, the zeroed padding rows and the hand-off are
   run_gen's. */
NOINLINE void run_gen_inc(const struct SppArgs* a, uint64_t shire, uint64_t mi, uint64_t g, uint32_t* err,
                          uint64_t* tiles_out, uint64_t* polls_out)
{
    const uint64_t k1 = a->k - 1, S = a->S, n = a->n, nrows = a->nrows, nbuf = a->nbuf, epoch = a->epoch;
    const uint64_t* XT = (const uint64_t*)a->xt;
    const uint64_t* Y = (const uint64_t*)a->ybits;
    const struct SppMinion* mp = (const struct SppMinion*)a->minions + g;
    const struct SppBlock* blocks = (const struct SppBlock*)a->blocks;
    const uint64_t sbytes = 16 * S * 64;
    const uint64_t stage0 = stage_base(a, shire, mi, g);
    const bool global = !a->stage_global;
    const bool nostore = (a->flags & SPP_F_GEN_NOSTORE) != 0;
    const uint64_t mode = nostore ? 2 : global ? 0 : 1;
    const uint64_t gen_line = a->sync + g * SPP_SYNC_BYTES, rel_line = gen_line + 64;
    uint32_t sink[64] __attribute__((aligned(64)));  // SPP_F_GEN_NOSTORE's target (256 B: 4 of hart 1's 8 L1 lines)
    struct GenRun runs[16];
    uint64_t q = 0, polls = 0;
    gen_consts();
    for (uint32_t b = 0; b < mp->nblocks; ++b) {
        const struct SppBlock* blk = blocks + mp->first_block + b;
        uint64_t r[SPP_KMAX];
        for (uint64_t e = 0; e < k1; ++e) {
            r[e] = blk->sub[e];
        }
        uint64_t rank = 16ull * blk->tile0;
        for (uint32_t t = 0; t < blk->ntiles; ++t, ++q) {
            if (q >= nbuf) {
                const int w = wait_count(rel_line, epoch, q - nbuf + 1, a->poll_limit, &polls);
                if (w <= 0) {
                    if (w == 0) {
                        *err |= SPP_ERR_POLL;
                        signal_abort(gen_line, epoch);  // hart 0 stops waiting for rows
                    } else {
                        *err |= SPP_ERR_ABORTED;
                    }
                    goto out;
                }
            }
            const uint64_t dst = stage0 + (nbuf == 2 ? (q & 1) : 0) * sbytes;
            uint64_t nvalid = 0, nruns = 0;
            for (uint64_t i = 0; i < 16; ++i, ++rank) {
                if (rank < nrows) {
                    if (nruns == 0 || r[0] != runs[nruns - 1].off + runs[nruns - 1].len) {
                        struct GenRun* u = &runs[nruns++];
                        u->row0 = (uint32_t)i;
                        u->len = 1;
                        u->off = r[0];
                        for (uint64_t e = 1; e < k1; ++e) {
                            u->pre[e - 1] = (uint16_t)r[e];
                        }
                    } else {
                        ++runs[nruns - 1].len;
                    }
                    sub_next(r, k1);
                    ++nvalid;
                }
            }
            if (nruns == 1 && nvalid == 16) {
                // the common case: one prefix, r0 consecutive over all 16 rows
                const uint64_t off = runs[0].off;
                for (uint64_t s = 0; s < S; ++s) {
                    const uint64_t* xs = XT + s * n;
                    uint64_t v = Y[s];
                    for (uint64_t e = 1; e < k1; ++e) {
                        v ^= xs[runs[0].pre[e - 1]];
                    }
                    const uint64_t* xo = xs + off;
                    const uint64_t d = nostore ? (uint64_t)sink : dst + s * 1024;
                    for (uint64_t i = 0; i < 16; i += 4) {
                        emit4(nostore ? d : d + 64 * i, v ^ xo[i], v ^ xo[i + 1], v ^ xo[i + 2], v ^ xo[i + 3], mode);
                    }
                }
            } else {
                for (uint64_t s = 0; s < S; ++s) {
                    const uint64_t* xs = XT + s * n;
                    uint64_t p[16];
                    for (uint64_t i = nvalid; i < 16; ++i) {
                        p[i] = 0;  // padding rows: zeroed below
                    }
                    for (uint64_t u = 0; u < nruns; ++u) {
                        uint64_t v = Y[s];
                        for (uint64_t e = 1; e < k1; ++e) {
                            v ^= xs[runs[u].pre[e - 1]];
                        }
                        const uint64_t* xo = xs + runs[u].off;
                        uint64_t* pp = p + runs[u].row0;
                        for (uint64_t i = 0; i < runs[u].len; ++i) {
                            pp[i] = v ^ xo[i];
                        }
                    }
                    const uint64_t d = nostore ? (uint64_t)sink : dst + s * 1024;
                    for (uint64_t i = 0; i < 16; i += 4) {
                        emit4(nostore ? d : d + 64 * i, p[i], p[i + 1], p[i + 2], p[i + 3], mode);
                    }
                }
                if (!nostore) {
                    for (uint64_t i = nvalid; i < 16; ++i) {
                        for (uint64_t s = 0; s < S; ++s) {
                            zero_line(dst + (s * 32 + 2 * i) * 32, global);
                        }
                    }
                }
            }
            l2_write(gen_line, (epoch << 32) | (q + 1));  // fence, then the count
        }
    }
out:
    *tiles_out = q;
    *polls_out = polls;
}

/* ---------------------------------------------------------------- SPP_TENSOR, hart 0: tensor ops and epilogue */

// The row tile being scanned.
struct TileInfo {
    uint64_t rank0;      // row rank of row 0
    int64_t pmax[16];    // largest element of each row's subset
    uint64_t nvalid;     // rows 0..nvalid-1 are real rows, the rest padding
    uint64_t J0;         // first column tile
    uint64_t A;          // staging buffer of its A operand
};

struct T0 {
    const struct SppArgs* a;
    uint64_t S, n, xb_scp;
    bool resident, dump, noepi, perturb;
    struct Acc acc;
    uint64_t ops, best_scans;
    uint8_t tgt[SPP_SMAX];  // SPP_F_EPI_HIDE: pieces of the pending epilogue done after slot s
    uint32_t buf[256] __attribute__((aligned(64)));  // spills, results and best scans (hart 0's L1 / stack)
};

INLINE uint64_t xb_addr(const struct T0* c, uint64_t J, uint64_t s)
{
    return c->xb_scp + (J * c->S + s) * SPP_TILE_BYTES;
}

/* The reduction of one output tile in f0..f31 (invalid entries already zeroed): per-lane sum(c^2), sum(c) and
   max(c) into buf[128..151] (lanes of SQ, SUM, MAX). Rows 8-15 (f16..f31) are spilled to buf[0..127] so that
   rows 0-7 can be reduced with f16..f31 as temporaries, then reloaded into f0..f15 and reduced the same way.
   Rounds of independent ops are separated by taken branches (errata 1.29 types B and C). */
#define REDUCE_HALF                                                                                             \
    "fmul.pi f16, f0, f0\n fmul.pi f17, f1, f1\n fmul.pi f18, f2, f2\n fmul.pi f19, f3, f3\n"                   \
    "fmul.pi f20, f4, f4\n fmul.pi f21, f5, f5\n fmul.pi f22, f6, f6\n fmul.pi f23, f7, f7\n"                   \
    "fmul.pi f24, f8, f8\n fmul.pi f25, f9, f9\n fmul.pi f26, f10, f10\n fmul.pi f27, f11, f11\n"               \
    "fmul.pi f28, f12, f12\n fmul.pi f29, f13, f13\n fmul.pi f30, f14, f14\n fmul.pi f31, f15, f15\n" TAKEN     \
    "fadd.pi f16, f16, f17\n fadd.pi f18, f18, f19\n fadd.pi f20, f20, f21\n fadd.pi f22, f22, f23\n"           \
    "fadd.pi f24, f24, f25\n fadd.pi f26, f26, f27\n fadd.pi f28, f28, f29\n fadd.pi f30, f30, f31\n" TAKEN     \
    "fadd.pi f16, f16, f18\n fadd.pi f20, f20, f22\n fadd.pi f24, f24, f26\n fadd.pi f28, f28, f30\n" TAKEN     \
    "fadd.pi f16, f16, f20\n fadd.pi f24, f24, f28\n" TAKEN                                                     \
    "fadd.pi f16, f16, f24\n"                                                                                   \
    "fadd.pi f17, f0, f1\n fadd.pi f19, f2, f3\n fadd.pi f21, f4, f5\n fadd.pi f23, f6, f7\n"                   \
    "fadd.pi f25, f8, f9\n fadd.pi f27, f10, f11\n fadd.pi f29, f12, f13\n fadd.pi f31, f14, f15\n"             \
    "fmax.pi f0, f0, f1\n fmax.pi f2, f2, f3\n fmax.pi f4, f4, f5\n fmax.pi f6, f6, f7\n"                       \
    "fmax.pi f8, f8, f9\n fmax.pi f10, f10, f11\n fmax.pi f12, f12, f13\n fmax.pi f14, f14, f15\n" TAKEN        \
    "fadd.pi f17, f17, f19\n fadd.pi f21, f21, f23\n fadd.pi f25, f25, f27\n fadd.pi f29, f29, f31\n"           \
    "fmax.pi f0, f0, f2\n fmax.pi f4, f4, f6\n fmax.pi f8, f8, f10\n fmax.pi f12, f12, f14\n" TAKEN             \
    "fadd.pi f17, f17, f21\n fadd.pi f25, f25, f29\n fmax.pi f0, f0, f4\n fmax.pi f8, f8, f12\n" TAKEN          \
    "fadd.pi f17, f17, f25\n fmax.pi f0, f0, f8\n" TAKEN

INLINE void reduce_tile(uint32_t* buf)
{
    __asm__ __volatile__(
        "fsw.ps f16, 0(%0)\n   fsw.ps f17, 32(%0)\n  fsw.ps f18, 64(%0)\n  fsw.ps f19, 96(%0)\n"
        "fsw.ps f20, 128(%0)\n fsw.ps f21, 160(%0)\n fsw.ps f22, 192(%0)\n fsw.ps f23, 224(%0)\n"
        "fsw.ps f24, 256(%0)\n fsw.ps f25, 288(%0)\n fsw.ps f26, 320(%0)\n fsw.ps f27, 352(%0)\n"
        "fsw.ps f28, 384(%0)\n fsw.ps f29, 416(%0)\n fsw.ps f30, 448(%0)\n fsw.ps f31, 480(%0)\n"
        REDUCE_HALF
        "fsw.ps f16, 512(%0)\n fsw.ps f17, 544(%0)\n fsw.ps f0, 576(%0)\n"
        "flw.ps f0, 0(%0)\n    flw.ps f1, 32(%0)\n   flw.ps f2, 64(%0)\n   flw.ps f3, 96(%0)\n"
        "flw.ps f4, 128(%0)\n  flw.ps f5, 160(%0)\n  flw.ps f6, 192(%0)\n  flw.ps f7, 224(%0)\n"
        "flw.ps f8, 256(%0)\n  flw.ps f9, 288(%0)\n  flw.ps f10, 320(%0)\n flw.ps f11, 352(%0)\n"
        "flw.ps f12, 384(%0)\n flw.ps f13, 416(%0)\n flw.ps f14, 448(%0)\n flw.ps f15, 480(%0)\n"
        // errata 1.29 type A: an fmv.x.w of each loaded register, then at least one more instruction
        "fmv.x.w x0, f0\n fmv.x.w x0, f1\n fmv.x.w x0, f2\n fmv.x.w x0, f3\n fmv.x.w x0, f4\n fmv.x.w x0, f5\n"
        "fmv.x.w x0, f6\n fmv.x.w x0, f7\n fmv.x.w x0, f8\n fmv.x.w x0, f9\n fmv.x.w x0, f10\n fmv.x.w x0, f11\n"
        "fmv.x.w x0, f12\n fmv.x.w x0, f13\n fmv.x.w x0, f14\n fmv.x.w x0, f15\n"
        TAKEN
        REDUCE_HALF
        // combine with the first half's results (SQ, SUM, MAX at 512, 544, 576)
        "flw.ps f18, 512(%0)\n flw.ps f19, 544(%0)\n flw.ps f20, 576(%0)\n"
        "fmv.x.w x0, f18\n fmv.x.w x0, f19\n fmv.x.w x0, f20\n"
        TAKEN
        "fadd.pi f16, f16, f18\n fadd.pi f17, f17, f19\n fmax.pi f0, f0, f20\n"
        TAKEN
        "fsw.ps f16, 512(%0)\n fsw.ps f17, 544(%0)\n fsw.ps f0, 576(%0)\n"
        : : "r"(buf) : "memory", FREGS);
}

/* Zero the invalid entries of the tile in f0..f31: inv[r] is the byte mask of lanes of register fr to clear. */
#define MASKREG(r) "lbu t0, " #r "(%0)\n mov.m.x m0, t0, 0\n fxor.pi f" #r ", f" #r ", f" #r "\n"
INLINE void mask_tile(const uint8_t* inv)
{
    __asm__ __volatile__(
        MASKREG(0) MASKREG(1) MASKREG(2) MASKREG(3) MASKREG(4) MASKREG(5) MASKREG(6) MASKREG(7)
        MASKREG(8) MASKREG(9) MASKREG(10) MASKREG(11) MASKREG(12) MASKREG(13) MASKREG(14) MASKREG(15)
        MASKREG(16) MASKREG(17) MASKREG(18) MASKREG(19) MASKREG(20) MASKREG(21) MASKREG(22) MASKREG(23)
        MASKREG(24) MASKREG(25) MASKREG(26) MASKREG(27) MASKREG(28) MASKREG(29) MASKREG(30) MASKREG(31)
        "mov.m.x m0, zero, 0xff\n" TAKEN
        : : "r"(inv) : "t0", "memory", FREGS);
}

// Issues the S ops of output tile (ti, J) with C to f0..f31 on the last. A is resident (lines 16s..) or is
// reloaded here slice by slice into L1 scratchpad lines 32-47 (only used by best scans).
INLINE void recompute(struct T0* c, const struct TileInfo* ti, uint64_t J)
{
    t_wait(0);
    t_wait(1);
    t_wait(7);
    for (uint64_t s = 0; s < c->S; ++s) {
        uint64_t astart = 16 * s;
        if (!c->resident) {
            astart = 32;
            t_load(32, ti->A + s * SPP_TILE_BYTES, 0, 0);
            t_wait(0);
        }
        t_load(0, xb_addr(c, J, s), 0, 1);
        t_fma(ima8_word(astart, s == 0, s + 1 == c->S));
        if (!c->resident) {
            t_wait(7);  // the FMA has read lines 32-47 before the next slice overwrites them
        }
    }
    t_wait(7);
}

// Scalar scan of the raw tile in c->buf for a new best among its valid entries.
INLINE void best_scan(struct T0* c, const struct TileInfo* ti, uint64_t J)
{
    const uint64_t* CK = (const uint64_t*)c->a->binom_k;
    for (uint64_t i = 0; i < ti->nvalid; ++i) {
        for (uint64_t jj = 0; jj < 16; ++jj) {
            const uint64_t j = 16 * J + jj;
            if ((int64_t)j <= ti->pmax[i] || j >= c->n) {
                continue;
            }
            consider(&c->acc, (int32_t)c->buf[i * 16 + jj], ti->rank0 + i + CK[j]);
        }
    }
}

// Epilogue of output tile (ti, J), after its last op (C to f0..f31) has been issued.
INLINE void epilogue(struct T0* c, const struct TileInfo* ti, uint64_t J, uint64_t seq)
{
    t_wait(7);
    if (c->noepi) {
        return;
    }
    __asm__ __volatile__(TOUCH_ALL : : : "memory");
    if (c->dump) {
        const uint64_t d = c->a->dump + seq * SPP_TILE_BYTES;
        __asm__ __volatile__(STORE_ALL : : "r"(d) : "memory");
    }
    // Valid entries: rows < nvalid, columns j with pmax[i] < j < n.
    const uint64_t n = c->n, j0 = 16 * J;
    uint64_t cnt = 0;
    // The negative control (SPP_F_PERTURB_MASK): in the first tile whose row 0 has a masked column just below its
    // first valid one, every such row's window moves one column left (it scores j = max(R) and drops its last
    // valid j), once per launch. Same count, wrong candidates: both checksums fail.
    bool shift = false;
    if (c->perturb && ti->nvalid > 0 && (int64_t)j0 <= ti->pmax[0] && ti->pmax[0] + 1 < (int64_t)(j0 + 16) &&
        ti->pmax[0] + 1 < (int64_t)n) {
        shift = true;
        c->perturb = false;
    }
    const bool boundary = shift || ti->nvalid < 16 || (int64_t)j0 <= ti->pmax[ti->nvalid - 1] || j0 + 16 > n;
    if (boundary) {
        uint8_t inv[32] __attribute__((aligned(8)));
        for (uint64_t i = 0; i < 16; ++i) {
            uint64_t valid = 0;
            if (i < ti->nvalid) {
                int64_t lo = ti->pmax[i] + 1 - (int64_t)j0;
                int64_t hi = (int64_t)n - (int64_t)j0;
                lo = lo < 0 ? 0 : lo;
                hi = hi > 16 ? 16 : hi;
                if (shift && lo >= 1 && hi > lo) {
                    --lo;
                    --hi;
                }
                if (hi > lo) {
                    valid = ((1ull << hi) - 1) & ~((1ull << lo) - 1);
                    cnt += (uint64_t)(hi - lo);
                }
            }
            inv[2 * i] = (uint8_t)(~valid & 0xFF);
            inv[2 * i + 1] = (uint8_t)((~valid >> 8) & 0xFF);
        }
        mask_tile(inv);
    } else {
        cnt = 256;
    }
    reduce_tile(c->buf);
    int32_t tmax = INT32_MIN;
    for (uint64_t l = 0; l < 8; ++l) {
        c->acc.sq += c->buf[128 + l];
        c->acc.sum += (int32_t)c->buf[136 + l];
        const int32_t v = (int32_t)c->buf[144 + l];
        tmax = v > tmax ? v : tmax;
    }
    c->acc.count += cnt;
    if (cnt && tmax >= c->acc.best) {
        recompute(c, ti, J);
        __asm__ __volatile__(TOUCH_ALL STORE_ALL : : "r"(c->buf) : "memory");
        best_scan(c, ti, J);
        ++c->best_scans;
    }
}

/* ---------------------------------------------------------------- SPP_F_EPI_HIDE: the epilogue in pieces

   Output tile J's last op writes f0..f31; the next output tile's first S-1 ops accumulate in TenC and leave them
   alone, so J's epilogue runs in NCHUNK pieces between those ops, and all of it before the next last op is issued
   (the PRM needs no wait between a vector instruction and a later tensor op). Errata 1.29: type F by construction,
   as in M1 (a TensorWait 7 after the last op, then TOUCH_ALL before any vector instruction; the ops in between have
   DST = 0 and write no f register); types A to C inside the pieces as in reduce_tile, and every piece ends with a
   taken branch, so a register a piece writes is read only after one. The reduction spills rows 12-15 (f24..f31,
   256 B) instead of 16 registers (512 B, as much as hart 0's L1), and keeps its three accumulators in registers:
   SQ f24, SUM f25, MAX f0. A tile whose maximum reaches the running best is rescanned at the end of the row tile
   (the tensor unit is busy with the next tile until then): the rescans see a best that may be lower than M1's at
   that point, so they are a superset of M1's, and the record (best, rank, tie flag, sums, count) is the same. */
#define NCHUNK 8

struct Pend {
    uint64_t J, seq, step, cnt;
    bool active, ready;  // ready: J's last op is complete and TOUCH_ALL ran
};

// One group of 8 registers (4 rows) at f16..f23, reduced into SQ f24, SUM f25, MAX f0 with f1..f12 as temporaries.
#define REDUCE_G16                                                                                              \
    "fmul.pi f1, f16, f16\n fmul.pi f2, f17, f17\n fmul.pi f3, f18, f18\n fmul.pi f4, f19, f19\n"               \
    "fmul.pi f5, f20, f20\n fmul.pi f6, f21, f21\n fmul.pi f7, f22, f22\n fmul.pi f8, f23, f23\n" TAKEN         \
    "fadd.pi f1, f1, f2\n fadd.pi f3, f3, f4\n fadd.pi f5, f5, f6\n fadd.pi f7, f7, f8\n"                       \
    "fadd.pi f9, f16, f17\n fadd.pi f10, f18, f19\n fadd.pi f11, f20, f21\n fadd.pi f12, f22, f23\n"            \
    "fmax.pi f16, f16, f17\n fmax.pi f18, f18, f19\n fmax.pi f20, f20, f21\n fmax.pi f22, f22, f23\n" TAKEN     \
    "fadd.pi f1, f1, f3\n fadd.pi f5, f5, f7\n fadd.pi f9, f9, f10\n fadd.pi f11, f11, f12\n"                   \
    "fmax.pi f16, f16, f18\n fmax.pi f20, f20, f22\n" TAKEN                                                     \
    "fadd.pi f1, f1, f5\n fadd.pi f9, f9, f11\n fmax.pi f16, f16, f20\n" TAKEN                                  \
    "fadd.pi f24, f24, f1\n fadd.pi f25, f25, f9\n fmax.pi f0, f0, f16\n" TAKEN

// piece 1: spill rows 12-15 (f24..f31) to buf[0..63]
INLINE void epi_spill(uint32_t* buf)
{
    __asm__ __volatile__(
        "fsw.ps f24, 0(%0)\n   fsw.ps f25, 32(%0)\n  fsw.ps f26, 64(%0)\n  fsw.ps f27, 96(%0)\n"
        "fsw.ps f28, 128(%0)\n fsw.ps f29, 160(%0)\n fsw.ps f30, 192(%0)\n fsw.ps f31, 224(%0)\n" TAKEN
        : : "r"(buf) : "memory", FREGS);
}

// piece 2: rows 0-3 (f0..f7), temporaries f24..f31: SQ f24, SUM f25, MAX f0
INLINE void epi_red_a(void)
{
    __asm__ __volatile__(
        "fmul.pi f24, f0, f0\n fmul.pi f25, f1, f1\n fmul.pi f26, f2, f2\n fmul.pi f27, f3, f3\n"
        "fmul.pi f28, f4, f4\n fmul.pi f29, f5, f5\n fmul.pi f30, f6, f6\n fmul.pi f31, f7, f7\n" TAKEN
        "fadd.pi f24, f24, f25\n fadd.pi f26, f26, f27\n fadd.pi f28, f28, f29\n fadd.pi f30, f30, f31\n"
        "fadd.pi f25, f0, f1\n fadd.pi f27, f2, f3\n fadd.pi f29, f4, f5\n fadd.pi f31, f6, f7\n"
        "fmax.pi f0, f0, f1\n fmax.pi f2, f2, f3\n fmax.pi f4, f4, f5\n fmax.pi f6, f6, f7\n" TAKEN
        "fadd.pi f24, f24, f26\n fadd.pi f28, f28, f30\n fadd.pi f25, f25, f27\n fadd.pi f29, f29, f31\n"
        "fmax.pi f0, f0, f2\n fmax.pi f4, f4, f6\n" TAKEN
        "fadd.pi f24, f24, f28\n fadd.pi f25, f25, f29\n fmax.pi f0, f0, f4\n" TAKEN
        : : : "memory", FREGS);
}

// piece 3: rows 4-7 (f8..f15), temporaries f1..f7, f26..f30
INLINE void epi_red_b(void)
{
    __asm__ __volatile__(
        "fmul.pi f1, f8, f8\n fmul.pi f2, f9, f9\n fmul.pi f3, f10, f10\n fmul.pi f4, f11, f11\n"
        "fmul.pi f5, f12, f12\n fmul.pi f6, f13, f13\n fmul.pi f7, f14, f14\n fmul.pi f26, f15, f15\n" TAKEN
        "fadd.pi f1, f1, f2\n fadd.pi f3, f3, f4\n fadd.pi f5, f5, f6\n fadd.pi f7, f7, f26\n"
        "fadd.pi f27, f8, f9\n fadd.pi f28, f10, f11\n fadd.pi f29, f12, f13\n fadd.pi f30, f14, f15\n"
        "fmax.pi f8, f8, f9\n fmax.pi f10, f10, f11\n fmax.pi f12, f12, f13\n fmax.pi f14, f14, f15\n" TAKEN
        "fadd.pi f1, f1, f3\n fadd.pi f5, f5, f7\n fadd.pi f27, f27, f28\n fadd.pi f29, f29, f30\n"
        "fmax.pi f8, f8, f10\n fmax.pi f12, f12, f14\n" TAKEN
        "fadd.pi f1, f1, f5\n fadd.pi f27, f27, f29\n fmax.pi f8, f8, f12\n" TAKEN
        "fadd.pi f24, f24, f1\n fadd.pi f25, f25, f27\n fmax.pi f0, f0, f8\n" TAKEN
        : : : "memory", FREGS);
}

// pieces 4 and 6: rows 8-11 (f16..f23), then the reloaded rows 12-15 in the same registers
INLINE void epi_red_c(void)
{
    __asm__ __volatile__(REDUCE_G16 : : : "memory", FREGS);
}

// piece 5: reload rows 12-15 into f16..f23 (errata 1.29 type A: an fmv.x.w of each, then another instruction)
INLINE void epi_reload(const uint32_t* buf)
{
    __asm__ __volatile__(
        "flw.ps f16, 0(%0)\n   flw.ps f17, 32(%0)\n  flw.ps f18, 64(%0)\n  flw.ps f19, 96(%0)\n"
        "flw.ps f20, 128(%0)\n flw.ps f21, 160(%0)\n flw.ps f22, 192(%0)\n flw.ps f23, 224(%0)\n"
        "fmv.x.w x0, f16\n fmv.x.w x0, f17\n fmv.x.w x0, f18\n fmv.x.w x0, f19\n"
        "fmv.x.w x0, f20\n fmv.x.w x0, f21\n fmv.x.w x0, f22\n fmv.x.w x0, f23\n" TAKEN
        : : "r"(buf) : "memory", FREGS);
}

// after piece 6: the lanes of SQ, SUM and MAX to buf[64..87]
INLINE void epi_store_acc(uint32_t* buf)
{
    __asm__ __volatile__("fsw.ps f24, 256(%0)\n fsw.ps f25, 288(%0)\n fsw.ps f0, 320(%0)\n" : : "r"(buf) : "memory",
                         FREGS);
}

// The staircase and padding mask of output tile J (M1's epilogue, plain C, so it may be called): inv[] gets each
// register's lanes to clear; returns the valid entries (cnt) and whether any lane is cleared.
static bool mask_bits(struct T0* c, const struct TileInfo* ti, uint64_t J, uint8_t* inv, uint64_t* cnt_out)
{
    const uint64_t n = c->n, j0 = 16 * J;
    uint64_t cnt = 0;
    bool shift = false;
    if (c->perturb && ti->nvalid > 0 && (int64_t)j0 <= ti->pmax[0] && ti->pmax[0] + 1 < (int64_t)(j0 + 16) &&
        ti->pmax[0] + 1 < (int64_t)n) {
        shift = true;
        c->perturb = false;
    }
    const bool boundary = shift || ti->nvalid < 16 || (int64_t)j0 <= ti->pmax[ti->nvalid - 1] || j0 + 16 > n;
    if (!boundary) {
        *cnt_out = 256;
        return false;
    }
    for (uint64_t i = 0; i < 16; ++i) {
        uint64_t valid = 0;
        if (i < ti->nvalid) {
            int64_t lo = ti->pmax[i] + 1 - (int64_t)j0;
            int64_t hi = (int64_t)n - (int64_t)j0;
            lo = lo < 0 ? 0 : lo;
            hi = hi > 16 ? 16 : hi;
            if (shift && lo >= 1 && hi > lo) {
                --lo;
                --hi;
            }
            if (hi > lo) {
                valid = ((1ull << hi) - 1) & ~((1ull << lo) - 1);
                cnt += (uint64_t)(hi - lo);
            }
        }
        inv[2 * i] = (uint8_t)(~valid & 0xFF);
        inv[2 * i + 1] = (uint8_t)((~valid >> 8) & 0xFF);
    }
    *cnt_out = cnt;
    return true;
}

// piece 0: the dump and the mask of the staircase and the padding (M1's epilogue after its TOUCH_ALL); sets cnt.
// Every function that runs a piece is always inlined into the tile loop: a called function whose asm clobbers the
// f registers saves and restores the callee-saved ones (f8, f9, f18..f27) around its body, which would undo the
// piece's work before the next piece reads it.
INLINE void epi_mask(struct T0* c, const struct TileInfo* ti, struct Pend* pd)
{
    if (c->dump) {
        const uint64_t d = c->a->dump + pd->seq * SPP_TILE_BYTES;
        __asm__ __volatile__(STORE_ALL : : "r"(d) : "memory");
    }
    uint8_t inv[32] __attribute__((aligned(8)));
    if (mask_bits(c, ti, pd->J, inv, &pd->cnt)) {
        mask_tile(inv);
    }
}

// piece 7: the lanes into the hart's sums; a tile that could hold a new best (or tie it) is marked for a rescan
// (plain C: it may be called)
static void epi_acc(struct T0* c, const struct TileInfo* ti, const struct Pend* pd, uint64_t* resc)
{
    int32_t tmax = INT32_MIN;
    for (uint64_t l = 0; l < 8; ++l) {
        c->acc.sq += c->buf[64 + l];
        c->acc.sum += (int32_t)c->buf[72 + l];
        const int32_t v = (int32_t)c->buf[80 + l];
        tmax = v > tmax ? v : tmax;
    }
    c->acc.count += pd->cnt;
    if (pd->cnt && tmax >= c->acc.best) {
        const uint64_t o = pd->J - ti->J0;
        resc[o >> 6] |= 1ull << (o & 63);
    }
}

// The last op of the pending tile is complete (a TensorWait 7 after it): errata 1.29 type F, then ready.
INLINE void epi_ready(struct Pend* pd)
{
    __asm__ __volatile__(TOUCH_ALL : : : "memory");
    pd->ready = true;
}

// Runs the pending epilogue's pieces up to `target` (exclusive); a no-op unless it is ready.
INLINE void epi_run(struct T0* c, const struct TileInfo* ti, struct Pend* pd, uint64_t target, uint64_t* resc)
{
    if (!pd->active || !pd->ready) {
        return;
    }
    while (pd->step < target) {
        switch (pd->step) {
        case 0: epi_mask(c, ti, pd); break;
        case 1: epi_spill(c->buf); break;
        case 2: epi_red_a(); break;
        case 3: epi_red_b(); break;
        case 4: epi_red_c(); break;
        case 5: epi_reload(c->buf); break;
        case 6:
            epi_red_c();
            epi_store_acc(c->buf);
            break;
        default: epi_acc(c, ti, pd, resc); break;
        }
        ++pd->step;
    }
    if (pd->step >= NCHUNK) {
        pd->active = false;
    }
}

/* The pieces due before op s of an output tile, whose predecessor's epilogue is pending: all of them before the op
   that writes f0..f31 (s = S-1; if the predecessor's last op has not been waited for, the wait comes first), else
   those of slot s-1 (op s-1 is in flight). The only call site in a tile loop (with the flush at its end), since
   each call site is a copy of every piece. */
INLINE void epi_slot(struct T0* c, const struct TileInfo* ti, struct Pend* pd, uint64_t s, uint64_t* resc)
{
    if (!pd->active) {
        return;
    }
    if (s + 1 == c->S) {
        if (!pd->ready) {
            t_wait(7);
            epi_ready(pd);
        }
        epi_run(c, ti, pd, NCHUNK, resc);
    } else if (s >= 1) {
        epi_run(c, ti, pd, c->tgt[s - 1], resc);
    }
}

// The row tile's rescans (deferred): each marked output tile is recomputed and scanned as in M1.
static void rescans(struct T0* c, const struct TileInfo* ti, const uint64_t* resc)
{
    const uint64_t nJ = c->a->nJ;
    for (uint64_t J = ti->J0; J < nJ; ++J) {
        const uint64_t o = J - ti->J0;
        if ((resc[o >> 6] >> (o & 63)) & 1) {
            recompute(c, ti, J);
            __asm__ __volatile__(TOUCH_ALL STORE_ALL : : "r"(c->buf) : "memory");
            best_scan(c, ti, J);
            ++c->best_scans;
        }
    }
}

INLINE void pend_start(const struct T0* c, struct Pend* pd, uint64_t J, uint64_t seq)
{
    pd->active = !c->noepi;
    pd->ready = false;
    pd->J = J;
    pd->seq = seq;
    pd->step = 0;
}

/* One row tile, SPP_F_EPI_HIDE, A resident (S <= 3; A already in L1 scratchpad lines 0..16S-1). */
static void tile_hide_res(struct T0* c, const struct TileInfo* ti, uint64_t seq)
{
    const uint64_t S = c->S, nJ = c->a->nJ;
    struct Pend pd = { 0, 0, 0, 0, false, false };
    uint64_t resc[2] = { 0, 0 };
    for (uint64_t J = ti->J0; J < nJ; ++J) {
        if (pd.active) {
            t_wait(7);  // J-1's last op
            epi_ready(&pd);
        }
        for (uint64_t s = 0; s < S; ++s) {
            epi_slot(c, ti, &pd, s, resc);
            t_load(0, xb_addr(c, J, s), 0, 1);  // B -> TenB, paired with the next TensorIMA8A32
            t_fma(ima8_word(16 * s, s == 0, s + 1 == S));
        }
        c->ops += S;
        pend_start(c, &pd, J, seq + J - ti->J0);
    }
    t_wait(7);
    if (pd.active) {
        epi_ready(&pd);
        epi_run(c, ti, &pd, NCHUNK, resc);
    }
    if (resc[0] | resc[1]) {
        CALL_GUARD();
        rescans(c, ti, resc);
    }
}

/* One row tile, SPP_F_EPI_HIDE, A streamed from the staging buffer at ti->A with 2 L1 buffers (M1's order: op i's
   buffer i & 1, loaded with id i & 1 once the FMA that last read it, op i-1, is complete). The pieces of slot s-1
   run before op s's TensorWait 7, while op s-1 computes. */
static void tile_hide_str(struct T0* c, const struct TileInfo* ti, uint64_t seq, bool nowait)
{
    const uint64_t S = c->S, nJ = c->a->nJ;
    struct Pend pd = { 0, 0, 0, 0, false, false };
    uint64_t resc[2] = { 0, 0 };
    t_wait(7);
    t_load(0, ti->A, 0, 0);
    uint64_t i = 0;
    for (uint64_t J = ti->J0; J < nJ; ++J) {
        for (uint64_t s = 0; s < S; ++s, ++i) {
            const uint64_t bsel = i & 1;
            const bool more = s + 1 < S || J + 1 < nJ;
            epi_slot(c, ti, &pd, s, resc);
            if (more && !nowait) {
                t_wait(7);
            }
            if (s == 0 && pd.active) {  // J-1's last op (issued just before) is complete
                if (nowait) {
                    t_wait(7);
                }
                epi_ready(&pd);
            }
            if (more) {
                const uint64_t sn = s + 1 < S ? s + 1 : 0;
                t_load(16 * (bsel ^ 1), ti->A + sn * SPP_TILE_BYTES, bsel ^ 1, 0);
            }
            t_wait(bsel);
            t_load(0, xb_addr(c, J, s), 0, 1);
            t_fma(ima8_word(16 * bsel, s == 0, s + 1 == S));
        }
        c->ops += S;
        pend_start(c, &pd, J, seq + J - ti->J0);
    }
    t_wait(7);
    if (pd.active) {
        epi_ready(&pd);
        epi_run(c, ti, &pd, NCHUNK, resc);
    }
    if (resc[0] | resc[1]) {  // A from the staging buffer (not yet released), into L1 scratchpad lines 32-47
        CALL_GUARD();
        rescans(c, ti, resc);
    }
    t_wait(0);
    t_wait(1);
}

/* One row tile, SPP_F_ABUF3 (A streamed; the epilogue always in pieces): op i reads L1 scratchpad buffer i % 3
   (lines 16 (i % 3) ..), loaded with id i & 1. Ops go in pairs (2p, 2p+1): the pending pieces (both FMAs of the
   previous pair in flight), one TensorWait 7 (every earlier FMA complete), the A of op 2p+1 into its buffer (last
   read by op 2p-2), op 2p, the A of op 2p+2 into its buffer (last read by op 2p-1), op 2p+1. Each FMA waits
   (TensorWait 0 or 1) for its own A load, and no load overwrites a buffer that an FMA not yet waited for reads (the
   PRM's rule, which sys_emu's L1 scratchpad checker enforces). An output tile's last op (DST = 1) at an even index
   is followed by the next tile's first op (MUL = 1) with no TensorWait 7 between: the PRM needs none between
   tensor ops, but M1 never issued that sequence on silicon. If m4d alone mismatches on a card, the first thing to
   try is a t_wait(7) after every last op (review of M4, finding 6). */
static void tile_abuf3(struct T0* c, const struct TileInfo* ti, uint64_t seq)
{
    const uint64_t S = c->S, nJ = c->a->nJ;
    const uint64_t nops = (nJ - ti->J0) * S;
    struct Pend pd = { 0, 0, 0, 0, false, false };
    uint64_t resc[2] = { 0, 0 };
    t_wait(7);
    t_load(0, ti->A, 0, 0);  // op 0: buffer 0, id 0
    uint64_t J = ti->J0, s = 0;  // op i = (J, s)
    uint64_t Jn = J, sn = 0;     // op i+1
    uint64_t lb = 0;             // buffer of op i
    for (uint64_t i = 0; i < nops; ++i) {
        const bool first = (i & 1) == 0;
        if (first || s + 1 == S) {
            epi_slot(c, ti, &pd, s, resc);
        }
        if (first) {
            t_wait(7);  // every FMA before op i is complete
            if (pd.active && !pd.ready) {
                epi_ready(&pd);
            }
        }
        if (++sn == S) {
            sn = 0;
            ++Jn;
        }
        const uint64_t nb = lb == 2 ? 0 : lb + 1;
        if (first && i + 1 < nops) {
            t_load(16 * nb, ti->A + sn * SPP_TILE_BYTES, 1, 0);  // op i+1 (odd): id 1
        }
        t_wait(i & 1);
        t_load(0, xb_addr(c, J, s), 0, 1);
        t_fma(ima8_word(16 * lb, s == 0, s + 1 == S));
        if (!first && i + 1 < nops) {
            t_load(16 * nb, ti->A + sn * SPP_TILE_BYTES, 0, 0);  // op i+1 (even): id 0
        }
        if (s + 1 == S) {
            c->ops += S;
            pend_start(c, &pd, J, seq + J - ti->J0);
        }
        lb = nb;
        J = Jn;
        s = sn;
    }
    t_wait(7);
    if (pd.active) {
        epi_ready(&pd);
        epi_run(c, ti, &pd, NCHUNK, resc);
    }
    if (resc[0] | resc[1]) {
        CALL_GUARD();
        rescans(c, ti, resc);
    }
    t_wait(0);
    t_wait(1);
}

NOINLINE void run_t0(const struct SppArgs* a, uint64_t shire, uint64_t mi, uint64_t g, uint32_t* err,
                     struct T0* c, uint64_t* waitc, uint32_t* copyc)
{
    const uint64_t t_start = cycles();
    const uint64_t S = a->S, nJ = a->nJ, k1 = a->k - 1, nrows = a->nrows, P = a->per_shire;
    const uint64_t nbuf = a->nbuf, epoch = a->epoch;
    const bool nowait = (a->flags & SPP_F_NOWAIT_A) != 0;
    const uint64_t gen_line = a->sync + g * SPP_SYNC_BYTES, rel_line = gen_line + 64;
    c->a = a;
    c->S = S;
    c->n = a->n;
    c->xb_scp = SPP_SCP_LOCAL(a->xb_line * 64);
    c->resident = S <= 3;
    c->dump = (a->flags & SPP_F_DUMP) != 0;
    c->noepi = (a->flags & SPP_F_NOEPI) != 0;
    c->perturb = (a->flags & SPP_F_PERTURB_MASK) != 0 && SPP_PERTURB_SLOT(a->flags) == g;
    // M4 (flags; none set = M1): the epilogue in pieces, 3 A buffers (streamed A only; always with the pieces)
    const bool abuf3 = (a->flags & SPP_F_ABUF3) != 0 && !c->resident && !nowait;
    const bool hide = (a->flags & SPP_F_EPI_HIDE) != 0 || abuf3;
    {
        // pieces done after slot s (op s of the next output tile in flight): one per slot, or more when the
        // S-1 slots are fewer than the pieces
        const uint64_t nslots = S > 1 ? S - 1 : 1;
        for (uint64_t s = 0; s < S; ++s) {
            uint64_t t = ((s + 1) * NCHUNK + nslots - 1) / nslots;
            t = t < s + 1 ? s + 1 : t;
            c->tgt[s] = (uint8_t)(t < NCHUNK ? t : NCHUNK);
        }
    }
    __asm__ __volatile__("mov.m.x m0, zero, 0xff\n" : : : "memory");

    // Copy-in: this minion's share of X_B (1 KB chunks mi, mi+P, ..) into the shire's scratchpad.
    uint64_t id = 0, issued = 0;
    for (uint64_t ch = mi; ch < nJ * S; ch += P, ++issued, id ^= 1) {
        if (issued >= 2) {
            t_wait(2 + id);
        }
        t_load_l2scp(a->xb_line + 16 * ch, a->xb + ch * SPP_TILE_BYTES, id);
    }
    t_wait(2);
    t_wait(3);
    if (!shire_barrier(shire, P, a->poll_limit)) {
        *err |= SPP_ERR_BARRIER;
        *copyc = (uint32_t)(cycles() - t_start);
        signal_abort(rel_line, epoch);  // hart 1 stops waiting for buffers
        return;
    }
    *copyc = (uint32_t)(cycles() - t_start);

    const struct SppMinion* mp = (const struct SppMinion*)a->minions + g;
    const struct SppBlock* blocks = (const struct SppBlock*)a->blocks;
    const uint64_t sbytes = 16 * S * 64;
    // The same staging lines hart 1 writes; in the scratchpad, read through the local alias (finding R1-4).
    const uint64_t stage0 = a->stage_global ? stage_base(a, shire, mi, g) : SPP_SCP_LOCAL(a->stage + mi * a->stage_stride);
    uint64_t q = 0, seq = mp->dump_base, polls = 0;
    struct TileInfo ti;
    for (uint32_t b = 0; b < mp->nblocks; ++b) {
        const struct SppBlock* blk = blocks + mp->first_block + b;
        uint64_t r[SPP_KMAX];
        for (uint64_t e = 0; e < k1; ++e) {
            r[e] = blk->sub[e];
        }
        uint64_t rank = 16ull * blk->tile0;
        for (uint32_t t = 0; t < blk->ntiles; ++t, ++q) {
            ti.rank0 = rank;
            ti.nvalid = 0;
            for (uint64_t i = 0; i < 16; ++i, ++rank) {
                ti.pmax[i] = sub_max(r, k1);
                if (rank < nrows) {
                    sub_next(r, k1);
                    ++ti.nvalid;
                }
            }
            ti.J0 = (uint64_t)(ti.pmax[0] + 1) >> 4;
            ti.A = stage0 + (nbuf == 2 ? (q & 1) : 0) * sbytes;
            const uint64_t t0 = cycles();
            const int w = wait_count(gen_line, epoch, q + 1, a->poll_limit, &polls);
            if (w <= 0) {
                if (w == 0) {
                    *err |= SPP_ERR_POLL;
                    signal_abort(rel_line, epoch);  // hart 1 stops waiting for buffers
                } else {
                    *err |= SPP_ERR_ABORTED;
                }
                goto out;
            }
            *waitc += cycles() - t0;
            if (hide) {
                if (c->resident) {
                    t_wait(7);  // the previous tile's FMAs no longer read lines 0..16S-1
                    for (uint64_t s = 0; s < S; ++s) {
                        t_load(16 * s, ti.A + s * SPP_TILE_BYTES, 0, 0);
                        t_wait(0);
                    }
                    l2_write(rel_line, (epoch << 32) | (q + 1));  // A is in L1 scratchpad
                    CALL_GUARD();
                    tile_hide_res(c, &ti, seq);
                } else {
                    CALL_GUARD();
                    if (abuf3) {
                        tile_abuf3(c, &ti, seq);
                    } else {
                        tile_hide_str(c, &ti, seq, nowait);
                    }
                    l2_write(rel_line, (epoch << 32) | (q + 1));  // after the rescans, which reload A from it
                }
            } else if (c->resident) {
                t_wait(7);  // the previous tile's FMAs no longer read lines 0..16S-1
                for (uint64_t s = 0; s < S; ++s) {
                    t_load(16 * s, ti.A + s * SPP_TILE_BYTES, 0, 0);
                    t_wait(0);
                }
                l2_write(rel_line, (epoch << 32) | (q + 1));  // A is in L1 scratchpad: hart 1 may reuse the buffer
                for (uint64_t J = ti.J0; J < nJ; ++J) {
                    for (uint64_t s = 0; s < S; ++s) {
                        t_load(0, xb_addr(c, J, s), 0, 1);  // B -> TenB, paired with the next TensorIMA8A32
                        t_fma(ima8_word(16 * s, s == 0, s + 1 == S));
                    }
                    c->ops += S;
                    epilogue(c, &ti, J, seq + J - ti.J0);
                }
            } else {
                // A streamed: op i reads L1 scratchpad lines 16*(i&1).., loaded with id i&1; the load of op i+1
                // is issued before op i's FMA, once the FMA that last read its buffer (op i-1) is done.
                t_wait(7);
                t_load(0, ti.A, 0, 0);
                uint64_t i = 0;
                for (uint64_t J = ti.J0; J < nJ; ++J) {
                    for (uint64_t s = 0; s < S; ++s, ++i) {
                        const uint64_t bsel = i & 1;
                        const bool more = s + 1 < S || J + 1 < nJ;
                        if (more) {
                            if (!nowait) {
                                t_wait(7);
                            }
                            const uint64_t sn = s + 1 < S ? s + 1 : 0;
                            t_load(16 * (bsel ^ 1), ti.A + sn * SPP_TILE_BYTES, bsel ^ 1, 0);
                        }
                        t_wait(bsel);
                        t_load(0, xb_addr(c, J, s), 0, 1);
                        t_fma(ima8_word(16 * bsel, s == 0, s + 1 == S));
                    }
                    c->ops += S;
                    epilogue(c, &ti, J, seq + J - ti.J0);
                }
                t_wait(0);
                t_wait(1);
                l2_write(rel_line, (epoch << 32) | (q + 1));
            }
            seq += nJ - ti.J0;
        }
    }
out:
    t_wait(7);
}

/* ---------------------------------------------------------------- entry */

INLINE bool args_ok(const struct SppArgs* a)
{
    return a->k >= 1 && a->k <= SPP_KMAX && a->n >= a->k && a->n <= SPP_NMAX && a->S >= 1 && a->S <= SPP_SMAX &&
           a->m >= 1 && a->m <= 64 * a->S && a->nJ == (a->n + 15) / 16 && a->per_shire >= 1 && a->per_shire <= 32 &&
           (a->mode != SPP_TENSOR || a->nbuf == 1 || a->nbuf == 2);
}

int64_t entry_point(const struct SppArgs* args)
{
    const uint64_t hart = get_hart_id();
    const uint64_t shire = hart >> 6, mi = (hart >> 1) & 31, thread = hart & 1;
    if (shire >= 32 || !((args->shire_mask >> shire) & 1) || mi >= args->per_shire) {
        return 0;
    }
    const uint64_t mode = args->mode;
    if (mode == SPP_SCALAR && thread == 1 && !(args->flags & SPP_F_TWOHART)) {
        return 0;  // one hart per minion
    }
    const uint64_t g = shire * 32 + mi;
    const uint64_t t_entry = thread == 0 ? cycles() : 0;  // erratum 1.23: never both harts on the counter
    uint32_t err = 0, copyc = 0;
    uint64_t count = 0, wait = 0, work = 0;
    struct T0 c;
    c.acc.sum = 0;
    c.acc.sq = 0;
    c.acc.count = 0;
    c.acc.best_rank = ~0ull;
    c.acc.best = INT32_MIN;
    c.acc.tie = 0;
    c.ops = 0;
    c.perturb = false;
    c.best_scans = 0;
    if (!args_ok(args)) {
        err |= SPP_ERR_ARGS;
    } else if (mode == SPP_SCALAR) {
        run_scalar(args, g, thread, &c.acc, &work);
        count = c.acc.count;
    } else if (mode == SPP_TENSOR && thread == 0) {
        run_t0(args, shire, mi, g, &err, &c, &wait, &copyc);
        count = c.acc.count;
        work = c.ops;
    } else if (mode == SPP_TENSOR && (args->flags & SPP_F_GEN_INC) && args->k >= 2) {
        run_gen_inc(args, shire, mi, g, &err, &count, &wait);
    } else if (mode == SPP_TENSOR) {
        run_gen(args, shire, mi, g, &err, &count, &wait);
    } else {
        err |= SPP_ERR_ARGS;
    }
    const uint64_t te = tensor_error();
    if (te) {
        err |= SPP_ERR_TENSOR;
    }
    volatile struct SppRecord* r = (volatile struct SppRecord*)args->records + hart;
    r->sum_c = c.acc.sum;
    r->sum_c2 = c.acc.sq;
    r->count = count;
    r->best_rank = c.acc.best_rank;
    r->best_c = c.acc.best;
    r->cycles = thread == 0 ? cycles() - t_entry : 0;
    r->wait = wait;
    r->work = (uint32_t)work;
    r->copy_cycles = copyc;
    const uint32_t tie = (thread == 0 || mode == SPP_SCALAR) && c.acc.tie ? SPP_INFO_TIE : 0;
    r->status = (uint32_t)((args->epoch & 0xFFFF) << 16) | ((uint32_t)(te & 0xFF) << 8) | tie | (err & 0x7F);
    return 0;
}
