#!/usr/bin/env python3
"""E153 (Q139): corrections after verification. POST HOC, never a verdict. Written at the desk on Tue 3 Nov 2026, about 18:20 PST, by the
fix pass, after an independent verifier re-derived every registered number and verdict of E153 (all stand) and reported one major and six
minor faults in what the README and the lane's result say about them. Nothing here was registered. Nothing frozen, measured or registered
changes, and no verdict moves.

Inputs, all committed: this directory's scored.json, scored-session.json, results.md, results-session.md, e153*.json, runs*.csv,
ccheck/ccheck-all.json, aifoundry3/e153/p1531*/runs.jsonl and interim/ (the two interim printouts C1 discloses); the registration's
tools/claims-v3/e153/score_e153.py and predictions-e153.json, and the scorer AS REGISTERED, read from git (359c96b2, before amendment A1);
pool 6's blind6.json, predictions-blind6-aifoundry3.json and card-scale-blind6.json; E157's scored.json, scored-e153.json and C check, and
E160's C check. Standard library only. Nothing is written into the tree except corrections.json beside this file, and no bytecode.

    python3 -B docs/reports/data/2026-11-03-e153-blind6-aifoundry3/corrections_e153.py > docs/reports/data/2026-11-03-e153-blind6-aifoundry3/corrections.txt

  C1  the interim look before A1: the verdicts the registered scorer printed at 16:40:11 PST on pass 15310 listed twice, and at 16:41:35 after
      the fix, against the final verdicts; then the scorer as registered (359c96b2, before A1) and the scorer at HEAD, each re-run in memory on
      the committed final reduction, its seven arms and the C check, compared with scored.json and results.md key by key
  C2  rank 5's own test on this card: the cheap-read scale predicted for aifoundry3 held out (from the other two cards; card-scale-blind6.json),
      against the card's scale of 1 and against CS0's measured ratio; the same forms on card 1 (E157); E157's X1/X2 on this e153.json
  C3  rank 8: R1 and R2 at the primary and at every arm
  C4  the 3,140 launches of the C check, by input
  C5  fp32.a_zeros_b_complement: its D, its pool rule and its power rows (blog point 7's fp32 figure)
  C6  M8's near-whole-byte discount (bsat): the tiles it acts on, the three where it acts most against M8/M7/M6 and M8's band; M2 and M1 with
      the registered compare_rule on the 30 and on the 28 without the two priority-1 bsat tiles; int8's rms with and without them
  C7  what the C check covers: distinct inputs, the host and kernel by sha256; E157's and E160's own C checks and E157's K1

SPDX-License-Identifier: Apache-2.0
"""
import collections
import gzip
import hashlib
import importlib.util
import json
import math
import os
import random
import re
import subprocess
import sys
import types

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
E153T = os.path.join(ROOT, "tools", "claims-v3", "e153")
BLIND6 = os.path.join(ROOT, "tools", "claims-v3", "kinds", "blind6")
E157 = os.path.join(ROOT, "docs", "reports", "data", "2026-11-03-e157-blind6-card1")
E160 = os.path.join(ROOT, "docs", "reports", "data", "2026-11-03-e160-blind6-aifoundry2")
REGISTERED = "359c96b2"   # E153's registration; A1 is e6ca949d
ARMS = [("session_own", "e153-session.json"), ("auto_dips_removed", "e153-auto-nodips.json"), ("kfrozen_dips_kept", "e153-kfrozen-dips.json"),
        ("leak0.1994", "e153-leak0.1994.json"), ("leak0.3803", "e153-leak0.3803.json"), ("leak0", "e153-leak0.json"),
        ("gates_off", "e153-gatesoff.json")]   # collect_e153.sh's order
OUT = {}


def J(*p):
    return json.load(open(os.path.join(*p)))


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def git_show(rev, rel):
    return subprocess.run(["git", "-C", ROOT, "show", f"{rev}:{rel}"], capture_output=True, check=True).stdout


def load_scorer_from_text(src, name):
    """Run a scorer's source as a module whose __file__ is the registration's score_e153.py, so its REG and pick6 resolve in the tree."""
    mod = types.ModuleType(name)
    mod.__file__ = os.path.join(E153T, "score_e153.py")
    exec(compile(src, name, "exec"), mod.__dict__)
    return mod


