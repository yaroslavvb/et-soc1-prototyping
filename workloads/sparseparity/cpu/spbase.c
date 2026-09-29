// spbase.c: the CPU baselines the card is compared with (milestone M0). Host CPU only; opens no card.
//
//   vexh   exhaustive scan, vectorised across candidates: 8 candidates (8 last features j) per 512-bit
//          register, word-major X, AVX-512 VPOPCNTQ; prefix XORs over i1 < ... < i_{k-1}; OpenMP over the
//          (i1, i2) prefixes. The critique's `vexh` (SP5), made parallel and exact: ties go to the smallest
//          colex rank as in sp.h, sums=1 accumulates the coverage checksums, tau= logs the survivors of a
//          two-stage screen (stage 1 on the first m samples; m2= rescoring on all m2 samples, timed separately).
//   mitm   bucketed meet-in-the-middle (bit-sampling LSH, GRV-style): each repetition samples r positions,
//          buckets the a-subsets (a = floor(k/2)) by the r-bit fingerprint of y + x_A, probes with every
//          b-subset (b = k - a), verifies each collision on all m samples. split=1 (the default for k >= 4; review
//          R2, finding 4) also draws a random halving of the features each repetition and takes the a-subsets from
//          one half and the b-subsets from the other: each k-set then appears once instead of C(k,a) times, the
//          tables are 2^a and 2^b times smaller and the false collisions 2^k times fewer, for a C(k,a)/2^k chance
//          that the secret is split right. The secret collides in a repetition when it is split right and none of
//          the r sampled labels is noisy: q = C(k,a)/2^k * C(m-t, r)/C(m, r) for t noisy labels. Stops at the
//          first candidate that clears the union-bound acceptance threshold (false accept <= fa), or after
//          ln(1/delta)/q repetitions (then it returns the best seen). OpenMP over repetitions. expected_s_full
//          is this seed's expected time: 1/q repetitions when the secret can clear the threshold, else the cap.
//   batch  B1: `count` independent instances (seeds seed..seed+count-1). lanes=1 (the default, m <= 64; review
//          R2, finding 3): 8 instances per 512-bit register, one 64-bit lane each, an exhaustive scan with the
//          prefix XORs shared; lanes=0: each instance by a one-thread vexh. OpenMP over groups of 8 instances.
//
// Every subcommand prints one JSON object. Instances come from sp.h (= proto/spbits.c = tools/spcore.py).
// Build: make (in this directory; -O3 -march=native -fopenmp; needs AVX-512F/DQ/VPOPCNTDQ).

#define _GNU_SOURCE
#include "sp.h"
#include <immintrin.h>
#include <time.h>
#ifdef _OPENMP
#include <omp.h>
#endif
#if !defined(__AVX512F__) || !defined(__AVX512VPOPCNTDQ__) || !defined(__AVX512DQ__)
#error "spbase needs AVX-512F, AVX-512DQ and AVX-512 VPOPCNTDQ (build with -march=native on Ice Lake / Rocket Lake or later)"
#endif

static double now(void) {
    struct timespec t;
    clock_gettime(CLOCK_MONOTONIC, &t);
    return t.tv_sec + 1e-9 * t.tv_nsec;
}

static int g_argc;
static char **g_argv;
static const char *argval(const char *key, const char *def) {
    size_t L = strlen(key);
    for (int i = 2; i < g_argc; i++)
        if (!strncmp(g_argv[i], key, L) && g_argv[i][L] == '=') return g_argv[i] + L + 1;
    if (!def) { fprintf(stderr, "missing %s=\n", key); exit(2); }
    return def;
}
static long argl(const char *key, const char *def) { return strtol(argval(key, def), 0, 0); }
static double argd(const char *key, const char *def) { return strtod(argval(key, def), 0); }

static void print_set(const int *s, int k) {
    printf("[");
    for (int i = 0; i < k; i++) printf("%s%d", i ? "," : "", s[i]);
    printf("]");
}
static int threads_now(void) {
#ifdef _OPENMP
    return omp_get_max_threads();
#else
    return 1;
#endif
}

// colex rank of an ascending k-set (tie-break key; sp.h order)
static uint64_t colex_key(const sp_geom_t *G, const int *T, int k) {
    uint64_t r = 0;
    for (int t = 0; t < k; t++) r += sp_C(G, T[t], t + 1);
    return r;
}

// ================================================================ vexh
typedef struct {
    const sp_inst_t *I;
    const sp_geom_t *G;
    int n, k, Wm, np;
    uint64_t *Xw;          // Wm x np, word-major: Xw[w * np + j]; columns n..np-1 are zero
    int sums;              // accumulate sum d and sum d^2
    uint32_t dsurv;        // log survivors with d <= dsurv (UINT32_MAX: off)
    int slice;
} vctx_t;

typedef struct {
    uint32_t bestd;
    uint64_t best_key, nbest, subsets;
    int arg[SP_KMAX];
    uint64_t sd, sd2;      // sum of d and of d^2 over the scanned candidates (sums=1)
    uint64_t *surv;        // survivors: the k indices, 12 bits each
    size_t nsurv, capsurv;
} vacc_t;

static void vnote(const vctx_t *V, vacc_t *A, uint32_t d, const int *pre, int j) {
    int T[SP_KMAX];
    for (int i = 0; i < V->k - 1; i++) T[i] = pre[i];
    T[V->k - 1] = j;
    if (d < A->bestd) {
        A->bestd = d; A->nbest = 1;
        A->best_key = colex_key(V->G, T, V->k);
        memcpy(A->arg, T, sizeof T);
    } else if (d == A->bestd) {
        A->nbest++;
        uint64_t key = colex_key(V->G, T, V->k);
        if (key < A->best_key) { A->best_key = key; memcpy(A->arg, T, sizeof T); }
    }
}
static void vsurv(vacc_t *A, const int *pre, int k, int j) {
    if (A->nsurv == A->capsurv) {
        A->capsurv = A->capsurv ? 2 * A->capsurv : 4096;
        A->surv = (uint64_t *)realloc(A->surv, A->capsurv * 8);
    }
    uint64_t e = 0;
    for (int i = 0; i < k - 1; i++) e |= (uint64_t)pre[i] << (12 * i);
    A->surv[A->nsurv++] = e | (uint64_t)j << (12 * (k - 1));
}

