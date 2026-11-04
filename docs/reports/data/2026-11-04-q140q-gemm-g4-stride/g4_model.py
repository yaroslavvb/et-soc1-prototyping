#!/usr/bin/env python3
"""Q140(q): G4, a governed large GEMM's sustained clock, board and window die on aifoundry2, as registered in REGISTRATION.md
(49575094). G3 (docs/reports/data/2026-11-03-q139q-gemm-g3/g3_model.py, frozen at 91def7c4) is imported unchanged: its chain,
cap, trip rule, gaps, schedule and window. G4 adds the registered terms:

  T_Z  Q140(l)'s zeros level: every level + beta x delta_t (m9_a2.json: beta 0.648275, the format's fallback delta, T_ref 54.38 C).
  T_D  one die law for P0: every level is P0(f) [+ beta delta] + k_D (T(t) - T_ref), T(t) the chain's die at the step, T_ref
       54.3818 C; it replaces G3's effective k_eff (T(t) - T_start). Without T_D the level is G3's: P0(f) [+ beta delta] +
       k_eff (T(t) - T_start).
  T_G  the governor's process-boundary and in-process steps, folded into one dip at each process's kernel start: for d_G x the
       process's kernel seconds the clock is min(618 MHz, the clock G3's loop gives) when the raised 800 MHz level at the
       process's first kernel step is at least P_G; the board is the raised level at that clock.
  T_S  M8's span fraction for other kinds (levels_phi136, levels_phi146 below): every arm's energy S(zeros) + phi (S(top) -
       S(zeros)), phi = D_M8(kind) / D_M8(top).

Nothing here opens a device. SPDX-License-Identifier: Apache-2.0
"""
import gzip
import json
import math
import os
import sys

sys.dont_write_bytecode = True
import numpy as np  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
LAB = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
G3D = os.path.join(LAB, "docs/reports/data/2026-11-03-q139q-gemm-g3")
sys.path.insert(0, G3D)
import g3_model as G  # noqa: E402  (G3 as frozen: chain, cap, trip rule, gaps, schedule, window)

M9P = os.path.join(LAB, "docs/reports/data/2026-11-04-q140l-a2-session-terms/m9_a2.json")
M9 = json.load(open(M9P))
BETA = M9["params"]["beta"]
T_REF = M9["params"]["T_ref_c"]
DELTA_FALLBACK = dict(M9["fallback_delta_w"])
F_DIP = 618.0
DT = G.DT
A, R, P_REF = G.A, G.R, G.P_REF
RON = float(R @ (1.0 - A))


def simulate4(levels, on, x0, T_anchor, T_start, trip, k, T_ref=None, shift=0.0, dip=None, p_scale=1.0):
    """G3's loop with G4's terms. levels: P0 {600, 700, 800}; on: bool per step; x0, T_anchor: the chain's start state and
    anchor; T_start: the run's start die (G3's leakage reference when T_ref is None); trip: the held die; k: G3's k_eff when
    T_ref is None, T_D's k_D otherwise; shift: beta x delta (T_Z), 0 without it; dip: (d_G, P_G) for T_G or None.
    Returns per step T (C), P (W), F (MHz)."""
    n = len(on)
    x = np.array(x0, float)
    Tk = T_anchor + float(R @ x)
    ref = T_start if T_ref is None else T_ref
    T = np.empty(n)
    P = np.empty(n)
    F = np.empty(n)
    p_on_last = levels[800] * p_scale + shift
    # the dip schedule: per step, the share of the step inside a process's opening dip (computed per contiguous kernel stretch)
    dipw = np.zeros(n)
    starts = []
    if dip is not None and dip[0] > 0:
        i = 0
        while i < n:
            if on[i] and (i == 0 or not on[i - 1]):
                j = i
                while j < n and on[j]:
                    j += 1
                nd = dip[0] * (j - i)          # the dip's length in steps (the process's kernel steps x d_G)
                full = int(math.floor(nd))
                dipw[i:i + full] = 1.0
                if i + full < j:
                    dipw[i + full] = nd - full
                starts.append(i)
                i = j
            else:
                i += 1
    gate = {}
    for kk in range(n):
        leak = k * (Tk - ref) + shift
        L = {f: levels[f] * p_scale + leak for f in (600, 700, 800)}
        if on[kk]:
            fc = G.cap_clock(L)
            pc = G.p_at(L, fc)
            p_trip = P_REF + (trip - T_anchor - float(R @ (A * x))) / RON
            if p_trip >= pc:
                p, f = pc, fc
            else:
                p = max(p_trip, L[600])
                f = G.f_at(L, p)
            if dipw[kk] > 0:
                if kk in starts or not (kk - 1) in gate:
                    gate[kk] = L[800] >= dip[1]
                else:
                    gate[kk] = gate[kk - 1]
                if gate[kk]:
                    fd = min(F_DIP, f)
                    pd = G.p_at(L, fd)
                    w = dipw[kk]
                    p, f = w * pd + (1 - w) * p, w * fd + (1 - w) * f
            p_on_last = p
        else:
            p = P_REF + G.OFF_SHARE * (p_on_last - P_REF)
            f = float("nan")
        x = A * x + (1.0 - A) * (p - P_REF)
        Tk = T_anchor + float(R @ x)
        T[kk], P[kk], F[kk] = Tk, p, f
    return T, P, F


