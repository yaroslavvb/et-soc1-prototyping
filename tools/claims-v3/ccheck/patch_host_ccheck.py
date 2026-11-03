#!/usr/bin/env python3
"""Q139(k): the host change that logs every launch's C, so ccheck.py can check it. Applied by build_host_ccheck.sh to a
COPY of workloads/sparsity in build/ccheck/; workloads/sparsity and build/sparsity (the binary the power passes run) are
not touched. Standard library only. E104's patch_host_e104.py is the precedent (its --dump-c read the same buffer).

    patch_host_ccheck.py <copy of workloads/sparsity/host/main.cpp>

Two flags, both for --test fma, both off unless given:
  --c-log <file>  after each launch, one more read of the buffer the kernel stores C into on a launch's last op (run_fma,
                  a->out + minion * SP_TILE_BYTES; `dev.get("out", ...)`, the runtime's device-to-host DMA, the read
                  checkC already makes on --values small launches), and one JSON line appended to <file>: the launch's own
                  iters, its window, its kernel flags (use_mask, row_mask, b_stream: ccheck.py refuses a launch with the
                  mask on or B streamed, which its reference does not model), and each distinct 1,024-byte C among the
                  participating minions with how many hold it. Each sweep point's A and B tiles (the bytes the launch
                  used, file: or built-in) are logged once before its launches, with the kernel's path. The read comes
                  after the launch's end time stamp and after its SPARSITY line.
                  (Fix pass of Tue 3 Nov 2026: the flags and the kernel's path are new; the patch of 60b91395 logged
                  neither, and no card ran it.)
  --c-poison      with --c-log, write 0x7FBADBAD to the whole C buffer before each launch (`dev.put("out", ...)`, the
                  host-to-device DMA the harness already makes every launch for the results buffer), so a minion that
                  never stored C reads as the poison, not as the previous launch's C. The write comes before the launch's
                  start time stamp.
The SPARSITY line, the kernel, the tiles, the launch and its timing are unchanged; no new device command of any kind.
"""
import hashlib
import sys

WANT_SHA = "0f53a7d505155156c933e2d9a64d38803ca4e0cea3e20242e0aaafbf35e82284"  # workloads/sparsity/host/main.cpp

FUNCS = r'''// Q139(k) (tools/claims-v3/ccheck): the C log. One JSON line per launch, appended: the launch's own iters and window, and
// each distinct 1,024-byte C among the participating minions with how many hold it (minions listed for groups of <= 64);
// the A and B tiles once per sweep point. The check runs at the desk (ccheck.py) against the bench's arithmetic.
constexpr uint32_t CC_POISON = 0x7FBADBADu;  // a NaN payload the tensor unit does not write on finite operands

std::string ccHex(const uint8_t* p, size_t n) {
  static const char* d = "0123456789abcdef";
  std::string s(2 * n, '0');
  for (size_t i = 0; i < n; ++i) {
    s[2 * i] = d[p[i] >> 4];
    s[2 * i + 1] = d[p[i] & 15];
  }
  return s;
}

uint64_t ccFnv(const Tiles& t) {  // FNV-1a over A then B, pairing a launch's C with its tiles
  uint64_t h = 1469598103934665603ull;
  for (const auto* v : {&t.a, &t.b}) {
    for (uint8_t x : *v) {
      h ^= x;
      h *= 1099511628211ull;
    }
  }
  return h;
}

std::string ccJson(const std::string& s) {
  std::string o;
  for (char c : s) {
    if (c == '"' || c == '\\') o += '\\';
    o += c;
  }
  return o;
}

void ccLogTiles(const Options& o, const Tiles& t, double s) {
  std::ofstream f(o.cLog, std::ios::app);
  char fnv[24];
  std::snprintf(fnv, sizeof fnv, "%016llx", (unsigned long long)ccFnv(t));
  f << "{\"ccheck\":1,\"kind\":\"tiles\",\"type\":\"" << o.type << "\",\"values\":\"" << ccJson(o.values)
    << "\",\"kernel\":\"" << ccJson(o.kernel) << "\",\"sweep\":" << s << ",\"fnv\":\"" << fnv << "\",\"a\":\""
    << ccHex(t.a.data(), t.a.size()) << "\",\"b\":\"" << ccHex(t.b.data(), t.b.size()) << "\"}\n";
}

void ccLogLaunch(const Options& o, Session& dev, const Tiles& t, const SpArgs& a, uint64_t iters, int launchNo,
                 const Session::Launch& L, const std::vector<uint64_t>& harts, double s) {
  std::map<std::string, std::vector<uint64_t>> groups;
  if (L.ok) {
    std::vector<uint8_t> c(size_t(SP_MINIONS) * SP_TILE_BYTES);
    dev.get("out", c.data(), c.size());
    for (uint64_t h : harts) {
      const uint64_t m = h >> 1;
      groups[std::string(reinterpret_cast<const char*>(&c[m * SP_TILE_BYTES]), SP_TILE_BYTES)].push_back(m);
    }
  }
  char head[640];
  std::snprintf(head, sizeof head,
                "{\"ccheck\":1,\"kind\":\"c\",\"type\":\"%s\",\"sweep\":%.4f,\"launch\":%d,\"iters\":%llu,\"t_start_ms\":%lld,"
                "\"t_end_ms\":%lld,\"ok\":%s,\"participants\":%zu,\"poison\":%s,\"use_mask\":%llu,\"row_mask\":\"0x%04llx\","
                "\"b_stream\":%llu,\"fnv\":\"%016llx\",\"groups\":[",
                o.type.c_str(), s, launchNo, (unsigned long long)iters, L.t0Ms, L.t1Ms, L.ok ? "true" : "false",
                harts.size(), o.cPoison ? "true" : "false", (unsigned long long)a.use_mask,
                (unsigned long long)(a.mask & 0xFFFF), (unsigned long long)a.b_stream, (unsigned long long)ccFnv(t));
  std::ofstream f(o.cLog, std::ios::app);
  f << head;
  bool first = true;
  for (const auto& [bytes, ms] : groups) {
    f << (first ? "" : ",") << "{\"count\":" << ms.size() << ",\"first_minion\":" << ms.front() << ",\"minions\":[";
    if (ms.size() <= 64) {
      for (size_t i = 0; i < ms.size(); ++i) f << (i ? "," : "") << ms[i];
    }
    f << "],\"hex\":\"" << ccHex(reinterpret_cast<const uint8_t*>(bytes.data()), bytes.size()) << "\"}";
    first = false;
  }
  f << "]}\n";
}

'''

