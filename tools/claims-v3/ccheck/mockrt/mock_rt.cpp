// ccheck's mock runtime (Q139(k)): lets workloads/sparsity/host/main.cpp, patched or not, build and run on a machine with
// no ET runtime and no card, so the C log's whole path (poison, launch, read, log line) runs before any card sees it.
// Device memory is host memory; kernelLaunch runs a software SP_FMA: every participating minion gets the C that
// rtl-sim/fma_toggle_v2/accum.c computes for the launch's tile and iters (MOCK_ACCUM = the built engine), and a result
// record (magic, hart, count, cycles at 546 a op). Nothing here talks to a device.
//
//   MOCK_ACCUM=<accum binary>   required for --test fma
//   MOCK_SLEEP_MS=<ms>          wall time of each launch (default 40), so repeatFor calibrates a small iters
//   MOCK_FAULT=bitflip|nostore|stale|stale2|wrongn|swapab   a kernel fault to inject (default none):
//     bitflip  minion 5 (or the first participant) stores C with word 17's lowest bit flipped
//     nostore  minion 7 (or the second participant) never stores C
//     stale    after the first launch, no minion stores C
//     stale2   after the second launch, no minion stores C (the buffer then holds a launch of the same n:
//              only --c-poison can tell)
//     wrongn   every minion stores the C of iters + 1 ops
//     swapab   every minion stores the C of the tile with A and B swapped
// At exit it prints the DMA it served: host-to-device and device-to-host calls and bytes, per launch.
// SPDX-License-Identifier: Apache-2.0
#include <runtime/IRuntime.h>
#include <device-layer/IDeviceLayer.h>
#include <sw-sysemu/SysEmuOptions.h>

#include <algorithm>
#include <chrono>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <fstream>
#include <map>
#include <string>
#include <thread>
#include <vector>
#include <unistd.h>

#include "sparsity_args.h"

namespace {
struct Counters {
  unsigned long long h2dCalls = 0, h2dBytes = 0, d2hCalls = 0, d2hBytes = 0, launches = 0;
  ~Counters() {
    std::fprintf(stderr, "mock: %llu launches; host-to-device %llu calls %llu bytes; device-to-host %llu calls %llu bytes\n",
                 launches, h2dCalls, h2dBytes, d2hCalls, d2hBytes);
  }
} counters;

std::string fault() {
  const char* f = std::getenv("MOCK_FAULT");
  return f ? f : "";
}

// C after n ops of (type, A, B), from the engine, cached.
std::vector<uint8_t> engineC(uint64_t type, const uint8_t* a, const uint8_t* b, uint64_t n) {
  static std::map<std::string, std::vector<uint8_t>> cache;
  const char* tn = type == SP_FP32 ? "fp32" : type == SP_FP16 ? "fp16" : "int8";
  std::string key = std::string(tn) + ":" + std::to_string(n) + ":" + std::string((const char*)a, 1024) +
                    std::string((const char*)b, 1024);
  auto it = cache.find(key);
  if (it != cache.end()) return it->second;
  const char* exe = std::getenv("MOCK_ACCUM");
  if (!exe) {
    std::fprintf(stderr, "mock: set MOCK_ACCUM to the built accum engine\n");
    std::exit(3);
  }
  char dir[] = "./mockrt-XXXXXX";
  if (!mkdtemp(dir)) std::exit(3);
  {
    std::ofstream f(std::string(dir) + "/tile.bin", std::ios::binary);
    f.write((const char*)a, 1024);
    f.write((const char*)b, 1024);
  }
  const std::string cmd = std::string("cd ") + dir + " && " + exe + " " + tn + " tile.bin " + std::to_string(n);
  if (std::system(cmd.c_str()) != 0) std::exit(3);
  std::vector<uint8_t> c(1024);
  std::ifstream g(std::string(dir) + "/accum_" + std::to_string(n) + ".bin", std::ios::binary);
  g.read((char*)c.data(), 1024);
  std::remove((std::string(dir) + "/accum_" + std::to_string(n) + ".bin").c_str());
  std::remove((std::string(dir) + "/tile.bin").c_str());
  std::remove(dir);
  cache[key] = c;
  return c;
}
}  // namespace

