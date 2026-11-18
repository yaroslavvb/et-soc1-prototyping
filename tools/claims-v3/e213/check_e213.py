#!/usr/bin/env python3
"""E213's harness and THE KERNEL GATE (Q216, lane kit-e213, Tue 17 Nov 2026, before any E213 datum): the sha256 of every file a box (aifoundry3
~/aifoundry, arm A; aifoundry1 ~/nekko, arm B) runs or reads, and its check; E211's harness (tools/claims-v3/e211/check_e211.py, landed in
2b7f261f) for E213's files, its two kernels and its two boxes. Python's own modules only.

    python3 -B tools/claims-v3/e213/check_e213.py --make            writes harness-e213.json (the desk, from the lab clone)
    python3 -B tools/claims-v3/e213/check_e213.py --check           re-makes it in memory and compares: CHECK PASS
    python3 -B tools/claims-v3/e213/check_e213.py --box [--only-src]
                    on a box's tree (or the desk's): every file at its sha256 (HARNESS OK: <n> files); --only-src the twenty sources of the
                    two kernels only (build_e213.sh's first check)
    python3 -B tools/claims-v3/e213/check_e213.py --list            the paths, one a line (step 5's sync list)
    python3 -B tools/claims-v3/e213/check_e213.py --kernel rgm136|rgm211 <elf> [--whole]
                    THE KERNEL GATE on one built ELF: KERNEL OK: ... or KERNEL FAILED: <why>; --whole requires the whole ELF at its pin (arm B's
                    rgm136, E213.md 2)
    python3 -B tools/claims-v3/e213/check_e213.py --identity <elf>  the ELF's whole, .text and loadable-identity sha256 (JSON)

THE KERNEL GATE (kernel-e213.json; E213.md section 2): each built kernel through the kit's identity gate, ident_e213.gate, for a family that
kernel's ELF serves (rgm136: 'rgm136 gemmL'; rgm211: 'rgm211 gemmLn'; the gate reads only the ELF's pins, so the family names the ELF): its .text
sha256 (objcopy -O binary -j .text, E206's recipe) equals the kernel's pin (rgm136 61315bf6..., rgm211 82c79807...), AND its whole ELF equals the
pin (rgm136 aace138c..., E136's build record; rgm211 00402801..., E211's desk build) OR its LOADABLE IDENTITY (check_e206.elf_identity) equals the
pin (rgm136 649d4079..., rgm211 1351a569...); with --whole the whole ELF only. aifoundry3's riscv gcc prints "(g1b306039a) 15.1.0" into .comment,
so arm A's builds pass by the loadable identity (E211's build there: rgm136 ELF ff2723b8..., rgm211 70c066e8...); aifoundry1's prints "() 15.1.0"
(E206 arm B's rgm136 build there reached aace138c...). The runner gates EVERY PROCESS by its point's family with the same gate (run_e213.gate_of).
The files: E213's box files (the runner, its two modules, the wrapper, the guard, the build, this check, the preflight, the doubles, the gate
ident_e213.py), the registration's files the runner, the gate and the doubles read (plan, points, the kernel record, arm B's frozen MM1-v3
forecast, and arm A's from MM1-v3's land), the two E206 files the gate imports (check_e206.py at its pinned sha256, and e206_common.py, which it
imports), the device-command checker v2 and its table, the tile manifest, the eight tiles the points name, and the two kernels' twenty sources.
RB_DESKTEST=1 lets E206_OBJCOPY stand in for objcopy inside the gate (the desk tests only).
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
HARNESS = os.path.join(HERE, "harness-e213.json")
E = "tools/claims-v3/e213/"
NAMES = ("CMakeLists.txt", "README.md", "sparsity_args.h", "host/CMakeLists.txt", "host/Constants.h.in", "host/main.cpp",
         "kernel/CMakeLists.txt", "kernel/crt.S", "kernel/sections.ld", "kernel/sparsity.c")
sys.path.insert(0, HERE)
import e213_common as C  # noqa: E402

SRC = [C.KERNELS[k]["src"] + "/" + f for k in ("rgm136", "rgm211") for f in NAMES]
FILES = [E + f for f in ("run_e213.py", "e213_common.py", "e213_ident.py", "session_e213.sh", "build_e213.sh", "check_e213.py",
                         "preflight_e213.sh", "ettelem_guard_e213.sh", "fake_card_e213.py", "ident_e213.py", "plan-e213.json", "points-e213.json",
                         "kernel-e213.json", "forecast-e213b-v3.csv")] + [
    C.FC["A"][0], "tools/claims-v3/e206/check_e206.py", "tools/claims-v3/e206/e206_common.py",
    "tools/claims-v3/dmcmd_audit_v2.py", "tools/claims-v3/dmcmd_table_v2.json", C.TILE_MANIFEST] + sorted(C.TILES) + SRC
GATE_FAMILY = {"rgm136": "rgm136 gemmL", "rgm211": "rgm211 gemmLn"}


def sha(p):
    with open(os.path.join(REPO, p), "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def kernel_gate(kind, elf, whole=False):
    """THE KERNEL GATE on one built kernel: (ok, words), by the kit's gate for a family that kernel's ELF serves."""
    if kind not in C.KERNELS:
        return False, f"no kernel {kind!r} (rgm136, rgm211)"
    import ident_e213 as IG     # imported here: it pins E206's check_e206.py by sha256 and stops on a difference (the --box check reads that file first)
    good, words = IG.gate(GATE_FAMILY[kind], elf, whole=whole)
    return good, f"{kind}: {words}"


def make():
    return {"what": "E213's harness: every file a box runs or reads, at its sha256 (check_e213.py)", "files": {p: sha(p) for p in FILES}}


def main(argv):
    if argv[:1] == ["--make"]:
        with open(HARNESS, "w") as f:
            json.dump(make(), f, indent=1, sort_keys=True)
            f.write("\n")
        print(f"wrote harness-e213.json ({len(FILES)} files)")
        return 0
    if argv[:1] == ["--list"]:
        print("\n".join(FILES))
        return 0
    if argv[:1] == ["--kernel"] and len(argv) in (3, 4) and (len(argv) == 3 or argv[3] == "--whole"):
        good, words = kernel_gate(argv[1], argv[2], whole=len(argv) == 4)
        print(f"KERNEL {'OK' if good else 'FAILED'}: {words}")
        return 0 if good else 1
    if argv[:1] == ["--identity"] and len(argv) == 2:
        import ident_e213 as IG
        print(json.dumps(IG.identity(argv[1]), indent=1, sort_keys=True))
        return 0
    if argv[:1] == ["--check"]:
        H = json.load(open(HARNESS))
        m = make()
        bad = sorted(set(m["files"]) ^ set(H["files"])) + [p for p in m["files"] if H["files"].get(p) != m["files"][p]]
        print(f"harness-e213.json re-made: {'equal' if not bad else 'DIFFERS'} ({len(FILES)} files)")
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
        print(f"HARNESS OK: {len(want)} files at harness-e213.json's sha256" + (" (the two kernels' sources)" if "--only-src" in argv else ""))
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
