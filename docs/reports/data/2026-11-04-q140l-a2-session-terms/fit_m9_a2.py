#!/usr/bin/env python3
"""Q140(l): aifoundry2's level and session terms with the clock-voltage term, leave one session out over E80, E83, E143
and E160, exactly as registered in REGISTRATION.md / registration.json (committed 245caffe, 00:43:45 PST, before this
file was run). Desk only; reads committed files only; writes only beside itself.

    python3 fit_m9_a2.py > fit-output.txt          (numpy; about a minute on the Intel)

Writes loso.json (every arm, fold and score), rows-m9a2.json (per cell: measured, every arm's held-out prediction, the
final model's in-sample prediction) and m9_a2.json (M9's aifoundry2 part, frozen).

Imports unchanged: tools/claims-v3/e119/make_predictions_e119.py (E83's dither, through kspeed/e83/predict_e83.py) for
the reference clock function, and Q139(s)'s fit_clock_voltage.py (voltage_table, sf, Chain.fit_B) for T4's chain.
The dither is evaluated vectorized here; selfcheck_dither() proves it equals the imported one to 1e-9 MHz first.
SPDX-License-Identifier: Apache-2.0
"""
import sys

sys.dont_write_bytecode = True
import gzip  # noqa: E402
import hashlib  # noqa: E402
import json  # noqa: E402
import math  # noqa: E402
import os  # noqa: E402

import numpy as np  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
DD = os.path.join(REPO, "docs", "reports", "data")
REG = json.load(open(os.path.join(HERE, "registration.json")))
QS = os.path.join(DD, "2026-11-03-q139s-clock-voltage")
FOOT = os.path.join(DD, "2026-11-03-q139u-footing")
sys.path.insert(0, QS)
import fit_clock_voltage as FCV  # noqa: E402
sys.path.insert(0, os.path.join(REPO, "tools", "claims-v3", "e119"))
import make_predictions_e119 as M119  # noqa: E402

PTS = (600, 700, 800)
TYPES = ("fp32", "fp16", "int8")
SIG = REG["sigma_w"]
WGRID = np.arange(REG["W_grid"][0], REG["W_grid"][1] + 0.0001, REG["W_grid"][2])   # M8's fit_cap grid, 55.0 ... 75.0
NQ = M119.PE.NQ
ZS = np.array([-3.0 + 6.0 * i / (NQ - 1) for i in range(NQ)])
WS = np.array([math.exp(-z * z / 2.0) for z in ZS])
QN = ("G", "Bg", "Bp")
QLONG = {"G": "G_governed_clock_rms", "Bg": "Bg_governed_board_rms", "Bp": "Bp_pinned_board_rms"}
SESS = list(REG["sessions"])
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()  # noqa: E731
M8J = os.path.join(DD, "2026-11-03-q139m-model", "m8.json")
M8 = json.load(open(M8J))["aifoundry2"]


def rms(v):
    v = np.asarray(v, float)
    return float(np.sqrt(np.mean(v * v))) if len(v) else None


def q95(v):
    v = np.sort(np.abs(np.asarray(v, float)))
    return float(np.quantile(v, 0.95)) if len(v) else None


def phi(x):
    x = np.asarray(x, float)
    return 0.5 * (1.0 + np.vectorize(math.erf)(x / math.sqrt(2.0)))


# ------------------------------------------------------------------ the governor's clock (E83's dither), vectorized
def dither_vec(L6, L7, L8, W):
    Wz = W + SIG * ZS[None, :]
    a, b, c = L6[:, None], L7[:, None], L8[:, None]
    with np.errstate(divide="ignore", invalid="ignore"):
        f = np.where(Wz >= c, 800.0, np.where(Wz >= b, 700.0 + 100.0 * (Wz - b) / (c - b),
                                               np.where(Wz >= a, 600.0 + 100.0 * (Wz - a) / (b - a), 600.0)))
    return (f * WS[None, :]).sum(1) / WS.sum()


def p_at_vec(L6, L7, L8, f):
    return np.where(f >= 800, L8, np.where(f >= 700, L7 + (L8 - L7) * (f - 700) / 100.0,
                                           np.where(f >= 600, L6 + (L7 - L6) * (f - 600) / 100.0, L6)))


def selfcheck_dither():
    rng = np.random.default_rng(140)
    worst = 0.0
    for _ in range(400):
        c = float(rng.uniform(-1, 30))
        L = {600: 25.4556 + c, 700: 28.2433 + 1.408 * c, 800: 33.6096 + 1.905 * c}
        sh = float(rng.uniform(-3, 3))
        W = float(rng.uniform(55, 75))
        ref = M119.dither({f: L[f] + sh for f in PTS}, W, SIG)[0]
        got = dither_vec(np.array([L[600] + sh]), np.array([L[700] + sh]), np.array([L[800] + sh]), W)[0]
        worst = max(worst, abs(ref - got))
    assert worst < 1e-9, worst
    return worst


