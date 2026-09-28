#!/usr/bin/env python3
"""Build heat.json, the data of the heat-placement page (docs/reports/2026-09-28-et-soc1-heat-placement.html).

    python3 docs/reports/data/2026-09-28-heat-placement/build_heat_data.py [--val PATH] [--out PATH] [--check]

Every number on the page comes from this file's output, and every number here from the committed data:

  reductions/dev-r3.json   development (aifoundry3, R1-R3): `reduce.py --dev` on raw/aifoundry3 (byte for byte)
  reductions/reg.json      the registration (P3): `reduce.py --p3 --cal-card1 raw/aifoundry1-c1` (byte for byte)
  tools/claims-v3/hp/prereg/prereg.json, PREREG.md, PREREG.sha256   the frozen predictions and their hash
  tools/claims-v3/hp/placements.json   the placements and the die grid; tools/claims-v3/hp/README.md the departures
  raw/<card>/hp/p*/        block times, probes, V0 chains (hplib.v0_series) and the heating traces
                           (reduce.load_blocks: the reducer's own observables, t0 and t66)
  raw/aifoundry2/hp/a2/    aifoundry2's same-day attempts (A2)
  docs/reports/data/2026-09-28-dvfs2-aifoundry2/dv2.json   the DVFS page's development answer to Q1 (DV2, E51), with
                           its reductions/dv2-dev.json (G1-T's outcome) and tools/claims-v3/dv2/reduce_dv2.py (the
                           G1-T count rule)
  val.json (optional)      the verdicts: `reduce.py --val` on card 1's validation blocks (README, "The verdicts").
                           Without it the page says "pending". With it, card 1's per-block values and traces come
                           from raw/aifoundry1-c1 through the reducer's own functions when those blocks are there,
                           with val_blocks.summary (the times, the runs the 150 s cap cut off, the sessions from the
                           validation queue logs in logs/): what the page's summary and section 8 rest on.

--check rebuilds in memory and exits 1 if heat.json differs (nothing is written). Deterministic: no clock is read.
"""
import argparse
import datetime
import glob
import json
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
HP = os.path.join(ROOT, "tools", "claims-v3", "hp")
sys.path.insert(0, HP)
import hplib as H  # noqa: E402
import reduce as R  # noqa: E402

RAW = os.path.join(HERE, "raw")
PDT = datetime.timezone(datetime.timedelta(hours=-7))
CARDS = ["aifoundry3", "aifoundry1-c1"]          # development card first, then the validation card


def rel(p):
    return os.path.relpath(p, ROOT)


def load(p, default=None):
    try:
        with open(p) as f:
            return json.load(f)
    except (OSError, ValueError):
        return default


def pdt(ms):
    return None if ms is None else datetime.datetime.fromtimestamp(ms / 1000.0, PDT).strftime("%Y-%m-%d %H:%M:%S")


def r3(x, n=3):
    return None if x is None else round(float(x), n)


def ci(c):
    return None if not c else {k: r3(c.get(k), 5) for k in ("mean", "lo", "hi", "n", "sd", "half") if k in c}


# ---------------------------------------------------------------------------------------------- the placements
def placements():
    P = load(os.path.join(HP, "placements.json"))
    runs = P["runs"]
    status = {  # which block type used each placement, and what became of it (DESIGN2 §4.3; README departure 36)
        "INT16@32": ("L16, S", "registered"), "PER16@32": ("L16, S", "registered"), "UNI32@16": ("L16, S, L8", "registered"),
        "B4NE": ("S (MAP)", "development"), "B4SW": ("S (MAP)", "development"),
        "INT16@16": ("L8", "dropped"), "PER16@16": ("L8", "dropped"), "MEM8": ("L8", "dropped"),
        "EDGE8": ("L8", "dropped"), "CEN8": ("L8", "dropped"),
        "W8b": ("G8", "dropped"), "E8b": ("G8", "dropped"), "N8b": ("G8", "dropped"), "S8b": ("G8", "dropped"),
        "ALL24": ("every block (burn-in, preheat, V0)", "calibration"),
    }
    out = {}
    for name, (types, st) in status.items():
        r = runs[name]
        out[name] = {"group": r["group"], "mask": r["mask"], "per_shire": r["per_shire"], "minions": r["minions"],
                     "shires": r["shires"], "centroid_rc": r["centroid_rc"], "by_io": r["by_io"], "by_ms": r["by_ms"],
                     "mem_side": r["mem_side"], "ns_edge": r["ns_edge"], "types": types, "status": st}
    return {"grid": P["grid_rows_r0_r5_cols_c1_c6"], "runs": out, "identities": P["identities"], "source": P["source"]}


