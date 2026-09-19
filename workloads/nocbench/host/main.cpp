// On-chip communication probes on ET-SoC-1 (see ../README.md). Every measurement prints one line
//   NOCBENCH {json}
//
//   nocbench_host [--sysemu] --test pairs --pairs 0-1,0-8,0.0-5.0 [--mode pingpong|stream|fcc|flag]
//                 [--counts 1,2,4,...] [--funct move|iadd|imax|fadd] [--iters N] [--warmup N] [--concurrent]
//   nocbench_host [--sysemu] --test matrix [--mode pingpong|fcc|flag] [--minion M] [--shires MASK] [--concurrent]
//   nocbench_host [--sysemu] --test intra [--shire S] [--mode pingpong|stream|fcc|flag] [--count C]
//   nocbench_host [--sysemu] --test shift --rings pair|neigh|shire|xshire:K [--per-shire N] [--count C] [--seconds T]
//   nocbench_host [--sysemu] --test allreduce [--levels 1,2,3,4,5] [--shires MASK] [--count C] [--iters N]
//   nocbench_host [--sysemu] --test barrier --scope shire|chip [--per-shire N] [--shires MASK]
//   nocbench_host [--sysemu] --test spin [--per-shire N] [--shires MASK] [--seconds T]
//
// Minions are named by global ID (shire * 32 + minion) or as shire.minion. A pair a-b makes a the
// initiator: it sends first and its cycle count is the one reported.
//
// Every schedule is checked on the host before launch: a TensorSend or credit that nobody answers would
// hang the hart, and a hart that never returns can wedge a shared card. The hardware keeps one "ready"
// flag per minion for TensorSend/Recv, not one per partner (dcache_reduce.v, partner_ready_peer), so on
// silicon no minion may have two partners that could both be ready at once: schedules where a minion
// changes partner need a barrier between rounds. (The simulator tracks every partner separately and
// never shows the problem; a schedule that broke this rule hung the card.) Credit waits that cross
// shires poll FCCNB and give up after --poll-limit reads (--poll 0|1 forces either way). The device is
// open only while measuring, and a budget (--budget, default 8 s on silicon) stops further launches.
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
#include <map>
#include <numeric>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

#include "Constants.h"
#include "nocbench_args.h"

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

std::vector<std::string> split(const std::string& s, char sep) {
  std::vector<std::string> out;
  std::stringstream ss(s);
  for (std::string item; std::getline(ss, item, sep);) {
    if (!item.empty()) {
      out.push_back(item);
    }
  }
  return out;
}

uint64_t parseMinion(const std::string& s) {  // "37" or "1.5" (shire 1, minion 5)
  const auto dot = s.find('.');
  const uint64_t m = dot == std::string::npos
                       ? std::strtoull(s.c_str(), nullptr, 0)
                       : std::strtoull(s.substr(0, dot).c_str(), nullptr, 0) * 32 +
                           std::strtoull(s.substr(dot + 1).c_str(), nullptr, 0);
  if (m >= NB_MINIONS || (dot != std::string::npos && std::strtoull(s.substr(dot + 1).c_str(), nullptr, 0) >= 32)) {
    throw std::runtime_error("bad minion " + s);
  }
  return m;
}

std::vector<uint64_t> parseList(const std::string& s) {
  std::vector<uint64_t> out;
  for (const auto& item : split(s, ',')) {
    out.push_back(std::strtoull(item.c_str(), nullptr, 0));
  }
  return out;
}

const std::map<std::string, uint64_t> kFuncts = {{"fadd", NB_FADD}, {"fmax", NB_FMAX}, {"fmin", NB_FMIN},
                                                  {"iadd", NB_IADD}, {"imax", NB_IMAX}, {"imin", NB_IMIN},
                                                  {"move", NB_MOVE}};
const std::map<std::string, uint64_t> kModes = {{"pingpong", NB_PINGPONG}, {"stream", NB_STREAM},
                                                {"fcc", NB_FCC}, {"flag", NB_FLAG}};

std::string modeName(uint64_t mode) {
  switch (mode) {
  case NB_PINGPONG: return "pingpong";
  case NB_STREAM: return "stream";
  case NB_SHIFT: return "shift";
  case NB_ALLREDUCE: return "allreduce";
  case NB_FCC: return "fcc";
  case NB_FLAG: return "flag";
  case NB_BARRIER: return "barrier";
  case NB_SPIN: return "spin";
  default: return "?";
  }
}

struct Options {
  bool sysemu = false;
  std::string simArgs;
  std::string test;
  std::string mode = "pingpong";
  std::string pairs;
  std::string counts = "1";
  std::string funct = "move";
  std::string rings = "shire";
  std::string levels = "1,2,3,4,5";
  std::string scope = "shire";
  uint64_t count = 1;
  uint64_t iters = 0;  // 0: a default that suits the test
  uint64_t warmup = 20;
  bool concurrent = false;
  uint64_t minion = 0;
  uint64_t shire = 0;
  uint64_t perShire = 32;
  uint64_t shireMask = 0xffffffff;
  double seconds = 0;
  double budget = -1;
  int poll = -1;  // -1: poll only when credits cross shires
  uint64_t pollLimit = 1ull << 26;
  std::string kernel = KERNEL_ELF;
};

