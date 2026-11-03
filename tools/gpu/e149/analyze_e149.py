"""E149's reduction, fit, freeze, prediction and scoring (E149.md). Written before any GPU call.

    python analyze_e149.py reduce <logs/<run>> <out.json>            # one stage's run: windows -> y per kind
    python analyze_e149.py fit <reduce1.json> <logs/<run1>> <model.json>   # stage 1 -> the frozen models + heat
    python analyze_e149.py predict <model.json> <logs/<run1>> <pred.json>  # stage 2's kinds, from stage-1 features
    python analyze_e149.py score <model.json> <pred.json> <reduce2.json> <logs/<run2>> <score.json>

Needs numpy (2.x). Every number a rule reads is written to the JSON outputs; a text summary goes to stdout.
"""
import glob
import gzip
import json
import math
import os
import sys

import numpy as np

CAP_BITS = 0x4 | 0x8 | 0x20 | 0x40 | 0x80     # SW power cap, HW slowdown, SW thermal, HW thermal, HW power brake
SETTLE = {"cell": 1.5, "ref": 1.0, "pre": 5.0, "hold": 1.0}
FIELDS = {"bf16": {"sign": [15], "exp": list(range(7, 15)), "mant": list(range(0, 7))},
          "fp16": {"sign": [15], "exp": list(range(10, 15)), "mant": list(range(0, 10))},
          "int8": {"sign": [7], "high": [4, 5, 6], "low": [0, 1, 2, 3]}}
LAGS = [1, 2, 4, 8, 16, 32]
MODELS = ["G0", "S1", "G1", "G1s", "G2", "G3"]
PRIMARY = "G1"


# ---------------------------------------------------------------------------------------------------------------
def _jl_gz(path):
    out = []
    with gzip.open(path, "rt") as f:
        for line in f:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out


def load_unit(udir):
    steps = []
    for p in sorted(glob.glob(os.path.join(udir, "steps", "*.json.gz"))):
        with gzip.open(p, "rt") as f:
            steps.append(json.load(f))
    samples = []
    for p in sorted(glob.glob(os.path.join(udir, "samples", "*.jsonl.gz"))):
        samples += [r for r in _jl_gz(p) if "status" not in r]
    feats = {}
    for p in glob.glob(os.path.join(udir, "features-*.json.gz")):
        with gzip.open(p, "rt") as f:
            feats[os.path.basename(p)[9:-8]] = json.load(f)
    static = next((s["static"] for s in steps if s.get("op") == "static"), {})
    ts = np.array([0.5 * (r["t"] + r["tb"]) for r in samples])
    return {"steps": steps, "samples": samples, "ts": ts, "feats": feats, "static": static}


def wstats(u, t_a, t_b, settle, max_sm):
    ss = u["samples"]
    ts = u["ts"]
    lo, hi = np.searchsorted(ts, t_a + settle), np.searchsorted(ts, t_b - 0.05)
    sel = [r for r in ss[lo:hi]]
    if not sel:
        return {"n": 0, "valid": False}
    p = [r["p_mw"] / 1000.0 for r in sel if r.get("p_mw") is not None]
    tmp = [r["temp"] for r in sel if r.get("temp") is not None]
    sm = [r["sm"] for r in sel if r.get("sm") is not None]
    rsn = [int(r.get("rsn") or 0) for r in sel]
    e = [(0.5 * (r["t"] + r["tb"]), r["e_mj"]) for r in sel if r.get("e_mj") is not None]
    slope = None
    if len(e) >= 2 and e[-1][0] > e[0][0]:
        slope = (e[-1][1] - e[0][1]) / 1000.0 / (e[-1][0] - e[0][0])
    capfrac = sum(1 for x in rsn if x & CAP_BITS) / len(rsn)
    out = {"n": len(sel), "p_w": float(np.mean(p)), "p_sd": float(np.std(p)), "p_e_w": slope,
           "t_c": float(np.mean(tmp)), "sm_min": min(sm), "sm_mean": float(np.mean(sm)), "cap_frac": capfrac,
           "rsn_or": int(np.bitwise_or.reduce(rsn)) if rsn else 0}
    out["valid"] = bool(out["sm_min"] >= max_sm and capfrac == 0.0 and out["n"] >= 0.6 * (t_b - t_a - settle) / 0.1)
    return out


