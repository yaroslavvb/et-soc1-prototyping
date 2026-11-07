// desk stub (E184 syntax check only): the libetrt calls main.cpp makes, with plausible signatures
#pragma once
#include <chrono>
#include <cstddef>
#include <cstdint>
#include <memory>
#include <string>
#include <vector>
#include "runtime/Types.h"
namespace dev { class IDeviceLayer; }
namespace rt {
struct LoadResult { EventId event_; KernelId kernel_; };
struct StreamError { std::string getString() const { return {}; } };
class KernelLaunchOptions { public: void setShireMask(uint64_t) {} void setBarrier(bool) {} };
class IRuntime {
 public:
  static std::unique_ptr<IRuntime> create(std::shared_ptr<dev::IDeviceLayer>);
  std::vector<DeviceId> getDevices();
  StreamId createStream(DeviceId);
  LoadResult loadCode(StreamId, const std::byte*, size_t);
  void waitForEvent(EventId);
  std::byte* mallocDevice(DeviceId, size_t);
  void freeDevice(DeviceId, std::byte*);
  void unloadCode(KernelId);
  void destroyStream(StreamId);
  void memcpyHostToDevice(StreamId, const std::byte*, std::byte*, size_t);
  void memcpyDeviceToHost(StreamId, const std::byte*, std::byte*, size_t);
  bool waitForStream(StreamId);
  bool waitForStream(StreamId, std::chrono::seconds);
  void kernelLaunch(StreamId, KernelId, const std::byte*, size_t, KernelLaunchOptions);
  EventId abortStream(StreamId);
  std::vector<StreamError> retrieveStreamErrors(StreamId);
};
using RuntimePtr = std::unique_ptr<IRuntime>;
}
