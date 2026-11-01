#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9,<3.13"
# dependencies = ["numpy==1.26.4"]
# ///
"""Q132(r): desk checks of the committed real2 files, from the committed files only (no model, no card).

    uv run --python 3.11 --with numpy==1.26.4 --no-project tools/claims-v3/kinds/real2/check_real2.py > check_real2.txt

The gate and the zero counts are recomputed here with plain loops over the tile's bytes, not with make_kinds.py, and the
statements the README makes about pairs and nested windows are checked on the bytes. Exits 1 on any failure.
"""
import hashlib
import json
import os
import struct
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools/claims-v3/kinds/real"))
import make_real as MR  # noqa: E402

S = json.load(open(os.path.join(HERE, "real2.json")))
P = json.load(open(os.path.join(HERE, "predictions-real2.json")))
A1 = json.load(open(os.path.join(ROOT, "tools/claims-v3/kinds/real/amendment-1.json")))
CAP = json.load(open(os.path.join(HERE, "capture.json")))
fails = []


def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + (f": {detail}" if detail else ""))
    if not ok:
        fails.append(name)


def raw_of(t, n, base=HERE):
    return open(os.path.join(base, "tiles", t, n + ".bin"), "rb").read()


def words(b):
    return list(struct.unpack("<256I", b))


def gate_loops(raw, t):
    """The gate of make_kinds' fact 3, by plain loops: fp32/fp16 8 slots a micro-op, int8 the pair (l, l+8)."""
    a, b = words(raw[:1024]), words(raw[1024:])
    A = [[a[i * 16 + w] for w in range(16)] for i in range(16)]
    B = [[b[p * 16 + j] for j in range(16)] for p in range(16)]
    off = tot = 0
    if t == "int8":
        for p in range(16):
            for i in range(16):
                for l in range(8):
                    tot += 1
                    off += A[i][p] == 0 or (B[p][l] == 0 and B[p][l + 8] == 0)
    else:
        for k in range(16):
            for i in range(16):
                for h in (0, 1):
                    for l in range(8):
                        tot += 1
                        off += A[i][k] == 0 or B[k][8 * h + l] == 0
    return off / tot


# ---- every tile: size, sha, gate, zero words
n_tiles = 0
for t, ts in S["tiles"].items():
    for n, e in ts.items():
        n_tiles += 1
        raw = raw_of(t, n)
        pr = P["tiles"][f"{t}/{n}"]
        ok = len(raw) == 2048 and hashlib.sha256(raw).hexdigest() == e["sha256"] == pr["tile_sha256"]
        g = gate_loops(raw, t)
        zw = float(np.mean([w == 0 for w in words(raw[:1024])]))
        check(f"{t}/{n}", ok and abs(g - e["stats"]["gated_lane_frac"]) < 1e-6 and abs(zw - e["stats"]["a"]["zero_word_frac"]) < 1e-9,
              f"gate {g:.6f} A zero words {zw:.6f}")
check("30 tiles", n_tiles == 30, str(n_tiles))
tier = {1: 0, 2: 0}
for v in P["tiles"].values():
    tier[v["tier"]] += 1
check("25 new tier-1, 5 tier-2", tier == {1: 25, 2: 5}, str(tier))


# ---- pairs differ only where the README says
def AB(t, n, base=HERE):
    r = raw_of(t, n, base)
    return r[:1024], r[1024:]


REAL = os.path.join(ROOT, "tools/claims-v3/kinds/real")
pairs = [("int8", "gpt2_l6_down_per_token", REAL, "l6_mlp_down"), ("int8", "gpt2_l6_down_p9999", REAL, "l6_mlp_down"), ("int8", "gpt2_l6_down_p999", REAL, "l6_mlp_down"),
         ("fp16", "gpt2_l6_mlp_down_fp16fwd", REAL, "l6_mlp_down"), ("int8", "gpt2_l11_down_p999", HERE, "gpt2_l11_down_maxabs"), ("int8", "gpt2_l11_down_asym", HERE, "gpt2_l11_down_maxabs"),
         ("int8", "vgg16_fc2_asym", HERE, "vgg16_fc2")]
for t, n, base, m in pairs:
    a0, b0 = AB(t, m, base)
    a1, b1 = AB(t, n)
    check(f"pair {t}/{n} vs {m}: same B, different A", b0 == b1 and a0 != a1)

# ---- nested windows: the same numbers in another format
for n in ("resnet18_l3c1", "vgg16_fc2", "t5small_l0_down"):
    a32 = np.frombuffer(raw_of("fp32", n)[:1024], dtype="<f4").reshape(16, 16)
    a16 = np.frombuffer(raw_of("fp16", n)[:1024], dtype="<f2").reshape(16, 32)
    a8 = np.frombuffer(raw_of("int8", n)[:1024], dtype="<i1").reshape(16, 64)
    check(f"nested {n}: fp16's first 16 k are fp32's, rounded", np.array_equal(a32.astype(np.float16).view(np.uint16), a16[:, :16].view(np.uint16)))
    check(f"nested {n}: an exact zero in fp32 is a zero byte in int8", bool(np.all(a8[:, :16][a32 == 0] == 0)))
    w = S["tiles"]["fp32"][n]["window"]
    check(f"nested {n}: same rows and columns in all three", all(S["tiles"][t][n]["window"]["rows"] == w["rows"] and S["tiles"][t][n]["window"]["cols"] == w["cols"] and S["tiles"][t][n]["window"]["k"][0] == w["k"][0] for t in ("fp16", "int8")))

