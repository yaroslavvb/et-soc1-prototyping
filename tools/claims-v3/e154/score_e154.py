#!/usr/bin/env python3
"""E154 (Q139): score E154's measured pass against Q139(e)'s frozen predictions, with the registered machinery. Desk only (the Intel).

The registered rules are Q139(e)'s (docs/reports/data/2026-11-03-q139e-heat-end-to-end/predictions-q139e.json > rules > E154, frozen in
455c46c1; amendment A1 in e224a3f8 changed no rule). Nothing is fitted or tuned; every frozen input is checked by sha256 first.

  ARM E, end to end from the bits (the primary, per pool-6 hold K_S, K_Q, K_L, K_O): Q138(t)'s frozen chain closed through E97's idle law
    from R0's measured rest die (34-sensor mean, last 120 s of R0), on the session's realized dispatch records, each on at the item's frozen
    S (S_table_W: M8's S_w for the pool-6 items) - score_e144.py's arm (b) machinery (A1.2), unchanged, with its S78 table extended by
    S_table_W's pool-6 entries (int8.full keeps E78's own S, as Q138(t)'s scorer reads it). Plateau = the mean rise over the hold's last
    300 s over the chain's carried-in base (score_e144.traj); the trajectory = checkpoints from 60 s to the end (5 s means; one cycle on
    K_S). PASS: |plateau error| <= band_95_C and the checkpoints' rms <= band_95_C. FAIL: |plateau error| > fail_beyond_C. Else
    INCONCLUSIVE. band_95_C and fail_beyond_C are the frozen session table's (aifoundry3.session.holds).
  ARM A, given watts (beside, per hold): score_e144.py's arm (a) unchanged (the chain on the measured board trace): PASS rms <= 0.80 and
    |plateau| <= 1.00 C; FAIL > 1.60 or > 2.00. E minus A on the plateau is the power path's share of the error.
  M7 and M6: their S (predictions-q139e.json > aifoundry3.power_arms), through the same chain (arm E's machinery, S78 extended by theirs).
  H_M (E97 H1's replicate, not end to end): Q138(t)'s (b) from E78's S (PASS +-1.30 C, FAIL outside 2.60) and (c) replicate (the rise per
    board W at 570-630 s over E97's H1 0.898: PASS [0.94, 1.06], FAIL outside [0.88, 1.12]), as score_e144.py reads them; band_95_C (0.361)
    reported as the tight reading.
  SESSION FIGURE: the rms of the pool-6 holds' arm E plateau errors (4 in the full design, 2 in the subset), with M7's, M6's and arm A's.
  E153 (reported, registered before the data): the same four tiles' S as E153 MEASURED them on this card (e153.json > items > S > mean,
    Q139(u)'s footing, committed 8e18eb67 at 17:25:43 PST) through the same chain on the same records: given measured watts for the same
    kinds, as E144's (b) read E78's. E - E153 on the plateau is M8's power error at work; E153 - A is the chain's error from steady watts.

Reported beside, never a verdict: the plan readings (the frozen session table's numbers, and amendment A1's arm-E-on-the-plan table for K_S
and K_Q), the rest die before each hold (the runner's rest_die marks and the scorer's anchor), the realized share and period, the carried-in
tail, each hold's peak die and board, and E - A.

    python3 tools/claims-v3/e154/score_e154.py <pass dir> [--json <out>]
    python3 tools/claims-v3/e154/score_e154.py --self-test [--json <out>]
numpy 1.26.4, Python 3.9 (the Intel's /usr/bin/python3).
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
QE = os.path.join(ROOT, "docs", "reports", "data", "2026-11-03-q139e-heat-end-to-end")
QT = os.path.join(ROOT, "docs", "reports", "data", "2026-11-02-q138t-heat-model")
FROZEN = {
    "docs/reports/data/2026-11-03-q139e-heat-end-to-end/predict_q139e.py": "0dad4370b5274f6bd85ab86c4065ac9bab8c414f68542d6552255b7891526314",
    "docs/reports/data/2026-11-03-q139e-heat-end-to-end/predictions-q139e.json": "60424edb5ade86bc50986b9a8eb3368a4fdf28c10780f662361a518e225ed703",
    "docs/reports/data/2026-11-03-q139e-heat-end-to-end/amendment-a1.json": "1e2b7abf99e126a229a6102aa68af211c792a114578f786f281281b7b1ebeb8a",
    "docs/reports/data/2026-11-02-q138t-heat-model/score_e144.py": "0569c49474da4058de4ad14c13d1081fa50ba2e7dd705d4a564835d94c2e1494",
    "docs/reports/data/2026-11-02-q138t-heat-model/heat_q138t.py": "9dbb288f896b7e588fbc155d67f32b1cb7089ffe4ede465c1380d2724d1fb49b",
    "docs/reports/data/2026-11-02-q138t-heat-model/fit_q138t.py": "0f21f77cb916bb65c85708b89a89a36e7add3146e098da38dd64b4077e9eb29a",
    "docs/reports/data/2026-11-02-q138t-heat-model/model-q138t.json": "268b47fd580b330738eb3e1c83ea392f3784aae348a658e7335b734a1168e8fa",
    "docs/reports/data/2026-11-02-q138t-heat-model/predictions-e144.json": "ae840f84bd36e80f822981913b3d44f314248669f56ff96dc2c2b61ced0a92d0",
    "docs/reports/data/2026-11-02-q138t-heat-model/amendment-a1.json": "a147f40c5225e6d213f6f907dae652961f2b7ae784fe56747dbf6d22b5726240",
    "docs/reports/data/2026-10-31-e78-kinds-energy-matrix/e78.json": "b7463b6c2c159eb70bd59418f729c4c9144f6eec778126ef660fe781cc724da5",
    "docs/reports/data/2026-11-02-q137m-model/m6.json": "87c17e086ee36699d7bb96609c02c471b5ba6b7bcdc20ead576d26f89e136e82",
    "tools/claims-v3/kinds/blind6/predictions-blind6-aifoundry3.json": "972476423c2bd70b00066037060ec8cc45b000ce90017b1ef8c6b58cf961e21f",
    "docs/reports/data/2026-11-03-e153-blind6-aifoundry3/e153.json": "afff8cb2eca522ebdc9e22138850aef9d92bf482d8ebb4a0aae2faa4ef14be38",
}
POOL6 = {"K_S": "fp32.real_smol_softmax_v_causal", "K_Q": "int8.real_qwen_w8a8_v", "K_L": "int8.b_line_zero_ff",
         "K_O": "fp32.a_onebit_b5_third"}
HOLD_ITEMS = {"H_M": "int8.full", **POOL6}


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def check_frozen():
    bad = []
    for rel, want in FROZEN.items():
        p = os.path.join(ROOT, rel)
        have = sha(p) if os.path.exists(p) else "missing"
        if have != want:
            bad.append(f"{rel}: {have} != {want}")
    return bad


_bad = check_frozen()
if _bad:
    raise SystemExit("E154 scorer: a frozen input differs:\n  " + "\n  ".join(_bad))
sys.path.insert(0, QT)
import score_e144 as se  # noqa: E402  frozen, unchanged
hm = se.hm
PRED = json.load(open(os.path.join(QE, "predictions-q139e.json")))
A1 = json.load(open(os.path.join(QE, "amendment-a1.json")))
A3 = PRED["aifoundry3"]
FZ = {h["hold"]: h for h in A3["session"]["holds"]}
S_TABLE = dict(A3["S_table_W"])
ARMS = A3["power_arms"]
S78_E78 = dict(se.S78)                      # score_e144's own table, as frozen (E78's S)
# the reported arm "E153": the same four tiles' S MEASURED on this card by E153 (4.5 s runs, Q139(u)'s footing; e153.json, 8e18eb67, committed
# 17:25:43 PST, before this registration) - the chain on the realized records given measured watts for the same kinds, as E144's (b) from E78
E153_S = {it: float(v["S"]["mean"]) for it, v in json.load(open(os.path.join(ROOT, "docs", "reports", "data", "2026-11-03-e153-blind6-aifoundry3",
                                                                        "e153.json")))["items"].items() if it in POOL6.values()}
MODELS = ("M8", "M7", "M6", "E153")


def s_table(model):
    """the S each record is on: E78's (score_e144's) for every E78 item, plus the model's S for the four pool-6 items. M8's is S_table_W
    (Q139(e)'s 'S78 table extended by S_table_W'); int8.full keeps E78's own value in every arm."""
    t = dict(S78_E78)
    for it in POOL6.values():
        t[it] = float(S_TABLE[it]) if model == "M8" else (E153_S[it] if model == "E153" else float(ARMS[it][f"{model}_S_W"]))
    return t


def score_with(sess, model):
    se.S78.clear()
    se.S78.update(s_table(model))
    try:
        return se.score_a3(sess)
    finally:
        se.S78.clear()
        se.S78.update(S78_E78)


def rms(xs):
    xs = [x for x in xs if x is not None and np.isfinite(x)]
    return float(math.sqrt(sum(x * x for x in xs) / len(xs))) if xs else None


def verdict_e(pe, trms, band, fail):
    if pe is None or not np.isfinite(pe):
        return "NOT SCORED"
    if abs(pe) > fail:
        return "FAIL"
    if abs(pe) <= band and trms is not None and trms <= band:
        return "PASS"
    return "INCONCLUSIVE"


def r3(x, n=3):
    return None if x is None or (isinstance(x, float) and not np.isfinite(x)) else round(float(x), n)


def session_extras(sess, marks):
    """the rest die marks, the room mark and each hold's peaks, from the pass's own files"""
    g, T, P = sess["g"], sess["T"], sess["P"]
    rd = {m["hold"]: m for m in marks if m.get("kind") == "rest_die"}
    room = [m for m in marks if m.get("kind") == "room"]
    hold_marks = {m["name"]: m for m in marks if m.get("kind") == "hold"}
    out = {}
    for h in sess["holds"]:
        k = (g >= h["t0"]) & (g < h["t1"])
        out[h["name"]] = {"rest_die_mark": rd.get(h["name"]), "hold_mark": hold_marks.get(h["name"]),
                          "peak_mean34_C": r3(float(np.nanmax(T[k])) if k.any() else None, 2),
                          "peak_board_W": r3(float(np.nanmax(P[k])) if k.any() else None, 2)}
    return out, (room[0] if room else None)


def score(pass_dir):
    sess = se.a3_load([pass_dir])
    marks = [json.loads(x) for x in open(os.path.join(pass_dir, "marks.jsonl")) if x.strip()]
    res = {m: score_with(sess, m) for m in MODELS}
    extras, room = session_extras(sess, marks)
    by = {m: {r["hold"]: r for r in res[m]["holds"]} for m in res}
    out = {"experiment": "E154", "pass_dir": os.path.basename(os.path.normpath(pass_dir)),
           "frozen": {"predictions": "455c46c1", "amendment_a1": "e224a3f8", "sha256_checked": len(FROZEN)},
           "session": {**res["M8"]["session"], "room_mark": room,
                       "int8.full_S_W": {"E78_as_scored": S78_E78["int8.full"], "S_table_W": S_TABLE["int8.full"]}},
           "holds": {}, "verdicts": {}}
    pe_e, pe_a, pe_m7, pe_m6, pe_53 = [], [], [], [], []
    for name, rE in by["M8"].items():
        item = rE.get("item")
        fz = FZ.get(name, {})
        row = {"item": item, "t0": rE["t0"], "dur_s": r3(rE["dur_s"], 1), "share_recorded": r3(rE["share_recorded"], 4),
               "launch_period_s": r3(rE["launch_period_s"], 3), "from_rest": rE["from_rest"], "rest_die_C": r3(rE["rest_die_C"]),
               **extras.get(name, {})}
        b = rE["b"]
        cp = {k: v for k, v in b["checkpoint_err_C"].items()}
        trms = rms(list(cp.values()))
        a = rE["a"]
        row["A_given_watts"] = {"rms_C": r3(a["rms_C"]), "plateau_err_C": r3(a["plateau_err_C"]), "max_abs_C": r3(a["max_abs_C"]),
                                "cooldown_rms_C": r3(a.get("cooldown_rms_C")), "verdict": a["verdict"]}
        row["measured"] = {"base_C": r3(b["measured"]["base_C"]), "plateau_rise_C": r3(b["measured"]["plateau_rise_C"]),
                           "rise_C_by_s": {k: r3(v) for k, v in b["measured"]["rise_C_by_s"].items()}}
        row["E_predicted_M8"] = {"base_C": r3(b["predicted"]["base_C"]), "plateau_rise_C": r3(b["predicted"]["plateau_rise_C"]),
                                 "carried_in_C": r3(b["predicted"]["base_C"] - out["session"]["rest_die_R0_C"]),
                                 "rise_C_by_s": {k: r3(v) for k, v in b["predicted"]["rise_C_by_s"].items()}}
        row["M6_frozen_step_response_on_measured_trace"] = rE.get("a_M6")
        if name in POOL6:
            band, fail = float(fz["band_95_C"]), float(fz["fail_beyond_C"])
            v = verdict_e(b["plateau_err_C"], trms, band, fail)
            row["E_end_to_end"] = {"plateau_err_C": r3(b["plateau_err_C"]), "checkpoint_err_C": cp, "checkpoint_rms_C": r3(trms),
                                   "band_95_C": band, "fail_beyond_C": fail, "critic_scale_C": fz.get("critic_scale_C"),
                                   "verdict": v}
            row["E_minus_A_plateau_C"] = r3(b["plateau_err_C"] - a["plateau_err_C"])
            pe_e.append(b["plateau_err_C"])
            pe_a.append(a["plateau_err_C"])
            for m, acc in (("M7", pe_m7), ("M6", pe_m6), ("E153", pe_53)):
                bm = by[m][name]["b"]
                tm = rms(list(bm["checkpoint_err_C"].values()))
                row[f"{m}_through_the_chain"] = {"S_W": E153_S[item] if m == "E153" else ARMS[item][f"{m}_S_W"],
                                                "predicted_plateau_rise_C": r3(bm["predicted"]["plateau_rise_C"]),
                                                "plateau_err_C": r3(bm["plateau_err_C"]), "checkpoint_rms_C": r3(tm),
                                                "verdict_by_the_same_rule": verdict_e(bm["plateau_err_C"], tm, band, fail)}
                acc.append(bm["plateau_err_C"])
            row["S_W"] = {"M8": S_TABLE[item], "M7": ARMS[item]["M7_S_W"], "M6": ARMS[item]["M6_S_W"], "E153_measured": E153_S[item]}
            row["E_minus_E153_plateau_C"] = r3(b["plateau_err_C"] - by["E153"][name]["b"]["plateau_err_C"])
            row["E153_minus_A_plateau_C"] = r3(by["E153"][name]["b"]["plateau_err_C"] - a["plateau_err_C"])
            row["plan_reading_frozen_table"] = {"frozen_plateau_rise_C": fz.get("plateau_rise_C"),
                                                "frozen_carried_in_C": fz.get("carried_in_C"),
                                                "measured_minus_frozen_C": r3(b["measured"]["plateau_rise_C"] - fz["plateau_rise_C"])
                                                if fz.get("plateau_rise_C") is not None else None}
            c1 = A1.get("C1_E154_plan_on_the_registered_machinery", {}).get("frozen_vs_armE_at_51.2C", {}).get(name)
            if c1:
                row["plan_reading_A1_armE_51.2C"] = {"plateau_rise_C": c1["armE_plateau_rise_C"], "carried_in_C": c1["armE_carried_in_C"],
                                                     "measured_minus_A1_C": r3(b["measured"]["plateau_rise_C"] - c1["armE_plateau_rise_C"])}
            out["verdicts"][f"{name} E"] = v
            out["verdicts"][f"{name} A"] = a["verdict"]
        else:
            row["H_M_b_E78_S"] = {"plateau_err_C": r3(b["plateau_err_C"]), "checkpoint_err_C": cp, "checkpoint_rms_C": r3(trms),
                                  "verdict": b["verdict"], "tight_band_95_C": fz.get("band_95_C"),
                                  "within_tight_band": None if b["plateau_err_C"] is None else bool(abs(b["plateau_err_C"]) <= fz.get("band_95_C", 0)
                                                                                                       and (trms or 9) <= fz.get("band_95_C", 0))}
            row["H_M_c_replicate"] = rE.get("c_replicate")
            row["H_M_c_per_board_W"] = rE.get("c_per_board_W")
            row["H_M_c_t63"] = rE.get("c_t63")
            out["verdicts"][f"{name} b"] = b["verdict"]
            if rE.get("c_replicate"):
                out["verdicts"][f"{name} c_replicate"] = rE["c_replicate"]["verdict"]
            out["verdicts"][f"{name} A"] = a["verdict"]
        row["c_per_board_W_last300s"] = rE.get("c_per_board_W")
        out["holds"][name] = row
    out["session_figure"] = {"n_pool6_holds": len(pe_e), "rms_plateau_err_C": {"E_M8": r3(rms(pe_e)), "M7": r3(rms(pe_m7)),
                                                                                 "M6": r3(rms(pe_m6)), "E153_measured_S": r3(rms(pe_53)),
                                                                                 "A_given_watts": r3(rms(pe_a))},
                             "mean_plateau_err_C": {"E_M8": r3(float(np.mean(pe_e))) if pe_e else None,
                                                    "A_given_watts": r3(float(np.mean(pe_a))) if pe_a else None}}
    return out


# ------------------------------------------------------------------------------------------------ self-test
def synth(T_rest=51.2, period=4.37, offsets=None, scale=1.0):
    """a synthetic E154 pass made by the frozen model at the plan's pattern (natural chain 5.6 s on / 0.2 s off, K_S 3.456 s once every
    `period` s), as amendment A1's plan_records lays it out; offsets {hold: C} add a constant to the die over each hold's last 300 s;
    scale multiplies the die's rise over T_rest"""
    se.S78.clear()
    se.S78.update(s_table("M8"))
    try:
        on = A3["K_S_duty"]["plan (room <= 51.5 C)"]["recorded_s"]
        holds = [("H_M", "int8.full", 5.6, 0.2, 11.0), ("K_S", POOL6["K_S"], on, period - on, 10.0),
                 ("K_Q", POOL6["K_Q"], 5.6, 0.2, 10.0), ("K_L", POOL6["K_L"], 5.6, 0.2, 10.0), ("K_O", POOL6["K_O"], 5.6, 0.2, 10.0)]
        s = se.synth_a3(holds, [5.0, 3.5, 3.5, 3.5, 3.5, 2.5], T_rest=T_rest)
    finally:
        se.S78.clear()
        se.S78.update(S78_E78)
    s["T"] = T_rest + scale * (s["T"] - T_rest)
    for h in s["holds"]:
        if offsets and h["name"] in offsets:
            k = (s["g"] >= h["t1"] - 300) & (s["g"] < h["t1"])
            s["T"][k] += offsets[h["name"]]
    return s


