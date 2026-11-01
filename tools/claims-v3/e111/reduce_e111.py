#!/usr/bin/env python3
"""E111 (Q133): the registered reduction and scorer. Frozen with the pre-registration, before the claim and the first launch.

    python3 tools/claims-v3/e111/reduce_e111.py <DATA> [--out results.json] [--e98 <E98 DATA>] > reduce.txt

<DATA> holds W1/ W2/ END/ (run_e111.py sessions), CAM/ and CAM-ANA/lockin.json (run_hlc.py's session and lockin_hlf.py's
output), queue.jsonl, phone.jsonl and history/<box>-<UTC date>.jsonl[.gz], the boxes' own 5 s records. <E98 DATA> is E98's
committed data directory (docs/reports/data/2026-11-01-e98-heat-path-drift), read for its probes. Epoch ms throughout.
Standard library only, plus the lab's reduce_hpl.py, reduce_kspeed.py and E98's reduce_e98.py, imported unchanged.

PART A, THE STEADY STATE (E111-A1..A3; A4 the inlet proxies, beside). Two holds: H-I8, the int8 neg_ones hold of W1 (190 processes
of 8 s from E98's 57 C gate, 800 MHz), and H-F32, the fp32 randn hold of W2 (190 processes straight after E98's hold, under the
card's governor, at the 600 MHz floor). For each, over its work samples (inside kernel launches):
  * the plateau: the last 300 s; the previous window: the 300 s before it. Die (the firmware's whole-degree minshire mean), board W,
    clock, the share at the hold's clock, and the fine W: the mean over samples at the hold's clock with each idle-reset dip and the 3 s
    after it left out (E98's rule), existing only with at least 70% of the window left.
  * E111-A1, steady?: the OLS slope of 30 s bins of the fine W over the last 600 s, in C/min at k = 0.442 W/C (E64's, frozen).
    PASS if |slope| <= 0.02 C/min (E97-B1's bar), else FAIL. Without a fine W (the clock not held), the die's own 30 s bins stand in,
    and the verdict says so. The die's slope is printed beside either way.
  * the idle: the 60 s at the end of the REST block before the hold's step (idle before) and of the next step's REST block (idle after:
    W2's for H-I8, END's for H-F32), 10 Hz, die and board W.
  * E111-A2, the coefficient c = (plateau die - idle die) / (plateau W - idle W), per board W, open loop (the leakage is in the watts).
    Its range: every combination of {idle before, idle after, their mean} with {the plateau, the previous window}. Against each band of
    predictions-e111.json: PASS if the range lies inside, FAIL if it lies wholly outside, INCONCLUSIVE otherwise. Bands: aifoundry2's
    near-steady readings [0.62, 0.82] (predicted PASS); the lab's September model [1.25, 1.70], E97's aifoundry3 plateau [0.86, 0.95]
    and the 76 s line [0.40, 0.52] (each predicted FAIL).
  * E111-A3, linear in power: c(H-F32) / c(H-I8), its range from the two ranges' extremes, against [0.90, 1.11]: PASS inside, FAIL
    wholly outside, INCONCLUSIVE otherwise (predicted PASS).
  * beside, labelled: an exponential's asymptote of the fine W over the hold after its first 120 s (tau on a grid, 60-5000 s), the
    die it implies at k, and c at the asymptote; the inlet proxies (A4) below.
  * E111-A4, the inlet proxies (beside the holds, never a verdict): from the boxes' history, in three 300 s windows (ending at the
    idle-before REST's end, the plateau, ending at the idle-after REST's end), rows with load under 2: aifoundry1's and aifoundry3's NIC
    and NVMe, every card that is free (not held, W under its idle bar; either card held blanks aifoundry1's cards), aifoundry2's own NIC
    and NVMe in the idle windows only; and the phone's battery reading (it charges: descriptive). For each proxy, its move from the
    idle mean to the plateau, in C of aifoundry2 rest die by E98's nine-day relation, and c with the rise corrected by it.
PART B, THE DRIFT (E111-B0..B4). E98's own reading of a probe (reduce_e98.read_probe, unchanged) on E98's probes P1, P2, P3, P6, P7
and on W1 and W2, with W1's hold read as E98 reads a hold, on its first 39 processes (the 120 s ending with process 39). E98's
scoring with its labelled arms and proxies, copied here verbatim as score98() and checked against E98's committed results.json on E98's
probes alone (the scorer refuses to score if they differ), then run on all of them:
  * E111-B0, the gate: E98-R0's gate on the combined probes (at least 4 counted, rest-die range at least 0.75 C).
  * E111-B1 = E98-R1 on the combined probes (the 76 s line against the rest die, against 0 and 0.25).
  * E111-B2 = E98-R2 on the combined probes (the hold's die against the rest die, band 1.00-1.25, floor 0.25); E111-BV = E98-V of B1, B2.
  * E111-B3, does P1's lead repeat? Each warm probe W against the mean of P3, P6, P7: its rest-die lead dx (W-derived, as E98), its
    hold-die lead and its line lead, each over dx. A warm probe has dx >= 0.5 C. Over the warm probes, the mean of each ratio with a
    95% normal interval from E98's frozen per-probe scatter (hold 0.375 C, line 0.089 C, one probe against a mean of three). The hold:
    E98-R2's partition (band 1.00-1.25, floor 0.25); the line: E98-R1's (against 0 and 0.25). Whether P1's own 2.25 (hold) and 0.52
    (line) lie inside is printed beside. No warm probe: UNDER-RESOLVED.
  * E111-B4 = E98-S4 on the combined probes (fp16 ones at the trip: MHz and W against the rest die).
PART C, THE CAMERA BELOW 0.01 Hz (E111-C1..C4), from lockin_hlf.py's lockin.json, block E111-F05 (fp32 randn against fp32 zeros on
192 minions, a 200 s lap, five laps analysed):
  * E111-C1, detected: the ROI's fundamental >= 3 SE (lap jackknife) and the board's >= 5 SE. The sign-flip p is printed with its floor
    (2 / 2^laps), and is not a bar.
  * E111-C2, the lag at 0.005 Hz, H(f0)'s phase with a 95% t interval on laps - 1 df: SLOW if it lies wholly above 40 deg (a longer
    pole or a distributed path, P1D refuted there); P1D if wholly below 40 deg and it overlaps P1D's [22.2, 34.3]; BETWEEN if wholly
    below 40 and above 34.3; BELOW if wholly under 22.2; INCONCLUSIVE if it holds 40.
  * E111-C3, the session against E73: the fifth harmonic's lag (0.025 Hz) against E73-F25's 75.60 +- 7.82 deg: INSIDE within 3 SE of
    the difference, else OUTSIDE. The third harmonic (0.015 Hz) and |H(3f0)| / |H(f0)| are printed beside the models' values.
  * E111-C4, the hold: >= 95% of in-launch samples at >= 790 MHz and the die mean under 65 C (E73's R6).
"""
import argparse
import glob
import gzip
import hashlib
import json
import math
import os
import statistics as st
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools/claims-v3/kspeed/e98"))
import reduce_e98 as E  # noqa: E402

