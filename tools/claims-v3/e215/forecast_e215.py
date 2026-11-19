#!/usr/bin/env python3
"""E215 (Q224): THE FORECASTS THIS REGISTRATION FREEZES - arm B's by the landed MM1-v3.1, MM1-v3 and MM1-v2 predictors, UNCHANGED; arm A's MM1-v2
column beside MM1-v3.1's land (whose MM1-v3.1 and MM1-v3 columns are frozen there and only re-checked here); and 'v3.1 with T7' for every point
of both arms (REPORTED, never scored by a registered rule). Written before any E215 datum; this registration's commit is their freeze line.
numpy through the predictors (single-threaded).

    /usr/bin/python3 -I -B tools/claims-v3/e215/forecast_e215.py            writes the files below
    /usr/bin/python3 -I -B tools/claims-v3/e215/forecast_e215.py --check    re-makes them in memory and compares bytes (exit 0 = PASS)

OUTPUTS: forecast-e215b-v31.csv and .json (MM1-v3.1, arm B: every field), forecast-e215b-v3.csv (MM1-v3), forecast-e215b-v2.csv (MM1-v2),
forecast-e215a-v2.csv (MM1-v2 at arm A's points), forecast-e215-refs.csv (the references and ties, every model; REPORTED only),
forecast-e215-t7.csv and .json ('v3.1 with T7', both arms), forecast-e215.txt (the printed table, every input and output by sha256).
WHAT EACH PREDICTOR IS GIVEN (exactly; nothing else is passed, nothing is fitted, no file of any model is changed):
  MM1-v3.1  tools/matmul/mm1/v3.1/mm1_v31.py, Model(json.load(out/mm1_v31_params.json)).predict(card, arm, fmt, kind, mask, 600.0, kernel):
            card 'aifoundry1 card 1' (arm B) or 'aifoundry3 card 0' (references); arm the point's token (gemmL, gemmLn or gemmLnc; the predictor
            reads the loop from it and from kernel, and prices the census path); fmt; kind (random, zeros, or a counted kind with item 7's phi);
            mask as MM1 spells it; f 600.0; kernel 'rgm136' or 'rgm211' (rgm211's own gemmL and gemmLn); V None, so mm1_core_v3.volts (card 1:
            0.517 V, s_V = 1); G None, so G_of_f (0 W, a pinned card); t0_c None, so the energy at a 50 C die and the J at rest REPORTED at the
            card's rest law's T0 (card 1: 55 C); minions and ops None (32 a shire of the mask; 64 MB NB KB an op a minion).
  MM1-v3    tools/matmul/mm1/v3/mm1_v3.py (landed b1493082), Model(out/mm1_v3_params.json).predict(card, arm, fmt, kind, mask, 600.0,
            kernel=kernel, t0_c=None), its 170-line SHA256SUMS checked first; the same inputs as MM1-v3.1's (a kind without its committed switch
            count: energy NOT FORECAST, time forecast).
  MM1-v2    tools/matmul/mm1/v2 as landed (3ca4b717), loaded by MM1-v3's e213_v3.v2_model() (its pins and 114-line SHA256SUMS checked),
            .predict(card, arm2, fmt, kind, mask, 600.0, V=None, t0_c=None): arm2 = the token with gemmLnc and gemmLn read as gemmL (MM1-v2 has no
            code-path term: a point of rgm211's loops or of gemmLnc is priced as its rgm136 gemmL twin, literally; rgm211's own gemmL is spelled
            gemmL already); kinds zeros, ones, random priced; any other kind's energy NOT FORECAST.
  v3.1 with T7  MM1-v3.1's predictor, unchanged, with its time constants and time form replaced by the same fit's declared T7 form
            (tools/matmul/mm1/v3.1/out/fits/time_T5r+G0+T7.json > theta_all and form: time_v31.Engine31 through t7_v31.py, as v3.1's fit
            evaluated it); every other input as MM1-v3.1's (its energy constants, rest laws and imbalance law). Its energy at its own op time and
            lines is REPORTED with it; the fit never chose it (item 4: T7 failed its LOEO condition). Never scored by a registered rule.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import copy
import csv
import hashlib
import io
import json
import os
import platform
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
V31 = os.path.join(REPO, "tools", "matmul", "mm1", "v3.1")
V3 = os.path.join(REPO, "tools", "matmul", "mm1", "v3")
A3 = "aifoundry3 card 0"
C1 = "aifoundry1 card 1"
T7FIT = "tools/matmul/mm1/v3.1/out/fits/time_T5r+G0+T7.json"
INPUTS = ["tools/matmul/mm1/v3.1/mm1_v31.py", "tools/matmul/mm1/v3.1/time_v31.py", "tools/matmul/mm1/v3.1/energy_v31.py",
          "tools/matmul/mm1/v3.1/t7_v31.py", "tools/matmul/mm1/v3.1/out/mm1_v31_params.json", T7FIT,
          "tools/matmul/mm1/v3.1/out/e215/mm1_v31_e215.csv", "tools/matmul/mm1/v3.1/out/e215/mm1_v31_e215.json",
          "tools/matmul/mm1/v3.1/out/e215/e215_choice.json", "tools/matmul/mm1/v3.1/SHA256SUMS",
          "tools/matmul/mm1/v3/mm1_v3.py", "tools/matmul/mm1/v3/engine_v3.py", "tools/matmul/mm1/v3/energy_v3.py",
          "tools/matmul/mm1/v3/mm1_core_v3.py", "tools/matmul/mm1/v3/out/mm1_v3_params.json", "tools/matmul/mm1/v3/e213_v3.py",
          "tools/matmul/mm1/v3/unread_v2_e212.py", "tools/matmul/mm1/v3/SHA256SUMS", "tools/matmul/mm1/v2/mm1_v2.py",
          "tools/matmul/mm1/v2/out/mm1_v2_params.json", "tools/matmul/mm1/v2/SHA256SUMS", "tools/claims-v3/e215/points-e215.json",
          "tools/claims-v3/e215/desk/choice-e215b.json"]
OUTS = ("forecast-e215b-v31.csv", "forecast-e215b-v31.json", "forecast-e215b-v3.csv", "forecast-e215b-v2.csv", "forecast-e215a-v2.csv",
        "forecast-e215-refs.csv", "forecast-e215-t7.csv", "forecast-e215-t7.json", "forecast-e215.txt")
COLS = ["id", "family", "reading", "role", "card", "f_mhz", "kernel", "loop", "arm", "fmt", "kind", "mask", "model", "arm_called", "footprint_MB",
        "cycles_per_op_wall", "cycles_per_op_mean", "T_op_us", "seconds_per_gemm", "W_over_idle", "A_W", "B_W_us", "J_over_idle_per_gemm",
        "P_rest_W_REPORTED", "J_at_rest_per_gemm_REPORTED", "switches_data_term_equivalent_REPORTED", "sim_steps_per_minion_per_gemm",
        "t7_mapped", "energy", "note"]


def sha_rel(rel):
    return hashlib.sha256(open(os.path.join(REPO, rel), "rb").read()).hexdigest()


def check_sums(folder, n_want=None):
    bad, n = [], 0
    for ln in open(os.path.join(folder, "SHA256SUMS")):
        h, rel = ln.split()
        n += 1
        if hashlib.sha256(open(os.path.join(folder, rel), "rb").read()).hexdigest() != h:
            bad.append(rel)
    if bad:
        print(f"forecast_e215: REFUSED, {folder}/SHA256SUMS: {len(bad)} of {n} differ: {bad[:5]}")
        sys.exit(4)
    return n


def r6(x, nd=6):
    return None if x is None else round(float(x), nd)


def row_of(p, r, model, arm_called=None, note=""):
    row = {"id": p["id"], "family": p["family"], "reading": p["reading"], "role": p["role"], "card": p["card"], "f_mhz": 600.0,
           "kernel": p["kernel"], "loop": p["loop"], "arm": p["arm"], "fmt": p["format"], "kind": p["kind"], "mask": p["mm1_mask"], "model": model,
           "arm_called": arm_called or p["arm"], "footprint_MB": r6(r.get("footprint_MB"), 4),
           "cycles_per_op_wall": r6(r["cycles_per_op_wall"], 4), "cycles_per_op_mean": r6(r["cycles_per_op_mean"], 4),
           "T_op_us": r6(r.get("T_op_us"), 8), "seconds_per_gemm": r.get("seconds_per_gemm"),
           "sim_steps_per_minion_per_gemm": r.get("sim_steps_per_minion_per_gemm"), "t7_mapped": r.get("t7_mapped", ""), "note": note}
    if "W_over_idle" in r:
        rl = r.get("rest_law") or {}
        sw = r.get("switches") or {}
        row.update({"W_over_idle": r6(r["W_over_idle"], 5), "A_W": r6(r["W_affine"]["A_W"], 6), "B_W_us": r6(r["W_affine"]["B_W_us"], 6),
                    "J_over_idle_per_gemm": r.get("J_over_idle_per_gemm"), "P_rest_W_REPORTED": r6(rl.get("P_rest_W"), 5),
                    "J_at_rest_per_gemm_REPORTED": rl.get("J_at_rest_per_gemm_REPORTED"),
                    "switches_data_term_equivalent_REPORTED": (sw.get("data_term_energy_equivalent") or {}).get("value")})
    else:
        row["energy"] = r.get("energy") or "NOT FORECAST"
    return row


def csv_of(rows):
    s = io.StringIO()
    w = csv.DictWriter(s, fieldnames=COLS, extrasaction="ignore", lineterminator="\n")
    w.writeheader()
    for r in rows:
        w.writerow(r)
    return s.getvalue()


def make():
    n31 = check_sums(V31)
    n3 = check_sums(V3)
    sys.path.insert(0, V31)
    import numpy as np  # noqa: E402
    import mm1_v31  # noqa: E402
    sys.path.insert(0, V3)
    import mm1_v3  # noqa: E402
    import e213_v3  # noqa: E402
    P31 = json.load(open(os.path.join(V31, "out", "mm1_v31_params.json")))
    M31 = mm1_v31.Model(P31)
    T7 = json.load(open(os.path.join(REPO, T7FIT)))
    P7 = copy.deepcopy(P31)
    P7["time"]["theta"] = dict(T7["theta_all"])
    P7["time"]["form"] = dict(T7["form"])
    M7 = mm1_v31.Model(P7)
    M3 = mm1_v3.Model(json.load(open(os.path.join(V3, "out", "mm1_v3_params.json"))))
    M2 = e213_v3.v2_model()
    nv2 = None
    if isinstance(M2, tuple):
        M2, nv2 = M2
    PT = json.load(open(os.path.join(HERE, "points-e215.json")))["arms"]
    landJ = json.load(open(os.path.join(V31, "out", "e215", "mm1_v31_e215.json")))["points"]
    land_by_tok = {q["token"]: q for q in landJ}
    out_rows = {k: [] for k in ("b31", "b3", "b2", "a2", "refs", "t7")}
    js_b31, js_t7, recheck = {}, {}, []

    def spec(p):
        return {"card": p["card"], "arm": p["arm"], "fmt": p["format"], "kind": p["kind"], "mask": p["mm1_mask"], "f": 600.0, "kernel": p["kernel"]}

    def v2_of(p):
        arm2 = p["arm"].replace("gemmLnc", "gemmL").replace("gemmLn", "gemmL")
        r2 = M2.predict(p["card"], arm2, p["format"], p["kind"], p["mm1_mask"], 600.0, V=None, t0_c=None)
        note = "MM1-v2 has no code-path term: its rgm136 gemmL twin, literally" if (arm2 != p["arm"] or p["kernel"] == "rgm211") else ""
        return r2, arm2, note

    for tag in ("A", "B"):
        A = PT[tag]
        pts = A["points"]
        refs = A["references"] + [A["tie"]]
        # MM1-v3.1, MM1-v3: arm B made here; arm A re-checked against the land (never re-frozen)
        f31 = M31.predict_many([spec(p) for p in pts])
        f7 = M7.predict_many([spec(p) for p in pts + refs])
        for j, p in enumerate(pts):
            r31 = f31[j]
            r3 = M3.predict(p["card"], p["arm"], p["format"], p["kind"], p["mm1_mask"], 600.0, kernel=p["kernel"], t0_c=None)
            if r31["loop"] != p["loop"] or r3["loop"] != p["loop"]:
                raise SystemExit(f"forecast_e215: {p['id']} loop {r31['loop']} / {r3['loop']} != registered {p['loop']}")
            r2, arm2, note2 = v2_of(p)
            if tag == "B":
                out_rows["b31"].append(row_of(p, r31, "MM1-v3.1"))
                js_b31[p["id"]] = r31
                out_rows["b3"].append(row_of(p, r3, "MM1-v3"))
                out_rows["b2"].append(row_of(p, r2, "MM1-v2", arm2, note2))
            else:
                out_rows["a2"].append(row_of(p, r2, "MM1-v2", arm2, note2))
                land = land_by_tok[p["source_token"]]
                d31 = max(abs(r31[k] / land["v31"][k] - 1) for k in ("cycles_per_op_wall", "cycles_per_op_mean", "seconds_per_gemm"))
                d3 = max(abs(r3[k] / land["v3"][k] - 1) for k in ("cycles_per_op_wall", "cycles_per_op_mean", "seconds_per_gemm"))
                dW31 = abs(r31["W_over_idle"] / land["v31"]["W_over_idle"] - 1) if "W_over_idle" in land["v31"] else None
                dW3 = abs(r3["W_over_idle"] / land["v3"]["W_over_idle"] - 1) if "W_over_idle" in land["v3"] else None
                recheck.append({"id": p["id"], "token": p["source_token"], "max_rel_time_v31": d31, "max_rel_time_v3": d3, "rel_W_v31": dW31,
                                "rel_W_v3": dW3})
        for j, p in enumerate(pts + refs):
            r7 = f7[j]
            out_rows["t7"].append(row_of(p, r7, "v3.1 with T7"))
            js_t7[f"{tag}:{p['id']}"] = r7
        fr = M31.predict_many([spec(p) for p in refs])
        for j, p in enumerate(refs):
            out_rows["refs"].append(row_of(p, fr[j], "MM1-v3.1", note="reference or tie: REPORTED, never scored"))
            r3 = M3.predict(p["card"], p["arm"], p["format"], p["kind"], p["mm1_mask"], 600.0, kernel=p["kernel"], t0_c=None)
            out_rows["refs"].append(row_of(p, r3, "MM1-v3", note="reference or tie: REPORTED, never scored"))
            r2, arm2, note2 = v2_of(p)
            out_rows["refs"].append(row_of(p, r2, "MM1-v2", arm2, "reference or tie: REPORTED, never scored"))
    worst = {k: max((x[k] for x in recheck if x[k] is not None), default=0.0) for k in ("max_rel_time_v31", "max_rel_time_v3", "rel_W_v31", "rel_W_v3")}
    out = {"forecast-e215b-v31.csv": csv_of(out_rows["b31"]), "forecast-e215b-v3.csv": csv_of(out_rows["b3"]),
           "forecast-e215b-v2.csv": csv_of(out_rows["b2"]), "forecast-e215a-v2.csv": csv_of(out_rows["a2"]),
           "forecast-e215-refs.csv": csv_of(out_rows["refs"]), "forecast-e215-t7.csv": csv_of(out_rows["t7"])}
    ins = {rel: sha_rel(rel) for rel in INPUTS}
    calls = {"MM1-v3.1": "mm1_v31.Model(out/mm1_v31_params.json).predict_many([{card, arm, fmt, kind, mask, f: 600.0, kernel}])",
             "MM1-v3": "mm1_v3.Model(out/mm1_v3_params.json).predict(card, arm, fmt, kind, mask, 600.0, kernel=kernel, t0_c=None)",
             "MM1-v2": "e213_v3.v2_model().predict(card, arm with gemmLnc and gemmLn read as gemmL, fmt, kind, mask, 600.0, V=None, t0_c=None)",
             "v3.1 with T7": ("mm1_v31.Model(params with time.theta = time_T5r+G0+T7.json > theta_all and time.form = its form).predict_many(...)")}
    meta = {"what": "E215 arm B: MM1-v3.1's forecasts (every field of its predictor), aifoundry1 card 1 at 600 MHz", "calls": calls,
            "inputs_sha256": ins, "mm1_v31_sha256sums_checked": n31, "mm1_v3_sha256sums_checked": n3, "mm1_v2_sha256sums_checked": nv2,
            "interpreter": f"{sys.executable} {platform.python_version()}", "numpy": np.__version__, "points": js_b31}
    out["forecast-e215b-v31.json"] = json.dumps(meta, indent=1, sort_keys=True, default=float) + "\n"
    meta7 = {"what": "E215, both arms: 'v3.1 with T7' (REPORTED, never scored by a registered rule)", "calls": calls,
             "t7_fit": {"path": T7FIT, "sha256": ins[T7FIT], "form": T7["form"], "form_name": T7.get("form_name")},
             "inputs_sha256": ins, "interpreter": f"{sys.executable} {platform.python_version()}", "numpy": np.__version__, "points": js_t7}
    out["forecast-e215-t7.json"] = json.dumps(meta7, indent=1, sort_keys=True, default=float) + "\n"
    L = [f"E215 forecasts frozen by this registration: arm B by MM1-v3.1, MM1-v3 and MM1-v2 as landed, unchanged; MM1-v2 beside arm A; 'v3.1 with T7' "
         f"for both arms (REPORTED); {sys.executable} {platform.python_version()}, numpy {np.__version__}; MM1-v3.1's SHA256SUMS {n31} of {n31} "
         f"checked, MM1-v3's {n3} of {n3}; MM1-v2 through e213_v3.v2_model (pins and SHA256SUMS checked)",
         f"arm A re-check (never re-frozen): MM1-v3.1's and MM1-v3's land columns re-made from the landed predictors: worst relative difference "
         f"time v3.1 {worst['max_rel_time_v31']:.1e}, v3 {worst['max_rel_time_v3']:.1e}; W v3.1 {worst['rel_W_v31']:.1e}, v3 {worst['rel_W_v3']:.1e}"]
    for rel, h in ins.items():
        L.append(f"input {h} {rel}")
    L.append("arm id   fam rd  arm token        fmt  kind              mask       | v3.1 wall  v3 wall  v2 wall  T7 wall | v3.1 W   v3 W    v2 W   T7 W")
    t7 = {(r["card"], r["id"]): r for r in out_rows["t7"]}

    def fv(x, w=8, nd=1):
        return f"{x:{w}.{nd}f}" if isinstance(x, (int, float)) else f"{'n.f.':>{w}s}"
    for tag in ("A", "B"):
        pts = PT[tag]["points"]
        rows31 = {r["id"]: r for r in out_rows["b31"]} if tag == "B" else None
        rows3 = {r["id"]: r for r in out_rows["b3"]} if tag == "B" else None
        rows2 = {r["id"]: r for r in (out_rows["b2"] if tag == "B" else out_rows["a2"])}
        for p in pts:
            if tag == "B":
                a, b = rows31[p["id"]], rows3[p["id"]]
                c31, c3, W31, W3 = a["cycles_per_op_wall"], b["cycles_per_op_wall"], a.get("W_over_idle"), b.get("W_over_idle")
            else:
                land = land_by_tok[p["source_token"]]
                c31, c3 = land["v31"]["cycles_per_op_wall"], land["v3"]["cycles_per_op_wall"]
                W31, W3 = land["v31"].get("W_over_idle"), land["v3"].get("W_over_idle")
            c = rows2[p["id"]]
            q = t7[(p["card"], p["id"])]
            L.append(f"{tag}   {p['id']} {p['family']:3s} {p['reading'][:3]} {p['arm']:16s} {p['format']:4s} {p['kind'][:17]:17s} {p['mm1_mask']:10s} | "
                     f"{fv(c31, 9)} {fv(c3)} {fv(c['cycles_per_op_wall'])} {fv(q['cycles_per_op_wall'])} | {fv(W31, 6, 2)} {fv(W3, 6, 2)} "
                     f"{fv(c.get('W_over_idle'), 6, 2)} {fv(q.get('W_over_idle'), 6, 2)}")
    for name in OUTS[:-1]:
        L.append(f"output {hashlib.sha256(out[name].encode()).hexdigest()} {name}")
    out["forecast-e215.txt"] = "\n".join(L) + "\n"
    return out, recheck, worst


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    out, recheck, worst = make()
    if a.check:
        res = {n: open(os.path.join(HERE, n)).read() == out[n] for n in OUTS}
        print(f"forecast_e215 --check: {res}")
        print("PASS" if all(res.values()) else "FAIL")
        sys.exit(0 if all(res.values()) else 1)
    for n in OUTS:
        open(os.path.join(HERE, n), "w").write(out[n])
    print(out["forecast-e215.txt"])
    print("arm A re-check worst:", worst)


if __name__ == "__main__":
    main()
