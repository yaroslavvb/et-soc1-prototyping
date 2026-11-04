#!/usr/bin/env python3
"""E170 (Q141(w)): the scorer's self-test, on the parent's committed data. No card, no device, no ssh; it reads committed files only and writes only
a temporary directory (the decompressed C-check file).

    python3 -B tools/claims-v3/e170/selftest_score_e170.py > tools/claims-v3/e170/selftest-score.txt      (about 4 minutes, one core)

The parent: E170 is E165's design on card 0, and E165 has no data yet, so the parent's committed data are E165's parent's, E160's session on
aifoundry2 (pool 6 in governed 6 s bursts: the same harness, burst shape, reduction and C join). E157's and E164's are 600 MHz sessions of E78's
frame, a different reduction, so they cannot test this scorer.

  1. THE PARENT'S REGISTERED VERDICTS, through the reduction E170 imports. score_e165.collect and cells_of (imported unchanged by score_e170.py),
     run on E160's committed session with its committed ccheck-s1.json under E160's frozen predictions and rules (score_e165.score_parent_e160),
     reproduce E160's results.json field for field: every rule, E160-C, R0, every pass alone and the rules over the complete runs.
  2. THE CARD TERM AGAINST THE FROZEN CODE, on E160's own cells: pred_card0 in E165's form (full_level False, kappa 1) equals the frozen burst()
     (E165's primary path) field for field on the 45 pool tiles; with the level in full, every pinned tile's board moves by (1 - beta) x the
     format's session offset, to the frozen code's rounding (the level is session_delta's, at weight 1); the kappa0 arm scales burst D exactly.
  3. E170'S RULES AT KNOWN ANSWERS, on cells made up from E170's frozen predictions: measured = the primary passes every rule, M1 and M2 BETTER;
     boards 0.8 W high fail B (FAIL LOW); boards +-1.2 W fail B on the rms and W; a true scale of 0.90 fails X0 and B (FAIL HIGH); measured D = M6's
     chain reads M1 WORSE; rises 2 C high fail H1 and H3; clocks 6 MHz low fail F; seven tiles leave the rules NOT SCORED; no anchor leaves every
     rule NOT SCORED; one counted pass of half A leaves every rule NOT SCORED.
  4. The order, the left-out tiles and the constants: 135 runs, each pass opening with the three zeros anchors, half B in ascending estimate; a run
     whose label is not the order's at its idx is refused; a run of a tile left out by name is refused; kappa0 is the median of its five ratios; an
     anchor burst at 752 MHz is not counted; a format with no anchor takes the others' mean.
  5. E170-S's reader on E160's session (a known answer): no line under 590 MHz (aifoundry2 has never shown the 300 MHz point), and the runs at or
     over 62 W are E160's hot tiles (its board maximum 79.37 W), so S reads FAIL there, as it must.
SPDX-License-Identifier: Apache-2.0
"""
import copy
import gzip
import json
import os
import shutil
import sys
import tempfile

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import e170_common as C  # noqa: E402
import score_e170 as SC  # noqa: E402

S = SC.S
ROOT = C.ROOT
D160 = os.path.join(ROOT, "docs/reports/data/2026-11-03-e160-blind6-aifoundry2")
P160 = json.load(open(os.path.join(ROOT, "tools/claims-v3/e160/predictions-e160.json")))
RES160 = json.load(open(os.path.join(D160, "results.json")))
P6 = json.load(open(os.path.join(ROOT, "tools/claims-v3/kinds/blind6/predictions-blind6-aifoundry2.json")))["tiles"]
P = SC.load_pred()
fails = []


def ok(cond, what):
    print(("ok   " if cond else "FAIL ") + what)
    if not cond:
        fails.append(what)


def cmp(got, want, path=""):
    out = []
    if isinstance(want, dict):
        for k in want:
            out += cmp(got.get(k) if isinstance(got, dict) else None, want[k], f"{path}.{k}")
    elif got != want:
        out.append(f"{path}: {got!r} != {want!r}")
    return out


