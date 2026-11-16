#!/usr/bin/env python3
"""E198's harness after dated amendment A1 (Q196, lane a1-e198, Mon 16 Nov 2026, before any E198 datum): every file aifoundry1 runs or
reads for E198 from E198's root, at its sha256. It is harness_e198.py (kit-e198, Q191; unchanged beside it, with harness-e198.json) with
the box files A1 changes: the lab's runner copy run_x04_e198a1.py (E198.md.dated-amendment-A1.md), session_e198a1.sh, build_e198a1.sh,
check_e198a1.py (with check_e198.py, which it imports), preflight_e198a1.sh and this file, in place of session_e198.sh, build_e198.sh,
check_e198.py's lone use, preflight_e198.sh and harness_e198.py; its JSON is harness-e198-a1.json; everything else is harness_e198.py's.
    python3 -I -B harness_e198a1.py --list               the sync list, one repository path a line (harness-e198-a1.json last)
    python3 -I -B harness_e198a1.py --make               write harness-e198-a1.json from the files as they are (the kit's own step)
    python3 -I -B harness_e198a1.py --check              harness-e198-a1.json re-made in memory equals the committed one: CHECK PASS
    python3 -I -B harness_e198a1.py --box [--root DIR]   every file of harness-e198-a1.json at its sha256 under DIR (default: the
                                                         repository's top), the three executables executable: HARNESS OK, or HARNESS FAIL
    python3 -I -B harness_e198a1.py --tree [--root DIR]  from the box's tree: its two files at the pins harness-e198-a1.json names: TREE OK
The files: E193's registration (every path SHA256SUMS-e193-registration names, and the list: E193.md, its proposal/ byte for byte (its
arms.tsv, host and kernel sources, reducer and runner; the runner is not run for E198 after A1), its desk/ with the registered dry listings
and the bodies check), E193's checker (check_e193.py: the smoke gate and the stop reason, unchanged), E198's box files as A1 leaves them,
E191's guard and identity module and ET_DEVICES reading (unchanged), and the device-command checker with its table.
The box root is <tree>/build/claims-v3/aifoundry1/e198 on aifoundry1 (~/nekko), where step 5's rsync -R puts each file at its repository
path. Two files run from the TREE, not the root, and are checked by the session itself at their sha256: the tree's own copy of E191's guard
(tools/claims-v3/e191/ettelem_guard_e191.sh, which the guard shim runs) and the box's reader build/ettelem/ettelem (8008f96f...).
Exit 0, 3 a failed check, 2 usage. SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
E = "tools/claims-v3/e198"
JSON = os.path.join(HERE, "harness-e198-a1.json")
REG_LIST = "tools/claims-v3/e193/SHA256SUMS-e193-registration"
EXECUTABLE = [E + "/ettelem_guard_e198.sh", E + "/holdercheck_e198.sh", E + "/x04host_e198.sh"]
KIT_BOX = [E + "/session_e198a1.sh", E + "/run_x04_e198a1.py", E + "/privdev_e198.sh", E + "/warden_e198.py", E + "/dropruntime_e198.py",
           E + "/ident_e198.py", E + "/ident_inner_e198.sh", E + "/check_e198.py", E + "/check_e198a1.py", E + "/build_e198a1.sh",
           E + "/preflight_e198a1.sh", E + "/harness_e198a1.py"] + EXECUTABLE
# Two files run from the box's TREE, not E198's root, each at its pin (the session checks them with --tree before any card command):
TREE_PINS = {"tools/claims-v3/e191/ettelem_guard_e191.sh": "6fd26f51129dec427674394a1b60315ca027bde18aa268ab0215d54608db2eb6",
             "build/ettelem/ettelem": "8008f96f056ae1c224c33ccce38070a67882a664620d637b8833d378b2167325"}
OTHERS = ["tools/claims-v3/e193/check_e193.py", "tools/claims-v3/e191/ettelem_guard_e191.sh", "tools/claims-v3/e191/e191_ident.py",
          "tools/claims-v3/e191/etdevices_e191.sh", "tools/claims-v3/dmcmd_audit.py", "tools/claims-v3/dmcmd_table.json"]


def sha(p):
    with open(p, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def paths():
    reg = []
    with open(os.path.join(REPO, REG_LIST)) as f:
        for ln in f:
            if ln.strip():
                reg.append(ln.rstrip("\n").split("  ", 1)[1])
    return sorted(set(reg + [REG_LIST] + KIT_BOX + OTHERS))


def made():
    ps = paths()
    return {"schema": "e198-harness-a1/1", "count": len(ps), "executable": sorted(EXECUTABLE),
            "files": {p: sha(os.path.join(REPO, p)) for p in ps}, "tree": dict(TREE_PINS)}


def main(argv):
    if argv == ["--list"]:
        for p in paths():
            print(p)
        print(E + "/harness-e198-a1.json")
        return 0
    if argv == ["--make"]:
        with open(JSON, "w") as f:
            json.dump(made(), f, indent=1, sort_keys=True)
            f.write("\n")
        print(f"harness-e198-a1.json written: {made()['count']} files")
        return 0
    if argv == ["--check"]:
        with open(JSON) as f:
            have = json.load(f)
        want = made()
        if have == want:
            print(f"CHECK PASS: harness-e198-a1.json re-made equals the committed one ({want['count']} files)")
            return 0
        diff = sorted(set(have.get("files", {}).items()) ^ set(want["files"].items()))
        print("CHECK FAIL: harness-e198-a1.json differs from the files as they are: " + ", ".join(p for p, _ in diff[:8]))
        return 3
    if argv[:1] == ["--tree"]:
        root = argv[argv.index("--root") + 1] if "--root" in argv else REPO
        with open(os.path.join(root, E, "harness-e198-a1.json")) as f:
            h = json.load(f)
        bad = [f"{p} reads {sha(p)[:16] if os.path.isfile(p) else 'nothing'}, not {want[:16]}" for p, want in sorted(h.get("tree", {}).items())
               if not (os.path.isfile(p) and sha(p) == want)]
        if bad or len(h.get("tree", {})) != len(TREE_PINS):
            print("TREE FAIL: " + "; ".join(bad))
            return 3
        print("TREE OK: " + ", ".join(f"{p} {w[:16]}" for p, w in sorted(h["tree"].items())) + " (the box's tree, at their pins)")
        return 0
    if argv[:1] == ["--box"]:
        root = argv[argv.index("--root") + 1] if "--root" in argv else REPO
        with open(os.path.join(root, E, "harness-e198-a1.json")) as f:
            h = json.load(f)
        bad = []
        for p, want in sorted(h["files"].items()):
            q = os.path.join(root, p)
            if not os.path.isfile(q):
                bad.append(f"missing {p}")
            elif sha(q) != want:
                bad.append(f"differs {p}")
        for p in h.get("executable", []):
            if os.path.isfile(os.path.join(root, p)) and not os.access(os.path.join(root, p), os.X_OK):
                bad.append(f"not executable {p}")
        if bad or len(h["files"]) != h.get("count"):
            print("HARNESS FAIL: " + ", ".join(bad[:10]) + (f" (and {len(bad) - 10} more)" if len(bad) > 10 else ""))
            return 3
        print(f"HARNESS OK: {len(h['files'])} files at their sha256 under the root, {len(h.get('executable', []))} executable")
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
