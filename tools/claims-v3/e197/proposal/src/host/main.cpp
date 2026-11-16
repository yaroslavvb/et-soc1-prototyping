// regfile: the integer register file's reads and writes (host program).
//
// Every participating hart (hart 0 of every minion by default) runs one loop form: a fixed stream of 128 32-bit
// integer instructions with no load and no store, flat out until a cycle deadline, on the register values of one
// kind (make_images.py: forms, images, designed counts; regfile_kinds.h is generated from it). Energy per instruction
// is what one kind costs over another kind of the same issue, divided by the rate. Every launch prints one line
//   REGFILE {json}
//
//   regfile_host --kind NAME [--seconds S | --launches N]      bursts of one kind, launches back to back
//   regfile_host --train F,S --orient SFFS|FSSF [--launches 13] an A B B A train in one process: launch 0 settles
//                                                               with the orientation's first letter, launch n >= 1
//                                                               takes letter (n - 1) mod 4 (F = the first kind)
//   regfile_host --kinds A,B,... [--launches N]                 a suite: each kind launched N times (1 by default)
//   regfile_host --list [--json]                                the kind table (no device)
//   common: [--window CYCLES] [--harts 1|2] [--shires MASK] [--minions MASK] [--budget S] [--stop-file PATH]
//
// The card is shared: each launch runs `window` cycles (0.4 s at 600 MHz by default; at most 1.2e9) and no launch
// starts unless it can end inside --budget seconds of holding the device (8.5 by default, at most 9), in every mode,
// so the process ends under `timeout 10`; nothing more is launched once the --stop-file exists (checked before every
// launch). One card only: before anything is opened the host counts the card nodes (/dev/et<N>_ops). With one node it
// runs; with several it runs only when the device selection variable names one of them and the linked device layer
// reads that variable (the same test the lab's kits make on a binary); otherwise it refuses. After opening, the
// runtime must list exactly one device. The variable's name is assembled at run time, so this program's own text
// never contains it and a check of the binary for the name sees only the device layer's.
//
// Session code follows the public lab repo's workloads/enercat/host/main.cpp.
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
#include <iterator>
#include <map>
#include <sstream>
#include <string>
#include <system_error>
#include <vector>

#include "Constants.h"
#include "regfile_args.h"
#include "regfile_kinds.h"

// The runtime's worker threads log at three custom levels that only the default logger registers. Registering them
// before the runtime starts any thread avoids a race in the logging library's level map (a rare host crash).
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

std::string hex(uint64_t x) {
  char b[24];
  std::snprintf(b, sizeof b, "0x%016llx", (unsigned long long)x);
  return b;
}

int findKind(const std::string& n) {
  for (int i = 0; i < RF_NKINDS; ++i)
    if (n == RF_KINDS[i].name) return i;
  throw std::runtime_error("unknown kind " + n + " (see --list)");
}

std::string kindJson(const RfKind& k) {
  std::ostringstream o;
  o << "\"kind\":\"" << k.name << "\",\"form_id\":" << k.form << ",\"per_instr\":{";
  for (int i = 0; i < RF_NCOUNTS; ++i) o << (i ? "," : "") << "\"" << RF_COUNT_KEYS[i] << "\":" << k.per_instr[i];
  o << "}";
  return o.str();
}
std::string kindRegsJson(const RfKind& k) {
  std::ostringstream o;
  o << "\"regs\":{";
  bool first = true;
  for (int r = 0; r < 32; ++r)
    if ((k.named >> r) & 1) {
      o << (first ? "" : ",") << "\"x" << r << "\":\"" << hex(k.regs[r]) << "\"";
      first = false;
    }
  o << "}";
  return o.str();
}

// ---------------------------------------------------------------------------------------------------------------
// Device session (as in the public lab repo's enercat host)
// ---------------------------------------------------------------------------------------------------------------

struct Options {
  bool json = false, list = false;
  std::string kind, kinds, train, orient = "SFFS", kernel = KERNEL_ELF;
  uint64_t harts = 1, shireMask = 0xffffffff, minionMask = 0, window = 240000000;
  double seconds = 4.0, budget = 8.5;
  std::string stopFile;  // no further launch once this file exists
  int launches = 0;      // 0: as many as fit in --seconds (bursts), 13 (train), 1 (suite)
};

