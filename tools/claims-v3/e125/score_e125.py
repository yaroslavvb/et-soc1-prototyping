#!/usr/bin/env python3
"""E125 (Q134): E113's A-side ladder on a second card (aifoundry1 card 1), scored as registered (E125.md, this directory).

    python3 tools/claims-v3/e125/score_e125.py --runs runs.csv --pred113 tools/claims-v3/e113/predictions-e113.json \
        --pred tools/claims-v3/e125/predictions-e125.json [--hl hl.json] [--arm NAME=runs.csv ...] \
        --out report.md --json scored.json [--e113-report report-e113-format.md]

runs.csv is hl/reduce_hl.py's per-run table (its per-run gates applied). Three parts, all from the same kept passes:
  1. E113's seven rules P1-P7, scored by tools/claims-v3/e113/score_e113.py UNCHANGED (imported, its frozen predictions file
     passed as it is): its pass gates (E67's two, E70's D-a), its paired contrasts, fits and verdicts. Z compares them with
     E113's own verdicts.
  2. The cross-card X rules: each card-1 number against E113's (a watt quantity over E82's fp32 card scale s), with both
     sessions' 95% half-widths in quadrature, PASS if |d| + h <= w, FAIL if |d| - h > w, else INCONCLUSIVE.
  3. N1: the low-layout A/B ratio at k = 2 and 4 against k = 8, within card 1's own passes (lq_h2, lq_h4 run beside alq).
Pure stdlib. SPDX-License-Identifier: Apache-2.0
"""
import argparse
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "e113"))
import score_e113 as S13  # noqa: E402  (E113's registered scorer, read only)

MIN_PASSES = S13.MIN_PASSES
N1_THRESHOLD = 0.20


def half95(se, n):
    if se is None or n is None or n < 2:
        return None
    return S13.T975.get(n - 1, 1.96) * se


def xverdict(meas, se, n, pred, h_pred, w):
    if meas is None or se is None or n is None or n < MIN_PASSES:
        return {"measured": meas, "se": se, "n": n, "pred": pred, "verdict": "UNRESOLVED"}
    h125 = half95(se, n)
    d = meas - pred
    h = math.sqrt(h125 ** 2 + (h_pred or 0.0) ** 2)
    v = "PASS" if abs(d) + h <= w else ("FAIL" if abs(d) - h > w else "INCONCLUSIVE")
    return {"measured": meas, "se": se, "n": n, "h125": h125, "pred": pred, "h_pred": h_pred, "d": d, "h": h, "w": w,
            "verdict": v}


def card1_value(R, xid):
    """The card-1 number an X rule reads, with its SE and pass count, from score_e113's result R."""
    if xid.startswith("X-alq_h") or xid.startswith("X-als_h"):
        e = R["items"].get(xid[2:], {})
        return e.get("dW"), e.get("se"), e.get("n_passes")
    if xid == "X-D1_A8":
        d = [d for d in R["D1_A"] if d["k"] == 8][0]
        return d["dW_spread_minus_low"], d["se"], d["n_passes"]
    if xid.startswith("X-rho8-"):
        r = R["rho8"][xid.split("-")[-1]]
        return r["rho"], r["se"], r["n_passes"]
    if xid == "X-nrd":
        n = R["nrd"]
        return n["ratio_nrd_a_over_nrd_b"], n["se"], n["n_passes"]
    if xid == "X-c":
        m, se = R["D2_A"].get("c_per_pass_mean_se", (None, None))
        return m, se, len(R["D2_A"].get("c_per_pass", []))
    raise KeyError(xid)


