#!/usr/bin/env python3
"""E99: write the host source E99 builds: workloads/enercat/host/main.cpp with one operand added. The tree's main.cpp stays
as it is, so no other experiment's build changes.

    python3 tools/claims-v3/dm/make_host_src.py workloads/enercat/host/main.cpp build/enercat-e99/main_e99.cpp

--operands file: takes exactly 256 B (four lines), which is why E81 could not run a period between 4 and 8,192 lines.
--operands lines:<path> takes any whole number of 64 B lines up to the 512 KB a built-in source holds. The source buffer
becomes a whole number of images at least as long as the built-in one, so the slices' fill, src[i % src.size()], has exactly
the image's period everywhere, and the kernel, which reads no operand from it for flw_pat, is untouched.
"""
import sys

ANCHOR = '  if (kind.rfind("bern:", 0) == 0) {\n'
BRANCH = '''  if (kind.rfind("lines:", 0) == 0) {   // E99, tools/claims-v3/dm: any whole number of 64 B lines, up to 512 KB
    std::ifstream f(kind.substr(6), std::ios::binary | std::ios::ate);
    if (!f) throw std::runtime_error("--operands lines: cannot read " + kind.substr(6));
    const size_t bytes = static_cast<size_t>(f.tellg());
    if (bytes == 0 || bytes % 64 || bytes > v.size() * 4)
      throw std::runtime_error("--operands lines: needs a whole number of 64 B lines, at most 512 KB: " + kind.substr(6));
    std::vector<uint32_t> img(bytes / 4);
    f.seekg(0);
    f.read(reinterpret_cast<char*>(img.data()), static_cast<std::streamsize>(bytes));
    if (!f) throw std::runtime_error("--operands lines: short read: " + kind.substr(6));
    v.resize((v.size() + img.size() - 1) / img.size() * img.size());
    for (size_t i = 0; i < v.size(); ++i) v[i] = img[i % img.size()];
    return v;
  }
'''


def main():
    src = open(sys.argv[1]).read()
    if src.count(ANCHOR) != 1:
        raise SystemExit("the anchor line must occur exactly once in " + sys.argv[1])
    open(sys.argv[2], "w").write(src.replace(ANCHOR, BRANCH + ANCHOR))


if __name__ == "__main__":
    main()
