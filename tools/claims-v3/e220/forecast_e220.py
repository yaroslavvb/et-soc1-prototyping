#!/usr/bin/env python3
"""E220 (Q233): THE FORECASTS, frozen by E220's registration commit: every E220 point of both arms, the tie t01 and the two smoke rows, by the four
forecasters each from its frozen code unchanged (desk/models_e220.py: MM1-v3.2 REGISTERED; MM1-v3.1, MM1-v3, MM1-v2 beside), at arm A's 600.0 MHz on
aifoundry1 card 1 and at arm B's 799.0 (registered, route c), 700.0 and 600.0 MHz (route m, REPORTED) on aifoundry2 card 0. numpy through the
predictors; single-threaded (the caller sets the four thread variables to 1).

    /usr/bin/python3 -I -B tools/claims-v3/e220/forecast_e220.py            writes forecast-e220.json, forecast-e220.csv, forecast-e220.txt
    /usr/bin/python3 -I -B tools/claims-v3/e220/forecast_e220.py --check    re-makes them in memory and compares with the files (exit 0 = SAME)

Per point and model and clock: the op time (us, the slowest minion), cycles an op on the wall and the counter's mean, seconds a GEMM, W over idle at
its own seconds, the affine form W = A + B / t_op (t_op in us, the slowest minion: the scorer's given()), J over idle a GEMM, the J at rest REPORTED
at the card's rest law at its T0 forecast, the volts and governed base each model used, and MM1-v3.2's F3 term (W at its own op time, dup, first).
THE PER-CARD PARAMETERS each model carries for the two cards are written out (forecast-e220.json > per_card): how MM1-v3.2 prices each card.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import csv
import datetime
import hashlib
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(HERE, "desk"))
import models_e220 as MZ  # noqa: E402

POINTS = "points-e220.json"
EXTRA = (("t01", "tie (E218's t01, a bridge; run and read, never in a rule)", "gemmL2x4x4", "fp32"),
         ("s01", "smoke (the session gate; never a point)", "gemmL2x2x2", "fp32"),
         ("s03", "smoke (the G block's gate; never a point)", "gemmLnc2x2x2", "fp32"))
QTY = ("T_op_us", "cycles_per_op_wall", "cycles_per_op_mean", "seconds_per_gemm", "W_over_idle", "A_W", "B_W_us", "J_over_idle_per_gemm",
       "rest_law_W", "J_at_rest_per_gemm")


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def r9(x):
    return None if x is None else float("%.12g" % x)


def build():
    R = json.load(open(os.path.join(HERE, POINTS)))
    M = MZ.Models()
    out = {"what": ("E220's frozen forecasts: every point of both arms, the tie and the smoke rows, by MM1-v3.2 (REGISTERED), MM1-v3.1, MM1-v3 and "
                    "MM1-v2, each from its frozen code unchanged (desk/models_e220.py)"),
           "points_sha256": sha(os.path.join(HERE, POINTS)), "pins": M.pins, "interpreter": "/usr/bin/python3 " + sys.version.split()[0],
           "calls": {
               "MM1-v3.2": "mm1_v32.Model(out/mm1_v32_params.json).predict_many([{card, arm: token, fmt, kind: 'random', mask, f, kernel: 'rgm136'}])",
               "MM1-v3.1": "mm1_v31.Model(out/mm1_v31_params.json).predict_many([{card, arm: token, fmt, kind: 'random', mask, f, kernel: 'rgm136'}])",
               "MM1-v3": "mm1_v3.Model(out/mm1_v3_params.json).predict(card, token, fmt, 'random', mask, f, kernel='rgm136', t0_c=None)",
               "MM1-v2": "e213_v3.v2_model().predict(card, token with gemmLnc read as gemmL, fmt, 'random', mask, f, V=None, t0_c=None)",
               "given": ("card 'aifoundry1 card 1' (arm A) or 'aifoundry2 card 0' (arm B); f 600.0 (A) or 799.0 / 700.0 / 600.0 MHz (B); V, G, t0_c, "
                         "minions and ops not given (each model's own volts and governed base at f for the card; the energy at a 50 C die; 32 minions "
                         "a shire of the mask; 64 MB NB KB ops a minion)")},
           "registered_clock": {"A": 600.0, "B": 799.0}, "eps_G": M.eps_g, "rest_law_v32": M.rest, "arms": {}}
    # how each model prices the two cards: its per-card constants as frozen
    pc = {}
    for nm, P in (("MM1-v3.2", M.P32), ("MM1-v3.1", M.P31)):
        th = P["energy"]["theta"]
        pc[nm] = {}
        for arm, a in MZ.ARMS.items():
            c = a["card"]
            pc[nm][c] = {"Pa_W_awake_at_1024_minions": th.get(f"Pa|{c}"), "kc_energy_scale": th.get(f"kc|{c}"),
                         "volts": (P["energy"].get("volts", {}).get(c) or P["energy"].get("volts", {}).get("pinned", {}).get(c)),
                         "rest_law": P.get("rest_law", {}).get(c), "time": "shared constants across cards; the clock f an input"}
    pc["MM1-v3.2"]["governed_base_w_points"] = M.P32["energy"].get("governed_base_w")
    pc["MM1-v3.2"]["aifoundry3 card 0 (E218's card, for comparison)"] = {"Pa_W_awake_at_1024_minions": M.P32["energy"]["theta"].get("Pa|aifoundry3 card 0"),
                                                                         "kc_energy_scale": "1 (the reference card: no kc term)"}
    out["per_card"] = pc
    for arm in ("A", "B"):
        pts = [{"id": p["id"], "arm": p["token"], "fmt": p["format"], "kind": p["kind"], "mask": p["shire_mask"]} for p in R["points"][arm]]
        pts += [{"id": i, "arm": t, "fmt": f, "kind": "random", "mask": "0xffffffff"} for i, _, t, f in EXTRA]
        roles = {i: w for i, w, _, _ in EXTRA}
        cols = {}
        for f in MZ.ARMS[arm]["clocks"]:
            cols["%.1f" % f] = M.forecast(arm, pts, f)
        rows = {}
        for p in pts:
            rows[p["id"]] = {"token": p["arm"], "fmt": p["fmt"], "kind": p["kind"], "mask": p["mask"], "role": roles.get(p["id"], "point"),
                             "clocks": {fk: {m: {k: (r9(v) if isinstance(v, float) else v) for k, v in (cols[fk][p["id"]][m] or {}).items() if k != "Q_mean"}
                                             for m in MZ.MODELS} for fk in cols}}
            # the planning peaks at the registered clock (MM1-v3.2's, the drop rule's; the four models' largest, REPORTED)
            freg = "%.1f" % MZ.ARMS[arm]["f_reg"]
            pp32, ppall, by = M.planning_peak(arm, cols[freg][p["id"]], p["arm"])
            rows[p["id"]]["PP32_W"] = r9(pp32)
            rows[p["id"]]["PP_all_W"] = r9(ppall)
            rows[p["id"]]["PP_all_by"] = by
        out["arms"][arm] = {"card": MZ.ARMS[arm]["card"], "clocks_mhz": list(MZ.ARMS[arm]["clocks"]), "f_registered_mhz": MZ.ARMS[arm]["f_reg"],
                            "points": rows}
    return out


def table(F):
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(["arm", "card", "id", "role", "token", "format", "mask", "f_mhz", "model"] + list(QTY) + ["F3_W_at_own_t", "PP32_W"])
    for arm in ("A", "B"):
        a = F["arms"][arm]
        for pid, r in a["points"].items():
            for fk, ms in r["clocks"].items():
                for m in MZ.MODELS:
                    x = ms.get(m) or {}
                    w.writerow([arm, a["card"], pid, r["role"], r["token"], r["fmt"], r["mask"], fk, m] +
                               [("" if x.get(q) is None else "%.9g" % x[q]) for q in QTY] +
                               [("" if x.get("F3_W_at_own_t") is None else "%.9g" % x["F3_W_at_own_t"]), ("" if r["PP32_W"] is None else "%.6g" % r["PP32_W"])])
    return buf.getvalue()


def summary(F):
    L = ["E220's frozen forecasts (forecast-e220.json): MM1-v3.2 REGISTERED; MM1-v3.1, MM1-v3, MM1-v2 beside. Per arm at its registered clock:",
         "id | token fmt mask | wall cycles an op v3.2 / v3.1 / v3 / v2 | ms a GEMM v3.2 | W over idle v3.2 / v3.1 / v3 / v2 | F3 W | PP32"]
    for arm in ("A", "B"):
        a = F["arms"][arm]
        fk = "%.1f" % a["f_registered_mhz"]
        L.append(f"--- arm {arm}: {a['card']} at {fk} MHz")
        for pid, r in a["points"].items():
            ms = r["clocks"][fk]

            def g(m, q, fmtx="%.1f"):
                x = (ms.get(m) or {}).get(q)
                return "-" if x is None else fmtx % x
            L.append(f"{pid:6s} | {r['token']:16s} {r['fmt']:5s} {r['mask']:10s} | {g('MM1-v3.2', 'cycles_per_op_wall')} / {g('MM1-v3.1', 'cycles_per_op_wall')} / "
                     f"{g('MM1-v3', 'cycles_per_op_wall')} / {g('MM1-v2', 'cycles_per_op_wall')} | {g('MM1-v3.2', 'seconds_per_gemm', '%.6f')} s | "
                     f"{g('MM1-v3.2', 'W_over_idle', '%.2f')} / {g('MM1-v3.1', 'W_over_idle', '%.2f')} / {g('MM1-v3', 'W_over_idle', '%.2f')} / "
                     f"{g('MM1-v2', 'W_over_idle', '%.2f')} | {g('MM1-v3.2', 'F3_W_at_own_t', '%.2f')} | {('%.2f' % r['PP32_W']) if r['PP32_W'] else '-'}")
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    F = build()
    js = json.dumps(F, indent=1, sort_keys=True) + "\n"
    tb = table(F)
    tx = summary(F)
    files = {"forecast-e220.json": js, "forecast-e220.csv": tb, "forecast-e220.txt": tx}
    if a.check:
        bad = [k for k, v in files.items() if open(os.path.join(HERE, k)).read() != v]
        print("forecast_e220 --check:", "SAME" if not bad else f"DIFFER {bad}")
        sys.exit(0 if not bad else 1)
    for k, v in files.items():
        open(os.path.join(HERE, k), "w").write(v)
    print(datetime.datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z"), {k: sha(os.path.join(HERE, k)) for k in files})


if __name__ == "__main__":
    main()