R, RK = E.R, E.RK
rnd, mean, ols = E.rnd, E.mean, E.ols
DIP_RAMP_S = E.RAMP_AFTER_DIP_S


# ============================================================================================ part B: E98's scoring, verbatim
def score98(probes, P):
    """E98's reduce_e98.main() from 'which probes count' to the proxies, copied verbatim (prints removed), as a function of the probes."""
    T = P["t975"]
    G, TG, C = P["gates"], P["targets"], P["constants"]
    GATED_IDX = E.GATED_IDX
    probe_line, verdict_target, verdict_band, verdict_room = E.probe_line, E.verdict_target, E.verdict_band, E.verdict_room
    cnt = [p for p in probes if p.get("rest_ok") and p.get("rest_die_w_derived") is not None]
    cnt_line = [p for p in cnt if sum(1 for i in GATED_IDX if i in p["runs"]) >= G["min_gated_runs_per_probe"]]
    cnt_hold = [p for p in cnt if p.get("hold") and not p["hold"].get("rc_bad") and p["hold"].get("processes") == p["hold"].get("processes_planned")]
    line, line_kinds = probe_line(cnt_line, "line", GATED_IDX, P)
    line_nd, _ = probe_line(cnt_line, "line_nodip", GATED_IDX, P)
    un = [i for i in GATED_IDX if cnt_line and cnt_line[0]["runs"].get(i, {}).get("kind") in ("fp16/zeros", "int8/zeros", "int8/neg_ones", "int8/sparse50")]
    line_un, _ = probe_line(cnt_line, "line", un or [1, 2, 3, 4], P)
    line_an, _ = probe_line(cnt_line, "line", [5, 6, 7, 8], P)
    fine_i = [1, 2, 3]
    fine, _ = probe_line(cnt_line, "fine_w", fine_i, P)
    px = {p["probe"]: p["rest_die_w_derived"] for p in cnt}
    pw = {p["probe"]: p["rest_w"] for p in cnt}
    p60 = {p["probe"]: (p["rest60"]["w"] / C["rest_w_per_c"] if p["rest60"]["w"] is not None else None) for p in cnt}
    p60w = {p["probe"]: p["rest60"]["w"] for p in cnt}
    phd = {p["probe"]: p["rest20"].get("die") for p in cnt}
    names_line = [p["probe"] for p in cnt_line]
    names_hold = [p["probe"] for p in cnt_hold]

    def fit(xmap, ymap, names):
        return ols([xmap.get(n) for n in names], [ymap.get(n) for n in names], T)

    res = {"probes_counted": [p["probe"] for p in cnt], "probes_line": names_line, "probes_hold": names_hold}
    xs = [p["rest_die_w_derived"] for p in cnt]
    ws = [p["rest_w"] for p in cnt]
    rng = max(xs) - min(xs) if len(xs) >= 2 else 0.0
    fall_w = (ws[0] - ws[-1]) if len(ws) >= 2 else None
    band = P["expected_fall"]["band_w"]
    res["R0"] = {"fall_w": rnd(fall_w, 3), "fall_c_w_derived": rnd(fall_w / C["rest_w_per_c"], 3) if fall_w is not None else None, "range_c": rnd(rng, 3),
                 "expected_w": P["expected_fall"]["w"], "band_w": band,
                 "against_expected": ("NOT_SCORED" if fall_w is None else ("INSIDE_BAND" if band[0] <= fall_w <= band[1] else ("BELOW_BAND" if fall_w < band[0] else "ABOVE_BAND"))),
                 "gate": "OK" if (len(cnt) >= G["min_probes"] and rng >= G["min_rest_range_c"]) else "UNDER-RESOLVED"}
    gated = res["R0"]["gate"] != "OK"

    def scored(v):
        return "UNDER-RESOLVED" if gated else v

    f1 = fit(px, line, names_line)
    res["R1"] = {"fit": f1, "verdict": scored(verdict_target(f1, TG["line_slope"])), "target": TG["line_slope"], "per_probe": {k: rnd(v, 3) for k, v in line.items()},
                 "kinds": {p: {k: rnd(v, 3) for k, v in kv.items()} for p, kv in line_kinds.items()}}
    hold_die = {p["probe"]: p["hold"]["die"] for p in cnt_hold}
    hold_w = {p["probe"]: p["hold"].get("fine_w") for p in cnt_hold}
    hold_io = {p["probe"]: p["hold"].get("io") for p in cnt_hold}
    f2 = fit(px, hold_die, names_hold)
    res["R2"] = {"fit": f2, "verdict": scored(verdict_band(f2, TG["hold_band"], TG["hold_floor"])), "band": TG["hold_band"], "floor": TG["hold_floor"],
                 "per_probe": {k: rnd(v, 3) for k, v in hold_die.items()}, "path_slope": TG["hold_slope_path"]}
    res["V"] = verdict_room(res["R1"]["verdict"], res["R2"]["verdict"])
    f_s1 = fit(pw, fine, names_line)
    res["S1"] = {"fit": f_s1, "verdict": scored(verdict_target(f_s1, TG["fine_line_w_per_w_desk"])), "target": TG["fine_line_w_per_w_desk"], "per_probe": {k: rnd(v, 3) for k, v in fine.items()}}
    f_s2 = fit(pw, hold_w, names_hold)
    res["S2"] = {"fit": f_s2, "verdict": scored(verdict_band(f_s2, TG["hold_w_band"], TG["hold_w_per_w_if_line_slope"])), "band": TG["hold_w_band"],
                 "per_probe": {k: rnd(v, 3) for k, v in hold_w.items()}, "path": TG["hold_w_per_w_path"]}
    fr_w = {p["probe"]: p["runs"].get(0, {}).get("fine_w") for p in cnt}
    fr_l = {p["probe"]: p["runs"].get(0, {}).get("line") for p in cnt}
    nm = [p["probe"] for p in cnt]
    f3w, f3l = fit(pw, fr_w, nm), fit(px, fr_l, nm)
    res["S3"] = {"fit_w": f3w, "verdict_w": scored(verdict_target(f3w, TG["from_rest_w_per_w_room"])), "target_w": TG["from_rest_w_per_w_room"],
                 "fit_line": f3l, "verdict_line": scored(verdict_target(f3l, TG["from_rest_line_slope"])), "target_line": TG["from_rest_line_slope"],
                 "per_probe": {k: {"fine_w": rnd(fr_w[k], 3), "line": rnd(fr_l[k], 3)} for k in nm}}
    trip = {p["probe"]: mean([p["runs"][i]["mhz"] for i in (5, 8) if i in p["runs"]]) for p in cnt}
    tripw = {p["probe"]: mean([p["runs"][i]["w"] for i in (5, 8) if i in p["runs"]]) for p in cnt}
    f4m, f4w = fit(px, trip, nm), fit(px, tripw, nm)
    res["S4"] = {"fit_mhz": f4m, "verdict_mhz": scored(verdict_target(f4m, TG["trip_mhz_per_c"])), "target_mhz": TG["trip_mhz_per_c"], "fit_w": f4w,
                 "verdict_w": scored(verdict_target(f4w, TG["trip_w_per_c"])), "target_w": TG["trip_w_per_c"],
                 "per_probe": {k: {"mhz": rnd(trip[k], 1), "w": rnd(tripw[k], 2)} for k in nm}}
    arms = {
        "R1_on_60s_rest": fit(p60, line, names_line),
        "R1_on_history_die": fit(phd, line, names_line),
        "R1_dips_left_out": fit(px, line_nd, names_line),
        "R1_unclamped_only": fit(px, line_un, names_line),
        "R1_unanchored_idx1to4_A2": fit(px, line_un, names_line),
        "R1_anchored_idx5to8_A2": fit(px, line_an, names_line),
        "R2_on_60s_rest": fit(p60, hold_die, names_hold),
        "R2_on_history_die": fit(phd, hold_die, names_hold),
        "R2_ioshire": fit(px, hold_io, names_hold),
        "S1_on_60s_rest": fit(p60w, fine, names_line),
        "S2_on_60s_rest": fit(p60w, hold_w, names_hold),
    }
    by_idx = {}
    for i in GATED_IDX:
        ym = {p["probe"]: p["runs"].get(i, {}).get("line") for p in cnt_line}
        kind = next((p["runs"][i]["kind"] for p in cnt_line if i in p["runs"]), None)
        by_idx[f"{i}:{kind}"] = fit(px, ym, names_line)
    arms["R1_by_position"] = by_idx
    res["arms"] = arms
    prox = {}
    a2p = {"a2-nic": {p["probe"]: p["rest20"].get("nic") for p in cnt}, "a2-nvme": {p["probe"]: p["rest20"].get("nvme") for p in cnt}}
    names_other = sorted({k for p in cnt for k in p.get("others", {})})
    for k in names_other:
        a2p[k] = {p["probe"]: p.get("others", {}).get(k) for p in cnt}
    for k, m in a2p.items():
        have = [p["probe"] for p in cnt if m.get(p["probe"]) is not None]
        if len(have) < G["min_probes"]:
            prox[k] = {"n": len(have), "note": "too few counted probes with rows"}
            continue
        prox[k] = {"n": len(have), "line_on_it": fit(m, line, names_line), "hold_on_it": fit(m, hold_die, names_hold), "it_on_rest_die": fit(px, m, nm), "values": {p: rnd(m[p], 3) for p in have}}
    res["proxies"] = prox
    res["_maps"] = {"px": px, "line": line, "hold_die": hold_die, "trip": trip}
    return res