def reduce_run(run_dir):
    """Every unit's passes -> d (cell minus the mean of its two bracketing reference windows) and y (d minus the mean
    d of its format's zeros windows in that pass), per window; then per (unit, kind) and per kind."""
    out = {"units": {}, "kinds": {}}
    for udir in sorted(glob.glob(os.path.join(run_dir, "*"))):
        if not os.path.isdir(udir):
            continue
        un = os.path.basename(udir)
        u = load_unit(udir)
        st = u["static"]
        max_sm = st.get("max_clock_sm") if isinstance(st.get("max_clock_sm"), int) else 1410
        rec = {"static": {k: v for k, v in st.items() if not k.startswith("nvidia-smi")}, "passes": {}, "holds": [],
               "heat": {}, "flops": {}}
        for s in u["steps"]:
            if s.get("op") == "hold":
                w = s["windows"][0]
                rec["heat"][s["label"]] = {"t_a": w["t_a"], "t_b": w["t_b"], "kind": w["kind"]}
            if s.get("op") == "pass":
                ws = s["windows"]
                rows = []
                for i, w in enumerate(ws):
                    w["st"] = wstats(u, w["t_a"], w["t_b"], SETTLE[w["role"]], max_sm)
                for i, w in enumerate(ws):
                    if w["role"] != "cell":
                        continue
                    r0, r1 = ws[i - 1], ws[i + 1] if i + 1 < len(ws) else None
                    if r1 is None or r0["role"] != "ref" or r1["role"] != "ref":
                        continue
                    ok = w["st"]["valid"] and r0["st"]["valid"] and r1["st"]["valid"]
                    pr = 0.5 * (r0["st"]["p_w"] + r1["st"]["p_w"])
                    tr = 0.5 * (r0["st"]["t_c"] + r1["st"]["t_c"])
                    fl = (2.0 * w.get("n", 2048) ** 3 * w["calls"] / (w["gpu_ms"] / 1000.0) / 1e12
                          if w["gpu_ms"] > 0 else None)
                    rows.append({"kind": w["kind"], "d": w["st"]["p_w"] - pr, "dT": w["st"]["t_c"] - tr,
                                 "p": w["st"]["p_w"], "p_e": w["st"]["p_e_w"], "p_ref": pr, "T": w["st"]["t_c"],
                                 "valid": ok, "cell_valid": w["st"]["valid"], "sm_min": w["st"]["sm_min"],
                                 "cap_frac": w["st"]["cap_frac"], "rsn_or": w["st"]["rsn_or"], "n": w["st"]["n"],
                                 "tflops": fl, "t_a": w["t_a"]})
                zeros = {}
                for r in rows:
                    if r["kind"].endswith(".zeros") and r["valid"]:
                        zeros.setdefault(r["kind"].split(".")[0], []).append(r["d"])
                for r in rows:
                    f = r["kind"].split(".")[0]
                    r["y"] = (r["d"] - float(np.mean(zeros[f]))) if zeros.get(f) else None
                rec["passes"][str(s["step"]["p"])] = {"rows": rows, "zeros_d": {k: v for k, v in zeros.items()},
                                                      "ref": [w["st"] for w in ws if w["role"] == "ref"]}
            if s.get("op") == "holds":
                ws = s["windows"]
                for i in range(0, len(ws) - 1, 2):
                    pre, hold = ws[i], ws[i + 1]
                    rec["holds"].append({"kind": hold["kind"], "pre": [pre["t_a"], pre["t_b"]],
                                         "hold": [hold["t_a"], hold["t_b"]],
                                         "pre_st": wstats(u, pre["t_a"], pre["t_b"], SETTLE["pre"], max_sm),
                                         "hold_st": wstats(u, hold["t_a"], hold["t_b"], SETTLE["hold"], max_sm)})
        out["units"][un] = rec
    per = {}
    for un, rec in out["units"].items():
        for p, ps in rec["passes"].items():
            for r in ps["rows"]:
                per.setdefault(r["kind"], []).append(dict(r, unit=un, pass_=p))
    for k, rs in per.items():
        good = [r for r in rs if r["valid"] and r["y"] is not None]
        ys = [r["y"] for r in good]
        byu = {}
        for r in good:
            byu.setdefault(r["unit"], []).append(r["y"])
        out["kinds"][k] = {"n": len(ys), "n_all": len(rs), "y": float(np.mean(ys)) if ys else None,
                           "sd": float(np.std(ys, ddof=1)) if len(ys) > 1 else None,
                           "se": float(np.std(ys, ddof=1) / math.sqrt(len(ys))) if len(ys) > 1 else None,
                           "by_unit": {un: float(np.mean(v)) for un, v in byu.items()},
                           "reps": [[r["unit"], r["pass_"], r["y"]] for r in good],
                           "invalid": [[r["unit"], r["pass_"], r["sm_min"], r["cap_frac"], r["rsn_or"]] for r in rs
                                       if not r["valid"]],
                           "p_abs": float(np.mean([r["p"] for r in good])) if good else None,
                           "tflops": float(np.mean([r["tflops"] for r in good if r["tflops"]])) if good else None}
    return out


# ---------------------------------------------------------------------------------------------------------------
# The models' features (E149.md, "The model").
def _fsum(fe, key, pos):
    return sum(fe["A"][key][p] + fe["B"][key][p] for p in pos)


def _fpos(fe, key, pos):
    w = len(pos)
    if w < 2:
        return 0.0
    lo = pos[0]
    return sum((fe["A"][key][p] + fe["B"][key][p]) * ((p - lo) - (w - 1) / 2.0) / (w - 1) for p in pos)


def _asym(fe, key):
    return sum(fe["A"][key]) - sum(fe["B"][key])


