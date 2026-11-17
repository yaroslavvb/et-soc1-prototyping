#!/usr/bin/env python3
"""A desk test of score_v2_e207.py's cross-check path (Q206 score-v2-e207), /usr/bin/python3 -I -B, in a scratch folder outside every round
folder: a stand-in E207 day whose every point sits off MM1-v1 by a stated, deterministic factor (time x f_t, W over idle x f_w, per point;
the rest 25 W), scored by E207's REGISTERED scorer (score_e207.py, run as its own process from the lab clone, unchanged; its output only feeds
this test) and by this lane's scorer reading that output. Stated outcomes: the measured side equal (worst relative difference < 1e-12); H1-H4's
counts equal and every d equal to < 1e-12 in ln (the watts rows < 1e-3 W: the registered reads W as j_over / t); MM1-v1's T1-T4 / E1-E4 pass
counts equal; F2's given() read at every point F2 prices.
    python3 -I -B selftest_xcheck_v2_e207.py LABROOT WORKDIR      (from tools/matmul/mm1/v2/, LABROOT the lab's top, WORKDIR a scratch folder)
"""
import csv
import hashlib
import json
import math
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import score_v2_e207 as S  # noqa: E402

LAB, WORK = sys.argv[1], sys.argv[2]
REL = {"points": "tools/claims-v3/e207/points-e207.json", "rules": "tools/claims-v3/e207/rules-e207.json",
       "v1": "tools/matmul/mm1/v1/out/mm1_v1_blind_day.csv", "f12": "tools/matmul/mm1/v1/out/f1f2_blind_day.json",
       "f12csv": "tools/matmul/mm1/v1/out/f1f2_blind_day.csv", "v2": "tools/matmul/mm1/v2/forecasts-e207.csv"}
PIN = {"points": "2a905b4ec9e6295bdce5f55a67669d247f11bdc475e9ab51873f68ad02b899e1", "rules": "ffeb322e9d83e46bf41cdf55ecd4a5e5e1d42e30b07ba56f52d1c8fa6f881dec",
       "v1": "90dffe943d611d139e091f481a32f6e04207d17937fd6cca96744658488032c6", "f12": "2f252ebdfd0ada66684a71adceb2f227ca559818b1bfb188322378296641a3d0",
       "f12csv": "8ff5e73a077e02513b15ff15a4067ab839186b3b56519118e6774376b5a46645", "v2": "873360bb7ef028c4922f6f55c6c61133a32da28fa6e19a6a02fa7f77d45d63d3"}
fails = []


def check(name, cond, detail=""):
    print(f"{'PASS' if cond else 'FAIL'} {name} {detail}")
    if not cond:
        fails.append(name)


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


base = os.path.join(WORK, "xcheck_root")
if os.path.isdir(base):
    shutil.rmtree(base)
for k, rel in REL.items():
    os.makedirs(os.path.dirname(os.path.join(base, rel)), exist_ok=True)
    shutil.copyfile(os.path.join(LAB, rel), os.path.join(base, rel))
    check(f"pin {rel}", sha(os.path.join(base, rel)) == PIN[k])
pts = json.load(open(os.path.join(base, REL["points"])))
byid = {p["id"]: p for p in pts["points"]}
v1 = {r["id"]: r for r in csv.DictReader(open(os.path.join(base, REL["v1"]), newline=""))}
REST = 25.0


def fac(pid, salt):
    """a deterministic factor in [0.88, 1.12] from the point id"""
    h = int(hashlib.sha256(f"{salt}|{pid}".encode()).hexdigest()[:8], 16)
    return 0.88 + 0.24 * (h / 0xFFFFFFFF)


A = {"smoke": {"checks": ["exact"] * 3, "cycles_per_op": {p: float(v1[p]["cycles_per_op_mean"]) for p in ("b01", "b02", "b03")}},
     "points": {}, "ties": {"runs": []}}