def score_session(s):
    """score() on an in-memory session (no marks file)"""
    res = {"M8": score_with(s, "M8")}
    out = {}
    for r in res["M8"]["holds"]:
        nm = r["hold"]
        if nm not in POOL6:
            out[nm] = {"b": r["b"]["verdict"], "plateau_err_C": r3(r["b"]["plateau_err_C"]),
                       "c_replicate": (r.get("c_replicate") or {}).get("verdict"), "A": r["a"]["verdict"],
                       "predicted_plateau_rise_C": r3(r["b"]["predicted"]["plateau_rise_C"])}
            continue
        fz = FZ[nm]
        trms = rms(list(r["b"]["checkpoint_err_C"].values()))
        out[nm] = {"E": verdict_e(r["b"]["plateau_err_C"], trms, fz["band_95_C"], fz["fail_beyond_C"]), "A": r["a"]["verdict"],
                   "plateau_err_C": r3(r["b"]["plateau_err_C"]), "checkpoint_rms_C": r3(trms),
                   "predicted_plateau_rise_C": r3(r["b"]["predicted"]["plateau_rise_C"]),
                   "carried_in_C": r3(r["b"]["predicted"]["base_C"] - T_rest_of(s)),
                   "share": r3(r["share_recorded"], 4)}
    return out


