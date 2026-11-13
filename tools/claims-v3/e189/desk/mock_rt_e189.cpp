// E189 (Q167, the kit, Thu 12 Nov 2026, before any E189 datum): the desk's DEVICE-RECORDING mock runtime, so that the two hosts E189 runs
// (workloads/ledger/host/main.cpp at 46a16bd0 and workloads/sparseparity/host/main.cpp) build on the Intel with no ET runtime and no
// card, and the kit's behavioural host check (hostcheck_e189.sh) can be shown to reach NO device call. It is compiled against the check
// of C's mock headers widened by sparse parity's calls (desk/include/, beside this file; the check of C's own stay as committed). Every call into the device layer or the
// runtime appends one line, "MOCKDEV <call>", to the file named by E189_DEVICE_RECORD when that variable is set (E183's kit note 4's
// device record, E188's form); the device layer then reports NO device, so a host that reached Session's constructor would stop there
// ("no ET devices found") after leaving its record. Nothing here talks to a device, and it never runs on a box.
// SPDX-License-Identifier: Apache-2.0
#include <runtime/IRuntime.h>
#include <device-layer/IDeviceLayer.h>
#include <sw-sysemu/SysEmuOptions.h>

#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <new>
#include <string>

namespace {
void rec(const char* what) {
  const char* f = std::getenv("E189_DEVICE_RECORD");
  if (!f || !*f) return;
  if (std::FILE* o = std::fopen(f, "a")) {
    std::fprintf(o, "MOCKDEV %s\n", what);
    std::fclose(o);
  }
}
class MockDL : public dev::IDeviceLayer {};
}  // namespace

namespace dev {
std::unique_ptr<IDeviceLayer> IDeviceLayer::createSysEmuDeviceLayer(const emu::SysEmuOptions&, int) {
  rec("createSysEmuDeviceLayer");
  return std::unique_ptr<IDeviceLayer>(new MockDL());
}
std::unique_ptr<IDeviceLayer> IDeviceLayer::createPcieDeviceLayer(bool, bool) {
  rec("createPcieDeviceLayer");
  return std::unique_ptr<IDeviceLayer>(new MockDL());
}
}  // namespace dev

namespace rt {
std::unique_ptr<IRuntime> IRuntime::create(std::shared_ptr<dev::IDeviceLayer>) {
  rec("IRuntime::create");
  return std::unique_ptr<IRuntime>(new IRuntime());
}
IRuntime::~IRuntime() {}
std::vector<DeviceId> IRuntime::getDevices() { rec("getDevices"); return {}; }   // no device: Session stops here
DeviceProperties IRuntime::getDeviceProperties(DeviceId) { rec("getDeviceProperties"); return {}; }
StreamId IRuntime::createStream(DeviceId) { rec("createStream"); return 1; }
LoadCodeResult IRuntime::loadCode(StreamId, const std::byte*, size_t) { rec("loadCode"); return {}; }
bool IRuntime::waitForEvent(EventId, std::chrono::seconds) { rec("waitForEvent"); return false; }
bool IRuntime::waitForStream(StreamId, std::chrono::seconds) { rec("waitForStream"); return false; }
EventId IRuntime::abortStream(StreamId) { rec("abortStream"); return {}; }
std::vector<StreamError> IRuntime::retrieveStreamErrors(StreamId) { rec("retrieveStreamErrors"); return {}; }
std::byte* IRuntime::mallocDevice(DeviceId, size_t n, uint32_t) { rec("mallocDevice"); return static_cast<std::byte*>(std::malloc(n ? n : 1)); }
void IRuntime::freeDevice(DeviceId, std::byte* p) { rec("freeDevice"); std::free(p); }
void IRuntime::memcpyHostToDevice(StreamId, const std::byte*, std::byte*, size_t) { rec("memcpyHostToDevice"); }
void IRuntime::memcpyDeviceToHost(StreamId, const std::byte*, std::byte*, size_t) { rec("memcpyDeviceToHost"); }
void IRuntime::kernelLaunch(StreamId, KernelId, const std::byte*, size_t, KernelLaunchOptions) { rec("kernelLaunch"); }
void IRuntime::unloadCode(KernelId) { rec("unloadCode"); }
void IRuntime::destroyStream(StreamId) { rec("destroyStream"); }
}  // namespace rt