n = 0
for pid, p in byid.items():
    f = v1[pid]
    ops = p["ops_per_minion_per_gemm"]
    ft, fw = fac(pid, "t"), fac(pid, "w")
    runs = []
    for b, jit in (("pass1", 1.0), ("pass2", 1.0007)):
        n += 1
        t = float(f["seconds_per_gemm"]) * ft * jit
        W = float(f["W_over_idle"]) * fw / jit
        runs.append({"n": n, "block": b, "t_gemm_s": t, "cycles_gemm": float(f["cycles_per_op_wall"]) * ft * jit * ops,
                     "cycles_per_op": float(f["cycles_per_op_mean"]) * ft * jit, "p_rest_w": REST + 0.01 * (n % 3), "p_work_w": REST + 0.01 * (n % 3) + W,
                     "die_start_c": 50.0, "die_c": 52.0, "mhz": 600.0, "mhz_min": 600, "mhz_max": 600, "checks": ["exact"],
                     "record": {"arm": p["arm"], "type": p["format"], "minions": p["minions"], "shire_mask": p["shire_mask"]}})
    A["points"][pid] = {"runs": runs}
data = {"experiment": "E207", "arms": {"A": A}}
os.makedirs(os.path.join(base, "standin"), exist_ok=True)
dp = os.path.join(base, "standin", "data-xcheck.json")
json.dump(data, open(dp, "w"))
regp = os.path.join(base, "standin", "reg-xcheck.json")
rc = subprocess.run(["/usr/bin/python3", "-I", "-B", os.path.join(LAB, "tools/claims-v3/e207/score_e207.py"), dp, "--out", regp],
                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=600)
print("registered scorer rc", rc.returncode, "| last lines:", " / ".join(rc.stdout.strip().splitlines()[-3:])[:600])
check("the registered scorer ran on the stand-in day", rc.returncode == 0 and os.path.exists(regp))
cfg = {"base": base, "files": {k: [REL[k], PIN[k]] for k in REL}, "v2": {"label": "STAND-IN", "freeze": None}}
cfg["files"]["data"] = ["standin/data-xcheck.json", None]
cfg["files"]["regscore"] = ["standin/reg-xcheck.json", None]
o = S.score(cfg)
cr = o.get("crosscheck_registered") or {}
check("measured side equal to the registered scorer's", cr.get("measured_fields_compared", 0) >= 53 * 6 and cr.get("worst_relative_difference", 1) < 1e-12,
      f"{cr.get('measured_fields_compared')} fields, worst {cr.get('worst_relative_difference')}")
for hname, x in (cr.get("h1_h4") or {}).items():
    check(f"{hname} counts and d equal", x["counts_equal"] and x["d_on_one_side_only"] == 0 and x["worst_abs_d_difference_ln_rows"] < 1e-12
          and x["worst_abs_d_difference_watts_rows_W"] < 1e-3 and x["d_compared"] >= 45,
          f"registered {x['registered']} | this code {x['this_code']} | d {x['d_compared']}, ln {x['worst_abs_d_difference_ln_rows']:.2e}, W {x['worst_abs_d_difference_watts_rows_W']:.2e}")
check("H1-H4 all four compared", len(cr.get("h1_h4") or {}) == 4)
for rl, x in (cr.get("v1_rules") or {}).items():
    check(f"{rl} pass counts equal", x["equal"], f"registered {x['registered']} vs {x['this_code_inside_of']}")
nF2 = sum(1 for r in json.load(open(os.path.join(base, REL["f12"])))["rows"] if r.get("F2_J_over_idle_per_gemm") is not None)
check("F2 given() read at every point F2 prices", cr.get("F2_given_points") == nF2 and o["coverage"]["F2"]["points_jo_given"] == nF2,
      f"{cr.get('F2_given_points')} of {nF2}")
# the stated errors: MM1-v1's wall error per case is 1/(f_t x mean jitter) - 1 at a single-point case
c = "gemmL1x9x3|fp32|0xffffffff" if "gemmL1x9x3|fp32|0xffffffff" in o["cases"] else sorted(o["cases"])[0]
pid = o["cases"][c]["points"][0]
want = 1.0 / (fac(pid, "t") * (1 + 1.0007) / 2) - 1
check(f"MM1-v1's wall error at {c} = 1/(f_t x mean jitter) - 1", abs(o["cases"][c]["err"]["v1"]["cyc_wall"] - want) < 1e-12,
      f"{o['cases'][c]['err']['v1']['cyc_wall']:.12f} vs {want:.12f}")
print(f"SELFTEST-XCHECK {'PASS' if not fails else 'FAIL'}: {len(fails)} failed {fails}")
sys.exit(0 if not fails else 1)
