#!/usr/bin/env python3
"""E98 (Q132): the registered reduction and the scorer. Frozen with the pre-registration, before the first probe.

    python3 reduce_e98.py <DATA> [--out results.json] [--pred predictions.json] > reduce.txt

<DATA> holds P1/ ... P7/ (one run_e98.py session each), queue.jsonl, and history/<box>-<UTC date>.jsonl[.gz], the boxes' own 5 s
records. Times are epoch ms throughout. Standard library plus the lab's reduce_hpl.py and reduce_kspeed.py (unchanged).

PER RUN (block SUS). E64's window: the work samples of the last 40 s, a work sample being one inside a kernel launch. Board W and
die are their means (`reduce_hpl.run_metrics` computes the same two numbers, rounded, and the reducer refuses a disagreement); the
run's line is die - k W with k frozen. An idle-reset dip (the clock falls 800 to 600 MHz with no 700 sample, more than 1.5 s after
its process started and more than 0.3 s before it ended, die under 65 C: E80's A1) is flagged by name and KEPT IN the registered
numbers. The fine W of a run is the mean over its 800 MHz samples with each dip and the 3 s after it left out, and it exists only
if at least 70% of the window remains.

THE HOLD. The same over the last 120 s: die, ioshire, board W, the fine W, the share at 800 MHz, the dips.

THE REST READING, per probe. Primary: aifoundry2's idle board W over the 20 min of its own 5 s history before the probe's REST block
started, leaving out any row within 10 min after a busy one, the die derived as W / 0.2315. Beside it: the raw history die over the
same rows, the 60 s reading (last 60 s of the REST block, 10 Hz), NIC and NVMe over the same rows, and sensors -j. Without 60
history rows the 60 s reading stands in, and the probe says so.

A PROBE COUNTS when no history row within 15 min before its REST block shows a busy card (else it is reported and left out), for the
line when at least 6 of the 8 gated runs have a window, and for the hold when all its planned processes ran and none failed.

THE LINE of a probe: each kind's runs averaged first (fp16 ones has two), then the mean over the kinds, each kind's own mean over the
probes taken out, so that a probe missing a kind is not moved by that kind's level. Run index 0 (from the rest) is not in it.

RULES (predictions.json has the numbers; the probe is the unit; every interval is OLS on n - 2 df at 95%, on the probes that count):
  E98-R0  the rest die's own fall, P-first minus P-last, against the expected 0.44 W (band 0.1-0.9 W). The GATE: fewer than 4 probes,
          or a range of the rest die under 0.75 C, makes every slope rule below UNDER-RESOLVED.
  E98-R1  the 76 s line against the rest die, against 0 and 0.25: SUPPORTS (excludes 0, holds 0.25), INCONCLUSIVE (holds both),
          BELOW_TARGET (holds 0, excludes 0.25), POSITIVE_BELOW_TARGET, ABOVE_TARGET, OPPOSITE.
  E98-R2  the hold's die against the rest die, against the band 1.00-1.25 and 0.25: SUPPORTS (reaches the band, excludes 0.25),
          INCONCLUSIVE (reaches the band and 0.25), BELOW_BAND, ABOVE_BAND.
  E98-S1  the fine line: the mean fine W of fp16 zeros, int8 zeros, int8 neg_ones against rest W, against 0 and 0.60 W/W.
  E98-S2  the hold's fine W against rest W, against the band 1.91-2.39 W/W and 0.60.
  E98-S3  the from-rest run's fine W against rest W, against 0 and 2.14 W/W; and its line against the rest die, against 0.89.
  E98-S4  the trip: fp16 ones' mean clock and board W against the rest die, against 0 and -12 MHz/C, -1 W/C.
  The verdict on the room (E98-V) follows from R1 and R2 as the README says; labelled arms sit beside it: the 60 s rest reading, the raw
  history die, dips left out, unclamped kinds only, each kind alone, by position; and the proxies, a2's NIC and NVMe at rest and the
  other boxes' idle readings, each only when it has rows in at least 4 counted probes.
"""
import argparse
import glob
import gzip
import hashlib
import json
import math
import os
import statistics as st
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(HERE, "..", "..", "hpl"))
import reduce_hpl as R  # noqa: E402
import reduce_kspeed as RK  # noqa: E402

SUS_S, HOLD_S = 40.0, 120.0
RAMP_AFTER_DIP_S = 3.0
GATED_IDX = range(1, 9)
OTHER_BARS = {"a1c0": ("aifoundry1", 0, 22.0), "a1c1": ("aifoundry1", 1, 34.0), "a3c0": ("aifoundry3", 0, 27.0)}