print(f"E170 scorer self-test: score_e170.py {C.sha256_file(SC.__file__)}, e170_common.py {C.sha256_file(C.__file__)}, "
      f"predictions-e170.json {C.sha256_file(SC.PRED_REL)}, score_e165.py {C.sha256_file(S.__file__)} (imported unchanged)")
print(f"  parent: E160 results.json {C.sha256_file(os.path.join(D160, 'results.json'))}")

# 1 ----------------------------------------------------------------------------------------------------------------------------------------------
with tempfile.TemporaryDirectory() as td:
    ccp = os.path.join(td, "ccheck-s1.json")
    with gzip.open(os.path.join(D160, "ccheck-s1.json.gz"), "rb") as f, open(ccp, "wb") as g:
        shutil.copyfileobj(f, g)
    ok(C.sha256_file(ccp) == RES160["ccheck_files"]["ccheck-s1.json"], f"E160's ccheck-s1.json decompressed is the file its results name ({C.sha256_file(ccp)[:16]}...)")
    runs = S.collect([os.path.join(D160, "aifoundry2", "s1")], S.load_ccheck([ccp]), S.pass_by_rep)
meta6, zeros6 = S.parent_meta(P160)
ok(len(runs) == RES160["runs"] == 150 and sum(m["counted"] for m in runs) == RES160["runs_counted"] and sum(m["complete"] for m in runs) == RES160["runs_complete"],
   f"E160's s1 reduced again through the imported collect: {len(runs)} runs, {sum(m['complete'] for m in runs)} complete, {sum(m['counted'] for m in runs)} counted")
cells = S.cells_of(runs, meta6, zeros6)
sc = S.score_parent_e160(cells, P160, 2)
d = cmp(sc["rules"], RES160["score"]["rules"])
ok(not d and sc["tiles_scored"] == RES160["score"]["tiles_scored"] == 48,
   f"E160's registered rules reproduced field for field ({len(RES160['score']['rules'])} rules, {sum(len(v) for v in RES160['score']['rules'].values())} fields, "
   f"{len(d)} differ): " + "; ".join(f"{k} {v['verdict']}" for k, v in sc["rules"].items()) + (f" | {d[:3]}" if d else ""))
cr = S.c_rule(runs, True)
d = cmp(cr, {k: RES160["c_check"][k] for k in ("verdict", "launches", "by_verdict", "runs_not_all_pass")})
ok(not d and cr["verdict"] == "PASS" and cr["launches"] == 2596, f"E160-C reproduced: {cr['verdict']}, {cr['launches']} launches ({len(d)} differ)")
rp = S.replicate(cells, P160["replicate"], P160["rules"], beside=("e143",))
d = cmp(rp, RES160["replicate"])
ok(not d and rp["verdict"] == "PASS", f"E160-R0 reproduced: {rp['verdict']} ({len(d)} differ)")
dp = []
for p in RES160["passes"]:
    sp = S.score_parent_e160(S.cells_of(runs, meta6, zeros6, passes={p}), P160, 1)
    mine = {k: {kk: v.get(kk) for kk in ("n", "rms", "inside", "verdict")} for k, v in sp["rules"].items()}
    dp += cmp(mine, RES160["per_pass"][str(p)], f"pass{p}")
ok(not dp, f"E160's every pass alone reproduced ({len(RES160['passes'])} passes, {len(dp)} differ)")
scc = S.score_parent_e160(S.cells_of(runs, meta6, zeros6, key="complete"), P160, 2)
d = cmp(scc["rules"], RES160["as_e143_counted"]["score_rules"])
ok(not d, f"E160's rules over the complete runs (C not required) reproduced ({len(d)} differ)")