# ------------------------------------------------------------------ the data (registration: Data)
def load_cells():
    d78 = json.load(open(os.path.join(FOOT, "reduced", "e78-footing.json")))["items"]
    d141 = json.load(open(os.path.join(FOOT, "reduced", "e141-footing.json")))["items"]
    d153 = json.load(open(os.path.join(DD, "2026-11-03-e153-blind6-aifoundry3", "e153.json")))["items"]
    Dm = lambda src, key: ((src.get(key) or {}).get("D") or {}).get("mean")  # noqa: E731
    cells, checks = [], []
    for h, spec in REG["sessions"].items():
        R = json.load(open(os.path.join(DD, spec["dir"], "results.json")))
        anchors = set(spec["anchors"].values())
        if h in ("E80", "E83"):
            bu = [m for m in R["runs"] if m.get("block") == "BURST"]
            for lab, c in R["cells"].items():
                if c.get("burst_mhz") is None:
                    continue
                t, k = lab.split("/")
                runs = [{"mhz": float(m["burst_mhz"]), "w": float(m["burst_w"]), "T": float(m["die_start"])} for m in bu if m.get("kind") == lab]
                name, src, srcn = f"{t}.{k}", d78, "E78"
                checks.append((h, lab, abs(np.mean([r["mhz"] for r in runs]) - float(c["burst_mhz"])), abs(np.mean([r["w"] for r in runs]) - float(c["burst_w"]))))
                cells.append({"session": h, "label": lab, "type": t, "name": name, "anchor": lab in anchors,
                              "D": 0.0 if lab in anchors else Dm(src, name), "D_src": srcn,
                              "mhz": float(c["burst_mhz"]), "w": float(c["burst_w"]), "runs": runs})
        else:
            for lab, c in R["cells"].items():
                if "name" in c:
                    name, t = c["name"], c["type"]
                    src, srcn = (d141, "E141") if h == "E143" else (d153, "E153")
                else:
                    _, t, k = lab.split("-", 2)
                    name, src, srcn = f"{t}.{k}", d78, "E78"
                runs = [{"mhz": float(a), "w": float(b), "T": float(d)} for a, b, d in zip(c["burst_mhz_runs"], c["burst_w_runs"], c["die_start_runs"])]
                checks.append((h, lab, abs(np.mean([r["mhz"] for r in runs]) - float(c["burst_mhz"])), abs(np.mean([r["w"] for r in runs]) - float(c["burst_w"]))))
                cells.append({"session": h, "label": lab, "type": t, "name": name, "anchor": lab in anchors,
                              "D": 0.0 if lab in anchors else Dm(src, name), "D_src": srcn, "registered_group": c.get("group"),
                              "mhz": float(c["burst_mhz"]), "w": float(c["burst_w"]), "runs": runs})
    return cells, checks


# ------------------------------------------------------------------ the chains (base = M8's relation; T4 = n = 2 from the reads)
def base_chain():
    rel, par = M8["relation"], M8["params"]
    return {"name": "M8 relation (E136's B and s; M8's c_zeros and g)", "B": {int(k): v for k, v in rel["B_w"].items()},
            "s": {int(k): v for k, v in rel["s_f"].items()}, "cz": dict(par["c_zeros_w"]), "g": par["g"]["fp32"]}


_READS, _CH, _VCHECK = None, None, None


def pvt_busy_means(reads, exclude_dirs):
    """FCV.voltage_table's pvt_busy_mean_mv (steady bins, a PVT reading, minion rail >= 8 W; weighted by the bin's count), per
    card@MHz, computed directly: voltage_table also fits the droop with an n x n weight matrix (np.diag), about 20 GB for
    aifoundry2's 600 MHz point, which this needs nowhere. checked against Q139(s)'s committed clock-voltage.json first."""
    acc = {}
    for r in reads["files"]:
        if r["top"] in exclude_dirs:
            continue
        for b in r["bins"]:
            f, steady, reg, die, spv, wb, n = b[:7]
            if not steady or die is None or wb is None or wb < 8.0:
                continue
            a = acc.setdefault(f"{r['card']}@{f}", [0.0, 0.0])
            a[0] += die * n
            a[1] += n
    return {k: v[0] / v[1] for k, v in acc.items() if v[1] > 0}


def reads_chain(exclude_dir):
    """T4: s(f) at n = 2 from Q139(s)'s reads with exclude_dir left out; B by E64's fit_linear; c_zeros from E64's zeros runs;
    g = 1/xfer from the same reads (Q139(s)'s arm A2's chain)"""
    global _READS, _CH, _VCHECK
    if _READS is None:
        _READS = json.load(gzip.open(os.path.join(QS, "voltage-reads.json.gz"), "rt"))
        _CH = FCV.Chain(REPO)
        cv = json.load(open(os.path.join(QS, "clock-voltage.json")))
        worst = 0.0
        for key, ex in (("pvt_busy_mean_all", ()), ("pvt_busy_mean_no_E143", ("2026-11-02-e143-blind5-aifoundry2",))):
            pm = pvt_busy_means(_READS, ex)
            worst = max([worst] + [abs(pm[f"aifoundry2@{f}"] / 1000.0 - cv["V_aifoundry2_v"][key][str(f)]) for f in PTS]
                        + [abs((pm["aifoundry3@600"] / pm["aifoundry2@600"]) ** 2 - cv["xfer"][key])])
        assert worst < 1e-12, worst
        _VCHECK = worst
    pm = pvt_busy_means(_READS, (exclude_dir,) if exclude_dir else ())
    V = {f: pm[f"aifoundry2@{f}"] / 1000.0 for f in PTS}
    S = FCV.sf(V, 2.0)
    B, c64, r64, n64 = _CH.fit_B(S)
    cz = {t: float(np.mean([v for k, v in c64.items() if f"-{t}-zeros" in k])) for t in TYPES}
    xfer = (pm["aifoundry3@600"] / pm["aifoundry2@600"]) ** 2
    return {"name": f"n = 2 from the reads without {exclude_dir}" if exclude_dir else "n = 2 from every committed read (Q139(s)'s survey)", "V": V, "B": B, "s": S, "cz": cz, "g": 1.0 / xfer,
            "xfer": xfer, "E64_rows": n64, "E64_fit_rms_w": r64}


