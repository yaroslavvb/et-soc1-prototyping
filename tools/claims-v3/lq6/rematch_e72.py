#!/usr/bin/env python3
"""E72 vs E60 at matched leakage slopes, on a FIXED pass set, with intervals - the corrected comparison.

    python3 tools/claims-v3/lq6/rematch_e72.py --out docs/reports/data/2026-10-27-e72-600mhz/matched

Written at the desk on 27 Oct 2026, 16:1x PDT, after an independent review of E72 found four things wrong
with the first `matched/matched.txt` (no card was touched and nothing was re-measured):

  1. The five "matched" rows were not matched IN SAMPLE. `reduce_hl.py` sets a pass aside when its
     `anchor_pi` drifts more than 0.3 W, and that drift is computed on the LEAKAGE-CORRECTED power, so
     changing the slope changes which passes are kept. E60 keeps 9 passes at 0.4420 and 8 at 0.000, so
     part of every row-to-row move - and all of the rail column's - was a change of sample, not of slope.
     Here E60 is reduced on the INTERSECTION set (passes 2,3,4,6,7,8,9,10; 143 runs) at every slope, so a
     row-to-row move is a slope move and nothing else. E72 keeps all 5 passes / 125 runs at every slope.
  2. No row carried an interval, so "n = 2 is inside that range everywhere" was read off point estimates.
     Every row here carries the per-pass SE of both secants (the pass is the unit of replication, as E60
     registered), propagated into the ratio and into the exponent n.
  3. The registered +-10% V1 test was never re-run at a matched slope: the frozen prediction is E60's
     number at E60's own auto slope. Here the prediction MOVES WITH THE SLOPE, pred = E60(slope) x
     (V600/V800)^2 at the measured voltages, and the +-10% band is applied to that.
  4. The rail was called slope-free. It is not corrected at all - `reduce_hl.py` applies the leakage
     correction to the board only - and it is read over a window one second later than the board's. Part
     B re-extracts the rail from the committed telemetry over both windows and prices the same assumed
     slopes on it, which is what "not slope-free, merely uncorrected" means in numbers.

Everything is computed from files committed in this repo:
  * `docs/reports/data/2026-10-20-bitflip-ladder/runs.csv`   (E60, this card at 800 MHz)
  * `docs/reports/data/2026-10-27-e72-600mhz/runs.csv`       (E72, this card at 600 MHz)
  * the per-pass telemetry of both, for part B
  * `docs/reports/data/2026-10-20-bitflip-ladder/hl.json`    (E60's measured voltage)
  * `tools/claims-v3/lq6/predictions.json`                   (the frozen band, for reference only)

The arithmetic in part A is `reduce_hl.py`'s own, downstream of the window extraction: p80 = p_raw -
k (T_window - T_launch); the pass gates as the reducer wrote them into runs.csv; a pass set aside when
more than one of its runs failed a gate or its anchor_pi drifted > 0.3 W; one value per (pass, item) as
the mean of its runs; items as the mean over passes of (item - its zero); the h2 -> h8 secant with E60's
exact formula. Part A reproduces every published number to the last digit (`--selftest`), which is how
the changes below are isolated.
"""
import argparse
import csv
import gzip
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
E60_DIR = os.path.join(ROOT, "docs/reports/data/2026-10-20-bitflip-ladder")
E72_DIR = os.path.join(ROOT, "docs/reports/data/2026-10-27-e72-600mhz")
E60_CSV = os.path.join(E60_DIR, "runs.csv")
E72_CSV = os.path.join(E72_DIR, "runs.csv")
E60_PASSES = os.path.join(E60_DIR, "aifoundry2/hl")
E72_PASSES = os.path.join(E72_DIR, "aifoundry2/e72")
H2, H8 = 8192, 32768                       # designed B-mantissa flips per op at the two rungs
CARD = "aifoundry2"

K_E60_AUTO = 0.4419545454545419            # reduce_hl.py's own within-run fit on E60's 800 MHz passes
K_E72_AUTO = 0.09823275862069246           # the same fit on E72's 600 MHz passes
SLOPES = [(0.0, "0.000 (no leakage correction)"),
          (K_E72_AUTO, "0.098 (E72's own auto fit)"),
          (0.2936, "0.2936 (E66, measured idle on THIS card)"),
          (0.4420, "0.4420 (E60's own auto fit)")]
