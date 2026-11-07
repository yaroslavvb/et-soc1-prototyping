#!/usr/bin/env python3
"""E184's reduction (the kit): the collected raw passes of either arm into the numbers the scorer reads. Desk only; it never opens a card.

    python3 -B tools/claims-v3/e184/reduce_e184.py <raw dir> --arm S > reduced-e184s.json   # <raw dir>/aifoundry3/e184{,-smoke}/p184NN/
    python3 -B tools/claims-v3/e184/reduce_e184.py <raw dir> --arm B > reduced-e184b.json   # <raw dir>/aifoundry1-c1/e184{,-smoke}/p184NN/

Arm S: every quad of every pass through e184_common.read_process, on the board (board_w) and on the minion rail's PMIC average; a quad
that cannot be read is set aside with the reason, and kept nowhere. Per pass: the block's status, the quads (seq, part, n, ref, mask,
orientation, contrast, the A blocks' level), the calibration (cal.json) where it is, and the minion-average glitch count.
Arm B: B1's steady reset-window samples per level (e184_common.reset_window_ratios, Q150's rule) with E184.md section 5.3's gap rule (a
sample counts only if its window, from its reset to the sample, lies inside one span of launches with no gap over 50 ms, or inside the
idle item's span); each reset's restart (the first non-zero average after it over the window's last); B2's step responses per burst and
rail by dated amendment A1's reader (tau_a1_e184.fit_burst: E58's filter model, its rise and fall split); B3's SRAM share of the board
over idle per burst; the glitch census (the plain passes only).
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import gzip
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import e184_common as c  # noqa: E402
import tau_a1_e184 as tau  # noqa: E402

RAILS = ("sram_w", "minion_w", "noc_w")
SP_PASS_S = 0.16


def jl(path):
    for p, op in ((path + ".gz", gzip.open), (path, open)):
        if os.path.exists(p):
            out = []
            with op(p, "rt") as f:
                for line in f:
                    if line.startswith("{"):
                        try:
                            out.append(json.loads(line))
                        except ValueError:
                            pass
            return out
    return []


def jload(path, default=None):
    try:
        return json.load(open(path))
    except (OSError, ValueError):
        return default


def r6(x):
    return None if x is None or x != x else float("%.6g" % x)


def glitches(tel):
    n = g = 0
    for d in tel:
        try:
            mw = d["sp"]["minion_w"]
        except (KeyError, TypeError):
            continue
        n += 1
        g += 1 if mw[0] == mw[2] else 0
    return {"samples": n, "avg_equals_running_max": g}


# ---- arm S --------------------------------------------------------------------------------------------------------------------------
def reduce_s(raw):
    card = os.path.join(raw, "aifoundry3")
    out = {"arm": "S", "card": "aifoundry3", "passes": {}, "glitch": {"samples": 0, "avg_equals_running_max": 0}}
    for exp in ("e184-smoke", "e184"):
        d = os.path.join(card, exp)
        if not os.path.isdir(d):
            continue
        for pn in sorted(os.listdir(d)):
            if not pn.startswith("p") or ".attempt" in pn:
                continue
            pdir = os.path.join(d, pn)
            tel, runs = jl(os.path.join(pdir, "telemetry.jsonl")), jl(os.path.join(pdir, "runs.jsonl"))
            g = glitches(tel)
            out["glitch"]["samples"] += g["samples"]
            out["glitch"]["avg_equals_running_max"] += g["avg_equals_running_max"]
            by = {}
            for r in runs:
                by.setdefault(r["seq"], []).append(r)
            quads, aside = [], []
            for seq, lns in sorted(by.items()):
                rb = c.read_process(tel, lns, "board")
                rr = c.read_process(tel, lns, "rail")
                q = {"seq": seq, "part": lns[0]["part"], "n": lns[0]["n"], "ref": lns[0]["ref"], "mask_m": lns[0]["mask_m"],
                     "orient": lns[0]["orient"], "t0_ms": min(x["t_start_ms"] for x in lns)}
                if rb["reason"] is not None:
                    aside.append(dict(q, reason=rb["reason"]))
                    continue
                q["y"], q["base"] = c.quad_contrast(rb["blocks"])
                q["refreshes"] = [b[2] for b in rb["blocks"]]
                if rr["reason"] is None:
                    q["y_rail"], q["base_rail"] = c.quad_contrast(rr["blocks"])
                quads.append(q)
            blk = jload(os.path.join(pdir, "block.json"), {})
            out["passes"][pn[1:]] = {"exp": exp, "block_status": blk.get("status"), "block_note": blk.get("note"), "quads": quads,
                                     "set_aside": aside, "cal": jload(os.path.join(pdir, "cal.json")),
                                     "stop": jload(os.path.join(pdir, "stop.json"))}
    return out


# ---- arm B --------------------------------------------------------------------------------------------------------------------------
def spans_of(launches, marks, item, max_gap_ms=50):
    if item["cfg"] == "idle":
        st = [m["t_ms"] for m in marks if m.get("event") == "item_start" and m.get("seq") == item["seq"]]
        en = [m["t_ms"] for m in marks if m.get("event") == "item_end" and m.get("seq") == item["seq"]]
        return [(st[0], en[0])] if st and en else []
    iv = sorted((r["t_start_ms"], r["t_end_ms"]) for r in launches if r["seq"] == item["seq"] and r.get("ok"))
    spans = []
    for a, b in iv:
        if spans and a - spans[-1][1] <= max_gap_ms:
            spans[-1] = (spans[-1][0], max(spans[-1][1], b))
        else:
            spans.append((a, b))
    return spans


def in_spans(t0, t1, spans):
    return any(a <= t0 and t1 <= b for a, b in spans)


def restarts_in(sub, spans):
    """Each reset inside one span: the first non-zero average of a rail after it, over the rail's last average before it."""
    out = {r: [] for r in RAILS}
    prev, pending, t_last = None, {}, None
    for d in sub:
        s = d.get("since_reset_ms")
        sp = d.get("sp")
        if (prev is not None and s is not None and prev.get("since_reset_ms") is not None and 0 <= s < prev["since_reset_ms"]
                and prev.get("sp") and in_spans(prev["t_ms"], d["t_ms"], spans)):
            pending, t_last = {r: prev["sp"][r][0] for r in RAILS}, prev["t_ms"]
        if sp and pending:
            if not in_spans(t_last, d["t_ms"], spans):
                pending = {}
            for r in list(pending):
                if sp[r][0] > 0:
                    if pending[r] > 0:
                        out[r].append(sp[r][0] / pending[r])
                    del pending[r]
        prev = d
    return out