def run_like_main(S, reg, prim_name, runs_name, arms):
    """score_e153.main() without its file writes: the same calls in the same order (collect_e153.sh's arguments)."""
    ccheck, passes = os.path.join(HERE, "ccheck"), os.path.join(HERE, "aifoundry3", "e153")
    prim = J(HERE, prim_name)
    cst = S.c_status(reg, prim, ccheck, passes)
    res = {"experiment": "E153", "c_status": cst, "primary": S.score(prim, reg, os.path.join(HERE, runs_name), cst, None), "arms": {}}
    for name, fn in arms:
        arm = J(HERE, fn)
        res["arms"][name] = S.score(arm, reg, None, S.c_status(reg, arm, ccheck, passes), None)
        for k in ("power_rows", "heat_rows"):
            (res["arms"][name].get("primary") or {}).pop(k, None)
    pv = S.verdicts(res["primary"])
    res["verdicts"] = pv
    res["arm_sensitive"] = {r: [n for n, x in res["arms"].items() if S.verdicts(x).get(r) != v] for r, v in pv.items()}
    md = S.markdown(res, reg)
    return json.loads(json.dumps(res, default=lambda o: None)), md


def diff(a, b, path=""):
    out = []
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b), key=str):
            if k not in a or k not in b:
                out.append(f"{path}/{k}: only in {'the re-run' if k in a else 'the committed file'} ({json.dumps(a.get(k, b.get(k)))[:60]})")
            else:
                out += diff(a[k], b[k], f"{path}/{k}")
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            out.append(f"{path}: length {len(a)} against {len(b)}")
        for i, (x, y) in enumerate(zip(a, b)):
            out += diff(x, y, f"{path}[{i}]")
    elif isinstance(a, (int, float)) and isinstance(b, (int, float)) and not isinstance(a, bool) and not isinstance(b, bool):
        if not (isinstance(a, float) and isinstance(b, float) and math.isnan(a) and math.isnan(b)):
            if abs(float(a) - float(b)) > 1e-9 * max(1.0, abs(float(a))):
                out.append(f"{path}: {a} against {b}")
    elif a != b:
        out.append(f"{path}: {json.dumps(a)[:60]} against {json.dumps(b)[:60]}")
    return out


def md_verdicts(md):
    v = {}
    for m in re.finditer(r"^\| (E153-[A-Z0-9]+) \| \*\*([A-Z ]+)\*\* \| ([^|]*) \|", md, re.M):
        v[m.group(1)] = (m.group(2), m.group(3).strip())
    for m in re.finditer(r"^- (E153-CS[0-9]-?\w*): \*\*([A-Z ]+)\*\* ?(.*)$", md, re.M):
        v[m.group(1)] = (m.group(2), m.group(3).strip())
    k = re.search(r"^(K1 [A-Z ]+ \(.*)$", md, re.M)
    if k:
        v["K1 line"] = ("", k.group(1))
    kp = re.search(r"^Kept passes: (.*)$", md, re.M)
    if kp:
        v["header"] = ("", kp.group(1))
    return v


reg = J(E153T, "predictions-e153.json")
scored = J(HERE, "scored.json")
prim = scored["primary"]["primary"]
rows = prim["power_rows"]
print(__doc__.split("\n\n")[0].replace("\n", " "))
print()

# ------------------------------------------------------------------------------------------------------------------------------------ C1
print("C1  The interim look before A1, and what A1 changed")
interim = {}
for tag, fn_md, fn_js in (("16:40:11 PST, the scorer as registered (pre-A1), pass 15310 listed twice", "results-15310x2-pre-a1.md",
                           "scored-15310x2-pre-a1.json"),
                          ("16:41:35 PST, the scorer after the A1 fix, the same input", "results-15310x2-a1.md", "scored-15310x2-a1.json")):
    js = J(HERE, "interim", fn_js)
    interim[tag] = {"passes": js["primary"]["passes"], "verdicts": js["verdicts"], "c_excluded": js["primary"].get("c_excluded"),
                    "c_not_measured": js["primary"].get("c_not_measured"), "md_sha256": sha(os.path.join(HERE, "interim", fn_md)),
                    "json_sha256": sha(os.path.join(HERE, "interim", fn_js)),
                    "readings": {k: v[1] for k, v in md_verdicts(open(os.path.join(HERE, "interim", fn_md)).read()).items()}}
