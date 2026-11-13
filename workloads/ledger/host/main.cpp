// ledger_host: the ledger's plain programs (../ledger_args.h, ../kernel/ledger.c) on every participating hart, in
// the simulator or, only with --card, on a card. One process: build the inputs, open the device, copy in, launch
// (--launches times), read back, close the device, check everything on the CPU, print one JSON line on stdout
// (progress on stderr). The session pattern is workloads/enercat's.
//
//   ledger_host (--sysemu [--sim-args "..."] | --card) --prog copy|sha256|sort
//       where:  --shires MASK (default 0xffffffff) --minions MASK (0 = all 32) --harts 1|2 (default 2)
//       copy:   --bytes TOTAL (default 1G; split evenly, each part a multiple of 256 B) --passes R (default 1)
//               --data zeros|random --width 32|8 (default 32: flw.ps/fsw.ps; 8: ld/sd)
//       sha256: --block B (default 2048; a multiple of 64) --repeat R (default 1): participant p hashes one message,
//               its own B-byte block repeated R times; --expect FILE (digests computed on the desk: one line per
//               participant, "p hex64"); --digests-out FILE
//       sort:   --keys N (default 512; a power of two) --reps R (default 1) --order sorted|shuffled
//       all:    --seed S (default 1) --launches K (default 1) --budget S (default 9.5) --max-kernel-s S (default 4)
//               --kernel ELF --dry (inputs and model only; no device) --selftest (the host's SHA-256 on test vectors)
//
// Inputs (reproducible on the desk, tools in ../ledger_desk.py): a splitmix64 stream per (seed, tag, participant):
//   s = seed ^ tag * 0xA0761D6478BD642F ^ (p + 1) * 0xE7037ED1A0B428DB (mod 2^64), then splitmix64 outputs.
//   copy random: tag 1, participant = the 8 B word's index / (part bytes / 8), the words in order;
//   sha256 block: tag 2, B/8 words, little-endian bytes; sort keys: tag 3, N keys = the top 32 bits of each output;
//   the shuffle: tag 4, Fisher-Yates from the last index down, j = output mod (i + 1). Sorted order = ascending.
//   The same multiset of keys for --order sorted and --order shuffled.
//
// Checks: copy, the destination equals the source byte for byte (read back whole) and every record's units;
// sha256, every participant's digest against this host's own SHA-256 when the message bytes in all are at most
// 2^30 (else a sample of 64 participants), and against --expect for every participant when given; sort, every
// participant's result equals std::sort of its input, and the kernel's own out-of-order count is 0.
//
// Card etiquette (as workloads/sparseparity): the device is held only between opening the runtime and tearing it
// down; a model of the kernel's time (constants below, deliberately slow) refuses a launch over --max-kernel-s; a
// launch's timeout is min(8 s, 2 x model + 1.5 s, the time left in --budget, counted from the process's start);
// after a timed-out launch the stream is aborted and nothing is read back. Without --card or --sysemu nothing opens.
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
#include "ledger_args.h"

// libetrt's thread-pool workers log at the custom levels VERBOSE_HIGH/MID/LOW, which only logging::LoggerDefault
// registers with g3log; registering them first removes the race behind aifoundry3's 1.08 s host crash
// (docs/findings/14-card-behaviour.md, "Traps"), as workloads/enercat and workloads/sparseparity do.
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
std::vector<std::byte> readFile(const std::string& path) {
  std::ifstream file(path, std::ios::binary);
  if (!file) return {};
  std::vector<std::byte> data(fs::file_size(path));
  file.read(reinterpret_cast<char*>(data.data()), static_cast<std::streamsize>(data.size()));
  return data;
}
uint64_t parseSize(const std::string& s) {
  char* end = nullptr;
  double v = std::strtod(s.c_str(), &end);
  switch (end && *end ? std::toupper(static_cast<unsigned char>(*end)) : 0) {
  case 'K': v *= 1024; break;
  case 'M': v *= 1024 * 1024; break;
  case 'G': v *= 1024.0 * 1024 * 1024; break;
  default: break;
  }
  return static_cast<uint64_t>(v);
}