// NBLK = 4 sibling prefixes at once: they share the first d prefix elements (pre[0..d-1]) and have last prefix
// elements c0, c0+1, c0+2, c0+3 (nb of them valid), packed XORs P[i] = y ^ x_pre ^ x_{c0+i}. Every 512-bit load of
// X (8 candidates j, one word) is reused by the 4 prefixes: without the blocking the scan streams all of X from L2
// once per prefix and runs at about half the port-bound rate (measured on aifoundry3, 29 September).
#define NBLK 4
static inline __attribute__((always_inline)) void vinner4_t(const vctx_t *V, vacc_t *A, const uint64_t *const *P,
                                                             int *pre, int d, int c0, int nb, const int WC,
                                                             const int SUMS, const int SURV) {
    const int n = V->n, np = V->np;
    const uint64_t *Xw = V->Xw;
    const uint64_t *P0 = P[0], *P1 = P[1], *P2 = P[2], *P3 = P[3];
    __m512i bestv = _mm512_set1_epi64((long long)A->bestd);
    const __m512i survv = _mm512_set1_epi64((long long)V->dsurv);
    __m512i sd = _mm512_setzero_si512(), sd2 = _mm512_setzero_si512();
    for (int i = 0; i < nb; i++) A->subsets += (uint64_t)(n - (c0 + i + 1));
    for (int j = (c0 + 1) & ~7; j < n; j += 8) {
        __m512i a[NBLK];
        a[0] = a[1] = a[2] = a[3] = _mm512_setzero_si512();
        for (int w = 0; w < WC; w++) {
            __m512i x = _mm512_load_si512((const void *)(Xw + (size_t)w * np + j));
            a[0] = _mm512_add_epi64(a[0], _mm512_popcnt_epi64(_mm512_xor_si512(x, _mm512_set1_epi64((long long)P0[w]))));
            a[1] = _mm512_add_epi64(a[1], _mm512_popcnt_epi64(_mm512_xor_si512(x, _mm512_set1_epi64((long long)P1[w]))));
            a[2] = _mm512_add_epi64(a[2], _mm512_popcnt_epi64(_mm512_xor_si512(x, _mm512_set1_epi64((long long)P2[w]))));
            a[3] = _mm512_add_epi64(a[3], _mm512_popcnt_epi64(_mm512_xor_si512(x, _mm512_set1_epi64((long long)P3[w]))));
        }
        const __mmask8 tail = (j + 8 > n) ? (__mmask8)(0xFF >> (j + 8 - n)) : (__mmask8)0xFF;
        for (int i = 0; i < NBLK; i++) {
            if (i >= nb) break;
            const int start = c0 + i + 1;
            const __mmask8 valid = (j < start) ? (__mmask8)(tail & (0xFF << (start - j))) : tail;
            if (SUMS) {
                sd = _mm512_mask_add_epi64(sd, valid, sd, a[i]);
                sd2 = _mm512_mask_add_epi64(sd2, valid, sd2, _mm512_mullo_epi64(a[i], a[i]));
            }
            if (SURV) {
                __mmask8 sh = _mm512_mask_cmple_epu64_mask(valid, a[i], survv);
                if (__builtin_expect(sh != 0, 0)) {
                    pre[d] = c0 + i;
                    for (int l = 0; l < 8; l++)
                        if (sh >> l & 1) vsurv(A, pre, V->k, j + l);
                }
            }
            __mmask8 hit = _mm512_mask_cmple_epu64_mask(valid, a[i], bestv);
            if (__builtin_expect(hit != 0, 0)) {
                uint64_t lanes[8];
                _mm512_storeu_si512((void *)lanes, a[i]);
                pre[d] = c0 + i;
                for (int l = 0; l < 8; l++)
                    if (hit >> l & 1) vnote(V, A, (uint32_t)lanes[l], pre, j + l);
                bestv = _mm512_set1_epi64((long long)A->bestd);
            }
        }
    }
    if (SUMS) {
        A->sd += (uint64_t)_mm512_reduce_add_epi64(sd);
        A->sd2 += (uint64_t)_mm512_reduce_add_epi64(sd2);
    }
}

// Wm is a compile-time constant for the ladder's sizes (C0/C1 1-3, L1 7, the two-stage m1 13 and 20, L2 29,
// (256,5) 31, L5 34) on the timed paths; the checksum path (sums=1, a correctness check) takes the generic loop
#define VCASE(WC)                                                              \
    case WC:                                                                   \
        if (surv) vinner4_t(V, A, P, pre, d, c0, nb, WC, 0, 1);                \
        else vinner4_t(V, A, P, pre, d, c0, nb, WC, 0, 0);                     \
        break;

static void vinner4(const vctx_t *V, vacc_t *A, const uint64_t *const *P, int *pre, int d, int c0, int nb) {
    const int surv = V->dsurv != UINT32_MAX;
    if (V->sums) {
        if (surv) vinner4_t(V, A, P, pre, d, c0, nb, V->Wm, 1, 1);
        else vinner4_t(V, A, P, pre, d, c0, nb, V->Wm, 1, 0);
        return;
    }
    switch (V->Wm) {
        VCASE(1) VCASE(2) VCASE(3) VCASE(4) VCASE(5) VCASE(6) VCASE(7) VCASE(8)
        VCASE(13) VCASE(20) VCASE(29) VCASE(30) VCASE(31) VCASE(34)
    default:
        if (surv) vinner4_t(V, A, P, pre, d, c0, nb, V->Wm, 0, 1);
        else vinner4_t(V, A, P, pre, d, c0, nb, V->Wm, 0, 0);
    }
}

// the last prefix element c in [cbeg, cend], in groups of NBLK; Pprev = y ^ x_pre[0..d-1]; gbuf: NBLK * Wm words
static void vgroups(const vctx_t *V, vacc_t *A, const uint64_t *Pprev, int *pre, int d, int cbeg, int cend,
                    uint64_t *gbuf) {
    const sp_inst_t *I = V->I;
    const int Wm = V->Wm;
    for (int c0 = cbeg; c0 <= cend; c0 += NBLK) {
        const int nb = cend - c0 + 1 < NBLK ? cend - c0 + 1 : NBLK;
        const uint64_t *P[NBLK];
        for (int i = 0; i < NBLK; i++) {
            if (i >= nb) { P[i] = P[0]; continue; }
            uint64_t *q = gbuf + (size_t)i * Wm;
            const uint64_t *xc = I->X + (size_t)(c0 + i) * I->W;
            for (int w = 0; w < Wm; w++) q[w] = Pprev[w] ^ xc[w];
            P[i] = q;
        }
        vinner4(V, A, P, pre, d, c0, nb);
    }
}

