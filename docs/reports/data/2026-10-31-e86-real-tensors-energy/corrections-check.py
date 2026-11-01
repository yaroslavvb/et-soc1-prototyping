#!/usr/bin/env python3
"""E86: the desk check behind 'Corrections after verification' (Sat 31 Oct 2026). Written after an independent
verifier's report, at the desk: no card touched, nothing re-run. Every number is read from committed files; none is
a registered rule, and none changes a registered number or verdict. Standard library only.

    python3 corrections-check.py > corrections-check.txt

C1  Heat. Each real tile's 2 s die rise minus the same pass's random kind (fp32 randn, fp16 randn, int8 full),
    paired per kept pass, from e86.json per_pass; the same from runs.csv's runs; the rise the tile's lower switching
    predicts at its random kind's own degrees per watt of S (a consistency check, labelled).
C2  The baseline behind the ratios. Per kept pass, each tile's D / D(random) (D = board power over the type's own
    all-zeros level; the registered ratio), S / S(random) (S = over idle) and p80 / p80(random) (p80 = the window's
    whole board power, leakage-corrected: idle plus S); each format's three-tile mean per pass, then the mean over
    passes. Also the README's first arithmetic, (idle level + S) / (idle level + S(random)) from item means.
C3  E89 as corrected (ae24b0af): r per board W (tables.txt T1) and, post hoc, per minion-rail W (posthoc.txt
    POST HOC 2).
C4  Zeros in the real tiles: zero 32-bit words (what the zero gate sees) and zero elements (what the data is), per
    side, from real.json; the gated fraction from e86.json.
C5  A no-model baseline beside E86-R2: 'each real tile costs E78's random kind of its format' (E78's frozen D in
    predictions-e86.json e78_reference), and for int8 also 'costs E78's gauss_q'; rms against the predictor's.
C6  Facts: the passes each leakage arm set aside; the commit and push times; the claim's hold and the card time.
C7  What one tile a cell is: the window and the quantisation of each tile, from real.json.
"""
import csv
import json
import math
import os
import re
import statistics as st

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_DIR = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
E = json.load(open(os.path.join(HERE, "e86.json")))
SC = json.load(open(os.path.join(HERE, "scored.json")))
P = json.load(open(os.path.join(REPO_DIR, "tools/claims-v3/kinds/predictions-e86.json")))
REAL = json.load(open(os.path.join(REPO_DIR, "tools/claims-v3/kinds/real/real.json")))
E89 = os.path.join(REPO_DIR, "docs/reports/data/2026-10-31-e89-heat-low-power")

FMTS = ("fp32", "fp16", "int8")
NAMES = ("l0_mlp_up", "l6_mlp_down", "l6_attn_qk")
REF = {"fp32": "fp32.randn", "fp16": "fp16.randn", "int8": "int8.full"}
PASSES = [str(p) for p in E["passes"]]
# two-sided 95% Student t, by degrees of freedom
T975 = {1: 12.7062, 2: 4.3027, 3: 3.1824, 4: 2.7764, 5: 2.5706, 6: 2.4469, 7: 2.3646, 8: 2.3060, 9: 2.2622}


def mci(v):
    """mean and 95% half-width over the values (the pass as the unit)"""
    n = len(v)
    m = st.mean(v)
    h = T975[n - 1] * st.stdev(v) / math.sqrt(n) if n > 1 else float("nan")
    return m, h


def pp(p, item, key):
    return E["per_pass"][p][item][key]


def fmt_mci(v, d=3):
    m, h = mci(v)
    return f"{m:+.{d}f} +- {h:.{d}f}"


def rms(v):
    return math.sqrt(sum(x * x for x in v) / len(v))


print("E86 corrections-check (desk only; committed files only)")
print(f"kept passes {PASSES} (n = {len(PASSES)}, t(0.975, {len(PASSES) - 1}) = {T975[len(PASSES) - 1]}); "
      f"idle level {E['idle_level']['mean']:.4f} +- {E['idle_level']['ci95']:.4f} W")

# ---------------------------------------------------------------- C1
print("\n== C1 heat: 2 s die rise (dT_win, whole-degree reading) of each real tile minus the same pass's random kind")
for t in FMTS:
    ref = REF[t]
    rd = [pp(p, ref, "dT_win") for p in PASSES]
    m, h = mci(rd)
    rS = E["items"][ref]["S"]["mean"]
    rT = E["items"][ref]["dT_win"]["mean"]
    print(f"{t}: random kind {ref} dT per pass {['%.3f' % x for x in rd]} -> {m:.3f} +- {h:.3f} C; "
          f"its S {rS:.3f} W, so {rT / rS:.4f} C per W of S")
    for n in NAMES:
        it = f"{t}.real_{n}"
        d = [pp(p, it, "dT_win") - pp(p, ref, "dT_win") for p in PASSES]
        dm, dh = mci(d)
        excl = "excludes 0" if (dm - dh > 0 or dm + dh < 0) else "includes 0"
        dS = [pp(p, it, "S") - pp(p, ref, "S") for p in PASSES]
        pred = [x * rT / rS for x in dS]
        print(f"   {n:12s} dT {E['items'][it]['dT_win']['mean']:.3f} C; paired minus random per pass "
              f"{['%+.3f' % x for x in d]} -> {dm:+.3f} +- {dh:.3f} C ({excl}); S minus random "
              f"{fmt_mci(dS)} W predicts {fmt_mci(pred)} C")

