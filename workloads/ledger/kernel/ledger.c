/*-------------------------------------------------------------------------
 * The ledger's plain programs (the November checkpoint's plan, step 3; Q166): a copy through DRAM, SHA-256 of one
 * message per hart, and a merge sort, each on every participating hart with its own data.
 *
 * User mode, no libc, no threads, no floating-point arithmetic (so none of the thirteen instructions that trap in
 * U-mode). Every hart touches whole cache lines of its own only. Only hart 0 of a minion reads hpmcounter3
 * (erratum 1.23, as workloads/sparseparity does), with the late-carry fix of workloads/memprobe.
 *
 * Layout and the host's checks: ../ledger_args.h and ../host/main.cpp.
 *
 * SPDX-License-Identifier: Apache-2.0
 *-------------------------------------------------------------------------*/

#include <stdint.h>
#include "etsoc/isa/hart.h"
#include "ledger_args.h"

int64_t entry_point(const struct LgArgs* a);

#define INLINE static inline __attribute__((always_inline))
#define NOINLINE static __attribute__((noinline))

// hpmcounter3 reads 128 short when its low 7 bits are 0-10 (the late carry; workloads/memprobe): put it back.
INLINE uint64_t cycles(void)
{
    uint64_t v;
    __asm__ __volatile__("csrr %0, hpmcounter3" : "=r"(v));
    return v + ((uint64_t)((v & 0x7F) < 11) << 7);
}

/* ---------------------------------------------------------------- copy */

// 256 B per iteration: eight 32 B vector loads, then eight 32 B vector stores (all eight lanes, m0 = 0xff).
NOINLINE void copy_v32(uint64_t s, uint64_t d, uint64_t n)
{
    __asm__ __volatile__("mov.m.x m0, zero, 0xff" : : : "memory");
    const uint64_t end = s + n;
    for (; s < end; s += 256, d += 256) {
        __asm__ __volatile__(
            "flw.ps f0, 0(%0)\n flw.ps f1, 32(%0)\n flw.ps f2, 64(%0)\n flw.ps f3, 96(%0)\n"
            "flw.ps f4, 128(%0)\n flw.ps f5, 160(%0)\n flw.ps f6, 192(%0)\n flw.ps f7, 224(%0)\n"
            "fsw.ps f0, 0(%1)\n fsw.ps f1, 32(%1)\n fsw.ps f2, 64(%1)\n fsw.ps f3, 96(%1)\n"
            "fsw.ps f4, 128(%1)\n fsw.ps f5, 160(%1)\n fsw.ps f6, 192(%1)\n fsw.ps f7, 224(%1)\n"
            : : "r"(s), "r"(d) : "memory", "f0", "f1", "f2", "f3", "f4", "f5", "f6", "f7");
    }
}

// 64 B per iteration: eight 8 B loads, then eight 8 B stores.
NOINLINE void copy_x8(uint64_t s, uint64_t d, uint64_t n)
{
    const uint64_t end = s + n;
    for (; s < end; s += 64, d += 64) {
        uint64_t t0, t1, t2, t3, t4, t5, t6, t7;
        __asm__ __volatile__(
            "ld %0, 0(%8)\n ld %1, 8(%8)\n ld %2, 16(%8)\n ld %3, 24(%8)\n"
            "ld %4, 32(%8)\n ld %5, 40(%8)\n ld %6, 48(%8)\n ld %7, 56(%8)\n"
            "sd %0, 0(%9)\n sd %1, 8(%9)\n sd %2, 16(%9)\n sd %3, 24(%9)\n"
            "sd %4, 32(%9)\n sd %5, 40(%9)\n sd %6, 48(%9)\n sd %7, 56(%9)\n"
            : "=&r"(t0), "=&r"(t1), "=&r"(t2), "=&r"(t3), "=&r"(t4), "=&r"(t5), "=&r"(t6), "=&r"(t7)
            : "r"(s), "r"(d)
            : "memory");
    }
}

/* ---------------------------------------------------------------- SHA-256 (FIPS 180-4) */

