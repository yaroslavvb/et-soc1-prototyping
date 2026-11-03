#!/usr/bin/env python3
"""Q139(q) for E159: G3's frozen predictions for three GEMM shapes nobody has run, held about 106 s on aifoundry2 under its own governor, and
the scorer that applies the critic's rules to them. Desk only; nothing here opens a device.

    python3 e159_g3.py predict > predictions-e159.txt      (writes predictions-e159.json, the frozen numbers and the design)
    python3 e159_g3.py score <E159 session dir> [<results.json out>]   (after E159: G3 per hold, mechanically, then the rules)

THE PRIMARY PREDICTION is mechanical and frozen: for each hold, g3_model.simulate with these levels and G3's frozen constants (K_LEAK_G3 0.1,
TRIP_G3 65.5), started from the session's own state (the chain open loop on the measured board trace up to the hold's first process, anchored
on the measured die over the 20 s before it) and run on the hold's own kernel windows; nothing measured after the hold starts enters. The
frozen table below gives the same numbers for two nominal starts, so the predictions are on record as numbers too.

THE ARMS, all registered: (1) G3 (primary); (2) G3 at Q138(t)'s constants (0.442 W per C, 65.9 C); (3) the chain on the measured trace (the
heat path alone, given the watts; die only); (4) E136's law, the old arm (footing G2 on the same P0 levels: the sustained cap 60.827 W, a held
cell at 62.06 W; the die min(65.5, 0.379 die_start + 0.621 (44.0 + 0.67 (P_sus - 21.5))) with the hold's measured die_start); (5) G3 given
the hold's own first second (P0's levels scaled to the measured p800), a diagnostic that separates P0's level from the governor and heat path.

THE RULES (the critic's, Q138(f) open item 3): per hold, the sustained clock within 15 MHz, the board within 2 W and the window die within 1 C
of G3 (measured - predicted, the window = in-kernel samples of the last 40 s, reduce_hpl's). Verdicts: per quantity, G3 PASSES when every
scored hold is inside; the summary also gives the count inside, the rms of every arm, and whether G3's rms is below E136's law's.
"""
import gzip
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import g3_model as G  # noqa: E402

LAB = G.LAB
sys.path.insert(0, os.path.join(LAB, "tools/claims-v3/e146/desk"))
sys.path.insert(0, os.path.join(LAB, "tools/claims-v3/e146"))
import reuse_e146 as RD  # noqa: E402  (E146's desk line split, unchanged)
import make_predictions_e146 as M146  # noqa: E402  (E146's P0: E136's law for explicit lines, unchanged)

SHAPES = {"H1": (2, 4, 8), "H2": (4, 2, 4), "H3": (1, 2, 2)}       # gemmL<MB>x<NB>x<KB>, none run before
KINDS = {"fp32": "randn", "int8": "full", "zeros": "zeros"}
ORDER = ["H1-fp32-randn", "H1-int8-full", "H2-fp32-randn", "H2-int8-full", "H3-fp32-randn", "H3-int8-full", "H1-fp32-zeros", "H2-fp32-zeros",
         "H3-fp32-zeros"]
SUBSET = ORDER[:6]
N_PROC, SECONDS = 12, 8.0
PEAK_MARGIN_W = 8.51           # the largest 10 Hz board sample over P0(800) in the 56 committed sustained runs (posthoc-g3.json, E126 c4s fp32)
PEAK_LIMIT_W = 82.0            # the brief's aifoundry2 rule: no design whose predicted peak exceeds 82 W
STOPS = {"abs_stop_c": 76, "board_cap_w": 85, "cap_consecutive": 3}
RULE = {"mhz": 15.0, "w": 2.0, "die": 1.0}
P_REST, T_REST = 22.0, 46.0     # a rested aifoundry2 (E146's smoke 22.06 W, 46.0 C; E144b's 46 C)


