// E184 (the kit's desk test of the host-only change): a mock of the libetrt calls the energy catalogue's host makes, so the patched
// host/main.cpp (host_patch_e184.py) can be compiled and run on the Intel against desk/stubs/ (never on a box, never with a card).
// Device memory is host memory; a launch fills one EcResult per participating hart (both harts of 32 minions of every shire in the
// launch's shire mask), cycles = the window, iters = window / 168 (fadd.ps's 64 ops at about 0.38 ops a cycle a hart), and sleeps
// E184_MOCK_LAUNCH_MS (default 5 ms). It also records every source-buffer copy's sha256-free fingerprint (the count of nonzero words)
// on stderr, so a desk test can see which image each segment carried.
// SPDX-License-Identifier: Apache-2.0
#include "runtime/IRuntime.h"
#include "device-layer/IDeviceLayer.h"
#include "sw-sysemu/SysEmuOptions.h"
#include "enercat_args.h"

#include <chrono>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <thread>

namespace dev {
std::shared_ptr<IDeviceLayer> IDeviceLayer::createSysEmuDeviceLayer(const emu::SysEmuOptions&, int) { return std::make_shared<IDeviceLayer>(); }
std::shared_ptr<IDeviceLayer> IDeviceLayer::createPcieDeviceLayer(bool, bool) { return std::make_shared<IDeviceLayer>(); }
}

namespace rt {
std::unique_ptr<IRuntime> IRuntime::create(std::shared_ptr<dev::IDeviceLayer>) { return std::make_unique<IRuntime>(); }
std::vector<DeviceId> IRuntime::getDevices() { return {DeviceId(0)}; }
StreamId IRuntime::createStream(DeviceId) { return StreamId(0); }
LoadResult IRuntime::loadCode(StreamId, const std::byte*, size_t) { return LoadResult{EventId(0), KernelId(0)}; }
void IRuntime::waitForEvent(EventId) {}
std::byte* IRuntime::mallocDevice(DeviceId, size_t n) { return static_cast<std::byte*>(std::calloc(n ? n : 1, 1)); }
void IRuntime::freeDevice(DeviceId, std::byte* p) { std::free(p); }
void IRuntime::unloadCode(KernelId) {}
void IRuntime::destroyStream(StreamId) {}
void IRuntime::memcpyHostToDevice(StreamId, const std::byte* src, std::byte* dst, size_t n) {
  std::memcpy(dst, src, n);
  if (n == EC_MAX_HARTS * 256) {
    size_t nz = 0;
    const uint32_t* w = reinterpret_cast<const uint32_t*>(src);
    for (size_t i = 0; i < n / 4; ++i) nz += w[i] != 0;
    std::fprintf(stderr, "MOCK sources copied: %zu nonzero words\n", nz);
  }
}
void IRuntime::memcpyDeviceToHost(StreamId, const std::byte* src, std::byte* dst, size_t n) { std::memcpy(dst, src, n); }
bool IRuntime::waitForStream(StreamId) { return true; }
bool IRuntime::waitForStream(StreamId, std::chrono::seconds) { return true; }
void IRuntime::kernelLaunch(StreamId, KernelId, const std::byte* args, size_t n, KernelLaunchOptions) {
  EcArgs a{};
  std::memcpy(&a, args, n < sizeof a ? n : sizeof a);
  EcResult* r = reinterpret_cast<EcResult*>(a.results);
  for (int s = 0; s < 32; ++s) {
    if (!((a.shire_mask >> s) & 1)) continue;
    for (int m = 0; m < 32; ++m)
      for (int t = 0; t < (a.harts >= 2 ? 2 : 1); ++t) {
        EcResult& x = r[s * 64 + m * 2 + t];
        x.cycles = a.window; x.iters = a.window / 168; x.bytes = 0; x.hart = uint32_t(s * 64 + m * 2 + t); x.magic = EC_MAGIC;
      }
  }
  const char* ms = std::getenv("E184_MOCK_LAUNCH_MS");
  std::this_thread::sleep_for(std::chrono::milliseconds(ms ? std::atoi(ms) : 5));
}
EventId IRuntime::abortStream(StreamId) { return EventId(0); }
std::vector<StreamError> IRuntime::retrieveStreamErrors(StreamId) { return {}; }
}
