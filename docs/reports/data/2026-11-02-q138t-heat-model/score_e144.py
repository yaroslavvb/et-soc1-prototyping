#!/usr/bin/env python3
"""Q138(t): score a heat session against the frozen chain (arm a) and the frozen predictions (arms b, c). No refit, no tuning.

aifoundry3 (E97's harness: one telemetry.jsonl.gz with the 34 raw codes, marks.jsonl with "rest" and "hold_start" marks):
    python3 score_e144.py a3 <pass dir> [<earlier pass dirs of the same session, in time order>...]
aifoundry2 (E133's harness: <step>/tel/REST-*.jsonl.gz, then the hold's file):
    python3 score_e144.py a2 <step dir> [<step dir> ...]
--self-test runs both on the committed E97 Part B and E133 W1B/W2 (in sample for the chain: it checks the code, not the model).
Hold names that match predictions-e144.json (H_L, H_M, H_H, H_H', G1, G2) are also scored on arms b and c.
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import heat_q138t as hm  # noqa: E402
import fit_q138t as ft  # noqa: E402

M = json.load(open(os.path.join(HERE, "model-q138t.json")))
PRED = json.load(open(os.path.join(HERE, "predictions-e144.json")))
TAU = M["tau_grid_s"]


def verdict_a(card, r):
    if card == "a3":
        ok, bad = (0.80, 1.00), (1.60, 2.00)
    else:
        ok, bad = (1.20, 1.30), (2.20, 2.40)
    if r["rms_C"] > bad[0] or abs(r["plateau_err_C"]) > bad[1]:
        return "FAIL"
    if r["rms_C"] <= ok[0] and abs(r["plateau_err_C"]) <= ok[1]:
        return "PASS"
    return "INCONCLUSIVE"


def a3_session(dirs):
    tel = hm.load_tel([os.path.join(d, "telemetry.jsonl.gz") for d in dirs], "codes")
    marks = [json.loads(x) for x in open(os.path.join(dirs[-1], "marks.jsonl"))]
    g, P, T = hm.grid(tel)
    holds, rests = [], []
    for m in marks:
        if m.get("kind") == "rest" and "t_end_ms" in m:
            rests.append({"name": m["name"], "t0": m["t_start_ms"] / 1e3, "t1": m["t_end_ms"] / 1e3})
        if m.get("kind") == "hold_start":
            holds.append({"name": m["name"], "item": m.get("item"), "t0": m["t_start_ms"] / 1e3})
    for h in holds:
        later = [r["t0"] for r in rests if r["t0"] >= h["t0"]] + [x["t0"] for x in holds if x["t0"] > h["t0"]] + [g[-1]]
        h["t1"] = min(later)
        h["anchor_end"] = max(r["t1"] for r in rests if r["t1"] <= h["t0"] + 1e-3)
        nxt = [r for r in rests if abs(r["t0"] - h["t1"]) < 1e-3]
        h["rest_after"] = (nxt[0]["t0"], nxt[0]["t1"]) if nxt else None
    r0 = rests[0]
    Pref = float(np.median(P[(g >= r0["t1"] - hm.ANCHOR_S) & (g < r0["t1"])]))
    return {"name": "session", "g": g, "P": P, "T": T, "Pref": Pref, "dP": P - Pref, "holds": holds, "rests": rests}


def a2_sessions(dirs):
    out = []
    for d in dirs:
        fs = sorted(os.listdir(os.path.join(d, "tel")))
        paths = [os.path.join(d, "tel", f) for f in fs]
        spans = []
        for f, p in zip(fs, paths):
            t = hm.load_tel([p], "fw")["t"]
            spans.append({"file": f, "t0": float(t[0]), "t1": float(t[-1])})
        tel = hm.load_tel(paths, "fw")
        g, P, T = hm.grid(tel)
        rest = [x for x in spans if x["file"].startswith("REST")][0]
        Pref = float(np.median(P[(g >= rest["t0"]) & (g <= rest["t1"])]))
        holds = [{"name": x["file"].split("-r1")[0], "t0": x["t0"], "t1": x["t1"], "anchor_end": rest["t1"]} for x in spans if x["file"].startswith("HOLD")]
        out.append({"name": os.path.basename(d.rstrip("/")), "g": g, "P": P, "T": T, "Pref": Pref, "dP": P - Pref, "holds": holds,
                    "mhz": np.interp(g, tel["t"], tel["mhz"])})
    return out


def t63_measured(s, h, pred_rise_plateau):
    """first time the measured rise over the anchor (5 s means) reaches 63% of the hold's own last-300-s rise"""
    g, T = s["g"], s["T"]
    a = float(np.mean(T[(g >= h["anchor_end"] - hm.ANCHOR_S) & (g < h["anchor_end"])]))
    m = (g >= h["t0"]) & (g < h["t1"])
    tt, yy = g[m] - h["t0"], T[m] - a
    plat = float(np.mean(yy[tt >= tt[-1] - 300]))
    k = np.convolve(yy, np.ones(25) / 25, mode="same")
    i = int(np.argmax(k >= 0.632 * plat))
    return float(tt[i]), plat


