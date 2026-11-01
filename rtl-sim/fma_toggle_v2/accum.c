// The accumulators a launch has reached after n TensorFMA ops, in software, so the bench can start an op mid-launch.
//
//   accum <fp32|fp16|int8> <tile.bin (2048 bytes)> <n0> [<n1> ...]    # one n per output file, ascending
//   writes accum_<n>.bin (1024 bytes, C[row][col] row-major, little-endian) in the current directory
//
// fp32: FMADD with round-to-nearest-even, denormal operands read as zero, denormal results flushed (the rules
// fcheck_unit.py checks against the RTL, 20,000 of 20,000 exact). fp16: the fixed-point window of fp16_model.py.
// int8: exact, closed form. The order and the zero gate are the RTL's: for k, for row i, for column j, skip a word pair
// whose A or B word is zero (first pass: a multiply, not gated, in the first A column of op 0 only).
// SPDX-License-Identifier: Apache-2.0
#include <fenv.h>
#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static uint32_t A[16][16], B[16][16], C[16][16];
typedef union { float f; uint32_t u; } fu;

static inline float daz(uint32_t w) {
    fu x; x.u = w;
    if ((w & 0x7F800000u) == 0) x.u = w & 0x80000000u;
    return x.f;
}
static inline uint32_t ftz(float r) {
    fu x; x.f = r;
    if ((x.u & 0x7F800000u) == 0) x.u &= 0x80000000u;
    return x.u;
}

// ---------------------------------------------------------------- fp16: fp16_model.py, ported
typedef struct { int e; int zero; uint32_t m; int s; } term;
static inline int e32_of(int e, int zq) {
    int e4 = (e >> 4) & 1, ext = e4 ? 0 : 7;
    if (zq && e == 0) ext = 0;
    return (e4 << 7) | (ext << 4) | (e & 0xF);
}
static inline uint32_t fp16_step(uint32_t a, uint32_t b, uint32_t c, int mul) {
    uint32_t ah = a >> 16, al = a & 0xFFFF, bh = b >> 16, bl = b & 0xFFFF;
    int ea = (ah >> 10) & 31, eb = (bh >> 10) & 31, eal = (al >> 10) & 31, ebl = (bl >> 10) & 31;
    int ec = mul ? 0 : (c >> 23) & 0xFF;
    uint32_t fc = mul ? 0 : c & 0x7FFFFF;
    int sc = mul ? 1 : c >> 31;       // a multiply has no C: -0 is the neutral term for the sign of a sum of zeros
    int ph_z = ea == 0 || eb == 0, pl_z = eal == 0 || ebl == 0, c_z = ec == 0;
    int eph = e32_of(ea, 1) + e32_of(eb, 0) - 127, epl = e32_of(eal, 0) + e32_of(ebl, 0) - 127;
    uint64_t mph = (uint64_t)(ea ? 0x400 | (ah & 0x3FF) : 0) * (eb ? 0x400 | (bh & 0x3FF) : 0);
    uint64_t mpl = (uint64_t)(eal ? 0x400 | (al & 0x3FF) : 0) * (ebl ? 0x400 | (bl & 0x3FF) : 0);
    uint64_t mc = ec ? (0x800000 | fc) : 0;
    int sph = ((ah ^ bh) >> 15) & 1, spl = ((al ^ bl) >> 15) & 1;
    int cph = ((ec - eph) < 0 && !ph_z) || c_z, cpl = ((ec - epl) < 0 && !pl_z) || c_z, phpl = ((eph - epl) < 0 && !pl_z) || ph_z;
    // 0 C, 1 PH, 2 PL
    int E[3] = {ec, eph, epl}, S[3] = {sc, sph, spl}, Z[3] = {c_z, ph_z, pl_z};
    uint64_t M[3] = {mc << 2, mph << 5, mpl << 5};
    int op3, al1, al2;
    if (!cph && !cpl) { op3 = 0; al1 = 1; al2 = 2; }
    else if (cpl && phpl) { op3 = 2; al1 = 0; al2 = 1; }
    else { op3 = 1; al1 = 0; al2 = 2; }
    int eref = E[op3];
    int d1 = abs(eref - E[al1]), d2 = abs(eref - E[al2]);
    int64_t m1 = d1 > 26 ? 0 : (int64_t)(M[al1] >> d1), m2 = d2 > 26 ? 0 : (int64_t)(M[al2] >> d2);
    int lost1 = d1 > 26 ? M[al1] != 0 : (M[al1] & ((1ull << d1) - 1)) != 0;
    int lost2 = d2 > 26 ? M[al2] != 0 : (M[al2] & ((1ull << d2) - 1)) != 0;
    if (Z[al1] && d1 <= 26) lost1 = 0;
    if (Z[al2] && d2 <= 26) lost2 = 0;
    int neg1 = S[al1] != S[op3], neg2 = S[al2] != S[op3];
    int64_t x = (int64_t)M[op3];
    x += neg1 ? -m1 - lost1 : m1;
    x += neg2 ? -m2 - lost2 : m2;
    int sign = S[op3];
    if (x < 0) { sign ^= 1; x = -x; if (lost1 || lost2) x -= 1; }
    if (x <= 0) return (c_z && ph_z && pl_z && sc && sph && spl) ? 0x80000000u : 0;
    int n = 64 - __builtin_clzll((uint64_t)x);
    int be = eref + (n - 1 - 25);
    uint64_t mant = n >= 24 ? ((uint64_t)x >> (n - 24)) : ((uint64_t)x << (24 - n));
    if (be <= 0) return (uint32_t)sign << 31;
    if (be >= 255) return ((uint32_t)sign << 31) | 0x7F7FFFFF;
    return ((uint32_t)sign << 31) | ((uint32_t)be << 23) | (uint32_t)(mant & 0x7FFFFF);
}

