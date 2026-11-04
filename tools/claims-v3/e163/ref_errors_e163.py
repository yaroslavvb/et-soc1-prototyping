#!/usr/bin/env python3
"""E163 (Q141): M9's nested leave-one-kind-out error of every training row, the reference distribution of E163's P1-P3 and B1-B2
rules, as tools/claims-v3/e153/ref_errors_e153.py made M8's for E153. Q140(m)'s fit_m9.main wrote each row's outer error into the
committed rows-m9.json (`M9_nested_err_w`: the nested procedure's error, the `outer` array its band pools were computed from), so this
script reads them there and checks that every pool's n and rms equal m9.json's and nested-m9.json's exactly (to 1e-9 W), refusing to
write otherwise. With --recompute it also re-runs Q140(m)'s own fit_m9.run_family, unchanged, on the committed rows and requires the
recomputed errors to equal the committed ones row by row (to 1e-9 W). Desk only; nothing here reads pool 7 or any card data.

    python3 -B tools/claims-v3/e163/ref_errors_e163.py [--recompute] [--out tools/claims-v3/e163/ref-errors-m9.json]

--recompute needs numpy and takes several minutes (the nested procedure's inner scores); set OMP_NUM_THREADS etc. to bound the
cores. SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
Q140M = os.path.join(ROOT, "docs", "reports", "data", "2026-11-04-q140m-m9")
REL = "docs/reports/data/2026-11-04-q140m-m9"
FROZEN = {f"{REL}/m9.json": "322dd73983cb293aebfb7894eb868e7d0b650ae36d30d5626bba283be25e4835"}


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def main():
    out = os.path.join(HERE, "ref-errors-m9.json")
    if "--out" in sys.argv:
        out = sys.argv[sys.argv.index("--out") + 1]
    for rel, want in FROZEN.items():
        have = sha(os.path.join(ROOT, rel))
        if have != want:
            raise SystemExit(f"{rel}: sha256 {have} != M9's frozen {want}")
    rows = json.load(open(os.path.join(Q140M, "rows-m9.json")))
    m9 = json.load(open(os.path.join(Q140M, "m9.json")))
    nested = json.load(open(os.path.join(Q140M, "nested-m9.json")))
    res = {"_note": "E163: M9's nested leave-one-kind-out errors (measured - predicted, W) of every row of rows-m9.json, as Q140(m)'s "
                    "fit_m9.main wrote them (M9_nested_err_w); every pool equals m9.json's and nested-m9.json's (checked)",
           "sha256": {f"{REL}/{f}": sha(os.path.join(Q140M, f)) for f in ("fit_m9.py", "rows-m9.json", "nested-m9.json", "m9.json")},
           "families": {}}
    bad = []
    recomputed = {}
    if "--recompute" in sys.argv:
        sys.path.insert(0, Q140M)
        import fit_m9 as F9  # noqa: E402  (Q140(m)'s frozen fit code, unchanged)
        m6 = json.load(open(os.path.join(F9.M7.M6D, "m6.json")))
        m7 = json.load(open(os.path.join(F9.M8.M7D, "m7.json")))
        m8 = json.load(open(os.path.join(F9.M8D, "m8.json")))
        for famname, want in (("float", lambda r: r["type"] != "int8"), ("int8", lambda r: r["type"] == "int8")):
            fr = [{k: v for k, v in r.items() if k != "M9_nested_err_w"} for r in rows if want(r)]
            _, _, outer, _, _, _ = F9.run_family(fr, famname, m6, m7, m8, lambda s: print(s, flush=True))
            recomputed[famname] = [float(x) for x in outer]
    for famname, want in (("float", lambda r: r["type"] != "int8"), ("int8", lambda r: r["type"] == "int8")):
        fr = [r for r in rows if want(r)]
        errs = [{"exp": r["exp"], "card": r["card"], "key": r["key"], "type": r["type"], "err_w": float(r["M9_nested_err_w"])} for r in fr]
        if famname in recomputed:
            worst = max(abs(a - e["err_w"]) for a, e in zip(recomputed[famname], errs) if not (math.isnan(a) and math.isnan(e["err_w"])))
            res.setdefault("recompute", {})[famname] = {"rows": len(errs), "max_abs_diff_w": worst}
            if worst > 1e-9:
                bad.append(f"{famname}: fit_m9.run_family recomputed errors differ from rows-m9.json by up to {worst} W")
        pools_m9 = m9["families"][famname]["interval_pool_by_format_card"]
        pools_nested = nested["families"][famname]["band"]["pools"]
        check = {}
        for key, p in pools_m9.items():
            t, cd = key.split("|")
            e = [x["err_w"] for x in errs if x["type"] == t and x["card"] == cd and not math.isnan(x["err_w"])]
            r_ = math.sqrt(sum(v * v for v in e) / len(e)) if e else None
            pn = pools_nested[key]
            check[key] = {"n": len(e), "rms_w": r_, "frozen_n": p["n"], "frozen_rms_w": p["rms_w"], "nested_n": pn["n"],
                          "nested_rms_w": pn["rms_w"]}
            if len(e) != p["n"] or r_ is None or abs(r_ - p["rms_w"]) > 1e-9 or pn["n"] != p["n"] or abs(pn["rms_w"] - p["rms_w"]) > 1e-12:
                bad.append(f"{famname} {key}: n {len(e)} rms {r_} != frozen n {p['n']} rms {p['rms_w']}")
        res["families"][famname] = {"pool_check": check, "row_errors": errs}
        print(famname, json.dumps(check))
    if bad:
        print("REFUSED: the nested errors do not reproduce M9's frozen pools:\n  " + "\n  ".join(bad))
        sys.exit(9)
    if recomputed:
        print("recompute:", json.dumps(res["recompute"]))
    json.dump(res, open(out, "w"), indent=0)
    print("wrote", os.path.relpath(out, ROOT) if out.startswith(ROOT) else out)


if __name__ == "__main__":
    main()
