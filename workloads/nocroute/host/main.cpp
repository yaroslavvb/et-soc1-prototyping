// nocroute host (EXPERIMENT nocr; ../README.md). Runs a plan, one launch per line, and prints one line per launch:
//   NOCR {json}
//
//   nocroute_host [--sysemu] [--budget S] [--kernel ELF] [--out-dir D] --plan PLAN
//
// PLAN lines (blank lines and # comments skipped):
//   mesh  <name> <calls.bin> <caller_mask> <slot_cycles> <lead_cycles> <gap_cycles>
//         R31: the callers take turns running the call list (u64 entries, nocroute_args.h; a multiple of 8 of them,
//         so each caller's results fill whole 64 B lines); the per-call results go to D/<name>.u32: 32 caller slots
//         x n_calls x {cycles, low 32 bits of the syscall's a0}, NR_BAD where nothing was written.
//   fill  <slice_bytes>
//         every minion of every compute shire tensor-stores the pattern over its read slice of its own scratchpad
//   read  <label> <window_cycles> <slice_bytes> <src>dst,...>
//         R32: each dst shire's 32 minions stream 1 KB tensor loads from the src shire's scratchpad
//   write <label> <window_cycles> <slice_bytes> <src>dst,...>
//         R32w: each src shire's 32 minions stream 512 B tensor stores into the dst shire's scratchpad
//
// Every NOCR line has "timed_out": true when the launch did not finish within 6 s and the host aborted its stream (a
// hart may be wedged: the block then writes its HALT marker).
// The card is shared: the device is open only while the plan runs, and --budget (default 8 s on silicon) stops
// further launches; the block wraps every run in timeout 10 and the card lock.
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
#include <limits>
#include <random>
#include <sstream>
#include <string>
#include <vector>

#include "Constants.h"
#include "nocroute_args.h"

// libetrt's thread-pool workers log at the custom levels VERBOSE_HIGH/MID/LOW, which only logging::LoggerDefault
// registers with g3log. Left unregistered, the first log call from several new workers inserts the level into g3log's
// level map from all of them at once and can corrupt it: aifoundry3's host crash about 1.08 s into 1 launch in 100
// (docs/findings/14-card-behaviour.md, "Traps"). Registering them first removes the race.
static void registerRuntimeLogLevels() {
  const LEVELS levels[] = {LEVELS(g3::kDebugValue - 100, "VERBOSE_HIGH"), LEVELS(g3::kDebugValue - 99, "VERBOSE_MID"),
                           LEVELS(g3::kDebugValue - 98, "VERBOSE_LOW")};
  for (const auto& l : levels) g3::only_change_at_initialization::addLogLevel(l, false);
}

namespace fs = std::filesystem;
using Clock = std::chrono::steady_clock;

