#!/usr/bin/env python3
"""E189's harness (Q167, the kit, Thu 12 Nov 2026, before any E189 datum): the sha256 of every file the box runs or reads, and its check.

    python3 -B tools/claims-v3/e189/check_e189.py --make        # writes harness-e189.json (the desk, from the lab clone)
    python3 -B tools/claims-v3/e189/check_e189.py --check       # re-makes it in memory and compares: CHECK PASS
    python3 -B tools/claims-v3/e189/check_e189.py --box [--built ledger,spp]
                    # on the box's tree (or the desk's): every file at its sha256 (HARNESS OK: <n> files); with --built, the kernels
                    # built today at their pins too (the ELF and its .text, as BUILD-INFO and kernel.sha256 record them)
    python3 -B tools/claims-v3/e189/check_e189.py --list        # the paths, one a line (step 5's sync list)
The files: E189's box files; E128's guard; the device-command checker and its table; the two programs' build inputs (workloads/ledger at
46a16bd0, workloads/sparseparity's host and kernel as the 29 Sep card runs built them) and energy_stub.py (the box's dry pass); the
registration's plan; the SHA-256 digests --expect reads (the day's and the smoke's); sparse parity's committed --dry line (the host check).
RB_DESKTEST=1 lets E189_OBJCOPY and E189_KERNEL_PINS stand in (the runbook's desk test only). Python's own modules only.
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
HARNESS = os.path.join(HERE, "harness-e189.json")
E = "tools/claims-v3/e189/"
FILES = [E + f for f in ("run_e189.py", "e189_common.py", "session_e189.sh", "build_e189.sh", "hostcheck_e189.py",
                         "hostcheck-e189.json", "plan-e189.json", "preflight_e189.sh", "fake_card_e189.py", "check_e189.py",
                         "forecast-e189.json")] + [
    "tools/claims-v3/e128/ettelem_guard.sh", "tools/claims-v3/dmcmd_audit.py", "tools/claims-v3/dmcmd_table.json",
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


def sha(p):
    return hashlib.sha256(open(os.path.join(REPO, p), "rb").read()).hexdigest()


def make():
    return {"what": "E189's harness: every file the box runs or reads, at its sha256 (check_e189.py)", "files": {p: sha(p) for p in FILES}}


def text_sha(elf):
    """.text's bytes as `objcopy -O binary -j .text` writes them (the recipe of BUILD-INFO and kernel.sha256), sha256."""
    oc = "/opt/et/bin/riscv64-unknown-elf-objcopy"
    if os.environ.get("RB_DESKTEST") == "1" and os.environ.get("E189_OBJCOPY"):
        oc = os.environ["E189_OBJCOPY"]            # the runbook's desk test only
    elif not os.path.exists(oc):
        oc = "objcopy"
    r = subprocess.run([oc, "-O", "binary", "-j", ".text", elf, "/dev/stdout"], capture_output=True, timeout=60)
    return hashlib.sha256(r.stdout).hexdigest() if r.returncode == 0 and r.stdout else None


def main(argv):
    if argv[:1] == ["--make"]:
        with open(HARNESS, "w") as f:
            json.dump(make(), f, indent=1, sort_keys=True)
            f.write("\n")
        print(f"wrote harness-e189.json ({len(FILES)} files)")
        return 0
    if argv[:1] == ["--list"]:
        print("\n".join(FILES))
        return 0
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
            jp = os.path.join(HERE, "hostcheck-e189.json")
            if os.environ.get("RB_DESKTEST") == "1" and os.environ.get("E189_KERNEL_PINS"):
                jp = os.environ["E189_KERNEL_PINS"]       # the runbook's desk test's stand-in kernels only
            J = json.load(open(jp))
            built = argv[argv.index("--built") + 1].split(",")
            for prog, elf in (("ledger", "build/e189ledger/kernel/ledger.elf"), ("spp", "build/e189spp/kernel/sparseparity.elf")):
                if prog not in built:
                    continue
                n += 2
                if not os.path.exists(os.path.join(REPO, elf)):
                    bad.append(f"{elf} missing")
                    continue
                if sha(elf) != J["kernels"][prog]["elf_sha256"]:
                    bad.append(f"{elf} ELF differs")
                if text_sha(os.path.join(REPO, elf)) != J["kernels"][prog]["text_sha256"]:
                    bad.append(f"{elf} .text differs")
        if bad:
            print("HARNESS FAIL: " + "; ".join(bad))
            return 1
        print(f"HARNESS OK: {n} files")
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
