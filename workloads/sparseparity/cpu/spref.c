// spref.c: the CPU reference for the card's sparse-parity solver (milestone M0). Host CPU only; opens no card.
//
// It implements exactly the card's formulation (sp.h, "T2 split"): a candidate is a (k-1)-subset R in colex
// order plus one feature j > max(R); row u_R = y * prod(x_R) in +-1; columns are the raw features; every
// correlation is an exact int32 c = sum_i u_R[i] x~_ij. Row tiles of 16 rows visit column tiles of 16 features
// from floor((pmin+1)/16); the staircase is masked. Two scoring paths give identical results:
//   mode=bits   packed XOR + popcount per candidate (fast; c = m - 2 * disagreements)
//   mode=int8   the card's arithmetic literally: +-1 byte rows, B tiles in TensorLoadInterleave8 layout,
//               16x16x64 multiply-accumulate blocks over the padded samples, the staircase mask in an epilogue
// Output: the argmax (ties to the smallest colex rank), a top-M list, the coverage checksums sum c and sum c^2
// (mod 2^64) with their closed forms, and with plan= the per-hart records the card must reproduce.
//
// Subcommands (key=value arguments; every one prints one JSON object):
//   gen    n k eta m seed [out=PREFIX]      instance hash (= proto/spbits gen), secret, hashes of the +-1 and
//                                           B-tile layouts; out= writes PREFIX.bits, PREFIX.pm1, PREFIX.btiles
//   scan   n k eta m seed [mode=bits|int8] [threads=1] [topm=8] [m1= tau1=] [plan=WL out=OUT] [dump=FILE]
//                                           [log=FILE] [cf=1]
//          plan=: run a work list from tools/planner.py and write the per-hart records file OUT (the expected
//          card output); m1= tau1=: two-stage screen (stage 1 on the first m1 samples logs c1 >= tau1, stage 2
//          rescores the survivors on all m); dump=: every correlation as int32, indexed by colex rank
//          (C(j,k) + row); log=: the sorted survivor entries (u64, sp.h packing)
//   check  n k eta m seed [brute=0|1]       closed-form checksums; brute=1 also enumerates all C(n,k) directly
//   selftest [threads=2]                    closed forms = brute force = bits = int8 = merged plan ranges, on small
//                                           sizes (best, top list and the tie flag); negative controls (a dropped
//                                           range, a duplicated range, one tile's staircase mask shifted) must fail
//
// Build: make (in this directory). Deterministic: every result is independent of the thread count.

#define _GNU_SOURCE
#include "sp.h"
#include <time.h>
#ifdef _OPENMP
#include <omp.h>
#endif

static double now(void) {
    struct timespec t;
    clock_gettime(CLOCK_MONOTONIC, &t);
    return t.tv_sec + 1e-9 * t.tv_nsec;
}

// ---------------------------------------------------------------- arguments
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

// ---------------------------------------------------------------- survivor buffers
typedef struct { uint64_t *v; size_t n, cap; } vec64_t;
static void vpush(vec64_t *b, uint64_t x) {
    if (b->n == b->cap) {
        b->cap = b->cap ? 2 * b->cap : 1024;
        b->v = (uint64_t *)realloc(b->v, b->cap * 8);
        if (!b->v) { fprintf(stderr, "out of memory (survivors)\n"); exit(1); }
    }
    b->v[b->n++] = x;
}
static int cmp_surv(const void *a, const void *b) {
    uint64_t x = sp_surv_key(*(const uint64_t *)a), y = sp_surv_key(*(const uint64_t *)b);
    return x < y ? -1 : x > y;
}

// ---------------------------------------------------------------- the scan
typedef struct {
    sp_inst_t I;          // the instance scanned (m1 samples in stage 1 of a two-stage screen)
    sp_geom_t G;
    int mode;             // 0 bits, 1 int8
    int topm;
    int32_t tau1;         // log survivors with c >= tau1 (INT32_MAX: none)
    int8_t *btiles;       // int8 mode: B tiles
    int32_t *dump;        // optional: every correlation by colex rank
    uint8_t *cover;       // optional: how many times each candidate was scored
    int perturb_mask;     // int8, a negative control: the first eligible tile of each range has its staircase
                          // shifted one column left in every row that allows it (the kernel's SPP_F_PERTURB_MASK)
} ctx_t;

static inline void emit(const ctx_t *C, sp_stats_t *st, vec64_t *sv, int32_t c, uint32_t j, uint64_t row) {
    sp_stats_add(st, c, j, row);
    if (c >= C->tau1) vpush(sv, sp_surv_pack(row, j, c));
    if (C->dump) {
        uint64_t idx = sp_C(&C->G, (int)j, C->G.k) + row;
        C->dump[idx] = c;
        if (C->cover[idx] < 255) C->cover[idx]++;
    }
}

