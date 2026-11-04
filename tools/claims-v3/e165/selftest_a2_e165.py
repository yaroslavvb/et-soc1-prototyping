#!/usr/bin/env python3
"""E165 (Q141(g)), amendment A2: the self-test of A2's two checks, on committed data only. No card, no device, no ssh; it writes only a temporary
directory (the code-path check's own self-test).

    python3 -B tools/claims-v3/e165/selftest_a2_e165.py > tools/claims-v3/e165/selftest-a2.txt      (about 3 minutes: E160's 150 bursts once)

  1. A2-4's burst D on E160's committed session. score_e165's own collect and cells_of on E160's s1 (with its committed ccheck-s1.json), then
     report_d_e165.d_795: the registered form equals results.json's D (D_w and D_runs) on every pool tile; the second form, D_795, equals E160's
     corrections C1 (corrections.json C1_fp16_tiles: D_w_corrected, D_runs_corrected) on all 12 fp16 tiles that are not the anchor, and equals the
     registered D on every fp32 and int8 tile (their anchors ran every pass at 800 MHz); the fp16 anchor's pass below 795 MHz is pass 1 and its
     reference is C1's 34.645 W.
  2. A2-4 on a made-up E165 session (three passes of every tile that runs, each at its frozen M9.a2_q140l clock and board): with the fp16 anchor's
     pass 1 at 752 MHz and 2.185 W short (E160's case), every fp16 tile's registered D reads 2.185 / 3 W high and its D_795 reads its made-up D; every
     fp32 and int8 tile's D_795 equals its registered D; score_e165.score() on the two forms differs in the D rows only.
  3. A2-5's code-path check: check_path_e165.py passes on this tree, and its --self-test refuses a changed byte (run as subprocesses).
SPDX-License-Identifier: Apache-2.0
"""
import copy
import gzip
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import e165_common as C  # noqa: E402
import report_d_e165 as RD  # noqa: E402
import score_e165 as S  # noqa: E402

ROOT = C.ROOT
D160 = os.path.join(ROOT, "docs/reports/data/2026-11-03-e160-blind6-aifoundry2")
P160 = json.load(open(os.path.join(ROOT, "tools/claims-v3/e160/predictions-e160.json")))
RES160 = json.load(open(os.path.join(D160, "results.json")))
COR160 = json.load(open(os.path.join(D160, "corrections.json")))
P = json.load(open(os.path.join(HERE, "predictions-e165.json")))
fails = []


def ok(cond, what):
    print(("ok   " if cond else "FAIL ") + what)
    if not cond:
        fails.append(what)


print(f"E165 amendment A2 self-test: report_d_e165.py {C.sha256_file(RD.__file__)[:16]}..., check_path_e165.py "
      f"{C.sha256_file(os.path.join(HERE, 'check_path_e165.py'))[:16]}..., score_e165.py {C.sha256_file(S.__file__)[:16]}...")
print(f"  E160 results.json {C.sha256_file(os.path.join(D160, 'results.json'))[:16]}..., corrections.json {C.sha256_file(os.path.join(D160, 'corrections.json'))[:16]}...")

# 1 ----------------------------------------------------------------------------------------------------------------------------------------------
with tempfile.TemporaryDirectory() as td:
    ccp = os.path.join(td, "ccheck-s1.json")
    with gzip.open(os.path.join(D160, "ccheck-s1.json.gz"), "rb") as f, open(ccp, "wb") as g:
        shutil.copyfileobj(f, g)
    runs = S.collect([os.path.join(D160, "aifoundry2", "s1")], S.load_ccheck([ccp]), S.pass_by_rep)
meta6, zeros6 = S.parent_meta(P160)
cells = S.cells_of(runs, meta6, zeros6)
rows = RD.d_795(cells, meta6, zeros6)
rc = RES160["cells"]
reg_bad = [lab for lab, r in rows.items() if (r["D_w"], r["D_runs"]) != (rc[lab].get("D_w"), rc[lab].get("D_runs"))]
ok(len(rows) == 48 and not reg_bad, f"E160: the registered form, from score_e165's own collect and cells_of, equals results.json's D on all {len(rows)} pool tiles "
   f"({len(reg_bad)} differ)")
c1 = COR160["C1_fp16_tiles"]
fp16 = {lab: r for lab, r in rows.items() if r["type"] == "fp16" and r["D_w_795"] is not None}
c1_bad = [r["name"] for r in fp16.values() if (r["D_w_795"], r["D_runs_795"]) != (c1[r["name"]]["D_w_corrected"], c1[r["name"]]["D_runs_corrected"])]
ok(len(fp16) == len(c1) == 12 and not c1_bad, f"E160: D_795 equals C1's corrected D (D_w and D_runs) on all {len(c1)} fp16 tiles that are not the anchor "
   f"({len(c1_bad)} differ); the shift {min(r['D_w_795'] - r['D_w'] for r in fp16.values()):+.3f} to {max(r['D_w_795'] - r['D_w'] for r in fp16.values()):+.3f} W "
   f"(C1: {COR160['C1_anchor']['mean_D_shift_w']:+.3f} high)")
