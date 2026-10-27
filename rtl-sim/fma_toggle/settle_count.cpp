// settle_count: count what really changes in a VCD, once per bit per cycle.
//
// Verilator's --coverage-toggle counter, which rtl-sim/fma_toggle uses, counts every assignment the
// scheduler makes, including the intermediate values a combinational net takes while a cycle settles,
// and it counts a net once for every RTL name it carries (a module port is a new name at each level of
// the hierarchy). This reads a VCD of the same run and counts four things instead:
//
//   names    bit changes between consecutive SETTLED samples, one sample per clock cycle, per RTL name
//            (the same unit as the coverage counter, with the settling transients removed)
//   ids      the same, counted once per VCD identifier: Verilator gives aliased signals one id, so this
//            removes the hierarchy's name multiplicity wherever Verilator could see the alias
//   hier     the same, counted once per net: two names with the same waveform are one net when one
//            scope is an ancestor of the other, which is what a port carried up the hierarchy looks
//            like. THE FIGURE TO QUOTE as a net count — see docs/reports/data/2026-10-26-toggle-recount/
//   distinct the same, counted once per distinct waveform over the window, ancestry ignored: a LOWER
//            BOUND on the net count, and it collapses badly under a stimulus of period 2.
//
// It also reports the RAW count (every value change in the VCD, settling transients included) so the
// two can be differenced block by block, and the clocked-register bits per cycle.
//
//   settle_count <file.vcd> --modmap <tsv> --out <json> [--phase even|odd] [--skip N] [--keep N]
//
// --modmap is <scope path>\t<RTL module name>, one per line (scope_modules.py writes it).
// --phase picks the timestamp parity of the settled sample; the bench drives inputs at the negedge
// (even timestamps) and clocks registers at the posedge (odd), so "even" is the settled point.
// --skip drops the first N sample cycles (pipeline warm-up), --keep stops after N more.
//
// SPDX-License-Identifier: Apache-2.0

#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cstdint>
#include <string>
#include <vector>
#include <map>
#include <unordered_map>
#include <algorithm>

namespace {

struct Sig {               // one VCD identifier
  int width = 0;
  int off = 0;             // first bit in the global bit arrays
  std::vector<std::string> names;   // every <scope>.<name> declared with this id
  std::string scope;       // shallowest scope among them (the driving level)
  int depth = 1 << 30;
  uint64_t raw = 0;        // bit changes seen in the VCD, transients included
  uint64_t settled = 0;    // bit changes between consecutive settled samples
};

std::vector<uint64_t> cur, lastSample, initVal;   // packed bit arrays, 64 bits per word
std::vector<uint64_t> whash;                      // per-bit waveform hash
std::vector<uint32_t> wchanges;                   // per-bit settled change count

inline bool getbit(const std::vector<uint64_t>& v, int i) { return (v[i >> 6] >> (i & 63)) & 1ULL; }
inline void setbit(std::vector<uint64_t>& v, int i, bool b) {
  if (b) v[i >> 6] |= 1ULL << (i & 63); else v[i >> 6] &= ~(1ULL << (i & 63));
}

// Decode a VCD vector literal ("b1010x1") into bits, MSB first in the text, bit 0 last.
// x and z are carried as 0 with a flag; the bench's design has no x after reset.
int decode(const char* p, int n, int width, uint64_t* out, int nw) {
  for (int w = 0; w < nw; w++) out[w] = 0;
  int xz = 0;
  // VCD left-extends with the leading character, so bit (width-1) down to 0.
  int bit = n - 1;  // index into the text from the right
  for (int i = 0; i < width; i++) {
    char c;
    if (i < n) c = p[n - 1 - i];
    else c = (p[0] == '1') ? '0' : p[0];   // 0/x/z extend with themselves, 1 extends with 0
    if (c == '1') out[i >> 6] |= 1ULL << (i & 63);
    else if (c == 'x' || c == 'X' || c == 'z' || c == 'Z') xz = 1;
  }
  (void)bit;
  return xz;
}

}  // namespace