// bits: rows rho in [16 t0, 16 t1) with suffix XORs Q[t] = y ^ x_R[t] ^ ... ^ x_R[a-1] kept across colex steps
static void scan_range_bits(const ctx_t *C, uint64_t t0, uint64_t t1, sp_stats_t *st, vec64_t *sv) {
    const sp_geom_t *G = &C->G;
    const sp_inst_t *I = &C->I;
    const int a = G->a, n = G->n, Wm = I->Wm, W = I->W, m = I->m;
    const uint64_t *X = I->X;
    uint64_t r0 = 16 * t0, r1 = 16 * t1 < G->NR ? 16 * t1 : G->NR;
    if (r1 <= r0) return;
    int R[SP_KMAX];
    sp_unrank(G, r0, R, a);
    uint64_t *Q = (uint64_t *)malloc(sizeof(uint64_t) * (size_t)(a + 1) * Wm);
    memcpy(Q + (size_t)a * Wm, I->y, sizeof(uint64_t) * Wm);
    for (int t = a - 1; t >= 0; t--)
        for (int w = 0; w < Wm; w++) Q[(size_t)t * Wm + w] = Q[(size_t)(t + 1) * Wm + w] ^ X[(size_t)R[t] * W + w];
    const int fast = !C->dump && C->tau1 == INT32_MAX;
    for (uint64_t row = r0; row < r1; row++) {
        const uint64_t *P = Q;
        const int start = R[a - 1] + 1;
#define INNER(WC)                                                                          \
        for (int j = start; j < n; j++) {                                                  \
            const uint64_t *xj = X + (size_t)j * W;                                        \
            int d = 0;                                                                     \
            for (int w = 0; w < (WC); w++) d += __builtin_popcountll(P[w] ^ xj[w]);        \
            int32_t c = m - 2 * d;                                                         \
            if (fast) sp_stats_add(st, c, (uint32_t)j, row);                               \
            else emit(C, st, sv, c, (uint32_t)j, row);                                     \
        }
        switch (Wm) {
        case 1: INNER(1); break;
        case 2: INNER(2); break;
        case 3: INNER(3); break;
        case 4: INNER(4); break;
        default: INNER(Wm); break;
        }
#undef INNER
        if (row + 1 < r1) {
            int t = sp_next(R, a);
            for (int u = t; u >= 0; u--)
                for (int w = 0; w < Wm; w++) Q[(size_t)u * Wm + w] = Q[(size_t)(u + 1) * Wm + w] ^ X[(size_t)R[u] * W + w];
        }
    }
    free(Q);
    st->ops += sp_range_outtiles(G, t0, t1) * (uint64_t)G->S;
}

// int8: the card's arithmetic, tile by tile
static void scan_range_int8(const ctx_t *C, uint64_t t0, uint64_t t1, sp_stats_t *st, vec64_t *sv) {
    const sp_geom_t *G = &C->G;
    const sp_inst_t *I = &C->I;
    const int a = G->a, n = G->n, S = G->S, mp = G->mp, m = I->m, Wm = I->Wm;
    int8_t *A = (int8_t *)malloc((size_t)16 * mp);
    uint64_t u[128];
    int pert = C->perturb_mask;
    for (uint64_t t = t0; t < t1 && t < G->NT; t++) {
        int valid[16], maxR[16];
        uint64_t rowid[16];
        for (int i = 0; i < 16; i++) {
            uint64_t row = 16 * t + (uint64_t)i;
            rowid[i] = row;
            valid[i] = row < G->NR;
            int8_t *ar = A + (size_t)i * mp;
            if (!valid[i]) { memset(ar, 0, (size_t)mp); maxR[i] = n; continue; }
            int R[SP_KMAX];
            sp_unrank(G, row, R, a);
            maxR[i] = R[a - 1];
            for (int w = 0; w < Wm; w++) {           // u_R in the bit domain: y ^ x_R
                uint64_t v = I->y[w];
                for (int q = 0; q < a; q++) v ^= I->X[(size_t)R[q] * I->W + w];
                u[w] = v;
            }
            for (int s = 0; s < mp; s++) ar[s] = s < m ? (int8_t)(1 - 2 * sp_bit(u, s)) : 0;
        }
        const int j0 = sp_tile_j0(G, t);
        for (int J = j0; J < G->NJ; J++) {
            int shift = 0;
            if (pert && valid[0] && 16 * J <= maxR[0] && maxR[0] + 1 < 16 * J + 16 && maxR[0] + 1 < n) {
                shift = 1;
                pert = 0;
            }
            int32_t Cm[16][16];
            memset(Cm, 0, sizeof Cm);
            for (int s = 0; s < S; s++) {            // one TensorIMA8A32: C[16x16] += A[16x64] x B[64x16]
                const int8_t *B = C->btiles + ((size_t)J * S + s) * 1024;
                for (int i = 0; i < 16; i++) {
                    const int8_t *ar = A + (size_t)i * mp + 64 * s;
                    for (int c = 0; c < 16; c++) {
                        int32_t acc = 0;
                        for (int r = 0; r < 16; r++)
                            for (int e = 0; e < 4; e++) acc += (int32_t)ar[4 * r + e] * (int32_t)B[r * 64 + 4 * c + e];
                        Cm[i][c] += acc;
                    }
                }
                st->ops++;
            }
            for (int i = 0; i < 16; i++) {           // epilogue: the staircase mask
                if (!valid[i]) continue;
                int lo = maxR[i] + 1 - 16 * J, hi = n - 16 * J;
                lo = lo < 0 ? 0 : lo;
                hi = hi > 16 ? 16 : hi;
                if (shift && lo >= 1 && hi > lo) { lo--; hi--; }
                for (int c = lo; c < hi; c++) emit(C, st, sv, Cm[i][c], (uint32_t)(16 * J + c), rowid[i]);
            }
        }
    }
    free(A);
}

static void scan_range(const ctx_t *C, uint64_t t0, uint64_t t1, sp_stats_t *st, vec64_t *sv) {
    if (C->mode == 1) scan_range_int8(C, t0, t1, st, sv);
    else scan_range_bits(C, t0, t1, st, sv);
}

