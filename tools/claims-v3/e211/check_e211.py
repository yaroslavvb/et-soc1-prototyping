#!/usr/bin/env python3
"""E211's harness and THE KERNEL GATE (Q204, lane kit-e211, Tue 17 Nov 2026, before any E211 datum): the sha256 of every file the box
(aifoundry3 ~/aifoundry) runs or reads, and its check; E206's harness (tools/claims-v3/e206/check_e206.py, landed in 906699ea) as E207's kit
ported it (Q199), for E211's files and its two kernels. Python's own modules only.

    python3 -B tools/claims-v3/e211/check_e211.py --make            writes harness-e211.json (the desk, from the lab clone)
    python3 -B tools/claims-v3/e211/check_e211.py --check           re-makes it in memory and compares: CHECK PASS
    python3 -B tools/claims-v3/e211/check_e211.py --box [--only-src]
                    on the box's tree (or the desk's): every file at its sha256 (HARNESS OK: <n> files); --only-src the twenty sources of the
                    two kernels only (build_e211.sh's first check)
    python3 -B tools/claims-v3/e211/check_e211.py --list            the paths, one a line (step 5's sync list)
    python3 -B tools/claims-v3/e211/check_e211.py --kernel rgm136|rgm211 <elf>
                    THE KERNEL GATE on one built ELF: KERNEL OK: ... or KERNEL FAILED: <why>
    python3 -B tools/claims-v3/e211/check_e211.py --identity <elf>  the ELF's whole, .text and loadable-identity sha256 (JSON)

THE KERNEL GATE (kernel-e211.json; E211.md section 2): each built kernel through the registration's own identity gate, ident_e211.gate, for the
arm family that kernel serves alone (rgm136: gemmL; rgm211: gemmLn): its .text sha256 (objcopy -O binary -j .text, E206's recipe) equals the
kernel's pin (rgm136 61315bf6..., rgm211 82c79807...), AND its whole ELF equals the desk build's (rgm136 aace138c..., E136's build record;
rgm211 00402801..., the registration's desk build) OR its LOADABLE IDENTITY (check_e206.elf_identity, check_e191.py's second form: every byte
and header the card's loader can read and nothing else) equals the pin (rgm136 649d4079..., E206's LOAD_PIN; rgm211 1351a569...). aifoundry3's
riscv gcc prints "(g1b306039a) 15.1.0" where aifoundry2's prints "() 15.1.0", and the string lands in .comment, a section the card never
loads: aifoundry3's builds pass by the loadable identity (this lane's build there, Tue 17 Nov 2026 00:25 PST: rgm136 ELF ff2723b8..., rgm211
ELF 70c066e8..., both identities the pins; logs/a3-build-e211.txt). The runner gates EVERY PROCESS by its point's arm family with the same
gate (run_e211.gate_of).
The files: E211's box files (the runner, its two modules, the wrapper, the guard, the build, this check, the preflight, the doubles), the
registration's files the runner, the gate and the doubles read (plan, points, forecast, the kernel record, the gate ident_e211.py), the two
E206 files the gate imports (check_e206.py at its pinned sha256, and e206_common.py, which it imports), the device-command checker v2 and its
table, the tile manifest, the two tiles the points name, and the two kernels' twenty sources. RB_DESKTEST=1 lets E206_OBJCOPY stand in for
objcopy inside the gate (the desk tests only).
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
HARNESS = os.path.join(HERE, "harness-e211.json")
E = "tools/claims-v3/e211/"
NAMES = ("CMakeLists.txt", "README.md", "sparsity_args.h", "host/CMakeLists.txt", "host/Constants.h.in", "host/main.cpp",
         "kernel/CMakeLists.txt", "kernel/crt.S", "kernel/sections.ld", "kernel/sparsity.c")
sys.path.insert(0, HERE)
import e211_common as C  # noqa: E402

SRC = [C.KERNELS[k]["src"] + "/" + f for k in ("rgm136", "rgm211") for f in NAMES]
FILES = [E + f for f in ("run_e211.py", "e211_common.py", "e211_ident.py", "session_e211.sh", "build_e211.sh", "check_e211.py",
                         "preflight_e211.sh", "ettelem_guard_e211.sh", "fake_card_e211.py", "plan-e211.json", "points-e211.json",
                         "forecast-e211.json", "kernel-e211.json", "ident_e211.py")] + [
    "tools/claims-v3/e206/check_e206.py", "tools/claims-v3/e206/e206_common.py",
    "tools/claims-v3/dmcmd_audit_v2.py", "tools/claims-v3/dmcmd_table_v2.json", C.TILE_MANIFEST] + sorted(C.TILES) + SRC


def sha(p):
    with open(os.path.join(REPO, p), "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def kernel_gate(kind, elf):
    """THE KERNEL GATE on one built kernel: (ok, words), by the registration's gate for the family that kernel serves alone."""
    if kind not in C.KERNELS:
        return False, f"no kernel {kind!r} (rgm136, rgm211)"
    import ident_e211 as IG     # imported here: it pins E206's check_e206.py by sha256 and stops on a difference (the --box check reads that file first)
    good, words = IG.gate(C.KERNELS[kind]["family"], elf)
    return good, f"{kind}: {words}"


def make():
    return {"what": "E211's harness: every file the box runs or reads, at its sha256 (check_e211.py)", "files": {p: sha(p) for p in FILES}}


def main(argv):
    if argv[:1] == ["--make"]:
        with open(HARNESS, "w") as f:
            json.dump(make(), f, indent=1, sort_keys=True)
            f.write("\n")
        print(f"wrote harness-e211.json ({len(FILES)} files)")
        return 0
    if argv[:1] == ["--list"]:
        print("\n".join(FILES))
        return 0
    if argv[:1] == ["--kernel"] and len(argv) == 3:
        good, words = kernel_gate(argv[1], argv[2])
        print(f"KERNEL {'OK' if good else 'FAILED'}: {words}")
        return 0 if good else 1
    if argv[:1] == ["--identity"] and len(argv) == 2:
        import ident_e211 as IG
        print(json.dumps(IG.identity(argv[1]), indent=1, sort_keys=True))
        return 0
    if argv[:1] == ["--check"]:
        H = json.load(open(HARNESS))
        m = make()
        bad = sorted(set(m["files"]) ^ set(H["files"])) + [p for p in m["files"] if H["files"].get(p) != m["files"][p]]
        print(f"harness-e211.json re-made: {'equal' if not bad else 'DIFFERS'} ({len(FILES)} files)")
        print("CHECK PASS" if not bad else "CHECK FAIL: " + ", ".join(bad[:10]))
        return 0 if not bad else 1
    if argv[:1] == ["--box"]:
        H = json.load(open(HARNESS))["files"]
        want = {p: v for p, v in H.items() if ("--only-src" not in argv or p in SRC)}
        bad = []
        for p, v in sorted(want.items()):
            got = sha(p) if os.path.isfile(os.path.join(REPO, p)) else "missing"
            if got != v:
                bad.append(f"{p}: {got[:16]} (want {v[:16]})")
        if bad:
            print("HARNESS DIFFERS: " + "; ".join(bad[:10]))
            return 9
        print(f"HARNESS OK: {len(want)} files at harness-e211.json's sha256" + (" (the two kernels' sources)" if "--only-src" in argv else ""))
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
