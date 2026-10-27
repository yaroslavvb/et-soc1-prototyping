#!/usr/bin/env python3
"""Score E72 against its frozen predictions, and nothing else.

    python3 tools/claims-v3/lq6/score_e72.py --results <results.json> --csv <runs.csv> \
            --pred tools/claims-v3/lq6/predictions.json --out <verdicts.json>

`reduce_e72.py` (= E60's reducer) produces the measurements. This file only compares them with
[`predictions.json`](predictions.json) and prints PASS / FAIL / INCONCLUSIVE per registered rule. It
adds one estimator that reduce_hl.py computes only when a reference card is present (its `v2` block
needs aifoundry3 in the same run): the **h2 -> h8 secant**, with E60's exact formula

    lq_h2_h8_J = (d_p80[lq_h8] - d_p80[lq_h2]) / ((32768 - 8192) * rate[lq_h8])

so E72's number and E60's published one are the same quantity. It is computed twice: once from the
pass-averaged items (E60's own published definition, for the like-for-like comparison) and once per
pass, whose scatter gives the standard error - the unit of replication is the pass, as E60 registered.
"""
import argparse
import csv
import json
import math
from collections import defaultdict

H2_FLIPS, H8_FLIPS = 8192, 32768


def mean_se(v):
    v = [x for x in v if x is not None]
    if not v:
        return None, None, 0
    m = sum(v) / len(v)
    if len(v) < 2:
        return m, None, len(v)
    sd = math.sqrt(sum((x - m) ** 2 for x in v) / (len(v) - 1))
    return m, sd / math.sqrt(len(v)), len(v)


def inband(x, band):
    return x is not None and band[0] <= x <= band[1]


def verdict(x, band, alt_band=None):
    """PASS inside the band; when an alternative band is given, PASS also needs x outside it."""
    if x is None:
        return "UNMEASURED"
    if inband(x, band):
        return "PASS" if not (alt_band and inband(x, alt_band)) else "INCONCLUSIVE"
    if alt_band and inband(x, alt_band):
        return "FAIL (the alternative's band)"
    return "FAIL"


def per_pass_values(csv_path, card, set_aside):
    """{pass: {item: {p80, rail, rate}}} over the runs E60's own gates kept."""
    out = defaultdict(lambda: defaultdict(list))
    with open(csv_path) as f:
        for r in csv.DictReader(f):
            if r["card"] != card or r["fail"] not in ("[]", ""):
                continue
            p = int(r["pass"])
            if p in set_aside:
                continue
            out[p][r["item"]].append({"p80": float(r["p80"]), "rate": float(r["rate"]),
                                      "rail": float(r["rail"]) if r["rail"] not in ("", "None") else None})
    val = {}
    for p, items in out.items():
        val[p] = {}
        for it, rr in items.items():
            val[p][it] = {k: mean_se([x[k] for x in rr])[0] for k in ("p80", "rate", "rail")}
    return val


