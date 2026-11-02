#!/usr/bin/env python3
"""E132 reduction: the decision rules frozen in e132/predictions.json and e132/README.md, written and tested BEFORE the first measured pass
(selftest_e132.py: E110's committed passes relabelled, a pipeline test that means nothing as an E132 result).

    python3 tools/claims-v3/e132/reduce_e132.py <pass dir> [...] --gen <make_e132.py dir> --pred tools/claims-v3/e132/predictions.json
        --out e132.json [--csv runs.csv] [--leak auto|<W per C>] [--warmup N]

E110's estimator, gates, windows and pass rules, unchanged (its reduce_e110.extra_of_pass reads the NoC, SRAM and minion rails over
[t0+2 s, t0+4 s) never past the run, raw, and the DDR die rail over the board's [t0+1 s, t0+3 s); reduce_hl.runs_of_pass gives the board
over [t0+1 s, t0+3 s) corrected to the launch reading with the leakage slope; reduce_mf's ec_fields and took_ms_window; the run gates;
a pass set aside at an anchor drift above 0.3 W or a third of its memory runs failing a gate; the warm-up pass out of the headline).
New here: E132's contrasts, the hart-stream correction of the address-bit rungs, per-rail thresholds, and the rules R1-R6.
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
sys.path.insert(0, os.path.join(HERE, "..", "e110"))
from reduce_hl import leak_slope, load_jsonl, runs_of_pass  # noqa: E402
from reduce_mf import ci, ec_fields, took_ms_window  # noqa: E402
from reduce_e110 import extra_of_pass, value  # noqa: E402  (E110's rail and die-rail windows, unchanged)

COLS = ("board", "noc", "sram", "minion", "off", "ddr_mv")
RAILS = ("noc", "sram", "minion")
AB = ["dm_u4"] + ["ab_%d" % b for b in range(8)]


def build_contrasts(man):
    """Every contrast, as {item: coefficient}. The rungs' hart-stream correction uses each image's own stream count (manifest "k",
    make_e132.stream_k): R(x, y) = (x - y) - (k_x - k_y) / (k_ab_x70 - k_ab_7) * (ab_x70 - ab_7)."""
    k = {n: float(man[n]["k"]) for n in AB + ["ab_x70", "ab_rnd"]}
    dk = k["ab_x70"] - k["ab_7"]
    C = {}

    def add(name, spec, what):
        C[name] = (spec, what)

    add("S64", {"wl_64": 1, "dm_l08": -1}, "E110's S64: 64-bit blocks of 0x00/0xFF over lanes-constant")
    add("S128", {"wl_128": 1, "dm_l08": -1}, "E110's S128")
    add("V16", {"dm_a44": 1, "dm_u4": -1}, "E110's V16: 496 pin toggles (beats 0x0F0F/0xF0F0 over 0x0F)")
    add("V64", {"vl_64": 1, "dm_u4": -1}, "E110's V64")
    add("V128", {"vl_128": 1, "dm_u4": -1}, "E110's V128")
    add("U4z", {"dm_u4": 1, "dp_zeros": -1}, "every byte 0x0F over zeros")
    add("H", {"ab_x70": 1, "ab_7": -1}, "the hart stream: %.0f more bits changed a line in a hart's own stream, every path's view equal" % dk)

    def rung(name, x, y, what):
        s = {x: 1.0, y: -1.0}
        f = (k[x] - k[y]) / dk
        s["ab_x70"] = s.get("ab_x70", 0.0) - f
        s["ab_7"] = s.get("ab_7", 0.0) + f
        s = {i: c for i, c in s.items() if abs(c) > 1e-15}
        add(name, s, what + " (hart stream removed: %+.4f x H)" % (-f))
        add("D" + name[1:], {x: 1, y: -1}, what + " (raw, no correction)")

    rung("R_0", "ab_0", "dm_u4", "1-way: every path that carries all lines, over constant lines")
    for b in range(1, 8):
        rung("R_%d" % b, "ab_%d" % b, "ab_%d" % (b - 1), "the %d-way path's changes, every finer path's count held" % 2 ** b)
    rung("R_hi", "ab_rnd", "ab_7", "256 ways and wider: the not-periodic image over ab_7")
    rung("R_wide", "ab_rnd", "ab_4", "32 ways and wider (E99's L8192 - L32)")
    rung("R_all", "ab_rnd", "dm_u4", "the whole ladder: the not-periodic two-value image over constant lines")
    add("Hp", {"c3_64": 0.5, "wl_64": -0.5, "c3_128": 0.5, "wl_128": -0.5}, "192 pins driven high at equal toggles (C3 over W, both rungs)")
    add("RH64", {"c3_64": 1, "wl_64": -1}, "192 pins high at the 64-bit rung")
    add("RH128", {"c3_128": 1, "wl_128": -1}, "192 pins high at the 128-bit rung")
    add("P56", {"eh_64": 1, "el_64": -1}, "encoded 64-bit toggles +392 at raw 56 (pins +98, high +32)")
    add("P448", {"vl_64": 1, "c3_64": -1}, "encoded 64-bit toggles +392 at raw 448 (pins +98, high +32)")
    add("P192", {"vl_128": 1, "c3_128": -1}, "encoded 64-bit toggles +168 at raw 192 (pins +42, high +32)")
    for nm, pair, dpin in (("E56", ("eh_64", "el_64"), 98), ("E448", ("vl_64", "c3_64"), 98), ("E192", ("vl_128", "c3_128"), 42)):
        s = {pair[0]: 1.0, pair[1]: -1.0, "dm_a44": -dpin / 496.0, "dm_u4": dpin / 496.0}
        for it, c in {"c3_64": 0.5, "wl_64": -0.5, "c3_128": 0.5, "wl_128": -0.5}.items():
            s[it] = s.get(it, 0.0) - (32.0 / 192.0) * c
        add(nm, s, "the encoded wide-path residual: %s - %s - (%d/496) V16 - (32/192) Hp" % (pair[0], pair[1], dpin))
    for n in ("eh_64", "el_64", "wl_64", "vl_64", "c3_64", "wl_128", "vl_128", "c3_128", "dm_l08", "dm_u4"):
        add(n + "z", {n: 1, "dp_zeros": -1}, n + " over zeros")
    add("RE64", {"eh_64": 1, "el_64": -1}, "the DDR die rail on encoded toggles at raw 56 (= P56)")
    add("RE128", {"vl_128": 1, "c3_128": -1}, "the DDR die rail on encoded toggles at raw 192 (= P192)")
    return C, k


def cls_t(c, t):
    if c["mean"] is None or c["lo"] is None:
        return "unresolved"
    if c["mean"] >= t and c["lo"] > 0:
        return "present"
    if c["mean"] <= -t and c["hi"] < 0:
        return "negative"
    if c["lo"] >= -t and c["hi"] <= t:
        return "absent"
    return "unresolved"


def cls_nonzero(c, half):
    if c["mean"] is None or c["lo"] is None:
        return "unresolved"
    if c["lo"] > 0:
        return "present"
    if c["hi"] < 0:
        return "negative"
    if c["lo"] >= -half and c["hi"] <= half:
        return "absent"
    return "unresolved"


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
    P_ = pred["prediction"]
    warmup = a.warmup if a.warmup is not None else D_["warmup_pass"]
    man = {it["name"]: it for it in json.load(open(os.path.join(a.gen, "manifest.json")))["items"]}
    CONTRASTS, KS = build_contrasts(man)

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
        out["over_zeros"] = {c: {n: ci([per_pass[p]["items"][c][n] - per_pass[p]["items"][c]["dp_zeros"] for p in passes
                                        if per_pass[p]["items"][c].get(n) is not None and per_pass[p]["items"][c].get("dp_zeros") is not None])
                                 for n in names} for c in COLS}
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
    enough = len(headline) >= D_["min_headline_passes"]
    T = D_["rail_threshold_W"]
    lr = head["lines_per_s"]
    m = lambda cn, col="board": C[col][cn]["mean"]
    iv = lambda cn, col="board": [C[col][cn]["lo"], C[col][cn]["hi"]]
    ddr = lambda cn: cls_ddr(C["ddr_mv"][cn], D_["ddr_moves_mV"], D_["ddr_still_half_mV"]) if enough else "unresolved"
    V = {}

    # R1, the session's tie to E110 (byte-identical images and commands)
    tie = {}
    for cn, ref in P_["ties_W"].items():
        tol = D_["tie_within_W"]
        tie[cn] = {"E110_W": ref, "mean_W": m(cn), "interval_W": iv(cn), "within_W": tol,
                   "verdict": "UNRESOLVED" if (m(cn) is None or not enough) else ("PASS" if abs(m(cn) - ref) <= tol else "FAIL")}
    V["R1_tie"] = {"items": tie, "verdict": "UNRESOLVED" if any(x["verdict"] == "UNRESOLVED" for x in tie.values())
                   else ("PASS" if all(x["verdict"] == "PASS" for x in tie.values()) else "FAIL")}

    # R2, the channel rung: does a channel's path pay for changes between the lines it carries?
    c4 = cls_t(B["R_4"], D_["board_present_W"]) if enough else "unresolved"
    if c4 == "present":
        r2 = "EDGES"
    elif c4 == "absent":
        r2 = "NO-EDGES"
    else:
        r2 = "UNRESOLVED"
    rs4 = ci([sum(per_pass[p]["contrasts"][c]["R_4"] for c in RAILS) for p in headline
              if all(per_pass[p]["contrasts"][c]["R_4"] is not None for c in RAILS)])
    V["R2_channel_rung"] = {"R_4": {"class": c4, "mean_W": m("R_4"), "interval_W": iv("R_4"),
                                    "raw_D_4_W": m("D_4"), "rails_sum": rs4, "off": C["off"]["R_4"], "ddr_mV": C["ddr_mv"]["R_4"],
                                    "pJ_per_bit_on_a_256_bit_path": (m("R_4") / (128 * lr) * 1e12) if (m("R_4") is not None and lr) else None},
                            "predicted": P_["R2"], "reading": r2,
                            "verdict": "UNRESOLVED" if r2 == "UNRESOLVED" else ("PASS" if r2 == P_["R2"]["reading"] else "FAIL")}

    # R3, the encoded part at the DDR die rail
    cz = {n: ddr(n) for n in ("eh_64z", "el_64z", "wl_64z", "vl_64z", "c3_64z", "wl_128z", "vl_128z", "c3_128z", "dm_l08z", "dm_u4z",
                              "RE64", "RE128", "RH64", "RH128")}
    if not enough:
        r3 = "UNRESOLVED"
    elif cz["wl_64z"] != "moves":
        r3 = "UNRESOLVED"          # the raw positive control did not move the rail: the instrument says nothing here
    elif cz["el_64z"] in ("moves", "rises"):
        r3 = "OTHER"
    elif cz["RE64"] == "moves" and cz["el_64z"] == "still":
        r3 = "ENCODED"
    elif cz["eh_64z"] == "still" and cz["el_64z"] == "still" and cz["RE64"] == "still":
        r3 = "RAW"
    else:
        r3 = "UNRESOLVED"
    V["R3_encoded_ddr"] = {"classes": cz, "mV": {n: {"mean": C["ddr_mv"][n]["mean"], "interval": iv(n, "ddr_mv")} for n in cz},
                           "predicted": P_["R3"], "reading": r3,
                           "verdict": "UNRESOLVED" if r3 == "UNRESOLVED" else ("PASS" if r3 == P_["R3"]["reading"] else "FAIL")}

    # R4, the encoded part on the board, beyond the pins and the pins held high
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
    pr = lambda cn, n: (m(cn) / (n * lr) * 1e12) if (m(cn) is not None and lr) else None
    V["R4_encoded_board"] = {"E56": {"class": c56, "mean_W": m("E56"), "interval_W": iv("E56"), "pJ_per_encoded_toggle": pr("E56", 392)},
                             "E448": {"class": c448, "mean_W": m("E448"), "interval_W": iv("E448"), "pJ_per_encoded_toggle": pr("E448", 392)},
                             "E192": {"class": cls_nonzero(B["E192"], half) if enough else "unresolved", "mean_W": m("E192"),
                                      "interval_W": iv("E192"), "pJ_per_encoded_64bit_toggle": pr("E192", 168)},
                             "pairs_W": {cn: {"mean": m(cn), "interval": iv(cn)} for cn in ("P56", "P448", "P192")},
                             "predicted": P_["R4"], "reading": r4,
                             "verdict": "UNRESOLVED" if r4 == "UNRESOLVED" else ("PASS" if r4 == P_["R4"]["reading"] else "FAIL")}

    # R5, which interleave sets each rail's steps: the hart-corrected rungs on every rail, against E99's steps mapped rung by rung
    rungs = ["R_0"] + ["R_%d" % b for b in range(1, 8)] + ["R_hi", "R_wide", "R_all", "H"]
    r5 = {}
    for col in ("board", "noc", "sram", "minion", "off"):
        t = T[col]
        got = {rn: {"class": cls_t(C[col][rn], t) if enough else "unresolved", "mean_W": m(rn, col), "interval_W": iv(rn, col),
                    "raw_mean_W": m("D" + rn[1:], col) if rn != "H" else None} for rn in rungs}
        frozen = P_["R5"].get(col, {})
        cmp_ = {}
        nres, ncon = 0, 0
        for rn, fz in frozen.items():
            g = got[rn]["class"]
            both = g != "unresolved" and fz["class"] != "unresolved"
            con = both and g != fz["class"]
            nres += 1 if both else 0
            ncon += 1 if con else 0
            cmp_[rn] = {"E99": fz["class"], "E132": g, "contradiction": con}
        verdict = "UNRESOLVED" if not enough or nres == 0 else ("FAIL" if ncon else "PASS")
        biggest = max(((got[rn]["mean_W"] or -1e9), rn) for rn in rungs[:9])[1] if enough else None
        r5[col] = {"threshold_W": t, "rungs": got, "against_E99": cmp_, "largest_rung": biggest, "verdict": verdict}
    vs = [x["verdict"] for x in r5.values()]
    V["R5_rail_steps"] = {"rails": r5, "verdict": "FAIL" if "FAIL" in vs else ("PASS" if "PASS" in vs else "UNRESOLVED")}

    # R6, the pins held high on the DDR die rail, and their board price
    h64, h128 = cz["RH64"], cz["RH128"]
    if not enough:
        r6 = "UNRESOLVED"
    elif h64 == "still" and h128 == "still":
        r6 = "PASS"
    elif h64 in ("moves", "rises") or h128 in ("moves", "rises"):
        r6 = "FAIL"
    else:
        r6 = "UNRESOLVED"
    V["R6_high_pins_ddr"] = {"RH64": h64, "RH128": h128, "Hp_W": {"mean": m("Hp"), "interval": iv("Hp")},
                             "pJ_per_high_pin_beat_line": pr("Hp", 192), "predicted": P_["R6"], "verdict": r6}

    # where each effect is paid: the three metered rails' sum, and off
    where = {}
    for cn in rungs + ["Hp", "P56", "P448", "P192", "E56", "E448", "E192", "V16", "S64", "V64"]:
        rs = ci([sum(per_pass[p]["contrasts"][c][cn] for c in RAILS) for p in headline
                 if all(per_pass[p]["contrasts"][c][cn] is not None for c in RAILS)])
        on_none = (rs["lo"] is not None and rs["lo"] >= -D_["rails_on_none_half_W"] and rs["hi"] <= D_["rails_on_none_half_W"])
        where[cn] = {"board_W": m(cn), "rails_sum": rs, "off": C["off"][cn], "on_no_metered_rail": bool(on_none) if enough else None,
                     "noc": C["noc"][cn], "sram": C["sram"][cn], "minion": C["minion"][cn], "ddr_mV": C["ddr_mv"][cn]}
    V["where"] = where

    res = {"exp": "E132", "card": card, "dirs": a.dirs, "warmup_pass": warmup, "passes_all": all_passes, "passes_healthy": healthy,
           "passes_headline": headline, "passes_set_aside": set_aside, "anchor_drift_W": drift, "stream_k": KS,
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

    print("E132 %s: %d runs, %d kept, healthy %s, headline %s, set aside %s, leak %.4f W/C (%d runs), lines/s %s"
          % (card, len(R), len(G), healthy, headline, set_aside, k_leak, nk, lr))
    for cn, c in B.items():
        if c["mean"] is not None and not cn.startswith("D_"):
            print("  %-7s %+.3f W [%s, %s] n=%d | noc %+.3f sram %+.3f minion %+.3f off %+.3f | ddr %+.2f mV" % (
                cn, c["mean"], "%+.3f" % c["lo"] if c["lo"] is not None else "n/a", "%+.3f" % c["hi"] if c["hi"] is not None else "n/a",
                c["n"], C["noc"][cn]["mean"] or 0, C["sram"][cn]["mean"] or 0, C["minion"][cn]["mean"] or 0,
                C["off"][cn]["mean"] or 0, C["ddr_mv"][cn]["mean"] if C["ddr_mv"][cn]["mean"] is not None else float("nan")))
    for k_ in ("R1_tie", "R2_channel_rung", "R3_encoded_ddr", "R4_encoded_board", "R5_rail_steps", "R6_high_pins_ddr"):
        v = V[k_]
        print("  %-18s %s %s" % (k_, v["verdict"], v.get("reading", "")))
    for col, x in r5.items():
        print("  R5 %-6s %-10s largest %s | %s" % (col, x["verdict"], x["largest_rung"],
                                                  " ".join("%s:%s" % (rn, g["class"][:4]) for rn, g in x["rungs"].items())))


if __name__ == "__main__":
    main()
