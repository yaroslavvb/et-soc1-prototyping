#!/usr/bin/env python3
"""E202's harness (Q193, lane kit-e202, Mon 16 Nov 2026, before any E202 datum): the sha256 of every file the box runs or reads, and its
check (E189's check_e189.py form).

    python3 -B tools/claims-v3/e202/check_e202.py --make        # writes harness-e202.json (the desk, from the lab clone)
    python3 -B tools/claims-v3/e202/check_e202.py --check       # re-makes it in memory and compares: CHECK PASS
    python3 -B tools/claims-v3/e202/check_e202.py --box [--built]
                    # on the box's tree (or the desk's): every file at its sha256 (HARNESS OK: <n> files); with --built, the kernel
                    # built today too: its .text at E202.md's pin (ace7bcb0...), and the host and ELF at today's build record's sha256
    python3 -B tools/claims-v3/e202/check_e202.py --list        # the paths, one a line (step 5's sync list)
The files: E202's box files (the runner, its common module and doubles, the wrapper, the build, the files and the host check, the
preflight, this file); the registration's plan (and plan_e202.py, whose r_rule the runner calls), forecast (the doubles' seconds and
watts) and the trained weights' durable home; E128's guard; the device-command checker v2 and its table; the program's build inputs
and its model and data recipe (workloads/mnistmlp, as landed with E202's program commit); energy_stub.py (the box's dry pass).
Python's own modules only. SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
HARNESS = os.path.join(HERE, "harness-e202.json")
E = "tools/claims-v3/e202/"
M = "workloads/mnistmlp/"
FILES = [E + f for f in ("run_e202.py", "e202_common.py", "session_e202.sh", "build_e202.sh", "files_e202.sh", "hostcheck_e202.py",
                         "preflight_e202.sh", "fake_card_e202.py", "check_e202.py", "plan-e202.json", "plan_e202.py",
                         "forecast-e202.json", "weights/mnist-int8-trained.mlpw.gz")] + [
    "tools/claims-v3/e128/ettelem_guard.sh", "tools/claims-v3/dmcmd_audit_v2.py", "tools/claims-v3/dmcmd_table_v2.json",
    "workloads/sparseparity/tools/energy_stub.py"] + [M + f for f in (
        "CMakeLists.txt", "mnistmlp_args.h", "host/CMakeLists.txt", "host/Constants.h.in", "host/main.cpp", "kernel/CMakeLists.txt",
        "kernel/crt.S", "kernel/mnistmlp.c", "kernel/sections.ld", "model/fetch_mnist.sh", "model/mnist_model.py",
        "model/MNIST-SHA256SUMS", "model/PINS-SHA256SUMS")]
TEXT_PIN = "ace7bcb04536329f1d75135446049c442b9f4b65f726083f7623b959b279d82d"


def sha(p):
    h = hashlib.sha256()
    with open(os.path.join(REPO, p), "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def make():
    return {"what": "E202's harness: every file the box runs or reads, at its sha256 (check_e202.py)", "files": {p: sha(p) for p in FILES}}


def text_sha(elf):
    """.text's bytes as `objcopy -O binary -j .text` writes them (BUILD-INFO's recipe), sha256."""
    oc = "/opt/et/bin/riscv64-unknown-elf-objcopy"
    if not os.path.exists(oc):
        oc = "objcopy"
    r = subprocess.run([oc, "-O", "binary", "-j", ".text", elf, "/dev/stdout"], capture_output=True, timeout=60)
    return hashlib.sha256(r.stdout).hexdigest() if r.returncode == 0 and r.stdout else None


def main(argv):
    if argv[:1] == ["--make"]:
        with open(HARNESS, "w") as f:
            json.dump(make(), f, indent=1, sort_keys=True)
            f.write("\n")
        print(f"wrote harness-e202.json ({len(FILES)} files)")
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
            n += 3
            rp = "build/e202mnist/BUILD-E202.json"
            try:
                rec = json.load(open(os.path.join(REPO, rp)))
            except (OSError, ValueError):
                rec = {}
                bad.append(f"{rp} missing")
            elf, host = "build/e202mnist/kernel/mnistmlp.elf", "build/e202mnist/host/mnistmlp_host"
            for p, key in ((elf, "elf_sha256"), (host, "host_sha256")):
                if not os.path.exists(os.path.join(REPO, p)):
                    bad.append(f"{p} missing")
                elif sha(p) != rec.get(key):
                    bad.append(f"{p} differs from {rp}")
            if os.path.exists(os.path.join(REPO, elf)) and text_sha(os.path.join(REPO, elf)) != TEXT_PIN:
                bad.append(f"{elf} .text is not E202.md's pin")
        if bad:
            print("HARNESS FAIL: " + "; ".join(bad))
            return 1
        print(f"HARNESS OK: {n} files")
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