// One kernel launch: a schedule of rounds plus the scalar arguments.
struct Plan {
  uint64_t mode = 0;
  std::vector<std::vector<uint32_t>> rounds;  // rounds x NB_MINIONS entries
  bool roundBarrier = false;
  uint64_t count = 1, funct = NB_MOVE, iters = 1, warmup = 0, levels = 0, scope = 0;
  uint64_t shireMask = 1;  // NB_ALLREDUCE: shires that each run a tree
  bool poll = false;

  std::vector<uint32_t>& addRound() {
    rounds.emplace_back(NB_MINIONS, NB_IDLE);
    return rounds.back();
  }
};

void addPair(std::vector<uint32_t>& round, uint64_t a, uint64_t b) {
  if (a == b || round[a] != NB_IDLE || round[b] != NB_IDLE) {
    throw std::runtime_error("pair " + std::to_string(a) + "-" + std::to_string(b) + " clashes in its round");
  }
  round[a] = NB_ENTRY(b, 0, true);
  round[b] = NB_ENTRY(a, 0, false);
}

// Derived launch data: which minions take part, where their records go, which shires to launch.
struct Layout {
  std::vector<uint32_t> partMasks = std::vector<uint32_t>(32, 0);
  std::vector<uint32_t> slotBase = std::vector<uint32_t>(NB_MINIONS, 0);
  uint64_t slots = 0, shireMask = 0, partShires = 0;
};

Layout layoutOf(const Plan& p) {
  Layout l;
  std::vector<uint32_t> perMinion(NB_MINIONS, 0);
  if (p.mode == NB_ALLREDUCE) {
    for (uint64_t m = 0; m < NB_MINIONS; ++m) {
      perMinion[m] = p.levels <= 5 ? ((p.shireMask >> (m / 32)) & 1) && (m % 32) < (1ull << p.levels)
                                   : m < (1ull << p.levels);
    }
  } else {
    for (const auto& round : p.rounds) {
      for (uint64_t m = 0; m < NB_MINIONS; ++m) {
        perMinion[m] += round[m] != NB_IDLE;
      }
    }
  }
  for (uint64_t m = 0; m < NB_MINIONS; ++m) {
    l.slotBase[m] = uint32_t(l.slots);
    l.slots += perMinion[m];
    if (perMinion[m]) {
      l.partMasks[m / 32] |= 1u << (m % 32);
    }
  }
  for (uint64_t s = 0; s < 32; ++s) {
    if (l.partMasks[s]) {
      l.shireMask |= 1ull << s;
      ++l.partShires;
    }
  }
  return l;
}

// Credit waits poll (and can give up) when credits cross shires, unless --poll says otherwise.
void setPoll(Plan& p, const Options& o) {
  const bool credits = p.mode == NB_FCC || p.roundBarrier || (p.mode == NB_BARRIER && p.scope == NB_SCOPE_CHIP);
  p.poll = o.poll == 1 || (o.poll == -1 && credits && layoutOf(p).partShires > 1);
}