def features(fe, model, lag=1):
    fmt = fe["fmt"]
    fl = FIELDS[fmt]
    c = fe["cross"]
    names, x = [], []

    def add(n, v):
        names.append(n)
        x.append(float(v))
    if model == "G0":
        add("nzprod", c["nzprod"])
        return names, x
    if model == "S1":
        add("nzprod", c["nzprod"])
        for f, pos in fl.items():
            add(f"ones_{f}", _fsum(fe, "ones", pos))
        add("negprod", c["negprod"])
        add("asym_ones", _asym(fe, "ones"))
        return names, x
    s = lag if model == "G1s" else 1
    key = f"lag{s}"
    add("nzprod", c["nzprod"])
    add("gtr", c[f"gtr{s}"])
    for f, pos in fl.items():
        add(f"flip_{f}", _fsum(fe, key, pos))
    if fmt == "bf16":
        add("pos_exp", _fpos(fe, key, fl["exp"]))
    if fmt in ("bf16", "fp16"):
        add("pos_mant", _fpos(fe, key, fl["mant"]))
    add("asym", _asym(fe, key))
    add("psgn", c[f"psgn{s}"])
    if model == "G2":
        add("acc", fe["acc"]["acc"])
    if model == "G3":
        for f, pos in fl.items():
            add(f"row_{f}", _fsum(fe, "row", pos))
    return names, x


def ols(X, y):
    X = np.asarray(X, float)
    y = np.asarray(y, float)
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    return beta


def fit_format(rows, model, lag=1):
    """rows: [(kind, fe, y)] of one format, zeros excluded. Returns coefficients, in-sample and LOKO errors."""
    names = features(rows[0][1], model, lag)[0]
    X = [features(fe, model, lag)[1] for _, fe, _ in rows]
    y = [yy for _, _, yy in rows]
    beta = ols(X, y)
    fit = np.asarray(X) @ beta
    loko = []
    for i in range(len(rows)):
        Xi = [X[j] for j in range(len(rows)) if j != i]
        yi = [y[j] for j in range(len(rows)) if j != i]
        b = ols(Xi, yi)
        loko.append(float(np.asarray(X[i]) @ b))
    res = np.asarray(y) - fit
    lres = np.asarray(y) - np.asarray(loko)
    return {"names": names, "coef": [float(b) for b in beta], "rms_in": float(np.sqrt(np.mean(res ** 2))),
            "rms_loko": float(np.sqrt(np.mean(lres ** 2))), "n": len(rows), "lag": lag,
            "rows": [{"kind": k, "y": float(yy), "fit": float(f), "loko": float(l)}
                     for (k, _, yy), f, l in zip(rows, fit, loko)]}


def predict_one(fz, fe):
    m = fz
    names, x = features(fe, m["model"], m.get("lag", 1))
    assert names == m["names"], (names, m["names"])
    return float(np.dot(x, m["coef"]))


# ---------------------------------------------------------------------------------------------------------------
# Heat: a two-pole linear model of the die temperature driven by board power, and leakage at a held load.
def _series(u, t0=None, t1=None):
    ts, ss = u["ts"], u["samples"]
    P = np.array([r["p_mw"] / 1000.0 if r.get("p_mw") is not None else np.nan for r in ss])
    T = np.array([r["temp"] if r.get("temp") is not None else np.nan for r in ss], float)
    m = np.isfinite(P) & np.isfinite(T)
    if t0 is not None:
        m &= ts >= t0
    if t1 is not None:
        m &= ts <= t1
    return ts[m], P[m], T[m]


def _filt(ts, P, tau, x0=None):
    """First-order low-pass of power with time constant tau (zero-order hold between samples)."""
    tsl, Pl = list(map(float, ts)), list(map(float, P))
    out = [0.0] * len(Pl)
    x = Pl[0] if x0 is None else float(x0)
    out[0] = x
    for i in range(1, len(Pl)):
        x += (1.0 - math.exp(-(tsl[i] - tsl[i - 1]) / tau)) * (Pl[i - 1] - x)
        out[i] = x
    return np.array(out)


TAU1 = list(np.geomspace(0.2, 20.0, 21))
TAU2 = list(np.geomspace(8.0, 2000.0, 25))


