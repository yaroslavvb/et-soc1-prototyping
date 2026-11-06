#!/usr/bin/env python3
"""Dated amendment A1 to the dip term (REGISTRATION.md.dated-note-4.md): the fall rule set against the governor's own steps.
dipterm.py, the registered term, is imported unchanged; this module wraps it. Python 3 standard library only.

    import dipterm_a1 as A1
    procs = A1.load_session(<session dir>, blocks=("BURST",))   dipterm.load_session, plus each process's block and its
                                                                 SP ring status (A1-2) and scope (A1-3)
    A1.count_rule(procs, card)                                   DT-N on A1's fall rule (A1-1)
    A1.predict(procs, card, f_ref, dP, arm)                      the arms, with A1-2's first calibration fall, A1-4's
                                                                 Monte Carlo batches, A1-5's card 0 climb, A1-6's lag arm
    A1.lattice_rule(procs, card, pred_seq)                       DT-L from A1's calibration
    python3 dipterm_a1.py --selftest                             T1-T9

A1-1  A fall is an eligible gap whose next launch reads 0.55-0.62 GHz (the boot point; Q132(g)'s kernel rule). A gap is
      eligible when it is structurally eligible as registered (inside one process, its zone opening at least one heartbeat
      period after the process's first launch, a stamp gap of 0 ms or more) and its process is in scope (A1-3), and either
      the launch before it read 0.79 GHz or more (a full-clock launch: the governor moves one point a pass, so only the idle
      reset reaches the boot point from there in one gap), or it read 0.65 GHz or more and the process is CLEAR (A1-2).
A1-2  A process is CLEAR when its run's SP ring dump exists, reaches back to the previous run's dump (nothing between the
      two dumps can have been overwritten), holds power-status records, and holds none that sets the boot point or lower
      for any reason but POWER_IDLE (throttle state not 0 and target 620 MHz or less: a power or thermal step, or the alarm).
      The calibration's first fall must lie in a clear process; later falls are checked against the lattice at 20 ms, as
      registered.
A1-3  DT-N and DT-L score the processes of the session's registered burst block(s) only (default "BURST"). A process that
      holds an alarm step (a launch under 0.55 GHz straight after one at 0.65 GHz or more, or a POWER_SAFE record in its
      run's ring) is out of scope; it is reported, never counted.
A1-4  Each arm's Monte Carlo is 8 batches of 500 draws (seeds 145-152, 4,000 draws a process); a rule's figure is read on
      the pooled deficits, and its Monte Carlo standard error is the sd of the 8 batch figures over sqrt(8).
A1-5  Card 0's climb after a fall: c7 0.062 s, c8 0.262 s (climb_c0_a1.py over E114's and E174's committed falls). At a
      process start card 0 keeps the registered 0.11 / 0.39 s (E114's start table: 0.389 s). aifoundry2 is unchanged.
A1-6  The board's deficit is also reported with the meter lag at 0.17 s (one aifoundry2 SP pass under the 10 Hz sampler)
      beside the registered 0.24 s: a sensitivity arm, never a verdict.
SPDX-License-Identifier: Apache-2.0
"""
import gzip
import json
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "hpl"))
import dipterm as DT  # noqa: E402  (the registered term, unchanged)

# ------------------------------------------------------------------ A1's constants (REGISTRATION.md.dated-note-4.md)
FALL_LO_GHZ, FALL_HI_GHZ = 0.55, DT.FALL_GHZ          # A1-1: the boot point, Q132(g)'s 0.55-0.62
FULL_GHZ = 0.79                                       # A1-1: Q132(g)'s full-clock launch
ABOVE_GHZ = DT.ABOVE_GHZ                              # 0.65, as registered
STEP_MHZ = 620                                        # A1-2: a step to the boot point or lower
BURST_BLOCKS = ("BURST",)                             # A1-3
MC_BATCHES, MC_BATCH_DRAWS = 8, 500                   # A1-4
CLIMB_START_S = {"a2": DT.CLIMB_S["a2"], "c0": DT.CLIMB_S["c0"]}      # A1-5: at a process start, as registered
CLIMB_FALL_S = {"a2": DT.CLIMB_S["a2"], "c0": (0.062, 0.262)}         # A1-5: after a fall (climb-c0-a1.txt, pooled)
BOARD_LAG_SENS_S = 0.17                               # A1-6
LAGS = (DT.BOARD_LAG_S, BOARD_LAG_SENS_S)