# cross-check from runs.csv: the per-pass mean of each item's kept runs
rows = [r for r in csv.DictReader(open(os.path.join(HERE, "runs.csv")))
        if r["pass"] in PASSES and r["fail"] in ("0", "False", "") and r["dT_win"] not in ("", "None")]
print("runs.csv cross-check (per-pass means of each item's runs, then paired):")
for t in FMTS:
    ref = REF[t]
    out = []
    for n in NAMES:
        it = f"{t}.real_{n}"
        d = []
        for p in PASSES:
            a = [float(r["dT_win"]) for r in rows if r["pass"] == p and r["item"] == it]
            b = [float(r["dT_win"]) for r in rows if r["pass"] == p and r["item"] == ref]
            d.append(st.mean(a) - st.mean(b))
        out.append(f"{n} {fmt_mci(d)}")
    print(f"   {t}: " + "; ".join(out))

# ---------------------------------------------------------------- C2
print("\n== C2 the baseline behind the ratios (per kept pass, then the mean over passes; 95%)")
print("D = board power over the type's own all-zeros level (the registered ratio); S = over idle; "
      "p80 = the window's whole board power (leakage-corrected), i.e. idle plus S")
for t in FMTS:
    ref = REF[t]
    print(f"{t} (random kind {ref}: D {E['items'][ref]['D']['mean']:.3f} W, S {E['items'][ref]['S']['mean']:.3f} W, "
          f"p80 {E['items'][ref]['p80']['mean']:.3f} W; the type's zeros: S "
          f"{E['items'][t + '.zeros']['S']['mean']:.3f} W over idle)")
    three = {k: {p: [] for p in PASSES} for k in ("D", "S", "p80")}
    rng = {k: [] for k in ("D", "S", "p80")}
    for n in NAMES:
        it = f"{t}.real_{n}"
        cells = []
        for k in ("D", "S", "p80"):
            v = [pp(p, it, k) / pp(p, ref, k) for p in PASSES]
            for p, x in zip(PASSES, v):
                three[k][p].append(x)
            m, h = mci(v)
            rng[k].append(m)
            cells.append(f"{k} {m:.4f} +- {h:.4f}")
        print(f"   {n:12s} " + "; ".join(cells))
    for k in ("D", "S", "p80"):
        v = [st.mean(three[k][p]) for p in PASSES]
        m, h = mci(v)
        print(f"   three-tile mean, {k:3s}: {m:.4f} +- {h:.4f} (tiles {min(rng[k]):.4f}-{max(rng[k]):.4f}; "
              f"saving {100 * (1 - max(rng[k])):.1f}-{100 * (1 - min(rng[k])):.1f}%)")
    I = E["idle_level"]["mean"]
    sr = E["items"][ref]["S"]["mean"]
    arith = [(I + E["items"][f"{t}.real_{n}"]["S"]["mean"]) / (I + sr) for n in NAMES]
    print(f"   README's first arithmetic, (idle level + S) / (idle level + S(random)) from item means: "
          f"{min(arith):.5f}-{max(arith):.5f}")

# ---------------------------------------------------------------- C3
print("\n== C3 E89 as corrected (ae24b0af): heat per watt relative to fp32 random data")


def md_table(path, start_marker, col_header):
    lines = open(path).read().splitlines()
    i = next(k for k, l in enumerate(lines) if l.startswith(start_marker))
    head = None
    out = []
    for l in lines[i + 1:]:
        if not l.startswith("|"):
            if head is not None and out:
                break
            continue
        cells = [c.strip() for c in l.strip().strip("|").split("|")]
        if head is None:
            head = cells
            continue
        if set(cells[0]) <= set("-: "):
            continue
        out.append((cells[0], cells[head.index(col_header)]))
    return out


