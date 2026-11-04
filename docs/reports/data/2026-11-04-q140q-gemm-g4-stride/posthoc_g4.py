#!/usr/bin/env python3
"""Q140(q), POST HOC (written after fit_g4.py's registered result was read; nothing frozen depends on it, nothing is re-frozen).

    nice -n 10 /usr/bin/python3 -B posthoc_g4.py > posthoc-g4.txt      (writes posthoc-g4.json; 4 workers)

P1  T_D failed the forward rule while the same law fixed E158's zeros bursts (checks-g4 (i)). Split it: the START-die offset alone,
    every level + k_s (T_start - T_ref) at the run's start, with G3's in-run k_eff (T - T_start) kept, plus T_Z and G4's dip; nested
    leave one session out on k_s {0.44, 0.47, 0.50} x k_eff {0.1, 0.2, 0.3} x trip {65.3, 65.5, 65.7}, scored against G4 nested.
P2  G4's d_G was chosen at its grid's top (0.12): d_G 0.15 and 0.18 at G4's other final constants, in sample (is the edge binding?).
P3  M8's span fraction against E136's bursts: the first second's board at 800 MHz of E136's sparse50 and real bursts (every format)
    against E136's own law (E107's sparse50 S, E95's r_real) and T_S (phi = D_M8(kind) / D_M8(top)), both at the level's 800 MHz.
SPDX-License-Identifier: Apache-2.0
"""
import itertools
import json
import math
import os
import sys
from multiprocessing import Pool

sys.dont_write_bytecode = True
import numpy as np  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import g4_model as G4  # noqa: E402
import fit_g4 as FG  # noqa: E402  (its rows, loss and stats, unchanged)

G = G4.G
LAB = G4.LAB
C4 = json.load(open(os.path.join(HERE, "g4.json")))["constants"]
DIP = (C4["dip"]["d_G"], C4["dip"]["P_G_w"])
INP = None


def _init():
    global INP
    INP = FG.load_inputs()


def run_p1(cfg):
    key, (ks, ke, tr) = cfg
    out = []
    for c in INP:
        lev = {int(f): v for f, v in c["lev"].items()}
        on = np.asarray(c["on"], bool)
        gg = c["gg0"] + np.arange(len(on)) * G.DT
        shift = G4.BETA * G4.DELTA_FALLBACK[c["type"]] + ks * (c["T_start"] - G4.T_REF)
        T, P, F = G4.simulate4(lev, on, np.array(c["x0"]), c["anc"], c["T_start"], tr, ke, shift=shift, dip=DIP)
        out.append(G.window_means(gg, on, T, P, F, c["t1"]))
    return key, out


def run_p2(cfg):
    key, dg = cfg
    arm = {"k": C4["k_W_per_C"], "trip": C4["trip_C"], "zeros": True, "dip": (dg, DIP[1])}
    return key, [G4.run_arm(c, arm) for c in INP]


def p3():
    M136 = G4._m136()
    R = json.load(open(os.path.join(LAB, "docs/reports/data/2026-11-02-e136-large-gemm/results.json")))
    P136 = json.load(open(os.path.join(LAB, "tools/claims-v3/e136/predictions-e136.json")))
    ck = json.load(open(os.path.join(HERE, "checks-g4.json")))["iii_E136_other_kinds_T_S"]["phi"]
    m = G4.m8_D_rows([("E78", "a3", f"{t}.sparse50") for t in ("fp16", "int8")] + [("E78", "a3", "fp16.randn"), ("E78", "a3", "int8.full")])
    phi = {"fp32.sparse50": ck["fp32.sparse50"]["phi_M8"], "fp16.sparse50": m[("E78", "a3", "fp16.sparse50")]["D_M8"] / m[("E78", "a3", "fp16.randn")]["D_M8"],
           "int8.sparse50": m[("E78", "a3", "int8.sparse50")]["D_M8"] / m[("E78", "a3", "int8.full")]["D_M8"],
           "fp32.real": ck["fp32.real"]["phi_M8"], "fp16.real": ck["fp16.real"]["phi_M8"], "int8.real": ck["int8.real"]["phi_M8"]}
    rows = []
    for cell, v in sorted(R["cells"].items()):
        g, t, kind = cell.split("-")[0], cell.split("-")[1], "-".join(cell.split("-")[2:])
        if kind not in ("sparse50", "real") or not v.get("burst_p800_w_runs"):
            continue
        runs = [x for x in v["burst_p800_w_runs"] if x is not None]
        if not runs:
            continue
        p8 = sum(runs) / len(runs)
        lev136 = {int(f): x for f, x in P136["cells"][cell]["P_w"].items()}
        model = "P1"
        levS = G4.levels_phi136(g, t, phi[f"{t}.{kind}"], model)
        zl = {int(f): x for f, x in P136["cells"][f"{g}-{t}-zeros"]["P_w"].items()}
        tl = {int(f): x for f, x in P136["cells"][f"{g}-{t}-{M136.TOP[t]}"]["P_w"].items()}
        span_meas = None
        zr = [x for x in R["cells"][f"{g}-{t}-zeros"].get("burst_p800_w_runs", []) if x is not None]
        tr_ = [x for x in R["cells"][f"{g}-{t}-{M136.TOP[t]}"].get("burst_p800_w_runs", []) if x is not None]
        if zr and tr_:
            span_meas = sum(tr_) / len(tr_) - sum(zr) / len(zr)
            frac_meas = (p8 - sum(zr) / len(zr)) / span_meas
        else:
            frac_meas = None
        rows.append({"cell": cell, "p800_meas": round(p8, 2), "E136_law_800": round(lev136[800], 2), "T_S_800": round(levS[800], 2),
                     "err_E136_law": round(p8 - lev136[800], 2), "err_T_S": round(p8 - levS[800], 2), "phi_M8": round(phi[f"{t}.{kind}"], 4),
                     "span_fraction_measured_in_bursts": None if frac_meas is None else round(frac_meas, 3),
                     "span_fraction_E136_law": round((lev136[800] - zl[800]) / (tl[800] - zl[800]), 3)})
    return {"phi": phi, "rows": rows}


