// Which configurations make pipeSimMinion stop early (the new q < T check), and at what simulated time?
#include <cstdio>
#include "spp_common.h"
using namespace spp;
int main() {
  int bad = 0, n = 0;
  double minFailT = 1e300, maxOkT = 0;
  for (int gi = 0; gi < 2; ++gi) for (int eh = 0; eh < 2; ++eh) for (int a3 = 0; a3 < 2; ++a3)
  for (int S : {1, 2, 3, 4, 7, 29, 31, 40}) for (int k1 : {0, 1, 3, 5}) for (int nbuf : {1, 2}) for (int epi : {0, 1})
  for (int dram : {0, 1}) for (double U : {0.0, 0.58, 1.5}) for (int nout : {1, 2, 17, 32, 128}) {
    PipeConst P = pipeVariant(gi, eh, a3 && S > 3);
    const bool res = S <= 3;
    for (uint64_t T : {1ull, 2ull, 10ull, 1000ull, 20000ull}) {
      std::vector<std::pair<int, uint64_t>> rle = {{nout, T}};
      if (T >= 10) rle = {{nout, T / 2}, {1, T - T / 2}};
      ++n;
      // expected size: hart 0's tensor work alone
      const double big = double(T / 2) * nout * S * 300.0;
      try {
        const PipeSim s = pipeSimMinion(rle, S, k1, res, nbuf, epi, dram, U, 5000.0, P);
        maxOkT = std::max(maxOkT, s.cycles);
      } catch (const std::exception& e) {
        minFailT = std::min(minFailT, big);
        if (++bad <= 12) std::printf("gi %d eh %d a3 %d S %d k1 %d nbuf %d epi %d dram %d U %.2f nout %d T %llu (>= %.3g cycles): %s\n", gi, eh, a3, S, k1, nbuf, epi, dram, U, nout, (unsigned long long)T, big, e.what());
      }
    }
  }
  std::printf("%d sims, %d stopped early; smallest failing run >= %.3g cycles; largest passing %.3g cycles\n", n, bad, minFailT, maxOkT);
  return bad != 0;
}