// ranges[i] = [lo[i], hi[i]) row tiles; per-range stats out[i]; survivors appended to *sv (sorted later)
static void scan_ranges(const ctx_t *C, int nr, const uint64_t *lo, const uint64_t *hi, sp_stats_t *out,
                        vec64_t *sv, int threads) {
#ifdef _OPENMP
    if (threads > 0) omp_set_num_threads(threads);
#endif
    for (int i = 0; i < nr; i++) sp_stats_init(&out[i], C->topm);
#pragma omp parallel
    {
        vec64_t mine = {0};
#pragma omp for schedule(dynamic, 1)
        for (int i = 0; i < nr; i++) scan_range(C, lo[i], hi[i], &out[i], &mine);
#pragma omp critical
        {
            for (size_t q = 0; q < mine.n; q++) vpush(sv, mine.v[q]);
        }
        free(mine.v);
    }
}

// the whole scan as `chunks` equal runs of row tiles
static void scan_all(const ctx_t *C, int threads, sp_stats_t *tot, vec64_t *sv) {
    uint64_t NT = C->G.NT;
    int chunks = NT < 4096 ? (int)NT : 4096;
    if (chunks < 1) chunks = 1;
    uint64_t *lo = (uint64_t *)malloc(8 * (size_t)chunks), *hi = (uint64_t *)malloc(8 * (size_t)chunks);
    for (int i = 0; i < chunks; i++) { lo[i] = NT * i / chunks; hi[i] = NT * (i + 1) / chunks; }
    sp_stats_t *st = (sp_stats_t *)malloc(sizeof(sp_stats_t) * chunks);
    scan_ranges(C, chunks, lo, hi, st, sv, threads);
    sp_stats_init(tot, C->topm);
    for (int i = 0; i < chunks; i++) sp_stats_merge(tot, &st[i]);
    free(lo); free(hi); free(st);
}

// ---------------------------------------------------------------- brute force (independent of the tile geometry)
// Enumerates k-subsets in lexicographic order; pm1=1 scores through per-sample +-1 products (slow, tiny sizes).
static void brute(const sp_inst_t *I, const sp_geom_t *G, int pm1, sp_stats_t *st, int32_t *dump) {
    const int n = I->n, k = I->k, m = I->m, Wm = I->Wm;
    int T[SP_KMAX];
    for (int i = 0; i < k; i++) T[i] = i;
    uint64_t v[128];
    for (;;) {
        int32_t c;
        if (pm1) {
            c = 0;
            for (int s = 0; s < m; s++) {
                int prod = 1 - 2 * sp_bit(I->y, s);
                for (int i = 0; i < k; i++) prod *= 1 - 2 * sp_bit(I->X + (size_t)T[i] * I->W, s);
                c += prod;
            }
        } else {
            for (int w = 0; w < Wm; w++) {
                uint64_t x = I->y[w];
                for (int i = 0; i < k; i++) x ^= I->X[(size_t)T[i] * I->W + w];
                v[w] = x;
            }
            c = m - 2 * sp_popcount_words(v, Wm);
        }
        uint64_t row = sp_rank(G, T, k - 1);
        uint32_t j = (uint32_t)T[k - 1];
        sp_stats_add(st, c, j, row);
        if (dump) dump[sp_C(G, (int)j, k) + row] = c;
        int i = k - 1;
        while (i >= 0 && T[i] == n - k + i) i--;
        if (i < 0) break;
        T[i]++;
        for (int q = i + 1; q < k; q++) T[q] = T[q - 1] + 1;
    }
}

// ---------------------------------------------------------------- work lists and records
typedef struct {
    sp_wl_hdr_t h;
    sp_wl_minion_t *mi;
    sp_wl_range_t *rg;
} wl_t;

static int wl_read(const char *path, wl_t *L) {
    FILE *f = fopen(path, "rb");
    if (!f) { fprintf(stderr, "cannot open %s\n", path); return -1; }
    int ok = fread(&L->h, sizeof L->h, 1, f) == 1 && L->h.magic == SP_WL_MAGIC && L->h.version == SP_WL_VERSION;
    if (ok) {
        L->mi = (sp_wl_minion_t *)calloc(L->h.nminions ? L->h.nminions : 1, sizeof(sp_wl_minion_t));
        L->rg = (sp_wl_range_t *)calloc(L->h.nranges ? L->h.nranges : 1, sizeof(sp_wl_range_t));
        ok = fread(L->mi, sizeof(sp_wl_minion_t), L->h.nminions, f) == L->h.nminions &&
             fread(L->rg, sizeof(sp_wl_range_t), L->h.nranges, f) == L->h.nranges;
    }
    fclose(f);
    if (!ok) fprintf(stderr, "%s: not a version-%u work list\n", path, SP_WL_VERSION);
    return ok ? 0 : -1;
}