// prefix levels d .. k-3 (buf holds the running XORs, Wm words per level); level k-2 goes to vgroups
static void vrec(const vctx_t *V, vacc_t *A, uint64_t *buf, uint64_t *gbuf, int *pre, int d) {
    const sp_inst_t *I = V->I;
    const int n = V->n, k = V->k, Wm = V->Wm;
    const uint64_t *P = buf + (size_t)(d - 1) * Wm;
    if (d == k - 2) { vgroups(V, A, P, pre, d, pre[d - 1] + 1, n - 2, gbuf); return; }
    uint64_t *Q = buf + (size_t)d * Wm;
    for (int j = pre[d - 1] + 1; j <= n - (k - d); j++) {
        const uint64_t *xj = I->X + (size_t)j * I->W;
        for (int w = 0; w < Wm; w++) Q[w] = P[w] ^ xj[w];
        pre[d] = j;
        vrec(V, A, buf, gbuf, pre, d + 1);
    }
}

static void vctx_init(vctx_t *V, const sp_inst_t *I, const sp_geom_t *G) {
    memset(V, 0, sizeof *V);
    V->I = I; V->G = G; V->n = I->n; V->k = I->k; V->Wm = I->Wm;
    V->np = (I->n + 7) / 8 * 8 + 8;
    V->Xw = (uint64_t *)sp_alloc(sizeof(uint64_t) * (size_t)V->Wm * V->np);
    for (int w = 0; w < V->Wm; w++)
        for (int j = 0; j < I->n; j++) V->Xw[(size_t)w * V->np + j] = I->X[(size_t)j * I->W + w];
    V->dsurv = UINT32_MAX;
    V->slice = 1;
}

static void vacc_init(vacc_t *A) {
    memset(A, 0, sizeof *A);
    A->bestd = UINT32_MAX;
    A->best_key = UINT64_MAX;
}
static void vacc_merge(vacc_t *G, const vacc_t *A) {
    G->subsets += A->subsets; G->sd += A->sd; G->sd2 += A->sd2;
    if (A->bestd < G->bestd || (A->bestd == G->bestd && A->best_key < G->best_key)) {
        uint64_t nb = A->bestd == G->bestd ? G->nbest + A->nbest : A->nbest;
        G->bestd = A->bestd; G->best_key = A->best_key; memcpy(G->arg, A->arg, sizeof A->arg);
        G->nbest = nb;
    } else if (A->bestd == G->bestd) {
        G->nbest += A->nbest;
    }
    if (A->nsurv) {
        G->surv = (uint64_t *)realloc(G->surv, (G->nsurv + A->nsurv) * 8);
        memcpy(G->surv + G->nsurv, A->surv, A->nsurv * 8);
        G->nsurv += A->nsurv;
    }
}

// the whole scan (or every slice-th task), `threads` OpenMP threads. Tasks: k = 2, groups of NBLK first elements;
// k = 3, the first element; k >= 4, the pair of first elements (as spbits, so slice= samples the same tasks).
static vacc_t vscan(const vctx_t *V, int threads) {
    const sp_inst_t *I = V->I;
    const int n = V->n, k = V->k, Wm = V->Wm;
    vacc_t G;
    vacc_init(&G);
    int ntask = 0, *t1 = NULL, *t2 = NULL;
    if (k == 2) {
        ntask = (n - 1 + NBLK - 1) / NBLK;
    } else if (k == 3) {
        ntask = n - 2;
    } else {
        t1 = (int *)malloc(sizeof(int) * (size_t)n * n);
        t2 = (int *)malloc(sizeof(int) * (size_t)n * n);
        for (int a = 0; a <= n - k; a++)
            for (int b = a + 1; b <= n - (k - 1); b++) { t1[ntask] = a; t2[ntask] = b; ntask++; }
    }
#ifdef _OPENMP
    if (threads > 0) omp_set_num_threads(threads);
#endif
#pragma omp parallel
    {
        vacc_t A;
        vacc_init(&A);
        uint64_t *buf = (uint64_t *)sp_alloc(sizeof(uint64_t) * (size_t)SP_KMAX * Wm);
        uint64_t *gbuf = (uint64_t *)sp_alloc(sizeof(uint64_t) * (size_t)NBLK * Wm);
        int pre[SP_KMAX + 2];
#pragma omp for schedule(dynamic, 8)
        for (int t = 0; t < ntask; t++) {
            if (V->slice > 1 && t % V->slice) continue;
            if (k == 2) {
                int cend = NBLK * t + NBLK - 1 < n - 2 ? NBLK * t + NBLK - 1 : n - 2;
                vgroups(V, &A, I->y, pre, 0, NBLK * t, cend, gbuf);
            } else if (k == 3) {
                pre[0] = t;
                const uint64_t *x1 = I->X + (size_t)t * I->W;
                for (int w = 0; w < Wm; w++) buf[w] = I->y[w] ^ x1[w];
                vgroups(V, &A, buf, pre, 1, t + 1, n - 2, gbuf);
            } else {
                pre[0] = t1[t];
                pre[1] = t2[t];
                const uint64_t *x1 = I->X + (size_t)t1[t] * I->W, *x2 = I->X + (size_t)t2[t] * I->W;
                for (int w = 0; w < Wm; w++) buf[Wm + w] = I->y[w] ^ x1[w] ^ x2[w];
                vrec(V, &A, buf, gbuf, pre, 2);
            }
        }
        free(buf);
        free(gbuf);
#pragma omp critical
        vacc_merge(&G, &A);
        free(A.surv);
    }
    free(t1); free(t2);
    return G;
}

static int cmp_d(const void *a, const void *b) {
    double x = *(const double *)a, y = *(const double *)b;
    return x < y ? -1 : x > y;
}

