#!/usr/bin/env python3
"""PCIE2 (hub rungs 34 and 35): the pre-registered reduction. PREREG.md states the same predictions and rules in prose;
`--print-predictions` prints the table this code judges, for comparing the two before the freeze.

    reduce.py --check-pass <pass dir>                 one pass's integrity (block.sh writes check.json with it)
    reduce.py --data <root> --out pcie2.json --md results.md [--dev] [--allow-dry]
                                                      every card under <root>: per-pass values, card means with 99%
                                                      intervals, the predictions' verdicts, the theories' fates
    reduce.py --self-test                             the whole chain on the DRY stub's four model pairs
    reduce.py --print-predictions

<root> holds <card>/pcie2/p<pass>/ (build/claims-v3, or a collected raw/) or <card>/p<pass>/. Passes 1-99 are the
validation passes, 100-899 development, 900+ smokes: verdicts come from validation passes (--dev judges the development
passes instead, for the development summary; smokes are never judged). A pass whose block.json is not ok, or whose
check fails, is left out and listed; so is a validation pass that did not run frozen (pass.json "frozen" true) on this
PREREG.md (its "prereg_sha256" equal to PREREG.sha256 beside this file), and any V3_DRY pass (unless --allow-dry).

The unit of replication is the pass. A pass's value of a quantity:
  R35 (conc): per process (MB per command, elements), a configuration's aggregate rate is the median over the process's
    trials of legs x bytes_per_leg / wall_ns; a ratio is the ratio of two such medians from the same process. The
    rate ratio rr: per configuration (h2d, h2d/ser; plain call), a least-squares line wall = a + bytes / R through the
    median wall times at 1, 4, 16 and 64 MB (at least three sizes); rr = R(h2d) / R(h2d/ser). Fixed costs, whether they
    overlap or not, go to the intercepts a, so rr is the rate the overlap leaves; icpt_gap_ms = a(h2d) - a(h2d/ser).
  R34 (touch): per repetition, each timed line has two references from the same repetition, its first-touch cycles in
    dram_ref (after a flush launch: DRAM) and in l3_ref (next: the L3); a line whose references differ by less than
    40 cycles is ambiguous and left out (their share is reported). A line of another arm is L3-like when its cycles are
    closer to its l3_ref value than to its dram_ref value. The pass's fraction is the mean over repetitions of the
    fraction of lines that are L3-like; a repetition in which fewer than half its lines are kept (not ambiguous) is
    left out of the fractions (the instrument did not separate DRAM from L3 in it), and counted. Latency medians pool
    every line of every repetition. The latency quantities (P34-1..4, absolute cycle counts) are taken only from passes
    in which every telemetry sample read the minion clock at 600 MHz; the fractions do not depend on the clock.
A card's value is the mean of its passes' values with a 99% t-interval (n passes, t at 0.995, n - 1 df); n = 1 gives
the point value. PASS: the interval lies inside the predicted range (ge / le: on the predicted side of the bound);
FAIL: it lies wholly outside; otherwise INCONCLUSIVE. A count predicted zero passes only if it is zero in every pass.
A theory is refuted on a card when any of its conditions FAILs, survives when all PASS, and is open otherwise.
The R34 theories (T34-*) are judged only when the instrument's own controls all PASS on that card (P34-1, P34-2, P34-3,
P34-5, P34-6: the flush launch empties the L3, the L3 keeps what a kernel read, the two references are apart, few
lines ambiguous); otherwise every T34 theory is "invalid" on that card, whatever its conditions say.
"""
import argparse
import glob
import hashlib
import json
import os
import shutil
import statistics as st
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
_T995 = [63.657, 9.925, 5.841, 4.604, 4.032, 3.707, 3.499, 3.355, 3.250, 3.169]
AMBIG = 40          # cycles: a line whose two references differ by less is left out of the R34 fractions
GLITCH = 1 << 31    # a first-touch interval at or above this is a wrapped u32 (the counter's carry glitch)


def tq(df):
    return _T995[df - 1] if 1 <= df <= len(_T995) else 2.576


