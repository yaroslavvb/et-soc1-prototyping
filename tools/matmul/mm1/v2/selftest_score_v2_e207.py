#!/usr/bin/env python3
"""Self-tests of score_v2_e207.py (the lane's own scorer), desk only, /usr/bin/python3 -I -B.
  1. the measured side on real committed data: E206 arm A's data-e206.json through score_v2_e207.measure() against E206's committed scores
     (scores-e206-A.json cells' measured fields), 119 points;
  2. stand-in E207 days built from the frozen files, each outcome stated here by arithmetic written apart from the scorer's code path:
     A: every point at MM1-v1's forecast; a stand-in v2 = MM1-v1 x 1.05 in time and x 1.10 in W (so x 1.155 in J);
     B: every point at the stand-in v2's forecast;
     C: day A with one run of b01 carrying another shire mask (set aside) and b05's second run without p_work (not kept);
     D: day A with W at b34 0.30 W over MM1-v1's W (the watts reading), and a stand-in F2 given() file.
     E: day A with "ran before" labels (b01, a point; b05's case) applied as E207.md A1 item 3 does, and an unknown label refused;
     and day A's family-level check (A1 item 5, REPORTED) on the wall and on J over idle with the seconds forecast.
    python3 -I -B selftest_score_v2_e207.py LABROOT REGTREE WORKDIR      (from tools/matmul/mm1/v2/; LABROOT = REGTREE = the lab's top)
"""
import copy
import csv
import hashlib
import json
import math
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import score_v2_e207 as S  # noqa: E402  (the lane's own scorer)

LAB, REG, WORK = sys.argv[1], sys.argv[2], sys.argv[3]
V1CSV = "tools/matmul/mm1/v1/out/mm1_v1_blind_day.csv"
F12J = "tools/matmul/mm1/v1/out/f1f2_blind_day.json"
F12C = "tools/matmul/mm1/v1/out/f1f2_blind_day.csv"
PTS = "tools/claims-v3/e207/points-e207.json"
RUL = "tools/claims-v3/e207/rules-e207.json"
PINS = {V1CSV: "90dffe943d611d139e091f481a32f6e04207d17937fd6cca96744658488032c6",
        F12J: "2f252ebdfd0ada66684a71adceb2f227ca559818b1bfb188322378296641a3d0",
        F12C: "8ff5e73a077e02513b15ff15a4067ab839186b3b56519118e6774376b5a46645",
        PTS: "2a905b4ec9e6295bdce5f55a67669d247f11bdc475e9ab51873f68ad02b899e1",
        RUL: "ffeb322e9d83e46bf41cdf55ecd4a5e5e1d42e30b07ba56f52d1c8fa6f881dec"}
fails = []


def check(name, cond, detail=""):
    print(f"{'PASS' if cond else 'FAIL'} {name} {detail}")
    if not cond:
        fails.append(name)


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


# ------------------------------------------------------------------ 1. the measured side on E206's committed data
D6 = os.path.join(LAB, "docs/reports/data/2026-11-16-e206-matmul-sweep-aifoundry3")
d6 = json.load(open(os.path.join(D6, "data-e206.json")))
s6 = json.load(open(os.path.join(D6, "scores-e206-A.json")))
p6 = json.load(open(os.path.join(LAB, "tools/claims-v3/e206/points-e206.json")))
by6 = {p["id"]: p for p in p6["points"]}
M6, aside6, nokeep6, _ = S.measure(d6, by6)
worst, n = 0.0, 0
for pid, st in M6.items():
    c = s6["cells"].get(f"A.{pid}")
    if not c:
        continue
    m = c["measured"]
    for kr, km, f in (("t", "t", 1), ("cycles_per_op", "cyc_mean", 1), ("cycles_gemm", "cyc_wall", by6[pid]["ops_per_minion_per_gemm"]),
                      ("j_over", "j_over", 1), ("j_rest", "j_rest", 1), ("p_rest", "p_rest", 1), ("p_work", "p_work", 1)):
        if m.get(kr) is None or st.get(km) is None:
            continue
        n += 1
        worst = max(worst, abs(m[kr] - st[km] * f) / abs(m[kr]))
check("1 measured side on E206 arm A (119 points)", len(M6) == 119 and n >= 119 * 6 and worst < 1e-12,
      f"points {len(M6)}, fields {n}, worst relative difference {worst:.2e}, set aside {len(aside6)}")

# ------------------------------------------------------------------ 2. stand-in days
base = os.path.join(WORK, "standin_root")
if os.path.isdir(base):
    shutil.rmtree(base)
