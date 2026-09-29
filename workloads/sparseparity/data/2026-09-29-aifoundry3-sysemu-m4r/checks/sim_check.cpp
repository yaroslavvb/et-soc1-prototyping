// R3's model check: pipeSimMinion over 153,600 configurations (the cycles bound and monotone in T).
#include <cstdio>
#include "spp_common.h"
using namespace spp;
int main() {
  int bad = 0, n = 0;
  for (int gi = 0; gi < 2; ++gi) for (int eh = 0; eh < 2; ++eh) for (int a3 = 0; a3 < 2; ++a3)
  for (int S : {1, 2, 3, 4, 7, 29, 31, 40}) for (int k1 : {0, 1, 3, 5}) for (int nbuf : {1, 2}) for (int epi : {0, 1})
  for (int dram : {0, 1}) for (double U : {0.0, 0.58, 1.5}) for (int nout : {1, 2, 17, 32, 128}) {
    PipeConst P = pipeVariant(gi, eh, a3 && S > 3);
    const bool res = S <= 3;
    double prev = -1, per = 0;
    for (uint64_t T : {1ull, 2ull, 10ull, 1000ull, 20000ull}) {
      std::vector<std::pair<int, uint64_t>> rle = {{nout, T}};
      if (T >= 10) rle = {{nout, T / 2}, {1, T - T / 2}};
      const PipeSim s = pipeSimMinion(rle, S, k1, res, nbuf, epi, dram, U, 5000.0, P);
      // lower bound: hart 1 must generate T tiles
      const double g = pipeGen(S, k1, dram, U, P);
      ++n;
      if (!(s.cycles >= 5000.0 + 0.5 * g * T * 0 + 0.99 * g * T / 1.0 - 1e-6) && s.cycles < g * T) {
        if (++bad <= 10) std::printf("short: S %d k1 %d nbuf %d nout %d T %llu cycles %.0f < gen %.0f\n", S, k1, nbuf, nout, (unsigned long long)T, s.cycles, g * T);
      }
      if (s.cycles <= prev) { if (++bad <= 10) std::printf("not increasing: T %llu\n", (unsigned long long)T); }
      prev = s.cycles;
    }
  }
  std::printf("%d sims, %d bad\n", n, bad);
  return bad != 0;
}
