#!/usr/bin/env python3
"""Q140(q): G4's registered reported checks (REGISTRATION.md A5 (i)-(iii), 49575094), with the frozen g4.json. No selection.

    /usr/bin/python3 -B checks_g4.py > checks-g4.txt      (writes checks-g4.json)

(i)   E158's 42 zeros bursts (never in P0's fit): the first second's board at 800 MHz (E158 results.json rules.R7.cells.*.p800_w) against
      P0 (R7's, strict lines), P0 + beta x delta (T_Z) and P0 + beta x delta + k_D (T_start - T_ref) (T_Z + T_D), T_start the burst's
      die start (cells.*.burst_die_start, the runs' mean).
(ii)  E159's three zeros holds: the measured window boards' spread against G3's and G4's (rows-g4.json).
(iii) E136's four other-kind sustained runs (g4k fp32 real, fp32 sparse50, int8 real, fp16 real): G4 (final constants) on E136's
      frozen levels (E95's r_real, E107's sparse50 S) against G4 with T_S, M8's span fraction phi = D_M8(kind) / D_M8(top).
SPDX-License-Identifier: Apache-2.0
"""
import json
import math
import os
import sys

sys.dont_write_bytecode = True
import numpy as np  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import g4_model as G4  # noqa: E402

LAB = G4.LAB
C4 = json.load(open(os.path.join(HERE, "g4.json")))["constants"]
RULE = {"mhz": 15.0, "w": 2.0, "die": 1.0}


def rms(v):
    return math.sqrt(sum(x * x for x in v) / len(v)) if v else None


def check_i():
    r = json.load(open(os.path.join(LAB, "docs/reports/data/2026-11-03-e158-l3-retention/results.json")))
    R7, cells = r["rules"]["R7"]["cells"], r["cells"]
    rows = []
    kD = C4["k_W_per_C"] if C4.get("T_ref_C") else None
    kd_use = kD if kD is not None else 0.47
    for c, v in sorted(R7.items()):
        t = c.split("-")[1]
        ds = [x for x in cells[c]["burst_die_start"] if x is not None]
        Ts = sum(ds) / len(ds)
        sh = G4.BETA * G4.DELTA_FALLBACK[t]
        rows.append({"cell": c, "p800": v["p800_w"], "P0": v["P0"], "die_start": round(Ts, 2),
                     "err_P0": round(v["p800_w"] - v["P0"], 3), "err_Z": round(v["p800_w"] - v["P0"] - sh, 3),
                     "err_ZD": round(v["p800_w"] - v["P0"] - sh - kd_use * (Ts - G4.T_REF), 3)})
    out = {"n": len(rows), "k_D_used": kd_use, "k_D_is_G4s": kD is not None,
           "rms": {k: round(rms([x[k] for x in rows]), 3) for k in ("err_P0", "err_Z", "err_ZD")},
           "mean": {k: round(sum(x[k] for x in rows) / len(rows), 3) for k in ("err_P0", "err_Z", "err_ZD")},
           "die_start_range": [min(x["die_start"] for x in rows), max(x["die_start"] for x in rows)], "rows": rows}
    return out


def check_ii():
    rows = json.load(open(os.path.join(HERE, "rows-g4.json")))
    z = [x for x in rows if x["session"] == "E159" and x["cell"].endswith("zeros")]
    out = {"holds": [{"cell": x["cell"], "T_start": x["T_start"], "meas_w": x["meas"]["w"], "meas_die": x["meas"]["die"], "G3_as_frozen_w": x["G3_as_frozen"]["w"],
                      "G4_nested_w": x["G4_nested"]["w"], "G4_final_w": x["G4_final"]["w"], "G4_final_die": x["G4_final"]["die"]} for x in z]}
    for k in ("meas_w", "G3_as_frozen_w", "G4_nested_w", "G4_final_w"):
        v = [h[k] for h in out["holds"]]
        out[f"spread_{k}"] = round(max(v) - min(v), 3)
    out["miss_G4_nested_w"] = [round(h["meas_w"] - h["G4_nested_w"], 3) for h in out["holds"]]
    out["miss_G3_as_frozen_w"] = [round(h["meas_w"] - h["G3_as_frozen_w"], 3) for h in out["holds"]]
    return out