final_v = scored["verdicts"]
tags = list(interim)
print(f"  inputs: {tags[0]}; {tags[1]}")
for t in tags:
    print(f"    {t}: passes {interim[t]['passes']}, C-excluded {interim[t]['c_excluded']}, not measured {interim[t]['c_not_measured']};"
          f" sha256 md {interim[t]['md_sha256'][:12]}..., json {interim[t]['json_sha256'][:12]}...")
print(f"  {'rule':16s} {'16:40:11 (pre-A1)':18s} {'16:41:35 (A1)':15s} {'final (4 passes)':17s} interim reading (pre-A1 printout)")
same_except = []
for r in final_v:
    a, b, c = interim[tags[0]]["verdicts"].get(r), interim[tags[1]]["verdicts"].get(r), final_v[r]
    rd = interim[tags[0]]["readings"].get(r, "")
    print(f"  {r:16s} {str(a):18s} {str(b):15s} {c:17s} {rd}")
    if a != c:
        same_except.append(r)
print(f"  rules whose interim (pre-A1) verdict differs from the final: {same_except}")
OUT["C1"] = {"interim": interim, "final_verdicts": final_v, "differ_from_final": same_except}

old_src = git_show(REGISTERED, "tools/claims-v3/e153/score_e153.py")
old_reg = git_show(REGISTERED, "tools/claims-v3/e153/predictions-e153.json")
old_pick6 = git_show(REGISTERED, "tools/claims-v3/ccheck/pick6.py")
same_reg = old_reg == open(os.path.join(E153T, "predictions-e153.json"), "rb").read()
same_pick6 = old_pick6 == open(os.path.join(ROOT, "tools", "claims-v3", "ccheck", "pick6.py"), "rb").read()
print(f"  predictions-e153.json at HEAD equals {REGISTERED}'s: {same_reg}; pick6.py equals {REGISTERED}'s: {same_pick6}")
assert same_reg and same_pick6
spec = importlib.util.spec_from_file_location("score_e153_head", os.path.join(E153T, "score_e153.py"))
S_head = importlib.util.module_from_spec(spec)
spec.loader.exec_module(S_head)
S_old = load_scorer_from_text(old_src.decode(), f"{REGISTERED}:tools/claims-v3/e153/score_e153.py")
c1 = {}
for label, S in ((f"as registered ({REGISTERED}, before A1)", S_old), ("at HEAD (A1)", S_head)):
    res, md = run_like_main(S, reg, "e153.json", "runs.csv", ARMS)
    d = diff(res, scored)
    res_s, md_s = run_like_main(S, reg, "e153-session.json", "runs-session.csv", [])
    d_s = diff(res_s, J(HERE, "scored-session.json"))
    md_same = md == open(os.path.join(HERE, "results.md")).read()
    mds_same = md_s == open(os.path.join(HERE, "results-session.md")).read()
    print(f"  the scorer {label}, re-run on the committed final reduction: scored.json {len(d)} differences, results.md identical: {md_same};"
          f" scored-session.json {len(d_s)} differences, results-session.md identical: {mds_same}")
    for x in d:
        print(f"      scored.json {x}")
    for x in d_s:
        print(f"      scored-session.json {x}")
    c1[label] = {"scored_json_differences": d, "results_md_identical": md_same, "session_differences": d_s,
                 "results_session_md_identical": mds_same, "verdicts": res["verdicts"]}
not_measured_final = scored["primary"].get("c_not_measured")
_pp = J(HERE, "e153.json")["per_pass"]
_np = {t: sum(1 for p in _pp.values() if (p.get(t) or {}).get("D") is not None) for t in list(reg["tiles"]) + list(reg["k1"])}
print(f"  the final data's c_not_measured: {not_measured_final}; every tile has D in at least {min(_np.values())} kept passes"
      f" (fewest: {sorted(t for t, n in _np.items() if n == min(_np.values()))})")