def n1(runs, kept):
    val = S13.pass_values(runs, kept)
    per, rk = [], {2: [], 4: [], 8: []}
    for p in kept:
        r = {}
        for k in (2, 4, 8):
            a, b = S13.dw(val, p, f"alq_h{k}"), S13.dw(val, p, f"lq_h{k}")
            r[k] = (a / b) if (a is not None and b) else None
        for k in (2, 4, 8):
            if r[k] is not None:
                rk[k].append(r[k])
        if None not in r.values():
            per.append((r[2] + r[4]) / 2 - r[8])
    m, se, n = S13.mean_se(per)
    out = {"N1": m, "se": se, "n_passes": n, "ci95": S13.ci95(m, se, n), "per_pass": per,
           "r": {k: dict(zip(("mean", "se", "n"), S13.mean_se(v))) | {"per_pass": v} for k, v in rk.items()}}
    if n < MIN_PASSES or m is None or se is None:
        out["verdict"] = "NOT SCORED"
    elif m >= N1_THRESHOLD and m / se >= 3:
        out["verdict"] = "SMALL-K EXCESS"
    elif out["ci95"] and out["ci95"][1] < N1_THRESHOLD:
        out["verdict"] = "NO SMALL-K EXCESS"
    else:
        out["verdict"] = "INCONCLUSIVE"
    return out


def zrule(R, pred):
    if "note" in R["rules"]:
        return {"verdict": "NOT SCORED", "note": R["rules"]["note"]}
    ev = pred["e113_verdicts"]
    got = {k: v["verdict"] for k, v in R["rules"].items()}
    same = {}
    for k in ("P1", "P2", "P3", "P5", "P6", "P7"):
        same[k] = got[k] == ev[k]
    same["P4"] = got["P4"].startswith("which bits") and (R["rules"]["P4"].get("one_parameter_laws") or "").startswith("the mirror law")
    if all(same.values()):
        v = "REPLICATES"
    elif got["P1"] == "PASS" and got["P4"].startswith("which bits"):
        v = "PARTIAL"
    else:
        v = "DOES NOT REPLICATE"
    return {"verdict": v, "same_as_E113": same, "E125": got, "E113": ev}


def ladder_scale(R, pred):
    """Reported, never a verdict: this ladder's own card scale, E113's 16 A rungs over card 1's, through the origin."""
    xs = [(R["items"][r["id"][2:]]["dW"], r["E113"]) for r in pred["x_rules"] if r["group"] == "A_rungs"
          and R["items"].get(r["id"][2:], {}).get("dW") is not None]
    if len(xs) < 5:
        return None
    sxx = sum(a * a for a, _ in xs)
    s = sum(a * b for a, b in xs) / sxx
    return {"s_ladder": s, "rms_W": math.sqrt(sum((b - s * a) ** 2 for a, b in xs) / len(xs)), "n_rungs": len(xs),
            "s_E82": pred["card_scale"]["s_fp32_aifoundry3_over_card1"]}


def score(runs, pred113, pred, all_passes=False):
    R = S13.score(runs, pred113, all_passes=all_passes)
    kept = R["passes_kept"]
    def xs(rules_):
        X_ = []
        for r in rules_:
            m, se, n = card1_value(R, r["id"])
            if len(kept) < MIN_PASSES:
                n = len(kept) if n is None else min(n, len(kept))
            X_.append({"id": r["id"], "group": r["group"], "quantity": r["quantity"], "E113": r["E113"], "scaled": r["scaled"],
                       **xverdict(m, se, n, r["pred"], r["h_pred"], r["w"])})
        return X_
    X = xs(pred["x_rules"])                          # the primary: E113 in E125's frame (dips removed, its own slope)
    Xreg = xs(pred.get("x_rules_registered", []))    # reported: against E113's registered numbers (dips kept)
    arows = [x for x in X if x["group"] == "A_rungs"]
    nf = sum(1 for x in arows if x["verdict"] == "FAIL")
    npass = sum(1 for x in arows if x["verdict"] == "PASS")
    if len(kept) < MIN_PASSES:
        agg = "UNRESOLVED"
    elif nf == 0 and npass >= 8:
        agg = "PASS"
    elif nf >= 3:
        agg = "FAIL"
    else:
        agg = "INCONCLUSIVE"
    E = {"x_rules": X, "x_rules_registered": Xreg, "x_A_rungs": {"verdict": agg, "n_pass": npass, "n_fail": nf, "n": len(arows)},
         "N1": n1(runs, kept), "Z": zrule(R, pred), "ladder_scale": ladder_scale(R, pred)}
    return R, E


def fmt(x, nd=3):
    return "—" if x is None else (f"{x:.{nd}f}" if isinstance(x, (int, float)) else str(x))


