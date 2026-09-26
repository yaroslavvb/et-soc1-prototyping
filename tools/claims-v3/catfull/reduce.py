#!/usr/bin/env python3
"""V3-CATFULL reduction: the full energy catalogue per card, pooled over cards, and card to card.

    python3 tools/claims-v3/catfull/reduce.py --data <dir> --out verdicts.json [--catalogue-out catalogue4.json]
        [--committed docs/reports/data/2026-09-23-energy-manual/catalogue.json | none] [--cards a,b,...] [--root <tree>]

<dir>/<card>/catfull/p<KS>/ for every card directory present (the queue's DATA_ROOT/catfull collected per card:
aifoundry1-c0, aifoundry1-c1, aifoundry2, aifoundry3, or any other card id). A block is used when its block.json says
ok, offclock or partial (not a smoke, never an .attempt-* directory); its bursts are cut by analyze_catalogue.py's own
bursts_of() on the block alone and the drop rules of cflib.py apply (busy samples only on governor-free cards).
A pass K is COMPLETE when all its parts (pass.json "parts", 3) are used; per-configuration values use every kept burst
of every used block, pass-level items use complete passes only.

What it writes (verdicts.json):
  cards, passes             every card present and its blocks (status, kept, dropped, missing, idle clock)
  idle_clock                per card: the clock of the kept bursts' idle brackets (burst and sample counts), the idle
                            board power at each clock, the lead's clock, the clock read before the block (pass.json);
                            state "600" when >= 90% of kept bursts have every idle sample at 600 MHz
  configs                   per configuration: each card's mean, sd, se, n (pJ/op or pJ/B, analyze_catalogue's unit),
                            pooled over every card (pooled_all), over the cards whose idle is at 600 MHz
                            (pooled_600idle, the headline), over aifoundry2 + aifoundry3 (pooled_registered), each card's
                            ratio to aifoundry2, and the committed 23 Sep values beside (never pooled)
  ratios                    per card against aifoundry2 (median, 10-90% over configurations), every pair, and the
                            committed catalogue's cross_card (aifoundry3 / aifoundry2 0.950) beside
  items                     CF-GAP, CF-COVER, CF-REP: the amendment's rules (README), each with the REGISTERED outcome
                            (aifoundry2 and aifoundry3, as the 23 Sep catalogue) and an all_cards outcome
--catalogue-out writes the analyze_catalogue.py shape (cards/summary/wire/sram_leakage, bursts, combined, cross_card,
rail_filter), keyed by card id, for the energy-manual builder.
"""
import argparse
import json
import math
import os
import re
import sys
from collections import Counter, defaultdict

import numpy as np

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import campaign  # noqa: E402  (the campaign's cards: amendments A2 and A4)
sys.path.insert(0, HERE)
import cflib as L  # noqa: E402

USED = {"ok", "offclock", "partial"}
MIN_REPEATS = 3
IDLE600_FRAC = 0.9
T95 = {1: 12.71, 2: 4.30, 3: 3.18, 4: 2.78, 5: 2.57, 6: 2.45, 7: 2.36, 8: 2.31, 9: 2.26, 10: 2.23}   # analyze_catalogue
COMMITTED_REP = {"aifoundry2": {"median_pct": 1.9, "p90_pct": 6.1}, "aifoundry3": {"median_pct": 1.2, "p90_pct": 3.6}}
COMMITTED_GAP = {"median": 0.950, "p10": 0.906, "p90": 0.987, "n": 386}
RULES = {
    "unit": "pass (a complete pass = all its parts used); per-configuration values over kept bursts of used blocks",
    "drops": "governor-free cards (all but aifoundry3): busy samples off 600 MHz, or a launch with an implied clock "
             "outside 0.595-0.605 GHz (the first launch is not tested when the bracket before the burst is not all "
             "at 600 MHz: the wake-up from another idle state); idle brackets never tested (V3-CAT's R-clock "
             "idle-bracket rule on aifoundry2 is not applied: CF-GAP gives the registered test without those bursts "
             "as a sensitivity); every card: bursts bursts_of cannot cut, heater inside the brackets (guard)",
    "repeats": f">= {MIN_REPEATS} complete passes on a card, else INSUFFICIENT on that card",
    "registered": "aifoundry2 and aifoundry3 (the committed 23 Sep catalogue's cards)",
    "all_cards": "every expected card (--cards, default the four campaign cards) and any other card present: PASS "
                 "if the item holds on every card, CARD-DIFFERENT on some, FAIL on none, INSUFFICIENT if a card lacks "
                 "repeats (outcome_over_cards_with_repeats gives the outcome over the others); an item registered for "
                 "named cards only is REPORTED on the others",
    "idle_600": f"a card's idle is at 600 MHz when >= {int(IDLE600_FRAC * 100)}% of its kept bursts have every idle "
                "sample at 600 MHz; pooled_600idle uses only those cards",
    "interval": "99% two-sided Welch t on pass-level values",
}


