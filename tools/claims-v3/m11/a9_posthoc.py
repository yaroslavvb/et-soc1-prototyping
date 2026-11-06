#!/usr/bin/env python3
"""M11's dated amendment A9 (Fri 6 Nov 2026, before any E181 datum): the reported two-pass arm, and its post hoc evidence. Desk only; it reads
committed files and writes one JSON file. Every session it reads has been seen, so every figure is post hoc; the arm's definition (A9-1, the
function two_pass() below, which M11's scorer v4 imports unchanged) was written before this script was first run.

  THE REGISTERED READING (REGISTRATION.md section 1; score_m11.py line 150): Q138(t)'s chain as Q139(e) froze it (predict_q139e's TAU and R3,
           M11's arm A) on the MEASURED PASS ALONE: score_e144.a3_load([pass]): its telemetry on heat_q138t's 0.2 s grid, the input the
           board above Pref (the median board W over R0's last 120 s), the chain's states 0 at the pass's first grid point, each hold's
           anchor the mean of T - pred over the 120 s before its anchor end (fit_q138t.score_hold, score_e166.arm_a_error).
  A9-1, THE ARM (reported, never a verdict): the same chain, the same Pref, the same anchors and windows, over the smoke pass and the
           measured pass TOGETHER:
             - the telemetry of both passes (heat_q138t.load_tel on the smoke's telemetry.jsonl.gz then the measured pass's, the 34 codes);
             - the grid: the measured pass's own grid (heat_q138t.grid on its telemetry alone), extended back by whole 0.2 s steps to the
               smoke's first sample, so every grid point inside the measured pass, and every value the registered reading reads there
               (T, P, Pref, each hold's measured rise R), is the registered reading's own, bit for bit; the gap between the two passes is
               the straight line across it (heat_q138t.grid's interpolation of any gap);
             - the chain's states 0 at the first grid point: the card settled at F0 (A6-1, A7-4's hour of rest);
             - the marks and dispatch records of the measured pass only (score_e144.a3_session, unchanged);
             - refused (the arm reads NOT SCORED, with the reason) when the smoke's telemetry is not there or holds fewer than 10 readable
               samples, or when the gap between the smoke's last readable sample and the measured pass's first is not in (0, 600] s.
           So R is unchanged, and the arm's e differs from the registered e only through the chain's prediction.
  THE POST HOC READING HERE: on every committed aifoundry3 session with a smoke pass and then a fixed R0 (E144, R0 8 min; E154, E166 and
           E176, R0 5 min; the sessions A8 reads), each hold's plateau error by fit_q138t.score_hold (the reader score_e144 uses), on the
           measured pass alone and with the arm, and the difference; beside it, the arm's start at the floor's equilibrium (the states at
           the board's excess over Pref in the smoke's first 3 s, not 0: a sensitivity, never the arm), and A8-6's estimate of the first
           hold's part (residue-a8.json > H_E_anchor_estimate). For each session with 4 or more holds, the first hold's offset from the
           straight line e = a + g P (P = R - e) through the session's other holds, on each chain. E176's measured pass holds no hold (G0
           refused it): its gap and R0 only.

    python3 -B tools/claims-v3/m11/a9_posthoc.py <lab repo top> <out.json>
Python 3.9 with numpy 1.26 (the Intel's /usr/bin/python3; numpy in the user site, so never -I).
SPDX-License-Identifier: Apache-2.0
"""
import sys

sys.dont_write_bytecode = True
import hashlib  # noqa: E402
import json  # noqa: E402
import math  # noqa: E402
import os  # noqa: E402

GAP_MAX_S = 600.0            # A9-1: the gap between the smoke's last readable sample and the measured pass's first, at most
MIN_SMOKE_SAMPLES = 10       # A9-1: the smoke's readable samples, at least
F0_S = 3.0                   # A6-1's window (the sensitivity's start at the floor's equilibrium)
D = "docs/reports/data"
SESSIONS = [
    ("E144", D + "/2026-11-02-e144-heat-minutes/aifoundry3/e144-smoke/p14401", D + "/2026-11-02-e144-heat-minutes/aifoundry3/e144/p14420"),
    ("E154", D + "/2026-11-03-e154-heat-e2e-aifoundry3/aifoundry3/e154-smoke/p15401", D + "/2026-11-03-e154-heat-e2e-aifoundry3/aifoundry3/e154/p15420"),
    ("E166", D + "/2026-11-04-e166-heat-replicate-aifoundry3/aifoundry3/e166-smoke/p16601", D + "/2026-11-04-e166-heat-replicate-aifoundry3/aifoundry3/e166/p16620"),
    ("E176", D + "/2026-11-05-e176-m11-holds-aifoundry3/aifoundry3/e176-smoke/p17601", D + "/2026-11-05-e176-m11-holds-aifoundry3/aifoundry3/e176/p17620"),
]
_HERE = os.path.dirname(os.path.abspath(__file__))
_V1 = None


