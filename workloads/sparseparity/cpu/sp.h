/* sp.h: sparse parity, the parts shared by the CPU reference (spref.c), the CPU baselines (spbase.c) and the
 * card's host program (M1+). Header-only; C11 and C++ (the card host is C++). Nothing here opens a card.
 *
 *   1. The instance generator: counter-based (splitmix64), bit-identical to proto/spbits.c, proto/sp.py and
 *      tools/spcore.py, so every instance has one definition everywhere. It is prefix-consistent: the first m1
 *      samples of (n, k, eta, m, seed) are the instance (n, k, eta, m1, seed), which is what the two-stage
 *      screen scans.
 *   2. Data layouts: bit-packed feature-major X and y; +-1 int8 (bit 0 -> +1 = 0x01, bit 1 -> -1 = 0xFF, padding
 *      samples 0); TensorIMA8A32's B tiles for the columns (the layout TensorLoadInterleave8 produces).
 *   3. Colex ranks of (k-1)-subsets and the T2 tile geometry: a candidate T = R + {j}, R a (k-1)-subset of
 *      0..n-2 with max(R) < j. Rows are R in colex order (row rank rho), 16 rows per row tile; columns are the raw
 *      features, 16 per column tile. Row tile t visits column tiles floor((pmin+1)/16) .. NJ-1, where pmin is the
 *      largest element of its first row; entries with j <= max(R) or j >= n are masked.
 *      Scores: c(T) = sum_i y~_i prod_{j in T} x~_ij = m - 2 * popcount(y ^ x_T) (exact int32).
 *      Order of candidates ("colex"): by j, then by rho; colex rank of T = C(j, k) + rho. The answer is the
 *      largest c; ties go to the smallest colex rank. Every per-hart best and top list uses this order.
 *   4. Coverage checksums over all C(n,k) candidates, and their closed forms (Krawtchouk polynomials
 *      K_k(w) = sum_t (-1)^t C(w,t) C(n-w,k-t)):  sum_T c(T) = sum_i y~_i K_k(w_i)  and
 *      sum_T c(T)^2 = sum_{i,i'} y~_i y~_i' K_k(d(x_i, x_i')). Sums of squares are kept modulo 2^64 (uint64
 *      wrap-around), the way an int64 accumulator on the card keeps them; the identity holds modulo 2^64.
 *   5. Binary formats: the work list (planner -> host -> kernel), the per-hart records and top lists
 *      (kernel -> host -> merge), survivor-log entries (two-stage screen). All little-endian; sizes are
 *      asserted below. tools/spcore.py parses the same layouts.
 */
#ifndef SP_H
#define SP_H

#include <inttypes.h>
#include <math.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define SP_KMAX 6          /* k <= 6, so a row subset has at most 5 elements */
#define SP_NMAX 4096       /* n <= 4096 (j fits 12 bits in a survivor entry) */
#define SP_TOPM_MAX 64

#ifdef __cplusplus
#define SP_STATIC_ASSERT(c, msg) static_assert(c, msg)
#else
#define SP_STATIC_ASSERT(c, msg) _Static_assert(c, msg)
#endif

/* ================================================================ 1. generator */
static inline uint64_t sp_mix64(uint64_t z) {
    z ^= z >> 30; z *= 0xbf58476d1ce4e5b9ULL;
    z ^= z >> 27; z *= 0x94d049bb133111ebULL;
    return z ^ (z >> 31);
}
/* Stream `stream` of instance `seed`, element `idx`. Streams: 1 = X words, 2 = label noise, 3 = the secret. */
static inline uint64_t sp_rnd(uint64_t seed, uint64_t stream, uint64_t idx) {
    uint64_t key = sp_mix64(seed * 0x9E3779B97F4A7C15ULL + stream * 0xD1B54A32D192ED03ULL + 0x632BE59BD9B4E019ULL);
    return sp_mix64(key + idx * 0x9E3779B97F4A7C15ULL);
}

