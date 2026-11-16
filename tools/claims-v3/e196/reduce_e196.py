#!/usr/bin/env python3
"""E196's registered reduction (Q185, lane reg-e196, Sun 15 Nov 2026, before any datum): the proposal's reduce_x14.py
(request 1113-x14-zeroshare, sha256 c86892e134b5a037770db99c38201d7cce9bc5eb066884096347241d474eaabc, committed byte for
byte as proposal/src/reduce_x14.py) with ONE change, registered in E196.md section 7:

    --readback-none-ok   a run all of whose launch records carry "readback": "none" (a run of the lab's unchanged
                         sparsity host, which reads no C back on file tiles: E196's pass runs and train-block anchors)
                         is not set aside for the C read-back gate; every other gate applies as written; the output then
                         carries "readback_gate" (how many runs it exempted). Without the flag this program is
                         reduce_x14.py: the same output, byte for byte (E196's desk check).

Every other line below is reduce_x14.py's.

The registered reduction of request 1113-x14-zeroshare (standard library only).

    python3 -B reduce_x14.py OUT [--gen DIR] [--json x14.json] [--leak 0.1994] [--rail-tau 1.05] [--rail-delay 0.26]
                             [--drop-pass0] [--min-passes 5]

OUT holds a session (run_session.sh): telemetry.jsonl (the lab's sampler, 10 Hz), runs.jsonl (one X14 record per pass
launch, with arm, pass, seq, role, approach), train.jsonl (one X14 record per train launch, with train, process and
order), checks.jsonl (the read-backs of C), marks.jsonl (device processes and idle stretches); DIR (default OUT/gen)
the arm and train tables make_x14.py wrote (arms.json).

The dip rule (the lab's E82 amendment A2), over the session's samples in time order: board sample i is dropped when
board_w[i] < min(board_w[i-2], board_w[i+2]) - 4.0 W. Nothing is set aside for a dip; the sample counts below are of
kept samples.

Per pass run (one device process of 4 s): the burst starts at its first launch (t0).
  board  B = mean of board_w over [t0 + 1, t0 + 3) s; the idle bracket I = mean over [t0 - 1.2, t0 - 0.2) s;
         S = B - I - leak x (die reading in the window - die reading in the bracket): W over idle (the E78 footing);
         Bc = B - leak x (die reading in the window - 58 C): the leak-corrected busy mean;
  rail   the core (minion) rail is the PMIC's running average, first order (tau ~1.05 s on the reference card) and one
         meter pass late: its true mean over a window [a, b) is mean(r) + tau x (r(b) - r(a)) / (b - a) (r at the ends
         averaged over 0.3 s), read --rail-delay later; the same over the board's window and over the idle bracket
         gives rail S, W, with the leakage correction scaled by 0.85; its volts from the same samples;
  rate   multiply-add ops completed inside the board window: every launch overlapping it, prorated by overlap;
         ops a second = that / 2 s; issued multiply-adds = ops x the arm's issued multiply-adds per op (arms.json).
Gates (each run, all registered; a failed run is set aside and counted; the E78 frame's gates): at least 15 kept board
samples in the window and 8 in the bracket, no gap over 0.5 s between kept window samples; launches cover at least
0.97 of the window; every sample in the window at the pass's clock; rail volts within 3 mV of the pass median; cycles
per op within 0.5 % of 546 (no row mask, or every row enabled) or 544 (a row masked); tensor_errors 0 and ok on every
launch; both read-backs of C (after the first and the last launch) ok; the approach on protocol.
A pass: its anchor (K.pi) runs first and last; drift = last - first S. The pass is kept when both anchors pass their
gates and |drift| <= 0.3 W; when one anchor fails a gate and the other passes, the pass is kept with drift unmeasured
(flagged); when both fail, or |drift| > 0.3 W, it is set aside. Every pass counts (each starts with two unrecorded
burn-in runs); --drop-pass0 sets the first aside as a warm-up. A result over fewer than --min-passes kept passes is
flagged provisional.
Per pass: D = Bc(arm) - Bc(its reference) (the primary form: the difference of leak-corrected busy means, the lab's
E60 form) and D_bracketed = S(arm) - S(reference); per op, D_pJ = S(arm)/rate(arm) - S(ref)/rate(ref) (board, pJ an
op over idle), which is the form to compare where two arms run at different rates. The unit of replication is the
pass: means, standard errors and 95 % intervals over the kept passes (t quantiles). Every result is also given at leak
slopes 0 and 0.3803 W/C (the E78 sensitivity arms).
Derived, per pass then over passes: per op and per issued multiply-add (pJ, board and rail); electrons per op through
the core rail (rail energy / e / rail volts) and through the 12 V input (board energy / e / 12 V); the issue ladders'
least-squares slopes per issued micro-op (pJ, from S per op) and the steps between rungs; spacing contrasts; field
prices per designed operand flip and per all designed flips (operand + the accumulator estimates of arms.json, mid-
launch); zero shares (S(Z) - S(zeros)) / (S(random) - S(zeros)) and r = (share - (1 - g)) / g with g the arm's gated
lane-micro-op fraction; the ties (random per multiply-add, ones, pi, the A-zero tile).

Trains (the lab's E182 statistic): a launch's reading is the mean of the kept board samples in [its start + 170 ms,
its end] (at least 2); a quad (launches 4q+1 to 4q+4, q = 0, 1, 2; launch 0 settles) is sigma (L2 + L3 - L1 - L4) / 2,
sigma = +1 in an SFFS process and -1 in an FSSF one, so every quad reads D(F) - D(S); a process's value is the mean of
its complete quads; a unit is processes 2j and 2j + 1 (one of each order), the mean of their values when both exist;
the train's estimate is the mean over units with the 95 % interval t(0.975, n - 1) sd / sqrt(n); fewer than 8 units:
not scored. A process with a launch not ok, a failed read-back of C, a launch off its order, or a STOP mark during it
gives no value. Raw board watts: no leak correction, no zeros subtracted (both kinds share one thermal state). Per op:
the estimate over the mean ops a second of the train's launches.
"""
import argparse
import bisect
import json
import math
import os
import statistics as st

