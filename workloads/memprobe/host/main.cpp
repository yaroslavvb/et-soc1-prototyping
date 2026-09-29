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
//   (MP_EXT builds, -DMEMPROBE_EXT=ON, e.g. build/memprobe2; tools/claims-v3/memp2:)
//   memprobe_host --tloop --stride S [--where scp|arena] [--tl-lines 16] [--span 32K] [--minions MASK]
//       [--shires MASK] [--spread same|bank|sub|onebank] [--iters N] [--reps R] [--name NAME]
//       TensorLoad bandwidth: hart 0 of every minion in --minions (per shire) streams --tl-lines-line TensorLoads,
//       S bytes apart inside a load, the next load 16 x S further on (--tl-lines x S), wrapping every --span bytes.
//       scp: minion m's region starts at 256 KB + m x (span + 1 KB) of its own shire's scratchpad; arena: an L2-resident
//       buffer of span bytes per minion in DRAM (each minion scalar-loads its span before the timed part, and the
//       first launch warms it too). --spread moves each minion's start by (m mod 4) x 64 B (bank), also by
//       ((m / 4) mod 4) x 256 B (sub), or by (m mod 4) x 256 B only (onebank: every minion in bank 0, on sub-bank
//       m mod 4); same = every minion starts in bank 0, sub-bank 0. One MEMPROBE line per launch, with per-shire
//       bytes per cycle; tensor_errors counts minions whose tensor_error gained a bit during the launch. A launch
//       that does not finish (or a stream error) ends the program at once with exit code 3: no further launch.
//   In an op program (MP_EXT), OP_TTLOAD times one TensorLoad and OP_TERR records tensor_error; a program with
//   OP_TTLOAD must run on an even hart (hart 0 of a minion). In MP_EXT builds a program launch that does not finish
//   (or a stream error) ends the run at once with exit code 3: the next program is not launched.
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
#ifdef MP_EXT
  bool tloop = false;
  std::string where = "scp";
  uint64_t tlLines = 16;
  uint64_t span = 32 * 1024;
  uint64_t minionMask = 0xffffffff;
  std::string spread = "same";
  uint64_t iters = 20000;
  int reps = 3;
  std::string name;
#endif
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
#ifdef MP_EXT
      timed += code == OP_TTLOAD || code == OP_TERR;
      if (code == OP_TTLOAD && (o.hart & 1)) {
        std::fprintf(stderr, "%s: OP_TTLOAD needs hart 0 of a minion (an even --hart)\n", o.programs[i].c_str());
        return 2;
      }
      if (code == OP_TERR) {
        continue;
      }
      if (code == OP_TTLOAD && !(w[k + 1] >> 63)) {
        const uint64_t arg = w[k] >> 8, lines = (arg & 0xF) + 1, stride = (arg >> 8) ? (arg >> 8) : 64;
        if (w[k + 1] + (lines - 1) * stride + 64 > o.arena) {
          std::fprintf(stderr, "%s: op %zu: the TensorLoad leaves the arena\n", o.programs[i].c_str(), k / 2);
          return 2;
        }
      }
#endif
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
#ifdef MP_EXT
    const bool launched = ok;
#endif
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
#ifdef MP_EXT
    if (!launched) {  // the kernel did not finish (or a stream error): launch nothing more on this card
      std::fprintf(stderr, "memprobe: launch failed (did not finish or stream error): no further launch\n");
      return 3;
    }
#endif
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


