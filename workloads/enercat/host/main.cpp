// The energy catalogue: one kind of operation flat out on every hart, while the host's power logger runs.
// Every launch prints one line
//   ENERCAT {json}
//
//   enercat_host --pattern spin|iadd|...|tload [--operands zeros|const|random] [--harts 1|2]
//                [--seconds S] [--window CYCLES] [--slice-bytes B] [--scp] [--shires MASK]
//
// The card is shared: each launch runs `window` cycles (0.4 s by default) and the process stops after
// --seconds, so nothing holds the device for long.
#include <g3log/loglevels.hpp>
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
#include <limits>
#include <map>
#include <cmath>
#include <random>
#include <sstream>
#include <string>
#include <vector>

#include "Constants.h"
#include "enercat_args.h"
#include "enercat_modes.h"
#ifdef ENERCAT_GS
#include <functional>
#include <set>
#include "enercat_gs.h"
#endif

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
  switch (end && *end ? std::toupper(*end) : 0) {
  case 'K': v *= 1024; break;
  case 'M': v *= 1024 * 1024; break;
  case 'G': v *= 1024.0 * 1024 * 1024; break;
  default: break;
  }
  return static_cast<uint64_t>(v);
}

// name -> (mode, ops per loop iteration, unit, hart-0-only)
struct Pat { uint64_t mode; uint64_t opsPerIter; const char* unit; bool hart0; };
const std::map<std::string, Pat> PATTERNS = {
  {"spin", {EC_SPIN, 64, "addi", false}},       {"iadd", {EC_IADD, 64, "add", false}},
  {"imul", {EC_IMUL, 64, "mul", false}},        {"ixor", {EC_IXOR, 64, "xor", false}},
  {"fadd_s", {EC_FADD_S, 64, "fadd.s", false}}, {"fmul_s", {EC_FMUL_S, 64, "fmul.s", false}},
  {"fmadd_s", {EC_FMADD_S, 64, "fmadd.s", false}},
  {"fadd_ps", {EC_FADD_PS, 64, "fadd.ps", false}}, {"fmul_ps", {EC_FMUL_PS, 64, "fmul.ps", false}},
  {"fmadd_ps", {EC_FMADD_PS, 64, "fmadd.ps", false}},
  {"iadd_pi", {EC_IADD_PI, 64, "fadd.pi", false}}, {"imul_pi", {EC_IMUL_PI, 64, "fmul.pi", false}},
  {"fexp_ps", {EC_FEXP_PS, 64, "fexp.ps", false}}, {"frcp_ps", {EC_FRCP_PS, 64, "frcp.ps", false}},
  {"fsqrt_ps", {EC_FSQRT_PS, 64, "fsqrt.ps", false}}, {"fdiv_ps", {EC_FDIV_PS, 64, "fdiv.ps", false}},
  {"ld_l1", {EC_LD_L1, 64, "flw.ps", false}},   {"st_l1", {EC_ST_L1, 64, "fsw.ps", false}},
  {"st_stream", {EC_ST_STREAM, 64, "fsw.ps", false}},
  {"tstore", {EC_TSTORE, 8, "tensor_store", true}}, {"tstore_raw", {EC_TSTORE_RAW, 8, "tensor_store", true}}, {"tstore_uniq", {EC_TSTORE_UNIQ, 8, "tensor_store", true}}, {"tload", {EC_TLOAD, 8, "tensor_load", true}},
};

