"""Fits on Method B burst energies: Theil-Sen per-hop slopes, ones/transition model, complements, wsep vs wu."""
import collections
import itertools
import json
import sys

import numpy as np

from methodb import theil_sen

FN = sys.argv[1] if len(sys.argv) > 1 else "bursts_b_1.0_0.0.json"
VERBOSE = "-q" not in sys.argv
Bs = json.load(open(FN))["bursts"]
HOSTS = ("aifoundry2", "aifoundry3")
METERS = ("noc", "board", "board_tc")
F = 125.0   # pJ per byte-hop -> fJ per bit-hop
FRZ = 244 / 512


def sel(st, host, prefix, hops=None, suffix=None):
    return [b for b in Bs if b["set"] == st and b["host"] == host and b["cfg"].startswith(prefix)
            and (suffix is None or b["cfg"].endswith(suffix)) and (hops is None or b["hop"] in hops)]


def ts_slope(bs, m, per_pass=False):
    if not bs:
        return None
    s, c = theil_sen([b["hop"] for b in bs], [b["e_" + m] for b in bs])
    if not per_pass:
        return s, c
    pp = collections.defaultdict(list)
    for b in bs:
        pp[b["pass"]].append(b)
    return s, c, [theil_sen([b["hop"] for b in v], [b["e_" + m] for b in v])[0] for _, v in sorted(pp.items()) if len({b["hop"] for b in v}) >= 3]


def diff_slope(bs_a, bs_b, m):
    """Theil-Sen slope of the paired difference e(a) - e(b), matched by hop and pass."""
    ia = {(b["hop"], b["pass"]): b["e_" + m] for b in bs_a}
    ib = {(b["hop"], b["pass"]): b["e_" + m] for b in bs_b}
    ks = sorted(set(ia) & set(ib))
    s, c = theil_sen([k[0] for k in ks], [ia[k] - ib[k] for k in ks])
    pp = collections.defaultdict(list)
    for k in ks:
        pp[k[1]].append((k[0], ia[k] - ib[k]))
    per = [theil_sen([h for h, _ in v], [x for _, x in v])[0] for _, v in sorted(pp.items()) if len({h for h, _ in v}) >= 3]
    return s, c, per


R = {}
out = lambda *a: VERBOSE and print(*a)

# ------------------------------------------------------------------ C1: linearity, d = 0, the step out of the shire
out("=== C1: per-hop slopes (Theil-Sen, passes pooled), pJ/B/hop; linearity: slope d<=3 vs d>=3, rms resid")
fam = []
for p in ("0", "0.1", "0.25", "0.5", "0.75", "0.9", "1"):
    fam.append(("v1", f"wbern/p{p}/", None, (1, 2, 3, 4, 6)))
for n in (16, 32, 64, 128, 256):
    fam.append(("v1", f"walt/n{n}/", None, (1, 3, 6)))
fam.append(("v1", "wlegacy/", None, (1, 3, 6)))
for ax in ("x", "y"):
    for p in ("0", "0.5"):
        fam.append(("v1", f"waxis/{ax}/", f"/p{p}", (1, 2, 3, 4)))
for p in ("0", "0.25", "0.5", "0.75", "1"):
    fam.append(("v2", f"wu/p{p}/", None, (1, 2, 3, 4, 6)))
fam.append(("v2", "wfrz/", None, (1, 3, 6)))
for p in ("0", "0.5"):
    fam.append(("v2", f"wsep/p{p}/", None, (1, 2, 3, 4, 5)))
lin = {}
for st, pre, suf, hops in fam:
    for m in ("noc", "board"):
        row = []
        for h in HOSTS:
            bs = sel(st, h, pre, hops, suf)
            if len({b["hop"] for b in bs}) < 3:
                row.append(None); continue
            s, c = ts_slope(bs, m)
            med = {d: np.median([b["e_" + m] for b in bs if b["hop"] == d]) for d in sorted({b["hop"] for b in bs})}
            ds = sorted(med)
            lo_part = theil_sen([d for d in ds if d <= 3], [med[d] for d in ds if d <= 3])[0] if len([d for d in ds if d <= 3]) >= 2 else float("nan")
            hi_part = theil_sen([d for d in ds if d >= 3], [med[d] for d in ds if d >= 3])[0] if len([d for d in ds if d >= 3]) >= 2 else float("nan")
            resid = np.array([med[d] - (c + s * d) for d in ds])
            b0 = [b["e_" + m] for b in sel(st, h, pre, (0,), suf)]
            e0 = float(np.median(b0)) if b0 else float("nan")
            row.append({"slope": s, "icpt": c, "slope_d<=3": lo_part, "slope_d>=3": hi_part, "rms_rel": float(np.sqrt((resid ** 2).mean()) / (s * np.mean(ds))),
                        "e_d0": e0, "exit_in_hops": (c - e0) / s if b0 else float("nan"), "medians": med})
        lin[(pre + (suf or ""), m)] = row
        if row[0] or row[1]:
            out(f"{st} {pre + (suf or ''):18s} {m:5s} " + "  |  ".join(
                (f"{h[-1]}: s {r['slope']:.3f} (d<=3 {r['slope_d<=3']:.3f}, d>=3 {r['slope_d>=3']:.3f}) icpt {r['icpt']:.3f} d0 {r['e_d0']:.3f} exit {r['exit_in_hops']:.2f} hops rms {100*r['rms_rel']:.1f}%" if r else f"{h[-1]}: -")
                for h, r in zip(HOSTS, row)))
