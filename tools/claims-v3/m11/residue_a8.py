#!/usr/bin/env python3
"""M11's dated amendment A8 (Fri 6 Nov 2026, before any M11 hold): the smoke's residue at G0-A6's window, predicted by M6's frozen step
response on the planned smoke, that prediction checked on every committed M11-family session, and A8's rule between the two remedies the
round A critic named (a longer R0, or A6-2's line referred to the predicted residue). Desk only; it reads committed files and writes one
JSON file. Post hoc: every session it reads has been seen.

  M6       docs/reports/data/2026-11-02-q137m-model/m6.json (6a713a9f) > heat: the step response F(t) = 1 - sum w_i exp(-t / tau_i)
           (tau 1.005, 15.98, 138.2, 1500 s) and aifoundry3's steady 0.9 C per board W, frozen; driven here by a MEASURED board trace,
           open loop, as Q138(t)'s arm A drives its chain: the 34-sensor mean's excess over F0 is 0.9 sum_i w_i x_i, each x_i following
           the board's excess over P0 with time constant tau_i (exact for a straight line between samples; a gap between the two passes
           filled by the straight line across it).
  F0, P0   A6-1's floor: the 34-sensor mean (E97's code_to_c on the 34 raw codes) over the first 3 s of the smoke pass's samples, and the
           board W over the same samples.
  residue  A6-2's: the 34-sensor mean over R0's last 120 s, less F0 (the window [t_R0 + L - 120, t_R0 + L), L the R0 length).
  miss     the measured residue less M6's prediction from the same session's own committed traces.
  sessions the four committed aifoundry3 sessions with a smoke pass and then a fixed R0 in the measured pass, every one with the raw codes:
           E144 (R0 8 min), E154, E166, E176 (R0 5 min); E89 and E97 are not used (E97's R0 is slope-ended 2.3 h after its smoke; E89's
           measured pass holds no rest marks).
  E181     M11's session 2 runs E176's smoke unchanged (tools/claims-v3/e176/run_e176.py DESIGNS["smoke"] and stoptests(), carried into
           E181's kit), so the planned smoke's board trace is E176's committed one, smoke and R0 (its measured pass, refused at G0 after R0).
  (a)      a longer R0: the longest whole minute that leaves L2's start at least 60 s inside run_e176.py's rule ("a hold does not start with
           less than its length + 30 s left") on E176's committed session timeline (T0 17:21:15 PST, R0's start 79.251 s later, the measured
           pass's deadline T0 + 4,500 s), the other rests and holds unchanged; its residue predicted on E176's trace extended past R0's
           end with the board's excess following the predicted die (primary) or held at its last 30 s (beside).
  (b)      A6-2's line referred to the predicted residue: R0's room less F0 less the frozen prediction at or under 0.50 C.
  the rule A8-R: the remedy with the smaller chance of refusing a settled card, from the committed misses at the 300 s window (a normal with
           their mean and sd, n - 1): P = 1 - Phi((line - prediction - mean) / sd); within 0.5 percentage points, (a), which changes no gate.
           The empirical count of misses over each margin is printed beside.

    python3 -B tools/claims-v3/m11/residue_a8.py <lab repo top> <out.json>
SPDX-License-Identifier: Apache-2.0
"""
import gzip
import hashlib
import json
import math
import os
import sys
import time

