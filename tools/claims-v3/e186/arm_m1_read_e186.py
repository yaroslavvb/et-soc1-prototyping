#!/usr/bin/env python3
"""E186 (Q158): october-forecast-model v4's REPORTED arm for E186, read by E186.md.dated-note-M1.md section M1-4's words. Never a rule.

    /usr/bin/python3 -B tools/claims-v3/e186/arm_m1_read_e186.py --scored <data dir>/scored-e186.json --out <data dir>/arm-m1-e186
    (writes arm-m1-e186.json and arm-m1-e186.txt)

THE MEASURED SIDE is the scorer's file in E182's scored.json form, which E186's kit ports: "trains" > <train id> > the train's interval
(mean, lo, hi, se, n, df, hw; lo null when the scorer reads it NOT SCORED), and, when kinds passes ran, "reported" > "kinds" > <kind key> >
D_w (the kind's mean D over its kept passes). THE MODEL'S SIDE is m1-october-forecast-model-e186.json beside this file, refused (exit 2)
unless its sha256 is the one pinned here. THE WORDS, never the scorer's verdict words: the model's central lies inside / above / below the
measured 95% interval; its sign is the estimate's or the other (none to compare when either is 0); the measured estimate lies inside /
above / below the model's band. A train or kind the model does not cover reads "not covered", one the session did not run "not run", one
the scorer reads NOT SCORED "not read". Card 1's figures are never read. Exit 0 when written; 2 the model's file differs; 3 the scorer's
file has no "trains".
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
M1_JSON = os.path.join(HERE, "m1-october-forecast-model-e186.json")
M1_SHA256 = "bf9a1b02b3e7e42c82c79e86894604e3fddac486b2a62dd530b9b40778dee13a"


def where(x, lo, hi):
    return "inside" if lo <= x <= hi else ("above" if x > hi else "below")


def sign_word(m, est):
    if m == 0 or est == 0:
        return "no sign to compare"
    return "the estimate's sign" if (m > 0) == (est > 0) else "the other sign"


def read(scored, m1):
    out = {"_what": "october-forecast-model v4's reported arm for E186 (arm_m1_read_e186.py; E186.md.dated-note-M1.md section M1-4), never a rule",
           "freeze_line": m1["freeze_line"], "trains": {}, "kinds": {}, "counts": {}}
    tr = scored["trains"]
    for tid, v in sorted(m1["trains"].items()):
        if not v["covered"]:
            out["trains"][tid] = {"reading": "not covered"}
            continue
        if tid not in tr:
            out["trains"][tid] = {"reading": "not run", "v4_W": v["v4_W"]}
            continue
        iv = tr[tid]
        if iv.get("lo") is None:
            out["trains"][tid] = {"reading": "not read", "why": "NOT SCORED by the scorer", "v4_W": v["v4_W"]}
            continue
        blo, bhi = v["v4_band"]
        out["trains"][tid] = {"reading": "read", "v4_W": v["v4_W"], "v4_band": v["v4_band"], "estimate": iv["mean"], "lo": iv["lo"], "hi": iv["hi"],
                              "model_in_interval": where(v["v4_W"], iv["lo"], iv["hi"]), "sign": sign_word(v["v4_W"], iv["mean"]),
                              "estimate_in_model_band": where(iv["mean"], blo, bhi)}
    kd = (scored.get("reported") or {}).get("kinds") or {}
    for kid, v in sorted(m1["kinds"].items()):
        if not v["covered"]:
            out["kinds"][kid] = {"key": v["key"], "reading": "not covered"}
            continue
        r = kd.get(v["key"])
        if r is None or r.get("D_w") is None:
            out["kinds"][kid] = {"key": v["key"], "reading": "not run", "v4_W": v["v4_W"]}
            continue
        blo, bhi = v["v4_band"]
        out["kinds"][kid] = {"key": v["key"], "reading": "read", "v4_W": v["v4_W"], "D_w": r["D_w"], "D_minus_v4_w": r["D_w"] - v["v4_W"],
                             "measured_in_model_band": where(r["D_w"], blo, bhi)}
    for sec in ("trains", "kinds"):
        c = {}
        for x in out[sec].values():
            c[x["reading"]] = c.get(x["reading"], 0) + 1
        out["counts"][sec] = c
    return out


def text(o):
    L = ["october-forecast-model v4's reported arm for E186 (never a rule): " + o["freeze_line"], "",
         "trains: " + json.dumps(o["counts"]["trains"], sort_keys=True)]
    for tid, v in o["trains"].items():
        if v["reading"] == "read":
            L.append(f"  {tid:9s} v4 {v['v4_W']:+.4f} [{v['v4_band'][0]:+.4f}, {v['v4_band'][1]:+.4f}]  measured {v['estimate']:+.4f} [{v['lo']:+.4f}, "
                     f"{v['hi']:+.4f}]: v4 {v['model_in_interval']} the interval, {v['sign']}; the estimate {v['estimate_in_model_band']} v4's band")
        else:
            L.append(f"  {tid:9s} {v['reading']}")
    L.append("kinds: " + json.dumps(o["counts"]["kinds"], sort_keys=True))
    for kid, v in o["kinds"].items():
        if v["reading"] == "read":
            L.append(f"  {kid} {v['key']:28s} v4 {v['v4_W']:.4f}  measured {v['D_w']:.4f}: {v['measured_in_model_band']} v4's band")
        elif v["reading"] != "not covered":
            L.append(f"  {kid} {v['key']:28s} {v['reading']}")
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scored", required=True)
    ap.add_argument("--out", required=True, help="an output stem: <stem>.json and <stem>.txt")
    ap.add_argument("--model", default=M1_JSON)
    a = ap.parse_args()
    raw = open(a.model, "rb").read()
    if hashlib.sha256(raw).hexdigest() != M1_SHA256:
        print("REFUSED: the model's file is not the one note M1 pins")
        return 2
    sc = json.load(open(a.scored))
    if not isinstance(sc.get("trains"), dict):
        print("REFUSED: the scorer's file has no trains")
        return 3
    o = read(sc, json.loads(raw))
    open(a.out + ".json", "w").write(json.dumps(o, indent=1, sort_keys=True) + "\n")
    open(a.out + ".txt", "w").write(text(o))
    print(text(o))
    return 0


if __name__ == "__main__":
    sys.exit(main())