// ---------------------------------------------------------------- the inputs' generator (ledger_desk.py mirrors it)
inline uint64_t splitmix64(uint64_t& s) {
  uint64_t z = (s += 0x9E3779B97F4A7C15ull);
  z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9ull;
  z = (z ^ (z >> 27)) * 0x94D049BB133111EBull;
  return z ^ (z >> 31);
}
inline uint64_t streamSeed(uint64_t seed, uint64_t tag, uint64_t p) {
  return seed ^ (tag * 0xA0761D6478BD642Full) ^ ((p + 1) * 0xE7037ED1A0B428DBull);
}

// ---------------------------------------------------------------- SHA-256 (FIPS 180-4), for the host's own check
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
  void finish(uint32_t out[8]) {
    const uint64_t bits = len * 8;
    uint8_t one = 0x80, zero = 0;
    update(&one, 1);
    while (nbuf != 56) update(&zero, 1);
    uint8_t L[8];
    for (int i = 0; i < 8; ++i) L[i] = uint8_t(bits >> (56 - 8 * i));
    update(L, 8);
    std::memcpy(out, h, sizeof h);
  }
};
constexpr uint32_t Sha256::K[64];

std::string hex8(const uint32_t w[8]) {
  char s[65];
  for (int i = 0; i < 8; ++i) std::snprintf(s + 8 * i, 9, "%08x", w[i]);
  return std::string(s, 64);
}

// ---------------------------------------------------------------- options
struct Options {
  bool sysemu = false, card = false, dry = false, selftest = false;
  std::string simArgs, prog, data = "random", order = "shuffled", expect, digestsOut;
  uint64_t shireMask = 0xffffffffull, minionMask = 0, harts = 2, seed = 1, launches = 1;
  uint64_t bytes = 1ull << 30, passes = 1, width = 32;  // copy
  uint64_t block = 2048, repeat = 1;                    // sha256
  uint64_t keys = 512, reps = 1;                        // sort
  double budget = 9.5, maxKernelS = 4.0;
  std::string kernel = KERNEL_ELF;
};

[[noreturn]] void usage(const char* argv0, const std::string& why = "") {
  if (!why.empty()) std::fprintf(stderr, "%s: %s\n", argv0, why.c_str());
  std::fprintf(stderr,
               "usage: %s (--sysemu [--sim-args ARGS] | --card | --dry | --selftest) --prog copy|sha256|sort"
               " [--shires MASK] [--minions MASK] [--harts 1|2] [--seed S] [--launches K] [--budget S]"
               " [--max-kernel-s S] [--kernel ELF]  copy: [--bytes TOTAL] [--passes R] [--data zeros|random]"
               " [--width 32|8]  sha256: [--block B] [--repeat R] [--expect FILE] [--digests-out FILE]"
               "  sort: [--keys N] [--reps R] [--order sorted|shuffled]\n",
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
    else if (a == "--selftest") o.selftest = true;
    else if (a == "--sim-args") o.simArgs = next();
    else if (a == "--prog") o.prog = next();
    else if (a == "--shires") o.shireMask = std::stoull(next(), nullptr, 0);
    else if (a == "--minions") o.minionMask = std::stoull(next(), nullptr, 0);
    else if (a == "--harts") o.harts = std::stoull(next());
    else if (a == "--seed") o.seed = std::stoull(next(), nullptr, 0);
    else if (a == "--launches") o.launches = std::stoull(next());
    else if (a == "--budget") o.budget = std::stod(next());
    else if (a == "--max-kernel-s") o.maxKernelS = std::stod(next());
    else if (a == "--kernel") o.kernel = next();
    else if (a == "--bytes") o.bytes = parseSize(next());
    else if (a == "--passes") o.passes = std::stoull(next());
    else if (a == "--data") o.data = next();
    else if (a == "--width") o.width = std::stoull(next());
    else if (a == "--block") o.block = parseSize(next());
    else if (a == "--repeat") o.repeat = std::stoull(next());
    else if (a == "--expect") o.expect = next();
    else if (a == "--digests-out") o.digestsOut = next();
    else if (a == "--keys") o.keys = std::stoull(next());
    else if (a == "--reps") o.reps = std::stoull(next());
    else if (a == "--order") o.order = next();
    else usage(argv[0], "unknown option " + a);
  }
  if (o.selftest) return o;
  if (int(o.sysemu) + int(o.card) + int(o.dry) != 1) usage(argv[0], "give exactly one of --sysemu, --card, --dry");
  if (o.prog != "copy" && o.prog != "sha256" && o.prog != "sort") usage(argv[0], "--prog copy|sha256|sort");
  if (o.harts != 1 && o.harts != 2) usage(argv[0], "--harts 1|2");
  if ((o.shireMask & 0xffffffffull) == 0 || (o.shireMask >> 32)) usage(argv[0], "--shires: a mask of shires 0-31");
  if (o.launches < 1 || o.launches > 100) usage(argv[0], "--launches 1-100");
  if (o.budget > 9.5) usage(argv[0], "--budget at most 9.5 s");
  return o;
}

