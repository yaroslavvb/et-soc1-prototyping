// x04clock host: launches one arm repeatedly until --seconds have passed, while the lab's power sampler runs.
// Every launch prints one line
//   X04 {json}
//
//   x04clock_host --arm tk|spin|wait|duty|stall|mix [--cls fsgnj_s|fadd_s|fadd_ps|fsgnj_ps] [--every P] [--cluster]
//                 [--mask 0xff] [--t1 off|same|wait] [--duty-pct D] [--period CYCLES] [--window CYCLES]
//                 [--seconds S] [--budget S] [--shires MASK] [--minions MASK] [--label NAME]
//                 [--seg-launches N  ARM-OPTIONS --then ARM-OPTIONS --then ...]
//
// The card is shared: each launch runs `window` cycles (0.4 s at 600 MHz by default) and the process stops after
// --seconds, or at --budget seconds (at most 9.5) after the device was opened, so nothing holds the device for long;
// a launch starts only if its wait fits inside the budget. One card only: the host refuses to open the device unless
// /dev/et<N>_ops (N = ET_DEVICES, 0 when unset) is the only ops node on the machine.
// A train (--seg-launches N with segments joined by --then) runs each segment's arm for N launches, in order, in
// one device process: A B B A gives a contrast without an idle baseline in which a linear drift cancels.
// Exit status: 0 every launch ok; 3 a launch returned but was not complete (a thread missed the start, or the
// credits did not balance: nothing is left blocked, the launch is not counted); 1 a launch did not finish, a stream
// error, or a bad option.
#include <g3log/loglevels.hpp>
#include <runtime/IRuntime.h>
#include <runtime/Types.h>
#include <device-layer/IDeviceLayer.h>

#include <algorithm>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <filesystem>
#include <fstream>
#include <map>
#include <sstream>
#include <string>
#include <vector>

#include "Constants.h"
#include "x04_args.h"

static_assert(sizeof(X04Result) == 128, "one result record per two cache lines");

// Register the runtime's custom log levels before any library starts a thread (the lab repo's enercat host does the
// same: without it, about one launch in a hundred crashed the host on one card).
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

const std::map<std::string, uint64_t> ARMS = {{"tk", X04_TK},       {"spin", X04_SPIN},   {"wait", X04_WAIT},
                                              {"duty", X04_DUTY},   {"stall", X04_STALL}, {"mix", X04_MIX}};
const std::map<std::string, uint64_t> CLASSES = {{"none", 0},
                                                 {"fsgnj_s", X04_CLS_FSGNJ_S},
                                                 {"fadd_s", X04_CLS_FADD_S},
                                                 {"fadd_ps", X04_CLS_FADD_PS},
                                                 {"fsgnj_ps", X04_CLS_FSGNJ_PS}};
const std::map<std::string, uint64_t> T1 = {{"off", X04_T1_OFF}, {"same", X04_T1_SAME}, {"wait", X04_T1_WAIT}};

struct Options {
  std::string arm = "spin", cls = "none", t1 = "same", label;
  uint64_t every = 1, mask = 0xff, shireMask = 0xffffffff, minionMask = 0xfffffffe, window = 240000000,
           period = 65536, dutyPct = 50, cluster = 0, hsLimit = 6000000, segLaunches = 0;
  double seconds = 3.0, budget = 9.5;
  std::string kernel = KERNEL_ELF;
};

// One card only. The device layer opens every ops node it finds, so before it is created the nodes are counted:
// exactly one /dev/et<N>_ops may exist, and it must be the card ET_DEVICES selects (0 when unset).
void checkOneCard() {
  const char* sel = std::getenv("ET_DEVICES");
  const std::string want = std::string("/dev/et") + (sel && *sel ? sel : "0") + "_ops";
  std::vector<std::string> nodes;
  std::error_code ec;
  for (const auto& e : fs::directory_iterator("/dev", ec)) {
    const std::string n = e.path().filename().string();
    if (n.size() > 6 && n.rfind("et", 0) == 0 && n.compare(n.size() - 4, 4, "_ops") == 0 &&
        std::all_of(n.begin() + 2, n.end() - 4, [](char c) { return c >= '0' && c <= '9'; }))
      nodes.push_back("/dev/" + n);
  }
  if (ec) throw std::runtime_error("cannot list /dev: " + ec.message());
  if (nodes.size() != 1 || nodes[0] != want)
    throw std::runtime_error("found " + std::to_string(nodes.size()) + " ops node(s); need exactly " + want +
                             " (the device layer opens every node it finds): not opening");
}