# ---------------------------------------------------------------------------------------------- what ran, when
def timeline():
    rows = []
    for card in ("aifoundry3", "aifoundry1-c1"):
        for bj in sorted(glob.glob(os.path.join(RAW, card, "hp", "p*", "block.json")),
                         key=lambda p: (load(p) or {}).get("t0_ms") or 0):
            d = os.path.dirname(bj)
            b = load(bj) or {}
            info = (load(os.path.join(d, "plan.json"), {}) or {}).get("info") or {}
            params = (load(os.path.join(d, "plan.json"), {}) or {}).get("params") or {}
            runs = H.load_jsonl(os.path.join(d, "runs.jsonl"))
            edges = sorted({r.get("edge") for r in runs if r.get("edge") is not None})
            try:
                rnd, typ, _ = H.decode_pass(b.get("pass"))       # pass = R x 1000 + T x 100 + k (README)
            except (TypeError, ValueError):
                rnd, typ = None, None
            rows.append({"card": card, "pass": b.get("pass"), "dir": os.path.basename(d),
                         "round": info.get("round") or rnd, "type": info.get("type") or typ,
                         "skipped": bool(info.get("skip")) or str(b.get("note") or "").startswith(("skipped", "not applicable")),
                         "t0": pdt(b.get("t0_ms")), "t1": pdt(b.get("t1_ms")),
                         "minutes": r3((b["t1_ms"] - b["t0_ms"]) / 60000.0, 1) if b.get("t1_ms") else None,
                         "status": b.get("status"), "note": b.get("note"), "edges": edges,
                         "die_c_start": b.get("die_c_start"), "die_c_end": b.get("die_c_end"),
                         "runs": len(runs), "params_types": params.get("types")})
    for a in sorted(glob.glob(os.path.join(RAW, "aifoundry2", "hp", "a2", "p*", "a2.json"))):
        d = os.path.dirname(a)
        b = load(os.path.join(d, "block.json")) or {}
        x = load(a) or {}
        rows.append({"card": "aifoundry2", "pass": "a2/" + os.path.basename(d), "dir": "a2/" + os.path.basename(d),
                     "round": "a2", "type": "A2", "t0": pdt(b.get("t0_ms")), "t1": pdt(b.get("t1_ms")),
                     "minutes": r3((b["t1_ms"] - b["t0_ms"]) / 60000.0, 1) if b.get("t1_ms") else None,
                     "status": b.get("status"), "note": x.get("note") or b.get("note"), "edges": [],
                     "die_c_start": x.get("rest_c"), "die_c_end": None, "runs": 0, "params_types": None, "skipped": False})
    return rows


