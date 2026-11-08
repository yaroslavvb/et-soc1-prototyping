#!/usr/bin/env python3
"""E186 (Q158): october-forecast-model's later versions as four REPORTED arms for E186 (v4 on M12's set, v5, v6 and v7), read by
E186.md.dated-note-M2.md section M2-5's words. Never a rule. It is note M1's reader (arm_m1_read_e186.py) in form, for four arms at once,
with each arm's errors written beside its words.

    /usr/bin/python3 -B tools/claims-v3/e186/arm_m2_read_e186.py --scored <data dir>/scored-e186.json --out <data dir>/arm-m2-e186
    (writes arm-m2-e186.json and arm-m2-e186.txt)

THE MEASURED SIDE is the session's reduced trains and kinds as the scorer's file carries them, in E182's scored.json form: "trains" >
<train id> > the train's interval (mean, lo, hi; lo null when the scorer reads it NOT SCORED), and, when kinds passes ran, "reported" >
"kinds" > <kind key> > D_w (the kind's mean D over its kept passes). THE MODEL'S SIDE is m2-october-forecast-model-e186.json beside this
file, refused (exit 2) unless its sha256 is the one pinned here; each kind's key is read from E186's list
(tools/claims-v3/m12/kinds-m12-e186.json, 80d53792), refused (exit 2) unless its sha256 is pinned here too and its words are the json's.
THE WORDS, for each arm, are note M1's: the arm's centre lies inside / above / below the measured 95% interval; its sign is the estimate's
or the other (none to compare when either is 0); the measured estimate lies inside / above / below the arm's band; a kind's measured D
lies inside / above / below the arm's band. A train or kind the arm does not cover reads "not covered", one the session did not run "not
run", one the scorer reads NOT SCORED "not read". THE ERRORS beside: the arm's figure less the measured one, in W, for every train and kind
read, and over each arm's trains read (and kinds read) the count, the count inside, the mean error and the rms error. Card 1's figures are
never read. Exit 0 when written; 2 a pinned file differs; 3 the scorer's file has no "trains".
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import hashlib
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOP = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
M2_JSON = os.path.join(HERE, "m2-october-forecast-model-e186.json")
M2_SHA256 = "ab00ac052275cb4c0779275f16c381642e794256febf7495b9c0efd9bded92f2"
LIST = os.path.join(TOP, "tools", "claims-v3", "m12", "kinds-m12-e186.json")
LIST_SHA256 = "9af274eb1c10db3e8caa1800304b00b3b4078fac4fc567760808e8a63a96d80a"


def where(x, lo, hi):
    return "inside" if lo <= x <= hi else ("above" if x > hi else "below")


def sign_word(m, est):
    if m == 0 or est == 0:
        return "no sign to compare"
    return "the estimate's sign" if (m > 0) == (est > 0) else "the other sign"


def summary(errs, inside):
    if not errs:
        return {"n": 0, "inside": 0, "mean_error_W": None, "rms_error_W": None}
    return {"n": len(errs), "inside": inside, "mean_error_W": sum(errs) / len(errs), "rms_error_W": math.sqrt(sum(e * e for e in errs) / len(errs))}


def read_arm(scored, arm, keys):
    tr = scored["trains"]
    kd = (scored.get("reported") or {}).get("kinds") or {}
    out = {"freeze_line": arm["freeze_line"], "trains": {}, "kinds": {}, "counts": {}}
    te, ti, ke, ki = [], 0, [], 0
    for tid in sorted(arm["trains"]):
        v = arm["trains"][tid]
        if not v["covered"]:
            out["trains"][tid] = {"reading": "not covered"}
            continue
        if tid not in tr:
            out["trains"][tid] = {"reading": "not run", "model_W": v["W"]}
            continue
        iv = tr[tid]
        if iv.get("lo") is None or iv.get("hi") is None or iv.get("mean") is None:
            out["trains"][tid] = {"reading": "not read", "why": "NOT SCORED by the scorer", "model_W": v["W"]}
            continue
        blo, bhi = v["band_W"]
        w = where(v["W"], iv["lo"], iv["hi"])
        e = v["W"] - iv["mean"]
        out["trains"][tid] = {"reading": "read", "model_W": v["W"], "model_band_W": v["band_W"], "estimate": iv["mean"], "lo": iv["lo"],
                              "hi": iv["hi"], "model_in_interval": w, "sign": sign_word(v["W"], iv["mean"]),
                              "estimate_in_model_band": where(iv["mean"], blo, bhi), "error_W": e}
        te.append(e)
        ti += w == "inside"
    for kid in sorted(arm["kinds"]):
        v = arm["kinds"][kid]
        if not v["covered"]:
            out["kinds"][kid] = {"reading": "not covered"}
            continue
        r = kd.get(keys[kid])
        if r is None or r.get("D_w") is None:
            out["kinds"][kid] = {"reading": "not run", "model_W": v["W"]}
            continue
        blo, bhi = v["band_W"]
        w = where(r["D_w"], blo, bhi)
        e = v["W"] - r["D_w"]
        out["kinds"][kid] = {"reading": "read", "model_W": v["W"], "model_band_W": v["band_W"], "D_w": r["D_w"], "measured_in_model_band": w,
                             "error_W": e}
        ke.append(e)
        ki += w == "inside"
    for sec in ("trains", "kinds"):
        c = {}
        for x in out[sec].values():
            c[x["reading"]] = c.get(x["reading"], 0) + 1
        out["counts"][sec] = c
    out["errors"] = {"trains": summary(te, ti), "kinds": summary(ke, ki),
                     "what": "the arm's figure less the measured one, W; 'inside' counts the arm's centre inside the measured interval (trains) "
                             "and the measured D inside the arm's band (kinds)"}
    return out


def read(scored, m2, keys):
    return {"_what": "october-forecast-model's later versions as reported arms for E186 (arm_m2_read_e186.py; E186.md.dated-note-M2.md "
                     "section M2-5), never a rule",
            "arm_order": m2["arm_order"], "arms": {a: read_arm(scored, m2["arms"][a], keys) for a in m2["arm_order"]}}


def fmt(x):
    return "-" if x is None else f"{x:+.4f}"


def text(o):
    L = ["october-forecast-model's later versions, reported arms for E186 (never a rule)", ""]
    for a in o["arm_order"]:
        r = o["arms"][a]
        L.append(f"arm {a}: {r['freeze_line']}")
        L.append("  trains: " + json.dumps(r["counts"]["trains"], sort_keys=True))
        for tid, v in r["trains"].items():
            if v["reading"] == "read":
                L.append(f"    {tid:9s} model {v['model_W']:+.4f} [{v['model_band_W'][0]:+.4f}, {v['model_band_W'][1]:+.4f}]  measured {v['estimate']:+.4f} "
                         f"[{v['lo']:+.4f}, {v['hi']:+.4f}]: the model {v['model_in_interval']} the interval, {v['sign']}; the estimate "
                         f"{v['estimate_in_model_band']} the model's band; error {v['error_W']:+.4f}")
            elif v["reading"] != "not covered":
                L.append(f"    {tid:9s} {v['reading']}")
        L.append("  kinds: " + json.dumps(r["counts"]["kinds"], sort_keys=True))
        for kid, v in r["kinds"].items():
            if v["reading"] == "read":
                L.append(f"    {kid} model {v['model_W']:.4f} [{v['model_band_W'][0]:.4f}, {v['model_band_W'][1]:.4f}]  measured {v['D_w']:.4f}: "
                         f"{v['measured_in_model_band']} the model's band; error {v['error_W']:+.4f}")
            elif v["reading"] != "not covered":
                L.append(f"    {kid} {v['reading']}")
        et, ek = r["errors"]["trains"], r["errors"]["kinds"]
        L.append(f"  errors: trains read {et['n']}, the model inside {et['inside']}, mean {fmt(et['mean_error_W'])}, rms {fmt(et['rms_error_W'])}; "
                 f"kinds read {ek['n']}, inside the band {ek['inside']}, mean {fmt(ek['mean_error_W'])}, rms {fmt(ek['rms_error_W'])}")
        L.append("")
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scored", required=True)
    ap.add_argument("--out", required=True, help="an output stem: <stem>.json and <stem>.txt")
    ap.add_argument("--model", default=M2_JSON)
    ap.add_argument("--list", default=LIST)
    a = ap.parse_args()
    raw = open(a.model, "rb").read()
    if hashlib.sha256(raw).hexdigest() != M2_SHA256:
        print("REFUSED: the model's file is not the one note M2 pins")
        return 2
    lraw = open(a.list, "rb").read()
    if hashlib.sha256(lraw).hexdigest() != LIST_SHA256:
        print("REFUSED: E186's list is not the one note M2 pins")
        return 2
    m2 = json.loads(raw)
    lst = json.loads(lraw)
    keys = {}
    for k in lst["kinds"]:
        mk = m2["kinds"].get(k["e186_id"])
        if mk is None or (mk["a_word"], mk["b_word"], mk["type"]) != (k["a_word"].lower(), k["b_word"].lower(), k["type"]):
            print("REFUSED: E186's list and the model's file disagree on a kind's words")
            return 2
        keys[k["e186_id"]] = k["key"]
    if sorted(keys) != sorted(m2["kinds"]):
        print("REFUSED: E186's list and the model's file name different kinds")
        return 2
    sc = json.load(open(a.scored))
    if not isinstance(sc.get("trains"), dict):
        print("REFUSED: the scorer's file has no trains")
        return 3
    o = read(sc, m2, keys)
    open(a.out + ".json", "w").write(json.dumps(o, indent=1, sort_keys=True) + "\n")
    open(a.out + ".txt", "w").write(text(o))
    print(text(o))
    return 0


if __name__ == "__main__":
    sys.exit(main())
