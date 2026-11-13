#!/usr/bin/env python3
"""Has a sparse-parity instance ever run? Every instance a committed file names, against one candidate.

  spp_never_ran.py [--repo TREE] [--exclude PATH ...] --n N --k K --eta E --m M [--seed S]

Reads every file under workloads/sparseparity/ and docs/ (files over 50 MB skipped) and collects the instances they
name: command lines with --n/--k (and --eta, --m, --seed when they follow), spref's "n= k= eta= m= seed=", the
planner's "--n --k --m", and JSON lines carrying "n" and "k" (top level or under "instance"). It prints the (n, k)
pairs found, the noise levels and sample counts, and for the candidate: every file that names its n with its k, its
eta, its m, or the whole tuple. "Never ran" here means no committed file names it; it cannot see runs nobody
committed. Once a run of the candidate is committed it is named, of course: --exclude leaves out a path (a folder or a
file, relative to the tree), e.g. the candidate's own data folder, to re-check the record as it stood before it.

Desk only. Standard library only; run with python3 -I -B. SPDX-License-Identifier: Apache-2.0
"""
import argparse
import collections
import json
import os
import re
import sys

CMD = re.compile(r"--n\s+(\d+)\s+--k\s+(\d+)(?:\s+--eta\s+([0-9.]+))?(?:\s+--m\s+(\d+))?(?:\s+--seed\s+(\d+))?")
SPREF = re.compile(r"\bn=(\d+)\s+k=(\d+)\s+eta=([0-9.]+)\s+m=(\d+)(?:\s+seed=(\d+))?")
PLANNER = re.compile(r"--n\s+(\d+)\s+--k\s+(\d+)\s+--m\s+(\d+)")


def num(x, kind):
    try:
        return kind(x)
    except (TypeError, ValueError):
        return None


def collect(tree, exclude=()):
    found = collections.defaultdict(set)    # (n, k, eta, m, seed) -> files
    nfiles = 0
    exclude = tuple(os.path.normpath(e) for e in exclude)
    for d in (os.path.join(tree, "workloads", "sparseparity"), os.path.join(tree, "docs")):
        for dp, _, fn in os.walk(d):
            for f in fn:
                p = os.path.join(dp, f)
                try:
                    if os.path.getsize(p) > 50_000_000:
                        continue
                    t = open(p, errors="replace").read()
                except OSError:
                    continue
                nfiles += 1
                rel = os.path.relpath(p, tree)
                if any(rel == e or rel.startswith(e + os.sep) for e in exclude):
                    continue
                for mt in CMD.finditer(t):
                    n, k, eta, m, seed = mt.groups()
                    found[(num(n, int), num(k, int), num(eta, float), num(m, int), num(seed, int))].add(rel)
                for mt in SPREF.finditer(t):
                    n, k, eta, m, seed = mt.groups()
                    found[(num(n, int), num(k, int), num(eta, float), num(m, int), num(seed, int))].add(rel)
                for mt in PLANNER.finditer(t):
                    n, k, m = mt.groups()
                    found[(num(n, int), num(k, int), None, num(m, int), None)].add(rel)
                if '"n"' not in t or '"k"' not in t:
                    continue
                for line in t.splitlines():
                    line = line.strip()
                    if not (line.startswith("{") and '"n"' in line and '"k"' in line):
                        continue
                    try:
                        j = json.loads(line)
                    except ValueError:
                        continue
                    if not isinstance(j, dict):
                        continue
                    src = j.get("instance") if isinstance(j.get("instance"), dict) else j
                    g = lambda key: src.get(key, j.get(key))  # noqa: E731
                    found[(num(g("n"), int), num(g("k"), int), num(g("eta"), float), num(g("m"), int),
                           num(g("seed"), int))].add(rel)
    return found, nfiles


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--repo", default=os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")))
    ap.add_argument("--n", type=int, required=True)
    ap.add_argument("--k", type=int, required=True)
    ap.add_argument("--eta", type=float, required=True)
    ap.add_argument("--m", type=int, required=True)
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument("--exclude", action="append", default=[], help="a path to leave out (repeatable)")
    a = ap.parse_args(argv)
    found, nfiles = collect(a.repo, a.exclude)
    if a.exclude:
        print("left out:", " ".join(sorted(a.exclude)))
    pairs = sorted({(n, k) for (n, k, *_r) in found if n is not None and k is not None})
    etas = sorted({e for (_n, _k, e, *_r) in found if e is not None})
    print(f"files read: {nfiles}; distinct instance tuples: {len(found)}")
    print("(n, k) pairs named:", " ".join(f"({n},{k})" for n, k in pairs))
    print("eta values named:", " ".join(f"{e:g}" for e in etas))
    def files(pred):
        out = set()
        for key, fs in found.items():
            if pred(key):
                out |= fs
        return sorted(out)
    checks = {
        f"n = {a.n} with k = {a.k}": files(lambda t: t[0] == a.n and t[1] == a.k),
        f"n = {a.n} (any k)": files(lambda t: t[0] == a.n),
        f"eta = {a.eta:g}": files(lambda t: t[2] is not None and abs(t[2] - a.eta) < 1e-9),
        f"m = {a.m}": files(lambda t: t[3] == a.m),
        f"the tuple ({a.n},{a.k},{a.eta:g},{a.m})": files(lambda t: t[0] == a.n and t[1] == a.k and t[3] == a.m
                                                         and t[2] is not None and abs(t[2] - a.eta) < 1e-9),
    }
    for what, fs in checks.items():
        print(f"{what}: " + ("named by no committed file" if not fs else f"named by {len(fs)}: " + ", ".join(fs[:5])))
    print("NEVER RAN (by the committed record)" if not checks[f"the tuple ({a.n},{a.k},{a.eta:g},{a.m})"] and
          not checks[f"n = {a.n} with k = {a.k}"] else "NAMED BEFORE")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
