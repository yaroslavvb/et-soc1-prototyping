"""mlp.py: a small MLP trained by online SGD on sparse parity, as a reference point only.

The setup follows the style of Barak et al., "Hidden progress in deep learning: SGD learns parities near
the computational limit" (NeurIPS 2022): +-1 inputs, one hidden ReLU layer, hinge loss, minibatch SGD on
fresh samples every step. Width, learning rate and batch are this script's choices, not the paper's.
Success = accuracy >= 99% against the clean parity on 4,096 held-out samples.

  OPENBLAS_NUM_THREADS=1 python3 mlp.py --n 50 --k 3 --eta 0 --seeds 1,2,3 --out mlp.jsonl
"""
from __future__ import annotations

import argparse
import json
import time

import numpy as np


def train(n, k, eta, seed, width=1000, batch=32, lr=0.1, max_steps=300_000, eval_every=500, max_s=120.0):
    rng = np.random.default_rng(seed)
    secret = np.sort(rng.choice(n, k, replace=False))
    f32 = np.float32
    s1, s2 = 1 / np.sqrt(n), 1 / np.sqrt(width)  # PyTorch-style uniform init
    W1 = rng.uniform(-s1, s1, (n, width)).astype(f32)
    b1 = rng.uniform(-s1, s1, width).astype(f32)
    W2 = rng.uniform(-s2, s2, width).astype(f32)
    b2 = f32(0)
    Xt = (2 * rng.integers(0, 2, (4096, n)) - 1).astype(f32)
    yt = np.prod(Xt[:, secret], axis=1)
    t0 = time.perf_counter()
    step, acc, hist = 0, 0.0, []
    while step < max_steps:
        X = (2 * rng.integers(0, 2, (batch, n)) - 1).astype(f32)
        y = np.prod(X[:, secret], axis=1)
        if eta > 0:
            y = np.where(rng.random(batch) < eta, -y, y)
        h = X @ W1 + b1
        a = np.maximum(h, 0)
        out = a @ W2 + b2
        g = np.where(y * out < 1, -y, 0).astype(f32) / batch   # d(mean hinge)/d(out)
        gW2 = a.T @ g
        gb2 = g.sum()
        gh = np.outer(g, W2) * (h > 0)
        gW1 = X.T @ gh
        gb1 = gh.sum(0)
        W1 -= lr * gW1
        b1 -= lr * gb1
        W2 -= lr * gW2
        b2 -= lr * gb2
        step += 1
        if step % eval_every == 0:
            ot = np.maximum(Xt @ W1 + b1, 0) @ W2 + b2
            acc = float(np.mean(np.sign(ot) == yt))
            hist.append((step, acc))
            if acc >= 0.99 or time.perf_counter() - t0 > max_s:
                break
    wall = time.perf_counter() - t0
    macs_per_step = 2 * batch * n * width + 3 * batch * width
    return dict(n=n, k=k, eta=eta, seed=seed, width=width, batch=batch, lr=lr, steps=step,
                samples=step * batch, ok=acc >= 0.99, final_acc=acc, wall_s=wall,
                macs=float(step) * macs_per_step, us_per_step=1e6 * wall / max(step, 1),
                hist=hist[:: max(1, len(hist) // 40)])


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=50)
    ap.add_argument("--k", type=int, default=3)
    ap.add_argument("--eta", type=float, default=0.0)
    ap.add_argument("--seeds", default="1,2,3")
    ap.add_argument("--width", type=int, default=1000)
    ap.add_argument("--batch", type=int, default=32)
    ap.add_argument("--lr", type=float, default=0.1)
    ap.add_argument("--max-steps", type=int, default=300_000)
    ap.add_argument("--max-s", type=float, default=120.0)
    ap.add_argument("--out", default="")
    a = ap.parse_args()
    for s in [int(x) for x in a.seeds.split(",")]:
        r = train(a.n, a.k, a.eta, s, a.width, a.batch, a.lr, a.max_steps, max_s=a.max_s)
        line = json.dumps(r)
        print(line, flush=True)
        if a.out:
            with open(a.out, "a") as f:
                f.write(line + "\n")
