#!/usr/bin/env python3
"""E158 (Q139): the numbers quoted by the README's "Corrections after verification" (Tue 3 Nov 2026), POST HOC, desk only. Standard library.

    python3 docs/reports/data/2026-11-03-e158-l3-retention/corrections_e158.py > docs/reports/data/2026-11-03-e158-l3-retention/corrections.txt
    (writes corrections.json beside it)

Reads committed files only: this directory's results.json, posthoc.json and aifoundry2/ records, tools/claims-v3/e158/ (the frozen model, imported
unchanged, its desk and predictions) and E146's committed results.json. It refits nothing that a rule registered; every curve below is the registered
scorer (model_e158.fit_iso, fit_logi) run on a subset chosen after the data, so every line is post hoc. No measured, frozen or registered number or
verdict changes.

  C1 F6 ran in E146 (2 Nov); R3's pass, ISO at every w of its near-best interval, and ISO refitted without the collapse rungs; the out-of-sample errors
  C2 the two block structures that collapse, against F6 and D4, their all-fresh prices and their neighbours
  C3 the zeros' energy per op step three ways: the whole board, over the idle rest, over E119's 800 MHz base
  C4 C's occupancy off the two collapses (R2's registered logic applied post hoc), and the plateau's KB confound
  C5 the counts: rungs run, the 98 bursts by block
"""
import gzip
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools/claims-v3/e158"))
import model_e158 as M  # noqa: E402

RES = json.load(open(os.path.join(HERE, "results.json")))
PH = json.load(open(os.path.join(HERE, "posthoc.json")))
P = json.load(open(os.path.join(ROOT, "tools/claims-v3/e158/predictions-e158.json")))
E146 = json.load(open(os.path.join(ROOT, "docs/reports/data/2026-11-02-e146-gemm-stores/results.json")))
DESK = M.load_desk()
AB, C1 = M.load_prices()
V = RES["rules"]
SH = V["shares"]
OUT = {}


def T8(key, src=RES):
    return (src["per_shape"].get(key) or {}).get("T800")


def pc(v):
    return f"{100 * v:+.2f}%"


def f6_err(fit):
    cr = M.iso_curve(fit)
    return {t: T8(f"F6.{t}") / M.T_model(DESK["shapes"]["F6"], cr, fit["w"], AB, C1, t)["T800"] - 1 for t in M.TYPES}


def iso_at_w(rungs, w):
    """the registered PAV fit at one fixed w (fit_iso's inner step), as fit_iso returns it"""
    ys = [y for _, y, _ in rungs]
    ws = [k for _, _, k in rungs]
    xs = [M.far_x(DESK["shapes"][s], w)[0] for s, _, _ in rungs]
    fit = M.pav_decreasing(xs, ys, ws)
    rms = math.sqrt(sum(k * (y - f) ** 2 for y, f, k in zip(ys, fit, ws)) / sum(ws))
    pts = sorted(set((round(x, 4), round(f, 6)) for x, f in zip(xs, fit)))
    return {"w": w, "rms_share": rms, "points": [[x, f] for x, f in pts]}


def r2_logic(fit):
    """R2's registered words (E158.md), applied to a fit"""
    near = M.W_GRID[M.W_GRID.index(fit["w_near"][0]):M.W_GRID.index(fit["w_near"][1]) + 1]
    if fit["rms_share"] > 0.06:
        return "NO SINGLE CURVE"
    if 1.0 in near and 0.0 not in near and near[0] >= 0.5:
        return "C OCCUPIES THE L3"
    if 0.0 in near and 1.0 not in near and near[-1] <= 0.5:
        return "C TAKES NONE OF IT"
    if 0.0 not in near and 1.0 not in near:
        return "PARTIAL"
    return "UNRESOLVED"


rungs22 = [(s, v["share"], v["passes"]) for s, v in SH.items()]
F6m = {t: T8(f"F6.{t}") for t in M.TYPES}
F6e146 = {t: T8(f"F6.{t}", E146) for t in M.TYPES}