def write_report(R, E, arms, path, pred):
    L = []
    w = L.append
    w("# E125 — E113's A-side ladder on a second card (aifoundry1 card 1), scored\n")
    w(f"Passes run {R['passes_all']}, kept {R['passes_kept']} (E113's gates: E67's two and E70's D-a). Runs {R['n_runs']}, "
      f"failed a per-run gate {R['n_runs_failed']}. Card scale s (aifoundry3 over card 1, E82 fp32) "
      f"{pred['card_scale']['s_fp32_aifoundry3_over_card1']:.6f}.\n")
    w("## Pass health\n")
    w("| pass | runs | failed | anchor_pi drift (W) | constant-operand spread (W) | op rate (G minion-ops/s, card) | set aside |")
    w("|---|---|---|---|---|---|---|")
    for p, d in sorted(R["pass_table"].items()):
        w(f"| {p} | {d['n_runs']} | {d['n_failed']} | {fmt(d['pi_drift_W'])} | {fmt(d['const_spread_W'])} | "
          f"{fmt(d['mean_rate'] / 1e9 if d['mean_rate'] else None, 4)} | {', '.join(d['set_aside']) or '—'} |")
    w("\n## Z: E113's seven rules, scored by score_e113.py unchanged on card 1\n")
    Z = E["Z"]
    if "note" in Z:
        w(Z["note"])
    else:
        w("| rule | E125 (card 1) | E113 (aifoundry3) | same |")
        w("|---|---|---|---|")
        for k in ("P1", "P2", "P3", "P4", "P5", "P6", "P7"):
            w(f"| {k} | {Z['E125'][k]} | {Z['E113'][k]} | {'yes' if Z['same_as_E113'][k] else '**no**'} |")
        w(f"\nP4's one-parameter reading on card 1: {R['rules']['P4'].get('one_parameter_laws')}.")
    w(f"\n**Z: {Z['verdict']}**\n")
    w("## X: card 1 against E113 in the same frame (dips removed; a watt quantity at E113 / s)\n")
    w("| rule | quantity | E113 | prediction | card 1 | ± SE (n) | d | h | w | verdict |")
    w("|---|---|---|---|---|---|---|---|---|---|")
    for x in E["x_rules"]:
        w(f"| {x['id']} | {x['quantity']} | {fmt(x['E113'])} | {fmt(x['pred'])} | {fmt(x['measured'])} | "
          f"{fmt(x['se'])} ({x['n']}) | {fmt(x.get('d'))} | {fmt(x.get('h'))} | {fmt(x.get('w'), 2)} | **{x['verdict']}** |")
    a = E["x_A_rungs"]
    w(f"\nThe A rungs together: {a['n_pass']} of {a['n']} PASS, {a['n_fail']} FAIL: **{a['verdict']}**.")
    if E.get("x_rules_registered"):
        w("\nReported beside them, never a verdict: the same rules against E113's registered numbers (dips kept, six passes):")
        w("\n| rule | E113 registered | prediction | card 1 | d | h | verdict |")
        w("|---|---|---|---|---|---|---|")
        for x in E["x_rules_registered"]:
            w(f"| {x['id']} | {fmt(x['E113'])} | {fmt(x['pred'])} | {fmt(x['measured'])} | {fmt(x.get('d'))} | {fmt(x.get('h'))} | "
              f"{x['verdict']} |")
    ls = E["ladder_scale"]
    if ls:
        w(f"\nReported, never a verdict: this ladder's own scale, E113's A rungs over card 1's through the origin, "
          f"{ls['s_ladder']:.4f} (rms {ls['rms_W']:.3f} W over {ls['n_rungs']} rungs), against E82's {ls['s_E82']:.4f}.")
    N = E["N1"]
    w("\n## N1: the low layout's A/B ratio at k = 2 and 4 against k = 8, within card 1's passes\n")
    for k in (2, 4, 8):
        r = N["r"][k]
        w(f"- r{k} = dW(alq_h{k}) / dW(lq_h{k}): {fmt(r['mean'])} ± {fmt(r['se'])} (n {r['n']}); E113 across sessions "
          f"{fmt(pred['N1']['E113_cross_session_r'][str(k)] if str(k) in pred['N1']['E113_cross_session_r'] else pred['N1']['E113_cross_session_r'].get(k))}")
    ci = N["ci95"]
    w(f"- N1 = (r2 + r4)/2 − r8: {fmt(N['N1'])} ± {fmt(N['se'])} (n {N['n_passes']}), 95% "
      f"{'—' if not ci else f'[{ci[0]:.3f}, {ci[1]:.3f}]'}; E113 across sessions {fmt(pred['N1']['E113_cross_session_N1'])}; "
      f"threshold {N1_THRESHOLD}")
    w(f"\n**N1: {N['verdict']}**\n")
    if arms:
        w("## Arms (reported, never verdicts)\n")
        w("| arm | passes kept | P1-P7 | Z | X A rungs | N1 | D1_A(8) | c refit | rho8 low / spread | nrd ratio |")
        w("|---|---|---|---|---|---|---|---|---|---|")
        for name, (Ra, Ea) in arms.items():
            d8 = [d for d in Ra["D1_A"] if d["k"] == 8][0]
            vs = " ".join(f"{k}:{v['verdict'].split(' ')[0]}" for k, v in Ra["rules"].items()) if "note" not in Ra["rules"] else "NOT SCORED"
            w(f"| {name} | {Ra['passes_kept']} | {vs} | {Ea['Z']['verdict']} | {Ea['x_A_rungs']['verdict']} "
              f"({Ea['x_A_rungs']['n_pass']}/{Ea['x_A_rungs']['n_fail']}) | {Ea['N1']['verdict']} ({fmt(Ea['N1']['N1'])}) | "
              f"{fmt(d8['dW_spread_minus_low'])} ± {fmt(d8['se'])} | {fmt(Ra['D2_A'].get('c_refit'), 4)} | "
              f"{fmt(Ra['rho8']['low']['rho'])} / {fmt(Ra['rho8']['spread']['rho'])} | {fmt(Ra['nrd']['ratio_nrd_a_over_nrd_b'])} |")
    open(path, "w").write("\n".join(L) + "\n")


