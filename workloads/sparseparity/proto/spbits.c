// spbits.c: bit-packed CPU prototypes for (noisy) sparse parity.
//
// A reference for the ET-SoC-1 port, not a card program: it runs on the host CPU only.
//
//   x ~ uniform {0,1}^n, y = XOR of x over a secret k-subset, each label flipped with probability eta.
//   Data are packed per feature: X[j] is an m-bit set over the samples (W = ceil(m/64) words), as is y.
//   The generator is counter-based (splitmix64 finaliser), so spgen.py produces the identical instance.
//
// Build:  gcc -O3 -march=native -fopenmp -o spbits spbits.c       (see Makefile)
//
// Subcommands (arguments are key=value):
//   gen     n k eta m seed                         secret + a hash of the packed data (cross-check with spgen.py)
//   exh     n k eta m seed [threads] [slice]       exhaustive scan of all C(n,k) subsets for the fewest
//                                                  disagreements with y (= the largest +-1 correlation);
//                                                  slice=S scans every S-th outer task only (timing sample)
//   msearch n k eta seed probes=m1,m2,... [threads] one scan over the largest probe; for every probe m_p reports
//                                                  whether the secret is the unique best subset on the first m_p
//                                                  samples (needs the secret, used only for evaluation)
//   ge      n k seed mmax                          noiseless GF(2) elimination, rows inserted one at a time:
//                                                  first m at which rank = n, then back-substitution
//   gers    n k eta m seed ncols extra maxtrials [maxsec]
//                                                  noisy labels: Gaussian elimination on random subsets of
//                                                  (ncols+extra) samples and, if ncols < n, ncols random features,
//                                                  until a weight-k solution verifies on all m samples
// Every subcommand prints one JSON object on stdout.

#define _GNU_SOURCE
#include <inttypes.h>
#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#ifdef _OPENMP
#include <omp.h>
#endif

#define KMAX 8
#define PMAX 64

// ---------------------------------------------------------------- RNG and generator (mirrors spgen.py)
static inline uint64_t mix64(uint64_t z) {
    z ^= z >> 30; z *= 0xbf58476d1ce4e5b9ULL;
    z ^= z >> 27; z *= 0x94d049bb133111ebULL;
    return z ^ (z >> 31);
}
// Stream s of instance seed; idx is the counter.
static inline uint64_t rnd(uint64_t seed, uint64_t stream, uint64_t idx) {
    uint64_t key = mix64(seed * 0x9E3779B97F4A7C15ULL + stream * 0xD1B54A32D192ED03ULL + 0x632BE59BD9B4E019ULL);
    return mix64(key + idx * 0x9E3779B97F4A7C15ULL);
}

typedef struct {
    int n, k, m, W;
    double eta;
    uint64_t seed;
    uint64_t *X;      // n * W, feature-major
    uint64_t *y;      // W
    uint64_t *noise;  // W (the flipped labels; kept for evaluation only)
    int secret[KMAX];
} inst_t;

static double now(void) {
    struct timespec t;
    clock_gettime(CLOCK_MONOTONIC, &t);
    return t.tv_sec + 1e-9 * t.tv_nsec;
}
static double cpu_now(void) {
    struct timespec t;
    clock_gettime(CLOCK_PROCESS_CPUTIME_ID, &t);
    return t.tv_sec + 1e-9 * t.tv_nsec;
}

// Words per packed column: ceil(m/64), padded with zero words to a multiple of 8 above 4 when the build
// has AVX-512 VPOPCNTQ (8 words per instruction; zero words add nothing to XOR + popcount).
static int padded_words(int m) {
    int W = (m + 63) / 64;
#ifdef __AVX512VPOPCNTDQ__
    if (W > 4) W = (W + 7) / 8 * 8;
#endif
    return W;
}