# C1
print("C1 POST HOC: F6 ran in E146; R3's pass and what carries it; the out-of-sample errors")
print(f"  F6 = {DESK['shapes']['F6']['arm']} (MB, NB, KB = {DESK['shapes']['F6']['blocks']}): E146's session (2 Nov) measured T800 "
      + " / ".join(f"{F6e146[t]:.4f}" for t in M.TYPES) + " us (fp32 / fp16 / int8; E146 results.json per_shape), its far-B share through MAB "
      f"{next(r['e146_share'] for r in PH['shares'] if r['rung'] == 'F6'):+.3f} (posthoc.json shares); here " + " / ".join(f"{F6m[t]:.4f}" for t in M.TYPES))
print("  so F6 was never fitted (no curve saw it), but it was run before E158, and its 0.33 share was known when E158's ladder was set (E158.md, 'Why')")
iso = V["R2"]["iso"]
print(f"  R3 as registered: ISO on 22 rungs, w {iso['w']}, near-best {iso['w_near']}, rms {iso['rms_share']:.4f}; F6 "
      + " / ".join(pc(V["R3"]["per_format"][t]["ISO"]["rel"]) for t in M.TYPES) + f" -> {V['R3']['verdict']}")
lo, hi = iso["w_near"]
worst = 0.0
by_w = {}
for w in M.W_GRID:
    if lo - 1e-9 <= w <= hi + 1e-9:
        e = f6_err(iso_at_w(rungs22, w))
        by_w[str(w)] = {t: round(v, 4) for t, v in e.items()}
        worst = max(worst, max(abs(v) for v in e.values()))
print(f"  ISO at each w of the near-best interval {lo}-{hi}: the worst |F6 error| {100 * worst:.2f}% (R3 holds at every such w)")
subsets = {"without K4n8": ("K4n8",), "without K6n4": ("K6n4",), "without K6n4 and K4n8 (20 rungs)": ("K6n4", "K4n8")}
refits = {}
for name, drop in subsets.items():
    rs = [r for r in rungs22 if r[0] not in drop]
    f = M.fit_iso(rs, DESK)
    e = f6_err(f)
    refits[name] = {"n": len(rs), "w": f["w"], "w_tied": f["w_tied"], "w_near": f["w_near"], "rms_share": round(f["rms_share"], 4),
                    "F6": {t: round(v, 4) for t, v in e.items()}, "R3": "PASS" if all(abs(v) <= 0.03 for v in e.values()) else "FAIL"}
    print(f"  ISO refitted {name}: w {f['w']} (near {f['w_near']}), rms {f['rms_share']:.4f}; F6 " + " / ".join(pc(e[t]) for t in M.TYPES)
          + f" -> {refits[name]['R3']} of the 3% rule")
cr = M.iso_curve(iso)
fb = M.far_bins(DESK["shapes"]["F6"])
nfar = sum(v for _, _, v in fb)
at54 = sum(v for a, c, v in fb if (a + 0.5) * M.BIN_MB + iso["w"] * (c + 0.5) * M.BIN_MB > 52.0)
print(f"  F6's far B lines an op: {nfar:.0f}, of them {at54:.0f} at 54 MB (w {iso['w']}), where ISO's r is {cr(54.0):.3f}: the pool of K4n8 "
      f"({SH['K4n8']['share']:+.3f}) and K6n6 ({SH['K6n6']['share']:+.3f}); at 42-48 MB ISO's r is {cr(45.0):.3f}, which pools K6n4 ({SH['K6n4']['share']:+.3f}) with plateau rungs")
