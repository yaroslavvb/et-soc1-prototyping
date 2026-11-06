#!/usr/bin/env python3
"""Q145(b) fix, POST HOC: the dip term's amendment A1 (tools/claims-v3/dipterm/REGISTRATION.md.dated-note-4.md, lab 3002edaf)
on committed sessions, and the checks the registration promised. Every figure is post hoc: the data existed first, and A1's
rule was chosen after its author read the verifier's Q132(g) check and E173-E175's rings. Desk only, no card.

    python3 -I -B posthoc_dips_a1.py --lab <the lab tree> --out posthoc-dips-a1.json > posthoc-dips-a1.txt

1. Q132(g)'s six sessions (E64, E69, E80, E83, E87 on aifoundry2; E84 on card 0), the check the registration's Builds-on block
   promised: DT-N's registered rule, Q132(g)'s own rule through DT-N's formula, and A1's rule (all blocks, and burst blocks only).
2. E100, arm by arm and pooled over its five gapped arms: the registered rule and A1's.
3. E173, E174 and E175 under A1 with score_dipterm_v4.py: DT-N, DT-L, the scope, every arm's rules with their Monte Carlo
   standard errors, seq-gc and seq-lag (reported); beside them the registered rule's count and seq arms at A1-4's draws, and
   each registered fall against the lattice of the session's other falls (leave one out).
4. Each session's period from its falls, with the card's prior (as the registration fits it) and without it.
5. The SP pass under the 10 Hz sampler: the mean time between board_w changes at 800 MHz, per run, in E173-E175.
6. What each fall cost its pass against the term's cost on the lattice of all the session's falls, with the registered climb and
   with A1-5's (card 0; in sample for E174, whose falls enter A1-5's pooled climb).
It imports dipterm.py, dipterm_a1.py and score_dipterm_v4.py after checking them against SHA256SUMS-5.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import gzip
import hashlib
import json
import math
import os
import statistics as st
import sys

D = "docs/reports/data"
Q132 = {
    "E64": ("a2", ["2026-10-23-e64-horace-power-limit/s1", "2026-10-23-e64-horace-power-limit/s2"]),
    "E69": ("a2", ["2026-10-27-e69-governor-knob/s1", "2026-10-27-e69-governor-knob/s2", "2026-10-27-e69-governor-knob/s3"]),
    "E80": ("a2", ["2026-10-31-e80-kinds-speed/s1"]),
    "E83": ("a2", ["2026-10-31-e83-kinds-speed-rest/s1"]),
    "E87": ("a2", ["2026-10-31-e87-real-tensors-speed/s1"]),
    "E84": ("c0", ["2026-10-31-e84-speed-aifoundry1-card0/s1"]),
}
E100 = "2026-11-01-e100-idle-reset/s1"
SESSIONS = {
    "E173": {"dir": "2026-11-05-e173-blind8-aifoundry2", "sdir": "aifoundry2/s1", "card": "a2",
             "clock": ("P8-A2-F2", "pinned"), "board": ("P8-A2-Bp", "pinned"),
             "pred": "tools/claims-v3/kinds/blind8/predictions-pool8-aifoundry2.json"},
    "E174": {"dir": "2026-11-05-e174-blind8-card0", "sdir": "aifoundry1-c0/s1", "card": "c0",
             "clock": ("P8-C0-F", "all"), "board": None, "pred": None},
    "E175": {"dir": "2026-11-05-e175-governed-aifoundry2", "sdir": "aifoundry2/s1", "card": "a2",
             "clock": ("E175-A2-G", "governed"), "board": ("E175-A2-Bp", "pinned"),
             "pred": "tools/claims-v3/e175/predictions-e175.json", "clock2": ("E175-A2-F2", "pinned")},
}
REL = "docs/reports/data/2026-11-04-q140l-a2-session-terms/m9_a2.json"


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def load(lab):
    d = os.path.join(lab, "tools", "claims-v3", "dipterm")
    for ln in open(os.path.join(d, "SHA256SUMS-5")):
        h, f = ln.split()
        if sha(os.path.join(d, f)) != h:
            raise SystemExit(f"refused: {f} is not the file SHA256SUMS-5 lists")
    sys.path.insert(0, d)
    import dipterm as DT  # noqa: E402
    import dipterm_a1 as A1  # noqa: E402
    import score_dipterm_v4 as V4  # noqa: E402
    return DT, A1, V4


def dtn(DT, card, elig, seen):
    P0 = DT.PERIOD_PRIOR_MS[card][0]
    n, s = len(elig), float(sum(elig))
    e = {d: (s + n * d) / P0 for d in (0.0, 0.7, 1.2)}
    lo, hi = DT.pois_lo(e[0.0]), DT.pois_hi(e[1.2])
    return {"eligible_gaps": n, "expected_0_0.7_1.2": [round(e[0.0], 2), round(e[0.7], 2), round(e[1.2], 2)], "band_95": [lo, hi],
            "falls": seen, "verdict": "PASS" if lo <= seen <= hi else ("FAIL low" if seen < lo else "FAIL high")}


def pois_tail(DT, k, mu):
    """P(X >= k) for a Poisson mean mu"""
    return 1.0 - DT._pois_cdf(k - 1, mu)


def q132_rule(DT, procs, card):
    """Q132(g)'s kernel rule through DT-N's formula: exposure = structurally eligible gaps after a launch at >= 0.79 GHz;
    a fall = one of them whose next launch reads 0.55-0.62 GHz."""
    elig, seen = [], 0
    for p in procs:
        for g in DT.gaps(p, card):
            if g["stamp_gap"] >= 0 and g["after_first_beat"] and g["prev_ghz"] >= 0.79:
                elig.append(g["stamp_gap"])
                seen += 0.55 <= g["ghz"] <= 0.62
    return dtn(DT, card, elig, seen)


def a1_rule(A1, DT, procs, card):
    c = A1.count_rule(procs, card)
    elig = []
    for p in procs:
        for g in A1.gaps(p, card):
            if g["eligible"]:
                elig.append(g["stamp_gap"])
    out = dtn(DT, card, elig, c["observed_falls"])
    out["not_counted"] = len(c["registered_falls_not_counted"])
    out["processes_in_scope"] = c["processes_in_scope"]
    out["clear"] = sum(p["a1"]["clear"] for p in procs)
    return out


def registered_rule(DT, procs, card):
    c = DT.count_rule(procs, card)
    elig = [g["stamp_gap"] for p in procs for g in DT.gaps(p, card) if g["eligible"]]
    out = dtn(DT, card, elig, c["observed_falls"])
    out["falls_at_ineligible_gaps"] = sum(1 for p in procs for g in DT.gaps(p, card) if g["fell"] and not g["eligible"])
    return out


# ------------------------------------------------------------------ 1. Q132(g)'s six sessions
def q132_check(lab, DT, A1):
    out, tot = {}, {}
    for name, (card, dirs) in Q132.items():
        allp, burst = [], []
        for rel in dirs:
            sd = os.path.join(lab, D, rel)
            ps = A1.load_session(sd, None)
            allp += ps
        for p in allp:
            p["a1"]["in_scope"] = not p["a1"]["alarm"]
        burst = [p for p in allp if p["a1"]["block"] == "BURST"]
        rec = {"processes": len(allp), "burst_processes": len(burst), "registered": registered_rule(DT, allp, card),
               "q132_rule": q132_rule(DT, allp, card), "a1_all_blocks": a1_rule(A1, DT, allp, card),
               "registered_burst_only": registered_rule(DT, burst, card), "a1_burst_only": a1_rule(A1, DT, burst, card)}
        why = {}
        for x in A1.count_rule(allp, card)["registered_falls_not_counted"]:
            w = x["why"]
            k = ("inside the process's first heartbeat period" if "first heartbeat period" in w else
                 "an alarm step" if "alarm" in w else "a dither launch in a process that is not clear" if "not clear" in w else w)
            why[k] = why.get(k, 0) + 1
        rec["registered_falls_not_counted_by_A1"] = why
        out[name] = rec
        for k in ("registered", "q132_rule", "a1_all_blocks", "registered_burst_only", "a1_burst_only"):
            t = tot.setdefault(k, {"falls": 0, "e07": 0.0, "pass": 0})
            t["falls"] += rec[k]["falls"]
            t["e07"] += rec[k]["expected_0_0.7_1.2"][1]
            t["pass"] += rec[k]["verdict"] == "PASS"
    tw = {}
    for rec in out.values():
        for k, v in rec["registered_falls_not_counted_by_A1"].items():
            tw[k] = tw.get(k, 0) + v
    tot["registered_falls_not_counted_by_A1"] = tw
    for k, t in tot.items():
        if k == "registered_falls_not_counted_by_A1":
            continue
        t["e07"] = round(t["e07"], 2)
        t["P(X>=falls)"] = round(pois_tail(DT, t["falls"], t["e07"]), 4)
        t["P(X<=falls)"] = round(DT._pois_cdf(t["falls"], t["e07"]), 4)
    return {"sessions": out, "pooled": tot,
            "q132_statement": "Q132(g)'s README (13de3994), 'What the data show': 25 falls in six sessions against 23.5 expected "
                              "(2 ms in 1000.01 ms over 11,781 kernel boundaries at 800 MHz), 95% interval 16.2-36.9"}


# ------------------------------------------------------------------ 2. E100
def e100_check(lab, DT, A1):
    sd = os.path.join(lab, D, E100)
    procs = A1.load_session(sd, None)
    res = json.load(open(os.path.join(lab, D, os.path.dirname(E100), "results.json")))
    out, pooled = {}, {"registered": [0, 0.0], "a1": [0, 0.0]}
    for arm in ("A0", "A5", "A20", "A100", "N", "R"):
        pp = [p for p in procs if p["run"].split("-")[0] in (f"R1{arm}", f"R2{arm}")]
        r, a = registered_rule(DT, pp, "a2"), a1_rule(A1, DT, pp, "a2")
        ea = (res.get("arms") or {}).get(arm, {})
        out[arm] = {"processes": len(pp), "registered": r, "a1": a, "E100_registered_prediction_at_w2": ea.get("predicted_falls_at_w2"),
                    "E100_band": ea.get("band"), "E100_falls": ea.get("falls"), "E100_kernel_falls": ea.get("kernel_falls")}
        if arm != "N":
            for k, v in (("registered", r), ("a1", a)):
                pooled[k][0] += v["falls"]
                pooled[k][1] += v["expected_0_0.7_1.2"][1]
    for k, (f, e) in pooled.items():
        sd_ = math.sqrt(e) if e > 0 else None
        pooled[k] = {"falls": f, "expected_0.7": round(e, 2), "z": round((f - e) / sd_, 2) if sd_ else None,
                     "P(X>=falls)": round(pois_tail(DT, f, e), 4)}
    return {"arms": out, "pooled_gapped_arms_A0_A5_A20_A100_R": pooled}


# ------------------------------------------------------------------ 4. the period with and without the prior
def fit_noprior(cal, P0):
    c1 = cal[0][0]
    rows = [(round((c - c1) / P0), c, sd) for c, sd in cal]
    a11 = sum(1.0 / sd ** 2 for _, _, sd in rows)
    a12 = sum(k / sd ** 2 for k, _, sd in rows)
    a22 = sum(k * k / sd ** 2 for k, _, sd in rows)
    b1 = sum(c / sd ** 2 for _, c, sd in rows)
    b2 = sum(k * c / sd ** 2 for k, c, sd in rows)
    det = a11 * a22 - a12 * a12
    if len({k for k, _, _ in rows}) < 2 or det <= 0:
        return None, None
    return (a11 * b2 - a12 * b1) / det, math.sqrt(a11 / det)


def periods(DT, A1, procs, card):
    out = {}
    for label, use_a1 in (("registered falls", False), ("A1 falls", True)):
        cal = []
        for p in procs:
            for g in (A1.gaps(p, card) if use_a1 else DT.gaps(p, card)):
                if g["fell"]:
                    cal.append((0.5 * (g["lo"] + g["hi"]), math.sqrt((g["hi"] - g["lo"]) ** 2 / 12 + DT.SIGMA_Z_MS ** 2)))
        if len(cal) < 2:
            out[label] = {"falls": len(cal)}
            continue
        _, P, cov = DT.fit_lattice(cal, card)
        Pn, sn = fit_noprior(cal, DT.PERIOD_PRIOR_MS[card][0])
        out[label] = {"falls": len(cal), "with_prior_ms": [round(P, 5), round(math.sqrt(cov[1][1]), 5)],
                      "without_prior_ms": [round(Pn, 5), round(sn, 5)] if Pn else None, "prior_ms": list(DT.PERIOD_PRIOR_MS[card])}
    return out


def loo_residuals(DT, procs, card):
    """Each registered fall against the lattice fitted on the session's other registered falls (with the card's prior)."""
    falls = []
    for p in procs:
        for g in DT.gaps(p, card):
            if g["fell"]:
                falls.append((p["run"], g["i"], 0.5 * (g["lo"] + g["hi"]), math.sqrt((g["hi"] - g["lo"]) ** 2 / 12 + DT.SIGMA_Z_MS ** 2)))
    out = []
    for i, (run, gi, c, _) in enumerate(falls):
        others = [(cc, ss) for j, (_, _, cc, ss) in enumerate(falls) if j != i]
        if len(others) < 2:
            continue
        phi, P, cov = DT.fit_lattice(others, card)
        k = round((c - phi) / P)
        sd = math.sqrt(max(cov[0][0] + 2 * k * cov[0][1] + k * k * cov[1][1], 0.0))
        out.append({"run": run, "gap": gi, "residual_ms": round(c - (phi + k * P), 2), "lattice_sd_ms": round(sd, 2)})
    return out


def registered_at_a1_draws(lab, cfg, DT, A1, V4):
    """The registered rule, climb and calibration (dipterm.predict's arms) at A1-4's 8 x 500 draws: the study's seq and count
    figures without its one seed's Monte Carlo noise, beside A1's."""
    S1 = V4.S1
    sd = os.path.join(lab, D, cfg["dir"], cfg["sdir"])
    R = json.load(open(os.path.join(lab, D, cfg["dir"], "results.json")))
    procs = A1.load_session(sd, ("BURST",))
    tiles = R["score"]["reported"]["tiles"]
    by_tile = {}
    for r in R["run_rows"]:
        if r.get("counted"):
            by_tile.setdefault(S1.tile_of(r["label"]), []).append(r)
    pred = json.load(open(os.path.join(lab, cfg["pred"]))) if cfg.get("pred") else None
    rel = json.load(open(os.path.join(lab, REL)))["relation"] if cfg.get("board") else None
    f_ref, dP = {}, {}
    for r in R["run_rows"]:
        t = S1.tile_of(r["label"])
        m = (tiles.get(t) or {}).get("M10") or {}
        f_ref[r["run"]] = float(m.get("burst_mhz", 800.0))
        if rel is not None and cfg["card"] == "a2":
            dd = S1.d_of(pred, t)
            if dd and dd[0] is not None:
                dP[r["run"]] = DT.board_drops(rel, dd[1], dd[0], f_ref[r["run"]])
    out = {}
    rules = [("clock", cfg["clock"])] + ([("board", cfg["board"])] if cfg.get("board") else []) + \
            ([("clock", cfg["clock2"])] if cfg.get("clock2") else [])
    for arm in ("count", "seq"):
        pr = A1.predict(procs, cfg["card"], f_ref, dP if dP else None, arm, rule="registered", climbs="registered")
        P = {p["run"]: p for p in pr["processes"]}
        for kind, (rid, gset) in rules:
            f = V4.figures(R["score"]["rules"][rid], kind, gset, tiles, by_tile, P)
            out.setdefault(arm, {})[f"DT-{rid}"] = {k: f[k] for k in ("n", "rms", "mc_se_rms", "mean", "mc_se_mean", "verdict")}
    return out


# ------------------------------------------------------------------ 5. the SP pass under the 10 Hz sampler
def jl(p):
    for q in (p, p + ".gz"):
        if os.path.exists(q):
            break
    else:
        return []
    op = gzip.open if q.endswith(".gz") else open
    out = []
    with op(q, "rt") as f:
        for ln in f:
            ln = ln.strip()
            if ln.startswith("{"):
                try:
                    out.append(json.loads(ln))
                except ValueError:
                    pass
    return out


def sp_pass(sdir):
    """Per run: over its runs of consecutive 10 Hz samples at >= 800 MHz (at least 10 samples), the elapsed time over the
    number of board_w changes (the SP refreshes board_w once a pass). The median and p10/p90 over runs."""
    per = []
    tdir = os.path.join(sdir, "tel")
    for f in sorted(os.listdir(tdir)):
        s = sorted((int(d["t_ms"]), (d.get("mhz") or {}).get("minion"), d.get("board_w")) for d in jl(os.path.join(tdir, f.replace(".gz", "")))
                   if "t_ms" in d)
        el = ch = 0
        seg = []
        for row in s + [(None, None, None)]:
            if row[1] is not None and row[1] >= 800 and row[2] is not None:
                seg.append(row)
                continue
            if len(seg) >= 10:
                el += seg[-1][0] - seg[0][0]
                ch += sum(1 for a, b in zip(seg, seg[1:]) if a[2] != b[2])
            seg = []
        if ch >= 5:
            per.append(el / ch)
    per.sort()
    n = len(per)
    return {"runs": n, "median_ms": round(st.median(per), 1) if per else None,
            "p10_ms": round(per[n // 10], 1) if per else None, "p90_ms": round(per[9 * n // 10], 1) if per else None}


# ------------------------------------------------------------------ 6. what each fall cost its pass, registered and A1-5's climb
def fall_costs(lab, cfg, DT, A1, procs):
    R = json.load(open(os.path.join(lab, D, cfg["dir"], "results.json")))
    card = cfg["card"]
    byrun = {p["run"]: p for p in procs}
    tiles = R["score"]["reported"]["tiles"]
    rows = [r for r in R["run_rows"] if r.get("counted")]
    cal = []
    for p in procs:
        for g in A1.gaps(p, card):
            if g["fell"]:
                cal.append((0.5 * (g["lo"] + g["hi"]), math.sqrt((g["hi"] - g["lo"]) ** 2 / 12 + DT.SIGMA_Z_MS ** 2)))
    if not cal:
        return []
    phi, P, _ = DT.fit_lattice(cal, card)
    out = []
    for r in rows:
        p = byrun.get(r["run"])
        if p is None:
            continue
        fl = [g for g in A1.gaps(p, card) if g["fell"]]
        if not fl:
            continue
        t = r["label"].split("-", 1)[1]
        rec = tiles.get(t)
        others = [x for x in rows if x["label"] == r["label"] and x["run"] != r["run"]
                  and not any(g["fell"] for g in A1.gaps(byrun[x["run"]], card))]
        f_ref = float(rec["M10"]["burst_mhz"]) if rec else 800.0
        pp = A1.prep(p, card)
        lr, _, _ = A1.simulate(pp, phi, P, f_ref, DT.CLIMB_S[card], DT.CLIMB_S[card])
        la, _, _ = A1.simulate(pp, phi, P, f_ref, A1.CLIMB_START_S[card], A1.CLIMB_FALL_S[card])
        dr, _ = A1.deficits(p, lr, f_ref)
        da, _ = A1.deficits(p, la, f_ref)
        ref = (sum(float(x["burst_mhz"]) for x in others) / len(others)) if others else None
        out.append({"run": r["run"], "tile": t, "group": (rec.get("group") or rec.get("set") or "pinned") if rec else "other",
                    "fall_s_into_process": round((fl[0]["lo"] - p["t0"]) / 1000.0, 2), "f_ref_mhz": f_ref,
                    "cost_mhz_measured": round(ref - float(r["burst_mhz"]), 2) if ref is not None else None,
                    "cost_mhz_term_registered_climb": round(dr, 2), "cost_mhz_term_a1_climb": round(da, 2)})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lab", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    lab = os.path.abspath(a.lab)
    DT, A1, V4 = load(lab)
    out = {"label": "POST HOC (the data existed before A1, 3002edaf; A1's rule was chosen after reading the verifier's Q132(g) check "
                    "and E173-E175's rings)",
           "sha256": {"dipterm.py": sha(os.path.join(lab, "tools/claims-v3/dipterm/dipterm.py")),
                      "dipterm_a1.py": sha(os.path.join(lab, "tools/claims-v3/dipterm/dipterm_a1.py")),
                      "score_dipterm_v4.py": sha(os.path.join(lab, "tools/claims-v3/dipterm/score_dipterm_v4.py"))},
           "Q132g_check": q132_check(lab, DT, A1), "E100_check": e100_check(lab, DT, A1), "sessions": {}}
    cache = {}
    for name, cfg in SESSIONS.items():
        sd = os.path.join(lab, D, cfg["dir"], cfg["sdir"])
        ns = argparse.Namespace(session=sd, results=os.path.join(lab, D, cfg["dir"], "results.json"), card=cfg["card"], blocks="BURST",
                                clock_rule=cfg["clock"][0], clock_set=cfg["clock"][1],
                                board_rule=cfg["board"][0] if cfg["board"] else None, board_set=cfg["board"][1] if cfg["board"] else "pinned",
                                predictions=os.path.join(lab, cfg["pred"]) if cfg["pred"] else None,
                                relation=os.path.join(lab, REL) if cfg["board"] else None,
                                arms="none,count,seq,oracle,seq-gc,seq-lag" if cfg["board"] else "none,count,seq,oracle,seq-gc", out=None)
        rec = {"score": V4.score(ns, cache)}
        if cfg.get("clock2"):
            ns2 = argparse.Namespace(**dict(vars(ns), clock_rule=cfg["clock2"][0], clock_set=cfg["clock2"][1], board_rule=None,
                                            arms="none,count,seq,oracle,seq-gc"))
            s2 = V4.score(ns2, cache)
            rec["score_clock2"] = {arm: v.get(f"DT-{cfg['clock2'][0]}") for arm, v in s2["arms"].items()}
        procs = A1.load_session(sd, ("BURST",))
        rec["registered_rule_at_a1_draws"] = registered_at_a1_draws(lab, cfg, DT, A1, V4)
        rec["loo_residuals_registered_falls"] = loo_residuals(DT, procs, cfg["card"])
        rec["periods"] = periods(DT, A1, procs, cfg["card"])
        rec["sp_pass_10hz"] = sp_pass(sd)
        rec["fall_costs"] = fall_costs(lab, cfg, DT, A1, procs)
        out["sessions"][name] = rec
    open(a.out, "w").write(json.dumps(out, indent=1, sort_keys=True) + "\n")
    # the printed summary
    print(out["label"])
    q = out["Q132g_check"]
    print("\n1. Q132(g)'s six sessions: falls / expected at delta 0, 0.7, 1.2 ms / band: verdict")
    for name, rec in q["sessions"].items():
        print(f"  {name} ({rec['processes']} processes, {rec['burst_processes']} in burst blocks)")
        for k in ("registered", "q132_rule", "a1_all_blocks", "registered_burst_only", "a1_burst_only"):
            v = rec[k]
            print(f"     {k:22s} gaps {v['eligible_gaps']:5d}  falls {v['falls']:3d}  expected {v['expected_0_0.7_1.2']}  band {v['band_95']}  {v['verdict']}"
                  + (f"  (not counted {v['not_counted']}, clear {v['clear']} of {v['processes_in_scope']} in scope)" if "not_counted" in v else "")
                  + (f"  (falls at ineligible gaps {v['falls_at_ineligible_gaps']})" if "falls_at_ineligible_gaps" in v else ""))
        print(f"     the registered rule's falls A1 does not count, by reason: {rec['registered_falls_not_counted_by_A1']}")
    print("  pooled: " + json.dumps(q["pooled"]))
    print("  " + q["q132_statement"])
    e = out["E100_check"]
    print("\n2. E100, arm by arm")
    for arm, v in e["arms"].items():
        print(f"  {arm:4s} registered: {v['registered']['falls']} falls, {v['registered']['expected_0_0.7_1.2']} expected, {v['registered']['verdict']};"
              f"  A1: {v['a1']['falls']} falls, {v['a1']['expected_0_0.7_1.2']} expected, {v['a1']['verdict']} (clear {v['a1']['clear']} of {v['processes']});"
              f"  E100's prediction {v['E100_registered_prediction_at_w2']} in {v['E100_band']}, falls {v['E100_falls']} (kernel {v['E100_kernel_falls']})")
    print("  pooled over A0, A5, A20, A100 and R: " + json.dumps(e["pooled_gapped_arms_A0_A5_A20_A100_R"]))
    for name, rec in out["sessions"].items():
        sc = rec["score"]
        n, nr = sc["DT-N"], sc["DT-N_registered_for_reference"]
        print(f"\n== {name} ({sc['card']}): {sc['processes']} processes, {sc['scope']['in_scope']} in scope, {sc['scope']['clear']} clear")
        print(f"  3. DT-N (A1): gaps {n['eligible_gaps']}, expected {n['expected']}, band {n['band_95']}, falls {n['observed_falls']}: {n['verdict']}")
        print(f"     falls: {[(x['run'][:30], x['gap'], round(x['prev_ghz'], 3), x['by']) for x in n['falls']]}")
        print(f"     registered falls not counted: {[(x['run'][:30], x['gap'], round(x['prev_ghz'], 3), x['why']) for x in n['registered_falls_not_counted']]}")
        print(f"     registered DT-N, for reference: gaps {nr['eligible_gaps']}, expected {nr['expected']}, band {nr['band_95']}, falls {nr['observed_falls']}: {nr['verdict']}")
        if "DT-L" in sc:
            l_ = sc["DT-L"]
            print(f"     DT-L (A1): first fall in {sc['calibration']['first_run']}; later falls {l_['later_falls']}, sensitivity {l_['sensitivity']}, "
                  f"PPV {l_['ppv']}: {l_['verdict']}; P at each later fall {[x['p'] for x in l_['later']]}; skipped as first {sc['calibration']['first_skipped']}; "
                  f"off lattice {sc['calibration']['off_lattice']}")
        for arm, v in sc["arms"].items():
            rules = {k: (v[k]["rms"], v[k]["mc_se_rms"], v[k]["mean"], v[k]["mc_se_mean"], v[k]["verdict"], v[k]["near_line"])
                     for k in v if k.startswith("DT-")}
            print(f"     {arm:7s} falls expected {v['falls_expected']:6.2f}, late climbs {v['late_climbs_expected']:5.2f}  {rules}")
        if rec.get("score_clock2"):
            print(f"     {SESSIONS[name]['clock2'][0]}: " + str({arm: (x['rms'], x['mc_se_rms'], x['mean'], x['verdict']) for arm, x in rec['score_clock2'].items() if x}))
        print(f"     the registered rule at A1-4's draws (the study's arms without its one seed's noise): {json.dumps(rec['registered_rule_at_a1_draws'])}")
        print(f"     each registered fall against the lattice of the session's other falls: {json.dumps(rec['loo_residuals_registered_falls'])}")
        print(f"  4. periods: {json.dumps(rec['periods'])}")
        print(f"  5. SP pass under the 10 Hz sampler (mean time between board_w changes at 800 MHz, per run): {rec['sp_pass_10hz']}")
        print("  6. fall costs (MHz): measured, the term with the registered climb, with A1-5's")
        for x in rec["fall_costs"]:
            print(f"     {x['tile'][:36]:36s} {x['group']:8s} at {x['fall_s_into_process']:5.2f} s: {x['cost_mhz_measured']}, "
                  f"{x['cost_mhz_term_registered_climb']}, {x['cost_mhz_term_a1_climb']}")


if __name__ == "__main__":
    main()
