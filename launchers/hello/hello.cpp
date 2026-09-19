// Host side of the hello example.  Loads kernels/hello, launches it on every
// hart of the selected shires, copies the per-hart records back and checks
// them.  Runs unchanged on the simulator (--device_type=sysemu, default) and
// on a real ET-SoC-1 card (--device_type=silicon).
#include <cstdlib>
#include <getopt.h>
#include <iostream>
#include <set>
#include <string>
#include <vector>

#include "GenericLauncher.h"
#include "hello/hello_args.h"

namespace {

struct Options {
  fs::path kernel_path;
  std::string device_type = "sysemu";
  uint64_t shire_mask = 0xffffffff;  // the 32 compute shires
  int timeout_s = 300;
};

Options parseArgs(int argc, char** argv, std::vector<char*>& passthrough) {
  static constexpr const char* kHelp =
    "Usage: hello_launcher -k <hello.elf> [options]\n"
    "  -k, --kernel_path   path to hello.elf (required)\n"
    "  -d, --device_type   sysemu (default) | silicon | fake\n"
    "  -s, --shire_mask    compute shires to launch on (default 0xffffffff)\n"
    "  -t, --timeout       kernel timeout in seconds (default 300)\n";
  static const option kLongOpts[] = {{"kernel_path", required_argument, nullptr, 'k'},
                                     {"device_type", required_argument, nullptr, 'd'},
                                     {"shire_mask", required_argument, nullptr, 's'},
                                     {"timeout", required_argument, nullptr, 't'},
                                     {"help", no_argument, nullptr, 'h'},
                                     {nullptr, 0, nullptr, 0}};
  Options opts;
  opterr = 0;
  int c;
  while ((c = getopt_long(argc, argv, "k:d:s:t:h", kLongOpts, nullptr)) != -1) {
    switch (c) {
    case 'k': opts.kernel_path = optarg; break;
    case 'd': opts.device_type = optarg; break;
    case 's': opts.shire_mask = std::strtoull(optarg, nullptr, 0); break;
    case 't': opts.timeout_s = std::atoi(optarg); break;
    case 'h': std::cout << kHelp << GenericLauncher::help_msg; std::exit(0);
    default: passthrough.push_back(argv[optind - 1]); break;  // GenericLauncher options
    }
  }
  if (opts.kernel_path.empty()) {
    std::cerr << kHelp;
    std::exit(2);
  }
  return opts;
}

class HelloLauncher : public GenericLauncher {
public:
  using GenericLauncher::GenericLauncher;

  // Returns the number of bad records.
  int run(rt::KernelId kernel, uint64_t shireMask, std::chrono::seconds timeout) {
    constexpr size_t kHartsPerShire = 32 * 2;  // 32 minions x 2 harts
    const size_t numRecords = __builtin_popcountll(shireMask) * kHartsPerShire;
    std::vector<HelloRecord> records(numRecords);  // zero-initialized
    const size_t bytes = numRecords * sizeof(HelloRecord);

    auto* devRecords = runtime_->mallocDevice(devices_[0], bytes);
    auto stream = defaultStreams_[0];
    runtime_->memcpyHostToDevice(stream, reinterpret_cast<std::byte*>(records.data()), devRecords, bytes);

    HelloArgs args{numRecords, reinterpret_cast<uint64_t>(devRecords)};
    kernelLaunch(kernel, &args, nullptr, 0, 0, shireMask);
    runtime_->memcpyDeviceToHost(stream, devRecords, reinterpret_cast<std::byte*>(records.data()), bytes);
    waitKernelCompletion(timeout);
    dumpTracesToFile(0);
    runtime_->freeDevice(devices_[0], devRecords);
    if (checkKernelExecutionErrors()) {
      std::cerr << "kernel reported execution errors\n";
      return -1;
    }

    int bad = 0;
    std::set<uint32_t> shires;
    for (size_t i = 0; i < numRecords; ++i) {
      const auto& r = records[i];
      const bool ok = r.magic == HELLO_MAGIC && r.rel_tid == static_cast<int32_t>(i) &&
                      r.num_threads == numRecords && r.shire_id == (r.hart_id >> 6) &&
                      r.minion_id == (r.hart_id >> 1) && r.thread_id == (r.hart_id & 1) &&
                      ((shireMask >> r.shire_id) & 1);
      if (!ok && bad++ < 10) {
        std::cerr << "bad record " << i << ": magic=0x" << std::hex << r.magic << std::dec
                  << " hart=" << r.hart_id << " rel_tid=" << r.rel_tid << " num_threads=" << r.num_threads << "\n";
      }
      shires.insert(r.shire_id);
    }
    // std::dec: GenericLauncher::loadKernel() leaves std::cout in hex mode.
    std::cout << std::dec << "hello: " << (numRecords - bad) << "/" << numRecords << " harts reported in from "
              << shires.size() << " shires (first hart " << records.front().hart_id << ", last hart "
              << records.back().hart_id << ")\n";
    return bad;
  }
};

} // namespace

int main(int argc, char** argv) {
  std::vector<char*> passthrough{argv[0]};
  const Options opts = parseArgs(argc, argv, passthrough);

  const Config config{modeFromString(opts.device_type), 1};
  config.dump();
  HelloLauncher launcher(config, static_cast<int>(passthrough.size()), passthrough.data());
  launcher.initialize();
  const auto kernel = launcher.loadKernel(opts.kernel_path);
  const int bad = launcher.run(kernel, opts.shire_mask, std::chrono::seconds(opts.timeout_s));
  launcher.unLoadKernel(kernel);
  launcher.tearDown();

  std::cout << (bad == 0 ? "PASS" : "FAIL") << "\n";
  return bad == 0 ? 0 : 1;
}
