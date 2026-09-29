// Review R (M4): exhaustive coverage of the host's plans (M1 and fitted costs, slices) and an emulation of the
// kernel's SPP_F_GEN_INC row construction against rowBits. CPU only.
// R3's program, with its two emulations of main.cpp's old sliceRange replaced by spp_common.h's positional one.
//   g++ -O2 -std=c++17 -I<src>/workloads/sparseparity -I<src>/workloads/sparseparity/host cov_check.cpp
#include <cstdio>
#include <random>
#include <set>
#include "spp_common.h"
using namespace spp;

static int fails = 0;
#define CHECK(c, ...)                         \
  do {                                        \
    if (!(c)) {                               \
      if (++fails <= 30) {                    \
        std::printf("FAIL %s:%d ", __FILE__, __LINE__); \
        std::printf(__VA_ARGS__);             \
        std::printf("\n");                    \
      }                                       \
    }                                         \
  } while (0)

// The kernel's sub_next on uint64 (identical logic).
static void sub_next(uint64_t* r, uint64_t k1) {
  for (uint64_t e = 0; e < k1; ++e) {
    if (e + 1 == k1 || r[e] + 1 < r[e + 1]) {
      ++r[e];
      for (uint64_t f = 0; f < e; ++f) r[f] = f;
      return;
    }
  }
}

// Transliteration of run_gen_inc's row build for one tile: rows' words p[i][s] for valid rows.
static void gen_inc_tile(const Instance& I, const std::vector<uint64_t>& XT, uint64_t* r, uint64_t& rank,
                         uint64_t nrows, std::vector<uint64_t>& out /* 16*S */, uint64_t& nvalid_out) {
  const uint64_t k1 = I.k - 1, S = I.W, n = I.n;
  struct GenRun { uint32_t row0, len; uint64_t off; uint16_t pre[SPP_KMAX - 2]; } runs[16];
  uint64_t nvalid = 0, nruns = 0;
  for (uint64_t i = 0; i < 16; ++i, ++rank) {
    if (rank < nrows) {
      if (nruns == 0 || r[0] != runs[nruns - 1].off + runs[nruns - 1].len) {
        GenRun* u = &runs[nruns++];
        u->row0 = uint32_t(i);
        u->len = 1;
        u->off = r[0];
        for (uint64_t e = 1; e < k1; ++e) u->pre[e - 1] = uint16_t(r[e]);
      } else {
        ++runs[nruns - 1].len;
      }
      sub_next(r, k1);
      ++nvalid;
    }
  }
  out.assign(16 * S, 0xDEADBEEFDEADBEEFull);
  if (nruns == 1 && nvalid == 16) {
    const uint64_t off = runs[0].off;
    for (uint64_t s = 0; s < S; ++s) {
      const uint64_t* xs = XT.data() + s * n;
      uint64_t v = I.y[s];
      for (uint64_t e = 1; e < k1; ++e) v ^= xs[runs[0].pre[e - 1]];
      const uint64_t* xo = xs + off;
      CHECK(off + 15 < n, "common path reads past feature n-1: off %llu", (unsigned long long)off);
      for (uint64_t i = 0; i < 16; ++i) out[i * S + s] = v ^ xo[i];
    }
  } else {
    for (uint64_t s = 0; s < S; ++s) {
      const uint64_t* xs = XT.data() + s * n;
      uint64_t p[16];
      for (uint64_t i = nvalid; i < 16; ++i) p[i] = 0;
      for (uint64_t u = 0; u < nruns; ++u) {
        uint64_t v = I.y[s];
        for (uint64_t e = 1; e < k1; ++e) v ^= xs[runs[u].pre[e - 1]];
        CHECK(runs[u].off + runs[u].len <= n, "run past n");
        const uint64_t* xo = xs + runs[u].off;
        uint64_t* pp = p + runs[u].row0;
        for (uint64_t i = 0; i < runs[u].len; ++i) pp[i] = v ^ xo[i];
      }
      for (uint64_t i = 0; i < 16; ++i) out[i * S + s] = p[i];
    }
  }
  nvalid_out = nvalid;
}

