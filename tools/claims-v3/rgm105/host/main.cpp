// Sparse-compute probes on ET-SoC-1 (see ../README.md). Every measurement prints one line
//   SPARSITY {json}
//
//   sparsity_host [--sysemu] --test fma --type fp32|fp16|int8 --pattern elem|col|row|pair|none
//                 [--sweep 0,0.5,0.9] [--b-sparsity S] [--b-stream] [--row-mask 0xFFFF] [--iters N]
//   sparsity_host [--sysemu] --test tload --where dram|l2|scp [--masks 0xFFFF,0xFF,0x1,0] [--iters N]
//   sparsity_host [--sysemu] --test gemv [--sweep 0,0.9,0.99] [--gemv dense|masked|skip] [--iters N]
//   sparsity_host [--sysemu] --test diverge --variant static|refill|scalar [--alpha 1.5] [--mean-k 64]
//                 [--items N] [--harts 1|2]
//   sparsity_host [--sysemu] --test spin
// Common: [--shires MASK] [--per-shire N] [--seconds T] [--seed S] [--budget S]
//
// Inputs are small integers, so every fp32, fp16 and int8 result is exact and is checked on the host.
// With --seconds T a test repeats its launch for about T seconds (for the power logger).
// The card is shared: the device is open only while measuring, and --budget (default 8 s on silicon)
// stops further launches.
#include <g3log/loglevels.hpp>
#include <runtime/IRuntime.h>
#include <runtime/Types.h>
#include <device-layer/IDeviceLayer.h>
#include <sw-sysemu/SysEmuOptions.h>

#include <algorithm>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <filesystem>
#include <fstream>
#include <limits>
#include <map>
#include <random>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

#include "Constants.h"
#include "sparsity_args.h"

// libetrt's thread-pool workers log at the custom levels VERBOSE_HIGH/MID/LOW, which only logging::LoggerDefault
// registers with g3log. Left unregistered, the first log call from several new workers inserts the level into g3log's
// level map from all of them at once and can corrupt it: aifoundry3's host crash about 1.08 s into 1 launch in 100
// (docs/findings/14-card-behaviour.md, "Traps"). Registering them, disabled as the map's default would leave them,
// before the runtime starts any thread removes the race.
static void registerRuntimeLogLevels() {
  const LEVELS levels[] = {LEVELS(g3::kDebugValue - 100, "VERBOSE_HIGH"), LEVELS(g3::kDebugValue - 99, "VERBOSE_MID"),
                           LEVELS(g3::kDebugValue - 98, "VERBOSE_LOW")};
  for (const auto& l : levels) g3::only_change_at_initialization::addLogLevel(l, false);
}

namespace fs = std::filesystem;
using Clock = std::chrono::steady_clock;

namespace {

double secondsSince(Clock::time_point t0) {
  return std::chrono::duration<double>(Clock::now() - t0).count();
}

long long epochMs() {
  return std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::system_clock::now().time_since_epoch())
    .count();
}

std::vector<std::byte> readFile(const std::string& path) {
  std::ifstream file(path, std::ios::binary);
  if (!file) {
    return {};
  }
  std::vector<std::byte> data(fs::file_size(path));
  file.read(reinterpret_cast<char*>(data.data()), static_cast<std::streamsize>(data.size()));
  return data;
}

std::vector<double> parseDoubles(const std::string& s) {
  std::vector<double> out;
  std::stringstream ss(s);
  for (std::string item; std::getline(ss, item, ',');) {
    if (!item.empty()) {
      out.push_back(std::atof(item.c_str()));
    }
  }
  return out;
}

std::vector<uint64_t> parseInts(const std::string& s) {
  std::vector<uint64_t> out;
  std::stringstream ss(s);
  for (std::string item; std::getline(ss, item, ',');) {
    if (!item.empty()) {
      out.push_back(std::strtoull(item.c_str(), nullptr, 0));
    }
  }
  return out;
}

uint16_t toHalf(int v) {  // exact for |v| <= 2048
  if (v == 0) {
    return 0;
  }
  const uint16_t sign = v < 0 ? 0x8000 : 0;
  unsigned m = unsigned(std::abs(v));
  int e = 0;
  while ((m >> e) > 1) {
    ++e;
  }
  const unsigned frac = (m << (10 - e)) & 0x3FF;  // e <= 10
  return uint16_t(sign | ((e + 15) << 10) | frac);
}

struct Options {
  bool sysemu = false;
  std::string simArgs;
  std::string test;
  std::string type = "fp32";
  std::string pattern = "elem";
  std::string values = "small";  // fp32 operand values for --test fma; see fillValues()
  std::string dumpTiles;         // --test fma: write the A and B tiles (2 x 1024 bytes) here
  std::string stopFile;          // --seconds loops end early once this file exists (a runner's temperature cap)
  std::string sweep = "0";
  double bSparsity = 0;
  bool bStream = false;
  int64_t rowMask = -1;
  std::string where = "dram";
  std::string masks = "0xFFFF,0x7FFF,0xFF,0xF,0x3,0x1,0x0";
  std::string gemv = "skip";
  bool gemvTree = false;
  std::string variant = "refill";
  double alpha = 0;  // 0: every item has the same k
  double meanK = 64;
  uint64_t kmax = 1u << 20;
  uint64_t items = 1024;
  uint64_t harts = 1;
  uint64_t iters = 0;
  uint64_t shireMask = 1;
  uint64_t perShire = 1;
  double seconds = 0;
  uint64_t seed = 1;
  double budget = -1;
  std::string kernel = KERNEL_ELF;
};

class Session {
public:
  Session(const Options& o, const std::vector<std::byte>& elf) : o_(o), tOpen_(Clock::now()) {
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
      std::istringstream extra(o.simArgs);
      for (std::string arg; extra >> arg;) {
        s.additionalOptions.push_back(arg);
      }
      dl_ = dev::IDeviceLayer::createSysEmuDeviceLayer(s, 1);
    } else {
      // Ops node only: the power logger needs /dev/et0_mgmt, which allows one opener.
      dl_ = dev::IDeviceLayer::createPcieDeviceLayer(true, false);
    }
    rt_ = rt::IRuntime::create(dl_);
    const auto devices = rt_->getDevices();
    if (devices.empty()) {
      throw std::runtime_error("no ET devices found");
    }
    dev_ = devices[0];
    stream_ = rt_->createStream(dev_);
    const auto load = rt_->loadCode(stream_, elf.data(), elf.size());
    rt_->waitForEvent(load.event_);
    kernel_ = load.kernel_;
    std::fprintf(stderr, "device ready in %.2f s\n", secondsSince(tOpen_));
  }

  ~Session() {
    for (auto& [name, buf] : buffers_) {
      rt_->freeDevice(dev_, buf.second);
    }
    rt_->unloadCode(kernel_);
    rt_->destroyStream(stream_);
    std::fprintf(stderr, "device held for %.2f s\n", secondsSince(tOpen_));
  }

  bool overBudget() const {
    return secondsSince(tOpen_) > o_.budget;
  }

  // Device buffers are kept by name and grown as needed, so repeated launches reuse them.
  uint64_t put(const std::string& name, const void* src, size_t bytes) {
    auto& [have, ptr] = buffers_[name];
    if (have < bytes) {
      if (ptr) {
        rt_->freeDevice(dev_, ptr);
      }
      ptr = rt_->mallocDevice(dev_, bytes);
      have = bytes;
    }
    if (src) {
      rt_->memcpyHostToDevice(stream_, reinterpret_cast<const std::byte*>(src), ptr, bytes);
      rt_->waitForStream(stream_);
    }
    return reinterpret_cast<uint64_t>(ptr);
  }

  void get(const std::string& name, void* dst, size_t bytes) {
    rt_->memcpyDeviceToHost(stream_, buffers_.at(name).second, reinterpret_cast<std::byte*>(dst), bytes);
    rt_->waitForStream(stream_);
  }

  struct Launch {
    bool ok = false;
    double wallS = 0;
    long long t0Ms = 0, t1Ms = 0;
    std::vector<SpResult> res;
    double ghz = 0;  // longest kernel's cycles over the launch's wall time (meaningful for launches of 0.1 s+)
  };

  Launch launch(SpArgs a) {
    Launch L;
    std::vector<SpResult> zeros(2048);
    a.results = put("results", zeros.data(), zeros.size() * sizeof(SpResult));
    rt::KernelLaunchOptions opts;
    opts.setShireMask(a.shire_mask);
    opts.setBarrier(true);
    const int timeoutS = o_.sysemu ? 3600 : 6;
    L.t0Ms = epochMs();
    const auto t0 = Clock::now();
    rt_->kernelLaunch(stream_, kernel_, reinterpret_cast<const std::byte*>(&a), sizeof(a), opts);
    L.ok = rt_->waitForStream(stream_, std::chrono::seconds(timeoutS));
    L.wallS = secondsSince(t0);
    L.t1Ms = epochMs();
    if (!L.ok) {
      std::fprintf(stderr, "kernel did not finish within %d s, aborting the stream\n", timeoutS);
      rt_->waitForEvent(rt_->abortStream(stream_));
    }
    for (const auto& e : rt_->retrieveStreamErrors(stream_)) {
      std::fprintf(stderr, "stream error: %s\n", e.getString().c_str());
      L.ok = false;
    }
    L.res.resize(2048);
    get("results", L.res.data(), L.res.size() * sizeof(SpResult));
    uint64_t longest = 0;
    for (const auto& r : L.res) {
      if (r.magic == SP_MAGIC) {
        longest = std::max<uint64_t>(longest, r.t_exit - r.t_entry);
      }
    }
    L.ghz = L.wallS > 0 ? double(longest) / L.wallS / 1e9 : 0;
    return L;
  }