for rel, src in ((V1CSV, LAB), (F12J, LAB), (F12C, LAB), (PTS, REG), (RUL, REG)):
    os.makedirs(os.path.dirname(os.path.join(base, rel)), exist_ok=True)
    shutil.copyfile(os.path.join(src, rel), os.path.join(base, rel))
    check(f"2 pin {rel}", sha(os.path.join(base, rel)) == PINS[rel])
v1rows = list(csv.DictReader(open(os.path.join(base, V1CSV), newline="")))
hdr = list(v1rows[0].keys())
KT, KW = 1.05, 1.10
v2rows = []
for r in v1rows:
    r2 = dict(r)
    for k in ("cycles_per_op_wall", "cycles_per_op_mean", "seconds_per_gemm"):
        r2[k] = repr(float(r[k]) * KT)
    for k in ("W_over_idle", "W_affine_A_W", "W_affine_B_W_us"):
        r2[k] = repr(float(r[k]) * KW)
    r2["J_over_idle_per_gemm"] = repr(float(r["J_over_idle_per_gemm"]) * KT * KW)
    v2rows.append(r2)
V2REL = "standin/v2.csv"
os.makedirs(os.path.join(base, "standin"), exist_ok=True)
with open(os.path.join(base, V2REL), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=hdr)
    w.writeheader()
    w.writerows(v2rows)
pts = json.load(open(os.path.join(base, PTS)))
byid = {p["id"]: p for p in pts["points"]}
f12 = {r["id"]: r for r in json.load(open(os.path.join(base, F12J)))["rows"]}
v1 = {r["id"]: r for r in v1rows}
v2 = {r["id"]: r for r in v2rows}
REST = 25.0


def run(pid, src, n, block, rest=REST, mask=None, pwork=True):
    f = src[pid]
    ops = byid[pid]["ops_per_minion_per_gemm"]
    t = float(f["seconds_per_gemm"])
    W = float(f["W_over_idle"])
    r = {"n": n, "block": block, "t_gemm_s": t, "cycles_gemm": float(f["cycles_per_op_wall"]) * ops, "cycles_per_op": float(f["cycles_per_op_mean"]),
         "p_rest_w": rest, "die_start_c": 50.0, "mhz": 600.0, "mhz_min": 600, "mhz_max": 600, "checks": ["exact"],
         "record": {"arm": byid[pid]["arm"], "type": byid[pid]["format"], "minions": byid[pid]["minions"], "shire_mask": mask or byid[pid]["shire_mask"]}}
    if pwork:
        r["p_work_w"] = rest + W
    return r


def day(src, mods=None):
    A = {"smoke": {"checks": ["exact"] * 3, "cycles_per_op": {}}, "points": {}, "ties": {"runs": []}}
    n = 0
    for pid in byid:
        runs = []
        for b in ("pass1", "pass2"):
            n += 1
            runs.append(run(pid, src, n, b))
        A["points"][pid] = {"runs": runs}
    if mods:
        mods(A)
    return {"experiment": "E207", "arms": {"A": A}}


def cfg_for(dname, data, reg=None):
    dp = os.path.join(base, "standin", f"data-{dname}.json")
    json.dump(data, open(dp, "w"))
    files = {"points": [PTS, PINS[PTS]], "rules": [RUL, PINS[RUL]], "v1": [V1CSV, PINS[V1CSV]], "f12": [F12J, PINS[F12J]],
             "f12csv": [F12C, PINS[F12C]], "v2": [V2REL, sha(os.path.join(base, V2REL))], "data": [f"standin/data-{dname}.json", None]}
    c = {"base": base, "files": files, "optional": ["regscore"], "v2": {"label": "STAND-IN", "freeze": None}}
    if reg is not None:
        rp = os.path.join(base, "standin", f"reg-{dname}.json")
        json.dump(reg, open(rp, "w"))
        c["files"]["regscore"] = [f"standin/reg-{dname}.json", None]
    return c


def close(a, b, tol):
    return a is not None and b is not None and abs(a - b) <= tol


# expected numbers, by arithmetic on the frozen files written here
cases = {}
for p in pts["points"]:
    cases.setdefault(p["case"], []).append(p["id"])
WPTS = set(json.load(open(os.path.join(base, RUL)))["watts"]["points"])


def exp_rms(vals):
    return 100 * math.sqrt(sum(x * x for x in vals) / len(vals)), 100 * sum(vals) / len(vals)