def pct(v, q):
    return float(np.percentile(v, q)) if len(v) else None


def dist(v):
    v = np.array(sorted(v), float)
    return {"median": float(np.median(v)) if len(v) else None, "p10": pct(v, 10), "p90": pct(v, 90), "n": int(len(v))}


def outcome_of(holds):
    """holds: {card: True | False | None (lacks repeats)} -> PASS / CARD-DIFFERENT / FAIL / INSUFFICIENT."""
    if not holds or any(v is None for v in holds.values()):
        return "INSUFFICIENT"
    n = sum(1 for v in holds.values() if v)
    return "PASS" if n == len(holds) else ("FAIL" if n == 0 else "CARD-DIFFERENT")


def all_cards_outcome(holds, expected):
    h = {c: holds.get(c) for c in expected}
    with_rep = {c: v for c, v in h.items() if v is not None}
    return {"outcome": outcome_of(h), "cards": expected,
            "lacking_repeats": [c for c, v in h.items() if v is None],
            "holds_on": [c for c, v in h.items() if v], "fails_on": [c for c, v in h.items() if v is False],
            "outcome_over_cards_with_repeats": outcome_of(with_rep) if with_rep else "INSUFFICIENT"}


# ---------------- loading ----------------
def load_card(root, card_dir, card):
    """Every catfull block of one card: records, with kept bursts and drops for the used ones."""
    base = os.path.join(card_dir, "catfull")
    recs, curves = [], []
    if not os.path.isdir(base):
        return recs, curves
    for name in sorted(os.listdir(base)):
        m = re.fullmatch(r"p(\d+)", name)
        if not m:
            continue                      # .attempt-* and anything else: never used
        d = os.path.join(base, name)
        bj = L.load_block_json(os.path.join(d, "block.json")) or {}
        pj = L.jload(os.path.join(d, "pass.json"), {}) or {}
        ks = m.group(1)
        k = pj.get("pass") or (int(ks[0]) if len(ks) == 2 else None)
        s = pj.get("part") or (int(ks[1]) if len(ks) == 2 else None)
        gov = pj.get("gov_free", L.gov_free(card))
        rec = {"block": ks, "pass": k, "part": s, "parts": pj.get("parts", L.PARTS), "status": bj.get("status"),
               "note": bj.get("note"), "gov_free": bool(gov), "idle_mhz_start": pj.get("idle_mhz_start"),
               "heat_reached": pj.get("heat_reached"), "n_total": pj.get("n_total"),
               "used": bj.get("status") in USED and not pj.get("smoke") and k is not None and s is not None}
        if rec["used"]:
            kept, dropped, expected, info, cv = L.pass_bursts(d, gov, root)
            for b in kept:
                b["pass"], b["part"], b["block"] = k, s, ks
            rec.update({"kept": kept, "dropped": dropped, "expected": expected, "info": info})
            curves += cv
        recs.append(rec)
    return recs, curves


