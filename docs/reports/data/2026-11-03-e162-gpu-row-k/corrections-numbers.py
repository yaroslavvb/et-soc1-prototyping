"""E162: the numbers quoted by the README's "Corrections after verification" (Tue 3 Nov 2026; post hoc, no verdict).

Every number comes from committed files only: the freeze (`model-e162-a100.json`, `predictions-e162-a100.json`), the
reductions (`reduce-a1.json`, `reduce-a2.json`), the score (`score-e162-a100.json`, `score-e162-a100.txt`), the L40S
smoke (`choice-ls.json`), stage 1's feature files under `logs/e162-20261103-a1/A/`, the push times
(`pushes-e162.json`), and E149's `reduce-stage1.json` / `reduce-stage2.json`. The registered feature definitions and
ridge code are imported from `tools/gpu/e162/analyze_e162.py` (which imports E149's analysis itself) and used unchanged.
Nothing is written; no GPU, no Modal call.

    python3 -I -B docs/reports/data/2026-11-03-e162-gpu-row-k/corrections-numbers.py \
        > docs/reports/data/2026-11-03-e162-gpu-row-k/corrections-numbers.txt

C1  the K-lag: the stage-1 scan as frozen, its spread, and the same form refitted at every pairing, scored blind
C2  the LOKO: exact leave-one-kind-out with the column scale recomputed on each fold's training rows (the registered
    text) against the code's closed form (the scale held at all the rows)
C3  the boards: E149's (the fit's E149 rows) and E162's
C4  the L40S smoke: power, clock and speed, random against zeros
C5  the best form frozen before E162, on the 22 held-out kinds
C6  heat: what HT1 compares, through E149's frozen linear heat model
C7  cosmetic: five stage-1 SEs double-rounded in the README; score-e162-a100.txt's band line
C8  times: committed against pushed
Needs numpy (under a minute).
"""
import gzip
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools", "gpu", "e162"))
import analyze_e162 as A  # noqa: E402  (the registered rk_features, ridge_fit, ridge_loo, _best_lam, RowSet, boot_beat)

E149 = os.path.join(REPO, "docs", "reports", "data", "2026-11-02-e149-gpu-model-check")
UNIT = os.path.join(HERE, "logs", "e162-20261103-a1", "A")   # the freeze reads unit A's feature files (_feats_of_run)


def jl(p):
    with open(p) as f:
        return json.load(f)


def jz(p):
    with gzip.open(p, "rt") as f:
        return json.load(f)


def rms(e):
    return float(np.sqrt(np.mean(np.square(e))))


M = jl(os.path.join(HERE, "model-e162-a100.json"))
P = jl(os.path.join(HERE, "predictions-e162-a100.json"))
S = jl(os.path.join(HERE, "score-e162-a100.json"))
R1 = jl(os.path.join(HERE, "reduce-a1.json"))["kinds"]
R2 = jl(os.path.join(HERE, "reduce-a2.json"))["kinds"]
CH = jl(os.path.join(HERE, "choice-ls.json"))
feA1 = jz(os.path.join(UNIT, "features-A1.json.gz"))
feE = jz(os.path.join(UNIT, "features-E149.json.gz"))
feH = jz(os.path.join(UNIT, "features-HA.json.gz"))
LAMS = A.LAMS

# ---- the frozen fit rows, rebuilt exactly as do_freezeA built them (kinds and y from the frozen model file) ----------
rows = {f: [(r["kind"], feA1[r["kind"]] if r["kind"] in M["new_rows"] else feE[r["kind"]], r["y"]) for r in v["rows"]]
        for f, v in M["rk"]["fmts"].items()}
sets = {f: A.RowSet(rr) for f, rr in rows.items()}
N = {f: s.n() for f, s in sets.items()}
FMTS = list(sets)
PAIRS = list(sets[FMTS[0]].X)            # (s, r) in the code's order: s outer, r inner
HELD = list(S["blind"])                  # the 22 held-out kinds as scored
yb = np.array([R2[k]["y"] for k in HELD])
assert all(abs(R2[k]["y"] - S["per_kind"][k]["meas"]) < 1e-9 for k in HELD)
assert sorted(HELD) == sorted(k for k in feH if not k.endswith(".zeros"))

print("E162 corrections after verification: numbers from committed files (post hoc, no verdict)")
print(f"fit rows {N} = {sum(N.values())}; E162's new rows {len(M['new_rows'])}, E149's rows "
      f"{sum(N.values()) - len(M['new_rows'])}; held-out kinds {len(HELD)}")

