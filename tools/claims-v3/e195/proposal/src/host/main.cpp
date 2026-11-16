// x09mem: memory traffic with designed data, flat out or paced, while the host's power logger runs.
// Every launch prints one line
//   X09MEM {json}            (the arm's name is "arm": the lab's runner merges the record into its own, whose
//                             "item" is the manifest's name)
//
//   x09mem_host --item NAME [--seconds S] [--window CYCLES] [--budget S] [--stop-file PATH] [--seed N] [--no-ms]
//   x09mem_host --mode rd|wr|rdl1|wrscp|wrnst --image SPEC [--period CYCLES] [--region BYTES] ...   (any other arm)
//   x09mem_host --list [--json]                       the arm table (no device is opened)
//   x09mem_host --item NAME --dump-image FILE         the bytes the host would write for this arm (no device)
//
// Images (SPEC), each a rule for the bytes of every 64 B line:
//   z               all zeros
//   b:XX            every byte XX (hex)
//   first:XX        the line's first byte XX, the other 63 zero (first:01 is one bit a line)
//   alt:XX:YY:N     runs of N bytes, alternately XX and YY, from the line's first byte (N divides 64)
//   par:XX:YY       the whole line XX or YY: for writes by the minion's parity, for reads by bit 4 of the line
//                   index (so one channel, which carries every 16th line, sees the two values in turn)
//   rnd             random bytes, a different line everywhere (from --seed, the hart or minion and the line)
//
// The card is shared: each launch runs `window` cycles (0.4 s at 600 MHz) and no launch starts unless it can end
// inside --budget seconds of holding the device (8.5 by default, at most 9), so the process ends inside `timeout 10`;
// nothing more is launched once the --stop-file exists. One card only: before anything is opened the host counts the
// card nodes (/dev/et<N>_ops) and refuses unless there is exactly one, so it never opens a second card; after
// opening, the runtime must list exactly one device. Paced arms spread the harts' slots over each period (the
// kernel's `phase`; --no-phase starts every hart's grid at once).
#include <g3log/loglevels.hpp>
#include <runtime/IRuntime.h>
#include <runtime/Types.h>
#include <device-layer/IDeviceLayer.h>

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
#include <random>
#include <sstream>
#include <string>
#include <vector>

#include "Constants.h"
#include "x09mem_args.h"

// The runtime's thread-pool workers log at custom levels that only the default logger registers with g3log; left
// unregistered, the first log calls from several new workers can corrupt its level map (the public lab repo's
// docs/findings/14-card-behaviour.md, "Traps"). Registering them first, disabled, removes the race.
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
  default: break;
  }
  return static_cast<uint64_t>(v);
}
uint32_t crc32(const uint8_t* p, size_t n, uint32_t c = 0) {
  c = ~c;
  for (size_t i = 0; i < n; ++i) {
    c ^= p[i];
    for (int k = 0; k < 8; ++k) c = (c >> 1) ^ (0xEDB88320u & (0u - (c & 1u)));
  }
  return ~c;
}

// ---- images -------------------------------------------------------------------------------------------------
struct Image {
  enum Kind { ZERO, BYTE, FIRST, ALT, PAR, RND } kind = ZERO;
  uint8_t x = 0, y = 0;
  unsigned run = 64;
  std::string spec = "z";
};