# 2 ----------------------------------------------------------------------------------------------------------------------------------------------
A2 = C.m9a2()
lab2 = {t["label"]: n for n, t in P160["tiles"].items()}
mine = {lab2[lab]: c for lab, c in cells.items() if lab in lab2}
anc = {}
for n, t in P160["tiles"].items():
    if t["anchor"] and n.endswith("anchor6_zeros"):
        c = mine[n]
        anc[t["type"]] = [{"burst_w": w, "burst_mhz": f, "die_start": T} for w, f, T in zip(c["burst_w_runs"], c["burst_mhz_runs"], c["die_start_runs"])]
pool = sorted(n for n in mine if n in P6 and not P160["tiles"][n]["anchor"] and mine[n]["n"] >= 2)
same, moved, scaled, worst = 0, [], 0, 0.0
delta, _ = A2.session_delta(anc)
for n in pool:
    t = P160["tiles"][n]["type"]
    Dn = P6[n]["M8"]["D600_a3_footing_w"]
    ds = mine[n]["die_start_runs"]
    b = C.m9a2().burst(Dn, t, anchors=anc, die_starts=ds, D_band_hw=0.0)
    e165 = C.pred_card0(Dn, t, anc, ds, 0.0, kappa=1.0, full_level=False)
    same += (e165["burst_board_w"] == b["burst_board_w"] and e165["burst_mhz"] == b["burst_mhz"] and e165["burst_D_w"] == b["burst_D_w"])
    full = C.pred_card0(Dn, t, anc, ds, 0.0, kappa=1.0, full_level=True)
    if b["group"] == "pinned":
        dv = (full["burst_board_w"] - b["burst_board_w"]) - (1.0 - A2.BETA) * delta[t]
        worst = max(worst, abs(dv))
        moved.append(dv)
    k0 = C.pred_card0(Dn, t, anc, ds, 0.0)
    scaled += abs(k0["burst_D_w"] - round(C.KAPPA0 * b["burst_D_w"], 3)) < 1e-9
ok(len(pool) >= 40 and same == len(pool), f"E165's form through pred_card0 (full_level False, kappa 1) equals the frozen burst() on E160's {len(pool)} pool tiles "
   f"(board, clock and burst D field for field: {same} of {len(pool)})")
ok(moved and worst <= 0.003, f"the level in full moves every pinned tile's board by (1 - beta) x its format's session offset ({len(moved)} pinned tiles, "
   f"worst {worst:.4f} W; beta {A2.BETA:.4f}; offsets {json.dumps({k: round(v, 3) for k, v in delta.items()})})")
ok(scaled == len(pool), f"the primary's burst D is kappa0 x the frozen burst D on every tile ({scaled} of {len(pool)})")
ew = []
for n in pool:
    full = C.pred_card0(P6[n]["M8"]["D600_a3_footing_w"], P160["tiles"][n]["type"], anc, mine[n]["die_start_runs"], 0.0, kappa=1.0)
    if full["group"] == "pinned":
        ew.append(mine[n]["burst_w"] - full["burst_board_w"])
print(f"     (information: on aifoundry2 itself, E160's pinned tiles with M8's blind D, the level in full and kappa 1: board rms {C.rms(ew):.3f} W, "
      f"mean {C.mean(ew):+.3f} W over {len(ew)} tiles)")

# 3 ----------------------------------------------------------------------------------------------------------------------------------------------
Z = {"fp32": 29.6, "fp16": 29.5, "int8": 29.8}
ANC = {t: [{"burst_w": Z[t], "burst_mhz": 800.0, "die_start": 54.0} for _ in range(6)] for t in Z}
DS = [54.0, 54.0, 54.0]