RAIL_SLOPES = [0.0, K_E72_AUTO, 0.2936, 0.4420]


# ---------------------------------------------------------------- helpers
def mean(v):
    v = [x for x in v if x is not None]
    return sum(v) / len(v) if v else None


def mean_se(v):
    v = [x for x in v if x is not None]
    if not v:
        return None, None, 0
    m = sum(v) / len(v)
    if len(v) < 2:
        return m, None, len(v)
    sd = math.sqrt(sum((x - m) ** 2 for x in v) / (len(v) - 1))
    return m, sd / math.sqrt(len(v)), len(v)


def load_csv(path, card=CARD):
    out = []
    with open(path) as f:
        for r in csv.DictReader(f):
            if r["card"] != card:
                continue
            out.append({"pass": int(r["pass"]), "item": r["item"], "pos": int(r["pos"]),
                        "attempt": int(r["attempt"]),
                        "p_raw": float(r["p_raw"]), "p80": float(r["p80"]), "t_win": float(r["t_win"]),
                        "start_c": float(r["start_c"]) if r["start_c"] not in ("", "None") else None,
                        "rail": float(r["rail"]) if r["rail"] not in ("", "None") else None,
                        "rate": float(r["rate"]), "mv": float(r["mv"]),
                        "fail": json.loads(r["fail"]) if r["fail"] else []})
    return out


# ---------------------------------------------------------------- part A: the matched-slope table
def reduce_at(rows, k, force_passes=None):
    """reduce_hl.py's arithmetic at leakage slope k, optionally on a forced pass set."""
    for r in rows:
        base = r["start_c"] if r["start_c"] is not None else r["t_win"]
        r["p80k"] = r["p_raw"] - k * (r["t_win"] - base)
    set_aside = []
    for p in sorted({r["pass"] for r in rows}):
        rp = [r for r in rows if r["pass"] == p]
        nf = sum(1 for r in rp if r["fail"])
        pis = sorted([r for r in rp if r["item"] == "anchor_pi" and not r["fail"]], key=lambda r: r["pos"])
        drift = pis[-1]["p80k"] - pis[0]["p80k"] if len(pis) >= 2 else None
        if nf > 1 or (drift is not None and abs(drift) > 0.3):
            set_aside.append({"pass": p, "failed_runs": nf, "pi_drift_W": drift})
    bad = {x["pass"] for x in set_aside}
    if force_passes is not None:
        bad |= {p for p in {r["pass"] for r in rows} if p not in set(force_passes)}
    G = [r for r in rows if not r["fail"] and r["pass"] not in bad]
    val = {}
    for p in sorted({r["pass"] for r in G}):
        val[p] = {}
        for item in sorted({r["item"] for r in G if r["pass"] == p}):
            rr = [r for r in G if r["pass"] == p and r["item"] == item]
            val[p][item] = {key: mean([x[key] for x in rr]) for key in ("p80k", "rail", "rate", "t_win")}
    passes = sorted(val)
    d = {}
    for item in ("lq_h2", "lq_h8"):
        for key, dk in (("p80k", "d_p80"), ("rail", "d_rail")):
            m, se, n = mean_se([val[p][item][key] - val[p]["lq_h0"][key]
                                for p in passes if item in val[p] and "lq_h0" in val[p]
                                and val[p][item][key] is not None and val[p]["lq_h0"][key] is not None])
            d.setdefault(item, {})[dk] = m
        d[item]["rate"] = mean([val[p][item]["rate"] for p in passes if item in val[p]])
    sec = ((d["lq_h8"]["d_p80"] - d["lq_h2"]["d_p80"]) / ((H8 - H2) * d["lq_h8"]["rate"]) * 1e15)
    secr = None
    if d["lq_h8"]["d_rail"] is not None and d["lq_h2"]["d_rail"] is not None:
        secr = (d["lq_h8"]["d_rail"] - d["lq_h2"]["d_rail"]) / ((H8 - H2) * d["lq_h8"]["rate"]) * 1e15
    pp, ppr, dts = [], [], []
    for p in passes:
        it = val[p]
        if not all(n in it for n in ("lq_h0", "lq_h2", "lq_h8")):
            continue
        pp.append((it["lq_h8"]["p80k"] - it["lq_h2"]["p80k"]) / ((H8 - H2) * it["lq_h8"]["rate"]) * 1e15)
        if it["lq_h8"]["rail"] is not None and it["lq_h2"]["rail"] is not None:
            ppr.append((it["lq_h8"]["rail"] - it["lq_h2"]["rail"]) / ((H8 - H2) * it["lq_h8"]["rate"]) * 1e15)
        dts.append(it["lq_h8"]["t_win"] - it["lq_h2"]["t_win"])
    m, se, n = mean_se(pp)
    mr, ser, nr = mean_se(ppr)
    return {"k": k, "passes": passes, "kept": len(G), "runs": len(rows), "set_aside": set_aside,
            "sec_items_fJ": sec, "sec_pp_fJ": m, "sec_pp_se_fJ": se, "n_passes": n, "per_pass_fJ": pp,
            "rail_items_fJ": secr, "rail_pp_fJ": mr, "rail_pp_se_fJ": ser,
            "dT_h8_h2_C": dts,
            "v_mean": (mean([r["mv"] for r in G]) / 1000) if G else None}