class Session {
public:
  Session(const Options& o, const std::vector<std::byte>& elf) : o_(o), tOpen_((checkOneCard(), Clock::now())) {
    dl_ = dev::IDeviceLayer::createPcieDeviceLayer(true, false);  // ops node only
    rt_ = rt::IRuntime::create(dl_);
    const auto devices = rt_->getDevices();
    if (devices.size() != 1) throw std::runtime_error("need exactly one ET device, found " + std::to_string(devices.size()));
    dev_ = devices[0];
    stream_ = rt_->createStream(dev_);
    const auto load = rt_->loadCode(stream_, elf.data(), elf.size());
    rt_->waitForEvent(load.event_);
    kernel_ = load.kernel_;
    results_ = rt_->mallocDevice(dev_, X04_MAX_HARTS * sizeof(X04Result));
    // The sync words carry each launch's epoch, so the buffer is zeroed once and never needs it again.
    sync_ = rt_->mallocDevice(dev_, 32 * X04_SYNC_PER_SHIRE);
    {
      std::vector<std::byte> z(32 * X04_SYNC_PER_SHIRE, std::byte{0});
      rt_->memcpyHostToDevice(stream_, z.data(), sync_, z.size());
      rt_->waitForStream(stream_);
    }
    epoch_ = (uint64_t(std::chrono::system_clock::now().time_since_epoch().count()) & 0xFFFFFFFFull) << 24;
    tReady_ = Clock::now();
    std::fprintf(stderr, "device ready in %.2f s\n", secondsSince(tOpen_));
  }
  ~Session() {
    for (auto* p : allocs_) rt_->freeDevice(dev_, p);
    rt_->freeDevice(dev_, results_);
    rt_->freeDevice(dev_, sync_);
    rt_->unloadCode(kernel_);
    rt_->destroyStream(stream_);
    std::fprintf(stderr, "device held for %.2f s\n", secondsSince(tOpen_));
  }
  std::byte* alloc(size_t bytes) {
    allocs_.push_back(rt_->mallocDevice(dev_, bytes));
    return allocs_.back();
  }
  void put(const void* src, std::byte* dst, size_t bytes) {
    rt_->memcpyHostToDevice(stream_, reinterpret_cast<const std::byte*>(src), dst, bytes);
    rt_->waitForStream(stream_);
  }
  // The budget counts from the device's opening.
  bool overBudget() const { return secondsSince(tOpen_) > o_.budget; }
  // A launch starts only if it can finish, timeout included, inside the budget.
  bool fits(double launchS) const { return secondsSince(tOpen_) + launchS + waitS(launchS) < o_.budget; }
  double waitS(double launchS) const { return std::ceil(launchS + 1.0); }

  long long t0Ms = 0, t1Ms = 0;  // epoch bounds of the last launch, for lining up with power samples

  bool launch(X04Args a, std::vector<X04Result>& res, double& wallS) {
    res.assign(X04_MAX_HARTS, X04Result{});
    rt_->memcpyHostToDevice(stream_, reinterpret_cast<const std::byte*>(res.data()), results_,
                            res.size() * sizeof(X04Result));
    rt_->waitForStream(stream_);
    a.results = reinterpret_cast<uint64_t>(results_);
    a.sync = reinterpret_cast<uint64_t>(sync_);
    a.epoch = ++epoch_;
    rt::KernelLaunchOptions opts;
    opts.setShireMask(a.shire_mask);
    opts.setBarrier(true);
    const double launchS = double(a.window) / 6.0e8;
    const auto timeoutS = std::chrono::seconds(static_cast<long long>(waitS(launchS)));
    t0Ms = epochMs();
    const auto t0 = Clock::now();
    rt_->kernelLaunch(stream_, kernel_, reinterpret_cast<const std::byte*>(&a), sizeof(a), opts);
    bool ok = rt_->waitForStream(stream_, timeoutS);
    wallS = secondsSince(t0);
    t1Ms = epochMs();
    if (!ok) {
      std::fprintf(stderr, "kernel did not finish within %lld s, aborting the stream\n", (long long)timeoutS.count());
      rt_->waitForEvent(rt_->abortStream(stream_));
    }
    for (const auto& e : rt_->retrieveStreamErrors(stream_)) {
      std::fprintf(stderr, "stream error: %s\n", e.getString().c_str());
      ok = false;
    }
    rt_->memcpyDeviceToHost(stream_, results_, reinterpret_cast<std::byte*>(res.data()),
                            res.size() * sizeof(X04Result));
    rt_->waitForStream(stream_);
    return ok;
  }

private:
  const Options& o_;
  Clock::time_point tOpen_, tReady_;
  std::shared_ptr<dev::IDeviceLayer> dl_;
  rt::RuntimePtr rt_;
  rt::DeviceId dev_{};
  rt::StreamId stream_{};
  rt::KernelId kernel_{};
  std::byte* results_ = nullptr;
  std::byte* sync_ = nullptr;
  uint64_t epoch_ = 0;
  std::vector<std::byte*> allocs_;
};