private:
  const Options& o_;
  Clock::time_point tOpen_;
  std::shared_ptr<dev::IDeviceLayer> dl_;
  rt::RuntimePtr rt_;
  rt::DeviceId dev_{};
  rt::StreamId stream_{};
  rt::KernelId kernel_{};
  std::map<std::string, std::pair<size_t, std::byte*>> buffers_;
};

// Hart IDs that run: hart 0 (and 1 when `harts` is 2) of minions 0..perShire-1 of every shire in the mask.
std::vector<uint64_t> participants(uint64_t shireMask, uint64_t perShire, uint64_t harts) {
  std::vector<uint64_t> out;
  for (uint64_t s = 0; s < 32; ++s) {
    if ((shireMask >> s) & 1) {
      for (uint64_t m = 0; m < perShire; ++m) {
        for (uint64_t t = 0; t < harts; ++t) {
          out.push_back(s * 64 + m * 2 + t);
        }
      }
    }
  }
  return out;
}

struct Summary {
  uint64_t reported = 0, bad = 0, cmax = 0;
  double cmean = 0;
  uint64_t tensorErrors = 0;
};

Summary summarize(const Session::Launch& L, const std::vector<uint64_t>& harts) {
  Summary s;
  double sum = 0;
  for (uint64_t h : harts) {
    const auto& r = L.res[h];
    if (r.magic != SP_MAGIC || r.hart != h) {
      ++s.bad;
      continue;
    }
    ++s.reported;
    s.cmax = std::max<uint64_t>(s.cmax, r.cycles);
    sum += double(r.cycles);
    s.tensorErrors += r.tensor_error != 0;
  }
  s.cmean = s.reported ? sum / double(s.reported) : 0;
  return s;
}

/* ------------------------------------------------------------------------------------------ fma */

struct Tiles {
  std::vector<uint8_t> a = std::vector<uint8_t>(SP_TILE_BYTES), b = std::vector<uint8_t>(SP_TILE_BYTES);
  int A[16][64] = {};  // A[i][k], k < K
  int B[64][16] = {};  // B[k][j]
  int K = 16, E = 1;
  uint64_t nnzA = 0;
  uint64_t zeroPairsOneSided = 0;  // fp16: (a1, a2) pairs with exactly one zero
};

// Random small nonzero integer in [-3, 3] \ {0}.
int smallNonzero(std::mt19937_64& rng) {
  static const int v[] = {-3, -2, -1, 1, 2, 3};
  return v[rng() % 6];
}

Tiles makeTiles(uint64_t type, const std::string& pattern, double s, double bs, std::mt19937_64& rng) {
  Tiles t;
  t.E = type == SP_FP32 ? 1 : type == SP_FP16 ? 2 : 4;
  t.K = 16 * t.E;
  std::uniform_real_distribution<double> u(0, 1);
  // Which A elements are zero.
  std::vector<bool> zeroCol(t.K), zeroRow(16);
  for (int k = 0; k < t.K; ++k) {
    zeroCol[k] = u(rng) < s;
  }
  for (int i = 0; i < 16; ++i) {
    zeroRow[i] = u(rng) < s;
  }
  for (int i = 0; i < 16; ++i) {
    for (int k = 0; k < t.K; ++k) {
      bool z = false;
      if (pattern == "elem") {
        z = u(rng) < s;
      } else if (pattern == "col") {
        z = zeroCol[k];
      } else if (pattern == "row") {
        z = zeroRow[i];
      } else if (pattern == "pair") {  // fp16: zero exactly one element of a fraction s of the (2k, 2k+1) pairs
        z = (k % 2 == 1) && u(rng) < s;
      }
      t.A[i][k] = z ? 0 : smallNonzero(rng);
      t.nnzA += t.A[i][k] != 0;
    }
    if (t.E == 2) {
      for (int k = 0; k < t.K; k += 2) {
        t.zeroPairsOneSided += (t.A[i][k] == 0) != (t.A[i][k + 1] == 0);
      }
    }
  }
  for (int k = 0; k < t.K; ++k) {
    for (int j = 0; j < 16; ++j) {
      t.B[k][j] = u(rng) < bs ? 0 : smallNonzero(rng);
    }
  }
  // Pack A: row i = line i; B: line p, column j, element e -> bytes (j*E + e) * size.
  const int size = type == SP_FP32 ? 4 : type == SP_FP16 ? 2 : 1;
  auto store = [&](std::vector<uint8_t>& buf, size_t off, int v) {
    if (type == SP_FP32) {
      const float f = float(v);
      std::memcpy(&buf[off], &f, 4);
    } else if (type == SP_FP16) {
      const uint16_t h = toHalf(v);
      std::memcpy(&buf[off], &h, 2);
    } else {
      buf[off] = uint8_t(int8_t(v));
    }
  };
  for (int i = 0; i < 16; ++i) {
    for (int k = 0; k < t.K; ++k) {
      store(t.a, size_t(i * 64 + k * size), t.A[i][k]);
    }
  }
  for (int p = 0; p < 16; ++p) {
    for (int j = 0; j < 16; ++j) {
      for (int e = 0; e < t.E; ++e) {
        store(t.b, size_t(p * 64 + (j * t.E + e) * size), t.B[p * t.E + e][j]);
      }
    }
  }
  return t;
}

// Overwrites the fp32 A and B tiles with a value pattern, for the data-dependent power experiment
// (docs/reports: horace-experiment). Results are not checked for these: only time and power matter.
//   zeros ones twos pi        every element the same constant
//   checker                   1, 0, 1, 0, ...
//   ternary                   -1, 0, 1 at random
//   onebit                    the smallest normal float (bit pattern 0x00800000: a single set bit)
//   uniform randn             random in [0, 1) / standard normal: every mantissa bit is busy
//   sparse75 sparse50         randn with 75% / 50% of the elements zeroed
//   signs pow2 mant           one field of the word random: +-1 / 2^-8..2^8 / [1, 2)
//   a_randn_b_ones, a_ones_b_randn   one operand random, the other constant
//   file:<path>               custom tiles: raw A then raw B, 1,024 bytes each (tools/ettelem/make_tiles.py)
// --dump-tiles <file> writes the A and B tiles, so that rtl-sim/fma_toggle can replay the exact operands.
// IEEE half from a float that is zero or within half's normal range (|f| in [6.2e-5, 65504]); smaller values flush to zero.
uint16_t halfFromFloat(float f) {
  uint32_t b;
  std::memcpy(&b, &f, 4);
  const uint32_t sign = (b >> 16) & 0x8000u;
  const int32_t exp = int32_t((b >> 23) & 0xFF) - 127 + 15;
  const uint32_t man = (b >> 13) & 0x3FFu;
  if (exp <= 0) return uint16_t(sign);
  if (exp >= 31) return uint16_t(sign | 0x7BFFu);
  return uint16_t(sign | (uint32_t(exp) << 10) | man);
}