def main():
    inp = FG.load_inputs()
    sess = [c["session"] for c in inp]
    cfgs = {("P1",) + k: k for k in itertools.product((0.44, 0.47, 0.50), (0.1, 0.2, 0.3), (65.3, 65.5, 65.7))}
    with Pool(4, initializer=_init) as pool:
        p1 = dict(pool.map(run_p1, list(cfgs.items()), chunksize=1))
        p2 = dict(pool.map(run_p2, [(("P2", dg), dg) for dg in (0.12, 0.15, 0.18)], chunksize=1))
    err = {k: [{q: c["meas"][q] - p[q] for q in FG.RULE} for c, p in zip(inp, v)] for k, v in {**p1, **p2}.items()}
    nest, held = {}, []
    for s in FG.SESS:
        best = min(cfgs, key=lambda k: FG.loss_rows([e for e, ss in zip(err[k], sess) if ss != s]))
        e = [x for x, ss in zip(err[best], sess) if ss == s]
        nest[s] = {"chosen": list(best[1:]), "loss": round(FG.loss_rows(e), 3), "stats": FG.stats(e)}
        held += e
    L = json.load(open(os.path.join(HERE, "loso-g4.json")))
    g4n = {s: L["forward_steps"][2]["per_session"][s]["new"] for s in FG.SESS}
    out = {"what": "Q140(q) POST HOC (after fit_g4's registered result was read): P1 the start-die offset alone; P2 the dip's grid edge; P3 the span fraction in E136's bursts",
           "P1_start_offset_only": {"nested": nest, "pooled": FG.stats(held), "pooled_loss": round(sum(n["loss"] for n in nest.values()), 3),
                                    "G4_nested_loss_by_session": g4n, "G4_nested_pooled_loss": round(sum(g4n.values()), 3),
                                    "sessions_lower_than_G4": [s for s in FG.SESS if nest[s]["loss"] < g4n[s]]},
           "P2_dip_edge_in_sample": {str(k[1]): {"loss": round(FG.loss_rows(err[k]), 3), "stats": FG.stats(err[k])} for k in p2},
           "P3_E136_bursts": p3()}
    json.dump(out, open(os.path.join(HERE, "posthoc-g4.json"), "w"), indent=1)
    a = out["P1_start_offset_only"]
    print("P1 (post hoc): the start-die offset alone (k_s (T_start - T_ref) at the start, G3's in-run k_eff kept), T_Z and G4's dip, nested:")
    print(f"   pooled loss {a['pooled_loss']} against G4 nested {a['G4_nested_pooled_loss']}; lower than G4 in {a['sessions_lower_than_G4']}")
    print("   pooled: " + "  ".join(f"{q} {a['pooled'][q]['rms']:.3f} ({a['pooled'][q]['mean']:+.3f}) {a['pooled'][q]['inside']}/{a['pooled'][q]['n']}" for q in FG.RULE))
    print("   choices: " + ", ".join(f"{s} {v['chosen']}" for s, v in a["nested"].items()))
    print("P2 (post hoc, in sample): G4's final constants with d_G 0.12 / 0.15 / 0.18:")
    for k, v in out["P2_dip_edge_in_sample"].items():
        print(f"   d_G {k}: loss {v['loss']}  " + "  ".join(f"{q} {v['stats'][q]['rms']:.3f}" for q in FG.RULE))
    print("P3 (post hoc): E136's sparse50 and real bursts, p800 measured - level at 800 MHz (E136's law; T_S with M8's phi):")
    for r in out["P3_E136_bursts"]["rows"]:
        print(f"   {r['cell']:20s} meas {r['p800_meas']:6.2f}  E136 {r['err_E136_law']:+6.2f}  T_S {r['err_T_S']:+6.2f}  phi_M8 {r['phi_M8']:.3f}  "
              f"fraction measured {r['span_fraction_measured_in_bursts']}  E136's {r['span_fraction_E136_law']}")


if __name__ == "__main__":
    main()
