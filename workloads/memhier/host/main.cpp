// Memory-hierarchy probes on ET-SoC-1 (see ../README.md). Every measurement prints one line
//   MEMHIER {json}
//
//   memhier_host [--sysemu] --test chase [--where dram|scp] [--sizes 256,4K,1M,...] [--steps N]
//                [--chaser-shire S] [--chaser-minion M] [--thread T] [--scp-shire local|all|K]
//   memhier_host [--sysemu] --test stream --where dram|scp-local|scp-remote --bytes-per-minion B
//                [--scp-shift K] [--seconds T] [--shires MASK]
//   memhier_host [--sysemu] --test l1|spin [--seconds T] [--shires MASK]
//
// The card is shared, so the device is open only while measuring. Chains are prepared before
// it is opened, and a budget (--budget, default 8 s on silicon) stops further launches.
#include <runtime/IRuntime.h>
#include <runtime/Types.h>
#include <device-layer/IDeviceLayer.h>
#include <sw-sysemu/SysEmuOptions.h>

#include <algorithm>
#include <cctype>
#include <chrono>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <limits>
#include <numeric>
#include <random>
#include <sstream>
#include <string>
#include <vector>

#include "Constants.h"
#include "memhier_args.h"

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

uint64_t parseSize(const std::string& s) {  // 256, 4K, 2M, 1G
  char* end = nullptr;
  double v = std::strtod(s.c_str(), &end);
  switch (end && *end ? std::toupper(*end) : 0) {
  case 'K': v *= 1024; break;
  case 'M': v *= 1024 * 1024; break;
  case 'G': v *= 1024.0 * 1024 * 1024; break;
  default: break;
  }
  return static_cast<uint64_t>(v);
}

std::vector<uint64_t> parseSizes(const std::string& s) {
  std::vector<uint64_t> out;
  std::stringstream ss(s);
  for (std::string item; std::getline(ss, item, ',');) {
    if (!item.empty()) {
      out.push_back(parseSize(item));
    }
  }
  return out;
}

// Successor array of one random cycle through all n lines, so a chase visits every line
// in an order that no prefetcher can guess.
std::vector<uint32_t> randomCycle(size_t n, std::mt19937_64& rng) {
  std::vector<uint32_t> order(n);
  std::iota(order.begin(), order.end(), 0u);
  std::shuffle(order.begin(), order.end(), rng);
  std::vector<uint32_t> next(n);
  for (size_t j = 0; j < n; ++j) {
    next[order[j]] = order[(j + 1) % n];
  }
  return next;
}

uint64_t walk(const std::vector<uint32_t>& next, uint64_t steps) {
  uint64_t i = 0;
  for (uint64_t s = 0; s < steps; ++s) {
    i = next[i];
  }
  return i;
}

uint64_t round8(uint64_t v) {
  return (v + 7) / 8 * 8;
}

