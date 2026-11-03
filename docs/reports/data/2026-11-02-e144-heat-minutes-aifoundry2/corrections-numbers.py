#!/usr/bin/env python3
"""E144b, corrections after verification: every number the README's corrections C1-C5 quote, printed from committed files.

    /usr/bin/python3 docs/reports/data/2026-11-02-e144-heat-minutes-aifoundry2/corrections-numbers.py \
        > docs/reports/data/2026-11-02-e144-heat-minutes-aifoundry2/corrections-numbers.txt

Post hoc and desk only (Mon 2 / Tue 3 Nov 2026, after an independent verifier's report): no card, no device command, nothing re-run.
No verdict comes from this file; the registered verdicts are results.json's, unchanged. Q138(t)'s frozen code is imported as committed at
amendment A1 (c2f9920d) after its seven sha256 are checked, the way reduce_e144b.py checks them, and is never edited:
  C1  die rise per board W by kind and session (score_e144.per_board_w's formula, and the same formula over 600-900 s), with the
      frozen chain's plateau error per hold, over E111 (1 Nov), E133 (2 Nov, morning) and E144b (2 Nov, evening) on aifoundry2 card 0;
  C2  E144b's G1 and G2 scored by the frozen score_a2 with the rest anchor's die moved by delta (the whole-degree reading's +-0.5 C),
      the edges each PASS crosses, the die readings behind the anchor, and the before/after at one hold length (Q138(t)'s two
      session-out chains, fit_q138t's folds, on the four long holds cut to E144b's lengths);
  C3  G2's clock with its time bases (the hold file's first sampler line, the first sparsity_host process, its first kernel launch);
  C5  the commands, counted from the records (each run_hpl query set: one ettelem sptrace, one residency read answered unsent, one
      ettelem config; the queue's config reads; the session-end read; et-lab-manifest).
"""
import glob
import gzip
import hashlib
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
DATA = os.path.join(ROOT, "docs", "reports", "data")
Q138T = os.path.join(DATA, "2026-11-02-q138t-heat-model")
FROZEN = {  # sha256 at c2f9920d, as reduce_e144b.py lists them
    "predictions-e144.json": "ae840f84bd36e80f822981913b3d44f314248669f56ff96dc2c2b61ced0a92d0",
    "amendment-a1.json": "a147f40c5225e6d213f6f907dae652961f2b7ae784fe56747dbf6d22b5726240",
    "model-q138t.json": "268b47fd580b330738eb3e1c83ea392f3784aae348a658e7335b734a1168e8fa",
    "score_e144.py": "0569c49474da4058de4ad14c13d1081fa50ba2e7dd705d4a564835d94c2e1494",
    "heat_q138t.py": "9dbb288f896b7e588fbc155d67f32b1cb7089ffe4ede465c1380d2724d1fb49b",
    "fit_q138t.py": "0f21f77cb916bb65c85708b89a89a36e7add3146e098da38dd64b4077e9eb29a",
    "predict_e144.py": "313c6840337615b2c474c39f74f095737bf7a35ecc6f9d8ac2356478f6442512",
}
for f, h in FROZEN.items():
    if hashlib.sha256(open(os.path.join(Q138T, f), "rb").read()).hexdigest() != h:
        sys.exit(f"refusing: {f} differs from c2f9920d")
sys.path.insert(0, Q138T)
import heat_q138t as hm  # noqa: E402
import fit_q138t as ft  # noqa: E402
import score_e144 as sc  # noqa: E402

E111 = os.path.join(DATA, "2026-11-01-e111-heat-steady")
E133 = os.path.join(DATA, "2026-11-02-e133-heat-holds")
MP = {"W1B/HOLD-00-int8-neg_ones-hold": "G1", "W2/HOLDF-00-fp32-randn-hold": "G2", "W2/HOLD-00-int8-neg_ones-hold": None}  # the self-test's
OUT = {}


