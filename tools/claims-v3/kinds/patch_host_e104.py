#!/usr/bin/env python3
"""E104: the one host change that reads the accumulators back. Applied by build_host_e104.sh to a COPY of workloads/sparsity in E104's own build directory;
workloads/sparsity itself and build/sparsity (the binary every power pass runs) stay as they are. Standard library only.

    patch_host_e104.py <copy of workloads/sparsity/host/main.cpp>

`--dump-c <file>` makes --test fma write, after each launch, the buffer the kernel copies C into on a launch's last op (run_fma in kernel/sparsity.c,
a->out + minion * SP_TILE_BYTES): SP_MINIONS x 256 words, minion m's C[i][j] at word m*256 + i*16 + j, as checkC reads it. The kernel is not rebuilt: the
read-back runs pass --kernel with the ELF of the existing build. Nothing else changes: same launch, same tile, one more DMA read after it, and only when
the flag is given.
"""
import hashlib
import sys

WANT_SHA = "0f53a7d5"  # the first 8 hex of workloads/sparsity/host/main.cpp as the box and the repo hold it

PATCHES = (
    ('  std::string dumpTiles;         // --test fma: write the A and B tiles (2 x 1024 bytes) here\n',
     '  std::string dumpTiles;         // --test fma: write the A and B tiles (2 x 1024 bytes) here\n'
     '  std::string dumpC;             // E104, --test fma: write C after each launch (SP_MINIONS x 256 words) here\n'),
    ('      const Summary sm = summarize(L, harts);\n      const std::string check =\n        !L.ok ? "no-result" : rawValues ? "unchecked" : checkC(dev, t, type, iters, harts, uint32_t(a.mask));\n',
     '      const Summary sm = summarize(L, harts);\n      if (L.ok && !o.dumpC.empty()) {\n        std::vector<uint32_t> cd(SP_MINIONS * 256);\n        dev.get("out", cd.data(), cd.size() * 4);\n'
     '        std::ofstream df(o.dumpC, std::ios::binary);\n        df.write(reinterpret_cast<const char*>(cd.data()), std::streamsize(cd.size() * 4));\n      }\n'
     '      const std::string check =\n        !L.ok ? "no-result" : rawValues ? "unchecked" : checkC(dev, t, type, iters, harts, uint32_t(a.mask));\n'),
    ('    else if (a == "--values") o.values = next();\n',
     '    else if (a == "--values") o.values = next();\n    else if (a == "--dump-c") o.dumpC = next();\n'),
)


def main():
    p = sys.argv[1]
    raw = open(p, "rb").read()
    have = hashlib.sha256(raw).hexdigest()
    assert have.startswith(WANT_SHA), f"main.cpp sha256 {have} is not the one this patch was written for"
    s = raw.decode()
    for old, new in PATCHES:
        assert s.count(old) == 1, old
        s = s.replace(old, new)
    open(p, "w").write(s)
    print("patched", p, "sha256", hashlib.sha256(s.encode()).hexdigest())


if __name__ == "__main__":
    main()
