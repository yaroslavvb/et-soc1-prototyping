// E81 (V3-DP): a byte-exact replica of enercat_host's sources() for the two built-in operands E81 uses,
// `random` and `bern:P`, so the bits each hart's DRAM slice holds can be counted on a desk machine.
// Copied from workloads/enercat/host/main.cpp (sources(), the "bern:" and "random" branches, seed 1 = the host's
// default), with EC_MAX_HARTS = 2048. Build it with a GCC libstdc++ (the lab hosts' library), because
// std::bernoulli_distribution and std::uniform_real_distribution are library-specific:
//   g++ -O2 -std=c++17 -o build/dp-replica tools/claims-v3/dp/src_replica.cpp
//   build/dp-replica random 1 > random.bin ; build/dp-replica bern:0.5 1 > bern50.bin
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <random>
#include <stdexcept>
#include <string>
#include <vector>

static const size_t EC_MAX_HARTS = 2048;

std::vector<uint32_t> sources(const std::string& kind, uint64_t seed) {
  std::vector<uint32_t> v(EC_MAX_HARTS * 64);
  std::mt19937_64 rng(seed);
  std::uniform_real_distribution<float> u(0.5f, 2.0f);
  if (kind.rfind("bern:", 0) == 0) {
    const double pr = std::stod(kind.substr(5));
    std::bernoulli_distribution bit(pr);
    for (auto& w : v) { w = 0; for (int b = 0; b < 32; ++b) if (bit(rng)) w |= 1u << b; }
    return v;
  }
  for (auto& w : v) {
    if (kind == "zeros") w = 0;
    else if (kind == "random") { const float f = u(rng); std::memcpy(&w, &f, 4); }
    else throw std::runtime_error("unknown kind " + kind);
  }
  return v;
}

int main(int argc, char** argv) {
  if (argc < 2) { std::fprintf(stderr, "usage: dp-replica random|bern:P [seed]\n"); return 2; }
  const uint64_t seed = argc > 2 ? std::strtoull(argv[2], nullptr, 0) : 1;
  const auto v = sources(argv[1], seed);
  std::fwrite(v.data(), 4, v.size(), stdout);
  return 0;
}