def regression_check(res, committed):
    """score98 on E98's probes must give E98's committed R0..S4 and the arms, key for key."""
    bad = []
    for k in ("R0", "R1", "R2", "V", "S1", "S2", "S3", "S4", "arms", "proxies"):
        a = json.dumps(res.get(k), sort_keys=True)
        b = json.dumps(committed.get(k), sort_keys=True)
        if a != b:
            bad.append(k)
    return bad


def hold39(pdir, P98):
    """W1's hold read as E98 reads a hold, on its first 39 processes: the 120 s ending with process 39."""
    sess, runs, launches, q0 = R.load_session(pdir)
    r = next((x for x in runs if x["block"] == "HOLD"), None)
    if r is None:
        return None
    procs = sorted([L for L in launches if L["run"] == r["run"] and L.get("role") == "work"], key=lambda L: L["proc"])
    n = P98_HOLD_N
    first = procs[:n]
    s = E.tel_rows(os.path.join(pdir, r["tel"]))
    win = E.window(s, first, E.HOLD_S)
    if win is None:
        return None
    k = P98["constants"]["k_line_c_per_w"]
    rec = {"run": r["run"], "idx": r["idx"], "kind": E.kind_of(r["values"]), "rc_bad": sum(1 for p in first if p.get("rc") != 0),
           "t0_ms": r["t_first_ms"], "processes": len(first), "processes_planned": n, "of_processes_run": len(procs),
           "gate": {"held_s": r["gate"].get("held_s"), "reached": r["gate"].get("reached"), "die": (r["gate"].get("reading") or [None])[0]},
           "calibration": E.hold_calibration(s, first), "read_as": f"E98's hold on the first {n} processes"}
    rec.update({k2: (rnd(v, 4) if isinstance(v, float) else v) for k2, v in win.items()})
    rec["line"] = rnd(win["die"] - k * win["w"], 4)
    rec["line_nodip"] = rnd(win["die_nodip"] - k * win["w_nodip"], 4) if win["die_nodip"] is not None and win["w_nodip"] is not None else None
    return rec


P98_HOLD_N = 39


