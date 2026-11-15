// intbits: scalar integer bit-flip and carry ladders (host program).
//
// Every participating hart (hart 0 of every minion by default) runs one fixed stream of 32-bit integer
// instructions with no load and no store, flat out until a cycle deadline, while the host's power logger runs.
// Energy per instruction is what is left over idle (or over the arm's control) divided by the rate.
// Every launch prints one line
//   INTBITS {json}
//
//   intbits_host --arm NAME [--seconds S] [--window CYCLES] [--harts 1|2] [--shires MASK] [--minions MASK]
//                [--stop-file PATH]   (no further launch once PATH exists; checked before every 0.4 s launch)
//   intbits_host --form pair|split|same|nop --op add|xor|sub|and|or --a0 V --b0 V --a1 V --b1 V   (a custom arm)
//   intbits_host --arms all|NAME,NAME,... [--launches N]   (a suite: each arm launched N times, one process)
//   intbits_host --list [--json]                      (the arm table with values and designed counts)
//
// The card is shared: each launch runs `window` cycles (0.4 s at 600 MHz by default; at most 1.2e9) and no launch
// starts unless it can end inside --budget seconds of holding the device (8.5 by default, at most 9), in every mode,
// so the process ends under `timeout 10`; --seconds (4 by default) ends a single arm's run first.
// One card only: before anything is opened the host counts the card nodes (/dev/et<N>_ops). With one node it runs;
// with several it runs only when the device selection variable names one of them and the linked device layer reads
// that variable (the same test the lab's kits make on a binary); otherwise it refuses. After opening, the runtime must
// list exactly one device. The variable's name is assembled at run time, so this program's own text never contains it
// and a check of the binary for the name sees only the device layer's.
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
#include <limits>
#include <map>
#include <random>
#include <sstream>
#include <string>
#include <system_error>
#include <vector>

#include "Constants.h"
#include "intbits_args.h"

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
int pop(uint64_t x) { return __builtin_popcountll(x); }

// ---------------------------------------------------------------------------------------------------------------
// Arms
// ---------------------------------------------------------------------------------------------------------------

struct Arm {
  std::string name;
  uint64_t form, op;
  uint64_t a0, b0, a1, b1;
  std::string note;
};

const char* opName(uint64_t op) {
  switch (op) {
  case IB_ADD: return "add";
  case IB_XOR: return "xor";
  case IB_SUB: return "sub";
  case IB_AND: return "and";
  case IB_OR: return "or";
  default: return "nop";
  }
}
const char* formName(uint64_t f) {
  switch (f) {
  case IB_NOP: return "nop";
  case IB_SAME: return "same";
  case IB_PAIR: return "pair";
  case IB_SPLIT: return "split";
  default: return "?";
  }
}
uint64_t apply(uint64_t op, uint64_t a, uint64_t b) {
  switch (op) {
  case IB_ADD: return a + b;
  case IB_XOR: return a ^ b;
  case IB_SUB: return a - b;
  case IB_AND: return a & b;
  case IB_OR: return a | b;
  default: return 0;
  }
}
// R-type encoding (RV64I, opcode OP): funct7 | rs2 | rs1 | funct3 | rd | 0110011
uint32_t encode(uint64_t op, uint32_t rd, uint32_t rs1, uint32_t rs2) {
  uint32_t f3 = 0, f7 = 0;
  switch (op) {
  case IB_ADD: break;
  case IB_SUB: f7 = 0x20; break;
  case IB_XOR: f3 = 4; break;
  case IB_OR: f3 = 6; break;
  case IB_AND: f3 = 7; break;
  default: return 0x00000013u;  // addi x0, x0, 0
  }
  return (f7 << 25) | (rs2 << 20) | (rs1 << 15) | (f3 << 12) | (rd << 7) | 0x33u;
}

// Bits that change between neighbouring instructions, by design (per instruction, in the steady stream).
struct Counts {
  int portA = 0, portB = 0, result = 0, carry = 0, cell = 0, enc = 0;
  uint64_t r0 = 0, r1 = 0;
};
Counts designed(const Arm& m) {
  Counts c;
  if (m.form == IB_NOP) return c;
  c.r0 = apply(m.op, m.a0, m.b0);
  c.r1 = apply(m.op, m.a1, m.b1);
  if (m.form == IB_SAME) { c.r1 = c.r0; return c; }
  c.portA = pop(m.a0 ^ m.a1);
  c.portB = pop(m.b0 ^ m.b1);
  c.result = pop(c.r0 ^ c.r1);
  if (m.op == IB_ADD) {  // carry-in vector of each addition: (a + b) ^ a ^ b
    const uint64_t cv0 = (m.a0 + m.b0) ^ m.a0 ^ m.b0, cv1 = (m.a1 + m.b1) ^ m.a1 ^ m.b1;
    c.carry = pop(cv0 ^ cv1);
  }
  c.cell = m.form == IB_PAIR ? c.result : 0;  // one destination: its stored bits change with the result
  const uint32_t rdB = m.form == IB_SPLIT ? 30 : 5;
  c.enc = pop(encode(m.op, 5, 6, 7) ^ encode(m.op, rdB, 28, 29));
  return c;
}