def _jl(path):
    for p in (path, path + ".gz"):
        if os.path.exists(p):
            break
    else:
        return []
    op = gzip.open if p.endswith(".gz") else open
    out = []
    with op(p, "rt") as f:
        for ln in f:
            ln = ln.strip()
            if ln.startswith("{"):
                try:
                    out.append(json.loads(ln))
                except ValueError:
                    pass
    return out


# ------------------------------------------------------------------ A1-2: the ring
def classify_ring(prev, cur):
    """One run's ring status from the previous dump's entries (prev; None when there is none) and this run's (cur; None
    when the dump is missing or unreadable). Entries are sptrace_full.scan's dicts."""
    st = {"dump": cur is not None, "complete": False, "pstat": 0, "power_idle": 0, "steps_to_boot": 0, "alarm_records": 0}
    if cur:
        st["complete"] = bool(prev) and min(e["ts"] for e in cur) <= max(e["ts"] for e in prev)
        t0 = max(e["ts"] for e in prev) if prev else None
        for e in cur:
            if t0 is not None and e["ts"] <= t0:
                continue
            if e.get("kind") != "pstat":
                continue
            st["pstat"] += 1
            ths, mhz = e.get("throttle_state"), e.get("mhz")
            if ths == 0:
                st["power_idle"] += 1
            elif mhz is not None and mhz <= STEP_MHZ:
                st["steps_to_boot"] += 1
            if ths == 3:
                st["alarm_records"] += 1
    st["clear"] = bool(st["dump"] and st["complete"] and st["pstat"] > 0 and st["steps_to_boot"] == 0)
    return st


def ring_status(sdir):
    """{run: status} over the runs of runs.jsonl in order, each dump against the one before it (sp/start.bin first)."""
    import sptrace_full as spf
    sp = os.path.join(sdir, "sp")
    prev = None
    sb = os.path.join(sp, "start.bin")
    if os.path.exists(sb):
        prev = spf.scan(open(sb, "rb").read())
    out = {}
    for r in _jl(os.path.join(sdir, "runs.jsonl")):
        fp = os.path.join(sp, r["run"] + ".bin")
        cur = spf.scan(open(fp, "rb").read()) if os.path.exists(fp) else None
        out[r["run"]] = classify_ring(prev, cur)
        prev = cur          # a missing or unreadable dump leaves the next run's completeness unshown
    return out


NO_RING = {"dump": False, "complete": False, "pstat": 0, "power_idle": 0, "steps_to_boot": 0, "alarm_records": 0, "clear": False}


def mark(procs, ring, blocks=BURST_BLOCKS, runs=None):
    """Attach A1's fields to dipterm.load_session's processes: block, ring status, clear, alarm, in scope."""
    runs = runs or {}
    for p in procs:
        blk = (runs.get(p["run"]) or {}).get("block") or p["run"].split("-", 1)[0]
        rs = ring.get(p["run"], NO_RING)
        L = p["launches"]
        alarm_clock = any(L[i - 1][3] >= ABOVE_GHZ and L[i][3] < FALL_LO_GHZ for i in range(1, len(L)))
        alarm = bool(rs["alarm_records"] or alarm_clock)
        p["a1"] = {"block": blk, "ring": rs, "clear": bool(rs["clear"]), "alarm": alarm,
                   "in_scope": bool((blocks is None or blk in blocks) and not alarm)}
    return procs


def load_session(sdir, blocks=BURST_BLOCKS):
    procs = DT.load_session(sdir)
    runs = {r["run"]: r for r in _jl(os.path.join(sdir, "runs.jsonl"))}
    return mark(procs, ring_status(sdir), blocks, runs)


