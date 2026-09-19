// SGEMM on ET-SoC-1: C = A * B (n x n fp32), checked against a host reference.
//   sgemm_host [--sysemu [--sim-args "..."]] [-n N] [--shires MASK] [--reps R] [--kernel sgemm.elf]
// On a shared lab card the device is held only between opening the runtime and
// tearing it down; everything else (input generation, the reference product,
// checking) happens with the device closed, and a time budget stops further
// launches if the device has been held too long.
#include <runtime/IRuntime.h>
#include <runtime/Types.h>
#include <device-layer/IDeviceLayer.h>
#include <sw-sysemu/SysEmuOptions.h>

#include <algorithm>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <limits>
#include <random>
#include <sstream>
#include <string>
#include <vector>

#include "Constants.h"
#include "sgemm_args.h"

namespace fs = std::filesystem;
using Clock = std::chrono::steady_clock;

static double secondsSince(Clock::time_point t0) {
  return std::chrono::duration<double>(Clock::now() - t0).count();
}

static std::vector<std::byte> readFile(const std::string& path) {
  std::ifstream file(path, std::ios::binary);
  if (!file) {
    return {};
  }
  std::vector<std::byte> data(fs::file_size(path));
  file.read(reinterpret_cast<char*>(data.data()), static_cast<std::streamsize>(data.size()));
  return data;
}

static std::unique_ptr<dev::IDeviceLayer> makeDeviceLayer(bool sysemu, const std::string& simArgs) {
  if (!sysemu) {
    return dev::IDeviceLayer::createPcieDeviceLayer(true, true);  // /dev/et0_ops + /dev/et0_mgmt
  }
  emu::SysEmuOptions o;
  o.bootromTrampolineToBL2ElfPath = BOOTROM_TRAMPOLINE_TO_BL2_ELF;
  o.spBL2ElfPath = BL2_ELF;
  o.masterMinionElfPath = MASTER_MINION_ELF;
  o.machineMinionElfPath = MACHINE_MINION_ELF;
  o.workerMinionElfPath = WORKER_MINION_ELF;
  o.executablePath = fs::path(SYSEMU_INSTALL_DIR) / "sys_emu";
  o.runDir = fs::current_path();
  o.maxCycles = std::numeric_limits<uint64_t>::max();
  o.minionShiresMask = 0x1FFFFFFFFu;
  o.puUart0Path = o.runDir + "/pu_uart0_tx.log";
  o.puUart1Path = o.runDir + "/pu_uart1_tx.log";
  o.spUart0Path = o.runDir + "/spio_uart0_tx.log";
  o.spUart1Path = o.runDir + "/spio_uart1_tx.log";
  o.startGdb = false;
  std::istringstream extra(simArgs);  // e.g. "-vpurf_warn"
  for (std::string arg; extra >> arg;) {
    o.additionalOptions.push_back(arg);
  }
  return dev::IDeviceLayer::createSysEmuDeviceLayer(o, 1);
}