def check_iii():
    sys.path.insert(0, os.path.join(LAB, "tools/claims-v3/kinds"))
    import e101_common as EC  # noqa: E402
    inp = json.load(open(os.path.join(G4.G3D, "posthoc-g3-inputs.json")))
    P136 = json.load(open(os.path.join(LAB, "tools/claims-v3/e136/predictions-e136.json")))
    M136 = G4._m136()
    top = {"fp32": "fp32.randn", "fp16": "fp16.randn", "int8": "int8.full"}
    keys = [("E78", "a3", top[t]) for t in top] + [("E78", "a3", "fp32.sparse50")]
    for t in ("fp32", "fp16", "int8"):
        keys += [("E95", "a3", f"{t}.real2:{n}") for n in EC.REAL_SET[t]]
    D = G4.m8_D_rows(keys)
    phi = {}
    for t in ("fp32", "fp16", "int8"):
        vals = [D[("E95", "a3", f"{t}.real2:{n}")]["D_M8"] for n in EC.REAL_SET[t] if D.get(("E95", "a3", f"{t}.real2:{n}"))]
        phi[f"{t}.real"] = {"phi_M8": sum(vals) / len(vals) / D[("E78", "a3", top[t])]["D_M8"] if vals else None, "n_tiles_with_M8": len(vals),
                            "r_real_E136": round(M136.r_real(t), 4)}
    phi["fp32.sparse50"] = {"phi_M8": D[("E78", "a3", "fp32.sparse50")]["D_M8"] / D[("E78", "a3", "fp32.randn")]["D_M8"]}
    # self-check: levels_phi136 at E136's own r_real reproduces E136's frozen real levels
    selfchk = {}
    for t in ("fp32", "fp16", "int8"):
        mine = G4.levels_phi136("g4k", t, M136.r_real(t))
        ref = {int(f): v for f, v in P136["cells"][f"g4k-{t}-real"]["P_w"].items()}
        selfchk[t] = round(max(abs(mine[f] - ref[f]) for f in (600, 700, 800)), 4)
    arm = {"k": C4["k_W_per_C"], "trip": C4["trip_C"], "T_ref": C4["T_ref_C"], "zeros": C4["zeros_level"],
           "dip": None if not C4["dip"] else (C4["dip"]["d_G"], C4["dip"]["P_G_w"])}
    runs = []
    for c in inp:
        if c["session"] != "E136" or not any(c["cell"].endswith(k) for k in ("-real", "-sparse50")):
            continue
        c = dict(c, type=G4.cell_type(c["cell"]))
        t = c["type"]
        kind = "real" if c["cell"].endswith("-real") else "sparse50"
        ph = phi[f"{t}.{kind}"]["phi_M8"]
        p_e136 = G4.run_arm(c, arm)
        lev_s = G4.levels_phi136("g4k", t, ph)
        p_s = G4.run_arm(c, dict(arm, lev=lev_s))
        runs.append({"cell": c["cell"], "phi_M8": round(ph, 4), "meas": {q: round(c["meas"][q], 3) for q in RULE},
                     "P0_E136_w": {str(f): round(v, 2) for f, v in c["lev"].items()}, "P0_T_S_w": {str(f): round(v, 2) for f, v in lev_s.items()},
                     "err_G4_on_E136_levels": {q: round(c["meas"][q] - p_e136[q], 3) for q in RULE},
                     "err_G4_with_T_S": {q: round(c["meas"][q] - p_s[q], 3) for q in RULE}})
    summ = {a: {q: round(rms([r[a][q] for r in runs]), 3) for q in RULE} for a in ("err_G4_on_E136_levels", "err_G4_with_T_S")}
    return {"phi": phi, "levels_phi136_selfcheck_max_abs_w": selfchk, "runs": runs, "rms": summ}


def main():
    out = {"what": "Q140(q) G4's reported checks (registered A5 (i)-(iii)); no selection", "g4_constants": C4,
           "i_E158_zeros_bursts": check_i(), "ii_E159_zeros_spread": check_ii(), "iii_E136_other_kinds_T_S": check_iii()}
    json.dump(out, open(os.path.join(HERE, "checks-g4.json"), "w"), indent=1)
    a = out["i_E158_zeros_bursts"]
    print(f"(i) E158's {a['n']} zeros bursts, p800 - predicted, rms (mean): P0 {a['rms']['err_P0']} ({a['mean']['err_P0']:+}); + T_Z {a['rms']['err_Z']} ({a['mean']['err_Z']:+}); "
          f"+ T_Z + T_D at k_D {a['k_D_used']} {a['rms']['err_ZD']} ({a['mean']['err_ZD']:+}); die starts {a['die_start_range']}")
    b = out["ii_E159_zeros_spread"]
    print(f"(ii) E159's zeros holds: measured spread {b['spread_meas_w']} W; G3 as frozen {b['spread_G3_as_frozen_w']}; G4 nested {b['spread_G4_nested_w']}; "
          f"G4 final {b['spread_G4_final_w']}; misses G4 nested {b['miss_G4_nested_w']}, G3 {b['miss_G3_as_frozen_w']}")
    c = out["iii_E136_other_kinds_T_S"]
    print(f"(iii) E136's other kinds: phi {json.dumps({k: (None if v['phi_M8'] is None else round(v['phi_M8'], 4)) for k, v in c['phi'].items()})}; "
          f"self-check {c['levels_phi136_selfcheck_max_abs_w']}; rms {c['rms']}")
    for r in c["runs"]:
        print(f"    {r['cell']:20s} phi {r['phi_M8']}: E136 levels {r['err_G4_on_E136_levels']} | T_S {r['err_G4_with_T_S']}")


if __name__ == "__main__":
    main()