static void gen(inst_t *I, int n, int k, double eta, int m, uint64_t seed) {
    I->n = n; I->k = k; I->eta = eta; I->m = m; I->seed = seed;
    I->W = padded_words(m);
    int W = I->W, Wm = (m + 63) / 64;
    uint64_t last = (m % 64) ? ((1ULL << (m % 64)) - 1) : ~0ULL;
    I->X = aligned_alloc(64, ((size_t)n * W * 8 + 63) / 64 * 64);
    I->y = aligned_alloc(64, ((size_t)W * 8 + 63) / 64 * 64);
    I->noise = aligned_alloc(64, ((size_t)W * 8 + 63) / 64 * 64);
    for (int j = 0; j < n; j++)
        for (int w = 0; w < W; w++) {
            uint64_t v = w < Wm ? rnd(seed, 1, ((uint64_t)j << 32) | (uint64_t)w) : 0;
            I->X[(size_t)j * W + w] = (w == Wm - 1) ? (v & last) : v;
        }
    // secret: partial Fisher-Yates
    int idx[4096];
    for (int j = 0; j < n; j++) idx[j] = j;
    for (int i = 0; i < k; i++) {
        uint64_t r = rnd(seed, 3, i) % (uint64_t)(n - i);
        int t = idx[i]; idx[i] = idx[i + r]; idx[i + r] = t;
    }
    for (int i = 0; i < k; i++) I->secret[i] = idx[i];
    for (int i = 1; i < k; i++)  // sort
        for (int j = i; j > 0 && I->secret[j - 1] > I->secret[j]; j--) {
            int t = I->secret[j]; I->secret[j] = I->secret[j - 1]; I->secret[j - 1] = t;
        }
    uint64_t thr = (uint64_t)(eta * 9007199254740992.0);  // eta * 2^53
    for (int w = 0; w < W; w++) {
        uint64_t nz = 0;
        for (int b = 0; b < 64; b++) {
            uint64_t s = (uint64_t)w * 64 + b;
            if (s >= (uint64_t)m) break;
            if ((rnd(seed, 2, s) >> 11) < thr) nz |= 1ULL << b;
        }
        I->noise[w] = nz;
        uint64_t v = nz;
        for (int i = 0; i < k; i++) v ^= I->X[(size_t)I->secret[i] * W + w];
        I->y[w] = v;
    }
}

static uint64_t inst_hash(const inst_t *I) {  // over the unpadded words, as spgen does
    uint64_t h = 0x12345678ULL;
    int Wm = (I->m + 63) / 64;
    for (int j = 0; j < I->n; j++)
        for (int w = 0; w < Wm; w++) h = mix64(h ^ I->X[(size_t)j * I->W + w]);
    for (int w = 0; w < Wm; w++) h = mix64(h ^ I->y[w]);
    return h;
}

static int popcount_words(const uint64_t *a, int W) {
    int c = 0;
    for (int w = 0; w < W; w++) c += __builtin_popcountll(a[w]);
    return c;
}

// ---------------------------------------------------------------- argument parsing
static const char *argval(int argc, char **argv, const char *key, const char *def) {
    size_t L = strlen(key);
    for (int i = 2; i < argc; i++)
        if (!strncmp(argv[i], key, L) && argv[i][L] == '=') return argv[i] + L + 1;
    if (!def) { fprintf(stderr, "missing %s=\n", key); exit(2); }
    return def;
}
static long argl(int argc, char **argv, const char *key, const char *def) { return strtol(argval(argc, argv, key, def), 0, 0); }
static double argd(int argc, char **argv, const char *key, const char *def) { return strtod(argval(argc, argv, key, def), 0); }

static void print_secret(const int *s, int k) {
    printf("[");
    for (int i = 0; i < k; i++) printf("%s%d", i ? "," : "", s[i]);
    printf("]");
}

