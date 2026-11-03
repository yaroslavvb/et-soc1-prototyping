"""E162's reduction, the L40S smoke's size rule, the fits and freezes, the predictions and the blind scores (E162.md).
Written before any GPU call.

    python analyze_e162.py reduce <logs/<run>> <out.json> [--max-sm <MHz>]
    python analyze_e162.py choose <logs/<smoke run>> <choice.json>
    python analyze_e162.py freezeA <reduceA1.json> <logs/<runA1>> <out_dir>
    python analyze_e162.py freezeL <reduceL1.json> <logs/<runL1>> <modelA.json> <out_dir>
    python analyze_e162.py score A|L <model.json> <pred.json> <reduce2.json> <logs/<run2>> <score.json>

E149's analysis (`tools/gpu/e149/analyze_e149.py`) and its frozen files are imported and read unchanged. Needs numpy.
"""
import glob
import gzip
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools", "gpu", "e149"))
import analyze_e149 as A9  # noqa: E402

E149_DIR = os.path.join(REPO, "docs", "reports", "data", "2026-11-02-e149-gpu-model-check")
FIELDS = A9.FIELDS
LAGS = [1, 2, 4, 8, 16, 32]
RLAGS = [1, 2, 4, 8, 16, 32]
LAMS = [1e-4, 3e-4, 1e-3, 3e-3, 1e-2, 3e-2, 0.1, 0.3, 1.0]
SETTLE = A9.SETTLE
CAP_BITS = A9.CAP_BITS
BOOT_N, BOOT_SEED = 10000, 162
STABLE_RATIO = 3.0          # STABLE (i): nested rms <= 3 x in-sample rms, per format
BEAT_RATIO = 0.8            # BEAT: rms(RK) <= 0.8 x rms(G1), and the paired bootstrap's 2.5% point > 0
BRIDGE = {"bf16": ["randn", "sq1", "sq16", "sq64", "dsortK", "dshufK", "dsortM", "drollK", "mk3"],
          "fp16": ["randn", "mk5"], "int8": ["rand", "k3"]}


def _jload(p):
    if p.endswith(".gz"):
        with gzip.open(p, "rt") as f:
            return json.load(f)
    with open(p) as f:
        return json.load(f)


def _wjson(p, obj):
    with open(p, "w") as f:
        json.dump(obj, f, indent=1, sort_keys=True)


def unit_dirs(run_dir):
    """The run's unit folders, refused ones apart (DONE carries 'refused')."""
    ok, refused = [], {}
    for d in sorted(glob.glob(os.path.join(run_dir, "*"))):
        if not os.path.isdir(d):
            continue
        done = os.path.join(d, "DONE")
        r = _jload(done).get("refused") if os.path.exists(done) else None
        if r:
            refused[os.path.basename(d)] = r
        else:
            ok.append(d)
    return ok, refused


# ---------------------------------------------------------------------------------------------------------------
# The reduction: E149's `reduce_run`, unchanged in method, with the validity clock as a parameter (the L40S's held
# clock, E162.md "The L40S smoke") and refused boards left out.
def reduce_run(run_dir, max_sm=None):
    out = {"units": {}, "kinds": {}}
    dirs, refused = unit_dirs(run_dir)
    out["refused"] = refused
    for udir in dirs:
        un = os.path.basename(udir)
        u = A9.load_unit(udir)
        st = u["static"]
        msm = max_sm if max_sm else (st.get("max_clock_sm") if isinstance(st.get("max_clock_sm"), int) else 1410)
        rec = {"static": {k: v for k, v in st.items() if not k.startswith("nvidia-smi")}, "passes": {}, "holds": [],
               "heat": {}, "flops": {}, "max_sm_used": msm}
        for s in u["steps"]:
            if s.get("op") == "hold":
                w = s["windows"][0]
                rec["heat"][s["label"]] = {"t_a": w["t_a"], "t_b": w["t_b"], "kind": w["kind"]}
            if s.get("op") == "pass":
                ws = s["windows"]
                rows = []
                for w in ws:
                    w["st"] = A9.wstats(u, w["t_a"], w["t_b"], SETTLE[w["role"]], msm)
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
                                 "tflops": fl, "t_a": w["t_a"], "t_b": w["t_b"],
                                 "ref_win": [[r0["t_a"], r0["t_b"]], [r1["t_a"], r1["t_b"]]]})
                zeros = {}
                for r in rows:
                    if r["kind"].endswith(".zeros") and r["valid"]:
                        zeros.setdefault(r["kind"].split(".")[0], []).append(r["d"])
                for r in rows:
                    f = r["kind"].split(".")[0]
                    r["y"] = (r["d"] - float(np.mean(zeros[f]))) if zeros.get(f) else None
                rec["passes"][str(s["step"]["p"])] = {"rows": rows, "zeros_d": {k: v for k, v in zeros.items()},
                                                      "ref": [w["st"] for w in ws if w["role"] == "ref"]}
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
# The L40S smoke's rule (E162.md, "The L40S smoke").
def do_choose(run_dir, out_path):
    dirs, refused = unit_dirs(run_dir)
    assert dirs, ("no unrefused smoke board", refused)
    u = A9.load_unit(dirs[0])
    st = u["static"]
    smax = st.get("max_clock_sm")
    lim_w = st.get("power_enforced_mw") / 1000.0
    wins = {}
    for s in u["steps"]:
        if s.get("op") == "pass":
            for w in s["windows"]:
                if w["role"] == "cell":
                    wins[w["kind"]] = w
    # the held clock H: the NVML maximum if bf16 zeros at the smallest size hold it in every sample, else that
    # window's lowest SM clock provided no reason bit is set in it
    z0 = wins.get("bf16.zeros@1024")
    zst = A9.wstats(u, z0["t_a"], z0["t_b"], SETTLE["cell"], smax) if z0 else {"n": 0}
    if zst.get("n") and zst["sm_min"] >= smax and zst["cap_frac"] == 0:
        H, hrule = smax, "the NVML maximum, held by bf16 zeros at 1024^3"
    elif zst.get("n") and zst["rsn_or"] & CAP_BITS == 0:
        H, hrule = zst["sm_min"], "the lowest clock of bf16 zeros at 1024^3 (no reason bit), below the NVML maximum"
    else:
        H, hrule = None, "none: bf16 zeros at 1024^3 carried a reason bit"
    table = []
    for n in (1024, 1536, 2048, 3072, 4096):
        row = {"n": n}
        for nm in ("randn", "zeros"):
            w = wins.get(f"bf16.{nm}@{n}")
            if not w or H is None:
                row[nm] = None
                continue
            x = A9.wstats(u, w["t_a"], w["t_b"], SETTLE["cell"], H)
            fl = 2.0 * n ** 3 * w["calls"] / (w["gpu_ms"] / 1000.0) / 1e12 if w["gpu_ms"] > 0 else None
            row[nm] = {"p_w": x.get("p_w"), "sm_min": x.get("sm_min"), "sm_mean": x.get("sm_mean"),
                       "cap_frac": x.get("cap_frac"), "rsn_or": x.get("rsn_or"), "valid": x.get("valid"),
                       "t_c": x.get("t_c"), "tflops": fl, "n_samples": x.get("n")}
        r, z = row["randn"], row["zeros"]
        row["qualifies"] = bool(r and z and r["valid"] and z["valid"] and r["p_w"] <= 0.9 * lim_w and
                                r["p_w"] - z["p_w"] >= 25.0)
        table.append(row)
    q = [row["n"] for row in table if row["qualifies"]]
    choice = {"gpu": st.get("name"), "uuid_sha12": st.get("uuid_sha12"), "enforced_w": lim_w, "nvml_max_sm": smax,
              "held_clock": H, "held_rule": hrule, "table": table, "size": max(q) if q else None,
              "verdict": ("L40S runs bf16 at %d^3" % max(q)) if q else "cap-bound or clock-bound: the L40S arm stops",
              "refused": refused}
    _wjson(out_path, choice)
    return choice