namespace dev {
std::shared_ptr<IDeviceLayer> IDeviceLayer::createSysEmuDeviceLayer(const emu::SysEmuOptions&, int) {
  return std::make_shared<IDeviceLayer>();
}
std::shared_ptr<IDeviceLayer> IDeviceLayer::createPcieDeviceLayer(bool, bool) { return std::make_shared<IDeviceLayer>(); }
}  // namespace dev

namespace rt {
std::unique_ptr<IRuntime> IRuntime::create(std::shared_ptr<dev::IDeviceLayer>) { return std::make_unique<IRuntime>(); }
IRuntime::~IRuntime() = default;
std::vector<DeviceId> IRuntime::getDevices() { return {0}; }
StreamId IRuntime::createStream(DeviceId) { return 1; }
LoadCodeResult IRuntime::loadCode(StreamId, const std::byte*, size_t) { return {}; }
void IRuntime::waitForEvent(EventId) {}
bool IRuntime::waitForStream(StreamId, std::chrono::seconds) { return true; }
EventId IRuntime::abortStream(StreamId) { return {}; }
std::vector<StreamError> IRuntime::retrieveStreamErrors(StreamId) { return {}; }
std::byte* IRuntime::mallocDevice(DeviceId, size_t n) {
  auto* p = static_cast<std::byte*>(std::malloc(n));
  std::memset(p, 0x5A, n);  // device memory is not cleared: stale-looking bytes until something writes them
  return p;
}
void IRuntime::freeDevice(DeviceId, std::byte* p) { std::free(p); }
void IRuntime::memcpyHostToDevice(StreamId, const std::byte* s, std::byte* d, size_t n) {
  std::memcpy(d, s, n);
  ++counters.h2dCalls;
  counters.h2dBytes += n;
}
void IRuntime::memcpyDeviceToHost(StreamId, const std::byte* s, std::byte* d, size_t n) {
  std::memcpy(d, s, n);
  ++counters.d2hCalls;
  counters.d2hBytes += n;
}
void IRuntime::unloadCode(KernelId) {}
void IRuntime::destroyStream(StreamId) {}

void IRuntime::kernelLaunch(StreamId, KernelId, const std::byte* args, size_t bytes, KernelLaunchOptions) {
  SpArgs a;
  std::memcpy(&a, args, sizeof a < bytes ? sizeof a : bytes);
  ++counters.launches;
  const char* ms = std::getenv("MOCK_SLEEP_MS");
  std::this_thread::sleep_for(std::chrono::milliseconds(ms ? std::atoi(ms) : 40));
  if (a.mode != SP_FMA) return;
  const std::string f = fault();
  const auto* A = reinterpret_cast<const uint8_t*>(a.a_tile);
  const auto* B = reinterpret_cast<const uint8_t*>(a.b_tile);
  std::vector<uint8_t> c = f == "swapab" ? engineC(a.type, B, A, a.iters)
                         : f == "wrongn" ? engineC(a.type, A, B, a.iters + 1)
                                         : engineC(a.type, A, B, a.iters);
  std::vector<uint64_t> minions;
  for (uint64_t s = 0; s < 32; ++s) {
    if ((a.shire_mask >> s) & 1) {
      for (uint64_t m = 0; m < a.per_shire; ++m) minions.push_back(s * 32 + m);
    }
  }
  const uint64_t flipM = std::find(minions.begin(), minions.end(), 5) != minions.end() ? 5 : minions.front();
  const uint64_t skipM = std::find(minions.begin(), minions.end(), 7) != minions.end() ? 7 : minions.at(1 % minions.size());
  for (uint64_t m : minions) {
    const bool store = !(f == "nostore" && m == skipM) && !(f == "stale" && counters.launches > 1) &&
                        !(f == "stale2" && counters.launches > 2);
    if (store) {
      auto* out = reinterpret_cast<uint8_t*>(a.out) + m * SP_TILE_BYTES;
      std::memcpy(out, c.data(), 1024);
      if (f == "bitflip" && m == flipM) out[17 * 4] ^= 1;
    }
    auto* r = reinterpret_cast<SpResult*>(a.results) + m * 2;
    r->cycles = a.iters * 546;
    r->count = a.iters;
    r->aux = r->aux2 = 0;
    r->t_entry = 0;
    r->t_exit = r->cycles + 100;
    r->hart = uint32_t(m * 2);
    r->tensor_error = 0;
    r->magic = SP_MAGIC;
  }
}
}  // namespace rt