// ---------------------------------------------------------------- exhaustive scan
// Enumerate i1 < ... < ik with running prefix XORs P_d = y ^ X[i1] ^ ... ^ X[id]; the innermost level
// counts popcount(P_{k-1} ^ X[ik]) = disagreements of subset {i1..ik} with y.
typedef struct {
    uint32_t best;
    uint64_t nbest;       // subsets reaching best
    int arg[KMAX];
    uint64_t subsets;
    // msearch only
    int np;
    uint32_t minw[PMAX];  // min over wrong subsets of the count on the first probe[p] samples
} acc_t;

typedef struct {
    const inst_t *I;
    int slice;  // > 1: scan only outer tasks t with t % slice == 0 (a timing sample of a large scan)
    int np;
    int pword[PMAX];
    uint64_t pmask[PMAX];
} ctx_t;

static inline uint32_t xorpop(const uint64_t *restrict a, const uint64_t *restrict b, int W) {
    uint32_t c = 0;
    for (int w = 0; w < W; w++) c += __builtin_popcountll(a[w] ^ b[w]);
    return c;
}

static inline void note(acc_t *A, uint32_t c, const int *pre, int d, int j) {
    if (c < A->best) {
        A->best = c; A->nbest = 1;
        for (int i = 0; i < d; i++) A->arg[i] = pre[i];
        A->arg[d] = j;
    } else if (c == A->best) {
        A->nbest++;
    }
}

// innermost level: prefix P (depth d = k-1 indices in pre), last index from start to n-1
static void inner_exh(const ctx_t *C, acc_t *A, const uint64_t *P, const int *pre, int d, int start) {
    const inst_t *I = C->I;
    const int n = I->n, W = I->W;
    const uint64_t *X = I->X;
    A->subsets += (uint64_t)(n - start);
#define INNER_W(WC)                                                           \
    for (int j = start; j < n; j++) {                                        \
        const uint64_t *xj = X + (size_t)j * (WC);                           \
        uint32_t c = 0;                                                      \
        for (int w = 0; w < (WC); w++) c += __builtin_popcountll(P[w] ^ xj[w]); \
        if (__builtin_expect(c <= A->best, 0)) note(A, c, pre, d, j);        \
    }
    switch (W) {
    case 1: INNER_W(1); break;
    case 2: INNER_W(2); break;
    case 3: INNER_W(3); break;
    case 4: INNER_W(4); break;
    default:
        for (int j = start; j < n; j++) {
            uint32_t c = xorpop(P, X + (size_t)j * W, W);
            if (__builtin_expect(c <= A->best, 0)) note(A, c, pre, d, j);
        }
    }
#undef INNER_W
}

// msearch innermost: counts on every probe prefix, skipping the secret itself
static void inner_ms(const ctx_t *C, acc_t *A, const uint64_t *P, int start, int skip) {
    const inst_t *I = C->I;
    const int n = I->n, W = I->W, np = C->np;
    const uint64_t *X = I->X;
    A->subsets += (uint64_t)(n - start);
    for (int j = start; j < n; j++) {
        if (j == skip) continue;
        const uint64_t *xj = X + (size_t)j * W;
        uint32_t acc = 0;
        int p = 0;
        for (int w = 0; w < W && p < np; w++) {
            uint64_t v = P[w] ^ xj[w];
            while (p < np && C->pword[p] == w) {
                uint32_t c = acc + (uint32_t)__builtin_popcountll(v & C->pmask[p]);
                if (c < A->minw[p]) A->minw[p] = c;
                p++;
            }
            acc += (uint32_t)__builtin_popcountll(v);
        }
    }
}

