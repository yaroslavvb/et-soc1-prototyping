#!/usr/bin/env python3
"""E183's reduction (Q155, the kit; E183.md section 5.1): each train block's launches read as an A B B A train, by the registration's own
statistics (e183_stats.py, which imports E182's e182_stats.py unchanged), and each block's anchors by the energy catalogue's own reduction
(workloads/enercat/analyze_catalogue.py's bursts_of, E180's, unchanged). Reads committed or collected files only; opens no device.

    /usr/bin/python3 -B tools/claims-v3/e183/reduce_e183.py --raw <collection's raw dir> --out reduced-e183.json [--root <lab repo>]

THE TRAIN (per block p18310-p18315 under <raw>/e183/): the block's 10 Hz samples (telemetry.jsonl[.gz]: t_ms, board_w) after E82 A2's dip
rule over the block (e182_stats.dips_kept); each launch's reading in [t_start + 170 ms, t_end] (e182_stats.launch_reading); a process gives
quads (launches 1-4, 5-8, 9-12, signed by its orientation: e182_stats.quads_of_process) only when it has exactly 13 launch records, every
one ok, each launch's kind, orientation and number by the registered schedule, and no stop fired during it (stop.json); else it gives no
value. The planned processes and their orientations are the block's configs.json (the runner's, from plan-e183.json).
REPORTED (never a verdict): each process's raw readings and quads; the carry-over reading (L3 - L2 in each quad, by orientation); the
launches' rates by kind; the minion rail's mean over the train; the anchors' bursts (over_idle_w, ops_per_s, 600 MHz) and random - zeros at
the block's open and close; the samples per launch window.
A block whose block.json status is not ok or partial is set aside with its reason; the rest are reduced.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import bisect
import gzip
import importlib
import json
import os
import statistics as st
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import e183_common as E  # noqa: E402
import e183_stats as S   # noqa: E402

BLOCKS = tuple(range(18310, 18316))


def jl(path):
    if os.path.exists(path + ".gz"):
        return [json.loads(l) for l in gzip.open(path + ".gz", "rt") if l.startswith("{")]
    if os.path.exists(path):
        return [json.loads(l) for l in open(path) if l.startswith("{")]
    return []


def analyzer(root):
    sys.path.insert(0, os.path.join(root, "workloads", "enercat"))
    try:
        return importlib.import_module("analyze_catalogue")
    finally:
        sys.path.pop(0)


def kept_samples(tel):
    """the block's samples after E82 A2's dip rule: (ts, ws) lists"""
    sm = sorted((int(s["t_ms"]), float(s["board_w"])) for s in tel
                if isinstance(s.get("t_ms"), (int, float)) and isinstance(s.get("board_w"), (int, float)))
    k = S.dips_kept(sm)
    return [t for t, _ in k], [w for _, w in k], len(sm) - len(k)


def process_value(L, ori, ts, ws):
    """(why or None, readings, quads, window sample counts) for one process's launch records L"""
    want = E.schedule(ori)
    L = sorted(L, key=lambda r: r.get("launch", -1))
    if len(L) != E.LAUNCHES:
        return f"{len(L)} launches", {}, [], []
    if not all(r.get("ok") for r in L):
        return "a launch record not ok", {}, [], []
    if [r.get("launch") for r in L] != list(range(E.LAUNCHES)):
        return "its launch numbers are not 0-12", {}, [], []
    if [r.get("train_kind") for r in L] != want or any(r.get("abba") != ori or r.get("orientation") != ori for r in L):
        return "a launch's kind or orientation is off the plan's schedule", {}, [], []
    rd, nwin = {}, []
    for r in L:
        v = S.launch_reading(ts, ws, r["t_start_ms"], r["t_end_ms"])
        lo = bisect.bisect_left(ts, r["t_start_ms"] + S.LAG_MS)
        hi = bisect.bisect_right(ts, r["t_end_ms"])
        nwin.append(hi - lo)
        if v is not None:
            rd[r["launch"]] = v
    return None, rd, S.quads_of_process(rd, ori), nwin


