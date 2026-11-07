// m10-acc (Q153): the two features of M10's accumulator-toggle term, per tile, exact (tools/claims-v3/m10-acc/REGISTRATION.md
// section 2).
//
//   acctrace_m10acc <fp32|fp16|int8> <tile.bin (2048 bytes: A then B)> <N1>[,<N2>,...]     # launch sizes, ascending, each >= 2
//
// x_acc: the accumulator's register toggles per op, as the mean over ops 1..N-1 of one launch of N ops (op 0's first step is a
//   multiply that overwrites the previous launch's state; it is left out, as flipmodel_e178.c leaves it out). Every element
//   C[i][j] follows its own sequence c <- step(A[i][k], B[k][j], c), k = 0..15 an op, stepped with the lab's committed
//   accumulator arithmetic, rtl-sim/fma_toggle_v2/accum.c included unchanged (fmaf with DAZ/FTZ for fp32, its fp16_step window
//   for fp16, the exact int32 sum for int8), with its zero gate (a word pair whose A or B word is 0 is skipped). What is counted
//   is the Hamming distance of the 32-bit accumulator word at every step, summed over the 256 elements: the register-file entry
//   a micro-op writes (floats, vpu_64x32_3r2w_vpurf) or the TenC entry (int8). One run to the largest N gives every N's launch
//   mean exactly (cumulative sums). Elements whose 32 operand words are identical are stepped once and counted with their
//   multiplicity (exact). Floats also give the toggles by field (sign, exponent, mantissa).
// x_bth (floats only; 0 for int8): A's non-zero Booth rows beyond those of A = 1.0, times B's toggled significand bits, summed
//   over the lanes and the micro-op transitions of one op in the PRM's issue order (for B row k, for A row i, two micro-ops of
//   8 lanes: lane l takes the broadcast A word A[i][k] and B[k][8h + l], h = 0, 1), the op's last micro-op followed by the next
//   op's first. The recoder is the open RTL's (core-et b38a1a3, txfma_7s/txfma_booth_ppg_32r4.v, radix 4, 17 digits from
//   ext = {2'b0, mplr, 1'b0}; a digit is non-zero unless its three bits are 000 or 111), and its multiplier operand is A
//   (txfma_f1.v: mplr = fa, mpcnd = fb; txfma_f0.v: fa from opa; vpu_bypass.v: source 0 is TenA's data, source 1 TenB's).
//   mplr as txfma_f0.v forms it: fp32 {hidden, mantissa[22:0], 8'b0}; fp16 {hidden_hi, mant_hi[9:0], 9'b0, hidden_lo,
//   mant_lo[9:0], 1'b0} (a zero or denormal half contributes no row). A = 1.0 has 2 non-zero rows per product, the fewest any
//   normal word has, so the excess is >= 0 and 0 at A = 1.0. B's significand: the hidden bit and the mantissa (a zero or
//   denormal half reads 0); fp16 pairs each half of A with the same half of B. A lane at a gated slot keeps its operands (no
//   toggle, no contribution).
// Output: one JSON line. SPDX-License-Identifier: Apache-2.0
#define main accum_main
#include ACCUM_C
#undef main

static int pc32(uint32_t x) { return __builtin_popcount(x); }

static int nzr_mplr(uint32_t mplr) {
    uint64_t ext = ((uint64_t)mplr) << 1;
    int n = 0;
    for (int i = 0; i < 17; i++) {
        unsigned t = (unsigned)((ext >> (2 * i)) & 7u);
        if (t != 0 && t != 7) n++;
    }
    return n;
}
// excess non-zero Booth rows of an A word (beyond A = 1.0's 2 per product)
static int excess_rows(int ty, uint32_t a) {
    if (ty == 0) {
        if ((a & 0x7F800000u) == 0) return 0;
        uint32_t mplr = 0x80000000u | ((a & 0x7FFFFFu) << 8);
        return nzr_mplr(mplr) - 2;
    }
    int ex = 0;
    uint32_t hi = a >> 16, lo = a & 0xFFFFu;
    if (hi & 0x7C00u) ex += nzr_mplr(0x80000000u | ((hi & 0x3FFu) << 21)) - 2;
    if (lo & 0x7C00u) ex += nzr_mplr((1u << 11) | ((lo & 0x3FFu) << 1)) - 2;
    return ex;
}
static int excess_rows_half(uint32_t a, int half) {
    uint32_t h = half ? (a >> 16) : (a & 0xFFFFu);
    if (!(h & 0x7C00u)) return 0;
    return half ? nzr_mplr(0x80000000u | ((h & 0x3FFu) << 21)) - 2 : nzr_mplr((1u << 11) | ((h & 0x3FFu) << 1)) - 2;
}
static uint32_t sig32(uint32_t b) { return (b & 0x7F800000u) ? (0x800000u | (b & 0x7FFFFFu)) : 0u; }
static uint32_t sig16(uint32_t b, int half) {
    uint32_t h = half ? (b >> 16) : (b & 0xFFFFu);
    return (h & 0x7C00u) ? (0x400u | (h & 0x3FFu)) : 0u;
}