# ------------------------------------------------------------------ A1-1: the gaps and the count
def gaps(proc, card):
    a1 = proc.get("a1") or {"clear": False, "in_scope": True}
    out = []
    for g in DT.gaps(proc, card):
        h = dict(g)
        h["reg_eligible"], h["reg_fell"] = g["eligible"], g["fell"]
        struct = g["stamp_gap"] >= 0 and g["after_first_beat"]
        clock = g["prev_ghz"] >= FULL_GHZ or (g["prev_ghz"] >= ABOVE_GHZ and a1["clear"])
        h["eligible"] = bool(a1["in_scope"] and struct and clock)
        h["fell"] = bool(h["eligible"] and FALL_LO_GHZ <= g["ghz"] <= FALL_HI_GHZ)
        h["by"] = (("full clock" if g["prev_ghz"] >= FULL_GHZ else "clear process") if h["fell"] else None)
        out.append(h)
    return out


def why_not(proc, g):
    a1 = proc["a1"]
    if not a1["in_scope"]:
        return "out of scope: " + ("an alarm step in the process" if a1["alarm"] else f"block {a1['block']}")
    if not (g["stamp_gap"] >= 0 and g["after_first_beat"]):
        return "inside the process's first heartbeat period (no idle edge can fall there)"
    if g["ghz"] < FALL_LO_GHZ:
        return "an alarm step (under 0.55 GHz)"
    if g["prev_ghz"] < FULL_GHZ and not a1["clear"]:
        r = a1["ring"]
        cause = ("no ring dump" if not r["dump"] else "the ring does not reach the previous dump" if not r["complete"]
                 else f"{r['steps_to_boot']} governor or alarm steps to <= {STEP_MHZ} MHz in the run's ring")
        return f"the launch before read {g['prev_ghz']:.3f} GHz, under 0.79, and the process is not clear ({cause})"
    return "other"


def count_rule(procs, card):
    P0 = DT.PERIOD_PRIOR_MS[card][0]
    elig, falls, excluded = [], [], []
    n_scope = 0
    for p in procs:
        n_scope += p["a1"]["in_scope"]
        for g in gaps(p, card):
            if g["fell"]:
                falls.append({"run": p["run"], "gap": g["i"], "prev_ghz": g["prev_ghz"], "ghz": g["ghz"], "by": g["by"],
                              "clear": p["a1"]["clear"]})
            elif g["reg_fell"]:
                excluded.append({"run": p["run"], "gap": g["i"], "prev_ghz": g["prev_ghz"], "ghz": g["ghz"], "why": why_not(p, g)})
            if g["eligible"]:
                elig.append(g["stamp_gap"])
    n = len(elig)
    s = float(sum(elig))
    seen = len(falls)
    exp = {f"delta_{d:.1f}_ms": round((s + n * d) / P0, 3) for d in (DT.DELTA_BAND_MS[0], DT.A_MS + DT.B_MS, DT.DELTA_BAND_MS[1])}
    lo = DT.pois_lo((s + n * DT.DELTA_BAND_MS[0]) / P0)
    hi = DT.pois_hi((s + n * DT.DELTA_BAND_MS[1]) / P0)
    verdict = ("PASS" if lo <= seen <= hi else ("FAIL (fewer falls than the gaps allow)" if seen < lo
                                                 else "FAIL (more falls than the gaps allow)"))
    return {"rule": "DT-N (A1)", "processes": len(procs), "processes_in_scope": n_scope, "eligible_gaps": n,
            "stamp_gap_ms_mean": round(s / n, 3) if n else None, "expected": exp, "band_95": [lo, hi], "observed_falls": seen,
            "verdict": verdict, "falls": falls, "registered_falls_not_counted": excluded,
            "form": "A1-1: a fall is an eligible gap whose next launch reads 0.55-0.62 GHz; eligible = structurally eligible, "
                    "in scope (A1-3), and the launch before at >= 0.79 GHz, or at >= 0.65 GHz in a clear process (A1-2); "
                    "expected and band as registered. A rate check: it tests how many falls the gaps allow, not where."}


# ------------------------------------------------------------------ the state machine (DT.simulate, with A1-5's two climbs)
def prep(proc, card):
    L = proc["launches"]
    zs = DT.gaps(proc, card)
    return {"busy": [(l[1] + 0.5 + DT.A_MS, l[2] + 0.5 - DT.B_MS) for l in L], "zones": [(z["i"], z["lo"], z["hi"]) for z in zs],
            "t_s": L[0][1] + 0.5, "t_e": L[-1][2] + 0.5}