struct Options {
  bool sysemu = false;
  std::string simArgs;
  std::string test;
  std::string where = "dram";
  std::string sizes = "256,512,768,1K,2K,4K,8K,16K,32K,64K,128K,256K,384K,512K,768K,1M,2M,4M,8M,16M,24M,32M,48M,64M,128M,256M";
  uint64_t steps = 40000;
  uint64_t chaserShire = 0, chaserMinion = 0, thread = 0;
  std::string scpShire = "local";
  uint64_t bytesPerMinion = 8192;
  uint64_t scpShift = 16;
  double seconds = 2.0;
  uint64_t shireMask = 0xffffffff;
  double budget = -1;
  uint64_t seed = 1;
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
    results_ = rt_->mallocDevice(dev_, MH_MAX_HARTS * sizeof(MhResult));
    std::fprintf(stderr, "device ready in %.2f s\n", secondsSince(tOpen_));
  }

  ~Session() {
    for (auto* p : allocs_) {
      rt_->freeDevice(dev_, p);
    }
    rt_->freeDevice(dev_, results_);
    rt_->unloadCode(kernel_);
    rt_->destroyStream(stream_);
    std::fprintf(stderr, "device held for %.2f s\n", secondsSince(tOpen_));
  }

  std::byte* alloc(size_t bytes) {
    allocs_.push_back(rt_->mallocDevice(dev_, bytes));
    return allocs_.back();
  }
  void toDevice(const void* src, std::byte* dst, size_t bytes) {
    rt_->memcpyHostToDevice(stream_, reinterpret_cast<const std::byte*>(src), dst, bytes);
    rt_->waitForStream(stream_);
  }
  bool overBudget() const {
    return secondsSince(tOpen_) > o_.budget;
  }

  // Launches once and returns the per-hart results; wall time and epoch timestamps in the out-params.
  bool launch(MhArgs a, uint64_t mask, std::vector<MhResult>& res, double& wallS, long long& t0Ms, long long& t1Ms) {
    res.assign(MH_MAX_HARTS, MhResult{});
    rt_->memcpyHostToDevice(stream_, reinterpret_cast<const std::byte*>(res.data()), results_,
                            res.size() * sizeof(MhResult));
    rt_->waitForStream(stream_);
    a.shire_mask = mask;
    a.results = reinterpret_cast<uint64_t>(results_);
    rt::KernelLaunchOptions opts;
    opts.setShireMask(mask);
    opts.setBarrier(true);
    const int timeoutS = o_.sysemu ? 3600 : 6;
    t0Ms = epochMs();
    const auto t0 = Clock::now();
    rt_->kernelLaunch(stream_, kernel_, reinterpret_cast<const std::byte*>(&a), sizeof(a), opts);
    bool ok = rt_->waitForStream(stream_, std::chrono::seconds(timeoutS));
    wallS = secondsSince(t0);
    t1Ms = epochMs();
    if (!ok) {
      std::fprintf(stderr, "kernel did not finish within %d s, aborting the stream\n", timeoutS);
      rt_->waitForEvent(rt_->abortStream(stream_));
    }
    for (const auto& e : rt_->retrieveStreamErrors(stream_)) {
      std::fprintf(stderr, "stream error: %s\n", e.getString().c_str());
      ok = false;
    }
    rt_->memcpyDeviceToHost(stream_, results_, reinterpret_cast<std::byte*>(res.data()), res.size() * sizeof(MhResult));
    rt_->waitForStream(stream_);
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

uint64_t chaserHart(const Options& o) {
  return o.chaserShire * 64 + o.chaserMinion * 2 + o.thread;
}

int runChase(const Options& o, const std::vector<std::byte>& elf) {
  const auto sizes = parseSizes(o.sizes);
  std::vector<uint64_t> targets;  // scratchpad shire IDs
  if (o.where == "scp") {
    if (o.scpShire == "all") {
      for (uint64_t s = 0; s < 32; ++s) {
        targets.push_back(s);
      }
    } else {
      targets.push_back(o.scpShire == "local" ? MH_SCP_LOCAL : std::strtoull(o.scpShire.c_str(), nullptr, 0));
    }
  } else {
    targets.push_back(0);
  }
  // Chains are built before the device is opened.
  std::mt19937_64 rng(o.seed);
  std::vector<std::vector<uint32_t>> chains;
  uint64_t totalBytes = 0;
  for (uint64_t size : sizes) {
    const uint64_t lines = std::max<uint64_t>(size / 64, 4);
    if (o.where == "scp" && lines * 64 > MH_SCP_BYTES_PER_SHIRE) {
      std::fprintf(stderr, "scratchpad chains must fit in %llu bytes\n", (unsigned long long)MH_SCP_BYTES_PER_SHIRE);
      return 2;
    }
    chains.push_back(randomCycle(lines, rng));
    totalBytes += lines * 64;
  }

  Session dev(o, elf);
  // DRAM chains get disjoint regions, so no line of one size is still cached from another.
  std::byte* region = dev.alloc(o.where == "dram" ? totalBytes : 64);
  size_t maxLines = 0;
  for (const auto& c : chains) {
    maxLines = std::max(maxLines, c.size());
  }
  std::byte* dNext = o.where == "scp" ? dev.alloc(maxLines * 4 + 64) : nullptr;
  uint64_t offset = 0;
  int bad = 0;
  std::vector<MhResult> res;
  std::vector<uint64_t> image;
  for (uint64_t target : targets) {
    offset = 0;
    for (size_t i = 0; i < sizes.size(); ++i) {
      if (dev.overBudget()) {
        std::fprintf(stderr, "stopping: device-time budget of %.1f s used\n", o.budget);
        return bad ? 1 : 0;
      }
      const auto& next = chains[i];
      const uint64_t lines = next.size();
      MhArgs a{};
      a.mode = MH_CHASE;
      a.chaser_hart = chaserHart(o);
      // Two passes to fill the caches, capped at 2^19 steps: one pass over a 32 MB (L3-sized) chain.
      a.warm_steps = round8(std::min<uint64_t>(std::max<uint64_t>(2 * lines, 16384), 1u << 19));
      a.steps = round8(o.steps);
      if (o.where == "dram") {
        const uint64_t base = reinterpret_cast<uint64_t>(region) + offset;
        image.assign(lines * 8, 0);
        for (uint64_t l = 0; l < lines; ++l) {
          image[l * 8] = base + uint64_t(next[l]) * 64;
        }
        dev.toDevice(image.data(), region + offset, lines * 64);
        a.chain_base = base;
        offset += lines * 64;
      } else {
        dev.toDevice(next.data(), dNext, lines * 4);
        a.chain_base = MH_SCP_ADDR(target, 0);
        a.build_next = reinterpret_cast<uint64_t>(dNext);
        a.build_lines = lines;
      }
      double wall = 0;
      long long t0 = 0, t1 = 0;
      bool ok = dev.launch(a, 1ull << o.chaserShire, res, wall, t0, t1);
      const MhResult& r = res[a.chaser_hart];
      const uint64_t want = a.chain_base + walk(next, a.warm_steps + a.steps) * 64;
      ok = ok && r.magic == MH_MAGIC && r.value == want;
      bad += !ok;
      std::printf("MEMHIER {\"test\":\"chase\",\"where\":\"%s\",\"scp_shire\":%lld,\"size\":%llu,\"lines\":%llu,"
                  "\"chaser_shire\":%llu,\"chaser_minion\":%llu,\"thread\":%llu,\"warm_steps\":%llu,\"steps\":%llu,"
                  "\"cycles\":%llu,\"cycles_per_load\":%.3f,\"wall_s\":%.4f,\"t_start_ms\":%lld,\"t_end_ms\":%lld,"
                  "\"ok\":%s}\n",
                  o.where.c_str(), o.where == "scp" ? (long long)target : -1LL, (unsigned long long)(lines * 64),
                  (unsigned long long)lines, (unsigned long long)o.chaserShire, (unsigned long long)o.chaserMinion,
                  (unsigned long long)o.thread, (unsigned long long)a.warm_steps, (unsigned long long)a.steps,
                  (unsigned long long)r.cycles, double(r.cycles) / double(a.steps), wall, t0, t1,
                  ok ? "true" : "false");
      std::fflush(stdout);
    }
  }
  return bad ? 1 : 0;
}

// Stream, L1 and spin: calibrate on one short launch, then launch until --seconds of launches.
int runThroughput(const Options& o, const std::vector<std::byte>& elf) {
  const size_t shires = size_t(__builtin_popcountll(o.shireMask));
  const size_t minions = shires * 32;
  MhArgs a{};
  if (o.test == "stream") {
    if (o.bytesPerMinion == 0 || o.bytesPerMinion % 1024) {
      std::fprintf(stderr, "--bytes-per-minion must be a positive multiple of 1024\n");
      return 2;
    }
    a.mode = MH_STREAM_TL;
    a.bytes_per_minion = o.bytesPerMinion;
    a.minion_stride = o.bytesPerMinion;
    if (o.where == "scp-local" || o.where == "scp-remote") {
      if (32 * o.bytesPerMinion > MH_SCP_BYTES_PER_SHIRE) {
        std::fprintf(stderr, "32 minions x %llu B does not fit a 2.5 MB scratchpad\n",
                     (unsigned long long)o.bytesPerMinion);
        return 2;
      }
      a.scp_target = o.where == "scp-local" ? MH_SCP_LOCAL : o.scpShift % 32;
      if (a.scp_target == 0) {
        std::fprintf(stderr, "--scp-shift must not be a multiple of 32 (use scp-local)\n");
        return 2;
      }
    }
  } else if (o.test == "l1") {
    a.mode = MH_STREAM_L1;
  } else {
    a.mode = MH_SPIN;
  }

  Session dev(o, elf);
  if (a.mode == MH_STREAM_TL && a.scp_target == 0) {
    a.stream_base = reinterpret_cast<uint64_t>(dev.alloc(minions * o.bytesPerMinion));
  }
  if (a.mode == MH_STREAM_L1) {
    a.l1_buffers = reinterpret_cast<uint64_t>(dev.alloc(minions * 2 * 256));
  }
  std::vector<MhResult> res;
  const int harts = a.mode == MH_STREAM_TL ? 1 : 2;  // per minion
  auto one = [&](uint64_t iters, int launchNo) -> double {
    a.iters = iters;
    double wall = 0;
    long long t0 = 0, t1 = 0;
    bool ok = dev.launch(a, o.shireMask, res, wall, t0, t1);
    uint64_t bytes = 0, cmax = 0, reported = 0;
    double csum = 0;
    for (uint64_t h = 0; h < MH_MAX_HARTS; ++h) {
      const bool active = ((o.shireMask >> (h / 64)) & 1) && (harts == 2 || h % 2 == 0);
      if (!active) {
        continue;
      }
      const MhResult& r = res[h];
      if (r.magic != MH_MAGIC || r.hart != h) {
        ok = false;
        continue;
      }
      ++reported;
      bytes += r.bytes;
      cmax = std::max(cmax, r.cycles);
      csum += double(r.cycles);
    }
    ok = ok && reported == minions * harts;
    const double cmean = reported ? csum / double(reported) : 0;
    std::printf("MEMHIER {\"test\":\"%s\",\"where\":\"%s\",\"bytes_per_minion\":%llu,\"scp_target\":%llu,"
                "\"shire_mask\":\"0x%llx\",\"minions\":%zu,\"harts\":%llu,\"iters\":%llu,\"launch\":%d,"
                "\"t_start_ms\":%lld,\"t_end_ms\":%lld,\"wall_s\":%.6f,\"bytes\":%llu,\"cycles_max\":%llu,"
                "\"cycles_mean\":%.0f,\"gbps_wall\":%.3f,\"bytes_per_cycle_per_hart\":%.4f,\"implied_ghz\":%.4f,"
                "\"ok\":%s}\n",
                o.test.c_str(), a.mode == MH_STREAM_TL ? o.where.c_str() : "-", (unsigned long long)a.bytes_per_minion,
                (unsigned long long)a.scp_target, (unsigned long long)o.shireMask, minions,
                (unsigned long long)reported, (unsigned long long)iters, launchNo, t0, t1, wall,
                (unsigned long long)bytes, (unsigned long long)cmax, cmean, wall > 0 ? double(bytes) / wall / 1e9 : 0.0,
                cmean > 0 && reported ? double(bytes) / double(reported) / cmean : 0.0,
                wall > 0 ? double(cmax) / wall / 1e9 : 0.0, ok ? "true" : "false");
    std::fflush(stdout);
    if (!ok) {
      throw std::runtime_error("bad launch");
    }
    return wall;
  };
  // Calibration: aim for about 0.1 s, then size the real launches at about 0.6 s each.
  uint64_t iters = a.mode == MH_STREAM_TL ? std::max<uint64_t>(1, (4u << 20) / o.bytesPerMinion)
                                          : (a.mode == MH_STREAM_L1 ? 20000 : 200000);
  if (o.sysemu) {
    iters = std::max<uint64_t>(1, iters / 1000);
  }
  double wall = one(iters, -1);
  if (o.sysemu) {
    return 0;  // the simulator only checks that the kernel runs; its timing is meaningless
  }
  const double perIter = std::max(wall, 1e-4) / double(iters);
  iters = std::max<uint64_t>(1, uint64_t(0.6 / perIter));
  double spent = 0;
  for (int launchNo = 0; spent < o.seconds; ++launchNo) {
    if (dev.overBudget()) {
      std::fprintf(stderr, "stopping: device-time budget of %.1f s used\n", o.budget);
      break;
    }
    spent += one(iters, launchNo);
  }
  return 0;
}

}  // namespace

