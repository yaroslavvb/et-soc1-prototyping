#!/usr/bin/env python3
"""Scratch: every captured product x type, 20 windows, the gate and the predictor, to choose the tile list."""
import hashlib, json, os, sys
import numpy as np
REPO, CAPD = sys.argv[1], sys.argv[2]
sys.path.insert(0, os.path.join(REPO, "tools/claims-v3/kinds/real"))
import make_real as MR
MK = MR.MK
E78 = json.load(open(os.path.join(REPO, MR.E78J)))
P, rows = MR.fit_predictor(E78, REPO)
for t in MR.TYPES:
    print(t, P[t]["selected"], P[t]["beta"])
CAP = json.load(open(os.path.join(CAPD, "capture.json")))
names = sorted(CAP["products"])
SEED = 20261101
for name in names:
    if name.startswith("x_"):
        continue
    d = np.load(os.path.join(CAPD, "products", name + ".npz"))
    A, B = d["A"], d["B"]
    rec = CAP["products"][name]
    a_is, b_is = rec["A_is"], rec["B_is"]
    out = []
    for t in MR.TYPES:
        E, size, dtype, K = MK.TYPES[t]
        if "bf16" in name and t != "fp32":
            continue
        if "fp16fwd" in name and t != "fp16":
            continue
        if t == "fp32":
            Aq, Bq = A.astype(np.float32), B.astype(np.float32)
        elif t == "fp16":
            Aq, Bq = A.astype(np.float16), B.astype(np.float16)
        else:
            Aq = MR.quant_per_tensor(A)[0]
            Bq = MR.quant_per_out_channel(B)[0] if b_is == "weight" else MR.quant_per_tensor(B)[0]
        nr, nk, nj = Aq.shape[0] // 16, Aq.shape[1] // K, Bq.shape[1] // 16
        rng = np.random.default_rng(int.from_bytes(hashlib.sha256(f"{SEED}/explore/{name}/{t}".encode()).digest()[:8], "little"))
        seen, g, bus, D, nz = set(), [], [], [], []
        n_try = min(20, nr * nk * nj)
        while len(seen) < n_try:
            w = (int(rng.integers(nr)) * 16, int(rng.integers(nk)) * K, int(rng.integers(nj)) * 16)
            if w in seen:
                continue
            seen.add(w)
            Aw, Bw = MR.cut(Aq, Bq, w[0], w[1], w[2], K)
            raw = MK.encode(Aw, Bw, t)
            st = MK.tile_stats(raw, t)
            fe = MR.features(raw, t)
            g.append(st["gated_lane_frac"]); bus.append(st["bus_bits_per_op"])
            D.append(float(np.dot([fe[c] for c in P[t]["cols"]], P[t]["beta"])))
            nz.append(st["a"]["zero_elem_frac"])
        out.append(f"{t}: zel {np.median(nz):.3f} g {np.median(g):.3f} [{min(g):.2f},{max(g):.2f}] bus {int(np.median(bus))} D {np.median(D):.2f} [{min(D):.2f},{max(D):.2f}]")
    print(name.ljust(30), f"A+0 {rec['stats']['A']['plus_zero_frac']:.3f} A-0 {rec['stats']['A']['neg_zero_frac']:.3f}", " | ".join(out), flush=True)
