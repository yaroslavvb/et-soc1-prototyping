#!/usr/bin/env python3
"""E157 (Q139): M8's nested leave-one-kind-out error of every training row, the reference distribution of E157's P1-P3 and B1-B2 rules, as
E142 took M7's card-1 rows from loko-m7.json > families.<family>.row_errors. Q139(m) committed M8's nested rms by format and card
(nested-m8.json > families.<f>.band.pools) but not the per-row errors, so this script recomputes them with Q139(m)'s own code, unchanged:
fit_m8.run_family on the committed rows-m8.json (the rows fit_m8.assemble wrote, 767), whose third return value is the nested `outer`
residual array the frozen pools were computed from. It checks that every pool's rms and n equal nested-m8.json's (to 1e-9 W) and refuses
to write otherwise. E153 (aifoundry3) takes its reference the same way (tools/claims-v3/e153/ref_errors_e153.py); this is E157's own copy
of the method, card 1's rows. Desk only; nothing here reads pool 6 or any card data. Needs numpy (fit_m8's).

    python3 tools/claims-v3/e157/ref_errors_e157.py [--out tools/claims-v3/e157/ref-errors-m8.json]
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
Q139M = os.path.join(ROOT, "docs", "reports", "data", "2026-11-03-q139m-model")
sys.path.insert(0, Q139M)
import fit_m8 as F8  # noqa: E402  (Q139(m)'s frozen fit code, unchanged)


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def main():
    out = os.path.join(HERE, "ref-errors-m8.json")
    if "--out" in sys.argv:
        out = sys.argv[sys.argv.index("--out") + 1]
    rows = json.load(open(os.path.join(Q139M, "rows-m8.json")))
    nested = json.load(open(os.path.join(Q139M, "nested-m8.json")))
    m6 = json.load(open(os.path.join(F8.M7.M6D, "m6.json")))
    m7 = json.load(open(os.path.join(F8.M7D, "m7.json")))
    res = {"_note": "E157: M8's nested leave-one-kind-out errors (measured - predicted, W) of every row of rows-m8.json, from Q139(m)'s "
                    "fit_m8.run_family unchanged; every pool's rms and n equal nested-m8.json's (checked to 1e-9 W)",
           "sha256": {rel: sha(os.path.join(ROOT, rel)) for rel in (
               "docs/reports/data/2026-11-03-q139m-model/fit_m8.py", "docs/reports/data/2026-11-03-q139m-model/rows-m8.json",
               "docs/reports/data/2026-11-03-q139m-model/nested-m8.json", "docs/reports/data/2026-11-03-q139m-model/m8.json")},
           "families": {}, "card1_by_format": {}, "both_cards_by_format": {}}
    bad = []
    for famname, want in (("float", lambda r: r["type"] != "int8"), ("int8", lambda r: r["type"] == "int8")):
        fr = [r for r in rows if want(r)]
        _, _, outer = F8.run_family(fr, famname, m6, m7)
        errs = [{"exp": r["exp"], "card": r["card"], "key": r["key"], "type": r["type"], "err_w": float(outer[i])}
                for i, r in enumerate(fr)]
        check = {}
        for key, p in nested["families"][famname]["band"]["pools"].items():
            t, cd = key.split("|")
            e = [x["err_w"] for x in errs if x["type"] == t and x["card"] == cd and not math.isnan(x["err_w"])]
            r_ = math.sqrt(sum(v * v for v in e) / len(e)) if e else None
            check[key] = {"n": len(e), "rms_w": r_, "frozen_n": p["n"], "frozen_rms_w": p["rms_w"]}
            if len(e) != p["n"] or r_ is None or abs(r_ - p["rms_w"]) > 1e-9:
                bad.append(f"{famname} {key}: n {len(e)} rms {r_} != frozen n {p['n']} rms {p['rms_w']}")
        res["families"][famname] = {"pool_check": check, "row_errors": errs}
        for x in errs:
            if math.isnan(x["err_w"]):
                continue
            res["both_cards_by_format"].setdefault(x["type"], []).append(x["err_w"])
            if x["card"] == "c1":
                res["card1_by_format"].setdefault(x["type"], []).append(x["err_w"])
        print(famname, json.dumps(check))
    if bad:
        raise SystemExit("refusing to write - the recomputed pools differ from nested-m8.json:\n  " + "\n  ".join(bad))
    res["n"] = {"card1": {t: len(v) for t, v in res["card1_by_format"].items()},
                "both": {t: len(v) for t, v in res["both_cards_by_format"].items()}}
    json.dump(res, open(out, "w"), indent=1)
    print("wrote", out, json.dumps(res["n"]))


if __name__ == "__main__":
    main()
