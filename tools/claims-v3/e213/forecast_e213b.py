#!/usr/bin/env python3
"""E213 (Q216): ARM B's FROZEN FORECASTS - MM1-v3 and MM1-v2, as landed, UNCHANGED, called on arm B's 41 points (and its tie) on aifoundry1 card
1 at 600 MHz. Written before any E213 datum; this registration's commit is their freeze line. numpy through the predictors (single-threaded).

    /usr/bin/python3 -I -B tools/claims-v3/e213/forecast_e213b.py            writes forecast-e213b-v3.csv, forecast-e213b-v3.json,
                                                                              forecast-e213b-v2.csv and forecast-e213b.txt
    /usr/bin/python3 -I -B tools/claims-v3/e213/forecast_e213b.py --check    re-makes all four in memory and compares bytes (exit 0 = PASS)

WHAT EACH PREDICTOR IS GIVEN (exactly; nothing else is passed, nothing is fitted, no file of either model is changed):
  MM1-v3  tools/matmul/mm1/v3/mm1_v3.py, Model(json.load(out/mm1_v3_params.json)), .predict(card, arm, fmt, kind, mask, f, kernel, t0_c=None):
          card 'aifoundry1 card 1' (its name in MM1-v3's vendored inputs and parameters: Pa, kc, the rest law); arm the point's token (gemmL... or
          gemmLnc...: the predictor reads the kernel's loop from it, engine_v3.loop_of, and prices its census path); fmt; kind (random, zeros,
          ones, sparse50: each has a committed switch count); mask '0xffffffff'; f 600.0 MHz; kernel 'rgm136'; V None, so mm1_core_v3.volts gives
          card 1's 0.517 V (CARD_V, the fit's footing, s_V = 1); G None, so mm1_core_v3.G_of_f gives 0 W (a pinned card); ops and minions None
          (64 MB NB KB a minion, 1,024 minions); t0_c None, so the energy is at a 50 C die (energy_v3.Features: no start die given -> 50 C, the
          die factor 1, as MM1-v3's own arm-A forecasts are made) and the J at rest (REPORTED) uses card 1's rest law at its T0 55 C.
  MM1-v2  tools/matmul/mm1/v2 as landed (3ca4b717), loaded by MM1-v3's own e213_v3.v2_model() (unread_v2_e212.v2_model: its four freeze-table
          files pinned by sha256 and its 114-line SHA256SUMS checked), .predict(card, arm2, fmt, kind, mask, f, V=None, t0_c=None): card
          'aifoundry1 card 1' (CKEY 'c1'); arm2 the token with gemmLnc read as gemmL - MM1-v2 has no term for rgm136's non-cooperative loads, so
          a gemmLnc point is priced as its rgm136 twin, literally (as MM1-v3's lane priced arm A's gemmLnc points, e213_v3.py); the point's own
          kind (random, zeros, ones; sparse50 has no MM1-v2 price: its energy is NOT FORECAST, its time is forecast); mask '0xffffffff'; f 600.0;
          V None, so mm1_core_v2.volts gives 0.517 V (CARD_V); G None (0 W); t0_c None.
The columns are MM1-v3's own E213 files' (e213_v3.py: mm1_v3_e213.csv's for MM1-v3, mm1_v2_e213.csv's for MM1-v2), so the scorer reads arm A's
and arm B's forecasts the same way. Every input's sha256 is printed in forecast-e213b.txt and recorded in forecast-e213b-v3.json > inputs_sha256.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import csv
import hashlib
import io
import json
import os
import platform
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
V3 = os.path.join(REPO, "tools", "matmul", "mm1", "v3")
V2 = os.path.join(REPO, "tools", "matmul", "mm1", "v2")
C1 = "aifoundry1 card 1"
INPUTS = ["tools/matmul/mm1/v3/mm1_v3.py", "tools/matmul/mm1/v3/engine_v3.py", "tools/matmul/mm1/v3/energy_v3.py",
          "tools/matmul/mm1/v3/mm1_core_v3.py", "tools/matmul/mm1/v3/kinds_v3.py", "tools/matmul/mm1/v3/inputs/census/census-v3.json",
          "tools/matmul/mm1/v3/out/mm1_v3_params.json", "tools/matmul/mm1/v3/e213_v3.py", "tools/matmul/mm1/v3/unread_v2_e212.py",
          "tools/matmul/mm1/v3/SHA256SUMS", "tools/matmul/mm1/v2/mm1_v2.py", "tools/matmul/mm1/v2/mm1_core_v2.py", "tools/matmul/mm1/v2/kinds_v2.py",
          "tools/matmul/mm1/v2/out/mm1_v2_params.json", "tools/matmul/mm1/v2/SHA256SUMS", "tools/claims-v3/e213/points-e213.json"]
OUTS = ("forecast-e213b-v3.csv", "forecast-e213b-v3.json", "forecast-e213b-v2.csv", "forecast-e213b.txt")


def sha_rel(rel):
    return hashlib.sha256(open(os.path.join(REPO, rel), "rb").read()).hexdigest()


def check_v3_folder():
    """MM1-v3's own SHA256SUMS, every line (the folder as landed)"""
    bad, n = [], 0
    for ln in open(os.path.join(V3, "SHA256SUMS")):
        h, rel = ln.split()
        n += 1
        if hashlib.sha256(open(os.path.join(V3, rel), "rb").read()).hexdigest() != h:
            bad.append(rel)
    if bad:
        print(f"forecast_e213b: REFUSED, MM1-v3's SHA256SUMS: {len(bad)} of {n} differ: {bad[:5]}")
        sys.exit(4)
    return n


