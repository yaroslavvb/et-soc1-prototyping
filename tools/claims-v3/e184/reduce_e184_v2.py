#!/usr/bin/env python3
"""E184's reduction, v2 (kit note 1, KIT.md.dated-note-1.md section 2; dated amendment A2, A2-5): reduce_e184.py (v1, which stays as
committed) with the gates the verifier found missing (its fault 3) and A2-5's refresh rule. Desk only; it never opens a card.

    python3 -B tools/claims-v3/e184/reduce_e184_v2.py <raw dir> --arm S [--t0 <epoch>] > reduced-e184s-v2.json
    python3 -B tools/claims-v3/e184/reduce_e184_v2.py <raw dir> --arm B [--t0 <epoch>] > reduced-e184b-v2.json
    <raw dir>/<card>/e184{,-smoke,-stoptest}/p184NN/ and <raw dir>/<card>/logs/ (the box's build/e184/: the session's own log, queue output,
    config reads and preflight, every one named by its T0), as the runbook's step 22 (rb/s22_collect_e184.sh) copies them back.

What changes from v1, and nothing else:
1. A2-5 (arm S): inside every block, after E82 amendment A2's dip rule and the 0.35 s discard (v1's reader, unchanged), a kept refresh more
   than 0.5 W from the median of that block's kept refreshes is set aside (board_w; the rail's block reads the same refreshes). A block
   still needs 4 refreshes. Each quad records how many A2-5 set aside; the pass and the arm their sum. On E180's committed fadd.ps bursts
   this rule sets aside 5 of 2,649 block refreshes, the 4 partial dips the verifier counted and one more, 0.72 W low (a2-check-e184.json).
2. The pass gate, E180's (reduce_e180_v3.py, lines 145-146): a pass whose block.json status is not "ok" or "partial" (a stop, a fail,
   another user's process, no block.json) is set aside whole: its reading is kept nowhere, and the pass is listed with its reason. And a
   pass any of whose busy samples (board above 28 W) is off 600 MHz is set aside, read again here from its telemetry (check_e184_v2.py's
   verdict, which makes such a pass "fail"; for a pass checked by v1 it was "partial").
3. The session gate, per arm, from <card>/logs/: the session is the one whose T0 is given (--t0), else the newest real one there
   (session-<arm>-t<T0>.log; a dry session's log never counts). It holds when (a) that log says "smoke gate passed" and the smoke, checked
   again here by check_e184_v2.py smoke on the copied pass, reads SMOKE GO; (b) both config reads exist (config-<arm>-t<T0>-start.json and
   -end.json) and read the card as registered: aifoundry3 TDP 0 W, threshold 65 C, minion 600 MHz, at both; card 1 minion 600 MHz at both,
   and the same TDP and threshold at both (its own, never set). The reduced file carries session.gate_ok and every reason; score_e184_v2.py
   scores no rule of an arm whose gate does not hold.
Arm B: v1's reduce_b, unchanged, then gates 2 and 3.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import glob
import io
import json
import os
import re
import sys
from contextlib import redirect_stdout

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import e184_common as c  # noqa: E402
import reduce_e184 as r1  # noqa: E402
import check_e184_v2 as chk  # noqa: E402

ROBUST_W = 0.5
CARDS = {"S": "aifoundry3", "B": "aifoundry1-c1"}
SMOKES = {"S": "p18401", "B": "p18431"}


def read_process_a2(samples, launches):
    """e184_common.read_process (v1's reader, line for line) with A2-5's rule inside each block; board and rail from the same refreshes.
    Returns {'board': blocks, 'rail': blocks, 'a2_5': n set aside, 'reason': None or why the quad is set aside}."""
    segs = {}
    for ln in launches:
        s = segs.setdefault(ln["seg"], {"label": ln["label"], "t0": ln["t_start_ms"], "t1": ln["t_end_ms"], "n": 0, "ok": True})
        s["t0"] = min(s["t0"], ln["t_start_ms"])
        s["t1"] = max(s["t1"], ln["t_end_ms"])
        s["n"] += 1
        s["ok"] = s["ok"] and bool(ln.get("ok", True))
    order = sorted(segs)
    out = {"board": [], "rail": [], "a2_5": 0, "reason": None}
    if [segs[k]["label"] for k in order][:1] != ["S"] or len(order) != 5:
        out["reason"] = "segments %s, not S + four blocks" % [segs[k]["label"] for k in order]
        return out
    if any(not segs[k]["ok"] for k in order):
        out["reason"] = "a launch did not end ok"
        return out
    if any(segs[k]["n"] != (c.SETTLE_LAUNCHES if segs[k]["label"] == "S" else c.BLOCK_LAUNCHES) for k in order):
        out["reason"] = "a segment ran %s launches" % [segs[k]["n"] for k in order]
        return out
    t_lo = segs[order[0]]["t0"] - 1000
    t_hi = segs[order[-1]]["t1"] + 1000
    ref = c.refreshes([d for d in samples if t_lo <= d.get("t_ms", -1) <= t_hi])
    xs = [d["board_w"] for d in ref]
    kept = set(c.dip_keep(xs))
    for k in order[1:]:
        g = segs[k]
        lo, hi = g["t0"] + c.DISCARD_S * 1000.0, g["t1"]
        idx = [i for i, d in enumerate(ref) if i in kept and lo <= d["t_ms"] <= hi]
        vals = [xs[i] for i in idx]
        if vals:
            m = c.median(vals)
            keep = [i for i, v in zip(idx, vals) if abs(v - m) <= ROBUST_W]
            out["a2_5"] += len(idx) - len(keep)
            idx = keep
        if len(idx) < c.MIN_REFRESHES:
            out["reason"] = "block %s has %d kept refreshes (< %d, after A2-5)" % (g["label"], len(idx), c.MIN_REFRESHES)
            out["board"], out["rail"] = [], []
            return out
        out["board"].append((g["label"], c.fmean(xs[i] for i in idx), len(idx), g["t0"], g["t1"]))
        out["rail"].append((g["label"], c.fmean(ref[i]["sp"]["minion_w"][0] for i in idx), len(idx), g["t0"], g["t1"]))
    if tuple(b[0] for b in out["board"]) not in c.ORIENT.values():
        out["reason"] = "block order %s" % (tuple(b[0] for b in out["board"]),)
        out["board"], out["rail"] = [], []
    return out


def mhz_ok(tel):
    busy = [d["mhz"]["minion"] for d in tel if d.get("board_w", 0) > 28 and "mhz" in d]
    return all(m == 600 for m in busy), len(busy)


def pass_gate(pdir, tel):
    """E180's rule and the 600 MHz re-read. Returns (keep, why, block_status)."""
    blk = r1.jload(os.path.join(pdir, "block.json"), None)
    st = blk.get("status") if isinstance(blk, dict) else None
    if st not in ("ok", "partial"):
        return False, "block status %s" % st, st
    ok, nb = mhz_ok(tel)
    if not ok:
        return False, "a busy sample off 600 MHz (%d busy samples)" % nb, st
    return True, None, st


def session_gate(raw, arm, t0):
    card = CARDS[arm]
    logs = os.path.join(raw, card, "logs")
    g = {"logs_dir": os.path.relpath(logs, raw), "t0": t0, "reasons": []}
    cands = []
    for p in glob.glob(os.path.join(logs, "session-%s-t*.log" % arm)):
        mt = re.match(r"session-%s-t(\d+)\.log$" % arm, os.path.basename(p))
        if mt:
            cands.append(int(mt.group(1)))
    if t0 is None:
        t0 = max(cands) if cands else None
        g["t0"] = t0
        g["t0_from"] = "the newest real session log" if t0 else None
    else:
        g["t0_from"] = "--t0"
    g["session_logs_found"] = sorted(cands)
    log = os.path.join(logs, "session-%s-t%s.log" % (arm, t0)) if t0 else None
    if not log or not os.path.exists(log):
        g["reasons"].append("no session log for T0 %s in %s" % (t0, g["logs_dir"]))
        txt = ""
    else:
        txt = open(log, errors="replace").read()
    g["log_smoke_gate_passed"] = "smoke gate passed" in txt
    g["log_session_end"] = ("session end (T0 %s)" % t0) in txt
    if txt and not g["log_smoke_gate_passed"]:
        g["reasons"].append("the session log has no 'smoke gate passed' line")
    sp = os.path.join(raw, card, "e184-smoke", SMOKES[arm])
    if os.path.isdir(sp):
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = chk.smoke(sp)
        g["desk_smoke"] = buf.getvalue().strip()
        if rc != 0:
            g["reasons"].append("the smoke, checked again at the desk: " + g["desk_smoke"][:300])
    else:
        g["desk_smoke"] = None
        g["reasons"].append("no smoke pass in the raw copy")
    cfg = {}
    for edge in ("start", "end"):
        p = os.path.join(logs, "config-%s-t%s-%s.json" % (arm, t0, edge)) if t0 else None
        try:
            cfg[edge] = json.load(open(p)) if p else None
        except (OSError, ValueError):
            cfg[edge] = None
        if not isinstance(cfg[edge], dict) or cfg[edge].get("dry"):
            g["reasons"].append("no %s config read for T0 %s" % (edge, t0))
            cfg[edge] = cfg[edge] if isinstance(cfg[edge], dict) else None
    g["config"] = cfg
    a, b = cfg.get("start") or {}, cfg.get("end") or {}
    if a and b and not a.get("dry") and not b.get("dry"):
        if arm == "S":
            for edge, x in (("start", a), ("end", b)):
                if not (x.get("tdp_w") == 0 and x.get("temp_threshold_c") == 65 and x.get("minion_mhz") == 600):
                    g["reasons"].append("the %s config read is not TDP 0 W / 65 C / 600 MHz: %s" % (edge, json.dumps(x, sort_keys=True)[:200]))
        else:
            for edge, x in (("start", a), ("end", b)):
                if x.get("minion_mhz") != 600:
                    g["reasons"].append("the %s config read is not 600 MHz" % edge)
            for k in ("tdp_w", "temp_threshold_c"):
                if a.get(k) != b.get(k):
                    g["reasons"].append("%s changed between the start and end reads (%s, %s)" % (k, a.get(k), b.get(k)))
    g["gate_ok"] = not g["reasons"]
    return g


def reduce_s(raw):
    card = os.path.join(raw, "aifoundry3")
    out = {"arm": "S", "card": "aifoundry3", "passes": {}, "set_aside_passes": {}, "glitch": {"samples": 0, "avg_equals_running_max": 0},
           "a2_5_set_aside": 0, "reducer": "reduce_e184_v2.py"}
    for exp in ("e184-smoke", "e184"):
        d = os.path.join(card, exp)
        if not os.path.isdir(d):
            continue
        for pn in sorted(os.listdir(d)):
            if not pn.startswith("p") or ".attempt" in pn:
                continue
            pdir = os.path.join(d, pn)
            tel, runs = r1.jl(os.path.join(pdir, "telemetry.jsonl")), r1.jl(os.path.join(pdir, "runs.jsonl"))
            keep, why, st = pass_gate(pdir, tel)
            g = r1.glitches(tel)
            if not keep:
                out["set_aside_passes"][pn[1:]] = {"exp": exp, "why": why, "block_status": st, "stop": r1.jload(os.path.join(pdir, "stop.json"))}
                continue
            out["glitch"]["samples"] += g["samples"]
            out["glitch"]["avg_equals_running_max"] += g["avg_equals_running_max"]
            by = {}
            for r in runs:
                by.setdefault(r["seq"], []).append(r)
            quads, aside, n25 = [], [], 0
            for seq, lns in sorted(by.items()):
                rd = read_process_a2(tel, lns)
                q = {"seq": seq, "part": lns[0]["part"], "n": lns[0]["n"], "ref": lns[0]["ref"], "mask_m": lns[0]["mask_m"],
                     "orient": lns[0]["orient"], "t0_ms": min(x["t_start_ms"] for x in lns), "a2_5_set_aside": rd["a2_5"]}
                n25 += rd["a2_5"]
                if rd["reason"] is not None:
                    aside.append(dict(q, reason=rd["reason"]))
                    continue
                q["y"], q["base"] = c.quad_contrast(rd["board"])
                q["refreshes"] = [b[2] for b in rd["board"]]
                q["y_rail"], q["base_rail"] = c.quad_contrast(rd["rail"])
                quads.append(q)
            out["a2_5_set_aside"] += n25
            blk = r1.jload(os.path.join(pdir, "block.json"), {})
            out["passes"][pn[1:]] = {"exp": exp, "block_status": blk.get("status"), "block_note": blk.get("note"), "quads": quads,
                                     "set_aside": aside, "a2_5_set_aside": n25, "cal": r1.jload(os.path.join(pdir, "cal.json")),
                                     "stop": r1.jload(os.path.join(pdir, "stop.json"))}
    return out


def reduce_b(raw):
    out = r1.reduce_b(raw)
    out["reducer"] = "reduce_e184_v2.py (v1's reduce_b, then the pass gate)"
    out["set_aside_passes"] = {}
    card = os.path.join(raw, "aifoundry1-c1")
    g_s = g_n = 0
    for p in sorted(out["passes"]):
        rec = out["passes"][p]
        pdir = os.path.join(card, rec["exp"], "p" + p)
        tel = r1.jl(os.path.join(pdir, "telemetry.jsonl"))
        keep, why, st = pass_gate(pdir, tel)
        if not keep:
            out["set_aside_passes"][p] = {"exp": rec["exp"], "why": why, "block_status": st, "stop": rec.get("stop")}
            del out["passes"][p]
            continue
        if p != "18441":
            g_s += rec["glitch"]["samples"]
            g_n += rec["glitch"]["avg_equals_running_max"]
    out["glitch"] = {"samples": g_s, "avg_equals_running_max": g_n}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("raw")
    ap.add_argument("--arm", choices=["S", "B"], required=True)
    ap.add_argument("--t0", type=int, default=None)
    a = ap.parse_args()
    res = reduce_s(a.raw) if a.arm == "S" else reduce_b(a.raw)
    res["session"] = session_gate(a.raw, a.arm, a.t0)
    print(json.dumps(res, indent=1, sort_keys=True))


if __name__ == "__main__":
    main()