typedef struct {
    int n, k, m;
    int Wm;            /* words that carry samples: ceil(m/64) */
    int W;             /* row stride in words, >= Wm; words Wm..W-1 are zero */
    double eta;
    uint64_t seed;
    uint64_t *X;       /* n x W, feature-major: bit (s & 63) of X[j*W + s/64] is feature j of sample s */
    uint64_t *y;       /* W words: the labels */
    uint64_t *noise;   /* W words: the flipped labels (evaluation only) */
    int secret[SP_KMAX];
} sp_inst_t;

static inline void *sp_alloc(size_t bytes) {
    void *p = NULL;
    if (posix_memalign(&p, 64, bytes ? (bytes + 63) / 64 * 64 : 64)) return NULL;
    memset(p, 0, bytes ? (bytes + 63) / 64 * 64 : 64);
    return p;
}

/* wpad: pad the stride W to a multiple of wpad words (1 = none; spbits uses 8 above 4 on AVX-512). */
static inline int sp_gen(sp_inst_t *I, int n, int k, double eta, int m, uint64_t seed, int wpad) {
    if (n < 2 || n > SP_NMAX || k < 1 || k > SP_KMAX || k > n || m < 1 || eta < 0 || eta >= 1) return -1;
    I->n = n; I->k = k; I->m = m; I->eta = eta; I->seed = seed;
    I->Wm = (m + 63) / 64;
    if (wpad < 1) wpad = 1;
    I->W = (I->Wm + wpad - 1) / wpad * wpad;
    const int W = I->W, Wm = I->Wm;
    const uint64_t last = (m % 64) ? ((1ULL << (m % 64)) - 1) : ~0ULL;
    I->X = (uint64_t *)sp_alloc((size_t)n * W * 8);
    I->y = (uint64_t *)sp_alloc((size_t)W * 8);
    I->noise = (uint64_t *)sp_alloc((size_t)W * 8);
    if (!I->X || !I->y || !I->noise) return -1;
    for (int j = 0; j < n; j++)
        for (int w = 0; w < Wm; w++) {
            uint64_t v = sp_rnd(seed, 1, ((uint64_t)j << 32) | (uint64_t)w);
            I->X[(size_t)j * W + w] = (w == Wm - 1) ? (v & last) : v;
        }
    int idx[SP_NMAX];          /* partial Fisher-Yates for the secret, as spbits.c */
    for (int j = 0; j < n; j++) idx[j] = j;
    for (int i = 0; i < k; i++) {
        uint64_t r = sp_rnd(seed, 3, (uint64_t)i) % (uint64_t)(n - i);
        int t = idx[i]; idx[i] = idx[i + r]; idx[i + r] = t;
    }
    for (int i = 0; i < k; i++) I->secret[i] = idx[i];
    for (int i = 1; i < k; i++)
        for (int j = i; j > 0 && I->secret[j - 1] > I->secret[j]; j--) {
            int t = I->secret[j]; I->secret[j] = I->secret[j - 1]; I->secret[j - 1] = t;
        }
    for (int i = k; i < SP_KMAX; i++) I->secret[i] = -1;
    const uint64_t thr = (uint64_t)(eta * 9007199254740992.0);   /* eta * 2^53 */
    for (int w = 0; w < Wm; w++) {
        uint64_t nz = 0;
        for (int b = 0; b < 64; b++) {
            uint64_t s = (uint64_t)w * 64 + b;
            if (s >= (uint64_t)m) break;
            if ((sp_rnd(seed, 2, s) >> 11) < thr) nz |= 1ULL << b;
        }
        I->noise[w] = nz;
        uint64_t v = nz;
        for (int i = 0; i < k; i++) v ^= I->X[(size_t)I->secret[i] * W + w];
        I->y[w] = v;
    }
    return 0;
}

static inline void sp_free(sp_inst_t *I) {
    free(I->X); free(I->y); free(I->noise);
    I->X = I->y = I->noise = NULL;
}

