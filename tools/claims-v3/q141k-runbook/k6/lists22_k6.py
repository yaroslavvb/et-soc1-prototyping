#!/usr/bin/env python3
"""Q142(v2) fix pass, Thu 5 Nov 2026: every hash list the pool-8 card day rests on, checked at the go (step 3b, s03b_lists_k6.sh).

THE 22 LISTS are the readiness critic's set (critic-q142xk, Thu 5 Nov 2026, its work/lists_check.py, which read them at lab 1a76a870 and found
all 22 passing), ported here unchanged in what each reads: the 12 of the round before (blind7 91, blind6 80, frozen-sha256-e168.json 9 and
-scorer.txt 18, predict_q140e's FROZEN 26, M10's registration 174, M10 68 and SHA256SUMS-a2 10, POOL8-SHA256SUMS 209 and -62 62, the predictor's
SHA256SUMS 16 and -a2 9), then Q142(x)'s and (k)'s ten (the freeze's 160, the pool's 89, p8-600's SHA256SUMS 5 and SHA256SUMS-v2 4,
frozen-sha256-e173.json's 26 and -e174.json's 32 files, and the four kits' harness files, 97, 99, 135 and 110, their box binaries left out:
those live on the boxes and each kit's own harness check reads them there). The critic's fault 3: s03_desk_k6.sh covers 5 of them.
THIS PASS'S TWO: p8-600's SHA256SUMS-v3 (4: score_p8_600_v3.py, its self-test and the self-test's output) and the drivers list,
k6/SHA256SUMS-drivers-v3 (every runbook and kit file the card day's steps run at the desk, by path, after this pass).

FOR EACH LIST, at the revision (default HEAD) and in the work tree:
  1. the list file itself: its committed blob's sha256 is the one pinned below (the 22 as committed in their own creation commits, none
     changed since), and its work-tree copy is that blob;
  2. as many entries as registered;
  3. every entry: its committed blob at the revision and its work-tree file both have the listed sha256.
A list that is not there, a count that differs, a pin that differs or a file that differs is a FAIL.

    python3 -B tools/claims-v3/q141k-runbook/k6/lists22_k6.py [--repo <lab clone>] [--rev <rev>] [--worktree <dir>] [--json <out>]

It prints one PASS or FAIL line per list, then `LISTS22: <k> of 22 PASS`, `LISTS-V3: <k> of 2 PASS` and `ALL LISTS PASS` or `A LIST FAILS`.
Exit 0 when every list passes; 4 when one does not; 2 on a usage error. --worktree (default: the repo) reads the work-tree side from another
directory laid out like the repo (the desk test's). Standard library and git; it reads, and writes nothing but --json.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import ast
import hashlib
import json
import os
import re
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
G4 = "docs/reports/data/2026-11-04-q140q-gemm-g4-stride"
# (name, the list's path, how it is read, entries, the list file's own sha256)
#   kinds: rel = SHA256SUMS lines, paths relative to the list's directory; top = the same, relative to the repo's top; e168 = frozen-sha256-e168.json;
#   pyfrozen = predict_q140e.py's FROZEN dict; files = a frozen-sha256-e17N.json's "files"; harness = a harness-e17N.json's file maps
LISTS = [
    ("blind7/SHA256SUMS", "tools/claims-v3/kinds/blind7/SHA256SUMS", "rel", 91,
     "df8610eeece7703e0aecb3bff58e226bff45320e0c54ae29c504a4ef8ed48239"),
    ("blind6/SHA256SUMS", "tools/claims-v3/kinds/blind6/SHA256SUMS", "rel", 80,
     "8ab259209fc51ebb658dcfb1cb0fa62f33d1d6c27910c5a3867e2d12812cc509"),
    ("frozen-sha256-e168.json", f"{G4}/frozen-sha256-e168.json", "e168", 9,
     "6309746a6a126dc86bb4febde5f1bae635595194bdc67ff8e21378459136cf64"),
    ("frozen-sha256-e168-scorer.txt", f"{G4}/frozen-sha256-e168-scorer.txt", "rel", 18,
     "7f29e7998772aa8959335c7ac8307559534d40437c285fd7350a710944a96719"),
    ("predict_q140e FROZEN", "docs/reports/data/2026-11-04-q140e-heat-replicates/predict_q140e.py", "pyfrozen", 26,
     "79dbcfc3e835242cb56459c9917a6ea80b77de5deeb1c34c9edcb7ca8591620f"),
    ("M10 registration SHA256SUMS", "tools/claims-v3/m10/SHA256SUMS", "top", 174,
     "a3ef8786ded8c54ea73e17e08cdd5898b0f75a8d56e458088da871bcbfa531f5"),
    ("M10 data SHA256SUMS", "docs/reports/data/2026-11-04-q142m-m10/SHA256SUMS", "rel", 68,
     "89463de27354f68fed9fab56ec7bb8b5d962ede274f2fb8b0662d86fc34ef597"),
    ("M10 SHA256SUMS-a2", "docs/reports/data/2026-11-04-q142m-m10/SHA256SUMS-a2", "rel", 10,
     "0187d28e5d9c2a3992fc152c343d1a38f9b2c87a157abef6e40d1def5dc24c65"),
    ("POOL8-SHA256SUMS", "tools/claims-v3/m10/POOL8-SHA256SUMS", "top", 209,
     "9675e44e1343dd77871d33427efd84ffff43a858659446c3e17edf9dc7c8cd18"),
    ("POOL8-SHA256SUMS-62", "tools/claims-v3/m10/POOL8-SHA256SUMS-62", "top", 62,
     "e761c5acdfd0eceede6e3569248e4b87398dff6a202a8de60ddeb3976475c5b5"),
    ("predictor SHA256SUMS", "docs/reports/data/2026-11-05-q142p-pool8-predictor/SHA256SUMS", "top", 16,
     "fa274e3673865d5681d83c2fc3deb38e76fde001fd6931cef332c6119df85013"),
    ("predictor SHA256SUMS-a2", "docs/reports/data/2026-11-05-q142p-pool8-predictor/SHA256SUMS-a2", "top", 9,
     "65942a7669016df1b1f46f5266bb95cb78bcef2083bc873d3832bd5887898b27"),
    ("freeze SHA256SUMS (Q142(x))", "docs/reports/data/2026-11-05-q142x-pool8-freeze/SHA256SUMS", "top", 160,
     "26eb0b2511e6f4ed3e6e9cc0646f24106a06cfffd402b388ddb110a5e10ab8d2"),
    ("blind8/SHA256SUMS (the pool)", "tools/claims-v3/kinds/blind8/SHA256SUMS", "rel", 89,
     "606b3d7ee607d6c6d4f3f0ab61f86bf7e14a3de8889572843017738037b7dde8"),
    ("p8-600/SHA256SUMS", "tools/claims-v3/p8-600/SHA256SUMS", "top", 5,
     "dc52c3a035504f7cd6e66186214e3c828f2d3a7bb05b043b86fd0f3824b593ea"),
    ("p8-600/SHA256SUMS-v2", "tools/claims-v3/p8-600/SHA256SUMS-v2", "top", 4,
     "e3b56ce62e9e614768f11b0097deba76bb1fbe42e3e9bebb4e8b85b5d74a9a7d"),
    ("frozen-sha256-e173.json files", "tools/claims-v3/e173/frozen-sha256-e173.json", "files", 26,
     "8948175db7018f091574e07f3652bb3376d613c19f50a462476792e603b24fc7"),
    ("frozen-sha256-e174.json files", "tools/claims-v3/e174/frozen-sha256-e174.json", "files", 32,
     "cc31984b518ad430b8bc658ee9abf11d2a523c3d340fb38baf10ea57dbcc8b66"),
    ("harness-e171.json (repo files)", "tools/claims-v3/e171/harness-e171.json", "harness", 97,
     "234a61236f9d3fab3601bd134f4ae24e5d99362280f1e9b5cba13480ac6a5561"),
    ("harness-e172.json (repo files)", "tools/claims-v3/e172/harness-e172.json", "harness", 99,
     "5680f42ec3ddd2d999895fe046c5c88de96729605e799373d336ed5c3fd40016"),
    ("harness-e173.json (repo files)", "tools/claims-v3/e173/harness-e173.json", "harness", 135,
     "aa64054f3d56a76c0676e78e1e96fbeb22439c2907fddab79368027c3d7f96ba"),
    ("harness-e174.json (repo files)", "tools/claims-v3/e174/harness-e174.json", "harness", 110,
     "22b7f71389cf037e4bea2dcd1a4f8302ae94caac8a33eeb45d4d6d2a201a70e8"),
]
V3_LISTS = [  # this pass's two (pins written when the lists were made, before their commit)
    ("p8-600/SHA256SUMS-v3", "tools/claims-v3/p8-600/SHA256SUMS-v3", "top", 4,
     "2194f2b4cd2a82673ac246beb10cd1a4c408472f3cc0afc0cafed1a9f62c8bcb"),
    ("k6/SHA256SUMS-drivers-v3 (the card day's drivers)", "tools/claims-v3/q141k-runbook/k6/SHA256SUMS-drivers-v3", "top", 39,
     "673de2ca66e2bf6cef9bbf0fa99bffdd94d48d0fbe851ad30485697359a4b0cb"),
]


class Blobs:
    """the committed blobs at one revision, through one `git cat-file --batch` process"""
    def __init__(self, repo, rev):
        self.repo, self.rev, self.cache = repo, rev, {}
        self.p = subprocess.Popen(["git", "-C", repo, "cat-file", "--batch"], stdin=subprocess.PIPE, stdout=subprocess.PIPE)

    def get(self, path):
        if path not in self.cache:
            self.p.stdin.write(f"{self.rev}:{path}\n".encode())
            self.p.stdin.flush()
            head = self.p.stdout.readline().decode().split()
            if len(head) == 3 and head[1] == "blob":
                data = self.p.stdout.read(int(head[2]))
                self.p.stdout.read(1)
                self.cache[path] = data
            else:
                self.cache[path] = None
        return self.cache[path]

    def close(self):
        self.p.stdin.close()
        self.p.wait(timeout=60)


def h(b):
    return hashlib.sha256(b).hexdigest() if b is not None else None


def entries(kind, path, text):
    """[(repo-relative path, sha256)] of one list's text"""
    base = os.path.dirname(path)
    if kind in ("rel", "top"):
        out = []
        for line in text.splitlines():
            if line.strip() and not line.startswith("#"):
                hh, p = line.split(None, 1)
                out.append((os.path.normpath(os.path.join(base if kind == "rel" else "", p.strip().lstrip("*"))), hh))
        return out
    if kind == "e168":
        fj = json.loads(text)
        it = list(fj.items()) if isinstance(fj, dict) else [tuple(x) for x in fj]
        return [(os.path.normpath(os.path.join(base, p)), hh) for p, hh in it]
    if kind == "pyfrozen":
        m = re.search(r"^FROZEN\s*=\s*(\{.*?^\})", text, re.S | re.M)
        return list(ast.literal_eval(m.group(1)).items()) if m else []
    if kind == "files":
        return list(json.loads(text)["files"].items())
    if kind == "harness":
        out = []
        for k, v in json.loads(text).items():
            if isinstance(v, dict) and k != "box_binaries_sha256" and not k.startswith("_"):
                out += list(v.items())
        return out
    raise ValueError(kind)


