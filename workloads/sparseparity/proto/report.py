"""report.py: tables, plots and ET-SoC-1 projections from the sweep's JSONL files.

  python3 report.py --data data/2026-09-28-aifoundry1 [--png-dir .]

Prints markdown tables on stdout (RESULTS.md quotes them) and writes fig_*.png.
The ET-SoC-1 throughput assumptions are the ET dict below; every projection is derived from it.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import statistics as st
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sp  # noqa: E402

NS = [32, 64, 128, 256, 512]
KS = [2, 3, 4, 5]
ETAS = [0.0, 0.1, 0.2, 0.3, 0.4]

# ---------------------------------------------------------------- ET-SoC-1 assumptions (stated in RESULTS.md)
ET = dict(
    minions=1024,          # 32 compute shires x 32 minions (the kernel-visible part of the 1,088)
    hz=600e6,              # sustained clock on a warm die (800 MHz only below ~65 C)
    vec_bits=256,          # 8 lanes x 32 bits of packed-integer VPU per minion
    instr_per_vec=8,       # load + XOR + ~6 carry-save / popcount ops per 256 subset-samples (no popcount insn)
    ipc=(0.25, 0.5, 1.0),  # vector instructions per minion-cycle: low / central / high
    int8_mac_s=35.9e12,    # TensorIMA8A32 measured 71.8 TOP/s at 600 MHz on 1,024 minions (mmbench, 18 Sep)
    tensor_eff=(0.5, 1.0), # fraction of that rate a sparse-parity GEMM keeps (tiles generated on the fly)
    board_w=60.0,          # board power under full int8 load, 57-62 W (docs/et-soc1-notes.md)
)


def et_vector_rate(ipc: float) -> float:
    """subset-samples per second, bit-packed XOR + carry-save popcount on the VPU"""
    return ET["minions"] * ET["hz"] * ET["vec_bits"] / ET["instr_per_vec"] * ipc


def et_times(n: int, k: int, m: int) -> dict:
    """Projected ET-SoC-1 times for the exhaustive search at sample count m.
    Tensor route (central): canonical-split GEMM on TensorIMA8A32, 16x16 output tiles, K = 64 samples per op
    (m rounded up to 64), at tensor_eff of the measured int8 rate. Vector route (fallback): bit-packed XOR +
    carry-save popcount, instr_per_vec per 256 subset-samples at the given IPC range."""
    work = math.comb(n, k) * m
    lo, mid, hi = (math.comb(n, k) * max(m, 64) / et_vector_rate(i) for i in ET["ipc"])
    m64 = -(-max(m, 1) // 64) * 64
    macs = sp.gemm_macs(n, k, m64, tile=16, round_cols=True)
    t_mid, t_best = (macs / (ET["int8_mac_s"] * e) for e in ET["tensor_eff"])
    return dict(work=work, vec_mid=mid, vec_best=hi, vec_worst=lo, tensor_mid=t_mid, tensor_best=t_best,
                best_mid=t_mid, macs=macs, redundancy=macs / work)


# ---------------------------------------------------------------- loading
def load(d: str, task: str) -> list[dict]:
    p = os.path.join(d, f"{task}.jsonl")
    if not os.path.exists(p):
        return []
    return [json.loads(line) for line in open(p) if line.strip()]


def m99_emp(ms: list[dict]) -> dict:
    by = {}
    for d in ms:
        for m, t, w in zip(d["probes"], d["true_count"], d["min_wrong"]):
            by.setdefault((d["n"], d["k"], d["eta"]), {}).setdefault(m, {})[d["seed"]] = t < w
    res, curves = {}, {}
    for key, per_m in by.items():
        best = None
        for m in sorted(per_m, reverse=True):
            if len(per_m[m]) < 20:
                continue
            if all(per_m[m].values()):
                best = m
            else:
                break
        res[key] = best
        curves[key] = sorted((m, sum(v.values()) / len(v)) for m, v in per_m.items() if len(v) >= 20)
    return res, curves


def fmt_t(s: float | None) -> str:
    if s is None or (isinstance(s, float) and math.isnan(s)):
        return "-"
    if s < 1e-3:
        return f"{s * 1e6:.0f} us"
    if s < 1:
        return f"{s * 1e3:.1f} ms"
    if s < 120:
        return f"{s:.1f} s"
    if s < 7200:
        return f"{s / 60:.1f} min"
    if s < 2 * 86400:
        return f"{s / 3600:.1f} h"
    return f"{s / 86400:.0f} d"


class Fit:
    """Single-thread exhaustive-scan cost per subset (ns) against W (words per packed column, padded), from
    the exh runs of the same n (the innermost loop does not depend on k); the nearest measured n otherwise."""

    def __init__(self, exh: list[dict]):
        by = {}
        for d in exh:
            if d["threads"] == 1 and d["wall_s"] > 0.01:
                by.setdefault(d["n"], {}).setdefault(d["W"], []).append(1e9 * d["wall_s"] / d["subsets"])
        self.tab = {n: (np.array(sorted(v)), np.array([st.median(v[w]) for w in sorted(v)])) for n, v in by.items()}
        allw = {}
        for d in exh:
            if d["threads"] == 1 and d["wall_s"] > 0.01:
                allw.setdefault(d["W"], []).append(1e9 * d["wall_s"] / d["subsets"])
        self.W = np.array(sorted(allw))
        self.ns = np.array([st.median(allw[w]) for w in self.W])

    def ns_per_subset(self, W: int, n: int | None = None) -> float:
        if n is not None and self.tab:
            nn = min(self.tab, key=lambda x: (abs(math.log2(x / n)), -x))
            Ws, ns = self.tab[nn]
            if len(Ws) >= 2 and Ws[0] <= W <= Ws[-1] * 1.5:
                if W > Ws[-1]:
                    sl = (ns[-1] - ns[-2]) / (Ws[-1] - Ws[-2])
                    return float(ns[-1] + sl * (W - Ws[-1]))
                return float(np.interp(W, Ws, ns))
        if W > self.W[-1] and len(self.W) >= 2:
            sl = (self.ns[-1] - self.ns[-2]) / (self.W[-1] - self.W[-2])
            return float(self.ns[-1] + sl * (W - self.W[-1]))
        return float(np.interp(W, self.W, self.ns))

    def t1(self, n: int, k: int, m: int) -> float:
        return math.comb(n, k) * self.ns_per_subset(padded_words(m), n) * 1e-9


def padded_words(m: int) -> int:
    """words per packed column in the AVX-512 build of spbits (zero-padded to a multiple of 8 above 4)"""
    W = (m + 63) // 64
    return W if W <= 4 else (W + 7) // 8 * 8


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--png-dir", default=HERE)
    a = ap.parse_args()
    D = a.data
    ms, exh, exh3 = load(D, "msearch"), load(D, "exh"), load(D, "exh_v3")
    gemm, ge, gers, mlp = load(D, "gemm"), load(D, "ge"), load(D, "gers"), load(D, "mlp")
    slices = {(d["n"], d["k"], d["eta"]): d for d in load(D, "exh_slice")}
    memp, curves = m99_emp(ms)
    fit = Fit(exh)
    mmod = {(n, k, e): sp.m99_model(n, k, e) for n in NS for k in KS for e in ETAS}

    def m_of(n, k, e):
        return memp.get((n, k, e)) or mmod[(n, k, e)]

    out = []
    P = out.append

    # ---------------- m99
    P("### Samples needed: smallest m with 20/20 seeds solved (exhaustive / GEMM estimator)\n")
    P("Measured by one scan per seed over nested prefixes (`spbits msearch`); `model` is the smallest m with "
      "P(success) >= 0.99 under the independent-binomial model; a `~` entry had no measured search (model only).\n")
    P("| n | k | " + " | ".join(f"eta={e}" for e in ETAS) + " |")
    P("|---|---|" + "---|" * len(ETAS))
    for n in NS:
        for k in KS:
            cells = []
            for e in ETAS:
                me = memp.get((n, k, e))
                cells.append(f"{me} ({mmod[(n, k, e)]})" if me else f"~{mmod[(n, k, e)]}")
            P(f"| {n} | {k} | " + " | ".join(cells) + " |")
    ratios = [memp[key] / mmod[key] for key in memp if memp[key]]
    if ratios:
        P(f"\nmeasured / model over {len(ratios)} points: median {st.median(ratios):.2f}, "
          f"range {min(ratios):.2f}-{max(ratios):.2f}\n")

    # ---------------- exhaustive scan timings
    P("### Exhaustive scan (C, bit-packed XOR + popcount), wall time at that m\n")
    P("`1T` = one thread (median of up to 3 seeds), `4T` = four threads; `1T proj` = the one-core time from, in "
      "order of preference, a timed slice (`slice=S`: every S-th outer task), the 4T run x the measured 4-thread "
      "speedup, or C(n,k) x the per-n fitted ns/subset against padded W; for measured points it shows the fit, as a "
      "check. i7-11700K (aifoundry1), AVX-512 VPOPCNTQ build, columns zero-padded to 8 words above 4.\n")
    P("| n | k | eta | m | C(n,k) | 1T | 4T | 1T proj | subset-samples/s (1T) |")
    P("|---|---|---|---|---|---|---|---|---|")
    ex1, ex4 = {}, {}
    for d in exh:
        key = (d["n"], d["k"], d["eta"])
        (ex1 if d["threads"] == 1 else ex4).setdefault(key, []).append(d)
    okcount = sum(d["ok"] for d in exh)
    sp4 = [st.median(x["wall_s"] for x in ex1[k2]) / st.median(x["wall_s"] for x in ex4[k2])
           for k2 in ex4 if k2 in ex1 and st.median(x["wall_s"] for x in ex1[k2]) > 0.2]
    sp4m = st.median(sp4) if sp4 else 3.8

    def t1_info(n, k, e, m):
        """one-core time and its source: measured / slice (every S-th task, timed) / 4T x speedup / fit"""
        key = (n, k, e)
        if key in ex1:
            return st.median(x["wall_s"] for x in ex1[key]), "measured"
        if key in slices and slices[key]["m"] == m:
            d = slices[key]
            return math.comb(n, k) * d["wall_s"] / d["subsets"], f"slice 1/{d['slice']}"
        if key in ex4:
            return st.median(x["wall_s"] for x in ex4[key]) * sp4m, f"4T x {sp4m:.2f}"
        return fit.t1(n, k, m), "fit"
    for n in NS:
        for k in KS:
            for e in ETAS:
                key = (n, k, e)
                m = m_of(n, k, e)
                t1 = st.median(x["wall_s"] for x in ex1[key]) if key in ex1 else None
                t4 = st.median(x["wall_s"] for x in ex4[key]) if key in ex4 else None
                tp, src = t1_info(n, k, e, m) if key not in ex1 else (fit.t1(n, k, m), "fit")
                thr = math.comb(n, k) * m / t1 if t1 else None
                if n >= 128 or k >= 4:
                    P(f"| {n} | {k} | {e} | {m} | {math.comb(n, k):.3g} | {fmt_t(t1)} | {fmt_t(t4)} | "
                      f"{fmt_t(tp)} ({src}) | {thr:.3g} |" if thr else
                      f"| {n} | {k} | {e} | {m} | {math.comb(n, k):.3g} | {fmt_t(t1)} | {fmt_t(t4)} | "
                      f"{fmt_t(tp)} ({src}) | - |")
    P(f"\n(n <= 64 with k <= 3 omitted: all under 1 ms.) Solved: {okcount}/{len(exh)} timing runs.\n")
    if sp4:
        P(f"4-thread speedup where 1T > 0.2 s: median {st.median(sp4):.2f}x ({min(sp4):.2f}-{max(sp4):.2f}x, "
          f"{len(sp4)} points)\n")
    P("Single-thread cost per subset (ns) by n and padded W, the basis of every projection:\n")
    for n in sorted(fit.tab):
        Ws, ns = fit.tab[n]
        P(f"- n={n}: " + ", ".join(f"W={w}: {v:.2f}" for w, v in zip(Ws.tolist(), ns.tolist())))
    P("")
    if exh3:
        P("Scalar-POPCNT build (`spbits_v3`, x86-64-v3, no vector popcount) vs AVX-512 build, one thread:\n")
        P("| n | k | eta | m | v3 | AVX-512 | ratio |")
        P("|---|---|---|---|---|---|---|")
        for d in exh3:
            key = (d["n"], d["k"], d["eta"])
            if key in ex1:
                t1 = st.median(x["wall_s"] for x in ex1[key])
                P(f"| {d['n']} | {d['k']} | {d['eta']} | {d['m']} | {fmt_t(d['wall_s'])} | {fmt_t(t1)} | "
                  f"{d['wall_s'] / t1:.1f}x |")
        P("")

    # ---------------- GEMM
    P("### GEMM form (numpy float32 on OpenBLAS, one thread)\n")
    rates = [g["macs"] / g["wall_s"] for g in gemm if g["macs"] > 1e9]
    grate = st.median(rates) if rates else 5e10
    P(f"Effective rate on runs over 1e9 MACs: median {grate:.3g} MAC/s (includes forming the +-1 "
      "products and masking entries off the canonical staircase). Skipped points are projected at that rate.\n")
    P("| n | k | eta | m | MACs | redundancy vs C(n,k)m | numpy time | projected | C scan 1T |")
    P("|---|---|---|---|---|---|---|---|---|")
    gby = {(g["n"], g["k"], g["eta"]): g for g in gemm}
    for n in NS:
        for k in KS:
            for e in [0.0, 0.2, 0.4]:
                m = m_of(n, k, e)
                macs = sp.gemm_macs(n, k, m)
                g = gby.get((n, k, e))
                red = macs / (math.comb(n, k) * m)
                t1 = t1_info(n, k, e, m)[0]
                P(f"| {n} | {k} | {e} | {m} | {macs:.3g} | {red:.2f} | {fmt_t(g['wall_s']) if g else '-'} | "
                  f"{fmt_t(macs / grate)} | {fmt_t(t1)} |")
    gok = sum(g["ok"] for g in gemm)
    P(f"\nGEMM runs solved: {gok}/{len(gemm)}.\n")

    # ---------------- GE
    P("### GF(2) elimination, noiseless labels (C, rows inserted one at a time)\n")
    P("| n | m at full rank: mean | max of 20 seeds (= 20/20 m) | median time | solved |")
    P("|---|---|---|---|---|")
    for n in NS:
        rs = [d for d in ge if d["n"] == n and d["k"] == 3]
        allr = [d for d in ge if d["n"] == n]
        if not rs:
            continue
        mf = [d["m_full_rank"] for d in rs]
        P(f"| {n} | {st.mean(mf):.1f} | {max(mf)} | {fmt_t(st.median(d['wall_s'] for d in rs))} | "
          f"{sum(d['ok'] for d in allr)}/{len(allr)} |")
    P("")
    if gers:
        P("### GF(2) elimination on random subsets, noisy labels (C)\n")
        P("Each trial: pick `ncols` random features and ncols+8 random samples, eliminate, accept a weight-k "
          "solution whose disagreement on all m samples is below m(0.5+eta)/2. `ncols` minimises the "
          "expected work (it must contain the secret; all chosen samples must be clean).\n")
        P("| n | k | eta | ncols | m | expected trials | median trials | median time | solved | C scan 1T |")
        P("|---|---|---|---|---|---|---|---|---|---|")
        gb = {}
        for d in gers:
            gb.setdefault((d["n"], d["k"], d["eta"]), []).append(d)
        for key in sorted(gb):
            rs = gb[key]
            n, k, e = key
            t1 = t1_info(n, k, e, m_of(n, k, e))[0]
            P(f"| {n} | {k} | {e} | {rs[0]['ncols']} | {rs[0]['m']} | {rs[0]['exp_trials']:.3g} | "
              f"{st.median(r['trials'] for r in rs):.3g} | {fmt_t(st.median(r['wall_s'] for r in rs))} | "
              f"{sum(r['ok'] for r in rs)}/{len(rs)} | {fmt_t(t1)} |")
        P("")
    if mlp:
        P("### MLP + online SGD (numpy, one thread), reference only\n")
        P("| n | k | eta | solved | median steps | median samples | median time | MACs |")
        P("|---|---|---|---|---|---|---|---|")
        mb = {}
        for d in mlp:
            mb.setdefault((d["n"], d["k"], d["eta"]), []).append(d)
        for key in sorted(mb):
            rs = mb[key]
            P(f"| {key[0]} | {key[1]} | {key[2]} | {sum(r['ok'] for r in rs)}/{len(rs)} | "
              f"{st.median(r['steps'] for r in rs):.3g} | {st.median(r['samples'] for r in rs):.3g} | "
              f"{fmt_t(st.median(r['wall_s'] for r in rs))} | {st.median(r['macs'] for r in rs):.3g} |")
        P("")

    # ---------------- ET projections and showcase
    P("### ET-SoC-1 projection per grid point (exhaustive search, tensor route at 50% of the measured int8 rate)\n")
    P("| n | k | " + " | ".join(f"eta={e}" for e in ETAS) + " |")
    P("|---|---|" + "---|" * len(ETAS))
    for n in [128, 256, 512]:
        for k in KS:
            cells = []
            for e in ETAS:
                m = m_of(n, k, e)
                t1 = t1_info(n, k, e, m)[0]
                cells.append(f"{fmt_t(t1)} -> {fmt_t(et_times(n, k, m)['best_mid'])}")
            P(f"| {n} | {k} | " + " | ".join(cells) + " |")
    P("\n(cell = one CPU core -> ET-SoC-1 projected)\n")

    show = [(256, 5, 0.3), (512, 4, 0.4), (512, 5, 0.2), (512, 5, 0.4), (1024, 5, 0.4)]
    P("### Showcase sizes\n")
    P("| n | k | eta | m | subset-samples | 1 CPU core | 4 threads | ET vector route (IPC 1 - 0.25) | "
      "ET tensor int8 (eff 1 - 0.5) | ET central | vs 1 core | vs 4 threads | ET energy |")
    P("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    show_rows = []
    for n, k, e in show:
        m = memp.get((n, k, e)) or sp.m99_model(n, k, e)
        key = (n, k, e)
        t1, src = t1_info(n, k, e, m)
        t4m = st.median(x["wall_s"] for x in ex4[key]) if key in ex4 else None
        t4 = t4m if t4m else t1 / sp4m
        E = et_times(n, k, m)
        show_rows.append(dict(n=n, k=k, eta=e, m=m, t1=t1, t1_src=src, t4=t4, t4_meas=bool(t4m), **E))
        P(f"| {n} | {k} | {e} | {m} | {E['work']:.2g} | {fmt_t(t1)} ({src}) | "
          f"{fmt_t(t4)}{'' if t4m else ' (1T / ' + f'{sp4m:.2f})'} | {fmt_t(E['vec_best'])} - {fmt_t(E['vec_worst'])} | "
          f"{fmt_t(E['tensor_best'])} - {fmt_t(E['tensor_mid'])} | "
          f"{fmt_t(E['best_mid'])} | {t1 / E['best_mid']:.0f}x | {t4 / E['best_mid']:.1f}x | "
          f"{E['best_mid'] * ET['board_w'] / 1e3:.2g} kJ |")
    P("")
    print("\n".join(out))
    plots(a.png_dir, memp, curves, mmod, fit, ex1, ex4, exh3, gemm, grate, ge, gers, show_rows, t1_info)


# ---------------------------------------------------------------- plots
INK, INK2, GRID, SURF = "#0b0b0b", "#52514e", "#e4e3de", "#fcfcfb"
CAT = ["#2a78d6", "#eb6834", "#1baf7a", "#4a3aa7"]  # validated all-pairs (light)
SEQ5 = ["#86b6ef", "#5598e7", "#2a78d6", "#1c5cab", "#104281"]
SEQ4 = ["#86b6ef", "#3987e5", "#1c5cab", "#0d366b"]


def style(ax, title=None):
    ax.set_facecolor(SURF)
    for s in ["top", "right"]:
        ax.spines[s].set_visible(False)
    for s in ["left", "bottom"]:
        ax.spines[s].set_color(INK2)
        ax.spines[s].set_linewidth(0.8)
    ax.tick_params(colors=INK2, labelsize=8)
    ax.grid(True, which="major", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    if title:
        ax.set_title(title, color=INK, fontsize=10, loc="left")


def reflines(ax, horizontal=True):
    for v, lab in [(1, "1 s"), (60, "1 min"), (3600, "1 h")]:
        (ax.axhline if horizontal else ax.axvline)(v, color=INK2, lw=0.8, ls=(0, (2, 3)), zorder=1)
        if horizontal:
            ax.text(ax.get_xlim()[0], v * 1.15, " " + lab, color=INK2, fontsize=7, va="bottom")


def plots(pdir, memp, curves, mmod, fit, ex1, ex4, exh3, gemm, grate, ge, gers, show_rows, t1f):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.rcParams.update({"font.size": 9, "figure.facecolor": SURF, "savefig.facecolor": SURF,
                         "text.color": INK, "axes.labelcolor": INK2})

    # 1. samples needed
    fig, axs = plt.subplots(1, 4, figsize=(12, 3.4), sharey=True)
    for ax, k in zip(axs, KS):
        style(ax, f"k = {k}")
        for c, n in zip(SEQ5, NS):
            ys = [mmod[(n, k, e)] for e in ETAS]
            ax.plot(ETAS, ys, color=c, lw=2, label=f"n={n}", zorder=2)
            xe = [e for e in ETAS if memp.get((n, k, e))]
            ax.plot(xe, [memp[(n, k, e)] for e in xe], "o", ms=5, color=c, mec=SURF, mew=1.2, zorder=3)
        ax.set_yscale("log")
        ax.set_xlabel("label noise eta")
    axs[0].set_ylabel("samples m for 99% success")
    axs[-1].legend(frameon=False, fontsize=8, loc="upper left")
    fig.suptitle("Samples the exhaustive search needs: lines = binomial model, dots = measured (20/20 seeds)",
                 x=0.01, ha="left", fontsize=10, color=INK)
    fig.tight_layout()
    fig.savefig(os.path.join(pdir, "fig_samples.png"), dpi=130)
    plt.close(fig)

    # 2. model check: success curves
    fig, ax = plt.subplots(figsize=(6.5, 3.6))
    style(ax, "P(success) vs m: binomial model (line) and 20 seeds (dots)")
    picks = [(128, 3, 0.1), (128, 5, 0.3), (256, 4, 0.4), (512, 3, 0.2)]
    for c, key in zip(CAT, picks):
        if key not in curves:
            continue
        pts = curves[key]
        mm = np.unique(np.linspace(min(p[0] for p in pts) * 0.8, max(p[0] for p in pts) * 1.1, 60).astype(int))
        N = math.comb(key[0], key[1])
        ax.plot(mm, [sp.p_success(N, int(x), key[2]) for x in mm], color=c, lw=2,
                label=f"n={key[0]} k={key[1]} eta={key[2]}")
        ax.plot([p[0] for p in pts], [p[1] for p in pts], "o", color=c, ms=5, mec=SURF, mew=1.2)
    ax.set_xscale("log")
    ax.set_xlabel("samples m")
    ax.set_ylabel("fraction solved")
    ax.legend(frameon=False, fontsize=8)
    fig.tight_layout()
    fig.savefig(os.path.join(pdir, "fig_model_check.png"), dpi=130)
    plt.close(fig)

    # 3. single-core cost map of the exhaustive scan
    fig, axs = plt.subplots(1, 5, figsize=(14, 3.9), sharey=True)
    for ax, e in zip(axs, ETAS):
        style(ax, f"eta = {e}")
        for c, k in zip(SEQ4, KS):
            ts, meas = [], []
            for n in NS:
                key = (n, k, e)
                m = memp.get(key) or mmod[key]
                if key in ex1:
                    ts.append(st.median(x["wall_s"] for x in ex1[key]))
                    meas.append(True)
                else:
                    ts.append(t1f(n, k, e, m)[0])
                    meas.append(False)
            ax.plot(NS, ts, color=c, lw=2, label=f"k={k}", zorder=2)
            ax.plot([n for n, f in zip(NS, meas) if f], [t for t, f in zip(ts, meas) if f], "o", color=c,
                    ms=5, mec=SURF, mew=1.2, zorder=3)
            ax.plot([n for n, f in zip(NS, meas) if not f], [t for t, f in zip(ts, meas) if not f], "o",
                    mfc=SURF, mec=c, ms=5, mew=1.5, zorder=3)
        ax.set_xscale("log", base=2)
        ax.set_yscale("log")
        ax.set_xticks(NS)
        ax.set_xticklabels([str(n) for n in NS])
        ax.set_xlabel("n")
        reflines(ax)
    axs[0].set_ylabel("one core, seconds")
    h, l = axs[0].get_legend_handles_labels()
    fig.legend(h, l, frameon=False, fontsize=8, loc="lower center", ncol=4, bbox_to_anchor=(0.5, 0.0))
    fig.suptitle("Exhaustive k-subset scan at the 99% sample count, one i7-11700K core (filled = measured, "
                 "hollow = projected from a timed slice, the 4-thread run or the fitted ns/subset)", x=0.01, ha="left", fontsize=10, color=INK)
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    fig.savefig(os.path.join(pdir, "fig_cpu_cost.png"), dpi=130)
    plt.close(fig)

    # 4. throughput per core vs m, with ET lines
    fig, ax = plt.subplots(figsize=(7, 4.6))
    style(ax, "Throughput of the exhaustive search: subset-samples per second")
    for c, (lab, rows, per) in zip(
            CAT, [("C AVX-512, 1 thread", ex1, 1), ("C AVX-512, 4 threads", ex4, 1), ("C scalar POPCNT, 1 thread", None, 1)]):
        if rows is None:
            pts = [(d["m"], math.comb(d["n"], d["k"]) * d["m"] / d["wall_s"]) for d in exh3 if d["wall_s"] > 0.01]
        else:
            pts = [(r["m"], r["subsets"] * r["m"] / r["wall_s"]) for v in rows.values() for r in v
                   if r["wall_s"] > 0.01]
        if pts:
            ax.plot([p[0] for p in pts], [p[1] for p in pts], "o", color=c, ms=5, mec=SURF, mew=1, label=lab)
    gp = [(g["m"], math.comb(g["n"], g["k"]) * g["m"] / g["wall_s"]) for g in gemm if g["macs"] > 1e8]
    if gp:
        ax.plot([p[0] for p in gp], [p[1] for p in gp], "s", color=CAT[3], ms=5, mec=SURF, mew=1,
                label="numpy GEMM, 1 thread (per unique subset)")
    t_mid, t_hi = (ET["int8_mac_s"] * e for e in ET["tensor_eff"])
    ax.axhspan(t_mid, t_hi, color=INK, alpha=0.08, lw=0)
    ax.axhline(t_mid, color=INK, lw=1.5)
    ax.set_xlim(20, 3000)
    ax.text(22, t_mid * 1.12, "ET-SoC-1 projected, tensor int8 route (band: 50-100% of the measured int8 rate)",
            fontsize=7, color=INK)
    ax.axhline(et_vector_rate(0.5), color=INK2, lw=1, ls=(0, (1, 2)))
    ax.text(22, et_vector_rate(0.5) * 0.72, "ET-SoC-1 vector route (fallback), IPC 0.5", fontsize=7, color=INK2)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("samples m")
    ax.set_ylabel("subset-samples / s")
    ax.legend(frameon=False, fontsize=7, loc="upper center", bbox_to_anchor=(0.5, -0.16), ncol=2)
    fig.tight_layout()
    fig.savefig(os.path.join(pdir, "fig_throughput.png"), dpi=130)
    plt.close(fig)

    # 5. showcase
    fig, ax = plt.subplots(figsize=(8, 4.2))
    style(ax, "Showcase sizes: time to solve at the 99% sample count")
    labels = [f"n={r['n']} k={r['k']} eta={r['eta']}" for r in show_rows]
    y = np.arange(len(show_rows))[::-1]
    series = [("1 CPU core", "t1", CAT[0], "o"), ("4 CPU threads", "t4", CAT[3], "s"),
              ("ET-SoC-1 projected (tensor route; bar = 100-50% eff.)", "best_mid", INK, "D")]
    for lab, key, c, mk in series:
        xs = [r[key] for r in show_rows]
        ax.plot(xs, y, mk, color=c, ms=7, mec=SURF, mew=1.2, label=lab, zorder=3)
    for yi, r in zip(y, show_rows):
        ax.plot([r["tensor_best"], r["tensor_mid"]], [yi, yi], color=INK, lw=1.5, zorder=2)
        ax.plot([r["best_mid"], r["t1"]], [yi, yi], color=GRID, lw=3, zorder=1)
    ax.plot([r["vec_mid"] for r in show_rows], y, "D", mfc=SURF, mec=INK2, ms=6, mew=1.2,
            label="ET vector route (fallback)", zorder=3)
    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=8)
    ax.set_xscale("log")
    ax.set_ylim(y[-1] - 0.6, y[0] + 0.8)
    for v, lab in [(1, "1 s"), (60, "1 min"), (3600, "1 h")]:
        ax.axvline(v, color=INK2, lw=0.8, ls=(0, (2, 3)), zorder=0)
        ax.text(v * 1.1, y[0] + 0.45, lab, fontsize=7, color=INK2)
    ax.set_xlabel("seconds (log scale)")
    ax.legend(frameon=False, fontsize=8, loc="upper center", bbox_to_anchor=(0.45, -0.2), ncol=2)
    fig.tight_layout()
    fig.savefig(os.path.join(pdir, "fig_showcase.png"), dpi=130)
    plt.close(fig)


if __name__ == "__main__":
    main()
