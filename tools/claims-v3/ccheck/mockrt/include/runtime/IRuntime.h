// ccheck's mock build: the runtime calls workloads/sparsity/host/main.cpp makes, with the same signatures as far as
// main.cpp can tell. mock_rt.cpp implements them on host memory, with a software kernel for --test fma.
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
  StreamId createStream(DeviceId);
  LoadCodeResult loadCode(StreamId, const std::byte*, size_t);
  void waitForEvent(EventId);
  bool waitForStream(StreamId, std::chrono::seconds timeout = std::chrono::seconds(0));
  EventId abortStream(StreamId);
  std::vector<StreamError> retrieveStreamErrors(StreamId);
  std::byte* mallocDevice(DeviceId, size_t);
  void freeDevice(DeviceId, std::byte*);
  void memcpyHostToDevice(StreamId, const std::byte* src, std::byte* dst, size_t bytes);
  void memcpyDeviceToHost(StreamId, const std::byte* src, std::byte* dst, size_t bytes);
  void kernelLaunch(StreamId, KernelId, const std::byte* args, size_t bytes, KernelLaunchOptions);
  void unloadCode(KernelId);
  void destroyStream(StreamId);
};
using RuntimePtr = std::unique_ptr<IRuntime>;
}  // namespace rt
