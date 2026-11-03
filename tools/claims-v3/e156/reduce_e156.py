#!/usr/bin/env python3
"""E156 reduction: the decision rules frozen in e156/predictions-e156.json and e156/README.md, written and tested BEFORE the first measured
pass (selftest_e156.py: E139's committed passes, which must give E139's committed contrasts exactly; a pipeline test, no E156 result).

    python3 tools/claims-v3/e156/reduce_e156.py <pass dir> [...] --gen <make_e156.py dir> --pred tools/claims-v3/e156/predictions-e156.json
        --out e156.json [--csv runs.csv] [--leak auto|<W per C>] [--warmup N]

The estimator, windows, run gates and pass rules are E139's, which are E132's and E110's, UNCHANGED: the code from reduce_e132.main() up to
its verdicts is copied below line for line (marked), with E132's own helpers imported, not copied (reduce_hl.runs_of_pass, leak_slope,
reduce_mf.ec_fields, took_ms_window, ci, reduce_e110.extra_of_pass, value; reduce_e132.cls_t, cls_nonzero, cls_ddr). New here: E156's
contrasts (E132's family-E contrasts, unchanged, plus the two new pairs, every coefficient computed from the images' own counts), and the
rules N1, N2, C1 and D (README section "Rules").
"""
import argparse
import csv
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
for sub in ("hl", "mf", "e110", "e132"):
    sys.path.insert(0, os.path.join(HERE, "..", sub))
from reduce_hl import leak_slope, load_jsonl, runs_of_pass  # noqa: E402
from reduce_mf import ci, ec_fields, took_ms_window  # noqa: E402
from reduce_e110 import extra_of_pass, value  # noqa: E402  (E110's rail and die-rail windows, unchanged)
from reduce_e132 import cls_ddr, cls_nonzero, cls_t  # noqa: E402  (E132's classes, unchanged)

COLS = ("board", "noc", "sram", "minion", "off", "ddr_mv")
RAILS = ("noc", "sram", "minion")
HP = {"c3_64": 0.5, "wl_64": -0.5, "c3_128": 0.5, "wl_128": -0.5}       # E132's Hp: 192 pins high at equal toggles, both rungs
PAIRS = {"E56": ("eh_64", "el_64"), "E448": ("vl_64", "c3_64"), "E192": ("vl_128", "c3_128"),     # E132's three
         "E7": ("e7_64", "e2_64"), "E32": ("eh_32", "el_32")}                                       # E156's two new
READINGS = ("A", "B", "C", "E", "F")
DDR_NAME = {"E56": "RE64", "E448": "RE448", "E192": "RE128", "E7": "RE7", "E32": "RE32"}   # E132's names for its first and third


def pair_counts(counts, x, y):
    cx, cy = counts["items"][x], counts["items"][y]
    d = {k: cx[k] - cy[k] for k in ("hi", "t_enc", "e32", "e64", "e128", "tx_enc", "w", "t_raw", "r32", "r64", "r128", "half")}
    d["e64_plus_e128"] = d["e64"] + d["e128"]
    return d