def fit_heat(series_list):
    """series_list: [(ts, P, T)] per unit. Shared tau1, tau2, r1, r2; per unit an intercept and an initial-transient
    term exp(-(t - t0)/tau2). Grid over the taus, least squares for the rest."""
    nu = len(series_list)
    F1 = {t1: [_filt(ts, P, t1) for ts, P, T in series_list] for t1 in TAU1}
    F2 = {t2: [_filt(ts, P, t2) for ts, P, T in series_list] for t2 in TAU2}
    y = np.concatenate([T for _, _, T in series_list])
    best = None
    for t1 in TAU1:
        for t2 in TAU2:
            if t2 <= 2.0 * t1:
                continue
            cols = []
            for ui, (ts, P, T) in enumerate(series_list):
                Xu = np.zeros((len(ts), 2 + 2 * nu))
                Xu[:, 0] = F1[t1][ui]
                Xu[:, 1] = F2[t2][ui]
                Xu[:, 2 + ui] = 1.0
                Xu[:, 2 + nu + ui] = np.exp(-(ts - ts[0]) / t2)
                cols.append(Xu)
            X = np.vstack(cols)
            b = ols(X, y)
            sse = float(np.sum((y - X @ b) ** 2))
            if best is None or sse < best["sse"]:
                best = {"sse": sse, "tau1": float(t1), "tau2": float(t2), "r1": float(b[0]), "r2": float(b[1]),
                        "icpt": [float(v) for v in b[2:2 + nu]], "init": [float(v) for v in b[2 + nu:]],
                        "rms": float(np.sqrt(sse / len(y))), "n": int(len(y))}
    best["R_ss"] = best["r1"] + best["r2"]
    best["F30"] = (best["r1"] * (1 - math.exp(-30 / best["tau1"])) + best["r2"] * (1 - math.exp(-30 / best["tau2"]))) / \
        best["R_ss"]
    best["rise30_per_W"] = best["R_ss"] * best["F30"]
    best["edge"] = {"tau1": best["tau1"] in (TAU1[0], TAU1[-1]), "tau2": best["tau2"] in (TAU2[0], TAU2[-1])}
    return best


def sim_T(ts, P, hm, x0=None):
    x1 = _filt(ts, P, hm["tau1"], None if x0 is None else x0[0])
    x2 = _filt(ts, P, hm["tau2"], None if x0 is None else x0[1])
    return hm["r1"] * x1 + hm["r2"] * x2, x1, x2


def rise_cross(hm_fit_on, series):
    """Out-of-board check: rises over every 30 s window (starts every 10 s) of a unit's session, predicted with the
    model fitted on the other unit from the measured power."""
    ts, P, T = series
    Ts, _, _ = sim_T(ts, P, hm_fit_on)
    errs = []
    t = ts[0] + 60.0
    while t + 30.0 <= ts[-1]:
        i0, i1 = np.searchsorted(ts, [t, t + 30.0])
        j0, j1 = np.searchsorted(ts, [t - 1.0, t + 29.0])
        mT = np.mean(T[i1 - 10:i1]) - np.mean(T[i0 - 10:i0])
        pT = np.mean(Ts[i1 - 10:i1]) - np.mean(Ts[i0 - 10:i0])
        errs.append(mT - pT)
        t += 10.0
    return float(np.sqrt(np.mean(np.square(errs)))) if errs else None, len(errs)


def leakage(u, heat_win):
    ts, P, T = _series(u, heat_win["t_a"] + 10.0, heat_win["t_b"] - 0.1)
    if len(ts) < 50:
        return None
    b = ols(np.column_stack([np.ones_like(T), T]), P)
    return {"lambda_w_per_c": float(b[1]), "T_range": [float(T.min()), float(T.max())],
            "P_range": [float(P.min()), float(P.max())], "n": int(len(ts))}


