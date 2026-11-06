#!/usr/bin/env python3
"""Q145(b): the dip term (tools/claims-v3/dipterm, registered in 7a099fb9) on committed sessions. POST HOC, every figure:
the data of E173, E174, E175 and E100 existed before the term was registered. Desk only, no card.

    python3 posthoc_dips_q145b.py --root <the lab tree> --out posthoc-dips.json > posthoc-dips.txt

1. The term's own check against an earlier measurement of the same quantity at the same operating point: DT-N's formula,
   arm by arm, on E100's committed session (aifoundry2, 800 MHz), against E100's registered predictions and its falls.
2. The mechanism's timing re-derived from E173-E175's committed records: each session's period from its own falls (the
   lattice fitted on all of them) and from the rings' POWER_IDLE records on the SP's tick; a fall's length at 600 and 700 MHz
   from the 10 Hz telemetry; the late climbs; where each fall sits in its zone; the rings' POWER_IDLE record behind each fall.
3. The count (DT-N) and the in-session calibration (DT-L) on E173, E174 and E175.
4. F2 (E173), C0-F (E174), G and F2 (E175), and Bp (E173, E175) re-scored with the term: arms none (the committed verdict,
   reproduced), count, seq and oracle; beside them the reference figures that drop the dipped passes (selection on the outcome).
5. What each fall cost its pass, measured against the same tile's passes with no fall, and the term's cost for that pass on the
   lattice fitted on all of the session's falls.
It imports the registered dipterm.py and the scorer's v2 (score_dipterm_v2.py, the registration's dated note 1) after checking
them against SHA256SUMS and SHA256SUMS-1.
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

SESSIONS = {
    "E173": {"dir": "docs/reports/data/2026-11-05-e173-blind8-aifoundry2", "sdir": "aifoundry2/s1", "card": "a2",
             "clock": ("P8-A2-F2", "pinned"), "board": ("P8-A2-Bp", "pinned"),
             "pred": "tools/claims-v3/kinds/blind8/predictions-pool8-aifoundry2.json"},
    "E174": {"dir": "docs/reports/data/2026-11-05-e174-blind8-card0", "sdir": "aifoundry1-c0/s1", "card": "c0",
             "clock": ("P8-C0-F", "all"), "board": None, "pred": None},
    "E175": {"dir": "docs/reports/data/2026-11-05-e175-governed-aifoundry2", "sdir": "aifoundry2/s1", "card": "a2",
             "clock": ("E175-A2-G", "governed"), "board": ("E175-A2-Bp", "pinned"),
             "pred": "tools/claims-v3/e175/predictions-e175.json", "clock2": ("E175-A2-F2", "pinned")},
}
REL = "docs/reports/data/2026-11-04-q140l-a2-session-terms/m9_a2.json"
E100 = "docs/reports/data/2026-11-01-e100-idle-reset"
Q132 = "docs/reports/data/2026-11-01-q132-governor-desk"


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def load_term(root):
    d = os.path.join(root, "tools", "claims-v3", "dipterm")
    for ln in open(os.path.join(d, "SHA256SUMS")):
        h, f = ln.split()
        if sha(os.path.join(d, f)) != h:
            raise SystemExit(f"refused: {f} is not the registered file")
    sys.path.insert(0, d)
    for ln in open(os.path.join(d, "SHA256SUMS-1")):
        h, f = ln.split()
        if sha(os.path.join(d, f)) != h:
            raise SystemExit(f"refused: {f} is not the file of dated note 1")
    import dipterm as DT  # noqa: E402
    import score_dipterm_v2 as SD  # noqa: E402  (dated note 1: the scorer's v2)
    SD.DT_SHA = sha(os.path.join(d, "dipterm.py"))
    return DT, SD


def jl(p):
    """JSON lines; a line that is not JSON (the sampler's own messages) is skipped, as reduce_hpl.tel skips it"""
    with gzip.open(p, "rt") if p.endswith(".gz") else open(p) as f:
        for ln in f:
            ln = ln.strip()
            if not ln.startswith("{"):
                continue
            try:
                yield json.loads(ln)
            except ValueError:
                continue


# ------------------------------------------------------------------ 1. E100, arm by arm
def e100_check(root, DT):
    sdir = os.path.join(root, E100, "s1")
    procs = DT.load_session(sdir)
    res = json.load(open(os.path.join(root, E100, "results.json")))
    out = {}
    for arm in ("A0", "A5", "A20", "A100", "N", "R"):
        pp = [p for p in procs if p["run"].split("-")[0] in (f"R1{arm}", f"R2{arm}")]
        c = DT.count_rule(pp, "a2")
        a = (res.get("arms") or {}).get(arm, {})
        out[arm] = {"processes": len(pp), "eligible_gaps": c["eligible_gaps"], "stamp_gap_ms_mean": c["stamp_gap_ms_mean"],
                    "DT-N_expected": c["expected"], "DT-N_band": c["band_95"], "DT-N_falls_kernel_rule": c["observed_falls"],
                    "DT-N_verdict": c["verdict"],
                    "E100_falls": a.get("falls"), "E100_kernel_falls": a.get("kernel_falls"),
                    "E100_predicted_at_w2": a.get("predicted_falls_at_w2"), "E100_band": a.get("band"),
                    "E100_heartbeats": a.get("heartbeats")}
    return out


# ------------------------------------------------------------------ 2. timing
def fit_ring(ts_us, ir_lib):
    f = ir_lib.fit_lattice(ts_us)
    res = sorted(x / 1000.0 for x in f["res_us"])
    n = len(res)
    return {"records": n, "period_us": round(f["q_us"], 2), "R": round(f["R"], 4),
            "res_ms_p10_p50_p90": [round(res[n // 10], 1), round(res[n // 2], 1), round(res[9 * n // 10], 1)]}


def timing(root, name, cfg, DT, sp, ir_lib):
    sdir = os.path.join(root, cfg["dir"], cfg["sdir"])
    card = cfg["card"]
    procs = DT.load_session(sdir)
    P0 = DT.PERIOD_PRIOR_MS[card][0]
    falls = []
    for pi, p in enumerate(procs):
        for g in DT.gaps(p, card):
            if g["fell"]:
                falls.append((pi, p, g))
    out = {"falls": len(falls)}
    if falls:
        cal = [(0.5 * (g["lo"] + g["hi"]), math.sqrt((g["hi"] - g["lo"]) ** 2 / 12 + DT.SIGMA_Z_MS ** 2)) for _, _, g in falls]
        phi, P, cov = DT.fit_lattice(cal, card)
        out["period_from_falls_ms"] = round(P, 5)
        out["period_sd_ms"] = round(math.sqrt(cov[1][1]), 5)
        out["prior_ms"] = DT.PERIOD_PRIOR_MS[card]
        span_beats = round((cal[-1][0] - cal[0][0]) / P)
        out["falls_span_beats"] = span_beats
        pos = []
        for (pi, p, g), (c, sd) in zip(falls, cal):
            k = round((c - phi) / P)
            h = phi + k * P
            pos.append({"run": p["run"], "gap": g["i"], "stamp_gap_ms": g["stamp_gap"],
                        "lattice_minus_zone_lo_ms": round(h - g["lo"], 2), "zone_hi_minus_lattice_ms": round(g["hi"] - h, 2),
                        "s_into_process": round((g["lo"] - p["t0"]) / 1000.0, 2)})
        out["falls_in_zone"] = pos
        # the lattice's own gaps: every eligible gap with the fitted lattice point inside its zone, and whether it fell
        hit_fell = hit_no = miss_fell = 0
        for pi, p in enumerate(procs):
            for g in DT.gaps(p, card):
                if not g["eligible"]:
                    continue
                k = round((0.5 * (g["lo"] + g["hi"]) - phi) / P)
                h = phi + k * P
                inz = g["lo"] <= h <= g["hi"]
                hit_fell += inz and g["fell"]
                hit_no += inz and not g["fell"]
                miss_fell += (not inz) and g["fell"]
        out["in_sample_lattice_table"] = {"point_in_zone_fell": hit_fell, "point_in_zone_no_fall": hit_no,
                                          "no_point_fell": miss_fell,
                                          "note": "in sample: the lattice is fitted on these falls (Q132(g)'s caveat)"}
    # the fall's length from the 10 Hz telemetry: first 600 reading after the gap, first 700 and first 800 after that
    lens6, lens7 = [], []
    for pi, p, g in falls:
        tf = os.path.join(sdir, "tel", p["run"] + ".jsonl.gz")
        if not os.path.exists(tf):
            continue
        s = sorted((int(d["t_ms"]), (d.get("mhz") or {}).get("minion")) for d in jl(tf) if "t_ms" in d)
        t0 = g["lo"]
        a = next((t for t, f in s if t >= t0 - 50 and f == 600), None)
        if a is None:
            continue
        b7 = next((t for t, f in s if t > a and f is not None and f > 600), None)
        b8 = next((t for t, f in s if b7 is not None and t >= b7 and f is not None and f >= 800), None)
        if b7 is not None:
            lens6.append((b7 - a) / 1000.0)
        if b7 is not None and b8 is not None:
            lens7.append((b8 - b7) / 1000.0)
    out["fall_600_s"] = {"n": len(lens6), "median": round(st.median(lens6), 3) if lens6 else None,
                         "min": min(lens6) if lens6 else None, "max": max(lens6) if lens6 else None}
    out["fall_700_s"] = {"n": len(lens7), "median": round(st.median(lens7), 3) if lens7 else None}
    # late climbs from the telemetry: the first 800 MHz reading after the process start later than the window's opening
    late, first8 = [], []
    for p in procs:
        tf = os.path.join(sdir, "tel", p["run"] + ".jsonl.gz")
        if not os.path.exists(tf):
            continue
        s = sorted((int(d["t_ms"]), (d.get("mhz") or {}).get("minion")) for d in jl(tf) if "t_ms" in d)
        f8 = next((t for t, f in s if t >= p["launches"][0][1] and f is not None and f >= 800), None)
        if f8 is None:
            continue
        x = (f8 - p["t0"]) / 1000.0
        first8.append(x)
        if x > DT.BURST_FROM_S:
            late.append({"run": p["run"], "first_800_s": round(x, 2)})
    out["first_800_s_after_start"] = {"n": len(first8), "median": round(st.median(first8), 3) if first8 else None,
                                      "max": round(max(first8), 2) if first8 else None}
    out["late_climbs_seen"] = late
    # the rings: POWER_IDLE records (throttle state 0) on the SP's tick, per run's dump, and the session's lattice on them
    spd = os.path.join(sdir, "sp")
    prev = None
    idle_ts, per_run = [], {}
    if os.path.isdir(spd):
        names = {p["run"] for p in procs}
        files = sorted(f for f in os.listdir(spd) if f.endswith(".bin") and f[:-4] in names)
        order = {p["run"]: p["launches"][0][1] for p in procs}
        files.sort(key=lambda f: order.get(f[:-4], 0))
        for f in files:
            cur = sp.scan(open(os.path.join(spd, f), "rb").read()) or []
            new = sp.since(prev, cur) if prev is not None else cur
            prev = cur
            ids = [e["ts"] for e in new if e.get("kind") == "pstat" and e.get("throttle_state") == 0]
            per_run[f[:-4]] = len(ids)
            idle_ts += ids
        idle_ts = sorted(set(idle_ts))
        if len(idle_ts) >= 10:
            out["ring_lattice_sp_tick"] = fit_ring(idle_ts, ir_lib)
        fell_runs = {p["run"] for _, p, _ in falls}
        a = [per_run[r] for r in per_run if r in fell_runs]
        b = [per_run[r] for r in per_run if r not in fell_runs]
        out["ring_power_idle_per_run"] = {"runs_with_a_fall": {"n": len(a), "records": dict(sorted({x: a.count(x) for x in a}.items()))},
                                          "runs_without": {"n": len(b), "records": dict(sorted({x: b.count(x) for x in b}.items()))}}
    return out


# ------------------------------------------------------------------ 5. what each fall cost its pass, against the term's cost
def fall_costs(root, cfg, DT):
    """Each fall's pass: its window clock and board against the mean of the same tile's passes with no fall, and the term's
    deficit for that pass on the lattice fitted on all of the session's falls (deterministic, the fit's mean)."""
    R = json.load(open(os.path.join(root, cfg["dir"], "results.json")))
    card = cfg["card"]
    procs = DT.load_session(os.path.join(root, cfg["dir"], cfg["sdir"]))
    byrun = {p["run"]: p for p in procs}
    tiles = R["score"]["reported"]["tiles"]
    rows = [r for r in R["run_rows"] if r.get("counted")]
    cal = []
    for p in procs:
        for g in DT.gaps(p, card):
            if g["fell"]:
                cal.append((0.5 * (g["lo"] + g["hi"]), math.sqrt((g["hi"] - g["lo"]) ** 2 / 12 + DT.SIGMA_Z_MS ** 2)))
    if not cal:
        return []
    phi, P, _ = DT.fit_lattice(cal, card)
    rel = json.load(open(os.path.join(root, REL)))["relation"] if card == "a2" else None
    pred = json.load(open(os.path.join(root, cfg["pred"]))) if cfg.get("pred") else None
    out = []
    for r in rows:
        p = byrun.get(r["run"])
        if p is None or not any(g["fell"] for g in DT.gaps(p, card)):
            continue
        t = r["label"].split("-", 1)[1]
        rec = tiles.get(t)
        others = [x for x in rows if x["label"] == r["label"] and x["run"] != r["run"]
                  and not any(g["fell"] for g in DT.gaps(byrun[x["run"]], card))]
        f_ref = float(rec["M10"]["burst_mhz"]) if rec else 800.0
        dp = None
        if rel is not None and pred is not None:
            tt = (pred.get("tiles") or {}).get(t)
            if tt:
                m = tt.get("M10") or (tt.get("models") or {}).get("M10") or {}
                if m.get("D600_a3_footing_w") is not None:
                    dp = DT.board_drops(rel, tt.get("type") or t.split(".", 1)[0], m["D600_a3_footing_w"], f_ref)
        lows, fell, c0 = DT.simulate(p, card, phi, P, f_ref)
        dc, db = DT.deficits(p, lows, f_ref, dp)
        g = [x for x in DT.gaps(p, card) if x["fell"]][0]
        ref_mhz = (sum(float(x["burst_mhz"]) for x in others) / len(others)) if others else None
        ref_w = (sum(float(x["burst_w"]) for x in others) / len(others)) if others else None
        out.append({"run": r["run"], "tile": t, "scored": rec is not None,
                    "group": (rec.get("group") or rec.get("set") or "pinned") if rec else ("anchor" if "anchor" in t else "other"),
                    "pass": r["pass"], "fall_s_into_process": round((g["lo"] - p["t0"]) / 1000.0, 2), "f_ref_mhz": f_ref,
                    "pass_mhz": r["burst_mhz"], "other_passes_mhz": round(ref_mhz, 2) if ref_mhz is not None else None,
                    "cost_mhz_measured": round(ref_mhz - float(r["burst_mhz"]), 2) if ref_mhz is not None else None,
                    "cost_mhz_term": round(dc, 2), "term_fell_here": g["i"] in fell,
                    "pass_w": r["burst_w"], "cost_w_measured": round(ref_w - float(r["burst_w"]), 3) if ref_w is not None else None,
                    "cost_w_term": round(db, 3) if dp is not None else None})
    return out


# ------------------------------------------------------------------ 4. the reference figures that drop dipped passes
def dropped(root, cfg, DT, rid, gset):
    R = json.load(open(os.path.join(root, cfg["dir"], "results.json")))
    procs = DT.load_session(os.path.join(root, cfg["dir"], cfg["sdir"]))
    fell = {p["run"] for p in procs if any(g["fell"] for g in DT.gaps(p, cfg["card"]))}
    tiles = R["score"]["reported"]["tiles"]
    rows = [r for r in R["run_rows"] if r.get("counted")]
    out = {}
    for label, keep in (("every pass with a fall dropped", lambda r: r["run"] not in fell),
                        ("every tile with a dipped pass (< 799 MHz) dropped", None)):
        errs = []
        for t, rec in tiles.items():
            if gset != "all" and (rec.get("group") or rec.get("set") or "pinned") != gset:
                continue
            rr = [r for r in rows if r["label"].split("-", 1)[1] == t]
            if keep is None:
                if gset != "pinned" and gset != "all":
                    continue
                if any(float(r["burst_mhz"]) < 799.0 for r in rr):
                    continue
            else:
                rr = [r for r in rr if keep(r)]
            if not rr:
                continue
            errs.append(sum(float(r["burst_mhz"]) for r in rr) / len(rr) - float(rec["M10"]["burst_mhz"]))
        if errs:
            out[label] = {"n": len(errs), "rms": round(DT.rms(errs), 4), "mean": round(DT.mean(errs), 4)}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    root = os.path.abspath(a.root)
    DT, SD = load_term(root)
    sys.path.insert(0, os.path.join(root, "tools", "claims-v3", "hpl"))
    import sptrace_full as sp  # noqa: E402
    sys.path.insert(0, os.path.join(root, Q132))
    import ir_lib  # noqa: E402
    out = {"label": "POST HOC (the term was registered in 7a099fb9 after these sessions' data existed)",
           "dipterm_sha256": SD.DT_SHA, "E100_check": e100_check(root, DT), "sessions": {}}
    for name, cfg in SESSIONS.items():
        rec = {"timing": timing(root, name, cfg, DT, sp, ir_lib)}
        ns = argparse.Namespace(session=os.path.join(root, cfg["dir"], cfg["sdir"]), results=os.path.join(root, cfg["dir"], "results.json"),
                                card=cfg["card"], clock_rule=cfg["clock"][0], clock_set=cfg["clock"][1],
                                board_rule=cfg["board"][0] if cfg["board"] else None, board_set=cfg["board"][1] if cfg["board"] else "pinned",
                                predictions=os.path.join(root, cfg["pred"]) if cfg["pred"] else None,
                                relation=os.path.join(root, REL) if cfg["board"] else None, arms="none,count,seq,oracle")
        rec["score"] = SD.score(ns)
        if cfg.get("clock2"):
            ns2 = argparse.Namespace(**dict(vars(ns), clock_rule=cfg["clock2"][0], clock_set=cfg["clock2"][1], board_rule=None))
            s2 = SD.score(ns2)
            rec["score_clock2"] = {arm: v.get(f"DT-{cfg['clock2'][0]}") for arm, v in s2["arms"].items()}
        rec["dropped_reference"] = dropped(root, cfg, DT, cfg["clock"][0], cfg["clock"][1])
        rec["fall_costs"] = fall_costs(root, cfg, DT)
        out["sessions"][name] = rec
    s = json.dumps(out, indent=1, sort_keys=True)
    open(a.out, "w").write(s + "\n")
    # the printed summary
    print(out["label"])
    print("\n1. DT-N's formula on E100's committed session (aifoundry2, 800 MHz), arm by arm")
    for arm, v in out["E100_check"].items():
        print(f"  {arm:4s} procs {v['processes']:3d} eligible gaps {v['eligible_gaps']:5d} (stamp gap {v['stamp_gap_ms_mean']} ms)  "
              f"expected {v['DT-N_expected']}  band {v['DT-N_band']}  falls (kernel rule) {v['DT-N_falls_kernel_rule']}  {v['DT-N_verdict']}  | "
              f"E100: falls {v['E100_falls']} (kernel {v['E100_kernel_falls']}), predicted {v['E100_predicted_at_w2']} in {v['E100_band']}")
    for name, rec in out["sessions"].items():
        t, sc = rec["timing"], rec["score"]
        print(f"\n== {name} ({SESSIONS[name]['card']})")
        print(f"  2. period from its {t['falls']} falls: {t.get('period_from_falls_ms')} ms (sd {t.get('period_sd_ms')}; prior {t.get('prior_ms')}), "
              f"spanning {t.get('falls_span_beats')} beats; ring lattice on the SP tick {t.get('ring_lattice_sp_tick')}")
        print(f"     fall at 600 MHz {t['fall_600_s']}, at 700 MHz {t['fall_700_s']}; first 800 reading after the process start "
              f"{t['first_800_s_after_start']}; late climbs seen {len(t['late_climbs_seen'])}: {t['late_climbs_seen']}")
        print(f"     falls in their zones: {[ (x['lattice_minus_zone_lo_ms'], x['zone_hi_minus_lattice_ms']) for x in t.get('falls_in_zone', [])]}")
        print(f"     in-sample lattice table {t.get('in_sample_lattice_table')}; ring POWER_IDLE per run {t.get('ring_power_idle_per_run')}")
        n = sc["DT-N"]
        print(f"  3. DT-N: eligible gaps {n['eligible_gaps']} (stamp gap {n['stamp_gap_ms_mean']} ms), expected {n['expected']}, band {n['band_95']}, "
              f"falls {n['observed_falls']}: {n['verdict']}")
        if "DT-L" in sc:
            l_ = sc["DT-L"]
            print(f"     DT-L: later falls {l_['later_falls']}, sensitivity {l_['sensitivity']}, PPV {l_['ppv']}: {l_['verdict']}; "
                  f"P at each later fall {[x['p'] for x in l_['later']]}; off lattice {sc.get('off_lattice')}")
        print("  4. the rules with the term")
        for arm, v in sc["arms"].items():
            rules = {k: (v[k]["rms"], v[k]["mean"], v[k]["verdict"]) for k in v if k.startswith("DT-")}
            print(f"     {arm:7s} falls expected {v['falls_expected']:6.2f}, late climbs {v['late_climbs_expected']:5.2f}  {rules}")
        if rec.get("score_clock2"):
            print(f"     {SESSIONS[name]['clock2'][0]}: " + str({arm: (x['rms'], x['mean'], x['verdict']) for arm, x in rec['score_clock2'].items() if x}))
        print(f"     reference, selected on the outcome: {rec['dropped_reference']}")
        print("  5. what each fall cost its pass (the tile's other passes with no fall as the reference) against the term's cost")
        for x in rec["fall_costs"]:
            print(f"     {x['tile'][:34]:34s} {x['group']:8s} pass {x['pass']} fall at {x['fall_s_into_process']:5.2f} s: "
                  f"{x['pass_mhz']} against {x['other_passes_mhz']} MHz, cost {x['cost_mhz_measured']} measured, {x['cost_mhz_term']} term"
                  f"{'' if x['term_fell_here'] else ' (the fitted lattice puts no fall in this gap)'}; board {x['cost_w_measured']} W measured, "
                  f"{x['cost_w_term']} term")


if __name__ == "__main__":
    main()
