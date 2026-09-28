// pciebench: the host <-> card link and the launch path, timed through the runtime API (docs/reports/data/
// 2026-09-27-pcie/README.md has the schedule and the commands). One test per process; every result is a line
//   PCIE {json}
// and the process stops starting new work at --budget seconds after it began, so nothing holds the card for long.
//
//   pciebench_host --test info       the device's properties, DMA limits and PCIe link, no transfer
//   pciebench_host --test bw         memcpy bandwidth, --min 4K .. --max 256M in x2 steps, both directions, staged
//                                    and dma-only, the four variants interleaved rep by rep
//   pciebench_host --test lat        small-copy round trips (64 B, 4 KB) back to back and after random gaps,
//                                    pipelined 4 KB copies, an idle-stream wait
//   pciebench_host --test launch     an empty kernel: launch to completion, and back-to-back launches, 32 shires and 1
//   pciebench_host --test conc       2 x 64 MB per stream: H2D alone, D2H alone, both at once, two H2D streams, two
//                                    D2H streams; and with a barrier on every transfer (one command in flight per stream)
//   pciebench_host --test hostcopy   the host's own memcpy over the same sizes (no device): the staging copy's ceiling
//   options: --budget S (default 8.5), --seed N, --verify (bw: check the staged path's data once, 1 MB each way)
//
// Staged and dma-only. The runtime has no pinned-memory API: every copy of user memory goes through its CMA bounce
// buffer, which a thread pool fills (host to device) or drains (device to host) with a plain copy while the card's
// PCIe DMA engine moves the bounce buffer over the link. That is "staged", the path every program takes. The API lets
// the caller replace the bounce copy (the cmaCopyFunction argument of memcpyHostToDevice/memcpyDeviceToHost);
// "dma-only" passes one that copies nothing, so the same DMA commands run and the same bytes cross the link without the
// host copy: the analogue of a pinned buffer. Its bytes are whatever the bounce buffer held, so it is for timing only.
#include <g3log/loglevels.hpp>
#include <runtime/IRuntime.h>
#include <runtime/Types.h>
#include <device-layer/IDeviceLayer.h>

#include <algorithm>
#include <chrono>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <filesystem>
#include <fstream>
#include <random>
#include <sstream>
#include <string>
#include <thread>
#include <vector>

#include "Constants.h"

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