QE = 1.602176634e-19
T975 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228,
        11: 2.201, 12: 2.179, 13: 2.160, 14: 2.145, 15: 2.131, 16: 2.120, 17: 2.110, 18: 2.101, 19: 2.093, 20: 2.086}
LEAK_ARMS = (0.0, 0.3803)
T_REF = 58.0


def load_jsonl(path):
    out = []
    if not os.path.exists(path):
        return out
    for line in open(path, errors="ignore"):
        line = line.strip()
        if line.startswith("{") and line.endswith("}"):
            try:
                out.append(json.loads(line))
            except ValueError:
                pass
    return out


def avg(v):
    return sum(v) / len(v) if v else float("nan")


def summary(vals, min_n=1):
    v = [x for x in vals if x is not None and not math.isnan(x)]
    if not v:
        return None
    m = avg(v)
    if len(v) < 2:
        return {"mean": m, "n": len(v), "provisional": len(v) < min_n}
    se = st.stdev(v) / math.sqrt(len(v))
    t = T975.get(len(v) - 1, 2.0)
    return {"mean": m, "se": se, "ci95": [m - t * se, m + t * se], "n": len(v), "provisional": len(v) < min_n}


def lsq(xs, ys):
    n = len(xs)
    mx, my = avg(xs), avg(ys)
    sxx = sum((x - mx) ** 2 for x in xs)
    if n < 2 or sxx == 0:
        return None, None
    b = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx
    return b, my - b * mx