uint64_t participants(const Options& o) {
  const uint64_t mm = o.minionMask ? (o.minionMask & 0xffffffffull) : 0xffffffffull;
  return uint64_t(__builtin_popcountll(o.shireMask & 0xffffffffull)) * uint64_t(__builtin_popcountll(mm)) * o.harts;
}

// The participant number the kernel computes for a hart (kernel/ledger.c, entry_point), or -1.
int64_t participant(const Options& o, uint64_t hart) {
  const uint64_t shire = hart >> 6, thread = hart & 1, minion = (hart >> 1) & 31;
  const uint64_t mm = o.minionMask ? (o.minionMask & 0xffffffffull) : 0xffffffffull;
  if (shire >= 32 || !((o.shireMask >> shire) & 1) || (thread && o.harts < 2) || !((mm >> minion) & 1)) return -1;
  const uint64_t ps = __builtin_popcountll(mm), sb = __builtin_popcountll(o.shireMask & ((1ull << shire) - 1));
  const uint64_t mb = __builtin_popcountll(mm & ((1ull << minion) - 1));
  return int64_t((sb * ps + mb) * o.harts + (o.harts >= 2 ? thread : 0));
}

// The guard's model of one launch on a card, deliberately slow (so it refuses early): a copy at 20 GB/s of DRAM
// traffic (two bytes moved per byte copied; the energy manual's DRAM figure is 76 GB/s), and the other two at 0.25
// instructions per hart-cycle at 600 MHz, 4,500 instructions a compression and 20 per key per merge level.
double modelSeconds(const Options& o, uint64_t P) {
  if (o.prog == "copy") return double(o.bytes) * double(o.passes) * 2.0 / 20e9;
  const double ipc = 0.25 * 600e6;
  if (o.prog == "sha256") return (double(o.repeat) * double(o.block / 64) + 1) * 4500.0 / ipc;
  const double lg = std::log2(double(o.keys));
  (void)P;
  return double(o.reps) * double(o.keys) * (20.0 * lg + 6.0) / ipc;
}

