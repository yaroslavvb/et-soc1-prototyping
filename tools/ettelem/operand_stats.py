#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.9,<3.13"
# dependencies = ["numpy==1.26.4"]
# ///
"""An operand-statistics front end: the load model's flip counts without the RTL bench. Q126, 26 Oct 2026.

Recap item 2b. The flip model's only activity input is a replay of dumped fp32 tiles through one Verilator
bench, so "predict" has meant "run it, dump it, replay it". This predicts the four counted classes from
statistics of the operands alone -- the zero-gated lane count, the bits that flip between successive operand
words, the mantissa population, per side -- and then feeds load_model.py as the bench's counts would.

    fit    : the 14 fp32 operand patterns of 21 Sep (toggles.json)
    score  : the 17 structured matrices of 21 Sep (structured_toggles.json and the measured board powers in
             report.json), WITHOUT refitting
    output : docs/reports/data/2026-10-26-load-model/operand_stats.json

    ./operand_stats.py                       # the shebang runs it under `uv run --script`, which
                                             # fetches its own numpy -- nothing to install
    /usr/bin/python3 operand_stats.py        # any interpreter that already has numpy. On the Intel
                                             # /usr/local/bin/python3.12 does NOT; /usr/bin/python3
                                             # (3.9.6, numpy 1.26.4) does, and the lab boxes do.

The PEP 723 block above pins BOTH python (< 3.13) and numpy (== 1.26.4), and both pins earn their
keep (Q128(e), 26 Oct 2026, the run that proved the shebang):
  * python < 3.13 -- 3.13 dedents docstrings at compile time, and this script publishes its own
    `features` docstring into the JSON, so a newer interpreter silently rewrites a committed field;
  * numpy == 1.26.4 -- the version the committed operand_stats.json was made with (numpy 2.5.4
    moved the last digits of every lstsq coefficient).
Even pinned, the re-run is not byte-identical: the macOS system numpy links Accelerate and uv's
wheel links OpenBLAS, so the solve differs in the last digits -- measured max relative difference
3.7e-12 over every number in the file, with every non-numeric field identical. Re-running this
script therefore reproduces the committed JSON to ~1e-12, not to the byte; do not commit that churn.

The operands. The structured matrices' tiles are on disk as the raw pairs the card was given
(2026-09-21-horace-aifoundry2/structured_tiles/<kind>.<seed>.bin), so their statistics are exact. The 14
patterns were drawn by the host's own generator on the card and were not kept, so they are re-drawn here with
rtl-sim/fma_toggle/tiles.py, which implements the same distributions. Every feature below is distributional --
a zero fraction, a mean Hamming distance, a mean population count over 256 words -- so a re-draw reproduces it
to sampling noise, and `zeros`, `ones`, `pi` and `checker` are deterministic anyway. That is the one
approximation in the fit, and it is named here rather than buried.
"""
import json
import os
import struct
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
D21 = os.path.join(REPO, "docs", "reports", "data", "2026-09-21-horace-aifoundry2")
OUT = os.path.join(REPO, "docs", "reports", "data", "2026-10-26-load-model", "operand_stats.json")
sys.path.insert(0, os.path.join(REPO, "rtl-sim", "fma_toggle"))
sys.path.insert(0, os.path.join(REPO, "tools", "ettelem"))

CLASSES = ("ffclk", "mult", "rest", "bus")
MULT_BLOCKS = ("csa", "compressor", "wallace", "booth")
MAC = 4096
SEEDS = (1, 2, 3, 4, 5)


# ---------------------------------------------------------------- the features
def popcount(x):
    x = x.astype(np.uint32)
    c = np.zeros(x.shape, dtype=np.int64)
    for b in range(32):
        c += ((x >> np.uint32(b)) & np.uint32(1)).astype(np.int64)
    return c


def stats(words):
    """Statistics of one 512-word operand tile pair (A then B), each 16x16 fp32 as raw uint32.

    Nothing here needs the RTL, a card or a clock: it is arithmetic on the operands a kernel would hand the
    tensor unit, which is the whole point."""
    A = words[:256].astype(np.uint32)
    B = words[256:].astype(np.uint32)
    f = {}
    for name, W in (("a", A), ("b", B)):
        nz = W != 0
        f[name + "_zero_frac"] = float(1.0 - nz.mean())
        d = np.bitwise_xor(W[1:], W[:-1])
        f[name + "_h_mean"] = float(popcount(d).mean())                      # bits that flip, word to word
        mant = W & np.uint32(0x7FFFFF)
        f[name + "_mant_pop"] = float(popcount(mant)[nz].mean()) if nz.any() else 0.0
        exps = ((W >> np.uint32(23)) & np.uint32(0xFF))
        f[name + "_exp_distinct"] = float(len(np.unique(exps[nz])) / 256.0) if nz.any() else 0.0
        # the per-position flip rate, mantissa-weighted: a high mantissa bit drives more of the tree
        pos = np.zeros(32)
        for b in range(32):
            pos[b] = float((((d >> np.uint32(b)) & np.uint32(1)) != 0).mean())
        f[name + "_pos_rate"] = pos.tolist()
        f[name + "_h_weighted"] = float(sum(pos[b] * (b + 1) / 23.0 for b in range(23)) + pos[31] + pos[30])
    # the zero gate, exactly: a multiply-add is live when both its operands are nonzero
    a_nz = (A != 0).reshape(16, 16)          # a[i][k]
    b_nz = (B != 0).reshape(16, 16)          # b[k][j]
    live = (a_nz.astype(np.int64)[:, :, None] & b_nz.astype(np.int64)[None, :, :]).sum()
    f["valid_frac"] = float(live) / MAC
    return f


