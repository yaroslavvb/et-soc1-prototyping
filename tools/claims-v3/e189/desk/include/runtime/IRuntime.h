// E189's desk mock (Q167, the kit): the runtime calls the two hosts E189 runs make (workloads/ledger/host/main.cpp and
// workloads/sparseparity/host/main.cpp), with the same signatures as far as those sources can tell. It is the check of C's mock header
// (tools/claims-v3/ccheck/mockrt/include/runtime/IRuntime.h, which stays as committed) widened by sparse parity's calls:
// getDeviceProperties, a timed waitForEvent returning bool, and mallocDevice's alignment. desk/mock_rt_e189.cpp records every call.
// SPDX-License-Identifier: Apache-2.0
#pragma once
#include <chrono>
#include <cstddef>
#include <cstdint>
#include <memory>
#include <string>
#include <vector>
namespace dev { class IDeviceLayer; }
namespace rt {
using DeviceId = int;
using StreamId = int;
using KernelId = int;
struct EventId { int id = 0; };
struct LoadCodeResult { EventId event_; KernelId kernel_ = 0; };
struct DeviceProperties { uint64_t computeMinionShireMask_ = 0; uint64_t l2scratchpadSize_ = 0; };
class KernelLaunchOptions {
public:
  void setShireMask(uint64_t m) { shireMask = m; }
  void setBarrier(bool b) { barrier = b; }
  uint64_t shireMask = 0;
  bool barrier = false;
};
struct StreamError {
  std::string s;
  std::string getString() const { return s; }
};
class IRuntime {
public:
  static std::unique_ptr<IRuntime> create(std::shared_ptr<dev::IDeviceLayer>);
  virtual ~IRuntime();
  std::vector<DeviceId> getDevices();
  DeviceProperties getDeviceProperties(DeviceId);
  StreamId createStream(DeviceId);
  LoadCodeResult loadCode(StreamId, const std::byte*, size_t);
  bool waitForEvent(EventId, std::chrono::seconds timeout = std::chrono::seconds(0));
  bool waitForStream(StreamId, std::chrono::seconds timeout = std::chrono::seconds(0));
  EventId abortStream(StreamId);
  std::vector<StreamError> retrieveStreamErrors(StreamId);
  std::byte* mallocDevice(DeviceId, size_t, uint32_t alignment = 64);
  void freeDevice(DeviceId, std::byte*);
  void memcpyHostToDevice(StreamId, const std::byte* src, std::byte* dst, size_t bytes);
  void memcpyDeviceToHost(StreamId, const std::byte* src, std::byte* dst, size_t bytes);
  void kernelLaunch(StreamId, KernelId, const std::byte* args, size_t bytes, KernelLaunchOptions);
  void unloadCode(KernelId);
  void destroyStream(StreamId);
};
using RuntimePtr = std::unique_ptr<IRuntime>;
}  // namespace rt
