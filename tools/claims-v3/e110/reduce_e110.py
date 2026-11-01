#!/usr/bin/env python3
"""E110 reduction: the decision rules frozen in e110/predictions.json and e110/README.md, written and tested BEFORE the first measured pass
(selftest_e110.py: E99's committed passes relabelled, a pipeline test that means nothing).

    python3 tools/claims-v3/e110/reduce_e110.py <pass dir> [...] --gen <make_e110.py dir> --pred tools/claims-v3/e110/predictions.json
        --out e110.json [--csv runs.csv] [--leak auto|<W per C>] [--warmup N]

E99's estimator and gates, unchanged (reduce_hl.runs_of_pass: board power over [t0+1 s, t0+3 s) corrected to the launch reading with the
leakage slope; reduce_mf.ec_fields and took_ms_window; the run and pass gates; the warm-up rule). Registered here, beyond E99's reducer:
the NoC, SRAM and minion rails read as reduce_hl reads the minion rail (sp.<rail>_w[0] over [t0+2 s, t0+4 s), never past the run, raw),
"off" = the board less the three rails, the DDR die rail (die_mv.ddr, mV, over the board's window), one line rate per level, and the
rules R1-R6. Primary arm: the passes with the board meter's dip samples removed by E82 A2's definition (dp/posthoc_dips.py, as E99).
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
sys.path.insert(0, os.path.join(HERE, "..", "dp"))
from reduce_hl import leak_slope, load_jsonl, runs_of_pass  # noqa: E402
from reduce_mf import ci, ec_fields, took_ms_window  # noqa: E402
from reduce_dp import classify  # noqa: E402

COLS = ("board", "noc", "sram", "minion", "off", "ddr_mv")
N = {16: 31, 32: 15, 64: 7, 128: 3, 256: 1}
WR = {16: "dm_a08", 32: "wl_32", 64: "wl_64", 128: "wl_128", 256: "wl_256"}
VR = {16: "dm_a44", 32: "vl_32", 64: "vl_64", 128: "vl_128", 256: "vl_256"}

CONTRASTS = {}
for _w in N:
    CONTRASTS["S%d" % _w] = ({WR[_w]: 1, "dm_l08": -1}, "W ladder: %d-bit blocks of 0x00/0xFF over lanes-constant (raw toggles; encoded only DMI)" % _w)
    CONTRASTS["V%d" % _w] = ({VR[_w]: 1, "dm_u4": -1}, "V ladder: %d-bit blocks of 0x0F/0xF0 over 0x0F (raw = encoded toggles)" % _w)
for _w in (32, 64, 128, 256):
    k = N[_w] / 31.0
    CONTRASTS["E%d" % _w] = ({VR[_w]: 1, "dm_u4": -1, WR[_w]: -1, "dm_l08": 1, "dm_a44": -k, "dm_a08": k},
                             "encoded wide-path residual at %d bits: V - S - (n/31)(V16 - S16), the pins' share removed" % _w)
CONTRASTS.update({
    "Sc1": ({"dp_c1": 1, "dm_l08": -1}, "E99's `half`: the 32 B halves 0xFF then 0x00, over lanes-constant"),
    "c256": ({"wl_256": 1, "wl_128": -1.0 / 3.0, "dm_l08": -2.0 / 3.0}, "S256 - S128/3: a 256-bit path beyond the narrower ones (within-line edges)"),
    "c256_cyc": ({"wl_256": 1, "wl_128": -0.5, "dm_l08": -0.5}, "S256 - S128/2: the same with each path's line-to-line edge counted"),
    "phase": ({"dp_c1": 1, "wl_256": -1}, "ones in the first 32 B against the second: where the register load's half sits"),
    "tie18": ({"dm_u8": 1, "dm_u1": -1}, "DRAM: 448 more ones, 64 pins high on both, no toggle (E99's tie18)"),
    "ones_u8": ({"dm_u8": 1, "dp_zeros": -1}, "DRAM: all 0xFF over zeros"),
    "l2_ones": ({"l2_u8": 1, "l2_u1": -1}, "L2: 448 more ones, no DRAM, no pins"),
    "l2_u8z": ({"l2_u8": 1, "l2_zeros": -1}, "L2: all 0xFF over L2 zeros"),
    "cal": ({"dp_zeros": 1, "l2_zeros": -1}, "DRAM zeros over L2 zeros: the DRAM path's own traffic, for the DDR die rail's scale"),
    "D": ({"dm_L8192": 1, "dm_L2": -1}, "E99's period step: 8,192 distinct lines over 2"),
    "bern": ({"dp_bern": 1, "dp_zeros": -1}, "E81's random bits over zeros"),
})


def value(row, spec):
    out = 0.0
    for it, c in spec.items():
        v = row.get(it)
        if v is None:
            return None
        out += c * v
    return out


def extra_of_pass(d):
    """{(pass, item, pos, attempt): {noc, sram, minion, ddr_mv}} with reduce_hl's windows: rails over [t0+2 s, t0+4 s) never past the run,
    the DDR die rail over the board's [t0+1 s, t0+3 s)."""
    tel = load_jsonl(os.path.join(d, "telemetry.jsonl"))
    t = np.array([s["t_ms"] for s in tel], float)
    A = {"noc": np.array([s["sp"]["noc_w"][0] for s in tel], float),
         "sram": np.array([s["sp"]["sram_w"][0] for s in tel], float),
         "minion": np.array([s["sp"]["minion_w"][0] for s in tel], float)}
    ddr = np.array([s.get("die_mv", {}).get("ddr", np.nan) for s in tel], float)
    first, last = {}, {}
    for r in load_jsonl(os.path.join(d, "runs.jsonl")):
        key = (r["block"], r["item"], r.get("pos", 0), r.get("attempt", 1))
        first[key] = min(first.get(key, 1e30), r["t_start_ms"])
        last[key] = max(last.get(key, 0), r["t_end_ms"])
    out = {}
    for key, t0 in first.items():
        lo = t0 + 1000
        w = (t >= lo) & (t < lo + 2000)
        wr = (t >= lo + 1000) & (t < min(lo + 3000, last[key]))
        if w.sum() < 5 or wr.sum() < 3:
            continue
        rec = {f: float(A[f][wr].mean()) for f in A}
        rec["ddr_mv"] = float(np.nanmean(ddr[w]))
        out[key] = rec
    return out