# ---------------------------------------------------------------------------------------------------------------
def stage1_rules(red):
    """Registered structure tests on stage 1's measured y (E149.md, "Rules, stage 1")."""
    K = red["kinds"]

    def g(k):
        v = K.get(k)
        return (v["y"], v["se"] if v and v["se"] is not None else float("nan"), v["n"]) if v and v["y"] is not None \
            else (None, None, 0)

    def diff(a, b):
        ya, sa, na = g(a)
        yb, sb, nb = g(b)
        if ya is None or yb is None:
            return None
        return {"a": a, "b": b, "diff": ya - yb, "se": math.sqrt(sa ** 2 + sb ** 2), "na": na, "nb": nb}

    def resolved_pos(d):
        return d is not None and d["na"] >= 3 and d["nb"] >= 3 and d["diff"] > 2 * d["se"]

    R = {}
    # V0: >= 90% of the kinds keep every window valid on each board (the size kept the data off the cap)
    units = sorted({r[0] for v in K.values() for r in v.get("reps", [])} |
                   {r[0] for v in K.values() for r in v.get("invalid", [])})
    v0 = {}
    for un in units:
        bad = [k for k, v in K.items() if any(r[0] == un for r in v.get("invalid", []))]
        v0[un] = {"kinds": len(K), "with_invalid": len(bad), "share_ok": 1 - len(bad) / max(1, len(K)), "bad": bad}
    if v0:
        R["V0"] = {"verdict": "HOLDS" if all(x["share_ok"] >= 0.9 for x in v0.values()) else "FAILS", "units": v0}
    # R1a: the scattered zero ladders fall with the zero fraction (no resolved rise between rungs)
    for fmt, base in (("bf16", "bf16.randn"), ("int8", "int8.rand")):
        lad = [base] + [f"{fmt}.zs{f}" for f in (25, 50, 75, 90)] + [f"{fmt}.zeros"]
        steps = [diff(lad[i + 1], lad[i]) for i in range(len(lad) - 1)]
        bad = [s for s in steps if s is None or (s["diff"] > 2 * s["se"])]
        R[f"R1a_{fmt}"] = {"verdict": "HOLDS" if not bad else "FAILS", "steps": steps}
    # R1b: blocks of zeros cost less than scattered zeros, at 50% and 75% (bf16)
    ds = [diff("bf16.zs50", "bf16.zb50"), diff("bf16.zs75", "bf16.zb75")]
    R["R1b"] = {"verdict": "HOLDS" if all(resolved_pos(d) for d in ds) else "FAILS", "diffs": ds}
    # R2: the Hamming ladders follow flips, not ones: the middle rung rises, the all-flipped constant comes back
    lads = {"bf16.mant": ("bf16.base1", "bf16.mk3", "bf16.mk7"), "bf16.exp": ("bf16.base1", "bf16.ek3", "bf16.ek5"),
            "fp16.mant": ("fp16.base1", "fp16.mk5", "fp16.mk10"), "int8.bits": ("int8.base1", "int8.k3", "int8.k7")}
    for nm, (b0, mid, top) in lads.items():
        up = diff(mid, b0)
        back = diff(top, b0)
        ok = resolved_pos(up) and back is not None and back["diff"] < 0.5 * up["diff"]
        R[f"R2_{nm}"] = {"verdict": "HOLDS" if ok else "FAILS", "mid_minus_base": up, "top_minus_base": back}
    # R3a: a random sign costs at constant magnitude; R3b: a fixed negative sign costs nothing extra
    d = diff("bf16.srand", "bf16.sfix")
    R["R3a"] = {"verdict": "HOLDS" if resolved_pos(d) else "FAILS", "diff": d}
    e = diff("bf16.sfixAneg", "bf16.sfix")
    lim = max(2 * e["se"], 0.1 * d["diff"]) if (d and e) else None
    R["R3b"] = {"verdict": "HOLDS" if (e and abs(e["diff"]) <= lim) else "FAILS", "diff": e, "limit": lim}
    # R4a: sorting along K saves against the same values shuffled
    d = diff("bf16.dshufK", "bf16.dsortK")
    R["R4a"] = {"verdict": "HOLDS" if resolved_pos(d) else "FAILS", "diff": d}
    # R4b: the ET-SoC-1 form's lag: consecutive along K carries the flips, so a period-2 square wave costs more
    # than a period-128 one (blocks 1 against 64)
    d = diff("bf16.sq1", "bf16.sq64")
    R["R4b"] = {"verdict": "HOLDS" if resolved_pos(d) else "FAILS", "diff": d,
                "ladder": {b: g(f"bf16.sq{b}")[:2] for b in (1, 2, 4, 8, 16, 64)}}
    # B1: the two boards agree on stage 1's kinds
    ka = [(k, v["by_unit"]) for k, v in K.items() if v["y"] is not None and len(v["by_unit"]) == 2
          and not k.endswith(".zeros")]
    if ka:
        ua, ub = sorted(ka[0][1].keys())
        a = np.array([v[ua] for _, v in ka])
        b = np.array([v[ub] for _, v in ka])
        slope = float(np.dot(a, b) / np.dot(a, a))
        rmsd = float(np.sqrt(np.mean((a - b) ** 2)))
        span = K["bf16.randn"]["y"]
        R["B1"] = {"verdict": "HOLDS" if (0.9 <= slope <= 1.1 and rmsd <= 0.05 * span) else "FAILS",
                   "slope_b_on_a": slope, "rms_diff_w": rmsd, "limit_w": 0.05 * span, "n": len(ka)}
    return R