def b3(res_all, baseline, warm, P):
    """E111-B3: each warm probe's leads over the mean of the baseline probes, per C of rest-die lead."""
    pb = P["partB"]
    m = res_all["_maps"]
    px, line, hold = m["px"], m["line"], m["hold_die"]
    base = [b for b in baseline if b in px]
    out = {"baseline": base, "per_probe": {}, "min_lead_c": pb["b3_min_lead_c"]}
    if len(base) < 2:
        out["verdict_hold"] = out["verdict_line"] = "UNDER-RESOLVED"
        return out
    bx = mean([px[b] for b in base])
    bl = mean([line.get(b) for b in base])
    bh = mean([hold.get(b) for b in base])
    sh, sl = [], []
    for w in warm:
        if w not in px:
            out["per_probe"][w] = {"note": "not counted"}
            continue
        dx = px[w] - bx
        rec = {"dx_c": rnd(dx, 3), "line_lead": rnd(line[w] - bl, 3) if line.get(w) is not None else None,
               "hold_lead": rnd(hold[w] - bh, 3) if hold.get(w) is not None else None}
        rec["warm"] = dx >= pb["b3_min_lead_c"]
        if rec["warm"]:
            if rec["line_lead"] is not None:
                rec["line_per_c"] = rnd(rec["line_lead"] / dx, 3)
                sl.append((rec["line_lead"] / dx, dx))
            if rec["hold_lead"] is not None:
                rec["hold_per_c"] = rnd(rec["hold_lead"] / dx, 3)
                sh.append((rec["hold_lead"] / dx, dx))
        out["per_probe"][w] = rec
    nb = len(base)
    for key, vals, sig, tgt, p1 in (("hold", sh, pb["b3_noise_per_probe_c"]["hold"], None, pb["p1_lead_per_c"]["hold"]),
                                    ("line", sl, pb["b3_noise_per_probe_c"]["line"], P["partB"]["e98_targets"]["line_slope"], pb["p1_lead_per_c"]["line"])):
        if not vals:
            out[f"verdict_{key}"] = "UNDER-RESOLVED"
            continue
        mu = mean([v for v, _ in vals])
        se = math.sqrt(sum((sig * math.sqrt(1 + 1.0 / nb) / dx) ** 2 for _, dx in vals)) / len(vals)
        f = {"slope": rnd(mu, 4), "lo": rnd(mu - 1.96 * se, 4), "hi": rnd(mu + 1.96 * se, 4), "se": rnd(se, 4), "n": len(vals)}
        out[key] = f
        if key == "hold":
            T = P["partB"]["e98_targets"]
            out["verdict_hold"] = E.verdict_band(f, T["hold_band"], T["hold_floor"])
        else:
            out["verdict_line"] = E.verdict_target(f, tgt)
        out[f"p1_{key}_inside"] = bool(f["lo"] <= p1 <= f["hi"])
        out[f"p1_{key}"] = p1
    return out


# ============================================================================================ part A: the holds
def work_samples(pdir, run_name):
    sess, runs, launches, q0 = R.load_session(pdir)
    r = next((x for x in runs if x["run"] == run_name), None)
    if r is None:
        return None, None, None
    procs = sorted([L for L in launches if L["run"] == run_name and L.get("role") == "work"], key=lambda L: L["proc"])
    s = E.tel_rows(os.path.join(pdir, r["tel"]))
    kw = E.kernel_spans(procs)
    ws = [x for x in s if any(a <= x["t"] <= b for a, b in kw)]
    return r, procs, ws


def fine_mask(ws, procs, clock):
    dips = E.find_dips(ws, E.work_spans(procs))
    def dipped(t):
        return any(d["t0"] <= t <= d["t1"] + DIP_RAMP_S * 1000 for d in dips)
    return [(x["mhz"] == clock and x["w"] is not None and not dipped(x["t"])) for x in ws], dips


def win_stats(ws, mask, a, b, clock, minshare):
    sel = [(x, m) for x, m in zip(ws, mask) if a <= x["t"] < b]
    if not sel:
        return None
    xs = [x for x, _ in sel]
    fine = [x["w"] for x, m in sel if m]
    return {"n": len(xs), "die": mean([x["die"] for x in xs]), "w": mean([x["w"] for x in xs]), "io": mean([x["io"] for x in xs]),
            "mhz": mean([x["mhz"] for x in xs]), "share_clock": sum(1 for x in xs if x["mhz"] == clock) / len(xs),
            "fine_w": mean(fine) if len(fine) >= minshare * len(xs) else None, "fine_share": len(fine) / len(xs),
            "t0_ms": a, "t1_ms": b}


def bins_slope(pts, t_end, span_s, bin_s):
    """OLS slope per minute of bin means over the last span_s (pts: (t_ms, y)), with its se and the bins."""
    t0 = t_end - span_s * 1000
    nb = int(round(span_s / bin_s))
    bins = []
    for i in range(nb):
        a, b = t0 + i * bin_s * 1000, t0 + (i + 1) * bin_s * 1000
        ys = [y for t, y in pts if a <= t < b and y is not None]
        if len(ys) >= 10:
            bins.append(((a + b) / 2.0 / 60000.0, sum(ys) / len(ys)))
    if len(bins) < 5:
        return None
    mx, my = mean([b[0] for b in bins]), mean([b[1] for b in bins])
    sxx = sum((x - mx) ** 2 for x, _ in bins)
    sl = sum((x - mx) * (y - my) for x, y in bins) / sxx
    res = [y - my - sl * (x - mx) for x, y in bins]
    se = math.sqrt(sum(r * r for r in res) / (len(bins) - 2) / sxx)
    return {"slope_per_min": sl, "se": se, "n_bins": len(bins), "range": max(y for _, y in bins) - min(y for _, y in bins)}