// Throws unless every rendezvous in the plan has a partner that will answer it.
void checkPlan(const Plan& p, bool sysemu) {
  if (p.iters == 0 || p.count == 0 || p.count > 127) {
    throw std::runtime_error("iters must be >= 1 and count 1..127");
  }
  if (p.mode == NB_ALLREDUCE) {
    if (p.levels < 1 || p.levels > 10) {
      throw std::runtime_error("allreduce levels must be 1..10 (level 10 would reach the master shire)");
    }
    return;
  }
  const bool tensor = p.mode == NB_PINGPONG || p.mode == NB_STREAM || p.mode == NB_SHIFT;
  if ((tensor || p.mode == NB_FCC) && !sysemu && !p.roundBarrier && p.rounds.size() > 1) {
    // Without barriers, rounds overlap: a later partner's ready (or credit) could arrive early and be taken
    // for the current partner's. Allow it only when no minion ever changes partner.
    std::map<uint64_t, uint64_t> partnerOf;
    for (const auto& e : p.rounds) {
      for (uint64_t m = 0; m < NB_MINIONS; ++m) {
        if (e[m] == NB_IDLE) {
          continue;
        }
        const uint64_t key = NB_PARTNER(e[m]) | (uint64_t(NB_PREV(e[m])) << 16);
        if (partnerOf.count(m) && partnerOf[m] != key) {
          throw std::runtime_error("minion " + std::to_string(m) + " changes partner between rounds without a "
                                   "barrier; on silicon a minion has one TensorSend ready flag, not one per partner, "
                                   "so this can deadlock (drop --concurrent)");
        }
        partnerOf[m] = key;
      }
    }
  }
  if (p.mode == NB_BARRIER && (p.rounds.size() != 1 || p.roundBarrier)) {
    throw std::runtime_error("barrier plans have one round and no round barrier");
  }
  for (size_t r = 0; r < p.rounds.size(); ++r) {
    const auto& e = p.rounds[r];
    for (uint64_t m = 0; m < NB_MINIONS; ++m) {
      if (e[m] == NB_IDLE || p.mode == NB_BARRIER || p.mode == NB_SPIN) {
        continue;
      }
      const uint64_t q = NB_PARTNER(e[m]);
      const std::string where = "round " + std::to_string(r) + " minion " + std::to_string(m);
      if (q >= NB_MINIONS || q == m || e[q] == NB_IDLE) {
        throw std::runtime_error(where + ": partner " + std::to_string(q) + " is not scheduled");
      }
      if (p.mode == NB_SHIFT) {
        const uint64_t prev = NB_PREV(e[m]);
        if (prev >= NB_MINIONS || e[prev] == NB_IDLE || NB_PREV(e[q]) != m || NB_PARTNER(e[prev]) != m) {
          throw std::runtime_error(where + ": ring links do not match");
        }
        if (NB_FIRST(e[q]) == NB_FIRST(e[m])) {
          throw std::runtime_error(where + ": ring neighbours must alternate send-first / receive-first");
        }
      } else if (NB_PARTNER(e[q]) != m || NB_FIRST(e[q]) == NB_FIRST(e[m])) {
        throw std::runtime_error(where + ": partner does not point back, or both would send first");
      }
    }
  }
}

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

  struct Outcome {
    bool ok = false;
    double wallS = 0;
    long long t0Ms = 0, t1Ms = 0;
    std::vector<NbResult> records, clocks;
    Layout layout;
    double ghz = 0;  // minion clock over the launch: the longest kernel's cycles over the launch's wall time
  };

  Outcome run(const Plan& p) {
    checkPlan(p, o_.sysemu);
    Outcome out;
    out.layout = layoutOf(p);
    const Layout& l = out.layout;
    const uint64_t shireMask = l.shireMask;
    std::vector<uint32_t> sched;
    for (const auto& r : p.rounds) {
      sched.insert(sched.end(), r.begin(), r.end());
    }
    if (sched.empty()) {
      sched.assign(NB_MINIONS, NB_IDLE);
    }
    const size_t nrec = std::max<uint64_t>(l.slots, 1);
    std::vector<NbResult> zeros(std::max<size_t>(nrec, NB_MINIONS));
    NbArgs a{};
    a.mode = p.mode;
    a.shire_mask = shireMask;
    a.results = put("results", zeros.data(), nrec * sizeof(NbResult));
    a.slot_base = put("slot_base", l.slotBase.data(), l.slotBase.size() * 4);
    a.clocks = put("clocks", zeros.data(), NB_MINIONS * sizeof(NbResult));
    a.schedule = put("schedule", sched.data(), sched.size() * 4);
    a.rounds = p.rounds.size();
    a.round_barrier = p.roundBarrier;
    a.part_masks = put("part_masks", l.partMasks.data(), 32 * 4);
    a.part_shires = l.partShires;
    a.counter = put("counter", zeros.data(), 64);
    if (p.mode == NB_FLAG) {
      std::vector<uint8_t> flagZeros(p.rounds.size() * NB_MINIONS * 64, 0);
      a.flags = put("flags", flagZeros.data(), flagZeros.size());
    }
    a.iters = p.iters;
    a.warmup = p.warmup;
    a.count = p.count;
    a.funct = p.funct;
    a.levels = p.levels;
    a.scope = p.scope;
    a.poll = p.poll;
    a.poll_limit = o_.pollLimit;

    rt::KernelLaunchOptions opts;
    opts.setShireMask(shireMask);
    opts.setBarrier(true);
    const int timeoutS = o_.sysemu ? 3600 : 6;
    out.t0Ms = epochMs();
    const auto t0 = Clock::now();
    rt_->kernelLaunch(stream_, kernel_, reinterpret_cast<const std::byte*>(&a), sizeof(a), opts);
    out.ok = rt_->waitForStream(stream_, std::chrono::seconds(timeoutS));
    out.wallS = secondsSince(t0);
    out.t1Ms = epochMs();
    if (!out.ok) {
      std::fprintf(stderr, "kernel did not finish within %d s, aborting the stream\n", timeoutS);
      rt_->waitForEvent(rt_->abortStream(stream_));
    }
    for (const auto& e : rt_->retrieveStreamErrors(stream_)) {
      std::fprintf(stderr, "stream error: %s\n", e.getString().c_str());
      out.ok = false;
    }
    out.records.resize(nrec);
    out.clocks.resize(NB_MINIONS);
    get("results", out.records.data(), nrec * sizeof(NbResult));
    get("clocks", out.clocks.data(), NB_MINIONS * sizeof(NbResult));
    uint64_t longest = 0;
    for (const auto& c : out.clocks) {
      if (c.magic == NB_MAGIC) {
        longest = std::max<uint64_t>(longest, c.t_exit - c.t_entry);
      }
    }
    out.ghz = out.wallS > 0 ? double(longest) / out.wallS / 1e9 : 0;
    return out;
  }

private:
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
    rt_->memcpyHostToDevice(stream_, reinterpret_cast<const std::byte*>(src), ptr, bytes);
    rt_->waitForStream(stream_);
    return reinterpret_cast<uint64_t>(ptr);
  }

  void get(const std::string& name, void* dst, size_t bytes) {
    rt_->memcpyDeviceToHost(stream_, buffers_.at(name).second, reinterpret_cast<std::byte*>(dst), bytes);
    rt_->waitForStream(stream_);
  }

  const Options& o_;
  Clock::time_point tOpen_;
  std::shared_ptr<dev::IDeviceLayer> dl_;
  rt::RuntimePtr rt_;
  rt::DeviceId dev_{};
  rt::StreamId stream_{};
  rt::KernelId kernel_{};
  std::map<std::string, std::pair<size_t, std::byte*>> buffers_;
};