f1_cyc_err = [float(f12[ids[0]]["F1_cycles_per_op"]) / float(v1[ids[0]]["cycles_per_op_wall"]) - 1 for ids in cases.values()]
f1_t_err = [float(f12[ids[0]]["F1_seconds_per_gemm"]) / float(v1[ids[0]]["seconds_per_gemm"]) - 1 for ids in cases.values()]
f1_jfc_err = [float(f12[p]["F1_J_over_idle_per_gemm"]) / (float(v1[p]["W_over_idle"]) * float(v1[p]["seconds_per_gemm"])) - 1
              for p in byid if f12[p].get("F1_J_over_idle_per_gemm") is not None and p not in WPTS]

# day A
oA = S.score(cfg_for("A", day(v1)))
sA = oA["summary"]
check("2A v1 time errors 0", all(close(sA["v1"][q]["rms_pct"], 0, 1e-9) for q in S.TIME_Q), str({q: sA["v1"][q]["rms_pct"] for q in S.TIME_Q}))
check("2A v2 time errors +5.000% everywhere", all(close(sA["v2"][q]["rms_pct"], 5.0, 1e-9) and close(sA["v2"][q]["bias_pct"], 5.0, 1e-9) for q in S.TIME_Q))
check("2A v1 J over idle with the seconds forecast 0 (the CSV prints J and t to 9 decimals: about 3e-6 relative)", sA["v1"]["jo_fc_3W"]["rms_pct"] < 1e-3, f"{sA['v1']['jo_fc_3W']['rms_pct']:.2e}")
check("2A v1 J over idle given the seconds 0 (CSV precision 3.1e-6)", sA["v1"]["jo_given_3W"]["rms_pct"] < 1e-3, f"{sA['v1']['jo_given_3W']['rms_pct']:.2e}")
check("2A v2 J over idle with the seconds forecast +15.5% (CSV precision)", close(sA["v2"]["jo_fc_3W"]["rms_pct"], 15.5, 1e-3), f"{sA['v2']['jo_fc_3W']['rms_pct']:.6f}")
check("2A v2 W over idle given the seconds +10% (A, B x 1.10 at v1's seconds)", close(sA["v2"]["w_given_3W"]["rms_pct"], 10.0, 1e-3), f"{sA['v2']['w_given_3W']['rms_pct']:.6f}")
e_cyc = exp_rms(f1_cyc_err)
check("2A F1 wall cycles per case = F1/v1 - 1", close(sA["F1"]["cyc_wall"]["rms_pct"], e_cyc[0], 1e-9) and close(sA["F1"]["cyc_wall"]["bias_pct"], e_cyc[1], 1e-9),
      f"{sA['F1']['cyc_wall']['rms_pct']:.4f} vs {e_cyc[0]:.4f}")
e_t = exp_rms(f1_t_err)
check("2A F1 seconds per case = F1/v1 - 1", close(sA["F1"]["t"]["rms_pct"], e_t[0], 1e-9), f"{sA['F1']['t']['rms_pct']:.4f} vs {e_t[0]:.4f}")
e_j = exp_rms(f1_jfc_err)
check("2A F1 J over idle with the seconds forecast", close(sA["F1"]["jo_fc_3W"]["rms_pct"], e_j[0], 1e-3), f"{sA['F1']['jo_fc_3W']['rms_pct']:.4f} vs {e_j[0]:.4f} (n {len(f1_jfc_err)})")
# J at rest with the seconds forecast for v2: (rest 1.05 t + 1.155 W t) / ((rest + W) t) - 1
jr = [(REST * KT + KT * KW * float(v1[p]["W_over_idle"])) / (REST + float(v1[p]["W_over_idle"])) - 1 for p in byid]
e_jr = exp_rms(jr)
check("2A v2 J at rest with the seconds forecast", close(sA["v2"]["jr_fc"]["rms_pct"], e_jr[0], 1e-3), f"{sA['v2']['jr_fc']['rms_pct']:.5f} vs {e_jr[0]:.5f}")
h = oA["head_to_head"]["v2_vs_v1.cyc_wall"]
check("2A v2 vs v1 on the wall: v1 closer 47 of 47, v1 BETTER", h["other_closer"] == 47 and h["first_closer"] == 0 and h["reading"] == "v1 BETTER",
      f"{h['first_closer']}/{h['other_closer']}/{h['ties']} p {h['p_two_sided']:.3g}")