uint64_t lookup(const std::map<std::string, uint64_t>& m, const std::string& k, const char* what) {
  const auto it = m.find(k);
  if (it == m.end()) throw std::runtime_error(std::string("unknown ") + what + " " + k);
  return it->second;
}

// Run one configuration: launches until --seconds have passed (or maxLaunches, for a train's segment) or the budget
// is spent. Returns 0 (all ok), 3 (a launch returned incomplete: nothing blocked, not counted), 1 (a launch failed).
int run(const Options& o, Session& dev, int seg = -1, uint64_t maxLaunches = 0) {
  X04Args a{};
  a.arm = lookup(ARMS, o.arm, "--arm");
  a.cls = lookup(CLASSES, o.cls, "--cls");
  a.every = o.every;
  a.mask = o.mask & 0xff;
  a.t1 = lookup(T1, o.t1, "--t1");
  a.shire_mask = o.shireMask & 0xffffffffull;
  a.minion_mask = o.minionMask & 0xfffffffeull;
  a.period = o.period;
  a.cluster = o.cluster ? 1 : 0;
  a.hs_limit = o.hsLimit;
  if (a.arm == X04_MIX) {
    if (a.cls == 0) throw std::runtime_error("--arm mix needs --cls");
    if (o.every != 1 && o.every != 2 && o.every != 4 && o.every != 8 && o.every != 16 && o.every != 32 && o.every != 64)
      throw std::runtime_error("--every must be 1, 2, 4, 8, 16, 32 or 64");
    if (a.cluster && !(a.cls == X04_CLS_FADD_PS && (o.every == 8 || o.every == 16)))
      throw std::runtime_error("--cluster is built for --cls fadd_ps --every 8 or 16 only");
  }
  if (o.dutyPct > 100) throw std::runtime_error("--duty-pct must be 0..100 (100: awake all the time, no waits)");
  if (o.period < 1024) throw std::runtime_error("--period must be at least 1024 cycles");
  if (a.shire_mask == 0) throw std::runtime_error("--shires selects no shire");
  // Whole periods only, so the timekeeper sends exactly the credits every waiting thread takes.
  a.window = o.window / o.period * o.period;
  if (a.window == 0) throw std::runtime_error("--window shorter than one --period");
  a.duty_cycles = o.period * o.dutyPct / 100;

  std::vector<uint64_t> zeros(32, 0);
  std::byte* sbuf = dev.alloc(256);
  dev.put(zeros.data(), sbuf, 256);
  a.sources = reinterpret_cast<uint64_t>(sbuf);

  const bool dutyWaits = a.arm == X04_DUTY && a.duty_cycles < a.period;
  const bool t0Waits = a.arm == X04_WAIT || dutyWaits;
  const bool t1Waits = a.t1 == X04_T1_WAIT || (a.t1 == X04_T1_SAME && t0Waits);
  const uint64_t body = (a.arm == X04_SPIN || a.arm == X04_MIX) ? 512 : 64;   // slots per loop
  const double launchS = double(a.window) / 6.0e8;
  const auto tStart = Clock::now();
  int status = 0;
  uint64_t n = 0;
  while ((maxLaunches ? n < maxLaunches : secondsSince(tStart) < o.seconds) && !dev.overBudget() && dev.fits(launchS)) {
    ++n;
    std::vector<X04Result> res;
    double wallS = 0;
    const bool ok = dev.launch(a, res, wallS);
    uint64_t workers0 = 0, workers1 = 0, loops = 0, taken = 0, tkSent = 0, tkCyc = 0, cmax = 0, readers = 0;
    uint64_t ret0 = 0, ret1 = 0, icReq = 0, icMiss = 0, expected0 = 0, expected1 = 0, drained = 0, awake = 0;
    uint64_t late = 0, bailouts = 0, unsynced = 0, hsMax = 0, waiting = 0;
    double csum = 0;
    for (uint64_t h = 0; h < res.size(); ++h) {
      const auto& r = res[h];
      const uint64_t shire = h >> 6, minion = (h >> 1) & 31, thread = h & 1;
      if (!((a.shire_mask >> shire) & 1)) continue;
      const bool worker = minion != 0 && ((a.minion_mask >> minion) & 1);
      if (worker && a.arm != X04_TK) {
        if (thread == 0) { ++expected0; if (t0Waits) ++waiting; }
        if (thread == 1 && a.t1 != X04_T1_OFF) { ++expected1; if (t1Waits) ++waiting; }
      }
      if (r.magic != X04_MAGIC) continue;
      if (r.flags & X04_F_LATE) ++late;
      if (r.flags & X04_F_HS_BAILOUT) ++bailouts;
      if (r.flags & X04_F_CTR_UNSYNCED) ++unsynced;
      if ((minion & 7) == 0 && thread == 0) {
        ++readers; ret0 += r.retired0; ret1 += r.retired1; icReq += r.icache_req; icMiss += r.icache_miss;
      }
      if (minion == 0) {
        tkSent += r.periods; tkCyc = std::max<uint64_t>(tkCyc, r.cycles); hsMax = std::max<uint64_t>(hsMax, r.hs_cycles);
        continue;
      }
      if (thread == 0) ++workers0; else ++workers1;
      loops += r.loops; taken += r.periods; drained += r.drained; awake += r.awake;
      cmax = std::max<uint64_t>(cmax, r.cycles); csum += double(r.cycles);
    }
    const uint64_t nw = workers0 + workers1;
    const double slots = double(loops) * double(body);
    const bool complete = workers0 == expected0 && workers1 == expected1 && late == 0;
    const bool creditsOk = waiting == 0 || taken == (a.window / a.period) * waiting;
    std::printf("X04 {\"label\":\"%s\",\"seg\":%d,\"arm\":\"%s\",\"cls\":\"%s\",\"every\":%llu,\"cluster\":%llu,"
                "\"mask\":\"0x%llx\",\"t1\":\"%s\",\"duty_pct\":%llu,\"period\":%llu,\"window\":%llu,"
                "\"shire_mask\":\"0x%llx\",\"minion_mask\":\"0x%llx\",\"shires\":%d,"
                "\"workers_t0\":%llu,\"workers_t1\":%llu,\"slots\":%.0f,\"slots_per_cycle_per_hart\":%.4f,"
                "\"awake_cycles\":%llu,\"credits_taken\":%llu,\"credits_drained\":%llu,\"tk_credits_sent\":%llu,"
                "\"tk_cycles\":%llu,\"hs_cycles_max\":%llu,\"late\":%llu,\"hs_bailouts\":%llu,\"ctr_unsynced\":%llu,"
                "\"cycles_max\":%llu,\"cycles_mean\":%.0f,"
                "\"readers\":%llu,\"retired0\":%llu,\"retired1\":%llu,\"icache_req\":%llu,\"icache_miss\":%llu,"
                "\"wall_s\":%.4f,\"t_start_ms\":%lld,\"t_end_ms\":%lld,\"complete\":%s,\"credits_ok\":%s,\"ok\":%s}\n",
                o.label.c_str(), seg, o.arm.c_str(), o.cls.c_str(), (unsigned long long)o.every,
                (unsigned long long)a.cluster, (unsigned long long)a.mask, o.t1.c_str(), (unsigned long long)o.dutyPct,
                (unsigned long long)a.period, (unsigned long long)a.window, (unsigned long long)a.shire_mask,
                (unsigned long long)a.minion_mask, __builtin_popcountll(a.shire_mask), (unsigned long long)workers0,
                (unsigned long long)workers1, slots, (cmax && nw) ? slots / (csum > 0 ? csum : 1.0) : 0.0,
                (unsigned long long)awake, (unsigned long long)taken, (unsigned long long)drained,
                (unsigned long long)tkSent, (unsigned long long)tkCyc, (unsigned long long)hsMax,
                (unsigned long long)late, (unsigned long long)bailouts, (unsigned long long)unsynced,
                (unsigned long long)cmax, nw ? csum / double(nw) : 0.0, (unsigned long long)readers,
                (unsigned long long)ret0, (unsigned long long)ret1, (unsigned long long)icReq,
                (unsigned long long)icMiss, wallS, dev.t0Ms, dev.t1Ms, complete ? "true" : "false",
                creditsOk ? "true" : "false", (ok && complete && creditsOk) ? "true" : "false");
    std::fflush(stdout);
    if (!ok) return 1;                          // did not finish, or a stream error: stop at once
    if (!complete || !creditsOk) { status = 3; break; }
  }
  return status;
}

