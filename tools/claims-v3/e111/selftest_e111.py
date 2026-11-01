#!/usr/bin/env python3
"""E111 (Q133): the scorer's self-test, run before the freeze. Standard library only.

    python3 tools/claims-v3/e111/selftest_e111.py [<dry-run data dir>] > tools/claims-v3/e111/selftest.txt

1. E98's regression: score98() on E98's committed probes reproduces E98's committed results.json (R0..S4 and every arm).
2. Part A's pieces on planted holds: the 600 s slope of a flat and of a still-rising fine W; the asymptote of a planted exponential;
   the band verdicts at their edges.
3. Part B's B3 on planted probes: hold leads at 1.12, 2.25 and 0 times the rest-die lead; a probe under 0.5 C of lead; no warm probe.
4. Part C's verdicts on hand-made blocks: each C2 branch, C1, C3 and C4.
5. With a dry-run data dir (run_e111.sh dry, collected), the whole scorer end to end on toy-card data: it must run and score every
   rule it can (the camera's dry block is a 0.05 Hz block, so C2 there says nothing about the heat path).
"""
import copy
import json
import math
import os
import random
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import reduce_e111 as X  # noqa: E402

E = X.E
P = json.load(open(os.path.join(HERE, "predictions-e111.json")))
P98 = json.load(open(os.path.join(ROOT, "tools/claims-v3/kspeed/e98/predictions.json")))
D98 = os.path.join(ROOT, "docs/reports/data/2026-11-01-e98-heat-path-drift")
fails = []


def check(name, ok, detail=""):
    print(f"{'PASS' if ok else 'FAIL'}  {name}  {detail}")
    if not ok:
        fails.append(name)


# 1 ------------------------------------------------------------------------------------------------
H98 = E.History(D98)
q98 = E.R.jl(os.path.join(D98, "queue.jsonl"))
probes = []
for n in P["partB"]["e98_probes"]:
    pr = E.read_probe(os.path.join(D98, n), n, H98, P98, [q for q in q98 if q.get("probe") == n])
    pr["queue"] = [q for q in q98 if q.get("probe") == n]
    probes.append(pr)
s98 = X.score98(probes, P98)
bad = X.regression_check(s98, json.load(open(os.path.join(D98, "results.json"))))
check("1 score98 reproduces E98's committed R0-S4 and arms on E98's probes", not bad, f"differing: {bad}")
check("1 E98's verdicts as committed", (s98["R1"]["verdict"], s98["R2"]["verdict"], s98["V"]) == ("ABOVE_TARGET", "SUPPORTS", "PARTLY"),
      f"{s98['R1']['verdict']} {s98['R2']['verdict']} {s98['V']}")

# 2 ------------------------------------------------------------------------------------------------
rng = random.Random(111)
t0 = 1_800_000_000_000
def planted(rise_tau_s, w_inf=42.0, span_s=1620, amp=1.5):
    pts = []
    for i in range(int(span_s * 10)):
        t = t0 + i * 100
        x = i / 10.0
        pts.append((t, w_inf - amp * math.exp(-x / rise_tau_s) + rng.gauss(0, 0.06)))
    return pts
flat = planted(150.0)
rising = planted(4000.0)
t_end = flat[-1][0]
fs = X.bins_slope(flat, t_end, 600, 30)
rs = X.bins_slope(rising, t_end, 600, 30)
k = P["partA"]["k_fine_w_per_c"]
check("2 a settled fine W reads steady (|slope| <= 0.02 C/min)", abs(fs["slope_per_min"] / k) <= 0.02, f"{fs['slope_per_min'] / k:.4f} C/min")
check("2 a fine W still rising on a 4000 s stage reads not steady", abs(rs["slope_per_min"] / k) > 0.02, f"{rs['slope_per_min'] / k:.4f} C/min")
asy = X.asymptote(planted(400.0, w_inf=41.3, amp=3.0), t0, t_end)
check("2 the asymptote of a planted 400 s exponential", abs(asy["w_inf"] - 41.3) < 0.05 and 300 < asy["tau_s"] < 530, json.dumps(asy))
check("2 band verdicts", (X.band_verdict(0.70, 0.75, [0.62, 0.82]), X.band_verdict(0.60, 0.70, [0.62, 0.82]), X.band_verdict(0.83, 0.9, [0.62, 0.82]),
                         X.band_verdict(None, 0.7, [0.62, 0.82])) == ("PASS", "INCONCLUSIVE", "FAIL", "NOT_SCORED"))

