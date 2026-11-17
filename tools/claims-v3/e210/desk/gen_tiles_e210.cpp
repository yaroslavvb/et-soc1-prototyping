// E210 (Q202): the desk tile generator (sw-design-a's gen_tiles.cpp, unchanged but for this header and its include). Draws N tile pairs
// (A then B, 1,024 bytes each: the host's and the bench's tile format) of one pattern:
//   - E210's designed patterns: drawTilePattern() from drawtile_e210.h (sw-design-a's drawtile_ext.h, verbatim);
//   - the calibration generators randn / sparse50 / sparse25 / e37: rgm136's own drawTile() and halfRounded(), copied verbatim below from
//     tools/claims-v3/e136/rgm136/host/main.cpp (sha256 f9b2279f838ad30444748f2a5abad5dd646df631735fc029a6ac01f9036e2fda, lines 731-769).
// Each draw is one GEMM tile pair (what one op of a minion consumes). The seed is fixed per pattern (FNV-1a of "E210-desk|<gen>|<type>").
//   g++ -O2 -std=c++17 -o gen_tiles_e210 gen_tiles_e210.cpp
//   ./gen_tiles_e210 <gen> <fp32|fp16> <n_pairs> <outdir>   writes <outdir>/<gen>_<NN>.bin (the first n pairs of the seeded stream)
// SPDX-License-Identifier: Apache-2.0
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <random>
#include <stdexcept>
#include <string>
#define SP_FP32 0u
#define SP_FP16 1u
#define SP_INT8 3u
#define SP_TILE_BYTES 1024u
#include "drawtile_e210.h"

// ---- verbatim from rgm136's host/main.cpp ----
uint16_t halfRounded(float f) {
  uint32_t b;
  std::memcpy(&b, &f, 4);
  const uint32_t sign = (b >> 16) & 0x8000u;
  int32_t exp = int32_t((b >> 23) & 0xFF) - 127 + 15;
  uint32_t man = (b & 0x7FFFFFu) + 0x1000u;
  if (man & 0x800000u) { man = 0; ++exp; }
  if (exp <= 0) return uint16_t(sign);
  if (exp >= 31) return uint16_t(sign | 0x7BFFu);
  return uint16_t(sign | (uint32_t(exp) << 10) | ((man >> 13) & 0x3FFu));
}

// One tile of `gen`: every element slot drawn independently.
void drawTile(uint8_t* t, uint64_t type, const std::string& gen, std::mt19937_64& rng) {
  std::normal_distribution<float> n(0.f, 1.f);
  static const int e37[4] = {-2, -1, 1, 2};
  const size_t size = type == SP_FP32 ? 4 : type == SP_FP16 ? 2 : 1;
  const bool sparse = gen == "sparse50", sparse25 = gen == "sparse25", small = gen == "e37";
  if (!sparse && !sparse25 && !small && gen != "randn") throw std::runtime_error("--values: unknown gen " + gen);
  for (size_t off = 0; off + size <= SP_TILE_BYTES; off += size) {
    const bool zero = sparse ? bool(rng() & 1) : sparse25 ? (rng() & 3) == 0 : false;
    if (type == SP_INT8) {
      const int q = zero ? 0 : small ? e37[rng() & 3] : int(rng() % 256) - 128;
      t[off] = uint8_t(int8_t(q));
    } else {
      const float f = zero ? 0.f : small ? float(e37[rng() & 3]) : n(rng);
      if (type == SP_FP32) std::memcpy(t + off, &f, 4);
      else { const uint16_t h = halfRounded(f); std::memcpy(t + off, &h, 2); }
    }
  }
}
// ---- end verbatim ----

static uint64_t fnv1a(const std::string& s) {
  uint64_t h = 1469598103934665603ull;
  for (unsigned char c : s) { h ^= c; h *= 1099511628211ull; }
  return h;
}

int main(int argc, char** argv) {
  if (argc != 5) { std::fprintf(stderr, "usage: gen_tiles <gen> <fp32|fp16> <n_pairs> <outdir>\n"); return 2; }
  const std::string gen = argv[1], ts = argv[2];
  const uint64_t type = ts == "fp32" ? SP_FP32 : ts == "fp16" ? SP_FP16 : 99;
  if (type == 99) { std::fprintf(stderr, "type must be fp32 or fp16\n"); return 2; }
  const int n = std::atoi(argv[3]);
  std::mt19937_64 rng(fnv1a("E210-desk|" + gen + "|" + ts));
  uint8_t a[1024], b[1024];
  for (int p = 0; p < n; ++p) {
    // A then B, as fillPools draws the A pool and then the B pool (here pair by pair; the law per tile is the same)
    if (!drawTilePattern(a, type, gen, false, rng)) drawTile(a, type, gen, rng);
    if (!drawTilePattern(b, type, gen, true, rng)) drawTile(b, type, gen, rng);
    char path[4096];
    std::snprintf(path, sizeof path, "%s/%s_%02d.bin", argv[4], gen.c_str(), p);
    FILE* f = std::fopen(path, "wb");
    if (!f) { std::perror(path); return 1; }
    std::fwrite(a, 1, 1024, f);
    std::fwrite(b, 1, 1024, f);
    std::fclose(f);
  }
  std::printf("%s %s: %d pairs\n", gen.c_str(), ts.c_str(), n);
  return 0;
}