def modules(top=None):
    """the registered reading's own modules, through M11's scorer v1 (score_m11.py, unchanged: on import it checks M11's lists and its pinned
    reader, and score_e166 checks its frozen inputs): (heat_q138t, score_e144, fit_q138t, predict_q139e, numpy)"""
    global _V1
    if _V1 is None:
        m11 = os.path.join(top, "tools", "claims-v3", "m11") if top else _HERE
        if m11 not in sys.path:
            sys.path.insert(0, m11)
        import score_m11 as V1  # noqa: E402
        _V1 = V1
    return _V1.S166.hm, _V1.SE, _V1.FT, _V1.PQ, _V1.np


def _marks_recs(pass_dir):
    """score_e144.a3_load's reads of the measured pass, line for line: its marks and its dispatch records"""
    marks = [json.loads(x) for x in open(os.path.join(pass_dir, "marks.jsonl")) if x.strip()]
    recs = []
    rp = os.path.join(pass_dir, "runs.jsonl")
    if os.path.exists(rp):
        for x in open(rp):
            if x.strip():
                r = json.loads(x)
                recs.append((r["t_start_ms"] / 1e3, r["t_end_ms"] / 1e3, r["item"]))
    return marks, recs


def one_pass(pass_dir):
    """the registered reading's session (score_m11.py line 150; score_m11_v2.py's _context)"""
    hm, SE, FT, PQ, np = modules()
    return SE.a3_load([pass_dir])


def two_pass(pass_dir, smoke_dir):
    """A9-1: the session over the smoke pass and the measured pass together, or (None, why). Returns (session, info)."""
    hm, SE, FT, PQ, np = modules()
    mp = os.path.join(pass_dir, "telemetry.jsonl.gz")
    sp = os.path.join(smoke_dir, "telemetry.jsonl.gz") if smoke_dir else None
    if not sp or not os.path.exists(sp):
        return None, {"why": "the smoke pass's telemetry.jsonl.gz is not there"}
    tel_m = hm.load_tel([mp], "codes")
    g1, P1, T1 = hm.grid(tel_m)
    try:
        tel_s = hm.load_tel([sp], "codes")
    except (OSError, ValueError, KeyError, TypeError, EOFError) as e:
        return None, {"why": f"the smoke pass's telemetry is unreadable ({type(e).__name__})"}
    oks = np.isfinite(tel_s["T"]) & np.isfinite(tel_s["P"])
    if int(oks.sum()) < MIN_SMOKE_SAMPLES:
        return None, {"why": f"the smoke pass holds {int(oks.sum())} readable samples (fewer than {MIN_SMOKE_SAMPLES})"}
    okm = np.isfinite(tel_m["T"]) & np.isfinite(tel_m["P"])
    s_first, s_last = float(tel_s["t"][oks][0]), float(tel_s["t"][oks][-1])
    m_first = float(tel_m["t"][okm][0])
    gap = m_first - s_last
    if not (0.0 < gap <= GAP_MAX_S):
        return None, {"why": f"the gap between the passes is {gap:.1f} s, not in (0, {GAP_MAX_S:g}] s", "gap_s": gap}
    tel = hm.load_tel([sp, mp], "codes")
    ok = np.isfinite(tel["T"]) & np.isfinite(tel["P"])
    k = int(math.floor((float(g1[0]) - s_first) / hm.DT + 1e-9))
    g2 = np.concatenate([float(g1[0]) - hm.DT * np.arange(k, 0, -1), g1])
    P2 = np.interp(g2, tel["t"][ok], tel["P"][ok])
    T2 = np.interp(g2, tel["t"][ok], tel["T"][ok])
    same = bool(np.array_equal(P2[k:], P1) and np.array_equal(T2[k:], T1) and np.array_equal(g2[k:], g1))
    if not same:
        return None, {"why": "the extended grid does not reproduce the measured pass's own grid values (refused)", "gap_s": gap}
    marks, recs = _marks_recs(pass_dir)
    s2 = SE.a3_session(g2, P2, T2, marks, recs)
    f0w = (g2 >= s_first) & (g2 < s_first + F0_S)
    info = {"gap_s": gap, "smoke_readable_samples": int(oks.sum()), "smoke_span_s": s_last - s_first, "prepended_points": k,
            "measured_points_identical": same, "first_grid_point_after_smoke_first_s": float(g2[0]) - s_first,
            "dP_first_3s_W": float(np.mean(s2["dP"][f0w])) if f0w.any() else None}
    return s2, info