def sessions():
    """(label, session) for every aifoundry2 step with a long hold: E111 and E133 as score_e144's self-test loads them, E144b as reduce does"""
    out = []
    for lab, d in (("E111", E111), ("E133", E133)):
        for s in sc.a2_load([os.path.join(d, "W1B"), os.path.join(d, "W2")], MP):
            out.append((lab, s))
    for s in sc.a2_load([os.path.join(HERE, "G1"), os.path.join(HERE, "G2")]):
        out.append(("E144b", s))
    return out


def kind(name):
    return "int8 -1s" if "int8-neg_ones" in name else ("fp32 randn" if "fp32-randn" in name else name)


def anchor_mask(s, h):
    return (s["g"] >= h["anchor_end"] - hm.ANCHOR_S) & (s["g"] < h["anchor_end"])


def per_w(s, h, w0=None, w1=None):
    """score_e144.per_board_w's point estimate (rise over the anchor window per board W of rise), over the hold's last 300 s, or over
    [t0 + w0, t0 + w1) post hoc"""
    g, T, P = s["g"], s["T"], s["P"]
    a = anchor_mask(s, h)
    Tb, Pb = float(np.mean(T[a])), float(np.mean(P[a]))
    m = (g >= h["t1"] - 300) & (g < h["t1"]) if w0 is None else (g >= h["t0"] + w0) & (g < h["t0"] + w1)
    dT, dP = float(np.mean(T[m])) - Tb, float(np.mean(P[m])) - Pb
    return {"per_W": dT / dP, "rise_C": dT, "board_rise_W": dP, "anchor_pm": 0.5 / dP}


def raw_window(s, t0, t1, key="mhz_raw"):
    k = (s["t_raw"] >= t0) & (s["t_raw"] < t1)
    return s[key][k]


def shifted(s, delta):
    """the session with the anchor window's die moved by delta (the rest die read as 46.00 + delta); nothing else changes"""
    s2 = dict(s)
    s2["T"] = s["T"].copy()
    for h in s["holds"]:
        s2["T"][anchor_mask(s, h)] += delta
    return s2


def counts(x):
    v, n = np.unique(np.asarray(x).astype(int), return_counts=True)
    return {int(a): int(b) for a, b in zip(v, n)}


def p(line=""):
    print(line)