def asymptote(pts, t_start, t_end, bin_s=30):
    """W(t) = Winf + B exp(-(t - t_start)/tau) on 30 s bin means after the hold's first 120 s; tau on a grid; least squares."""
    bins = []
    a = t_start + 120000
    while a + bin_s * 1000 <= t_end:
        ys = [y for t, y in pts if a <= t < a + bin_s * 1000 and y is not None]
        if len(ys) >= 10:
            bins.append(((a + bin_s * 500 - t_start) / 1000.0, sum(ys) / len(ys)))
        a += bin_s * 1000
    if len(bins) < 8:
        return None
    best = None
    tau = 60.0
    while tau <= 5000.0:
        e = [math.exp(-x / tau) for x, _ in bins]
        y = [v for _, v in bins]
        me, my = mean(e), mean(y)
        see = sum((u - me) ** 2 for u in e)
        if see > 0:
            B = sum((u - me) * (v - my) for u, v in zip(e, y)) / see
            Winf = my - B * me
            rss = sum((v - Winf - B * u) ** 2 for u, v in zip(e, y))
            if best is None or rss < best[0]:
                best = (rss, tau, Winf, B)
        tau *= 1.05
    rss, tau, Winf, B = best
    return {"tau_s": rnd(tau, 1), "w_inf": rnd(Winf, 4), "B": rnd(B, 4), "rms": rnd(math.sqrt(rss / len(bins)), 4), "n_bins": len(bins),
            "at_tau_edge": tau < 63 or tau > 4760}


def rest_block(pdir):
    """The REST block's last 60 s (10 Hz): die, W, n; and its span."""
    try:
        sess, runs, launches, q0 = R.load_session(pdir)
    except (OSError, ValueError):
        return None
    r = next((x for x in runs if x["block"] == "REST"), None)
    if r is None:
        return None
    s = E.tel_rows(os.path.join(pdir, r["tel"]))
    if not s:
        return None
    t1 = s[-1]["t"]
    last = [x for x in s if x["t"] >= t1 - 60000]
    return {"die": mean([x["die"] for x in last]), "w": mean([x["w"] for x in last]), "n": len(last), "t0_ms": s[0]["t"], "t1_ms": t1,
            "die_values": {str(v): sum(1 for x in last if x["die"] == v) for v in sorted({x["die"] for x in last if x["die"] is not None})}}


def band_verdict(lo, hi, band):
    if lo is None or hi is None:
        return "NOT_SCORED"
    if band[0] <= lo and hi <= band[1]:
        return "PASS"
    if hi < band[0] or lo > band[1]:
        return "FAIL"
    return "INCONCLUSIVE"


def proxies(H, a, b, include_a2=False):
    """The boxes' readings over [a, b): rows with load under 2; cards free and under their idle bars; aifoundry1's cards blank if either
    is held. Six rows at least for a reading."""
    out = {}
    for box in ("aifoundry1", "aifoundry2", "aifoundry3"):
        rows = [r for r in H.window(box, a, b) if (r.get("load") or 0) <= 2]
        tag = box.replace("aifoundry", "a")
        if box == "aifoundry2" and not include_a2:
            pass
        else:
            nic = [((r.get("temps") or {}).get("nic")) for r in rows]
            nvme = [((r.get("temps") or {}).get("nvme")) for r in rows]
            if sum(1 for x in nic if x is not None) >= 6:
                out[tag + "-nic"] = mean(nic)
            if sum(1 for x in nvme if x is not None) >= 6:
                out[tag + "-nvme"] = mean(nvme)
        if box == "aifoundry2":
            continue
        bars = {0: 22.0, 1: 34.0} if box == "aifoundry1" else {0: 27.0}
        for n, bar in bars.items():
            die = []
            for r in rows:
                cards = {c.get("n"): c for c in (r.get("cards") or [])}
                c = cards.get(n)
                if not c or c.get("die") is None or c.get("w") is None or c.get("held") or c["w"] > bar:
                    continue
                if box == "aifoundry1" and any(x.get("held") for x in cards.values()):
                    continue
                die.append(c["die"])
            if len(die) >= 6:
                out[f"{tag}c{n}-die"] = mean(die)
    return out


def phone_window(rows, a, b):
    xs = [r.get("batteryTempC") for r in rows if a <= r.get("t_ms", 0) < b and r.get("batteryTempC") is not None]
    return mean(xs) if xs else None


