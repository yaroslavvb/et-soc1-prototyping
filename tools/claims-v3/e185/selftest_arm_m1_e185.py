#!/usr/bin/env python3
"""E185's dated note M1: the self-test of arm_m1_read_e185.py, on stand-in data directories in the form E185's step 22 commits them:
scored-m11.json's E185 section and sessions, written the way M11's scorer v5 writes them (score_m11_v5.e185: each hold's figures at 4
decimals, the cool-down misses, the frozen two-pass gains; its rules() run unchanged on the stand-in's holds), and the measured pass's
marks.jsonl room mark. Never a card, never a real run's data: every hold is built here from the committed json's own forecasts and E185's
registered planned forecasts (design-e185.json), with stated offsets.

    /usr/bin/python3 -B tools/claims-v3/e185/selftest_arm_m1_e185.py <scratch dir outside the repository>
                                                    # prints SELFTEST-ARM-M1-E185 <k> of <n> PASS; Python 3.9 with numpy (the scorer's)

THE CASES:
  K1  the constants: sigma_c is score_m11_v5's and design_e185's 0.0884 C; G_B is arms-e185-train.json's two-pass gain;
  C1  room 50.8 C (a plan room, the cool pattern in the room mark), every hold's rise and every big hold's cool-down at v3's forecast:
      every rise reads inside with z 0, every cool-down inside with |z| under 0.05 (the recovery's rounding), each recovered cool-down
      within 0.004 C of the truth, each plateau's recovery within 0.004 C; S and S2's cool-downs not covered; v4 reads as v3; the rms
      over six rises 0; the registered arms' planned rms equal this test's own;
  C2  room 50.55 C: the model's figures are this test's own linear interpolation between 50.3 and 50.8 C (1e-12), and inside;
  C3  room 52.0 C with the warm pattern in the room mark: extrapolated 0.500 C below 52.5 C from 52.5 and 53.0, equal to this test's own;
  C4  room 50.8 C, H_E's R 0.30 C above the forecast: the model reads below, R inside its band (z +1.89); L1's R 0.40 C below: the model
      reads above, R below its band; the rms over the six rises is this test's own;
  C5  S2 not scored and H_E2's cool-down window absent: both not read, said so; S's cool-down not covered;
  C6  no marks file at room 51.2 C: the pattern from A6-3's room rule (cool), said so;
  C7  E185's score reads NOT SCORED: nothing read, said so;
  C8  a hold whose plateau recovery misses by 0.05 C (e_B moved): its cool-down not read, the others read;
  R1  a copy of the committed json with one digit changed is refused (exit 2); R2 a score whose frozen G_B differs is refused (exit 3).
SPDX-License-Identifier: Apache-2.0
"""
import json
import os
import shutil
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(TOP, "tools", "claims-v3", "m11"))
import score_m11_v5 as V5  # noqa: E402  (unchanged: its rules(), r4, GAINS, SIGMA_C, KIND)
sys.path.insert(0, HERE)
import design_e185 as DE  # noqa: E402  (unchanged: SIGMA_C)

PY = "/usr/bin/python3"
M1P = os.path.join(HERE, "m1-october-forecast-model-e185.json")
M1 = json.load(open(M1P))
D = json.load(open(os.path.join(HERE, "design-e185.json")))
HOLDS = ("H_E", "L1", "L2", "H_E2", "S", "S2")
BIG = ("H_E", "L1", "L2", "H_E2")
G = V5.GAINS
results = []


def check(name, ok, what):
    results.append((name, bool(ok)))
    print(f"{name}: {'PASS' if ok else 'FAIL'} - {what}")


def lin(room, rs, vals):
    """this test's own room rule: linear between the bracketing plan rooms of the pattern, or from the two nearest at that end"""
    xs = [float(r) for r in rs]
    if room <= xs[0]:
        i, j = 0, 1
    elif room >= xs[-1]:
        i, j = len(xs) - 2, len(xs) - 1
    else:
        i = [k for k in range(len(xs) - 1) if xs[k] <= room <= xs[k + 1]][0]
        j = i + 1
    return vals[i] + (room - xs[i]) / (xs[j] - xs[i]) * (vals[j] - vals[i])