# 3 ------------------------------------------------------------------------------------------------
def planted_b3(hold_per_c, line_per_c, dxs):
    base = {"P3": 94.59, "P6": 94.81, "P7": 94.50}
    bx = sum(base.values()) / 3
    px = dict(base)
    line = {"P3": 39.33, "P6": 39.40, "P7": 39.31}
    hold = {"P3": 58.05, "P6": 58.80, "P7": 58.49}
    bl, bh = sum(line.values()) / 3, sum(hold.values()) / 3
    for i, dx in enumerate(dxs):
        w = f"W{i + 1}"
        px[w] = bx + dx
        line[w] = bl + line_per_c * dx
        hold[w] = bh + hold_per_c * dx
    return {"_maps": {"px": px, "line": line, "hold_die": hold}}
r = X.b3(planted_b3(1.12, 0.25, [1.5, 1.8]), ["P3", "P6", "P7"], ["W1", "W2"], P)
check("3 room-sized leads: hold SUPPORTS, line SUPPORTS", (r["verdict_hold"], r["verdict_line"]) == ("SUPPORTS", "SUPPORTS"), json.dumps({k2: r.get(k2) for k2 in ("hold", "line")}))
r = X.b3(planted_b3(2.25, 0.52, [1.5, 1.8]), ["P3", "P6", "P7"], ["W1", "W2"], P)
check("3 P1-sized leads: hold reaches past the band, P1's own value inside", r["p1_hold_inside"] and r["verdict_hold"] in ("SUPPORTS", "ABOVE_BAND"), json.dumps(r.get("hold")) + " " + r["verdict_hold"])
r = X.b3(planted_b3(0.0, 0.0, [1.5, 1.8]), ["P3", "P6", "P7"], ["W1", "W2"], P)
check("3 no lead: hold BELOW_BAND, line BELOW_TARGET or INCONCLUSIVE", r["verdict_hold"] == "BELOW_BAND" and r["verdict_line"] in ("BELOW_TARGET", "INCONCLUSIVE"), f"{r['verdict_hold']} {r['verdict_line']}")
r = X.b3(planted_b3(1.12, 0.25, [0.3, -1.0]), ["P3", "P6", "P7"], ["W1", "W2"], P)
check("3 no warm probe (leads 0.3 and -1.0 C): UNDER-RESOLVED", (r["verdict_hold"], r["verdict_line"]) == ("UNDER-RESOLVED", "UNDER-RESOLVED"))

# 4 ------------------------------------------------------------------------------------------------
def block(lag, se, snr_roi=20.0, snr_b=40.0, lag5=74.0, se5=6.0, share=0.99, die=56.0, n=5):
    return {"blocks": {"E111-F05": {"laps_analysed": n, "laps_total": n + 1, "stretches": 120,
            "roi": {"n_laps": n, "amp": 900.0, "se_along": 900.0 / snr_roi, "snr": snr_roi, "phase_deg": lag + 3, "p_signflip": 0.0625},
            "power": {"amp": 4.4, "se_along": 4.4 / snr_b, "snr": snr_b}, "board_step_w": {"mean": 8.3},
            "transfer": {"1": {"H_mag": 220.0, "se_H_mag": 10.0, "H_phase_deg": lag, "se_H_phase_deg": se, "n_laps": n, "f_hz": 0.005},
                         "3": {"H_mag": 135.0, "se_H_mag": 10.0, "H_phase_deg": 62.0, "se_H_phase_deg": 4.0, "n_laps": n, "f_hz": 0.015},
                         "5": {"H_mag": 90.0, "se_H_mag": 9.0, "H_phase_deg": lag5, "se_H_phase_deg": se5, "n_laps": n, "f_hz": 0.025}},
            "hold": {"samples_800_share": share, "die_mean_c": die}}}}