# ---- predictions and theories --------------------------------------------------------------------------------------
# (id, quantity, kind, a, b, what). kind: range [a, b]; ge a; le a; zero.
PRED = [
    ("P35-1", "h64", "range", 0.44, 0.54, "two H2D commands in flight / one, 2 x 64 MB (D19: 0.49)"),
    ("P35-2", "h16", "range", 0.44, 0.62, "the same, 2 x 16 MB"),
    ("P35-3", "h4", "range", 0.50, 0.80, "the same, 2 x 4 MB"),
    ("P35-4", "h1", "range", 0.55, 1.15, "the same, 2 x 1 MB (not a T35-B/C condition: fixed costs dominate)"),
    ("P35-5a", "d1", "ge", 0.95, None, "two D2H commands in flight / one, 2 x 1 MB"),
    ("P35-5b", "d4", "ge", 0.95, None, "the same, 2 x 4 MB"),
    ("P35-5c", "d16", "ge", 0.95, None, "the same, 2 x 16 MB"),
    ("P35-5d", "d64", "range", 1.00, 1.20, "the same, 2 x 64 MB (27 Sep: 1.08-1.11)"),
    ("P35-6", "s2", "range", 0.44, 0.60, "two streams, one H2D command of each in flight / one in flight, 64 MB"),
    ("P35-7", "e1", "range", 0.93, 1.07, "one H2D command in flight: 8 elements / 1 element (a list), 64 MB"),
    ("P35-8", "e2", "range", 0.44, 0.56, "two H2D in flight / one, 64 MB, 8 elements per command"),
    ("P35-9", "lc", "range", 0.95, 1.05, "one H2D in flight: a 1-element list / the plain call, 64 MB"),
    ("P35-10", "rr", "range", 0.44, 0.54, "rate ratio R(h2d)/R(h2d/ser): slopes of wall = a + bytes/R, 1-64 MB"),
    ("P34-1", "dref", "range", 250, 380, "first touch after a flush launch (dram_ref), median cycles"),
    ("P34-2", "lref", "range", 135, 195, "first touch of lines the L3 holds (l3_ref), median cycles"),
    ("P34-3", "gap", "range", 80, 220, "dram_ref minus l3_ref, per line, median cycles"),
    ("P34-4", "l2", "range", 35, 65, "second touch (an L2 hit), median cycles"),
    ("P34-5", "amb", "le", 0.05, None, "share of lines whose two references differ by < 40 cycles"),
    ("P34-6", "fr", "ge", 0.90, None, "l3_ref2 (control): share of lines L3-like"),
    ("P34-7", "fw", "ge", 0.90, None, "h2d_warm: share of lines L3-like (T34-A)"),
    ("P34-8", "fc", "ge", 0.90, None, "h2d_cold: share of lines L3-like (T34-A)"),
    ("P34-9", "bad", "zero", None, None, "first-touch values not equal to the last pattern written, all arms"),
]
# theory -> [(quantity, kind, a, b)]; the conditions each theory predicts
THEORY = {
    "T35-A": ("a fixed cost per overlapping command (the lost time does not grow with size)",
              [("h1", "le", 0.20, None), ("h4", "le", 0.35, None), ("h64", "range", 0.44, 0.54),
               ("rr", "ge", 0.85, None)]),
    "T35-BC": ("a rate that halves while two H2D commands overlap, whichever streams: a shared DMA read engine (B) or "
               "the IOMMU (C); this experiment cannot separate B from C (iommu=pt would)",
               [("rr", "range", 0.44, 0.54), ("h64", "range", 0.44, 0.54), ("h16", "range", 0.44, 0.62),
                ("h4", "range", 0.50, 0.80), ("s2", "range", 0.44, 0.60), ("e1", "range", 0.93, 1.07),
                ("e2", "range", 0.44, 0.56)]),
    "T35-E": ("a loss that sets in only after a long overlap (a queue that fills)",
              [("h1", "ge", 0.95, None), ("h4", "ge", 0.85, None)]),
    "T35-X": ("elements, not commands: a command split into elements loses even alone", [("e1", "le", 0.65, None)]),
    "T35-S": ("only two commands of one stream collide", [("s2", "ge", 0.90, None)]),
    "T34-A": ("host writes go through the lines' L3 homes, which allocate them",
              [("fw", "ge", 0.90, None), ("fc", "ge", 0.90, None), ("bad", "zero", None, None)]),
    "T34-B": ("host writes go through the L3 homes, which update a line they hold and allocate none",
              [("fw", "ge", 0.90, None), ("fc", "le", 0.10, None), ("bad", "zero", None, None)]),
    "T34-C": ("host writes go to the memory shires, and the L3's copy is invalidated",
              [("fw", "le", 0.10, None), ("fc", "le", 0.10, None), ("bad", "zero", None, None)]),
    "T34-D": ("host writes go to the memory shires, and the L3 keeps its stale copy",
              [("stale_warm", "ge", 0.90, None), ("fc", "le", 0.10, None)]),
}
# the R34 instrument's controls: every T34 theory is "invalid" on a card unless all of these PASS there
T34_CONTROLS = ("P34-1", "P34-2", "P34-3", "P34-5", "P34-6")
KEEP_MIN = 0.5      # a repetition with fewer kept (not ambiguous) lines than this share is left out of the fractions
CLOCK_Q = ("dref", "lref", "gap", "l2")   # absolute cycle counts: only from passes whose samples all read 600 MHz


