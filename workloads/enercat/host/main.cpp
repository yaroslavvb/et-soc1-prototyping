// The energy catalogue: one kind of operation flat out on every hart, while the host's power logger runs.
// Every launch prints one line
//   ENERCAT {json}
//
//   enercat_host --pattern spin|iadd|...|tload [--operands zeros|const|random] [--harts 1|2]
//                [--seconds S] [--window CYCLES] [--slice-bytes B] [--scp] [--shires MASK]
//
// The card is shared: each launch runs `window` cycles (0.4 s by default) and the process stops after
// --seconds, so nothing holds the device for long.
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
  {"tstore", {EC_TSTORE, 8, "tensor_store", true}}, {"tload", {EC_TLOAD, 8, "tensor_load", true}},
};

struct Options {
  bool sysemu = false;
  std::string simArgs, pattern = "spin", operands = "random";
  uint64_t harts = 2, shireMask = 0xffffffff, window = 240000000, sliceBytes = 256 * 1024, seed = 1;
  bool scp = false;
  uint64_t minionMask = 0, stride = 64, accessBytes = 64, region = 0, hopDistance = 0, jumpEvery = 0, jumpBytes = 0;
  std::string targets;   // "shift:K" or an explicit 32-entry list "t0,t1,...": the shire each shire reads from
  double seconds = 4.0, budget = 9.5;
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
  bool overBudget() const { return secondsSince(tOpen_) > o_.budget; }

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
std::vector<uint32_t> sources(const std::string& kind, uint64_t seed) {
  std::vector<uint32_t> v(EC_MAX_HARTS * 64);
  std::mt19937_64 rng(seed);
  std::uniform_real_distribution<float> u(0.5f, 2.0f);
  for (auto& w : v) {
    if (kind == "zeros") w = 0;
    else if (kind == "const") w = 0x3F800000u;
    else { const float f = u(rng); std::memcpy(&w, &f, 4); }
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
std::pair<std::vector<uint32_t>, uint64_t> targetsAtDistance(int d, uint64_t shireMask) {
  std::vector<uint32_t> t(32, 0);
  std::vector<int> load(32, 0);
  uint64_t mask = 0;
  for (int s = 0; s < 32; ++s) {
    if (!((shireMask >> s) & 1)) continue;
    int best = -1;
    for (int c = 0; c < 32; ++c) {
      if (c == s || hops(s, c) != d || load[c] >= 2) continue;
      if (best < 0 || load[c] < load[best]) best = c;
    }
    if (best >= 0) { t[s] = best; ++load[best]; mask |= 1ull << s; }
  }
  return {t, mask};
}

int run(const Options& o, Session& dev) {
  const Pat p = lookup(o.pattern);
  const uint64_t harts = p.hart0 ? 1 : o.harts;
  const auto src = sources(o.operands, o.seed);
  std::byte* sbuf = dev.alloc(src.size() * 4);
  dev.put(src.data(), sbuf, src.size() * 4);
  std::byte* slice = nullptr;
  const bool stream = p.mode == EC_ST_STREAM || p.mode == EC_TSTORE || p.mode == EC_TLOAD ||
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
  if ((o.scp || o.hopDistance || !o.targets.empty()) && 256 * 1024 + 32 * o.sliceBytes > 0x280000ull) {
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
  if (o.hopDistance || !o.targets.empty()) {
    std::vector<uint32_t> t(32, 0);
    if (o.hopDistance) {
      auto r = targetsAtDistance((int)o.hopDistance, o.shireMask);
      t = r.first; shireMaskUsed = r.second;
    } else if (o.targets.rfind("shift:", 0) == 0) {
      const int k = std::stoi(o.targets.substr(6));
      for (int s = 0; s < 32; ++s) t[s] = (uint32_t)((s + k) % 32);
    } else {
      std::stringstream ss(o.targets); std::string item; int i = 0;
      while (std::getline(ss, item, ',') && i < 32) t[i++] = (uint32_t)std::stoul(item);
    }
    int n = 0; for (int s = 0; s < 32; ++s) if ((shireMaskUsed >> s) & 1) { meanHops += hops(s, (int)t[s]); ++n; }
    meanHops = n ? meanHops / n : 0;
    std::byte* tb = dev.alloc(32 * 4);
    dev.put(t.data(), tb, 32 * 4);
    a.targets = reinterpret_cast<uint64_t>(tb);
    a.scp = 2;
  }
  a.shire_mask = shireMaskUsed;

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
                "\"region\":%llu,\"jump_every\":%llu,\"jump_bytes\":%llu,\"hop_distance\":%llu,\"mean_hops\":%.3f,\"targets\":\"%s\","
                "\"t_start_ms\":%lld,\"t_end_ms\":%lld,\"ok\":%s}\n",
                o.pattern.c_str(), p.unit, o.operands.c_str(), (unsigned long long)harts,
                __builtin_popcountll(shireMaskUsed), (unsigned long long)n, (unsigned long long)shireMaskUsed, ops,
                (unsigned long long)bytes,
                (unsigned long long)cmax, n ? csum / double(n) : 0.0, secs > 0 ? ops / secs : 0.0,
                secs > 0 ? double(bytes) / secs : 0.0, (cmax && n) ? ops / double(cmax) / double(n) : 0.0,
                wallS, (o.scp || a.scp) ? "true" : "false", (unsigned long long)o.sliceBytes,
                (unsigned long long)o.minionMask, (unsigned long long)o.stride, (unsigned long long)o.accessBytes,
                (unsigned long long)a.region, (unsigned long long)o.jumpEvery, (unsigned long long)o.jumpBytes,
                (unsigned long long)o.hopDistance, meanHops, o.targets.c_str(),
                dev.t0Ms, dev.t1Ms, (ok && n) ? "true" : "false");
    std::fflush(stdout);
    if (!ok || !n) { ++bad; break; }
  }
  return bad ? 1 : 0;
}

}  // namespace

int main(int argc, char** argv) {
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
    else if (a == "--targets") o.targets = next();
    else if (a == "--jump-every") o.jumpEvery = std::strtoull(next().c_str(), nullptr, 0);
    else if (a == "--jump-bytes") o.jumpBytes = parseSize(next());
    else if (a == "--list") { for (const auto& g : EC_GEN_MODES) std::printf("%s\t%s\n", g.name, g.note); return 0; }
    else if (a == "--kernel") o.kernel = next();
    else { std::fprintf(stderr, "unknown option %s\n", a.c_str()); return 2; }
  }
  try {
    const auto elf = readFile(o.kernel);
    if (elf.empty()) throw std::runtime_error("cannot read kernel " + o.kernel);
    Session dev(o, elf);
    return run(o, dev);
  } catch (const std::exception& e) {
    std::fprintf(stderr, "FAIL: %s\n", e.what());
    return 1;
  }
}
