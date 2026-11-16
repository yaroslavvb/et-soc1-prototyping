#!/usr/bin/env python3
"""E194's harness (Q183, the kit, Sun 15 Nov 2026, after E194's registration 0d8e3de0 and before any E194 datum): the sha256 of every file
the box (aifoundry2, the box tree ~/claude/et-soc1-prototyping) runs or reads, and its check, with THE KERNEL GATE. E191's harness
(tools/claims-v3/e191/check_e191.py, eb1ac923, unchanged beside it) with E194's files; THE KERNEL GATE, its loadable identity (second form)
and its pins are E191's, unchanged: the "() 15.1.0" toolchain's pins were made on THIS box (aifoundry2, Sat 14 Nov 2026), which builds
E194's kernels (desk/realbuild_e194.sh shows the gate on this box's real build).

    python3 -B tools/claims-v3/e194/check_e194.py --make        # writes harness-e194.json (the desk, from the lab clone)
    python3 -B tools/claims-v3/e194/check_e194.py --check       # re-makes it in memory and compares: CHECK PASS
    python3 -B tools/claims-v3/e194/check_e194.py --box [--built ledger,spp]
                    # on the box's tree (or the desk's): every file at its sha256 (HARNESS OK: <n> files); with --built, the kernels
                    # built today through THE KERNEL GATE too (its .text and its identity, two checks a kernel)
    python3 -B tools/claims-v3/e194/check_e194.py --kernel ledger|spp <elf>      # THE KERNEL GATE on one ELF (build_e194.sh calls it):
                    # KERNEL OK <prog>: ... or KERNEL FAILED <prog>: <why>
    python3 -B tools/claims-v3/e194/check_e194.py --identity <elf>              # the ELF's loadable identity (JSON) and its sha256
    python3 -B tools/claims-v3/e194/check_e194.py --list        # the paths, one a line (step 5 reads them in the box tree)
    python3 -B tools/claims-v3/e194/check_e194.py --plans       # E194's six configurations equal E189's (args, reps flag, K): PLANS SAME
THE KERNEL GATE (E191's fix-e191k and fix-e191k2, unchanged): for each kernel, (1) its .text sha256 (objcopy -O binary -j .text, the
registered recipe) equals E189.md 4's registered .text (hostcheck-e189.json's text_sha256), always required; and (2) its whole ELF equals
one of its pinned ELFs (E189's, aifoundry3's toolchain; or the "() 15.1.0" toolchain's, ELF_ALSO, built on aifoundry2), OR its LOADABLE
IDENTITY (the ELF header's fields, every program header, every PT_LOAD segment's bytes, every SHF_ALLOC section with its bytes, the symbol
table) equals the pinned one (LOAD_SHA256): a toolchain that differs only in .comment or debug sections passes, any loadable byte or header
differing fails. The files: E194's box files (the runner, its modules, the wrapper, the guard, the build and its ET_DEVICES reading, the
preflight, the doubles, the registered plan and forecast the doubles read); E189's host check, its frozen lines and E189's plan (the host
check reads it; E194's configurations equal E189's), unchanged; the device-command checker and its table; the two programs' build inputs;
energy_stub.py (the box's dry pass); the SHA-256 digests --expect reads; sparse parity's committed --dry line. RB_DESKTEST=1 lets
E194_OBJCOPY and E194_KERNEL_PINS stand in (the desk tests only). Python's own modules only. SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import os
import struct
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
HARNESS = os.path.join(HERE, "harness-e194.json")
E = "tools/claims-v3/e194/"
FILES = [E + f for f in ("run_e194.py", "e194_common.py", "e194_ident.py", "session_e194.sh", "build_e194.sh", "etdevices_e194.sh",
                         "ettelem_guard_e194.sh", "preflight_e194.sh", "fake_card_e194.py", "check_e194.py", "plan-e194.json",
                         "forecast-e194.json")] + [
    "tools/claims-v3/e189/hostcheck_e189.py", "tools/claims-v3/e189/hostcheck-e189.json", "tools/claims-v3/e189/plan-e189.json",
    "tools/claims-v3/dmcmd_audit.py", "tools/claims-v3/dmcmd_table.json",
    "workloads/ledger/CMakeLists.txt", "workloads/ledger/ledger_args.h", "workloads/ledger/host/CMakeLists.txt",
    "workloads/ledger/host/Constants.h.in", "workloads/ledger/host/main.cpp", "workloads/ledger/kernel/CMakeLists.txt",
    "workloads/ledger/kernel/crt.S", "workloads/ledger/kernel/ledger.c", "workloads/ledger/kernel/sections.ld",
    "workloads/sparseparity/CMakeLists.txt", "workloads/sparseparity/sparseparity_args.h", "workloads/sparseparity/cpu/sp.h",
    "workloads/sparseparity/host/CMakeLists.txt", "workloads/sparseparity/host/Constants.h.in",
    "workloads/sparseparity/host/main.cpp", "workloads/sparseparity/host/spp_common.h",
    "workloads/sparseparity/host/spp_selftest.cpp", "workloads/sparseparity/kernel/CMakeLists.txt",
    "workloads/sparseparity/kernel/crt.S", "workloads/sparseparity/kernel/sections.ld",
    "workloads/sparseparity/kernel/sparseparity.c", "workloads/sparseparity/tools/energy_stub.py",
    "docs/reports/data/2026-11-12-q166-progs/digests/expect-card-b2048-r800.txt",
    "docs/reports/data/2026-11-12-q166-progs/digests/expect-b2048-r1-2048.txt",
    "docs/reports/data/2026-11-12-q166-progs/runs/p2-dry/new-dry.json"]
KERNELS = (("ledger", "build/e194ledger/kernel/ledger.elf"), ("spp", "build/e194spp/kernel/sparseparity.elf"))
# THE KERNEL GATE's own pins (the module docstring), made on aifoundry2 on Sat 14 Nov 2026 with riscv64-unknown-elf-gcc "() 15.1.0" (as
# aifoundry1's reads) from the lab's sources at E191's kit (workloads/ledger, workloads/sparseparity), the same bytes from two source paths
ELF_ALSO = {"ledger": "2b2eb281c45408ea7a43307e65bd68ec0470c662752f0d474cd58579076db65a",
            "spp": "6ee70c925ef377f27b3941600be72b848206804633ee56c95550e96782f78814"}
# the loadable identity's second form (fix-e191k2, Sun 15 Nov 2026: every program header, e_ident[6..8], e_version, the entry sizes) of
# those same ELFs, re-made from a real build on aifoundry2 (the first form's pins were 8c6e42df... and c3632ecc...)
LOAD_SHA256 = {"ledger": "2ef2747f3c0fc65c0d808de4e690e7655cf1d7bb1b93dac5fc9dc006d2b0010b",
               "spp": "2dd06a909660cf53fa4c9b5b870bc003b373c202b8a3601a2de3ede1021536d9"}
TOOLCHAINS = {"elf_e189": "E189's pin (aifoundry3's riscv gcc '(g1b306039a) 15.1.0')",
              "elf_also": "the '() 15.1.0' toolchain's pin (built on aifoundry2, Sat 14 Nov 2026)"}


def sha(p):
    return hashlib.sha256(open(os.path.join(REPO, p), "rb").read()).hexdigest()


def elf_identity(path):
    """The ELF's LOADABLE IDENTITY (the module docstring) as a dict, or (None, why) when the file is not a little-endian ELF64 this reads.
    Python's own struct module only (aifoundry1's system python3)."""
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
                for p in phs if p[0] == 1]                                   # PT_LOAD
        phdrs = [{"type": p[0], "flags": p[1], "vaddr": p[3], "paddr": p[4], "filesz": p[5], "memsz": p[6], "align": p[7]}
                 for p in phs]                                               # fix-e191k2: EVERY program header, in order (no offset)
        secs = [{"name": sname(i), "type": s[1], "flags": s[2], "addr": s[3], "size": s[5], "align": s[8], "entsize": s[9],
                 "sha256": None if s[1] == 8 else h(s[4], s[5])}           # SHT_NOBITS holds no bytes
                for i, s in enumerate(shs) if s[2] & 0x2]                    # SHF_ALLOC
        syms = []
        for i, s in enumerate(shs):
            if s[1] != 2:                                                    # SHT_SYMTAB
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


def kernel_pins(prog):
    """The gate's pins for one program: (registered .text, [pinned whole ELFs with their names], pinned loadable identity or None). From
    E189's hostcheck-e189.json (unchanged) and this file's ELF_ALSO / LOAD_SHA256; with RB_DESKTEST=1, E194_KERNEL_PINS (the desk tests'
    stand-in kernels: their elf_sha256 a string or a list, load_sha256 optional) stands in for both."""
    if os.environ.get("RB_DESKTEST") == "1" and os.environ.get("E194_KERNEL_PINS"):
        k = json.load(open(os.environ["E194_KERNEL_PINS"]))["kernels"][prog]
        elfs = k["elf_sha256"] if isinstance(k["elf_sha256"], list) else [k["elf_sha256"]]
        return k["text_sha256"], [(e, "a desk-test stand-in pin") for e in elfs], k.get("load_sha256")
    k = json.load(open(os.path.join(REPO, "tools/claims-v3/e189/hostcheck-e189.json")))["kernels"][prog]
    return k["text_sha256"], [(k["elf_sha256"], TOOLCHAINS["elf_e189"]), (ELF_ALSO[prog], TOOLCHAINS["elf_also"])], LOAD_SHA256[prog]


def kernel_gate(prog, elf):
    """THE KERNEL GATE on one built kernel: (ok, words). .text the registered one always; then a pinned whole ELF, or the pinned identity."""
    if not os.path.isfile(elf):
        return False, f"no kernel at {elf}"
    text_pin, elfs, load_pin = kernel_pins(prog)
    t = text_sha(elf)
    e = hashlib.sha256(open(elf, "rb").read()).hexdigest()
    if t != text_pin:
        return False, f".text sha256 {t} is not the registered {text_pin} (E189.md 4); ELF {e}"
    named = [n for (p, n) in elfs if p == e]
    if named:
        return True, f".text {t[:16]}... the registered (E189.md 4); ELF {e[:16]}... {named[0]}"
    if not load_pin:
        return False, f".text the registered, but the ELF {e} is none of the pinned ({', '.join(p[:16] + '...' for p, _ in elfs)}) and no loadable identity is pinned"
    ident, why = elf_identity(elf)
    if ident is None:
        return False, f".text the registered, the ELF {e} none of the pinned, and its loadable identity cannot be read: {why}"
    li = identity_sha(ident)
    if li != load_pin:
        return False, f".text the registered, but the ELF {e} is none of the pinned and its loadable identity {li} is not the pinned {load_pin}"
    return True, (f".text {t[:16]}... the registered (E189.md 4); ELF {e[:16]}... none of the pinned (the difference lies in sections the card "
                  f"never loads); its loadable identity {li[:16]}... the pinned one")


def make():
    return {"what": "E194's harness: every file the box runs or reads, at its sha256 (check_e194.py)", "files": {p: sha(p) for p in FILES}}


def text_sha(elf):
    """.text's bytes as `objcopy -O binary -j .text` writes them (the recipe of BUILD-INFO and kernel.sha256), sha256."""
    oc = "/opt/et/bin/riscv64-unknown-elf-objcopy"
    if os.environ.get("RB_DESKTEST") == "1" and os.environ.get("E194_OBJCOPY"):
        oc = os.environ["E194_OBJCOPY"]
    elif not os.path.exists(oc):
        oc = "objcopy"
    r = subprocess.run([oc, "-O", "binary", "-j", ".text", elf, "/dev/stdout"], capture_output=True, timeout=60)
    return hashlib.sha256(r.stdout).hexdigest() if r.returncode == 0 and r.stdout else None


