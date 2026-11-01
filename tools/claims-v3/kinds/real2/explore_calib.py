#!/usr/bin/env python3
"""Scratch: int8 calibrations on several products, medians over 12 windows and low-bit statistics of the weights."""
import hashlib, json, os, sys
import numpy as np
REPO, CAPD = sys.argv[1], sys.argv[2]
sys.path.insert(0, os.path.join(REPO, "tools/claims-v3/kinds/real"))
import make_real as MR
MK = MR.MK
E78 = json.load(open(os.path.join(REPO, MR.E78J)))
P, rows = MR.fit_predictor(E78, REPO)
CAP = json.load(open(os.path.join(CAPD, "capture.json")))

def q(x, s):
    return np.clip(np.rint(x.astype(np.float64) / s), -127, 127).astype(np.int8)

def variants(x, tok_axis=0):
    a = np.abs(x.astype(np.float64))
    lo, hi = min(float(x.min()), 0.0), max(float(x.max()), 0.0)
    s = (hi - lo) / 255.0
    z = int(np.clip(np.rint(-128 - lo / s), -128, 127))
    asym = np.clip(np.rint(x.astype(np.float64) / s) + z, -128, 127).astype(np.int8)
    return {"maxabs": q(x, float(a.max()) / 127.0),
            "per_token": q(x, a.max(axis=1 - tok_axis, keepdims=True) / 127.0),
            "p9999": q(x, float(np.quantile(a, 0.9999)) / 127.0),
            "p999": q(x, float(np.quantile(a, 0.999)) / 127.0),
            "asym": asym}, z

for name in sorted(CAP["products"]):
    d = np.load(os.path.join(CAPD, "products", name + ".npz"))
    A, B = d["A"], d["B"]
    if B.dtype == np.float32:
        ub = B.view(np.uint32)
        ua = A.view(np.uint32)
        lowB = float(np.mean((ub & 0xFFFF) == 0))
        lowA = float(np.mean(((ua & 0xFFFF) == 0) & (ua != 0)))
        print(f"{name:30s} low16-zero share: A {lowA:.4f} B {lowB:.4f}  low8-zero B {float(np.mean((ub & 0xFF) == 0)):.4f}")

for name in ("gpt2_l0_mlp_up", "gpt2_l6_mlp_down", "gpt2_l6_attn_qk", "gpt2_l3_mlp_down", "gpt2_l11_mlp_down", "bert_l2_ff_down", "bert_l6_ff_down", "distilbert_l1_ff_down", "vit_l5_ff_down", "vit_l11_ff_down", "resnet18_layer3_0_conv1", "vgg16_fc2", "t5small_l0_ff_down"):
    d = np.load(os.path.join(CAPD, "products", name + ".npz"))
    A, B = d["A"], d["B"]
    rec = CAP["products"][name]
    t = "int8"
    E, size, dtype, K = MK.TYPES[t]
    Bch = MR.quant_per_out_channel(B)[0] if rec["B_is"] == "weight" else MR.quant_per_tensor(B)[0]
    Bten = MR.quant_per_tensor(B)[0]
    V, z = variants(A)
    if rec["B_is"] != "weight":
        Vb, _ = variants(B, 1)
    print(name, "A shape", A.shape, "zero point", z, "max", float(np.abs(A).max()), "p99.9", float(np.quantile(np.abs(A), 0.999)), "p99", float(np.quantile(np.abs(A), 0.99)), "median", float(np.median(np.abs(A))))
    for vn, Aq in V.items():
        Bq = (Bten if vn == "asym" else Bch) if rec["B_is"] == "weight" else Vb[vn]
        nr, nk, nj = Aq.shape[0] // 16, Aq.shape[1] // K, Bq.shape[1] // 16
        rng = np.random.default_rng(int.from_bytes(hashlib.sha256(f"calib/{name}".encode()).digest()[:8], "little"))
        G, Bus, D, Zel = [], [], [], []
        for _ in range(12):
            w = (int(rng.integers(nr)) * 16, int(rng.integers(nk)) * K, int(rng.integers(nj)) * 16)
            Aw, Bw = MR.cut(Aq, Bq, w[0], w[1], w[2], K)
            raw = MK.encode(Aw, Bw, t)
            st = MK.tile_stats(raw, t)
            fe = MR.features(raw, t)
            G.append(st["gated_lane_frac"]); Bus.append(st["bus_bits_per_op"]); Zel.append(st["a"]["zero_elem_frac"])
            D.append(float(np.dot([fe[c] for c in P[t]["cols"]], P[t]["beta"])))
        print(f"   {vn:10s} zel {np.median(Zel):.3f} g {np.median(G):.3f} bus {int(np.median(Bus)):6d} D {np.median(D):.2f} [{min(D):.2f},{max(D):.2f}] sd-steps {float(Aq.astype(np.float64).std()):.2f}")
