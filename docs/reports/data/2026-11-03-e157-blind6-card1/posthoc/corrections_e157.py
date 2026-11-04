#!/usr/bin/env python3
"""E157, corrections after verification (Tue 3 Nov 2026, week 45). Post hoc and reported only: no rule, verdict, prediction, reduction or
measured number changes. Standard library only; committed inputs only:
  this data dir: scored.json, scored-e153.json, e157.json, e157-e142footing.json;
  E142's reductions as posthoc_e157.py reads them (E142's e142.json; Q139(u)'s reduced/e142-footing.json);
  tools/claims-v3/e157/ccheck-domain.txt (the first-read notes, written at registration) and predictions-e157.json;
  E160's results.json, ccheck-smoke.json and ccheck-stoptest-board.json (docs/reports/data/2026-11-03-e160-blind6-aifoundry2/);
  E153's scored.json and ccheck/ccheck-all.json (docs/reports/data/2026-11-03-e153-blind6-aifoundry3/).
It prints the numbers the README's section "Corrections after verification" quotes:
  C1 every case's rms (M8, non-anchor tiles), in order, with its tile count;
  C2 who read the first-read ranges: E157's first-read tiles against E160's and E153's checked launches;
  C4 each model's float bias over B1's 18 tiles and over the 30 priority-1 tiles; E78's random anchors against E142, both footings;
  C5 the single-bit tiles' errors and bands; X1, X2, S1 and S2 at every scored arm.
    python3 posthoc/corrections_e157.py <data dir> [--json <out.json>]     # prints corrections.txt's content
SPDX-License-Identifier: Apache-2.0
"""
import gzip
import json
import math
import os
import sys

D = sys.argv[1]
OUT_JSON = sys.argv[sys.argv.index("--json") + 1] if "--json" in sys.argv else None
REPO = os.path.abspath(D)
while not os.path.isdir(os.path.join(REPO, "tools", "claims-v3")) and REPO != "/":
    REPO = os.path.dirname(REPO)
sys.path.insert(0, os.path.join(REPO, "tools", "claims-v3", "e157"))
import score_e157 as S  # noqa: E402

DATA = os.path.join(REPO, "docs", "reports", "data")
E160D = os.path.join(DATA, "2026-11-03-e160-blind6-aifoundry2")
E153D = os.path.join(DATA, "2026-11-03-e153-blind6-aifoundry3")


def load(*p):
    return json.load(open(os.path.join(*p)))


sc = load(D, "scored.json")
sc153 = load(D, "scored-e153.json")
prim = load(D, "e157.json")
e142f = load(D, "e157-e142footing.json")
E142 = load(DATA, "2026-11-02-e142-blind5-card1", "e142.json")
E142U = load(DATA, "2026-11-03-q139u-footing", "reduced", "e142-footing.json")
reg = load(REPO, "tools", "claims-v3", "e157", "predictions-e157.json")
pw = sc["primary"]["power_rows"]
out = {}


def rms(v):
    return math.sqrt(sum(x * x for x in v) / len(v)) if v else None


def mean(v):
    return sum(v) / len(v) if v else None


print("E157 corrections after verification (post hoc and reported only; nothing here is a verdict)")

# C1: every case's rms, in order
cases = {}
for t, r in pw["M8"].items():
    if r["pool_anchor"] or r["error"] is None:
        continue
    cases.setdefault(r["case"].split(" ")[0], []).append(t)
rows = []
for c, ts in cases.items():
    row = {"case": c, "n": len(ts)}
    for m in ("M8", "M7", "M6"):
        e = [pw[m][t]["error"] for t in ts]
        row[m] = {"rms": rms(e), "bias": mean(e)}
    row["inside_M8"] = sum(1 for t in ts if pw["M8"][t]["inside"])
    rows.append(row)
rows.sort(key=lambda r: r["M8"]["rms"])
print("\nC1 every case, non-anchor tiles, M8's rms (bias), W, lowest first; M7 and M6 beside")
for r in rows:
    print(f"  {r['case']} ({r['n']} tiles): M8 {r['M8']['rms']:.3f} ({r['M8']['bias']:+.3f}), {r['inside_M8']} of {r['n']} inside;"
          f" M7 {r['M7']['rms']:.3f}; M6 {r['M6']['rms']:.3f}")
big = [r for r in rows if r["n"] > 2]
print(f"  lowest M8 rms of all cases: {rows[0]['case']} ({rows[0]['n']} tiles); of the cases with more than two tiles: {big[0]['case']} "
      f"({big[0]['n']} tiles, {big[0]['M8']['rms']:.3f} W)")
out["C1_cases"] = rows

