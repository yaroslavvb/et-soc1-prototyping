#!/usr/bin/env python3
"""E81 (V3-DP) reduction: the decision rules frozen in dp/predictions.json and dp/README.md, written and tested
BEFORE the first measured pass (on E75's committed passes relabelled, which exercises every path but means nothing).

    python3 tools/claims-v3/dp/reduce_dp.py <pass dir> [<pass dir> ...] --gen <make_dp.py dir>
        --pred tools/claims-v3/dp/predictions.json --out dp.json [--csv runs.csv] [--leak auto|<W per C>]

Per run, E75's machinery unchanged: reduce_hl.runs_of_pass (board power over [t0+1 s, t0+3 s), corrected to the
launch reading with the leakage slope: p80 = p_raw - k (T_window - T_launch)), reduce_mf.ec_fields (the device
record's ops_per_s and bytes_per_s) and reduce_mf.took_ms_window (rule 3's meter-starvation gate). Run gates are
E75's: one clock, voltage within 3 mV of the pass median, an on-protocol launch within 0.5 C of the target, the
window's median took_ms <= 60 ms, an ok device record.

Pass gates (registered): anchor_pi first-to-last drift above 0.3 W sets a pass aside (E75's rule); a pass in
which more than a third of its DRAM runs fail a gate is set aside (E75's rule 3, one level here); the registered
warm-up pass (the first measured pass, `warmup` in predictions.json) is reduced and reported but kept out of the
headline numbers (E75's lesson 5: in E74 and E75 the first pass off an idle card was the one set aside).

Per kept pass, each item's p80 (the mean if an item ran more than once); every registered contrast is a
within-pass difference; the headline is the mean over kept passes with a two-sided t interval on their scatter
(df = n - 1). Watts convert to pJ per 64 B line with the measured line rate (the mean ops_per_s of the pass's
DRAM runs: flw_pat --stride 64 fetches one line per load), never an assumed one.
"""
import argparse
import csv
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "hl"))
sys.path.insert(0, os.path.join(HERE, "..", "mf"))
from reduce_hl import leak_slope, load_jsonl, runs_of_pass  # noqa: E402
from reduce_mf import ci, ec_fields, took_ms_window  # noqa: E402

# the registered contrasts: name -> (plus item, minus item, what it isolates)
CONTRASTS = {
    "arr1": ("dp_s1", "dp_c1", "arrangement at period 1 (no line ever changes): scattered - contiguous"),
    "arr2": ("dp_s2", "dp_c2", "arrangement at period 2 (E75's k256 rung): scattered - contiguous"),
    "arr4": ("dp_s4", "dp_c4", "arrangement at period 4: scattered - contiguous"),
    "arr2r": ("dp_s2r", "dp_c2r", "arrangement at period 2, at random's own counts"),
    "per_c_2to4": ("dp_c4", "dp_c2", "period 2 -> 4, contiguous"),
    "per_s_2to4": ("dp_s4", "dp_s2", "period 2 -> 4, scattered"),
    "per_s_4tolong": ("dp_bern", "dp_s4", "period 4 -> 8,192 distinct lines, scattered"),
    "period_s": ("dp_bern", "dp_s2", "THE PERIOD EFFECT: period 2 -> 8,192 distinct lines, scattered, same counts"),
    "pattern_total": ("dp_bern", "dp_c2", "E75's k256 rung against random bits at the same mean counts"),
    "s1_to_s2": ("dp_s2", "dp_s1", "scattered, period 1 (k 0) -> period 2 (k 256)"),
    "gap_r": ("dp_random", "dp_c2r", "E75's miss, measured: random against a contiguous 2-cycle at its own counts"),
    "resid_r": ("dp_random", "dp_s2r", "what is left of random once the bits are scattered (period 2, its counts)"),
    "random_minus_bern": ("dp_random", "dp_bern", "random floats against random bits (counts 190/288 vs 256/256)"),
    "chord": ("dp_random", "dp_zeros", "E75's DRAM chord, replicated (E75: 3.250 W, SE 0.126)"),
    "c2_minus_zeros": ("dp_c2", "dp_zeros", "E75's k256 rung over zeros, replicated (E75 passes 7511-7514: 1.933 W)"),
    "c1_minus_c2": ("dp_c1", "dp_c2", "E75's k0 rung over its k256 rung, replicated (E75: +0.20 W)"),
}
SHARES = {   # ratios of contrasts, per pass, then the mean and interval of the per-pass ratios
    "arrangement_share_of_pattern_total": ("arr2", "pattern_total"),
    "period_share_of_pattern_total": ("period_s", "pattern_total"),
    "arrangement_share_of_gap_r": ("arr2r", "gap_r"),
    "resid_share_of_gap_r": ("resid_r", "gap_r"),
}