def verdict(kind, a, b, vals):
    """PASS / FAIL / INCONCLUSIVE for one quantity's per-pass values."""
    if not vals:
        return "NO DATA", None
    if kind == "zero":
        return ("PASS" if all(v == 0 for v in vals) else "FAIL"), None
    m = st.mean(vals)
    if len(vals) > 1:
        h = tq(len(vals) - 1) * st.stdev(vals) / len(vals) ** 0.5
        lo, hi = m - h, m + h
    else:
        lo = hi = m
    if kind == "range":
        v = "PASS" if a <= lo and hi <= b else ("FAIL" if hi < a or lo > b else "INCONCLUSIVE")
    elif kind == "ge":
        v = "PASS" if lo >= a else ("FAIL" if hi < a else "INCONCLUSIVE")
    elif kind == "le":
        v = "PASS" if hi <= a else ("FAIL" if lo > a else "INCONCLUSIVE")
    else:
        raise ValueError(kind)
    return v, {"mean": round(m, 4), "lo": round(lo, 4), "hi": round(hi, 4), "n": len(vals)}


def bound_text(kind, a, b):
    return {"range": f"{a}-{b}", "ge": f">= {a}", "le": f"<= {a}", "zero": "0 in every pass"}[kind]


# ---- reading a pass ------------------------------------------------------------------------------------------------
def read_pcie(path):
    out = []
    try:
        with open(path, errors="replace") as f:
            for ln in f:
                if ln.startswith("PCIE {"):
                    try:
                        out.append(json.loads(ln[5:]))
                    except ValueError:
                        out.append({"test": "unparsable"})
    except OSError:
        pass
    return out


def read_jsonl(path):
    try:
        with open(path) as f:
            return [json.loads(ln) for ln in f if ln.strip().startswith("{")]
    except (OSError, ValueError):
        return []


def read_json(path):
    try:
        with open(path) as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def check_pass(d):
    """Integrity of one pass: every planned process ran and exited 0, no stream error, every trial and arm present."""
    probs = []
    plan = read_json(os.path.join(d, "plan.json"))
    if not plan:
        return {"ok": False, "problems": ["no plan.json"]}
    launches = {x.get("id"): x for x in read_jsonl(os.path.join(d, "launches.jsonl"))}
    for p in plan:
        pid = p["id"]
        la = launches.get(pid)
        if not la:
            probs.append(f"{pid}: never launched")
            continue
        if la.get("rc") != 0:
            probs.append(f"{pid}: exit {la.get('rc')}")
        lines = read_pcie(os.path.join(d, f"{pid}.out"))
        if not any(x.get("test") == "done" for x in lines):
            probs.append(f"{pid}: no done line")
        for x in lines:
            if x.get("test") in ("error", "unparsable") or x.get("truncated"):
                probs.append(f"{pid}: {x.get('test')} {x.get('what', '')}{' truncated' if x.get('truncated') else ''}")
            if x.get("stream_errors", 0):
                probs.append(f"{pid}: stream errors in {x.get('cfg') or x.get('arm')}")
        if p["kind"] == "conc":
            cnt = {}
            for x in lines:
                if x.get("test") == "conc" and "wall_ns" in x:
                    cnt[x["cfg"]] = cnt.get(x["cfg"], 0) + 1
            cfgs = p["args"][p["args"].index("--cfgs") + 1].split(",")
            for c in cfgs:
                if cnt.get(c, 0) != p["trials"]:
                    probs.append(f"{pid}: {c} has {cnt.get(c, 0)} of {p['trials']} trials")
        else:
            arms = [x for x in lines if x.get("test") == "touch" and x.get("kind") == "arm"]
            if len(arms) != 5 * p["reps"]:
                probs.append(f"touch: {len(arms)} of {5 * p['reps']} arms")
            for x in arms:
                if not x.get("valid") or (x.get("dt1") or [-1])[0] == -1:
                    probs.append(f"touch: rep {x.get('rep')} {x.get('arm')} not valid (the kernel's results missing)")
    pj = read_json(os.path.join(d, "pass.json")) or {}
    if pj.get("max_c") is not None and pj["max_c"] >= 90:
        probs.append(f"a die read {pj['max_c']} C")
    notes = []
    if pj.get("mhz") and any(m != 600 for m in pj["mhz"] if m):
        notes.append(f"minion clock not 600 MHz in a sample: {pj['mhz']} (R34's cycles assume a fixed clock)")
    return {"ok": not probs, "problems": probs, "notes": notes}