static int cmd_vexh(void) {
    int n = argl("n", 0), k = argl("k", 0), m = argl("m", 0);
    double eta = argd("eta", "0");
    uint64_t seed = (uint64_t)argl("seed", "1");
    int threads = argl("threads", "1"), slice = argl("slice", "1"), reps = argl("reps", "1");
    int sums = argl("sums", "0");
    int tau = argl("tau", "0"), m2 = argl("m2", "0");
    if (k < 2 || k > SP_KMAX) { fprintf(stderr, "2 <= k <= %d\n", SP_KMAX); return 2; }
    sp_inst_t I;
    sp_geom_t G;
    if (sp_gen(&I, n, k, eta, m, seed, 1) || sp_geom_init(&G, n, k, m)) { fprintf(stderr, "bad instance\n"); return 2; }
    vctx_t V;
    vctx_init(&V, &I, &G);
    V.sums = sums;
    V.slice = slice;
    if (tau > 0) V.dsurv = (uint32_t)((m - tau) / 2);   // c >= tau  <=>  d <= (m - tau) / 2
    double *wall = (double *)malloc(sizeof(double) * (reps > 0 ? reps : 1));
    vacc_t A;
    for (int r = 0; r < reps; r++) {
        double t0 = now();
        A = vscan(&V, threads);
        wall[r] = now() - t0;
        if (r + 1 < reps) free(A.surv);
    }
    qsort(wall, reps, sizeof(double), cmp_d);
    const double wmin = wall[0], wmed = wall[reps / 2], wmax = wall[reps - 1];
    int ok = A.nbest == 1;
    for (int i = 0; i < k; i++) ok = ok && A.arg[i] == I.secret[i];
    const int best_c = m - 2 * (int)A.bestd;
    printf("{\"cmd\":\"vexh\",\"n\":%d,\"k\":%d,\"eta\":%g,\"m\":%d,\"seed\":%" PRIu64 ",\"threads\":%d,"
           "\"omp_threads\":%d,\"slice\":%d,\"reps\":%d,\"Wm\":%d,\"secret\":",
           n, k, eta, m, seed, threads, threads_now(), slice, reps, I.Wm);
    print_set(I.secret, k);
    printf(",\"found\":");
    print_set(A.arg, k);
    printf(",\"ok\":%d,\"best_c\":%d,\"nbest\":%" PRIu64 ",\"subsets\":%" PRIu64 ",\"Ncand\":%" PRIu64
           ",\"fraction\":%.6g,\"wall_s\":%.6f,\"wall_med_s\":%.6f,\"wall_max_s\":%.6f,\"ns_per_subset\":%.5f,"
           "\"subset_samples_per_s\":%.4g",
           ok, best_c, A.nbest, A.subsets, G.Ncand, (double)A.subsets / (double)G.Ncand, wmin, wmed, wmax,
           1e9 * wmin / (double)A.subsets, (double)A.subsets * m / wmin);
    int rc = 0;
    if (sums) {   // sum c = N m - 2 sum d; sum c^2 = N m^2 - 4 m sum d + 4 sum d^2 (mod 2^64)
        uint64_t N = A.subsets;
        int64_t sc = (int64_t)(N * (uint64_t)m - 2 * A.sd);
        uint64_t sc2 = N * (uint64_t)m * (uint64_t)m - 4 * (uint64_t)m * A.sd + 4 * A.sd2;
        int64_t cf1; uint64_t cf2; int fits;
        sp_closed_forms(&I, &cf1, &cf2, &fits);
        int applies = slice == 1 && N == G.Ncand, match = applies && sc == cf1 && sc2 == cf2;
        printf(",\"sum_c\":%" PRId64 ",\"sum_c2\":%" PRIu64 ",\"closed\":{\"sum_c\":%" PRId64 ",\"sum_c2\":%" PRIu64
               ",\"applies\":%d,\"match\":%d}", sc, sc2, cf1, cf2, applies, match);
        if (applies && !match) rc = 1;
    }
    if (tau > 0) {   // two-stage: stage 2 rescoring of the survivors on all m2 samples
        int secret_kept = 0;
        uint64_t skey = 0;
        for (int i = 0; i < k; i++) skey |= (uint64_t)I.secret[i] << (12 * i);
        for (size_t i = 0; i < A.nsurv; i++) secret_kept |= A.surv[i] == skey;
        printf(",\"tau\":%d,\"survivors\":%zu,\"secret_survived\":%d", tau, A.nsurv, secret_kept);
        if (m2 > 0) {
            sp_inst_t I2;
            sp_gen(&I2, n, k, eta, m2, seed, 1);
            double t0 = now();
            uint32_t bestd = UINT32_MAX;
            uint64_t bestkey = UINT64_MAX;
            size_t besti = 0;
#ifdef _OPENMP
            if (threads > 0) omp_set_num_threads(threads);
#endif
#pragma omp parallel
            {
                uint32_t bd = UINT32_MAX;
                uint64_t bk = UINT64_MAX;
                size_t bi = 0;
#pragma omp for schedule(static)
                for (size_t i = 0; i < A.nsurv; i++) {
                    int T[SP_KMAX];
                    for (int q = 0; q < k; q++) T[q] = (int)((A.surv[i] >> (12 * q)) & 0xFFF);
                    uint32_t d = 0;
                    for (int w = 0; w < I2.Wm; w++) {
                        uint64_t v = I2.y[w];
                        for (int q = 0; q < k; q++) v ^= I2.X[(size_t)T[q] * I2.W + w];
                        d += (uint32_t)__builtin_popcountll(v);
                    }
                    uint64_t key = colex_key(&G, T, k);
                    if (d < bd || (d == bd && key < bk)) { bd = d; bk = key; bi = i; }
                }
#pragma omp critical
                if (bd < bestd || (bd == bestd && bk < bestkey)) { bestd = bd; bestkey = bk; besti = bi; }
            }
            double t1 = now();
            int T[SP_KMAX] = {0};
            if (A.nsurv)
                for (int q = 0; q < k; q++) T[q] = (int)((A.surv[besti] >> (12 * q)) & 0xFFF);
            int ok2 = A.nsurv > 0;
            for (int q = 0; q < k; q++) ok2 = ok2 && T[q] == I.secret[q];
            printf(",\"m2\":%d,\"stage2_s\":%.6f,\"stage2_found\":", m2, t1 - t0);
            print_set(T, k);
            printf(",\"stage2_best_c\":%d,\"stage2_ok\":%d", A.nsurv ? m2 - 2 * (int)bestd : 0, ok2);
            sp_free(&I2);
        }
    }
    printf("}\n");
    free(A.surv); free(wall); free(V.Xw);
    sp_free(&I);
    sp_geom_free(&G);
    return rc;
}