def T_rest_of(s):
    r0 = s["rests"][0]
    return se.wmean(s["g"], s["T"], r0["t1"] - hm.ANCHOR_S, r0["t1"])


def expected(pe, trms, nm):
    fz = FZ[nm]
    return verdict_e(pe, trms, fz["band_95_C"], fz["fail_beyond_C"])


def self_test():
    out = {"note": "synthetic E154 passes made by the frozen model itself at the plan's pattern (amendment A1's plan_records): arm E must "
                   "give back amendment A1's arm-E-on-the-plan numbers at a 51.2 C room and read PASS with every arm; die offsets over "
                   "the last 300 s must move the verdicts as the rule says; the verdict function is checked on its edges"}
    probs = []
    base = score_session(synth())
    out["exact_plan"] = base
    a1 = A1["C1_E154_plan_on_the_registered_machinery"]["frozen_vs_armE_at_51.2C"]
    for nm in POOL6:
        d = abs(base[nm]["predicted_plateau_rise_C"] - a1[nm]["armE_plateau_rise_C"])
        dc = abs(base[nm]["carried_in_C"] - a1[nm]["armE_carried_in_C"])
        if d > 0.02 or dc > 0.02:
            probs.append(f"{nm}: arm E on the synthetic plan {base[nm]['predicted_plateau_rise_C']} (tail {base[nm]['carried_in_C']}) "
                         f"vs A1 {a1[nm]['armE_plateau_rise_C']} (tail {a1[nm]['armE_carried_in_C']})")
        if base[nm]["E"] != "PASS" or base[nm]["A"] != "PASS":
            probs.append(f"{nm}: exact plan reads E {base[nm]['E']}, A {base[nm]['A']}")
    if base["H_M"]["b"] != "PASS" or base["H_M"]["A"] != "PASS":
        probs.append(f"H_M: exact plan reads b {base['H_M']['b']}, A {base['H_M']['A']}")
    cases = {}
    for off in (0.3, 1.0, 1.6, 3.0):
        r = score_session(synth(offsets={nm: off for nm in POOL6}))
        got = {nm: r[nm]["E"] for nm in POOL6}
        want = {nm: expected(r[nm]["plateau_err_C"], r[nm]["checkpoint_rms_C"], nm) for nm in POOL6}
        cases[f"+{off} C over the last 300 s"] = {"verdicts": got, "plateau_err_C": {nm: r[nm]["plateau_err_C"] for nm in POOL6},
                                                 "checkpoint_rms_C": {nm: r[nm]["checkpoint_rms_C"] for nm in POOL6}}
        if got != want:
            probs.append(f"offset {off}: {got} != the rule's {want}")
        for nm in POOL6:
            if abs(r[nm]["plateau_err_C"] - off) > 0.02:
                probs.append(f"offset {off}: {nm} plateau error {r[nm]['plateau_err_C']}")
    want_fixed = {"+0.3 C over the last 300 s": {nm: "PASS" for nm in POOL6},
                  "+3.0 C over the last 300 s": {nm: "FAIL" for nm in POOL6}}
    for k, w in want_fixed.items():
        if cases[k]["verdicts"] != w:
            probs.append(f"{k}: {cases[k]['verdicts']} != {w}")
    out["offsets"] = cases
    warm = score_session(synth(T_rest=52.0, period=4.97))
    out["warm_room_52C_period_4.97s"] = warm
    if any(warm[nm]["E"] != "PASS" for nm in POOL6):
        probs.append("warm room: not every hold PASS")
    edges = [((0.59, 0.59, "K_S"), "PASS"), ((0.61, 0.10, "K_S"), "INCONCLUSIVE"), ((0.10, 0.61, "K_S"), "INCONCLUSIVE"),
             ((-1.31, 0.2, "K_S"), "FAIL"), ((1.88, 0.2, "K_Q"), "INCONCLUSIVE"), ((-1.89, 0.2, "K_Q"), "FAIL"),
             ((2.89, 0.2, "K_L"), "INCONCLUSIVE"), ((2.90, 0.2, "K_L"), "FAIL"), ((1.37, 0.2, "K_O"), "INCONCLUSIVE"),
             ((1.38, 0.2, "K_O"), "FAIL")]
    ed = []
    for (pe, tr, nm), want in edges:
        got = expected(pe, tr, nm)
        ed.append({"hold": nm, "plateau_err_C": pe, "checkpoint_rms_C": tr, "verdict": got, "want": want})
        if got != want:
            probs.append(f"edge {nm} {pe}/{tr}: {got} != {want}")
    out["edges"] = ed
    out["self_test_ok"] = not probs
    out["problems"] = probs
    return out


def _json(x):
    return json.dumps(x, indent=1, default=lambda o: float(o) if isinstance(o, np.floating) else (bool(o) if isinstance(o, np.bool_) else str(o)))


def main():
    args = sys.argv[1:]
    jout = None
    if "--json" in args:
        i = args.index("--json")
        jout = args[i + 1]
        args = args[:i] + args[i + 2:]
    if args and args[0] == "--self-test":
        res = self_test()
    else:
        res = score(args[0])
    txt = _json(res)
    if jout:
        open(jout, "w").write(txt + "\n")
    print(txt)
    if args and args[0] == "--self-test" and not res["self_test_ok"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