def med(v):
    return st.median(v) if v else None


def fit_line(pts):
    """Least squares y = a + b x through [(x, y)]: (a, b), or None with fewer than three points."""
    if len(pts) < 3:
        return None
    mx = st.mean(x for x, _ in pts)
    my = st.mean(y for _, y in pts)
    sxx = sum((x - mx) ** 2 for x, _ in pts)
    if not sxx:
        return None
    b = sum((x - mx) * (y - my) for x, y in pts) / sxx
    return my - b * mx, b


def clock_ok(pj):
    """True when every telemetry sample of the pass read the minion clock at 600 MHz."""
    m = (pj or {}).get("mhz") or []
    return bool(m) and all(x == 600 for x in m)


def pass_values(d, pj=None):
    """Every quantity of one pass (None where its process is missing)."""
    plan = read_json(os.path.join(d, "plan.json")) or []
    if pj is None:
        pj = read_json(os.path.join(d, "pass.json")) or {}
    tot_bytes = {}
    agg, wall = {}, {}
    V = {}
    for p in plan:
        lines = read_pcie(os.path.join(d, f"{p['id']}.out"))
        if p["kind"] == "conc":
            per = {}
            for x in lines:
                if x.get("test") == "conc" and "wall_ns" in x:
                    per.setdefault(x["cfg"], []).append(x)
            for c, xs in per.items():
                agg[(p["mb"], p["elements"], c)] = med([x["legs"] * x["bytes_per_leg"] / x["wall_ns"] for x in xs])
                wall[(p["mb"], p["elements"], c)] = med([x["wall_ns"] / 1e6 for x in xs])
                tot_bytes[(p["mb"], p["elements"], c)] = xs[0]["legs"] * xs[0]["bytes_per_leg"]
        else:
            V.update(touch_values(lines))
    if not clock_ok(pj):   # R34's absolute cycle counts assume 600 MHz: not from this pass
        V["clock_excluded"] = 1
        for q in CLOCK_Q:
            V.pop(q, None)

    def ratio(k1, k2):
        return agg[k1] / agg[k2] if k1 in agg and k2 in agg and agg[k2] else None

    for mb in (1, 4, 16, 64):
        V[f"h{mb}"] = ratio((mb, 0, "h2d"), (mb, 0, "h2d/ser"))
        V[f"d{mb}"] = ratio((mb, 0, "d2h"), (mb, 0, "d2h/ser"))
        V[f"s2_{mb}"] = ratio((mb, 0, "2xh2d/ser"), (mb, 0, "h2d/ser"))
        V[f"h{mb}e8"] = ratio((mb, 8, "h2d"), (mb, 8, "h2d/ser"))
        if (mb, 0, "h2d") in wall and (mb, 0, "h2d/ser") in wall:
            V[f"lost_ms{mb}"] = wall[(mb, 0, "h2d")] - wall[(mb, 0, "h2d/ser")]
    V["s2"] = V.get("s2_64")
    V["e1"] = ratio((64, 8, "h2d/ser"), (64, 1, "h2d/ser"))
    V["e2"] = V.get("h64e8")
    V["lc"] = ratio((64, 1, "h2d/ser"), (64, 0, "h2d/ser"))
    V["gbs"] = {f"{mb}m-e{el}-{c}": round(g, 4) for (mb, el, c), g in sorted(agg.items())}
    fits = {}
    for c in ("h2d", "h2d/ser"):
        fits[c] = fit_line([(tot_bytes[(mb, 0, c)], wall[(mb, 0, c)])
                            for mb in (1, 4, 16, 64) if (mb, 0, c) in wall])
    if fits["h2d"] and fits["h2d/ser"] and fits["h2d"][1] > 0:
        V["rr"] = fits["h2d/ser"][1] / fits["h2d"][1]
        V["icpt_gap_ms"] = fits["h2d"][0] - fits["h2d/ser"][0]
        V["icpt_ser_ms"] = fits["h2d/ser"][0]
    return V