# C2: the first-read ranges, and who read them
dom = []
dom_summary = None
for line in open(os.path.join(REPO, "tools", "claims-v3", "e157", "ccheck-domain.txt")):
    if line.startswith("{"):
        dom_summary = json.loads(line)
        continue
    if not line.strip() or line.startswith("#"):
        continue
    path = line.split()[1]
    note = line.split("|", 1)[1].strip() if "|" in line else ""
    dom.append({"tile": os.path.basename(path)[:-4], "pool": "blind6" if "/blind6/" in path else "blind5", "note": note})
first = [d for d in dom if d["note"].startswith("first silicon read")]
r160 = load(E160D, "results.json")["c_check"]
smoke160 = load(E160D, "ccheck-smoke.json")["summary"]
stop160 = load(E160D, "ccheck-stoptest-board.json")["summary"]
by160 = {k[3:]: v for k, v in r160["by_tile"].items() if k.startswith("b6-")}
c153 = load(E153D, "scored.json")["c_status"]
all153 = load(E153D, "ccheck", "ccheck-all.json")["summary"]
c157 = json.load(gzip.open(os.path.join(D, "ccheck", "ccheck-session.json.gz")))["summary"]
pool6 = sorted(pw["M8"])
int8_6 = [t for t in pool6 if pw["M8"][t]["type"] == "int8"]
real_6 = [t for t in pool6 if pw["M8"][t]["real"]]
print("\nC2 the first-read ranges (tools/claims-v3/e157/ccheck-domain.txt, written at registration) and who read them")
print(f"  E157's domain file: {len(dom)} tiles, {len(first)} with first-read notes "
      f"({sum(1 for d in first if d['pool'] == 'blind6')} of pool 6, {sum(1 for d in first if d['pool'] == 'blind5')} of pool 5: K1's); "
      f"its own summary line: {json.dumps(dom_summary)}")
n160 = r160["launches"] + smoke160["launches"] + stop160["launches"]
p160 = r160["by_verdict"].get("PASS", 0) + smoke160["PASS"] + stop160["PASS"]
print(f"  E160 (aifoundry2): s1 {r160['by_verdict'].get('PASS', 0)} PASS of {r160['launches']}, smoke {smoke160['PASS']} of "
      f"{smoke160['launches']}, board stop test {stop160['PASS']} of {stop160['launches']}: {p160} of {n160}")
ran160 = [t for t in pool6 if t in by160]
print(f"  E160 ran {len(ran160)} of pool 6's {len(pool6)} tiles, every launch PASS: "
      f"{all(set(v) == {'PASS'} for v in by160.values())}; not run: {sorted(set(pool6) - set(ran160))}")
print(f"    int8: {sum(1 for t in int8_6 if t in by160)} of {len(int8_6)}; real tiles: {sum(1 for t in real_6 if t in by160)} of "
      f"{len(real_6)}")
f6 = [d for d in first if d["pool"] == "blind6"]
f6_160 = [d["tile"] for d in f6 if d["tile"] in by160]
print(f"    of E157's {len(f6)} pool-6 first-read tiles, E160 ran {len(f6_160)}; not: "
      f"{sorted(d['tile'] for d in f6 if d['tile'] not in by160)}")
wrap = [d["tile"] for d in first if "wrap" in d["note"]]
print(f"    E157's tiles whose notes say the words wrap at 32 bits: {len(wrap)} ({sum(1 for t in wrap if t in by160)} run by E160)")
print(f"  E153 (aifoundry3): {all153['PASS']} PASS of {all153['launches']}; {len(c153)} tiles C-checked, "
      f"{sum(1 for d in first if d['tile'] in c153 and c153[d['tile']]['all_pass'])} of E157's {len(first)} first-read tiles among them, "
      f"all PASS")
print(f"  E157 (aifoundry1 card 1, ccheck/ccheck-session.json.gz): {c157['PASS']} PASS of {c157['launches']} (fp32 "
      f"{c157['by_type']['fp32']['PASS']}, fp16 {c157['by_type']['fp16']['PASS']}, int8 {c157['by_type']['int8']['PASS']})")
pool5_first = sorted(d["tile"] for d in first if d["pool"] == "blind5")
first_not160 = sorted(d["tile"] for d in first if d["tile"] not in by160)
print(f"  E157's first-read tiles E160 did not run (so first checked on silicon by E157 and E153, the same evening): {first_not160}")
out["C2"] = {"domain_tiles": len(dom), "first_read_tiles": len(first), "first_read_pool6": len(f6), "first_read_pool5": len(first) - len(f6),
             "e160_launches": n160, "e160_pass": p160, "e160_pool6_tiles_run": len(ran160),
             "e160_not_run": sorted(set(pool6) - set(ran160)), "e160_int8": [sum(1 for t in int8_6 if t in by160), len(int8_6)],
             "e160_real": [sum(1 for t in real_6 if t in by160), len(real_6)], "e160_first_read_pool6_run": len(f6_160),
             "wrap_tiles": len(wrap), "wrap_tiles_e160": sum(1 for t in wrap if t in by160),
             "e153_launches": all153["launches"], "e153_pass": all153["PASS"], "e153_tiles": len(c153),
             "e157_launches": c157["launches"], "e157_pass": c157["PASS"], "first_read_not_run_by_e160": first_not160,
             "first_read_pool5": pool5_first}