// ================================================================ mitm (bucketed meet in the middle)
static double lbinom(int n, int k) { return lgamma(n + 1.0) - lgamma(k + 1.0) - lgamma(n - k + 1.0); }

// largest d with N * P(Bin(m, 1/2) <= d) <= fa (-1 if none): accepting d <= this is a false accept w.p. <= fa
static int accept_threshold(double lnN, int m, double fa) {
    double cdf = 0;
    int d = -1;
    for (int i = 0; i <= m; i++) {
        cdf += exp(lbinom(m, i) - m * log(2.0));
        if (lnN + log(cdf) > log(fa)) break;
        d = i;
    }
    return d;
}
// P(no noisy label among r sampled without replacement) = C(m-t, r) / C(m, r)
static double q_clean(int m, double t, int r) {
    double lq = 0;
    for (int i = 0; i < r; i++) {
        double num = m - t - i;
        if (num <= 0) return 0;
        lq += log(num / (m - i));
    }
    return exp(lq);
}
// modelled seconds of one repetition on one core (per thread at 6 threads), calibrated on aifoundry3's i7-11700K:
// the table and probe terms from the r sweep of 29 September (L2, whole tables), the verification term refitted on
// the split tables (review R2's r sweeps at L1 and L2: about 12.5 ns + 0.46 ns per k x Wm word per verification)
static double rep_cost(double NA, double NB, int r, int k, int Wm, int n) {
    double bm_bytes = ldexp(1.0, r) / 8;
    double cB = bm_bytes <= 256e3 ? 4e-9 : bm_bytes <= 8e6 ? 8e-9 : 15e-9;
    double hits = NB * fmin(1.0, NA / ldexp(1.0, r));      // probes that find their bitmap bit set
    double cV = 12.5e-9 + 0.46e-9 * k * Wm;
    return 12e-9 * NA + cB * NB + 20e-9 * hits + cV * NA * NB / ldexp(1.0, r) + 1e-9 * n * r;
}

typedef struct {
    uint32_t bestd;
    uint64_t best_key;
    int T[SP_KMAX];
    long reps, verifies, found_rep;
} macc_t;

static inline uint64_t pack_set(const int *s, int c) {
    uint64_t e = 0;
    for (int i = 0; i < c; i++) e |= (uint64_t)s[i] << (12 * i);
    return e;
}

typedef struct {
    const sp_inst_t *I;
    const sp_geom_t *G;
    int n, k, a, b, m, Wm, r, rb;
    uint32_t dacc;
    int early;
    int split;         // a random halving of the features per repetition: A from half 0, B from half 1
} mctx_t;

// verify the candidate A-subset (packed) + B-subset u[0..b-1]
static inline void mverify(const mctx_t *M, macc_t *R, uint64_t sa, const int *u, long rep) {
    int T[SP_KMAX], c = 0;
    for (int i = 0; i < M->a; i++) T[c++] = (int)((sa >> (12 * i)) & 0xFFF);
    for (int i = 0; i < M->b; i++) {
        for (int q = 0; q < M->a; q++)
            if (T[q] == u[i]) return;   // not disjoint
        T[c++] = u[i];
    }
    for (int i = 1; i < c; i++)
        for (int q = i; q > 0 && T[q - 1] > T[q]; q--) { int t = T[q]; T[q] = T[q - 1]; T[q - 1] = t; }
    R->verifies++;
    const sp_inst_t *I = M->I;
    uint32_t d = 0;
    for (int w = 0; w < M->Wm; w++) {
        uint64_t v = I->y[w];
        for (int q = 0; q < c; q++) v ^= I->X[(size_t)T[q] * I->W + w];
        d += (uint32_t)__builtin_popcountll(v);
    }
    if (d <= R->bestd) {
        uint64_t key = colex_key(M->G, T, c);
        if (d < R->bestd || key < R->best_key) {
            R->bestd = d; R->best_key = key; memcpy(R->T, T, sizeof T); R->found_rep = rep;
        }
    }
}

typedef struct {
    uint32_t *keyA, *cnt, *ek, *h;
    uint64_t *subA, *es, *bm;
    int *pos, *ia, *ib;    // ia / ib: the features the A and B sides draw from this repetition
} mws_t;

