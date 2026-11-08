#!/usr/bin/env python3
"""E183 (Q155, the kit): the host-only change that runs an A B B A train of two one-number operand images inside one process (E183.md
section 3). Applied by build_host_e183.sh to the copy of host/main.cpp inside the build tree E180's own generator writes
(tools/claims-v3/e180/gen_acc_e180.py --src workloads/enercat --dst build/enercat-e183-src, unchanged); workloads/enercat and every
committed file stay as they are. Standard library only.

    /usr/bin/python3 -B patch_host_e183.py <build tree>/host/main.cpp       # patch it in place (its sha256 must be SRC_SHA256)
    /usr/bin/python3 -B patch_host_e183.py --check workloads/enercat         # the patch applies to the committed main.cpp, and gives OUT_SHA256
    /usr/bin/python3 -B patch_host_e183.py --print-sha                       # SRC_SHA256 and OUT_SHA256

Three flags, all off unless given (without --operands-b the host is the catalogue's own, line for line):
  --operands-b file:<path>  the S kind's 256 B image; with it the process is a train: the F image (--operands file:) and the S image are
                            each copied to the card once (`dev.put`, the runtime's host-to-device copy the host already makes), and each
                            launch's kernel argument `sources` points at one of them;
  --abba SFFS|FSSF          the order: launch 0 (the settle) takes its first letter, launch n >= 1 takes letter (n - 1) mod 4;
  --launches N              with --operands-b: exactly N launches, then the process ends (E183: 13); fewer (the budget or --seconds ran
                            out first) exits 3 after the last record.
Every launch's ENERCAT line gains "train_kind" (F or S), "train_operands" (that kind's --operands string), "abba" and "launch" (0..N-1).
The kernel, the mode, the launch, its window and every device call are unchanged: no new device command of any kind.
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import os
import sys

SRC_SHA256 = "3cad4adc16534b845cc142f78a28907192b62fe21081e282d6df67342200359c"   # the committed workloads/enercat/host/main.cpp
OUT_SHA256 = "9b8f1a088a7a83c00af64387c80f0f92b0522dcb89ce3a330853ca8e00b0c5f1"   # the patched host/main.cpp, pinned

PATCHES = (
    # 1. the options
    ('  std::string kernel = KERNEL_ELF;\n',
     '  std::string kernel = KERNEL_ELF;\n'
     '  std::string operandsB, abba = "SFFS";   // E183 (tools/claims-v3/e183): --operands-b file:<S image>, --abba SFFS|FSSF\n'
     '  uint64_t launches = 0;                  // E183, with --operands-b: exactly this many launches\n'),
    # 2. the flags, after --kernel
    ('    else if (a == "--kernel") o.kernel = next();\n',
     '    else if (a == "--kernel") o.kernel = next();\n'
     '    else if (a == "--operands-b") o.operandsB = next();   // E183\n'
     '    else if (a == "--abba") o.abba = next();              // E183\n'
     '    else if (a == "--launches") o.launches = std::strtoull(next().c_str(), nullptr, 0);   // E183\n'),
    # 3. the S image on the card, once, beside the F image
    ('  dev.put(src.data(), sbuf, src.size() * 4);\n',
     '  dev.put(src.data(), sbuf, src.size() * 4);\n'
     '  // E183: a train (--operands-b): the S kind\'s image on the card beside the F kind\'s, once; each launch points sources at one\n'
     '  const bool train = !o.operandsB.empty();\n'
     '  std::byte* sbufB = nullptr;\n'
     '  if (train) {\n'
     '    if (o.operands.rfind("file:", 0) != 0 || o.operandsB.rfind("file:", 0) != 0) {\n'
     '      throw std::runtime_error("E183: a train takes --operands file: and --operands-b file:");\n'
     '    }\n'
     '    if (o.abba != "SFFS" && o.abba != "FSSF") throw std::runtime_error("E183: --abba is SFFS or FSSF");\n'
     '    if (o.launches == 0) throw std::runtime_error("E183: a train needs --launches");\n'
     '    if (p.mode == EC_TSTORE_UNIQ) throw std::runtime_error("E183: a train runs a vector mode, not tstore_uniq");\n'
     '    const auto srcB = sources(o.operandsB, o.seed);\n'
     '    if (srcB.size() != src.size()) throw std::runtime_error("E183: the two images\' source buffers differ in size");\n'
     '    sbufB = dev.alloc(srcB.size() * 4);\n'
     '    dev.put(srcB.data(), sbufB, srcB.size() * 4);\n'
     '  }\n'),
    # 4. each launch's kind, before the launch
    ('  int bad = 0;\n  while (secondsSince(tStart) < o.seconds && !dev.overBudget()) {\n    std::vector<EcResult> res;\n'
     '    double wallS = 0;\n    const bool ok = dev.launch(a, res, wallS);\n',
     '  int bad = 0;\n  long long launchNo = 0;   // E183\n'
     '  while (secondsSince(tStart) < o.seconds && !dev.overBudget()) {\n'
     '    if (train && launchNo >= (long long)o.launches) break;   // E183\n'
     '    std::string trainField;\n'
     '    if (train) {   // E183: launch 0 takes the order\'s first letter, launch n >= 1 letter (n - 1) mod 4\n'
     '      const char c = launchNo < 1 ? o.abba[0] : o.abba[size_t((launchNo - 1) % 4)];\n'
     '      a.sources = reinterpret_cast<uint64_t>(c == \'F\' ? sbuf : sbufB);\n'
     '      trainField = std::string(",\\"train_kind\\":\\"") + c + "\\",\\"train_operands\\":\\"" + (c == \'F\' ? o.operands : o.operandsB) +\n'
     '                   "\\",\\"abba\\":\\"" + o.abba + "\\",\\"launch\\":" + std::to_string(launchNo);\n'
     '    }\n'
     '    std::vector<EcResult> res;\n'
     '    double wallS = 0;\n    const bool ok = dev.launch(a, res, wallS);\n'),
    # 5. the ENERCAT line carries the kind
    ('"\\"t_start_ms\\":%lld,\\"t_end_ms\\":%lld,\\"ok\\":%s}\\n",\n',
     '"\\"t_start_ms\\":%lld,\\"t_end_ms\\":%lld,\\"ok\\":%s%s}\\n",\n'),
    ('                dev.t0Ms, dev.t1Ms, (ok && n) ? "true" : "false");\n    std::fflush(stdout);\n'
     '    if (!ok || !n) { ++bad; break; }\n  }\n',
     '                dev.t0Ms, dev.t1Ms, (ok && n) ? "true" : "false", trainField.c_str());\n    std::fflush(stdout);\n'
     '    ++launchNo;   // E183\n'
     '    if (!ok || !n) { ++bad; break; }\n  }\n'
     '  if (train && !bad && launchNo < (long long)o.launches) {   // E183: a train cut short by the budget or --seconds\n'
     '    std::fprintf(stderr, "E183: the train ended after %lld of %llu launches\\n", launchNo, (unsigned long long)o.launches);\n'
     '    return 3;\n'
     '  }\n'),
)


def patch_text(s):
    for old, new in PATCHES:
        if s.count(old) != 1:
            raise SystemExit("E183 patch anchor not found exactly once:\n" + old)
        s = s.replace(old, new)
    return s


def main():
    a = sys.argv[1:]
    if a == ["--print-sha"]:
        print("SRC_SHA256", SRC_SHA256)
        print("OUT_SHA256", OUT_SHA256)
        return 0
    if len(a) == 2 and a[0] == "--check":
        raw = open(os.path.join(a[1], "host", "main.cpp"), "rb").read()
        have = hashlib.sha256(raw).hexdigest()
        if have != SRC_SHA256:
            print(f"PATCH-CHECK FAIL: {a[1]}/host/main.cpp sha256 {have} is not the committed {SRC_SHA256}")
            return 2
        out = hashlib.sha256(patch_text(raw.decode()).encode()).hexdigest()
        if out != OUT_SHA256:
            print(f"PATCH-CHECK FAIL: the patched main.cpp would be {out}, not the pinned {OUT_SHA256}")
            return 2
        print(f"PATCH-CHECK OK: {SRC_SHA256[:12]} -> {OUT_SHA256[:12]}")
        return 0
    if len(a) != 1:
        print(__doc__)
        return 2
    p = a[0]
    raw = open(p, "rb").read()
    have = hashlib.sha256(raw).hexdigest()
    if have != SRC_SHA256:
        print(f"{p}: sha256 {have} is not the committed main.cpp the patch was written for ({SRC_SHA256})")
        return 2
    s = patch_text(raw.decode())
    out = hashlib.sha256(s.encode()).hexdigest()
    if out != OUT_SHA256:
        print(f"{p}: the patched text's sha256 {out} is not the pinned {OUT_SHA256}: nothing written")
        return 2
    open(p, "w").write(s)
    print("patched", p, "sha256", out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