static int write_out(const char *path, const wl_t *L, const sp_stats_t *ms, const ctx_t *C) {
    FILE *f = fopen(path, "wb");
    if (!f) { fprintf(stderr, "cannot write %s\n", path); return -1; }
    const uint32_t nm = L->h.nminions, topm = L->h.topm;
    sp_out_hdr_t oh;
    memset(&oh, 0, sizeof oh);
    oh.magic = SP_OUT_MAGIC; oh.version = 1; oh.nminions = nm; oh.harts = 2; oh.topm = topm;
    oh.n = (uint32_t)C->G.n; oh.k = (uint32_t)C->G.k; oh.m = (uint32_t)C->G.m;
    oh.nranges = L->h.nranges; oh.total_ops = L->h.total_ops; oh.total_cands = L->h.total_cands;
    fwrite(&oh, sizeof oh, 1, f);
    for (uint32_t q = 0; q < nm; q++) {
        sp_rec_t r0, r1;
        sp_stats_to_rec(&ms[q], q, &r0);
        memset(&r1, 0, sizeof r1);
        r1.magic = SP_REC_MAGIC; r1.hart = 1; r1.minion = q; r1.flags = SP_REC_VALID; r1.best_c = INT32_MIN;
        uint64_t tiles = 0;
        for (uint32_t i = 0; i < L->mi[q].nranges; i++) {
            const sp_wl_range_t *g = &L->rg[L->mi[q].first_range + i];
            tiles += g->tile_end - g->tile_begin;
        }
        r1.ops = (uint32_t)tiles;
        fwrite(&r0, sizeof r0, 1, f);
        fwrite(&r1, sizeof r1, 1, f);
    }
    for (uint32_t q = 0; q < nm; q++)
        for (uint32_t i = 0; i < topm; i++) {
            sp_top_t e;
            if ((int)i < ms[q].ntop && (int)i < ms[q].topm) e = ms[q].top[i];
            else { e.c = INT32_MIN; e.j = 0; e.row = 0; }
            fwrite(&e, sizeof e, 1, f);
        }
    fclose(f);
    return 0;
}

// ---------------------------------------------------------------- JSON output
static void print_set(const int *s, int k) {
    printf("[");
    for (int i = 0; i < k; i++) printf("%s%d", i ? "," : "", s[i]);
    printf("]");
}
static void found_set(const sp_geom_t *G, uint64_t row, uint32_t j, int *T) {
    sp_unrank(G, row, T, G->a);
    T[G->a] = (int)j;
}
static int same_set(const int *a, const int *b, int k) {
    for (int i = 0; i < k; i++)
        if (a[i] != b[i]) return 0;
    return 1;
}
static void print_stats(const char *name, const sp_stats_t *st, const sp_geom_t *G, const sp_inst_t *I) {
    int T[SP_KMAX] = {0};
    if (st->has_best) found_set(G, st->best_row, st->best_j, T);
    int unique = st->has_best && !st->tie;
    printf("\"%s\":{\"best_c\":%d,\"best_row\":%" PRIu64 ",\"best_j\":%u,\"found\":", name, st->best_c,
           st->best_row, st->best_j);
    print_set(T, G->k);
    printf(",\"unique\":%d,\"ok\":%d,\"sum_c\":%" PRId64 ",\"sum_c2\":%" PRIu64 ",\"cands\":%" PRIu64
           ",\"ops\":%" PRIu64 ",\"top\":[",
           unique, st->has_best && unique && same_set(T, I->secret, G->k), st->sum_c, st->sum_c2, st->cands, st->ops);
    for (int i = 0; i < st->ntop; i++)
        printf("%s[%d,%u,%" PRIu64 "]", i ? "," : "", st->top[i].c, st->top[i].j, st->top[i].row);
    printf("]}");
}

// ---------------------------------------------------------------- subcommands
static int init_ctx(ctx_t *C, int n, int k, double eta, int m, uint64_t seed, int mode, int topm) {
    memset(C, 0, sizeof *C);
    if (sp_gen(&C->I, n, k, eta, m, seed, 1) || sp_geom_init(&C->G, n, k, m)) {
        fprintf(stderr, "bad instance (n=%d k=%d m=%d; 2 <= k <= %d, n <= %d)\n", n, k, m, SP_KMAX, SP_NMAX);
        return -1;
    }
    if (m > 64 * 128) { fprintf(stderr, "m <= 8192\n"); return -1; }
    C->mode = mode;
    C->topm = topm;
    C->tau1 = INT32_MAX;
    if (mode == 1) {
        C->btiles = (int8_t *)sp_alloc(sp_btiles_bytes(n, C->G.S));
        sp_btiles(&C->I, C->G.S, C->btiles);
    }
    return 0;
}
static void free_ctx(ctx_t *C) {
    sp_free(&C->I);
    sp_geom_free(&C->G);
    free(C->btiles); free(C->dump); free(C->cover);
}

static int cmd_gen(void) {
    int n = argl("n", 0), k = argl("k", 0), m = argl("m", 0);
    double eta = argd("eta", "0");
    uint64_t seed = (uint64_t)argl("seed", "1");
    const char *out = argval("out", "");
    sp_inst_t I;
    if (sp_gen(&I, n, k, eta, m, seed, 1)) { fprintf(stderr, "bad instance\n"); return 2; }
    const int S = sp_slices(m), mp = 64 * S;
    int8_t *pf = (int8_t *)sp_alloc((size_t)n * mp), *pl = (int8_t *)sp_alloc((size_t)mp);
    int8_t *bt = (int8_t *)sp_alloc(sp_btiles_bytes(n, S));
    sp_pm1_features(&I, mp, pf);
    sp_pm1_labels(&I, mp, pl);
    sp_btiles(&I, S, bt);
    printf("{\"cmd\":\"gen\",\"n\":%d,\"k\":%d,\"eta\":%g,\"m\":%d,\"seed\":%" PRIu64 ",\"hash\":\"%016" PRIx64
           "\",\"secret\":", n, k, eta, m, seed, sp_hash(&I));
    print_set(I.secret, k);
    printf(",\"noise\":%d,\"Wm\":%d,\"S\":%d,\"mp\":%d,\"pm1_hash\":\"%016" PRIx64 "\",\"labels_hash\":\"%016" PRIx64
           "\",\"btiles_hash\":\"%016" PRIx64 "\"}\n",
           sp_popcount_words(I.noise, I.Wm), I.Wm, S, mp, sp_bytes_hash(pf, (size_t)n * mp),
           sp_bytes_hash(pl, (size_t)mp), sp_bytes_hash(bt, sp_btiles_bytes(n, S)));
    if (*out) {
        char path[4096];
        FILE *f;
        snprintf(path, sizeof path, "%s.bits", out);          // X (n x Wm u64), then y (Wm u64)
        if (!(f = fopen(path, "wb"))) { fprintf(stderr, "cannot write %s\n", path); return 1; }
        fwrite(I.X, 8, (size_t)n * I.Wm, f);                 // W == Wm here (wpad 1)
        fwrite(I.y, 8, (size_t)I.Wm, f);
        fclose(f);
        snprintf(path, sizeof path, "%s.pm1", out);           // features (n x mp int8), then labels (mp int8)
        if (!(f = fopen(path, "wb"))) { fprintf(stderr, "cannot write %s\n", path); return 1; }
        fwrite(pf, 1, (size_t)n * mp, f);
        fwrite(pl, 1, (size_t)mp, f);
        fclose(f);
        snprintf(path, sizeof path, "%s.btiles", out);        // NJ x S tiles of 1 KB
        if (!(f = fopen(path, "wb"))) { fprintf(stderr, "cannot write %s\n", path); return 1; }
        fwrite(bt, 1, sp_btiles_bytes(n, S), f);
        fclose(f);
    }
    free(pf); free(pl); free(bt);
    sp_free(&I);
    return 0;
}