class Session {
public:
  Session(const Options& o, const std::vector<std::byte>& elf, const std::vector<int>& kinds)
      : o_(o), tOpen_(Clock::now()) {
    dl_ = dev::IDeviceLayer::createPcieDeviceLayer(true, false);  // ops node only
    rt_ = rt::IRuntime::create(dl_);
    const auto devices = rt_->getDevices();
    if (devices.empty()) throw std::runtime_error("no ET devices found");
    if (devices.size() > 1) throw std::runtime_error("more than one device: this host is for a one-card machine");
    dev_ = devices[0];
    stream_ = rt_->createStream(dev_);
    const auto load = rt_->loadCode(stream_, elf.data(), elf.size());
    rt_->waitForEvent(load.event_);
    kernel_ = load.kernel_;
    results_ = rt_->mallocDevice(dev_, RF_MAX_HARTS * sizeof(RfResult));
    // Each kind's register image goes to the card once; a launch points at one of them.
    for (int k : kinds) {
      if (images_.count(k)) continue;
      std::byte* p = rt_->mallocDevice(dev_, 32 * sizeof(uint64_t));
      rt_->memcpyHostToDevice(stream_, reinterpret_cast<const std::byte*>(RF_KINDS[k].regs), p, 32 * sizeof(uint64_t));
      rt_->waitForStream(stream_);
      images_[k] = p;
    }
    std::fprintf(stderr, "device ready in %.2f s\n", secondsSince(tOpen_));
  }
  ~Session() {
    for (auto& kv : images_) rt_->freeDevice(dev_, kv.second);
    rt_->freeDevice(dev_, results_);
    rt_->unloadCode(kernel_);
    rt_->destroyStream(stream_);
    std::fprintf(stderr, "device held for %.2f s\n", secondsSince(tOpen_));
  }
  // Whether one more launch (its cycles at the slowest clock considered, 500 MHz, plus 1 s of slack for the copies and
  // a possible abort) still ends inside the budget.
  bool launchFits() const { return secondsSince(tOpen_) + double(o_.window) / 0.5e9 + 1.0 <= o_.budget; }
  long long t0Ms = 0, t1Ms = 0;  // epoch bounds of the last launch, for lining up with power samples
  bool launch(int k, std::vector<RfResult>& res, double& wallS) {
    res.assign(RF_MAX_HARTS, RfResult{});
    rt_->memcpyHostToDevice(stream_, reinterpret_cast<const std::byte*>(res.data()), results_,
                            res.size() * sizeof(RfResult));
    rt_->waitForStream(stream_);
    RfArgs a{};
    a.form = (uint64_t)RF_KINDS[k].form;
    a.shire_mask = o_.shireMask;
    a.minion_mask = o_.minionMask;
    a.harts = o_.harts;
    a.window = o_.window;
    a.results = reinterpret_cast<uint64_t>(results_);
    a.image = reinterpret_cast<uint64_t>(images_.at(k));
    rt::KernelLaunchOptions opts;
    opts.setShireMask(o_.shireMask);
    opts.setBarrier(true);
    const int timeoutS = 3;  // a launch is at most 1.2e9 cycles: 2.4 s at 500 MHz
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
    rt_->memcpyDeviceToHost(stream_, results_, reinterpret_cast<std::byte*>(res.data()), res.size() * sizeof(RfResult));
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
  std::map<int, std::byte*> images_;
};

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

// One launch of one kind; prints one REGFILE line. Returns false on a failed launch or a failed check.
bool runOnce(const Options& o, Session& dev, int k, int idx, char letter) {
  std::vector<RfResult> res;
  double wallS = 0;
  const bool ok = dev.launch(k, res, wallS);
  const RfKind& K = RF_KINDS[k];
  uint64_t n = 0, iters = 0, cmax = 0, bad = 0, raDiff = 0, imin = ~0ull, imax = 0;
  double csum = 0;
  uint64_t ret = 0, icr = 0, icm = 0, l1m = 0, ra = 0, gp = 0, dl = 0;
  std::vector<bool> nbSeen(RF_MAX_HARTS / 16, false);
  for (const auto& r : res) {
    if (r.magic != RF_MAGIC) continue;
    if (!n) { ra = r.ra; gp = r.gp; dl = r.deadline; }
    else if (r.ra != ra || r.gp != gp) ++raDiff;
    ++n;
    iters += r.iters;
    imin = std::min<uint64_t>(imin, r.iters);  // the spread of iterations over the harts: a hart that left its loop
    imax = std::max<uint64_t>(imax, r.iters);  // early, or ran slow, shows here (the rate sees only the sum)
    cmax = std::max<uint64_t>(cmax, r.cycles);
    csum += double(r.cycles);
    // Every register the form writes holds the value the kind's model says after a whole body.
    for (int x = 0; x < 32; ++x)
      if (((K.written >> x) & 1) && r.regs[x] != K.end[x]) { ++bad; break; }
    // The minion counters are neighbourhood sums: count each neighbourhood (16 harts) once.
    const uint32_t nb = r.hart / 16;
    if (nb < nbSeen.size() && !nbSeen[nb]) {
      nbSeen[nb] = true;
      ret += r.ret1 - r.ret0; icr += r.icr1 - r.icr0; icm += r.icm1 - r.icm0; l1m += r.l1m1 - r.l1m0;
    }
  }
  const double instr = double(iters) * RF_PER_ITER;
  const double secs = cmax / 0.6e9;  // device seconds at the 600 MHz the reference card is pinned to
  std::printf("REGFILE {%s,\"launch\":%d,\"letter\":\"%c\",\"orient\":\"%s\",\"harts\":%llu,\"participants\":%llu,"
              "\"iters\":%llu,\"iters_min\":%llu,\"iters_max\":%llu,\"instr_body\":%.0f,\"retired_counter\":%llu,\"icache_req\":%llu,\"icache_miss\":%llu,"
              "\"l1d_miss\":%llu,\"cycles_max\":%llu,\"cycles_mean\":%.0f,\"instr_per_cycle_per_hart\":%.4f,"
              "\"instr_per_s_600\":%.4e,\"ra\":\"%s\",\"gp\":\"%s\",\"deadline\":\"%s\",\"ra_gp_differ\":%llu,"
              "\"window\":%llu,\"wall_s\":%.4f,\"t_start_ms\":%lld,\"t_end_ms\":%lld,\"check_bad\":%llu,\"ok\":%s}\n",
              kindJson(K).c_str(), idx, letter, letter == '-' ? "" : o.orient.c_str(), (unsigned long long)o.harts,
              (unsigned long long)n, (unsigned long long)iters, (unsigned long long)(n ? imin : 0),
              (unsigned long long)imax, instr, (unsigned long long)ret, (unsigned long long)icr,
              (unsigned long long)icm, (unsigned long long)l1m, (unsigned long long)cmax, n ? csum / double(n) : 0.0,
              (cmax && n) ? instr / double(cmax) / double(n) : 0.0, secs > 0 ? instr / secs : 0.0, hex(ra).c_str(),
              hex(gp).c_str(), hex(dl).c_str(), (unsigned long long)raDiff, (unsigned long long)o.window, wallS,
              dev.t0Ms, dev.t1Ms, (unsigned long long)bad, (ok && n && !bad) ? "true" : "false");
  std::fflush(stdout);
  return ok && n && !bad;
}

uint64_t parseU(const std::string& s) { return std::strtoull(s.c_str(), nullptr, 0); }

std::vector<int> splitKinds(const std::string& s) {
  std::vector<int> v;
  std::stringstream ss(s);
  for (std::string n; std::getline(ss, n, ',');) v.push_back(findKind(n));
  return v;
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
    if (a == "--kind") o.kind = next();
    else if (a == "--kinds") o.kinds = next();
    else if (a == "--train") o.train = next();
    else if (a == "--orient") o.orient = next();
    else if (a == "--harts") o.harts = parseU(next());
    else if (a == "--shires") o.shireMask = parseU(next());
    else if (a == "--minions") o.minionMask = parseU(next());
    else if (a == "--window") o.window = parseU(next());
    else if (a == "--seconds") o.seconds = std::strtod(next().c_str(), nullptr);
    else if (a == "--budget") o.budget = std::strtod(next().c_str(), nullptr);
    else if (a == "--launches") o.launches = (int)parseU(next());
    else if (a == "--kernel") o.kernel = next();
    else if (a == "--stop-file") o.stopFile = next();
    else if (a == "--list") o.list = true;
    else if (a == "--json") o.json = true;
    else { std::fprintf(stderr, "unknown option %s\n", a.c_str()); return 2; }
  }
  if (o.list) {
    for (int k = 0; k < RF_NKINDS; ++k) {
      const RfKind& K = RF_KINDS[k];
      if (o.json) std::printf("{%s,%s}\n", kindJson(K).c_str(), kindRegsJson(K).c_str());
      else {
        std::printf("%-11s form %2d", K.name, K.form);
        for (int i = 0; i < RF_NCOUNTS; ++i) std::printf(" %s %.2f", RF_COUNT_KEYS[i], K.per_instr[i]);
        std::printf("\n");
      }
    }
    return 0;
  }
  try {
    const int modes = !o.kind.empty() + !o.kinds.empty() + !o.train.empty();
    if (modes != 1) throw std::runtime_error("give exactly one of --kind, --kinds, --train (or --list)");
    std::vector<int> todo;
    if (!o.kind.empty()) todo.push_back(findKind(o.kind));
    if (!o.kinds.empty()) todo = splitKinds(o.kinds);
    if (!o.train.empty()) {
      todo = splitKinds(o.train);
      if (todo.size() != 2) throw std::runtime_error("--train takes two kinds: F,S");
      if (o.orient != "SFFS" && o.orient != "FSSF") throw std::runtime_error("--orient must be SFFS or FSSF");
      if (RF_KINDS[todo[0]].form < 1 || RF_KINDS[todo[1]].form < 1) throw std::runtime_error("bad kind");
    }
    if (o.harts > 1) std::fprintf(stderr, "note: --harts 2 interleaves two streams in one pipeline; designed counts assume 1\n");
    if (o.window == 0 || o.window > 1200000000ull) throw std::runtime_error("--window must be 1 .. 1200000000 cycles");
    if (!(o.budget > 0 && o.budget <= 9.0)) throw std::runtime_error("--budget must be in (0, 9] seconds");
    checkOneCard();  // before anything opens a device
    const auto elf = readFile(o.kernel);
    if (elf.empty()) throw std::runtime_error("cannot read kernel " + o.kernel);
    Session dev(o, elf, todo);
    auto stopped = [&]() { return !o.stopFile.empty() && fs::exists(o.stopFile); };
    if (!o.train.empty()) {
      // The lab's train form: launch 0 settles with the orientation's first letter; launch n >= 1 takes letter
      // (n - 1) mod 4 of the orientation; F is the first kind, S the second. Exactly --launches (13) or nothing.
      const int L = o.launches ? o.launches : 13;
      for (int n = 0; n < L; ++n) {
        if (stopped() || !dev.launchFits()) {
          std::fprintf(stderr, "train ended early at launch %d (stop file or --budget): this process gives no value\n", n);
          return 3;
        }
        const char letter = n == 0 ? o.orient[0] : o.orient[(n - 1) % 4];
        if (!runOnce(o, dev, letter == 'F' ? todo[0] : todo[1], n, letter)) return 1;
      }
      return 0;
    }
    int bad = 0;
    if (todo.size() > 1) {  // a suite: each kind launched --launches times (1 by default), one session, same limits
      const auto tStart = Clock::now();
      int idx = 0;
      for (int k : todo)
        for (int r = 0; r < std::max(1, o.launches); ++r) {
          if (stopped() || !dev.launchFits() || secondsSince(tStart) >= o.seconds) {
            std::fprintf(stderr, "suite ended early (stop file, --budget or --seconds): later kinds not run\n");
            return 3;
          }
          bad += !runOnce(o, dev, k, idx++, '-');
        }
    } else {
      const auto tStart = Clock::now();
      int n = 0;
      while ((o.launches ? n < o.launches : secondsSince(tStart) < o.seconds) && dev.launchFits() && !stopped()) {
        if (!runOnce(o, dev, todo[0], n, '-')) { ++bad; break; }
        ++n;
      }
    }
    return bad ? 1 : 0;
  } catch (const std::exception& e) {
    std::fprintf(stderr, "FAIL: %s\n", e.what());
    return 1;
  }
}
