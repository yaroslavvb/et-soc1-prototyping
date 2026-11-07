// m10-acc (Q153), dated amendment A1: x_lane, the accumulator words a lane's datapath takes in from one micro-op to the next
// (tools/claims-v3/m10-acc/REGISTRATION.md.dated-note-A1.md, A1-2), with x_acc and x_bth as acctrace_m10acc.c gives them.
//
//   acctrace_m10acc_a1 <fp32|fp16|int8> <tile.bin (2048 bytes: A then B)> <N1>[,<N2>,...]     # launch sizes, ascending, each >= 2
//
// All 256 elements are stepped together, op by op, with rtl-sim/fma_toggle_v2/accum.c's arithmetic and zero gate (included
// unchanged); op 0's first step is a multiply. Within each step k of an op, in the PRM's issue order (floats: for A row i, for
// h = 0, 1, lane l takes element (i, 8h + l); int8: for A row i, slot s takes element (i, s)), a lane's C operand is the element's
// word before its update at that step. x_lane = the mean over ops 1..N-1 of the sum over the lanes and the op's micro-ops of the
// Hamming distance between the C operand a lane takes and the one it took at its previous active slot (a gated slot, an A or B word
// of 0, keeps the lane's previous word and adds nothing). x_acc (each element's own word, before and after each step, summed) is
// recomputed in the same pass and must equal acctrace_m10acc.c's. Elements whose 32 operand words are identical share one state
// (exact: their sequences are identical). One run to the largest N gives every N's launch mean (cumulative sums).
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
static int excess_rows32(uint32_t a) {
    if ((a & 0x7F800000u) == 0) return 0;
    return nzr_mplr(0x80000000u | ((a & 0x7FFFFFu) << 8)) - 2;
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
                        if (!aw || !bw) continue;
                        if (have[l] && op == 1) {
                            if (ty == 0) x += (double)excess_rows32(aw) * pc32(sig32(prevB[l]) ^ sig32(bw));
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

int main(int argc, char** argv) {
    if (argc < 4) { fprintf(stderr, "usage: acctrace_m10acc_a1 type tile.bin N1[,N2,...]\n"); return 2; }
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
    // unique element sequences: uid[e], e = 16 i + j
    static uint32_t ua[256][16], ub[256][16];
    static int uid[256], mult[256];
    int ne = 0;
    for (int i = 0; i < 16; i++)
        for (int j = 0; j < 16; j++) {
            uint32_t ea[16], eb[16];
            for (int k = 0; k < 16; k++) { ea[k] = A[i][k]; eb[k] = B[k][j]; }
            int found = -1;
            for (int q = 0; q < ne; q++)
                if (!memcmp(ua[q], ea, sizeof ea) && !memcmp(ub[q], eb, sizeof eb)) { found = q; break; }
            if (found < 0) { memcpy(ua[ne], ea, sizeof ea); memcpy(ub[ne], eb, sizeof eb); mult[ne] = 0; found = ne++; }
            mult[found]++;
            uid[16 * i + j] = found;
        }
    static float fa[256][16], fb[256][16];
    static int64_t dk[256][16];
    static int act[256][16];
    static uint32_t cu[256], cb[256];
    for (int q = 0; q < ne; q++)
        for (int k = 0; k < 16; k++) {
            act[q][k] = ua[q][k] != 0 && ub[q][k] != 0;
            fa[q][k] = daz(ua[q][k]);
            fb[q][k] = daz(ub[q][k]);
            int64_t s = 0;
            for (int b8 = 0; b8 < 4; b8++) s += (int64_t)(int8_t)(ua[q][k] >> (8 * b8)) * (int8_t)(ub[q][k] >> (8 * b8));
            dk[q][k] = s;
        }
    int L = ty == 2 ? 16 : 8;
    uint32_t prev[16];
    int have[16];
    memset(prev, 0, sizeof prev);
    memset(have, 0, sizeof have);
    double cum_lane[MAXN], cum_acc[MAXN];
    for (int q = 0; q < MAXN; q++) cum_lane[q] = cum_acc[q] = 0.0;
    uint64_t tl = 0, ta = 0;
    int nxt = 0;
    for (int q = 0; q < ne; q++) cu[q] = 0;
    for (long op = 0; op < Nmax; op++) {
        int count = op >= 1;
        for (int k = 0; k < 16; k++) {
            memcpy(cb, cu, sizeof(uint32_t) * ne);       // every element's word before its update at this step
            // the lanes' C operands, in issue order
            if (ty == 2) {
                for (int i = 0; i < 16; i++)
                    for (int s = 0; s < 16; s++) {
                        int u = uid[16 * i + s];
                        if (!act[u][k]) continue;
                        uint32_t wd = cb[u];
                        if (have[s] && count) tl += pc32(prev[s] ^ wd);
                        prev[s] = wd;
                        have[s] = 1;
                    }
            } else {
                for (int i = 0; i < 16; i++)
                    for (int h = 0; h < 2; h++)
                        for (int l = 0; l < 8; l++) {
                            int u = uid[16 * i + 8 * h + l];
                            if (!act[u][k]) continue;
                            uint32_t wd = cb[u];
                            if (have[l] && count) tl += pc32(prev[l] ^ wd);
                            prev[l] = wd;
                            have[l] = 1;
                        }
            }
            // the updates (each unique state once; multiplicity for x_acc)
            for (int u = 0; u < ne; u++) {
                uint32_t c = cu[u], cn = c;
                if (ty == 0) {
                    if (op == 0 && k == 0) cn = ftz(fa[u][0] * fb[u][0]);
                    else if (act[u][k]) { fu cx; cx.u = c; cn = ftz(fmaf(fa[u][k], fb[u][k], cx.f)); }
                } else if (ty == 1) {
                    if (op == 0 && k == 0) cn = fp16_step(ua[u][0], ub[u][0], 0, 1);
                    else if (act[u][k]) cn = fp16_step(ua[u][k], ub[u][k], c, 0);
                } else {
                    cn = (uint32_t)((int64_t)(int32_t)c + dk[u][k]);
                }
                if (count) ta += (uint64_t)pc32(c ^ cn) * (uint64_t)mult[u];
                cu[u] = cn;
            }
        }
        while (nxt < nn && op == Ns[nxt] - 1) { cum_lane[nxt] = (double)tl; cum_acc[nxt] = (double)ta; nxt++; }
    }
    double xb = bth_per_op(ty);
    printf("{\"type\":\"%s\",\"unique_elements\":%d,\"lanes\":%d,\"uops_per_op\":%d,\"x_bth_per_op\":%.4f,\"x\":{", argv[1], ne, L,
           ty == 2 ? 256 : 512, xb);
    for (int q = 0; q < nn; q++) {
        double n1 = (double)(Ns[q] - 1);
        printf("\"%ld\":{\"x_lane\":%.6f,\"x_acc\":%.6f}%s", Ns[q], cum_lane[q] / n1, cum_acc[q] / n1, q + 1 < nn ? "," : "");
    }
    printf("}}\n");
    return 0;
}
