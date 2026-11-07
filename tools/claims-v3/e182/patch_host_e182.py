#!/usr/bin/env python3
"""E182 (Q153, the kit): the host-only change that runs an A B B A train inside one process (E182.md section 3). Applied by
build_host_e182.sh to a COPY of workloads/sparsity in build/e182host/; workloads/sparsity, build/sparsity and build/ccheck (the binaries
the kinds passes run) are not touched. Standard library only.

    patch_host_e182.py <copy of workloads/sparsity/host/main.cpp>

It first applies Q139(k)'s C-log patch, tools/claims-v3/ccheck/patch_host_ccheck.py's patch_text(), unchanged (the copy must be the
committed main.cpp: that patch checks its sha256), then three flags for --test fma, all off unless given:
  --values-b file:<path>  the second kind's tiles (raw A then raw B, 1,024 bytes each, as --values file: takes them); with it the process
                          is a train: both tile sets are copied to the card once (`dev.put`, the runtime's host-to-device DMA the host
                          already makes), and each launch points the kernel's a_tile and b_tile at one of them;
  --abba SFFS|FSSF        the order: F is the --values kind, S the --values-b kind; the calibration launch (launch -1) and the settle
                          (launch 0) take the order's first letter, and launch n >= 1 takes letter (n - 1) mod 4;
  --launches N            with --values-b: stop after exactly N launches after the calibration launch (E182: 13).
Every launch's SPARSITY line gains "train_kind" (F or S), "train_values" (that kind's --values string) and "abba"; the C log logs both
tile sets once (the --values-b set under its own values string) and pairs each launch's C with the tiles it ran (their fnv), so the check
of C judges every train launch against its own tiles; --dump-tiles also writes the S tiles to <path>.S. The kernel, the launch, its
timing and every device call are unchanged: no new device command of any kind.
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(TOP, "tools", "claims-v3", "ccheck"))
import patch_host_ccheck as PC  # noqa: E402  (patch_text and WANT_SHA only; its main() is not called)

PATCHES = (
    # 1. the options, after the C log's two
    ('  bool cPoison = false;          // Q139(k), with --c-log: poison the C buffer before each launch\n',
     '  bool cPoison = false;          // Q139(k), with --c-log: poison the C buffer before each launch\n'
     '  std::string valuesB;           // E182, --test fma: the second kind\'s tiles (file:); with it the process is an A B B A train\n'
     '  std::string abba = "SFFS";     // E182: SFFS or FSSF (F = the --values kind, S = the --values-b kind)\n'
     '  uint64_t launches = 0;         // E182, with --values-b: exactly this many launches after the calibration launch\n'),
    # 2. the flags, after the C log's two
    ('    else if (a == "--c-poison") o.cPoison = true;\n',
     '    else if (a == "--c-poison") o.cPoison = true;\n'
     '    else if (a == "--values-b") o.valuesB = next();\n'
     '    else if (a == "--abba") o.abba = next();\n'
     '    else if (a == "--launches") o.launches = std::strtoull(next().c_str(), nullptr, 0);\n'),
    # 3. the launch count: repeatFor stops after --launches launches (0: unchanged)
    ('  for (int n = 0; spent < o.seconds; ++n) {\n    if (dev.overBudget()) {\n',
     '  for (int n = 0; spent < o.seconds; ++n) {\n    if (o.launches > 0 && uint64_t(n) >= o.launches) {\n      break;  // E182\n    }\n'
     '    if (dev.overBudget()) {\n'),
    # 4. the second tile set, after the dump of the first and before the launch arguments
    ('      f.write(reinterpret_cast<const char*>(t.b.data()), std::streamsize(t.b.size()));\n    }\n    SpArgs a{};\n',
     '      f.write(reinterpret_cast<const char*>(t.b.data()), std::streamsize(t.b.size()));\n    }\n'
     '    Tiles t2 = t;  // E182: the S kind\'s tiles (the same layout); used only when --values-b is given\n'
     '    const bool train = !o.valuesB.empty();\n'
     '    if (train) {\n'
     '      if (o.values.rfind("file:", 0) != 0 || o.valuesB.rfind("file:", 0) != 0) {\n'
     '        throw std::runtime_error("E182: a train takes --values file: and --values-b file:");\n'
     '      }\n'
     '      if (o.abba != "SFFS" && o.abba != "FSSF") {\n'
     '        throw std::runtime_error("E182: --abba is SFFS or FSSF");\n'
     '      }\n'
     '      if (o.launches == 0) {\n'
     '        throw std::runtime_error("E182: a train needs --launches");\n'
     '      }\n'
     '      fillValues(t2, type, o.valuesB, rng);\n'
     '      if (!o.dumpTiles.empty()) {\n'
     '        std::ofstream f(o.dumpTiles + ".S", std::ios::binary);\n'
     '        f.write(reinterpret_cast<const char*>(t2.a.data()), std::streamsize(t2.a.size()));\n'
     '        f.write(reinterpret_cast<const char*>(t2.b.data()), std::streamsize(t2.b.size()));\n'
     '      }\n'
     '    }\n'
     '    SpArgs a{};\n'),
    # 5. the S tiles on the card, once, beside the F tiles
    ('    a.b_tile = dev.put("b", t.b.data(), t.b.size());\n',
     '    a.b_tile = dev.put("b", t.b.data(), t.b.size());\n'
     '    const uint64_t aF = a.a_tile, bF = a.b_tile;  // E182\n'
     '    const uint64_t aS = train ? dev.put("a2", t2.a.data(), t2.a.size()) : 0;\n'
     '    const uint64_t bS = train ? dev.put("b2", t2.b.data(), t2.b.size()) : 0;\n'),
    # 6. the C log names the S tiles too (under their own values string), once, after the F tiles
    ('    if (!o.cLog.empty()) {\n      ccLogTiles(o, t, s);\n    }\n',
     '    if (!o.cLog.empty()) {\n      ccLogTiles(o, t, s);\n      if (train) {  // E182\n        Options oS = o;\n'
     '        oS.values = o.valuesB;\n        ccLogTiles(oS, t2, s);\n      }\n    }\n'),
    # 7. each launch's kind, before the poison and the launch
    ('      a.iters = iters;\n      if (!o.cLog.empty() && o.cPoison) {\n',
     '      a.iters = iters;\n'
     '      const Tiles* tl = &t;  // E182: the tiles this launch runs\n'
     '      std::string trainField;\n'
     '      if (train) {\n'
     '        const char c = launchNo < 1 ? o.abba[0] : o.abba[size_t((launchNo - 1) % 4)];\n'
     '        tl = c == \'F\' ? &t : &t2;\n'
     '        a.a_tile = c == \'F\' ? aF : aS;\n'
     '        a.b_tile = c == \'F\' ? bF : bS;\n'
     '        trainField = std::string(",\\"train_kind\\":\\"") + c + "\\",\\"train_values\\":\\"" + (c == \'F\' ? o.values : o.valuesB) +\n'
     '                     "\\",\\"abba\\":\\"" + o.abba + "\\"";\n'
     '      }\n'
     '      if (!o.cLog.empty() && o.cPoison) {\n'),
    # 8. the SPARSITY line carries the kind
    ('"\\"ghz\\":%.4f,\\"tensor_errors\\":%llu,\\"result\\":\\"%s\\",\\"ok\\":%s}\\n",\n',
     '"\\"ghz\\":%.4f,\\"tensor_errors\\":%llu,\\"result\\":\\"%s\\",\\"ok\\":%s%s}\\n",\n'),
    ('                  (unsigned long long)sm.tensorErrors, check.c_str(), ok ? "true" : "false");\n',
     '                  (unsigned long long)sm.tensorErrors, check.c_str(), ok ? "true" : "false", trainField.c_str());\n'),
    # 9. the C record pairs with the launch's own tiles
    ('        ccLogLaunch(o, dev, t, a, iters, launchNo, L, harts, s);\n',
     '        ccLogLaunch(o, dev, *tl, a, iters, launchNo, L, harts, s);\n'),
)


def patch_text(s):
    s = PC.patch_text(s)
    for old, new in PATCHES:
        assert s.count(old) == 1, "E182 patch anchor not found exactly once:\n" + old
        s = s.replace(old, new)
    return s


def main():
    p = sys.argv[1]
    raw = open(p, "rb").read()
    have = hashlib.sha256(raw).hexdigest()
    assert have == PC.WANT_SHA, f"main.cpp sha256 {have} is not the committed one the C-log patch was written for ({PC.WANT_SHA})"
    s = patch_text(raw.decode())
    open(p, "w").write(s)
    print("patched", p, "sha256", hashlib.sha256(s.encode()).hexdigest())


if __name__ == "__main__":
    main()
