// mnistmlp_host: one forward pass (or R passes) of E202's int8 MLP over MNIST (../mnistmlp_args.h,
// ../kernel/mnistmlp.c), in the simulator or, only with --card, on a card. One process = at most one launch: read and
// pin-check the inputs, pack them, open the device, copy in, poison the outputs, launch, read back, close the device,
// check everything on the CPU, write one JSON result to --out (and the same line on stdout; progress on stderr).
//
//   mnistmlp_host (--sysemu [--sim-args "..."] [--sim-extra "..."] | --card | --dry | --ref | --selftest)
//       --images IDX --weights MLPW --expect MLPE [--expect-logits MLPL] [--true-labels IDX]
//       [--split train|test] [--passes R | --groups N] [--shires MASK] [--per-shire P] [--stage scp|dram]
//       [--debug-logits] [--epoch E] [--out FILE] [--labels-out FILE] [--pins FILE | --no-pins]
//       [--max-kernel-s S] [--budget S] [--kernel ELF] [--poll-limit N]
//   --ref: no device. The host's own reference of the kernel's arithmetic on the packed tiles for groups
//          0..--ref-groups-1 (default 2), compared with --expect (and --expect-logits); --ref-out FILE writes them
//          (MLPR: per group the 16 labels, the checksum and the raw layer-5 C tile).
//
// Inputs (model/: fetch_mnist.sh, train_int8.py, mnist_model.py write them; PINS-SHA256SUMS pins them):
//   IDX   the decompressed MNIST files (images: 0x00000803, n, 28, 28; labels: 0x00000801, n);
//   MLPW  the weights: a 256 B header ("MLPW0001", 5 layers' padded and real K and N, the 4 multipliers, a name), then
//         each layer's int8 Q[Kpad][Npad] (k-major), then each layer's int32 bias[Npad] (Bp for hidden layers);
//   MLPE  expected outputs for one split and one weights file: "MLPE0001", groups, images, then uint8 labels[groups*16]
//         and uint32 checksums[groups];
//   MLPL  expected raw layer-5 C tiles: "MLPL0001", groups, then int32 [groups][16][16].
// Every input file's sha256 must equal its line in the pins file (sha256sum format, by basename) unless --no-pins.
//
// Checks (all must pass for "PASS", exit 0): every working minion's record (this epoch, magic, no error flag,
// tensor_error 0, groups and ops as the plan says); every label line 0..groups-1 written with its own group number,
// this epoch and DONE, its 16 labels and checksum equal to --expect's for input group G mod gpp; every padding group's
// discard line; with --debug-logits every layer-5 C tile equal to --expect-logits'. Accuracy against --true-labels is
// reported, not checked. The JSON also carries "core_status" (every check but the debug logits) and "logits_status"
// (the debug logits alone; "NOT CHECKED" without --debug-logits); "status" is PASS only when both pass.
//
// Card etiquette (as workloads/ledger): the device is held only between opening the runtime and tearing it down; a
// deliberately slow model of the kernel's time refuses a launch over --max-kernel-s; the launch's timeout is min(8 s,
// 2 x model + 1.5 s, the time left in --budget); after a timed-out launch the stream is aborted and nothing is read
// back. Without --card or --sysemu nothing opens. The result goes to --out (the host's own file): a runtime line can
// split a host's stdout on a real box (E191's first session), so a kit reads the file.
// SPDX-License-Identifier: Apache-2.0
#include <g3log/loglevels.hpp>
#include <runtime/IRuntime.h>
#include <runtime/Types.h>
#include <device-layer/IDeviceLayer.h>
#include <sw-sysemu/SysEmuOptions.h>

#include <algorithm>
#include <cctype>
#include <chrono>
#include <cinttypes>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <filesystem>
#include <fstream>
#include <limits>
#include <map>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

#include "Constants.h"
#include "mnistmlp_args.h"

// libetrt's thread-pool workers log at the custom levels VERBOSE_HIGH/MID/LOW, which only logging::LoggerDefault
// registers with g3log; registering them first removes the race behind aifoundry3's 1.08 s host crash
// (docs/findings/14-card-behaviour.md, "Traps"), as workloads/enercat, sparseparity and ledger do.
static void registerRuntimeLogLevels() {
  const LEVELS levels[] = {LEVELS(g3::kDebugValue - 100, "VERBOSE_HIGH"), LEVELS(g3::kDebugValue - 99, "VERBOSE_MID"),
                           LEVELS(g3::kDebugValue - 98, "VERBOSE_LOW")};
  for (const auto& l : levels) g3::only_change_at_initialization::addLogLevel(l, false);
}

namespace fs = std::filesystem;
using Clock = std::chrono::steady_clock;

namespace {

const Clock::time_point kStart = Clock::now();
double secondsSince(Clock::time_point t0) { return std::chrono::duration<double>(Clock::now() - t0).count(); }
long long epochMs() {
  return std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::system_clock::now().time_since_epoch())
      .count();
}
std::vector<uint8_t> readFile(const std::string& path) {
  std::ifstream file(path, std::ios::binary);
  if (!file) return {};
  std::vector<uint8_t> data(fs::file_size(path));
  file.read(reinterpret_cast<char*>(data.data()), static_cast<std::streamsize>(data.size()));
  return data;
}