def b1_levels(pdir, items, reset):
    tel, runs, marks = jl(os.path.join(pdir, "telemetry.jsonl")), jl(os.path.join(pdir, "runs.jsonl")), jl(os.path.join(pdir, "marks.jsonl"))
    levels, restarts = [], {r: [] for r in RAILS}
    for it in items:
        spans = spans_of(runs, marks, it)
        row = {"seq": it["seq"], "cfg": it["cfg"], "mask_m": it["mask_m"], "spans": len(spans)}
        sub = [d for d in tel if any(a <= d.get("t_ms", -1) <= b for a, b in spans)]
        avg = {rail: [d["sp"][rail][0] for d in sub if d.get("sp")] for rail in RAILS}
        row["avg_w"] = {rail: r6(c.median(v)) for rail, v in avg.items()}
        row["board_w"] = r6(c.median([d["board_w"] for d in sub])) if sub else None
        if reset:
            for rail in RAILS:
                ok = [d for d in sub if d.get("since_reset_ms") is not None and d.get("since_reset_ms", -1) >= 0
                      and in_spans(d["t_ms"] - d["since_reset_ms"], d["t_ms"], spans)]
                rs = c.reset_window_ratios(ok, rail)
                row[rail] = {"n": len(rs), "min_over_avg": r6(c.median([x[0] for x in rs])), "max_over_avg": r6(c.median([x[1] for x in rs])),
                             "min_over_avg_all": [r6(x[0]) for x in rs], "max_over_avg_all": [r6(x[1]) for x in rs]}
            rr = restarts_in(sub, spans)
            row["restart"] = {r: r6(c.median(v)) if v else None for r, v in rr.items()}
            for r in RAILS:
                restarts[r].extend(rr[r])
        levels.append(row)
    return levels, {rail: [r6(x) for x in restarts[rail]] for rail in RAILS}, glitches(tel)


