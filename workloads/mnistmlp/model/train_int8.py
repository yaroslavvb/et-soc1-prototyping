#!/usr/bin/env python3
"""E202's trained-weights recipe: numpy float32 training on the CPU from a fixed seed, then post-training int8
quantization exactly as the kernel computes (mnist_model.py), written as an MLPW file and a JSON report.

Recipe (the design's section 4; the same code as the design lane's feasibility run):
  - He-normal initialisation from numpy.random.default_rng(20261116); the same generator draws the batch order;
  - input pixel / 255; cross-entropy; SGD with momentum 0.9, batch 128, learning rate 0.05 on a cosine schedule to 0
    over 6 epochs, weight decay 5e-5 on the weights; no augmentation, dropout or batch norm;
  - quantization: per-layer symmetric int8 weights (scale max|W| / 127, values -127..127); uint8 activations, each
    hidden layer's scale at the 99.99th percentile of its positive float activations over the first 10,000 training
    images; int32 biases b / (s_w s_in); multipliers M = round(2^32 s_w s_in / s_out) (0 < M < 2^31); the rounding
    offset floor(2^31 / M) folded into the hidden biases (Bp); the output layer keeps B.
Float training through a BLAS is not bit-reproducible across machines or thread counts: run it once and pin the
output by sha256 (model/PINS-SHA256SUMS). Never retrain on a card's box.

Usage: python3 -I -B train_int8.py --data DIR --out W.mlpw --report R.json [--epochs 6]
SPDX-License-Identifier: Apache-2.0
"""
import json
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mnist_model as mm  # noqa: E402

SEED = 20261116
BATCH = 128
LR0 = 0.05
MOMENTUM = 0.9
WD = 5e-5
ACT_PCT = 99.99


def forward_float(W, b, x):
    hs = [x]
    for l in range(4):
        hs.append(np.maximum(hs[-1] @ W[l] + b[l], 0))
    return hs, hs[-1] @ W[4] + b[4]


def predict_float(W, b, x, chunk=10000):
    out = []
    for i in range(0, x.shape[0], chunk):
        _, z = forward_float(W, b, x[i:i + chunk])
        out.append(z.argmax(axis=1))
    return np.concatenate(out)


def train(xtr, ytr, xte, yte, epochs, log):
    rng = np.random.default_rng(SEED)
    W, b = [], []
    for l in range(5):
        fi, fo = mm.DIMS[l], mm.DIMS[l + 1]
        W.append((rng.standard_normal((fi, fo), dtype=np.float32) * np.float32(np.sqrt(2.0 / fi))))
        b.append(np.zeros(fo, dtype=np.float32))
    vW = [np.zeros_like(w) for w in W]
    vb = [np.zeros_like(x) for x in b]
    n = xtr.shape[0]
    steps_per_epoch = (n + BATCH - 1) // BATCH
    total = steps_per_epoch * epochs
    step = 0
    hist = []
    for ep in range(epochs):
        t0 = time.time()
        perm = rng.permutation(n)
        loss_sum = 0.0
        for s in range(steps_per_epoch):
            idx = perm[s * BATCH:(s + 1) * BATCH]
            x = xtr[idx]
            y = ytr[idx]
            lr = np.float32(LR0 * 0.5 * (1.0 + np.cos(np.pi * step / total)))
            hs = [x]
            for l in range(4):
                hs.append(np.maximum(hs[-1] @ W[l] + b[l], 0))
            z = hs[-1] @ W[4] + b[4]
            z = z - z.max(axis=1, keepdims=True)
            e = np.exp(z)
            p = e / e.sum(axis=1, keepdims=True)
            m = x.shape[0]
            loss_sum += float(-np.log(p[np.arange(m), y] + 1e-12).sum())
            g = p
            g[np.arange(m), y] -= 1.0
            g /= np.float32(m)
            for l in range(4, -1, -1):
                gW = hs[l].T @ g + np.float32(WD) * W[l]
                gb = g.sum(axis=0)
                if l > 0:
                    g = (g @ W[l].T) * (hs[l] > 0)
                vW[l] = np.float32(MOMENTUM) * vW[l] - lr * gW
                vb[l] = np.float32(MOMENTUM) * vb[l] - lr * gb
                W[l] += vW[l]
                b[l] += vb[l]
            step += 1
        acc_te = float((predict_float(W, b, xte) == yte).mean())
        hist.append({"epoch": ep + 1, "loss": loss_sum / n, "test_acc_float": acc_te, "seconds": time.time() - t0})
        log(f"epoch {ep + 1}: loss {loss_sum / n:.4f} test acc (float) {acc_te:.4f} ({time.time() - t0:.1f} s)")
    return W, b, hist