static void check_gen_inc(int n, int k, int m, uint64_t seed) {
  const Instance I = generate(n, k, 0.2, m, seed);
  const Geometry G(I);
  const std::vector<uint64_t> XT = makeXT(I);
  const int k1 = k - 1;
  // every tile as a block start, and a contiguous walk from each start for 3 tiles
  for (uint64_t t0 = 0; t0 < G.ntiles; ++t0) {
    const std::vector<int> sub = unrank(16 * t0, k1);
    uint64_t r[SPP_KMAX] = {0};
    for (int e = 0; e < k1; ++e) r[e] = uint16_t(sub[e]);  // SppBlock.sub is uint16
    uint64_t rank = 16 * t0;
    std::vector<int> ref = sub;
    for (uint64_t t = t0; t < std::min<uint64_t>(G.ntiles, t0 + 3); ++t) {
      std::vector<uint64_t> out;
      uint64_t nvalid = 0;
      const uint64_t rank0 = rank;
      gen_inc_tile(I, XT, r, rank, G.nrows, out, nvalid);
      for (uint64_t i = 0; i < 16; ++i) {
        if (rank0 + i >= G.nrows) {
          CHECK(i >= nvalid, "padding row counted valid");
          continue;
        }
        std::vector<uint64_t> P(I.W);
        rowBits(I, ref, P.data());
        for (int s = 0; s < I.W; ++s)
          CHECK(out[i * I.W + s] == P[s], "gen_inc n=%d k=%d m=%d tile %llu row %llu slice %d", n, k, m,
                (unsigned long long)t, (unsigned long long)i, s);
        colexNext(ref);
      }
    }
  }
}

struct CostSpec {
  const char* name;
  bool m1;
  bool gi, eh, a3;
  int nbuf;
  bool dram;
  int epi;
};