/* The hash spbits gen and sp.py --hash print (over the unpadded words). */
static inline uint64_t sp_hash(const sp_inst_t *I) {
    uint64_t h = 0x12345678ULL;
    for (int j = 0; j < I->n; j++)
        for (int w = 0; w < I->Wm; w++) h = sp_mix64(h ^ I->X[(size_t)j * I->W + w]);
    for (int w = 0; w < I->Wm; w++) h = sp_mix64(h ^ I->y[w]);
    return h;
}

/* Hash of a byte buffer (zero-padded to 8 B words, little-endian); tools/spcore.py bytes_hash() matches it. */
static inline uint64_t sp_bytes_hash(const void *buf, size_t len) {
    const uint8_t *p = (const uint8_t *)buf;
    uint64_t h = 0x9E3779B97F4A7C15ULL ^ (uint64_t)len;
    for (size_t o = 0; o < len; o += 8) {
        uint64_t v = 0;
        for (size_t b = 0; b < 8 && o + b < len; b++) v |= (uint64_t)p[o + b] << (8 * b);
        h = sp_mix64(h ^ v);
    }
    return h;
}

static inline int sp_bit(const uint64_t *v, int s) { return (int)((v[s >> 6] >> (s & 63)) & 1); }
static inline int sp_popcount_words(const uint64_t *a, int W) {
    int c = 0;
    for (int w = 0; w < W; w++) c += __builtin_popcountll(a[w]);
    return c;
}

/* ================================================================ 2. layouts */
/* Samples padded to mp = 64 * S, S = ceil(m / 64) sample slices of 64 (one TensorIMA8A32 K-depth each). */
static inline int sp_slices(int m) { return (m + 63) / 64; }

/* +-1 bytes, feature-major: out[j * mp + s] = x~_sj for s < m, 0 for m <= s < mp. */
static inline void sp_pm1_features(const sp_inst_t *I, int mp, int8_t *out) {
    for (int j = 0; j < I->n; j++)
        for (int s = 0; s < mp; s++)
            out[(size_t)j * mp + s] = s < I->m ? (int8_t)(1 - 2 * sp_bit(I->X + (size_t)j * I->W, s)) : 0;
}
static inline void sp_pm1_labels(const sp_inst_t *I, int mp, int8_t *out) {
    for (int s = 0; s < mp; s++) out[s] = s < I->m ? (int8_t)(1 - 2 * sp_bit(I->y, s)) : 0;
}

/* B tiles: tile (J, s) is the 1 KB at out + (J * S + s) * 1024, TensorIMA8A32's B operand for the columns
 * 16J .. 16J+15 and the samples 64s .. 64s+63. Line r (64 B, r = 0..15) holds, for column c, the four bytes
 * x~[16J+c][64s + 4r + e] (e = 0..3) at byte 4c + e: the layout TensorLoadInterleave8 writes and the one
 * sw-sysemu's tensor_ima8a32_execute reads (tmpb.u8[j*4 + x]). Columns >= n and samples >= m are 0. */
static inline size_t sp_btiles_bytes(int n, int S) { return (size_t)((n + 15) / 16) * (size_t)S * 1024; }
static inline void sp_btiles(const sp_inst_t *I, int S, int8_t *out) {
    const int NJ = (I->n + 15) / 16;
    for (int J = 0; J < NJ; J++)
        for (int s = 0; s < S; s++) {
            int8_t *t = out + ((size_t)J * S + s) * 1024;
            for (int r = 0; r < 16; r++)
                for (int c = 0; c < 16; c++)
                    for (int e = 0; e < 4; e++) {
                        int j = 16 * J + c, smp = 64 * s + 4 * r + e;
                        t[r * 64 + 4 * c + e] = (j < I->n && smp < I->m)
                            ? (int8_t)(1 - 2 * sp_bit(I->X + (size_t)j * I->W, smp)) : 0;
                    }
        }
}