OUT["C1"]["passes_per_tile_min"] = min(_np.values())
OUT["C1"]["rescore"] = c1
print()

# ------------------------------------------------------------------------------------------------------------------------------------ C2
print("C2  Rank 5's own test on this card: a card's scale predicted from cheap reads, within 1%, on a held-out card")
cs = scored["primary"]["CS"]
csf = J(BLIND6, "card-scale-blind6.json")
e157s = J(E157, "scored-e153.json")["primary"]["rules"]
c2 = {"note_q139m": csf["_note"], "formula": csf["formula"], "families": {}}
for fam, e157rule in (("floats", "E157-S1"), ("int8", "E157-S2")):
    v = cs[f"E153-CS0-{fam}"]
    m = v["measured_scale"]
    print(f"  {fam}: CS0 measured {m:.4f} [{v['lo95']:.4f}, {v['hi95']:.4f}] over {v['n']} tiles (M8 applies 1.0): CS0 {v['verdict']}")
    rowsf = []
    for form, p in sorted(v["cheap_read_predictions_for_a3"].items(), key=lambda kv: abs(kv[1] - 1.0)):
        c1f = e157s[e157rule]["every_form"].get(form, {})
        r = {"form": form, "pred_a3": p, "rel_to_1": p - 1.0, "rel_to_measured": p / m - 1.0, "within_1pct_of_1": abs(p - 1.0) <= 0.01,
             "within_1pct_of_measured": abs(p / m - 1.0) <= 0.01, "card1_rel_err_E157": c1f.get("rel_err"),
             "card1_within_1pct_E157": c1f.get("within_1pct")}
        rowsf.append(r)
        print(f"    {form:40s} predicts {p:.4f}: {100 * r['rel_to_1']:+6.2f}% of 1, {100 * r['rel_to_measured']:+6.2f}% of {m:.4f}"
              f"  | on card 1 (E157) {100 * (r['card1_rel_err_E157'] or 0):+6.2f}%")
    best1 = min(rowsf, key=lambda r: abs(r["rel_to_1"]))
    bestm = min(rowsf, key=lambda r: abs(r["rel_to_measured"]))
    inside1 = [r["form"] for r in rowsf if r["within_1pct_of_1"]]
    insidem = [r["form"] for r in rowsf if r["within_1pct_of_measured"]]
    both = [r["form"] for r in rowsf if r["within_1pct_of_measured"] and r["card1_within_1pct_E157"]]
    print(f"    within 1% of 1: {inside1 or 'none'} (closest {best1['form']}, {100 * best1['rel_to_1']:+.2f}%);"
          f" within 1% of the measured {m:.4f}: {insidem or 'none'} (closest {bestm['form']}, {100 * bestm['rel_to_measured']:+.2f}%);"
          f" within 1% here (measured) and on card 1: {both or 'none'}")
    c2["families"][fam] = {"cs0": v, "forms": rowsf, "within_1pct_of_1": inside1, "within_1pct_of_measured": insidem, "both_cards": both}
for k in ("E157-X1", "E157-X2", "E157-S1", "E157-S2"):
    x = e157s[k]
    if "median_ratio" in x:
        print(f"  {k} (E157, on this e153.json): median D(card 1) / D(aifoundry3) {x['median_ratio']:.4f} [{x['lo95']:.4f}, {x['hi95']:.4f}]"
              f" over {x['n']}, M8's card term {x['card_term']:.4f} ({100 * (x['median_ratio'] / x['card_term'] - 1):+.2f}%):"
              f" {x['verdict']}; E153-CS1's reading within 1% of M8: {x['E153_CS1_reading_within_1pct_of_M8']}")
    else:
        print(f"  {k} (E157): {x['form']} predicts {x['predicted']:.4f} against {x['measured']:.4f} ({100 * x['rel_err']:+.2f}%): {x['verdict']}")
    c2[k] = {kk: vv for kk, vv in x.items() if kk not in ("ratios", "every_form")}
