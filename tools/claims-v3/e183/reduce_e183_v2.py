#!/usr/bin/env python3
"""E183's reduction v2 (Q155, the kit's dated note 1, KIT.md.dated-note-1.md; written before any E183 datum). It is reduce_e183.py (v1,
cc597bf2), which stays as committed, with three changes, each answering a fault of the kit's verifier (verify-e183, Sat 7 Nov 2026):

  1. A STOP BLOCK IS REDUCED BY THE PROCESS RULE (the verifier's fault 1). A block whose block.json status is 'stop' (a live stop fired and
     the runner exited 5) is no longer set aside whole. E183.md section 5.1's rule is a process's: "A process during which a stop fired ...
     gives no value". So the process stop.json names gives no value; the processes before it keep theirs; the processes after it never ran,
     have no records and give no value. A stop block without its stop.json is set aside, since the process cannot be named. In v1 such a
     block was set aside with every earlier good process, and its own stop rule was never reached.
  2. THE IMAGE (the verifier's nit 6). A process gives no value when a launch's image is not its kind's. The image is the launch record's
     train_operands, and the test is check_e183.py's own (train_faults): the path ends with the kind's image. This sits beside the kind,
     orientation and number rules. v1 read the kind but not the image, so a process run on a wrong image was used.
  3. THE SESSION'S T0 (the verifier's nit 8). --t0 <the session's T0, epoch seconds> is required. A block whose block.json t0_ms is missing,
     or earlier than T0 x 1000, is set aside as not this session's. lib.sh's block_end writes t0_ms, on the box's own clock, the clock the
     session's T0 is read from (step 9). So a stale block left on the box by an earlier session is never reduced as this session's.

REPORTED beside, never a verdict: the box's post-block check (the block's check.json: its status, note, train faults, train samples off
600 MHz, processes good), copied into the block as box_check, since a stop block's status no longer carries the check's own word.
Everything else is v1's, line for line: the launch reading, the quads, the anchors, the rail, the carry-over, the sets aside for any other
status. Reads committed or collected files only; opens no device.

    /usr/bin/python3 -B tools/claims-v3/e183/reduce_e183_v2.py --raw <collection's raw dir> --t0 <epoch s> --out reduced-e183.json [--root <lab repo>]
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
REDUCED = ("ok", "partial", "stop")          # v2: 'stop' added (change 1)
BOX_CHECK_KEYS = ("status", "note", "processes_planned", "processes_good", "train_faults", "train_samples_off_600")


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


def process_value(L, ori, ts, ws, imgs):
    """(why or None, readings, quads, window sample counts) for one process's launch records L; imgs: {"F": F's image, "S": S's image}"""
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
    if any(not str(r.get("train_operands", "")).endswith(imgs[r["train_kind"]]) for r in L):      # v2 (change 2)
        return "a launch's image is not its kind's", {}, [], []
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
    ck = json.load(open(os.path.join(d, "check.json"))) if os.path.exists(os.path.join(d, "check.json")) else None
    ts, ws, ndips = kept_samples(tel)
    t = E.train_of_block(conf["pass"])
    imgs = {"F": E.image_rel(t["first"]), "S": E.image_rel(t["second"])}
    byp = {}
    for r in recs:
        byp.setdefault(r["process"], []).append(r)
    procs, info = [], []
    for p in conf["processes"]:
        k, ori = p["process"], p["orientation"]
        why, rd, quads, nwin = process_value(byp.get(k, []), ori, ts, ws, imgs)
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
            "minion_rail_mean_w": rail, "t0_ms": bj.get("t0_ms"), "t1_ms": bj.get("t1_ms"),
            "box_check": ({k: ck.get(k) for k in BOX_CHECK_KEYS} if isinstance(ck, dict) else None)}


def reduce_all(raw, root, t0):
    ac = analyzer(root)
    out = {"what": "E183's reduction v2 (reduce_e183_v2.py)", "card": E.CARD, "t0": t0, "blocks": {}, "set_aside": {}}
    for b in BLOCKS:
        d = os.path.join(raw, "e183", f"p{b}")
        if not os.path.isdir(d):
            continue
        bj = json.load(open(os.path.join(d, "block.json"))) if os.path.exists(os.path.join(d, "block.json")) else {}
        if bj.get("status") not in REDUCED:
            out["set_aside"][str(b)] = f"block.json status {bj.get('status')!r} ({str(bj.get('note', ''))[:160]})"
            continue
        tms = bj.get("t0_ms")                                                                 # v2 (change 3)
        if isinstance(tms, bool) or not isinstance(tms, (int, float)):
            out["set_aside"][str(b)] = ("block.json carries no t0_ms (lib.sh's block_end writes one): its time cannot be read against "
                                        f"the session's T0 {t0}")
            continue
        if tms < t0 * 1000:
            out["set_aside"][str(b)] = (f"block.json t0_ms {int(tms)} is before the session's T0 {t0} (epoch s): a block from an earlier "
                                        "session, not this one's")
            continue
        if bj.get("status") == "stop" and not os.path.exists(os.path.join(d, "stop.json")):    # v2 (change 1)
            out["set_aside"][str(b)] = "block.json status 'stop' with no stop.json: the process the stop fired during cannot be named"
            continue
        try:
            out["blocks"][str(b)] = reduce_block(d, ac, root)
        except (OSError, ValueError, KeyError) as e:
            out["set_aside"][str(b)] = f"unreadable: {type(e).__name__}: {e}"
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", required=True)
    ap.add_argument("--t0", required=True, type=int, help="the session's T0 (epoch seconds), as step 9 recorded it")
    ap.add_argument("--out", required=True)
    ap.add_argument("--root", default=os.path.abspath(os.path.join(HERE, "..", "..", "..")))
    a = ap.parse_args()
    r = reduce_all(a.raw, a.root, a.t0)
    json.dump(r, open(a.out, "w"), indent=1, sort_keys=True)
    for b, v in sorted(r["blocks"].items()):
        print(f"block {b} {v['train']}: {v['n_processes_with_value']} of {v['n_processes_planned']} processes with a value"
              + (f" (a stop fired: {str((v['stop'] or {}).get('where', ''))[:80]})" if v["status"] == "stop" else ""))
    for b, w in sorted(r["set_aside"].items()):
        print(f"block {b} set aside: {w}")


if __name__ == "__main__":
    main()