def slim(R, E):
    return {"passes_kept": R["passes_kept"], "rules": R["rules"], "Z": E["Z"]["verdict"], "x_A_rungs": E["x_A_rungs"],
            "x": {x["id"]: x["verdict"] for x in E["x_rules"]}, "N1": {k: E["N1"][k] for k in ("N1", "se", "n_passes", "verdict")},
            "D1_A": R["D1_A"], "c_refit": R["D2_A"].get("c_refit"), "rho8": {k: R["rho8"][k]["rho"] for k in ("low", "spread")},
            "nrd": R["nrd"]["ratio_nrd_a_over_nrd_b"],
            "items": {n: {"dW": e["dW"], "se": e["se"]} for n, e in R["items"].items()}}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", required=True)
    ap.add_argument("--pred113", required=True)
    ap.add_argument("--pred", required=True)
    ap.add_argument("--hl")
    ap.add_argument("--arm", action="append", default=[], help="NAME=runs.csv, a labelled sensitivity")
    ap.add_argument("--out", required=True)
    ap.add_argument("--json", required=True)
    ap.add_argument("--e113-report", help="also write score_e113's own report for card 1's runs")
    a = ap.parse_args()
    pred113, pred = json.load(open(a.pred113)), json.load(open(a.pred))
    runs = S13.load_runs(a.runs)
    R, E = score(runs, pred113, pred)
    if a.hl and os.path.exists(a.hl):
        g = list(json.load(open(a.hl)).get("gates", {}).values())
        if g:
            R["leak_W_per_C"], R["clock_mhz"] = g[0].get("leak_W_per_C"), g[0].get("clock_mhz")
    arms = {"all passes (E67's gates, no D-a)": score(runs, pred113, pred, all_passes=True)}
    for spec in a.arm:
        name, path = spec.split("=", 1)
        arms[name] = score(S13.load_runs(path), pred113, pred)
    write_report(R, E, arms, a.out, pred)
    if a.e113_report:
        S13.write_report(R, {k: v[0] for k, v in arms.items()}, a.e113_report)
    out = dict(R)
    out["e125"] = E
    out["arms"] = {k: slim(*v) for k, v in arms.items()}
    json.dump(out, open(a.json, "w"), indent=1, default=str)
    print(open(a.out).read())


if __name__ == "__main__":
    main()