namespace {

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

struct Options {
  bool sysemu = false;
  std::string simArgs;
  std::string plan;
  std::string outDir = ".";
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
      for (std::string arg; extra >> arg;) s.additionalOptions.push_back(arg);
      dl_ = dev::IDeviceLayer::createSysEmuDeviceLayer(s, 1);
    } else {
      dl_ = dev::IDeviceLayer::createPcieDeviceLayer(true, false);  // ops node only; never the management node
    }
    rt_ = rt::IRuntime::create(dl_);
    const auto devices = rt_->getDevices();
    if (devices.empty()) throw std::runtime_error("no ET devices found");
    dev_ = devices[0];
    stream_ = rt_->createStream(dev_);
    const auto load = rt_->loadCode(stream_, elf.data(), elf.size());
    rt_->waitForEvent(load.event_);
    kernel_ = load.kernel_;
    status_ = alloc(NR_MAX_HARTS * sizeof(NrResult));
    std::fprintf(stderr, "device ready in %.2f s\n", secondsSince(tOpen_));
  }
  ~Session() {
    for (auto* p : allocs_) rt_->freeDevice(dev_, p);
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
  double held() const { return secondsSince(tOpen_); }
  bool timedOut() const { return timedOut_; }
  uint64_t status() const { return reinterpret_cast<uint64_t>(status_); }

  // One launch on `mask`; the per-hart status comes back in st. Wall time and epoch stamps in the out-params.
  bool launch(NrArgs a, uint64_t mask, std::vector<NrResult>& st, double& wallS, long long& t0Ms, long long& t1Ms) {
    st.assign(NR_MAX_HARTS, NrResult{});
    toDevice(st.data(), status_, st.size() * sizeof(NrResult));
    a.shire_mask = mask;
    a.status = status();
    rt::KernelLaunchOptions opts;
    opts.setShireMask(mask);
    opts.setBarrier(true);
    const int timeoutS = o_.sysemu ? 3600 : 6;
    timedOut_ = false;
    t0Ms = epochMs();
    const auto t0 = Clock::now();
    rt_->kernelLaunch(stream_, kernel_, reinterpret_cast<const std::byte*>(&a), sizeof(a), opts);
    bool ok = rt_->waitForStream(stream_, std::chrono::seconds(timeoutS));
    wallS = secondsSince(t0);
    t1Ms = epochMs();
    if (!ok) {
      timedOut_ = true;
      std::fprintf(stderr, "kernel did not finish within %d s, aborting the stream\n", timeoutS);
      rt_->waitForEvent(rt_->abortStream(stream_));
    }
    for (const auto& e : rt_->retrieveStreamErrors(stream_)) {
      std::fprintf(stderr, "stream error: %s\n", e.getString().c_str());
      ok = false;
    }
    toHost(status_, st.data(), st.size() * sizeof(NrResult));
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
  bool timedOut_ = false;
};

struct Line {
  std::string op;
  std::vector<std::string> f;
};

std::vector<Line> readPlan(const std::string& path) {
  std::ifstream in(path);
  if (!in) throw std::runtime_error("cannot read plan " + path);
  std::vector<Line> out;
  for (std::string s; std::getline(in, s);) {
    const auto h = s.find('#');
    if (h != std::string::npos) s.resize(h);
    std::istringstream ss(s);
    Line l;
    if (!(ss >> l.op)) continue;
    for (std::string w; ss >> w;) l.f.push_back(w);
    out.push_back(l);
  }
  return out;
}

uint64_t num(const std::string& s) { return std::strtoull(s.c_str(), nullptr, 0); }

// "src>dst,..." -> the partner map (indexed by the participating shire) and the mask of participants.
// read: dst participates and reads src; write: src participates and writes dst.
bool parsePairs(const std::string& s, bool write, std::vector<uint32_t>& map, uint64_t& mask,
                std::vector<std::pair<int, int>>& pairs) {
  map.assign(32, NR_NONE);
  mask = 0;
  pairs.clear();
  std::stringstream ss(s);
  for (std::string item; std::getline(ss, item, ',');) {
    const auto c = item.find('>');
    if (c == std::string::npos) return false;
    const int src = std::atoi(item.substr(0, c).c_str()), dst = std::atoi(item.substr(c + 1).c_str());
    if (src < 0 || src >= 32 || dst < 0 || dst >= 32 || src == dst) return false;
    const int who = write ? src : dst, partner = write ? dst : src;
    if ((mask >> who) & 1) return false;  // a shire takes part once per launch
    map[who] = (uint32_t)partner;
    mask |= 1ull << who;
    pairs.push_back({src, dst});
  }
  return mask != 0;
}

int run(const Options& o, const std::vector<std::byte>& elf) {
  const auto plan = readPlan(o.plan);
  // Check the whole plan before opening the device.
  for (const auto& l : plan) {
    const size_t need = l.op == "mesh" ? 6 : l.op == "fill" ? 1 : (l.op == "read" || l.op == "write") ? 4 : 0;
    if (!need || l.f.size() != need) {
      std::fprintf(stderr, "bad plan line: %s (%zu fields)\n", l.op.c_str(), l.f.size());
      return 2;
    }
    if (l.op == "read" || l.op == "write") {
      std::vector<uint32_t> m;
      uint64_t mk;
      std::vector<std::pair<int, int>> p;
      const uint64_t sb = num(l.f[2]);
      if (!parsePairs(l.f[3], l.op == "write", m, mk, p) || sb == 0 || sb > NR_SLICE_MAX || (sb & 1023)) {
        std::fprintf(stderr, "bad %s line %s\n", l.op.c_str(), l.f[0].c_str());
        return 2;
      }
    }
    if (l.op == "mesh") {
      const auto raw = readFile(l.f[1]);
      const uint64_t cm = num(l.f[2]);
      if (raw.empty() || raw.size() % 64 || raw.size() / 8 > NR_MAX_CALLS || cm == 0 || (cm >> 32)) {
        std::fprintf(stderr, "bad mesh line %s\n", l.f[0].c_str());
        return 2;
      }
    }
  }

  Session dev(o, elf);
  std::vector<uint32_t> pat(128);
  std::mt19937 rng(20260928);
  for (auto& w : pat) w = rng();
  std::byte* dPat = dev.alloc(512);
  dev.toDevice(pat.data(), dPat, 512);
  std::byte* dMap = dev.alloc(32 * 4);
  std::byte* dCalls = dev.alloc(NR_MAX_CALLS * 8);
  std::byte* dOut = dev.alloc(32ull * NR_MAX_CALLS * 8);
  std::vector<NrResult> st;
  int bad = 0;
  for (const auto& l : plan) {
    if (!o.sysemu && dev.held() > o.budget) {
      std::printf("NOCR {\"test\":\"budget\",\"budget_s\":%.1f,\"held_s\":%.2f,\"ok\":false}\n", o.budget, dev.held());
      std::fflush(stdout);
      return 1;
    }
    NrArgs a{};
    double wall = 0;
    long long t0 = 0, t1 = 0;
    if (l.op == "mesh") {
      const auto raw = readFile(l.f[1]);
      const uint64_t n = raw.size() / 8, cm = num(l.f[2]);
      dev.toDevice(raw.data(), dCalls, raw.size());
      // every result slot starts as NR_BAD, so an entry no caller wrote can never pass for an earlier launch's value
      std::vector<uint32_t> res(32 * n * 2, NR_BAD);
      dev.toDevice(res.data(), dOut, res.size() * 4);
      a.mode = NR_MESH;
      a.calls = reinterpret_cast<uint64_t>(dCalls);
      a.n_calls = n;
      a.out = reinterpret_cast<uint64_t>(dOut);
      a.caller_mask = cm;
      a.window = num(l.f[3]);
      a.lead = num(l.f[4]);
      a.gap = num(l.f[5]);
      bool ok = dev.launch(a, cm, st, wall, t0, t1);
      const bool timedOut = dev.timedOut();
      dev.toHost(dOut, res.data(), res.size() * 4);
      const std::string outPath = (fs::path(o.outDir) / (l.f[0] + ".u32")).string();
      std::ofstream(outPath, std::ios::binary)
        .write(reinterpret_cast<const char*>(res.data()), static_cast<std::streamsize>(res.size() * 4));
      std::string cs;
      for (int s = 0; s < 32; ++s) {
        if (!((cm >> s) & 1)) continue;
        const NrResult& r = st[s * 64];
        // answered, made every call, refused none (PREREG: no refused entry), and no slot overrun
        const bool good =
          r.magic == NR_MAGIC && r.hart == (uint32_t)(s * 64) && r.bytes == n && r.iters == 0 && r.err == 0;
        ok = ok && good;
        char buf[256];
        std::snprintf(buf, sizeof buf,
                      "%s{\"shire\":%d,\"slot\":%llu,\"t_begin\":%llu,\"cycles\":%llu,\"refused\":%llu,\"err\":%llu,"
                      "\"ok\":%s}",
                      cs.empty() ? "" : ",", s, (unsigned long long)r.partner, (unsigned long long)r.t_begin,
                      (unsigned long long)r.cycles, (unsigned long long)r.iters, (unsigned long long)r.err,
                      good ? "true" : "false");
        cs += buf;
      }
      std::printf("NOCR {\"test\":\"mesh\",\"name\":\"%s\",\"calls_file\":\"%s\",\"n_calls\":%llu,"
                  "\"callers\":\"0x%llx\",\"slot\":%llu,\"lead\":%llu,\"gap\":%llu,\"out\":\"%s\",\"t_start_ms\":%lld,"
                  "\"t_end_ms\":%lld,\"wall_s\":%.4f,\"per_caller\":[%s],\"timed_out\":%s,\"ok\":%s}\n",
                  l.f[0].c_str(), l.f[1].c_str(), (unsigned long long)n, (unsigned long long)cm,
                  (unsigned long long)a.window, (unsigned long long)a.lead, (unsigned long long)a.gap,
                  outPath.c_str(), t0, t1, wall, cs.c_str(), timedOut ? "true" : "false", ok ? "true" : "false");
      bad += !ok;
    } else if (l.op == "fill") {
      a.mode = NR_FILL;
      a.pattern = reinterpret_cast<uint64_t>(dPat);
      a.slice_bytes = num(l.f[0]);
      bool ok = dev.launch(a, 0xFFFFFFFFull, st, wall, t0, t1);
      const bool timedOut = dev.timedOut();
      uint64_t done = 0;
      for (int h = 0; h < NR_MAX_HARTS; h += 2) done += st[h].magic == NR_MAGIC && st[h].err == 0;
      ok = ok && done == 1024;
      std::printf("NOCR {\"test\":\"fill\",\"slice_bytes\":%llu,\"minions\":%llu,\"t_start_ms\":%lld,"
                  "\"t_end_ms\":%lld,\"wall_s\":%.4f,\"timed_out\":%s,\"ok\":%s}\n",
                  (unsigned long long)a.slice_bytes, (unsigned long long)done, t0, t1, wall,
                  timedOut ? "true" : "false", ok ? "true" : "false");
      bad += !ok;
    } else {
      const bool write = l.op == "write";
      std::vector<uint32_t> map;
      uint64_t mask = 0;
      std::vector<std::pair<int, int>> pairs;
      parsePairs(l.f[3], write, map, mask, pairs);
      dev.toDevice(map.data(), dMap, 32 * 4);
      a.mode = write ? NR_WRITE : NR_READ;
      a.window = num(l.f[1]);
      a.slice_bytes = num(l.f[2]);
      a.map = reinterpret_cast<uint64_t>(dMap);
      a.pattern = reinterpret_cast<uint64_t>(dPat);
      bool ok = dev.launch(a, mask, st, wall, t0, t1);
      const bool timedOut = dev.timedOut();
      std::string fs_;
      for (const auto& [src, dst] : pairs) {
        const int who = write ? src : dst;
        uint64_t minions = 0, bytes = 0, errs = 0;
        double bpc = 0, cyc = 0;
        for (int m = 0; m < 32; ++m) {
          const NrResult& r = st[who * 64 + m * 2];
          if (r.magic != NR_MAGIC || r.hart != (uint32_t)(who * 64 + m * 2)) continue;
          if (r.err) { ++errs; continue; }
          ++minions;
          bytes += r.bytes;
          cyc += double(r.cycles);
          if (r.cycles) bpc += double(r.bytes) / double(r.cycles);
        }
        const bool good = minions == 32 && errs == 0;
        ok = ok && good;
        char buf[320];
        std::snprintf(buf, sizeof buf,
                      "%s{\"src\":%d,\"dst\":%d,\"minions\":%llu,\"errs\":%llu,\"bytes\":%llu,\"cyc_mean\":%.0f,"
                      "\"bpc\":%.5f}",
                      fs_.empty() ? "" : ",", src, dst, (unsigned long long)minions, (unsigned long long)errs,
                      (unsigned long long)bytes, minions ? cyc / double(minions) : 0.0, bpc);
        fs_ += buf;
      }
      std::printf("NOCR {\"test\":\"%s\",\"label\":\"%s\",\"window\":%llu,\"slice_bytes\":%llu,\"pairs\":\"%s\","
                  "\"mask\":\"0x%llx\",\"t_start_ms\":%lld,\"t_end_ms\":%lld,\"wall_s\":%.4f,\"flows\":[%s],"
                  "\"timed_out\":%s,\"ok\":%s}\n",
                  l.op.c_str(), l.f[0].c_str(), (unsigned long long)a.window, (unsigned long long)a.slice_bytes,
                  l.f[3].c_str(), (unsigned long long)mask, t0, t1, wall, fs_.c_str(), timedOut ? "true" : "false",
                  ok ? "true" : "false");
      bad += !ok;
    }
    std::fflush(stdout);
  }
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
    else if (a == "--plan") o.plan = next();
    else if (a == "--out-dir") o.outDir = next();
    else if (a == "--budget") o.budget = std::atof(next().c_str());
    else if (a == "--kernel") o.kernel = next();
    else {
      std::fprintf(stderr, "unknown option %s (see the comment at the top of host/main.cpp)\n", a.c_str());
      return 2;
    }
  }
  if (o.budget < 0) o.budget = o.sysemu ? 1e9 : 8.0;  // the simulator is private; a real card is shared
  if (o.plan.empty()) {
    std::fprintf(stderr, "give --plan\n");
    return 2;
  }
  const auto elf = readFile(o.kernel);
  if (elf.empty()) {
    std::fprintf(stderr, "cannot read kernel %s\n", o.kernel.c_str());
    return 1;
  }
  try {
    return run(o, elf);
  } catch (const std::exception& e) {
    std::fprintf(stderr, "FAIL: %s\n", e.what());
    return 1;
  }
}