void fillValues(Tiles& t, uint64_t type, const std::string& mode, std::mt19937_64& rng) {
  std::normal_distribution<float> n(0.f, 1.f);
  std::uniform_real_distribution<float> u(0.f, 1.f);
  if (mode.rfind("file:", 0) == 0) {
    // Custom operands: the raw A tile then the raw B tile, 1,024 bytes each, in the layout of the chosen type
    // (fp32: 16 lines of 16 floats; tools/ettelem/make_tiles.py writes them).
    std::ifstream f(mode.substr(5), std::ios::binary);
    f.read(reinterpret_cast<char*>(t.a.data()), std::streamsize(t.a.size()));
    f.read(reinterpret_cast<char*>(t.b.data()), std::streamsize(t.b.size()));
    if (!f) throw std::runtime_error("cannot read 2 x 1024 bytes of tiles from " + mode.substr(5));
    return;
  }
  if (type != SP_FP32) {
    // fp16 and int8 tiles (the precision comparison): every element slot of A and B gets the pattern.
    // int8 "randn" is uniform over -128..127; "uniform" over 0..127.
    const size_t size = type == SP_FP16 ? 2 : 1;
    for (auto* buf : {&t.a, &t.b}) {
      for (size_t off = 0; off + size <= buf->size(); off += size) {
        float f;
        int q;
        if (mode == "zeros") { f = 0.f; q = 0; }
        else if (mode == "ones") { f = 1.f; q = 1; }
        else if (mode == "uniform") { f = u(rng); q = int(rng() % 128); }
        else if (mode == "randn") { f = n(rng); q = int(rng() % 256) - 128; }
        else throw std::runtime_error("--values " + mode + " is fp32 only; fp16 and int8 take zeros, ones, uniform, randn");
        if (type == SP_FP16) {
          const uint16_t h = halfFromFloat(f);
          std::memcpy(&(*buf)[off], &h, 2);
        } else {
          (*buf)[off] = uint8_t(int8_t(q));
        }
      }
    }
    return;
  }
  size_t idx = 0;
  auto value = [&](bool isB) -> float {
    ++idx;
    if (mode == "zeros") return 0.f;
    if (mode == "ones") return 1.f;
    if (mode == "twos") return 2.f;
    if (mode == "pi") return 3.14159274f;
    if (mode == "checker") return float(idx & 1);
    if (mode == "ternary") return float(int(rng() % 3) - 1);
    if (mode == "onebit") { const uint32_t b = 0x00800000u; float f; std::memcpy(&f, &b, 4); return f; }
    if (mode == "uniform") return u(rng);
    if (mode == "randn") return n(rng);
    if (mode == "sparse75") return (rng() % 4) ? 0.f : n(rng);
    if (mode == "sparse50") return (rng() % 2) ? 0.f : n(rng);
    // One field of the fp32 word random, the others fixed: sign only, exponent only, mantissa only.
    if (mode == "signs") return (rng() % 2) ? 1.f : -1.f;
    if (mode == "pow2") return std::ldexp(1.f, int(rng() % 17) - 8);
    if (mode == "mant") return 1.f + u(rng);
    // One operand random, the other constant.
    if (mode == "a_randn_b_ones") return isB ? 1.f : n(rng);
    if (mode == "a_ones_b_randn") return isB ? n(rng) : 1.f;
    throw std::runtime_error("unknown --values " + mode);
  };
  for (auto* buf : {&t.a, &t.b}) {
    for (size_t off = 0; off + 4 <= buf->size(); off += 4) {
      const float f = value(buf == &t.b);
      std::memcpy(&(*buf)[off], &f, 4);
    }
  }
}

// C[i][j] after `iters` ops; `literal` applies the fp16 pseudo-code as written in PRM 9.4 (the 2-term update
// happens only when all four of a1, a2, b1, b2 are nonzero), except on the first op (MUL), which always multiplies.
int64_t expectC(const Tiles& t, uint64_t type, uint64_t iters, int i, int j, bool literal, uint32_t rowMask) {
  if (!((rowMask >> i) & 1)) {
    return 0;  // masked rows: MUL zeroes them on the first op, and no later op touches them
  }
  int64_t first = 0, rest = 0;
  for (int k = 0; k < t.K; k += (type == SP_FP16 ? 2 : 1)) {
    if (type == SP_FP16) {
      const int64_t p = int64_t(t.A[i][k]) * t.B[k][j] + int64_t(t.A[i][k + 1]) * t.B[k + 1][j];
      const bool all = t.A[i][k] && t.A[i][k + 1] && t.B[k][j] && t.B[k + 1][j];
      const int64_t kept = (!literal || all) ? p : 0;
      first += k == 0 ? p : kept;  // the first op's k = 0 step multiplies (MUL); later steps accumulate
      rest += kept;
    } else {
      const int64_t p = int64_t(t.A[i][k]) * t.B[k][j];
      first += p;
      rest += p;
    }
  }
  return first + int64_t(iters - 1) * rest;
}

// Checks the C tiles of every participant; returns "math", "prm-literal", "both" (they agree) or "wrong".
// fp32 and fp16 sums are exact only while they stay below 2^24; longer runs return "unchecked" (the short sweeps
// check them). int8 accumulates in int32, whose wraparound is exact, so it is compared modulo 2^32.
std::string checkC(Session& dev, const Tiles& t, uint64_t type, uint64_t iters, const std::vector<uint64_t>& harts,
                   uint32_t rowMask) {
  if (type != SP_INT8) {
    int64_t biggest = 0;
    for (int i = 0; i < 16; ++i) {
      for (int j = 0; j < 16; ++j) {
        biggest = std::max<int64_t>(biggest, std::llabs(expectC(t, type, iters, i, j, false, rowMask)));
        biggest = std::max<int64_t>(biggest, std::llabs(expectC(t, type, iters, i, j, true, rowMask)));
      }
    }
    // Partial sums can exceed the final value by at most one op's worth of |products|.
    if (biggest + 16 * 64 * 9 >= (int64_t(1) << 24)) {
      return "unchecked";
    }
  }
  std::vector<uint32_t> c(SP_MINIONS * 256);
  dev.get("out", c.data(), c.size() * 4);
  bool math = true, literal = true;
  for (uint64_t h : harts) {
    const uint64_t m = h >> 1;
    for (int i = 0; i < 16; ++i) {
      for (int j = 0; j < 16; ++j) {
        const uint32_t w = c[m * 256 + i * 16 + j];
        if (type == SP_INT8) {
          math &= w == uint32_t(uint64_t(expectC(t, type, iters, i, j, false, rowMask)));
          literal &= w == uint32_t(uint64_t(expectC(t, type, iters, i, j, true, rowMask)));
        } else {
          float f;
          std::memcpy(&f, &w, 4);
          const int64_t got = std::llround(double(f));
          math &= got == expectC(t, type, iters, i, j, false, rowMask);
          literal &= got == expectC(t, type, iters, i, j, true, rowMask);
        }
      }
    }
  }
  return math && literal ? "both" : math ? "math" : literal ? "prm-literal" : "wrong";
}

uint64_t typeOf(const std::string& s) {
  if (s == "fp32") return SP_FP32;
  if (s == "fp16") return SP_FP16;
  if (s == "int8") return SP_INT8;
  throw std::runtime_error("--type must be fp32, fp16 or int8");
}

// Repeats `one(iters)` for about --seconds after a calibration launch (only on silicon).
template <typename F>
void repeatFor(const Options& o, Session& dev, uint64_t iters, F one) {
  const double wall = one(iters, -1);
  if (o.sysemu || o.seconds <= 0) {
    return;
  }
  iters = std::max<uint64_t>(1, uint64_t(double(iters) * 0.5 / std::max(wall, 1e-4)));
  double spent = 0;
  for (int n = 0; spent < o.seconds; ++n) {
    if (dev.overBudget()) {
      std::fprintf(stderr, "stopping: device-time budget of %.1f s used\n", o.budget);
      break;
    }
    if (!o.stopFile.empty() && fs::exists(o.stopFile)) {
      std::fprintf(stderr, "stopping: %s exists\n", o.stopFile.c_str());
      break;
    }
    spent += one(iters, n);
  }
}

int testFma(const Options& o, Session& dev) {
  const uint64_t type = typeOf(o.type);
  const auto harts = participants(o.shireMask, o.perShire, 1);
  std::mt19937_64 rng(o.seed);
  int bad = 0;
  for (double s : parseDoubles(o.sweep)) {
    Tiles t = makeTiles(type, o.pattern, s, o.bSparsity, rng);
    const bool rawValues = o.values != "small";
    if (rawValues) {
      fillValues(t, type, o.values, rng);
    }
    if (!o.dumpTiles.empty()) {
      std::ofstream f(o.dumpTiles, std::ios::binary);
      f.write(reinterpret_cast<const char*>(t.a.data()), std::streamsize(t.a.size()));
      f.write(reinterpret_cast<const char*>(t.b.data()), std::streamsize(t.b.size()));
    }
    SpArgs a{};
    a.mode = SP_FMA;
    a.shire_mask = o.shireMask;
    a.per_shire = o.perShire;
    a.type = type;
    a.a_tile = dev.put("a", t.a.data(), t.a.size());
    a.b_tile = dev.put("b", t.b.data(), t.b.size());
    a.out = dev.put("out", nullptr, SP_MINIONS * SP_TILE_BYTES);
    a.b_stream = o.bStream;
    a.use_mask = o.rowMask >= 0;
    a.mask = o.rowMask >= 0 ? uint64_t(o.rowMask) & 0xFFFF : 0xFFFF;
    auto one = [&](uint64_t iters, int launchNo) -> double {
      a.iters = iters;
      const auto L = dev.launch(a);
      const Summary sm = summarize(L, harts);
      const std::string check =
        !L.ok ? "no-result" : rawValues ? "unchecked" : checkC(dev, t, type, iters, harts, uint32_t(a.mask));
      const bool ok = L.ok && sm.bad == 0 && sm.tensorErrors == 0 && check != "wrong";
      bad += !ok;
      std::printf("SPARSITY {\"test\":\"fma\",\"type\":\"%s\",\"pattern\":\"%s\",\"values\":\"%s\",\"sparsity\":%.4f,\"b_sparsity\":%.4f,"
                  "\"b_stream\":%d,\"row_mask\":\"0x%04llx\",\"nnz_a\":%llu,\"a_elems\":%d,\"fp16_one_sided_pairs\":%llu,"
                  "\"minions\":%zu,\"shire_mask\":\"0x%llx\",\"iters\":%llu,\"launch\":%d,\"cycles_max\":%llu,"
                  "\"cycles_mean\":%.1f,\"cycles_per_op\":%.3f,\"wall_s\":%.6f,\"t_start_ms\":%lld,\"t_end_ms\":%lld,"
                  "\"ghz\":%.4f,\"tensor_errors\":%llu,\"result\":\"%s\",\"ok\":%s}\n",
                  o.type.c_str(), o.pattern.c_str(), o.values.c_str(), s, o.bSparsity, int(o.bStream),
                  (unsigned long long)a.mask,
                  (unsigned long long)t.nnzA, 16 * t.K, (unsigned long long)t.zeroPairsOneSided, harts.size(),
                  (unsigned long long)o.shireMask, (unsigned long long)iters, launchNo, (unsigned long long)sm.cmax,
                  sm.cmean, sm.cmean / double(iters), L.wallS, L.t0Ms, L.t1Ms, L.ghz,
                  (unsigned long long)sm.tensorErrors, check.c_str(), ok ? "true" : "false");
      std::fflush(stdout);
      return L.wallS;
    };
    repeatFor(o, dev, o.iters ? o.iters : (o.sysemu ? 4 : 20000), one);
    if (dev.overBudget()) {
      break;
    }
  }
  return bad ? 1 : 0;
}

