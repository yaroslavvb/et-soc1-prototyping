/*-------------------------------------------------------------------------
 * One forward pass of an int8 MLP over MNIST on the ET-SoC-1 (E202; see ../mnistmlp_args.h and ../README.md).
 *
 * Hart 0 of each working minion takes groups of 16 images through 784 -> 1792 -> 1792 -> 1792 -> 1792 -> 10:
 *  - The P working minions of a shire walk the network's 449 weight chunks together (a chunk = one 16-column block
 *    of one layer: 13 or 28 B tiles of 1 KiB). Chunk u+1 is copied into staging buffer S[(u+1) & 1] while chunk u is
 *    computed from S[u & 1] (u counts chunks across rounds, so the two buffers alternate even though 449 is odd);
 *    each minion copies the tiles i with i mod P == its index, with TensorLoadL2Scp from the shire that keeps the
 *    chunk resident (scp staging) or from the packed weights in DRAM (MLP_F_STAGE_DRAM, the registered fallback).
 *    A shire barrier ends every chunk: it releases S[u & 1] for the copy two chunks later and proves chunk u+1
 *    complete.
 *  - scp staging only: at launch start each shire copies the chunks it keeps from DRAM into its resident region,
 *    meets at a shire barrier and then at one chip barrier (workloads/onchip's credit-release shape: one global
 *    atomic per shire, nobody spins on it).
 *  - The tile loop is sparse parity's streamed-A TensorIMA8A32 loop (M1's order, exact on silicon) with UA = 1:
 *    A (uint8 activations, 16 images x 64) from the minion's own buffer into L1 scratchpad lines 0-15 / 16-31,
 *    B (int8 weights, 64 k x 16 columns) from the staging buffer into TenB, paired with the next TensorIMA8A32;
 *    int32 accumulation in TenC; the last operation writes C to f0..f31 (row i in f[2i], f[2i+1]).
 *  - Hidden layers: y = sat_u8(((acc + Bp) * M) >> 32) with fadd.pi, fmulh.pi (the upper 32 bits of the signed
 *    64-bit product), fsatu8.pi (ReLU and clamp), fpackrepb.pi and one masked for.pi per row that puts columns 8-15
 *    beside columns 0-7. Column blocks go in pairs: an even block's 16 x 16 bytes wait in the hart's stack, and the
 *    odd block writes each image's 32 bytes (both blocks) into the next layer's A tile with one fswg.ps (tile c / 4,
 *    bytes 32 ((c / 2) mod 2) .. +31 of each image's line). No masked contiguous store: erratum 1.8 ignores the mask
 *    of contiguous L1-bypassing stores (fswg.ps), and sys_emu's A0 model does too. No TensorStore into the scratchpad
 *    for data the kernel reads back: the shire cache's coalescing buffer would need a drain first.
 *  - The output layer: the C tile goes to the hart's stack (fsw.ps), scalar code adds B and takes the first index of
 *    the maximum (strict >, numpy's argmax rule), and the group's 64 B label line (labels, group, epoch, checksum of
 *    the 160 logits) is written with plain stores, as every lab record is.
 *
 * No floating point anywhere (the requantization is integer), so none of the 13 trapping instructions; no libc; no
 * double. Only hart 0 reads hpmcounter3 (erratum 1.23), four back-to-back reads, late-carry corrected. Errata 1.29:
 * TOUCH_ALL after the last TensorWait 7 before vector code (type F); every vector register is read 8 or more
 * instructions after it was written or after a taken branch (types B and C); every flw.ps target gets an fmv.x.w and
 * one more instruction before use (type A). Every wait is polled with a limit: a hart that gives up records the error
 * and ends its launch, and the others then fail their next barrier the same way.
 *-------------------------------------------------------------------------*/

#include <stdbool.h>
#include <stdint.h>
#include "etsoc/isa/esr_defines.h"
#include "etsoc/isa/hart.h"
#include "mnistmlp_args.h"

int64_t entry_point(const struct MlpArgs* args);

#define INLINE static inline __attribute__((always_inline))
#define NOINLINE static __attribute__((noinline))

#define FREGS                                                                                      \
    "f0", "f1", "f2", "f3", "f4", "f5", "f6", "f7", "f8", "f9", "f10", "f11", "f12", "f13", "f14", \
        "f15", "f16", "f17", "f18", "f19", "f20", "f21", "f22", "f23", "f24", "f25", "f26", "f27", \
        "f28", "f29", "f30", "f31"