// levels 3..k (prefix already has depth d >= 1)
static void rec(const ctx_t *C, acc_t *A, uint64_t *buf, int *pre, int d, int mode, int on_secret) {
    const inst_t *I = C->I;
    const int n = I->n, W = I->W, k = I->k;
    const uint64_t *P = buf + (size_t)(d - 1) * W;  // prefix XOR after d indices
    if (d == k - 1) {
        if (mode == 0) inner_exh(C, A, P, pre, d, pre[d - 1] + 1);
        else inner_ms(C, A, P, pre[d - 1] + 1, on_secret ? I->secret[k - 1] : -1);
        return;
    }
    uint64_t *Q = buf + (size_t)d * W;
    for (int j = pre[d - 1] + 1; j <= n - (k - d); j++) {
        const uint64_t *xj = I->X + (size_t)j * W;
        for (int w = 0; w < W; w++) Q[w] = P[w] ^ xj[w];
        pre[d] = j;
        rec(C, A, buf, pre, d + 1, mode, on_secret && j == I->secret[d]);
    }
}

// mode 0: exhaustive (min + argmin); mode 1: msearch (min over wrong subsets at every probe)
static acc_t scan(const ctx_t *C, int mode, int threads) {
    const inst_t *I = C->I;
    const int n = I->n, k = I->k, W = I->W;
    acc_t G;
    memset(&G, 0, sizeof G);
    G.best = UINT32_MAX;
    G.np = C->np;
    for (int p = 0; p < PMAX; p++) G.minw[p] = UINT32_MAX;
    if (k == 1) {  // trivial
        for (int j = 0; j < n; j++) {
            int pre[1] = {j};
            uint32_t c = xorpop(I->y, I->X + (size_t)j * W, W);
            G.subsets++;
            if (mode == 0) note(&G, c, pre, 0, j);
        }
        return G;
    }
    // tasks: first index (k == 2) or first two indices (k >= 3)
    int ntask;
    int *t1, *t2;
    if (k == 2) {
        ntask = n - 1;
        t1 = malloc(sizeof(int) * ntask); t2 = NULL;
        for (int i = 0; i < ntask; i++) t1[i] = i;
    } else {
        ntask = 0;
        t1 = malloc(sizeof(int) * (size_t)n * n); t2 = malloc(sizeof(int) * (size_t)n * n);
        for (int a = 0; a <= n - k; a++)
            for (int b = a + 1; b <= n - (k - 1); b++) { t1[ntask] = a; t2[ntask] = b; ntask++; }
    }
#ifdef _OPENMP
    if (threads > 0) omp_set_num_threads(threads);
#endif
#pragma omp parallel
    {
        acc_t A;
        memset(&A, 0, sizeof A);
        A.best = UINT32_MAX;
        A.np = C->np;
        for (int p = 0; p < PMAX; p++) A.minw[p] = UINT32_MAX;
        uint64_t *buf = aligned_alloc(64, ((size_t)KMAX * W * 8 + 63) / 64 * 64);
        int pre[KMAX];
#pragma omp for schedule(dynamic, 16)
        for (int t = 0; t < ntask; t++) {
            if (C->slice > 1 && t % C->slice) continue;
            const uint64_t *x1 = I->X + (size_t)t1[t] * W;
            pre[0] = t1[t];
            int on = (t1[t] == I->secret[0]);
            for (int w = 0; w < W; w++) buf[w] = I->y[w] ^ x1[w];
            if (k == 2) {
                if (mode == 0) inner_exh(C, &A, buf, pre, 1, t1[t] + 1);
                else inner_ms(C, &A, buf, t1[t] + 1, on ? I->secret[1] : -1);
            } else {
                const uint64_t *x2 = I->X + (size_t)t2[t] * W;
                pre[1] = t2[t];
                on = on && (t2[t] == I->secret[1]);
                for (int w = 0; w < W; w++) buf[W + w] = buf[w] ^ x2[w];
                rec(C, &A, buf, pre, 2, mode, on);
            }
        }
        free(buf);
#pragma omp critical
        {
            G.subsets += A.subsets;
            if (A.best < G.best) {
                G.best = A.best; G.nbest = A.nbest;
                memcpy(G.arg, A.arg, sizeof A.arg);
            } else if (A.best == G.best) {
                G.nbest += A.nbest;
            }
            for (int p = 0; p < C->np; p++)
                if (A.minw[p] < G.minw[p]) G.minw[p] = A.minw[p];
        }
    }
    free(t1); free(t2);
    return G;
}

