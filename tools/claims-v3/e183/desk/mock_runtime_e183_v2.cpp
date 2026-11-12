// E183 (the kit's dated note 4, KIT.md.dated-note-4.md, Thu 12 Nov 2026): E183's mock of the libetrt and device-layer calls the energy
// catalogue's host makes (desk/mock_runtime_e183.cpp, cc597bf2, which stays as committed), with ONE addition: every call into the device
// layer or the runtime appends one line, "MOCKDEV <call>", to the file named by E183_DEVICE_RECORD when that variable is set (nothing is
// written when it is not). The record is the desk's evidence of whether a run of the host reached the device: the host's first device
// call is IDeviceLayer::createPcieDeviceLayer (main.cpp, Session's constructor), so a run that leaves the record empty opened no device.
// Everything else is E183's mock, line for line: device memory is host memory; a launch fills one EcResult per participating hart, prints
// its sources word and sleeps E183_MOCK_LAUNCH_MS; every source-buffer copy prints its count of nonzero words. It is compiled against
// E184's desk stubs (tools/claims-v3/e184/desk/stubs), unchanged. Never on a box, never with a card.
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

namespace {
void rec(const char* call) {   // note 4: the device record
  const char* p = std::getenv("E183_DEVICE_RECORD");
  if (!p || !*p) return;
  if (std::FILE* f = std::fopen(p, "a")) {
    std::fprintf(f, "MOCKDEV %s\n", call);
    std::fclose(f);
  }
}
}  // namespace

namespace dev {
std::shared_ptr<IDeviceLayer> IDeviceLayer::createSysEmuDeviceLayer(const emu::SysEmuOptions&, int) { rec("createSysEmuDeviceLayer"); return std::make_shared<IDeviceLayer>(); }
std::shared_ptr<IDeviceLayer> IDeviceLayer::createPcieDeviceLayer(bool, bool) { rec("createPcieDeviceLayer"); return std::make_shared<IDeviceLayer>(); }
}

namespace rt {
std::unique_ptr<IRuntime> IRuntime::create(std::shared_ptr<dev::IDeviceLayer>) { rec("IRuntime::create"); return std::make_unique<IRuntime>(); }
std::vector<DeviceId> IRuntime::getDevices() { rec("getDevices"); return {DeviceId(0)}; }
StreamId IRuntime::createStream(DeviceId) { rec("createStream"); return StreamId(0); }
LoadResult IRuntime::loadCode(StreamId, const std::byte*, size_t) { rec("loadCode"); return LoadResult{EventId(0), KernelId(0)}; }
void IRuntime::waitForEvent(EventId) { rec("waitForEvent"); }
std::byte* IRuntime::mallocDevice(DeviceId, size_t n) { rec("mallocDevice"); return static_cast<std::byte*>(std::calloc(n ? n : 1, 1)); }
void IRuntime::freeDevice(DeviceId, std::byte* p) { rec("freeDevice"); std::free(p); }
void IRuntime::unloadCode(KernelId) { rec("unloadCode"); }
void IRuntime::destroyStream(StreamId) { rec("destroyStream"); }
void IRuntime::memcpyHostToDevice(StreamId, const std::byte* src, std::byte* dst, size_t n) {
  rec("memcpyHostToDevice");
  std::memcpy(dst, src, n);
  if (n == EC_MAX_HARTS * 256) {
    size_t nz = 0;
    const uint32_t* w = reinterpret_cast<const uint32_t*>(src);
    for (size_t i = 0; i < n / 4; ++i) nz += w[i] != 0;
    std::fprintf(stderr, "MOCK sources copied: %zu nonzero words\n", nz);
  }
}
void IRuntime::memcpyDeviceToHost(StreamId, const std::byte* src, std::byte* dst, size_t n) { rec("memcpyDeviceToHost"); std::memcpy(dst, src, n); }
bool IRuntime::waitForStream(StreamId) { rec("waitForStream"); return true; }
bool IRuntime::waitForStream(StreamId, std::chrono::seconds) { rec("waitForStream"); return true; }
void IRuntime::kernelLaunch(StreamId, KernelId, const std::byte* args, size_t n, KernelLaunchOptions) {
  rec("kernelLaunch");
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
  std::fprintf(stderr, "MOCK launch sources word0 %08x\n", *reinterpret_cast<const uint32_t*>(a.sources));   // E183
  const char* ms = std::getenv("E183_MOCK_LAUNCH_MS");
  std::this_thread::sleep_for(std::chrono::milliseconds(ms ? std::atoi(ms) : 5));
}
EventId IRuntime::abortStream(StreamId) { rec("abortStream"); return EventId(0); }
std::vector<StreamError> IRuntime::retrieveStreamErrors(StreamId) { rec("retrieveStreamErrors"); return {}; }
}