// ---------------------------------------------------------------- SHA-256 (FIPS 180-4), for the pins
struct Sha256 {
  uint32_t h[8];
  uint64_t len = 0;
  uint8_t buf[64];
  size_t nbuf = 0;
  static constexpr uint32_t K[64] = {
      0x428a2f98u, 0x71374491u, 0xb5c0fbcfu, 0xe9b5dba5u, 0x3956c25bu, 0x59f111f1u, 0x923f82a4u, 0xab1c5ed5u,
      0xd807aa98u, 0x12835b01u, 0x243185beu, 0x550c7dc3u, 0x72be5d74u, 0x80deb1feu, 0x9bdc06a7u, 0xc19bf174u,
      0xe49b69c1u, 0xefbe4786u, 0x0fc19dc6u, 0x240ca1ccu, 0x2de92c6fu, 0x4a7484aau, 0x5cb0a9dcu, 0x76f988dau,
      0x983e5152u, 0xa831c66du, 0xb00327c8u, 0xbf597fc7u, 0xc6e00bf3u, 0xd5a79147u, 0x06ca6351u, 0x14292967u,
      0x27b70a85u, 0x2e1b2138u, 0x4d2c6dfcu, 0x53380d13u, 0x650a7354u, 0x766a0abbu, 0x81c2c92eu, 0x92722c85u,
      0xa2bfe8a1u, 0xa81a664bu, 0xc24b8b70u, 0xc76c51a3u, 0xd192e819u, 0xd6990624u, 0xf40e3585u, 0x106aa070u,
      0x19a4c116u, 0x1e376c08u, 0x2748774cu, 0x34b0bcb5u, 0x391c0cb3u, 0x4ed8aa4au, 0x5b9cca4fu, 0x682e6ff3u,
      0x748f82eeu, 0x78a5636fu, 0x84c87814u, 0x8cc70208u, 0x90befffau, 0xa4506cebu, 0xbef9a3f7u, 0xc67178f2u};
  Sha256() {
    const uint32_t iv[8] = {0x6a09e667u, 0xbb67ae85u, 0x3c6ef372u, 0xa54ff53au,
                            0x510e527fu, 0x9b05688cu, 0x1f83d9abu, 0x5be0cd19u};
    std::memcpy(h, iv, sizeof h);
  }
  static uint32_t ror(uint32_t x, int n) { return (x >> n) | (x << (32 - n)); }
  void block(const uint8_t* p) {
    uint32_t w[64];
    for (int t = 0; t < 16; ++t)
      w[t] = (uint32_t(p[4 * t]) << 24) | (uint32_t(p[4 * t + 1]) << 16) | (uint32_t(p[4 * t + 2]) << 8) | p[4 * t + 3];
    for (int t = 16; t < 64; ++t) {
      const uint32_t s0 = ror(w[t - 15], 7) ^ ror(w[t - 15], 18) ^ (w[t - 15] >> 3);
      const uint32_t s1 = ror(w[t - 2], 17) ^ ror(w[t - 2], 19) ^ (w[t - 2] >> 10);
      w[t] = w[t - 16] + s0 + w[t - 7] + s1;
    }
    uint32_t a = h[0], b = h[1], c = h[2], d = h[3], e = h[4], f = h[5], g = h[6], hh = h[7];
    for (int t = 0; t < 64; ++t) {
      const uint32_t t1 = hh + (ror(e, 6) ^ ror(e, 11) ^ ror(e, 25)) + ((e & f) ^ (~e & g)) + K[t] + w[t];
      const uint32_t t2 = (ror(a, 2) ^ ror(a, 13) ^ ror(a, 22)) + ((a & b) ^ (a & c) ^ (b & c));
      hh = g; g = f; f = e; e = d + t1; d = c; c = b; b = a; a = t1 + t2;
    }
    h[0] += a; h[1] += b; h[2] += c; h[3] += d; h[4] += e; h[5] += f; h[6] += g; h[7] += hh;
  }
  void update(const uint8_t* p, size_t n) {
    len += n;
    while (n) {
      if (nbuf == 0 && n >= 64) { block(p); p += 64; n -= 64; continue; }
      const size_t k = std::min(n, 64 - nbuf);
      std::memcpy(buf + nbuf, p, k);
      nbuf += k; p += k; n -= k;
      if (nbuf == 64) { block(buf); nbuf = 0; }
    }
  }
  std::string hex() {
    const uint64_t bits = len * 8;
    uint8_t one = 0x80, zero = 0;
    update(&one, 1);
    while (nbuf != 56) update(&zero, 1);
    uint8_t L[8];
    for (int i = 0; i < 8; ++i) L[i] = uint8_t(bits >> (56 - 8 * i));
    update(L, 8);
    char s[65];
    for (int i = 0; i < 8; ++i) std::snprintf(s + 8 * i, 9, "%08x", h[i]);
    return std::string(s, 64);
  }
};
constexpr uint32_t Sha256::K[64];
std::string sha256hex(const std::vector<uint8_t>& d) {
  Sha256 s;
  s.update(d.data(), d.size());
  return s.hex();
}

inline uint64_t splitmix64(uint64_t& s) {
  uint64_t z = (s += 0x9E3779B97F4A7C15ull);
  z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9ull;
  z = (z ^ (z >> 27)) * 0x94D049BB133111EBull;
  return z ^ (z >> 31);
}

// ---------------------------------------------------------------- the network's shape
const uint32_t kKpad[MLP_NLAYERS] = {832, MLP_HID, MLP_HID, MLP_HID, MLP_HID};
const uint32_t kNpad[MLP_NLAYERS] = {MLP_HID, MLP_HID, MLP_HID, MLP_HID, MLP_OUT_PAD};
const uint32_t kKreal[MLP_NLAYERS] = {MLP_IN, MLP_HID, MLP_HID, MLP_HID, MLP_HID};
const uint32_t kNreal[MLP_NLAYERS] = {MLP_HID, MLP_HID, MLP_HID, MLP_HID, MLP_OUT};
const uint32_t kBiasBase[MLP_NLAYERS] = {0, MLP_HID, 2 * MLP_HID, 3 * MLP_HID, 4 * MLP_HID};

struct Weights {
  std::string name;
  uint32_t mult[4] = {0, 0, 0, 0};
  std::vector<int8_t> q[MLP_NLAYERS];     // [Kpad][Npad]
  std::vector<int32_t> b[MLP_NLAYERS];    // [Npad]
};

uint32_t rd32(const uint8_t* p) { uint32_t v; std::memcpy(&v, p, 4); return v; }
uint32_t be32(const uint8_t* p) { return (uint32_t(p[0]) << 24) | (uint32_t(p[1]) << 16) | (uint32_t(p[2]) << 8) | p[3]; }

bool parseWeights(const std::vector<uint8_t>& d, Weights& w, std::string& why) {
  if (d.size() < 256 || std::memcmp(d.data(), "MLPW0001", 8) != 0) { why = "not an MLPW0001 file"; return false; }
  if (rd32(&d[8]) != MLP_NLAYERS) { why = "layer count"; return false; }
  size_t need = 256;
  for (uint32_t l = 0; l < MLP_NLAYERS; ++l) {
    const uint8_t* p = &d[12 + 16 * l];
    if (rd32(p) != kKpad[l] || rd32(p + 4) != kNpad[l] || rd32(p + 8) != kKreal[l] || rd32(p + 12) != kNreal[l]) {
      why = "layer " + std::to_string(l + 1) + " shape";
      return false;
    }
    need += size_t(kKpad[l]) * kNpad[l] + 4 * size_t(kNpad[l]);
  }
  if (d.size() != need) { why = "size " + std::to_string(d.size()) + " != " + std::to_string(need); return false; }
  for (int i = 0; i < 4; ++i) {
    w.mult[i] = rd32(&d[92 + 4 * i]);
    if (w.mult[i] == 0 || w.mult[i] >= 0x80000000u) { why = "multiplier out of range"; return false; }
  }
  w.name.assign(reinterpret_cast<const char*>(&d[108]), strnlen(reinterpret_cast<const char*>(&d[108]), 32));
  size_t off = 256;
  for (uint32_t l = 0; l < MLP_NLAYERS; ++l) {
    const size_t n = size_t(kKpad[l]) * kNpad[l];
    w.q[l].resize(n);
    std::memcpy(w.q[l].data(), &d[off], n);
    off += n;
  }
  for (uint32_t l = 0; l < MLP_NLAYERS; ++l) {
    w.b[l].resize(kNpad[l]);
    std::memcpy(w.b[l].data(), &d[off], 4 * size_t(kNpad[l]));
    off += 4 * size_t(kNpad[l]);
  }
  // The padding must be zero: rows past K and columns past N carry no weight.
  for (uint32_t l = 0; l < MLP_NLAYERS; ++l)
    for (uint32_t k = 0; k < kKpad[l]; ++k)
      for (uint32_t n = 0; n < kNpad[l]; ++n)
        if ((k >= kKreal[l] || n >= kNreal[l]) && w.q[l][size_t(k) * kNpad[l] + n] != 0) {
          why = "nonzero padding weight in layer " + std::to_string(l + 1);
          return false;
        }
  return true;
}

bool parseImages(const std::vector<uint8_t>& d, std::vector<uint8_t>& px, uint32_t& n, std::string& why) {
  if (d.size() < 16 || be32(&d[0]) != 0x00000803u || be32(&d[8]) != 28 || be32(&d[12]) != 28) {
    why = "not an idx3 image file of 28 x 28";
    return false;
  }
  n = be32(&d[4]);
  if (d.size() != 16 + size_t(n) * 784) { why = "image file size"; return false; }
  px.assign(d.begin() + 16, d.end());
  return true;
}

