// acct.cpp with one addition: the same counters by register, its path with the lane and unit numbers removed, written to $ACCT_FILES_OUT at exit.
// For a question about which registers stay clocked on zeros; no quoted count comes from this build but that table.
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <map>
#include <regex>
#include <string>
#include <array>
#include "verilated.h"
#include "verilated_cov.h"
static uint64_t g[4][3];
static std::map<std::string, std::array<uint64_t, 3>> byname;
static inline int unit_of(const char* s) {
  if (strstr(s, "txfma")) return 1;
  if (strstr(s, "tima")) return 2;
  return 3;
}
static std::string key_of(const char* s) {
  static std::regex idx("\\[[0-9]+\\]");
  std::string k = std::regex_replace(std::string(s), idx, "");
  auto p = k.rfind("/rtl/");
  if (p != std::string::npos) k = k.substr(p + 5);
  auto d = k.find(".dut.");
  if (d != std::string::npos) k = k.substr(d + 5);
  // a register module's own name is the last element: keep the block it sits in
  auto q = k.rfind('.');
  if (q != std::string::npos && k.find('/') == std::string::npos) k = k.substr(0, q);
  return k;
}
static std::map<const char*, std::string> memo;
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
  auto it = memo.find(where);
  if (it == memo.end()) it = memo.emplace(where, key_of(where)).first;
  auto& a = byname[it->second];
  a[2] += uint64_t(width);
  if (enabled) { a[0] += uint64_t(width); a[1] += uint64_t(toggles); }
}
extern "C" void acct_reset() {
  memset(g, 0, sizeof g);
  byname.clear();
  Verilated::threadContextp()->coveragep()->zero();
}
extern "C" long long acct_get(int which) {
  if (which < 3) return (long long)g[0][which];
  return (long long)g[which / 10][which % 10];
}
namespace { struct AtExit { ~AtExit() {
  const char* f = getenv("ACCT_FILES_OUT");
  if (!f) return;
  FILE* o = fopen(f, "w");
  if (!o) return;
  for (auto& kv : byname) fprintf(o, "%llu %llu %llu %s\n", (unsigned long long)kv.second[0], (unsigned long long)kv.second[1], (unsigned long long)kv.second[2], kv.first.c_str());
  fclose(o);
} } atexit_; }