// The arm table. Background bits are fixed random values (from --seed) that never change within an arm; every
// pattern keeps the two sources' ones disjoint wherever no carry is wanted, so an add there has no carries at all
// and its result equals the xor (and the or); an and of the two sources is zero throughout.
uint64_t field(int f) { return 0xFFFFull << (16 * f); }
std::vector<Arm> armTable(uint64_t seed) {
  std::mt19937_64 rng(seed);
  const uint64_t X = rng(), Yr = rng();
  const uint64_t Y = Yr & ~X;  // disjoint from X
  std::vector<Arm> v;
  auto shapeA = [&](const std::string& n, uint64_t op, uint64_t M, uint64_t form = IB_PAIR) {
    const uint64_t a = X & ~M, b = Y & ~M;
    v.push_back({n, form, op, a, b, a | M, b, "port A and the result change in the masked bits; port B held"});
  };
  auto shapeB = [&](const std::string& n, uint64_t op, uint64_t M) {
    const uint64_t a = X & ~M, b = Y & ~M;
    v.push_back({n, IB_PAIR, op, a, b, a, b | M, "port B and the result change in the masked bits; port A held"});
  };
  auto shapeS = [&](const std::string& n, uint64_t op, uint64_t M) {
    const uint64_t a = X & ~M, b = Y & ~M;
    v.push_back({n, IB_PAIR, op, a | M, b, a, b | M, "the masked bits move from port A to port B; result constant"});
  };
  // Result-held carry ladder: instruction A adds (a run of L ones from bit s) + (one at bit s), which carries L
  // positions to bit s+L; instruction B adds (one at bit s+L) + 0. Both results are equal, so the result is held while
  // the carry runs L positions; port A changes in L+1 bits (s..s+L), port B in one (bit s).
  auto carryR = [&](const std::string& n, uint64_t op, int s, int L) {
    const uint64_t span = (L + 1 >= 64 ? ~0ull : ((1ull << (L + 1)) - 1)) << s;
    const uint64_t a = X & ~span, b = Y & ~span;
    const uint64_t run = (L ? ((1ull << L) - 1) : 0ull) << s;
    v.push_back({n, IB_PAIR, op, a | run, b | (1ull << s), a | (1ull << (s + L)), b,
                 "result-held carry ladder: A = run of L ones from bit s plus one at bit s, B = one at bit s+L plus 0"});
  };
  // Port-held carry ladder: port A holds a run of L ones from bit s in both instructions; port B alternates 0 and one
  // at bit s. Port A changes in no bit, port B in one; the carry runs L positions and the result changes in L+1 bits.
  auto carryB = [&](const std::string& n, uint64_t op, int s, int L) {
    const uint64_t span = (L + 1 >= 64 ? ~0ull : ((1ull << (L + 1)) - 1)) << s;
    const uint64_t a = X & ~span, b = Y & ~span;
    const uint64_t run = (L ? ((1ull << L) - 1) : 0ull) << s;
    v.push_back({n, IB_PAIR, op, a | run, b, a | run, b | (1ull << s),
                 "port-held carry ladder: A = run of L ones from bit s in both, B = 0 then one at bit s"});
  };
  v.push_back({"nop", IB_NOP, IB_NOPS, 0, 0, 0, 0, "the no-op sled: 32-bit nop"});
  v.push_back({"add.same", IB_SAME, IB_ADD, X, Y, X, Y, "one add repeated, constant sources"});
  v.push_back({"add.z", IB_PAIR, IB_ADD, X, Y, X, Y, "two adds alternating, equal sources: the add ladders' zero rung"});
  v.push_back({"xor.z", IB_PAIR, IB_XOR, X, Y, X, Y, "two xors alternating, equal sources: the xor arm's zero rung"});
  v.push_back({"and.z", IB_PAIR, IB_AND, X, Y, X, Y, "two ands alternating, equal sources: the and arms' zero rung"});
  // Hamming ladder on port A (the result follows): position (16-bit fields) and count (4, 8, 16 bits in field 2;
  // 32 = fields 1 and 2; 64 = all).
  for (int f = 0; f < 4; ++f) shapeA("add.a.f" + std::to_string(f), IB_ADD, field(f));
  shapeA("add.a.f2.k4", IB_ADD, 0xFull << 32);
  shapeA("add.a.f2.k8", IB_ADD, 0xFFull << 32);
  shapeA("add.a.f12", IB_ADD, field(1) | field(2));
  shapeA("add.a.all", IB_ADD, ~0ull);
  shapeB("add.b.f0", IB_ADD, field(0));
  shapeB("add.b.f2", IB_ADD, field(2));
  shapeS("add.s.f0", IB_ADD, field(0));
  shapeS("add.s.f2", IB_ADD, field(2));
  shapeA("xor.a.f2", IB_XOR, field(2));
  // Result-held and: port A changes in a field where port B is zero, so the and (the result) stays 0.
  for (int f = 1; f < 4; ++f) shapeA("and.a.f" + std::to_string(f), IB_AND, field(f));
  for (int L : {0, 8, 16, 24, 31}) carryR("add.cr.l" + std::to_string(L), IB_ADD, 16, L);
  for (int L : {0, 8, 16, 24, 31}) carryB("add.crb.l" + std::to_string(L), IB_ADD, 16, L);
  v.push_back({"add.ripple", IB_PAIR, IB_ADD, ~0ull, 0, ~0ull, 1,
               "all ones plus zero, then all ones plus one: a carry through every position, every result bit flips"});
  return v;
}