# ---------------------------------------------------------------------------------------------------------------
# The models' features. G1 and its comparisons are E149's (`A9.features`); RK is E162's row+K form (E162.md).
def rk_features(fe, s, r):
    fmt = fe["fmt"]
    fl = FIELDS[fmt]
    c = fe["cross"]
    names, x = [], []

    def add(n, v):
        names.append(n)
        x.append(float(v))
    add("nzprod", c["nzprod"])
    add("gtr", c[f"gtr{s}"])
    add("gtrR", c[f"gtrR{r}"])
    for f, pos in fl.items():
        add(f"flip_{f}", A9._fsum(fe, f"lag{s}", pos))
    if fmt == "bf16":
        add("pos_exp", A9._fpos(fe, f"lag{s}", fl["exp"]))
    if fmt in ("bf16", "fp16"):
        add("pos_mant", A9._fpos(fe, f"lag{s}", fl["mant"]))
    add("asym", A9._asym(fe, f"lag{s}"))
    add("psgn", c[f"psgn{s}"])
    for f, pos in fl.items():
        add(f"rflip_{f}", A9._fsum(fe, f"rlag{r}", pos))
    add("rasym", A9._asym(fe, f"rlag{r}"))
    return names, x


def _scale(X):
    d = np.sqrt(np.mean(X ** 2, axis=0))
    return d, d > 1e-12


def ridge_fit(X, y, alpha):
    """Ridge without an intercept on RMS-scaled columns (a zero column gets a zero coefficient); alpha = lambda x the
    format's stage-1 row count, fixed per format."""
    d, keep = _scale(X)
    Z = X[:, keep] / d[keep]
    A = Z.T @ Z + alpha * np.eye(Z.shape[1])
    bz = np.linalg.solve(A, Z.T @ y)
    beta = np.zeros(X.shape[1])
    beta[keep] = bz / d[keep]
    return beta


def ridge_loo(X, y, alpha):
    """Exact leave-one-out residuals of `ridge_fit` with the column scale held at (X)'s."""
    d, keep = _scale(X)
    Z = X[:, keep] / d[keep]
    Ainv = np.linalg.inv(Z.T @ Z + alpha * np.eye(Z.shape[1]))
    bz = Ainv @ (Z.T @ y)
    e = y - Z @ bz
    h = np.einsum("ij,jk,ik->i", Z, Ainv, Z)
    return e / (1.0 - h)


def ols_loko(X, y):
    beta = A9.ols(X, y)
    loko = []
    for i in range(len(y)):
        m = np.arange(len(y)) != i
        loko.append(float(X[i] @ A9.ols(X[m], y[m])))
    return beta, np.asarray(loko)


class RowSet:
    """Stage-1 rows of one format: (kind, features, y)."""

    def __init__(self, rows):
        self.rows = rows
        self.kinds = [k for k, _, _ in rows]
        self.y = np.array([yy for _, _, yy in rows], float)
        self.X = {}
        self.names = {}
        for s in LAGS:
            for r in RLAGS:
                nm = rk_features(rows[0][1], s, r)[0]
                self.names[(s, r)] = nm
                self.X[(s, r)] = np.array([rk_features(fe, s, r)[1] for _, fe, _ in rows], float)

    def n(self):
        return len(self.y)


def _best_lam(X, y, N):
    sse = {lam: float(np.sum(ridge_loo(X, y, lam * N) ** 2)) for lam in LAMS}
    lam = min(LAMS, key=lambda v: sse[v])
    return lam, sse[lam], sse