// ---------------------------------------------------------------- the device (workloads/enercat's Session)
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
    stream_ = rt_->createStream(dev_);
    const auto load = rt_->loadCode(stream_, elf.data(), elf.size());
    rt_->waitForEvent(load.event_);
    kernel_ = load.kernel_;
    results_ = rt_->mallocDevice(dev_, LG_MAX_HARTS * sizeof(LgResult));
    std::fprintf(stderr, "device ready in %.2f s\n", secondsSince(tOpen_));
  }
  ~Session() {
    for (auto* p : allocs_) rt_->freeDevice(dev_, p);
    rt_->freeDevice(dev_, results_);
    rt_->unloadCode(kernel_);
    rt_->destroyStream(stream_);
    std::fprintf(stderr, "device held for %.2f s\n", secondsSince(tOpen_));
  }
  // `bytes` of device memory, 4 KB aligned.
  std::byte* alloc(size_t bytes) {
    allocs_.push_back(rt_->mallocDevice(dev_, bytes + 4096));
    const uintptr_t v = reinterpret_cast<uintptr_t>(allocs_.back());
    return reinterpret_cast<std::byte*>((v + 4095) & ~uintptr_t(4095));
  }
  void put(const void* src, std::byte* dst, size_t bytes) {
    rt_->memcpyHostToDevice(stream_, reinterpret_cast<const std::byte*>(src), dst, bytes);
    rt_->waitForStream(stream_);
  }
  void get(const std::byte* src, void* dst, size_t bytes) {
    rt_->memcpyDeviceToHost(stream_, src, reinterpret_cast<std::byte*>(dst), bytes);
    rt_->waitForStream(stream_);
  }

  long long t0Ms = 0, t1Ms = 0;  // epoch bounds of the last launch, for lining up with power samples

  bool launch(LgArgs a, int timeoutS, std::vector<LgResult>& res, double& wallS) {
    res.assign(LG_MAX_HARTS, LgResult{});
    put(res.data(), results_, res.size() * sizeof(LgResult));
    a.results = reinterpret_cast<uint64_t>(results_);
    rt::KernelLaunchOptions opts;
    opts.setShireMask(o_.shireMask);
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
    get(results_, res.data(), res.size() * sizeof(LgResult));
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
  std::byte* results_ = nullptr;
  std::vector<std::byte*> allocs_;
};

int selftest() {
  // FIPS 180-2 examples: "abc", the empty message, the 448-bit message, and one million 'a'.
  struct V { std::string msg; uint64_t times; const char* hex; };
  const V vs[] = {
      {"abc", 1, "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"},
      {"", 1, "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"},
      {"abcdbcdecdefdefgefghfghighijhijkijkljklmklmnlmnomnopnopq", 1,
       "248d6a61d20638b8e5c026930c3e6039a33ce45964ff2167f6ecedd419db06c1"},
      {"a", 1000000, "cdc76e5c9914fb9281a1c7e284d73e67f1809a48a497200e046d39ccc7112cd0"}};
  int bad = 0;
  for (const auto& v : vs) {
    Sha256 s;
    for (uint64_t i = 0; i < v.times; ++i) s.update(reinterpret_cast<const uint8_t*>(v.msg.data()), v.msg.size());
    uint32_t d[8];
    s.finish(d);
    const bool ok = hex8(d) == v.hex;
    bad += !ok;
    std::printf("SELFTEST %s x%llu %s %s\n", v.msg.size() > 8 ? (v.msg.substr(0, 8) + "...").c_str() : v.msg.c_str(),
                (unsigned long long)v.times, hex8(d).c_str(), ok ? "OK" : "MISMATCH");
  }
  std::printf("SELFTEST %s\n", bad ? "FAIL" : "PASS");
  return bad ? 1 : 0;
}

}  // namespace