def touch_values(lines):
    arms = {}
    for x in lines:
        if x.get("test") == "touch" and x.get("kind") == "arm" and x.get("valid"):
            arms.setdefault(x["rep"], {})[x["arm"]] = x
    fr = {"h2d_warm": [], "h2d_cold": [], "l3_ref2": []}
    pool = {"dram_ref": [], "l3_ref": [], "gap": [], "l2": []}
    amb, tot, bad, stale_warm, m_warm, dropped = 0, 0, 0, 0, 0, 0
    for rep, a in sorted(arms.items()):
        if "dram_ref" not in a or "l3_ref" not in a:
            continue
        dr, l3 = a["dram_ref"]["dt1"], a["l3_ref"]["dt1"]
        pool["dram_ref"] += dr
        pool["l3_ref"] += l3
        pool["gap"] += [x - y for x, y in zip(dr, l3)]
        # a u32 interval the counter's carry glitch made negative reads as about 4e9: such a line is left out too
        keep = [i for i in range(len(dr)) if dr[i] - l3[i] >= AMBIG and max(dr[i], l3[i]) < GLITCH]
        amb += len(dr) - len(keep)
        tot += len(dr)
        if not dr or len(keep) < KEEP_MIN * len(dr):   # the references did not separate in this repetition
            dropped += 1
            keep = []
        for name in fr:
            if name in a and keep:
                t = a[name]["dt1"]
                fr[name].append(sum(1 for i in keep if abs(t[i] - l3[i]) < abs(t[i] - dr[i]) and t[i] < GLITCH)
                                / len(keep))
        for x in a.values():
            pool["l2"] += x["dt2"]
            bad += (len(x["dt1"]) - x["ok"])
        if "h2d_warm" in a:
            stale_warm += a["h2d_warm"]["stale"]
            m_warm += len(a["h2d_warm"]["dt1"])
    if not tot:
        return {}
    return {"dref": med(pool["dram_ref"]), "lref": med(pool["l3_ref"]), "gap": med(pool["gap"]),
            "l2": med(pool["l2"]), "amb": amb / tot,
            "fw": st.mean(fr["h2d_warm"]) if fr["h2d_warm"] else None,
            "fc": st.mean(fr["h2d_cold"]) if fr["h2d_cold"] else None,
            "fr": st.mean(fr["l3_ref2"]) if fr["l3_ref2"] else None,
            "bad": bad, "stale_warm": stale_warm / m_warm if m_warm else None, "touch_reps": len(arms),
            "reps_dropped": dropped}


# ---- cards ---------------------------------------------------------------------------------------------------------
def find_passes(root):
    out = {}
    for d in sorted(glob.glob(os.path.join(root, "*", "pcie2", "p*")) + glob.glob(os.path.join(root, "*", "p*"))):
        base = os.path.basename(d)
        if not os.path.isdir(d) or not base[1:].isdigit():
            continue
        card = os.path.basename(os.path.dirname(d))
        card = os.path.basename(os.path.dirname(os.path.dirname(d))) if card == "pcie2" else card
        out.setdefault(card, []).append((int(base[1:]), d))
    return out


def frozen_sha():
    """PREREG.md's sha256 as the freeze recorded it (PREREG.sha256 beside this file), or None before the freeze."""
    try:
        with open(os.path.join(HERE, "PREREG.sha256")) as f:
            return f.read().split()[0]
    except (OSError, IndexError):
        return None


def reduce_all(root, dev=False, prereg=None, allow_dry=False):
    """prereg: the PREREG.md sha256 a validation pass must have run on (default: PREREG.sha256's)."""
    prereg = prereg if prereg is not None else frozen_sha()
    D = {"meta": {"prereg_sha256": sha(os.path.join(HERE, "PREREG.md")), "frozen_prereg_sha256": prereg,
                  "reduce_sha256": sha(__file__),
                  "judged": "development passes (100-899)" if dev else "validation passes (1-99)"},
         "cards": {}}
    for card, passes in sorted(find_passes(root).items()):
        C = {"passes": {}, "left_out": {}, "stats": {}, "verdicts": {}, "theories": {}}
        for p, d in sorted(passes):
            if p >= 900 or (dev and not 100 <= p < 900) or (not dev and not 1 <= p < 100):
                continue
            bj = read_json(os.path.join(d, "block.json")) or {}
            pj = read_json(os.path.join(d, "pass.json")) or {}
            ck = check_pass(d)
            why = []
            if bj.get("status") != "ok" or not ck["ok"]:
                why += ck["problems"][:10] or [f"block.json status {bj.get('status')}"]
            if (pj.get("dry") or bj.get("dry")) and not allow_dry:
                why.append("a V3_DRY pass (the stub's numbers)")
            if not dev:
                if pj.get("frozen") is not True:
                    why.append("a validation pass that did not run frozen")
                if not prereg:
                    why.append("no PREREG.sha256 here: nothing is frozen, so no pass is a validation pass")
                elif pj.get("prereg_sha256") != prereg:
                    why.append(f"ran on PREREG.md {str(pj.get('prereg_sha256'))[:12]}, not the frozen {prereg[:12]}")
            if why:
                C["left_out"][p] = {"status": bj.get("status"), "problems": why}
                continue
            C["passes"][p] = pass_values(d, pj)
        vals = lambda q: [v[q] for v in C["passes"].values() if v.get(q) is not None]
        for pid, q, kind, a, b, _ in PRED:
            v, s = verdict(kind, a, b, vals(q))
            C["verdicts"][pid] = v
            C["stats"][q] = s if s else {"values": vals(q)}
        for q in ("lost_ms1", "lost_ms4", "lost_ms16", "lost_ms64", "s2_1", "s2_4", "s2_16", "h1e8", "h4e8",
                  "h16e8", "stale_warm", "touch_reps", "reps_dropped", "icpt_gap_ms", "icpt_ser_ms",
                  "clock_excluded"):
            if vals(q):
                C["stats"][q] = verdict("range", -1e18, 1e18, vals(q))[1]
        bad_ctl = [c for c in T34_CONTROLS if C["verdicts"][c] != "PASS"]
        C["t34_controls"] = {c: C["verdicts"][c] for c in T34_CONTROLS}
        for t, (_, conds) in THEORY.items():
            vs = [verdict(kind, a, b, vals(q))[0] for q, kind, a, b in conds]
            C["theories"][t] = ("refuted" if "FAIL" in vs else "survives" if all(v == "PASS" for v in vs)
                                else "no data" if all(v == "NO DATA" for v in vs) else "open")
            if t.startswith("T34-") and bad_ctl:
                C["theories"][t] = "invalid"   # the instrument's controls did not all pass: nothing to judge
        D["cards"][card] = C
    return D