def design(f):
    """Five features, each with a reason, shared by all four classes.

    1  an intercept: the per-op cost that does not depend on the data
    v  the zero-gated live multiply-adds: the gate, computed exactly from the operands
    t  v * (h_a + h_b): operand bits that flip, which is what the bus carries and the pipeline re-clocks
    p  v * mant_pop_a * mant_pop_b: the partial products the tree has to add
    x  v * (h_a * mant_pop_b + h_b * mant_pop_a): the partial products that CHANGE, word to word
    """
    v = f["valid_frac"]
    ha, hb = f["a_h_mean"], f["b_h_mean"]
    pa, pb = f["a_mant_pop"], f["b_mant_pop"]
    return [1.0, v, v * (ha + hb), v * pa * pb, v * (ha * pb + hb * pa)]


def lsq(A, b):
    A = np.asarray(A, float)
    b = np.asarray(b, float)
    return np.linalg.lstsq(A, b, rcond=None)[0]


# ---------------------------------------------------------------- the data
def counts_of(entry):
    m = entry["mean"]
    mult = sum(v for k, v in m["by_block"].items() if any(s in k for s in MULT_BLOCKS))
    return {"ffclk": m["ff_clocked"], "mult": mult, "rest": m["nets"] - mult, "bus": m["bus"],
            "valid": m["lane_valid"]}


def pattern_stats(pat):
    """Re-draw the pattern with the bench's own generator and average its statistics over the five seeds."""
    import tiles as T
    acc = None
    for s in SEEDS:
        f = stats(T.draw(pat, np.random.default_rng(s)))
        if acc is None:
            acc = {k: (list(v) if isinstance(v, list) else v) for k, v in f.items()}
        else:
            for k, v in f.items():
                if isinstance(v, list):
                    acc[k] = [a + b for a, b in zip(acc[k], v)]
                else:
                    acc[k] += v
    n = len(SEEDS)
    return {k: ([x / n for x in v] if isinstance(v, list) else v / n) for k, v in acc.items()}


def structured_stats(kind):
    acc, n = None, 0
    for s in (1, 2):
        p = os.path.join(D21, "structured_tiles", f"{kind}.{s}.bin")
        if not os.path.exists(p):
            continue
        w = np.frombuffer(open(p, "rb").read(), dtype=np.uint32)[:512]
        f = stats(w)
        n += 1
        if acc is None:
            acc = {k: (list(v) if isinstance(v, list) else v) for k, v in f.items()}
        else:
            for k, v in f.items():
                if isinstance(v, list):
                    acc[k] = [a + b for a, b in zip(acc[k], v)]
                else:
                    acc[k] += v
    if not n:
        return None
    return {k: ([x / n for x in v] if isinstance(v, list) else v / n) for k, v in acc.items()}