def make():
    nsums = check_v3_folder()
    sys.path.insert(0, V3)
    import mm1_v3  # noqa: E402
    import e213_v3  # noqa: E402
    import numpy as np  # noqa: E402
    params_path = os.path.join(V3, "out", "mm1_v3_params.json")
    M3 = mm1_v3.Model(json.load(open(params_path)))
    M2 = e213_v3.v2_model()
    P = json.load(open(os.path.join(HERE, "points-e213.json")))["arms"]["B"]
    pts = list(P["points"]) + [P["tie"]]
    rows3, rows2, js = [], [], {}
    for p in pts:
        r3 = M3.predict(C1, p["arm"], p["format"], p["kind"], p["mm1_mask"], 600.0, kernel=p["kernel"], t0_c=None)
        if r3["loop"] != p["loop"]:
            raise SystemExit(f"forecast_e213b: {p['id']} loop {r3['loop']} != registered {p['loop']}")
        role = p["role"]
        row = {"id": p["id"], "family": p["family"], "card": C1, "f_mhz": 600.0, "kernel": p["kernel"], "arm": p["arm"], "fmt": p["format"],
               "kind": p["kind"], "mask": p["mm1_mask"], "t0_c": "", "never_run_on_card": (p.get("never_run_scan") or {}).get("never_run", ""),
               "note": f"{role}: {p['why']}", "footprint_MB": r3["footprint_MB"], "cycles_per_op_wall": round(r3["cycles_per_op_wall"], 3),
               "cycles_per_op_mean": round(r3["cycles_per_op_mean"], 3), "seconds_per_gemm": r3.get("seconds_per_gemm"),
               "T_op_us": round(r3["T_op_us"], 6), "census_D_B_cycles": r3["census_path_D_cycles"]["D_B"]}
        if "W_over_idle" in r3:
            row.update({"W_over_idle": round(r3["W_over_idle"], 4), "A_W": round(r3["W_affine"]["A_W"], 5), "B_W_us": round(r3["W_affine"]["B_W_us"], 5),
                        "J_over_idle_per_gemm": r3.get("J_over_idle_per_gemm"),
                        "J_at_rest_per_gemm_REPORTED": (r3.get("rest_law") or {}).get("J_at_rest_per_gemm_REPORTED"),
                        "P_rest_W_REPORTED": (r3.get("rest_law") or {}).get("P_rest_W")})
            sw = r3.get("switches") or {}
            row["switches_counted_signal_lo"] = (sw.get("counted_signal_fin_edges") or {}).get("lo_zero_delay")
            row["switches_data_term_equivalent"] = (sw.get("data_term_energy_equivalent") or {}).get("value")
        else:
            row["energy"] = r3.get("energy")
        rows3.append(row)
        js[p["id"]] = r3
        arm2 = p["arm"].replace("gemmLnc", "gemmL").replace("gemmLn", "gemmL")
        r2 = M2.predict(C1, arm2, p["format"], p["kind"], p["mm1_mask"], 600.0, V=None, t0_c=None)
        row2 = {"id": p["id"], "v2_arm_called": arm2, "cycles_per_op_wall": round(r2["cycles_per_op_wall"], 3),
                "cycles_per_op_mean": round(r2["cycles_per_op_mean"], 3), "seconds_per_gemm": r2.get("seconds_per_gemm"),
                "note": ("MM1-v2 has no term for this kernel's loop: its rgm136 twin, literally" if arm2 != p["arm"] else "")}
        if "W_over_idle" in r2:
            row2.update({"W_over_idle": round(r2["W_over_idle"], 4), "A_W": round(r2["W_affine"]["A_W"], 5), "B_W_us": round(r2["W_affine"]["B_W_us"], 5),
                         "J_over_idle_per_gemm": r2.get("J_over_idle_per_gemm"),
                         "J_at_rest_per_gemm_REPORTED": (r2.get("rest_law") or {}).get("J_at_rest_per_gemm_REPORTED")})
        else:
            row2["energy"] = r2.get("energy")
        rows2.append(row2)
    pcols = ["id", "family", "card", "f_mhz", "kernel", "arm", "fmt", "kind", "mask", "t0_c", "never_run_on_card", "note"]
    c3 = pcols + ["footprint_MB", "cycles_per_op_wall", "cycles_per_op_mean", "T_op_us", "seconds_per_gemm", "census_D_B_cycles", "W_over_idle", "A_W",
                  "B_W_us", "J_over_idle_per_gemm", "P_rest_W_REPORTED", "J_at_rest_per_gemm_REPORTED", "switches_counted_signal_lo",
                  "switches_data_term_equivalent", "energy"]
    c2 = ["id", "v2_arm_called", "cycles_per_op_wall", "cycles_per_op_mean", "seconds_per_gemm", "W_over_idle", "A_W", "B_W_us", "J_over_idle_per_gemm",
          "J_at_rest_per_gemm_REPORTED", "energy", "note"]
    out = {}
    for name, cols, rows in (("forecast-e213b-v3.csv", c3, rows3), ("forecast-e213b-v2.csv", c2, rows2)):
        s = io.StringIO()
        w = csv.DictWriter(s, fieldnames=cols, extrasaction="ignore", lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow(r)
        out[name] = s.getvalue()
    ins = {rel: sha_rel(rel) for rel in INPUTS}
    meta = {"what": "E213 arm B: MM1-v3's forecasts (every field of its predictor), aifoundry1 card 1 at 600 MHz; MM1-v2 beside in forecast-e213b-v2.csv",
            "calls": {"MM1-v3": "Model(params).predict('aifoundry1 card 1', arm, fmt, kind, '0xffffffff', 600.0, kernel='rgm136', t0_c=None)",
                      "MM1-v2": "e213_v3.v2_model().predict('aifoundry1 card 1', arm with gemmLnc read as gemmL, fmt, kind, '0xffffffff', 600.0, V=None, t0_c=None)"},
            "inputs_sha256": ins, "mm1_v3_sha256sums_checked": nsums, "interpreter": f"{sys.executable} {platform.python_version()}",
            "numpy": np.__version__, "points": js}
    out["forecast-e213b-v3.json"] = json.dumps(meta, indent=1, sort_keys=True, default=float) + "\n"
    lines = [f"E213 arm B forecasts (aifoundry1 card 1, 600 MHz): MM1-v3 and MM1-v2 as landed, unchanged; {sys.executable} {platform.python_version()}, "
             f"numpy {np.__version__}; MM1-v3's SHA256SUMS {nsums} of {nsums} checked; MM1-v2 through e213_v3.v2_model (pins and SHA256SUMS checked)"]
    for rel, h in ins.items():
        lines.append(f"input {h} {rel}")
    lines.append("id   family arm             fmt  kind     | v3 wall   mean     ms        W      mJ       | v2 wall   mean     W      mJ      | v3/v2 wall W")
    by2 = {r["id"]: r for r in rows2}
    for r in rows3:
        q = by2[r["id"]]
        W3, W2 = r.get("W_over_idle"), q.get("W_over_idle")
        J3, J2 = r.get("J_over_idle_per_gemm"), q.get("J_over_idle_per_gemm")
        gw = f"{W3 / W2:.3f}" if (W3 and W2) else "n.f."
        lines.append(f"{r['id']:4s} {r['family']:6s} {r['arm']:15s} {r['fmt']:4s} {r['kind']:8s} | {r['cycles_per_op_wall']:8.1f} {r['cycles_per_op_mean']:8.1f} "
                     f"{1e3 * r['seconds_per_gemm']:8.4f} {W3 if W3 is not None else float('nan'):6.2f} {1e3 * J3 if J3 else float('nan'):8.3f} | "
                     f"{q['cycles_per_op_wall']:8.1f} {q['cycles_per_op_mean']:8.1f} {W2 if W2 is not None else float('nan'):6.2f} "
                     f"{1e3 * J2 if J2 else float('nan'):8.3f} | {r['cycles_per_op_wall'] / q['cycles_per_op_wall']:.3f} {gw}")
    for name in ("forecast-e213b-v3.csv", "forecast-e213b-v2.csv", "forecast-e213b-v3.json"):
        lines.append(f"output {hashlib.sha256(out[name].encode()).hexdigest()} {name}")
    out["forecast-e213b.txt"] = "\n".join(lines) + "\n"
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    out = make()
    if a.check:
        res = {n: open(os.path.join(HERE, n)).read() == out[n] for n in OUTS}
        print(f"forecast_e213b --check: {res}")
        print("PASS" if all(res.values()) else "FAIL")
        sys.exit(0 if all(res.values()) else 1)
    for n in OUTS:
        open(os.path.join(HERE, n), "w").write(out[n])
    print(out["forecast-e213b.txt"])


if __name__ == "__main__":
    main()
