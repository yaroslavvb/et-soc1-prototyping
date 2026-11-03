#!/usr/bin/env python3
"""Q139(q), corrections after verification (Tue 3 Nov 2026, C8): E159's frozen scorer, run with a hash check first, and its self-test without
writing into the tree. The frozen files are not edited: e159_g3.py, g3_model.py and predictions-e159.json keep their bytes at 91def7c4, and this
wrapper calls e159_g3.score unchanged.

    python3 score_e159.py check                              every file the scorer reads equals its bytes at 91def7c4 (frozen-sha256.json); exit 2 if not
    python3 score_e159.py selftest                           e159_g3's self-test on E146's session, with the relabelled predictions in a temp dir
    python3 score_e159.py score <E159 session dir> [out]     check, then e159_g3.score(<dir>, [out]) unchanged
    python3 score_e159.py manifest                           rebuild frozen-sha256.json from git (the files the scorer opens, at 91def7c4)

Use these, never `e159_g3.py selftest`: the frozen self-test rewrites predictions-e159.json in place and restores it in a `finally`, so an
interrupted run would leave F6's levels in H1's cells. Its result is the same: this self-test prints what selftest-e159.txt holds.

g3_model.py's module docstring gives leakage 0.442 W per C and a 65.9 C trip. Those are Q138(t)'s constants, which the module keeps as K_LEAK and
T_TRIP for the registered arm "G3 at Q138(t)'s constants". G3's own frozen constants are K_LEAK_G3 = 0.1 W per C and TRIP_G3 = 65.5 C (the
comment above them in the module says so), and they are what e159_g3.py scores G3 with. The docstring is left as frozen.
"""
import builtins
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
FREEZE = "91def7c45dfcda08b8180a37e73a941a80fe417a"
MANIFEST = os.path.join(HERE, "frozen-sha256.json")
SESSION146 = "docs/reports/data/2026-11-02-e146-gemm-stores/aifoundry2/s1"
ALWAYS = ("e159_g3.py", "g3_model.py", "predictions-e159.json", "predictions-e159.txt")


def lab_root():
    return os.environ.get("LAB") or os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


def check(quiet=False):
    man = json.load(open(MANIFEST))
    lab = lab_root()
    bad = []
    for rel, want in sorted(man["files"].items()):
        p = os.path.join(lab, rel)
        got = sha(p) if os.path.exists(p) else "missing"
        if got != want:
            bad.append((rel, want[:16], got[:16]))
    if bad:
        print(f"CHECK FAILED: {len(bad)} of {len(man['files'])} files differ from {man['commit'][:8]}:")
        for b in bad:
            print(f"   {b[0]}: frozen {b[1]}..., now {b[2]}...")
        sys.exit(2)
    if not quiet:
        print(f"CHECK OK: all {len(man['files'])} files the E159 scorer reads equal their bytes at {man['commit'][:8]}")
    return True


def _selftest_run(E):
    """e159_g3.selftest's steps, with the relabelled predictions file in the temp dir instead of over the frozen one"""
    lab = E.LAB
    src = os.path.join(lab, SESSION146)
    P = json.load(open(os.path.join(E.HERE, "predictions-e159.json")))
    P146 = json.load(open(os.path.join(lab, "tools/claims-v3/e146/predictions-e146.json")))
    tmp = tempfile.mkdtemp(prefix="e159-selftest-", dir=os.environ.get("TMPDIR"))
    sess = os.path.join(tmp, "session")
    os.mkdir(sess)
    here0 = E.HERE
    try:
        os.symlink(os.path.join(src, "tel"), os.path.join(sess, "tel"))
        os.symlink(os.path.join(src, "launches.jsonl.gz"), os.path.join(sess, "launches.jsonl.gz"))
        rel = {"F6-fp32-randn": "H1-fp32-randn", "F6-int8-full": "H1-int8-full"}
        with open(os.path.join(sess, "runs.jsonl"), "w") as f:
            for x in open(os.path.join(src, "runs.jsonl")):
                r = json.loads(x)
                if r.get("processes", 1) > 1:
                    r["label"] = rel.get(r["label"], r["label"])
                f.write(json.dumps(r) + "\n")
        for a, b in rel.items():
            P["cells"][b]["P0_w"] = P146["cells"][a]["P0_w"]
        json.dump(P, open(os.path.join(tmp, "predictions-e159.json"), "w"))
        E.HERE = tmp  # score() reads predictions-e159.json from e159_g3.HERE at call time
        res = E.score(sess)
        print("SELFTEST (E146's F6 holds through the E159 scorer, F6's own P0 levels):", json.dumps(res["verdict_G3"]))
        return res
    finally:
        E.HERE = here0
        shutil.rmtree(tmp)


def manifest():
    """record every lab file the scorer opens on import and in the self-test, plus its frozen outputs, and hash each at FREEZE from git"""
    lab = lab_root()
    opened = set()
    real_open = builtins.open

    def rec(file, *a, **k):
        try:
            opened.add(os.path.realpath(os.fspath(file)))
        except TypeError:
            pass
        return real_open(file, *a, **k)

    builtins.open = rec
    try:
        sys.path.insert(0, HERE)
        import e159_g3 as E
        _selftest_run(E)
    finally:
        builtins.open = real_open
    mods = {os.path.realpath(m.__file__) for m in list(sys.modules.values()) if getattr(m, "__file__", None)}
    labr = os.path.realpath(lab) + os.sep
    skip = (os.path.join(os.path.realpath(lab), SESSION146) + os.sep, os.path.realpath(tempfile.gettempdir()) + os.sep,
            os.path.realpath(os.environ.get("TMPDIR") or tempfile.gettempdir()) + os.sep)
    rels = set(os.path.join(os.path.relpath(HERE, lab), f) for f in ALWAYS)
    me = os.path.realpath(os.path.abspath(__file__))  # this wrapper (loaded as __main__) is not part of the freeze
    for p in opened | mods:
        if p.startswith(labr) and not p.startswith(skip) and "__pycache__" not in p and p != me and not p.endswith(os.sep + "frozen-sha256.json"):
            rels.add(os.path.relpath(p, lab))
    files = {}
    for rel in sorted(rels):
        blob = subprocess.run(["git", "-C", lab, "show", f"{FREEZE}:{rel}"], capture_output=True, check=True).stdout
        files[rel] = hashlib.sha256(blob).hexdigest()
    out = {"what": "sha256 of every lab file E159's scorer (e159_g3.py score) imports or opens, and of its frozen outputs, at the freeze commit; "
                   "score_e159.py check compares the working files with these", "commit": FREEZE, "files": files}
    json.dump(out, open(MANIFEST, "w"), indent=1)
    print(f"wrote {os.path.basename(MANIFEST)}: {len(files)} files at {FREEZE[:8]}")
    for rel, h in files.items():
        print(f"   {h[:16]}  {rel}")


def main():
    if len(sys.argv) >= 2 and sys.argv[1] == "check":
        check()
    elif len(sys.argv) >= 2 and sys.argv[1] == "selftest":
        check()
        sys.path.insert(0, HERE)
        import e159_g3 as E
        _selftest_run(E)
        check()
    elif len(sys.argv) >= 3 and sys.argv[1] == "score":
        check()
        sys.path.insert(0, HERE)
        import e159_g3 as E
        E.score(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
    elif len(sys.argv) >= 2 and sys.argv[1] == "manifest":
        manifest()
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