def expected_cycles(arm):
    m = arm["row_mask"]
    return 546.0 if m is None or int(m, 16) == 0xFFFF else 544.0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("out")
    parser.add_argument("--gen", default=None)
    parser.add_argument("--json", default=None, help="output file (default OUT/x14.json)")
    parser.add_argument("--leak", type=float, default=0.1994, help="board W per C of die reading (E78's fitted slope)")
    parser.add_argument("--rail-tau", type=float, default=1.05, help="the rail filter's time constant, s")
    parser.add_argument("--rail-delay", type=float, default=0.26, help="the rail reading's delay, s (one meter pass)")
    parser.add_argument("--drop-pass0", action="store_true")
    parser.add_argument("--min-passes", type=int, default=5)
    parser.add_argument("--readback-none-ok", action="store_true",
                        help="E196: a run whose launch records all carry readback 'none' (the lab's unchanged host) is not "
                             "set aside for the C read-back gate")
    a = parser.parse_args()
    gen = a.gen or os.path.join(a.out, "gen")
    manifest = json.load(open(os.path.join(gen, "arms.json")))
    table = {x["name"]: x for x in manifest["arms"]}
    trains = {t["name"]: t for t in manifest.get("trains", [])}
    tel = load_jsonl(os.path.join(a.out, "telemetry.jsonl"))
    recs = load_jsonl(os.path.join(a.out, "runs.jsonl"))
    trecs = load_jsonl(os.path.join(a.out, "train.jsonl"))
    checks = load_jsonl(os.path.join(a.out, "checks.jsonl"))
    marks = load_jsonl(os.path.join(a.out, "marks.jsonl"))
    tel.sort(key=lambda s: s.get("t_ms", 0))
    # the dip rule (E82 A2) over the session's samples
    bw = [s.get("board_w") for s in tel]
    dropped = 0
    keep_tel = []
    for i, s in enumerate(tel):
        w = bw[i]
        if not isinstance(w, (int, float)):
            continue
        if 2 <= i < len(tel) - 2 and isinstance(bw[i - 2], (int, float)) and isinstance(bw[i + 2], (int, float)) \
                and w < min(bw[i - 2], bw[i + 2]) - 4.0:
            dropped += 1
            continue
        keep_tel.append(s)
    T = [s["t_ms"] / 1000.0 for s in keep_tel]
    Tall = [s["t_ms"] / 1000.0 for s in tel]

    def window(t0, t1, kept=True):
        src, tt = (keep_tel, T) if kept else (tel, Tall)
        i, j = bisect.bisect_left(tt, t0), bisect.bisect_left(tt, t1)
        return src[i:j]

    def rail_w(s):
        v = s.get("sp", {}).get("minion_w")
        return v[0] if isinstance(v, list) else v

    def rail_mv(s):
        v = s.get("sp", {}).get("minion_mv")
        if v is None:
            v = s.get("die_mv", {}).get("minion")
        return v[0] if isinstance(v, list) else v

    def die(s):
        return s["temp_c"]["minshire"][0]

    def rail_true(t0, t1):
        d = a.rail_delay
        mid = [rail_w(s) for s in window(t0 + d, t1 + d, False) if rail_w(s) is not None]
        ra = [rail_w(s) for s in window(t0 + d - 0.15, t0 + d + 0.15, False) if rail_w(s) is not None]
        rb = [rail_w(s) for s in window(t1 + d - 0.15, t1 + d + 0.15, False) if rail_w(s) is not None]
        if not mid or not ra or not rb:
            return float("nan")
        return avg(mid) + a.rail_tau * (avg(rb) - avg(ra)) / (t1 - t0)

    chk = {}
    for c in checks:
        if c.get("train") is None:
            chk.setdefault((c.get("pass"), c.get("seq")), []).append(c)
    runs = {}
    for r in recs:
        if r.get("role") in ("burnin", "smoke"):
            continue
        runs.setdefault((r["pass"], r["seq"]), []).append(r)
    per_run, set_aside = [], []
    exempt = []   # E196: runs of the lab's unchanged host, not set aside for the C read-back gate (with --readback-none-ok)
    for (p, seq), rs in sorted(runs.items()):
        arm = rs[0]["arm"]
        t0 = min(x["t_start_ms"] for x in rs) / 1000.0
        why = []
        busy = window(t0 + 1.0, t0 + 3.0)
        idle = window(t0 - 1.2, t0 - 0.2)
        rail = window(t0 + 2.0, t0 + 4.0, False)
        if len(busy) < 15 or len(idle) < 8 or len(rail) < 8:
            set_aside.append({"pass": p, "seq": seq, "arm": arm, "gates_failed": ["too few samples (%d window, %d "
                                                                                  "bracket)" % (len(busy), len(idle))]})
            continue
        tb = [s["t_ms"] / 1000.0 for s in busy]
        gap = max([y - x for x, y in zip(tb, tb[1:])] + [tb[0] - (t0 + 1.0), (t0 + 3.0) - tb[-1]])
        if gap > 0.5:
            why.append("gap %.2f s in the window" % gap)
        cover = 0.0
        for x in rs:
            l0, l1 = x["t_start_ms"] / 1000.0, x["t_end_ms"] / 1000.0
            cover += max(0.0, min(l1, t0 + 3.0) - max(l0, t0 + 1.0))
        duty = cover / 2.0
        if duty < 0.97:
            why.append("duty %.3f" % duty)
        clocks = sorted({int(s.get("mhz", {}).get("minion", 0)) for s in busy})
        P = avg([s["board_w"] for s in busy])
        P0 = avg([s["board_w"] for s in idle])
        Tb = avg([die(s) for s in busy])
        Ti = avg([die(s) for s in idle])
        R1 = rail_true(t0 + 1.0, t0 + 3.0)
        R0 = rail_true(t0 - 1.2, t0 - 0.2)
        mv = avg([rail_mv(s) for s in rail if rail_mv(s) is not None])
        ops = 0.0
        for x in rs:
            l0, l1 = x["t_start_ms"] / 1000.0, x["t_end_ms"] / 1000.0
            ov = max(0.0, min(l1, t0 + 3.0) - max(l0, t0 + 1.0))
            if l1 > l0:
                ops += x["ops"] * ov / (l1 - l0)
        rate = ops / 2.0
        cpo = avg([x["cycles_per_op"] for x in rs if x.get("launch", 0) >= 0] or [x["cycles_per_op"] for x in rs])
        want = expected_cycles(table[arm])
        if abs(cpo - want) > 0.005 * want:
            why.append("cycles per op %.2f" % cpo)
        if any(x.get("tensor_errors", 0) for x in rs):
            why.append("tensor errors")
        if any(not x.get("ok", False) for x in rs):
            why.append("a launch not ok")
        cs = chk.get((p, seq), [])
        if a.readback_none_ok and all(x.get("readback") == "none" for x in rs):
            exempt.append([p, seq, arm])   # E196 (registered): the lab's unchanged host reads no C back on file tiles
        elif len(cs) < 2 or not all(c.get("ok") for c in cs):
            why.append("C read-back: %s" % [(c.get("zero_rows_bad"), c.get("live_rows_zero")) for c in cs])
        apr = rs[0].get("approach", {})
        if apr and not apr.get("on_protocol", True):
            why.append("approach off protocol")
        rec = {"pass": p, "seq": seq, "arm": arm, "role": rs[0].get("role"), "t0": t0, "P_busy_W": P, "P_idle_W": P0,
               "die_busy_C": Tb, "die_idle_C": Ti, "R_busy_W": R1, "R_idle_W": R0, "rail_mV": mv, "clocks": clocks,
               "ops_per_s": rate, "cycles_per_op": cpo, "duty": duty, "launches": len(rs), "gates_failed": why}
        (set_aside if why else per_run).append(rec)
    passes = sorted({r["pass"] for r in per_run} | {r["pass"] for r in set_aside if "pass" in r})
    passes = [p for p in passes if p < 100]
    keep = []
    for p in passes:
        R = [r for r in per_run if r["pass"] == p]
        if not R:
            keep.append({"pass": p, "anchor_drift_W": None, "kept": False, "why": "no run kept"})
            continue
        clock = st.median([c for r in R for c in r["clocks"]] or [0])
        mvm = st.median([r["rail_mV"] for r in R])
        for r in list(R):
            bad = []
            if r["clocks"] != [clock]:
                bad.append("clock %s" % r["clocks"])
            if abs(r["rail_mV"] - mvm) > 3.0:
                bad.append("rail %.1f mV" % r["rail_mV"])
            if bad:
                r["gates_failed"] = bad
                set_aside.append(r)
                per_run.remove(r)
        roles = {r["role"]: r for r in per_run if r["pass"] == p and r["arm"] == "K.pi"}
        first, last = roles.get("anchor_first"), roles.get("anchor_last")
        S_ = lambda r: r["P_busy_W"] - r["P_idle_W"] - a.leak * (r["die_busy_C"] - r["die_idle_C"])
        if first and last:
            drift = S_(last) - S_(first)
            ok, why = abs(drift) <= 0.3, "" if abs(drift) <= 0.3 else "anchor drift"
        elif first or last:
            drift, ok, why = None, True, "one anchor set aside: drift unmeasured"
        else:
            drift, ok, why = None, False, "both anchors set aside"
        if p == 0 and a.drop_pass0:
            ok, why = False, "warm-up (--drop-pass0)"
        keep.append({"pass": p, "anchor_drift_W": drift, "kept": ok, "why": why})
    kept = {k["pass"] for k in keep if k["kept"]}

    def reduce_at(leak):
        """per pass, per arm: S, Bc, rail S, rate, volts at one leak slope"""
        S = {}
        for r in per_run:
            if r["pass"] not in kept or r["role"] not in ("arm", "anchor_first", "anchor_last"):
                continue
            if r["role"] != "arm" and r["arm"] != "K.pi":
                continue
            v = {"S_W": r["P_busy_W"] - r["P_idle_W"] - leak * (r["die_busy_C"] - r["die_idle_C"]),
                 "Bc_W": r["P_busy_W"] - leak * (r["die_busy_C"] - T_REF),
                 "rail_S_W": r["R_busy_W"] - r["R_idle_W"] - leak * 0.85 * (r["die_busy_C"] - r["die_idle_C"]),
                 "ops_per_s": r["ops_per_s"], "rail_mV": r["rail_mV"]}
            d = S.setdefault(r["arm"], {}).setdefault(r["pass"], [])
            d.append(v)
        out = {}
        for arm, byp in S.items():
            for p, vs in byp.items():
                out.setdefault(arm, {})[p] = {k: avg([v[k] for v in vs]) for k in vs[0]}
        return out

    res = {"request": "1113-x14-zeroshare", "passes": keep, "set_aside": set_aside, "dips_dropped": dropped,
           "leak_W_per_C": a.leak, "arms": {}, "derived": {}, "trains": {}, "sensitivity": {}}
    if a.readback_none_ok:   # E196: which runs the C read-back gate did not apply to (the lab's unchanged host)
        res["readback_gate"] = {"rule": "E196: runs whose launch records carry readback 'none' are not set aside for the C "
                                        "read-back gate", "exempt_runs": len(exempt), "exempt": exempt}
    rows = lambda arm: bin(int(table[arm]["row_mask"], 16)).count("1") if table[arm]["row_mask"] else 16
    uops = lambda arm: table[arm]["counts"]["issued_uops"]

    def derive(S, full=True):
        def per_pass(fn):
            out = []
            for p in sorted(kept):
                try:
                    v = fn(p)
                except (KeyError, ZeroDivisionError, TypeError):
                    v = None
                if v is not None:
                    out.append(v)
            return summary(out, a.min_passes)
        g = lambda arm, p, k="S_W": S[arm][p][k]
        epo = lambda arm, p, k="S_W": S[arm][p][k] / S[arm][p]["ops_per_s"] * 1e12     # pJ an op over idle
        arms_out = {}
        for arm, t in table.items():
            if not t.get("in_passes", True):
                continue
            macs = t["counts"]["issued_macs"]
            rec = {"S_W": per_pass(lambda p: g(arm, p)), "ops_per_s": per_pass(lambda p: g(arm, p, "ops_per_s"))}
            if full:
                rec.update({"rail_S_W": per_pass(lambda p: g(arm, p, "rail_S_W")),
                            "pJ_per_op_board": per_pass(lambda p: epo(arm, p)),
                            "pJ_per_op_rail": per_pass(lambda p: epo(arm, p, "rail_S_W")),
                            "electrons_rail_per_op": per_pass(lambda p: g(arm, p, "rail_S_W") / g(arm, p, "ops_per_s") /
                                                              (QE * g(arm, p, "rail_mV") / 1000.0)),
                            "electrons_12V_per_op": per_pass(lambda p: g(arm, p) / g(arm, p, "ops_per_s") / (QE * 12.0))})
                if macs:
                    rec["pJ_per_issued_mac_board"] = per_pass(lambda p: g(arm, p) / (g(arm, p, "ops_per_s") * macs) * 1e12)
            if t["ref"]:
                ref = t["ref"]
                rec["D_W"] = per_pass(lambda p: g(arm, p, "Bc_W") - g(ref, p, "Bc_W"))
                rec["D_bracketed_W"] = per_pass(lambda p: g(arm, p) - g(ref, p))
                rec["D_pJ_per_op_board"] = per_pass(lambda p: epo(arm, p) - epo(ref, p))
                if full:
                    rec["D_rail_W"] = per_pass(lambda p: g(arm, p, "rail_S_W") - g(ref, p, "rail_S_W"))
            arms_out[arm] = rec
        d = {}
        for tile, lad in (("H", ["I.H.m0000", "I.H.m000F", "I.H.m00FF", "I.H.m0FFF", "I.H.full"]),
                          ("Z", ["I.Z.m0000", "I.Z.m000F", "I.Z.m00FF", "I.Z.m0FFF", "I.Z.full"]),
                          ("R", ["I.R.m0000", "I.R.m00FF", "I.R.full"])):
            d["ladder_%s_S_W" % tile] = {x: per_pass(lambda p, x=x: g(x, p)) for x in lad}
            for i in range(len(lad) - 1):
                x0, x1 = lad[i], lad[i + 1]
                d["ladder_%s_step_%s_to_%s_W" % (tile, x0, x1)] = per_pass(lambda p, x0=x0, x1=x1: g(x1, p, "Bc_W") - g(x0, p, "Bc_W"))
            mid = lad[1:4] if tile != "R" else lad
            d["ladder_%s_slope_pJ_per_issued_uop" % tile] = per_pass(
                lambda p, mid=mid: lsq([uops(x) for x in mid], [epo(x, p) for x in mid])[0])
            d["ladder_%s_slope_W_per_row" % tile] = per_pass(
                lambda p, mid=mid: lsq([rows(x) for x in mid], [g(x, p, "Bc_W") for x in mid])[0])
        def held_line(p):
            xs = [uops(x) for x in ("I.H.m000F", "I.H.m00FF", "I.H.m0FFF")]
            ys = [epo(x, p) for x in ("I.H.m000F", "I.H.m00FF", "I.H.m0FFF")]
            return lsq(xs, ys)
        d["held_line_at_0_minus_mask0_pJ_per_op"] = per_pass(lambda p: held_line(p)[1] - epo("I.H.m0000", p))
        d["held_full_minus_line_at_512_pJ_per_op"] = per_pass(lambda p: epo("I.H.full", p) - (held_line(p)[1] + 512 * held_line(p)[0]))
        d["held_ladder_middle_step_ratio"] = per_pass(
            lambda p: (g("I.H.m0FFF", p, "Bc_W") - g("I.H.m00FF", p, "Bc_W")) / (g("I.H.m00FF", p, "Bc_W") - g("I.H.m000F", p, "Bc_W")))
        d["zero_ladder_first_step_ratio"] = per_pass(
            lambda p: (g("I.Z.m000F", p, "Bc_W") - g("I.Z.m0000", p, "Bc_W")) / (g("I.Z.m00FF", p, "Bc_W") - g("I.Z.m000F", p, "Bc_W")))
        d["lanes_clock_plus_accumulator_writes_per_mac_board_pJ"] = per_pass(
            lambda p: (epo("I.H.full", p) - epo("I.Z.full", p)) / 4096)
        if full:
            d["lanes_clock_plus_accumulator_writes_per_mac_rail_pJ"] = per_pass(
                lambda p: (epo("I.H.full", p, "rail_S_W") - epo("I.Z.full", p, "rail_S_W")) / 4096)
        d["data_part_per_issued_mac_random_board_pJ"] = per_pass(lambda p: (epo("I.R.full", p) - epo("I.H.full", p)) / 4096)
        for x in ("I.H.m0F0F", "I.H.m3333", "I.H.m5555"):
            d["spread_%s_minus_I.H.m00FF_W" % x] = per_pass(lambda p, x=x: g(x, p, "Bc_W") - g("I.H.m00FF", p, "Bc_W"))
        d["msk_null_I.H.mFFFF_minus_I.H.full_pJ_per_op"] = per_pass(lambda p: epo("I.H.mFFFF", p) - epo("I.H.full", p))
        for x in ("I.H.m0000", "I.R.m0000", "Z.a0.m0000"):
            d["mask0_%s_minus_zero_W" % x] = per_pass(lambda p, x=x: g(x, p, "Bc_W") - g("I.Z.m0000", p, "Bc_W"))
        d["b_through_gated_micro_ops_W"] = per_pass(
            lambda p: (g("Z.a0", p, "Bc_W") - g("I.Z.full", p, "Bc_W")) - (g("Z.a0.m0000", p, "Bc_W") - g("I.Z.m0000", p, "Bc_W")))
        for arm in ("F.Bs", "F.Be", "F.Ae"):
            t = table[arm]
            side = "a" if arm[2] == "A" else "b"
            flips = t["counts"]["issued_%s_all" % side]
            rc = table[t["ref"]]["counts"]
            acc = (t["counts"]["acc_mid_c_in_flips_est"] + t["counts"]["acc_mid_result_flips_est"]) - \
                (rc["acc_mid_c_in_flips_est"] + rc["acc_mid_result_flips_est"])
            d["field_%s_fJ_per_operand_flip_board" % arm] = per_pass(
                lambda p, arm=arm, t=t, flips=flips: (epo(arm, p) - epo(t["ref"], p)) / flips * 1e3)
            d["field_%s_fJ_per_flip_all_board" % arm] = per_pass(
                lambda p, arm=arm, t=t, n=flips + acc: (epo(arm, p) - epo(t["ref"], p)) / n * 1e3)
            if full:
                d["field_%s_electrons_per_operand_flip_rail" % arm] = per_pass(
                    lambda p, arm=arm, t=t, flips=flips: (epo(arm, p, "rail_S_W") - epo(t["ref"], p, "rail_S_W")) * 1e-12 /
                    flips / (QE * g(arm, p, "rail_mV") / 1000.0))
        share = lambda z, p: (g(z, p) - g("I.Z.full", p)) / (g("I.R.full", p) - g("I.Z.full", p))
        for z in ("Z.a50", "Z.b50", "Z.ab50"):
            gf = table[z]["counts"]["gated_fraction"]
            d["share_%s" % z] = per_pass(lambda p, z=z: share(z, p))
            d["r_from_%s" % z] = per_pass(lambda p, z=z, gf=gf: (share(z, p) - (1 - gf)) / gf)
        d["tie_random_pJ_per_mac_board"] = per_pass(lambda p: g("I.R.full", p) / (g("I.R.full", p, "ops_per_s") * 4096) * 1e12)
        d["tie_zeros_S_W"] = per_pass(lambda p: g("I.Z.full", p))
        d["tie_pi_S_W"] = per_pass(lambda p: g("K.pi", p))
        d["tie_ones_D_W"] = per_pass(lambda p: g("K.ones", p, "Bc_W") - g("I.Z.full", p, "Bc_W"))
        d["tie_random_D_W"] = per_pass(lambda p: g("I.R.full", p, "Bc_W") - g("I.Z.full", p, "Bc_W"))
        d["tie_a_zero_D_W"] = per_pass(lambda p: g("Z.a0", p, "Bc_W") - g("I.Z.full", p, "Bc_W"))
        d["tie_sparse50_D_W"] = per_pass(lambda p: g("Z.ab50", p, "Bc_W") - g("I.Z.full", p, "Bc_W"))
        d["tie_b_sign_D_W"] = per_pass(lambda p: g("F.Bs", p, "Bc_W") - g("F.B0", p, "Bc_W"))
        return arms_out, d

    S = reduce_at(a.leak)
    res["arms"], res["derived"] = derive(S)
    for lk in LEAK_ARMS:
        ao, dd = derive(reduce_at(lk), full=False)
        res["sensitivity"]["leak_%g" % lk] = {"arms_D_W": {k: v.get("D_W") for k, v in ao.items()}, "derived": dd}

    # ------------------------------------------------------------ trains
    stop_t = []   # the STOP file's time (run_block.py and stopwatch.py write {"by", "why", "t_ms"}; by hand: its mtime)
    sp = os.path.join(a.out, "STOP")
    if os.path.exists(sp):
        try:
            stop_t.append(json.loads(open(sp).readline())["t_ms"] / 1000.0)
        except (ValueError, KeyError, TypeError):
            stop_t.append(os.path.getmtime(sp))
    for name, t in trains.items():
        tr = [r for r in trecs if r.get("train") == name and r.get("role") == "train"]
        procs = {}
        for r in tr:
            procs.setdefault(r["process"], []).append(r)
        tchk = {}
        for c in checks:
            if c.get("train") == name and c.get("role") == "train":
                tchk.setdefault(c["process"], []).append(c)
        values, notes, rates = {}, [], []
        for k, rs in sorted(procs.items()):
            rs.sort(key=lambda r: r["launch"])
            order = rs[0].get("order")
            sig = 1.0 if order == "SFFS" else -1.0
            want = [order[0], order[0]] + [order[(n - 1) % 4] for n in range(1, len(rs) - 1)]
            t0, t1 = rs[0]["t_start_ms"] / 1000.0, rs[-1]["t_end_ms"] / 1000.0
            bad = []
            if [r["kind"] for r in rs] != want:
                bad.append("off its order")
            if not all(r.get("ok") for r in rs):
                bad.append("a launch not ok")
            cs = tchk.get(k, [])
            if len(cs) < 2 or not all(c.get("ok") for c in cs):
                bad.append("C read-back")
            if any(t0 <= x <= t1 + 1.0 for x in stop_t):
                bad.append("a stop during it")
            if bad:
                notes.append({"process": k, "why": bad})
                continue
            L = {}
            for r in rs:
                if r["launch"] < 1:
                    continue
                w = [s["board_w"] for s in window(r["t_start_ms"] / 1000.0 + 0.17, r["t_end_ms"] / 1000.0 + 1e-6)]
                if len(w) >= 2:
                    L[r["launch"]] = avg(w)
                if r["wall_s"] > 0:
                    rates.append(r["ops"] / r["wall_s"])
            quads = []
            for q in range(3):
                n = [4 * q + 1, 4 * q + 2, 4 * q + 3, 4 * q + 4]
                if all(x in L for x in n):
                    quads.append(sig * (L[n[1]] + L[n[2]] - L[n[0]] - L[n[3]]) / 2.0)
            if quads:
                values[k] = avg(quads)
        units = []
        for j in range(0, max(list(procs) + [0]) + 1, 2):
            v = [values[x] for x in (j, j + 1) if x in values]
            if len(v) == 2:
                units.append(avg(v))
        est = summary(units)
        rate = avg(rates) if rates else float("nan")
        out = {"F": t["F"], "S": t["S"], "processes": len(procs), "processes_with_value": len(values), "units": len(units),
               "scored": len(units) >= 8, "D_W": est, "excluded": notes, "ops_per_s": rate}
        if est and rate == rate and rate > 0:
            out["D_pJ_per_op_board"] = {k: (v / rate * 1e12 if isinstance(v, float) else [x / rate * 1e12 for x in v])
                                        for k, v in est.items() if k in ("mean", "se", "ci95")}
        anc = sorted([r for r in per_run if r["arm"] == "K.pi" and r["role"] in ("train_anchor_first", "train_anchor_last")
                      and any(x.get("train") == name and x.get("pass") == r["pass"] for x in tr)], key=lambda r: r["seq"])
        if len(anc) >= 2:
            S_ = lambda r: r["P_busy_W"] - r["P_idle_W"] - a.leak * (r["die_busy_C"] - r["die_idle_C"])
            out["anchor_drift_W"] = S_(anc[-1]) - S_(anc[0])
        res["trains"][name] = out
    path = a.json or os.path.join(a.out, "x14.json")
    json.dump(res, open(path, "w"), indent=1)
    print("passes kept %s; runs %d kept, %d set aside; %d dips dropped -> %s" % (sorted(kept), len(per_run),
                                                                                 len(set_aside), dropped, path))
    for k, v in res["derived"].items():
        if isinstance(v, dict) and "mean" in v:
            print("%-56s %s" % (k, " ".join("%s=%.4g" % (kk, vv) for kk, vv in v.items() if isinstance(vv, (int, float)))))
    for k, v in res["trains"].items():
        print("train %s: units %d scored %s D %s" % (k, v["units"], v["scored"], v["D_W"]))


if __name__ == "__main__":
    main()
