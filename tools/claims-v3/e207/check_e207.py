#!/usr/bin/env python3
"""E207's harness and THE KERNEL GATE (Q199, lane kit-e207, Mon 16 Nov 2026, before any E207 datum): the sha256 of every file the box
(aifoundry3 ~/aifoundry) runs or reads, and its check; E206's harness (tools/claims-v3/e206/check_e206.py, landed in 906699ea) for E207's
files, with E191's kernel gate for rgm136's one kernel, unchanged. Python's own modules only.

    python3 -B tools/claims-v3/e207/check_e207.py --make            writes harness-e207.json (the desk, from the lab clone)
    python3 -B tools/claims-v3/e207/check_e207.py --check           re-makes it in memory and compares: CHECK PASS
    python3 -B tools/claims-v3/e207/check_e207.py --box [--only-src]
                    on the box's tree (or the desk's): every file at its sha256 (HARNESS OK: <n> files); --only-src the ten rgm136 sources
                    only (build_e207.sh's first check)
    python3 -B tools/claims-v3/e207/check_e207.py --list            the paths, one a line (step 5's sync list)
    python3 -B tools/claims-v3/e207/check_e207.py --kernel <elf>    THE KERNEL GATE on one ELF: KERNEL OK: ... or KERNEL FAILED: <why>
    python3 -B tools/claims-v3/e207/check_e207.py --identity <elf>  the ELF's loadable identity (JSON) and its sha256

THE KERNEL GATE (kernel-e207.json, equal to E206's kernel-e206.json; E207.md 2: "on aifoundry3 the kernel is gated on its .text (E191's kit
fix; E206's kit)"): rgm136's kernel ELF as built on aifoundry2 and aifoundry1 is aace138c... (E136's build record), but aifoundry3's riscv gcc
prints "(g1b306039a) 15.1.0" where theirs print "() 15.1.0", and the string lands in the ELF (.comment, a section the card never loads), so
aifoundry3's build cannot reach the whole-ELF pin (E206 arm A's build there read "ELF ff2723b8... not the registered, loadable identity the
pinned 649d4079..."). For each built kernel:
  1. its .text sha256 (objcopy -O binary -j .text, the registered recipe) equals the registered 61315bf6... (kernel-e207.json): always;
  2. its whole ELF equals the registered aace138c..., OR its LOADABLE IDENTITY equals the pinned one (LOAD_PIN, below): every byte and
     header the card's loader can read and nothing else - the ELF header's class, data, ident version, OS/ABI and ABI version bytes, type,
     machine, e_version, flags and entry point; every program header's type, flags, addresses, sizes and alignment (its file offset is
     layout, left out) and every PT_LOAD segment's bytes; every SHF_ALLOC section (name, type, flags, address, size, alignment, entry size,
     its bytes unless NOBITS); and the symbol table (name, value, size, info, other, its section's name). elf_identity() is check_e191.py's
     second form, line for line (E206's). LOAD_PIN is the identity of the registered ELF aace138c... itself (E206's pin; desk/
     desktest_build_e207.sh re-makes the ELF on this desk and shows it at the pin and its identity at LOAD_PIN).
The files: E207's box files (the runner, its two modules, the wrapper, the guard, the build, this check, the preflight, the doubles; the
registration's plan and points, which the runner and the doubles read), MM1-v1's frozen blind-day forecasts (the smoke's check reads its
counter-mean forecast; the doubles read its seconds and watts), the device-command checker v2 and its table, the three tile manifests the common
self-check reads, every tile a point names (10), and rgm136's ten sources. RB_DESKTEST=1 lets E207_OBJCOPY stand in (the desk tests only).
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import os
import struct
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
HARNESS = os.path.join(HERE, "harness-e207.json")
E = "tools/claims-v3/e207/"
R = "tools/claims-v3/e136/rgm136/"
SRC = [R + f for f in ("CMakeLists.txt", "README.md", "sparsity_args.h", "host/CMakeLists.txt", "host/Constants.h.in", "host/main.cpp",
                       "kernel/CMakeLists.txt", "kernel/crt.S", "kernel/sections.ld", "kernel/sparsity.c")]
sys.path.insert(0, HERE)
import e207_common as C  # noqa: E402

FILES = [E + f for f in ("run_e207.py", "e207_common.py", "e207_ident.py", "session_e207.sh", "build_e207.sh", "check_e207.py",
                         "preflight_e207.sh", "ettelem_guard_e207.sh", "fake_card_e207.py", "plan-e207.json", "points-e207.json")] + [
    C.MM1_REL, "tools/claims-v3/dmcmd_audit_v2.py", "tools/claims-v3/dmcmd_table_v2.json"] + list(C.TILE_MANIFESTS) + sorted(C.TILES) + SRC
KERNEL_PIN = C.KERNEL_PIN
TEXT_PIN = C.TEXT_PIN
LOAD_PIN = "649d40793e459e51db9a590ca90dd1363da3a00398f98938c3ef6e190514e2b7"   # the loadable identity of the registered ELF aace138c... (E206's pin: a real desk build, Mon 16 Nov 2026 12:17 PST; re-made by desk/desktest_build_e207.sh)


def sha(p):
    with open(os.path.join(REPO, p), "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def elf_identity(path):
    """The ELF's LOADABLE IDENTITY (the module docstring) as a dict, or (None, why). check_e191.py's elf_identity, second form."""
    try:
        b = open(path, "rb").read()
    except OSError as e:
        return None, f"cannot read the ELF ({type(e).__name__})"
    if len(b) < 64 or b[:4] != b"\x7fELF":
        return None, "not an ELF file"
    if b[4] != 2 or b[5] != 1:
        return None, f"not a little-endian ELF64 (class {b[4]}, data {b[5]})"
    try:
        (e_type, e_machine, e_version, e_entry, e_phoff, e_shoff, e_flags, e_ehsize, e_phentsize, e_phnum, e_shentsize, e_shnum,
         e_shstrndx) = struct.unpack_from("<HHIQQQIHHHHHH", b, 16)
        phs = [struct.unpack_from("<IIQQQQQQ", b, e_phoff + i * e_phentsize) for i in range(e_phnum)]
        shs = [struct.unpack_from("<IIQQQQIIQQ", b, e_shoff + i * e_shentsize) for i in range(e_shnum)]
        names = shs[e_shstrndx] if e_shnum and e_shstrndx < e_shnum else None

        def cstr(tab_off, tab_size, off):
            if off >= tab_size:
                return "?"
            return b[tab_off + off:tab_off + tab_size].split(b"\0", 1)[0].decode("utf-8", "replace")

        def sname(i):
            return cstr(names[4], names[5], shs[i][0]) if names else str(i)

        def h(off, size):
            if off + size > len(b):
                raise ValueError("a part reaches past the file's end")
            return hashlib.sha256(b[off:off + size]).hexdigest()
        segs = [{"vaddr": p[3], "paddr": p[4], "filesz": p[5], "memsz": p[6], "flags": p[1], "align": p[7], "sha256": h(p[2], p[5])}
                for p in phs if p[0] == 1]
        phdrs = [{"type": p[0], "flags": p[1], "vaddr": p[3], "paddr": p[4], "filesz": p[5], "memsz": p[6], "align": p[7]} for p in phs]
        secs = [{"name": sname(i), "type": s[1], "flags": s[2], "addr": s[3], "size": s[5], "align": s[8], "entsize": s[9],
                 "sha256": None if s[1] == 8 else h(s[4], s[5])}
                for i, s in enumerate(shs) if s[2] & 0x2]
        syms = []
        for i, s in enumerate(shs):
            if s[1] != 2:
                continue
            strtab = shs[s[6]] if s[6] < e_shnum else None
            ent = s[9] or 24
            for k in range(s[5] // ent):
                st_name, st_info, st_other, st_shndx, st_value, st_size = struct.unpack_from("<IBBHQQ", b, s[4] + k * ent)
                nm = cstr(strtab[4], strtab[5], st_name) if strtab else str(st_name)
                sec = sname(st_shndx) if 0 < st_shndx < e_shnum else {0: "UNDEF", 0xfff1: "ABS", 0xfff2: "COMMON"}.get(st_shndx, str(st_shndx))
                syms.append([nm, st_value, st_size, st_info, st_other, sec])
        syms.sort()
    except (struct.error, ValueError, IndexError) as e:
        return None, f"the ELF's headers cannot be read ({e})"
    ident = {"what": "the ELF's loadable identity, second form (check_e191.py THE KERNEL GATE; fix-e191k2)", "class": 64,
             "data": "little-endian", "ei_version": b[6], "osabi": b[7], "abiversion": b[8], "type": e_type, "machine": e_machine,
             "version": e_version, "flags": e_flags, "entry": e_entry, "program_headers": phdrs, "load_segments": segs,
             "alloc_sections": secs, "symbols_n": len(syms),
             "symbols_sha256": hashlib.sha256(json.dumps(syms, separators=(",", ":")).encode()).hexdigest()}
    return ident, ""


def identity_sha(ident):
    return hashlib.sha256(json.dumps(ident, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def text_sha(elf):
    """.text's bytes as `objcopy -O binary -j .text` writes them, sha256; None when objcopy fails or writes nothing."""
    oc = "/opt/et/bin/riscv64-unknown-elf-objcopy"
    if os.environ.get("RB_DESKTEST") == "1" and os.environ.get("E207_OBJCOPY"):
        oc = os.environ["E207_OBJCOPY"]
    elif not os.path.exists(oc):
        oc = "objcopy"
    try:
        r = subprocess.run([oc, "-O", "binary", "-j", ".text", elf, "/dev/stdout"], capture_output=True)
    except OSError:
        return None
    return hashlib.sha256(r.stdout).hexdigest() if r.returncode == 0 and r.stdout else None