static const uint32_t K256[64] = {
    0x428a2f98u, 0x71374491u, 0xb5c0fbcfu, 0xe9b5dba5u, 0x3956c25bu, 0x59f111f1u, 0x923f82a4u, 0xab1c5ed5u,
    0xd807aa98u, 0x12835b01u, 0x243185beu, 0x550c7dc3u, 0x72be5d74u, 0x80deb1feu, 0x9bdc06a7u, 0xc19bf174u,
    0xe49b69c1u, 0xefbe4786u, 0x0fc19dc6u, 0x240ca1ccu, 0x2de92c6fu, 0x4a7484aau, 0x5cb0a9dcu, 0x76f988dau,
    0x983e5152u, 0xa831c66du, 0xb00327c8u, 0xbf597fc7u, 0xc6e00bf3u, 0xd5a79147u, 0x06ca6351u, 0x14292967u,
    0x27b70a85u, 0x2e1b2138u, 0x4d2c6dfcu, 0x53380d13u, 0x650a7354u, 0x766a0abbu, 0x81c2c92eu, 0x92722c85u,
    0xa2bfe8a1u, 0xa81a664bu, 0xc24b8b70u, 0xc76c51a3u, 0xd192e819u, 0xd6990624u, 0xf40e3585u, 0x106aa070u,
    0x19a4c116u, 0x1e376c08u, 0x2748774cu, 0x34b0bcb5u, 0x391c0cb3u, 0x4ed8aa4au, 0x5b9cca4fu, 0x682e6ff3u,
    0x748f82eeu, 0x78a5636fu, 0x84c87814u, 0x8cc70208u, 0x90befffau, 0xa4506cebu, 0xbef9a3f7u, 0xc67178f2u};

#define ROR(x, n) (((x) >> (n)) | ((x) << (32 - (n))))
#define BS0(x) (ROR(x, 2) ^ ROR(x, 13) ^ ROR(x, 22))
#define BS1(x) (ROR(x, 6) ^ ROR(x, 11) ^ ROR(x, 25))
#define SS0(x) (ROR(x, 7) ^ ROR(x, 18) ^ ((x) >> 3))
#define SS1(x) (ROR(x, 17) ^ ROR(x, 19) ^ ((x) >> 10))
#define CH(x, y, z) (((x) & (y)) ^ (~(x) & (z)))
#define MAJ(x, y, z) (((x) & (y)) ^ ((x) & (z)) ^ ((y) & (z)))

// The message's bytes are big-endian words; the core is little-endian and has no byte-reverse instruction.
INLINE uint32_t bswap32(uint32_t x)
{
    return (x >> 24) | ((x >> 8) & 0xff00u) | ((x << 8) & 0xff0000u) | (x << 24);
}

// One compression of the 64 bytes at p (as stored: 16 little-endian words read as the message's big-endian ones).
NOINLINE void sha256_compress(uint32_t* st, const uint32_t* p)
{
    uint32_t w[64];
    for (int t = 0; t < 16; ++t) {
        w[t] = bswap32(p[t]);
    }
    for (int t = 16; t < 64; ++t) {
        w[t] = SS1(w[t - 2]) + w[t - 7] + SS0(w[t - 15]) + w[t - 16];
    }
    uint32_t a = st[0], b = st[1], c = st[2], d = st[3], e = st[4], f = st[5], g = st[6], h = st[7];
    for (int t = 0; t < 64; ++t) {
        const uint32_t t1 = h + BS1(e) + CH(e, f, g) + K256[t] + w[t];
        const uint32_t t2 = BS0(a) + MAJ(a, b, c);
        h = g;
        g = f;
        f = e;
        e = d + t1;
        d = c;
        c = b;
        b = a;
        a = t1 + t2;
    }
    st[0] += a;
    st[1] += b;
    st[2] += c;
    st[3] += d;
    st[4] += e;
    st[5] += f;
    st[6] += g;
    st[7] += h;
}

// SHA-256 of `reps` copies of the `bytes`-byte block at blk; returns the compressions done.
NOINLINE uint64_t sha256_repeated(uint32_t* st, const uint32_t* blk, uint64_t bytes, uint64_t reps)
{
    st[0] = 0x6a09e667u;
    st[1] = 0xbb67ae85u;
    st[2] = 0x3c6ef372u;
    st[3] = 0xa54ff53au;
    st[4] = 0x510e527fu;
    st[5] = 0x9b05688cu;
    st[6] = 0x1f83d9abu;
    st[7] = 0x5be0cd19u;
    const uint64_t nb = bytes >> 6;
    for (uint64_t r = 0; r < reps; ++r) {
        for (uint64_t b = 0; b < nb; ++b) {
            sha256_compress(st, blk + 16 * b);
        }
    }
    // The padding block: 0x80, zeros, the message's length in bits (big-endian), stored as the message is.
    const uint64_t bits = reps * bytes * 8;
    uint32_t pad[16];
    pad[0] = 0x80u;
    for (int t = 1; t < 14; ++t) {
        pad[t] = 0;
    }
    pad[14] = bswap32((uint32_t)(bits >> 32));
    pad[15] = bswap32((uint32_t)bits);
    sha256_compress(st, pad);
    return reps * nb + 1;
}

/* ---------------------------------------------------------------- merge sort */