other = [r for r in rows.values() if r["type"] != "fp16" and r["D_w_795"] is not None]
same = [r["name"] for r in other if (r["D_w_795"], r["D_runs_795"]) != (r["D_w"], r["D_runs"])]
ok(len(other) == 48 - 12 - 3 and not same, f"E160: D_795 equals the registered D on all {len(other)} fp32 and int8 tiles that are not anchors ({len(same)} differ)")
ab = RD.anchors_below(cells, zeros6)
r16 = next(iter(fp16.values()))["ref_by_pass"]["1"]
ok(ab["fp16"]["passes_below"] == [1] and not ab["fp32"]["passes_below"] and not ab["int8"]["passes_below"]
   and abs(r16["w"] - COR160["C1_anchor"]["w_at_800_passes"]) < 5e-4,
   f"E160: the anchors' passes below 795 MHz: fp16 {ab['fp16']['passes_below']} ({ab['fp16']['burst_mhz_runs']} MHz), fp32 none, int8 none; pass 1's "
   f"reference {r16['w']} W (C1: {COR160['C1_anchor']['w_at_800_passes']} W, the anchor's two 800 MHz passes)")
anc = [r for r in rows.values() if r["name"].endswith("anchor6_zeros")]
ok(len(anc) == 3 and all(r["D_w_795"] is None and "zeros anchor" in r["why"] for r in anc), "E160: the three zeros anchors get no D_795 (inputs, never scored)")

# 2 ----------------------------------------------------------------------------------------------------------------------------------------------
meta, zeros = S.meta_of(P)
SHORT = 2.185
mk = []
for name, t in sorted(P["tiles"].items()):
    if t["left_out"]:
        continue
    q = t["models"]["M9"]["a2_q140l"]
    for p in (1, 2, 3):
        f, w = q["burst_mhz"], q["burst_board_w"]
        if name == "fp16.anchor7_zeros" and p == 1:
            f, w = 752.0, w - SHORT
        mk.append({"label": C.label_of(name), "pass": p, "counted": True, "complete": True, "burst_mhz": f, "burst_w": w,
                   "rise_c": q["burst_die_rise_c"], "die_start": 54, "die_max": 54 + q["burst_die_rise_c"], "p800_w": None, "c_w": None,
                   "burst_rate": None, "peak_w": q["burst_board_w"] + 1.0, "first_down_kind": None, "burst_ghz_kernel": None})
cm = S.cells_of(mk, meta, zeros)
rm = RD.d_795(cm, meta, zeros)
w_a = P["tiles"]["fp16.anchor7_zeros"]["models"]["M9"]["a2_q140l"]["burst_board_w"]
bad16, badot = [], []
for lab, r in rm.items():
    if r["D_w_795"] is None:
        continue
    true = round(P["tiles"][r["name"]]["models"]["M9"]["a2_q140l"]["burst_board_w"] - P["tiles"][f"{r['type']}.anchor7_zeros"]["models"]["M9"]["a2_q140l"]["burst_board_w"], 3)
    if r["type"] == "fp16":
        if abs(r["D_w"] - r["D_w_795"] - SHORT / 3) > 1.5e-3 or abs(r["D_w_795"] - true) > 1.5e-3:
            bad16.append(r["name"])
    elif (r["D_w_795"], r["D_runs_795"]) != (r["D_w"], r["D_runs"]):
        badot.append(r["name"])
n16 = sum(1 for r in rm.values() if r["type"] == "fp16" and r["D_w_795"] is not None)
ok(n16 > 0 and not bad16, f"made up: with the fp16 anchor's pass 1 at 752 MHz and {SHORT} W short, all {n16} fp16 tiles' registered D read {SHORT / 3:.3f} W high "
   f"and their D_795 their made-up D ({len(bad16)} differ)")
ok(not badot, f"made up: every fp32 and int8 tile's D_795 equals its registered D ({len(badot)} differ)")
mp = P["rules"]["min_passes"]
s0 = S.score(cm, P, mp, light=True)
s1 = S.score(RD.with_d795(cm, rm), P, mp, light=True)
same = json.dumps(RD.strip_d(s0), sort_keys=True) == json.dumps(RD.strip_d(s1), sort_keys=True)
d0, d1 = RD.d_rows(s0)["fp16"], RD.d_rows(s1)["fp16"]
ok(same and d0["M9_as_frozen_D_mean"] != d1["M9_as_frozen_D_mean"],
   f"made up: score_e165.score() on the two forms differs in the D rows only (rules, lines, coverage, peaks, tiles' clocks and boards identical: {same}); "
   f"fp16's M9-as-frozen D mean {d0['M9_as_frozen_D_mean']} -> {d1['M9_as_frozen_D_mean']} W")

# 3 ----------------------------------------------------------------------------------------------------------------------------------------------
cp = subprocess.run([sys.executable, "-B", os.path.join(HERE, "check_path_e165.py")], capture_output=True, text=True, cwd=ROOT)
last = (cp.stdout.strip().splitlines() or [""])[-1]
ok(cp.returncode == 0 and last.startswith("CHECK-PATH: PASS"), f"check_path_e165.py on this tree: rc {cp.returncode}, {last}")
cs = subprocess.run([sys.executable, "-B", os.path.join(HERE, "check_path_e165.py"), "--self-test"], capture_output=True, text=True, cwd=ROOT)
last = (cs.stdout.strip().splitlines() or [""])[-1]
ok(cs.returncode == 0 and last.endswith("ALL PASS"), f"check_path_e165.py --self-test: rc {cs.returncode}, {last}")

print("A2 SELF-TEST:", "ALL PASS" if not fails else f"{len(fails)} FAIL")
sys.exit(1 if fails else 0)
