// Fine-grained memory probes on ET-SoC-1 (see ../README.md). Every launch prints one line
//   MEMPROBE {json}
//
//   memprobe_host [--sysemu] [--arena 1G] [--out-dir D] [--hart H] --program a.ops [--program b.ops ...]
//       Runs each op list (see memprobe_args.h and ../gen_ops.py) on one hart and writes its u32
//       results to D/<name>.u32. In an op, an address with bit 63 set is absolute; otherwise it is an
//       offset into the arena, which is aligned to its own size, so offset bits equal physical address bits.
//   memprobe_host [--sysemu] [--arena 1G] --loop --table t.tbl --level L [--shires MASK] [--seconds T]
//       Power loop: hart 0 of every minion loads and evicts its own addresses until --seconds of launches.
//       t.tbl (from ../gen_ops.py): u64 n_addrs, then n_addrs u64 arena offsets per minion of --shires.
//       With --stride S --lines N, minion m instead cycles through its first table address + j * S, j < N.
//   memprobe_host --info      prints the arena's device address and exits.
//
// The card is shared, so the device is open only while measuring, and a budget (--budget, default
// 8 s on silicon) stops further launches.
#include <g3log/loglevels.hpp>
#include <runtime/IRuntime.h>
#include <runtime/Types.h>
#include <device-layer/IDeviceLayer.h>
#include <sw-sysemu/SysEmuOptions.h>

#include <algorithm>
#include <chrono>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <limits>
#include <sstream>
#include <string>
#include <vector>

#include "Constants.h"
#include "memprobe_args.h"

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

struct Options {
  bool sysemu = false;
  std::string simArgs;
  std::vector<std::string> programs;
  bool loop = false;
  bool info = false;
  std::string outDir = ".";
  uint64_t arena = 1ull << 30;
  uint64_t hart = 0;
  std::string table;
  uint64_t stride = 0;
  uint64_t nLines = 0;
  uint64_t level = 3;
  uint64_t shireMask = 0xffffffff;
  double seconds = 2.0;
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
    status_ = rt_->mallocDevice(dev_, MP_MAX_HARTS * sizeof(MpStatus));
    std::fprintf(stderr, "device ready in %.2f s\n", secondsSince(tOpen_));
  }

  ~Session() {
    for (auto* p : allocs_) {
      rt_->freeDevice(dev_, p);
    }
    rt_->freeDevice(dev_, status_);
    rt_->unloadCode(kernel_);
    rt_->destroyStream(stream_);
    std::fprintf(stderr, "device held for %.2f s\n", secondsSince(tOpen_));
  }

  std::byte* alloc(size_t bytes, uint32_t alignment = 64) {
    allocs_.push_back(rt_->mallocDevice(dev_, bytes, alignment));
    return allocs_.back();
  }
  void toDevice(const void* src, std::byte* dst, size_t bytes) {
    rt_->memcpyHostToDevice(stream_, reinterpret_cast<const std::byte*>(src), dst, bytes);
    rt_->waitForStream(stream_);
  }
  void toHost(const std::byte* src, void* dst, size_t bytes) {
    rt_->memcpyDeviceToHost(stream_, src, reinterpret_cast<std::byte*>(dst), bytes);
    rt_->waitForStream(stream_);
  }
  bool overBudget() const {
    return secondsSince(tOpen_) > o_.budget;
  }

  // Launches once and returns the per-hart status; wall time and epoch timestamps in the out-params.
  bool launch(MpArgs a, uint64_t mask, std::vector<MpStatus>& st, double& wallS, long long& t0Ms, long long& t1Ms) {
    st.assign(MP_MAX_HARTS, MpStatus{});
    toDevice(st.data(), status_, st.size() * sizeof(MpStatus));
    a.shire_mask = mask;
    a.status = reinterpret_cast<uint64_t>(status_);
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
    toHost(status_, st.data(), st.size() * sizeof(MpStatus));
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
  std::byte* status_ = nullptr;
  std::vector<std::byte*> allocs_;
};

// The arena is aligned to its own size (up to 2 GB, the runtime's largest alignment).
std::byte* allocArena(Session& dev, uint64_t bytes) {
  const uint64_t align = std::min<uint64_t>(bytes, 1ull << 31);
  return dev.alloc(bytes, static_cast<uint32_t>(align));
}

