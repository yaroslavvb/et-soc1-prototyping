// Host-side pieces of the sparseparity workload that need no device: the instance generator (bit-identical to
// workloads/sparseparity/proto/spbits.c `gen`), the instance file, colex ranks, the row-tile model, the planner, the
// CPU oracle and the two closed-form checksums. Used by sparseparity_host and by spp_selftest (CPU only).
#pragma once
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <fstream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

#include "sparseparity_args.h"

namespace spp {

// ---------------------------------------------------------------- the generator (mirrors spbits.c / sp.py)

inline uint64_t mix64(uint64_t z) {
  z ^= z >> 30;
  z *= 0xbf58476d1ce4e5b9ULL;
  z ^= z >> 27;
  z *= 0x94d049bb133111ebULL;
  return z ^ (z >> 31);
}

inline uint64_t rnd(uint64_t seed, uint64_t stream, uint64_t idx) {
  const uint64_t key = mix64(seed * 0x9E3779B97F4A7C15ULL + stream * 0xD1B54A32D192ED03ULL + 0x632BE59BD9B4E019ULL);
  return mix64(key + idx * 0x9E3779B97F4A7C15ULL);
}

struct Instance {
  int n = 0, k = 0, m = 0, W = 0;  // W = ceil(m / 64) words per packed column (no padding words)
  double eta = 0;
  uint64_t seed = 0;
  std::vector<uint64_t> X;  // n * W, feature-major; bit b of word w = sample 64w + b; bits past m are zero
  std::vector<uint64_t> y;  // W
  std::vector<int> secret;  // sorted; empty when unknown
  bool Xbit(int f, int i) const { return (X[size_t(f) * W + i / 64] >> (i % 64)) & 1; }
  bool ybit(int i) const { return (y[i / 64] >> (i % 64)) & 1; }
};

// spbits `gen` with W = ceil(m/64): the same X, y and secret (spbits pads W with zero words on AVX-512 builds;
// the hash below ignores the padding, as spbits' does).
inline Instance generate(int n, int k, double eta, int m, uint64_t seed) {
  if (n < 1 || n > int(SPP_NMAX) || k < 1 || k > int(SPP_KMAX) || k > n || m < 1 || m > int(64 * SPP_SMAX)) {
    throw std::runtime_error("instance out of range: 1 <= k <= 6, k <= n <= 2048, 1 <= m <= 2560");
  }
  Instance I;
  I.n = n;
  I.k = k;
  I.m = m;
  I.eta = eta;
  I.seed = seed;
  I.W = (m + 63) / 64;
  const int W = I.W;
  const uint64_t last = (m % 64) ? ((1ULL << (m % 64)) - 1) : ~0ULL;
  I.X.assign(size_t(n) * W, 0);
  I.y.assign(W, 0);
  for (int j = 0; j < n; j++) {
    for (int w = 0; w < W; w++) {
      const uint64_t v = rnd(seed, 1, (uint64_t(j) << 32) | uint64_t(w));
      I.X[size_t(j) * W + w] = (w == W - 1) ? (v & last) : v;
    }
  }
  std::vector<int> idx(n);
  for (int j = 0; j < n; j++) idx[j] = j;
  for (int i = 0; i < k; i++) {
    const uint64_t r = rnd(seed, 3, i) % uint64_t(n - i);
    std::swap(idx[i], idx[i + r]);
  }
  I.secret.assign(idx.begin(), idx.begin() + k);
  std::sort(I.secret.begin(), I.secret.end());
  const uint64_t thr = uint64_t(eta * 9007199254740992.0);  // eta * 2^53
  for (int w = 0; w < W; w++) {
    uint64_t nz = 0;
    for (int b = 0; b < 64; b++) {
      const uint64_t s = uint64_t(w) * 64 + b;
      if (s >= uint64_t(m)) break;
      if ((rnd(seed, 2, s) >> 11) < thr) nz |= 1ULL << b;
    }
    uint64_t v = nz;
    for (int i = 0; i < k; i++) v ^= I.X[size_t(I.secret[i]) * W + w];
    I.y[w] = v;
  }
  return I;
}

// spbits' inst_hash over the unpadded words.
inline uint64_t instHash(const Instance& I) {
  uint64_t h = 0x12345678ULL;
  for (int j = 0; j < I.n; j++)
    for (int w = 0; w < I.W; w++) h = mix64(h ^ I.X[size_t(j) * I.W + w]);
  for (int w = 0; w < I.W; w++) h = mix64(h ^ I.y[w]);
  return h;
}

// Instance file "SPI1" (little-endian): magic, then uint32 n, k, m, W, uint32 0, uint64 seed, double eta,
// int32 secret[8] (-1 = unused or unknown), then X (n * W uint64, feature-major), then y (W uint64).
inline void saveInstance(const std::string& path, const Instance& I) {
  std::ofstream f(path, std::ios::binary);
  if (!f) throw std::runtime_error("cannot write " + path);
  const char magic[4] = {'S', 'P', 'I', '1'};
  const uint32_t hdr[5] = {uint32_t(I.n), uint32_t(I.k), uint32_t(I.m), uint32_t(I.W), 0};
  int32_t sec[8];
  for (int i = 0; i < 8; i++) sec[i] = i < int(I.secret.size()) ? I.secret[i] : -1;
  f.write(magic, 4);
  f.write(reinterpret_cast<const char*>(hdr), sizeof hdr);
  f.write(reinterpret_cast<const char*>(&I.seed), 8);
  f.write(reinterpret_cast<const char*>(&I.eta), 8);
  f.write(reinterpret_cast<const char*>(sec), sizeof sec);
  f.write(reinterpret_cast<const char*>(I.X.data()), std::streamsize(I.X.size() * 8));
  f.write(reinterpret_cast<const char*>(I.y.data()), std::streamsize(I.y.size() * 8));
}

inline Instance loadInstance(const std::string& path) {
  std::ifstream f(path, std::ios::binary);
  if (!f) throw std::runtime_error("cannot read " + path);
  char magic[4];
  uint32_t hdr[5];
  int32_t sec[8];
  Instance I;
  f.read(magic, 4);
  f.read(reinterpret_cast<char*>(hdr), sizeof hdr);
  f.read(reinterpret_cast<char*>(&I.seed), 8);
  f.read(reinterpret_cast<char*>(&I.eta), 8);
  f.read(reinterpret_cast<char*>(sec), sizeof sec);
  if (!f || std::memcmp(magic, "SPI1", 4) != 0) throw std::runtime_error(path + " is not an SPI1 instance file");
  I.n = int(hdr[0]);
  I.k = int(hdr[1]);
  I.m = int(hdr[2]);
  I.W = int(hdr[3]);
  if (I.n < 1 || I.n > int(SPP_NMAX) || I.k < 1 || I.k > int(SPP_KMAX) || I.k > I.n || I.m < 1 ||
      I.m > int(64 * SPP_SMAX) || I.W != (I.m + 63) / 64) {
    throw std::runtime_error(path + ": sizes out of range");
  }
  for (int i = 0; i < 8; i++)
    if (sec[i] >= 0 && i < I.k) I.secret.push_back(sec[i]);
  if (int(I.secret.size()) != I.k) I.secret.clear();
  I.X.resize(size_t(I.n) * I.W);
  I.y.resize(I.W);
  f.read(reinterpret_cast<char*>(I.X.data()), std::streamsize(I.X.size() * 8));
  f.read(reinterpret_cast<char*>(I.y.data()), std::streamsize(I.y.size() * 8));
  if (!f) throw std::runtime_error(path + ": truncated");
  return I;
}

// ---------------------------------------------------------------- binomials and colex ranks

// C(a, b) for a < 2^31, b <= 6, exact in 128 bits; C(a, b) = 0 for a < b (and for a < 0).
inline unsigned __int128 binom(int64_t a, int b) {
  if (b < 0 || a < b) return 0;
  unsigned __int128 r = 1;
  for (int i = 0; i < b; i++) r = r * uint64_t(a - i) / uint64_t(i + 1);
  return r;
}
inline uint64_t binom64(int64_t a, int b) { return uint64_t(binom(a, b)); }

// The (r)-subset of colex rank `rank` (ascending), for r >= 0.
inline std::vector<int> unrank(uint64_t rank, int r) {
  std::vector<int> s(r);
  for (int e = r; e >= 1; --e) {
    int64_t p = e - 1;  // largest p with C(p, e) <= rank
    int64_t lo = e - 1, hi = int64_t(SPP_NMAX) * 4;
    while (lo < hi) {
      const int64_t mid = (lo + hi + 1) / 2;
      if (binom(mid, e) <= rank) lo = mid; else hi = mid - 1;
    }
    p = lo;
    s[e - 1] = int(p);
    rank -= binom64(p, e);
  }
  return s;
}

inline uint64_t rankOf(const std::vector<int>& s) {
  uint64_t r = 0;
  for (size_t e = 0; e < s.size(); ++e) r += binom64(s[e], int(e) + 1);
  return r;
}

inline void colexNext(std::vector<int>& r) {
  const size_t k1 = r.size();
  for (size_t e = 0; e < k1; ++e) {
    if (e + 1 == k1 || r[e] + 1 < r[e + 1]) {
      ++r[e];
      for (size_t f = 0; f < e; ++f) r[f] = int(f);
      return;
    }
  }
}

// ---------------------------------------------------------------- the row-tile model

// cpu/sp.h's geometry: rows are the (k-1)-subsets of 0..n-2 (a row whose max is n-1 has no candidate), so
// nrows = C(n-1, k-1) and every row tile has at least one candidate; M0's work lists index the same tiles.
struct Geometry {
  int n = 0, k = 0, m = 0, S = 0, nJ = 0;
  uint64_t nrows = 0;      // C(n-1, k-1)
  uint64_t ntiles = 0;     // ceil(nrows / 16)
  uint64_t workTiles = 0;  // = ntiles: tiles [0, workTiles) have candidates
  uint64_t ncand = 0;      // C(n, k)
  // Row tiles grouped by first column tile: tiles [runStart[J], runStart[J+1]) have J0 = J, for J = 0..nJ
  // (J0 = nJ: no column tile, no candidate).
  std::vector<uint64_t> runStart;  // nJ + 2 entries
  explicit Geometry(const Instance& I) : n(I.n), k(I.k), m(I.m), S(I.W), nJ((I.n + 15) / 16) {
    nrows = binom64(n - 1, k - 1);
    ntiles = (nrows + 15) / 16;
    ncand = binom64(n, k);
    runStart.assign(nJ + 2, ntiles);
    // The row of rank rho has max element p = the largest p with C(p, k-1) <= rho (k >= 2); J0 = (p + 1) >> 4.
    // J0(t) >= J  <=>  p(16t) >= 16J - 1  <=>  16t >= C(16J - 1, k-1).
    for (int J = 0; J <= nJ; ++J) {
      if (J == 0) {
        runStart[J] = 0;
      } else if (k == 1) {
        runStart[J] = ntiles;  // the one row (the empty subset) has J0 = 0
      } else {
        const uint64_t first = binom64(16 * int64_t(J) - 1, k - 1);  // first row rank with max >= 16J - 1
        runStart[J] = std::min<uint64_t>(ntiles, (first + 15) / 16);
      }
    }
    runStart[nJ + 1] = ntiles;
    workTiles = runStart[nJ];
  }
  int J0(uint64_t t) const {
    const auto it = std::upper_bound(runStart.begin(), runStart.end(), t);
    return int(it - runStart.begin()) - 1;
  }
  uint64_t opsOfTile(uint64_t t) const { return uint64_t(nJ - J0(t)) * S; }
};

// The cost model of one row tile (the same as tools/planner.py's tile_cycles; M2 calibrates the constants). A row
// tile with `nout` column tiles and S slices costs
//   max(hart 0 = ops * cOp + nout * cEpi + (A resident ? S KB / bw : 0),   the tensor ops, epilogues, A load
//       hart 1 = S * cGen,                                                the row generation (2 buffers: one ahead)
//       bytes / bw)                                                       the shire's streaming limit
// with ops = nout * S; bytes = B (1 KB per op) + A reads (S KB once if resident, 1 KB per op if streamed) + the
// generated rows (S KB). cOp: 270 resident (M, E39) / 280.35 streamed (M, E37); bw = 4 B per minion-cycle (M, E37);
// cEpi 450 and cGen 800 are assumed (A): the epilogue's ~110 instructions plus the spill, and hart 1's
// 4 x (~100 instructions + 8 uncached stores) per slice (review R1, finding 6). estCycles is the same with 350 per
// streamed op (the A prefetch waits for the previous FMA as the PRM requires), for sizing launches only.
struct CostModel {
  double cOpResident = 270.0, cOpStreamed = 280.35, cEpi = 450.0, cGen = 800.0, bw = 4.0;
};
inline double tileCyclesWith(int nJ, int J0, int S, const CostModel& M) {
  const double nout = double(nJ - J0), ops = nout * S;
  const bool resident = S <= 3;
  const double aLoad = resident ? S * 1024.0 / M.bw : 0.0;
  const double hart0 = ops * (resident ? M.cOpResident : M.cOpStreamed) + nout * M.cEpi + aLoad;
  const double gen = S * M.cGen;
  const double bytes = ops * 1024.0 + (resident ? S * 1024.0 : ops * 1024.0) + S * 1024.0;
  return std::max({hart0, gen, bytes / M.bw});
}
inline double tileCycles(int nJ, int J0, int S) { return tileCyclesWith(nJ, J0, S, CostModel{}); }

// ---------------------------------------------------------------- the work list

struct Block {
  uint64_t tile0 = 0, ntiles = 0;
};

struct Plan {
  uint64_t shireMask = 0;
  int perShire = 0;
  std::vector<std::vector<Block>> slots;  // SPP_MINION_SLOTS entries, index shire * 32 + minion
  Plan() : slots(SPP_MINION_SLOTS) {}
  std::vector<int> activeSlots() const {
    std::vector<int> v;
    for (int s = 0; s < 32; ++s)
      if ((shireMask >> s) & 1)
        for (int mi = 0; mi < perShire; ++mi) v.push_back(s * 32 + mi);
    return v;
  }
};

// Cost-balanced plan for tiles [t0, t1): the range is cut into (minions * rounds) contiguous blocks of equal
// modelled cycles, and block b goes to shire b mod S, minion (b / S) mod P of round b / (S * P), so consecutive
// blocks land in different shires (each shire gets a like mix of wide and narrow row tiles).
inline Plan makePlan(const Geometry& G, uint64_t shireMask, int perShire, int rounds, uint64_t t0, uint64_t t1) {
  Plan plan;
  plan.shireMask = shireMask;
  plan.perShire = perShire;
  std::vector<int> shires;
  for (int s = 0; s < 32; ++s)
    if ((shireMask >> s) & 1) shires.push_back(s);
  if (shires.empty() || perShire < 1 || perShire > 32) throw std::runtime_error("empty shire mask or bad --per-shire");
  const uint64_t nblocks = uint64_t(shires.size()) * perShire * std::max(1, rounds);
  // Cumulative cost over the runs of equal J0.
  double total = 0;
  for (int J = 0; J <= G.nJ; ++J) {
    const uint64_t a = std::max(G.runStart[J], t0), b = std::min(G.runStart[J + 1], t1);
    if (b > a) total += double(b - a) * tileCycles(G.nJ, J, G.S);
  }
  // Walk the tiles run by run, closing a block whenever the cumulative cost passes the next cut.
  std::vector<Block> blocks;
  blocks.reserve(nblocks);
  uint64_t cur0 = t0;
  double acc = 0;
  uint64_t made = 0;
  for (int J = 0; J <= G.nJ && made + 1 < nblocks; ++J) {
    const uint64_t a = std::max(G.runStart[J], t0), b = std::min(G.runStart[J + 1], t1);
    if (b <= a) continue;
    const double c = tileCycles(G.nJ, J, G.S);
    uint64_t t = a;
    while (t < b && made + 1 < nblocks) {
      const double target = total * double(made + 1) / double(nblocks);
      // tiles of this run needed to reach the target
      const double need = (target - acc) / c;
      uint64_t take = need <= 0 ? 0 : uint64_t(std::ceil(need - 1e-9));
      if (take > b - t) {
        acc += double(b - t) * c;
        t = b;
        break;
      }
      t += take;
      acc += double(take) * c;
      blocks.push_back({cur0, t - cur0});
      cur0 = t;
      ++made;
    }
  }
  blocks.push_back({cur0, t1 - cur0});
  while (blocks.size() < nblocks) blocks.push_back({t1, 0});
  const uint64_t S = shires.size();
  for (uint64_t b = 0; b < nblocks; ++b) {
    if (blocks[b].ntiles == 0) continue;
    const int shire = shires[b % S];
    const int minion = int((b / S) % uint64_t(perShire));
    plan.slots[shire * 32 + minion].push_back(blocks[b]);
  }
  return plan;
}

// "shire minion tile0 ntiles" per line (# comments): the M0 planner's text form.
inline Plan readPlan(const std::string& path, uint64_t shireMask, int perShire, const Geometry& G) {
  std::ifstream f(path);
  if (!f) throw std::runtime_error("cannot read " + path);
  Plan plan;
  plan.shireMask = shireMask;
  plan.perShire = perShire;
  std::string line;
  while (std::getline(f, line)) {
    const auto h = line.find('#');
    if (h != std::string::npos) line.resize(h);
    std::istringstream in(line);
    long long s, mi, t0, nt;
    if (!(in >> s >> mi >> t0 >> nt)) continue;
    if (s < 0 || s >= 32 || !((shireMask >> s) & 1) || mi < 0 || mi >= perShire || t0 < 0 || nt < 1 ||
        uint64_t(t0 + nt) > G.ntiles) {
      throw std::runtime_error(path + ": block out of range: " + line);
    }
    plan.slots[s * 32 + mi].push_back({uint64_t(t0), uint64_t(nt)});
  }
  return plan;
}

// ---------------------------------------------------------------- CPU scoring

inline int popc(uint64_t x) { return __builtin_popcountll(x); }

// P_R = y ^ X[r] for r in R (S words).
inline void rowBits(const Instance& I, const std::vector<int>& R, uint64_t* P) {
  for (int w = 0; w < I.W; ++w) {
    uint64_t v = I.y[w];
    for (int r : R) v ^= I.X[size_t(r) * I.W + w];
    P[w] = v;
  }
}

// The +-1 correlation of row bits P with feature j (any j < n; 0 for j >= n): the GEMM's raw entry.
inline int32_t corr(const Instance& I, const uint64_t* P, int j) {
  if (j >= I.n) return 0;
  int pc = 0;
  const uint64_t* x = &I.X[size_t(j) * I.W];
  for (int w = 0; w < I.W; ++w) pc += popc(P[w] ^ x[w]);
  return I.m - 2 * pc;
}

inline int32_t scoreSubset(const Instance& I, const std::vector<int>& T) {
  std::vector<uint64_t> P(I.W);
  std::vector<int> R(T.begin(), T.end() - 1);
  rowBits(I, R, P.data());
  return corr(I, P.data(), T.back());
}

// tie: another candidate has c == best (the kernel's SPP_INFO_TIE). Merging keeps it exact: equal bests from two
// disjoint sets are a tie.
struct Acc {
  __int128 sum = 0;
  unsigned __int128 sq = 0;
  uint64_t count = 0;
  int32_t best = INT32_MIN;
  uint64_t bestRank = ~0ull;
  bool tie = false;
  void add(int32_t c, uint64_t rank) {
    sum += c;
    sq += uint64_t(int64_t(c) * c);
    ++count;
    if (c > best) {
      best = c;
      bestRank = rank;
      tie = false;
    } else if (c == best) {
      tie = true;
      bestRank = std::min(bestRank, rank);
    }
  }
  void merge(const Acc& o) {
    sum += o.sum;
    sq += o.sq;
    count += o.count;
    if (o.best == INT32_MIN) return;  // o scored nothing
    if (o.best > best) {
      best = o.best;
      bestRank = o.bestRank;
      tie = o.tie;
    } else if (o.best == best) {
      tie = true;
      bestRank = std::min(bestRank, o.bestRank);
    }
  }
};

// Visits the output tiles of a slot's blocks in the kernel's order: f(tile t, J, J0, rows' subsets, validity).
// Scores every valid candidate into acc; if `tiles` is given, appends each output tile's raw 16 x 16 GEMM values
// (tensor dump) or its scalar-dump image (valid entries c, others INT32_MIN).
inline void scoreBlocks(const Instance& I, const Geometry& G, const std::vector<Block>& blocks, Acc& acc,
                        std::vector<int32_t>* tiles = nullptr, bool scalarImage = false) {
  const int k1 = I.k - 1;
  std::vector<uint64_t> P(size_t(16) * I.W);
  for (const Block& b : blocks) {
    std::vector<int> r = unrank(16 * b.tile0, k1);
    uint64_t rank = 16 * b.tile0;
    for (uint64_t t = 0; t < b.ntiles; ++t) {
      int pmax[16];
      bool valid[16];
      for (int i = 0; i < 16; ++i, ++rank) {
        valid[i] = rank < G.nrows;
        pmax[i] = k1 ? r[k1 - 1] : -1;
        if (valid[i]) {
          rowBits(I, r, &P[size_t(i) * I.W]);
          colexNext(r);
        }
      }
      const uint64_t rank0 = rank - 16;
      const int J0 = (pmax[0] + 1) >> 4;
      for (int J = J0; J < G.nJ; ++J) {
        int32_t img[256];
        for (int i = 0; i < 16; ++i) {
          for (int jj = 0; jj < 16; ++jj) {
            const int j = 16 * J + jj;
            int32_t raw = 0;
            if (valid[i]) raw = corr(I, &P[size_t(i) * I.W], j);
            const bool ok = valid[i] && j > pmax[i] && j < I.n;
            if (ok) acc.add(raw, rank0 + i + binom64(j, I.k));
            img[i * 16 + jj] = scalarImage ? (ok ? raw : INT32_MIN) : raw;
          }
        }
        if (tiles) tiles->insert(tiles->end(), img, img + 256);
      }
    }
  }
}

// Candidates in a list of blocks, without scoring: rows of max p contribute n - 1 - p each.
inline uint64_t countCandidates(const Geometry& G, const std::vector<Block>& blocks) {
  uint64_t total = 0;
  const int k1 = G.k - 1;
  for (const Block& b : blocks) {
    uint64_t lo = 16 * b.tile0, hi = std::min<uint64_t>(G.nrows, 16 * (b.tile0 + b.ntiles));
    if (hi <= lo) continue;
    if (k1 == 0) {
      total += uint64_t(G.n);
      continue;
    }
    for (int p = k1 - 1; p < G.n; ++p) {
      const uint64_t a = std::max(lo, binom64(p, k1)), e = std::min(hi, binom64(p + 1, k1));
      if (e > a) total += (e - a) * uint64_t(G.n - 1 - p);
    }
  }
  return total;
}

// Output tiles of a list of blocks (the dump's size).
inline uint64_t countOutputTiles(const Geometry& G, const std::vector<Block>& blocks) {
  uint64_t total = 0;
  for (const Block& b : blocks) {
    for (int J = 0; J < G.nJ; ++J) {
      const uint64_t a = std::max(G.runStart[J], b.tile0), e = std::min(G.runStart[J + 1], b.tile0 + b.ntiles);
      if (e > a) total += (e - a) * uint64_t(G.nJ - J);
    }
  }
  return total;
}

inline uint64_t countOps(const Geometry& G, const std::vector<Block>& blocks) {
  return countOutputTiles(G, blocks) * uint64_t(G.S);
}

inline double modelCycles(const Geometry& G, const std::vector<Block>& blocks) {
  double c = 0;
  for (const Block& b : blocks) {
    for (int J = 0; J <= G.nJ; ++J) {
      const uint64_t a = std::max(G.runStart[J], b.tile0), e = std::min(G.runStart[J + 1], b.tile0 + b.ntiles);
      if (e > a) c += double(e - a) * tileCycles(G.nJ, J, G.S);
    }
  }
  return c;
}

// A conservative cycle estimate for sizing launches (not a prediction): the cost model with 275 cycles per
// resident op and 350 per streamed op (the A prefetch waits for the previous FMA).
inline double estCycles(const Geometry& G, const std::vector<Block>& blocks) {
  CostModel M;
  M.cOpResident = 275.0;
  M.cOpStreamed = 350.0;
  double c = 0;
  for (const Block& b : blocks) {
    for (int J = 0; J <= G.nJ; ++J) {
      const uint64_t a = std::max(G.runStart[J], b.tile0), e = std::min(G.runStart[J + 1], b.tile0 + b.ntiles);
      if (e > a) c += double(e - a) * tileCyclesWith(G.nJ, J, G.S, M);
    }
  }
  return c;
}

// ---------------------------------------------------------------- the closed forms (DESIGN.md 4.1)

// Krawtchouk K_k(w) = sum_t (-1)^t C(w, t) C(n - w, k - t).
inline __int128 kraw(int n, int k, int w) {
  __int128 s = 0;
  for (int t = 0; t <= k; ++t) {
    const __int128 v = __int128(binom(w, t)) * __int128(binom(n - w, k - t));
    s += (t & 1) ? -v : v;
  }
  return s;
}

// sum over all C(n,k) candidates of c and of c^2: sum_i y~_i K_k(w_i) and sum_{i,i'} y~_i y~_i' K_k(d(x_i, x_i')).
inline void closedForms(const Instance& I, __int128& sumC, unsigned __int128& sumC2) {
  const int n = I.n, m = I.m, Wn = (n + 63) / 64;
  std::vector<__int128> K(n + 1);
  for (int w = 0; w <= n; ++w) K[w] = kraw(n, I.k, w);
  std::vector<uint64_t> rows(size_t(m) * Wn, 0);  // sample-major
  for (int f = 0; f < n; ++f)
    for (int i = 0; i < m; ++i)
      if (I.Xbit(f, i)) rows[size_t(i) * Wn + f / 64] |= 1ull << (f % 64);
  std::vector<int> ys(m);
  for (int i = 0; i < m; ++i) ys[i] = I.ybit(i) ? -1 : 1;
  sumC = 0;
  __int128 s2 = 0;
  for (int i = 0; i < m; ++i) {
    int w = 0;
    for (int q = 0; q < Wn; ++q) w += popc(rows[size_t(i) * Wn + q]);
    sumC += ys[i] * K[w];
    s2 += K[0];  // i = i'
    for (int i2 = i + 1; i2 < m; ++i2) {
      int d = 0;
      for (int q = 0; q < Wn; ++q) d += popc(rows[size_t(i) * Wn + q] ^ rows[size_t(i2) * Wn + q]);
      s2 += 2 * ys[i] * ys[i2] * K[d];
    }
  }
  sumC2 = (unsigned __int128)s2;
}

inline std::string i128(__int128 v) {
  if (v == 0) return "0";
  const bool neg = v < 0;
  unsigned __int128 u = neg ? (unsigned __int128)(-v) : (unsigned __int128)v;
  std::string s;
  while (u) {
    s.push_back(char('0' + int(u % 10)));
    u /= 10;
  }
  if (neg) s.push_back('-');
  std::reverse(s.begin(), s.end());
  return s;
}

// ---------------------------------------------------------------- device images

// X as int8 B tiles: tile (J, s) at (J*S + s) KB; line p, byte 4j + e = x[64s + 4p + e][16J + j] as +1/-1, 0 pad.
inline std::vector<uint8_t> makeXB(const Instance& I) {
  const int S = I.W, nJ = (I.n + 15) / 16;
  std::vector<uint8_t> xb(size_t(nJ) * S * SPP_TILE_BYTES, 0);
  for (int J = 0; J < nJ; ++J)
    for (int s = 0; s < S; ++s) {
      uint8_t* t = &xb[(size_t(J) * S + s) * SPP_TILE_BYTES];
      for (int p = 0; p < 16; ++p)
        for (int j = 0; j < 16; ++j)
          for (int e = 0; e < 4; ++e) {
            const int i = 64 * s + 4 * p + e, f = 16 * J + j;
            if (i < I.m && f < I.n) t[p * 64 + j * 4 + e] = I.Xbit(f, i) ? 0xFF : 0x01;
          }
    }
  return xb;
}

}  // namespace spp