arms157 = J(E157, "scored-e153.json")["arms"]
for a in arms157:
    r = arms157[a].get("rules")
    if not r:
        print(f"    E157 arm {a}: not scored there ({json.dumps(arms157[a].get('NOT SCORED'))[:80]})")
        continue
    print(f"    E157 arm {a}: E153-CS1 reading within 1% floats {r['E157-X1'].get('E153_CS1_reading_within_1pct_of_M8')},"
          f" int8 {r['E157-X2'].get('E153_CS1_reading_within_1pct_of_M8')}")
print(f"  scored.json's E153-CS1: {cs['E153-CS1']['verdict']} ({cs['E153-CS1']['why']})")
OUT["C2"] = c2
print()

# ------------------------------------------------------------------------------------------------------------------------------------ C3
print("C3  Rank 8 (item 7, real tensors): pool 6's real-tile sub-rule on this card")
r1, r2 = prim["rules"]["E153-R1"], prim["rules"]["E153-R2"]
print(f"  primary: R1 {r1['verdict']}, rms {r1['rms']:.3f} W over {r1['interval']['n']} real tiles {r1['interval']['mix']},"
      f" line {r1['interval']['hi95']:.3f} (2.5% point {r1['interval']['lo95']:.3f}), the pool's own non-real rms {r1['pool_own_rms']:.3f} W;"
      f" R2 {r2['verdict']}, {r2['inside']} of {r2['n']} inside, outside {r2['outside']}")
real_err = sorted(((rows["M8"][t]["error"], t) for t in r1["tiles"]), key=lambda x: abs(x[0]), reverse=True)
print(f"  the largest real-tile errors (measured - M8, W): " + ", ".join(f"{t} {e:+.3f}" for e, t in real_err[:3]))
c3 = {"primary": {"R1": r1, "R2": r2}, "arms": {}}
for a in scored["arms"]:
    ar = scored["arms"][a]["primary"]["rules"]
    c3["arms"][a] = {"R1": [ar["E153-R1"]["verdict"], ar["E153-R1"].get("rms")], "R2": [ar["E153-R2"]["verdict"], ar["E153-R2"].get("inside")]}
    print(f"    arm {a}: R1 {ar['E153-R1']['verdict']} {ar['E153-R1'].get('rms', float('nan')):.3f} W; R2 {ar['E153-R2']['verdict']}"
          f" {ar['E153-R2'].get('inside')} of {ar['E153-R2'].get('n')}")
OUT["C3"] = c3
print()

# ------------------------------------------------------------------------------------------------------------------------------------ C4
print("C4  The 3,140 launches of the C check, by input (ccheck/ccheck-all.json, each launch's 'values')")
cc = J(HERE, "ccheck", "ccheck-all.json")
pool6, k1 = set(reg["tiles"]), set(reg["k1"])
g, names = collections.Counter(), collections.defaultdict(set)
for v in cc["launches"]:
    val = str(v.get("values"))
    base = val.rsplit("/", 1)[-1].replace(".bin", "")
    if "/kinds/blind5/" in val and base in k1:
        key = "K1: the six re-run pool-5 tiles"
    elif "/kinds/blind6/" in val and base in pool6 and ".anchor6_" in base:
        key = "pool 6's six anchors"
    elif "/kinds/blind6/" in val and base in pool6:
        key = "pool 6's 44 new kinds"
    elif "/kinds/tiles/" in val:
        key, base = "E78's six anchors", val.split("/kinds/tiles/")[1]
    else:
        key = f"the tie ({val})"
    g[key] += 1
    names[key].add(base)
for k, c in g.most_common():
    print(f"  {c:5d}  {k} ({len(names[k])} distinct)")
print(f"  total {sum(g.values())} launches on {sum(len(s) for s in names.values())} distinct inputs; summary {cc['summary']['launches']} launches,"
      f" {cc['summary']['PASS']} PASS")
OUT["C4"] = {"by_input": dict(g), "distinct": {k: len(s) for k, s in names.items()}, "summary": cc["summary"]}
print()

