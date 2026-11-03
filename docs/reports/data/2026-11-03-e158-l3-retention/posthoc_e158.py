#!/usr/bin/env python3
"""E158 (Q139): POST HOC readings of the committed session, labelled as such; none of them is a registered rule or changes a verdict. Standard library.

    python3 docs/reports/data/2026-11-03-e158-l3-retention/posthoc_e158.py > docs/reports/data/2026-11-03-e158-l3-retention/posthoc.txt
    (writes posthoc.json beside it)

  §1 every rung's far-B share (pooled and per pass) with its block structure (NB, KB), distance and C's share of it; E146's shapes on the same axis
  §2 the structure of the shares: the hold, the step, the plateau and the two collapses
  §3 F6 under the registered ISO and under readings no rule registered: ISO without its flat extrapolation onto F6's first-touch A lines at 77 MB; a
     plateau; F6's (NB, KB) twin K6n4; the rung nearest in distance
  §4 E146's committed ladder against every model, cell by cell (out of sample for ISO and LOGI)
  §5 the zeros' power and energy per op against time per op
  §6 cycles per op at the measured clock, per rung (T x f at the launches at or above 790 MHz)
  §7 card time, the commands' counts, the stop tests, the rest reading
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
P = json.load(open(os.path.join(ROOT, "tools/claims-v3/e158/predictions-e158.json")))
E146 = json.load(open(os.path.join(ROOT, "docs/reports/data/2026-11-02-e146-gemm-stores/results.json")))
DESK = M.load_desk()
AB, C1 = M.load_prices()
V = RES["rules"]
OUT = {}


def T8(key, src=RES):
    v = src["per_shape"].get(key) or {}
    return v.get("T800")


def pr(*a):
    print(*a)


# §1
pr("§1 POST HOC: every rung's far-B share (fp32 unless named), through MAB's frozen prices, with its structure")
pr(f"  {'rung':6s} {'arm':12s} {'NB':>2s} {'KB':>2s} {'x(w=1)':>7s} {'d_AB':>6s} {'d_C':>5s} {'C%':>4s} {'T800':>7s} {'share':>7s} {'pass1':>7s} {'pass2':>7s} {'pass3':>7s} {'fp16':>6s} {'int8':>6s}")
rows = []
for s in P["ladder"] + ["D2", "D4", "F6"]:
    rec = DESK["shapes"][s]
    x1, n = M.far_x(rec, 1.0)
    if not n:
        pr(f"  {s:6s} {rec['arm']:12s} (no far B lines: A at 19 MB, B at 12; T800 {T8(s + '.fp32'):.4f}, STRICT-C {P['laws'][s + '.fp32']['STRICT-C']['T800_us']:.4f})")
        continue
    x0, _ = M.far_x(rec, 0.0)
    T = T8(f"{s}.fp32")
    sh = M.share_of(T, rec, AB, C1, "fp32")
    pp = {ps: RES["t800_by_pass"].get(f"{ps}|{s}.fp32") for ps in (1, 2, 3)}
    shp = {ps: (None if v is None else M.share_of(v, rec, AB, C1, "fp32")) for ps, v in pp.items()}
    o = {t: (None if T8(f"{s}.{t}") is None else M.share_of(T8(f"{s}.{t}"), rec, AB, C1, t)) for t in ("fp16", "int8")}
    _, NB, KB = rec["blocks"]
    row = {"rung": s, "arm": rec["arm"], "NB": NB, "KB": KB, "MB": rec["blocks"][0], "x_w1": round(x1, 2), "d_AB": round(x0, 2), "d_C": round(x1 - x0, 2),
           "C_share": round((x1 - x0) / x1, 3), "T800": round(T, 4), "share": round(sh, 3), "per_pass": {k: (None if v is None else round(v, 3)) for k, v in shp.items()},
           "fp16": None if o["fp16"] is None else round(o["fp16"], 3), "int8": None if o["int8"] is None else round(o["int8"], 3)}
    if s in ("D2", "D4", "F6"):
        row["e146_share"] = round(M.share_of(T8(f"{s}.fp32", E146), rec, AB, C1, "fp32"), 3)
    rows.append(row)
    f = lambda v: "" if v is None else f"{v:+.3f}"  # noqa: E731
    pr(f"  {s:6s} {rec['arm']:12s} {NB:2d} {KB:2d} {x1:7.2f} {x0:6.2f} {x1 - x0:5.2f} {100 * (x1 - x0) / x1:4.0f} {T:7.4f} {sh:+7.3f} {f(shp[1]):>7s} {f(shp[2]):>7s} {f(shp[3]):>7s} {f(o['fp16']):>6s} {f(o['int8']):>6s}"
       + (f"   E146's session: {row['e146_share']:+.3f}" if "e146_share" in row else ""))
OUT["shares"] = rows
spread = max(max(v for v in r["per_pass"].values() if v is not None) - min(v for v in r["per_pass"].values() if v is not None) for r in rows)
pr(f"  the largest spread of a rung's share between its passes: {spread:.3f}")

# §2
pr("\n§2 POST HOC: the structure of the shares (fp32)")
lad = [r for r in rows if r["rung"].startswith("K")]
hold = [r for r in lad if r["x_w1"] < 32]
step = [r for r in lad if 32 <= r["x_w1"] < 38]
far = [r for r in lad if r["x_w1"] >= 38]
pr(f"  held, below 32 MB (C counted): {len(hold)} rungs, shares {min(r['share'] for r in hold):.3f} to {max(r['share'] for r in hold):.3f}")
pr(f"  the step, 32-38 MB: " + "; ".join(f"{r['rung']} {r['x_w1']:.0f} MB {r['share']:.3f}" for r in step))
plat = [r for r in far if not ((r["NB"], r["KB"]) in ((8, 4), (4, 6)))]
coll = [r for r in far if (r["NB"], r["KB"]) in ((8, 4), (4, 6))]
pm = sum(r["share"] for r in plat) / len(plat)
psd = math.sqrt(sum((r["share"] - pm) ** 2 for r in plat) / (len(plat) - 1))
pr(f"  beyond 38 MB, {len(plat)} rungs (every family): shares {min(r['share'] for r in plat):.3f} to {max(r['share'] for r in plat):.3f}, mean {pm:.3f} +- {psd:.3f} (sd), "
   f"from {min(r['x_w1'] for r in plat):.0f} to {max(r['x_w1'] for r in plat):.0f} MB: no fall with distance")
pr("  beyond 38 MB, the collapses: " + "; ".join(f"{r['rung']} ({r['arm']}, NB {r['NB']} KB {r['KB']}) {r['x_w1']:.0f} MB {r['share']:+.3f}" for r in coll))
pr("  E146's shapes with the same (NB, KB): D4 = gemmL4x8x4 (NB 8, KB 4) at 61.5 MB: here %+.3f, E146 %+.3f; F6 = gemmL3x4x6 (NB 4, KB 6) at 50.5 MB: here %+.3f, E146 %+.3f"
   % tuple(next(r[k] for r in rows if r["rung"] == s) for s, k in (("D4", "share"), ("D4", "e146_share"), ("F6", "share"), ("F6", "e146_share"))))
pr("  so: the L3 holds every far line below 32 MB; at 35-37 MB it holds 72-94%; from 39 to 59 MB it holds about half in every family, with no fall")
pr("  with distance, except in two block structures, NB 8 with KB 4 and NB 4 with KB 6 (a B panel of 4-6 blocks at a power-of-two stride of 4 or 8")
k2 = [r["share"] for r in plat if r["rung"].startswith("K2")]
ot = [r["share"] for r in plat if not r["rung"].startswith("K2")]
pr(f"  MB), where it holds 18% or less. On the plateau the C-heavy rungs (C 44-45% of the distance) hold {sum(k2) / len(k2):.3f} on average and the others (C 16-27%)")
pr(f"  {sum(ot) / len(ot):.3f}: C's share moves the plateau by {sum(ot) / len(ot) - sum(k2) / len(k2):.3f}. Retention is not a function of reuse distance at any w (R2), and the collapse is a structural reading of four shapes")
pr("  (K4n8 and K6n4 here; E146's D4, NB 8 with KB 4, and D8, NB 8 with KB 8, on which MAB's prices were solved with its far B lines fresh), not a")
pr("  tested law: no rung puts NB 4 or 8 with KB >= 4 at the plateau's distances other than these.")
OUT["structure"] = {"hold": [r["rung"] for r in hold], "step": [[r["rung"], r["x_w1"], r["share"]] for r in step], "plateau_mean": round(pm, 3), "plateau_sd": round(psd, 3),
                    "plateau_rungs": [r["rung"] for r in plat], "collapses": [[r["rung"], r["NB"], r["KB"], r["x_w1"], r["share"]] for r in coll]}

# §3
pr("\n§3 POST HOC: F6 under the registered ISO and under readings no rule registered (T800, measured - predicted, relative)")
iso = V["R2"]["iso"]
cr = M.iso_curve(iso)
w = iso["w"]
F6 = DESK["shapes"]["F6"]


def cr_cut(x, _c=cr):
    return 0.0 if x > 60.0 else _c(x)          # no L3 hits past the ladder's last rung (59 MB)


def share_const(v):
    def r(x):
        return 1.0 if x < 32.0 else v
    return r


alts = {"ISO (registered)": (cr, w), "ISO, r = 0 past the last rung (F6's first-touch A lines at 77 MB fresh)": (cr_cut, w)}
for name, v in (("a plateau, r = 0.50 past 38 MB, 1 below 32 MB", pm), ("F6's (NB, KB) twin K6n4's share", next(r["share"] for r in rows if r["rung"] == "K6n4")),
                ("the rung nearest in distance, K6n5 (51 MB)", next(r["share"] for r in rows if r["rung"] == "K6n5"))):
    alts[f"{name}: {v:.3f}"] = (share_const(v), 1.0)
f6 = {}
for name, (r, ww) in alts.items():
    e = {}
    for t in M.TYPES:
        p = M.T_model(F6, r, ww, AB, C1, t)["T800"]
        e[t] = round(T8(f"F6.{t}") / p - 1, 4)
    f6[name] = e
    pr(f"  {name:90s} fp32 {e['fp32']:+.4f}  fp16 {e['fp16']:+.4f}  int8 {e['int8']:+.4f}")
lnF = M.lines(F6, cr, w)
pr(f"  ISO's lines for F6 (an op): A from the L3 {lnF['A_L3']:.2f}, fresh {lnF['A_F']:.2f}; B from the L3 {lnF['B_L3']:.2f}, fresh {lnF['B_F']:.2f}; ISO's r at F6's far B "
   f"distances: {cr(45.0 + 0 * w):.3f} (42-48 MB), {cr(54.5):.3f} (54 MB), and at its first-touch A lines (77 MB): {cr(77.0):.3f} (flat past 58 MB)")
pr(f"  F6's measured share, through MAB: {next(r['share'] for r in rows if r['rung'] == 'F6'):.3f}; ISO's pooled values at its distances average "
   f"{(cr(45.0) + cr(54.5)) / 2:.3f}: the 3% PASS rests on ISO pooling the plateau with the two collapse rungs in F6's distance bins")
OUT["F6"] = f6

# §4
pr("\n§4 POST HOC: E146's committed ladder (its own session, 2 Nov), cell by cell, T800 measured - predicted (relative)")
models = ("STRICT-C", "PRIOR")
lg = V["R2"]["logi"]
crl = M.curve_logistic(lg["x50_mb"], lg["s_mb"])
tab = {}
for s in ("L1", "L2", "L4", "L8", "D1", "D2", "D4", "D8"):
    for t in M.TYPES:
        T = T8(f"{s}.{t}", E146)
        rec = DESK["shapes"][s]
        e = {m: T / P["laws"][f"{s}.{t}"][m]["T800_us"] - 1 for m in models}
        e["ISO"] = T / M.T_model(rec, cr, w, AB, C1, t)["T800"] - 1
        e["LOGI"] = T / M.T_model(rec, crl, lg["w"], AB, C1, t)["T800"] - 1
        tab[f"{s}.{t}"] = {k: round(v, 4) for k, v in e.items()}
    pr(f"  {s}: " + "; ".join(f"{t} " + " ".join(f"{m} {tab[f'{s}.{t}'][m]:+.3f}" for m in ("STRICT-C", "PRIOR", "ISO", "LOGI")) for t in M.TYPES))
OUT["e146_ladder"] = tab

# §5
pr("\n§5 POST HOC: the zeros' power and energy per op against time per op (fp32 cells; burst p800, the first second's median at 800 MHz)")
B800 = P["relation"]["B"]["800"]
pts = []
for lab, c in RES["cells"].items():
    s, t, _ = lab.split("-")
    if t != "fp32":
        continue
    p8 = [x for x in (c.get("burst_p800_w_runs") or []) if x is not None]
    T = T8(f"{s}.fp32")
    if not p8 or T is None:
        continue
    p = sum(p8) / len(p8)
    pts.append((s, T, p, (p - B800) * T))
n = len(pts)
mt, mp = sum(x[1] for x in pts) / n, sum(x[2] for x in pts) / n
sl = sum((x[1] - mt) * (x[2] - mp) for x in pts) / sum((x[1] - mt) ** 2 for x in pts)
res = [x[2] - (mp + sl * (x[1] - mt)) for x in pts]
se = math.sqrt(sum(r * r for r in res) / (n - 2) / sum((x[1] - mt) ** 2 for x in pts))
pr(f"  {n} fp32 cells: p800 {min(x[2] for x in pts):.2f}-{max(x[2] for x in pts):.2f} W; least squares p800 = {mp:.2f} + ({sl:+.2f} +- {se:.2f}) (T800 - {mt:.3f} us) W per us")
held = [x for x in pts if x[1] < 1.40]
slow = [x for x in pts if x[1] > 2.05]
mean = lambda xs: sum(xs) / len(xs)  # noqa: E731
pr(f"  energy per op over E119's base B(800) = {B800:.2f} W, e = (p800 - B) T800: {min(x[3] for x in pts):.2f}-{max(x[3] for x in pts):.2f} uJ an op step (every minion one op); "
   f"the held rungs (T800 < 1.40 us, {len(held)}) {mean([x[3] for x in held]):.2f}, the slowest (T800 > 2.05 us: {', '.join(x[0] for x in slow)}) {mean([x[3] for x in slow]):.2f}")
pr(f"  the whole energy per op, p800 x T800 (the base included, which zeros' power barely clears): held {mean([x[2] * x[1] for x in held]):.1f} uJ, slowest "
   f"{mean([x[2] * x[1] for x in slow]):.1f} uJ ({mean([x[2] * x[1] for x in slow]) / mean([x[2] * x[1] for x in held]) - 1:+.0%}): a zeros GEMM's energy per op follows its time per op")
OUT["power"] = {"slope_w_per_us": round(sl, 3), "slope_se": round(se, 3), "n": n, "B800": B800, "points": [[s, round(T, 4), round(p, 2), round(e, 3)] for s, T, p, e in pts]}

# §6
pr("\n§6 POST HOC: cycles per op at the measured clock (cycles_max / ops at the launches at or above 790 MHz), by pass; and the fit's C (cycles) and M (us)")
cyc = {}
for k in sorted(RES["cycles_per_op_800_by_pass"]):
    v = RES["cycles_per_op_800_by_pass"][k]
    f = (RES["per_shape"].get(k) or {}).get("fit") or {}
    cyc[k] = {"by_pass": v, "fit_C": f.get("C"), "fit_M": f.get("M"), "X": (RES["per_shape"].get(k) or {}).get("X")}
    pr(f"  {k:11s} {json.dumps(v):58s} fit C {f.get('C') or 0:6.1f} M {f.get('M') or 0:.4f}  X {cyc[k]['X'] or 0:.3f}")
OUT["cycles"] = cyc

# §7
pr("\n§7 POST HOC: card time, the commands' counts, the stop tests, the rest reading")
q = [json.loads(x) for x in open(os.path.join(HERE, "aifoundry2", "queue.jsonl"))]
t_first = next(x for x in q if x["kind"] == "before_first_launch")["snapshot"]["t_ms"]
t_end = next(x for x in q if x["kind"] == "queue_end")["t_ms"]
lines = 0
for sd in ("smoke", "stoptest-board", "stoptest-die", "s1"):
    tdir = os.path.join(HERE, "aifoundry2", sd, "tel")
    for fn in sorted(os.listdir(tdir)):
        op = gzip.open if fn.endswith(".gz") else open
        with op(os.path.join(tdir, fn), "rt") as f:
            lines += sum(1 for ln in f if ln.startswith("{"))
runs = {sd: (sum(1 for _ in open(os.path.join(HERE, "aifoundry2", sd, "runs.jsonl"))) if os.path.exists(os.path.join(HERE, "aifoundry2", sd, "runs.jsonl")) else 0)
        for sd in ("smoke", "stoptest-board", "stoptest-die", "s1")}
pr(f"  card time, the start snapshot's config read to the queue's end: {(t_end - t_first) / 60000:.2f} min; session s1 {json.load(open(os.path.join(HERE, 'aifoundry2', 's1', 'end.json')))['card_min']} min")
pr(f"  sampler lines (each GET_MODULE_POWER, GET_SP_STATS, GET_MODULE_CURRENT_TEMPERATURE, GET_ASIC_VOLTAGE, GET_MODULE_VOLTAGE, GET_ASIC_FREQUENCIES): {lines}; "
   f"runs (each followed by an ettelem config and an sptrace): {runs}")
for x in q:
    if x["kind"] in ("stoptest_detail", "stoptest_check", "smoke_check"):
        pr("  ", json.dumps(x))
sm = [json.loads(x) for x in open(os.path.join(HERE, "aifoundry2", "smoke", "runs.jsonl"))]
rest = next(r for r in sm if r["label"] == "rest")
tel = []
p = os.path.join(HERE, "aifoundry2", "smoke", rest["tel"])
op = gzip.open if os.path.exists(p + ".gz") else open
with op(p + ".gz" if os.path.exists(p + ".gz") else p, "rt") as f:
    for ln in f:
        if ln.startswith("{"):
            d = json.loads(ln)
            tel.append((d.get("t_ms"), d.get("board_w"), ((d.get("temp_c") or {}).get("minshire") or [None])[0]))
t1 = tel[-1][0]
last = [x for x in tel if x[0] >= t1 - 30000 and x[1] is not None]
pr(f"  the smoke's rest reading (its last 30 s, the idle card): board {sum(x[1] for x in last) / len(last):.2f} W, die {sum(x[2] for x in last if x[2] is not None) / len(last):.1f} C, n {len(last)}")
OUT["card"] = {"card_min": round((t_end - t_first) / 60000, 2), "sampler_lines": lines, "runs": runs}
json.dump(OUT, open(os.path.join(HERE, "posthoc.json"), "w"), indent=1)