def idle_clock(card, used):
    kept = [b for r in used for b in r["kept"]]
    hist, wsum = Counter(), Counter()
    for r in used:
        for m, n in r["info"].get("idle_mhz_hist", {}).items():
            hist[m] += n
            wsum[m] += n * r["info"]["idle_w_by_mhz"].get(m, 0.0)
    bursts = Counter(b["idle_mhz"] for b in kept)
    frac600 = (bursts.get("600", 0) / len(kept)) if kept else None
    if frac600 is None:
        state = "none"
    elif frac600 >= IDLE600_FRAC:
        state = "600"
    else:   # under the threshold: the most common clock among the bursts whose brackets were NOT all at 600 MHz
        state = Counter({k: v for k, v in bursts.items() if k != "600"}).most_common(1)[0][0]
    out = {"state": state, "frac_bursts_idle_600": frac600, "bursts_by_idle_mhz": dict(bursts),
           "samples_by_mhz": dict(hist), "idle_w_by_mhz": {m: wsum[m] / hist[m] for m in hist if hist[m]},
           "lead_mhz": dict(Counter(r["info"].get("lead_mhz") for r in used if r["info"].get("lead_mhz"))),
           "idle_mhz_start": [r["idle_mhz_start"] for r in used],
           "busy_by_mhz": dict(Counter(b["busy_mhz"] for b in kept)),
           "first_launch_ghz_min": min((b["first_launch_ghz"] for b in kept if b.get("first_launch_ghz")), default=None),
           "first_launch_untested": sum(1 for b in kept if not b.get("first_launch_tested", True))}
    if state == "none":
        out["note"] = f"{card}: no kept bursts"
    elif state == "600":
        out["note"] = f"{card}: idle brackets at 600 MHz ({100 * frac600:.0f}% of kept bursts), as on the committed cards"
    else:
        wv = out["idle_w_by_mhz"]
        step = (f"; idle board power {', '.join(f'{m} MHz {w:.1f} W' for m, w in sorted(wv.items()))}" if wv else "")
        out["note"] = (f"{card}: idle brackets not all at 600 MHz in {100 * (1 - frac600):.0f}% of kept bursts (most "
                       f"often {state} MHz; the rule needs {100 * IDLE600_FRAC:.0f}% at 600 MHz){step}. "
                       f"Its energies over idle are over that idle state, not a 600 MHz idle: they include the step "
                       f"from it to the 600 MHz operating point, so they are reported per card and left out of "
                       f"pooled_600idle")
    return out


# ---------------- analysis ----------------
def pool(cards, by_cfg):
    """analyze_catalogue.py main's "combined" (confidence bars), over the given cards, keyed by card id."""
    out = {}
    cfgs = sorted({cfg for c in cards for cfg in by_cfg.get(c, {})})
    for cfg in cfgs:
        per_card, vals, within = {}, [], []
        for h in cards:
            bs = by_cfg.get(h, {}).get(cfg, [])
            if not bs:
                continue
            key = "pj_per_byte" if bs[0]["bytes"] else "pj_per_op"
            v = np.array([b[key] for b in bs if b.get(key) is not None], float)
            if not len(v):
                continue
            per_card[h] = {"mean": float(v.mean()), "sd": float(v.std(ddof=1)) if len(v) > 1 else 0.0,
                           "se": float(v.std(ddof=1) / math.sqrt(len(v))) if len(v) > 1 else 0.0, "n": int(len(v)),
                           "unit": "pJ/B" if key == "pj_per_byte" else "pJ/op"}
            vals += list(v)
            within += list(v - v.mean())
        if not vals:
            continue
        vals = np.array(vals)
        dfree = len(vals) - len(per_card)
        sd_within = float(np.sqrt(np.sum(np.square(within)) / dfree)) if dfree > 0 else 0.0
        out[cfg] = {"mean": float(vals.mean()), "lo": float(vals.min()), "hi": float(vals.max()), "n": int(len(vals)),
                    "cards": len(per_card), "per_card": per_card, "sd_within": sd_within,
                    "ci95_half": T95.get(dfree, 1.96) * sd_within / math.sqrt(len(vals)) if dfree > 0 else None,
                    "card_diff": (max(c["mean"] for c in per_card.values()) - min(c["mean"] for c in per_card.values()))
                                 if len(per_card) > 1 else 0.0,
                    "unit": next(iter(per_card.values()))["unit"]}
    return out


def summary_value(s):
    """analyze_catalogue.py's cross_card: pj_per_byte if present, else pj_per_op."""
    return s["pj_per_byte"] or s["pj_per_op"]


def card_ratios(summ, a, b):
    """Per configuration mean_b / mean_a, as analyze_catalogue.py's cross_card (a = its cards[0])."""
    r = {}
    for k in summ.get(a, {}):
        if k in summ.get(b, {}):
            va, vb = summary_value(summ[a][k]), summary_value(summ[b][k])
            if va and vb and va["mean"]:
                r[k] = vb["mean"] / va["mean"]
    return r