# ------------------------------------------------------------------ the model (registration: the terms and the stages)
class Runs:
    """the runs of a list of cells, flattened, with the per-run inputs"""

    def __init__(self, cells):
        self.cells = cells
        self.idx = np.array([i for i, c in enumerate(cells) for _ in c["runs"]], int)
        self.T = np.array([r["T"] for c in cells for r in c["runs"]], float)
        self.mhz = np.array([r["mhz"] for c in cells for r in c["runs"]], float)
        self.w = np.array([r["w"] for c in cells for r in c["runs"]], float)
        self.type = [c["type"] for c in cells for _ in c["runs"]]
        self.sess = [c["session"] for c in cells for _ in c["runs"]]
        self.D = np.array([c["D"] for c in cells for _ in c["runs"]], float)
        self.n = np.bincount(self.idx, minlength=len(cells)).astype(float)

    def cellmean(self, v):
        return np.bincount(self.idx, weights=v, minlength=len(self.cells)) / self.n


def c_of(chain, t, D):
    return chain["cz"][t] + chain["g"] * D


def L800(chain, t, D):
    return chain["B"][800] + c_of(chain, t, D) * chain["s"][800]


def session_delta(anchor_runs, chain, kT, Tref, use_T3):
    """T2's input: per format, the mean over the anchor's runs at >= 795 MHz of burst_w - L(800; c_zeros), die-referred if T3"""
    out, filled = {}, []
    for t, rr in anchor_runs.items():
        rr = [r for r in rr if r["mhz"] >= REG["anchor_run_min_mhz"]]
        if not rr:
            continue
        Lz = chain["B"][800] + chain["cz"][t] * chain["s"][800]
        out[t] = float(np.mean([r["w"] - Lz - (kT * (r["T"] - Tref) if use_T3 else 0.0) for r in rr]))
    have = dict(out)
    for t in TYPES:
        if t not in out:
            out[t] = float(np.mean(list(have.values())))
            filled.append(t)
    return out, filled, have


def shifts(par, R, deltas):
    s = np.zeros(len(R.T))
    if par["cfg"]["T2"]:
        s += par["beta"] * np.array([deltas[h][t] for h, t in zip(R.sess, R.type)])
    if par["cfg"]["T3"]:
        s += par["kT"] * (R.T - par["T_ref"])
    return s


def levels(chain, R, sh):
    c = np.array([chain["cz"][t] for t in R.type]) + chain["g"] * R.D
    return tuple(chain["B"][f] + c * chain["s"][f] + sh for f in PTS)


def run_pred(par, R, deltas, W=None, with_T1=True):
    W = par["W"] if W is None else W
    L6, L7, L8 = levels(par["chain"], R, shifts(par, R, deltas))
    f = dither_vec(L6, L7, L8, W)
    P = p_at_vec(L6, L7, L8, f)
    pi = phi((L8 - W) / SIG)
    if with_T1 and par["cfg"]["T1"]:
        P = P + par["dcap"] * pi
    return f, P, pi, L8


def fit(cfg, train, chain, anchors):
    """S1a, S1b, S2, S3 on the training cells (anchors excluded); anchors = {session: {type: runs}}"""
    par = {"cfg": dict(cfg), "chain": chain, "kT": 0.0, "beta": 0.0, "dcap": 0.0}
    R = Runs(train)
    par["T_ref"] = float(R.T.mean())
    # S1: the pinned runs at >= 795 MHz
    pm = np.array([train[i]["group"] == "pinned" for i in R.idx]) & (R.mhz >= REG["pinned_fit_run_min_mhz"])
    r = R.w - np.array([L800(chain, t, D) for t, D in zip(R.type, R.D)])
    if cfg["T3"]:
        ss = sorted(set(np.array(R.sess)[pm]))
        X = np.column_stack([R.T[pm]] + [np.array([s == q for s in np.array(R.sess)[pm]], float) for q in ss])
        b = np.linalg.lstsq(X, r[pm], rcond=None)[0]
        par["kT"] = float(b[0])
        par["kT_n_runs"] = int(pm.sum())
    deltas = {}
    for h in set(c["session"] for c in train):
        deltas[h], par.setdefault("filled", {})[h], _ = session_delta(anchors[h], chain, par["kT"], par["T_ref"], cfg["T3"])
    par["train_deltas"] = deltas
    if cfg["T2"]:
        x = np.array([deltas[h][t] for h, t in zip(R.sess, R.type)])[pm]
        y = r[pm] - (par["kT"] * (R.T[pm] - par["T_ref"]) if cfg["T3"] else 0.0)
        par["beta"] = float((x * y).sum() / (x * x).sum())
    # S2: the cap on the clocks, M8's grid
    L6, L7, L8 = levels(chain, R, shifts(par, R, deltas))
    meas = np.array([c["mhz"] for c in train])
    sse = [float(((R.cellmean(dither_vec(L6, L7, L8, W)) - meas) ** 2).sum()) for W in WGRID]
    par["W"] = float(WGRID[int(np.argmin(sse))])
    # S3: the cap level on the boards
    if cfg["T1"]:
        f, P, pi, _ = run_pred(par, R, deltas, with_T1=False)
        e = np.array([c["w"] for c in train]) - R.cellmean(P)
        p = R.cellmean(pi)
        par["dcap"] = float((p * e).sum() / (p * p).sum())
    return par