int main(int argc, char** argv) {
  const char* vcdPath = nullptr;
  const char* modmapPath = nullptr;
  const char* outPath = nullptr;
  int phase = 0;                 // 0 = even timestamps
  long skipCycles = 0, keepCycles = -1;
  bool excludeClocks = true;
  std::string incl = ".txfma";

  for (int i = 1; i < argc; i++) {
    std::string a = argv[i];
    if (a == "--modmap") modmapPath = argv[++i];
    else if (a == "--out") outPath = argv[++i];
    else if (a == "--phase") phase = (std::string(argv[++i]) == "odd") ? 1 : 0;
    else if (a == "--skip") skipCycles = atol(argv[++i]);
    else if (a == "--keep") keepCycles = atol(argv[++i]);
    else if (a == "--keep-clocks") excludeClocks = false;
    else if (a == "--include") incl = argv[++i];
    else if (!vcdPath) vcdPath = argv[i];
    else { fprintf(stderr, "unexpected argument %s\n", argv[i]); return 2; }
  }
  if (!vcdPath || !outPath) { fprintf(stderr, "usage: settle_count <file.vcd> --out <json> [--modmap f]\n"); return 2; }

  std::unordered_map<std::string, std::string> modmap;
  if (modmapPath) {
    FILE* f = fopen(modmapPath, "r");
    if (!f) { perror(modmapPath); return 1; }
    char line[4096];
    while (fgets(line, sizeof line, f)) {
      char* tab = strchr(line, '\t');
      if (!tab) continue;
      *tab = 0;
      std::string v = tab + 1;
      while (!v.empty() && (v.back() == '\n' || v.back() == '\r')) v.pop_back();
      modmap[line] = v;
    }
    fclose(f);
  }

  FILE* f = fopen(vcdPath, "r");
  if (!f) { perror(vcdPath); return 1; }

  // ---- header ----
  std::unordered_map<std::string, int> idOf;
  std::vector<Sig> sigs;
  std::vector<std::string> scopeStack;
  long long totalBits = 0;
  {
    char raw[8192];
    while (fgets(raw, sizeof raw, f)) {
      char* line = raw;
      while (*line == ' ' || *line == '\t') line++;
      if (!strncmp(line, "$scope", 6)) {
        char kind[64], name[512];
        if (sscanf(line + 6, "%63s %511s", kind, name) == 2) scopeStack.push_back(name);
      } else if (!strncmp(line, "$upscope", 8)) {
        if (!scopeStack.empty()) scopeStack.pop_back();
      } else if (!strncmp(line, "$var", 4)) {
        char kind[64], id[64], name[512], range[64];
        int width = 0;
        int n = sscanf(line + 4, "%63s %d %63s %511s %63s", kind, &width, id, name, range);
        if (n < 4) continue;
        if (!strcmp(kind, "real")) continue;
        // a bit-selected name like "x [3]" keeps its own entry; fold the range into the name
        std::string nm = name;
        if (n >= 5 && range[0] == '[') nm += range;
        std::string scope;
        for (size_t i = 0; i < scopeStack.size(); i++) { if (i) scope += "."; scope += scopeStack[i]; }
        std::string full = scope + "." + nm;
        auto it = idOf.find(id);
        int si;
        if (it == idOf.end()) {
          si = (int)sigs.size();
          idOf[id] = si;
          sigs.emplace_back();
          sigs[si].width = width;
          sigs[si].off = (int)totalBits;
          totalBits += width;
        } else si = it->second;
        sigs[si].names.push_back(full);
        int depth = 1; for (char c : scope) if (c == '.') depth++;
        if (depth < sigs[si].depth) { sigs[si].depth = depth; sigs[si].scope = scope; }
      } else if (!strncmp(line, "$enddefinitions", 15)) {
        break;
      }
    }
  }
  fprintf(stderr, "settle_count: %zu ids, %lld bits\n", sigs.size(), totalBits);

  // Keep only the multiply-add units: Verilator ignores $dumpvars' scope argument, so the VCD also
  // holds the testbench's own arrays and the package constants.
  std::vector<char> keep(sigs.size(), 0);
  size_t nKept = 0;
  for (size_t i = 0; i < sigs.size(); i++) {
    for (const auto& nm : sigs[i].names) {
      if (!incl.empty() && nm.find(incl) == std::string::npos) continue;
      keep[i] = 1; break;
    }
    if (keep[i]) nKept++;
  }

  // Signals whose name says clock: the bench's coverage parser drops them, so drop them here too.
  std::vector<char> isClock(sigs.size(), 0);
  if (excludeClocks) {
    for (size_t i = 0; i < sigs.size(); i++) {
      for (const auto& nm : sigs[i].names) {
        std::string tail = nm.substr(nm.rfind('.') + 1);
        std::string low; for (char c : tail) low += (char)tolower(c);
        if (low.find("clk") != std::string::npos || low.find("clock") != std::string::npos) { isClock[i] = 1; break; }
      }
    }
  }
  for (size_t i = 0; i < sigs.size(); i++) if (!keep[i]) isClock[i] = 1;
  fprintf(stderr, "settle_count: %zu of %zu ids inside %s\n", nKept, sigs.size(), incl.c_str());

  int nw = (int)((totalBits + 63) / 64);
  cur.assign(nw, 0); lastSample.assign(nw, 0); initVal.assign(nw, 0);
  whash.assign(totalBits, 1469598103934665603ULL);
  wchanges.assign(totalBits, 0);

  // ---- body ----
  long long time = -1, t0 = -1, step = -1;
  long sampleIdx = -1, sampleCount = 0;
  bool pendingSample = false;
  bool rawOn = false;   // the VCD opens with a full dump of the initial state: not changes
  std::vector<uint64_t> tmp(1024);
  char* line = nullptr; size_t cap = 0; ssize_t len;
  long long xzHits = 0;
  bool done = false;

  auto takeSample = [&]() {
    sampleIdx++;
    if (sampleIdx < skipCycles) {                       // warm-up: just remember the state
      for (int w = 0; w < nw; w++) lastSample[w] = cur[w];
      return;
    }
    if (sampleIdx == skipCycles) {
      for (int w = 0; w < nw; w++) { lastSample[w] = cur[w]; initVal[w] = cur[w]; }
      sampleCount = 1;
      rawOn = true;      // from here the raw and the settled count cover the same cycles
      return;
    }
    if (keepCycles >= 0 && sampleCount > keepCycles) { done = true; return; }
    long s = sampleCount;
    for (int w = 0; w < nw; w++) {
      uint64_t x = cur[w] ^ lastSample[w];
      if (!x) continue;
      lastSample[w] = cur[w];
      while (x) {
        int b = __builtin_ctzll(x);
        x &= x - 1;
        int gb = w * 64 + b;
        whash[gb] = (whash[gb] ^ (uint64_t)s) * 1099511628211ULL;
        wchanges[gb]++;
      }
    }
    sampleCount++;
  };

  while (!done && (len = getline(&line, &cap, f)) > 0) {
    char c = line[0];
    if (c == '#') {
      if (pendingSample) takeSample();
      long long t = atoll(line + 1);
      // The VCD's time unit is not the clock: derive the half-period from the first two stamps.
      if (t0 < 0) t0 = t;
      else if (step < 0 && t > t0) step = t - t0;
      time = t;
      pendingSample = (step < 0) ? (t == t0) : ((((t - t0) / step) & 1) == phase);
      continue;
    }
    if (c == '$') {
      if (!strncmp(line, "$dumpoff", 8)) break;         // the window is closed; X's follow
      continue;
    }
    int si = -1; const char* idp; uint64_t* val; int width;
    if (c == 'b' || c == 'B') {
      char* sp = strchr(line, ' ');
      if (!sp) continue;
      *sp = 0;
      char* idend = sp + 1;
      while (*idend && *idend != '\n' && *idend != '\r' && *idend != ' ') idend++;
      *idend = 0;
      idp = sp + 1;
      auto it = idOf.find(idp);
      if (it == idOf.end()) continue;
      si = it->second;
      width = sigs[si].width;
      int nwv = (width + 63) / 64;
      if ((int)tmp.size() < nwv) tmp.resize(nwv);
      xzHits += decode(line + 1, (int)(sp - line - 1), width, tmp.data(), nwv);
      val = tmp.data();
    } else if (c == '0' || c == '1' || c == 'x' || c == 'X' || c == 'z' || c == 'Z') {
      char* idend = line + 1;
      while (*idend && *idend != '\n' && *idend != '\r') idend++;
      *idend = 0;
      idp = line + 1;
      auto it = idOf.find(idp);
      if (it == idOf.end()) continue;
      si = it->second;
      width = 1;
      if ((int)tmp.size() < 1) tmp.resize(1);
      tmp[0] = (c == '1') ? 1 : 0;
      if (c != '0' && c != '1') xzHits++;
      val = tmp.data();
    } else continue;

    // apply, counting raw bit changes
    Sig& S = sigs[si];
    int base = S.off;
    uint64_t changed = 0;
    for (int i = 0; i < width; i++) {
      bool nb = (val[i >> 6] >> (i & 63)) & 1ULL;
      int gb = base + i;
      bool ob = getbit(cur, gb);
      if (nb != ob) { setbit(cur, gb, nb); changed++; }
    }
    if (rawOn) S.raw += changed;
  }
  if (!done && pendingSample) takeSample();
  free(line);
  fclose(f);

  // ---- roll up ----
  // settled toggles per id
  for (auto& S : sigs) {
    uint64_t t = 0;
    for (int i = 0; i < S.width; i++) t += wchanges[S.off + i];
    S.settled = t;
  }

  auto moduleOf = [&](const std::string& scope) -> std::string {
    auto it = modmap.find(scope);
    if (it != modmap.end()) return it->second;
    return "?" ;
  };

  struct Row { double name_raw = 0, name_settled = 0, id_raw = 0, id_settled = 0, distinct_settled = 0,
               hier_settled = 0;
               double n_names = 0, n_ids = 0, n_distinct = 0, n_hier = 0, bits_names = 0, bits_ids = 0; };
  std::map<std::string, Row> byMod;
  double totNameRaw = 0, totNameSettled = 0, totIdRaw = 0, totIdSettled = 0;

  for (auto& S : sigs) {
    if (isClock[&S - &sigs[0]]) continue;
    // every RTL name of this id gets the full count, as the coverage counter does
    for (const auto& nm : S.names) {
      std::string sc = nm.substr(0, nm.rfind('.'));
      Row& r = byMod[moduleOf(sc)];
      r.name_raw += (double)S.raw;
      r.name_settled += (double)S.settled;
      r.n_names += 1;
      r.bits_names += S.width;
      totNameRaw += (double)S.raw; totNameSettled += (double)S.settled;
    }
    Row& r = byMod[moduleOf(S.scope)];
    r.id_raw += (double)S.raw;
    r.id_settled += (double)S.settled;
    r.n_ids += 1;
    r.bits_ids += S.width;
    totIdRaw += (double)S.raw; totIdSettled += (double)S.settled;
  }

  // Two merges, both keyed on the bit's waveform over the window (for a binary signal the cycles it
  // changed in plus its first value ARE its waveform):
  //   hier     merge only where one name's scope is an ancestor of the other's. That is the hierarchy's
  //            own duplication -- a port renamed at each level -- and nothing else, so it is safe on any
  //            stimulus. This is the honest "names per net" correction.
  //   distinct merge every identical waveform. A lower bound on physical nets, and only meaningful when
  //            the stimulus separates nets: an operand stream of period 2 drives most of the unit on the
  //            same period-2 waveform and collapses it to a handful of groups.
  long long nDistinct = 0, distinctToggles = 0, nHier = 0, hierToggles = 0;
  {
    struct Member { int sig; uint32_t changes; };
    std::unordered_map<uint64_t, std::vector<Member>> groups;
    groups.reserve(1 << 18);
    for (size_t i = 0; i < sigs.size(); i++) {
      if (isClock[i]) continue;
      Sig& S = sigs[i];
      for (int b = 0; b < S.width; b++) {
        int gb = S.off + b;
        if (!wchanges[gb]) continue;
        uint64_t key = whash[gb] ^ (getbit(initVal, gb) ? 0x9E3779B97F4A7C15ULL : 0);
        // (no bit-position term: a generate-loop port connects bit i of a bus to bit 0 of a scalar)
        groups[key].push_back({(int)i, wchanges[gb]});
      }
    }
    for (auto& kv : groups) {
      auto& g = kv.second;
      // distinct: one representative, the shallowest
      int rep = 0;
      for (size_t j = 1; j < g.size(); j++)
        if (sigs[g[j].sig].depth < sigs[g[rep].sig].depth) rep = (int)j;
      nDistinct++;
      distinctToggles += g[rep].changes;
      byMod[moduleOf(sigs[g[rep].sig].scope)].distinct_settled += g[rep].changes;
      byMod[moduleOf(sigs[g[rep].sig].scope)].n_distinct += 1;
      // hier: drop a member only when another member of the group names it from an ancestor scope
      for (size_t j = 0; j < g.size(); j++) {
        const std::string& sj = sigs[g[j].sig].scope;
        bool covered = false;
        for (size_t k = 0; k < g.size() && !covered; k++) {
          if (k == j) continue;
          const std::string& sk = sigs[g[k].sig].scope;
          if (sk.size() < sj.size() && sj.compare(0, sk.size(), sk) == 0 && sj[sk.size()] == '.')
            covered = true;
        }
        if (covered) continue;
        nHier++;
        hierToggles += g[j].changes;
        byMod[moduleOf(sj)].hier_settled += g[j].changes;
        byMod[moduleOf(sj)].n_hier += 1;
      }
    }
  }

  FILE* o = fopen(outPath, "w");
  if (!o) { perror(outPath); return 1; }
  fprintf(o, "{\n");
  fprintf(o, " \"vcd\": \"%s\",\n", vcdPath);
  fprintf(o, " \"sample_cycles\": %ld,\n", sampleCount - 1 > 0 ? sampleCount - 1 : 0);
  fprintf(o, " \"n_ids\": %zu,\n", sigs.size());
  fprintf(o, " \"n_bits\": %lld,\n", totalBits);
  fprintf(o, " \"xz_values\": %lld,\n", xzHits);
  fprintf(o, " \"total\": {\"name_raw\": %.0f, \"name_settled\": %.0f, \"id_raw\": %.0f, \"id_settled\": %.0f, "
             "\"distinct_settled\": %lld, \"n_distinct\": %lld, "
             "\"hier_settled\": %lld, \"n_hier\": %lld},\n",
          totNameRaw, totNameSettled, totIdRaw, totIdSettled, distinctToggles, nDistinct,
          hierToggles, nHier);
  fprintf(o, " \"by_module\": {\n");
  bool first = true;
  for (auto& kv : byMod) {
    if (!first) fprintf(o, ",\n");
    first = false;
    const Row& r = kv.second;
    fprintf(o, "  \"%s\": {\"name_raw\": %.0f, \"name_settled\": %.0f, \"id_raw\": %.0f, \"id_settled\": %.0f, "
               "\"distinct_settled\": %.0f, \"hier_settled\": %.0f, \"n_names\": %.0f, \"n_ids\": %.0f, "
               "\"n_distinct\": %.0f, \"n_hier\": %.0f, \"bits_names\": %.0f, \"bits_ids\": %.0f}",
            kv.first.c_str(), r.name_raw, r.name_settled, r.id_raw, r.id_settled, r.distinct_settled,
            r.hier_settled, r.n_names, r.n_ids, r.n_distinct, r.n_hier, r.bits_names, r.bits_ids);
  }
  fprintf(o, "\n }\n}\n");
  fclose(o);
  fprintf(stderr, "settle_count: %ld sampled cycles, name_raw %.0f, settled %.0f, ids %.0f, "
                  "hier %lld/%lld, distinct %lld/%lld\n",
          sampleCount - 1, totNameRaw, totNameSettled, totIdSettled, hierToggles, nHier,
          distinctToggles, nDistinct);
  return 0;
}