struct Options {
  bool sysemu = false;
  std::string simArgs, pattern = "spin", operands = "random", hopAxis = "any", pairs;
  bool uniqRegions = false;   // --uniq-regions: the second reader of a target reads region 1 (see EC_TSTORE_UNIQ)
  uint64_t dumpBytes = 0;   // --dump-slice N: after the run, print the first N bytes of hart 0's DRAM slice (checks a store image)
  uint64_t harts = 2, shireMask = 0xffffffff, window = 240000000, sliceBytes = 256 * 1024, seed = 1;
  bool scp = false;
  uint64_t minionMask = 0, stride = 64, accessBytes = 64, region = 0, hopDistance = 0, jumpEvery = 0, jumpBytes = 0;
  std::string targets;   // "shift:K" or an explicit 32-entry list "t0,t1,...": the shire each shire reads from
  double seconds = 4.0, budget = 9.5;
  std::string kernel = KERNEL_ELF;
#ifdef ENERCAT_GS
  // gathers and scatters (host/enercat_gs_host.inc)
  std::string gsIndex = "rand", gsShare = "hart", suite;
  uint64_t gsWs = 0, gsMask = 0xff, gsVerify = 0;
  int gsWarm = -1;   // -1: automatic (tables up to 64 KB, not the atomics)
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
      for (std::string arg; extra >> arg;) s.additionalOptions.push_back(arg);
      dl_ = dev::IDeviceLayer::createSysEmuDeviceLayer(s, 1);
    } else {
      dl_ = dev::IDeviceLayer::createPcieDeviceLayer(true, false);  // ops node only
    }
    rt_ = rt::IRuntime::create(dl_);
    const auto devices = rt_->getDevices();
    if (devices.empty()) throw std::runtime_error("no ET devices found");
    dev_ = devices[0];
    stream_ = rt_->createStream(dev_);
    const auto load = rt_->loadCode(stream_, elf.data(), elf.size());
    rt_->waitForEvent(load.event_);
    kernel_ = load.kernel_;
    results_ = rt_->mallocDevice(dev_, EC_MAX_HARTS * sizeof(EcResult));
    std::fprintf(stderr, "device ready in %.2f s\n", secondsSince(tOpen_));
  }
  ~Session() {
    for (auto* p : allocs_) rt_->freeDevice(dev_, p);
    rt_->freeDevice(dev_, results_);
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
  void get(const std::byte* src, void* dst, size_t bytes) {
    rt_->memcpyDeviceToHost(stream_, src, reinterpret_cast<std::byte*>(dst), bytes);
    rt_->waitForStream(stream_);
  }
  bool overBudget() const { return secondsSince(tOpen_) > o_.budget; }
#ifdef ENERCAT_GS
  void freeAll() {   // between the configurations of a --suite session
    for (auto* p : allocs_) rt_->freeDevice(dev_, p);
    allocs_.clear();
  }
#endif

  long long t0Ms = 0, t1Ms = 0;  // epoch bounds of the last launch, for lining up with power samples

  bool launch(EcArgs a, std::vector<EcResult>& res, double& wallS) {
    res.assign(EC_MAX_HARTS, EcResult{});
    rt_->memcpyHostToDevice(stream_, reinterpret_cast<const std::byte*>(res.data()), results_,
                            res.size() * sizeof(EcResult));
    rt_->waitForStream(stream_);
    if (!a.shire_mask) a.shire_mask = o_.shireMask;
    a.results = reinterpret_cast<uint64_t>(results_);
    rt::KernelLaunchOptions opts;
    opts.setShireMask(o_.shireMask);
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
    rt_->memcpyDeviceToHost(stream_, results_, reinterpret_cast<std::byte*>(res.data()),
                            res.size() * sizeof(EcResult));
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


// 256 B of sources per hart. zeros: all 0. const: every word 1.0f (also a fine integer constant).
// random: floats drawn in [0.5, 2) so every unit sees ordinary values and no operation overflows, traps or
// hits a slow path; as integers those bit patterns are simply random 32-bit words.
// Two families for the wire experiments, stored with --pattern tstore_raw so the scratchpad holds exactly these
// bytes (the store image of hart h is its block followed by hart h+1's, 512 B, repeated through the slice):
//   bern:P  every bit independently 1 with probability P, so any two words differ in a bit with probability
//           2P(1-P), whichever flows interleave on a link.
//   alt:N   blocks of N bytes (N >= 4, dividing 512) alternately all-zero and all-one, by offset in the 512 B image:
//           the bytes on a link toggle only where a flit boundary meets a block boundary, which probes flit width.
std::vector<uint32_t> sources(const std::string& kind, uint64_t seed) {
  std::vector<uint32_t> v(EC_MAX_HARTS * 64);
  std::mt19937_64 rng(seed);
  std::uniform_real_distribution<float> u(0.5f, 2.0f);
  if (kind.rfind("bern:", 0) == 0) {
    const double pr = std::stod(kind.substr(5));
    std::bernoulli_distribution bit(pr);
    for (auto& w : v) { w = 0; for (int b = 0; b < 32; ++b) if (bit(rng)) w |= 1u << b; }
    return v;
  }
  if (kind.rfind("uq:", 0) == 0) return v;   // a label for readers: the data was put in the scratchpads by tstore_uniq
  if (kind == "frz") {
    // one random 64 B line, the same everywhere: half the bits are ones, and no two lines differ
    uint32_t line[16];
    for (auto& w : line) w = (uint32_t)rng();
    for (size_t i = 0; i < v.size(); ++i) v[i] = line[i % 16];
    return v;
  }
  if (kind.rfind("alt:", 0) == 0) {
    const uint64_t n = std::stoull(kind.substr(4));
    if (n < 4 || 512 % n) throw std::runtime_error("alt:N needs N >= 4 dividing 512");
    for (size_t i = 0; i < v.size(); ++i) {
      const uint64_t hart = i / 64, off = (hart & 1) * 256 + (i % 64) * 4;   // byte offset in the 512 B image
      v[i] = ((off / n) & 1) ? 0xFFFFFFFFu : 0u;
    }
    return v;
  }
  for (auto& w : v) {
    if (kind == "zeros") w = 0;
    else if (kind == "const") w = 0x3F800000u;
    else if (kind == "random") { const float f = u(rng); std::memcpy(&w, &f, 4); }
    else throw std::runtime_error("unknown --operands " + kind);
  }
  return v;
}

// uq:P for --pattern tstore_uniq: 1024 minions x 2 regions x `bytes` of independent bits, every bit 1 with probability
// P, built from whole random words so it is fast: 1/2 = a, 1/4 = a&b, 1/8 = a&b&c, and 3/4, 7/8 as the exact bitwise
// complements of 1/4, 1/8 (same random stream), so P and 1-P carry complementary bits.
std::vector<uint32_t> uniqueSources(const std::string& kind, uint64_t bytes, uint64_t seed) {
  const std::string ps = kind.substr(3);
  std::vector<uint32_t> v(1024ull * 2 * bytes / 4);
  std::mt19937_64 rng(seed);
  auto w32 = [&]() { return (uint32_t)(rng() >> 32); };
  int ands = 0; bool inv = false, zero = false;
  if (ps == "0") zero = true;
  else if (ps == "1") { zero = true; inv = true; }
  else if (ps == "0.5") ands = 1;
  else if (ps == "0.25") ands = 2;
  else if (ps == "0.125") ands = 3;
  else if (ps == "0.75") { ands = 2; inv = true; }
  else if (ps == "0.875") { ands = 3; inv = true; }
  else throw std::runtime_error("uq:P supports P in {0, 0.125, 0.25, 0.5, 0.75, 0.875, 1}");
  for (auto& w : v) {
    uint32_t x = zero ? 0u : 0xFFFFFFFFu;
    for (int k = 0; k < ands; ++k) x &= w32();
    w = inv ? ~x : x;
  }
  return v;
}

Pat lookup(const std::string& name) {
  const auto it = PATTERNS.find(name);
  if (it != PATTERNS.end()) return it->second;
  for (const auto& g : EC_GEN_MODES) {
    if (name == g.name) return Pat{g.mode, g.ops_per_iter, g.unit, g.hart0};
  }
  if (name == "tload_pat") return Pat{EC_TLOAD_PAT, 8, "tensor_load", true};
  if (name == "flw_pat") return Pat{EC_FLW_PAT, 8, "flw.ps", false};
  throw std::runtime_error("unknown --pattern " + name);
}

// The mesh, as workloads/memprobe/gen_ops.py has it: shire -> (x, y). Hop distance is Manhattan.
const std::map<int, std::pair<int,int>> MESH = {
  {0,{0,0}},{24,{1,0}},{9,{2,0}},{25,{3,0}},{2,{4,0}},{11,{5,0}},
  {8,{0,1}},{16,{1,1}},{1,{2,1}},{17,{3,1}},{10,{4,1}},{19,{5,1}},
  {3,{0,2}},{4,{1,2}},{13,{2,2}},{14,{3,2}},{18,{4,2}},{27,{5,2}},
  {12,{1,3}},{21,{2,3}},{22,{3,3}},{26,{4,3}},
  {20,{1,4}},{29,{2,4}},{30,{3,4}},{15,{4,4}},{23,{5,4}},
  {28,{1,5}},{5,{2,5}},{6,{3,5}},{7,{4,5}},{31,{5,5}}};
int hops(int a, int b) { auto pa = MESH.at(a), pb = MESH.at(b); return std::abs(pa.first - pb.first) + std::abs(pa.second - pb.second); }

// For --hop-distance d: give every shire a target exactly d hops away, at most two readers per target so
// no scratchpad is swamped. Shires with no such target sit out (returned mask says which run).
// axis "x" or "y" keeps only pairs that differ in that coordinate alone (a straight run of d links).
std::pair<std::vector<uint32_t>, uint64_t> targetsAtDistance(int d, uint64_t shireMask, const std::string& axis = "any") {
  std::vector<uint32_t> t(32, 0);
  std::vector<int> load(32, 0);
  uint64_t mask = 0;
  auto onAxis = [&](int s, int c) {
    const auto ps = MESH.at(s), pc = MESH.at(c);
    if (axis == "x") return ps.second == pc.second;
    if (axis == "y") return ps.first == pc.first;
    return true;
  };
  for (int s = 0; s < 32; ++s) {
    if (!((shireMask >> s) & 1)) continue;
    int best = -1;
    for (int c = 0; c < 32; ++c) {
      if (c == s || hops(s, c) != d || !onAxis(s, c) || load[c] >= 2) continue;
      if (best < 0 || load[c] < load[best]) best = c;
    }
    if (best >= 0) { t[s] = best; ++load[best]; mask |= 1ull << s; }
  }
  return {t, mask};
}

#ifdef ENERCAT_GS
#include "enercat_gs_host.inc"
#endif

int run(const Options& o, Session& dev) {
  const Pat p = lookup(o.pattern);
  const uint64_t harts = p.hart0 ? 1 : o.harts;
  const auto small = sources(o.operands, o.seed);
  const auto src = p.mode == EC_TSTORE_UNIQ ? uniqueSources(o.operands, o.sliceBytes, o.seed) : small;
  std::byte* sbuf = dev.alloc(src.size() * 4);
  dev.put(src.data(), sbuf, src.size() * 4);
  std::byte* slice = nullptr;
  const bool stream = p.mode == EC_ST_STREAM || p.mode == EC_TSTORE || p.mode == EC_TSTORE_RAW || p.mode == EC_TSTORE_UNIQ || p.mode == EC_TLOAD ||
                      p.mode == EC_TLOAD_PAT || p.mode == EC_FLW_PAT || p.mode >= EC_GEN_FIRST;
  uint64_t sliceStride = o.sliceBytes;
  if (stream && !o.scp && o.hopDistance == 0 && o.targets.empty()) {
    const bool pat = p.mode == EC_TLOAD_PAT || p.mode == EC_FLW_PAT;
    if (pat) sliceStride += 8192;   // room for the kernel's bank spread
    // One slice per participant when a minion mask is given (the kernel indexes by rank), else per hart.
    uint64_t nslices = EC_MAX_HARTS;
    if (p.mode == EC_TLOAD_PAT && o.minionMask) {
      nslices = (uint64_t)__builtin_popcountll(o.shireMask) * (uint64_t)__builtin_popcountll(o.minionMask & 0xFFFFFFFFull);
    }
    slice = dev.alloc(nslices * sliceStride);
    // Loads read what is there, so fill the slices with the operand pattern: the bytes on the wire are then
    // zeros, one constant or random, the same as the arithmetic patterns see.
    if (p.mode == EC_TLOAD || p.mode == EC_TLOAD_PAT || p.mode == EC_FLW_PAT) {
      std::vector<uint32_t> fill(nslices * sliceStride / 4);
      for (size_t i = 0; i < fill.size(); ++i) fill[i] = src[i % src.size()];
      dev.put(fill.data(), slice, fill.size() * 4);
    }
  }
  const uint64_t regions = (p.mode == EC_TSTORE_UNIQ || o.uniqRegions) ? 2 : 1;
  if ((o.scp || o.hopDistance || !o.targets.empty() || !o.pairs.empty()) && 256 * 1024 + regions * 32 * o.sliceBytes > 0x280000ull) {
    throw std::runtime_error("--scp: 256 KB + 32 x --slice-bytes must fit the 2.5 MB scratchpad");
  }
  EcArgs a{};
  a.mode = p.mode;
  a.window = o.window;
  a.harts = harts;
  a.sources = reinterpret_cast<uint64_t>(sbuf);
  a.slice = reinterpret_cast<uint64_t>(slice);
  a.slice_bytes = sliceStride;
  a.scp = o.scp ? 1 : 0;
  a.scp_off = 256 * 1024;
  a.minion_mask = o.minionMask;
  a.stride = o.stride;
  a.access_bytes = o.accessBytes;
  a.region = o.region ? o.region : o.sliceBytes;
  a.jump_every = o.jumpEvery;
  a.jump_bytes = o.jumpBytes;
  uint64_t shireMaskUsed = o.shireMask;
  double meanHops = 0;
  std::string targetMap;   // reader>target for every participating shire
  if (o.hopDistance || !o.targets.empty() || !o.pairs.empty()) {
    std::vector<uint32_t> t(32, 0);
    if (!o.pairs.empty()) {
      // "r:t,r:t,...": shire r reads the scratchpad of shire t; only the listed readers run
      shireMaskUsed = 0;
      std::stringstream ss(o.pairs); std::string item;
      while (std::getline(ss, item, ',')) {
        const auto c = item.find(':');
        const int r = std::stoi(item.substr(0, c)), tg = std::stoi(item.substr(c + 1));
        t[r] = (uint32_t)tg; shireMaskUsed |= 1ull << r;
      }
    } else if (o.hopDistance) {
      auto r = targetsAtDistance((int)o.hopDistance, o.shireMask, o.hopAxis);
      t = r.first; shireMaskUsed = r.second;
    } else if (o.targets.rfind("shift:", 0) == 0) {
      const int k = std::stoi(o.targets.substr(6));
      for (int s = 0; s < 32; ++s) t[s] = (uint32_t)((s + k) % 32);
    } else {
      std::stringstream ss(o.targets); std::string item; int i = 0;
      while (std::getline(ss, item, ',') && i < 32) t[i++] = (uint32_t)std::stoul(item);
    }
    if (o.uniqRegions) {   // the k-th reader of a target (k = 0, 1) reads that target's region k
      std::vector<int> seen(32, 0);
      for (int s = 0; s < 32; ++s) if ((shireMaskUsed >> s) & 1) {
        const int k = seen[t[s]]++;
        if (k > 1) throw std::runtime_error("--uniq-regions: more than two readers of one target");
        t[s] |= (uint32_t)k << 16;
      }
    }
    int n = 0; for (int s = 0; s < 32; ++s) if ((shireMaskUsed >> s) & 1) { meanHops += hops(s, (int)(t[s] & 0xFFFF)); ++n; }
    for (int s = 0; s < 32; ++s) if ((shireMaskUsed >> s) & 1) targetMap += (targetMap.empty() ? "" : ",") + std::to_string(s) + ">" + std::to_string(t[s] & 0xFFFF) + ((t[s] >> 16) ? "/r1" : "");
    meanHops = n ? meanHops / n : 0;
    std::byte* tb = dev.alloc(32 * 4);
    dev.put(t.data(), tb, 32 * 4);
    a.targets = reinterpret_cast<uint64_t>(tb);
    a.scp = 2;
  }
  a.shire_mask = shireMaskUsed;
  // A memory mode with neither a DRAM slice nor a scratchpad target would address physical 0 (the I/O region).
  const bool memMode = p.mode == EC_ST_STREAM || p.mode == EC_TSTORE || p.mode == EC_TSTORE_RAW || p.mode == EC_TSTORE_UNIQ || p.mode == EC_TLOAD ||
                       p.mode == EC_TLOAD_PAT || p.mode == EC_FLW_PAT;
  if (memMode && a.scp == 0 && a.slice == 0) throw std::runtime_error("refusing to launch: memory pattern with no slice");

  const auto tStart = Clock::now();
  int bad = 0;
  while (secondsSince(tStart) < o.seconds && !dev.overBudget()) {
    std::vector<EcResult> res;
    double wallS = 0;
    const bool ok = dev.launch(a, res, wallS);
    uint64_t n = 0, iters = 0, bytes = 0, cmax = 0;
    double csum = 0;
    for (const auto& r : res) {
      if (r.magic != EC_MAGIC) continue;
      ++n; iters += r.iters; bytes += r.bytes; cmax = std::max<uint64_t>(cmax, r.cycles); csum += double(r.cycles);
    }
    const double ops = double(iters) * double(p.opsPerIter);
    const double secs = cmax / 0.6e9;   // device seconds at the 600 MHz the card is pinned to
    std::printf("ENERCAT {\"pattern\":\"%s\",\"unit\":\"%s\",\"operands\":\"%s\",\"harts\":%llu,\"shires\":%d,"
                "\"participants\":%llu,\"shire_mask_used\":\"0x%llx\",\"ops\":%.0f,\"bytes\":%llu,\"cycles_max\":%llu,\"cycles_mean\":%.0f,"
                "\"ops_per_s\":%.4e,\"bytes_per_s\":%.4e,\"ops_per_cycle_per_hart\":%.4f,\"wall_s\":%.4f,"
                "\"scp\":%s,\"slice_bytes\":%llu,\"minion_mask\":\"0x%llx\",\"stride\":%llu,\"access_bytes\":%llu,"
                "\"region\":%llu,\"jump_every\":%llu,\"jump_bytes\":%llu,\"hop_distance\":%llu,\"hop_axis\":\"%s\",\"mean_hops\":%.3f,\"targets\":\"%s\",\"target_map\":\"%s\","
                "\"t_start_ms\":%lld,\"t_end_ms\":%lld,\"ok\":%s}\n",
                o.pattern.c_str(), p.unit, o.operands.c_str(), (unsigned long long)harts,
                __builtin_popcountll(shireMaskUsed), (unsigned long long)n, (unsigned long long)shireMaskUsed, ops,
                (unsigned long long)bytes,
                (unsigned long long)cmax, n ? csum / double(n) : 0.0, secs > 0 ? ops / secs : 0.0,
                secs > 0 ? double(bytes) / secs : 0.0, (cmax && n) ? ops / double(cmax) / double(n) : 0.0,
                wallS, (o.scp || a.scp) ? "true" : "false", (unsigned long long)o.sliceBytes,
                (unsigned long long)o.minionMask, (unsigned long long)o.stride, (unsigned long long)o.accessBytes,
                (unsigned long long)a.region, (unsigned long long)o.jumpEvery, (unsigned long long)o.jumpBytes,
                (unsigned long long)o.hopDistance, o.hopAxis.c_str(), meanHops, o.targets.c_str(), targetMap.c_str(),
                dev.t0Ms, dev.t1Ms, (ok && n) ? "true" : "false");
    std::fflush(stdout);
    if (!ok || !n) { ++bad; break; }
  }
  if (o.dumpBytes && slice && !a.scp) {
    // hart 0's slice is the first one (the kernel indexes slices by hart id); print it as hex words
    std::vector<uint32_t> buf((o.dumpBytes + 3) / 4);
    dev.get(slice, buf.data(), buf.size() * 4);
    std::printf("DUMP");
    for (size_t i = 0; i < buf.size(); ++i) std::printf("%s%08x", i % 8 ? " " : "\nDUMP ", buf[i]);
    std::printf("\n");
    // and the expected image: hart 0's source block followed by hart 1's
    std::printf("EXPECT");
    for (size_t i = 0; i < buf.size(); ++i) std::printf("%s%08x", i % 8 ? " " : "\nEXPECT ", p.mode == EC_TSTORE_UNIQ ? src[i] : src[i % 128]);
    std::printf("\n");
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
      if (i + 1 >= argc) { std::fprintf(stderr, "%s needs a value\n", a.c_str()); std::exit(2); }
      return argv[++i];
    };
    if (a == "--sysemu") o.sysemu = true;
    else if (a == "--sim-args") o.simArgs = next();
    else if (a == "--pattern") o.pattern = next();
    else if (a == "--operands") o.operands = next();
    else if (a == "--harts") o.harts = std::strtoull(next().c_str(), nullptr, 0);
    else if (a == "--shires") o.shireMask = std::strtoull(next().c_str(), nullptr, 0);
    else if (a == "--window") o.window = std::strtoull(next().c_str(), nullptr, 0);
    else if (a == "--slice-bytes") o.sliceBytes = parseSize(next());
    else if (a == "--scp") o.scp = true;
    else if (a == "--seconds") o.seconds = std::strtod(next().c_str(), nullptr);
    else if (a == "--budget") o.budget = std::strtod(next().c_str(), nullptr);
    else if (a == "--seed") o.seed = std::strtoull(next().c_str(), nullptr, 0);
    else if (a == "--minions") o.minionMask = std::strtoull(next().c_str(), nullptr, 0);
    else if (a == "--stride") o.stride = parseSize(next());
    else if (a == "--access-bytes") o.accessBytes = parseSize(next());
    else if (a == "--region") o.region = parseSize(next());
    else if (a == "--hop-distance") o.hopDistance = std::strtoull(next().c_str(), nullptr, 0);
    else if (a == "--hop-axis") o.hopAxis = next();
    else if (a == "--pairs") o.pairs = next();
    else if (a == "--uniq-regions") o.uniqRegions = true;
    else if (a == "--dump-slice") o.dumpBytes = parseSize(next());
    else if (a == "--targets") o.targets = next();
    else if (a == "--jump-every") o.jumpEvery = std::strtoull(next().c_str(), nullptr, 0);
    else if (a == "--jump-bytes") o.jumpBytes = parseSize(next());
    else if (a == "--list") { for (const auto& g : EC_GEN_MODES) std::printf("%s\t%s\n", g.name, g.note); return 0; }
    else if (a == "--kernel") o.kernel = next();
#ifdef ENERCAT_GS
    else if (gsParseOne(o, a, next)) {}
#endif
    else { std::fprintf(stderr, "unknown option %s\n", a.c_str()); return 2; }
  }
  try {
    const auto elf = readFile(o.kernel);
    if (elf.empty()) throw std::runtime_error("cannot read kernel " + o.kernel);
    Session dev(o, elf);
#ifdef ENERCAT_GS
    if (!o.suite.empty()) return runGsSuite(o, dev);
    if (o.pattern.rfind("gs.", 0) == 0) return runGs(o, dev);
#endif
    return run(o, dev);
  } catch (const std::exception& e) {
    std::fprintf(stderr, "FAIL: %s\n", e.what());
    return 1;
  }
}