static void print_cf(const sp_inst_t *I, const char *name) {
    int64_t s1; uint64_t s2; int fits;
    sp_closed_forms(I, &s1, &s2, &fits);
    printf("\"%s\":{\"sum_c\":%" PRId64 ",\"sum_c2\":%" PRIu64 ",\"sum_c2_exact\":%d}", name, s1, s2, fits);
}

static int cmd_check(void) {
    int n = argl("n", 0), k = argl("k", 0), m = argl("m", 0);
    double eta = argd("eta", "0");
    uint64_t seed = (uint64_t)argl("seed", "1");
    int dobrute = argl("brute", "0");
    sp_inst_t I;
    sp_geom_t G;
    if (sp_gen(&I, n, k, eta, m, seed, 1) || sp_geom_init(&G, n, k, m)) { fprintf(stderr, "bad instance\n"); return 2; }
    int64_t s1; uint64_t s2; int fits;
    double t0 = now();
    sp_closed_forms(&I, &s1, &s2, &fits);
    double t1 = now();
    printf("{\"cmd\":\"check\",\"n\":%d,\"k\":%d,\"eta\":%g,\"m\":%d,\"seed\":%" PRIu64 ",\"cands\":%" PRIu64
           ",\"sum_c\":%" PRId64 ",\"sum_c2\":%" PRIu64 ",\"sum_c2_exact\":%d,\"cf_s\":%.4f",
           n, k, eta, m, seed, G.Ncand, s1, s2, fits, t1 - t0);
    int rc = 0;
    if (dobrute) {
        sp_stats_t st;
        sp_stats_init(&st, 8);
        brute(&I, &G, argl("pm1", "0"), &st, NULL);
        int ok = st.sum_c == s1 && st.sum_c2 == s2 && st.cands == G.Ncand;
        printf(",\"brute\":{\"sum_c\":%" PRId64 ",\"sum_c2\":%" PRIu64 ",\"cands\":%" PRIu64 ",\"match\":%d}",
               st.sum_c, st.sum_c2, st.cands, ok);
        rc = !ok;
    }
    printf("}\n");
    sp_free(&I);
    sp_geom_free(&G);
    return rc;
}