static void write_c(long n) {
    char name[64];
    snprintf(name, sizeof name, "accum_%ld.bin", n);
    FILE* f = fopen(name, "wb");
    fwrite(C, 4, 256, f);
    fclose(f);
}

int main(int argc, char** argv) {
    if (argc < 4) { fprintf(stderr, "usage\n"); return 2; }
    const char* fmt = argv[1];
    FILE* f = fopen(argv[2], "rb");
    if (!f) { perror(argv[2]); return 1; }
    uint32_t w[512];
    if (fread(w, 4, 512, f) != 512) { fprintf(stderr, "short tile\n"); return 1; }
    fclose(f);
    memcpy(A, w, 1024);
    memcpy(B, w + 256, 1024);
    memset(C, 0, sizeof C);
    long op = 0;
    for (int a = 3; a < argc; a++) {
        long target = atol(argv[a]);
        if (!strcmp(fmt, "int8")) {
            // closed form: C = n * (sum over k, bytes of signed products), mod 2^32. The gate only skips zeros.
            static int64_t sum[16][16];
            static int done = 0;
            if (!done) {
                for (int i = 0; i < 16; i++) for (int j = 0; j < 16; j++) {
                    int64_t s = 0;
                    for (int k = 0; k < 16; k++) for (int e = 0; e < 4; e++) {
                        int x = (int8_t)(A[i][k] >> (8 * e)), y = (int8_t)(B[k][j] >> (8 * e));
                        s += x * y;
                    }
                    sum[i][j] = s;
                }
                done = 1;
            }
            for (int i = 0; i < 16; i++) for (int j = 0; j < 16; j++) C[i][j] = (uint32_t)(sum[i][j] * target);
            op = target;
        } else if (!strcmp(fmt, "fp32")) {
            static float fa[16][16], fb[16][16];
            static float cf[16][16];
            for (int i = 0; i < 16; i++) for (int j = 0; j < 16; j++) { fa[i][j] = daz(A[i][j]); fb[i][j] = daz(B[i][j]); }
            for (int i = 0; i < 16; i++) for (int j = 0; j < 16; j++) { fu x; x.u = C[i][j]; cf[i][j] = x.f; }
            for (; op < target; op++) {
                for (int k = 0; k < 16; k++) {
                    for (int i = 0; i < 16; i++) {
                        uint32_t aw = A[i][k]; float av = fa[i][k];
                        if (op == 0 && k == 0) {
                            for (int j = 0; j < 16; j++) { fu x; x.u = ftz(av * fb[k][j]); cf[i][j] = x.f; }
                        } else if (aw) {
                            for (int j = 0; j < 16; j++) {
                                if (B[k][j]) { fu x; x.u = ftz(fmaf(av, fb[k][j], cf[i][j])); cf[i][j] = x.f; }
                            }
                        }
                    }
                }
            }
            for (int i = 0; i < 16; i++) for (int j = 0; j < 16; j++) { fu x; x.f = cf[i][j]; C[i][j] = x.u; }
        } else {
            for (; op < target; op++) {
                for (int k = 0; k < 16; k++) for (int i = 0; i < 16; i++) {
                    uint32_t aw = A[i][k];
                    if (op == 0 && k == 0) {
                        for (int j = 0; j < 16; j++) C[i][j] = fp16_step(aw, B[k][j], 0, 1);
                    } else if (aw) {
                        for (int j = 0; j < 16; j++) if (B[k][j]) C[i][j] = fp16_step(aw, B[k][j], C[i][j], 0);
                    }
                }
            }
        }
        write_c(target);
    }
    return 0;
}