def made_up(fw=lambda n, v: v, fm=lambda n, v: v, fr=lambda n, v: v, fD=None, names=None, anchors=ANC, a_passes=(1, 2, 3)):
    """cells for the scored tiles and the three zeros anchors, measured = the primary unless a function says otherwise"""
    names = P["scored"] if names is None else names
    cells = {}
    for zn in C.ZEROS_ANCHORS:
        t = P["tiles"][zn]["type"]
        rr = (anchors or {}).get(t, [])
        if rr:
            cells[C.label_of(zn)] = {"label": C.label_of(zn), "passes": list(range(1, len(rr) + 1)), "n": len(rr),
                                     "burst_w_runs": [r["burst_w"] for r in rr], "burst_mhz_runs": [r["burst_mhz"] for r in rr],
                                     "die_start_runs": [r["die_start"] for r in rr], "burst_w": Z[t], "burst_mhz": 800.0, "rise_c": 4.0, "peak_w": Z[t] + 2}
    for n in names:
        t = P["tiles"][n]
        ps = list(a_passes) if t["tier"] == "A" else [4, 5, 6]
        pr = C.pred_card0(t["models"]["M9"]["D600_a3_footing_w"], t["type"], anchors or ANC, DS, t["models"]["M9"]["D_band_hw"])
        D = (C.KAPPA0 * pr["a2_burst_D_w"]) if fD is None else fD(n, pr)
        w = pr["zeros_level_w"] + D if fD is not None else pr["burst_board_w"]
        cells[t["label"]] = {"label": t["label"], "passes": ps, "n": len(ps), "die_start_runs": [54.0] * len(ps),
                             "burst_w": fw(n, w), "burst_mhz": fm(n, pr["burst_mhz"]), "rise_c": fr(n, pr["burst_die_rise_c"]),
                             "D_w": D, "peak_w": w + 2.0}
    return cells


def vs(res):
    r = res["rules"]
    return {k: v["verdict"] for k, v in r.items()} if "note" not in r else r


base = SC.score(made_up(), P)
v = vs(base)
ok(all(str(x).startswith("PASS") for k, x in v.items() if k not in ("E170-M1", "E170-M2")) and v["E170-M1"] == "BETTER" and v["E170-M2"] == "BETTER",
   f"measured = the primary ({base['tiles_scored']} tiles): {v}")
v = vs(SC.score(made_up(fw=lambda n, w: w + 0.8), P))
ok(v["E170-B"] == "FAIL LOW" and v["E170-X0"] == "PASS", f"boards 0.8 W high: B {v['E170-B']}, W {v['E170-W']}, X0 {v['E170-X0']}")
sg = {n: (1 if i % 2 else -1) for i, n in enumerate(P["scored"])}
v = vs(SC.score(made_up(fw=lambda n, w: w + 1.2 * sg[n]), P))
ok(v["E170-B"] == "FAIL (rms)" and v["E170-W"] == "FAIL", f"boards +-1.2 W: B {v['E170-B']}, W {v['E170-W']}")
r90 = SC.score(made_up(fD=lambda n, pr: 0.90 * pr["a2_burst_D_w"]), P)
v = vs(r90)
ok(v["E170-X0"] == "FAIL" and v["E170-B"] == "FAIL HIGH", f"a true scale of 0.90: X0 {v['E170-X0']} (median {r90['rules']['E170-X0']['median']}), B {v['E170-B']} "
   f"(mean {r90['rules']['E170-B']['mean']} W)")
pm6 = {}
for n in P["scored"]:
    t = P["tiles"][n]
    pm6[n] = C.pred_card0(t["models"]["M6"]["D600_a3_footing_w"], t["type"], ANC, DS, 0.0)["burst_D_w"]