# C4: the bias comparison and E78's anchors
b1 = sc["primary"]["rules"]["E157-B1"]["tiles"]
print(f"\nC4 bias, measured - model, W, over B1's {len(b1)} priority-1 float tiles (12 fp32, 6 fp16) and over all 30 priority-1 tiles")
out["C4_bias"] = {}
for m in ("M8", "M7", "M6"):
    e = [pw[m][t]["error"] for t in b1]
    a30 = sc["primary"]["reported"][m]["power_priority1_all"]
    print(f"  {m}: {mean(e):+.5f} over the {len(e)} floats; {a30['bias']:+.5f} over the {a30['n']}")
    out["C4_bias"][m] = {"floats_18": mean(e), "priority1_30": a30["bias"]}
print("  E78's random anchors, E157 - E142 (D, W; posthoc_e157.py (b)'s arithmetic)")
out["C4_anchors"] = {}
for frame, mine, theirs in (("Q139(u)'s footing", prim, E142U), ("E142's own footing (0.2414)", e142f, E142)):
    d = {}
    for t in ("fp32.randn", "fp16.randn", "int8.full"):
        m_, _ = S.measured(mine, [t], "D", 2)
        d[t] = m_[t]["mean"] - theirs["items"][t]["D"]["mean"]
    print(f"    {frame}: " + ", ".join(f"{t} {v:+.3f}" for t, v in d.items()) + f"; largest move {max(abs(v) for v in d.values()):.3f}")
    out["C4_anchors"][frame] = d

# C5: the single-bit tiles, and the card term at every arm
print("\nC5 the single-bit tiles (case S), measured - model, W, and whether each sits inside that model's 95% band")
out["C5_single_bits"] = {}
for t in sorted(cases.get("S", [])):
    s = "; ".join(f"{m} {pw[m][t]['error']:+.3f} ({'in' if pw[m][t]['inside'] else 'OUT'})" for m in ("M8", "M7", "M6"))
    print(f"  {t} ({pw['M8'][t]['type']}, priority {pw['M8'][t]['priority']}): {s}")
    out["C5_single_bits"][t] = {m: [pw[m][t]["error"], pw[m][t]["inside"]] for m in ("M8", "M7", "M6")}
print("  X1, X2 (median D card 1 / aifoundry3) and S1, S2 (the zeros level's error), scored-e153.json, primary and every scored arm")
out["C5_card_term"] = {}
arms = [("primary", sc153["primary"])] + [(k, v) for k, v in sc153["arms"].items()]
fails = {"E157-X1": 0, "E157-X2": 0, "E157-S1": 0, "E157-S2": 0}
scored_arms = 0
for name, a in arms:
    rr = a.get("rules")
    if not rr or "E157-X1" not in rr:
        print(f"    {name}: not scored (no rules)")
        continue
    if name != "primary":
        scored_arms += 1
        for k in fails:
            fails[k] += rr[k]["verdict"] == "FAIL"
    x1, x2, s1, s2 = rr["E157-X1"], rr["E157-X2"], rr["E157-S1"], rr["E157-S2"]
    print(f"    {name}: X1 {x1['median_ratio']:.4f} {x1['verdict']}; X2 {x2['median_ratio']:.4f} {x2['verdict']}; "
          f"S1 {s1['rel_err'] * 100:+.2f}% {s1['verdict']}; S2 {s2['rel_err'] * 100:+.2f}% {s2['verdict']}")
    out["C5_card_term"][name] = {"X1": [x1["median_ratio"], x1["verdict"]], "X2": [x2["median_ratio"], x2["verdict"]],
                                 "S1": [s1["rel_err"], s1["verdict"]], "S2": [s2["rel_err"], s2["verdict"]]}
print(f"  FAIL counts over the {scored_arms} scored arms: " + ", ".join(f"{k[5:]} {v}" for k, v in fails.items()))
out["C5_arm_fail_counts"] = {"scored_arms": scored_arms, **fails}

if OUT_JSON:
    with open(OUT_JSON, "w") as f:
        json.dump(out, f, indent=1, sort_keys=True)
        f.write("\n")