# ------------------------------------------------------------------------------------------------------------------------------------ C5
print("C5  fp32.a_zeros_b_complement (blog point 7's fp32 figure)")
e = J(HERE, "e153.json")
t5 = "fp32.a_zeros_b_complement"
it = e["items"][t5]["D"]
pp = {p: e["per_pass"][p][t5]["D"] for p in e["per_pass"] if t5 in e["per_pass"][p]}
rule5 = next(x["rule"] for x in J(BLIND6, "blind6.json")["tiles"] if x["name"] == t5)
print(f"  D {it['mean']:.4f} +- {it['ci95']:.3f} W (95%, {it['n']} passes: " + ", ".join(f"{p} {d:.3f}" for p, d in pp.items()) + ")")
print(f"  M8 {rows['M8'][t5]['pred']:.3f} (error {rows['M8'][t5]['error']:+.3f}, band [{rows['M8'][t5]['lo95']:.3f}, {rows['M8'][t5]['hi95']:.3f}]),"
      f" M7 {rows['M7'][t5]['pred']:.3f}, M6 {rows['M6'][t5]['pred']:.3f} (scored.json > primary.primary.power_rows)")
print(f"  the pool's rule: {rule5}")
t5b = "int8.a_zeros_b_lineflip"
print(f"  beside it, {t5b}: D {e['items'][t5b]['D']['mean']:.4f} +- {e['items'][t5b]['D']['ci95']:.3f} W ({e['items'][t5b]['D']['n']} passes)")
OUT["C5"] = {"D": it, "per_pass": pp, "rows": {m: rows[m][t5] for m in ("M8", "M7", "M6")}, "rule": rule5, "int8_lineflip_D": e["items"][t5b]["D"]}
print()

# ------------------------------------------------------------------------------------------------------------------------------------ C6
print("C6  M8's int8 near-whole-byte discount (bsat, -56.8 fJ a bit): where it acts, and what carries M2")
p6 = J(BLIND6, "predictions-blind6-aifoundry3.json")["tiles"]
bs_t = {t: (p6[t].get("M8", {}).get("features") or p6[t].get("features") or {}).get("bsat", 0) for t in p6 if t.startswith("int8.")}
acting = sorted(((f, t) for t, f in bs_t.items() if f), reverse=True)
print("  bsat feature by tile: " + ", ".join(f"{t} {f:g}" for f, t in acting))
top = [t for f, t in acting if f == acting[0][0]]
c6 = {"bsat": {t: f for f, t in acting}, "top": {}}
for t in top:
    r8 = rows["M8"][t]
    print(f"  {t} (priority {r8['priority']}): measured {r8['measured']:.3f} W; M8 {r8['pred']:.3f} [{r8['lo95']:.2f}, {r8['hi95']:.2f}]"
          f" {'inside' if r8['lo95'] <= r8['measured'] <= r8['hi95'] else 'OUTSIDE'}, error {r8['error']:+.3f};"
          f" M7 {rows['M7'][t]['pred']:.3f} (error {rows['M7'][t]['error']:+.3f}); M6 {rows['M6'][t]['pred']:.3f} (error {rows['M6'][t]['error']:+.3f})")
    c6["top"][t] = {m: {k: rows[m][t][k] for k in ("pred", "lo95", "hi95", "measured", "error", "priority")} for m in ("M8", "M7", "M6")}
bs = reg["plan"]["bootstrap"]
cov = [t for t in reg["sets"]["coverage_tiles"] if rows["M8"].get(t, {}).get("error") is not None]
err = {m: {t: rows[m][t]["error"] for t in cov} for m in ("M8", "M7", "M6")}