def simulate(pp, t_ref, P, f_ref, cs, cf):
    """DT.simulate on prep()'s structures; cs is the climb at the process start, cf the climb after a fall (s)."""
    c7s, c8s, c7f, c8f = cs[0] * 1000.0, cs[1] * 1000.0, cf[0] * 1000.0, cf[1] * 1000.0
    busy, zs, t_s, t_e = pp["busy"], pp["zones"], pp["t_s"], pp["t_e"]
    k = math.ceil((t_s - t_ref) / P)
    state, lows, fell, climb0 = "idle", [], [], None
    low_from = t_s
    j = 0
    while True:
        h = t_ref + k * P
        k += 1
        if h > t_e:
            break
        while j < len(busy) and busy[j][1] < h:
            j += 1
        inside = j < len(busy) and busy[j][0] <= h <= busy[j][1]
        if inside and state == "idle":
            state = "busy"
            if climb0 is None:
                climb0 = h
                c7, c8 = c7s, c8s
            else:
                c7, c8 = c7f, c8f
            lows.append((low_from, h + c7, 600.0))
            lows.append((h + c7, h + c8, 700.0))
        elif not inside and state == "busy":
            state = "idle"
            low_from = h
            g = next((z for z in zs if z[1] <= h <= z[2]), None)
            fell.append(g[0] if g else None)
    if state == "idle":
        lows.append((low_from, t_e + 1.0, 600.0))
    return [(a, b, f) for a, b, f in lows if b > a and f < f_ref], fell, climb0


def deficits(proc, lows, f_ref, dp=None, lags=LAGS):
    """DT.deficits, with the board's deficit at each meter lag in lags."""
    w0, w1 = DT.window(proc)
    span = (w1 - w0) / 1000.0
    if span <= 0:
        return 0.0, [0.0 for _ in lags]
    clk = 0.0
    brd = [0.0 for _ in lags]
    for a, b, f in lows:
        clk += (f_ref - f) * max(0.0, min(b, w1) - max(a, w0)) / 1000.0
        if dp is not None:
            for n, lag_s in enumerate(lags):
                lag = lag_s * 1000.0
                brd[n] += dp.get(f, 0.0) * max(0.0, min(b + lag, w1) - max(a + lag, w0)) / 1000.0
    return clk / span, [x / span for x in brd]


# ------------------------------------------------------------------ the calibration and the arms
def calibration(procs, card, rule="a1"):
    """The seq arm's lattice before each process, built as dipterm.predict builds it (each process sees the falls of the
    processes before it; a later fall over 20 ms off the lattice so far is reported and not used), with A1-2's rule that
    the first fall used lies in a clear process (rule "a1"). rule "registered" is dipterm's own fall rule and calibration."""
    fall_obs = []
    for pi, p in enumerate(procs):
        for g in (gaps(p, card) if rule == "a1" else DT.gaps(p, card)):
            if g["fell"]:
                w = g["hi"] - g["lo"]
                ok_first = (p["a1"]["clear"] if rule == "a1" else True)
                fall_obs.append((pi, 0.5 * (g["lo"] + g["hi"]), math.sqrt(w * w / 12.0 + DT.SIGMA_Z_MS ** 2), ok_first, g["i"]))
    used, offl, skipped, fits, first = [], [], [], [], None
    for pi, p in enumerate(procs):
        for (qi, c, sd, ok_first, gi) in [f for f in fall_obs if f[0] == pi - 1]:
            if used:
                t0_, P_, _ = DT.fit_lattice(used, card)
                r = c - (t0_ + round((c - t0_) / P_) * P_)
                if abs(r) > DT.OFF_LATTICE_MS:
                    offl.append({"process": qi, "run": procs[qi]["run"], "residual_ms": round(r, 2)})
                    continue
            elif not ok_first:
                skipped.append({"process": qi, "run": procs[qi]["run"], "gap": gi,
                                "why": "A1-2: the calibration's first fall must lie in a clear process"})
                continue
            if first is None:
                first = qi
            used.append((c, sd))
        fits.append((DT.fit_lattice(used, card) if used else None, len(used)))
    return {"fall_obs": fall_obs, "fits": fits, "off_lattice": offl, "first_skipped": skipped, "first_process": first}