def fit_rk(sets):
    """sets: {fmt: RowSet}. The registered RK procedure: (s, r) pooled over the formats by the lowest total
    leave-one-kind-out SSE, each format at its own lambda (chosen by the same closed-form LOO); then the fully nested
    error, with (s, r) and lambda re-chosen inside every outer fold on the remaining kinds only."""
    N = {f: rs.n() for f, rs in sets.items()}
    full = {}
    for f, rs in sets.items():
        for sr in rs.X:
            full[(f, sr)] = _best_lam(rs.X[sr], rs.y, N[f])
    scan = {}
    for sr in sets[next(iter(sets))].X:
        tot = sum(full[(f, sr)][1] for f in sets)
        scan[f"{sr[0]},{sr[1]}"] = {"rms_loo_pooled": math.sqrt(tot / sum(N.values())),
                                    "by_fmt": {f: math.sqrt(full[(f, sr)][1] / N[f]) for f in sets},
                                    "lam": {f: full[(f, sr)][0] for f in sets}}
    best = min(sets[next(iter(sets))].X, key=lambda sr: sum(full[(f, sr)][1] for f in sets))
    model = {"s": best[0], "r": best[1], "scan": scan, "fmts": {}}
    for f, rs in sets.items():
        lam = full[(f, best)][0]
        X, y = rs.X[best], rs.y
        beta = ridge_fit(X, y, lam * N[f])
        fit = X @ beta
        loo = y - ridge_loo(X, y, lam * N[f])
        model["fmts"][f] = {"names": rs.names[best], "coef": [float(b) for b in beta], "lam": lam,
                            "alpha": lam * N[f], "n": N[f], "rms_in": float(np.sqrt(np.mean((y - fit) ** 2))),
                            "rms_loo_at_choice": float(np.sqrt(np.mean((y - loo) ** 2))),
                            "rows": [{"kind": k, "y": float(yy), "fit": float(ff), "loo": float(ll)}
                                     for k, yy, ff, ll in zip(rs.kinds, y, fit, loo)]}
    # the fully nested error
    nested = {}
    for f, rs in sets.items():
        res = []
        for i in range(rs.n()):
            m = np.arange(rs.n()) != i
            tot = {}
            lam_f = {}
            for sr in rs.X:
                lam, sse, _ = _best_lam(rs.X[sr][m], rs.y[m], N[f])
                lam_f[sr] = lam
                tot[sr] = sse + sum(full[(g, sr)][1] for g in sets if g != f)
            sr_i = min(tot, key=lambda v: tot[v])
            beta = ridge_fit(rs.X[sr_i][m], rs.y[m], lam_f[sr_i] * N[f])
            pred = float(rs.X[sr_i][i] @ beta)
            res.append({"kind": rs.kinds[i], "y": float(rs.y[i]), "nested": pred, "s": sr_i[0], "r": sr_i[1],
                        "lam": lam_f[sr_i]})
        e = np.array([x["y"] - x["nested"] for x in res])
        nested[f] = {"rms_nested": float(np.sqrt(np.mean(e ** 2))), "rows": res,
                     "choices": sorted({(x["s"], x["r"]) for x in res})}
    model["nested"] = {f: {k: v for k, v in nv.items() if k != "choices"} for f, nv in nested.items()}
    for f in nested:
        model["nested"][f]["choices"] = [list(c) for c in nested[f]["choices"]]
    allres = [x["y"] - x["nested"] for f in nested for x in nested[f]["rows"]]
    model["rms_nested_pooled"] = float(np.sqrt(np.mean(np.square(allres))))
    # the same form by OLS at the chosen (s, r): what the ridge adds (reported)
    model["ols_at_choice"] = {}
    for f, rs in sets.items():
        b, lk = ols_loko(rs.X[best], rs.y)
        model["ols_at_choice"][f] = {"rms_in": float(np.sqrt(np.mean((rs.y - rs.X[best] @ b) ** 2))),
                                     "rms_loko": float(np.sqrt(np.mean((rs.y - lk) ** 2)))}
    return model


def predict_rk(m, fe):
    f = fe["fmt"]
    names, x = rk_features(fe, m["s"], m["r"])
    assert names == m["fmts"][f]["names"], (names, m["fmts"][f]["names"])
    return float(np.dot(x, m["fmts"][f]["coef"]))


def fit_g_form(sets, model):
    """E149's form `model` (G1, G4, ...) by E149's OLS fit_format on these rows; G4 with its own lag scan."""
    out = {}
    if model in ("G1s", "G4"):
        scan = {}
        for s in LAGS:
            fits = {f: A9.fit_format(rs.rows, model, s) for f, rs in sets.items()}
            allres = [r["y"] - r["loko"] for f in fits for r in fits[f]["rows"]]
            scan[str(s)] = float(np.sqrt(np.mean(np.square(allres))))
        best = min(LAGS, key=lambda s: scan[str(s)])
        out["lag"], out["lag_scan"] = best, scan
        out["fmts"] = {f: dict(A9.fit_format(rs.rows, model, best), model=model) for f, rs in sets.items()}
    else:
        out["fmts"] = {f: dict(A9.fit_format(rs.rows, model), model=model) for f, rs in sets.items()}
    return out


