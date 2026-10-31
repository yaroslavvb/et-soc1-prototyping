// Activity counters behind ff_acct.sv, and a hook that zeroes Verilator's toggle coverage so that the
// measurement window excludes reset and warm-up.
#include <cstdint>
#include "verilated.h"
#include "verilated_cov.h"

static uint64_t g_clocked_bits, g_ff_toggles, g_present_bits;

extern "C" void acct_ff(int width, int toggles) {
  g_clocked_bits += uint64_t(width);
  g_ff_toggles += uint64_t(toggles);
}
extern "C" void acct_ff_all(int width) { g_present_bits += uint64_t(width); }
extern "C" void acct_reset() {
  g_clocked_bits = g_ff_toggles = g_present_bits = 0;
  Verilated::threadContextp()->coveragep()->zero();
}
extern "C" long long acct_get(int which) {
  return (long long)(which == 0 ? g_clocked_bits : which == 1 ? g_ff_toggles : g_present_bits);
}
