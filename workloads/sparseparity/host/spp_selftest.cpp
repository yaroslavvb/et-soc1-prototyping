// CPU-only checks of the host's model of the scan (no device, no runtime library):
//   spp_selftest                          all checks below; exit 0 when all pass
//   spp_selftest --hash N K ETA M SEED    print the instance hash (compare with `spbits gen`)
//   spp_selftest --plan N K ETA M SEED SHIRE_MASK PER_SHIRE [SLICE_I SLICE_N]   M1's built-in plan and M1's model
//                                         (sparseparity_host --dry prints M4's plan and the fitted model's time)
//   spp_selftest --tie-instance FILE [M]  write the tie instance (C0's shape, two candidates at c = m) as SPI1; M
//                                         samples (default 128; 256 or more streams A)
//   spp_selftest --bench-oracle N K ETA M TILES   the CPU oracle's speed (words popcounted per second)
//   spp_selftest --pipe-table N K M NBUF GEN_INC EPI_HIDE ABUF3 [U]   the fitted pipeline's cycles per row tile by
//                                         column tiles (tools/cycle_model.py table prints the same numbers)
// 1. colex rank/unrank round trips; the closed-form J0 runs against a row-by-row walk; sp.h's row count;
// 2. both closed-form checksums against brute force over all C(n,k) subsets;
// 3. plans (several shire masks, minions and rounds): every row tile in exactly one block, candidates counted in
//    closed form equal C(n,k), and the plan-order oracle's sum, sum of squares, count, argmax and tie flag equal
//    brute force;
// 4. the argmax tie rule (smallest colex rank, and the tie flag, within one Acc and across merged ones) and the
//    secret found at a noise level the model says is easy;
// 5. M4: plans cut by the fitted pipeline's costs cover every tile once with the same oracle; the C++ pipeline
//    model equals tools/cycle_model.py's (its table at L1, L2 and C1, M1's kernel and M4's) to 0.1%.
// 6. M5 (the two-stage screen): the m1-sample prefix of an instance equals the instance generated with m1 samples;
//    the plan-order survivor oracle (merged over minions) equals brute force's survivor set; stage 2 on those
//    survivors finds brute force's best among them on all m samples and flags corrupted entries; the screen's
//    probabilities equal design_model.py's.
//   spp_selftest --bench-stage2 N K ETA M M1 NSURV THREADS   stage 2's speed on NSURV random valid entries in the
//                                         kernel's order (ns per survivor and 64-sample word)
#include <chrono>
#include <random>
#include <thread>
#include <cstdio>
#include <cstdlib>
#include <string>

#include "spp_common.h"

using namespace spp;

static int fails = 0;
#define CHECK(cond, ...)                   \
  do {                                     \
    if (!(cond)) {                         \
      ++fails;                             \
      std::printf("FAIL: " __VA_ARGS__);   \
      std::printf("\n");                   \
    }                                      \
  } while (0)

// Brute force over all k-subsets in colex order.
static Acc brute(const Instance& I) {
  Acc a;
  std::vector<int> T(I.k);
  for (int i = 0; i < I.k; ++i) T[i] = i;
  const uint64_t N = binom64(I.n, I.k);
  for (uint64_t r = 0; r < N; ++r) {
    CHECK(rankOf(T) == r, "rankOf mismatch at %llu", (unsigned long long)r);
    // direct: count disagreements sample by sample
    int c = 0;
    for (int i = 0; i < I.m; ++i) {
      int b = I.ybit(i);
      for (int f : T) b ^= I.Xbit(f, i);
      c += b ? -1 : 1;
    }
    a.add(c, r);
    colexNext(T);
  }
  return a;
}

// M5: the survivors of the first m1 samples by brute force (c1 >= tau1), sorted by colex key.
static std::vector<uint64_t> bruteSurvivors(const Instance& I1, int tau1) {
  std::vector<uint64_t> out;
  std::vector<int> T(I1.k);
  for (int i = 0; i < I1.k; ++i) T[i] = i;
  const uint64_t N = binom64(I1.n, I1.k);
  for (uint64_t r = 0; r < N; ++r) {
    const int32_t c = scoreSubset(I1, T);
    if (c >= tau1) out.push_back(survPack(r - binom64(T.back(), I1.k), uint32_t(T.back()), c));
    colexNext(T);
  }
  std::sort(out.begin(), out.end(), [](uint64_t a, uint64_t b) { return survKey(a) < survKey(b); });
  return out;
}

