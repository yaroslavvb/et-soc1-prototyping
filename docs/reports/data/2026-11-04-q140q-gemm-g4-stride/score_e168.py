#!/usr/bin/env python3
"""Q140(q): E168's scorer (REGISTRATION.md A7, 49575094), frozen with predictions-e168.json. Desk only; it opens no device.

    /usr/bin/python3 -B score_e168.py check                               (the frozen files' sha256, against frozen-sha256-e168.json)
    /usr/bin/python3 -B score_e168.py score <E168 session dir> [out.json] [--anchors <anchors.json>]
    /usr/bin/python3 -B score_e168.py selftest                            (E159's committed session through the code path; writes nothing)

THE PRIMARY is G4 (g4.json) run mechanically per hold from the session's own state, exactly as e159_g3.score builds it (the chain open
loop on the measured board trace up to the hold's first process, anchored on the measured die over the 20 s before it, the hold's own
kernel windows, the window = in-kernel samples of the last 40 s), with each hold's P0 levels from predictions-e168.json. T_Z uses
m9_a2.json's fallback; with --anchors (the session's kinds zeros-anchor reads in predict_m9_a2.session_delta's layout) a second arm
uses the session's own delta. Beside it, scored the same way: G3 as frozen (0.1 W/C, 65.5 C), E136's law (its die law on the hold's
measured die start), the chain on the measured trace (heat alone, die only).

THE RULES (the critic's rank 5): per hold, measured - G4, the window clock within 15 MHz, the board within 2 W, the window die within 1 C;
each quantity PASSES when at least 8 of the 9 holds are inside (a hold not run or cut by a stop is not scored, and the count is given).
The increment rule: for int8 W8A8 real and int8 sparse50 at S2, (the hold's window board - int8 zeros' window board at S2), measured
against G4's, within 15% of the span (G4's frozen 800 MHz level int8 full - int8 zeros at S2, predictions-e168.json). runs.jsonl labels
must equal the cell names (e.g. S2-int8-zeros-warm55).
SPDX-License-Identifier: Apache-2.0
"""
import gzip
import hashlib
import json
import os
import sys

sys.dont_write_bytecode = True
import numpy as np  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import g4_model as G4  # noqa: E402

G = G4.G
LAB = G4.LAB
RULE = {"mhz": 15.0, "w": 2.0, "die": 1.0}
FROZEN = ["g4.json", "g4_model.py", "predictions-e168.json", "score_e168.py",
          "../2026-11-03-q139q-gemm-g3/g3_model.py", "../2026-11-04-q140l-a2-session-terms/m9_a2.json",
          "../2026-11-04-q140l-a2-session-terms/predict_m9_a2.py", "../2026-11-02-q138t-heat-model/model-q138t.json",
          "../2026-11-02-q138t-heat-model/heat_q138t.py", "../../../../tools/claims-v3/e119/make_predictions_e119.py"]


def sha(p):
    return hashlib.sha256(open(os.path.join(HERE, p), "rb").read()).hexdigest()


def check():
    ref = json.load(open(os.path.join(HERE, "frozen-sha256-e168.json")))
    bad = [p for p in FROZEN if p != "score_e168.py" and ref.get(p) != sha(p)]
    print("CHECK OK" if not bad else f"CHECK FAILED: {bad}", f"({len(FROZEN) - 1} files)")
    return not bad


