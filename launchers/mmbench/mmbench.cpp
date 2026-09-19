// Host side of the matmul throughput / energy benchmark (kernels/mmbench).
//
// Fills a pool of A/B tiles with small non-zero integers. They are exact in fp32,
// fp16 and int8, and never zero, so the tensor unit cannot skip any multiplies.
// It then launches the kernel --repeat times on the selected shires, checks every
// minion's C tile against iters * sum_t A_t * B_t, and prints one line per launch:
//   MMBENCH {json}
// Each line includes wall-clock start/end times (ms since the epoch), so
// scripts/mmbench-power.py can line launches up with a board-power log.
// Runs unchanged on the simulator (--device_type=sysemu) and on a card (silicon).
#include <algorithm>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <getopt.h>
#include <iostream>
#include <random>
#include <string>
#include <vector>

#include "GenericLauncher.h"
#include "mmbench/mmbench_args.h"

namespace {

constexpr size_t kNumMinions = 32 * 32;  // compute shires x minions; C/stats slots by global minion id
constexpr size_t kTileWords = MMBENCH_TILE_BYTES / 4;
constexpr double kExactLimit = 16777216.0;  // 2^24: integers up to here are exact in fp32

struct TypeInfo {
  uint32_t mode;
  int k;          // reduction depth of one TensorFMA op
  int elemBytes;  // bytes per A/B element
  const char* name;
};

bool typeFromString(const std::string& s, TypeInfo& out) {
  static const TypeInfo kTypes[] = {
    {MMBENCH_FP32, 16, 4, "fp32"}, {MMBENCH_FP16, 32, 2, "fp16"}, {MMBENCH_INT8, 64, 1, "int8"}};
  for (const auto& t : kTypes) {
    if (s == t.name) {
      out = t;
      return true;
    }
  }
  return false;
}

struct Options {
  fs::path kernel_path;
  std::string device_type = "sysemu";
  uint64_t shire_mask = 0xffffffff;
  TypeInfo type{MMBENCH_FP32, 16, 4, "fp32"};
  uint32_t ntiles = 16;
  uint64_t iters = 100;
  bool private_pools = false;
  int repeat = 1;
  int timeout_s = 300;
  uint32_t seed = 1;
};

Options parseArgs(int argc, char** argv, std::vector<char*>& passthrough) {
  static constexpr const char* kHelp =
    "Usage: mmbench_launcher -k <mmbench.elf> [options]\n"
    "  -k, --kernel_path    path to mmbench.elf (required)\n"
    "  -d, --device_type    sysemu (default) | silicon\n"
    "  -s, --shire_mask     compute shires to run on (default 0xffffffff)\n"
    "  -m, --mode           fp32 (default) | fp16 | int8\n"
    "  -n, --ntiles         A/B tile pairs each minion cycles through (default 16)\n"
    "  -i, --iters          passes over the tiles; TensorFMA ops per minion = iters * ntiles (default 100)\n"
    "  -p, --private_pools  give every minion its own ntiles tiles (defeats caching)\n"
    "  -r, --repeat         kernel launches (default 1)\n"
    "  -t, --timeout        per-launch timeout in seconds (default 300)\n"
    "      --seed           RNG seed for the tile contents (default 1)\n";
  static const option kLongOpts[] = {{"kernel_path", required_argument, nullptr, 'k'},
                                     {"device_type", required_argument, nullptr, 'd'},
                                     {"shire_mask", required_argument, nullptr, 's'},
                                     {"mode", required_argument, nullptr, 'm'},
                                     {"ntiles", required_argument, nullptr, 'n'},
                                     {"iters", required_argument, nullptr, 'i'},
                                     {"private_pools", no_argument, nullptr, 'p'},
                                     {"repeat", required_argument, nullptr, 'r'},
                                     {"timeout", required_argument, nullptr, 't'},
                                     {"seed", required_argument, nullptr, 'S'},
                                     {"help", no_argument, nullptr, 'h'},
                                     {nullptr, 0, nullptr, 0}};
  Options opts;
  opterr = 0;
  int c;
  while ((c = getopt_long(argc, argv, "k:d:s:m:n:i:pr:t:h", kLongOpts, nullptr)) != -1) {
    switch (c) {
    case 'k': opts.kernel_path = optarg; break;
    case 'd': opts.device_type = optarg; break;
    case 's': opts.shire_mask = std::strtoull(optarg, nullptr, 0); break;
    case 'm':
      if (!typeFromString(optarg, opts.type)) {
        std::cerr << "unknown mode " << optarg << "\n" << kHelp;
        std::exit(2);
      }
      break;
    case 'n': opts.ntiles = static_cast<uint32_t>(std::strtoul(optarg, nullptr, 0)); break;
    case 'i': opts.iters = std::strtoull(optarg, nullptr, 0); break;
    case 'p': opts.private_pools = true; break;
    case 'r': opts.repeat = std::atoi(optarg); break;
    case 't': opts.timeout_s = std::atoi(optarg); break;
    case 'S': opts.seed = static_cast<uint32_t>(std::strtoul(optarg, nullptr, 0)); break;
    case 'h': std::cout << kHelp << GenericLauncher::help_msg; std::exit(0);
    default: passthrough.push_back(argv[optind - 1]); break;  // GenericLauncher options
    }
  }
  if (opts.kernel_path.empty() || opts.ntiles == 0 || opts.iters == 0 || opts.repeat < 1 ||
      (opts.shire_mask & ~0xffffffffull) != 0) {
    std::cerr << kHelp;
    std::exit(2);
  }
  return opts;
}

// Only small integers are ever converted, so the fp16 encoding is a table lookup.
uint16_t halfBits(int v) {
  switch (v) {
  case 1: return 0x3C00;
  case 2: return 0x4000;
  case -1: return 0xBC00;
  case -2: return 0xC000;
  default: std::abort();
  }
}

void packValue(std::byte* dst, int8_t v, int elemBytes) {
  if (elemBytes == 4) {
    const float f = v;
    std::memcpy(dst, &f, 4);
  } else if (elemBytes == 2) {
    const uint16_t h = halfBits(v);
    std::memcpy(dst, &h, 2);
  } else {
    std::memcpy(dst, &v, 1);
  }
}

class MmBenchLauncher : public GenericLauncher {
public:
  using GenericLauncher::GenericLauncher;