# ---------------------------------------------------------------------------------------------- Q1
def q1():
    probes = {}
    for card in ("aifoundry3", "aifoundry1-c1"):
        p = load(os.path.join(RAW, card, "hp", "p801", "probe.json")) or {}
        probes[card] = {k: p.get(k) for k in ("rest_c", "class", "silent_reason", "level", "prediction", "prediction_met")}
    a2 = []
    for f in sorted(glob.glob(os.path.join(RAW, "aifoundry2", "hp", "a2", "p*", "a2.json"))):
        x = load(f) or {}
        pj = load(os.path.join(os.path.dirname(f), "probe", "probe.json")) or {}
        a2.append({"attempt": x.get("attempt"), "rest_c": x.get("rest_c"), "branch": x.get("branch"),
                   "time": pdt(x.get("reading_t_ms") or (load(os.path.join(os.path.dirname(f), "block.json")) or {}).get("t0_ms")),
                   "probe_class": x.get("probe_class") or pj.get("class"), "note": x.get("note")})
    DV = os.path.join(ROOT, "docs", "reports", "data", "2026-09-28-dvfs2-aifoundry2")
    dv = load(os.path.join(DV, "dv2.json"))
    c = dv["cards"]["aifoundry2"]
    q = c["q1"]
    sep = q["separating"]
    fit = [s for s in sep if s["fits_mean"]]
    g = c["q2"]
    fin = [b for b in g["blocks"] if b.get("final_candidate") and b.get("L") is not None]
    # DV2's frozen count rule for G1-T (tools/claims-v3/dv2/reduce_dv2.py g1t: PASS needs >= N separating runs over
    # >= B blocks) and its development outcome (DV2/reductions/dv2-dev.json, G1/G1-T)
    src = open(os.path.join(ROOT, "tools", "claims-v3", "dv2", "reduce_dv2.py")).read()
    m = re.search(r"elif n >= (\d+) and len\(blocks\) >= (\d+)", src)
    g1t = ((load(os.path.join(DV, "reductions", "dv2-dev.json")) or {}).get("G1") or {}).get("G1-T") or {}
    return {
        "firmware": {"sensors": 34, "threshold_c": c["threshold_c"][0] if isinstance(c["threshold_c"], list) else c["threshold_c"],
                     "rule": "floor(sum of floor(T_i) / n) > threshold, n = the minion-shire sensors that return a sample (34 when all do)",
                     "source": "BL2 0.20.0 (release 1.3.1), pvt_get_minion_avg_temperature(); the DVFS page §1",
                     "commit": "ffca4cbb4", "mean_at": "driver/pvt_controller.c:1279–1306",
                     "threshold_at": "include/thermal_pwr_mgmt.h:46"},
        "dv2": {"runs": q["T_runs"], "hold_runs": q["g1h"]["holds"], "max_over_thr": q["g1h"]["max_over_thr"],
                "separating": len(sep), "blocks": len(q["blocks"]), "fit_mean": len(fit),
                "fit_max": sum(1 for s in sep if s["fits_max"]),
                "down_minus_mean": [min(s["down_minus_mean"] for s in fit), max(s["down_minus_mean"] for s in fit)] if fit else None,
                "down_minus_high": [min(s["down_minus_high"] for s in sep), max(s["down_minus_high"] for s in sep)],
                "down_minus_high_fit": [min(s["down_minus_high"] for s in fit), max(s["down_minus_high"] for s in fit)] if fit else None,
                "neither": [{"name": s["name"], "block": s["block"], "down_minus_mean": s["down_minus_mean"],
                             "down_minus_high": s["down_minus_high"]} for s in sep if not s["fits_mean"] and not s["fits_max"]],
                "g1t_min": {"runs": int(m.group(1)), "blocks": int(m.group(2))} if m else None,
                "g1t_outcome": g1t.get("rule_outcome_if_registered"),
                "window_s": q["window_s"], "idle": q["idle_separating"][:1],
                "q2": {"blocks": [{"block": b["block"], "minions": b["minions"], "t800_int": b["t800_int"],
                                   "t800_per": b["t800_per"], "censored_per": b["censored_per"], "L": b["L"]} for b in fin],
                       "ratio": g["ratio"], "L_mean": g["L_mean"], "L_pred": g["L_pred"]},
                "prereg_val_sha256": dv["prereg"]["sha256"], "source": "docs/reports/data/2026-09-28-dvfs2-aifoundry2/dv2.json"},
        "probes": probes, "a2": a2,
    }


# ---------------------------------------------------------------------------------------------- traces
def traces(card, rounds, types=("L16", "S")):
    """Per block: the edge and, per measured run, the whole-degree mean the governor compares (temp_c.minshire[0]) at
    each change, in seconds from the run's t0 (the reducer's own t0 and t66: hplib.run_observables)."""
    d = os.path.join(RAW, card)
    if not os.path.isdir(os.path.join(d, "hp")):
        return {}
    out = {}
    for b in R.load_blocks(d, card, rounds=rounds):
        if b["type"] not in types:
            continue
        kept = R.kept_runs(b)
        runs = []
        for slot, x in sorted(kept.items()):
            o, rec = x["obs"], x["rec"]
            if rec.get("role") != "meas" or not o.get("t0_ms"):
                continue
            C = o.get("C") or (150.0 if b["type"] != "S" else 7.0)
            t0 = o["t0_ms"]
            stop = min(t0 + 1000 * ((o["t66_s"] if o.get("t66_s") is not None else C) + 4), o.get("t_end_ms") or 1e99)
            pts, last = [], None
            sam = [(s["t_ms"], s["temp_c"]["minshire"][0]) for s in x["tel"]
                   if s.get("t_ms") and (s.get("temp_c") or {}).get("minshire") and t0 - 3000 <= s["t_ms"] <= stop]
            for k, (t, m) in enumerate(sam):
                if m != last or k == len(sam) - 1:
                    pts.append([round((t - t0) / 1000.0, 2), m]); last = m
            runs.append({"name": rec["name"], "t66": r3(o.get("t66_s")), "censored": bool(o.get("censored")),
                         "C": C, "sw_W": r3(o.get("sw_W"), 2), "tau_c": r3(o.get("tau_c_s"), 2),
                         "W_idle": r3(o.get("W_idle"), 2), "pts": pts})
        edge = R.params_edge(b)
        out[str(b["pass"])] = {"pass": b["pass"], "round": b["round"], "type": b["type"], "edge": edge,
                               "void": b["void"], "runs": runs}
    return out