/* Sample-major bits (m x nw words, nw = ceil(n/64)): bit j of xs[i*nw + j/64] is feature j of sample i. */
static inline uint64_t *sp_sample_major(const sp_inst_t *I, int *nw_out) {
    const int nw = (I->n + 63) / 64;
    uint64_t *xs = (uint64_t *)sp_alloc((size_t)I->m * nw * 8);
    for (int j = 0; j < I->n; j++)
        for (int i = 0; i < I->m; i++)
            if (sp_bit(I->X + (size_t)j * I->W, i)) xs[(size_t)i * nw + j / 64] |= 1ULL << (j & 63);
    *nw_out = nw;
    return xs;
}

/* ================================================================ 3. colex ranks and the T2 geometry */
typedef struct {
    int n, k, a;        /* a = k - 1: elements in a row subset */
    int m, S, mp;       /* samples scanned, sample slices, padded samples */
    int NJ;             /* column tiles: ceil(n / 16) */
    uint64_t NR, NT;    /* rows = C(n-1, a) (a-subsets of 0..n-2), row tiles = ceil(NR / 16) */
    uint64_t Ncand;     /* C(n, k) */
    uint64_t *Cb;       /* binomial table: Cb[p * (k+1) + t] = C(p, t), p = 0..n, t = 0..k */
} sp_geom_t;

static inline uint64_t sp_C(const sp_geom_t *G, int p, int t) {
    if (t < 0 || p < 0 || t > p) return 0;
    return G->Cb[(size_t)p * (G->k + 1) + t];
}

static inline int sp_geom_init(sp_geom_t *G, int n, int k, int m) {
    if (k < 2 || k > SP_KMAX || n < k || n > SP_NMAX) return -1;
    G->n = n; G->k = k; G->a = k - 1; G->m = m;
    G->S = sp_slices(m); G->mp = 64 * G->S; G->NJ = (n + 15) / 16;
    G->Cb = (uint64_t *)calloc((size_t)(n + 1) * (k + 1), sizeof(uint64_t));
    if (!G->Cb) return -1;
    for (int p = 0; p <= n; p++) {
        G->Cb[(size_t)p * (k + 1)] = 1;
        for (int t = 1; t <= k && t <= p; t++)
            G->Cb[(size_t)p * (k + 1) + t] = G->Cb[(size_t)(p - 1) * (k + 1) + t - 1] +
                                             (t <= p - 1 ? G->Cb[(size_t)(p - 1) * (k + 1) + t] : 0);
    }
    G->NR = sp_C(G, n - 1, G->a);
    G->NT = (G->NR + 15) / 16;
    G->Ncand = sp_C(G, n, k);
    return 0;
}
static inline void sp_geom_free(sp_geom_t *G) { free(G->Cb); G->Cb = NULL; }