int main(int argc, char** argv) {
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
    else if (a == "--where") o.where = next();
    else if (a == "--sizes") o.sizes = next();
    else if (a == "--steps") o.steps = std::strtoull(next().c_str(), nullptr, 0);
    else if (a == "--chaser-shire") o.chaserShire = std::strtoull(next().c_str(), nullptr, 0);
    else if (a == "--chaser-minion") o.chaserMinion = std::strtoull(next().c_str(), nullptr, 0);
    else if (a == "--thread") o.thread = std::strtoull(next().c_str(), nullptr, 0);
    else if (a == "--scp-shire") o.scpShire = next();
    else if (a == "--bytes-per-minion") o.bytesPerMinion = parseSize(next());
    else if (a == "--scp-shift") o.scpShift = std::strtoull(next().c_str(), nullptr, 0);
    else if (a == "--seconds") o.seconds = std::atof(next().c_str());
    else if (a == "--shires") o.shireMask = std::strtoull(next().c_str(), nullptr, 0);
    else if (a == "--budget") o.budget = std::atof(next().c_str());
    else if (a == "--seed") o.seed = std::strtoull(next().c_str(), nullptr, 0);
    else if (a == "--kernel") o.kernel = next();
    else {
      std::fprintf(stderr, "unknown option %s (see the comment at the top of host/main.cpp)\n", a.c_str());
      return 2;
    }
  }
  if (o.budget < 0) {
    o.budget = o.sysemu ? 1e9 : 8.0;  // the simulator is private; a real card is shared
  }
  if (o.chaserShire >= 32 || o.chaserMinion >= 32 || o.thread > 1 || o.shireMask == 0 || (o.shireMask >> 32)) {
    std::fprintf(stderr, "bad shire / minion / thread / mask\n");
    return 2;
  }
  const auto elf = readFile(o.kernel);
  if (elf.empty()) {
    std::fprintf(stderr, "cannot read kernel %s\n", o.kernel.c_str());
    return 1;
  }
  try {
    if (o.test == "chase") {
      return runChase(o, elf);
    }
    if (o.test == "stream" || o.test == "l1" || o.test == "spin") {
      return runThroughput(o, elf);
    }
  } catch (const std::exception& e) {
    std::fprintf(stderr, "FAIL: %s\n", e.what());
    return 1;
  }
  std::fprintf(stderr, "--test must be chase, stream, l1 or spin\n");
  return 2;
}