// Errata 1.29 type F: after a tensor op writes the vector registers, an fmv.x.w must come before any other VPU
// instruction reads them. Touch all 32.
#define TOUCH_ALL                                                                                    \
    "fmv.x.w x0, f0\n fmv.x.w x0, f1\n fmv.x.w x0, f2\n fmv.x.w x0, f3\n fmv.x.w x0, f4\n"          \
    "fmv.x.w x0, f5\n fmv.x.w x0, f6\n fmv.x.w x0, f7\n fmv.x.w x0, f8\n fmv.x.w x0, f9\n"          \
    "fmv.x.w x0, f10\n fmv.x.w x0, f11\n fmv.x.w x0, f12\n fmv.x.w x0, f13\n fmv.x.w x0, f14\n"     \
    "fmv.x.w x0, f15\n fmv.x.w x0, f16\n fmv.x.w x0, f17\n fmv.x.w x0, f18\n fmv.x.w x0, f19\n"     \
    "fmv.x.w x0, f20\n fmv.x.w x0, f21\n fmv.x.w x0, f22\n fmv.x.w x0, f23\n fmv.x.w x0, f24\n"     \
    "fmv.x.w x0, f25\n fmv.x.w x0, f26\n fmv.x.w x0, f27\n fmv.x.w x0, f28\n fmv.x.w x0, f29\n"     \
    "fmv.x.w x0, f30\n fmv.x.w x0, f31\n"

// Errata 1.29 types B and C: a register must not be read within 8 instructions of being written unless a taken
// branch comes between. TAKEN is that branch.
#define TAKEN "j 91f\n91:\n"

// The hidden layers' requantization, rows 0-13 (f0..f27; Bp of columns 0-7 in f28, of 8-15 in f29, M in f30).
// Each step runs over all 28 registers, so every register is read 28 instructions after it was written.
#define ADD28                                                                                         \
    "fadd.pi f0, f0, f28\n fadd.pi f1, f1, f29\n fadd.pi f2, f2, f28\n fadd.pi f3, f3, f29\n"          \
    "fadd.pi f4, f4, f28\n fadd.pi f5, f5, f29\n fadd.pi f6, f6, f28\n fadd.pi f7, f7, f29\n"          \
    "fadd.pi f8, f8, f28\n fadd.pi f9, f9, f29\n fadd.pi f10, f10, f28\n fadd.pi f11, f11, f29\n"      \
    "fadd.pi f12, f12, f28\n fadd.pi f13, f13, f29\n fadd.pi f14, f14, f28\n fadd.pi f15, f15, f29\n"  \
    "fadd.pi f16, f16, f28\n fadd.pi f17, f17, f29\n fadd.pi f18, f18, f28\n fadd.pi f19, f19, f29\n"  \
    "fadd.pi f20, f20, f28\n fadd.pi f21, f21, f29\n fadd.pi f22, f22, f28\n fadd.pi f23, f23, f29\n"  \
    "fadd.pi f24, f24, f28\n fadd.pi f25, f25, f29\n fadd.pi f26, f26, f28\n fadd.pi f27, f27, f29\n"
#define OP28(OP, B)                                                                                   \
    OP " f0, f0" B "\n " OP " f1, f1" B "\n " OP " f2, f2" B "\n " OP " f3, f3" B "\n "               \
    OP " f4, f4" B "\n " OP " f5, f5" B "\n " OP " f6, f6" B "\n " OP " f7, f7" B "\n "               \
    OP " f8, f8" B "\n " OP " f9, f9" B "\n " OP " f10, f10" B "\n " OP " f11, f11" B "\n "           \
    OP " f12, f12" B "\n " OP " f13, f13" B "\n " OP " f14, f14" B "\n " OP " f15, f15" B "\n "       \
    OP " f16, f16" B "\n " OP " f17, f17" B "\n " OP " f18, f18" B "\n " OP " f19, f19" B "\n "       \
    OP " f20, f20" B "\n " OP " f21, f21" B "\n " OP " f22, f22" B "\n " OP " f23, f23" B "\n "       \
    OP " f24, f24" B "\n " OP " f25, f25" B "\n " OP " f26, f26" B "\n " OP " f27, f27" B "\n"
// With m0 = 0x0c: lanes 2-3 of f[2i] <- lanes 2-3 of f[2i+1], so f[2i]'s first 16 bytes are row i's 16 outputs.
#define MERGE14                                                                                       \
    "for.pi f0, f1, f1\n for.pi f2, f3, f3\n for.pi f4, f5, f5\n for.pi f6, f7, f7\n"                  \
    "for.pi f8, f9, f9\n for.pi f10, f11, f11\n for.pi f12, f13, f13\n for.pi f14, f15, f15\n"          \
    "for.pi f16, f17, f17\n for.pi f18, f19, f19\n for.pi f20, f21, f21\n for.pi f22, f23, f23\n"      \
    "for.pi f24, f25, f25\n for.pi f26, f27, f27\n"

