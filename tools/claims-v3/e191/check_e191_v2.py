#!/usr/bin/env python3
"""E191's harness, v2 (KIT.md.dated-note-2.md, Q184, Sun 15 Nov 2026, PST: after E189's data commit fa9098c4 of Sat 14 Nov 2026, 20:34:12
PST, and after E191's first session stopped at its smoke gate (1a4bc1e3), before any E191 pass datum): check_e191.py (eb1ac923, unchanged
beside it) with kit note 2's box files added to the files the box runs or reads. The v2 list is v1's 42 files, v1's own harness-e191.json
(so v1's check still reads OK on the box, as step 6's wait runs it), and the note's six box files: run_e191_v2.py, e191_common_v2.py,
session_e191_v2.sh, fake_card_e191_v2.py (step 8 v2's dry pass), preflight_e191_v2.sh and this file. THE KERNEL GATE, the identity and
PLANS SAME are v1's, by call.

    python3 -B tools/claims-v3/e191/check_e191_v2.py --make      # writes harness-e191-v2.json (the desk, from the lab clone)
    python3 -B tools/claims-v3/e191/check_e191_v2.py --check     # re-makes it in memory and compares: CHECK PASS
    python3 -B tools/claims-v3/e191/check_e191_v2.py --box [--built ledger,spp]
                    # every file of the v2 list at its sha256 (HARNESS-V2 OK: <n> files); with --built, the kernels through v1's gate
    python3 -B tools/claims-v3/e191/check_e191_v2.py --list      # the paths, one a line (step 5 v2's sync list)
    python3 -B tools/claims-v3/e191/check_e191_v2.py --kernel|--identity|--plans ...      # v1's, unchanged
Python's own modules only. SPDX-License-Identifier: Apache-2.0
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import check_e191 as V1  # noqa: E402

HARNESS2 = os.path.join(HERE, "harness-e191-v2.json")
E = "tools/claims-v3/e191/"
NEW = [E + f for f in ("run_e191_v2.py", "e191_common_v2.py", "session_e191_v2.sh", "fake_card_e191_v2.py", "preflight_e191_v2.sh",
                       "check_e191_v2.py")]
FILES = list(V1.FILES) + [E + "harness-e191.json"] + NEW


def make():
    return {"what": "E191's harness v2 (kit note 2): every file the box runs or reads, at its sha256 (check_e191_v2.py)",
            "files": {p: V1.sha(p) for p in FILES}}


def main(argv):
    if argv[:1] == ["--make"]:
        with open(HARNESS2, "w") as f:
            json.dump(make(), f, indent=1, sort_keys=True)
            f.write("\n")
        print(f"wrote harness-e191-v2.json ({len(FILES)} files)")
        return 0
    if argv[:1] == ["--list"]:
        print("\n".join(FILES))
        return 0
    if argv[:1] in (["--kernel"], ["--identity"], ["--plans"]):
        return V1.main(argv)
    H = json.load(open(HARNESS2))
    if argv[:1] == ["--check"]:
        m = make()
        bad = sorted(set(m["files"]) ^ set(H["files"])) + [p for p in m["files"] if H["files"].get(p) != m["files"][p]]
        print("CHECK PASS (v2)" if not bad else "CHECK FAIL (v2): " + ", ".join(bad))
        return 0 if not bad else 1
    if argv[:1] == ["--box"]:
        bad = []
        for p, h in sorted(H["files"].items()):
            if not os.path.exists(os.path.join(V1.REPO, p)):
                bad.append(f"{p} missing")
            elif V1.sha(p) != h:
                bad.append(f"{p} differs")
        n = len(H["files"])
        if "--built" in argv:
            built = argv[argv.index("--built") + 1].split(",")
            for prog, elf in V1.KERNELS:
                if prog not in built:
                    continue
                n += 2
                if not os.path.exists(os.path.join(V1.REPO, elf)):
                    bad.append(f"{elf} missing")
                    continue
                good, words = V1.kernel_gate(prog, os.path.join(V1.REPO, elf))
                if not good:
                    bad.append(f"{elf}: the kernel gate: {words}")
        if bad:
            print("HARNESS-V2 FAIL: " + "; ".join(bad))
            return 1
        print(f"HARNESS-V2 OK: {n} files")
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