def predict(procs, card, f_ref, dP=None, arm="seq", batches=MC_BATCHES, batch_draws=MC_BATCH_DRAWS, seed=DT.SEED,
            rule="a1", climbs="a1", lags=LAGS, cal=None):
    """Per process: the clock deficit (MHz) and the board deficit at each lag (W) in its window, per batch and pooled;
    P(fall) per gap and P(late climb), pooled. With rule "registered", climbs "registered", batches 1 and the registered
    draws and seed this is dipterm.predict draw for draw (self-test T4)."""
    P0, s0 = DT.PERIOD_PRIOR_MS[card]
    cs = DT.CLIMB_S[card] if climbs == "registered" else CLIMB_START_S[card]
    cf = DT.CLIMB_S[card] if climbs == "registered" else CLIMB_FALL_S[card]
    cal = cal or calibration(procs, card, rule)
    oracle = (DT.fit_lattice([(c, sd) for _, c, sd, _, _ in cal["fall_obs"]], card) if (arm == "oracle" and cal["fall_obs"])
              else None)
    preps = [prep(p, card) for p in procs]
    recs = []
    for pi, p in enumerate(procs):
        recs.append({"run": p["run"], "arm": arm, "clock_batches": [], "board_batches": [[] for _ in lags],
                     "p_fall_n": {}, "late_n": 0, "draws": 0,
                     "calibration_falls": cal["fits"][pi][1] if arm == "seq" else 0})
    for b in range(batches):
        rng = random.Random(seed + b)
        for pi, p in enumerate(procs):
            rec = recs[pi]
            if arm == "none":
                rec["clock_batches"].append(0.0)
                for n in range(len(lags)):
                    rec["board_batches"][n].append(0.0)
                continue
            fr = float(f_ref.get(p["run"], 800.0))
            dp = (dP or {}).get(p["run"])
            fit = cal["fits"][pi][0] if arm == "seq" else None
            w0 = DT.window(p)[0]
            clk = 0.0
            brd = [0.0 for _ in lags]
            for _ in range(batch_draws):
                if arm == "count" or (arm == "seq" and fit is None):
                    P = rng.gauss(P0, s0)
                    t_ref = p["launches"][0][1] + 0.5 + rng.random() * P
                elif arm == "seq":
                    t_ref, P = DT._draw(fit[0], fit[1], fit[2], rng)
                else:
                    t_ref, P = DT._draw(oracle[0], oracle[1], oracle[2], rng)
                lows, fell, c0 = simulate(preps[pi], t_ref, P, fr, cs, cf)
                c, bb = deficits(p, lows, fr, dp, lags)
                clk += c
                for n in range(len(lags)):
                    brd[n] += bb[n]
                for i in fell:
                    if i is not None:
                        rec["p_fall_n"][i] = rec["p_fall_n"].get(i, 0) + 1
                if c0 is not None and c0 + cs[1] * 1000.0 > w0:
                    rec["late_n"] += 1
            rec["draws"] += batch_draws
            rec["clock_batches"].append(clk / batch_draws)
            for n in range(len(lags)):
                rec["board_batches"][n].append(brd[n] / batch_draws)
    out = []
    for rec in recs:
        d = max(rec["draws"], 1)
        out.append({"run": rec["run"], "arm": arm, "calibration_falls": rec["calibration_falls"],
                    "clock_deficit_mhz": sum(rec["clock_batches"]) / len(rec["clock_batches"]),
                    "board_deficit_w": [sum(x) / len(x) for x in rec["board_batches"]],
                    "clock_batches": rec["clock_batches"], "board_batches": rec["board_batches"],
                    "p_fall": {i: n / d for i, n in sorted(rec["p_fall_n"].items())} if arm != "none" else {},
                    "p_late_climb": rec["late_n"] / d if arm != "none" else 0.0})
    return {"arm": arm, "card": card, "rule": rule, "climbs": climbs, "lags_s": list(lags), "batches": batches,
            "batch_draws": batch_draws, "seeds": [seed + b for b in range(batches)], "processes": out,
            "off_lattice": cal["off_lattice"], "first_skipped": cal["first_skipped"],
            "calibration_first_process": cal["first_process"], "falls_observed": len(cal["fall_obs"]),
            "oracle_fit": ({"period_ms": oracle[1], "period_sd_ms": math.sqrt(oracle[2][1][1])} if oracle else None)}