def predict(par, cells, anchors):
    """predict cells of one or more sessions with their own anchors' delta (computed with the fit's k_T and T_ref)"""
    R = Runs(cells)
    deltas = {h: session_delta(anchors[h], par["chain"], par["kT"], par["T_ref"], par["cfg"]["T3"])[0] for h in set(c["session"] for c in cells)}
    f, P, pi, L8 = run_pred(par, R, deltas)
    return R.cellmean(f), R.cellmean(P), deltas


def fixed_W_par(W, chain=None):
    return {"cfg": {"T1": False, "T2": False, "T3": False, "T4": False}, "chain": chain or base_chain(), "kT": 0.0, "beta": 0.0,
            "dcap": 0.0, "T_ref": 0.0, "W": W}


# ------------------------------------------------------------------ scoring
def score(cells, pm, pw):
    em = np.array([c["mhz"] for c in cells]) - pm
    ew = np.array([c["w"] for c in cells]) - pw
    g = np.array([c["group"] == "governed" for c in cells])
    out = {"n": len(cells), "n_governed": int(g.sum()), "n_pinned": int((~g).sum())}
    for lab, m, e in (("G", g, em), ("Bg", g, ew), ("Bp", ~g, ew), ("Gp", ~g, em), ("clk_all", np.ones(len(g), bool), em), ("brd_all", np.ones(len(g), bool), ew)):
        out[lab] = {"rms": rms(e[m]), "mean": float(e[m].mean()) if m.any() else None}
    return out


def evaluate(pred_by_cell, cells):
    """pred_by_cell: {id: (mhz, w)}; per session and pooled scores"""
    res = {}
    for h in SESS + ["pooled"]:
        cs = [c for c in cells if h == "pooled" or c["session"] == h]
        res[h] = score(cs, np.array([pred_by_cell[c["id"]][0] for c in cs]), np.array([pred_by_cell[c["id"]][1] for c in cs]))
    return res


def loso(cfg, cells, anchors, keep_params=False):
    preds, params = {}, {}
    for h in SESS:
        chain = reads_chain(REG["sessions"][h]["dir"]) if cfg["T4"] else base_chain()
        par = fit(cfg, [c for c in cells if c["session"] != h], chain, anchors)
        test = [c for c in cells if c["session"] == h]
        pm, pw, dl = predict(par, test, anchors)
        for c, a, b in zip(test, pm, pw):
            preds[c["id"]] = (float(a), float(b))
        params[h] = {k: v for k, v in par.items() if k not in ("chain", "train_deltas", "filled")}
        params[h]["heldout_delta"] = dl[h]
        params[h]["chain"] = {k: v for k, v in chain.items() if k in ("name", "B", "s", "cz", "g", "V", "xfer")}
        params[h]["train_deltas"] = par["train_deltas"]
        if keep_params:
            params[h]["_par"] = par
    return {"cfg": dict(cfg), "scores": evaluate(preds, cells), "params": params, "preds": preds}


def compare(new, cur):
    tol = {q: REG["rule"]["tolerance"][QLONG[q]] for q in QN}
    out = {"per_quantity": {}}
    for q in QN:
        lower = {h: new["scores"][h][q]["rms"] < cur["scores"][h][q]["rms"] for h in SESS}
        pooled_lower = new["scores"]["pooled"][q]["rms"] < cur["scores"]["pooled"][q]["rms"]
        out["per_quantity"][q] = {"sessions_lower": [h for h in SESS if lower[h]], "n_lower": int(sum(lower.values())),
                                  "pooled_cur": cur["scores"]["pooled"][q]["rms"], "pooled_new": new["scores"]["pooled"][q]["rms"],
                                  "pooled_lower": bool(pooled_lower), "carries": bool(sum(lower.values()) >= REG["rule"]["min_sessions"] and pooled_lower),
                                  "pooled_rise": new["scores"]["pooled"][q]["rms"] - cur["scores"]["pooled"][q]["rms"], "tolerance": tol[q]}
    car = [q for q in QN if out["per_quantity"][q]["carries"]]
    harm = [q for q in QN if q not in car and out["per_quantity"][q]["pooled_rise"] > tol[q]]
    out["carries_on"], out["harms"] = car, harm
    out["kept"] = bool(car) and not harm
    return out


def boot_diff(cells, pa, pb, seed):
    """95% interval of rms(a) - rms(b) per quantity over cells resampled inside the session"""
    rng = np.random.default_rng(seed)
    n = len(cells)
    mm = np.array([c["mhz"] for c in cells])
    ww = np.array([c["w"] for c in cells])
    g = np.array([c["group"] == "governed" for c in cells])
    ea = {"G": mm - pa[:, 0], "Bg": ww - pa[:, 1], "Bp": ww - pa[:, 1]}
    eb = {"G": mm - pb[:, 0], "Bg": ww - pb[:, 1], "Bp": ww - pb[:, 1]}
    sel = {"G": g, "Bg": g, "Bp": ~g}
    d = {q: [] for q in QN}
    for _ in range(REG["bootstrap"]["draws"]):
        k = rng.integers(0, n, n)
        for q in QN:
            m = sel[q][k]
            if m.sum() == 0:
                continue
            d[q].append(rms(ea[q][k][m]) - rms(eb[q][k][m]))
    out = {}
    for q in QN:
        v = np.array(d[q])
        out[q] = {"point": rms(ea[q][sel[q]]) - rms(eb[q][sel[q]]), "ci95": [float(np.quantile(v, 0.025)), float(np.quantile(v, 0.975))],
                  "resolved_below_zero": bool(np.quantile(v, 0.975) < 0)}
    return out