def kernel_gate(elf):
    """THE KERNEL GATE on one built kernel: (ok, words). .text the registered one always; then the registered ELF, or the pinned identity."""
    if not os.path.isfile(elf):
        return False, f"no kernel at {elf}"
    t = text_sha(elf)
    e = hashlib.sha256(open(elf, "rb").read()).hexdigest()
    if t != TEXT_PIN:
        return False, f".text sha256 {t} is not the registered {TEXT_PIN} (kernel-e207.json); ELF {e}"
    if e == KERNEL_PIN:
        return True, f".text {t[:16]}... the registered; ELF {e[:16]}... the registered (E136's build record)"
    ident, why = elf_identity(elf)
    if ident is None:
        return False, f".text the registered, the ELF {e} not the registered, and its loadable identity cannot be read: {why}"
    li = identity_sha(ident)
    if li != LOAD_PIN:
        return False, f".text the registered, but the ELF {e} is not the registered and its loadable identity {li} is not the pinned {LOAD_PIN}"
    return True, (f".text {t[:16]}... the registered; ELF {e[:16]}... not the registered (the difference lies in sections the card never "
                  f"loads); its loadable identity {li[:16]}... the pinned one")


def make():
    return {"what": "E207's harness: every file the box runs or reads, at its sha256 (check_e207.py)", "files": {p: sha(p) for p in FILES}}