#ifdef MP_EXT
// TensorLoad bandwidth (MP_TLOOP): see the comment at the top. Every launch prints one MEMPROBE line with the
// per-shire bytes per shire-cycle (all streaming minions' bytes over the slowest of them) and the per-minion cycles
// per load; tensor_error from every minion (the status line's sink) must be 0.
int runTloop(const Options& o, const std::vector<std::byte>& elf) {
  const uint64_t stride = o.stride ? o.stride : 64;
  const uint64_t step = o.tlLines * stride;
  const uint64_t nsh = __builtin_popcountll(o.shireMask), nmin = __builtin_popcountll(o.minionMask & 0xffffffffull);
  const uint64_t scpOff = 256 * 1024, scpBytes = 0x280000;  // start 256 KB in (offset 0 faults for some ops)
  if (o.tlLines < 1 || o.tlLines > 16 || stride % 64 || stride == 0 || nmin == 0 || (o.minionMask >> 32) ||
      o.span % step || (o.tlLines - 1) * stride + 64 > o.span || o.iters == 0 || o.reps < 1 ||
      (o.where != "scp" && o.where != "arena") ||
      (o.spread != "same" && o.spread != "bank" && o.spread != "sub" && o.spread != "onebank")) {
    std::fprintf(stderr, "tloop: bad --tl-lines/--stride/--span/--minions/--iters/--reps/--where/--spread "
                         "(the span must be a multiple of tl-lines x stride and hold one load)\n");
    return 2;
  }
  auto spreadOff = [&](uint64_t m) -> uint64_t {
    if (o.spread == "same") return 0;
    if (o.spread == "onebank") return (m % 4) * 256;  // bank 0 (PA[7:6] = 0), sub-bank m mod 4 (PA[9:8])
    const uint64_t bank = (m % 4) * 64;
    return o.spread == "bank" ? bank : bank + ((m / 4) % 4) * 256;
  };
  const uint64_t slot = o.span + 1024;  // room for the spread offset
  if (o.where == "scp" && scpOff + 32 * slot > scpBytes) {
    std::fprintf(stderr, "tloop: 32 minions x %llu B does not fit the 2.5 MB scratchpad from 256 KB\n",
                 (unsigned long long)slot);
    return 2;
  }
  if (o.where == "arena" && nsh * 32 * slot > o.arena) {
    std::fprintf(stderr, "tloop: the arena is smaller than %llu minions x %llu B\n", (unsigned long long)(nsh * 32),
                 (unsigned long long)slot);
    return 2;
  }
  Session dev(o, elf);
  const uint64_t base = o.where == "arena" ? reinterpret_cast<uint64_t>(allocArena(dev, o.arena)) : 0;
  std::vector<uint64_t> tbl(nsh * 32);
  for (uint64_t si = 0; si < nsh; ++si) {
    for (uint64_t m = 0; m < 32; ++m) {
      tbl[si * 32 + m] = o.where == "scp" ? MP_SCP_ADDR(0x7F, scpOff + m * slot + spreadOff(m))
                                          : base + (si * 32 + m) * slot + spreadOff(m);
    }
  }
  std::byte* dTbl = dev.alloc(tbl.size() * 8);
  dev.toDevice(tbl.data(), dTbl, tbl.size() * 8);
  MpArgs a{};
  a.mode = MP_TLOOP;
  a.table = reinterpret_cast<uint64_t>(dTbl);
  a.n_addrs = 1;
  a.stride = stride;
  a.iters = o.sysemu ? std::min<uint64_t>(o.iters, 8) : o.iters;
  a.minion_mask = o.minionMask;
  a.tl_lines = o.tlLines;
  a.tl_step = step;
  a.tl_span = o.span;
  a.tl_flags = o.where == "arena" ? MP_TL_WARM : 0;
  const std::string name = o.name.empty() ? "tloop" : o.name;
  std::vector<MpStatus> st;
  int bad = 0;
  for (int launchNo = 0; launchNo < o.reps; ++launchNo) {
    if (dev.overBudget()) {
      std::fprintf(stderr, "stopping: device-time budget of %.1f s used\n", o.budget);
      return 1;
    }
    double wall = 0;
    long long t0 = 0, t1 = 0;
    bool ok = dev.launch(a, o.shireMask, st, wall, t0, t1);
    const bool launched = ok;
    uint64_t reported = 0, terr = 0, stale = 0, cmax = 0;
    double csum = 0;
    std::string bpc = "[", cpl = "[";
    for (uint64_t s = 0, si = 0; s < 32; ++s) {
      if (!((o.shireMask >> s) & 1)) continue;
      uint64_t smax = 0, n = 0;
      double scsum = 0;
      for (uint64_t m = 0; m < 32; ++m) {
        if (!((o.minionMask >> m) & 1)) continue;
        const MpStatus& x = st[s * 64 + m * 2];
        if (x.magic != MP_MAGIC || x.hart != s * 64 + m * 2 || x.count != a.iters) {
          ok = false;
          continue;
        }
        ++reported;
        ++n;
        const uint64_t e0 = x.sink >> 32, e1 = x.sink & 0xFFFFFFFFull;
        terr += (e1 & ~e0) != 0;  // a bit this launch added
        stale += e0 != 0;         // set before the first tensor op (an earlier kernel)
        smax = std::max<uint64_t>(smax, x.cycles);
        scsum += double(x.cycles);
      }
      cmax = std::max(cmax, smax);
      csum += scsum;
      const double bytes = double(n) * double(a.iters) * double(o.tlLines) * 64.0;
      char buf[64];
      std::snprintf(buf, sizeof buf, "%s%.3f", si ? "," : "", smax ? bytes / double(smax) : 0.0);
      bpc += buf;
      std::snprintf(buf, sizeof buf, "%s%.2f", si ? "," : "", n ? scsum / double(n) / double(a.iters) : 0.0);
      cpl += buf;
      ++si;
    }
    bpc += "]";
    cpl += "]";
    ok = ok && reported == nsh * nmin && terr == 0;
    bad += !ok;
    std::printf("MEMPROBE {\"test\":\"tloop\",\"name\":\"%s\",\"where\":\"%s\",\"stride\":%llu,\"tl_lines\":%llu,"
                "\"span\":%llu,\"spread\":\"%s\",\"minion_mask\":\"0x%llx\",\"shire_mask\":\"0x%llx\",\"minions\":%llu,"
                "\"iters\":%llu,\"launch\":%d,\"t_start_ms\":%lld,\"t_end_ms\":%lld,\"wall_s\":%.6f,\"cycles_max\":%llu,"
                "\"cycles_mean\":%.1f,\"tensor_errors\":%llu,\"tensor_error_stale\":%llu,\"launch_ok\":%s,"
                "\"bytes_per_shire_cycle\":%s,\"cycles_per_load\":%s,\"ok\":%s}\n",
                name.c_str(), o.where.c_str(), (unsigned long long)stride, (unsigned long long)o.tlLines,
                (unsigned long long)o.span, o.spread.c_str(), (unsigned long long)o.minionMask,
                (unsigned long long)o.shireMask, (unsigned long long)reported, (unsigned long long)a.iters, launchNo, t0,
                t1, wall, (unsigned long long)cmax, reported ? csum / double(reported) : 0.0,
                (unsigned long long)terr, (unsigned long long)stale, launched ? "true" : "false", bpc.c_str(),
                cpl.c_str(), ok ? "true" : "false");
    std::fflush(stdout);
    if (!launched) {  // the kernel did not finish (or a stream error): launch nothing more on this card
      std::fprintf(stderr, "tloop: launch failed (did not finish or stream error): no further launch\n");
      return 3;
    }
  }
  return bad ? 1 : 0;
}
#endif
}  // namespace