// Parse one configuration's options into o; returns 0, or 2 on a bad option.
int parseArgs(Options& o, const std::vector<std::string>& args) {
  for (size_t i = 0; i < args.size(); ++i) {
    const std::string& a = args[i];
    auto next = [&]() -> std::string {
      if (i + 1 >= args.size()) throw std::runtime_error(a + " needs a value");
      return args[++i];
    };
    if (a == "--arm") o.arm = next();
    else if (a == "--cls") o.cls = next();
    else if (a == "--every") o.every = std::strtoull(next().c_str(), nullptr, 0);
    else if (a == "--cluster") o.cluster = 1;
    else if (a == "--mask") o.mask = std::strtoull(next().c_str(), nullptr, 0);
    else if (a == "--t1") o.t1 = next();
    else if (a == "--duty-pct") o.dutyPct = std::strtoull(next().c_str(), nullptr, 0);
    else if (a == "--period") o.period = std::strtoull(next().c_str(), nullptr, 0);
    else if (a == "--window") o.window = std::strtoull(next().c_str(), nullptr, 0);
    else if (a == "--shires") o.shireMask = std::strtoull(next().c_str(), nullptr, 0);
    else if (a == "--minions") o.minionMask = std::strtoull(next().c_str(), nullptr, 0);
    else if (a == "--seconds") o.seconds = std::strtod(next().c_str(), nullptr);
    else if (a == "--budget") o.budget = std::strtod(next().c_str(), nullptr);
    else if (a == "--hs-limit") o.hsLimit = std::strtoull(next().c_str(), nullptr, 0);
    else if (a == "--seg-launches") o.segLaunches = std::strtoull(next().c_str(), nullptr, 0);
    else if (a == "--label") o.label = next();
    else if (a == "--kernel") o.kernel = next();
    else { std::fprintf(stderr, "unknown option %s\n", a.c_str()); return 2; }
  }
  return 0;
}

