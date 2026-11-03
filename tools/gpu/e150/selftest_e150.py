"""E150 selftest: synthetic logs in the harness's format for the measured run (plan "M": phase L, phase H, holds) on
two boards, with power made by E149's frozen G1 times a known per-board scale and the measured multiply-add rate, a
known two-pole heat path with leakage (E149's selftest simulator), and noise; run through reduce L -> freeze ->
reduce H -> score. It checks that the chain recovers the scales and the heat path and that the rules hold on data made
by the frozen form, then that they fail on data the form does not make. No GPU, no Modal call.

    python selftest_e150.py <scratch dir>
"""
import gzip
import json
import os
import random
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "e149"))
import analyze_e150 as AE  # noqa: E402
import analyze_e149 as AZ  # noqa: E402
import e150_app as APP  # noqa: E402
import selftest_e149 as ST9  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
D149 = os.path.join(ROOT, "docs", "reports", "data", "2026-11-02-e149-gpu-model-check")
MZ = json.load(open(os.path.join(D149, "model-e149.json")))
RED1 = os.path.join(D149, "reduce-stage1.json")
C_TRUE = {"A": 1.30, "B": 1.40}
TF_NEW = {"bf16": 60.0, "fp16": 62.0, "int8": 120.0}
SIZES = {"bf16": 1536, "fp16": 1536, "int8": 1024}
rnd = random.Random(150)


def write_unit(root, un, feats, power):
    os.makedirs(f"{root}/{un}/steps", exist_ok=True)
    os.makedirs(f"{root}/{un}/samples", exist_ok=True)
    sim = ST9.Sim(1.0e9)
    steps = [{"op": "static", "label": "static", "static": {"name": "SIM", "max_clock_sm": 1410}}]
    sim.run(30.0, 60.0)
    pl = APP.plan("M", un, SIZES)

    def win(secs, kn, cap=False):
        f = kn.split(".")[0]
        n = SIZES[f]
        w = sim.run(secs, power[kn], cap=cap)
        calls = int(round(TF_NEW[f] * 1e12 * secs / (2.0 * n ** 3)))
        return dict(w, kind=kn, n=n, calls=calls, gpu_ms=secs * 1000.0)
    for st in pl["steps"]:
        if st["op"] == "hold":
            steps.append({"op": "hold", "label": st["label"], "windows": [win(st["s"], st["kind"])]})
        if st["op"] == "pass":
            ws = [dict(win(3.0, "bf16.REF"), role="ref")]
            for kn in st["seq"]:
                ws.append(dict(win(5.0, kn, cap=(kn == "bf16.zs25" and st["p"] == 1 and un == "A")), role="cell"))
                ws.append(dict(win(3.0, "bf16.REF"), role="ref"))
            steps.append({"op": "pass", "label": f"pass{st['p']}", "step": {"p": st["p"]}, "windows": ws})
        if st["op"] == "holds":
            ws = []
            for kn in st["seq"]:
                ws.append(dict(win(st["pre_s"], "bf16.zeros"), role="pre"))
                ws.append(dict(win(st["hold_s"], kn), role="hold"))
            steps.append({"op": "holds", "label": "holds", "windows": ws})
    for i, s in enumerate(steps):
        with gzip.open(f"{root}/{un}/steps/{i:03d}_{s['label']}.json.gz", "wt") as f:
            json.dump(s, f)
    with gzip.open(f"{root}/{un}/samples/000.jsonl.gz", "wt") as f:
        for r in sim.samples:
            f.write(json.dumps(r) + "\n")
    with gzip.open(f"{root}/{un}/features-M.json.gz", "wt") as f:
        json.dump(feats, f)
    with open(f"{root}/{un}/plan.json", "w") as f:
        json.dump(pl, f)


def t100():
    red1 = json.load(open(RED1))
    out = {}
    for f in AE.FMTS:
        v = [x["tflops"] for k, x in red1["kinds"].items() if k.startswith(f + ".") and x.get("tflops")]
        out[f] = float(np.mean(v))
    return out


def make_run(root, feats, extra):
    T100 = t100()
    for un in ("A", "B"):
        pw = {}
        for kn, fe in feats.items():
            f = fe["fmt"]
            y = 0.0
            if not kn.endswith("zeros"):
                y = C_TRUE[un] * TF_NEW[f] / T100[f] * AZ.predict_one(MZ["models"]["G1"][f], fe) + extra.get(kn, 0.0)
            pw[kn] = ST9.P_ZERO[f] + y
        write_unit(root, un, feats, pw)