  // Returns the number of launches with bad results.
  int run(rt::KernelId kernel, const Options& o) {
    const TypeInfo& ti = o.type;
    const int K = ti.k;
    const int E = 4 / ti.elemBytes;  // k-elements per 32-bit word of a B line
    const size_t poolTiles = o.private_pools ? kNumMinions * o.ntiles : o.ntiles;
    const size_t poolBytes = poolTiles * MMBENCH_TILE_BYTES;
    const size_t numRefs = o.private_pools ? kNumMinions : 1;

    // Tiles and the exact reference: S[r] = sum over the tiles of pool r of A_t * B_t.
    std::mt19937 rng(o.seed);
    static constexpr int8_t kVals[4] = {-2, -1, 1, 2};
    std::vector<std::byte> aPool(poolBytes), bPool(poolBytes);
    std::vector<int64_t> S(numRefs * kTileWords, 0), absS(numRefs * kTileWords, 0);
    std::vector<int8_t> A(16 * K), B(K * 16);
    for (size_t tile = 0; tile < poolTiles; ++tile) {
      for (auto& v : A) {
        v = kVals[rng() & 3];
      }
      for (auto& v : B) {
        v = kVals[rng() & 3];
      }
      std::byte* a = aPool.data() + tile * MMBENCH_TILE_BYTES;
      std::byte* b = bPool.data() + tile * MMBENCH_TILE_BYTES;
      for (int i = 0; i < 16; ++i) {
        for (int k = 0; k < K; ++k) {
          packValue(a + i * 64 + k * ti.elemBytes, A[i * K + k], ti.elemBytes);
        }
      }
      for (int p = 0; p < 16; ++p) {
        for (int j = 0; j < 16; ++j) {
          for (int e = 0; e < E; ++e) {
            packValue(b + p * 64 + (j * E + e) * ti.elemBytes, B[(p * E + e) * 16 + j], ti.elemBytes);
          }
        }
      }
      const size_t ref = (o.private_pools ? tile / o.ntiles : 0) * kTileWords;
      for (int i = 0; i < 16; ++i) {
        for (int j = 0; j < 16; ++j) {
          int64_t dot = 0;
          for (int k = 0; k < K; ++k) {
            dot += A[i * K + k] * B[k * 16 + j];
          }
          S[ref + i * 16 + j] += dot;
          absS[ref + i * 16 + j] += std::llabs(dot);
        }
      }
    }
    // |every partial sum| <= iters * max(absS): below 2^24 the fp32 accumulation is exact.
    const double maxAbsS = double(*std::max_element(absS.begin(), absS.end()));
    const bool isFloat = ti.mode != MMBENCH_INT8;
    const bool exact = !isFloat || double(o.iters) * maxAbsS < kExactLimit;
    const uint64_t maxExactIters = uint64_t((kExactLimit - 1) / maxAbsS);

    auto dev = devices_[0];
    auto stream = defaultStreams_[0];
    std::byte* dA = runtime_->mallocDevice(dev, poolBytes);
    std::byte* dB = runtime_->mallocDevice(dev, poolBytes);
    std::byte* dC = runtime_->mallocDevice(dev, kNumMinions * MMBENCH_TILE_BYTES);
    std::byte* dStats = runtime_->mallocDevice(dev, kNumMinions * sizeof(MmBenchStats));
    runtime_->memcpyHostToDevice(stream, aPool.data(), dA, poolBytes);
    runtime_->memcpyHostToDevice(stream, bPool.data(), dB, poolBytes);
    runtime_->waitForStream(stream);

    MmBenchArgs args{reinterpret_cast<uint64_t>(dA), reinterpret_cast<uint64_t>(dB),
                     reinterpret_cast<uint64_t>(dC), reinterpret_cast<uint64_t>(dStats),
                     o.iters, o.ntiles, o.private_pools ? 1u : 0u, ti.mode, uint32_t(kNumMinions)};
    const uint64_t opsPerMinion = o.iters * o.ntiles;
    const double flopPerOp = 2.0 * 16 * 16 * K;
    const size_t minions = size_t(__builtin_popcountll(o.shire_mask)) * 32;
    const std::vector<uint32_t> cInit(kNumMinions * kTileWords, 0xDEADBEEF);
    const std::vector<MmBenchStats> statsInit(kNumMinions, MmBenchStats{});
    std::vector<uint32_t> c(kNumMinions * kTileWords);
    std::vector<MmBenchStats> stats(kNumMinions);

    int badLaunches = 0;
    for (int r = 0; r < o.repeat; ++r) {
      // Poison the outputs so a launch that did not run cannot pass the check.
      runtime_->memcpyHostToDevice(stream, reinterpret_cast<const std::byte*>(cInit.data()), dC,
                                   cInit.size() * sizeof(uint32_t));
      runtime_->memcpyHostToDevice(stream, reinterpret_cast<const std::byte*>(statsInit.data()), dStats,
                                   statsInit.size() * sizeof(MmBenchStats));
      runtime_->waitForStream(stream);

      const auto t0 = std::chrono::system_clock::now();
      kernelLaunch(kernel, &args, nullptr, 0, 0, o.shire_mask);
      waitKernelCompletion(std::chrono::seconds(o.timeout_s));
      const auto t1 = std::chrono::system_clock::now();
      const bool launchErrors = checkKernelExecutionErrors();

      runtime_->memcpyDeviceToHost(stream, dC, reinterpret_cast<std::byte*>(c.data()), c.size() * sizeof(uint32_t));
      runtime_->memcpyDeviceToHost(stream, dStats, reinterpret_cast<std::byte*>(stats.data()),
                                   stats.size() * sizeof(MmBenchStats));
      runtime_->waitForStream(stream);

      int bad = 0;
      uint64_t cyclesMax = 0;
      double cyclesSum = 0;
      for (size_t m = 0; m < kNumMinions; ++m) {
        if (!((o.shire_mask >> (m / 32)) & 1)) {
          continue;
        }
        const MmBenchStats& s = stats[m];
        bool ok = s.magic == MMBENCH_MAGIC && s.ops == opsPerMinion && (s.hart_id >> 1) == m;
        const int64_t* ref = &S[(o.private_pools ? m : 0) * kTileWords];
        int badElem = -1;
        for (size_t e = 0; ok && e < kTileWords; ++e) {
          const uint32_t got = c[m * kTileWords + e];
          const int64_t want = ref[e] * int64_t(o.iters);
          if (!isFloat) {
            ok = got == uint32_t(uint64_t(want));  // int32 accumulation wraps mod 2^32
          } else {
            float f;
            std::memcpy(&f, &got, 4);
            ok = exact ? double(f) == double(want)
                       : std::fabs(double(f) - double(want)) <= 1e-4 * double(o.iters) * maxAbsS + 1;
          }
          if (!ok) {
            badElem = int(e);
          }
        }
        if (!ok && bad++ < 5) {
          std::fprintf(stderr, "bad minion %zu: magic=0x%x ops=%lu hart=%u", m, s.magic, (unsigned long)s.ops,
                       s.hart_id);
          if (badElem >= 0) {
            float f;
            std::memcpy(&f, &c[m * kTileWords + badElem], 4);
            std::fprintf(stderr, " C[%d]=0x%08x (%g) want %ld", badElem, c[m * kTileWords + badElem], double(f),
                         long(ref[badElem] * int64_t(o.iters)));
          }
          std::fprintf(stderr, "\n");
        }
        cyclesMax = std::max(cyclesMax, s.cycles);
        cyclesSum += double(s.cycles);
      }
      if (launchErrors || bad) {
        ++badLaunches;
      }

      const double wall = std::chrono::duration<double>(t1 - t0).count();
      const double flop = double(minions) * double(opsPerMinion) * flopPerOp;
      const double cyclesMean = cyclesSum / double(minions);
      const auto ms = [](auto t) {
        return (long long)std::chrono::duration_cast<std::chrono::milliseconds>(t.time_since_epoch()).count();
      };
      std::printf("MMBENCH {\"device\":\"%s\",\"mode\":\"%s\",\"shire_mask\":\"0x%llx\",\"minions\":%zu,"
                  "\"ntiles\":%u,\"private_pools\":%d,\"iters\":%llu,\"ops_per_minion\":%llu,"
                  "\"flop_per_op\":%.0f,\"launch\":%d,\"t_start_ms\":%lld,\"t_end_ms\":%lld,\"wall_s\":%.6f,"
                  "\"total_flop\":%.6e,\"tflops\":%.4f,\"cycles_max\":%llu,\"cycles_mean\":%.0f,"
                  "\"flop_per_minion_cycle\":%.3f,\"implied_ghz\":%.4f,\"check\":\"%s\",\"bad_minions\":%d,"
                  "\"launch_errors\":%d,\"max_exact_iters\":%llu}\n",
                  o.device_type.c_str(), ti.name, (unsigned long long)o.shire_mask, minions, o.ntiles,
                  o.private_pools ? 1 : 0, (unsigned long long)o.iters, (unsigned long long)opsPerMinion, flopPerOp,
                  r, ms(t0), ms(t1), wall, flop, flop / wall / 1e12, (unsigned long long)cyclesMax, cyclesMean,
                  cyclesMean > 0 ? double(opsPerMinion) * flopPerOp / cyclesMean : 0.0,
                  wall > 0 ? double(cyclesMax) / wall / 1e9 : 0.0,
                  bad || launchErrors ? "FAIL" : (exact ? "exact" : "approx"), bad, launchErrors ? 1 : 0,
                  (unsigned long long)maxExactIters);
      std::fflush(stdout);
    }

    runtime_->freeDevice(dev, dA);
    runtime_->freeDevice(dev, dB);
    runtime_->freeDevice(dev, dC);
    runtime_->freeDevice(dev, dStats);
    return badLaunches;
  }
};

} // namespace

int main(int argc, char** argv) {
  std::vector<char*> passthrough{argv[0]};
  const Options opts = parseArgs(argc, argv, passthrough);

  const Config config{modeFromString(opts.device_type), 1};
  MmBenchLauncher launcher(config, static_cast<int>(passthrough.size()), passthrough.data());
  launcher.initialize();
  const auto kernel = launcher.loadKernel(opts.kernel_path);
  const int bad = launcher.run(kernel, opts);
  launcher.unLoadKernel(kernel);
  launcher.tearDown();

  std::fprintf(stderr, "%s\n", bad == 0 ? "PASS" : "FAIL");
  return bad == 0 ? 0 : 1;
}
