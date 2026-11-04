#!/usr/bin/env python3
"""E164 (Q141(b)): rank 4's paired-anchor rule, Q140(x)'s (tools/claims-v3/kinds/blind7/rank4_rule.json, RANK4-RULE.md, lab
75802201), scored on the E163 / E164 pair with Q140(x)'s scorer score_rank4.py run unchanged (its sha256 and the rule's are checked
first). E164.md registers only RK4's inputs (pool 7's int8 random anchors three times a pass, four planned passes); the rule, the
pairing and the verdicts are Q140(x)'s. Standard library only.

    python3 -B tools/claims-v3/e164/pair_rank4_e164.py --e163 <E163's scored.json or a D table> --e164 <E164's scored.json> \
        [--out rank4-e163-e164.json] [--txt rank4-e163-e164.txt]
    python3 -B tools/claims-v3/e164/pair_rank4_e164.py --selftest [--txt selftest-rank4-pair.txt]

Each session file is what score_rank4.load_session reads: a registered scored.json in E153's or E157's layout (E164's scorer writes
E157's: primary.power_rows.<model>.<tile>.measured, n_passes, sd; primary.pool_anchors; primary.e78_anchors_D) or a D table. Beside the
verdict (never a verdict): the int8 difference's standard error from the two sessions' passes, sqrt(se(s_anchor)^2 + se(s_pool)^2),
with se(s_pool) read from the pool median's bootstrap interval as (hi - lo) / 3.92, against the registered forecast's 1.35-1.64% and
Q140's final critic's planning estimate for this design (about 0.95%).

--selftest: (1) score_rank4.py's own self-test on pool 6 (E153 / E157), which must read 16 checks, 0 differ, as committed in
selftest-rank4.txt; (2) the plumbing on E164's layout: a session scored by score_e164.run on simulated data (nothing measured) paired
with an aifoundry3 D table at card 1 / M9's terms (PASS on both families, offset 0), and again with card 1's two int8 random anchors
3% low (int8 FAIL, floats PASS).
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import copy
import contextlib
import hashlib
import importlib.util
import io
import json
import os
import random
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
P7 = os.path.join(ROOT, "tools", "claims-v3", "kinds", "blind7")
PINNED = {"score_rank4.py": "2aba0a82898c96521f35fa402a376cb303588791775da2c7d4b8004bb8998897",
          "rank4_rule.json": "4b9ccaf006fff9bc92041bf470fe8520e7443f790c02dd1ba3e1ee62293f2507",
          "selftest-rank4.txt": "b35d4dfea830549c69d8d5369aabb9daf146fbdf1838104226241052593f427b"}


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def rank4():
    bad = [f"{f}: {sha(os.path.join(P7, f))} != {w}" for f, w in PINNED.items() if sha(os.path.join(P7, f)) != w]
    if bad:
        raise SystemExit("refusing - Q140(x)'s frozen rule or scorer differs from lab 75802201:\n  " + "\n  ".join(bad))
    spec = importlib.util.spec_from_file_location("score_rank4", os.path.join(P7, "score_rank4.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def beside(out):
    """The int8 difference's standard error from the passes (a reading, never a verdict)."""
    r = out["families"].get("int8", {})
    if r.get("verdict") in (None, "NOT SCORED") or r.get("s_anchor_mean_se_from_passes") is None:
        return None
    se_a = r["s_anchor_mean_se_from_passes"] / r["s_anchor"]
    lo, hi = r["s_pool_95"]
    se_p = (hi - lo) / 3.92 / r["s_pool"]
    return {"int8_s_anchor_rel_se": se_a, "int8_s_pool_rel_se_from_interval": se_p, "int8_difference_rel_se": (se_a ** 2 + se_p ** 2) ** 0.5,
            "registered_forecast_rel_se": [0.0135, 0.0164], "critic_planning_estimate_rel_se": 0.0095}


