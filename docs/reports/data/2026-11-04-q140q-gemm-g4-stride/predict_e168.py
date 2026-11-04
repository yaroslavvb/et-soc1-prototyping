#!/usr/bin/env python3
"""Q140(q): E168's frozen predictions (REGISTRATION.md A6-A8, 49575094): G4 (g4.json, frozen by fit_g4.py) for nine holds of three
shapes nobody has run, on aifoundry2 under its own governor, with G3 as frozen and E136's law beside it. Desk only.

    /usr/bin/python3 -B predict_e168.py > predictions-e168.txt        (writes predictions-e168.json)

Levels: E146's levels0 on the desk's 32 MB split (E146's make_predictions_e146 and reuse_e146, unchanged), for fp32 random, int8
zeros and int8 full; the int8 W8A8 real tile and int8 sparse50 through T_S, every arm's energy S(zeros) + phi (S(top) - S(zeros)),
phi = D_M8(kind) / D_M8(int8 full) (M8's frozen D: pool 6's predictions-blind6-aifoundry3.json for the W8A8 tile, blind for M8;
E78's aifoundry3 rows in rows-m8.json for int8 full and int8 sparse50, in sample for M8). The registered primary is G4 run from
each hold's own measured start (score_e168.py); the nominal starts below put the same model on record as numbers: "cold", the chain
at rest at 46.0 C; "warm55", after the same shape's fp32 random hold from cold, idle until the die reads 55 C.
SPDX-License-Identifier: Apache-2.0
"""
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
G4J = json.load(open(os.path.join(HERE, "g4.json")))
C4 = G4J["constants"]
SHAPES = {"S1": (1, 3, 3), "S2": (3, 3, 2), "S3": (3, 5, 3)}
HOLDS = [("S1", "fp32", "randn", "cold"), ("S1", "fp32", "randn", "warm55"), ("S2", "fp32", "randn", "cold"), ("S2", "fp32", "randn", "warm55"),
         ("S3", "fp32", "randn", "cold"), ("S3", "fp32", "randn", "warm55"), ("S2", "int8", "zeros", "warm55"),
         ("S2", "int8", "real_smol_w8a8_down", "warm55"), ("S2", "int8", "sparse50", "warm55")]
N_PROC, SECONDS = 12, 8.0
PEAK_MARGIN_W, PEAK_LIMIT_W = 8.51, 82.0
T_COLD, T_WARM = 46.0, 55.0
RULE = {"mhz": 15.0, "w": 2.0, "die": 1.0}
W8A8_FILE = "tools/claims-v3/kinds/blind6/tiles/int8/int8.real_smol_w8a8_down.bin"


def label(s, t, k, start):
    return f"{s}-{t}-{k}-{start}"


def values(s, t, k):
    MB, NB, KB = SHAPES[s]
    arm = f"gemmL{MB}x{NB}x{KB}"
    if k == "zeros":
        return f"{arm}:tiles:tools/claims-v3/kinds/tiles/{t}/zeros.bin"
    if k == "randn":
        return f"{arm}:randn:tools/claims-v3/kinds/tiles/{t}/randn.bin"
    if k == "sparse50":
        return f"{arm}:sparse50:tools/claims-v3/kinds/tiles/{t}/sparse50.bin"
    return f"{arm}:tiles:{W8A8_FILE}"


def phis():
    m = G4.m8_D_rows([("E78", "a3", "int8.full"), ("E78", "a3", "int8.sparse50"), ("E78", "a3", "fp32.randn"), ("E78", "a3", "fp32.sparse50")])
    pool = json.load(open(os.path.join(LAB, "tools/claims-v3/kinds/blind6/predictions-blind6-aifoundry3.json")))
    dw = pool["tiles"]["int8.real_smol_w8a8_down"]["M8"]["D600_a3_footing_w"]
    dfull = m[("E78", "a3", "int8.full")]["D_M8"]
    return {"real_smol_w8a8_down": {"phi": dw / dfull, "D_M8_w": dw, "D_M8_top_w": dfull, "source": "predictions-blind6-aifoundry3.json (blind for M8) over E78 a3 int8.full (rows-m8.json)"},
            "sparse50": {"phi": m[("E78", "a3", "int8.sparse50")]["D_M8"] / dfull, "D_M8_w": m[("E78", "a3", "int8.sparse50")]["D_M8"], "D_M8_top_w": dfull,
                         "D_meas_w": m[("E78", "a3", "int8.sparse50")]["D_meas"], "source": "rows-m8.json E78 a3 (in sample for M8)"},
            "fp32_sparse50_for_reference": {"phi": m[("E78", "a3", "fp32.sparse50")]["D_M8"] / m[("E78", "a3", "fp32.randn")]["D_M8"]}}


