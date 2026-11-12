#!/usr/bin/env python3
"""E188 (Q165, the kit): the reader of october-forecast-model's two frozen versions, v8 and v9, as REPORTED arms for E188 (E188.md section
8), never a rule. It is E186's note M2 reader v2 (tools/claims-v3/e186/arm_m2_read_e186_v2.py) in E188's form: the same words per item,
its finite-number and C-kept guards and its strict json, with three changes:
  1. THE MODEL'S SIDE is E188's registered ofm-e188.json (878b6f63), refused (exit 2) unless its sha256 is the registration list's pin; its
     two arms, v8 and v9, each with its freeze line verbatim, its seven trains and its kinds-pass items, each item with its frozen label
     ("blind": frozen before any session read the train; "post hoc": a committed session read these words before the freeze), copied to
     the output beside every reading;
  2. THE MEASURED SIDE is score_e188.py's file: "trains" > <train id> > the interval (mean, lo, hi; lo null when the scorer reads it NOT
     SCORED), and, when FULL's kinds passes ran, "reported" > "kinds_vs_ones" > <kind key> > the kind's per-segment contrast over fp32.ones
     (mean, lo, hi) and "reported" > "tie" > "tie_minus_ones" for the built-in pi; a kinds-pass item's measured side is its contrast, as the
     arm's figure is a level above 1.0 x 1.0;
  3. NO SUMMARY: per item only (its words and its error); no count inside, no mean or rms error over items. Its output carries readings of
     a reported arm, which the tier keeps private: it is written where the gate puts it (check_arms_e188.py: outside the lab repo), and
     public records name the arms by their committed files only (ofm-e188.json, this reader, its self-test).
THE WORDS, for each arm and item: the arm's centre lies inside / above / below the measured 95% interval; its sign is the estimate's or the
other (none to compare when either is 0); the measured estimate lies inside / above / below the arm's band; the error is the arm's figure
less the measured one, W. An item the arm does not cover reads "not covered", one the session did not run "not run", one the scorer reads
NOT SCORED, or whose figure is not a finite number, "not read". Exit 0 when written; 2 the model's file is off its pin; 3 the scorer's
file has no "trains"; 4 a non-finite number left to write (nothing written).

    /usr/bin/python3 -B tools/claims-v3/e188/arm_read_e188.py --scored <data dir>/scored-e188.json --out <a stem outside the repo>
    (writes <stem>.json and <stem>.txt)
Standard library only. SPDX-License-Identifier: Apache-2.0
"""
import argparse
import hashlib
import json
import math
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
OFM = os.path.join(HERE, "ofm-e188.json")
OFM_SHA256 = "779e2cfbd7815ca1508cfa08dc2abf8d31a4d4f132d3257a074971023c46600b"   # SHA256SUMS-e188-registration's (878b6f63)
KINDS_PASS_KEYS = {"1.0 x 1.0": "fp32.ones", "4.0 x 4.0": "fp32.e178_v4", "5.0 x 5.0": "fp32.e178_v5", "pi x pi (tile)": "fp32.pi",
                   "BALL (1.0, 0x3fffffff)": "fp32.e182_a1_b3fffffff", "AALL (0x3fffffff, 1.0)": "fp32.e182_a3fffffff_b1",
                   "lq_h0": "fp32.lq_h0", "aq_h0": "fp32.aq_h0", "pi x pi (the tie, built-in)": "anchor_pi"}
ARMS = ("v8", "v9")


def finite(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x)


def where(x, lo, hi):
    return "inside" if lo <= x <= hi else ("above" if x > hi else "below")


def sign_word(m, est):
    if m == 0 or est == 0:
        return "no sign to compare"
    return "the estimate's sign" if (m > 0) == (est > 0) else "the other sign"


def one(model, iv, label, what):
    """one item: model = {W, band95_W}; iv = the measured interval or None"""
    if iv is None:
        return {"reading": "not run", "model_W": model["W"], "label": label}
    if iv.get("lo") is None or iv.get("hi") is None or iv.get("mean") is None:
        return {"reading": "not read", "why": iv.get("why") or f"NOT SCORED by the scorer ({what})", "model_W": model["W"], "label": label}
    if not all(finite(iv[k]) for k in ("mean", "lo", "hi")):
        return {"reading": "not read", "why": "a non-finite figure in the scorer's interval (mean, lo or hi)", "model_W": model["W"], "label": label}
    blo, bhi = model["band95_W"]
    return {"reading": "read", "label": label, "model_W": model["W"], "model_band_W": [blo, bhi], "estimate": iv["mean"], "lo": iv["lo"],
            "hi": iv["hi"], "model_in_interval": where(model["W"], iv["lo"], iv["hi"]), "sign": sign_word(model["W"], iv["mean"]),
            "estimate_in_model_band": where(iv["mean"], blo, bhi), "error_W": model["W"] - iv["mean"]}