def part_a(data, P, H, phone):
    pa = P["partA"]
    out = {}
    idles = {s: rest_block(os.path.join(data, s)) for s in ("W1", "W2", "END")}
    out["idles"] = {k: ({kk: (rnd(vv, 4) if isinstance(vv, float) else vv) for kk, vv in v.items()} if v else None) for k, v in idles.items()}
    for hname, spec in pa["holds"].items():
        pdir = os.path.join(data, spec["step"])
        r, procs, ws = work_samples(pdir, spec["run"]) if os.path.exists(os.path.join(pdir, "runs.jsonl")) else (None, None, None)
        rec = {"kind": spec["kind"], "clock_mhz": spec["clock_mhz"]}
        out[hname] = rec
        if not ws:
            rec["note"] = "the hold did not run"
            continue
        clock = spec["clock_mhz"]
        mask, dips = fine_mask(ws, procs, clock)
        t_start = min(p["t_start_ms"] for p in procs)
        t_end = max(p["t_end_ms"] for p in procs)
        rec.update({"processes_run": len(procs), "processes_planned": r.get("processes"), "rc_bad": sum(1 for p in procs if p.get("rc") != 0),
                    "t_start_ms": t_start, "t_end_ms": t_end, "minutes": rnd((t_end - t_start) / 60000.0, 2), "dips": len(dips),
                    "complete": len(procs) == r.get("processes") and not any(p.get("rc") for p in procs)})
        plat = win_stats(ws, mask, t_end - pa["plateau_s"] * 1000, t_end + 1, clock, pa["fine_min_share"])
        prev = win_stats(ws, mask, t_end - (pa["plateau_s"] + pa["previous_s"]) * 1000, t_end - pa["plateau_s"] * 1000, clock, pa["fine_min_share"])
        rec["plateau"] = {k: (rnd(v, 4) if isinstance(v, float) else v) for k, v in (plat or {}).items()}
        rec["previous"] = {k: (rnd(v, 4) if isinstance(v, float) else v) for k, v in (prev or {}).items()}
        rec["clock_held"] = bool(plat and plat["share_clock"] >= pa["clock_share_min"])
        # A1
        k = pa["k_fine_w_per_c"]
        fpts = [(x["t"], x["w"]) for x, m in zip(ws, mask) if m]
        dpts = [(x["t"], x["die"]) for x in ws]
        fs = bins_slope(fpts, t_end, pa["slope_window_s"], pa["slope_bin_s"])
        ds = bins_slope(dpts, t_end, pa["slope_window_s"], pa["slope_bin_s"])
        a1 = {"fine_slope_c_per_min": rnd(fs["slope_per_min"] / k, 4) if fs else None, "fine_slope_se": rnd(fs["se"] / k, 4) if fs else None,
              "fine_slope_w_per_min": rnd(fs["slope_per_min"], 5) if fs else None,
              "die_slope_c_per_min": rnd(ds["slope_per_min"], 4) if ds else None, "die_slope_se": rnd(ds["se"], 4) if ds else None,
              "fine_range_w": rnd(fs["range"], 4) if fs else None, "die_range_c": rnd(ds["range"], 3) if ds else None}
        use = a1["fine_slope_c_per_min"] if (fs and plat and plat["fine_w"] is not None) else a1["die_slope_c_per_min"]
        a1["read_on"] = "fine W" if (fs and plat and plat["fine_w"] is not None) else "the die (no fine W: the clock not held)"
        a1["verdict"] = "NOT_SCORED" if use is None else ("PASS" if abs(use) <= pa["steady_bar_c_per_min"] else "FAIL")
        rec["A1"] = a1
        # A2
        ib, ia = idles.get(spec["idle_before"]), idles.get(spec["idle_after"])
        rec["idle_before"], rec["idle_after"] = (ib or {}).get("die"), (ia or {}).get("die")
        cands = []
        for idl in ([ib] if ib else []) + ([ia] if ia else []) + ([{"die": mean([ib["die"], ia["die"]]), "w": mean([ib["w"], ia["w"]])}] if ib and ia else []):
            for wv in [x for x in (plat, prev) if x]:
                dw = wv["w"] - idl["w"]
                if dw > 0:
                    cands.append((wv["die"] - idl["die"]) / dw)
        if ib and ia and plat:
            im = {"die": (ib["die"] + ia["die"]) / 2.0, "w": (ib["w"] + ia["w"]) / 2.0}
            rise, dW = plat["die"] - im["die"], plat["w"] - im["w"]
            c = rise / dW
            rec["A2"] = {"rise_c": rnd(rise, 3), "dW_w": rnd(dW, 3), "c": rnd(c, 4), "c_lo": rnd(min(cands), 4), "c_hi": rnd(max(cands), 4),
                         "idle_mismatch_c": rnd(ia["die"] - ib["die"], 3), "idle_mismatch_w": rnd(ia["w"] - ib["w"], 3)}
            for bname, band in pa["bands"].items():
                if bname == "linearity_ratio":
                    continue
                rec["A2"][bname] = band_verdict(min(cands), max(cands), band)
        elif ib and plat:
            rise, dW = plat["die"] - ib["die"], plat["w"] - ib["w"]
            rec["A2"] = {"rise_c": rnd(rise, 3), "dW_w": rnd(dW, 3), "c": rnd(rise / dW, 4), "c_lo": rnd(min(cands), 4) if cands else None,
                         "c_hi": rnd(max(cands), 4) if cands else None, "note": "no idle after: the idle before alone"}
            for bname, band in pa["bands"].items():
                if bname != "linearity_ratio" and cands:
                    rec["A2"][bname] = band_verdict(min(cands), max(cands), band)
        else:
            rec["A2"] = {"note": "no idle reading", "verdicts": "NOT_SCORED"}
        # beside: the asymptote
        asy = asymptote(fpts, t_start, t_end) if fpts else None
        if asy and plat and plat.get("fine_w") is not None and ib and ia:
            die_inf = plat["die"] + (asy["w_inf"] - plat["fine_w"]) / k
            w_inf_total = plat["w"] + (asy["w_inf"] - plat["fine_w"])
            im = {"die": (ib["die"] + ia["die"]) / 2.0, "w": (ib["w"] + ia["w"]) / 2.0}
            asy.update({"die_inf": rnd(die_inf, 3), "c_inf": rnd((die_inf - im["die"]) / (w_inf_total - im["w"]), 4)})
        rec["asymptote"] = asy
        # A4: the proxies beside
        if ib and plat:
            wb = (ib["t1_ms"] - 300000, ib["t1_ms"])
            wp = (plat["t0_ms"], plat["t1_ms"])
            wa = (ia["t1_ms"] - 300000, ia["t1_ms"]) if ia else None
            pb_, pp_, pa_ = proxies(H, *wb, include_a2=True), proxies(H, *wp), (proxies(H, *wa, include_a2=True) if wa else {})
            rows = {}
            for key in sorted(set(pb_) | set(pp_) | set(pa_)):
                vb, vp, va = pb_.get(key), pp_.get(key), pa_.get(key)
                idle_m = mean([vb, va])
                rows[key] = {"before": rnd(vb, 3), "plateau": rnd(vp, 3), "after": rnd(va, 3)}
                slope = pa["proxy_c_per_c_of_rest_die"].get(key)
                if vp is not None and idle_m is not None and slope:
                    d = (vp - idle_m) / slope
                    rows[key]["room_move_c"] = rnd(d, 3)
                    if rec["A2"].get("rise_c") is not None:
                        rows[key]["c_corrected"] = rnd((rec["A2"]["rise_c"] - d) / rec["A2"]["dW_w"], 4)
            rec["A4"] = {"windows_ms": {"before": wb, "plateau": wp, "after": wa}, "proxies": rows,
                         "phone_battery_c": {"before": rnd(phone_window(phone, *wb), 2), "plateau": rnd(phone_window(phone, *wp), 2),
                                             "after": rnd(phone_window(phone, *wa), 2) if wa else None}}
    a, b = out.get("H-I8", {}).get("A2", {}), out.get("H-F32", {}).get("A2", {})
    if a.get("c_lo") and b.get("c_lo"):
        ratio = b["c"] / a["c"]
        lo, hi = b["c_lo"] / a["c_hi"], b["c_hi"] / a["c_lo"]
        out["A3"] = {"ratio": rnd(ratio, 4), "lo": rnd(lo, 4), "hi": rnd(hi, 4), "band": pa["bands"]["linearity_ratio"],
                     "verdict": band_verdict(lo, hi, pa["bands"]["linearity_ratio"])}
    else:
        out["A3"] = {"verdict": "NOT_SCORED"}
    return out


