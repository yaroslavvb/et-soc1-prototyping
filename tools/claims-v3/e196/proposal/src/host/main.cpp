// x14_host: the resident fp32 TensorFMA loop of the public lab repo's workloads/sparsity (`--test fma`), card only,
// with the arms of request 1113-x14-zeroshare. Every launch prints one line
//   X14 {json}
// and every read-back of C (after the first launch of a process and after its last) one line
//   X14CHECK {json}
//
//   x14_host --values file:<tiles>|zeros|ones|pi|randn [--row-mask 0xMMMM] [--zero-rows 0xMMMM] [--live-rows 0xMMMM]
//            [--label NAME] [--seconds T] [--iters N] [--shires MASK] [--per-shire N] [--seed S] [--budget S]
//            [--stop-file PATH] [--dump-tiles FILE]
//   an A B B A train in one process (the lab's E182 method, with a second row mask as well as second tiles):
//   x14_host <the F kind's options as above> [--values-b file:<tiles>] [--row-mask-b 0xMMMM|none] [--label-b NAME]
//            [--zero-rows-b 0xMMMM|none] [--live-rows-b 0xMMMM|none] --abba SFFS|FSSF --launches N
//
// The kernel is the lab's sparsity kernel, unchanged (kernel/sparsity.c): hart 0 of every participating minion
// loads A into L1 scratchpad lines 0-15 and B into lines 16-31, then repeats one 16 x 16 x 16 TensorFMA32, the first
// op of a launch with MUL set; with --row-mask the control word carries the MSK bit and tensor_mask holds the mask
// (PRM 9.4: a row whose bit is clear issues no micro-op). This host is the lab's sparsity host with the other probes
// and the simulator option removed, plus: --label (echoed in every record); the read-back of C after the first
// (calibration) launch of the process and after its last launch only, so that every launch in between is the same
// for every arm: --zero-rows counts the 32-bit words of the named rows that are not zero (+0.0 or -0.0;
// `zero_rows_bad` must be 0) and --live-rows counts the named rows whose 16 words are all zero (`live_rows_zero` must
// be 0); the train; and the one-card rule below.
//
// The train: F is the kind of --values/--row-mask, S the kind of --values-b/--row-mask-b (each defaults to F's). Both
// tile sets are copied to the card once, and each launch points the kernel at one kind's tiles and mask. The
// calibration launch (launch -1) and launch 0 take the order's first letter; launch n >= 1 takes letter (n - 1) mod 4
// of SFFS or FSSF; the process stops after exactly --launches launches after the calibration launch (or earlier, at
// the budget or the stop file: the records show it). Every record carries its kind.
//
// The card is shared: the device is open only while measuring; no launch starts unless it can end inside --budget
// seconds of holding the device (8 by default, at most 9), so the process ends under `timeout 10`; --seconds T
// repeats launches of about 0.5 s for T seconds; nothing more is launched once --stop-file exists.
// One card only: before anything is opened the host counts the card nodes (/dev/et<N>_ops). With one node it runs;
// with several it runs only when the device selection variable names one of them and the linked device layer reads
// that variable (the same test the lab's kits make on a binary); otherwise it refuses. After opening, the runtime must
// list exactly one device. The variable's name is assembled at run time, so this program's own text never contains it
// and a check of the binary for the name sees only the device layer's. (This rule follows request 1113-x01-intbits.)
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
#include <iterator>
#include <limits>
#include <map>
#include <random>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

#include "Constants.h"
#include "sparsity_args.h"

// libetrt's thread-pool workers log at the custom levels VERBOSE_HIGH/MID/LOW, which only logging::LoggerDefault
// registers with g3log. Left unregistered, the first log call from several new workers inserts the level into g3log's
// level map from all of them at once and can corrupt it (the lab's card-behaviour notes, "Traps": a host crash in about
// 1 launch in 100). Registering them before the runtime starts any thread removes the race.
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