def lattice_rule(procs, card, pred_seq, min_later=3):
    """DT-L: over the eligible gaps (A1-1) of the processes after the one holding the calibration's first fall."""
    first = pred_seq.get("calibration_first_process")
    tp = fn = fp = tn = 0
    later = []
    if first is not None:
        for pi in range(first + 1, len(procs)):
            p = procs[pi]
            pf = pred_seq["processes"][pi]["p_fall"]
            for g in gaps(p, card):
                if not g["eligible"]:
                    continue
                pr = pf.get(g["i"], 0.0) >= 0.5
                if g["fell"]:
                    later.append({"run": p["run"], "gap": g["i"], "p": round(pf.get(g["i"], 0.0), 3)})
                tp += pr and g["fell"]
                fn += (not pr) and g["fell"]
                fp += pr and not g["fell"]
                tn += (not pr) and not g["fell"]
    n_later = tp + fn
    sens = tp / n_later if n_later else None
    ppv = tp / (tp + fp) if (tp + fp) else None
    if n_later < min_later:
        verdict = f"NOT SCORED ({n_later} later falls < {min_later})"
    else:
        verdict = "PASS" if (sens >= DT.SENS_LINE and ppv is not None and ppv >= DT.PPV_LINE) else "FAIL"
    return {"rule": "DT-L (A1)", "first_process": first, "later_falls": n_later, "predicted_and_fell": tp, "missed": fn,
            "predicted_no_fall": fp, "neither": tn, "sensitivity": round(sens, 3) if sens is not None else None,
            "ppv": round(ppv, 3) if ppv is not None else None, "verdict": verdict, "later": later}


def mc_se(vals):
    """The Monte Carlo standard error of a figure read on the pooled draws, from its batch figures."""
    if len(vals) < 2:
        return None
    m = sum(vals) / len(vals)
    return math.sqrt(sum((v - m) ** 2 for v in vals) / (len(vals) - 1)) / math.sqrt(len(vals))


# ------------------------------------------------------------------ self-test
def _proc(run, ghz, t0=0, gap=2, kern=366, clear=True, in_scope=True):
    L = [(-1, t0 + 150, t0 + 168, 0.59)]
    s = t0 + 168 + gap
    for i, g in enumerate(ghz):
        L.append((i, s, s + kern, g))
        s += kern + gap
    p = {"run": run, "t0": t0, "t1": L[-1][2] + 20, "launches": L}
    rs = dict(NO_RING, dump=True, complete=True, pstat=4, clear=clear, steps_to_boot=0 if clear else 3)
    p["a1"] = {"block": "BURST", "ring": rs, "clear": clear, "alarm": False, "in_scope": in_scope}
    return p