def b2_fits(pdir, items):
    """B2 under dated amendment A1: each burst's rails read with E58's filter model (tau_a1_e184.fit_burst), on the pass grid."""
    tel, runs = jl(os.path.join(pdir, "telemetry.jsonl")), jl(os.path.join(pdir, "runs.jsonl"))
    tp, ref = tau.passes(tel)
    e58 = json.load(open(os.path.join(HERE, "..", "..", "..", "docs/reports/data/2026-09-29-tau-aifoundry1-c1/report.json")))
    dd = {rail: e58[rail]["100"]["one_pass"]["d_s"] for rail in RAILS}
    edges = []
    for it in items:
        lns = [r for r in runs if r["seq"] == it["seq"] and r.get("ok")]
        edges.append((it, min(r["t_start_ms"] for r in lns) / 1000.0, max(r["t_end_ms"] for r in lns) / 1000.0) if lns else (it, None, None))
    out = []
    for k, (it, tr, tf) in enumerate(edges):
        if tr is None:
            out.append({"seq": it["seq"], "reason": "no launch"})
            continue
        t_next = next((e[1] for e in edges[k + 1:] if e[1] is not None), None)
        row = {"seq": it["seq"], "burst_s": it["burst_s"]}
        for rail in RAILS:
            row[rail] = tau.fit_burst(tp, [d["sp"][rail][0] for d in ref], tr, tf, t_next, dd[rail])
        out.append(row)
    return out, glitches(tel)


def b3_shares(pdir, items):
    tel, runs = jl(os.path.join(pdir, "telemetry.jsonl")), jl(os.path.join(pdir, "runs.jsonl"))
    out = []
    for it in items:
        lns = [r for r in runs if r["seq"] == it["seq"] and r.get("ok")]
        if not lns:
            out.append({"seq": it["seq"], "cfg": it["cfg"], "reason": "no launch"})
            continue
        t0, t1 = min(r["t_start_ms"] for r in lns), max(r["t_end_ms"] for r in lns)
        idle = [d for d in tel if t0 - 1500 <= d["t_ms"] <= t0 - 200]
        busy = [d for d in tel if t1 - 1000 <= d["t_ms"] <= t1]
        if not idle or not busy:
            out.append({"seq": it["seq"], "cfg": it["cfg"], "reason": "no idle or busy samples"})
            continue
        so = c.fmean(d["sp"]["sram_w"][0] for d in busy) - c.fmean(d["sp"]["sram_w"][0] for d in idle)
        bo = c.fmean(d["board_w"] for d in busy) - c.fmean(d["board_w"] for d in idle)
        out.append({"seq": it["seq"], "cfg": it["cfg"], "sram_over_w": r6(so), "board_over_w": r6(bo), "share": r6(so / bo) if bo > 0.2 else None})
    return out, glitches(tel)


def reduce_b(raw):
    plan = json.load(open(os.path.join(HERE, "plan-e184.json")))
    passes = {q["pass"]: q for q in plan["arm_B"]["passes"]}
    card = os.path.join(raw, "aifoundry1-c1")
    out = {"arm": "B", "card": "aifoundry1-c1", "passes": {}, "glitch": {"samples": 0, "avg_equals_running_max": 0}}
    for exp in ("e184-smoke", "e184"):
        d = os.path.join(card, exp)
        if not os.path.isdir(d):
            continue
        for pn in sorted(os.listdir(d)):
            if not pn.startswith("p") or ".attempt" in pn:
                continue
            p = int(pn[1:])
            pdir = os.path.join(d, pn)
            cfg = jload(os.path.join(pdir, "configs.json"), {})
            items = cfg.get("items") or passes.get(p, {}).get("items", [])
            blk = jload(os.path.join(pdir, "block.json"), {})
            rec = {"exp": exp, "block_status": blk.get("status"), "block_note": blk.get("note"), "stop": jload(os.path.join(pdir, "stop.json"))}
            if p in (18440, 18441):
                rec["levels"], rec["restarts"], g = b1_levels(pdir, items, p == 18441)
            elif p == 18442:
                rec["fits"], g = b2_fits(pdir, items)
            elif p in (18443, 18444):
                rec["shares"], g = b3_shares(pdir, items)
            else:
                g = glitches(jl(os.path.join(pdir, "telemetry.jsonl")))
            if p != 18441:      # the census reads the plain passes only: after a reset the first update makes average, min and max equal
                out["glitch"]["samples"] += g["samples"]
                out["glitch"]["avg_equals_running_max"] += g["avg_equals_running_max"]
            rec["glitch"] = g
            out["passes"][str(p)] = rec
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("raw")
    ap.add_argument("--arm", choices=["S", "B"], required=True)
    a = ap.parse_args()
    res = reduce_s(a.raw) if a.arm == "S" else reduce_b(a.raw)
    print(json.dumps(res, indent=1, sort_keys=True))


if __name__ == "__main__":
    main()