def run_arm(c, arm):
    """one input record (posthoc-g3-inputs.json's layout) through an arm {k, trip, T_ref, zeros, dip, lev}; window means"""
    lev = arm.get("lev") or {int(f): v for f, v in c["lev"].items()}
    on = np.asarray(c["on"], bool)
    gg = c["gg0"] + np.arange(len(on)) * DT
    t = c["type"]
    shift = BETA * DELTA_FALLBACK[t] if arm.get("zeros") else 0.0
    T, P, F = simulate4(lev, on, np.array(c["x0"]), c["anc"], c["T_start"], arm["trip"], arm["k"], T_ref=arm.get("T_ref"),
                        shift=shift, dip=arm.get("dip"))
    return G.window_means(gg, on, T, P, F, c["t1"])


def cell_type(cell):
    return cell.split("-")[1]


# ------------------------------------------------------------------ E159's nine holds in posthoc-g3-inputs.json's layout
def e159_inputs():
    """E159's holds rebuilt on e159_g3.score's path, unchanged: the chain open loop on the measured trace up to the hold's first
    process, the anchor over the 20 s before it, the hold's own kernel windows, the window = in-kernel samples of the last 40 s"""
    sdir = os.path.join(LAB, "docs/reports/data/2026-11-03-e159-gemm-sustained/aifoundry2/s1")
    P = json.load(open(os.path.join(G3D, "predictions-e159.json")))
    hm = G.hm
    runs = [json.loads(x) for x in open(os.path.join(sdir, "runs.jsonl"))]
    Lr = [json.loads(x) for x in gzip.open(os.path.join(sdir, "launches.jsonl.gz"), "rt")]
    paths = sorted(os.path.join(sdir, "tel", f) for f in os.listdir(os.path.join(sdir, "tel")) if f.endswith(".jsonl.gz") or f.endswith(".jsonl"))
    tel = hm.load_tel(paths, sensor="fw")
    t = tel["t"]
    ok = np.isfinite(tel["T"]) & np.isfinite(tel["P"])
    g = np.arange(t[ok][0], t[ok][-1], DT)
    Pm, Tm = np.interp(g, t[ok], tel["P"][ok]), np.interp(g, t[ok], tel["T"][ok])
    Xm = G.chain_open(Pm)
    out = []
    for r in runs:
        cell = r.get("label")
        if r.get("processes", 1) < 2 or cell not in P["cells"]:
            continue
        procs = [p for p in Lr if p["run"] == r["run"] and p.get("role") == "work"]
        if not procs:
            continue
        t0, t1 = min(p["t_start_ms"] for p in procs) / 1000.0, max(p["t_end_ms"] for p in procs) / 1000.0
        kw = [(k["t_start_ms"] / 1000.0, k["t_end_ms"] / 1000.0) for p in procs for k in p.get("sparsity", []) if k.get("t_start_ms") and k.get("t_end_ms")]
        i0, i1 = int(np.searchsorted(g, t0)), int(np.searchsorted(g, t1))
        gg = g[i0:i1 + 1]
        on = np.zeros(len(gg), bool)
        for a, b in kw:
            on |= (gg >= a) & (gg <= b)
        ma = (g >= t0 - G.ANCHOR_S) & (g < t0)
        anc = float(np.mean(Tm[ma] - Xm[ma] @ G.R))
        x0 = Xm[i0 - 1]
        Ts = anc + float(G.R @ x0)
        inw = np.zeros(len(t), bool)
        for a, b in kw:
            inw |= (t >= a) & (t <= b)
        mw = inw & (t >= t1 - G.SUS_LAST_S) & (t <= t1)
        meas = {"mhz": float(np.nanmean(tel["mhz"][mw])), "w": float(np.mean(tel["P"][mw])), "die": float(np.mean(tel["T"][mw]))}
        die_start = float(tel["T"][inw & (t >= t0)][0])
        lev = {str(f): v for f, v in P["cells"][cell]["P0_w"].items()}
        out.append({"session": "E159", "run": r["run"], "cell": cell, "lev": lev, "on": [bool(v) for v in on], "gg0": float(gg[0]), "t1": t1,
                    "x0": [float(v) for v in x0], "anc": anc, "T_start": Ts, "die_start_meas": die_start, "meas": meas})
    return out


