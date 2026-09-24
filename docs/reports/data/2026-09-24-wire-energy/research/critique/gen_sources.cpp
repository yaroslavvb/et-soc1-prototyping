// Exact copy of enercat host sources() for "random" (workloads/enercat/host/main.cpp), dumped as little-endian u32.
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <random>
#include <vector>
int main(int argc, char** argv) {
  const int EC_MAX_HARTS = 2048;
  uint64_t seed = argc > 1 ? strtoull(argv[1], nullptr, 0) : 1;
  std::vector<uint32_t> v(EC_MAX_HARTS * 64);
  std::mt19937_64 rng(seed);
  std::uniform_real_distribution<float> u(0.5f, 2.0f);
  for (auto& w : v) { const float f = u(rng); std::memcpy(&w, &f, 4); }
  fwrite(v.data(), 4, v.size(), stdout);
  return 0;
}