def rnd(x, n=3):
    return None if x is None else round(x, n)


def mean(xs):
    xs = [x for x in xs if x is not None]
    return sum(xs) / len(xs) if xs else None


def ols(xs, ys, t975):
    """(slope, its 95% interval on n - 2 df, se, intercept, rms, n) over the pairs with both values, or None under 3 pairs."""
    pts = [(x, y) for x, y in zip(xs, ys) if x is not None and y is not None]
    n = len(pts)
    if n < 3:
        return None
    mx, my = mean([p[0] for p in pts]), mean([p[1] for p in pts])
    sxx = sum((x - mx) ** 2 for x, _ in pts)
    if sxx <= 0:
        return None
    b = sum((x - mx) * (y - my) for x, y in pts) / sxx
    a = my - b * mx
    res = [y - a - b * x for x, y in pts]
    s2 = sum(r * r for r in res) / (n - 2)
    se = math.sqrt(s2 / sxx)
    tq = t975[str(n - 2)]
    return {"slope": rnd(b, 4), "lo": rnd(b - tq * se, 4), "hi": rnd(b + tq * se, 4), "se": rnd(se, 4), "icpt": rnd(a, 3),
            "rms": rnd(math.sqrt(sum(r * r for r in res) / n), 4), "n": n, "df": n - 2, "x_range": rnd(max(p[0] for p in pts) - min(p[0] for p in pts), 3)}


# ------------------------------------------------------------------------------------------------- the verdicts
def verdict_target(f, target):
    """Against 0 and a target of either sign. f is ols()'s record."""
    if f is None:
        return "NOT_SCORED"
    lo, hi = (f["lo"], f["hi"]) if target > 0 else (-f["hi"], -f["lo"])
    t = abs(target)
    if hi < 0:
        return "OPPOSITE"
    if lo > t:
        return "ABOVE_TARGET"
    if hi < t:
        return "POSITIVE_BELOW_TARGET" if lo > 0 else "BELOW_TARGET"
    return "SUPPORTS" if lo > 0 else "INCONCLUSIVE"


def verdict_band(f, band, floor):
    if f is None:
        return "NOT_SCORED"
    if f["lo"] > band[1]:
        return "ABOVE_BAND"
    if f["hi"] < band[0]:
        return "BELOW_BAND"
    return "SUPPORTS" if f["lo"] > floor else "INCONCLUSIVE"


def verdict_room(r1, r2):
    """E98-V. The room's reading: the hold follows the rest die about 1:1, and the 76 s line follows it at the desk's rate."""
    if "UNDER-RESOLVED" in (r1, r2) or "NOT_SCORED" in (r1, r2):
        return "UNDER-RESOLVED"
    if r2 in ("BELOW_BAND", "ABOVE_BAND") or r1 in ("OPPOSITE", "BELOW_TARGET"):
        return "REFUTED"
    if r2 == "SUPPORTS" and r1 == "SUPPORTS":
        return "SUPPORTED"
    if r2 == "SUPPORTS":
        return "PARTLY"
    return "INCONCLUSIVE"


# ------------------------------------------------------------------------------------------------- the readings
def tel_rows(path):
    out = []
    for d in R.jl(path):
        try:
            t = d.get("temp_c", {})
            ms = t.get("minshire") or [None]
            io = t.get("ioshire") or [None]
            out.append({"t": int(d["t_ms"]), "die": ms[0], "io": io[0], "w": d.get("board_w"), "mhz": d.get("mhz", {}).get("minion")})
        except (KeyError, TypeError, ValueError, AttributeError):
            pass
    out.sort(key=lambda r: r["t"])
    return out


def work_spans(procs):
    return [(p["t_start_ms"], p["t_end_ms"]) for p in procs if p.get("role") == "work"]


def kernel_spans(procs):
    ks = [(k["t_start_ms"], k["t_end_ms"]) for p in procs if p.get("role") == "work" for k in p.get("sparsity", [])
          if k.get("t_start_ms") and k.get("t_end_ms")]
    return ks or work_spans(procs)