static void mrep(const mctx_t *M, mws_t *S, macc_t *R, long rep) {
    const sp_inst_t *I = M->I;
    const int n = M->n, m = M->m, r = M->r, W = I->W;
    // r distinct sample positions (partial Fisher-Yates; deterministic in (seed, rep))
    uint64_t rs = sp_rnd(I->seed, 4, (uint64_t)rep);
    for (int i = 0; i < m; i++) S->pos[i] = i;
    for (int i = 0; i < r; i++) {
        rs = sp_mix64(rs + 0x9E3779B97F4A7C15ULL);
        int jx = i + (int)(rs % (uint64_t)(m - i));
        int t = S->pos[i]; S->pos[i] = S->pos[jx]; S->pos[jx] = t;
    }
    uint32_t hy = 0;
    for (int t = 0; t < r; t++) hy |= (uint32_t)sp_bit(I->y, S->pos[t]) << t;
    for (int j = 0; j < n; j++) {
        uint32_t v = 0;
        const uint64_t *xj = I->X + (size_t)j * W;
        for (int t = 0; t < r; t++) v |= (uint32_t)sp_bit(xj, S->pos[t]) << t;
        S->h[j] = v;
    }
    // the features each side draws from: all of them, or the two halves of a random halving (deterministic in
    // (seed, rep))
    int na = 0, nb = 0;
    for (int j = 0; j < n; j++) {
        if (!M->split) { S->ia[na++] = j; S->ib[nb++] = j; continue; }
        if (sp_rnd(I->seed, 5, ((uint64_t)rep << 13) | (uint64_t)j) & 1) S->ib[nb++] = j;
        else S->ia[na++] = j;
    }
    const int *ia = S->ia, *ib = S->ib;
    // bucket the A side: key = hy ^ h(A); buckets on the low rb bits; a bitmap on all r bits
    const uint32_t mrb = (1u << M->rb) - 1;
    size_t q = 0;
    int s3[3];
    if (M->a == 1) {
        for (int x1 = 0; x1 < na; x1++) {
            const int i1 = ia[x1];
            S->keyA[q] = hy ^ S->h[i1]; s3[0] = i1; S->subA[q++] = pack_set(s3, 1);
        }
    } else if (M->a == 2) {
        for (int x1 = 0; x1 < na; x1++)
            for (int x2 = x1 + 1; x2 < na; x2++) {
                const int i1 = ia[x1], i2 = ia[x2];
                S->keyA[q] = hy ^ S->h[i1] ^ S->h[i2]; s3[0] = i1; s3[1] = i2; S->subA[q++] = pack_set(s3, 2);
            }
    } else {
        for (int x1 = 0; x1 < na; x1++)
            for (int x2 = x1 + 1; x2 < na; x2++)
                for (int x3 = x2 + 1; x3 < na; x3++) {
                    const int i1 = ia[x1], i2 = ia[x2], i3 = ia[x3];
                    S->keyA[q] = hy ^ S->h[i1] ^ S->h[i2] ^ S->h[i3];
                    s3[0] = i1; s3[1] = i2; s3[2] = i3; S->subA[q++] = pack_set(s3, 3);
                }
    }
    const size_t NA = q;
    memset(S->cnt, 0, sizeof(uint32_t) * ((size_t)mrb + 2));
    for (size_t z = 0; z < NA; z++) {
        uint32_t key = S->keyA[z];
        S->cnt[(key & mrb) + 1]++;
        S->bm[key >> 6] |= 1ULL << (key & 63);
    }
    for (size_t bk = 0; bk <= mrb; bk++) S->cnt[bk + 1] += S->cnt[bk];
    for (size_t z = 0; z < NA; z++) {
        uint32_t key = S->keyA[z], p = S->cnt[key & mrb]++;
        S->ek[p] = key; S->es[p] = S->subA[z];
    }
    // after the fill, bucket bk spans [bk ? cnt[bk-1] : 0, cnt[bk])
#define MPROBE(KEY, U)                                                                   \
    do {                                                                                 \
        uint32_t key_ = (KEY);                                                           \
        if (S->bm[key_ >> 6] >> (key_ & 63) & 1) {                                       \
            uint32_t bk_ = key_ & mrb;                                                   \
            uint32_t s_ = bk_ ? S->cnt[bk_ - 1] : 0, e_ = S->cnt[bk_];                    \
            for (uint32_t z_ = s_; z_ < e_; z_++)                                        \
                if (S->ek[z_] == key_) mverify(M, R, S->es[z_], (U), rep);               \
        }                                                                                \
    } while (0)
    int u[3];
    if (M->b == 1) {
        for (int y1 = 0; y1 < nb; y1++) { u[0] = ib[y1]; MPROBE(S->h[u[0]], u); }
    } else if (M->b == 2) {
        for (int y1 = 0; y1 < nb; y1++)
            for (int y2 = y1 + 1; y2 < nb; y2++) { u[0] = ib[y1]; u[1] = ib[y2]; MPROBE(S->h[u[0]] ^ S->h[u[1]], u); }
    } else {
        for (int y1 = 0; y1 < nb; y1++)
            for (int y2 = y1 + 1; y2 < nb; y2++) {
                u[0] = ib[y1]; u[1] = ib[y2];
                uint32_t h12 = S->h[u[0]] ^ S->h[u[1]];
                for (int y3 = y2 + 1; y3 < nb; y3++) { u[2] = ib[y3]; MPROBE(h12 ^ S->h[u[2]], u); }
            }
    }
#undef MPROBE
    for (size_t z = 0; z < NA; z++) S->bm[S->keyA[z] >> 6] = 0;   // clear only the touched bitmap words
    R->reps++;
}

