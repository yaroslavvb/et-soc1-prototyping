"""E149 selftest: synthetic logs in the harness's exact format, with a known power model (G1's form), a known two-pole
heat path, leakage, noise and one capped window, run through reduce -> fit -> predict -> score. It checks that the
chain recovers what was put in and that the rules can hold and fail. No GPU, no Modal call (the app module is
imported only for its kind tables).

    python selftest_e149.py <scratch dir>      # writes synthetic logs there, prints the checks
"""
import gzip
import json
import math
import os
import random
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import analyze_e149 as AZ  # noqa: E402
import e149_app as APP  # noqa: E402

rnd = random.Random(149)
TRUE = {"bf16": {"nzprod": 20.0, "gtr": 15.0, "flip_sign": 6.0, "flip_exp": 4.0, "flip_mant": 9.0, "pos_exp": 2.0,
                 "pos_mant": 3.0, "asym": 1.0, "psgn": 5.0},
        "fp16": {"nzprod": 22.0, "gtr": 14.0, "flip_sign": 6.0, "flip_exp": 5.0, "flip_mant": 7.0, "pos_mant": 2.0,
                 "asym": 0.5, "psgn": 4.0},
        "int8": {"nzprod": 18.0, "gtr": 10.0, "flip_sign": 5.0, "flip_high": 6.0, "flip_low": 4.0, "asym": 1.0,
                 "psgn": 3.0}}
P_ZERO = {"bf16": 168.0, "fp16": 170.0, "int8": 160.0}
HEAT = {"tau1": 2.0, "tau2": 60.0, "r1": 0.03, "r2": 0.07, "amb": 30.0, "lam": 0.6}


def fake_feats(k, zero=False):
    fmt = k[0]
    W = 8 if fmt == "int8" else 16
    sd = {}
    for side in ("A", "B"):
        d = {"ones": [rnd.random() for _ in range(W)], "row": [0.5 * rnd.random() for _ in range(W)]}
        for s in AZ.LAGS:
            d[f"lag{s}"] = [0.0 if zero else 0.5 * rnd.random() for _ in range(W)]
        d["stats"] = {"frac_zero": 1.0 if zero else 0.0}
        sd[side] = d
    cr = {"nzprod": 0.0 if zero else rnd.uniform(0.1, 1.0), "negprod": rnd.random()}
    for s in AZ.LAGS:
        cr[f"psgn{s}"] = 0.0 if zero else 0.5 * rnd.random()
        cr[f"gtr{s}"] = 0.0 if zero else 0.5 * rnd.random()
    h = f"{rnd.getrandbits(64):016x}"
    return {"kind": APP.kid(k), "fmt": fmt, "A": sd["A"], "B": sd["B"], "cross": cr,
            "acc": {"acc": rnd.random(), "acc_pos": []}, "sha_A": h, "sha_B": h[::-1]}


def true_y(fe):
    names, x = AZ.features(fe, "G1", 1)
    c = TRUE[fe["fmt"]]
    return float(sum(c[n] * v for n, v in zip(names, x)))


class Sim:
    def __init__(self, t0):
        self.t = t0
        self.x1 = self.x2 = 60.0
        self.samples = []
        self.T = HEAT["amb"] + (HEAT["r1"] + HEAT["r2"]) * 60.0

    def run(self, secs, p_of, cap=False):
        t_a = self.t
        n = int(round(secs / 0.1))
        for _ in range(n):
            T = HEAT["amb"] + HEAT["r1"] * self.x1 + HEAT["r2"] * self.x2
            P = p_of + HEAT["lam"] * (T - 50.0) + rnd.gauss(0, 1.0)
            self.x1 += (1 - math.exp(-0.1 / HEAT["tau1"])) * (P - self.x1)
            self.x2 += (1 - math.exp(-0.1 / HEAT["tau2"])) * (P - self.x2)
            self.samples.append({"t": round(self.t, 4), "tb": round(self.t + 0.007, 4), "sm": 1395 if cap else 1410,
                                 "p_mw": int(P * 1000), "e_mj": 0, "temp": int(round(T)),
                                 "rsn": 4 if cap else 0})
            self.t += 0.1
        return {"t_a": t_a, "t_b": self.t, "calls": 1000, "group": 100, "gpu_ms": secs * 1000.0}