bool parseLabels(const std::vector<uint8_t>& d, std::vector<uint8_t>& lab, std::string& why) {
  if (d.size() < 8 || be32(&d[0]) != 0x00000801u || d.size() != 8 + size_t(be32(&d[4]))) {
    why = "not an idx1 label file";
    return false;
  }
  lab.assign(d.begin() + 8, d.end());
  return true;
}

struct Expect {
  uint32_t groups = 0;
  std::vector<uint8_t> labels;     // [groups * 16]
  std::vector<uint32_t> checksum;  // [groups]
};
bool parseExpect(const std::vector<uint8_t>& d, Expect& e, std::string& why) {
  if (d.size() < 64 || std::memcmp(d.data(), "MLPE0001", 8) != 0) { why = "not an MLPE0001 file"; return false; }
  e.groups = rd32(&d[8]);
  if (d.size() != 64 + size_t(e.groups) * 16 + 4 * size_t(e.groups)) { why = "MLPE size"; return false; }
  e.labels.assign(d.begin() + 64, d.begin() + 64 + size_t(e.groups) * 16);
  e.checksum.resize(e.groups);
  std::memcpy(e.checksum.data(), &d[64 + size_t(e.groups) * 16], 4 * size_t(e.groups));
  return true;
}
bool parseLogits(const std::vector<uint8_t>& d, uint32_t& groups, std::vector<int32_t>& c5, std::string& why) {
  if (d.size() < 64 || std::memcmp(d.data(), "MLPL0001", 8) != 0) { why = "not an MLPL0001 file"; return false; }
  groups = rd32(&d[8]);
  if (d.size() != 64 + size_t(groups) * 1024) { why = "MLPL size"; return false; }
  c5.resize(size_t(groups) * 256);
  std::memcpy(c5.data(), &d[64], size_t(groups) * 1024);
  return true;
}

// ---------------------------------------------------------------- packing (the memory images the kernel reads)
// Input group g: 13 A tiles; tile t line i = image 16g + i, bytes = pixels 64t .. 64t+63 (zero past 784).
std::vector<uint8_t> packInput(const std::vector<uint8_t>& px, uint32_t nimages, uint32_t ngroups) {
  std::vector<uint8_t> out(size_t(ngroups) * MLP_INPUT_GROUP_BYTES, 0);
  for (uint32_t g = 0; g < ngroups; ++g)
    for (uint32_t i = 0; i < MLP_GROUP; ++i) {
      const uint32_t img = MLP_GROUP * g + i;
      if (img >= nimages) continue;
      for (uint32_t p = 0; p < MLP_IN; ++p)
        out[size_t(g) * MLP_INPUT_GROUP_BYTES + size_t(p / 64) * MLP_TILE_BYTES + i * 64 + p % 64] = px[size_t(img) * 784 + p];
    }
  return out;
}

// The chunk table in issue order and the packed B tiles: chunk (layer l, block c), k tile t: line p, bytes 4j..4j+3 =
// Q[64t + 4p .. 64t + 4p + 3][16c + j] (the order TensorIMA8A32 reads TenB).
void packWeights(const Weights& w, std::vector<MlpChunk>& ch, std::vector<int8_t>& tiles, std::vector<int32_t>& bias) {
  ch.clear();
  tiles.assign(size_t(MLP_NBTILES) * MLP_TILE_BYTES, 0);
  bias.assign(MLP_BIAS_INTS, 0);
  uint32_t wt = 0;
  for (uint32_t l = 0; l < MLP_NLAYERS; ++l) {
    const uint32_t nt = kKpad[l] / 64, nb = kNpad[l] / 16;
    for (uint32_t c = 0; c < nb; ++c) {
      MlpChunk k{};
      k.wtile = wt;
      k.ntiles = uint16_t(nt);
      k.layer = uint8_t(l);
      k.block = uint16_t(c);
      k.bias = uint16_t(kBiasBase[l] + 16 * c);
      for (uint32_t t = 0; t < nt; ++t, ++wt)
        for (uint32_t p = 0; p < 16; ++p)
          for (uint32_t j = 0; j < 16; ++j)
            for (uint32_t x = 0; x < 4; ++x)
              tiles[size_t(wt) * MLP_TILE_BYTES + p * 64 + 4 * j + x] =
                  w.q[l][size_t(64 * t + 4 * p + x) * kNpad[l] + 16 * c + j];
      ch.push_back(k);
    }
    for (uint32_t n = 0; n < kNpad[l]; ++n) bias[kBiasBase[l] + n] = w.b[l][n];
  }
}

// scp staging: chunk q is kept by the (q mod nshires)-th working shire, packed in issue order from line 4096.
// Returns the largest resident line count of any shire.
uint32_t assignOwners(std::vector<MlpChunk>& ch, uint64_t shireMask) {
  std::vector<uint32_t> shires;
  for (uint32_t s = 0; s < 32; ++s) if ((shireMask >> s) & 1) shires.push_back(s);
  std::vector<uint32_t> used(32, 0);
  uint32_t mx = 0;
  for (size_t q = 0; q < ch.size(); ++q) {
    const uint32_t s = shires[q % shires.size()];
    ch[q].owner = uint8_t(s);
    ch[q].res_line = MLP_RES_LINE0 + used[s];
    used[s] += 16u * ch[q].ntiles;
    mx = std::max(mx, used[s]);
  }
  return mx;
}

uint32_t tableSum(const std::vector<MlpChunk>& ch) {
  uint32_t s = 0;
  for (const auto& c : ch) s += c.wtile + c.ntiles + c.layer + c.block + c.bias;
  return s;
}

// ---------------------------------------------------------------- the host's reference of the kernel's arithmetic
// Emulates, for one input group, exactly what the kernel computes from the packed memory images: the TensorIMA8A32
// tile products (UA = 1: A unsigned; B signed; int32 accumulation, 4 products per 32-bit step), the requantization
// y = sat_u8(((acc + Bp) * M) >> 32) with fadd.pi's 32-bit wrap and fmulh.pi's floor, the bytes into the next A tile,
// and the output layer's logits, first-maximum labels and checksum.
struct RefOut {
  uint8_t label[16];
  uint32_t checksum;
  int32_t c5[256];
};
RefOut refGroup(const uint8_t* in13, const std::vector<int8_t>& tiles, const std::vector<MlpChunk>& ch,
                const std::vector<int32_t>& bias, const uint32_t mult[4]) {
  std::vector<uint8_t> P(28 * MLP_TILE_BYTES, 0), Q(28 * MLP_TILE_BYTES, 0);
  std::memcpy(P.data(), in13, MLP_INPUT_GROUP_BYTES);
  RefOut r{};
  for (const auto& c : ch) {
    const uint8_t* A = (c.layer & 1) ? Q.data() : P.data();
    uint8_t* O = (c.layer & 1) ? P.data() : Q.data();
    uint32_t C[16][16] = {};
    for (uint32_t t = 0; t < c.ntiles; ++t) {
      const int8_t* B = tiles.data() + size_t(c.wtile + t) * MLP_TILE_BYTES;
      for (uint32_t p = 0; p < 16; ++p)
        for (uint32_t i = 0; i < 16; ++i)
          for (uint32_t j = 0; j < 16; ++j) {
            int32_t s = 0;
            for (uint32_t x = 0; x < 4; ++x)
              s += int32_t(A[size_t(t) * MLP_TILE_BYTES + i * 64 + 4 * p + x]) * int32_t(B[p * 64 + 4 * j + x]);
            C[i][j] += uint32_t(s);
          }
    }
    if (c.layer < 4) {
      const int64_t M = mult[c.layer];
      for (uint32_t i = 0; i < 16; ++i)
        for (uint32_t j = 0; j < 16; ++j) {
          const int32_t v = int32_t(C[i][j] + uint32_t(bias[c.bias + j]));
          int64_t y = (int64_t(v) * M) >> 32;
          y = y < 0 ? 0 : (y > 255 ? 255 : y);
          O[size_t(c.block / 4) * MLP_TILE_BYTES + i * 64 + 16 * (c.block % 4) + j] = uint8_t(y);
        }
    } else {
      uint32_t sum = 0;
      for (uint32_t i = 0; i < 16; ++i) {
        int32_t best = 0;
        uint32_t arg = 0;
        for (uint32_t j = 0; j < 16; ++j) r.c5[16 * i + j] = int32_t(C[i][j]);
        for (uint32_t j = 0; j < MLP_OUT; ++j) {
          const int32_t v = int32_t(C[i][j] + uint32_t(bias[c.bias + j]));
          sum += uint32_t(v);
          if (j == 0 || v > best) { best = v; arg = j; }
        }
        r.label[i] = uint8_t(arg);
      }
      r.checksum = sum;
    }
  }
  return r;
}