def main(argv):
    if argv[:1] == ["--make"]:
        with open(HARNESS, "w") as f:
            json.dump(make(), f, indent=1, sort_keys=True)
            f.write("\n")
        print(f"wrote harness-e207.json ({len(FILES)} files)")
        return 0
    if argv[:1] == ["--list"]:
        print("\n".join(FILES))
        return 0
    if argv[:1] == ["--kernel"] and len(argv) == 2:
        good, words = kernel_gate(argv[1])
        print(f"KERNEL {'OK' if good else 'FAILED'}: {words}")
        return 0 if good else 1
    if argv[:1] == ["--identity"] and len(argv) == 2:
        ident, why = elf_identity(argv[1])
        if ident is None:
            print(f"IDENTITY UNREADABLE: {why}")
            return 1
        print(json.dumps(ident, indent=1, sort_keys=True))
        print(f"IDENTITY {identity_sha(ident)}")
        return 0
    if argv[:1] == ["--check"]:
        H = json.load(open(HARNESS))
        m = make()
        bad = sorted(set(m["files"]) ^ set(H["files"])) + [p for p in m["files"] if H["files"].get(p) != m["files"][p]]
        print(f"harness-e207.json re-made: {'equal' if not bad else 'DIFFERS'} ({len(FILES)} files)")
        print("CHECK PASS" if not bad else "CHECK FAIL: " + ", ".join(bad[:10]))
        return 0 if not bad else 1
    if argv[:1] == ["--box"]:
        H = json.load(open(HARNESS))["files"]
        want = {p: v for p, v in H.items() if ("--only-src" not in argv or p.startswith(R))}
        bad = []
        for p, v in sorted(want.items()):
            got = sha(p) if os.path.isfile(os.path.join(REPO, p)) else "missing"
            if got != v:
                bad.append(f"{p}: {got[:16]} (want {v[:16]})")
        if bad:
            print("HARNESS DIFFERS: " + "; ".join(bad[:10]))
            return 9
        print(f"HARNESS OK: {len(want)} files at harness-e207.json's sha256" + (" (rgm136's sources)" if "--only-src" in argv else ""))
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
