// Gathers, scatters and packed atomics (V3-GS, E48): the host side. Included into main.cpp's anonymous namespace
// only when ENERCAT_GS is defined (build/enercat_gs). The catalogue's own options and output are unchanged; a
// --pattern gs.<op> launch prints the same ENERCAT fields plus "gs" (and "verify" for a --verify launch).
//
//   enercat_host --pattern gs.fgw.ps --gs-index rand --ws 4K [--operands zeros|random] [--harts 1|2] [--mask 0xff]
//                [--scp | --hop-distance 2] [--share hart|shire|chip] [--shires M] [--minions M] [--verify N]
//                [--warm 0|1] [--seconds S] [--window CYCLES]
//   enercat_host --sysemu --suite FILE [...]      one simulator session, one configuration per line of FILE
//
// Ops: gs.fg{w,h,b}{,l,g}.ps  gs.fsc{w,h,b}{,l,g}.ps  gs.fg32{w,h,b}.ps  gs.fsc32{w,h,b}.ps  gs.upd
//      gs.famoaddl.pi  gs.famoaddg.pi  gs.flw  gs.fsw  gs.amoaddl.w  gs.amoaddg.w  gs.probe
// Tables: private per hart in DRAM (default; filled by DMA with a hash of (hart, word) as floats in [0.5, 1), or
// zeros), the hart's 16 KB of its own shire's scratchpad (--scp) or of a shire 2 hops away (--hop-distance 2; the
// kernel copies the image in at every launch), or one shared counter table per shire (--share shire, 256 KB) or
// per chip (--share chip, 8 MB) for the atomics.