Image parseImage(const std::string& s) {
  Image im;
  im.spec = s;
  auto hex = [&](const std::string& h) -> uint8_t {
    if (h.size() != 2 || h.find_first_not_of("0123456789abcdefABCDEF") != std::string::npos)
      throw std::runtime_error("image " + s + ": bytes are two hex digits");
    return (uint8_t)std::stoul(h, nullptr, 16);
  };
  std::vector<std::string> f;
  std::stringstream ss(s);
  for (std::string t; std::getline(ss, t, ':');) f.push_back(t);
  if (f.empty()) throw std::runtime_error("empty image");
  if (f[0] == "z" && f.size() == 1) { im.kind = Image::ZERO; return im; }
  if (f[0] == "rnd" && f.size() == 1) { im.kind = Image::RND; return im; }
  if (f[0] == "b" && f.size() == 2) { im.kind = Image::BYTE; im.x = hex(f[1]); return im; }
  if (f[0] == "first" && f.size() == 2) { im.kind = Image::FIRST; im.x = hex(f[1]); return im; }
  if (f[0] == "par" && f.size() == 3) { im.kind = Image::PAR; im.x = hex(f[1]); im.y = hex(f[2]); return im; }
  if (f[0] == "alt" && f.size() == 4) {
    im.kind = Image::ALT; im.x = hex(f[1]); im.y = hex(f[2]);
    im.run = (unsigned)std::stoul(f[3]);
    if (im.run == 0 || 64 % im.run) throw std::runtime_error("image " + s + ": the run must divide 64");
    return im;
  }
  throw std::runtime_error("unknown image " + s);
}

// One 64 B line. `who` is the hart (reads) or the minion (writes); `line` the line's index in its slice or image;
// `rng` that hart's or minion's random stream (seeded once from --seed and `who`, drawn line after line).
void fillLine(const Image& im, uint8_t* out, uint64_t who, uint64_t line, std::mt19937_64& rng, bool writes) {
  switch (im.kind) {
  case Image::ZERO: std::memset(out, 0, 64); break;
  case Image::BYTE: std::memset(out, im.x, 64); break;
  case Image::FIRST: std::memset(out, 0, 64); out[0] = im.x; break;
  case Image::ALT:
    for (unsigned j = 0; j < 64; ++j) out[j] = ((j / im.run) & 1) ? im.y : im.x;
    break;
  case Image::PAR: {
    const bool second = writes ? (who & 1) : ((line >> 4) & 1);
    std::memset(out, second ? im.y : im.x, 64);
    break;
  }
  case Image::RND: {
    for (unsigned j = 0; j < 64; j += 8) {
      const uint64_t v = rng();
      std::memcpy(out + j, &v, 8);
    }
    break;
  }
  }
}

// ---- arms ---------------------------------------------------------------------------------------------------
struct Arm {
  std::string name;
  uint64_t mode;
  std::string image;
  uint64_t period;   // 0: flat out
  const char* role;
};

constexpr uint64_t RD_PERIOD = 1024;    // one line per 1,024 cycles per hart: half the flat-out read rate
constexpr uint64_t WR_PERIOD = 8192;    // one 512 B store (8 lines) per 8,192 cycles per hart: the same line rate

