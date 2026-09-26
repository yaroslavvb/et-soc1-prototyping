// Checks the counter-configure syscall (see ../README.md).
//   pmcsel_host [--sysemu [--fw-dir build/fw-build]] [--event N] [--iters N]
#include <g3log/loglevels.hpp>
#include <runtime/IRuntime.h>
#include <runtime/Types.h>
#include <device-layer/IDeviceLayer.h>
#include <sw-sysemu/SysEmuOptions.h>

#include <chrono>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <filesystem>
#include <fstream>
#include <limits>
#include <map>
#include <sstream>
#include <string>
#include <vector>


#include "Constants.h"
#include "pmcsel_args.h"

// libetrt's thread-pool workers log at the custom levels VERBOSE_HIGH/MID/LOW, which only logging::LoggerDefault
// registers with g3log. Left unregistered, the first log call from several new workers inserts the level into g3log's
// level map from all of them at once and can corrupt it: aifoundry3's host crash about 1.08 s into 1 launch in 100
// (docs/findings/14-card-behaviour.md, "Traps"). Registering them, disabled as the map's default would leave them,
// before the runtime starts any thread removes the race.
static void registerRuntimeLogLevels() {
  const LEVELS levels[] = {LEVELS(g3::kDebugValue - 100, "VERBOSE_HIGH"), LEVELS(g3::kDebugValue - 99, "VERBOSE_MID"),
                           LEVELS(g3::kDebugValue - 98, "VERBOSE_LOW")};
  for (const auto& l : levels) g3::only_change_at_initialization::addLogLevel(l, false);
}

namespace fs = std::filesystem;
using Clock = std::chrono::steady_clock;

namespace {

std::vector<std::byte> readFile(const std::string& path) {
  std::ifstream file(path, std::ios::binary);
  if (!file) {
    return {};
  }
  std::vector<std::byte> data(fs::file_size(path));
  file.read(reinterpret_cast<char*>(data.data()), static_cast<std::streamsize>(data.size()));
  return data;
}

}  // namespace

int main(int argc, char** argv) {
  registerRuntimeLogLevels();  // first, before any library starts a thread
  bool sysemu = false;
  uint64_t event = 2, iters = 100000;
  std::string fwDir, kernelPath = KERNEL_ELF;
  for (int i = 1; i < argc; ++i) {
    std::string a = argv[i];
    auto next = [&]() -> std::string { if (i + 1 >= argc) { std::fprintf(stderr, "%s needs a value\n", a.c_str()); std::exit(2); } return argv[++i]; };
    if (a == "--sysemu") sysemu = true;
    else if (a == "--event") event = std::strtoull(next().c_str(), nullptr, 0);
    else if (a == "--iters") iters = std::strtoull(next().c_str(), nullptr, 0);
    else if (a == "--fw-dir") fwDir = next();  // a device-minion-runtime build dir: uses its rebuilt minion ELFs (simulator only)
    else if (a == "--kernel") kernelPath = next();
    else { std::fprintf(stderr, "unknown option %s\n", a.c_str()); return 2; }
  }
  const auto elfBytes = readFile(kernelPath);
  if (elfBytes.empty()) {
    std::fprintf(stderr, "cannot read kernel %s\n", kernelPath.c_str());
    return 1;
  }
  try {
    std::shared_ptr<dev::IDeviceLayer> dl;
    if (sysemu) {
      emu::SysEmuOptions s;
      s.bootromTrampolineToBL2ElfPath = BOOTROM_TRAMPOLINE_TO_BL2_ELF;
      s.spBL2ElfPath = BL2_ELF;
      s.masterMinionElfPath = fwDir.empty() ? MASTER_MINION_ELF : fwDir + "/src/MasterMinion/MasterMinion.elf";
      s.machineMinionElfPath = fwDir.empty() ? MACHINE_MINION_ELF : fwDir + "/src/MachineMinion/MachineMinion.elf";
      s.workerMinionElfPath = fwDir.empty() ? WORKER_MINION_ELF : fwDir + "/src/WorkerMinion/WorkerMinion.elf";
      s.executablePath = fs::path(SYSEMU_INSTALL_DIR) / "sys_emu";
      s.runDir = fs::current_path();
      s.maxCycles = std::numeric_limits<uint64_t>::max();
      s.minionShiresMask = 0x1FFFFFFFFu;
      s.puUart0Path = s.runDir + "/pu_uart0_tx.log";
      s.puUart1Path = s.runDir + "/pu_uart1_tx.log";
      s.spUart0Path = s.runDir + "/spio_uart0_tx.log";
      s.spUart1Path = s.runDir + "/spio_uart1_tx.log";
      s.startGdb = false;
      dl = dev::IDeviceLayer::createSysEmuDeviceLayer(s, 1);
    } else {
      dl = dev::IDeviceLayer::createPcieDeviceLayer(true, false);
    }
    auto rt = rt::IRuntime::create(dl);
    const auto dev = rt->getDevices().at(0);
    const auto stream = rt->createStream(dev);
    const auto load = rt->loadCode(stream, elfBytes.data(), elfBytes.size());
    rt->waitForEvent(load.event_);
    std::byte* dRes = rt->mallocDevice(dev, sizeof(PsResult));
    PsResult res{};
    rt->memcpyHostToDevice(stream, reinterpret_cast<const std::byte*>(&res), dRes, sizeof(res));
    PsArgs args{reinterpret_cast<uint64_t>(dRes), event, iters};
    rt::KernelLaunchOptions opts;
    opts.setShireMask(0x1);
    opts.setBarrier(true);
    rt->kernelLaunch(stream, load.kernel_, reinterpret_cast<const std::byte*>(&args), sizeof(args), opts);
    bool ok = rt->waitForStream(stream, std::chrono::seconds(sysemu ? 3600 : 6));
    for (const auto& e : rt->retrieveStreamErrors(stream)) {
      std::fprintf(stderr, "stream error: %s\n", e.getString().c_str());
      ok = false;
    }
    rt->memcpyDeviceToHost(stream, dRes, reinterpret_cast<std::byte*>(&res), sizeof(res));
    rt->waitForStream(stream);
    rt->freeDevice(dev, dRes);
    rt->unloadCode(load.kernel_);
    rt->destroyStream(stream);
    ok = ok && res.magic == PS_MAGIC;
    std::printf("PMCSEL {\"event\":%llu,\"iters\":%llu,\"rc_core\":%lld,\"rc_bad\":%lld,\"rc_sc\":%lld,"
                "\"hpm6_delta\":%llu,\"hpm4_delta\":%llu,\"ok\":%s}\n",
                (unsigned long long)event, (unsigned long long)iters, (long long)res.rc_core, (long long)res.rc_bad,
                (long long)res.rc_sc, (unsigned long long)(res.c6_after - res.c6_before),
                (unsigned long long)(res.c4_after - res.c4_before), ok ? "true" : "false");
    return ok ? 0 : 1;
  } catch (const std::exception& e) {
    std::fprintf(stderr, "FAIL: %s\n", e.what());
    return 1;
  }
}