def exponent(r_ratio, se_ratio, vr):
    """n and its SE in ratio = (V600/V800)^n."""
    ln = math.log(vr)
    n = math.log(r_ratio) / ln
    se = abs((se_ratio / r_ratio) / ln) if se_ratio else None
    return n, se


# ---------------------------------------------------------------- part B: the rail estimator
def jl(path):
    if not os.path.exists(path) and os.path.exists(path + ".gz"):
        path += ".gz"
    op = gzip.open if path.endswith(".gz") else open
    out = []
    for line in op(path, "rt"):
        if line.startswith("{"):
            try:
                out.append(json.loads(line))
            except ValueError:
                pass
    return out


def ols(x, y):
    n = len(x)
    mx, my = sum(x) / n, sum(y) / n
    sxx = sum((a - mx) ** 2 for a in x)
    return sum((a - mx) * (b - my) for a, b in zip(x, y)) / sxx if sxx else None


def median(v):
    v = sorted(v)
    n = len(v)
    return (v[n // 2] if n % 2 else 0.5 * (v[n // 2 - 1] + v[n // 2])) if n else None


def windows_of_pass(d, gov_free, busy_mhz=800):
    """reduce_hl.py's own window selection, with the rail read over BOTH windows."""
    tel = jl(os.path.join(d, "telemetry.jsonl"))
    t = [s["t_ms"] for s in tel]
    P = [s["board_w"] for s in tel]
    RL = [s["sp"]["minion_w"][0] for s in tel]
    MH = [s["mhz"]["minion"] for s in tel]
    T = [float(s["temp_c"]["minshire"][0]) for s in tel]
    by = {}
    for r in jl(os.path.join(d, "runs.jsonl")):
        by.setdefault((r["block"], r["item"], r.get("pos", 0), r.get("attempt", 1)), []).append(r)
    out = []
    for m in [x for x in jl(os.path.join(d, "marks.jsonl")) if x.get("kind") == "run"]:
        rr = sorted(by.get((m["block"], m["item"], m.get("pos", 0), m.get("attempt", 1)), []),
                    key=lambda r: r["t_start_ms"])
        if not rr:
            continue
        t0 = rr[0]["t_start_ms"]
        lo = t0 + 1000
        if gov_free:
            at = [i for i, (ti, mi) in enumerate(zip(t, MH)) if t0 <= ti <= t0 + 4000 and mi == busy_mhz]
            if at:
                lo = max(t0 + 1000, t[at[0]] + 500)
        hi, rend = lo + 2000, rr[-1]["t_end_ms"]
        iw = [i for i, ti in enumerate(t) if lo <= ti < hi]
        iwr = [i for i, ti in enumerate(t) if lo + 1000 <= ti < min(lo + 3000, rend)]
        itr = [i for i, ti in enumerate(t) if max(t0 + 800, lo - 200) <= ti <= rend]
        if len(iw) < 5:
            continue
        kb = kr = None
        if len(itr) > 10 and max(T[i] for i in itr) - min(T[i] for i in itr) >= 1:
            kb = ols([T[i] for i in itr], [P[i] for i in itr])
            kr = ols([T[i] for i in itr], [RL[i] for i in itr])
        out.append({"pass": m["block"], "item": m["item"], "pos": m.get("pos", 0),
                    "attempt": m.get("attempt", 1), "start_c": m.get("start_c"),
                    "p_raw": mean([P[i] for i in iw]), "t_win": mean([T[i] for i in iw]),
                    "rail_wr": mean([RL[i] for i in iwr]) if iwr else None,
                    "rail_w": mean([RL[i] for i in iw]),
                    "t_wr": mean([T[i] for i in iwr]) if iwr else None,
                    "k_board_run": kb, "k_rail_run": kr})
    return out


def rail_block(base, gov_free, csv_rows, passes, kept_passes, label):
    rows = []
    for p in passes:
        rows += windows_of_pass(os.path.join(base, f"p{p}"), gov_free)
    rows = [r for r in rows if r["item"] != "ls_h8"]     # reduce_hl.py amendment A3 on this card
    ref = {(r["pass"], r["item"], r["pos"], r["attempt"]): r for r in csv_rows}
    worst = {"p_raw": 0.0, "t_win": 0.0, "rail": 0.0}
    for r in rows:
        k = (r["pass"], r["item"], r["pos"], r["attempt"])
        if k not in ref:
            r["fail"], r["rate"] = ["unmatched"], None
            continue
        worst["p_raw"] = max(worst["p_raw"], abs(r["p_raw"] - ref[k]["p_raw"]))
        worst["t_win"] = max(worst["t_win"], abs(r["t_win"] - ref[k]["t_win"]))
        if ref[k]["rail"] is not None and r["rail_wr"] is not None:
            worst["rail"] = max(worst["rail"], abs(r["rail_wr"] - ref[k]["rail"]))
        r["rate"], r["fail"] = ref[k]["rate"], ref[k]["fail"]

    def sec(key, k_leak, tkey):
        val = {}
        for r in rows:
            if r["fail"] or r["pass"] not in kept_passes or r.get(key) is None:
                continue
            base_c = r["start_c"] if r["start_c"] is not None else r[tkey]
            val.setdefault(r["pass"], {}).setdefault(r["item"], []).append(
                (r[key] - k_leak * (r[tkey] - base_c), r["rate"]))
        pp = []
        for p, items in sorted(val.items()):
            if not all(n in items for n in ("lq_h2", "lq_h8")):
                continue
            m = {n: (mean([x[0] for x in items[n]]), mean([x[1] for x in items[n]])) for n in ("lq_h2", "lq_h8")}
            pp.append((m["lq_h8"][0] - m["lq_h2"][0]) / ((H8 - H2) * m["lq_h8"][1]) * 1e15)
        return mean_se(pp)

    kb = [r["k_board_run"] for r in rows if r["k_board_run"] is not None]
    kr = [r["k_rail_run"] for r in rows if r["k_rail_run"] is not None]
    off = mean([r["t_wr"] - r["t_win"] for r in rows
                if r["pass"] in kept_passes and not r["fail"] and r["t_wr"] is not None])
    out = {"label": label, "kept_passes": sorted(kept_passes),
           "reproduces_runs_csv_worst_abs_diff": worst,
           "within_run_fit_board_W_per_C": median(kb), "within_run_fit_rail_W_per_C": median(kr),
           "n_runs_fitted": len(kb),
           "rail_window_minus_board_window_C": off,
           "rail_published_window_fJ": None, "rail_board_window_fJ": None, "at_assumed_slope": {}}
    m, se, n = sec("rail_wr", 0.0, "t_wr")
    out["rail_published_window_fJ"], out["rail_published_window_se_fJ"], out["n_passes"] = m, se, n
    m2, se2, _ = sec("rail_w", 0.0, "t_win")
    out["rail_board_window_fJ"], out["rail_board_window_se_fJ"] = m2, se2
    for k in RAIL_SLOPES:
        m3, se3, _ = sec("rail_wr", k, "t_wr")
        out["at_assumed_slope"][f"{k:.4f}"] = {"fJ": m3, "se_fJ": se3}
    return out


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(E72_DIR, "matched"))
    ap.add_argument("--selftest", action="store_true", help="only check that the published numbers reproduce")
    a = ap.parse_args()

    e60 = load_csv(E60_CSV)
    e72 = load_csv(E72_CSV)
    hl = json.load(open(os.path.join(E60_DIR, "hl.json")))
    v800 = hl["cards"][CARD]["v_mean"]
    pred = json.load(open(os.path.join(HERE, "predictions.json")))

    # ---- self-test: the published rows must come back exactly
    checks = []
    # NOTE: the published row labelled "0.098 (E72's auto)" was reduced at the literal 0.098, not at
    # E72's exact auto fit 0.09823275862069246 (a 0.002% difference in the result; 125.2925 vs 125.2898).
    # The matched family below uses the exact auto value and says so.
    for k, want in ((K_E60_AUTO, 121.26260641705045), (0.0, 126.44430273746795),
                    (0.098, 125.29250181993704), (0.2936, 122.99360121310984),
                    (0.4420, 121.2620627219662)):
        got = reduce_at(e60, k)["sec_items_fJ"]
        checks.append(("E60 sec @ %.6g" % k, got, want, abs(got - want) < 1e-6))
    for k, want in ((K_E72_AUTO, 79.17699443471498), (0.0, 81.06719586341879),
                    (0.2936, 75.41772467621172), (0.4420, 72.56220177368593)):
        got = reduce_at(e72, k)["sec_items_fJ"]
        checks.append(("E72 sec @ %.6g" % k, got, want, abs(got - want) < 1e-6))
    r = reduce_at(e72, K_E72_AUTO)
    checks.append(("E72 per-pass mean", r["sec_pp_fJ"], 79.17567, abs(r["sec_pp_fJ"] - 79.17567) < 5e-5))
    checks.append(("E72 per-pass SE", r["sec_pp_se_fJ"], 3.08546, abs(r["sec_pp_se_fJ"] - 3.08546) < 5e-5))
    checks.append(("E72 rail", r["rail_items_fJ"], 63.265378429718226, abs(r["rail_items_fJ"] - 63.2653784) < 1e-6))
    print("SELF-TEST against the published reductions")
    for name, got, want, ok in checks:
        print(f"   {'OK ' if ok else 'BAD'} {name:22s} {got:12.6f}  (published {want})")
    if a.selftest:
        return

    v600 = reduce_at(e72, K_E72_AUTO)["v_mean"]
    vr = v600 / v800
    r_v2 = vr ** 2
    r_fv2 = 0.75 * r_v2

    # ---- the E60 pass sets, and the intersection the matched family is reduced on
    sets = {}
    for k, _ in [(K_E60_AUTO, "auto")] + SLOPES:
        sets[k] = reduce_at(e60, k)["passes"]
    fixed = sorted(set.intersection(*[set(v) for v in sets.values()]))

    rows = []
    reg60, reg72 = reduce_at(e60, K_E60_AUTO), reduce_at(e72, K_E72_AUTO)
    rows.append(dict(tag="registered", label="the registered reduction: each experiment's own auto slope",
                     matched=False, k_e60=K_E60_AUTO, k_e72=K_E72_AUTO, e60=reg60, e72=reg72))
    for k, lab in SLOPES:
        rows.append(dict(tag=f"{k:.4f}", label=lab, matched=True, k_e60=k, k_e72=k,
                         e60=reduce_at(e60, k, force_passes=fixed), e72=reduce_at(e72, k)))

    table = []
    for row in rows:
        a60, a72 = row["e60"], row["e72"]
        rec = {"tag": row["tag"], "label": row["label"], "matched_sample": row["matched"],
               "k_e60_W_per_C": row["k_e60"], "k_e72_W_per_C": row["k_e72"],
               "e60_passes": a60["passes"], "e60_runs_kept": a60["kept"],
               "e72_passes": a72["passes"], "e72_runs_kept": a72["kept"],
               "e60_fJ": a60["sec_items_fJ"], "e60_se_fJ": a60["sec_pp_se_fJ"],
               "e72_fJ": a72["sec_items_fJ"], "e72_se_fJ": a72["sec_pp_se_fJ"],
               "e60_rail_fJ": a60["rail_items_fJ"], "e60_rail_se_fJ": a60["rail_pp_se_fJ"],
               "e72_rail_fJ": a72["rail_items_fJ"], "e72_rail_se_fJ": a72["rail_pp_se_fJ"]}
        for side, b60, s60, b72, s72 in (("board", a60["sec_items_fJ"], a60["sec_pp_se_fJ"],
                                          a72["sec_items_fJ"], a72["sec_pp_se_fJ"]),
                                         ("rail", a60["rail_items_fJ"], a60["rail_pp_se_fJ"],
                                          a72["rail_items_fJ"], a72["rail_pp_se_fJ"])):
            ratio = b72 / b60
            se_ratio = ratio * math.sqrt((s72 / b72) ** 2 + (s60 / b60) ** 2) if s60 and s72 else None
            n, se_n = exponent(ratio, se_ratio, vr)
            rec[f"ratio_{side}"] = ratio
            rec[f"ratio_{side}_se"] = se_ratio
            rec[f"n_{side}"] = n
            rec[f"n_{side}_se"] = se_n
            rec[f"n_{side}_dist_from_2_SE"] = abs(n - 2) / se_n if se_n else None
            rec[f"n_{side}_dist_from_364_SE"] = abs(n - 3.637) / se_n if se_n else None
        # the registered +-10% test, with the prediction moved to the SAME slope
        p = a60["sec_items_fJ"] * r_v2
        rec["v1_pred_fJ"], rec["v1_band"] = p, [p * 0.9, p * 1.1]
        rec["v1_measured_fJ"] = a72["sec_items_fJ"]
        rec["v1_err_frac"] = a72["sec_items_fJ"] / p - 1
        rec["v1_verdict"] = "PASS" if p * 0.9 <= a72["sec_items_fJ"] <= p * 1.1 else "FAIL"
        table.append(rec)

    # ---- part B: the rail estimator
    railb = {"E60_800MHz": rail_block(E60_PASSES, True, e60, range(1, 11), set(fixed), "E60 @ 800 MHz, fixed 8 passes"),
             "E72_600MHz": rail_block(E72_PASSES, False, e72, range(1, 6), {1, 2, 3, 4, 5}, "E72 @ 600 MHz, 5 passes")}
    rail_rows = []
    for k in RAIL_SLOPES:
        b = railb["E60_800MHz"]["at_assumed_slope"][f"{k:.4f}"]
        c = railb["E72_600MHz"]["at_assumed_slope"][f"{k:.4f}"]
        ratio = c["fJ"] / b["fJ"]
        se = ratio * math.sqrt((c["se_fJ"] / c["fJ"]) ** 2 + (b["se_fJ"] / b["fJ"]) ** 2)
        n, se_n = exponent(ratio, se, vr)
        rail_rows.append({"assumed_slope_W_per_C": k, "e60_fJ": b["fJ"], "e60_se_fJ": b["se_fJ"],
                          "e72_fJ": c["fJ"], "e72_se_fJ": c["se_fJ"], "ratio": ratio, "ratio_se": se,
                          "n": n, "n_se": se_n})

    # ---- the die-temperature difference the board correction acts on
    dt = {"e72_dT_h8_minus_h2_C_per_pass": reg72["dT_h8_h2_C"],
          "e72_per_pass_secant_fJ_registered": reg72["per_pass_fJ"],
          "e60_dT_h8_minus_h2_C_per_pass": reg60["dT_h8_h2_C"],
          "e60_per_pass_secant_fJ_auto": reg60["per_pass_fJ"],
          "sensor_resolution_C": 1.0,
          "note": ("the leak correction moves the secant by k (dT_h8 - dT_h2) / ((32768-8192) rate); on E72 that "
                   "difference is 0.53 C on average and 0.000 C in pass 2, from a die sensor that reports whole "
                   "degrees, so a 10% swing in the board price rests on a sub-degree difference")}

    out = {"what": "E72 vs E60 on the same card, matched leakage slope, fixed pass set, with intervals",
           "written": "2026-10-27 (Tue, week 44), desk correction after independent review",
           "card": "aifoundry2 card 0", "v800_measured": v800, "v600_measured": v600,
           "v_ratio": vr, "ratio_v2": r_v2, "ratio_f_times_v2": r_fv2,
           "n_of_the_alternative": math.log(r_fv2) / math.log(vr),
           "e60_pass_sets_by_slope": {f"{k:.6g}": v for k, v in sets.items()},
           "e60_fixed_pass_set": fixed,
           "frozen_prediction_for_reference": {"V1_predicted": pred["rules"]["V1"]["predicted"],
                                               "V1_band": pred["rules"]["V1"]["band"],
                                               "evaluated_at_v600": pred["voltages"]["v600_expected"]},
           "rows": table, "rail": railb, "rail_ratio_at_assumed_slope": rail_rows, "dT": dt}
    os.makedirs(a.out, exist_ok=True)
    jp = os.path.join(a.out, "matched-fixed.json")
    with open(jp, "w") as f:
        json.dump(out, f, indent=1)
        f.write("\n")

    L = []
    L.append("E72 vs E60, SAME CARD (aifoundry2 card 0), same operand files, same reducer.")
    L.append(f"E60 ran it at 800 MHz / {v800:.4f} V; E72 at 600 MHz / {v600:.4f} V.  "
             f"(V600/V800)^2 = {r_v2:.4f} ; x 600/800 = {r_fv2:.4f}  (the alternative is n = "
             f"{math.log(r_fv2)/math.log(vr):.3f})")
    L.append("")
    L.append("CORRECTED 27 Oct 2026 at the desk: the matched rows below are reduced on a FIXED E60 pass set")
    L.append(f"   {fixed} (the intersection of the sets the five slopes keep), so a row-to-row move is a")
    L.append("   slope move and not a change of sample. E60's kept passes by slope, as reduce_hl.py chooses them:")
    for k, v in sets.items():
        L.append(f"      k={k:<10.6g} passes {v}")
    L.append("   E72 keeps all 5 passes / 125 runs at every slope. Every number carries the per-pass SE.")
    L.append("")
    L.append("A. the h2 -> h8 secant, board, fJ per designed flipped B mantissa bit")
    L.append("")
    L.append("   leakage slope                         E60 800        E72 600        ratio          n (board)")
    for r in table:
        mark = "  " if r["matched_sample"] else " *"
        L.append(f"{mark} {r['label'][:35]:<35s} {r['e60_fJ']:7.2f}+-{r['e60_se_fJ']:4.2f} "
                 f"{r['e72_fJ']:7.2f}+-{r['e72_se_fJ']:4.2f}  {r['ratio_board']:.4f}+-{r['ratio_board_se']:.4f}  "
                 f"{r['n_board']:.2f}+-{r['n_board_se']:.2f}")
    L.append("   * the registered row: E60 at its own auto slope on 9 passes, E72 at its own on 5 - the two sides")
    L.append("     are NOT at the same slope, which is why it is kept apart from the matched family.")
    L.append("")
    L.append("B. the SAME +-10% test as the registered V1, with the prediction moved to the SAME slope")
    L.append("   (pred = E60(slope) x (V600/V800)^2 at the measured voltages)")
    L.append("")
    L.append("   leakage slope                        pred      band                measured   err     verdict")
    for r in table:
        L.append(f"   {r['label'][:35]:<35s} {r['v1_pred_fJ']:6.2f}  "
                 f"[{r['v1_band'][0]:6.2f},{r['v1_band'][1]:6.2f}]  {r['v1_measured_fJ']:7.2f}  "
                 f"{r['v1_err_frac']*100:+6.1f}%  {r['v1_verdict']}")
    L.append("   The registered verdict is the first row and stands as registered. The matched family is a")
    L.append("   POST-HOC re-test: it fails at three of the four matched slopes, passing only at slope 0.")
    L.append("")
    L.append("C. the exponent n in (V600/V800)^n, with the SE propagated from both per-pass SEs")
    L.append("")
    L.append("   leakage slope                        n board          |n-2|   n rail           |n-2|")
    for r in table:
        L.append(f"   {r['label'][:35]:<35s} {r['n_board']:.2f}+-{r['n_board_se']:.2f}      "
                 f"{r['n_board_dist_from_2_SE']:4.1f} SE   {r['n_rail']:.2f}+-{r['n_rail_se']:.2f}      "
                 f"{r['n_rail_dist_from_2_SE']:4.1f} SE")
    L.append("   n = 2 is NOT the point estimate of any row. The board family runs 2.4-2.9 and the rail family")
    L.append("   1.6-1.7: the two bracket 2 from opposite sides. The clock-scaling alternative (n = 3.64) is")
    L.append("   excluded by every row, board and rail, at 3 SE or more - that half of the identification stands.")
    L.append("")
    L.append("D. the rail is not slope-free, it is UNCORRECTED (reduce_hl.py corrects the board only), and it is")
    L.append("   read over a window one second later than the board's because the rail telemetry is a 1 s running")
    L.append("   average. Re-extracted from the committed telemetry (reproduces runs.csv exactly):")
    L.append("")
    for key in ("E60_800MHz", "E72_600MHz"):
        b = railb[key]
        L.append(f"   {b['label']}")
        L.append(f"      rail window is {b['rail_window_minus_board_window_C']:+.3f} C hotter than the board window")
        L.append(f"      rail secant over the published window : {b['rail_published_window_fJ']:7.3f} "
                 f"+- {b['rail_published_window_se_fJ']:.3f} fJ")
        L.append(f"      the same over the BOARD's window      : {b['rail_board_window_fJ']:7.3f} "
                 f"+- {b['rail_board_window_se_fJ']:.3f} fJ  (biased: it reaches into the 1 s average's past)")
        L.append(f"      within-run power-vs-temperature fit   : board {b['within_run_fit_board_W_per_C']:.4f}, "
                 f"rail {b['within_run_fit_rail_W_per_C']:.4f} W/C - the rail's is a launch transient, not leakage,")
        L.append("                                              which is why the rail cannot be self-corrected")
    L.append("")
    L.append("   if the rail DID carry a leakage slope of the same size as the board's:")
    L.append("      assumed slope   E60 rail        E72 rail        ratio            n (rail)")
    for r in rail_rows:
        L.append(f"      {r['assumed_slope_W_per_C']:<13.4f} {r['e60_fJ']:7.2f}+-{r['e60_se_fJ']:4.2f} "
                 f"{r['e72_fJ']:7.2f}+-{r['e72_se_fJ']:4.2f}  {r['ratio']:.4f}+-{r['ratio_se']:.4f}  "
                 f"{r['n']:.2f}+-{r['n_se']:.2f}")
    L.append("   So the rail moves by 16% across the same slope ladder the board moves 10% across. 'Quote the")
    L.append("   rail, it is slope-free' is withdrawn: neither side is slope-free, and only the board has an")
    L.append("   independently measured idle slope (E66, 0.2936 W/C on this card) to be corrected at.")
    L.append("")
    L.append("E. the die-temperature difference the board correction actually acts on")
    L.append(f"   E72 (t_h8 - t_h2) per pass, board window: {[round(x, 3) for x in dt['e72_dT_h8_minus_h2_C_per_pass']]}"
             f"  mean {mean(dt['e72_dT_h8_minus_h2_C_per_pass']):.3f} C")
    L.append(f"   E72 per-pass secants at the registered slope: "
             f"{[round(x, 1) for x in dt['e72_per_pass_secant_fJ_registered']]} fJ")
    L.append(f"   E60 (t_h8 - t_h2) per pass, board window: {[round(x, 3) for x in dt['e60_dT_h8_minus_h2_C_per_pass']]}")
    L.append("   The die sensor reports whole degrees. The whole leakage-slope sensitivity of the board price")
    L.append("   rests on that 0.53 C mean difference, which is exactly 0 in one of the five passes.")
    tp = os.path.join(a.out, "matched-fixed.txt")
    with open(tp, "w") as f:
        f.write("\n".join(L) + "\n")
    print("\n".join(L))
    print(f"\n   wrote {jp}\n   wrote {tp}")


if __name__ == "__main__":
    main()