def score(card, sessions):
    R = np.array(M[card]["R_full_grid"])
    rows = []
    for s in sessions:
        pred = ft.predict_session(s, TAU, R)
        for h in s["holds"]:
            r = ft.score_hold(s, pred, h)
            r["a_verdict"] = verdict_a(card, r)
            g = s["g"]
            mp = (g >= h["t1"] - 300) & (g < h["t1"])
            ma = (g >= h["anchor_end"] - hm.ANCHOR_S) & (g < h["anchor_end"])
            r["board_rise_W"] = float(np.mean(s["P"][mp]) - np.mean(s["P"][ma]))
            r["per_board_W"] = r["rise_meas_C"] / r["board_rise_W"] if r["board_rise_W"] > 1 else None
            if h["t1"] - h["t0"] > 600:
                r["t63_s"], _ = t63_measured(s, h, None)
            key = h["name"]
            if card == "a3":
                pl = {x["hold"]: x for x in PRED["aifoundry3"]["holds"]}
                pc = {x["hold"]: x for x in PRED["aifoundry3"]["plateaus"]}
                if key in pl:
                    e = r["rise_meas_C"] - pl[key]["plateau_rise_C"]
                    r["b_plateau_err_C"] = e
                    r["b_verdict"] = "FAIL" if abs(e) > 2.6 else ("PASS" if abs(e) <= 1.3 else "INCONCLUSIVE")
                    r["c_per_board_W_verdict"] = None if r["per_board_W"] is None else (
                        "PASS" if 0.80 <= r["per_board_W"] <= 0.94 else ("FAIL" if not (0.74 <= r["per_board_W"] <= 1.00) else "INCONCLUSIVE"))
                    if "t63_s" in r and key in pc:
                        q = r["t63_s"] / pc[key]["t63_closed_s"]
                        r["c_t63_ratio"] = q
                        r["c_t63_verdict"] = "PASS" if 0.75 <= q <= 1.33 else ("FAIL" if not (0.5 <= q <= 2.0) else "INCONCLUSIVE")
            else:
                if key.startswith("HOLD-00") and "G1" in PRED["aifoundry2"]:
                    pass   # E144's G1/G2 are named by its runner; the self-test's holds are E111/E133's
            rows.append(r)
    return rows


def main():
    args = sys.argv[1:]
    if args and args[0] == "--self-test":
        e97 = os.path.join(hm.DATA, "2026-11-01-e97-heat-low-power-steady/aifoundry3/e97")
        s3 = a3_session([os.path.join(e97, "p9711"), os.path.join(e97, "p9720")])
        rows3 = score("a3", [s3])
        e133 = os.path.join(hm.DATA, "2026-11-02-e133-heat-holds")
        rows2 = score("a2", a2_sessions([os.path.join(e133, "W1B"), os.path.join(e133, "W2")]))
        out = {"note": "in sample for the chain (E97 and E133 trained it): this checks the scorer, not the model", "a3_E97": rows3, "a2_E133": rows2}
        print(json.dumps(out, indent=1))
        return
    card, dirs = args[0], args[1:]
    sessions = [a3_session(dirs)] if card == "a3" else a2_sessions(dirs)
    print(json.dumps(score(card, sessions), indent=1))


if __name__ == "__main__":
    main()
