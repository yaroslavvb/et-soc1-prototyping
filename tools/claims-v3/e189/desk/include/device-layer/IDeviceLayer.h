// E189's desk mock (Q167, the kit): the two factory calls both hosts make. The check of C's mock header returns shared_ptr; sparse parity's
// host needs unique_ptr (it returns the factory's result from a function typed std::unique_ptr<dev::IDeviceLayer>), and the ledger host
// stores it in a shared_ptr, which takes either. SPDX-License-Identifier: Apache-2.0
#pragma once
#include <memory>
namespace emu { struct SysEmuOptions; }
namespace dev {
class IDeviceLayer {
public:
  virtual ~IDeviceLayer() = default;
  static std::unique_ptr<IDeviceLayer> createSysEmuDeviceLayer(const emu::SysEmuOptions&, int);
  static std::unique_ptr<IDeviceLayer> createPcieDeviceLayer(bool, bool);
};
}  // namespace dev