// f0 lane 0 of a pair after `n` round trips (or one-way messages), as the hardware computes it.
std::pair<uint32_t, uint32_t> expectPair(uint64_t mode, uint64_t funct, uint64_t a, uint64_t b, uint64_t n) {
  uint32_t va = NB_PATTERN(a), vb = NB_PATTERN(b);
  auto combine = [&](uint32_t in, uint32_t mine) -> uint32_t {
    switch (funct) {
    case NB_MOVE: return in;
    case NB_IADD: return in + mine;
    case NB_IMAX: return uint32_t(std::max(int32_t(in), int32_t(mine)));
    case NB_IMIN: return uint32_t(std::min(int32_t(in), int32_t(mine)));
    default: return 0;
    }
  };
  for (uint64_t i = 0; i < n; ++i) {
    vb = combine(va, vb);
    if (mode == NB_PINGPONG) {
      va = combine(vb, va);
    }
  }
  return {va, vb};
}

bool checkable(uint64_t funct) {
  return funct == NB_MOVE || funct == NB_IADD || funct == NB_IMAX || funct == NB_IMIN;
}

// Records of one outcome by (round, minion).
std::map<std::pair<uint32_t, uint32_t>, NbResult> byRound(const Session::Outcome& out) {
  std::map<std::pair<uint32_t, uint32_t>, NbResult> m;
  for (const auto& r : out.records) {
    if (r.magic == NB_MAGIC) {
      m[{r.round, r.minion}] = r;
    }
  }
  return m;
}

void printLaunch(const Plan& p, const Session::Outcome& out, const char* test) {
  std::printf("NOCBENCH {\"test\":\"%s\",\"kind\":\"launch\",\"mode\":\"%s\",\"rounds\":%zu,\"shire_mask\":\"0x%llx\","
              "\"wall_s\":%.4f,\"t_start_ms\":%lld,\"t_end_ms\":%lld,\"ghz\":%.4f,\"ok\":%s}\n",
              test, modeName(p.mode).c_str(), p.rounds.size(), (unsigned long long)out.layout.shireMask, out.wallS,
              out.t0Ms, out.t1Ms, out.ghz, out.ok ? "true" : "false");
}

// Pair modes: one line per pair, from the initiator's record (and the partner's for the data check).
int reportPairs(const char* test, const Plan& p, const Session::Outcome& out) {
  printLaunch(p, out, test);
  const auto recs = byRound(out);
  int bad = !out.ok;
  for (size_t r = 0; r < p.rounds.size(); ++r) {
    for (uint64_t a = 0; a < NB_MINIONS; ++a) {
      const uint32_t e = p.rounds[r][a];
      if (e == NB_IDLE || !NB_FIRST(e)) {
        continue;
      }
      const uint64_t b = NB_PARTNER(e);
      const auto ia = recs.find({uint32_t(r), uint32_t(a)});
      const auto ib = recs.find({uint32_t(r), uint32_t(b)});
      bool ok = out.ok && ia != recs.end() && ib != recs.end() && ia->second.value1 != NB_TIMEOUT &&
                ib->second.value1 != NB_TIMEOUT;
      uint64_t cyc = ok ? ia->second.cycles : 0;
      if (ok && (p.mode == NB_PINGPONG || p.mode == NB_STREAM) && checkable(p.funct)) {
        const auto [va, vb] = expectPair(p.mode, p.funct, a, b, p.warmup + p.iters);
        ok = ia->second.value1 == va && ib->second.value1 == vb;
        if (!ok) {
          std::fprintf(stderr, "round %zu %llu-%llu: f0 = 0x%08x / 0x%08x, want 0x%08x / 0x%08x\n", r,
                       (unsigned long long)a, (unsigned long long)b, ia->second.value1, ib->second.value1, va, vb);
        }
      }
      if (ok && p.mode == NB_FLAG) {
        ok = ia->second.value1 == p.warmup + p.iters && ib->second.value1 == p.warmup + p.iters;
      }
      if (ok && p.mode == NB_STREAM) {
        cyc = std::max(cyc, ib->second.cycles);  // the receiver sees the last message arrive
      }
      bad += !ok;
      std::printf("NOCBENCH {\"test\":\"%s\",\"kind\":\"pair\",\"mode\":\"%s\",\"round\":%zu,\"a\":%llu,\"b\":%llu,"
                  "\"a_shire\":%llu,\"a_minion\":%llu,\"b_shire\":%llu,\"b_minion\":%llu,\"count\":%llu,"
                  "\"funct\":%llu,\"iters\":%llu,\"cycles\":%llu,\"cycles_per_iter\":%.3f,\"b_cycles\":%llu,"
                  "\"ghz\":%.4f,\"concurrent\":%s,\"poll\":%s,\"ok\":%s}\n",
                  test, modeName(p.mode).c_str(), r, (unsigned long long)a, (unsigned long long)b,
                  (unsigned long long)(a / 32), (unsigned long long)(a % 32), (unsigned long long)(b / 32),
                  (unsigned long long)(b % 32), (unsigned long long)p.count, (unsigned long long)p.funct,
                  (unsigned long long)p.iters, (unsigned long long)cyc, double(cyc) / double(p.iters),
                  (unsigned long long)(ok ? ib->second.cycles : 0), out.ghz, p.roundBarrier ? "false" : "true",
                  p.poll ? "true" : "false", ok ? "true" : "false");
    }
  }
  std::fflush(stdout);
  return bad;
}