// x_bth per op: two ops of the issue stream, the second counted (so the wrap from one op to the next is in it)
static double bth_per_op(int ty) {
    if (ty == 2) return 0.0;
    uint32_t prevB[8];
    int have[8];
    memset(have, 0, sizeof have);
    memset(prevB, 0, sizeof prevB);
    double x = 0.0;
    for (int op = 0; op < 2; op++)
        for (int k = 0; k < 16; k++)
            for (int i = 0; i < 16; i++)
                for (int h = 0; h < 2; h++) {
                    uint32_t aw = A[i][k];
                    for (int l = 0; l < 8; l++) {
                        uint32_t bw = B[k][8 * h + l];
                        if (!aw || !bw) continue;          // a gated slot: the lane keeps its operands
                        if (have[l] && op == 1) {
                            if (ty == 0) x += (double)excess_rows(0, aw) * pc32(sig32(prevB[l]) ^ sig32(bw));
                            else
                                x += (double)excess_rows_half(aw, 1) * pc32(sig16(prevB[l], 1) ^ sig16(bw, 1)) +
                                     (double)excess_rows_half(aw, 0) * pc32(sig16(prevB[l], 0) ^ sig16(bw, 0));
                        }
                        prevB[l] = bw;
                        have[l] = 1;
                    }
                }
    return x;
}

#define MAXN 16
typedef struct { uint32_t a[16], b[16]; int mult; } elem;