def do_fit(red_path, run1_dir, out_path):
    red = json.load(open(red_path))
    units = {os.path.basename(d): load_unit(d) for d in sorted(glob.glob(os.path.join(run1_dir, "*")))
             if os.path.isdir(d)}
    un0 = sorted(units)[0]
    fe1 = units[un0]["feats"]["1"]
    for un, u in units.items():                       # the features are the same bytes on both boards
        for k, v in u["feats"]["1"].items():
            assert v["sha_A"] == fe1[k]["sha_A"] and v["sha_B"] == fe1[k]["sha_B"], (un, k)
    K = red["kinds"]
    rows = {f: [] for f in FIELDS}
    for k, v in K.items():
        fmt = k.split(".")[0]
        if k.endswith(".zeros") or v["y"] is None or k not in fe1:
            continue
        rows[fmt].append((k, fe1[k], v["y"]))
    out = {"models": {}, "lag_scan": {}}
    for m in MODELS:
        if m == "G1s":
            continue
        out["models"][m] = {f: dict(fit_format(rows[f], m), model=m) for f in FIELDS}
    for s in LAGS:
        fits = {f: fit_format(rows[f], "G1s", s) for f in FIELDS}
        allres = [r["y"] - r["loko"] for f in FIELDS for r in fits[f]["rows"]]
        out["lag_scan"][str(s)] = {"rms_loko_pooled": float(np.sqrt(np.mean(np.square(allres)))),
                                   "by_fmt": {f: fits[f]["rms_loko"] for f in FIELDS}}
    best = min(LAGS, key=lambda s: out["lag_scan"][str(s)]["rms_loko_pooled"])
    out["models"]["G1s"] = {f: dict(fit_format(rows[f], "G1s", best), model="G1s") for f in FIELDS}
    out["G1s_lag"] = best
    out["span_w"] = K["bf16.randn"]["y"]
    out["zeros_offset_w"] = {}
    for f in FIELDS:                                   # P(zeros of f) - P(zeros bf16), reference-differenced
        dz = [np.mean(ps["zeros_d"][f]) - np.mean(ps["zeros_d"]["bf16"]) for rec in red["units"].values()
              for ps in rec["passes"].values() if ps["zeros_d"].get(f) and ps["zeros_d"].get("bf16")]
        out["zeros_offset_w"][f] = float(np.mean(dz))
    # heat
    ser, leak = [], {}
    for un, u in units.items():
        hw = red["units"][un]["heat"]
        t0 = hw["heat_ref"]["t_a"] - 25.0
        lastp = max(r["t_a"] for ps in red["units"][un]["passes"].values() for r in ps["rows"]) + 10.0
        ser.append(_series(u, t0, lastp))
        leak[un] = leakage(u, hw["heat_ref"])
    hm = fit_heat(ser)
    per_unit = {}
    for i, un in enumerate(units):
        per_unit[un] = fit_heat([ser[i]])
    cross = []
    names = list(units)
    if len(names) == 2:
        for i, j in ((0, 1), (1, 0)):
            rms, n = rise_cross(per_unit[names[i]], ser[j])
            cross.append({"fit_on": names[i], "scored_on": names[j], "rms_c": rms, "n": n})
    sig_cross = float(np.sqrt(np.mean([c["rms_c"] ** 2 for c in cross]))) if cross else None
    lam = float(np.mean([v["lambda_w_per_c"] for v in leak.values() if v]))
    out["heat"] = {"pooled": hm, "per_unit": per_unit, "cross": cross, "sigma_cross_c": sig_cross,
                   "leakage": leak, "lambda_w_per_c": lam}
    out["band"] = {f: 1.645 * out["models"][PRIMARY][f]["rms_loko"] for f in FIELDS}
    out["rules_stage1"] = stage1_rules(red)
    out["units"] = {un: {k: v for k, v in red["units"][un]["static"].items() if k in
                         ("name", "uuid_sha12", "driver", "vbios", "power_enforced_mw", "max_clock_sm")}
                    for un in red["units"]}
    with open(out_path, "w") as f:
        json.dump(out, f, indent=1, sort_keys=True)
    return out


def do_predict(model_path, run1_dir, out_path):
    mz = json.load(open(model_path))
    units = {os.path.basename(d): load_unit(d) for d in sorted(glob.glob(os.path.join(run1_dir, "*")))
             if os.path.isdir(d)}
    fe2 = None
    for un, u in units.items():
        f2 = u["feats"]["2"]
        if fe2 is None:
            fe2 = f2
        for k, v in f2.items():
            assert v["sha_A"] == fe2[k]["sha_A"] and v["sha_B"] == fe2[k]["sha_B"], (un, k)
    pred = {"kinds": {}}
    for k, fe in fe2.items():
        fmt = fe["fmt"]
        if k.endswith(".zeros"):
            continue
        p = {m: predict_one(mz["models"][m][fmt], fe) for m in MODELS}
        pred["kinds"][k] = {"fmt": fmt, "pred": p, "band90_w": mz["band"][fmt], "sha_A": fe["sha_A"],
                            "sha_B": fe["sha_B"], "blind": k != "bf16.randn",
                            "stats": {"A": fe["A"]["stats"], "B": fe["B"]["stats"]},
                            "nzprod": fe["cross"]["nzprod"]}
    with open(out_path, "w") as f:
        json.dump(pred, f, indent=1, sort_keys=True)
    return pred