# ---- check: the registered procedure at (8, 1) reproduces the frozen coefficients and the frozen predictions ---------
s0, r0 = M["rk"]["s"], M["rk"]["r"]
dmax_c, dmax_p = 0.0, 0.0
for f in FMTS:
    lam = M["rk"]["fmts"][f]["lam"]
    b = A.ridge_fit(sets[f].X[(s0, r0)], sets[f].y, lam * N[f])
    dmax_c = max(dmax_c, float(np.max(np.abs(b - np.array(M["rk"]["fmts"][f]["coef"])))))
for k in HELD:
    dmax_p = max(dmax_p, abs(A.predict_rk(M["rk"], feH[k]) - P["kinds"][k]["pred"]["RK"]))
assert dmax_c < 1e-9 and dmax_p < 1e-9, (dmax_c, dmax_p)
print(f"check: the frozen RK is (s, r) = ({s0}, {r0}), lambda {[M['rk']['fmts'][f]['lam'] for f in FMTS]}; refitted "
      f"here, its coefficients and its 22 held-out predictions equal the frozen ones to better than 1e-9")


# ---- exact leave-one-out of ridge_fit with the column scale recomputed on each training set -------------------------
def exact_loo_res(X, y, alphas):
    """Residuals y_j - x_j beta_(-j), beta_(-j) = ridge_fit(X without row j, alpha), the column scale recomputed on the
    n - 1 training rows, for every alpha at once: shape (len(alphas), n). Sums over the other rows are formed directly
    (no subtraction), so a column that is zero outside row j is dropped exactly as ridge_fit drops it."""
    n, p = X.shape
    Mk = 1.0 - np.eye(n)
    XX = (X[:, :, None] * X[:, None, :]).reshape(n, p * p)
    Sj = (Mk @ XX).reshape(n, p, p)
    uj = Mk @ (X * y[:, None])
    d2 = (Mk @ (X * X)) / (n - 1)
    keep = np.sqrt(d2) > 1e-12
    inv = np.where(keep, 1.0 / np.sqrt(np.where(keep, d2, 1.0)), 0.0)
    G = Sj * inv[:, :, None] * inv[:, None, :]
    g = uj * inv
    eye = np.eye(p)
    out = np.empty((len(alphas), n))
    for t, a in enumerate(alphas):
        bz = np.linalg.solve(G + a * eye, g[..., None])[..., 0]
        out[t] = y - np.sum(X * (bz * inv), axis=1)
    return out


def brute_loo_res(X, y, alpha):
    e = []
    for j in range(len(y)):
        m = np.arange(len(y)) != j
        e.append(y[j] - X[j] @ A.ridge_fit(X[m], y[m], alpha))
    return np.array(e)


chk = 0.0
for f, sr in (("bf16", (8, 1)), ("int8", (1, 32)), ("fp16", (32, 4))):
    for lam in (1e-4, 0.03, 1.0):
        chk = max(chk, float(np.max(np.abs(exact_loo_res(sets[f].X[sr], sets[f].y, [lam * N[f]])[0] -
                                              brute_loo_res(sets[f].X[sr], sets[f].y, lam * N[f])))))
assert chk < 1e-8, chk
print("check: the vectorized exact LOO equals a brute-force refit loop (9 cases) to better than 1e-8 W")


def choose_lam(R):
    sse = np.sum(R ** 2, axis=1)
    t = int(np.argmin(sse))                # the first minimum, as min(LAMS, key=...) picks it
    return t, float(sse[t])


# closed form (the code, as frozen) and exact, on all the rows, every pairing
cf, ex = {}, {}
for f in FMTS:
    X, y = sets[f].X, sets[f].y
    for sr in PAIRS:
        lam, sse, _ = A._best_lam(X[sr], y, N[f])
        cf[(f, sr)] = {"lam": lam, "sse": sse, "res": A.ridge_loo(X[sr], y, lam * N[f])}
        R = exact_loo_res(X[sr], y, [l * N[f] for l in LAMS])
        t, sse = choose_lam(R)
        ex[(f, sr)] = {"lam": LAMS[t], "sse": sse, "res": R[t]}
NT = sum(N.values())


def pooled(tab, sr):
    return math.sqrt(sum(tab[(f, sr)]["sse"] for f in FMTS) / NT)


for sr in PAIRS:   # the closed-form scan is the frozen one
    assert abs(pooled(cf, sr) - M["rk"]["scan"][f"{sr[0]},{sr[1]}"]["rms_loo_pooled"]) < 1e-9