def find_dips(samples, spans):
    """E80's A1, DIP: a work sample at 600 MHz straight after one at 800, inside a process. Each with its samples named."""
    eps = []
    for a, b in spans:
        idx = [i for i, s in enumerate(samples) if a <= s["t"] <= b]
        k = 1
        while k < len(idx):
            s, p = samples[idx[k]], samples[idx[k - 1]]
            if s["mhz"] == 600 and p["mhz"] == 800 and s["t"] - a > 1500 and b - s["t"] > 300 and (s["die"] is None or s["die"] < 65):
                j = k
                while j < len(idx) and samples[idx[j]]["mhz"] != 800:
                    j += 1
                eps.append({"t0": s["t"], "t1": samples[idx[j - 1]]["t"], "samples": j - k, "w_before": p["w"], "w_in": s["w"], "die": s["die"]})
                k = j
            k += 1
    return eps


def window(samples, procs, last_s):
    """The registered window: work samples in the last last_s seconds of the work; and what is left for the fine W."""
    spans, kw = work_spans(procs), kernel_spans(procs)
    if not spans:
        return None
    t1 = max(b for _, b in spans)
    tl = t1 - last_s * 1000
    ws = [s for s in samples if any(a <= s["t"] <= b for a, b in kw)]
    last = [s for s in ws if s["t"] >= tl]
    if not last:
        return None
    dips = find_dips(ws, spans)
    in_win = [d for d in dips if d["t1"] >= tl]
    def dipped(t):
        return any(d["t0"] <= t <= d["t1"] + RAMP_AFTER_DIP_S * 1000 for d in dips)
    fine = [s["w"] for s in last if s["mhz"] == 800 and s["w"] is not None and not dipped(s["t"])]
    nodip = [s for s in last if not dipped(s["t"])]
    out = {"n": len(last), "w": mean([s["w"] for s in last]), "die": mean([s["die"] for s in last]), "io": mean([s["io"] for s in last]),
           "mhz": mean([s["mhz"] for s in last]), "share_800": sum(1 for s in last if s["mhz"] == 800) / len(last),
           "dips": [{"t_from_end_s": round((t1 - d["t0"]) / 1000.0, 1), **{k: d[k] for k in ("samples", "w_before", "w_in", "die")}} for d in in_win],
           "dips_in_work": len(dips),
           "fine_w": mean(fine) if len(fine) >= 0.7 * len(last) else None, "fine_share": len(fine) / len(last),
           "w_nodip": mean([s["w"] for s in nodip]), "die_nodip": mean([s["die"] for s in nodip]),
           "die_values": {str(v): sum(1 for s in last if s["die"] == v) for v in sorted({s["die"] for s in last if s["die"] is not None})}}
    return out


def hold_calibration(samples, procs):
    """W at 800 MHz against the die reading inside the hold, after its first 60 s, dips left out: E64's 0.442 W/C checked in place."""
    spans, kw = work_spans(procs), kernel_spans(procs)
    if not spans:
        return None
    t0 = min(a for a, _ in spans)
    ws = [s for s in samples if any(a <= s["t"] <= b for a, b in kw)]
    dips = find_dips(ws, spans)
    use = [s for s in ws if s["t"] >= t0 + 60000 and s["mhz"] == 800 and s["w"] is not None and s["die"] is not None
           and not any(d["t0"] <= s["t"] <= d["t1"] + RAMP_AFTER_DIP_S * 1000 for d in dips)]
    if len(use) < 100 or len({s["die"] for s in use}) < 2:
        return None
    mx, my = mean([s["die"] for s in use]), mean([s["w"] for s in use])
    sxx = sum((s["die"] - mx) ** 2 for s in use)
    return {"w_per_c": rnd(sum((s["die"] - mx) * (s["w"] - my) for s in use) / sxx, 3), "n": len(use), "die_span": [min(s["die"] for s in use), max(s["die"] for s in use)]}


class History:
    def __init__(self, data):
        self.rows = {}
        for b in ("aifoundry1", "aifoundry2", "aifoundry3"):
            rows = []
            for p in sorted(glob.glob(os.path.join(data, "history", f"{b}-*.jsonl*"))):
                op = gzip.open if p.endswith(".gz") else open
                for ln in op(p, "rt"):
                    try:
                        r = json.loads(ln)
                    except ValueError:
                        continue
                    if "t" in r:
                        rows.append(r)
            rows.sort(key=lambda r: r["t"])
            self.rows[b] = rows

    def window(self, box, a, b):
        return [r for r in self.rows.get(box, []) if a <= r["t"] < b]