R["lin"] = {f"{k[0]}|{k[1]}": v for k, v in lin.items()}

# the NoC data-dependent part D(d) = e(P) - e(0) at d = 0 and its per-hop growth
out("\n=== C1: NoC-rail data-dependent part D(d) = e(P) - e(zeros), pJ/B, medians per d")
for st, fam5, fam0, hops in (("v1", "wbern/p0.5/", "wbern/p0/", (0, 1, 2, 3, 4, 6)), ("v1", "wbern/p1/", "wbern/p0/", (0, 1, 2, 3, 4, 6)),
                             ("v2", "wu/p0.5/", "wu/p0/", (0, 1, 2, 3, 4, 6)), ("v2", "wu/p1/", "wu/p0/", (0, 1, 2, 3, 4, 6))):
    for h in HOSTS:
        a, b_ = sel(st, h, fam5, hops), sel(st, h, fam0, hops)
        D = {d: float(np.median([x["e_noc"] for x in a if x["hop"] == d]) - np.median([x["e_noc"] for x in b_ if x["hop"] == d])) for d in hops}
        s, c, per = diff_slope([x for x in a if x["hop"] >= 1], [x for x in b_ if x["hop"] >= 1], "noc")
        R[f"D|{st}|{fam5}|{h}"] = {"D": D, "slope": s, "icpt": c}
        out(f"{st} {fam5:12s}-zeros {h}: " + " ".join(f"d{d} {v:.3f}" for d, v in D.items()) + f"   TS slope {s:.3f} icpt {c:.3f} (icpt/slope {c/s:.2f})  D(0)/slope {D[0]/s:.3f}")

# ------------------------------------------------------------------ C2: ones vs transitions
out("\n=== C2: model slope(P) = s0 + a*2P(1-P) + b*P, fJ per bit-hop")


def model(points):
    """points: list of (t, P, slope pJ/B/hop). LS; returns a, b (fJ), s0 (pJ/B/hop), rms (pJ/B/hop)."""
    A = np.array([[t, p, 1.0] for t, p, _ in points]); y = np.array([s for *_, s in points])
    c, *_ = np.linalg.lstsq(A, y, rcond=None)
    return {"a": c[0] * F, "b": c[1] * F, "s0": c[2], "rms": float(np.sqrt(((A @ c - y) ** 2).mean())),
            "rand": (0.5 * c[0] + 0.5 * c[1]) * F, "resid": (y - A @ c).tolist()}


