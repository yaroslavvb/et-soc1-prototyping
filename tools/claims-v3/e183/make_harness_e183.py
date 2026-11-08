#!/usr/bin/env python3
"""E183 (Q155, the kit): harness-e183.json, the sha256 of every file the box session runs, sources, builds from or reads, of the train
host's build inputs, and of the build tree the box makes from them (E180's make_harness_e180_v2.py and E182's harness, ported).

    /usr/bin/python3 -B tools/claims-v3/e183/make_harness_e183.py           # writes harness-e183.json beside this file
    /usr/bin/python3 -B tools/claims-v3/e183/make_harness_e183.py --check   # re-makes it in memory and compares: CHECK PASS or exit 1

  files         the box's files: lib.sh, D1's rule (others_d1_e180.sh), E128's guard, dmcmd_audit.py and its table, E180's generator and its
                appended text, E180's five images E183 reuses, the 37 committed files of workloads/enercat, E183's registration (every
                file its list names, and the list), and the kit's ten box files. s07 syncs exactly these and this file.
  build_inputs  what the train host is built from: the 37 workloads/enercat files, gen_acc_e180.py, acc-modes-e180.inc and
                patch_host_e183.py (check_inputs_e183.py).
  build_tree    every file of the tree build_host_e183.sh makes on the box, made here the same way in a scratch root: a stage of the 37,
                gen_acc_e180.py --src build/e183-enercat-stage --dst build/enercat-e183-src (the same relative words, since the
                generator's marker records its --src), then patch_host_e183.py; relative to the tree.
  patched_main_sha256  patch_host_e183.py's OUT_SHA256.
It refuses unless workloads/enercat's 37 files are committed and clean (git), so the pins are the committed bytes. Standard library only.
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
REL = "tools/claims-v3/e183"
KIT_BOX = ["e183_common.py", "patch_host_e183.py", "check_inputs_e183.py", "build_host_e183.sh", "run_e183.py", "block_e183.sh",
           "queue_e183.sh", "session_e183.sh", "check_e183.py", "preflight_e183.sh"]
SHARED = ["tools/claims-v3/lib.sh", "tools/claims-v3/e180/others_d1_e180.sh", "tools/claims-v3/e128/ettelem_guard.sh",
          "tools/claims-v3/dmcmd_audit.py", "tools/claims-v3/dmcmd_table.json", "tools/claims-v3/e180/gen_acc_e180.py",
          "tools/claims-v3/e180/acc-modes-e180.inc"] + [f"tools/claims-v3/e180/images/{n}.bin" for n in ("f_0p5", "f_1p5", "f_2", "f_4", "f_5")]
GEN, INC = "tools/claims-v3/e180/gen_acc_e180.py", "tools/claims-v3/e180/acc-modes-e180.inc"


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def git(*a):
    return subprocess.run(["git", "-C", TOP] + list(a), capture_output=True, text=True, check=True).stdout


def enercat_files():
    fs = [l for l in git("ls-files", "workloads/enercat").splitlines() if l]
    dirty = git("status", "--porcelain", "--untracked-files=no", "--", "workloads/enercat").strip()
    if dirty:
        raise SystemExit("workloads/enercat has uncommitted changes: refusing\n" + dirty)
    return fs


def registration():
    out = [f"{REL}/SHA256SUMS-e183-registration"]
    for line in open(os.path.join(HERE, "SHA256SUMS-e183-registration")):
        parts = line.split()
        if len(parts) == 2:
            out.append(parts[1])
    return out


def build_tree(enercat):
    sys.path.insert(0, HERE)
    import patch_host_e183 as PH   # noqa: E402
    root = tempfile.mkdtemp(prefix="harness-e183-")
    try:
        stage = os.path.join(root, "build", "e183-enercat-stage")
        for rel in enercat:
            dst = os.path.join(stage, rel[len("workloads/enercat/"):])
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(os.path.join(TOP, rel), dst)
        subprocess.run([sys.executable, "-B", os.path.join(TOP, GEN), "--src", "build/e183-enercat-stage", "--dst",
                        "build/enercat-e183-src"], cwd=root, check=True, capture_output=True, text=True)
        tree = os.path.join(root, "build", "enercat-e183-src")
        mp = os.path.join(tree, "host", "main.cpp")
        s = open(mp, "rb").read()
        if sha_bytes(s) != PH.SRC_SHA256:
            raise SystemExit("the generated tree's main.cpp is not the committed one")
        patched = PH.patch_text(s.decode())
        if sha_bytes(patched.encode()) != PH.OUT_SHA256:
            raise SystemExit("the patch's output is not its pinned OUT_SHA256")
        open(mp, "w").write(patched)
        out = {}
        for d, _dirs, files in os.walk(tree):
            for f in sorted(files):
                p = os.path.join(d, f)
                out[os.path.relpath(p, tree)] = sha(p)
        return dict(sorted(out.items())), PH.OUT_SHA256
    finally:
        shutil.rmtree(root, ignore_errors=True)


def sha_bytes(b):
    return hashlib.sha256(b).hexdigest()


def build():
    enercat = enercat_files()
    files = sorted(set(SHARED + enercat + registration() + [f"{REL}/{f}" for f in KIT_BOX]))
    inputs = sorted(enercat + [GEN, INC, f"{REL}/patch_host_e183.py"])
    tree, out_sha = build_tree(enercat)
    return {"what": "E183's harness (make_harness_e183.py): the box's files, the train host's build inputs, and the build tree the box "
                    "makes from them, each at its sha256",
            "files": {f: sha(os.path.join(TOP, f)) for f in files},
            "build_inputs": {f: sha(os.path.join(TOP, f)) for f in inputs},
            "build_tree": tree, "patched_main_sha256": out_sha,
            "counts": {"files": len(files), "build_inputs": len(inputs), "build_tree": len(tree), "workloads_enercat": len(enercat)}}


def main():
    js = json.dumps(build(), indent=1, sort_keys=True) + "\n"
    dst = os.path.join(HERE, "harness-e183.json")
    if sys.argv[1:] == ["--check"]:
        ok = os.path.exists(dst) and open(dst).read() == js
        print("CHECK PASS" if ok else "CHECK FAIL")
        sys.exit(0 if ok else 1)
    open(dst, "w").write(js)
    c = json.loads(js)["counts"]
    print(f"wrote {dst}: {c['files']} files, {c['build_inputs']} build inputs, a build tree of {c['build_tree']} files")


if __name__ == "__main__":
    main()
