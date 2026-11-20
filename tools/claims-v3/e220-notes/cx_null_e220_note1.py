#!/usr/bin/env python3
"""E220, dated note 1, part 2 (fix-e220, Q233, Fri 20 Nov 2026, before any E220 datum; verify-e220's F3): THE CROSS-CARD ENERGY TEST'S FALSE
'LARGER HERE' RATE AT EQUAL DISTRIBUTION, to be printed beside any CX-E or CXP-E verdict. No rule changes: the registered CX-E and CXP-E read as
registered (E220.md section 7, rules-e220.json > cross_card_test); this is a reading printed beside them.

    /usr/bin/python3 -I -B tools/claims-v3/e220-notes/cx_null_e220_note1.py make <the lab clone> <out.json>
        reads the frozen tools/claims-v3/e220/rules-e220.json (the X twins' aifoundry3 errors frozen there from E218's committed data and MM1-v3.2's
        frozen E218 forecast, each arm's ties, the registered power at k = 1) and simulates, per arm (CX-E: W over idle given the measured op
        time; CX-T, the wall cycles, beside) and pooled over both arms' twins (CXP-E, CXP-T), DAYS days of the registered test (d = e_here - e_a3,
        decided past the arm's tie, the exact two-sided sign test, at least 10 decided, p < 0.05) under two nulls:
          normal     e_here = |N(0, sigma_a3)|, sigma_a3 the rms of the twins' aifoundry3 errors: the registered power's own form at k = 1
                     (rules_e220.cross_power; its 2,000 days re-drawn here with another generator, so its figure is matched, not reproduced);
          resampled  e_here = |an aifoundry3 error drawn with replacement from the same twins|: THIS CARD'S ERRORS DISTRIBUTED AS aifoundry3's,
                     the null of "MM1-v3.2's energy error is no larger on this card" when the errors are heavy-tailed;
        and writes, per test, the rates of LARGER HERE, SMALLER HERE, NOT DECIDED and TOO FEW under each null, the registered k = 1 figures
        beside, and the twins' shape (n, rms, median |e|, the median a normal error of the same rms would give: 0.6745 sigma).
    /usr/bin/python3 -I -B tools/claims-v3/e220-notes/cx_null_e220_note1.py beside <a scorer output .json> [<the note's .json>]
        prints each CX-E / CXP-E (and CX-T / CXP-T) verdict the frozen scorer wrote (score_e220.py's out["verdicts"] and its counts) with the
        false LARGER HERE rates beside it: "<rule>: <verdict> (<n> twins, <here> larger here, <a3> larger on aifoundry3, p <p>) | dated note 1:
        false LARGER HERE at equal distribution <r1> (resampled), at equal rms with normal errors <r2> (registered <r3>)". Reads only.
    /usr/bin/python3 -I -B tools/claims-v3/e220-notes/cx_null_e220_note1.py selftest <a new scratch folder>
        beside on a stand-in scorer output (score_e220.py's form) and on a missing file: "SELFTEST-BESIDE-E220-NOTE1 2 of 2 PASS".
Standard library only, single-threaded (Python's own random.Random, seeded from a fixed string). SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import math
import os
import random
import sys

DAYS = 20000
SEED = "E220 dated note 1 cross-card null (fix-e220)"
TOO_FEW = 10


def sign_p(npos, nneg):
    n = npos + nneg
    if n == 0:
        return 1.0
    k = min(npos, nneg)
    return min(1.0, 2 * sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n)


def twins(R, arm, q):
    """the arm's X twins' |aifoundry3 error| for the test (q 'Wg': the energy-scored-relative twins, as rules_e220.cross_power reads them)"""
    base = R["arms"][arm]["cross_card"]["baseline_aifoundry3_E218"]
    key = "a3_ln_err_wall" if q == "wall" else "a3_ln_err_Wg"
    out = []
    for pid, v in sorted(base.items()):
        if isinstance(v, dict) and v.get(key) is not None and (q == "wall" or v.get("a3_energy_scored_relative")):
            out.append((pid, abs(v[key])))
    return out


def simulate(cases, null, rng):
    """cases: [(|e_a3|, tie)]; -> the rates of each verdict over DAYS days"""
    e3 = [e for e, _ in cases]
    s3 = math.sqrt(sum(e * e for e in e3) / len(e3))
    cnt = {"LARGER HERE": 0, "SMALLER HERE": 0, "NOT DECIDED": 0, "TOO FEW": 0}
    for _ in range(DAYS):
        npos = nneg = 0
        for e, tie in cases:
            eh = abs(rng.gauss(0.0, s3)) if null == "normal" else e3[rng.randrange(len(e3))]
            d = eh - e
            if d > tie:
                npos += 1
            elif d < -tie:
                nneg += 1
        if npos + nneg < TOO_FEW:
            cnt["TOO FEW"] += 1
            continue
        p = sign_p(npos, nneg)
        cnt[("LARGER HERE" if npos > nneg else "SMALLER HERE") if p < 0.05 else "NOT DECIDED"] += 1
    return {k: round(v / DAYS, 4) for k, v in cnt.items()}


def shape(cases):
    e = sorted(x for x, _ in cases)
    n = len(e)
    rms = math.sqrt(sum(x * x for x in e) / n)
    med = (e[n // 2] if n % 2 else 0.5 * (e[n // 2 - 1] + e[n // 2]))
    return {"n": n, "rms_pct": round(100 * rms, 3), "median_abs_pct": round(100 * med, 3), "normal_median_abs_pct": round(100 * 0.6745 * rms, 3)}


def make(lab, out):
    rp = os.path.join(lab, "tools", "claims-v3", "e220", "rules-e220.json")
    raw = open(rp, "rb").read()
    R = json.loads(raw)
    rng = random.Random(int(hashlib.sha256(SEED.encode()).hexdigest()[:16], 16))
    res = {"what": "E220 dated note 1 (fix-e220): the cross-card test's verdict rates under two nulls, before any E220 datum (REPORTED; no rule changes)",
           "rules_e220_json_sha256": hashlib.sha256(raw).hexdigest(), "days": DAYS, "seed": SEED, "interpreter": sys.version.split()[0],
           "tests": {}}
    per = {}
    for arm in ("A", "B"):
        ties = R["arms"][arm]["ties"]
        for cid, q, tie in (("CX-E", "Wg", ties["joules_ln"]), ("CX-T", "wall", ties["cycles_ln"])):
            tw = twins(R, arm, q)
            cases = [(e, tie) for _, e in tw]
            per[(arm, q)] = cases
            reg = (R["arms"][arm]["cross_card"].get("power_REPORTED", {}).get(q) or {}).get("k=1.0")
            res["tests"][f"{arm}:{cid}"] = {"twins": [p for p, _ in tw], "tie_ln": tie, "shape": shape(cases),
                                            "normal": simulate(cases, "normal", rng), "resampled": simulate(cases, "resampled", rng),
                                            "registered_k1_REPORTED": reg}
    for cid, q in (("CXP-E", "Wg"), ("CXP-T", "wall")):
        cases = per[("A", q)] + per[("B", q)]
        res["tests"][cid] = {"n_cases": len(cases), "shape": shape(cases), "normal": simulate(cases, "normal", rng),
                             "resampled": simulate(cases, "resampled", rng), "registered_k1_REPORTED": None}
    json.dump(res, open(out, "x"), indent=1, sort_keys=True)
    for k, v in res["tests"].items():
        s = v["shape"]
        print(f"{k}: n {s['n']}, rms {s['rms_pct']}%, median |e| {s['median_abs_pct']}% (a normal error of that rms: {s['normal_median_abs_pct']}%); "
              f"false LARGER HERE: resampled {v['resampled']['LARGER HERE']}, normal {v['normal']['LARGER HERE']} "
              f"(registered k=1: {(v['registered_k1_REPORTED'] or {}).get('LARGER HERE', 'none registered')})")
    print(f"CX-NULL-E220-NOTE1: written {out} ({DAYS} days a test; rules-e220.json {res['rules_e220_json_sha256'][:12]})")
    return 0


def beside(scores, note):
    S = json.load(open(scores))
    N = json.load(open(note))["tests"]
    V = S.get("verdicts", {})
    rows = []
    for key in ("A:CX-E", "B:CX-E", "CXP-E", "A:CX-T", "B:CX-T", "CXP-T"):
        if key not in V:
            continue
        if ":" in key:
            arm, cid = key.split(":")
            d = S.get("arms", {}).get(arm, {}).get("cross_card", {}).get(cid, {})
        else:
            d = S.get("pooled", {}).get(key, {})
        t = N.get(key, {})
        reg = (t.get("registered_k1_REPORTED") or {}).get("LARGER HERE")
        rows.append(f"{key}: {V[key]} ({d.get('n', 0)} twins, {d.get('first_closer', 0)} larger here, {d.get('second_closer', 0)} larger on "
                    f"aifoundry3, p {d.get('p', 'none')}) | dated note 1: false LARGER HERE at equal distribution "
                    f"{t.get('resampled', {}).get('LARGER HERE')} (resampled aifoundry3 errors), at equal rms with normal errors "
                    f"{t.get('normal', {}).get('LARGER HERE')}" + (f" (registered {reg})" if reg is not None else ""))
    for r in rows:
        print(r)
    print(f"CX-BESIDE-E220-NOTE1: {len(rows)} cross-card verdict(s) printed with the null rates beside")
    return 0


def selftest(tmp, note):
    """beside on a stand-in scorer output in score_e220.py's form (six cross-card verdicts and one other rule), and on a missing file"""
    import subprocess
    os.makedirs(tmp)
    S = {"verdicts": {"A:CX-E": "LARGER HERE", "A:CX-T": "NOT DECIDED", "B:CX-E": "TOO FEW", "B:CX-T": "SMALLER HERE", "CXP-E": "LARGER HERE",
                      "CXP-T": "NOT DECIDED", "A:E1": "PASS"},
         "arms": {"A": {"cross_card": {"CX-E": {"verdict": "LARGER HERE", "n": 41, "first_closer": 30, "second_closer": 9, "ties": 2, "p": 0.001},
                                       "CX-T": {"verdict": "NOT DECIDED", "n": 52, "first_closer": 27, "second_closer": 23, "ties": 2, "p": 0.67}}},
                  "B": {"cross_card": {"CX-E": {"verdict": "TOO FEW", "n": 9, "first_closer": 5, "second_closer": 3, "ties": 1},
                                       "CX-T": {"verdict": "SMALLER HERE", "n": 42, "first_closer": 10, "second_closer": 30, "ties": 2, "p": 0.002}}}},
         "pooled": {"CXP-E": {"verdict": "LARGER HERE", "n": 50, "first_closer": 35, "second_closer": 12, "ties": 3, "p": 0.001},
                    "CXP-T": {"verdict": "NOT DECIDED", "n": 94, "first_closer": 47, "second_closer": 45, "ties": 2, "p": 0.9}}}
    sp = os.path.join(tmp, "scores-standin.json")
    json.dump(S, open(sp, "w"))
    r = subprocess.run([sys.executable, "-I", "-B", os.path.abspath(__file__), "beside", sp, note], capture_output=True, text=True)
    o = r.stdout
    N = json.load(open(note))["tests"]
    ok = (r.returncode == 0 and "CX-BESIDE-E220-NOTE1: 6 cross-card verdict(s)" in o
          and ("A:CX-E: LARGER HERE (41 twins, 30 larger here, 9 larger on aifoundry3, p 0.001) | dated note 1: false LARGER HERE at equal "
               f"distribution {N['A:CX-E']['resampled']['LARGER HERE']}") in o
          and "B:CX-E: TOO FEW (9 twins" in o and "CXP-E: LARGER HERE (50 twins" in o and "(registered 0.095)" in o and "(registered 0.331)" in o
          and "A:E1" not in o)
    print(o.strip())
    print(f"{'PASS' if ok else 'FAIL'} BESIDE the six cross-card verdicts of a stand-in scorer output printed with the note's rates beside them "
          f"(the registered k = 1 figures where registered; no other rule printed)")
    r2 = subprocess.run([sys.executable, "-I", "-B", os.path.abspath(__file__), "beside", os.path.join(tmp, "missing.json"), note],
                        capture_output=True, text=True)
    ok2 = r2.returncode != 0
    print(f"{'PASS' if ok2 else 'FAIL'} BESIDE-MISSING a missing scorer output: a non-zero exit (rc {r2.returncode})")
    print(f"SELFTEST-BESIDE-E220-NOTE1 {int(ok) + int(ok2)} of 2 PASS")
    return 0 if ok and ok2 else 1


def main(a):
    if len(a) == 3 and a[0] == "make":
        return make(os.path.abspath(a[1]), os.path.abspath(a[2]))
    if len(a) == 2 and a[0] == "selftest":
        return selftest(os.path.abspath(a[1]), os.path.join(os.path.dirname(os.path.abspath(__file__)), "cx-null-e220-note1.json"))
    if len(a) in (2, 3) and a[0] == "beside":
        note = a[2] if len(a) == 3 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "cx-null-e220-note1.json")
        return beside(a[1], note)
    print(__doc__)
    return 10


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