def selftest():
    res = {}
    card = "a2"
    # T1 (A1-1): falls after a full-clock launch count in any process; after a dither launch only in a clear process
    g16 = [0.80] * 16
    pa = _proc("A", g16[:6] + [0.60, 0.60] + g16[8:], clear=False)
    pb = _proc("B", g16[:6] + [0.72, 0.60] + g16[8:], clear=True)
    pc = _proc("C", g16[:6] + [0.72, 0.60] + g16[8:], clear=False)
    pd = _proc("D", g16[:6] + [0.75, 0.40] + g16[8:], clear=True)
    mark([pd], {"D": dict(NO_RING, dump=True, complete=True, pstat=4, clear=True)}, BURST_BLOCKS, {"D": {"block": "BURST"}})
    fa = [g["i"] for g in gaps(pa, card) if g["fell"]]
    fb = [g["i"] for g in gaps(pb, card) if g["fell"]]
    fc = [g["i"] for g in gaps(pc, card) if g["fell"]]
    res["T1_fall_rule"] = {"full_clock_nonclear": fa, "dither_clear": fb, "dither_nonclear": fc, "alarm_in_scope": pd["a1"]["in_scope"],
                           "ok": fa == [7] and fb == [8] and fc == [] and pd["a1"]["in_scope"] is False}
    # T2 (A1-2): the ring's classification
    e = lambda ts, st, mhz: {"ts": ts, "kind": "pstat", "throttle_state": st, "mhz": mhz}  # noqa: E731
    prev = [e(10, 0, 600)]
    r_clear = classify_ring(prev, [e(10, 0, 600), e(20, 1, 700), e(30, 1, 800), e(40, 2, 700), e(50, 0, 600)])
    r_step = classify_ring(prev, [e(10, 0, 600), e(20, 1, 700), e(30, 2, 600), e(50, 0, 600)])
    r_alarm = classify_ring(prev, [e(10, 0, 600), e(30, 3, 300), e(40, 1, 600)])
    r_gap = classify_ring(prev, [e(20, 1, 700), e(50, 0, 600)])
    r_none = classify_ring(prev, None)
    res["T2_ring"] = {"clear": r_clear["clear"], "step": r_step["clear"], "alarm": (r_alarm["clear"], r_alarm["alarm_records"]),
                      "not_reaching_back": r_gap["clear"], "no_dump": r_none["clear"],
                      "ok": r_clear["clear"] and not r_step["clear"] and not r_alarm["clear"] and r_alarm["alarm_records"] == 1
                      and not r_gap["clear"] and not r_none["clear"] and r_clear["power_idle"] == 1}
    # T3 (A1-2): the calibration's first fall must lie in a clear process
    procs, truth, _ = DT._synth(card, 160, 1003, "chain")
    for p in procs:
        p["a1"] = {"block": "BURST", "ring": dict(NO_RING, clear=True), "clear": True, "alarm": False, "in_scope": True}
    first_fall = min(pi for pi, _ in truth)
    procs[first_fall]["a1"]["clear"] = False
    cal = calibration(procs, card, "a1")
    second = min(pi for pi, _ in truth if pi != first_fall)
    res["T3_first_fall"] = {"first_fall_process": first_fall, "calibration_first": cal["first_process"],
                            "skipped": len(cal["first_skipped"]),
                            "ok": cal["first_process"] == second and len(cal["first_skipped"]) >= 1
                            and all(x["process"] == first_fall for x in cal["first_skipped"])}
    # T4: with dipterm's rule, climbs, draws and seed, predict() is dipterm.predict draw for draw (both cards, every arm)
    t4 = {}
    for cd in ("a2", "c0"):
        procs, _, _ = DT._synth(cd, 40, 1100 if cd == "a2" else 1200, "chain")
        for p in procs:
            p["a1"] = {"block": "BURST", "ring": dict(NO_RING, clear=True), "clear": True, "alarm": False, "in_scope": True}
        dp = {p["run"]: {600.0: 20.0, 700.0: 11.0} for p in procs}
        for arm in ("count", "seq", "oracle"):
            ref = DT.predict(procs, cd, {}, dp, arm, draws=DT.MC_DRAWS, seed=DT.SEED)
            got = predict(procs, cd, {}, dp, arm, batches=1, batch_draws=DT.MC_DRAWS, seed=DT.SEED, rule="registered",
                          climbs="registered", lags=(DT.BOARD_LAG_S,))
            same = all(abs(a["clock_deficit_mhz"] - b["clock_deficit_mhz"]) < 1e-12 and abs(a["board_deficit_w"] - b["board_deficit_w"][0]) < 1e-12
                       and a["p_fall"] == b["p_fall"] and a["p_late_climb"] == b["p_late_climb"]
                       for a, b in zip(ref["processes"], got["processes"]))
            t4[f"{cd}_{arm}"] = same
    res["T4_registered_reproduced"] = dict(t4, ok=all(t4.values()))
    # T5: on sessions whose processes are all clear and whose falls are full-clock, A1's DT-N is the registered DT-N
    t5 = []
    for s in range(6):
        procs, _, _ = DT._synth(card, 160, 1500 + s, "chain")
        for p in procs:
            p["a1"] = {"block": "BURST", "ring": dict(NO_RING, clear=True), "clear": True, "alarm": False, "in_scope": True}
        a, r = count_rule(procs, card), DT.count_rule(procs, card)
        t5.append(all(a[k] == r[k] for k in ("eligible_gaps", "expected", "band_95", "observed_falls", "verdict")))
    res["T5_dtn_regression"] = {"sessions": len(t5), "same": sum(t5), "ok": all(t5)}
    # T6 (A1-5): one card-0 fall in the middle of a window costs (f - 600)(P + c7) + (f - 700)(c8 - c7) after the fall
    p = {"run": "x", "t0": 0, "t1": 6300, "launches": [(-1, 150, 168, 0.59)] + [(i, 171 + i * 369, 171 + i * 369 + 366, 0.8) for i in range(16)]}
    pp = prep(p, "c0")
    zz = DT.gaps(p, "c0")[3]
    t_ref = 0.5 * (zz["lo"] + zz["hi"])
    P0 = DT.PERIOD_PRIOR_MS["c0"][0]
    lows, fell, c0 = simulate(pp, t_ref, P0, 800.0, CLIMB_START_S["c0"], CLIMB_FALL_S["c0"])
    fall_lows = [x for x in lows if x[0] >= t_ref - 1e-9]
    c7f, c8f = CLIMB_FALL_S["c0"]
    want = [(t_ref, t_ref + P0 + c7f * 1000.0, 600.0), (t_ref + P0 + c7f * 1000.0, t_ref + P0 + c8f * 1000.0, 700.0)]
    ok6 = fell[:1] == [zz["i"]] and len(fall_lows) >= 2 and all(abs(a[0] - b[0]) < 1e-6 and abs(a[1] - b[1]) < 1e-6 and a[2] == b[2]
                                                                 for a, b in zip(fall_lows[:2], want))
    res["T6_card0_fall_climb"] = {"fell": fell[:1], "segments_s": [round((b - a) / 1000.0, 4) for a, b, _ in fall_lows[:2]],
                                  "want_s": [round(P0 / 1000.0 + c7f, 4), round(c8f - c7f, 4)], "ok": ok6}
    # T7 (A1-6): a fall in the middle of the window costs the board the same at either lag; one at its end does not
    lows_mid = [(3000.0, 4120.0, 600.0)]
    lows_end = [(6100.0, 7220.0, 600.0)]
    _, bm = deficits(p, lows_mid, 800.0, {600.0: 20.0}, LAGS)
    _, be = deficits(p, lows_end, 800.0, {600.0: 20.0}, LAGS)
    res["T7_lag_arm"] = {"mid": [round(x, 4) for x in bm], "end": [round(x, 4) for x in be],
                         "ok": abs(bm[0] - bm[1]) < 1e-9 and be[1] > be[0]}
    # T8 (A1-4): 8 batches of 500; the pooled deficit is the batches' mean and the standard error is finite
    procs, _, _ = DT._synth(card, 12, 1700, "chain")
    for p in procs:
        p["a1"] = {"block": "BURST", "ring": dict(NO_RING, clear=True), "clear": True, "alarm": False, "in_scope": True}
    pr = predict(procs, card, {}, None, "count")
    x = pr["processes"][3]
    res["T8_batches"] = {"batches": len(x["clock_batches"]), "draws": MC_BATCHES * MC_BATCH_DRAWS,
                         "se_mhz": round(mc_se(x["clock_batches"]), 4),
                         "ok": len(x["clock_batches"]) == MC_BATCHES and abs(x["clock_deficit_mhz"] - sum(x["clock_batches"]) / MC_BATCHES) < 1e-12
                         and mc_se(x["clock_batches"]) is not None}
    # T9 (A1-5): card 0's frozen climb equals climb-c0-a1.txt's pooled values, if that file sits beside this one
    f = os.path.join(HERE, "climb-c0-a1.txt")
    if os.path.exists(f):
        pooled = json.load(open(f))["card0"]["pooled_E114_E174"]
        res["T9_climb_file"] = {"file": [pooled["c7_s"], pooled["c8_s"]], "frozen": list(CLIMB_FALL_S["c0"]),
                                "ok": [pooled["c7_s"], pooled["c8_s"]] == list(CLIMB_FALL_S["c0"])}
    res["ok"] = all(v.get("ok", True) for v in res.values() if isinstance(v, dict))
    return res


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        r = selftest()
        print(json.dumps(r, indent=1, sort_keys=True))
        sys.exit(0 if r["ok"] else 1)
    print(__doc__)