# ------------------------------------------------------------------------------------------------------------------------------ C1
def c1(S):
    p("C1. Die rise per board W, by kind and session (aifoundry2 card 0; score_e144.per_board_w's formula; the rest anchor is the")
    p("    whole-degree die over the REST's last 120 s; '+-' is that anchor's +-0.5 C over the window's board rise)")
    rows = []
    for lab, s in S:
        pred = ft.predict_session(s, sc.TAU, sc.R2)
        for h in s["holds"]:
            dur = h["t1"] - h["t0"]
            if dur < 800:
                continue  # the 339-345 s warm probes have no 600-900 s window
            a = anchor_mask(s, h)
            last = per_w(s, h)
            mid = per_w(s, h, 600.0, 900.0)
            ra = ft.score_hold(s, pred, h)
            hcut = dict(h, t1=h["t0"] + 900.0)
            rc = ft.score_hold(s, pred, hcut)
            mhz_last = raw_window(s, h["t1"] - 300, h["t1"])
            mhz_mid = raw_window(s, h["t0"] + 600, h["t0"] + 900)
            r = {"session": lab, "step": s["name"], "hold": h["name"], "kind": kind(h["name"]), "dur_s": dur,
                 "rest_die_C": float(np.mean(s["T"][a])), "rest_values": counts(s["T"][a]), "start_after_rest_s": h["t0"] - h["anchor_end"],
                 "last300": last, "w600_900": mid, "mhz_mean_last300": float(np.mean(mhz_last)), "mhz_mean_600_900": float(np.mean(mhz_mid)),
                 "share600_last300": float(np.mean(mhz_last <= 610)),
                 "a_plateau_err_last300_C": ra["plateau_err_C"], "a_plateau_err_600_900_C": rc["plateau_err_C"],
                 "in_sample": lab != "E144b"}
            rows.append(r)
            start = ("from rest" if r["start_after_rest_s"] < 5 else
                     f"warm: it starts {r['start_after_rest_s']:.0f} s after the REST, after the step's other runs")
            p(f"  {lab:5s} {s['name']:3s} {r['kind']:10s} {dur:6.0f} s  rest die {r['rest_die_C']:.2f} (readings {r['rest_values']}); {start}")
            p(f"        last 300 s : {last['per_W']:.4f} +-{last['anchor_pm']:.4f} C/W ({last['rise_C']:.2f} C over {last['board_rise_W']:.2f} W), "
              f"{r['mhz_mean_last300']:.1f} MHz, 600 MHz share {r['share600_last300']:.3f}; the frozen chain's plateau error {ra['plateau_err_C']:+.3f} C")
            p(f"        600-900 s  : {mid['per_W']:.4f} +-{mid['anchor_pm']:.4f} C/W ({mid['rise_C']:.2f} C over {mid['board_rise_W']:.2f} W), "
              f"{r['mhz_mean_600_900']:.1f} MHz; the frozen chain's plateau error over 600-900 s {rc['plateau_err_C']:+.3f} C"
              f"{'  (in sample: the chain was fitted on E111 and E133)' if r['in_sample'] else '  (blind)'}")
    p()
    p("  int8 -1s minus fp32 randn, per session (each with the two anchors' quantization added: +-(0.5/dP_int8 + 0.5/dP_fp32))")
    gaps = {}
    for lab in ("E111", "E133", "E144b"):
        i8 = [r for r in rows if r["session"] == lab and r["kind"] == "int8 -1s"][0]
        f32 = [r for r in rows if r["session"] == lab and r["kind"] == "fp32 randn"][0]
        gl = i8["last300"]["per_W"] - f32["last300"]["per_W"]
        el = i8["last300"]["anchor_pm"] + f32["last300"]["anchor_pm"]
        gm = i8["w600_900"]["per_W"] - f32["w600_900"]["per_W"]
        em = i8["w600_900"]["anchor_pm"] + f32["w600_900"]["anchor_pm"]
        gaps[lab] = {"last300": [gl, el], "w600_900": [gm, em], "fp32_regime_last300": "floor" if f32["share600_last300"] >= 0.98 else "trip"}
        p(f"  {lab:5s} last 300 s {gl:+.4f} +-{el:.4f} (range {gl - el:+.3f} to {gl + el:+.3f}); 600-900 s {gm:+.4f} +-{em:.4f} "
          f"(range {gm - em:+.3f} to {gm + em:+.3f}); fp32's regime over its last 300 s: {gaps[lab]['fp32_regime_last300']}")
    p()
    p("  the frozen chain's single R (model-q138t.json a2): %.4f C per board W" % float(np.sum(sc.R2)))
    i8 = [r for r in rows if r["kind"] == "int8 -1s"]
    p("  int8 -1s plateau error, the frozen chain (last 300 s): " + ", ".join(f"{r['session']} {r['a_plateau_err_last300_C']:+.3f}" for r in i8)
      + "; over 600-900 s: " + ", ".join(f"{r['session']} {r['a_plateau_err_600_900_C']:+.3f}" for r in i8))
    f32 = [r for r in rows if r["kind"] == "fp32 randn"]
    p("  fp32 randn plateau error, the frozen chain (last 300 s): " + ", ".join(f"{r['session']} {r['a_plateau_err_last300_C']:+.3f}" for r in f32)
      + "; over 600-900 s: " + ", ".join(f"{r['session']} {r['a_plateau_err_600_900_C']:+.3f}" for r in f32))
    p("  int8 -1s per board W, last 300 s: " + ", ".join(f"{r['session']} {r['last300']['per_W']:.4f}" for r in i8)
      + "; 600-900 s: " + ", ".join(f"{r['session']} {r['w600_900']['per_W']:.4f}" for r in i8))
    p("  int8 -1s per board W over its chain's 0.663: last 300 s " + ", ".join(f"{r['session']} x{r['last300']['per_W'] / float(np.sum(sc.R2)):.3f}" for r in i8))
    OUT["C1"] = {"rows": rows, "gaps": gaps, "R_chain": float(np.sum(sc.R2))}


# ------------------------------------------------------------------------------------------------------------------------------ C2
_BASE = []