/* colex rank of an ascending a-subset: sum_t C(R[t], t+1) */
static inline uint64_t sp_rank(const sp_geom_t *G, const int *R, int a) {
    uint64_t r = 0;
    for (int t = 0; t < a; t++) r += sp_C(G, R[t], t + 1);
    return r;
}
/* largest p in [lo, hi] with C(p, t) <= v (C(lo, t) <= v assumed) */
static inline int sp_pmax(const sp_geom_t *G, int t, uint64_t v, int lo, int hi) {
    while (lo < hi) {
        int mid = (lo + hi + 1) / 2;
        if (sp_C(G, mid, t) <= v) lo = mid; else hi = mid - 1;
    }
    return lo;
}
static inline void sp_unrank(const sp_geom_t *G, uint64_t rank, int *R, int a) {
    int hi = G->n;
    for (int t = a - 1; t >= 0; t--) {
        int p = sp_pmax(G, t + 1, rank, t, hi - 1);
        R[t] = p;
        rank -= sp_C(G, p, t + 1);
        hi = p;
    }
}
/* colex successor of an ascending a-subset; returns the highest position that changed */
static inline int sp_next(int *R, int a) {
    int t = 0;
    while (t < a - 1 && R[t] + 1 == R[t + 1]) t++;
    R[t]++;
    for (int u = 0; u < t; u++) R[u] = u;
    return t;
}
/* largest element of row `rank` */
static inline int sp_row_max(const sp_geom_t *G, uint64_t rank) {
    return sp_pmax(G, G->a, rank, G->a - 1, G->n - 1);
}
/* first column tile of row tile t */
static inline int sp_tile_j0(const sp_geom_t *G, uint64_t t) { return (sp_row_max(G, 16 * t) + 1) / 16; }
/* first row tile whose first column tile is >= q (q = 0..NJ) */
static inline uint64_t sp_tile_of_j0(const sp_geom_t *G, int q) {
    if (q <= 0) return 0;
    int p = 16 * q - 1;
    if (p > G->n - 2) return G->NT;
    uint64_t c = sp_C(G, p, G->a);
    uint64_t t = (c + 15) / 16;
    return t < G->NT ? t : G->NT;
}
/* output tiles (row tile x column tile) in row tiles [t0, t1): tensor ops = S times this */
static inline uint64_t sp_range_outtiles(const sp_geom_t *G, uint64_t t0, uint64_t t1) {
    uint64_t tot = 0;
    for (int q = 0; q < G->NJ; q++) {
        uint64_t a0 = sp_tile_of_j0(G, q), a1 = sp_tile_of_j0(G, q + 1);
        uint64_t lo = a0 > t0 ? a0 : t0, hi = a1 < t1 ? a1 : t1;
        if (hi > lo) tot += (hi - lo) * (uint64_t)(G->NJ - q);
    }
    return tot;
}
/* candidates (valid entries) in row tiles [t0, t1): rows with max p contribute n-1-p each */
static inline uint64_t sp_range_cands(const sp_geom_t *G, uint64_t t0, uint64_t t1) {
    uint64_t r0 = 16 * t0, r1 = 16 * t1 < G->NR ? 16 * t1 : G->NR, tot = 0;
    for (int p = G->a - 1; p <= G->n - 2; p++) {
        uint64_t a0 = sp_C(G, p, G->a), a1 = sp_C(G, p + 1, G->a);
        uint64_t lo = a0 > r0 ? a0 : r0, hi = a1 < r1 ? a1 : r1;
        if (hi > lo) tot += (hi - lo) * (uint64_t)(G->n - 1 - p);
    }
    return tot;
}

/* ================================================================ 4. checksums: closed forms */
/* C(n, t) exactly (0 if t < 0 or t > n); the running product stays exact since C(n-t+i, i) is an integer */
static inline uint64_t sp_binom(int n, int t) {
    if (t < 0 || t > n) return 0;
    unsigned __int128 r = 1;
    for (int i = 1; i <= t; i++) r = r * (unsigned __int128)(n - t + i) / (unsigned __int128)i;
    return (uint64_t)r;
}
/* K_k(w) for w = 0..n (exact: |K_k(w)| <= C(n, k)) */
static inline void sp_krawtchouk(int n, int k, int64_t *K) {
    for (int w = 0; w <= n; w++) {
        __int128 s = 0;
        for (int t = 0; t <= k; t++) {
            __int128 v = (__int128)sp_binom(w, t) * (__int128)sp_binom(n - w, k - t);
            s += (t & 1) ? -v : v;
        }
        K[w] = (int64_t)s;
    }
}
/* sum_T c(T) and sum_T c(T)^2 over all C(n,k) candidates, from the data alone: O(m n) and O(m^2 n / 64).
 * *sq_fits = 1 when the exact sum of squares is below 2^63 (then the modular value is the true value). */