# ---------------------------------------------------------------------------------------------- development
def development():
    dv = load(os.path.join(HERE, "reductions", "dev-r3.json"))
    items = dv["dev"]["items"]
    keep = ("PLACE-t", "PLACE-tS", "PLACE-kappa", "PLACE-kappa-S", "SPREAD", "CONC", "MAP", "MEM", "EDGE",
            "PLACE8-t", "GRAD-EW", "GRAD-NS", "LIN", "CONC-L", "INTRA-TILE")
    it = {}
    for k in keep:
        v = items.get(k)
        if v is None:
            continue
        e = {"type": v.get("type"), "pair": v.get("pair"), "stat": v.get("stat"), "band": v.get("band"),
             "n_blocks": v.get("n_blocks"), "values": [[p, r3(x, 5)] for p, x in v.get("values") or []],
             "ci99": ci(v.get("ci99"))}
        for kk in ("sign_count", "fixed_prediction"):
            if v.get(kk) is not None:
                e[kk] = v[kk]
        for kk in ("L_P", "L_ops", "power_w", "work", "dhot", "iota_io"):
            if isinstance(v.get(kk), dict) and "mean" in v[kk]:
                e[kk] = ci(v[kk])
        it[k] = e
    blocks = []
    for b in dv["blocks"]:
        blocks.append({"pass": b["pass"], "round": b["round"], "type": b["type"], "void": b["void"],
                       "kappa_match": r3((b.get("kappa_network") or {}).get("match_cal")),
                       "runs": [{"name": r["name"], "role": r["role"], "t66": r3(r["t66_s"]), "censored": r["censored"],
                                 "sw_W": r3(r["sw_W"], 2), "kappa": r3(r["kappa"]), "tau_c": r3(r["tau_c_s"], 2),
                                 "W_idle": r3(r["W_idle"], 2), "void": r["void"]} for r in b["runs"]]})
    # the per-placement means of the registered tier-L trio (dev), and the calibration chains
    def per(name, key, typ="L16"):
        vv = [r[key] for b in blocks if b["type"] == typ for r in b["runs"]
              if r["name"] == name and r["role"] == "meas" and r[key] is not None and not r["void"]]
        return {"mean": r3(sum(vv) / len(vv), 3) if vv else None, "min": min(vv) if vv else None,
                "max": max(vv) if vv else None, "n": len(vv)}
    trio = {n: {"t66": per(n, "t66"), "sw_W": per(n, "sw_W"), "t66_S": per(n, "t66", "S")}
            for n in ("INT16@32", "PER16@32", "UNI32@16")}
    cal = [r["t66"] for b in blocks if b["type"] == "L16" and b["round"] == "r3" for r in b["runs"] if r["role"] == "cal"]
    l8 = next((b for b in blocks if b["type"] == "L8"), None)
    kappa_runs = {"L16": [sum(1 for b in blocks if b["type"] == "L16" for r in b["runs"] if r["role"] == "meas" and r["kappa"] is not None),
                          sum(1 for b in blocks if b["type"] == "L16" for r in b["runs"] if r["role"] == "meas")],
                  "match": [min(b["kappa_match"] for b in blocks if b["kappa_match"]),
                            max(b["kappa_match"] for b in blocks if b["kappa_match"])]}
    return {"card": "aifoundry3", "items": it, "blocks": blocks, "beta": r3(dv["dev"]["beta"], 5), "trio": trio,
            "cal_r3_L16": cal, "l8_block": l8, "kappa": kappa_runs, "source": "reductions/dev-r3.json"}


# ---------------------------------------------------------------------------------------------- registration
def registration():
    reg = load(os.path.join(HERE, "reductions", "reg.json"))["registration"]
    pr = load(os.path.join(HP, "prereg", "prereg.json"))
    sha = open(os.path.join(HP, "prereg", "PREREG.sha256")).read().split()[0]
    md = open(os.path.join(HP, "prereg", "PREREG.md"), "rb").read()
    import hashlib
    assert hashlib.sha256(md).hexdigest() == sha, "PREREG.md does not match PREREG.sha256"
    items = []
    for iid, v in pr["items"].items():
        r = reg["items"].get(iid, {})
        items.append({"id": iid, "type": v.get("type"), "prediction": v.get("prediction"), "band": r3(v.get("band"), 5),
                      "registered": bool(v.get("registered")), "reason": v.get("reason"),
                      "dev": ci(v.get("dev_ci99")), "n_dev_blocks": v.get("n_dev_blocks"),
                      "h_at_n_val": r3(v.get("h_at_n_val"), 4), "target_h": r3(v.get("target_h"), 4),
                      "s_card1": r3(v.get("s_card1"), 4), "power_work_pairs": v.get("power_work_pairs"),
                      "power_waived_pairs": v.get("power_waived_pairs")})
    fz = pr["frozen"]
    return {"prereg_sha256": sha, "written": pr.get("written"), "file": "tools/claims-v3/hp/prereg/PREREG.md",
            "items": items, "family_size": sum(1 for i in items if i["registered"]), "n_val": fz["n_val"],
            "types": fz["types"], "frozen": fz, "beta": r3(pr["beta"], 5), "cv": pr["cv"], "probes": pr["probes"],
            "trig_a_card1": pr["trig_a_card1"], "power_waiver_tier_s": pr["power_waiver_tier_s"],
            "outcome_precedence": pr["outcome_precedence"], "types_kept": reg["types_kept"], "d_s": pr.get("d_s"),
            "card1_minutes": reg.get("card1_minutes"), "n_val_rule": reg.get("n_val_rule")}