def values(shape, t, kind):
    MB, NB, KB = SHAPES[shape]
    arm = f"gemmL{MB}x{NB}x{KB}"
    if kind == "zeros":
        return f"{arm}:tiles:tools/claims-v3/kinds/tiles/{t}/zeros.bin"
    return f"{arm}:randn:tools/claims-v3/kinds/tiles/{t}/{kind}.bin"


def desk():
    out = {}
    for s, (MB, NB, KB) in SHAPES.items():
        sp = RD.split(("large", MB, NB, KB), 32)
        M146.DESK["shapes"][s] = {"lines": {"32MB": sp}, "store_every_ops": KB * 32}
        fp = {"A_MB": MB * KB * 2, "B_MB": KB * NB * 1, "C_MB": MB * NB * 2}
        out[s] = {"arm": f"gemmL{MB}x{NB}x{KB}", "blocks": [MB, NB, KB], "elements_MNK_fp32": [MB * 1024, NB * 512, KB * 512],
                  "footprint_MB": dict(fp, total=sum(fp.values())), "store_every_ops": KB * 32, "lines_32MB": sp}
    return out


def levels(s, t, kind):
    k = "top" if kind != "zeros" else "zeros"
    return M146.levels0(s, t, k)


def nominal(lev, start):
    """G3 for a 12-process hold from a nominal start: 'rest' (states zero at a 46.0 C rest) or 'gate57' (after the same shape's fp32 random
    hold from rest, idle until the die reads 57 C)."""
    g, on, wins = G.run_schedule(N_PROC, SECONDS)
    t_end = wins[-1][1]
    x0 = np.zeros(len(G.TAU))
    if start == "gate57":
        Tp, Pp, Fp = G.simulate(lev["prev"], on, x0, T_REST, T_start=T_REST, k_leak=G.K_LEAK_G3, trip=G.TRIP_G3)
        xs = G.chain_open(Pp)
        x = xs[-1]
        while T_REST + float(G.R @ x) > 57.0:
            x = G.A * x + (1 - G.A) * 0.0
        x0 = x
    T0 = T_REST + float(G.R @ x0)
    out = {}
    for arm, (k, tr) in {"G3": (G.K_LEAK_G3, G.TRIP_G3), "G3_q138t_constants": (G.K_LEAK, G.T_TRIP)}.items():
        T, P, F = G.simulate(lev["P"], on, x0, T_REST, T_start=T0, k_leak=k, trip=tr)
        w = G.window_means(g, on, T, P, F, t_end)
        out[arm] = {"mhz": round(w["mhz"], 1), "w": round(w["w"], 2), "die": round(w["die"], 2), "die_start": round(T0, 2),
                    "peak_w_traj": round(float(np.max(P)), 2)}
    law = G.e136_law(lev["P"], T0)
    out["E136_law"] = {k: round(v, 2) for k, v in law.items()}
    return out