static int cmd_mitm(void) {
    int n = argl("n", 0), k = argl("k", 0), m = argl("m", 0);
    double eta = argd("eta", "0");
    uint64_t seed = (uint64_t)argl("seed", "1");
    int threads = argl("threads", "1"), r = argl("r", "0"), early = argl("early", "1");
    double maxsec = argd("maxsec", "600"), fa = argd("fa", "1e-3"), delta = argd("delta", "1e-3");
    long maxreps = argl("maxreps", "0");
    if (k < 2 || k > 6) { fprintf(stderr, "2 <= k <= 6\n"); return 2; }
    sp_inst_t I;
    sp_geom_t G;
    if (sp_gen(&I, n, k, eta, m, seed, 1) || sp_geom_init(&G, n, k, m)) { fprintf(stderr, "bad instance\n"); return 2; }
    mctx_t M;
    memset(&M, 0, sizeof M);
    M.I = &I; M.G = &G; M.n = n; M.k = k; M.a = k / 2; M.b = k - M.a; M.m = m; M.Wm = I.Wm; M.early = early;
    M.split = (int)argl("split", k >= 4 ? "1" : "0");
    // table sizes (expected, with the halving) and the chance that the halving splits the secret a | b
    const double NA = M.split ? exp(lbinom(n / 2, M.a)) : (double)sp_C(&G, n, M.a);
    const double NB = M.split ? exp(lbinom(n - n / 2, M.b)) : (double)sp_C(&G, n, M.b);
    const double psplit = M.split ? exp(lbinom(k, M.a)) / ldexp(1.0, k) : 1.0;
    const int dacc = accept_threshold(log((double)G.Ncand), m, fa);
    M.dacc = (uint32_t)(dacc < 0 ? 0 : dacc);
    const double texp = eta * m;
    const int rauto = r <= 0;
    if (rauto) {   // minimise E[time] = rep_cost / q(r)
        double bestT = 1e300;
        for (int rr = 4; rr <= 28 && rr < m; rr++) {
            double qq = psplit * q_clean(m, texp, rr);
            if (qq <= 0) break;
            double T = rep_cost(NA, NB, rr, k, I.Wm, n) / qq;
            if (T < bestT) { bestT = T; r = rr; }
        }
    }
    if (r > 30 || r >= m) { fprintf(stderr, "r must be < min(31, m)\n"); return 2; }
    M.r = r;
    // buckets on the low rb bits, about 4 A entries each, so the bucket counts stay in L2
    int rb = (int)ceil(log2(NA > 1 ? NA : 2)) - 2;
    M.rb = rb < 8 ? (r < 8 ? r : 8) : (rb > r ? r : rb);
    const int tnoise = sp_popcount_words(I.noise, I.Wm);
    const double qm = psplit * q_clean(m, texp, r), qa = psplit * q_clean(m, tnoise, r);
    const long cap = maxreps > 0 ? maxreps : (long)ceil(log(1.0 / delta) / qm);
    macc_t best;
    memset(&best, 0, sizeof best);
    best.bestd = UINT32_MAX; best.best_key = UINT64_MAX; best.found_rep = -1;
    long next = 0;
    int done = 0, stop_time = 0;
    double t0 = now();
#ifdef _OPENMP
    if (threads > 0) omp_set_num_threads(threads);
#endif
#pragma omp parallel
    {
        mws_t S;
        const size_t NAmax = (size_t)sp_C(&G, n, M.a);   // a halving can be uneven: room for every a-subset
        S.keyA = (uint32_t *)malloc(sizeof(uint32_t) * NAmax);
        S.subA = (uint64_t *)malloc(sizeof(uint64_t) * NAmax);
        S.ek = (uint32_t *)malloc(sizeof(uint32_t) * NAmax);
        S.es = (uint64_t *)malloc(sizeof(uint64_t) * NAmax);
        S.ia = (int *)malloc(sizeof(int) * n);
        S.ib = (int *)malloc(sizeof(int) * n);
        S.cnt = (uint32_t *)malloc(sizeof(uint32_t) * (((size_t)1 << M.rb) + 2));
        S.bm = (uint64_t *)sp_alloc((((size_t)1 << r) / 64 + 8) * 8);
        S.h = (uint32_t *)malloc(sizeof(uint32_t) * n);
        S.pos = (int *)malloc(sizeof(int) * m);
        macc_t R;
        memset(&R, 0, sizeof R);
        R.bestd = UINT32_MAX; R.best_key = UINT64_MAX; R.found_rep = -1;
        for (;;) {
            long rep;
            int stop;
#pragma omp atomic read
            stop = done;
            if (stop) break;
#pragma omp atomic capture
            rep = next++;
            if (rep >= cap) break;
            mrep(&M, &S, &R, rep);
            if (early && R.bestd <= M.dacc) {
#pragma omp atomic write
                done = 1;
            }
            if (now() - t0 > maxsec) {
#pragma omp atomic write
                done = 1;
#pragma omp atomic write
                stop_time = 1;
            }
        }
#pragma omp critical
        {
            best.reps += R.reps; best.verifies += R.verifies;
            if (R.bestd < best.bestd || (R.bestd == best.bestd && R.best_key < best.best_key)) {
                best.bestd = R.bestd; best.best_key = R.best_key; memcpy(best.T, R.T, sizeof R.T);
                best.found_rep = R.found_rep;
            }
        }
        free(S.keyA); free(S.subA); free(S.ek); free(S.es); free(S.cnt); free(S.bm); free(S.h); free(S.pos);
        free(S.ia); free(S.ib);
    }
    double t1 = now();
    int ok = best.bestd != UINT32_MAX;
    for (int i = 0; i < k; i++) ok = ok && best.T[i] == I.secret[i];
    // this seed's expected solve time at this thread count: 1/q repetitions if the secret can clear the acceptance
    // threshold (it has tnoise disagreements), else the run goes to the cap (review R2, finding 4)
    const double wall_per_rep = best.reps ? (t1 - t0) / (double)best.reps : 0.0;
    const int can_accept = tnoise <= dacc;
    const double exp_full = can_accept ? (qa > 0 ? wall_per_rep / qa : 0.0) : wall_per_rep * (double)cap;
    printf("{\"cmd\":\"mitm\",\"n\":%d,\"k\":%d,\"eta\":%g,\"m\":%d,\"seed\":%" PRIu64 ",\"threads\":%d,"
           "\"omp_threads\":%d,\"a\":%d,\"b\":%d,\"r\":%d,\"r_auto\":%d,\"rb\":%d,\"split\":%d,\"psplit\":%.4g,"
           "\"early\":%d,\"can_accept\":%d,\"expected_s_full\":%.4g,\"secret\":",
           n, k, eta, m, seed, threads, threads_now(), M.a, M.b, r, rauto, M.rb, M.split, psplit, early, can_accept,
           exp_full);
    print_set(I.secret, k);
    printf(",\"found\":");
    print_set(best.T, k);
    printf(",\"ok\":%d,\"best_c\":%d,\"accepted\":%d,\"dacc\":%d,\"tau_acc\":%d,\"noise\":%d,\"reps\":%ld,"
           "\"found_rep\":%ld,\"cap\":%ld,\"hit_maxsec\":%d,\"q_model\":%.4g,\"q_actual\":%.4g,"
           "\"expected_reps_actual\":%.4g,\"verifies\":%ld,\"wall_s\":%.4f,\"s_per_rep\":%.6g,"
           "\"expected_s_actual\":%.4g}\n",
           ok, best.bestd == UINT32_MAX ? 0 : m - 2 * (int)best.bestd, best.bestd <= M.dacc, dacc, m - 2 * dacc,
           tnoise, best.reps, best.found_rep, cap, stop_time, qm, qa, qa > 0 ? 1.0 / qa : 0.0, best.verifies, t1 - t0,
           best.reps ? (t1 - t0) * threads_now() / (double)best.reps : 0.0,
           best.reps && qa > 0 ? (t1 - t0) / (double)best.reps / qa : 0.0);
    sp_free(&I);
    sp_geom_free(&G);
    return 0;
}

// ================================================================ batch (B1)
// lanes=1: 8 instances per 512-bit register (lane l of group g = instance 8g + l), m <= 64 so an instance's column
// is one 64-bit word. Exhaustive over the k-subsets in lexicographic order with the prefix XORs shared by the 8
// lanes; a lane's best moves only on the rare path (popcount <= its running best). Solved = a unique best (no tie)
// equal to the secret, as lanes=0 (vexh per instance) and the reference count it.
typedef struct {
    const __m512i *X;      // n vectors of the group
    int n, k;
    __m512i best;          // per-lane running best d
    uint64_t bestl[8], nbest[8];
    int arg[8][SP_KMAX];
    int pre[SP_KMAX];
} bgrp_t;