// ---------------------------------------------------------------- options
struct Options {
  bool sysemu = false, card = false, dry = false, ref = false, selftest = false, debug = false, noPins = false;
  std::string simArgs, simExtra, images, weights, expect, expectLogits, trueLabels, split = "train", stage = "scp", out,
      labelsOut, refOut, pins = PINS_FILE, kernel = KERNEL_ELF;
  uint64_t passes = 1, groups = 0, shireMask = 0xffffffffull, perShire = 32, epoch = 0, refGroups = 2,
           pollLimit = 1ull << 26;
  double maxKernelS = 6.0, budget = 9.5;
};

[[noreturn]] void usage(const char* argv0, const std::string& why = "") {
  if (!why.empty()) std::fprintf(stderr, "%s: %s\n", argv0, why.c_str());
  std::fprintf(stderr,
               "usage: %s (--sysemu [--sim-args ARGS] [--sim-extra ARGS] | --card | --dry | --ref | --selftest) --images IDX --weights MLPW"
               " --expect MLPE [--expect-logits MLPL] [--true-labels IDX] [--split train|test] [--passes R | --groups N]"
               " [--shires MASK] [--per-shire P] [--stage scp|dram] [--debug-logits] [--epoch E] [--out FILE]"
               " [--labels-out FILE] [--pins FILE | --no-pins] [--max-kernel-s S] [--budget S] [--kernel ELF]"
               " [--poll-limit N] [--ref-groups N] [--ref-out FILE]\n",
               argv0);
  std::exit(2);
}

Options parse(int argc, char** argv) {
  Options o;
  for (int i = 1; i < argc; ++i) {
    const std::string a = argv[i];
    auto next = [&]() -> std::string {
      if (i + 1 >= argc) usage(argv[0], a + " needs a value");
      return argv[++i];
    };
    if (a == "--sysemu") o.sysemu = true;
    else if (a == "--card") o.card = true;
    else if (a == "--dry") o.dry = true;
    else if (a == "--ref") o.ref = true;
    else if (a == "--selftest") o.selftest = true;
    else if (a == "--sim-args") o.simArgs = next();
    else if (a == "--sim-extra") o.simExtra = next();
    else if (a == "--images") o.images = next();
    else if (a == "--weights") o.weights = next();
    else if (a == "--expect") o.expect = next();
    else if (a == "--expect-logits") o.expectLogits = next();
    else if (a == "--true-labels") o.trueLabels = next();
    else if (a == "--split") o.split = next();
    else if (a == "--passes") o.passes = std::stoull(next());
    else if (a == "--groups") o.groups = std::stoull(next());
    else if (a == "--shires") o.shireMask = std::stoull(next(), nullptr, 0);
    else if (a == "--per-shire") o.perShire = std::stoull(next());
    else if (a == "--stage") o.stage = next();
    else if (a == "--debug-logits") o.debug = true;
    else if (a == "--epoch") o.epoch = std::stoull(next(), nullptr, 0);
    else if (a == "--out") o.out = next();
    else if (a == "--labels-out") o.labelsOut = next();
    else if (a == "--pins") o.pins = next();
    else if (a == "--no-pins") o.noPins = true;
    else if (a == "--max-kernel-s") o.maxKernelS = std::stod(next());
    else if (a == "--budget") o.budget = std::stod(next());
    else if (a == "--kernel") o.kernel = next();
    else if (a == "--poll-limit") o.pollLimit = std::stoull(next(), nullptr, 0);
    else if (a == "--ref-groups") o.refGroups = std::stoull(next());
    else if (a == "--ref-out") o.refOut = next();
    else usage(argv[0], "unknown option " + a);
  }
  if (o.selftest) return o;
  if (int(o.sysemu) + int(o.card) + int(o.dry) + int(o.ref) != 1) usage(argv[0], "give exactly one of --sysemu, --card, --dry, --ref");
  if (o.images.empty() || o.weights.empty() || o.expect.empty()) usage(argv[0], "--images, --weights and --expect are required");
  if (o.split != "train" && o.split != "test") usage(argv[0], "--split train|test");
  if (o.stage != "scp" && o.stage != "dram") usage(argv[0], "--stage scp|dram");
  if ((o.shireMask & 0xffffffffull) == 0 || (o.shireMask >> 32)) usage(argv[0], "--shires: a mask of shires 0-31");
  if (o.perShire < 1 || o.perShire > 32) usage(argv[0], "--per-shire 1-32");
  if (o.passes < 1 || o.passes > 1000) usage(argv[0], "--passes 1-1000");
  if (o.budget > 9.5) usage(argv[0], "--budget at most 9.5 s");
  if (o.debug && o.expectLogits.empty() && !o.dry) usage(argv[0], "--debug-logits needs --expect-logits");
  return o;
}

// The guard's model of one launch on a card at 600 MHz, deliberately slow (so it refuses early): 700 cycles per
// TensorIMA8A32 (the design's band tops at 589) and 1,500 cycles per chunk for the epilogue and the barrier, on the
// shire with the most rounds, plus 2 ms.
double modelSeconds(uint64_t rounds, uint64_t nshires) {
  const double perShire = double((rounds + nshires - 1) / nshires);
  return perShire * (double(MLP_NBTILES) * 700.0 + double(MLP_NCHUNKS) * 1500.0) / 600e6 + 0.002;
}