e = RES["errors"]
print("  out of sample (results.json errors), STRICT-C -> ISO (LOGI): E146's committed ladder, the 18 KB >= 2 cells "
      f"{100 * e['e146_ladder_T800_rel']['STRICT-C']['rms_kb2_18']:.1f}% -> {100 * e['e146_ladder_T800_rel']['ISO']['rms_kb2_18']:.1f}% "
      f"({100 * e['e146_ladder_T800_rel']['LOGI']['rms_kb2_18']:.1f}%) rms; all 24 {100 * e['e146_ladder_T800_rel']['STRICT-C']['rms_all24']:.1f}% -> "
      f"{100 * e['e146_ladder_T800_rel']['ISO']['rms_all24']:.1f}% ({100 * e['e146_ladder_T800_rel']['LOGI']['rms_all24']:.1f}%); D2 and D4 here "
      f"{100 * e['here_D2_D4_T800_rel']['STRICT-C']['rms']:.1f}% -> {100 * e['here_D2_D4_T800_rel']['ISO']['rms']:.1f}% "
      f"({100 * e['here_D2_D4_T800_rel']['LOGI']['rms']:.1f}%); R4 {V['R4']['verdict']}")
single = {}
for lab, src in (("D4 here", RES), ("D4 E146", E146), ("D8 E146", E146), ("K4n8 here", RES), ("K6n4 here", RES), ("D2 here", RES)):
    s = lab.split()[0]
    single[lab] = {}
    for t in M.TYPES:
        T = T8(f"{s}.{t}", src)
        if T is None:
            continue
        single[lab][t] = round(T / M.T_model(DESK["shapes"][s], cr, iso["w"], AB, C1, t)["T800"] - 1, 4)
print("  ISO's single-shape errors (measured / predicted - 1; positive = ISO reads it fast): "
      + "; ".join(f"{lab} " + " / ".join(f"{t} {pc(v)}" for t, v in d.items()) for lab, d in single.items()))
OUT["C1"] = {"F6_e146_T800": F6e146, "F6_here_T800": F6m, "R3_registered": {t: V["R3"]["per_format"][t]["ISO"]["rel"] for t in M.TYPES},
             "iso_by_w_near": by_w, "worst_in_near": round(worst, 4), "refits": refits, "F6_far_lines": nfar, "F6_far_at_54mb": at54,
             "iso_r_54": round(cr(54.0), 4), "iso_r_45": round(cr(45.0), 4),
             "out_of_sample": {"e146_kb2_18": {m: e["e146_ladder_T800_rel"][m]["rms_kb2_18"] for m in ("STRICT-C", "ISO", "LOGI", "PRIOR")},
                               "e146_all24": {m: e["e146_ladder_T800_rel"][m]["rms_all24"] for m in ("STRICT-C", "ISO", "LOGI", "PRIOR")},
                               "here_D2_D4": {m: e["here_D2_D4_T800_rel"][m]["rms"] for m in ("STRICT-C", "ISO", "LOGI", "PRIOR")}},
             "single": single}

# C2
print("\nC2 POST HOC: the two block structures that collapse, against the other shapes with the same (NB, KB), their all-fresh price and their neighbours (fp32)")
c2 = {}
for s in ("K6n4", "F6", "K4n8", "D4"):
    rec = DESK["shapes"][s]
    tf, tl, n = M.share_axis(rec, AB, C1, "fp32")
    T = T8(f"{s}.fp32")
    x1, _ = M.far_x(rec, 1.0)
    c2[s] = {"arm": rec["arm"], "MB_NB_KB": rec["blocks"], "x_w1": round(x1, 2), "share": round(M.share_of(T, rec, AB, C1, "fp32"), 3),
             "T800": round(T, 4), "T_allF": round(tf, 4), "T_allL3": round(tl, 4), "over_allF": round(T / tf - 1, 4)}
    print(f"  {s:5s} {rec['arm']:11s} MB {rec['blocks'][0]} row block(s), NB {rec['blocks'][1]}, KB {rec['blocks'][2]}; far B at {x1:.1f} MB; share {c2[s]['share']:+.3f}; "
          f"T800 {T:.4f} us against MAB's all-fresh {tf:.4f} and all-L3 {tl:.4f} ({pc(T / tf - 1)} over all-fresh)")
nb = {}
for a, b in (("K6n4", "K6n3"), ("K6n4", "K6n5"), ("K4n8", "K4n7")):
    nb[f"{a}/{b}"] = round(T8(f"{a}.fp32") / T8(f"{b}.fp32") - 1, 4)