PATCHES = (
    # 1. the options
    ('  std::string dumpTiles;         // --test fma: write the A and B tiles (2 x 1024 bytes) here\n',
     '  std::string dumpTiles;         // --test fma: write the A and B tiles (2 x 1024 bytes) here\n'
     '  std::string cLog;              // Q139(k), --test fma: append each launch\'s C (tools/claims-v3/ccheck) here\n'
     '  bool cPoison = false;          // Q139(k), with --c-log: poison the C buffer before each launch\n'),
    # 2. the log's functions, after checkC
    ('uint64_t typeOf(const std::string& s) {\n', FUNCS + 'uint64_t typeOf(const std::string& s) {\n'),
    # 3. the tiles, once per sweep point, after the launch arguments are set
    ('    a.mask = o.rowMask >= 0 ? uint64_t(o.rowMask) & 0xFFFF : 0xFFFF;\n    auto one = [&](uint64_t iters, int launchNo) -> double {\n',
     '    a.mask = o.rowMask >= 0 ? uint64_t(o.rowMask) & 0xFFFF : 0xFFFF;\n    if (!o.cLog.empty()) {\n'
     '      ccLogTiles(o, t, s);\n    }\n    auto one = [&](uint64_t iters, int launchNo) -> double {\n'),
    # 4. the poison, before the launch (before its start time stamp)
    ('      a.iters = iters;\n      const auto L = dev.launch(a);\n      const Summary sm = summarize(L, harts);\n      const std::string check =\n',
     '      a.iters = iters;\n      if (!o.cLog.empty() && o.cPoison) {\n'
     '        static const std::vector<uint32_t> poison(size_t(SP_MINIONS) * 256, CC_POISON);\n'
     '        dev.put("out", poison.data(), poison.size() * 4);\n      }\n'
     '      const auto L = dev.launch(a);\n      const Summary sm = summarize(L, harts);\n      const std::string check =\n'),
    # 5. the read and the log line, after the launch's SPARSITY line
    ('      std::fflush(stdout);\n      return L.wallS;\n    };\n    repeatFor(o, dev, o.iters ? o.iters : (o.sysemu ? 4 : 20000), one);\n',
     '      std::fflush(stdout);\n      if (!o.cLog.empty()) {\n        ccLogLaunch(o, dev, t, a, iters, launchNo, L, harts, s);\n      }\n'
     '      return L.wallS;\n    };\n    repeatFor(o, dev, o.iters ? o.iters : (o.sysemu ? 4 : 20000), one);\n'),
    # 6. the flags
    ('    else if (a == "--dump-tiles") o.dumpTiles = next();\n',
     '    else if (a == "--dump-tiles") o.dumpTiles = next();\n    else if (a == "--c-log") o.cLog = next();\n'
     '    else if (a == "--c-poison") o.cPoison = true;\n'),
)


def patch_text(s):
    for old, new in PATCHES:
        assert s.count(old) == 1, "patch anchor not found exactly once:\n" + old
        s = s.replace(old, new)
    return s


def main():
    p = sys.argv[1]
    raw = open(p, "rb").read()
    have = hashlib.sha256(raw).hexdigest()
    assert have == WANT_SHA, f"main.cpp sha256 {have} is not the one this patch was written for ({WANT_SHA})"
    s = patch_text(raw.decode())
    open(p, "w").write(s)
    print("patched", p, "sha256", hashlib.sha256(s.encode()).hexdigest())


if __name__ == "__main__":
    main()