static double binom(int n, int k) {
    double r = 1;
    for (int i = 0; i < k; i++) r = r * (n - i) / (i + 1);
    return r;
}

static int cmd_exh(int argc, char **argv) {
    inst_t I;
    int n = argl(argc, argv, "n", 0), k = argl(argc, argv, "k", 0), m = argl(argc, argv, "m", 0);
    double eta = argd(argc, argv, "eta", "0");
    uint64_t seed = argl(argc, argv, "seed", "1");
    int threads = argl(argc, argv, "threads", "1");
    if (k > KMAX || k < 1 || n > 4096 || k > n) { fprintf(stderr, "bad n/k\n"); return 2; }
    int slice = argl(argc, argv, "slice", "1");
    gen(&I, n, k, eta, m, seed);
    ctx_t C = {.I = &I, .slice = slice, .np = 0};
    double t0 = now(), c0 = cpu_now();
    acc_t G = scan(&C, 0, threads);
    double t1 = now(), c1 = cpu_now();
    int ok = G.nbest == 1;
    for (int i = 0; i < k; i++) ok = ok && G.arg[i] == I.secret[i];
    uint32_t tc = popcount_words(I.noise, I.W);
    printf("{\"cmd\":\"exh\",\"n\":%d,\"k\":%d,\"eta\":%g,\"m\":%d,\"W\":%d,\"seed\":%" PRIu64 ",\"threads\":%d,"
           "\"slice\":%d,\"secret\":", n, k, eta, m, I.W, seed, threads, slice);
    print_secret(I.secret, k);
    printf(",\"found\":");
    print_secret(G.arg, k);
    printf(",\"ok\":%d,\"best\":%u,\"nbest\":%" PRIu64 ",\"true_count\":%u,\"subsets\":%" PRIu64
           ",\"expected_subsets\":%.0f,\"word_ops\":%.0f,\"wall_s\":%.6f,\"cpu_s\":%.6f}\n",
           ok, G.best, G.nbest, tc, G.subsets, binom(n, k), (double)G.subsets * I.W, t1 - t0, c1 - c0);
    return 0;
}

static int cmp_int(const void *a, const void *b) { return *(const int *)a - *(const int *)b; }

static int cmd_msearch(int argc, char **argv) {
    inst_t I;
    int n = argl(argc, argv, "n", 0), k = argl(argc, argv, "k", 0);
    double eta = argd(argc, argv, "eta", "0");
    uint64_t seed = argl(argc, argv, "seed", "1");
    int threads = argl(argc, argv, "threads", "1");
    const char *ps = argval(argc, argv, "probes", 0);
    int probes[PMAX], np = 0;
    for (const char *s = ps; *s && np < PMAX;) {
        probes[np++] = strtol(s, (char **)&s, 10);
        if (*s == ',') s++;
    }
    qsort(probes, np, sizeof(int), cmp_int);
    int m = probes[np - 1];
    gen(&I, n, k, eta, m, seed);
    ctx_t C = {.I = &I, .np = np};
    for (int p = 0; p < np; p++) {
        C.pword[p] = (probes[p] - 1) / 64;
        C.pmask[p] = (probes[p] % 64) ? ((1ULL << (probes[p] % 64)) - 1) : ~0ULL;
    }
    double t0 = now(), c0 = cpu_now();
    acc_t G = scan(&C, 1, threads);
    double t1 = now(), c1 = cpu_now();
    printf("{\"cmd\":\"msearch\",\"n\":%d,\"k\":%d,\"eta\":%g,\"seed\":%" PRIu64 ",\"threads\":%d,\"W\":%d,"
           "\"subsets\":%" PRIu64 ",\"wall_s\":%.6f,\"cpu_s\":%.6f,\"probes\":[",
           n, k, eta, seed, threads, I.W, G.subsets, t1 - t0, c1 - c0);
    for (int p = 0; p < np; p++) printf("%s%d", p ? "," : "", probes[p]);
    printf("],\"true_count\":[");
    for (int p = 0; p < np; p++) {
        uint32_t c = 0;
        for (int w = 0; w <= C.pword[p]; w++)
            c += __builtin_popcountll(I.noise[w] & (w == C.pword[p] ? C.pmask[p] : ~0ULL));
        printf("%s%u", p ? "," : "", c);
    }
    printf("],\"min_wrong\":[");
    for (int p = 0; p < np; p++) printf("%s%u", p ? "," : "", G.minw[p]);
    printf("]}\n");
    return 0;
}