def rooms(pattern):
    return [r for r in ("49.4", "50.3", "50.8", "51.5") if pattern == "cool"] or ["52.5", "53.0", "53.9"]


def truth(room, pattern, arm="v3"):
    rs = rooms(pattern)
    t = {}
    for h in HOLDS:
        e = {r: M1["arms"][arm]["rooms"][r]["holds"][h] for r in rs}
        t[h] = {"rise": lin(room, rs, [e[r]["rise_C"] for r in rs]), "sd": lin(room, rs, [e[r]["rise_sd_C"] for r in rs])}
        if h in BIG:
            t[h]["cool"] = lin(room, rs, [e[r]["cooldown_C"] for r in rs])
            t[h]["csd"] = lin(room, rs, [e[r]["cooldown_sd_C"] for r in rs])
    return t


def planned(room, pattern, h, key):
    rs = rooms(pattern)
    return lin(room, rs, [[x for x in D["plans"][r]["holds"] if x["hold"] == h][0][key] for r in rs])


def standin(tmp, name, room, pattern, offsets=None, mark=True, he=None, unscored=(), no_cool=(), bad_eb=None, reads="SCORED", gb=None):
    """a data directory in step 22's form; the holds' R are the v3 forecast at the room plus the offsets"""
    d = os.path.join(tmp, name)
    shutil.rmtree(d, ignore_errors=True)
    pd = os.path.join(d, "aifoundry3", "e185", "p18520")
    os.makedirs(pd)
    t = truth(room, pattern)
    offsets = offsets or {}
    holds, raw = {}, {}
    for h in HOLDS:
        R = t[h]["rise"] + offsets.get(h, 0.0)
        PF, PRl = planned(room, pattern, h, "P_F_C") - 0.05, planned(room, pattern, h, "P_Rl_C") + 0.03   # a measured-watt chain, near the plan
        x = {"item": [y for y in D["plans"]["50.8"]["holds"] if y["hold"] == h][0]["item"], "scored": h not in unscored, "rail_ok": True,
             "rail_rows": {"anchor_rows": 1200, "plateau_rows": 3000, "ok": True}, "R_C": R, "P_F_C": PF, "P_B_C": G["G_B"] * PF,
             "P_Rl_C": PRl, "e_F_C": R - PF, "e_B_C": R - G["G_B"] * PF, "e_Rl_C": R - PRl, "rail_share": 0.88}
        x["kind"] = V5.KIND.get(x["item"])
        if h in BIG and h not in no_cool:
            Rc = t[h]["cool"] + offsets.get(h + ":cool", 0.0)
            cPF, cPRl = planned(room, pattern, h, "cool_P_F_C") - 0.02, planned(room, pattern, h, "cool_P_Rl_C") + 0.01
            x["cool"] = {"e_F_C": Rc - cPF, "e_B_C": Rc - G["G_B"] * cPF, "e_Rl_C": Rc - cPRl}
            x["_cool_truth"] = Rc
        else:
            x["cool"] = None
            x["cool_why"] = "the rest after it is 120 s (the window needs 360 s)" if h not in BIG else "no window (stand-in)"
        if bad_eb == h:
            x["e_B_C"] += 0.05 * (G["G_B"] - 1)    # moves the plateau recovery, e_F + (e_F - e_B) / (G_B - 1), by -0.05 C
        raw[h] = x
    # the scorer's rules on the unrounded holds, then the holds at 4 decimals, as score_m11_v5.e185 writes them
    rules = V5.rules({h: {k: v for k, v in x.items() if not k.startswith("_")} for h, x in raw.items()})
    for h, x in raw.items():
        holds[h] = {k: (V5.r4(v) if isinstance(v, float) else v) for k, v in x.items() if k not in ("cool",) and not k.startswith("_")} | \
            {"cool": None if not x["cool"] else {k: V5.r4(v) for k, v in x["cool"].items()}}
    E = {"label": "stand-in", "gains_frozen": dict(G) if gb is None else {"G_B": gb, "G_Rl": G["G_Rl"]}, "reads": reads}
    if reads == "SCORED":
        E |= {"reading": "the chain over the smoke and the measured pass (A10)", "session": "S3:p18520", "holds": holds, "rules": rules,
              "blind": True}
    sc = {"E185": E, "sessions": {"S3:p18520": {"pass_dir": "p18520", "start_gate": {"kind": "start_gate", "room_c": room, "passed": True}}}}
    json.dump(sc, open(os.path.join(d, "scored-m11.json"), "w"), indent=1, sort_keys=True, default=str)
    if mark:
        hs = he if he is not None else (3.2 if pattern == "cool" else 2.6)
        with open(os.path.join(pd, "marks.jsonl"), "w") as f:
            f.write(json.dumps({"kind": "room", "t_ms": 1, "window_s": 120.0, "he_seconds": hs,
                                "he_period_s": 7.56 if hs == 3.2 else 7.98}) + "\n")
    return d, t, raw


