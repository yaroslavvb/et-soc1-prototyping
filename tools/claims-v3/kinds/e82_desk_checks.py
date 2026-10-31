#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""E82 (Q130) desk checks, run before the freeze from committed files only (no card, no E78 data):

    python3 tools/claims-v3/kinds/e82_desk_checks.py > tools/claims-v3/kinds/e82_desk_checks.txt

[1] card 1's idle leakage slope over the launch band, from E44's idle bins (the card-1 arm of the leakage
    correction; the same estimator on aifoundry3's bins must reproduce E71's measured 0.3803 W/C);
[2] the September card scale between aifoundry3 and aifoundry1's card 1 (the band of cross-card rule X2/X3);
[3] E38's card-1 operand anchors (E82-R4's targets);
[4] card 1's configuration as last read (the config gate's registered values);
[5] card 1's launch coverage in September's sparsity records (the duty gate can be met on this host);
[6] the kinds eligible for X2/X3 (frozen Q130(c) prediction >= 5.0 W);
[7] how often X1-X3 pass when the two cards differ only by one scale and measurement noise (simulation);
[8] the registered order of E82's first pass on this card;
[9] sha256 of the E78 code E82 reuses unchanged.
Nothing here is an E82 measurement.
"""
import glob
import hashlib
import json
import math
import os
import random
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import e78_common as ec  # noqa: E402

BAND = (0.88, 0.99)
ELIGIBLE_MIN_W = 5.0


def p(*a):
    print(*a)


def spearman(x, y):
    def rank(a):
        o = sorted(range(len(a)), key=lambda i: a[i])
        r = [0.0] * len(a)
        i = 0
        while i < len(o):
            j = i
            while j + 1 < len(o) and a[o[j + 1]] == a[o[i]]:
                j += 1
            for q in range(i, j + 1):
                r[o[q]] = (i + j) / 2.0 + 1
            i = j + 1
        return r
    rx, ry = rank(list(x)), rank(list(y))
    mx, my = sum(rx) / len(rx), sum(ry) / len(ry)
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    den = math.sqrt(sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry))
    return num / den if den else None


def main():
    p("# e82_desk_checks.py: committed files only, before the E82 freeze; nothing here is an E82 measurement")
    # ---- [1]
    iv = json.load(open(os.path.join(ROOT, "docs/reports/data/2026-09-28-overheating/analysis/idle_vs_temp.json")))
    p("\n[1] idle leakage slope over the launch band 58-62 C (E44's idle bins, 28 Sep, 600 MHz; unweighted least squares)")
    k = {}
    for card in ("aifoundry1-c1", "aifoundry3"):
        b = [x for x in iv[card]["bins"] if 58 <= x["T"] <= 62]
        T = np.array([x["T"] for x in b], float)
        W = np.array([x["board_w"] for x in b], float)
        k[card] = float(np.polyfit(T, W, 1)[0])
        p(f"  {card:14s} bins {[(int(t), round(w, 2)) for t, w in zip(T, W)]} -> {k[card]:.4f} W/C "
          f"(n samples {sum(x['n'] for x in b)})")
    p(f"  check: aifoundry3's E44 bins give {k['aifoundry3']:.4f} against E71's measured 0.3803 +- 0.0036 W/C "
      f"(docs/findings/05-claims.md, E71): difference {k['aifoundry3'] - 0.3803:+.4f}")
    p(f"  => E82's card-1 leakage arm: {round(k['aifoundry1-c1'], 3)} W/C (E78's arm on aifoundry3: 0.3803)")
    # ---- [2]
    cv = json.load(open(os.path.join(ROOT, "docs/reports/data/2026-09-21-horace-aifoundry2/cards-v3.json")))
    p("\n[2] the September card scale, aifoundry3 over aifoundry1's card 1 (cards-v3.json; E38, 26 Sep)")
    s = {}
    s["registered fit scale"] = cv["fit"]["aifoundry3"]["scale"] / cv["fit"]["aifoundry1-c1"]["scale"]
    s["registered ratio_to_ref"] = cv["ratio_to_ref"]["aifoundry3"] / cv["ratio_to_ref"]["aifoundry1-c1"]
    for nm in ("at_launch", "at_launch_step"):
        s[f"{nm} fit scale"] = cv[nm]["fit"]["aifoundry3"]["scale"] / cv[nm]["fit"]["aifoundry1-c1"]["scale"]
        s[f"{nm} ratio_to_ref"] = cv[nm]["ratio_to_ref"]["aifoundry3"] / cv[nm]["ratio_to_ref"]["aifoundry1-c1"]
    for kk, v in s.items():
        p(f"  {kk:28s} {v:.4f}")
    pats = {x["values"]: x["per_card"] for x in cv["patterns"]}
    z3, z1 = pats["zeros"]["aifoundry3"]["mean"], pats["zeros"]["aifoundry1-c1"]["mean"]
    rr = {}
    for nm, pc in pats.items():
        if nm == "zeros":
            continue
        rr[nm] = (pc["aifoundry3"]["mean"] - z3) / (pc["aifoundry1-c1"]["mean"] - z1)
    p("  per pattern, switching over each card's own zeros (registered values, launches at 57 C on aifoundry3 and 80 C on card 1):")
    p("   " + ", ".join(f"{nm} {v:.3f}" for nm, v in rr.items()))
    p(f"  minion mV: aifoundry3 {cv['mv']['aifoundry3']}, card 1 {cv['mv']['aifoundry1-c1']} "
      f"(V^2 alone would give {(cv['mv']['aifoundry3'] / cv['mv']['aifoundry1-c1']) ** 2:.3f}; the cards' measured scale is the other way)")
    lo, hi = min(s.values()), max(s.values())
    p(f"  range over the six readings {lo:.3f}-{hi:.3f}; per-pattern range {min(rr.values()):.3f}-{max(rr.values()):.3f}")
    p(f"  => registered band for D(aifoundry3)/D(card 1): [{BAND[0]}, {BAND[1]}]")
    # ---- [3]
    ab = json.load(open(os.path.join(ROOT, "docs/reports/data/2026-09-25-claims-v3/results/abla.json")))
    items = ab["items"] if isinstance(ab, dict) and "items" in ab else ab
    p("\n[3] E38's card-1 operand anchors (abla.json, ABL-T8 per_card.aifoundry1-c1.vs_aifoundry2_values; built-in values,"
      " 4 runs, launches near 80 C)")
    for it in items:
        if it.get("item") == "ABL-T8":
            for st in it["per_card"]["aifoundry1-c1"]["vs_aifoundry2_values"]["subtests"]:
                c = st["ci"]
                p(f"  {st['test']:24s} {c['point']:.3f} W, se {c['se']:.3f}, corrected interval [{c['lo']}, {c['hi']}]")
        if it.get("item") == "ABL-T5":
            for st in it["per_card"]["aifoundry1-c1"]["reported"]["vs_aifoundry2_values"]:
                c = st["ci"]
                p(f"  {st['test']:24s} {c['point']:.3f} pJ/MAC over idle, interval [{c['lo']}, {c['hi']}] (reported beside E82)")
    # ---- [4]
    p("\n[4] card 1's configuration as last read (claims-v3 raw, 25-26 Sep)")
    seen = set()
    for f in sorted(glob.glob(os.path.join(ROOT, "docs/reports/data/2026-09-25-claims-v3/raw/aifoundry1-c1/*/p*/config_start.json"))):
        try:
            c = json.load(open(f))
        except ValueError:
            continue
        key = (c.get("tdp_w"), c.get("temp_threshold_c"), c.get("minion_mhz"), c.get("minion_mv"), c.get("power_state_name"))
        seen.add(key)
    for key in sorted(seen, key=str):
        p(f"  tdp_w {key[0]}, temp_threshold_c {key[1]}, minion_mhz {key[2]}, minion_mv {key[3]}, {key[4]}")
    # ---- [5]
    p("\n[5] launch coverage inside a run on card 1 (claims-v3 raw abla p1-p4 runs.jsonl: consecutive launches of one run)")
    cov, gaps = [], []
    for f in sorted(glob.glob(os.path.join(ROOT, "docs/reports/data/2026-09-25-claims-v3/raw/aifoundry1-c1/abla/p*/runs.jsonl"))):
        recs = [json.loads(line) for line in open(f) if line.startswith("{")]
        run, prev = [], None
        for r in recs + [None]:
            if r is not None and prev is not None and r["launch"] == prev["launch"] + 1 and r["t_start_ms"] - prev["t_end_ms"] < 50:
                run.append(r)
            else:
                L = [x for x in run if x["launch"] >= 0]
                if len(L) >= 3:
                    span = L[-1]["t_end_ms"] - L[0]["t_start_ms"]
                    cov.append(sum(x["t_end_ms"] - x["t_start_ms"] for x in L) / span)
                    gaps += [b["t_start_ms"] - a["t_end_ms"] for a, b in zip(L, L[1:])]
                run = [r] if r is not None else []
            prev = r
    p(f"  {len(cov)} runs: busy fraction {min(cov):.4f}-{max(cov):.4f} (median {float(np.median(cov)):.4f}); "
      f"gap between launches median {float(np.median(gaps)):.0f} ms, max {max(gaps)} ms")
    p("  => the duty gate (work in the window >= 0.97 of nominal) can be met on this host")
    # ---- [6]
    pc = json.load(open(os.path.join(ROOT, "docs/reports/data/2026-10-31-q130-kinds-model/predictions.json")))
    pred = {kk.replace("/", "."): v["switching_w_600mhz_a3"] for kk, v in pc["predictions"].items()}
    alt = {kk.replace("/", "."): v.get("switching_w_alt_gating_arm") for kk, v in pc["predictions"].items()}
    elig = sorted(n for n, v in pred.items() if v >= ELIGIBLE_MIN_W)
    p(f"\n[6] kinds eligible for X2/X3 (frozen Q130(c) switching_w_600mhz_a3 >= {ELIGIBLE_MIN_W} W): {len(elig)}")
    for ty in ec.TYPES:
        e_ = [n.split('.', 1)[1] for n in elig if n.startswith(ty + ".")]
        p(f"  {ty} ({len(e_)}): {', '.join(e_)}")
    rank_sets = {ty: sorted(n for n in pred if n.startswith(ty + ".") and n != ec.ZERO[ty]) for ty in ec.TYPES}
    p("  X1's sets (every kind but the type's zeros): " + ", ".join(f"{ty} {len(v)}" for ty, v in rank_sets.items()))
    # ---- [7]
    p("\n[7] power of X1-X3 when the cards differ only by one scale s = D(aifoundry3)/D(card 1) and noise")
    p("  truth: the frozen Q130(c) predictions (or their alt gating arm) as each kind's switching on aifoundry3;")
    p("  noise per (pass, kind) value sd = a + 1% of D, a = 0.35 W fp32/fp16, 0.25 W int8 (E67's anchors, per-pass sd")
    p("  0.11-0.38 W for zeros/pi/ones); 'x2' doubles it; 'dev' adds a 2% per-kind deviation from one common scale;")
    p("  E78 6 passes, E82 n passes")
    rng = np.random.default_rng(82)

    T95 = {2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365}

    def sim(s, n82, truth, noise=1.0, dev=0.0, draws=1500, n78=6):
        """Per-pass values on each card, means and 95% intervals as reduce_e78 computes them, then the rules as
        score_e82 scores them: X1 rho >= 0.90 per type; X2a point ratio inside the band for >= 80% of the eligible
        kinds; X2b the ratio's 95% interval overlapping the band for >= 80%; X3 the median ratio inside the band."""
        res = {"X1": {ty: 0 for ty in ec.TYPES}, "X1all": 0, "X2a": 0, "X2b": 0, "X3": 0, "fa": [], "fb": []}
        for _ in range(draws):
            m78, m82, c78, c82 = {}, {}, {}, {}
            for nme, tv in truth.items():
                ty = nme.split(".", 1)[0]
                a = 0.25 if ty == "int8" else 0.35
                sd = noise * (a + 0.01 * abs(tv))
                kdev = 1 + dev * rng.standard_normal()
                x78 = tv + sd * rng.standard_normal(n78)
                x82 = tv * kdev / s + sd / s * rng.standard_normal(n82)
                m78[nme], m82[nme] = float(x78.mean()), float(x82.mean())
                c78[nme] = T95[n78 - 1] * float(x78.std(ddof=1)) / math.sqrt(n78)
                c82[nme] = T95[n82 - 1] * float(x82.std(ddof=1)) / math.sqrt(n82)
            ok_all = True
            for ty in ec.TYPES:
                ns = rank_sets[ty]
                rho = spearman([m82[x] for x in ns], [m78[x] for x in ns])
                if rho is not None and rho >= 0.90:
                    res["X1"][ty] += 1
                else:
                    ok_all = False
            res["X1all"] += ok_all
            ins_a, ins_b, rat = 0, 0, []
            for x in elig:
                if m82[x] <= 0 or m78[x] <= 0:
                    rat.append(-1.0)
                    continue
                r = m78[x] / m82[x]
                hw = r * math.sqrt((c78[x] / m78[x]) ** 2 + (c82[x] / m82[x]) ** 2)
                rat.append(r)
                ins_a += BAND[0] <= r <= BAND[1]
                ins_b += (r - hw) <= BAND[1] and (r + hw) >= BAND[0]
            fa, fb = ins_a / len(elig), ins_b / len(elig)
            res["fa"].append(fa)
            res["fb"].append(fb)
            res["X2a"] += fa >= 0.80
            res["X2b"] += fb >= 0.80
            res["X3"] += BAND[0] <= float(np.median(rat)) <= BAND[1]
        d = draws
        return (f"X1 {res['X1']['fp32'] / d:.2f}/{res['X1']['fp16'] / d:.2f}/{res['X1']['int8'] / d:.2f} "
                f"all {res['X1all'] / d:.2f} | X2a {res['X2a'] / d:.2f} (median fraction {float(np.median(res['fa'])):.2f})"
                f" | X2b {res['X2b'] / d:.2f} ({float(np.median(res['fb'])):.2f}) | X3 {res['X3'] / d:.2f}")

    tp = {n: v for n, v in pred.items() if n not in ec.ZERO.values()}
    ta = {n: (alt[n] if alt[n] is not None else v) for n, v in tp.items()}
    p("  columns: X1 fp32/fp16/int8 and all three | X2a | X2b | X3 (the probability each passes; 1,500 draws a row)")
    for label, truth in (("frozen predictions", tp), ("alt gating arm", ta)):
        for s_ in (0.85, 0.887, 0.935, 0.96, 0.985, 1.0, 1.05):
            for n82 in (4, 6):
                p(f"  {label:18s} s {s_:.3f} n {n82}: {sim(s_, n82, truth)}")
        p(f"  {label:18s} s 0.960 n 4 x2: {sim(0.96, 4, truth, noise=2.0)}")
        p(f"  {label:18s} s 0.960 n 4 dev: {sim(0.96, 4, truth, dev=0.02)}")
        p(f"  {label:18s} s 0.935 n 4 x2+dev: {sim(0.935, 4, truth, noise=2.0, dev=0.02)}")
        p(f"  {label:18s} s 0.960 n 4 dev 5%: {sim(0.96, 4, truth, dev=0.05)}")
        p(f"  {label:18s} s 1.050 n 4 x2: {sim(1.05, 4, truth, noise=2.0)}")
    # ---- [8]
    items = ec.load_items()
    o = ec.pass_order(items, "aifoundry1-c1", 8210)
    p(f"\n[8] E82's first pass (8210) on aifoundry1-c1: {len(o)} runs, random.Random('E78|aifoundry1-c1|8210'); "
      f"first ten: {[r['item'] for r in o[:10]]}")
    p("  (pass 8210 is not E78's 7810, so fp32.a_randn_b_zeros is NOT moved to the front: Q130(c)'s R9 asked that of E78)")
    # ---- [9]
    p("\n[9] the E78 code E82 runs unchanged (sha256)")
    for f in ("tools/claims-v3/lib.sh", "tools/claims-v3/kinds/e78_common.py", "tools/claims-v3/kinds/run_e78.py",
              "tools/claims-v3/kinds/block_e78.sh", "tools/claims-v3/kinds/queue_e78.sh",
              "tools/claims-v3/kinds/reduce_e78.py", "tools/claims-v3/kinds/score_e78.py",
              "tools/claims-v3/kinds/kinds.json"):
        p(f"  {hashlib.sha256(open(os.path.join(ROOT, f), 'rb').read()).hexdigest()}  {f}")


if __name__ == "__main__":
    random.seed(82)
    main()