static void check_plans(int n, int k, int m, std::mt19937_64& rng, uint64_t& nplans) {
  const Instance I = generate(n, k, 0.2, m, 1);
  const Geometry G(I);
  // exact candidate map for small C(n,k): every candidate exactly once over the row tiles
  const uint64_t NC = G.ncand;
  std::vector<CostSpec> costs = {{"m1", true, 0, 0, 0, 2, false, 1}};
  for (int gi = 0; gi < 2; ++gi)
    for (int eh = 0; eh < 2; ++eh)
      for (int a3 = 0; a3 < 2; ++a3)
        for (int nb = 1; nb <= 2; ++nb)
          for (int dr = 0; dr < 2; ++dr)
            for (int epi = 0; epi < 2; ++epi) costs.push_back({"fit", false, bool(gi), bool(eh), bool(a3), nb, bool(dr), epi});
  const std::vector<uint64_t> masks = {0x1, 0x3, 0x5, 0x80000001ull, 0xFFFFFFFFull, 0xAAAAAAAAull, rng() & 0xFFFFFFFFull | 1};
  const std::vector<int> pss = {1, 2, 3, 7, 32};
  for (const CostSpec& cs : costs) {
    for (uint64_t mask : masks) {
      for (int ps : pss) {
        // sample: not every combination (keep the run short)
        if ((rng() & 3) != 0) continue;
        for (int rounds : {1, 4}) {
          for (int nsl : {1, 2, 3, 7}) {
            TileCost cost;
            if (!cs.m1) {
              PipeConst P = pipeVariant(cs.gi, cs.eh, cs.a3 && G.S > 3);
              cost = pipeTileCost(G, P, cs.nbuf, cs.dram, pipePlanU(ps), cs.epi);
            }
            std::vector<uint8_t> seen(G.workTiles, 0);
            uint64_t cand = 0, prev_t1 = 0;
            for (int si = 0; si < nsl; ++si) {
              // sliceRange (main.cpp, static): n contiguous equal-cost blocks
              uint64_t t0 = 0, t1 = G.workTiles;
              sliceRange(G, si, nsl, t0, t1, cost);  // the host's (spp_common.h, positional)
              {
                CHECK(t0 == prev_t1, "slices not contiguous: slice %d starts at %llu, previous ended %llu", si,
                      (unsigned long long)t0, (unsigned long long)prev_t1);
                prev_t1 = t1;
              }
              const Plan plan = makePlan(G, mask, ps, rounds, t0, t1, cost);
              ++nplans;
              for (int g = 0; g < int(SPP_MINION_SLOTS); ++g) {
                const int sh = g / 32, mi = g % 32;
                const bool active = ((mask >> sh) & 1) && mi < ps;
                if (!active) {
                  CHECK(plan.slots[g].empty(), "blocks on an inactive slot %d", g);
                  continue;
                }
                for (const Block& b : plan.slots[g]) {
                  CHECK(b.ntiles > 0, "empty block on slot %d", g);
                  CHECK(b.tile0 >= t0 && b.tile0 + b.ntiles <= t1, "block outside the slice");
                  for (uint64_t t = b.tile0; t < b.tile0 + b.ntiles && t < G.workTiles; ++t) {
                    CHECK(seen[t] == 0, "tile %llu twice (n=%d k=%d cost %s mask %llx ps %d rounds %d slices %d)",
                          (unsigned long long)t, n, k, cs.name, (unsigned long long)mask, ps, rounds, nsl);
                    seen[t] = 1;
                  }
                }
                cand += countCandidates(G, plan.slots[g]);
              }
            }
            CHECK(prev_t1 == G.workTiles, "slices end at %llu of %llu", (unsigned long long)prev_t1,
                  (unsigned long long)G.workTiles);
            for (uint64_t t = 0; t < G.workTiles; ++t)
              CHECK(seen[t] == 1, "tile %llu missing (n=%d k=%d cost %s mask %llx ps %d rounds %d slices %d)",
                    (unsigned long long)t, n, k, cs.name, (unsigned long long)mask, ps, rounds, nsl);
            CHECK(cand == NC, "candidates %llu != C(n,k) %llu", (unsigned long long)cand, (unsigned long long)NC);
          }
        }
      }
    }
  }
}

// Every candidate exactly once through the kernel's tile walk (J0 from the first row, masks j > pmax, j < n).
static void check_tiling(int n, int k) {
  const Instance I = generate(n, k, 0.2, 64, 1);
  const Geometry G(I);
  const int k1 = k - 1;
  std::vector<uint8_t> hit(G.ncand, 0);
  uint64_t r[SPP_KMAX] = {0};
  const std::vector<int> sub = unrank(0, k1);
  for (int e = 0; e < k1; ++e) r[e] = sub[e];
  uint64_t rank = 0;
  for (uint64_t t = 0; t < G.ntiles; ++t) {
    int64_t pmax[16];
    uint64_t nvalid = 0;
    const uint64_t rank0 = rank;
    for (int i = 0; i < 16; ++i, ++rank) {
      pmax[i] = k1 ? int64_t(r[k1 - 1]) : -1;
      if (rank < G.nrows) {
        sub_next(r, k1);
        ++nvalid;
      }
    }
    const uint64_t J0 = uint64_t(pmax[0] + 1) >> 4;
    CHECK(int(J0) == G.J0(t), "J0 kernel %llu host %d", (unsigned long long)J0, G.J0(t));
    for (uint64_t J = J0; J < uint64_t(G.nJ); ++J)
      for (uint64_t i = 0; i < nvalid; ++i)
        for (int jj = 0; jj < 16; ++jj) {
          const int64_t j = 16 * J + jj;
          if (j <= pmax[i] || j >= n) continue;
          const uint64_t cr = rank0 + i + binom64(j, k);
          CHECK(cr < G.ncand, "rank out of range");
          if (cr < G.ncand) {
            CHECK(hit[cr] == 0, "candidate %llu twice", (unsigned long long)cr);
            hit[cr] = 1;
          }
        }
  }
  for (uint64_t c = 0; c < G.ncand; ++c) CHECK(hit[c] == 1, "candidate %llu missed (n=%d k=%d)", (unsigned long long)c, n, k);
}

