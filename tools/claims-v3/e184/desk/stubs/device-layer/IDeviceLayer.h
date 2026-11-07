// desk stub (E184 syntax check only)
#pragma once
#include <memory>
namespace emu { struct SysEmuOptions; }
namespace dev { class IDeviceLayer { public:
  static std::shared_ptr<IDeviceLayer> createSysEmuDeviceLayer(const emu::SysEmuOptions&, int);
  static std::shared_ptr<IDeviceLayer> createPcieDeviceLayer(bool, bool); }; }