def busy_times(rows):
    """The busy rows' times: a die over 55 C, a board reading over 26 W, or the card held on two rows running (a launch session holds it
    for many rows; the 1-2 s of a config read or a lock probe can show on one)."""
    out = []
    for i, r in enumerate(rows):
        c = (r.get("cards") or [{}])[0]
        hot = (c.get("w") is not None and c["w"] > 26.0) or (c.get("die") is not None and c["die"] > 55)
        held = bool(c.get("held"))
        adj = any(0 <= j < len(rows) and ((rows[j].get("cards") or [{}])[0]).get("held") for j in (i - 1, i + 1))
        if hot or (held and adj):
            out.append(r["t"])
    return out


def rest_reading(H, t_end, gates):
    """The 20 min of history before t_end (the moment the queue began the probe's snapshot, before anything of the probe touched the card).
    Returns the reading; a row within 10 min after a busy row is left out; no row with the card held is used."""
    a = t_end - gates["rest_history_window_min"] * 60000
    look = H.window("aifoundry2", t_end - 40 * 60000, t_end)
    busy = busy_times(look)
    last_busy = max(busy) if busy else None
    skip_to = (last_busy + gates["rest_skip_after_busy_min"] * 60000) if last_busy else 0
    rows = [r for r in look if r["t"] >= a and r["t"] >= skip_to and not ((r.get("cards") or [{}])[0]).get("held")]
    c = [(r.get("cards") or [{}])[0] for r in rows]
    W = [x.get("w") for x in c if x.get("w") is not None]
    out = {"rows": len(W), "w": mean(W), "die": mean([x.get("die") for x in c]), "nic": mean([(r.get("temps") or {}).get("nic") for r in rows]),
           "nvme": mean([(r.get("temps") or {}).get("nvme") for r in rows]), "cpu": mean([(r.get("temps") or {}).get("cpu") for r in rows]),
           "load": mean([r.get("load") for r in rows]), "window_end_ms": t_end,
           "since_busy_min": round((t_end - last_busy) / 60000.0, 1) if last_busy else None,
           "busy_within_rest": bool(last_busy and t_end - last_busy < gates["rest_min"] * 60000),
           "w_sd": rnd(st.pstdev(W), 3) if len(W) > 1 else None}
    return out, rows


def other_box_proxies(H, a, b):
    """The other boxes' idle readings over [a, b): a box's row counts only with its card not held, a die, W under the card's idle bar,
    and load under 2; on aifoundry1 either card held blanks both. A proxy with under 60 rows is left empty."""
    out = {}
    for name, (box, n, bar) in OTHER_BARS.items():
        rows = H.window(box, a, b)
        die, w, nic, nvme = [], [], [], []
        for r in rows:
            cards = {c.get("n"): c for c in (r.get("cards") or [])}
            c = cards.get(n)
            if not c or c.get("die") is None or c.get("w") is None or (r.get("load") or 0) > 2:
                continue
            if box == "aifoundry1" and any(x.get("held") for x in cards.values()):
                continue
            if c.get("held") or c["w"] > bar:
                continue
            die.append(c["die"]); w.append(c["w"])
            T = r.get("temps") or {}
            nic.append(T.get("nic")); nvme.append(T.get("nvme"))
        if len(w) >= 60:
            out[name + "-die"], out[name + "-w"] = mean(die), mean(w)
            tag = box.replace("aifoundry", "a")
            out[tag + "-nic"], out[tag + "-nvme"] = mean(nic), mean(nvme)
    return out


def kind_of(values):
    return RK.kind_of(values)