#ifdef MP_EXT
// The sha256 of the main.cpp and memprobe_args.h this binary was configured from (host/CMakeLists.txt passes it):
// tools/claims-v3/memp2/block.sh refuses a build/memprobe2 whose tag does not match the tree's sources.
#ifndef MP2_SRC_TAG
#define MP2_SRC_TAG "memp2-src:unknown"
#endif
extern "C" const char memp2_src_tag[];
extern "C" __attribute__((used)) const char memp2_src_tag[] = MP2_SRC_TAG;
#endif

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
#ifdef MP_EXT
    else if (a == "--tloop") o.tloop = true;
    else if (a == "--where") o.where = next();
    else if (a == "--tl-lines") o.tlLines = std::strtoull(next().c_str(), nullptr, 0);
    else if (a == "--span") o.span = parseSize(next());
    else if (a == "--minions") o.minionMask = std::strtoull(next().c_str(), nullptr, 0);
    else if (a == "--spread") o.spread = next();
    else if (a == "--iters") o.iters = std::strtoull(next().c_str(), nullptr, 0);
    else if (a == "--reps") o.reps = std::atoi(next().c_str());
    else if (a == "--name") o.name = next();
#endif
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
#ifdef MP_EXT
    if (o.tloop) {
      return runTloop(o, elf);
    }
#endif
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
