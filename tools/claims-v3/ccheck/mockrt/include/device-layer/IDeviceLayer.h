// ccheck's mock build: the two factory calls main.cpp makes.
#pragma once
#include <memory>
namespace emu { struct SysEmuOptions; }
namespace dev {
class IDeviceLayer {
public:
  virtual ~IDeviceLayer() = default;
  static std::shared_ptr<IDeviceLayer> createSysEmuDeviceLayer(const emu::SysEmuOptions&, int);
  static std::shared_ptr<IDeviceLayer> createPcieDeviceLayer(bool, bool);
};
}  // namespace dev