std::string hex(uint64_t x) {
  char b[24];
  std::snprintf(b, sizeof b, "0x%016llx", (unsigned long long)x);
  return b;
}
std::string armJson(const Arm& m) {
  const Counts c = designed(m);
  std::ostringstream o;
  o << "\"arm\":\"" << m.name << "\",\"form\":\"" << formName(m.form) << "\",\"op\":\"" << opName(m.op)
    << "\",\"a0\":\"" << hex(m.a0) << "\",\"b0\":\"" << hex(m.b0) << "\",\"a1\":\"" << hex(m.a1) << "\",\"b1\":\""
    << hex(m.b1) << "\",\"r0\":\"" << hex(c.r0) << "\",\"r1\":\"" << hex(c.r1) << "\",\"n_port_a\":" << c.portA
    << ",\"n_port_b\":" << c.portB << ",\"n_result\":" << c.result << ",\"n_carry\":" << c.carry
    << ",\"n_cell\":" << c.cell << ",\"n_enc\":" << c.enc;
  return o.str();
}

// ---------------------------------------------------------------------------------------------------------------
// Device session (as in the public lab repo's enercat host)
// ---------------------------------------------------------------------------------------------------------------

struct Options {
  bool json = false, list = false;
  std::string arm, arms, kernel = KERNEL_ELF;
  std::string form, op;
  uint64_t a0 = 0, b0 = 0, a1 = 0, b1 = 0;
  uint64_t harts = 1, shireMask = 0xffffffff, minionMask = 0, window = 240000000, seed = 1;
  double seconds = 4.0, budget = 8.5;
  std::string stopFile;  // no further launch once this file exists
  int launches = 0;  // 0: as many as fit in --seconds
};