# ---- the asymmetric tile: a ReLU zero is -128, no zero byte is left
a_sym = np.frombuffer(raw_of("int8", "vgg16_fc2")[:1024], dtype="<i1")
a_asy = np.frombuffer(raw_of("int8", "vgg16_fc2_asym")[:1024], dtype="<i1")
a_32 = np.frombuffer(raw_of("fp32", "vgg16_fc2")[:1024], dtype="<f4").reshape(16, 16)
aa = a_asy.reshape(16, 64)
check("asym: every exact zero of the fp32 tile's k range is -128 here", bool(np.all(aa[:, :16][a_32 == 0] == -128)))
check("asym: no zero byte in A", int(np.sum(a_asy == 0)) == 0, f"zero bytes {int(np.sum(a_asy == 0))} (symmetric tile {int(np.sum(a_sym == 0))} of 1024), -128 bytes {int(np.sum(a_asy == -128))}")

# ---- T5's weights: the low 16 mantissa bits of every B word are zero; other models' are not
bw = np.frombuffer(raw_of("fp32", "t5small_l0_up")[1024:], dtype="<u4")
check("T5 B on the bf16 grid (tile)", bool(np.all(bw & 0xFFFF == 0)))
for name in ("t5small_l0_ff_up", "t5small_l0_ff_down", "t5small_l2_ff_up", "t5small_l2_ff_down", "t5small_l5_ff_up", "t5small_l5_ff_down"):
    check(f"T5 B on the bf16 grid (whole weight, {name})", CAP["products"][name]["stats"]["B"]["low_mantissa_bits_zero_frac"] == 1.0)
check("other models' weights are not", all(CAP["products"][n]["stats"]["B"]["low_mantissa_bits_zero_frac"] < 0.001 for n in ("vgg16_fc2", "bert_l6_ff_up", "vit_l5_ff_down", "gpt2_l6_mlp_down", "resnet18_layer3_0_conv1")))

# ---- ViT layer 11: -0.0 in A, and the gate does not take it
av = np.frombuffer(raw_of("fp32", "vit_l11_down")[:1024], dtype="<u4")
nz = float(np.mean(av == 0x80000000))
check("vit_l11_down: -0.0 share in A, no +0.0", nz == S["tiles"]["fp32"]["vit_l11_down"]["zero"]["a"]["neg_zero_elem_frac"] and int(np.sum(av == 0)) == 0, f"{nz:.6f}")

# ---- the predictions recomputed: (a) from the frozen beta, the half-widths from the listed misses, (c) from its formula
PR = json.load(open(os.path.join(ROOT, "tools/claims-v3/kinds/real/predictions-real.json")))
for k, v in P["tiles"].items():
    t, n = k.split("/")
    fz = PR["predictor"]["per_type"][t]
    f = MR.features(raw_of(t, n), t)
    D = max(sum(b * f[c] for c, b in zip(fz["cols"], fz["beta"])), 0.0)
    a_ = v["a_aifoundry3_600mhz"]
    ok = abs(D - a_["D_w"]) < 6e-4
    c = v.get("c_gate_law")
    if c:
        G = P["gate_law"]["per_type"][t]
        ok = ok and abs(v["gated_lane_frac"] * G["G_w"] + (1 - v["gated_lane_frac"]) * G["L_w"] - c["D_w"]) < 6e-4
    if not ok:
        check(f"recompute {k}", False)
check("every (a) point from the frozen beta and every (c) from its formula", True)
for c, v in P["known_misses"]["classes"].items():
    vals = list(v["tiles"].values())
    r = float(np.sqrt(np.mean(np.square(vals))))
    check(f"known misses {c}: rms {r:.4f}, half-width {v['t975'] * r:.3f}", abs(r - v["rms_w"]) < 2e-4 and abs(v["t975"] * r - v["halfwidth_w"]) < 2e-3 and len(vals) == v["n"])

# ---- the calibration tiles reproduce Q130(n)'s sensitivity numbers (its D_w on E86's window)
cs = A1["calibration_sensitivity"]["products"]["l6_mlp_down"]
for n, key in (("gpt2_l6_down_per_token", "per-token max-abs (vector-wise)"), ("gpt2_l6_down_p9999", "per-tensor 99.99th percentile clip"), ("gpt2_l6_down_p999", "per-tensor 99.9th percentile clip")):
    check(f"{n} = amendment-1.json calibration_sensitivity '{key}'", abs(P["tiles"][f"int8/{n}"]["a_aifoundry3_600mhz"]["D_w"] - cs[key]["D_w"]) < 6e-4 and P["tiles"][f"int8/{n}"]["bus_bits_per_op"] == cs[key]["bus_bits_per_op"],
          f"D {P['tiles'][f'int8/{n}']['a_aifoundry3_600mhz']['D_w']} W, bus {cs[key]['bus_bits_per_op']}")
check("the committed int8 l6_mlp_down tile came back from this capture byte for byte", S["committed_int8_l6_mlp_down_reproduced_from_this_capture"] is True)
print(f"predictions-real2.json sha256 {MR.sha_file(os.path.join(HERE, 'predictions-real2.json'))}")
print(f"real2.json sha256 {MR.sha_file(os.path.join(HERE, 'real2.json'))}")
print(("ALL PASS" if not fails else f"FAILED: {fails}"))
sys.exit(1 if fails else 0)