int main(int argc, char** argv) {
    if (argc < 4) { fprintf(stderr, "usage: acctrace_m10acc type tile.bin N1[,N2,...]\n"); return 2; }
    int ty = !strcmp(argv[1], "fp32") ? 0 : !strcmp(argv[1], "fp16") ? 1 : !strcmp(argv[1], "int8") ? 2 : -1;
    if (ty < 0) { fprintf(stderr, "type\n"); return 2; }
    FILE* f = fopen(argv[2], "rb");
    if (!f) { perror(argv[2]); return 1; }
    uint32_t w[512];
    if (fread(w, 4, 512, f) != 512) { fprintf(stderr, "short tile\n"); return 1; }
    fclose(f);
    memcpy(A, w, 1024);
    memcpy(B, w + 256, 1024);
    long Ns[MAXN]; int nn = 0;
    for (char* s = strtok(argv[3], ","); s && nn < MAXN; s = strtok(NULL, ",")) Ns[nn++] = atol(s);
    for (int q = 0; q < nn; q++) if (Ns[q] < 2 || (q && Ns[q] <= Ns[q - 1])) { fprintf(stderr, "N list\n"); return 2; }
    long Nmax = Ns[nn - 1];
    // unique element sequences
    static elem E[256];
    int ne = 0;
    for (int i = 0; i < 16; i++)
        for (int j = 0; j < 16; j++) {
            elem e;
            for (int k = 0; k < 16; k++) { e.a[k] = A[i][k]; e.b[k] = B[k][j]; }
            int found = -1;
            for (int q = 0; q < ne; q++)
                if (!memcmp(E[q].a, e.a, sizeof e.a) && !memcmp(E[q].b, e.b, sizeof e.b)) { found = q; break; }
            if (found >= 0) E[found].mult++;
            else { e.mult = 1; E[ne++] = e; }
        }
    // cumulative toggles at each N (ops 1..N-1), by field
    double cum_t[MAXN], cum_s[MAXN], cum_e[MAXN], cum_m[MAXN];
    for (int q = 0; q < MAXN; q++) cum_t[q] = cum_s[q] = cum_e[q] = cum_m[q] = 0.0;
    for (int q = 0; q < ne; q++) {
        const elem* e = &E[q];
        uint64_t ts = 0, tsg = 0, tex = 0, tma = 0;
        int nxt = 0;
        int act[16];
        for (int k = 0; k < 16; k++) act[k] = e->a[k] != 0 && e->b[k] != 0;
        if (ty == 0) {
            float fa[16], fb[16];
            for (int k = 0; k < 16; k++) { fa[k] = daz(e->a[k]); fb[k] = daz(e->b[k]); }
            uint32_t c = ftz(fa[0] * fb[0]);
            for (int k = 1; k < 16; k++) if (act[k]) { fu cx; cx.u = c; c = ftz(fmaf(fa[k], fb[k], cx.f)); }
            for (long op = 1; op < Nmax; op++) {
                for (int k = 0; k < 16; k++) {
                    if (!act[k]) continue;
                    fu cx; cx.u = c;
                    uint32_t cn = ftz(fmaf(fa[k], fb[k], cx.f));
                    uint32_t d = c ^ cn;
                    if (d) { tsg += d >> 31; tex += pc32(d & 0x7F800000u); tma += pc32(d & 0x007FFFFFu); }
                    c = cn;
                }
                while (nxt < nn && op == Ns[nxt] - 1) {
                    cum_s[nxt] += (double)tsg * e->mult; cum_e[nxt] += (double)tex * e->mult; cum_m[nxt] += (double)tma * e->mult;
                    cum_t[nxt] += (double)(tsg + tex + tma) * e->mult;
                    nxt++;
                }
            }
        } else if (ty == 1) {
            uint32_t c = fp16_step(e->a[0], e->b[0], 0, 1);
            for (int k = 1; k < 16; k++) if (act[k]) c = fp16_step(e->a[k], e->b[k], c, 0);
            for (long op = 1; op < Nmax; op++) {
                for (int k = 0; k < 16; k++) {
                    if (!act[k]) continue;
                    uint32_t cn = fp16_step(e->a[k], e->b[k], c, 0);
                    uint32_t d = c ^ cn;
                    if (d) { tsg += d >> 31; tex += pc32(d & 0x7F800000u); tma += pc32(d & 0x007FFFFFu); }
                    c = cn;
                }
                while (nxt < nn && op == Ns[nxt] - 1) {
                    cum_s[nxt] += (double)tsg * e->mult; cum_e[nxt] += (double)tex * e->mult; cum_m[nxt] += (double)tma * e->mult;
                    cum_t[nxt] += (double)(tsg + tex + tma) * e->mult;
                    nxt++;
                }
            }
        } else {
            // accum.c's int8 closed form: C = n x (the sum over k of the word pairs' four byte products), mod 2^32; a gated
            // pair (a zero word) has products 0, and op 0's first-step multiply equals 0 + its products
            int64_t dk[16];
            for (int k = 0; k < 16; k++) {
                int64_t s = 0;
                for (int b8 = 0; b8 < 4; b8++) s += (int64_t)(int8_t)(e->a[k] >> (8 * b8)) * (int8_t)(e->b[k] >> (8 * b8));
                dk[k] = s;
            }
            uint32_t c = 0;
            for (int k = 0; k < 16; k++) c = (uint32_t)((int64_t)(int32_t)c + dk[k]);
            for (long op = 1; op < Nmax; op++) {
                for (int k = 0; k < 16; k++) {
                    uint32_t cn = (uint32_t)((int64_t)(int32_t)c + dk[k]);
                    ts += pc32(c ^ cn);
                    c = cn;
                }
                while (nxt < nn && op == Ns[nxt] - 1) { cum_t[nxt] += (double)ts * e->mult; nxt++; }
            }
        }
    }
    double xb = bth_per_op(ty);
    printf("{\"type\":\"%s\",\"unique_elements\":%d,\"uops_per_op\":%d,\"x_bth_per_op\":%.4f,\"x_acc\":{", argv[1], ne,
           ty == 2 ? 256 : 512, xb);
    for (int q = 0; q < nn; q++) {
        double n1 = (double)(Ns[q] - 1);
        if (ty == 2)
            printf("\"%ld\":{\"total\":%.6f}%s", Ns[q], cum_t[q] / n1, q + 1 < nn ? "," : "");
        else
            printf("\"%ld\":{\"total\":%.6f,\"sign\":%.6f,\"exp\":%.6f,\"mant\":%.6f}%s", Ns[q], cum_t[q] / n1, cum_s[q] / n1,
                   cum_e[q] / n1, cum_m[q] / n1, q + 1 < nn ? "," : "");
    }
    printf("}}\n");
    return 0;
}