class Session {
public:
  Session(const Options& o, const std::vector<std::byte>& elf) : o_(o), tOpen_(Clock::now()) {
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
    results_ = rt_->mallocDevice(dev_, IB_MAX_HARTS * sizeof(IbResult));
    std::fprintf(stderr, "device ready in %.2f s\n", secondsSince(tOpen_));
  }
  ~Session() {
    rt_->freeDevice(dev_, results_);
    rt_->unloadCode(kernel_);
    rt_->destroyStream(stream_);
    std::fprintf(stderr, "device held for %.2f s\n", secondsSince(tOpen_));
  }
  bool overBudget() const { return secondsSince(tOpen_) > o_.budget; }
  // Whether one more launch (its cycles at the slowest clock considered, 500 MHz, plus 1 s of slack for the copies and
  // a possible abort) still ends inside the budget.
  bool launchFits() const { return secondsSince(tOpen_) + double(o_.window) / 0.5e9 + 1.0 <= o_.budget; }
  long long t0Ms = 0, t1Ms = 0;  // epoch bounds of the last launch, for lining up with power samples
  bool launch(IbArgs a, std::vector<IbResult>& res, double& wallS) {
    res.assign(IB_MAX_HARTS, IbResult{});
    rt_->memcpyHostToDevice(stream_, reinterpret_cast<const std::byte*>(res.data()), results_,
                            res.size() * sizeof(IbResult));
    rt_->waitForStream(stream_);
    a.results = reinterpret_cast<uint64_t>(results_);
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
    rt_->memcpyDeviceToHost(stream_, results_, reinterpret_cast<std::byte*>(res.data()),
                            res.size() * sizeof(IbResult));
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

// One launch of one arm; prints one INTBITS line. Returns false on a failed launch or a failed check.
bool runOnce(const Options& o, Session& dev, const Arm& m) {
  IbArgs a{};
  a.form = m.form;
  a.op = m.op;
  a.shire_mask = o.shireMask;
  a.minion_mask = o.minionMask;
  a.harts = o.harts;
  a.window = o.window;
  a.a0 = m.a0; a.b0 = m.b0; a.a1 = m.a1; a.b1 = m.b1;
  std::vector<IbResult> res;
  double wallS = 0;
  const bool ok = dev.launch(a, res, wallS);
  const Counts c = designed(m);
  uint64_t n = 0, iters = 0, cmax = 0, bad = 0;
  double csum = 0;
  uint64_t ret = 0, icr = 0, icm = 0, l1m = 0;
  std::vector<bool> nbSeen(IB_MAX_HARTS / 16, false);
  for (const auto& r : res) {
    if (r.magic != IB_MAGIC) continue;
    ++n;
    iters += r.iters;
    cmax = std::max<uint64_t>(cmax, r.cycles);
    csum += double(r.cycles);
    // Expected destinations after the check pair.
    if (m.form == IB_SAME && r.res_x5 != c.r0) ++bad;
    if (m.form == IB_PAIR && r.res_x5 != c.r1) ++bad;
    if (m.form == IB_SPLIT && (r.res_x5 != c.r0 || r.res_x30 != c.r1)) ++bad;
    // The minion counters are neighbourhood sums: count each neighbourhood (16 harts) once.
    const uint32_t nb = r.hart / 16;
    if (!nbSeen[nb]) {
      nbSeen[nb] = true;
      ret += r.ret1 - r.ret0; icr += r.icr1 - r.icr0; icm += r.icm1 - r.icm0; l1m += r.l1m1 - r.l1m0;
    }
  }
  const double instr = double(iters) * IB_PER_ITER;
  const double secs = cmax / 0.6e9;  // device seconds at the 600 MHz the reference card is pinned to
  std::printf("INTBITS {%s,\"harts\":%llu,\"participants\":%llu,\"iters\":%llu,\"instr_body\":%.0f,"
              "\"retired_counter\":%llu,\"icache_req\":%llu,\"icache_miss\":%llu,\"l1d_miss\":%llu,"
              "\"cycles_max\":%llu,\"cycles_mean\":%.0f,\"instr_per_cycle_per_hart\":%.4f,\"instr_per_s_600\":%.4e,"
              "\"window\":%llu,\"wall_s\":%.4f,\"t_start_ms\":%lld,\"t_end_ms\":%lld,\"check_bad\":%llu,\"ok\":%s}\n",
              armJson(m).c_str(), (unsigned long long)o.harts, (unsigned long long)n, (unsigned long long)iters, instr,
              (unsigned long long)ret, (unsigned long long)icr, (unsigned long long)icm, (unsigned long long)l1m,
              (unsigned long long)cmax, n ? csum / double(n) : 0.0, (cmax && n) ? instr / double(cmax) / double(n) : 0.0,
              secs > 0 ? instr / secs : 0.0, (unsigned long long)o.window, wallS, dev.t0Ms, dev.t1Ms,
              (unsigned long long)bad, (ok && n && !bad) ? "true" : "false");
  std::fflush(stdout);
  return ok && n && !bad;
}

uint64_t parseU(const std::string& s) { return std::strtoull(s.c_str(), nullptr, 0); }

Arm customArm(const Options& o) {
  Arm m{"custom", IB_PAIR, IB_ADD, o.a0, o.b0, o.a1, o.b1, "custom values"};
  const std::map<std::string, uint64_t> forms = {{"nop", IB_NOP}, {"same", IB_SAME}, {"pair", IB_PAIR}, {"split", IB_SPLIT}};
  const std::map<std::string, uint64_t> ops = {{"add", IB_ADD}, {"xor", IB_XOR}, {"sub", IB_SUB}, {"and", IB_AND}, {"or", IB_OR}};
  if (!o.form.empty()) {
    if (!forms.count(o.form)) throw std::runtime_error("unknown --form " + o.form);
    m.form = forms.at(o.form);
  }
  if (!o.op.empty()) {
    if (!ops.count(o.op)) throw std::runtime_error("unknown --op " + o.op);
    m.op = ops.at(o.op);
  }
  if (m.form == IB_NOP) m.op = IB_NOPS;
  return m;
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
    if (a == "--arm") o.arm = next();
    else if (a == "--arms") o.arms = next();
    else if (a == "--form") o.form = next();
    else if (a == "--op") o.op = next();
    else if (a == "--a0") o.a0 = parseU(next());
    else if (a == "--b0") o.b0 = parseU(next());
    else if (a == "--a1") o.a1 = parseU(next());
    else if (a == "--b1") o.b1 = parseU(next());
    else if (a == "--harts") o.harts = parseU(next());
    else if (a == "--shires") o.shireMask = parseU(next());
    else if (a == "--minions") o.minionMask = parseU(next());
    else if (a == "--window") o.window = parseU(next());
    else if (a == "--seconds") o.seconds = std::strtod(next().c_str(), nullptr);
    else if (a == "--budget") o.budget = std::strtod(next().c_str(), nullptr);
    else if (a == "--launches") o.launches = (int)parseU(next());
    else if (a == "--seed") o.seed = parseU(next());
    else if (a == "--kernel") o.kernel = next();
    else if (a == "--stop-file") o.stopFile = next();
    else if (a == "--list") o.list = true;
    else if (a == "--json") o.json = true;
    else { std::fprintf(stderr, "unknown option %s\n", a.c_str()); return 2; }
  }
  const auto table = armTable(o.seed);
  if (o.list) {
    for (const auto& m : table) {
      if (o.json) std::printf("{%s,\"note\":\"%s\"}\n", armJson(m).c_str(), m.note.c_str());
      else {
        const Counts c = designed(m);
        std::printf("%-16s %-5s %-4s portA %2d portB %2d result %2d carry %2d cell %2d enc %2d  %s\n", m.name.c_str(),
                    formName(m.form), opName(m.op), c.portA, c.portB, c.result, c.carry, c.cell, c.enc, m.note.c_str());
      }
    }
    return 0;
  }
  try {
  // Which arms to run.
  std::vector<Arm> todo;
  auto find = [&](const std::string& n) {
    for (const auto& m : table) if (m.name == n) return m;
    throw std::runtime_error("unknown arm " + n + " (see --list)");
  };
  if (!o.arms.empty()) {
    if (o.arms == "all") todo = table;
    else {
      std::stringstream ss(o.arms);
      for (std::string n; std::getline(ss, n, ',');) todo.push_back(find(n));
    }
  } else if (!o.arm.empty()) todo.push_back(find(o.arm));
  else todo.push_back(customArm(o));
  if (o.harts > 1) std::fprintf(stderr, "note: --harts 2 interleaves two streams in one pipeline; designed counts assume 1\n");
    if (o.window == 0 || o.window > 1200000000ull) throw std::runtime_error("--window must be 1 .. 1200000000 cycles");
    if (!(o.budget > 0 && o.budget <= 9.0)) throw std::runtime_error("--budget must be in (0, 9] seconds");
    checkOneCard();  // before anything opens a device
    const auto elf = readFile(o.kernel);
    if (elf.empty()) throw std::runtime_error("cannot read kernel " + o.kernel);
    Session dev(o, elf);
    int bad = 0;
    auto stopped = [&]() { return !o.stopFile.empty() && fs::exists(o.stopFile); };
    if (todo.size() > 1) {  // a suite: each arm launched --launches times (1 by default), one session, same limits
      const auto tStart = Clock::now();
      for (const auto& m : todo)
        for (int k = 0; k < std::max(1, o.launches); ++k) {
          if (stopped() || !dev.launchFits() || secondsSince(tStart) >= o.seconds) {
            std::fprintf(stderr, "suite ended early (stop file, --budget or --seconds): later arms not run\n");
            return 3;
          }
          bad += !runOnce(o, dev, m);
        }
    } else {
      const auto tStart = Clock::now();
      int k = 0;
      while ((o.launches ? k < o.launches : secondsSince(tStart) < o.seconds) && dev.launchFits() && !stopped()) {
        if (!runOnce(o, dev, todo[0])) { ++bad; break; }
        ++k;
      }
    }
    return bad ? 1 : 0;
  } catch (const std::exception& e) {
    std::fprintf(stderr, "FAIL: %s\n", e.what());
    return 1;
  }
}