const Clock::time_point T_START = Clock::now();
double sinceStart() { return std::chrono::duration<double>(Clock::now() - T_START).count(); }
long long epochMs() {
  return std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::system_clock::now().time_since_epoch())
      .count();
}
long long nsBetween(Clock::time_point a, Clock::time_point b) {
  return std::chrono::duration_cast<std::chrono::nanoseconds>(b - a).count();
}
uint64_t parseSize(const std::string& s) {
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
std::string readText(const fs::path& p) {
  std::ifstream f(p);
  std::stringstream ss;
  ss << f.rdbuf();
  std::string s = ss.str();
  while (!s.empty() && (s.back() == '\n' || s.back() == ' ')) s.pop_back();
  return s;
}
std::string jsonStr(const std::string& s) {
  std::string o = "\"";
  for (char c : s) {
    if (c == '"' || c == '\\') { o += '\\'; o += c; }
    else if (c == '\n') o += "\\n";
    else if (static_cast<unsigned char>(c) < 0x20) o += ' ';
    else o += c;
  }
  return o + "\"";
}
std::string jsonArr(const std::vector<long long>& v) {
  std::string o = "[";
  for (size_t i = 0; i < v.size(); ++i) o += (i ? "," : "") + std::to_string(v[i]);
  return o + "]";
}
void emit(const std::string& body) {
  std::printf("PCIE {\"t_ms\":%lld,%s}\n", epochMs(), body.c_str());
  std::fflush(stdout);
}

struct Options {
  std::string test = "bw";
  double budget = 8.5;
  uint64_t minBytes = 4096, maxBytes = 256ull << 20, seed = 1;
  bool verify = false;
};

// The bounce copy the runtime does by default, and the one dma-only passes instead.
const rt::CmaCopyFunction COPY_NONE = [](const std::byte*, std::byte*, size_t, rt::CmaCopyType) {};
const rt::CmaCopyFunction COPY_STAGED = rt::defaultCmaCopyFunction;   // std::copy, the API's default

// Host buffers: page-aligned and touched before any timing, so no first-touch page fault lands inside a transfer.
struct HostBuf {
  std::byte* p = nullptr;
  size_t n = 0;
  explicit HostBuf(size_t bytes, uint64_t seed = 0) : n(bytes) {
    p = static_cast<std::byte*>(std::aligned_alloc(4096, (bytes + 4095) / 4096 * 4096));
    if (!p) throw std::runtime_error("host allocation failed");
    std::mt19937_64 rng(seed);
    auto* w = reinterpret_cast<uint64_t*>(p);
    for (size_t i = 0; i < bytes / 8; ++i) w[i] = rng();
  }
  ~HostBuf() { std::free(p); }
  HostBuf(const HostBuf&) = delete;
  HostBuf& operator=(const HostBuf&) = delete;
};

class Session {
public:
  explicit Session(const Options& o) : o_(o) {
    const auto t0 = Clock::now();
    dl_ = dev::IDeviceLayer::createPcieDeviceLayer(true, false);  // ops node only
    rt_ = rt::IRuntime::create(dl_);
    const auto devices = rt_->getDevices();
    if (devices.empty()) throw std::runtime_error("no ET devices found");
    dev_ = devices[0];
    openNs = nsBetween(t0, Clock::now());
  }
  ~Session() {
    for (auto* p : allocs_) rt_->freeDevice(dev_, p);
    for (auto s : streams_) rt_->destroyStream(s);
    std::fprintf(stderr, "device held for %.2f s\n", sinceStart());
  }
  rt::IRuntime& rt() { return *rt_; }
  rt::DeviceId dev() const { return dev_; }
  rt::StreamId stream() {
    streams_.push_back(rt_->createStream(dev_));
    return streams_.back();
  }
  std::byte* alloc(size_t bytes) {
    allocs_.push_back(rt_->mallocDevice(dev_, bytes));
    return allocs_.back();
  }
  bool overBudget() const { return sinceStart() > o_.budget; }
  // Wait for an event; on a timeout abort the stream and throw, so a stuck transfer never holds the card.
  void wait(rt::StreamId s, rt::EventId e) {
    if (!rt_->waitForEvent(e, std::chrono::seconds(5))) {
      rt_->waitForEvent(rt_->abortStream(s), std::chrono::seconds(2));
      throw std::runtime_error("an operation did not finish within 5 s");
    }
  }
  void waitStream(rt::StreamId s) {
    if (!rt_->waitForStream(s, std::chrono::seconds(5))) {
      rt_->waitForEvent(rt_->abortStream(s), std::chrono::seconds(2));
      throw std::runtime_error("a stream did not drain within 5 s");
    }
  }
  int errors(rt::StreamId s) {
    int n = 0;
    for (const auto& e : rt_->retrieveStreamErrors(s)) {
      std::fprintf(stderr, "stream error: %s\n", e.getString().c_str());
      ++n;
    }
    return n;
  }
  long long openNs = 0;

private:
  const Options& o_;
  std::shared_ptr<dev::IDeviceLayer> dl_;
  rt::RuntimePtr rt_;
  rt::DeviceId dev_{};
  std::vector<rt::StreamId> streams_;
  std::vector<std::byte*> allocs_;
};

// Every ET-SoC-1 on the bus: its PCIe address, negotiated link and the driver's CMA use (sysfs, world-readable).
std::string linkJson() {
  std::string o = "[";
  bool first = true;
  std::vector<fs::path> devs;
  for (const auto& e : fs::directory_iterator("/sys/bus/pci/devices")) devs.push_back(e.path());
  std::sort(devs.begin(), devs.end());
  for (const auto& d : devs) {
    if (readText(d / "vendor") != "0x1e0a") continue;
    o += std::string(first ? "" : ",") + "{\"bdf\":" + jsonStr(d.filename().string()) +
         ",\"speed\":" + jsonStr(readText(d / "current_link_speed")) +
         ",\"width\":" + jsonStr(readText(d / "current_link_width")) +
         ",\"max_speed\":" + jsonStr(readText(d / "max_link_speed")) +
         ",\"max_width\":" + jsonStr(readText(d / "max_link_width")) +
         ",\"cma_allocated\":" + jsonStr(readText(d / "mem_stats" / "cma_allocated")) + "}";
    first = false;
  }
  return o + "]";
}

void testInfo(Session& s) {
  const auto p = s.rt().getDeviceProperties(s.dev());
  const auto d = s.rt().getDmaInfo(s.dev());
  std::ostringstream o;
  o << "\"test\":\"info\",\"open_ns\":" << s.openNs << ",\"frequency_mhz\":" << p.frequency_
    << ",\"shires\":" << p.availableShires_ << ",\"memory_bw_mbs\":" << p.memoryBandwidth_
    << ",\"memory_bytes\":" << p.memorySize_ << ",\"tdp_w\":" << unsigned(p.tdp_)
    << ",\"form_factor\":" << (p.formFactor_ == rt::DeviceProperties::FormFactor::PCIE ? "\"PCIE\"" : "\"M2\"")
    << ",\"compute_shire_mask\":" << p.computeMinionShireMask_ << ",\"dma_max_elem_bytes\":" << d.maxElementSize_
    << ",\"dma_max_elem_count\":" << d.maxElementCount_ << ",\"link\":" << linkJson()
    << ",\"host_threads\":" << std::thread::hardware_concurrency();
  emit(o.str());
}

// One timed transfer: issue, wait, return the wall time in ns.
long long timedCopy(Session& s, rt::StreamId st, bool h2d, std::byte* host, std::byte* devp, size_t n, bool staged) {
  const auto& fn = staged ? COPY_STAGED : COPY_NONE;
  const auto t0 = Clock::now();
  const auto e = h2d ? s.rt().memcpyHostToDevice(st, host, devp, n, false, fn)
                     : s.rt().memcpyDeviceToHost(st, devp, host, n, false, fn);
  s.wait(st, e);
  return nsBetween(t0, Clock::now());
}

std::vector<uint64_t> sweepSizes(const Options& o) {
  std::vector<uint64_t> v;
  for (uint64_t n = o.minBytes; n <= o.maxBytes; n *= 2) v.push_back(n);
  return v;
}

void testBw(Session& s, const Options& o) {
  const auto st = s.stream();
  HostBuf src(o.maxBytes, o.seed), dst(o.maxBytes, o.seed + 1);
  std::byte* d0 = s.alloc(o.maxBytes);
  std::byte* d1 = s.alloc(o.maxBytes);
  if (o.verify) {   // the staged path delivers the bytes: 1 MB there and back
    const size_t n = std::min<uint64_t>(o.maxBytes, 1 << 20);
    timedCopy(s, st, true, src.p, d0, n, true);
    std::memset(dst.p, 0, n);
    timedCopy(s, st, false, dst.p, d0, n, true);
    emit(std::string("\"test\":\"verify\",\"bytes\":") + std::to_string(n) +
         ",\"equal\":" + (std::memcmp(src.p, dst.p, n) == 0 ? "true" : "false"));
  }
  // warm-up: one transfer of each variant at 1 MB (first use of the bounce buffer and the DMA channels)
  for (int v = 0; v < 4; ++v) timedCopy(s, st, v < 2, v < 2 ? src.p : dst.p, v < 2 ? d0 : d1, 1 << 20, v % 2 == 0);
  const char* DIR[2] = {"h2d", "d2h"};
  const char* CPY[2] = {"staged", "dma"};
  std::mt19937_64 rng(o.seed);
  for (uint64_t n : sweepSizes(o)) {
    if (s.overBudget()) { emit("\"test\":\"bw\",\"truncated_at\":" + std::to_string(n)); break; }
    // repeats: at least 3, at most 20, about 64 MB per variant for the mid sizes
    const int reps = static_cast<int>(std::clamp<uint64_t>((64ull << 20) / n, 3, 20));
    std::vector<long long> ns[4];
    long long warm[4];
    for (int v = 0; v < 4; ++v)
      warm[v] = timedCopy(s, st, v < 2, v < 2 ? src.p : dst.p, v < 2 ? d0 : d1, n, v % 2 == 0);
    // The four variants (h2d staged, h2d dma, d2h staged, d2h dma) in a new random order every rep: the runtime's
    // response receiver sleeps 50 us or 500 us between polls depending on a race with the next issue, and a fixed
    // order locks each variant to one of the two (seen in the pilot run of 27 Sep).
    int order[4] = {0, 1, 2, 3};
    for (int r = 0; r < reps; ++r) {
      std::shuffle(order, order + 4, rng);
      for (int v : order)
        ns[v].push_back(timedCopy(s, st, v < 2, v < 2 ? src.p : dst.p, v < 2 ? d0 : d1, n, v % 2 == 0));
    }
    const int err = s.errors(st);
    for (int v = 0; v < 4; ++v) {
      std::ostringstream b;
      b << "\"test\":\"bw\",\"dir\":\"" << DIR[v / 2] << "\",\"copy\":\"" << CPY[v % 2] << "\",\"bytes\":" << n
        << ",\"warm_ns\":" << warm[v] << ",\"ns\":" << jsonArr(ns[v]) << ",\"stream_errors\":" << err;
      emit(b.str());
    }
  }
}

void testLat(Session& s, const Options& o) {
  const auto st = s.stream();
  HostBuf hb(1 << 20, o.seed);
  std::byte* d0 = s.alloc(1 << 20);
  // an idle stream: the cost of asking whether nothing has finished
  {
    std::vector<long long> ns;
    for (int r = 0; r < 300; ++r) {
      const auto t0 = Clock::now();
      s.waitStream(st);
      ns.push_back(nsBetween(t0, Clock::now()));
    }
    emit("\"test\":\"lat\",\"kind\":\"idle_wait\",\"ns\":" + jsonArr(ns));
  }
  // round trips: issue one copy, wait for it; four variants interleaved, 64 B and 4 KB
  const char* DIR[2] = {"h2d", "d2h"};
  const char* CPY[2] = {"staged", "dma"};
  for (size_t n : {size_t(64), size_t(4096)}) {
    for (int v = 0; v < 4; ++v) timedCopy(s, st, v < 2, hb.p, d0, n, v % 2 == 0);   // warm-up
    std::vector<long long> ns[4];
    for (int r = 0; r < 250 && !s.overBudget(); ++r)
      for (int v = 0; v < 4; ++v) ns[v].push_back(timedCopy(s, st, v < 2, hb.p, d0, n, v % 2 == 0));
    const int err = s.errors(st);
    for (int v = 0; v < 4; ++v)
      emit(std::string("\"test\":\"lat\",\"kind\":\"round_trip\",\"dir\":\"") + DIR[v / 2] + "\",\"copy\":\"" +
           CPY[v % 2] + "\",\"bytes\":" + std::to_string(n) + ",\"ns\":" + jsonArr(ns[v]) +
           ",\"stream_errors\":" + std::to_string(err));
  }
  // sporadic: 4 KB round trips, each after a random idle gap of 0-1 ms (a program that copies now and then), so the
  // issue lands anywhere in the receiver's sleep; the four variants in a random order
  {
    std::mt19937_64 rng(o.seed + 7);
    std::uniform_int_distribution<int> gapUs(0, 1000);
    std::vector<long long> ns[4], gaps[4];
    int order[4] = {0, 1, 2, 3};
    for (int r = 0; r < 120 && !s.overBudget(); ++r) {
      std::shuffle(order, order + 4, rng);
      for (int v : order) {
        const int g = gapUs(rng);
        const auto until = Clock::now() + std::chrono::microseconds(g);
        while (Clock::now() < until) {}   // spin, so the gap has no timer slack
        gaps[v].push_back(g);
        ns[v].push_back(timedCopy(s, st, v < 2, hb.p, d0, 4096, v % 2 == 0));
      }
    }
    const int err = s.errors(st);
    for (int v = 0; v < 4; ++v)
      emit(std::string("\"test\":\"lat\",\"kind\":\"sporadic\",\"dir\":\"") + DIR[v / 2] + "\",\"copy\":\"" +
           CPY[v % 2] + "\",\"bytes\":4096,\"gap_us\":" + jsonArr(gaps[v]) + ",\"ns\":" + jsonArr(ns[v]) +
           ",\"stream_errors\":" + std::to_string(err));
  }
  // pipelined: 200 copies of 4 KB queued without barriers, then one wait; three trials per direction
  for (int v = 0; v < 4 && !s.overBudget(); ++v) {
    std::vector<long long> ns;
    const bool h2d = v < 2, staged = v % 2 == 0;
    for (int t = 0; t < 3; ++t) {
      const auto t0 = Clock::now();
      for (int k = 0; k < 200; ++k) {
        std::byte* dp = d0 + (k % 64) * 4096;
        std::byte* hp = hb.p + (k % 64) * 4096;
        if (h2d) s.rt().memcpyHostToDevice(st, hp, dp, 4096, false, staged ? COPY_STAGED : COPY_NONE);
        else s.rt().memcpyDeviceToHost(st, dp, hp, 4096, false, staged ? COPY_STAGED : COPY_NONE);
      }
      s.waitStream(st);
      ns.push_back(nsBetween(t0, Clock::now()));
    }
    emit(std::string("\"test\":\"lat\",\"kind\":\"pipelined\",\"dir\":\"") + DIR[v / 2] + "\",\"copy\":\"" +
         CPY[v % 2] + "\",\"bytes\":4096,\"count\":200,\"ns\":" + jsonArr(ns) +
         ",\"stream_errors\":" + std::to_string(s.errors(st)));
  }
}

std::vector<std::byte> readFile(const std::string& path) {
  std::ifstream file(path, std::ios::binary);
  if (!file) throw std::runtime_error("cannot read " + path);
  std::vector<std::byte> data(fs::file_size(path));
  file.read(reinterpret_cast<char*>(data.data()), static_cast<std::streamsize>(data.size()));
  return data;
}

void testLaunch(Session& s, const Options&) {
  const auto st = s.stream();
  const auto elf = readFile(KERNEL_ELF);
  auto t0 = Clock::now();
  const auto load = s.rt().loadCode(st, elf.data(), elf.size());
  s.wait(st, load.event_);
  const long long loadNs = nsBetween(t0, Clock::now());
  const uint64_t arg = 0;
  auto launch = [&](uint64_t mask) {
    rt::KernelLaunchOptions opts;
    opts.setShireMask(mask);
    opts.setBarrier(true);
    return s.rt().kernelLaunch(st, load.kernel_, reinterpret_cast<const std::byte*>(&arg), sizeof(arg), opts);
  };
  t0 = Clock::now();
  s.wait(st, launch(0xffffffffull));
  const long long firstNs = nsBetween(t0, Clock::now());
  emit("\"test\":\"launch\",\"kind\":\"load_and_first\",\"elf_bytes\":" + std::to_string(elf.size()) +
       ",\"load_ns\":" + std::to_string(loadNs) + ",\"first_ns\":" + std::to_string(firstNs) +
       ",\"stream_errors\":" + std::to_string(s.errors(st)));
  const uint64_t MASKS[2] = {0xffffffffull, 0x1ull};
  for (int round = 0; round < 2; ++round) {   // two rounds, so each mask is measured early and late in the process
    for (uint64_t mask : MASKS) {
      if (s.overBudget()) break;
      std::vector<long long> ns;
      for (int r = 0; r < 150 && !s.overBudget(); ++r) {
        t0 = Clock::now();
        s.wait(st, launch(mask));
        ns.push_back(nsBetween(t0, Clock::now()));
      }
      std::vector<long long> b2b;
      for (int t = 0; t < 3 && !s.overBudget(); ++t) {   // 100 launches queued, one wait
        t0 = Clock::now();
        for (int k = 0; k < 100; ++k) launch(mask);
        s.waitStream(st);
        b2b.push_back(nsBetween(t0, Clock::now()));
      }
      std::ostringstream b;
      b << "\"test\":\"launch\",\"kind\":\"empty\",\"round\":" << round << ",\"shire_mask\":" << mask
        << ",\"shires\":" << __builtin_popcountll(mask) << ",\"ns\":" << jsonArr(ns)
        << ",\"b2b_count\":100,\"b2b_ns\":" << jsonArr(b2b) << ",\"stream_errors\":" << s.errors(st);
      emit(b.str());
    }
  }
  s.rt().unloadCode(load.kernel_);
}

void testConc(Session& s, const Options& o) {
  const size_t n = 64ull << 20;
  const int k = 2;   // transfers per stream per trial
  rt::StreamId sts[4] = {s.stream(), s.stream(), s.stream(), s.stream()};
  HostBuf h0(n, o.seed), h1(n, o.seed + 1), h2(n, o.seed + 2), h3(n, o.seed + 3);
  std::byte* hs[4] = {h0.p, h1.p, h2.p, h3.p};
  std::byte* ds[4] = {s.alloc(n), s.alloc(n), s.alloc(n), s.alloc(n)};
  // a configuration: which of the four streams run, and in which direction (true: h2d)
  // ser: every transfer carries the barrier flag, so the device runs one command of that stream at a time (added
  // after the pilot run showed two H2D commands in flight moving less than one)
  struct Cfg { const char* name; std::vector<std::pair<int, bool>> legs; bool ser; };
  const std::vector<Cfg> CFGS = {{"h2d", {{0, true}}, false},
                                 {"d2h", {{1, false}}, false},
                                 {"h2d+d2h", {{0, true}, {1, false}}, false},
                                 {"2xh2d", {{0, true}, {2, true}}, false},
                                 {"2xd2h", {{1, false}, {3, false}}, false},
                                 {"h2d/ser", {{0, true}}, true},
                                 {"d2h/ser", {{1, false}}, true},
                                 {"h2d+d2h/ser", {{0, true}, {1, false}}, true}};
  for (int trial = 0; trial < 3; ++trial) {
    for (int staged = 0; staged < 2; ++staged) {
      for (const auto& c : CFGS) {
        if (s.overBudget()) { emit("\"test\":\"conc\",\"truncated\":true"); return; }
        std::vector<rt::EventId> last(c.legs.size());
        const auto t0 = Clock::now();
        for (int j = 0; j < k; ++j)
          for (size_t l = 0; l < c.legs.size(); ++l) {
            const int i = c.legs[l].first;
            last[l] = c.legs[l].second
                          ? s.rt().memcpyHostToDevice(sts[i], hs[i], ds[i], n, c.ser, staged ? COPY_STAGED : COPY_NONE)
                          : s.rt().memcpyDeviceToHost(sts[i], ds[i], hs[i], n, c.ser, staged ? COPY_STAGED : COPY_NONE);
          }
        // each leg's completion, in the order they finish (poll the events without blocking)
        std::vector<long long> doneNs(c.legs.size(), -1);
        size_t left = c.legs.size();
        while (left) {
          for (size_t l = 0; l < c.legs.size(); ++l)
            if (doneNs[l] < 0 && s.rt().waitForEvent(last[l], std::chrono::seconds(0))) {
              doneNs[l] = nsBetween(t0, Clock::now());
              --left;
            }
          if (nsBetween(t0, Clock::now()) > 5'000'000'000LL) throw std::runtime_error("conc trial over 5 s");
        }
        for (int i = 0; i < 4; ++i) s.waitStream(sts[i]);
        const long long wall = nsBetween(t0, Clock::now());
        int err = 0;
        for (int i = 0; i < 4; ++i) err += s.errors(sts[i]);
        std::ostringstream b;
        b << "\"test\":\"conc\",\"trial\":" << trial << ",\"copy\":\"" << (staged ? "staged" : "dma")
          << "\",\"cfg\":\"" << c.name << "\",\"legs\":" << c.legs.size() << ",\"bytes_per_leg\":" << n * k
          << ",\"leg_ns\":" << jsonArr(doneNs) << ",\"wall_ns\":" << wall << ",\"stream_errors\":" << err;
        emit(b.str());
      }
    }
  }
}

void testHostCopy(const Options& o) {
  HostBuf a(o.maxBytes, o.seed), b(o.maxBytes, o.seed + 1);
  for (uint64_t n : sweepSizes(o)) {
    if (sinceStart() > o.budget) break;
    const int reps = static_cast<int>(std::clamp<uint64_t>((64ull << 20) / n, 3, 20));
    std::memcpy(b.p, a.p, n);
    std::vector<long long> ns;
    for (int r = 0; r < reps; ++r) {
      const auto t0 = Clock::now();
      std::memcpy(b.p, a.p, n);
      ns.push_back(nsBetween(t0, Clock::now()));
      __asm__ __volatile__("" : : "r"(b.p) : "memory");
    }
    emit("\"test\":\"hostcopy\",\"bytes\":" + std::to_string(n) + ",\"ns\":" + jsonArr(ns));
  }
}

}  // namespace

int main(int argc, char** argv) {
  registerRuntimeLogLevels();  // first, before any library starts a thread
  Options o;
  for (int i = 1; i < argc; ++i) {
    const std::string a = argv[i];
    auto next = [&]() -> std::string {
      if (i + 1 >= argc) { std::fprintf(stderr, "%s needs a value\n", a.c_str()); std::exit(2); }
      return argv[++i];
    };
    if (a == "--test") o.test = next();
    else if (a == "--budget") o.budget = std::strtod(next().c_str(), nullptr);
    else if (a == "--min") o.minBytes = parseSize(next());
    else if (a == "--max") o.maxBytes = parseSize(next());
    else if (a == "--seed") o.seed = std::strtoull(next().c_str(), nullptr, 10);
    else if (a == "--verify") o.verify = true;
    else {
      std::fprintf(stderr, "usage: %s --test info|bw|lat|launch|conc|hostcopy [--budget S] [--min 4K] [--max 256M] "
                           "[--seed N] [--verify]\n", argv[0]);
      return 2;
    }
  }
  if (o.budget > 9.5) o.budget = 9.5;   // the lab's rule: a device process holds the card for at most 10 s
  try {
    if (o.test == "hostcopy") { testHostCopy(o); return 0; }
    Session s(o);
    emit("\"test\":\"open\",\"open_ns\":" + std::to_string(s.openNs) + ",\"link\":" + linkJson());
    if (o.test == "info") testInfo(s);
    else if (o.test == "bw") testBw(s, o);
    else if (o.test == "lat") testLat(s, o);
    else if (o.test == "launch") testLaunch(s, o);
    else if (o.test == "conc") testConc(s, o);
    else { std::fprintf(stderr, "unknown test %s\n", o.test.c_str()); return 2; }
    emit("\"test\":\"done\",\"which\":" + jsonStr(o.test) + ",\"elapsed_s\":" + std::to_string(sinceStart()));
  } catch (const std::exception& e) {
    emit("\"test\":\"error\",\"which\":" + jsonStr(o.test) + ",\"what\":" + jsonStr(e.what()));
    return 1;
  }
  return 0;
}