def classify(c, present_min, absent_half):
    """present: mean >= present_min and the 95 % interval excludes 0; absent: the interval lies inside
    +-absent_half; otherwise unresolved."""
    if c["mean"] is None or c["lo"] is None:
        return "unresolved"
    if c["mean"] >= present_min and c["lo"] > 0:
        return "present"
    if c["mean"] <= -present_min and c["hi"] < 0:
        return "present_negative"
    if c["lo"] >= -absent_half and c["hi"] <= absent_half:
        return "absent"
    return "unresolved"


def inside(c, lohi):
    return None if c.get("mean") is None else bool(lohi[0] <= c["mean"] <= lohi[1])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dirs", nargs="+")
    ap.add_argument("--gen", required=True)
    ap.add_argument("--pred", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--csv")
    ap.add_argument("--leak", default="auto")
    ap.add_argument("--warmup", type=int, default=None, help="override predictions.json's warm-up pass (tests)")
    a = ap.parse_args()

    pred = json.load(open(a.pred))
    warmup = a.warmup if a.warmup is not None else pred["decision"]["warmup_pass"]
    gen_man = json.load(open(os.path.join(a.gen, "manifest.json")))
    man = {it["name"]: it for it in gen_man["items"]}
    counts = {}
    cp = os.path.join(a.gen, "counts.json")
    if os.path.exists(cp):
        counts = json.load(open(cp))

    R, card = [], None
    for d in a.dirs:
        rr, c = runs_of_pass(d, man)
        card = card or c
        ec = ec_fields(d)
        for r in rr:
            r.update(ec.get((r["pass"], r["item"], r["pos"], r["attempt"]), {}))
        by = {}
        for x in load_jsonl(os.path.join(d, "runs.jsonl")):
            key = (x["block"], x["item"], x.get("pos", 0), x.get("attempt", 1))
            by[key] = min(by.get(key, x["t_start_ms"]), x["t_start_ms"])
        for r in rr:
            r["_t0_ms"] = by.get((r["pass"], r["item"], r["pos"], r["attempt"]))
        took_ms_window(d, rr)
        R += rr
    if not R:
        raise SystemExit("no runs: is telemetry.jsonl(.gz) in the pass directories?")

    k_leak, nk = leak_slope(R) if a.leak == "auto" else (float(a.leak), -1)
    clocks = sorted({m for r in R for m in r["mhz"]})
    mv_med = {p: float(np.median([r["mv"] for r in R if r["pass"] == p])) for p in {r["pass"] for r in R}}
    for r in R:
        it = man.get(r["item"], {})
        r["p80"] = r["p_raw"] - k_leak * (r["t_win"] - r["start_c"])
        r["k"], r["w"] = it.get("k"), it.get("w")
        r["arm"] = "drift" if r["kind"] == "fma" else "dram"
        fails = []
        if len(r["mhz"]) != 1 or r["mhz"][0] != (clocks[0] if clocks else None):
            fails.append("clock")
        if abs(r["mv"] - mv_med[r["pass"]]) > 3:
            fails.append("voltage")
        if not r["on_protocol"] or (r["target"] is not None and abs(r["start_c"] - r["target"]) > 0.5):
            fails.append("approach")
        if r["arm"] != "drift":
            if r.get("took_ms_med") is not None and r["took_ms_med"] > 60:
                fails.append("burst")
            if not r.get("ok", True) or not r.get("launches"):
                fails.append("record")
        r["fails"] = fails

    all_passes = sorted({r["pass"] for r in R})
    drift, set_aside = {}, {}
    for p in all_passes:
        anc = sorted([r for r in R if r["pass"] == p and r["kind"] == "fma"], key=lambda r: r["pos"])
        drift[p] = (anc[-1]["p80"] - anc[0]["p80"]) if len(anc) >= 2 else None
        if drift[p] is not None and abs(drift[p]) > 0.3:
            set_aside[p] = "anchor_pi drift %.3f W" % drift[p]
        at = [r for r in R if r["pass"] == p and r["arm"] == "dram"]
        nf = sum(1 for r in at if r["fails"])
        if at and nf > len(at) / 3.0:
            set_aside[p] = set_aside.get(p, "") + ("; " if p in set_aside else "") + \
                "%d of %d DRAM runs fail a gate" % (nf, len(at))
    healthy = [p for p in all_passes if p not in set_aside]
    headline = [p for p in healthy if p != warmup]
    G = [r for r in R if r["pass"] in healthy and not r["fails"]]

    def item_p80(p, name):
        v = [r["p80"] for r in G if r["pass"] == p and r["item"] == name]
        return float(np.mean(v)) if v else None

    def rate(p):
        v = [r["ops_per_s"] for r in G if r["pass"] == p and r["arm"] == "dram" and r.get("ops_per_s")]
        return float(np.mean(v)) if v else None

    names = [n for n, it in man.items() if it["kind"] == "cmd"]
    per_pass = {}
    for p in healthy:
        row = {"items_W": {n: item_p80(p, n) for n in names}, "lines_per_s": rate(p),
               "bytes_per_s": (float(np.mean([r["bytes_per_s"] for r in G if r["pass"] == p and r["arm"] == "dram"
                                               and r.get("bytes_per_s")])) if rate(p) else None),
               "drift_W": drift.get(p), "contrasts_W": {}}
        for cn, (plus, minus, _) in CONTRASTS.items():
            x, y = row["items_W"].get(plus), row["items_W"].get(minus)
            row["contrasts_W"][cn] = (x - y) if (x is not None and y is not None) else None
        row["shares"] = {}
        for sn, (num, den) in SHARES.items():
            x, y = row["contrasts_W"].get(num), row["contrasts_W"].get(den)
            row["shares"][sn] = (x / y) if (x is not None and y not in (None, 0.0)) else None
        per_pass[p] = row

    def summarize(passes):
        out = {"passes": passes}
        lps = [per_pass[p]["lines_per_s"] for p in passes if per_pass[p]["lines_per_s"]]
        lr = float(np.mean(lps)) if lps else None
        out["lines_per_s"] = lr
        out["line_bytes_per_s"] = (64.0 * lr) if lr else None
        out["items_W"] = {n: ci([per_pass[p]["items_W"][n] for p in passes]) for n in names}
        out["items_over_zeros_W"] = {n: ci([(per_pass[p]["items_W"][n] - per_pass[p]["items_W"]["dp_zeros"])
                                           for p in passes if per_pass[p]["items_W"].get(n) is not None
                                           and per_pass[p]["items_W"].get("dp_zeros") is not None])
                                     for n in names}
        out["contrasts_W"] = {}
        out["contrasts_pJ_per_line"] = {}
        for cn, (plus, minus, what) in CONTRASTS.items():
            c = ci([per_pass[p]["contrasts_W"][cn] for p in passes])
            c["what"] = what
            c["plus"], c["minus"] = plus, minus
            out["contrasts_W"][cn] = c
            out["contrasts_pJ_per_line"][cn] = {k: ((c[k] / lr * 1e12) if (c.get(k) is not None and lr) else None)
                                                for k in ("mean", "se", "lo", "hi")}
        out["shares"] = {sn: ci([per_pass[p]["shares"][sn] for p in passes]) for sn in SHARES}
        return out

    head = summarize(headline)
    every = summarize(healthy)
    C = head["contrasts_W"]
    P = pred["predictions"]
    D = pred["decision"]
    pm, ah = D["present_min_W"], D["absent_half_W"]
    cls = {cn: classify(C[cn], pm, ah) for cn in C}
    min_passes = D.get("min_headline_passes", 4)
    if len(headline) < min_passes:   # rule 5: too few headline passes -> every verdict unresolved
        cls = {cn: "unresolved" for cn in C}

    scored = {}
    for key, spec in P.items():
        c = C[spec["contrast"]]
        if spec["test"] == "range":
            ok = inside(c, spec["range"])
        elif spec["test"] == "present":
            ok = None if c["mean"] is None else (cls[spec["contrast"]] == "present")
        elif spec["test"] == "absent":
            ok = None if c["mean"] is None else (cls[spec["contrast"]] == "absent")
        else:
            raise SystemExit("unknown test " + spec["test"])
        if len(headline) < min_passes:
            ok = None
        scored[key] = {"claim": spec["claim"], "contrast": spec["contrast"], "test": spec["test"],
                       "registered": spec.get("range", spec["test"]), "mean_W": c["mean"],
                       "interval_W": [c["lo"], c["hi"]], "se_W": c["se"], "n": c["n"],
                       "class": cls[spec["contrast"]], "pass": ok}

    # the hub's question, by the registered rule: is a two-value alternating image cheaper than random data at the
    # same counts BECAUSE it repeats? period_s decides; the arrangement contrasts say what else differs.
    hub = {"question": pred["hub_question"],
           "period_effect": {"contrast": "period_s", "class": cls["period_s"], **{k: C["period_s"][k]
                                                                                    for k in ("mean", "lo", "hi")}},
           "arrangement_effect": {"contrast": "arr2", "class": cls["arr2"], **{k: C["arr2"][k]
                                                                              for k in ("mean", "lo", "hi")}},
           "verdict": None}
    pe, ae = cls["period_s"], cls["arr2"]
    if pe == "present" and ae != "present":
        hub["verdict"] = "the period: a two-value image is cheaper because it repeats"
    elif ae == "present" and pe != "present":
        hub["verdict"] = "the arrangement: the repetition costs nothing; scattered ones inside a line cost"
    elif ae == "present" and pe == "present":
        hub["verdict"] = "both: the repetition and the arrangement each cost (shares in shares.*)"
    elif pe == "absent" and ae == "absent":
        hub["verdict"] = "neither: the gap is not in the pattern of a 256/256 image (see random_minus_bern)"
    else:
        hub["verdict"] = "unresolved at the registered thresholds"

    # derived, reported and NOT scored: the arrangement contrasts per changed-piece of a hypothetical in-order
    # narrow path (counts.json beat16/beat32/beat64: toggles between consecutive 16/32/64-bit pieces of the
    # stream). If the arrangement costs, this is what it costs per toggle on such a path, at each period.
    derived = {}
    if counts:
        lr = head["lines_per_s"]
        for cn in ("arr1", "arr2", "arr4", "arr2r"):
            plus, minus = CONTRASTS[cn][0], CONTRASTS[cn][1]
            row = {}
            for b in ("beat16", "beat32", "beat64"):
                if plus in counts and minus in counts and lr and C[cn]["mean"] is not None:
                    dt = counts[plus][b] - counts[minus][b]
                    row[b + "_toggles_per_line_added"] = dt
                    row[b + "_pJ_per_toggle"] = (C[cn]["mean"] / lr * 1e12 / dt) if dt else None
            derived[cn] = row

    res = {"exp": "E81", "card": card, "dirs": a.dirs, "warmup_pass": warmup, "passes_all": all_passes,
           "passes_healthy": healthy, "passes_headline": headline, "passes_set_aside": set_aside,
           "anchor_drift_W": drift,
           "gates": {"runs": len(R), "kept": len(G), "clocks_mhz": clocks, "leak_W_per_C": k_leak, "leak_runs": nk,
                     "failures": dict(sorted(((f, sum(1 for r in R if f in r["fails"]))
                                              for f in {f for r in R for f in r["fails"]}))) or {},
                     "took_ms_med_max": max([r.get("took_ms_med") or 0 for r in R])},
           "headline": head, "with_warmup": every, "classes": cls, "scored": scored, "hub": hub,
           "derived_not_scored": derived, "counts": counts, "per_pass": per_pass}
    json.dump(res, open(a.out, "w"), indent=1, default=float)

    if a.csv:
        cols = ["card", "pass", "item", "arm", "k", "w", "pos", "attempt", "start_c", "t_win", "on_protocol",
                "p_raw", "p80", "rail", "mv", "ops_per_s", "bytes_per_s", "took_ms_med", "fails"]
        with open(a.csv, "w", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(cols)
            for r in sorted(R, key=lambda r: (r["pass"], r["pos"])):
                w.writerow([("|".join(r[c]) if c == "fails" else r.get(c)) for c in cols])

    print("E81 %s: %d runs, %d kept, healthy passes %s, headline %s, set aside %s, leak %.4f W/C (%d runs)"
          % (card, len(R), len(G), healthy, headline, set_aside, k_leak, nk))
    for cn, c in C.items():
        if c["mean"] is not None:
            print("  %-18s %+.3f W [%+.3f, %+.3f] n=%d  %s" % (cn, c["mean"], c["lo"] if c["lo"] is not None else
                                                              float("nan"), c["hi"] if c["hi"] is not None else
                                                              float("nan"), c["n"], cls[cn]))
    for k_, v in scored.items():
        print("  %-28s %s" % (k_, v["pass"]))
    print("  hub: %s" % hub["verdict"])


if __name__ == "__main__":
    main()