int testPairs(const Options& o, Session& dev) {
  std::vector<std::pair<uint64_t, uint64_t>> pairs;
  for (const auto& item : split(o.pairs, ',')) {
    const auto parts = split(item, '-');
    if (parts.size() != 2) {
      throw std::runtime_error("--pairs wants a-b,c-d,...");
    }
    pairs.emplace_back(parseMinion(parts[0]), parseMinion(parts[1]));
  }
  if (pairs.empty() || !kModes.count(o.mode)) {
    throw std::runtime_error("--test pairs needs --pairs and a --mode of pingpong, stream, fcc or flag");
  }
  int bad = 0;
  for (uint64_t count : parseList(o.counts)) {
    Plan p;
    p.mode = kModes.at(o.mode);
    p.count = count;
    p.funct = kFuncts.at(o.funct);
    p.iters = o.iters ? o.iters : 2000;
    p.warmup = o.warmup;
    // Isolated (default): one pair per round with a chip-wide barrier in between, so pairs never overlap.
    p.roundBarrier = !o.concurrent;
    if (o.concurrent) {
      auto* round = &p.addRound();
      for (const auto& [a, b] : pairs) {
        if ((*round)[a] != NB_IDLE || (*round)[b] != NB_IDLE) {
          round = &p.addRound();
        }
        addPair(*round, a, b);
      }
    } else {
      for (const auto& [a, b] : pairs) {
        addPair(p.addRound(), a, b);
      }
    }
    if (dev.overBudget()) {
      std::fprintf(stderr, "stopping: device-time budget of %.1f s used\n", o.budget);
      break;
    }
    setPoll(p, o);
    bad += reportPairs("pairs", p, dev.run(p));
  }
  return bad ? 1 : 0;
}

// Every pair of shires in --shires, between minion --minion of each. Isolated: one pair per round,
// with barriers. Concurrent: the circle method, so every round pairs up all shires at once.
int testMatrix(const Options& o, Session& dev) {
  std::vector<uint64_t> shires;
  for (uint64_t s = 0; s < 32; ++s) {
    if ((o.shireMask >> s) & 1) {
      shires.push_back(s);
    }
  }
  if (shires.size() < 2 || !kModes.count(o.mode) || o.mode == "stream") {
    throw std::runtime_error("--test matrix needs two or more shires and --mode pingpong, fcc or flag");
  }
  Plan p;
  p.mode = kModes.at(o.mode);
  p.count = o.count;
  p.funct = kFuncts.at(o.funct);
  p.iters = o.iters ? o.iters : 200;
  p.warmup = o.warmup;
  p.roundBarrier = !o.concurrent;
  auto m = [&](uint64_t s) { return s * 32 + o.minion; };
  if (o.concurrent) {
    std::vector<int64_t> ring(shires.begin(), shires.end());
    if (ring.size() % 2) {
      ring.push_back(-1);  // bye
    }
    const size_t n = ring.size();
    for (size_t r = 0; r + 1 < n; ++r) {
      auto& round = p.addRound();
      for (size_t i = 0; i < n / 2; ++i) {
        const int64_t x = ring[i], y = ring[n - 1 - i];
        if (x >= 0 && y >= 0) {
          addPair(round, m(uint64_t(std::min(x, y))), m(uint64_t(std::max(x, y))));
        }
      }
      std::rotate(ring.begin() + 1, ring.end() - 1, ring.end());
    }
  } else {
    for (size_t i = 0; i < shires.size(); ++i) {
      for (size_t j = i + 1; j < shires.size(); ++j) {
        addPair(p.addRound(), m(shires[i]), m(shires[j]));
      }
    }
  }
  setPoll(p, o);
  return reportPairs("matrix", p, dev.run(p)) ? 1 : 0;
}

// Every pair of minions inside shire --shire, one pair per round with a barrier in between (the barrier's
// credits stay inside the shire).
int testIntra(const Options& o, Session& dev) {
  if (!kModes.count(o.mode)) {
    throw std::runtime_error("--test intra needs --mode pingpong, stream, fcc or flag");
  }
  Plan p;
  p.mode = kModes.at(o.mode);
  p.count = o.count;
  p.funct = kFuncts.at(o.funct);
  p.iters = o.iters ? o.iters : 200;
  p.warmup = o.warmup;
  p.roundBarrier = true;
  for (uint64_t i = 0; i < 32; ++i) {
    for (uint64_t j = i + 1; j < 32; ++j) {
      addPair(p.addRound(), o.shire * 32 + i, o.shire * 32 + j);
    }
  }
  setPoll(p, o);
  return reportPairs("intra", p, dev.run(p)) ? 1 : 0;
}

