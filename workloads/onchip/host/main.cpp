// Does shire-to-shire communication beat main memory? Every measurement prints one line
//   ONCHIP {json}
//
//   onchip_host [--sysemu] --test probe [--shift K] [--method 0|1] [--shires MASK]
//   onchip_host [--sysemu] --test relay --medium dram|scp|hop [--stage-bytes B] [--stages K]
//               [--shires MASK] [--reps N]
//
// The card is shared, so the device is open only while measuring.
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
#include <sstream>
#include <string>
#include <vector>

#include "Constants.h"
#include "onchip_args.h"

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

struct Options {
  bool sysemu = false;
  std::string simArgs, test = "probe", medium = "dram";
  uint64_t shift = 0, method = 0, shireMask = 0xffffffff;
  uint64_t stageBytes = 1024 * 1024, stages = 8, reps = 1, work = 1, hopDist = 1;
  double budget = 8.0;
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
    results_ = rt_->mallocDevice(dev_, OC_MAX_MINIONS * sizeof(OcResult));
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
  void zero(std::byte* p, size_t bytes) {
    const std::vector<uint8_t> z(bytes, 0);
    rt_->memcpyHostToDevice(stream_, reinterpret_cast<const std::byte*>(z.data()), p, bytes);
    rt_->waitForStream(stream_);
  }
  bool overBudget() const { return secondsSince(tOpen_) > o_.budget; }

  long long t0Ms = 0, t1Ms = 0;  // epoch bounds of the last launch, for lining up with power samples