static void blevel(bgrp_t *B, int depth, int start, __m512i P) {
    const int n = B->n, k = B->k;
    if (depth == k - 1) {                     // the last element: the hot loop
        for (int d = start; d < n; d++) {
            const __m512i pc = _mm512_popcnt_epi64(_mm512_xor_si512(P, B->X[d]));
            const __mmask8 le = _mm512_cmple_epu64_mask(pc, B->best);
            if (__builtin_expect(le != 0, 0)) {
                uint64_t v[8];
                _mm512_storeu_si512((void *)v, pc);
                for (int l = 0; l < 8; l++) {
                    if (!(le >> l & 1)) continue;
                    if (v[l] < B->bestl[l]) {
                        B->bestl[l] = v[l]; B->nbest[l] = 1;
                        for (int q = 0; q < k - 1; q++) B->arg[l][q] = B->pre[q];
                        B->arg[l][k - 1] = d;
                    } else {
                        B->nbest[l]++;
                    }
                }
                B->best = _mm512_loadu_si512((const void *)B->bestl);
            }
        }
        return;
    }
    for (int a = start; a <= n - (k - depth); a++) {
        B->pre[depth] = a;
        blevel(B, depth + 1, a + 1, _mm512_xor_si512(P, B->X[a]));
    }
}

static int cmd_batch(void) {
    int n = argl("n", "64"), k = argl("k", "4"), m = argl("m", "64"), count = argl("count", "1024");
    double eta = argd("eta", "0.1");
    uint64_t seed = (uint64_t)argl("seed", "1");
    int threads = argl("threads", "1"), reps = argl("reps", "1"), lanes = argl("lanes", m <= 64 ? "1" : "0");
    if (lanes && m > 64) { fprintf(stderr, "lanes=1 needs m <= 64\n"); return 2; }
    if (k < 2 || k > SP_KMAX) { fprintf(stderr, "2 <= k <= %d\n", SP_KMAX); return 2; }
    sp_inst_t *I = (sp_inst_t *)calloc(count, sizeof(sp_inst_t));
    vctx_t *V = (vctx_t *)calloc(count, sizeof(vctx_t));
    sp_geom_t G;
    sp_geom_init(&G, n, k, m);
    for (int i = 0; i < count; i++) {
        if (sp_gen(&I[i], n, k, eta, m, seed + (uint64_t)i, 1)) { fprintf(stderr, "bad instance\n"); return 2; }
        if (!lanes) vctx_init(&V[i], &I[i], &G);
    }
    const int ng = (count + 7) / 8;
    __m512i *X = NULL, *Y = NULL;
    if (lanes) {   // lane l of X[g * n + j] = feature j of instance 8g + l (zero for padding lanes)
        X = (__m512i *)sp_alloc(sizeof(__m512i) * (size_t)ng * n);
        Y = (__m512i *)sp_alloc(sizeof(__m512i) * (size_t)ng);
        for (int i = 0; i < count; i++) {
            const int g = i / 8, l = i % 8;
            for (int j = 0; j < n; j++) ((uint64_t *)&X[(size_t)g * n + j])[l] = I[i].X[(size_t)j * I[i].W];
            ((uint64_t *)&Y[g])[l] = I[i].y[0];
        }
    }
    int *okv = (int *)calloc(count, sizeof(int));
    double *wall = (double *)malloc(sizeof(double) * (reps > 0 ? reps : 1));
#ifdef _OPENMP
    if (threads > 0) omp_set_num_threads(threads);
#endif
    for (int rr = 0; rr < reps; rr++) {
        double t0 = now();
        if (lanes) {
#pragma omp parallel for schedule(dynamic, 1)
            for (int g = 0; g < ng; g++) {
                bgrp_t B;
                memset(&B, 0, sizeof B);
                B.X = X + (size_t)g * n; B.n = n; B.k = k;
                for (int l = 0; l < 8; l++) { B.bestl[l] = (uint64_t)m + 1; B.nbest[l] = 0; }
                B.best = _mm512_set1_epi64((long long)m + 1);
                blevel(&B, 0, 0, Y[g]);
                for (int l = 0; l < 8; l++) {
                    const int i = 8 * g + l;
                    if (i >= count) continue;
                    int ok = B.nbest[l] == 1;
                    for (int q = 0; q < k; q++) ok = ok && B.arg[l][q] == I[i].secret[q];
                    okv[i] = ok;
                }
            }
        } else {
#pragma omp parallel for schedule(dynamic, 4)
            for (int i = 0; i < count; i++) {
                vacc_t A = vscan(&V[i], 1);
                int ok = A.nbest == 1;
                for (int q = 0; q < k; q++) ok = ok && A.arg[q] == I[i].secret[q];
                okv[i] = ok;
            }
        }
        wall[rr] = now() - t0;
    }
    qsort(wall, reps, sizeof(double), cmp_d);
    int solved = 0;
    for (int i = 0; i < count; i++) solved += okv[i];
    printf("{\"cmd\":\"batch\",\"n\":%d,\"k\":%d,\"eta\":%g,\"m\":%d,\"seed0\":%" PRIu64 ",\"count\":%d,\"threads\":%d,"
           "\"lanes\":%d,\"reps\":%d,\"solved\":%d,\"wall_s\":%.6f,\"wall_med_s\":%.6f,\"wall_max_s\":%.6f,"
           "\"per_instance_s\":%.4g,\"Ncand\":%" PRIu64 "}\n",
           n, k, eta, m, seed, count, threads, lanes, reps, solved, wall[0], wall[reps / 2], wall[reps - 1],
           wall[0] / count, G.Ncand);
    for (int i = 0; i < count; i++) { free(V[i].Xw); sp_free(&I[i]); }
    free(I); free(V); free(okv); free(wall); free(X); free(Y);
    sp_geom_free(&G);
    return 0;
}

int main(int argc, char **argv) {
    g_argc = argc; g_argv = argv;
    if (argc < 2) { fprintf(stderr, "usage: spbase vexh|mitm|batch key=value ...\n"); return 2; }
    if (!strcmp(argv[1], "vexh")) return cmd_vexh();
    if (!strcmp(argv[1], "mitm")) return cmd_mitm();
    if (!strcmp(argv[1], "batch")) return cmd_batch();
    fprintf(stderr, "unknown subcommand %s\n", argv[1]);
    return 2;
}