namespace gs {

struct Participant { uint32_t hart, rank, shire, minion, thread, inShire; };

std::vector<Participant> participants(uint64_t shireMask, uint64_t minionMask, uint64_t harts) {
  std::vector<Participant> v;
  const uint64_t mm = minionMask ? (minionMask & 0xFFFFFFFFull) : 0xFFFFFFFFull;
  for (uint32_t s = 0; s < 32; ++s) {
    if (!((shireMask >> s) & 1)) continue;
    uint32_t idx = 0;
    for (uint32_t m = 0; m < 32; ++m) {
      if (!((mm >> m) & 1)) continue;
      for (uint32_t t = 0; t < harts; ++t) {
        v.push_back({s * 64 + m * 2 + t, (uint32_t)v.size(), s, m, t, (uint32_t)(idx * harts + t)});
      }
      ++idx;
    }
  }
  return v;
}

// Table contents: floats in [0.5, 1) from a hash of (hart, word index); every host and kernel agree on it.
inline uint32_t hashVal(uint32_t id, uint32_t w) {
  uint32_t x = id * 0x9E3779B1u + w * 0x85EBCA77u + 0x165667B1u;
  x ^= x >> 15; x *= 0x2C1B3C6Du; x ^= x >> 12; x *= 0x297A2D39u; x ^= x >> 15;
  return 0x3F000000u | (x >> 9);
}

int patternIndex(const std::string& p) {
  for (int i = 0; i < 7; ++i) if (p == EC_GS_PATTERNS[i]) return i;
  throw std::runtime_error("unknown --gs-index " + p + " (unit s2 s4 s16 line rand bcast)");
}

const EcGsOp& lookupOp(const std::string& pattern, uint64_t ws) {
  std::string n = pattern.substr(3);
  if (n == "flw" || n == "fsw") n += ws < 4096 ? ".t512" : ".t4096";
  if (n == "amoaddl.w" || n == "amoaddg.w") n += ".t4096";
  for (const auto& op : EC_GS_OPS) if (n == op.name) return op;
  throw std::runtime_error("unknown gather/scatter op " + pattern);
}

bool isPow2(uint64_t x) { return x && !(x & (x - 1)); }
uint64_t log2u(uint64_t x) { uint64_t l = 0; while ((1ull << l) < x) ++l; return l; }

// Everything a launch and its model need, fixed before any device call.
struct Plan {
  const EcGsOp* op = nullptr;
  int fam = 0, pat = 5, e32 = 0;
  std::string patName = "rand", target = "dram", share = "hart";
  uint64_t ws = 0, tile = 0, tileLog2 = 0, ntiles = 1, step = 1, mask = 0xff, stride = 0, verify = 0, checkBytes = 0;
  int shareCode = GS_SHARE_HART, scp = 0;
  bool warm = false, atomic = false, zeros = false;
  int32_t off[64] = {};      // vector families: byte offsets from the tile base; scalar families: from the table base
  uint64_t f32[8] = {};
  int perm[8][8] = {};
  double linesPerInstr = 0;
  unsigned lanes = 8;        // active lanes per vector instruction
  unsigned perInstr = 8;     // elements (or updates) per counted instruction
  std::vector<Participant> parts;
  uint64_t shireMaskUsed = 0;
  std::vector<uint32_t> targets;   // scp = 2
  std::string targetMap;
  double meanHops = 0;
};

// The walk start of a participant, as the kernel computes it.
uint64_t kstart(const Plan& p, const Participant& q) {
  const uint64_t M = p.ntiles - 1;
  if (p.shareCode == GS_SHARE_SHIRE) {
    const uint64_t perShire = p.parts.size() / (uint64_t)__builtin_popcountll(p.shireMaskUsed);
    return (uint64_t)q.inShire * p.ntiles / perShire;
  }
  if (p.shareCode == GS_SHARE_CHIP) return (uint64_t)q.rank * p.ntiles / p.parts.size();
  return q.rank & M;
}

Plan makePlan(const Options& o) {
  Plan p;
  const uint64_t wsArg = o.gsWs;
  p.op = &lookupOp(o.pattern, wsArg ? wsArg : 4096);
  p.fam = p.op->family;
  p.patName = o.gsIndex;
  p.pat = patternIndex(o.gsIndex);
  p.mask = o.gsMask & 0xFF;
  p.verify = o.gsVerify;
  p.zeros = o.operands == "zeros";
  p.atomic = p.fam == GS_F_FAMO || p.fam == GS_F_AMO;
  if (o.operands != "zeros" && o.operands != "random") throw std::runtime_error("gs: --operands must be zeros or random");
  if (!p.mask) throw std::runtime_error("gs: --mask 0 runs nothing");
  p.share = o.gsShare;
  p.shareCode = p.share == "hart" ? GS_SHARE_HART : p.share == "shire" ? GS_SHARE_SHIRE : p.share == "chip" ? GS_SHARE_CHIP : -1;
  if (p.shareCode < 0) throw std::runtime_error("gs: --share must be hart, shire or chip");
  const bool remote = o.hopDistance || !o.targets.empty() || !o.pairs.empty();
  p.scp = o.scp ? 1 : remote ? 2 : 0;
  p.target = p.shareCode != GS_SHARE_HART ? p.share : p.scp == 1 ? "scp" : p.scp == 2 ? "rscp" : "dram";
  // refusals that protect the card (the design's section 3.2)
  if (p.atomic && p.scp) throw std::runtime_error("refusing: an atomic on a scratchpad address is a bus error on silicon");
  if (p.shareCode != GS_SHARE_HART && !p.atomic)
    throw std::runtime_error("refusing: shared tables are for the atomics only (the L1 is not coherent)");
  if (p.shareCode != GS_SHARE_HART && p.scp) throw std::runtime_error("refusing: shared tables live in DRAM");
  if (p.shareCode != GS_SHARE_HART && p.patName == "bcast")
    throw std::runtime_error("refusing: every lane on one word of a shared table is a hot line");
  if (p.fam == GS_F_PROBE && (p.scp || p.shareCode != GS_SHARE_HART)) throw std::runtime_error("gs.probe runs on private DRAM slices");
  // the working set
  if (p.shareCode == GS_SHARE_SHIRE) p.ws = GS_SHIRE_TABLE;
  else if (p.shareCode == GS_SHARE_CHIP) p.ws = GS_CHIP_TABLE;
  else if (p.fam == GS_F_PROBE) p.ws = 4096;
  else p.ws = wsArg ? wsArg : 4096;
  if (wsArg && wsArg != p.ws) throw std::runtime_error("gs: --ws does not apply to shared tables or the probe");
  if (!isPow2(p.ws) || p.ws < 256) throw std::runtime_error("gs: --ws must be a power of two >= 256");
  if (p.scp && p.ws > GS_SCP_BYTES) throw std::runtime_error("gs: a scratchpad table holds at most 16 KB per hart");
  // offsets, tile and walk
  const int e = p.op->elem;
  if (p.fam == GS_F_G32 || p.fam == GS_F_S32) {
    p.tile = 256;
    p.e32 = e == 4 ? 0 : e == 2 ? 1 : 2;
    for (int b = 0; b < 8; ++b) {
      p.f32[b] = EC_GS_F32_WORD[p.e32][b];
      for (int i = 0; i < 8; ++i) p.perm[b][i] = EC_GS_F32_PERM[p.e32][b][i];
    }
    p.linesPerInstr = 0.5;
    if (p.patName != "rand") throw std::runtime_error("gs: the restricted forms walk blocks in order with the rand fields (--gs-index rand)");
  } else if (p.fam == GS_F_BLD || p.fam == GS_F_BST || p.fam == GS_F_AMO) {
    if (p.patName != "rand") throw std::runtime_error("gs: the scalar baselines use the rand offsets only");
    p.tile = p.op->btile;
    if (p.ws < p.tile) throw std::runtime_error("gs: the scalar baselines need --ws >= " + std::to_string(p.tile));
    for (int j = 0; j < 64; ++j) p.off[j] = EC_GS_IDX[5][j] % (int32_t)p.tile;
  } else if (p.fam == GS_F_PROBE) {
    p.tile = 4096;
  } else {
    p.tile = std::min<uint64_t>(EC_GS_PAT_TILE[p.pat], p.ws);
    for (int j = 0; j < 64; ++j) p.off[j] = EC_GS_IDX[p.pat][j] % (int32_t)p.tile;
  }
  p.tileLog2 = log2u(p.tile);
  p.ntiles = std::max<uint64_t>(1, p.ws / p.tile);
  if (p.patName == "rand" && p.ntiles > 1 && p.fam != GS_F_G32 && p.fam != GS_F_S32) {   // restricted forms stream
    const double target = 0.618 * (double)p.ntiles;
    uint64_t s = (uint64_t)std::llround((target - 1.0) / 2.0) * 2 + 1;
    p.step = std::max<uint64_t>(1, std::min<uint64_t>(s, p.ntiles - 1)) | 1;
  } else {
    p.step = 1;
  }
  for (int j = 0; j < 64 && p.fam != GS_F_G32 && p.fam != GS_F_S32 && p.fam != GS_F_PROBE; ++j) {
    const int32_t x = p.off[j];
    if (x < 0 || (uint64_t)x + (uint64_t)e > p.tile) throw std::runtime_error("refusing: an offset outside the tile");
    if (x % e) throw std::runtime_error("refusing: an offset not aligned to the element size");
  }
  // lines per instruction = distinct 64 B lines one visit touches / the instructions of a visit, from the offsets
  // actually used: the pattern's nominal figure (EC_GS_PAT_LINES) holds only when the tile is the pattern's own, not
  // when a smaller working set folds the offsets (rand at 256 B / 512 B / 1 KB touches 4 / 8 / 16 lines a visit, not 64)
  if (p.fam != GS_F_G32 && p.fam != GS_F_S32 && p.fam != GS_F_PROBE) {
    std::set<int32_t> lines;
    for (int j = 0; j < 64; ++j) lines.insert(p.off[j] >> 6);
    const bool scalarFam = p.fam == GS_F_BLD || p.fam == GS_F_BST || p.fam == GS_F_AMO;
    p.linesPerInstr = double(lines.size()) / (scalarFam ? 64.0 : 8.0);
  }
  p.lanes = (unsigned)__builtin_popcountll(p.mask);
  p.perInstr = (p.fam == GS_F_BLD || p.fam == GS_F_BST || p.fam == GS_F_AMO) ? 1 : p.lanes;
  p.warm = o.gsWarm >= 0 ? o.gsWarm != 0 : (!p.atomic && p.fam != GS_F_PROBE && p.ws <= 64 * 1024);
  if (p.atomic && p.warm) throw std::runtime_error("gs: no warm-up walk for the atomics (it would change the counters)");
  p.stride = std::max<uint64_t>(4096, (p.ws + 4095) / 4096 * 4096);
  // check area per participant: every gathered vector of every verify visit (256 B each), else the probe's 512 B
  p.checkBytes = GS_CHECK_MIN;
  if (p.verify && (p.fam == GS_F_GATHER || p.fam == GS_F_G32)) p.checkBytes = std::max<uint64_t>(p.checkBytes, 256 * p.verify);
  if (p.verify == 0 && o.seconds <= 0) throw std::runtime_error("gs: nothing to run (--seconds 0 without --verify)");
  // participants, and the remote targets as run() builds them (every reader of a target gets its own region)
  uint64_t shireMask = o.shireMask & 0xFFFFFFFFull;
  if (p.scp == 2) {
    std::vector<uint32_t> t(32, 0);
    uint64_t used = 0;
    if (!o.pairs.empty()) {
      std::stringstream ss(o.pairs); std::string item;
      while (std::getline(ss, item, ',')) {
        const auto c = item.find(':');
        const int r = std::stoi(item.substr(0, c)), tg = std::stoi(item.substr(c + 1));
        t[r] = (uint32_t)tg; used |= 1ull << r;
      }
    } else if (o.hopDistance) {
      auto r = targetsAtDistance((int)o.hopDistance, shireMask, o.hopAxis);
      t = r.first; used = r.second;
    } else {
      throw std::runtime_error("gs: remote scratchpad tables need --hop-distance or --pairs");
    }
    std::vector<int> seen(32, 0);
    int n = 0;
    for (int s = 0; s < 32; ++s) if ((used >> s) & 1) {
      const int k = seen[t[s]]++;
      if (k > 1) throw std::runtime_error("gs: more than two readers of one scratchpad");
      if (t[s] == (uint32_t)s) throw std::runtime_error("gs: a remote target must be another shire");
      p.meanHops += hops(s, (int)t[s]); ++n;
      p.targetMap += (p.targetMap.empty() ? "" : ",") + std::to_string(s) + ">" + std::to_string(t[s]) + (k ? "/r1" : "");
      t[s] |= (uint32_t)k << 16;
    }
    p.meanHops = n ? p.meanHops / n : 0;
    p.targets = t;
    shireMask = used;
  }
  p.shireMaskUsed = shireMask;
  const uint64_t harts = o.harts < 2 ? 1 : 2;
  p.parts = participants(shireMask, o.minionMask, harts);
  if (p.parts.empty()) throw std::runtime_error("gs: no participants");
  return p;
}

// The table's initial word w for participant q (private) or of the shared table.
inline uint32_t initWord(const Plan& p, const Participant& q, uint64_t w) {
  if (p.atomic || p.zeros) return 0;
  return hashVal(q.hart, (uint32_t)w);
}

// The probe's slice image (the kernel's gs_probe comments give the layout).
std::vector<uint32_t> probeImage() {
  std::vector<uint32_t> v(1024, 0);
  for (uint32_t i = 0; i < 64; ++i) v[i] = 0x1000 + i;
  const uint32_t t2[8] = {0xFFFF8001u, 0x7F80FF7Fu, 0x00018002u, 0x80808080u, 0x7F7F7F7Fu, 0x12345678u, 0x9ABCDEF0u, 0xFEDCBA98u};
  for (int i = 0; i < 8; ++i) v[64 + i] = t2[i];
  for (int i = 0; i < 8; ++i) {
    v[128 + i] = (uint32_t)(4 * i);             // unit
    v[136 + i] = (uint32_t)(-64 + 4 * i);       // negative, from T + 64
    v[144 + i] = 12;                            // every lane on word 3
    v[152 + i] = 0xA0u + (uint32_t)i;           // scatter data
  }
  return v;
}

int32_t sext(uint32_t v, int bytes) {
  if (bytes == 4) return (int32_t)v;
  if (bytes == 2) return (int32_t)(int16_t)(uint16_t)v;
  return (int32_t)(int8_t)(uint8_t)v;
}

// A byte-addressed view of a table held as words.
struct Mem {
  std::vector<uint32_t> w;
  uint32_t get(uint64_t byteOff, int bytes) const {
    const uint64_t wi = byteOff / 4, sh = (byteOff % 4) * 8;
    const uint32_t x = w.at(wi) >> sh;
    return bytes == 4 ? x : bytes == 2 ? (x & 0xFFFFu) : (x & 0xFFu);
  }
  void put(uint64_t byteOff, int bytes, uint32_t v) {
    const uint64_t wi = byteOff / 4, sh = (byteOff % 4) * 8;
    const uint32_t m = bytes == 4 ? 0xFFFFFFFFu : bytes == 2 ? 0xFFFFu : 0xFFu;
    w.at(wi) = (w.at(wi) & ~(m << sh)) | ((v & m) << sh);
  }
};

struct Check {
  uint64_t checked = 0, mismatches = 0;
  std::string first;
  std::map<int, uint64_t> winners;   // lane whose value remained at a lane-conflict address -> count
  uint64_t conflicts = 0, conflictsAmbiguous = 0;
  std::string probe;                 // the probe's per-case report (JSON object text)
  bool probeOk = true;
  void bad(const std::string& what) { ++mismatches; if (first.empty()) first = what; }
};

// The visits a verify launch makes, in order: the warm-up walk (every tile once) then gs_verify visits.
std::vector<uint64_t> visits(const Plan& p, const Participant& q, bool withWarm) {
  std::vector<uint64_t> v;
  const uint64_t k0 = kstart(p, q), M = p.ntiles - 1;
  if (withWarm && p.warm) for (uint64_t j = 0; j < p.ntiles; ++j) v.push_back((k0 + j * p.step) & M);
  for (uint64_t j = 0; j < p.verify; ++j) v.push_back((k0 + j * p.step) & M);
  return v;
}

// Apply the stores of one visit of the scatter-like families to the model; conflict bookkeeping per address.
struct Last { bool conflict = false; std::vector<std::pair<int, uint32_t>> cand; };

void applyVisit(const Plan& p, Mem& m, uint64_t base, const std::vector<uint32_t>& data, std::map<uint64_t, Last>* last) {
  const int e = p.op->elem;
  auto store = [&](uint64_t a, uint32_t v) { m.put(a, e, v); };
  if (p.fam == GS_F_SCATTER || p.fam == GS_F_S32) {
    for (int b = 0; b < 8; ++b) {
      std::map<uint64_t, std::vector<std::pair<int, uint32_t>>> byAddr;
      for (int i = 0; i < 8; ++i) {
        if (!((p.mask >> i) & 1)) continue;
        const uint64_t a = p.fam == GS_F_SCATTER ? base + (uint64_t)p.off[b * 8 + i]
                                                  : base + 32 * (uint64_t)b + (uint64_t)p.perm[b][i] * (uint64_t)e;
        const uint32_t d = data[b * 8 + i];
        store(a, d);                                  // lane order: the highest active lane's value remains (model)
        byAddr[a].push_back({i, d});
      }
      if (last) for (auto& kv : byAddr) {
        Last l; l.conflict = kv.second.size() > 1; l.cand = kv.second; (*last)[kv.first] = l;
      }
    }
  } else if (p.fam == GS_F_BST) {
    for (int j = 0; j < 64; ++j) {
      const uint64_t a = base + (uint64_t)p.off[j];
      store(a, data[(j % 8) * 8]);                    // fsw f(16 + j%8): lane 0 of that data vector
      if (last) { Last l; l.cand = {{0, data[(j % 8) * 8]}}; (*last)[a] = l; }
    }
  } else if (p.fam == GS_F_UPD) {
    for (int v = 0; v < 8; ++v) {
      uint32_t got[8];
      for (int i = 0; i < 8; ++i) got[i] = m.get(base + (uint64_t)p.off[v * 8 + i], 4);
      for (int i = 0; i < 8; ++i) {
        if (!((p.mask >> i) & 1)) continue;
        float f; std::memcpy(&f, &got[i], 4);
        volatile float g = f + 1.0f;                  // round to nearest even, as fadd.ps ..., rne
        float gg = g; uint32_t u; std::memcpy(&u, &gg, 4);
        store(base + (uint64_t)p.off[v * 8 + i], u);
        if (last) { Last l; l.cand = {{i, u}}; (*last)[base + (uint64_t)p.off[v * 8 + i]] = l; }
      }
    }
  }
}

std::vector<size_t> sampled(size_t n) {
  std::vector<size_t> v;
  if (n <= 16) { for (size_t i = 0; i < n; ++i) v.push_back(i); return v; }
  for (size_t i = 0; i < 16; ++i) {
    size_t r = i * n / 16;
    r = (r & ~(size_t)1) | (i & 1);   // alternate threads when both harts run
    if (r >= n) r = n - 1;
    if (v.empty() || v.back() != r) v.push_back(r);
  }
  return v;
}

std::string hex32(uint32_t v) { char b[16]; std::snprintf(b, sizeof b, "%08x", v); return b; }

}  // namespace gs