const std::vector<Arm> ARMS = {
  {"rd.z", X9_RD, "z", 0, "read, zeros: the control of every flat-out read"},
  {"rd.w1", X9_RD, "first:01", 0, "read, one bit a line: what a line that is not all zeros adds"},
  {"rd.u2", X9_RD, "b:03", 0, "read, every byte 0x03: 128 ones, 128 high pins a line"},
  {"rd.u4", X9_RD, "b:0f", 0, "read, every byte 0x0F: 256 ones, 256 high pins"},
  {"rd.u7", X9_RD, "b:7f", 0, "read, every byte 0x7F: 448 ones, 128 high pins (inverted)"},
  {"rd.u8", X9_RD, "b:ff", 0, "read, every byte 0xFF: 512 ones, 64 high pins (inverted)"},
  {"rd.l08", X9_RD, "alt:00:ff:1", 0, "read, byte lanes constant 0x00 and 0xFF: 256 ones, 32 high pins, no toggle"},
  {"rd.a44", X9_RD, "alt:0f:f0:2", 0, "read, beats alternate 0x0F/0xF0: 256 ones, 256 high, 512 pin toggles"},
  {"rd.rnd", X9_RD, "rnd", 0, "read, random lines"},
  {"wr.z", X9_WR, "z", 0, "write, zeros: the control of every flat-out write"},
  {"wr.w1", X9_WR, "first:01", 0, "write, one bit a line"},
  {"wr.u2", X9_WR, "b:03", 0, "write, every byte 0x03"},
  {"wr.u4", X9_WR, "b:0f", 0, "write, every byte 0x0F"},
  {"wr.u7", X9_WR, "b:7f", 0, "write, every byte 0x7F"},
  {"wr.u8", X9_WR, "b:ff", 0, "write, every byte 0xFF: 512 ones, 64 high pins if inverted, 512 if not"},
  {"wr.l08", X9_WR, "alt:00:ff:1", 0, "write, byte lanes constant 0x00 and 0xFF: 256 ones, no pin toggle"},
  {"wr.a08", X9_WR, "alt:00:ff:2", 0, "write, beats 0x0000/0xFFFF: l08's ones and pins, 64 toggles inverted, 512 not"},
  {"wr.a44", X9_WR, "alt:0f:f0:2", 0, "write, beats alternate 0x0F/0xF0: 512 pin toggles either way"},
  {"wr.p64", X9_WR, "alt:0f:f0:8", 0, "write, 8-byte pieces alternate 0x0F/0xF0"},
  {"wr.h256", X9_WR, "alt:0f:f0:32", 0, "write, the line's 32 B halves 0x0F and 0xF0"},
  {"wr.c44", X9_WR, "par:0f:f0", 0, "write, whole lines 0x0F or 0xF0 by minion parity: a channel's lines change"},
  {"wr.rnd", X9_WR, "rnd", 0, "write, random lines (each minion its own 512 B)"},
  {"rdh.z", X9_RD, "z", RD_PERIOD, "paced read, zeros"},
  {"rdh.u4", X9_RD, "b:0f", RD_PERIOD, "paced read, every byte 0x0F"},
  {"rdh.rnd", X9_RD, "rnd", RD_PERIOD, "paced read, random lines"},
  {"rdh.l1", X9_RD_L1, "z", RD_PERIOD, "paced read loop on one L1 line: no memory traffic"},
  {"wrh.z", X9_WR, "z", WR_PERIOD, "paced write, zeros"},
  {"wrh.u4", X9_WR, "b:0f", WR_PERIOD, "paced write, every byte 0x0F"},
  {"wrh.rnd", X9_WR, "rnd", WR_PERIOD, "paced write, random lines"},
  {"wrh.scp", X9_WR_SCP, "z", WR_PERIOD, "paced write loop into the own scratchpad: no DRAM traffic"},
  {"wrh.nst", X9_WR_NST, "z", WR_PERIOD, "paced write loop with no store at all: no traffic"},
};

const char* modeName(uint64_t m) {
  switch (m) {
  case X9_RD: return "rd";
  case X9_WR: return "wr";
  case X9_RD_L1: return "rdl1";
  case X9_WR_SCP: return "wrscp";
  case X9_WR_NST: return "wrnst";
  default: return "?";
  }
}
uint64_t modeOf(const std::string& s) {
  if (s == "rd") return X9_RD;
  if (s == "wr") return X9_WR;
  if (s == "rdl1") return X9_RD_L1;
  if (s == "wrscp") return X9_WR_SCP;
  if (s == "wrnst") return X9_WR_NST;
  throw std::runtime_error("unknown --mode " + s);
}
bool isRead(uint64_t m) { return m == X9_RD || m == X9_RD_L1; }

struct Options {
  std::string item, mode, image, kernel = KERNEL_ELF, stopFile, dumpImage;
  uint64_t period = 0, region = 0, sliceBytes = 0, window = 240000000, seed = 1;
  uint64_t shireMask = 0xffffffff, minionMask = 0, scpOff = 256 * 1024, scpBytes = 16 * 1024;
  uint32_t fillWord = 0;   // --check-slice: the word unwritten memory holds
  double seconds = 4.0, budget = 8.5;
  bool list = false, json = false, ms = true, emu = false, checkSlice = false, phase = true;
  bool buffersOnly = false;   // --buffers-only: build what would be copied to the card, time it, open nothing
  std::string emuArgs;
};

// The resolved run: an arm from the table or one given by --mode and --image.
struct Run {
  std::string name;
  uint64_t mode = X9_RD, period = 0, region = 0, sliceBytes = 0;
  Image image;
};

