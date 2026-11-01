#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""E102's corrections after verification: every number the README's corrections state, recomputed from committed files and corrections-counts.json (corrections-counts.py). No card, no reduction re-run, no frozen or data file changed; post hoc throughout.
Run from anywhere; prints what corrections-check.txt holds."""
import csv
import json
import math
import os
import re
import struct
import subprocess

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
K = os.path.join(ROOT, "tools", "claims-v3", "kinds")
DD = os.path.join(ROOT, "docs", "reports", "data")
E92 = os.path.join(DD, "2026-11-01-e92-sign-split")
E79 = os.path.join(DD, "2026-10-31-e79-fp16-int8-bit-prices")
E88 = os.path.join(DD, "2026-10-31-e88-result-path")
C = json.load(open(os.path.join(HERE, "corrections-counts.json")))
S = json.load(open(os.path.join(HERE, "scored.json")))
P = S["primary"]
FIVE = ["fp16.h_sub", "fp16.c_alt", "fp16.hh_sub", "fp16.hl_sub", "fp16.s_abs"]
FLOPS = ("live", "bus", "prod", "res", "flops")
ALT = ("live", "bus", "prod", "res", "alt")
T95 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571}
OPS = json.load(open(os.path.join(E92, "posthoc-fit.json")))["ops_per_s"]
fj = lambda w: w / OPS * 1e15
wstr = lambda w: f"0x{w:08x}"


def ci(x):
    x = np.array(x, float)
    return float(x.mean()), float(T95[len(x) - 1] * x.std(ddof=1) / math.sqrt(len(x))), len(x)


def fit(rows, feats):
    X = np.array([[r[f] for f in feats] for r in rows], float)
    y = np.array([r["D"] for r in rows], float)
    c, *_ = np.linalg.lstsq(X, y, rcond=None)
    return c, float(np.sqrt(np.mean((y - X @ c) ** 2)))


def rows_of(arm):
    return {n: dict(v, D=C["fit_D"][n]["D"], name=n) for n, v in C["fit"][arm].items()}


def e86_of(arm):
    return [dict(v, D=C["e86_D"][n], name=n) for n, v in C["e86"][arm].items()]


def rms(x):
    return float(np.sqrt(np.mean(np.square(x))))


def err(rows, feats, c):
    return np.array([r["D"] - float(np.dot([r[f] for f in feats], c)) for r in rows])


def prices(feats, c):
    return ", ".join(f"{f} {fj(x):.1f}" for f, x in zip(feats[1:], c[1:]))


def measured(path, plus, minus):
    d = json.load(open(path))["per_pass"]
    vals = []
    for p, items in sorted(d.items()):
        if all(f"fp16.{t}" in items and items[f"fp16.{t}"].get("D") is not None for t in plus + minus):
            vals.append(sum(items[f"fp16.{t}"]["D"] for t in plus) - sum(items[f"fp16.{t}"]["D"] for t in minus))
    return ci(vals)


print("E102, corrections after verification (Sun 1 Nov 2026, week 44). Post hoc. C was read back on no card.\n")

# ---------------------------------------------------------------- C1
print("[C1] The refit is not evidence for the walk. The real test: prices fitted on the other 29 fp16 tiles, nothing fitted on the five.")
for s in ("4", "16"):
    st, re_ = rows_of("start" + s), rows_of("real" + s)
    print(f"  {s} op indices, make_e92's launch, 'four prices + flops':")
    for lab, rr, h in (("all 34, start's counts", list(st.values()), e86_of("start" + s)), ("all 34, real sums", list(re_.values()), e86_of("real" + s)),
                       ("29 without the five, start's counts", [v for k, v in st.items() if k not in FIVE], e86_of("start" + s)), ("29 without the five, real sums", [v for k, v in re_.items() if k not in FIVE], e86_of("real" + s))):
        c, r = fit(rr, FLOPS)
        print(f"    {lab:38s} fit rms {r:.3f} W; {prices(FLOPS, c)}; E86 held out {rms(err(h, FLOPS, c)):.3f} W")
    c, r = fit([v for k, v in st.items() if k not in FIVE], FLOPS)
    arms = [("the start", st), ("real sums", re_)] + ([("real sums, RTL arithmetic in the counted ops", rows_of("rtl16"))] if s == "16" else [])
    print("    the five, measured D minus prediction, at the prices fitted on the 29 from the start's counts:")
    for lab, src in arms:
        e = err([src[n] for n in FIVE], FLOPS, c)
        print(f"      from {lab:46s} " + ", ".join(f"{n.split('.')[1]} {x:+.2f}" for n, x in zip(FIVE, e)) + f"; rms {rms(e):.2f} W")
    ex = err([st[n] for n in FIVE], FLOPS, c)
    pred = np.array([(np.array([re_[n][f] for f in FLOPS], float) - np.array([st[n][f] for f in FLOPS], float)) @ c for n in FIVE])
    print("      excess over the start: " + ", ".join(f"{x:.2f}" for x in ex) + "; predicted from the walk's bits: " + ", ".join(f"{x:.2f}" for x in pred) + f"; best scale on the walk {float(ex @ pred / (pred @ pred)):.2f}")
    if s == "16":
        rt = rows_of("rtl16")
        pr2 = np.array([(np.array([rt[n][f] for f in FLOPS], float) - np.array([st[n][f] for f in FLOPS], float)) @ c for n in FIVE])
        print("      and with the RTL's arithmetic in the counted ops: predicted " + ", ".join(f"{x:.2f}" for x in pr2) + f"; best scale {float(ex @ pr2 / (pr2 @ pr2)):.2f}")
    print(f"      s_abs's excess over h_sub's {ex[4] / ex[0]:.2f} (its walk's predicted share {pred[4] / pred[0]:.2f}); hh_sub {ex[2] / ex[0]:.2f}, hl_sub {ex[3] / ex[0]:.2f} of h_sub's")
    print("      alternations, per op, from the start: " + ", ".join(f"{n.split('.')[1]} {st[n]['alt']:.0f}" for n in FIVE))
    for lab, feats in (("alternations in place of flops", ALT), ("four prices, no fifth", ("live", "bus", "prod", "res"))):
        ca, ra = fit([v for k, v in st.items() if k not in FIVE], feats)
        e1, e2 = err([st[n] for n in FIVE], feats, ca), err([re_[n] for n in FIVE], feats, ca)
        print(f"      {lab}: fit on 29 rms {ra:.3f} W ({prices(feats, ca)}); five from the start rms {rms(e1):.2f} W, from real sums rms {rms(e2):.2f} W")
bp = json.load(open(os.path.join(E92, "bench-prediction-de545f0c.json")))["variants"]["nets_hier2"]["tiles_D_over_zeros_w"]
b = lambda t: bp["fp16." + t]
pri, dip = os.path.join(E92, "e92.json"), os.path.join(E92, "dips-arm", "e92-nodips.json")
print("\n  The RTL bench's frozen prediction, nets_hier2 at de545f0c, against E92's measured (primary; dips removed):")
for lab, val, plus, minus in (("h_sub - h_add", b("h_sub") - b("h_add"), ("h_sub",), ("h_add",)), ("c_alt - c_abs", b("c_alt") - b("c_abs"), ("c_alt",), ("c_abs",)),
                              ("hh + hl - both", b("hh_sub") + b("hl_sub") - b("h_sub") - b("c_abs"), ("hh_sub", "hl_sub"), ("h_sub", "c_abs"))):
    m1, c1, n1 = measured(pri, plus, minus)
    m2, c2, n2 = measured(dip, plus, minus)
    print(f"    {lab:16s} bench {val:+.2f} W; measured {m1:+.3f} +- {c1:.3f} ({n1} passes); {m2:+.3f} +- {c2:.3f} ({n2})")
for t in ("hh_sub", "hl_sub"):
    m1 = measured(pri, (t,), ("c_abs",))[0] / measured(pri, ("h_sub",), ("c_abs",))[0]
    m2 = measured(dip, (t,), ("c_abs",))[0] / measured(dip, ("h_sub",), ("c_abs",))[0]
    print(f"    {t} over c_abs, as a share of h_sub's: bench {(b(t) - b('c_abs')) / (b('h_sub') - b('c_abs')):.3f}; measured {m1:.2f}; {m2:.2f}")
git = lambda *a: subprocess.run(["git", "-C", ROOT] + list(a), capture_output=True, text=True).stdout.strip()
print("    bench commit " + git("log", "-1", "--format=%h %ci", "de545f0c") + "; E92's first data commit " + git("log", "--format=%h %ci", "--diff-filter=A", "--", "docs/reports/data/2026-11-01-e92-sign-split/e92.json"))
print("    fp16_step lines in that commit's accum.c: " + str(git("show", "de545f0c:rtl-sim/fma_toggle_v2/accum.c").count("fp16_step")))

# ---------------------------------------------------------------- C2
print("\n[C2] The mechanism for hh_sub and hl_sub. Words at C[0][0] / C[0][8], and how many distinct words in the 256:")
print("  the start = fl(n S); the manual = corrections-counts.py's own emulator of PRM 9.3.3 ('added with no intermediate rounding. The final sum is calculated using round towards zero'); the RTL = accum.c's port of the window (fp16_model.py)")
for t, o in C["words"].items():
    for n in ("2", "16", "1000"):
        f = lambda a: f"{wstr(a[0])} / {wstr(a[1])} ({a[2]})"
        print(f"  {t:9s} n {n:>4s}: start {f(o[n]['start'])}; manual {f(o[n]['manual'])}; RTL {f(o[n]['accum'])}")
print("  make_e88.emulate_launch at n = 2, which make_e92.self_check reads as proof of the freeze, rounding to nearest: " + "; ".join(f"{t} {wstr(a[0])} / {wstr(a[1])}" for t, a in C["emulate_launch_n2"].items() if t in ("h_sub", "hh_sub", "r_abs")))
RTLF = os.path.join(ROOT, "external", "core-et", "rtl", "shire", "minion", "vpu")
for f, lines in (("txfma_7s/txfma_c2.v", (309, 310)), ("txfma_7s/txfma_f4.v", (82, 85)), ("vpu_tensorfma.v", (691, 693))):
    p = os.path.join(RTLF, f)
    if os.path.exists(p):
        src = open(p, errors="replace").read().splitlines()
        for n in lines:
            print(f"  {f}:{n}: {src[n - 1].strip()[:150]}")
print("  fp16_model.py and txfma_top on one absorbed term: fault_e92_fp16_e102.txt part A.")

# ---------------------------------------------------------------- C3
print("\n[C3] Tiles the ordinary addition in the counted ops hides. Every fp16 tile of the fault's table, at make_e88's launch and 4 op indices; RTL = fp16_model.model in the two counted ops. W at E88's b + E92's f, then at the 29-tile fit's two prices.")
fault = open(os.path.join(K, "fault_fl_ns_e102.txt")).read()
tab = {}
for line in fault.splitlines():
    f = line.split()
    if len(f) >= 8 and re.match(r"fp(32|16)\.", f[0]) and re.match(r"[-+]\d", f[7]):
        tab[f[0]] = dict(res_f=float(f[1]), res_r=float(f[2]), fl_f=float(f[3]), fl_r=float(f[4]), moved=float(f[7]), who=" ".join(f[8:]))
e88 = json.load(open(os.path.join(ROOT, "tools", "claims-v3", "rpath", "e88.json")))["fit"]
b16, b32 = e88["fp16"]["coef"][3], e88["fp32"]["coef"][3]
f_w = json.load(open(os.path.join(K, "predictions-e92.json")))["models"]["f_w_per_flop_bit_per_op"]
c29, _ = fit([v for k, v in rows_of("start4").items() if k not in FIVE], FLOPS)
b29, f29 = c29[3], c29[4]
out = []
for n, r in C["table_rtl"].items():
    t = tab[n]
    w = (r["res"] - t["res_f"]) * b16 + (r["flops"] - t["fl_f"]) * f_w
    w2 = (r["res"] - t["res_f"]) * b29 + (r["flops"] - t["fl_f"]) * f29
    out.append((abs(w), n, t, r, w, w2))
for _, n, t, r, w, w2 in sorted(out, key=lambda x: -x[0]):
    if abs(w) >= 0.02 or n in ("fp16.c_abs", "fp16.h_add", "fp16.r_cancel"):
        print(f"  {n:24s} res start {t['res_f']:7.0f}, real {t['res_r']:7.0f}, RTL {r['res']:7.0f}; flops {t['fl_f']:7.0f}, {t['fl_r']:7.0f}, {r['flops']:7.0f}; moved {w:+.2f} W, {w2:+.2f} W; {t['who']}")
rest = sorted((abs(x[4]), x[1]) for x in out if x[1] not in FIVE + ["fp16.r_abs", "fp16.h_allsub"])
print(f"  the other {len(rest)} fp16 tiles: largest {rest[-1][1]} {rest[-1][0]:.2f} W, then {rest[-2][1]} {rest[-2][0]:.2f} W, {rest[-3][1]} {rest[-3][0]:.2f} W")
print(f"  fp32's {sum(1 for n in tab if n.startswith('fp32.'))} tiles keep the table's 'moved': largest besides pm_pi: " + ", ".join(f"{n} {tab[n]['moved']:+.2f}" for n in sorted((n for n in tab if n.startswith('fp32.') and n != 'fp32.pm_pi'), key=lambda n: -abs(tab[n]['moved']))[:2]))
ra, rc = C["table_rtl"]["fp16.r_abs"], C["table_rtl"]["fp16.r_cancel"]
print(f"  E88's arm: r_abs res {ra['res']:.0f} (ordinary 612, E88's count {tab['fp16.r_abs']['res_f']:.0f}), r_cancel {rc['res']:.0f}. At 30 and {e88['fp16']['b_fj_per_result_bit']:.2f} fJ: {(ra['res'] - rc['res']) * 30e-15 * OPS:.2f} and {(ra['res'] - rc['res']) * e88['fp16']['b_fj_per_result_bit'] * 1e-15 * OPS:.2f} W.")
readme88 = open(os.path.join(E88, "README.md")).read()
for key in ("A16", "R16abs"):
    m = re.search(rf"\| {key} \| [^|]*\| ([\d.]+ ± [\d.]+) \| ([\d.]+) ", readme88)
    print(f"    E88 README {key}: measured {m.group(1)}; model {m.group(2)}")
print(f"    R16abs's model, r_walk - r_abs, with r_abs's walk counted at E88's price: {7.23 - (ra['res'] - tab['fp16.r_abs']['res_f']) * b16:.2f} W")
print("  words at n = 541,999: " + "; ".join(f"{t} {wstr(a[0])} / {wstr(a[1])} ({a[2]})" for t, a in C["late_541999"].items() if t in ("h_sub", "r_abs", "h_allsub")))

# ---------------------------------------------------------------- C4
print("\n[C4] 'Up to 5.5 W' is one price.")
hs = tab["fp16.h_sub"]
dr, dfl = hs["res_r"] - hs["res_f"], hs["fl_r"] - hs["fl_f"]
print(f"  h_sub, make_e88's launch, 4 indices: {dr:,.0f} result bits x E88's {e88['fp16']['b_fj_per_result_bit']:.2f} fJ = {dr * b16:.2f} W, + {dfl:,.0f} flop bits x E92's {fj(f_w):.2f} fJ = {dfl * f_w:.2f} W; sum {dr * b16 + dfl * f_w:.2f} W at {OPS:.4g} ops/s. E88's fit has no flop term, so its bit price carries what flops carry.")
print(f"  the same counts at the 29-tile fit's two prices, {fj(b29):.1f} and {fj(f29):.1f} fJ: {dr * b29 + dfl * f29:.2f} W. At fp32's 30.0 and 6.68 fJ: {(dr * 30 + dfl * 6.68) * 1e-15 * OPS:.2f} W.")
for g, o in C["h_sub_by_index"].items():
    v = list(o.values())
    print(f"  h_sub's real count, ordinary counted ops, launch/indices {g}: mean {np.mean(v):,.0f}, per index {min(v):,.0f} to {max(v):,.0f}")
print(f"  h_sub with the RTL's arithmetic in the counted ops, 128 op indices over 542,000: {C['h_sub_rtl_128']:,.0f}")
ph = json.load(open(os.path.join(E92, "posthoc-fit.json")))["models"]["fp32: four prices + flops"]["prices_fj"]
for lab, line in (("fp32 B bit 6 over its zero", re.search(r"bit  6: res bits fl\s+(\d+), real\s+(\d+); flops fl\s+(\d+), real\s+(\d+)", fault)), ):
    a, c_, d, e = [float(x) for x in line.groups()]
    print(f"  {lab}: at E88's {e88['fp32']['b_fj_per_result_bit']:.2f} fJ + E92's f {(c_ - a) * b32 + (e - d) * f_w:+.2f} W; at E92's fp32 fit with both terms, {ph['res']:.1f} and {ph['flops']:.1f} fJ, {((c_ - a) * ph['res'] + (e - d) * ph['flops']) * 1e-15 * OPS:+.2f} W")
t = tab["fp32.pm_pi"]
print(f"  fp32.pm_pi: {t['moved']:+.2f} W; at that fit's prices {((t['res_r'] - t['res_f']) * ph['res'] + (t['fl_r'] - t['fl_f']) * ph['flops']) * 1e-15 * OPS:+.2f} W")

# ---------------------------------------------------------------- C5, C8, C9
pr = P["prices"]
TILES = json.load(open(os.path.join(K, "e102", "e102.json")))["tiles"]


def where(name):
    k = [x for x in pr if x.startswith(name + "@")]
    return k


def board(name):
    ks = where(name)
    out_ = {}
    for k in ks:
        out_[k.split("@")[1]] = pr[k]["board"]["fJ"]["mean"]
    return out_


print("\n[C5] Balanced mantissa flips, board fJ, by block:")
for side, tag in (("B", "bp"), ("A", "ap")):
    print(f"  {side}: " + "; ".join(f"bit {j} " + ", ".join(f"{b_} {v:.0f}" for b_, v in sorted(board(f'fp32.{tag}_{j}').items())) for j in (0, 6, 11, 16, 20, 22)))

print("\n[C8] Final ratios per bit, all-in over balanced (scored.json's rule cells; README result 1), and the bench's frozen ratio:")
R1 = P["rules"]["E102-R1"]
print("  R1's cells at bits 0, 6, 22, rail: " + ", ".join(f"{j} {R1['rail_arm']['cells'][j]['ratio']:.2f}" for j in R1["rail_arm"]["cells"]) + "; board: " + ", ".join(f"{j} {R1['board_arm']['cells'][j]['ratio']:.2f}" for j in R1["board_arm"]["cells"]))
rd = open(os.path.join(HERE, "README.md")).read()
for j in (16, 22):
    m = re.search(rf"^\| {j} \| mant \|.*$", rd, re.M)
    cells = [x.strip() for x in m.group(0).strip("|").split("|")]
    print(f"  bit {j}: B board {cells[4]}, rail {cells[5]}, bench {cells[6]}; A board {cells[9]}, rail {cells[10]}, bench {cells[11]}")

print("\n[C9] Balanced over all-in at the exponent and sign, board fJ, from README result 1 (the replacement paragraph's 'by 2-5x' reads 2-6x with A's sign):")
for j in (23, 27, 30, 31):
    m = re.search(rf"^\| {j} \| (exp|sign) \|.*$", rd, re.M)
    cells = [x.strip() for x in m.group(0).strip("|").split("|")]
    n = lambda s: float(s.split("[")[0].replace(",", "").split(";")[0])
    print(f"  bit {j}: B {n(cells[3]) / n(cells[2]):.1f}x, A {n(cells[8]) / n(cells[7]):.1f}x")

# ---------------------------------------------------------------- C6, C7
print("\n[C6] int8: the registered masks and the post-hoc singles.")
r9 = P["rules"]["E102-R9"]
for arm in ("rail_arm", "board_arm"):
    x = r9[arm]
    print(f"  bk_2a over bk_15, {arm[:-4]}: {x['difference_w']['mean']:+.3f} [{x['difference_w']['lo']:.3f}, {x['difference_w']['hi']:.3f}] W, ratio {x['ratio']['ratio']:.2f} [{x['ratio']['lo']:.2f}, {x['ratio']['hi']:.2f}] (registered): verdict {x['verdict']}")
w = struct.unpack("<512I", open(os.path.join(K, "e102", "tiles", "int8", "hq.bin"), "rb").read())
print(f"  every int8 tile: A word {wstr(w[0])} in all {256 if len(set(w[:256])) == 1 else 'NOT ALL'} A words (A = 1); B base bytes by column mod 8: " + " ".join(f"{x & 0xFF:02x}" for x in w[256:264]))
allb = {f: struct.unpack("<512I", open(os.path.join(K, "e102", "tiles", "int8", f), "rb").read())[0] for f in os.listdir(os.path.join(K, "e102", "tiles", "int8"))}
print(f"  A word across {len(allb)} int8 tile files: " + ", ".join(sorted({wstr(v) for k, v in allb.items() if k not in ('zeros.bin',)})))


def book(rows, passes, zero, items, val, k=0.0, crb=1.0, t="t0_ms", seg=True):
    o = {}
    for pp in passes:
        rr = [r for r in rows if r["pass"] == pp and int(float(r.get("fail") or 0)) == 0 and (not seg or r.get("segment") not in ("-1", "-1.0"))]

        def v(r):
            x = float(r[val])
            return x - crb * k * (float(r["t_win"]) - float(r["start_c"])) if k else x
        z = sorted((float(r[t]), v(r)) for r in rr if r["item"] == zero)
        for it in items:
            xs = [v(r) - float(np.interp(float(r[t]), [a for a, _ in z], [b_ for _, b_ in z])) for r in rr if r["item"] == it]
            if xs:
                o.setdefault(it, {})[pp] = sum(xs) / len(xs)
    return o


rows = list(csv.DictReader(open(os.path.join(HERE, "runs.csv"))))
PI = ["10230", "10231", "10232", "10233", "10234"]
names = [f"int8.bk_{j}" for j in range(8)]
print("\n[C7] 'No verdict moves at any registered arm' is hollow for a rail-primary rule: rail_raw carries no temperature term in any arm.")
print("  scored.json, R9 on the rail by arm: " + ", ".join(f"{a}: {v['rules']['E102-R9']['rail_arm']['difference_w']['mean']:+.3f}" for a, v in S["arms"].items()))
print("  E102's I blocks, recomputed here, rail_raw less 0.81 k x the run's reading (reduce_e78.py's --c-rb, E79's rail change per board change); board p_raw less k x the same:")
print("  arm                  bk_2a - bk_15 [95%]       odd 1,3,5 - even 0,2,4 [95%]   odd/even")
for lab, val, k, crb in (("rail, no term", "rail_raw", 0, 1), ("rail, k 0.1994", "rail_raw", .1994, .81), ("rail, k 0.2414", "rail_raw", .2414, .81), ("rail, k 0.3803", "rail_raw", .3803, .81), ("rail, k 0.545", "rail_raw", .545, .81),
                         ("board, no term", "p_raw", 0, 1), ("board, k 0.2414", "p_raw", .2414, 1), ("board, k 0.3803", "p_raw", .3803, 1), ("board, k 0.545", "p_raw", .545, 1)):
    bk = book(rows, PI, "int8.hq", names + ["int8.bk_15", "int8.bk_2a"], val, k, crb)
    a = ci([bk["int8.bk_2a"][p] - bk["int8.bk_15"][p] for p in PI])
    o = [np.mean([bk[f"int8.bk_{j}"][p] for j in (1, 3, 5)]) for p in PI]
    e = [np.mean([bk[f"int8.bk_{j}"][p] for j in (0, 2, 4)]) for p in PI]
    d = ci(np.array(o) - np.array(e))
    print(f"  {lab:18s} {a[0]:+.3f} [{a[0] - a[1]:+.3f}, {a[0] + a[1]:+.3f}]     {d[0]:+.3f} [{d[0] - d[1]:+.3f}, {d[0] + d[1]:+.3f}]    {np.mean(o) / np.mean(e):.2f}")
r79 = list(csv.DictReader(open(os.path.join(E79, "runs.csv"))))
P79 = ["7920", "7921", "7922", "7923"]
n79 = [f"b8k_{j}" for j in range(8)]
print("  E79 on aifoundry3, the same singles (byte-identical tiles), its list, rail column:")
for lab, val, k, crb in (("rail, no term", "rail", 0, 1), ("rail, k 0.0834", "rail", .0834, .81), ("rail, k 0.3803", "rail", .3803, .81), ("board, no term", "p_raw", 0, 1), ("board, k 0.3803", "p_raw", .3803, 1)):
    bk = book(r79, P79, "h8q", n79, val, k, crb, t="pos", seg=False)
    ks = sorted(set.intersection(*[set(bk[n]) for n in n79]))
    o = [np.mean([bk[n79[j]][p] for j in (1, 3, 5)]) for p in ks]
    e = [np.mean([bk[n79[j]][p] for j in (0, 2, 4)]) for p in ks]
    d = ci(np.array(o) - np.array(e))
    print(f"  {lab:18s} odd - even {d[0]:+.3f} [{d[0] - d[1]:+.3f}, {d[0] + d[1]:+.3f}]; odd/even {np.mean(o) / np.mean(e):.2f}; {len(ks)} passes")
print("  Is the whole-degree reading a real signal inside a list? Per read, item means removed, residual over the own zero against the reading over the zero's:")
for lab, rs, ps, zero, t, seg, vals, its in (("E102 I blocks", rows, PI, "int8.hq", "t0_ms", True, (("rail", "rail_raw"), ("board", "p_raw")), names + ["int8.bk_15", "int8.bk_2a", "int8.bk_0f", "int8.bk_f0", "int8.bk_ff", "int8.hq"]), ("E79 int8 list", r79, P79, "h8q", "pos", False, (("rail", "rail"), ("board", "p_raw")), n79 + ["h8q"])):
    for an, val in vals:
        X, Y, G = [], [], []
        for p in ps:
            rr = [r for r in rs if r["pass"] == p and int(float(r.get("fail") or 0)) == 0 and (not seg or r.get("segment") not in ("-1", "-1.0"))]
            z = sorted((float(r[t]), float(r[val])) for r in rr if r["item"] == zero)
            zt = sorted((float(r[t]), float(r["t_win"])) for r in rr if r["item"] == zero)
            for r in rr:
                if r["item"] in its:
                    x0 = float(r[t])
                    X.append(float(r["t_win"]) - float(np.interp(x0, [a for a, _ in zt], [b_ for _, b_ in zt])))
                    Y.append(float(r[val]) - float(np.interp(x0, [a for a, _ in z], [b_ for _, b_ in z])))
                    G.append(r["item"])
        X, Y, G = np.array(X), np.array(Y), np.array(G)
        for it in set(G):
            m = G == it
            X[m] -= X[m].mean()
            Y[m] -= Y[m].mean()
        beta = float((X * Y).sum() / (X * X).sum())
        res = Y - beta * X
        se = math.sqrt(float((res ** 2).sum()) / (len(X) - len(set(G)) - 1) / float((X * X).sum()))
        print(f"    {lab}, {an}: {beta:+.3f} +- {1.96 * se:.3f} W per degC over {len(X)} reads; sd of the reading {X.std():.3f} degC (a true leakage of 0.24-0.55 would read about +0.2 to +0.5)")