def predict(sess, x0_value=None):
    """the registered chain (Q139(e)'s TAU and R3, fit_q138t.predict_session); x0_value: the sensitivity's start (every state at that W)"""
    hm, SE, FT, PQ, np = modules()
    if x0_value is None:
        return FT.predict_session(sess, PQ.TAU, PQ.R3)
    X = hm.states(sess["dP"], PQ.TAU, x0=np.full(len(PQ.TAU), float(x0_value)))
    return X @ np.asarray(PQ.R3, float)


def _sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def r6(x):
    return None if x is None or (isinstance(x, float) and not math.isfinite(x)) else round(float(x), 6)


def line_offset(pts, first):
    """the first hold's e less the straight line e = a + g P through the other holds (ordinary least squares); None with fewer than 3 others"""
    oth = [p for n, p in pts.items() if n != first]
    if len(oth) < 3 or first not in pts:
        return None
    n = len(oth)
    mx = sum(p for p, _ in oth) / n
    my = sum(e for _, e in oth) / n
    sxx = sum((p - mx) ** 2 for p, _ in oth)
    if sxx <= 0:
        return None
    g = sum((p - mx) * (e - my) for p, e in oth) / sxx
    a = my - g * mx
    res = [e - (a + g * p) for p, e in oth]
    s = math.sqrt(sum(x * x for x in res) / (n - 2)) if n > 2 else None
    p1, e1 = pts[first]
    se = s * math.sqrt(1.0 + 1.0 / n + (p1 - mx) ** 2 / sxx) if s is not None else None
    return {"offset_C": e1 - (a + g * p1), "line_a_C": a, "line_g": g, "others": n, "residual_sd_C": s, "prediction_se_C": se}


def session_reading(name, smoke, meas):
    hm, SE, FT, PQ, np = modules()
    s1 = one_pass(meas)
    s2, info = two_pass(meas, smoke)
    out = {"smoke": smoke, "measured": meas, "arm": info}
    if s2 is None:
        out["arm_reads"] = "NOT SCORED: " + info["why"]
        return out
    p1, p2 = predict(s1), predict(s2)
    p2e = predict(s2, x0_value=info["dP_first_3s_W"])
    k = info["prepended_points"]
    g = s1["g"]
    r0 = s1["rests"][0]
    out["Pref_W"] = {"one_pass": s1["Pref"], "two_pass": s2["Pref"]}
    out["R0"] = {"t0_s_after_measured_first": r0["t0"] - float(g[0]), "length_s": r0["t1"] - r0["t0"]}
    aw = (g >= r0["t1"] - hm.ANCHOR_S) & (g < r0["t1"])
    out["R0_anchor_window"] = {"pred_two_less_one_C": float(np.mean(p2[k:][aw] - p1[aw]))}
    holds = {}
    for h in s1["holds"]:
        h2 = [x for x in s2["holds"] if x["name"] == h["name"] and abs(x["t0"] - h["t0"]) < 1e-6][0]
        a1 = FT.score_hold(s1, p1, h)
        a2 = FT.score_hold(s2, p2, h2)
        a3 = FT.score_hold(s2, p2e, h2)
        holds[h["name"]] = {
            "item": h.get("item"), "t0_s_after_R0_start": h["t0"] - r0["t0"], "from_rest": h["from_rest"], "share": h["share"],
            "R_C": a1["rise_meas_C"], "R_C_two_pass": a2["rise_meas_C"],
            "e_one_pass_C": a1["plateau_err_C"], "e_two_pass_C": a2["plateau_err_C"], "delta_e_C": a2["plateau_err_C"] - a1["plateau_err_C"],
            "e_two_pass_floor_equilibrium_start_C": a3["plateau_err_C"],
            "delta_e_floor_equilibrium_start_C": a3["plateau_err_C"] - a1["plateau_err_C"]}
    out["holds"] = holds
    order = [h["name"] for h in sorted(s1["holds"], key=lambda x: x["t0"])]
    out["hold_order"] = order
    if order:
        f = order[0]
        pts1 = {n: (v["R_C"] - v["e_one_pass_C"], v["e_one_pass_C"]) for n, v in holds.items()}
        pts2 = {n: (v["R_C"] - v["e_two_pass_C"], v["e_two_pass_C"]) for n, v in holds.items()}
        out["first_hold"] = {"name": f, "delta_e_C": holds[f]["delta_e_C"],
                             "offset_from_the_other_holds_line": {"one_pass": line_offset(pts1, f), "two_pass": line_offset(pts2, f)}}
        later = [holds[n]["delta_e_C"] for n in order[1:]]
        out["later_holds_delta_e_C"] = {"max_abs": max(abs(x) for x in later) if later else None, "n": len(later)}
    return out