def heat_holds(mz, u, red2_unit, pred):
    """Each stage-2 hold's die rise (mean of the hold's last 1 s minus the pre-hold's last 1 s), against the frozen
    heat model driven by (a) the measured power, (b) the blind power: the pre-hold's measured zeros plus the kind's
    format offset and frozen prediction, plus the frozen leakage slope times the simulated rise."""
    hm = mz["heat"]["pooled"]
    lam = mz["heat"]["lambda_w_per_c"]
    ts, P, T = _series(u)
    out = []
    for h in red2_unit["holds"]:
        k = h["kind"]
        t_h, t_e = h["hold"]
        i_h, i_e = np.searchsorted(ts, [t_h, t_e])
        meas = float(np.mean(T[i_e - 10:i_e]) - np.mean(T[i_h - 10:i_h]))
        Tm, _, _ = sim_T(ts[:i_e], P[:i_e], hm)
        rise_m = float(np.mean(Tm[i_e - 10:i_e]) - np.mean(Tm[i_h - 10:i_h]))
        rec = {"kind": k, "meas_rise_c": meas, "pred_rise_measP_c": rise_m,
               "p_hold_meas_w": h["hold_st"].get("p_w"), "p_pre_w": h["pre_st"].get("p_w"),
               "valid": bool(h["hold_st"].get("valid")) and bool(h["pre_st"].get("valid"))}
        if k in pred["kinds"]:
            fmt = pred["kinds"][k]["fmt"]
            p_kind = h["pre_st"]["p_w"] + mz["zeros_offset_w"][fmt] + pred["kinds"][k]["pred"][PRIMARY]
            Pb = P[:i_e].copy()
            x1 = _filt(ts[:i_h + 1], P[:i_h + 1], hm["tau1"])[-1]
            x2 = _filt(ts[:i_h + 1], P[:i_h + 1], hm["tau2"])[-1]
            T0 = hm["r1"] * x1 + hm["r2"] * x2
            Tsim = [T0]
            pb = []
            for i in range(i_h + 1, i_e):
                dt = ts[i] - ts[i - 1]
                pw = p_kind + lam * (Tsim[-1] - T0)
                pb.append(pw)
                x1 += (1 - math.exp(-dt / hm["tau1"])) * (pw - x1)
                x2 += (1 - math.exp(-dt / hm["tau2"])) * (pw - x2)
                Tsim.append(hm["r1"] * x1 + hm["r2"] * x2)
            Tb = np.array(Tsim)
            pre_mean = float(np.mean(Tm[i_h - 10:i_h]))      # the model's pre-hold level, as the measured rise uses
            rec["pred_rise_blind_c"] = float(np.mean(Tb[-10:]) - pre_mean)
            rec["p_hold_pred_w"] = float(np.mean(pb[-200:])) if pb else None
        out.append(rec)
    return out


