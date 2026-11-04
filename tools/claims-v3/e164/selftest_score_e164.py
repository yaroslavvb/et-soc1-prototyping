#!/usr/bin/env python3
"""E164 (Q141(b)): the scorer's self-test on its parent run's committed data, before E164's claim. Section 26 of the round's brief:
"Each scorer is self-tested on its parent run's committed data. The self-test must reproduce the parent's registered verdicts, and
its output is committed"; E157 -> E164, with M8 primary as registered then. Standard library only; reads only committed files.

score_e164.run(), the same code that scores E164, is run on E157's own registration (tools/claims-v3/e157/predictions-e157.json,
lab 01676499: score_e164 reads it with E157's scheme, M8 primary) and E157's committed data
(docs/reports/data/2026-11-03-e157-blind6-card1/), exactly as E157's collector ran its scorer (collect_e157.sh step 5; the lane's
score_check.sh and score_x.sh): the primary reduction e157.json, the C verdicts ccheck/ccheck-session.json.gz, every pass's and the
smoke's runs.jsonl, runs.csv, the six arms, and E142's registered footing for K1. Then:

  A. without E153's reduction: every verdict, every rule's numbers and every reported block equal the committed scored.json (a
     leaf-by-leaf comparison of the two JSON trees, exact), and the generated results.md equals the committed one byte for byte;
  B. with E153's committed primary reduction (docs/reports/data/2026-11-03-e153-blind6-aifoundry3/e153.json, no tile dropped:
     E153's C check excluded none), the same against scored-e153.json and results-e153.md (X1, X2, S1, S2 scored).

    python3 -B tools/claims-v3/e164/selftest_score_e164.py > tools/claims-v3/e164/selftest-e157-repro.txt

Run it with Python 3.12 or later (the Intel's python3, 3.13), as E157's scorer ran: Python 3.12 changed float sum() to a compensated
summation, so on 3.9 the verdicts and both results pages are still identical but about 1 in 40 of the numbers differ in their last
binary digit. One leaf is allowed by name, and only with exactly these values: c_check/verdict_files[0], the input file's name, which
is 'ccheck-session.json.gz' here (read as committed) and 'ccheck-session.json' in E157's run (its collector read the gunzipped copy).
SPDX-License-Identifier: Apache-2.0
"""
import glob
import hashlib
import json
import math
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import score_e164 as S  # noqa: E402

D = os.path.join(ROOT, "docs", "reports", "data", "2026-11-03-e157-blind6-card1")
REG157 = os.path.join(ROOT, "tools", "claims-v3", "e157", "predictions-e157.json")
E153 = os.path.join(ROOT, "docs", "reports", "data", "2026-11-03-e153-blind6-aifoundry3", "e153.json")
ARMS = (("e142_footing", "e157-e142footing.json"), ("session_own_slope", "e157-auto.json"), ("dips_kept", "e157-dipskept.json"),
        ("leak0.2955", "e157-leak0.2955.json"), ("leak0.3320", "e157-leak0.3320.json"), ("relaxed", "e157-relaxed.json"))
ALLOWED = {"/c_check/verdict_files[0]": ("ccheck-session.json.gz", "ccheck-session.json")}   # the input file's name only


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def walk(a, b, path, diffs, counts):
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b)):
            if k not in a or k not in b:
                diffs.append(f"{path}/{k}: {'missing in the reproduction' if k not in a else 'not in the committed file'}")
                continue
            walk(a[k], b[k], f"{path}/{k}", diffs, counts)
        return
    if isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            diffs.append(f"{path}: list length {len(a)} != {len(b)}")
            return
        for i, (x, y) in enumerate(zip(a, b)):
            walk(x, y, f"{path}[{i}]", diffs, counts)
        return
    counts[0] += 1
    if isinstance(a, float) and isinstance(b, float) and math.isnan(a) and math.isnan(b):
        return
    if path in ALLOWED and (a, b) == ALLOWED[path]:
        counts[1] += 1
        return
    if a != b or type(a) is not type(b) and not (isinstance(a, (int, float)) and isinstance(b, (int, float)) and a == b):
        diffs.append(f"{path}: {a!r} != committed {b!r}")


def one(label, reg, other, committed_json, committed_md):
    prim = json.load(open(os.path.join(D, "e157.json")))
    runs_jsonl = sorted(glob.glob(os.path.join(D, "aifoundry1-c1", "e157", "p157*", "runs.jsonl"))) + \
        [os.path.join(D, "aifoundry1-c1", "e157-smoke-p15701", "runs.jsonl")]
    arms = [(n, json.load(open(os.path.join(D, f)))) for n, f in ARMS]
    res = S.run(reg, prim, [os.path.join(D, "ccheck", "ccheck-session.json.gz")], runs_jsonl, os.path.join(D, "runs.csv"), arms,
                other, (), json.load(open(os.path.join(D, "e157-e142footing.json"))))
    mine = json.loads(json.dumps(res, default=lambda o: None))
    ref = json.load(open(os.path.join(D, committed_json)))
    diffs, counts = [], [0, 0]
    walk(mine, ref, "", diffs, counts)
    md_same = S.markdown(res, reg) == open(os.path.join(D, committed_md)).read()
    vs = mine["verdicts"]
    same_v = vs == ref["verdicts"]
    print(f"[{label}] against {committed_json} ({sha(os.path.join(D, committed_json))[:16]}...) and {committed_md}")
    print(f"  verdicts: {len(vs)} reproduced, {'all equal' if same_v else 'DIFFER'} to the committed ones")
    for r, v in vs.items():
        arm = mine["arm_sensitive"].get(r) or []
        print(f"    {r}: {v}" + (f"   (differs in: {', '.join(arm)})" if arm else ""))
    print(f"  the JSON trees: {counts[0]} leaves compared, {len(diffs)} differ" + (": " + "; ".join(diffs[:12]) if diffs else "") +
          f" ({counts[1]} allowed by name: the input file's name, " + ", ".join(f"{k} {v[0]!r} / {v[1]!r}" for k, v in ALLOWED.items()) + ")")
    print(f"  {committed_md}: {'byte-identical' if md_same else 'DIFFERS'}")
    return same_v and not diffs and md_same


def main():
    reg = json.load(open(REG157))
    print("E164 scorer self-test: score_e164.py run on E157's registration and committed data (nothing here is new data)")
    print(f"  Python {sys.version.split()[0]}" + ("" if sys.version_info >= (3, 12) else
                                                   " (older than 3.12: expect last-digit differences in the numbers, see the docstring)"))
    print(f"  score_e164.py {sha(os.path.join(HERE, 'score_e164.py'))[:16]}...; E157's registration predictions-e157.json "
          f"{sha(REG157)[:16]}... (lab 01676499); E157's scorer score_e157.py "
          f"{sha(os.path.join(ROOT, 'tools/claims-v3/e157/score_e157.py'))[:16]}... (not run here)")
    print(f"  scheme: {json.dumps(S.scheme_of(reg))}")
    ok_a = one("A, E157 as reduced (X1, X2, S1, S2 not scored)", reg, None, "scored.json", "results.md")
    ok_b = one("B, with E153's committed reduction (8e18eb67)", reg, json.load(open(E153)), "scored-e153.json", "results-e153.md")
    ok = ok_a and ok_b
    print(f"SELFTEST {'PASS' if ok else 'FAIL'}: E157's registered verdicts and numbers {'reproduced' if ok else 'NOT reproduced'} "
          "by score_e164.py in E157's scheme")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