// All 32 vector registers (the 16 x 16 int32 C tile: row i in f[2i], f[2i+1]) to 1 KiB at %0.
#define STORE_ALL                                                                                  \
    "fsw.ps f0, 0(%0)\n    fsw.ps f1, 32(%0)\n   fsw.ps f2, 64(%0)\n   fsw.ps f3, 96(%0)\n"          \
    "fsw.ps f4, 128(%0)\n  fsw.ps f5, 160(%0)\n  fsw.ps f6, 192(%0)\n  fsw.ps f7, 224(%0)\n"         \
    "fsw.ps f8, 256(%0)\n  fsw.ps f9, 288(%0)\n  fsw.ps f10, 320(%0)\n fsw.ps f11, 352(%0)\n"        \
    "fsw.ps f12, 384(%0)\n fsw.ps f13, 416(%0)\n fsw.ps f14, 448(%0)\n fsw.ps f15, 480(%0)\n"       \
    "fsw.ps f16, 512(%0)\n fsw.ps f17, 544(%0)\n fsw.ps f18, 576(%0)\n fsw.ps f19, 608(%0)\n"       \
    "fsw.ps f20, 640(%0)\n fsw.ps f21, 672(%0)\n fsw.ps f22, 704(%0)\n fsw.ps f23, 736(%0)\n"       \
    "fsw.ps f24, 768(%0)\n fsw.ps f25, 800(%0)\n fsw.ps f26, 832(%0)\n fsw.ps f27, 864(%0)\n"       \
    "fsw.ps f28, 896(%0)\n fsw.ps f29, 928(%0)\n fsw.ps f30, 960(%0)\n fsw.ps f31, 992(%0)\n"

// Scratchpad addresses (PRM 15.3 format 0): 0x80000000 + (shire << 23) + offset; shire 0x7F = this shire.
#define SCP_LOCAL(off) (0x80000000ull + (0x7Full << 23) + (uint64_t)(off))
#define SCP_SHIRE(s, off) (0x80000000ull + ((uint64_t)(s) << 23) + (uint64_t)(off))

/* ---------------------------------------------------------------- counters, CSRs, tensor ops */