def lab(sr):
    return f"({sr[0]},{sr[1]})"


def pooled_res(tab, sr):
    return np.concatenate([tab[(f, sr)]["res"] for f in FMTS])


def boot_diff(ea, eb, seed=A.BOOT_SEED, n=A.BOOT_N):
    """rms(ea) - rms(eb), paired bootstrap over the units (E162's boot_beat: 10,000 resamples, seed 162)."""
    b = A.boot_beat(ea, eb, seed=seed, n=n)
    return b["diff"], b["ci95"]


print()
print("C1  THE K-LAG")
print("  stage-1 scan, pooled LOKO rms (W) at its best lambda per format: closed form (as frozen) | exact (C2);")
print("  then rms(pair) - rms(8,1) with a paired bootstrap over the 125 rows (approximate: LOO residuals share rows)")
for sr in sorted(PAIRS, key=lambda v: pooled(cf, v)):
    if sr[1] != 1 and sr[0] != 8:
        continue
    bf = "/".join(f"{math.sqrt(cf[(f, sr)]['sse'] / N[f]):.2f}" for f in FMTS)
    d_cf, ci_cf = boot_diff(pooled_res(cf, sr), pooled_res(cf, (8, 1)))
    d_ex, ci_ex = boot_diff(pooled_res(ex, sr), pooled_res(ex, (8, 1)))
    print(f"  {lab(sr):7s} closed {pooled(cf, sr):6.2f} (bf16/fp16/int8 {bf})  exact {pooled(ex, sr):6.2f}   "
          f"minus (8,1): closed {d_cf:+5.2f} [{ci_cf[0]:+5.2f}, {ci_cf[1]:+5.2f}]  exact {d_ex:+5.2f} "
          f"[{ci_ex[0]:+5.2f}, {ci_ex[1]:+5.2f}]")
rk1_cf = [pooled(cf, sr) for sr in PAIRS if sr[1] == 1]
rkx_cf = [pooled(cf, sr) for sr in PAIRS if sr[1] != 1]
rk1_ex = [pooled(ex, sr) for sr in PAIRS if sr[1] == 1]
rkx_ex = [pooled(ex, sr) for sr in PAIRS if sr[1] != 1]
best_x_cf = min((sr for sr in PAIRS if sr[1] != 1), key=lambda v: pooled(cf, v))
best_x_ex = min((sr for sr in PAIRS if sr[1] != 1), key=lambda v: pooled(ex, v))
print(f"  row-lag 1, worst of the six: closed {max(rk1_cf):.2f}, exact {max(rk1_ex):.2f}; row-lag != 1, best: closed "
      f"{min(rkx_cf):.2f} {lab(best_x_cf)}, exact {min(rkx_ex):.2f} {lab(best_x_ex)}; 'every row-lag != 1 worse than "
      f"every row-lag 1': closed {max(rk1_cf) < min(rkx_cf)}, exact {max(rk1_ex) < min(rkx_ex)}")

print("  stage-1 waves, bf16 y +- SE (W over zeros, reduce-a1.json):")
for nm in ("kS", "sq", "rS"):
    cells = []
    for b in (1, 2, 4, 8, 16, 32, 64):
        k = f"bf16.{nm}{b}"
        if k in R1:
            cells.append(f"b{b} {R1[k]['y']:.1f} +- {R1[k]['se']:.2f}")
    print(f"    {nm}: " + "; ".join(cells))

# post hoc: RK's registered per-pairing procedure (lambda by the code's closed form, ridge_fit on the frozen rows) at
# every pairing, scored on the 22 held-out kinds against the committed stage-2 y
blind = {}
for sr in PAIRS:
    coef = {f: A.ridge_fit(sets[f].X[sr], sets[f].y, cf[(f, sr)]["lam"] * N[f]) for f in FMTS}
    pr = np.array([float(np.dot(A.rk_features(feH[k], *sr)[1], coef[feH[k]["fmt"]])) for k in HELD])
    e = yb - pr
    coef_x = {f: A.ridge_fit(sets[f].X[sr], sets[f].y, ex[(f, sr)]["lam"] * N[f]) for f in FMTS}
    pr_x = np.array([float(np.dot(A.rk_features(feH[k], *sr)[1], coef_x[feH[k]["fmt"]])) for k in HELD])
    blind[sr] = {"e": e, "rms": rms(e), "bias": float(np.mean(e)), "rms_exactlam": rms(yb - pr_x),
                 "no_stripes": rms([x for k, x in zip(HELD, e) if "stripe" not in k])}