int runPrograms(const Options& o, const std::vector<std::byte>& elf) {
  std::vector<std::vector<uint64_t>> progs;
  for (const auto& p : o.programs) {
    const auto raw = readFile(p);
    if (raw.empty() || raw.size() % 16) {
      std::fprintf(stderr, "bad op file %s\n", p.c_str());
      return 2;
    }
    std::vector<uint64_t> w(raw.size() / 8);
    std::memcpy(w.data(), raw.data(), raw.size());
    if (w.size() / 2 > MP_MAX_OPS) {
      std::fprintf(stderr, "%s has more than %llu ops\n", p.c_str(), (unsigned long long)MP_MAX_OPS);
      return 2;
    }
    progs.push_back(std::move(w));
  }

  Session dev(o, elf);
  std::byte* arena = allocArena(dev, o.arena);
  const uint64_t base = reinterpret_cast<uint64_t>(arena);
  size_t maxOps = 0;
  for (const auto& w : progs) {
    maxOps = std::max(maxOps, w.size() / 2);
  }
  std::byte* dOps = dev.alloc(maxOps * 16 + 64);
  std::byte* dRes = dev.alloc(MP_MAX_RESULTS * 4);
  int bad = 0;
  std::vector<MpStatus> st;
  for (size_t i = 0; i < progs.size(); ++i) {
    if (dev.overBudget()) {
      std::fprintf(stderr, "stopping: device-time budget of %.1f s used\n", o.budget);
      return 1;
    }
    auto w = progs[i];
    uint64_t timed = 0;
    for (size_t k = 0; k < w.size(); k += 2) {
      const uint64_t code = w[k] & 0xFF;
      timed += code == OP_TLOAD || code == OP_TEVICT || code == OP_STAMP || code == OP_TFENCE ||
               code == OP_TNOP || code == OP_MSREAD;
      timed += code == OP_RAW ? 4 : 0;
      timed += code == OP_TLOAD2;
      if (code != OP_DELAY && code != OP_FENCE && code != OP_TFENCE && code != OP_STAMP && code != OP_END &&
          code != OP_TNOP && code != OP_RAW && code != OP_MSREAD) {
        const uint64_t a = w[k + 1];
        if (a >> 63) {
          w[k + 1] = a & ~(1ull << 63);
        } else if (a >= o.arena) {
          std::fprintf(stderr, "%s: op %zu offset 0x%llx is outside the arena\n", o.programs[i].c_str(), k / 2,
                       (unsigned long long)a);
          return 2;
        } else {
          w[k + 1] = base + a;
        }
      }
    }
    dev.toDevice(w.data(), dOps, w.size() * 8);
    MpArgs a{};
    a.mode = MP_PROGRAM;
    a.hart = o.hart;
    a.ops = reinterpret_cast<uint64_t>(dOps);
    a.n_ops = w.size() / 2;
    a.results = reinterpret_cast<uint64_t>(dRes);
    double wall = 0;
    long long t0 = 0, t1 = 0;
    bool ok = dev.launch(a, 1ull << (o.hart / 64), st, wall, t0, t1);
    const MpStatus& s = st[o.hart];
    ok = ok && s.magic == MP_MAGIC && s.count == std::min<uint64_t>(timed, MP_MAX_RESULTS);
    std::vector<uint32_t> res(s.count);
    if (s.count) {
      dev.toHost(dRes, res.data(), res.size() * 4);
    }
    const std::string name = fs::path(o.programs[i]).stem().string();
    const std::string outPath = (fs::path(o.outDir) / (name + ".u32")).string();
    std::ofstream(outPath, std::ios::binary)
      .write(reinterpret_cast<const char*>(res.data()), static_cast<std::streamsize>(res.size() * 4));
    bad += !ok;
    std::printf("MEMPROBE {\"test\":\"program\",\"name\":\"%s\",\"hart\":%llu,\"arena_base\":\"0x%llx\","
                "\"ops\":%llu,\"results\":%llu,\"cycles\":%llu,\"wall_s\":%.4f,\"t_start_ms\":%lld,\"t_end_ms\":%lld,"
                "\"out\":\"%s\",\"ok\":%s}\n",
                name.c_str(), (unsigned long long)o.hart, (unsigned long long)base, (unsigned long long)(w.size() / 2),
                (unsigned long long)s.count, (unsigned long long)s.cycles, wall, t0, t1, outPath.c_str(),
                ok ? "true" : "false");
    std::fflush(stdout);
  }
  return bad ? 1 : 0;
}