def reduce_block(d, ac, root):
    conf = json.load(open(os.path.join(d, "configs.json")))
    bj = json.load(open(os.path.join(d, "block.json"))) if os.path.exists(os.path.join(d, "block.json")) else {}
    tel = jl(os.path.join(d, "telemetry.jsonl"))
    recs = jl(os.path.join(d, "train.jsonl"))
    runs = jl(os.path.join(d, "runs.jsonl"))
    stop = json.load(open(os.path.join(d, "stop.json"))) if os.path.exists(os.path.join(d, "stop.json")) else None
    ts, ws, ndips = kept_samples(tel)
    t = E.train_of_block(conf["pass"])
    byp = {}
    for r in recs:
        byp.setdefault(r["process"], []).append(r)
    procs, info = [], []
    for p in conf["processes"]:
        k, ori = p["process"], p["orientation"]
        why, rd, quads, nwin = process_value(byp.get(k, []), ori, ts, ws)
        if why is None and stop and f"process {k} " in str(stop.get("where", "")):
            why, quads = "a stop fired during it", []
        if why is None and not quads:
            why = "no complete quad (a launch with fewer than 2 window samples)"
        procs.append([ori, quads if why is None else []])
        L = sorted(byp.get(k, []), key=lambda r: r.get("launch", -1))
        carry = []
        if why is None:
            for q in range(3):
                i = 4 * q
                if all(j in rd for j in (i + 2, i + 3)):
                    carry.append(rd[i + 3] - rd[i + 2])
        info.append({"process": k, "orientation": ori, "why_no_value": why, "readings": {str(i): v for i, v in sorted(rd.items())},
                     "quads": quads if why is None else [], "carry_L3_minus_L2": carry, "window_samples": nwin,
                     "rates": {kk: [r["ops_per_s"] for r in L if r.get("train_kind") == kk] for kk in ("F", "S")}})
    # the anchors: the catalogue's own reduction over the block's anchor bursts (E180's)
    anchors = {}
    if len(tel) >= 30 and runs:
        res = ac.bursts_of(tel, runs)
        for b in (res[0] if isinstance(res, tuple) else res):
            anchors[b["cfg"]] = {"over_idle_w": b["over_idle_w"], "ops_per_s": b["ops_per_s"], "mhz_busy_all_600": b["mhz_busy_all_600"],
                                 "die_c_busy": b["die_c_busy"], "launches": b["launches"]}

    def anchor_pair(side):
        z = anchors.get(E.anchor_cfg("fadd.ps/zeros", t["block"], side))
        rr = anchors.get(E.anchor_cfg("fadd.ps/random", t["block"], side))
        if z and rr and z["mhz_busy_all_600"] and rr["mhz_busy_all_600"]:
            return rr["over_idle_w"] - z["over_idle_w"]
        return None

    rail = None
    if recs:
        lo, hi = min(r["t_start_ms"] for r in recs), max(r["t_end_ms"] for r in recs)
        mw = [s["sp"]["minion_w"][0] for s in tel if lo <= s.get("t_ms", 0) <= hi and isinstance(s.get("sp"), dict)
              and isinstance(s["sp"].get("minion_w"), list)]
        rail = st.mean(mw) if mw else None
    return {"block": t["block"], "train": t["train"], "pair": t["pair"], "first": t["first"], "second": t["second"], "dR": t["dR"],
            "dO": t["dO"], "status": bj.get("status"), "processes": procs, "process_info": info,
            "n_processes_planned": len(conf["processes"]), "n_processes_with_value": sum(1 for _, q in procs if q),
            "dips_dropped": ndips, "n_tel": len(tel), "n_launch_records": len(recs), "stop": stop, "anchors": anchors,
            "random_minus_zeros_open_w": anchor_pair("open"), "random_minus_zeros_close_w": anchor_pair("close"),
            "minion_rail_mean_w": rail}


def reduce_all(raw, root):
    ac = analyzer(root)
    out = {"what": "E183's reduction (reduce_e183.py)", "card": E.CARD, "blocks": {}, "set_aside": {}}
    for b in BLOCKS:
        d = os.path.join(raw, "e183", f"p{b}")
        if not os.path.isdir(d):
            continue
        bj = json.load(open(os.path.join(d, "block.json"))) if os.path.exists(os.path.join(d, "block.json")) else {}
        if bj.get("status") not in ("ok", "partial"):
            out["set_aside"][str(b)] = f"block.json status {bj.get('status')!r} ({str(bj.get('note', ''))[:160]})"
            continue
        try:
            out["blocks"][str(b)] = reduce_block(d, ac, root)
        except (OSError, ValueError, KeyError) as e:
            out["set_aside"][str(b)] = f"unreadable: {type(e).__name__}: {e}"
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--root", default=os.path.abspath(os.path.join(HERE, "..", "..", "..")))
    a = ap.parse_args()
    r = reduce_all(a.raw, a.root)
    json.dump(r, open(a.out, "w"), indent=1, sort_keys=True)
    for b, v in sorted(r["blocks"].items()):
        print(f"block {b} {v['train']}: {v['n_processes_with_value']} of {v['n_processes_planned']} processes with a value")
    for b, w in sorted(r["set_aside"].items()):
        print(f"block {b} set aside: {w}")


if __name__ == "__main__":
    main()