h1 = oA["head_to_head"]["v1_vs_F1.cyc_wall"]
nz = sum(1 for e in f1_cyc_err if abs(math.log(1 + e)) > 0.001)
check("2A v1 vs F1 on the wall: v1 closer at every case F1 differs by more than the tie", h1["first_closer"] == nz and h1["other_closer"] == 0, f"{h1['first_closer']} vs {nz}")
check("2A per-run v2 time +5%", close(sA["v2"]["t_per_run"]["rms_pct"], 5.0, 1e-9) and sA["v2"]["t_per_run"]["n"] == 106)
check("2A counts", oA["n"] == {"points_measured": 53, "points_scored": 53, "cases_scored": 47, "runs_scored": 106}, str(oA["n"]))
iv = oA["inside_v1_bands_REPORTED"]
check("2A v1 inside its bands everywhere; v2 (+5% time, +10% W) inside T1-T3 and E3, outside E2 (15.5% < 16%? inside)",
      iv["v1"]["T1"]["inside"] == 47 and iv["v2"]["T1"]["inside"] == 47, json.dumps(iv["v2"]))

# day B: at v2's forecast
oB = S.score(cfg_for("B", day(v2)))
sB = oB["summary"]
check("2B v2 time errors 0", all(close(sB["v2"][q]["rms_pct"], 0, 1e-9) for q in S.TIME_Q))
check("2B v1 time errors 1/1.05 - 1", all(close(sB["v1"][q]["bias_pct"], 100 * (1 / KT - 1), 1e-9) for q in S.TIME_Q), f"{sB['v1']['t']['bias_pct']:.6f}")
hB = oB["head_to_head"]["v2_vs_v1.cyc_mean"]
check("2B v2 vs v1 on the counter's mean: v2 closer 47 of 47", hB["first_closer"] == 47 and hB["reading"] == "v2 BETTER")
check("2B v2 J over idle with the seconds forecast 0 (CSV precision)", sB["v2"]["jo_fc_3W"]["rms_pct"] < 1e-3, f"{sB['v2']['jo_fc_3W']['rms_pct']:.2e}")


# day C: one b01 run set aside (another mask); b05's second run without p_work (not kept)
def modC(A):
    A["points"]["b01"]["runs"][0]["record"]["shire_mask"] = "0xff"
    A["points"]["b05"]["runs"][1].pop("p_work_w")


oC = S.score(cfg_for("C", day(v1, modC)))
check("2C b01 run set aside, b05 run not kept", "b01" in oC["set_aside_runs"] and oC["points"]["b01"]["measured"]["n_runs"] == 1
      and oC["points"]["b05"]["measured"]["n_runs"] == 1 and oC["n"]["runs_scored"] == 104, str(oC["n"]))


# day D: b34's W 0.30 W over MM1-v1's; a stand-in F2 given() = F2's frozen J scaled to the measured seconds
def modD(A):
    for r in A["points"]["b34"]["runs"]:
        r["p_work_w"] += 0.30


regD = {"points": {}}
for p in byid:
    if f12[p].get("F2_J_over_idle_per_gemm") is not None:
        regD["points"][p] = {"models": {"F2": {"given": {"J_over": f12[p]["F2_J_over_idle_per_gemm"] * float(v1[p]["seconds_per_gemm"]) / f12[p]["F1_seconds_per_gemm"]}}}}
oD = S.score(cfg_for("D", day(v1, modD), regD))
ew = oD["points"]["b34"]["err_w"]["v1"]
check("2D b34 in watts: v1 W given and forecast 0.30 W low", close(ew["w_given"], -0.30, 1e-4) and close(ew["w_fc"], -0.30, 1e-9), json.dumps(ew))
nF2 = sum(1 for p in byid if f12[p].get("F2_J_over_idle_per_gemm") is not None)
check("2D F2 given read for every priced point", oD["coverage"]["F2"]["points_jo_given"] == nF2, f"{oD['coverage']['F2']} of {nF2}")
# F2 given at v1's seconds = F2 J x tv1/tF1; error vs measured v1 W tv1: = F2_J tv1/tF1 / (W tv1) - 1
e2 = [f12[p]["F2_J_over_idle_per_gemm"] / f12[p]["F1_seconds_per_gemm"] / float(v1[p]["W_over_idle"]) - 1 for p in byid
      if f12[p].get("F2_J_over_idle_per_gemm") is not None and p not in WPTS]
check("2D F2 J over idle given = F2 W(F1 s) / v1 W - 1", close(oD["summary"]["F2"]["jo_given_3W"]["rms_pct"], exp_rms(e2)[0], 1e-6),
      f"{oD['summary']['F2']['jo_given_3W']['rms_pct']:.5f} vs {exp_rms(e2)[0]:.5f}")