// Four back-to-back reads (the firmware's workaround for RTLMIN-6496), then the late-carry correction: hpmcounter3
// reads 128 short when its low 7 bits are 0-10 (workloads/memprobe).
INLINE uint64_t cycles(void)
{
    uint64_t v;
    __asm__ __volatile__(".p2align 4\n csrr %0, hpmcounter3\n csrr %0, hpmcounter3\n"
                         " csrr %0, hpmcounter3\n csrr %0, hpmcounter3\n" : "=r"(v));
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

/* TensorLoadL2Scp: 16 lines from addr (DRAM or any shire's scratchpad) into this shire's L2 scratchpad starting at
   scratchpad line dst, bypassing L1 and L2. TensorWait 2 + id. */
INLINE void t_load_l2scp(uint64_t dst, uint64_t addr, uint64_t id)
{
    const uint64_t v = ((dst & 0x1FFFCull) << 46) | ((dst & 3) << 4) | (addr & 0xFFFFFFFFFFC0ull) | 15u;
    register uint64_t x31 __asm__("x31") = 64ull | (id & 1);
    __asm__ __volatile__("csrw 0x85f, %1" : : "r"(x31), "r"(v) : "memory");
}

/* TensorIMA8A32 control word (PRM 9.4): 16 A rows x 64 bytes (ACOLS 15) x 16 B columns (BCOLS 3), A unsigned
   (UA, bit 21), B signed, B streamed through TenB (bit 20), A from L1 scratchpad line astart. MUL (bit 0) starts C at
   A*B; DST (bit 23) writes C to f0..f31 instead of TenC. Type 3 (bits 3:1) = IMA8A32. */
INLINE uint64_t ima8u_word(uint64_t astart, bool first, bool last)
{
    return (3ull << 55) | (15ull << 51) | (15ull << 47) | ((uint64_t)last << 23) | (1ull << 21) | (1ull << 20) |
           ((astart & 0x3F) << 4) | (3ull << 1) | (uint64_t)first;
}

/* TensorStore from registers (PRM 9.4): `rows` rows of 16 x cols bytes, row r from f[regstart + srcinc * r] (cols 1:
   the register's first 16 B; cols 4: 64 B from two registers), to addr + r * stride, bypassing L1 and L2. TensorWait 8. */
INLINE uint64_t tstore_word(uint64_t srcinc, uint64_t cols, uint64_t rows, uint64_t addr)
{
    return (((srcinc - 1) & 3) << 62) | (((cols - 1) & 3) << 55) | (((rows - 1) & 0xF) << 51) |
           (addr & 0xFFFFFFFFFFF0ull);
}

INLINE void t_store(uint64_t word, uint64_t stride)
{
    register uint64_t x31 __asm__("x31") = stride & 0xFFFFFFFFFFF0ull;
    __asm__ __volatile__(TAKEN "csrw 0x87f, %1" : : "r"(x31), "r"(word) : "memory");
}

// Population count without libgcc (its __popcountdi2 uses the slow multiplier); called a few times a launch.
INLINE uint64_t popcount64(uint64_t x)
{
    uint64_t n = 0;
    for (; x; x &= x - 1) {
        ++n;
    }
    return n;
}

/* ---------------------------------------------------------------- barriers */

// One credit on counter 1 of this hart, by polling FCCNB (CSR 0xCC0, counter 1 in bits 31:16) with a limit.
INLINE bool take_credit1(uint64_t limit)
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

INLINE uint64_t minion_credit_mask(uint64_t P)
{
    return P >= 32 ? 0xFFFFFFFFull : ((1ull << P) - 1);
}

// The hart 0s of minions 0..P-1 of this shire: FLB 30 counts arrivals and the last gives each a credit on FCC
// counter 1 of thread 0 (workloads/sparsity, workloads/sparseparity).
INLINE bool shire_barrier(uint64_t shire, uint64_t P, uint64_t limit)
{
    uint64_t last;
    __asm__ __volatile__("csrrw %0, 0x820, %1" : "=r"(last) : "r"(((P - 1) << 5) | 30) : "memory");
    if (last) {
        *((volatile uint64_t*)ESR_SHIRE(shire, FCC_CREDINC_0) + 1) = minion_credit_mask(P);
    }
    return take_credit1(limit);
}

INLINE uint32_t amoadd_g(volatile uint32_t* p, uint32_t v)
{
    uint32_t old;
    __asm__ __volatile__("amoaddg.w %0, %1, (%2)" : "=r"(old) : "r"(v), "r"(p) : "memory");
    return old;
}

/* Chip-wide barrier (workloads/onchip): the shire's P minions meet in FLB 29, the last adds one to the DRAM counter,
   and the shire that sees the final count releases every working shire's P minions with one credit store each. */
INLINE bool chip_barrier(const struct MlpArgs* a, uint64_t P)
{
    uint64_t last;
    __asm__ __volatile__("csrrw %0, 0x820, %1" : "=r"(last) : "r"(((P - 1) << 5) | 29) : "memory");
    if (last) {
        const uint32_t seen = amoadd_g((volatile uint32_t*)a->counter, 1) + 1;
        if (seen == (uint32_t)a->nshires) {
            for (uint64_t s = 0; s < 32; ++s) {
                if ((a->shire_mask >> s) & 1) {
                    *((volatile uint64_t*)ESR_SHIRE(s, FCC_CREDINC_0) + 1) = minion_credit_mask(P);
                }
            }
        }
    }
    return take_credit1(a->poll_limit);
}

/* ---------------------------------------------------------------- the work */

// This minion's share (tiles t with t mod P == mi) of chunk c's copy into this shire's scratchpad at line dst.
INLINE uint64_t copy_share(const struct MlpArgs* a, const struct MlpChunk* c, bool dram, uint64_t dst, uint64_t P,
                           uint64_t mi, uint64_t* id)
{
    uint64_t issued = 0;
    for (uint64_t t = mi; t < c->ntiles; t += P) {
        if (issued >= 2) {
            t_wait(2 + *id);  // the copy that last used this id is complete
        }
        const uint64_t src = dram ? a->wtiles + ((uint64_t)c->wtile + t) * MLP_TILE_BYTES
                                  : SCP_SHIRE(c->owner, ((uint64_t)c->res_line + 16 * t) * 64);
        t_load_l2scp(dst + 16 * t, src, *id);
        *id ^= 1;
        ++issued;
    }
    return issued;
}

/* One C tile: n k tiles, A from the scratchpad buffer at `abuf` (local alias), B from the staging buffer at `bbuf`.
   Sparse parity's streamed-A order: op k reads L1 scratchpad lines 16 (k & 1).., loaded with id k & 1; the load of
   op k+1 is issued before op k's FMA, once the FMA that last read its lines (op k-1) is complete (TensorWait 7). */
INLINE void tile_loop(uint64_t abuf, uint64_t bbuf, uint64_t n)
{
    t_wait(7);
    t_load(0, abuf, 0, 0);
    for (uint64_t k = 0; k < n; ++k) {
        const uint64_t b = k & 1;
        if (k + 1 < n) {
            t_wait(7);
            t_load(16 * (b ^ 1), abuf + (k + 1) * MLP_TILE_BYTES, b ^ 1, 0);
        }
        t_wait(b);
        t_load(0, bbuf + k * MLP_TILE_BYTES, 0, 1);  // B -> TenB, paired with the next TensorIMA8A32
        t_fma(ima8u_word(16 * b, k == 0, k + 1 == n));
    }
    t_wait(7);  // C is in f0..f31
}

/* Hidden-layer epilogue on the C tile in f0..f31: y = sat_u8(((acc + Bp) * M) >> 32). Rows 14-15 are spilled to
   `spill` (128 B, the hart's stack) to free f28-f31 for Bp (columns 0-7, 8-15) and M. Column blocks go in pairs
   (c even, c + 1) so that every store into the scratchpad is a whole 32 bytes (two blocks of one image's A-tile line):
   fswg.ps ignores its mask (erratum 1.8; the simulator's A0 model too), and a TensorStore into the scratchpad followed
   by a TensorLoad of the same line needs the shire cache's coalescing buffer drained first (the simulator's memory
   checker stops the run otherwise; workloads/sparsity's README), so neither is used. Even block: each row's 16 bytes
   go to the hart's stack slot (row i: 32 B at slot + 32 i; full-width fsw.ps, lanes 4-7 carry no data). Odd block:
   each row's slot comes back into a free register, its lanes 4-7 take this block's 16 bytes, and one fswg.ps writes
   the 32 bytes to the next layer's A-tile line (explicit shire address, as sparse parity's staging stores). */
#define EPI_HEAD(MK)                                                                                  \
    TOUCH_ALL                                                                                         \
    "fsw.ps f28, 0(%[sp])\n fsw.ps f29, 32(%[sp])\n fsw.ps f30, 64(%[sp])\n fsw.ps f31, 96(%[sp])\n"   \
    "flw.ps f28, 0(%[b])\n flw.ps f29, 32(%[b])\n fbcx.ps f30, %[m]\n"                                \
    "fmv.x.w x0, f28\n fmv.x.w x0, f29\n"                                                             \
    TAKEN                                                                                             \
    ADD28                                                                                             \
    OP28("fmulh.pi", ", f30")                                                                         \
    OP28("fsatu8.pi", "")                                                                             \
    OP28("fpackrepb.pi", "")                                                                          \
    "mov.m.x m0, zero, " MK "\n"                                                                      \
    MERGE14                                                                                           \
    "mov.m.x m0, zero, 0xff\n"                                                                        \
    TAKEN
// Rows 14-15: Bp and M into f1, f3, f5 (free by now), the spilled rows back into f28-f31, the same four steps.
#define EPI_R1415(MK)                                                                                 \
    "for.pi f1, f28, f28\n for.pi f3, f29, f29\n for.pi f5, f30, f30\n"                               \
    "flw.ps f28, 0(%[sp])\n flw.ps f29, 32(%[sp])\n flw.ps f30, 64(%[sp])\n flw.ps f31, 96(%[sp])\n"   \
    "fmv.x.w x0, f28\n fmv.x.w x0, f29\n fmv.x.w x0, f30\n fmv.x.w x0, f31\n"                         \
    TAKEN                                                                                             \
    "fadd.pi f28, f28, f1\n fadd.pi f29, f29, f3\n fadd.pi f30, f30, f1\n fadd.pi f31, f31, f3\n"     \
    TAKEN                                                                                             \
    "fmulh.pi f28, f28, f5\n fmulh.pi f29, f29, f5\n fmulh.pi f30, f30, f5\n fmulh.pi f31, f31, f5\n" \
    TAKEN                                                                                             \
    "fsatu8.pi f28, f28\n fsatu8.pi f29, f29\n fsatu8.pi f30, f30\n fsatu8.pi f31, f31\n"             \
    TAKEN                                                                                             \
    "fpackrepb.pi f28, f28\n fpackrepb.pi f29, f29\n fpackrepb.pi f30, f30\n fpackrepb.pi f31, f31\n" \
    TAKEN                                                                                             \
    "mov.m.x m0, zero, " MK "\n"                                                                      \
    "for.pi f28, f29, f29\n for.pi f30, f31, f31\n"                                                   \
    "mov.m.x m0, zero, 0xff\n"                                                                        \
    TAKEN
#define EVEN_STORE14                                                                                  \
    "fsw.ps f0, 0(%[sl])\n fsw.ps f2, 32(%[sl])\n fsw.ps f4, 64(%[sl])\n fsw.ps f6, 96(%[sl])\n"       \
    "fsw.ps f8, 128(%[sl])\n fsw.ps f10, 160(%[sl])\n fsw.ps f12, 192(%[sl])\n fsw.ps f14, 224(%[sl])\n" \
    "fsw.ps f16, 256(%[sl])\n fsw.ps f18, 288(%[sl])\n fsw.ps f20, 320(%[sl])\n fsw.ps f22, 352(%[sl])\n" \
    "fsw.ps f24, 384(%[sl])\n fsw.ps f26, 416(%[sl])\n"
#define ODD_LOAD14                                                                                    \
    "flw.ps f1, 0(%[sl])\n flw.ps f3, 32(%[sl])\n flw.ps f5, 64(%[sl])\n flw.ps f7, 96(%[sl])\n"       \
    "flw.ps f9, 128(%[sl])\n flw.ps f11, 160(%[sl])\n flw.ps f13, 192(%[sl])\n flw.ps f15, 224(%[sl])\n" \
    "flw.ps f17, 256(%[sl])\n flw.ps f19, 288(%[sl])\n flw.ps f21, 320(%[sl])\n flw.ps f23, 352(%[sl])\n" \
    "flw.ps f25, 384(%[sl])\n flw.ps f27, 416(%[sl])\n"                                               \
    "fmv.x.w x0, f1\n fmv.x.w x0, f3\n fmv.x.w x0, f5\n fmv.x.w x0, f7\n fmv.x.w x0, f9\n"             \
    "fmv.x.w x0, f11\n fmv.x.w x0, f13\n fmv.x.w x0, f15\n fmv.x.w x0, f17\n fmv.x.w x0, f19\n"        \
    "fmv.x.w x0, f21\n fmv.x.w x0, f23\n fmv.x.w x0, f25\n fmv.x.w x0, f27\n"
// With m0 = 0xf0: lanes 4-7 of the slot copy <- lanes 4-7 of f[2i] (the odd block's 16 bytes).
#define ODD_MERGE14                                                                                   \
    "for.pi f1, f0, f0\n for.pi f3, f2, f2\n for.pi f5, f4, f4\n for.pi f7, f6, f6\n"                  \
    "for.pi f9, f8, f8\n for.pi f11, f10, f10\n for.pi f13, f12, f12\n for.pi f15, f14, f14\n"          \
    "for.pi f17, f16, f16\n for.pi f19, f18, f18\n for.pi f21, f20, f20\n for.pi f23, f22, f22\n"      \
    "for.pi f25, f24, f24\n for.pi f27, f26, f26\n"
#define SWG(R) "fswg.ps " R ", (%[ln])\n addi %[ln], %[ln], 64\n"
#define ODD_STORE14                                                                                   \
    SWG("f1") SWG("f3") SWG("f5") SWG("f7") SWG("f9") SWG("f11") SWG("f13")                           \
    SWG("f15") SWG("f17") SWG("f19") SWG("f21") SWG("f23") SWG("f25") SWG("f27")

INLINE void epi_hidden(uint64_t spill, uint64_t slot, uint64_t bias_addr, uint64_t M, bool odd, uint64_t line)
{
    if (!odd) {
        __asm__ __volatile__(
            EPI_HEAD("0x0c")
            EVEN_STORE14
            EPI_R1415("0x0c")
            "fsw.ps f28, 448(%[sl])\n fsw.ps f30, 480(%[sl])\n"
            :
            : [sp] "r"(spill), [sl] "r"(slot), [b] "r"(bias_addr), [m] "r"(M)
            : "memory", FREGS);
    } else {
        uint64_t ln = line;
        __asm__ __volatile__(
            EPI_HEAD("0xc0")
            ODD_LOAD14
            TAKEN
            "mov.m.x m0, zero, 0xf0\n"
            ODD_MERGE14
            "mov.m.x m0, zero, 0xff\n"
            TAKEN
            ODD_STORE14
            EPI_R1415("0xc0")
            "flw.ps f7, 448(%[sl])\n flw.ps f9, 480(%[sl])\n fmv.x.w x0, f7\n fmv.x.w x0, f9\n"
            TAKEN
            "mov.m.x m0, zero, 0xf0\n for.pi f7, f28, f28\n for.pi f9, f30, f30\n mov.m.x m0, zero, 0xff\n"
            TAKEN
            "fswg.ps f7, (%[ln])\n addi %[ln], %[ln], 64\n fswg.ps f9, (%[ln])\n"
            : [ln] "+r"(ln)
            : [sp] "r"(spill), [sl] "r"(slot), [b] "r"(bias_addr), [m] "r"(M)
            : "memory", FREGS);
    }
}

struct Run {
    const struct MlpArgs* a;
    uint64_t shire, sidx, mi, P;
    uint32_t err;
    uint64_t ops, groups, pad_groups, barriers, wait, copy_cycles, work_cycles;
};

// The end of a chunk: this minion's copy share (and a debug TensorStore) complete, its stores fenced, then the shire
// barrier.
INLINE bool end_chunk(struct Run* r)
{
    t_wait(2);
    t_wait(3);
    t_wait(8);
    __asm__ __volatile__("fence" : : : "memory");
    const uint64_t t0 = cycles();
    const bool ok = shire_barrier(r->shire, r->P, r->a->poll_limit);
    r->wait += cycles() - t0;
    if (ok) {
        ++r->barriers;
    } else {
        r->err |= MLP_ERR_BARRIER;
    }
    return ok;
}

// The output layer's epilogue: C (16 images x 16 int32, columns 10-15 zero) to the stack, then the labels, the
// checksum and the group's label line. `line` is this group's label line (or the slot's discard line).
NOINLINE void epi_out(const struct MlpArgs* a, const struct MlpChunk* c, uint64_t G, uint64_t gin, uint64_t slot,
                      bool pad, bool debug)
{
    uint32_t cbuf[256] __attribute__((aligned(64)));
    // Reads f0..f31 only, so no FREGS clobber: the compiler then saves no callee-saved f register in this function's
    // prologue, which would read the tensor-written registers before the TOUCH_ALL (errata 1.29 type F).
    __asm__ __volatile__(TOUCH_ALL STORE_ALL : : "r"(cbuf) : "memory");
    if (debug) {  // the raw C tile, 16 rows of 64 B from f[2r], f[2r+1]
        const uint64_t dst = a->logits + (pad ? (a->groups + slot) : G) * MLP_TILE_BYTES;
        t_store(tstore_word(1, 4, 16, dst), 64);
    }
    const int32_t* B = (const int32_t*)a->bias + c->bias;
    int32_t b[MLP_OUT];
    for (uint64_t j = 0; j < MLP_OUT; ++j) {
        b[j] = B[j];
    }
    uint64_t lab_lo = 0, lab_hi = 0;
    uint32_t sum = 0;
    for (uint64_t i = 0; i < MLP_GROUP; ++i) {
        const int32_t* row = (const int32_t*)cbuf + 16 * i;
        int32_t best = row[0] + b[0];
        uint64_t arg = 0;
        sum += (uint32_t)best;
        for (uint64_t j = 1; j < MLP_OUT; ++j) {
            const int32_t v = row[j] + b[j];
            sum += (uint32_t)v;
            if (v > best) {
                best = v;
                arg = j;
            }
        }
        if (i < 8) {
            lab_lo |= arg << (8 * i);
        } else {
            lab_hi |= arg << (8 * (i - 8));
        }
    }
    const uint64_t lineno = pad ? (a->groups + slot) : G;
    volatile uint64_t* L = (volatile uint64_t*)(a->labels + lineno * 64);
    L[0] = lab_lo;
    L[1] = lab_hi;
    L[2] = (lineno & 0xFFFFFFFFull) | ((a->epoch & 0xFFFFFFFFull) << 32);
    L[3] = (uint64_t)sum | ((uint64_t)(MLP_LBL_DONE | (pad ? MLP_LBL_DISCARD : 0)) << 32);
    L[4] = slot | ((gin & 0xFFFFFFFFull) << 32);
    L[5] = 0;
    L[6] = 0;
    L[7] = 0;
}

NOINLINE void run(struct Run* r)
{
    const struct MlpArgs* a = r->a;
    const uint64_t P = r->P, mi = r->mi, shire = r->shire;
    const bool dram = (a->flags & MLP_F_STAGE_DRAM) != 0, debug = (a->flags & MLP_F_DEBUG_LOGITS) != 0;
    const struct MlpChunk* ch = (const struct MlpChunk*)a->chunks;
    const uint64_t slot = shire * 32 + mi;
    const uint64_t pbuf = MLP_ACT_LINE0 + 2 * MLP_ACT_LINES * mi, qbuf = pbuf + MLP_ACT_LINES;
    uint32_t spill[32] __attribute__((aligned(32)));     // rows 14-15 of a C tile (128 B)
    uint32_t slotbuf[128] __attribute__((aligned(32)));  // an even block's 16 rows x 16 B, one 32 B slot a row
    uint64_t id = 0;
    __asm__ __volatile__("mov.m.x m0, zero, 0xff\n" : : : "memory");
    const uint64_t t0 = cycles();

    // scp staging: the chunks this shire keeps, DRAM -> its resident region; shire barrier; chip barrier.
    if (!dram) {
        uint64_t tile = 0, issued = 0;
        for (uint64_t q = 0; q < MLP_NCHUNKS; ++q) {
            const struct MlpChunk* c = ch + q;
            if (c->owner != shire) {
                continue;
            }
            for (uint64_t t = 0; t < c->ntiles; ++t, ++tile) {
                if (tile % P != mi) {
                    continue;
                }
                if (issued >= 2) {
                    t_wait(2 + id);
                }
                t_load_l2scp(c->res_line + 16 * t, a->wtiles + ((uint64_t)c->wtile + t) * MLP_TILE_BYTES, id);
                id ^= 1;
                ++issued;
            }
        }
        t_wait(2);
        t_wait(3);
        if (!shire_barrier(shire, P, a->poll_limit)) {
            r->err |= MLP_ERR_BARRIER;
            return;
        }
        if (!chip_barrier(a, P)) {
            r->err |= MLP_ERR_CHIP;
            return;
        }
    }
    // Chunk 0 into S0 before the first round.
    copy_share(a, ch, dram, MLP_STAGE_LINE0, P, mi, &id);
    t_wait(2);
    t_wait(3);
    if (!shire_barrier(shire, P, a->poll_limit)) {
        r->err |= MLP_ERR_BARRIER;
        return;
    }
    const uint64_t t1 = cycles();
    r->copy_cycles = t1 - t0;

    uint64_t u = 0;  // chunks computed by this shire so far: chunk u uses S[u & 1]
    for (uint64_t rho = r->sidx; rho < a->rounds; rho += a->nshires) {
        const uint64_t G = rho * P + mi;
        const bool pad = G >= a->groups;
        const uint64_t gin = pad ? 0 : G % a->gpp;
        const bool more = rho + a->nshires < a->rounds;
        // The group's 13 input tiles, DRAM -> buffer P.
        for (uint64_t t = 0; t < MLP_IN_TILES; ++t) {
            if (t >= 2) {
                t_wait(2 + id);
            }
            t_load_l2scp(pbuf + 16 * t, a->input + gin * MLP_INPUT_GROUP_BYTES + t * MLP_TILE_BYTES, id);
            id ^= 1;
        }
        t_wait(2);
        t_wait(3);
        for (uint64_t q = 0; q < MLP_NCHUNKS; ++q, ++u) {
            const struct MlpChunk* c = ch + q;
            // The next chunk's copy (the first chunk of this shire's next round after the last).
            if (q + 1 < MLP_NCHUNKS || more) {
                const struct MlpChunk* cn = ch + (q + 1 < MLP_NCHUNKS ? q + 1 : 0);
                copy_share(a, cn, dram, MLP_STAGE_LINE0 + MLP_STAGE_LINES * ((u + 1) & 1), P, mi, &id);
            }
            // Layers 1, 3 and 5 read P; 2 and 4 read Q. Layer l writes the other buffer.
            const uint64_t inb = (c->layer & 1) ? qbuf : pbuf, outb = (c->layer & 1) ? pbuf : qbuf;
            tile_loop(SCP_LOCAL(inb * 64), SCP_LOCAL((MLP_STAGE_LINE0 + MLP_STAGE_LINES * (u & 1)) * 64),
                      c->ntiles);
            r->ops += c->ntiles;
            if (c->layer < 4) {
                // An odd block writes its pair's 32 bytes of each image line: tile block / 4, half (block / 2) mod 2.
                const uint64_t line = SCP_SHIRE(shire, outb * 64 + (uint64_t)(c->block >> 2) * MLP_TILE_BYTES +
                                                           32 * (uint64_t)((c->block >> 1) & 1));
                epi_hidden((uint64_t)spill, (uint64_t)slotbuf, a->bias + 4 * (uint64_t)c->bias, a->mult[c->layer],
                           (c->block & 1) != 0, line);
            } else {
                epi_out(a, c, G, gin, slot, pad, debug);
            }
            if (!end_chunk(r)) {
                goto out;
            }
        }
        ++r->groups;
        if (pad) {
            ++r->pad_groups;
        }
    }
out:
    t_wait(7);
    t_wait(8);
    t_wait(2);
    t_wait(3);
    r->work_cycles = cycles() - t1;
}

INLINE bool args_ok(const struct MlpArgs* a)
{
    return a->magic == MLP_MAGIC && a->per_shire >= 1 && a->per_shire <= 32 && a->nshires >= 1 &&
           a->nshires <= 32 && popcount64(a->shire_mask & 0xFFFFFFFFull) == a->nshires &&
           a->groups >= 1 && a->gpp >= 1 && a->rounds == (a->groups + a->per_shire - 1) / a->per_shire &&
           a->table_magic == MLP_TABLE_MAGIC;
}

INLINE bool table_ok(const struct MlpArgs* a)
{
    const struct MlpChunk* ch = (const struct MlpChunk*)a->chunks;
    uint32_t sum = 0;
    for (uint64_t q = 0; q < MLP_NCHUNKS; ++q) {
        const struct MlpChunk* c = ch + q;
        if (c->ntiles != (c->layer == 0 ? MLP_IN_TILES : MLP_HID_TILES) || c->layer >= MLP_NLAYERS ||
            (uint64_t)c->wtile + c->ntiles > MLP_NBTILES || (uint64_t)c->bias + 16 > MLP_BIAS_INTS) {
            return false;
        }
        if (!(a->flags & MLP_F_STAGE_DRAM) &&
            (c->res_line < MLP_RES_LINE0 || (uint64_t)c->res_line + 16 * c->ntiles > MLP_RES_LINE0 + MLP_RES_LINES_MAX ||
             c->owner >= 32 || !((a->shire_mask >> c->owner) & 1))) {
            return false;
        }
        sum += c->wtile + c->ntiles + c->layer + c->block + c->bias;
    }
    return sum == a->table_sum;
}

int64_t entry_point(const struct MlpArgs* args)
{
    const uint64_t hart = get_hart_id();
    const uint64_t shire = hart >> 6, mi = (hart >> 1) & 31, thread = hart & 1;
    if (thread == 1 || shire >= 32 || !((args->shire_mask >> shire) & 1) || mi >= args->per_shire) {
        return 0;  // hart 1 returns at once, as in every lab tensor kernel
    }
    const uint64_t t_entry = cycles();
    struct Run r;
    r.a = args;
    r.shire = shire;
    r.sidx = popcount64(args->shire_mask & ((1ull << shire) - 1));
    r.mi = mi;
    r.P = args->per_shire;
    r.err = 0;
    r.ops = r.groups = r.pad_groups = r.barriers = r.wait = r.copy_cycles = r.work_cycles = 0;
    if (!args_ok(args)) {
        r.err |= MLP_ERR_ARGS;
    } else if (!table_ok(args)) {
        r.err |= MLP_ERR_TABLE;
    } else {
        run(&r);
        __asm__ __volatile__(TOUCH_ALL : : : "memory");  // run's epilogue restores callee-saved f registers
    }
    const uint64_t te = tensor_error();
    if (te) {
        r.err |= MLP_ERR_TENSOR;
    }
    volatile struct MlpRecord* rec = (volatile struct MlpRecord*)args->records + (shire * 32 + mi);
    rec->magic = MLP_REC_MAGIC;
    rec->cycles = cycles() - t_entry;
    rec->work_cycles = r.work_cycles;
    rec->copy_cycles = r.copy_cycles;
    rec->wait_cycles = r.wait;
    rec->groups = (uint32_t)r.groups;
    rec->pad_groups = (uint32_t)r.pad_groups;
    rec->ops = r.ops;
    rec->barriers = (uint32_t)r.barriers;
    rec->tensor_error = (uint32_t)te;
    rec->status = (uint32_t)((args->epoch & 0xFFFF) << 16) | ((uint32_t)(te & 0xFF) << 8) | (r.err & 0xFF);
    return 0;
}