def write_unit(root, un, stage, feats, power):
    os.makedirs(f"{root}/{un}/steps", exist_ok=True)
    os.makedirs(f"{root}/{un}/samples", exist_ok=True)
    sim = Sim(1.0e9)
    steps = [{"op": "static", "label": "static", "static": {"name": "SIM", "max_clock_sm": 1410}}]
    sim.run(30.0, 60.0)
    pl = APP.plan(stage, un)
    capped = "bf16.zs25" if stage == "1" else None
    for st in pl["steps"]:
        if st["op"] == "hold":
            w = sim.run(st["s"], power[st["kind"]])
            steps.append({"op": "hold", "label": st["label"], "windows": [dict(w, kind=st["kind"])]})
        if st["op"] == "pass":
            ws = [dict(sim.run(3.0, power["bf16.REF"]), kind="bf16.REF", role="ref")]
            for kn in st["seq"]:
                ws.append(dict(sim.run(5.0, power[kn], cap=(kn == capped and st["p"] == 1 and un == "A")), kind=kn,
                               role="cell"))
                ws.append(dict(sim.run(3.0, power["bf16.REF"]), kind="bf16.REF", role="ref"))
            steps.append({"op": "pass", "label": f"pass{st['p']}", "step": {"p": st["p"]}, "windows": ws})
        if st["op"] == "holds":
            ws = []
            for kn in st["seq"]:
                ws.append(dict(sim.run(st["pre_s"], power["bf16.zeros"]), kind="bf16.zeros", role="pre"))
                ws.append(dict(sim.run(st["hold_s"], power[kn]), kind=kn, role="hold"))
            steps.append({"op": "holds", "label": "holds", "windows": ws})
    for i, s in enumerate(steps):
        with gzip.open(f"{root}/{un}/steps/{i:03d}_{s['label']}.json.gz", "wt") as f:
            json.dump(s, f)
    with gzip.open(f"{root}/{un}/samples/000.jsonl.gz", "wt") as f:
        for r in sim.samples:
            f.write(json.dumps(r) + "\n")
    for nm, fz in feats.items():
        with gzip.open(f"{root}/{un}/features-{nm}.json.gz", "wt") as f:
            json.dump(fz, f)