print("  against the neighbour with one column block fewer or more: " + "; ".join(f"{k} {pc(v)}" for k, v in nb.items()))
others = sorted((r["rung"], r["NB"], r["KB"], r["x_w1"]) for r in PH["shares"] if r["rung"].startswith("K") and r["x_w1"] >= 38 and r["KB"] >= 4)
print("  every MB = 1 rung past 38 MB with KB >= 4: " + ", ".join(f"{s} (NB {n}, KB {k}, {x:.0f} MB)" for s, n, k, x in others)
      + ": NB 4 and NB 8 appear only in K6n4 and K4n8, so the stride reading rests on these two single-row-block rungs, and of the multi-row-block")
print("  shapes with the same (NB, KB), D4 (four row blocks, K4n8's layout) also runs slower than all-fresh while F6 (three row blocks, K6n4's layout) keeps 0.33")
OUT["C2"] = {"shapes": c2, "neighbours": nb, "plateau_kb4_rungs": others}

# C3
print("\nC3 POST HOC: the zeros' energy per op step, three ways (fp32 cells; burst p800 x T800, the cells and the split posthoc.txt §5 uses)")
sm = [json.loads(x) for x in open(os.path.join(HERE, "aifoundry2", "smoke", "runs.jsonl"))]
rest = next(r for r in sm if r["label"] == "rest")
p = os.path.join(HERE, "aifoundry2", "smoke", rest["tel"])
op = gzip.open if os.path.exists(p + ".gz") else open
tel = []
with op(p + ".gz" if os.path.exists(p + ".gz") else p, "rt") as f:
    for ln in f:
        if ln.startswith("{"):
            d = json.loads(ln)
            tel.append((d.get("t_ms"), d.get("board_w")))
t1 = tel[-1][0]
last = [x for x in tel if x[0] >= t1 - 30000 and x[1] is not None]
IDLE = sum(x[1] for x in last) / len(last)
B800 = P["relation"]["B"]["800"]
pts = [(s, T, pw) for s, T, pw, _ in PH["power"]["points"]]
held = [x for x in pts if x[1] < 1.40]
slow = [x for x in pts if x[1] > 2.05]


def mean(xs):
    return sum(xs) / len(xs)


c3 = {"idle_rest_w": round(IDLE, 2), "B800_w": round(B800, 2), "held": [x[0] for x in held], "slowest": [x[0] for x in slow]}
for name, base in (("whole board (base included)", 0.0), (f"over the idle rest ({IDLE:.2f} W, the smoke's last 30 s)", IDLE),
                   (f"over E119's 800 MHz base B(800) = {B800:.2f} W", B800)):
    h = mean([(pw - base) * T for _, T, pw in held])
    sl = mean([(pw - base) * T for _, T, pw in slow])
    c3[name.split(" (")[0]] = {"held_uJ": round(h, 3), "slowest_uJ": round(sl, 3), "change": round(sl / h - 1, 4)}
    print(f"  {name}: held ({len(held)} cells, T800 < 1.40 us) {h:.3f} uJ, slowest ({', '.join(x[0] for x in slow)}, T800 > 2.05 us) {sl:.3f} uJ: {sl / h - 1:+.1%}")
print(f"  the board's p800: held {min(x[2] for x in held):.2f}-{max(x[2] for x in held):.2f} W, slowest {min(x[2] for x in slow):.2f}-{max(x[2] for x in slow):.2f} W: "
      "the slower shapes draw a little less, so the energy over the base falls while the whole board's rises")
OUT["C3"] = c3

# C4
print("\nC4 POST HOC: C's occupancy off the two collapses, by R2's registered logic, and the plateau's KB confound")
rs20 = [r for r in rungs22 if r[0] not in ("K6n4", "K4n8")]
f20 = M.fit_iso(rs20, DESK)
lg20 = M.fit_logi(rs20, DESK)
print(f"  ISO (the registered scorer) on the 20 rungs off K6n4 and K4n8: w {f20['w']}, tied {f20['w_tied']}, near-best {f20['w_near']}, rms {f20['rms_share']:.4f} "
      f"(R2's bar 0.06); rms at w = 0 {f20['rms_by_w']['0.0']:.3f}, at w = 1 {f20['rms_by_w']['1.0']:.3f} -> by R2's words: {r2_logic(f20)}")