def main():
    import load_model as LM

    tog = json.load(open(os.path.join(D21, "toggles.json")))
    stog = json.load(open(os.path.join(D21, "structured_toggles.json")))
    rep = json.load(open(os.path.join(D21, "report.json")))["structured"]
    meas = rep["measured"]

    fit_pats = [p for p in tog if p != "twos"]
    X = [design(pattern_stats(p)) for p in fit_pats]
    Y = {c: [counts_of(tog[p])[c] for p in fit_pats] for c in CLASSES}
    Yv = [counts_of(tog[p])["valid"] for p in fit_pats]
    coef = {c: lsq(X, Y[c]).tolist() for c in CLASSES}

    def pred_counts(f):
        d = design(f)
        out = {c: max(0.0, sum(a * b for a, b in zip(d, coef[c]))) for c in CLASSES}
        out["valid"] = f["valid_frac"] * MAC
        return out

    # in sample
    ins = {c: [sum(a * b for a, b in zip(X[i], coef[c])) - Y[c][i] for i in range(len(X))] for c in CLASSES}
    rms = lambda v: float(np.sqrt(np.mean(np.square(v))))

    # the gate, checked on its own: the predicted live multiply-adds against the bench's lane_valid
    gate = [(fit_pats[i], X[i][1] * MAC, Yv[i]) for i in range(len(X))]

    # score on the structured matrices, WITHOUT refitting
    rows = []
    for kind in sorted(stog):
        f = structured_stats(kind)
        if f is None:
            continue
        pc = pred_counts(f)
        bc = counts_of(stog[kind])
        w_pred, _ = LM.flip_w(pc, 1024, 600.0, LM.V_REF, "aifoundry2", LM.T_FIT, 0.0, 1.0)
        w_bench, _ = LM.flip_w(bc, 1024, 600.0, LM.V_REF, "aifoundry2", LM.T_FIT, 0.0, 1.0)
        m = meas.get(kind)
        row = {"kind": kind, "features": {k: v for k, v in f.items() if not k.endswith("pos_rate")},
               "predicted_counts": pc, "bench_counts": bc,
               "count_err_pct": {c: (100 * (pc[c] - bc[c]) / bc[c] if bc[c] else None) for c in CLASSES},
               "valid_pred": pc["valid"], "valid_bench": bc["valid"],
               "switching_w_from_operand_stats": w_pred + LM.K.p_sm,
               "switching_w_from_bench_counts": w_bench + LM.K.p_sm}
        if m:
            row["measured_dyn_w"] = m["dyn"]
            row["err_w_operand_stats"] = w_pred + LM.K.p_sm - m["dyn"]
            row["err_w_bench_counts"] = w_bench + LM.K.p_sm - m["dyn"]
        rows.append(row)

    scored = [r for r in rows if "measured_dyn_w" in r]
    doc = {"what": "An operand-statistics front end for the flip model: the four counted classes predicted "
                   "from the operands alone, with no RTL bench. Fitted on the 14 fp32 patterns of 21 Sep, "
                   "scored on the structured matrices without refitting.",
           "request": "Q126", "written_utc": "2026-10-26",
           "features": design.__doc__,
           "approximation": "the 14 patterns' own tiles were drawn on the card and not kept, so they are "
                            "re-drawn here from the same distributions with rtl-sim/fma_toggle/tiles.py, "
                            "averaged over seeds 1-5; every feature is distributional, so a re-draw "
                            "reproduces it to sampling noise.",
           "fit": {"patterns": fit_pats, "coefficients": coef,
                   "in_sample_count_rms": {c: rms(ins[c]) for c in CLASSES},
                   "in_sample_count_rms_pct": {c: 100 * rms(ins[c]) / float(np.mean(Y[c])) for c in CLASSES},
                   "gate_check": [{"pattern": p, "predicted_live_macs": a, "bench_lane_valid": b}
                                  for p, a, b in gate],
                   "gate_rms_macs": rms([a - b for _, a, b in gate])},
           "scored_structured": rows,
           "summary": {
               "n_scored": len(scored),
               "rms_w_operand_stats": rms([r["err_w_operand_stats"] for r in scored]) if scored else None,
               "rms_w_bench_counts": rms([r["err_w_bench_counts"] for r in scored]) if scored else None,
               "bias_w_operand_stats": float(np.mean([r["err_w_operand_stats"] for r in scored])) if scored
               else None,
               "worst": max(scored, key=lambda r: abs(r["err_w_operand_stats"]))["kind"] if scored else None,
           }}
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(doc, open(OUT, "w"), indent=1)
    print("wrote", OUT)
    print("\nfit on %d patterns, count rms as a share of the mean count:" % len(fit_pats))
    for c in CLASSES:
        print(f"  {c:6s} {doc['fit']['in_sample_count_rms_pct'][c]:6.1f}%")
    print(f"  the zero gate alone: {doc['fit']['gate_rms_macs']:.1f} multiply-adds rms out of 4,096")
    print("\nscored on the structured matrices, no refit (switching W at 1,024 minions, 600 MHz, 0.517 V):")
    print(f"  {'matrix':16s}{'measured':>10s}{'bench cnt':>11s}{'operand st':>12s}{'err st':>9s}{'err bench':>11s}")
    for r in sorted(scored, key=lambda r: r["measured_dyn_w"]):
        print(f"  {r['kind']:16s}{r['measured_dyn_w']:10.2f}{r['switching_w_from_bench_counts']:11.2f}"
              f"{r['switching_w_from_operand_stats']:12.2f}{r['err_w_operand_stats']:+9.2f}"
              f"{r['err_w_bench_counts']:+11.2f}")
    s = doc["summary"]
    print(f"  rms: operand statistics {s['rms_w_operand_stats']:.2f} W, the RTL bench's own counts "
          f"{s['rms_w_bench_counts']:.2f} W, over {s['n_scored']} matrices")


if __name__ == "__main__":
    main()