def pairing_rules(K, fmts):
    """E162.md's W rules on one stage-1 session's measured y (kinds: {kind: {y, se, n}})."""
    def g(k):
        v = K.get(k)
        return (v["y"], v["se"] if v.get("se") is not None else float("nan"), v["n"]) if v and v.get("y") is not None \
            else (None, None, 0)

    def diff(a, b):
        ya, sa, na = g(a)
        yb, sb, nb = g(b)
        if ya is None or yb is None:
            return None
        return {"a": a, "b": b, "diff": ya - yb, "se": math.sqrt(sa ** 2 + sb ** 2), "na": na, "nb": nb}

    def pos(d):
        return d is not None and d["na"] >= 3 and d["nb"] >= 3 and d["diff"] > 2 * d["se"]

    def neg(d):
        return d is not None and d["na"] >= 3 and d["nb"] >= 3 and -d["diff"] > 2 * d["se"]

    def lab(d, a, b):
        return f"{a}>{b}" if pos(d) else (f"{b}>{a}" if neg(d) else "UNRESOLVED")
    R = {}
    if "bf16" in fmts:
        ds = [diff(f"bf16.sq{b}", f"bf16.kS{b}") for b in (1, 16, 64)]
        R["W1"] = {"verdict": "HOLDS" if all(pos(d) for d in ds) else "FAILS", "diffs": ds,
                   "what": "a phase per row costs more than one shared phase (square waves along K, b = 1, 16, 64)"}
        d = diff("bf16.kS1", "bf16.kS64")
        R["W2"] = {"verdict": "HOLDS" if pos(d) else "FAILS", "diff": d,
                   "what": "with no row flips, neighbours along K are a pairing (b = 1 costs more than b = 64)"}
        d = diff("bf16.rS1", "bf16.rS64")
        R["W3"] = {"verdict": "HOLDS" if pos(d) else "FAILS", "diff": d,
                   "what": "with no K flips, neighbouring rows are a pairing (b = 1 costs more than b = 64)"}
        d = diff("bf16.sq1", "bf16.sq64")
        R["R4b"] = {"verdict": "HOLDS" if pos(d) else "FAILS", "diff": d,
                    "what": "E149's R4b again: with a phase per row, period 2 along K costs more than period 128"}
        d = diff("bf16.drollK", "bf16.rollM")
        R["W5"] = {"verdict": lab(d, "ROW", "K"), "diff": d,
                   "what": "rows random with K smooth (drollK) against K random with rows smooth (rollM)"}
        R["W6"] = {"kS1": {"verdict": lab(diff("bf16.kS1A", "bf16.kS1B"), "A", "B"),
                           "diff": diff("bf16.kS1A", "bf16.kS1B")},
                   "rS1": {"verdict": lab(diff("bf16.rS1A", "bf16.rS1B"), "A", "B"),
                           "diff": diff("bf16.rS1A", "bf16.rS1B")}}
        R["ladders"] = {"kS": {b: g(f"bf16.kS{b}")[:2] for b in (1, 2, 4, 8, 16, 32, 64)},
                        "rS": {b: g(f"bf16.rS{b}")[:2] for b in (1, 2, 4, 8, 16, 32, 64)},
                        "sq_row_phase": {b: g(f"bf16.sq{b}")[:2] for b in (1, 4, 16, 64)}}
    R["W4"] = {}
    for f in fmts:
        d = diff(f"{f}.rowc", f"{f}.colc")
        R["W4"][f] = {"verdict": lab(d, "ROW", "K"), "diff": d}
    for f in fmts:
        if f == "bf16":
            continue
        R.setdefault("other_fmts", {})[f] = {"kS1_minus_kS16": diff(f"{f}.kS1", f"{f}.kS16"),
                                             "rS1_minus_rS16": diff(f"{f}.rS1", f"{f}.rS16")}
    return R


def _feats_of_run(run_dir, name):
    """{unit: features dict} for features-<name>.json.gz in each unrefused unit; checks every unit built the same bytes."""
    dirs, _ = unit_dirs(run_dir)
    per = {}
    for d in dirs:
        p = os.path.join(d, f"features-{name}.json.gz")
        if os.path.exists(p):
            per[os.path.basename(d)] = _jload(p)
    assert per, (run_dir, name)
    un0 = sorted(per)[0]
    base = per[un0]
    mism = []
    for un, fe in per.items():
        for k, v in fe.items():
            if k in base and (v["sha_A"] != base[k]["sha_A"] or v["sha_B"] != base[k]["sha_B"]):
                mism.append([un, k])
    return base, {"units": sorted(per), "sha_mismatch": mism}


def _cmp_e149_feats(fe_new, fe_old):
    """E162's features of E149's bytes against E149's committed features: the same sha and E149's keys equal."""
    out = {"same_sha": [], "other_sha": [], "max_abs_diff": 0.0}
    for k, old in fe_old.items():
        new = fe_new.get(k)
        if new is None:
            continue
        if new["sha_A"] != old["sha_A"] or new["sha_B"] != old["sha_B"]:
            out["other_sha"].append(k)
            continue
        out["same_sha"].append(k)
        dm = 0.0
        for side in ("A", "B"):
            for key in ["ones", "row"] + [f"lag{s}" for s in LAGS]:
                a, b = np.array(new[side][key]), np.array(old[side][key])
                dm = max(dm, float(np.max(np.abs(a - b))))
        for key, v in old["cross"].items():
            dm = max(dm, abs(new["cross"][key] - v))
        out["max_abs_diff"] = max(out["max_abs_diff"], dm)
    return out


def boot_beat(e_g1, e_rk, seed=BOOT_SEED, n=BOOT_N):
    e1, e2 = np.asarray(e_g1, float), np.asarray(e_rk, float)
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(e1), size=(n, len(e1)))
    d = np.sqrt(np.mean(e1[idx] ** 2, axis=1)) - np.sqrt(np.mean(e2[idx] ** 2, axis=1))
    r1, r2 = float(np.sqrt(np.mean(e1 ** 2))), float(np.sqrt(np.mean(e2 ** 2)))
    lo, hi = float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))
    return {"rms_g1": r1, "rms_rk": r2, "diff": r1 - r2, "ci95": [lo, hi], "ratio": r2 / r1 if r1 > 0 else None,
            "verdict": "HOLDS" if (r2 <= BEAT_RATIO * r1 and lo > 0) else "FAILS", "n": len(e1)}