static int cmd_scan(void) {
    int n = argl("n", 0), k = argl("k", 0), m = argl("m", 0);
    double eta = argd("eta", "0");
    uint64_t seed = (uint64_t)argl("seed", "1");
    int threads = argl("threads", "1"), topm = argl("topm", "8"), cf = argl("cf", "1");
    int mode = !strcmp(argval("mode", "bits"), "int8");
    int m1 = argl("m1", "0");
    int32_t tau1 = (int32_t)argl("tau1", "0");
    const char *plan = argval("plan", ""), *out = argval("out", ""), *dumpf = argval("dump", "");
    const char *logf = argval("log", "");
    const int twostage = m1 > 0;
    if (twostage && (m1 > m || tau1 < 1)) { fprintf(stderr, "two-stage needs 0 < m1 <= m and tau1 >= 1\n"); return 2; }
    const int ms = twostage ? m1 : m;   // samples the scan sees
    ctx_t C;
    if (init_ctx(&C, n, k, eta, ms, seed, mode, topm)) return 2;
    if (twostage && (C.G.NR >= (1ULL << 40) || m1 > 4095)) {   // the survivor entry: row 40 bits, c1 12 bits
        fprintf(stderr, "two-stage: C(n-1,k-1) = %" PRIu64 " rows and m1 = %d do not fit a survivor entry "
                "(rows < 2^40, m1 <= 4095)\n", C.G.NR, m1);
        return 2;
    }
    if (twostage) C.tau1 = tau1;
    if (*dumpf) {
        if (C.G.Ncand > (1ULL << 28)) { fprintf(stderr, "dump= only up to 2^28 candidates\n"); return 2; }
        C.dump = (int32_t *)calloc(C.G.Ncand, 4);
        C.cover = (uint8_t *)calloc(C.G.Ncand, 1);
    }
    vec64_t sv = {0};
    sp_stats_t tot;
    wl_t L;
    memset(&L, 0, sizeof L);
    sp_stats_t *mstats = NULL;
    int rc = 0, plan_ok = 1;
    double t0 = now();
    if (*plan) {
        if (wl_read(plan, &L)) return 2;
        if ((int)L.h.n != n || (int)L.h.k != k || (int)L.h.m != ms) {
            fprintf(stderr, "plan is for n=%u k=%u m=%u, the scan for n=%d k=%d m=%d\n", L.h.n, L.h.k, L.h.m, n, k, ms);
            return 2;
        }
        if ((int)L.h.topm != topm) C.topm = topm = (int)L.h.topm;
        uint64_t *lo = (uint64_t *)malloc(8 * (L.h.nranges + 1)), *hi = (uint64_t *)malloc(8 * (L.h.nranges + 1));
        for (uint32_t i = 0; i < L.h.nranges; i++) { lo[i] = L.rg[i].tile_begin; hi[i] = L.rg[i].tile_end; }
        sp_stats_t *rs = (sp_stats_t *)malloc(sizeof(sp_stats_t) * (L.h.nranges + 1));
        scan_ranges(&C, (int)L.h.nranges, lo, hi, rs, &sv, threads);
        for (uint32_t i = 0; i < L.h.nranges; i++)   // the planner's arithmetic, checked against the scan
            if (rs[i].ops != L.rg[i].ops || rs[i].cands != L.rg[i].cands) {
                if (plan_ok) fprintf(stderr, "range %u: plan says ops %" PRIu64 " cands %" PRIu64 ", scan did %" PRIu64
                                     " / %" PRIu64 "\n", i, L.rg[i].ops, L.rg[i].cands, rs[i].ops, rs[i].cands);
                plan_ok = 0;
            }
        mstats = (sp_stats_t *)malloc(sizeof(sp_stats_t) * (L.h.nminions + 1));
        sp_stats_init(&tot, topm);
        for (uint32_t q = 0; q < L.h.nminions; q++) {
            sp_stats_init(&mstats[q], topm);
            for (uint32_t i = 0; i < L.mi[q].nranges; i++) sp_stats_merge(&mstats[q], &rs[L.mi[q].first_range + i]);
            sp_stats_merge(&tot, &mstats[q]);
        }
        free(lo); free(hi); free(rs);
    } else {
        scan_all(&C, threads, &tot, &sv);
    }
    double t1 = now();
    printf("{\"cmd\":\"scan\",\"mode\":\"%s\",\"n\":%d,\"k\":%d,\"eta\":%g,\"m\":%d,\"seed\":%" PRIu64
           ",\"threads\":%d,\"topm\":%d,\"secret\":", mode ? "int8" : "bits", n, k, eta, m, seed, threads, topm);
    print_set(C.I.secret, k);
    printf(",\"noise\":%d,\"NT\":%" PRIu64 ",\"Ncand\":%" PRIu64 ",\"wall_s\":%.6f,",
           sp_popcount_words(C.I.noise, C.I.Wm), C.G.NT, C.G.Ncand, t1 - t0);
    if (*plan)
        printf("\"plan\":{\"file\":\"%s\",\"nminions\":%u,\"nranges\":%u,\"slice\":%u,\"nslices\":%u,"
               "\"total_ops\":%" PRIu64 ",\"total_cands\":%" PRIu64 ",\"ranges_match\":%d},",
               plan, L.h.nminions, L.h.nranges, L.h.slice, L.h.nslices, L.h.total_ops, L.h.total_cands, plan_ok);
    print_stats(twostage ? "stage1" : "result", &tot, &C.G, &C.I);
    const int complete = tot.cands == C.G.Ncand;
    if (cf) {
        int64_t s1; uint64_t s2; int fits;
        sp_closed_forms(&C.I, &s1, &s2, &fits);
        int match = tot.sum_c == s1 && tot.sum_c2 == s2 && complete;
        printf(",\"closed\":{\"cands\":%" PRIu64 ",\"sum_c\":%" PRId64 ",\"sum_c2\":%" PRIu64
               ",\"sum_c2_exact\":%d,\"applies\":%d,\"match\":%d}",
               C.G.Ncand, s1, s2, fits, complete, match);
        if (complete && !match) rc = 1;
    }
    if (C.dump) {
        uint64_t miss = 0, dup = 0;
        for (uint64_t i = 0; i < C.G.Ncand; i++) { miss += C.cover[i] == 0; dup += C.cover[i] > 1; }
        FILE *f = fopen(dumpf, "wb");
        if (f) { fwrite(C.dump, 4, C.G.Ncand, f); fclose(f); }
        printf(",\"dump\":{\"file\":\"%s\",\"missing\":%" PRIu64 ",\"duplicated\":%" PRIu64 "}", dumpf, miss, dup);
        if ((miss && !*plan) || dup) rc = 1;
    }
    if (twostage) {   // stage 2: rescore the survivors on all m samples
        qsort(sv.v, sv.n, 8, cmp_surv);
        sp_inst_t Ifull;
        sp_geom_t Gfull;
        sp_gen(&Ifull, n, k, eta, m, seed, 1);
        sp_geom_init(&Gfull, n, k, m);
        double t2 = now();
        sp_stats_t s2;
        sp_stats_init(&s2, topm);
        int secret_kept = 0;
        const uint64_t srow = sp_rank(&Gfull, Ifull.secret, k - 1);
        const uint32_t sj = (uint32_t)Ifull.secret[k - 1];
#pragma omp parallel
        {
            sp_stats_t mine;
            sp_stats_init(&mine, topm);
            uint64_t tmp[128];
#pragma omp for schedule(static)
            for (size_t i = 0; i < sv.n; i++) {
                uint64_t row = sp_surv_row(sv.v[i]);
                uint32_t j = sp_surv_j(sv.v[i]);
                sp_stats_add(&mine, sp_score(&Ifull, &Gfull, row, j, tmp), j, row);
            }
#pragma omp critical
            sp_stats_merge(&s2, &mine);
        }
        for (size_t i = 0; i < sv.n; i++)
            if (sp_surv_row(sv.v[i]) == srow && sp_surv_j(sv.v[i]) == sj) secret_kept = 1;
        double t3 = now();
        printf(",\"m1\":%d,\"tau1\":%d,\"survivors\":%zu,\"secret_survived\":%d,\"stage2_s\":%.6f,", m1, tau1, sv.n,
               secret_kept, t3 - t2);
        print_stats("result", &s2, &Gfull, &Ifull);
        if (*logf) {
            FILE *f = fopen(logf, "wb");
            if (f) { fwrite(sv.v, 8, sv.n, f); fclose(f); }
        }
        sp_free(&Ifull);
        sp_geom_free(&Gfull);
    }
    printf("}\n");
    if (*plan && *out && write_out(out, &L, mstats, &C)) rc = 1;
    if (!plan_ok) rc = 1;
    free(mstats); free(L.mi); free(L.rg); free(sv.v);
    free_ctx(&C);
    return rc;
}