// ---------------------------------------------------------------- the device (workloads/ledger's Session)
class Session {
public:
  Session(const Options& o, const std::vector<uint8_t>& elf, uint64_t& scpKBPerShire) : o_(o), tOpen_(Clock::now()) {
    if (o.sysemu) {
      emu::SysEmuOptions s;
      s.bootromTrampolineToBL2ElfPath = BOOTROM_TRAMPOLINE_TO_BL2_ELF;
      s.spBL2ElfPath = BL2_ELF;
      s.masterMinionElfPath = MASTER_MINION_ELF;
      s.machineMinionElfPath = MACHINE_MINION_ELF;
      s.workerMinionElfPath = WORKER_MINION_ELF;
      s.executablePath = fs::path(SYSEMU_INSTALL_DIR) / "sys_emu";
      s.runDir = fs::current_path();
      s.maxCycles = std::numeric_limits<uint64_t>::max();
      s.minionShiresMask = 0x1FFFFFFFFu;
      s.puUart0Path = s.runDir + "/pu_uart0_tx.log";
      s.puUart1Path = s.runDir + "/pu_uart1_tx.log";
      s.spUart0Path = s.runDir + "/spio_uart0_tx.log";
      s.spUart1Path = s.runDir + "/spio_uart1_tx.log";
      s.startGdb = false;
      std::istringstream extra(o.simArgs + " " + o.simExtra);
      for (std::string arg; extra >> arg;) s.additionalOptions.push_back(arg);
      dl_ = dev::IDeviceLayer::createSysEmuDeviceLayer(s, 1);
    } else if (o.card) {
      dl_ = dev::IDeviceLayer::createPcieDeviceLayer(true, false);  // ops node only
    } else {
      throw std::runtime_error("no device chosen");
    }
    rt_ = rt::IRuntime::create(dl_);
    const auto devices = rt_->getDevices();
    if (devices.empty()) throw std::runtime_error("no ET devices found");
    dev_ = devices[0];
    {
      // The device reports the whole chip's scratchpad in MB over its compute shires (workloads/sparseparity).
      const auto props = rt_->getDeviceProperties(dev_);
      const int nsh = __builtin_popcount(props.computeMinionShireMask_ & 0xFFFFFFFFu);
      scpKBPerShire = (props.l2scratchpadSize_ && nsh) ? uint64_t(props.l2scratchpadSize_) * 1024 / uint64_t(nsh) : 0;
    }
    stream_ = rt_->createStream(dev_);
    const auto load = rt_->loadCode(stream_, reinterpret_cast<const std::byte*>(elf.data()), elf.size());
    rt_->waitForEvent(load.event_);
    kernel_ = load.kernel_;
    std::fprintf(stderr, "device ready in %.2f s\n", secondsSince(tOpen_));
  }
  ~Session() {
    for (auto* p : allocs_) rt_->freeDevice(dev_, p);
    rt_->unloadCode(kernel_);
    rt_->destroyStream(stream_);
    std::fprintf(stderr, "device held for %.2f s\n", secondsSince(tOpen_));
  }
  std::byte* alloc(size_t bytes) {
    allocs_.push_back(rt_->mallocDevice(dev_, std::max<size_t>(bytes, 64), 4096));
    return allocs_.back();
  }
  void put(const void* src, std::byte* dst, size_t bytes) {
    rt_->memcpyHostToDevice(stream_, reinterpret_cast<const std::byte*>(src), dst, bytes);
    rt_->waitForStream(stream_);
  }
  void get(const std::byte* src, void* dst, size_t bytes) {
    rt_->memcpyDeviceToHost(stream_, src, reinterpret_cast<std::byte*>(dst), bytes);
    rt_->waitForStream(stream_);
  }
  long long t0Ms = 0, t1Ms = 0;
  bool launch(const MlpArgs& a, int timeoutS, double& wallS) {
    rt::KernelLaunchOptions opts;
    opts.setShireMask(a.shire_mask);
    opts.setBarrier(true);
    t0Ms = epochMs();
    const auto t0 = Clock::now();
    rt_->kernelLaunch(stream_, kernel_, reinterpret_cast<const std::byte*>(&a), sizeof(a), opts);
    bool ok = rt_->waitForStream(stream_, std::chrono::seconds(timeoutS));
    wallS = secondsSince(t0);
    t1Ms = epochMs();
    if (!ok) {
      std::fprintf(stderr, "kernel did not finish within %d s, aborting the stream\n", timeoutS);
      rt_->waitForEvent(rt_->abortStream(stream_));
      return false;
    }
    for (const auto& e : rt_->retrieveStreamErrors(stream_)) {
      std::fprintf(stderr, "stream error: %s\n", e.getString().c_str());
      ok = false;
    }
    return ok;
  }

private:
  const Options& o_;
  Clock::time_point tOpen_;
  std::shared_ptr<dev::IDeviceLayer> dl_;
  rt::RuntimePtr rt_;
  rt::DeviceId dev_{};
  rt::StreamId stream_{};
  rt::KernelId kernel_{};
  std::vector<std::byte*> allocs_;
};

// ---------------------------------------------------------------- self-test (CPU only)
int selftest() {
  int bad = 0;
  auto check = [&](const char* what, bool ok) {
    std::printf("SELFTEST %-44s %s\n", what, ok ? "OK" : "MISMATCH");
    bad += !ok;
  };
  {
    Sha256 s;
    s.update(reinterpret_cast<const uint8_t*>("abc"), 3);
    check("sha256(abc)", s.hex() == "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad");
  }
  {
    uint64_t s = 0;  // splitmix64 from seed 0: the first output (the generator's published test value)
    check("splitmix64(0) first output", splitmix64(s) == 0xE220A8397B1DCDAFull);
  }
  // The B-tile interleave: a random 64 x 16 block and 16 x 64 A, the packed TensorIMA8A32 order against a direct product.
  {
    uint64_t s = 0xE202;
    Weights w;
    for (uint32_t l = 0; l < MLP_NLAYERS; ++l) {
      w.q[l].assign(size_t(kKpad[l]) * kNpad[l], 0);
      w.b[l].assign(kNpad[l], 0);
    }
    for (uint32_t k = 0; k < 64; ++k)
      for (uint32_t n = 0; n < 16; ++n) w.q[1][size_t(k) * MLP_HID + 16 * 5 + n] = int8_t(splitmix64(s) & 0xFF);
    std::vector<MlpChunk> ch;
    std::vector<int8_t> tiles;
    std::vector<int32_t> bias;
    packWeights(w, ch, tiles, bias);
    const MlpChunk& c = ch[MLP_HID_BLOCKS + 5];  // layer 2, block 5
    uint8_t A[16][64];
    for (auto& r : A) for (auto& v : r) v = uint8_t(splitmix64(s) & 0xFF);
    bool ok = c.layer == 1 && c.block == 5 && c.ntiles == 28;
    for (uint32_t i = 0; i < 16 && ok; ++i)
      for (uint32_t j = 0; j < 16 && ok; ++j) {
        int64_t direct = 0, packed = 0;
        for (uint32_t k = 0; k < 64; ++k) direct += int64_t(A[i][k]) * w.q[1][size_t(k) * MLP_HID + 16 * 5 + j];
        const int8_t* B = tiles.data() + size_t(c.wtile) * MLP_TILE_BYTES;
        for (uint32_t p = 0; p < 16; ++p)
          for (uint32_t x = 0; x < 4; ++x) packed += int64_t(A[i][4 * p + x]) * B[p * 64 + 4 * j + x];
        ok = direct == packed;
      }
    check("B-tile interleave vs direct product", ok);
    uint32_t tot = 0;
    for (const auto& k : ch) tot += k.ntiles;
    check("449 chunks, 10,892 tiles", ch.size() == MLP_NCHUNKS && tot == MLP_NBTILES);
    const uint32_t mx = assignOwners(ch, 0xffffffffull);
    check("scp resident layout fits 360 tiles a shire", mx <= MLP_RES_LINES_MAX);
  }
  // The requantization's floor and saturation (fmulh.pi = floor(p / 2^32); fsatu8.pi clamps to 0..255).
  {
    auto rq = [](int32_t acc, int32_t bp, uint32_t M) {
      int64_t y = (int64_t(int32_t(uint32_t(acc) + uint32_t(bp))) * int64_t(M)) >> 32;
      return y < 0 ? 0 : (y > 255 ? 255 : int(y));
    };
    check("requant: -1 x M floors below 0 -> 0", rq(-1, 0, 4492549) == 0);
    check("requant: exact 2^32 / M steps", rq(956, 0, 4492549) == 0 && rq(957, 0, 4492549) == 1);
    check("requant: saturates at 255", rq(1 << 24, 0, 4492549) == 255);
  }
  std::printf("SELFTEST %s\n", bad ? "FAIL" : "PASS");
  return bad ? 1 : 0;
}