def read(d, m1=M1P):
    r = subprocess.run([PY, "-B", os.path.join(HERE, "arm_m1_read_e185.py"), "--data", d, "--out", os.path.join(d, "arm-m1-e185"), "--m1", m1],
                       capture_output=True, text=True, cwd=TOP)
    j = json.load(open(os.path.join(d, "arm-m1-e185.json"))) if r.returncode == 0 else None
    return r, j


def main():
    tmp = sys.argv[1] if len(sys.argv) > 1 else None
    if not tmp or os.path.abspath(tmp).startswith(TOP):
        print("usage: selftest_arm_m1_e185.py <scratch dir outside the repository>")
        sys.exit(2)
    os.makedirs(tmp, exist_ok=True)
    gtrain = json.load(open(os.path.join(HERE, "arms-e185-train.json")))["two_pass"]["gains"]["G_B"]
    check("K1", V5.SIGMA_C == DE.SIGMA_C == 0.0884 and G["G_B"] == gtrain,
          f"sigma_c {V5.SIGMA_C} (score_m11_v5) = {DE.SIGMA_C} (design_e185); G_B {G['G_B']} = arms-e185-train.json's {gtrain}")
    # C1
    d, t, raw = standin(tmp, "c1", 50.8, "cool")
    r, j = read(d)
    A = j["arms"]["v3"]["holds"]
    rz = [abs(A[h]["rise"]["z"]) for h in HOLDS]
    cz = [abs(A[h]["cooldown"]["z"]) for h in BIG]
    crec = [abs(j["measured"][h]["cool"]["R_C"] - raw[h]["_cool_truth"]) for h in BIG]
    prec = [abs(j["measured"][h]["plateau_recovery_C"]) for h in HOLDS]
    pl = j["arms"]["v3"]["summary"]["beside_registered_arms_planned_forecasts"]
    own_pl = {}
    for arm, k in (("F", "P_F_C"), ("B", "P_B_C"), ("Rl", "P_Rl_C")):
        e = [V5.r4(raw[h]["R_C"]) - planned(50.8, "cool", h, k) for h in HOLDS]
        own_pl[arm] = (sum(x * x for x in e) / len(e)) ** 0.5
    ok = (r.returncode == 0 and all(A[h]["rise"]["model_reads"] == "inside" and A[h]["rise"]["R_against_model_band"] == "inside" for h in HOLDS)
          and max(rz) < 0.002 and all(A[h]["cooldown"]["model_reads"] == "inside" for h in BIG) and max(cz) < 0.05 and max(crec) <= 0.004
          and max(prec) <= 0.004 and all("not covered" in A[h]["cooldown"] for h in ("S", "S2")) and j["v4_reads_as_v3"]
          and j["arms"]["v3"]["summary"]["rise_rms_C"] < 0.0002 and all(abs(pl[k]["rise_rms_C"] - own_pl[k]) < 1e-9 for k in own_pl)
          and A["H_E"]["room_rule"] == "at the plan room 50.8 C" and j["session"]["pattern"] == "cool")
    check("C1", ok, f"rc {r.returncode}; rises inside, max |z| {max(rz):.4f}; cool-downs inside, max |z| {max(cz):.4f}; recovered cool-downs "
          f"within {max(crec):.4f} C of the truth; plateau recovery within {max(prec):.4f} C; S/S2 cool-downs not covered; v4 as v3 "
          f"{j['v4_reads_as_v3']}; planned arms' rise rms F {pl['F']['rise_rms_C']:.4f}, B {pl['B']['rise_rms_C']:.4f}, Rl {pl['Rl']['rise_rms_C']:.4f} C")
    # C2
    d, t, raw = standin(tmp, "c2", 50.55, "cool")
    r, j = read(d)
    A = j["arms"]["v3"]["holds"]
    dmax = max(abs(A[h]["rise_model_C"] - t[h]["rise"]) for h in HOLDS)
    dmaxc = max(abs(A[h]["cooldown_model_C"] - t[h]["cool"]) for h in BIG)
    ok = (r.returncode == 0 and dmax < 1e-12 and dmaxc < 1e-12 and A["L1"]["room_rule"] == "interpolated between the plan rooms 50.3 and 50.8 C"
          and all(A[h]["rise"]["model_reads"] == "inside" for h in HOLDS))
    check("C2", ok, f"room 50.55: the model's rises and cool-downs equal this test's interpolation to {max(dmax, dmaxc):.1e}; "
          f"'{A['L1']['room_rule']}'; every rise inside")
    # C3
    d, t, raw = standin(tmp, "c3", 52.0, "warm")
    r, j = read(d)
    A = j["arms"]["v3"]["holds"]
    dmax = max(abs(A[h]["rise_model_C"] - t[h]["rise"]) for h in HOLDS)
    ok = (r.returncode == 0 and dmax < 1e-12 and j["session"]["pattern"] == "warm"
          and A["H_E"]["room_rule"] == "extrapolated 0.500 C below the plan room 52.5 C (from 52.5 and 53.0)")
    check("C3", ok, f"room 52.0, warm in the mark: '{A['H_E']['room_rule']}'; equal to this test's own to {dmax:.1e}; pattern from "
          f"'{j['session']['pattern_from']}'")
    # C4
    d, t, raw = standin(tmp, "c4", 50.8, "cool", offsets={"H_E": +0.30, "L1": -0.40})
    r, j = read(d)
    A = j["arms"]["v3"]["holds"]
    own = (sum(x * x for x in [V5.r4(raw[h]["R_C"]) - t[h]["rise"] for h in HOLDS]) / 6) ** 0.5
    ok = (r.returncode == 0 and A["H_E"]["rise"]["model_reads"] == "below" and A["H_E"]["rise"]["R_against_model_band"] == "inside"
          and abs(A["H_E"]["rise"]["z"] - 0.30 / t["H_E"]["sd"]) < 0.002 and A["L1"]["rise"]["model_reads"] == "above"
          and A["L1"]["rise"]["R_against_model_band"] == "below" and abs(j["arms"]["v3"]["summary"]["rise_rms_C"] - own) < 1e-12
          and all(A[h]["rise"]["model_reads"] == "inside" for h in ("L2", "H_E2", "S", "S2")))
    check("C4", ok, f"H_E +0.30: {A['H_E']['rise']['model_reads']}, R {A['H_E']['rise']['R_against_model_band']} the band, z "
          f"{A['H_E']['rise']['z']:+.2f}; L1 -0.40: {A['L1']['rise']['model_reads']}, R {A['L1']['rise']['R_against_model_band']} the band; "
          f"rms {j['arms']['v3']['summary']['rise_rms_C']:.4f} C = this test's {own:.4f}")
    # C5
    d, t, raw = standin(tmp, "c5", 50.8, "cool", unscored=("S2",), no_cool=("H_E2",))
    r, j = read(d)
    A = j["arms"]["v3"]["holds"]
    ok = (r.returncode == 0 and A["S2"]["rise"] == "not read: the score reads this hold not scored"
          and A["H_E2"]["cooldown"] == "not read: the score gives no cool-down window for this hold" and "not covered" in A["S"]["cooldown"]
          and j["arms"]["v3"]["summary"]["rises_read"] == ["H_E", "L1", "L2", "H_E2", "S"]
          and j["arms"]["v3"]["summary"]["cooldowns_read"] == ["H_E", "L1", "L2"])
    check("C5", ok, f"S2: '{A['S2']['rise']}'; H_E2 cool-down: '{A['H_E2']['cooldown']}'; rises read {j['arms']['v3']['summary']['rises_read']}")
    # C6
    d, t, raw = standin(tmp, "c6", 51.2, "cool", mark=False)
    r, j = read(d)
    ok = r.returncode == 0 and j["session"]["pattern"] == "cool" and j["session"]["pattern_from"].startswith("no H_E pattern in the measured pass's room mark")
    check("C6", ok, f"no marks file: pattern {j['session']['pattern']} from '{j['session']['pattern_from']}'")
    # C7
    d, t, raw = standin(tmp, "c7", 50.8, "cool", reads="NOT SCORED: the pass did not pass its start gate")
    r, j = read(d)
    ok = r.returncode == 0 and j.get("read", "").startswith("not read: E185's score reads") and not j["arms"]
    check("C7", ok, f"'{j.get('read')}'")
    # C8
    d, t, raw = standin(tmp, "c8", 50.8, "cool", bad_eb="L2")
    r, j = read(d)
    A = j["arms"]["v3"]["holds"]
    ok = (r.returncode == 0 and isinstance(A["L2"]["cooldown"], str) and A["L2"]["cooldown"].startswith("not read: the recovery misses the plateau")
          and isinstance(A["L1"]["cooldown"], dict) and A["L2"]["rise"]["model_reads"] == "inside")
    check("C8", ok, f"L2's plateau recovery {j['measured']['L2']['plateau_recovery_C']:+.4f} C: cool-down '{A['L2']['cooldown']}'; L1's read")
    # refusals
    d, t, raw = standin(tmp, "r", 50.8, "cool")
    bad = os.path.join(tmp, "m1-bad.json")
    s = open(M1P).read()
    i = s.index("14.648")
    open(bad, "w").write(s[:i] + "14.649" + s[i + 6:])
    r, j = read(d, m1=bad)
    check("R1", r.returncode == 2 and "REFUSED" in r.stdout, f"a json with one digit changed: rc {r.returncode}, {' '.join(r.stdout.split())[:170]}")
    d, t, raw = standin(tmp, "r2", 50.8, "cool", gb=G["G_B"] + 1e-6)
    r, j = read(d)
    check("R2", r.returncode == 3 and "REFUSED" in r.stdout, f"a score whose G_B moved 1e-6: rc {r.returncode}, {' '.join(r.stdout.split())[:170]}")
    d, t, raw = standin(tmp, "show", 50.8, "cool", offsets={"H_E": +0.30, "L1": -0.40})
    r, j = read(d)
    print("--- the reader's text in C4's world, for the record:")
    print(r.stdout.rstrip())
    k = sum(1 for _, o in results if o)
    print(f"SELFTEST-ARM-M1-E185 {k} of {len(results)} {'PASS' if k == len(results) else 'FAIL'}")
    sys.exit(0 if k == len(results) else 1)


if __name__ == "__main__":
    main()