int main() {
  std::mt19937_64 rng(12345);
  // tiling: every candidate once
  for (int k = 1; k <= 6; ++k)
    for (int n : {6, 7, 16, 17, 31, 32, 33, 40, 48, 64}) {
      if (n < k || binom64(n, k) > 20000000) continue;
      check_tiling(n, k);
    }
  std::printf("tiling done, fails %d\n", fails);
  // GEN_INC emulation
  for (int k = 2; k <= 6; ++k)
    for (int n : {6, 8, 16, 17, 21, 33, 40}) {
      if (n < k || binom64(n - 1, k - 1) > 200000) continue;
      for (int m : {1, 63, 64, 100, 256, 449}) check_gen_inc(n, k, m, 7 + n + k + m);
    }
  std::printf("gen_inc done, fails %d\n", fails);
  // plans
  uint64_t nplans = 0;
  for (int k = 1; k <= 6; ++k)
    for (int n : {6, 17, 33, 64, 100}) {
      if (n < k || binom64(n, k) > 5000000) continue;
      for (int m : {64, 256, 448}) check_plans(n, k, m, rng, nplans);
    }
  std::printf("plans done (%llu plans), fails %d\n", (unsigned long long)nplans, fails);
  // big geometries: L1, L2, (256,5) fitted plans on 32x32 and 1x32, slices
  {
    const int inst[3][3] = {{512, 4, 448}, {512, 4, 1850}, {256, 5, 1925}};
    for (const auto& in : inst) {
      const Instance I = generate(in[0], in[1], 0.4, in[2], 1);
      const Geometry G(I);
      for (int m4 = 0; m4 < 2; ++m4)
        for (uint64_t mask : {0x1ull, 0xFFFFFFFFull})
          for (int nsl : {1, 2, 3, 8, 16}) {
            PipeConst P = pipeVariant(m4, m4, false);
            const int nbuf = G.S <= 7 ? 2 : 1;
            const TileCost cost = pipeTileCost(G, P, nbuf, false, pipePlanU(32), 1);
            const TileCost m1c;
            std::vector<uint8_t> seen(G.workTiles, 0);
            uint64_t cand = 0;
            for (int si = 0; si < nsl; ++si) {
              uint64_t t0 = 0, t1 = G.workTiles;
              sliceRange(G, si, nsl, t0, t1, m1c);  // --slice-cost m1, the host's positional slices
              const Plan plan = makePlan(G, mask, 32, 1, t0, t1, cost);
              for (int g = 0; g < int(SPP_MINION_SLOTS); ++g)
                for (const Block& b : plan.slots[g]) {
                  for (uint64_t t = b.tile0; t < b.tile0 + b.ntiles; ++t) {
                    CHECK(!seen[t], "big: tile twice");
                    seen[t] = 1;
                  }
                  cand += countCandidates(G, {b});
                }
            }
            uint64_t miss = 0;
            for (uint64_t t = 0; t < G.workTiles; ++t) miss += !seen[t];
            CHECK(miss == 0 && cand == G.ncand, "big (%d,%d,%d) m4=%d mask %llx slices %d: missing %llu cand %llu/%llu",
                  in[0], in[1], in[2], m4, (unsigned long long)mask, nsl, (unsigned long long)miss,
                  (unsigned long long)cand, (unsigned long long)G.ncand);
          }
    }
  }
  std::printf("big done, fails %d\n", fails);
  std::printf(fails ? "COVERAGE FAIL\n" : "COVERAGE PASS\n");
  return fails ? 1 : 0;
}
