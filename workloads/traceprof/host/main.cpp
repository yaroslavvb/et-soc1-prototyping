// Runs the traced kernel with user tracing on and writes its profile events as JSON lines (see ../README.md).
//   traceprof_host [--sysemu] [--shires MASK] [--reps N] [--out events.jsonl] [--raw trace.bin]
// Each line: {"hart","cycle","insts","region","start","line","func","name"}. scripts/trace-flamegraph.py
// turns them into folded stacks and an SVG flame graph.
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

#define ET_TRACE_DECODER_IMPL
#include <esperanto/et-trace/decoder.h>
#include <esperanto/et-trace/encoder.h>
#include <esperanto/et-trace/layout.h>

#include "Constants.h"
#include "traceprof_args.h"

namespace fs = std::filesystem;
using Clock = std::chrono::steady_clock;

namespace {

constexpr size_t kTraceBytesPerHart = 4096;
constexpr size_t kTraceHarts = 2080;  // the runtime wants 4 KB for every hart of the chip
constexpr size_t kTraceBytes = kTraceBytesPerHart * kTraceHarts;

std::vector<std::byte> readFile(const std::string& path) {
  std::ifstream file(path, std::ios::binary);
  if (!file) {
    return {};
  }
  std::vector<std::byte> data(fs::file_size(path));
  file.read(reinterpret_cast<char*>(data.data()), static_cast<std::streamsize>(data.size()));
  return data;
}

struct Elf {
  std::vector<std::byte> bytes;
  explicit Elf(std::vector<std::byte> b) : bytes(std::move(b)) {}
};

std::string jsonEscape(const std::string& s) {
  std::string o;
  for (char c : s) {
    if (c == '"' || c == '\\') o += '\\';
    if (static_cast<unsigned char>(c) >= 0x20) o += c;
  }
  return o;
}

}  // namespace