def score_e144b(delta):
    """the frozen score_a2 on E144b's G1 and G2 with the anchor window's die moved by delta (the sessions loaded once)"""
    if not _BASE:
        _BASE.extend(sc.a2_load([os.path.join(HERE, "G1"), os.path.join(HERE, "G2")]))
    return {r["G"]: r for r in sc.score_a2([shifted(s, delta) for s in _BASE])["holds"]}


def bisect(f, lo, hi, n=24):
    """the delta in [lo, hi] where f changes sign (f continuous), or None"""
    flo, fhi = f(lo), f(hi)
    if flo == 0:
        return lo
    if (flo > 0) == (fhi > 0):
        return None
    for _ in range(n):
        mid = 0.5 * (lo + hi)
        fm = f(mid)
        if (fm > 0) == (flo > 0):
            lo, flo = mid, fm
        else:
            hi = mid
    return 0.5 * (lo + hi)


def c2():
    p("C2. The rest anchor's quantization: E144b scored by the frozen score_a2, the anchor window's die moved by delta")
    p("    (the rest die read as 46.00 + delta C; every REST sample read one whole degree; the holds' own samples are left as read)")
    score_e144b(0.0)
    for s in _BASE:
        for h in s["holds"]:
            # the raw whole-degree readings (not the grid) behind the anchor and the plateau
            tel = hm.load_tel(sorted(glob.glob(os.path.join(HERE, s["name"], "tel", "*.jsonl.gz"))), "fw")
            kr = (tel["t"] >= h["anchor_end"] - hm.ANCHOR_S) & (tel["t"] <= h["anchor_end"])
            kl = (tel["t"] >= h["t1"] - 300) & (tel["t"] <= h["t1"])
            p(f"  {s['name']}: raw die readings over the anchor window {counts(tel['T'][kr])} (n {int(kr.sum())}); over the last 300 s "
              f"{counts(tel['T'][kl])} (mean {float(np.mean(tel['T'][kl])):.3f})")
    deltas = (-0.5, -0.25, 0.0, 0.25, 0.5)
    grid_rows = {}
    p()
    p("  delta  | G1 (a) rms, plateau, verdict | G1 (b) err, verdict | G1 (c) per W, verdict | G1 t63 x open, x A1.8 | G2 (a) rms, plateau, verdict | G2 (b) predicted, err, regime predicted, verdict")
    for d in deltas:
        r = score_e144b(d)
        g1, g2 = r["G1"], r["G2"]
        grid_rows[d] = {"G1": {"a_rms": g1["a"]["rms_C"], "a_plateau": g1["a"]["plateau_err_C"], "a": g1["a"]["verdict"],
                               "b_err": g1["b"]["err_C"], "b": g1["b"]["verdict"], "c_per_W": g1["c_per_board_W"]["per_board_W"],
                               "c": g1["c_per_board_W"]["verdict"], "t63_open": g1["c_t63"]["ratio"], "t63_A1": g1["c_t63_A1"]["ratio"],
                               "t63_A1_verdict": g1["c_t63_A1"]["verdict"]},
                        "G2": {"a_rms": g2["a"]["rms_C"], "a_plateau": g2["a"]["plateau_err_C"], "a": g2["a"]["verdict"],
                               "b_pred": g2["b"]["predicted_C"], "b_err": g2["b"]["err_C"], "b_regime_pred": g2["b"]["regime_predicted"],
                               "b": g2["b"]["verdict"], "per_W": g2["per_board_W_last300s"]}}
        x, y = grid_rows[d]["G1"], grid_rows[d]["G2"]
        p(f"  {d:+.2f}  | {x['a_rms']:.3f} {x['a_plateau']:+.3f} {x['a']:12s} | {x['b_err']:+.3f} {x['b']:12s} | {x['c_per_W']:.4f} {x['c']:4s} | "
          f"x{x['t63_open']:.3f} x{x['t63_A1']:.3f} ({x['t63_A1_verdict']}) | {y['a_rms']:.3f} {y['a_plateau']:+.3f} {y['a']:12s} | "
          f"{y['b_pred']:.3f} {y['b_err']:+.3f} {y['b_regime_pred']} {y['b']} (G2 per W {y['per_W']:.4f})")
    p()
    edges = {
        "G1 (a) rms reaches its PASS edge 1.20": bisect(lambda d: score_e144b(d)["G1"]["a"]["rms_C"] - 1.20, -0.5, 0.0),
        "G1 (a) plateau error reaches +1.30": bisect(lambda d: score_e144b(d)["G1"]["a"]["plateau_err_C"] - 1.30, -0.5, 0.0),
        "G1 (b) error reaches +1.30": bisect(lambda d: score_e144b(d)["G1"]["b"]["err_C"] - 1.30, -0.5, 0.0),
        "G1 (c) per W reaches 0.74": bisect(lambda d: score_e144b(d)["G1"]["c_per_board_W"]["per_board_W"] - 0.74, -0.5, 0.0),
        "G1 t63 against the open loop's 49.6 s reaches x1.33 (its PASS edge)": bisect(lambda d: score_e144b(d)["G1"]["c_t63"]["ratio"] - 1.33, -0.5, -0.25),
        "G2 (a) rms reaches 1.20": bisect(lambda d: score_e144b(d)["G2"]["a"]["rms_C"] - 1.20, -0.5, 0.5),
        "G2 (b) error reaches -0.60": bisect(lambda d: score_e144b(d)["G2"]["b"]["err_C"] + 0.60, 0.0, 0.5),
        "G2 (b) error reaches +0.60": bisect(lambda d: score_e144b(d)["G2"]["b"]["err_C"] - 0.60, -0.5, 0.0),
    }
    p("  the delta at which a PASS edge is reached inside [-0.5, +0.5] C (None: not inside the range)")
    for k, v in edges.items():
        p(f"    {k}: {'None' if v is None else f'{v:+.3f} C'}")
    p("  G2's regime edge: the rest die where max(rest + 21.49, 65.9) changes regime is 44.41 C, 1.59 C under the 46.00 reading")
    OUT["C2"] = {"by_delta": {str(k): v for k, v in grid_rows.items()}, "edges": edges}

    p()
    p("  Before and after at one hold length. Before = Q138(t)'s two session-out chains (fit_q138t's folds: fit on one day, score the")
    p("  other); after = the frozen chain on E144b, blind. The four long holds whole (as cv-q138t.json has them), then cut post hoc at")
    p("  E144b's lengths (int8 -1s at 902.8 s, fp32 randn at 912.6 s): rms over the hold, plateau error over its last 300 s")
    A2 = ft.a2_sessions()
    cv = json.load(open(os.path.join(Q138T, "cv-q138t.json")))["a2"]
    L = {"int8 -1s": 902.829, "fp32 randn": 912.618}
    folds = {"fit E111, predict E133": (["E111-W2", "E111-W1B"], ["E133-W2", "E133-W1B"]),
             "fit E133, predict E111": (["E133-W2", "E133-W1B"], ["E111-W2", "E111-W1B"])}
    before = []
    for fold, (tr, te) in folds.items():
        R, _, _ = ft.fit_on([s for s in A2 if s["name"] in tr])
        p(f"    {fold}: R_total {float(R.sum()):.4f} (cv-q138t.json {cv[fold]['R_total']:.4f})")
        for s in A2:
            if s["name"] not in te:
                continue
            pred = ft.predict_session(s, ft.TAU, R)
            for h in s["holds"]:
                if not h["name"].startswith("HOLD"):
                    continue
                whole = ft.score_hold(s, pred, h)
                ref = [x for x in cv[fold]["rows"] if x["session"] == s["name"] and x["hold"] == h["name"]][0]
                k = kind(h["name"])
                dur = h["t1"] - h["t0"]
                line = (f"      {s['name']:9s} {k:10s} {dur:6.0f} s whole: rms {whole['rms_C']:.3f} (cv-q138t.json {ref['rms_C']:.3f}), "
                        f"plateau {whole['plateau_err_C']:+.3f}")
                row = {"fold": fold, "session": s["name"], "kind": k, "dur_s": dur, "whole_rms": whole["rms_C"], "whole_plateau": whole["plateau_err_C"]}
                if dur > L[k] + 60:
                    cut = ft.score_hold(s, pred, dict(h, t1=h["t0"] + L[k]))
                    line += f" | cut at {L[k]:.0f} s: rms {cut['rms_C']:.3f}, plateau {cut['plateau_err_C']:+.3f}"
                    row.update({"cut_s": L[k], "cut_rms": cut["rms_C"], "cut_plateau": cut["plateau_err_C"]})
                else:
                    line += " | shorter than E144b's holds: not cut"
                p(line)
                before.append(row)
    long_rows = [r for r in before if "cut_rms" in r]
    p(f"    the four long holds, session-out: whole rms {min(r['whole_rms'] for r in long_rows):.3f}-{max(r['whole_rms'] for r in long_rows):.3f} "
      f"(mean {np.mean([r['whole_rms'] for r in long_rows]):.3f}, holds {min(r['dur_s'] for r in long_rows):.0f}-{max(r['dur_s'] for r in long_rows):.0f} s); "
      f"cut to E144b's lengths {min(r['cut_rms'] for r in long_rows):.3f}-{max(r['cut_rms'] for r in long_rows):.3f} (mean {np.mean([r['cut_rms'] for r in long_rows]):.3f})")
    for k in ("int8 -1s", "fp32 randn"):
        rr = [r for r in long_rows if r["kind"] == k]
        p(f"      {k}: cut rms " + ", ".join(f"{r['session']} {r['cut_rms']:.3f} (plateau {r['cut_plateau']:+.3f})" for r in rr))
    six = [r["whole_rms"] for r in before]
    p(f"    all six holds as committed (two of them the 339-345 s warm probes): mean {np.mean(six):.3f} (A1 A1_7 means_over_six_holds 0.789)")
    r0 = score_e144b(0.0)
    p(f"    after (E144b, blind, the frozen chain): G1 int8 -1s {r0['G1']['dur_s']:.1f} s rms {r0['G1']['a']['rms_C']:.3f}, "
      f"G2 fp32 randn {r0['G2']['dur_s']:.1f} s rms {r0['G2']['a']['rms_C']:.3f}")
    OUT["C2"]["before_after"] = {"before": before, "after": {"G1": r0["G1"]["a"], "G2": r0["G2"]["a"]}}