static inline void sp_closed_forms(const sp_inst_t *I, int64_t *sum_c, uint64_t *sum_c2, int *sq_fits) {
    const int n = I->n, k = I->k, m = I->m;
    int64_t *K = (int64_t *)malloc(sizeof(int64_t) * (n + 1));
    sp_krawtchouk(n, k, K);
    int nw;
    uint64_t *xs = sp_sample_major(I, &nw);
    int *yt = (int *)malloc(sizeof(int) * m);
    __int128 s1 = 0, s2 = 0;
    for (int i = 0; i < m; i++) {
        yt[i] = 1 - 2 * sp_bit(I->y, i);
        s1 += (__int128)yt[i] * K[sp_popcount_words(xs + (size_t)i * nw, nw)];
    }
    for (int i = 0; i < m; i++) {
        __int128 row = K[0];   /* i' = i: d = 0, y~^2 = 1 */
        for (int i2 = i + 1; i2 < m; i2++) {
            int d = 0;
            for (int w = 0; w < nw; w++) d += __builtin_popcountll(xs[(size_t)i * nw + w] ^ xs[(size_t)i2 * nw + w]);
            __int128 v = 2 * (__int128)K[d];
            row += (yt[i] == yt[i2]) ? v : -v;
        }
        s2 += row;
    }
    *sum_c = (int64_t)s1;
    *sum_c2 = (uint64_t)s2;
    *sq_fits = s2 >= 0 && s2 < ((__int128)1 << 63);
    free(K); free(xs); free(yt);
}

/* ================================================================ 5. per-candidate statistics */
/* Better = larger c; on equal c, smaller colex rank (smaller j, then smaller row rank). */
static inline int sp_better(int32_t c1, uint32_t j1, uint64_t r1, int32_t c2, uint32_t j2, uint64_t r2) {
    return c1 > c2 || (c1 == c2 && (j1 < j2 || (j1 == j2 && r1 < r2)));
}

typedef struct { int32_t c; uint32_t j; uint64_t row; } sp_top_t;   /* 16 B; c == INT32_MIN: empty slot */

typedef struct {
    int topm;                  /* entries kept (0..SP_TOPM_MAX); the best is kept regardless */
    int has_best;
    int32_t best_c; uint32_t best_j; uint64_t best_row;
    int64_t sum_c; uint64_t sum_c2; uint64_t cands; uint64_t ops;
    int ntop;
    int tie;                   /* another candidate has c == best_c (the card's tie flag; exact under merges) */
    int32_t thr;               /* a candidate below thr cannot enter the best or the top list */
    sp_top_t top[SP_TOPM_MAX]; /* best first */
} sp_stats_t;

static inline void sp_stats_init(sp_stats_t *S, int topm) {
    memset(S, 0, sizeof *S);
    S->topm = topm < 0 ? 0 : (topm > SP_TOPM_MAX ? SP_TOPM_MAX : topm);
    S->best_c = INT32_MIN;
    S->thr = INT32_MIN;
    for (int i = 0; i < SP_TOPM_MAX; i++) S->top[i].c = INT32_MIN;
}
/* the slow path: c >= S->thr */
static inline void sp_stats_offer(sp_stats_t *S, int32_t c, uint32_t j, uint64_t row) {
    if (S->has_best && c == S->best_c) S->tie = 1;               /* a second candidate at the best c */
    else if (!S->has_best || c > S->best_c) S->tie = 0;
    if (!S->has_best || sp_better(c, j, row, S->best_c, S->best_j, S->best_row)) {
        S->has_best = 1; S->best_c = c; S->best_j = j; S->best_row = row;
    }
    if (S->topm > 0) {
        int pos = S->ntop;
        if (pos == S->topm) {
            const sp_top_t *w = &S->top[pos - 1];
            if (!sp_better(c, j, row, w->c, w->j, w->row)) goto done;
            pos--;
        } else {
            S->ntop++;
        }
        while (pos > 0 && sp_better(c, j, row, S->top[pos - 1].c, S->top[pos - 1].j, S->top[pos - 1].row)) {
            S->top[pos] = S->top[pos - 1];
            pos--;
        }
        S->top[pos].c = c; S->top[pos].j = j; S->top[pos].row = row;
    }
done:
    S->thr = (S->topm > 0) ? (S->ntop == S->topm ? S->top[S->topm - 1].c : INT32_MIN) : S->best_c;
}
static inline void sp_stats_add(sp_stats_t *S, int32_t c, uint32_t j, uint64_t row) {
    S->sum_c += c;
    S->sum_c2 += (uint64_t)((int64_t)c * c);
    S->cands++;
    if (c >= S->thr) sp_stats_offer(S, c, j, row);
}
/* D and X hold disjoint candidate sets. */
static inline void sp_stats_merge(sp_stats_t *D, const sp_stats_t *X) {
    D->sum_c += X->sum_c; D->sum_c2 += X->sum_c2; D->cands += X->cands; D->ops += X->ops;
    int tie = D->tie;
    if (X->has_best) {
        if (!D->has_best || X->best_c > D->best_c) tie = X->tie;
        else if (X->best_c == D->best_c) tie = 1;
    }
    if (X->has_best) sp_stats_offer(D, X->best_c, X->best_j, X->best_row);
    for (int i = 0; i < X->ntop; i++) {
        const sp_top_t *e = &X->top[i];
        if (X->has_best && e->c == X->best_c && e->j == X->best_j && e->row == X->best_row) continue;
        sp_stats_offer(D, e->c, e->j, e->row);
    }
    D->tie = tie;
}