def chain(scr, tag, extra):
    run = f"{scr}/{tag}"
    make_run(run, FEATS, extra)
    redL = AE.reduce_phase(run, "L")
    json.dump(redL, open(f"{scr}/{tag}-redL.json", "w"))
    pz = AE.do_freeze(f"{scr}/{tag}-redL.json", run, os.path.join(D149, "model-e149.json"), RED1,
                      f"{scr}/{tag}-pred.json")
    redH = AE.reduce_phase(run, "H")
    json.dump(redH, open(f"{scr}/{tag}-redH.json", "w"))
    sc = AE.do_score(f"{scr}/{tag}-pred.json", f"{scr}/{tag}-redH.json", run, f"{scr}/{tag}-score.json")
    return redL, pz, sc


def main(scr):
    global FEATS
    kinds = APP.PHASE_L + APP.PHASE_H + [APP.REF]
    FEATS = {APP.kid(k): ST9.fake_feats(k, k[1] == "zeros") for k in kinds}
    FEATS["bf16.REF"] = dict(FEATS["bf16.randn"], kind="bf16.REF")
    checks = []
    redL, pz, sc = chain(scr, "hold", {})
    c = pz["scales"]["G1"]["per_board"]
    rr = pz["rate_ratio"]["A"]
    T100 = t100()
    checks.append(("the measured rate ratio is the simulated one (bf16, int8)",
                   abs(rr["bf16"] / (TF_NEW["bf16"] / T100["bf16"]) - 1) < 0.01 and
                   abs(rr["int8"] / (TF_NEW["int8"] / T100["int8"]) - 1) < 0.01))
    checks.append(("G1's per-board scales recovered within 6% (leakage inflates y a little)",
                   all(abs(c[u] / C_TRUE[u] - 1) < 0.06 for u in C_TRUE)))
    checks.append(("the capped window was excluded (bf16.zs25 has one invalid replicate)",
                   len(redL["kinds"]["bf16.zs25"]["invalid"]) == 1))
    checks.append(("phase H's kinds are the blind set (17) and none was in the scale's fit",
                   len(pz["blind_kinds"]) == 17 and not set(pz["blind_kinds"]) & set(pz["phase_L_kinds"])))
    h = pz["heat"]["pooled"]
    checks.append(("heat fitted on phase L: tau2 within 35%, R_ss within 15%",
                   abs(h["tau2"] / 60.0 - 1) < 0.35 and abs(h["R_ss"] / 0.10 - 1) < 0.15))
    checks.append(("F1-F4 and F6 hold on data made by the frozen form",
                   all(sc["rules"][r]["verdict"] == "HOLDS" for r in ("F1", "F2", "F3", "F4", "F6"))))
    checks.append(("H2 holds (measured power through the fitted heat path)", sc["rules"]["H2"]["verdict"] == "HOLDS"))
    checks.append(("the corrected heat arm is no worse than the registered one here",
                   sc["heat"]["rms_corr_c"] <= sc["heat"]["rms_blind_c"] + 0.05))
    print("hold: scales", {u: round(v, 4) for u, v in c.items()}, "models",
          {m: round(v["rms_w"], 2) for m, v in sc["models"].items()}, "arms",
          {a: round(v["rms_w"], 2) for a, v in sc["arms"].items()}, {k: v["verdict"] for k, v in sc["rules"].items()},
          "heat", {k: round(sc["heat"][k], 3) for k in ("rms_blind_c", "rms_corr_c", "rms_measP_c")})
    # data the frozen form does not make: every blind kind off by +/-40 W (alternating), and the boards' scales apart
    bad = {k: (40.0 if i % 2 else -40.0) for i, k in enumerate(sorted(pz["blind_kinds"]))}
    C_TRUE["B"] = 1.80
    _, pz2, sc2 = chain(scr, "fail", bad)
    checks.append(("F1, F3 and F6 fail on data the frozen form does not make",
                   all(sc2["rules"][r]["verdict"] == "FAILS" for r in ("F1", "F3", "F6"))))
    print("fail: scales", {u: round(v, 4) for u, v in pz2["scales"]["G1"]["per_board"].items()},
          {k: v["verdict"] for k, v in sc2["rules"].items()})
    ok = True
    for name, cc in checks:
        print(("PASS " if cc else "FAIL ") + name)
        ok &= bool(cc)
    print("SELFTEST", "OK" if ok else "FAILED")


if __name__ == "__main__":
    main(sys.argv[1])