# ------------------------------------------------------------------------------------------------------------------------------ C3
def rows_of(path):
    with gzip.open(path, "rt") as f:
        for ln in f:
            if ln.startswith("{"):
                yield json.loads(ln)


def c3():
    p("C3. The time bases of the clock readings (G1, G2), and G2's clock (raw 10 Hz rows of the hold file; sp.board_avg_w is the SP's running board average)")
    out = {}
    for step in ("G1", "G2"):
        hf = sorted(glob.glob(os.path.join(HERE, step, "tel", "HOLD*.jsonl.gz")))[0]
        R = list(rows_of(hf))
        L = [json.loads(x) for x in gzip.open(os.path.join(HERE, step, "launches.jsonl.gz"), "rt") if x.startswith("{")]
        ts0 = R[0]["t_ms"] / 1e3
        tp0 = min(x["t_start_ms"] for x in L) / 1e3
        tk0 = min(k["t_start_ms"] for k in L[0]["sparsity"]) / 1e3
        t = np.array([r["t_ms"] / 1e3 for r in R])
        mhz = np.array([r["mhz"]["minion"] for r in R], float)
        die = np.array([r["temp_c"]["minshire"][0] for r in R], float)
        bw = np.array([r["board_w"] for r in R], float)
        avg = np.array([r["sp"]["board_avg_w"] for r in R], float)
        # reduce_e144b.clock_and_safety's base: the first sample over 30 W; its "first step down": the first sample from there at or under
        # 610 MHz with the board over 30 W
        ib = int(np.argmax(bw > 30))
        isd = ib + int(np.argmax((mhz[ib:] <= 610) & (bw[ib:] > 30)))
        tsd = t[isd]
        pr = [x for x in L if x["t_start_ms"] / 1e3 <= tsd <= x["t_end_ms"] / 1e3]
        ks = [k for x in L for k in x.get("sparsity", []) if k["t_start_ms"] / 1e3 <= tsd <= k["t_end_ms"] / 1e3]
        o = {"sampler_first_line_to_first_process_s": tp0 - ts0, "first_process_to_first_kernel_s": tk0 - tp0,
             "reducer_base_after_first_process_s": t[ib] - tp0, "reducer_step_after_base_s": round(tsd - t[ib], 1),
             "reducer_step_after_first_process_s": round(tsd - tp0, 2), "reducer_step_mhz": int(mhz[isd]), "reducer_step_die_C": int(die[isd]),
             "reducer_step_in_process": bool(pr), "reducer_step_in_kernel_launch": bool(ks)}
        p(f"  {step}: the hold file's first sampler line comes {tp0 - ts0:.3f} s before the first sparsity_host process starts (its first kernel "
          f"launch {tk0 - tp0:.3f} s after that); posthoc.txt's times count from that first line")
        if pr:
            x = pr[0]
            k0 = min(k["t_start_ms"] for k in x["sparsity"]) / 1e3
            where = (f"inside process {x['proc']}, {tsd - x['t_start_ms'] / 1e3:.3f} s after it started and "
                     + ("inside a kernel launch" if ks else f"before its first kernel launch ({k0 - x['t_start_ms'] / 1e3:.3f} s after its start): a process boundary"))
        else:
            where = "between two processes"
        p(f"    results.json's first_step_down counts from the first sample over 30 W, {t[ib] - tp0:.3f} s after the first process started; its "
          f"{o['reducer_step_after_base_s']} s sample ({o['reducer_step_after_first_process_s']} s after the first process, {o['reducer_step_mhz']} MHz, "
          f"die {o['reducer_step_die_C']}) is {where}")
        if step == "G1":
            out[step] = o
            continue
        i800 = int(np.argmax(mhz >= 790))
        j = i800 + int(np.argmax(mhz[i800:] < 790))
        j610 = i800 + int(np.argmax(mhz[i800:] <= 610))
        i66 = int(np.argmax(die >= 66))
        above = np.where(mhz > 610)[0]
        ilast = int(above[-1])
        ipk = int(np.argmax(bw))
        span = slice(j, ilast + 1)
        sh = {f: float(np.mean(mhz[span] == f)) for f in (600.0, 700.0, 800.0)}

        def at(i):
            return round(t[i] - tp0, 2)
        o.update({"first_ge_790_s": at(i800), "first_below_790_s": at(j), "first_below_790_mhz": int(mhz[j]), "first_below_790_board_w": float(bw[j]),
                  "first_below_790_sp_avg_w": float(avg[j]), "sp_avg_max_before_s": float(np.max(avg[i800:j + 1])), "die_at_step": int(die[j]),
                  "first_le_610_s": at(j610), "die_first_66_s": at(i66), "last_above_610_s": at(ilast), "last_above_610_mhz": int(mhz[ilast]),
                  "last_above_610_after_die66_s": round(t[ilast] - t[i66], 1), "share_between": sh, "n_ge_790": int((mhz >= 790).sum()),
                  "peak_w": float(bw[ipk]), "peak_s": at(ipk), "peak_mhz": int(mhz[ipk]), "peak_after_die66_s": round(t[ipk] - t[i66], 1)})
        p(f"    (every time below counts from the first sparsity_host process's start)")
        p(f"    first sample >= 790 MHz {o['first_ge_790_s']} s after the first process (posthoc.txt: 2.4 s from the first line)")
        p(f"    first sample under 790 MHz after it: {o['first_below_790_s']} s, {o['first_below_790_mhz']} MHz, die {o['die_at_step']} C, board {o['first_below_790_board_w']} W, "
          f"the SP's running average {o['first_below_790_sp_avg_w']} W (its highest from the first 800 MHz sample to here {o['sp_avg_max_before_s']} W; the TDP is 65 W, "
          f"the die threshold 65 C)")
        p(f"    first sample at or under 610 MHz after it: {o['first_le_610_s']} s (posthoc.txt: 3.8 s from the first line)")
        p(f"    the die's first reading of 66: {o['die_first_66_s']} s; the last sample above 610 MHz: {o['last_above_610_s']} s ({o['last_above_610_mhz']} MHz), "
          f"{o['last_above_610_after_die66_s']} s after the die's first 66")
        p(f"    from the first step down to the last sample above 610 MHz: 800 MHz {sh[800.0]:.3f}, 700 MHz {sh[700.0]:.3f}, 600 MHz {sh[600.0]:.3f} of samples")
        p(f"    samples >= 790 MHz in the whole hold: {o['n_ge_790']} ({o['n_ge_790'] / 10:.1f} s at 10 Hz)")
        p(f"    board peak {o['peak_w']} W at {o['peak_s']} s, {o['peak_mhz']} MHz, {o['peak_after_die66_s']} s after the die's first 66")
        out[step] = o
    OUT["C3"] = out