# ============================================================================================ part C: the camera
def part_c(data, P):
    pc = P["partC"]
    p = os.path.join(data, "CAM-ANA", "lockin.json")
    if not os.path.exists(p):
        return {"note": "no lockin.json: the camera block did not run or was not reduced", "C1": "NOT_SCORED", "C2": "NOT_SCORED",
                "C3": "NOT_SCORED", "C4": "NOT_SCORED"}
    L = json.load(open(p))
    b = (L.get("blocks") or {}).get(pc["block"])
    if not b or "error" in b:
        return {"note": f"block missing or in error: {(b or {}).get('error')}", "C1": "NOT_SCORED", "C2": "NOT_SCORED", "C3": "NOT_SCORED", "C4": "NOT_SCORED"}
    roi, pw, tr, hold = b.get("roi", {}), b.get("power", {}), b.get("transfer", {}), b.get("hold", {})
    n = int(roi.get("n_laps") or b.get("laps_analysed") or 0)
    out = {"laps_analysed": b.get("laps_analysed"), "laps_total": b.get("laps_total"), "stretches": b.get("stretches"),
           "roi_amp_mk": rnd(roi.get("amp"), 2), "roi_se_mk": rnd(roi.get("se_along"), 2), "roi_snr": rnd(roi.get("snr"), 2),
           "roi_phase_deg": rnd(roi.get("phase_deg"), 2), "p_signflip": roi.get("p_signflip"), "p_floor": rnd(2.0 / 2 ** n, 4) if n else None,
           "board_amp_w": rnd(pw.get("amp"), 4), "board_snr": rnd(pw.get("snr"), 2), "board_step_w": b.get("board_step_w")}
    out["C1"] = "PASS" if (roi.get("snr") or 0) >= pc["detect"]["roi_min_se"] and (pw.get("snr") or 0) >= pc["detect"]["board_min_se"] else "FAIL"
    t1 = tr.get("1") or {}
    T = P["t975"]
    nl = int(t1.get("n_laps") or n or 0)
    tq = T.get(str(nl - 1)) if nl >= 2 else None
    if t1.get("H_phase_deg") is not None and tq:
        lag, se = t1["H_phase_deg"], t1["se_H_phase_deg"]
        lo, hi = lag - tq * se, lag + tq * se
        thr = pc["lag_threshold_deg"]
        p1d = pc["models_at_0p005"]["P1D"]["lag_95"]
        if lo > thr:
            v = "SLOW"
        elif hi < thr:
            v = "BELOW" if hi < p1d[0] else ("BETWEEN" if lo > p1d[1] else "P1D")
        else:
            v = "INCONCLUSIVE"
        out["C2"] = v
        out["lag_0p005"] = {"deg": rnd(lag, 2), "se": rnd(se, 2), "lo": rnd(lo, 2), "hi": rnd(hi, 2), "t": tq, "n_laps": nl,
                            "H_mag": rnd(t1.get("H_mag"), 2), "se_H_mag": rnd(t1.get("se_H_mag"), 2), "f_hz": t1.get("f_hz")}
    else:
        out["C2"] = "NOT_SCORED"
    t5 = tr.get("5") or {}
    e = pc["e73_0p025_lag"]
    if t5.get("H_phase_deg") is not None:
        d = t5["H_phase_deg"] - e["deg"]
        sd = math.sqrt(t5["se_H_phase_deg"] ** 2 + e["se"] ** 2)
        out["C3"] = "INSIDE" if abs(d) <= 3 * sd else "OUTSIDE"
        out["lag_0p025"] = {"deg": rnd(t5["H_phase_deg"], 2), "se": rnd(t5["se_H_phase_deg"], 2), "e73": e, "diff": rnd(d, 2), "sd": rnd(sd, 2)}
    else:
        out["C3"] = "NOT_SCORED"
    t3 = tr.get("3") or {}
    if t3.get("H_mag") and t1.get("H_mag"):
        out["h3_over_h1"] = rnd(t3["H_mag"] / t1["H_mag"], 4)
        out["lag_0p015"] = {"deg": rnd(t3.get("H_phase_deg"), 2), "se": rnd(t3.get("se_H_phase_deg"), 2)}
    out["harmonics"] = {k: {"f_hz": v.get("f_hz"), "H_mag": rnd(v.get("H_mag"), 2), "se_H_mag": rnd(v.get("se_H_mag"), 2),
                            "lag": rnd(v.get("H_phase_deg"), 2), "se_lag": rnd(v.get("se_H_phase_deg"), 2)} for k, v in tr.items()}
    out["models"] = pc["models_at_0p005"]
    sh, dm = hold.get("samples_800_share"), hold.get("die_mean_c")
    out["hold"] = hold
    out["C4"] = "NOT_SCORED" if sh is None or dm is None else ("PASS" if sh >= pc["hold"]["share_790_min"] and dm < pc["hold"]["die_mean_max_c"] else "FAIL")
    return out