Run resolve(const Options& o) {
  Run r;
  if (!o.item.empty()) {
    const auto it = std::find_if(ARMS.begin(), ARMS.end(), [&](const Arm& a) { return a.name == o.item; });
    if (it == ARMS.end()) throw std::runtime_error("unknown --item " + o.item + " (see --list)");
    r.name = it->name;
    r.mode = it->mode;
    r.image = parseImage(it->image);
    r.period = it->period;
  } else {
    if (o.mode.empty() || o.image.empty()) throw std::runtime_error("give --item, or --mode and --image");
    r.mode = modeOf(o.mode);
    r.image = parseImage(o.image);
    r.period = o.period;
    r.name = std::string("custom.") + modeName(r.mode);
  }
  if (!o.item.empty() && (o.period || !o.mode.empty() || !o.image.empty()))
    throw std::runtime_error("--item fixes the mode, image and period");
  // Reads sweep 128 KB a hart (the footprint of the public catalogue's flw_pat DRAM rows) with an 8 KB bank spread;
  // writes 256 KB a hart (its tensor-store rows). Either way 1,024 harts cover far more than the L3.
  r.region = o.region ? o.region : (isRead(r.mode) ? 128 * 1024 : 256 * 1024);
  r.sliceBytes = o.sliceBytes ? o.sliceBytes : (isRead(r.mode) ? r.region + 8192 : r.region);
  if (r.region % 512 || r.region < 4096) throw std::runtime_error("--region must be a multiple of 512, at least 4 KB");
  if (r.sliceBytes < r.region + (isRead(r.mode) ? 8192 : 0)) throw std::runtime_error("--slice-bytes too small");
  if (r.period && r.period < 64) throw std::runtime_error("--period must be 0 or at least 64 cycles");
  if (r.mode == X9_WR_NST && !r.period) throw std::runtime_error("the no-store loop is paced only: give --period");
  if (o.scpBytes % 512 || o.scpBytes < 4096 || o.scpOff < 4096 || o.scpOff + 32 * o.scpBytes > 0x280000ull)
    throw std::runtime_error("the scratchpad regions must fit 2.5 MB, past offset 0");
  return r;
}

// The bytes a run puts in memory: for reads hart h's swept region (lines 0..region/64-1); for writes minion m's
// 512 B image (8 lines).
uint64_t streamSeed(uint64_t seed, uint64_t who) { return seed * 0x9E3779B97F4A7C15ull ^ (who << 32); }
void readRegion(const Run& r, uint64_t hart, uint64_t seed, std::vector<uint8_t>& out) {
  out.resize(r.region);
  std::mt19937_64 rng(streamSeed(seed, hart));
  for (uint64_t l = 0; l < r.region / 64; ++l) fillLine(r.image, out.data() + 64 * l, hart, l, rng, false);
}
void writeImage(const Run& r, uint64_t minion, uint64_t seed, uint8_t* out) {
  std::mt19937_64 rng(streamSeed(seed, minion));
  for (uint64_t l = 0; l < 8; ++l) fillLine(r.image, out + 64 * l, minion, l, rng, true);
}

// What the host puts in device memory for a run, built before any device is opened: the 1,024 minions' images
// (writes) or every hart's slice with its swept region filled (reads; the bank spread puts hart h's region
// ((h / 2) % 8) KB into its slice).
struct Buffers {
  std::vector<uint8_t> images, slices;
  uint32_t crc = 0;
};
Buffers buildBuffers(const Options& o, const Run& r) {
  Buffers b;
  if (r.mode == X9_WR || r.mode == X9_WR_SCP || r.mode == X9_WR_NST) {
    b.images.resize(1024 * 512);
    for (uint64_t m = 0; m < 1024; ++m) writeImage(r, m, o.seed, b.images.data() + 512 * m);
    b.crc = crc32(b.images.data(), b.images.size());
  }
  if (isRead(r.mode)) {
    b.slices.assign(X9_MAX_HARTS * r.sliceBytes, 0);
    std::vector<uint8_t> reg;
    for (uint64_t h = 0; h < X9_MAX_HARTS; ++h) {
      readRegion(r, h, o.seed, reg);
      std::memcpy(b.slices.data() + h * r.sliceBytes + ((h >> 1) & 7) * 1024, reg.data(), reg.size());
      if (h == 0) b.crc = crc32(reg.data(), reg.size());
    }
  }
  return b;
}

}  // namespace