def build(sdir, P):
    """per hold: the inputs in g4_model's layout, from the session's runs.jsonl, launches.jsonl.gz and tel/ (e159_g3.score's path)"""
    hm = G.hm
    runs = [json.loads(x) for x in open(os.path.join(sdir, "runs.jsonl"))]
    L = [json.loads(x) for x in gzip.open(os.path.join(sdir, "launches.jsonl.gz"), "rt")]
    paths = sorted(os.path.join(sdir, "tel", f) for f in os.listdir(os.path.join(sdir, "tel")) if f.endswith(".jsonl.gz") or f.endswith(".jsonl"))
    tel = hm.load_tel(paths, sensor="fw")
    t = tel["t"]
    ok = np.isfinite(tel["T"]) & np.isfinite(tel["P"])
    g = np.arange(t[ok][0], t[ok][-1], G.DT)
    Pm, Tm = np.interp(g, t[ok], tel["P"][ok]), np.interp(g, t[ok], tel["T"][ok])
    Xm = G.chain_open(Pm)
    out = []
    for r in runs:
        cell = r.get("label")
        if r.get("processes", 1) < 2 or cell not in P["cells"]:
            continue
        procs = [p for p in L if p["run"] == r["run"] and p.get("role") == "work"]
        if not procs:
            continue
        t0, t1 = min(p["t_start_ms"] for p in procs) / 1000.0, max(p["t_end_ms"] for p in procs) / 1000.0
        kw = [(k["t_start_ms"] / 1000.0, k["t_end_ms"] / 1000.0) for p in procs for k in p.get("sparsity", []) if k.get("t_start_ms") and k.get("t_end_ms")]
        i0, i1 = int(np.searchsorted(g, t0)), int(np.searchsorted(g, t1))
        gg = g[i0:i1 + 1]
        on = np.zeros(len(gg), bool)
        for a, b in kw:
            on |= (gg >= a) & (gg <= b)
        ma = (g >= t0 - G.ANCHOR_S) & (g < t0)
        anc = float(np.mean(Tm[ma] - Xm[ma] @ G.R))
        x0 = Xm[i0 - 1]
        Ts = anc + float(G.R @ x0)
        inw = np.zeros(len(t), bool)
        for a, b in kw:
            inw |= (t >= a) & (t <= b)
        mw = inw & (t >= t1 - G.SUS_LAST_S) & (t <= t1)
        meas = {"mhz": float(np.nanmean(tel["mhz"][mw])), "w": float(np.mean(tel["P"][mw])), "die": float(np.mean(tel["T"][mw]))}
        die_start = float(tel["T"][inw & (t >= t0)][0])
        Tc = anc + Xm[i0:i1 + 1] @ G.R
        mm = on & (gg >= t1 - G.SUS_LAST_S) & (gg <= t1)
        out.append({"cell": cell, "run": r["run"], "type": P["cells"][cell]["type"], "lev": P["cells"][cell]["P0_w"], "on": on, "gg0": float(gg[0]), "t1": t1,
                    "x0": x0, "anc": anc, "T_start": Ts, "die_start_meas": die_start, "meas": meas, "chain_die": float(np.mean(Tc[mm]))})
    return out


def score(sdir, outp=None, anchors=None, ppath=None):
    P = json.load(open(ppath or os.path.join(HERE, "predictions-e168.json")))
    C4 = P["g4"]["constants"]
    arm4 = {"k": C4["k_W_per_C"], "trip": C4["trip_C"], "T_ref": C4["T_ref_C"], "zeros": C4["zeros_level"],
            "dip": None if not C4["dip"] else (C4["dip"]["d_G"], C4["dip"]["P_G_w"])}
    arm3 = {"k": G.K_LEAK_G3, "trip": G.TRIP_G3}
    own = None
    if anchors:
        sys.path.insert(0, os.path.join(LAB, "docs/reports/data/2026-11-04-q140l-a2-session-terms"))
        import predict_m9_a2 as A2  # noqa: E402
        own, _ = A2.session_delta(json.load(open(anchors)))
    rows = []
    for c in build(sdir, P):
        lev = {int(f): v for f, v in c["lev"].items()}
        cc = dict(c, lev={str(k): v for k, v in lev.items()}, on=[bool(v) for v in c["on"]], x0=[float(v) for v in c["x0"]])
        pred = {"G4": G4.run_arm(cc, arm4), "G3_as_frozen": G4.run_arm(cc, arm3),
                "E136_law": G.e136_law(lev, c["die_start_meas"]), "chain_on_measured": {"die": c["chain_die"]}}
        if own is not None:
            save = dict(G4.DELTA_FALLBACK)
            try:
                G4.DELTA_FALLBACK.update(own)
                pred["G4_own_anchors"] = G4.run_arm(cc, arm4)
            finally:
                G4.DELTA_FALLBACK.clear()
                G4.DELTA_FALLBACK.update(save)
        err = {a: {q: c["meas"][q] - v[q] for q in v} for a, v in pred.items()}
        rows.append({"cell": c["cell"], "run": c["run"], "meas": c["meas"], "die_start": c["die_start_meas"], "pred": pred, "err": err,
                     "inside_G4": {q: abs(err["G4"][q]) <= RULE[q] for q in RULE}})
    summ = {}
    for a in ("G4", "G4_own_anchors", "G3_as_frozen", "E136_law", "chain_on_measured"):
        for q in RULE:
            e = [x["err"][a][q] for x in rows if a in x["err"] and q in x["err"][a]]
            if e:
                e = np.array(e)
                summ[f"{a}.{q}"] = {"n": int(len(e)), "rms": round(float(np.sqrt(np.mean(e ** 2))), 3), "mean": round(float(np.mean(e)), 3),
                                    "inside": int(np.sum(np.abs(e) <= RULE[q]))}
    n = len(rows)
    verdict = {q: ("PASS" if n and sum(x["inside_G4"][q] for x in rows) >= min(8, n) and (n >= 9 or all(x["inside_G4"][q] for x in rows)) else "FAIL")
               + f" ({sum(x['inside_G4'][q] for x in rows)} of {n}; the rule needs 8 of 9)" for q in RULE}
    inc = {}
    by = {x["cell"]: x for x in rows}
    z = by.get("S2-int8-zeros-warm55")
    for k in ("real_smol_w8a8_down", "sparse50"):
        h = by.get(f"S2-int8-{k}-warm55")
        if z and h:
            rule = P["cells"][f"S2-int8-{k}-warm55"]["increment_rule"]
            mi = h["meas"]["w"] - z["meas"]["w"]
            pi = h["pred"]["G4"]["w"] - z["pred"]["G4"]["w"]
            inc[k] = {"measured_increment_w": round(mi, 3), "G4_increment_w": round(pi, 3), "err_w": round(mi - pi, 3), "band_w": rule["band_w"],
                      "verdict": "PASS" if abs(mi - pi) <= rule["band_w"] else "FAIL"}
    res = {"rows": rows, "summary": summ, "verdict_G4": verdict, "increment_rule": inc,
           "G4_rms_below": {ref: {q: summ.get(f"G4.{q}", {}).get("rms", 1e9) < summ.get(f"{ref}.{q}", {}).get("rms", -1) for q in RULE} for ref in ("G3_as_frozen", "E136_law")},
           "note": "scored with predictions-e168.json, g4.json and g4_model.py as frozen by Q140(q)"}
    for x in rows:
        print(f"{x['cell']:36s} meas {x['meas']['mhz']:6.1f} MHz {x['meas']['w']:6.2f} W {x['meas']['die']:5.2f} C | G4 {x['pred']['G4']['mhz']:6.1f} {x['pred']['G4']['w']:6.2f} "
              f"{x['pred']['G4']['die']:5.2f} | inside {x['inside_G4']}")
    print(json.dumps({"verdict_G4": verdict, "increment_rule": inc, "G4_rms_below": res["G4_rms_below"], "summary": summ}, indent=1, default=str))
    if outp:
        json.dump(res, open(outp, "w"), indent=1, default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o))
    return res