assert abs(blind[(8, 1)]["rms"] - S["models"]["RK"]["rms_w"]) < 1e-9
print("  post hoc, blind (22 held-out kinds, new boards): the same form refitted at each pairing, rms (bias) W;")
print("  rms(pair) - rms(8,1) with the registered paired bootstrap over the 22 kinds (10,000, seed 162)")
for sr in [p for p in PAIRS if p[1] == 1] + [p for p in PAIRS if p[0] == 8 and p[1] != 1]:
    d, ci = boot_diff(blind[sr]["e"], blind[(8, 1)]["e"])
    print(f"  {lab(sr):7s} blind {blind[sr]['rms']:6.2f} ({blind[sr]['bias']:+6.2f})  [lambda by exact LOO "
          f"{blind[sr]['rms_exactlam']:6.2f}]  without the stripes {blind[sr]['no_stripes']:6.2f}   minus (8,1) "
          f"{d:+6.2f} [{ci[0]:+6.2f}, {ci[1]:+6.2f}]")
top = sorted(PAIRS, key=lambda v: blind[v]["rms"])[:6]
print("  the six best pairings blind, of 36: " + ", ".join(f"{lab(v)} {blind[v]['rms']:.2f}" for v in top))

print()
print("C2  THE LOKO, EXACT (the column scale recomputed on each fold's training rows)")
best_cf = min(PAIRS, key=lambda v: sum(cf[(f, v)]["sse"] for f in FMTS))
best_ex = min(PAIRS, key=lambda v: sum(ex[(f, v)]["sse"] for f in FMTS))
print(f"  choice: closed form {lab(best_cf)} lambda {[cf[(f, best_cf)]['lam'] for f in FMTS]}; exact {lab(best_ex)} "
      f"lambda {[ex[(f, best_ex)]['lam'] for f in FMTS]}")
print("  the scan's best six, exact: " + ", ".join(f"{lab(v)} {pooled(ex, v):.2f}" for v in
                                                    sorted(PAIRS, key=lambda v: pooled(ex, v))[:6]))
print("  LOO at the choice, bf16/fp16/int8: closed " +
      " / ".join(f"{math.sqrt(cf[(f, best_cf)]['sse'] / N[f]):.2f}" for f in FMTS) + "; exact " +
      " / ".join(f"{math.sqrt(ex[(f, best_ex)]['sse'] / N[f]):.2f}" for f in FMTS))
# fully nested, exact: for every left-out kind, (s, r) and lambda chosen again on the remaining kinds (the other formats
# at their full-data exact SSE, as fit_rk pools them), then that kind predicted
nested, choices, allres = {}, {}, []
for f in FMTS:
    X, y = sets[f].X, sets[f].y
    res, ch = [], []
    for i in range(N[f]):
        m = np.arange(N[f]) != i
        tot, lamf = {}, {}
        for sr in PAIRS:
            t, sse = choose_lam(exact_loo_res(X[sr][m], y[m], [l * N[f] for l in LAMS]))
            lamf[sr] = LAMS[t]
            tot[sr] = sse + sum(ex[(g, sr)]["sse"] for g in FMTS if g != f)
        sr_i = min(tot, key=lambda v: tot[v])
        b = A.ridge_fit(X[sr_i][m], y[m], lamf[sr_i] * N[f])
        res.append(float(y[i] - X[sr_i][i] @ b))
        ch.append(sr_i)
    nested[f] = rms(res)
    choices[f] = {lab(c): ch.count(c) for c in sorted(set(ch))}
    allres += res
pool_ex = rms(allres)
fr = {f: M["rk"]["nested"][f]["rms_nested"] for f in FMTS}
rin = {f: M["rk"]["fmts"][f]["rms_in"] for f in FMTS}
g1pool = S["rules"]["STABLE"]["pooled"]["g1form_rms_loko"]
print("  fully nested rms, bf16/fp16/int8 (pooled): as frozen " + " / ".join(f"{fr[f]:.3f}" for f in FMTS) +
      f" ({M['rk']['rms_nested_pooled']:.3f}); exact " + " / ".join(f"{nested[f]:.3f}" for f in FMTS) +
      f" ({pool_ex:.3f})")
frozen_ch = {f: {lab(c): sum(1 for x in M["rk"]["nested"][f]["rows"] if (x["s"], x["r"]) == c)
                 for c in sorted({(x["s"], x["r"]) for x in M["rk"]["nested"][f]["rows"]})} for f in FMTS}