def do_score(model_path, pred_path, red2_path, run2_dir, out_path):
    mz = json.load(open(model_path))
    pred = json.load(open(pred_path))
    red = json.load(open(red2_path))
    units = {os.path.basename(d): load_unit(d) for d in sorted(glob.glob(os.path.join(run2_dir, "*")))
             if os.path.isdir(d)}
    for un, u in units.items():                        # stage 2 ran the very bytes the predictions were made from
        f2 = u["feats"].get("2", {})
        for k, v in f2.items():
            if k in pred["kinds"]:
                assert v["sha_A"] == pred["kinds"][k]["sha_A"] and v["sha_B"] == pred["kinds"][k]["sha_B"], (un, k)
    span = mz["span_w"]
    sc = {"per_kind": {}, "models": {}, "rules": {}}
    blind = [k for k, v in pred["kinds"].items() if v["blind"] and red["kinds"].get(k, {}).get("y") is not None]
    for k in pred["kinds"]:
        v = red["kinds"].get(k)
        if not v or v["y"] is None:
            continue
        sc["per_kind"][k] = {"meas": v["y"], "se": v["se"], "n": v["n"], "by_unit": v["by_unit"],
                             "pred": pred["kinds"][k]["pred"], "band90_w": pred["kinds"][k]["band90_w"],
                             "err": {m: v["y"] - pred["kinds"][k]["pred"][m] for m in MODELS},
                             "blind": pred["kinds"][k]["blind"], "invalid": v["invalid"]}
    for m in MODELS:
        e = np.array([sc["per_kind"][k]["err"][m] for k in blind])
        byf = {}
        for f in FIELDS:
            ef = [sc["per_kind"][k]["err"][m] for k in blind if k.startswith(f + ".")]
            if ef:
                byf[f] = {"rms": float(np.sqrt(np.mean(np.square(ef)))), "bias": float(np.mean(ef)), "n": len(ef)}
        sc["models"][m] = {"rms_w": float(np.sqrt(np.mean(e ** 2))), "bias_w": float(np.mean(e)),
                           "max_abs_w": float(np.max(np.abs(e))), "n": int(len(e)), "by_fmt": byf}
    inside = [k for k in blind if abs(sc["per_kind"][k]["err"][PRIMARY]) <= sc["per_kind"][k]["band90_w"]]
    g1, g0, s1 = sc["models"][PRIMARY], sc["models"]["G0"], sc["models"]["S1"]
    nb = len(blind)
    need = math.ceil(0.75 * nb)
    sc["rules"]["P1"] = {"verdict": "HOLDS" if g1["rms_w"] <= 0.10 * span else "FAILS", "rms_w": g1["rms_w"],
                         "limit_w": 0.10 * span}
    sc["rules"]["P2"] = {"verdict": "HOLDS" if abs(g1["bias_w"]) <= 0.05 * span else "FAILS", "bias_w": g1["bias_w"],
                         "limit_w": 0.05 * span}
    sc["rules"]["P3"] = {"verdict": "HOLDS" if len(inside) >= need else "FAILS", "inside": len(inside), "of": nb,
                         "need": need, "outside": sorted(set(blind) - set(inside))}
    sc["rules"]["P4"] = {"verdict": "HOLDS" if g1["rms_w"] <= 0.7 * g0["rms_w"] else "FAILS", "g1_rms_w": g1["rms_w"],
                         "g0_rms_w": g0["rms_w"]}
    sc["rules"]["P5"] = {"verdict": "HOLDS" if g1["rms_w"] < s1["rms_w"] else "FAILS", "g1_rms_w": g1["rms_w"],
                         "s1_rms_w": s1["rms_w"]}
    # heat
    hh = {}
    for un, u in units.items():
        hh[un] = heat_holds(mz, u, red["units"][un], pred)
    sc["heat_holds"] = hh
    byk = {}
    for un, lst in hh.items():
        for r in lst:
            if r["kind"] in pred["kinds"] and pred["kinds"][r["kind"]]["blind"] and r["valid"]:
                byk.setdefault(r["kind"], []).append(r)
    hm = mz["heat"]["pooled"]
    sig_cross = mz["heat"]["sigma_cross_c"] or 0.0
    eb, em, ins = [], [], 0
    rows = {}
    for k, rs in byk.items():
        mr = float(np.mean([r["meas_rise_c"] for r in rs]))
        pb = float(np.mean([r["pred_rise_blind_c"] for r in rs]))
        pm = float(np.mean([r["pred_rise_measP_c"] for r in rs]))
        band = 1.645 * math.sqrt(sig_cross ** 2 + (hm["rise30_per_W"] * mz["band"][pred["kinds"][k]["fmt"]] / 1.645)
                                 ** 2)
        rows[k] = {"meas_rise_c": mr, "pred_blind_c": pb, "pred_measP_c": pm, "band90_c": band, "n_units": len(rs)}
        eb.append(mr - pb)
        em.append(mr - pm)
        ins += abs(mr - pb) <= band
    sc["heat"] = {"rows": rows}
    if eb:
        rb, rm = float(np.sqrt(np.mean(np.square(eb)))), float(np.sqrt(np.mean(np.square(em))))
        sc["heat"].update({"rms_blind_c": rb, "bias_blind_c": float(np.mean(eb)), "rms_measP_c": rm,
                           "bias_measP_c": float(np.mean(em)), "inside": ins, "of": len(eb)})
        sc["rules"]["H1"] = {"verdict": "HOLDS" if rb <= 0.8 else "FAILS", "rms_c": rb, "limit_c": 0.8}
        sc["rules"]["H2"] = {"verdict": "HOLDS" if rm <= 0.6 else "FAILS", "rms_c": rm, "limit_c": 0.6}
        needh = math.ceil(0.75 * len(eb))
        sc["rules"]["H3"] = {"verdict": "HOLDS" if ins >= needh else "FAILS", "inside": ins, "of": len(eb),
                             "need": needh}
    pu = mz["heat"]["per_unit"]
    if len(pu) == 2:
        a, b = [v["R_ss"] for v in pu.values()]
        sc["rules"]["H4"] = {"verdict": "HOLDS" if 0.8 <= a / b <= 1.25 else "FAILS", "ratio": a / b,
                             "R_ss": {k: v["R_ss"] for k, v in pu.items()}}
    with open(out_path, "w") as f:
        json.dump(sc, f, indent=1, sort_keys=True)
    return sc


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "reduce":
        r = reduce_run(sys.argv[2])
        with open(sys.argv[3], "w") as f:
            json.dump(r, f, indent=1, sort_keys=True)
        for k, v in sorted(r["kinds"].items()):
            print(f"{k:<18} n {v['n']}/{v['n_all']}  y {v['y'] if v['y'] is None else round(v['y'], 2)}"
                  f"  se {v['se'] if v['se'] is None else round(v['se'], 2)}  P {v['p_abs'] and round(v['p_abs'], 1)}"
                  f"  T/s {v['tflops'] and round(v['tflops'], 1)}  invalid {len(v['invalid'])}")
    elif cmd == "fit":
        o = do_fit(sys.argv[2], sys.argv[3], sys.argv[4])
        for m, fm in o["models"].items():
            print(m, {f: (round(v["rms_in"], 2), round(v["rms_loko"], 2), v["n"]) for f, v in fm.items()})
        print("G1s lag", o["G1s_lag"], "span", round(o["span_w"], 2), "heat", {k: o["heat"]["pooled"][k] for k in
                                                                               ("tau1", "tau2", "R_ss", "F30", "rms")})
        for k, v in o["rules_stage1"].items():
            print(k, v["verdict"])
    elif cmd == "predict":
        p = do_predict(sys.argv[2], sys.argv[3], sys.argv[4])
        for k, v in sorted(p["kinds"].items()):
            print(f"{k:<18}", {m: round(x, 1) for m, x in v["pred"].items()})
    elif cmd == "score":
        s = do_score(*sys.argv[2:7])
        for m, v in s["models"].items():
            print(m, {k: (round(x, 2) if isinstance(x, float) else x) for k, x in v.items() if k != "by_fmt"})
        for k, v in s["rules"].items():
            print(k, v["verdict"])
    else:
        raise SystemExit(cmd)