def secant(items, key="d_p80", rate_key="rate"):
    a, b = items.get("lq_h8"), items.get("lq_h2")
    if not a or not b or a.get(key) is None or b.get(key) is None or not a.get(rate_key):
        return None
    return (a[key] - b[key]) / ((H8_FLIPS - H2_FLIPS) * a[rate_key])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", required=True)
    ap.add_argument("--csv", required=True)
    ap.add_argument("--pred", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--card", default="aifoundry2")
    ap.add_argument("--label", default="registered")
    a = ap.parse_args()

    res = json.load(open(a.results))
    pred = json.load(open(a.pred))
    C = res["cards"][a.card]
    g = res["gates"][a.card]
    R = pred["rules"]
    set_aside = {x["pass"] for x in g.get("passes_set_aside", [])}

    # --- the h2 -> h8 secant, E60's definition, from the pass-averaged items -----------------------
    sec_items = secant(C["items"])
    sec_items_rail = secant(C["items"], key="d_rail")

    # --- and per pass, for the standard error -----------------------------------------------------
    val = per_pass_values(a.csv, a.card, set_aside)
    per_pass, per_pass_rail = [], []
    for p, items in sorted(val.items()):
        z = items.get("lq_h0")
        if not z:
            continue
        d = {n: {"d_p80": items[n]["p80"] - z["p80"], "rate": items[n]["rate"],
                 "d_rail": (items[n]["rail"] - z["rail"]) if items[n]["rail"] is not None
                           and z["rail"] is not None else None}
             for n in ("lq_h2", "lq_h8") if n in items}
        s = secant(d)
        if s is not None:
            per_pass.append(s)
        sr = secant(d, key="d_rail")
        if sr is not None:
            per_pass_rail.append(sr)
    sec_m, sec_se, sec_n = mean_se(per_pass)
    secr_m, secr_se, secr_n = mean_se(per_pass_rail)

    fJ = lambda x: None if x is None else x * 1e15                                   # noqa: E731
    lq_full = C["lq"]["designed"]["fJ"]
    lq_full_se = (C["lq"]["designed"]["se_J"] or 0) * 1e15
    lb_full = C["lb"]["designed"]["fJ"]
    lb_full_se = (C["lb"]["designed"]["se_J"] or 0) * 1e15
    bend = lq_full / fJ(sec_items) if sec_items else None
    lb_over_lq = lb_full / lq_full if lq_full else None
    turnon = (C["lb"]["first_flip_W"]["W"] / C["lq"]["first_flip_W"]["W"]
              if C["lq"]["first_flip_W"]["W"] else None)

    alt = R["V1"]["alternative_if_it_scaled_with_f_too"]
    alt_band = [alt * 0.9, alt * 1.1]

    out = {
        "label": a.label,
        "card": a.card,
        "clock_mhz": g["clock_mhz"],
        "v_mean": C["v_mean"],
        "passes": C["passes"],
        "runs_kept": f"{g['kept']}/{g['runs']}",
        "leak_W_per_C": g["leak_W_per_C"],
        "measured": {
            "lq_h2_h8_secant_fJ_items": fJ(sec_items),
            "lq_h2_h8_secant_fJ_per_pass_mean": fJ(sec_m), "lq_h2_h8_secant_fJ_se": fJ(sec_se),
            "n_passes_secant": sec_n,
            "lq_h2_h8_secant_rail_fJ_items": fJ(sec_items_rail),
            "lq_h2_h8_secant_rail_fJ_per_pass_mean": fJ(secr_m), "lq_h2_h8_secant_rail_fJ_se": fJ(secr_se),
            "lq_full_ladder_fJ": lq_full, "lq_full_ladder_fJ_se": lq_full_se,
            "lb_full_ladder_fJ": lb_full, "lb_full_ladder_fJ_se": lb_full_se,
            "bend_full_over_secant": bend,
            "lb_over_lq": lb_over_lq,
            "turnon_lb_h1_over_lq_h1": turnon,
            "lq_rung_W": {n: C["items"][n].get("d_p80") for n in sorted(C["items"])
                          if n.startswith("lq_h") and n != "lq_h0"},
            "lb_rung_W": {n: C["items"][n].get("d_p80") for n in sorted(C["items"])
                          if n.startswith("lb_h") and n != "lb_h0"},
            "anchors_W": C.get("anchors"),
            "lq_linear": C["lq"].get("linear"), "lb_linear": C["lb"].get("linear"),
            "rtl_score": {k: C["rtl_score"][k] for k in ("rms_W", "ratio_measured_over_pred", "n_items", "scale")},
        },
        "rules": {
            "V1": {"predicted": R["V1"]["predicted"], "band": R["V1"]["band"],
                   "alternative": alt, "alternative_band": [round(x, 3) for x in alt_band],
                   "measured": fJ(sec_items), "measured_per_pass": fJ(sec_m), "se": fJ(sec_se),
                   "verdict": verdict(fJ(sec_items), R["V1"]["band"], alt_band)},
            "V2": {"predicted": R["V2"]["predicted"], "band": R["V2"]["band"],
                   "measured": fJ(sec_items_rail),
                   "verdict": verdict(fJ(sec_items_rail), R["V2"]["band"])},
            "V3": {"predicted_W": R["V3"]["predicted_W"],
                   "measured_W": {n: C["items"][n].get("d_p80") for n in ("lq_h1", "lq_h2", "lq_h4", "lq_h8")
                                  if n in C["items"]},
                   "scored": ["lq_h2", "lq_h8"],
                   "verdict": "PASS" if all(
                       inband(C["items"][n].get("d_p80"),
                              [R["V3"]["predicted_W"][n] * 0.9, R["V3"]["predicted_W"][n] * 1.1])
                       for n in ("lq_h2", "lq_h8") if n in C["items"] and n in R["V3"]["predicted_W"])
                       else "FAIL"},
            "V4": {"predicted": R["V4"]["predicted"], "band": R["V4"]["band"], "measured": bend,
                   "full_ladder_predicted": R["V4"]["and_so_full_ladder_fJ"],
                   "full_ladder_band": R["V4"]["full_ladder_band"], "full_ladder_measured": lq_full,
                   "verdict": verdict(bend, R["V4"]["band"])},
            "V5": {"predicted": R["V5"]["predicted"], "band": R["V5"]["band"], "measured": lb_over_lq,
                   "lb_predicted": R["V5"]["and_so_lb_fJ"], "lb_band": R["V5"]["lb_band"],
                   "lb_measured": lb_full, "verdict": verdict(lb_over_lq, R["V5"]["band"])},
            "V6": {"predicted": R["V6"]["predicted"], "band": R["V6"]["band"], "measured": turnon,
                   "verdict": verdict(turnon, R["V6"]["band"])},
            "G2": {"predicted": R["G2"]["predicted"], "band": R["G2"]["band"], "measured": C["v_mean"],
                   "verdict": verdict(C["v_mean"], R["G2"]["band"])},
        },
        "gate_failures": g["failed"], "passes_set_aside": g.get("passes_set_aside"),
    }
    with open(a.out, "w") as f:
        json.dump(out, f, indent=1)
        f.write("\n")

    print(f"== E72 [{a.label}] {a.card} {g['clock_mhz']} MHz, {C['v_mean']*1000:.1f} mV, "
          f"passes {C['passes']}, runs kept {g['kept']}/{g['runs']}, leak {g['leak_W_per_C']:.3f} W/C")
    print(f"   lq h2->h8 secant : {fJ(sec_items):7.2f} fJ   (per pass {fJ(sec_m):.2f} +- "
          f"{fJ(sec_se) if sec_se else float('nan'):.2f}, n={sec_n})")
    print(f"   lq full ladder   : {lq_full:7.2f} +- {lq_full_se:.2f} fJ")
    print(f"   lb full ladder   : {lb_full:7.2f} +- {lb_full_se:.2f} fJ")
    print(f"   rail secant      : {fJ(sec_items_rail):7.2f} fJ")
    for k, v in out["rules"].items():
        m = v.get("measured")
        p_ = v.get("predicted", v.get("predicted_W"))
        print(f"   {k:3s} {v['verdict']:28s} predicted {p_}  band {v.get('band')}  "
              f"measured {round(m, 4) if isinstance(m, float) else (m if m is not None else v.get('measured_W'))}")
    print(f"   wrote {a.out}")


if __name__ == "__main__":
    main()