struct Pins {
  bool off = false;
  std::map<std::string, std::string> byName;
  std::vector<std::string> log;
  bool ok = true;
  std::string firstBad;
};

void pinCheck(Pins& pins, const std::string& path, const std::vector<uint8_t>& data) {
  const std::string h = sha256hex(data), name = fs::path(path).filename().string();
  std::string verdict;
  if (pins.off) verdict = "UNPINNED";
  else {
    auto it = pins.byName.find(name);
    verdict = it == pins.byName.end() ? "NOT LISTED" : (it->second == h ? "OK" : "MISMATCH");
    if (verdict != "OK" && pins.ok) { pins.ok = false; pins.firstBad = name + " " + verdict; }
  }
  pins.log.push_back("{\"file\":\"" + name + "\",\"sha256\":\"" + h + "\",\"pin\":\"" + verdict + "\"}");
}

}  // namespace

int main(int argc, char** argv) {
  registerRuntimeLogLevels();
  const Options o = parse(argc, argv);
  if (o.selftest) return selftest();
  std::ostringstream js;
  auto finish = [&](const std::string& status, int rc) {
    js << ",\"status\":\"" << status << "\"}";
    const std::string line = js.str();
    std::printf("%s\n", line.c_str());
    std::fflush(stdout);
    if (!o.out.empty()) {
      std::ofstream f(o.out);
      f << line << "\n";
    }
    return rc;
  };
  const char* device = o.sysemu ? "sysemu" : (o.card ? "card" : (o.dry ? "dry" : "ref"));
  js << "{\"mnistmlp\":1,\"device\":\"" << device << "\",\"split\":\"" << o.split << "\",\"stage\":\"" << o.stage
     << "\",\"debug_logits\":" << (o.debug ? "true" : "false");

  // ---- inputs, pinned
  Pins pins;
  pins.off = o.noPins;
  if (!pins.off) {
    std::ifstream pf(o.pins);
    if (!pf) { std::fprintf(stderr, "cannot read pins %s\n", o.pins.c_str()); js << ",\"why\":\"no pins file\""; return finish("REFUSED", 2); }
    for (std::string line; std::getline(pf, line);) {
      std::istringstream ls(line);
      std::string h, n;
      if (ls >> h >> n && h.size() == 64) pins.byName[fs::path(n[0] == '*' ? n.substr(1) : n).filename().string()] = h;
    }
  }
  std::string why;
  const auto dImg = readFile(o.images), dW = readFile(o.weights), dE = readFile(o.expect);
  if (dImg.empty() || dW.empty() || dE.empty()) { js << ",\"why\":\"cannot read an input\""; return finish("REFUSED", 2); }
  pinCheck(pins, o.images, dImg);
  pinCheck(pins, o.weights, dW);
  pinCheck(pins, o.expect, dE);
  std::vector<uint8_t> px, trueLab;
  uint32_t nimg = 0;
  Weights w;
  Expect ex;
  if (!parseImages(dImg, px, nimg, why) || !parseWeights(dW, w, why) || !parseExpect(dE, ex, why)) {
    js << ",\"why\":\"" << why << "\"";
    return finish("REFUSED", 2);
  }
  std::vector<int32_t> exC5;
  uint32_t exC5Groups = 0;
  if (!o.expectLogits.empty()) {
    const auto dL = readFile(o.expectLogits);
    pinCheck(pins, o.expectLogits, dL);
    if (!parseLogits(dL, exC5Groups, exC5, why)) { js << ",\"why\":\"" << why << "\""; return finish("REFUSED", 2); }
  }
  if (!o.trueLabels.empty()) {
    const auto dT = readFile(o.trueLabels);
    pinCheck(pins, o.trueLabels, dT);
    if (!parseLabels(dT, trueLab, why) || trueLab.size() != nimg) { js << ",\"why\":\"true labels: " << why << "\""; return finish("REFUSED", 2); }
  }
  js << ",\"inputs\":[";
  for (size_t i = 0; i < pins.log.size(); ++i) js << (i ? "," : "") << pins.log[i];
  js << "],\"pins\":\"" << (pins.off ? "OFF" : (pins.ok ? "OK" : "FAIL")) << "\",\"weights_name\":\"" << w.name << "\"";
  if (!pins.ok) { js << ",\"why\":\"pin " << pins.firstBad << "\""; return finish("REFUSED", 2); }
  const uint32_t splitGroups = o.split == "train" ? MLP_TRAIN_GROUPS : MLP_TEST_GROUPS;
  if (nimg != splitGroups * MLP_GROUP || ex.groups != splitGroups) {
    js << ",\"why\":\"the images or the expected file do not match the split\"";
    return finish("REFUSED", 2);
  }
  if (!exC5.empty() && exC5Groups != splitGroups) { js << ",\"why\":\"logits file groups\""; return finish("REFUSED", 2); }

  // ---- the plan
  const uint64_t gpp = splitGroups;
  const uint64_t groups = o.groups ? o.groups : o.passes * gpp;
  const uint64_t nsh = uint64_t(__builtin_popcountll(o.shireMask & 0xffffffffull)), P = o.perShire;
  const uint64_t rounds = (groups + P - 1) / P;
  const uint64_t ngin = std::min<uint64_t>(groups, gpp);
  const bool dram = o.stage == "dram";
  std::vector<MlpChunk> ch;
  std::vector<int8_t> tiles;
  std::vector<int32_t> bias;
  packWeights(w, ch, tiles, bias);
  uint32_t resLines = 0;
  if (!dram) resLines = assignOwners(ch, o.shireMask);
  const std::vector<uint8_t> input = packInput(px, nimg, uint32_t(ngin));
  const double model = modelSeconds(rounds, nsh);
  uint64_t epoch = o.epoch ? o.epoch : (uint64_t(epochMs()) & 0xFFFFFFFFull);
  if ((epoch & 0xFFFF) == 0) epoch |= 1;
  js << ",\"gpp\":" << gpp << ",\"groups\":" << groups << ",\"passes\":" << (o.groups ? 0 : o.passes)
     << ",\"shire_mask\":\"0x" << std::hex << o.shireMask << std::dec << "\",\"nshires\":" << nsh
     << ",\"per_shire\":" << P << ",\"rounds\":" << rounds << ",\"input_groups_copied\":" << ngin
     << ",\"resident_lines_max\":" << resLines << ",\"epoch\":" << epoch << ",\"model_s\":" << model
     << ",\"ops_per_group\":" << MLP_NBTILES << ",\"macs_issued_per_image\":11153408"
     << ",\"weights_mult\":[" << w.mult[0] << "," << w.mult[1] << "," << w.mult[2] << "," << w.mult[3] << "]";
  if (!dram && resLines > MLP_RES_LINES_MAX) {
    js << ",\"why\":\"scp staging: the resident chunks need " << resLines << " lines in a shire (at most "
       << MLP_RES_LINES_MAX << "): use more shires or --stage dram\"";
    return finish("REFUSED", 2);
  }

  // ---- --ref: the host's reference on the first groups (no device)
  if (o.ref) {
    const uint64_t n = std::min<uint64_t>(o.refGroups, ngin);
    uint64_t labBad = 0, sumBad = 0, c5Bad = 0, c5Checked = 0;
    std::string first;
    std::vector<uint8_t> outFile;
    if (!o.refOut.empty()) {
      outFile.assign(64, 0);
      std::memcpy(outFile.data(), "MLPR0001", 8);
      const uint32_t n32 = uint32_t(n);
      std::memcpy(&outFile[8], &n32, 4);
    }
    for (uint64_t g = 0; g < n; ++g) {
      const RefOut r = refGroup(input.data() + g * MLP_INPUT_GROUP_BYTES, tiles, ch, bias, w.mult);
      for (int i = 0; i < 16; ++i)
        if (r.label[i] != ex.labels[g * 16 + i]) { ++labBad; if (first.empty()) first = "group " + std::to_string(g) + " label"; }
      if (r.checksum != ex.checksum[g]) { ++sumBad; if (first.empty()) first = "group " + std::to_string(g) + " checksum"; }
      if (!exC5.empty()) {
        ++c5Checked;
        if (std::memcmp(r.c5, &exC5[g * 256], 1024) != 0) { ++c5Bad; if (first.empty()) first = "group " + std::to_string(g) + " logits"; }
      }
      if (!o.refOut.empty()) {
        outFile.insert(outFile.end(), r.label, r.label + 16);
        const uint8_t* cs = reinterpret_cast<const uint8_t*>(&r.checksum);
        outFile.insert(outFile.end(), cs, cs + 4);
        outFile.insert(outFile.end(), 12, 0);
        const uint8_t* c5 = reinterpret_cast<const uint8_t*>(r.c5);
        outFile.insert(outFile.end(), c5, c5 + 1024);
      }
    }
    if (!o.refOut.empty()) {
      std::ofstream f(o.refOut, std::ios::binary);
      f.write(reinterpret_cast<const char*>(outFile.data()), std::streamsize(outFile.size()));
    }
    js << ",\"ref_groups\":" << n << ",\"ref_label_mismatches\":" << labBad << ",\"ref_checksum_mismatches\":" << sumBad
       << ",\"ref_logit_tiles_checked\":" << c5Checked << ",\"ref_logit_tile_mismatches\":" << c5Bad
       << ",\"first_mismatch\":\"" << first << "\"";
    const bool pass = n > 0 && labBad == 0 && sumBad == 0 && c5Bad == 0;
    return finish(pass ? "PASS" : "FAIL", pass ? 0 : 1);
  }
  if (o.dry) return finish("DRY", 0);
  if (o.card && model > o.maxKernelS) {
    js << ",\"why\":\"model " << model << " s over --max-kernel-s " << o.maxKernelS << "\"";
    return finish("REFUSED", 3);
  }

  const auto elf = readFile(o.kernel);
  if (elf.empty()) { js << ",\"why\":\"cannot read kernel " << o.kernel << "\""; return finish("REFUSED", 2); }
  js << ",\"kernel_sha256\":\"" << sha256hex(elf) << "\"";

  // ---- the device: copy in, poison, launch, read back, close
  const uint64_t nLines = groups + 1024;
  std::vector<MlpLabel> lab(nLines);
  std::vector<MlpRecord> rec(1024);
  std::vector<int32_t> c5(o.debug ? (groups + 1024) * 256 : 0);
  bool launchOk = false;
  double wall = 0;
  long long t0Ms = 0, t1Ms = 0;
  uint64_t scpKB = 0;
  {
    Session ses(o, elf, scpKB);
    js << ",\"device_scp_kb_per_shire\":" << scpKB;
    if (scpKB && uint64_t(MLP_LAYOUT_END_LINE) * 64 > scpKB * 1024) {
      js << ",\"why\":\"the scratchpad layout ends at " << MLP_LAYOUT_END_LINE * 64 / 1024 << " KB, the device reports "
         << scpKB << " KB per shire\"";
      return finish("REFUSED", 2);
    }
    std::byte* dIn = ses.alloc(input.size());
    std::byte* dW = ses.alloc(tiles.size());
    std::byte* dCh = ses.alloc(ch.size() * sizeof(MlpChunk));
    std::byte* dB = ses.alloc(bias.size() * 4);
    std::byte* dLab = ses.alloc(nLines * 64);
    std::byte* dRec = ses.alloc(1024 * sizeof(MlpRecord));
    std::byte* dCnt = ses.alloc(64);
    std::byte* dLog = o.debug ? ses.alloc(c5.size() * 4) : nullptr;
    ses.put(input.data(), dIn, input.size());
    ses.put(tiles.data(), dW, tiles.size());
    ses.put(ch.data(), dCh, ch.size() * sizeof(MlpChunk));
    ses.put(bias.data(), dB, bias.size() * 4);
    // Poison: a pattern no kernel line has, so a skipped store shows.
    std::vector<uint8_t> poison(nLines * 64, 0xA5);
    ses.put(poison.data(), dLab, poison.size());
    std::vector<uint8_t> rpoison(1024 * sizeof(MlpRecord), 0x5A);
    ses.put(rpoison.data(), dRec, rpoison.size());
    std::vector<uint8_t> zero(64, 0);
    ses.put(zero.data(), dCnt, 64);
    if (o.debug) {
      std::vector<uint8_t> lp(c5.size() * 4, 0xA5);
      ses.put(lp.data(), dLog, lp.size());
    }
    MlpArgs a{};
    a.magic = MLP_MAGIC;
    a.epoch = epoch;
    a.flags = (dram ? MLP_F_STAGE_DRAM : 0) | (o.debug ? MLP_F_DEBUG_LOGITS : 0);
    a.shire_mask = o.shireMask;
    a.per_shire = P;
    a.nshires = nsh;
    a.groups = groups;
    a.gpp = gpp;
    a.rounds = rounds;
    a.input = reinterpret_cast<uint64_t>(dIn);
    a.wtiles = reinterpret_cast<uint64_t>(dW);
    a.chunks = reinterpret_cast<uint64_t>(dCh);
    a.bias = reinterpret_cast<uint64_t>(dB);
    a.labels = reinterpret_cast<uint64_t>(dLab);
    a.logits = reinterpret_cast<uint64_t>(dLog);
    a.records = reinterpret_cast<uint64_t>(dRec);
    a.counter = reinterpret_cast<uint64_t>(dCnt);
    a.poll_limit = o.pollLimit;
    for (int i = 0; i < 4; ++i) a.mult[i] = w.mult[i];
    a.table_magic = MLP_TABLE_MAGIC;
    a.table_sum = tableSum(ch);
    int timeoutS = 7200;
    if (o.card) {
      const double left = o.budget - secondsSince(kStart);
      timeoutS = int(std::min({8.0, 2.0 * model + 1.5, left}));
      if (timeoutS < 1 || left < model + 0.5) {
        js << ",\"why\":\"budget spent before the launch\"";
        return finish("REFUSED", 3);
      }
    }
    launchOk = ses.launch(a, timeoutS, wall);
    t0Ms = ses.t0Ms;
    t1Ms = ses.t1Ms;
    if (launchOk) {
      ses.get(dLab, lab.data(), nLines * 64);
      ses.get(dRec, rec.data(), rec.size() * sizeof(MlpRecord));
      if (o.debug) ses.get(dLog, c5.data(), c5.size() * 4);
    }
  }

  // ---- checks
  uint64_t recOk = 0, recBad = 0, opsSum = 0, groupsSum = 0, padSum = 0, teAny = 0;
  uint64_t cycMax = 0, cycMin = ~0ull, workMax = 0, waitMax = 0, copyMax = 0;
  double cycSum = 0, workSum = 0, waitSum = 0;
  std::string first;
  std::vector<uint64_t> roundsOf(32, 0);
  {
    std::vector<uint32_t> shires;
    for (uint32_t s = 0; s < 32; ++s) if ((o.shireMask >> s) & 1) shires.push_back(s);
    for (uint64_t rho = 0; rho < rounds; ++rho) ++roundsOf[shires[rho % shires.size()]];
  }
  for (uint32_t s = 0; s < 32 && launchOk; ++s) {
    if (!((o.shireMask >> s) & 1)) continue;
    for (uint32_t m = 0; m < P; ++m) {
      const MlpRecord& r = rec[s * 32 + m];
      const bool ok = r.magic == MLP_REC_MAGIC && (r.status >> 16) == (epoch & 0xFFFF) && (r.status & 0xFFFF) == 0 &&
                      r.tensor_error == 0 && r.groups == roundsOf[s] && r.ops == uint64_t(r.groups) * MLP_NBTILES &&
                      r.barriers == r.groups * MLP_NCHUNKS;
      if (ok) ++recOk;
      else {
        ++recBad;
        if (first.empty()) {
          char b[160];
          std::snprintf(b, sizeof b, "record shire %u minion %u status 0x%08x groups %u ops %llu barriers %u", s, m,
                        r.status, r.groups, (unsigned long long)r.ops, r.barriers);
          first = b;
        }
      }
      teAny |= r.tensor_error;
      opsSum += r.ops;
      groupsSum += r.groups;
      padSum += r.pad_groups;
      cycMax = std::max<uint64_t>(cycMax, r.cycles);
      cycMin = std::min<uint64_t>(cycMin, r.cycles);
      workMax = std::max<uint64_t>(workMax, r.work_cycles);
      waitMax = std::max<uint64_t>(waitMax, r.wait_cycles);
      copyMax = std::max<uint64_t>(copyMax, r.copy_cycles);
      cycSum += double(r.cycles);
      workSum += double(r.work_cycles);
      waitSum += double(r.wait_cycles);
    }
  }
  const uint64_t working = nsh * P;
  uint64_t lineBad = 0, labBad = 0, sumBad = 0, discardOk = 0, discardBad = 0, c5Checked = 0, c5Bad = 0, correct = 0, scored = 0;
  for (uint64_t G = 0; G < groups && launchOk; ++G) {
    const MlpLabel& L = lab[G];
    const uint64_t gin = G % gpp;
    if (L.group != uint32_t(G) || L.epoch != uint32_t(epoch) || L.flags != MLP_LBL_DONE || L.input_group != gin) {
      ++lineBad;
      if (first.empty()) first = "label line " + std::to_string(G) + " not written by this launch";
      continue;
    }
    if (std::memcmp(L.label, &ex.labels[gin * 16], 16) != 0) {
      ++labBad;
      if (first.empty()) first = "label line " + std::to_string(G) + " labels";
    }
    if (L.checksum != ex.checksum[gin]) {
      ++sumBad;
      if (first.empty()) first = "label line " + std::to_string(G) + " checksum";
    }
    if (o.debug) {
      ++c5Checked;
      if (std::memcmp(&c5[G * 256], &exC5[gin * 256], 1024) != 0) {
        ++c5Bad;
        if (first.empty()) first = "logits of group " + std::to_string(G);
      }
    }
    if (!trueLab.empty() && G < gpp)
      for (int i = 0; i < 16; ++i) { ++scored; correct += L.label[i] == trueLab[gin * 16 + i]; }
  }
  // Discard lines: one per minion slot that took a padding group.
  for (uint32_t s = 0; s < 32 && launchOk; ++s) {
    if (!((o.shireMask >> s) & 1)) continue;
    for (uint32_t m = 0; m < P; ++m) {
      const MlpRecord& r = rec[s * 32 + m];
      if (r.magic != MLP_REC_MAGIC || r.pad_groups == 0) continue;
      const MlpLabel& L = lab[groups + s * 32 + m];
      const bool ok = L.group == uint32_t(groups + s * 32 + m) && L.epoch == uint32_t(epoch) &&
                      L.flags == (MLP_LBL_DONE | MLP_LBL_DISCARD) && L.slot == s * 32 + m && L.input_group == 0;
      ok ? ++discardOk : ++discardBad;
    }
  }
  if (!o.labelsOut.empty() && launchOk) {
    std::ofstream f(o.labelsOut, std::ios::binary);
    f.write(reinterpret_cast<const char*>(lab.data()), std::streamsize(groups * 64));
  }
  const uint64_t opsExpect = (groups + padSum) * MLP_NBTILES;
  // Every round has P group slots (one per working minion of its shire): groups real, the rest padding.
  // core: every check but the debug logits; logits: the debug path alone (its TensorStore of 64 B rows from register
  // pairs is a form no lab kernel has run on silicon, so a kit may read a logits-only failure apart from the rest).
  const bool corePass = launchOk && recBad == 0 && recOk == working && opsSum == opsExpect && groupsSum == rounds * P &&
                        padSum == rounds * P - groups && discardOk == padSum && lineBad == 0 &&
                        labBad == 0 && sumBad == 0 && discardBad == 0;
  const bool logitsPass = launchOk && c5Bad == 0 && c5Checked == groups;
  const bool pass = corePass && (!o.debug || logitsPass);
  js << ",\"launch_ok\":" << (launchOk ? "true" : "false") << ",\"wall_s\":" << wall << ",\"launch_epoch_ms\":["
     << t0Ms << "," << t1Ms << "],\"working_minions\":" << working << ",\"records_ok\":" << recOk
     << ",\"records_bad\":" << recBad << ",\"groups_done\":" << groupsSum << ",\"pad_groups\":" << padSum
     << ",\"ops\":" << opsSum << ",\"ops_expected\":" << opsExpect << ",\"tensor_error_or\":" << teAny
     << ",\"hart0_cycles\":{\"max\":" << cycMax << ",\"min\":" << (recOk + recBad ? cycMin : 0) << ",\"mean\":"
     << (working ? cycSum / double(working) : 0.0) << "},\"work_cycles\":{\"max\":" << workMax << ",\"mean\":"
     << (working ? workSum / double(working) : 0.0) << "},\"wait_cycles\":{\"max\":" << waitMax << ",\"mean\":"
     << (working ? waitSum / double(working) : 0.0) << "},\"copy_cycles_max\":" << copyMax
     << ",\"label_lines_bad\":" << lineBad << ",\"label_mismatches\":" << labBad << ",\"checksum_mismatches\":" << sumBad
     << ",\"discard_lines_ok\":" << discardOk << ",\"discard_lines_bad\":" << discardBad
     << ",\"logit_tiles_checked\":" << c5Checked << ",\"logit_tile_mismatches\":" << c5Bad;
  if (scored) js << ",\"accuracy\":{\"correct\":" << correct << ",\"scored\":" << scored << "}";
  js << ",\"first_mismatch\":\"" << first << "\",\"core_status\":\"" << (corePass ? "PASS" : "FAIL")
     << "\",\"logits_status\":\"" << (!o.debug ? "NOT CHECKED" : (logitsPass ? "PASS" : "FAIL")) << "\"";
  return finish(pass ? "PASS" : "FAIL", pass ? 0 : 1);
}
