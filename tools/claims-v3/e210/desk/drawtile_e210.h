// E210 (Q202): the desk generator of E210's operand patterns, the laws its tile files are drawn by. This is sw-design-a's code (round Q202,
// its scripts/drawtile_ext.h, sha256 recorded in desk/tiles-e210.json), unchanged below this header. E210 does NOT change rgm136's host or
// kernel: the host reads these laws from tile files (--values gemmL<MB>x<NB>x<KB>:tiles:<61 files>, the pool cycling the files), so this code
// runs only at the desk (gen_tiles_e210.cpp), never on a card.
//
// Tile layout (the host's and the bench's): 1,024 bytes = 16 lines of 64 B; fp32: word 16 r + c is row r, column c. An A tile's row i is
// A[i][0..15] (K across the line); a B tile's row k is B[k][0..15] (N across the line). PRM 9.4's order (vpu_tensorfma.v, the bench):
// for k, for i, two micro-ops (columns 0-7 then 8-15): lane l computes C[i][8h+l] += A[i][k] * B[k][8h+l]. So the A operand walks DOWN
// a column of the A tile (i) at fixed k, changing every 2 micro-ops; a lane's B operand alternates between B[k][l] and B[k][l+8].
// The patterns below are written against that order.
// SPDX-License-Identifier: Apache-2.0
#pragma once
#include <cstdint>
#include <cstring>
#include <random>
#include <string>
#ifndef SP_FP32
#define SP_FP32 0u  // as sparsity_args.h
#define SP_FP16 1u
#endif

static inline uint32_t sw_randn_word(std::mt19937_64& rng, std::normal_distribution<float>& n) {
  // a normal(0,1) float with a normal (non-zero, non-denormal) bit pattern; redraw otherwise (never taken in practice)
  for (;;) {
    const float f = n(rng);
    uint32_t w;
    std::memcpy(&w, &f, 4);
    if ((w & 0x7F800000u) != 0 && (w & 0x7F800000u) != 0x7F800000u) return w;
  }
}

// exactly 4 distinct bits among mantissa bits 0..22, uniformly (a partial Fisher-Yates over the 23 positions)
static inline uint32_t sw_mask4(std::mt19937_64& rng) {
  int pos[23];
  for (int i = 0; i < 23; ++i) pos[i] = i;
  uint32_t m = 0;
  for (int j = 0; j < 4; ++j) {
    const int r = j + int(rng() % uint64_t(23 - j));
    const int tmp = pos[j]; pos[j] = pos[r]; pos[r] = tmp;
    m |= 1u << pos[j];
  }
  return m;
}