def predict():
    D = desk()
    cells = {}
    for s in SHAPES:
        for t, kind in (("fp32", "randn"), ("int8", "full"), ("fp32", "zeros")):
            lab = f"{s}-{t}-{kind}"
            P0 = levels(s, t, kind)
            prev = levels(s, "fp32", "randn")
            est = M146.B[800] + M146.SF[800] * M146.c600(s, t, "top" if kind != "zeros" else "zeros")
            peak = P0[800] + PEAK_MARGIN_W
            nom = {st: nominal({"P": P0, "prev": prev}, st) for st in ("rest", "gate57")}
            cells[lab] = {"values": values(s, t, kind), "type": t, "P0_w": {str(f): round(v, 2) for f, v in P0.items()},
                          "admission_p800_estimate_w": round(est, 1), "predicted_peak_w": round(peak, 2), "runs_as_designed": peak <= PEAK_LIMIT_W,
                          "T0_800_us": round(M146.T0(s, t, 800), 4), "nominal": nom}
    design = {"card": "aifoundry2 card 0, its own governor (65 W / 65 C read, never set)", "binary": "E136's rgm136 SP_GEMM_LARGE, unchanged (sha256 as E136/E146)",
              "shapes": D, "order": ORDER, "registered_subset": SUBSET,
              "hold": {"processes": N_PROC, "seconds": SECONDS, "budget": 9.5, "tail_s": 6, "start": {"mode": "cool", "max_c": 57, "max_wait_s": 300},
                       "window": "in-kernel samples of the last 40 s of work (reduce_hpl SUS_LAST_S)"},
              "stops": STOPS, "stops_note": "board above 85 W on 3 live samples in a row, or a die reading at or above 76 C, ends the session; both tested on live samples in the smoke (E146's stoptest-board at 30 W and stoptest-die at 30 C)",
              "power_rule": f"predicted peak = P0(800) + {PEAK_MARGIN_W} W (the largest excursion in 56 committed sustained runs) must be <= {PEAK_LIMIT_W} W; every cell here is",
              "budget": "about 31 card-minutes planned (9 holds of about 106 s, cool-downs, smoke and stop tests); cap 40; the subset (first 6) about 22",
              "device_commands": "E146's chain unchanged (ettelem sample without --reset-ms, ettelem config, ettelem sptrace, the residency rewrite answered unsent, sparsity_host): every command READ; the E159 lane re-runs tools/claims-v3/dmcmd_audit.py before its claim"}
    out = {"what": "Q139(q): G3's frozen predictions for E159 (aifoundry2, its own governor), nothing of E159 exists", "date": "2026-11-03",
           "g3": {"k_leak_W_per_C": G.K_LEAK_G3, "trip_C": G.TRIP_G3, "chain": "docs/reports/data/2026-11-02-q138t-heat-model/model-q138t.json a2",
                  "burst_cap": [G.WB, G.SB], "off_share": G.OFF_SHARE, "anchor_s": G.ANCHOR_S, "P0": "E146 make_predictions_e146.levels0 on the desk's 32 MB split"},
           "q138t_constants_arm": {"k_leak_W_per_C": G.K_LEAK, "trip_C": G.T_TRIP},
           "rules": {"per_hold": {"clock_mhz": RULE["mhz"], "board_w": RULE["w"], "window_die_c": RULE["die"]},
                     "text": "measured - predicted per hold, G3 the primary: clock within 15 MHz, board within 2 W, window die within 1 C. Per quantity PASS when every scored hold is inside, else FAIL with the count; the rms of each arm per quantity; G3 beats E136's law on a quantity when its rms is lower. The chain on the measured trace and E136's law are scored the same way and reported beside G3; the p800 diagnostic has no verdict. A hold cut by a stop or not run is not scored; the registered subset is the first six of the order.",
                     "attribution": "a G3 clock or board miss on a hold whose first-second power p800 is more than 4 W from P0(800) is P0's level (E146 R3's band), and the diagnostic arm says how much of it; a die miss where the chain on the measured trace is inside 1 C is the power path, not heat"},
           "design": design, "cells": cells}
    json.dump(out, open(os.path.join(HERE, "predictions-e159.json"), "w"), indent=1)
    print("Q139(q) frozen G3 predictions for E159 (aifoundry2, its own governor). Nominal starts: 'rest' (46.0 C) and 'gate57' (after a governed fp32 hold, idle to 57 C).")
    print("The registered primary is the mechanical G3 from each hold's own measured start (score); these are the same model at nominal starts.")
    for s, d in D.items():
        print(f"  {s} {d['arm']}: M x N x K fp32 {d['elements_MNK_fp32']}, {d['footprint_MB']['total']} MB with C, a C store every {d['store_every_ops']} ops; "
              f"lines an op that miss the L2: L3 {d['lines_32MB']['n_L3']}, fresh {d['lines_32MB']['n_F']}")
    print(f"{'cell':18s} {'P0 600/700/800 W':>18s} {'peak':>6s} | {'G3 rest: MHz':>12s} {'W':>6s} {'die':>5s} | {'G3 gate57: MHz':>14s} {'W':>6s} {'die':>5s} | "
          f"{'Q138t-const gate57':>18s} | {'E136 law gate57':>16s}")
    for lab, c in cells.items():
        P0 = c["P0_w"]
        a, b = c["nominal"]["rest"]["G3"], c["nominal"]["gate57"]["G3"]
        q, lw = c["nominal"]["gate57"]["G3_q138t_constants"], c["nominal"]["gate57"]["E136_law"]
        print(f"{lab:18s} {P0['600']:5.1f}/{P0['700']:5.1f}/{P0['800']:5.1f} {c['predicted_peak_w']:6.1f} | {a['mhz']:12.1f} {a['w']:6.2f} {a['die']:5.2f} | "
              f"{b['mhz']:14.1f} {b['w']:6.2f} {b['die']:5.2f} | {q['mhz']:6.1f} {q['w']:5.1f} {q['die']:5.1f} | {lw['mhz']:5.1f} {lw['w']:5.1f} {lw['die']:5.1f}")


