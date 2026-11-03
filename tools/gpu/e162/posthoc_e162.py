"""E162 post hoc readings (no verdicts), from the committed files of the data directory, into posthoc.txt / posthoc.json.

    python posthoc_e162.py <data dir>

§1 approximate 95% intervals on the blind rms (bootstrap over the held-out kinds, seed 162);
§2 the blind scores without the two zero stripes (RK's two worst kinds) and per board;
§3 the heat cells per kind; §4 the seen-kinds arm per kind; §5 stage 1's ladders read model-free.
"""
import json
import os
import sys

import numpy as np


def J(d, f):
    return json.load(open(os.path.join(d, f)))


def rms(e):
    e = np.asarray(e, float)
    return float(np.sqrt(np.mean(e ** 2)))


def main():
    d = sys.argv[1]
    sc = J(d, "score-e162-a100.json")
    red2 = J(d, "reduce-a2.json")
    red1 = J(d, "reduce-a1.json")
    out, txt = {}, []
    blind = sc["blind"]
    models = ["RK", "G1", "G1p", "G4p", "e149_S1", "e149_G0"]
    rng = np.random.default_rng(162)
    idx = rng.integers(0, len(blind), size=(10000, len(blind)))
    s1 = {}
    for m in models:
        e = np.array([sc["per_kind"][k]["err"][m] for k in blind])
        bs = np.sqrt(np.mean(e[idx] ** 2, axis=1))
        s1[m] = {"rms": rms(e), "ci95": [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))]}
    out["s1_rms_intervals"] = s1
    txt.append("§1 blind rms over %d held-out kinds, approximate 95%% intervals (bootstrap over kinds):" % len(blind))
    for m, v in s1.items():
        txt.append(f"   {m:<8} {v['rms']:7.2f} W  [{v['ci95'][0]:.2f}, {v['ci95'][1]:.2f}]")
    span = J(d, "model-e162-a100.json")["span_w"]
    txt.append(f"   as a share of E149's span S = {span:.2f} W: RK {s1['RK']['rms'] / span:.3f}, G1 {s1['G1']['rms'] / span:.3f}")
    out["span_w"] = span
    drop = ["bf16.stripeK0", "bf16.stripeR0"]
    rest = [k for k in blind if k not in drop]
    s2 = {m: rms([sc["per_kind"][k]["err"][m] for k in rest]) for m in models}
    out["s2_without_stripes"] = s2
    txt.append("§2 without the two zero stripes (%d kinds): " % len(rest) +
               ", ".join(f"{m} {v:.2f} W" for m, v in s2.items()))
    byb = {}
    for b in sorted(red2["units"]):
        byb[b] = {}
        for m in ("RK", "G1"):
            e = [red2["kinds"][k]["by_unit"][b] - sc["per_kind"][k]["pred"][m] for k in blind
                 if b in red2["kinds"][k]["by_unit"]]
            byb[b][m] = {"rms": rms(e), "bias": float(np.mean(e)), "n": len(e)}
    out["s2_by_board"] = byb
    txt.append("   by board: " + "; ".join(f"{b}: RK {v['RK']['rms']:.2f} (bias {v['RK']['bias']:+.2f}), G1 "
                                         f"{v['G1']['rms']:.2f} (bias {v['G1']['bias']:+.2f})" for b, v in byb.items()))
    for k in drop:
        v = sc["per_kind"][k]
        txt.append(f"   {k}: measured {v['meas']:.1f} W, RK {v['pred']['RK']:.1f} (error {v['err']['RK']:+.1f}), "
                   f"G1 {v['pred']['G1']:.1f} (error {v['err']['G1']:+.1f})")
    ht = sc["heat_cells"]
    out["s3_heat_cells"] = ht
    txt.append("§3 heat cells (die reading over the references, °C; mean of each kind's replicates): rms measured-power "
               f"{ht['rms_measP_c']:.3f} (bias {ht['bias_measP_c']:+.3f}), RK {ht['rms_RK_c']:.3f} "
               f"(bias {ht['bias_RK_c']:+.3f}), G1 {ht['rms_G1_c']:.3f} (bias {ht['bias_G1_c']:+.3f})")
    for k in sorted(ht["rows"]):
        r = ht["rows"][k]
        txt.append(f"   {k:<16} measured {r['meas_dT']:+6.2f}  measured P {r['measP']:+6.2f}  RK {r['RK']:+6.2f}  "
                   f"G1 {r['G1']:+6.2f}")
    a = sc["seen_kinds_e149_stage2"]
    out["s4_seen_kinds"] = a
    txt.append("§4 the seen-kinds arm (E149's 17 held-out kinds on E149's stage-2 boards; not blind to the designer):")
    for k in sorted(a["per_kind"]):
        v = a["per_kind"][k]
        txt.append(f"   {k:<18} measured {v['meas']:7.1f}  RK {v['RK']:7.1f}  G1 {v['G1']:7.1f}  G4p {v['G4p']:7.1f}")
    txt.append("   rms: " + ", ".join(f"{m} {a[m]['rms_w']:.2f} W" for m in ("RK", "G1p", "G4p", "G1")) +
               f"; without the checkerboard RK {rms([v['meas'] - v['RK'] for k, v in a['per_kind'].items() if k != 'bf16.checker']):.2f}"
               f", G1 {rms([v['meas'] - v['G1'] for k, v in a['per_kind'].items() if k != 'bf16.checker']):.2f} W")
    K = red1["kinds"]
    lad = {"kS": {b: K[f"bf16.kS{b}"]["y"] for b in (1, 2, 4, 8, 16, 32, 64)},
           "rS": {b: K[f"bf16.rS{b}"]["y"] for b in (1, 2, 4, 8, 16, 32, 64)}}
    out["s5_ladders"] = lad
    txt.append("§5 stage 1 model-free: K waves with no row flips (kS, W): " +
               ", ".join(f"b{b} {v:.1f}" for b, v in lad["kS"].items()) +
               "; row waves with no K flips (rS, W): " + ", ".join(f"b{b} {v:.1f}" for b, v in lad["rS"].items()))
    txt.append("   the row term at fixed K flips (per-row phase minus shared, W): " + ", ".join(
        f"b{b} {K[f'bf16.sq{b}']['y'] - K[f'bf16.kS{b}']['y']:+.1f}" for b in (1, 16, 64)))
    txt.append("   one side only: K wave b1 on A {:.1f}, on B {:.1f}; row wave b1 on A {:.1f}, on B {:.1f} W".format(
        K["bf16.kS1A"]["y"], K["bf16.kS1B"]["y"], K["bf16.rS1A"]["y"], K["bf16.rS1B"]["y"]))
    json.dump(out, open(os.path.join(d, "posthoc.json"), "w"), indent=1, sort_keys=True)
    open(os.path.join(d, "posthoc.txt"), "w").write("\n".join(txt) + "\n")
    print("\n".join(txt))


if __name__ == "__main__":
    main()