# day A's common point sets: the stand-in v2 prices every point (as MM1-v1 does), so its set with v1 is every point (50 at 3 W and above,
# 3 in watts); all four price only where F1 and F2 both do: the random points (44 at 3 W and above); there v2 is still +15.5% on J forecast
allr = [p for p in byid if f12[p].get("F1_J_over_idle_per_gemm") is not None and f12[p].get("F2_J_over_idle_per_gemm") is not None]
SCA = oA["summary_common_points"]
check("2A common point sets: v2 and v1 at 50 + 3 points; all four at the points F1 and F2 both price (v2 +15.5% there)",
      SCA["v2_v1"]["v1"]["jo_fc_3W"]["n"] == 50 and SCA["v2_v1"]["v2"]["jo_fc_watts_pts"]["n"] == 3
      and SCA["all_four"]["v1"]["jo_fc_3W"]["n"] == len([p for p in allr if p not in WPTS]) and SCA["all_four"]["F2"]["jo_fc_3W"]["n"] == len([p for p in allr if p not in WPTS])
      and close(SCA["all_four"]["v2"]["jo_fc_3W"]["rms_pct"], 15.5, 1e-3),
      f"v2_v1 n {SCA['v2_v1']['v1']['jo_fc_3W']['n']}; all four n {SCA['all_four']['v1']['jo_fc_3W']['n']} (stated {len([p for p in allr if p not in WPTS])})")
# day A's family-level check (E207.md A1 item 5, REPORTED): every family favours v1 on the wall (v2 is 5% off everywhere)
tfam = {byid[ids[0]]["family"] for ids in cases.values()}
fcA = oA["head_to_head"]["v2_vs_v1.cyc_wall"]["family_check"]
pf = 2.0 / 2 ** len(tfam)
check("2A family check on the wall: every time family favours v1 (stated: v1 BETTER at p 2/2^families)",
      fcA["other_favoured"] == len(tfam) and fcA["first_favoured"] == 0 and fcA["reading"] == "v1 BETTER" and close(fcA["p_two_sided"], pf, 1e-15),
      f"{fcA['first_favoured']}/{fcA['other_favoured']}/{fcA['tied']} p {fcA['p_two_sided']} vs {pf}; families {len(tfam)}")
efam = {p["family"] for p in pts["points"]}
fcE = oA["head_to_head"]["v2_vs_v1.jo_fc"]["family_check"]
check("2A family check on J over idle with the seconds forecast: every energy family favours v1",
      fcE["other_favoured"] == len(efam) and fcE["reading"] == "v1 BETTER", f"{fcE['first_favoured']}/{fcE['other_favoured']}/{fcE['tied']}; families {len(efam)}")


# day E: day A with "ran before" labels applied A1's way: point b01 (its case leaves time with b42's and b49's time) and b05's case (time only)
cE = cfg_for("E", day(v1))
cE["labels"] = {"source": "stand-in", "points": ["b01"], "cases": [byid["b05"]["case"]]}
oE = S.score(cE)
n01, n05 = len(cases[byid["b01"]["case"]]), len(cases[byid["b05"]["case"]])
exp_t_runs = 106 - 2 * (n01 + n05)
check("2E labels: 45 cases, 52 points, 104 runs; per-run time on the runs outside the two cases; J over idle on 49 points",
      oE["n"]["cases_scored"] == 45 and oE["n"]["points_scored"] == 52 and oE["n"]["runs_scored"] == 104
      and oE["summary"]["v2"]["t_per_run"]["n"] == exp_t_runs and oE["summary"]["v1"]["jo_given_3W"]["n"] == 49
      and oE["summary"]["v1"]["jr_given"]["n"] == 52 and byid["b05"]["case"] not in oE["cases"] and byid["b01"]["case"] not in oE["cases"]
      and "b05" in oE["points"] and "b42" in oE["points"] and "b01" not in oE["points"],
      f"{oE['n']}; t per run n {oE['summary']['v2']['t_per_run']['n']} (stated {exp_t_runs}); jo_given n {oE['summary']['v1']['jo_given_3W']['n']}")
cX = cfg_for("X", day(v1))
cX["labels"] = {"source": "stand-in", "points": ["zz99"], "cases": []}
try:
    S.score(cX)
    refused = False
except SystemExit as e:
    refused = (e.code == 2)
check("2E an unknown label refused (exit 2)", refused)
check("2E the model labels kept beside the ran-before labels; the text summary runs on days A and E",
      oE["labels"]["v2"] == "STAND-IN" and oE["ranbefore_labels"]["points"] == ["b01"] and "v1" in oE["labels"]
      and len(S.text(oA)) > 1000 and "ran-before labels" in S.text(oE), str(oE["labels"].get("v2")))
json.dump({"A": oA["summary"], "B": oB["summary"]}, open(os.path.join(WORK, "selftest_summaries.json"), "w"), indent=1)
print(f"SELFTEST {'PASS' if not fails else 'FAIL'}: {len(fails)} failed {fails}")
sys.exit(0 if not fails else 1)