# ------------------------------------------------------------------ T_S: E136's law with M8's span fraction
def _m136():
    sys.path.insert(0, os.path.join(LAB, "tools/claims-v3/e136"))
    import make_predictions_e136 as M136  # noqa: E402
    return M136


def levels_phi136(g, t, phi, model="P1"):
    """E136's frozen law (make_predictions_e136.levels) for one of its GEMMs with every arm's S interpolated by phi between the
    format's zeros and top S (E107's pinned S, unchanged)"""
    M136 = _m136()
    nl, nf = M136.lines(g, model)
    E = {}
    for a in ("c1", "c8s", "c16"):
        sz, st = M136.S_arm(a, t, "zeros"), M136.S_arm(a, t, "top")
        E[a] = (sz + phi * (st - sz)) * M136.S107["T"][f"{a}.{t}"]
    e = E["c1"] + nl / 128.0 * (E["c8s"] - E["c1"]) + nf / 128.0 * (E["c16"] - E["c1"])
    S = e / M136.T_a3_600(g, t, model)
    c = M136.CZ[t] + (S - M136.E107[f"{t}.zeros"]["S"]["mean"]) / M136.XFER
    t6 = M136.T_a2(g, t, 600, model)
    return {f: M136.B[f] + c * M136.SF[f] * (600.0 * t6) / (f * M136.T_a2(g, t, f, model)) for f in (600, 700, 800)}


def _m146():
    sys.path.insert(0, os.path.join(LAB, "tools/claims-v3/e146"))
    sys.path.insert(0, os.path.join(LAB, "tools/claims-v3/e146/desk"))
    import make_predictions_e146 as M146  # noqa: E402
    import reuse_e146 as RD  # noqa: E402
    return M146, RD


def add_shape146(label, MB, NB, KB):
    """registers a new shape in E146's desk dict as e159_g3.desk() does (the desk's 32 MB split, unchanged)"""
    M146, RD = _m146()
    if label not in M146.DESK["shapes"]:
        sp = RD.split(("large", MB, NB, KB), 32)
        M146.DESK["shapes"][label] = {"lines": {"32MB": sp}, "store_every_ops": KB * 32}
    return M146.DESK["shapes"][label]["lines"]["32MB"]


def levels_phi146(s, t, phi):
    """E146's levels0 (E136's law for explicit lines) with every arm's S interpolated by phi (phi 0 = zeros, 1 = top)"""
    M146, _ = _m146()
    M136 = M146.M136
    d = M146.ln(s)
    E = {}
    for a in ("c1", "c8s", "c16"):
        sz, st = M136.S_arm(a, t, "zeros"), M136.S_arm(a, t, "top")
        E[a] = (sz + phi * (st - sz)) * M136.S107["T"][f"{a}.{t}"]
    e = E["c1"] + d["n_L3"] / 128.0 * (E["c8s"] - E["c1"]) + d["n_F"] / 128.0 * (E["c16"] - E["c1"])
    S = e / M146.T_a3_600(s, t)
    c = M146.CZ[t] + (S - M136.E107[f"{t}.zeros"]["S"]["mean"]) / M146.XFER
    t6 = M146.T0(s, t, 600)
    return {f: M146.B[f] + c * M146.SF[f] * (600.0 * t6) / (f * M146.T0(s, t, f)) for f in (600, 700, 800)}


# ------------------------------------------------------------------ M8's D for the span fraction
def m8_D_rows(keys):
    """M8's frozen D (600 MHz, aifoundry3's footing) for rows of rows-m8.json given as (exp, card, kind): rate x features . coef_J"""
    q = os.path.join(LAB, "docs/reports/data/2026-11-03-q139m-model")
    m8 = json.load(open(os.path.join(q, "m8.json")))
    rows = json.load(open(os.path.join(q, "rows-m8.json")))
    out = {}
    for exp, card, kind in keys:
        rr = [r for r in rows if r["exp"] == exp and r["card"] == card and r["kind"] == kind]
        if not rr:
            out[(exp, card, kind)] = None
            continue
        r = rr[0]
        fam = m8["families"]["int8" if r["type"] == "int8" else "float"]
        d = float(r["rate"]) * sum(float(r["f"][qq]) * float(c) for qq, c in zip(fam["terms"], fam["coef_J"]))
        out[(exp, card, kind)] = {"D_M8": d, "D_meas": r.get("D"), "type": r["type"]}
    return out