// Participants: the first --per-shire minions of every shire in --shires.
std::vector<uint64_t> participants(const Options& o) {
  std::vector<uint64_t> out;
  for (uint64_t s = 0; s < 32; ++s) {
    if ((o.shireMask >> s) & 1) {
      for (uint64_t k = 0; k < std::min<uint64_t>(o.perShire, 32); ++k) {
        out.push_back(s * 32 + k);
      }
    }
  }
  return out;
}

// Rings for NB_SHIFT. Each ring is a list of minions; consecutive members alternate send-first.
std::vector<std::vector<uint64_t>> makeRings(const Options& o) {
  std::vector<std::vector<uint64_t>> rings;
  const uint64_t per = std::min<uint64_t>(o.perShire, 32);
  std::vector<uint64_t> shires;
  for (uint64_t s = 0; s < 32; ++s) {
    if ((o.shireMask >> s) & 1) {
      shires.push_back(s);
    }
  }
  if (o.rings == "pair" || o.rings == "neigh" || o.rings == "shire") {
    const uint64_t len = o.rings == "pair" ? 2 : o.rings == "neigh" ? 8 : 32;
    for (uint64_t s : shires) {
      for (uint64_t k = 0; k + len <= per; k += len) {
        std::vector<uint64_t> ring;
        for (uint64_t i = 0; i < len; ++i) {
          ring.push_back(s * 32 + k + i);
        }
        rings.push_back(ring);
      }
    }
  } else if (o.rings.rfind("xshire:", 0) == 0) {
    // Minion k of shire list[i] sends to minion k of list[(i + K) % n]: every message crosses the mesh.
    const uint64_t K = std::strtoull(o.rings.c_str() + 7, nullptr, 0);
    const uint64_t n = shires.size();
    if (K == 0 || K >= n) {
      throw std::runtime_error("xshire:K needs 0 < K < number of shires");
    }
    std::vector<bool> used(n, false);
    for (uint64_t start = 0; start < n; ++start) {
      if (used[start]) {
        continue;
      }
      std::vector<uint64_t> cycle;
      for (uint64_t i = start; !used[i]; i = (i + K) % n) {
        used[i] = true;
        cycle.push_back(i);
      }
      for (uint64_t k = 0; k < per; ++k) {
        std::vector<uint64_t> ring;
        for (uint64_t i : cycle) {
          ring.push_back(shires[i] * 32 + k);
        }
        rings.push_back(ring);
      }
    }
  } else {
    throw std::runtime_error("--rings must be pair, neigh, shire or xshire:K");
  }
  for (const auto& r : rings) {
    if (r.size() < 2 || r.size() % 2) {
      throw std::runtime_error("every ring needs an even length (got " + std::to_string(r.size()) + ")");
    }
  }
  return rings;
}

// Throughput tests (shift, spin): one calibration launch, then about 0.5 s launches until --seconds.
int throughputLoop(const Options& o, Session& dev, Plan p, const char* test, uint64_t bytesPerIter,
                   const std::vector<std::vector<uint64_t>>& rings) {
  int bad = 0;
  auto one = [&](int launchNo) -> double {
    const auto out = dev.run(p);
    uint64_t cmax = 0, reported = 0, checked = 0;
    double csum = 0;
    bool ok = out.ok;
    std::map<uint64_t, uint64_t> prevOf;
    for (const auto& r : rings) {
      for (size_t i = 0; i < r.size(); ++i) {
        prevOf[r[i]] = r[(i + r.size() - 1) % r.size()];
      }
    }
    for (const auto& r : out.records) {
      if (r.magic != NB_MAGIC) {
        continue;
      }
      ++reported;
      cmax = std::max<uint64_t>(cmax, r.cycles);
      csum += double(r.cycles);
      if (p.mode == NB_SHIFT && p.count <= 16 && p.funct == NB_MOVE) {
        ++checked;
        if (r.value1 != NB_PATTERN(prevOf[r.minion])) {
          ok = false;
        }
      }
    }
    ok = ok && reported == out.layout.slots;
    const double bytes = double(bytesPerIter) * double(p.iters);
    const double secs = out.ghz > 0 ? double(cmax) / (out.ghz * 1e9) : 0;
    std::printf("NOCBENCH {\"test\":\"%s\",\"kind\":\"throughput\",\"mode\":\"%s\",\"rings\":\"%s\",\"count\":%llu,"
                "\"participants\":%llu,\"shire_mask\":\"0x%llx\",\"iters\":%llu,\"launch\":%d,\"t_start_ms\":%lld,"
                "\"t_end_ms\":%lld,\"wall_s\":%.6f,\"ghz\":%.4f,\"cycles_max\":%llu,\"cycles_mean\":%.0f,"
                "\"bytes\":%.0f,\"gbps_kernel\":%.3f,\"bytes_per_cycle_per_minion\":%.4f,\"checked\":%llu,\"ok\":%s}\n",
                test, modeName(p.mode).c_str(), o.rings.c_str(), (unsigned long long)p.count,
                (unsigned long long)reported, (unsigned long long)out.layout.shireMask, (unsigned long long)p.iters,
                launchNo, out.t0Ms, out.t1Ms, out.wallS, out.ghz, (unsigned long long)cmax,
                reported ? csum / double(reported) : 0.0, bytes, secs > 0 ? bytes / secs / 1e9 : 0.0,
                reported && csum > 0 ? bytes / double(reported) / (csum / double(reported)) : 0.0,
                (unsigned long long)checked, ok ? "true" : "false");
    std::fflush(stdout);
    bad += !ok;
    return std::max(out.wallS, 1e-4);
  };
  const double wall = one(-1);
  if (o.sysemu || o.seconds <= 0) {
    return bad;
  }
  p.iters = std::max<uint64_t>(1, uint64_t(double(p.iters) * 0.5 / wall));
  double spent = 0;
  for (int launchNo = 0; spent < o.seconds; ++launchNo) {
    if (dev.overBudget()) {
      std::fprintf(stderr, "stopping: device-time budget of %.1f s used\n", o.budget);
      break;
    }
    spent += one(launchNo);
  }
  return bad;
}

