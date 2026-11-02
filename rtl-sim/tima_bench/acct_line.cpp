// Q136(c): the register accounting of rtl-sim/fma_toggle_v2/acct.cpp (unit 0 total, 1 txfma, 2 tima, 3 the rest; clocked, toggles,
// present), unchanged in what it computes, plus three tallies the first bench did not keep:
//   1. every macro register by source file and line (acct_ff_l), so that a named group of registers (the TIMA controls) can be summed;
//   2. the register arrays (arrays_acct.sv): per class, writes, bits written, storage bits changed, write-data latch openings and
//      changes, reads, reads at a new address, read-address and read-data toggles, and the negedge shadow's count of storage changes;
//   3. a dump (acct_dump) printing all of it as JSON lines after the bench's ACCT line.
// No coverage hook: this is the lean build (no --coverage), as E109's desk bench built it.
// SPDX-License-Identifier: Apache-2.0
#include <array>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <map>
#include <string>
#include <unordered_map>
#include <vector>

static uint64_t g[4][3];

static inline int unit_of(const char* s) {
  if (strstr(s, "txfma")) return 1;
  if (strstr(s, "tima")) return 2;
  return 3;
}

static inline void tally_unit(const char* where, int width, int toggles, int enabled) {
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

extern "C" void acct_ff_u(const char* where, int width, int toggles, int enabled) { tally_unit(where, width, toggles, enabled); }

// ---- 1. macro registers by file and line ---------------------------------------------------------------------------------------
struct LineTally { uint64_t clocked = 0, toggles = 0, present = 0; int width = 0; };
static std::vector<std::string> files;                       // file id -> path
static std::unordered_map<std::string, int> file_ids;
static std::map<std::pair<int, int>, LineTally> lines;       // (file id, line) -> tally
static const char* last_ptr = nullptr;                        // fast path: the same literal is passed again and again
static int last_id = -1;

static int file_id(const char* f) {
  if (f == last_ptr && last_id >= 0 && strcmp(f, files[last_id].c_str()) == 0) return last_id;   // content checked, not just the pointer
  std::string s(f);
  auto it = file_ids.find(s);
  int id;
  if (it == file_ids.end()) {
    id = int(files.size());
    files.push_back(s);
    file_ids.emplace(s, id);
  } else {
    id = it->second;
  }
  last_ptr = f;
  last_id = id;
  return id;
}

extern "C" void acct_ff_l(const char* where, int line, int width, int toggles, int enabled) {
  tally_unit(where, width, toggles, enabled);
  LineTally& t = lines[{file_id(where), line}];
  t.width = width;
  t.present += uint64_t(width);
  if (enabled) {
    t.clocked += uint64_t(width);
    t.toggles += uint64_t(toggles);
  }
}

// ---- 2. register arrays ----------------------------------------------------------------------------------------------------------
enum { A_WRITES, A_BITS_WRITTEN, A_CHANGED, A_DL_OPEN, A_DL_BITS, A_DL_CHANGED, A_READS, A_READS_NEWADDR, A_BITS_READ, A_RADDR_TOG,
       A_RDATA_TOG, A_SHADOW_CHANGED, A_N };
static const char* A_NAMES[A_N] = {"writes", "bits_written", "changed", "dl_open", "dl_bits", "dl_changed", "reads", "reads_newaddr",
                                   "bits_read", "raddr_tog", "rdata_tog", "shadow_changed"};
static const char* CLS_NAMES[6] = {"tena", "tenb", "tentmp", "tenc", "lane_rf", "other"};
struct Arr { std::string where; int width, entries, kind, cls; std::array<uint64_t, A_N> c{}; };
static std::vector<Arr> arrs;

static int class_of(const std::string& w) {
  if (w.find("tena_rf") != std::string::npos) return 0;
  if (w.find("tenb_rf") != std::string::npos) return 1;
  if (w.find("tentmp_rf") != std::string::npos) return 2;
  if (w.find("tenc_rf") != std::string::npos) return 3;
  if (w.find("vpu_64x32_3r2w_vpurf") != std::string::npos) return 4;
  return 5;
}

extern "C" int arr_register(const char* where, int width, int entries, int kind) {
  Arr a;
  a.where = where;
  a.width = width;
  a.entries = entries;
  a.kind = kind;
  a.cls = class_of(a.where);
  arrs.push_back(a);
  return int(arrs.size()) - 1;
}

extern "C" void arr_cycle(int id, int writes, int bits_written, int changed, int dl_open, int dl_changed, int reads, int reads_newaddr,
                          int raddr_tog, int rdata_tog, int shadow_changed) {
  Arr& a = arrs[id];
  a.c[A_WRITES] += writes;
  a.c[A_BITS_WRITTEN] += bits_written;
  a.c[A_CHANGED] += changed;
  a.c[A_DL_OPEN] += dl_open;
  a.c[A_DL_BITS] += uint64_t(dl_open) * a.width;
  a.c[A_DL_CHANGED] += dl_changed;
  a.c[A_READS] += reads;
  a.c[A_READS_NEWADDR] += reads_newaddr;
  a.c[A_BITS_READ] += uint64_t(reads) * a.width;
  a.c[A_RADDR_TOG] += raddr_tog;
  a.c[A_RDATA_TOG] += rdata_tog;
  a.c[A_SHADOW_CHANGED] += shadow_changed;
}

// ---- reset, get, dump ------------------------------------------------------------------------------------------------------------
extern "C" void acct_reset() {
  memset(g, 0, sizeof g);
  for (auto& kv : lines) kv.second = LineTally{0, 0, 0, kv.second.width};
  for (auto& a : arrs) a.c.fill(0);
}

extern "C" long long acct_get(int which) {
  if (which < 3) return (long long)g[0][which];
  // tb_vpu.sv's ACCTU line also asks for 40-42, a fourth unit that does not exist: acct.cpp reads past its array there; this returns 0
  if (which / 10 > 3 || which % 10 > 2) return 0;
  return (long long)g[which / 10][which % 10];
}

static void json_str(const std::string& s) {
  putchar('"');
  for (char ch : s) {
    if (ch == '"' || ch == '\\') putchar('\\');
    putchar(ch);
  }
  putchar('"');
}

// ACCTARR {"cls": {...counters..., "instances": n, "width": w, "entries": e}, ...}
// ACCTLINE {"<file>:<line>": [width, clocked, toggles, present], ...}   (every macro register line with any clock edge)
extern "C" void acct_dump() {
  std::array<std::array<uint64_t, A_N>, 6> cls{};
  std::array<int, 6> inst{}, width{}, entries{};
  for (auto& a : arrs) {
    for (int k = 0; k < A_N; k++) cls[a.cls][k] += a.c[k];
    inst[a.cls]++;
    width[a.cls] = a.width;
    entries[a.cls] = a.entries;
  }
  printf("ACCTARR {");
  bool first = true;
  for (int c = 0; c < 6; c++) {
    if (!inst[c]) continue;
    printf("%s\"%s\": {\"instances\": %d, \"width\": %d, \"entries\": %d", first ? "" : ", ", CLS_NAMES[c], inst[c], width[c], entries[c]);
    for (int k = 0; k < A_N; k++) printf(", \"%s\": %llu", A_NAMES[k], (unsigned long long)cls[c][k]);
    printf("}");
    first = false;
  }
  printf("}\n");
  printf("ACCTLINE {");
  first = true;
  for (auto& kv : lines) {
    const LineTally& t = kv.second;
    if (!t.present) continue;
    std::string f = files[kv.first.first];
    size_t p = f.find("/rtl/");
    if (p != std::string::npos) f = f.substr(p + 5);
    if (!first) printf(", ");
    json_str(f + ":" + std::to_string(kv.first.second));
    printf(": [%d, %llu, %llu, %llu]", t.width, (unsigned long long)t.clocked, (unsigned long long)t.toggles, (unsigned long long)t.present);
    first = false;
  }
  printf("}\n");
  fflush(stdout);
}