def stable_rule(rk, g1form):
    """STABLE (E162.md): (i) per format, RK's fully nested rms <= STABLE_RATIO x its in-sample rms (no explosion out of
    kind; E149's G4 ran 11-40x); (ii) pooled over the formats, RK's fully nested rms <= the G1 form's OLS
    leave-one-kind-out rms on the same rows (no loss against G1's form out of kind)."""
    out = {}
    for f, v in rk["fmts"].items():
        nst = rk["nested"][f]["rms_nested"]
        out[f] = {"rms_in": v["rms_in"], "rms_nested": nst, "ratio": nst / v["rms_in"] if v["rms_in"] > 0 else None,
                  "g1form_rms_loko": g1form["fmts"][f]["rms_loko"], "ok_i": bool(nst <= STABLE_RATIO * v["rms_in"])}
    g1res = [r["y"] - r["loko"] for f in rk["fmts"] for r in g1form["fmts"][f]["rows"]]
    g1pool = float(np.sqrt(np.mean(np.square(g1res))))
    ok_ii = bool(rk["rms_nested_pooled"] <= g1pool)
    return {"verdict": "HOLDS" if (all(x["ok_i"] for x in out.values()) and ok_ii) else "FAILS", "by_fmt": out,
            "pooled": {"rk_rms_nested": rk["rms_nested_pooled"], "g1form_rms_loko": g1pool, "ok_ii": ok_ii}}


# ---------------------------------------------------------------------------------------------------------------
def do_freezeA(red_path, run_dir, out_dir):
    red = _jload(red_path)
    K = red["kinds"]
    fe1, chk1 = _feats_of_run(run_dir, "A1")
    feH, chkH = _feats_of_run(run_dir, "HA")
    feE, chkE = _feats_of_run(run_dir, "E149")
    e149_f1 = _jload(os.path.join(E149_DIR, "logs", "e149-20261102-r1", "A", "features-1.json.gz"))
    e149_f2 = _jload(os.path.join(E149_DIR, "logs", "e149-20261102-r1", "A", "features-2.json.gz"))
    cmp1 = _cmp_e149_feats(feE, e149_f1)
    cmp2 = _cmp_e149_feats(feE, {k: v for k, v in e149_f2.items() if "cross" in v})
    cmpB = _cmp_e149_feats(fe1, e149_f1)            # the bridge kinds, as measured here
    r149 = _jload(os.path.join(E149_DIR, "reduce-stage1.json"))["kinds"]
    m149 = _jload(os.path.join(E149_DIR, "model-e149.json"))
    # the session scale per format, from the bridge kinds (E162 y on E149 y, through the origin)
    scale = {}
    for f, names in BRIDGE.items():
        a = np.array([r149[f"{f}.{n}"]["y"] for n in names if K.get(f"{f}.{n}", {}).get("y") is not None])
        b = np.array([K[f"{f}.{n}"]["y"] for n in names if K.get(f"{f}.{n}", {}).get("y") is not None])
        scale[f] = {"c": float(np.dot(a, b) / np.dot(a, a)), "n": int(len(a)),
                    "rms_diff_w": float(np.sqrt(np.mean((b - a) ** 2))),
                    "pairs": {n: [r149[f"{f}.{n}"]["y"], K.get(f"{f}.{n}", {}).get("y")] for n in names}}
    # the pooled rows: E149's stage-1 kinds (E149's y, E162's features of E149's bytes) + E162's new kinds (y / c)
    sets_rows = {f: [] for f in FIELDS}
    left_out = []
    for k, v in r149.items():
        f = k.split(".")[0]
        if k.endswith(".zeros") or v["y"] is None:
            continue
        if k not in feE or k not in cmp1["same_sha"]:
            left_out.append(k)
            continue
        sets_rows[f].append((k, feE[k], v["y"]))
    bridge_ids = {f"{f}.{n}" for f, ns in BRIDGE.items() for n in ns}
    new_rows = []
    for k, v in K.items():
        f = k.split(".")[0]
        if k.endswith(".zeros") or k in bridge_ids or v["y"] is None or k not in fe1:
            continue
        sets_rows[f].append((k, fe1[k], v["y"] / scale[f]["c"]))
        new_rows.append(k)
    sets = {f: RowSet(rows) for f, rows in sets_rows.items()}
    rk = fit_rk(sets)
    g1p = fit_g_form(sets, "G1")
    g4p = fit_g_form(sets, "G4")
    stable = stable_rule(rk, g1p)
    # E149's frozen G1 on E162's new stage-1 kinds (out of G1's fit; on this session's boards, at the E149 footing)
    g1_new = []
    for k in new_rows:
        f = k.split(".")[0]
        yy = K[k]["y"] / scale[f]["c"]
        g1_new.append({"kind": k, "y": yy, "g1": A9.predict_one(m149["models"]["G1"][f], fe1[k])})
    eg = [x["y"] - x["g1"] for x in g1_new]
    model = {"rk": rk, "g1p": g1p, "g4p": g4p, "stable": stable, "scale": scale, "left_out_e149_rows": left_out,
             "new_rows": new_rows, "n_rows": {f: s.n() for f, s in sets.items()},
             "g1_frozen_on_new_rows": {"rms_w": float(np.sqrt(np.mean(np.square(eg)))), "bias_w": float(np.mean(eg)),
                                       "rows": g1_new},
             "span_w": m149["span_w"], "heat": m149["heat"]["pooled"], "zeros_offset_w": m149["zeros_offset_w"],
             "checks": {"A1": chk1, "HA": chkH, "E149": chkE, "e149_stage1_feats": cmp1, "e149_stage2_feats": cmp2,
                        "bridge_feats": cmpB},
             "rules_stage1": pairing_rules(K, ["bf16", "fp16", "int8"]),
             "units": {un: {k: v for k, v in rec["static"].items() if k in
                            ("name", "uuid_sha12", "driver", "vbios", "power_enforced_mw", "max_clock_sm")}
                       for un, rec in red["units"].items()},
             "band90": {f: 1.645 * rk["nested"][f]["rms_nested"] for f in rk["fmts"]}}
    os.makedirs(out_dir, exist_ok=True)
    _wjson(os.path.join(out_dir, "model-e162-a100.json"), model)
    # predictions, frozen: the held-out kinds (A100 bytes) and, for the seen-kinds arm, E149's 17 blind kinds
    pred = {"kinds": {}, "e149_blind": {}, "rk_sr": [rk["s"], rk["r"]]}
    for k, fe in feH.items():
        f = fe["fmt"]
        if k.endswith(".zeros"):
            continue
        p = {"RK": predict_rk(rk, fe), "G1": A9.predict_one(m149["models"]["G1"][f], fe),
             "G1p": A9.predict_one(g1p["fmts"][f], fe), "G4p": A9.predict_one(g4p["fmts"][f], fe)}
        for mm in ("G0", "S1", "G1s", "G3", "G4"):
            p["e149_" + mm] = A9.predict_one(m149["models"][mm][f], fe)
        pred["kinds"][k] = {"fmt": f, "pred": p, "sha_A": fe["sha_A"], "sha_B": fe["sha_B"], "blind": True,
                            "band90_w": model["band90"][f], "stats": {"A": fe["A"]["stats"], "B": fe["B"]["stats"]}}
    for k in [k for k in feE if k not in r149]:
        fe = feE[k]
        f = fe["fmt"]
        if k.endswith(".zeros"):
            continue
        pred["e149_blind"][k] = {"fmt": f, "RK": predict_rk(rk, fe), "G1p": A9.predict_one(g1p["fmts"][f], fe),
                                 "G4p": A9.predict_one(g4p["fmts"][f], fe),
                                 "G1": A9.predict_one(m149["models"]["G1"][f], fe)}
    _wjson(os.path.join(out_dir, "predictions-e162-a100.json"), pred)
    return model, pred