v = vs(SC.score(made_up(fD=lambda n, pr: pm6[n]), P))
ok(v["E170-M1"] == "WORSE", f"measured D = M6's chain: M1 {v['E170-M1']}, M2 {v['E170-M2']}")
v = vs(SC.score(made_up(fr=lambda n, r: r + 2.0), P))
ok(v["E170-H1"] == "FAIL" and v["E170-H3"] == "FAIL", f"rises 2 C high: H1 {v['E170-H1']}, H3 {v['E170-H3']}")
v = vs(SC.score(made_up(fm=lambda n, f: f - 6.0), P))
ok(v["E170-F"] == "FAIL", f"clocks 6 MHz low: F {v['E170-F']}")
seven = SC.score(made_up(names=P["scored"][:7]), P)
v = vs(seven)
ok(all(str(x).startswith("NOT SCORED") for x in v.values()), f"seven tiles: {v}")
na = SC.score(made_up(anchors=None), P)
ok("note" in na["rules"], f"no zeros-anchor burst: {na['rules']}")
one = SC.scoring([{"counted": True, "pass": 1, "label": P["tiles"][P["scored"][0]]["label"], "burst_w": 40.0, "burst_mhz": 800.0, "rise_c": 4.0,
                   "die_start": 54.0, "die_max": 58.0, "c_w": None, "p800_w": None, "burst_rate": None, "peak_w": 41.0, "first_down_kind": None,
                   "burst_ghz_kernel": None}], P, "counted")
ok("note" in one["score"], f"one counted pass of half A: {one['score'].get('note')}")

# 4 ----------------------------------------------------------------------------------------------------------------------------------------------
order = P["order"]
starts = [i for i in range(len(order)) if i == 0 or order[i]["pass"] != order[i - 1]["pass"]]
opens = len(starts) == 6 and all(sorted(order[i + k]["name"] for k in range(3)) == sorted(C.ZEROS_ANCHORS) for i in starts)
bh = [o for o in order if o["half"] == "B" and o["pass"] == 4 and o["name"] not in C.ZEROS_ANCHORS]
asc = [P["tiles"][o["name"]]["est_card0_peak_w"] for o in bh]
ok(len(order) == 135 and opens and asc == sorted(asc) and P["passes"] == [1, 2, 3, 4, 5, 6],
   f"the order: {len(order)} runs, every pass opens with the three zeros anchors, half B ascending ({asc[0]:.2f} -> {asc[-1]:.2f} W, the last "
   f"{bh[-1]['name']})")
f = SC.pass_by_order(P)
try:
    f({"run": "x", "idx": 3, "label": "b7-not.this"})
    refused = False
except SystemExit:
    refused = True
ok(refused and f({"run": "y", "idx": 40, "label": order[40]["label"]}) == order[40]["pass"], "a run whose label is not the order's at its idx is refused")
why = SC.stray_left_out([{"label": "b7-fp32.uniform_pm1"}], P)
ok(why is not None and len(P["left_out"]) == 19, f"a run of a left-out tile is refused ({why}); 19 left out by name")
rat = sorted(C.kappa0_ratios().values())
ok(C.KAPPA0 == round(rat[2], 4) == 0.9463, f"kappa0 {C.KAPPA0} is the median of its five ratios {[round(x, 4) for x in rat]}")
z1 = C.zeros_level({"fp32": [{"burst_w": 30.0, "burst_mhz": 752.0, "die_start": 54.38}], "int8": [{"burst_w": 31.0, "burst_mhz": 800.0, "die_start": A2.TREF}]},
                   "fp32", [A2.TREF], A2.KT, A2.TREF)
ok(abs(z1 - 31.0) < 1e-9, f"an anchor burst at 752 MHz is not counted, and a format with none takes the others' mean ({z1})")

# 5 ----------------------------------------------------------------------------------------------------------------------------------------------
P160_like = {"left_out": []}
sf = SC.safety(runs, [os.path.join(D160, "aifoundry2", "s1")], P160_like)
ok(not sf["runs_under_590_mhz"] and sf["runs_at_or_over_62w"] and abs((sf["board_max_w"] or 0) - 79.37) < 0.01 and sf["verdict"] == "FAIL",
   f"E170-S's reader on E160: {len(sf['runs_under_590_mhz'])} runs under 590 MHz, {len(sf['runs_at_or_over_62w'])} runs at or over 62 W, board max "
   f"{sf['board_max_w']} W: {sf['verdict']}, as it must on aifoundry2's hot tiles")

print()
print("ALL PASS" if not fails else f"{len(fails)} FAILED")
sys.exit(1 if fails else 0)