struct GsBuffers { std::byte *params = nullptr, *table = nullptr, *stage = nullptr, *check = nullptr, *copy = nullptr, *targets = nullptr; };

// Fill a device buffer with a word function, in chunks (never the whole 512 MB image in host memory at once).
template <class F>
void gsFill(Session& dev, std::byte* dst, uint64_t words, F f) {
  const uint64_t chunk = 4ull << 20;   // words
  std::vector<uint32_t> buf(std::min<uint64_t>(chunk, words));
  for (uint64_t w0 = 0; w0 < words; w0 += chunk) {
    const uint64_t n = std::min<uint64_t>(chunk, words - w0);
    for (uint64_t i = 0; i < n; ++i) buf[i] = f(w0 + i);
    dev.put(buf.data(), dst + w0 * 4, n * 4);
  }
}

// The verify launch's checks: every participant's gather sums (or B sums, famo old values), sampled participants'
// tables after scatters, the whole shared table after atomics, the probe's cases.
gs::Check gsVerify(Session& dev, const gs::Plan& p, const GsBuffers& B, const std::vector<uint32_t>& src) {
  using namespace gs;
  Check c;
  const size_t np = p.parts.size();
  const int e = p.op->elem;
  const uint64_t cw = p.checkBytes / 4;   // check words per participant
  std::vector<uint32_t> chk(np * cw);
  dev.get(B.check, chk.data(), chk.size() * 4);
  auto dataOf = [&](const Participant& q) {
    std::vector<uint32_t> d(64);
    for (int j = 0; j < 64; ++j) d[j] = src[(size_t)q.hart * 64 + j];
    return d;
  };
  auto tableWords = [&](const Participant& q) {
    Mem m; m.w.resize(p.ws / 4);
    for (uint64_t w = 0; w < m.w.size(); ++w) m.w[w] = initWord(p, q, w);
    return m;
  };
  if (p.fam == GS_F_GATHER || p.fam == GS_F_G32) {
    // every gathered vector of every verify visit, exactly; a masked-off lane must still hold the sentinel
    for (const auto& q : p.parts) {
      const auto vs = visits(p, q, false);
      for (size_t j = 0; j < vs.size(); ++j) {
        const uint64_t base = vs[j] * p.tile;
        for (int b = 0; b < 8; ++b) for (int i = 0; i < 8; ++i) {
          uint32_t want = GS_SENTINEL;
          if ((p.mask >> i) & 1) {
            const uint64_t a = p.fam == GS_F_GATHER ? base + (uint64_t)p.off[b * 8 + i]
                                                     : base + 32 * (uint64_t)b + (uint64_t)p.perm[b][i] * (uint64_t)e;
            const uint32_t word = initWord(p, q, a / 4) >> ((a % 4) * 8);
            want = (uint32_t)sext(word, e);
          }
          const uint32_t got = chk[(size_t)q.rank * cw + j * 64 + (size_t)(b * 8 + i)];
          ++c.checked;
          if (got != want) c.bad("hart " + std::to_string(q.hart) + " visit " + std::to_string(j) + " vector " + std::to_string(b) +
                                 " lane " + std::to_string(i) + ": " + hex32(got) + " expected " + hex32(want));
        }
      }
    }
  } else if (p.fam == GS_F_BLD) {
    for (const auto& q : p.parts) {
      uint64_t sum = 0;
      for (uint64_t k : visits(p, q, false)) {
        const uint64_t base = k * p.tile;
        for (int j = 0; j < 64; ++j) sum += (uint64_t)(int64_t)(int32_t)initWord(p, q, (base + (uint64_t)p.off[j]) / 4);
      }
      uint64_t got; std::memcpy(&got, &chk[(size_t)q.rank * cw], 8);
      ++c.checked;
      if (got != sum) c.bad("hart " + std::to_string(q.hart) + ": flw sum " + std::to_string(got) + " expected " + std::to_string(sum));
    }
  } else if (p.fam == GS_F_SCATTER || p.fam == GS_F_S32 || p.fam == GS_F_BST || p.fam == GS_F_UPD) {
    for (size_t si : sampled(np)) {
      const auto& q = p.parts[si];
      Mem m = tableWords(q);
      std::map<uint64_t, Last> last;
      const auto d = dataOf(q);
      for (uint64_t k : visits(p, q, true)) applyVisit(p, m, k * p.tile, d, &last);
      std::vector<uint32_t> got(p.ws / 4);
      const std::byte* from = p.scp ? B.copy + (uint64_t)q.rank * GS_SCP_BYTES : B.table + (uint64_t)q.rank * p.stride;
      dev.get(from, got.data(), got.size() * 4);
      const uint32_t em = e == 4 ? 0xFFFFFFFFu : e == 2 ? 0xFFFFu : 0xFFu;
      Mem G; G.w = got;
      // lane conflicts (several active lanes of the last instruction that wrote an element on it): which lane's
      // value remained? The model keeps the highest lane's; any lane's value passes, and the lane is recorded.
      std::map<uint64_t, bool> conflictOk;
      for (auto& kv : last) {
        if (!kv.second.conflict) continue;
        ++c.conflicts;
        const uint32_t have = G.get(kv.first, e);
        const auto& cand = kv.second.cand;
        bool allSame = true;
        for (auto& cv : cand) if ((cv.second & em) != (cand[0].second & em)) allSame = false;
        int lane = -1;
        for (auto& cv : cand) if ((cv.second & em) == have) lane = cv.first;
        if (allSame) ++c.conflictsAmbiguous;
        else if (lane >= 0) ++c.winners[lane];
        conflictOk[kv.first] = lane >= 0;
      }
      for (uint64_t a = 0; a < p.ws; a += (uint64_t)e) {
        ++c.checked;
        const uint32_t have = G.get(a, e), want = m.get(a, e);
        auto it = conflictOk.find(a);
        if (it != conflictOk.end() ? !it->second : have != want)
          c.bad("hart " + std::to_string(q.hart) + " byte " + std::to_string(a) + ": " + hex32(have) + " expected " + hex32(want));
      }
    }
  } else if (p.fam == GS_F_FAMO || p.fam == GS_F_AMO) {
    // counters: every participant's updates, in any order (atomics); famo old values of a private word in lane order
    const bool shared = p.shareCode != GS_SHARE_HART;
    std::map<uint64_t, uint32_t> cnt;   // byte offset in the shared table, or (rank << 32 | offset) for private
    for (const auto& q : p.parts) {
      const uint64_t tbase = p.shareCode == GS_SHARE_SHIRE ? (uint64_t)q.shire * GS_SHIRE_TABLE : 0;
      for (uint64_t k : visits(p, q, false)) {
        const uint64_t base = tbase + k * p.tile;
        if (p.fam == GS_F_FAMO) {
          for (int b = 0; b < 8; ++b) for (int i = 0; i < 8; ++i) if ((p.mask >> i) & 1) {
            const uint64_t a = base + (uint64_t)p.off[b * 8 + i];
            ++cnt[shared ? a : ((uint64_t)q.rank << 32 | a)];
          }
        } else {
          for (int j = 0; j < 64; ++j) {
            const uint64_t a = base + (uint64_t)p.off[j];
            ++cnt[shared ? a : ((uint64_t)q.rank << 32 | a)];
          }
        }
      }
    }
    if (shared) {
      const uint64_t bytes = p.shareCode == GS_SHARE_SHIRE ? 32ull * GS_SHIRE_TABLE : GS_CHIP_TABLE;
      std::vector<uint32_t> got(bytes / 4);
      dev.get(B.table, got.data(), bytes);
      for (uint64_t w = 0; w < got.size(); ++w) {
        auto it = cnt.find(w * 4);
        const uint32_t want = it == cnt.end() ? 0 : it->second;
        ++c.checked;
        if (got[w] != want) c.bad("counter at +" + std::to_string(w * 4) + ": " + std::to_string(got[w]) + " expected " + std::to_string(want));
      }
    } else {
      for (size_t si : sampled(np)) {
        const auto& q = p.parts[si];
        std::vector<uint32_t> got(p.ws / 4);
        dev.get(B.table + (uint64_t)q.rank * p.stride, got.data(), got.size() * 4);
        for (uint64_t w = 0; w < got.size(); ++w) {
          auto it = cnt.find((uint64_t)q.rank << 32 | (w * 4));
          const uint32_t want = it == cnt.end() ? 0 : it->second;
          ++c.checked;
          if (got[w] != want) c.bad("hart " + std::to_string(q.hart) + " counter word " + std::to_string(w) + ": " +
                                    std::to_string(got[w]) + " expected " + std::to_string(want));
        }
      }
    }
    if (p.fam == GS_F_FAMO && !shared) {
      // the old values the first visit's eight famo returned: sequential, lane order, counters from zero
      for (const auto& q : p.parts) {
        std::map<uint64_t, uint32_t> c0;
        const uint64_t base = kstart(p, q) * p.tile;
        for (int b = 0; b < 8; ++b) for (int i = 0; i < 8; ++i) {
          uint32_t want = 1;   // a masked-off lane keeps its addend
          if ((p.mask >> i) & 1) want = c0[base + (uint64_t)p.off[b * 8 + i]]++;
          const uint32_t got = chk[(size_t)q.rank * cw + (size_t)(b * 8 + i)];
          ++c.checked;
          if (got != want) c.bad("hart " + std::to_string(q.hart) + " famo old value vector " + std::to_string(b) + " lane " +
                                 std::to_string(i) + ": " + std::to_string(got) + " expected " + std::to_string(want));
        }
      }
    }
  } else if (p.fam == GS_F_PROBE) {
    const auto img = probeImage();
    std::vector<uint32_t> tab(np * p.stride / 4);
    dev.get(B.table, tab.data(), tab.size() * 4);
    std::map<std::string, uint64_t> caseBad;
    std::map<std::string, std::map<int, uint64_t>> winner;
    std::map<std::string, uint64_t> maskIgnored;
    auto T = [&](int i) { return img[i]; };
    const int fw[8] = {7, 6, 5, 4, 3, 2, 1, 0};
    const int fh[8] = {15, 12, 9, 6, 3, 0, 1, 10};
    const int fb[8] = {31, 26, 21, 16, 11, 6, 1, 3};
    Mem blk; blk.w.assign(img.begin() + 64, img.begin() + 72);
    for (const auto& q : p.parts) {
      const uint32_t* C = &chk[(size_t)q.rank * cw];
      const uint32_t* S = &tab[(size_t)q.rank * p.stride / 4];
      auto expect = [&](const std::string& name, int vec, const uint32_t want[8]) {
        for (int i = 0; i < 8; ++i) { ++c.checked; if (C[vec * 8 + i] != want[i]) { ++caseBad[name]; c.bad("hart " + std::to_string(q.hart) + " probe " + name + " lane " + std::to_string(i) + ": " + hex32(C[vec * 8 + i]) + " expected " + hex32(want[i])); break; } }
      };
      uint32_t w[8];
      for (int i = 0; i < 8; ++i) w[i] = T(i);
      expect("fgw_unit", 0, w);
      expect("fgw_negative_offsets", 1, w);
      for (int i = 0; i < 8; ++i) w[i] = T(fw[i]);
      expect("fg32w_fields", 2, w);
      for (int i = 0; i < 8; ++i) w[i] = T((1 + fw[i]) & 7);
      expect("fg32w_rs2_rotation", 3, w);
      for (int i = 0; i < 8; ++i) w[i] = (uint32_t)sext(blk.get((uint64_t)(2 * fh[i]), 2), 2);
      expect("fg32h_fields", 4, w);
      for (int i = 0; i < 8; ++i) w[i] = (uint32_t)sext(blk.get((uint64_t)fb[i], 1), 1);
      expect("fg32b_fields", 5, w);
      for (int i = 0; i < 8; ++i) w[i] = (uint32_t)sext(img[64 + i] & 0xFFFF, 2);
      expect("fgh_sign_extension", 6, w);
      for (int i = 0; i < 8; ++i) w[i] = (uint32_t)sext(img[64 + i] & 0xFF, 1);
      expect("fgb_sign_extension", 7, w);
      for (int i = 0; i < 8; ++i) w[i] = i < 4 ? T(i) : 0xEEu;
      expect("fgw_masked_keeps_lanes", 8, w);
      for (int i = 0; i < 8; ++i) w[i] = (uint32_t)i;
      expect("famoaddl_old_values_lane_order", 9, w);
      for (int i = 0; i < 8; ++i) w[i] = 0;
      expect("famoaddg_old_values", 10, w);
      ++c.checked;
      if (C[88] != 0 || C[89] != 0) { ++caseBad["gsc_progress_zero"]; c.bad("hart " + std::to_string(q.hart) + " gsc_progress " + std::to_string(C[88]) + "/" + std::to_string(C[89])); }
      for (int i = 0; i < 8; ++i) w[i] = T(i);
      expect("fgwl_unit", 12, w);
      expect("fgwg_unit", 13, w);
      // memory after: counters, conflicts, masks, restricted scatters
      ++c.checked;
      if (S[0x600 / 4 + 3] != 8) { ++caseBad["famoaddl_counter"]; c.bad("hart " + std::to_string(q.hart) + " famoaddl counter " + std::to_string(S[0x600 / 4 + 3])); }
      for (int i = 0; i < 8; ++i) { ++c.checked; if (S[0x640 / 4 + i] != 1) { ++caseBad["famoaddg_counters"]; c.bad("hart " + std::to_string(q.hart) + " famoaddg counter " + std::to_string(i)); break; } }
      const char* cn[3] = {"fscw", "fscwl", "fscwg"};
      for (int k = 0; k < 3; ++k) {
        const uint32_t* A = S + (0x400 + 0x40 * k) / 4;
        int lane = -1;
        for (int i = 0; i < 8; ++i) if (A[3] == 0xA0u + (uint32_t)i) lane = i;
        ++winner[cn[k]][lane];
        bool rest = true;
        for (int i = 0; i < 16; ++i) if (i != 3 && A[i] != 0) rest = false;
        ++c.checked;
        if (lane < 0 || !rest) { ++caseBad[std::string(cn[k]) + "_conflict"]; c.bad("hart " + std::to_string(q.hart) + " " + cn[k] + " conflict word " + hex32(A[3])); }
      }
      const char* mn[3] = {"fscwl", "fscwg", "fscw"};
      for (int k = 0; k < 3; ++k) {
        const uint32_t* A = S + (0x4C0 + 0x40 * k) / 4;
        bool ok = A[0] == 0xA0u && A[7] == 0xA7u, ign = true;
        for (int i = 1; i < 7; ++i) { if (A[i] != 0) ok = false; if (A[i] != 0xA0u + (uint32_t)i) ign = false; }
        for (int i = 8; i < 16; ++i) if (A[i] != 0) ok = false;
        if (ign) ++maskIgnored[mn[k]];
        ++c.checked;
        if (!ok) { ++caseBad[std::string(mn[k]) + "_masked"]; c.bad("hart " + std::to_string(q.hart) + " masked " + mn[k] + " word1 " + hex32(A[1])); }
      }
      {
        const uint32_t* A = S + 0x580 / 4;
        bool ok = true;
        for (int i = 0; i < 8; ++i) if (A[fw[i]] != 0xA0u + (uint32_t)i) ok = false;
        for (int i = 8; i < 16; ++i) if (A[i] != 0) ok = false;
        ++c.checked;
        if (!ok) { ++caseBad["fsc32w_fields"]; c.bad("hart " + std::to_string(q.hart) + " fsc32w"); }
        Mem g; g.w.assign(S + 0x5C0 / 4, S + 0x5C0 / 4 + 16);
        bool okb = true;
        std::vector<int> want(64, 0);
        for (int i = 0; i < 8; ++i) want[fb[i]] = 0xA0 + i;
        for (int bo = 0; bo < 64; ++bo) if (g.get((uint64_t)bo, 1) != (uint32_t)want[bo]) okb = false;
        ++c.checked;
        if (!okb) { ++caseBad["fsc32b_fields"]; c.bad("hart " + std::to_string(q.hart) + " fsc32b"); }
      }
    }
    std::string s = "{\"cases_failed\":{";
    bool first = true;
    for (auto& kv : caseBad) { s += (first ? "" : ",") + ("\"" + kv.first + "\":" + std::to_string(kv.second)); first = false; }
    s += "},\"winner_lane\":{";
    first = true;
    for (auto& kv : winner) {
      s += (first ? "" : ",") + ("\"" + kv.first + "\":{");
      bool f2 = true;
      for (auto& w2 : kv.second) { s += (f2 ? "" : ",") + ("\"" + std::to_string(w2.first) + "\":" + std::to_string(w2.second)); f2 = false; }
      s += "}"; first = false;
    }
    s += "},\"mask_ignored\":{";
    first = true;
    for (auto& kv : maskIgnored) { s += (first ? "" : ",") + ("\"" + kv.first + "\":" + std::to_string(kv.second)); first = false; }
    s += "}}";
    c.probe = s;
    c.probeOk = caseBad.empty();
  }
  return c;
}