def wt_sha(wt, path):
    try:
        with open(os.path.join(wt, path), "rb") as f:
            return h(f.read())
    except OSError:
        return None


def check(B, wt, name, path, kind, want_n, pin):
    rec = {"name": name, "list": path, "expected": want_n, "pin": pin}
    blob = B.get(path)
    bad = []
    if blob is None:
        rec.update(entries=0, committed=0, work_tree=0)
        bad.append("the list is not in the revision")
    else:
        rec["list_sha256"] = h(blob)
        if h(blob) != pin:
            bad.append(f"the list's sha256 {h(blob)[:12]} is not the pinned {pin[:12]}")
        if wt_sha(wt, path) != h(blob):
            bad.append("the list's work-tree copy is not its committed blob")
        try:
            it = entries(kind, path, blob.decode("utf-8"))
        except Exception as e:  # noqa: BLE001
            it = []
            bad.append(f"unreadable ({type(e).__name__})")
        b = [p for p, hh in it if h(B.get(p)) != hh]
        w = [p for p, hh in it if wt_sha(wt, p) != hh]
        rec.update(entries=len(it), committed=len(it) - len(b), work_tree=len(it) - len(w))
        if len(it) != want_n:
            bad.append(f"{len(it)} entries, not {want_n}")
        if b:
            bad.append(f"{len(b)} committed blob(s) differ: {', '.join(b[:3])}")
        if w:
            bad.append(f"{len(w)} work-tree file(s) differ: {', '.join(w[:3])}")
    rec["pass"] = not bad
    rec["why"] = bad
    print(f"{'PASS' if not bad else 'FAIL'} {name}: {rec['entries']} entries (expected {want_n}); committed {rec['committed']}; work tree "
          f"{rec['work_tree']}" + (f"; {'; '.join(bad)}" if bad else ""))
    return rec


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=TOP)
    ap.add_argument("--rev", default="HEAD")
    ap.add_argument("--worktree")
    ap.add_argument("--json")
    a = ap.parse_args(argv)
    if not os.path.isdir(os.path.join(a.repo, ".git")) and not os.path.isfile(os.path.join(a.repo, ".git")):
        print(f"usage: {a.repo} is not a git work tree")
        return 2
    r = subprocess.run(["git", "-C", a.repo, "rev-parse", "--verify", a.rev + "^{commit}"], capture_output=True, text=True)
    if r.returncode != 0:
        print(f"usage: {a.rev} is not a commit of {a.repo}")
        return 2
    rev = r.stdout.strip()
    wt = a.worktree or a.repo
    print(f"== lists at {rev[:12]} (committed blobs) and in the work tree {'(the repo)' if wt == a.repo else '(another directory)'}")
    B = Blobs(a.repo, rev)
    try:
        r22 = [check(B, wt, *x) for x in LISTS]
        r3 = [check(B, wt, *x) for x in V3_LISTS]
    finally:
        B.close()
    k22, k3 = sum(x["pass"] for x in r22), sum(x["pass"] for x in r3)
    me = h(open(os.path.abspath(__file__), "rb").read())
    print(f"LISTS22: {k22} of {len(r22)} PASS")
    print(f"LISTS-V3: {k3} of {len(r3)} PASS")
    print(f"lists22_k6.py sha256 {me}")
    ok = k22 == len(r22) and k3 == len(r3)
    print("ALL LISTS PASS" if ok else "A LIST FAILS")
    if a.json:
        open(a.json, "w").write(json.dumps({"rev": rev, "lists22": r22, "lists_v3": r3, "pass": ok, "checker_sha256": me}, indent=1, sort_keys=True)
                                + "\n")
    return 0 if ok else 4


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