/* ------------------------------------------------------------------------------- E101: a matmul that streams */

// --test fma --values <arm>:<gen>:<files> (E101, tools/claims-v3/kinds/E101.md). The grammar sits in --values so the lab's runners, which build
// every other argument, run unchanged.
//   arm    tenb        E39's mode: A resident in the L1, B streamed through TenB; one tile, the file's (gen must be tiles)
//          mm<N>       kernels/mmbench's loop: A and B both streamed from a shared pool of N tile pairs
//          mmp<N>      the same with a private pool of N pairs per minion, which makes every load come from DRAM
//          gemm<B>     a real GEMM of B blocks, each 64 x 32 tiles x 32 tiles (1024 x 512 x 512 elements in fp32), cooperative loads, C stored
//          gemmnc<B>   the same with every minion loading for itself
//          gemmc<B>    E105: gemm with B packed by column, gemmv<B> with the vendor's strides (A and C at a pitch of 2,048 B, B at 2,112 B), gemmh<B> by column with 16 k tiles; the tile contents are gemm's
//   gen    tiles       the pool cycles through the files' tile pairs (E105 adds sparse25: as sparse50 with a quarter of the elements zero)
//          randn | sparse50 | e37    pair 0 is the first file's; the rest are drawn: normal (fp32, fp16) or uniform -128..127 (int8); that with half
//                      the elements zero; +-1, +-2 as launchers/mmbench fills its tiles
//   files  comma-separated tile files: raw A then raw B, 1,024 bytes each
// A run's iters in its SPARSITY records is the ops per minion, so every reducer's work and rate stand. On silicon the last launch, launch -3, is a short one for
// the check: fp32 sums over a whole 0.5 s launch round by more than any honest tolerance, so C is compared after a few passes only, after the power window. The last
// record, test "check", gives the host's comparison of that C with its own reference: exact, approx (inside 1e-4 of the sum of the absolute products) or wrong.

struct ArmSpec {
  std::string arm, gen;
  std::vector<std::string> files;
  uint64_t n = 0;       // mm: tile pairs per pool; gemm: blocks
  bool tenb = false, mm = false, priv = false, gemm = false, coop = false;
  uint64_t layout = SP_LAYOUT_PACKED;
};

bool isArmValues(const std::string& v) {
  for (const char* p : {"tenb:", "mm", "gemm"}) {
    if (v.rfind(p, 0) == 0) return true;
  }
  return false;
}

ArmSpec parseArm(const std::string& v) {
  ArmSpec s;
  const auto c1 = v.find(':');
  const auto c2 = c1 == std::string::npos ? c1 : v.find(':', c1 + 1);
  if (c2 == std::string::npos) throw std::runtime_error("--values: want <arm>:<gen>:<files>, got " + v);
  s.arm = v.substr(0, c1);
  s.gen = v.substr(c1 + 1, c2 - c1 - 1);
  std::istringstream fs_(v.substr(c2 + 1));
  for (std::string f; std::getline(fs_, f, ',');) s.files.push_back(f);
  if (s.files.empty()) throw std::runtime_error("--values: no tile file in " + v);
  auto num = [&](const char* prefix) { return std::strtoull(s.arm.c_str() + std::strlen(prefix), nullptr, 10); };
  if (s.arm == "tenb") { s.tenb = true; s.n = 1; }
  else if (s.arm.rfind("mmp", 0) == 0) { s.mm = s.priv = true; s.n = num("mmp"); }
  else if (s.arm.rfind("mm", 0) == 0) { s.mm = true; s.n = num("mm"); }
  else if (s.arm.rfind("gemmnc", 0) == 0) { s.gemm = true; s.n = num("gemmnc"); }
  else if (s.arm.rfind("gemmc", 0) == 0) { s.gemm = s.coop = true; s.layout = SP_LAYOUT_BYCOL; s.n = num("gemmc"); }
  else if (s.arm.rfind("gemmv", 0) == 0) { s.gemm = s.coop = true; s.layout = SP_LAYOUT_VENDOR; s.n = num("gemmv"); }
  else if (s.arm.rfind("gemmh", 0) == 0) { s.gemm = s.coop = true; s.layout = SP_LAYOUT_HALFK; s.n = num("gemmh"); }
  else if (s.arm.rfind("gemm", 0) == 0) { s.gemm = s.coop = true; s.n = num("gemm"); }
  else throw std::runtime_error("--values: unknown arm " + s.arm);
  if (s.n == 0) throw std::runtime_error("--values: arm needs a size: " + s.arm);
  return s;
}

// IEEE half from a float, rounded to nearest (kinds.json's fp16 tiles are numpy's rounding); below half's normal range it flushes to zero.
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