int main(int argc, char** argv) {
  bool sysemu = false;
  uint64_t shireMask = 0x1, reps = 4;
  std::string out = "events.jsonl", raw, kernelPath = KERNEL_ELF;
  for (int i = 1; i < argc; ++i) {
    std::string a = argv[i];
    auto next = [&]() -> std::string { if (i + 1 >= argc) { std::fprintf(stderr, "%s needs a value\n", a.c_str()); std::exit(2); } return argv[++i]; };
    if (a == "--sysemu") sysemu = true;
    else if (a == "--shires") shireMask = std::strtoull(next().c_str(), nullptr, 0);
    else if (a == "--reps") reps = std::strtoull(next().c_str(), nullptr, 0);
    else if (a == "--out") out = next();
    else if (a == "--raw") raw = next();
    else if (a == "--kernel") kernelPath = next();
    else { std::fprintf(stderr, "unknown option %s\n", a.c_str()); return 2; }
  }
  const auto elfBytes = readFile(kernelPath);
  if (elfBytes.empty()) {
    std::fprintf(stderr, "cannot read kernel %s\n", kernelPath.c_str());
    return 1;
  }
  const Elf elf(elfBytes);

  try {
    const auto tOpen = Clock::now();
    std::shared_ptr<dev::IDeviceLayer> dl;
    if (sysemu) {
      emu::SysEmuOptions s;
      s.bootromTrampolineToBL2ElfPath = BOOTROM_TRAMPOLINE_TO_BL2_ELF;
      s.spBL2ElfPath = BL2_ELF;
      s.masterMinionElfPath = MASTER_MINION_ELF;
      s.machineMinionElfPath = MACHINE_MINION_ELF;
      s.workerMinionElfPath = WORKER_MINION_ELF;
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
    const uint64_t loadAddr = reinterpret_cast<uint64_t>(load.loadAddress_);

    const size_t minions = size_t(__builtin_popcountll(shireMask)) * 32;
    std::byte* arena = rt->mallocDevice(dev, minions * 65536);
    std::byte* trace = rt->mallocDevice(dev, kTraceBytes);
    std::vector<std::byte> zeros(kTraceBytes);
    rt->memcpyHostToDevice(stream, zeros.data(), trace, zeros.size());
    rt->waitForStream(stream);

    TpArgs args{shireMask, reinterpret_cast<uint64_t>(arena), reps};
    rt::KernelLaunchOptions opts;
    opts.setShireMask(shireMask);
    opts.setBarrier(true);
    opts.setUserTracing(reinterpret_cast<uint64_t>(trace), kTraceBytes, 0, shireMask, 0xFFFFFFFFFFFFFFFFull,
                        TRACE_EVENT_ENABLE_ALL, TRACE_FILTER_ENABLE_ALL);
    rt->kernelLaunch(stream, load.kernel_, reinterpret_cast<const std::byte*>(&args), sizeof(args), opts);
    bool ok = rt->waitForStream(stream, std::chrono::seconds(sysemu ? 3600 : 6));
    for (const auto& e : rt->retrieveStreamErrors(stream)) {
      std::fprintf(stderr, "stream error: %s\n", e.getString().c_str());
      ok = false;
    }
    std::vector<std::byte> buf(kTraceBytes);
    rt->memcpyDeviceToHost(stream, trace, buf.data(), buf.size());
    rt->waitForStream(stream);
    rt->freeDevice(dev, trace);
    rt->freeDevice(dev, arena);
    rt->unloadCode(load.kernel_);
    rt->destroyStream(stream);
    std::fprintf(stderr, "device held for %.2f s, kernel loaded at 0x%llx\n",
                 std::chrono::duration<double>(Clock::now() - tOpen).count(), (unsigned long long)loadAddr);
    if (!raw.empty()) {
      std::ofstream(raw, std::ios::binary).write(reinterpret_cast<const char*>(buf.data()), (std::streamsize)buf.size());
    }

    const auto* tb = reinterpret_cast<const trace_buffer_std_header_t*>(buf.data());
    if (tb->magic_header != TRACE_MAGIC_HEADER) {
      std::fprintf(stderr, "no trace magic (0x%x): tracing was not enabled\n", tb->magic_header);
      return 1;
    }
    // Strings are logged as device pointers. The runtime copies the whole ELF file to loadAddress_, so a
    // pointer minus the load address is an offset into the file.
    auto resolve = [&](uint64_t ptr) -> std::string {
      const uint64_t off = ptr - loadAddr;
      if (ptr < loadAddr || off >= elf.bytes.size()) return {};
      const char* c = reinterpret_cast<const char*>(elf.bytes.data()) + off;
      return std::string(c, strnlen(c, elf.bytes.size() - off));
    };
    std::ofstream os(out);
    std::map<int, size_t> counts;
    size_t n = 0;
    for (const trace_entry_header_t* e = Trace_Decode(tb, nullptr); e; e = Trace_Decode(tb, e)) {
      counts[e->type]++;
      if (e->type != TRACE_TYPE_USER_PROFILE_EVENT) continue;
      const auto* p = reinterpret_cast<const trace_user_profile_event_t*>(e);
      os << "{\"hart\":" << e->hart_id << ",\"cycle\":" << e->cycle << ",\"insts\":" << p->retiredInsts
         << ",\"region\":" << ((p->line_region_status >> 16) & 0xFFFF) << ",\"start\":"
         << ((p->line_region_status & 0xFFFF) ? "true" : "false") << ",\"line\":" << (p->line_region_status >> 32)
         << ",\"func\":\"" << jsonEscape(resolve(p->func)) << "\",\"name\":\"" << jsonEscape(resolve(p->regionName))
         << "\"}\n";
      ++n;
    }
    for (auto [type, c] : counts) std::fprintf(stderr, "trace entry type %d: %zu\n", type, c);
    std::printf("TRACEPROF {\"events\":%zu,\"out\":\"%s\",\"ok\":%s}\n", n, out.c_str(), ok ? "true" : "false");
    return ok && n ? 0 : 1;
  } catch (const std::exception& e) {
    std::fprintf(stderr, "FAIL: %s\n", e.what());
    return 1;
  }
}