// The device layer: the card's PCIe layer in this build (a build for the open emulator supplies its own).
std::shared_ptr<dev::IDeviceLayer> makeLayer(const Options& o);

namespace {

class Session {
public:
  Session(const Options& o, const std::vector<std::byte>& elf) : o_(o), tOpen_(Clock::now()) {
    dl_ = makeLayer(o);
    rt_ = rt::IRuntime::create(dl_);
    const auto devices = rt_->getDevices();
    if (devices.empty()) throw std::runtime_error("no device found");
    if (devices.size() > 1) throw std::runtime_error("more than one device: this host is for one card");
    dev_ = devices[0];
    stream_ = rt_->createStream(dev_);
    const auto load = rt_->loadCode(stream_, elf.data(), elf.size());
    rt_->waitForEvent(load.event_);
    kernel_ = load.kernel_;
    results_ = rt_->mallocDevice(dev_, X9_MAX_HARTS * sizeof(X9Result));
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
  // Whether one more launch (its cycles at a 500 MHz clock, plus 1 s for the copies and a possible abort) still ends
  // inside the budget.
  bool launchFits() const {
    if (o_.emu) return true;   // the emulator holds no card
    return secondsSince(tOpen_) + double(o_.window) / 0.5e9 + 1.0 <= o_.budget;
  }
  long long t0Ms = 0, t1Ms = 0;

  bool launch(X9Args a, std::vector<X9Result>& res, double& wallS) {
    res.assign(X9_MAX_HARTS, X9Result{});
    rt_->memcpyHostToDevice(stream_, reinterpret_cast<const std::byte*>(res.data()), results_,
                            res.size() * sizeof(X9Result));
    rt_->waitForStream(stream_);
    a.results = reinterpret_cast<uint64_t>(results_);
    rt::KernelLaunchOptions opts;
    opts.setShireMask(o_.shireMask);
    opts.setBarrier(true);
    const int timeoutS = o_.emu ? 3600 : 3;   // a launch is at most 1.2e9 cycles: 2.4 s at 500 MHz
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
                            res.size() * sizeof(X9Result));
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

// Refuses (throws) unless this host has exactly one card node, so that no other card is ever opened. Runs before
// any device is opened; the runtime's own device count is checked again after opening (Session).
void checkOneCard() {
  std::vector<int> v;
  std::error_code ec;
  for (const auto& e : fs::directory_iterator("/dev", ec)) {
    const std::string n = e.path().filename().string();
    if (n.size() < 7 || n.compare(0, 2, "et") != 0 || n.compare(n.size() - 4, 4, "_ops") != 0) continue;
    const std::string d = n.substr(2, n.size() - 6);
    if (d.empty() || d.find_first_not_of("0123456789") != std::string::npos) continue;
    v.push_back(std::stoi(d));
  }
  if (v.empty()) throw std::runtime_error("no card node /dev/et<N>_ops on this host");
  if (v.size() > 1)
    throw std::runtime_error(std::to_string(v.size()) + " card nodes on this host: this host program is for a host "
                             "with one card and refuses to run here");
}

void printList(bool json) {
  if (json) std::printf("[");
  bool first = true;
  for (const auto& a : ARMS) {
    if (json) {
      std::printf("%s{\"name\":\"%s\",\"mode\":\"%s\",\"image\":\"%s\",\"period\":%llu,\"role\":\"%s\"}",
                  first ? "" : ",", a.name.c_str(), modeName(a.mode), a.image.c_str(), (unsigned long long)a.period,
                  a.role);
    } else {
      std::printf("%-8s %-6s %-14s period %-5llu %s\n", a.name.c_str(), modeName(a.mode), a.image.c_str(),
                  (unsigned long long)a.period, a.role);
    }
    first = false;
  }
  if (json) std::printf("]\n");
}

// Writes the bytes this arm puts in memory: reads, harts 0, 2 and 4's swept regions; writes, all 1,024 minions'
// images. No device is opened.
void dumpImage(const Options& o, const Run& r) {
  std::ofstream f(o.dumpImage, std::ios::binary);
  if (!f) throw std::runtime_error("cannot write " + o.dumpImage);
  if (isRead(r.mode)) {
    std::vector<uint8_t> reg;
    for (uint64_t h : {0ull, 2ull, 4ull}) {
      readRegion(r, h, o.seed, reg);
      f.write(reinterpret_cast<const char*>(reg.data()), (std::streamsize)reg.size());
    }
  } else {
    std::vector<uint8_t> img(1024 * 512);
    for (uint64_t m = 0; m < 1024; ++m) writeImage(r, m, o.seed, img.data() + 512 * m);
    f.write(reinterpret_cast<const char*>(img.data()), (std::streamsize)img.size());
  }
}

int run(const Options& o, const Run& r, const Buffers& b, Session& dev) {
  const bool reads = isRead(r.mode);
  X9Args a{};
  a.mode = r.mode;
  a.shire_mask = o.shireMask;
  a.minion_mask = o.minionMask;
  a.window = o.window;
  a.period = r.period;
  a.slice_bytes = r.sliceBytes;
  a.region = r.region;
  a.stride = r.mode == X9_RD ? 64 : 0;
  a.bank_spread = reads ? 1 : 0;
  a.scp_off = o.scpOff;
  a.scp_bytes = o.scpBytes;
  a.ms_counters = o.ms ? 1 : 0;
  a.phase = (r.period && o.phase) ? 1 : 0;

  const uint32_t crc = b.crc;
  if (!b.images.empty()) {
    std::byte* ib = dev.alloc(b.images.size());
    dev.put(b.images.data(), ib, b.images.size());
    a.images = reinterpret_cast<uint64_t>(ib);
  }
  std::byte* slice = nullptr;
  if (r.mode != X9_WR_SCP && r.mode != X9_WR_NST) {
    slice = dev.alloc(X9_MAX_HARTS * r.sliceBytes);
    a.slice = reinterpret_cast<uint64_t>(slice);
    if (reads) dev.put(b.slices.data(), slice, b.slices.size());   // loads read what is there
  }

  std::fprintf(stderr, "images 0x%llx slices 0x%llx (%llu B each) results\n", (unsigned long long)a.images,
               (unsigned long long)a.slice, (unsigned long long)a.slice_bytes);
  const auto tStart = Clock::now();
  auto stopped = [&]() { return !o.stopFile.empty() && fs::exists(o.stopFile); };
  int bad = 0;
  while (secondsSince(tStart) < o.seconds && dev.launchFits() && !stopped()) {
    std::vector<X9Result> res;
    double wallS = 0;
    const bool ok = dev.launch(a, res, wallS);
    uint64_t n = 0, iters = 0, acc = 0, lines = 0, cmax = 0, ret = 0, l1m = 0, spins = 0, late = 0;
    uint64_t msRd = 0, msWr = 0, msCyc = 0, msBad = 0;
    bool msSeen = false;
    double csum = 0;
    for (const auto& x : res) {
      if (x.magic != X9_MAGIC) continue;
      ++n; iters += x.iters; acc += x.accesses; lines += x.lines; spins += x.spins; late += x.late;
      cmax = std::max<uint64_t>(cmax, x.cycles); csum += double(x.cycles);
      if (((x.hart >> 1) & 7) == 0) { ret += x.ret1 - x.ret0; l1m += x.l1m1 - x.l1m0; }   // one per neighbourhood
      if (x.pad == 1) { msSeen = true; msRd = x.ms_rd; msWr = x.ms_wr; msCyc = x.ms_cyc; msBad = x.ms_bad; }
    }
    const double secs = cmax / 0.6e9;   // device seconds at the 600 MHz the card is pinned to
    const bool memArm = r.mode == X9_RD || r.mode == X9_WR;
    const double ops = double(memArm ? lines : acc);
    std::printf("X09MEM {\"arm\":\"%s\",\"mode\":\"%s\",\"image\":\"%s\",\"period\":%llu,\"unit\":\"%s\","
                "\"participants\":%llu,\"ops\":%.0f,\"lines\":%llu,\"accesses\":%llu,\"bytes\":%llu,\"iters\":%llu,"
                "\"cycles_max\":%llu,\"cycles_mean\":%.0f,\"ops_per_s\":%.4e,\"bytes_per_s\":%.4e,"
                "\"ret_t0\":%llu,\"l1_miss\":%llu,\"ms\":%s,\"ms_rd\":%llu,\"ms_wr\":%llu,\"ms_cyc\":%llu,\"ms_bad\":%llu,"
                "\"spins\":%llu,\"late\":%llu,\"phase\":%llu,\"region\":%llu,\"slice_bytes\":%llu,\"seed\":%llu,"
                "\"image_crc\":\"%08x\","
                "\"wall_s\":%.4f,\"t_start_ms\":%lld,\"t_end_ms\":%lld,\"ok\":%s}\n",
                r.name.c_str(), modeName(r.mode), r.image.spec.c_str(), (unsigned long long)r.period,
                memArm ? "line" : "access", (unsigned long long)n, ops, (unsigned long long)lines,
                (unsigned long long)acc, (unsigned long long)(lines * 64), (unsigned long long)iters,
                (unsigned long long)cmax, n ? csum / double(n) : 0.0, secs > 0 ? ops / secs : 0.0,
                secs > 0 ? double(lines * 64) / secs : 0.0, (unsigned long long)ret, (unsigned long long)l1m,
                msSeen ? "true" : "false", (unsigned long long)msRd, (unsigned long long)msWr,
                (unsigned long long)msCyc, (unsigned long long)msBad, (unsigned long long)spins,
                (unsigned long long)late, (unsigned long long)a.phase, (unsigned long long)r.region,
                (unsigned long long)r.sliceBytes,
                (unsigned long long)o.seed, crc, wallS, dev.t0Ms, dev.t1Ms, (ok && n) ? "true" : "false");
    std::fflush(stdout);
    if (!ok || !n) { ++bad; break; }
  }
  if (o.checkSlice && slice && !bad) {
    // Hart 0's swept region against what it should hold: for writes minion 0's image repeated, for reads the fill.
    // Hart 0's bank spread is 0 KB, so its region starts at the start of the slices.
    std::vector<uint8_t> got(r.region), want(r.region);
    dev.get(slice, got.data(), got.size());
    if (reads) {
      readRegion(r, 0, o.seed, want);
    } else {
      uint8_t img[512];
      writeImage(r, 0, o.seed, img);
      for (uint64_t i = 0; i < r.region; ++i) want[i] = img[i % 512];
    }
    // A word that still holds what the memory held before the run (`--fill-word`, 0 on a card) was not yet written
    // back (lines can still sit in a cache when the host reads); any other mismatch is a wrong byte.
    uint64_t nbad = 0, first = 0, unwritten = 0;
    for (uint64_t i = 0; i < r.region; i += 4) {
      uint32_t g, w;
      std::memcpy(&g, got.data() + i, 4);
      std::memcpy(&w, want.data() + i, 4);
      if (g == w) continue;
      if (g == o.fillWord) { unwritten += 4; continue; }
      for (unsigned j = 0; j < 4; ++j)
        if (got[i + j] != want[i + j]) { if (!nbad) first = i + j; ++nbad; }
    }
    std::printf("X09CHECK {\"arm\":\"%s\",\"bytes\":%llu,\"wrong\":%llu,\"first_wrong\":%llu,"
                "\"unwritten\":%llu,\"crc_got\":\"%08x\"}\n",
                r.name.c_str(), (unsigned long long)r.region, (unsigned long long)nbad, (unsigned long long)first,
                (unsigned long long)unwritten, crc32(got.data(), got.size()));
    std::fflush(stdout);
    if (nbad) bad = 1;
  }
  return bad ? 1 : 0;
}

}  // namespace

#ifndef X09_OTHER_LAYER
std::shared_ptr<dev::IDeviceLayer> makeLayer(const Options& o) {
  if (o.emu) throw std::runtime_error("this build has the card's device layer only");
  return dev::IDeviceLayer::createPcieDeviceLayer(true, false);   // the ops node only
}
#endif

int main(int argc, char** argv) {
  registerRuntimeLogLevels();   // first, before any library starts a thread
  Options o;
  for (int i = 1; i < argc; ++i) {
    std::string a = argv[i];
    auto next = [&]() -> std::string {
      if (i + 1 >= argc) { std::fprintf(stderr, "%s needs a value\n", a.c_str()); std::exit(2); }
      return argv[++i];
    };
    if (a == "--item") o.item = next();
    else if (a == "--mode") o.mode = next();
    else if (a == "--image") o.image = next();
    else if (a == "--period") o.period = std::strtoull(next().c_str(), nullptr, 0);
    else if (a == "--region") o.region = parseSize(next());
    else if (a == "--slice-bytes") o.sliceBytes = parseSize(next());
    else if (a == "--window") o.window = std::strtoull(next().c_str(), nullptr, 0);
    else if (a == "--seconds") o.seconds = std::strtod(next().c_str(), nullptr);
    else if (a == "--budget") o.budget = std::strtod(next().c_str(), nullptr);
    else if (a == "--seed") o.seed = std::strtoull(next().c_str(), nullptr, 0);
    else if (a == "--shires") o.shireMask = std::strtoull(next().c_str(), nullptr, 0);
    else if (a == "--minions") o.minionMask = std::strtoull(next().c_str(), nullptr, 0);
    else if (a == "--scp-off") o.scpOff = parseSize(next());
    else if (a == "--scp-bytes") o.scpBytes = parseSize(next());
    else if (a == "--stop-file") o.stopFile = next();
    else if (a == "--no-ms") o.ms = false;
    else if (a == "--no-phase") o.phase = false;
    else if (a == "--dump-image") o.dumpImage = next();
    else if (a == "--check-slice") o.checkSlice = true;
    else if (a == "--buffers-only") o.buffersOnly = true;
    else if (a == "--fill-word") o.fillWord = (uint32_t)std::strtoul(next().c_str(), nullptr, 0);
    else if (a == "--list") o.list = true;
    else if (a == "--json") o.json = true;
    else if (a == "--kernel") o.kernel = next();
    else if (a == "--emu") o.emu = true;
    else if (a == "--emu-args") o.emuArgs = next();
    else { std::fprintf(stderr, "unknown option %s\n", a.c_str()); return 2; }
  }
  try {
    if (o.list) { printList(o.json); return 0; }
    const Run r = resolve(o);
    if (!o.dumpImage.empty()) { dumpImage(o, r); return 0; }
    if (!o.emu && !(o.budget > 0 && o.budget <= 9.0)) throw std::runtime_error("--budget must be in (0, 9] seconds");
    if (o.window == 0 || o.window > 1200000000ull) throw std::runtime_error("--window must be in (0, 1.2e9] cycles");
    if (!o.emu && !o.buffersOnly) checkOneCard();
    const auto elf = readFile(o.kernel);
    if (elf.empty()) throw std::runtime_error("cannot read kernel " + o.kernel);
    const auto tb = Clock::now();
    const Buffers bufs = buildBuffers(o, r);   // before the device is opened: the hold is the launches only
    std::fprintf(stderr, "buffers built in %.2f s\n", secondsSince(tb));
    if (o.buffersOnly) return 0;
    Session dev(o, elf);
    return run(o, r, bufs, dev);
  } catch (const std::exception& e) {
    std::fprintf(stderr, "FAIL: %s\n", e.what());
    return 1;
  }
}