  bool launch(OcArgs a, std::vector<OcResult>& res, double& wallS) {
    res.assign(OC_MAX_MINIONS, OcResult{});
    rt_->memcpyHostToDevice(stream_, reinterpret_cast<const std::byte*>(res.data()), results_,
                            res.size() * sizeof(OcResult));
    rt_->waitForStream(stream_);
    a.shire_mask = o_.shireMask;
    a.results = reinterpret_cast<uint64_t>(results_);
    a.poll_limit = 1ull << 22;
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
                            res.size() * sizeof(OcResult));
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

// Reference for OC_PAT, so the host can check what the card read.
uint32_t pat(uint64_t shire, uint64_t minion, uint64_t k) {
  return 0x5A000000u | (uint32_t)(shire << 19) | (uint32_t)(minion << 14) | (uint32_t)k;
}

int testProbe(const Options& o, Session& dev) {
  // Launch 1: every minion writes its pattern into its own shire's scratchpad.
  OcArgs w{};
  w.mode = OC_WRITE;
  w.method = o.method;
  std::vector<OcResult> res;
  double wallS = 0;
  const bool okW = dev.launch(w, res, wallS);
  uint64_t wrote = 0, wrongSelf = 0;
  for (const auto& r : res) {
    if (r.magic != OC_MAGIC) continue;
    ++wrote;
    uint64_t want = 0;
    for (uint64_t k = 0; k < OC_PROBE_BLOCK / 4; ++k) want += pat(r.minion / 32, r.minion % 32, k / 8);
    if (r.checksum != want) ++wrongSelf;
  }
  // Launch 2: every minion reads what the shire `--shift` away wrote.
  OcArgs rd{};
  rd.mode = OC_READ;
  rd.shift = o.shift ? o.shift : 1;
  std::vector<OcResult> res2;
  double wallS2 = 0;
  const bool okR = dev.launch(rd, res2, wallS2);
  uint64_t read = 0, wrongRemote = 0, badWords = 0;
  for (const auto& r : res2) {
    if (r.magic != OC_MAGIC) continue;
    ++read;
    badWords += r.errors;
    if (r.errors) ++wrongRemote;
  }
  const bool ok = okW && okR && wrote && read && !wrongSelf && !wrongRemote;
  std::printf("ONCHIP {\"test\":\"probe\",\"method\":%llu,\"method_name\":\"%s\",\"shift\":%llu,"
              "\"minions_wrote\":%llu,\"self_readback_wrong\":%llu,\"minions_read\":%llu,"
              "\"remote_blocks_wrong\":%llu,\"remote_words_wrong\":%llu,\"wall_s\":%.6f,\"ok\":%s}\n",
              (unsigned long long)o.method, o.method == 0 ? "tensor_store" : "vector_stores",
              (unsigned long long)o.shift, (unsigned long long)wrote, (unsigned long long)wrongSelf,
              (unsigned long long)read, (unsigned long long)wrongRemote, (unsigned long long)badWords,
              wallS + wallS2, ok ? "true" : "false");
  std::fflush(stdout);
  return ok ? 0 : 1;
}


// The experiment: K stages over a slab per shire, changing only where the intermediate lives.
int testRelay(const Options& o, Session& dev) {
  const uint64_t shires = (uint64_t)__builtin_popcountll(o.shireMask);
  const uint64_t medium = o.medium == "dram" ? OC_MEM_DRAM : o.medium == "scp" ? OC_MEM_SCP : OC_MEM_HOP;
  if (o.medium != "dram" && o.medium != "scp" && o.medium != "hop") {
    throw std::runtime_error("--medium wants dram, scp or hop");
  }
  if (medium != OC_MEM_DRAM && 256 * 1024 + 2 * o.stageBytes > OC_SCP_BYTES) {
    throw std::runtime_error("--stage-bytes too large: 256 KB + two buffers must fit the 2.5 MB scratchpad");
  }
  if (o.stageBytes % (32 * 512)) {
    throw std::runtime_error("--stage-bytes must be a multiple of 16 KB (32 minions x 512 B blocks)");
  }
  OcArgs a{};
  a.mode = OC_RELAY;
  a.medium = medium;
  a.stage_bytes = o.stageBytes;
  a.stages = o.stages;
  a.work = o.work;
  a.shift = o.shift;  // debug: stop after phase 1, 2 or 3
  a.hop_dist = o.hopDist;
  // Offset 0 of a shire's scratchpad faults; start the buffers 256 KB in, which leaves room for two of
  // them inside the 2.5 MB.
  a.scp_a = 256 * 1024;
  a.scp_b = 256 * 1024 + o.stageBytes;
  // Two DRAM slabs are always allocated: the on-chip media still need the barrier counter, and allocating
  // the same memory either way keeps page placement out of the comparison.
  std::byte* da = dev.alloc(32 * o.stageBytes);
  std::byte* db = dev.alloc(32 * o.stageBytes);
  std::byte* ctr = dev.alloc(64);
  dev.zero(ctr, 64);
  a.dram_a = reinterpret_cast<uint64_t>(da);
  a.dram_b = reinterpret_cast<uint64_t>(db);
  a.counter = reinterpret_cast<uint64_t>(ctr);

  std::vector<OcResult> res;
  double wallS = 0;
  const bool ok = dev.launch(a, res, wallS);
  uint64_t n = 0, bad = 0, cmax = 0, bytes = 0;
  double csum = 0;
  // The value shire 0 ends up holding, decoded from its checksum. With --medium hop it is the value shire
  // (0 - stages) mod 32 started with, which is how the run shows the data really crossed shires.
  float shire0 = 0;
  for (const auto& r : res) {
    if (r.magic != OC_MAGIC) continue;
    if (r.minion == 0 && r.bytes) {
      const uint32_t bits = (uint32_t)(r.checksum / (o.stageBytes / 32 / 4));
      std::memcpy(&shire0, &bits, 4);
    }
    ++n;
    bad += r.errors;
    cmax = std::max<uint64_t>(cmax, r.cycles);
    csum += double(r.cycles);
    bytes += r.bytes;
  }
  // Bytes moved is one read plus one write of every element, every stage. Rates come from the on-device
  // cycle counter, not the wall clock: a launch costs a few hundred microseconds either way, which would
  // swamp the thing being measured.
  const double bpc = cmax ? double(bytes) / double(cmax) : 0;       // bytes per cycle, chip-wide
  const double gbs = bpc * 0.6;                                     // GB/s at the 600 MHz the card is pinned to
  const double perElem = o.stageBytes / 4.0 * shires * o.stages;    // elements processed
  const double flops = perElem * o.work;                            // one fadd.ps per lane per pass
  std::printf("ONCHIP {\"test\":\"relay\",\"medium\":\"%s\",\"hop_distance\":%llu,"
              "\"stage_bytes\":%llu,\"stages\":%llu,"
              "\"work\":%llu,\"shires\":%llu,\"minions\":%llu,\"bytes\":%llu,\"cycles_max\":%llu,"
              "\"cycles_mean\":%.0f,\"wall_s\":%.6f,\"bytes_per_cycle\":%.3f,\"gb_s\":%.2f,"
              "\"flop_per_byte\":%.4f,\"gflop_s\":%.2f,\"shire0_final\":%.1f,\"wrong_elements\":%llu,"
              "\"t_start_ms\":%lld,\"t_end_ms\":%lld,\"ok\":%s}\n",
              o.medium.c_str(), (unsigned long long)o.hopDist, (unsigned long long)o.stageBytes,
              (unsigned long long)o.stages,
              (unsigned long long)o.work, (unsigned long long)shires, (unsigned long long)n,
              (unsigned long long)bytes, (unsigned long long)cmax, n ? csum / double(n) : 0.0, wallS, bpc,
              gbs, o.work / 8.0, cmax ? flops / double(cmax) * 0.6 : 0.0, (double)shire0,
              (unsigned long long)bad, dev.t0Ms, dev.t1Ms, (ok && n && !bad) ? "true" : "false");
  std::fflush(stdout);
  return (ok && n && !bad) ? 0 : 1;
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
    else if (a == "--test") o.test = next();
    else if (a == "--medium") o.medium = next();
    else if (a == "--shift") o.shift = std::strtoull(next().c_str(), nullptr, 0);
    else if (a == "--method") o.method = std::strtoull(next().c_str(), nullptr, 0);
    else if (a == "--shires") o.shireMask = std::strtoull(next().c_str(), nullptr, 0);
    else if (a == "--stage-bytes") o.stageBytes = parseSize(next());
    else if (a == "--stages") o.stages = std::strtoull(next().c_str(), nullptr, 0);
    else if (a == "--reps") o.reps = std::strtoull(next().c_str(), nullptr, 0);
    else if (a == "--work") o.work = std::strtoull(next().c_str(), nullptr, 0);
    else if (a == "--hop-distance") o.hopDist = std::strtoull(next().c_str(), nullptr, 0);
    else if (a == "--budget") o.budget = std::strtod(next().c_str(), nullptr);
    else if (a == "--kernel") o.kernel = next();
    else { std::fprintf(stderr, "unknown option %s\n", a.c_str()); return 2; }
  }
  try {
    const auto elf = readFile(o.kernel);
    if (elf.empty()) throw std::runtime_error("cannot read kernel " + o.kernel);
    Session dev(o, elf);
    if (o.test == "probe") return testProbe(o, dev);
    if (o.test == "relay") return testRelay(o, dev);
    std::fprintf(stderr, "--test must be probe or relay\n");
    return 2;
  } catch (const std::exception& e) {
    std::fprintf(stderr, "FAIL: %s\n", e.what());
    return 1;
  }
}