def gap_values(card, vals, complete, ref_mean):
    """CF-GAP: per complete pass, 100 x median over configurations of ln(value / aifoundry2's config mean)."""
    g = []
    for k in complete.get(card, []):
        logs = [math.log(pv[k] / ref_mean[cfg]) for cfg, pv in vals.get(card, {}).items()
                if k in pv and pv[k] is not None and pv[k] > 0 and ref_mean.get(cfg, 0) > 0]
        if logs:
            g.append(100.0 * float(np.median(logs)))
    return g


def ratio_ci(w):
    if not w:
        return None
    return {"ratio": math.exp(w["diff"] / 100), "lo": math.exp(w["lo"] / 100), "hi": math.exp(w["hi"] / 100),
            "diff_pct_log": w["diff"], "ci_pct_log": [w["lo"], w["hi"]], "df": w["df"], "p": w["p"], "n": w["n"]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--catalogue-out")
    ap.add_argument("--committed", default=None, help="the committed catalogue.json, or 'none'")
    ap.add_argument("--cards", default=",".join(campaign.CAMPAIGN), help="the cards all_cards expects")
    ap.add_argument("--root", default=os.path.abspath(os.path.join(HERE, "..", "..", "..")))
    a = ap.parse_args()
    committed_path = a.committed or os.path.join(a.root, "docs", "reports", "data", "2026-09-23-energy-manual", "catalogue.json")
    committed = None if a.committed == "none" else L.jload(committed_path)

    present = sorted(c for c in os.listdir(a.data) if os.path.isdir(os.path.join(a.data, c, "catfull")))
    expected = [c for c in a.cards.split(",") if c]
    expected += [c for c in present if c not in expected]
    blocks, curves = {}, {}
    for c in present:
        blocks[c], curves[c] = load_card(a.root, os.path.join(a.data, c), c)

    ac = L.analyzer(a.root)
    kept, by_cfg, vals, complete, summ, cards_out, passes_out, idle, catalog_n = {}, {}, {}, {}, {}, {}, {}, {}, {}
    for c in present:
        used = [r for r in blocks[c] if r["used"]]
        kept[c] = [b for r in used for b in r["kept"]]
        by_cfg[c] = defaultdict(list)
        vals[c] = defaultdict(dict)
        for b in kept[c]:
            by_cfg[c][b["cfg"]].append(b)
            vals[c][b["cfg"]][b["pass"]] = b["value"]
        parts = defaultdict(set)
        for r in used:
            parts[r["pass"]].add(r["part"])
        complete[c] = sorted(k for k, ps in parts.items()
                             if all(s in ps for s in range(1, max(r["parts"] for r in used if r["pass"] == k) + 1)))
        catalog_n[c] = {"expected": sorted({cfg for r in used for cfg in r["expected"]}),
                        "n_total": max([r["n_total"] or 0 for r in used], default=0)}
        idle[c] = idle_clock(c, used)
        passes_out[c] = [{**{k: v for k, v in r.items() if k not in ("kept", "dropped", "expected", "info")},
                          **({"kept": len(r["kept"]), "dropped": len(r["dropped"]),
                              "dropped_clock": sum(1 for x in r["dropped"] if x["kind"] == "clock"),
                              "missing": r["info"].get("missing", []),
                              "idle_mhz_hist": r["info"].get("idle_mhz_hist"), "lead_mhz": r["info"].get("lead_mhz")}
                             if r["used"] else {})} for r in blocks[c]]
        if kept[c]:
            summ[c] = ac.summarise(kept[c])
            cards_out[c] = {"summary": summ[c], "wire": {o: ac.wire_fit(summ[c], o) for o in ("zeros", "random")},
                            "sram_leakage": ac.sram_leakage(kept[c]), "idle_clock": idle[c]}

    with_data = [c for c in present if kept.get(c)]
    idle600 = [c for c in with_data if idle[c]["state"] == "600"]
    reg = [c for c in L.REGISTERED if c in with_data]
    pooled_all, pooled_600, pooled_reg = pool(with_data, by_cfg), pool(idle600, by_cfg), pool(reg, by_cfg)

    # ratios: every card against aifoundry2, every pair, and analyze_catalogue's cross_card for the committed pair
    ref = L.REFERENCE
    ratios = {"reference": ref, "per_card": {}, "pairs": {}, "committed_cross_card": None}
    per_cfg_ratio = defaultdict(dict)
    for c in with_data:
        if c == ref or ref not in summ:
            continue
        r = card_ratios(summ, ref, c)
        for k, v in r.items():
            per_cfg_ratio[k][c] = v
        ratios["per_card"][c] = {**dist(list(r.values())), "idle_state": idle[c]["state"]}
    for i, x in enumerate(with_data):
        for y in with_data[i + 1:]:
            ratios["pairs"][f"{y}/{x}"] = dist(list(card_ratios(summ, x, y).values()))
    cross_card = None
    if all(c in summ for c in L.REGISTERED):
        r = card_ratios(summ, L.REGISTERED[0], L.REGISTERED[1])
        rv = np.array(sorted(r.values()))
        cross_card = {"pair": L.REGISTERED, "ratios": r, **{k: v for k, v in dist(rv).items()}}
    if committed and "cross_card" in committed:
        cc = committed["cross_card"]
        ratios["committed_cross_card"] = {"pair": cc.get("pair"), "median": cc.get("median"), "p10": cc.get("p10"),
                                          "p90": cc.get("p90"), "n": cc.get("n")}

    # per configuration: each card, pooled, ratio to aifoundry2, committed beside
    csum = (committed or {}).get("cards", {})
    configs = {}
    for cfg in sorted(set(pooled_all) | {k for c in L.REGISTERED for k in csum.get(c, {}).get("summary", {})}):
        pa = pooled_all.get(cfg)
        configs[cfg] = {"unit": pa["unit"] if pa else None,
                        "per_card": {c: pa["per_card"][c] for c in (pa["per_card"] if pa else {})},
                        "pooled_all": {k: pa[k] for k in ("mean", "lo", "hi", "n", "cards", "sd_within", "ci95_half", "card_diff")} if pa else None,
                        "pooled_600idle": ({k: pooled_600[cfg][k] for k in ("mean", "lo", "hi", "n", "cards", "sd_within", "ci95_half", "card_diff")}
                                           if cfg in pooled_600 else None),
                        "pooled_registered": ({k: pooled_reg[cfg][k] for k in ("mean", "lo", "hi", "n", "cards", "sd_within", "ci95_half", "card_diff")}
                                              if cfg in pooled_reg else None),
                        "ratio_to_" + ref: per_cfg_ratio.get(cfg, {}),
                        "committed_23sep": {c: (summary_value(csum[c]["summary"][cfg]) or {}).get("mean")
                                            for c in L.REGISTERED if cfg in csum.get(c, {}).get("summary", {})}}
    vs_committed = {}
    for c in L.REGISTERED:
        if c in summ and c in csum:
            r = [summary_value(summ[c][k])["mean"] / summary_value(csum[c]["summary"][k])["mean"]
                 for k in summ[c] if k in csum[c]["summary"] and summary_value(summ[c][k]) and
                 summary_value(csum[c]["summary"][k]) and summary_value(csum[c]["summary"][k])["mean"]]
            vs_committed[c] = dist(r)

    # ---------------- items ----------------
    items = []
    notes_idle = {c: idle[c]["note"] for c in with_data}
    # CF-GAP: aifoundry3 cheaper than aifoundry2 across the catalogue (E27: median ratio 0.950)
    ref_mean = {cfg: float(np.mean([b["value"] for b in bs])) for cfg, bs in by_cfg.get(ref, {}).items()} if ref in kept else {}
    g = {c: gap_values(c, vals, complete, ref_mean) for c in present}
    per_card = {}
    for c in expected:
        if c not in present:
            per_card[c] = {"present": False}
            continue
        w = L.welch(g[c], g[ref]) if c != ref and ref in g else None
        per_card[c] = {"complete_passes": len(complete[c]), "g_pct_log": g[c],
                       "mean_ratio_to_" + ref: math.exp(float(np.mean(g[c])) / 100) if g[c] else None,
                       "vs_" + ref: ratio_ci(w) if len(g[c]) >= MIN_REPEATS and len(g.get(ref, [])) >= MIN_REPEATS else None,
                       "idle_state": idle[c]["state"]}
    a2n, a3n = len(g.get("aifoundry2", [])), len(g.get("aifoundry3", []))
    if a2n < MIN_REPEATS or a3n < MIN_REPEATS:
        reg_out = "INSUFFICIENT"
        reading = (f"complete passes: aifoundry2 {len(complete.get('aifoundry2', []))}, aifoundry3 "
                   f"{len(complete.get('aifoundry3', []))} (need {MIN_REPEATS} each)"
                   + ("" if ref_mean else f"; no {ref} values to refer to"))
        test = None
    else:
        test = ratio_ci(L.welch(g["aifoundry3"], g["aifoundry2"]))
        reg_out = "PASS" if test["hi"] < 1 else "FAIL"
        reading = (f"aifoundry3 / aifoundry2 = {test['ratio']:.3f} (99% {test['lo']:.3f}-{test['hi']:.3f}) over the "
                   f"pass-level medians; committed 23 Sep {COMMITTED_GAP['median']:.3f}; "
                   + ("aifoundry3 cheaper" if reg_out == "PASS" else "no gap established (interval reaches 1 or above)"))
    # sensitivity (reported, never the outcome): the same test on the bursts whose idle brackets were all at 600 MHz,
    # i.e. with V3-CAT's R-clock idle-bracket rule applied, which catfull's drop rules do not apply
    vals600 = {c: defaultdict(dict) for c in L.REGISTERED if c in present}
    for c in vals600:
        for b in kept[c]:
            if b.get("idle_mhz") == "600":
                vals600[c][b["cfg"]][b["pass"]] = b["value"]
    ref600 = defaultdict(list)
    for b in kept.get(ref, []):
        if b.get("idle_mhz") == "600":
            ref600[b["cfg"]].append(b["value"])
    ref_mean600 = {cfg: float(np.mean(v)) for cfg, v in ref600.items()}
    g600 = {c: gap_values(c, vals600, complete, ref_mean600) for c in vals600}
    sens_test = (ratio_ci(L.welch(g600["aifoundry3"], g600["aifoundry2"]))
                 if all(len(g600.get(c, [])) >= MIN_REPEATS for c in L.REGISTERED) else None)
    sensitivity = {"test": sens_test,
                   "outcome_if_applied": (None if not sens_test else "PASS" if sens_test["hi"] < 1 else "FAIL"),
                   "bursts_left_out": {c: sum(1 for b in kept[c] if b.get("idle_mhz") != "600") for c in vals600},
                   "why": "reported, not the outcome: the registered test without the bursts whose idle brackets were "
                          "not all at 600 MHz (V3-CAT's R-clock idle-bracket rule on aifoundry2, not a catfull rule)"}
    items.append({"item": "CF-GAP", "claims": "E27 cross-card: aifoundry3 / aifoundry2 median 0.950 over the catalogue",
                  "rule": "per complete pass, g = 100 x median over configurations of ln(value / aifoundry2's mean); "
                          "Welch 99% of aifoundry3 - aifoundry2; PASS when the ratio interval lies wholly below 1",
                  "per_card": per_card, "test": test, "outcome": reg_out, "reading": reading,
                  "sensitivity_idle600_only": sensitivity,
                  "all_cards": {"outcome": "REPORTED",
                                "why": "the claim names aifoundry3 against aifoundry2; the other cards' ratios to "
                                       "aifoundry2 are reported (per_card vs_aifoundry2), not tested",
                                "reported": {c: per_card[c].get("vs_" + ref) for c in expected
                                             if c not in L.REGISTERED and c in present}},
                  "idle_clock": notes_idle, "committed_23sep": ratios["committed_cross_card"] or COMMITTED_GAP})
    # CF-COVER: every configuration of the catalogue kept in >= 3 passes on the card (E27: all at 600 MHz, none failed)
    holds, per_card = {}, {}
    for c in expected:
        if c not in present:
            holds[c] = None
            per_card[c] = {"present": False}
            continue
        exp_c = catalog_n[c]["expected"]
        npass = {cfg: len(vals[c].get(cfg, {})) for cfg in exp_c}
        short = sorted(cfg for cfg, n in npass.items() if n < MIN_REPEATS)
        n_total = catalog_n[c]["n_total"] or len(exp_c)
        used = [r for r in blocks[c] if r["used"]]
        drops = Counter(x["kind"] for r in used for x in r["dropped"])
        per_card[c] = {"complete_passes": len(complete[c]), "configurations": len(exp_c), "n_total": n_total,
                       "kept_bursts": len(kept[c]), "dropped": dict(drops),
                       "missing_launches": sum(len(r["info"].get("missing", [])) for r in used),
                       "configs_under_3_passes": len(short), "examples": short[:10], "idle_state": idle[c]["state"]}
        if len(complete[c]) < MIN_REPEATS:
            holds[c] = None
        else:
            holds[c] = (not short) and len(exp_c) >= n_total
    reg_out = outcome_of({c: holds.get(c) for c in L.REGISTERED})
    items.append({"item": "CF-COVER", "claims": "E27: every configuration measured, at 600 MHz, no failed launch",
                  "rule": f"each card: >= {MIN_REPEATS} complete passes and every configuration of the catalogue kept "
                          f"in >= {MIN_REPEATS} passes (after the drop rules)",
                  "per_card": per_card, "outcome": reg_out,
                  "reading": "; ".join(f"{c}: " + ("holds" if holds.get(c) else "INSUFFICIENT" if holds.get(c) is None
                                                  else f"{per_card[c]['configs_under_3_passes']} configurations under 3 passes")
                                       for c in L.REGISTERED),
                  "all_cards": all_cards_outcome(holds, expected), "idle_clock": notes_idle})
    # CF-REP: pass-to-pass standard error (E27: 1.9% / 6.1% aifoundry2, 1.2% / 3.6% aifoundry3): reported
    per_card = {}
    for c in expected:
        if c not in summ:
            per_card[c] = {"present": c in present, "median_pct": None}
            continue
        rel = [v["pj_per_op"]["se"] / v["pj_per_op"]["mean"] for v in summ[c].values()
               if v["pj_per_op"] and v["pj_per_op"]["mean"] > 0 and v["passes"] > 1]
        per_card[c] = {"median_pct": 100 * float(np.median(rel)) if rel else None,
                       "p90_pct": 100 * pct(rel, 90) if rel else None, "n": len(rel), "idle_state": idle[c]["state"],
                       "committed_23sep": COMMITTED_REP.get(c)}
    items.append({"item": "CF-REP", "claims": "E27: pass-to-pass standard error per card", "rule": "reported, no test",
                  "per_card": per_card, "outcome": "REPORTED",
                  "reading": "; ".join(f"{c} {v['median_pct']:.1f}% / {v['p90_pct']:.1f}%" for c, v in per_card.items()
                                       if v.get("median_pct") is not None),
                  "all_cards": {"outcome": "REPORTED", "why": "the committed values are per card"},
                  "idle_clock": notes_idle})

    res = {"exp": "catfull", "rules": RULES, "cards": present, "expected_cards": expected, "passes": passes_out,
           "complete_passes": complete, "idle_clock": idle, "items": items, "ratios": ratios,
           "vs_committed_23sep": vs_committed, "configs": configs,
           "pooled_sets": {"all": with_data, "600idle": idle600, "registered": reg}}
    json.dump(L.rnd(res, 5), open(a.out, "w"), indent=1)
    if a.catalogue_out:
        cat = {"cards": cards_out, "bursts": {c: kept[c] for c in with_data}, "combined": pooled_all,
               "combined_600idle": pooled_600, "combined_registered": pooled_reg, "cross_card": cross_card,
               "rail_filter": {c: ac.rail_filter(curves[c]) if hasattr(ac, "rail_filter") else None for c in with_data}}
        json.dump(L.rnd(cat, 6), open(a.catalogue_out, "w"), indent=1)

    # ---------------- print ----------------
    for c in expected:
        if c not in present:
            print(f"{c}: no data")
            continue
        st = Counter(r["status"] for r in blocks[c])
        print(f"{c}: blocks {dict(st)}, complete passes {complete[c]}, kept bursts {len(kept[c])}; {idle[c]['note']}")
    for it in items:
        ac_ = it["all_cards"]["outcome"]
        print(f"{it['item']}: {it['outcome']} (all cards: {ac_}) {it['reading']}")
        sv = it.get("sensitivity_idle600_only")
        if sv and sv["test"]:
            print(f"  sensitivity (not the outcome), without bursts whose brackets were off 600 MHz "
                  f"{sv['bursts_left_out']}: {sv['test']['ratio']:.3f} (99% {sv['test']['lo']:.3f}-{sv['test']['hi']:.3f}), "
                  f"{sv['outcome_if_applied']}")
    for c, r in ratios["per_card"].items():
        if r["n"]:
            print(f"ratio {c} / {ref}: median {r['median']:.3f}, 10-90% {r['p10']:.3f}-{r['p90']:.3f}, n={r['n']} (idle {r['idle_state']} MHz)")


if __name__ == "__main__":
    main()