double halfValue(uint16_t h) {
  const int e = (h >> 10) & 0x1F, m = h & 0x3FF;
  const double v = e == 0 ? std::ldexp(double(m), -24) : std::ldexp(double(0x400 + m), e - 25);
  return (h & 0x8000) ? -v : v;
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

// The pools. Pair 0 is the first file's, so --dump-tiles can be checked against its sha256. At most 8,192 distinct tiles per pool are drawn and the
// pool repeats them: 8 MB of period, far past the four distinct lines beyond which E81 saw the period stop mattering, and generation stays under 0.2 s.
void fillPools(std::vector<uint8_t>& A, std::vector<uint8_t>& B, const ArmSpec& s, uint64_t type, std::mt19937_64& rng, std::vector<uint8_t>& firstA,
               std::vector<uint8_t>& firstB) {
  std::vector<std::vector<uint8_t>> fa, fb;
  for (const auto& p : s.files) {
    std::ifstream f(p, std::ios::binary);
    std::vector<uint8_t> a(SP_TILE_BYTES), b(SP_TILE_BYTES);
    f.read(reinterpret_cast<char*>(a.data()), SP_TILE_BYTES);
    f.read(reinterpret_cast<char*>(b.data()), SP_TILE_BYTES);
    if (!f) throw std::runtime_error("cannot read 2 x 1024 bytes of tiles from " + p);
    fa.push_back(a);
    fb.push_back(b);
  }
  firstA = fa[0];
  firstB = fb[0];
  const bool fromFiles = s.gen == "tiles";
  const size_t kDistinct = 8192;
  auto fill = [&](std::vector<uint8_t>& P, const std::vector<std::vector<uint8_t>>& files) {
    const size_t tiles = P.size() / SP_TILE_BYTES, distinct = std::min(tiles, kDistinct);
    for (size_t t = 0; t < distinct; ++t) {
      uint8_t* d = P.data() + t * SP_TILE_BYTES;
      if (fromFiles) std::memcpy(d, files[t % files.size()].data(), SP_TILE_BYTES);
      else if (t == 0) std::memcpy(d, files[0].data(), SP_TILE_BYTES);
      else drawTile(d, type, s.gen, rng);
    }
    for (size_t t = distinct; t < tiles; ++t) {
      std::memcpy(P.data() + t * SP_TILE_BYTES, P.data() + (t % distinct) * SP_TILE_BYTES, SP_TILE_BYTES);
    }
  };
  fill(A, fa);
  fill(B, fb);
}

// A tile's elements as doubles: A[i][k], B[k][j], in the layout of kernels/mmbench.
struct Elems {
  int K, E;
  uint64_t type;
  double a(const uint8_t* t, int i, int k) const {
    const uint8_t* p = t + i * 64;
    if (type == SP_FP32) { float f; std::memcpy(&f, p + k * 4, 4); return f; }
    if (type == SP_FP16) { uint16_t h; std::memcpy(&h, p + k * 2, 2); return halfValue(h); }
    return double(int8_t(p[k]));
  }
  double b(const uint8_t* t, int k, int j) const {
    const int line = k / E, e = k % E;
    const uint8_t* p = t + line * 64;
    if (type == SP_FP32) { float f; std::memcpy(&f, p + j * 4, 4); return f; }
    if (type == SP_FP16) { uint16_t h; std::memcpy(&h, p + (j * 2 + e) * 2, 2); return halfValue(h); }
    return double(int8_t(p[j * 4 + e]));
  }
};

struct Ref {
  double want[256] = {}, abs[256] = {};
  void add(const Elems& el, const uint8_t* ta, const uint8_t* tb, double times) {
    double av[16][64], bv[64][16];
    for (int i = 0; i < 16; ++i) for (int k = 0; k < el.K; ++k) av[i][k] = el.a(ta, i, k);
    for (int k = 0; k < el.K; ++k) for (int j = 0; j < 16; ++j) bv[k][j] = el.b(tb, k, j);
    for (int i = 0; i < 16; ++i) {
      for (int k = 0; k < el.K; ++k) {
        for (int j = 0; j < 16; ++j) {
          const double p = av[i][k] * bv[k][j];
          want[i * 16 + j] += times * p;
          abs[i * 16 + j] += times * std::fabs(p);
        }
      }
    }
  }
};

struct CheckCount { uint64_t words = 0, exact = 0, within = 0; };

void compareC(const uint32_t* c, const Ref& r, uint64_t type, CheckCount& n) {
  for (int e = 0; e < 256; ++e) {
    ++n.words;
    if (type == SP_INT8) {
      const uint32_t want = uint32_t(uint64_t(int64_t(std::llround(std::fmod(r.want[e], 4294967296.0)))));
      if (c[e] == want) { ++n.exact; ++n.within; }
    } else {
      float f;
      std::memcpy(&f, &c[e], 4);
      if (double(f) == r.want[e]) { ++n.exact; ++n.within; }
      else if (std::fabs(double(f) - r.want[e]) <= 1e-4 * r.abs[e]) ++n.within;
    }
  }
}

// E105: the bytes the device reads, from the packed pools the reference is computed on. Same tile contents, same draw, other addresses.
std::vector<uint8_t> layoutA(const std::vector<uint8_t>& A, const ArmSpec& s) {
  if (s.layout != SP_LAYOUT_VENDOR) return A;
  std::vector<uint8_t> out(A.size());
  for (uint64_t b = 0; b < s.n; ++b) {
    for (uint64_t r = 0; r < SP_GEMM_MT; ++r) {
      for (uint64_t k = 0; k < SP_GEMM_KT; ++k) {
        for (uint64_t i = 0; i < 16; ++i) {
          std::memcpy(out.data() + b * SP_GEMM_A_BLOCK + (r * 16 + i) * SP_GEMM_A_PITCH + k * 64, A.data() + b * SP_GEMM_A_BLOCK + (r * SP_GEMM_KT + k) * SP_TILE_BYTES + i * 64, 64);
        }
      }
    }
  }
  return out;
}

std::vector<uint8_t> layoutB(const std::vector<uint8_t>& B, const ArmSpec& s) {
  if (s.layout == SP_LAYOUT_PACKED) return B;
  const bool vendor = s.layout == SP_LAYOUT_VENDOR;
  std::vector<uint8_t> out(vendor ? s.n * size_t(SP_GEMM_VB_BLOCK) : B.size());
  for (uint64_t b = 0; b < s.n; ++b) {
    for (uint64_t k = 0; k < SP_GEMM_KT; ++k) {
      for (uint64_t c = 0; c < SP_GEMM_NT; ++c) {
        const uint8_t* from = B.data() + b * SP_GEMM_B_BLOCK + (k * SP_GEMM_NT + c) * SP_TILE_BYTES;
        if (vendor) {
          for (uint64_t i = 0; i < 16; ++i) std::memcpy(out.data() + b * SP_GEMM_VB_BLOCK + (k * 16 + i) * SP_GEMM_B_PITCH + c * 64, from + i * 64, 64);
        } else {
          std::memcpy(out.data() + b * SP_GEMM_B_BLOCK + (c * SP_GEMM_KT + k) * SP_TILE_BYTES, from, SP_TILE_BYTES);
        }
      }
    }
  }
  return out;
}

int testArm(const Options& o, Session& dev) {
  const uint64_t type = typeOf(o.type);
  const ArmSpec s = parseArm(o.values);
  const auto harts = participants(o.shireMask, o.perShire, 1);
  if (s.gemm && o.perShire != 32) throw std::runtime_error("gemm needs --per-shire 32: every minion of a coop group must take part");
  if (s.tenb && s.gen != "tiles") throw std::runtime_error("tenb runs one tile: gen must be tiles");
  const int E = type == SP_FP32 ? 1 : type == SP_FP16 ? 2 : 4;
  const Elems el{16 * E, E, type};
  std::mt19937_64 rng(o.seed);
  size_t aTiles = 1, bTiles = 1;
  if (s.mm) aTiles = bTiles = (s.priv ? size_t(SP_MINIONS) : size_t(1)) * s.n;
  if (s.gemm) {
    aTiles = s.n * SP_GEMM_MT * SP_GEMM_KT;
    bTiles = s.n * SP_GEMM_KT * SP_GEMM_NT;
  }
  std::vector<uint8_t> A(aTiles * SP_TILE_BYTES), B(bTiles * SP_TILE_BYTES), first_a, first_b;
  fillPools(A, B, s, type, rng, first_a, first_b);
  if (!o.dumpTiles.empty()) {
    std::ofstream f(o.dumpTiles, std::ios::binary);
    f.write(reinterpret_cast<const char*>(first_a.data()), SP_TILE_BYTES);
    f.write(reinterpret_cast<const char*>(first_b.data()), SP_TILE_BYTES);
  }
  SpArgs a{};
  a.shire_mask = o.shireMask;
  a.per_shire = o.perShire;
  a.type = type;
  const size_t cBytes = s.gemm ? s.n * SP_GEMM_C_BLOCK : SP_MINIONS * SP_TILE_BYTES;
  const uint64_t cAddr = dev.put("out", nullptr, cBytes);
  uint64_t opsPerPass = 1;
  uint64_t firstIters = o.sysemu ? 2 : 64000;
  if (s.tenb) {
    a.mode = SP_FMA;
    a.a_tile = dev.put("a", A.data(), A.size());
    a.b_tile = dev.put("b", B.data(), B.size());
    a.out = cAddr;
    a.b_stream = 1;
    a.mask = 0xFFFF;
  } else if (s.mm) {
    a.mode = SP_STREAM;
    a.a_pool = dev.put("a", A.data(), A.size());
    a.b_pool = dev.put("b", B.data(), B.size());
    a.out = cAddr;
    a.ntiles = s.n;
    a.private_pools = s.priv;
    opsPerPass = s.n;
    firstIters = o.sysemu ? 2 : s.priv ? 20 : std::max<uint64_t>(1, 64000 / s.n);
  } else {
    a.mode = SP_GEMM;
    const std::vector<uint8_t> devA = layoutA(A, s), devB = layoutB(B, s);
    a.a_pool = dev.put("a", devA.data(), devA.size());
    a.b_pool = dev.put("b", devB.data(), devB.size());
    a.c_pool = cAddr;
    a.nblocks = s.n;
    a.coop = s.coop;
    a.layout = s.layout;
    opsPerPass = s.n * 2 * (s.layout == SP_LAYOUT_HALFK ? SP_GEMM_KT / 2 : SP_GEMM_KT);
    firstIters = o.sysemu ? 1 : std::max<uint64_t>(1, 64000 / opsPerPass);
  }
  a.out = a.out ? a.out : dev.put("unused", nullptr, 64);
  int bad = 0;
  uint64_t lastIters = 0;
  double lastCpo = 0;
  auto one = [&](uint64_t iters, int launchNo) -> double {
    a.iters = iters;
    const auto L = dev.launch(a);
    const Summary sm = summarize(L, harts);
    const uint64_t ops = iters * opsPerPass;
    const bool ok = L.ok && sm.bad == 0 && sm.tensorErrors == 0;
    bad += !ok;
    lastIters = iters;
    const double cpoNow = sm.cmean / double(ops);
    if (launchNo != -3) lastCpo = cpoNow;
    std::printf("SPARSITY {\"test\":\"fma\",\"arm\":\"%s\",\"gen\":\"%s\",\"type\":\"%s\",\"pattern\":\"none\",\"values\":\"%s\",\"b_stream\":%d,"
                "\"minions\":%zu,\"shire_mask\":\"0x%llx\",\"iters\":%llu,\"passes\":%llu,\"launch\":%d,\"cycles_max\":%llu,"
                "\"cycles_mean\":%.1f,\"cycles_per_op\":%.3f,\"wall_s\":%.6f,\"t_start_ms\":%lld,\"t_end_ms\":%lld,"
                "\"ghz\":%.4f,\"tensor_errors\":%llu,\"result\":\"unchecked\",\"ok\":%s}\n",
                s.arm.c_str(), s.gen.c_str(), o.type.c_str(), o.values.c_str(), int(s.tenb), harts.size(),
                (unsigned long long)o.shireMask, (unsigned long long)ops, (unsigned long long)iters, launchNo, (unsigned long long)sm.cmax,
                sm.cmean, cpoNow, L.wallS, L.t0Ms, L.t1Ms, L.ghz,
                (unsigned long long)sm.tensorErrors, ok ? "true" : "false");
    std::fflush(stdout);
    return L.wallS;
  };
  repeatFor(o, dev, o.iters ? o.iters : firstIters, one);
  if (!o.sysemu) {
    one(s.gemm ? 1 : s.mm ? 2 : 32, -3);    // the short launch the check reads
  }

  // The check: C of the last launch against the host's own reference, on a sample of the output tiles.
  CheckCount n;
  const long long tc0 = epochMs();
  std::vector<uint32_t> C(cBytes / 4);
  dev.get("out", C.data(), cBytes);
  if (s.gemm) {
    const uint64_t b = s.n - 1;
    const uint8_t* ab = A.data() + b * SP_GEMM_A_BLOCK;
    const uint8_t* bb = B.data() + b * SP_GEMM_B_BLOCK;
    const uint32_t* cb = C.data() + b * SP_GEMM_C_BLOCK / 4;
    size_t step = std::max<size_t>(1, harts.size() / 64);
    for (size_t h = 0; h < harts.size(); h += step) {
      const uint64_t minion = harts[h] >> 1, shire = minion >> 5, m = minion & 31;
      const uint64_t r = ((shire >> 2) & 7) * 8 + ((m >> 3) & 3) * 2 + ((h / step) & 1), c = (shire & 3) * 8 + (m & 7);
      Ref ref;
      for (uint64_t k = 0; k < (s.layout == SP_LAYOUT_HALFK ? SP_GEMM_KT / 2 : SP_GEMM_KT); ++k) {
        ref.add(el, ab + (r * SP_GEMM_KT + k) * SP_TILE_BYTES, bb + (k * SP_GEMM_NT + c) * SP_TILE_BYTES, 1.0);
      }
      uint32_t tile[256];
      if (s.layout == SP_LAYOUT_VENDOR) {
        for (uint64_t i = 0; i < 16; ++i) std::memcpy(tile + i * 16, reinterpret_cast<const uint8_t*>(cb) + (r * 16 + i) * SP_GEMM_C_PITCH + c * 64, 64);
      } else {
        std::memcpy(tile, cb + (r * SP_GEMM_NT + c) * 256, SP_TILE_BYTES);
      }
      compareC(tile, ref, type, n);
    }
  } else {
    size_t step = std::max<size_t>(1, harts.size() / 64);
    for (size_t h = 0; h < harts.size(); h += step) {
      const uint64_t minion = harts[h] >> 1;
      Ref ref;
      if (s.tenb) ref.add(el, A.data(), B.data(), double(lastIters));
      else {
        const size_t base = s.priv ? size_t(minion) * s.n : 0;
        for (uint64_t t = 0; t < s.n; ++t) {
          ref.add(el, A.data() + (base + t) * SP_TILE_BYTES, B.data() + (base + t) * SP_TILE_BYTES, double(lastIters));
        }
      }
      compareC(C.data() + minion * 256, ref, type, n);
    }
  }
  const char* verdict = n.within < n.words ? "wrong" : n.exact == n.words ? "exact" : "approx";
  const bool ok = n.within == n.words;
  bad += !ok;
  const long long tc1 = epochMs();
  std::printf("SPARSITY {\"test\":\"check\",\"arm\":\"%s\",\"gen\":\"%s\",\"type\":\"%s\",\"minions\":%zu,\"iters\":0,\"launch\":-2,\"cycles_per_op\":%.3f,\"wall_s\":0,"
              "\"t_start_ms\":%lld,\"t_end_ms\":%lld,\"ghz\":0,\"words\":%llu,\"exact\":%llu,\"within\":%llu,\"result\":\"%s\",\"ok\":%s}\n",
              s.arm.c_str(), s.gen.c_str(), o.type.c_str(), harts.size(), lastCpo, tc0, tc1, (unsigned long long)n.words,
              (unsigned long long)n.exact, (unsigned long long)n.within, verdict, ok ? "true" : "false");
  std::fflush(stdout);
  return bad ? 1 : 0;
}

/* ------------------------------------------------------------------------------------------ tload */

int testTload(const Options& o, Session& dev) {
  const auto harts = participants(o.shireMask, o.perShire, 1);
  SpArgs a{};
  a.mode = SP_TLOAD;
  a.shire_mask = o.shireMask;
  a.per_shire = o.perShire;
  a.use_mask = 1;
  if (o.where == "scp") {
    a.src_bytes = 64 * 1024;  // 32 minions x 64 KB = 2 MB of the 2.5 MB scratchpad
    a.src = SP_SCP_LOCAL(0);
  } else if (o.where == "l2") {
    a.src_bytes = 8 * 1024;  // stays in the 512 KB shire L2
    a.src = dev.put("src", nullptr, SP_MINIONS * a.src_bytes);
  } else {
    // Streaming from DRAM: the minions together must cover more than the 32 MB L3 (and each shire more than its
    // L2), so a lone minion gets 64 MB. The kernel indexes the buffer by minion ID.
    a.src_bytes = std::max<uint64_t>(256 * 1024, (64ull << 20) / harts.size());
    a.src = dev.put("src", nullptr, ((harts.back() >> 1) + 1) * a.src_bytes);
  }
  int bad = 0;
  for (uint64_t m : parseInts(o.masks)) {
    a.mask = m & 0xFFFF;
    auto one = [&](uint64_t iters, int launchNo) -> double {
      a.iters = iters;
      const auto L = dev.launch(a);
      const Summary sm = summarize(L, harts);
      const bool ok = L.ok && sm.bad == 0 && sm.tensorErrors == 0;
      bad += !ok;
      const double lines = double(__builtin_popcountll(a.mask));
      std::printf("SPARSITY {\"test\":\"tload\",\"where\":\"%s\",\"mask\":\"0x%04llx\",\"lines\":%.0f,\"src_bytes\":%llu,"
                  "\"minions\":%zu,\"shire_mask\":\"0x%llx\",\"iters\":%llu,\"launch\":%d,\"cycles_max\":%llu,"
                  "\"cycles_mean\":%.1f,\"cycles_per_load\":%.3f,\"bytes_requested\":%.0f,\"wall_s\":%.6f,"
                  "\"gbps_wall\":%.3f,\"t_start_ms\":%lld,\"t_end_ms\":%lld,\"ghz\":%.4f,\"tensor_errors\":%llu,\"ok\":%s}\n",
                  o.where.c_str(), (unsigned long long)a.mask, lines, (unsigned long long)a.src_bytes, harts.size(),
                  (unsigned long long)o.shireMask, (unsigned long long)iters, launchNo, (unsigned long long)sm.cmax,
                  sm.cmean, sm.cmean / double(iters), lines * 64 * double(iters) * double(harts.size()), L.wallS,
                  L.wallS > 0 ? lines * 64 * double(iters) * double(harts.size()) / L.wallS / 1e9 : 0.0, L.t0Ms,
                  L.t1Ms, L.ghz, (unsigned long long)sm.tensorErrors, ok ? "true" : "false");
      std::fflush(stdout);
      return L.wallS;
    };
    repeatFor(o, dev, o.iters ? o.iters : (o.sysemu ? 8 : 20000), one);
    if (dev.overBudget()) {
      break;
    }
  }
  return bad ? 1 : 0;
}

/* ------------------------------------------------------------------------------------------ gemv */

int testGemv(const Options& o, Session& dev) {
  if (o.perShire != 32) {
    throw std::runtime_error("--test gemv needs --per-shire 32 (all minions of a shire share the reduction)");
  }
  const auto harts = participants(o.shireMask, 32, 1);
  std::mt19937_64 rng(o.seed);
  std::uniform_real_distribution<double> u(0, 1);
  // W (N x K) as small integers; slabs of W^T per minion: minion m = 32 s + j covers block 2s + j/16 and
  // k in [256 (j%16), +256); line k of its slab holds W[16 block + 0..15][k].
  std::vector<int8_t> W(size_t(SP_GEMV_N) * SP_GEMV_K);
  for (auto& w : W) {
    w = int8_t(smallNonzero(rng));
  }
  std::vector<float> slabs(size_t(SP_MINIONS) * SP_GEMV_SLAB_LINES * 16);
  for (uint64_t m = 0; m < SP_MINIONS; ++m) {
    const uint64_t s = m / 32, j = m % 32, block = 2 * s + j / 16, k0 = 256 * (j % 16);
    for (uint64_t k = 0; k < 256; ++k) {
      for (uint64_t c = 0; c < 16; ++c) {
        slabs[(m * 256 + k) * 16 + c] = float(W[(block * 16 + c) * SP_GEMV_K + k0 + k]);
      }
    }
  }
  SpArgs a{};
  a.mode = SP_GEMV;
  a.shire_mask = o.shireMask;
  a.per_shire = 32;
  a.w = dev.put("w", slabs.data(), slabs.size() * 4);
  a.out = dev.put("out", nullptr, SP_MINIONS * 64);  // y, or one partial row per minion
  a.gemv_flags = (o.gemv == "dense" ? 0 : o.gemv == "masked" ? SP_GEMV_MASKED_LOADS
                                                               : SP_GEMV_MASKED_LOADS | SP_GEMV_SKIP_EMPTY) |
                 (o.gemvTree ? SP_GEMV_TREE : 0);

  int bad = 0;
  for (double s : parseDoubles(o.sweep)) {
    std::vector<float> x(SP_GEMV_K);
    std::vector<uint16_t> xmask(SP_GEMV_K / 16, 0);
    uint64_t nnz = 0;
    for (uint64_t k = 0; k < SP_GEMV_K; ++k) {
      x[k] = u(rng) < s ? 0.0f : float(smallNonzero(rng));
      if (x[k] != 0) {
        xmask[k / 16] |= uint16_t(1u << (k % 16));
        ++nnz;
      }
    }
    a.x = dev.put("x", x.data(), x.size() * 4);
    a.xmask = dev.put("xmask", xmask.data(), xmask.size() * 2);
    std::vector<double> yref(SP_GEMV_N, 0);
    for (uint64_t n = 0; n < SP_GEMV_N; ++n) {
      for (uint64_t k = 0; k < SP_GEMV_K; ++k) {
        yref[n] += double(W[n * SP_GEMV_K + k]) * x[k];
      }
    }
    auto one = [&](uint64_t iters, int launchNo) -> double {
      a.iters = iters;
      std::vector<float> junk(SP_MINIONS * 16, -12345.0f);
      dev.put("out", junk.data(), junk.size() * 4);
      const auto L = dev.launch(a);
      const Summary sm = summarize(L, harts);
      std::vector<float> got(SP_MINIONS * 16);
      dev.get("out", got.data(), got.size() * 4);
      std::vector<double> y(SP_GEMV_N, 0);
      if (o.gemvTree) {
        for (uint64_t n = 0; n < SP_GEMV_N; ++n) {
          y[n] = got[n];
        }
      } else {  // add the 16 partial rows of each block
        for (uint64_t m = 0; m < SP_MINIONS; ++m) {
          const uint64_t block = 2 * (m / 32) + (m % 32) / 16;
          for (uint64_t c = 0; c < 16; ++c) {
            y[block * 16 + c] += got[m * 16 + c];
          }
        }
      }
      // A block's time is its slowest minion's, from the barrier at the start of each layer (with the tree, the
      // root finishes last).
      uint64_t wrong = 0, timeouts = 0;
      std::vector<double> blockCycles(SP_MINIONS / 16, -1);
      double slices = 0, lines = 0;
      for (uint64_t h : harts) {
        const uint64_t m = h >> 1, sh = m / 32, j = m % 32, block = 2 * sh + j / 16;
        const auto& r = L.res[h];
        timeouts += r.magic == SP_MAGIC && r.count != iters;  // a barrier gave up
        slices += double(r.aux);
        lines += double(r.aux2);
        blockCycles[block] = std::max(blockCycles[block], double(r.cycles));
        if (j % 16 == 0) {
          for (uint64_t c = 0; c < 16; ++c) {
            wrong += y[block * 16 + c] != yref[block * 16 + c];
          }
        }
      }
      double rootSum = 0, rootMax = 0;
      uint64_t roots = 0;
      for (double c : blockCycles) {
        if (c >= 0) {
          rootSum += c;
          rootMax = std::max(rootMax, c);
          ++roots;
        }
      }
      const bool ok = L.ok && sm.bad == 0 && sm.tensorErrors == 0 && wrong == 0 && timeouts == 0;
      bad += !ok;
      std::printf("SPARSITY {\"test\":\"gemv\",\"gemv\":\"%s\",\"reduce\":\"%s\",\"layer_time\":\"block-max\",\"timeouts\":%llu,\"sparsity\":%.4f,\"nnz\":%llu,\"shire_mask\":\"0x%llx\","
                  "\"minions\":%zu,\"iters\":%llu,\"launch\":%d,\"cycles_per_layer_mean\":%.1f,"
                  "\"cycles_per_layer_max\":%.1f,\"slices_per_minion\":%.2f,\"lines_per_minion\":%.2f,\"wall_s\":%.6f,"
                  "\"t_start_ms\":%lld,\"t_end_ms\":%lld,\"ghz\":%.4f,\"wrong\":%llu,\"tensor_errors\":%llu,\"ok\":%s}\n",
                  o.gemv.c_str(), o.gemvTree ? "tree" : "host", (unsigned long long)timeouts, s,
                  (unsigned long long)nnz, (unsigned long long)o.shireMask, harts.size(),
                  (unsigned long long)iters, launchNo, roots ? rootSum / double(roots) / double(iters) : 0.0,
                  rootMax / double(iters), slices / double(harts.size()), lines / double(harts.size()), L.wallS,
                  L.t0Ms, L.t1Ms, L.ghz, (unsigned long long)wrong, (unsigned long long)sm.tensorErrors,
                  ok ? "true" : "false");
      std::fflush(stdout);
      return L.wallS;
    };
    repeatFor(o, dev, o.iters ? o.iters : (o.sysemu ? 2 : 2000), one);
    if (dev.overBudget()) {
      break;
    }
  }
  return bad ? 1 : 0;
}

/* ------------------------------------------------------------------------------------------ diverge */

// Pareto(alpha) with minimum xmin, rounded up and capped at kmax; alpha <= 0 gives the constant mean.
std::vector<uint32_t> drawK(size_t n, double alpha, double mean, uint64_t kmax, std::mt19937_64& rng) {
  std::vector<uint32_t> k(n);
  std::uniform_real_distribution<double> u(std::numeric_limits<double>::min(), 1.0);
  const double xmin = alpha > 1 ? mean * (alpha - 1) / alpha : mean;
  for (auto& v : k) {
    const double x = alpha > 0 ? xmin * std::pow(u(rng), -1.0 / alpha) : mean;
    v = uint32_t(std::min<double>(double(kmax), std::max(1.0, std::ceil(x))));
  }
  return k;
}

// SIMT model on the same items: groups of `w` consecutive items run for as long as their longest item.
double groupEfficiency(const std::vector<uint32_t>& k, size_t w) {
  double useful = 0, spent = 0;
  for (size_t g = 0; g < k.size(); g += w) {
    uint32_t mx = 0;
    for (size_t i = g; i < std::min(k.size(), g + w); ++i) {
      useful += k[i];
      mx = std::max(mx, k[i]);
    }
    spent += double(mx) * double(w);
  }
  return spent > 0 ? useful / spent : 0;
}

int testDiverge(const Options& o, Session& dev) {
  const uint64_t variant = o.variant == "static" ? SP_DIV_STATIC : o.variant == "refill" ? SP_DIV_REFILL
                                                                                         : SP_DIV_SCALAR;
  if (o.harts < 1 || o.harts > 2) {
    throw std::runtime_error("--harts must be 1 or 2");
  }
  const auto harts = participants(o.shireMask, o.perShire, o.harts);
  std::mt19937_64 rng(o.seed);
  // --items per hart on average; every hart takes chunks from one shared queue.
  const size_t total = (harts.size() * o.items + SP_DIV_CHUNK - 1) / SP_DIV_CHUNK * SP_DIV_CHUNK;
  const auto k = drawK(total, o.alpha, o.meanK, o.kmax, rng);
  SpArgs a{};
  a.mode = SP_DIVERGE;
  a.shire_mask = o.shireMask;
  a.per_shire = o.perShire;
  a.items = dev.put("items", k.data(), k.size() * 4);
  a.out = dev.put("out", nullptr, k.size() * 4);
  a.n_items = total;
  a.variant = variant;
  a.harts = o.harts;
  a.iters = 1;
  double kmean = 0;
  uint32_t kmx = 0;
  for (uint32_t v : k) {
    kmean += v;
    kmx = std::max(kmx, v);
  }
  kmean /= double(k.size());
  int bad = 0;
  double spent = 0;
  for (int launchNo = 0;; ++launchNo) {
    const uint64_t zero[8] = {};
    a.counter = dev.put("counter", zero, sizeof(zero));
    std::vector<uint32_t> junk(k.size(), 0xFFFFFFFFu);
    dev.put("out", junk.data(), junk.size() * 4);
    const auto L = dev.launch(a);
    std::vector<uint32_t> out(k.size());
    dev.get("out", out.data(), out.size() * 4);
    uint64_t wrong = 0;
    for (size_t i = 0; i < k.size(); ++i) {
      float f;
      std::memcpy(&f, &out[i], 4);
      wrong += f != float(k[i]);
    }
    double useful = 0, iters = 0, refills = 0, chunks = 0, cycMax = 0, cycSum = 0;
    uint64_t reported = 0;
    for (uint64_t h : harts) {
      const auto& r = L.res[h];
      if (r.magic != SP_MAGIC) {
        continue;
      }
      ++reported;
      useful += double(r.count);
      iters += double(r.aux);
      refills += double(r.aux2 & 0xFFFFFFFFu);
      chunks += double(r.aux2 >> 32);
      cycMax = std::max(cycMax, double(r.cycles));
      cycSum += double(r.cycles);
    }
    double kSum = 0;
    for (uint32_t v : k) {
      kSum += v;
    }
    const bool ok = L.ok && reported == harts.size() && wrong == 0 && useful == kSum &&
                    chunks == double(total / SP_DIV_CHUNK);
    bad += !ok;
    const double laneSlots = variant == SP_DIV_SCALAR ? iters : 8 * iters;
    const size_t minions = harts.size() / o.harts;
    std::printf("SPARSITY {\"test\":\"diverge\",\"variant\":\"%s\",\"alpha\":%.3f,\"mean_k_target\":%.1f,"
                "\"mean_k\":%.2f,\"max_k\":%u,\"items\":%zu,\"chunk\":%u,\"chains\":%u,\"harts\":%zu,\"minions\":%zu,"
                "\"harts_per_minion\":%llu,\"launch\":%d,\"useful_lane_iters\":%.0f,\"loop_iters\":%.0f,"
                "\"refills\":%.0f,\"chunks\":%.0f,\"lane_efficiency\":%.4f,\"cycles_max\":%.0f,\"cycles_mean\":%.0f,"
                "\"fma_per_cycle_per_minion\":%.4f,\"simt8_efficiency\":%.4f,\"simt32_efficiency\":%.4f,\"wall_s\":%.6f,"
                "\"t_start_ms\":%lld,\"t_end_ms\":%lld,\"ghz\":%.4f,\"wrong\":%llu,\"ok\":%s}\n",
                o.variant.c_str(), o.alpha, o.meanK, kmean, kmx, k.size(), (unsigned)SP_DIV_CHUNK,
                (unsigned)SP_DIV_CHAINS, harts.size(), minions, (unsigned long long)o.harts, launchNo, useful, iters,
                refills, chunks, laneSlots > 0 ? useful / laneSlots : 0.0, cycMax,
                reported ? cycSum / double(reported) : 0.0,
                cycMax > 0 ? double(SP_DIV_CHAINS) * useful / double(minions) / cycMax : 0.0, groupEfficiency(k, 8),
                groupEfficiency(k, 32), L.wallS, L.t0Ms, L.t1Ms, L.ghz, (unsigned long long)wrong,
                ok ? "true" : "false");
    std::fflush(stdout);
    spent += L.wallS;
    if (o.sysemu || o.seconds <= 0 || spent >= o.seconds || dev.overBudget()) {
      break;
    }
  }
  return bad ? 1 : 0;
}

/* ------------------------------------------------------------------------------------------ spin */

int testSpin(const Options& o, Session& dev) {
  const auto harts = participants(o.shireMask, o.perShire, 1);
  SpArgs a{};
  a.mode = SP_SPIN;
  a.shire_mask = o.shireMask;
  a.per_shire = o.perShire;
  int bad = 0;
  auto one = [&](uint64_t iters, int launchNo) -> double {
    a.iters = iters;
    const auto L = dev.launch(a);
    const Summary sm = summarize(L, harts);
    const bool ok = L.ok && sm.bad == 0;
    bad += !ok;
    std::printf("SPARSITY {\"test\":\"spin\",\"minions\":%zu,\"shire_mask\":\"0x%llx\",\"iters\":%llu,\"launch\":%d,"
                "\"cycles_max\":%llu,\"wall_s\":%.6f,\"t_start_ms\":%lld,\"t_end_ms\":%lld,\"ghz\":%.4f,\"ok\":%s}\n",
                harts.size(), (unsigned long long)o.shireMask, (unsigned long long)iters, launchNo,
                (unsigned long long)sm.cmax, L.wallS, L.t0Ms, L.t1Ms, L.ghz, ok ? "true" : "false");
    std::fflush(stdout);
    return L.wallS;
  };
  repeatFor(o, dev, o.iters ? o.iters : (o.sysemu ? 100 : 2000000), one);
  return bad ? 1 : 0;
}

}  // namespace