def score_pair(R, a3_path, c1_path, label="E163/E164"):
    rule = json.load(open(os.path.join(P7, "rank4_rule.json")))
    mname, man = R.load_manifest(P7)
    A, srcA = R.load_session(a3_path)
    C, srcC = R.load_session(c1_path)
    out = R.score(rule, man, A, C, label)
    out["inputs"] = {"aifoundry3": [os.path.basename(a3_path), srcA], "aifoundry1c1": [os.path.basename(c1_path), srcC], "manifest": mname,
                     "score_rank4_sha256": PINNED["score_rank4.py"], "rank4_rule_sha256": PINNED["rank4_rule.json"]}
    out["beside_not_a_verdict"] = beside(out)
    return out


def selftest(txt):
    R = rank4()
    L = []
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = R.selftest(ROOT, None)
    own = buf.getvalue()
    same = own == open(os.path.join(P7, "selftest-rank4.txt")).read()
    L.append(f"(1) score_rank4.py's own self-test on pool 6 (E153 / E157): rc {rc}; output byte-identical to the committed "
             f"selftest-rank4.txt: {same}; last line: {own.strip().splitlines()[-1]}")
    ok = rc == 0 and same
    sys.path.insert(0, HERE)
    import score_e164 as S  # noqa: E402
    import selftest_e164 as T  # noqa: E402  (its simulated session; nothing measured)
    reg = T.REG
    term = reg["model"]["card_term_applied"]
    tmp = os.path.join(HERE, "__pair_selftest_tmp")
    os.makedirs(tmp, exist_ok=True)
    for label, int8_anchor_shift in (("card 1 at M9's terms", 1.0), ("card 1's two int8 random anchors 3% low", 0.97)):
        sess = T.session(random.Random(7), "as_good")
        for p in sess["per_pass"].values():
            for a in reg["sets"]["anchors_random_int8"]:
                p[a]["D"] *= int8_anchor_shift
        res = S.run(reg, sess)
        c1p = os.path.join(tmp, "e164-scored.json")
        json.dump(res, open(c1p, "w"), default=lambda o: None)
        a3 = {"tiles": {}}
        clean = T.session(random.Random(7), "as_good")
        for t in reg["tiles"]:
            vals = [clean["per_pass"][str(p)][t]["D"] / (term["M9_int8"] if t.startswith("int8.") else term["M9"]) for p in clean["passes"]]
            a3["tiles"][t] = {"mean": sum(vals) / len(vals), "per_pass": vals}
        a3p = os.path.join(tmp, "e163-table.json")
        json.dump(a3, open(a3p, "w"))
        out = score_pair(R, a3p, c1p, f"selftest: {label}")
        L += R.lines(out)
        want = {"floats": "PASS", "int8": "PASS" if int8_anchor_shift == 1.0 else "FAIL"}
        got = {f: out["families"][f]["verdict"] for f in want}
        good = got == want
        L.append(f"  expected {want}: {'ok' if good else 'DIFFERS'}; beside: {json.dumps(out['beside_not_a_verdict'])}")
        ok &= good
    for f in os.listdir(tmp):
        os.remove(os.path.join(tmp, f))
    os.rmdir(tmp)
    L.append(f"SELFTEST {'PASS' if ok else 'FAIL'}")
    text = "\n".join(L) + "\n"
    print(text, end="")
    if txt:
        open(txt, "w").write(text)
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--e163")
    ap.add_argument("--e164")
    ap.add_argument("--out")
    ap.add_argument("--txt")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        sys.exit(selftest(a.txt))
    if not (a.e163 and a.e164):
        ap.error("--e163 and --e164 are required (or --selftest)")
    R = rank4()
    out = score_pair(R, a.e163, a.e164)
    text = "\n".join(R.lines(out)) + "\nbeside (not a verdict): " + json.dumps(out["beside_not_a_verdict"]) + "\n"
    print(text, end="")
    if a.out:
        json.dump(out, open(a.out, "w"), indent=1, sort_keys=True)
    if a.txt:
        open(a.txt, "w").write(text)


if __name__ == "__main__":
    main()