# ------------------------------------------------------------------------------------------------- one probe
def read_probe(pdir, name, H, P, qrec):
    gates = P["gates"]
    k = P["constants"]["k_line_c_per_w"]
    sess, runs, launches, q0 = R.load_session(pdir)
    byrun = {}
    for L in launches:
        byrun.setdefault(L["run"], []).append(L)
    evs = R.sp_events_by_run(pdir, sess, runs, q0)
    fit = R.fit_clock(evs, launches, sess)
    out = {"probe": name, "dry": bool(sess.get("dry")), "runs": {}, "gates": {}, "config_reads": [], "binaries": sess.get("sha256"), "git_head": sess.get("git_head")}
    rest = next((r for r in runs if r["block"] == "REST"), None)
    if rest is None:
        out["no_rest_block"] = True
        return out
    rs = tel_rows(os.path.join(pdir, rest["tel"]))
    t_rest = rs[0]["t"] if rs else rest["t_first_ms"]
    t_end = rs[-1]["t"] if rs else rest["t_last_ms"]
    last60 = [s for s in rs if s["t"] >= t_end - 60000]
    out["t_rest_ms"] = t_rest
    out["rest60"] = {"w": rnd(mean([s["w"] for s in last60]), 4), "die": rnd(mean([s["die"] for s in last60]), 3), "io": rnd(mean([s["io"] for s in last60]), 3),
                     "n": len(last60), "w_sd": rnd(st.pstdev([s["w"] for s in last60 if s["w"] is not None]), 3) if len(last60) > 1 else None}
    try:
        t_snap = json.load(open(os.path.join(pdir, "snapshot-start.json")))["t_ms"]
    except (OSError, ValueError, KeyError):
        t_snap = t_rest - 60000
    hist, rows = rest_reading(H, t_snap, gates)
    out["rest20"] = {k2: (rnd(v, 4) if isinstance(v, float) else v) for k2, v in hist.items()}
    out["others"] = {k2: rnd(v, 3) for k2, v in other_box_proxies(H, t_snap - gates["rest_history_window_min"] * 60000, t_snap).items()}
    w_x = hist["w"] if hist["rows"] >= gates["rest_min_rows"] else out["rest60"]["w"]
    out["rest_source"] = "history 20 min" if hist["rows"] >= gates["rest_min_rows"] else "60 s reading (too few history rows)"
    out["rest_w"] = rnd(w_x, 4)
    out["rest_die_w_derived"] = rnd(w_x / P["constants"]["rest_w_per_c"], 3) if w_x is not None else None
    out["rest_ok"] = not hist["busy_within_rest"]
    for r in runs:
        cfg = (r.get("queries") or {}).get("config") or {}
        out["config_reads"].append([cfg.get("tdp_w"), cfg.get("temp_threshold_c")])
        if r["block"] not in ("SUS", "HOLD"):
            continue
        procs = byrun.get(r["run"], [])
        rc_bad = sum(1 for p in procs if p.get("role") == "work" and p.get("rc") != 0)
        s = tel_rows(os.path.join(pdir, r["tel"]))
        if r["block"] == "SUS":
            win = window(s, procs, SUS_S)
            if win is None:
                continue
            m = R.run_metrics(pdir, r, procs, evs.get(r["run"]), fit)
            if (rnd(win["w"], 2) != m.get("sus_w_mean") and abs(win["w"] - (m.get("sus_w_mean") or 0)) > 0.0051) or \
                    abs(win["die"] - (m.get("sus_die_mean") or 0)) > 0.051:
                raise SystemExit(f"{name} {r['run']}: window disagrees with run_metrics: {win['w']} {win['die']} {m.get('sus_w_mean')} {m.get('sus_die_mean')}")
            rec = {"run": r["run"], "idx": r["idx"], "kind": kind_of(r["values"]), "limit": RK.sus_limit(m), "rc_bad": rc_bad, "t0_ms": r["t_first_ms"],
                   "gate": {"held_s": r["gate"].get("held_s"), "reached": r["gate"].get("reached"), "die": (r["gate"].get("reading") or [None])[0]}}
        else:
            win = window(s, procs, HOLD_S)
            if win is None:
                continue
            rec = {"run": r["run"], "idx": r["idx"], "kind": kind_of(r["values"]), "rc_bad": rc_bad, "t0_ms": r["t_first_ms"], "processes": len(procs), "processes_planned": r.get("processes"),
                   "gate": {"held_s": r["gate"].get("held_s"), "reached": r["gate"].get("reached"), "die": (r["gate"].get("reading") or [None])[0]},
                   "calibration": hold_calibration(s, procs)}
        rec.update({k2: (rnd(v, 4) if isinstance(v, float) else v) for k2, v in win.items()})
        rec["line"] = rnd(win["die"] - k * win["w"], 4)
        rec["line_nodip"] = rnd(win["die_nodip"] - k * win["w_nodip"], 4) if win["die_nodip"] is not None and win["w_nodip"] is not None else None
        if r["block"] == "SUS":
            out["runs"][r["idx"]] = rec
        else:
            out["hold"] = rec
    return out