def score(sdir, outp=None):
    """G3 per hold, mechanically, then the rules. sdir: the E159 session dir holding runs.jsonl, launches.jsonl.gz and tel/."""
    P = json.load(open(os.path.join(HERE, "predictions-e159.json")))
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
    rows = []
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
        lev = {int(f): v for f, v in P["cells"][cell]["P0_w"].items()}
        arms = {}
        for name, (k, tr) in {"G3": (G.K_LEAK_G3, G.TRIP_G3), "G3_q138t_constants": (G.K_LEAK, G.T_TRIP)}.items():
            T_, P_, F_ = G.simulate(lev, on, x0, anc, T_start=Ts, k_leak=k, trip=tr)
            arms[name] = G.window_means(gg, on, T_, P_, F_, t1)
        inw = np.zeros(len(t), bool)
        for a, b in kw:
            inw |= (t >= a) & (t <= b)
        mw = inw & (t >= t1 - G.SUS_LAST_S) & (t <= t1)
        meas = {"mhz": float(np.nanmean(tel["mhz"][mw])), "w": float(np.mean(tel["P"][mw])), "die": float(np.mean(tel["T"][mw]))}
        die_start = float(tel["T"][inw & (t >= t0)][0])
        arms["E136_law"] = G.e136_law(lev, die_start)
        Tc = anc + Xm[i0:i1 + 1] @ G.R
        mm = on & (gg >= t1 - G.SUS_LAST_S) & (gg <= t1)
        arms["chain_on_measured"] = {"die": float(np.mean(Tc[mm]))}
        first = [i for i in np.nonzero(inw & (t >= t0) & (tel["mhz"] == 800))[0]]
        p800 = float(np.median([tel["P"][i] for i in first if t[i] <= t[first[0]] + 1.0])) if first else None
        if p800:
            T_, P_, F_ = G.simulate(lev, on, x0, anc, T_start=Ts, k_leak=G.K_LEAK_G3, trip=G.TRIP_G3, p_scale=p800 / lev[800])
            arms["G3_given_p800"] = G.window_means(gg, on, T_, P_, F_, t1)
        err = {a: {q: meas[q] - v[q] for q in v} for a, v in arms.items()}
        rows.append({"run": r["run"], "cell": cell, "meas": meas, "die_start": die_start, "p800": p800, "P0_800": lev[800],
                     "pred": arms, "err": err, "inside_G3": {q: abs(err["G3"][q]) <= RULE[q] for q in RULE}})
    summ = {}
    for a in ("G3", "G3_q138t_constants", "E136_law", "chain_on_measured", "G3_given_p800"):
        for q in RULE:
            e = [x["err"][a][q] for x in rows if a in x["err"] and q in x["err"][a]]
            if e:
                e = np.array(e)
                summ[f"{a}.{q}"] = {"n": int(len(e)), "rms": round(float(np.sqrt(np.mean(e ** 2))), 3), "mean": round(float(np.mean(e)), 3),
                                    "inside": int(np.sum(np.abs(e) <= RULE[q]))}
    verdict = {q: ("PASS" if rows and all(x["inside_G3"][q] for x in rows) else "FAIL") + f" ({sum(x['inside_G3'][q] for x in rows)} of {len(rows)})" for q in RULE}
    beats = {q: (summ.get(f"G3.{q}", {}).get("rms", 1e9) < summ.get(f"E136_law.{q}", {}).get("rms", -1)) for q in RULE}
    res = {"rows": rows, "summary": summ, "verdict_G3": verdict, "G3_rms_below_E136_law": beats,
           "predictions_sha256_note": "score with predictions-e159.json and g3_model.py as committed by Q139(q)"}
    for x in rows:
        print(f"{x['cell']:18s} meas {x['meas']['mhz']:6.1f} MHz {x['meas']['w']:6.2f} W {x['meas']['die']:5.2f} C | G3 {x['pred']['G3']['mhz']:6.1f} "
              f"{x['pred']['G3']['w']:6.2f} {x['pred']['G3']['die']:5.2f} | inside {x['inside_G3']}")
    print(json.dumps({"verdict_G3": verdict, "G3_rms_below_E136_law": beats, "summary": summ}, indent=1))
    if outp:
        json.dump(res, open(outp, "w"), indent=1)
    return res