def read_arm(scored, arm):
    tr = scored["trains"]
    rep = scored.get("reported") or {}
    kvo = rep.get("kinds_vs_ones") or {}
    tie = (rep.get("tie") or {}).get("tie_minus_ones")
    out = {"freeze_line": arm["freeze_line"], "trains": {}, "kinds_pass": {}, "counts": {}}
    for tid in sorted(arm["trains"]):
        v = arm["trains"][tid]
        out["trains"][tid] = one(v, tr.get(tid), v["label"], "its train rule")
    for name in sorted(KINDS_PASS_KEYS):
        if name == "1.0 x 1.0":
            continue                                    # the reference: every contrast is read over it
        v = arm["kinds_pass"].get(name)
        if v is None:
            out["kinds_pass"][name] = {"reading": "not covered"}
            continue
        key = KINDS_PASS_KEYS[name]
        iv = tie if key == "anchor_pi" else kvo.get(key)
        if iv is not None and not iv.get("segments", 1) and key != "anchor_pi":
            iv = None
        if key == "anchor_pi" and iv is not None and not (rep.get("tie") or {}).get("passes"):
            iv = None
        out["kinds_pass"][name] = one(v, iv, v["label"], "its contrast")
    for sec in ("trains", "kinds_pass"):
        c = {}
        for x in out[sec].values():
            c[x["reading"]] = c.get(x["reading"], 0) + 1
        out["counts"][sec] = c
    return out


def read(scored, ofm):
    return {"_what": "october-forecast-model's v8 and v9 as reported arms for E188 (arm_read_e188.py; E188.md section 8), never a rule; "
                     "per item only, no summary; the readings of a reported arm are kept private by the tier",
            "units": ofm["units"], "labels": ofm["labels"], "arms": {a: read_arm(scored, ofm[a]) for a in ARMS}}


def text(o):
    L = ["october-forecast-model v8 and v9, reported arms for E188 (never a rule; per item, no summary)", ""]
    for a in ARMS:
        r = o["arms"][a]
        L.append(f"arm {a}: {r['freeze_line']}")
        for sec in ("trains", "kinds_pass"):
            L.append(f"  {sec}: " + json.dumps(r["counts"][sec], sort_keys=True))
            for k, v in r[sec].items():
                if v["reading"] == "read":
                    L.append(f"    {k} ({v['label']}): model {v['model_W']:+.4f} [{v['model_band_W'][0]:+.4f}, {v['model_band_W'][1]:+.4f}]; measured "
                             f"{v['estimate']:+.4f} [{v['lo']:+.4f}, {v['hi']:+.4f}]: the model {v['model_in_interval']} the interval, {v['sign']}; "
                             f"the estimate {v['estimate_in_model_band']} the model's band; error {v['error_W']:+.4f}")
                elif v["reading"] != "not covered":
                    L.append(f"    {k}: {v['reading']}" + (f" ({v['why']})" if v.get("why") else ""))
        L.append("")
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scored", required=True)
    ap.add_argument("--out", required=True, help="an output stem: <stem>.json and <stem>.txt")
    ap.add_argument("--model", default=OFM)
    a = ap.parse_args()
    raw = open(a.model, "rb").read()
    if hashlib.sha256(raw).hexdigest() != OFM_SHA256:
        print("REFUSED: the model's file is not ofm-e188.json as E188's registration pins it")
        return 2
    ofm = json.loads(raw)
    sc = json.load(open(a.scored))
    if not isinstance(sc.get("trains"), dict):
        print("REFUSED: the scorer's file has no trains")
        return 3
    o = read(sc, ofm)
    try:
        js = json.dumps(o, indent=1, sort_keys=True, allow_nan=False) + "\n"
    except ValueError:
        print("REFUSED: a non-finite number is left to write (nothing written)")
        return 4
    t = text(o)
    open(a.out + ".json", "w").write(js)
    open(a.out + ".txt", "w").write(t)
    print(t)
    return 0


if __name__ == "__main__":
    sys.exit(main())
