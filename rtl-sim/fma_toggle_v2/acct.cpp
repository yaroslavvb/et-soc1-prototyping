// Register accounting behind macros_acct.vh and ff_acct.sv, and a hook that zeroes Verilator's toggle coverage so the
// measurement window excludes reset and warm-up. Unit 0 is the total, 1 txfma, 2 tima, 3 everything else in the VPU.
// A register reports: width bits "present" on every edge of its (possibly gated) clock, width bits "clocked" when its
// enable is also high, and the bits that actually change.
//   selector: 0 clocked, 1 toggles, 2 present (total); 10-12 txfma; 20-22 tima; 30-32 the rest
#include <cstdint>
#include <cstring>
#include "verilated.h"
#include "verilated_cov.h"

static uint64_t g[4][3];

static inline int unit_of(const char* s) {
  if (strstr(s, "txfma")) return 1;
  if (strstr(s, "tima")) return 2;
  return 3;
}
extern "C" void acct_ff_u(const char* where, int width, int toggles, int enabled) {
  int u = unit_of(where);
  g[0][2] += uint64_t(width);
  g[u][2] += uint64_t(width);
  if (enabled) {
    g[0][0] += uint64_t(width);
    g[u][0] += uint64_t(width);
    g[0][1] += uint64_t(toggles);
    g[u][1] += uint64_t(toggles);
  }
}
extern "C" void acct_reset() {
  memset(g, 0, sizeof g);
  Verilated::threadContextp()->coveragep()->zero();
}
extern "C" long long acct_get(int which) {
  if (which < 3) return (long long)g[0][which];
  return (long long)g[which / 10][which % 10];
}