int main(int argc, char** argv) {
  registerRuntimeLogLevels();  // first, before any library starts a thread
  Options o;
  for (int i = 1; i < argc; ++i) {
    std::string a = argv[i];
    auto next = [&]() -> std::string {
      if (i + 1 >= argc) {
        std::fprintf(stderr, "%s needs a value\n", a.c_str());
        std::exit(2);
      }
      return argv[++i];
    };
    if (a == "--sysemu") o.sysemu = true;
    else if (a == "--sim-args") o.simArgs = next();
    else if (a == "--test") o.test = next();
    else if (a == "--type") o.type = next();
    else if (a == "--pattern") o.pattern = next();
    else if (a == "--values") o.values = next();
    else if (a == "--dump-tiles") o.dumpTiles = next();
    else if (a == "--stop-file") o.stopFile = next();
    else if (a == "--sweep") o.sweep = next();
    else if (a == "--b-sparsity") o.bSparsity = std::atof(next().c_str());
    else if (a == "--b-stream") o.bStream = true;
    else if (a == "--row-mask") o.rowMask = std::strtoll(next().c_str(), nullptr, 0);
    else if (a == "--where") o.where = next();
    else if (a == "--masks") o.masks = next();
    else if (a == "--gemv") o.gemv = next();
    else if (a == "--gemv-tree") o.gemvTree = true;
    else if (a == "--variant") o.variant = next();
    else if (a == "--alpha") o.alpha = std::atof(next().c_str());
    else if (a == "--mean-k") o.meanK = std::atof(next().c_str());
    else if (a == "--kmax") o.kmax = std::strtoull(next().c_str(), nullptr, 0);
    else if (a == "--items") o.items = std::strtoull(next().c_str(), nullptr, 0);
    else if (a == "--harts") o.harts = std::strtoull(next().c_str(), nullptr, 0);
    else if (a == "--iters") o.iters = std::strtoull(next().c_str(), nullptr, 0);
    else if (a == "--shires") o.shireMask = std::strtoull(next().c_str(), nullptr, 0);
    else if (a == "--per-shire") o.perShire = std::strtoull(next().c_str(), nullptr, 0);
    else if (a == "--seconds") o.seconds = std::atof(next().c_str());
    else if (a == "--seed") o.seed = std::strtoull(next().c_str(), nullptr, 0);
    else if (a == "--budget") o.budget = std::atof(next().c_str());
    else if (a == "--kernel") o.kernel = next();
    else {
      std::fprintf(stderr, "unknown option %s (see the comment at the top of host/main.cpp)\n", a.c_str());
      return 2;
    }
  }
  if (o.budget < 0) {
    o.budget = o.sysemu ? 1e9 : 8.0;  // the simulator is private; a real card is shared
  }
  if (o.shireMask == 0 || (o.shireMask >> 32) || o.perShire == 0 || o.perShire > 32) {
    std::fprintf(stderr, "bad --shires / --per-shire\n");
    return 2;
  }
  const auto elf = readFile(o.kernel);
  if (elf.empty()) {
    std::fprintf(stderr, "cannot read kernel %s\n", o.kernel.c_str());
    return 1;
  }
  try {
    if (o.test != "fma" && o.test != "tload" && o.test != "gemv" && o.test != "diverge" && o.test != "spin") {
      std::fprintf(stderr, "--test must be fma, tload, gemv, diverge or spin\n");
      return 2;
    }
    Session dev(o, elf);
    if (o.test == "fma" && isArmValues(o.values)) return testArm(o, dev);
    if (o.test == "fma") return testFma(o, dev);
    if (o.test == "tload") return testTload(o, dev);
    if (o.test == "gemv") return testGemv(o, dev);
    if (o.test == "diverge") return testDiverge(o, dev);
    return testSpin(o, dev);
  } catch (const std::exception& e) {
    std::fprintf(stderr, "FAIL: %s\n", e.what());
    return 1;
  }
}