# ------------------------------------------------------------------------------------------------------------------------------ C5
def c5():
    p("C5. Commands, counted from the records (each run_hpl query set = one ettelem sptrace, one residency read answered unsent, one ettelem config)")
    steps = ("SMOKE", "STOPTEST-DIE", "STOPTEST-BOARD", "G1", "END", "G2", "END2")
    tot = {"query_sets": 0, "config_in_query_sets": 0, "sptrace": 0, "residency_not_sent": 0, "queue_config": 0, "manifest": 0}
    for st in steps:
        d = os.path.join(HERE, st)
        qs = [json.loads(x) for x in open(os.path.join(d, "queries.jsonl")) if x.strip()]
        if os.path.exists(os.path.join(d, "runs.jsonl")):
            qs += [json.loads(x).get("queries") for x in open(os.path.join(d, "runs.jsonl")) if x.strip()]
        qs = [q for q in qs if q]
        n_cfg = sum(1 for q in qs if "config_rc" in q)
        n_spt = sum(1 for q in qs if "sptrace_rc" in q)
        n_ns = sum(1 for x in open(os.path.join(d, "e144b-not-sent.jsonl")) if x.strip())
        n_qc = sum(1 for tg in ("start", "end") if os.path.exists(os.path.join(d, f"config-{tg}.txt")))
        n_man = 1 if os.path.exists(os.path.join(d, "manifest.txt")) else 0
        for k, v in (("query_sets", len(qs)), ("config_in_query_sets", n_cfg), ("sptrace", n_spt), ("residency_not_sent", n_ns),
                     ("queue_config", n_qc), ("manifest", n_man)):
            tot[k] += v
        p(f"  {st:15s} query sets {len(qs):2d} (config {n_cfg}, sptrace {n_spt}), residency answered unsent {n_ns}, queue config reads {n_qc}, et-lab-manifest {n_man}")
    tot["session_end_config"] = 1 if os.path.exists(os.path.join(HERE, "config-session-end.txt")) else 0
    tot["ettelem_config_all"] = tot["config_in_query_sets"] + tot["queue_config"] + tot["session_end_config"]
    p(f"  total: {json.dumps(tot)}")
    man = sorted(glob.glob(os.path.join(HERE, "*", "manifest.txt")))
    p(f"  et-lab-manifest outputs: {len(man)} (one per run_hpl session, run_hpl.py:824); tools/lab/et-lab-manifest sha256 "
      f"{hashlib.sha256(open(os.path.join(ROOT, 'tools', 'lab', 'et-lab-manifest'), 'rb').read()).hexdigest()[:16]}")
    OUT["C5"] = tot


def main():
    p("E144b corrections after verification: numbers (post hoc, desk only; no verdict comes from this file)")
    p("frozen inputs at c2f9920d verified (7 files); Q138(t)'s score_e144, fit_q138t and heat_q138t imported as committed")
    p()
    c1(sessions())
    p()
    c2()
    p()
    c3()
    p()
    c5()
    json.dump(OUT, open(os.path.join(HERE, "corrections-numbers.json"), "w"), indent=1,
              default=lambda o: float(o) if isinstance(o, np.floating) else (int(o) if isinstance(o, np.integer) else str(o)))


if __name__ == "__main__":
    main()