def boot_share(err_a, err_b, sel, rid):
    """compare_rule's own draws (the same RNG and order), returned with the share of draws at or below zero."""
    rms = S_head.rms
    rng = random.Random(bs["seed"] + sum(map(ord, rid)))
    ds = []
    for _ in range(bs["draws"] // 4):
        s = [sel[rng.randrange(len(sel))] for _ in sel]
        ds.append(rms([err_a[t] for t in s]) - rms([err_b[t] for t in s]))
    ds.sort()
    return ds[int(0.025 * len(ds))], ds[int(0.975 * len(ds)) - 1], sum(1 for d in ds if d <= 0) / len(ds)


p1bsat = [t for t in top if rows["M8"][t]["priority"] == 1 and t in cov]
cov28 = [t for t in cov if t not in p1bsat]
c6["M"] = {}
for rid, other in (("E153-M2", "M7"), ("E153-M1", "M6")):
    reg_r = prim["rules"][rid]
    full = S_head.compare_rule(err["M8"], err[other], cov, bs, rid)
    lo, hi, share = boot_share(err["M8"], err[other], cov, rid)
    assert abs(full["d_rms_w"] - reg_r["d_rms_w"]) < 1e-12 and abs(full["lo95"] - reg_r["lo95"]) < 1e-12 and abs(lo - full["lo95"]) < 1e-12
    w28 = S_head.compare_rule(err["M8"], err[other], cov28, bs, rid)
    lo28, hi28, share28 = boot_share(err["M8"], err[other], cov28, rid)
    alt = [S_head.compare_rule(err["M8"], err[other], cov28, bs, f"{rid}-posthoc-{k}") for k in range(1, 5)]
    print(f"  {rid} (M8 against {other}), the registered 30: d {full['d_rms_w']:+.4f} W [{full['lo95']:+.4f}, {full['hi95']:+.4f}] {full['verdict']}"
          f" (reproduces scored.json exactly; share of draws <= 0: {share:.4f})")
    print(f"     without {p1bsat} (28, post hoc): d {w28['d_rms_w']:+.4f} W [{w28['lo95']:+.4f}, {w28['hi95']:+.4f}] {w28['verdict']}"
          f" (share <= 0: {share28:.4f}); four other seeds: " + "; ".join(f"[{a['lo95']:+.4f}, {a['hi95']:+.4f}] {a['verdict']}" for a in alt))
    c6["M"][rid] = {"registered": full, "share_le_0": share, "without_two": w28, "share_le_0_without": share28, "other_seeds_without": alt}
i8 = [t for t in reg["sets"]["priority1_by_format"]["int8"] if t in cov]
i8w = [t for t in i8 if t not in p1bsat]
c6["int8_rms"] = {}
for m in ("M8", "M7", "M6"):
    a, b = S_head.rms([err[m][t] for t in i8]), S_head.rms([err[m][t] for t in i8w])
    c6["int8_rms"][m] = {"12": a, "10_without_two": b}
print("  priority-1 int8 rms, all 12 / without the two (10): " + "; ".join(f"{m} {v['12']:.3f} / {v['10_without_two']:.3f} W"
                                                                       for m, v in c6["int8_rms"].items()))
OUT["C6"] = c6
print()

# ------------------------------------------------------------------------------------------------------------------------------------ C7
print("C7  What the C check covers, and the other cards' own checks")
hosts = collections.Counter((v.get("host_sha256"), v.get("kernel_sha256")) for v in cc["launches"])
for (h, k), c in hosts.items():
    print(f"  {c} launches: host {str(h)[:16]}..., kernel {str(k)[:16]}...")
print(f"  distinct inputs checked: {sum(len(s) for s in names.values())} (pool 6's 50, K1's 6, E78's 6 anchors, the tie); pool 5's other"
      f" {36 - len(k1)} tiles were not re-run")
c157 = json.load(gzip.open(os.path.join(E157, "ccheck", "ccheck-session.json.gz")))["summary"]
k157 = {k: v for k, v in J(E157, "scored.json")["verdicts"].items() if "K1" in k}
s160 = []
for f in ("ccheck-s1.json.gz", "ccheck-smoke.json", "ccheck-stoptest-board.json"):
    p = os.path.join(E160, f)
    s160.append((f, (json.load(gzip.open(p)) if f.endswith(".gz") else J(p))["summary"]))
print(f"  E157 (aifoundry1 card 1): {c157['PASS']} of {c157['launches']} launches PASS; its K1: {k157}")
print(f"  E160 (aifoundry2): " + ", ".join(f"{f} {s['PASS']} of {s['launches']}" for f, s in s160)
      + f"; {sum(s['PASS'] for f, s in s160)} of {sum(s['launches'] for f, s in s160)} in all")
OUT["C7"] = {"host_kernel": {f"{h}|{k}": c for (h, k), c in hosts.items()}, "e157": {"summary": c157, "k1": k157},
             "e160": {f: s for f, s in s160}}

json.dump(OUT, open(os.path.join(HERE, "corrections.json"), "w"), indent=1, default=lambda o: None)
print()
print("corrections.json written beside this file.")
