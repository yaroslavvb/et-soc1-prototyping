#!/usr/bin/env python3
"""E164 (Q141(b)): M9's nested leave-one-kind-out error of every training row, the reference distribution of E164's P1-P3 and B1-B2
rules (E164.md, Decision rules), as ref_errors_e157.py took M8's. Q140(m)'s fit_m9.py wrote each row's nested error into its committed
rows-m9.json (`M9_nested_err_w`); this script recomputes them with Q140(m)'s own code, unchanged: fit_m9.run_family on the committed
rows (855, in rows-m9.json's order, split into the float and int8 families as fit_m9.main splits them), whose third return value is
the nested `outer` residual array. It refuses to write unless every recomputed row equals the committed `M9_nested_err_w` (to 1e-9 W)
and every pool's rms and n equal nested-m9.json's band pools (to 1e-9 W). Desk only: nothing here reads pool 7 or any card data.
Needs numpy (fit_m9's); run it with nice -n 10 and at most two BLAS threads (the variables below are set before numpy loads).

    python3 -B tools/claims-v3/e164/ref_errors_e164.py [--out tools/claims-v3/e164/ref-errors-m9.json]
SPDX-License-Identifier: Apache-2.0
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[_v] = "2"
import hashlib  # noqa: E402
import json  # noqa: E402
import math  # noqa: E402
import sys  # noqa: E402

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
Q140M = os.path.join(ROOT, "docs", "reports", "data", "2026-11-04-q140m-m9")
sys.path.insert(0, Q140M)
import fit_m9 as F9  # noqa: E402  (Q140(m)'s frozen fit code, unchanged; it imports fit_m8, fit_m7, fit_m6 unchanged)

PINNED = {   # the committed inputs (lab 1f244140), refused if they differ
    "docs/reports/data/2026-11-04-q140m-m9/fit_m9.py": "0b3f1074c4a84865dd2f6e6e4e018a56ce28e016b22b6fbfd66b74a1520752f5",
    "docs/reports/data/2026-11-04-q140m-m9/rows-m9.json": "96ec405065257a543f7385711ad1841eb37316cc0148c362f35727534d05d41e",
    "docs/reports/data/2026-11-04-q140m-m9/nested-m9.json": "f6057e3b9f055d538182485756fbe7cde27f96f8af7617085314d68ebada44a0",
    "docs/reports/data/2026-11-04-q140m-m9/m9.json": "322dd73983cb293aebfb7894eb868e7d0b650ae36d30d5626bba283be25e4835",
}


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def main():
    out = os.path.join(HERE, "ref-errors-m9.json")
    if "--out" in sys.argv:
        out = sys.argv[sys.argv.index("--out") + 1]
    bad = [f"{rel}: {sha(os.path.join(ROOT, rel))} != {w}" for rel, w in PINNED.items() if sha(os.path.join(ROOT, rel)) != w]
    if bad:
        raise SystemExit("refusing - a frozen input differs from lab 1f244140:\n  " + "\n  ".join(bad))
    rows = json.load(open(os.path.join(Q140M, "rows-m9.json")))
    nested = json.load(open(os.path.join(Q140M, "nested-m9.json")))
    m6 = F9.load(os.path.join(F9.M7.M6D, "m6.json"))
    m7 = F9.load(os.path.join(F9.M8.M7D, "m7.json"))
    m8 = F9.load(os.path.join(F9.M8D, "m8.json"))
    res = {"_note": "E164: M9's nested leave-one-kind-out errors (measured - predicted, W) of every row of rows-m9.json, recomputed "
                    "with Q140(m)'s fit_m9.run_family unchanged; every row equals the committed M9_nested_err_w and every pool's "
                    "rms and n equal nested-m9.json's band pools (checked to 1e-9 W)",
           "sha256": dict(PINNED), "families": {}, "card1_by_format": {}, "aifoundry3_by_format": {}, "both_cards_by_format": {}}
    bad = []
    worst_row = 0.0
    for famname, want in (("float", lambda r: r["type"] != "int8"), ("int8", lambda r: r["type"] == "int8")):
        fr = [r for r in rows if want(r)]
        _, _, outer, _, _, _ = F9.run_family(fr, famname, m6, m7, m8, lambda s: print(s, flush=True))
        errs = []
        for i, r in enumerate(fr):
            e = float(outer[i])
            c = r.get("M9_nested_err_w")
            if not (math.isnan(e) and (c is None or (isinstance(c, float) and math.isnan(c)))):
                d = abs(e - float(c)) if c is not None else float("inf")
                worst_row = max(worst_row, d)
                if d > 1e-9:
                    bad.append(f"{famname} row {i} {r['exp']} {r['card']} {r['key']}: recomputed {e} != committed {c}")
            errs.append({"exp": r["exp"], "card": r["card"], "key": r["key"], "type": r["type"], "err_w": e})
        check = {}
        for key, p in nested["families"][famname]["band"]["pools"].items():
            t, cd = key.split("|")
            ev = [x["err_w"] for x in errs if x["type"] == t and x["card"] == cd and not math.isnan(x["err_w"])]
            r_ = math.sqrt(sum(v * v for v in ev) / len(ev)) if ev else None
            check[key] = {"n": len(ev), "rms_w": r_, "frozen_n": p["n"], "frozen_rms_w": p["rms_w"]}
            if len(ev) != p["n"] or r_ is None or abs(r_ - p["rms_w"]) > 1e-9:
                bad.append(f"{famname} {key}: n {len(ev)} rms {r_} != frozen n {p['n']} rms {p['rms_w']}")
        res["families"][famname] = {"pool_check": check, "row_errors": errs}
        for x in errs:
            if math.isnan(x["err_w"]):
                continue
            res["both_cards_by_format"].setdefault(x["type"], []).append(x["err_w"])
            res[{"c1": "card1_by_format", "a3": "aifoundry3_by_format"}[x["card"]]].setdefault(x["type"], []).append(x["err_w"])
        print(famname, json.dumps(check), flush=True)
    if bad:
        raise SystemExit("refusing to write - the recomputed errors differ from the committed ones:\n  " + "\n  ".join(bad[:20]))
    res["worst_row_difference_w"] = worst_row
    res["n"] = {"card1": {t: len(v) for t, v in res["card1_by_format"].items()},
                "aifoundry3": {t: len(v) for t, v in res["aifoundry3_by_format"].items()},
                "both": {t: len(v) for t, v in res["both_cards_by_format"].items()}}
    json.dump(res, open(out, "w"), indent=1)
    print("wrote", out, json.dumps(res["n"]), f"worst row difference {worst_row:.3g} W")


if __name__ == "__main__":
    main()