print(f"  the nested folds' choices: exact {choices}; as frozen (closed form) {frozen_ch}")
print("  STABLE (i) nested / in-sample (<= 3): as frozen " + " / ".join(f"{fr[f] / rin[f]:.2f}" for f in FMTS) +
      "; exact " + " / ".join(f"{nested[f] / rin[f]:.2f}" for f in FMTS) +
      f"; (ii) pooled nested <= G1's form's OLS LOKO {g1pool:.2f}: exact {pool_ex:.2f} -> "
      f"{'HOLDS' if all(nested[f] <= 3 * rin[f] for f in FMTS) and pool_ex <= g1pool else 'FAILS'}")
print("  the band (1.645 x nested rms) under exact refits, bf16/fp16/int8: " +
      " / ".join(f"{1.645 * nested[f]:.1f}" for f in FMTS) + " W (frozen " +
      " / ".join(f"{M['band90'][f]:.1f}" for f in FMTS) + "); held-out kinds inside: frozen " +
      f"{sum(abs(x) <= M['band90'][feH[k]['fmt']] for k, x in zip(HELD, blind[(8, 1)]['e']))}, exact-band "
      f"{sum(abs(x) <= 1.645 * nested[feH[k]['fmt']] for k, x in zip(HELD, blind[(8, 1)]['e']))} of {len(HELD)}")

print()
print("C3  THE BOARDS")
for nm, p in (("E149 stage 1 (fit rows)", "reduce-stage1.json"), ("E149 stage 2 (seen-kinds arm)", "reduce-stage2.json")):
    u = jl(os.path.join(E149, p))["units"]
    print(f"  {nm}: " + "; ".join(f"{k} {v['static']['name']} {v['static']['uuid_sha12']} "
                                  f"{v['static']['mem_total_mib']} MiB" for k, v in sorted(u.items())))
for nm, p in (("E162 stage 1", "reduce-a1.json"), ("E162 stage 2", "reduce-a2.json")):
    u = jl(os.path.join(HERE, p))["units"]
    print(f"  {nm}: " + "; ".join(f"{k} {v['static']['name']} {v['static']['uuid_sha12']} "
                                  f"{v['static']['mem_total_mib']} MiB" for k, v in sorted(u.items())))

print()
print("C4  THE L40S SMOKE (choice-ls.json; one 5 s window per cell, one board)")
L = CH["enforced_w"]
dz, dw, dc, dt = [], [], [], []
for t in CH["table"]:
    rr, zz = t["randn"], t["zeros"]
    w, z = rr["p_w"], zz["p_w"]
    c = rr["sm_mean"] / zz["sm_mean"] - 1.0
    q = rr["tflops"] / zz["tflops"] - 1.0
    dz.append(z / L)
    dw.append(w - z)
    dc.append(c)
    dt.append(q)
    print(f"  {t['n']}^3: random {w:6.1f} W ({w / L:4.0%} of {L:.0f}), {rr['sm_mean']:6.0f} MHz, {rr['tflops']:6.1f} "
          f"TFLOPS, 0x4 in {rr['cap_frac']:.0%}; zeros {z:6.1f} W ({z / L:4.0%}), {zz['sm_mean']:6.0f} MHz, "
          f"{zz['tflops']:6.1f} TFLOPS, 0x4 in {zz['cap_frac']:.0%}; random - zeros {w - z:+6.1f} W, clock {c:+5.1%}, "
          f"TFLOPS {q:+5.1%}")
print(f"  zeros at {min(dz):.0%}-{max(dz):.0%} of the limit; random draws {min(dw):.1f}-{max(dw):.1f} W more than zeros; "
      f"its mean SM clock {-max(dc):.1%}-{-min(dc):.1%} lower; TFLOPS {min(dt):+.1%} to {max(dt):+.1%}")

print()
print("C5  THE BEST FORM FROZEN BEFORE E162, on the 22 held-out kinds (score-e162-a100.json models)")
for m, v in sorted(S["models"].items(), key=lambda kv: kv[1]["rms_w"]):
    who = "E162's own (frozen at 54e8f87d)" if m in ("RK", "G1p", "G4p") else "E149's, frozen at e929b00f"
    print(f"  {m:9s} {v['rms_w']:8.2f} W rms, bias {v['bias_w']:+8.2f}   {who}")