def clean(x):
    if isinstance(x, dict):
        return {k: clean(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [clean(v) for v in x]
    if isinstance(x, bool) or x is None or isinstance(x, (int, str)):
        return x
    try:
        return r6(float(x))
    except (TypeError, ValueError):
        return str(x)


def main(argv):
    if len(argv) != 2:
        raise SystemExit(__doc__)
    top, outp = os.path.abspath(argv[0]), argv[1]
    os.chdir(top)
    modules(top)
    a8 = json.load(open("tools/claims-v3/m11/residue-a8.json"))["H_E_anchor_estimate"]
    res = {"what": "A9's post hoc evidence: each hold's plateau error on the measured pass alone (registered) and over both passes (A9-1's arm)",
           "gap_max_s": GAP_MAX_S, "sessions": {}, "inputs_sha256": {}}
    for name, smoke, meas in SESSIONS:
        r = session_reading(name, smoke, meas)
        est = (a8.get("by_session", {}).get(name) or {}).get("estimated_first_hold_e_C")
        r["A8_6_estimate_of_the_first_hold_e_C"] = est
        res["sessions"][name] = r
        for d in (smoke, meas):
            for fn in ("telemetry.jsonl.gz", "marks.jsonl", "runs.jsonl"):
                p = os.path.join(d, fn)
                if os.path.exists(p):
                    res["inputs_sha256"][p] = _sha(p)
    res["inputs_sha256"]["tools/claims-v3/m11/residue-a8.json"] = _sha("tools/claims-v3/m11/residue-a8.json")
    res["A8_6_estimate_E181_C"] = a8.get("E181", {}).get("R0_300_s")
    res = clean(res)
    json.dump(res, open(outp, "w"), indent=1, sort_keys=True)
    for name, _, _ in SESSIONS:
        r = res["sessions"][name]
        a = r["arm"]
        print(f"{name}: gap {a.get('gap_s')} s, smoke {a.get('smoke_span_s')} s over {a.get('smoke_readable_samples')} samples, "
              f"{a.get('prepended_points')} points prepended, measured points identical {a.get('measured_points_identical')}; "
              f"dP over F0's 3 s {a.get('dP_first_3s_W')} W; R0 anchor: pred two - one {r.get('R0_anchor_window', {}).get('pred_two_less_one_C')} C")
        for n in r.get("hold_order", []):
            h = r["holds"][n]
            print(f"   {n:5s} {h['item']:12s} t0 R0+{h['t0_s_after_R0_start']:7.1f} s  R {h['R_C']:7.3f} (two-pass {h['R_C_two_pass']:7.3f})  "
                  f"e one {h['e_one_pass_C']:+.3f}  two {h['e_two_pass_C']:+.3f}  delta {h['delta_e_C']:+.3f}  "
                  f"(floor-equilibrium start: delta {h['delta_e_floor_equilibrium_start_C']:+.3f})")
        if r.get("first_hold"):
            f = r["first_hold"]
            o1, o2 = f["offset_from_the_other_holds_line"]["one_pass"], f["offset_from_the_other_holds_line"]["two_pass"]
            fmt = lambda o: "n/a" if not o else f"{o['offset_C']:+.3f} (se {o['prediction_se_C']}, {o['others']} others)"  # noqa: E731
            print(f"   first hold {f['name']}: delta e {f['delta_e_C']:+.3f} C against A8-6's estimate {r['A8_6_estimate_of_the_first_hold_e_C']}; "
                  f"offset from the other holds' line: one pass {fmt(o1)}, two pass {fmt(o2)}; later holds' |delta e| max "
                  f"{r['later_holds_delta_e_C']['max_abs']}")
        if r.get("arm_reads"):
            print("   arm: " + r["arm_reads"])
    print(f"A8-6's estimate for E181's H_E (R0 300 s): {res['A8_6_estimate_E181_C']} C")


if __name__ == "__main__":
    main(sys.argv[1:])