struct Options {
  std::string values = "randn";  // file:<path> or a built-in fp32 pattern (zeros, ones, pi, randn)
  std::string label;
  std::string dumpTiles;
  std::string stopFile;
  int64_t rowMask = -1;   // -1: no MSK bit
  int64_t zeroRows = -1;  // -1: no read-back check of rows that must be +0.0
  int64_t liveRows = -1;  // -1: no read-back check of rows that must hold a non-zero word
  // the train's second kind (S); unset: S = F
  std::string valuesB, labelB;
  int64_t rowMaskB = -2;  // -2: as F's; -1: no MSK bit
  int64_t zeroRowsB = -2, liveRowsB = -2;
  std::string abba;
  uint64_t launches = 0;
  uint64_t iters = 0;
  uint64_t shireMask = 0xFFFFFFFFull;
  uint64_t perShire = 32;
  double seconds = 0;
  uint64_t seed = 1;
  double budget = 8.0;
  std::string kernel = KERNEL_ELF;
};

// ------------------------------------------------------------------------------------------ one card only

// The device selection variable's name, assembled at run time (see the header).
std::string selVarName() {
  const char rev[] = "SECIVED_TE";
  return std::string(std::rbegin(rev) + 1, std::rend(rev));
}

// The card nodes present, by index (/dev/et<N>_ops).
std::vector<int> cardNodes() {
  std::vector<int> v;
  std::error_code ec;
  for (const auto& e : fs::directory_iterator("/dev", ec)) {
    const std::string n = e.path().filename().string();
    if (n.size() < 7 || n.compare(0, 2, "et") != 0 || n.compare(n.size() - 4, 4, "_ops") != 0) continue;
    const std::string d = n.substr(2, n.size() - 6);
    if (d.empty() || d.find_first_not_of("0123456789") != std::string::npos) continue;
    v.push_back(std::stoi(d));
  }
  std::sort(v.begin(), v.end());
  return v;
}

// Whether this program's binary (the device layer is linked into it) carries the selection variable's name.
bool layerReadsSelection() {
  std::ifstream f("/proc/self/exe", std::ios::binary);
  if (!f) return false;
  const std::string bin((std::istreambuf_iterator<char>(f)), std::istreambuf_iterator<char>());
  return bin.find(selVarName()) != std::string::npos;
}

// Refuses (throws) unless exactly one card will be opened. Runs before any device is opened.
void checkOneCard() {
  const auto nodes = cardNodes();
  if (nodes.empty()) throw std::runtime_error("no card node /dev/et<N>_ops on this host");
  const std::string var = selVarName();
  const char* sel = std::getenv(var.c_str());
  if (sel && *sel) {
    const std::string s(sel);
    if (s.find_first_not_of("0123456789") != std::string::npos)
      throw std::runtime_error(var + " must be one card index, not '" + s + "'");
    if (std::find(nodes.begin(), nodes.end(), std::stoi(s)) == nodes.end())
      throw std::runtime_error(var + "=" + s + ": no such card node");
  }
  if (nodes.size() > 1) {
    if (!(sel && *sel))
      throw std::runtime_error(std::to_string(nodes.size()) + " cards on this host and " + var +
                               " unset: refusing to open every card");
    if (!layerReadsSelection())
      throw std::runtime_error("the linked device layer does not read " + var + ": it would open every card");
  }
}

// ------------------------------------------------------------------------------------------ the session