int testShift(const Options& o, Session& dev) {
  const auto rings = makeRings(o);
  Plan p;
  p.mode = NB_SHIFT;
  p.count = o.count;
  p.funct = kFuncts.at(o.funct);
  p.iters = o.iters ? o.iters : 2000;
  p.warmup = o.warmup;
  auto& round = p.addRound();
  uint64_t members = 0;
  for (const auto& r : rings) {
    for (size_t i = 0; i < r.size(); ++i) {
      round[r[i]] = NB_ENTRY(r[(i + 1) % r.size()], r[(i + r.size() - 1) % r.size()], i % 2 == 0);
    }
    members += r.size();
  }
  return throughputLoop(o, dev, p, "shift", members * p.count * 32, rings) ? 1 : 0;
}

int testSpin(const Options& o, Session& dev) {
  Plan p;
  p.mode = NB_SPIN;
  p.iters = o.iters ? o.iters : 200000;
  auto& round = p.addRound();
  for (uint64_t m : participants(o)) {
    round[m] = NB_ENTRY(0, 0, false);
  }
  return throughputLoop(o, dev, p, "spin", 0, {}) ? 1 : 0;
}

int testAllreduce(const Options& o, Session& dev) {
  int bad = 0;
  for (uint64_t levels : parseList(o.levels)) {
    Plan p;
    p.mode = NB_ALLREDUCE;
    p.levels = levels;
    p.shireMask = levels <= 5 ? o.shireMask : (1ull << std::max<uint64_t>(1, (1ull << levels) / 32)) - 1;
    p.count = o.count;
    p.funct = o.funct == "move" ? NB_IMAX : kFuncts.at(o.funct);  // must keep the sum: imax, imin or move
    p.iters = o.iters ? o.iters : 500;
    if (dev.overBudget()) {
      std::fprintf(stderr, "stopping: device-time budget of %.1f s used\n", o.budget);
      break;
    }
    const auto out = dev.run(p);
    const uint64_t n = 1ull << levels;  // minions per tree
    const uint32_t want = uint32_t(n * (n + 1) / 2);
    const uint64_t rootMask = levels <= 5 ? 31 : NB_MINIONS - 1;
    uint64_t reported = 0, wrong = 0, cmax = 0;
    std::vector<uint64_t> roots;
    for (const auto& r : out.records) {
      if (r.magic != NB_MAGIC) {
        continue;
      }
      ++reported;
      wrong += r.value0 != want || r.value1 != want;
      cmax = std::max<uint64_t>(cmax, r.cycles);
      if ((r.minion & rootMask) == 0) {
        roots.push_back(r.cycles);
      }
    }
    std::sort(roots.begin(), roots.end());
    const uint64_t root = roots.empty() ? 0 : roots[roots.size() / 2];
    const bool ok = out.ok && reported == out.layout.slots && wrong == 0;
    bad += !ok;
    std::printf("NOCBENCH {\"test\":\"allreduce\",\"kind\":\"allreduce\",\"levels\":%llu,\"minions\":%llu,"
                "\"trees\":%zu,\"shire_mask\":\"0x%llx\",\"count\":%llu,\"funct\":%llu,\"iters\":%llu,\"cycles\":%llu,"
                "\"cycles_per_iter\":%.2f,\"root_min\":%.2f,\"root_max\":%.2f,\"cycles_max\":%llu,\"wrong\":%llu,"
                "\"wall_s\":%.4f,\"ghz\":%.4f,\"t_start_ms\":%lld,\"t_end_ms\":%lld,\"ok\":%s}\n",
                (unsigned long long)levels, (unsigned long long)n, roots.size(),
                (unsigned long long)out.layout.shireMask, (unsigned long long)p.count, (unsigned long long)p.funct,
                (unsigned long long)p.iters, (unsigned long long)root, double(root) / double(p.iters),
                roots.empty() ? 0.0 : double(roots.front()) / double(p.iters),
                roots.empty() ? 0.0 : double(roots.back()) / double(p.iters), (unsigned long long)cmax,
                (unsigned long long)wrong, out.wallS, out.ghz, out.t0Ms, out.t1Ms, ok ? "true" : "false");
    std::fflush(stdout);
  }
  return bad ? 1 : 0;
}