def build_contrasts(counts, names):
    """Every contrast, as {item: coefficient}. The encoded residual of a pair (x, y) with equal raw counts is E132's
    (x - y) - (d_t_enc / 496) V16 - (d_hi / 192) Hp, with V16 = dm_a44 - dm_u4 (496 pin toggles) and Hp as E132's; d_ the pair's count
    differences from the images' own bytes (gen/counts.json). For E132's three pairs this is E132's formula exactly (98/496 and 32/192;
    42/496 for E192)."""
    C = {}

    def add(name, spec, what):
        if all(i in names for i in spec):
            C[name] = (spec, what)

    add("S64", {"wl_64": 1, "dm_l08": -1}, "E110's S64: 64-bit blocks of 0x00/0xFF over lanes-constant")
    add("S128", {"wl_128": 1, "dm_l08": -1}, "E110's S128")
    add("V16", {"dm_a44": 1, "dm_u4": -1}, "E110's V16: 496 pin toggles (beats 0x0F0F/0xF0F0 over 0x0F)")
    add("V64", {"vl_64": 1, "dm_u4": -1}, "E110's V64")
    add("V128", {"vl_128": 1, "dm_u4": -1}, "E110's V128")
    add("U4z", {"dm_u4": 1, "dp_zeros": -1}, "every byte 0x0F over zeros")
    add("Hp", dict(HP), "192 pins driven high at equal toggles (C3 over W, both rungs)")
    add("RH64", {"c3_64": 1, "wl_64": -1}, "192 pins high at the 64-bit rung")
    add("RH128", {"c3_128": 1, "wl_128": -1}, "192 pins high at the 128-bit rung")
    for pn, (x, y) in PAIRS.items():
        if x not in names or y not in names:
            continue
        d = pair_counts(counts, x, y)
        add("P" + pn[1:], {x: 1, y: -1}, "%s - %s: encoded 64-bit toggles %+.0f, 32-bit %+.0f, pins %+.0f, high %+.0f" % (
            x, y, d["e64"], d["e32"], d["t_enc"], d["hi"]))
        s = {x: 1.0, y: -1.0, "dm_a44": -d["t_enc"] / 496.0, "dm_u4": d["t_enc"] / 496.0}
        for it, c in HP.items():
            s[it] = s.get(it, 0.0) - (d["hi"] / 192.0) * c
        s = {i: c for i, c in s.items() if abs(c) > 1e-15}
        add(pn, s, "the encoded residual: %s - %s - (%.0f/496) V16 - (%.0f/192) Hp" % (x, y, d["t_enc"], d["hi"]))
        add(DDR_NAME[pn], {x: 1, y: -1}, "the DDR die rail on %s - %s" % (x, y))
    for n in names:
        if n != "dp_zeros":
            add(n + "z", {n: 1, "dp_zeros": -1}, n + " over zeros")
    return C


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dirs", nargs="+")
    ap.add_argument("--gen", required=True)
    ap.add_argument("--pred", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--csv")
    ap.add_argument("--leak", default="auto")
    ap.add_argument("--warmup", type=int, default=None)
    ap.add_argument("--label", default="E156")
    a = ap.parse_args()
    pred = json.load(open(a.pred))
    D_ = pred["decision"]
    warmup = a.warmup if a.warmup is not None else D_["warmup_pass"]
    man = {it["name"]: it for it in json.load(open(os.path.join(a.gen, "manifest.json")))["items"]}
    counts = json.load(open(os.path.join(a.gen, "counts.json")))

    # ---- E132's estimator, gates and pass rules: reduce_e132.main(), copied unchanged from here ... -------------------------------
    R, card = [], None
    for d in a.dirs:
        rr, c = runs_of_pass(d, man)
        card = card or c
        ec = ec_fields(d)
        ex = extra_of_pass(d)
        for r in rr:
            r.update(ec.get((r["pass"], r["item"], r["pos"], r["attempt"]), {}))
            r.update(ex.get((r["pass"], r["item"], r["pos"], r["attempt"]), {}))
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
        r["level"] = it.get("level")
        r["arm"] = "drift" if r["kind"] == "fma" else "mem"
        if r.get("noc") is not None:
            r["board"] = r["p80"]
            r["off"] = r["p80"] - r["noc"] - r["sram"] - r["minion"]
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
            if r.get("noc") is None:
                fails.append("rails")
        r["fails"] = fails

    all_passes = sorted({r["pass"] for r in R})
    drift, set_aside = {}, {}
    for p in all_passes:
        anc = sorted([r for r in R if r["pass"] == p and r["kind"] == "fma"], key=lambda r: r["pos"])
        drift[p] = (anc[-1]["p80"] - anc[0]["p80"]) if len(anc) >= 2 else None
        if drift[p] is not None and abs(drift[p]) > 0.3:
            set_aside[p] = "anchor_pi drift %.3f W" % drift[p]
        at = [r for r in R if r["pass"] == p and r["arm"] == "mem"]
        nf = sum(1 for r in at if r["fails"])
        if at and nf > len(at) / 3.0:
            set_aside[p] = set_aside.get(p, "") + ("; " if p in set_aside else "") + "%d of %d memory runs fail a gate" % (nf, len(at))
    healthy = [p for p in all_passes if p not in set_aside]
    headline = [p for p in healthy if p != warmup]
    G = [r for r in R if r["pass"] in healthy and not r["fails"]]

    def item_of(p, name, field):
        v = [r[field] for r in G if r["pass"] == p and r["item"] == name and r.get(field) is not None]
        return float(np.mean(v)) if v else None

    names = [n for n, it in man.items() if it["kind"] == "cmd"]
    # ---- ... to here (E156: the contrasts are built here, from E156's images; E132 built them before reading the passes) ----------
    CONTRASTS = build_contrasts(counts, set(names))
    per_pass = {}
    for p in healthy:
        cols = {c: {n: item_of(p, n, c) for n in names} for c in COLS}
        v = [r["ops_per_s"] for r in G if r["pass"] == p and r["level"] == "dram" and r.get("ops_per_s")]
        per_pass[p] = {"items": cols, "lines_per_s": float(np.mean(v)) if v else None, "drift_W": drift.get(p),
                       "contrasts": {c: {cn: value(cols[c], s) for cn, (s, _) in CONTRASTS.items()} for c in COLS}}

    def summarize(passes):
        out = {"passes": passes, "line_rate_by_item": {}}
        v = [per_pass[p]["lines_per_s"] for p in passes if per_pass[p]["lines_per_s"]]
        out["lines_per_s"] = float(np.mean(v)) if v else None
        for n in names:
            v = [r["ops_per_s"] for r in G if r["pass"] in passes and r["item"] == n and r.get("ops_per_s")]
            out["line_rate_by_item"][n] = float(np.mean(v)) if v else None
        out["items_W"] = {n: ci([per_pass[p]["items"]["board"][n] for p in passes if per_pass[p]["items"]["board"][n] is not None])
                          for n in names}
        out["contrasts"] = {c: {} for c in COLS}
        for c in COLS:
            for cn, (s, what) in CONTRASTS.items():
                x = ci([v for v in (per_pass[p]["contrasts"][c][cn] for p in passes) if v is not None])
                if c == "board":
                    x["what"], x["items"] = what, s
                out["contrasts"][c][cn] = x
        return out
    # ---- (summarize: reduce_e132's, without its over_zeros table, which the <item>z contrasts carry) -------------------------------

    head = summarize(headline)
    every = summarize(healthy)
    C = head["contrasts"]
    B = C["board"]
    enough = len(headline) >= D_["min_headline_passes"]
    lr = head["lines_per_s"]
    m = lambda cn, col="board": C[col][cn]["mean"] if cn in C[col] else None
    iv = lambda cn, col="board": [C[col][cn]["lo"], C[col][cn]["hi"]] if cn in C[col] else [None, None]
    PR = pred["prices"]
    tol = D_["within_W"]
    V = {}

    def pred_W(pn, reading):
        """A reading's frozen prediction for a pair's encoded residual, at this session's line rate (W)."""
        if lr is None:
            return None
        cnt = pred["pairs"][pn]["counts"][PR[reading]["count"]]
        return PR[reading]["pJ"] * 1e-12 * cnt * lr

    def score(pn, reading="A"):
        mu, (lo, hi) = m(pn), iv(pn)
        p = pred_W(pn, reading)
        if not enough or mu is None or p is None:
            return {"predicted_W": p, "mean_W": mu, "interval_W": [lo, hi], "error_W": None, "verdict": "NOT-SCORED"}
        err = mu - p
        if lo is not None and lo >= p - tol and hi <= p + tol:
            dec = "decided: the 95%% interval lies inside the prediction +- %.2f W" % tol
        elif lo is not None and (lo > p + tol or hi < p - tol):
            dec = "decided: the 95%% interval lies wholly outside the prediction +- %.2f W" % tol
        else:
            dec = "not decided by the interval: it straddles the prediction +- %.2f W" % tol
        return {"predicted_W": p, "mean_W": mu, "interval_W": [lo, hi], "error_W": err, "abs_error_W": abs(err),
                "within_W": tol, "verdict": "PASS" if abs(err) <= tol else "FAIL", "interval_reading": dec,
                "contains_prediction": (lo is not None and lo <= p <= hi)}

    # N1, the critic's rule on the two new images: E139's frozen price per encoded 64-bit toggle (reading A) predicts each residual
    n1 = {pn: score(pn, "A") for pn in pred["rules"]["N1"]["pairs"]}
    vs = [x["verdict"] for x in n1.values()]
    V["N1_new_images"] = {"pairs": n1, "verdict": "NOT-SCORED" if "NOT-SCORED" in vs else ("PASS" if all(v == "PASS" for v in vs) else "FAIL")}

    # C1, E139's own images on this card: the same price and the same rule
    c1 = {pn: score(pn, "A") for pn in pred["rules"]["C1"]["pairs"]}
    half = D_["board_absent_half_W"]
    c56 = cls_nonzero(B["E56"], half) if enough else "unresolved"
    c448 = cls_nonzero(B["E448"], half) if enough else "unresolved"
    if not enough:
        r4 = "UNRESOLVED"
    elif c56 == "present" and c448 == "present":
        r4 = "PAYS"
    elif c56 == "absent" and c448 == "absent":
        r4 = "NONE"
    elif c448 == "present" and c56 == "absent":
        r4 = "AT-HIGH-RAW-ONLY"
    elif c56 == "present" and c448 == "absent":
        r4 = "AT-LOW-RAW-ONLY"
    else:
        r4 = "UNRESOLVED"
    vs = [x["verdict"] for x in c1.values()]
    V["C1_card_transfer"] = {"pairs": c1, "E132_R4_reading": r4, "E132_R4_classes": {"E56": c56, "E448": c448},
                             "against_E132_frozen_0185": {pn: (m(pn) - pred["E132_frozen_W"]) if (enough and m(pn) is not None) else None
                                                          for pn in ("E56", "E448")},
                             "verdict": "NOT-SCORED" if "NOT-SCORED" in vs else ("PASS" if all(v == "PASS" for v in vs) else "FAIL")}

    # N2, the width reading, inside this session (free of the card's price): for each reading X and pair, per pass
    # d_X = E_pair - k_X * (E56 + E448) / 2, k_X = the pair's count over E56's count under X; X is consistent on the pair when the 95%
    # interval of d_X over the headline passes contains 0. Beside it, each reading's absolute prediction at aifoundry3's price (reported).
    n2 = {}
    for pn in PAIRS:
        mu, (lo, hi) = m(pn), iv(pn)
        row = {"mean_W": mu, "interval_W": [lo, hi]}
        for rd in READINGS:
            cnt = pred["pairs"][pn]["counts"][PR[rd]["count"]]
            k = cnt / pred["pairs"]["E56"]["counts"][PR[rd]["count"]]
            dv = [per_pass[p]["contrasts"]["board"][pn] - k * 0.5 * (per_pass[p]["contrasts"]["board"]["E56"] + per_pass[p]["contrasts"]["board"]["E448"])
                  for p in headline if pn in per_pass[p]["contrasts"]["board"]
                  and None not in (per_pass[p]["contrasts"]["board"][pn], per_pass[p]["contrasts"]["board"].get("E56"),
                                   per_pass[p]["contrasts"]["board"].get("E448"))]
            dd = ci(dv)
            row[rd] = {"k": k, "d_W": dd, "consistent": bool(enough and dd["lo"] is not None and dd["lo"] <= 0.0 <= dd["hi"]),
                       "absolute_prediction_W": pred_W(pn, rd)}
        n2[pn] = row
    test = pred["rules"]["N2"]["pairs"]
    cons = [rd for rd in READINGS if all(n2[pn][rd]["consistent"] for pn in test if pn in n2)]
    if not enough or any(m(pn) is None for pn in test):
        n2v = "NOT-SCORED"
    elif not cons:
        n2v = "NONE"
    elif len(cons) == 1:
        n2v = cons[0] + " ONLY"
    else:
        n2v = "SEVERAL: " + ",".join(cons)
    V["N2_width"] = {"pairs": n2, "tested_on": test, "consistent_readings": cons, "verdict": n2v,
                     "E32_alone": [rd for rd in READINGS if n2["E32"][rd]["consistent"]] if m("E32") is not None else None,
                     "E192_alone": [rd for rd in READINGS if n2["E192"][rd]["consistent"]] if m("E192") is not None else None}

    # D, read DBI evident on this card: the pins held high pay as on aifoundry3 (E132's board class at 0.10 W)
    hp = cls_t(B["Hp"], D_["board_present_W"]) if enough else "unresolved"
    V["D_dbi_evident"] = {"Hp": {"class": hp, "mean_W": m("Hp"), "interval_W": iv("Hp")},
                          "verdict": "NOT-SCORED" if not enough else ("EVIDENT" if hp == "present" else ("NOT EVIDENT" if hp == "absent" else "UNRESOLVED"))}

    # reported: the ties against E139's aifoundry3 values, the prices on this card, the DDR die rail, where each is paid
    ties = {}
    for cn, ref in pred["E139_ties_W"].items():
        ties[cn] = {"E139_W": ref, "mean_W": m(cn), "interval_W": iv(cn), "card1_minus_E139_W": (m(cn) - ref) if m(cn) is not None else None}
    V["ties_vs_E139"] = ties
    pj = {}
    for pn in PAIRS:
        cnt = pred["pairs"][pn]["counts"]["e64"]
        pj[pn] = (m(pn) / (cnt * lr) * 1e12) if (m(pn) is not None and lr and cnt) else None
    V["pJ_per_encoded_64bit_toggle"] = pj
    ddr = lambda cn: cls_ddr(C["ddr_mv"][cn], D_["ddr_moves_mV"], D_["ddr_still_half_mV"]) if (enough and cn in C["ddr_mv"]) else "unresolved"
    dn = ["RE64", "RE448", "RE128", "RE7", "RE32", "RH64", "RH128"] + [n + "z" for n in names if n != "dp_zeros"]
    V["ddr_die_rail"] = {cn: {"class": ddr(cn), "mean_mV": m(cn, "ddr_mv"), "interval_mV": iv(cn, "ddr_mv")} for cn in dn if cn in C["ddr_mv"]}
    where = {}
    for cn in ("Hp", "V16", "S64", "V64", "E56", "E448", "E192", "E7", "E32", "P56", "P448", "P192", "P7", "P32"):
        if cn not in B:
            continue
        rs = ci([sum(per_pass[p]["contrasts"][c][cn] for c in RAILS) for p in headline
                 if all(per_pass[p]["contrasts"][c][cn] is not None for c in RAILS)])
        where[cn] = {"board_W": m(cn), "rails_sum": rs, "off": C["off"][cn], "noc": C["noc"][cn], "sram": C["sram"][cn],
                     "minion": C["minion"][cn], "ddr_mV": C["ddr_mv"][cn]}
    V["where"] = where

    res = {"exp": a.label, "card": card, "dirs": a.dirs, "leak_arm": a.leak, "warmup_pass": warmup, "passes_all": all_passes,
           "passes_healthy": healthy, "passes_headline": headline, "passes_set_aside": set_aside, "anchor_drift_W": drift,
           "gates": {"runs": len(R), "kept": len(G), "clocks_mhz": clocks, "leak_W_per_C": k_leak, "leak_runs": nk,
                     "failures": dict(sorted(((f, sum(1 for r in R if f in r["fails"])) for f in {f for r in R for f in r["fails"]}))) or {},
                     "took_ms_med_max": max([r.get("took_ms_med") or 0 for r in R])},
           "headline": head, "with_warmup": every, "verdicts": V, "per_pass": per_pass}
    json.dump(res, open(a.out, "w"), indent=1, default=float)

    if a.csv:
        cols = ["card", "pass", "item", "level", "arm", "pos", "attempt", "start_c", "t_win", "on_protocol", "p_raw", "p80",
                "noc", "sram", "minion", "off", "ddr_mv", "mv", "ops_per_s", "took_ms_med", "fails"]
        with open(a.csv, "w", newline="") as fh:
            wcsv = csv.writer(fh)
            wcsv.writerow(cols)
            for r in sorted(R, key=lambda r: (r["pass"], r["pos"])):
                wcsv.writerow([("|".join(r[c]) if c == "fails" else r.get(c)) for c in cols])

    print("%s %s: %d runs, %d kept, healthy %s, headline %s, set aside %s, leak %.4f W/C (%d runs), lines/s %s"
          % (a.label, card, len(R), len(G), healthy, headline, set_aside, k_leak, nk, lr))
    for cn in ("V16", "Hp", "S64", "S128", "V64", "V128", "U4z", "P56", "P448", "P192", "P7", "P32", "E56", "E448", "E192", "E7", "E32"):
        c = B.get(cn)
        if c and c["mean"] is not None:
            print("  %-5s %+.3f W [%s, %s] n=%d | ddr %+.2f mV" % (
                cn, c["mean"], "%+.3f" % c["lo"] if c["lo"] is not None else "n/a", "%+.3f" % c["hi"] if c["hi"] is not None else "n/a",
                c["n"], C["ddr_mv"][cn]["mean"] if C["ddr_mv"][cn]["mean"] is not None else float("nan")))
    for k_ in ("N1_new_images", "C1_card_transfer"):
        print("  %-18s %s %s" % (k_, V[k_]["verdict"], " ".join("%s: pred %s err %s %s" % (
            pn, "%.3f" % x["predicted_W"] if x["predicted_W"] is not None else "n/a",
            "%+.3f" % x["error_W"] if x["error_W"] is not None else "n/a", x["verdict"]) for pn, x in V[k_]["pairs"].items())))
    print("  N2_width           %s (E32 alone: %s)" % (V["N2_width"]["verdict"], V["N2_width"]["E32_alone"]))
    print("  D_dbi_evident      %s" % V["D_dbi_evident"]["verdict"])


if __name__ == "__main__":
    main()