def v0():
    P = H.resolve_params("v0", "aifoundry1-c1")      # DEFAULTS + params/params-v0-aifoundry1-c1.json, as v0final
    series = H.v0_series(os.path.join(RAW, "aifoundry1-c1"), "aifoundry1-c1", "L", P)
    fin = load(os.path.join(HERE, "reductions", "v0.json"))
    T = P["T_cal_s"]["L"]
    edges = []
    for s in series:
        if s["edge"] is None:                  # a block that ended at once ("skipped": the rule had settled)
            continue
        tt = sorted(x for x in s["t66"] if x is not None)
        med = tt[len(tt) // 2] if tt else None
        edges.append({"pass": s["pass"], "edge": s["edge"], "t66": [r3(x) for x in s["t66"]], "median": r3(med),
                      "censored": s["censored"],
                      "rule": ("lower by 1" if med is not None and med < 0.5 * T else
                               "raise by 1" if s["censored"] or (med is not None and med > 2 * T) else "settle")})
    return {"T_cal_s": T, "lo_s": 0.5 * T, "hi_s": 2 * T, "start": P["S_L"], "edges": edges, "settled": fin["S_L"],
            "why": fin["L"]["why"], "a3_cal_r3": None}


# ---------------------------------------------------------------------------------------------- the design's constants
DESIGN_KEYS = ("S_launch_s", "chain_launch_s", "chain_after_66", "edge_wait_cap_s", "preheat_s", "C_S", "C_L",
               "kappa_gate", "void_tauc_lo", "void_tauc_hi", "void_widle_range_w", "void_work", "abs_stop_c",
               "cap_mean_c", "cap_high_c", "cap_board_w", "cap_consecutive", "guard_stop_c", "guard_widle_rise_w",
               "sampler_every_ms", "band_t", "band_power_w", "band_work", "reg_factor", "n_min", "n_max")


def design():
    """The fixed rules the page quotes (hplib.DEFAULTS and RANGES: DESIGN2, fixed before any data)."""
    out = {k: (r3(H.DEFAULTS[k], 5) if isinstance(H.DEFAULTS[k], float) else H.DEFAULTS[k]) for k in DESIGN_KEYS}
    out["ranges"] = {k: list(v) for k, v in H.RANGES.items() if k in ("S_L", "S_L8", "kappa_gate")}
    out["val_ranges"] = {k: list(H.VAL_RANGES[k]) for k in ("S_L", "S_L8")}
    return out


# ---------------------------------------------------------------------------------------------- departures
def departures():
    t = open(os.path.join(HP, "README.md")).read()
    sec = t.split("## Departures from DESIGN2", 1)[1].split("\n## ", 1)[0]
    out, cur = [], None
    for line in sec.splitlines():
        m = re.match(r"^(\d+)\. (.*)$", line)
        if m:
            cur = {"n": int(m.group(1)), "text": m.group(2).strip()}
            out.append(cur)
        elif cur is not None and line.strip():
            cur["text"] += " " + line.strip()
    for d in out:
        m = re.match(r"\*\*(.+?)\*\*", d["text"])
        d["title"] = m.group(1) if m else d["text"][:60]
    return out


# ---------------------------------------------------------------------------------------------- verdicts
THEORIES = [
    ("H1", "The governor acts on the mean of the 34 shire sensors", ["TRIG-A", "TRIG-B"]),
    ("H1'", "The governor acts on the hottest sensor", ["TRIG-A", "TRIG-B"]),
    ("H2", "The edges trip later: the same work placed on the perimeter takes longer to bring the mean to 66 °C", ["PLACE-t", "PLACE-tS"]),
    ("H3", "The centre trips later", ["PLACE-t"]),
    ("H4", "Only total power matters: placement changes the time to the trip by less than 10%", ["PLACE-t"]),
    ("H3'", "An airflow gradient across the heatsink (east against west, north against south)", ["GRAD-EW", "GRAD-NS"]),
    ("H6", "Heating is linear: the two halves' responses add up to the whole", ["LIN"]),
    ("H7", "Concentrating the work lifts the hottest sensor more than spreading it", ["CONC"]),
    ("H8", "The memory-strip side couples less heat into the mean", ["MEM"]),
    ("H9", "The bare north and south edges couple less heat into the mean", ["EDGE"]),
    ("H10", "The I/O corner is where the latency map puts it", ["MAP"]),
    ("H11", "Development's signs transfer to another card", ["H11"]),
    ("H12", "Placement delays the clock's step down (aifoundry2)", ["DVFS-PLACE"]),
    ("H13", "The placements draw equal power (and do equal work)", ["PLACE-t/POWER", "PLACE-t/WORK", "PLACE-tS/WORK"]),
]


def verdicts(val, regn):
    if val is None:
        return None
    v = val.get("validation") or {}
    items = v.get("items") or {}
    out = {"card": v.get("card"), "items": {}, "blocks": v.get("blocks"), "family_size": v.get("family_size"),
           "lock": v.get("lock")}
    for k, x in items.items():
        out["items"][k] = {kk: (ci(x[kk]) if kk in ("ci99", "tier_L_ci99") else x[kk]) for kk in x
                           if kk in ("outcome", "holds", "ci99", "prediction", "band", "primary", "reason", "note",
                                     "tier_L_ci99", "tier_L_blocks", "of", "words", "value")}
    # Which theories survived (the page's last table). H2, H11 and H13 are the registered items' own words; H3 and H4
    # were never registered on their own and are read from PLACE-t's 99% interval, and only once PLACE-t has its
    # frozen number of usable blocks (no reading from a partial set, as reduce.py --val's own rule).
    pt = (items.get("PLACE-t") or {})
    band = next((i["band"] for i in regn["items"] if i["id"] == "PLACE-t"), None)
    c = pt.get("ci99") or {}
    cnt = v.get("blocks") or {}
    full = (cnt.get("used") or {}).get("L16", 0) >= (cnt.get("n_val") or {}).get("L16", 1)
    lo, hi = c.get("lo"), c.get("hi")
    w = lambda k: (items.get(k) or {}).get("outcome")
    word3 = lambda o: {"PASS": "survived", "FAIL": "refuted"}.get(o, "undecided")
    th = {"H2": word3(w("PLACE-t")), "H2_S": w("PLACE-tS"), "H11": word3(w("H11")), "H11_word": w("H11"),
          "H13": word3(w("PLACE-t/POWER")), "H13_word": w("PLACE-t/POWER")}
    # DESIGN2's frozen table ("Theories survived"): H2 / H3 / H4 survive if PLACE-t is registered SIGN+ / SIGN- / EQUIV
    # and PASSes. PLACE-t was registered with one prediction, so only that theory has a frozen entry; the other two are
    # "not registered". Their *_reading is the page's own reading of PLACE-t's 99% interval, outside the frozen rules
    # (and only once PLACE-t has its frozen number of usable blocks), shown as such.
    pred = next((i.get("prediction") for i in regn["items"] if i["id"] == "PLACE-t"), None)
    frozen_of = {"SIGN+": "H2", "SIGN-": "H3", "SIGN−": "H3", "EQUIV": "H4"}
    reg_h = frozen_of.get(pred)
    for h in ("H2", "H3", "H4"):
        th[h] = word3(w("PLACE-t")) if h == reg_h else "not registered"
    th["registered_as"] = pred
    if not full or lo is None or hi is None or band is None:
        th["H3_reading"] = th["H4_reading"] = "undecided"
    else:
        th["H3_reading"] = "refuted" if lo > 0 else ("survived" if hi < 0 else "undecided")
        th["H4_reading"] = ("survived" if -band < lo and hi < band else
                            "refuted" if lo > band or hi < -band else "undecided")
    th["full_L16"] = full
    out["theories"] = th
    return out


def val_blocks(val, prereg):
    """Card 1's per-block values of every registered item, by the reducer's own functions on the raw validation
    blocks when they are in raw/aifoundry1-c1 (the same path reduce.py --val takes), else None."""
    d = os.path.join(RAW, "aifoundry1-c1")
    vb = [b for b in R.load_blocks(d, "aifoundry1-c1") if b["round"] == "val"] if os.path.isdir(d) else []
    if not vb or val is None:
        return None
    regd = [i for i, r in prereg["items"].items() if r.get("registered")]
    R.mark_incomplete(vb, regd)
    used, counts = R.select_val_blocks(vb, prereg)
    summ = R.summarise(used, "aifoundry1-c1", prereg.get("beta"), prereg.get("primary"))
    out = {"counts": counts, "items": {}}
    for iid in regd:
        s = summ.get(iid) or {}
        out["items"][iid] = {"values": [[p, r3(x, 5)] for p, x in s.get("values") or []], "ci99": ci(s.get("ci99")),
                             "sign_count": s.get("sign_count")}
    out["summary"] = val_summary(used, prereg)
    return out


def val_sessions():
    """{pass: session} from the validation queue logs (logs/queue-hp-aifoundry1-c1-val<session>.log): the session in
    which each block began, and each session's start (its "queue starts" line)."""
    by, starts = {}, {}
    for p in sorted(glob.glob(os.path.join(HERE, "logs", "queue-hp-aifoundry1-c1-val*.log"))):
        s = re.search(r"-val(\w+)\.log$", p).group(1)
        for line in open(p):
            m = re.search(r"hp p(\d+) begins", line)
            if m:
                by[int(m.group(1))] = s            # a later begin (a re-run in a later session) wins
            if "queue starts" in line and s not in starts:
                starts[s] = line.split()[0].replace("T", " ")
    return by, starts


def val_summary(used, prereg):
    """What the verdicts rest on, from the same blocks reduce.py --val used: each registered placement's times to
    66 °C on card 1 and how many runs the chain cap cut off (censored), block by block with its session, and card 1's
    Tier L calibration chains (ALL24, never a tested workload) against its V0 chains. Reported numbers: no test."""
    PAIR = ("PER16@32", "INT16@32")                     # PLACE-t and PLACE-tS: L(PER16@32 / INT16@32)
    TRIO3 = ("INT16@32", "PER16@32", "UNI32@16")
    sess, starts = val_sessions()
    fz = prereg.get("frozen") or {}
    band = (prereg.get("items", {}).get("PLACE-t") or {}).get("band")
    out = {"sessions": starts, "C": {"L16": fz.get("C_L"), "S": 7.0}, "band": band}
    for typ in ("L16", "S"):
        bl = sorted([b for b in used if b["type"] == typ], key=lambda b: b["pass"])
        by_pl = {n: {"t66": [], "censored": 0, "n": 0} for n in TRIO3}
        blocks = []
        for b in bl:
            names = R.by_name(b)
            row = {"pass": b["pass"], "session": sess.get(b["pass"]), "runs": {}}
            for n in TRIO3:
                x = (names.get(n) or [None])[-1]
                if x is None:
                    continue
                o = x["obs"]
                row["runs"][n] = {"t66": r3(o.get("t66_s")), "censored": bool(o.get("censored"))}
                by_pl[n]["n"] += 1
                if o.get("censored"):
                    by_pl[n]["censored"] += 1
                elif o.get("t66_s") is not None:
                    by_pl[n]["t66"].append(r3(o["t66_s"]))
            cal = [r3(x["obs"]["t66_s"]) for x in b["runs"] if x["rec"].get("role") == "cal" and not x["obs"]["void"]
                   and x["obs"].get("t66_s") is not None]
            row["cal_t66"] = cal
            a, c = row["runs"].get(PAIR[0]), row["runs"].get(PAIR[1])
            row["pair"] = ("both censored" if a and c and a["censored"] and c["censored"] else
                           "perimeter longer" if a and c and (a["censored"] or (not c["censored"] and a["t66"] > c["t66"])) else
                           "interior longer" if a and c else None)
            blocks.append(row)
        for n, v in by_pl.items():
            t = sorted(v["t66"])
            v["mean_crossed"] = r3(sum(t) / len(t)) if t else None
            v["median_crossed"] = r3(t[len(t) // 2] if len(t) % 2 else (t[len(t) // 2 - 1] + t[len(t) // 2]) / 2) if t else None
        pairs = [r["pair"] for r in blocks]
        out[typ] = {"blocks": blocks, "placements": by_pl,
                    "runs": sum(v["n"] for v in by_pl.values()), "censored": sum(v["censored"] for v in by_pl.values()),
                    "pairs": {k: pairs.count(k) for k in ("perimeter longer", "interior longer", "both censored")}}
        if typ == "L16":
            cal = sorted(x for r in blocks for x in r["cal_t66"])
            out[typ]["cal_t66"] = {"n": len(cal), "min": cal[0] if cal else None, "max": cal[-1] if cal else None,
                                   "median": r3(cal[len(cal) // 2] if len(cal) % 2 else (cal[len(cal) // 2 - 1] + cal[len(cal) // 2]) / 2) if cal else None}
            by_s = {}
            for r in blocks:
                s = by_s.setdefault(r["session"], {"blocks": [], "runs": 0, "censored": 0})
                s["blocks"].append(r["pass"])
                for x in r["runs"].values():
                    s["runs"] += 1; s["censored"] += int(x["censored"])
            out[typ]["by_session"] = by_s
    return out


# ---------------------------------------------------------------------------------------------- tau_c by role
def tauc_roles(val):
    """The edge-cooling time (tau_c, the reducer's own observable) of the burn-in CAL runs against the measured runs,
    per block type, on the development card and (with val.json) card 1's validation blocks. The block-void rule is read
    over the measured runs only (reduce.py block_void over kept_runs; README departure 40); `literal_void` counts the
    blocks that the design's literal "any run's tau_c" would void, with the CAL runs included. Reported, no test."""
    out = {}
    for card, rounds in (("aifoundry3", ["r1", "r2", "r3"]), ("aifoundry1-c1", ["val"])):
        if card != "aifoundry3" and val is None:
            continue
        d = os.path.join(RAW, card)
        if not os.path.isdir(os.path.join(d, "hp")):
            continue
        for b in R.load_blocks(d, card, rounds=rounds):
            if b["type"] not in ("L16", "S"):
                continue
            cal = [x["obs"].get("tau_c_s") for x in b["runs"] if x["rec"].get("role") == "cal"]
            first = next((t for t in cal if t), None)
            meas = [x["obs"].get("tau_c_s") for x in R.kept_runs(b).values() if x["obs"].get("tau_c_s")]
            allt = sorted(t for t in cal + meas if t)
            n = len(allt)
            med = (allt[n // 2] if n % 2 else (allt[n // 2 - 1] + allt[n // 2]) / 2) if n else None
            P = b["params"]
            lit = bool(med) and any(not P.get("void_tauc_lo", 0.5) * med <= t <= P.get("void_tauc_hi", 2.0) * med
                                    for t in allt)
            e = out.setdefault(b["type"], {"first_cal": [], "meas": [], "blocks": 0, "literal_void": 0,
                                           "cards": [], "by_card": {}})
            if card not in e["cards"]:
                e["cards"].append(card)
            if first:
                e["first_cal"].append(first)
            e["meas"] += meas
            e["blocks"] += 1
            e["literal_void"] += int(lit)
            bc = e["by_card"].setdefault(card, {"blocks": 0, "literal_void": 0})
            bc["blocks"] += 1
            bc["literal_void"] += int(lit)
    for e in out.values():
        for k in ("first_cal", "meas"):
            e[k] = [r3(min(e[k]), 2), r3(max(e[k]), 2)] if e[k] else None
    return out


# ---------------------------------------------------------------------------------------------- main
def build(val_path):
    val = load(val_path) if val_path and os.path.exists(val_path) else None
    prereg = load(os.path.join(HP, "prereg", "prereg.json"))
    regn = registration()
    out = {
        "generated_by": rel(os.path.abspath(__file__)),
        "val_json": rel(val_path) if val else None,
        "placements": placements(),
        "q1": q1(),
        "timeline": timeline(),
        "dev": development(),
        "registration": regn,
        "v0": v0(),
        "traces": {"aifoundry3": traces("aifoundry3", ["r1", "r2", "r3"]),
                   "aifoundry1-c1": traces("aifoundry1-c1", ["val"]) if val else {}},
        "verdicts": verdicts(val, regn),
        "val_blocks": val_blocks(val, prereg),
        "theories": [{"id": a, "text": b, "items": c} for a, b, c in THEORIES],
        "design": design(),
        "tauc_roles": tauc_roles(val),
        "departures": departures(),
        "cards": {"development": "aifoundry3", "validation": ["aifoundry1-c1"], "q1_same_day": "aifoundry2"},
    }
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--val", default=os.path.join(HERE, "val.json"))
    ap.add_argument("--out", default=os.path.join(HERE, "heat.json"))
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    s = json.dumps(build(a.val), indent=1, sort_keys=False, ensure_ascii=False) + "\n"
    if a.check:
        old = open(a.out).read() if os.path.exists(a.out) else ""
        print("heat.json is %s" % ("current" if old == s else "STALE"))
        sys.exit(0 if old == s else 1)
    open(a.out, "w").write(s)
    d = json.loads(s)
    pt = d["dev"]["items"]["PLACE-t"]["ci99"]
    print("wrote %s (%d bytes): PLACE-t dev %.3f [%.3f, %.3f] over %d blocks; verdicts %s" % (
        rel(a.out), len(s), pt["mean"], pt["lo"], pt["hi"], pt["n"],
        "from " + rel(a.val) if d["verdicts"] else "pending (no val.json)"))


if __name__ == "__main__":
    main()