// ---------------------------------------------------------------- selftest
static int stats_equal(const sp_stats_t *a, const sp_stats_t *b, int with_ops) {
    if (a->sum_c != b->sum_c || a->sum_c2 != b->sum_c2 || a->cands != b->cands) return 0;
    if (with_ops && a->ops != b->ops) return 0;
    if (a->has_best != b->has_best || a->best_c != b->best_c || a->best_j != b->best_j || a->best_row != b->best_row)
        return 0;
    if (a->has_best && a->tie != b->tie) return 0;
    if (a->ntop != b->ntop) return 0;
    for (int i = 0; i < a->ntop; i++)
        if (a->top[i].c != b->top[i].c || a->top[i].j != b->top[i].j || a->top[i].row != b->top[i].row) return 0;
    return 1;
}

static int cmd_selftest(void) {
    int threads = argl("threads", "2");
    struct { int n, k; double eta; int m; uint64_t seed; int pm1; } cases[] = {
        {12, 3, 0.2, 20, 1, 1},  {16, 4, 0.1, 37, 2, 1},   {10, 5, 0.3, 9, 3, 1},    {32, 3, 0.1, 128, 1, 1},
        {20, 2, 0.2, 50, 4, 1},  {18, 6, 0.1, 30, 5, 1},   {40, 4, 0.25, 100, 6, 0}, {33, 3, 0.3, 70, 7, 1},
        {48, 4, 0.2, 130, 8, 0}, {64, 3, 0.1, 64, 9, 0},   {17, 2, 0.0, 5, 10, 1},   {80, 3, 0.4, 300, 11, 0},
        {128, 4, 0.2, 192, 1, 0},
    };
    int fails = 0;
    for (size_t ci = 0; ci < sizeof cases / sizeof cases[0]; ci++) {
        const int n = cases[ci].n, k = cases[ci].k, m = cases[ci].m;
        const double eta = cases[ci].eta;
        const uint64_t seed = cases[ci].seed;
        ctx_t Cb, Ci;
        if (init_ctx(&Cb, n, k, eta, m, seed, 0, 8) || init_ctx(&Ci, n, k, eta, m, seed, 1, 8)) return 2;
        const int small = Cb.G.Ncand <= 2000000;
        // closed forms and brute force
        int64_t s1; uint64_t s2; int fits;
        sp_closed_forms(&Cb.I, &s1, &s2, &fits);
        sp_stats_t br;
        sp_stats_init(&br, 8);
        int32_t *dump_br = small ? (int32_t *)calloc(Cb.G.Ncand, 4) : NULL;
        brute(&Cb.I, &Cb.G, cases[ci].pm1, &br, dump_br);
        int cf_ok = br.sum_c == s1 && br.sum_c2 == s2 && br.cands == Cb.G.Ncand;
        // bits (with a dump: every candidate exactly once, same value as brute force), int8
        vec64_t sv = {0};
        if (small) { Cb.dump = (int32_t *)calloc(Cb.G.Ncand, 4); Cb.cover = (uint8_t *)calloc(Cb.G.Ncand, 1); }
        sp_stats_t sb, si;
        scan_all(&Cb, threads, &sb, &sv);
        int cover_ok = 1;
        if (small)
            for (uint64_t i = 0; i < Cb.G.Ncand; i++)
                if (Cb.cover[i] != 1 || Cb.dump[i] != dump_br[i]) { cover_ok = 0; break; }
        scan_all(&Ci, threads, &si, &sv);
        int bits_ok = stats_equal(&sb, &br, 0), int8_ok = stats_equal(&si, &sb, 1);
        int ops_ok = sb.ops == sp_range_outtiles(&Cb.G, 0, Cb.G.NT) * (uint64_t)Cb.G.S &&
                     sb.cands == sp_range_cands(&Cb.G, 0, Cb.G.NT);
        // a plan: 7 uneven ranges dealt to 3 minions; merged it must equal the full scan; negative controls fail
        uint64_t NT = Cb.G.NT, lo[8], hi[8];
        int nr = NT >= 7 ? 7 : (int)NT;
        for (int i = 0; i < nr; i++) { lo[i] = NT * i * i / (nr * nr); hi[i] = NT * (i + 1) * (i + 1) / (nr * nr); }
        sp_stats_t rs[8], merged, drop, dupl;
        vec64_t sv2 = {0};
        free(Cb.dump); free(Cb.cover); Cb.dump = NULL; Cb.cover = NULL;
        scan_ranges(&Cb, nr, lo, hi, rs, &sv2, threads);
        sp_stats_t mins[3];
        for (int q = 0; q < 3; q++) sp_stats_init(&mins[q], 8);
        for (int i = 0; i < nr; i++) sp_stats_merge(&mins[i % 3], &rs[i]);
        sp_stats_init(&merged, 8);
        for (int q = 0; q < 3; q++) sp_stats_merge(&merged, &mins[q]);
        int plan_ok = stats_equal(&merged, &sb, 1);
        // negative controls: drop the largest range; duplicate the range with the most candidates
        int big = 0;
        for (int i = 1; i < nr; i++) if (rs[i].cands > rs[big].cands) big = i;
        sp_stats_init(&drop, 8);
        sp_stats_init(&dupl, 8);
        for (int i = 0; i < nr; i++) {
            if (i != big) sp_stats_merge(&drop, &rs[i]);
            sp_stats_merge(&dupl, &rs[i]);
        }
        sp_stats_merge(&dupl, &rs[big]);
        int neg_ok = !(drop.sum_c == s1 && drop.sum_c2 == s2) && !(dupl.sum_c == s1 && dupl.sum_c2 == s2);
        // the third control: range `big` scanned (int8) with one tile's staircase shifted; the count is unchanged
        sp_stats_t mrs[8], mask;
        vec64_t sv3 = {0};
        scan_ranges(&Ci, nr, lo, hi, mrs, &sv3, threads);
        Ci.perturb_mask = 1;
        scan_ranges(&Ci, 1, lo + big, hi + big, &mrs[big], &sv3, threads);
        Ci.perturb_mask = 0;
        sp_stats_init(&mask, 8);
        for (int i = 0; i < nr; i++) sp_stats_merge(&mask, &mrs[i]);
        const int mask_sum_fails = mask.sum_c != s1, mask_sq_fails = mask.sum_c2 != s2;
        const int mask_ok = mask.cands == Cb.G.Ncand && mask_sum_fails && mask_sq_fails;
        free(sv3.v);
        // two-stage survivors: those with c1 >= tau1 on the first m/2 samples, against brute force at m/2
        int m1 = m / 2 > 0 ? m / 2 : 1;
        ctx_t C1;
        init_ctx(&C1, n, k, eta, m1, seed, ci % 2, 8);
        C1.tau1 = m1 / 4 > 0 ? m1 / 4 : 1;
        vec64_t s1v = {0};
        sp_stats_t st1;
        scan_all(&C1, threads, &st1, &s1v);
        uint64_t want = 0;
        int surv_ok = 1;
        if (small) {
            int32_t *d1 = (int32_t *)calloc(C1.G.Ncand, 4);
            sp_stats_t b1;
            sp_stats_init(&b1, 0);
            brute(&C1.I, &C1.G, 0, &b1, d1);
            for (uint64_t i = 0; i < C1.G.Ncand; i++) want += d1[i] >= C1.tau1;
            for (size_t i = 0; i < s1v.n; i++) {
                uint64_t e = s1v.v[i];
                if (d1[sp_C(&C1.G, (int)sp_surv_j(e), k) + sp_surv_row(e)] != sp_surv_c1(e)) surv_ok = 0;
            }
            surv_ok = surv_ok && want == s1v.n;
            free(d1);
        }
        int ok = cf_ok && bits_ok && int8_ok && ops_ok && cover_ok && plan_ok && neg_ok && mask_ok && surv_ok;
        fails += !ok;
        printf("{\"selftest\":[%d,%d,%g,%d,%" PRIu64 "],\"Ncand\":%" PRIu64 ",\"closed_eq_brute\":%d,\"bits_eq_brute\":%d,"
               "\"int8_eq_bits\":%d,\"ops_cands\":%d,\"each_once\":%d,\"plan_merge\":%d,\"neg_controls_fail\":%d,"
               "\"mask_control\":{\"count_kept\":%d,\"sum_c_fails\":%d,\"sum_c2_fails\":%d},\"tie\":%d,"
               "\"survivors\":%d,\"sum_c2_exact\":%d,\"ok\":%d}\n",
               n, k, eta, m, seed, Cb.G.Ncand, cf_ok, bits_ok, int8_ok, ops_ok, small ? cover_ok : -1, plan_ok, neg_ok,
               mask.cands == Cb.G.Ncand, mask_sum_fails, mask_sq_fails, sb.tie, small ? surv_ok : -1, fits, ok);
        free(dump_br); free(sv.v); free(sv2.v); free(s1v.v);
        free_ctx(&Cb); free_ctx(&Ci); free_ctx(&C1);
    }
    printf("{\"selftest\":\"done\",\"failures\":%d}\n", fails);
    return fails ? 1 : 0;
}

int main(int argc, char **argv) {
    g_argc = argc; g_argv = argv;
    if (argc < 2) {
        fprintf(stderr, "usage: spref gen|scan|check|selftest key=value ...\n");
        return 2;
    }
    if (!strcmp(argv[1], "gen")) return cmd_gen();
    if (!strcmp(argv[1], "scan")) return cmd_scan();
    if (!strcmp(argv[1], "check")) return cmd_check();
    if (!strcmp(argv[1], "selftest")) return cmd_selftest();
    fprintf(stderr, "unknown subcommand %s\n", argv[1]);
    return 2;
}