static void checkScreen(int n, int k, double eta, int m, int m1, int tau1, uint64_t seed) {
  const Instance F = generate(n, k, eta, m, seed);
  const Instance I1 = prefixInstance(F, m1), G1 = generate(n, k, eta, m1, seed);
  CHECK(I1.X == G1.X && I1.y == G1.y && I1.secret == G1.secret && instHash(I1) == instHash(G1),
        "prefix (%d,%d,%g,%d) to m1 = %d differs from the instance generated with m1", n, k, eta, m, m1);
  const std::vector<uint64_t> want = bruteSurvivors(I1, tau1);
  const Geometry G(I1);
  std::vector<uint64_t> got;
  for (uint64_t mask : {0x1ull, 0x5ull}) {
    const Plan P = makePlan(G, mask, 3, 2, 0, G.workTiles);
    got.clear();
    Acc merged;
    for (int g : P.activeSlots()) {
      Acc a;
      std::vector<uint64_t> sv;
      scoreBlocks(I1, G, P.slots[g], a, nullptr, false, &sv, tau1);
      for (size_t q = 1; q < sv.size(); ++q)  // the kernel's order: row tile, then column tile, row, column
        CHECK(survRow(sv[q]) / 16 >= survRow(sv[q - 1]) / 16 || P.slots[g].size() > 1, "survivor order in slot %d", g);
      got.insert(got.end(), sv.begin(), sv.end());
      merged.merge(a);
    }
    std::sort(got.begin(), got.end(), [](uint64_t a, uint64_t b) { return survKey(a) < survKey(b); });
    CHECK(got == want, "survivors (%d,%d,%g,m1=%d,tau1=%d) mask %llx: plan oracle %zu, brute force %zu", n, k, eta, m1,
          tau1, (unsigned long long)mask, got.size(), want.size());
  }
  // stage 2 over the survivors: brute force's best among them on all m samples; every entry passes
  Stage2 s2;
  stage2Range(F, m1, tau1, want.data(), want.size(), s2);
  Acc best;
  for (uint64_t e : want) {
    std::vector<int> T = unrank(survRow(e), k - 1);
    T.push_back(int(survJ(e)));
    best.add(scoreSubset(F, T), rankOf(T));
  }
  CHECK(s2.bad == 0 && s2.entries == want.size() && s2.acc.best == best.best && s2.acc.bestRank == best.bestRank &&
            s2.acc.tie == best.tie,
        "stage 2 (%d,%d,m=%d,m1=%d): bad %llu, best %d@%llu vs %d@%llu", n, k, m, m1, (unsigned long long)s2.bad,
        s2.acc.best, (unsigned long long)s2.acc.bestRank, best.best, (unsigned long long)best.bestRank);
  const uint64_t sr = rankOf(F.secret);
  bool secretIn = false;
  for (uint64_t e : want) secretIn |= survRow(e) + binom64(survJ(e), k) == sr;
  CHECK(s2.secretIn == secretIn, "stage 2's secret flag");
  // corrupted entries are flagged: c1 off by 2, j at max(R), a row past the last
  if (!want.empty()) {
    const uint64_t e = want[want.size() / 2];
    std::vector<int> R = unrank(survRow(e), k - 1);
    const uint64_t bad[3] = {survPack(survRow(e), survJ(e), survC1(e) + 2),
                             k > 1 ? survPack(survRow(e), uint32_t(R.back()), survC1(e)) : survPack(survRow(e), survJ(e), survC1(e) - 2),
                             survPack(binom64(n - 1, k - 1), survJ(e), survC1(e))};
    Stage2 b;
    stage2Range(F, m1, tau1, bad, 3, b);
    CHECK(b.bad == 3, "stage 2 flags %llu of 3 corrupted entries", (unsigned long long)b.bad);
  }
  std::printf("ok screen (%d,%d,%g,m=%d) m1=%d tau1=%d: prefix = generated; %zu survivors, plan oracle = brute "
              "force; stage 2 best %d (secret %s)\n",
              n, k, eta, m, m1, tau1, want.size(), s2.acc.best, secretIn ? "kept" : "lost");
}