def fmt_scores(lab, S):
    def g(h, q, k):
        v = S[h][q][k]
        return float("nan") if v is None else v
    s = [f"  {lab:34s}"]
    for h in SESS + ["pooled"]:
        s.append(f" | {h:6s} G {g(h,'G','rms'):5.2f} ({g(h,'G','mean'):+5.2f}) Bg {g(h,'Bg','rms'):4.2f} ({g(h,'Bg','mean'):+5.2f}) Bp {g(h,'Bp','rms'):4.2f} ({g(h,'Bp','mean'):+5.2f})")
    return "".join(s)


def main():
    L = []

    def P(*a):
        L.append(" ".join(str(x) for x in a))
        print(L[-1], file=sys.stderr, flush=True)
    worst = selfcheck_dither()
    P(f"Q140(l) fit_m9_a2.py: the registration (registration.json sha256 {sha(os.path.join(HERE, 'registration.json'))[:16]}), m8.json {sha(M8J)[:16]}")
    P(f"dither self-check: vectorized vs make_predictions_e119.dither, worst |diff| {worst:.2e} MHz over 400 random inputs")
    allc, checks = load_cells()
    for i, c in enumerate(allc):
        c["id"] = i
    dmax = max(x[2] for x in checks)
    wmax = max(x[3] for x in checks)
    P(f"cells: {len(allc)}; cell value = mean of its runs: max |d| {dmax:.4f} MHz, {wmax:.4f} W")
    noD = [(c["session"], c["label"]) for c in allc if not c["anchor"] and c["D"] is None]
    P(f"cells without a measured D (dropped): {noD}")
    anchors = {h: {} for h in SESS}
    for c in allc:
        if c["anchor"]:
            anchors[c["session"]][c["type"]] = c["runs"]
    cells = [c for c in allc if not c["anchor"] and c["D"] is not None]
    # the groups: M8 as frozen, primary D
    R8 = fixed_W_par(REG["reference_lines"]["R8"]["W"])
    pm, pw, _ = predict(R8, cells, anchors)
    for c, f in zip(cells, pm):
        c["group"] = "governed" if f < 795.0 else "pinned"
    cnt = {h: sum(1 for c in cells if c["session"] == h) for h in SESS}
    P(f"scored cells per session: {cnt} (registered {REG['expected_scored_cells']}); governed per session: "
      f"{ {h: sum(1 for c in cells if c['session'] == h and c['group'] == 'governed') for h in SESS} }")
    out = {"_note": "Q140(l) fit_m9_a2.py output; every arm as registered (REGISTRATION.md, 245caffe)", "registration_sha256": sha(os.path.join(HERE, "registration.json")),
           "m8_sha256": sha(M8J), "dither_selfcheck_worst_mhz": worst, "cells_dropped_no_D": noD, "scored_cells": cnt,
           "anchors": {h: {t: rr for t, rr in a.items()} for h, a in anchors.items()}}

    # ---- the reference lines (fixed W, no fit)
    refs = {}
    for lab in ("R7", "R8"):
        par = fixed_W_par(REG["reference_lines"][lab]["W"])
        pm, pw, _ = predict(par, cells, anchors)
        refs[lab] = {"preds": {c["id"]: (float(a), float(b)) for c, a, b in zip(cells, pm, pw)}}
        refs[lab]["scores"] = evaluate(refs[lab]["preds"], cells)
    out["reference_lines"] = {k: {"W": REG["reference_lines"][k]["W"], "scores": v["scores"]} for k, v in refs.items()}
    P("")
    P("REFERENCE LINES (measured - predicted; rms (mean); primary D = measured aifoundry3 D on the footing)")
    for k in ("R7", "R8"):
        P(fmt_scores(f"{k} as frozen (W {REG['reference_lines'][k]['W']:.2f})", refs[k]["scores"]))

    # ---- the reproduction checks (they test the code)
    P("")
    P("REPRODUCTION CHECKS (registered sets, registered groups, the models' own blind D)")
    rep = {}
    P143 = json.load(open(os.path.join(REPO, "tools/claims-v3/e143/predictions-e143.json")))["tiles"]
    P160 = json.load(open(os.path.join(REPO, "tools/claims-v3/kinds/blind6/predictions-blind6-aifoundry2.json")))["tiles"]
    for h, lab, src, getD, want in (("E143", "R7", P143, lambda n: P143[n]["models"]["M7"]["D600_a3_footing_w"], REG["reproduction_checks"]["E143_R7_M7_blind_D_registered_groups"]),
                                    ("E160", "R8", P160, lambda n: P160[n]["M8"]["D600_a3_footing_w"], REG["reproduction_checks"]["E160_R8_M8_blind_D_registered_groups"])):
        cs = [dict(c, D=getD(c["name"]), group=c["registered_group"]) for c in allc if c["session"] == h and c.get("registered_group")]
        pm, pw, _ = predict(fixed_W_par(REG["reference_lines"][lab]["W"]), cs, anchors)
        sc = score(cs, pm, pw)
        got = {"G_rms": sc["G"]["rms"], "Bg_rms": sc["Bg"]["rms"], "pinned_clock_rms": sc["Gp"]["rms"], "Bp_rms": sc["Bp"]["rms"]}
        ok = all(abs(got[k] - want[k]) <= (0.06 if "clock" in k or k == "G_rms" else 0.011) for k in want)
        rep[f"{h}_{lab}"] = {"n": len(cs), "got": got, "registered": want, "ok": ok}
        P(f"  {h} {lab}: n {len(cs)} got " + ", ".join(f"{k} {v:.3f}" for k, v in got.items()) + f" | registered {want} | {'OK' if ok else 'FAIL'}")
    out["reproduction_checks"] = rep
    if not all(v["ok"] for v in rep.values()):
        print("\n".join(L))
        raise SystemExit("reproduction check failed: the code is wrong; nothing scored")

    # ---- the base and the forward selection (the registered rule)
    cfg0 = {"T1": False, "T2": False, "T3": False, "T4": False}
    arms = {}
    arms["A0"] = loso(cfg0, cells, anchors)
    P("")
    P("LEAVE ONE SESSION OUT (each session predicted by the fold that held it out)")
    P(fmt_scores("A0 base (M8's form, W refit)", arms["A0"]["scores"]))
    P("  A0's W per fold: " + ", ".join(f"{h} {arms['A0']['params'][h]['W']:.1f}" for h in SESS))
    steps = []
    cur_cfg, cur_lab = dict(cfg0), "A0"
    for term in ("T1", "T2", "T3", "T4"):
        cand = dict(cur_cfg, **{term: True})
        lab = "+".join(k for k in ("T1", "T2", "T3", "T4") if cand[k]) or "A0"
        if lab not in arms:
            arms[lab] = loso(cand, cells, anchors)
        cmp_ = compare(arms[lab], arms[cur_lab])
        steps.append({"term": term, "against": cur_lab, "config": lab, **cmp_})
        P(fmt_scores(f"{lab}", arms[lab]["scores"]))
        P(f"    step {term} vs {cur_lab}: " + "; ".join(f"{q} lower in {v['n_lower']}/4 {v['sessions_lower']} pooled {v['pooled_cur']:.3f}->{v['pooled_new']:.3f} carries {v['carries']}" for q, v in cmp_["per_quantity"].items())
          + f" -> {'KEPT' if cmp_['kept'] else 'not kept'} (carries on {cmp_['carries_on']}, harms {cmp_['harms']})")
        if cmp_["kept"]:
            cur_cfg, cur_lab = cand, lab
    out["forward_steps"] = steps
    out["final_config"] = {"label": cur_lab, "cfg": cur_cfg}
    out["T4_voltage_check_vs_q139s_worst"] = _VCHECK
    P(f"  T4's PVT busy means against Q139(s)'s committed clock-voltage.json (all reads; without E143): worst |diff| {_VCHECK}")
    P(f"  FINAL CONFIGURATION: {cur_lab}")

    # ---- reported: each term alone against A0
    P("")
    P("REPORTED: EACH TERM ALONE AGAINST A0 (marginal; not a selection input)")
    marg = {}
    for term in ("T1", "T2", "T3", "T4"):
        lab = term
        cfg = dict(cfg0, **{term: True})
        key = term
        if key not in arms:
            arms[key] = loso(cfg, cells, anchors)
        marg[term] = compare(arms[key], arms["A0"])
        P(fmt_scores(f"{term} alone", arms[key]["scores"]))
        P(f"    {term} vs A0: " + "; ".join(f"{q} {v['n_lower']}/4 pooled {v['pooled_cur']:.3f}->{v['pooled_new']:.3f}" for q, v in marg[term]["per_quantity"].items()) + f" -> would be {'kept' if marg[term]['kept'] else 'not kept'}")
    out["marginal"] = marg
    out["arms"] = {k: {"cfg": v["cfg"], "scores": v["scores"], "params": v["params"]} for k, v in arms.items()}
    P("")
    P("PARAMETERS PER FOLD (fitted on the other three sessions)")
    def dh(p):
        return ", ".join("%s %+.2f" % (t, p["heldout_delta"][t]) for t in TYPES)
    for k, v in arms.items():
        P(f"  {k:12s} " + " | ".join(f"{h}: W {p['W']:.1f} kT {p['kT']:.3f} beta {p['beta']:.3f} dcap {p['dcap']:.3f} Tref {p['T_ref']:.2f} dheld {dh(p)}" for h, p in v["params"].items()))

    # ---- the final configuration: against R7 and R8 per session, bootstrap, the rank-2 targets
    fin = arms[cur_lab]
    P("")
    P(f"FINAL ({cur_lab}) AGAINST M7 AND M8 AS FROZEN, per held-out session (paired difference final - reference; 95% over cells inside the session)")
    bt = {}
    for h in SESS:
        cs = [c for c in cells if c["session"] == h]
        pa = np.array([fin["preds"][c["id"]] for c in cs])
        bt[h] = {}
        for ref in ("R7", "R8"):
            pb = np.array([refs[ref]["preds"][c["id"]] for c in cs])
            bt[h][ref] = boot_diff(cs, pa, pb, REG["bootstrap"]["seed"])
            P(f"  {h} vs {ref}: " + "; ".join(f"{q} {v['point']:+.3f} [{v['ci95'][0]:+.3f}, {v['ci95'][1]:+.3f}]{' resolved' if v['resolved_below_zero'] else ''}" for q, v in bt[h][ref].items()))
    out["final_vs_references_bootstrap"] = bt
    tg = REG["rank2_targets_reported"]
    r2 = {}
    for h in SESS + ["pooled"]:
        s = fin["scores"][h]
        r2[h] = {"G_rms_le_4": s["G"]["rms"] <= tg["G_rms_max_mhz"], "G_mean_within_2": abs(s["G"]["mean"]) <= tg["G_abs_mean_max_mhz"],
                 "Bg_mean_within_0.5": abs(s["Bg"]["mean"]) <= tg["Bg_abs_mean_max_w"], "Bp_mean_within_0.5": abs(s["Bp"]["mean"]) <= tg["Bp_abs_mean_max_w"],
                 "Bp_rms_le_1": s["Bp"]["rms"] <= tg["Bp_rms_max_w"]}
    out["rank2_targets_on_final_loso"] = r2
    P("  the critic's rank-2 targets on the final configuration's held-out numbers: " + "; ".join(f"{h} " + ",".join(k for k, v in d.items() if v) for h, d in r2.items()))

    # ---- end to end with the blind D (E143: M7's; E160: M8's), non-anchor registered tiles
    P("")
    P("REPORTED: END TO END WITH THE MODELS' BLIND D (E143 with M7's frozen D, E160 with M8's), non-anchor registered tiles")
    e2e = {}
    for h, getD in (("E143", lambda n: P143[n]["models"]["M7"]["D600_a3_footing_w"]), ("E160", lambda n: P160[n]["M8"]["D600_a3_footing_w"])):
        base = [c for c in cells if c["session"] == h and c.get("registered_group")]
        cs = [dict(c, D=getD(c["name"])) for c in base]
        e2e[h] = {}
        for lab, par in (("R7", fixed_W_par(REG["reference_lines"]["R7"]["W"])), ("R8", fixed_W_par(REG["reference_lines"]["R8"]["W"])),
                         ("A0", None), (cur_lab, None)):
            if par is None:
                arm = arms["A0"] if lab == "A0" else fin
                p = arm["params"][h]
                chain = reads_chain(REG["sessions"][h]["dir"]) if arm["cfg"]["T4"] else base_chain()
                par = dict(p, chain=chain, cfg=arm["cfg"])
            pm, pw, _ = predict(par, cs, anchors)
            e2e[h][lab] = score(cs, pm, pw)
            s = e2e[h][lab]
            P(f"  {h} {lab:12s} n {s['n']}: G {s['G']['rms']:.2f} ({s['G']['mean']:+.2f}) Bg {s['Bg']['rms']:.2f} ({s['Bg']['mean']:+.2f}) Bp {s['Bp']['rms']:.2f} ({s['Bp']['mean']:+.2f})")
    out["end_to_end_blind_D"] = e2e

    # ---- the freeze: refit on all four sessions
    chain_all = reads_chain(None) if cur_cfg["T4"] else base_chain()
    parF = fit(cur_cfg, cells, chain_all, anchors)
    pmF, pwF, dF = predict(parF, cells, anchors)
    _, _, have = zip(*[session_delta(anchors[h], chain_all, parF["kT"], parF["T_ref"], cur_cfg["T3"]) for h in SESS])
    fallback = {t: float(np.mean([hv[t] for hv in have if t in hv])) for t in TYPES}
    fallback_n = {t: int(sum(1 for hv in have if t in hv)) for t in TYPES}
    # bands: per predicted group of the final configuration's held-out predictions
    em = np.array([c["mhz"] - fin["preds"][c["id"]][0] for c in cells])
    ew = np.array([c["w"] - fin["preds"][c["id"]][1] for c in cells])
    gov = np.array([fin["preds"][c["id"]][0] < 795.0 for c in cells])
    bands = {"governed": {"n": int(gov.sum()), "q95_abs_mhz": q95(em[gov]), "q95_abs_board_w": q95(ew[gov])},
             "pinned": {"n": int((~gov).sum()), "q95_abs_mhz": q95(em[~gov]), "q95_abs_board_w": q95(ew[~gov])},
             "rule": "per the model's own predicted group (governed: predicted clock below 795 MHz), the 95th percentile of |held-out error| of the final configuration over the four sessions' 134 held-out cells; burst D takes the board band"}
    kept_terms = [k for k in ("T1", "T2", "T3", "T4") if cur_cfg[k]]
    m9 = {"_model": "M9's aifoundry2 part (Q140(l)), frozen from fit_m9_a2.py on E80, E83, E143 and E160 as registered in REGISTRATION.md (245caffe)",
          "kept_terms": kept_terms, "config": cur_cfg, "label": cur_lab,
          "if_none_kept": "M8's aifoundry2 terms as frozen" if not kept_terms else None,
          "relation": {"B_w": {str(k): v for k, v in chain_all["B"].items()}, "s_f": {str(k): v for k, v in chain_all["s"].items()},
                       "c_zeros_w": chain_all["cz"], "g": chain_all["g"], "sigma_w": SIG, "chain": chain_all["name"],
                       "law": "levels L(f) = B(f) + c s(f) + shift, c = c_zeros[t] + g D (D at 600 MHz on aifoundry3's footing); clock = E83's dither of L about W with sigma; board = L at the clock (+ T1's dcap x Phi((L800 - W)/sigma))"},
          "params": {"W": parF["W"], "dcap_w": parF["dcap"], "beta": parF["beta"], "kT_w_per_c": parF["kT"], "T_ref_c": parF["T_ref"]},
          "fallback_delta_w": fallback, "fallback_delta_n_sessions": fallback_n,
          "session_deltas_w": {h: dF[h] for h in SESS},
          "bands": bands,
          "burst_heat": M8["burst_heat"],
          "peak": dict(M8["peak"], note="M8's peak rule, unchanged and with no level shift (registered: a level term must not loosen the 82 W admission stop)"),
          "M8_params_for_the_peak": {"B_w": M8["relation"]["B_w"], "s_f": M8["relation"]["s_f"], "c_zeros_w": M8["params"]["c_zeros_w"], "g": M8["params"]["g"]["fp32"]},
          "loso": {h: fin["scores"][h] for h in SESS + ["pooled"]},
          "references_loso_cells": {k: {h: refs[k]["scores"][h] for h in SESS + ["pooled"]} for k in ("R7", "R8")},
          "registration": "docs/reports/data/2026-11-04-q140l-a2-session-terms/REGISTRATION.md (245caffe)",
          "inputs": "the session's own zeros-anchor reads per format (burst_w, burst_mhz, die_start of each anchor run; only runs at >= 795 MHz count) when T2 is kept, else none; each run's die start when T3 is kept, else none"}
    json.dump(m9, open(os.path.join(HERE, "m9_a2.json"), "w"), indent=1, sort_keys=True)
    P("")
    P(f"FROZEN m9_a2.json: kept {kept_terms or 'none (M8 as frozen)'}; W {parF['W']:.2f} dcap {parF['dcap']:.3f} beta {parF['beta']:.3f} kT {parF['kT']:.3f} Tref {parF['T_ref']:.2f}; fallback delta {fallback} (n {fallback_n})")
    P(f"  bands: governed n {bands['governed']['n']} q95 {bands['governed']['q95_abs_mhz']:.2f} MHz / {bands['governed']['q95_abs_board_w']:.2f} W; pinned n {bands['pinned']['n']} q95 {bands['pinned']['q95_abs_mhz']:.2f} MHz / {bands['pinned']['q95_abs_board_w']:.2f} W")
    sF = evaluate({c["id"]: (float(a), float(b)) for c, a, b in zip(cells, pmF, pwF)}, cells)
    P(fmt_scores("final, in sample (all four fitted)", sF))
    out["final_in_sample"] = sF

    # ---- the checks: E159's zeros GEMMs and E161's first hold
    P("")
    P("REPORTED CHECKS: E159's zeros GEMMs and E161's first hold (no anchors ran there: the fallback delta)")
    shift = {t: (parF["beta"] * fallback[t] if cur_cfg["T2"] else 0.0) for t in TYPES}
    R159 = json.load(open(os.path.join(DD, "2026-11-03-e159-gemm-sustained", "results.json")))
    rows = [r for r in R159["rows"] if "zeros" in str(r.get("cell", ""))]
    chk = {"shift_at_T_ref_w": shift, "E159": [], "E161": None}
    for r in rows:
        mw, pwg = float(r["meas"]["w"]), float(r["pred"]["G3"]["w"])
        kinds_lvl = L800(base_chain(), "fp32", 0.0)
        chk["E159"].append({"hold": r["cell"], "measured_mhz": r["meas"]["mhz"], "measured_board_w": mw, "die_start_c": r.get("die_start"), "G3_w": pwg,
                            "G3_miss_meas_minus_pred_w": mw - pwg, "M9_shift_w": shift["fp32"], "G3_plus_M9_shift_miss_w": mw - (pwg + shift["fp32"]),
                            "M8_kinds_zeros_level_800_w": kinds_lvl, "measured_minus_M8_kinds_zeros_level_w": mw - kinds_lvl})
        P(f"  E159 {r['cell']}: measured {mw:.2f} W at {r['meas']['mhz']:.1f} MHz, G3 {pwg:.2f} (miss {mw - pwg:+.2f}); with M9's fp32 level shift {shift['fp32']:+.2f}: miss {mw - pwg - shift['fp32']:+.2f}; "
          f"M8's kinds fp32 zeros level at 800 MHz {kinds_lvl:.2f} W (measured - it {mw - kinds_lvl:+.2f})")
    s161 = open(os.path.join(DD, "2026-11-03-e161-heat-e2e-aifoundry2", "corrections.txt")).read()
    c161 = json.loads(s161[s161.find("{"):])
    lvl = c161["C1"]["G1Q"]["decomposition_posthoc"]["M8_level_offset_in_kernel_launches_ge790MHz_W"]
    chk["E161"] = {"tile": "int8.b_line_zero_ff", "M8_level_high_by_w": lvl, "M9_shift_w": shift["int8"], "M9_level_high_by_w": lvl + shift["int8"]}
    P(f"  E161 G1Q (int8.b_line_zero_ff, 800 MHz in the kernel launches): M8's level {lvl:+.3f} W high; with M9's int8 level shift {shift['int8']:+.3f}: {lvl + shift['int8']:+.3f} W")
    out["checks"] = chk

    # ---- rows
    rows_out = []
    for c, a, b in zip(cells, pmF, pwF):
        rows_out.append({"session": c["session"], "label": c["label"], "name": c["name"], "type": c["type"], "group": c["group"], "D": c["D"], "D_src": c["D_src"],
                         "runs": c["runs"], "mhz": c["mhz"], "w": c["w"],
                         "heldout": {k: arms[k]["preds"][c["id"]] for k in arms}, "R7": refs["R7"]["preds"][c["id"]], "R8": refs["R8"]["preds"][c["id"]],
                         "final_in_sample": (float(a), float(b))})
    json.dump({"_note": "Q140(l) per-cell rows: measured, held-out predictions of every arm, references, the final model in sample", "rows": rows_out,
               "anchors": out["anchors"]}, open(os.path.join(HERE, "rows-m9a2.json"), "w"), indent=0, sort_keys=True)
    json.dump(out, open(os.path.join(HERE, "loso.json"), "w"), indent=1, sort_keys=True, default=float)
    print("\n".join(L))


if __name__ == "__main__":
    main()