def _rate(red, fmt="bf16"):
    v = [k["tflops"] for kk, k in red["kinds"].items() if kk.startswith(fmt + ".") and k.get("tflops")]
    return float(np.mean(v)) if v else None


def do_freezeL(red_path, run_dir, modelA_path, out_dir):
    red = _jload(red_path)
    K = red["kinds"]
    fe1, chk1 = _feats_of_run(run_dir, "L1")
    feH, chkH = _feats_of_run(run_dir, "HL")
    m149 = _jload(os.path.join(E149_DIR, "model-e149.json"))
    r149full = _jload(os.path.join(E149_DIR, "reduce-stage1.json"))
    mA = _jload(modelA_path)
    rows = [(k, fe1[k], v["y"]) for k, v in K.items() if not k.endswith(".zeros") and v["y"] is not None and k in fe1]
    sets = {"bf16": RowSet(rows)}
    rk = fit_rk(sets)
    g1 = fit_g_form(sets, "G1")
    g4 = fit_g_form(sets, "G4")
    stable = stable_rule(rk, g1)
    # the A100's frozen G1 and RK carried over (E150's method): rate conversion and one scale, both from stage 1
    rate_l = _rate(red)
    rate_a = _rate(r149full)
    rr = rate_l / rate_a
    carried = {}
    for nm, fn in (("G1_e149", lambda fe: A9.predict_one(m149["models"]["G1"]["bf16"], fe)),
                   ("RK_a100", lambda fe: predict_rk(mA["rk"], fe))):
        q = np.array([rr * fn(fe) for _, fe, _ in rows])
        y = np.array([yy for _, _, yy in rows])
        c = float(np.dot(y, q) / np.dot(q, q))
        carried[nm] = {"rate_ratio": rr, "scale": c, "rms_in": float(np.sqrt(np.mean((y - c * q) ** 2)))}
    # heat: E149's two-pole model refitted on this stage-1 session (both boards pooled)
    dirs, _ = unit_dirs(run_dir)
    ser = []
    for d in dirs:
        un = os.path.basename(d)
        u = A9.load_unit(d)
        ps = red["units"][un]["passes"]
        if not ps:
            continue
        t0 = min(r["t_a"] for p in ps.values() for r in p["rows"]) - 25.0
        t1 = max(r["t_b"] for p in ps.values() for r in p["rows"]) + 4.0
        ser.append(A9._series(u, t0, t1))
    heat = A9.fit_heat(ser) if ser else None
    model = {"rk": rk, "g1": g1, "g4": g4, "stable": stable, "carried": carried, "heat": heat,
             "span_w": K["bf16.randn"]["y"], "rate_tflops": {"l40s": rate_l, "a100_e149": rate_a},
             "checks": {"L1": chk1, "HL": chkH}, "rules_stage1": pairing_rules(K, ["bf16"]),
             "units": {un: {k: v for k, v in rec["static"].items() if k in
                            ("name", "uuid_sha12", "driver", "vbios", "power_enforced_mw", "max_clock_sm")}
                       for un, rec in red["units"].items()},
             "max_sm_used": {un: rec.get("max_sm_used") for un, rec in red["units"].items()},
             "band90": {"bf16": 1.645 * rk["nested"]["bf16"]["rms_nested"]}}
    os.makedirs(out_dir, exist_ok=True)
    _wjson(os.path.join(out_dir, "model-e162-l40s.json"), model)
    pred = {"kinds": {}, "rk_sr": [rk["s"], rk["r"]]}
    for k, fe in feH.items():
        if k.endswith(".zeros"):
            continue
        p = {"RK": predict_rk(rk, fe), "G1": A9.predict_one(g1["fmts"]["bf16"], fe),
             "G4": A9.predict_one(g4["fmts"]["bf16"], fe),
             "G1_e149": carried["G1_e149"]["scale"] * rr * A9.predict_one(m149["models"]["G1"]["bf16"], fe),
             "RK_a100": carried["RK_a100"]["scale"] * rr * predict_rk(mA["rk"], fe)}
        pred["kinds"][k] = {"fmt": "bf16", "pred": p, "sha_A": fe["sha_A"], "sha_B": fe["sha_B"], "blind": True,
                            "band90_w": model["band90"]["bf16"], "stats": {"A": fe["A"]["stats"], "B": fe["B"]["stats"]}}
    _wjson(os.path.join(out_dir, "predictions-e162-l40s.json"), pred)
    return model, pred