for st, defs in (("v1", [(f"wbern/p{q}/", 2 * float(q) * (1 - float(q)), float(q), (1, 2, 3, 4, 6)) for q in ("0", "0.1", "0.25", "0.5", "0.75", "0.9", "1")]),
                 ("v2", [(f"wu/p{q}/", 2 * float(q) * (1 - float(q)), float(q), (1, 2, 3, 4, 6)) for q in ("0", "0.25", "0.5", "0.75", "1")] + [("wfrz/", 0.0, FRZ, (1, 3, 6))])):
    for m in METERS:
        per_card = {}
        for h in HOSTS:
            pts, ppts = [], collections.defaultdict(list)
            for pre, t_, p_, hp in defs:
                s, c, per = ts_slope(sel(st, h, pre, hp), m, per_pass=True)
                pts.append((t_, p_, s))
                for i, x in enumerate(per):
                    ppts[i].append((t_, p_, x))
            M = model(pts)
            Mp = [model(v) for v in ppts.values() if len(v) >= 4]
            M["per_pass_a"] = [x["a"] for x in Mp]; M["per_pass_b"] = [x["b"] for x in Mp]
            M["slopes"] = {pre: s for (pre, *_), (_, _, s) in zip(defs, pts)}
            if st == "v2":
                # fit on wu alone, predict the frozen line (ones 0.477, no transitions)
                Mw = model(pts[:-1])
                pred = (Mw["s0"] + Mw["b"] / F * FRZ)
                M["frz_pred_from_wu"] = pred; M["frz_meas"] = pts[-1][2]
                # complements
                sl = {pre: s for (pre, *_), (_, _, s) in zip(defs, pts)}
                M["comp_34_14"] = (sl["wu/p0.75/"] - sl["wu/p0.25/"]) / 0.5 * F
                M["comp_1_0"] = (sl["wu/p1/"] - sl["wu/p0/"]) * F
                M["ratio_1_to_half"] = sl["wu/p1/"] / sl["wu/p0.5/"]
                # complements from per-pass paired slope differences (hop, pass matched)
                M["comp_34_14_paired"] = diff_slope(sel(st, h, "wu/p0.75/", (1, 2, 3, 4, 6)), sel(st, h, "wu/p0.25/", (1, 2, 3, 4, 6)), m)[0] / 0.5 * F
                M["comp_1_0_paired"] = diff_slope(sel(st, h, "wu/p1/", (1, 2, 3, 4, 6)), sel(st, h, "wu/p0/", (1, 2, 3, 4, 6)), m)[0] * F
            else:
                sl = {pre: s for (pre, *_), (_, _, s) in zip(defs, pts)}
                M["ratio_1_to_half"] = sl["wbern/p1/"] / sl["wbern/p0.5/"]
                M["v1_1_minus_0"] = (sl["wbern/p1/"] - sl["wbern/p0/"]) * F
                M["v1_09_minus_01"] = (sl["wbern/p0.9/"] - sl["wbern/p0.1/"]) / 0.8 * F
            per_card[h] = M
        R[f"model|{st}|{m}"] = per_card
        mean = lambda k: np.mean([per_card[h][k] for h in HOSTS])
        out(f"{st} {m:8s}: a {mean('a'):6.1f} ({', '.join(f'{per_card[h][chr(97)]:.1f}' for h in HOSTS)})  b {mean('b'):6.1f} ({', '.join(f'{per_card[h][chr(98)]:.1f}' for h in HOSTS)})"
            f"  s0 {mean('s0'):.3f}  rand {mean('rand'):.1f}  rms {mean('rms'):.4f} pJ/B/hop  slope(1)/slope(.5) {mean('ratio_1_to_half'):.2f}"
            + (f"\n              complements 3/4-1/4 {mean('comp_34_14'):.1f} (paired {mean('comp_34_14_paired'):.1f});  1-0 {mean('comp_1_0'):.1f} (paired {mean('comp_1_0_paired'):.1f});"
               f"  frz slope meas {mean('frz_meas'):.3f} vs wu-model pred {mean('frz_pred_from_wu'):.3f}" if st == "v2" else
               f"\n              1-0 {mean('v1_1_minus_0'):.1f}   (0.9-0.1)/0.8 {mean('v1_09_minus_01'):.1f}")
            + "\n              per-pass a " + str([round(x, 0) for h in HOSTS for x in per_card[h]["per_pass_a"]]) + "  b " + str([round(x, 0) for h in HOSTS for x in per_card[h]["per_pass_b"]]))

# ------------------------------------------------------------------ C3: contention
out("\n=== C3: data-dependent (random - zeros) and zeros per-hop, fJ per bit-hop")
for m in METERS:
    for label, pre, hops in (("wsep d1-5", "wsep", (1, 2, 3, 4, 5)), ("wsep d1-4", "wsep", (1, 2, 3, 4)), ("wu d1-4", "wu", (1, 2, 3, 4)), ("wu d1-6", "wu", (1, 2, 3, 4, 6))):
        row = {}
        for h in HOSTS:
            a, z = sel("v2", h, f"{pre}/p0.5/", hops), sel("v2", h, f"{pre}/p0/", hops)
            sd, cd, perd = diff_slope(a, z, m)
            s5 = ts_slope(a, m)[0]; s0 = ts_slope(z, m)[0]
            d1 = {"data": float(np.median([b["e_" + m] for b in a if b["hop"] == 1]) - np.median([b["e_" + m] for b in z if b["hop"] == 1])),
                  "zeros": float(np.median([b["e_" + m] for b in z if b["hop"] == 1]))}
            row[h] = {"data_paired": sd * F, "data_diff_of_slopes": (s5 - s0) * F, "zeros": s0 * F, "random": s5 * F, "per_pass_data": [x * F for x in perd], "d1": d1}
        R[f"sep|{m}|{label}"] = row
        mean = lambda k: np.mean([row[h][k] for h in HOSTS])
        out(f"{m:8s} {label:10s}: data {mean('data_paired'):6.1f} (" + ", ".join(f"{row[h]['data_paired']:.1f}" for h in HOSTS) + f"; diff of slopes {mean('data_diff_of_slopes'):.1f})"
            f"  zeros {mean('zeros'):6.1f} (" + ", ".join(f"{row[h]['zeros']:.1f}" for h in HOSTS) + f")  random {mean('random'):6.1f}"
            f"   d=1: data {np.mean([row[h]['d1']['data'] for h in HOSTS]):.3f} zeros {np.mean([row[h]['d1']['zeros'] for h in HOSTS]):.3f} pJ/B"
            + "  per-pass data " + str([round(x) for h in HOSTS for x in row[h]["per_pass_data"]]))

json.dump(R, open(FN.replace("bursts_b", "summary_b"), "w"), indent=1, default=float)