def selftest():
    """the scorer on E146's committed session, with F6's two holds relabelled as E159 cells of the same levels (a check of the code path only)"""
    import tempfile
    import shutil
    src = os.path.join(LAB, "docs/reports/data/2026-11-02-e146-gemm-stores/aifoundry2/s1")
    P = json.load(open(os.path.join(HERE, "predictions-e159.json")))
    P146 = json.load(open(os.path.join(LAB, "tools/claims-v3/e146/predictions-e146.json")))
    tmp = tempfile.mkdtemp(prefix="e159-selftest-", dir=os.environ.get("TMPDIR"))
    try:
        os.symlink(os.path.join(src, "tel"), os.path.join(tmp, "tel"))
        os.symlink(os.path.join(src, "launches.jsonl.gz"), os.path.join(tmp, "launches.jsonl.gz"))
        rel = {"F6-fp32-randn": "H1-fp32-randn", "F6-int8-full": "H1-int8-full"}
        with open(os.path.join(tmp, "runs.jsonl"), "w") as f:
            for x in open(os.path.join(src, "runs.jsonl")):
                r = json.loads(x)
                if r.get("processes", 1) > 1:
                    r["label"] = rel.get(r["label"], r["label"])
                f.write(json.dumps(r) + "\n")
        saved = {k: P["cells"][k]["P0_w"] for k in rel.values()}
        for a, b in rel.items():
            P["cells"][b]["P0_w"] = P146["cells"][a]["P0_w"]
        json.dump(P, open(os.path.join(tmp, "p.json"), "w"))
        global HERE_P
        res = score_with(tmp, os.path.join(tmp, "p.json"))
        print("SELFTEST (E146's F6 holds through the E159 scorer, F6's own P0 levels):", json.dumps(res["verdict_G3"]))
    finally:
        shutil.rmtree(tmp)


def score_with(sdir, ppath):
    global HERE
    real = os.path.join(HERE, "predictions-e159.json")
    data = open(real).read()
    try:
        open(real, "w").write(open(ppath).read())
        return score(sdir)
    finally:
        open(real, "w").write(data)


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "predict":
        predict()
    elif len(sys.argv) >= 3 and sys.argv[1] == "score":
        score(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
    elif len(sys.argv) >= 2 and sys.argv[1] == "selftest":
        selftest()
    else:
        print(__doc__)