tmp = os.path.join(os.environ.get("TMPDIR", "/tmp"), f"e111-selftest-{os.getpid()}")
os.makedirs(os.path.join(tmp, "CAM-ANA"), exist_ok=True)
def c_of(L):
    json.dump(L, open(os.path.join(tmp, "CAM-ANA", "lockin.json"), "w"))
    return X.part_c(tmp, P)
for lag, se, want in ((28.0, 2.5, "P1D"), (55.0, 3.0, "SLOW"), (40.0, 4.0, "INCONCLUSIVE"), (15.0, 2.0, "BELOW"), (37.5, 0.8, "BETWEEN")):
    c = c_of(block(lag, se))
    check(f"4 C2 at {lag} +- {se} deg reads {want}", c["C2"] == want, json.dumps(c.get("lag_0p005")))
c = c_of(block(28.0, 2.5, snr_roi=2.5))
check("4 C1 FAILs under 3 SE", c["C1"] == "FAIL")
c = c_of(block(28.0, 2.5, lag5=130.0, se5=5.0))
check("4 C3 OUTSIDE when the 0.025 Hz lag is far from E73's", c["C3"] == "OUTSIDE", json.dumps(c.get("lag_0p025")))
c = c_of(block(28.0, 2.5, share=0.90))
check("4 C4 FAILs under 95% at 790 MHz", c["C4"] == "FAIL")
c = c_of(block(28.0, 2.5))
check("4 C1, C3, C4 PASS/INSIDE on a clean block", (c["C1"], c["C3"], c["C4"]) == ("PASS", "INSIDE", "PASS"))
for f in ("lockin.json",):
    os.remove(os.path.join(tmp, "CAM-ANA", f))

# 5 ------------------------------------------------------------------------------------------------
if len(sys.argv) > 1:
    d = sys.argv[1]
    out = os.path.join(tmp, "dry-results.json")
    p = subprocess.run([sys.executable, os.path.join(HERE, "reduce_e111.py"), d, "--out", out], capture_output=True, text=True)
    check("5 the scorer runs end to end on the dry run", p.returncode == 0, f"rc {p.returncode} {p.stderr[-400:]}")
    if p.returncode == 0:
        res = json.load(open(out))
        print("   dry tally", json.dumps(res["tally"]))
        print("   dry verdicts", json.dumps(res["verdicts"]))
        a = res["A"]
        for h in ("H-I8", "H-F32"):
            print(f"   dry {h}: A1 {json.dumps(a.get(h, {}).get('A1'))}")
            print(f"            A2 {json.dumps(a.get(h, {}).get('A2'))}")
        print("   dry C", json.dumps({k2: v for k2, v in res["C"].items() if k2 not in ("models", "harmonics")})[:900])
        check("5 the dry run's probes read as probes", set(res["B"]["rest_die"]) >= {"P1", "P3", "P6", "P7"}, json.dumps(sorted(res["B"]["rest_die"])))
        check("5 the dry run's holds are scored", all(a.get(h, {}).get("A2", {}).get("c") is not None for h in ("H-I8", "H-F32")))
        check("5 the dry camera block was reduced and scored", res["C"].get("C1") in ("PASS", "FAIL"), str(res["C"].get("note")))

print("\nSELFTEST", "FAIL: " + ", ".join(fails) if fails else "PASS (all checks)")
sys.exit(1 if fails else 0)