# ---------------------------------------------------------------------------------------------------------------
# Heat over a cell (E162.md, "Heat"): the cell's die reading over its two bracketing references, predicted by the frozen
# two-pole model driven by the session's measured power with the cell's samples replaced by a model's power.
def _win_mean(ts, T, t_a, t_b, settle):
    lo, hi = np.searchsorted(ts, t_a + settle), np.searchsorted(ts, t_b - 0.05)
    return float(np.mean(T[lo:hi])) if hi > lo else float("nan")


def cell_heat(u, rows, hm, preds_by_kind, zeros_d):
    """rows: one pass's reduced rows of a unit; preds_by_kind: {kind: {model: y_pred}}; zeros_d: {fmt: mean d}."""
    ts, P, T = A9._series(u)
    Ts_meas, _, _ = A9.sim_T(ts, P, hm)
    out = []
    for r in rows:
        k = r["kind"]
        if k not in preds_by_kind or not r["valid"]:
            continue
        f = k.split(".")[0]
        (a0, b0), (a1, b1) = r["ref_win"]
        meas = r["dT"]

        def dT_of(Ts):
            c = _win_mean(ts, Ts, r["t_a"], r["t_b"], SETTLE["cell"])
            q = 0.5 * (_win_mean(ts, Ts, a0, b0, SETTLE["ref"]) + _win_mean(ts, Ts, a1, b1, SETTLE["ref"]))
            return c - q
        rec = {"kind": k, "meas_dT": meas, "pred_measP": dT_of(Ts_meas)}
        sel = (ts >= r["t_a"]) & (ts <= r["t_b"])
        for mname, yp in preds_by_kind[k].items():
            Pm = P.copy()
            Pm[sel] = r["p_ref"] + zeros_d[f] + yp
            Ts_m, _, _ = A9.sim_T(ts, Pm, hm)
            rec[f"pred_{mname}"] = dT_of(Ts_m)
        out.append(rec)
    return out