// Returns false for a gen this function does not know (drawTile then goes on as before).
static bool drawTilePattern(uint8_t* t, uint64_t type, const std::string& gen, bool isB, std::mt19937_64& rng) {
  std::normal_distribution<float> n(0.f, 1.f);
  uint32_t w32[256];
  if (type == SP_FP32) {
    const uint32_t FLIP = 0x807FFFFFu;   // sign and all 23 mantissa bits: a finite value of the same exponent
    if (gen == "lowmant8") {             // 1.0 + 8 random LOW mantissa bits (0-7), A and B
      for (int e = 0; e < 256; ++e) w32[e] = 0x3F800000u | uint32_t(rng() & 0xFFu);
    } else if (gen == "highmant8") {     // 1.0 + 8 random HIGH mantissa bits (15-22), A and B: the same set-bit and change shares as lowmant8
      for (int e = 0; e < 256; ++e) w32[e] = 0x3F800000u | (uint32_t(rng() & 0xFFu) << 15);
    } else if (gen == "slowmant8") {     // lowmant8 with a random sign: the accumulators random-walk (small) instead of growing with K
      for (int e = 0; e < 256; ++e) { const uint32_t m = uint32_t(rng() & 0xFFu); w32[e] = 0x3F800000u | m | (uint32_t(rng() & 1u) << 31); }
    } else if (gen == "shighmant8") {    // highmant8 with a random sign: the same set-bit and change shares as slowmant8
      for (int e = 0; e < 256; ++e) { const uint32_t m = uint32_t(rng() & 0xFFu); w32[e] = 0x3F800000u | (m << 15) | (uint32_t(rng() & 1u) << 31); }
    } else if (gen == "bhalfeq") {       // A random normal; B's two halves equal (B[k][l+8] = B[k][l]): a lane's b never changes within a k step
      for (int r = 0; r < 16; ++r)
        for (int c = 0; c < 8; ++c) {
          if (!isB) { w32[16 * r + c] = sw_randn_word(rng, n); w32[16 * r + c + 8] = sw_randn_word(rng, n); }
          else { const uint32_t b = sw_randn_word(rng, n); w32[16 * r + c] = b; w32[16 * r + c + 8] = b; }
        }
    } else if (gen == "badjeq") {        // bhalfeq's values, ORDER changed: B's equal pairs in ADJACENT columns (2m, 2m+1), not (l, l+8)
      for (int r = 0; r < 16; ++r)       // (each B row holds 8 values twice, as in bhalfeq; a lane's b still alternates between 2 values)
        for (int c = 0; c < 16; c += 2) {
          if (!isB) { w32[16 * r + c] = sw_randn_word(rng, n); w32[16 * r + c + 1] = sw_randn_word(rng, n); }
          else { const uint32_t b = sw_randn_word(rng, n); w32[16 * r + c] = b; w32[16 * r + c + 1] = b; }
        }
    } else if (gen == "maxalt" || gen == "maxalte") {
      // maximal alternation: A down each column a, a^F, a, ...; B[k][l+8] = B[k][l]^F. maxalt: F = sign + 23 mantissa bits (24 bits, the
      // same exponent); maxalte: F = 0x83FFFFFF, also the exponent's low 3 bits (27 bits; magnitudes alternate by up to 2^7, so the
      // aligner's shift alternates too). The base is a normal(0,1) word with its exponent field in [8, 247], so a^F stays finite and normal.
      const uint32_t F = gen == "maxalt" ? FLIP : 0x83FFFFFFu;
      auto base = [&]() { for (;;) { const uint32_t w = sw_randn_word(rng, n); const uint32_t e = (w >> 23) & 0xFFu; if (e >= 8 && e <= 247) return w; } };
      if (!isB) {
        for (int c = 0; c < 16; ++c) {
          const uint32_t a = base();
          for (int r = 0; r < 16; ++r) w32[16 * r + c] = (r & 1) ? (a ^ F) : a;
        }
      } else {
        for (int r = 0; r < 16; ++r)
          for (int c = 0; c < 8; ++c) { const uint32_t b = base(); w32[16 * r + c] = b; w32[16 * r + c + 8] = b ^ F; }
      }
    } else if (gen == "hd4") {           // successive operands in the feed order exactly 4 mantissa bits apart: A down each column, B across the halves
      if (!isB) {
        for (int c = 0; c < 16; ++c) {
          uint32_t a = sw_randn_word(rng, n);
          for (int r = 0; r < 16; ++r) { if (r) a ^= sw_mask4(rng); w32[16 * r + c] = a; }
        }
      } else {
        for (int r = 0; r < 16; ++r)
          for (int c = 0; c < 8; ++c) { const uint32_t b = sw_randn_word(rng, n); w32[16 * r + c] = b; w32[16 * r + c + 8] = b ^ sw_mask4(rng); }
      }
    } else if (gen == "signs") {         // +-1.0, random sign (E9 ran this value set as a resident loop, never in a GEMM)
      for (int e = 0; e < 256; ++e) w32[e] = 0x3F800000u | (uint32_t(rng() & 1u) << 31);
    } else if (gen == "arow50") {        // A's odd rows zero (half the micro-ops gated on every lane), the rest and B random normal
      for (int r = 0; r < 16; ++r)
        for (int c = 0; c < 16; ++c) w32[16 * r + c] = (!isB && (r & 1)) ? 0u : sw_randn_word(rng, n);
    } else if (gen == "negzero") {       // -0.0 everywhere: never gated (the gate tests the all-zero word), nothing moves
      for (int e = 0; e < 256; ++e) w32[e] = 0x80000000u;
    } else {
      return false;
    }
    std::memcpy(t, w32, 1024);
    return true;
  }
  if (type == SP_FP16) {
    uint16_t h[512];
    if (gen == "lowmant4h") {            // fp16 1.0 + 4 random LOW mantissa bits (0-3)
      for (int e = 0; e < 512; ++e) h[e] = uint16_t(0x3C00u | uint32_t(rng() & 0xFu));
    } else if (gen == "highmant4h") {    // fp16 1.0 + 4 random HIGH mantissa bits (6-9)
      for (int e = 0; e < 512; ++e) h[e] = uint16_t(0x3C00u | (uint32_t(rng() & 0xFu) << 6));
    } else {
      return false;
    }
    std::memcpy(t, h, 1024);
    return true;
  }
  return false;
}