def main(argv):
    if argv[:1] == ["--make"]:
        with open(HARNESS, "w") as f:
            json.dump(make(), f, indent=1, sort_keys=True)
            f.write("\n")
        print(f"wrote harness-e194.json ({len(FILES)} files)")
        return 0
    if argv[:1] == ["--list"]:
        print("\n".join(FILES))
        return 0
    if argv[:1] == ["--kernel"] and len(argv) == 3 and argv[1] in ("ledger", "spp"):
        good, words = kernel_gate(argv[1], argv[2])
        print(f"KERNEL {'OK' if good else 'FAILED'} {argv[1]}: {words}")
        return 0 if good else 1
    if argv[:1] == ["--identity"] and len(argv) == 2:
        ident, why = elf_identity(argv[1])
        if ident is None:
            print(f"IDENTITY UNREADABLE: {why}")
            return 1
        print(json.dumps(ident, indent=1, sort_keys=True))
        print(f"IDENTITY {identity_sha(ident)}")
        return 0
    if argv[:1] == ["--plans"]:
        # E194.md 4: the six configurations' host arguments and K equal E189's, so E189's host check (its frozen --dry lines, its plan)
        # reads E194's hosts unchanged
        a = json.load(open(os.path.join(REPO, "tools/claims-v3/e189/plan-e189.json")))["configs"]
        b = json.load(open(os.path.join(HERE, "plan-e194.json")))["configs"]
        keys = ("args", "reps_flag", "launches_K")
        diff = sorted(set(a) ^ set(b)) + [f"{c}.{k}" for c in sorted(set(a) & set(b)) for k in keys if a[c].get(k) != b[c].get(k)]
        print(f"PLANS SAME: the six configurations' {', '.join(keys)} in plan-e194.json equal plan-e189.json's" if not diff
              else "PLANS DIFFER: " + ", ".join(diff))
        return 0 if not diff else 1
    H = json.load(open(HARNESS))
    if argv[:1] == ["--check"]:
        m = make()
        bad = sorted(set(m["files"]) ^ set(H["files"])) + [p for p in m["files"] if H["files"].get(p) != m["files"][p]]
        print("CHECK PASS" if not bad else "CHECK FAIL: " + ", ".join(bad))
        return 0 if not bad else 1
    if argv[:1] == ["--box"]:
        bad = []
        for p, h in sorted(H["files"].items()):
            if not os.path.exists(os.path.join(REPO, p)):
                bad.append(f"{p} missing")
            elif sha(p) != h:
                bad.append(f"{p} differs")
        n = len(H["files"])
        if "--built" in argv:
            built = argv[argv.index("--built") + 1].split(",")
            for prog, elf in KERNELS:
                if prog not in built:
                    continue
                n += 2                                  # THE KERNEL GATE: its .text, and its pinned ELF or pinned identity
                if not os.path.exists(os.path.join(REPO, elf)):
                    bad.append(f"{elf} missing")
                    continue
                good, words = kernel_gate(prog, os.path.join(REPO, elf))
                if not good:
                    bad.append(f"{elf}: the kernel gate: {words}")
        if bad:
            print("HARNESS FAIL: " + "; ".join(bad))
            return 1
        print(f"HARNESS OK: {n} files")
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