static int cmd_gen(int argc, char **argv) {
    inst_t I;
    int n = argl(argc, argv, "n", 0), k = argl(argc, argv, "k", 0), m = argl(argc, argv, "m", 0);
    double eta = argd(argc, argv, "eta", "0");
    uint64_t seed = argl(argc, argv, "seed", "1");
    gen(&I, n, k, eta, m, seed);
    printf("{\"cmd\":\"gen\",\"n\":%d,\"k\":%d,\"eta\":%g,\"m\":%d,\"seed\":%" PRIu64 ",\"secret\":", n, k, eta, m, seed);
    print_secret(I.secret, k);
    printf(",\"noisy\":%d,\"hash\":\"%016" PRIx64 "\"}\n", popcount_words(I.noise, I.W), inst_hash(&I));
    return 0;
}

// ---------------------------------------------------------------- GF(2) elimination
// Rows are samples: bits 0..nc-1 are features, bit nc is the label. R = words per row.
typedef struct {
    int nc, R, rank;
    uint64_t *basis;  // nc rows; basis[c] has its lowest set feature bit at c
    uint8_t *has;
    uint64_t row_xors;  // word XORs spent reducing rows
} gf2_t;

static void gf2_init(gf2_t *G, int nc) {
    G->nc = nc; G->R = (nc + 1 + 63) / 64; G->rank = 0; G->row_xors = 0;
    G->basis = calloc((size_t)nc * G->R, 8);
    G->has = calloc(nc, 1);
}
static void gf2_reset(gf2_t *G) {
    memset(G->has, 0, G->nc); G->rank = 0;
}
static void gf2_free(gf2_t *G) { free(G->basis); free(G->has); }

// returns 1 if the row added rank, 0 if it reduced to 0 = 0, -1 if it reduced to 0 = 1 (inconsistent)
static int gf2_insert(gf2_t *G, uint64_t *r) {
    const int R = G->R, nc = G->nc;
    for (int w = 0; w < R; w++) {
        for (;;) {
            uint64_t v = r[w];
            if (w == nc / 64) v &= (nc % 64) ? ((1ULL << (nc % 64)) - 1) : 0;  // feature bits only
            if (!v) break;
            int c = w * 64 + __builtin_ctzll(v);
            if (!G->has[c]) {
                memcpy(G->basis + (size_t)c * R, r, 8 * R);
                G->has[c] = 1; G->rank++;
                return 1;
            }
            const uint64_t *b = G->basis + (size_t)c * R;
            for (int u = w; u < R; u++) r[u] ^= b[u];
            G->row_xors += R - w;
        }
    }
    return ((r[nc / 64] >> (nc % 64)) & 1) ? -1 : 0;
}

// full rank only: back-substitution; sol gets nc bits
static void gf2_solve(gf2_t *G, uint64_t *sol) {
    const int R = G->R, nc = G->nc;
    memset(sol, 0, 8 * R);
    for (int c = nc - 1; c >= 0; c--) {
        const uint64_t *b = G->basis + (size_t)c * R;
        uint64_t par = (b[nc / 64] >> (nc % 64)) & 1;
        for (int w = c / 64; w < R; w++) {
            uint64_t v = b[w] & sol[w];
            if (w == c / 64) v &= ~((2ULL << (c % 64)) - 1);  // bits above c
            par ^= __builtin_parityll(v);
        }
        if (par) sol[c / 64] |= 1ULL << (c % 64);
    }
}