t1 = md_table(os.path.join(E89, "tables.txt"), "## T1", "r = H / H_ref [95%]")
ph2 = md_table(os.path.join(E89, "posthoc.txt"), "== POST HOC 2", "r on the minion rail [95%]")
num = lambda s: float(re.match(r"\s*([0-9.]+)", s).group(1))
t1v = [(k, num(v)) for k, v in t1 if "reference" not in k]
phv = [(k, num(v)) for k, v in ph2 if k != "f32randn"]
print(f"per board W (tables.txt T1), the {len(t1v)} kinds E89 measured: "
      + ", ".join(f"{k} {v:.3f}" for k, v in t1v)
      + f" -> {min(v for _, v in t1v):.3f}-{max(v for _, v in t1v):.3f}")
print(f"per minion-rail W, post hoc (posthoc.txt POST HOC 2): "
      + ", ".join(f"{k} {v:.3f}" for k, v in phv)
      + f" -> {min(v for _, v in phv):.3f}-{max(v for _, v in phv):.3f}")

# ---------------------------------------------------------------- C4
print("\n== C4 zeros in the real tiles (real.json tiles.<type>.<matrix>.stats; e86.json items.<item>.gated_lane_frac)")
for t in FMTS:
    for n in NAMES:
        s = REAL["tiles"][t][n]["stats"]
        g = E["items"][f"{t}.real_{n}"]["gated_lane_frac"]
        print(f"   {t} {n:12s} A zero words {s['a']['zero_word_frac']:.4f}, zero elements {s['a']['zero_elem_frac']:.4f}; "
              f"B zero words {s['b']['zero_word_frac']:.4f}, zero elements {s['b']['zero_elem_frac']:.4f}; gated {g}")
ze = [REAL["tiles"]["int8"][n]["stats"][side]["zero_elem_frac"] for n in NAMES for side in ("a", "b")]
print(f"   int8 zero elements over the six operands: {min(ze):.4f}-{max(ze):.4f}")

# ---------------------------------------------------------------- C5
print("\n== C5 a no-model baseline beside E86-R2 (labelled; not a registered rule)")
ref78 = P["e78_reference"]
for t in FMTS:
    e_pred, e_rand, e_gq = [], [], []
    for n in NAMES:
        tl = SC["tiles"][f"{t}.real_{n}"]
        D = tl["D"]["mean"]
        e_pred.append(D - tl["D_frozen_w"])
        e_rand.append(D - ref78[REF[t]]["D_w"])
        if t == "int8":
            e_gq.append(D - ref78["int8.gauss_q"]["D_w"])
    line = (f"{t}: predictor errors {['%+.3f' % x for x in e_pred]} rms {rms(e_pred):.3f} W "
            f"(scored.json R2 {SC['rules']['E86-R2']['by_type'][t]['rms_w']:.3f}); 'real = E78's {REF[t]}' "
            f"({ref78[REF[t]]['D_w']} W) errors {['%+.3f' % x for x in e_rand]} rms {rms(e_rand):.3f} W; "
            f"ratio {rms(e_rand) / rms(e_pred):.2f}")
    if e_gq:
        line += (f"; 'real = E78's int8.gauss_q' ({ref78['int8.gauss_q']['D_w']} W) errors "
                 f"{['%+.3f' % x for x in e_gq]} rms {rms(e_gq):.3f} W, ratio {rms(e_gq) / rms(e_pred):.2f}")
    print(line)

# ---------------------------------------------------------------- C6
print("\n== C6 facts")
for f in ("e86.json", "e86-leak0.1994.json", "e86-leak0.3803.json", "e86-leak0.json"):
    d = json.load(open(os.path.join(HERE, f)))
    print(f"   {f}: kept {d['passes']}; set aside " + "; ".join(
        f"{a['pass']} ({', '.join(a['why'])})" for a in d["passes_set_aside"]))
print("   times: logs/push-and-claim-times.txt")
for l in open(os.path.join(HERE, "logs", "push-and-claim-times.txt")).read().splitlines():
    print("      " + l)


def hms(s):
    h, m, x = s.split(":")
    return int(h) * 3600 + int(m) * 60 + float(x)


print(f"   claim held 20:06:48.140-20:41:29: {(hms('20:41:29') - hms('20:06:48.140')) / 60:.2f} min; "
      f"card time, first device access 20:07:09 to the closing config read 20:40:56: "
      f"{(hms('20:40:56') - hms('20:07:09')) / 60:.2f} min (registered max_card_min "
      f"{P['card_budget']['max_card_min']})")

# ---------------------------------------------------------------- C7
print("\n== C7 one tile a cell: the window and the quantisation of each tile (real.json)")
for t in FMTS:
    for n in NAMES:
        w = REAL["tiles"][t][n]["window"]
        print(f"   {t} {n:12s} rows (tokens) {w['rows']}, k {w['k']}, cols {w['cols']}")
q = REAL["tiles"]["int8"]["l0_mlp_up"]["quantisation"]
print(f"   int8 quantisation: A {q['A']['scheme']}; B {q['B']['scheme']}")
print(f"   conventions.int8: {REAL['conventions']['int8']}")
