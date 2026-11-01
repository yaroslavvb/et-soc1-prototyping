// E104: fp16's accumulators by the manual's sentence, ET Programmer's Reference Manual 9.3.3, TensorFMA16A32: the three values are added with no intermediate rounding and "the final sum is calculated using
// round towards zero". Not the RTL's arithmetic: accum.c and fp16_model.py truncate each aligned product separately (txfma_c2.v:309-310, txfma_f4.v:82-85), so a product that subtracts takes a unit off a large sum
// even if its partner adds. This one holds such a sum. The third reading E104 has to separate. Written from the sentence, not from accum.c or from the verifier's walk.c.
//
//   manual_e104 <tile.bin (2048 bytes)> <n0> [<n1> ...]    # ascending; writes manual_<n>.bin (1024 bytes, C[row][col] row-major, little-endian) in the current directory
//
// The order and the zero gate are the RTL's: for k, for row i, for column j, skip a word pair whose raw A or B word is zero; the first A column of op 0 is a multiply, not gated. Denormal operands read as zero, denormal
// results flush to a signed zero, as accum.c's. Every value is an integer in units of 2^-48: a product's last bit is 2^-48 at the smallest normal exponents, and a sum truncated to 24 bits stays a multiple of that.
// SPDX-License-Identifier: Apache-2.0
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef __int128 i128;
typedef unsigned __int128 u128;
static uint32_t A[16][16], B[16][16], C[16][16];

static inline i128 prod(uint32_t a, uint32_t b) {
    int ea = (a >> 10) & 31, eb = (b >> 10) & 31;
    if (!ea || !eb) return 0;
    u128 m = (u128)(0x400 | (a & 0x3FF)) * (0x400 | (b & 0x3FF));
    // value = m * 2^(ea - 25) * 2^(eb - 25); in units of 2^-48, m << (ea + eb - 2)
    i128 v = (i128)(m << (ea + eb - 2));
    return ((a ^ b) >> 15) & 1 ? -v : v;
}

static inline i128 fix(uint32_t c) {
    int e = (c >> 23) & 0xFF;
    if (!e) return 0;
    u128 m = 0x800000 | (c & 0x7FFFFF);
    int sh = e - 150 + 48;       // value = m * 2^(e - 150)
    i128 v;
    if (sh >= 0) {
        if (sh > 100) { fprintf(stderr, "C too large for the window\n"); exit(3); }
        v = (i128)(m << sh);
    } else {
        if (m & (((u128)1 << -sh) - 1)) { fprintf(stderr, "C has bits below 2^-48\n"); exit(3); }
        v = (i128)(m >> -sh);
    }
    return (c >> 31) ? -v : v;
}

static inline uint32_t rtz(i128 x, uint32_t neg_zero) {
    if (x == 0) return neg_zero;
    uint32_t s = x < 0 ? 0x80000000u : 0;
    u128 a = x < 0 ? (u128)(-x) : (u128)x;
    int n = 0;
    uint64_t hi = (uint64_t)(a >> 64), lo = (uint64_t)a;
    n = hi ? 128 - __builtin_clzll(hi) : 64 - __builtin_clzll(lo);
    int be = n - 1 - 48 + 127;
    if (be <= 0) return s;
    if (be >= 255) return s | 0x7F7FFFFF;
    uint64_t mant = n >= 24 ? (uint64_t)(a >> (n - 24)) : (uint64_t)(a << (24 - n));
    return s | ((uint32_t)be << 23) | (uint32_t)(mant & 0x7FFFFF);
}

static inline uint32_t step(uint32_t a, uint32_t b, uint32_t c, int mul) {
    uint32_t ah = a >> 16, al = a & 0xFFFF, bh = b >> 16, bl = b & 0xFFFF;
    i128 ph = prod(ah, bh), pl = prod(al, bl);
    i128 cv = mul ? 0 : fix(c);
    // a sum of zeros is negative only if every term is (a multiply's C is the neutral -0); an exact cancellation is +0, as in round toward zero
    int all_zero_neg = (mul || (((c >> 23) & 0xFF) == 0 && (c >> 31))) && ph == 0 && pl == 0 && (((ah ^ bh) >> 15) & 1) && (((al ^ bl) >> 15) & 1);
    return rtz(cv + ph + pl, all_zero_neg ? 0x80000000u : 0);
}

int main(int argc, char** argv) {
    if (argc < 3) { fprintf(stderr, "usage\n"); return 2; }
    FILE* f = fopen(argv[1], "rb");
    uint32_t w[512];
    if (!f || fread(w, 4, 512, f) != 512) { fprintf(stderr, "short tile\n"); return 1; }
    fclose(f);
    memcpy(A, w, 1024);
    memcpy(B, w + 256, 1024);
    memset(C, 0, sizeof C);
    long op = 0;
    for (int a = 2; a < argc; a++) {
        long target = atol(argv[a]);
        for (; op < target; op++) {
            for (int k = 0; k < 16; k++) for (int i = 0; i < 16; i++) {
                uint32_t aw = A[i][k];
                if (op == 0 && k == 0) {
                    for (int j = 0; j < 16; j++) C[i][j] = step(aw, B[k][j], 0, 1);
                } else if (aw) {
                    for (int j = 0; j < 16; j++) if (B[k][j]) C[i][j] = step(aw, B[k][j], C[i][j], 0);
                }
            }
        }
        char name[64];
        snprintf(name, sizeof name, "manual_%ld.bin", target);
        FILE* o = fopen(name, "wb");
        fwrite(C, 4, 256, o);
        fclose(o);
    }
    return 0;
}
