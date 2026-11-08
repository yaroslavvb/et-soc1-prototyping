#!/usr/bin/env python3
"""M12 (Q157): self-test of m12_common's pieces on synthetic data (no committed measurement is read), plus the staging check.

    /usr/bin/python3 -B tools/claims-v3/m12/selftest_m12.py --root .      # prints one line per case and PASS/FAIL; exit 0 only if all pass
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import json
import math
import os
import random
import struct
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import m12_common as C  # noqa: E402

RES = []


def case(name, ok, detail=""):
    RES.append(ok)
    print(f"{'PASS' if ok else 'FAIL'}  {name}" + (f": {detail}" if detail else ""))


def synth_int8(rng, truth, noise_k, noise_t):
    """20 synthetic one-number int8 kinds and 4 trains from a known D8"""
    R = 1.92e9
    rows, ys = [], []
    for i in range(20):
        lm = {"c_store": rng.choice([8192, 14336, 15360, 16256, 18944, 25472]), "c_in": rng.choice([512, 896, 960, 1016]), "c_out": 0,
              "scp": rng.choice([0, 1024, 3072, 6144, 7168])}
        lm["c_out"] = lm["c_in"]
        r = C.int8_row(R, lm, 4 * rng.randint(1, 8), 4 * rng.randint(1, 8))
        rows.append(r)
        ys.append(C.dot(r, truth) + rng.gauss(0, noise_k))
    trows = [[0.0, R * 12096e-15, 0.0, 1.0, 1.0], [0.0, 0.0, 0.0, -7.0, 7.0], [0.0, 0.0, 0.0, 7.0, 7.0], [0.0, 0.0, 0.0, -1.0, 1.0]]
    ty = [C.dot(r, truth) + rng.gauss(0, noise_t) for r in trows]
    return rows, ys, trows, ty


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    root = os.path.abspath(ap.parse_args().root)
    truth = [1.70, 1.2, 12.9, 0.0084, 0.0099]
    rng = random.Random(15701)
    # S1: noiseless data: the joint fit returns the truth
    rows, ys, trows, ty = synth_int8(rng, truth, 0.0, 0.0)
    J = C.joint_fit(rows, [y + 1e-9 * (i % 3 - 1) for i, y in enumerate(ys)], trows, ty, [0.0025] * 4)
    err = max(abs(a - b) for a, b in zip(J["b"], truth))
    case("S1 the joint fit recovers known int8 parameters from noiseless rows", err < 1e-6, f"largest |b - truth| {err:.2e}")
    # S2: noisy data: sigma_K near the truth on average over 200 draws, and the 95% intervals cover near 95%
    sig, cover, nd = [], 0, 200
    for d in range(nd):
        rows, ys, trows, ty = synth_int8(random.Random(20000 + d), truth, 0.036, 0.0025)
        J = C.joint_fit(rows, ys, trows, ty, [0.0025] * 4)
        sig.append(J["sigma_K"])
        cover += all(abs(J["b"][i] - truth[i]) <= 1.96 * math.sqrt(J["cov"][i][i]) for i in (1, 3))
    ms = sum(sig) / nd
    case("S2 sigma_K estimates the kinds' noise (truth 0.036 W) without large bias", abs(ms - 0.036) < 0.004, f"mean {ms:.4f}")
    case("S3 the 95% intervals of k_walk and beta_A both cover in at least 85% of draws", cover / nd >= 0.85, f"{cover} of {nd}")
    # S4: the float fit recovers c_f, gamma_A, gamma_B from noiseless kinds and trains
    tf = [-0.011, 0.0030, 0.0133]
    fk = [C.float_row(a, b) for a, b in ((2, 2), (3, 3), (7, 30), (30, 7))]
    ft = [[0.0, -23.0, 23.0], [0.0, 1.0, 1.0]]
    b, cov = C.wls(fk + ft, [C.dot(r, tf) for r in fk + ft], [0.03 ** 2] * 4 + [0.003 ** 2] * 2)
    case("S4 the float fit recovers c_f, gamma_A and gamma_B", max(abs(x - y) for x, y in zip(b, tf)) < 1e-12, str([round(x, 6) for x in b]))
    # S5: the delta method on a known covariance
    se = C.se_of([1.0, 2.0], [[4.0, 1.0], [1.0, 9.0]])
    case("S5 se_of = sqrt(x' S x)", abs(se - math.sqrt(4 + 4 + 36)) < 1e-12, f"{se:.6f}")
    # S6: popcounts of a one-base-word tile (A 1.0; B columns alternate two words one bit apart)
    aw, w0, w1 = 0x3F800000, 0x3EAAAAAB, 0x3EAAAAAB ^ (1 << 12)
    raw = struct.pack("<I", aw) * 256 + b"".join(struct.pack("<I", w0 if (i % 16) < 8 else w1) for i in range(256))
    pa, pb, na, nb = C.tile_popcounts(raw)
    want_b = (C.popcount(w0) + C.popcount(w1)) / 2
    case("S6 tile_popcounts: A's popcount and B's mean over two words", pa == 7 and abs(pb - want_b) < 1e-12 and na == 1 and nb == 2,
         f"pc_a {pa}, pc_b {pb} (want {want_b}), distinct {na}/{nb}")
    # S7: the t quantiles
    case("S7 t975 matches its table and the series at df 100 (1.98397)", abs(C.t975(3) - 3.182446305) < 1e-9 and abs(C.t975(100) - 1.98397) < 2e-4,
         f"t(3) {C.t975(3):.6f}, t(100) {C.t975(100):.5f}")
    # S8: the bootstrap and the gain/offset words
    e = [0.01 * i for i in range(10)]
    bt = C.boot_rms_diff(e, e)
    case("S8 the rms bootstrap of identical residuals is 0 [0, 0]", bt["diff"] == 0 and bt["lo95"] == 0 and bt["hi95"] == 0)
    case("S9 the gain/offset words", C.gain_offset_word({"lo95": 0.1, "hi95": 0.2}) == "OFFSET" and C.gain_offset_word({"lo95": -0.2, "hi95": -0.1}) == "GAIN"
         and C.gain_offset_word({"lo95": -0.1, "hi95": 0.1}) == "NOT SEPARABLE")
    # S10: the candidates' staging is reproducible and every new tile is its two words repeated
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import candidates_m12 as CM  # noqa: E402
    rows, blobs = CM.stage(root, None)
    kj = json.load(open(os.path.join(root, "tools/claims-v3/m12/kinds-m12.json")))["kinds"]
    same = kj == rows and all(open(os.path.join(root, p), "rb").read() == raw for p, raw in blobs.items())
    words = all(open(os.path.join(root, r["tile"]), "rb").read() == struct.pack("<I", int(r["a_word"], 16)) * 256 + struct.pack("<I", int(r["b_word"], 16)) * 256
                for r in rows)
    case("S10 the candidates' tiles and kinds-m12.json rebuild byte for byte, each tile its two words repeated", same and words, f"{len(rows)} kinds")
    print(f"{sum(RES)} of {len(RES)} PASS")
    return 0 if all(RES) else 1


if __name__ == "__main__":
    sys.exit(main())