sys.dont_write_bytecode = True
G_TS, H_TS, CAL5 = 57400, 249400, 4096          # E97's code_to_c (smoke_gate_e176.py, floor_scan.py)
A97, B97, C97 = 0.006175439291277969, -0.3665903970069978, 25.998917638611008   # E97's idle law (heat_q138t.py line 167)
R_Q138T = 0.8695                                # Q138(t)'s aifoundry3 chain, C per board W (model-q138t.json a3)
D = "docs/reports/data"
M6 = D + "/2026-11-02-q137m-model/m6.json"
SESSIONS = [
    ("E144", D + "/2026-11-02-e144-heat-minutes/aifoundry3/e144-smoke/p14401", D + "/2026-11-02-e144-heat-minutes/aifoundry3/e144/p14420"),
    ("E154", D + "/2026-11-03-e154-heat-e2e-aifoundry3/aifoundry3/e154-smoke/p15401", D + "/2026-11-03-e154-heat-e2e-aifoundry3/aifoundry3/e154/p15420"),
    ("E166", D + "/2026-11-04-e166-heat-replicate-aifoundry3/aifoundry3/e166-smoke/p16601", D + "/2026-11-04-e166-heat-replicate-aifoundry3/aifoundry3/e166/p16620"),
    ("E176", D + "/2026-11-05-e176-m11-holds-aifoundry3/aifoundry3/e176-smoke/p17601", D + "/2026-11-05-e176-m11-holds-aifoundry3/aifoundry3/e176/p17620"),
]
E176_LOG = D + "/2026-11-05-e176-m11-holds-aifoundry3/logs/session.log"
E176_T0_PST = "2026-11-05 17:21:15"             # the session log's "session start (T0 17:21:15 PST)"
BUDGET_S, DEADLINE_LESS_S = 4560, 60            # session_e176.sh: the pass's deadline T0 + 4560 - 60
AFTER_R0 = [("hold", "H_E", 600.0), ("rest", "R1", 360.0), ("hold", "Z", 600.0), ("rest", "R2", 120.0), ("hold", "L1", 600.0),
            ("rest", "R3", 360.0), ("hold", "S", 600.0), ("rest", "R4", 120.0)]          # run_e176.py DESIGNS["full"], R0 to L2's start
L2_S, HOLD_SPARE_S, SPARE_WANT_S = 600.0, 30.0, 60.0
LINE_C, WINDOW_S, F0_S = 0.50, 120.0, 3.0
TOP = None