def levels(s, t, k, PH):
    M146, _ = G4._m146()
    if k == "zeros":
        return M146.levels0(s, t, "zeros")
    if k in ("randn", "full"):
        return M146.levels0(s, t, "top")
    return G4.levels_phi146(s, t, PH[k]["phi"])


def g4_arm():
    return {"k": C4["k_W_per_C"], "trip": C4["trip_C"], "T_ref": C4["T_ref_C"], "zeros": C4["zeros_level"],
            "dip": None if not C4["dip"] else (C4["dip"]["d_G"], C4["dip"]["P_G_w"])}


def run_model(lev, t, arm, start, prev_lev):
    g, on, wins = G.run_schedule(N_PROC, SECONDS)
    t_end = wins[-1][1]
    x0 = np.zeros(len(G.TAU))
    shift_prev = G4.BETA * G4.DELTA_FALLBACK["fp32"] if arm.get("zeros") else 0.0
    if start == "warm55":
        Tp, Pp, Fp = G4.simulate4(prev_lev, on, x0, T_COLD, T_COLD, arm["trip"], arm["k"], T_ref=arm.get("T_ref"), shift=shift_prev, dip=arm.get("dip"))
        x = G.chain_open(Pp)[-1]
        while T_COLD + float(G.R @ x) > T_WARM:
            x = G.A * x
        x0 = x
    T0 = T_COLD + float(G.R @ x0)
    shift = G4.BETA * G4.DELTA_FALLBACK[t] if arm.get("zeros") else 0.0
    T, P, F = G4.simulate4(lev, on, x0, T_COLD, T0, arm["trip"], arm["k"], T_ref=arm.get("T_ref"), shift=shift, dip=arm.get("dip"))
    w = G.window_means(g, on, T, P, F, t_end)
    return {"mhz": round(w["mhz"], 2), "w": round(w["w"], 3), "die": round(w["die"], 3), "die_start": round(T0, 2), "peak_w_traj": round(float(np.max(P)), 2)}