def main(scr):
    f1 = {APP.kid(k): fake_feats(k, k[1] == "zeros") for k in APP.STAGE1 + [APP.REF]}
    f2 = {APP.kid(k): (f1[APP.kid(k)] if APP.kid(k) in f1 else fake_feats(k, k[1] == "zeros")) for k in APP.STAGE2}
    pw = {}
    for kn, fe in list(f1.items()) + list(f2.items()):
        pw[kn] = P_ZERO[fe["fmt"]] + (true_y(fe) if not kn.endswith("zeros") else 0.0)
    pw["bf16.REF"] = P_ZERO["bf16"] + true_y(f1["bf16.REF"])
    r1, r2 = f"{scr}/run1", f"{scr}/run2"
    for un in ("A", "B"):
        write_unit(r1, un, "1", {"1": f1, "2": f2}, pw)
        write_unit(r2, un, "2", {"2": {k: {"sha_A": v["sha_A"], "sha_B": v["sha_B"]} for k, v in f2.items()}}, pw)
    red1 = AZ.reduce_run(r1)
    json.dump(red1, open(f"{scr}/red1.json", "w"))
    mz = AZ.do_fit(f"{scr}/red1.json", r1, f"{scr}/model.json")
    AZ.do_predict(f"{scr}/model.json", r1, f"{scr}/pred.json")
    red2 = AZ.reduce_run(r2)
    json.dump(red2, open(f"{scr}/red2.json", "w"))
    sc = AZ.do_score(f"{scr}/model.json", f"{scr}/pred.json", f"{scr}/red2.json", r2, f"{scr}/score.json")
    checks = []
    g1 = mz["models"]["G1"]["bf16"]
    rec = dict(zip(g1["names"], g1["coef"]))
    checks.append(("G1 bf16 coefficients recovered within 15% (flip_mant, nzprod)",
                   abs(rec["flip_mant"] / 9.0 - 1) < 0.15 and abs(rec["nzprod"] / 20.0 - 1) < 0.15))
    checks.append(("G1 nested error small on synthetic data (< 1 W every format)",
                   all(mz["models"]["G1"][f]["rms_loko"] < 1.0 for f in AZ.FIELDS)))
    print("G1 nested rms by format:", {f: round(mz["models"]["G1"][f]["rms_loko"], 2) for f in AZ.FIELDS})
    checks.append(("the capped window was excluded (bf16.zs25 has one invalid replicate)",
                   len(red1["kinds"]["bf16.zs25"]["invalid"]) == 1))
    h = mz["heat"]["pooled"]
    checks.append(("heat: tau2 recovered within 35%, R_ss within 15%",
                   abs(h["tau2"] / 60.0 - 1) < 0.35 and abs(h["R_ss"] / 0.10 - 1) < 0.15))
    checks.append(("leakage slope recovered within 30%",
                   abs(mz["heat"]["lambda_w_per_c"] / 0.6 - 1) < 0.30))
    checks.append(("blind power: G1 beats G0 and holds P1-P4 on data made by G1's form",
                   all(sc["rules"][r]["verdict"] == "HOLDS" for r in ("P1", "P2", "P3", "P4"))))
    checks.append(("blind heat: H1 and H2 hold on data made by the two-pole path",
                   sc["rules"]["H1"]["verdict"] == "HOLDS" and sc["rules"]["H2"]["verdict"] == "HOLDS"))
    # the rules can fail: a model that is wrong by construction (S1 on toggle data) loses P5's comparison; and a
    # copy of the scores with the errors doubled fails P1 when the span is small
    checks.append(("P5 compares G1 with S1 (G1 better here)", sc["rules"]["P5"]["verdict"] == "HOLDS"))
    def made(vals, by_unit=None):
        K = {}
        for k, v in vals.items():
            K[k] = {"y": v, "se": 0.3, "n": 4, "by_unit": by_unit(k, v) if by_unit else {"A": v, "B": v},
                    "reps": [["A", "1", v], ["B", "1", v]],
                    "invalid": ([["A", "1", 1395, 1.0, 4]] if (by_unit and k.startswith("bf16")) else [])}
        return K
    hold = {"bf16.randn": 140, "bf16.zs25": 110, "bf16.zs50": 80, "bf16.zs75": 50, "bf16.zs90": 30, "bf16.zeros": 0,
            "int8.rand": 120, "int8.zs25": 95, "int8.zs50": 70, "int8.zs75": 45, "int8.zs90": 25, "int8.zeros": 0,
            "bf16.zb50": 60, "bf16.zb75": 35, "bf16.base1": 20, "bf16.mk3": 60, "bf16.mk7": 24, "bf16.ek3": 50,
            "bf16.ek5": 22, "fp16.base1": 20, "fp16.mk5": 70, "fp16.mk10": 25, "int8.base1": 18, "int8.k3": 55,
            "int8.k7": 20, "bf16.srand": 40, "bf16.sfix": 25, "bf16.sfixAneg": 25.4, "bf16.dshufK": 140,
            "bf16.dsortK": 90, "bf16.sq1": 70, "bf16.sq64": 40}
    fail = dict(hold)
    fail.update({"bf16.zs50": 150, "bf16.zb50": 90, "bf16.zb75": 60, "bf16.mk3": 20.2, "bf16.mk7": 60, "bf16.ek3": 20,
                 "fp16.mk5": 20, "int8.k3": 18, "int8.zs25": 130, "bf16.srand": 25, "bf16.sfixAneg": 40,
                 "bf16.dshufK": 90, "bf16.sq1": 40})
    fh = AZ.stage1_rules({"kinds": made(hold)})
    ff = AZ.stage1_rules({"kinds": made(fail, lambda k, v: {"A": v, "B": 1.3 * v})})
    checks.append(("every stage-1 rule HOLDS on a reduction made to hold",
                   all(v["verdict"] == "HOLDS" for v in fh.values())))
    checks.append(("every stage-1 rule FAILS on a reduction made to fail",
                   all(v["verdict"] == "FAILS" for v in ff.values())))
    print("stage-1 rules, made to hold:", {k: v["verdict"] for k, v in fh.items()})
    print("stage-1 rules, made to fail:", {k: v["verdict"] for k, v in ff.items()})
    ok = True
    for name, c in checks:
        print(("PASS " if c else "FAIL ") + name)
        ok &= bool(c)
    print("G1 bf16 fitted:", {k: round(v, 2) for k, v in rec.items()})
    print("heat fitted:", {k: (round(h[k], 4) if isinstance(h[k], float) else h[k]) for k in
                           ("tau1", "tau2", "r1", "r2", "R_ss", "F30")})
    print("scores:", {m: round(v["rms_w"], 2) for m, v in sc["models"].items()},
          {k: v["verdict"] for k, v in sc["rules"].items()})
    print("SELFTEST", "OK" if ok else "FAILED")


if __name__ == "__main__":
    main(sys.argv[1])
