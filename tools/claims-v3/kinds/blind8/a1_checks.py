#!/usr/bin/env python3
"""Q142(x): the facts dated note A1 (DESIGN.md.dated-note-1.md, A1-4) records about the designer's six faults, read from committed
files and git, plus two scratch files given as arguments (never named in the output).

    python3 -B a1_checks.py [--test-provenance <TEST pool's provenance-blind8.json>] [--rebuild <a rebuilt pool dir>]

Reads only; writes nothing. Standard library. SPDX-License-Identifier: Apache-2.0
"""
import argparse
import gzip
import hashlib
import json
import os
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
DD = os.path.join(TOP, "docs", "reports", "data")
B6 = os.path.join(TOP, "tools", "claims-v3", "kinds", "blind6")
fsha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()  # noqa: E731
HOLD = ("fp32.a_onebit_b5_third", "fp32.real_smol_softmax_v_causal")


def git(*a):
    return subprocess.run(["git", "-C", TOP] + list(a), capture_output=True, text=True, timeout=60).stdout.strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--test-provenance")
    ap.add_argument("--rebuild")
    a = ap.parse_args()
    out = {}
    # 1. the generator, the seed, the commit
    gen = os.path.join(HERE, "make_blind8.py")
    out["generator"] = {"sha256": fsha(gen), "git_blob_worktree": git("hash-object", gen),
                        "git_blob_committed": git("rev-parse", "153b720f:tools/claims-v3/kinds/blind8/make_blind8.py"),
                        "commit": git("show", "-s", "--format=%H %ci", "153b720f")}
    seed_commit = "c996d1357609c10009c80e59dd8e85bcc652343f"
    out["seed"] = {"commit": seed_commit, "hex": "0x" + hashlib.sha256(seed_commit.encode("ascii")).hexdigest()[:16],
                   "commit_is_ancestor_of_153b720f": subprocess.run(["git", "-C", TOP, "merge-base", "--is-ancestor", seed_commit, "153b720f"],
                                                                    timeout=60).returncode == 0}
    prov = json.load(open(os.path.join(HERE, "provenance-blind8.json")))
    out["pool_provenance"] = {"made_at": prov["made_at"], "made_by": prov["made_by"], "seed_hex": prov["seed"]["hex"]}
    if a.test_provenance:
        tp = json.load(open(a.test_provenance))
        out["test_pool_provenance"] = {"sha256_of_file": fsha(a.test_provenance), "made_at": tp["made_at"], "made_by": tp["made_by"],
                                       "seed": tp["seed"]}
    # 2. DESIGN.md's dateline
    dm = os.path.join(HERE, "DESIGN.md")
    out["design_md"] = {"line_3": open(dm).read().split("\n")[2], "git_blob_worktree": git("hash-object", dm),
                        "git_blob_committed": git("rev-parse", "153b720f:tools/claims-v3/kinds/blind8/DESIGN.md"),
                        "commit_time": git("show", "-s", "--format=%ci", "153b720f")}
    # 3. the two re-runs drawn from blind6 tiles flagged hold
    man6 = {}
    for line in open(os.path.join(B6, "MANIFEST")):
        f = line.split()
        if len(f) == 8:
            man6[f[2]] = {"sha256": f[0], "type": f[3], "flag": f[7]}
    hc = [h["name"] for h in json.load(open(os.path.join(B6, "blind6.json"))).get("hold_candidates", [])]
    sessions = {"E153": ("2026-11-03-e153-blind6-aifoundry3/e153.json", "2026-11-03-e153-blind6-aifoundry3/ccheck/ccheck-all.json"),
                "E157": ("2026-11-03-e157-blind6-card1/e157.json", "2026-11-03-e157-blind6-card1/ccheck/ccheck-session.json.gz")}
    holds = {}
    for n in HOLD:
        h = {"blind6_flag": man6[n]["flag"], "in_blind6_hold_candidates": n in hc, "pool8_bytes_equal_blind6":
             fsha(os.path.join(HERE, "tiles", "fp32", n + ".bin")) == man6[n]["sha256"], "sessions": {}}
        for s, (red, cc) in sessions.items():
            it = json.load(open(os.path.join(DD, red)))["items"][n]
            op = gzip.open if cc.endswith(".gz") else open
            L = json.load(op(os.path.join(DD, cc), "rt"))["launches"]
            v = {}
            for x in L:
                if x.get("tile_sha256") == man6[n]["sha256"] and x.get("type") == man6[n]["type"]:
                    v[x["verdict"]] = v.get(x["verdict"], 0) + 1
            h["sessions"][s] = {"D_mean_w": round(it["D"]["mean"], 3), "passes": it["D"]["n"], "c_check_launches": v}
        holds[n] = h
    out["hold_reruns"] = holds
    # 4. a rebuild of the pool from the committed generator, against this copy
    if a.rebuild:
        same, diff = [], []
        for line in open(os.path.join(HERE, "SHA256SUMS")):
            r = line.rstrip("\n").split("  ", 1)[1]
            (same if os.path.isfile(os.path.join(a.rebuild, r)) and fsha(os.path.join(a.rebuild, r)) == fsha(os.path.join(HERE, r)) else diff).append(r)
        sums_same = fsha(os.path.join(a.rebuild, "SHA256SUMS")) == fsha(os.path.join(HERE, "SHA256SUMS"))
        (same if sums_same else diff).append("SHA256SUMS")
        out["rebuild"] = {"files_compared": len(same) + len(diff), "identical": len(same), "differ": diff}
    print(json.dumps(out, indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
