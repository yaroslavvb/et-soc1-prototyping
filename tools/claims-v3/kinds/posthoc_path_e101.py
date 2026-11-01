#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""E101, POST HOC, labelled: never a verdict. What the memory path costs per op, arm by arm. It takes the registered reduction e101.json and the tile files, and writes posthoc-path.json and .txt.

    /usr/bin/python3 tools/claims-v3/kinds/posthoc_path_e101.py <e101.json> <out prefix>

E_path(arm, t, kind) = [S(arm, t, kind) - r S(res, t, kind)] / rate(arm, t) in nJ per op, with r = cycles(res) / cycles(arm), the arm's own measured cycles and rate. So it charges every watt above the loop's energy per op to the memory path.
Then, on mm16's 18 cells (six kinds, three formats): a least-squares split of E_path into a constant, a price per changed bit and a price per carried one, on the tiles' own counts per op (32 lines), the set of real files averaged. Also the same with the
changed-bit price held at E75's 0.274 pJ on 32 lines plus 0.0492 pJ on A's 16.
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import e101_common as e101  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
TYPES = ("fp32", "fp16", "int8")
ARMS = ("tenb", "mm16", "gemm1", "gemmnc1", "gemm16", "mmp64")
FLOP = {"fp32": 8192, "fp16": 16384, "int8": 32768}     # E80's operations per op (2 x multiply-adds for the floats, as the page quotes TFLOPS; int8 TOPS likewise)


def name(arm, t, k):
    if arm == "res":
        return f"res.{t}.{k}" if k in ("e37", "real") else f"{t}.{e101.kind_name(t, k)}"
    return f"{arm}.{t}.{e101.kind_name(t, k)}"


def counts(paths):
    """changed bits and carried ones per op (16 A lines + 16 B lines, pairs of consecutive lines in the repeating tile), averaged over the files; A's changed bits apart."""
    ca, cb, on = [], [], []
    for p in paths:
        b = open(os.path.join(ROOT, p), "rb").read()
        A = np.frombuffer(b[:1024], dtype=np.uint8).reshape(16, 64)
        B = np.frombuffer(b[1024:], dtype=np.uint8).reshape(16, 64)
        f = lambda X: float(np.unpackbits(np.bitwise_xor(X, np.roll(X, -1, axis=0)), axis=1).sum())
        ca.append(f(A))
        cb.append(f(B))
        on.append(float(np.unpackbits(A).sum() + np.unpackbits(B).sum()))
    return float(np.mean(ca)), float(np.mean(cb)), float(np.mean(on))


def main():
    E = json.load(open(sys.argv[1]))
    I = E["items"]
    out = {"note": "POST HOC, labelled, never a verdict", "path": {}, "rates": {}}
    items = {it["name"]: it for it in e101.load_items()}
    kinds = ("zeros", "ones", "sparse50", "e37", "real", "random")
    for arm in ARMS:
        for t in TYPES:
            for k in kinds:
                n = name(arm, t, k)
                if n not in I or I[n]["S"]["mean"] is None:
                    continue
                res = I[name("res", t, k)]
                r = res["cycles_per_op"] / I[n]["cycles_per_op"]
                rate = I[n]["rate"]["mean"] / 1e9
                ep = (I[n]["S"]["mean"] - r * res["S"]["mean"]) / rate
                out["path"][n] = {"arm": arm, "type": t, "kind": k, "E_path_nj_op": round(ep, 3), "E_total_nj_op": round(I[n]["pj_op_S"]["mean"] / 1000.0, 3), "E_res_nj_op": round(res["pj_op_S"]["mean"] / 1000.0, 3),
                                  "cycles": round(I[n]["cycles_per_op"], 2), "rate_gop_s": round(rate, 4), "rate_t_per_s": round(rate * FLOP[t] / 1000.0, 3), "pj_mac": round(I[n]["pj_mac_S"]["mean"], 3), "S_w": round(I[n]["S"]["mean"], 3), "die_rise_c": round(I[n]["dT_win"]["mean"], 2)}
    # the fit on mm16
    X, y, labels = [], [], []
    for t in TYPES:
        for k in kinds:
            n = name("mm16", t, k)
            it = items[n]
            v = it["values"]
            files = v.split(":", 2)[2].split(",")
            ca, cb, on = counts(files)
            X.append([1.0, ca + cb, on])
            y.append(out["path"][n]["E_path_nj_op"] * 1000.0)
            labels.append((n, ca, cb, on))
    X, y = np.array(X), np.array(y)
    coef, *_ = np.linalg.lstsq(X, y, rcond=None)
    pred = X @ coef
    dof = max(len(y) - 3, 1)
    s2 = float(((y - pred) ** 2).sum()) / dof
    cov = s2 * np.linalg.inv(X.T @ X)
    out["fit_mm16"] = {"pj_const": round(float(coef[0]), 1), "pj_per_changed_bit": round(float(coef[1]), 4), "pj_per_one": round(float(coef[2]), 4),
                       "se": [round(float(x), 4) for x in np.sqrt(np.diag(cov))], "rms_nj_op": round(float(np.sqrt(((y - pred) ** 2).mean())) / 1000.0, 3)}
    # with E75's changed-bit prices held
    held = np.array([0.274 * (ca + cb) + 0.0492 * ca for _, ca, cb, _ in labels])
    X2 = np.c_[np.ones(len(y)), X[:, 2]]
    c2, *_ = np.linalg.lstsq(X2, y - held, rcond=None)
    p2 = X2 @ c2 + held
    out["fit_mm16_e75_held"] = {"pj_const": round(float(c2[0]), 1), "pj_per_one": round(float(c2[1]), 4), "rms_nj_op": round(float(np.sqrt(((y - p2) ** 2).mean())) / 1000.0, 3)}
    out["counts"] = {n: {"changed_bits_a": round(a, 0), "changed_bits_b": round(b, 0), "ones": round(o, 0), "E_path_nj_op": round(float(yy) / 1000.0, 3), "fit_nj_op": round(float(pp) / 1000.0, 3), "fit_e75_held_nj_op": round(float(q) / 1000.0, 3)}
                     for (n, a, b, o), yy, pp, q in zip(labels, y, pred, p2)}
    json.dump(out, open(sys.argv[2] + ".json", "w"), indent=1)
    L = ["E101, POST HOC, labelled: what the memory path costs per op. E_path = [S(arm) - r S(res)] / rate, nJ per op; never a verdict.", ""]
    L.append(f"{'':10s} " + " ".join(f"{k:>9s}" for k in kinds) + "   cycles  Gop/s  T(FL)OP/s")
    for arm in ARMS:
        for t in TYPES:
            row = [out["path"].get(name(arm, t, k)) for k in kinds]
            if not any(row):
                continue
            first = next(x for x in row if x)
            L.append(f"{arm + ' ' + t:18s} " + " ".join(f"{x['E_path_nj_op']:9.2f}" if x else " " * 9 for x in row) + f"   {first['cycles']:8.1f} {first['rate_gop_s']:6.3f} {first['rate_t_per_s']:7.2f}")
    L += ["", f"mm16's 18 cells, least squares: {out['fit_mm16']}", f"with E75's changed-bit prices held: {out['fit_mm16_e75_held']}", ""]
    for n, c in out["counts"].items():
        L.append(f"  {n:22s} changed {c['changed_bits_a'] + c['changed_bits_b']:7.0f} ones {c['ones']:7.0f}  E_path {c['E_path_nj_op']:6.2f} fit {c['fit_nj_op']:6.2f} E75 held {c['fit_e75_held_nj_op']:6.2f}")
    open(sys.argv[2] + ".txt", "w").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