e_s1 = np.array([S["per_kind"][k]["err"]["e149_S1"] for k in HELD])
d, ci = boot_diff(e_s1, blind[(8, 1)]["e"])
span = float(M["span_w"]["bf16"] if isinstance(M["span_w"], dict) else M["span_w"])
print(f"  rms(S1) - rms(RK) {d:+.2f} W, paired bootstrap 95% [{ci[0]:+.2f}, {ci[1]:+.2f}] (no verdict; BEAT is "
      f"registered against G1); ratio {blind[(8, 1)]['rms'] / S['models']['e149_S1']['rms_w']:.3f}; as shares of "
      f"E149's span {span:.2f} W: S1 {S['models']['e149_S1']['rms_w'] / span:.1%}, G1 "
      f"{S['models']['G1']['rms_w'] / span:.1%}, RK {S['models']['RK']['rms_w'] / span:.1%}")

print()
print("C6  HEAT: HT1 THROUGH E149'S FROZEN LINEAR HEAT MODEL (score-e162-a100.json heat_cells, per_kind)")
hc = S["heat_cells"]["rows"]
xs, zs, tags = [], [], []
for k in HELD:
    for m in ("RK", "G1"):
        xs.append(S["per_kind"][k]["pred"][m] - S["per_kind"][k]["meas"])        # the model's power error, W
        zs.append(hc[k][m] - hc[k]["measP"])                                      # its heat minus measured power's, C
        tags.append(m)
xs, zs = np.array(xs), np.array(zs)
g = float(np.dot(xs, zs) / np.dot(xs, xs))
res0 = zs - g * xs
r2 = 1.0 - float(np.sum(res0 ** 2) / np.sum((zs - zs.mean()) ** 2))
gi, ci_ = np.polyfit(xs, zs, 1)
print(f"  dT(model) - dT(measured P) = g x (model y - measured y): g {g:.4f} C/W through the origin (with an intercept "
      f"{gi:.4f} C/W, {ci_:+.3f} C), residual rms {rms(res0):.3f} C, R^2 {r2:.5f}, over {len(xs)} points (22 kinds x RK, G1)")
for m in ("RK", "G1"):
    eh = np.array([hc[k]["meas_dT"] - hc[k][m] for k in HELD])
    own = np.array([hc[k]["meas_dT"] - hc[k]["measP"] for k in HELD])
    path = np.array([hc[k][m] - hc[k]["measP"] for k in HELD])
    pe = np.array([S["per_kind"][k]["pred"][m] - S["per_kind"][k]["meas"] for k in HELD])
    cross = 2.0 * float(np.mean(own * -path))
    print(f"  {m}: heat rms {rms(eh):.3f} C; it is the heat model's own error (from measured power) {rms(own):.3f} C, "
          f"bias {float(np.mean(own)):+.3f}, minus the power path's {rms(path):.3f} C (= g x its power rms "
          f"{rms(pe):.2f} W = {g * rms(pe):.3f} C): {rms(own) ** 2:.3f} + {rms(path) ** 2:.3f} + cross {cross:+.3f} = "
          f"{rms(eh) ** 2:.3f} C^2")
hm = M["heat"]
print(f"  E149's frozen pooled heat model: tau1 {hm['tau1']:.1f} s, tau2 {hm['tau2']:.1f} s, steady "
      f"{hm['r1'] + hm['r2']:.3f} C/W; over a 5 s cell read after its 1.5 s settle against references on either side, "
      f"a watt of power error reads {g:.3f} C")

print()
print("C7  COSMETIC")
for k in ("bf16.kS1", "bf16.kS8", "bf16.rS1", "bf16.rowcA_colcB", "int8.rand"):
    print(f"  {k}: y {R1[k]['y']:.3f} +- {R1[k]['se']:.4f} (reduce-a1.txt prints se {R1[k]['se']:.2f}; one decimal "
          f"{R1[k]['se']:.1f})")
with open(os.path.join(HERE, "score-e162-a100.txt")) as f:
    line = [x.strip() for x in f if x.startswith("inside_band")]
print(f"  score-e162-a100.txt: {line}; score-e162-a100.json rules.inside_band_RK: {S['rules']['inside_band_RK']}")

print()
print("C8  TIMES (pushes-e162.json: git's commit time against GitHub's ref update for main)")
for c in jl(os.path.join(HERE, "pushes-e162.json"))["commits"]:
    print(f"  {c['sha'][:8]} committed {c['committed_pst']}, pushed {c['pushed_pst']} PST  {c['what']}")