static inline int getbit(const uint64_t *v, int i) { return (v[i >> 6] >> (i & 63)) & 1; }

static int cmd_ge(int argc, char **argv) {
    int n = argl(argc, argv, "n", 0), k = argl(argc, argv, "k", 0), mmax = argl(argc, argv, "mmax", 0);
    uint64_t seed = argl(argc, argv, "seed", "1");
    inst_t I;
    gen(&I, n, k, 0.0, mmax, seed);
    gf2_t G;
    gf2_init(&G, n);
    uint64_t *row = calloc(G.R, 8), *sol = calloc(G.R, 8);
    double t0 = now();
    int mfull = -1;
    for (int s = 0; s < mmax; s++) {
        memset(row, 0, 8 * G.R);
        for (int j = 0; j < n; j++)
            if (getbit(I.X + (size_t)j * I.W, s)) row[j >> 6] |= 1ULL << (j & 63);
        if (getbit(I.y, s)) row[n >> 6] |= 1ULL << (n & 63);
        gf2_insert(&G, row);
        if (G.rank == n) { mfull = s + 1; break; }
    }
    int ok = 0, wt = -1;
    if (mfull > 0) {
        gf2_solve(&G, sol);
        wt = 0;
        for (int j = 0; j < n; j++) wt += getbit(sol, j);
        ok = (wt == k);
        for (int i = 0; i < k; i++) ok = ok && getbit(sol, I.secret[i]);
    }
    double t1 = now();
    printf("{\"cmd\":\"ge\",\"n\":%d,\"k\":%d,\"seed\":%" PRIu64 ",\"mmax\":%d,\"m_full_rank\":%d,\"ok\":%d,"
           "\"weight\":%d,\"row_xors\":%" PRIu64 ",\"wall_s\":%.6f}\n",
           n, k, seed, mmax, mfull, ok, wt, G.row_xors, t1 - t0);
    gf2_free(&G);
    return 0;
}

// xorshift-style trial RNG (independent of the data streams)
static inline uint64_t next64(uint64_t *s) { *s += 0x9E3779B97F4A7C15ULL; return mix64(*s); }

