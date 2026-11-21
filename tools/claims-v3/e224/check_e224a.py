#!/usr/bin/env python3
"""E224's harness and THE KERNEL GATE, ARM A (Q237, lane kit-e224, Fri 20 Nov 2026, before any E224 datum): the sha256 of every file arm A's
box (aifoundry1, its tree ~/nekko) runs or reads, and its check; E218's harness (tools/claims-v3/e218/check_e218.py, landed in 5582edfc) for E224
arm A's files, its two builds and its one box. Python's own modules only.

    python3 -B tools/claims-v3/e224/check_e224a.py --make            writes harness-e224a.json (the desk, from the lab clone)
    python3 -B tools/claims-v3/e224/check_e224a.py --check           re-makes it in memory and compares: CHECK PASS
    python3 -B tools/claims-v3/e224/check_e224a.py --box [--only-src]
                    on the box's tree (or the desk's): every file at its sha256 (HARNESS OK: <n> files); --only-src the twenty sources of the
                    two builds only (build_e224a.sh's first check)
    python3 -B tools/claims-v3/e224/check_e224a.py --list            the paths, one a line (step 5's sync list)
    python3 -B tools/claims-v3/e224/check_e224a.py --kernel rgm136|rgm211 <elf> [--whole]
                    THE KERNEL GATE on one built ELF: KERNEL OK: ... or KERNEL FAILED: <why>; rgm136 by the kit's identity gate
                    (ident_e224a.gate for 'rgm136 gemmL'), rgm211 by the build's tree gate (ident_e224a.tree_gate: that ELF runs no E224 point); --whole
                    requires the whole ELF at its pin (arm A's build and box check on aifoundry1 always pass it: E215 arm B's form)
    python3 -B tools/claims-v3/e224/check_e224a.py --identity <elf>  the ELF's whole, .text and loadable-identity sha256 (JSON)

THE KERNEL GATE (kernel-e224.json; E224.md section 2): rgm136's built ELF through the kit's identity gate: its .text sha256 (objcopy -O binary
-j .text, E206's recipe) equals the pin 61315bf6..., AND (on aifoundry1, --whole) its whole ELF equals the pin aace138c... (E136's build record;
aifoundry1's riscv gcc prints "() 15.1.0", as this desk's); rgm211's built ELF (the tree its host comes from) at kernel-e224.json's rgm211_host
pins (the whole ELF 00402801...). The runner gates EVERY PROCESS by its point's family with the identity gate at the whole ELF
(run_e224a.gate_of): rgm136's ELF for both families.
The files: E224 arm A's box files (the runner, its two modules, the wrapper, the guard, the build, this check, the preflight, the doubles, the
gate ident_e224a.py), the registration's files the runner, the gate and the doubles read (plan, points, the kernel record and the frozen forecast
CSV and JSON), the kit's timeout table (desk/timeouts-e224.json), the two E206 files the gate imports (check_e206.py at its pinned sha256, and
e206_common.py, which it imports), the device-command checker v2 and its table, the tiles' three manifests (kinds.json, E212's and E217's
src/SRC-SHA256SUMS), the seventeen tiles the points name (randn, zeros, ones and family P's eight patterns), and the two builds' twenty sources.
RB_DESKTEST=1 lets E206_OBJCOPY stand in for objcopy inside the gate (the desk tests only).
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
HARNESS = os.path.join(HERE, "harness-e224a.json")
E = "tools/claims-v3/e224/"
NAMES = ("CMakeLists.txt", "README.md", "sparsity_args.h", "host/CMakeLists.txt", "host/Constants.h.in", "host/main.cpp",
         "kernel/CMakeLists.txt", "kernel/crt.S", "kernel/sections.ld", "kernel/sparsity.c")
sys.path.insert(0, HERE)
import e224a_common as C  # noqa: E402

SRC = [C.KERNELS[k]["src"] + "/" + f for k in ("rgm136", "rgm211") for f in NAMES]
FILES = [E + f for f in ("run_e224a.py", "e224a_common.py", "e224a_ident.py", "session_e224a.sh", "build_e224a.sh", "check_e224a.py",
                         "preflight_e224a.sh", "ettelem_guard_e224a.sh", "fake_card_e224a.py", "ident_e224a.py", "plan-e224.json", "points-e224.json",
                         "kernel-e224.json", "desk/timeouts-e224.json")] + [
    C.FC[0], C.FCJ[0], "tools/claims-v3/e206/check_e206.py", "tools/claims-v3/e206/e206_common.py",
    "tools/claims-v3/dmcmd_audit_v2.py", "tools/claims-v3/dmcmd_table_v2.json"] + sorted({m for _, m, _, _ in C.TILE_MANIFESTS}) + \
    sorted(C.TILES) + SRC


def sha(p):
    with open(os.path.join(REPO, p), "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def kernel_gate(kind, elf, whole=False):
    """THE KERNEL GATE on one built ELF: (ok, words): rgm136's by the kit's identity gate for 'rgm136 gemmL' (the ELF both families run);
    rgm211's by the build's tree gate."""
    if kind not in C.KERNELS:
        return False, f"no kernel {kind!r} (rgm136, rgm211)"
    import ident_e224a as IG     # imported here: it pins E206's check_e206.py by sha256 and stops on a difference (the --box check reads that file first)
    if kind == "rgm136":
        good, words = IG.gate("rgm136 gemmL", elf, whole=whole)
    else:
        good, words = IG.tree_gate("rgm211", elf)
        if good and whole and IG.identity(elf)["elf_sha256"] != IG.kernels()["rgm211_host"]["elf_sha256"]:
            good, words = False, words + "; but --whole requires the whole ELF at its pin"
    return good, f"{kind}: {words}"


def make():
    return {"what": "E224's harness: every file the box runs or reads, at its sha256 (check_e224a.py)", "files": {p: sha(p) for p in FILES}}


def main(argv):
    if argv[:1] == ["--make"]:
        with open(HARNESS, "w") as f:
            json.dump(make(), f, indent=1, sort_keys=True)
            f.write("\n")
        print(f"wrote harness-e224a.json ({len(FILES)} files)")
        return 0
    if argv[:1] == ["--list"]:
        print("\n".join(FILES))
        return 0
    if argv[:1] == ["--kernel"] and len(argv) in (3, 4) and (len(argv) == 3 or argv[3] == "--whole"):
        good, words = kernel_gate(argv[1], argv[2], whole=len(argv) == 4)
        print(f"KERNEL {'OK' if good else 'FAILED'}: {words}")
        return 0 if good else 1
    if argv[:1] == ["--identity"] and len(argv) == 2:
        import ident_e224a as IG
        print(json.dumps(IG.identity(argv[1]), indent=1, sort_keys=True))
        return 0
    if argv[:1] == ["--check"]:
        H = json.load(open(HARNESS))
        m = make()
        bad = sorted(set(m["files"]) ^ set(H["files"])) + [p for p in m["files"] if H["files"].get(p) != m["files"][p]]
        print(f"harness-e224a.json re-made: {'equal' if not bad else 'DIFFERS'} ({len(FILES)} files)")
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
        print(f"HARNESS OK: {len(want)} files at harness-e224a.json's sha256" + (" (the two builds' sources)" if "--only-src" in argv else ""))
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