int runGs(const Options& o, Session& dev) {
  const gs::Plan p = gs::makePlan(o);
  const size_t np = p.parts.size();
  GsBuffers B;
  // sources: 256 B per hart (the scattered data), as the catalogue's
  const auto src = sources(o.operands, o.seed);
  std::byte* sbuf = dev.alloc(src.size() * 4);
  dev.put(src.data(), sbuf, src.size() * 4);
  // params: the index vectors (vector families) and the restricted-form fields
  std::vector<uint8_t> params(GS_PARAM_BYTES, 0);
  std::memcpy(params.data() + GS_PARAM_IDX, p.off, sizeof p.off);
  std::memcpy(params.data() + GS_PARAM_F32, p.f32, sizeof p.f32);
  B.params = dev.alloc(GS_PARAM_BYTES);
  dev.put(params.data(), B.params, GS_PARAM_BYTES);
  // tables
  if (!p.scp) {
    uint64_t bytes;
    if (p.shareCode == GS_SHARE_SHIRE) bytes = 32ull * GS_SHIRE_TABLE;
    else if (p.shareCode == GS_SHARE_CHIP) bytes = GS_CHIP_TABLE;
    else bytes = (uint64_t)np * p.stride;
    B.table = dev.alloc(bytes);
    if (p.fam == GS_F_PROBE) {
      const auto img = gs::probeImage();
      gsFill(dev, B.table, bytes / 4, [&](uint64_t w) { return img[w % 1024]; });
    } else if (p.shareCode != GS_SHARE_HART || p.atomic || p.zeros) {
      gsFill(dev, B.table, bytes / 4, [](uint64_t) { return 0u; });
    } else {
      const uint64_t wpp = p.stride / 4;
      gsFill(dev, B.table, bytes / 4, [&](uint64_t w) { return gs::hashVal(p.parts[w / wpp].hart, (uint32_t)(w % wpp)); });
    }
  } else {
    B.stage = dev.alloc((uint64_t)np * GS_SCP_BYTES);
    const uint64_t wpp = GS_SCP_BYTES / 4;
    gsFill(dev, B.stage, (uint64_t)np * wpp, [&](uint64_t w) { return p.zeros ? 0u : gs::hashVal(p.parts[w / wpp].hart, (uint32_t)(w % wpp)); });
    B.copy = dev.alloc((uint64_t)np * GS_SCP_BYTES);
  }
  B.check = dev.alloc((uint64_t)np * p.checkBytes);
  if (p.verify) gsFill(dev, B.check, (uint64_t)np * p.checkBytes / 4, [](uint64_t) { return 0xDEADBEEFu; });
  if (p.scp == 2) {
    B.targets = dev.alloc(32 * 4);
    dev.put(p.targets.data(), B.targets, 32 * 4);
  }
  EcArgs a{};
  a.mode = p.op->mode;
  a.window = o.window;
  a.harts = o.harts < 2 ? 1 : 2;
  a.sources = reinterpret_cast<uint64_t>(sbuf);
  a.slice = reinterpret_cast<uint64_t>(B.table);
  a.slice_bytes = p.stride;
  a.scp = (uint64_t)p.scp;
  a.scp_off = GS_SCP_OFF;
  a.targets = reinterpret_cast<uint64_t>(B.targets);
  a.minion_mask = o.minionMask;
  a.shire_mask = p.shireMaskUsed;
  a.gs_ws = p.ws;
  a.gs_tile_log2 = p.tileLog2;
  a.gs_step = p.step;
  a.gs_mask = p.mask;
  a.gs_verify = p.verify;
  a.gs_share = (uint64_t)p.shareCode;
  a.gs_params = reinterpret_cast<uint64_t>(B.params);
  a.gs_stage = reinterpret_cast<uint64_t>(B.stage);
  a.gs_check = reinterpret_cast<uint64_t>(B.check);
  a.gs_copy = reinterpret_cast<uint64_t>(B.copy);
  a.gs_warm = p.warm ? 1 : 0;
  a.gs_check_bytes = p.checkBytes;
  // the last guard against writing physical 0 (14-card-behaviour): a memory mode with no table
  if (a.scp == 0 && a.slice == 0) throw std::runtime_error("refusing to launch: gather/scatter mode with no table");
  if (a.gs_check == 0 || a.gs_params == 0) throw std::runtime_error("refusing to launch: no params/check buffer");

  const auto tStart = Clock::now();
  int bad = 0;
  int launches = 0;
  while (p.verify ? launches == 0 : (secondsSince(tStart) < o.seconds && !dev.overBudget())) {
    std::vector<EcResult> res;
    double wallS = 0;
    const bool ok = dev.launch(a, res, wallS);
    ++launches;
    uint64_t n = 0, iters = 0, instr = 0, cmax = 0, gscNonzero = 0, setupMax = 0, itMin = ~0ull, itMax = 0, missing = 0;
    double csum = 0;
    std::vector<double> cpi;
    for (const auto& q : p.parts) {
      const auto& r = res[q.hart];
      if (r.magic != EC_MAGIC || (r.pad[3] & 0xFFFF0000u) != EC_GS_MAGIC) { ++missing; continue; }
      ++n; iters += r.iters; instr += r.pad[0]; cmax = std::max<uint64_t>(cmax, r.cycles); csum += double(r.cycles);
      if (r.pad[1]) ++gscNonzero;
      setupMax = std::max<uint64_t>(setupMax, r.pad[2]);
      itMin = std::min<uint64_t>(itMin, r.iters); itMax = std::max<uint64_t>(itMax, r.iters);
      if (r.pad[0]) cpi.push_back(double(r.cycles) / double(r.pad[0]));
    }
    std::sort(cpi.begin(), cpi.end());
    auto pc = [&](double q) { return cpi.empty() ? 0.0 : cpi[std::min(cpi.size() - 1, (size_t)(q * (cpi.size() - 1) + 0.5))]; };
    const double elements = double(instr) * double(p.perInstr);
    const double bytes = elements * double(p.op->elem);
    const double secs = cmax / 0.6e9;
    std::string verify;
    bool vok = true;
    if (p.verify && ok && n == np) {
      const auto c = gsVerify(dev, p, B, src);
      std::string win = "{";
      bool first = true;
      for (auto& kv : c.winners) { win += (first ? "" : ",") + ("\"" + std::to_string(kv.first) + "\":" + std::to_string(kv.second)); first = false; }
      win += "}";
      int wl = -1; uint64_t wn = 0;
      for (auto& kv : c.winners) if (kv.second > wn) { wn = kv.second; wl = kv.first; }
      vok = c.mismatches == 0 && gscNonzero == 0 && c.checked > 0 && c.probeOk;
      std::string firstBad = c.first;
      for (auto& ch : firstBad) if (ch == '"' || ch == '\\') ch = '\'';
      verify = ",\"verify\":{\"ok\":" + std::string(vok ? "true" : "false") + ",\"checked\":" + std::to_string(c.checked) +
               ",\"mismatches\":" + std::to_string(c.mismatches) + ",\"gsc_nonzero\":" + std::to_string(gscNonzero) +
               ",\"conflicts\":" + std::to_string(c.conflicts) + ",\"conflicts_ambiguous\":" + std::to_string(c.conflictsAmbiguous) +
               ",\"winner_lane\":" + (wl >= 0 ? std::to_string(wl) : std::string("null")) + ",\"winners\":" + win +
               ",\"visits\":" + std::to_string(p.verify) + ",\"warm\":" + (p.warm ? "true" : "false") +
               ",\"first\":\"" + firstBad + "\"" + (c.probe.empty() ? "" : ",\"probe\":" + c.probe) + "}";
    } else if (p.verify) {
      vok = false;
      verify = ",\"verify\":{\"ok\":false,\"checked\":0,\"mismatches\":0,\"gsc_nonzero\":" + std::to_string(gscNonzero) +
               ",\"first\":\"launch failed or harts missing (" + std::to_string(missing) + " of " + std::to_string(np) + ")\"}";
    }
    char gsj[1400];
    std::snprintf(gsj, sizeof gsj,
                  ",\"gs\":{\"op\":\"%s\",\"family\":%d,\"form\":%d,\"index\":\"%s\",\"target\":\"%s\",\"ws\":%llu,\"tile\":%llu,"
                  "\"ntiles\":%llu,\"step\":%llu,\"share\":\"%s\",\"mask\":\"0x%02llx\",\"lanes\":%u,\"elem_bytes\":%d,"
                  "\"instr\":%llu,\"elements\":%.0f,\"per_instr\":%u,\"lines_per_instr\":%.4f,\"cpi_med\":%.3f,\"cpi_p10\":%.3f,"
                  "\"cpi_p90\":%.3f,\"iters_min\":%llu,\"iters_max\":%llu,\"gsc_nonzero\":%llu,\"missing\":%llu,"
                  "\"setup_cycles_max\":%llu,\"warm\":%s,\"verify_visits\":%llu,\"implied_ghz\":%.4f}",
                  p.op->name, p.fam, p.op->form, p.patName.c_str(), p.target.c_str(), (unsigned long long)p.ws,
                  (unsigned long long)p.tile, (unsigned long long)p.ntiles, (unsigned long long)p.step, p.share.c_str(),
                  (unsigned long long)p.mask, p.lanes, p.op->elem, (unsigned long long)instr, elements, p.perInstr,
                  p.linesPerInstr, pc(0.5), pc(0.1), pc(0.9), (unsigned long long)(n ? itMin : 0), (unsigned long long)itMax,
                  (unsigned long long)gscNonzero, (unsigned long long)missing, (unsigned long long)setupMax,
                  p.warm ? "true" : "false", (unsigned long long)p.verify, wallS > 0 ? double(cmax) / wallS / 1e9 : 0.0);
    std::printf("ENERCAT {\"pattern\":\"%s\",\"unit\":\"%s\",\"operands\":\"%s\",\"harts\":%llu,\"shires\":%d,"
                "\"participants\":%llu,\"shire_mask_used\":\"0x%llx\",\"ops\":%.0f,\"bytes\":%.0f,\"cycles_max\":%llu,\"cycles_mean\":%.0f,"
                "\"ops_per_s\":%.4e,\"bytes_per_s\":%.4e,\"ops_per_cycle_per_hart\":%.4f,\"wall_s\":%.4f,"
                "\"scp\":%s,\"slice_bytes\":%llu,\"minion_mask\":\"0x%llx\",\"stride\":0,\"access_bytes\":%d,"
                "\"region\":%llu,\"jump_every\":0,\"jump_bytes\":0,\"hop_distance\":%llu,\"hop_axis\":\"%s\",\"mean_hops\":%.3f,\"targets\":\"%s\",\"target_map\":\"%s\","
                "\"t_start_ms\":%lld,\"t_end_ms\":%lld,\"ok\":%s%s%s}\n",
                o.pattern.c_str(), p.op->unit, o.operands.c_str(), (unsigned long long)(o.harts < 2 ? 1 : 2),
                __builtin_popcountll(p.shireMaskUsed), (unsigned long long)n, (unsigned long long)p.shireMaskUsed, elements,
                bytes, (unsigned long long)cmax, n ? csum / double(n) : 0.0, secs > 0 ? elements / secs : 0.0,
                secs > 0 ? bytes / secs : 0.0, (cmax && n) ? elements / double(cmax) / double(n) : 0.0, wallS,
                p.scp ? "true" : "false", (unsigned long long)p.stride, (unsigned long long)o.minionMask, p.op->elem,
                (unsigned long long)p.ws, (unsigned long long)o.hopDistance, o.hopAxis.c_str(), p.meanHops, o.targets.c_str(),
                p.targetMap.c_str(), dev.t0Ms, dev.t1Ms, (ok && n == np && (!p.verify || vok)) ? "true" : "false", gsj, verify.c_str());
    std::fflush(stdout);
    if (!ok || n != np) { ++bad; break; }
    if (p.verify && !vok) ++bad;
  }
  return bad ? 1 : 0;
}