def cls_ddr(c, moves, still):
    if c["mean"] is None or c["lo"] is None:
        return "unresolved"
    if c["mean"] <= -moves and c["hi"] < 0:
        return "moves"
    if c["mean"] >= moves and c["lo"] > 0:
        return "rises"
    if c["lo"] >= -still and c["hi"] <= still:
        return "still"
    return "unresolved"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dirs", nargs="+")
    ap.add_argument("--gen", required=True)
    ap.add_argument("--pred", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--csv")
    ap.add_argument("--leak", default="auto")
    ap.add_argument("--warmup", type=int, default=None)
    a = ap.parse_args()
    pred = json.load(open(a.pred))
    D_ = pred["decision"]
    warmup = a.warmup if a.warmup is not None else D_["warmup_pass"]
    man = {it["name"]: it for it in json.load(open(os.path.join(a.gen, "manifest.json")))["items"]}

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
        r["k"], r["w"] = it.get("k"), it.get("w")
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
    per_pass = {}
    for p in healthy:
        cols = {c: {n: item_of(p, n, c) for n in names} for c in COLS}
        lr = {}
        for lvl in ("dram", "l2"):
            v = [r["ops_per_s"] for r in G if r["pass"] == p and r["level"] == lvl and r.get("ops_per_s")]
            lr[lvl] = float(np.mean(v)) if v else None
        per_pass[p] = {"items": cols, "lines_per_s": lr, "drift_W": drift.get(p),
                       "contrasts": {c: {cn: value(cols[c], s) for cn, (s, _) in CONTRASTS.items()} for c in COLS}}

    def summarize(passes):
        out = {"passes": passes, "lines_per_s": {}, "line_rate_by_item": {}}
        for lvl in ("dram", "l2"):
            v = [per_pass[p]["lines_per_s"][lvl] for p in passes if per_pass[p]["lines_per_s"][lvl]]
            out["lines_per_s"][lvl] = float(np.mean(v)) if v else None
        for n in names:
            v = [r["ops_per_s"] for r in G if r["pass"] in passes and r["item"] == n and r.get("ops_per_s")]
            out["line_rate_by_item"][n] = float(np.mean(v)) if v else None
        out["items_W"] = {n: ci([per_pass[p]["items"]["board"][n] for p in passes if per_pass[p]["items"]["board"][n] is not None])
                          for n in names}
        out["over_zeros"] = {}
        for c in COLS:
            out["over_zeros"][c] = {}
            for n in names:
                z = "l2_zeros" if man[n].get("level") == "l2" else "dp_zeros"
                out["over_zeros"][c][n] = ci([per_pass[p]["items"][c][n] - per_pass[p]["items"][c][z] for p in passes
                                              if per_pass[p]["items"][c].get(n) is not None and per_pass[p]["items"][c].get(z) is not None])
        out["contrasts"] = {c: {} for c in COLS}
        for c in COLS:
            for cn, (s, what) in CONTRASTS.items():
                x = ci([v for v in (per_pass[p]["contrasts"][c][cn] for p in passes) if v is not None])
                if c == "board":
                    x["what"], x["items"] = what, s
                out["contrasts"][c][cn] = x
        return out

    head = summarize(headline)
    every = summarize(healthy)
    C = head["contrasts"]
    B = C["board"]
    pm, ah = D_["present_min_W"], D_["absent_half_W"]
    enough = len(headline) >= D_["min_headline_passes"]
    cls = {cn: (classify(B[cn], pm, ah) if enough else "unresolved") for cn in B}
    m = lambda cn: B[cn]["mean"]
    iv = lambda cn: [B[cn]["lo"], B[cn]["hi"]]
    lr_d = head["lines_per_s"]["dram"]
    V = {}

    # R1, the session's tie to E99 (byte-identical images and commands)
    tie = {}
    for cn, ref in pred["prediction"]["ties"].items():
        tol = D_["tie_within_W"][cn]
        tie[cn] = {"E99_W": ref, "mean_W": m(cn), "within_W": tol,
                   "verdict": "UNRESOLVED" if (m(cn) is None or not enough) else ("PASS" if abs(m(cn) - ref) <= tol else "FAIL")}
    V["R1_tie"] = {"items": tie, "verdict": "UNRESOLVED" if any(x["verdict"] == "UNRESOLVED" for x in tie.values())
                   else ("PASS" if all(x["verdict"] == "PASS" for x in tie.values()) else "FAIL")}

    # R2, the raw path's width: the first W rung from 32 up that is present, with every rung below it (from 32) absent
    onset, why = None, ""
    if enough:
        for w in (32, 64, 128, 256):
            c_ = cls["S%d" % w]
            if c_ == "present":
                onset = w
                break
            if c_ != "absent":
                onset, why = "UNRESOLVED", "S%d is %s before any rung is present" % (w, c_)
                break
        if onset is None:
            onset = "NONE"
    else:
        onset = "UNRESOLVED"
    pr = pred["prediction"]["R2_onset_raw"]
    V["R2_raw_width"] = {"classes": {"S%d" % w: cls["S%d" % w] for w in N}, "means_W": {"S%d" % w: m("S%d" % w) for w in N},
                         "intervals_W": {"S%d" % w: iv("S%d" % w) for w in N}, "onset_bits": onset, "note": why,
                         "predicted_bits": pr,
                         "models_with_this_onset": [k for k, row in pred["contrasts"].items() if row["onset_raw"] == onset],
                         "verdict": "UNRESOLVED" if onset == "UNRESOLVED" else ("PASS" if onset == pr else "FAIL")}

    # R3, raw or encoded at 64 bits (and the other widths, reported)
    s64, e64 = cls["S64"], cls["E64"]
    if not enough:
        r3 = "UNRESOLVED"
    elif s64 == "present" and e64 == "absent":
        r3 = "RAW"
    elif e64 == "present" and s64 == "absent":
        r3 = "ENCODED"
    elif e64 == "present" and s64 == "present":
        r3 = "BOTH"
    elif e64 == "absent" and s64 == "absent":
        r3 = "NEITHER"
    else:
        r3 = "UNRESOLVED"
    V["R3_raw_or_encoded"] = {"S64": {"class": s64, "mean_W": m("S64"), "interval_W": iv("S64")},
                              "E64": {"class": e64, "mean_W": m("E64"), "interval_W": iv("E64")},
                              "others": {"E%d" % w: {"class": cls["E%d" % w], "mean_W": m("E%d" % w), "interval_W": iv("E%d" % w)}
                                         for w in (32, 128, 256)},
                              "reading": r3, "predicted": pred["prediction"]["R3_reading"],
                              "verdict": "UNRESOLVED" if r3 == "UNRESOLVED" else ("PASS" if r3 == pred["prediction"]["R3_reading"] else "FAIL")}

    # R4, the half-line bits: a raw 256-bit path beyond the narrower ones; not encoded; where the ones sit does not matter
    c4 = cls["c256"]
    r4 = "UNRESOLVED"
    if enough:
        if c4 == "present" and cls["E256"] != "present":
            r4 = "RAW256"
        elif c4 == "absent":
            r4 = "NO256"
        elif cls["E256"] == "present":
            r4 = "ENCODED256"
    V["R4_half_line"] = {"c256": {"class": c4, "mean_W": m("c256"), "interval_W": iv("c256"),
                                  "pJ_per_bit": (m("c256") / lr_d / 256 * 1e12) if (m("c256") is not None and lr_d) else None,
                                  "pJ_per_bit_if_line_edges_count": (m("c256_cyc") / lr_d / 512 * 1e12) if (m("c256_cyc") is not None and lr_d) else None},
                         "E256": {"class": cls["E256"], "mean_W": m("E256"), "interval_W": iv("E256")},
                         "phase": {"class": cls["phase"], "mean_W": m("phase"), "interval_W": iv("phase")},
                         "reading": r4, "verdict": "UNRESOLVED" if r4 == "UNRESOLVED" else ("PASS" if r4 == pred["prediction"]["R4_half"] else "FAIL")}

    # R5, the DDR die rail: which contrasts move the memory shires' logic, and a bound on the logic's share of those that do not
    dd = C["ddr_mv"]
    cal_off = C["off"]["cal"]["mean"]
    kd = [(-per_pass[p]["contrasts"]["ddr_mv"]["cal"] / per_pass[p]["contrasts"]["off"]["cal"])
          for p in headline if per_pass[p]["contrasts"]["off"]["cal"] and per_pass[p]["contrasts"]["ddr_mv"]["cal"] is not None]
    k_ddr = ci(kd)
    r5 = {}
    for cn, want in pred["prediction"]["R5_ddr"].items():
        cc = cls_ddr(dd[cn], D_["ddr_moves_mV"], D_["ddr_still_half_mV"]) if enough else "unresolved"
        bound = None
        if cc == "still" and k_ddr["mean"] and k_ddr["mean"] > 0:
            bound = max(abs(dd[cn]["lo"]), abs(dd[cn]["hi"])) / k_ddr["mean"]
        r5[cn] = {"mean_mV": dd[cn]["mean"], "interval_mV": [dd[cn]["lo"], dd[cn]["hi"]], "class": cc, "predicted": want,
                  "board_W": m(cn), "logic_share_at_most_W": bound,
                  "verdict": "UNRESOLVED" if cc == "unresolved" else ("PASS" if cc == want else "FAIL")}
    V["R5_ddr_die_rail"] = {"contrasts": r5, "k_ddr_mV_per_W_lower_bound": k_ddr, "cal_off_W": cal_off,
                            "verdict": "UNRESOLVED" if any(x["verdict"] == "UNRESOLVED" for x in r5.values())
                            else ("PASS" if all(x["verdict"] == "PASS" for x in r5.values()) else "FAIL")}

    # R6, the 1.3 pJ: a one's price per column at DRAM and at L2; the on-chip off-rail fraction; the regulators' share; the remainder
    rows = []
    for p in headline:
        cd, lrp = per_pass[p]["contrasts"], per_pass[p]["lines_per_s"]
        if not (lrp["dram"] and lrp["l2"]) or any(cd[c]["tie18"] is None or cd[c]["l2_ones"] is None for c in ("board", "noc", "sram", "minion", "off")):
            continue
        dr = {c: cd[c]["tie18"] / (448 * lrp["dram"]) * 1e12 for c in ("board", "noc", "sram", "minion", "off")}
        l2 = {c: cd[c]["l2_ones"] / (448 * lrp["l2"]) * 1e12 for c in ("board", "noc", "sram", "minion", "off")}
        f = l2["off"] / l2["board"] if l2["board"] else None
        rails = dr["noc"] + dr["sram"] + dr["minion"]
        reg = rails * f / (1 - f) if f is not None and f < 1 else None
        rows.append({"pass": p, "dram_pJ": dr, "l2_pJ": l2, "f": f, "regulator_pJ": reg,
                     "X_pJ": (dr["off"] - reg) if reg is not None else None})
    q = lambda k: ci([r[k] for r in rows if r.get(k) is not None])
    X = q("X_pJ")
    if not enough or X["mean"] is None:
        r6 = "UNRESOLVED"
    elif X["lo"] > 0:
        r6 = "PASS"
    elif X["hi"] < 0.30 and X["lo"] > -0.30:
        r6 = "FAIL"
    else:
        r6 = "UNRESOLVED"
    V["R6_one_off_rail"] = {"dram_pJ_per_one": {c: ci([r["dram_pJ"][c] for r in rows]) for c in ("board", "noc", "sram", "minion", "off")},
                            "l2_pJ_per_one": {c: ci([r["l2_pJ"][c] for r in rows]) for c in ("board", "noc", "sram", "minion", "off")},
                            "f_on_chip_off_fraction": q("f"), "regulator_share_pJ": q("regulator_pJ"), "remainder_X_pJ": X,
                            "per_pass": rows, "verdict": r6,
                            "reading": "a one pays off the metered rails beyond the regulators' share" if r6 == "PASS" else
                                       "the on-chip off-rail fraction accounts for it" if r6 == "FAIL" else "not resolved"}

    # where each ladder effect is paid: the three metered rails' sum, and off
    where = {}
    for cn in ("S32", "S64", "S128", "S256", "Sc1", "V32", "V64", "V128", "V256", "E64", "c256", "tie18", "D", "l2_ones"):
        rs = ci([sum(per_pass[p]["contrasts"][c][cn] for c in ("noc", "sram", "minion")) for p in headline
                 if all(per_pass[p]["contrasts"][c][cn] is not None for c in ("noc", "sram", "minion"))])
        on_none = (rs["lo"] is not None and rs["lo"] >= -D_["rails_on_none_half_W"] and rs["hi"] <= D_["rails_on_none_half_W"])
        where[cn] = {"board_W": m(cn), "rails_sum": rs, "off": C["off"][cn], "on_no_metered_rail": bool(on_none) if enough else None,
                     "noc": C["noc"][cn], "sram": C["sram"][cn], "minion": C["minion"][cn]}
    V["where"] = where

    # the triangular solve, reported: price per toggled bit at each width from the W and V ladders (within-line and line-edge counts)
    tri = {}
    for fam, pre in (("W", "S"), ("V", "V")):
        for cnt, nn in (("within", N), ("cyclic", {w: 512 // w for w in N})):
            A_ = {w: (m(pre + str(w)) / nn[w]) if m(pre + str(w)) is not None else None for w in N}
            pr_ = {}
            prev = 0.0
            for w in (16, 32, 64, 128, 256):
                if A_[w] is None or lr_d is None:
                    pr_[w] = None
                    continue
                pr_[w] = (A_[w] - prev) / w / lr_d * 1e12
                prev = A_[w]
            tri["%s_%s" % (fam, cnt)] = pr_
    V["prices_pJ_per_toggled_bit"] = tri

    # model scoring, reported: rms of every frozen model over the ladder contrasts
    keys = ["S32", "S64", "S128", "S256", "V32", "V64", "V128", "V256", "E64"]
    V["models_rms_W"] = {}
    for mod, row in pred["contrasts"].items():
        d_ = [m(k) - row[k] for k in keys if m(k) is not None]
        V["models_rms_W"][mod] = float(np.sqrt(np.mean(np.square(d_)))) if d_ else None

    res = {"exp": "E110", "card": card, "dirs": a.dirs, "warmup_pass": warmup, "passes_all": all_passes, "passes_healthy": healthy,
           "passes_headline": headline, "passes_set_aside": set_aside, "anchor_drift_W": drift,
           "gates": {"runs": len(R), "kept": len(G), "clocks_mhz": clocks, "leak_W_per_C": k_leak, "leak_runs": nk,
                     "failures": dict(sorted(((f, sum(1 for r in R if f in r["fails"])) for f in {f for r in R for f in r["fails"]}))) or {},
                     "took_ms_med_max": max([r.get("took_ms_med") or 0 for r in R])},
           "headline": head, "with_warmup": every, "classes": cls, "verdicts": V, "per_pass": per_pass}
    json.dump(res, open(a.out, "w"), indent=1, default=float)

    if a.csv:
        cols = ["card", "pass", "item", "level", "arm", "pos", "attempt", "start_c", "t_win", "on_protocol", "p_raw", "p80",
                "noc", "sram", "minion", "off", "ddr_mv", "mv", "ops_per_s", "took_ms_med", "fails"]
        with open(a.csv, "w", newline="") as fh:
            wcsv = csv.writer(fh)
            wcsv.writerow(cols)
            for r in sorted(R, key=lambda r: (r["pass"], r["pos"])):
                wcsv.writerow([("|".join(r[c]) if c == "fails" else r.get(c)) for c in cols])

    print("E110 %s: %d runs, %d kept, healthy %s, headline %s, set aside %s, leak %.4f W/C (%d runs), lines/s %s"
          % (card, len(R), len(G), healthy, headline, set_aside, k_leak, nk, head["lines_per_s"]))
    for cn, c in B.items():
        if c["mean"] is not None:
            print("  %-9s %+.3f W [%s, %s] n=%d %-10s | noc %+.3f sram %+.3f minion %+.3f off %+.3f | ddr %+.2f mV" % (
                cn, c["mean"], "%+.3f" % c["lo"] if c["lo"] is not None else "n/a", "%+.3f" % c["hi"] if c["hi"] is not None else "n/a",
                c["n"], cls[cn], C["noc"][cn]["mean"] or 0, C["sram"][cn]["mean"] or 0, C["minion"][cn]["mean"] or 0,
                C["off"][cn]["mean"] or 0, C["ddr_mv"][cn]["mean"] if C["ddr_mv"][cn]["mean"] is not None else float("nan")))
    for k_ in ("R1_tie", "R2_raw_width", "R3_raw_or_encoded", "R4_half_line", "R5_ddr_die_rail", "R6_one_off_rail"):
        v = V[k_]
        print("  %-20s %s %s" % (k_, v["verdict"], v.get("reading", v.get("onset_bits", ""))))
    print("  R6: X %s pJ, f %s, regulator %s pJ" % (json.dumps({k: round(x, 3) if isinstance(x, float) else x for k, x in X.items()}),
                                                    json.dumps({k: round(x, 3) if isinstance(x, float) else x for k, x in q("f").items()}),
                                                    json.dumps({k: round(x, 3) if isinstance(x, float) else x for k, x in q("regulator_pJ").items()})))
    print("  models rms:", json.dumps({k: round(x, 3) for k, x in V["models_rms_W"].items() if x is not None}))
    print("  prices W_within:", json.dumps({k: (round(x, 2) if x is not None else None) for k, x in tri["W_within"].items()}))
    print("  prices V_within:", json.dumps({k: (round(x, 2) if x is not None else None) for k, x in tri["V_within"].items()}))


if __name__ == "__main__":
    main()