static int cmd_gers(int argc, char **argv) {
    int n = argl(argc, argv, "n", 0), k = argl(argc, argv, "k", 0), m = argl(argc, argv, "m", 0);
    double eta = argd(argc, argv, "eta", "0");
    uint64_t seed = argl(argc, argv, "seed", "1");
    int nc = argl(argc, argv, "ncols", "0");
    if (nc <= 0 || nc > n) nc = n;
    int extra = argl(argc, argv, "extra", "8");
    long maxtrials = argl(argc, argv, "maxtrials", "1000000");
    double maxsec = argd(argc, argv, "maxsec", "60");
    int nr = nc + extra;
    if (nr > m) { fprintf(stderr, "m too small\n"); return 2; }
    inst_t I;
    gen(&I, n, k, eta, m, seed);
    // accept a candidate when its disagreements on all m samples are below the midpoint of eta*m and m/2
    double thr = m * (0.5 + eta) / 2;
    gf2_t G;
    gf2_init(&G, nc);
    uint64_t *row = calloc(G.R, 8), *sol = calloc(G.R, 8), *tmp = calloc(I.W, 8);
    int *cols = malloc(sizeof(int) * n), *rows = malloc(sizeof(int) * m);
    for (int j = 0; j < n; j++) cols[j] = j;
    for (int s = 0; s < m; s++) rows[s] = s;
    uint64_t rs = mix64(seed ^ 0xabcdef12345ULL);
    long trials = 0, fullrank = 0, weightk = 0, verified = 0;
    int found[KMAX], ok = 0;
    double t0 = now();
    for (; trials < maxtrials;) {
        trials++;
        if (nc < n)
            for (int i = 0; i < nc; i++) {
                int r = i + next64(&rs) % (uint64_t)(n - i);
                int t = cols[i]; cols[i] = cols[r]; cols[r] = t;
            }
        for (int i = 0; i < nr; i++) {
            int r = i + next64(&rs) % (uint64_t)(m - i);
            int t = rows[i]; rows[i] = rows[r]; rows[r] = t;
        }
        gf2_reset(&G);
        int bad = 0;
        for (int i = 0; i < nr && !bad; i++) {
            int s = rows[i];
            memset(row, 0, 8 * G.R);
            for (int c = 0; c < nc; c++)
                if (getbit(I.X + (size_t)cols[c] * I.W, s)) row[c >> 6] |= 1ULL << (c & 63);
            if (getbit(I.y, s)) row[nc >> 6] |= 1ULL << (nc & 63);
            if (gf2_insert(&G, row) < 0) bad = 1;  // inconsistent: a noisy row (or secret outside cols)
        }
        if (bad || G.rank < nc) goto next;
        fullrank++;
        gf2_solve(&G, sol);
        int wt = 0;
        for (int c = 0; c < nc; c++) wt += getbit(sol, c);
        if (wt != k) goto next;
        weightk++;
        {
            int f = 0;
            for (int c = 0; c < nc; c++)
                if (getbit(sol, c)) found[f++] = cols[c];
            memcpy(tmp, I.y, 8 * I.W);
            for (int i = 0; i < k; i++)
                for (int w = 0; w < I.W; w++) tmp[w] ^= I.X[(size_t)found[i] * I.W + w];
            if (popcount_words(tmp, I.W) < thr) {
                verified = 1;
                for (int i = 1; i < k; i++)
                    for (int j = i; j > 0 && found[j - 1] > found[j]; j--) {
                        int t = found[j]; found[j] = found[j - 1]; found[j - 1] = t;
                    }
                ok = 1;
                for (int i = 0; i < k; i++) ok = ok && found[i] == I.secret[i];
                break;
            }
        }
    next:
        if ((trials & 1023) == 0 && now() - t0 > maxsec) break;
    }
    double t1 = now();
    printf("{\"cmd\":\"gers\",\"n\":%d,\"k\":%d,\"eta\":%g,\"m\":%d,\"seed\":%" PRIu64 ",\"ncols\":%d,\"extra\":%d,"
           "\"noisy\":%d,\"trials\":%ld,\"fullrank\":%ld,\"weightk\":%ld,\"verified\":%ld,\"ok\":%d,"
           "\"row_xors\":%" PRIu64 ",\"wall_s\":%.6f,\"us_per_trial\":%.3f}\n",
           n, k, eta, m, seed, nc, extra, popcount_words(I.noise, I.W), trials, fullrank, weightk, verified, ok,
           G.row_xors, t1 - t0, 1e6 * (t1 - t0) / trials);
    gf2_free(&G);
    return 0;
}

int main(int argc, char **argv) {
    if (argc < 2) {
        fprintf(stderr, "usage: spbits gen|exh|msearch|ge|gers key=value...\n");
        return 2;
    }
    if (!strcmp(argv[1], "gen")) return cmd_gen(argc, argv);
    if (!strcmp(argv[1], "exh")) return cmd_exh(argc, argv);
    if (!strcmp(argv[1], "msearch")) return cmd_msearch(argc, argv);
    if (!strcmp(argv[1], "ge")) return cmd_ge(argc, argv);
    if (!strcmp(argv[1], "gers")) return cmd_gers(argc, argv);
    fprintf(stderr, "unknown subcommand %s\n", argv[1]);
    return 2;
}