// Options for one --suite line (and the gs options of the command line): the subset a gs configuration uses.
bool gsParseOne(Options& o, const std::string& a, const std::function<std::string()>& next) {
  if (a == "--gs-index") o.gsIndex = next();
  else if (a == "--ws") o.gsWs = parseSize(next());
  else if (a == "--share") o.gsShare = next();
  else if (a == "--mask") o.gsMask = std::strtoull(next().c_str(), nullptr, 0);
  else if (a == "--verify") o.gsVerify = std::strtoull(next().c_str(), nullptr, 0);
  else if (a == "--warm") o.gsWarm = std::atoi(next().c_str());
  else if (a == "--suite") o.suite = next();
  else return false;
  return true;
}

void gsParseLine(Options& o, const std::vector<std::string>& args) {
  for (size_t i = 0; i < args.size(); ++i) {
    const std::string& a = args[i];
    auto next = [&]() -> std::string {
      if (i + 1 >= args.size()) throw std::runtime_error(a + " needs a value");
      return args[++i];
    };
    if (gsParseOne(o, a, next)) continue;
    if (a == "--pattern") o.pattern = next();
    else if (a == "--operands") o.operands = next();
    else if (a == "--harts") o.harts = std::strtoull(next().c_str(), nullptr, 0);
    else if (a == "--shires") o.shireMask = std::strtoull(next().c_str(), nullptr, 0);
    else if (a == "--minions") o.minionMask = std::strtoull(next().c_str(), nullptr, 0);
    else if (a == "--window") o.window = std::strtoull(next().c_str(), nullptr, 0);
    else if (a == "--seconds") o.seconds = std::strtod(next().c_str(), nullptr);
    else if (a == "--seed") o.seed = std::strtoull(next().c_str(), nullptr, 0);
    else if (a == "--scp") o.scp = true;
    else if (a == "--hop-distance") o.hopDistance = std::strtoull(next().c_str(), nullptr, 0);
    else if (a == "--uniq-regions") o.uniqRegions = true;
    else if (a == "--pairs") o.pairs = next();
    else if (a == "--label") next();
    else throw std::runtime_error("suite line: unsupported option " + a);
  }
}