int main(int argc, char** argv) {
  bool sysemu = false;
  uint32_t n = 512;
  uint64_t shireMask = 0xffffffff;
  int reps = 3;
  double budgetS = -1;  // stop launching once the device has been held this long (default: 8 s on silicon)
  std::string kernelPath = KERNEL_ELF;
  std::string simArgs;
  for (int i = 1; i < argc; ++i) {
    std::string a = argv[i];
    auto next = [&]() -> const char* {
      if (i + 1 >= argc) {
        std::cerr << a << " needs a value\n";
        std::exit(2);
      }
      return argv[++i];
    };
    if (a == "--sysemu") sysemu = true;
    else if (a == "-n") n = static_cast<uint32_t>(std::atoi(next()));
    else if (a == "--shires") shireMask = std::strtoull(next(), nullptr, 0);
    else if (a == "--reps") reps = std::max(1, std::atoi(next()));
    else if (a == "--budget") budgetS = std::atof(next());
    else if (a == "--kernel") kernelPath = next();
    else if (a == "--sim-args") simArgs = next();
    else {
      std::cerr << "usage: " << argv[0]
                << " [--sysemu] [--sim-args \"-vpurf_warn ...\"] [-n N] [--shires MASK] [--reps R] [--budget SECONDS]"
                   " [--kernel sgemm.elf]\n";
      return 2;
    }
  }
  if (budgetS < 0) {
    budgetS = sysemu ? 1e9 : 8.0;  // the simulator is private; a real card is shared
  }
  const int timeoutS = sysemu ? 600 : 5;  // per launch; sys_emu steps ~2100 harts serially
  if (n == 0 || n % 16 != 0) {
    std::cerr << "n must be a positive multiple of 16\n";
    return 2;
  }

  // Everything that does not need the device happens before opening it.
  const auto elf = readFile(kernelPath);
  if (elf.empty()) {
    std::cerr << "cannot read kernel " << kernelPath << "\n";
    return 1;
  }
  const size_t count = size_t(n) * n;
  const size_t bytes = count * sizeof(float);
  std::vector<float> A(count), B(count), C(count), ref(count);
  std::mt19937 rng(1234);
  std::uniform_real_distribution<float> dist(-1.0f, 1.0f);
  for (auto& x : A) x = dist(rng);
  for (auto& x : B) x = dist(rng);
  for (uint32_t i = 0; i < n; ++i) {  // reference in double, i-k-j order
    std::vector<double> row(n, 0.0);
    for (uint32_t k = 0; k < n; ++k) {
      const double aik = A[size_t(i) * n + k];
      const float* b = &B[size_t(k) * n];
      for (uint32_t j = 0; j < n; ++j) row[j] += aik * b[j];
    }
    for (uint32_t j = 0; j < n; ++j) ref[size_t(i) * n + j] = static_cast<float>(row[j]);
  }
  std::fill(C.begin(), C.end(), std::numeric_limits<float>::quiet_NaN());  // unwritten -> mismatch

  std::cout << "sgemm n=" << n << " shires=0x" << std::hex << shireMask << std::dec << " reps=" << reps
            << " device=" << (sysemu ? "sysemu" : "silicon") << "\n";

  std::vector<double> launchS;
  double heldS = 0;
  {
    const auto tOpen = Clock::now();
    std::shared_ptr<dev::IDeviceLayer> deviceLayer = makeDeviceLayer(sysemu, simArgs);
    auto runtime = rt::IRuntime::create(deviceLayer);
    const auto devices = runtime->getDevices();
    if (devices.empty()) {
      std::cerr << "no ET devices found\n";
      return 1;
    }
    const auto device = devices[0];
    const auto stream = runtime->createStream(device);
    const double openS = secondsSince(tOpen);

    const auto load = runtime->loadCode(stream, elf.data(), elf.size());
    runtime->waitForEvent(load.event_);
    auto* dA = runtime->mallocDevice(device, bytes);
    auto* dB = runtime->mallocDevice(device, bytes);
    auto* dC = runtime->mallocDevice(device, bytes);
    runtime->memcpyHostToDevice(stream, reinterpret_cast<std::byte*>(A.data()), dA, bytes);
    runtime->memcpyHostToDevice(stream, reinterpret_cast<std::byte*>(B.data()), dB, bytes);
    runtime->memcpyHostToDevice(stream, reinterpret_cast<std::byte*>(C.data()), dC, bytes);
    runtime->waitForStream(stream);
    const double setupS = secondsSince(tOpen) - openS;

    SgemmArgs args{reinterpret_cast<uint64_t>(dA), reinterpret_cast<uint64_t>(dB),
                   reinterpret_cast<uint64_t>(dC), shireMask, n, 0};
    rt::KernelLaunchOptions opts;
    opts.setShireMask(shireMask);
    opts.setBarrier(true);
    bool ok = true;
    for (int r = 0; r < reps && ok; ++r) {
      if (secondsSince(tOpen) > budgetS) {
        std::cout << "stopping after " << r << " launches: device-time budget of " << budgetS << " s used\n";
        break;
      }
      const auto t0 = Clock::now();
      runtime->kernelLaunch(stream, load.kernel_, reinterpret_cast<const std::byte*>(&args), sizeof(args), opts);
      ok = runtime->waitForStream(stream, std::chrono::seconds(timeoutS));
      launchS.push_back(secondsSince(t0));
      if (!ok) {
        std::cerr << "kernel did not finish within " << timeoutS << " s, aborting the stream\n";
        runtime->waitForEvent(runtime->abortStream(stream));
      }
      for (const auto& e : runtime->retrieveStreamErrors(stream)) {
        std::cerr << "stream error: " << e.getString() << "\n";
        ok = false;
      }
    }
    runtime->memcpyDeviceToHost(stream, dC, reinterpret_cast<std::byte*>(C.data()), bytes);
    runtime->waitForStream(stream);
    runtime->freeDevice(device, dA);
    runtime->freeDevice(device, dB);
    runtime->freeDevice(device, dC);
    runtime->unloadCode(load.kernel_);
    runtime->destroyStream(stream);
    heldS = secondsSince(tOpen);
    std::cout << "device open " << openS << " s, load+copy-in " << setupS << " s\n";
    if (!ok) {
      std::cout << "FAIL (kernel error)\n";
      return 1;
    }
  }  // runtime and device layer are destroyed here, releasing the device
  std::cout << "device held for " << heldS << " s total\n";

  size_t bad = 0;
  double maxErr = 0;
  for (size_t i = 0; i < count; ++i) {
    const double err = std::fabs(double(C[i]) - double(ref[i]));
    if (!(err <= 1e-3 * (1.0 + std::fabs(double(ref[i]))))) {  // also catches NaN
      if (bad < 5) {
        std::cerr << "mismatch at (" << i / n << "," << i % n << "): got " << C[i] << " want " << ref[i] << "\n";
      }
      ++bad;
    }
    if (std::isfinite(err)) maxErr = std::max(maxErr, err);
  }
  const double flop = 2.0 * n * double(n) * n;
  for (size_t r = 0; r < launchS.size(); ++r) {
    std::cout << "launch " << r << ": " << launchS[r] * 1e3 << " ms, " << flop / launchS[r] * 1e-9 << " GFLOP/s\n";
  }
  std::cout << "max abs error " << maxErr << ", mismatches " << bad << "/" << count << "\n";
  std::cout << (bad == 0 && !launchS.empty() ? "PASS" : "FAIL") << "\n";
  return bad == 0 && !launchS.empty() ? 0 : 1;
}