static void checkInstance(int n, int k, double eta, int m, uint64_t seed) {
  const Instance I = generate(n, k, eta, m, seed);
  const Geometry G(I);
  // 1. ranks and the J0 runs; rows are the (k-1)-subsets of 0..n-2 (cpu/sp.h), and every row tile has candidates
  CHECK(G.nrows == binom64(n - 1, k - 1) && G.workTiles == G.ntiles, "geometry: rows %llu, work tiles %llu of %llu",
        (unsigned long long)G.nrows, (unsigned long long)G.workTiles, (unsigned long long)G.ntiles);
  for (uint64_t r = 0; r < std::min<uint64_t>(G.nrows, 5000); r += 7) {
    CHECK(rankOf(unrank(r, k - 1)) == r, "unrank(%llu,%d)", (unsigned long long)r, k - 1);
  }
  {
    std::vector<int> R = unrank(0, k - 1);
    for (uint64_t t = 0; t < G.ntiles; ++t) {
      const int p = k > 1 ? R[k - 2] : -1;
      CHECK(G.J0(t) == ((p + 1) >> 4), "J0(%llu) = %d, walk says %d (n=%d k=%d)", (unsigned long long)t, G.J0(t),
            (p + 1) >> 4, n, k);
      for (int i = 0; i < 16; ++i) colexNext(R);
    }
  }
  // 2. closed forms against brute force
  const Acc B = brute(I);
  __int128 s1;
  unsigned __int128 s2;
  closedForms(I, s1, s2);
  CHECK(B.count == G.ncand, "brute count %llu != C(n,k) %llu", (unsigned long long)B.count,
        (unsigned long long)G.ncand);
  CHECK(s1 == B.sum, "sum c: closed form %s, brute %s (n=%d k=%d m=%d)", i128(s1).c_str(), i128(B.sum).c_str(), n, k,
        m);
  CHECK(s2 == B.sq, "sum c^2: closed form %s, brute %s (n=%d k=%d m=%d)", i128(__int128(s2)).c_str(),
        i128(__int128(B.sq)).c_str(), n, k, m);
  // 3. plans (M1's cost, and the fitted pipeline's for M4's kernel)
  const uint64_t masks[] = {0x1, 0x3, 0x80000001ull, 0xF0F0};
  const int pers[] = {1, 3, 32};
  const TileCost fit = pipeTileCost(G, pipeVariant(true, true, false), 2, false, 0.58);
  for (int cf = 0; cf < 2; ++cf)
  for (uint64_t mask : masks)
    for (int per : pers)
      for (int rounds : {1, 4}) {
        const Plan P = makePlan(G, mask, per, rounds, 0, G.workTiles, cf ? fit : TileCost{});
        std::vector<int> seen(G.ntiles, 0);
        Acc A;
        uint64_t cand = 0;
        for (int g : P.activeSlots()) {
          for (const Block& b : P.slots[g])
            for (uint64_t t = b.tile0; t < b.tile0 + b.ntiles; ++t) {
              CHECK(t < G.ntiles, "tile %llu out of range", (unsigned long long)t);
              if (t < G.ntiles) ++seen[t];
            }
          scoreBlocks(I, G, P.slots[g], A);
          cand += countCandidates(G, P.slots[g]);
        }
        for (int g = 0; g < int(SPP_MINION_SLOTS); ++g) {
          const int s = g / 32, mi = g % 32;
          if (!((mask >> s) & 1) || mi >= per) CHECK(P.slots[g].empty(), "inactive slot %d has blocks", g);
        }
        bool once = true;
        for (uint64_t t = 0; t < G.ntiles; ++t) once &= seen[t] == (t < G.workTiles ? 1 : 0);
        CHECK(once, "plan mask=%llx per=%d rounds=%d does not cover every tile once", (unsigned long long)mask, per,
              rounds);
        CHECK(cand == G.ncand, "plan candidates %llu != %llu", (unsigned long long)cand,
              (unsigned long long)G.ncand);
        CHECK(A.count == B.count && A.sum == B.sum && A.sq == B.sq && A.best == B.best && A.bestRank == B.bestRank &&
                  A.tie == B.tie,
              "plan oracle != brute force (mask=%llx per=%d rounds=%d)", (unsigned long long)mask, per, rounds);
        // the per-minion Accs merged (as the host merges hart records) = brute force, tie flag included
        Acc M;
        for (int g : P.activeSlots()) {
          Acc a;
          scoreBlocks(I, G, P.slots[g], a);
          M.merge(a);
        }
        CHECK(M.count == B.count && M.sum == B.sum && M.best == B.best && M.bestRank == B.bestRank && M.tie == B.tie,
              "merged per-minion oracle != brute force (mask=%llx per=%d rounds=%d)", (unsigned long long)mask, per,
              rounds);
      }
  // 3b. host-side slices (sliceRange) are positional: slice i is equal-cost block i of N, the slices tile
  // [0, workTiles) in order, and an empty block (one row tile costing more than a slice's share) stays in its place
  // (review of M4, finding 7). N up to 4x the row tiles forces empty blocks.
  for (int cf = 0; cf < 2; ++cf)
    for (uint64_t N : {uint64_t(2), uint64_t(3), uint64_t(7), G.workTiles, 4 * G.workTiles + 1}) {
      const std::vector<Block> cut = cutBlocks(G, N, 0, G.workTiles, cf ? fit : TileCost{});
      CHECK(cut.size() == N, "cutBlocks: %zu blocks for N = %llu", cut.size(), (unsigned long long)N);
      uint64_t next = 0, empty = 0;
      for (uint64_t i = 0; i < N; ++i) {
        uint64_t a = 0, b = 0;
        sliceRange(G, int(i), int(N), a, b, cf ? fit : TileCost{});
        CHECK(a == next && b >= a && a == cut[i].tile0 && b == cut[i].tile0 + cut[i].ntiles,
              "slice %llu/%llu = [%llu, %llu), expected from %llu", (unsigned long long)i, (unsigned long long)N,
              (unsigned long long)a, (unsigned long long)b, (unsigned long long)next);
        empty += b == a;
        next = b;
      }
      CHECK(next == G.workTiles, "slices of N = %llu end at %llu of %llu", (unsigned long long)N,
            (unsigned long long)next, (unsigned long long)G.workTiles);
      if (N > G.workTiles) CHECK(empty >= N - G.workTiles, "N = %llu: %llu empty slices", (unsigned long long)N,
                                 (unsigned long long)empty);
    }
  // 4. the answer
  if (eta <= 0.1 && m >= 96) {
    const std::vector<int> T = unrank(B.bestRank, k);
    CHECK(T == I.secret, "secret not recovered at (n=%d k=%d eta=%.2f m=%d seed=%llu)", n, k, eta, m,
          (unsigned long long)seed);
  }
  std::printf("ok n=%d k=%d eta=%.2f m=%d seed=%llu: C(n,k)=%llu rows=%llu tiles=%llu best c=%d rank=%llu "
              "sum=%s sumsq=%s hash=%016llx\n",
              n, k, eta, m, (unsigned long long)seed, (unsigned long long)G.ncand, (unsigned long long)G.nrows,
              (unsigned long long)G.ntiles, B.best, (unsigned long long)B.bestRank, i128(B.sum).c_str(),
              i128(__int128(B.sq)).c_str(), (unsigned long long)instHash(I));
}