# ============================================================================================ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("data")
    ap.add_argument("--out")
    ap.add_argument("--pred", default=os.path.join(HERE, "predictions-e111.json"))
    ap.add_argument("--e98", default=os.path.join(ROOT, "docs/reports/data/2026-11-01-e98-heat-path-drift"))
    a = ap.parse_args()
    P = json.load(open(a.pred))
    P98 = json.load(open(os.path.join(ROOT, "tools/claims-v3/kspeed/e98/predictions.json")))
    res = {"experiment": "E111", "predictions_sha256": hashlib.sha256(open(a.pred, "rb").read()).hexdigest()}
    H = E.History(a.data)
    phone = R.jl(os.path.join(a.data, "phone.jsonl"))
    # ---- part B
    H98 = E.History(a.e98)
    q98 = R.jl(os.path.join(a.e98, "queue.jsonl"))
    p98 = []
    for name in P["partB"]["e98_probes"]:
        pdir = os.path.join(a.e98, name)
        pr = E.read_probe(pdir, name, H98, P98, [q for q in q98 if q.get("probe") == name])
        pr["queue"] = [q for q in q98 if q.get("probe") == name]
        p98.append(pr)
    s98 = score98(p98, P98)
    committed = json.load(open(os.path.join(a.e98, "results.json")))
    bad = regression_check(s98, committed)
    res["e98_regression"] = {"keys_differing": bad, "ok": not bad}
    if bad:
        print("REFUSED: score98 on E98's own probes does not reproduce E98's committed", bad)
        if a.out:
            json.dump(res, open(a.out, "w"), indent=1)
        return 2
    qrecs = R.jl(os.path.join(a.data, "queue.jsonl"))
    mine = []
    for name in ("W1", "W2"):
        pdir = os.path.join(a.data, name)
        if not os.path.exists(os.path.join(pdir, "runs.jsonl")):
            continue
        pr = E.read_probe(pdir, name, H, P98, [])
        if name == "W1":
            pr["hold_full_last120"] = pr.get("hold")
            pr["hold"] = hold39(pdir, P98)
        pr["queue"] = [q for q in qrecs if q.get("step") == name]
        mine.append(pr)
    sall = score98(p98 + mine, P98)
    res["B"] = {"B0_gate": sall["R0"]["gate"], "R0": sall["R0"], "B1": sall["R1"]["verdict"], "B1_fit": sall["R1"]["fit"],
                "B2": sall["R2"]["verdict"], "B2_fit": sall["R2"]["fit"], "BV": sall["V"],
                "B4_mhz": sall["S4"]["verdict_mhz"], "B4_w": sall["S4"]["verdict_w"], "B4": sall["S4"],
                "S1": sall["S1"], "S2": sall["S2"], "S3": sall["S3"], "arms": sall["arms"], "proxies": sall["proxies"],
                "probes_counted": sall["probes_counted"], "probes_line": sall["probes_line"], "probes_hold": sall["probes_hold"],
                "per_probe_line": sall["R1"]["per_probe"], "per_probe_hold": sall["R2"]["per_probe"], "rest_die": sall["_maps"]["px"]}
    res["B"]["B3"] = b3(sall, P["partB"]["baseline_probes"], [p["probe"] for p in mine], P)
    res["probes_e111"] = mine
    # ---- part A
    res["A"] = part_a(a.data, P, H, phone)
    # ---- part C
    res["C"] = part_c(a.data, P)
    # ---- the session
    res["queue"] = [q for q in qrecs if q.get("kind") in ("queue_start", "start", "end", "skip", "queue_end", "reduce_cam")]
    tally = {}
    verdicts = [("E111-A1 H-I8", (res["A"].get("H-I8", {}).get("A1") or {}).get("verdict", "NOT_SCORED")),
                ("E111-A1 H-F32", (res["A"].get("H-F32", {}).get("A1") or {}).get("verdict", "NOT_SCORED"))]
    for h in ("H-I8", "H-F32"):
        a2 = res["A"].get(h, {}).get("A2") or {}
        for bname in ("prior_aifoundry2", "lab_model_sept", "e97_aifoundry3_plateau", "line_76s"):
            verdicts.append((f"E111-A2 {h} {bname}", a2.get(bname, "NOT_SCORED")))
    verdicts += [("E111-A3", res["A"]["A3"]["verdict"]), ("E111-B0", res["B"]["B0_gate"]), ("E111-B1", res["B"]["B1"]), ("E111-B2", res["B"]["B2"]),
                 ("E111-BV", res["B"]["BV"]), ("E111-B3 hold", res["B"]["B3"].get("verdict_hold")), ("E111-B3 line", res["B"]["B3"].get("verdict_line")),
                 ("E111-B4 MHz", res["B"]["B4_mhz"]), ("E111-B4 W", res["B"]["B4_w"]), ("E111-C1", res["C"].get("C1")), ("E111-C2", res["C"].get("C2")),
                 ("E111-C3", res["C"].get("C3")), ("E111-C4", res["C"].get("C4"))]
    for _, v in verdicts:
        tally[v] = tally.get(v, 0) + 1
    res["verdicts"] = dict(verdicts)
    res["tally"] = tally
    # ---- print
    print("E111: aifoundry2's steady coefficient, the drift's warm probes, the camera at 0.005 Hz; under its own governor, nothing set")
    print("E98 regression (score98 on E98's probes == its committed results.json):", res["e98_regression"])
    print("\nVERDICTS")
    for k, v in verdicts:
        print(f"  {k:40s} {v}")
    print("  tally", json.dumps(tally))
    print("\nPART A, the holds")
    print("  idles", json.dumps(res["A"]["idles"]))
    for h in ("H-I8", "H-F32"):
        x = res["A"].get(h, {})
        print(f"  {h}: {json.dumps({k: x.get(k) for k in ('kind', 'clock_mhz', 'processes_run', 'processes_planned', 'minutes', 'dips', 'complete', 'clock_held')})}")
        print(f"     plateau {json.dumps(x.get('plateau'))}")
        print(f"     previous {json.dumps(x.get('previous'))}")
        print(f"     A1 {json.dumps(x.get('A1'))}")
        print(f"     A2 {json.dumps(x.get('A2'))}")
        print(f"     asymptote {json.dumps(x.get('asymptote'))}")
        print(f"     A4 {json.dumps(x.get('A4'))}")
    print("  A3", json.dumps(res["A"]["A3"]))
    print("\nPART B, the drift")
    for k in ("B0_gate", "R0", "B1", "B1_fit", "B2", "B2_fit", "BV", "B3", "B4"):
        print(f"  {k}: {json.dumps(res['B'][k])}")
    print("  rest die (W-derived)", json.dumps({k: rnd(v, 3) for k, v in res["B"]["rest_die"].items()}))
    print("  line per probe", json.dumps(res["B"]["per_probe_line"]), "\n  hold per probe", json.dumps(res["B"]["per_probe_hold"]))
    for pr in mine:
        print(f"  {pr['probe']}: rest W {pr.get('rest_w')} ({pr.get('rest_source')}), rest20 {json.dumps(pr.get('rest20'))}, rest60 {json.dumps(pr.get('rest60'))}")
        for i in sorted(pr["runs"]):
            r = pr["runs"][i]
            print(f"     {i} {r['kind']:14s} W {r['w']:.2f} die {r['die']:.2f} line {r['line']:.2f} MHz {r['mhz']:.0f} fine {r.get('fine_w')} gate {r['gate']}")
        print(f"     hold {json.dumps(pr.get('hold'))[:600]}")
    print("\nPART C, the camera")
    print("  ", json.dumps({k: v for k, v in res["C"].items() if k != "models"}))
    if a.out:
        json.dump(res, open(a.out, "w"), indent=1, sort_keys=True, default=str)
    return 0


if __name__ == "__main__":
    sys.exit(main())