def do_score(gpu, model_path, pred_path, red2_path, run2_dir, out_path):
    mz = _jload(model_path)
    pred = _jload(pred_path)
    red = _jload(red2_path)
    feA2, chk2 = _feats_of_run(run2_dir, "A2" if gpu == "A" else "L2")
    sha_bad = [k for k, v in pred["kinds"].items() if k in feA2 and (feA2[k]["sha_A"] != v["sha_A"] or
                                                                     feA2[k]["sha_B"] != v["sha_B"])]
    assert not sha_bad, ("stage 2 did not run the predicted bytes", sha_bad)
    rk_key, g1_key = "RK", "G1"
    models = sorted(next(iter(pred["kinds"].values()))["pred"].keys())
    blind = [k for k, v in pred["kinds"].items() if v["blind"] and red["kinds"].get(k, {}).get("y") is not None]
    sc = {"per_kind": {}, "models": {}, "rules": {}, "blind": blind, "units": {}, "refused": red.get("refused", {})}
    for un, rec in red["units"].items():
        sc["units"][un] = {k: v for k, v in rec["static"].items() if k in
                           ("name", "uuid_sha12", "driver", "vbios", "power_enforced_mw", "max_clock_sm")}
    for k in blind:
        v = red["kinds"][k]
        sc["per_kind"][k] = {"meas": v["y"], "se": v["se"], "n": v["n"], "by_unit": v["by_unit"],
                             "pred": pred["kinds"][k]["pred"], "band90_w": pred["kinds"][k]["band90_w"],
                             "err": {m: v["y"] - pred["kinds"][k]["pred"][m] for m in models},
                             "invalid": v["invalid"]}
    for m in models:
        e = np.array([sc["per_kind"][k]["err"][m] for k in blind])
        byf = {}
        for f in FIELDS:
            ef = [sc["per_kind"][k]["err"][m] for k in blind if k.startswith(f + ".")]
            if ef:
                byf[f] = {"rms": float(np.sqrt(np.mean(np.square(ef)))), "bias": float(np.mean(ef)), "n": len(ef)}
        sc["models"][m] = {"rms_w": float(np.sqrt(np.mean(e ** 2))), "bias_w": float(np.mean(e)),
                           "max_abs_w": float(np.max(np.abs(e))), "n": int(len(e)), "by_fmt": byf}
    e_rk = [sc["per_kind"][k]["err"][rk_key] for k in blind]
    sc["rules"]["BEAT"] = boot_beat([sc["per_kind"][k]["err"][g1_key] for k in blind], e_rk)
    if gpu == "A":
        sc["rules"]["BEAT_p"] = boot_beat([sc["per_kind"][k]["err"]["G1p"] for k in blind], e_rk)
    sc["rules"]["STABLE"] = mz["stable"]
    sc["rules"]["inside_band_RK"] = {"inside": sum(1 for k in blind if abs(sc["per_kind"][k]["err"][rk_key]) <=
                                                   sc["per_kind"][k]["band90_w"]), "of": len(blind)}
    # the registered secondary arm with a board scale (no verdict): each stage-2 board's predictions times its
    # measured y(bf16 randn) over the fit's span
    span = mz["span_w"]
    rn = red["kinds"].get("bf16.randn", {})
    bsc = {b: rn["by_unit"][b] / span for b in rn.get("by_unit", {})}
    sec = {"scale": bsc}
    for m in models:
        ek = []
        for k in blind:
            v = red["kinds"][k]
            eb = [v["by_unit"][b] - bsc[b] * pred["kinds"][k]["pred"][m] for b in v["by_unit"] if b in bsc]
            if eb:
                ek.append(float(np.mean(eb)))
        if ek:
            sec[m] = {"rms_w": float(np.sqrt(np.mean(np.square(ek)))), "bias_w": float(np.mean(ek))}
    sc["secondary_board_scale"] = sec
    # heat over each blind cell, from the frozen heat model
    hm = mz["heat"]
    if hm:
        dirs, _ = unit_dirs(run2_dir)
        hrows = []
        for d in dirs:
            un = os.path.basename(d)
            if un not in red["units"]:
                continue
            u = A9.load_unit(d)
            for p, ps in red["units"][un]["passes"].items():
                zd = {f: float(np.mean(v)) for f, v in ps["zeros_d"].items()}
                pk = {k: {"RK": pred["kinds"][k]["pred"][rk_key], "G1": pred["kinds"][k]["pred"][g1_key]}
                      for k in blind if k.split(".")[0] in zd}
                hrows += [dict(x, unit=un, pass_=p) for x in cell_heat(u, ps["rows"], hm, pk, zd)]
        byk = {}
        for x in hrows:
            byk.setdefault(x["kind"], []).append(x)
        ht = {"rows": {}}
        errs = {"measP": [], "RK": [], "G1": []}
        for k, xs in byk.items():
            mT = float(np.mean([x["meas_dT"] for x in xs]))
            rowk = {"meas_dT": mT}
            for nm, key in (("measP", "pred_measP"), ("RK", "pred_RK"), ("G1", "pred_G1")):
                pv = float(np.mean([x[key] for x in xs]))
                rowk[nm] = pv
                errs[nm].append(mT - pv)
            ht["rows"][k] = rowk
        for nm, ee in errs.items():
            if ee:
                ht[f"rms_{nm}_c"] = float(np.sqrt(np.mean(np.square(ee))))
                ht[f"bias_{nm}_c"] = float(np.mean(ee))
        sc["heat_cells"] = ht
        if errs["RK"]:
            sc["rules"]["HT1"] = {"verdict": "HOLDS" if ht["rms_RK_c"] <= ht["rms_G1_c"] else "FAILS",
                                  "rms_RK_c": ht["rms_RK_c"], "rms_G1_c": ht["rms_G1_c"],
                                  "rms_measP_c": ht.get("rms_measP_c")}
    # the seen-kinds arm (A100 only, no verdict): E149's 17 blind kinds against E149's committed stage-2 y
    if gpu == "A" and pred.get("e149_blind"):
        r2 = _jload(os.path.join(E149_DIR, "reduce-stage2.json"))["kinds"]
        arm = {}
        for m in ("RK", "G1p", "G4p", "G1"):
            ee = [r2[k]["y"] - v[m] for k, v in pred["e149_blind"].items() if r2.get(k, {}).get("y") is not None]
            arm[m] = {"rms_w": float(np.sqrt(np.mean(np.square(ee)))), "bias_w": float(np.mean(ee)), "n": len(ee)}
        arm["per_kind"] = {k: {"meas": r2[k]["y"], **{m: v[m] for m in ("RK", "G1p", "G4p", "G1")}}
                           for k, v in pred["e149_blind"].items() if r2.get(k, {}).get("y") is not None}
        sc["seen_kinds_e149_stage2"] = arm
    sc["checks"] = {"stage2_feats": chk2}
    _wjson(out_path, sc)
    return sc


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "reduce":
        ms = int(sys.argv[sys.argv.index("--max-sm") + 1]) if "--max-sm" in sys.argv else None
        r = reduce_run(sys.argv[2], ms)
        _wjson(sys.argv[3], r)
        for k, v in sorted(r["kinds"].items()):
            if "--quiet" in sys.argv:
                continue
            print(f"{k:<20} n {v['n']}/{v['n_all']}  y {v['y'] if v['y'] is None else round(v['y'], 2)}"
                  f"  se {v['se'] if v['se'] is None else round(v['se'], 2)}  P {v['p_abs'] and round(v['p_abs'], 1)}"
                  f"  T/s {v['tflops'] and round(v['tflops'], 1)}  invalid {len(v['invalid'])}")
        print("refused", r.get("refused"))
    elif cmd == "choose":
        c = do_choose(sys.argv[2], sys.argv[3])
        print(json.dumps({k: v for k, v in c.items() if k != "table"}, indent=1))
        for row in c["table"]:
            print(row["n"], row["qualifies"], {nm: (row[nm] and {k: row[nm][k] for k in ("p_w", "sm_min", "rsn_or",
                                                                                          "valid", "tflops")})
                                               for nm in ("randn", "zeros")})
    elif cmd == "freezeA":
        m, p = do_freezeA(sys.argv[2], sys.argv[3], sys.argv[4])
        print("RK s, r", m["rk"]["s"], m["rk"]["r"], "nested", {f: round(v["rms_nested"], 2)
                                                                for f, v in m["rk"]["nested"].items()},
              "in", {f: round(v["rms_in"], 2) for f, v in m["rk"]["fmts"].items()})
        print("G1p loko", {f: round(v["rms_loko"], 2) for f, v in m["g1p"]["fmts"].items()}, "STABLE",
              m["stable"]["verdict"], "scale", {f: round(v["c"], 4) for f, v in m["scale"].items()})
    elif cmd == "freezeL":
        m, p = do_freezeL(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
        print("RK s, r", m["rk"]["s"], m["rk"]["r"], "nested", m["rk"]["nested"]["bf16"]["rms_nested"],
              "in", m["rk"]["fmts"]["bf16"]["rms_in"], "STABLE", m["stable"]["verdict"])
    elif cmd == "score":
        s = do_score(*sys.argv[2:8])
        for m, v in s["models"].items():
            print(m, {k: (round(x, 2) if isinstance(x, float) else x) for k, x in v.items() if k != "by_fmt"})
        for k, v in s["rules"].items():
            print(k, v.get("verdict"))
    else:
        raise SystemExit(cmd)