int main(int argc, char** argv) {
  registerRuntimeLogLevels();
  const Options o = parse(argc, argv);
  if (o.selftest) return selftest();
  const uint64_t P = participants(o);
  const double model = modelSeconds(o, P);

  // ---- inputs
  LgArgs a{};
  a.shire_mask = o.shireMask;
  a.minion_mask = o.minionMask;
  a.harts = o.harts;
  std::vector<uint8_t> src;          // copy: the whole source; sha256: the blocks
  std::vector<uint32_t> keys;        // sort: every participant's input, in order
  size_t srcBytes = 0, dstBytes = 0;
  uint64_t part = 0;
  if (o.prog == "copy") {
    part = o.bytes / P;
    if (part == 0 || part % 256 || part * P != o.bytes) {
      std::fprintf(stderr, "copy: --bytes %llu does not split into %llu parts of a multiple of 256 B\n",
                   (unsigned long long)o.bytes, (unsigned long long)P);
      return 2;
    }
    if (o.width != 32 && o.width != 8) usage(argv[0], "--width 32|8");
    if (o.data != "zeros" && o.data != "random") usage(argv[0], "--data zeros|random");
    a.prog = LG_COPY; a.bytes = part; a.reps = o.passes; a.width = o.width;
    srcBytes = dstBytes = o.bytes;
    src.assign(o.bytes, 0);
    if (o.data == "random") {
      const uint64_t wpp = part / 8;
      for (uint64_t p = 0; p < P; ++p) {
        uint64_t s = streamSeed(o.seed, 1, p);
        uint8_t* q = src.data() + p * part;
        for (uint64_t w = 0; w < wpp; ++w) { const uint64_t x = splitmix64(s); std::memcpy(q + 8 * w, &x, 8); }
      }
    }
  } else if (o.prog == "sha256") {
    if (o.block == 0 || o.block % 64) usage(argv[0], "--block: a multiple of 64");
    a.prog = LG_SHA256; a.bytes = o.block; a.reps = o.repeat;
    srcBytes = o.block * P;
    src.assign(srcBytes, 0);
    for (uint64_t p = 0; p < P; ++p) {
      uint64_t s = streamSeed(o.seed, 2, p);
      uint8_t* q = src.data() + p * o.block;
      for (uint64_t w = 0; w < o.block / 8; ++w) { const uint64_t x = splitmix64(s); std::memcpy(q + 8 * w, &x, 8); }
    }
  } else {
    if (o.keys < 16 || (o.keys & (o.keys - 1)) || o.keys > (1u << 20)) usage(argv[0], "--keys: a power of two, 16..2^20");
    if (o.order != "sorted" && o.order != "shuffled") usage(argv[0], "--order sorted|shuffled");
    a.prog = LG_SORT; a.bytes = o.keys; a.reps = o.reps;
    keys.assign(o.keys * P, 0);
    for (uint64_t p = 0; p < P; ++p) {
      uint32_t* k = keys.data() + p * o.keys;
      uint64_t s = streamSeed(o.seed, 3, p);
      for (uint64_t i = 0; i < o.keys; ++i) k[i] = uint32_t(splitmix64(s) >> 32);
      std::sort(k, k + o.keys);
      if (o.order == "shuffled") {
        uint64_t t = streamSeed(o.seed, 4, p);
        for (uint64_t i = o.keys - 1; i > 0; --i) std::swap(k[i], k[splitmix64(t) % (i + 1)]);
      }
    }
    srcBytes = keys.size() * 4;
    dstBytes = keys.size() * 8;
  }

  // ---- the expected digests from the desk (sha256)
  std::map<uint64_t, std::string> expect;
  if (!o.expect.empty()) {
    std::ifstream f(o.expect);
    if (!f) { std::fprintf(stderr, "cannot read %s\n", o.expect.c_str()); return 2; }
    for (std::string line; std::getline(f, line);) {
      std::istringstream ls(line);
      uint64_t p; std::string h;
      if (ls >> p >> h) expect[p] = h;
    }
  }

  std::printf("{\"ledger\":1,\"prog\":\"%s\",\"device\":\"%s\",\"participants\":%llu,\"shire_mask\":\"0x%llx\","
              "\"minion_mask\":\"0x%llx\",\"harts\":%llu,\"seed\":%llu,\"model_s\":%.4f",
              o.prog.c_str(), o.sysemu ? "sysemu" : (o.card ? "card" : "dry"), (unsigned long long)P,
              (unsigned long long)o.shireMask, (unsigned long long)o.minionMask, (unsigned long long)o.harts,
              (unsigned long long)o.seed, model);
  if (o.prog == "copy")
    std::printf(",\"bytes\":%llu,\"part_bytes\":%llu,\"passes\":%llu,\"data\":\"%s\",\"width\":%llu",
                (unsigned long long)o.bytes, (unsigned long long)part, (unsigned long long)o.passes, o.data.c_str(),
                (unsigned long long)o.width);
  else if (o.prog == "sha256")
    std::printf(",\"block\":%llu,\"repeat\":%llu,\"message_bytes\":%llu,\"compressions_per_participant\":%llu",
                (unsigned long long)o.block, (unsigned long long)o.repeat, (unsigned long long)(o.block * o.repeat),
                (unsigned long long)(o.repeat * (o.block / 64) + 1));
  else
    std::printf(",\"keys\":%llu,\"reps\":%llu,\"order\":\"%s\"", (unsigned long long)o.keys,
                (unsigned long long)o.reps, o.order.c_str());
  if (o.dry) { std::printf(",\"status\":\"DRY\"}\n"); return 0; }
  if (o.card && model > o.maxKernelS) {
    std::printf(",\"status\":\"REFUSED\",\"why\":\"model %.3f s over --max-kernel-s %.3f\"}\n", model, o.maxKernelS);
    return 3;
  }

  const auto elf = readFile(o.kernel);
  if (elf.empty()) { std::fprintf(stderr, "cannot read kernel %s\n", o.kernel.c_str()); return 2; }

  // ---- the device: copy in, launch, read back, close
  std::vector<LgResult> res;
  std::vector<double> wall;
  std::vector<uint8_t> out;            // copy: the destination; sort: the work area
  std::vector<long long> spans;
  bool launchOk = true;
  uint64_t launched = 0;
  {
    Session ses(o, elf);
    std::byte* dS = ses.alloc(srcBytes);
    std::byte* dD = dstBytes ? ses.alloc(dstBytes) : nullptr;
    if (o.prog == "sort") ses.put(keys.data(), dS, srcBytes);
    else ses.put(src.data(), dS, srcBytes);
    if (o.prog == "copy" || o.prog == "sort") {   // a pattern no input has, so a missed store shows (the sort's
      // work area too: an identical sort left in DRAM by an earlier run could hide a missing write-back)
      std::vector<uint8_t> fill(dstBytes, 0x5A);
      ses.put(fill.data(), dD, dstBytes);
    }
    a.src = reinterpret_cast<uint64_t>(dS);
    a.dst = reinterpret_cast<uint64_t>(dD);
    for (uint64_t k = 0; k < o.launches; ++k) {
      int timeoutS = 3600;
      if (o.card) {
        const double left = o.budget - secondsSince(kStart);
        timeoutS = int(std::min({8.0, 2.0 * model + 1.5, left}));
        if (timeoutS < 1 || left < model + 0.5) { std::fprintf(stderr, "budget spent before launch %llu\n", (unsigned long long)k); break; }
      }
      double w = 0;
      const bool ok = ses.launch(a, timeoutS, res, w);
      wall.push_back(w);
      spans.push_back(ses.t0Ms);
      spans.push_back(ses.t1Ms);
      ++launched;
      if (!ok) { launchOk = false; break; }
    }
    if (launchOk && dstBytes) {
      out.assign(dstBytes, 0);
      ses.get(dD, out.data(), dstBytes);
    }
  }

  // ---- checks
  uint64_t recOk = 0, recBad = 0, cycMax = 0, cycMin = ~0ull, units = 0, nCyc = 0;
  double cycSum = 0;
  std::vector<int64_t> partOfHart(LG_MAX_HARTS, -1);
  for (uint64_t h = 0; h < LG_MAX_HARTS; ++h) partOfHart[h] = participant(o, h);
  for (uint64_t h = 0; h < LG_MAX_HARTS && launchOk; ++h) {
    if (partOfHart[h] < 0) continue;
    const LgResult& r = res[h];
    const bool ok = r.magic == LG_MAGIC && r.hart == h && int64_t(r.participant) == partOfHart[h];
    ok ? ++recOk : ++recBad;
    units += r.units;
    if (!(h & 1)) {
      cycMax = std::max<uint64_t>(cycMax, r.cycles);
      cycMin = std::min<uint64_t>(cycMin, r.cycles);
      cycSum += double(r.cycles);
      ++nCyc;
    }
  }
  uint64_t unitsExpect = 0, checked = 0, mismatches = 0, expectChecked = 0, expectMismatch = 0;
  std::string first;
  if (o.prog == "copy") {
    unitsExpect = o.bytes * o.passes;
    if (launchOk) {
      for (uint64_t p = 0; p < P; ++p) {
        ++checked;
        if (std::memcmp(out.data() + p * part, src.data() + p * part, part)) {
          ++mismatches;
          if (first.empty()) first = "participant " + std::to_string(p);
        }
      }
    }
  } else if (o.prog == "sha256") {
    unitsExpect = (o.repeat * (o.block / 64) + 1) * P;
    const bool all = double(o.block) * double(o.repeat) * double(P) <= double(1ull << 30);
    std::FILE* dout = o.digestsOut.empty() ? nullptr : std::fopen(o.digestsOut.c_str(), "w");
    for (uint64_t h = 0; h < LG_MAX_HARTS && launchOk; ++h) {
      const int64_t p = partOfHart[h];
      if (p < 0) continue;
      const std::string got = hex8(res[h].word);
      if (dout) std::fprintf(dout, "%lld %s\n", (long long)p, got.c_str());
      if (all || p < 32 || p >= int64_t(P) - 32) {
        Sha256 s;
        const uint8_t* blk = src.data() + uint64_t(p) * o.block;
        for (uint64_t r = 0; r < o.repeat; ++r) s.update(blk, o.block);
        uint32_t d[8];
        s.finish(d);
        ++checked;
        if (hex8(d) != got) { ++mismatches; if (first.empty()) first = "participant " + std::to_string(p); }
      }
      if (!expect.empty()) {
        ++expectChecked;
        auto it = expect.find(uint64_t(p));
        if (it == expect.end() || it->second != got) {
          ++expectMismatch;
          if (first.empty()) first = "participant " + std::to_string(p) + " (--expect)";
        }
      }
    }
    if (dout) std::fclose(dout);
  } else {
    unitsExpect = o.reps * P;
    const uint64_t n = o.keys;
    const bool inSecond = (__builtin_ctzll(n) & 1) != 0;   // log2(n) merge levels, ping-pong from the first buffer
    for (uint64_t h = 0; h < LG_MAX_HARTS && launchOk; ++h) {
      const int64_t p = partOfHart[h];
      if (p < 0) continue;
      std::vector<uint32_t> want(keys.begin() + p * n, keys.begin() + (p + 1) * n);
      std::sort(want.begin(), want.end());
      const uint32_t* got = reinterpret_cast<const uint32_t*>(out.data()) + uint64_t(p) * 2 * n + (inSecond ? n : 0);
      ++checked;
      const bool ok = std::equal(want.begin(), want.end(), got) && res[h].word[0] == 0 && res[h].word[3] == uint32_t(inSecond);
      if (!ok) { ++mismatches; if (first.empty()) first = "participant " + std::to_string(p); }
    }
  }
  const bool pass = launchOk && launched == o.launches && recBad == 0 && recOk == P && units == unitsExpect &&
                    checked > 0 && mismatches == 0 && expectMismatch == 0 &&
                    (o.expect.empty() || expectChecked == P);
  std::printf(",\"launches\":%llu,\"wall_s\":[", (unsigned long long)launched);
  for (size_t i = 0; i < wall.size(); ++i) std::printf("%s%.4f", i ? "," : "", wall[i]);
  std::printf("],\"launch_epoch_ms\":[");
  for (size_t i = 0; i < spans.size(); ++i) std::printf("%s%lld", i ? "," : "", spans[i]);
  std::printf("],\"records_ok\":%llu,\"records_bad\":%llu,\"units\":%llu,\"units_expected\":%llu,"
              "\"hart0_cycles\":{\"max\":%llu,\"min\":%llu,\"mean\":%.1f,\"n\":%llu},"
              "\"checked\":%llu,\"mismatches\":%llu,\"expect_checked\":%llu,\"expect_mismatches\":%llu,"
              "\"first_mismatch\":\"%s\",\"status\":\"%s\"}\n",
              (unsigned long long)recOk, (unsigned long long)recBad, (unsigned long long)units,
              (unsigned long long)unitsExpect, (unsigned long long)cycMax, (unsigned long long)(nCyc ? cycMin : 0),
              nCyc ? cycSum / double(nCyc) : 0.0, (unsigned long long)nCyc, (unsigned long long)checked,
              (unsigned long long)mismatches, (unsigned long long)expectChecked, (unsigned long long)expectMismatch,
              first.c_str(), pass ? "PASS" : "FAIL");
  return pass ? 0 : 1;
}