def main():
    PH = phis()
    split = {s: G4.add_shape146(s, *b) for s, b in SHAPES.items()}
    M146, _ = G4._m146()
    # self-check: levels_phi146 at phi 0 and 1 reproduce E146's levels0 for zeros and top
    chk = max(abs(G4.levels_phi146("S2", "int8", 0.0)[f] - M146.levels0("S2", "int8", "zeros")[f]) for f in (600, 700, 800))
    chk = max(chk, max(abs(G4.levels_phi146("S2", "int8", 1.0)[f] - M146.levels0("S2", "int8", "top")[f]) for f in (600, 700, 800)))
    arm4 = g4_arm()
    arm3 = {"k": G.K_LEAK_G3, "trip": G.TRIP_G3}
    cells = {}
    for s, t, k, start in HOLDS:
        lev = levels(s, t, k, PH)
        prev = levels(s, "fp32", "randn", PH)
        peak = lev[800] + PEAK_MARGIN_W
        rec = {"shape": s, "arm": f"gemmL{SHAPES[s][0]}x{SHAPES[s][1]}x{SHAPES[s][2]}", "type": t, "kind": k, "start": start, "values": values(s, t, k),
               "P0_w": {str(f): round(v, 3) for f, v in lev.items()}, "predicted_peak_w": round(peak, 2), "runs_as_designed": peak <= PEAK_LIMIT_W,
               "G4": run_model(lev, t, arm4, start, prev), "G3_as_frozen": run_model(lev, t, arm3, start, prev)}
        rec["E136_law"] = {q: round(v, 3) for q, v in G.e136_law(lev, rec["G4"]["die_start"]).items()}
        rec["both_nominal_starts"] = {st: {"G4": run_model(lev, t, arm4, st, prev), "G3_as_frozen": run_model(lev, t, arm3, st, prev)} for st in ("cold", "warm55")}
        if t == "int8":
            rec["int8_full_P0_w"] = {str(f): round(v, 3) for f, v in levels(s, "int8", "full", PH).items()}
        cells[label(s, t, k, start)] = rec
    # the increment rule's span: G4's 800 MHz level difference int8 full - int8 zeros at S2 at the hold's window die
    zl = cells[label("S2", "int8", "zeros", "warm55")]
    for k in ("real_smol_w8a8_down", "sparse50"):
        c = cells[label("S2", "int8", k, "warm55")]
        span = levels("S2", "int8", "full", PH)[800] - levels("S2", "int8", "zeros", PH)[800]
        c["increment_rule"] = {"predicted_increment_w": round(c["G4"]["w"] - zl["G4"]["w"], 3), "span_w": round(span, 3), "band_w": round(0.15 * span, 3),
                               "phi": round(PH[k]["phi"], 4)}
    design = {"card": "aifoundry2 card 0, its own governor (65 W / 65 C read, never set)", "binary": "E136's rgm136 SP_GEMM_LARGE, unchanged",
              "shapes": {s: {"arm": f"gemmL{b[0]}x{b[1]}x{b[2]}", "MNK_fp32": [b[0] * 1024, b[1] * 512, b[2] * 512],
                             "footprint_MB": {"A": b[0] * b[2] * 2, "B": b[2] * b[1], "C": b[0] * b[1] * 2, "total": b[0] * b[2] * 2 + b[2] * b[1] + b[0] * b[1] * 2},
                             "store_every_ops": b[2] * 32, "lines_32MB": split[s]} for s, b in SHAPES.items()},
              "order": [label(*h) for h in HOLDS],
              "hold": {"processes": N_PROC, "seconds": SECONDS, "budget": 9.5, "tail_s": 6, "window": "in-kernel samples of the last 40 s of work (reduce_hpl SUS_LAST_S)",
                       "starts": {"cold": "the card at rest, die about 46 C (wait for it, bounded)", "warm55": "after the preceding hold, idle until the die reads 55 C"}},
              "stops": {"abs_stop_c": 76, "board_cap_w": 85, "cap_consecutive": 3},
              "power_rule": f"predicted peak = P0(800) + {PEAK_MARGIN_W} W (G3's frozen rule, no level term) <= {PEAK_LIMIT_W} W; a hold above it is duty-cycled or dropped",
              "budget": "about 45 card-minutes planned (nine holds of about 106 s, three rests to about 46 C, idles to 55 C, smoke and stop tests); cap 55; registered subset the six fp32 random holds",
              "device_commands": "E159's chain unchanged (ettelem sample without --reset-ms, ettelem config, ettelem sptrace, sparsity_host); every command READ; the lane re-runs tools/claims-v3/dmcmd_audit.py before its claim"}
    out = {"what": "Q140(q): G4's frozen predictions for E168 (aifoundry2, its own governor); nothing of E168 exists", "date": "2026-11-04", "registration": "49575094",
           "g4": G4J, "g4_sha256": hashlib.sha256(open(os.path.join(HERE, "g4.json"), "rb").read()).hexdigest(),
           "span_fractions": PH, "levels_phi_selfcheck_max_abs_w": chk,
           "rules": {"per_hold": RULE, "pass": "each quantity inside on at least 8 of the 9 holds (measured - G4)",
                     "increment": "int8 W8A8 real and int8 sparse50 at S2: (window board minus int8 zeros' at S2), measured vs G4, within 15% of the span (G4's frozen 800 MHz level int8 full - int8 zeros at S2)",
                     "beside": "E136's law and G3 as frozen, scored the same way; the chain on the measured trace (heat alone)",
                     "primary": "G4 run from each hold's own measured start (score_e168.py); T_Z on the fallback; if the session ran kinds zeros anchors, an arm with its own delta"},
           "design": design, "cells": cells}
    json.dump(out, open(os.path.join(HERE, "predictions-e168.json"), "w"), indent=1)
    print("Q140(q) frozen G4 predictions for E168 (aifoundry2, its own governor). G4 constants:", json.dumps(C4))
    print("span fractions (M8):", json.dumps({k: round(v["phi"], 4) for k, v in PH.items()}), f"; levels_phi self-check max |diff| {chk:.2e} W")
    for s, d in design["shapes"].items():
        print(f"  {s} {d['arm']}: M x N x K fp32 {d['MNK_fp32']}, {d['footprint_MB']['total']} MB with C; lines an op missing the L2: L3 {d['lines_32MB']['n_L3']}, fresh {d['lines_32MB']['n_F']}")
    print(f"{'hold':34s} {'P0 600/700/800':>20s} {'peak':>6s} | {'G4: MHz':>8s} {'W':>7s} {'die':>6s} {'start':>6s} | {'G3: MHz':>8s} {'W':>7s} {'die':>6s} | {'E136 law':>16s}")
    for lab, c in cells.items():
        P0, a, b, l = c["P0_w"], c["G4"], c["G3_as_frozen"], c["E136_law"]
        print(f"{lab:34s} {P0['600']:6.2f}/{P0['700']:6.2f}/{P0['800']:6.2f} {c['predicted_peak_w']:6.1f} | {a['mhz']:8.1f} {a['w']:7.2f} {a['die']:6.2f} {a['die_start']:6.1f} | "
              f"{b['mhz']:8.1f} {b['w']:7.2f} {b['die']:6.2f} | {l['mhz']:5.1f} {l['w']:5.1f} {l['die']:5.1f}")
    for k in ("real_smol_w8a8_down", "sparse50"):
        print(f"increment rule {k}: {cells[label('S2', 'int8', k, 'warm55')]['increment_rule']}")


if __name__ == "__main__":
    main()