// One merge of s[lo, mid) and s[mid, hi) into d[lo, hi). The comparison's branch follows the data.
INLINE void merge(const uint32_t* s, uint32_t* d, uint64_t lo, uint64_t mid, uint64_t hi)
{
    uint64_t i = lo, j = mid, k = lo;
    while (i < mid && j < hi) {
        const uint32_t x = s[i], y = s[j];
        if (x <= y) {
            d[k++] = x;
            ++i;
        } else {
            d[k++] = y;
            ++j;
        }
    }
    while (i < mid) {
        d[k++] = s[i++];
    }
    while (j < hi) {
        d[k++] = s[j++];
    }
}

// Bottom-up merge sort of w0[0, n) using w1 as the second buffer; returns the buffer that holds the result.
NOINLINE uint32_t* merge_sort(uint32_t* w0, uint32_t* w1, uint64_t n)
{
    uint32_t* s = w0;
    uint32_t* d = w1;
    for (uint64_t width = 1; width < n; width <<= 1) {
        for (uint64_t lo = 0; lo < n; lo += 2 * width) {
            const uint64_t mid = lo + width < n ? lo + width : n;
            const uint64_t hi = lo + 2 * width < n ? lo + 2 * width : n;
            merge(s, d, lo, mid, hi);
        }
        uint32_t* t = s;
        s = d;
        d = t;
    }
    return s;
}

NOINLINE void copy_keys(uint32_t* d, const uint32_t* s, uint64_t n)
{
    for (uint64_t i = 0; i < n; ++i) {
        d[i] = s[i];
    }
}

/* ---------------------------------------------------------------- entry */

int64_t entry_point(const struct LgArgs* a)
{
    const uint64_t hart = get_hart_id();
    const uint64_t shire = hart >> 6;
    if (shire >= 32 || !((a->shire_mask >> shire) & 1)) {
        return 0;
    }
    const uint64_t thread = hart & 1;
    const uint64_t minion = (hart >> 1) & 31;
    if (thread && a->harts < 2) {
        return 0;
    }
    const uint64_t mmask = a->minion_mask ? (a->minion_mask & 0xFFFFFFFFull) : 0xFFFFFFFFull;
    if (!((mmask >> minion) & 1)) {
        return 0;
    }
    // This hart's participant number: shires below it in the mask, minions below it in the mask, then the thread.
    const uint64_t per_shire = (uint64_t)__builtin_popcountll(mmask);
    const uint64_t shires_below = (uint64_t)__builtin_popcountll(a->shire_mask & ((1ull << shire) - 1));
    const uint64_t minions_below = (uint64_t)__builtin_popcountll(mmask & ((1ull << minion) - 1));
    const uint64_t p = (shires_below * per_shire + minions_below) * a->harts + (a->harts >= 2 ? thread : 0);

    uint32_t word[8] = {0, 0, 0, 0, 0, 0, 0, 0};
    uint64_t units = 0;
    const uint64_t t0 = thread ? 0 : cycles();

    switch (a->prog) {
    case LG_COPY: {
        const uint64_t s = a->src + p * a->bytes, d = a->dst + p * a->bytes;
        for (uint64_t r = 0; r < a->reps; ++r) {
            if (a->width == 8) {
                copy_x8(s, d, a->bytes);
            } else {
                copy_v32(s, d, a->bytes);
            }
        }
        units = a->reps * a->bytes;
        break;
    }
    case LG_SHA256: {
        const uint32_t* blk = (const uint32_t*)(a->src + p * a->bytes);
        uint32_t st[8];
        units = sha256_repeated(st, blk, a->bytes, a->reps);
        for (int i = 0; i < 8; ++i) {
            word[i] = st[i];
        }
        break;
    }
    case LG_SORT: {
        const uint64_t n = a->bytes;
        const uint32_t* in = (const uint32_t*)(a->src + p * n * 4);
        uint32_t* w0 = (uint32_t*)(a->dst + p * n * 8);
        uint32_t* w1 = w0 + n;
        uint32_t* res = w0;
        for (uint64_t r = 0; r < a->reps; ++r) {
            copy_keys(w0, in, n);
            res = merge_sort(w0, w1, n);
        }
        units = a->reps;
        uint32_t bad = 0, x = 0, sum = 0;
        for (uint64_t i = 0; i < n; ++i) {
            if (i && res[i - 1] > res[i]) {
                ++bad;
            }
            x ^= res[i];
            sum += res[i];
        }
        word[0] = bad;
        word[1] = x;
        word[2] = sum;
        word[3] = res == w1;
        break;
    }
    default:
        return 0;
    }

    const uint64_t cyc = thread ? 0 : cycles() - t0;
    volatile struct LgResult* r = (volatile struct LgResult*)a->results + hart;
    r->cycles = cyc;
    r->units = units;
    r->hart = (uint32_t)hart;
    for (int i = 0; i < 8; ++i) {
        r->word[i] = word[i];
    }
    r->participant = p;
    r->magic = LG_MAGIC;
    return 0;
}