print(f"  LOGI on the same 20: x50 {lg20['x50_mb']} MB, s {lg20['s_mb']} MB, w {lg20['w']}, rms {lg20['rms_share']:.3f}")
print(f"  the registered R2 on all 22: {V['R2']['verdict']} (rms {iso['rms_share']:.3f}, near-best {iso['w_near']}); by R2's words on the 22: {r2_logic(iso)}")
plat = [dict(r) for r in PH["shares"] if r["rung"] in PH["structure"]["plateau_rungs"]]
for r in plat:                                   # C's share of the distance from the desk itself (posthoc.json's is rounded to 0.001)
    x1, _ = M.far_x(DESK["shapes"][r["rung"]], 1.0)
    x0, _ = M.far_x(DESK["shapes"][r["rung"]], 0.0)
    r["C_share"] = (x1 - x0) / x1
for r in sorted(plat, key=lambda r: (r["KB"], r["x_w1"])):
    print(f"    plateau {r['rung']:6s} KB {r['KB']} NB {r['NB']:2d} {r['x_w1']:5.1f} MB, C {100 * r['C_share']:.0f}% of the distance, share {r['share']:+.3f}")
k2 = [r for r in plat if r["KB"] == 2]
k46 = [r for r in plat if r["KB"] in (4, 6)]
print(f"  the plateau by KB: KB 2 ({len(k2)} rungs, C {min(100 * r['C_share'] for r in k2):.0f}-{max(100 * r['C_share'] for r in k2):.0f}%) mean {mean([r['share'] for r in k2]):.3f}; "
      f"KB 4-6 ({len(k46)} rungs, C {min(100 * r['C_share'] for r in k46):.0f}-{max(100 * r['C_share'] for r in k46):.0f}%) mean {mean([r['share'] for r in k46]):.3f}: "
      "every C-heavy rung is KB 2 and no other is, so C's share and KB are confounded by design (the family sets both)")
OUT["C4"] = {"iso20": {k: f20[k] for k in ("w", "w_tied", "w_near", "rms_share")}, "iso20_rms_by_w": f20["rms_by_w"], "iso20_r2_words": r2_logic(f20),
             "logi20": lg20, "plateau_kb2_mean": round(mean([r["share"] for r in k2]), 3), "plateau_kb46_mean": round(mean([r["share"] for r in k46]), 3)}

# C5
print("\nC5 POST HOC: the counts")
sess = json.load(open(os.path.join(HERE, "aifoundry2", "s1", "session.json")))
labs = sess["runs_planned"]
lad = set(P["ladder"])
cnt = {"ladder fp32": 0, "E146's F6, D2, D4": 0, "the K4 rungs' fp16 and int8": 0, "other": 0}
for lab in labs:
    parts = lab.split("-")
    s, t = parts[2], parts[3]
    if s in lad and t == "fp32":
        cnt["ladder fp32"] += 1
    elif s in ("F6", "D2", "D4"):
        cnt["E146's F6, D2, D4"] += 1
    elif s in lad and s.startswith("K4") and t in ("fp16", "int8"):
        cnt["the K4 rungs' fp16 and int8"] += 1
    else:
        cnt["other"] += 1
noshare = [s for s in P["ladder"] if s not in SH]
print(f"  ladder rungs run: {len(P['ladder'])} ({len(SH)} with far B lines and a share; {', '.join(noshare)} has none)")
print(f"  the {len(labs)} bursts (session.json runs_planned; RES runs {RES['runs']}): " + ", ".join(f"{k} {v}" for k, v in cnt.items()))
OUT["C5"] = {"rungs_run": len(P["ladder"]), "rungs_with_share": len(SH), "no_share": noshare, "bursts": cnt, "n": len(labs)}

json.dump(OUT, open(os.path.join(HERE, "corrections.json"), "w"), indent=1)