def selftest():
    """E159's committed session through the code path, its three fp32 random holds relabelled as E168 cells with E159's own P0 levels
    (a check of the code only: the scorer must reproduce fit_g4's G4 final predictions for those holds); writes nothing in the tree"""
    import tempfile
    import shutil
    src = os.path.join(LAB, "docs/reports/data/2026-11-03-e159-gemm-sustained/aifoundry2/s1")
    P = json.load(open(os.path.join(HERE, "predictions-e168.json")))
    P159 = json.load(open(os.path.join(G4.G3D, "predictions-e159.json")))
    rows_fit = {r["cell"]: r for r in json.load(open(os.path.join(HERE, "rows-g4.json"))) if r["session"] == "E159"}
    rel = {"H1-fp32-randn": "S1-fp32-randn-cold", "H2-fp32-randn": "S2-fp32-randn-cold", "H3-fp32-randn": "S3-fp32-randn-cold"}
    tmp = tempfile.mkdtemp(prefix="e168-selftest-", dir=os.environ.get("TMPDIR"))
    try:
        os.symlink(os.path.join(src, "tel"), os.path.join(tmp, "tel"))
        os.symlink(os.path.join(src, "launches.jsonl.gz"), os.path.join(tmp, "launches.jsonl.gz"))
        with open(os.path.join(tmp, "runs.jsonl"), "w") as f:
            for x in open(os.path.join(src, "runs.jsonl")):
                r = json.loads(x)
                if r.get("processes", 1) > 1 and r.get("label") in rel:
                    r["label"] = rel[r["label"]]
                    f.write(json.dumps(r) + "\n")
        for a, b in rel.items():
            P["cells"][b]["P0_w"] = P159["cells"][a]["P0_w"]
        pp = os.path.join(tmp, "p.json")
        json.dump(P, open(pp, "w"))
        res = score(tmp, ppath=pp)
        worst = 0.0
        for a, b in rel.items():
            mine = [x for x in res["rows"] if x["cell"] == b][0]["pred"]["G4"]
            ref = rows_fit[a]["G4_final"]
            worst = max(worst, max(abs(mine[q] - ref[q]) for q in RULE))
        print(f"SELFTEST: E159's three fp32 random holds through score_e168's path reproduce fit_g4's G4 final predictions: worst |diff| {worst:.4f} "
              f"({'PASS' if worst < 0.01 else 'FAIL'})")
    finally:
        shutil.rmtree(tmp)


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "check":
        sys.exit(0 if check() else 1)
    elif len(sys.argv) >= 3 and sys.argv[1] == "score":
        a = sys.argv[2:]
        anc = None
        if "--anchors" in a:
            i = a.index("--anchors")
            anc = a[i + 1]
            a = a[:i] + a[i + 2:]
        if not check():
            sys.exit(1)
        score(a[0], a[1] if len(a) > 1 else None, anchors=anc)
    elif len(sys.argv) >= 2 and sys.argv[1] == "selftest":
        selftest()
    else:
        print(__doc__)