// Split a command line at "--then" into segments; each segment's options apply over the first segment's.
int parseSegments(std::vector<Options>& segs, const std::vector<std::string>& args, const Options& start = Options()) {
  std::vector<std::vector<std::string>> parts(1);
  for (const auto& w : args) {
    if (w == "--then") parts.emplace_back();
    else parts.back().push_back(w);
  }
  Options base = start;
  if (int rc = parseArgs(base, parts[0])) return rc;
  segs.push_back(base);
  for (size_t k = 1; k < parts.size(); ++k) {
    Options o = base;
    if (int rc = parseArgs(o, parts[k])) return rc;
    segs.push_back(o);
  }
  if (segs.size() > 1 && base.segLaunches == 0) throw std::runtime_error("--then needs --seg-launches N");
  return 0;
}

// One configuration, or a train of segments, on one opened device.
int runSegments(const std::vector<Options>& segs, Session& dev) {
  if (segs.size() == 1) return run(segs[0], dev);
  int status = 0;
  for (size_t k = 0; k < segs.size(); ++k) {
    const int rc = run(segs[k], dev, static_cast<int>(k), segs[0].segLaunches);
    if (rc == 1) return 1;
    if (rc) status = rc;
  }
  return status;
}

}  // namespace

int main(int argc, char** argv) {
  registerRuntimeLogLevels();  // first, before any library starts a thread
  try {
    std::vector<Options> segs;
    if (int rc = parseSegments(segs, std::vector<std::string>(argv + 1, argv + argc))) return rc;
    const Options& o = segs[0];
    // The lab's 10 s rule: the process runs under `timeout 10`, so the device budget may not be raised past 9.5 s.
    for (const auto& s : segs)
      if (!(s.budget > 0.0 && s.budget <= 9.5)) throw std::runtime_error("--budget must be in (0, 9.5] seconds");
    const auto elf = readFile(o.kernel);
    if (elf.empty()) throw std::runtime_error("cannot read kernel " + o.kernel);
    Session dev(o, elf);
    return runSegments(segs, dev);
  } catch (const std::exception& e) {
    std::fprintf(stderr, "FAIL: %s\n", e.what());
    return 1;
  }
}