def sha(path):
    try:
        with open(path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()
    except OSError:
        return None


def markdown(D):
    cards = list(D["cards"])
    L = ["# PCIE2: results against the predictions", "",
         f"Generated by `tools/claims-v3/pcie2/reduce.py`; {D['meta']['judged']}. PREREG.md sha256 "
         f"`{D['meta']['prereg_sha256']}`. Per card: the mean over passes [99% interval] (n passes).", "",
         "| ID | Quantity | Prediction | " + " | ".join(cards) + " |", "|---|---|---|" + "---|" * len(cards)]
    for pid, q, kind, a, b, what in PRED:
        row = [pid, what, bound_text(kind, a, b)]
        for c in cards:
            s = D["cards"][c]["stats"].get(q) or {}
            v = D["cards"][c]["verdicts"][pid]
            row.append(f"{v}: {s['mean']} [{s['lo']}, {s['hi']}] (n={s['n']})" if "mean" in s else
                       f"{v}: {s.get('values')}")
        L.append("| " + " | ".join(row) + " |")
    L += ["", "| Theory | What | " + " | ".join(cards) + " |", "|---|---|" + "---|" * len(cards)]
    for t, (what, _) in THEORY.items():
        L.append(f"| {t} | {what} | " + " | ".join(D["cards"][c]["theories"][t] for c in cards) + " |")
    for c in cards:
        bad = {k: v for k, v in D["cards"][c].get("t34_controls", {}).items() if v != "PASS"}
        if bad:
            L += ["", f"On {c} the R34 theories are invalid: the instrument's controls did not all pass: "
                  + json.dumps(bad)]
    for c in cards:
        if D["cards"][c]["left_out"]:
            L += ["", f"Left out on {c}: " + json.dumps(D["cards"][c]["left_out"])]
    return "\n".join(L) + "\n"


def print_predictions():
    print("| ID | Quantity | Prediction |\n|---|---|---|")
    for pid, q, kind, a, b, what in PRED:
        print(f"| {pid} | {what} (`{q}`) | {bound_text(kind, a, b)} |")
    print("\n| Theory | Conditions |\n|---|---|")
    for t, (what, conds) in THEORY.items():
        print(f"| {t}: {what} | " + "; ".join(f"`{q}` {bound_text(k, a, b)}" for q, k, a, b in conds) + " |")
    print(f"\nT34 theories are invalid on a card unless {', '.join(T34_CONTROLS)} all PASS there. A repetition with "
          f"fewer than {KEEP_MIN:.0%} of its lines kept is left out of the fractions. {', '.join(CLOCK_Q)} come only "
          "from passes whose samples all read 600 MHz.")


# ---- self-test: the stub's model pairs through the whole chain ------------------------------------------------------
SELFTEST_SHA = "selftest-prereg-sha256"


def fake_pass(root, card, p, r35, r34, env_extra=None, pj_extra=None):
    d = os.path.join(root, card, "pcie2", f"p{p}")
    os.makedirs(d)
    env = dict(os.environ, PCIE2_DRY_R35=r35, PCIE2_DRY_R34=r34, **(env_extra or {}))
    lib = os.path.join(HERE, "pcie2lib.py")
    plan = [json.loads(x) for x in subprocess.run([sys.executable, lib, "plan", "--pass", str(p)], env=env, check=True,
                                                   capture_output=True, text=True).stdout.splitlines()]
    with open(os.path.join(d, "plan.json"), "w") as f:
        json.dump(plan, f)
    with open(os.path.join(d, "launches.jsonl"), "w") as lf:
        for x in plan:
            r = subprocess.run([sys.executable, lib, "stub"] + x["args"], env=env, capture_output=True, text=True)
            with open(os.path.join(d, f"{x['id']}.out"), "w") as f:
                f.write(r.stdout)
            lf.write(json.dumps({"id": x["id"], "rc": r.returncode}) + "\n")
    pj = {"max_c": 80, "mhz": [600, 600, 600], "frozen": True, "prereg_sha256": SELFTEST_SHA, "dry": False}
    pj.update(pj_extra or {})
    with open(os.path.join(d, "pass.json"), "w") as f:
        json.dump(pj, f)
    with open(os.path.join(d, "block.json"), "w") as f:
        json.dump({"status": "ok"}, f)
    return d


def self_test():
    T34_INVALID = {t: "invalid" for t in ("T34-A", "T34-B", "T34-C", "T34-D")}
    # (R35 model, R34 model, stub environment, the theories' expected fates, every prediction must pass)
    cases = [("B", "A", {}, {"T35-BC": "survives", "T35-A": "refuted", "T35-E": "refuted", "T35-X": "refuted",
                             "T35-S": "refuted", "T34-A": "survives", "T34-B": "refuted", "T34-C": "refuted",
                             "T34-D": "refuted"}, True),
             # the review's case: a command's fixed cost of 0 or 0.25 ms, overlapped when two are in flight
             ("B", "A", {"PCIE2_DRY_CMD_MS": "0"}, {"T35-BC": "survives", "T35-A": "refuted", "T35-E": "refuted"},
              True),
             ("B", "A", {"PCIE2_DRY_CMD_MS": "0.25"}, {"T35-BC": "survives", "T35-A": "refuted", "T35-E": "refuted"},
              True),
             ("A", "B", {}, {"T35-A": "survives", "T35-BC": "refuted", "T35-E": "refuted",
                             "T34-B": "survives", "T34-A": "refuted", "T34-C": "refuted", "T34-D": "refuted"}, False),
             ("E", "C", {}, {"T35-E": "survives", "T35-BC": "refuted", "T35-A": "refuted",
                             "T34-C": "survives", "T34-A": "refuted", "T34-B": "refuted", "T34-D": "refuted"}, False),
             ("X", "D", {}, {"T35-X": "survives", "T35-BC": "refuted",
                             "T34-D": "survives", "T34-A": "refuted", "T34-B": "refuted", "T34-C": "refuted"}, False),
             # the flush launch does not empty the L3: the R34 instrument fails its controls, so no T34 verdict
             ("B", "N", {}, dict(T34_INVALID, **{"T35-BC": "survives"}), False)]
    tmp = tempfile.mkdtemp(prefix="pcie2-selftest-")
    bad = 0

    def check(ok, what):
        nonlocal bad
        bad += not ok
        print(f"{'ok  ' if ok else 'FAIL'} {what}")

    try:
        for i, (r35, r34, env, want, allpass) in enumerate(cases):
            root = os.path.join(tmp, f"c{i}-{r35}{r34}")
            for p in (1, 2, 3):
                fake_pass(root, "aifoundry3", p, r35, r34, env)
            D = reduce_all(root, prereg=SELFTEST_SHA)
            got = D["cards"]["aifoundry3"]["theories"]
            tag = f"R35 model {r35}, R34 model {r34}{' ' + json.dumps(env) if env else ''}"
            for t, w in want.items():
                check(got[t] == w, f"{tag}: {t} {got[t]} (want {w})")
            if allpass:
                v = D["cards"]["aifoundry3"]["verdicts"]
                nonpass = {k: x for k, x in v.items() if x != "PASS"}
                check(not nonpass, f"{tag}: every registered prediction passes"
                      f"{'' if not nonpass else ': ' + json.dumps(nonpass)}")
                if i == 0:
                    print(markdown(D))
        # left out: a timed-out process; an unfrozen validation pass; another PREREG.md; a dry pass
        for name, pj_extra, env, why in [("rc124", {}, {}, "exit 124"),
                                         ("unfrozen", {"frozen": False}, {}, "did not run frozen"),
                                         ("prereg", {"prereg_sha256": "an-older-prereg"}, {}, "not the frozen"),
                                         ("dry", {"dry": True}, {}, "V3_DRY")]:
            root = os.path.join(tmp, "left-" + name)
            d = fake_pass(root, "aifoundry3", 1, "B", "A", env, pj_extra)
            if name == "rc124":
                with open(os.path.join(d, "launches.jsonl"), "a") as f:
                    f.write(json.dumps({"id": "touch", "rc": 124}) + "\n")
            D = reduce_all(root, prereg=SELFTEST_SHA)
            lo = D["cards"]["aifoundry3"]["left_out"].get(1)
            check(bool(lo) and any(why in x for x in lo["problems"]), f"a validation pass is left out: {name} ({lo})")
        # with no PREREG.sha256 (prereg ""), no validation pass is judged; --dev judges development passes regardless
        root = os.path.join(tmp, "nofreeze")
        fake_pass(root, "aifoundry3", 1, "B", "A", {}, {"frozen": False, "prereg_sha256": "draft"})
        fake_pass(root, "aifoundry3", 101, "B", "A", {}, {"frozen": False, "prereg_sha256": "draft"})
        D = reduce_all(root, prereg="")
        check(1 in D["cards"]["aifoundry3"]["left_out"] and not D["cards"]["aifoundry3"]["passes"],
              "no freeze: the validation pass is left out")
        D = reduce_all(root, dev=True, prereg="")
        check(list(D["cards"]["aifoundry3"]["passes"]) == [101], "--dev: the development pass is judged unfrozen")
        # a clock off 600 MHz: the latency quantities (P34-1..4) are not taken, so the T34 theories are invalid
        root = os.path.join(tmp, "clock")
        for p in (1, 2, 3):
            fake_pass(root, "aifoundry2", p, "B", "A", {}, {"mhz": [600, 800, 600]})
        D = reduce_all(root, prereg=SELFTEST_SHA)
        C = D["cards"]["aifoundry2"]
        check(C["verdicts"]["P34-1"] == "NO DATA" and C["verdicts"]["P34-7"] == "PASS"
              and C["theories"]["T34-A"] == "invalid", "clock at 800 MHz in a sample: P34-1..4 not judged, "
              f"fractions still are, T34 invalid ({C['verdicts']['P34-1']}, {C['verdicts']['P34-7']}, "
              f"{C['theories']['T34-A']})")
        # a repetition whose references did not separate is left out of the fractions, and counted
        root = os.path.join(tmp, "droprep")
        d = fake_pass(root, "aifoundry3", 1, "B", "A")
        out = os.path.join(d, "touch.out")
        lines = open(out).read().splitlines()
        l3 = {}
        for ln in lines:
            if ln.startswith("PCIE {"):
                x = json.loads(ln[5:])
                if x.get("arm") == "l3_ref":
                    l3[x["rep"]] = x["dt1"]
        with open(out, "w") as f:
            for ln in lines:
                if ln.startswith("PCIE {"):
                    x = json.loads(ln[5:])
                    if x.get("arm") == "dram_ref" and x["rep"] == 0:
                        x["dt1"] = [v + 5 for v in l3[0]]      # rep 0: DRAM reads like L3 (a flush that failed)
                        ln = "PCIE " + json.dumps(x, separators=(",", ":"))
                f.write(ln + "\n")
        V = pass_values(d)
        check(V["reps_dropped"] == 1 and V["fw"] is not None and V["fw"] >= 0.9,
              f"a repetition with its references < 40 cycles apart is dropped from the fractions "
              f"(reps_dropped {V['reps_dropped']}, fw {V['fw']:.3f}, amb {V['amb']:.3f})")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("self-test:", "PASS" if not bad else f"{bad} FAILURES")
    return 1 if bad else 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check-pass")
    ap.add_argument("--data")
    ap.add_argument("--out")
    ap.add_argument("--md")
    ap.add_argument("--dev", action="store_true")
    ap.add_argument("--allow-dry", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--print-predictions", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if a.print_predictions:
        print_predictions()
        return 0
    if a.check_pass:
        r = check_pass(a.check_pass)
        print(json.dumps(r))
        return 0 if r["ok"] else 1
    if a.data:
        D = reduce_all(a.data, a.dev, allow_dry=a.allow_dry)
        if not a.dev and not D["meta"]["frozen_prereg_sha256"]:
            print("note: no PREREG.sha256 here (not frozen): every validation pass is left out", file=sys.stderr)
        if a.out:
            with open(a.out, "w") as f:
                json.dump(D, f, indent=1)
        md = markdown(D)
        if a.md:
            with open(a.md, "w") as f:
                f.write(md)
        print(md)
        return 0
    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