def quantize(W, b, xcal_u8):
    s_prev = 1.0 / 255.0
    Q, Bq, M, info = [], [], [], []
    hs, _ = forward_float(W, b, xcal_u8.astype(np.float32) / 255.0)
    for l in range(5):
        w = float(np.abs(W[l]).max()) / 127.0
        q = np.zeros((mm.KPAD[l], mm.NPAD[l]), dtype=np.int8)
        q[:mm.DIMS[l], :mm.DIMS[l + 1]] = np.clip(np.rint(W[l] / w), -127, 127).astype(np.int8)
        bq = np.zeros(mm.NPAD[l], dtype=np.int64)
        bq[:mm.DIMS[l + 1]] = np.rint(b[l] / (w * s_prev)).astype(np.int64)
        Q.append(q)
        if l < 4:
            a = hs[l + 1]
            p = float(np.percentile(a[a > 0], ACT_PCT))
            s = p / 255.0
            m = w * s_prev / s
            Mi = int(round(m * 2 ** 32))
            assert 0 < Mi < 2 ** 31, (l, Mi)
            Bq.append(bq + (2 ** 31) // Mi)
            M.append(Mi)
            info.append({"layer": l + 1, "w_scale": w, "act_p": p, "act_scale": s, "m": m, "M": Mi})
            s_prev = s
        else:
            Bq.append(bq)
            info.append({"layer": 5, "w_scale": w})
    return Q, Bq, M, info


def main(argv):
    a = dict(zip(argv[1::2], argv[2::2]))
    if "--data" not in a or "--out" not in a or "--report" not in a:
        print(__doc__)
        return 2
    epochs = int(a.get("--epochs", "6"))
    d = a["--data"]
    logf = open(a["--report"] + ".log", "a")

    def log(s):
        line = time.strftime("%H:%M:%S ") + s
        print(line, flush=True)
        logf.write(line + "\n")
        logf.flush()

    log(f"python {sys.version.split()[0]} ({sys.executable}); numpy {np.__version__}; epochs {epochs}; "
        f"OPENBLAS_NUM_THREADS {os.environ.get('OPENBLAS_NUM_THREADS', '?')}")
    xtr_u8 = mm.load_images(os.path.join(d, "train-images-idx3-ubyte"))
    ytr = mm.load_idx(os.path.join(d, "train-labels-idx1-ubyte")).astype(np.int64)
    xte_u8 = mm.load_images(os.path.join(d, "t10k-images-idx3-ubyte"))
    yte = mm.load_idx(os.path.join(d, "t10k-labels-idx1-ubyte")).astype(np.int64)
    xtr = xtr_u8.astype(np.float32) / np.float32(255.0)
    xte = xte_u8.astype(np.float32) / np.float32(255.0)
    t0 = time.time()
    W, b, hist = train(xtr, ytr, xte, yte, epochs, log)
    t_train = time.time() - t0
    acc_float = {"train": float((predict_float(W, b, xtr) == ytr).mean()),
                 "test": float((predict_float(W, b, xte) == yte).mean())}
    log(f"float: train {acc_float['train']:.4f} test {acc_float['test']:.4f} (training {t_train:.0f} s)")
    Q, Bq, M, qinfo = quantize(W, b, xtr_u8[:mm.CAL_IMAGES])
    mm.write_mlpw(a["--out"], Q, Bq, M, "trained-seed20261116-e202")
    col = {}
    _, lb_tr, _ = mm.forward_chunked(Q, Bq, M, xtr_u8, collect=col)
    _, lb_te, _ = mm.forward_chunked(Q, Bq, M, xte_u8)
    rep = {"interpreter": sys.executable, "python": sys.version.split()[0], "numpy": np.__version__,
           "openblas_threads": os.environ.get("OPENBLAS_NUM_THREADS"), "seed": SEED, "batch": BATCH, "lr0": LR0,
           "momentum": MOMENTUM, "weight_decay": WD, "epochs": epochs, "act_percentile": ACT_PCT, "history": hist,
           "train_seconds": t_train, "acc_float": acc_float,
           "acc_int8_kernel": {"train": float((lb_tr == ytr).mean()), "test": float((lb_te == yte).mean())},
           "agree_int8_float_test": float((lb_te == predict_float(W, b, xte)).mean()),
           "quant": qinfo, "M": M, "acc_absmax": col["acc_absmax"],
           "out": os.path.basename(a["--out"]), "out_sha256": mm.sha256_file(a["--out"])}
    log(f"int8 as the kernel computes: train {rep['acc_int8_kernel']['train']:.4f} "
        f"test {rep['acc_int8_kernel']['test']:.4f}; {rep['out']} sha256 {rep['out_sha256']}")
    if a.get("--save-float"):
        np.savez_compressed(a["--save-float"], **{f"W{l + 1}": W[l] for l in range(5)},
                            **{f"b{l + 1}": b[l] for l in range(5)})
    json.dump(rep, open(a["--report"], "w"), indent=1)
    log("done")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