// The tie instance: C0's shape with no noise and one feature duplicated from a secret feature, so two candidates
// score c = m (the secret and its twin); the answer is the one of smaller colex rank and it is not unique.
static Instance tieInstance(int m = 128) {
  Instance I = generate(32, 3, 0.0, m, 1);
  const int b = I.secret[2];
  int dup = -1;
  for (int f = 0; f < I.n && dup < 0; ++f)
    if (f != I.secret[0] && f != I.secret[1] && f != b) dup = f;
  for (int w = 0; w < I.W; ++w) I.X[size_t(dup) * I.W + w] = I.X[size_t(b) * I.W + w];
  return I;
}

int main(int argc, char** argv) {
  if ((argc == 3 || argc == 4) && std::string(argv[1]) == "--tie-instance") {
    const Instance I = tieInstance(argc == 4 ? std::atoi(argv[3]) : 128);
    saveInstance(argv[2], I);
    const Acc B = brute(I);
    std::printf("tie instance %s: best c %d at rank %llu, tie %d\n", argv[2], B.best, (unsigned long long)B.bestRank,
                int(B.tie));
    return B.tie ? 0 : 1;
  }
  if (argc == 7 && std::string(argv[1]) == "--bench-oracle") {
    const Instance I = generate(std::atoi(argv[2]), std::atoi(argv[3]), std::atof(argv[4]), std::atoi(argv[5]), 1);
    const Geometry G(I);
    const uint64_t nt = std::min<uint64_t>(std::strtoull(argv[6], nullptr, 0), G.workTiles);
    const std::vector<Block> bl = {{0, nt}};
    Acc a;
    const auto t0 = std::chrono::steady_clock::now();
    scoreBlocks(I, G, bl, a);
    const double s = std::chrono::duration<double>(std::chrono::steady_clock::now() - t0).count();
    const double words = double(countOutputTiles(G, bl)) * 256.0 * G.S;
    std::printf("oracle n=%d k=%d m=%d S=%d tiles=%llu: %.3g words in %.3f s = %.3g words/s (candidates %llu)\n", I.n,
                I.k, I.m, G.S, (unsigned long long)nt, words, s, words / s, (unsigned long long)a.count);
    return 0;
  }
  if (argc == 9 && std::string(argv[1]) == "--bench-stage2") {
    // NSURV random valid entries (rows ascending, as a minion logs them), their c1 exact; then stage 2 timed
    const Instance F = generate(std::atoi(argv[2]), std::atoi(argv[3]), std::atof(argv[4]), std::atoi(argv[5]), 1);
    const int m1 = std::atoi(argv[6]), nt = std::max(1, std::atoi(argv[8]));
    const Instance I1 = prefixInstance(F, m1);
    const uint64_t ns = std::strtoull(argv[7], nullptr, 0), nrows = binom64(F.n - 1, F.k - 1);
    std::mt19937_64 rng(7);
    std::vector<uint64_t> rows(ns);
    for (auto& r : rows) r = rng() % nrows;
    std::sort(rows.begin(), rows.end());
    std::vector<uint64_t> e(ns);
    std::vector<uint64_t> P(size_t(I1.W));
    for (uint64_t q = 0; q < ns; ++q) {
      const std::vector<int> R = unrank(rows[q], F.k - 1);
      const int lo = R.empty() ? 0 : R.back() + 1;
      rowBits(I1, R, P.data());
      int j = lo, c = 0;
      for (int tries = 0; tries < 64; ++tries) {  // a positive c1, as a survivor has
        j = lo + int(rng() % uint64_t(F.n - lo));
        if ((c = corr(I1, P.data(), j)) >= 1) break;
      }
      e[q] = survPack(rows[q], uint32_t(j), std::max(1, c));
    }
    std::vector<Stage2> part(static_cast<size_t>(nt));
    const auto t0 = std::chrono::steady_clock::now();
    std::vector<std::thread> th;
    for (int t = 0; t < nt; ++t)
      th.emplace_back([&, t]() {
        const uint64_t a = ns * uint64_t(t) / uint64_t(nt), b = ns * uint64_t(t + 1) / uint64_t(nt);
        stage2Range(F, m1, -4096, e.data() + a, size_t(b - a), part[size_t(t)]);
      });
    for (auto& t : th) t.join();
    const double sec = std::chrono::duration<double>(std::chrono::steady_clock::now() - t0).count();
    uint64_t bad = 0;
    for (const auto& p : part) bad += p.bad;
    std::printf("stage2 n=%d k=%d m=%d W=%d m1=%d survivors=%llu threads=%d: %.4f s = %.1f ns per survivor, %.3f ns "
                "per survivor-word x threads (bad entries %llu)\n",
                F.n, F.k, F.m, F.W, m1, (unsigned long long)ns, nt, sec, sec / double(ns) * 1e9,
                sec / double(ns) / F.W * 1e9 * nt, (unsigned long long)bad);
    return 0;
  }
  if ((argc == 9 || argc == 10) && std::string(argv[1]) == "--pipe-table") {
    const Instance I = generate(std::atoi(argv[2]), std::atoi(argv[3]), 0.1, std::atoi(argv[4]), 1);
    const Geometry G(I);
    const int nbuf = std::atoi(argv[5]);
    const PipeConst P = pipeVariant(std::atoi(argv[6]) != 0, std::atoi(argv[7]) != 0, std::atoi(argv[8]) != 0 && G.S > 3);
    const double U = argc == 10 ? std::atof(argv[9]) : 0.58;
    std::printf("{\"n\": %d, \"k\": %d, \"m\": %d, \"S\": %d, \"nbuf\": %d, \"U\": %g, \"cycles_per_row_tile\": {", I.n,
                I.k, I.m, G.S, nbuf, U);
    for (int nout = 1; nout <= G.nJ; ++nout)
      std::printf("%s\"%d\": %.1f", nout > 1 ? ", " : "", nout,
                  pipeSteady(nout, G.S, I.k - 1, G.S <= 3, nbuf, 1, false, U, P));
    std::printf("}}\n");
    return 0;
  }
  if (argc == 7 && std::string(argv[1]) == "--hash") {
    const Instance I = generate(std::atoi(argv[2]), std::atoi(argv[3]), std::atof(argv[4]), std::atoi(argv[5]),
                                std::strtoull(argv[6], nullptr, 0));
    std::printf("hash %016llx secret", (unsigned long long)instHash(I));
    for (int s : I.secret) std::printf(" %d", s);
    std::printf("\n");
    return 0;
  }
  if (argc >= 9 && std::string(argv[1]) == "--plan") {
    // spp_selftest --plan N K ETA M SEED SHIRE_MASK PER_SHIRE [SLICE_I SLICE_N]: the built-in plan's size and
    // modelled times (the numbers sparseparity_host --dry prints), with no device and no runtime library.
    const Instance I = generate(std::atoi(argv[2]), std::atoi(argv[3]), std::atof(argv[4]), std::atoi(argv[5]),
                                std::strtoull(argv[6], nullptr, 0));
    const Geometry G(I);
    const uint64_t mask = std::strtoull(argv[7], nullptr, 0);
    const int per = std::atoi(argv[8]);
    const int si = argc >= 11 ? std::atoi(argv[9]) : 0, sn = argc >= 11 ? std::atoi(argv[10]) : 1;
    if (sn < 1 || si < 0 || si >= sn) {
      std::fprintf(stderr, "--plan: slice I/N with 0 <= I < N\n");
      return 2;
    }
    uint64_t t0 = 0, t1 = G.workTiles;
    sliceRange(G, si, sn, t0, t1);
    const Plan P = makePlan(G, mask, per, 4, t0, t1);
    double mx = 0, sum = 0, est = 0;
    uint64_t ops = 0, cand = 0, opsMax = 0;
    for (int g : P.activeSlots()) {
      const double c = modelCycles(G, P.slots[g]);
      mx = std::max(mx, c);
      sum += c;
      est = std::max(est, estCycles(G, P.slots[g]));
      const uint64_t o = countOps(G, P.slots[g]);
      ops += o;
      opsMax = std::max(opsMax, o);
      cand += countCandidates(G, P.slots[g]);
    }
    const double nact = double(P.activeSlots().size());
    std::printf("plan n=%d k=%d m=%d S=%d mask=%s per=%d slice=%d/%d tiles=[%llu,%llu) candidates=%llu ops=%llu "
                "ops_max=%llu model_s=%.4f est_s=%.4f imbalance=%.4f scalar_1hart_s=%.3f\n",
                I.n, I.k, I.m, G.S, argv[7], per, si, sn, (unsigned long long)t0, (unsigned long long)t1,
                (unsigned long long)cand, (unsigned long long)ops, (unsigned long long)opsMax, mx / 600e6,
                est / 600e6, mx / (sum / nact), double(cand) / nact * (24.0 * G.S + 40.0) / 600e6);
    return 0;
  }
  // 5. the C++ pipeline model against tools/cycle_model.py table (29 September FITTED; values printed by
  //    `cycle_model.py table --n N --k K --m M --nbuf B [--variant m4 [--abuf 3]]`, U = 0.58, scratchpad staging)
  {
    struct Ref {
      int n, k, m, nbuf;
      bool m4, abuf3;
      int nout;
      double cyc;
    };
    const Ref refs[] = {{512, 4, 448, 2, false, false, 1, 37272.5},    {512, 4, 448, 2, false, false, 8, 53156.2},
                        {512, 4, 448, 2, false, false, 32, 156611.4},  {512, 4, 448, 2, true, false, 1, 23044.2},
                        {512, 4, 448, 2, true, false, 32, 97088.2},    {512, 4, 1850, 1, false, false, 1, 147082.9},
                        {512, 4, 1850, 1, false, false, 32, 543167.1}, {512, 4, 1850, 1, true, false, 8, 170050.4},
                        {512, 4, 1850, 1, true, true, 32, 364615.8},   {128, 4, 192, 2, true, false, 8, 24398.7}};
    for (const Ref& r : refs) {
      const int S = (r.m + 63) / 64;
      const double c = pipeSteady(r.nout, S, r.k - 1, S <= 3, r.nbuf, 1, false, 0.58,
                                  pipeVariant(r.m4, r.m4, r.abuf3 && S > 3));
      CHECK(std::fabs(c / r.cyc - 1) < 1e-3, "pipeline model (%d,%d,%d) nbuf %d %s nout %d: %.1f, cycle_model.py %.1f",
            r.n, r.k, r.m, r.nbuf, r.m4 ? (r.abuf3 ? "m4 abuf3" : "m4") : "m1", r.nout, c, r.cyc);
    }
    std::printf("ok pipeline model = cycle_model.py on %zu table entries\n", sizeof(refs) / sizeof(refs[0]));
  }
  checkInstance(32, 3, 0.1, 128, 1);   // C0
  checkInstance(12, 3, 0.2, 20, 7);
  checkInstance(16, 4, 0.1, 37, 3);
  checkInstance(10, 5, 0.3, 9, 5);
  checkInstance(20, 1, 0.1, 40, 2);    // k = 1: one row, the empty subset
  checkInstance(40, 2, 0.1, 100, 4);   // n not a multiple of 16
  checkInstance(48, 3, 0.1, 256, 9);   // S = 4: the streamed-A path
  checkInstance(37, 4, 0.1, 200, 11);
  checkInstance(24, 6, 0.1, 150, 13);
  // 6. M5: the two-stage screen's host side
  checkScreen(24, 3, 0.2, 300, 128, 20, 3);
  checkScreen(40, 4, 0.1, 400, 192, 40, 5);   // n not a multiple of 16; S1 = 3 (A resident)
  checkScreen(20, 5, 0.3, 260, 100, 16, 2);   // m1 not a multiple of 64
  checkScreen(30, 2, 0.4, 700, 640, 50, 4);
  checkScreen(20, 1, 0.1, 90, 64, 8, 2);      // k = 1
  checkScreen(48, 3, 0.1, 256, 256, 70, 9);   // m1 = m
  {
    // design_model.py screen_at(512, 4, 0.4, 1024, 104): P(kept) 0.9993796315265675, E[survivors] 1806172.x
    const double pk = screenKept(1024, 104, 0.4), E = screenNull(1024, 104) * double(binom64(512, 4));
    CHECK(std::fabs(pk - 0.9993796315265675) < 1e-9 && std::fabs(E / 1806172.0 - 1) < 1e-5,
          "screen probabilities: kept %.12f, E %.1f", pk, E);
    std::printf("ok screen probabilities = design_model.py (L2, m1 = 1024, tau1 = 104: kept %.6f, E %.0f)\n", pk, E);
  }
  // A tie: two identical features make two candidates score the same; the smaller colex rank must win.
  {
    Instance I = generate(20, 2, 0.0, 64, 21);
    const int a = I.secret[0], b = I.secret[1];
    const int dup = (b + 1) % 20 == a ? (b + 2) % 20 : (b + 1) % 20;
    for (int w = 0; w < I.W; ++w) I.X[size_t(dup) * I.W + w] = I.X[size_t(b) * I.W + w];
    const Acc B = brute(I);
    std::vector<int> T1 = {a, b}, T2 = {std::min(a, dup), std::max(a, dup)};
    std::sort(T1.begin(), T1.end());
    const uint64_t r1 = rankOf(T1), r2 = rankOf(T2);
    CHECK(B.best == I.m && B.bestRank == std::min(r1, r2) && B.tie, "tie rule: best rank %llu, expected %llu",
          (unsigned long long)B.bestRank, (unsigned long long)std::min(r1, r2));
    // split across two Accs (each holds one of the pair): the merge must flag the tie
    const Geometry G(I);
    const Plan P = makePlan(G, 0x3, 32, 1, 0, G.workTiles);
    Acc M;
    int holders = 0;
    for (int g : P.activeSlots()) {
      Acc a;
      scoreBlocks(I, G, P.slots[g], a);
      holders += a.count && a.best == I.m;
      M.merge(a);
    }
    CHECK(M.best == I.m && M.bestRank == B.bestRank && M.tie, "tie across merged Accs (%d holders)", holders);
    const Acc T = brute(tieInstance());
    CHECK(T.best == 128 && T.tie, "the sys_emu tie instance has a tie at c = m");
    std::printf("ok tie rule: ranks %llu and %llu score %d, best rank %llu\n", (unsigned long long)r1,
                (unsigned long long)r2, B.best, (unsigned long long)B.bestRank);
  }
  // Planner balance on a ladder size (no scoring): max over minions of modelled cycles vs the mean.
  {
    const Instance I = generate(512, 4, 0.4, 1850, 1);
    const Geometry G(I);
    for (int rounds : {1, 4}) {
      const Plan P = makePlan(G, 0xFFFFFFFFull, 32, rounds, 0, G.workTiles);
      double mx = 0, sum = 0;
      uint64_t cand = 0;
      const auto act = P.activeSlots();
      for (int g : act) {
        const double c = modelCycles(G, P.slots[g]);
        mx = std::max(mx, c);
        sum += c;
        cand += countCandidates(G, P.slots[g]);
      }
      CHECK(cand == G.ncand, "L2 plan candidates %llu != %llu", (unsigned long long)cand,
            (unsigned long long)G.ncand);
      std::printf("ok L2 (512,4,0.4,1850) plan rounds=%d: %zu minions, max/mean modelled cycles %.4f, "
                  "max %.3g cycles = %.3f s at 600 MHz\n",
                  rounds, act.size(), mx / (sum / double(act.size())), mx, mx / 600e6);
    }
  }
  // M4's planner at L1 on 32 x 32 minions: every minion's row tiles simulated in the fitted pipeline model. M1's
  // plan (M1's cost) with M1's kernel is M3's run (0.204 s measured, busiest 1.55x the mean); the fitted cost must
  // balance it (under 1.02) with M1's kernel and with M4's.
  {
    const Instance I = generate(512, 4, 0.3, 448, 1);
    const Geometry G(I);
    auto simPlan = [&](const Plan& P, const PipeConst& pc, double& imb) {
      double mx = 0, sum = 0;
      int nb = 0;
      for (int g : P.activeSlots()) {
        const double c = pipeSimMinion(blocksRle(G, P.slots[g]), G.S, 3, false, 2, 1, false, 0.58, 5000, pc).cycles;
        mx = std::max(mx, c);
        sum += c;
        ++nb;
      }
      imb = mx / (sum / nb);
      return mx / 600e6;
    };
    for (int v = 0; v < 2; ++v) {
      const PipeConst pc = pipeVariant(v == 1, v == 1, false);
      double imbM1 = 0, imbFit = 0;
      const double tM1 = simPlan(makePlan(G, 0xFFFFFFFFull, 32, 4, 0, G.workTiles), pc, imbM1);
      const double tFit = simPlan(makePlan(G, 0xFFFFFFFFull, 32, 4, 0, G.workTiles, pipeTileCost(G, pc, 2, false, 0.58)),
                                  pc, imbFit);
      CHECK(imbFit < 1.02 && imbM1 > 1.3, "L1 %s kernel: fitted plan max/mean %.3f, M1's plan %.3f", v ? "m4" : "m1",
            imbFit, imbM1);
      std::printf("ok L1 (512,4,0.3,448) on 32 x 32, %s kernel (model, U = 0.58): M1's plan %.1f ms (max/mean %.3f), "
                  "fitted plan %.1f ms (max/mean %.3f)\n",
                  v ? "M4" : "M1", tM1 * 1e3, imbM1, tFit * 1e3, imbFit);
    }
  }
  std::printf(fails ? "SELFTEST FAIL (%d)\n" : "SELFTEST PASS\n", fails);
  return fails ? 1 : 0;
}
