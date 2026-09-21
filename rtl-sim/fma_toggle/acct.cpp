// Activity counters behind ff_acct.sv, and a hook that zeroes Verilator's toggle coverage so that the
// measurement window excludes reset and warm-up.
#include <cstdint>
#include "verilated.h"
#include "verilated_cov.h"

static uint64_t g_clocked_bits, g_ff_toggles;

extern "C" void acct_ff(int width, int toggles) {
  g_clocked_bits += uint64_t(width);
  g_ff_toggles += uint64_t(toggles);
}
extern "C" void acct_reset() {
  g_clocked_bits = g_ff_toggles = 0;
  Verilated::threadContextp()->coveragep()->zero();
}
extern "C" long long acct_get(int which) { return (long long)(which == 0 ? g_clocked_bits : g_ff_toggles); }