/* ================================================================ 6. binary formats */
/* Work list: sp_wl_hdr_t, then nminions x sp_wl_minion_t, then nranges x sp_wl_range_t. The planner
 * (tools/planner.py) writes it; the card host passes it to the kernel; spref plan= runs it on the CPU.
 * A minion is logical: index = shire_index * mps + minion_in_shire, shire_index = the rank of the physical
 * shire among the set bits of shire_mask (as sgemm numbers them). */
#define SP_WL_MAGIC 0x4c575053u        /* "SPWL" */
#define SP_WL_VERSION 1u
#define SP_WL_TWOSTAGE 1u              /* flags: log survivors with c >= tau1 (the scan runs on m = m1 samples) */
#define SP_WL_COOP 2u                  /* flags: the cost model assumed cooperative B loads */
typedef struct {
    uint32_t magic, version;
    uint32_t n, k, m, S;               /* m = samples this launch scans (m1 in a two-stage screen) */
    uint32_t nshires, mps, nminions, nranges;
    uint32_t topm, flags;
    int32_t tau1;
    uint32_t slice, nslices, blocks_per_minion;
    uint64_t shire_mask;
    uint64_t NR, NT, total_ops, total_cands, total_cyc;   /* of the ranges in this file */
    uint64_t reserved[2];
} sp_wl_hdr_t;
typedef struct { uint32_t first_range, nranges, shire, minion; } sp_wl_minion_t;   /* shire: logical index */
typedef struct {
    uint64_t tile_begin, tile_end;     /* row tiles [tile_begin, tile_end) */
    uint64_t ops, cands, cyc;          /* tensor ops, candidates, modelled cycles */
    uint16_t first_R[SP_KMAX];         /* the a-subset of row 16*tile_begin, ascending (unused slots 0xFFFF) */
    uint32_t minion;                   /* logical minion that owns the range */
    uint32_t block;                    /* its block number in colex order */
    uint32_t reserved;
} sp_wl_range_t;
SP_STATIC_ASSERT(sizeof(sp_wl_hdr_t) == 128, "work-list header is 128 B");
SP_STATIC_ASSERT(sizeof(sp_wl_minion_t) == 16, "minion entry is 16 B");
SP_STATIC_ASSERT(sizeof(sp_wl_range_t) == 64, "range entry is one 64 B line");

/* Output: sp_out_hdr_t, then nminions * harts sp_rec_t (index minion * harts + hart), then nminions * topm
 * sp_top_t (hart 0's top list, best first, empty slots c = INT32_MIN). Each hart writes only its own lines. */