// One simulator session for many configurations: each line of the file is one configuration's arguments ("#" starts a
// comment; a first word "label=<name>" names it). Every line's shire mask must lie inside the session's --shires.
int runGsSuite(const Options& base, Session& dev) {
  std::ifstream f(base.suite);
  if (!f) throw std::runtime_error("cannot read --suite " + base.suite);
  int failed = 0, n = 0;
  for (std::string line; std::getline(f, line);) {
    const auto hash = line.find('#');
    if (hash != std::string::npos) line = line.substr(0, hash);
    std::istringstream ss(line);
    std::vector<std::string> args;
    for (std::string w; ss >> w;) args.push_back(w);
    if (args.empty()) continue;
    std::string label = "cfg" + std::to_string(n);
    if (args[0].rfind("label=", 0) == 0) { label = args[0].substr(6); args.erase(args.begin()); }
    Options o = base;
    o.suite.clear();
    int rc = 1;
    std::printf("SUITE {\"label\":\"%s\",\"n\":%d,\"args\":\"%s\"}\n", label.c_str(), n, line.c_str());
    std::fflush(stdout);
    try {
      gsParseLine(o, args);
      if ((o.shireMask & ~base.shireMask) != 0) throw std::runtime_error("suite line uses shires outside the session's --shires");
      rc = runGs(o, dev);
    } catch (const std::exception& e) {
      std::printf("SUITEFAIL {\"label\":\"%s\",\"error\":\"%s\"}\n", label.c_str(), e.what());
    }
    dev.freeAll();
    std::printf("SUITEEND {\"label\":\"%s\",\"rc\":%d}\n", label.c_str(), rc);
    std::fflush(stdout);
    if (rc) ++failed;
    ++n;
  }
  std::printf("SUITEDONE {\"n\":%d,\"failed\":%d}\n", n, failed);
  return failed ? 1 : 0;
}