int testBarrier(const Options& o, Session& dev) {
  Plan p;
  p.mode = NB_BARRIER;
  p.scope = o.scope == "chip" ? NB_SCOPE_CHIP : NB_SCOPE_SHIRE;
  p.iters = o.iters ? o.iters : 2000;
  p.warmup = o.warmup;
  auto& round = p.addRound();
  for (uint64_t m : participants(o)) {
    round[m] = NB_ENTRY(0, 0, false);
  }
  setPoll(p, o);
  const auto out = dev.run(p);
  uint64_t reported = 0, cmax = 0, timeouts = 0;
  double csum = 0;
  for (const auto& r : out.records) {
    if (r.magic == NB_MAGIC) {
      ++reported;
      timeouts += r.value1 == NB_TIMEOUT;
      cmax = std::max<uint64_t>(cmax, r.cycles);
      csum += double(r.cycles);
    }
  }
  const bool ok = out.ok && reported == out.layout.slots && timeouts == 0;
  std::printf("NOCBENCH {\"test\":\"barrier\",\"kind\":\"barrier\",\"scope\":\"%s\",\"per_shire\":%llu,"
              "\"shire_mask\":\"0x%llx\",\"participants\":%llu,\"iters\":%llu,\"cycles_per_iter_max\":%.2f,"
              "\"cycles_per_iter_mean\":%.2f,\"wall_s\":%.4f,\"ghz\":%.4f,\"t_start_ms\":%lld,\"t_end_ms\":%lld,"
              "\"poll\":%s,\"ok\":%s}\n",
              o.scope.c_str(), (unsigned long long)std::min<uint64_t>(o.perShire, 32),
              (unsigned long long)out.layout.shireMask, (unsigned long long)reported, (unsigned long long)p.iters,
              double(cmax) / double(p.iters), reported ? csum / double(reported) / double(p.iters) : 0.0, out.wallS,
              out.ghz, out.t0Ms, out.t1Ms, p.poll ? "true" : "false", ok ? "true" : "false");
  std::fflush(stdout);
  return ok ? 0 : 1;
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
    else if (a == "--mode") o.mode = next();
    else if (a == "--pairs") o.pairs = next();
    else if (a == "--counts") o.counts = next();
    else if (a == "--count") o.count = std::strtoull(next().c_str(), nullptr, 0);
    else if (a == "--funct") o.funct = next();
    else if (a == "--rings") o.rings = next();
    else if (a == "--levels") o.levels = next();
    else if (a == "--scope") o.scope = next();
    else if (a == "--iters") o.iters = std::strtoull(next().c_str(), nullptr, 0);
    else if (a == "--warmup") o.warmup = std::strtoull(next().c_str(), nullptr, 0);
    else if (a == "--concurrent") o.concurrent = true;
    else if (a == "--minion") o.minion = std::strtoull(next().c_str(), nullptr, 0);
    else if (a == "--shire") o.shire = std::strtoull(next().c_str(), nullptr, 0);
    else if (a == "--per-shire") o.perShire = std::strtoull(next().c_str(), nullptr, 0);
    else if (a == "--shires") o.shireMask = std::strtoull(next().c_str(), nullptr, 0);
    else if (a == "--seconds") o.seconds = std::atof(next().c_str());
    else if (a == "--budget") o.budget = std::atof(next().c_str());
    else if (a == "--poll") o.poll = std::atoi(next().c_str());
    else if (a == "--poll-limit") o.pollLimit = std::strtoull(next().c_str(), nullptr, 0);
    else if (a == "--kernel") o.kernel = next();
    else {
      std::fprintf(stderr, "unknown option %s (see the comment at the top of host/main.cpp)\n", a.c_str());
      return 2;
    }
  }
  if (o.budget < 0) {
    o.budget = o.sysemu ? 1e9 : 8.0;  // the simulator is private; a real card is shared
  }
  if (!kFuncts.count(o.funct) || o.minion >= 32 || o.shire >= 32 || o.shireMask == 0 || (o.shireMask >> 32) ||
      o.perShire == 0) {
    std::fprintf(stderr, "bad --funct / --minion / --shire / --shires / --per-shire\n");
    return 2;
  }
  const auto elf = readFile(o.kernel);
  if (elf.empty()) {
    std::fprintf(stderr, "cannot read kernel %s\n", o.kernel.c_str());
    return 1;
  }
  try {
    // Plans are checked again before every launch (Session::run).
    if (o.test != "pairs" && o.test != "matrix" && o.test != "intra" && o.test != "shift" &&
        o.test != "allreduce" && o.test != "barrier" && o.test != "spin") {
      std::fprintf(stderr, "--test must be pairs, matrix, intra, shift, allreduce, barrier or spin\n");
      return 2;
    }
    if (o.test == "shift") {
      makeRings(o);
    }
    Session dev(o, elf);
    if (o.test == "pairs") return testPairs(o, dev);
    if (o.test == "matrix") return testMatrix(o, dev);
    if (o.test == "intra") return testIntra(o, dev);
    if (o.test == "shift") return testShift(o, dev);
    if (o.test == "allreduce") return testAllreduce(o, dev);
    if (o.test == "barrier") return testBarrier(o, dev);
    return testSpin(o, dev);
  } catch (const std::exception& e) {
    std::fprintf(stderr, "FAIL: %s\n", e.what());
    return 1;
  }
}