#define SP_OUT_MAGIC 0x314f5053u       /* "SPO1" */
#define SP_REC_MAGIC 0x31525053u       /* "SPR1" */
#define SP_REC_VALID 1u
#define SP_REC_HAS_BEST 2u
#define SP_REC_LOG_OVERFLOW 4u
#define SP_REC_ERROR 8u
#define SP_REC_TIE 16u                 /* another candidate of this hart has c equal to its best c (a tie) */
typedef struct {
    uint32_t magic, version, nminions, harts, topm, n, k, m;
    uint64_t nranges, total_ops, total_cands, reserved;
} sp_out_hdr_t;
typedef struct {
    uint32_t magic;
    uint16_t hart;                     /* 0: tensor ops + epilogue (the scores); 1: row generation */
    uint16_t flags;
    uint32_t minion;                   /* logical minion */
    int32_t best_c;
    uint64_t best_row;                 /* colex rank of R */
    uint32_t best_j;
    uint32_t ops;                      /* hart 0: tensor ops; hart 1: row tiles generated */
    int64_t sum_c;
    uint64_t sum_c2;                   /* modulo 2^64 */
    uint64_t cands;
    uint64_t cycles;                   /* hpmcounter3 exit - entry (fixcyc-corrected); 0 on the CPU */
} sp_rec_t;
SP_STATIC_ASSERT(sizeof(sp_out_hdr_t) == 64, "output header is 64 B");
SP_STATIC_ASSERT(sizeof(sp_rec_t) == 64, "a record is one 64 B line");
SP_STATIC_ASSERT(sizeof(sp_top_t) == 16, "a top entry is 16 B");

/* Survivor-log entry of the two-stage screen: row rank (40 bits) | j << 40 (12 bits) | c1 << 52 (12 bits,
 * 0 <= c1 < 4096). Sorted by value's (j, row) = colex order when compared with sp_surv_key. */
static inline uint64_t sp_surv_pack(uint64_t row, uint32_t j, int32_t c1) {
    return (row & 0xFFFFFFFFFFULL) | ((uint64_t)(j & 0xFFF) << 40) | ((uint64_t)(c1 & 0xFFF) << 52);
}
static inline uint64_t sp_surv_row(uint64_t e) { return e & 0xFFFFFFFFFFULL; }
static inline uint32_t sp_surv_j(uint64_t e) { return (uint32_t)((e >> 40) & 0xFFF); }
static inline int32_t sp_surv_c1(uint64_t e) { return (int32_t)(e >> 52); }
static inline uint64_t sp_surv_key(uint64_t e) { return ((uint64_t)sp_surv_j(e) << 40) | sp_surv_row(e); }

/* ================================================================ 7. host-side helpers */
/* c(T) on all m samples for the candidate (row, j): the stage-2 rescoring of the two-stage screen */
static inline int32_t sp_score(const sp_inst_t *I, const sp_geom_t *G, uint64_t row, uint32_t j, uint64_t *tmp) {
    int R[SP_KMAX];
    sp_unrank(G, row, R, G->a);
    for (int w = 0; w < I->Wm; w++) {
        uint64_t v = I->y[w] ^ I->X[(size_t)j * I->W + w];
        for (int t = 0; t < G->a; t++) v ^= I->X[(size_t)R[t] * I->W + w];
        tmp[w] = v;
    }
    return I->m - 2 * sp_popcount_words(tmp, I->Wm);
}

/* stats -> record (hart 0) */
static inline void sp_stats_to_rec(const sp_stats_t *S, uint32_t minion, sp_rec_t *r) {
    memset(r, 0, sizeof *r);
    r->magic = SP_REC_MAGIC; r->hart = 0; r->minion = minion;
    r->flags = (uint16_t)(SP_REC_VALID | (S->has_best ? SP_REC_HAS_BEST : 0) | (S->has_best && S->tie ? SP_REC_TIE : 0));
    r->best_c = S->has_best ? S->best_c : INT32_MIN;
    r->best_row = S->best_row; r->best_j = S->best_j;
    r->ops = (uint32_t)S->ops;
    r->sum_c = S->sum_c; r->sum_c2 = S->sum_c2; r->cands = S->cands;
}

#endif /* SP_H */
