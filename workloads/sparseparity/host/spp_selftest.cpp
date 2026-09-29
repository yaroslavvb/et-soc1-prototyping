// CPU-only checks of the host's model of the scan (no device, no runtime library):
//   spp_selftest                          all checks below; exit 0 when all pass
//   spp_selftest --hash N K ETA M SEED    print the instance hash (compare with `spbits gen`)
//   spp_selftest --plan N K ETA M SEED SHIRE_MASK PER_SHIRE [SLICE_I SLICE_N]   the built-in plan's model
//   spp_selftest --tie-instance FILE      write the tie instance (C0's shape, two candidates at c = m) as SPI1
//   spp_selftest --bench-oracle N K ETA M TILES   the CPU oracle's speed (words popcounted per second)
// 1. colex rank/unrank round trips; the closed-form J0 runs against a row-by-row walk; sp.h's row count;
// 2. both closed-form checksums against brute force over all C(n,k) subsets;
// 3. plans (several shire masks, minions and rounds): every row tile in exactly one block, candidates counted in
//    closed form equal C(n,k), and the plan-order oracle's sum, sum of squares, count, argmax and tie flag equal
//    brute force;
// 4. the argmax tie rule (smallest colex rank, and the tie flag, within one Acc and across merged ones) and the
//    secret found at a noise level the model says is easy.
#include <chrono>
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
  // 3. plans
  const uint64_t masks[] = {0x1, 0x3, 0x80000001ull, 0xF0F0};
  const int pers[] = {1, 3, 32};
  for (uint64_t mask : masks)
    for (int per : pers)
      for (int rounds : {1, 4}) {
        const Plan P = makePlan(G, mask, per, rounds, 0, G.workTiles);
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
static Instance tieInstance() {
  Instance I = generate(32, 3, 0.0, 128, 1);
  const int b = I.secret[2];
  int dup = -1;
  for (int f = 0; f < I.n && dup < 0; ++f)
    if (f != I.secret[0] && f != I.secret[1] && f != b) dup = f;
  for (int w = 0; w < I.W; ++w) I.X[size_t(dup) * I.W + w] = I.X[size_t(b) * I.W + w];
  return I;
}

int main(int argc, char** argv) {
  if (argc == 3 && std::string(argv[1]) == "--tie-instance") {
    const Instance I = tieInstance();
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
    uint64_t t0 = 0, t1 = G.workTiles;
    if (sn > 1) {
      const Plan p = makePlan(G, 0x1, 1, sn, 0, G.workTiles);
      t0 = p.slots[0][si].tile0;
      t1 = t0 + p.slots[0][si].ntiles;
    }
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
  checkInstance(32, 3, 0.1, 128, 1);   // C0
  checkInstance(12, 3, 0.2, 20, 7);
  checkInstance(16, 4, 0.1, 37, 3);
  checkInstance(10, 5, 0.3, 9, 5);
  checkInstance(20, 1, 0.1, 40, 2);    // k = 1: one row, the empty subset
  checkInstance(40, 2, 0.1, 100, 4);   // n not a multiple of 16
  checkInstance(48, 3, 0.1, 256, 9);   // S = 4: the streamed-A path
  checkInstance(37, 4, 0.1, 200, 11);
  checkInstance(24, 6, 0.1, 150, 13);
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
  std::printf(fails ? "SELFTEST FAIL (%d)\n" : "SELFTEST PASS\n", fails);
  return fails ? 1 : 0;
}