class Session {
public:
  Session(const Options& o, const std::vector<std::byte>& elf) : o_(o), tOpen_(Clock::now()) {
    // Ops node only: the power logger needs /dev/et0_mgmt, which allows one opener.
    dl_ = dev::IDeviceLayer::createPcieDeviceLayer(true, false);
    rt_ = rt::IRuntime::create(dl_);
    const auto devices = rt_->getDevices();
    if (devices.size() != 1) {
      throw std::runtime_error("the runtime lists " + std::to_string(devices.size()) + " devices, not one");
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

  double held() const {
    return secondsSince(tOpen_);
  }

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
    if (src) {
      rt_->memcpyHostToDevice(stream_, reinterpret_cast<const std::byte*>(src), ptr, bytes);
      rt_->waitForStream(stream_);
    }
    return reinterpret_cast<uint64_t>(ptr);
  }

  void get(const std::string& name, void* dst, size_t bytes) {
    rt_->memcpyDeviceToHost(stream_, buffers_.at(name).second, reinterpret_cast<std::byte*>(dst), bytes);
    rt_->waitForStream(stream_);
  }

  struct Launch {
    bool ok = false;
    double wallS = 0;
    long long t0Ms = 0, t1Ms = 0;
    std::vector<SpResult> res;
    double ghz = 0;  // longest kernel's cycles over the launch's wall time (meaningful for launches of 0.1 s+)
  };

  Launch launch(SpArgs a) {
    Launch L;
    std::vector<SpResult> zeros(2048);
    a.results = put("results", zeros.data(), zeros.size() * sizeof(SpResult));
    rt::KernelLaunchOptions opts;
    opts.setShireMask(a.shire_mask);
    opts.setBarrier(true);
    const int timeoutS = 6;
    L.t0Ms = epochMs();
    const auto t0 = Clock::now();
    rt_->kernelLaunch(stream_, kernel_, reinterpret_cast<const std::byte*>(&a), sizeof(a), opts);
    L.ok = rt_->waitForStream(stream_, std::chrono::seconds(timeoutS));
    L.wallS = secondsSince(t0);
    L.t1Ms = epochMs();
    if (!L.ok) {
      std::fprintf(stderr, "kernel did not finish within %d s, aborting the stream\n", timeoutS);
      rt_->waitForEvent(rt_->abortStream(stream_));
    }
    for (const auto& e : rt_->retrieveStreamErrors(stream_)) {
      std::fprintf(stderr, "stream error: %s\n", e.getString().c_str());
      L.ok = false;
    }
    L.res.resize(2048);
    get("results", L.res.data(), L.res.size() * sizeof(SpResult));
    uint64_t longest = 0;
    for (const auto& r : L.res) {
      if (r.magic == SP_MAGIC) {
        longest = std::max<uint64_t>(longest, r.t_exit - r.t_entry);
      }
    }
    L.ghz = L.wallS > 0 ? double(longest) / L.wallS / 1e9 : 0;
    return L;
  }

private:
  const Options& o_;
  Clock::time_point tOpen_;
  std::shared_ptr<dev::IDeviceLayer> dl_;
  rt::RuntimePtr rt_;
  rt::DeviceId dev_{};
  rt::StreamId stream_{};
  rt::KernelId kernel_{};
  std::map<std::string, std::pair<size_t, std::byte*>> buffers_;
};

// Hart IDs that run: hart 0 of minions 0..perShire-1 of every shire in the mask.
std::vector<uint64_t> participants(uint64_t shireMask, uint64_t perShire) {
  std::vector<uint64_t> out;
  for (uint64_t s = 0; s < 32; ++s) {
    if ((shireMask >> s) & 1) {
      for (uint64_t m = 0; m < perShire; ++m) {
        out.push_back(s * 64 + m * 2);
      }
    }
  }
  return out;
}

struct Summary {
  uint64_t reported = 0, bad = 0, cmax = 0, ops = 0;
  double cmean = 0;
  uint64_t tensorErrors = 0;
};

Summary summarize(const Session::Launch& L, const std::vector<uint64_t>& harts) {
  Summary s;
  double sum = 0;
  for (uint64_t h : harts) {
    const auto& r = L.res[h];
    if (r.magic != SP_MAGIC || r.hart != h) {
      ++s.bad;
      continue;
    }
    ++s.reported;
    s.cmax = std::max<uint64_t>(s.cmax, r.cycles);
    sum += double(r.cycles);
    s.ops += r.count;
    s.tensorErrors += r.tensor_error != 0;
  }
  s.cmean = s.reported ? sum / double(s.reported) : 0;
  return s;
}

/* ------------------------------------------------------------------------------------------ tiles */

// The fp32 A and B tiles (16 lines of 64 B each): a file (raw A then raw B, 1,024 bytes each, the layout of the lab
// host's --values file:) or a constant. The arms run files (the lab's own tile files for its kinds); the built-in
// randn here (std::mt19937_64(seed), a standard normal per element) is for the heater, and its values are not the
// lab host's built-in randn (that one draws its small-integer tiles from the same generator first).
void makeTiles(const Options& o, const std::string& mode, std::vector<uint8_t>& a, std::vector<uint8_t>& b) {
  a.assign(SP_TILE_BYTES, 0);
  b.assign(SP_TILE_BYTES, 0);
  if (mode.rfind("file:", 0) == 0) {
    std::ifstream f(mode.substr(5), std::ios::binary);
    f.read(reinterpret_cast<char*>(a.data()), std::streamsize(a.size()));
    f.read(reinterpret_cast<char*>(b.data()), std::streamsize(b.size()));
    if (!f) throw std::runtime_error("cannot read 2 x 1024 bytes of tiles from " + mode.substr(5));
    return;
  }
  std::mt19937_64 rng(o.seed);
  std::normal_distribution<float> n(0.f, 1.f);
  auto value = [&]() -> float {
    if (mode == "zeros") return 0.f;
    if (mode == "ones") return 1.f;
    if (mode == "pi") return 3.14159274f;
    if (mode == "randn") return n(rng);
    throw std::runtime_error("unknown --values " + mode + " (file:<path>, zeros, ones, pi, randn)");
  };
  for (auto* buf : {&a, &b}) {
    for (size_t off = 0; off + 4 <= buf->size(); off += 4) {
      const float f = value();
      std::memcpy(&(*buf)[off], &f, 4);
    }
  }
}

// One read-back of C over every participant: the words of the rows in `zeroRows` that are not zero, and the rows in
// `liveRows` whose 16 words are all zero (a word is zero when its magnitude bits are: +0.0 or -0.0; a zero A times a
// negative B leaves -0.0); a mask < 0: not counted, reported as -1.
struct CCheck {
  long long zeroBad = -1, liveZero = -1;
};

CCheck checkC(Session& dev, const std::vector<uint64_t>& harts, int64_t zeroRows, int64_t liveRows) {
  CCheck r;
  if (zeroRows < 0 && liveRows < 0) return r;
  std::vector<uint32_t> c(SP_MINIONS * 256);
  dev.get("out", c.data(), c.size() * 4);
  if (zeroRows >= 0) r.zeroBad = 0;
  if (liveRows >= 0) r.liveZero = 0;
  for (uint64_t h : harts) {
    const uint64_t m = h >> 1;
    for (int i = 0; i < 16; ++i) {
      int nz = 0;
      for (int j = 0; j < 16; ++j) nz += (c[m * 256 + i * 16 + j] & 0x7FFFFFFFu) != 0u;   // +0.0 and -0.0 are zero
      if (zeroRows >= 0 && ((zeroRows >> i) & 1)) r.zeroBad += nz;
      if (liveRows >= 0 && ((liveRows >> i) & 1)) r.liveZero += nz == 0;
    }
  }
  return r;
}

// A 16-bit mask, or "none" (-1).
int64_t maskOrNone(const std::string& v) {
  return v == "none" ? -1 : std::strtoll(v.c_str(), nullptr, 0);
}

std::string hex16(int64_t m) {
  if (m < 0) return "none";
  char t[8];
  std::snprintf(t, sizeof t, "0x%04llx", (unsigned long long)(m & 0xFFFF));
  return t;
}

struct Kind {
  std::string label, values;
  int64_t rowMask, zeroRows, liveRows;
  uint64_t aTile = 0, bTile = 0;
};

int run(const Options& o, Session& dev) {
  const auto harts = participants(o.shireMask, o.perShire);
  const bool train = !o.abba.empty();
  Kind F{o.label, o.values, o.rowMask, o.zeroRows, o.liveRows};
  Kind S = F;
  if (train) {
    if (!o.valuesB.empty()) S.values = o.valuesB;
    if (!o.labelB.empty()) S.label = o.labelB;
    if (o.rowMaskB != -2) S.rowMask = o.rowMaskB;
    if (o.zeroRowsB != -2) S.zeroRows = o.zeroRowsB;
    if (o.liveRowsB != -2) S.liveRows = o.liveRowsB;
  }
  std::vector<uint8_t> ta, tb;
  makeTiles(o, F.values, ta, tb);
  if (!o.dumpTiles.empty()) {
    std::ofstream f(o.dumpTiles, std::ios::binary);
    f.write(reinterpret_cast<const char*>(ta.data()), std::streamsize(ta.size()));
    f.write(reinterpret_cast<const char*>(tb.data()), std::streamsize(tb.size()));
  }
  F.aTile = dev.put("a", ta.data(), ta.size());
  F.bTile = dev.put("b", tb.data(), tb.size());
  if (train) {
    std::vector<uint8_t> sa, sb;
    makeTiles(o, S.values, sa, sb);
    if (!o.dumpTiles.empty()) {
      std::ofstream f(o.dumpTiles + ".S", std::ios::binary);
      f.write(reinterpret_cast<const char*>(sa.data()), std::streamsize(sa.size()));
      f.write(reinterpret_cast<const char*>(sb.data()), std::streamsize(sb.size()));
    }
    S.aTile = dev.put("a2", sa.data(), sa.size());
    S.bTile = dev.put("b2", sb.data(), sb.size());
  }
  SpArgs a{};
  a.mode = SP_FMA;
  a.shire_mask = o.shireMask;
  a.per_shire = o.perShire;
  a.type = SP_FP32;
  a.out = dev.put("out", nullptr, SP_MINIONS * SP_TILE_BYTES);
  a.b_stream = 0;
  // the kind of launch n (n = -1: the calibration launch)
  auto kindOf = [&](int n) -> char {
    if (!train) return 'F';
    return n < 1 ? o.abba[0] : o.abba[size_t((n - 1) % 4)];
  };
  int bad = 0;
  auto one = [&](uint64_t iters, int launchNo) -> double {
    const char k = kindOf(launchNo);
    const Kind& K = k == 'S' ? S : F;
    a.a_tile = K.aTile;
    a.b_tile = K.bTile;
    a.use_mask = K.rowMask >= 0;
    a.mask = K.rowMask >= 0 ? uint64_t(K.rowMask) & 0xFFFF : 0xFFFF;
    a.iters = iters;
    const auto L = dev.launch(a);
    const Summary sm = summarize(L, harts);
    const bool ok = L.ok && sm.bad == 0 && sm.tensorErrors == 0;
    bad += !ok;
    std::printf("X14 {\"label\":\"%s\",\"values\":\"%s\",\"row_mask\":\"%s\",\"kind\":\"%c\",\"abba\":\"%s\","
                "\"minions\":%zu,\"shire_mask\":\"0x%llx\",\"iters\":%llu,\"launch\":%d,\"ops\":%llu,"
                "\"cycles_max\":%llu,\"cycles_mean\":%.1f,\"cycles_per_op\":%.3f,\"wall_s\":%.6f,\"t_start_ms\":%lld,"
                "\"t_end_ms\":%lld,\"ghz\":%.4f,\"tensor_errors\":%llu,\"ok\":%s}\n",
                K.label.c_str(), K.values.c_str(), hex16(K.rowMask).c_str(), train ? k : '-', train ? o.abba.c_str() : "",
                harts.size(), (unsigned long long)o.shireMask, (unsigned long long)iters, launchNo,
                (unsigned long long)sm.ops, (unsigned long long)sm.cmax, sm.cmean,
                iters ? sm.cmean / double(iters) : 0.0, L.wallS, L.t0Ms, L.t1Ms, L.ghz,
                (unsigned long long)sm.tensorErrors, ok ? "true" : "false");
    std::fflush(stdout);
    return L.ok ? L.wallS : -1.0;
  };
  // the read-back after a launch (only after the first and the last launch of the process)
  auto check = [&](int launchNo) {
    const char k = kindOf(launchNo);
    const Kind& K = k == 'S' ? S : F;
    const CCheck c = checkC(dev, harts, K.zeroRows, K.liveRows);
    const bool ok = c.zeroBad <= 0 && c.liveZero <= 0;
    bad += !ok;
    std::printf("X14CHECK {\"label\":\"%s\",\"kind\":\"%c\",\"after_launch\":%d,\"zero_rows\":\"%s\","
                "\"live_rows\":\"%s\",\"zero_rows_bad\":%lld,\"live_rows_zero\":%lld,\"ok\":%s}\n",
                K.label.c_str(), train ? k : '-', launchNo, hex16(K.zeroRows).c_str(), hex16(K.liveRows).c_str(),
                c.zeroBad, c.liveZero, ok ? "true" : "false");
    std::fflush(stdout);
  };
  // A calibration launch, then launches of about 0.5 s: for --seconds, or exactly --launches of them in a train; no
  // launch starts unless it can end inside --budget seconds of holding the device.
  uint64_t iters = o.iters ? o.iters : 20000;
  double wall = one(iters, -1);
  if (wall < 0) return 1;
  check(-1);
  int last = -1;
  if (o.seconds > 0 || train) {
    iters = std::max<uint64_t>(1, uint64_t(double(iters) * 0.5 / std::max(wall, 1e-4)));
    double spent = 0;
    for (int n = 0; train ? uint64_t(n) < o.launches : spent < o.seconds; ++n) {
      if (dev.held() + 1.2 * wall > o.budget || dev.held() + 0.7 > o.budget) {
        std::fprintf(stderr, "stopping: the next launch would end after the %.1f s budget\n", o.budget);
        break;
      }
      if (!o.stopFile.empty() && fs::exists(o.stopFile)) {
        std::fprintf(stderr, "stopping: %s exists\n", o.stopFile.c_str());
        break;
      }
      wall = one(iters, n);
      if (wall < 0) break;
      last = n;
      spent += wall;
    }
  }
  if (last >= 0) check(last);
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
    if (a == "--values") o.values = next();
    else if (a == "--label") o.label = next();
    else if (a == "--dump-tiles") o.dumpTiles = next();
    else if (a == "--stop-file") o.stopFile = next();
    else if (a == "--row-mask") o.rowMask = std::strtoll(next().c_str(), nullptr, 0);
    else if (a == "--zero-rows") o.zeroRows = std::strtoll(next().c_str(), nullptr, 0);
    else if (a == "--live-rows") o.liveRows = std::strtoll(next().c_str(), nullptr, 0);
    else if (a == "--values-b") o.valuesB = next();
    else if (a == "--label-b") o.labelB = next();
    else if (a == "--row-mask-b") o.rowMaskB = maskOrNone(next());
    else if (a == "--zero-rows-b") o.zeroRowsB = maskOrNone(next());
    else if (a == "--live-rows-b") o.liveRowsB = maskOrNone(next());
    else if (a == "--abba") o.abba = next();
    else if (a == "--launches") o.launches = std::strtoull(next().c_str(), nullptr, 0);
    else if (a == "--iters") o.iters = std::strtoull(next().c_str(), nullptr, 0);
    else if (a == "--shires") o.shireMask = std::strtoull(next().c_str(), nullptr, 0);
    else if (a == "--per-shire") o.perShire = std::strtoull(next().c_str(), nullptr, 0);
    else if (a == "--seconds") o.seconds = std::atof(next().c_str());
    else if (a == "--seed") o.seed = std::strtoull(next().c_str(), nullptr, 0);
    else if (a == "--budget") o.budget = std::atof(next().c_str());
    else if (a == "--kernel") o.kernel = next();
    else {
      std::fprintf(stderr, "unknown option %s (see the comment at the top of host/main.cpp)\n", a.c_str());
      return 2;
    }
  }
  if (o.budget <= 0 || o.budget > 9.0) {
    std::fprintf(stderr, "--budget must be in (0, 9] seconds\n");
    return 2;
  }
  if (o.shireMask == 0 || (o.shireMask >> 32) || o.perShire == 0 || o.perShire > 32) {
    std::fprintf(stderr, "bad --shires / --per-shire\n");
    return 2;
  }
  if (o.rowMask > 0xFFFF || o.zeroRows > 0xFFFF || o.liveRows > 0xFFFF || o.rowMaskB > 0xFFFF ||
      o.zeroRowsB > 0xFFFF || o.liveRowsB > 0xFFFF) {
    std::fprintf(stderr, "row masks are 16-bit masks\n");
    return 2;
  }
  const bool trainOpt = !o.valuesB.empty() || !o.labelB.empty() || o.rowMaskB != -2 || o.zeroRowsB != -2 ||
                        o.liveRowsB != -2 || o.launches > 0 || !o.abba.empty();
  if (trainOpt) {
    if (o.abba != "SFFS" && o.abba != "FSSF") {
      std::fprintf(stderr, "a train needs --abba SFFS or FSSF\n");
      return 2;
    }
    if (o.launches == 0 || o.launches > 16) {
      std::fprintf(stderr, "a train needs --launches N (1..16)\n");
      return 2;
    }
    if (o.seconds > 0) {
      std::fprintf(stderr, "a train takes --launches, not --seconds\n");
      return 2;
    }
  }
  const auto elf = readFile(o.kernel);
  if (elf.empty()) {
    std::fprintf(stderr, "cannot read kernel %s\n", o.kernel.c_str());
    return 1;
  }
  try {
    checkOneCard();
    Session dev(o, elf);
    return run(o, dev);
  } catch (const std::exception& e) {
    std::fprintf(stderr, "FAIL: %s\n", e.what());
    return 1;
  }
}