int runLoop(const Options& o, const std::vector<std::byte>& elf) {
  const auto raw = readFile(o.table);
  const size_t minions = size_t(__builtin_popcountll(o.shireMask)) * 32;
  if (raw.size() < 8 || raw.size() % 8) {
    std::fprintf(stderr, "bad table %s\n", o.table.c_str());
    return 2;
  }
  std::vector<uint64_t> tbl(raw.size() / 8);
  std::memcpy(tbl.data(), raw.data(), raw.size());
  const uint64_t k = tbl[0];
  tbl.erase(tbl.begin());
  if (k == 0 || k > MP_LOOP_MAX_ADDRS || tbl.size() != minions * k) {
    std::fprintf(stderr, "table %s: %zu entries for %zu minions x %llu addresses\n", o.table.c_str(), tbl.size(),
                 minions, (unsigned long long)k);
    return 2;
  }
  for (uint64_t off : tbl) {
    if (off >= o.arena) {
      std::fprintf(stderr, "table offset 0x%llx is outside the arena\n", (unsigned long long)off);
      return 2;
    }
  }

  Session dev(o, elf);
  std::byte* arena = allocArena(dev, o.arena);
  const uint64_t base = reinterpret_cast<uint64_t>(arena);
  for (auto& off : tbl) {
    off += base;
  }
  std::byte* dTbl = dev.alloc(tbl.size() * 8);
  dev.toDevice(tbl.data(), dTbl, tbl.size() * 8);
  MpArgs a{};
  a.mode = MP_LOOP;
  a.table = reinterpret_cast<uint64_t>(dTbl);
  a.n_addrs = k;
  a.level = o.level;
  a.stride = o.stride;
  a.n_lines = o.nLines;
  if (a.stride && (o.nLines == 0 || o.nLines % 4)) {
    std::fprintf(stderr, "--lines must be a positive multiple of 4\n");
    return 2;
  }
  for (size_t m = 0; a.stride && m < minions; ++m) {
    if (tbl[m * k] - base + (o.nLines - 1) * o.stride + 64 > o.arena) {
      std::fprintf(stderr, "minion %zu: strided walk leaves the arena\n", m);
      return 2;
    }
  }
  const std::string name = fs::path(o.table).stem().string();
  std::vector<MpStatus> st;
  auto one = [&](uint64_t iters, int launchNo) -> double {
    a.iters = iters;
    double wall = 0;
    long long t0 = 0, t1 = 0;
    bool ok = dev.launch(a, o.shireMask, st, wall, t0, t1);
    uint64_t loads = 0, cmax = 0, reported = 0;
    double csum = 0;
    for (uint64_t h = 0; h < MP_MAX_HARTS; h += 2) {
      if (!((o.shireMask >> (h / 64)) & 1)) {
        continue;
      }
      const MpStatus& s = st[h];
      if (s.magic != MP_MAGIC || s.hart != h) {
        ok = false;
        continue;
      }
      ++reported;
      loads += s.count;
      cmax = std::max(cmax, s.cycles);
      csum += double(s.cycles);
    }
    ok = ok && reported == minions;
    const double cmean = reported ? csum / double(reported) : 0;
    std::printf("MEMPROBE {\"test\":\"loop\",\"name\":\"%s\",\"level\":%llu,\"n_addrs\":%llu,"
                "\"shire_mask\":\"0x%llx\",\"minions\":%zu,\"iters\":%llu,\"launch\":%d,\"arena_base\":\"0x%llx\","
                "\"t_start_ms\":%lld,\"t_end_ms\":%lld,\"wall_s\":%.6f,\"loads\":%llu,\"cycles_max\":%llu,"
                "\"cycles_mean\":%.0f,\"cycles_per_load\":%.3f,\"loads_per_s\":%.4e,\"ok\":%s}\n",
                name.c_str(), (unsigned long long)o.level, (unsigned long long)k,
                (unsigned long long)o.shireMask, minions, (unsigned long long)iters, launchNo,
                (unsigned long long)base, t0, t1, wall, (unsigned long long)loads, (unsigned long long)cmax, cmean,
                reported ? cmean * double(reported) / double(loads) : 0.0, wall > 0 ? double(loads) / wall : 0.0,
                ok ? "true" : "false");
    std::fflush(stdout);
    if (!ok) {
      throw std::runtime_error("bad launch");
    }
    return wall;
  };
  uint64_t iters = o.sysemu ? 4 : 2000;
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
    else if (a == "--program") o.programs.push_back(next());
    else if (a == "--loop") o.loop = true;
    else if (a == "--info") o.info = true;
    else if (a == "--out-dir") o.outDir = next();
    else if (a == "--arena") o.arena = parseSize(next());
    else if (a == "--hart") o.hart = std::strtoull(next().c_str(), nullptr, 0);
    else if (a == "--table") o.table = next();
    else if (a == "--stride") o.stride = parseSize(next());
    else if (a == "--lines") o.nLines = std::strtoull(next().c_str(), nullptr, 0);
    else if (a == "--level") o.level = std::strtoull(next().c_str(), nullptr, 0);
    else if (a == "--shires") o.shireMask = std::strtoull(next().c_str(), nullptr, 0);
    else if (a == "--seconds") o.seconds = std::atof(next().c_str());
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
  if (o.hart >= MP_MAX_HARTS || o.shireMask == 0 || (o.shireMask >> 32) || o.level > 4 ||
      (o.arena & (o.arena - 1))) {
    std::fprintf(stderr, "bad hart / mask / level, or an arena that is not a power of two\n");
    return 2;
  }
  const auto elf = readFile(o.kernel);
  if (elf.empty()) {
    std::fprintf(stderr, "cannot read kernel %s\n", o.kernel.c_str());
    return 1;
  }
  try {
    if (o.info) {
      Session dev(o, elf);
      std::printf("MEMPROBE {\"test\":\"info\",\"arena_base\":\"0x%llx\",\"arena\":%llu}\n",
                  (unsigned long long)reinterpret_cast<uint64_t>(allocArena(dev, o.arena)),
                  (unsigned long long)o.arena);
      return 0;
    }
    if (o.loop) {
      return runLoop(o, elf);
    }
    if (!o.programs.empty()) {
      return runPrograms(o, elf);
    }
  } catch (const std::exception& e) {
    std::fprintf(stderr, "FAIL: %s\n", e.what());
    return 1;
  }
  std::fprintf(stderr, "give --program, --loop or --info\n");
  return 2;
}
