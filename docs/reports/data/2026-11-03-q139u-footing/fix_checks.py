#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Q139(u), corrections after verification (post hoc, Tue 3 Nov 2026): the checks behind the README's dated notes C1-C5.
Committed files only are read; nothing here changes FOOTING-RULE.md, footing.json, a reduction, a fit, a score or a verdict.

    python3 fix_checks.py <scratch dir>      (writes fix-checks.json beside this file; copies and re-runs go in <scratch>)

C1  What E82 amendment A2's "dips" are on each card. Per sample i of every sampler trace: A2's test (board_w[i] below
    min(board_w[i-2], board_w[i+2]) - 4 W), the level min(board_w[i-2], board_w[i+2]), whether the sampled minion clock
    (mhz.minion) or the minion regulator's set point (reg_mv.minion) changes anywhere in i-2..i+2, whether the SP's own
    clock reading (sp.minion_mhz[0], refreshed together with board_w) at i is below one of A2's two reference samples,
    and the SP's minion rail (sp.minion_w[0]): min over i..i+3 less the reading at i-2. Dips against every other sample
    at the same level. Each dip against the samples A2 keeps within 8 samples in the same trace at the same SP clock and
    voltage reading (an artifact reads below them, a real phase at their level). Then
    E143's registered reducer (tools/claims-v3/e143/reduce_e143.py, unchanged) on a copy of session s1 with A2's dips
    removed, cell by cell, governed against pinned (the frozen group; the three session-link cells by their measured
    clock), and the same burst window (kspeed's: 1.5 s after the first launch to the end of the work) read on E80's and
    E83's s1 bursts with and without the dips.
C2  Pool 4 (E140) under the frozen M6, by registered rule (P1 the 14 priority-1 float tiles, P2 the 6 priority-1 int8
    tiles, P3 all 25), beside the all-tile figures, from the registered scorer's committed outputs in score/.
C3  M7u's C0 card term with its own sampling interval: the term recomputed from rows-m7u.json exactly as fit_m7.Fam does
    (per kind and format with E78 and E82 rows and a mean aifoundry3 D above 0.5 W, sum(a*b) / sum(a*a)), then a
    bootstrap over those kind pairs (20,000 draws, seed 139); and X1's gaps across sens-footing.json's grid.
C4  The idle-rest slope's errors-in-variables bracket: F1's rests regenerated at k = 0 (reduce_footing.reduce, the
    registered reducers unchanged, A2 once; outputs in <scratch> only), the within-pass OLS slope (it must equal
    footing.json's) and the reverse regression's slope (die reading on board W, inverted), the bound when the error is
    in the die reading alone.
C5  F4's denominators: sampler files, samples and A2 dips per session of E143, E80 and E83, and the dips inside the
    counted burst windows.
"""
import glob
import gzip
import json
import math
import os
import random
import shutil
import statistics as st
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
DD = os.path.join(ROOT, "docs", "reports", "data")
CV = os.path.join(ROOT, "tools", "claims-v3")
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(CV, "hpl"))
sys.path.insert(0, os.path.join(CV, "kspeed"))
import reduce_footing as RF  # noqa: E402
import reduce_hpl as R  # noqa: E402
import reduce_kspeed as RK  # noqa: E402

E143D = os.path.join(DD, "2026-11-02-e143-blind5-aifoundry2")
E80D = os.path.join(DD, "2026-10-31-e80-kinds-speed")
E83D = os.path.join(DD, "2026-10-31-e83-kinds-speed-rest")
E141D = os.path.join(DD, "2026-11-02-e141-blind5-aifoundry3")
E142D = os.path.join(DD, "2026-11-02-e142-blind5-card1")
GOV_MHZ = 795.0          # E143's frozen grouping: governed = M7 predicts the burst below 795 MHz
LEVEL_W = 55.0
rel = lambda p: os.path.relpath(p, ROOT)
load = lambda p: json.load(open(p))


def records(p):
    op = gzip.open if p.endswith(".gz") else open
    out = []
    with op(p, "rt") as f:
        for ln in f:
            if ln.startswith("{"):
                try:
                    out.append(json.loads(ln))
                except ValueError:
                    pass
    return out


def tel_files(d):
    return sorted(glob.glob(os.path.join(d, "tel", "*.jsonl")) + glob.glob(os.path.join(d, "tel", "*.jsonl.gz")))


def get(r, *path):
    x = r
    for k in path:
        if x is None:
            return None
        if isinstance(k, int):
            x = x[k] if isinstance(x, list) and len(x) > k else None
        else:
            x = x.get(k) if isinstance(x, dict) else None
    return x


# ---------------------------------------------------------------- C5: denominators per session

def per_session(base):
    out = {}
    for d in sorted(glob.glob(os.path.join(base, "**", "tel"), recursive=True)):
        sd = os.path.dirname(d)
        n = nd = fd = 0
        fs = tel_files(sd)
        for p in fs:
            recs = records(p)
            _, bad = RF.drop_dips(recs)
            n += len(recs)
            nd += len(bad)
            fd += bool(bad)
        out[rel(sd)] = {"files": len(fs), "files_with_dips": fd, "samples": n, "a2_dips": nd,
                        "dip_share": (nd / n) if n else None}
    return out


# ---------------------------------------------------------------- C1: what the dips are

def character(files, level_w=LEVEL_W):
    """dips against every other sample at the same level: the sampled clock and the regulator set point changing in
    i-2..i+2, the SP's own clock reading (sp.minion_mhz[0], refreshed with board_w) below one of A2's two reference
    samples, the SP's minion rail, and the size of the drop"""
    acc = {}
    for p in files:
        recs = records(p)
        bad = set(RF.drop_dips(recs)[1])
        B = [r.get("board_w") for r in recs]
        M = [get(r, "mhz", "minion") for r in recs]
        V = [get(r, "reg_mv", "minion") for r in recs]
        S = [get(r, "sp", "minion_mhz", 0) for r in recs]
        L = [get(r, "sp", "minion_w", 0) for r in recs]
        for i in range(2, len(recs) - 4):
            if None in (B[i - 2], B[i], B[i + 2]) or None in M[i - 2:i + 3] or None in L[i - 2:i + 4]:
                continue
            lev = min(B[i - 2], B[i + 2])
            for band in ("all", f"level_ge_{int(level_w)}w"):
                if band != "all" and lev < level_w:
                    continue
                a = acc.setdefault(band, {lab: {"n": 0, "clk": 0, "vset": 0, "vset_n": 0, "still": 0, "spl": 0, "spl_n": 0,
                                                "rail": [], "drop": []} for lab in ("dip", "other")})
                s = a["dip" if i in bad else "other"]
                s["n"] += 1
                clk = len(set(M[i - 2:i + 3])) > 1
                s["clk"] += clk
                vs = None
                if None not in V[i - 2:i + 3]:
                    vs = len(set(V[i - 2:i + 3])) > 1
                    s["vset_n"] += 1
                    s["vset"] += vs
                s["still"] += (not clk) and (vs is not True)
                if None not in (S[i - 2], S[i], S[i + 2]):
                    s["spl_n"] += 1
                    s["spl"] += S[i] < max(S[i - 2], S[i + 2])
                s["rail"].append(min(L[i:i + 4]) - L[i - 2])
                s["drop"].append(lev - B[i])
    out = {}
    for band, a in acc.items():
        out[band] = {}
        for lab, s in a.items():
            n = s["n"]
            out[band][lab] = {"n": n,
                              "clock_change_in_i-2..i+2_share": s["clk"] / n if n else None,
                              "setpoint_change_in_i-2..i+2_share": s["vset"] / s["vset_n"] if s["vset_n"] else None,
                              "no_clock_or_setpoint_change_n": s["still"],
                              "sp_clock_below_a_reference_sample_share": s["spl"] / s["spl_n"] if s["spl_n"] else None,
                              "rail_min_i..i+3_less_i-2_median_w": st.median(s["rail"]) if s["rail"] else None,
                              "level_less_board_median_w": st.median(s["drop"]) if s["drop"] else None}
    return out


def p10_p90(v):
    v = sorted(v)
    return [v[int(0.1 * len(v))], v[int(0.9 * len(v)) - 1]] if len(v) >= 10 else None


def matched_state(files, half=8):
    """each dip against the samples A2 keeps in the same trace within +-half samples whose SP reading (sp.minion_mhz[0],
    sp.minion_mv[0], refreshed with board_w) is the dip's: the dip's board W less their median, beside the dip's drop
    below A2's reference level. A meter artifact reads below the kept samples of its own state; a real phase reads at
    their level."""
    diffs, drops, by, unmatched = [], [], {}, 0
    for p in files:
        recs = records(p)
        bad = set(RF.drop_dips(recs)[1])
        B = [r.get("board_w") for r in recs]
        K = [(get(r, "sp", "minion_mhz", 0), get(r, "sp", "minion_mv", 0)) for r in recs]
        for i in sorted(bad):
            ks = [B[j] for j in range(max(0, i - half), min(len(recs), i + half + 1))
                  if j not in bad and B[j] is not None and K[j] == K[i] and None not in K[i]]
            if not ks:
                unmatched += 1
                continue
            d = B[i] - st.median(ks)
            diffs.append(d)
            drops.append(min(B[i - 2], B[i + 2]) - B[i])
            by.setdefault(str(K[i][0]), []).append(d)
    return {"dips_matched": len(diffs), "dips_unmatched": unmatched, "window_samples": half,
            "dip_less_matched_kept_median_w": st.median(diffs) if diffs else None,
            "dip_less_matched_kept_p10_p90_w": p10_p90(diffs),
            "matched_within_3w_share": sum(abs(x) <= 3 for x in diffs) / len(diffs) if diffs else None,
            "drop_below_reference_median_w": st.median(drops) if drops else None,
            "by_sp_clock_mhz": {k: {"n": len(v), "dip_less_matched_kept_median_w": st.median(v)} for k, v in sorted(by.items())}}


def filtered_session(src, dst):
    """copy a kspeed session directory with A2's dips removed from every sampler trace (tel/*); returns {file: dropped}"""
    if os.path.isdir(dst):
        shutil.rmtree(dst)
    shutil.copytree(src, dst)
    dropped = {}
    for p in tel_files(dst):
        op = gzip.open if p.endswith(".gz") else open
        lines = [ln for ln in op(p, "rt") if ln.startswith("{")]
        recs = []
        for ln in lines:
            try:
                recs.append(json.loads(ln))
            except ValueError:
                recs.append({})
        bad = set(RF.drop_dips(recs)[1])
        if bad:
            dropped[os.path.basename(p)] = len(bad)
        with op(p, "wt") as g:
            for i, ln in enumerate(lines):
                if i not in bad:
                    g.write(ln if ln.endswith("\n") else ln + "\n")
    return dropped


def burst_windows(rd):
    """kspeed's burst window per BURST run (reduce_kspeed.burst_extra's samples): n, mean board W, mean clock"""
    sess, rr, launches, q0 = R.load_session(rd)
    evs = R.sp_events_by_run(rd, sess, rr, q0)
    byrun = {}
    for x in launches:
        byrun.setdefault(x["run"], []).append(x)
    fit = R.fit_clock(evs, launches, sess)
    out = {}
    for r in rr:
        if r.get("block") != "BURST":
            continue
        m = R.run_metrics(rd, r, byrun.get(r["run"], []), evs.get(r["run"]), fit)
        tr = [x for x in (m.get("trace") or []) if m.get("work_s") is not None
              and RK.BURST_FROM_S <= x[0] <= m["work_s"] and x[3] in RK.PTS]
        ws = [x[2] for x in tr if x[2] is not None]
        out[r["run"]] = {"n": len(tr), "w": st.mean(ws) if ws else None, "mhz": st.mean([x[3] for x in tr]) if tr else None}
    return out


def windows_compare(src, scratch, tag):
    dst = os.path.join(scratch, f"{tag}-nodips", os.path.basename(src))
    dropped = filtered_session(src, dst)
    a, b = burst_windows(src), burst_windows(dst)
    runs = sorted(set(a) & set(b))
    n_in = sum(a[r]["n"] for r in runs)
    d_in = sum(a[r]["n"] - b[r]["n"] for r in runs)
    grp = {"governed": [], "pinned": []}
    for r in runs:
        if a[r]["w"] is None or b[r]["w"] is None or a[r]["mhz"] is None:
            continue
        grp["governed" if a[r]["mhz"] < GOV_MHZ else "pinned"].append((a[r]["w"], b[r]["w"]))
    return {"burst_runs": len(runs), "window_samples": n_in, "window_dips": d_in,
            "window_dip_share": d_in / n_in if n_in else None, "samples_dropped_whole_traces": sum(dropped.values()),
            "runs_by_measured_clock": {g: {"n": len(v), "burst_w_kept_mean": st.mean([x for x, _ in v]) if v else None,
                                           "burst_w_a2_removed_mean": st.mean([y for _, y in v]) if v else None,
                                           "shift_mean_w": st.mean([y - x for x, y in v]) if v else None}
                                       for g, v in grp.items()}}


def e143_cells(scratch):
    src = os.path.join(E143D, "aifoundry2", "s1")
    dst = os.path.join(scratch, "e143-cells-nodips", "s1")
    filtered_session(src, dst)
    out = os.path.join(scratch, "e143-cells-nodips", "results-nodips.json")
    r = subprocess.run([sys.executable, os.path.join(CV, "e143", "reduce_e143.py"), dst, "--out", out],
                       cwd=ROOT, capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(r.stderr[-2000:])
    old, new = load(os.path.join(E143D, "results.json")), load(out)
    groups = {}
    for lab, c in old["cells"].items():
        n = new["cells"].get(lab)
        if not n or c.get("burst_w") is None or n.get("burst_w") is None:
            continue
        g = c.get("group") or ("governed" if c["burst_mhz"] < GOV_MHZ else "pinned")
        key = g if c.get("group") else g + "_link"
        groups.setdefault(key, []).append((c["burst_w"], n["burst_w"]))
    summ = {}
    for g, v in sorted(groups.items()):
        summ[g] = {"n": len(v), "burst_w_kept_mean": st.mean([x for x, _ in v]), "burst_w_a2_removed_mean": st.mean([y for _, y in v]),
                   "shift_mean_w": st.mean([y - x for x, y in v]), "shift_range_w": [min(y - x for x, y in v), max(y - x for x, y in v)]}
    for name, parts in (("governed_all", ("governed", "governed_link")), ("pinned_all", ("pinned", "pinned_link"))):
        v = [x for p in parts for x in groups.get(p, [])]
        if v:
            summ[name] = {"n": len(v), "burst_w_kept_mean": st.mean([x for x, _ in v]),
                          "burst_w_a2_removed_mean": st.mean([y for _, y in v]), "shift_mean_w": st.mean([y - x for x, y in v])}
    rules = {k: {"kept": {x: old["score"]["rules"][k].get(x) for x in ("verdict", "rms", "mean_err", "n", "inside")},
                 "a2_removed": {x: new["score"]["rules"].get(k, {}).get(x) for x in ("verdict", "rms", "mean_err", "n", "inside")}}
             for k in ("E143-F1", "E143-F2", "E143-W1", "E143-W2", "E143-W3")}
    return {"cells_by_group": summ, "rules": rules}


def c1_character():
    e141 = sorted(glob.glob(os.path.join(E141D, "aifoundry3", "e141", "p*", "telemetry.jsonl*")))
    e142 = sorted(glob.glob(os.path.join(E142D, "aifoundry1-c1", "e142", "p*", "telemetry.jsonl*")))
    e141 = [p for p in e141 if not p.endswith(".raw")]
    e142 = [p for p in e142 if not p.endswith(".raw")]
    a2 = {"E143 s1": tel_files(os.path.join(E143D, "aifoundry2", "s1")), "E80 s1": tel_files(os.path.join(E80D, "s1")),
          "E83 s1": tel_files(os.path.join(E83D, "s1"))}
    m7 = load(os.path.join(DD, "2026-11-02-q138m-model", "m7.json"))
    return {
        "level_rule": f"level = min(board_w[i-2], board_w[i+2]); the band >= {LEVEL_W} W is where aifoundry2's governor acts",
        "character": {**{f"aifoundry2 {k}": character(v) for k, v in a2.items()},
                      "aifoundry3 E141 (600 MHz pinned)": character(e141),
                      "aifoundry1 card 1 E142 (600 MHz)": character(e142)},
        "matched_sp_state": {**{f"aifoundry2 {k}": matched_state(v) for k, v in a2.items()},
                             "aifoundry3 E141 (600 MHz pinned)": matched_state(e141),
                             "aifoundry1 card 1 E142 (600 MHz)": matched_state(e142)},
        "aifoundry2_cap_w": {"M7_W_star_w": m7["aifoundry2"]["burst_cap"]["W_star_used_w"],
                             "source": "docs/reports/data/2026-11-02-q138m-model/m7.json aifoundry2.burst_cap.W_star_used_w"}}


# ---------------------------------------------------------------- C2: pool 4 by registered rule

def c2():
    out = {}
    for lab in ("committed", "footing"):
        p = load(os.path.join(HERE, "score", f"scored-E140_{lab}_frozen.json"))["primary"]["power"]
        rows = p["rows"]
        rules = {k: {x: v.get(x) for x in ("verdict", "rms", "inside", "n") if x in v} for k, v in p["rules"].items()}
        p1 = p["rules"]["E140-P1"]["tiles"]
        p2 = p["rules"]["E140-P2"]["tiles"]
        e = lambda names: [rows[t]["error"] for t in names]
        fl = [t for t, r in rows.items() if r["type"] != "int8"]
        i8 = [t for t, r in rows.items() if r["type"] == "int8"]
        rms = lambda xs: math.sqrt(sum(x * x for x in xs) / len(xs))
        out[lab] = {"rules": rules,
                    "P1_tiles": len(p1), "P1_bias_meas_minus_pred_w": st.mean(e(p1)), "P1_rms_w": rms(e(p1)),
                    "P2_tiles": len(p2), "P2_bias_meas_minus_pred_w": st.mean(e(p2)), "P2_rms_w": rms(e(p2)),
                    "all_float_tiles": len(fl), "all_float_rms_w": rms(e(fl)), "all_float_bias_w": st.mean(e(fl)),
                    "all_int8_tiles": len(i8), "all_int8_rms_w": rms(e(i8)), "all_int8_bias_w": st.mean(e(i8)),
                    "priority_of_all_tiles": sorted({r["priority"] for r in rows.values()})}
    return out


# ---------------------------------------------------------------- C3: the card term's own interval

def c0_pairs(rows, dkey, fmts):
    by = {}
    for r in rows:
        if r["type"] in fmts and r["exp"] in ("E78", "E82"):
            by.setdefault((r["kind"], r["type"]), {"E78": [], "E82": []})[r["exp"]].append(r[dkey])
    pairs = []
    for (k, t), v in sorted(by.items()):
        if v["E78"] and v["E82"]:
            a, b = st.mean(v["E78"]), st.mean(v["E82"])
            if a > 0.5:
                pairs.append((k, t, a, b))
    return pairs


def boot_scale(pairs, draws=20000, seed=139):
    s = sum(a * b for _, _, a, b in pairs) / sum(a * a for _, _, a, _ in pairs)
    rng = random.Random(seed)
    bs = []
    for _ in range(draws):
        smp = [pairs[rng.randrange(len(pairs))] for _ in pairs]
        bs.append(sum(a * b for _, _, a, b in smp) / sum(a * a for _, _, a, _ in smp))
    bs.sort()
    return {"term": s, "n_pairs": len(pairs), "boot_median": bs[len(bs) // 2],
            "ci95": [bs[int(0.025 * len(bs))], bs[int(0.975 * len(bs)) - 1]], "draws": draws, "seed": seed}


def c3():
    rows = load(os.path.join(HERE, "rows-m7u.json"))
    m7u = load(os.path.join(HERE, "m7u.json"))
    sc = load(os.path.join(HERE, "scores-m7u.json"))["scores"]
    fam_m7u = m7u.get("families", m7u)
    out = {"floats_footing": boot_scale(c0_pairs(rows, "D", ("fp32", "fp16"))),
           "int8_footing": boot_scale(c0_pairs(rows, "D", ("int8",))),
           "floats_m7_rows": boot_scale(c0_pairs(rows, "D_m7", ("fp32", "fp16"))),
           "m7u_json_card1_scale": {f: fam_m7u[f]["card1_scale_by_format"] for f in ("float", "int8") if f in fam_m7u},
           "X1_at_footing": sc["E142_footing_m7u"]["X1"], "X2_at_footing": sc["E142_footing_m7u"]["X2"]}
    x1, t = out["X1_at_footing"], out["floats_footing"]
    out["overlap_floats"] = {"term_ci95_hi": t["ci95"][1], "ratio_lo95": x1["lo95"], "overlap": t["ci95"][1] >= x1["lo95"]}
    grid = load(os.path.join(HERE, "sens-footing.json"))["grid"]
    arms = {}
    for arm, g in grid.items():
        x = g.get("X1_m7u") or {}
        if x.get("verdict") in ("PASS", "FAIL"):
            arms[arm] = {"k_a3": g["k_a3"], "k_c1": g["k_c1"], "verdict": x["verdict"], "term": x["card_term"],
                         "lo95_less_term": x["lo95"] - x["card_term"], "median_less_term": x["median_ratio"] - x["card_term"]}
    per_card = {a: v for a, v in arms.items() if a not in ("both_at_a3_F1", "both_at_c1_F1")}
    fails = [v for v in per_card.values() if v["verdict"] == "FAIL"]
    out["grid"] = {"arms": arms, "per_card_arms_scored": len(per_card), "per_card_fails": len(fails),
                   "per_card_lo95_less_term_range": [min(v["lo95_less_term"] for v in fails), max(v["lo95_less_term"] for v in fails)],
                   "per_card_median_less_term_range": [min(v["median_less_term"] for v in fails),
                                                       max(v["median_less_term"] for v in fails)]}
    return out


# ---------------------------------------------------------------- C4: the slope's errors-in-variables bracket

def within(groups):
    sxx = syy = sxy = 0.0
    for g in groups:
        if len(g) < 2:
            continue
        mt = st.mean([r["t"] for r in g])
        mp = st.mean([r["p"] for r in g])
        for r in g:
            sxx += (r["t"] - mt) ** 2
            syy += (r["p"] - mp) ** 2
            sxy += (r["t"] - mt) * (r["p"] - mp)
    return sxx, syy, sxy


def c4(scratch):
    s4 = os.path.join(scratch, "c4-k0")
    with ThreadPoolExecutor(max_workers=6) as ex:
        res = list(ex.map(lambda e: RF.reduce(e, 0.0, os.path.join(s4, "stage-k0"), s4, "k0"), RF.EXPS))
    bad = [r["exp"] for r in res if r["rc"] != 0]
    rests = {"a3": [], "c1": []}
    for r in res:
        if r["rc"] == 0:
            rests[r["card"]] += RF.rests_from_csv(r["csv"], r["exp"])
    frozen = load(os.path.join(HERE, "footing.json"))["slopes"]
    out = {"failed": bad}
    for c, rs in rests.items():
        by = {}
        for r in rs:
            by.setdefault(r["pass"], []).append(r)
        sxx, syy, sxy = within(list(by.values()))
        tv = sorted({round(r["t"], 3) for r in rs})
        out[c] = {"n_rests": len(rs), "n_passes": len(by), "k_ols": sxy / sxx, "k_frozen": frozen[c]["k_w_per_c"],
                  "k_reverse_regression": syy / sxy, "within_pass_corr": sxy / math.sqrt(sxx * syy),
                  "within_pass_sd_t_c": math.sqrt(sxx / (len(rs) - len(by))),
                  "die_readings_on_0.1c_grid_share": sum(abs(r["t"] * 10 - round(r["t"] * 10)) < 1e-6 for r in rs) / len(rs),
                  "distinct_die_readings": len(tv)}
    return out


def main():
    from concurrent.futures import ProcessPoolExecutor
    scratch = os.path.abspath(sys.argv[1])
    os.makedirs(scratch, exist_ok=True)
    with ProcessPoolExecutor(max_workers=4) as ex:          # the slow re-runs in parallel (at most 5 processes with this one)
        f_cells = ex.submit(e143_cells, scratch)
        f_win = {lab: ex.submit(windows_compare, src, scratch, tag) for lab, src, tag in
                 (("E143 s1", os.path.join(E143D, "aifoundry2", "s1"), "e143"), ("E80 s1", os.path.join(E80D, "s1"), "e80"),
                  ("E83 s1", os.path.join(E83D, "s1"), "e83"))}
        sessions = {"E143": per_session(E143D), "E80": per_session(E80D), "E83": per_session(E83D)}
        dips = c1_character()
        pool4, card = c2(), c3()
        dips["e143_s1_reduced_with_a2_removed"] = f_cells.result()
        dips["burst_windows"] = {lab: f.result() for lab, f in f_win.items()}
    res = {"what": "Q139(u) corrections after verification (post hoc): the checks behind the README's dated notes C1-C5",
           "C5_sessions": sessions, "C1_dips": dips, "C2_pool4": pool4, "C3_card_term": card, "C4_slope_bracket": c4(scratch)}
    json.dump(res, open(os.path.join(HERE, "fix-checks.json"), "w"), indent=1, default=float)
    print(json.dumps(res, indent=1, default=float))


if __name__ == "__main__":
    main()