def sha(p):
    h = hashlib.sha256()
    with open(os.path.join(TOP, p), "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def code_to_c(n):
    return (G_TS + H_TS * n / CAL5 - H_TS / 2) / 1000.0


def k97(T):
    return 2 * A97 * T + B97


def tel(rel):
    """(t s, board W, 34-sensor mean or None) per sample, in time order"""
    out = []
    with gzip.open(os.path.join(TOP, rel, "telemetry.jsonl.gz"), "rt") as f:
        for line in f:
            line = line.strip()
            if not (line.startswith("{") and line.endswith("}")):
                continue
            try:
                s = json.loads(line)
            except ValueError:
                continue
            pv = s.get("pvt") or {}
            cs = pv.get("c") or []
            m = sum(code_to_c(x) for x in cs) / 34.0 if (pv.get("st") == 0 and len(cs) == 34 and not pv.get("f")) else None
            out.append((s["t_ms"] / 1000.0, float(s["board_w"]), m))
    out.sort(key=lambda r: r[0])
    return out


def marks(rel):
    return [json.loads(x) for x in open(os.path.join(TOP, rel, "marks.jsonl")) if x.strip().startswith("{")]


class M6Filter:
    def __init__(self, tau, w, gain):
        self.tau, self.w, self.g = tau, w, gain
        self.x = [0.0] * len(tau)

    def step(self, dt, u0, u1):
        """advance dt s with the input a straight line from u0 to u1 (exact for each first-order pole)"""
        for i, tau in enumerate(self.tau):
            a = math.exp(-dt / tau)
            b = (1.0 - a) * tau / dt - a if dt > 0 else 0.0      # the ramp's part: x += g w [u1 (1 - a) - (u1 - u0) b]
            self.x[i] = self.x[i] * a + self.g * self.w[i] * (u1 * (1.0 - a) - (u1 - u0) * b)

    def total(self):
        return sum(self.x)


def window_mean(series, a, b):
    v = [y for t, y in series if a <= t < b and y is not None]
    return (sum(v) / len(v), len(v)) if v else (None, 0)


def run_session(name, smoke, meas, m6, Ls, extend_to=None, extend_mode=None):
    a, b = tel(smoke), tel(meas)
    t_first = a[0][0]
    f0 = [r for r in a if r[0] < t_first + F0_S]
    F0 = sum(r[2] for r in f0 if r[2] is not None) / sum(1 for r in f0 if r[2] is not None)
    P0 = sum(r[1] for r in f0) / len(f0)
    mk = marks(meas)
    r0 = [m for m in mk if m.get("kind") == "rest" and m.get("name") == "R0"][0]
    t0r, t1r = r0["t_start_ms"] / 1000.0, r0["t_end_ms"] / 1000.0
    room_mark = [m for m in mk if m.get("kind") == "room"]
    allp = sorted(a + b, key=lambda r: r[0])
    allp = [r for r in allp if r[0] < t1r]
    filt = M6Filter(m6["tau_s"], m6["weights"], m6["gain"])
    pred = [(allp[0][0], 0.0)]
    for (tp, Pp, _), (t, P, _) in zip(allp, allp[1:]):
        filt.step(t - tp, Pp - P0, P - P0)
        pred.append((t, filt.total()))
    ext = None
    if extend_to is not None and t0r + extend_to > allp[-1][0]:
        tail = [r[1] - P0 for r in allp if r[0] >= allp[-1][0] - 30.0]
        u_end = sum(tail) / len(tail)
        x_end = filt.total()
        t, dt = allp[-1][0], 0.1
        u_prev = allp[-1][1] - P0
        while t < t0r + extend_to:
            u = u_end if extend_mode == "held" else (u_end * filt.total() / x_end if x_end > 0 else 0.0)
            filt.step(dt, u_prev, u)
            u_prev = u
            t += dt
            pred.append((t, filt.total()))
        ext = {"mode": extend_mode, "from_s_after_R0_start": round(allp[-1][0] - t0r, 1), "to_s": extend_to,
               "board_excess_last_30s_W": round(u_end, 4)}
    meas34 = [(t, m) for t, _, m in allp]
    out = {"session": name, "smoke": smoke, "measured": meas, "F0_C": F0, "P0_W": P0, "F0_samples": len(f0),
           "first_sample_C": next(r[2] for r in a if r[2] is not None),
           "smoke_span_s": round(a[-1][0] - t_first, 1), "gap_s": round(b[0][0] - a[-1][0], 1),
           "R0_start_s_after_first_sample": round(t0r - t_first, 2), "R0_length_s": round(t1r - t0r, 1),
           "room_mark_C": room_mark[0]["mean34_c"] if room_mark else None, "by_L": {}}
    for L in Ls:
        lo, hi = t0r + L - WINDOW_S, t0r + L
        if hi > t1r + 0.5 and ext is None:
            continue
        mres, n = window_mean(meas34, lo, hi)
        pres, npred = window_mean(pred, lo, hi)
        row = {"window_s_after_R0_start": [L - WINDOW_S, L], "predicted_C": pres, "predicted_points": npred}
        if mres is not None and hi <= t1r + 0.5:
            row.update(measured_C=mres - F0, samples=n, miss_C=(mres - F0) - pres)
        out["by_L"][str(int(L))] = row
    if ext:
        out["extension"] = ext
    return out


def phi_up(z):
    return 0.5 * math.erfc(z / math.sqrt(2.0))


def timeline(R0_s):
    """L2's start on E176's committed timeline with R0 = R0_s, against run_e176.py's rule (a hold starts only with its length + 30 s left)"""
    t0 = time.mktime(time.strptime(E176_T0_PST, "%Y-%m-%d %H:%M:%S"))
    mk = marks(SESSIONS[3][2])
    r0 = [m for m in mk if m.get("kind") == "rest" and m.get("name") == "R0"][0]
    off = r0["t_start_ms"] / 1000.0 - t0
    l2 = off + R0_s + sum(d for _, _, d in AFTER_R0)
    deadline = BUDGET_S - DEADLINE_LESS_S
    left = deadline - l2
    return {"R0_s": R0_s, "R0_start_after_T0_s": round(off, 3), "L2_start_after_T0_s": round(l2, 3), "left_at_L2_s": round(left, 3),
            "spare_s": round(left - (L2_S + HOLD_SPARE_S), 3), "R5_s_left_after_L2": round(max(0.0, left - L2_S), 3)}


def main():
    global TOP
    TOP, outp = sys.argv[1], sys.argv[2]
    os.environ["TZ"] = "America/Los_Angeles"
    time.tzset()
    m6j = json.load(open(os.path.join(TOP, M6)))["heat"]
    m6 = {"tau_s": m6j["step_response"]["tau_s"], "weights": m6j["step_response"]["weights"],
          "gain": m6j["steady_c_per_board_w"]["aifoundry3"]["value"]}
    inputs = {M6: sha(M6), E176_LOG: sha(E176_LOG)}
    for _, s, m in SESSIONS:
        for rel in (s, m):
            for f in ("telemetry.jsonl.gz", "marks.jsonl"):
                inputs[rel + "/" + f] = sha(rel + "/" + f)
    res = {"what": "M11 A8: the smoke's residue at G0-A6's window, M6's step response on the planned smoke, and A8's rule",
           "M6": m6, "line_C": LINE_C, "window_s": WINDOW_S, "inputs_sha256": inputs, "sessions": {}}
    # 1. the committed sessions, each from its own traces
    for name, s, m in SESSIONS:
        res["sessions"][name] = run_session(name, s, m, m6, (300.0, 360.0, 420.0, 480.0))
    m300 = [res["sessions"][n]["by_L"]["300"]["miss_C"] for n, _, _ in SESSIONS]
    mean = sum(m300) / len(m300)
    sd = math.sqrt(sum((x - mean) ** 2 for x in m300) / (len(m300) - 1))
    rms = math.sqrt(sum(x * x for x in m300) / len(m300))
    res["misses_300s"] = {"values_C": dict(zip([n for n, _, _ in SESSIONS], m300)), "mean_C": mean, "sd_C": sd, "rms_C": rms,
                          "min_C": min(m300), "max_C": max(m300), "n": len(m300)}
    e144 = res["sessions"]["E144"]["by_L"]
    res["E144_longer_windows"] = {L: {k: e144[L].get(k) for k in ("measured_C", "predicted_C", "miss_C")} for L in ("300", "360", "420", "480")}
    # 2. E181's prediction: E176's committed smoke and R0 (the same smoke), and its floor dependence (the R0 part scaled by E97's law's k)
    e176 = res["sessions"]["E176"]
    rhat = e176["by_L"]["300"]["predicted_C"]
    smoke_only = run_session_smoke_only(SESSIONS[3], m6)
    r0part = rhat - smoke_only
    k_e176 = k97(e176["F0_C"])
    floors = {}
    for T in (49.4, 51.5, e176["F0_C"], 53.9):
        floors[f"{T:.3f}"] = {"k_W_per_C": k97(T), "predicted_C": smoke_only + r0part * k97(T) / k_e176}
    res["E181"] = {"planned_smoke": "E176's (run_e176.py DESIGNS['smoke'] and stoptests(), unchanged in E181's kit)",
                   "predicted_residue_C": rhat, "smoke_pass_part_C": smoke_only, "R0_part_C": r0part,
                   "by_floor (the R0 part scaled by E97's k(F0))": floors,
                   "distance_to_line_C": LINE_C - rhat, "within_about_0.1_of_the_line": LINE_C - rhat <= 0.1 + 1e-9,
                   "expected_reading_C": rhat + mean, "expected_reading_sd_C": sd}
    # 3. option (a): the longest whole-minute R0 that leaves L2 at least 60 s to spare on E176's timeline
    tl = {str(int(L)): timeline(L) for L in (300.0, 360.0, 420.0, 480.0)}
    La = max(float(L) for L, v in tl.items() if v["spare_s"] >= SPARE_WANT_S)
    ra = {}
    for mode in ("proportional", "held"):
        r = run_session("E176", SESSIONS[3][1], SESSIONS[3][2], m6, (La,), extend_to=La, extend_mode=mode)
        ra[mode] = {"predicted_C": r["by_L"][str(int(La))]["predicted_C"], "extension": r.get("extension")}
    # 4. the rule
    def p_fr(margin):
        return phi_up((margin - mean) / sd)
    pa = {m: p_fr(LINE_C - v["predicted_C"]) for m, v in ra.items()}
    pb = p_fr(LINE_C)
    p_now = p_fr(LINE_C - rhat)
    emp = lambda margin: sum(1 for x in m300 if x > margin)   # noqa: E731
    choice = "b" if pb < pa["proportional"] - 0.005 else "a"
    res["options"] = {
        "timeline_on_E176": tl, "a_R0_s": La,
        "a": {"R0_s": La, "predicted_C": ra, "line_C": LINE_C, "P_refuse_settled": pa,
              "misses_over_margin": {m: emp(LINE_C - v["predicted_C"]) for m, v in ra.items()},
              "R5_s": tl[str(int(La))]["R5_s_left_after_L2"], "L2_spare_s": tl[str(int(La))]["spare_s"]},
        "b": {"R0_s": 300.0, "predicted_C": rhat, "line": f"R0's room - F0 - {rhat:.3f} <= {LINE_C:.2f} C", "P_refuse_settled": pb,
              "misses_over_margin": emp(LINE_C)},
        "as_A6_has_it": {"P_refuse_settled": p_now, "misses_over_margin": emp(LINE_C - rhat)},
        "rule": "A8-R: the remedy with the smaller chance of refusing a settled card (a normal with the 300 s misses' mean and sd); "
                "within 0.5 percentage points, (a)", "choice": choice}
    # 5. the smoke's residue at H_E's anchor, which the chain (measured pass only) does not see: an estimate, reported
    gl = {n: R_Q138T * k97(res["sessions"][n]["F0_C"]) for n, _, _ in SESSIONS}
    res["H_E_anchor_estimate"] = {
        "what": "the chain reads only the measured pass, so the smoke's residue at the first hold's anchor (R0's last 120 s) decays unseen "
                "except for the share g = R k(F0) the board's leakage carries; estimate of that hold's e: -(1 - g) x the predicted residue "
                "(M6, the planned R0); not verified on committed holds",
        "by_session": {n: {"R0_s": res["sessions"][n]["R0_length_s"], "g": gl[n],
                           "predicted_residue_at_anchor_C": res["sessions"][n]["by_L"][str(int(round(res["sessions"][n]["R0_length_s"] / 60.0) * 60))]["predicted_C"]
                           if str(int(round(res["sessions"][n]["R0_length_s"] / 60.0) * 60)) in res["sessions"][n]["by_L"] else None}
                       for n, _, _ in SESSIONS}}
    for n, v in res["H_E_anchor_estimate"]["by_session"].items():
        if v["predicted_residue_at_anchor_C"] is not None:
            v["estimated_first_hold_e_C"] = -(1.0 - v["g"]) * v["predicted_residue_at_anchor_C"]
    g181 = R_Q138T * k97(49.4)
    res["H_E_anchor_estimate"]["E181"] = {"R0_300_s": -(1.0 - g181) * floors["49.400"]["predicted_C"],
                                          f"R0_{int(La)}_s": -(1.0 - g181) * ra["proportional"]["predicted_C"] * floors["49.400"]["predicted_C"] / rhat,
                                          "g_at_49.4C": g181}
    json.dump(res, open(outp, "w"), indent=1, sort_keys=True)
    # the printout
    print("M6:", m6)
    for n, _, _ in SESSIONS:
        s = res["sessions"][n]
        row = "; ".join(f"L{L} meas {v.get('measured_C', float('nan')):+.3f} pred {v['predicted_C']:+.3f} miss {v.get('miss_C', float('nan')):+.3f}"
                        for L, v in s["by_L"].items())
        print(f"{n}: F0 {s['F0_C']:.3f} C (first sample {s['first_sample_C']:.3f}), P0 {s['P0_W']:.2f} W, R0 {s['R0_length_s']:.0f} s from "
              f"{s['R0_start_s_after_first_sample']:.1f} s; room mark {s['room_mark_C']}; {row}")
    q = res["misses_300s"]
    print(f"misses at 300 s: {[round(x, 3) for x in m300]}; mean {q['mean_C']:+.3f}, sd {q['sd_C']:.3f}, rms {q['rms_C']:.3f} C (n {q['n']})")
    e = res["E181"]
    print(f"E181 predicted residue {e['predicted_residue_C']:.3f} C (smoke pass {e['smoke_pass_part_C']:.3f} + R0 {e['R0_part_C']:.3f}); "
          f"{e['distance_to_line_C']:.3f} C under the line; within about 0.1: {e['within_about_0.1_of_the_line']}; expected reading "
          f"{e['expected_reading_C']:.3f} +/- {e['expected_reading_sd_C']:.3f} C")
    print("  by floor: " + "; ".join(f"{T} C: {v['predicted_C']:.3f}" for T, v in e["by_floor (the R0 part scaled by E97's k(F0))"].items()))
    o = res["options"]
    for L, v in o["timeline_on_E176"].items():
        print(f"  timeline R0 {L} s: L2 starts T0 + {v['L2_start_after_T0_s']:.1f} s, {v['left_at_L2_s']:.1f} s left, spare {v['spare_s']:.1f} s, "
              f"R5 {v['R5_s_left_after_L2']:.1f} s")
    print(f"(a) R0 {o['a_R0_s']:.0f} s: predicted {o['a']['predicted_C']['proportional']['predicted_C']:.3f} (held {o['a']['predicted_C']['held']['predicted_C']:.3f}) "
          f"C; P(refuse settled) {o['a']['P_refuse_settled']['proportional']:.4f} (held {o['a']['P_refuse_settled']['held']:.4f}); "
          f"misses over margin {o['a']['misses_over_margin']}")
    print(f"(b) {o['b']['line']}: P(refuse settled) {o['b']['P_refuse_settled']:.2e}; misses over margin {o['b']['misses_over_margin']}")
    print(f"as A6 has it: P(refuse settled) {o['as_A6_has_it']['P_refuse_settled']:.4f}; misses over margin {o['as_A6_has_it']['misses_over_margin']}")
    print(f"rule A8-R -> ({o['choice']})")
    h = res["H_E_anchor_estimate"]
    print("first hold's e from the unseen smoke residue (estimate): " + "; ".join(
        f"{n} R0 {v['R0_s']:.0f} s: {v.get('estimated_first_hold_e_C', float('nan')):+.3f}" for n, v in h["by_session"].items())
        + f"; E181 R0 300 s {h['E181']['R0_300_s']:+.3f}, R0 {int(La)} s {h['E181'][f'R0_{int(La)}_s']:+.3f} C")


def run_session_smoke_only(sess, m6):
    """M6 on the smoke pass's board alone (the excess set to 0 from the smoke's last sample): the smoke's own part of the residue"""
    name, smoke, meas = sess
    a, b = tel(smoke), tel(meas)
    t_first = a[0][0]
    f0 = [r for r in a if r[0] < t_first + F0_S]
    P0 = sum(r[1] for r in f0) / len(f0)
    mk = marks(meas)
    r0 = [m for m in mk if m.get("kind") == "rest" and m.get("name") == "R0"][0]
    t0r, t1r = r0["t_start_ms"] / 1000.0, r0["t_end_ms"] / 1000.0
    filt = M6Filter(m6["tau_s"], m6["weights"], m6["gain"])
    pts = [(r[0], r[1] - P0) for r in a] + [(r[0], 0.0) for r in b if r[0] < t1r]
    pts.sort()
    vals = []
    for (tp, up), (t, u) in zip(pts, pts[1:]):
        filt.step(t - tp, up, u)
        if t1r - WINDOW_S <= t < t1r:
            vals.append(filt.total())
    return sum(vals) / len(vals)


if __name__ == "__main__":
    main()