def probe_line(probes, field, idxs, P):
    """Per kind first, then each kind's mean over the probes out: the kinds' levels do not move a probe that misses one."""
    per = {}
    for pr in probes:
        kinds = {}
        for i in idxs:
            r = pr["runs"].get(i)
            if r is not None and r.get(field) is not None:
                kinds.setdefault(r["kind"], []).append(r[field])
        per[pr["probe"]] = {k: mean(v) for k, v in kinds.items()}
    allk = sorted({k for v in per.values() for k in v})
    centre = {k: mean([per[p].get(k) for p in per]) for k in allk}
    out = {}
    for p, kv in per.items():
        out[p] = mean([v - centre[k] for k, v in kv.items()]) if kv else None
    level = mean(list(centre.values())) if centre else 0.0
    return {p: (v + level if v is not None else None) for p, v in out.items()}, per


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("data")
    ap.add_argument("--out")
    ap.add_argument("--pred", default=os.path.join(HERE, "predictions.json"))
    a = ap.parse_args()
    P = json.load(open(a.pred))
    T = P["t975"]
    G, TG, C = P["gates"], P["targets"], P["constants"]
    H = History(a.data)
    qrecs = R.jl(os.path.join(a.data, "queue.jsonl"))
    probes = []
    for pdir in sorted(glob.glob(os.path.join(a.data, "P[0-9]*"))):
        name = os.path.basename(pdir)
        if not os.path.exists(os.path.join(pdir, "runs.jsonl")):
            continue
        qr = [q for q in qrecs if q.get("probe") == name]
        pr = read_probe(pdir, name, H, P, qr)
        pr["queue"] = qr
        probes.append(pr)
    # which probes count
    cnt = [p for p in probes if p.get("rest_ok") and p.get("rest_die_w_derived") is not None]
    cnt_line = [p for p in cnt if sum(1 for i in GATED_IDX if i in p["runs"]) >= G["min_gated_runs_per_probe"]]
    cnt_hold = [p for p in cnt if p.get("hold") and not p["hold"].get("rc_bad") and p["hold"].get("processes") == p["hold"].get("processes_planned")]
    line, line_kinds = probe_line(cnt_line, "line", GATED_IDX, P)
    line_nd, _ = probe_line(cnt_line, "line_nodip", GATED_IDX, P)
    un = [i for i in GATED_IDX if cnt_line and cnt_line[0]["runs"].get(i, {}).get("kind") in ("fp16/zeros", "int8/zeros", "int8/neg_ones", "int8/sparse50")]
    line_un, _ = probe_line(cnt_line, "line", un or [1, 2, 3, 4], P)
    fine_i = [1, 2, 3]
    fine, _ = probe_line(cnt_line, "fine_w", fine_i, P)
    px = {p["probe"]: p["rest_die_w_derived"] for p in cnt}
    pw = {p["probe"]: p["rest_w"] for p in cnt}
    p60 = {p["probe"]: (p["rest60"]["w"] / C["rest_w_per_c"] if p["rest60"]["w"] is not None else None) for p in cnt}
    p60w = {p["probe"]: p["rest60"]["w"] for p in cnt}
    phd = {p["probe"]: p["rest20"].get("die") for p in cnt}
    names_line = [p["probe"] for p in cnt_line]
    names_hold = [p["probe"] for p in cnt_hold]

    def fit(xmap, ymap, names):
        return ols([xmap.get(n) for n in names], [ymap.get(n) for n in names], T)

    res = {"experiment": "E98", "n_probes_run": len(probes), "probes_counted": [p["probe"] for p in cnt], "probes_line": names_line, "probes_hold": names_hold,
           "predictions_sha256": hashlib.sha256(open(a.pred, "rb").read()).hexdigest()}
    res["binaries_same_in_every_probe"] = len({json.dumps(p.get("binaries"), sort_keys=True) for p in probes}) <= 1
    # R0
    xs = [p["rest_die_w_derived"] for p in cnt]
    ws = [p["rest_w"] for p in cnt]
    rng = max(xs) - min(xs) if len(xs) >= 2 else 0.0
    fall_w = (ws[0] - ws[-1]) if len(ws) >= 2 else None
    band = P["expected_fall"]["band_w"]
    res["R0"] = {"fall_w": rnd(fall_w, 3), "fall_c_w_derived": rnd(fall_w / C["rest_w_per_c"], 3) if fall_w is not None else None, "range_c": rnd(rng, 3),
                 "expected_w": P["expected_fall"]["w"], "band_w": band,
                 "against_expected": ("NOT_SCORED" if fall_w is None else ("INSIDE_BAND" if band[0] <= fall_w <= band[1] else ("BELOW_BAND" if fall_w < band[0] else "ABOVE_BAND"))),
                 "gate": "OK" if (len(cnt) >= G["min_probes"] and rng >= G["min_rest_range_c"]) else "UNDER-RESOLVED"}
    gated = res["R0"]["gate"] != "OK"

    def scored(v):
        return "UNDER-RESOLVED" if gated else v

    # R1
    f1 = fit(px, line, names_line)
    res["R1"] = {"fit": f1, "verdict": scored(verdict_target(f1, TG["line_slope"])), "target": TG["line_slope"], "per_probe": {k: rnd(v, 3) for k, v in line.items()},
                 "kinds": {p: {k: rnd(v, 3) for k, v in kv.items()} for p, kv in line_kinds.items()}}
    # R2
    hold_die = {p["probe"]: p["hold"]["die"] for p in cnt_hold}
    hold_w = {p["probe"]: p["hold"].get("fine_w") for p in cnt_hold}
    hold_io = {p["probe"]: p["hold"].get("io") for p in cnt_hold}
    f2 = fit(px, hold_die, names_hold)
    res["R2"] = {"fit": f2, "verdict": scored(verdict_band(f2, TG["hold_band"], TG["hold_floor"])), "band": TG["hold_band"], "floor": TG["hold_floor"],
                 "per_probe": {k: rnd(v, 3) for k, v in hold_die.items()}, "path_slope": TG["hold_slope_path"]}
    res["V"] = verdict_room(res["R1"]["verdict"], res["R2"]["verdict"])
    # S1, S2
    f_s1 = fit(pw, fine, names_line)
    res["S1"] = {"fit": f_s1, "verdict": scored(verdict_target(f_s1, TG["fine_line_w_per_w_desk"])), "target": TG["fine_line_w_per_w_desk"], "per_probe": {k: rnd(v, 3) for k, v in fine.items()}}
    f_s2 = fit(pw, hold_w, names_hold)
    res["S2"] = {"fit": f_s2, "verdict": scored(verdict_band(f_s2, TG["hold_w_band"], TG["hold_w_per_w_if_line_slope"])), "band": TG["hold_w_band"],
                 "per_probe": {k: rnd(v, 3) for k, v in hold_w.items()}, "path": TG["hold_w_per_w_path"]}
    # S3, from the rest
    fr_w = {p["probe"]: p["runs"].get(0, {}).get("fine_w") for p in cnt}
    fr_l = {p["probe"]: p["runs"].get(0, {}).get("line") for p in cnt}
    nm = [p["probe"] for p in cnt]
    f3w, f3l = fit(pw, fr_w, nm), fit(px, fr_l, nm)
    res["S3"] = {"fit_w": f3w, "verdict_w": scored(verdict_target(f3w, TG["from_rest_w_per_w_room"])), "target_w": TG["from_rest_w_per_w_room"],
                 "fit_line": f3l, "verdict_line": scored(verdict_target(f3l, TG["from_rest_line_slope"])), "target_line": TG["from_rest_line_slope"],
                 "per_probe": {k: {"fine_w": rnd(fr_w[k], 3), "line": rnd(fr_l[k], 3)} for k in nm}}
    # S4, the trip
    trip = {p["probe"]: mean([p["runs"][i]["mhz"] for i in (5, 8) if i in p["runs"]]) for p in cnt}
    tripw = {p["probe"]: mean([p["runs"][i]["w"] for i in (5, 8) if i in p["runs"]]) for p in cnt}
    f4m, f4w = fit(px, trip, nm), fit(px, tripw, nm)
    res["S4"] = {"fit_mhz": f4m, "verdict_mhz": scored(verdict_target(f4m, TG["trip_mhz_per_c"])), "target_mhz": TG["trip_mhz_per_c"], "fit_w": f4w,
                 "verdict_w": scored(verdict_target(f4w, TG["trip_w_per_c"])), "target_w": TG["trip_w_per_c"],
                 "per_probe": {k: {"mhz": rnd(trip[k], 1), "w": rnd(tripw[k], 2)} for k in nm}}
    # labelled arms, beside the rules
    arms = {
        "R1_on_60s_rest": fit(p60, line, names_line),
        "R1_on_history_die": fit(phd, line, names_line),
        "R1_dips_left_out": fit(px, line_nd, names_line),
        "R1_unclamped_only": fit(px, line_un, names_line),
        "R2_on_60s_rest": fit(p60, hold_die, names_hold),
        "R2_on_history_die": fit(phd, hold_die, names_hold),
        "R2_ioshire": fit(px, hold_io, names_hold),
        "S1_on_60s_rest": fit(p60w, fine, names_line),
        "S2_on_60s_rest": fit(p60w, hold_w, names_hold),
    }
    by_idx = {}
    for i in GATED_IDX:
        ym = {p["probe"]: p["runs"].get(i, {}).get("line") for p in cnt_line}
        kind = next((p["runs"][i]["kind"] for p in cnt_line if i in p["runs"]), None)
        by_idx[f"{i}:{kind}"] = fit(px, ym, names_line)
    arms["R1_by_position"] = by_idx
    res["arms"] = arms
    # proxies, each beside: the line and the hold against it, and it against the rest die
    prox = {}
    a2p = {"a2-nic": {p["probe"]: p["rest20"].get("nic") for p in cnt}, "a2-nvme": {p["probe"]: p["rest20"].get("nvme") for p in cnt}}
    names_other = sorted({k for p in cnt for k in p.get("others", {})})
    for k in names_other:
        a2p[k] = {p["probe"]: p.get("others", {}).get(k) for p in cnt}
    for k, m in a2p.items():
        have = [p["probe"] for p in cnt if m.get(p["probe"]) is not None]
        if len(have) < G["min_probes"]:
            prox[k] = {"n": len(have), "note": "too few counted probes with rows"}
            continue
        prox[k] = {"n": len(have), "line_on_it": fit(m, line, names_line), "hold_on_it": fit(m, hold_die, names_hold), "it_on_rest_die": fit(px, m, nm), "values": {p: rnd(m[p], 3) for p in have}}
    res["proxies"] = prox
    res["probes"] = probes
    # a board-data free, flat print
    print("E98: the heat path's drift against the room, one night on aifoundry2, under its own governor")
    print(f"probes run {len(probes)}, counted {len(cnt)}, for the line {len(names_line)}, for the hold {len(names_hold)}")
    print("\nprobe  rest t          rest W (20 min)  rows  die-from-W  raw die  60 s W   60 s die  nic    nvme    since busy  line    hold die hold W(fine) hold MHz dips(hold) config")
    for p in probes:
        ho = p.get("hold") or {}
        print(f"{p['probe']:5s} {p.get('t_rest_ms')}  {p.get('rest_w')}  {p['rest20'].get('rows')}  {p.get('rest_die_w_derived')}  {p['rest20'].get('die')}  {p['rest60'].get('w')}  {p['rest60'].get('die')}  "
              f"{p['rest20'].get('nic')}  {p['rest20'].get('nvme')}  {p['rest20'].get('since_busy_min')}  {rnd(line.get(p['probe']), 3)}  {ho.get('die')}  {ho.get('fine_w')}  {ho.get('mhz')}  {len(ho.get('dips', []))}  {sorted({tuple(c) for c in p.get('config_reads', [])})}"
              + ("" if p.get("rest_ok") else "  REST NOT MET: left out"))
    print("\nper run: probe idx kind W die line MHz share800 fineW dips gate(held,die) limit")
    for p in probes:
        for i in sorted(p["runs"]):
            r = p["runs"][i]
            print(f"{p['probe']} {i} {r['kind']:14s} {r['w']:.2f} {r['die']:.2f} {r['line']:.2f} {r['mhz']:.0f} {r['share_800']:.3f} {r.get('fine_w')} d{len(r['dips'])} {r['gate']['held_s']},{r['gate']['die']} {r.get('limit')}")
    print("\nbinaries the same in every probe (session.json sha256):", res["binaries_same_in_every_probe"])
    print("\nRULES")
    print("R0 rest die's fall", json.dumps(res["R0"]))
    print("R1 line on rest die", res["R1"]["verdict"], json.dumps(f1))
    print("R2 hold die on rest die", res["R2"]["verdict"], json.dumps(f2))
    print("V  the room's reading:", res["V"])
    print("S1 fine line on rest W", res["S1"]["verdict"], json.dumps(f_s1))
    print("S2 hold fine W on rest W", res["S2"]["verdict"], json.dumps(f_s2))
    print("S3 from rest: W", res["S3"]["verdict_w"], json.dumps(f3w), "line", res["S3"]["verdict_line"], json.dumps(f3l))
    print("S4 trip: MHz", res["S4"]["verdict_mhz"], json.dumps(f4m), "W", res["S4"]["verdict_w"], json.dumps(f4w))
    print("\nARMS (labelled, never a verdict)")
    for k, v in arms.items():
        print(k, json.dumps(v))
    print("\nPROXIES (labelled)")
    for k, v in prox.items():
        print(k, json.dumps(v))
    if a.out:
        json.dump(res, open(a.out, "w"), indent=1, sort_keys=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
