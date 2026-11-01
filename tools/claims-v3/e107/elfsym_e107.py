#!/usr/bin/env python3
"""E107, POST HOC (written Sun 1 Nov 2026 ~12:50 PST, after the verifier's review; labelled, never a verdict): the size of one symbol in each kernel
ELF, with the file's sha256, so the README's "the compiled entry_point differs" can be re-derived. Standard library; reads ELF64 little-endian
symbol tables (.symtab, else .dynsym).

    python3 tools/claims-v3/e107/elfsym_e107.py entry_point <rgm105 sparsity.elf> <rgm107 sparsity.elf>

The ELFs are the boxes' build/e105/kernel/sparsity.elf and build/e107/kernel/sparsity.elf; their sha256 are committed in
docs/reports/data/2026-11-01-e105-gemm-layout/aifoundry3/binaries.sha256 and docs/reports/data/2026-11-01-e107-gemm-placement/logs/e107-binaries.sha256.
On a box, the `nm -S` of /opt/et's RISC-V toolchain prints the same st_size (in hex).
"""
import hashlib
import struct
import sys

SHT_SYMTAB, SHT_DYNSYM = 2, 11


def symbols(blob):
    if blob[:4] != b"\x7fELF" or blob[4] != 2 or blob[5] != 1:
        raise SystemExit("not an ELF64 little-endian file")
    e_shoff, = struct.unpack_from("<Q", blob, 0x28)
    e_shentsize, e_shnum = struct.unpack_from("<HH", blob, 0x3A)
    sections = [struct.unpack_from("<IIQQQQIIQQ", blob, e_shoff + i * e_shentsize) for i in range(e_shnum)]
    tables = [s for s in sections if s[1] == SHT_SYMTAB] or [s for s in sections if s[1] == SHT_DYNSYM]
    out = []
    for _name, _typ, _flags, _addr, off, size, link, _info, _align, entsize in tables:
        stroff = sections[link][4]
        for j in range(size // entsize):
            st_name, st_info, _other, _shndx, st_value, st_size = struct.unpack_from("<IBBHQQ", blob, off + j * entsize)
            end = blob.index(b"\0", stroff + st_name)
            out.append((blob[stroff + st_name:end].decode("ascii", "replace"), st_value, st_size, st_info & 0xF))
    return out


def main():
    if len(sys.argv) < 3:
        raise SystemExit(__doc__)
    want = sys.argv[1]
    for path in sys.argv[2:]:
        blob = open(path, "rb").read()
        print(f"{path.split('/')[-1]}  sha256 {hashlib.sha256(blob).hexdigest()}  ({len(blob)} bytes)")
        hits = [s for s in symbols(blob) if s[0] == want]
        for name, value, size, typ in hits:
            print(f"   {name}  value 0x{value:x}  size {size} bytes  type {typ}")
        if not hits:
            print(f"   no symbol named {want}")


if __name__ == "__main__":
    main()
